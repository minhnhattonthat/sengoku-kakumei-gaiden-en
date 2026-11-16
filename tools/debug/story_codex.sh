#!/bin/sh
# Story pass by read-only Codex reviewers, one per chapter (docs/story-reviewer-brief.md,
# references/translation.md §Review).
#   python -X utf8 tools/story.py chapters
#   python -X utf8 $SKILL/scripts/qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"
#   sh tools/debug/story_codex.sh [parallel=3] [chapter names...]
# Reports go to work/qa/story/reports/<chapter>.md; the controller reads each and writes the verdict
# (work/qa/story/verdicts/<chapter>.tsv: chapter<TAB>ok|issue<TAB>note) and the Minors to docs/polish.md.
# Chapters with a report already are skipped unless named.
set -u
PAR=${1:-3}; [ $# -gt 0 ] && shift
CH=work/qa/story/chapters; RP=work/qa/story/reports
mkdir -p "$RP"
run_one() {
  n=$1; out="$RP/$n.md"
  prompt="You are a read-only story reviewer for a GBA fan translation (repo: current directory).
Read docs/story-reviewer-brief.md and follow it exactly. Your chapter file is $CH/$n.txt.
Also read docs/synopsis.md, docs/style-reference.md and glossary.md first.
Do not write any file (read-only sandbox). Your final message is the report, ending with the Assessment line."
  codex exec -s read-only --skip-git-repo-check -o "$out" "$prompt" > "$RP/$n.log" 2>&1
  if [ -s "$out" ]; then echo "done $n: $(grep -A2 -i '^### Assessment' "$out" | tail -n +2 | tr '\n' ' ')"
  else echo "FAILED $n (see $RP/$n.log)"; fi
}
if [ $# -gt 0 ]; then names="$*"; else
  names=""; for c in "$CH"/*.txt; do n=$(basename "$c" .txt); [ -s "$RP/$n.md" ] || names="$names $n"; done; fi
for n in $names; do
  while [ "$(jobs -r | wc -l)" -ge "$PAR" ]; do sleep 5; done
  run_one "$n" &
done
wait

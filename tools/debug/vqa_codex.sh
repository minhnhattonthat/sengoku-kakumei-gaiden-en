#!/bin/sh
# Visual QA by read-only Codex reviewers, one per qa_gate chunk (docs/visual-qa-brief.md).
#   sh tools/debug/vqa_codex.sh work/qa/chunks work/qa/verdicts [parallel=4]
# Codex runs with -s read-only, so it cannot write its verdict file: it ends its reply with the verdict lines
# between VERDICTS-BEGIN / VERDICTS-END, and this script writes them to <verdicts>/<chunk>.tsv.
# Chunks that already have a verdict file are skipped (delete it to redo one).
set -u
CH=$1; VD=$2; PAR=${3:-4}
SKILL=$(python tools/skill.py)
mkdir -p "$VD" "$VD/raw"
run_one() {
  c=$1; n=$(basename "$c" .txt); out="$VD/$n.tsv"
  [ -s "$out" ] && return 0
  prompt="You are a read-only visual-QA reviewer for a GBA translation (repo: current directory).
Read docs/visual-qa-brief.md and follow it exactly; SKILL=$SKILL (tools: \$SKILL/scripts/sheet.py, inkbox.py).
Write zoomed crops only under your temp dir, never in the repo. Original ROM sheets: work/qa/tour_jp/<scene>/.
Your chunk file is $c: one id<TAB>path line per sheet; open and look at every sheet image in it (view the PNG).
Do not write the verdict file (read-only sandbox). Instead finish your reply with exactly:
VERDICTS-BEGIN
id<TAB>ok|issue<TAB>note   (one line per id in the chunk, every id)
VERDICTS-END"
  codex exec -s read-only --skip-git-repo-check -o "$VD/raw/$n.txt" "$prompt" > "$VD/raw/$n.log" 2>&1
  awk '/^VERDICTS-BEGIN/{f=1;next}/^VERDICTS-END/{f=0}f&&NF' "$VD/raw/$n.txt" > "$out.tmp"
  if [ -s "$out.tmp" ]; then mv "$out.tmp" "$out"; echo "done $n $(grep -c . "$out") lines, $(grep -c '	issue	' "$out") issues"
  else rm -f "$out.tmp"; echo "FAILED $n (see $VD/raw/$n.log)"; fi
}
for c in "$CH"/chunk_*.txt; do
  while [ "$(jobs -r | wc -l)" -ge "$PAR" ]; do sleep 5; done
  run_one "$c" &
done
wait

#!/bin/sh
# Run the graphics-survey brief (tools/re_survey_brief.md) through codex on each chunk of sheets, in parallel.
# Usage: cd work/re/sweep; ls *.png > all.txt; split -l 7 -d all.txt chunk_; cp ../../../tools/re_survey_brief.md brief.md;
#        sh ../../../tools/re_survey_codex.sh   -> result_chunk_NN.txt
cd "${1:-.}"
for c in chunk_0*; do
  imgs=""
  for f in $(cat "$c"); do imgs="$imgs -i $f"; done
  ( codex exec --skip-git-repo-check -s read-only --ephemeral $imgs -o "result_$c.txt" \
      "$(cat brief.md) Sheets attached in this order: $(cat "$c" | tr '\n' ' ')" < /dev/null > "log_$c.txt" 2>&1 ) &
done
wait
echo done

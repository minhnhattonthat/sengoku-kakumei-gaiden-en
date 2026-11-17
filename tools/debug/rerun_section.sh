#!/bin/sh
# Re-run final_tour.sh sections on the toured build (build/tour.gba), without the rest of the tour, then refresh
# their textcover logs in work/qa/cover:
#   sh tools/debug/rerun_section.sh mhelp prov
# Runs the same command lines as final_tour.sh (it greps them from there), so the two cannot drift apart.
set -u
cd "$(dirname "$0")/../.."
[ $# -gt 0 ] || { echo "usage: $0 SECTION.." >&2; exit 2; }
Q=work/qa
R=$(pwd -W 2>/dev/null || pwd)
SKILL=$(python tools/skill.py)
ROM="$R/build/tour.gba"
TC="--script $SKILL/scripts/lua/probes/textcover.lua"
RANGES=$(grep -o "^RANGES=\".*\"" tools/debug/final_tour.sh | sed 's/^RANGES="//; s/"$//')
W="python -X utf8 tools/debug/warp.py --rom $ROM"
J=${JOBS:-2}
run() { out=$1; shift; rm -rf "$Q/$out"; echo "== $out"; $W --out "$R/$Q/$out" $TC --var "$RANGES" "$@" 2>&1 | grep -v "tiles (row-major)"; }
st=0
for s in "$@"; do
  line=$(grep -E "^run $s " tools/debug/final_tour.sh) || { echo "no section $s in final_tour.sh" >&2; st=2; continue; }
  eval "$line"
  d=$(echo "$s" | tr / _); rm -rf "$Q/cover/$d"
  (cd "$Q/$s" && find . -name log.txt) | while read -r f; do
    dst="$Q/cover/$d/$(dirname "$f")"; mkdir -p "$dst"; cp "$Q/$s/$f" "$dst/"
  done
done
exit $st

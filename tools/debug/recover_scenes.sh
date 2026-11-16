#!/bin/sh
# Re-run only the coverage scenes that show strings a text edit moved (build.py keeps every other string in the
# toured build's slot, data/text_layout.tsv), with the textcover probe, on the current build.
#   sh tools/debug/recover_scenes.sh OUT SCENES_FILE [dojo]
# SCENES_FILE: scene lines (from tools/debug/scenes.txt) run as final_tour.sh's `pages` (A every 40 frames);
# `dojo` also re-runs final_tour.sh's go/dojo and go/dojo0. Then copy OUT/**/log.txt over the same scenes in
# work/qa/cover and re-run textcover.py.
set -u
cd "$(dirname "$0")/../.."
Q=$1; SC=$2; DOJO=${3:-}
R=$(pwd -W 2>/dev/null || pwd)
SKILL=$(python tools/skill.py)
cp build/sengoku_en.gba build/recover.gba
ROM="$R/build/recover.gba"
TC="--script $SKILL/scripts/lua/probes/textcover.lua"
RANGES="RANGES='0804CE4C-0805043E,0805045C-08055BA6,0805E2AC-0805E776,08061C1C-08061C59,0807E090-0807EF1C,08201800-08202114,087C1000-087DFFFF'"
W="python -X utf8 tools/debug/warp.py --rom $ROM"
run() { out=$1; shift; rm -rf "$Q/$out"; echo "== $out"; $W --out "$R/$Q/$out" $TC --var "$RANGES" "$@" 2>&1 | grep -v "tiles (row-major)"; }
J=${JOBS:-2}
run pages --jobs $J --scenes-file "$SC" --var PAGES=2400
if [ "$DOJO" = dojo ]; then
  run go/dojo --scenes-file work/qa/go/dojo.txt --script tools/lua/dojo.lua --var GOD=1 --var LIST=0 --var VERBOSE=1
  run go/dojo0 --scenes-file work/qa/go/dojo.txt --script tools/lua/dojo.lua --var GOD=1 --var CTRL=0 --var LIST=0 --var VERBOSE=1
fi
echo RECOVER_DONE

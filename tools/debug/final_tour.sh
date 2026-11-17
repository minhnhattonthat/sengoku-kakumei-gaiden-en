#!/bin/sh
# Final QA runs on one build: the screen tour and every text-coverage run (docs/re/coverage.md), each with the
# textcover probe, into the directories the visual-QA manifest (work/qa/manifest.tsv) and textcover.py read.
#   sh tools/debug/final_tour.sh [OUTROOT=work/qa]
#   SRC=other.gba TOUR=build/tour_other.gba sh tools/debug/final_tour.sh work/qa/other   (another ROM)
#   SKIP="tour" JOBS=1 sh tools/debug/final_tour.sh   (resume: keep runs that finished on this same build)
# Copies $SRC (build/sengoku_en.gba) to $TOUR (build/tour.gba) first; then:
#   python -X utf8 $SKILL/scripts/qa_gate.py init work/qa/manifest.tsv <dirs printed at the end> --build build/tour.gba
#   python -X utf8 $SKILL/scripts/textcover.py work/qa/cover build/strings.tsv --waive docs/text_unshown.tsv --mask 0x7FFFFF
set -u
cd "$(dirname "$0")/../.."
Q=${1:-work/qa}
R=$(pwd -W 2>/dev/null || pwd)
SKILL=$(python tools/skill.py)
SRC=${SRC:-build/sengoku_en.gba}
TOUR=${TOUR:-build/tour.gba}
mkdir -p "$Q"
cp "$SRC" "$TOUR"
ROM="$R/$TOUR"
TC="--script $SKILL/scripts/lua/probes/textcover.lua"
RANGES="RANGES='0804CE4C-0805043E,0805045C-08055BA6,0805E2AC-0805E776,08061C1C-08061C59,0807E090-0807EF1C,08201800-08202114,087C1000-087DFFFF'"
W="python -X utf8 tools/debug/warp.py --rom $ROM"
# SKIP="tour pages ..": keep those runs' existing output (same build, after a run that was killed part-way)
run() { out=$1; shift
  case " ${SKIP:-} " in *" $out "*) echo "== $out (skipped, kept)"; return;; esac
  rm -rf "$Q/$out"; echo "== $out"; $W --out "$R/$Q/$out" $TC --var "$RANGES" "$@" 2>&1 | grep -v "tiles (row-major)"; }

# JOBS=N (default 3): parallel emulators (~550 MB each); 5 next to another project's emulators ran out of memory
# and every Mesen start failed with exit 3221225794 (0xC0000142). Check the log for FAIL lines afterwards.
J=${JOBS:-3}
run tour --jobs $J --proof
# dialogue pages: every ev=/dlg= scene, A every 40 frames after the shot
grep -E '^[a-z0-9_]+ .*(ev=|dlg=)' tools/debug/scenes.txt > "$Q/pages_scenes.txt"
run pages --jobs $J --scenes-file "$Q/pages_scenes.txt" --var PAGES=2400
run desc item_desc --script tools/lua/itemdesc.lua --var STEP=1 --shot-every 40
run prov provinces --script tools/lua/liststep.lua --var LIST=0x08731448 --var N=51 --var STEP=1 --shot-every 90
run mhelp menu_help --script tools/lua/liststep.lua --var LIST=0x087303B8 --var N=46 --var STEP=1 --var AFTER=4900 --shot-every 60
run enc encyclopedia_all --shot-every 56
run restitles results_titles --script tools/lua/results.lua --var STEP=1 --shot-every 100
for k in 0x17 0x29 0x33; do
  run restitles_$k results_titles --script tools/lua/results.lua --var STEP=1 --var RANK=$k --shot-every 100
done
run go/dojo --scenes-file work/qa/go/dojo.txt --script tools/lua/dojo.lua --var GOD=1 --var LIST=0 --var VERBOSE=1
run go/dojo0 --scenes-file work/qa/go/dojo.txt --script tools/lua/dojo.lua --var GOD=1 --var CTRL=0 --var LIST=0 --var VERBOSE=1
run go/lk --jobs $J --scenes-file work/qa/go/lk.txt --script tools/lua/liststep.lua --var LIST=0 --var VERBOSE=1 --shot-every 60
# story flag branches (coverage only, no sheets in the manifest)
rm -rf "$Q/swap"
sh tools/debug/swap_groups.sh "$R/$Q/swap" "$ROM" 0x08730940 0x08730b38 0x08730b48 0x08730c78 0x08730cb0 0x08730f00 \
  0x08730f10 0x08730f44
# textcover reads the probes' log.txt files: merge copies of them only
rm -rf "$Q/cover"
for d in tour pages desc prov mhelp enc restitles restitles_0x17 restitles_0x29 restitles_0x33 go/dojo go/dojo0 go/lk swap; do
  (cd "$Q/$d" && find . -name log.txt) | while read -r f; do
    dst="$Q/cover/$(echo $d | tr / _)/$(dirname "$f")"; mkdir -p "$dst"; cp "$Q/$d/$f" "$dst/"
  done
done
echo "manifest dirs: $Q/tour $Q/pages $Q/desc $Q/prov $Q/restitles $Q/restitles_0x17 $Q/restitles_0x29 $Q/restitles_0x33 $Q/mhelp $Q/enc $Q/go/dojo $Q/go/dojo0 $Q/go/lk"

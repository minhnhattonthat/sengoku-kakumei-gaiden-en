#!/bin/sh
# Text coverage of story groups that only a story-flag branch shows: run ev003 once per group with
# liststep.lua SWAP=<group> (its first dialogue group replaced) and PAGES (A every 40 frames), textcover on.
#   sh tools/debug/swap_groups.sh OUTDIR ROM GROUP..      (GROUP = table address, e.g. 0x08730940)
# Output: OUTDIR/<group>/ev003/{log.txt,shots}; feed OUTDIR to tools/cover_report.py.
out=$1; rom=$2; shift 2
root=$(cd "$(dirname "$0")/../.." && pwd -W 2>/dev/null || pwd)
skill=$(python "$root/tools/skill.py")
ranges="RANGES='0804CE4C-0805043E,0805045C-08055BA6,0805E2AC-0805E776,08061C1C-08061C59,0807E090-0807EF1C,08201800-08202114,087C1000-087DFFFF'"
for g in "$@"; do
  python -X utf8 "$root/tools/debug/warp.py" ev003 --rom "$rom" --out "$out/$g" --shot-every 40 \
    --var PAGES=2400 --var LIST=0 --var "SWAP=$g" --script "$root/tools/lua/liststep.lua" \
    --script "$skill/scripts/lua/probes/textcover.lua" --var "$ranges"
done

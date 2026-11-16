"""story.py: the story script as the game groups it (docs/synopsis.md, docs/re/text.md).

    python -X utf8 tools/story.py groups [--en] > work/qa/story/groups.txt

The event tables hold dialogue groups: runs of string pointers ended by a 0 word. Each group is printed in
**display order** = pointer order in the table (proved in-game 2026-11-16, work/qa/order: group 0x730864 shows
しかも！敵は人間では… before 各地で我が軍は…), with its table address, so a reader sees the pages as the player does.
The strings themselves sit in ROM in the reverse order, so script/*.json (ROM order) lists a group last page first.
`--en` adds the English under each page.
"""
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom/Sengoku Kakumei Gaiden (Japan).gba"
TABLES = [(0x7303B8, 0x7311FC), (0x733868, 0x7338F8), (0x7341DC, 0x7343D8), (0x7469B0, 0x746CE8)]
REVERSED = False  # pointer order is display order (see the docstring)


def entries():
    out = {}
    for path in sorted((ROOT / "script").glob("*.json")):
        for e in json.loads(path.read_text(encoding="utf-8")):
            out[int(e["id"], 16)] = dict(e, bank=path.stem)
    return out


def groups(rom, ents):
    """[(table address of the group's first word, [entry, ...] in display order)]."""
    found = []
    for lo, hi in TABLES:
        run, start = [], None
        for a in range(lo, hi, 4):
            w = struct.unpack_from("<I", rom, a)[0]
            e = ents.get(w - 0x08000000) if 0x08000000 <= w < 0x0A000000 else None
            if e is not None and e["kind"] == "text":
                if start is None:
                    start = a
                run.append(e)
                continue
            if run:
                found.append((start, run[::-1] if REVERSED else run))
            run, start = [], None
        if run:
            found.append((start, run[::-1] if REVERSED else run))
    return found


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if not argv or argv[0] != "groups":
        print(__doc__)
        return 1
    rom = ROM.read_bytes()
    for start, run in groups(rom, entries()):
        print(f"## group {start:06x} ({len(run)} pages)")
        for e in run:
            print(f">> {e['id']} | {e['jp'].replace('|n', '')}")
            if "--en" in argv:
                print(f"   {e.get('en', '').replace('|n', ' ')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

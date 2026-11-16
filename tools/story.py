"""story.py: the story script as the game groups it (docs/synopsis.md, docs/re/text.md).

    python -X utf8 tools/story.py groups [--en] > work/qa/story/groups.txt

The event tables hold dialogue groups: runs of string pointers ended by a 0 word. Each group is printed in
**display order** = pointer order in the table (proved in-game 2026-11-16, work/qa/order: group 0x730864 shows
しかも！敵は人間では… before 各地で我が軍は…), with its table address, so a reader sees the pages as the player does.
The strings themselves sit in ROM in the reverse order, so script/*.json (ROM order) lists a group last page first.
`--en` adds the English under each page.

    python -X utf8 tools/story.py chapters [OUTDIR]   (default work/qa/story/chapters; story-pass input, CHAPTERS)
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


# Story-pass chapters (references/translation.md §Review): table ranges of groups, inclusive, by region/speaker as
# the tables hold them (docs/synopsis.md §Story by chapter; its chapters 5 and 10 are return talk inside 04 and the
# region files). Menus, item descriptions, link setup and results are not story and were reviewed per batch.
CHAPTERS = [
    ("01_kyushu", [(0x730830, 0x73091C)]),
    ("02_ryukyu", [(0x7341DC, 0x7343C4)]),
    ("03_mori", [(0x730930, 0x730A68)]),
    ("04_oda", [(0x730A78, 0x730BE8)]),
    ("06_sanada", [(0x730BF8, 0x730D1C)]),
    ("07_toyotomi", [(0x730D34, 0x730DE4)]),
    ("08_tokugawa", [(0x730DF8, 0x730E7C)]),
    ("09_date", [(0x730EA0, 0x730F80)]),
    ("11_ezo", [(0x730F90, 0x731008)]),
    ("12_ending", [(0x731010, 0x73106C)]),
    ("13_notices_profiles", [(0x731078, 0x7311F8)]),
]


def write_chapters(rom, ents, out):
    """One file per chapter: `## group` headers, then `>> id | group | JP` / `EN` in display order."""
    out.mkdir(parents=True, exist_ok=True)
    allg = groups(rom, ents)
    for name, ranges in CHAPTERS:
        lines = [f"# chapter {name} (story pass; pages in display order, |n = line break)"]
        for start, run in allg:
            if not any(lo <= start <= hi for lo, hi in ranges):
                continue
            lines.append(f"## group {start:06x} ({len(run)} pages)")
            for e in run:
                lines.append(f">> {e['id']} | {start:06x} | {e['jp'].replace('|n', '')}")
                lines.append(f"   {e.get('en', '').replace('|n', ' ')}")
        (out / f"{name}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(name, len(lines))


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if argv and argv[0] == "chapters":
        write_chapters(ROM.read_bytes(), entries(), Path(argv[1]) if len(argv) > 1 else ROOT / "work/qa/story/chapters")
        return 0
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

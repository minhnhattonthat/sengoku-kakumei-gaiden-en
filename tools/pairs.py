"""pairs.py: review input from script/ (docs/translator-brief.md, references/translation.md §Review).

    python -X utf8 tools/pairs.py [bank ...] > work/qa/review/pairs.txt

One `>> id | JP / EN` line per translated entry, banks in file order and entries in ROM order (story pages of one
dialogue are often stored in reverse display order: docs/re/text.md).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(banks):
    sys.stdout.reconfigure(encoding="utf-8")
    for path in sorted((ROOT / "script").glob("*.json")):
        if banks and path.stem not in banks:
            continue
        print(f"## bank {path.stem}")
        for e in json.loads(path.read_text(encoding="utf-8")):
            if e.get("en"):
                print(f">> {e['id']} | {e['jp']} / {e['en']}")


if __name__ == "__main__":
    main(sys.argv[1:])

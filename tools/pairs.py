"""pairs.py: review input from script/ (docs/translator-brief.md, references/translation.md §Review).

    python -X utf8 tools/pairs.py [bank ...] > work/qa/review/pairs.txt

One `>> id | JP / EN` line per translated entry, banks in file order and entries in ROM order. ROM order is the
reverse of display order inside each story dialogue group (docs/re/text.md); for story review use
`tools/story.py groups --en`, which prints display order.
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

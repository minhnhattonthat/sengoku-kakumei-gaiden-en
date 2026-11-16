"""script.py: the translation files in script/, one JSON per text bank (tools/textbank.py RANGES).

    python -X utf8 tools/script.py dump      write script/<bank>.json for every bank that has no file yet
    python -X utf8 tools/script.py update    refresh jp/sites/room/kind from the ROM, keep en/notes/status;
                                             an entry whose jp changed gets status "jp-changed" (re-check its en)
    python -X utf8 tools/script.py stats     entries and translated counts per bank

    import script; edits = script.load_en()   # {addr: en text} for every entry with an English text

Entry fields (one per pointed string, keyed by its ROM address):
    id      6-hex-digit ROM address of the string (stable; the pointer sites point here)
    sites   pointer sites (ROM offsets of the u32 0x08xxxxxx words that point at it)
    room    bytes usable in place, NUL included; a longer text is relocated to free space by the build
    kind    text      Japanese to translate
            debug     leftover debug-menu label in half-width katakana (0x04E008-0x04E20F), never shown in a
                      normal game; translate only if the debug menu is ever enabled
            code      no Japanese, only control sequences or ASCII (%n, %d,%d,%d, ???, error): keep as is
            dup       same string as `same_as` (menu help copy 2 at 0x04FDF0 = copy 1 at 0x04CE4C); its en is
                      taken from that entry unless it has its own
    jp      the original, decoded with tbl/jp.tbl, without the closing {end}; `|n` = new column, `%n` = name,
            `%d` = number, `%b %B %r` = save-confirm codes (docs/re/text.md); undecodable bytes are [XX]
    reading (debug entries) the bytes read as half-width katakana, e.g. ﾃﾞｰﾀｾﾝﾀｸ; jp shows them as EUC mojibake
    en      English ("" = untranslated: the build keeps the Japanese)
    notes, status   free text for translators and reviewers

The dump never overwrites a file; `update` never touches en, notes or status.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import textbank  # noqa: E402
from tbl import Table  # noqa: E402

SCRIPT = ROOT / "script"
END = "{end}"
DEBUG = (0x04E008, 0x04E210)  # half-width katakana labels of the leftover debug menu (mode 0)
DUP_BANKS = {"menu_help2": "menu_help1"}  # copy -> original, same strings in the same order
KEEP = ("en", "notes", "status")


def table():
    return Table.load(ROOT / "tbl" / "jp.tbl")


def decode(jp, raw):
    text = jp.decode(raw + b"\0")[0]
    assert text.endswith(END)
    return text[:-len(END)]


def encode(jp, text):
    data = jp.encode(text + END)
    if not data.endswith(b"\0") or b"\0" in data[:-1]:
        raise ValueError(f"text does not encode to one NUL-terminated string: {text!r}")
    return data[:-1]


def kind_of(addr, raw):
    if DEBUG[0] <= addr < DEBUG[1]:
        return "debug"
    if all(b < 0x80 for b in raw):
        return "code"
    return "text"


def fresh(rom=None):
    """{bank: [entry]} straight from the ROM, with empty en."""
    rom = rom or textbank.original_rom()
    jp = table()
    strs = textbank.strings(rom)
    banks = {name: [] for name, _, _ in textbank.RANGES}
    for addr in sorted(strs):
        s = strs[addr]
        banks[s.bank].append({
            "id": f"{addr:06x}",
            "sites": [f"{x:06x}" for x in sorted(s.sites)],
            "room": s.room,
            "kind": kind_of(addr, s.raw),
            "jp": decode(jp, s.raw),
            "en": "",
            "notes": "",
            "status": "",
        })
        if banks[s.bank][-1]["kind"] == "debug":
            banks[s.bank][-1]["reading"] = s.raw.decode("cp932")  # JIS X 0201 half-width katakana
    for copy, orig in DUP_BANKS.items():
        if [e["jp"] for e in banks[copy]] != [e["jp"] for e in banks[orig]]:
            raise ValueError(f"{copy} is no longer a copy of {orig}")
        for c, o in zip(banks[copy], banks[orig]):
            if c["kind"] == "text":
                c["kind"] = "dup"
                c["same_as"] = o["id"]
    return banks


def path_of(bank):
    return SCRIPT / f"{bank}.json"


def save(bank, entries):
    SCRIPT.mkdir(exist_ok=True)
    text = json.dumps(entries, indent=1, ensure_ascii=False) + "\n"
    with open(path_of(bank), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def load():
    """{bank: [entry]} from script/."""
    out = {}
    for name, _, _ in textbank.RANGES:
        p = path_of(name)
        if not p.exists():
            raise SystemExit(f"{p.relative_to(ROOT)} missing: run tools/script.py dump")
        out[name] = json.loads(p.read_text(encoding="utf-8"))
    return out


def load_en(banks=None):
    """{addr: text} for every entry the build should change: its own en, or a dup's source en."""
    banks = banks or load()
    by_id = {e["id"]: e for entries in banks.values() for e in entries}
    edits = {}
    for e in by_id.values():
        en = e.get("en", "")
        if not en and e.get("same_as"):
            en = by_id[e["same_as"]].get("en", "")
        if en:
            edits[int(e["id"], 16)] = en
    return edits


def dump():
    banks = fresh()
    for bank, entries in banks.items():
        if path_of(bank).exists():
            print(f"skip {bank}: script/{bank}.json exists (use update)")
            continue
        save(bank, entries)
        print(f"wrote script/{bank}.json  {len(entries)} entries")


def update():
    new = fresh()
    for bank, entries in new.items():
        old = {e["id"]: e for e in json.loads(path_of(bank).read_text(encoding="utf-8"))} if path_of(bank).exists() else {}
        changed = 0
        for e in entries:
            o = old.pop(e["id"], None)
            if o is None:
                continue
            for k in KEEP:
                e[k] = o.get(k, "")
            if o.get("jp") != e["jp"] and e["en"]:
                e["status"] = "jp-changed"
                changed += 1
        if old:
            raise SystemExit(f"{bank}: ids no longer in the ROM: {sorted(old)[:10]} (kept file unchanged)")
        save(bank, entries)
        print(f"updated script/{bank}.json  {len(entries)} entries, {changed} jp-changed")


def stats():
    for bank, entries in load().items():
        kinds = {}
        for e in entries:
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        done = sum(1 for e in entries if e["kind"] == "text" and e["en"])
        print(f"{bank:13} {len(entries):4} entries  {kinds}  translated {done}/{kinds.get('text', 0)}")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    {"dump": dump, "update": update, "stats": stats}[cmd]()


if __name__ == "__main__":
    main()

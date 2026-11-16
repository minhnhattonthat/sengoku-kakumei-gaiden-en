"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (for check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py rewrap                 re-break shipped lines with a stub last line (|n only)

Copied from the skill's assets/batches.py. Fit the ADAPTER section to this game's text format; the rest is shared.
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\|[nd]|%[nNdbBr]")  # tools/font_en.py CONTROLS; must survive translation
FREE = {"|n"}  # new line (next column): the English places its own breaks
VARIABLE = r"%d"  # a number the game draws: "1st" comes out as "1th"
# Honorifics are kept (glossary, D1). 殿/様 are also plain words here (殿 = my lord, 若殿, 殿下, 様子, 貴様, お兄様),
# so only a title right after a name is enforced: after %n, a glossary JP form, or either half of a 4-kanji name.
HONORIFICS = {"様": "-sama", "さま": "-sama", "殿": "-dono", "どの": "-dono"}
GENDERED = re.compile(r"\b(my boy|my lad|young man|my girl|young lady)\b", re.I)  # the hero's gender is chosen
READING = re.compile(r"（[ぁ-ゖー]+）")  # furigana in parentheses: 幸村（ゆきむら）様
# %n: the player's name, up to 8 letters, each drawn as a whole cell (name-entry letters are kana font glyphs,
# docs/re/name-entry.md), so 8 cells. A 4-cell budget split words after a full-length name (phase 8 tour).
NAME_CELLS = 8
BANK = {}  # id -> bank (script/<bank>.json), filled by docs()
# data/windows.tsv: (cells per line, lines) per box; results ids get their own budgets in width_problems.
SCROLL = (12, 3)
TIME_LABELS = {"07e2d4", "07e2dc", "07e2e4"}  # link time labels, guessed 3 cells x 1 line


def docs():
    """(path, doc, entries) per script file; entries hold id, jp, en, and optionally speaker, box, max, dup."""
    for path in sorted(SCRIPT.rglob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        entries = doc["entries"] if isinstance(doc, dict) else doc
        BANK.update((e["id"], path.stem) for e in entries)
        yield path, doc, entries


def needs_english(entry):
    """Empty JP isn't "untranslated": it would be re-queued forever. debug/code/dup entries need no English, nor
    text with no kana or kanji (061c1c is the arrows ↑↓, kept as the game's glyphs)."""
    has_jp = any(kind(c) != "other" for c in entry.get("jp", ""))
    return entry.get("kind") == "text" and has_jp and not entry.get("en")


def group_of(entry):
    """Entries with the same value stay in one batch: fragments of one sentence, split around a drawn number."""
    return entry.get("dup") or entry["id"]


def budget(entry):
    """(cells per line, lines) for this entry's box (data/windows.tsv)."""
    eid, bank = entry["id"], BANK.get(entry["id"])
    if eid in TIME_LABELS:
        return 3, 1
    if bank == "results":
        if "%d" in entry["jp"]:
            return 4, 1  # value column: 6 cells incl. one per digit, 2 digits budgeted
        if "20192c" <= eid <= "201bf0":
            return 11, 1  # title, first word (adjective): kana set, then kanji set from 201abc
        if "201bf8" <= eid <= "20210c":
            return 10, 1  # title, second word (noun), drawn one cell lower
        return 12, 1
    return SCROLL


def limit_label(entry):
    cells, lines = budget(entry)
    return f"{cells * 2}x{lines}"


def wrap(entry, en):
    """English with no |n is word-wrapped into the box's lines here; with any |n it is taken as written."""
    import font_en
    cells, lines = budget(entry)
    if "|n" in en or lines == 1:
        return en
    words = en.split()
    rows = balanced(words, cells, lines)
    if rows is None:  # does not fit: greedy, so the width check reports it
        rows = [""]
        for word in words:
            cand = f"{rows[-1]} {word}" if rows[-1] else word
            if rows[-1] and font_en.cells(cand) + NAME_CELLS * cand.count("%n") > cells:
                rows.append(word)
            else:
                rows[-1] = cand
    return "|n".join(rows)


STUB = 6  # a last line shorter than this (letters, %n = 8) is a stub: pipeline.md §Checks


def row_len(row):
    return len(row.replace("%n", "x" * 2 * NAME_CELLS))


def is_stub(row):
    return any(c.isalpha() for c in row.replace("%n", "")) and row_len(row.strip()) < STUB


def balanced(words, cells, lines):
    """Rows for words in at most `lines` lines of `cells` cells: fewest rows, then no stub last row, then the most
    even line lengths. None if the words do not fit."""
    import font_en

    def fits(row):
        return font_en.cells(row) + NAME_CELLS * row.count("%n") <= cells

    best = None

    def walk(i, rows):
        nonlocal best
        if i == len(words):
            score = (len(rows), is_stub(rows[-1]) and len(rows) > 1,
                     sum((2 * cells - row_len(r)) ** 2 for r in rows))
            if best is None or score < best[0]:
                best = (score, rows)
            return
        if len(rows) == lines:
            return
        for j in range(i + 1, len(words) + 1):
            row = " ".join(words[i:j])
            if not fits(row):
                break
            walk(j, rows + [row])

    walk(0, [])
    return best[1] if best else None


def stub_problem(entry, en):
    """A stub last line that a re-wrap of the same words would avoid (`batches.py rewrap` fixes it)."""
    cells, lines = budget(entry)
    rows = en.split("|n")
    if lines == 1 or len(rows) < 2 or rows[-1] == "" or not is_stub(rows[-1]):
        return []
    alt = balanced(" ".join(rows).split(), cells, lines)
    if alt and not (len(alt) > 1 and is_stub(alt[-1])):
        return [f"stub last line {rows[-1]!r}: run batches.py rewrap"]
    return []


def width_problems(entry, en):
    """Lines are |n-separated columns; a line's cells = its letter pairs (tools/font_en.py) + NAME_CELLS per %n."""
    import font_en
    cells, lines = budget(entry)
    rows = en.split("|n")
    if len(rows) > 1 and rows[-1] == "":
        rows = rows[:-1]
    out = []
    if len(rows) > lines:
        out.append(f"{len(rows)} lines, the box has {lines}")
    for row in rows:
        used = font_en.cells(row) + NAME_CELLS * row.count("%n")
        if used > cells:
            out.append(f"line over {cells} cells ({used}): {row!r}")
        if row != row.strip():
            out.append(f"line starts or ends with a space: {row!r}")
    return out


def encodable(char):
    """Read the project's table instead when it has glyphs beyond ASCII (a heart, say)."""
    return " " <= char <= "~"
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    """Every rule, on one line of English."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(c) and c != "\n"}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en:
        out.append("escape sequence or tab in the English")
    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. %d")')
    jp_plain = TOKEN.sub("", jp)
    flat = " ".join(TOKEN.sub(" ", en).split())  # a term may be wrapped across lines
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(e.lower() in flat.lower() for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", flat)]
    out += honorific_problems(jp, en, terms)
    if m := GENDERED.search(TOKEN.sub(" ", en)):
        out.append(f"genders the hero: {m.group(0)!r} (the player picks male or female)")
    return out + width_problems(entry, en) + stub_problem(entry, en)


def name_forms(terms):
    """%n, every glossary JP form, and both halves of a 4-kanji name (豊臣秀吉 -> 豊臣, 秀吉)."""
    names = {"%n"}
    for jps, _, _ in terms:
        for j in jps:
            names.add(j)
            if len(j) == 4 and all(kind(c) == "kanji" for c in j):
                names |= {j[:2], j[2:]}
    return names


def honorific_problems(jp, en, terms):
    text = READING.sub("", jp.replace("|n", ""))
    out = []
    for hon, en_form in HONORIFICS.items():
        hit = [n for n in name_forms(terms) if re.search(re.escape(n + hon) + "(?!下)", text)]
        if hit and en_form not in en.lower():
            out.append(f"honorific {max(hit, key=len)}{hon} needs {en_form}")
    return out


def index():
    return {e["id"]: e for _, _, entries in docs() for e in entries}


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for _, _, entries in docs():
        for e in entries:
            if needs_english(e) and e["id"] not in taken:
                groups.setdefault(group_of(e), []).append(e)
    batches, cur, chars = [], [], 0
    for group in groups.values():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{e['id']}\t{e.get('speaker', '')}\t{e.get('box', '')}\t{limit_label(e)}\t{e['jp']}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]) for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    rows = [(i, wrap(entries[i], en) if i in entries else en) for i, en in rows]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
    return bad, dict(rows)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if e["id"] in new and e.get("en") and e["en"] != new[e["id"]]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            if e["id"] in new and e.get("en") != new[e["id"]]:
                e["en"], e["status"] = new[e["id"]], "done"
                touched = True
                changed += 1
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def rewrap():
    """Re-break every shipped line flagged with a stub last line: only the |n positions change, never a word."""
    new = {}
    for _, _, entries in docs():
        for e in entries:
            en = e.get("en", "")
            if en and stub_problem(e, en):
                cells, lines = budget(e)
                rows = balanced(" ".join(en.split("|n")).split(), cells, lines)
                if " ".join(rows).split() != " ".join(en.split("|n")).split():
                    sys.exit(f"{e['id']}: rewrap would change words")
                new[e["id"]] = "|n".join(rows)
    merge(new, overwrite=True)


def fix(names):
    """Apply work/tl/bNNN.fix.tsv (id<TAB>English, any subset) onto bNNN.out.tsv, then delete the fix file."""
    for batch in names:
        fixes = dict((r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.fix.tsv"))
        out = TL / f"{batch}.out.tsv"
        rows = read_tsv(out)
        if unknown := set(fixes) - {r[0] for r in rows}:
            sys.exit(f"{batch}: fix ids not in the batch: {sorted(unknown)}")
        out.write_text("".join(f"{r[0]}\t{fixes.get(r[0], chr(9).join(r[1:]))}\n" for r in rows),
                       encoding="utf-8", newline="\n")
        (TL / f"{batch}.fix.tsv").unlink()
        print(f"{batch}: {len(fixes)} lines replaced")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    if cmd == "fix":
        return fix(args)
    if cmd == "rewrap":
        return rewrap()
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        print(f"{len(entries)} entries, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    new, failed = {}, 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        new.update(rows)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
    if failed:
        return 1
    if cmd == "merge":
        merge(new, overwrite)
    return 0


def _selftest():
    import tempfile
    global ROOT, TL, SCRIPT, GLOSSARY
    with tempfile.TemporaryDirectory() as d:
        ROOT = Path(d)
        TL, SCRIPT, GLOSSARY = ROOT / "work/tl", ROOT / "script", ROOT / "glossary.md"
        SCRIPT.mkdir()
        GLOSSARY.write_text("| JP | EN | max | notes | Avoid |\n|---|---|---|---|---|\n| ミン | Min | | | Minn |\n", encoding="utf-8")
        script = [{"id": "a", "kind": "text", "jp": "ミンが来た|n", "en": ""},
                  {"id": "b", "kind": "text", "jp": "タイミング", "en": ""},
                  {"id": "c", "kind": "text", "jp": "", "en": ""}, {"id": "d", "kind": "text", "jp": "%d番", "en": ""},
                  {"id": "e", "kind": "code", "jp": "%d", "en": ""}]
        (SCRIPT / "s.json").write_text(json.dumps(script), encoding="utf-8")
        assert main(["split"]) is None
        assert [r[0] for r in read_tsv(TL / "b001.tsv")] == ["a", "b", "d"]  # c has no JP
        assert "ミン\tMin" in (ROOT / "build/terms_b001.txt").read_text(encoding="utf-8")
        split(3500)
        assert len(existing()) == 1  # a repeat run makes no duplicate batch
        out = TL / "b001.out.tsv"
        out.write_text("a\tHe came\nb\tTiming\n", encoding="utf-8")
        assert main(["check", "b001"]) == 1  # d missing, a lacks the glossary term
        out.write_text("a\tMin came\nb\tTiming\nd\t%dth\n", encoding="utf-8")
        assert main(["merge", "b001"]) == 1  # ordinal after a variable: nothing written
        assert index()["a"]["en"] == ""
        out.write_text("a\tMinn and Min came\nb\tTiming\nd\tNo. %d\n", encoding="utf-8")
        assert main(["check", "b001"]) == 1  # the Avoid spelling
        out.write_text("a\tMin came\nb\tThe timing\nd\tNo. %d\n", encoding="utf-8")
        assert main(["merge", "b001"]) == 0 and index()["b"]["en"] == "The timing"
        assert main(["check"]) == 0
        out.write_text("a\tMin arrived\nb\tThe timing\nd\tNo. %d\n", encoding="utf-8")
        try:
            main(["merge", "b001"])
            raise AssertionError("merge replaced English")
        except SystemExit:
            pass
        assert main(["merge", "b001", "--overwrite"]) == 0 and index()["a"]["en"] == "Min arrived"
        long = "Min walked all the way from the far north to the capital"
        assert wrap(index()["a"], long) == "Min walked all the|nway from the far|nnorth to the capital"  # balanced
        assert width_problems(index()["a"], wrap(index()["a"], long + " in a single night")) == ["4 lines, the box has 3"]
        # odd runs around %n pad to a whole cell: 3 + 8 (name) + 9 cells
        assert width_problems(index()["a"], "Min, %n, a long greeting") == [
            "line over 12 cells (20): 'Min, %n, a long greeting'"]
    print("selftest ok")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        sys.exit(main(sys.argv[1:]))

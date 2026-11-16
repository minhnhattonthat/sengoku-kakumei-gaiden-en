"""marker.py: marker texts for the phase-5 marker build (`python -X utf8 build.py marker [ID=text ...]`).

Every `text` and `dup` entry becomes `[id]` plus filler, line for line: a Japanese line of k characters (k glyph
cells) becomes 2k English letters, which is k cells again with the 2-letters-per-cell font, so every box shows the
same layout as the Japanese, with its id at the start. Controls (|n %n %d %b %B %r) stay where they were.
`debug` (half-width katakana debug menu) and `code` (format strings) entries keep their bytes.

ID=text arguments override single entries (width gate stress lines); ID=TORTURE gives the glyph torture line.
STRESS=1 turns every entry into its id line plus one 14-cell ruler per Japanese line (stress(), the width gate).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402

FILL = "The quick brown fox jumps over the lazy dog. "
TORTURE = "".join(chr(c) for c in range(0x21, 0x7F)) + "  a  b"


def filler(n, offset=0):
    s = (FILL * (n // len(FILL) + 2))[offset:offset + n]
    return s


def marker(eid, jp):
    lines = jp.split("|n")
    out, first, used = [], True, 0
    for line in lines:
        parts = []
        for ctl, run in font_en.tokens(line):
            if ctl:
                parts.append(run)
                continue
            n = 2 * len(run)
            if first:
                tag = f"[{eid}]"
                n = max(0, n - len(tag))
                parts.append(tag + filler(n, used))
                first = False
            else:
                parts.append(filler(n, used))
            used = (used + n) % len(FILL)
        out.append("".join(parts))
    if first:          # no plain text at all (a line of only controls): still show the id
        out[0] = f"[{eid}]" + out[0]
    return "|n".join(out)


RULER = "0123456789abcdefghijklmnopqr"   # 14 cells: the last pair you can see gives the column's cell count


def stress(eid, jp):
    """Width gate: the id on its own line, then every Japanese line as a 14-cell ruler (cell k shows chars 2k-2..)."""
    lines = []
    for line in jp.split("|n"):
        ctl = "".join(t for c, t in font_en.tokens(line) if c)
        lines.append(ctl + RULER if any(not c for c, _ in font_en.tokens(line)) else ctl)
    return f"[{eid}]|n" + "|n".join(lines)


def texts(banks, qa=None):
    qa = dict(qa or {})
    make = stress if qa.pop("STRESS", None) else marker
    out = {}
    for entries in banks.values():
        for e in entries:
            if e["kind"] not in ("text", "dup"):
                continue
            out[int(e["id"], 16)] = make(e["id"], e["jp"])
    for k, v in qa.items():
        out[int(k, 16)] = TORTURE if v == "TORTURE" else v
    return out


if __name__ == "__main__":
    print(marker("05045c", "伊達政宗"))
    print(marker("050500", "よくきたな|n%nよ。"))
    print(marker("061c1c", "%b%n　%Bでいいですか？|n%rＡ…決定　Ｂ…戻る|n"))

"""OBJ label strips (menu headers etc.): 16 px wide vertical labels stored as 2-tile-wide 4bpp runs in a sprite bank
(tools/sprites.py). Viewed with 2 tiles per row, a bank is one tall 16 px strip; each label is a run of non-blank
rows. English is drawn rotated 90 degrees clockwise (reads top to bottom, as D8's text) with font_en's 5x9 letters.

    python -X utf8 tools/gfx_labels.py segments BANK          list the label runs (strip rows) and colour counts
    python -X utf8 tools/gfx_labels.py preview BANK OUT.png   original | English, side by side, from gfx/<bank>.tsv

gfx/bankNN.tsv: start<TAB>rows<TAB>jp<TAB>en   (start/rows in strip pixel rows; en empty = keep)
Build: labels_edits(rom) -> {offset: bytes} raw tile writes, for build.py.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font_en  # noqa: E402
import sprites  # noqa: E402
import textbank  # noqa: E402

W = 16
# Palette indices of a label box (bank 22, menu headers): 0 transparent, BG box fill, INK letters, EDGE outline.
STYLE = {22: {"bg": None, "ink": None, "edge": None}}


def strip(rom, bank):
    """Bank tiles as rows of 16 index pixels (2 tiles per 8-row band)."""
    b = sprites.banks(rom)[bank]
    data = rom[b["tiles"]:b["end"]]
    ntiles = len(data) // 32
    rows = []
    for band in range(ntiles // 2):
        for y in range(8):
            row = []
            for t in (2 * band, 2 * band + 1):
                for x in range(4):
                    v = data[t * 32 + y * 4 + x]
                    row += [v & 15, v >> 4]
            rows.append(row)
    return b, rows


def pack(rows, b):
    """Inverse of strip(): rows of 16 indices -> tile bytes."""
    out = bytearray(b["end"] - b["tiles"])
    for i, row in enumerate(rows):
        band, y = divmod(i, 8)
        for half in range(2):
            t = 2 * band + half
            for x in range(4):
                out[t * 32 + y * 4 + x] = row[half * 8 + 2 * x] | (row[half * 8 + 2 * x + 1] << 4)
    return bytes(out)


BLANK = (0, 15)  # transparent, white: the strip between labels
BG = range(10, 15)  # the peach gradient behind the letters (10 top .. 14 bottom, then white 15)
INK, SHADE = 1, 8   # black letter, mid-tone shadow (lower right, upright view)
GRADIENT = (10, 11, 13, 14)  # the original box's bands, top to bottom
PAD = 6
ADV = 6  # px per letter: font_en's 5 columns + 1 gap (a smeared bold closed up m and w)


def blank(row):
    return all(v in BLANK for v in row)


def segments(rows):
    segs, start = [], None
    for i, row in enumerate(rows + [[0] * W]):
        if not blank(row) and start is None:
            start = i
        elif blank(row) and start is not None:
            segs.append((start, i - start))
            start = None
    return segs


def load_tsv(bank):
    path = ROOT / "gfx" / f"bank{bank:02d}.tsv"
    out = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                start, n, jp, en = (line.split("\t") + [""])[:4]
                out.append((int(start), int(n), jp, en))
    return out


def colours(rows):
    hist = {}
    for row in rows:
        for v in row:
            hist[v] = hist.get(v, 0) + 1
    return hist


def draw(text, n, orig):
    """English label over a whole slot of n rows x 16 px (one OBJ frame, white below its box): a new gradient box
    from the original's first row, PAD rows longer than the text at each end, white after it; `text` is drawn
    rotated clockwise (letter rows run right to left across the strip, letters top to bottom) in font_en's 5x9
    letters with a mid-tone shadow."""
    glyphs = [font_en.FONT.get(c, font_en.FONT[" "]) for c in font_en.fold(text)]
    length = len(glyphs) * ADV - 1
    c0 = next(i for i, row in enumerate(orig) if not blank(row))
    box = length + 2 * PAD
    if c0 + box > n:
        raise ValueError(f"{text!r}: box {box} rows from row {c0}, slot {n}")
    out = [[15] * W for _ in range(n)]
    for i in range(box):
        out[c0 + i] = [GRADIENT[i * len(GRADIENT) // box]] * W
    y0 = c0 + PAD
    x_top = (W + 9) // 2 + 1  # 9 letter rows (cap 0-6, descender 7-8) + 1 shadow column, centred
    ink = set()
    for k, g in enumerate(glyphs):
        for r, line in enumerate(g):
            for c, ch in enumerate(line):
                if ch == "#":
                    ink.add((y0 + k * ADV + c, x_top - r))
    for y, x in ink:  # shadow one px right and down in the upright view = down and left in the strip
        for yy, xx in ((y + 1, x), (y, x - 1), (y + 1, x - 1)):
            if (yy, xx) not in ink and 0 <= yy < n and 0 <= xx < W:
                out[yy][xx] = SHADE
    for y, x in ink:
        out[y][x] = INK
    return out


def english_rows(rom, bank):
    b, rows = strip(rom, bank)
    new = [list(r) for r in rows]
    for start, n, jp, en in load_tsv(bank):
        if en:
            new[start:start + n] = draw(en, n, rows[start:start + n])
    return b, rows, new


def labels_edits(rom, banks=None):
    edits = {}
    for path in sorted((ROOT / "gfx").glob("bank*.tsv")):
        bank = int(path.stem[4:])
        if banks is not None and bank not in banks:
            continue
        b, rows, new = english_rows(rom, bank)
        if new != rows:
            edits[b["tiles"]] = pack(new, b)
    return edits


def preview(rom, bank, out):
    from PIL import Image
    b, rows, new = english_rows(rom, bank)
    pal = rom[b["pal"]:b["pal"] + 32]
    rgb = []
    for i in range(16):
        c = pal[2 * i] | pal[2 * i + 1] << 8
        rgb.append(((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31))
    rgb[0] = (255, 0, 255)
    segs = [s for s in load_tsv(bank) if s[3]]
    h = max(n for _, n, _, _ in segs)
    im = Image.new("RGB", (len(segs) * 2 * (W + 4), h), (40, 40, 40))
    for i, (start, n, _, _) in enumerate(segs):
        for j, src in enumerate((rows, new)):
            for y in range(n):
                for x in range(W):
                    im.putpixel(((2 * i + j) * (W + 4) + x, y), rgb[src[start + y][x]])
    im.resize((im.size[0] * 3, h * 3), Image.NEAREST).save(out)
    print(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["segments", "preview"])
    ap.add_argument("bank", type=int)
    ap.add_argument("out", nargs="?")
    a = ap.parse_args()
    rom = textbank.original_rom()
    if a.cmd == "segments":
        b, rows = strip(rom, a.bank)
        for start, n in segments(rows):
            print(f"{start}\t{n}\t{colours(rows[start:start + n])}")
    else:
        preview(rom, a.bank, a.out)


if __name__ == "__main__":
    main()

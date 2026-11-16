"""Latin name entry (docs/re/name-entry.md).

The name-entry grid (`newgame_name`) is part of a BG picture (tiles = LZ block 0x5AEA30, loaded at VRAM 0; the
BG2 tilemap at VRAM 0x4000 is built at run time, so the grid area's entries are captured once into
data/name_grid_map.tsv). The cursor picks an index into the u32 EUC table at 0x733660 (85 kana in gojuon order);
the name is stored as those indices and printed through the font. So the game keeps its kana codes and this
module changes only pictures:
  - glyph_overrides(): the font entries of those kana (engine.font_table) become one Latin letter each, rotated
    clockwise like the English text, centred in the 12 px cell (a name reads one letter per cell);
  - lz_edits(rom): each kana cell of the grid picture is cleared (ink 1/15 filled from the nearest background
    pixel of the same tile) and gets the same letter, white 15 with a black 1 edge.

    python -X utf8 tools/name_grid.py capture VRAM.bin     write data/name_grid_map.tsv from a newgame_name dump
    python -X utf8 tools/name_grid.py preview OUT.png      original | English grid, from the dump-free build data
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import lz77  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TABLE = 0x733660   # 85 u32 EUC codes, index 0 = あ
COUNT = 85
BLOCK = 0x5AEA30   # LZ77 tiles of the name-entry picture (VRAM 0x0000..)
MAP_TSV = ROOT / "data" / "name_grid_map.tsv"
INK, EDGE = 15, 1

# Table index -> letter, laid out so the grid reads in order when the screen is turned (columns = rows).
# Block 1 (top, 9 columns right to left): あ さ な ま ら が だ ば ゃ; block 2 (8 columns): か た は や わ ざ ぱ ぁ.
LETTERS = {}
for start, chars in [(0, "ABCDE"), (10, "FGHIJ"), (20, "KLMNO"), (30, "PQRST"), (40, "UVWXY"), (50, "Z.-'!"),
                     (60, "01234"), (65, "56789"), (80, "?&,+"),
                     (5, "abcde"), (15, "fghij"), (25, "klmno"), (45, "stuvw"), (55, "xyz:~"),
                     (70, "()*/="), (75, "#@;\"$")]:
    for k, ch in enumerate(chars):
        LETTERS[start + k] = ch
LETTERS.update({35: "p", 37: "q", 39: "r"})  # や ゆ よ (36 and 38 are full-width spaces: gaps in the grid)

BLOCK1 = [range(0, 5), range(10, 15), range(20, 25), range(30, 35), range(40, 45), range(50, 55), range(60, 65),
          range(65, 70), range(80, 84)]
BLOCK2 = [range(5, 10), range(15, 20), range(25, 30), range(35, 40), range(45, 50), range(55, 60), range(70, 75),
          range(75, 80)]
COL_X0, PITCH = 165, 12          # screen x of the rightmost column; columns go left
LABELS = [("Done", (57, 119, 11, 24))]  # 決定 (confirm) left of block 2: screen x, y, w, h
# 名前入力 header: a 16 px peach-gradient column (indices 10-15 banded by row) with black brush ink 1-9; each row
# is refilled from its edge pixel, then black 1 letters with a mid-tone 8 shadow (as gfx/bank22).
HEADERS = [("Your Name", (216, 4, 16, 57))]
ROW_Y0 = {1: 19, 2: 83}          # screen y of each block's first row


def cells():
    """{table index: (screen x0, y0)} of each grid cell (12x12)."""
    out = {}
    for blk, cols in ((1, BLOCK1), (2, BLOCK2)):
        for c, rng in enumerate(cols):
            for r, k in enumerate(rng):
                out[k] = (COL_X0 - PITCH * c, ROW_Y0[blk] + PITCH * r)
    return out


def codes(rom):
    return [struct.unpack_from("<I", rom, TABLE + 4 * k)[0] for k in range(COUNT)]


def letter_points(ch):
    """{(dy, dx)} in a 12x12 cell: font_en letter rotated clockwise (letter row r -> x X_TOP - r), centred along
    the column."""
    art = font_en.FONT[ch]
    span = [c for c in range(font_en.W) if any(row[c] == "#" for row in art)]
    w = span[-1] - span[0] + 1
    top = (font_en.CELL - w) // 2 - span[0]
    return {(top + c, font_en.X_TOP - r) for r in range(font_en.H) for c in range(font_en.W) if art[r][c] == "#"}


def glyph(ch):
    rows = [0] * font_en.GLYPH_ROWS
    for y, x in letter_points(ch):
        rows[y] |= 0x8000 >> x
    return b"".join(struct.pack(">H", v) for v in rows)


def glyph_overrides(rom):
    """{(code byte 0, code byte 1): 26 glyph bytes} for engine.font_table."""
    out = {}
    for k, code in enumerate(codes(rom)):
        if k in LETTERS:
            out[(code & 0xFF, code >> 8)] = glyph(LETTERS[k])
    return out


def load_map():
    m = {}
    for line in MAP_TSV.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            tx, ty, e = line.split("\t")
            m[(int(tx), int(ty))] = int(e, 16)
    return m


def where(m, x, y):
    """(byte index into the tile data, high nibble?, tile) of screen pixel x, y."""
    e = m[(x // 8, y // 8)]
    t, hf, vf = e & 0x3FF, e >> 10 & 1, e >> 11 & 1
    xx, yy = x % 8, y % 8
    if hf:
        xx = 7 - xx
    if vf:
        yy = 7 - yy
    return t * 32 + yy * 4 + xx // 2, xx & 1, t


def redraw(tiles, rom):
    """English grid drawn into a copy of the decompressed tile block."""
    m = load_map()
    data = bytearray(tiles)

    def get(x, y):
        i, hi, _ = where(m, x, y)
        return data[i] >> 4 if hi else data[i] & 15

    def put(x, y, v):
        i, hi, _ = where(m, x, y)
        data[i] = (data[i] & 0x0F) | (v << 4) if hi else (data[i] & 0xF0) | v

    spots = {}  # tile -> the screen tile positions showing it: an edited tile must show in one place only
    for (tx, ty), e in m.items():
        spots.setdefault(e & 0x3FF, set()).add((tx, ty))
    def clear(x0, y0, w, h):
        """Every ink pixel takes the nearest non-ink pixel of its own tile (same palette)."""
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if get(x, y) not in (INK, EDGE):
                    continue
                best = None
                for d in range(1, 8):
                    for yy in range(y - d, y + d + 1):
                        for xx in range(x - d, x + d + 1):
                            if (x // 8, y // 8) != (xx // 8, yy // 8):
                                continue
                            v = get(xx, yy)
                            if v not in (INK, EDGE) and best is None:
                                best = v
                    if best is not None:
                        break
                put(x, y, best if best is not None else 0)

    for k, (x0, y0) in cells().items():
        if codes(rom)[k] == 0xA1A1:  # full-width space: an empty slot
            continue
        clear(x0, y0, PITCH, PITCH)
        if k not in LETTERS:
            continue
        pts = {(y0 + dy, x0 + dx) for dy, dx in letter_points(LETTERS[k])}
        for y, x in pts:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if (yy, xx) not in pts and y0 <= yy < y0 + PITCH and x0 <= xx < x0 + PITCH:
                        put(xx, yy, EDGE)
        for y, x in pts:
            put(x, y, INK)
    for text, (x0, y0, w, h) in LABELS:
        clear(x0, y0, w, h)
        import gfx_labels
        length = gfx_labels.text_width(text)
        pts = {(y, x) for y, x in gfx_labels.letter_points(text, y0 + (h - length) // 2, x0 + w - 2)}
        for y, x in pts:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (y + dy, x + dx) not in pts:
                        put(x + dx, y + dy, EDGE)
        for y, x in pts:
            put(x, y, INK)
    for text, (x0, y0, w, h) in HEADERS:
        import gfx_labels
        for y in range(y0, y0 + h):
            left, right = get(x0, y), get(x0 + w - 1, y)
            for x in range(x0 + 1, x0 + w - 1):
                put(x, y, left if (x - x0) % 2 else right)
        length = gfx_labels.text_width(text)
        if length > h:
            raise ValueError(f"header {text!r}: {length} rows, room {h}")
        pts = gfx_labels.letter_points(text, y0 + (h - length) // 2, x0 + 12)
        for y, x in pts:
            for yy, xx in ((y + 1, x), (y, x - 1), (y + 1, x - 1)):
                if (yy, xx) not in pts:
                    put(xx, yy, 8)
        for y, x in pts:
            put(x, y, 1)
    for t in range(len(data) // 32):
        if data[t * 32:t * 32 + 32] != tiles[t * 32:t * 32 + 32] and len(spots.get(t, ())) != 1:
            raise ValueError(f"edited tile {t} shows at {sorted(spots.get(t, ()))}")
    return bytes(data)


def lz_edits(rom):
    tiles = lz77.decompress(rom, BLOCK)[0]
    return {BLOCK: redraw(tiles, rom)}


def capture(vram_path):
    v = Path(vram_path).read_bytes()
    lines = ["# BG2 tilemap entries (VRAM 0x4000, 32x32) over the name-entry grid, captured from a newgame_name",
             "# dump by tools/name_grid.py capture (the game builds this map at run time). tx\tty\tentry"]
    for ty in range(0, 152 // 8):
        for tx in range(56 // 8, 240 // 8):
            e = struct.unpack_from("<H", v, 0x4000 + 2 * (ty * 32 + tx))[0]
            lines.append(f"{tx}\t{ty}\t{e:04x}")
    MAP_TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(MAP_TSV, len(lines) - 2, "entries")


def preview(out, vram_path, pal_path):
    """Grid area from a dump's VRAM/palette, original | English, 3x."""
    from PIL import Image
    import textbank
    rom = textbank.original_rom()
    v = Path(vram_path).read_bytes()
    pal = Path(pal_path).read_bytes()
    m = load_map()
    tiles = lz77.decompress(rom, BLOCK)[0]
    new = redraw(tiles, rom)
    x0, y0, w, h = 64, 16, 120, 136
    im = Image.new("RGB", (2 * w + 4, h))
    for j, data in enumerate((tiles, new)):
        for y in range(h):
            for x in range(w):
                i, hi, _ = where(m, x0 + x, y0 + y)
                p = m[((x0 + x) // 8, (y0 + y) // 8)] >> 12
                vv = data[i] >> 4 if hi else data[i] & 15
                c = struct.unpack_from("<H", pal, 32 * p + 2 * vv)[0]
                im.putpixel((j * (w + 4) + x, y), ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8))
    assert v  # the dump only gives the palette here
    im.resize((im.size[0] * 3, h * 3), Image.NEAREST).save(out)
    print(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["capture", "preview"])
    ap.add_argument("args", nargs="*")
    a = ap.parse_args()
    if a.cmd == "capture":
        capture(a.args[0])
    else:
        preview(*a.args)


if __name__ == "__main__":
    main()

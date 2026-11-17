"""Latin name entry (docs/re/name-entry.md).

The name-entry grid (`newgame_name`) is part of a BG picture (tiles = LZ block 0x5AEA30, loaded at VRAM 0; the
BG2 tilemap at VRAM 0x4000 is built at run time, so the grid area's entries are captured once into
data/name_grid_map.tsv). The cursor picks an index into the u32 EUC table at 0x733660 (85 kana in gojuon order);
the name is stored as those indices and printed through the font. So the game keeps its kana codes and this
module changes only pictures:
  - glyph_overrides(): the font entries of those kana (engine.font_table, the v1 marker build) become one Latin
    letter each, upright in the 12 px cell; the release build uses manga.name_glyph instead (build.manga_overrides);
  - lz_edits(rom): each kana cell of the grid picture is cleared (ink 1/15 filled from the nearest background
    pixel of the same tile) and gets the same letter upright, white 15 with a black 1 edge; the 名前入力 header
    and 決定 get upright stacked English (tools/upright.py).

    python -X utf8 tools/name_grid.py capture VRAM.bin [MAP.tsv]   write data/name_grid_map.tsv (or MAP.tsv) from a
                                                                   newgame_name dump (group 7: name_grid_map7.tsv)
    python -X utf8 tools/name_grid.py preview OUT.png VRAM PAL [BLOCK]  original | English grid of one picture
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import lz77  # noqa: E402
import upright  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TABLE = 0x733660   # 85 u32 EUC codes, index 0 = あ
COUNT = 85
BLOCK = 0x5AEA30   # LZ77 tiles of the name-entry picture (VRAM 0x0000..)
MAP_TSV = ROOT / "data" / "name_grid_map.tsv"
# Mode 16 loads picture group 6 (BLOCK) or, when [0x030016FC] != 0 and the save's +0xC field != 1 (0x08010D6A),
# group 7: the same grid, header and 決定 in the same places and inks over a pink pattern, its own tiles and map.
PICTURES = {BLOCK: MAP_TSV, 0x5B14B4: ROOT / "data" / "name_grid_map7.tsv"}
# Header brush ink per picture (HEADER_FILL names the set): 1-9, and in group 6 its light grey antialias 12 (never a
# band there: bands are 10, 11, 13-15). Group 7's header spans tiles on palettes 2 and 4, so one index is two shades.
HEADER_FILL = {BLOCK: "edges", 0x5B14B4: "mode"}
HEADER_INK = {"edges": set(range(1, 10)) | {12}, "mode": set(range(1, 10))}
# Raw BG palettes of each picture (record +16 of 0x74F9C4, 0x74FAC8; slot 1 up): the header refill works in their
# lightness.
HEADER_PAL = {BLOCK: 0x74F924, 0x5B14B4: 0x74F9E8}
BAYER = ((0.125, 0.625), (0.875, 0.375))   # 2x2 ordered dither thresholds, [y % 2][x % 2]
HEADER_H = {BLOCK: 58, 0x5B14B4: 58}  # both 名前入力 brushes run to row 61 (group 6's antialiased tail too)
INK, EDGE = 15, 1

# Table indices of each grid column, right to left, as the game's cursor enters them (logged with
# tools/lua/namelog.lua, owner's state work/states/onmyou_name_input.mss): block 1 (top, 9 columns) あ さ な ま ら
# が だ ぱ(70-74) ゃ; block 2 (8 columns) か た は や わ ざ ば(65-69) ぁ. (Until D19 the ぱ/ば columns were swapped
# here, so B in the picture entered b: owner bug report.)
BLOCK1 = [range(0, 5), range(10, 15), range(20, 25), range(30, 35), range(40, 45), range(50, 55), range(60, 65),
          range(70, 75), range(80, 84)]
BLOCK2 = [range(5, 10), range(15, 20), range(25, 30), range(35, 40), range(45, 50), range(55, 60), range(65, 70),
          range(75, 80)]
GAPS = (36, 38)   # full-width spaces in the table: empty grid slots


def _rows_left_to_right(block, chars):
    """{table index: letter}: `chars` in reading order, rows top to bottom, each row left to right (the block's
    columns run right to left), skipping the gaps."""
    out, it = {}, iter(chars)
    for r in range(5):
        for col in reversed(block):
            if r < len(col) and col[r] not in GAPS:
                out[col[r]] = next(it)
    assert next(it, None) is None
    return out


# Table index -> letter (D18: the letters are drawn upright, so the grid reads A-I across the top row, left to
# right, as English does; the name is still stored as these indices).
LETTERS = {**_rows_left_to_right(BLOCK1, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-'!?&,+"),
           **_rows_left_to_right(BLOCK2, "abcdefghijklmnopqrstuvwxyz:~()*/=#@;\"$")}
COL_X0, PITCH = 165, 12          # screen x of the rightmost column; columns go left
LABELS = [("OK", (57, 119, 11, 24))]  # 決定 (confirm) left of block 2: screen x, y, w, h
LABEL_CLEAR_W = 12  # 決定's outline reaches x 68, one column past the letters' w: cleared too
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
    """{(dy, dx)} in a 12x12 cell: font_en letter upright (cap rows 0-6, descender 7-8 at cell rows 1-9), centred
    across the cell."""
    art = font_en.FONT[ch]
    span = [c for c in range(font_en.W) if any(row[c] == "#" for row in art)]
    w = span[-1] - span[0] + 1
    left = (font_en.CELL - w) // 2 - span[0]
    return {(1 + r, left + c) for r in range(font_en.H) for c in range(font_en.W) if art[r][c] == "#"}


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


def load_map(path=MAP_TSV):
    m = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
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


def lightness(rom, pal, p, i):
    """Lightness of colour i of map palette p: the raw palettes load from BG slot 1, so slot p = raw p - 1 (checked
    against palette dumps of both name-entry screens)."""
    c = struct.unpack_from("<H", rom, pal + 32 * (p - 1) + 2 * i)[0]
    return 0.3 * (c & 31) + 0.59 * (c >> 5 & 31) + 0.11 * (c >> 10 & 31)


def header_ramp(samples, y0, h):
    """{row: target lightness} for the header refill. samples: {row: lightness of the original's background there}
    (rows the brush covers have none). Gaps are interpolated, a median over 7 rows drops stray brush antialias, the
    ramp is held monotone (the gradient runs one way), and each step between two bands is split over its two rows
    (1/3, 2/3) so the dither draws a 2-row checkerboard there, as the original does, never a lone dotted row."""
    rows = list(range(y0, y0 + h))
    known = sorted(samples)
    raw = {}
    for y in rows:
        lo = max((k for k in known if k <= y), default=None)
        hi = min((k for k in known if k >= y), default=None)
        if lo is None or hi is None:
            raw[y] = samples[lo if hi is None else hi]
        else:
            raw[y] = samples[lo] if hi == lo else samples[lo] + (samples[hi] - samples[lo]) * (y - lo) / (hi - lo)
    med = {y: sorted(raw[k] for k in rows[max(0, i - 3):i + 4])[len(rows[max(0, i - 3):i + 4]) // 2]
           for i, y in enumerate(rows)}
    up = med[rows[-1]] >= med[rows[0]]
    mono, cur = {}, None
    for y in rows:
        cur = med[y] if cur is None else (max(cur, med[y]) if up else min(cur, med[y]))
        mono[y] = cur
    out = dict(mono)
    for a, b in zip(rows, rows[1:]):
        if mono[a] != mono[b] and mono.get(a - 1) == mono[a] and mono.get(b + 1, mono[b]) == mono[b]:
            out[a] = mono[a] + (mono[b] - mono[a]) / 3
            out[b] = mono[a] + (mono[b] - mono[a]) * 2 / 3
    return out


def header_points(text, x0, y0, w, h):
    """{(y, x)} of the header's letters: upright, stacked (tools/upright.py), centred in the column with room for
    the shadow right and below."""
    lay = upright.stack(text, h - 1, w - 3)
    top, left = y0 + (h - lay.h - 1) // 2, x0 + (w - lay.w - 1) // 2
    return {(top + y, left + x) for y, x in lay.points}


def redraw(tiles, rom, map_path=MAP_TSV, header_fill="edges", header_h=None, header_pal=HEADER_PAL[BLOCK]):
    """English grid drawn into a copy of the decompressed tile block."""
    m = load_map(map_path)
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
        clear(x0, y0, LABEL_CLEAR_W, h)
        lay = upright.stack(text, h - 2, w - 2)
        top, left = y0 + (h - lay.h) // 2, x0 + (w - lay.w) // 2
        pts = {(top + y, left + x) for y, x in lay.points}
        for y, x in pts:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if (y + dy, x + dx) not in pts:
                        put(x + dx, y + dy, EDGE)
        for y, x in pts:
            put(x, y, INK)
    for text, (x0, y0, w, h) in HEADERS:
        h = header_h or h
        ink = HEADER_INK[header_fill] | {0}

        def lum(x, y, v):
            return lightness(rom, header_pal, m[(x // 8, y // 8)] >> 12, v)
        # the background gradient, rebuilt in lightness (one index can be two shades in group 7) and dithered back
        # into each tile's own band colours: the old per-row index copy drew dotted rows and out-of-order bands
        samples = {}
        for y in range(y0, y0 + h):
            s = sorted(lum(x, y, get(x, y)) for x in range(x0, x0 + w) if get(x, y) not in ink)
            if s:
                samples[y] = s[len(s) // 2]
        ramp = header_ramp(samples, y0, h)
        # band colours per palette: one index per lightness, the one the original background uses most (group 7's
        # palette 4 has a grey antialias as light as its band a: picked on a tie, it drew a dark line)
        used = {}
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if get(x, y) not in ink:
                    key = m[(x // 8, y // 8)] >> 12, get(x, y)
                    used[key] = used.get(key, 0) + 1
        band_sets = {}
        for p in {m[(x // 8, y // 8)] >> 12 for y in range(y0, y0 + h) for x in range(x0, x0 + w)}:
            bands = []
            for i in sorted((i for i in range(16) if i not in ink and used.get((p, i))), key=lambda i: -used[(p, i)]):
                lv = lightness(rom, header_pal, p, i)
                if all(abs(lv - b) > 0.2 for b, _ in bands):   # a near-equal shade is the rarer twin: dropped
                    bands.append((lv, i))
            band_sets[p] = sorted(bands)
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                bands = band_sets[m[(x // 8, y // 8)] >> 12]
                target = ramp[y]
                lo = max((b for b in bands if b[0] <= target), default=bands[0])
                hi = min((b for b in bands if b[0] >= target), default=bands[-1])
                t = 0 if hi[0] == lo[0] else (target - lo[0]) / (hi[0] - lo[0])
                put(x, y, hi[1] if t > BAYER[y % 2][x % 2] else lo[1])
        pts = header_points(text, x0, y0, w, h)
        for y, x in upright.shadow(pts):
            put(x, y, 8)
        for y, x in pts:
            put(x, y, 1)
    for t in range(len(data) // 32):
        if data[t * 32:t * 32 + 32] != tiles[t * 32:t * 32 + 32] and len(spots.get(t, ())) != 1:
            raise ValueError(f"edited tile {t} shows at {sorted(spots.get(t, ()))}")
    return bytes(data)


def lz_edits(rom):
    return {blk: redraw(lz77.decompress(rom, blk)[0], rom, path, HEADER_FILL[blk], HEADER_H.get(blk), HEADER_PAL[blk])
            for blk, path in PICTURES.items()}


def capture(vram_path, out=MAP_TSV):
    v = Path(vram_path).read_bytes()
    out = Path(out)
    lines = ["# BG2 tilemap entries (VRAM 0x4000, 32x32) over the name-entry grid, captured from a newgame_name",
             "# dump by tools/name_grid.py capture (the game builds this map at run time). tx\tty\tentry"]
    for ty in range(0, 152 // 8):
        for tx in range(56 // 8, 240 // 8):
            e = struct.unpack_from("<H", v, 0x4000 + 2 * (ty * 32 + tx))[0]
            lines.append(f"{tx}\t{ty}\t{e:04x}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out, len(lines) - 2, "entries")


def preview(out, vram_path, pal_path, block=f"{BLOCK:x}"):
    """Grid area from a dump's VRAM/palette, original | English, 3x."""
    from PIL import Image
    import textbank
    rom = textbank.original_rom()
    v = Path(vram_path).read_bytes()
    pal = Path(pal_path).read_bytes()
    blk = int(block, 16)
    m = load_map(PICTURES[blk])
    tiles = lz77.decompress(rom, blk)[0]
    new = redraw(tiles, rom, PICTURES[blk], HEADER_FILL[blk], HEADER_H.get(blk), HEADER_PAL[blk])
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
        capture(*a.args)
    else:
        preview(*a.args)


if __name__ == "__main__":
    main()

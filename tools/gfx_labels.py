"""OBJ label strips (menu headers etc.): 16 px wide vertical labels stored as 2-tile-wide 4bpp runs in a sprite bank
(tools/sprites.py). Viewed with 2 tiles per row, a bank is one tall 16 px strip; each label is a run of non-blank
rows. English is drawn upright, letters stacked top to bottom (D17/D18, tools/upright.py: manga's 3x7 caps, 3x5
caps when long, more columns left to right); the other renderers below (grid, cells, frames, plates, orbs) too.

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
import manga  # noqa: E402
import sprites  # noqa: E402
import textbank  # noqa: E402
import upright  # noqa: E402

W = 16
# How each bank's labels are drawn: "box" = bank 22's peach gradient box (draw()); "plain" = black-on-white
# labels whose ink trio varies per slot (draw_plain(); `pal` = the palette row used to rank the trio dark..light,
# `skip` = antialias indices shared by every trio).
# "outline" = the menu choice boxes (banks 23-31, 37-39): white letters with a dark antialiased edge on the peach
# slot (index 13); a slot listed in `black` has black letters instead (bank 27's 通り名一覧), drawn as bank 22's.
STYLE = {22: {"kind": "box"}, 36: {"kind": "plain", "pal": 4, "skip": (10, 11)},
         35: {"kind": "plain", "pal": 0, "skip": (), "centre": True},
         # The menu bars show with OBJ palettes 5-7, where 15 is black / dark red on a light 13: white letters with a
         # dark edge came out as black silhouettes (visual QA on 4977f45e: unreadable at zoom 4), so every slot is
         # drawn black with a shade ("black": True = all slots).
         **{n: {"kind": "outline", "black": True} for n in (23, 24, 25, 27, 28, 29, 31, 37, 38, 39)},
         # (centred: the original はい/いいえ/一五分 fill the 44-row bar, rows 2-37)
         30: {"kind": "outline", "black": True, "centre": True},
         61: {"kind": "big"}}  # "big" = the combo counter's outlined gradient glyphs (draw_big())


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


INK_W = W - 2  # px of ink (+ shadow) across a 16 px strip: x 1..14


def placed(lay, top, x_lo, x_hi, extra=1):
    """{(row, x)} of an upright layout from row `top`, centred across x_lo..x_hi (with `extra` px of shadow or
    edge to the right counted in the width)."""
    x0 = x_lo + (x_hi - x_lo + 1 - (lay.w + extra)) // 2
    return {(top + y, x0 + x) for y, x in lay.points}


def paint(out, ink_pts, n, ink, shade=None, edge=None, only=None):
    """Ink `ink` with an upright drop shadow `shade` or an 8-neighbour `edge`, clipped to n rows x W; `only`: the
    colours a shadow may cover."""
    ring = upright.edge(ink_pts) if edge is not None else upright.shadow(ink_pts) if shade is not None else set()
    for y, x in ring:
        if 0 <= y < n and 0 <= x < W and (only is None or out[y][x] in only):
            out[y][x] = edge if edge is not None else shade
    for y, x in ink_pts:
        out[y][x] = ink


def draw(text, n, orig):
    """English label over a whole slot of n rows x 16 px (one OBJ frame, white below its box): a new gradient box
    from the original's first row, PAD rows longer than the text at each end, white after it; `text` upright and
    stacked (tools/upright.py), black with a mid-tone shadow."""
    c0 = next(i for i, row in enumerate(orig) if not blank(row))
    lay = upright.stack(text, n - c0 - 2 * PAD - 1, INK_W - 1)
    box = lay.h + 1 + 2 * PAD
    out = [[15] * W for _ in range(n)]
    for i in range(box):
        out[c0 + i] = [GRADIENT[i * len(GRADIENT) // box]] * W
    paint(out, placed(lay, c0 + PAD, 0, W - 1), n, INK, SHADE)
    return out


def glyph_cols(g):
    """(first, last) inked column of a font_en glyph, or None for a space."""
    cols = [i for line in g for i, ch in enumerate(line) if ch == "#"]
    return (min(cols), max(cols)) if cols else None


def text_width(text):
    """Rows a label takes with proportional spacing (inked columns + 1 gap; a space is 2 rows + gap)."""
    w = 0
    for c in font_en.fold(text):
        span = glyph_cols(font_en.FONT.get(c, font_en.FONT[" "]))
        w += (span[1] - span[0] + 1 if span else 2) + 1
    return w - 1


def palette(rom, b, row):
    pal = rom[b["pal"] + 32 * row:b["pal"] + 32 * row + 32]
    return [((c & 31), (c >> 5 & 31), (c >> 10 & 31)) for c in (pal[2 * i] | pal[2 * i + 1] << 8 for i in range(16))]


def ink_trio(orig, style, pal):
    """The slot's own letter colours: its 3 commonest indices (not 0, 15 or the shared antialias greys), darkest
    first by `pal`. The colour grades of bank 36 differ only in this trio."""
    hist = colours(orig)
    used = sorted((v for v in hist if v not in (0, 15) and v not in style["skip"]), key=lambda v: -hist[v])[:3]
    return sorted(used, key=lambda v: sum(pal[v]))


PLAIN_TOP = 1  # first letter row in a plain slot (the originals start at 2; 1 lets "Ashigaru Armor" fit)


def draw_plain(text, n, orig, ink, shade, centre=False):
    """English over a white label slot: every non-transparent pixel becomes white 15, then `text` upright and
    stacked from row PLAIN_TOP (or centred), with a `shade` shadow. A slot with no white (bare glyphs on
    transparent, e.g. bank 35's digits) is cleared to 0 and gets ink only (shade None)."""
    lay = upright.stack(text, n - PLAIN_TOP - 1, INK_W - 1)
    top = (n - lay.h - 1) // 2 if centre or lay.h + 1 > n - 2 * PLAIN_TOP else PLAIN_TOP
    white = any(15 in row for row in orig)
    out = [[0 if v == 0 or not white else 15 for v in row] for row in orig]
    paint(out, placed(lay, max(0, top), 0, W - 1), n, ink, shade, only=(15,))
    return out


OUT_BG, OUT_FILL, OUT_EDGE = 13, 15, 2  # peach slot, white letter, dark brown edge
OUT_TOP = 3  # first letter row in an outline slot (the originals' ink starts at +2; the edge takes +2)


def letter_points(text, top, x_top):
    """{(row, x)} of `text` rotated clockwise, proportionally spaced from row `top`, letter row 0 at x_top."""
    pts, y = set(), top
    for ch in font_en.fold(text):
        g = font_en.FONT.get(ch, font_en.FONT[" "])
        span = glyph_cols(g)
        if not span:
            y += 3
            continue
        for r, line in enumerate(g):
            for c, px in enumerate(line):
                if px == "#":
                    pts.add((y + c - span[0], x_top - r))
        y += span[1] - span[0] + 2
    return pts


def draw_outline(text, n, orig, black=False, centre=False):
    """English over a menu choice slot (rows of interior peach): cleared to OUT_BG, then white letters with an
    8-neighbour dark edge (or black letters with a shade, `black`), top-aligned from OUT_TOP, or centred in the
    slot (`centre`: bank 30, whose originals spread across the whole bar). Letters upright and stacked."""
    lay = upright.stack(text, n - 2 - 2, 12 - 1)   # from row 2 at the earliest, edge/shade below; ink x 2..13
    top = OUT_TOP if OUT_TOP + lay.h + 2 <= n else 2   # a tight slot: the edge may touch row 1
    if centre:
        top = max(top, (n - lay.h) // 2)
    out = [[v if v == 0 else OUT_BG for v in row] for row in orig]
    if black:
        paint(out, placed(lay, top, 2, 13), n, INK, SHADE)
    else:
        paint(out, placed(lay, top, 2, 13, extra=0), n, OUT_FILL, edge=OUT_EDGE)
    return out


BIG_FILL = {1: 4, 2: 4, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 2, 10: 2, 11: 3, 12: 3, 13: 4, 14: 4}


def draw_big(text, n, orig, fill=BIG_FILL, edge=15):
    """Big outlined glyphs (bank 61's combo counter): upright, 2x when it fits (a digit cell), else 1x stacked;
    the fill is the original's x gradient `fill` (white centre, blue rim), with an 8-neighbour `edge` outline;
    centred in the slot, everything else transparent."""
    lay = fit_scaled(text, n - 2, W - 2, ((2, 2), (1, 1)), gap=2)
    top = (n - lay.h) // 2
    pts = placed(lay, top, 0, W - 1, extra=0)
    out = [[0] * W for _ in range(n)]
    for yy, xx in upright.edge(pts):
        if 0 <= yy < n and 0 <= xx < W:
            out[yy][xx] = edge
    for yy, xx in pts:
        out[yy][xx] = fill.get(xx, edge)
    return out


def fit_scaled(text, room, width, scales, **kw):
    """The first (largest) scale (sx, sy) in `scales` at which `text` stacks upright in room x width: whole words
    at any scale before a word broken across columns."""
    for allow in (False, True):
        for sx, sy in scales:
            try:
                return upright.stack(text, room, width, sx=sx, sy=sy, allow_split=allow, **kw)
            except ValueError:
                continue
    raise ValueError(f"{text!r} does not fit {room} rows x {width} px at any of {scales}")


def english_rows(rom, bank):
    b, rows = strip(rom, bank)
    strip_rows = rows
    if bank in PIECED:
        rows = lay_pieces(rom, b, rows)
    new = [list(r) for r in rows]
    style = STYLE.get(bank, {"kind": "box"})
    pal = palette(rom, b, style.get("pal", 0))
    for start, n, jp, en in load_tsv(bank):
        if not en:
            continue
        orig = rows[start:start + n]
        if en == "(clear)":  # erase the slot, draw nothing (a trailing space would not survive the editor)
            en = " "
        if style["kind"] == "plain":
            trio = ink_trio(orig, style, pal)
            shade = trio[1] if len(trio) > 1 and any(15 in r for r in orig) else None
            new[start:start + n] = draw_plain(en, n, orig, trio[0], shade, style.get("centre", False))
        elif style["kind"] == "outline":
            black = style.get("black", ())
            new[start:start + n] = draw_outline(en, n, orig, black is True or start in black,
                                                style.get("centre", False))
        elif style["kind"] == "big":
            new[start:start + n] = draw_big(en, n, orig)
        else:
            new[start:start + n] = draw(en, n, orig)
    if bank in PIECED:
        rows, new = strip_rows, lay_pieces(rom, b, new, back=True)
    return b, rows, new


# Box banks whose cells show their 16 px pieces out of tile order: bank 22's 参加受付中・/・・/・・・ frames (16-18)
# put the slot's first tiles at the bottom, so a label drawn top to bottom showed "Taking Ent  ries." in game.
# english_rows() draws on the cells as seen (top to bottom) and lays the pieces back into their tiles.
PIECED = {22}


def lay_pieces(rom, b, rows, back=False):
    """Every cell's rows in screen order (back=False: tile order -> as seen), or back into its pieces' tiles
    (back=True). Strip row of tile t = t // 2 * 8 (2 tiles per 8-row band)."""
    out = [list(r) for r in rows]
    for ps in sprites.frames(rom, b):
        if any(p["w"] != 16 or p["x"] != 0 for p in ps):
            raise ValueError(f"bank {b['n']}: a cell's pieces are not one 16 px column")
        r0 = min(p["tile"] for p in ps) // 2 * 8
        for p in ps:
            pr = p["tile"] // 2 * 8
            if back:
                out[pr:pr + p["h"]] = rows[r0 + p["y"]:r0 + p["y"] + p["h"]]
            else:
                out[r0 + p["y"]:r0 + p["y"] + p["h"]] = rows[pr:pr + p["h"]]
    return out


# Banks drawn as whole OBJ pieces with 8 px label columns, not 16 px strips: (first tile, width, height) in tiles
# per piece (1D mapping, row-major). gfx/bankNN.tsv rows are then `piece col row rows jp en` (col in 8 px tile
# columns from x0, row/rows in pixel rows); the cell is cleared of `ink` to `bg` and the English drawn there in
# caps (7 rows tall, as the 7 px kanji), rotated clockwise, proportionally spaced from `row`. Bank 32's columns
# are not tile-aligned: the kanji sit at x = 5 + 8 * col .. +6. "(clear)" as en erases the cell.
GRID = {32: {"pieces": [(0, 8, 8), (64, 4, 8)], "ink": 1, "bg": 13, "x0": 5}}


def load_grid_tsv(bank):
    out = []
    for line in (ROOT / "gfx" / f"bank{bank:02d}.tsv").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            p, col, row, n, jp, en = (line.split("\t") + [""])[:6]
            out.append((int(p), int(col), int(row), int(n), jp, en))
    return out


def grid_edits(rom, bank):
    """English for a GRID bank: {tiles offset: new tile bytes}."""
    b = sprites.banks(rom)[bank]
    g = GRID[bank]
    data = bytearray(rom[b["tiles"]:b["end"]])

    def at(piece, y, x):
        t0, w, _ = g["pieces"][piece]
        t = t0 + (y // 8) * w + x // 8
        return t * 32 + (y % 8) * 4 + (x % 8) // 2, x & 1

    def get(piece, y, x):
        i, hi = at(piece, y, x)
        return data[i] >> 4 if hi else data[i] & 15

    def put(piece, y, x, v):
        i, hi = at(piece, y, x)
        data[i] = (data[i] & 0x0F) | (v << 4) if hi else (data[i] & 0xF0) | v

    for piece, col, row, n, jp, en in load_grid_tsv(bank):
        if not en:
            continue
        if en == "(clear)":  # erase the cell, draw nothing
            en = ""
        x0 = g["x0"] + col * 8  # the column's 7 letter pixels are x0..x0+6
        for y in range(row, row + n):
            for x in range(x0, x0 + 8):
                if get(piece, y, x) == g["ink"]:
                    put(piece, y, x, g["bg"])
        lay = upright.stack(en, n, 7, max_cols=1)
        for y, x in placed(lay, row, x0, x0 + 6, extra=0):
            put(piece, y, x, g["ink"])
    return {b["tiles"]: bytes(data)} if bytes(data) != rom[b["tiles"]:b["end"]] else {}


# The 8x8 small font (4bpp, ink 1 on 0, 32 bytes a glyph, ~0x61C58-0x7D2F8, no absolute pointer to it): its
# kanji numerals 〇 一 .. 九 at 0x7D098 + 32 * n draw the equip screen's stat values. Redrawn as rotated Arabic
# digits (font_en's, rows 0-6 at x 7..1, columns from y 2), so the values read like the rotated labels.
SMALL_DIGITS = 0x7D098

# Raw OBJ pictures outside the sprite banks, drawn upright (horizontal) on screen. 0x42B796: the stage's
# 昇段!! popup over the hero on a level-up (32x16 OBJ = 4x2 tiles, 1D mapping, OBJ palette 6; found by OAM dump
# + vramfind on the combo scene, docs/re/sprites.md §Raw popups). Redrawn as `en` in font_en caps, 1 px strokes
# doubled in height, proportional, centred, outline index 9 and the original's per-row fill gradient.
POPUPS = {0x42B796: {"w": 32, "h": 16, "jp": "昇段!!", "en": "LV UP!", "outline": 9,
                     "grad": [5, 5, 15, 15, 15, 15, 15, 15, 14, 14, 11, 11, 5, 5], "top": 1}}
# The same small font draws the player's name in the menu's stat panel: its kana from あ (0x7BC58) follow the name
# grid's table (name_grid.TABLE, 0x733660) without the table's two gaps (index 36, 38), 82 glyphs. Found by
# poking name indices into 0x02000618 and matching each drawn glyph to its ROM tile (all 82 matched). Each gets
# name_grid's letter for that slot, rotated as the digits, so a Latin name reads as it does everywhere else.
SMALL_KANA = 0x7BC58
SMALL_KANA_GAPS = (36, 38)


def small_kana_index(k):
    return k - sum(k > g for g in SMALL_KANA_GAPS)


SMALL_RANGES = ([(SMALL_DIGITS, SMALL_DIGITS + 10 * 32), (SMALL_KANA, SMALL_KANA + 82 * 32)]
                + [(o, o + p["w"] * p["h"] // 2) for o, p in POPUPS.items()])


def popup_mask(text):
    """{(row, x)} of `text` in font_en caps (rows 0-6), proportional: each glyph trimmed, 1 px gap, space 3 px."""
    pts, x = set(), 0
    for ch in text:
        if ch == " ":
            x += 3
            continue
        g = font_en.FONT[ch][:7]
        cols = [c for c in range(5) if any(line[c] == "#" for line in g)]
        for r, line in enumerate(g):
            for c in cols:
                if line[c] == "#":
                    pts.add((r, x + c - cols[0]))
        x += cols[-1] - cols[0] + 2
    return pts, x - 1


def popup_edits(rom):
    edits = {}
    for off, p in POPUPS.items():
        w, h = p["w"], p["h"]
        assert rom[off + 4:off + 8] != bytes(4), f"popup {off:x} moved"
        mask, width = popup_mask(p["en"])
        x0 = (w - width) // 2
        fill = {}
        for r, x in mask:
            for k in range(2):
                fill[(p["top"] + 2 * r + k, x0 + x)] = p["grad"][2 * r + k]
        pix = {}
        for (y, x) in fill:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (y + dy, x + dx)
                    if q not in fill and 0 <= q[0] < h and 0 <= q[1] < w:
                        pix[q] = p["outline"]
        pix.update(fill)
        assert all(0 <= y < h and 0 <= x < w for y, x in pix), f"popup {p['en']!r} does not fit {w}x{h}"
        out = bytearray(w * h // 2)
        for (y, x), v in pix.items():
            t = (y // 8) * (w // 8) + x // 8
            out[t * 32 + (y % 8) * 4 + (x % 8) // 2] |= v << (4 * (x & 1))
        edits[off] = bytes(out)
    return edits


def small_digit_edits(rom):
    """The stat digits upright (manga's 3x7 digits, rows 0-6, centred across the 8 px tile): the tiles stack down
    the stat column, so a value reads top to bottom like the labels."""
    assert rom[SMALL_DIGITS + 4:SMALL_DIGITS + 8] == bytes.fromhex("00101100"), "small-font 〇 moved"
    return {SMALL_DIGITS: b"".join(small_glyph(str(n)) for n in range(10))}


def small_glyph(ch):
    """32 bytes: manga.FONT's ch upright in an 8x8 tile, centred across, cap top at row 0; a letter with a
    descender (9 rows) loses its first blank row (the space above the x-height, or for 'j' the gap under the
    dot)."""
    g = list(manga.FONT[ch])
    if len(g) > 8:
        g.pop(next(r for r in range(len(g)) if "#" not in g[r]))
    out = bytearray(32)
    x0 = (8 - len(g[0])) // 2
    for r, line in enumerate(g):
        for c, px in enumerate(line):
            if px == "#":
                y, x = r, x0 + c
                assert 0 <= x < 8 and 0 <= y < 8, (ch, r, c)
                out[y * 4 + x // 2] |= 1 << (4 * (x & 1))
    return bytes(out)


def small_kana_edits(rom):
    import name_grid
    assert rom[SMALL_KANA + 4:SMALL_KANA + 8] == bytes.fromhex("00100000"), "small-font あ moved"
    out = bytearray(rom[SMALL_KANA:SMALL_KANA + 82 * 32])
    for k, ch in name_grid.LETTERS.items():
        i = small_kana_index(k)
        out[32 * i:32 * i + 32] = small_glyph(ch)
    return {SMALL_KANA: bytes(out)}


# Banks of square glyph cells (one 32x32 OBJ each, 4x4 tiles row-major, cells consecutive): gfx/bankNN.tsv rows
# `cell ncells jp en`. The cells are stacked into one 32 px column (cell k's rows, then cell k+1's), cleared, and
# `en` drawn rotated clockwise in font_en caps scaled `sx` in letter height (along x) and `sy` in width (along
# the column), bold by one px, centred, in index `ink`. Bank 33's big brush words sit in 2-3 cell columns on the
# link versus start screen (0x080147BC: いざ at x 0x90, 対戦!! at x 0x40, 32 px apart).
# Bank 34 = five 64x64 cells 男 女 (gender select) 空 (empty save slot) 終 (single-player game over; with 了
# below it, the link 終了 card).
# Bank 58 cells 0-2 = the stage HUD's current-weapon glyph 刀 槍 弓 (64x64 OBJ at screen x -1, y 112, bottom left:
# only rows 0-47 are on screen and the panel is x 1-24), white (1) outline glyphs. English sits in the panel:
# letters 14 px across (sx 2), condensed (sy 1 + bold 1), from row `top`, letter tops at x `x_top`, with a dark
# `edge` (4) ring so they read over the playfield too. Keys `top`/`x_top`/`bold`/`edge` are optional (default:
# centred, bold 1, no edge).
# Upright (D17): manga caps stacked down the cell column at the largest of `scales` (sx, sy) that fits `width`
# px across and the cells' rows less 4 (or `max_rows`), `gap` rows between letters; `cols` = the x range to
# centre in (default the cell). `bold` adds a px right of every stroke.
CELLS = {33: {"size": 32, "ink": 2, "width": 27, "bold": 1,
              "scales": [(4, 3), (4, 2.5), (4, 2), (4, 1.75), (3, 1.5), (3, 1.25), (2, 1)]},
         34: {"size": 64, "ink": 2, "width": 59, "bold": 1,
              "scales": [(6, 3), (5, 2.5), (4, 2), (4, 1.75), (3, 1.5), (2, 1.25), (2, 1)]},
         58: {"size": 64, "ink": 1, "width": 21, "cols": (2, 24), "top": 4, "edge": 4, "max_rows": 44,
              "scales": [(3, 2), (3, 1.75), (3, 1.5), (3, 1.25), (3, 1), (2, 1)]}}


def load_cells_tsv(bank):
    out = []
    for line in (ROOT / "gfx" / f"bank{bank:02d}.tsv").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            c, k, jp, en = (line.split("\t") + [""])[:4]
            out.append((int(c), int(k), jp, en))
    return out



def cells_edits(rom, bank):
    b = sprites.banks(rom)[bank]
    g = CELLS[bank]
    n = g["size"]
    tpr = n // 8  # tiles per row
    data = bytearray(rom[b["tiles"]:b["end"]])

    def at(cell, y, x):
        t = cell * tpr * tpr + (y // 8) * tpr + x // 8
        return t * 32 + (y % 8) * 4 + (x % 8) // 2, x & 1

    for cell, k, jp, en in load_cells_tsv(bank):
        if not en:
            continue
        room = g.get("max_rows", k * n - 4)
        lay = fit_scaled("" if en == "(clear)" else en, room, g["width"], g["scales"], gap=g.get("gap", 2),
                         space=g.get("gap", 2) * 3, fonts=("manga",))
        if g.get("bold"):  # one more px to the right of every stroke
            lay = lay._replace(points=lay.points | {(y, x + 1) for y, x in lay.points}, w=lay.w + 1)
        top = g.get("top", (k * n - lay.h) // 2)
        x_lo, x_hi = g.get("cols", (0, n - 1))
        ink = placed(lay, top, x_lo, x_hi, extra=0)

        def put(y, x, v):
            i, hi = at(cell + y // n, y % n, x)
            data[i] = (data[i] & 0x0F) | (v << 4) if hi else (data[i] & 0xF0) | v

        for y in range(k * n):  # clear
            for x in range(n):
                put(y, x, 0)
        if g.get("edge"):
            for y, x in ink:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if (y + dy, x + dx) not in ink and 0 <= y + dy < k * n and 0 <= x + dx < n:
                            put(y + dy, x + dx, g["edge"])
        for y, x in ink:
            put(y, x, g["ink"])
    return {b["tiles"]: bytes(data)} if bytes(data) != rom[b["tiles"]:b["end"]] else {}


# Banks drawn frame by frame (pieces from sprites.frames()): gfx/bankNN.tsv rows `frame jp en`. Each frame's
# pixels from row `top_keep` down become `bg`, then `en` is drawn rotated clockwise from row `row`, letter top
# at x `x_top`, in `ink` with a `shade` shadow. Bank 26 = the link lobby's player boxes (名前 / 参加者 headers;
# the game draws the player's name in the box's left half, x < 17, so the label keeps to x 18-27).
# Bank 26's frames show their own rows 32-63 again at 64-95 (the 32x32 piece reuses the tiles), so a label must
# end above row `end` or it repeats.
FRAMES = {26: {"bg": 13, "ink": 15, "shade": 9, "cols": (18, 27), "row": 3, "top_keep": 2, "end": 32}}


def frames_edits(rom, bank):
    b = sprites.banks(rom)[bank]
    g = FRAMES[bank]
    data = bytearray(rom[b["tiles"]:b["end"]])
    fr = sprites.frames(rom, b)
    for line in (ROOT / "gfx" / f"bank{bank:02d}.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        f, jp, en = (line.split("\t") + [""])[:3]
        if not en:
            continue
        pix = {}  # (y, x) -> (byte index, high nibble) over the frame's pieces
        for p in fr[int(f)]:
            for y in range(p["h"]):
                for x in range(p["w"]):
                    t = p["tile"] + (y // 8) * (p["w"] // 8) + x // 8
                    pix[(p["y"] + y, p["x"] + x)] = (t * 32 + (y % 8) * 4 + (x % 8) // 2, x & 1)
        height = g.get("end") or max(y for y, _ in pix) + 1
        lay = upright.stack(en, height - g["row"], g["cols"][1] - g["cols"][0])   # shadow may clip at the end

        def put(y, x, v):
            i, hi = pix[(y, x)]
            data[i] = (data[i] & 0x0F) | (v << 4) if hi else (data[i] & 0xF0) | v

        for (y, x) in pix:
            if y >= g["top_keep"]:
                put(y, x, g["bg"])
        pts = placed(lay, g["row"], *g["cols"])
        for yy, xx in upright.shadow(pts):
            if (yy, xx) in pix and yy < height:
                put(yy, xx, g["shade"])
        for y, x in pts:
            put(y, x, g["ink"])
    return {b["tiles"]: bytes(data)} if bytes(data) != rom[b["tiles"]:b["end"]] else {}


# Bank 20 = the province name plates beside the hero on the national map (frames 0-46, one 16x32 OBJ each, tile
# 8*frame; frames 47+ are flags, art). A plate is a black border (index 15) around a white field (14), the two
# kanji in rows 3-28, x 3-12. English (D18): upright.TINY 3x5 caps, one syllable per line (plate_layout), the
# lines centred in rows 4-27 (24 rows: a 1 px margin inside the border) and across x 1-14, ink 15. The tsv's '/'
# (v1 line breaks) is ignored. gfx/bank20.tsv rows `frame jp en`.
PLATES = {20: {"ink": 15, "bg": 14, "rows": (3, 28), "text_rows": (4, 27), "clear_x": (1, 14)}}


def plates_edits(rom, bank):
    b = sprites.banks(rom)[bank]
    g = PLATES[bank]
    data = bytearray(rom[b["tiles"]:b["end"]])
    fr = sprites.frames(rom, b)
    r0, r1 = g["rows"]
    for line in (ROOT / "gfx" / f"bank{bank:02d}.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        f, jp, en = (line.split("\t") + [""])[:3]
        if not en:
            continue
        (p,) = fr[int(f)]

        def put(y, x, v):
            t = p["tile"] + (y // 8) * (p["w"] // 8) + x // 8
            i = t * 32 + (y % 8) * 4 + (x % 8) // 2
            data[i] = (data[i] & 0x0F) | (v << 4) if x & 1 else (data[i] & 0xF0) | v

        for y in range(r0, r1 + 1):
            for x in range(g["clear_x"][0], g["clear_x"][1] + 1):
                put(y, x, g["bg"])
        t0, t1 = g["text_rows"]
        lay = plate_layout(en, t1 - t0 + 1, g["clear_x"][1] - g["clear_x"][0] + 1)
        top = t0 + (t1 - t0 + 1 - lay.h) // 2
        for y, x in placed(lay, top, *g["clear_x"], extra=0):
            put(y, x, g["ink"])
    return {b["tiles"]: bytes(data)} if bytes(data) != rom[b["tiles"]:b["end"]] else {}


def plate_layout(name, room, width):
    """A province name in TINY caps, upright, one syllable per line stacked down the plate (HYU / GA), centred.
    With more syllables than lines fit, neighbours share a line (shortest lines first) while it fits `width`."""
    rows = upright.syllables(name.replace("/", ""))
    max_rows = (room + 1) // 6
    while len(rows) > max_rows:
        k = min(range(len(rows) - 1), key=lambda i: upright.line_width(rows[i] + rows[i + 1]))
        if upright.line_width(rows[k] + rows[k + 1]) > width:
            raise ValueError(f"plate {name!r} does not fit {room} x {width}")
        rows[k:k + 2] = [rows[k] + rows[k + 1]]
    lay = upright.lines(rows)
    if lay.w > width or lay.h > room:
        raise ValueError(f"plate {name!r}: {lay.w}x{lay.h}, room {width}x{room}")
    return lay


# Bank 59 = the horizontal "スタートボタンを押してね" banner (16 cells of 112x16, 4 pieces each, identical pixels,
# each cell its own palette: the colour cycle). Drawn upright, not rotated (the original is horizontal): font_en
# letters centred in rows 3-11 (caps rows 3-9), x 2-109, ink `ink` with a `shade` shadow down-right, on `bg`.
HORIZ = {59: {"bg": 1, "ink": 11, "shade": 4, "rows": (2, 12), "cols": (2, 109), "top": 3}}


def horiz_edits(rom, bank):
    b = sprites.banks(rom)[bank]
    g = HORIZ[bank]
    data = bytearray(rom[b["tiles"]:b["end"]])
    fr = sprites.frames(rom, b)
    en = next(line.split("\t")[1] for line in (ROOT / "gfx" / f"bank{bank:02d}.tsv").read_text(
        encoding="utf-8").splitlines() if line and not line.startswith("#"))
    width = text_width(en)
    c0, c1 = g["cols"]
    if width > c1 - c0 + 1:
        raise ValueError(f"bank {bank} {en!r}: {width} px, banner has {c1 - c0 + 1}")
    left = c0 + (c1 - c0 + 1 - width) // 2
    # letter_points gives (run position, -glyph row) for a clockwise layout; upright = (top + glyph row, left + run)
    pts = {(g["top"] - xx, left + yy) for yy, xx in letter_points(en, 0, 0)}
    for cell in fr:
        pix = {}
        for p in cell:
            for y in range(p["h"]):
                for x in range(p["w"]):
                    t = p["tile"] + (y // 8) * (p["w"] // 8) + x // 8
                    pix[(p["y"] + y, p["x"] + x)] = (t * 32 + (y % 8) * 4 + (x % 8) // 2, x & 1)

        def put(y, x, v):
            i, hi = pix[(y, x)]
            data[i] = (data[i] & 0x0F) | (v << 4) if hi else (data[i] & 0xF0) | v

        for y in range(g["rows"][0], g["rows"][1] + 1):
            for x in range(c0, c1 + 1):
                put(y, x, g["bg"])
        for y, x in pts:
            if (y + 1, x + 1) not in pts:
                put(y + 1, x + 1, g["shade"])
        for y, x in pts:
            put(y, x, g["ink"])
    return {b["tiles"]: bytes(data)} if bytes(data) != rom[b["tiles"]:b["end"]] else {}


# Bank 47's magatama (gfx/bank47.tsv `frame jp en`): each 32x32 frame (tiles 16*frame.., 1D) is either an orb
# (white disc 2 with the kanji in blue 5) or the bare glyph (white 2 with blue 4/5 edges, on 0). The kanji
# becomes the virtue's initial (F W H M L P C, all different), font_en caps at 2x, rotated clockwise.
ORBS = {47: {"disc": 2, "ink": 5, "glyph": 2, "edge": 5}}


def orb_edits(rom, bank):
    b = sprites.banks(rom)[bank]
    g = ORBS[bank]
    data = bytearray(rom[b["tiles"]:b["end"]])

    def at(f, y, x):
        t = f * 16 + (y // 8) * 4 + x // 8
        return t * 32 + (y % 8) * 4 + (x % 8) // 2, x & 1

    def get(f, y, x):
        i, hi = at(f, y, x)
        return data[i] >> 4 if hi else data[i] & 15

    def put(f, y, x, v):
        i, hi = at(f, y, x)
        data[i] = (data[i] & 0x0F) | (v << 4) if hi else (data[i] & 0xF0) | v

    for line in (ROOT / "gfx" / f"bank{bank:02d}.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        f, jp, en = line.split("\t")[:3]
        f = int(f)
        lay = upright.stack(en, 20, 20, sx=3, sy=2)
        ink = placed(lay, (32 - lay.h) // 2, 0, 31, extra=0)
        orb = sum(get(f, y, x) == g["disc"] for y in range(32) for x in range(32)) > 200
        if orb:  # the kanji's pixels inside the disc go back to the disc colour
            for y in range(32):
                for x in range(32):
                    if get(f, y, x) not in (0, g["disc"]):
                        put(f, y, x, g["disc"])
            for y, x in ink:
                put(f, y, x, g["ink"])
        else:
            for y in range(32):
                for x in range(32):
                    put(f, y, x, 0)
            for y, x in ink:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if (y + dy, x + dx) not in ink:
                            put(f, y + dy, x + dx, g["edge"])
            for y, x in ink:
                put(f, y, x, g["glyph"])
    return {b["tiles"]: bytes(data)}


def labels_edits(rom, banks=None):
    edits = {} if banks is not None else {**small_digit_edits(rom), **small_kana_edits(rom), **popup_edits(rom)}
    for path in sorted((ROOT / "gfx").glob("bank*.tsv")):
        bank = int(path.stem[4:])
        if banks is not None and bank not in banks:
            continue
        if bank in GRID:
            edits.update(grid_edits(rom, bank))
            continue
        if bank in CELLS:
            edits.update(cells_edits(rom, bank))
            continue
        if bank in FRAMES:
            edits.update(frames_edits(rom, bank))
            continue
        if bank in PLATES:
            edits.update(plates_edits(rom, bank))
            continue
        if bank in HORIZ:
            edits.update(horiz_edits(rom, bank))
            continue
        if bank in ORBS:
            edits.update(orb_edits(rom, bank))
            continue
        b, rows, new = english_rows(rom, bank)
        if new != rows:
            edits[b["tiles"]] = pack(new, b)
    return edits


def grid_preview(rom, bank, out):
    """Every piece, original above English, 4x."""
    from PIL import Image
    b = sprites.banks(rom)[bank]
    rgb = [tuple(v * 255 // 31 for v in c) for c in palette(rom, b, 0)]
    rgb[0] = (255, 0, 255)
    new = grid_edits(rom, bank).get(b["tiles"], rom[b["tiles"]:b["end"]])
    pieces = GRID[bank]["pieces"]
    wsum = sum(w * 8 + 4 for _, w, _ in pieces)
    hmax = max(h * 8 for _, _, h in pieces)
    im = Image.new("RGB", (wsum, 2 * hmax + 4), (40, 40, 40))
    for k, data in enumerate((rom[b["tiles"]:b["end"]], new)):
        x0 = 0
        for t0, w, h in pieces:
            for y in range(h * 8):
                for x in range(w * 8):
                    t = t0 + (y // 8) * w + x // 8
                    v = data[t * 32 + (y % 8) * 4 + (x % 8) // 2]
                    im.putpixel((x0 + x, k * (hmax + 4) + y), rgb[v >> 4 if x & 1 else v & 15])
            x0 += w * 8 + 4
    im.resize((im.size[0] * 4, im.size[1] * 4), Image.NEAREST).save(out)
    print(out)


def preview(rom, bank, out):
    from PIL import Image
    if bank in GRID:
        return grid_preview(rom, bank, out)
    if bank in CELLS or bank in FRAMES or bank in PLATES or bank in HORIZ:  # every cell assembled, English build
        new = bytearray(rom)
        fn = (cells_edits if bank in CELLS else frames_edits if bank in FRAMES else
              plates_edits if bank in PLATES else horiz_edits)
        for off, data in fn(rom, bank).items():
            new[off:off + len(data)] = data
        return sprites.render_frames(bytes(new), bank, out)
    b, rows, new = english_rows(rom, bank)
    rgb = [tuple(v * 255 // 31 for v in c) for c in palette(rom, b, STYLE.get(bank, {}).get("pal", 0))]
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


def strips_sheet(rom, bank, out, col=256, pal_row=0):
    """A bank's 16 px strip wrapped into columns of `col` rows, 3x, with a ruler (tick every 16 rows, long every
    64, the column's first row printed in the segments listing): for reading off label start rows."""
    from PIL import Image
    b, rows = strip(rom, bank)
    rgb = [tuple(v * 255 // 31 for v in c) for c in palette(rom, b, pal_row)]
    rgb[0] = (255, 0, 255)
    ncol = (len(rows) + col - 1) // col
    im = Image.new("RGB", (ncol * (W + 10), col), (40, 40, 40))
    for i, row in enumerate(rows):
        k, y = divmod(i, col)
        x0 = k * (W + 10)
        for x, v in enumerate(row):
            im.putpixel((x0 + 6 + x, y), rgb[v])
    for k in range(ncol):
        for y in range(0, col, 16):
            for x in range(6 if y % 64 == 0 else 3):
                im.putpixel((k * (W + 10) + x, y), (255, 255, 0))
    im.resize((im.size[0] * 3, col * 3), Image.NEAREST).save(out)
    print(out, f"{ncol} columns of {col} rows")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["segments", "preview", "strips"])
    ap.add_argument("bank", type=int)
    ap.add_argument("out", nargs="?")
    ap.add_argument("--col", type=int, default=256)
    ap.add_argument("--pal", type=int, default=0)
    a = ap.parse_args()
    rom = textbank.original_rom()
    if a.cmd == "strips":
        return strips_sheet(rom, a.bank, a.out, a.col, a.pal)
    if a.cmd == "segments":
        b, rows = strip(rom, a.bank)
        for start, n in segments(rows):
            print(f"{start}\t{n}\t{colours(rows[start:start + n])}")
    else:
        preview(rom, a.bank, a.out)


if __name__ == "__main__":
    main()

"""English title logo (D15): SENGOKU / KAKUMEI GAIDEN in place of the 戦国革命外伝 lettering.

The title is one BG0 picture, in two versions (PICTURES): the usual one, and the one shown once a save has cleared
the game (0x080077DC: save byte +0x2A == 1 picks record 1 and sets [0x030016FC], which also switches the name entry
to its pink picture). Each has LZ tiles (512 tiles, VRAM 0), an LZ tilemap of 4x4-tile metatiles (map_slot()) and 15
raw sub-palettes; every logo tile shows once on screen, none flipped. For each picture:
  1. render the original to RGB;
  2. clear the old lettering exactly (old_lettering(): the kanji, their outline and halo; flames, mascot, ™ and
     the copyright line stay), refill with each row's background, rejoin the speed lines under it, and close the
     mascot's edge where the kanji had covered it;
  3. draw the English (fonts/Shojumaru-Regular.ttf, OFL) like the original: a fire gradient (yellow top, red
     bottom), a dark rim under each stroke, a 2 px black outline and a cream halo;
  4. re-fit the changed pixels to the tile's palette; a tile another palette shows better moves to that palette
     (its map entry changes palette bits only).

    python -X utf8 tools/title_logo.py preview OUT.png [title|cleared]   original | English, 3x (logo band)
    python -X utf8 tools/title_logo.py capture VRAM.bin                   data/title_map.tsv from a title dump (the
                                                                          test checks map_slot() against it)
"""
import argparse
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz77  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
# Picture records (7 u32: ?, ?, map, tiles, palette, 32, 20) at 0x7525B0 (title) and 0x7527B4 (cleared).
PICTURES = {"title": {"tiles": 0x5FD6AC, "map": 0x5FCEFC, "pal": 0x7523D0, "record": 0x7525B0},
            "cleared": {"tiles": 0x601044, "map": 0x6008D8, "pal": 0x7525D4, "record": 0x7527B4}}
MAP_TSV = ROOT / "data" / "title_map.tsv"
FONT = ROOT / "fonts" / "Shojumaru-Regular.ttf"
W, H = 240, 160
BAND = (46, 115)     # screen rows the old lettering (with its halo) can touch; the copyright text starts at 115
PEACH = (246, 197, 98)
BLACK = (0, 0, 0)
CREAM = (255, 238, 213)
RIM = (106, 82, 49)
FIRE = [(255, 222, 32), (255, 172, 16), (255, 131, 0), (255, 74, 0), (246, 32, 0), (238, 0, 0)]
DEEP_RED = {(238, 0, 0), (246, 0, 0), (246, 0, 8), (246, 16, 0), (246, 24, 0)}   # the kanji fill's reds
SEED_Y = 72          # flood seeds start here: every kanji reaches below it, the flames (same reds) end above it
OUTLINE, HALO = 4, 3                     # growth steps through the kanji's dark outline, then its light halo
ISLAND = 200                             # largest enclosed region old_lettering() takes as part of the kanji
STREAK_ROWS, STREAK_MIN = (94, 112), 40   # speed-line rows; a row needs this many streak pixels to count
CLEAR = {(x, y) for x in range(146, 226) for y in range(94, 112)}   # streak bits left between 外 and 伝
# Lines of English: text, font px, left x, top y (glyph box), letter spacing. Left of and under the mascot.
LINES = [("SENGOKU", 25, 5, 52, -1), ("KAKUMEI", 25, 5, 81, -1), ("GAIDEN", 20, 150, 71, -1)]


def mascot(x, y):
    """True in the box of the helmet mascot's lower half, whose edge the kanji covered."""
    return 143 <= x <= 219 and 50 <= y <= 80


def map_slot(tx, ty):
    """Byte offset of screen cell (tx, ty) in a decoded map block: a 16-byte header, then 4x4-tile metatiles of
    16 u16 entries, metatile 1 + 16 * (ty // 4) + tx // 4 at the screen position (checked against a title dump,
    data/title_map.tsv, by tests/test_title_logo.py)."""
    return 16 + 2 * (16 * (1 + 16 * (ty // 4) + tx // 4) + 4 * (ty % 4) + tx % 4)


def load_map(rom, pic):
    mp = lz77.decompress(rom, PICTURES[pic]["map"])[0]
    return {(tx, ty): struct.unpack_from("<H", mp, map_slot(tx, ty))[0] for ty in range(H // 8) for tx in range(W // 8)}


def load_tsv(path=MAP_TSV):
    m = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            tx, ty, e = line.split("\t")
            m[(int(tx), int(ty))] = int(e, 16)
    return m


def palettes(rom, pic):
    out = []
    for p in range(15):
        row = []
        for i in range(16):
            c = struct.unpack_from("<H", rom, PICTURES[pic]["pal"] + 32 * p + 2 * i)[0]
            row.append(((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31))
        row[0] = BLACK   # index 0 is transparent: the backdrop (palette 0 colour 0) is black
        out.append(row)
    return out


def render(tiles, m, pals):
    from PIL import Image
    im = Image.new("RGB", (W, H))
    px = im.load()
    for (tx, ty), e in m.items():
        t = e & 0x3FF
        for y in range(8):
            for x in range(8):
                b = tiles[t * 32 + y * 4 + x // 2]
                px[tx * 8 + x, ty * 8 + y] = pals[e >> 12][b >> 4 if x & 1 else b & 15]
    return im


def text_masks(size):
    """[{(x, y)} of one line's glyph pixels (no antialiasing)] per line of LINES."""
    from PIL import Image, ImageDraw, ImageFont
    masks = []
    for text, px, x0, y0, sp in LINES:
        font = ImageFont.truetype(str(FONT), px)
        im = Image.new("1", size, 0)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        x = x0
        for ch in text:
            left, top, right, _ = d.textbbox((0, 0), ch, font=font)
            d.text((x - left, y0 - top), ch, font=font, fill=1)
            x += right - left + sp - 1
        p = im.load()
        masks.append({(x, y) for y in range(size[1]) for x in range(size[0]) if p[x, y]})
    return masks


def grow(s, r):
    return {(x + dx, y + dy) for x, y in s for dx in range(-r, r + 1) for dy in range(-r, r + 1)
            if dx * dx + dy * dy <= r * r + r}


def old_lettering(px):
    """{(x, y)} of the kanji with their outline and halo: flood the letter interiors from their deep reds through
    fire colours, then grow OUTLINE steps through dark pixels (the black outline and its olive rim) and HALO steps
    through light ones (the cream halo). Peach never joins, so flames and mascot stop the growth."""
    def fire(c):
        return c[0] >= 200 and c[2] < 60 and not (c[1] > 190 and c[2] > 80)

    def inside(q):
        return 0 <= q[0] < W and BAND[0] <= q[1] < BAND[1]

    seen = {(x, y) for y in range(SEED_Y, BAND[1]) for x in range(W) if px[x, y] in DEEP_RED}
    stack = list(seen)
    while stack:
        x, y = stack.pop()
        for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if inside(q) and q not in seen and fire(px[q]):
                seen.add(q)
                stack.append(q)
    for steps, ok in ((OUTLINE, lambda c: max(c) < 160 or (c[2] < 60 and c[1] > 60 and c[0] < 200)),
                      (HALO, lambda c: min(c) > 150 and c != PEACH)):
        edge = set(seen)
        for _ in range(steps):
            edge = {q for x, y in edge for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                    if inside(q) and q not in seen and ok(px[q])}
            seen |= edge
    # islands the kanji enclose (highlights cut off by inner outlines, counters): small, off the band's border
    rest = {(x, y) for y in range(*BAND) for x in range(W)} - seen
    while rest:
        comp, stack = set(), [rest.pop()]
        while stack:
            x, y = stack.pop()
            comp.add((x, y))
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in rest:
                    rest.discard(q)
                    stack.append(q)
        if len(comp) <= ISLAND and all(0 < x < W - 1 and BAND[0] < y < BAND[1] - 1 for x, y in comp):
            seen |= comp
    return seen


def compose(orig):
    """Original RGB picture -> English logo picture (PIL image)."""
    im = orig.copy()
    px = im.load()
    gone = old_lettering(px)
    # each row's background: its commonest kept peach tone (the copyright strip has its own from row 112)
    bg = {}
    for y in range(*BAND):
        tones = Counter(c for c in (px[x, y] for x in range(W) if (x, y) not in gone)
                        if c[0] >= 240 and 185 <= c[1] <= 210 and 80 <= c[2] <= 110)
        bg[y] = tones.most_common(1)[0][0] if tones else PEACH
    for x, y in gone:
        px[x, y] = bg[y]
    near = grow(gone, 3)
    for _ in range(2):   # specks of outline or halo the growth missed: mostly-background neighbourhoods
        for x, y in sorted(near):
            if 0 < x < W - 1 and BAND[0] < y < BAND[1] - 1 and px[x, y] != bg[y]:
                if sum(px[x + dx, y + dy] == bg[y + dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)) >= 6:
                    px[x, y] = bg[y]
    for x, y in CLEAR:
        px[x, y] = bg[y]
    mend_streaks(px, orig.load(), bg)
    # the mascot's body ran on behind the kanji: close its cut edge with the black outline it has elsewhere
    edge = [(x, y) for x, y in grow(gone, 1) - gone if mascot(x, y) and px[x, y] != bg[y]
            and any(q in gone for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))]
    for q in edge:
        px[q] = BLACK
    for glyph in text_masks(im.size):   # each line over the ones before it, as the kanji overlap
        rim = grow(glyph, 1) - glyph
        line = grow(glyph, 2) | rim
        for x, y in grow(line, 1):
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = CREAM
        for x, y in line:
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = BLACK
        top = min(y for _, y in glyph)
        h = max(y for _, y in glyph) - top + 1
        for x, y in glyph:
            px[x, y] = FIRE[min(len(FIRE) - 1, (y - top) * len(FIRE) // h)]
        for x, y in rim:
            if (x, y - 1) in glyph and (x, y + 1) not in glyph:
                px[x, y] = RIM
    return im


def mend_streaks(px, orig, bg):
    """Redraw the speed lines under the text: in each streak row, the original's streak colour (its commonest
    yellow or cream) over every background pixel between the row's first and last streak pixel."""
    def streak(c):
        return c[0] > 240 and c[1] > 200 and (c[2] < 40 or c[2] > 160)

    for y in range(*STREAK_ROWS):
        xs = [x for x in range(W) if streak(orig[x, y])]
        if len(xs) < STREAK_MIN:
            continue
        colour = Counter(orig[x, y] for x in xs).most_common(1)[0][0]
        for x in range(xs[0], xs[-1] + 1):
            if px[x, y] == bg[y]:
                px[x, y] = colour


def dist(a, b):
    return sum((p - q) ** 2 for p, q in zip(a, b))


def nearest(pal, c):
    return min(range(16), key=lambda k: dist(pal[k], c))


def refit(tiles, m, pals, orig, new):
    """(tile bytes, map {cell: entry}, worst errors). Changed pixels take the nearest colour of the tile's palette,
    unless another palette shows all 64 of the tile's new pixels with less total error (then every pixel of the
    tile is re-fitted to it and its map entry changes palette)."""
    data = bytearray(tiles)
    o, n = orig.load(), new.load()
    m2, worst = dict(m), []
    for (tx, ty), e in m.items():
        cells = [(x, y, n[tx * 8 + x, ty * 8 + y]) for y in range(8) for x in range(8)]
        changed = [(x, y, c) for x, y, c in cells if c != o[tx * 8 + x, ty * 8 + y]]
        if not changed:
            continue
        p = e >> 12

        def miss(q, c):   # squared error, ten times over for a colour the palette can't come near (> 40)
            d = min(dist(k, c) for k in pals[q])
            return d * 10 if d > 1600 else d
        cost = {q: sum(miss(q, c) for _, _, c in (changed if q == p else cells)) for q in range(15)}
        best = min(cost, key=lambda q: (cost[q], q != p))
        if cost[best] < cost[p]:
            p = best
            changed = cells
            m2[(tx, ty)] = (e & 0x0FFF) | p << 12
        t = e & 0x3FF
        err = 0
        for x, y, c in changed:
            i = nearest(pals[p], c)
            err = max(err, dist(pals[p][i], c) ** 0.5)
            at = t * 32 + y * 4 + x // 2
            data[at] = (data[at] & 0x0F) | (i << 4) if x & 1 else (data[at] & 0xF0) | i
        worst.append((round(err), tx, ty, p))
    return bytes(data), m2, sorted(worst, reverse=True)


def build(rom, pic):
    """(tiles, new tiles, map, new map, palettes, worst refit errors) of one picture."""
    tiles = lz77.decompress(rom, PICTURES[pic]["tiles"])[0]
    m = load_map(rom, pic)
    pals = palettes(rom, pic)
    orig = render(tiles, m, pals)
    data, m2, worst = refit(tiles, m, pals, orig, compose(orig))
    return tiles, data, m, m2, pals, worst


def lz_edits(rom):
    out = {}
    for pic, p in PICTURES.items():
        _, data, _, m2, _, _ = build(rom, pic)
        mp = bytearray(lz77.decompress(rom, p["map"])[0])
        for cell, e in m2.items():
            struct.pack_into("<H", mp, map_slot(*cell), e)
        out[p["tiles"]] = data
        out[p["map"]] = bytes(mp)
    return out


def capture(vram_path, out=MAP_TSV):
    v = Path(vram_path).read_bytes()
    lines = ["# BG0 tilemap entries (VRAM 0x4000, 32x32) of the title picture, captured from a title dump by",
             "# tools/title_logo.py capture; tests/test_title_logo.py checks map_slot() against it. tx\tty\tentry"]
    for ty in range(H // 8):
        for tx in range(W // 8):
            e = struct.unpack_from("<H", v, 0x4000 + 2 * (ty * 32 + tx))[0]
            lines.append(f"{tx}\t{ty}\t{e:04x}")
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(out, len(lines) - 2, "entries")


def preview(out, pic="title"):
    from PIL import Image
    import textbank
    tiles, data, m, m2, pals, worst = build(textbank.original_rom(), pic)
    a, b = render(tiles, m, pals), render(data, m2, pals)
    y0, y1 = 0, 124
    im = Image.new("RGB", (W, 2 * (y1 - y0) + 4))
    im.paste(a.crop((0, y0, W, y1)), (0, 0))
    im.paste(b.crop((0, y0, W, y1)), (0, y1 - y0 + 4))
    im.resize((W * 3, im.size[1] * 3), Image.NEAREST).save(out)
    b.save(Path(out).with_name(Path(out).stem + "_full.png"))
    print(out, "worst refit error per tile (rgb distance, tx, ty, palette):", worst[:5])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["capture", "preview"])
    ap.add_argument("args", nargs="*")
    a = ap.parse_args()
    (capture if a.cmd == "capture" else preview)(*a.args)


if __name__ == "__main__":
    main()

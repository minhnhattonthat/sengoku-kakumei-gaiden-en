"""Link-error card (mode 22, scene `link_failed`): 通信に失敗しました。電源を切って、初めからやり直して下さい。
redrawn in English (docs/re/prose.md §Link-error card).

The card is BG2 in 8bpp (char base 0, map at VRAM 0x8000), from three LZ77 blocks in the idx/defs/tiles layout
of the ending cards, with 1x1 metatiles:
  idx   0x589198  2400 bytes = 30 x 20 u32: low 16 bits = metatile id, bit 25 = horizontal flip (border only)
  defs  0x589588  546 bytes  = header (1, 1, 265, 0) + 265 u16 tile entries
  tiles 0x5897EC  32 KB      = 512 8bpp tiles
English: the white (223) / black-edge (1) brush text is lifted off the emblem art (each light pixel and the
pixels within LIFT of it become the plain red 110; the emblem lines under the text are lost, the English covers
most of that), then the English goes on in the same white with a 1 px black edge,
font_en letters at 2x, rotated clockwise like all English text (D8).

    python -X utf8 tools/link_card.py preview OUT.png    original | English
Build: lz_edits(rom) -> {lz offset: decompressed bytes}.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import lz77  # noqa: E402

IDX, DEFS, TILES = 0x589198, 0x589588, 0x5897EC
W, H = 30, 20
WHITE, EDGE, BACK = 223, 1, 110          # BACK = the card's plain red
BRIGHT = {223, 222}                       # the brush text's whites (the emblem's light pixels are others)
TEXT_BOX = (40, 200, 8, 152)              # x0, x1, y0, y1 that holds the Japanese text
LIFT = 3                                  # px around a light pixel that may belong to the text (its black edge)
PAL = 0x74F1F0                            # the card's 256 colours (raw, right after its picture record)
DARK = 8                                  # near-black (the text's edge); with every colour lighter than the red
                                          # background (the text and its antialiasing), lifted near the text
LINES = ["Link failed.", "Turn off the", "power and", "start again", "from the", "beginning."]
SCALE, LEAD = 2, 4
FLIP = 1 << 25


def decoded(rom, off):
    return lz77.decompress(rom, off)[0]


def render(idx, defs, tiles):
    """160 rows of 240 colour indices."""
    ids = struct.unpack(f"<{W * H}I", idx)
    ents = struct.unpack_from(f"<{(len(defs) - 16) // 2}H", defs, 16)
    rows = []
    for y in range(H * 8):
        row = []
        for x in range(W * 8):
            word = ids[(y // 8) * W + x // 8]
            e = ents[word & 0xFFFF]
            xx, yy = x % 8, y % 8
            if word & FLIP or e & 0x400:
                xx = 7 - xx
            if e & 0x800:
                yy = 7 - yy
            row.append(tiles[(e & 0x3FF) * 64 + yy * 8 + xx])
        rows.append(row)
    return rows


def lift_text(px, pal):
    """Remove the Japanese: every pixel within LIFT of a light pixel (inside TEXT_BOX) gets the colour of the
    nearest pixel outside that set, searched in growing squares."""
    x0, x1, y0, y1 = TEXT_BOX
    text = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            if px[y][x] in BRIGHT:
                text |= {(x + dx, y + dy) for dx in range(-LIFT, LIFT + 1) for dy in range(-LIFT, LIFT + 1)}
    lum = luminance(pal)
    out = [r[:] for r in px]
    for x, y in text:
        c = px[y][x]
        if lum[c] > lum[BACK] or lum[c] <= DARK:
            out[y][x] = BACK
    return out


def luminance(pal):
    out = []
    for i in range(256):
        c = struct.unpack_from("<H", pal, 2 * i)[0]
        out.append(2 * (c & 31) + 4 * (c >> 5 & 31) + (c >> 10 & 31))
    return out


def draw_text(px):
    """English lines, rotated clockwise, centred in TEXT_BOX: white with a 1 px black edge."""
    x0, x1, y0, y1 = TEXT_BOX
    s = SCALE
    lh = font_en.H * s
    across = len(LINES) * lh + (len(LINES) - 1) * LEAD
    right = (x0 + x1 + across) // 2 - 1          # screen x of the first line's top row
    ink = set()
    for n, line in enumerate(LINES):
        length = (len(line) * (font_en.W + 1) - 1) * s
        u0 = (y0 + y1 - length) // 2              # each line centred along the column
        if length > 148:
            raise ValueError(f"line too long: {line!r}")
        for k, ch in enumerate(line):
            art = font_en.FONT[ch]
            for r in range(font_en.H):
                for c in range(font_en.W):
                    if art[r][c] == "#":
                        for a in range(s):
                            for b in range(s):
                                u = u0 + (k * (font_en.W + 1) + c) * s + a
                                v = n * (lh + LEAD) + r * s + b
                                ink.add((right - v, u))
    out = [r[:] for r in px]
    for x, y in ink:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                out[y + dy][x + dx] = EDGE
    for x, y in ink:
        out[y][x] = WHITE
    return out


def blocks(rom):
    """(idx, defs, tiles) for the English card, sizes as the originals."""
    idx, defs, tiles = (decoded(rom, o) for o in (IDX, DEFS, TILES))
    px = draw_text(lift_text(render(idx, defs, tiles), rom[PAL:PAL + 512]))
    new_tiles, index, ids = [], {}, []
    for ty in range(H):
        for tx in range(W):
            t = bytes(px[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8))
            mirror = bytes(t[y * 8 + 7 - x] for y in range(8) for x in range(8))
            if t not in index and mirror in index:
                ids.append(index[mirror] | FLIP)
                continue
            ids.append(index.setdefault(t, len(index)))
            if len(new_tiles) < len(index):
                new_tiles.append(t)
    if len(new_tiles) > len(tiles) // 64:
        raise ValueError(f"{len(new_tiles)} tiles: no room")
    # metatile k = tile k; the defs block grows past the original 265 entries when needed (the ending cards'
    # defs are 8208 bytes, so the game's buffer holds far more; checked in game on link_failed)
    n = max(len(new_tiles), (len(defs) - 16) // 2)
    new_defs = bytearray(defs[:16]) + struct.pack(f"<{n}H", *range(n))
    struct.pack_into("<I", new_defs, 8, n)
    return (struct.pack(f"<{W * H}I", *ids), bytes(new_defs), b"".join(new_tiles).ljust(len(tiles), b"\0"))


def lz_edits(rom):
    return dict(zip((IDX, DEFS, TILES), blocks(rom)))


def preview(out):
    from PIL import Image
    import textbank
    rom = textbank.original_rom()
    pal = Path(sys.argv[3]).read_bytes() if len(sys.argv) > 3 else None
    old = render(*(decoded(rom, o) for o in (IDX, DEFS, TILES)))
    new = render(*blocks(rom))
    im = Image.new("RGB", (2 * 240 + 4, 160))
    for k, rows in enumerate((old, new)):
        for y, row in enumerate(rows):
            for x, v in enumerate(row):
                if pal:
                    c = struct.unpack_from("<H", pal, 2 * v)[0]
                    rgb = ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8)
                else:
                    rgb = (v, v, v)
                im.putpixel((k * 244 + x, y), rgb)
    im.resize((im.size[0] * 2, 320), Image.NEAREST).save(out)
    print(out)


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

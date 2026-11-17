"""8bpp BG cards of the link mode, redrawn in English (docs/re/prose.md §Link-error card, §Replay map):
  "failed"  mode 22 `link_failed`: 通信に失敗しました。電源を切って、初めからやり直して下さい。
  "replay"  after the link 終了 card (`link_replay`): the 戦国リプレイ map with 一P..四P and 万石 labels.

Each card is BG2 in 8bpp (char base 0, map at VRAM 0x8000), from a picture record of u32 pointers: idx, a 600-byte
zero block, defs, tiles, palette (256 colours, raw). Same layout as the ending cards, with 1x1 metatiles:
  idx   2400 bytes = 30 x 20 u32: low 16 bits = metatile id, bit 25 = horizontal flip
  defs  header (1, 1, N, 0) + N u16 tile entries
  tiles 32 KB = 512 8bpp tiles
A card's Japanese is lifted in boxes (`lift`): within LIFT px of a pixel of the text's own colour, every pixel on
the text's side of the background (lighter for light text, darker for dark text, plus near-black edges) becomes
the background colour. Then the English goes on (`texts`), upright (D18): horizontal font_en lines, scaled, or
letters stacked down a narrow panel (tools/upright.py), with an optional 1 px edge. All three blocks are rewritten; the build moves the ones that outgrow their slot
(build.RELOCATABLE_LZ).

    python -X utf8 tools/link_card.py preview NAME OUT.png    original | English
Build: lz_edits(rom) -> {lz offset: decompressed bytes}.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import lz77  # noqa: E402
import upright  # noqa: E402

W, H = 30, 20
FLIP = 1 << 25
LIFT = 3
DARK = 8          # luminance at or below this counts as near-black

# lift: (x0, x1, y0, y1, text colours, background index, "light" or "dark" text)
# texts (D18, all upright): (kind, text, box (x0, x1, y0, y1), scale, ink, edge or None); kind "lines" = the
# text's '/'-separated lines horizontal, each centred across the box, the block centred down it (font_en,
# scaled); "stack" = upright.stack letters in the box (manga caps, columns of words).
CARDS = {
    "failed": {
        "idx": 0x589198, "defs": 0x589588, "tiles": 0x5897EC, "pal": 0x74F1F0,
        "lift": [(40, 212, 12, 148, {223, 222}, 110, "light")],
        "texts": [("lines", "Link failed./Turn off the/power and/start again/from the/beginning.",
                   (40, 212, 12, 148), 2, 223, 1)],
    },
    "replay": {
        "idx": 0x5B3604, "defs": 0x5B3A10, "tiles": 0x5B3C88, "pal": 0x74FAEC,
        "lift": [(216, 232, 0, 104, None, None, "rows"),     # 戦国リプレイ header panel (vertical gradient)
                 (8, 72, 8, 32, {1, 2}, 127, "dark"),        # 四P 三P 二P 一P
                 (8, 72, 66, 88, {1, 2}, 127, "dark")],      # 万石 x 4
        "texts": [("stack", "Sengoku Replay", (217, 231, 4, 100), 1, 1, None)] +
                 [("lines", f"{k}P", (60 - 16 * (k - 1), 75 - 16 * (k - 1), 10, 30), 1, 2, None)
                  for k in range(1, 5)] +
                 [("lines", "0K", (60 - 16 * k, 75 - 16 * k, 68, 86), 1, 2, None) for k in range(4)],
    },
}


def decoded(rom, off):
    return lz77.decompress(rom, off)[0]


def originals(rom, card):
    c = CARDS[card]
    return tuple(decoded(rom, c[k]) for k in ("idx", "defs", "tiles"))


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


def luminance(pal):
    out = []
    for i in range(256):
        c = struct.unpack_from("<H", pal, 2 * i)[0]
        out.append(2 * (c & 31) + 4 * (c >> 5 & 31) + (c >> 10 & 31))
    return out


def lift_text(px, pal, boxes):
    lum = luminance(pal)
    grey = []
    for i in range(256):
        c = struct.unpack_from("<H", pal, 2 * i)[0]
        rgb = (c & 31, c >> 5 & 31, c >> 10 & 31)
        grey.append(max(rgb) - min(rgb) <= 2)
    out = [r[:] for r in px]
    for x0, x1, y0, y1, inks, back, kind in boxes:
        if kind == "rows":  # a panel that only changes down the screen: each row = its commonest light colour
            for y in range(y0, y1):
                light = [c for c in px[y][x0:x1] if lum[c] >= 0.6 * max(lum)]
                fill = max(set(light), key=light.count) if light else out[y - 1][x0]
                out[y][x0:x1] = [fill] * (x1 - x0)
            continue
        near = set()
        for y in range(y0, y1):
            for x in range(x0, x1):
                if px[y][x] in inks:
                    near |= {(x + dx, y + dy) for dx in range(-LIFT, LIFT + 1) for dy in range(-LIFT, LIFT + 1)
                             if x0 <= x + dx < x1 and y0 <= y + dy < y1}
        for x, y in near:
            c = px[y][x]
            # dark text is black/grey on a coloured panel: only grey pixels (r = g = b within 2) are its own
            text_side = lum[c] > lum[back] if kind == "light" else lum[c] < lum[back] and grey[c]
            if text_side or lum[c] <= DARK:
                out[y][x] = back
    return out


def draw_texts(px, texts):
    out = [r[:] for r in px]
    for kind, text, (bx0, bx1, by0, by1), s, ink, edge in texts:
        pts = set()
        if kind == "stack":
            lay = upright.stack(text, by1 - by0, bx1 - bx0)
            x0, y0 = bx0 + (bx1 - bx0 - lay.w) // 2, by0 + (by1 - by0 - lay.h) // 2
            pts = {(x0 + x, y0 + y) for y, x in lay.points}
        else:
            lines = font_en.fold(text).split("/")
            pitch = (7 + 4) * s   # cap height + leading (no line here has a descender below the caps' gap)
            y = by0 + (by1 - by0 - (len(lines) * pitch - 4 * s)) // 2
            for line in lines:
                width = (len(line) * (font_en.W + 1) - 1) * s
                if width > bx1 - bx0:
                    raise ValueError(f"link card line {line!r}: {width} px, box {bx1 - bx0}")
                x = bx0 + (bx1 - bx0 - width) // 2
                for k, ch in enumerate(line):
                    art = font_en.FONT[ch]
                    for r in range(font_en.H):
                        for c in range(font_en.W):
                            if art[r][c] == "#":
                                for a in range(s):
                                    for b in range(s):
                                        pts.add((x + (k * (font_en.W + 1) + c) * s + a, y + r * s + b))
                y += pitch
            if y - pitch + 9 * s > by1 + 2 * s:
                raise ValueError(f"link card text {text!r} runs past its box")
        if edge is not None:
            for x, y in pts:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        out[y + dy][x + dx] = edge
        for x, y in pts:
            out[y][x] = ink
    return out


def blocks(rom, card):
    """(idx, defs, tiles) for the English card."""
    c = CARDS[card]
    idx, defs, tiles = originals(rom, card)
    px = draw_texts(lift_text(render(idx, defs, tiles), rom[c["pal"]:c["pal"] + 512], c["lift"]), c["texts"])
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
        raise ValueError(f"{card}: {len(new_tiles)} tiles, no room")
    # metatile k = tile k; the defs block grows past the original count when needed (the ending cards' defs are
    # 8208 bytes, so the game's buffer holds far more; checked in game on link_failed)
    n = max(len(new_tiles), (len(defs) - 16) // 2)
    new_defs = bytearray(defs[:16]) + struct.pack(f"<{n}H", *range(n))
    struct.pack_into("<I", new_defs, 8, n)
    return struct.pack(f"<{W * H}I", *ids), bytes(new_defs), b"".join(new_tiles).ljust(len(tiles), b"\0")


def lz_edits(rom):
    out = {}
    for card, c in CARDS.items():
        out.update(zip((c["idx"], c["defs"], c["tiles"]), blocks(rom, card)))
    return out


def preview(card, out):
    from PIL import Image
    import textbank
    rom = textbank.original_rom()
    pal = rom[CARDS[card]["pal"]:CARDS[card]["pal"] + 512]
    im = Image.new("RGB", (2 * 240 + 4, 160))
    for k, rows in enumerate((render(*originals(rom, card)), render(*blocks(rom, card)))):
        for y, row in enumerate(rows):
            for x, v in enumerate(row):
                c = struct.unpack_from("<H", pal, 2 * v)[0]
                im.putpixel((k * 244 + x, y), ((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8))
    im.resize((im.size[0] * 2, 320), Image.NEAREST).save(out)
    print(out)


def main():
    if len(sys.argv) == 4 and sys.argv[1] == "preview":
        preview(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

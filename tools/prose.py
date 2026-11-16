"""Ending cards (docs/re/prose.md): the six epilogue prose screens and the seven staff-credit screens, in English.

Each card is a BG2 picture made of three LZ77 blocks laid out in the ROM right before its tiles:
  idx   160 bytes   = 40 u32 metatile ids, 8 x 5 (32x32 px each; the 8th column is half off screen)
  defs  8208 bytes  = 16-byte header (4, 4, 256, 0) + 256 metatiles x 16 u16 tile entries (row-major 4x4)
  tiles 8/16 KB     = 4bpp tiles at VRAM 0x0000; the game adds palette 1 (grey ramp: 1 black .. 14 white,
                      15 = black on the credits and on the Masamune/Terumoto cards, a tint on the others)
A card's pointers sit in the table at 0x750000 (one u32 per block). All three blocks are rewritten in their own
slots: metatile ids are given by content (blank cells share one id), so the idx block stays small.
English is drawn rotated 90 degrees clockwise like the rest of the game (D8): lines read top to bottom, the
first line at the right edge of the screen.

    python -X utf8 tools/prose.py preview OUT.png     every card, original | English (screen orientation)
The 完 ("The End") card after the credits is OBJ tiles instead (END_TILES): end_edits() redraws it as THE / END.
Build: lz_edits(rom) -> {lz offset: decompressed bytes}, end_edits() -> {rom offset: raw tiles}, for build.py.
"""
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import lz77  # noqa: E402

SW, SH = 240, 160          # screen
MW = 8                     # metatiles per row (256 px)
INK, HEAD, SHADOW = 13, 14, 4
MARGIN = 6                 # px from the top of the screen to each line's first letter
INDENT = 12                # credits: names under their role
PITCH, HEAD_PITCH, GAP = 12, 16, 8
ADV, BOLD_ADV = font_en.W + 1, font_en.W + 2
ROOM = SH - 2 * MARGIN     # px along a line

# Prose: (idx, defs, tiles, title, body). Credits: (idx, defs, tiles, None, [(role, gloss, [names])]).
# Listed in the order the ending shows them (prose and credits alternate, then two credits at the end).
CARDS = [
    (0x5BE768, 0x5BE7E0, 0x5BEEC4, "Masamune Date",
     "At the Battle of Sekigahara he sided with the Tokugawa and the Eastern Army. In the summer "
     "campaign at Osaka he fought a fierce duel to the death with Yukimura Sanada... He lived on into "
     "the Edo period, feared as the realm's outspoken counsellor..."),
    (0x5D6CA4, 0x5D6D10, 0x5D72D0, None, [
        ("Cyber Foot Soldiers", "(Programming)",
         ["Hiroshige Orui", "Yasushi Ishikawa", "Takashi Umeda", "Mayuko Miura", "Yuta Sakamoto"])]),
    (0x5C7E14, 0x5C7E8C, 0x5C84F0, "Ieyasu Tokugawa",
     "After the death of Hideyoshi Toyotomi, he won the Battle of Sekigahara and founded the Tokugawa "
     "shogunate. Through the Siege of Osaka he wiped out the Toyotomi clan for good, and laid the "
     "foundation for three hundred years of Tokugawa rule..."),
    (0x5D85B4, 0x5D8618, 0x5D8BD0, None, [
        ("Brush Foot Soldiers", "(Design)",
         ["Hideo Osawa", "Yumi Miyashita", "Ai Shirane", "Katsuko Okabe", "Hiroshi Tanihiro"])]),
    (0x5C9C14, 0x5C9C8C, 0x5CA354, "Hideyoshi Toyotomi",
     "His invasion of Korea, a crushing burden on every daimyo in the land, ended with his death. "
     "Later, through the Battle of Sekigahara and the Siege of Osaka, the Toyotomi clan would meet "
     "its end..."),
    (0x5D9D84, 0x5D9DF0, 0x5DA368, None, [
        ("Court Musicians", "(Music)", ["Shinji Ushiroda", "Yasuhiro Ichihashi"]),
        ("Sound Masters", "(Sound Effects)", ["Yoichi Iwata"])]),
    (0x5C09B0, 0x5C0A34, 0x5C11A4, "Terumoto Mori",
     "At the Battle of Sekigahara he entered Osaka Castle as supreme commander of the Toyotomi side, "
     "but gave the castle up without ever fighting. His lands were cut, but the Mori clan survived, "
     "and would later become a great force behind the Meiji Restoration..."),
    (0x5DB2F4, 0x5DB36C, 0x5DB950, None, [
        ("Voice Samurai", "(Voices)", ["Chieko Atarashi", "Keiko Amano"]),
        ("Music Overseer", "(Sound Producer)", ["Hideyuki Suzuki"])]),
    (0x5C55E4, 0x5C5668, 0x5C5DB8, "Yukimura Sanada",
     "He fought for the Western Army at Sekigahara. With a handful of men he held back the Tokugawa "
     "army, but the West lost and he was exiled to Mount Kudo in Kii. At Osaka he joined the Toyotomi "
     "side once more. His fierce assault reached Ieyasu's own camp, but he fell in battle... "
     "Later he was hailed as \"the finest warrior in Japan\"..."),
    (0x5DCACC, 0x5DCB48, 0x5DD1B8, None, [
        ("Scribe Monks", "(Scenario)", ["Hiroshige Orui", "Hideo Osawa"]),
        ("Makeup Artist", "(Package Design)", ["Sakiko Tanaka"]),
        ("Picture-Show Man", "(Video Production)", ["Shinya Fukushima"])]),
    (0x5C2DBC, 0x5C2E40, 0x5C3598, "Yoshihiro Shimazu",
     "At the Battle of Sekigahara he joined the Western Army against his will. The Shimazu army took "
     "no part in the fighting, but when the West's defeat was sealed, it charged straight at Ieyasu's "
     "own camp, and in that rush it broke clean through to safety. The Shimazu clan would go on to "
     "last until the Meiji era..."),
    (0x5DEEAC, 0x5DEF24, 0x5DF5A0, None, [
        ("Ninja Squad", "(Publicity)", ["Yoko Sekiguchi", "Ryuji Mimura"]),
        ("Bug Catchers", "(Bug Check)", ["Yuichi Busujima", "Roppongi Monitoring Center"]),
        ("Reinforcements", "(Special Thanks)", ["The staff of Shutsugeki! Sengoku Kakumei"])]),
    (0x5E1150, 0x5E11C8, 0x5E17F8, None, [
        ("Sandal Bearer", "(Director)", ["Hideo Osawa"]),
        ("Elder Councillor", "(Producer)", ["Yoshinori Sasaki"]),
        ("His Lordship", "(Executive Producer)", ["Kazumi Kitakami"])]),
]


# The end card after the credits: the sword picture (BG2) with a big white 完 on top, which is four OBJs of
# sprite bank 44 (raw 4bpp at 0x71BAD8, 1D mapping, ink 15 on 0): 64x64 at (74,32), 32x64 at (138,32),
# 64x32 at (74,96), 32x32 at (138,96), so one 96x96 box. (LZ 0x5BB8AC also holds a 完 + (c) picture, but the
# ending never shows it; it stays as it is.)
END_TILES = 0x71BAD8
END_OBJS = [(0, 0, 8, 8), (64, 0, 4, 8), (0, 64, 8, 4), (64, 64, 4, 4)]   # box x, y, width and height in tiles
END_BOX = 96
END_SCALE, END_LEAD = 4, 8


def decoded(rom, off):
    return lz77.decompress(rom, off)[0]


def wrap(text, width):
    """Greedy word wrap to `width` px of ADV-wide letters."""
    room = width // ADV
    lines, cur = [], ""
    for w in font_en.fold(text).split():
        if len(w) > room:
            raise ValueError(f"word too long for a line: {w!r}")
        if cur and len(cur) + 1 + len(w) > room:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}" if cur else w
    return lines + [cur] if cur else lines


def layout(title, body):
    """[(v, u, bold, text)]: v = canvas row from the screen's right edge, u = px along the line."""
    out, v = [], 4

    def line(text, bold=False, u=0, pitch=PITCH):
        nonlocal v
        if len(text) * (BOLD_ADV if bold else ADV) > ROOM - u:
            raise ValueError(f"line too long: {text!r}")
        out.append((v, MARGIN + u, bold, text))
        v += pitch

    if title:
        line(title, bold=True, pitch=HEAD_PITCH)
        for t in wrap(body, ROOM):
            line(t)
    else:
        for k, (role, gloss, names) in enumerate(body):
            if k:
                v += GAP
            line(role, bold=True)
            line(gloss)
            for name in names:
                for t in wrap(name, ROOM - INDENT):
                    line(t, u=INDENT)
    if v - PITCH + font_en.H > SW:
        raise ValueError(f"{title or body[0][0]}: text runs off the screen")
    return out


def background(rom, card):
    """Colour index of the card's blank tile (the original's most used tile)."""
    idx_off, defs_off, tiles_off = card[:3]
    defs = struct.unpack_from("<4096H", decoded(rom, defs_off), 16)
    ids = struct.unpack("<40I", decoded(rom, idx_off))
    common = Counter(defs[i * 16 + k] & 0x3FF for i in ids for k in range(16)).most_common(1)[0][0]
    t = decoded(rom, tiles_off)[common * 32:common * 32 + 32]
    return Counter(v for b in t for v in (b & 15, b >> 4)).most_common(1)[0][0]


def draw_card(title, body, bg):
    """Screen pixels (160 rows of 256) with a one-pixel shadow under every letter."""
    px = [[bg] * (MW * 32) for _ in range(SH)]
    ink_px = []
    for v, u0, bold, text in layout(title, body):
        ink, adv = (HEAD, BOLD_ADV) if bold else (INK, ADV)
        for k, ch in enumerate(text):
            art = font_en.FONT[ch]
            for r in range(font_en.H):
                for c in range(font_en.W):
                    if art[r][c] == "#":
                        for dx in range(2 if bold else 1):  # bold = each pixel doubled along the line
                            ink_px.append((u0 + k * adv + c + dx, v + r, ink))
    for u, v, _ in ink_px:  # shadow first, ink over it
        x, y = SW - 1 - (v + 1), u + 1
        if 0 <= x < SW and 0 <= y < SH:
            px[y][x] = SHADOW
    for u, v, ink in ink_px:
        px[u][SW - 1 - v] = ink
    return px


def tiles_of(px):
    """Cut 256x160 screen pixels into 8x8 tiles; -> (tile bytes list, map[ty][tx] tile index), deduplicated."""
    tiles, index, tmap = [], {}, []
    for ty in range(SH // 8):
        row = []
        for tx in range(MW * 4):
            t = bytearray(32)
            for y in range(8):
                for x in range(0, 8, 2):
                    t[y * 4 + x // 2] = px[ty * 8 + y][tx * 8 + x] | px[ty * 8 + y][tx * 8 + x + 1] << 4
            t = bytes(t)
            if t not in index:
                index[t] = len(tiles)
                tiles.append(t)
            row.append(index[t])
        tmap.append(row)
    return tiles, tmap


def end_box():
    """96x96 index rows: THE / END in big rotated letters (ink 15 on transparent 0), as 完 was."""
    s, n = END_SCALE, END_BOX
    px = [[0] * n for _ in range(n)]
    for line, word in enumerate(("THE", "END")):
        v0 = (n - 2 * font_en.H * s - END_LEAD) // 2 + line * (font_en.H * s + END_LEAD)
        u0 = (n - (len(word) * ADV - 1) * s) // 2
        for k, ch in enumerate(word):
            art = font_en.FONT[ch]
            for r in range(font_en.H):
                for c in range(font_en.W):
                    if art[r][c] == "#":
                        for a in range(s):
                            for b in range(s):
                                px[u0 + (k * ADV + c) * s + a][n - 1 - (v0 + r * s + b)] = 15
    return px


def end_edits():
    """{0x71BAD8: tile bytes} for the four 完 OBJs (1D mapping: each OBJ's tiles row-major, one after another)."""
    px = end_box()
    out = bytearray()
    for bx, by, w, h in END_OBJS:
        for ty in range(h):
            for tx in range(w):
                for y in range(8):
                    for x in range(0, 8, 2):
                        row = px[by + ty * 8 + y]
                        out.append(row[bx + tx * 8 + x] | row[bx + tx * 8 + x + 1] << 4)
    return {END_TILES: bytes(out)}


def card_blocks(rom, card):
    """(new idx, defs, tiles bytes) for one card, each the size of the original block."""
    idx_off, defs_off, tiles_off, title, body = card
    tiles, tmap = tiles_of(draw_card(title, body, background(rom, card)))
    size = len(decoded(rom, tiles_off))
    if len(tiles) * 32 > size:
        raise ValueError(f"{title}: {len(tiles)} tiles, room for {size // 32}")
    defs = bytearray(decoded(rom, defs_off))
    defs[16:] = bytes(len(defs) - 16)
    known, ids = {}, []
    for p in range(40):
        my, mx = divmod(p, MW)
        ent = tuple(tmap[my * 4 + r][mx * 4 + c] for r in range(4) for c in range(4))
        mid = known.setdefault(ent, len(known) + 1)
        struct.pack_into("<16H", defs, 16 + mid * 32, *ent)
        ids.append(mid)
    return struct.pack("<40I", *ids), bytes(defs), b"".join(tiles).ljust(size, b"\0")


def lz_edits(rom):
    out = {}
    for card in CARDS:
        out[card[0]], out[card[1]], out[card[2]] = card_blocks(rom, card)
    return out


def render(rom, card, edits=None):
    """Colour-index picture (160 rows of 240) composed from the blocks as the game does."""
    idx_off, defs_off, tiles_off = card[:3]
    e = edits or {}
    idx = struct.unpack("<40I", e.get(idx_off) or decoded(rom, idx_off))
    defs = struct.unpack_from("<4096H", e.get(defs_off) or decoded(rom, defs_off), 16)
    tiles = e.get(tiles_off) or decoded(rom, tiles_off)
    rows = []
    for y in range(SH):
        row = []
        for x in range(SW):
            ent = defs[idx[(y // 32) * MW + x // 32] * 16 + ((y % 32) // 8) * 4 + (x % 32) // 8]
            t, xx, yy = ent & 0x3FF, x % 8, y % 8
            if ent & 0x400:
                xx = 7 - xx
            if ent & 0x800:
                yy = 7 - yy
            b = tiles[t * 32 + yy * 4 + xx // 2]
            row.append(b >> 4 if xx & 1 else b & 15)
        rows.append(row)
    return rows


def preview(out):
    from PIL import Image
    import textbank
    rom = textbank.original_rom()
    edits = lz_edits(rom)
    # palette 1 as the game sets it on these screens: 1..14 ramp, 15 black
    grey = [0, 0] + [round(255 * k / 13) for k in range(1, 14)] + [0]
    im = Image.new("L", (2 * SW + 4, len(CARDS) * (SH + 4)), 128)
    for j, card in enumerate(CARDS):
        for k, e in enumerate((None, edits)):
            for y, row in enumerate(render(rom, card, e)):
                for x, v in enumerate(row):
                    im.putpixel((k * (SW + 4) + x, j * (SH + 4) + y), grey[v])
    im.save(out)
    print(out)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

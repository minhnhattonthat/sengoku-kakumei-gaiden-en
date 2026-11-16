"""Sprite banks: the 62 records at 0x7585D0-0x759170 (48 bytes each), the source of every OBJ label graphic
(menu headers and buttons, item names, stat labels). Layout (docs/re/sprites.md):

    +0  u32 count    +4  u32 flags    +8  palette ptr   +12 tiles ptr   +16 tiles end (= first cell table)
    +20..+40  further table ptrs (cells / frames, not decoded)   +44 u32 sizes (not decoded)

Tiles are raw 4bpp GBA (32 bytes each, uncompressed); the palette is (tiles - palette) bytes of BGR555.

    python -X utf8 tools/sprites.py list
    python -X utf8 tools/sprites.py render [N ..] [--out work/gfx/banks] [--cols 32]   (PNG per bank, palette 0)
    python -X utf8 tools/sprites.py frames N .. [--out work/gfx/banks]   (each frame assembled from its pieces)
"""
import argparse
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402
import textbank  # noqa: E402

TABLE = (0x7585D0, 0x759170)
STRIDE = 0x30


def banks(rom):
    out = []
    for i, off in enumerate(range(TABLE[0], TABLE[1], STRIDE)):
        w = struct.unpack_from("<12I", rom, off)
        out.append({"n": i, "rec": off, "count": w[0], "flags": w[1], "pal": w[2] - 0x08000000,
                    "tiles": w[3] - 0x08000000, "end": w[4] - 0x08000000, "rest": [x - 0x08000000 for x in w[5:11]],
                    "sizes": w[11]})
    return out


OBJ_SIZE = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
            2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def frames(rom, b):
    """Decoded cells of a bank: [[{w, h, x, y, tile, pal}, ..], ..]. Pieces (12 bytes, from b['end']): u16 attr0
    (shape in bits 14-15), u16 attr1 (size in bits 14-15), u16 attr2-like (tile*2 in bits 0-9, relative to the
    cell's first tile; palette in 12-15), s16 y, s16 x. rest[0] = pieces per cell (bytes, 0-padded to
    rest[1]), rest[1] = each cell's first tile (u16); a cell's pieces are consecutive. rest[2] = animation frames
    (8 bytes: u16 cell, u16 duration?, u16 first piece, 0), `count` of them."""
    out, p = [], 0
    ncell = len(rom[b["rest"][0]:b["rest"][1]].rstrip(b"\0"))
    for f in range(ncell):
        n = rom[b["rest"][0] + f]
        base = struct.unpack_from("<H", rom, b["rest"][1] + 2 * f)[0]
        ps = []
        for k in range(n):
            a0, a1, a2, y, x = struct.unpack_from("<HHHhh", rom, b["end"] + 12 * (p + k))
            w, h = OBJ_SIZE[a0 >> 14][a1 >> 14]
            ps.append({"w": w, "h": h, "x": x, "y": y, "tile": base + (a2 & 0x3FF) // 2, "pal": a2 >> 12})
        out.append(ps)
        p += n
    return out


def render_frames(rom, n, out, scale=3):
    """Every frame of bank n laid out as on screen (pieces at their x/y), side by side, palette per piece."""
    from PIL import Image
    b = banks(rom)[n]
    npal = (b["tiles"] - b["pal"]) // 32
    pals = [[tuple(((c >> s) & 31) * 255 // 31 for s in (0, 5, 10))
             for c in struct.unpack_from("<16H", rom, b["pal"] + 32 * r)] for r in range(npal)]
    fr = frames(rom, b)
    boxes = []
    for ps in fr:
        x0, y0 = min(p["x"] for p in ps), min(p["y"] for p in ps)
        x1, y1 = max(p["x"] + p["w"] for p in ps), max(p["y"] + p["h"] for p in ps)
        boxes.append((x0, y0, x1, y1))
    wsum = sum(x1 - x0 + 4 for x0, _, x1, _ in boxes)
    hmax = max(y1 - y0 for _, y0, _, y1 in boxes)
    im = Image.new("RGB", (wsum, hmax), (255, 0, 255))
    cx = 0
    for ps, (x0, y0, x1, y1) in zip(fr, boxes):
        for p in ps:
            pal = pals[min(p["pal"], npal - 1)]
            for y in range(p["h"]):
                for x in range(p["w"]):
                    t = p["tile"] + (y // 8) * (p["w"] // 8) + x // 8
                    v = rom[b["tiles"] + 32 * t + (y % 8) * 4 + (x % 8) // 2]
                    v = v >> 4 if x & 1 else v & 15
                    if v:
                        im.putpixel((cx + p["x"] - x0 + x, p["y"] - y0 + y), pal[v])
        cx += x1 - x0 + 4
    im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST).save(out)
    print(out, f"{len(fr)} frames")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "render", "frames"])
    ap.add_argument("n", nargs="*", type=int)
    ap.add_argument("--out", default=str(ROOT / "work" / "gfx" / "banks"))
    ap.add_argument("--cols", type=int, default=32)
    a = ap.parse_args()
    rom = textbank.original_rom()
    bs = banks(rom)
    if a.cmd == "list":
        for b in bs:
            print(f"{b['n']:2d} rec {b['rec']:06x} count {b['count']:3d} flags {b['flags']:x} pal {b['pal']:06x} "
                  f"({(b['tiles'] - b['pal']) // 2} colours) tiles {b['tiles']:06x}-{b['end']:06x} "
                  f"({(b['end'] - b['tiles']) // 32} tiles) sizes {b['sizes']:08x}")
        return
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "frames":
        for n in a.n:
            render_frames(rom, n, out / f"frames{n:02d}.png")
        return
    for b in bs:
        if a.n and b["n"] not in a.n:
            continue
        pal = out / f"bank{b['n']:02d}.pal.bin"
        pal.write_bytes(rom[b["pal"]:b["tiles"]])
        subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "tiles.py"), "render",
                        str(ROOT / "rom" / "Sengoku Kakumei Gaiden (Japan).gba"), str(out / f"bank{b['n']:02d}.png"),
                        "--fmt", "gba4", "--at", f"{b['tiles']:X}", "--len", f"{b['end'] - b['tiles']:X}",
                        "--cols", str(a.cols), "--pal", str(pal), "--pal-index", "0"],
                       check=True, stdout=subprocess.DEVNULL)
        print(out / f"bank{b['n']:02d}.png")


if __name__ == "__main__":
    main()

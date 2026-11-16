"""Sprite banks: the 62 records at 0x7585D0-0x759170 (48 bytes each), the source of every OBJ label graphic
(menu headers and buttons, item names, stat labels). Layout (docs/re/sprites.md):

    +0  u32 count    +4  u32 flags    +8  palette ptr   +12 tiles ptr   +16 tiles end (= first cell table)
    +20..+40  further table ptrs (cells / frames, not decoded)   +44 u32 sizes (not decoded)

Tiles are raw 4bpp GBA (32 bytes each, uncompressed); the palette is (tiles - palette) bytes of BGR555.

    python -X utf8 tools/sprites.py list
    python -X utf8 tools/sprites.py render [N ..] [--out work/gfx/banks] [--cols 32]   (PNG per bank, palette 0)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["list", "render"])
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

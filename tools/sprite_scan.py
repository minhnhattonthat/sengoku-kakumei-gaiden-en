"""Find every 48-byte sprite record in the ROM (the sprite-bank layout of docs/re/sprites.md, not only the 62 banks
of the table at 0x7585D0): +0 count, +4 flags, +8 palette ptr, +12 tiles ptr (= palette + 32 * k), +16 tiles end.

    python -X utf8 tools/sprite_scan.py [--render DIR]   # list records outside the 62 banks; --render draws each

Read-only. Records found this way were how the stage's 昇段!! popup (0x74ECB8) turned up.
"""
import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprites  # noqa: E402
import textbank  # noqa: E402


def records(rom):
    out = []
    n = len(rom)
    for i in range(0, n - 48, 4):
        cnt, flags, pal, tiles, end = struct.unpack_from("<5I", rom, i)
        if not (0x08000000 <= pal < 0x08000000 + n and 0x08000000 <= tiles < end < 0x08000000 + n):
            continue
        k = tiles - pal
        if k <= 0 or k % 32 or k > 32 * 16 or not 0 < cnt < 4096 or flags > 0xFF:
            continue
        if end - tiles < 32 or end - tiles > 0x40000:
            continue
        out.append({"rec": i, "count": cnt, "flags": flags, "pal": pal & 0x1FFFFFF, "tiles": tiles & 0x1FFFFFF,
                    "end": end & 0x1FFFFFF, "colours": k // 2})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", help="draw each record's tiles (16 px strips) into this directory")
    a = ap.parse_args()
    rom = textbank.original_rom()
    known = {b["tiles"] for b in sprites.banks(rom)}
    recs = [r for r in records(rom) if r["tiles"] not in known]
    for r in recs:
        print(f"rec {r['rec']:06x} count {r['count']:4d} flags {r['flags']:x} pal {r['pal']:06x} "
              f"({r['colours']} colours) tiles {r['tiles']:06x}-{r['end']:06x} ({(r['end'] - r['tiles']) // 32} tiles)")
    print(f"{len(recs)} records outside the 62 banks")
    if a.render:
        from PIL import Image
        os.makedirs(a.render, exist_ok=True)
        for r in recs:
            t = rom[r["tiles"]:r["end"]]
            pal = [struct.unpack_from("<H", rom, r["pal"] + 2 * c)[0] for c in range(16)]
            rgb = [((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3) for c in pal]
            nt = len(t) // 32
            cols = 4
            im = Image.new("RGB", (cols * 8, ((nt + cols - 1) // cols) * 8), (255, 0, 255))
            px = im.load()
            for k in range(nt):
                for y in range(8):
                    for x in range(8):
                        b = t[k * 32 + y * 4 + x // 2]
                        v = (b >> 4) if x & 1 else b & 15
                        if v:
                            px[(k % cols) * 8 + x, (k // cols) * 8 + y] = rgb[v]
            im.save(os.path.join(a.render, f"rec{r['rec']:06x}.png"))


if __name__ == "__main__":
    main()

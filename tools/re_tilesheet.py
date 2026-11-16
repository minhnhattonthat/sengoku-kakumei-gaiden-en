"""re_tilesheet.py: render byte ranges as GBA 4bpp tiles (grey ramp) into labelled sheets for the graphics survey.

  python -X utf8 tools/re_tilesheet.py OUTPREFIX --cols 32 --rows 128 --zoom 2 SRC[:START-END] ...
SRC is a file (ROM or decompressed block); START/END are hex offsets. Identical and blank tiles are dropped
(dedupe across all sources) so each sheet holds only new tiles; every source gets a label strip with its name and
offset. Prints each sheet with the sources it holds, and every source skipped (with the reason).
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw


def tile_img(t):
    im = Image.new("L", (8, 8))
    px = []
    for b in t:
        px += [(b & 15) * 17, (b >> 4) * 17]
    im.putdata(px)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("src", nargs="+")
    ap.add_argument("--cols", type=int, default=32)
    ap.add_argument("--rows", type=int, default=128)
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--min-tiles", type=int, default=4)
    a = ap.parse_args()
    seen = set(); entries = []  # (label, [tiles])
    for spec in a.src:
        path, _, rng = spec.partition(":")
        data = Path(path).read_bytes()
        s, e = (int(x, 16) for x in rng.split("-")) if rng else (0, len(data))
        tiles = []
        for o in range(s, e - 31, 32):
            t = data[o:o + 32]
            if len(set(t)) <= 1 or t in seen:
                continue
            seen.add(t); tiles.append(t)
        label = f"{Path(path).stem}:{s:x}"
        if len(tiles) < a.min_tiles:
            print(f"skip {label}: {len(tiles)} new tiles")
            continue
        entries.append((label, tiles))
    # lay out: each entry starts on a new row after a label row
    pages = []; cur = []; used = 0
    for label, tiles in entries:
        rows = 1 + (len(tiles) + a.cols - 1) // a.cols
        while rows > 0:
            room = a.rows - used
            if room < 2:
                pages.append(cur); cur = []; used = 0; continue
            take = min(rows - 1, room - 1)
            cur.append((label, tiles[:take * a.cols])); tiles = tiles[take * a.cols:]
            used += 1 + take; rows -= 1 + take
            if not tiles:
                break
            rows = 1 + (len(tiles) + a.cols - 1) // a.cols
    if cur:
        pages.append(cur)
    for n, page in enumerate(pages):
        W = a.cols * 8
        im = Image.new("L", (W, a.rows * 8), 40)
        d = ImageDraw.Draw(im); y = 0
        for label, tiles in page:
            d.rectangle([0, y, W, y + 7], fill=255); d.text((1, y - 2), label, fill=0)
            y += 8
            for i, t in enumerate(tiles):
                im.paste(tile_img(t), ((i % a.cols) * 8, y + (i // a.cols) * 8))
            y += 8 * ((len(tiles) + a.cols - 1) // a.cols)
        im = im.resize((W * a.zoom, a.rows * 8 * a.zoom), Image.NEAREST)
        p = f"{a.out}_{n:03d}.png"; im.save(p)
        print(p, " ".join(l for l, _ in page))


if __name__ == "__main__":
    main()

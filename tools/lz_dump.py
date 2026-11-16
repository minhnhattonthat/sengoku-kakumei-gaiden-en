"""Decompress every LZ77 block in data/lz_blocks.tsv into a directory, one file per block named by ROM offset
(`<offset>.bin`), for `vramfind.py VRAM.bin DIR` (which block a VRAM tile came from).

    python -X utf8 tools/lz_dump.py [--out work/lz]
"""
import argparse
from pathlib import Path

import lz77
import textbank

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "lz"))
    a = ap.parse_args()
    rom = textbank.original_rom()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for line in (ROOT / "data" / "lz_blocks.tsv").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        off = int(line.split("\t")[0], 16)
        data = lz77.decompress(rom, off)
        if isinstance(data, tuple):
            data = data[0]
        (out / f"{off:06x}.bin").write_bytes(bytes(data))
        n += 1
    print(f"{n} blocks -> {out}")


if __name__ == "__main__":
    main()

"""re_lzsweep.py ROM OUTDIR: find every GBA BIOS LZ77 (type 0x10) block, decompress it, write OUTDIR/<off>.bin + index.tsv.

A candidate at a 4-aligned offset is kept when it decodes to exactly its header size with every back-reference
inside the output. Accepted blocks are skipped over (no overlapping finds). Prints every rejected-but-plausible
header count so nothing is dropped silently.
"""
import sys
from pathlib import Path


def lz77(rom, off, limit=0x80000):
    """Return (data, end_offset) or None."""
    if rom[off] != 0x10:
        return None
    size = rom[off + 1] | rom[off + 2] << 8 | rom[off + 3] << 16
    if not 32 <= size <= limit:
        return None
    out = bytearray(); i = off + 4; n = len(rom)
    while len(out) < size:
        if i >= n:
            return None
        flags = rom[i]; i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                if i + 1 >= n:
                    return None
                b0, b1 = rom[i], rom[i + 1]; i += 2
                ln = (b0 >> 4) + 3; disp = ((b0 & 15) << 8 | b1) + 1
                if disp > len(out):
                    return None
                for _ in range(ln):
                    out.append(out[-disp])
            else:
                if i >= n:
                    return None
                out.append(rom[i]); i += 1
    if len(out) != size:
        return None  # overran: last token wrote past size
    return bytes(out), i


def main():
    rom = Path(sys.argv[1]).read_bytes()
    outdir = Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    rows = []; off = 0; rejected = 0
    while off < len(rom) - 4:
        r = lz77(rom, off)
        if r and (r[1] - off) < len(r[0]) * 1.2 + 16:
            data, end = r
            (outdir / f"{off:06x}.bin").write_bytes(data)
            rows.append((off, end, len(data)))
            off = (end + 3) & ~3
            continue
        if rom[off] == 0x10 and r is None:
            rejected += 1
        off += 4
    with open(outdir / "index.tsv", "w", encoding="utf-8") as f:
        f.write("offset\tend\tsize\n")
        for o, e, s in rows:
            f.write(f"{o:06x}\t{e:06x}\t{s}\n")
    print(f"blocks {len(rows)}  bytes out {sum(r[2] for r in rows)}  rejected 0x10 headers {rejected}")


if __name__ == "__main__":
    main()

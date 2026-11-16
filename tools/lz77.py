"""lz77.py: GBA BIOS LZ77 (SWI 0x11/0x12, header type 0x10) decode and encode.

    from lz77 import decompress, compress
    data, end = decompress(rom, off)          # end = offset just past the block
    blob = compress(data)                     # greedy longest match; decodes back to `data`

The game's own compressor is weaker (it often stores literals where a match exists), so compress() does not
reproduce its bytes. The build never recompresses an unedited block: it keeps the original bytes, so the identity
build stays exact, and an edited block only has to decode back to its data (tests/test_identity.py checks that).
python -X utf8 tools/lz77.py ROM OFFSET  -> prints size, end, original and recompressed length.
"""
import sys


def decompress(buf, off=0):
    """Return (data, end_offset). Raises ValueError on a bad header or a reference before the start."""
    if buf[off] != 0x10:
        raise ValueError(f"{off:#x}: not an LZ77 block (type {buf[off]:#04x})")
    size = buf[off + 1] | buf[off + 2] << 8 | buf[off + 3] << 16
    out = bytearray()
    i = off + 4
    while len(out) < size:
        flags = buf[i]
        i += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b0, b1 = buf[i], buf[i + 1]
                i += 2
                n = (b0 >> 4) + 3
                disp = ((b0 & 15) << 8 | b1) + 1
                if disp > len(out):
                    raise ValueError(f"{off:#x}: back-reference before start at {i - 2:#x}")
                for _ in range(n):
                    out.append(out[-disp])
            else:
                out.append(buf[i])
                i += 1
    if len(out) != size:
        raise ValueError(f"{off:#x}: last token ran past the header size")
    return bytes(out), i


def compress(data, min_disp=2):
    """Greedy LZ77, longest match, nearest first. min_disp=2 (default) keeps the output safe for SWI 0x12 (VRAM),
    so one blob works for both BIOS calls."""
    n = len(data)
    out = bytearray([0x10, n & 0xFF, n >> 8 & 0xFF, n >> 16 & 0xFF])
    chains = {}  # 3-byte prefix -> positions, ascending
    indexed = 0
    pos = 0
    while pos < n:
        flag_at = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if pos >= n:
                break
            while indexed < pos and indexed + 3 <= n:
                chains.setdefault(data[indexed:indexed + 3], []).append(indexed)
                indexed += 1
            best_len, best_disp = 0, 0
            maxlen = min(18, n - pos)
            cands = chains.get(data[pos:pos + 3], ()) if maxlen >= 3 else ()
            for j in reversed(cands):
                disp = pos - j
                if disp > 0x1000:
                    break
                if disp < min_disp:
                    continue
                k = 3
                while k < maxlen and data[pos + k] == data[pos + k - disp]:
                    k += 1
                if k > best_len:
                    best_len, best_disp = k, disp
                    if k == maxlen:
                        break
            if best_len >= 3:
                flags |= 0x80 >> bit
                v = (best_len - 3) << 12 | (best_disp - 1)
                out += bytes([v >> 8, v & 0xFF])
                pos += best_len
            else:
                out.append(data[pos])
                pos += 1
        out[flag_at] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def main():
    rom = open(sys.argv[1], "rb").read()
    off = int(sys.argv[2], 16)
    data, end = decompress(rom, off)
    blob = compress(data)
    assert decompress(blob)[0] == data
    print(f"{off:#x}: {len(data)} bytes, ends {end:#x}, original {end - off} bytes, recompressed {len(blob)}")


if __name__ == "__main__":
    main()

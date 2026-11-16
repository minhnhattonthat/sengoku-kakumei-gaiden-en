"""engine.py: the English text engine patch (docs/re/english.md).

    python -X utf8 tools/engine.py --selftest

patch(rom_bytearray, encoder) -> writes [(off, old, new, who)]:
  - font table: the original 990 entries at 0x712128 copied to FONT_AT, then one entry per English letter pair
    (tools/font_en.py), and the table pointer literal at 0x04A464 (read by 0x0804A45C, glyph index -> entry)
    repointed there;
  - glyph lookup 0x080126C0 (code -> glyph index, a linear search over 990 entries) jumps to LOOKUP_AT: a pair code
    (b0 0x80-0x9F) maps straight to 990 + (b0-0x80)*128 + (b1-0x80); any other code runs the original linear search.
All of it lives in ENGINE, the top of the free space; textbank.FREE ends where it starts. Nothing may go in
textbank.PALETTE_READ (0x759178-0x7C0B40): the magatama page's palette copy reads it (docs/re/english.md).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402

ENGINE = (0x7E0000, 0x800000)
LOOKUP_AT = 0x7E0000          # thumb code, < 0x100 bytes
FONT_AT = 0x7E0100            # 32-byte entries (room for 990 + 3088 pairs)
ORIG_FONT = 0x712128
ORIG_COUNT = 0x3DE            # 990
ENTRY = 32
TABLE_LITERAL = 0x04A464      # ldr r1, =0x08712128 in 0x0804A45C
LOOKUP = 0x0126C0             # original lookup function
NOT_FOUND = 0x135
SITES = [(TABLE_LITERAL, 4), (LOOKUP, 8)]


def _asm(src, addr):
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, addr)
    return bytes(enc)


def lookup_code(font_addr):
    """Thumb replacement for 0x080126C0, assembled for LOOKUP_AT. Literals follow the code."""
    base = 0x08000000 | LOOKUP_AT
    body = f"""
        push {{r4, r5, r6, lr}}
        lsls r0, r0, #16
        lsrs r5, r0, #16
        lsls r1, r5, #24
        lsrs r1, r1, #24
        subs r1, #0x80
        cmp r1, #0x1f
        bhi linear
        lsrs r2, r5, #8
        subs r2, #0x80
        lsls r1, r1, #7
        adds r0, r1, r2
        ldr r1, lit_count
        adds r0, r0, r1
        b done
    linear:
        movs r4, #0
        ldr r6, lit_last
        ldr r3, lit_font
    loop:
        lsls r0, r4, #5
        ldrh r0, [r3, r0]
        cmp r0, r5
        beq found
        adds r4, #1
        cmp r4, r6
        bls loop
        ldr r0, lit_nf
        b done
    found:
        adds r0, r4, #0
    done:
        pop {{r4, r5, r6}}
        pop {{r1}}
        bx r1
        .align 2
    lit_count: .word {ORIG_COUNT}
    lit_last: .word {ORIG_COUNT - 1}
    lit_font: .word {0x08000000 | font_addr | 2}
    lit_nf: .word {NOT_FOUND}
    """
    code = _asm(body, base)
    assert len(code) <= FONT_AT - LOOKUP_AT
    return code


# lookup_code(FONT_AT), so the build needs no assembler; tests/test_engine.py re-assembles it when keystone is there.
# The code is position-independent; only the font literal (third pool word) depends on FONT_AT.
_LOOKUP_CODE = bytes.fromhex(
    "70b50004050c2906090e80391f2906d82a0a803ac9018818094940180ce00024084e094b6001185aa84204d00134b442f8d906"
    "4800e0201c70bc02bc084700bfde030000dd030000")
LOOKUP_BIN = _LOOKUP_CODE + struct.pack("<II", 0x08000000 | FONT_AT | 2, NOT_FOUND)


def hook_bytes():
    # 0x080126C0: ldr r3, [pc, #0] (pc = 0x080126C4); bx r3; .word LOOKUP_AT|1  -> 8 bytes, word aligned
    return struct.pack("<HHI", 0x4B00, 0x4718, 0x08000000 | LOOKUP_AT | 1)


def font_table(rom, encoder, overrides=None):
    """overrides: {(code b0, b1): 26 glyph bytes} replacing original entries' glyphs (name_grid: the name kana)."""
    out = bytearray(rom[ORIG_FONT:ORIG_FONT + ORIG_COUNT * ENTRY])
    for k in range(ORIG_COUNT):
        g = (overrides or {}).get((out[k * ENTRY + 2], out[k * ENTRY + 3]))
        if g is not None:
            out[k * ENTRY + 6:k * ENTRY + 6 + len(g)] = g
    for k, pair in enumerate(encoder.pairs):
        b0, b1 = font_en.code(k)
        # entry: u16 index, u8 code b0, u8 code b1, u16 0, 13 rows u16 big-endian (bit 15 = x 0)
        out += struct.pack("<HBBH", ORIG_COUNT + k + 1, b0, b1, 0) + font_en.glyph_bytes(pair)
    return bytes(out)


def patch(out, encoder, overrides=None):
    """Apply the engine to bytearray out; return the write list."""
    writes = []

    def put(off, data, who):
        writes.append((off, bytes(out[off:off + len(data)]), data, who))
        out[off:off + len(data)] = data

    table = font_table(out, encoder, overrides)
    if FONT_AT + len(table) > ENGINE[1]:
        raise ValueError(f"font table {len(table):#x} bytes overruns {ENGINE[1]:#x}")
    put(LOOKUP_AT, LOOKUP_BIN, "engine lookup")
    put(FONT_AT, table, f"engine font ({len(encoder.pairs)} pairs)")
    put(TABLE_LITERAL, struct.pack("<I", 0x08000000 | FONT_AT), "engine font pointer")
    put(LOOKUP, hook_bytes(), "engine lookup hook")
    return writes


def allowed(off, n):
    if ENGINE[0] <= off and off + n <= ENGINE[1]:
        return True
    return any(s <= off and off + n <= s + size for s, size in SITES)


def _selftest():
    assert struct.unpack("<H", _asm("ldr r3, [pc, #0]", 0x080126C0))[0] == 0x4B00
    assert struct.unpack("<H", _asm("bx r3", 0x080126C2))[0] == 0x4718
    code = lookup_code(FONT_AT)
    # literal pool: last four words
    lits = struct.unpack("<4I", code[-16:])
    assert lits == (ORIG_COUNT, ORIG_COUNT - 1, 0x08000000 | FONT_AT | 2, NOT_FOUND), [hex(x) for x in lits]
    print(f"selftest ok: lookup {len(code)} bytes")


if __name__ == "__main__":
    _selftest()

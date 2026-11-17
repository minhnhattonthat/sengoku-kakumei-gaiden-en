"""manga_engine.py: engine patch for the manga-bubble variant (D16, docs/re/manga.md, tools/manga.py).

    python -X utf8 tools/manga_engine.py --selftest      re-assemble with keystone and compare with the stored code

On top of tools/engine.py's layout (font table copy at FONT_AT, lookup at LOOKUP_AT):
  - lookup: English pair codes (b0 0x80-0x9F, v1 rotated text, kept for the one-column results labels) as before;
    slice codes (b0 0x01-0x24, b1 0x01-0xFF) -> MANGA_BASE + (b0-1)*255 + (b1-1); anything else: linear search.
  - font entry +4 (u16, 0 in the original table) = the glyph's advance in px for mode 0; 0 means 12.
  - 0x08011DB8 (position advance, called only by the reader 0x08011DDC): in mode 0 (the scroll, reader's
    [sp+0x4c] == 0) x += the advance of the glyph just drawn (code at [sb-2], or the name letter at [r5-2] after
    `%n`, whose sprite is also pulled left by manga.NAME_COL_X); y stays. Mode 1 keeps the original column flow.
  - 0x0801225C (`|n`): in mode 0 centre the line just finished (shift every sprite of the page whose y is the line's
    y so the line's centre lands on CX), then x = start x, y += LINE_PITCH.
  - 0x08012450 (end of the string): in mode 0 centre the last line, then move the whole block so its centre lands
    on CY.
Typewriter reveal (0x080124D8) is unchanged: sprites appear in slot order = reading order.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import engine  # noqa: E402
import manga  # noqa: E402

CODE_AT = 0x7FF800            # advance / newline / end handlers (ENGINE top 2 KB); font table must end below
PARAMS_AT = 0x7FFFF0          # u32 MANGA_BASE (written per build)
CX = 22                       # scroll inside x 2-41
CY = 80                       # scroll inside y 2-157
INK_H = 7                     # cap height (rows 0-6 of a glyph)
SLOTS = 0x030019A8
HOOK_ADV = 0x011DB8           # 12 bytes
HOOK_NL = 0x01225C            # 8 bytes
HOOK_END = 0x012450           # 8 bytes
SITES = [(HOOK_ADV, 12), (HOOK_NL, 8), (HOOK_END, 8), (PARAMS_AT, 4)]


def lookup_src():
    return f"""
        push {{r4, r5, r6, lr}}
        lsls r0, r0, #16
        lsrs r5, r0, #16
        lsls r1, r5, #24
        lsrs r1, r1, #24
        adds r2, r1, #0
        subs r1, #0x80
        cmp r1, #0x1f
        bhi notpair
        lsrs r2, r5, #8
        subs r2, #0x80
        lsls r1, r1, #7
        adds r0, r1, r2
        ldr r1, lit_count
        adds r0, r0, r1
        b done
    notpair:
        subs r2, #1
        cmp r2, #0x23
        bhi linear
        lsls r1, r2, #8
        subs r1, r1, r2
        lsrs r2, r5, #8
        subs r2, #1
        adds r0, r1, r2
        ldr r1, lit_params
        ldr r1, [r1]
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
    lit_count: .word {engine.ORIG_COUNT}
    lit_last: .word {engine.ORIG_COUNT - 1}
    lit_font: .word {0x08000000 | engine.FONT_AT | 2}
    lit_nf: .word {engine.NOT_FOUND}
    lit_params: .word {0x08000000 | PARAMS_AT}
    """


def handlers_src():
    lookup = 0x08000000 | engine.LOOKUP_AT
    return f"""
        b adv                           @ CODE_AT + 0
        b newline                       @ CODE_AT + 2
        b endstr                        @ CODE_AT + 4
        nop
    adv:                                @ hook did push {{r4, lr}}: reader [sp+X] is at [sp+X+8]
        ldr r4, [sp, #0x54]
        cmp r4, #0
        bne adv_orig
        push {{r0, r1, r2, r3, r5}}       @ reader [sp+X] now at [sp+X+28]
        mov r0, sb
        subs r0, #2
        ldrb r1, [r0]
        cmp r1, #0x25
        bne adv_code
        ldrb r1, [r0, #1]
        cmp r1, #0x6e
        bne adv_wide
        ldr r0, [sp, #0x74]             @ reader [sp+0x58]: the %n loop (0x08012130) counted this letter's slot
        subs r0, #1
        lsls r1, r0, #1
        adds r1, r1, r0
        lsls r1, r1, #3
        ldr r2, lit_slots
        ldr r2, [r2]
        adds r1, r1, r2
        ldrh r2, [r1, #2]
        subs r3, r2, #{manga.NAME_COL_X}
        lsls r3, r3, #23
        lsrs r3, r3, #23
        lsrs r2, r2, #9
        lsls r2, r2, #9
        orrs r2, r3
        strh r2, [r1, #2]
        ldr r0, [sp, #16]               @ saved r5: this letter's u16 (name-grid index + 1)
        ldrh r0, [r0]
        subs r0, #1
        lsls r0, r0, #2
        ldr r1, lit_grid
        adds r0, r0, r1                 @ its EUC code, as the loop reads it
    adv_code:
        ldrb r1, [r0]
        ldrb r2, [r0, #1]
        lsls r2, r2, #8
        orrs r1, r2
        adds r0, r1, #0
        bl {lookup:#x}
        lsls r0, r0, #5
        ldr r1, lit_font
        adds r0, r0, r1
        ldrh r4, [r0, #4]
        cmp r4, #0
        bne adv_set
    adv_wide:
        movs r4, #12
    adv_set:
        pop {{r0, r1, r2, r3, r5}}
        adds r1, r1, r4
        str r1, [r0]
        str r2, [r0, #4]
        pop {{r4}}
        pop {{r2}}
        bx r2
    adv_orig:                           @ 0x08011DBA.. as the game has it
        adds r4, r0, #0
        lsls r3, r3, #16
        lsrs r3, r3, #16
        adds r2, #12
        adds r0, r2, #0
        adds r0, #12
        cmp r0, #0x9f
        ble adv_o2
        subs r1, #12
        adds r2, r3, #0
    adv_o2:
        str r1, [r4]
        str r2, [r4, #4]
        adds r0, r4, #0
        pop {{r4}}
        pop {{r2}}
        bx r2

    newline:                            @ from 0x0801225C (reader body, reader sp)
        movs r2, #1
        add sb, r2
        ldr r3, [sp, #0x4c]
        cmp r3, #0
        bne nl_orig
        bl centre_row
        ldr r6, [sp, #0x50]
        adds r7, #{manga.LINE_PITCH}
        ldr r2, lit_loop
        bx r2
    nl_orig:
        ldr r3, [sp, #0x50]
        cmp r6, r3
        ldr r2, lit_nl_back
        bx r2

    endstr:                             @ from 0x08012450
        ldr r3, [sp, #0x4c]
        cmp r3, #0
        bne end_m1
        bl centre_row
        bl centre_block
    end_m1:
        ldr r3, [sp, #0x4c]
        cmp r3, #1
        bne end_out
        ldr r0, lit_19ac
        ldr r3, lit_end_store
        bx r3
    end_out:
        ldr r3, lit_end_out
        bx r3

    centre_row:                         @ called with the reader's sp; uses r6 (line end x), r7 (line y)
        ldr r0, [sp, #0x58]
        ldr r1, [sp, #0x50]
        push {{r4, r5, r6, r7, lr}}
        adds r1, r1, r6
        asrs r1, r1, #1
        movs r2, #{CX}
        subs r1, r2, r1
        ldr r4, lit_slots
        ldr r4, [r4]
        movs r3, #0x3c
        lsls r2, r7, #24
        lsrs r2, r2, #24
    cr_loop:
        cmp r3, r0
        bhs cr_done
        lsls r5, r3, #1
        adds r5, r5, r3
        lsls r5, r5, #3
        adds r5, r4, r5
        ldrb r6, [r5]
        cmp r6, r2
        bne cr_next
        ldrh r6, [r5, #2]
        adds r7, r6, r1
        lsls r7, r7, #23
        lsrs r7, r7, #23
        lsrs r6, r6, #9
        lsls r6, r6, #9
        orrs r6, r7
        strh r6, [r5, #2]
    cr_next:
        adds r3, #1
        b cr_loop
    cr_done:
        pop {{r4, r5, r6, r7}}
        pop {{r0}}
        bx r0

    centre_block:                       @ called with the reader's sp
        ldr r0, [sp, #0x58]
        push {{r4, r5, r6, r7, lr}}
        ldr r4, lit_slots
        ldr r4, [r4]
        movs r1, #0xff
        movs r2, #0
        movs r3, #0x3c
    cb_scan:
        cmp r3, r0
        bhs cb_scanned
        lsls r5, r3, #1
        adds r5, r5, r3
        lsls r5, r5, #3
        ldrb r6, [r4, r5]
        cmp r6, r1
        bhs cb_1
        adds r1, r6, #0
    cb_1:
        cmp r6, r2
        bls cb_2
        adds r2, r6, #0
    cb_2:
        adds r3, #1
        b cb_scan
    cb_scanned:
        cmp r2, r1
        blo cb_done
        adds r6, r1, r2
        adds r6, #{INK_H}
        asrs r6, r6, #1
        movs r7, #{CY}
        subs r6, r7, r6
        movs r3, #0x3c
    cb_move:
        cmp r3, r0
        bhs cb_done
        lsls r5, r3, #1
        adds r5, r5, r3
        lsls r5, r5, #3
        ldrb r7, [r4, r5]
        adds r7, r7, r6
        strb r7, [r4, r5]
        adds r3, #1
        b cb_move
    cb_done:
        pop {{r4, r5, r6, r7}}
        pop {{r0}}
        bx r0

        .align 2
    lit_slots: .word {SLOTS:#x}
    lit_grid: .word 0x08733660
    lit_font: .word {0x08000000 | engine.FONT_AT:#x}
    lit_loop: .word 0x08012447
    lit_nl_back: .word 0x08012265
    lit_19ac: .word 0x030019AC
    lit_end_store: .word 0x08012459
    lit_end_out: .word 0x0801245F
    """


def _asm(src, addr):
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, 0x08000000 | addr)
    return bytes(enc)


ENTRIES = {"adv": 0, "newline": 2, "endstr": 4}   # branch table at the top of the handler blob
# Assembled code, so the build needs no assembler: hex text of u16 lookup length, lookup, handlers. `--write`
# regenerates it (keystone); --selftest and tests/test_manga.py check it matches the sources here.
CODE_HEX = Path(__file__).resolve().parents[1] / "data" / "manga_code.hex"


def stored_code():
    return bytes.fromhex("".join(CODE_HEX.read_text(encoding="ascii").split()))


def write_code(blob):
    h = blob.hex()
    CODE_HEX.write_text("".join(h[k:k + 96] + "\n" for k in range(0, len(h), 96)), encoding="ascii", newline="\n")


def _code():
    blob = stored_code()
    n = struct.unpack_from("<H", blob)[0]
    return blob[2:2 + n], blob[2 + n:]


def lookup_bin():
    return _code()[0]


def handlers():
    """(bytes, {entry: thumb address}) of the handler blob at CODE_AT."""
    labels = {k: 0x08000000 | (CODE_AT + v) for k, v in ENTRIES.items()}
    return _code()[1], labels


def assemble():
    lk = _asm(lookup_src(), engine.LOOKUP_AT)
    assert len(lk) <= engine.FONT_AT - engine.LOOKUP_AT
    return struct.pack("<H", len(lk)) + lk + _asm(handlers_src(), CODE_AT)


def hooks(labels):
    """{rom offset: bytes} of the three jumps into the handlers (and the lookup hook from engine.py)."""
    adv = struct.pack("<HHHHI", 0xB510, 0x4C01, 0x4720, 0x46C0, labels["adv"] | 1)   # push {r4,lr}; ldr r4,[pc,#4]; bx r4; nop
    nl = struct.pack("<HHI", 0x4A00, 0x4710, labels["newline"] | 1)                     # ldr r2,[pc,#0]; bx r2
    end = struct.pack("<HHI", 0x4B00, 0x4718, labels["endstr"] | 1)                     # ldr r3,[pc,#0]; bx r3
    return {HOOK_ADV: adv, HOOK_NL: nl, HOOK_END: end, engine.LOOKUP: engine.hook_bytes()}


def font_table(rom, pairs_enc, slices_enc, overrides):
    """Original 990 entries (+ name-letter overrides with their advance), v1 pairs, manga slices (advance at +4)."""
    out = bytearray(rom[engine.ORIG_FONT:engine.ORIG_FONT + engine.ORIG_COUNT * engine.ENTRY])
    for k in range(engine.ORIG_COUNT):
        o = overrides.get((out[k * engine.ENTRY + 2], out[k * engine.ENTRY + 3]))
        if o is not None:
            glyph, adv = o
            out[k * engine.ENTRY + 4:k * engine.ENTRY + 6] = struct.pack("<H", adv)
            out[k * engine.ENTRY + 6:k * engine.ENTRY + 6 + len(glyph)] = glyph
    import font_en
    for k, pair in enumerate(pairs_enc.pairs if pairs_enc else []):
        b0, b1 = font_en.code(k)
        out += struct.pack("<HBBH", len(out) // engine.ENTRY, b0, b1, 0) + font_en.glyph_bytes(pair)
    base = len(out) // engine.ENTRY
    for k, s in enumerate(slices_enc.slices):
        b0, b1 = manga.code(k)
        out += struct.pack("<HBBH", base + k, b0, b1, manga.run_width(s)) + manga.glyph_bytes(s)
    return bytes(out), base


def patch(out, pairs_enc, slices_enc, overrides):
    """Apply the manga engine to bytearray out; return the write list."""
    writes = []

    def put(off, data, who):
        writes.append((off, bytes(out[off:off + len(data)]), data, who))
        out[off:off + len(data)] = data

    table, base = font_table(out, pairs_enc, slices_enc, overrides)
    if engine.FONT_AT + len(table) > CODE_AT:
        raise ValueError(f"font table {len(table):#x} bytes overruns {CODE_AT:#x}")
    code, labels = handlers()
    if CODE_AT + len(code) > PARAMS_AT:
        raise ValueError(f"manga handlers {len(code)} bytes overrun {PARAMS_AT:#x}")
    put(engine.LOOKUP_AT, lookup_bin(), "manga lookup")
    put(engine.FONT_AT, table, f"manga font ({len(slices_enc.slices)} slices)")
    put(CODE_AT, code, "manga handlers")
    put(PARAMS_AT, struct.pack("<I", base), "manga slice base")
    put(engine.TABLE_LITERAL, struct.pack("<I", 0x08000000 | engine.FONT_AT), "engine font pointer")
    for off, data in hooks(labels).items():
        put(off, data, f"manga hook {off:06x}")
    return writes


def allowed(off, n):
    return engine.allowed(off, n) or any(s <= off and off + n <= s + size for s, size in SITES)


def _selftest():
    if assemble() != stored_code():
        print(f"{CODE_HEX.name} is stale: run tools/manga_engine.py --write")
        sys.exit(1)
    code, labels = handlers()
    print(f"selftest ok: lookup {len(lookup_bin())} bytes, handlers {len(code)} bytes, "
          + ", ".join(f"{k} {v:#x}" for k, v in labels.items()))


if __name__ == "__main__":
    if "--write" in sys.argv:
        write_code(assemble())
        print(f"wrote {CODE_HEX}")
    _selftest()

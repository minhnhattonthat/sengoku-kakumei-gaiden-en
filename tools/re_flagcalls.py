"""List call sites of the story-flag helpers with the flag id loaded into r0 just before the BL.

usage: python -X utf8 tools/re_flagcalls.py [ROM]
Prints: helper  caller  r0-guess  containing-function(best guess: nearest preceding push {.., lr})
"""
import struct
import sys

ROM = sys.argv[1] if len(sys.argv) > 1 else "rom/Sengoku Kakumei Gaiden (Japan).gba"
d = open(ROM, "rb").read()
HELPERS = {0x08006A20: "test", 0x08006A50: "set", 0x080069F4: "set184", 0x08006A0C: "get184",
           0x08006A8C: "set188", 0x08006A78: "get188", 0x08006AA4: "set67", 0x08006ABC: "get67"}


def h(o):
    return struct.unpack_from("<H", d, o)[0]


def bl_target(o):
    hi, lo = h(o), h(o + 2)
    if (hi & 0xF800) != 0xF000 or (lo & 0xF800) != 0xF800:
        return None
    off = ((hi & 0x7FF) << 12) | ((lo & 0x7FF) << 1)
    if off & 0x400000:
        off -= 0x800000
    return 0x08000000 + o + 4 + off


def r0_guess(o):
    # walk back up to 6 halfwords: movs r0,#imm [; lsls r0,r0,#k] [; adds r0,#imm]
    val, shift, add = None, 0, 0
    for k in range(1, 7):
        ins = h(o - 2 * k)
        if (ins & 0xFF00) == 0x2000:  # movs r0,#imm
            val = ins & 0xFF
            return (val << shift) + add if val is not None else None
        if (ins & 0xF83F) == 0x0000 and ((ins >> 3) & 7) == 0:  # lsls r0,r0,#k
            shift = (ins >> 6) & 31
        elif (ins & 0xFF00) == 0x3000:  # adds r0,#imm
            add = ins & 0xFF
        elif (ins & 0xFFC7) == 0x1C00:  # adds r0, rX, #0 (mov)
            return None
    return None


def func_start(o):
    for k in range(0, 0x2000, 2):
        ins = h(o - k)
        if (ins & 0xFF00) == 0xB500:
            return 0x08000000 + o - k
    return 0


code_end = 0x0005A000
for o in range(0, code_end, 2):
    t = bl_target(o)
    if t in HELPERS:
        g = r0_guess(o)
        print(f"{HELPERS[t]:7s} {0x08000000 + o:08X} {g if g is not None else '?':>5} fn={func_start(o):08X}")

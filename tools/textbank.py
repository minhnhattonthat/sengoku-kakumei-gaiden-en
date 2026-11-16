"""textbank.py: the game's pointed strings, read from the ROM and written back in place or relocated.

    import textbank
    rom = textbank.original_rom()
    strs = textbank.strings(rom)                      # {addr: Str}, every string a committed site points to
    out = bytearray(rom); writes = textbank.repack(out, {addr: new_bytes})   # bytes without the NUL

A string is EUC-JP plus ASCII control sequences (|n %n %d ...), NUL-terminated, 4-byte aligned (docs/re/text.md).
In place, a string may use its bytes, its NUL and the zero padding up to the next 4-byte boundary (never past the
next pointed string). A longer one moves to free space and every site that pointed at it is rewritten; its old
slot is zero-filled. Bytes between strings that no site reaches (unpointed debug text, padding) are never touched.
"""
import struct
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "data" / "text_sites.tsv"

# (name, start, end exclusive): every range is listed in docs/re/text.md
RANGES = [
    ("menu_help1", 0x04CE4C, 0x04D49A),
    ("system", 0x04E008, 0x04FDD8),
    ("menu_help2", 0x04FDF0, 0x05043E),
    ("story", 0x05045C, 0x055BA6),
    ("provinces", 0x05E2AC, 0x05E776),
    ("save_confirm", 0x061C1C, 0x061C59),
    ("link", 0x07E090, 0x07EF1C),
    ("results", 0x201800, 0x202114),
]
FREE = (0x759178, 0x7C0000)  # 0xFF fill at the end of the 8 MiB ROM (docs/re/rom-map.md); 0x7C0000.. = tools/engine.py


@dataclass
class Str:
    addr: int
    raw: bytes  # without the NUL
    room: int  # bytes usable in place, NUL included
    sites: list = field(default_factory=list)

    @property
    def bank(self):
        return bank_of(self.addr)


def bank_of(addr):
    for name, lo, hi in RANGES:
        if lo <= addr < hi:
            return name
    return None


def original_rom():
    for line in (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            return (ROOT / line.split(None, 1)[1].strip().lstrip("*")).read_bytes()
    raise SystemExit("rom.sha1 lists no ROM")


def load_sites():
    rows = []
    for line in SITES.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            s, t = line.split("\t")
            rows.append((int(s, 16), int(t, 16)))
    return rows


def strings(rom):
    by_addr = {}
    for site, target in load_sites():
        got = struct.unpack_from("<I", rom, site)[0]
        if got != 0x08000000 | target:
            raise ValueError(f"site {site:06x} holds {got:#010x}, data/text_sites.tsv says {target:06x}")
        by_addr.setdefault(target, []).append(site)
    starts = sorted(by_addr)
    out = {}
    for i, a in enumerate(starts):
        end = rom.index(b"\0", a)
        limit = min(starts[i + 1] if i + 1 < len(starts) else 1 << 30, dict((n, h) for n, _, h in RANGES)[bank_of(a)])
        if end >= limit:
            raise ValueError(f"string {a:06x} runs into the next pointed string at {limit:06x}")
        room = min((end + 4) & ~3, limit) - a
        out[a] = Str(a, bytes(rom[a:end]), room, by_addr[a])
    return out


def repack(rom, new, free=FREE, strs=None, force_move=False):
    """Write new[addr] (bytes, no NUL) for each changed string. Returns the write log: (offset, orig, new, writer).
    force_move relocates every string in `new`, changed or not (tests use it to prove the pointer writer)."""
    strs = strs if strs is not None else strings(rom)
    writes = []
    cursor = (free[0] + 3) & ~3
    placed = {}  # bytes -> address already holding them in free space

    def put(off, data, who):
        writes.append((off, bytes(rom[off:off + len(data)]), bytes(data), who))
        rom[off:off + len(data)] = data

    for addr in sorted(new):
        s = strs[addr]
        data = bytes(new[addr])
        if b"\0" in data:
            raise ValueError(f"{addr:06x}: text contains a NUL")
        if data == s.raw and not force_move:
            continue
        who = f"text {addr:06x}"
        if len(data) + 1 <= s.room and not force_move:
            put(addr, data + bytes(s.room - len(data)), who)
            continue
        dest = placed.get(data)
        if dest is None:
            dest = cursor
            if dest + len(data) + 1 > free[1]:
                raise ValueError(f"free space full placing {addr:06x}")
            put(dest, data + b"\0", who + " moved")
            placed[data] = dest
            cursor = (dest + len(data) + 1 + 3) & ~3
        for site in s.sites:
            put(site, struct.pack("<I", 0x08000000 | dest), who + " ptr")
        put(addr, bytes(s.room), who + " old slot")
    return writes


def write_log(path, writes):
    with open(path, "w", encoding="utf-8") as f:
        for off, orig, new, who in writes:
            if orig != new:
                f.write(f"{off:06x} {orig.hex()} {new.hex()} {who}\n")

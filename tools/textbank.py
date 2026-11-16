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
import json
import struct
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITES = ROOT / "data" / "text_sites.tsv"
LAYOUT = ROOT / "data" / "text_layout.tsv"

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
# 0x759178-0x7FFFFF is 0xFF fill, but the magatama page (ev105-112) runs CpuSet(0x087573D8 -> 0x05001FE0, 0x34BB4
# halfwords), reading up to 0x087C0B40 into palette RAM: the last 1 KB (0xFF) is what makes that page white, and the
# rest flashes through the palette during the copy. So that range stays untouched (docs/re/english.md).
PALETTE_READ = (0x759178, 0x7C0B40)
FREE = (0x7C1000, 0x7D8000)      # text relocation (uses about 25 KB of it)
GFX_FREE = (0x7D8000, 0x7E0000)  # LZ blocks that outgrew their slot (build.py relocated_lz); 0x7E0000.. = engine


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


def load_layout(path=LAYOUT):
    """The frozen layout of the QA-toured build: ({source addr: dest}, end of the used free space, [letter pairs
    in code order] for font_en.Encoder), or None if there is none."""
    if not path.exists():
        return None
    lay, end, pairs = {}, None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# end "):
            end = int(line.split()[2], 16)
        elif line.startswith("# pairs "):
            pairs = json.loads(line[len("# pairs "):])
        elif line and not line.startswith("#"):
            s, d = line.split("\t")
            lay[int(s, 16)] = int(d, 16)
    return lay, end, pairs


def save_layout(writes, pairs, path=LAYOUT):
    """Freeze this build's relocation (from repack's write log) and letter pairs into data/text_layout.tsv."""
    lay, end = {}, None
    for off, _, data, who in writes:
        if who.startswith("text ") and who.endswith(" ptr"):
            lay[int(who.split()[1], 16)] = struct.unpack("<I", data)[0] - 0x08000000
        if who.startswith("text ") and who.endswith(" moved"):
            end = max(end or 0, (off + len(data) + 3) & ~3)
    rows = "".join(f"{s:06x}\t{d:06x}\n" for s, d in sorted(lay.items()))
    path.write_text("# text_layout.tsv: relocated string -> its address in free space, frozen from the QA-toured\n"
                    "# build (textbank.repack keeps these slots so a text edit moves only the edited string; text\n"
                    "# coverage logs and tour sheets stay valid). Regenerate: build.py freeze-layout.\n"
                    f"# end {end:06x}\n# pairs {json.dumps(list(pairs))}\n" + rows, encoding="utf-8", newline="\n")


def repack(rom, new, free=FREE, strs=None, force_move=False, layout=None):
    """Write new[addr] (bytes, no NUL) for each changed string. Returns the write log: (offset, orig, new, writer).
    force_move relocates every string in `new`, changed or not (tests use it to prove the pointer writer).
    layout = load_layout(): a relocated string keeps its frozen slot while it fits; the rest go after layout's end."""
    strs = strs if strs is not None else strings(rom)
    writes = []
    cursor = (free[0] + 3) & ~3
    placed = {}  # bytes -> address already holding them in free space

    def moves(addr, data):
        return force_move or (data != strs[addr].raw and len(data) + 1 > strs[addr].room)

    # Frozen slots first: a relocated string keeps its slot from the toured build while it still fits (one payload
    # per slot), so editing one string never shifts the others. Newcomers go after the layout's end.
    frozen = {}  # addr -> slot
    if layout:
        lay, lay_end = layout[:2]
        dests = sorted(set(lay.values()))
        size = {d: (dests[i + 1] if i + 1 < len(dests) else lay_end) - d for i, d in enumerate(dests)}
        cursor = max(cursor, lay_end)
        payload = {}
        for addr in sorted(new):
            data, d = bytes(new[addr]), lay.get(addr)
            if d is not None and moves(addr, data) and len(data) + 1 <= size[d] \
                    and payload.setdefault(d, data) == data:
                frozen[addr] = d

    def put(off, data, who):
        writes.append((off, bytes(rom[off:off + len(data)]), bytes(data), who))
        rom[off:off + len(data)] = data

    for addr in sorted(new):
        s = strs[addr]
        data = bytes(new[addr])
        if b"\0" in data:
            raise ValueError(f"{addr:06x}: text contains a NUL")
        if not moves(addr, data):
            if data != s.raw:
                put(addr, data + bytes(s.room - len(data)), f"text {addr:06x}")
            continue
        who = f"text {addr:06x}"
        dest = frozen.get(addr)
        if dest is not None:
            if placed.get(data) != dest:
                put(dest, data + b"\0", who + " moved")
                placed.setdefault(data, dest)
        elif (dest := placed.get(data)) is None:
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


def relocated(writes):
    """Source addresses of every string repack moved out of its slot. Taken from the ' old slot' entries, not
    ' moved': a string whose English payload another string already placed shares that copy and gets no ' moved'."""
    return {int(w[3].split()[1], 16) for w in writes if w[3].endswith(" old slot")}


def write_log(path, writes):
    with open(path, "w", encoding="utf-8") as f:
        for off, orig, new, who in writes:
            if orig != new:
                f.write(f"{off:06x} {orig.hex()} {new.hex()} {who}\n")

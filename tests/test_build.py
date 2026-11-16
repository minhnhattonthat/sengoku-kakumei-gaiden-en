"""Phase 7 ROM-level checks on an English build made in memory (never a stale build/ file):
references/pipeline.md §Checks. build.verify (allowed ranges + romdiff with the write log) runs first."""
import re
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

try:
    import build  # noqa: E402
    import capstone  # noqa: E402
    import engine  # noqa: E402
    import script  # noqa: E402
    import textbank  # noqa: E402
    ORIG = textbank.original_rom()
except (FileNotFoundError, OSError):
    ORIG = None

JAPANESE = re.compile(r"[぀-ヿ一-鿿＀-￯]")
KEEP_JP = ROOT / "script" / "keep_jp.txt"
# docs/re/rom-map.md: sound samples (0x440000..) and LZ77 screen graphics (..0x68FFFF). Their bytes are noise: the
# scan found 14 words there that look like pointers into moved strings, 13 of them mid-string (2026-11-16).
NOISE = (0x440000, 0x690000)
# Pointer-looking words into moved strings, each checked by hand (2026-11-16, phase 7 review): byte tables whose
# bytes happen to read 0x0805xxxx, all landing mid-string in 04ffe4 (menu_help2, a dedup relocation).
NOT_POINTERS = {
    "04dd90->0x8050000",  # 0x4DD80.. rows "ff000000 00000508 121314ff": byte records (00 00 05 08 + tile ids)
    "04dd9c->0x8050000",  # same table
    "72b56c->0x8050002",  # "e0030000 02000508 08140c1c": byte fields of a graphics/OBJ record, not a pointer
}
# Original bytes at the engine's hook sites (assert before trusting a patch made for this revision).
HOOK_ORIG = {engine.LOOKUP: "70b50004050c0024", engine.TABLE_LITERAL: "28217108"} if ORIG else {}


def stale_readers(rom, moved, strs, sites, noise=NOISE):
    """Words of `rom` outside `sites` (and the noise range) that point at or into a string in `moved`."""
    spans = set()
    for a in moved:
        spans.update(0x08000000 | (a + k) for k in range(len(strs[a].raw) + 1))
    return [f"{off:06x}->{v:#x}" for off in range(0, len(rom) - 3, 4)
            if (v := struct.unpack_from("<I", rom, off)[0]) in spans and off not in sites
            and not noise[0] <= off < noise[1]]


class SharedPayload(unittest.TestCase):
    def test_dedup_relocation_is_checked(self):
        """Two strings get the same long English: the second shares the first's copy (no ' moved' entry), yet its
        slot is cleared, so an unlisted reader of it must still be caught."""
        rom = bytearray(0x400)
        rom[0x100:0x104] = b"AB\0\0"
        rom[0x200:0x204] = b"CD\0\0"
        struct.pack_into("<III", rom, 0x10, 0x08000100, 0x08000200, 0x08000200)  # 0x18 = unlisted reader of 0x200
        strs = {0x100: textbank.Str(0x100, b"AB", 4, [0x10]), 0x200: textbank.Str(0x200, b"CD", 4, [0x14])}
        writes = textbank.repack(rom, {0x100: b"LONGER", 0x200: b"LONGER"}, free=(0x300, 0x400), strs=strs)
        self.assertEqual(sum(w[3].endswith(" moved") for w in writes), 1)
        self.assertEqual(textbank.relocated(writes), {0x100, 0x200})
        orig = bytearray(0x400)
        orig[0x100:0x104], orig[0x200:0x204] = b"AB\0\0", b"CD\0\0"
        struct.pack_into("<III", orig, 0x10, 0x08000100, 0x08000200, 0x08000200)
        self.assertEqual(stale_readers(orig, textbank.relocated(writes), strs, {0x10, 0x14}, noise=(0, 0)),
                         ["000018->0x8000200"])


def keep_list():
    return {line.split()[0] for line in KEEP_JP.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


@unittest.skipIf(ORIG is None, "rom/ absent")
class EnglishBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edits = script.load_en()
        cls.new, cls.writes, cls.enc = build.make_english(ORIG, cls.edits, textbank.load_layout())  # as build.py
        build.verify(ORIG, cls.new, cls.writes)
        cls.strs = textbank.strings(ORIG)

    def read(self, rom, addr):
        return rom[addr:rom.index(b"\0", addr)]

    def test_every_site_reads_its_english(self):
        """Every pointer slot of every edited string, in the built ROM, reaches exactly that string's bytes;
        so every entry with English was written, in place or moved."""
        bad = []
        for addr, text in self.edits.items():
            want = self.enc.encode(text)
            for site in self.strs[addr].sites:
                ptr = struct.unpack_from("<I", self.new, site)[0]
                if not 0x08000000 <= ptr < 0x08800000 or self.read(self.new, ptr - 0x08000000) != want:
                    bad.append(f"{addr:06x} via {site:06x}")
        self.assertEqual(bad, [], f"{len(bad)} sites wrong: {bad[:10]}")
        self.assertEqual(len(self.edits), sum(1 for _ in self.edits))

    def test_moved_strings_leave_no_reader(self):
        """No word in the original ROM other than a known site points at (or into) a string the build moved,
        deduplicated relocations included (textbank.relocated)."""
        moved = textbank.relocated(self.writes)
        self.assertGreaterEqual(len(moved), len({w[3] for w in self.writes if w[3].endswith(" moved")}))
        stale = stale_readers(ORIG, moved, self.strs, {s for s, _ in textbank.load_sites()})
        stale = [s for s in stale if s not in NOT_POINTERS]
        self.assertEqual(stale, [], f"stale readers: {stale[:20]}")

    def test_hook_sites_hold_the_original_bytes(self):
        for off, hexbytes in HOOK_ORIG.items():
            self.assertEqual(ORIG[off:off + len(hexbytes) // 2].hex(), hexbytes, f"{off:06x}")

    def test_hook_swallows_no_branch_target(self):
        """No Thumb branch within 4 KB of the lookup hook, and no literal-pool code pointer anywhere, lands strictly
        inside the 8 overwritten bytes."""
        lo, hi = 0x08000000 + engine.LOOKUP, 0x08000000 + engine.LOOKUP + 8
        md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
        md.skipdata = True
        start = engine.LOOKUP - 0x1000
        inside = []
        for ins in md.disasm(ORIG[start:engine.LOOKUP + 0x1000], 0x08000000 + start):
            if ins.mnemonic.startswith("b") and ins.op_str.startswith("#"):
                target = int(ins.op_str[1:], 16)
                if lo < target < hi:
                    inside.append(f"{ins.address:#x} {ins.mnemonic} {ins.op_str}")
        pool = [f"{off:06x}" for off in range(0, len(ORIG) - 3, 4)
                if lo < (struct.unpack_from("<I", ORIG, off)[0] & ~1) < hi]
        self.assertEqual(inside + pool, [])

    def test_no_japanese_in_english(self):
        bad = [f"{a:06x}" for a, t in self.edits.items() if JAPANESE.search(t)]
        self.assertEqual(bad, [])

    def test_untranslated_only_on_keep_list(self):
        keep = keep_list()
        missing = sorted(e["id"] for entries in script.load().values() for e in entries
                         if e["kind"] == "text" and e["jp"].strip() and int(e["id"], 16) not in self.edits
                         and e["id"] not in keep)
        self.assertEqual(missing, [], "Japanese text with no English and not in script/keep_jp.txt")


if __name__ == "__main__":
    unittest.main()

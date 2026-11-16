"""8bpp link cards (tools/link_card.py) and LZ relocation (build.RELOCATABLE_LZ)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
import link_card  # noqa: E402
import lz77  # noqa: E402
import textbank  # noqa: E402


class TestLinkCard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()
        cls.edits = link_card.lz_edits(cls.rom)

    def test_records_point_at_the_blocks(self):
        # picture record: idx, 600-byte block, defs, tiles, palette
        for name, c in link_card.CARDS.items():
            rec = build.RELOCATABLE_LZ[c["idx"]][0]
            words = [w - 0x08000000 for w in struct.unpack_from("<5I", self.rom, rec)]
            self.assertEqual(words[0], c["idx"], name)
            self.assertEqual(words[2:], [c["defs"], c["tiles"], c["pal"]], name)

    def test_new_blocks_round_trip(self):
        for name in link_card.CARDS:
            idx, defs, tiles = link_card.blocks(self.rom, name)
            self.assertEqual((len(idx), len(tiles)), (2400, 32768), name)
            n = struct.unpack_from("<I", defs, 8)[0]
            self.assertEqual(len(defs), 16 + 2 * n)
            self.assertLess(max(i & 0xFFFF for i in struct.unpack("<600I", idx)), n)
            new, old = link_card.render(idx, defs, tiles), link_card.render(*link_card.originals(self.rom, name))
            self.assertEqual(new[-1], old[-1], f"{name}: the bottom border stays as it was")

    def test_relocatable_sites_are_every_pointer(self):
        for off, sites in build.RELOCATABLE_LZ.items():
            hits, p = [], struct.pack("<I", 0x08000000 + off)
            i = self.rom.find(p)
            while i >= 0:
                hits.append(i)
                i = self.rom.find(p, i + 1)
            self.assertEqual(hits, sites, f"{off:06x}: every pointer to the block must be listed")

    def test_moved_blocks_land_in_graphics_free_space(self):
        new, _ = build.repack(self.rom, build.unpack(self.rom), lz_edits=self.edits)
        lo, hi = textbank.GFX_FREE
        for off, sites in build.RELOCATABLE_LZ.items():
            if off not in self.edits:
                continue   # another module's block (title picture: tests/test_title_logo.py)
            dest = struct.unpack_from("<I", new, sites[0])[0] - 0x08000000
            if dest != off:
                self.assertTrue(lo <= dest < hi, f"{off:06x} -> {dest:06x}")
            self.assertEqual(lz77.decompress(new, dest)[0], self.edits[off])


if __name__ == "__main__":
    unittest.main()

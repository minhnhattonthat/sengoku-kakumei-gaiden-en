"""Link-error card (tools/link_card.py) and LZ relocation (build.RELOCATABLE_LZ)."""
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

    def test_render_reads_the_blocks(self):
        rows = link_card.render(*(link_card.decoded(self.rom, o) for o in
                                  (link_card.IDX, link_card.DEFS, link_card.TILES)))
        self.assertEqual(len(rows), 160)
        self.assertIn(link_card.WHITE, {v for r in rows for v in r})

    def test_new_blocks_round_trip(self):
        idx, defs, tiles = link_card.blocks(self.rom)
        self.assertEqual(len(idx), 2400)
        self.assertEqual(len(tiles), 32768)
        n = struct.unpack_from("<I", defs, 8)[0]
        self.assertEqual(len(defs), 16 + 2 * n)
        ids = struct.unpack("<600I", idx)
        self.assertLess(max(i & 0xFFFF for i in ids), n)
        rows = link_card.render(idx, defs, tiles)
        old = link_card.render(*(link_card.decoded(self.rom, o) for o in
                                 (link_card.IDX, link_card.DEFS, link_card.TILES)))
        self.assertEqual(rows[0], old[0], "the border rows stay as they were")
        self.assertEqual(rows[-1], old[-1])

    def test_relocatable_sites_point_at_their_block(self):
        for off, sites in build.RELOCATABLE_LZ.items():
            hits = []
            p = struct.pack("<I", 0x08000000 + off)
            i = self.rom.find(p)
            while i >= 0:
                hits.append(i)
                i = self.rom.find(p, i + 1)
            self.assertEqual(hits, sites, f"{off:06x}: every pointer to the block must be listed")

    def test_moved_blocks_land_in_graphics_free_space(self):
        unpacked = build.unpack(self.rom)
        new, writes = build.repack(self.rom, unpacked, lz_edits=link_card.lz_edits(self.rom))
        lo, hi = textbank.GFX_FREE
        for off, sites in build.RELOCATABLE_LZ.items():
            for s in sites:
                dest = struct.unpack_from("<I", new, s)[0] - 0x08000000
                if dest != off:
                    self.assertTrue(lo <= dest < hi, f"{off:06x} -> {dest:06x}")
                data = lz77.decompress(new, dest)[0]
                self.assertEqual(data, link_card.lz_edits(self.rom)[off])


if __name__ == "__main__":
    unittest.main()

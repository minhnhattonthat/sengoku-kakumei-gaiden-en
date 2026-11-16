"""Latin name entry (tools/name_grid.py): letter table, font overrides, grid picture edit."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import engine  # noqa: E402
import lz77  # noqa: E402
import name_grid  # noqa: E402
import textbank  # noqa: E402


class TestNameGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()

    def test_table_is_the_kana_grid(self):
        codes = name_grid.codes(self.rom)
        self.assertEqual(bytes([codes[0] & 0xFF, codes[0] >> 8]).decode("euc_jp"), "あ")
        self.assertEqual(bytes([codes[84] & 0xFF, codes[84] >> 8]).decode("euc_jp"), "　")
        real = [c for c in codes if c != 0xA1A1]
        self.assertEqual(len(real), len(set(real)), "a kana twice: two letters would share one glyph")

    def test_every_slot_but_the_gaps_has_a_letter(self):
        codes = name_grid.codes(self.rom)
        self.assertEqual({k for k in range(name_grid.COUNT) if codes[k] != 0xA1A1}, set(name_grid.LETTERS))
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789":
            self.assertIn(c, name_grid.LETTERS.values())

    def test_font_overrides_land_on_the_kana_entries(self):
        ov = name_grid.glyph_overrides(self.rom)
        self.assertEqual(len(ov), len(name_grid.LETTERS))
        table = engine.font_table(self.rom, type("E", (), {"pairs": []})(), ov)
        hits = 0
        for k in range(engine.ORIG_COUNT):
            e = table[k * engine.ENTRY:(k + 1) * engine.ENTRY]
            g = ov.get((e[2], e[3]))
            if g:
                self.assertEqual(e[6:6 + len(g)], g)
                hits += 1
        self.assertEqual(hits, len(ov))

    def test_grid_edit_fits_its_lz_slot(self):
        edits = name_grid.lz_edits(self.rom)
        self.assertEqual(set(edits), set(name_grid.PICTURES))  # group 6 (0x5AEA30) and group 7 (0x5B14B4)
        for blk, data in edits.items():
            self.assertEqual(len(data), len(lz77.decompress(self.rom, blk)[0]), hex(blk))
            self.assertNotEqual(data, lz77.decompress(self.rom, blk)[0], hex(blk))
            size = struct.unpack_from("<I", self.rom, blk)[0] >> 8
            self.assertEqual(size, len(data), hex(blk))

    def test_group7_record_points_at_its_block(self):
        # picture group 7 = getter 0x08049BBC -> records at 0x74FAC8 (36 bytes each), tiles ptr at +12
        self.assertEqual(struct.unpack_from("<I", self.rom, 0x74FAC8 + 12)[0] - 0x08000000, 0x5B14B4)


if __name__ == "__main__":
    unittest.main()

"""The menu stat panel draws the player's name with the 8x8 small font: its kana (from 0x7BC58, the name table
without its two gaps) must carry name_grid's Latin letters, or a name entered as "AAA" shows as あああ there."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_labels  # noqa: E402
import name_grid  # noqa: E402
import textbank  # noqa: E402


class TestSmallKana(unittest.TestCase):
    def test_index_skips_table_gaps(self):
        self.assertEqual([gfx_labels.small_kana_index(k) for k in (0, 35, 37, 39, 40, 83)], [0, 35, 36, 37, 38, 81])

    def test_every_letter_redrawn(self):
        rom = textbank.original_rom()
        (off, data), = gfx_labels.small_kana_edits(rom).items()
        self.assertEqual(off, gfx_labels.SMALL_KANA)
        for k, ch in name_grid.LETTERS.items():
            i = gfx_labels.small_kana_index(k)
            self.assertEqual(data[32 * i:32 * i + 32], gfx_labels.small_glyph(ch), ch)
        self.assertNotEqual(data[:32], rom[off:off + 32])  # あ -> A


if __name__ == "__main__":
    unittest.main()

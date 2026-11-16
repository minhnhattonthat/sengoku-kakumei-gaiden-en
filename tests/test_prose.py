"""Ending cards (tools/prose.py): block layout, round trip of the English pictures, the THE END OBJ edit."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
import lz77  # noqa: E402
import prose  # noqa: E402
import textbank  # noqa: E402


class TestProse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()
        cls.edits = prose.lz_edits(cls.rom)
        cls.blocks = {o: (e, n) for o, e, n in build.lz_blocks()}

    def test_cards_are_idx_defs_tiles_triples(self):
        for idx, defs, tiles, _, _ in prose.CARDS:
            self.assertEqual(self.blocks[idx][1], 160)
            self.assertEqual(self.blocks[defs][1], 8208)
            self.assertIn(self.blocks[tiles][1], (8192, 16384))
            head = lz77.decompress(self.rom, defs)[0][:12]
            self.assertEqual(struct.unpack("<3I", head), (4, 4, 256))

    def test_edits_keep_sizes_and_fit_their_slots(self):
        self.assertEqual(len(self.edits), 3 * len(prose.CARDS))
        for off, data in self.edits.items():
            end, size = self.blocks[off]
            self.assertEqual(len(data), size, f"{off:06x}")
            self.assertLessEqual(len(lz77.compress(data)), ((end + 3) & ~3) - off, f"{off:06x}")

    def test_picture_round_trips(self):
        for card in prose.CARDS:
            want = prose.draw_card(card[3], card[4], prose.background(self.rom, card))
            got = prose.render(self.rom, card, self.edits)
            self.assertEqual(got, [row[:prose.SW] for row in want], card[3] or card[4][0][0])

    def test_text_fits_the_screen(self):
        for card in prose.CARDS:
            for v, u, bold, text in prose.layout(card[3], card[4]):
                self.assertLessEqual(v + 9, prose.SW)
                self.assertLessEqual(u + len(text) * (prose.BOLD_ADV if bold else prose.ADV), prose.SH)

    def test_end_card_obj_tiles(self):
        (off, data), = prose.end_edits().items()
        self.assertEqual(off, 0x71BAD8)
        self.assertEqual(len(data), 144 * 32)
        self.assertTrue(build.allowed_write(off, len(data)))
        self.assertEqual({v for b in data for v in (b & 15, b >> 4)}, {0, 15})


if __name__ == "__main__":
    unittest.main()

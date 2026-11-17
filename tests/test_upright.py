"""Upright pieces of the one edition (D18/D19): tools/upright.py (name-grid header and OK, link cards) and the
player-name letters."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import manga  # noqa: E402
import name_grid  # noqa: E402
import upright  # noqa: E402


class TestUpright(unittest.TestCase):
    def test_selftest(self):
        upright._selftest()

    def test_name_grid_labels_fit(self):
        for text, (x0, y0, w, h) in name_grid.HEADERS + name_grid.LABELS:
            lay = upright.stack(text, h - 1, w - 2)
            self.assertLessEqual(lay.h, h, text)
            self.assertLessEqual(lay.w, w, text)

    def test_name_capital_i_is_not_a_bar(self):
        """D19: a name's I has serifs, so it is not read as a lower-case l in the name box."""
        self.assertNotEqual(manga.name_art("I"), manga.name_art("l"))
        self.assertEqual(len(manga.name_art("I")[0]), 3)
        self.assertEqual(manga.name_adv("I"), 4)
        g = manga.name_glyph("I")
        self.assertEqual(len(g), 26)

    def test_name_letters_keep_their_case(self):
        """Upper-case block letters are upper case, lower-case block letters lower case (owner report D19)."""
        cells = name_grid.cells()
        top = {k for k, (x, y) in cells.items() if y < name_grid.ROW_Y0[2]}
        for k, ch in name_grid.LETTERS.items():
            if ch.isalpha():
                self.assertEqual(ch.isupper(), k in top, (k, ch))


if __name__ == "__main__":
    unittest.main()

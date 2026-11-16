"""Bank 30's Yes/No and link time choices are centred in their 44-row bars, as the originals fill them;
bank 27's choices stay top-aligned like theirs."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_labels  # noqa: E402
import textbank  # noqa: E402


def ink_span(slot):
    rows = [i for i, r in enumerate(slot) if any(v not in (0, gfx_labels.OUT_BG) for v in r)]
    return rows[0], rows[-1]


class TestOutlineCentre(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()

    def test_bank30_centred(self):
        _, _, new = gfx_labels.english_rows(self.rom, 30)
        for start, n, jp, en in gfx_labels.load_tsv(30):
            top, bottom = ink_span(new[start:start + n])
            self.assertLessEqual(abs(top - (n - 1 - bottom)), 2, f"{en!r}: rows {top}-{bottom} of {n}")

    def test_bank27_top_aligned(self):
        _, _, new = gfx_labels.english_rows(self.rom, 27)
        start, n, jp, en = next(r for r in gfx_labels.load_tsv(27) if r[3] == "Yes")
        self.assertLessEqual(ink_span(new[start:start + n])[0], gfx_labels.OUT_TOP)


if __name__ == "__main__":
    unittest.main()

"""Upright labels (D17/D18): tools/upright.py layout, every label bank rendered, the results screen's stacking."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_labels  # noqa: E402
import manga  # noqa: E402
import script  # noqa: E402
import textbank  # noqa: E402
import upright  # noqa: E402


class TestUpright(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()

    def test_selftest(self):
        upright._selftest()

    def test_whole_words_before_broken_ones(self):
        lay = gfx_labels.fit_scaled("WOMAN", 60, 59, [(6, 3), (3, 1.5)], gap=2, fonts=("manga",))
        self.assertEqual(lay.columns, ["WOMAN"])

    def test_every_label_bank_renders(self):
        for path in sorted((ROOT / "gfx").glob("bank*.tsv")):
            bank = int(path.stem[4:])
            with self.subTest(bank=bank):
                gfx_labels.labels_edits(self.rom, {bank})

    def test_strip_labels_stay_in_their_slot(self):
        """Every strip label's ink stays inside its 16 px slot (english_rows raises on overflow; this checks the
        rows outside every slot are untouched)."""
        for bank, style in gfx_labels.STYLE.items():
            b, rows, new = gfx_labels.english_rows(self.rom, bank)
            inside = set()
            for start, n, _, en in gfx_labels.load_tsv(bank):
                if en:
                    inside |= set(range(start, start + n))
            for y in range(len(rows)):
                if y not in inside and bank not in gfx_labels.PIECED:
                    self.assertEqual(rows[y], new[y], f"bank {bank} row {y}")

    def test_plates_are_syllable_lines(self):
        self.assertEqual(upright.syllables("SHIMOTSUKE"), ["SHI", "MO", "TSU", "KE"])
        self.assertEqual(upright.syllables("SETTSU"), ["SET", "TSU"])
        self.assertEqual(upright.syllables("BITCHU"), ["BIT", "CHU"])
        self.assertEqual(upright.syllables("ECHIZEN"), ["E", "CHI", "ZEN"])
        for line in (ROOT / "gfx" / "bank20.tsv").read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                name = line.split("\t")[2]
                lay = gfx_labels.plate_layout(name, 24, 14)
                self.assertLessEqual(len(lay.columns), 4, name)

    def test_results_labels_stack_within_the_column(self):
        labels = {int(e["id"], 16): e["en"] for e in script.load()["results"] if e["kind"] == "text" and e["en"]}
        bg = {t for a, t in labels.items() if a in manga.BG_LABELS}
        enc = manga.StackEncoder(labels.values(), 0, bg=bg)
        for t in labels.values():
            if t not in bg:
                self.assertLessEqual(enc.length(t, enc.font_of[t]), manga.STACK_LIMIT, t)
            self.assertTrue(enc.encode(t))
        for code_index, glyph, field in enc.entries():
            self.assertEqual(len(glyph), 26)
            self.assertLess(field >> 8, 16)


if __name__ == "__main__":
    unittest.main()

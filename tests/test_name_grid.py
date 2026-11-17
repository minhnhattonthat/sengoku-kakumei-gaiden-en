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

    @staticmethod
    def letters_and_shadow(text, x0, y0, w, h):
        pts = name_grid.header_points(text, x0, y0, w, h)
        return {(y + dy, x + dx) for y, x in pts for dy in (0, 1) for dx in (0, 1)}

    def test_grid_reads_left_to_right(self):
        """D18: upright letters, so the top row of each block reads A.. / a.. from the left."""
        cells = name_grid.cells()
        top = sorted((x, name_grid.LETTERS[k]) for k, (x, y) in cells.items()
                     if y == name_grid.ROW_Y0[1] and k in name_grid.LETTERS)
        self.assertEqual("".join(ch for _, ch in top), "ABCDEFGHI")

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

    def test_header_rows_carry_no_brush_ink(self):
        """Outside the letters (ink 1, shadow 8), no header row keeps a brush pixel: an antialiased edge pixel
        alternated across a row drew dotted lines beside "Your Name" (visual QA, build 4977f45e)."""
        edits = name_grid.lz_edits(self.rom)
        for blk, path in name_grid.PICTURES.items():
            m, data = name_grid.load_map(path), edits[blk]
            ink = name_grid.HEADER_INK[name_grid.HEADER_FILL[blk]]
            text, (x0, y0, w, h) = name_grid.HEADERS[0]
            h = name_grid.HEADER_H.get(blk) or h
            near = self.letters_and_shadow(text, x0, y0, w, h)
            for y in range(y0, y0 + h):
                for x in range(x0, x0 + w):
                    i, hi, _ = name_grid.where(m, x, y)
                    v = data[i] >> 4 if hi else data[i] & 15
                    if (y, x) not in near:
                        self.assertNotIn(v, ink, f"{hex(blk)} x {x} y {y}")

    def test_header_gradient_runs_one_way_without_dotted_rows(self):
        """The "Your Name" background is a dark-to-light ramp: no row lighter than the one below it, and a row mixing
        two shades only as half of a 2-row dither, never alone (lone rows read as dotted lines, visual QA 093e9076;
        group 7's mixed palettes once drew a band out of order)."""
        edits = name_grid.lz_edits(self.rom)
        for blk, path in name_grid.PICTURES.items():
            m, data = name_grid.load_map(path), edits[blk]
            text, (x0, y0, w, h) = name_grid.HEADERS[0]
            h = name_grid.HEADER_H.get(blk) or h
            near = self.letters_and_shadow(text, x0, y0, w, h)
            means, mixed = [], []
            for y in range(y0, y0 + h):
                vals = []
                for x in range(x0, x0 + w):
                    if (y, x) in near:
                        continue
                    i, hi, _ = name_grid.where(m, x, y)
                    v = data[i] >> 4 if hi else data[i] & 15
                    vals.append(name_grid.lightness(self.rom, name_grid.HEADER_PAL[blk], m[(x // 8, y // 8)] >> 12, v))
                means.append(sum(vals) / len(vals) if vals else None)
                mixed.append(max(vals) - min(vals) > 0.2 if vals else False)
            seen = [v for v in means if v is not None]
            for a, b in zip(seen, seen[1:]):
                self.assertLessEqual(a, b + 0.05, f"{hex(blk)}: header ramp goes back")
            for k, mx in enumerate(mixed):
                if mx:
                    self.assertTrue((k > 0 and mixed[k - 1]) or (k + 1 < len(mixed) and mixed[k + 1]),
                                    f"{hex(blk)}: lone dither row {y0 + k}")

    def test_group7_record_points_at_its_block(self):
        # picture group 7 = getter 0x08049BBC -> records at 0x74FAC8 (36 bytes each), tiles ptr at +12
        self.assertEqual(struct.unpack_from("<I", self.rom, 0x74FAC8 + 12)[0] - 0x08000000, 0x5B14B4)


if __name__ == "__main__":
    unittest.main()

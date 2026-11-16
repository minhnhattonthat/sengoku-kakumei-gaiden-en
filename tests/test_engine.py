"""English engine: font, pair encoder, lookup patch, marker build (tools/font_en.py, tools/engine.py)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import engine  # noqa: E402
import font_en  # noqa: E402
import marker  # noqa: E402


class TestFont(unittest.TestCase):
    def test_every_printable_has_a_glyph(self):
        self.assertEqual(set(font_en.FONT), set(font_en.PRINTABLE))

    def test_glyphs_stay_inside_the_12px_cell(self):
        for a in font_en.PRINTABLE:
            for b in "Mgj|_":
                rows = font_en.glyph_rows(a + b)
                self.assertEqual(len(rows), font_en.GLYPH_ROWS)
                self.assertEqual(rows[11] | rows[12], 0, a + b)       # 1 px gap before the next cell
                for v in rows:
                    self.assertEqual(v & 0b1100000000011111, 0, a + b)  # x 0-1 and 11-15 stay clear

    def test_encoder(self):
        e = font_en.Encoder(["Hello, %n!|nGo.", "it’s"])
        b = e.encode("Hello, %n!|nGo.")
        self.assertEqual(b.count(b"%n"), 1)
        self.assertEqual(b.count(b"|n"), 1)
        body = b.replace(b"%n", b"").replace(b"|n", b"")
        self.assertTrue(all(0x80 <= body[i] < 0xA0 and body[i + 1] >= 0x80 for i in range(0, len(body), 2)))
        self.assertNotIn(0, b)
        self.assertEqual(e.encode("it's"), e.encode("it’s"))
        with self.assertRaises(ValueError):
            font_en.Encoder(["あ"])

    def test_cells(self):
        self.assertEqual(font_en.cells("abc"), 2)
        self.assertEqual(font_en.cells("ab%ncd"), 2)


class TestEngine(unittest.TestCase):
    def test_lookup_blob_matches_source(self):
        try:
            import keystone  # noqa: F401
        except ImportError:
            self.skipTest("keystone not installed")
        self.assertEqual(engine.lookup_code(engine.FONT_AT), engine.LOOKUP_BIN)

    def test_hook(self):
        self.assertEqual(engine.hook_bytes(), struct.pack("<HHI", 0x4B00, 0x4718, 0x087C0001))

    def test_patch_on_rom(self):
        rom = ROOT / "rom" / "Sengoku Kakumei Gaiden (Japan).gba"
        if not rom.exists():
            self.skipTest("no ROM")
        out = bytearray(rom.read_bytes())
        enc = font_en.Encoder(["Ab cd"])
        writes = engine.patch(out, enc)
        self.assertTrue(all(engine.allowed(o, len(n)) for o, _, n, _ in writes))
        k = enc.index["Ab"]
        entry = engine.FONT_AT + (engine.ORIG_COUNT + k) * engine.ENTRY
        self.assertEqual(out[entry + 2:entry + 4], font_en.code(k))
        self.assertEqual(out[entry + 6:entry + 32], font_en.glyph_bytes("Ab"))
        # the original glyphs are copied unchanged
        self.assertEqual(out[engine.FONT_AT:engine.FONT_AT + 990 * 32], out[engine.ORIG_FONT:engine.ORIG_FONT + 990 * 32])


class TestMarker(unittest.TestCase):
    def test_marker_keeps_layout(self):
        m = marker.marker("050500", "よくきたな|n%nよ。")
        lines = m.split("|n")
        self.assertTrue(lines[0].startswith("[050500]"))
        self.assertEqual(font_en.cells(lines[0]), 5)
        self.assertEqual(lines[1][:2], "%n")
        self.assertEqual(font_en.cells(lines[1]), 2)


if __name__ == "__main__":
    unittest.main()

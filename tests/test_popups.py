"""Raw OBJ popups outside the sprite banks (gfx_labels.POPUPS): the stage's 昇段!! level-up popup."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_labels  # noqa: E402
import textbank  # noqa: E402


class TestPopups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()
        cls.edits = gfx_labels.popup_edits(cls.rom)

    def test_record_points_at_the_tiles(self):
        # sprite record 0x74ECB8: +8 palette, +12 tiles, +16 tiles end
        pal, tiles, end = (w - 0x08000000 for w in struct.unpack_from("<3I", self.rom, 0x74ECB8 + 8))
        p = gfx_labels.POPUPS[tiles]
        self.assertEqual(tiles - pal, 32)
        self.assertGreaterEqual(end - tiles, p["w"] * p["h"] // 2)

    def test_same_size_and_palette(self):
        for off, data in self.edits.items():
            p = gfx_labels.POPUPS[off]
            self.assertEqual(len(data), p["w"] * p["h"] // 2)
            old = self.rom[off:off + len(data)]
            used_old = {(b >> s) & 15 for b in old for s in (0, 4)}
            used_new = {(b >> s) & 15 for b in data for s in (0, 4)}
            self.assertLessEqual(used_new, used_old, "new pixels use only the original's indices")
            self.assertNotEqual(data, old)

    def test_writes_allowed(self):
        for off, data in self.edits.items():
            self.assertTrue(any(lo <= off and off + len(data) <= hi for lo, hi in gfx_labels.SMALL_RANGES))


if __name__ == "__main__":
    unittest.main()

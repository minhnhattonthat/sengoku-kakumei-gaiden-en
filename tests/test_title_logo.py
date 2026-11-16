"""English title logo (tools/title_logo.py)."""
import struct
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
import lz77  # noqa: E402
import textbank  # noqa: E402
import title_logo as T  # noqa: E402


class TestTitleLogo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()
        cls.pics = {pic: T.build(cls.rom, pic) for pic in T.PICTURES}
        cls.edits = T.lz_edits(cls.rom)

    def test_map_slot_matches_a_title_dump(self):
        self.assertEqual(T.load_map(self.rom, "title"), T.load_tsv())

    def test_records_point_at_the_blocks(self):
        for pic, p in T.PICTURES.items():
            words = [w - 0x08000000 for w in struct.unpack_from("<5I", self.rom, p["record"])]
            self.assertEqual(words[2:], [p["map"], p["tiles"], p["pal"]], pic)
            self.assertEqual(build.RELOCATABLE_LZ[p["map"]], [p["record"] + 8], pic)
            self.assertEqual(build.RELOCATABLE_LZ[p["tiles"]], [p["record"] + 12], pic)

    def test_edited_tiles_show_once(self):
        for pic, (tiles, data, m, _, _, _) in self.pics.items():
            uses = Counter(e & 0x3FF for e in m.values())
            for t in range(len(tiles) // 32):
                if data[t * 32:t * 32 + 32] != tiles[t * 32:t * 32 + 32]:
                    self.assertEqual(uses[t], 1, f"{pic}: edited tile {t} shows {uses[t]} times")

    def test_only_the_logo_band_changes(self):
        for pic, (tiles, data, m, m2, pals, _) in self.pics.items():
            a = T.render(tiles, m, pals).load()
            b = T.render(data, m2, pals).load()
            moved = {(x, y) for y in range(T.H) for x in range(T.W) if a[x, y] != b[x, y]}
            self.assertTrue(moved, pic)
            self.assertGreaterEqual(min(y for _, y in moved), T.BAND[0] - 8, pic)
            self.assertLess(max(y for _, y in moved), T.BAND[1], pic)
            for cell, e in m2.items():
                self.assertEqual(e & 0x0FFF, m[cell] & 0x0FFF, f"{pic}: only the palette of a map entry changes")

    def test_blocks_round_trip_through_the_build(self):
        new, _ = build.repack(self.rom, build.unpack(self.rom), lz_edits=self.edits)
        for p in T.PICTURES.values():
            for off, site in ((p["tiles"], p["record"] + 12), (p["map"], p["record"] + 8)):
                dest = struct.unpack_from("<I", new, site)[0] - 0x08000000
                self.assertEqual(lz77.decompress(new, dest)[0], self.edits[off], f"{off:06x}")


if __name__ == "__main__":
    unittest.main()

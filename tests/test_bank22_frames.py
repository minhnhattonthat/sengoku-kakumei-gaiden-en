"""Bank 22's 参加受付中 animation: frames 16-18 show their pieces out of tile order, so each drawn label must
read top to bottom once its pieces are assembled as the game does (sprites.frames), the same as frame 15's
"Taking Entries" over the shared letters. The original's frames assemble the same way."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx_labels  # noqa: E402
import sprites  # noqa: E402
import textbank  # noqa: E402


def shown(rows, ps):
    """The cell as on screen: rows top to bottom from each piece's tiles."""
    out = [None] * max(p["y"] + p["h"] for p in ps)
    for p in ps:
        pr = p["tile"] // 2 * 8
        out[p["y"]:p["y"] + p["h"]] = rows[pr:pr + p["h"]]
    return out


class TestBank22Frames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = textbank.original_rom()
        cls.b, cls.rows, cls.new = gfx_labels.english_rows(cls.rom, 22)
        cls.frames = sprites.frames(cls.rom, cls.b)

    def test_pieces_permuted(self):
        ys = [[p["y"] for p in self.frames[f]] for f in (16, 17, 18)]
        self.assertTrue(any(y != sorted(y) for y in ys))

    def test_original_frames_share_prefix(self):
        base = shown(self.rows, self.frames[15])
        for f in (16, 17, 18):
            self.assertEqual(shown(self.rows, self.frames[f])[:80], base[:80], f"original frame {f}")  # 5 kanji

    def test_english_frames_read_in_order(self):
        def ink(rows):  # letter pixels only: a longer label gets a longer gradient box
            return [[v == gfx_labels.INK for v in r] for r in rows]

        base = ink(shown(self.new, self.frames[15]))
        width = gfx_labels.text_width("Taking Entries")
        for f in (16, 17, 18):
            self.assertEqual(ink(shown(self.new, self.frames[f]))[:width], base[:width], f"frame {f}")


if __name__ == "__main__":
    unittest.main()

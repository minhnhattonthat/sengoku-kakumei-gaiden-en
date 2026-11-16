"""Frozen text layout (data/text_layout.tsv): a relocated string keeps the toured build's slot while it fits, so one
text edit moves only that string and leaves the QA tour's coverage logs and sheets valid; letter pairs keep their
codes (font_en.Encoder frozen=)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font_en  # noqa: E402
import textbank  # noqa: E402


def toy():
    rom = bytearray(0x400)
    strs = {}
    for k, a in enumerate((0x100, 0x140, 0x180)):
        rom[a:a + 4] = b"AB\0\0"
        struct.pack_into("<I", rom, 0x10 + 4 * k, 0x08000000 | a)
        strs[a] = textbank.Str(a, b"AB", 4, [0x10 + 4 * k])
    return rom, strs


def dest(rom, k):
    return struct.unpack_from("<I", rom, 0x10 + 4 * k)[0] - 0x08000000


class FrozenLayout(unittest.TestCase):
    def test_edit_moves_only_the_edited_string(self):
        rom, strs = toy()
        base = {0x100: b"FIRST1", 0x140: b"SECOND2", 0x180: b"THIRD3"}
        writes = textbank.repack(rom, dict(base), free=(0x300, 0x400), strs=strs)
        lay = {a: dest(rom, k) for k, a in enumerate(sorted(base))}
        end = max(o + len(d) + 3 & ~3 for o, _, d, w in writes if w.endswith(" moved"))
        layout = (lay, end, None)
        # same text + layout = same placement
        rom2, strs2 = toy()
        textbank.repack(rom2, dict(base), free=(0x300, 0x400), strs=strs2, layout=layout)
        self.assertEqual([dest(rom2, k) for k in range(3)], [lay[a] for a in sorted(base)])
        # the first string grows past its slot: it alone moves to the end; the others keep their slots
        rom3, strs3 = toy()
        textbank.repack(rom3, {**base, 0x100: b"FIRST1-MUCH-LONGER"}, free=(0x300, 0x400), strs=strs3,
                        layout=layout)
        self.assertEqual(dest(rom3, 0), end)
        self.assertEqual([dest(rom3, 1), dest(rom3, 2)], [lay[0x140], lay[0x180]])
        # a shorter edit stays in its slot
        rom4, strs4 = toy()
        textbank.repack(rom4, {**base, 0x140: b"SEC2X"}, free=(0x300, 0x400), strs=strs4, layout=layout)
        self.assertEqual(dest(rom4, 1), lay[0x140])

    def test_frozen_pairs_keep_codes(self):
        old = font_en.Encoder(["Hello there"])
        new = font_en.Encoder(["Hello there", "Zebra"], frozen=old.pairs)
        self.assertEqual(new.pairs[:len(old.pairs)], old.pairs)
        self.assertEqual(new.encode("Hello there"), old.encode("Hello there"))

    def test_layout_file_loads(self):
        lay = textbank.load_layout()
        if lay is None:
            self.skipTest("no data/text_layout.tsv")
        self.assertTrue(lay[0] and lay[1] and lay[2])
        self.assertTrue(all(textbank.FREE[0] <= d < lay[1] for d in lay[0].values()))


if __name__ == "__main__":
    unittest.main()

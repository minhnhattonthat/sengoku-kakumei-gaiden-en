"""Phase 3 identity build: unpack -> repack with no edits is byte-identical, and the writers it relies on work."""
import hashlib
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
HAVE_ROM = any((ROOT / "rom").glob("*.gba"))


@unittest.skipUnless(HAVE_ROM, "no ROM dump in rom/")
class Identity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import build
        import textbank
        cls.build, cls.tb = build, textbank
        cls.orig = textbank.original_rom()
        cls.unpacked = build.unpack(cls.orig)

    def test_identity_build_is_byte_identical(self):
        new, writes = self.build.repack(self.orig, self.unpacked)
        self.assertEqual(hashlib.sha1(new).hexdigest(), hashlib.sha1(self.orig).hexdigest())
        self.assertEqual([w for w in writes if w[1] != w[2]], [])

    def test_text_covers_every_site(self):
        strs = self.tb.strings(self.orig)
        self.assertEqual(len(strs), len(self.unpacked["text"]))
        self.assertEqual(sum(len(s.sites) for s in strs.values()), len(self.tb.load_sites()))
        self.assertGreater(len(strs), 1000)

    def test_sites_match_a_fresh_scan(self):
        import textmap
        self.assertEqual(textmap.render(textmap.scan(self.orig)), self.tb.SITES.read_text(encoding="utf-8"))

    def test_every_string_relocated_still_reads_the_same(self):
        out = bytearray(self.orig)
        strs = self.tb.strings(self.orig)
        writes = self.tb.repack(out, {a: s.raw for a, s in strs.items()}, strs=strs, force_move=True)
        for a, s in strs.items():
            for site in s.sites:
                dest = struct.unpack_from("<I", out, site)[0] - 0x08000000
                self.assertTrue(self.tb.FREE[0] <= dest < self.tb.FREE[1], f"{site:06x}")
                self.assertEqual(bytes(out[dest:dest + len(s.raw) + 1]), s.raw + b"\0", f"{a:06x}")
            self.assertEqual(bytes(out[a:a + s.room]), bytes(s.room), f"old slot {a:06x} not cleared")
        stray = [w for w in writes if not self.build.allowed_write(w[0], len(w[2]))]
        self.assertEqual(stray, [])

    def test_edit_in_place_and_moved(self):
        strs = self.tb.strings(self.orig)
        a = next(a for a, s in strs.items() if s.room >= 8 and s.bank == "story")
        out = bytearray(self.orig)
        self.tb.repack(out, {a: b"Hi"}, strs=strs)
        self.assertEqual(bytes(out[a:a + 3]), b"Hi\0")
        self.assertEqual([i for i in range(len(out)) if out[i] != self.orig[i] and not a <= i < a + strs[a].room], [])
        long = b"x" * (strs[a].room + 10)
        out = bytearray(self.orig)
        self.tb.repack(out, {a: long}, strs=strs)
        dest = struct.unpack_from("<I", out, strs[a].sites[0])[0] - 0x08000000
        self.assertEqual(dest, self.tb.FREE[0])
        self.assertEqual(bytes(out[dest:dest + len(long) + 1]), long + b"\0")

    def test_lz_blocks_decode_and_recompress(self):
        import lz77
        blocks = self.build.lz_blocks()
        self.assertEqual(len(blocks), len(self.unpacked["lz"]))
        self.assertGreater(len(blocks), 600)
        for off, end, size in blocks:
            data = self.unpacked["lz"][off]
            self.assertEqual(len(data), size)
            blob = lz77.compress(data)
            self.assertEqual(lz77.decompress(blob)[0], data, f"{off:06x}")
            self.assertLessEqual(len(blob), ((end + 3) & ~3) - off + 64, f"{off:06x} recompressed much larger")

    def test_lz_edit_is_written_and_decodes(self):
        off, end, size = self.build.lz_blocks()[0]
        data = bytearray(self.unpacked["lz"][off])
        data[0] ^= 0xFF
        new, writes = self.build.repack(self.orig, self.unpacked, lz_edits={off: bytes(data)})
        self.assertEqual(self.build.lz77.decompress(new, off)[0], bytes(data))


if __name__ == "__main__":
    unittest.main()

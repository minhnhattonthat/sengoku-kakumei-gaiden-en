"""The manga-bubble variant (D16): layout limits for every scroll page, the stored engine code, and a full build in
memory checked by build.verify (allowed ranges + romdiff)."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import manga  # noqa: E402
import manga_engine  # noqa: E402
import script  # noqa: E402

try:
    import build  # noqa: E402
    import textbank  # noqa: E402
    ORIG = textbank.original_rom()
except (FileNotFoundError, OSError):
    ORIG = None

# Original bytes at the hook sites (this revision of the game).
HOOK_ORIG = {manga_engine.HOOK_ADV: "10b5041c1b041b0c0c32101c", manga_engine.HOOK_NL: "01229144149b9e42",
             manga_engine.HOOK_END: "139b012b03d10a48"}


def scroll_pages():
    return [(b, e) for b, es in script.load().items() if b not in manga.MANGA_BANKS_SKIP for e in es if e.get("en")]


class Layout(unittest.TestCase):
    def test_every_page_fits(self):
        bad = [f"{b} {e['id']}: {manga.problems(e['en'])}" for b, e in scroll_pages() if manga.problems(e["en"])]
        self.assertEqual(bad, [])

    def test_slices_within_glyph(self):
        enc = manga.Encoder(e["en"] for _, e in scroll_pages())
        for s in enc.slices:
            self.assertLessEqual(manga.ink_width(s), manga.SLICE, s)
            self.assertTrue(all(v & 0xFFFF == v for v in manga.glyph_rows(s)))

    def test_encoding_bytes(self):
        """Slice codes never collide with NUL, the reader's controls or the v1 pair / EUC codes."""
        enc = manga.Encoder(e["en"] for _, e in scroll_pages())
        for _, e in scroll_pages():
            b = enc.encode(e["en"])
            k = 0
            while k < len(b):
                if b[k] in (0x25, 0x7C):
                    self.assertIn(b[k:k + 2], (b"%n", b"%b", b"%B", b"%r", b"|n"), e["id"])
                else:
                    self.assertTrue(manga.CODE_B0[0] <= b[k] < manga.CODE_B0[1] and b[k + 1] != 0, e["id"])
                k += 2

    def test_controls_kept(self):
        t = "%b%n%B, OK?|n%rA: Select  B: Back|n"
        out = manga.Encoder([t]).encode(t)
        self.assertTrue(out.startswith(b"%b%n%B"))
        self.assertIn(b"%r", out)

    def test_wrap_breaks_at_hyphen(self):
        self.assertEqual(manga.wrap("TOYOTOMI-DONO'S"), ["TOYOTOMI-", "DONO'S"])
        self.assertEqual(manga.wrap("GRANDFATHER'S"), ["GRAND-", "FATHER'S"])


class Code(unittest.TestCase):
    def test_code_bin_current(self):
        try:
            import keystone  # noqa: F401
        except ImportError:
            self.skipTest("keystone not installed")
        self.assertEqual(manga_engine.assemble(), manga_engine.stored_code(),
                         "data/manga_code.hex is stale: run tools/manga_engine.py --write")

    def test_entries_are_branches(self):
        code, _ = manga_engine.handlers()
        for off in manga_engine.ENTRIES.values():
            self.assertEqual(struct.unpack_from("<H", code, off)[0] >> 11, 0b11100, off)   # thumb B


@unittest.skipIf(ORIG is None, "needs the original ROM")
class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.new, cls.writes, cls.enc = build.make_manga(ORIG, script.load_en())

    def test_hook_sites_original(self):
        for off, hexs in HOOK_ORIG.items():
            self.assertEqual(ORIG[off:off + len(hexs) // 2].hex(), hexs, f"{off:06x}")
        self.assertEqual(set(ORIG[manga_engine.CODE_AT:0x800000]), {0xFF})

    def test_verified(self):
        build.verify(ORIG, self.new, self.writes)

    def test_hooks_jump_to_entries(self):
        self.assertEqual(struct.unpack_from("<I", self.new, manga_engine.HOOK_ADV + 8)[0],
                         0x08000000 | manga_engine.CODE_AT | 1)
        for off, entry in ((manga_engine.HOOK_NL, "newline"), (manga_engine.HOOK_END, "endstr")):
            self.assertEqual(struct.unpack_from("<I", self.new, off + 4)[0],
                             0x08000000 | (manga_engine.CODE_AT + manga_engine.ENTRIES[entry]) | 1)

    def test_slice_entries(self):
        """Each slice code finds its entry through MANGA_BASE, and the entry carries the slice's advance."""
        base = struct.unpack_from("<I", self.new, manga_engine.PARAMS_AT)[0]
        for k in (0, len(self.enc.slices) // 2, len(self.enc.slices) - 1):
            b0, b1 = manga.code(k)
            idx = base + (b0 - 1) * 255 + (b1 - 1)
            e = 0x7E0100 + idx * 32
            self.assertEqual(self.new[e + 2:e + 4], bytes((b0, b1)))
            self.assertEqual(struct.unpack_from("<H", self.new, e + 4)[0], manga.run_width(self.enc.slices[k]))
        end = 0x7E0100 + (base + len(self.enc.slices)) * 32
        self.assertLessEqual(end, manga_engine.CODE_AT)


if __name__ == "__main__":
    unittest.main()

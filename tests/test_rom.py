"""The supported dump is pinned in rom.sha1 and the build refuses anything else."""
import unittest
from pathlib import Path

import check_rom

ROOT = Path(__file__).resolve().parents[1]


class RomPin(unittest.TestCase):
    def test_sha1_listing_is_filled_in(self):
        text = (ROOT / "rom.sha1").read_text(encoding="utf-8")
        self.assertNotIn("<sha1>", text)

    @unittest.skipUnless(any((ROOT / "rom").glob("*.gba")), "no ROM dump in rom/")
    def test_dump_matches(self):
        check_rom.check()  # sys.exit on mismatch


if __name__ == "__main__":
    unittest.main()

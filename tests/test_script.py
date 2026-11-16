"""Phase 4 extract: script/*.json holds every pointed string exactly once, its jp re-encodes to the original bytes,
the text ranges are fully covered, and the build's loader path is byte-exact."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
HAVE_ROM = any((ROOT / "rom").glob("*.gba"))

import script  # noqa: E402

KINDS = {"text", "debug", "code", "dup"}


class ScriptFiles(unittest.TestCase):
    """Checks that need no ROM."""

    @classmethod
    def setUpClass(cls):
        cls.banks = script.load()
        cls.entries = [e for es in cls.banks.values() for e in es]
        cls.by_id = {e["id"]: e for e in cls.entries}
        cls.jp = script.table()

    def test_ids_unique_and_fields_present(self):
        self.assertEqual(len(self.by_id), len(self.entries))
        for e in self.entries:
            for k in ("id", "sites", "room", "kind", "jp", "en", "notes", "status"):
                self.assertIn(k, e, e["id"])
            self.assertIn(e["kind"], KINDS, e["id"])

    def test_dups_point_at_text(self):
        for e in self.entries:
            if e["kind"] == "dup":
                src = self.by_id[e["same_as"]]
                self.assertEqual(src["jp"], e["jp"], e["id"])
                self.assertEqual(src["kind"], "text", e["id"])

    def test_jp_roundtrips_through_the_table(self):
        for e in self.entries:
            raw = script.encode(self.jp, e["jp"])
            self.assertEqual(script.decode(self.jp, raw), e["jp"], e["id"])

    def test_en_encodes(self):
        for e in self.entries:
            if e["en"]:
                script.encode(self.jp, e["en"])


@unittest.skipUnless(HAVE_ROM, "no ROM dump in rom/")
class ScriptMatchesRom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import textbank
        cls.tb = textbank
        cls.orig = textbank.original_rom()
        cls.strs = textbank.strings(cls.orig)
        cls.banks = script.load()
        cls.jp = script.table()

    def test_every_string_once_with_original_bytes(self):
        seen = {}
        for bank, entries in self.banks.items():
            for e in entries:
                addr = int(e["id"], 16)
                self.assertEqual(self.tb.bank_of(addr), bank, e["id"])
                s = self.strs[addr]
                self.assertEqual(script.encode(self.jp, e["jp"]), s.raw, e["id"])
                self.assertEqual(e["sites"], [f"{x:06x}" for x in sorted(s.sites)], e["id"])
                self.assertEqual(e["room"], s.room, e["id"])
                seen[addr] = e
        self.assertEqual(set(seen), set(self.strs))

    def test_fresh_dump_matches_files(self):
        fresh = script.fresh(self.orig)
        for bank, entries in fresh.items():
            keep = ("en", "notes", "status")
            strip = lambda es: [{k: v for k, v in e.items() if k not in keep} for e in es]  # noqa: E731
            self.assertEqual(strip(entries), strip(self.banks[bank]), f"{bank}: run tools/script.py update")

    def test_ranges_fully_covered(self):
        cov = bytearray(len(self.orig))
        for a, s in self.strs.items():
            cov[a:a + s.room] = b"\1" * s.room
        for name, lo, hi in self.tb.RANGES:
            stray = [i for i in range(lo, hi) if not cov[i] and self.orig[i]]
            self.assertEqual(stray[:5], [], f"{name}: non-zero bytes no string covers")

    def test_loader_path_is_byte_exact(self):
        import build
        edits = {int(e["id"], 16): e["jp"] + script.END for es in self.banks.values() for e in es}
        new, writes = build.repack(self.orig, build.unpack(self.orig), text_edits=edits)
        self.assertEqual(new, self.orig)

    def test_load_en_uses_dup_source(self):
        banks = {b: [dict(e) for e in es] for b, es in self.banks.items()}
        src = banks["menu_help1"][0]
        src["en"] = "Overwrite which record?"
        edits = script.load_en(banks)
        dup = next(e for e in banks["menu_help2"] if e.get("same_as") == src["id"])
        self.assertEqual(edits[int(src["id"], 16)], src["en"])
        self.assertEqual(edits[int(dup["id"], 16)], src["en"])


if __name__ == "__main__":
    unittest.main()

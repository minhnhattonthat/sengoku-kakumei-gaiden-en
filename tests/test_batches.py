"""Phase 6 text lint: the batch tool's own selftest, and every shipped English line passes its checks
(control codes, ASCII, glossary, 24-letter x 3-line scroll budget, results budgets)."""
import contextlib
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import batches  # noqa: E402


class Batches(unittest.TestCase):
    def test_selftest(self):
        saved = (batches.ROOT, batches.TL, batches.SCRIPT, batches.GLOSSARY)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                batches._selftest()
        finally:
            batches.ROOT, batches.TL, batches.SCRIPT, batches.GLOSSARY = saved

    def test_honorifics(self):
        terms = batches.glossary()
        e = {"id": "x", "jp": "あの…|n%n様|nではありませんか？"}
        self.assertTrue(batches.honorific_problems(e["jp"], "Um... Aren't you|n%n?", terms))
        self.assertFalse(batches.honorific_problems(e["jp"], "Um... Aren't you|n%n-sama?", terms))
        self.assertTrue(batches.honorific_problems("豊臣殿の方は", "the Toyotomi matter", terms))
        self.assertTrue(batches.honorific_problems("幸村（ゆきむら）様", "Yukimura", terms))
        for plain in ("貴様を倒す", "お兄様", "若殿", "殿下…", "殿！", "毛利領の様子は"):
            self.assertFalse(batches.honorific_problems(plain, "x", terms), plain)

    def test_stub_last_line(self):
        e = {"id": "x", "jp": ""}
        self.assertTrue(batches.stub_problem(e, "Save your progress so|nfar."))
        self.assertFalse(batches.stub_problem(e, "Save your|nprogress so far."))
        self.assertFalse(batches.stub_problem(e, "...|n...|n...!"))  # punctuation only: intended
        self.assertEqual(batches.wrap(e, "Save your progress so far."), "Save your|nprogress so far.")

    def test_shipped_english(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = batches.main(["check"])
        self.assertEqual(code, 0, out.getvalue()[:3000])


if __name__ == "__main__":
    unittest.main()

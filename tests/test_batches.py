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

    def test_shipped_english(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = batches.main(["check"])
        self.assertEqual(code, 0, out.getvalue()[:3000])


if __name__ == "__main__":
    unittest.main()

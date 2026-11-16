"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it.

Runs every test under tests/ with unittest discovery (stdlib only, so a clone needs nothing extra).
Tests needing the ROM skip themselves when rom/ is absent. Exit code = pass/fail.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.path.insert(0, str(ROOT / "tools"))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    if suite.countTestCases() == 0:
        print("check: no tests found")
        return 1
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

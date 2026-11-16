"""release.py: build, run every gate, then make and verify the BPS patch and the release zip.

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-smoke] [--variant manga]

--variant manga (D16) runs the same gates on `build.py manga` (build/sengoku_manga.gba): its own tour manifest
work/qa/manga/manifest.tsv plus the story pass, coverage work/qa/manga/cover, and release/..._EN_Manga_v<version>.

Stops at the first failure (references/pipeline.md §Release), in this order:
  1. build.py (build/sengoku_en.gba)            2. tools/check.py (tests + text lint)
  3. emu.py --smoke on the build                4. jp_left.py: no Japanese a pointer still reaches
  5. qa_gate.py check on every work/qa/**/manifest.tsv (visual tour, story pass), verdicts in the sibling verdicts/
  6. textcover.py on work/qa/cover               7. no unticked line in docs/polish.md
  8. no template placeholder in README.md        9. debug off: the release build is the plain `build.py build`
     (no marker/STRESS/ID overrides) and the cartridge header/boot code equals the original's
 10. BPS patch (bps.py make re-applies it), then an independent re-apply to a clean original + byte compare
 11. release/Sengoku_Kakumei_Gaiden_EN_v<version>.zip = .bps + README.txt (with base and patched hashes)
Refuses to overwrite an existing version's files without --force. --help never builds. Publishing is the owner's call.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL as _SKILL  # noqa: E402

SKILL = Path(_SKILL)

ORIG = ROOT / "rom/Sengoku Kakumei Gaiden (Japan).gba"
PY = [sys.executable, "-X", "utf8"]
READING = {
    "en": """READING THE TEXT
The game draws all its text in vertical columns. The English is drawn rotated 90 degrees clockwise in those same
columns: tilt your head (or your screen) to the right. Columns run right to left, i.e. lines top to bottom.
A second patch (Manga edition) shows the dialogue upright instead.""",
    "manga": """READING THE TEXT (MANGA EDITION)
This edition letters the dialogue like a manga's vertical speech bubble: upright capitals in short centred lines
stacked down the game's tall scroll, read top to bottom with no head tilt. Menu labels, item names, the results
screen and other text drawn as graphics are the same as in the standard patch (drawn sideways: tilt your head to
the right). The standard patch draws all text sideways in the original columns.""",
}
VARIANTS = {
    "en": {"build": ["build.py"], "rom": "build/sengoku_en.gba", "name": "Sengoku_Kakumei_Gaiden_EN",
           "cover": "work/qa/cover", "strings": "build/strings.tsv", "title": ""},
    "manga": {"build": ["build.py", "manga"], "rom": "build/sengoku_manga.gba",
              "name": "Sengoku_Kakumei_Gaiden_EN_Manga", "cover": "work/qa/manga/cover",
              "strings": "build/strings_manga.tsv", "title": " (Manga edition)"},
}


def manifests_for(variant):
    """The tour manifests that judge this variant's build, plus the story pass (text, both variants)."""
    found = sorted((ROOT / "work/qa").rglob("manifest.tsv"))
    manga_dir = ROOT / "work/qa/manga"
    story = [m for m in found if m.parent.name == "story"]
    if variant == "manga":
        return story + [m for m in found if m.parent == manga_dir]
    return [m for m in found if manga_dir not in m.parents and m.parent != manga_dir]


def run(step, cmd):
    print(f"== {step}: {' '.join(str(c) for c in cmd)}", flush=True)
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"FAILED at {step} (exit {r.returncode})")


def fail(step, why):
    sys.exit(f"FAILED at {step}: {why}")


def hashes(data):
    return {"size": len(data), "crc32": f"{zlib.crc32(data):08X}", "md5": hashlib.md5(data).hexdigest(),
            "sha1": hashlib.sha1(data).hexdigest()}


README = """Sengoku Kakumei Gaiden - English translation patch v{version}{title}
================================================================

Unofficial English fan translation of Sengoku Kakumei Gaiden (Game Boy Advance, Konami, 2002).
Source, tools and bug reports: https://github.com/minhnhattonthat/sengoku-kakumei-gaiden-en

HOW TO PATCH
Apply {patch} to your own dump of the Japanese cartridge with any BPS patcher
(Floating IPS / flips, beat, or https://www.marcrobledo.com/RomPatcher.js/).

Base ROM (No-Intro: Sengoku Kakumei Gaiden (Japan).gba)
  Size   {o[size]} bytes
  CRC32  {o[crc32]}
  MD5    {o[md5]}
  SHA-1  {o[sha1]}
Patched ROM
  CRC32  {p[crc32]}
  SHA-1  {p[sha1]}
The patcher refuses any other dump (a different revision, a header, an already-patched copy).

{reading}

WHAT IS TRANSLATED
Dialogue, story events, biographies, tutorial, menus, item and art descriptions, shops, saving, link-cable setup,
battle results and titles; menu labels, item names, stat block, HUD, map plates and the other text drawn as
graphics; the title logo; the ending cards and staff credits; the name entry (Latin letters).
Left in Japanese: the family crests and banner mottos in the biography portraits (heraldry, not captions).

NOTES
- Tested in Mesen 2.2.1 (GBA) with the official BIOS. Start a new game from a cold boot; savestates made with
  the Japanese ROM carry its old text and graphics. In-game saves are compatible.
- Link-cable play was tested only in an emulator, not with two consoles.
- Known issues: none known. Please report bugs (with a savestate if you can) at the GitHub page above.

CREDITS
Translation, hacking and QA: minhnhattonthat, with extensive AI assistance (Claude by Anthropic; OpenAI Codex as
an independent reviewer). Sengoku Kakumei Gaiden is (c) Konami; this project is not affiliated with them.
This is an unofficial patch. No ROMs are provided; do not share patched ROMs.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    ap.add_argument("--skip-smoke", action="store_true", help="only when the emulator cannot run here (not a release)")
    ap.add_argument("--variant", choices=sorted(VARIANTS), default="en", help="manga = the D16 bubble edition")
    a = ap.parse_args()
    v = VARIANTS[a.variant]
    built_path = ROOT / v["rom"]

    out_dir = ROOT / "release"
    patch = out_dir / f"{v['name']}_v{a.version}.bps"
    zpath = out_dir / f"{v['name']}_v{a.version}.zip"
    if not a.force and (patch.exists() or zpath.exists()):
        fail("start", f"{patch.name} or {zpath.name} already exists (use --force or a new --version)")

    run("build", PY + v["build"])
    run("check", PY + ["tools/check.py"])
    if not a.skip_smoke:
        run("smoke", PY + [SKILL / "scripts/emu.py", built_path, "--out", ROOT / f"work/qa/smoke_{a.variant}",
                           "--route", ROOT / "tools/routes/boot.txt", "--smoke"])
    run("jp_left", PY + [SKILL / "scripts/jp_left.py", built_path, "--tbl", "tbl/jp.tbl", "--gba-ptrs",
                         "--known", "data/jp_known.txt"])
    manifests = manifests_for(a.variant)
    if not any(m.parent.name == "story" for m in manifests):
        fail("qa_gate", "no story-pass manifest (work/qa/story/manifest.tsv)")
    if len(manifests) < 2:
        fail("qa_gate", f"no visual-tour manifest for the {a.variant} build")
    for m in manifests:
        run(f"qa_gate {m.relative_to(ROOT)}", PY + [SKILL / "scripts/qa_gate.py", "check", m, m.parent / "verdicts"])
    run("textcover", PY + [SKILL / "scripts/textcover.py", v["cover"], v["strings"],
                           "--waive", "docs/text_unshown.tsv", "--mask", "0x7FFFFF"])

    open_lines = [ln for ln in (ROOT / "docs/polish.md").read_text(encoding="utf-8").splitlines()
                  if ln.lstrip().startswith("- [ ]")]
    if open_lines:
        fail("polish", f"{len(open_lines)} unticked line(s) in docs/polish.md, first: {open_lines[0]}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    ph = re.findall(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|game|ext|[A-Z][a-z]+ [^>]*)>", readme)
    if ph:
        fail("readme", f"template placeholder(s) left in README.md: {sorted(set(ph))}")

    orig, built = ORIG.read_bytes(), built_path.read_bytes()
    # Debug off: the game's leftover debug menu (mode 0) is reached only through the warp tool's Lua; the release
    # build must not change the header or the boot code that picks the first mode.
    if built[:0x200] != orig[:0x200]:
        fail("debug-off", "header/boot code 0x000-0x1FF differs from the original")
    for marker in (b"[05", b"[07", b"TORTURE"):
        if re.search(re.escape(marker) + rb"[0-9a-f]{3,4}\]" if marker.startswith(b"[") else re.escape(marker), built):
            fail("debug-off", f"marker-build text {marker!r} found: rebuild with plain `build.py`")

    out_dir.mkdir(exist_ok=True)
    run("bps make", PY + ["tools/bps.py", "make", ORIG, built_path, patch])
    check_out = ROOT / "build/release_check.gba"
    run("bps apply", PY + ["tools/bps.py", "apply", ORIG, patch, check_out])
    if check_out.read_bytes() != built:
        fail("verify", f"re-applied patch differs from {v['rom']}")
    check_out.unlink()

    o, p = hashes(orig), hashes(built)
    text = README.format(version=a.version, patch=patch.name, o=o, p=p, title=v["title"], reading=READING[a.variant])
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.writestr("README.txt", text.replace("\n", "\r\n"))
    print(f"OK {zpath.relative_to(ROOT)}: {patch.name} ({patch.stat().st_size} bytes) + README.txt; "
          f"patched CRC32 {p['crc32']} sha1 {p['sha1']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

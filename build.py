"""build.py: the one entry point for building the ROM.

    python -X utf8 build.py            build/sengoku_en.gba + build/writes.log from script/*.json (tools/script.py),
                                       checked by romdiff
    python -X utf8 build.py identity   unpack every string and LZ77 block, repack with no edits, require the
                                       result to be byte-identical to the original (build/identity.gba)

The dump is checked against rom.sha1 first. Text goes through tools/textbank.py (in place, or relocated to free
space with its pointers rewritten); LZ77 blocks that are not edited keep their original bytes.
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import engine  # noqa: E402
import font_en  # noqa: E402
import gfx_labels  # noqa: E402
import sprites  # noqa: E402
import lz77  # noqa: E402
import name_grid  # noqa: E402
import romdiff  # noqa: E402
import script  # noqa: E402
import textbank  # noqa: E402
from tbl import Table  # noqa: E402

BUILD = ROOT / "build"
LZ_BLOCKS = ROOT / "data" / "lz_blocks.tsv"


def lz_blocks():
    rows = []
    for line in LZ_BLOCKS.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            off, end, size = line.split("\t")
            rows.append((int(off, 16), int(end, 16), int(size)))
    return rows


def unpack(rom):
    """Everything the build can edit, decoded: {"text": {addr: str}, "lz": {offset: bytes}}."""
    jp = Table.load(ROOT / "tbl" / "jp.tbl")
    text = {a: jp.decode(s.raw + b"\0", 0)[0] for a, s in textbank.strings(rom).items()}
    lz = {off: lz77.decompress(rom, off)[0] for off, _, _ in lz_blocks()}
    return {"text": text, "lz": lz, "table": jp}


def repack(rom, unpacked, text_edits=None, lz_edits=None, raw_edits=None):
    """Return (new rom, writes). Unedited text is re-encoded from its decoded form; unedited LZ blocks are kept.
    text_edits are jp-table strings (with {end}); raw_edits are already-encoded bytes without the NUL (English)."""
    out = bytearray(rom)
    jp = unpacked["table"]
    new = {}
    for addr, txt in unpacked["text"].items():
        if raw_edits and addr in raw_edits:
            new[addr] = raw_edits[addr]
            continue
        enc = jp.encode((text_edits or {}).get(addr, txt))
        if not enc.endswith(b"\0"):
            raise ValueError(f"{addr:06x}: encoded text lacks {{end}}")
        new[addr] = enc[:-1]
    writes = textbank.repack(out, new)
    for off, data in (lz_edits or {}).items():
        end = dict((o, e) for o, e, _ in lz_blocks())[off]
        blob = lz77.compress(data)
        if len(blob) > ((end + 3) & ~3) - off:
            raise ValueError(f"LZ block {off:06x} grew past its slot; relocation not written yet")
        writes.append((off, bytes(out[off:off + len(blob)]), blob, f"lz {off:06x}"))
        out[off:off + len(blob)] = blob
    return bytes(out), writes


def allowed_write(off, n):
    sites = getattr(allowed_write, "sites", None)
    if sites is None:
        sites = allowed_write.sites = {s for s, _ in textbank.load_sites()}
    if off in sites and n == 4:
        return True
    if engine.allowed(off, n):
        return True
    end = off + n
    if textbank.FREE[0] <= off and end <= textbank.FREE[1]:
        return True
    if any(lo <= off and end <= hi for _, lo, hi in textbank.RANGES):
        return True
    if not hasattr(allowed_write, "banks"):
        allowed_write.banks = [(b["tiles"], b["end"]) for b in sprites.banks(textbank.original_rom())]
    if any(lo <= off and end <= hi for lo, hi in allowed_write.banks):
        return True  # sprite-bank tiles (label graphics), sizes unchanged
    if any(lo <= off and end <= hi for lo, hi in gfx_labels.SMALL_RANGES):
        return True  # 8x8 small-font glyphs (stat digits)
    return any(o <= off and end <= ((e + 3) & ~3) for o, e, _ in lz_blocks())


def verify(orig, new, writes):
    """Raise SystemExit on a write outside the allowed ranges or a romdiff error (tests call this too)."""
    stray = [w for w in writes if not allowed_write(w[0], len(w[2]))]
    if stray:
        raise SystemExit("writes outside text ranges, sites, LZ blocks and free space:\n" +
                         "\n".join(f"  {o:06x} {who}" for o, _, _, who in stray[:20]))
    errs, _ = romdiff.check(orig, new, set(), [w for w in writes if w[1] != w[2]])
    if errs:
        raise SystemExit("romdiff:\n  " + "\n  ".join(errs[:30]))


def finish(orig, new, writes, path):
    verify(orig, new, writes)
    BUILD.mkdir(exist_ok=True)
    path.write_bytes(new)
    textbank.write_log(BUILD / "writes.log", writes)
    print(f"{path.relative_to(ROOT)}  sha1 {hashlib.sha1(new).hexdigest()}  "
          f"{sum(w[1] != w[2] for w in writes)} writes")


def identity():
    check_rom.check()
    orig = textbank.original_rom()
    new, writes = repack(orig, unpack(orig))
    finish(orig, new, writes, BUILD / "identity.gba")
    if new != orig:
        raise SystemExit("identity build differs from the original")
    print("identity build is byte-identical to the original")


def make_english(orig, edits):
    """(new rom, writes, encoder) for {addr: English text} through the English engine (tools/font_en.py,
    tools/engine.py); encoder is None with no edits."""
    if not edits:
        new, writes = repack(orig, unpack(orig))
        return new, writes, None
    enc = font_en.Encoder(edits.values())
    new, writes = repack(orig, unpack(orig), raw_edits={a: enc.encode(t) for a, t in edits.items()},
                         lz_edits=name_grid.lz_edits(orig))  # Latin name-entry grid (tools/name_grid.py)
    out = bytearray(new)
    writes += engine.patch(out, enc, name_grid.glyph_overrides(orig))
    for off, data in gfx_labels.labels_edits(orig).items():  # OBJ label graphics, gfx/bank*.tsv
        writes.append((off, bytes(out[off:off + len(data)]), data, f"gfx {off:06x}"))
        out[off:off + len(data)] = data
    return bytes(out), writes, enc


def english(orig, edits, path):
    new, writes, enc = make_english(orig, edits)
    if enc:
        print(f"{len(edits)} English strings, {len(enc.pairs)} letter pairs")
    finish(orig, new, writes, path)
    write_strings(orig, new)


def write_strings(orig, new):
    """build/strings.tsv for textcover.py: id (= script id) <TAB> the ROM offset the game reads the string's first
    byte from in this build (its first pointer site), for every `text` and `dup` entry."""
    kinds = {e["id"]: e["kind"] for entries in script.load().values() for e in entries}
    rows = []
    for addr, s in sorted(textbank.strings(orig).items()):
        if kinds.get(f"{addr:06x}") in ("text", "dup"):
            ptr = int.from_bytes(new[s.sites[0]:s.sites[0] + 4], "little") - 0x08000000
            rows.append(f"{addr:06x}\t{ptr:x}\n")
    (BUILD / "strings.tsv").write_text("".join(rows), encoding="utf-8")


def build():
    check_rom.check()
    orig = textbank.original_rom()
    # Every script/ entry with an en text (or a dup whose source has one); untranslated entries keep the Japanese.
    english(orig, script.load_en(), BUILD / "sengoku_en.gba")


def marker():
    """Every text/dup entry replaced by its marker (tools/marker.py): the phase-5 marker build.
    STRESS=1 -> build/sengoku_stress.gba (width-gate rulers)."""
    check_rom.check()
    orig = textbank.original_rom()
    name = "sengoku_stress.gba" if "STRESS=1" in sys.argv else "sengoku_marker.gba"
    english(orig, marker_texts(), BUILD / name)


def marker_texts():
    import marker as mk
    return mk.texts(script.load(), qa=dict(a.split("=", 1) for a in sys.argv[2:] if "=" in a))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    {"build": build, "identity": identity, "marker": marker}[cmd]()


if __name__ == "__main__":
    main()

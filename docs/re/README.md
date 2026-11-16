# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [text.md](text.md) | EUC-JP encoding, `|n`/`%n` codes, vertical draw path, 990-glyph font at 0x712128, pointer tables, text ranges, free space | encoding, font, draw path verified; table grouping guessed |
| [compression.md](compression.md) | BIOS LZ77 wrapper 0x08048964, block list (`tools/re_lzsweep.py`) | verified |
| [graphics.md](graphics.md) | graphics-text survey: tour screens + static sweep of raw and LZ77 graphics | first pass (phase 1); re-check on the marker tour |
| [rom-map.md](rom-map.md) | coarse map of the 8 MiB ROM | guess per region, from renders |
| [sprites.md](sprites.md) | 62 sprite banks at 0x7585D0 (all OBJ label graphics), label redraw pipeline | table layout and bank 22 verified in game; cell tables not decoded |
| [name-entry.md](name-entry.md) | name-entry BG picture (LZ 0x5AEA30), kana table 0x733660, name storage, Latin grid (`tools/name_grid.py`) | verified in game |
| [build.md](build.md) | identity build: text sites, in-place/relocating text writer, LZ77 codec, write checks | verified (`tests/test_identity.py`) |

Recon helpers (rerun any time): `tools/re_eucscan.py ROM OUT.tsv` (EUC candidates), `tools/re_eucptrs.py ROM euc.tsv OUT.tsv` (pointer targets), `tools/re_eucblocks.py ROM pointed.tsv` (text blocks, pointer-site runs), `tools/re_lzsweep.py ROM DIR` (every LZ77 block), `tools/re_tilesheet.py` (survey sheets), `tools/lua/lzlog.lua` (LZ77 blocks loaded at run time).

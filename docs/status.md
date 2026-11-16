# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next (phase 1 recon done). Last build: none yet.
- **Done:**
  - Step 0 setup: MesenCE 2.2.1 + GBA BIOS in `tools/mesen/`; original ROM smoke-boots; rom.sha1 pinned; `tools/check.py` + pre-commit hook; guard hook in `.claude/settings.json`.
  - Phase 1 recon (`docs/re/`): no earlier English patch (only Chinese ones). Text is **EUC-JP**, uncompressed, `|n` newline, `%n` name; about 1000 pointed strings / 36 KB in 8 ranges (`text.md`). **Vertical text** drawn one OBJ per character, 12 px pitch; font 990 glyphs at 0x712128 found by linear search (no Latin lowercase). Pointers in event tables 0x7303B8-0x746CE8 + code pools. LZ77 only (wrapper 0x08048964, 615 blocks). Free-space candidate 0x759178-0x7FFFFF (667 KB). Graphics-text survey (`graphics.md`): tour of boot -> name entry + static sweep of raw and LZ graphics reviewed by codex.
- **Next:** Phase 2 debug tool: scene list + warp (`tools/debug/`). Must reach: field/HUD, status, shop, equipment, biographies, save, results screen, each chapter, the prose-graphics screens (LZ 0x5C3598..0x5CA354), game over, ending, credits, link mode, minigame. Find the scene/flag variables (event handler table near 0x730800; scene ids). Note: the opening dialogue loops when A is mashed (a choice repeats): a route needs a different answer there.
- **Phase 5 heads-up:** English needs horizontal text (the message scroll is a 40 px-wide vertical column) and a new font; Latin fonts exist at 0x1FC000 and 0x710000. Menu help strings exist twice (0x4CE4C and 0x4FDF0): translate both.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked by hand (headless worker); default key mappings are written by emu.py. Not blocking.

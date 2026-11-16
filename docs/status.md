# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress (warp tool built; full verification run still to do). Last build: none yet.
- **Done:**
  - Step 0 setup: MesenCE 2.2.1 + GBA BIOS in `tools/mesen/`; original ROM smoke-boots; rom.sha1 pinned; `tools/check.py` + pre-commit hook; guard hook in `.claude/settings.json`.
  - Phase 1 recon (`docs/re/`): no earlier English patch (only Chinese ones). Text is **EUC-JP**, uncompressed, `|n` newline, `%n` name; about 1000 pointed strings / 36 KB in 8 ranges (`text.md`). **Vertical text** drawn one OBJ per character, 12 px pitch; font 990 glyphs at 0x712128 found by linear search (no Latin lowercase). Pointers in event tables 0x7303B8-0x746CE8 + code pools. LZ77 only (wrapper 0x08048964, 615 blocks). Free-space candidate 0x759178-0x7FFFFF (667 KB). Graphics-text survey (`graphics.md`).
  - Phase 2 RE (`docs/re/scenes.md`): game modes (G=[0x03000000], table 0x7301F0), state struct S=0x02000614 (story flags S+0x164, country nibbles S+0x128, event id S+0x184, map hero position S+0x19C/0x1A0), map node table 0x5E7A0, all 117 event ids labelled, leftover debug menu = mode 0. The "opening loop" was A re-entering Satsuma on the national map.
  - Phase 2 tool: `tools/debug/warp.lua` + `warp.py` + `scenes.txt` (~140 scenes: title side, link mode, map menu screens, stages per region + tutorial + Mugen, results, game over, ending prose/credits/end card, every event incl. biographies and bosses). Proven by single runs this session: map, map menu, Higo barrier, path Higo→Satsuma→deploy confirm, stages in every region (mode 29), every event 0..117 (`work/qa/evs`), every mode (`work/qa/modes`), ending chain with all four prose screens.
- **Next:** run the whole list and check each shot: `python -X utf8 tools/debug/warp.py --jobs 3` (8 jobs ran the machine out of memory and the run was stopped after 5 scenes). Fix routes that miss: unverified guesses are `newgame_*`, `link_*` routes, `equip/save/controls/encyclopedia/shop` cursor counts, `ending_*` hold values, `stage_mugen`. Then GOD mode (player HP address not found yet) and a natural game over (mode 21 is forced now), `--states` library, and commit the proof sheet; then phase 3.
- **Phase 5 heads-up:** English needs horizontal text (the message scroll is a 40 px-wide vertical column) and a new font; Latin fonts exist at 0x1FC000 and 0x710000. Menu help strings exist twice (0x4CE4C and 0x4FDF0): translate both.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked by hand (headless worker). Not blocking.

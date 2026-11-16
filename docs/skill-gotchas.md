# Skill gotchas

One line per gotcha: the skill reference it belongs in, then the fact.

- scripts/fetch_emu.py + references/setup.md: `fetch_emu.py gba-bios` 404s; retrobios renamed the file to `bios/Nintendo/Game%20Boy%20Advance/GBA_bios.rom` (same sha1 300c20df6731a33952ded8c436f7f186d25d3492). Downloaded by hand with curl.
- references/graphics.md §Survey: an Orca worker can't spawn reviewer subagents; `codex exec -s read-only -i sheet.png ...` per chunk of 7 sheets in parallel worked for the static sweep (`tools/re_survey_codex.sh`). Labelling sources per 16 KB made its answers usable; one label per 500 KB region did not.
- references/graphics.md §Survey: `tiles.py render` takes one file; a multi-source deduped sheet with offset labels (`tools/re_tilesheet.py` here) would be worth adding to the skill.
- SKILL.md Step 0.2: in this Orca worker session the plugin's guard hook was not loaded (canary not blocked). Adding the `hooks` block to `.claude/settings.json` with `$HOME/.claude/plugins/marketplaces/retro-translation/...` took effect immediately, mid-session.
- references/emulator-qa.md: Mesen shares <exe>/Saves between runs; a game save written by one run turns later cold boots into Continue. warp.lua wipes SRAM via emu.memType.gbaSaveRam at start. Also 8 parallel Mesen runs exhausted memory on this machine; use --jobs 3.
- scripts/sheet.py: `sheet.py a.png --compare b.png --crop ...` printed and drew only one tile (a.png) here; and a dir of non-`f<frame>.png` files (warp's `scene_<name>.png`) gives "No f<frame>.png matched". Worked around by copying to f%06d.png names (`warp.py --proof`).
- references/emulator-qa.md §Debug tool: event shots timed by a fixed hold landed on fades/black about a third of the time with A mashed; timing the shot off the game's dialogue-list loader (on_exec, mashing stopped, +150 frames) gave a text page every time. Worth suggesting in the skill as the default for cutscene scenes.
- references/emulator-qa.md §Debug tool: a mode-byte proof (`expect=MODE`) passed for a scene that really reset the game (stage init crashed, boot code re-ran, the RAM mode byte stayed stale at 29). Proof needs a look at the shot or a reset detector (e.g. on_exec on the boot task init); a probe logging pc, DISPCNT and mode every 60 frames found it in one run.
- Claude Code reaps background shells under memory pressure; a ~1 h `warp.py --jobs 2` run was killed twice because another repo's 20 Mesen.exe (~300 MB each) were running. `warp.py --proof-only` now rebuilds the proof sheets from scene dirs already on disk, so a split run can resume by scene names.
- references/platform-gba.md: Sengoku Kakumei Gaiden mixes encodings: pointed script text is EUC-JP but item/technique names are Shift-JIS fixed records; scan every encoding, not just the first one that hits.
- references/platform-gba.md: font entry layout guessed from the bytes (rows at +4) was off by one; the draw routine read rows from +6. Read the draw routine's source offset before writing glyphs.
- references/emulator-qa.md: context-mode's hook truncates Bash/Read output above ~5 KB; write disassembly to work/ files and read them in slices.

# Skill gotchas

One line per gotcha: the skill reference it belongs in, then the fact.

- scripts/fetch_emu.py + references/setup.md: `fetch_emu.py gba-bios` 404s; retrobios renamed the file to `bios/Nintendo/Game%20Boy%20Advance/GBA_bios.rom` (same sha1 300c20df6731a33952ded8c436f7f186d25d3492). Downloaded by hand with curl.
- references/graphics.md §Survey: an Orca worker can't spawn reviewer subagents; `codex exec -s read-only -i sheet.png ...` per chunk of 7 sheets in parallel worked for the static sweep (`tools/re_survey_codex.sh`). Labelling sources per 16 KB made its answers usable; one label per 500 KB region did not.
- references/graphics.md §Survey: `tiles.py render` takes one file; a multi-source deduped sheet with offset labels (`tools/re_tilesheet.py` here) would be worth adding to the skill.
- SKILL.md Step 0.2: in this Orca worker session the plugin's guard hook was not loaded (canary not blocked). Adding the `hooks` block to `.claude/settings.json` with `$HOME/.claude/plugins/marketplaces/retro-translation/...` took effect immediately, mid-session.
- references/emulator-qa.md: Mesen shares <exe>/Saves between runs; a game save written by one run turns later cold boots into Continue. warp.lua wipes SRAM via emu.memType.gbaSaveRam at start. Also 8 parallel Mesen runs exhausted memory on this machine; use --jobs 3.

# Sengoku Kakumei Gaiden (GBA, Konami 2002, A7GJ) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `<SKILL_DIR>/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py` -> build/sengoku_en.gba (checks the dump against `rom.sha1` first): the one edition (D18/D19): manga-bubble dialogue (`docs/re/manga.md`), upright name grid/ending/link cards, narrow graphic labels sideways
- Tour:     `sh tools/debug/final_tour.sh` (every QA scene into work/qa/; then `qa_gate.py init`, visual QA, textcover)
- Check:    `python -X utf8 tools/check.py` (tests + lint; the pre-commit hook runs this; hooks: `git config core.hooksPath tools/hooks`)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/sengoku_en.gba --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 tools/debug/warp.py <scene>.. --rom <abs>/build/sengoku_en.gba --out <abs>/work/qa/<dir> [--proof] [--shot-every N] [--scenes-file F]` (scenes: `tools/debug/scenes.txt`; never ask the user to play to a scene)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Sengoku Kakumei Gaiden (Japan).gba` (8 MiB; gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own MesenCE QA fork in `tools/mesen/` (release qa-1, https://github.com/minhnhattonthat/MesenCE/releases/download/qa-1/Mesen_qa-1_Windows.zip, via `$SKILL/scripts/fetch_emu.py mesen`; gitignored; GBA BIOS in `tools/mesen/Firmware/gba_bios.bin`, sha1 300c20df…, from retrobios `bios/Nintendo/Game Boy Advance/GBA_bios.rom`; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/<bank>.json`, one entry per pointed string (id = ROM address, jp, en, kind text/debug/code/dup); format, dump and update in `tools/script.py`'s docstring; `build.py` loads every non-empty `en`. Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Copied from the skill so a clone builds without it: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py`, `tools/skill.py`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Gotchas: skill-level ones go in `docs/skill-gotchas.md`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.

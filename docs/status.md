# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress. Last build: none yet.
- **Done:** Step 0 setup: MesenCE 2.2.1 + GBA BIOS in `tools/mesen/`; original ROM smoke-boots (title -> Start -> menu; probe log works; `tools/routes/boot.txt`); rom.sha1 pinned; `tools/check.py` + pre-commit hook (failing test rejects the commit); guard hook in `.claude/settings.json` blocks `sed -i`.
- **Next:** Phase 1 recon: earlier patches, text encoding (likely SJIS), pointer tables, compression, free space, graphics-text survey -> `docs/re/`.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked by hand (headless worker); default key mappings are written by emu.py.

# Skill gotchas

One line per gotcha: the skill reference it belongs in, then the fact.

- scripts/fetch_emu.py + references/setup.md: `fetch_emu.py gba-bios` 404s; retrobios renamed the file to `bios/Nintendo/Game%20Boy%20Advance/GBA_bios.rom` (same sha1 300c20df6731a33952ded8c436f7f186d25d3492). Downloaded by hand with curl.
- SKILL.md Step 0.2: in this Orca worker session the plugin's guard hook was not loaded (canary not blocked). Adding the `hooks` block to `.claude/settings.json` with `$HOME/.claude/plugins/marketplaces/retro-translation/...` took effect immediately, mid-session.

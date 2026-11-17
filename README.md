# Sengoku Kakumei Gaiden English translation

Unofficial English fan translation of **Sengoku Kakumei Gaiden** (戦国革命外伝; Game Boy Advance, Konami, 2002): the
source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue, story events, biographies, tutorial | Translated |
| Menus, item and art descriptions, shops, saving, link-cable setup, battle results and titles | Translated |
| Menu labels, item names, stat block, HUD, map province plates, big letters, LV UP!, link cards | Translated (redrawn) |
| Ending cards and staff credits | Translated (redrawn; staff names romanized) |
| Name entry | Latin letters |
| Title logo | Redrawn in English: SENGOKU KAKUMEI GAIDEN |
| Family crests and banner mottos in the biography portraits | Left in Japanese (heraldry, not captions) |

The game was written in vertical Japanese. The dialogue reads **upright**, lettered like a manga's speech bubble:
short centred lines of capitals down the game's tall scroll. The name entry, ending cards and credits are upright
too. The narrow vertical labels (menu bars, item names, the stat block, the results screen, map plates) are drawn
**rotated 90° clockwise** in their columns: tilt your head to the right to read those.

Known issues (see also [Issues](../../issues)):
- The sideways labels (menu bars, item names, the stat block, the results screen, map plates) are a bit hard to read.
  This is a technical limitation: those columns are only a few pixels wide, too narrow for readable upright English
  words, so the English runs along the column instead.
- Link-cable play was tested only in a single emulator, not with two consoles.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `gfx/` | English labels for the redrawn sprite banks. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, graphics, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game, `Sengoku Kakumei Gaiden (Japan).gba` (No-Intro):

| | |
|---|---|
| Size | 8,388,608 bytes |
| CRC32 | 3DD25FD7 |
| MD5 | c6420001b019120cf0606dcbed749137 |
| SHA-1 | 6c2a464465855e7e8e9d8e02262ce44b61e34921 |

```sh
git clone https://github.com/minhnhattonthat/sengoku-kakumei-gaiden-en
cd sengoku-kakumei-gaiden-en
# copy your dump to: rom/Sengoku Kakumei Gaiden (Japan).gba  (the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/sengoku_en.gba
python -X utf8 tools/check.py                          # tests + text lint
python -X utf8 tools/release.py                        # BPS patch + zip in release/ (runs every QA gate)
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Konami's and is included only so
the translation can be checked against it. Sengoku Kakumei Gaiden is (c) Konami; this project is not affiliated with
them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic, with OpenAI Codex as an independent
reviewer). Corrections are very welcome.

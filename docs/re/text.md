# Text engine

## Encoding
- **EUC-JP**, two bytes per character, NUL-terminated, stored uncompressed in ROM. **verified**: `遊戯`, `我が軍`, `新しく遊戯を始めます。|nよろしいですか？` found as EUC-JP and match the title-menu and opening shots (`work/qa/explore1`). UTF-16 searches find nothing. **Shift-JIS does exist** (phase 5, `jp_left.py --sjis`): item records 0x7F7A8-0x80D44 (40 bytes, name at +12; never drawn, the on-screen names are graphics, `graphics.md`) and debug printf formats 0x81DD8-0x821A4 (`Lv1:%3d`, `アイテム出現確率一覧`, tab-separated debug logs, never on screen). Neither is in `script/`; both are out of scope.
- Control sequences are ASCII inside the EUC text:
  - `|n` (7C 6E) newline / next column. **verified** (1450 uses; line breaks match the screen).
  - `%n` player name (`よくきたな|n%nよ。`). **verified** by context (name entry precedes it).
  - `%d` number (`%dれんげき` = "N-hit combo", 0x201870). guess (printf style).
  - `%b %B %r` only in the save-confirm string at 0x61C28 (`%b%n　%Bでいいですか？|n%rＡ…決定　Ｂ…戻る|n`): likely colour/highlight on/off around the name. guess.
  - No other `%x`/`|x` sequence occurs in pointed text (`tools/re_eucscan.py` + `tools/re_eucptrs.py`).
- Not seen in real text: bytes 0x01-0x1F, half-width kana (8E xx), JIS X 0212 (8F xx xx).

## Draw path (verified by ROM-read probe, `work/qa/probe-read`, then disassembly)
- `0x080123D2`: reads the next 2 bytes (b0 | b1<<8), `bl 0x080126C0` maps the code to a glyph index, `bl 0x08011C80` draws it into slot N (N <= 0x5F, or <= 0x3B in one mode: a box holds at most 96 / 60 characters).
- `0x080126C0`: **linear search** of the font table for the code; not found -> glyph 0x135. So any new code we add must be a font-table entry (or the lookup replaced).
- `0x08011DB8`: position advance. **Vertical text**: y += 12 per character; when y + 12 > 159 the column moves x -= 12 and y returns to the top. 12 px character pitch and 12 px column pitch.
- Glyphs are drawn per character into OBJ (sprite) slots: slot records at `[0x030019A8] + 24*N`, then `0x080477FC` / `0x080475FC` (OAM setup). guess on the exact OAM layout; confirm in phase 5.
- Message window: a pink scroll on the left of the screen, about 40 px wide x 160 px tall, 3 columns of 12 px (shots: opening dialogue). Menus use the same vertical layout.

## Font (verified by disassembly of 0x0804A45C / 0x080126C0)
- Table at ROM **0x712128**, 0x3DE = **990 entries x 32 bytes**, ends 0x719CE8: `u16 index`, `u8 euc1, u8 euc2`, then 14 rows x u16 **big-endian** 1bpp (bit 15 = left), glyph about 13 x 13 inside 16 x 14.
- Contents: full-width punctuation, digits ０-９, Latin only Ａ Ｂ Ｅ Ｇ Ｌ Ｒ Ｔ, all hiragana and katakana, then kanji. No ASCII, no lowercase: **English needs a new font** (phase 5).

## Pointers
- GBA u32 `0x08000000 | offset`. 1009 distinct strings are pointer targets. Every kana-rich string that looked unpointed turned out to start 2 bytes earlier with `|n` or `%n` and is pointed there: **all real text is reached by a pointer to its first byte** (verified for 60 cases by script).
- Pointer sites:
  - **Event/script tables 0x7303B8-0x7311FC, 0x731448-0x731524, 0x733868-0x7338F8, 0x7341DC-0x7343D8, 0x7469B0-0x746CE8** (~990 pointers). In 0x730830.. pointers come in groups separated by a 0 word; inside a group the pages are **shown in pointer order**, but the strings sit in ROM in reverse, so script/*.json (ROM order) lists each group last page first. Proved in-game 2026-11-16 (`work/qa/order`): group 0x730864 shows しかも！敵は人間では… (pointer 0x730864, string 0x050654) before 各地で我が軍は… (0x730868, string 0x05062c). The earlier note here had it backwards. `tools/story.py groups --en` prints every group in display order. Mixed with records like `08xxxxx(thumb fn) 0 id` at 0x730800 (scene handlers).
  - Code literal pools: 0x9FF4-0xA2A0 (~30, menu strings), plus ~20 single pools elsewhere (`work/re/euc_pointed.tsv` lists every site).
- Repoint only through these tables and pools; never by a whole-ROM value scan.

## Text ranges (pointed strings, `tools/re_eucblocks.py`)
| Range | Bytes | Content |
|---|---|---|
| 0x04CE4C-0x04D499 | 1.6 KB | title/file menu help (copy 1) |
| 0x04E008-0x04FDD7 | 7.6 KB | names, items, techniques, system text |
| 0x04FDF0-0x05043D | 1.6 KB | title/file menu help (**copy 2**, same strings as copy 1: translate both) |
| 0x05045C-0x055BA5 | 22 KB | story dialogue (Shimazu, Nobunaga, Oichi, Sasuke, Yukimura, the Yokai King…) |
| 0x05E2AC-0x05E775 | 1.2 KB | goals and province names (`薩摩（さつま）の国`) |
| 0x061C1C-0x061C58 | small | save-confirm with `%b %B %r` |
| 0x07E090-0x07EF1B | 3.7 KB | link-cable battle mode, minigame, debug-ish `の出現位置が設定されていません` |
| 0x201800-0x202113 | 2.3 KB | results screen labels (kana and kanji twins: しょうごう / 称号), combo text |
Total about 36 KB of Japanese in about 1000 strings.

## Free space (candidate)
- 0x759178-0x7FFFFF: 0xFF fill, 667 KB, at the end of the 8 MiB ROM. Candidate only: trap-fill and tour before use. The ROM can also grow to 16 MiB (save type to check before going past 16 MiB).

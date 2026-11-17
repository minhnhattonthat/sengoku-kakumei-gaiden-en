# Name entry (`newgame_name`, also the link lobby's name screen)

Found 2026-11-16 (phase 8 session 5). Tool: `tools/name_grid.py`, test `tests/test_name_grid.py`.

- The whole screen (kana grid, 決定, the 名前入力 header) is **BG2**: tiles = LZ77 block **0x5AEA30** loaded at
  VRAM 0x0000 (`vramfind.py` against `tools/lz_dump.py`'s `work/lz/`), tilemap at VRAM 0x4000 **built at run time**
  (sequential tile ids, palettes 3-5), so the grid area's entries are captured once into
  `data/name_grid_map.tsv` (`name_grid.py capture <newgame_name ppu dump>.vram.bin`). Only the two OBJs at the top
  are sprites (cursor brush). The gender screen shares the block but none of the edited tiles.
- Grid = 85 slots, a u32 EUC table at **0x733660** in gojuon order (あ..お, か.., や　ゆ　よ with full-width
  spaces as gaps, わをんー〜, dakuten, handakuten, ぁ..ぉ, ゃゅょっ, then a position table). The cursor enters, by
  column right to left: block 1 (top) あ さ な ま ら が だ **ぱ (70-74)** ゃ, block 2 か た は や わ ざ **ば (65-69)** ぁ.
  Logged in game on 140 presses (`tools/lua/namelog.lua`, owner state `work/states/onmyou_name_input.mss`,
  2026-11-17); until then the tool had ば/ぱ the other way round, so those two columns' pictures showed the other
  block's letters (B entered b; in v1, 5-9 entered ( ) * / =). Cells are 12x12 on a
  12 px pitch: column 1 at x 165 (going left), block 1 rows from y 19, block 2 from y 83.
- The name is stored as table indices + 1 (S+4 = 0x02000618, u16 each; IWRAM 0x03001730 while editing) and
  printed through the font, so `%n` and the name box draw the kana's **font glyphs**.
- English: `name_grid.LETTERS` gives each slot a letter (block 1 A-Z . - ' ! 0-9 ? & , +, block 2 a-z : ~ ( ) * / =
  # @ ; " $). `glyph_overrides()` redraws those kana's font entries (in the engine's copy at 0x7E0100) as one
  rotated letter centred in the cell; `lz_edits()` clears each grid cell (ink 1/15 refilled from the nearest
  background pixel of the same tile) and draws the same letter white 15 / black edge 1, plus "Done" for 決定 and
  "Your Name" for the header. No English text uses kana glyphs, so nothing else changes. The default name
  あああ reads AAA.
- **Second picture (session 7):** mode 16 loads picture group 6 (getter 0x08049BA8, records 0x74F9C4: block
  0x5AEA30) or **group 7** (getter 0x08049BBC, records 0x74FAC8: block **0x5B14B4**, a pink variant with the same
  grid, 決定 and 名前入力 in the same places and the same inks 15/1). Choice at 0x08010D6A: group 7 when
  `[0x030016FC] != 0` and field +0xC of `[0x030016F4]`'s record != 1 (setter 0x08007618, 5 callers; which play
  state sets it is not traced). Its own map `data/name_grid_map7.tsv`; header refilled with the row's commonest
  background pixel and 58 rows tall (`HEADER_FILL`, `HEADER_H`). Scene `newgame_name7` (poke 030016FC=1),
  shot `work/gfx/shots/name_entry7.png`.
- Checked: `work/gfx/shots/name_entry.png` (A, down, A, left, A -> "A B G" in the box), `name_confirm.png`
  (`Is A B...` in the confirm line), link lobby (`work/qa/name6`).

# Sprite banks (OBJ label graphics)

Found 2026-11-16 (phase 8 pilot). Every OBJ label graphic (menu headers, buttons, item names, stat labels) comes
from one of **62 sprite banks**, records of 48 bytes at **0x7585D0-0x759170** (right below the old free-space
start 0x759178). Code reaches them through a pointer list at 0x04A138.. (each entry = record + 8).

| Offset | Field |
|---|---|
| +0 | u32 frame count |
| +4 | u32 flags |
| +8 | palette ptr (BGR555; tiles - palette bytes, usually 16 colours) |
| +12 | tiles ptr: raw 4bpp, uncompressed |
| +16 | tiles end = first cell table: 12-byte OAM pieces (attr0 0x8000 = tall, attr1 0x8000 = size 2 -> 16x32, y offset, tile offset) |
| +20..+40 | more tables: pieces per frame (bytes, mostly 5), frame -> piece offset, frame records; not decoded |
| +44 | u32 sizes (not decoded) |

`tools/sprites.py list` prints all 62; `render N --cols 2` draws a bank as one 16 px strip, which shows the
vertical labels upright (each 16x32 OBJ is 2 tiles x 4 rows in 1D mapping, and a label's pieces are stacked).

## Bank 22: menu headers (tiles 0x6D1FF8-0x6DB0F8, 1160 tiles)

29 headers, one **160-row slot** each (5 stacked 16x32 OBJs = the screen's full height; the slot is a peach
gradient box at the top, indices 10/11/13/14, black antialiased brush letters 1-9, white 15 below it, all drawn).
Slots 2400-2880 are the four frames of the 参加受付中 animation (0-3 dots). List and English: `gfx/bank22.tsv`.

## Redraw pipeline (`tools/gfx_labels.py`)

- `gfx/bankNN.tsv`: `start rows jp en` per slot (strip rows). `build.py` writes `gfx_labels.labels_edits()` into
  the bank's tiles in place (same size, `allowed_write` allows sprite-bank tiles only).
- English is drawn **rotated clockwise** like the dialogue (D8), in font_en's 5x9 letters (6 px per letter), black
  ink 1 with a mid-tone shadow 8, over a new gradient box sized to the text (PAD 6 rows each end), white below.
  A smeared bold closed up `m`/`w`, so it's regular weight. A slot fits 24 letters.
- `python -X utf8 tools/gfx_labels.py segments N` lists a bank's label runs; `preview N OUT.png` shows original |
  English pairs.
- Verified: `newgame_setup` shows "Load a Save" (`work/gfx/shots/pilot.png`).

## Bank 36: equipment and art names (tiles 0x6F6814-0x70DC94) - done
149 slots of 80 rows, white labels: 28 items (7 swords, 7 spears, 7 bows, 7 armours, `gfx/bank36.tsv`) x 4
grades 赤青緑黒, then 30 art slots (5 blank, 帰還の術 not among them), 6 empty boxes, 七支刀. The grade is the
**ink trio** (red {12,13,14}, blue {3,6,8}, green {2,5,9}, black {1,4,7} under palette 4; 10/11 = shared
antialias greys); `draw_plain()` reuses each slot's trio, so the English keeps the colour (D11). Checked in game
on `equip` (`work/gfx/shots/bank36_equip.png`).

## Map of all 62 banks (2026-11-16, overview sheets `work/gfx/sheet[A-D].png`, strips wrapped at 320 rows)
Rendered with `MONO`/palette 0, so multi-palette banks look odd; only the classification matters.
- **Text, to redraw:** 20 province name plates (2 kanji, ~50, plus greyed variants), 23-26 menu choice boxes
  (記録 1-4, 中断した記録, ハンディキャップ, 参加者 ...), 27 menu choices (戦国図鑑, 名一覧 ...), 28-31 menu/
  link labels (天下太平編/対戦国取り編, 記録 一..四, 一五分..四五分 time choices, 待機中/参加者), 32 stat labels
  (金 防御 攻撃 体力 脚力 次の段, 西/次/の/段), 33 big brush prompts (kana sentences), 35 HUD/equip icons (刀槍弓
  鎧術, ▲▼, kanji digits 〇-九, 連撃, 禄高 万石, あなたが), 37 操作方法選択 types, 38 上級者向 / タイプ二, 39 入る/
  閉める, 59 hiragana in boxes (name-entry kana grid), 61 combo counter digits + 連撃.
- **Already English:** 44 copyright (Konami Computer Entertainment Studios).
- **Art, no text:** 0-19, 21, 34, 40-43, 45-58 (except 47 = blue kana-like fragments, check), 60.

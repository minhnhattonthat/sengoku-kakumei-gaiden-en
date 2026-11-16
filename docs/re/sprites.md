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

## Next banks to map (from `tools/sprites.py list`)
Bank 36 (0x6F6674.., 2980 tiles, 37 frames) = item/weapon/technique names (the 0x6F6AD4 strip). Bank 23
(0x6DBC18..) and 24.. = buttons (はい/いいえ, file-menu buttons). 名前入力 (name entry header) is not in bank 22.
Render each with `sprites.py render N --cols 2` and classify.

# English text engine (phase 5)

## Decision: rotated English, two letters per glyph cell
Every text in the game (dialogue scroll, help scroll, menu strips, item and technique labels, biographies) is drawn
as vertical columns of 12 px glyph cells, one OBJ per cell, columns right to left (`text.md`). The layouts are BG
art built around those columns (the pink scroll is 3 columns wide; menu labels sit in 12 px white strips), so
horizontal English would mean redrawing every screen.

Instead English is drawn **rotated 90 degrees clockwise**: a column is one line, read top to bottom; the columns
read right to left, which is top to bottom once the player tilts the head (or the GBA) to the right. This is the
engine's own order, so no layout code changes. Each 12 px cell holds two 5x9 letters (6 px per letter): 2 letters
per cell, 26 letters in a full 13-cell column (about twice the Japanese characters per column).

Recorded as D8 in `docs/decisions.md` (pre-approved run; the owner may still ask for a horizontal redesign).

## Font entries
- Table entry (32 bytes): u16 index, u8 code byte 0, u8 code byte 1 (the lookup compares the u16 at +2 with
  `b0 | b1<<8`), u16 0, then **13 rows** of u16 big-endian 1bpp at **+6** (bit 15 = x 0). The draw
  0x08011C80 -> 0x080115EC reads the glyph from entry+6 (verified: rows written from +4 came out shifted one row up).
- Original glyphs use x 1-11, y 0-10 of the 16-wide cell; cells advance 12 px down, columns 12 px left.
- English cell (`tools/font_en.py`): letter 1 at y 0-4, gap y 5, letter 2 at y 6-10, gap y 11-12; a letter's row r
  (0 = top, 7-8 = descender) goes to x = 10 - r, so ink stays in x 2-10.

## Codes and lookup
- The reader (0x08011E46..0x08012450) treats only `%` (then a letter 0x42-0x73) and `|` (then `n` or `d`) as
  controls; every other character is read as 2 bytes and looked up. English pair codes are `b0 b1` with b0
  0x80-0x9F and b1 0x80-0xFF (4096 codes): never `%`/`|`/NUL, never EUC (b0 >= 0xA1).
- `tools/engine.py`: font table copied to 0x7E0100 (990 original entries + one per letter pair used by the script),
  pointer literal 0x04A464 repointed; lookup 0x080126C0 replaced by an 8-byte jump to 0x7E0000, which maps a pair
  code directly to 990 + (b0-0x80)*128 + (b1-0x80) and runs the original linear search for anything else.
  Free space for text relocation is 0x7C1000-0x7DFFFF (`textbank.FREE`); 0x7E0000-0x7FFFFF is the engine.
- **0x759178-0x7C0B40 is not free** (`textbank.PALETTE_READ`, `tests/test_engine.py`): the magatama page (events
  105-112) calls CpuSet(0x087573D8 -> 0x05001FE0, count 0x34BB4 halfwords), a game bug that streams 431 KB through
  the 1 KB palette RAM. The last 1 KB read (0x7C0740-0x7C0B40, 0xFF) leaves the palette all white, which *is* the
  white page. Anything written there turned the page into a dark patterned screen (found by bisecting the
  marker build's writes, then `watch.lua` read hook -> BIOS pc 0xB8E -> `tools/lua/swilog.lua`).
- The pair dictionary is rebuilt from the script on every build (sorted, so the same script gives the same ROM).

## Builds
- `python -X utf8 build.py marker [ID=text ...]` -> `build/sengoku_marker.gba`: every `text`/`dup` entry becomes
  `[id]` + filler, each Japanese line of k characters -> 2k letters (k cells, same layout as the Japanese). `debug`
  and `code` entries keep their bytes. `ID=text` overrides one entry (width-gate stress), `ID=TORTURE` gives every
  printable ASCII character.
- Runtime-inserted text (`%n` player name, `%d` numbers) is still drawn with the Japanese glyphs (upright kana,
  full-width digits); an odd-length English run before `%n`/`%d` gets a trailing space cell.

## Open (engine)
- Player name entry is a kana grid (`newgame_name`): English names need a Latin grid (graphics + code, phase 8).
- `%d` digits come out as upright full-width ０-９; rotated digit glyphs for that path are still to do.
- Text drawn from BG tiles (menu headers like 遊び選択/装備選択, mode banners 天下大乱編) is graphics, not this engine:
  `graphics.md`.

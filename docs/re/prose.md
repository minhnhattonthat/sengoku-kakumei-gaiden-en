# Ending cards (prose, staff credits, THE END)

Found 2026-11-16 (phase 8 session 6). Tool: `tools/prose.py`, test `tests/test_prose.py`, scenes `ending_*` in
`tools/debug/scenes.txt`.

- After the epilogue (ev 53 chain) the ending shows **six prose cards alternating with seven staff-credit cards**:
  Masamune, credits 1, Ieyasu, credits 2, Hideyoshi, credits 3, Terumoto, credits 4, Yukimura, credits 5,
  Yoshihiro, credits 6, credits 7, then the 完 card over the sword picture, the Konami logo and the title.
- Every prose/credits card is one **BG2 picture** (char base 0, map at VRAM 0x4000, palette 1 added by the game)
  built from three LZ77 blocks that sit right before its tiles in the ROM (a fourth, 640 zero bytes, comes first):
  - idx, 160 bytes: 40 u32 metatile ids, 8 x 5 metatiles of 32x32 px (the 8th column is half off screen);
  - defs, 8208 bytes: header `04 00 00 00 04 00 00 00 00 01 00 00 00 00 00 00` then 256 metatiles x 16 u16
    tile entries (row-major 4x4, no palette bits);
  - tiles, 16 KB (prose) or 8 KB (credits).
  Pointers: one u32 per block in the table around 0x750000 (e.g. 0x7500CC -> idx 0x5C7E14, 0x7500D8 -> tiles
  0x5C84F0). The same idx/defs/tiles layout is used by about 20 other pictures (`data/lz_blocks.tsv`: a 160-byte
  block followed by an 8208-byte one): name entry, title, map art, sword cards.
- Palette 1 on these screens: 1 = black .. 14 = white ramp; index 15 is black on the credits and on the
  Masamune/Terumoto cards, a tint on the other four. The prose cards' background is 1, the others' 15.

| Card | idx | defs | tiles |
|---|---|---|---|
| Masamune Date | 0x5BE768 | 0x5BE7E0 | 0x5BEEC4 |
| credits 1 (電脳足軽 programming) | 0x5D6CA4 | 0x5D6D10 | 0x5D72D0 |
| Ieyasu Tokugawa | 0x5C7E14 | 0x5C7E8C | 0x5C84F0 |
| credits 2 (絵筆足軽 design) | 0x5D85B4 | 0x5D8618 | 0x5D8BD0 |
| Hideyoshi Toyotomi | 0x5C9C14 | 0x5C9C8C | 0x5CA354 |
| credits 3 (楽師, 音師) | 0x5D9D84 | 0x5D9DF0 | 0x5DA368 |
| Terumoto Mori | 0x5C09B0 | 0x5C0A34 | 0x5C11A4 |
| credits 4 (声侍, 音楽御目付られ役) | 0x5DB2F4 | 0x5DB36C | 0x5DB950 |
| Yukimura Sanada | 0x5C55E4 | 0x5C5668 | 0x5C5DB8 |
| credits 5 (物書き坊主, 化粧師, 紙芝居師) | 0x5DCACC | 0x5DCB48 | 0x5DD1B8 |
| Yoshihiro Shimazu | 0x5C2DBC | 0x5C2E40 | 0x5C3598 |
| credits 6 (忍者部隊, 虫取り, 援軍) | 0x5DEEAC | 0x5DEF24 | 0x5DF5A0 |
| credits 7 (草履取り, 老中, 殿様) | 0x5E1150 | 0x5E11C8 | 0x5E17F8 |

- English: `prose.py` draws each card from scratch (font_en letters rotated clockwise as D8, bold name/role
  lines, a 1 px shadow in index 4), cuts it into deduplicated tiles, gives metatiles ids by content (blank cells
  share one, so the idx block still compresses into its slot; sequential ids would not fit) and rewrites all
  three blocks in place. Credits keep the game's joke: samurai-style role titles (Cyber Foot Soldiers, Scribe
  Monks, Sandal Bearer = director) with the real role in brackets, as the kana glosses did. Staff names are
  Hepburn readings (D2: no official romanisation found); 大類裕鎮 = Hiroshige Orui and 谷広裕史 = Hiroshi Tanihiro
  are the least certain.
- **The 完 card is not one of these pictures.** BG2 there is the sword picture; 完 is four OBJs of sprite bank 44
  (raw 4bpp at 0x71BAD8, 1D mapping, ink 15 on 0): 64x64 at (74,32), 32x64 at (138,32), 64x32 at (74,96),
  32x32 at (138,96). `prose.end_edits()` redraws that 96x96 box as a big rotated THE / END. The (c) KONAMI line
  is OBJs 4-11 (Latin, kept). LZ 0x5BB8AC (+ idx 0x5BAEE8, defs 0x5BAF38) also holds a 完 + (c) picture whose
  tiles are shared with the sword picture; it is left unedited (rewriting it broke the sword).

## Link-error card (mode 22, `link_failed`)

- BG2 in **8bpp** (BG2CNT 0x1083: char 0, map 0x8000), same picture record shape as the ending cards with 1x1
  metatiles. Record at 0x74F3B0: idx 0x589198 (30 x 20 u32; low 16 bits = id, bit 25 = h-flip, used on the
  border), +4 = 0x58C828 (600 zero bytes), defs 0x589588 (header 1, 1, 265, 0 + 265 u16), tiles 0x5897EC (32 KB).
  Its 256 colours are raw at 0x74F1F0. Text: 通信に失敗しました。電源を切って、初めからやり直して下さい。
- `tools/link_card.py` lifts the white brush text and its edge/antialiasing (every pixel within 3 px of a white
  one that is lighter than the red 110 or near-black) and writes "Link failed. Turn off the power and start again
  from the beginning." at 2x in white 223 with a black 1 edge. The new picture needs 279 tiles, more than the 265
  metatile entries, so the defs block grows (header count updated; the game reads it fine) and with the idx block
  no longer fits its slot: **build.py moves such blocks** to `textbank.GFX_FREE` (0x7D8000-0x7E0000) and rewrites
  their pointers (`build.RELOCATABLE_LZ` lists every pointer site, checked by tests/test_link_card.py).

## Replay map (after the link END card, `link_replay`)

- Same 8bpp record shape at 0x74FBEC: idx 0x5B3604, 0x5B692C (600 zeros), defs 0x5B3A10, tiles 0x5B3C88,
  palette 0x74FAEC. Japanese: header 戦国リプレイ (right panel, a vertical peach-to-white gradient), 一P..四P and
  万石 under each player's koku digits (the digits themselves are 8x8 OBJs, tile 162 = the small font).
- `link_card.CARDS["replay"]`: the header panel is rebuilt row by row (each row = its commonest light colour),
  then "Sengoku Replay"; 1P..4P; 万石 -> "0k", so a value of 3 reads "30k" (the box leaves 3 letters). Blocks
  relocated like the link-error card's. Shot: `work/gfx/shots/link_replay.png`.

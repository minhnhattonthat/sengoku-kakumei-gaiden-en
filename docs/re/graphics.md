# Graphics text survey

**Phase 8:** every OBJ label (headers, buttons, item names, stat labels) comes from the sprite-bank table at
0x7585D0, decoded in `sprites.md`, with the redraw pipeline `tools/gfx_labels.py` + `gfx/bankNN.tsv`. Done: bank 22
(29 menu headers).

Ruling D5: translate all graphics text; keep the original logo only if no official English logo exists (none known: the game was never released outside Japan, so the title logo gets an English version too).

**Title logo (D15, done):** `tools/title_logo.py` redraws 戦国革命外伝 as SENGOKU / KAKUMEI / GAIDEN on both title
pictures. Usual title: record 0x7525B0 = map LZ 0x5FCEFC, tiles LZ 0x5FD6AC, 15 raw palettes 0x7523D0. After a clear:
record 0x7527B4 = map 0x6008D8, tiles 0x601044 (other mascot), palettes 0x7525D4; 0x080077DC picks record 1 when a
save's byte +0x2A is 1 and then sets [0x030016FC] (the pink name entry). Maps are a 16-byte header + 4x4-tile
metatiles (`map_slot()`). Shots: `work/gfx/shots/title_logo.png` (both, in game; the after-clear one from a QA copy
with the branches at 0x080077B2/C8/DE NOP'd).

## Tour (boot -> title -> file menu -> new game -> gender -> name -> opening), `work/qa/explore1`, `work/qa/ppu-menu`
| Screen | Element | Layer | Source (first guess) |
|---|---|---|---|
| Title | logo 戦国革命外伝, line under it (スタートボタン…) | BG | LZ77 screen set (title loads 0x5FD6AC/0x5FCEFC/0x5FCE74, lzlog f664) - guess |
| File menu | header 項目選択; buttons 記録の選択 / 記録の複写 / 記録の削除 / 中断した所から再開 | OBJ | raw ROM 0x6D1FF8-0x6DF870 (verified by `vramfind.py` on `ppu_001400`) |
| Mode select | 天下太平録?, 物語編 / 合戦編 style buttons | OBJ | raw 0x69xxxx-0x6Fxxxx (guess) |
| Confirm | header 入力内容確認; buttons はい / いいえ | OBJ | raw 0x6Dxxxx (vramfind run 0x6DBC18, 0x6DEE30, 0x6DF7B0) |
| Gender | header 性別選択; large 女 / 男 | OBJ/BG | raw (guess) |
| Name entry | header 名前入力; kana grid | OBJ + font | grid likely drawn from the text font at run time (109-112 tiles not found raw in ppu dumps = font-drawn) - guess |
| Link time select (mode 20, `link_timesel`) | header 対戦時間選択; boxed choices 一五分 / 三〇分 / 四五分 | OBJ (guess) | not the EUC strings 07e2d4/dc/e4 (those are translated, yet the screen still shows kanji in a 2026-11-16 English-build shot, `work/qa/p7`); the only other EUC copies sit inside the description strings |
| Message window | pink scroll frame (no text) | BG | - |
| All dialogue and menu help | text | OBJ, drawn from the font | text engine (`text.md`), not graphics |

Not yet reached (phase 2 debug tool must warp to each): field HUD, pause/status menu, shop, equipment, character biographies (登場人物たちの経歴), save screen, results screen (称号 / 格付け / 所要時間), chapter or area cards, game over, ending, staff credits, link-battle (合戦編) screens, minigame.

## Static sweep
Sheets: `tools/re_tilesheet.py` over raw 0x080000-0x43FFFF and 0x690000-0x713FFF (16 KB labels), 0x719CE8-0x72FFFF, and all 560 LZ77 blocks >= 256 bytes (`work/re/lz/`, from `tools/re_lzsweep.py`); identical and blank tiles dropped. Skipped, with reason: 55 LZ blocks < 256 bytes (palettes); raw 0x440000-0x57FFFF (sound-like noise in the overview render); listed in `work/re/sweep/*_index.txt` (`skip` lines: sources with < 4 new tiles). Reviewed by codex (read-only) in 6 chunks, brief `work/re/sweep/brief.md`.

Results (raw codex lines: `work/re/sweep/result_chunk_*.txt`; 467 labels came back NO-TEXT). Tile order is scrambled in the sheets, so "what" is a first guess; each group is identified on screen with the debug tool (phase 2) and with `vramfind.py` on that screen's dump.

| Source | Kind | What | Screen (guess) |
|---|---|---|---|
| LZ 0x5FD6AC, 0x601044 | kanji-large + latin | title logo 戦国革命外伝 + © 2002 Konami Computer Entertainment line | title (0x5FD6AC verified loaded on the title, lzlog f664) |
| raw 0x719CE8-0x72FFFF | kanji-large + latin | logo fragments, ©2002 KONAMI, PRESS START | title / boot |
| LZ 0x5BB8AC | latin + kanji-large | copyright line, title characters | title variant / ending? |
| LZ 0x585370, 0x5877A4, 0x5CEE84, 0x5D31DC | kanji-large (possible) | big stylised characters among warrior art | mode select / chapter cards (0x585370 loaded at f959 = file/mode menu) **Session 7:** 0x585370 = the blue samurai backdrop of the menus (controls etc.), no text; 0x5CEE84 = ev052 villain art, 0x5D31DC = ev104_boss sword art, no text (tour shots). 0x5877A4 (picture group 3, record 0x74F1CC) loaded by no tour scene: still to place. |
| LZ 0x5EF208, 0x5F812C | kanji-large | white banner characters (林 readable) | **biography portraits** (ev101, ev092 ...): family crests and banner mottos, kept as heraldry (D12) |
| LZ 0x5AEA30, 0x5B14B4, 0x5BEEC4, 0x5C11A4, 0x5D72D0, 0x5D8BD0, 0x5DA368, 0x5DB950, 0x5DD1B8, 0x5DF5A0, 0x5E17F8 | label | outlined kana/kanji on light backgrounds (0x5AEA30 loaded at f1787 = gender / name screens) | name entry 0x5AEA30 + 0x5B14B4 done (`name_grid.py`, scene `newgame_name7`); 0x5BEEC4 .. 0x5E17F8 load on the ending chain = the prose/credit cards, done (`prose.py`) |
| LZ 0x5C3598, 0x5C5DB8, 0x5C84F0, 0x5CA354 | prose | white brush-style Japanese **sentences** with punctuation, 16 KB each | story scroll (prologue / ending / chapter intro): large redraw job, likely better replaced by font-rendered text |
| raw 0x6D0000-0x6DBFFF | kanji-large | large black brush kanji | menu headers (項目選択, 入力内容確認, 性別選択, 名前入力) |
| raw 0x6DC000-0x6E7FFF | label | outlined labels (verified: file-menu buttons 0x6D1FF8-0x6DF870) | file menu, mode menu, はい/いいえ |
| raw 0x6E8000-0x6F7FFF | label + kanji-large | small labels 間 防 気 力 の まで (stat names: 攻撃 防御 体力 気力 金, "次の…まで" = to next level) | field HUD / status screen |
| raw 0x6F6A94.. (and neighbours 0x6E6000-0x700000) | label | **item / weapon / armour / technique names**, one pre-rendered 16 px-wide OBJ strip per item (数打の刀青 = OBJ tiles 281-300 on `equip`, 0x6F6AD4-0x6F6C53, verified by corrupting it) | equip, shop, status |

The Shift-JIS item records at 0x7F7A8-0x80D44 (40 bytes, name at +12) are **not drawn**: their only readers are
whole-record copies (0x0803B4B8, 0x0803BD4C, 0x0803B3FA, 0x0803BD8A; `tools/lua/sjisread.lua`), and a build with all
139 names replaced by ＊ gave the same shots as the original on title, map_menu, equip, save, controls,
encyclopedia, shop, results, link_versus and stage_r1_hyuga (differences only in cursor blink). So item names are a
graphics job (phase 8), not a script bank.
| raw 0x6BC000-0x6CFFFF, 0x70C000 | possible | small white fragments in pale rectangles | unknown, check on screen |
| raw 0x1E4000-0x1EBFFF | label (possible) | vertical kana/kanji pieces among sprites | unknown, check on screen |
| raw 0x1FC000-0x203FFF | font | ordered set: punctuation, digits, A-Z, a-z, hiragana, katakana | secondary small font (results / name entry?); its Latin letters may serve English |
| raw 0x710000-0x712127 | font | small grid with Latin letters and digits | HUD numbers |
| LZ 0x6770C8, 0x618704, 0x625408, 0x63822C | possible | sign / lantern lettering in scenery | field maps (likely decoration; decide on screen) |
| raw 0x3C0000 | possible | small outlined letter fragments | unknown |

Takeaways for planning:
- Menus are OBJ label graphics (raw, uncompressed), so editing them in place needs no recompression.
- The prose blocks (0x5C3598..0x5CA354) are the biggest graphics job: first find the screen and whether the same text also exists as EUC strings.
- Two Latin fonts already exist in ROM (0x1FC000.., 0x710000..): candidates for the English font in phase 5.

# Scenes, game modes and story state (phase 2)

All addresses verified in MesenCE on the dump in `rom.sha1` (probes in `tools/lua/`, runs under `work/qa/`).

## Game mode (top-level scene)
- `G = [0x03000000]`: `G+0` current mode, `G+2` requested next mode (`0x0800030C` sets it). Mode handlers: ROM table
  `0x7301F0`, 42 x u32. Writing `G+2` from the map switches mode on the next frame (`warp.lua` `mode=`).
- The request only takes effect when the current scene exits (the map exits when a country is entered), so
  `warp.lua` keeps overwriting `G+2` until `G+0` matches.
- Modes (`tools/lua/modelog.lua`, probe run `work/qa/modes`):

| Mode | Screen |
|---|---|
| 0 | leftover debug menu (15 items launching 29, 2..11, 34, 36, 30, 40; handler 0x08036D9C). Debug only |
| 2..11 | debug test screens (checkerboard, sprite viewer, empty stage fields); not reachable in normal play |
| 12, 13 | boot logos, title intro ("press start") |
| 16 | new-game setup: difficulty, save slot, gender, name entry |
| 19, 20, 21, 22 | link versus: lobby (参加受付中), time select (対戦時間選択), 終了 end card, link-failure message |
| 24 | event / cutscene; event id at S+0x184 |
| 25 | national map (Start = menu: equip, save, controls, 戦国図鑑 encyclopedia, shop) |
| 29 | stage (top-down action; boss fights too) |
| 30 | castle event field |
| 34 | ending petals scene |
| 36 | results screen (戦闘結果: max combo, kills, time, rank, title) |
| 40 | encyclopedia / biography page |
| 41 | yes/no and menu dialog (title menu, "出陣します。よろしいですか？" deploy confirm) |

## Events (mode 24, id at S+0x184)
Probe: every id 0..117 forced on entering Satsuma (`work/qa/evs`). 0..68 castle and story talks (0 opening,
1/2 lord, 21 Oichi, 22 Honnoji ...), 53..74 the ending chain (epilogue, the four prose screens = LZ 0x5C84F0,
0x5CA354, 0x5C5DB8, 0x5C3598, staff credits, 完 card, then a reset to the title), 73..75 resume / save confirm,
76 Higo barrier, 77..83 barrier broken by each magatama, 84..91 + 104 + 51 boss intros (then mode 29),
92..103 biographies (mode 40), 105..112 magatama pieces. 113..117 empty.

## Game state struct
- `S = [0x030016F0] + 0x14` (= `0x02000600` in practice), 0x41C bytes, copied to `0x02000A1C` at scene changes and
  to SRAM (`0x0804A6B0`, via the buffer `0x030005A8`) when saving. Save type SRAM (`SRAM_V112`).
- `S+0x128`: country state, one nibble per country id (odd id = low nibble). Read `0x08006E30`, write `0x08006DE4`.
  1 = cleared (counted by `0x0800F710`).
- `S+0x164`: story flag bitfield. test `0x08006A20`, set `0x08006A50`. Flags k / k+8 / k+16 (k = region 1..8) are set
  by `0x0800F710`: region k has a cleared country / 7 cleared / all cleared.
- `S+0x184`: event id played by mode 24 (`0x080069F4` sets it). The castle chooser `0x0800DAEC(country)` picks it
  from the flags; the stage-clear handler `0x08005DF8` picks 0x69..0x70 for ordinary countries, 0x35 for country 47.
- NB: `S` is `0x02000614`; the copies at 0x02000600/0x02000A1C start 0x14 earlier, so offsets measured on a
  0x600-based dump are 0x14 too high.
- `S+0x19C`, `S+0x1A0`: hero position on the national map, read before the map's init runs (so warps write it
  while the previous scene still runs). Country id k sits at (x2, y2) = words 2, 3 of entry k in
  the node table ROM `0x5E7A0` (32 bytes per entry; word 5 = region). Ids 1..46 verified by poking each and reading
  the map cursor `0x02002E20`; 47 (Ezo) needs its region open.
- Castle countries: 4, 14, 22, 25, 31, 35, 42 (region bosses) and 47.

## Country ids (= index in the map label list ROM 0x731448; 0 = the key-help line)
1 Ryukyu 2 Satsuma 3 Hyuga 4 Higo 5 Bungo 6 Hizen 7 Buzen 8 Chikuzen 9 Tosa 10 Iyo 11 Awa 12 Sanuki 13 Nagato
14 Aki 15 Iwami 16 Bitchu 17 Izumo 18 Kii 19 Yamato 20 Settsu 21 Harima 22 Yamashiro 23 Echizen 24 Noto 25 Shinano
26 Etchu 27 Echigo 28 Kai 29 Ise 30 Omi 31 Owari 32 Mino 33 Suruga 34 Sagami 35 Edo 36 Shimosa 37 Musashi
38 Hitachi 39 Kozuke 40 Shimotsuke 41 Iwashiro 42 Rikuzen 43 Uzen 44 Rikuchu 45 Ugo 46 Mutsu 47 Ezo 48 Mugen

## Dialogue
- `0x08012F70(list)`: loads a null-terminated list of EUC string pointers (the lists live 0x7303B8..). Logged by
  `tools/lua/dlglog.lua`.

## The "opening loops" note from phase 1
Not a loop: after the lord's talk the national map comes up with the hero on Satsuma, and A re-enters Satsuma,
which replays the lord's hint. Move to another country before pressing A.

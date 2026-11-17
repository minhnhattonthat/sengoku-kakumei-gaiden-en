# Text coverage (phase 8)

How every script bank is reached in the emulator for `textcover.py`, and why the waived strings
(`docs/text_unshown.tsv`, written by `tools/waivers.py`) can't be. Merge runs with
`python -X utf8 tools/cover_report.py DIR.. --unshown work/qa/unshown.tsv` (per-bank counts).

All runs add `--script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='0804CE4C-0805043E,0805045C-08055BA6,
0805E2AC-0805E776,08061C1C-08061C59,0807E090-0807EF28,08201800-08202114,087C1000-087DFFFF'"`.

## Dialogue lists

Every pointed text but the results labels is drawn through the dialogue loader: `0x08012F70(list)` copies a
pointer list to RAM (reads it once, at 0x08012F88), then `0x0801316C(idx)` draws page idx. `tools/lua/liststep.lua`
logs both (`VERBOSE=1`), and with `LIST=<addr> STEP=1 [N=] [AFTER=frame]` replaces each draw's idx by 0, 1, 2, ...,
so every redraw the game makes shows the next page. `SWAP=<group>` replaces the first story-event group an event
loads (0x08730830..0x087311FF) by another one.

| Bank | Scene / run | How |
|---|---|---|
| story | every `ev=`/`dlg=` scene with `--var PAGES=2400` (A every 40 frames after the shot) | pages through each event |
| story, flag branches | `tools/debug/swap_groups.sh OUT ROM 0x08730940 0x08730b38 0x08730b48 0x08730c78 0x08730cb0 0x08730f00 0x08730f44` | ev003 with SWAP=group + PAGES |
| story, names 0x73076C | `encyclopedia_all` | the encyclopedia cursor rotates through every character |
| system (item descriptions) | `item_desc` + `tools/lua/itemdesc.lua --var STEP=1` | 0x0800A9AC(cat,item): idx = 0x0800B8F8(cat,item) in r4 at 0x0800AA7C; cats 0-3 = sword/spear/bow/armour lists, 4-6 = arts list 0x730644 |
| provinces 0x731448 | `provinces` + liststep LIST=0x08731448 N=51 STEP=1 | loaded by the map init 0x0800FD2E; redrawn on every hero arrival |
| menu_help1 0x7303B8 | `menu_help` + liststep LIST=0x087303B8 N=46 STEP=1 AFTER=4900 | loaded at 0x08008714 (title side and map menu); redrawn per map-menu item |
| link: dojo tutorial 0x734310.. | `stage_ryukyu_tutorial`-like route + `tools/lua/dojo.lua` (STUCK=500, and CTRL=0 for the other layout) | lesson state machine 0x08016FC4, state [obj+0x38] 0..17; after state 17 the 15 tip groups (table 0x08017590) cycle |
| results titles | `results_titles` + `tools/lua/results.lua --var STEP=1` | title drawn every frame of the results animation: adjective table 0x746A18, nouns 0x746B08..0x746CE4 |

## Waived (unreachable)

- **results labels**: 0x08039EA0 draws label table 0x7469B0 entries 0-7 and rank table 0x7469F8 entries 0-3 only;
  these are the only literal references (0x39E94..0x3A02C). The kana twins (0x7469D0..0x7469F4, 0x746A08..0x746A10)
  are never indexed. `Test`/`Test %d` (0x201800..) are printed by the debug printer 0x08049AB8 from 0x08039440.
- **menu_help2** (0x7306B0, a second copy of menu_help1): loaded at 0x0800BDE6, 0x0800C15A and 0x0800C2F0, each with a
  constant page, 0x29 or 0x2A (shop "sold out" / "nothing I can buy"); the other pages are never drawn.
- **link versus setup** (0x733868..0x7338F8): the lobby, handicap and battle-time help need a live link session; the
  forced modes 19/20 (`link_lobby_m`, `link_timesel`) draw their first page and ignore the cursor.
- **061c1c ↑↓**: kept Japanese (`script/keep_jp.txt`); its pointer 0x731520 has no code reference.

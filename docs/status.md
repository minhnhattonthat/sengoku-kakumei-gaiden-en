# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8/9 again for **v2.0, the one upright edition (D18)**. v1.0 (rotated English) was released as a zip
  2026-11-17 and is retired; `build.py` now builds only the upright edition.
- **Release v1.0 in progress (D20, 2026-11-17):** owner asked to release and publish (public repo + `gh release
  create v1.0`). Version is **1.0** (the old rotated v1.0 zip in `release/` was never published: run
  `tools/release.py --version 1.0 --force` to replace it). Done: build re-made (sha1 7863785d…, check ok), story gate ok, polish.md clean, no ROM/save in
  history, known issue (sideways labels a bit hard to read, technical limitation) in README.md and
  `tools/release.py`. The full tour (JOBS=2, log `work/qa/rel_tour.log`) was killed again by low system memory
  during `pages` (another project, vattroller-x-en, was running ~1 GB Mesens beside it); `tour` itself had finished.
  **Next:** rerun `JOBS=2 sh tools/debug/final_tour.sh` when memory allows, then `qa_gate.py init work/qa/manifest.tsv
  <dirs> --build build/tour.gba`, visual-QA verdicts, textcover, `tools/release.py --version 1.0 --force`, push, set public
  (topics fan-translation, gba; description "English fan translation of Sengoku Kakumei Gaiden (GBA)"), release.
- **D19 (2026-11-17, same session): narrow labels sideways again.** Owner found some upright labels hard to read and
  chose "all narrow labels sideways": `tools/gfx_labels.py`, `tools/manga.py`, `tools/manga_engine.py`,
  `data/manga_code.hex` restored from 55a1d79 (v1 rotated labels, stat digits/name letters, plates; results in v1
  pairs); kept upright: dialogue, name grid (A-I rows, YOUR/NAME, OK), ending pages, link cards. Name report
  ("upper case enters lower case"): **fixed** from the owner's state `work/states/onmyou_name_input.mss` (B
  entered b): `name_grid.BLOCK1/BLOCK2` had the ぱ/ば columns swapped; checked by logging 140 presses
  (`tools/lua/namelog.lua`, routes `work/qa/r_names*.txt`), all match the cell under the cursor; a name's I now
  has serifs (`manga.NAME_ART`). Build `build/sengoku_en.gba` sha1 7863785d… (1345 writes), check 90 ok. The
  full tour of the D19 build was killed by low system memory (not a build fault); rerun it with JOBS=2 when
  memory allows. Seen: name entry, results, equip, map menu, plates, ending, link failed
  (`work/qa/d19`). **Next:** full tour of this build, then the QA gates and `tools/release.py --version 2.0`
  (steps below). The D18 entry below is history (its upright labels were reverted).
- **D18 session (2026-11-17): one edition, everything upright.** Owner: "just have one version which is the manga
  version. make the other elements readable at original orientation". Done (commit 3abea6f, branch
  `manga-edition`): `tools/upright.py` (stacked layout: 3x7 caps, 3x5 caps when long, extra columns left to
  right, word breaks last), every `gfx_labels` renderer upright (plates as syllable lines SA/TSU/MA; HUD weapon,
  brush words, combo, orbs, lobby, stat grid, small digits/name letters), results titles stacked by a mode-1
  per-glyph down-advance (entry +5; `%s` reads `[r5-2]`), results stat labels as 3x5 letter pairs (BG routine
  0x08012A2C steps a fixed 12 px; `docs/re/manga.md`), name grid upright reading A-I across the top row, "OK" for
  決定, "YOUR/NAME" header, ending prose/credits and link cards as horizontal pages, THE/END upright. `build.py` ->
  `build/sengoku_en.gba` sha1 260fec83… (1458 writes, 2478 slices); `release.py` single edition, default v2.0;
  check 91 tests ok; smoke ok. Seen in game (work/qa/up1..3): results, titles, equip, map menu, provinces, name
  entry, lobby, combo HUD, shop.
  **Next:** the full tour of 260fec83 (`sh tools/debug/final_tour.sh`, log `work/qa/up_tour.log`, ends
  `FINAL_EXIT=`) -> `qa_gate.py init work/qa/manifest.tsv <tour dirs> --build build/tour.gba`, visual-QA verdicts,
  `textcover.py work/qa/cover build/strings.tsv`, story manifest re-check, then `tools/release.py --version 2.0`.
  Put back the final_tour.sh header comment (SRC/TOUR example: the manga variant line is stale; do not edit the
  script while a tour runs: bash reads it incrementally).
- **Manga edition (D16, 2026-11-17; superseded by D18 above: the plan below is done).** Owner asked for a second patch "with text running vertically like
  the original and manga bubble translation style" and chose manga bubble over stacked letters. Done:
  `tools/manga.py` (3x7 caps VWF, wrap 38 px + hyphenation, <= 16 px slices, layout limits), `tools/manga_engine.py`
  + `data/manga_code.hex` (lookup, advance/`|n`/end hooks, run-time line and block centring; `docs/re/manga.md`),
  `build.py manga` -> `build/sengoku_manga.gba` (sha1 be1b50c7…, 2385 slices, 1344 writes; also
  `build/strings_manga.tsv`, `writes_manga.log`), `tests/test_manga.py` (11 tests; check 84 ok), smoke ok, v1 build
  unchanged (ec92a3fe). Seen in game: opening, name confirm (`%b%n%B` colours, 8-letter name inline), map menu, equip,
  shop, provinces, menu help, encyclopedia, dojo, deploy, link texts, ev010/030/052 (`work/qa/manga1..4`).
  `tools/release.py --variant manga` (own manifest `work/qa/manga/manifest.tsv` + story pass, cover
  `work/qa/manga/cover`, zip `..._EN_Manga_v<ver>`); `final_tour.sh` takes `SRC=`/`TOUR=`.
  A full tour of be1b50c7 was started 2026-11-17 into `work/qa/manga` (log `work/qa/manga_tour.log`, ends with
  `FINAL_EXIT=`): use it only to scan the **scroll text** for layout/engine bugs (labels will change, so its sheets
  are not the release tour). Branch `manga-edition` (commit 5ce8e5b), not merged to main.
  **Next (D17, owner chose upright stacked labels):** add an upright mode for this edition, keeping v1 output
  byte-identical (test: `build.py` sha1 ec92a3fe unchanged):
  1. `gfx_labels.py`: a module switch (e.g. `UPRIGHT`/a `style` arg to `labels_edits`) and one stacking helper:
     manga caps (`manga.FONT`, 3x7) upright, centred across the strip, pitch 9 rows (8 if tight), a space = half
     pitch; when one column does not fit, words go into 2 columns right to left; shadows/edges move to right/down
     in screen terms. Route every renderer through it: strips `draw` (box, bank 22), `draw_plain` (36, 35),
     `draw_outline` (23-31, 37-39), `draw_big` (61), `grid_edits` (32, 8 px columns), `cells_edits` (33, 34, 58),
     `frames_edits` (26), `plates_edits` (20: 26x10 px plates, tiny font: likely 2 columns of 4), `orb_edits` (47),
     `HORIZ` (59, already horizontal: check), small digits/kana (`small_digit_edits`, `small_kana_edits`: upright).
  2. Results labels (mode 1, `results` bank, v1 pairs): encode upright stacked letters for this edition (a
     second glyph set: one upright letter per 12 px cell, `manga.name_glyph` style) instead of v1 pairs.
  3. BG pictures drawn rotated in v1: `name_grid.py` (grid letters + "Your Name" header; the grid then reads A-E down
     the first column, columns right to left, like the kana chart), `prose.py` (ending prose: upright horizontal
     lines like the bubbles; credits; THE END), `link_card.py` (link failed / replay). Title logo stays.
  4. `build.make_manga` passes the switch; tests for each renderer's upright output (fits, nothing outside the
     slot); `gfx_labels.py preview BANK` for both styles; then the real tour + visual QA + textcover, release
     `--variant manga`.
- **Phase 9 session 2 (2026-11-17): English title logo (D15).** Owner asked for a translated logo: SENGOKU / KAKUMEI /
  GAIDEN (`tools/title_logo.py`, font `fonts/Shojumaru-Regular.ttf` OFL, `tests/test_title_logo.py`) on both title
  pictures, the usual one and the after-clear one (record 0x7527B4, other mascot; `docs/re/graphics.md`). Build
  `build/sengoku_en.gba` sha1 093e9076…, CRC32 0FBEB0DE (2116 writes); check 72 tests ok, smoke ok; differs from v1.0
  only in the title blocks. Title-side scenes re-shot (`work/qa/p10`) and Codex-judged (`work/qa/p10_verdicts`):
  title + after-clear title ok; `qa_gate.py waive` on both manifests. **The v1.0 zip predates the logo:** run
  `tools/release.py --version 1.1` for a patch with it.
  - **"Your Name" header stripes fixed** (were in v1.0 too, flagged by Codex): the header refill copied indices per
    row, so lone rows alternated two shades (dotted lines) and group 7, whose header spans palettes 2 and 4, got a
    band out of order. `name_grid.redraw` now rebuilds the gradient in lightness from the raw palettes (map slot p =
    raw palette p - 1, checked against palette dumps), monotone, with a 2-row checker at isolated steps
    (`header_ramp`, `BAYER`), and maps it back to each tile's own band colours (a near-equal antialias twin is
    dropped). Test `test_header_gradient_runs_one_way_without_dotted_rows` (fails on the old code). Re-shot
    newgame_name, newgame_name7, link_lobby (`work/qa/p11`), Codex 3/3 ok (`work/qa/p11_verdicts`).
  - **Last build:** sha1 ec92a3fe…, CRC32 48B4F39F; differs from v1.0 only in the title and name-entry LZ blocks
    (+ the moved title map and its pointer); check 73 tests ok, smoke ok, `qa_gate.py waive` recorded.
- **Phase 9 session 1 (2026-11-17): release done.** `python -X utf8 tools/release.py --version 1.0` ran every step with
  exit 0: build, check (67 tests), smoke ok, `jp_left` 0 runs, `qa_gate check` on `work/qa/manifest.tsv` (777 sheets,
  waiver for d7b093ee) and `work/qa/story/manifest.tsv` (11 chapters), textcover 971/1037 shown + 66 waived, polish.md
  all ticked, README placeholders none, header/boot code = original, bps make + independent re-apply = build.
  - **Story pass:** `tools/story.py chapters` -> `work/qa/story/chapters/` (11 files, `story.CHAPTERS`), brief
    `docs/story-reviewer-brief.md`, runner `tools/debug/story_codex.sh` (codex exec read-only; reports in
    `work/qa/story/reports/`, earlier rounds in `round1/`, `round2/`). Round 1: 10 ok, 03_mori issue (051930,
    already fixed in the polish pass). Round 2 on the 5 changed chapters: 04_oda issue = the shrine maiden spoke
    formally (glossary gives her contractions): her lines contracted; round 3 on 04_oda ok. Minors all applied
    (`docs/polish.md`). Verdicts in `work/qa/story/verdicts/` (+ `recheck_1.tsv` = `fixed` for 4 chapters whose
    round-2 Minors were applied).
  - **Frozen text layout (D14):** relocated strings were packed in order, so one longer line shifted 353 strings
    and voided every coverage log. `data/text_layout.tsv` (`build.py freeze-layout`, frozen from the toured
    fe25914e, reproduces it byte for byte) keeps each relocated string in its toured slot while it fits and keeps
    the letter-pair codes (`font_en.Encoder(frozen=)`); `tests/test_layout.py`. d7b093ee differs from fe25914e in
    1717 bytes: the 23 edited strings, their pointers, 3 new pair glyphs. Every scene showing an edited string
    re-run (`tools/debug/recover_scenes.sh`, `work/qa/p9`, `work/qa/p9b`: 16 scenes, 50 sheets, all ok from a fresh
    Codex pass, `work/qa/p9_verdicts`); their logs merged into `work/qa/cover` (`work/qa/cover_fe25914e` = before).
  - **After any further text edit:** build, diff `build/strings.tsv` against `work/qa/strings_release.tsv` (v1.0's; only
    edited ids should move), re-run the scenes that show them with `recover_scenes.sh`, Codex the new sheets,
    `qa_gate.py waive`, then `tools/release.py --version 1.x`.
  - **Next:** nothing left in the phase list. Owner: playtest from `build/sengoku_en.gba`, decide on publishing.
- **Phase 8 session 13 (2026-11-17): visual QA done, phase 8 DONE.** The Codex run on the 777 sheets of 4977f45e
  finished (chunks 0-2 re-run from `work/qa/chunks_redo`: the first launch's codex died with the old session).
  99 issues, all eye-checked and all real except 8 stale ids: (1) Yes/No 5/2 px off-centre across the bar ->
  bank 30 centred at x_top 11 (abb7007); (2) dotted brush antialias striped beside "Your Name" in both name-entry
  pictures -> edge ink refilled, group 7 ties keep the row above's band (4658a42, `test_header_rows_carry_no_brush_ink`);
  (3) mode select, Yes/No, save, map menu, controls, shop labels were black silhouettes (OBJ palettes 5-7 show 15
  black) -> every outline bank drawn black with a shade (516a66e, 8af4653, **D13**; the brief's old "heavy font is
  ok" ruling replaced); (4) 8 manifest ids whose sheets no longer exist (fewer pages this tour): `ok`.
  `work/qa/verdicts/recheck_1.tsv` = 91 `fixed` + 8 `ok`. Re-shots of every changed screen on fe25914e
  (`work/qa/hotfix`, 21 sheets) got 21 `ok` from a fresh read-only Codex pass (`work/qa/hotfix_verdicts`).
  `manifest.tsv.build` now points at `build/sengoku_en.gba` (hash of the toured 4977f45e) and
  `qa_gate.py waive` accepts fe25914e (diff only in the menu banks' tiles and the name LZ blocks). Banks 25
  (handicap) and 39 (Go In / Shut) still never seen on screen (no warp reaches them). Smoke ok on fe25914e.
  **Next (phase 9):** story-pass verdicts per chapter (`references/translation.md` §Review), `docs/polish.md`,
  `tools/release.py` (patch + verify, qa_gate on every manifest, textcover, jp_left, debug off). **Any further
  ROM change needs a new waiver or a re-tour** (`qa_gate.py check` fails on a new hash).
- **Phase 8 session 12 (2026-11-17): final tour done on 4977f45e, Codex run stopped by low system memory.** The
  re-tour (`work/qa2`, FINAL_EXIT=0, no FAIL) is now in `work/qa/{tour,pages,desc,prov,mhelp,enc,restitles*,go/dojo,
  go/dojo0,go/lk,cover,swap}` (the 41741062 dirs, verdicts and chunks moved to `work/qa_old_41741/`).
  `qa_gate.py init` (same 13 dirs, `--build build/tour.gba`): 777 sheets, all changed, so `work/qa/chunks/chunk_000..025.txt`
  cover every sheet and `work/qa/verdicts/` is empty. **textcover on `work/qa/cover`: 971/1037 shown, 66 waived,
  exit 0** (done for this build). Triage of the old build's 209 Codex issues: all either fixed in this build
  (name splits, "no such / person" now `%n?|nI know no such person!`, Taking Entries gap, name-entry stray pixel:
  checked in the new shots) or standing non-bugs in the brief; new non-bug added: `menu_help` idx 28 is the original's
  `???` placeholder drawn as 帰帰. `vqa_codex.sh work/qa/chunks work/qa/verdicts 3` was reaped by Claude Code for
  low memory (~3.7 GB free, another project's codex/Mesen running) before any chunk finished.
  **Next:** when memory allows (`Get-Process Mesen,codex`; free > 6 GB), `sh tools/debug/vqa_codex.sh work/qa/chunks
  work/qa/verdicts 2 > work/qa_vqa2.log` (detached, e.g. `Start-Process sh`, so a reap of the agent shell does not
  kill it), eye-check each `issue`, write `verdicts/recheck_1.tsv` lines (`fixed`/`ok`) for false flags, then
  `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` exit 0 = phase 8 done.
- **Phase 8 session 11 (2026-11-17):** final tour on 41741062 **finished** (detached `Start-Process sh`, JOBS=2:
  tour 166/166, pages 124/124, every coverage run ok); textcover **971/1037 shown, 66 waived, exit 0**. Gate:
  `work/qa/manifest.tsv` (731 sheets, 25 chunks), `vqa_codex.sh work/qa/chunks work/qa/verdicts 2` running
  (log `work/qa_vqa.log`); old-build verdicts moved to `work/qa_old_b6d73/`. Codex flags so far were all the
  heavy mode-select labels (checked by eye: readable, same as the original) and SATSU/MA plates: both now `ok`
  in `docs/visual-qa-brief.md`. **Real bugs found and fixed:** (1) the player name split words after a full
  8-letter name ("Ho/w", "Wo/rking"): each name letter is a whole cell, `batches.NAME_CELLS` 4 -> 8, 29 `%n`
  lines re-broken (save confirm now `%n, OK?`). (2) Link lobby header "Taking Ent  ries.": bank 22 frames 16-18
  show their pieces out of tile order (offsets in whole tiles, `sprites.WHOLE_TILE_OFFSETS`); `gfx_labels`
  draws bank 22 on the assembled cells and lays them back (`tests/test_bank22_frames.py`). Build ba18e9be:
  re-tour into `work/qa2` (`sh tools/debug/final_tour.sh work/qa2`, log `work/qa2_final.log`).
  **Next:** when both finish, replace `work/qa/{tour,pages,desc,...}` with `work/qa2`'s, re-run `qa_gate.py init`
  on the same dirs `--build build/tour.gba` (unchanged sheets keep their verdicts), `todo` into a fresh chunks
  dir, Codex on the changed sheets, eye-check every `issue`, write `fixed`/`ok` lines for false flags, textcover
  on `work/qa2/cover`, `qa_gate.py check` exit 0 = phase 8 done.
- **Phase 8 session 10 (2026-11-17): final tour stopped by low system memory again, phase did not move.** Found
  the previous worker's runs orphaned: `final_tour.sh work/qa_b2` (every Mesen start failing, exit 3221225794 =
  0xC0000142, out of memory next to another project's emulators) and `vqa_codex.sh` on the **old-build** chunks
  (useless for the gate); killed both, deleted `work/qa_b2`. `final_tour.sh` now takes `JOBS=N` (default 3, was a
  hard 5). Re-ran `JOBS=3 sh tools/debug/final_tour.sh > work/qa_final.log`; Claude Code reaped it for low memory
  after ~163 of the tour's scene dirs (no `_proof`, pages/coverage runs not started). `work/qa/tour` is now partial
  and the old `work/qa/manifest.tsv`/`chunks` point at the old build: start over with step (1) below. **Run it only
  when other projects' emulators are not running** (check `Get-Process Mesen`; ~4-6 GB free is not enough for 3
  Mesen + other sessions), or `JOBS=2`. Same next steps as session 9.
- **Phase 8 session 9 (2026-11-17): final QA set up, runs killed by low system memory.** Done: `docs/visual-qa-brief.md`
  (game non-bugs: sideways text = `sheet.py --rotate 270`, outline menu-bar font and left start are the original's,
  scroll text over its decoration is the original's, 24-letter wraps, D5/D8/D11/D12); bank 30 Yes/No and
  15/30/45 min now **centred** like the original's (`gfx_labels.STYLE[30]["centre"]`, `tests/test_outline_centre.py`;
  `inkbox.py` margins 11/12 and 14/15 on `deploy_confirm`, bank 27 stays top-aligned as its original); 4 menu-help
  lines made one line (04cf94, 04d12c, 04d148, 04d168: the layout moved, so **textcover must be re-run**). Tours:
  `work/qa/tour_jp` (original ROM, 166/166) and `work/qa/tour` (old build 6d73f6e1, 166/166) done;
  `work/qa/manifest.tsv` (708 sheets: tour + pages + coverage dirs) and `work/qa/chunks/chunk_000..023.txt` made.
  Codex runner `tools/debug/vqa_codex.sh CHUNKS VERDICTS 4` (codex exec -s read-only, prints verdicts, script
  writes them) piloted ok; its first flags (heavy menu font, scroll overlap) were false, now non-bugs in the brief.
  **Next, in order:** (1) `sh tools/debug/final_tour.sh` (tour + pages + every coverage run + swaps with the
  textcover probe on build/tour.gba = current build, into work/qa; ~2-3 h; use fewer `--jobs` if memory is short:
  a run of 5 Mesen (~550 MB each) + 4 codex next to another project's emulators exhausted 16 GB). (2) Move old
  verdicts out, `qa_gate.py init work/qa/manifest.tsv <dirs it prints> --build build/tour.gba`, `todo`, then
  `vqa_codex.sh work/qa/chunks work/qa/verdicts 2`; check each `issue` by eye before fixing (Codex over-flags).
  (3) `textcover.py work/qa/cover build/strings.tsv --waive docs/text_unshown.tsv --mask 0x7FFFFF`. (4)
  `qa_gate.py check` exit 0 = phase 8 done. Leftovers (0) judged on screen in the tour instead: the "possible"
  sign tiles 0x6770C8/0x625408/0x63822C/0x618704 are scenery soup without a map; bank 47 orbs, bank 58 cell 29,
  bank 35 禄高/あなた cells and LZ 0x5877A4 not reached by any scene (not blocking).
- **Phase 8 session 8 (2026-11-17): text coverage DONE on build 6d73f6e1** — `textcover.py work/qa/cover
  build/strings.tsv --waive docs/text_unshown.tsv --mask 0x7FFFFF` = **973/1037 shown, 64 waived, 0 failing, exit 0**.
  How each bank is reached and why the 64 are unreachable: `docs/re/coverage.md` (waivers generated by
  `tools/waivers.py` from `tools/cover_report.py --unshown`; it refuses any id no rule explains). New probes:
  `tools/lua/liststep.lua` (LIST/STEP/N/AFTER page stepping of a dialogue list, SWAP=group for story-flag branches,
  VERBOSE logs every list load/draw), `itemdesc.lua` rewritten (idx is r4 at 0x0800AA7C), `results.lua` (STEP titles,
  RANK=), `dojo.lua` (tutorial state stepper, CTRL= layout). New scenes: `item_desc`, `provinces`, `menu_help`,
  `results_titles`, `encyclopedia_all`, `dojo_lessons` (each needs its probe vars, see the comment above it in
  `scenes.txt`); `tools/debug/swap_groups.sh` for flag-branch groups. warp.lua: `(steps)xN` repeat in input/route.
  Runs merged into `work/qa/cover` (log.txt copies of tour2, pages, desc, prov, restitles*, mhelp, go/dojo*,
  go/lk, enc, swap, swap2). **If the text layout changes (any `en` edit or relocation), re-run these scenes on the
  new build before release** (addresses in strings.tsv move). Shots of every item description / province / menu
  help page / title / lesson are in those dirs, not yet given a visual-QA verdict (they belong in the final tour).
- **Phase 8 session 7 (2026-11-16):** **tour2 finished** (157/157 ok, `textcover.lua` + `lzlog.lua`, log
  `work/qa/tour2.log`; the rest re-run from `work/qa/tour2_rest.txt` on build b56c4791). **textcover: still 174/1037**
  (`work/qa/tour2_cover.txt`): never shown = story 336/458 (dialogue pages after the first), results 187/198
  (rank titles etc.), system 137/138 (item descriptions), link 98/102, provinces 38/51, menu_help1 28/44,
  save_confirm 1. **game_over fixed**: new warp key `hpzero=N` (HP pinned to 0 N frames into a stage), END card
  shot. New warp keys `god=1` (per scene) and `poke=ADDR=VAL`. **Combo counter seen** (scene `combo`, 24 HITS,
  `work/gfx/shots/combo_hits.png`) and a new graphics text found there: the stage's **昇段!! level-up popup**
  (raw OBJ tiles 0x42B796 in sprite record 0x74ECB8, outside the bank table) -> **LV UP!** (`gfx_labels.POPUPS`,
  `tests/test_popups.py`, scene `lv_up`, `work/gfx/shots/lv_up.png`). `tools/sprite_scan.py` lists the 62 sprite
  records outside the bank table (0x743000-0x74F000); the 31 small ones checked by eye, only the popup is text;
  the 31 big ones (character/boss animation) not checked tile by tile. **Second name-entry picture done**
  (LZ 0x5B14B4 = picture group 7, chosen when `[0x030016FC] != 0`; `name_grid.PICTURES`, map
  `data/name_grid_map7.tsv`, scene `newgame_name7`, `work/gfx/shots/name_entry7.png`). Leftover LZ blocks placed:
  0x585370 menu backdrop, 0x5CEE84/0x5D31DC event art (no text); 0x5EF208/0x5F812C are biography crests, kept
  (**D12**). Last build sha1 6d73f6e1….
  **Text-coverage work started:** warp.lua `--var PAGES=N` = after a dialogue scene's shot, press A every 40
  frames for N frames (checked on ev003: pages advance, event ends, back on the map). A PAGES=2400 run over the
  124 `ev=`/`dlg=` scenes was started at hand-off: `work/qa/pages` (log `work/qa/pages.log`, ROM copy
  `build/tour.gba` = 6d73f6e1). If `grep -c ^ok work/qa/pages.log` is short of 124, re-run the missing ones; then
  `textcover.py` over **both** `work/qa/tour2` and `work/qa/pages` (copy or symlink both into one dir, or run
  twice and merge). Item descriptions: drawn via the dialogue loader 0x08012F70(list) from 0x0800A9AC, a switch
  on category 0-6 that calls 0x0800B8F8(cat) and loads lists 0x7304E8 / 0x73055C / 0x7305D0 / 0x730474 /
  0x730644 (29, 29, 29, 29, 26 entries); how the item index reaches the list is not yet clear (the `ldr r0, =list`
  is followed directly by the bl: read 0x0800A9E6..0x0800AA7C whole). Probe `tools/lua/itemdesc.lua` logs these
  calls (STEP=1 meant to step the index; untested, its r1 assumption is wrong). The `equip` route + 30 downs
  (`work/qa/go/desc.txt`) made only one call: the cursor route has to move over the item list, find the right
  keys from the equip shots.
- **Phase 8 session 6 (2026-11-16):** **ending cards done** (`docs/re/prose.md`, `tools/prose.py`): 6 prose
  cards (Masamune, Ieyasu, Hideyoshi, Terumoto, Yukimura, Yoshihiro) and 7 staff-credit cards are BG pictures
  (idx 160 B / defs 8208 B / tiles LZ triples), redrawn rotated with content-deduped metatiles in their own
  slots; the 完 card is bank 44 OBJ tiles at 0x71BAD8 -> THE / END. Credits keep the samurai joke titles
  (Cyber Foot Soldiers (Programming) ...), staff names in Hepburn (D2; Hiroshige Orui, Hiroshi Tanihiro least
  sure). Scenes `ending_*` retimed: one per card (`work/gfx/shots/ending_cards.png`). **Link-error card done**
  (`tools/link_card.py`, 8bpp, text lifted off the emblem; `work/gfx/shots/link_failed.png`); its blocks
  outgrew their slots, so **build.py now relocates LZ blocks** to `textbank.GFX_FREE` 0x7D8000-0x7E0000 (text
  FREE now ends there; `build.RELOCATABLE_LZ` lists pointer sites). **Link time choices** (bank 30 slots 98/146/194)
  drawn black: they use OBJ palettes 5-7 (`work/gfx/shots/link_timesel.png`). **Bank 47** = the seven magatama
  orbs (信智天仁忠孝勇) -> initials F W H M L P C (`gfx_labels.ORBS`); not yet seen in game (ev105 shows a shard
  icon, not these). **Link replay map done** (after the link END card; 8bpp picture, 戦国リプレイ -> "Sengoku
  Replay", 1P-4P, 万石 -> "0k"; new scene `link_replay`; `tools/link_card.py` now handles both 8bpp link cards,
  `work/gfx/shots/link_replay.png`). Full tour with `textcover.lua` + `lzlog.lua` started into `work/qa/tour2`
  (log `work/qa/tour2.log`, ROM copy `build/tour.gba`; 46/163 done at hand-off, it may have been killed with the
  session: if `grep -c ^ok work/qa/tour2.log` is short, re-run it). Last build sha1 b56c4791….
- **Phase 8 session 5 (2026-11-16):** **bank 20** province plates (`gfx_labels.PLATES`, tiny 5-row caps, "SATSU/MA"
  two-line splits; seen on `map`), **bank 58** = the stage HUD weapon glyph 刀槍弓 -> SWORD/SPEAR/BOW (`CELLS[58]`,
  seen on `stage_r1_hyuga`), **bank 59** = the title's "Please press START" banner (horizontal, `gfx_labels.HORIZ`;
  it was not the name grid), and the **Latin name-entry grid** (`tools/name_grid.py`, `docs/re/name-entry.md`:
  BG picture LZ 0x5AEA30 recompressed in its slot, kana font glyphs -> rotated letters, "Your Name" header,
  "Done"; checked on newgame_name, the confirm line and link lobby). New: `tools/lz_dump.py` (every LZ block to
  `work/lz/` for `vramfind.py`), `sprites.frames` flags bit 3 (tile offsets not halved), test_name_grid.py.
  Shots in `work/gfx/shots/` (bank20_map, bank58_hud, bank59_title, name_entry, name_confirm). Title logo stays
  Japanese (D5: no official English logo).
- **Phase 8 session 4 (2026-11-16):** banks **26, 33, 34, 35 (rest), 61 done** (`docs/re/sprites.md` §Banks 26..61):
  new `sprites.frames()`/`sprites.py frames N` decode the cell tables (pieces, palettes) and assemble cells;
  `gfx_labels` got `big` style (61), `CELLS` (33, 34: scaled caps across consecutive square cells), `FRAMES` (26)
  and `(clear)` as an `en` value. **Bank 34 was mis-classified as art**: it is the big 男/女/空/終/了 (the "BG"
  item of step 3), now MAN/WOMAN/EMPTY/END. Seen in game (`work/qa/p8b/rot.png`, rotate 270): EMPTY on
  newgame_setup and save, MAN/WOMAN on gender select, END on link_end_card, Name boxes on link_lobby_m. Not seen:
  33 (link versus start, needs 2 GBAs), 35's 禄高/あなた cells (link?), 61 combo counter (no stage route lands a
  hit yet: `work/qa/b33/scenes.txt` `combo` walks up mashing A and meets no enemy).
  **Flaky scene:** `game_over` no longer dies on this build (2 runs, no 終 card, HP never 0); re-time or GOD-less
  route needed. Spotted, not yet handled: the stage HUD's big red 刀 weapon glyph (bottom left, every stage) is
  not in any redrawn bank; the link versus map has a Japanese header and リプレイ-like label (`work/qa/b33/le_4.png`).
- **Phase 8 so far (session 1, 2026-11-16):**
  - Phase 7 review (Minor only) fixed: `textbank.relocated()` = every ` old slot` entry; regression test; 3 newly exposed byte-table words classified in `tests/test_build.py` NOT_POINTERS.
  - `build.py` now writes `build/strings.tsv` (id, read offset) for `textcover.py`.
  - **Graphics pipeline found and piloted** (`docs/re/sprites.md`): every OBJ label comes from 62 sprite banks at 0x7585D0 (`tools/sprites.py list|render N --cols 2`). Redraw = `gfx/bankNN.tsv` + `tools/gfx_labels.py` (rotated font_en letters over a new gradient box, written in place by `build.py`). **Bank 22 done** (29 menu headers incl. the 参加受付中 animation); checked in game on `newgame_setup` ("Load a Save", `work/gfx/shots/pilot.png`).
  - Baseline tour started: `warp.py --jobs 3 --proof` + `textcover.lua` into `work/qa/tour` (log `work/qa/tour.log`). Scenes after ~#40 ran on the bank-22 build. It is a baseline only: the gate tour must be re-run after the graphics are done. **Result:** 148/148 scenes ok, 10 proof sheets in `work/qa/tour/_proof` (not yet reviewed); `textcover.py` = **174/1037 strings shown**, 863 unshown. Each scene shoots one page, so coverage needs scenes (or a `mash=`/dialogue-advance variant) that page through every event's dialogue, plus scenes for menu help, item descriptions and results labels.
- **Phase 8 session 2 (2026-11-16):** all 62 sprite banks classified (`docs/re/sprites.md` §Map: text in 20,
  23-33, 35-39, 59, 61). `gfx_labels.py` has a second style `plain` (white label, each slot's own ink trio,
  proportional letters, optional centring, bare-glyph cells cleared to 0). **Bank 36 done** (149 equipment/art
  names, colour grade kept by ink, D11) and **bank 35 icons + digits** (刀槍弓鎧術 -> Sw Sp Bw Ar A1-A3, 〇-九 -> 0-9);
  both checked on `equip` (`work/gfx/shots/bank36_equip.png`, `work/gfx/shots/bank35_equip.png`). Bank 35's
  禄高/万石 and あなたが/は/番/!! cells are still Japanese (find where they show first). The equip screen's stat block
  (金 防御力 攻撃力 気力 体力 脚力 次の段まで, kanji numbers, 両) is **bank 32**: 8 px wide pieces, not 16 px
  strips; needs its own layout (caps without descenders fit 8 px, e.g. GOLD DEF ATK SPR HP SPD NEXT) and its
  digits are separate from bank 35's.
- **Phase 8 session 3 (2026-11-16):** **bank 32 done** (stat block: `gfx_labels.GRID`, 2 OBJ pieces, columns at
  x=5+8k; RYO SPEED GUARD ATTACK SPIRIT HEALTH NEXT LV LV) and the **8x8 small font's 〇-九 -> rotated 0-9**
  (0x7D098, `small_digit_edits`, allowed in `build.allowed_write`), checked on `equip`. **Menu choice banks done**
  (23-25, 27-31, 37-39, style `outline`), 10 menu scenes checked (`work/gfx/shots/menus_outline.png`). Still
  Japanese on those shots: big brush 空 (save slots) and 男/女 (gender), link lobby 参加 boxes (bank 26, 32 px
  wide) + kana names, the map menu's %n default name あああ. Last build sha1 6d6b9b65….
- **Next (phase 8), in order:** (A) text coverage: done (session 8). (0) leftovers: where bank 47's orbs
  show, bank 58 cell 29 (framed 術 icon), bank 35's 禄高/万石 and あなた cells, LZ 0x5877A4 (picture group 3, no
  tour scene loads it: find group 3's caller, xrefs of 0x08049AD8 with r0=3), sign lettering in stage tiles
  0x6770C8 (Mutsu/Uzen), 0x625408 (most stages), 0x63822C (events), 0x618704 (credits): look at those scenes'
  shots; then
  (1) if `work/qa/tour/_proof` is missing or the log is short, re-run the tour: `python -X utf8 tools/debug/warp.py --rom <abs>/build/sengoku_en.gba --out <abs>/work/qa/tour --jobs 3 --proof --script $SKILL/scripts/lua/probes/textcover.lua --var "RANGES='0804CE4C-0805043E,0805045C-08055BA6,0805E2AC-0805E776,08061C1C-08061C59,0807E090-0807EF1C,08201800-08202114,087C1000-087DFFFF'"` (background, ~1 h); then `textcover.py work/qa/tour build/strings.tsv --mask 0x7FFFFF` and add scenes/waivers (dialogue pages beyond the first may need a mash route). (2) map the other banks: `sprites.py render N --cols 2` for each, classify (bank 36 = item names, 23/24 = buttons, 名前入力 header elsewhere), add `gfx/bankNN.tsv` rows; strips narrower/wider than 16 px need `gfx_labels.W` per bank. (3) non-sprite graphics: ending prose LZ blocks, credits, link-error card (title logo stays Japanese, name grid done; find each screen's BG block with a ppudump + `vramfind.py VRAM work/lz`, edit as `name_grid.py` does). (4) final tour on the finished build, `qa_gate.py init/todo`, visual QA by `codex exec -s read-only` per chunk, `inkbox.py`, `textcover.py`.
- **Phase 7 result:** build green. `tools/check.py` (37 tests) = batches lint (control codes, ASCII, glossary, 3x24 budget, honorifics, gendered address, stub last lines) + `tests/test_build.py` on an in-memory English build: `build.verify` (allowed ranges + romdiff with the write log), every pointer site of every edited string reads its English, no word outside the sites points at/into a moved string (sound/LZ noise 0x440000-0x690000 excluded, 14 noise hits checked), hook bytes asserted, no branch/literal into the 8-byte lookup hook, no Japanese in `en`, untranslated text only on `script/keep_jp.txt` (061c1c arrows). `jp_left.py build/sengoku_en.gba --tbl tbl/jp.tbl --gba-ptrs --known data/jp_known.txt` = 0 runs (same with `--slots` from text_sites). Results screen labels fit in-game (`work/qa/p7`); the link time-select choices 一五分/三〇分/四五分 are graphics (added to `docs/re/graphics.md`).
- **Phase 6 review fixes (2026-11-16):** page order proved in-game (`work/qa/order`): pages show in **pointer order**, strings sit in ROM reversed, so script/*.json lists a group last page first (`docs/re/text.md` had it backwards; `tools/story.py groups --en` prints display order). Added `docs/synopsis.md`, `docs/style-reference.md`, `docs/translator-brief.md`; display-order flow review + re-review with synopsis (`docs/reviews/`), all Important fixed, one waived with reason. Honorific lint, gendered-address lint, balanced wrap + `batches.py rewrap`.
- **Phase 6 result:** every `text` entry in `script/` has `en` (only 061c1c ↑↓ stays the game's glyphs). Tool `tools/batches.py` (split / check / fix / merge; word-wraps English into 3 lines x 24 letters, budgets per bank incl. results 12/11/10/4 cells, `%n` = 4 cells), lint run by `tests/test_batches.py` in `check.py`. Item descriptions generated by `tools/items_en.py`. Glossary + voices in `glossary.md`, D9/D10 in `decisions.md`. Review: `codex exec` read-only over all pairs (`tools/pairs.py`), 11 Important fixed and re-reviewed ok, 0 Critical; 8 Minors in `docs/polish.md`. Story pass per chapter (phase 9) still to do, from `docs/synopsis.md`'s chapter list.
- **Phase 5 result (`docs/re/english.md`, `data/windows.tsv`):**
  - D8: English is drawn **rotated 90° clockwise** in the game's own vertical columns, 2 letters per 12 px cell (`tools/font_en.py`, 5x9 font, all printable ASCII). Pair codes b0 0x80-0x9F; font table at **0x7E0100**, lookup 0x080126C0 hooked to a direct index at 0x7E0000 (`tools/engine.py`). Text relocation 0x7C1000-0x7DFFFF.
  - **0x759178-0x7C0B40 is not free**: the magatama page's buggy CpuSet streams it into palette RAM; its 0xFF is what makes that page white (was the "dark magatama screen" bug; fixed, guarded by `tests/test_engine.py`).
  - `build.py marker` / `build.py marker STRESS=1` (rulers) / `ID=text` overrides / `0509d8=TORTURE`. Torture line renders all 95 glyphs (`l` redrawn with a tail).
  - **Width gate done** (`data/windows.tsv`): every bank but `results` is the pink scroll, 12 cells = 24 letters x 3 lines (story, menu help, system = item descriptions, provinces, link, save_confirm = name confirm). `results` is another renderer: `|n` is not a control there, labels 24 letters, `%d` values 6 cells incl. one per digit, title words 22 + 20 letters. Only guess: link time labels 07e2d4/dc/e4 (not drawn headless; keep to 6 letters).
  - Shift-JIS item records (0x7F7A8-0x80D44) are **never drawn**; on-screen item/weapon/technique names are pre-rendered OBJ graphics (~0x6E6000-0x700000, `graphics.md`). SJIS 0x81DD8-0x821A4 = debug printf. Neither goes into `script/`.
  - Still Japanese in the marker build, all graphics (phase 8, `graphics.md`): menu headers/strips/choices, item names, map labels, stat labels, HUD 刀, big letters (空, 女/男, 終), link-error card, ending prose, credits; name-entry kana grid (needs a Latin grid). Runtime: `%d` digits are upright full-width glyphs, `%n` default name あああ.
  - Probes added: `tools/lua/lookuplog.lua` (glyph lookups), `calllog.lua` (any function's calls), `sjisread.lua`.
- **Phase 8 plan (written at phase 7 end):** per `references/emulator-qa.md` and `graphics.md`: tour every changed scene by warp (`tools/debug/scenes.txt`, `--sheet`, rotate 270 to read) and get a read-only visual-QA verdict per sheet (no subagents here: `codex exec -s read-only -i sheet.png`, as `tools/re_survey_codex.sh`), `qa_gate.py check`; redraw every graphics-text row of `docs/re/graphics.md` in English (menu headers/strips/choices, item names, map labels, stat labels, HUD 刀, big letters, link-error card, link time choices, ending prose, credits); a Latin name-entry grid (the default name あああ draws as rotated kana in `%n`, see `work/qa/order/z.png`); `inkbox.py` on choice/centred boxes; `textcover.py`. Still guessed: link time strings 07e2d4/dc/e4 (where they are drawn is unknown; 3 cells), results `%d` values at 2 digits (1-digit values checked).
- **Done:**
  - Step 0 setup: MesenCE 2.2.1 + GBA BIOS in `tools/mesen/`; original ROM smoke-boots; rom.sha1 pinned; `tools/check.py` + pre-commit hook; guard hook in `.claude/settings.json`.
  - Phase 1 recon (`docs/re/`): no earlier English patch (only Chinese ones). Text is **EUC-JP**, uncompressed, `|n` newline, `%n` name; about 1000 pointed strings / 36 KB in 8 ranges (`text.md`). **Vertical text** drawn one OBJ per character, 12 px pitch; font 990 glyphs at 0x712128 found by linear search (no Latin lowercase). Pointers in event tables 0x7303B8-0x746CE8 + code pools. LZ77 only (wrapper 0x08048964, 615 blocks). Free-space candidate 0x759178-0x7FFFFF (667 KB). Graphics-text survey (`graphics.md`).
  - Phase 2 RE (`docs/re/scenes.md`): game modes (G=[0x03000000], table 0x7301F0), state struct S=0x02000614 (story flags S+0x164, country nibbles S+0x128, event id S+0x184, map hero position S+0x19C/0x1A0), map node table 0x5E7A0, all 117 event ids labelled, leftover debug menu = mode 0. The "opening loop" was A re-entering Satsuma on the national map.
  - Phase 2 tool: `tools/debug/warp.lua` + `warp.py` + `scenes.txt` (~140 scenes: title side, link mode, map menu screens, stages per region + tutorial, results, game over, ending prose/credits/end card, every event incl. biographies and bosses). Proven by single runs this session: map, map menu, Higo barrier, path Higo→Satsuma→deploy confirm, stages in every region (mode 29), every event 0..117 (`work/qa/evs`), every mode (`work/qa/modes`), ending chain with all four prose screens.
  - Session 2026-11-16: whole list ran at `--jobs 3`: 147/148 logged DONE + SCENE_OK. Fixed after visual check: `stage_ryukyu_tutorial` is the dojo in mode 30 (expect=30); mode 21 is the link 終了 card (renamed `link_end_card`); real `game_over` = walk Hyuga's stage without GOD, HP 0 at ~7620, shot lands on the in-stage 終 card (then mode 13 title); `link_versus`/`link_lobby` are 対戦国取り編's gender select and name entry (lobby needs a 2nd GBA: `link_lobby_m` forces mode 19); event shots now timed off the dialogue loader (`dlg=`, default +150 frames for `ev=` scenes; ending chain `dlg=0`), checked on ev001/003/005/007 + lord_after_higo. **GOD=1** works: HP = u16 S+0x80 (60 full), pinned each frame. `debug_menu` (mode 0) runs but draws a blank green screen (debug only; leave it). `warp.py --proof` collects scene shots into `<out>/_proof` + sheets.
  - Proof run 2026-11-16 (second session, `--jobs 2 --states --proof`): scenes 1-92 in list order (title … ev051_boss) all logged ok, with states in `work/states/`. All 92 shots checked by eye: every event shows a text page, the title side, menus, stages, link screens, game over and ending chain are right, and `debug_menu` is the known blank green screen. **`stage_mugen` was a false positive**: entering country 48 resets the game (boot code 0x08000F8C re-runs, screen black, mode byte stale at 29). Removed from `scenes.txt` with a note; 148 scenes now. Then Claude Code killed the run for low memory (about 20 `onmyou-taisenki-zeroshiki-en` Mesen.exe running again). New `warp.py --proof-only` rebuilds `_proof` from the scene dirs on disk without running the emulator.
  - **Phase 2 done** (third session): the last 57 scenes (ev052..ev112) all logged ok at `--jobs 2`; proof sheets 6-10 checked by eye: every event, biography, boss, barrier, magatama and resume/save screen shows its text page. All 148 scenes in `scenes.txt` now have a proof shot (`work/qa/warp/_proof`, index.txt) and states in `work/states/`.
  - **Phase 3 done**: `python -X utf8 build.py identity` is byte-identical (`tests/test_identity.py`, in `tools/check.py`). `data/text_sites.tsv` (1152 sites -> 1101 strings, `tools/textmap.py`), `tools/textbank.py` (in-place write within the string's 4-byte padding, else move to free space 0x759178.. and rewrite every site), `tbl/jp.tbl` (`tools/gen_jptbl.py`, exact roundtrip), `tools/lz77.py` + `data/lz_blocks.tsv` (615 blocks; unedited blocks kept verbatim, the game's compressor isn't reproducible). Details: `docs/re/build.md`.
  - **Phase 5 done** (2026-11-16): see "Phase 5 result" above.
  - **Phase 4 done**: `tools/script.py dump|update|stats` -> `script/<bank>.json` (8 files, 1101 entries: 993 `text`, 57 `debug` = half-width katakana labels 0x04E008-0x04E20F with a `reading` field, 7 `code` = `%n`/`%d,%d,%d`/`???`/`error`, 44 `dup` = menu_help2 with `same_as` its menu_help1 twin, whose `en` it inherits). `dump` never overwrites; `update` keeps en/notes/status and flags `jp-changed`. `tests/test_script.py`: every string once, jp re-encodes to the ROM bytes, files match a fresh dump, ranges fully covered (no non-zero byte outside a string's room), loader path byte-exact, dup inherits en. `build.py` loads every non-empty `en` (checked in memory: a long line relocates to 0x759178 with its pointer rewritten; a short one stays in place, its dup copy too).
- **Open question (not blocking):** how the real game reaches 無限国 (country 48, label ROM 0x5E2FC via 0x731508) is unknown; if it turns out to be a real stage, add a scene for it.
- Menu help strings exist twice (0x4CE4C and 0x4FDF0): menu_help2 entries are `dup` and inherit menu_help1's `en`.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked by hand (headless worker). Not blocking. D8 (rotated English instead of a horizontal redesign) was the agent's call under D6; the owner may overrule it (not blocking, work continues on rotated text).

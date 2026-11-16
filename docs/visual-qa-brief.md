# Visual-QA reviewer brief - Sengoku Kakumei Gaiden

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md`.

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- **The game is played sideways.** Every Japanese text was vertical columns; the English is drawn rotated in
  those columns (D8: 2 letters per 12 px cell, columns right to left = lines top to bottom). On the raw sheet
  English letters lie on their side: crop and pass `--rotate 270` to `sheet.py` (90 shows them upside down) to read them upright. Rotated
  English is the design, never an issue by itself.
- The title logo (戦国革命外伝 lettering) stays Japanese (D5: no official English logo).
- The family crests and banner mottos in the biography portraits (ev092-ev103: 十, 一 with three stars, 六文銭,
  大一大万大吉, aoi) are heraldry, kept (D12). Any other kanji in those scenes is an issue.
- Scenery kanji on signs, lanterns or banners inside stage/map backgrounds: report it as an `issue` with the tile
  position so it can be judged; if `tour_jp` shows the same art it is still worth the note.
- Menu bar labels (save menu, controls, shop, map menu, mode select, Yes/No and similar choice bars) are drawn in
  black letters with a grey shadow (the selected bar's in dark red) that start at the bar's left edge (top, when
  upright), as the original's heavier kanji labels do. Builds before fe25914e drew them as an outline font that
  showed as black silhouettes: an issue there, fixed since.
- The link END card (scene `link_end_card`): the original's 終了 is two 64x64 cells; 終 alone is also the
  single-player game over card, so its "END" sits in the left cell and 了 is cleared: left of centre is `ok`.
- The province plates beside the hero on the national map are 16x32 sprites in a tiny 5-row caps font; a name too
  long for one line is split over two lines on purpose ("SATSU/MA"): `ok`.
- The bottom scroll's help / message text runs over the scroll's diamond and line decoration on the right half:
  the original's text does the same (the decoration is under the text area).
- Yes/No (and 15/30/45 min) bars centre their label; other choice bars start at the bar's edge, as the original's.
- `tour_jp` frames are not in step with the English ones (same scene, different timing): compare the same
  screen, not the same frame number.
- Dialogue lines hold 24 letters (12 cells of 2). A short last line from word-wrapping at that limit ("...gather
  the magatama|nshards!") is normal English, not an issue; report a line break only when the last word would
  have fitted on the line above, a word is split, or a page cuts a sentence where the original does not.
- Scene `menu_help` page idx 28 (0x04D098) is the original's own `???` placeholder (bytes 3F 3F 3F, unchanged):
  the game draws it as two kanji (帰帰) over the previous page's "Change the controls.": `ok`.
- Debug menu text (scene `debug_menu`) is the project's own debug tool, not shipped: `ok`.
- Item / art name labels drop the colour word (D11): the ink colour shows the grade.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.

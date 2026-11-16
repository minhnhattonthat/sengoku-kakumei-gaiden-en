# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-16 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-16 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-16 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-16 | Abbreviations | engine work first (default), abbreviate | Default: full names and terms; engine work (VWF, wider boxes, relocation) before abbreviating. |
| D5 | 2026-11-16 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); keep the original Japanese logo only if no official English version exists. |
| D6 | 2026-11-16 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, report at the end. Never `gh release create`, never change repo visibility. |
| D7 | 2026-11-16 | Existing saves / savestates | user provides, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-16 | English text layout (every text is vertical columns in BG art built for them) | rotated English in the existing columns (2 letters per 12 px cell); horizontal English with every screen redrawn; tiny horizontal font in the 40 px scroll | Agent's call under D6 (pre-approved run): **rotated English**, read by tilting right; columns stay right to left = lines top to bottom. Keeps every layout, needs no per-screen work, about twice the Japanese characters per column. Horizontal would mean redesigning every BG screen and menu. Owner can overrule; details `docs/re/english.md`. |

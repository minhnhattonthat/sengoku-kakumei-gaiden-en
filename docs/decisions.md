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
| D9 | 2026-11-16 | Register, voices and sound effects (phase 6) | archaic English; plain modern with period feel; heavy localisation | Agent's call under D6: plain modern English with a period feel; lords formal without contractions, Sasuke/townsfolk/shrine maiden casual, the Sword Saint an old master ("my boy", "eh?"); laughs and cries romanised (Heh heh heh, Guoooh); furigana readings dropped. Voices in `glossary.md`. |
| D10 | 2026-11-16 | Fixed terms (phase 6) | romanise (Kampaku, yoma, kekkai) or translate | Translate where English is clear: 妖魔 demon, 結界 barrier, 関白 Regent, 連撃 combo, 術 art, 気力 spirit, 走る Dash, ちょうやく Leap; keep magatama, ryo, koku, Nue. 中国 = Chugoku (region). Province names "<Name> Province". |
| D11 | 2026-11-16 | Item/art name labels (bank 36 OBJ graphics, 80 rows = about 12 letters) | name + colour word (does not fit); name + colour initial; name only, colour kept by ink | Agent's call under D6: name only. The four grades 赤青緑黒 are already drawn in red/blue/green/black ink (palette 4), which the redraw keeps, and the item description names the colour. Arts drop "Art" (の術) on the label; 七支刀 = Seven-Branch. |

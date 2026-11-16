# ROM map (8 MiB, A7GJ)

Coarse, from `tools/re_lzsweep.py` coverage and a render of the first 2 KB of every 64 KB (`work/re/sweep/overview_000.png`). guess per region unless marked.

| Range | Content |
|---|---|
| 0x000000-0x04Cxxx | code (Thumb), literal pools (menu string pointers at 0x9FF4-0xA2A0) |
| 0x04C3F4-0x04CE2x | LZ77 blocks loaded at power-on (verified, lzlog) |
| 0x04CE4C-0x055BA5 | EUC-JP text (verified, `text.md`) |
| 0x05E2AC-0x061C58 | goal / province text, save-confirm string |
| 0x060000-0x07DFFF | LZ77 graphics blocks |
| 0x07E090-0x07EF1B | EUC-JP text: link mode, minigame |
| 0x080000-0x43FFFF | raw 4bpp graphics (sprites, portraits, effects); a Latin font around 0x200000; text 0x201800-0x202113 (results labels) |
| 0x440000-0x57FFFF | non-graphics (noise-like: sound samples / sequence data, guess) |
| 0x580000-0x68FFFF | LZ77 graphics blocks (screens: tiles + maps + palettes) |
| 0x690000-0x712127 | raw graphics with much Japanese text: menu labels (0x6D1FF8.., verified by vramfind on the file menu), stat labels, large kanji |
| 0x712128-0x719CE7 | text font, 990 x 32 bytes (verified) |
| 0x719CE8-0x72FFFF | raw graphics (title / Konami copyright strip) |
| 0x7303B8-0x746CE8 | event / script tables with text pointers (verified pointers) |
| 0x746CE8-0x759177 | tables (guess) |
| 0x759178-0x7C0B3F | 0xFF fill, **not free**: read into palette RAM by the magatama page's CpuSet (`english.md`) |
| 0x7C0B40-0x7FFFFF | 0xFF fill, free: text relocation 0x7C1000-0x7DFFFF, English engine 0x7E0000-0x7FFFFF |

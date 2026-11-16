# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| pixel art in `tools/font_en.py`, `tools/gfx_labels.py`, `tools/name_grid.py`, `tools/prose.py` | drawn for this project | MIT, same as repo | yes | text font, labels, name grid, prose cards | - |
| `fonts/Shojumaru-Regular.ttf` (sha1 85391cf2…) | https://github.com/google/fonts/tree/main/ofl/shojumaru (Astigmatic, 2012) | OFL 1.1 (`fonts/Shojumaru-OFL.txt`) | yes, as rendered glyphs | title logo (`tools/title_logo.py`, 25 and 20 px, no antialiasing) | none |

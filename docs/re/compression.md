# Compression

- **BIOS LZ77 (SWI 0x11, WRAM)** through one wrapper: `0x08048964(src)` reads the size from the header (`>>8`), allocates (`0x08047290`), then `svc 0x11` at 0x0804A620. 27 call sites (`disasm.py xref ... 08048964`). **verified** (disassembly + `tools/lua/lzlog.lua` logs real blocks).
- SWI 0x12 (LZ77 VRAM) exists at 0x0804CB78 but nothing calls it; no Huffman (0x13) or RL (0x14/0x15) SWIs in the first 512 KB of code. guess: LZ77 is the only scheme.
- Text strings are **not** compressed (see `text.md`).
- Blocks seen on the boot -> title -> new game -> opening route (`work/qa/explore2/log.txt`):
  - 0x04C4A0 (6336), 0x04CCBC (1200), 0x04C3F4 (512): loaded at power-on.
  - 0x5FD6AC / 0x5FCEFC / 0x5FCE74, 0x5A9254 / 0x5A91F4 / 0x5A9054, 0x585370 / 0x584D14 / 0x584CA8, 0x5AEA30 / 0x5AE37C / 0x5AE300: screen sets of 16384 (tiles) + 8208 (map?) + 160-192 (palette?). guess on the roles.
  - 0x60B7CC, 0x60A1F0, 0x609D74, 0x606D94, 0x5A282C, 0x5A0580, 0x59F8DC, 0x58C878: field / opening scene.
- Graphics live mostly in 0x580000-0x710000 (compressed blocks); the static sweep for graphics text decompresses them (`docs/re/graphics.md`).

-- Logs every LZ77 block the game decompresses: the wrapper at 0x08048964 takes the source in r0.
-- emu.py ... --script tools/lua/lzlog.lua   -> log.txt lines "lz f<frame> src=<rom offset> size=<bytes>"
local seen = {}
L.on_exec(0x08048964, 0x08048964, function()
  local s = emu.getState()
  local src = s["cpu.r0"]
  if src and not seen[src] then
    seen[src] = true
    local hdr = emu.read32(src, emu.memType.gbaMemory)
    L.log(string.format("lz f%d src=%06X size=%d", L.frame, src & 0x1FFFFFF, hdr >> 8))
  end
end)

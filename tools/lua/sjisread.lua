-- Who reads the name field (+12..+29) of the 40-byte Shift-JIS item records 0x0807F7A8..0x08080D44? One line per
-- distinct pc. Use: warp.py --script tools/lua/sjisread.lua SCENE..
local base, top, seen = 0x0807F7A8, 0x08080D44, {}
L.on_read(base, top, function(a)
  local f = (a - base) % 40
  if f < 12 or f >= 30 then return end
  local pc = L.pc()
  if seen[pc] then return end
  seen[pc] = true
  L.log(string.format("SJ %d pc=%08X addr=%08X field=%d", L.frame, pc, a, f))
end)

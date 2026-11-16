-- Logs game-mode changes: G = [0x03000000]; G+0 current mode, G+2 requested next mode (table at ROM 0x7301F0).
-- Also logs the event id at state+0x184 whenever the mode changes. "MODE frame cur=N next=N ev=N"
local mem = emu.memType.gbaMemory
local last = -1
L.on_frame(function(n)
  local g = emu.read32(0x03000000, mem)
  if g < 0x02000000 then return end
  local cur, nxt = emu.read(g, mem), emu.read(g + 2, mem)
  local key = cur * 256 + nxt
  if key ~= last then
    last = key
    local st = emu.read32(0x030016F0, mem) + 0x14
    L.log(string.format("MODE %d cur=%d next=%d ev=%d", n, cur, nxt, emu.read32(st + 0x184, mem)))
  end
end)

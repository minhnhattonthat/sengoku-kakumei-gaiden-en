-- Logs calls to the glyph lookup 0x080126C0 (r0 = code b0 | b1<<8): one line per distinct (lr, code) pair, at most
-- LOOKUP_MAX lines (default 400). Use: warp.py --script tools/lua/lookuplog.lua SCENE
local max, n, seen = LOOKUP_MAX or 400, 0, {}
L.on_exec(0x080126C0, 0x080126C0, function()
  if n >= max then return end
  local s = emu.getState()
  local r0, lr = s["cpu.r0"] & 0xFFFF, s["cpu.r14"]
  local k = lr * 65536 + r0
  if seen[k] then return end
  seen[k] = true
  n = n + 1
  L.log(string.format("LK %d code=%04X lr=%08X r1=%08X r2=%08X", L.frame, r0, lr, s["cpu.r1"], s["cpu.r2"]))
end)

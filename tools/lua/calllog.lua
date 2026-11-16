-- Logs calls to one function: CALL_AT (address, thumb bit off), one line per distinct (lr, r0, r1), at most
-- CALL_MAX lines (default 300), from frame CALL_FROM (default 0). Use:
--   warp.py --script tools/lua/calllog.lua --var CALL_AT=0x08011594 SCENE
local at = assert(CALL_AT, "set --var CALL_AT=0x...")
local max, from, n, seen = CALL_MAX or 300, CALL_FROM or 0, 0, {}
L.on_exec(at, at, function()
  if n >= max or L.frame < from then return end
  local s = emu.getState()
  local k = string.format("%08X %08X %08X", s["cpu.r14"], s["cpu.r0"], s["cpu.r1"])
  if seen[k] then return end
  seen[k] = true
  n = n + 1
  L.log(string.format("CALL %d lr=%08X r0=%08X r1=%08X r2=%08X r3=%08X", L.frame, s["cpu.r14"], s["cpu.r0"],
    s["cpu.r1"], s["cpu.r2"], s["cpu.r3"]))
end)

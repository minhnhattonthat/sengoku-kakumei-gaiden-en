-- Logs memcpy 0x0804C280(r0 dst, r1 src, r2 n) when dst or src is in CPY_LO..CPY_HI.
local lo, hi = CPY_LO, CPY_HI
L.on_exec(0x0804C280, 0x0804C280, function()
  local s = emu.getState()
  local d, sr = s["cpu.r0"], s["cpu.r1"]
  if (d >= lo and d <= hi) or (sr >= lo and sr <= hi) then
    L.log(string.format("CPY %d dst=%08X src=%08X n=%X lr=%08X", L.frame, d, sr, s["cpu.r2"], s["cpu.r14"]))
  end
end)

-- Logs BIOS SWI calls (vector 0x08) whose r0 or r1 is in SWI_LO..SWI_HI: "SWI frame r0 r1 r2 lr".
local lo, hi = SWI_LO or 0, SWI_HI or 0xFFFFFFFF
L.on_exec(0x00000008, 0x00000008, function()
  local s = emu.getState()
  local r0, r1 = s["cpu.r0"], s["cpu.r1"]
  if (r0 >= lo and r0 <= hi) or (r1 >= lo and r1 <= hi) then
    L.log(string.format("SWI %d r0=%08X r1=%08X r2=%08X lr=%08X", L.frame, r0, r1, s["cpu.r2"], s["cpu.r14"]))
  end
end)

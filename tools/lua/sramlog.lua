-- Logs SRAM copies: 0x0804A6B0(r0 = src, r1 = SRAM dst, r2 = bytes). "SRAMCPY frame src dst n lr".
L.on_exec(0x0804A6B0, 0x0804A6B0, function()
  local s = emu.getState()
  L.log(string.format("SRAMCPY %d src=%08X dst=%08X n=%X lr=%08X", L.frame, s["cpu.r0"], s["cpu.r1"], s["cpu.r2"], s["cpu.r14"]))
end)

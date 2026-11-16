-- Logs story-flag sets (0x08006A50 r0) and country-state writes (0x08006DE4 r0=id r1=value).
L.on_exec(0x08006A50, 0x08006A50, function()
  local s = emu.getState()
  L.log(string.format("SETFLAG %d flag=%d lr=%08X", L.frame, s["cpu.r0"], s["cpu.r14"]))
end)
L.on_exec(0x08006DE4, 0x08006DE4, function()
  local s = emu.getState()
  L.log(string.format("SETNIB %d id=%d v=%d lr=%08X", L.frame, s["cpu.r0"], s["cpu.r1"], s["cpu.r14"]))
end)

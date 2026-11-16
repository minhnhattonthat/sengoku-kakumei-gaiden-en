-- Logs task/scene creation: 0x08004720(r0, r1 = {a0, a1, a2, desc[6]}); desc = {?, size, init, update, draw, exit}.
-- Line: "TASK frame init=ADDR size=N a0=.. a1=.. a2=.. lr=..".
local function r32(a) return emu.read32(a, emu.memType.gbaMemory) end
L.on_exec(0x08004720, 0x08004720, function()
  local s = emu.getState()
  local p = s["cpu.r1"]
  L.log(string.format("TASK %d init=%08X size=%X a0=%08X a1=%08X a2=%08X r0=%08X lr=%08X",
    L.frame, r32(p + 0x14), r32(p + 0x10), r32(p), r32(p + 4), r32(p + 8), s["cpu.r0"], s["cpu.r14"]))
end)

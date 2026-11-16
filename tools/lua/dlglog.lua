-- Logs every dialogue list the game loads: 0x08012F70(r0 = null-terminated list of string pointers).
-- Line: "DLG frame list=ADDR caller=LR".
local keys
local function reg(s, n)
  if not keys then
    keys = {}
    for k, _ in pairs(s) do if k:match("^cpu%.r") then keys[#keys + 1] = k end end
    table.sort(keys)
    L.log("REGKEYS " .. table.concat(keys, " "))
  end
  return s["cpu.r" .. n] or s["cpu.r[" .. n .. "]"]
end
L.on_exec(0x08012F70, 0x08012F70, function()
  local s = emu.getState()
  L.log(string.format("DLG %d list=%08X lr=%08X", L.frame, reg(s, 0) or -1, reg(s, 14) or -1))
end)

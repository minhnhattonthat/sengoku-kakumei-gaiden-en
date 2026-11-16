-- Ryukyu dojo tutorial (mode 30, Kamiizumi's lessons; script/link.json 07eaac..07eef4) for text coverage.
-- The lesson state machine 0x08016FC4(obj) switches on state [obj+0x38] (0..17, jump table 0x08016FE0); text states
-- load a lesson list with 0x08012F70, wait states wait for the player's action (attack, charge, guard, arts,
-- weapon/art switch, dash). STUCK=N (default 500): when the state has not changed for N frames, step it to the next
-- state ([obj+0x30] = 0), so a route that only mashes A still reaches every lesson's text. Logs "DOJO state=<s>".
local mem = emu.memType.gbaMemory
local function r32(a) return emu.read32(a, mem) end
local function w32(a, v) emu.write32(a, v, mem) end
-- CTRL=n: the button-layout getter 0x080058A4 (settings word +0x10) returns n; the lessons for switching arts and
-- dashing have one text per layout (CTRL=0: 07ed2c/07ed48 SELECT and 07edcc/07ed94 double-tap; default build: R).
if CTRL then
  L.on_exec(0x080058B0, 0x080058B0, function() emu.setState({ ["cpu.r0"] = tonumber(CTRL) }) end)
end
local stuck = tonumber(STUCK or 500)
local obj, last, since = nil, -1, 0
L.on_exec(0x08016FC8, 0x08016FC8, function()
  obj = emu.getState()["cpu.r4"]
  local s = r32(obj + 0x38)
  if s ~= last then
    L.log(string.format("DOJO state=%d frame=%d", s, L.frame)); last = s; since = L.frame
  elseif L.frame - since > stuck and s < 17 then
    w32(obj + 0x38, s + 1); w32(obj + 0x30, 0)
    L.log(string.format("DOJO bump %d->%d frame=%d", s, s + 1, L.frame)); since = L.frame
  end
end)

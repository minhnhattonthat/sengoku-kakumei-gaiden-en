-- Item descriptions (script/system.json, 5 pointer lists at 0x7304E8 / 0x73055C / 0x7305D0 / 0x730474 / 0x730644,
-- drawn by the equip/shop help box from 0x0800A9AC(cat, item): the switch on cat 0-6 calls
-- idx = 0x0800B8F8(cat, item), loads the list with 0x08012F70(list) and draws page idx with 0x0801316C(idx) at
-- 0x0800AA7C (r4 = idx). Cats: 0 sword, 1 spear, 2 bow, 3 armour, 4-6 arts (all three use 0x730644).
-- Logs "DESC list=<addr> idx=<n>" on every draw. With --var STEP=1, each draw's index is replaced by the next one of
-- that list (0, 1, 2, ..., then it stops stepping), so moving the cursor N times draws N different descriptions in
-- the real box: a debug route to every description for text coverage and visual QA (warp scene item_desc).
local LISTS = { [0x087304E8] = 29, [0x0873055C] = 29, [0x087305D0] = 29, [0x08730474] = 29, [0x08730644] = 26 }
local nextIdx = {}
local lastList = nil
L.on_exec(0x08012F70, 0x08012F70, function()
  local list = emu.getState()["cpu.r0"]
  if LISTS[list] then lastList = list else lastList = nil end
end)
L.on_exec(0x0800AA7C, 0x0800AA7C, function()
  if not lastList then return end
  local idx = emu.getState()["cpu.r4"]
  if STEP then
    local k = nextIdx[lastList] or 0
    if k < LISTS[lastList] then
      emu.setState({ ["cpu.r4"] = k })
      idx = k
      nextIdx[lastList] = k + 1
    end
  end
  L.log(string.format("DESC list=%08X idx=%d frame=%d", lastList, idx, L.frame))
end)

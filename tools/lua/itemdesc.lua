-- Item descriptions (script/system.json, 5 pointer lists at 0x7304E8 / 0x73055C / 0x7305D0 / 0x730474 / 0x730644,
-- drawn by the equip/shop help box through the dialogue loader 0x08012F70(list, index) from 0x0800A9AC).
-- Logs "DESC list=<addr> idx=<n>" on every call. With --var STEP=1, each call's index is replaced by the next
-- one of that list (0, 1, 2, ...), so moving the cursor N times draws N different descriptions in the real box:
-- a debug route to every description for text coverage and visual QA (warp scene item_desc).
local LISTS = { [0x087304E8] = 29, [0x0873055C] = 29, [0x087305D0] = 29, [0x08730474] = 29, [0x08730644] = 26 }
local nextIdx = {}
L.on_exec(0x08012F70, 0x08012F70, function()
  local s = emu.getState()
  local list, idx = s["cpu.r0"], s["cpu.r1"]
  local n = LISTS[list]
  if not n then return end
  if STEP then
    local k = nextIdx[list] or 0
    if k < n then
      emu.setState({ ["cpu.r1"] = k })
      idx = k
      nextIdx[list] = k + 1
    end
  end
  L.log(string.format("DESC list=%08X idx=%d frame=%d", list, idx, L.frame))
end)

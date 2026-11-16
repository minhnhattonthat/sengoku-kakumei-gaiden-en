-- Step the page index of one dialogue list, for text coverage and visual QA of lists drawn one page at a time.
--   --script tools/lua/liststep.lua --var LIST=0x08731448 [--var N=51] [--var STEP=1]
-- The dialogue loader 0x08012F70(list) loads a pointer list; 0x0801316C(idx) then draws page idx of it. Every call
-- of 0x0801316C while LIST is the loaded list is logged ("PAGE list=<addr> idx=<n>"); with STEP=1 its index is
-- replaced by 0, 1, 2, ... N-1 (then left alone), so each redraw the game makes (hero moving on the map, cursor
-- moving in a menu) shows the next page. Used by scene provinces (LIST 0x08731448, the map help box).
local list = tonumber(LIST)
local n = tonumber(N or 999)
local loaded = nil
local k = 0
-- SWAP=0x0873xxxx: the first story-event dialogue group the game loads (a list in 0x08730830..0x087311FF) is
-- replaced by this group, so an event scene run with warp's PAGES=N pages through a group that only a story-flag
-- branch would show (text coverage of conditional groups; the box and renderer are the game's own).
local swap = SWAP and tonumber(SWAP)
L.on_exec(0x08012F70, 0x08012F70, function()
  loaded = emu.getState()["cpu.r0"]
  if swap and loaded >= 0x08730830 and loaded < 0x08731200 and L.frame >= tonumber(AFTER or 0) then
    L.log(string.format("SWAP %08X -> %08X frame=%d", loaded, swap, L.frame))
    emu.setState({ ["cpu.r0"] = swap })
    loaded = swap; swap = nil
  end
  if VERBOSE then L.log(string.format("LOAD list=%08X lr=%08X frame=%d", loaded, emu.getState()["cpu.r14"] or 0, L.frame)) end
end)
L.on_exec(0x0801316C, 0x0801316C, function()
  local idx = emu.getState()["cpu.r0"]
  if VERBOSE then L.log(string.format("DRAW loaded=%08X idx=%d frame=%d", loaded or 0, idx, L.frame)) end
  if loaded ~= list then return end
  if STEP and k < n and L.frame >= tonumber(AFTER or 0) then  -- AFTER=frame: leave the boot's own draws alone
    emu.setState({ ["cpu.r0"] = k })
    idx = k
    k = k + 1
  end
  L.log(string.format("PAGE list=%08X idx=%d frame=%d", list, idx, L.frame))
end)

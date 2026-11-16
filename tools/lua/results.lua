-- Results screen (mode 36) titles for text coverage and visual QA (warp scene results_titles).
-- The results setup picks a random title: adjective pointer from table 0x746A18 (rows of 5) into [r7+0x14], noun
-- from table 0x746B08 into [r7+0x1C] (0x08039DF0..0x08039E68), then draws them from 0x08039E6A on.
-- STEP=1: at 0x08039E6A the k-th adjective and k-th noun of those tables are written instead (k = 0, 1, ...).
-- LOOP=1: keep the next mode G+2 = 36, so pressing A on the results re-enters mode 36 and draws the next title.
-- Logs "TITLE k=<k> adj=<addr> noun=<addr>" on every draw.
local mem = emu.memType.gbaMemory
local function r32(a) return emu.read32(a, mem) end
local function w32(a, v) emu.write32(a, v, mem) end
local function w8(a, v) emu.write(a, v, mem) end
local function r8(a) return emu.read(a, mem) end
local function tbl(lo, hi)
  local t = {}
  for a = lo, hi, 4 do t[#t + 1] = r32(0x08000000 + a) end
  return t
end
local ADJ = tbl(0x746A18, 0x746B04)
local NOUN = tbl(0x746B08, 0x746CE4)
-- RANK=n: the rank label picks table 0x7469F8 entry 0 (> 0x32), 1 (> 0x28), 2 (> 0x16) or 3 from the value compared
-- at 0x08039FC6; force it to n (RANK=0x33 / 0x29 / 0x17 show the other three ranks).
if RANK then
  L.on_exec(0x08039FC6, 0x08039FC6, function() emu.setState({ ["cpu.r0"] = tonumber(RANK) }) end)
end
local k = 0
L.on_exec(0x08039E6A, 0x08039E6A, function()
  local r7 = emu.getState()["cpu.r7"]
  local adj, noun = r32(r7 + 0x14), r32(r7 + 0x1C)
  if STEP then
    adj = ADJ[(k % #ADJ) + 1]; noun = NOUN[(k % #NOUN) + 1]
    w32(r7 + 0x14, adj); w32(r7 + 0x1C, noun)
  end
  L.log(string.format("TITLE k=%d adj=%08X noun=%08X frame=%d", k, adj, noun, L.frame))
  k = k + 1
end)
if LOOP then
  L.on_frame(function()
    if r8(0x03000000) == 36 and r8(0x03000002) ~= 36 then w8(0x03000002, 36) end
  end)
end

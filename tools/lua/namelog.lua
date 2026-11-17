-- Name entry probe: log every write to the name buffer being edited (IWRAM 0x03001730.., u16 = grid index + 1,
-- docs/re/name-entry.md) with a screenshot, so a route that presses A on each cell maps cells to table indices.
--   emu.py ROM --state-in work/states/onmyou_name_input.mss --route R --script tools/lua/namelog.lua --out D
local shots = {}
L.on_write(0x03001730, 0x0300174F, function(addr, value)
  L.log(string.format("f%d addr=%08X value=%d", L.frame, addr, value))
  if value ~= 0 and not shots[L.frame] then
    shots[L.frame] = true
    L.shot(string.format("w%06d.png", L.frame))
  end
end)

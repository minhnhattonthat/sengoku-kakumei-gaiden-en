-- Warp to a scene from a cold boot. Sengoku Kakumei Gaiden (GBA, A7GJ).
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='name'" --var "SCENES=[[abs/tools/debug/scenes.txt]]"
--          --frames N --sheet
-- Opt-in globals: GOD=1 (pin player HP), HOLD=frames to keep running after the scene's inputs (default 600).
--
-- How (docs/re/scenes.md): mash A from boot through the new-game setup and the opening talk until the national
-- map's init (0x0800FCD4) runs. At that moment write the scene's story state into the game state struct
-- ([0x030016F0] + 0x14): story flags (bitfield at +0x164), country states (nibbles at +0x128), money, and the
-- hero's map position (+0x19C/+0x1A0, taken from the map node table at ROM 0x5E7A0). Then play the scene's
-- inputs (usually "A" = enter the country under the hero) and log "SCENE_OK" when the scene's marker fires.
local mem = emu.memType.gbaMemory
local function r32(a) return emu.read32(a, mem) end
local function w32(a, v) emu.write32(a, v, mem) end
local function r8(a) return emu.read(a, mem) end
local function w8(a, v) emu.write(a, v, mem) end
local function state() return r32(0x030016F0) + 0x14 end

-- ---------- scene list ----------
local function parse_scenes(path)
  local t = {}
  for line in io.lines(path) do
    local l = line:gsub("#.*", "")
    local name, rest = l:match("^%s*(%S+)%s*(.-)%s*$")
    if name and name ~= "" then
      local e = { name = name }
      for k, v in rest:gmatch('(%w+)=(%b"")') do e[k] = v:sub(2, -2) end
      for k, v in rest:gmatch('(%w+)=([^%s"]+)') do e[k] = e[k] or v end
      t[name] = e
    end
  end
  return t
end
local scenes = parse_scenes(assert(SCENES, "set --var SCENES=[[abs path of tools/debug/scenes.txt]]"))
local sc = assert(scenes[SCENE], "unknown SCENE " .. tostring(SCENE))
L.log("WARP " .. sc.name)

local function list(s)
  local t = {}
  for x in (s or ""):gmatch("[^,]+") do t[#t + 1] = x end
  return t
end
local function num(s) return tonumber(s) end

-- map node table: country id k -> hero position (x2, y2) of entry k
local function node(k)
  local base = 0x0805E7A0 + 32 * k
  return r32(base + 8), r32(base + 12)
end

local function set_flag(n) local a = state() + 0x164 + (n >> 3); w8(a, r8(a) | (1 << (n & 7))) end
local function set_nib(id, v)
  local a = state() + 0x128 + (id >> 1)
  local b = r8(a)
  if id & 1 == 1 then b = (b & 0xF0) | v else b = (b & 0x0F) | (v << 4) end
  w8(a, b)
end

local function apply_state(quiet)
  local s = state()
  -- flag ranges "a-b" allowed
  for _, f in ipairs(list(sc.flags)) do
    local a, b = f:match("^(%d+)%-(%d+)$")
    if a then for n = num(a), num(b) do set_flag(n) end else set_flag(num(f)) end
  end
  for _, kv in ipairs(list(sc.nib)) do
    local ids, v = kv:match("^(.-):(%d+)$")
    local a, b = ids:match("^(%d+)%-(%d+)$")
    if a then for id = num(a), num(b) do set_nib(id, num(v)) end else set_nib(num(ids), num(v)) end
  end
  for _, kv in ipairs(list(sc.poke)) do  -- poke=+OFF:VALUE (u32 into the state struct) or 0xADDR:VALUE
    local a, v = kv:match("^(.-):(.-)$")
    if a:sub(1, 1) == "+" then a = s + tonumber(a:sub(2)) else a = tonumber(a) end
    w32(a, tonumber(v))
  end
  if not quiet then
    L.log(string.format("STATE applied frame=%d S=%08X pos=%d,%d", L.frame, s, r32(s + 0x19C), r32(s + 0x1A0)))
  end
end

-- ---------- blank SRAM: a save left in tools/mesen/Saves by any earlier run turns the title's A into
-- "Continue" and the warp lands somewhere else. Wipe it before the game reads it (unless KEEPSAV=1).
if not KEEPSAV then
  local st = emu.memType.gbaSaveRam
  for a = 0, 0x7FFF do emu.write(a, 0xFF, st) end
  L.log("SRAM wiped")
end

-- ---------- phases ----------
local forcing, evforce = nil, nil
local phase = "boot"   --boot -> map -> inputs -> hold
local mapReady, t0 = nil, 0
-- path=a,b,c: countries entered first, in order (A on each, mash A through what follows), to play story
-- events the way the game does; each return to the map moves the hero to the next one, then to country=.
local path, pathi = list(sc.path), 0
local function put_hero(id)
  local s, x, y = state(), node(id)
  w32(s + 0x19C, x); w32(s + 0x1A0, y)
end
-- The map reads the hero position before its init (0x0800FCD4) runs, so the next target is written every frame
-- while another mode runs (next_target), and the init only advances the path.
local function next_target()
  if pathi + 1 <= #path then return num(path[pathi + 1]) end
  return num(sc.country)
end
L.on_exec(0x0800FCD4, 0x0800FCD4, function()
  if phase == "boot" then apply_state() end
  if phase == "boot" or phase == "path" then
    pathi = pathi + 1
    if pathi <= #path then
      phase = "path"; mapReady = L.frame
      L.log(string.format("PATH %d country=%s frame=%d", pathi, path[pathi], L.frame))
    else
      phase = "map"; mapReady = L.frame
    end
  end
end)
L.on_frame(function()
  if phase ~= "boot" and phase ~= "path" then return end
  local g = r32(0x03000000)
  if g < 0x02000000 or r32(0x030016F0) < 0x02000000 or r8(g) == 25 then return end
  local t = next_target()
  if t and (phase == "path" or r8(g) == 24) then put_hero(t) end
end)

if sc.marker then  -- marker=0xADDR : exec address that proves the scene was reached
  local m = tonumber(sc.marker)
  local seen = false
  L.on_exec(m, m, function()
    if not seen then seen = true; L.log(string.format("SCENE_OK %s frame=%d", sc.name, L.frame)) end
  end)
end

-- god mode: player HP lives in the stage task; pinned once known (docs/re/scenes.md)
-- expect=MODE[:EV]: the scene is proven when the game mode (and event id) match after the inputs start
local proven = false
L.on_frame(function(n)
  if proven or not sc.expect or (phase ~= "inputs" and phase ~= "hold") then return end
  local m, e = sc.expect:match("^(%d+):?(%d*)$")
  local g = r32(0x03000000)
  if r8(g) == num(m) and (e == "" or r32(state() + 0x184) == num(e)) then
    proven = true
    L.log(string.format("SCENE_OK %s frame=%d", sc.name, n))
  end
end)
L.on_frame(function(n)
  if evforce then
    local g = r32(0x03000000)
    w32(state() + 0x184, evforce)
    if r8(g) == 24 then L.log(string.format("EV_OK %d frame=%d", evforce, n)); evforce = nil end
  end
  if forcing then
    local g = r32(0x03000000)
    if r8(g) == forcing then
      L.log(string.format("MODE_OK %d frame=%d", forcing, n)); forcing = nil
    else
      w8(g + 2, forcing)
    end
  end
  if phase == "boot" and sc.route then
    -- route="N btn;..": title-side scenes (title menu, new-game setup, link mode): plain inputs from power-on
    phase = "inputs"
    for step in sc.route:gmatch("[^;]+") do
      local k, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
      L.press(spec, num(k))
    end
    if sc.mode then forcing = num(sc.mode) end
    return
  end
  if phase == "boot" then
    if n % 40 < 6 then L.press("a", 1) end
    -- the opening event (mode 24) writes the hero's start position: keep our state on top of it
    local g = r32(0x03000000)
    if g >= 0x02000000 and r8(g) == 24 and r32(0x030016F0) >= 0x02000000 then apply_state(true) end
    return
  end
  if phase == "path" then
    if n - mapReady >= 150 and n % 40 < 6 then L.press("a", 1) end
    return
  end
  if phase == "map" and n - mapReady >= (num(sc.wait) or 150) then
    phase = "inputs"
    if sc.ev then evforce = num(sc.ev) end  -- event id read by mode 24; the castle chooser writes its own on A
    -- mode=N: the map only leaves when a country is entered, and it then writes its own next mode; so keep
    -- overwriting G+2 every frame until the current mode G+0 becomes N (input should enter a country, e.g. A).
    if sc.mode then forcing = num(sc.mode) end
    for step in (sc.input or "6 a"):gmatch("[^;]+") do
      local k, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
      L.press(spec, num(k))
    end
    t0 = n
    return
  end
  if phase == "inputs" and L.route_done() then
    phase = "hold"; t0 = n
    L.log(string.format("INPUTS done frame=%d", n))
  end
  if phase == "hold" and (sc.mash or "") ~= "" and n % num(sc.mash) < 6 then L.press(sc.mashkey or "a", 1) end
  if phase == "hold" and n - t0 >= (num(HOLD) or num(sc.hold) or 600) then
    L.shot("scene_" .. sc.name .. ".png")
    L.log(string.format("DONE %s frame=%d", sc.name, n))
    phase = "end"
    if STATE_OUT then L.save_state(STATE_OUT, function() L.finish(0) end) else L.finish(0) end
  end
end)

"""Writes tools/debug/scenes.txt (run once; the file is then edited by hand)."""
HDR = """# Scene list for tools/debug/warp.lua (run: python -X utf8 tools/debug/warp.py [NAME..]). One scene per line:
#   NAME key=value ...
#   country=ID   hero on that country's map node, then the inputs (ids: docs/re/scenes.md)
#   path=a,b     countries entered first, in order, the game's own way (A, then A mashed until the map is back)
#   flags=a,b-c  story flags to set (bitfield at S+0x164); nib=ID:V country states (S+0x128)
#   poke=0xADDR:V absolute u32 writes (S = 0x02000614)
#   ev=N         force event id N (S+0x184) when the next scene starts (enter a castle: country=2)
#   mode=N       force game mode N (G = [0x03000000], G+2) when the map exits
#   route="N btn;.." title-side scene: plain inputs from power-on, no new game
#   input="N btn;.." presses once the map is up (default "6 a" = enter the country)
#   wait=N hold=N mash=N mashkey=b   timing; expect=MODE[:EV] proves the scene (logs SCENE_OK)
# ALL = every story flag and region flag: stages anywhere deploy without their region-intro events.
"""
ALL = "flags=1-24,33-90"
DEPLOY = 'input="6 a;200 -;6 a"'
L = [HDR]
add = L.append
add("# --- title side (no new game) ---")
add('title           route="900 -;6 start;200 -" hold=60')
add('newgame_setup   route="900 -;6 start;200 -;6 a;120 -;6 a;120 -" hold=200')
add('newgame_name    route="900 -;6 start;200 -;6 a;120 -;6 a;120 -;6 a;120 -;6 a;120 -;6 a;120 -" hold=200')
add('link_versus     route="900 -;6 start;200 -;6 left;60 -;6 a;200 -" hold=300')
add('link_lobby      route="900 -;6 start;200 -;6 left;60 -;6 a;200 -;6 a;300 -" hold=300')
add("# --- national map and its menu (Start) ---")
add('map             input="1 -" hold=120')
add('map_menu        input="6 start" hold=200')
add('equip           input="6 start;200 -;6 a" hold=300')
add('save            input="6 start;200 -;6 left;60 -;6 a" hold=300')
add('controls        input="6 start;200 -;6 left;60 -;6 left;60 -;6 a" hold=300')
add('encyclopedia    input="6 start;200 -;6 left;60 -;6 left;60 -;6 left;60 -;6 a" hold=300')
add('shop            input="6 start;200 -;6 left;60 -;6 left;60 -;6 left;60 -;6 left;60 -;6 a" hold=300')
add("# --- story path the game's own way (opening is played by every warp's boot) ---")
add('higo_barrier    country=4 mash=40 hold=900 expect=24:76')
add('lord_after_higo path=4 country=2 mash=40 hold=900 expect=24:2')
add('deploy_confirm  path=4,2 country=3 input="6 a" hold=300 expect=41')
add("# --- stages (field/HUD), one per region; Ryukyu = tutorial; mugen = endless ---")
for c, n in [(1, "ryukyu_tutorial"), (3, "r1_hyuga"), (9, "r2_tosa"), (17, "r3_izumo"), (23, "r4_echizen"),
             (28, "r5_kai"), (34, "r6_sagami"), (40, "r7_shimotsuke"), (43, "r8_uzen"), (46, "r8_mutsu")]:
    add(f"stage_{n:16s} country={c} {ALL} {DEPLOY} hold=900 expect=29")
add(f'stage_mugen             {ALL} poke=0x020007B0:732,0x020007B4:232 {DEPLOY} hold=900 expect=29')
add("# --- screens the game switches to by mode ---")
add(f"results         country=2 {ALL} mode=36 hold=400 expect=36")
add(f"game_over       country=2 {ALL} mode=21 hold=400 expect=21")
add(f"link_failed     country=2 mode=22 hold=400 expect=22")
add(f"link_timesel    country=2 mode=20 hold=400 expect=20")
add(f"link_lobby_m    country=2 mode=19 hold=400 expect=19")
add(f"ending_petals   country=2 mode=34 hold=400 expect=34")
add(f"debug_menu      country=2 mode=0 hold=400 expect=0   # leftover debug menu (debug only)")
add("# --- ending: ev 53 chains 53..74: epilogue, the four prose screens (LZ 0x5C84F0, 0x5CA354, 0x5C5DB8,")
add("#     0x5C3598), staff credits and the end card; holds land just after each prose screen loads ---")
add("ending_prose1   country=2 ev=53 mash=40 hold=3450 expect=24:53")
add("ending_prose2   country=2 ev=53 mash=40 hold=5520 expect=24:53")
add("ending_prose3   country=2 ev=53 mash=40 hold=9640 expect=24:53")
add("ending_prose4   country=2 ev=53 mash=40 hold=12090 expect=24:53")
add("ending_credits  country=2 ev=53 mash=40 hold=13000 expect=24:53")
add("ending_end      country=2 ev=53 mash=40 hold=14400 expect=24:53")
add("# --- every story event (castle talks, region events, boss intros, magatama, biographies) ---")
names = {0: "opening", 1: "lord_hint", 2: "lord_barrier", 21: "oichi", 22: "honnoji", 53: "epilogue",
         73: "resume", 74: "resume2", 75: "save_confirm", 76: "higo_barrier"}
for e in list(range(0, 69)) + list(range(73, 113)):
    tag = names.get(e, "")
    if 92 <= e <= 103:
        tag = "biography"
    elif 77 <= e <= 83:
        tag = "barrier_break"
    elif 105 <= e <= 112:
        tag = "magatama"
    elif e in (51, 84, 85, 86, 88, 89, 90, 91, 104):
        tag = "boss"
    nm = f"ev{e:03d}" + (f"_{tag}" if tag else "")
    add(f"{nm:24s} country=2 ev={e} mash=40 hold=2400 expect=24:{e}")
open("tools/debug/scenes.txt", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")

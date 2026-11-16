"""Run tools/debug/warp.lua for one, several or all scenes from a cold boot, in parallel.

usage: python -X utf8 tools/debug/warp.py [SCENE ...] [--rom ROM] [--out work/qa/warp] [--jobs 4] [--states]
       [--var NAME=LUA ...]
No SCENE = every scene in tools/debug/scenes.txt. Each scene gets work/qa/warp/<scene>/ with shots, a sheet,
log.txt and scene_<name>.png; --states also saves work/states/<scene>.mss at the end. Exit 1 if any scene
did not log DONE (or did not log SCENE_OK when it has a marker).
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCENES = os.path.join(ROOT, "tools", "debug", "scenes.txt")


def scene_names():
    out = []
    for line in open(SCENES, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line.split()[0])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--rom", default=os.path.join(ROOT, "rom", "Sengoku Kakumei Gaiden (Japan).gba"))
    ap.add_argument("--out", default=os.path.join(ROOT, "work", "qa", "warp"))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--states", action="store_true")
    ap.add_argument("--shot-every", default="120")
    ap.add_argument("--var", action="append", default=[])
    ap.add_argument("--script", action="append", default=[], help="extra Lua probe, e.g. tools/lua/modelog.lua")
    ap.add_argument("--scenes-file", default=None, help="another scene list (default tools/debug/scenes.txt)")
    a = ap.parse_args()
    global SCENES
    if a.scenes_file:
        SCENES = os.path.abspath(a.scenes_file)
    skill = subprocess.check_output([sys.executable, os.path.join(ROOT, "tools", "skill.py")], text=True).strip()
    names = a.scenes or scene_names()
    marked = {l.split()[0] for l in open(SCENES, encoding="utf-8")
              if l.split("#", 1)[0].strip() and ("marker=" in l.split("#", 1)[0] or "expect=" in l.split("#", 1)[0])}

    def run(name):
        out = os.path.join(a.out, name)
        cmd = [sys.executable, "-X", "utf8", os.path.join(skill, "scripts", "emu.py"), a.rom, "--out", out,
               "--script", os.path.join(ROOT, "tools", "debug", "warp.lua"),
               "--var", f"SCENE='{name}'", "--var", f"SCENES=[[{SCENES}]]",
               "--frames", "60000", "--timeout", "900", "--shot-every", a.shot_every, "--sheet"]
        for v in a.var:
            cmd += ["--var", v]
        for s in a.script:
            cmd += ["--script", os.path.abspath(s)]
        if a.states:
            cmd += ["--state-out", os.path.join(ROOT, "work", "states", name + ".mss")]
        p = subprocess.run(cmd, capture_output=True, text=True)
        log = open(os.path.join(out, "log.txt"), encoding="utf-8", errors="replace").read() \
            if os.path.exists(os.path.join(out, "log.txt")) else ""
        ok = "DONE " in log and (name not in marked or "SCENE_OK" in log)
        return name, ok, p.returncode

    bad = 0
    with ThreadPoolExecutor(a.jobs) as ex:
        for name, ok, rc in ex.map(run, names):
            print(f"{'ok  ' if ok else 'FAIL'} {name} (emu exit {rc})")
            bad += not ok
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

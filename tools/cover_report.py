"""Text coverage per bank, over several warp/tour log dirs at once.

    python -X utf8 tools/cover_report.py LOGDIR.. [--strings build/strings.tsv] [--unshown OUT.tsv] [--bank B]

Reads every log.txt under each LOGDIR for "TEXT <hex addr>" lines (lua/probes/textcover.lua), matches them
against build/strings.tsv (id, read address) the way $SKILL/scripts/textcover.py does (--mask 0x7FFFFF), and prints
shown/total per script bank (script/<bank>.json, only strings the build lists). --unshown writes
"id<TAB>bank<TAB>jp" for every string never shown; --bank limits that list to one bank.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASK = 0x7FFFFF


def shown_addrs(dirs):
    pat = re.compile(r"^TEXT ([0-9A-Fa-f]+)")
    seen = set()
    for d in dirs:
        for base, _, files in os.walk(d):
            if "log.txt" not in files:
                continue
            with open(os.path.join(base, "log.txt"), encoding="utf8", errors="replace") as f:
                for line in f:
                    m = pat.match(line)
                    if m:
                        seen.add(int(m.group(1), 16) & MASK)
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logdirs", nargs="+")
    ap.add_argument("--strings", default=os.path.join(ROOT, "build", "strings.tsv"))
    ap.add_argument("--unshown")
    ap.add_argument("--bank")
    a = ap.parse_args()
    addr = {}
    with open(a.strings, encoding="utf8") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                addr[p[0]] = int(p[1], 16) & MASK
    bank_of, jp_of = {}, {}
    sdir = os.path.join(ROOT, "script")
    for fn in sorted(os.listdir(sdir)):
        if fn.endswith(".json"):
            for e in json.load(open(os.path.join(sdir, fn), encoding="utf8")):
                bank_of[e["id"]] = fn[:-5]
                jp_of[e["id"]] = e.get("jp", "")
    seen = shown_addrs(a.logdirs)
    tot, ok, unshown = {}, {}, []
    for sid, ad in addr.items():
        b = bank_of.get(sid, "?")
        tot[b] = tot.get(b, 0) + 1
        if ad in seen:
            ok[b] = ok.get(b, 0) + 1
        else:
            unshown.append((sid, b))
    for b in sorted(tot):
        print(f"{b:14} {ok.get(b, 0):4}/{tot[b]}")
    print(f"{'total':14} {sum(ok.values()):4}/{sum(tot.values())}")
    if a.unshown:
        with open(a.unshown, "w", encoding="utf8", newline="\n") as f:
            for sid, b in unshown:
                if a.bank and b != a.bank:
                    continue
                f.write(f"{sid}\t{b}\t{jp_of.get(sid, '').replace(chr(10), ' ')}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

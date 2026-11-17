"""Write docs/text_unshown.tsv: the strings text coverage accepts as never shown, each with the reason it can't be.

    python -X utf8 tools/waivers.py UNSHOWN.tsv > docs/text_unshown.tsv

UNSHOWN.tsv is tools/cover_report.py --unshown output (id, bank, jp) over every coverage run. Each id must match one
rule below (proved unreachable in docs/re/coverage.md); an id no rule explains is printed to stderr and the exit is 1,
so a real gap can't be waived by accident.
"""
import sys

DEBUG_TEST = {"201800", "20180c", "201814"}
RESULTS_DEAD = {"201828", "201834", "201840", "201848", "201860", "201870", "20187c", "201890", "2018a0",
                "2018fc", "201904", "20190c"}
LINK_2GBA = {"07e0d0", "07e104", "07e124", "07e164", "07e180", "07e19c", "07e1d4", "07e20c", "07e274", "07e29c",
             "07e2d4", "07e2dc", "07e2e4", "07e2ec", "07e308", "07e340", "07e35c"}

# menu_help2 pages 0x29/0x2A ("sold out", "nothing I can buy"): the only pages of that list the game draws. In the
# manga-engine build every string stays at its own address, so these no longer share one with their twins (04cf20,
# 04cf00); the bytes are identical (tests/test_manga.py test_dups_match_their_twins).
MENU_HELP2_DRAWN = {"04fec4": "0x29", "04fea4": "0x2A"}


def reason(sid, bank):
    if sid in DEBUG_TEST:
        return "debug printout 0x08039440 (debug printer 0x08049AB8), not drawn in play"
    if sid in RESULTS_DEAD:
        return ("results: only entries 0-7 of label table 0x7469B0 and 0-3 of rank table 0x7469F8 are read "
                "(0x08039EA0..0x0803A01A); this kana/kanji twin is never indexed")
    if sid in LINK_2GBA:
        return "link versus setup (2-4 GBAs): drawn only in a live link session; forced modes 19/20 draw page 1 only"
    if sid in MENU_HELP2_DRAWN:
        return (f"menu_help2 page {MENU_HELP2_DRAWN[sid]} (shop, 0x0800BDEC/0x0800C160/0x0800C2F6) is drawn in play; "
                "the build writes it byte-identical to its menu_help1 twin, which the tour shows (reached, same bytes)")
    if bank == "menu_help2":
        return ("menu_help2 list 0x7306B0 is drawn only at pages 0x29/0x2A (0x0800BDEC, 0x0800C160, 0x0800C2F6); "
                "this page is never indexed (its menu_help1 twin is shown)")
    if sid == "061c1c":
        return "arrow glyphs kept Japanese (keep_jp.txt); pointer 0x731520 has no code reference"
    return None


def main():
    bad = 0
    for line in open(sys.argv[1], encoding="utf8"):
        p = line.rstrip("\n").split("\t")
        if len(p) < 2:
            continue
        r = reason(p[0], p[1])
        if r:
            print(f"{p[0]}\t{r}")
        else:
            print(f"not waivable: {line.strip()}", file=sys.stderr)
            bad = 1
    return bad


if __name__ == "__main__":
    sys.exit(main())

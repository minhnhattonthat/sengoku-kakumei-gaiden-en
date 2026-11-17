"""upright.py: English labels as upright letters stacked down a column (D17/D18, docs/decisions.md).

Used for the name-entry header and OK (tools/name_grid.py) and the link replay header (tools/link_card.py); the
sprite-bank labels went back to sideways in D19 (tools/gfx_labels.py). Narrow slots made for vertical Japanese:
upright capitals one under another, top to bottom; a label too long for one column continues in a second (and
third) column to the right, broken between words (a single word too long breaks at a syllable with a hyphen).
Two fonts: manga.FONT's condensed 3x7 caps (the scroll's lettering) and TINY, 3x5 caps for small slots. Spacing
down a column is proportional: a glyph takes its own ink height + GAP rows, a space SPACE rows.

    layout = stack(text, room, width)      -> Layout(points={(y, x)}, w, h, font, columns)
    python -X utf8 tools/upright.py --selftest
    python -X utf8 tools/upright.py TEXT ROOM WIDTH         print the layout as # art
"""
import sys
from collections import namedtuple
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manga  # noqa: E402

TINY_ART = {
    "A": ".#.|#.#|###|#.#|#.#", "B": "##.|#.#|##.|#.#|##.", "C": ".##|#..|#..|#..|.##", "D": "##.|#.#|#.#|#.#|##.",
    "E": "###|#..|##.|#..|###", "F": "###|#..|##.|#..|#..", "G": ".##|#..|#.#|#.#|.##", "H": "#.#|#.#|###|#.#|#.#",
    "I": "###|.#.|.#.|.#.|###", "J": "..#|..#|..#|#.#|.#.", "K": "#.#|#.#|##.|#.#|#.#", "L": "#..|#..|#..|#..|###",
    "M": "#...#|##.##|#.#.#|#...#|#...#", "N": "#..#|##.#|#.##|#..#|#..#", "O": ".#.|#.#|#.#|#.#|.#.",
    "P": "##.|#.#|##.|#..|#..", "Q": ".#.|#.#|#.#|##.|.##", "R": "##.|#.#|##.|#.#|#.#", "S": ".##|#..|.#.|..#|##.",
    "T": "###|.#.|.#.|.#.|.#.", "U": "#.#|#.#|#.#|#.#|###", "V": "#.#|#.#|#.#|#.#|.#.",
    "W": "#...#|#...#|#.#.#|##.##|#...#", "X": "#.#|#.#|.#.|#.#|#.#", "Y": "#.#|#.#|.#.|.#.|.#.",
    "Z": "###|..#|.#.|#..|###",
    "0": "###|#.#|#.#|#.#|###", "1": ".#.|##.|.#.|.#.|###", "2": "##.|..#|.#.|#..|###", "3": "##.|..#|.#.|..#|##.",
    "4": "#.#|#.#|###|..#|..#", "5": "###|#..|##.|..#|##.", "6": ".##|#..|###|#.#|###", "7": "###|..#|.#.|.#.|.#.",
    "8": "###|#.#|###|#.#|###", "9": "###|#.#|###|..#|##.",
    ".": "#", ",": "#|#", "-": "##", "'": "#|#", "!": "#|#|#|.|#", "?": "##.|..#|.#.|...|.#.", ":": "#|.|#",
    "/": "..#|..#|.#.|#..|#..", "&": ".#.|#.#|.#.|#.#|.##", "(": ".#|#.|#.|#.|.#", ")": "#.|.#|.#|.#|#.",
}
TINY = {ch: art.split("|") for ch, art in TINY_ART.items()}
FONTS = {"manga": manga.FONT, "tiny": TINY}
GAP = 1      # rows between glyphs in a column
SPACE = 3    # rows a space adds (on top of the gap)
COL_GAP = 2  # px between columns

Layout = namedtuple("Layout", "points w h font columns")


def fold(text):
    return manga.fold(text).upper()


def ink(ch, font="manga", sx=1, sy=1):
    """(points {(r, c)} trimmed to the glyph's ink, width, height) of one upright glyph, scaled sx by sy
    (sy may be a float: rows are resampled to round(7 * sy) etc.)."""
    art = FONTS[font].get(ch)
    if art is None:
        raise ValueError(f"no {font} glyph for {ch!r}")
    rows = [r for r, line in enumerate(art) if "#" in line]
    if not rows:
        return set(), 0, 0
    art = art[rows[0]:rows[-1] + 1]
    h0, w0 = len(art), len(art[0])
    h = max(1, round(h0 * sy))
    pts = set()
    for y in range(h):
        line = art[min(h0 - 1, int(y * h0 / h))]
        for c, px in enumerate(line):
            if px == "#":
                for dx in range(sx):
                    pts.add((y, c * sx + dx))
    return pts, w0 * sx, h


def column_length(word_list, font="manga", sx=1, sy=1, gap=GAP, space=SPACE):
    """Rows of words stacked in one column (no trailing gap)."""
    n = 0
    for k, w in enumerate(word_list):
        if k:
            n += space + gap
        for i, ch in enumerate(w):
            n += ink(ch, font, sx, sy)[2] + (gap if i < len(w) - 1 else 0)
    return n


def column_width(word_list, font="manga", sx=1, sy=1):
    return max((ink(ch, font, sx, sy)[1] for w in word_list for ch in w), default=0)


def _break_word(word, room, measure):
    """(head, tail) of a word too long for one column: after its own hyphen, else at a syllable with a hyphen
    added (>= 2 letters each side)."""
    for k in range(len(word) - 1, 0, -1):
        if word[k - 1] == "-" and measure([word[:k]]) <= room:
            return word[:k], word[k:]
    fits = [k for k in range(len(word) - 2, 1, -1) if measure([word[:k] + "-"]) <= room
            and word[k - 1].isalpha() and word[k].isalpha()]
    if not fits:
        return None
    k = next((k for k in fits if manga._syllable_break(word, k)), fits[0])
    return word[:k] + "-", word[k:]


def _columns(words, room, measure, split):
    """Greedy columns of whole words (or, `split`, words broken to fit); None if a word cannot fit."""
    cols, cur, todo = [], [], list(words)
    while todo:
        w = todo.pop(0)
        if measure(cur + [w]) <= room:
            cur.append(w)
            continue
        if cur:
            cols.append(cur)
            cur = []
            todo.insert(0, w)
            continue
        # also break at a hyphen inside the word when the word is too long
        parts = _break_word(w, room, measure) if split or "-" in w else None
        if not parts or (not split and not parts[0].endswith("-")):
            return None
        if not split and parts[0][:-1] + parts[1] != w:   # a hyphen was added: only with `split`
            return None
        cols.append([parts[0]])
        todo.insert(0, parts[1])
    if cur:
        cols.append(cur)
    return cols


def _balance(words, k, room, measure):
    """The split of `words` into k consecutive columns with the shortest longest column (ties: earlier columns
    longer), or None."""
    best = None

    def rec(i, left, acc):
        nonlocal best
        if left == 1:
            col = words[i:]
            if col and measure(col) <= room:
                cand = acc + [col]
                key = (max(measure(c) for c in cand), [-measure(c) for c in cand])
                if best is None or key < best[0]:
                    best = (key, cand)
            return
        for j in range(i + 1, len(words) - left + 2):
            col = words[i:j]
            if measure(col) > room:
                break
            rec(j, left - 1, acc + [col])
    rec(0, k, [])
    return best[1] if best else None


def place(cols, font="manga", sx=1, sy=1, col_gap=COL_GAP, gap=GAP, space=SPACE):
    """Layout of given columns (lists of words): columns left to right, each letter centred across its column."""
    pts = set()
    x, h = 0, 0
    for col in cols:
        cw = column_width(col, font, sx, sy)
        y = 0
        for k, w in enumerate(col):
            if k:
                y += space + gap
            for i, ch in enumerate(w):
                gp, gw, gh = ink(ch, font, sx, sy)
                dx = x + (cw - gw) // 2
                pts |= {(y + r, dx + c) for r, c in gp}
                y += gh + (gap if i < len(w) - 1 else 0)
        h = max(h, y)
        x += cw + col_gap
    return Layout(pts, x - col_gap if cols else 0, h, font, [" ".join(c) for c in cols])


def stack(text, room, width, fonts=("manga", "tiny"), max_cols=3, sx=1, sy=1, col_gap=COL_GAP, gap=GAP,
          space=SPACE, allow_split=True):
    """Upright stacked layout of `text` in at most `room` rows by `width` px of ink. Tries, in order: each font in
    one column, then more columns of whole words (balanced), then (`allow_split`) columns with words broken at a
    syllable. Explicit column breaks ('/' in the text) override the word fill."""
    t = fold(text).strip()
    if not t:
        return Layout(set(), 0, 0, fonts[0], [])
    tries = []
    for split_words in (False, True) if allow_split else (False,):
        for font in fonts:
            for k in range(1, max_cols + 1):
                tries.append((font, k, split_words))
    for font, k, split_words in tries:
        def measure(ws, font=font):
            return column_length(ws, font, sx, sy, gap, space)
        if "/" in t:
            cols = [p.split() for p in t.split("/")]
            if len(cols) != k or split_words:
                continue
        else:
            words = t.split()
            cols = _balance(words, k, room, measure) if not split_words else None
            if cols is None and split_words:
                cols = _columns(words, room, measure, True)
                if cols and len(cols) != k:
                    cols = None
        if not cols or any(measure(c) > room for c in cols):
            continue
        lay = place(cols, font, sx, sy, col_gap, gap, space)
        if lay.w <= width:
            return lay
    raise ValueError(f"{text!r} does not fit {room} rows x {width} px upright")


def line_width(s, font="tiny", gap=1):
    return sum(ink(ch, font)[1] + gap if ch != " " else SPACE for ch in s) - gap


def lines(rows, font="tiny", gap=1, line_gap=1):
    """Layout of short horizontal lines, upright, stacked down and each centred across (cap height rows each)."""
    h = 5 if font == "tiny" else 7
    w = max(line_width(r, font, gap) for r in rows)
    pts = set()
    for k, r in enumerate(rows):
        x = (w - line_width(r, font, gap)) // 2
        for ch in r:
            if ch == " ":
                x += SPACE
                continue
            art = FONTS[font][ch]
            for y, line in enumerate(art):
                for c, px in enumerate(line):
                    if px == "#":
                        pts.add((k * (h + line_gap) + y + (h - len(art) if ch in ".,_" else 0), x + c))
            x += len(art[0]) + gap
    return Layout(pts, w, len(rows) * (h + line_gap) - line_gap, font, list(rows))


def syllables(name):
    """Hepburn syllables of a romanized name: (consonants) vowel (+ a syllable-final N); a doubled consonant or
    the T of TCH closes the syllable before it (SET-TSU, BIT-CHU)."""
    import re
    sy = re.findall(r"[^AEIOU]*[AEIOU](?:N(?![AEIOUY]))?|[^AEIOU]+$", name.upper())
    for k in range(1, len(sy)):
        s = sy[k]
        if len(s) > 2 and (s[0] == s[1] or s.startswith("TCH")) and s[0] not in "AEIOU":
            sy[k - 1] += s[0]
            sy[k] = s[1:]
    return sy


def shadow(points, dirs=((0, 1), (1, 0), (1, 1))):
    """Pixels one step right/down of the ink (an upright drop shadow), not on the ink."""
    return {(y + dy, x + dx) for y, x in points for dy, dx in dirs} - set(points)


def edge(points):
    """8-neighbour ring around the ink."""
    return {(y + dy, x + dx) for y, x in points for dy in (-1, 0, 1) for dx in (-1, 0, 1)} - set(points)


def art(lay):
    if not lay.points:
        return ""
    return "\n".join("".join("#" if (y, x) in lay.points else "." for x in range(lay.w)) for y in range(lay.h))


def _selftest():
    for font in FONTS.values():
        for ch, a in font.items():
            assert len({len(r) for r in a}) == 1, ch
    lay = stack("Save", 40, 14)
    assert (lay.font, lay.columns, lay.h, lay.w) == ("manga", ["SAVE"], 31, 3), lay[1:]
    lay = stack("Ashigaru Armor", 70, 14)
    assert lay.columns == ["ASHIGARU", "ARMOR"] and lay.w == 3 + COL_GAP + 5, lay[1:]  # M is 5 wide
    lay = stack("HEALTH", 37, 7)
    assert lay.font == "tiny" and lay.h == 35, lay[1:]
    lay = stack("Encyclopedia", 88, 14)
    assert lay.font == "tiny" and lay.columns == ["ENCYCLOPEDIA"], lay[1:]
    lay = stack("SHIMO/TSUKE", 30, 14, fonts=("tiny",))
    assert lay.columns == ["SHIMO", "TSUKE"] and lay.h == 29, lay[1:]
    lay = stack("Seven-Branch Sword", 78, 14)
    assert (lay.font, lay.columns) == ("tiny", ["SEVEN-BRANCH", "SWORD"]), lay[1:]
    lay = stack("Grand Chamberlain", 70, 14)
    assert (lay.font, lay.columns) == ("manga", ["GRAND", "CHAMBER-", "LAIN"]) or lay.font == "tiny", lay[1:]
    try:
        stack("Supercalifragilistic", 10, 4)
        raise AssertionError("should not fit")
    except ValueError:
        pass
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        _selftest()
    else:
        lay = stack(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
        print(lay.font, lay.columns, f"{lay.w}x{lay.h}")
        print(art(lay))

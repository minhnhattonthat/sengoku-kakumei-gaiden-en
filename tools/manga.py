"""manga.py: the manga-bubble text style (second patch variant, D16 in docs/decisions.md, docs/re/manga.md).

The pink scroll (mode 0 of the reader 0x08011DDC) shows English upright, in short centred lines of condensed
ALL-CAPS lettering stacked down the tall scroll, like a scanlation's vertical speech bubble. Each line is cut at
build time into slices of at most 16 px of ink (one font entry = one OBJ, so a slice is one of the 36 sprite slots a
page has); the engine (tools/manga_engine.py) advances x by each slice's width, starts a new line at `|n`, and
centres every line and the whole block in the scroll at run time, so `%n` (the player name, drawn letter by letter
from the name-grid glyphs) can sit anywhere in a line.

    python -X utf8 tools/manga.py --selftest
    python -X utf8 tools/manga.py --sheet OUT.png [ID ...]      render pages as the engine lays them out
    python -X utf8 tools/manga.py --fit                         pages over the line, row or slot limits

Encoding of a page: slice codes (b0 0x01-0x24, b1 0x01-0xFF: never NUL, '%' 0x25, '|' 0x7C, nor the English pair
codes 0x80-0x9F or EUC), `|n` between lines, `%n %b %B %r` passed through.
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Condensed caps, cap height 7 (rows 0-6), descenders rows 7-8. Width = the art's width; advance = width + 1.
_ART = r"""
A .#. #.# #.# ### #.# #.# #.#
B ##. #.# #.# ##. #.# #.# ##.
C .## #.. #.. #.. #.. #.. .##
D ##. #.# #.# #.# #.# #.# ##.
E ### #.. #.. ##. #.. #.. ###
F ### #.. #.. ##. #.. #.. #..
G .## #.. #.. #.# #.# #.# .##
H #.# #.# #.# ### #.# #.# #.#
I # # # # # # #
J ..# ..# ..# ..# ..# #.# .#.
K #.# #.# ##. #.. ##. #.# #.#
L #.. #.. #.. #.. #.. #.. ###
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #..# ##.# ##.# #.## #.## #..# #..#
O .#. #.# #.# #.# #.# #.# .#.
P ##. #.# #.# ##. #.. #.. #..
Q .#. #.# #.# #.# #.# ##. .##
R ##. #.# #.# ##. #.# #.# #.#
S .## #.. #.. .#. ..# ..# ##.
T ### .#. .#. .#. .#. .#. .#.
U #.# #.# #.# #.# #.# #.# ###
V #.# #.# #.# #.# #.# .#. .#.
W #...# #...# #...# #.#.# #.#.# ##.## #...#
X #.# #.# #.# .#. #.# #.# #.#
Y #.# #.# #.# .#. .#. .#. .#.
Z ### ..# ..# .#. #.. #.. ###
a ... ... ##. ..# .## #.# .##
b #.. #.. ##. #.# #.# #.# ##.
c ... ... .## #.. #.. #.. .##
d ..# ..# .## #.# #.# #.# .##
e ... ... .#. #.# ### #.. .##
f .## #.. ##. #.. #.. #.. #..
g ... ... .## #.# #.# #.# .## ..# ##.
h #.. #.. ##. #.# #.# #.# #.#
i # . # # # # #
j .# .. .# .# .# .# .# .# #.
k #.. #.. #.# ##. #.. ##. #.#
l #. #. #. #. #. #. .#
m ..... ..... ####. #.#.# #.#.# #.#.# #.#.#
n ... ... ##. #.# #.# #.# #.#
o ... ... .#. #.# #.# #.# .#.
p ... ... ##. #.# #.# #.# ##. #.. #..
q ... ... .## #.# #.# #.# .## ..# ..#
r ... ... #.# ##. #.. #.. #..
s ... ... .## #.. .#. ..# ##.
t ... .#. ### .#. .#. .#. ..#
u ... ... #.# #.# #.# #.# .##
v ... ... #.# #.# #.# .#. .#.
w ..... ..... #...# #...# #.#.# #.#.# .#.#.
x ... ... #.# #.# .#. #.# #.#
y ... ... #.# #.# #.# #.# .## ..# ##.
z ... ... ### ..# .#. #.. ###
0 ### #.# #.# #.# #.# #.# ###
1 .#. ##. .#. .#. .#. .#. ###
2 ##. ..# ..# .#. #.. #.. ###
3 ##. ..# ..# .#. ..# ..# ##.
4 #.# #.# #.# ### ..# ..# ..#
5 ### #.. #.. ##. ..# ..# ##.
6 .## #.. #.. ##. #.# #.# .#.
7 ### ..# ..# .#. .#. .#. .#.
8 .#. #.# #.# .#. #.# #.# .#.
9 .#. #.# #.# .## ..# ..# ##.
. . . . . . . #
, .. .. .. .. .. .. .# #.
! # # # # # . #
? ##. ..# ..# .#. .#. ... .#.
' # # . . . . .
" #.# #.# ... ... ... ... ...
- ... ... ... ### ... ... ...
: . . # . . . #
; .. .. .# .. .. .. .# #.
( .# #. #. #. #. #. .#
) #. .# .# .# .# .# #.
& .#.. #.#. #.#. .#.. #.## #.#. .#.#
/ ..# ..# .#. .#. .#. #.. #..
~ .... .... .#.# #.#. .... .... ....
+ ... ... .#. ### .#. ... ...
* ... #.# .#. #.# ... ... ...
= ... ... ### ... ### ... ...
% #.# ..# .#. .#. .#. #.. #.#
# .#.#. .#.#. ##### .#.#. ##### .#.#. .#.#.
$ .#. .## #.. .#. ..# ##. .#.
@ .###. #...# #.### #.#.# #.### #.... .###.
[ ## #. #. #. #. #. ##
] ## .# .# .# .# .# ##
< ... ..# .#. #.. .#. ..# ...
> ... #.. .#. ..# .#. #.. ...
_ ... ... ... ... ... ... ... ###
^ .#. #.# ... ... ... ... ...
` #. .# .. .. .. .. ..
{ .## .#. .#. #.. .#. .#. .##
} ##. .#. .#. ..# .#. .#. ##.
\ #.. #.. .#. .#. .#. ..# ..#
| # # # # # # # #
"""
FONT = {}
for _line in _ART.strip("\n").splitlines():
    _ch, *_rows = _line.split(" ")
    assert len({len(r) for r in _rows}) == 1 and 7 <= len(_rows) <= 9, _line
    FONT[_ch] = _rows
SPACE = 3                      # advance of a space
PRINTABLE = "".join(chr(c) for c in range(0x21, 0x7F))
assert set(FONT) == set(PRINTABLE), set(PRINTABLE) ^ set(FONT)
FOLD = {"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-", "…": "..."}

SLICE = 16                     # px of ink per font entry (u16 rows)
GLYPH_ROWS = 13
LINE_MAX = 38                  # ink width of a line: the scroll's inside is x 2-41, 1 px margin each side
LINE_PITCH = 11                # px from one line's top to the next (engine)
PAGE_ROWS = 13                 # 13 * 11 + 7 = 150 px of the scroll's 156
PAGE_SLOTS = 36                # mode-0 sprite slots 0x3C-0x5F (0x08011F56, reveal cap 0x24 at 0x080124DE)
NAME_MAX = 8                   # player-name letters reserved where %n sits (name entry box)
NAME_ADV = 4                   # reserved advance per name letter (3 px letters + 1)
CONTROLS = re.compile(r"\|n|%[nbBr]")
CODE_B0 = (0x01, 0x25)         # slice codes: b0 0x01-0x24, b1 0x01-0xFF
MAX_SLICES = (CODE_B0[1] - CODE_B0[0]) * 255
MANGA_BANKS_SKIP = {"results"}  # drawn in one-column labels (mode 1 / BG): StackEncoder, not bubbles


COLOURS = {"%b": "\x01", "%B": "\x02", "%r": "\x03"}   # zero-width marks in the layout, codes again in the output
UNCOLOUR = {v: k for k, v in COLOURS.items()}


def width(ch):
    if ch in UNCOLOUR:
        return -1
    return SPACE - 1 if ch == " " else len(FONT[ch][0])


def adv(ch):
    return width(ch) + 1


def fold(text):
    for a, b in FOLD.items():
        text = text.replace(a, b)
    return text


def ink_width(s):
    """Ink extent of a run of letters starting at x 0 (no trailing gap); spaces count but have no ink."""
    x, end = 0, 0
    for ch in s:
        if ch != " " and ch not in UNCOLOUR:
            end = x + width(ch)
        x += adv(ch)
    return end


def run_width(s):
    return sum(adv(ch) for ch in s)


# ---- layout -------------------------------------------------------------------------------------------------

def _tokens(text):
    """Words of a page in reading order; '%n' is its own token glued to its neighbours by '\0' marks."""
    return text.split()


def _wordw(w):
    """Ink width of a word that may contain %n (reserved at NAME_MAX letters)."""
    parts = re.split(r"(%n)", w)
    total = 0
    for k, p in enumerate(parts):
        if p == "%n":
            total += NAME_MAX * NAME_ADV - 1 + (1 if k < len(parts) - 1 and parts[k + 1] else 0)
        elif p:
            total += ink_width(p) if k == len(parts) - 1 else run_width(p)
    return total


DIGRAPHS = {"TH", "SH", "CH", "WH", "PH", "CK", "NG", "TS", "QU",   # never split; also onset clusters:
            "PL", "PR", "TR", "BL", "BR", "CR", "CL", "DR", "FR", "FL", "GR", "GL", "SC", "SK", "SL", "SP", "ST"}
BAD_TAIL = re.compile(r"[^AEIOU]?ED|NG|[A-Z]{1,2}")   # tails that read as a broken suffix
# Break points for words the heuristic splits badly (checked first; the last one that fits wins).
HYPHENATION = {w.replace("-", ""): w for w in """
    BEGIN-NING GRAND-FATHER GRASS-LAND HIDE-YOSHI LIGHT-NING SIGN-POSTS THINK-ING UNDER-ESTI-MATE
    UNDER-ESTI-MATED POS-SES-SION IM-POS-SI-BLE KAMI-IZUMI UN-PUN-ISHED DIF-FER-ENT EVERY-THING EVERY-WHERE
    SOME-WHERE NETHER-WORLD SWORDS-MAN""".split()}


def _tail_ok(tail):
    core = re.sub(r"[^A-Z].*", "", tail)   # letters up to the first apostrophe / punctuation
    return not BAD_TAIL.fullmatch(core)


def _syllable_break(word, k):
    """True when word[:k] | word[k:] falls between syllables: V-CV, VC-CV, or before a digraph (Y is a vowel
    unless a vowel follows it). Good enough for the script's English and Hepburn names (HIDE-YOSHI, GRAND-FATHER,
    EVERY-WHERE, MITSU-HIDE)."""
    def vowel(i):
        ch = word[i] if 0 <= i < len(word) else ""
        if ch == "Y":
            return not (i + 1 < len(word) and word[i + 1] in "AEIOU")
        return ch in "AEIOU"
    a, b = word[k - 1], word[k]
    c = word[k + 1] if k + 1 < len(word) else ""
    if vowel(k - 1) and not vowel(k) and (vowel(k + 1) or b + c in DIGRAPHS):
        return True
    return not vowel(k - 1) and not vowel(k) and a + b not in DIGRAPHS and b != "Y" or a == "N" and not vowel(k)


def _split_long(word, room):
    """Break a word wider than a line: after a hyphen if one fits, else with an added hyphen (>= 3 letters each
    side), at the last syllable boundary that fits, else the last letter boundary. Returns (head, tail)."""
    for k in range(len(word) - 1, 0, -1):
        if word[k - 1] == "-" and _wordw(word[:k]) <= room:
            return word[:k], word[k:]
    fits = []
    for k in range(len(word) - 2, 1, -1):
        head = word[:k] + "-"
        letters = (sum(c.isalpha() for c in word[:k]), sum(c.isalpha() for c in word[k:]))
        if ("%n" not in head and word[k - 1].isalpha() and word[k].isalpha() and min(letters) >= 3
                and _tail_ok(word[k:]) and _wordw(head) <= room):
            fits.append(k)
    if not fits:
        raise ValueError(f"cannot break {word!r} into a {room} px line")
    stem = re.match(r"[A-Z]+", word)
    known = HYPHENATION.get(stem.group() if stem else "")
    if known:
        points = [k for k, ch in enumerate(known.replace("-", "\0").replace("\0", "-")) if ch == "-"]
        points = [p - n for n, p in enumerate(points)]          # letter index of each break
        k = next((k for k in sorted(points, reverse=True) if _wordw(word[:k] + "-") <= room), None)
        if k:
            return word[:k] + "-", word[k:]
    k = next((k for k in fits if _syllable_break(word, k)), fits[0])
    return word[:k] + "-", word[k:]


def wrap(text, line_max=LINE_MAX):
    """Lines of a page. `|n` in the English is a soft break (the v1 24-letter lines), so the page is re-wrapped
    as one paragraph; an empty line (|n|n) is kept as a paragraph break."""
    paras = re.split(r"(?:\|n){2,}", text)
    lines = []
    for para in paras:
        words = para.replace("|n", " ").split()
        cur = ""
        while words:
            w = words.pop(0)
            cand = f"{cur} {w}" if cur else w
            if _wordw(cand) <= line_max:
                cur = cand
                continue
            if cur:
                lines.append(cur)
                cur = ""
                words.insert(0, w)
                continue
            head, tail = _split_long(w, line_max)
            lines.append(head)
            words.insert(0, tail)
        if cur:
            lines.append(cur)
    return lines


def slices(line):
    """[(kind, text)]: kind 'g' = a slice drawn from one font entry (<= SLICE px of ink, trailing spaces kept in its
    advance), 'n' = the %n control, 'c' = a colour code (%b %B %r: applies to the sprites drawn after it).
    Greedy: letters join the current slice while its ink stays within SLICE."""
    out = []
    for part in re.split(r"(%n|[\x01-\x03])", line):
        if part == "%n":
            out.append(("n", part))
            continue
        if part in UNCOLOUR:
            out.append(("c", UNCOLOUR[part]))
            continue
        cur = ""
        for ch in part:
            if cur and ch != " " and ink_width(cur + ch) > SLICE:
                out.append(("g", cur))
                cur = ""
            if not cur and ch == " " and out and out[-1][0] == "g":
                out[-1] = ("g", out[-1][1] + ch)   # a space after a slice widens that slice's advance
                continue
            cur += ch
        if cur:
            out.append(("g", cur))
    return out


def page(text):
    """(lines, [[slices] per line]) for an English page, upper-cased; colour codes ride along as marks."""
    t = fold(text)
    for c, mark in COLOURS.items():
        t = t.replace(c, mark)
    t = t.replace("%n", "\x00").replace("|n", "\x04").upper().replace("\x00", "%n").replace("\x04", "|n")
    lines = wrap(t)
    return lines, [slices(ln) for ln in lines]


def slots(sl):
    return sum(NAME_MAX if k == "n" else 1 if k == "g" else 0 for line in sl for k, _ in line)


def problems(text):
    lines, sl = page(text)
    errs = []
    if len(lines) > PAGE_ROWS:
        errs.append(f"{len(lines)} lines > {PAGE_ROWS}")
    if slots(sl) > PAGE_SLOTS:
        errs.append(f"{slots(sl)} sprite slots > {PAGE_SLOTS}")
    for ln in lines:
        if _wordw(ln) > LINE_MAX:
            errs.append(f"line {ln!r} {_wordw(ln)} px > {LINE_MAX}")
    return errs


# ---- glyphs -------------------------------------------------------------------------------------------------

def glyph_rows(s):
    """13 u16 rows (bit 15 = x 0) of a slice drawn from x 0, cap top at row 0."""
    rows = [0] * GLYPH_ROWS
    x = 0
    for ch in s:
        if ch != " ":
            for r, line in enumerate(FONT[ch]):
                for c, px in enumerate(line):
                    if px == "#":
                        assert x + c < 16, s
                        rows[r] |= 0x8000 >> (x + c)
        x += adv(ch)
    return rows


def glyph_bytes(s):
    return b"".join(struct.pack(">H", v) for v in glyph_rows(s))


NAME_COL_X = 4   # a name letter's ink starts here, so a letter stacks centred in a 12 px column (mode 1)


def name_glyph(ch):
    """Name-grid letter (tools/name_grid.py LETTERS): upright, ink from x NAME_COL_X. In mode 0 the engine pulls
    the sprite left by NAME_COL_X and advances by the letter's own width + 1."""
    rows = [0] * GLYPH_ROWS
    for r, line in enumerate(FONT[ch]):
        for c, px in enumerate(line):
            if px == "#":
                rows[r + 2] |= 0x8000 >> (NAME_COL_X + c)
    return b"".join(struct.pack(">H", v) for v in rows)


def code(k):
    if not 0 <= k < MAX_SLICES:
        raise ValueError(f"slice index {k} out of range ({MAX_SLICES} codes)")
    return bytes((CODE_B0[0] + k // 255, 1 + k % 255))


class Encoder:
    """Slice dictionary over a set of pages (sorted, so the same script gives the same ROM)."""

    def __init__(self, texts):
        seen = set()
        self.pages = {}
        for t in texts:
            errs = problems(t)
            if errs:
                raise ValueError(f"{t!r}: {'; '.join(errs)}")
            _, sl = page(t)
            seen.update(s for line in sl for k, s in line if k == "g")
        self.slices = sorted(seen)
        if len(self.slices) > MAX_SLICES:
            raise ValueError(f"{len(self.slices)} slices, room for {MAX_SLICES}")
        self.index = {s: k for k, s in enumerate(self.slices)}

    def encode(self, text):
        _, sl = page(text)
        out = bytearray()
        for li, line in enumerate(sl):
            if li:
                out += b"|n"
            for kind, s in line:
                out += code(self.index[s]) if kind == "g" else s.encode("ascii")
        return bytes(out)

    def widths(self):
        """Advance of each slice (index order)."""
        return [run_width(s) for s in self.slices]


STACK_LIMIT = 116   # rows a mode-1 label may take: the title noun column starts near y 33 and the reader wraps
                    # a glyph past y 147, so the last letter (start = 33 + length - 7) must start by 147
STACK_SPACE = 4     # down-advance of a space
STACK_CX = 5        # letters centred on x 5 of the 16 px glyph (a 12 px column, as name_glyph)


def stack_glyph(ch, font):
    """(13 u16 rows, down-advance): one upright letter of `font` (upright.FONTS) for the mode-1 label columns,
    centred on STACK_CX, ink from row 2 (as the name letters), advance = ink height + 1 (a space STACK_SPACE)."""
    import upright
    rows = [0] * GLYPH_ROWS
    if ch == " ":
        return b"".join(struct.pack(">H", v) for v in rows), STACK_SPACE
    pts, w, h = upright.ink(ch, font)
    x0 = STACK_CX - w // 2
    for r, c in pts:
        rows[2 + r] |= 0x8000 >> (x0 + c)
    return b"".join(struct.pack(">H", v) for v in rows), h + 1


def pair_glyph(two):
    """13 u16 rows: two TINY letters stacked upright in one 12-row cell (rows 1-5 and 7-11), for the results
    screen's BG text routine 0x08012A2C, which steps a fixed 12 px a glyph: 6 px a letter."""
    import upright
    rows = [0] * GLYPH_ROWS
    for k, ch in enumerate(two):
        if ch == " ":
            continue
        pts, w, h = upright.ink(ch, "tiny")
        x0, y0 = STACK_CX - w // 2, 1 + 6 * k + (5 - h if ch in ".," else 0)
        for r, c in pts:
            rows[y0 + r] |= 0x8000 >> (x0 + c)
    return b"".join(struct.pack(">H", v) for v in rows)


# The results screen's stat labels and ranks (tables 0x7469B0 / 0x7469F8, script ids 201828-201927) are drawn by
# the BG routine 0x08012A2C, not the reader: they get letter pairs (pair_glyph).
BG_LABELS = range(0x201828, 0x201928)


class StackEncoder:
    """Mode-1 labels (the results screen) as upright letters stacked down the column, one font entry per
    letter; the engine moves down by each entry's +5 byte (manga_engine). A label longer than STACK_LIMIT in the
    3x7 caps uses upright's 3x5 TINY caps. `bg` texts are drawn by the BG routine instead: TINY letter pairs, one
    per 12 px glyph. Codes follow the scroll slices (code(first + k))."""

    def __init__(self, texts, first, bg=()):
        self.first = first
        self.bg = set(bg)
        self.font_of = {t: self._font(t) for t in texts if t not in self.bg}
        keys = {(f, ch) for t, f in self.font_of.items() for ch in self._chars(t)}
        keys |= {("pair", p) for t in self.bg for p in self._pairs(t)}
        self.glyphs = sorted(keys)
        self.index = {k: first + n for n, k in enumerate(self.glyphs)}
        if first + len(self.glyphs) > MAX_SLICES:
            raise ValueError("no codes left for the stacked labels")

    @classmethod
    def _pairs(cls, text):
        out = []
        for part in cls._parts(text):
            if not part.startswith("%"):
                part += " " * (len(part) % 2)
                out += [part[k:k + 2] for k in range(0, len(part), 2)]
        return out

    @staticmethod
    def _parts(text):
        """Upper-cased text split around its printf codes (kept lower case: %d)."""
        t = re.sub(r"%([A-Z])", lambda m: "%" + m.group(1).lower(), fold(text).upper())
        return [p for p in re.split(r"(%[a-z])", t) if p]

    @classmethod
    def _chars(cls, text):
        return [ch for part in cls._parts(text) if not part.startswith("%") for ch in part]

    def length(self, text, font):
        return sum(stack_glyph(ch, font)[1] for ch in self._chars(text)) - 1

    def _font(self, text):
        return "manga" if self.length(text, "manga") <= STACK_LIMIT else "tiny"

    def encode(self, text):
        out = bytearray()
        for part in self._parts(text):
            if part.startswith("%"):
                out += part.encode("ascii")
            elif text in self.bg:
                part += " " * (len(part) % 2)
                for k in range(0, len(part), 2):
                    out += code(self.index[("pair", part[k:k + 2])])
            else:
                for ch in part:
                    out += code(self.index[(self.font_of[text], ch)])
        return bytes(out)

    def entries(self):
        """[(code index, glyph bytes, u16 at +4)] (+4 low byte 0: no mode-0 advance; high byte = down-advance,
        0 = 12 for the pairs)."""
        out = []
        for (f, ch) in self.glyphs:
            if f == "pair":
                out.append((self.index[(f, ch)], pair_glyph(ch), 0))
                continue
            g, adv = stack_glyph(ch, f)
            out.append((self.index[(f, ch)], g, adv << 8))
        return out


# ---- tools --------------------------------------------------------------------------------------------------

def manga_texts(edits_by_bank):
    return {a: t for bank, d in edits_by_bank.items() if bank not in MANGA_BANKS_SKIP for a, t in d.items()}


def _render(text, scale=1):
    """Greyscale rows of a page as the engine lays it out (lines centred, block centred): for --sheet."""
    lines, sl = page(text)
    w, h = 40, 156
    img = [[255] * w for _ in range(h)]
    top = (h - ((len(lines) - 1) * LINE_PITCH + 7)) // 2
    for li, line in enumerate(sl):
        txt = "".join("N" * NAME_MAX if k == "n" else s for k, s in line if k != "c")
        x = (w - run_width(txt)) // 2
        for ch in txt:
            if ch != " ":
                for r, row in enumerate(FONT[ch]):
                    for c, px in enumerate(row):
                        if px == "#" and 0 <= x + c < w and 0 <= top + li * LINE_PITCH + r < h:
                            img[top + li * LINE_PITCH + r][x + c] = 0
            x += adv(ch)
    return img


def _png(path, img):
    import zlib
    w, h = len(img[0]), len(img)
    raw = b"".join(b"\0" + bytes(r) for r in img)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
    Path(path).write_bytes(data + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _sheet(out, ids):
    sys.path.insert(0, str(ROOT / "tools"))
    import script
    pages = [(e["id"], e["en"]) for bank, es in script.load().items() if bank not in MANGA_BANKS_SKIP
             for e in es if e.get("en") and (not ids or e["id"] in ids)][:24]
    tiles = [_render(t) for _, t in pages]
    cols = min(8, len(tiles))
    rows_n = (len(tiles) + cols - 1) // cols
    img = [[128] * (cols * 44) for _ in range(rows_n * 160)]
    for k, t in enumerate(tiles):
        ox, oy = (k % cols) * 44 + 2, (k // cols) * 160 + 2
        for y, row in enumerate(t):
            img[oy + y][ox:ox + 40] = row
    zoom = 3
    img = [[v for v in row for _ in range(zoom)] for row in img for _ in range(zoom)]
    _png(out, img)
    print(out, " ".join(i for i, _ in pages))


def _fit():
    sys.path.insert(0, str(ROOT / "tools"))
    import script
    bad = 0
    for bank, es in script.load().items():
        if bank in MANGA_BANKS_SKIP:
            continue
        for e in es:
            if e.get("en"):
                try:
                    errs = problems(e["en"])
                except ValueError as ex:
                    errs = [str(ex)]
                if errs:
                    bad += 1
                    print(f"{bank} {e['id']}: {'; '.join(errs)}")
    print(f"{bad} pages over a limit")
    return bad


def _selftest():
    for ch, art in FONT.items():
        assert 7 <= len(art) <= 9 and len(art[0]) <= 5, ch
    assert ink_width("ABC") == 11 and run_width("ABC") == 12
    lines, sl = page("What is more, the enemy|nis not human! They are|nmonsters and fiends!")
    assert lines[0] == "WHAT IS" and all(_wordw(ln) <= LINE_MAX for ln in lines), lines
    for line in sl:
        for k, s in line:
            assert k == "n" or ink_width(s.rstrip()) <= SLICE, s
    assert wrap("TOYOTOMI-DONO'S") == ["TOYOTOMI-", "DONO'S"], wrap("TOYOTOMI-DONO'S")
    e = Encoder(["Welcome,|n%n.", "%b%n%B, OK?|n%rA: Select  B: Back|n"])
    b = e.encode("Welcome,|n%n.")
    assert b"%n" in b and b"|n" in b and all(0 < x < 0x25 for x in b.replace(b"%n", b"").replace(b"|n", b""))
    assert e.encode("%b%n%B, OK?|n%rA: Select  B: Back|n").startswith(b"%b")
    print(f"selftest ok: {len(FONT)} glyphs")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        _selftest()
    elif "--sheet" in sys.argv:
        i = sys.argv.index("--sheet")
        _sheet(sys.argv[i + 1], set(sys.argv[i + 2:]))
    elif "--fit" in sys.argv:
        sys.exit(1 if _fit() else 0)
    else:
        print(__doc__)

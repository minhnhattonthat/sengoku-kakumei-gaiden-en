"""Find NUL-terminated EUC-JP strings (allowing ASCII control/printables), report regions and samples."""
import sys
from collections import Counter
rom = open(sys.argv[1], 'rb').read()
out = sys.argv[2] if len(sys.argv) > 2 else None

def parse(i):
    """Parse a candidate string at i; return (end, text, jpchars, other) or None."""
    text = ''; jp = 0; other = 0; j = i
    while j < len(rom):
        b = rom[j]
        if b == 0:
            return j, text, jp, other
        if 0xa1 <= b <= 0xfe and j + 1 < len(rom) and 0xa1 <= rom[j+1] <= 0xfe:
            try:
                text += rom[j:j+2].decode('euc_jp'); jp += 1; j += 2; continue
            except UnicodeDecodeError:
                return None
        if 0x20 <= b < 0x7f or b in (0x0a, 0x0d):
            text += chr(b) if b >= 0x20 else '\\n'; other += 1; j += 1; continue
        if b < 0x20:
            text += f'[{b:02X}]'; other += 1; j += 1; continue
        return None
    return None

strings = []
i = 0
while i < len(rom):
    if 0xa1 <= rom[i] <= 0xfe:
        r = parse(i)
        if r and r[2] >= 2 and r[2] >= r[3]:
            kana = sum(1 for c in r[1] if 'ぁ' <= c <= 'ヺ' or c in '。、！？ー「」…・　')
            if kana >= 1 or r[2] >= 2:
                strings.append((i, r[0], r[1]))
                i = r[0] + 1; continue
    i += 1

c = Counter(s[0] >> 16 for s in strings)
print('strings', len(strings), 'jp bytes', sum(s[1]-s[0] for s in strings))
for k in sorted(c): print(f'{k<<16:07x}:{c[k]}', end='  ')
print()
if out:
    with open(out, 'w', encoding='utf-8') as f:
        for s, e, t in strings:
            f.write(f'{s:07x}\t{e-s}\t{t}\n')

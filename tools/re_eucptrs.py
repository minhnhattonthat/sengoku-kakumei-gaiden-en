"""For each EUC candidate in euc.tsv, count aligned u32 pointers (0x08000000|off) to it; summarise."""
import sys, struct
from collections import Counter, defaultdict
rom = open(sys.argv[1], 'rb').read()
rows = [l.rstrip('\n').split('\t', 2) for l in open(sys.argv[2], encoding='utf-8')]
refs = defaultdict(list)
for p in range(0, len(rom) - 3, 4):
    v = struct.unpack_from('<I', rom, p)[0]
    if 0x08000000 <= v < 0x08000000 + len(rom):
        refs[v - 0x08000000].append(p)

pointed = []
for a, n, t in rows:
    a = int(a, 16)
    if a in refs:
        pointed.append((a, int(n), t, refs[a]))
print('candidates', len(rows), 'pointed', len(pointed), 'bytes', sum(x[1] for x in pointed))
c = Counter(x[0] >> 16 for x in pointed)
for k in sorted(c): print(f'{k<<16:07x}:{c[k]}', end='  ')
print()
# where do the pointers live?
pc = Counter(r >> 16 for x in pointed for r in x[3])
print('pointer sites by 64K:')
for k in sorted(pc): print(f'{k<<16:07x}:{pc[k]}', end='  ')
print()
with open(sys.argv[3], 'w', encoding='utf-8') as f:
    for a, n, t, rs in pointed:
        f.write(f'{a:07x}\t{n}\t{",".join("%x" % r for r in rs)}\t{t}\n')
# unpointed real-looking strings (kana-rich, len>=4)
un = [(int(a,16), t) for a, n, t in rows if int(a,16) not in refs and sum(1 for ch in t if 'ぁ' <= ch <= 'ヺ') >= 3]
print('unpointed kana-rich', len(un))
for a, t in un[:: max(1, len(un)//25)]: print(f'{a:07x} {t[:40]}')

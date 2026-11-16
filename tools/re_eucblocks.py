"""Group pointed EUC strings into contiguous blocks (gaps of NUL padding <= 8 bytes); list blocks and pointer-site runs."""
import sys
rom = open(sys.argv[1], 'rb').read()
rows = []
for l in open(sys.argv[2], encoding='utf-8'):
    a, n, refs, t = l.rstrip('\n').split('\t', 3)
    rows.append((int(a, 16), int(n), [int(r, 16) for r in refs.split(',')], t))
rows.sort()

def merge(spans, gap):
    out = []
    for s, e in sorted(spans):
        if out and s - out[-1][1] <= gap and all(b == 0 for b in rom[out[-1][1]:s]) or (out and s <= out[-1][1]):
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out

blocks = merge([(a, a + n + 1) for a, n, _, _ in rows], 64)
print('text blocks (start end size nstr):')
for s, e in blocks:
    k = sum(1 for a, *_ in rows if s <= a < e)
    if k >= 1: print(f'  {s:07x} {e:07x} {e-s:6d} {k}')
sites = sorted(r for _, _, rs, _ in rows for r in rs)
runs = []
for p in sites:
    if runs and p - runs[-1][1] <= 64: runs[-1][1] = p + 4; runs[-1][2] += 1
    else: runs.append([p, p + 4, 1])
print('pointer-site runs (start end count):')
for s, e, k in runs: print(f'  {s:07x} {e:07x} {k}')

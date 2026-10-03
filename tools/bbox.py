# -*- coding: utf-8 -*-
"""Measure the subject's on-screen bounding box (robust to a backdrop
gradient): find rows/columns whose pixel count far from the local backdrop
exceeds a threshold."""
import sys
from PIL import Image


def bbox(path, tol=38, frac=0.06):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    step = 4
    w, h = W // step, H // step
    px = im.resize((w, h), Image.BOX).load()
    corners = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
    colcnt = [0] * w
    rowcnt = [0] * h
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if (abs(c[0] - bg[0]) + abs(c[1] - bg[1]) + abs(c[2] - bg[2])) > tol:
                colcnt[x] += 1
                rowcnt[y] += 1
    cx = max(2, int(frac * h))
    cy = max(2, int(frac * w))
    cols = [i for i in range(w) if colcnt[i] > cx]
    rows = [i for i in range(h) if rowcnt[i] > cy]
    if not cols or not rows:
        print('%-30s no subject found' % path.split('/')[-1])
        return
    u0, u1 = cols[0] / w, (cols[-1] + 1) / w
    v0, v1 = rows[0] / h, (rows[-1] + 1) / h
    cw, ch = u1 - u0, v1 - v0
    print('%-30s bg=%s u[%.3f %.3f] v[%.3f %.3f]  w=%.3f h=%.3f  aspect=%.2f'
          % (path.split('/')[-1], str(bg), u0, u1, v0, v1, cw, ch,
             cw / max(ch, 1e-6)))


for p in sys.argv[1:]:
    bbox(p)

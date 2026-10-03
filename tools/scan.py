# -*- coding: utf-8 -*-
"""Vertical / horizontal colour scan to locate features in the reference plate."""
import sys
from PIL import Image

path = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else 'scan'
im = Image.open(path).convert('RGB')
W, H = im.size
if mode == 'scan':
    u = float(sys.argv[3])
    v0, v1, n = float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
    print('VSCAN u=%.3f  (x=%d)' % (u, int(u * W)))
    x = int(u * W)
    for i in range(n + 1):
        v = v0 + (v1 - v0) * i / n
        y = min(H - 1, int(v * H))
        c = im.crop((max(0, x - 3), max(0, y - 1), min(W, x + 3), min(H, y + 2)))
        c = c.resize((1, 1), Image.BOX).getpixel((0, 0))
        print('v=%.3f y=%4d  %3d %3d %3d  #%02X%02X%02X' % (v, y, c[0], c[1], c[2], *c))
else:
    v = float(sys.argv[3])
    u0, u1, n = float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
    y = int(v * H)
    print('HSCAN v=%.3f  (y=%d)' % (v, y))
    for i in range(n + 1):
        u = u0 + (u1 - u0) * i / n
        x = min(W - 1, int(u * W))
        c = im.crop((max(0, x - 1), max(0, y - 3), min(W, x + 2), min(H, y + 3)))
        c = c.resize((1, 1), Image.BOX).getpixel((0, 0))
        print('u=%.3f x=%4d  %3d %3d %3d  #%02X%02X%02X' % (u, x, c[0], c[1], c[2], *c))

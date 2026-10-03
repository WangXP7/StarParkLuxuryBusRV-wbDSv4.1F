# -*- coding: utf-8 -*-
"""One-shot patch sampling for the reference plate."""
import sys
from PIL import Image

P = [
    ('bg_top',      0.500, 0.030, 0.008),
    ('ground',      0.500, 0.965, 0.008),
    ('body_upper',  0.300, 0.230, 0.006),
    ('body_mid',    0.350, 0.500, 0.006),
    ('body_low',    0.350, 0.562, 0.006),
    ('gold_band',   0.348, 0.436, 0.004),
    ('skirt_upper', 0.352, 0.628, 0.005),
    ('skirt_lower', 0.352, 0.700, 0.005),
    ('skirt_front', 0.800, 0.780, 0.006),
    ('win_int_a',   0.335, 0.350, 0.006),
    ('win_int_b',   0.135, 0.345, 0.006),
    ('windshield',  0.760, 0.330, 0.006),
    ('tire',        0.118, 0.645, 0.005),
    ('rim',         0.098, 0.628, 0.004),
    ('roofkit',     0.300, 0.075, 0.006),
    ('roof_cream',  0.480, 0.190, 0.005),
]

for path, tag in ((sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'REF'),):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    print('=== %s  %dx%d ===' % (tag, W, H))
    for (nm, u, v, r) in P:
        x, y = int(u * W), int(v * H)
        rr = max(2, int(r * min(W, H)))
        c = im.crop((max(0, x - rr), max(0, y - rr),
                     min(W, x + rr), min(H, y + rr))).resize((1, 1), Image.BOX)
        px = c.getpixel((0, 0))
        print('%-13s %3d %3d %3d    #%02X%02X%02X' % (nm, px[0], px[1], px[2], *px))

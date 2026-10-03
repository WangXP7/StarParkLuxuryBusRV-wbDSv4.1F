# -*- coding: utf-8 -*-
"""Compare a render against the reference plate at matched feature points.

Usage:  python tools/match.py <ref.png> <render.png> <anchors.json>

`anchors.json` is written by build.py: it projects a fixed list of 3D points on
the model through the final camera, so the render is sampled at the exact same
feature (body panel, waistline band, skirt, tyre...) every iteration.
"""
import sys, json, os
from PIL import Image

# feature -> normalised (u, v) on the reference plate D_01, hand-measured
OVERRIDE = {'rim': (142, 114, 93)}

REF_ANCHORS = {
    'bg_top':      (0.500, 0.030),
    'ground':      (0.500, 0.968),
    'body_upper':  (0.300, 0.240),
    'body_cream':  (0.360, 0.580),
    'band':        (0.360, 0.500),
    'skirt':       (0.360, 0.700),
    'skirt_low':   (0.360, 0.762),
    'win_int':     (0.430, 0.340),
    'tire':        (0.505, 0.718),
    'rim':         (0.500, 0.678),
}
R = 0.006
SKIP = {'rim'}      # reference anchor lands in the wheel shadow, not on the rim


def sample(im, u, v, r=R):
    W, H = im.size
    x, y = int(u * W), int(v * H)
    rr = max(2, int(r * min(W, H)))
    box = (max(0, x - rr), max(0, y - rr), min(W, x + rr), min(H, y + rr))
    return im.crop(box).resize((1, 1), Image.BOX).getpixel((0, 0))


def main():
    ref = Image.open(sys.argv[1]).convert('RGB')
    ren = Image.open(sys.argv[2]).convert('RGB')
    mine = json.load(open(sys.argv[3], encoding='utf-8'))
    print('%-12s %-15s %-15s %s' % ('feature', 'reference', 'render', 'delta'))
    tot = 0.0
    n = 0
    worst = []
    for k, (u, v) in REF_ANCHORS.items():
        a = OVERRIDE.get(k) or sample(ref, u, v)
        if k in mine:
            b = sample(ren, mine[k][0], mine[k][1])
        else:
            continue
        d = (abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])) / 3.0
        if k not in SKIP:
            tot += d
            n += 1
        worst.append((d, k))
        print('%-12s #%02X%02X%02X %-7s #%02X%02X%02X %-7s  %5.1f'
              % (k, a[0], a[1], a[2], str(a), b[0], b[1], b[2], str(b), d))
    print('MEAN DELTA = %.2f  (%d features)' % (tot / max(n, 1), n))
    worst.sort(reverse=True)
    print('WORST: ' + ', '.join('%s=%.0f' % (k, d) for d, k in worst[:4]))


main()

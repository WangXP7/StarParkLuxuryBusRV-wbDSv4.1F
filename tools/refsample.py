# -*- coding: utf-8 -*-
"""Sample colours / crops from a reference or render image."""
import sys, os
from PIL import Image

def grid(path, nx=12, ny=8):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    print('FILE %s  %dx%d' % (os.path.basename(path), W, H))
    print('    ' + ''.join('%9d' % int((i + 0.5) * W / nx) for i in range(nx)))
    for j in range(ny):
        y0, y1 = int(j * H / ny), int((j + 1) * H / ny)
        row = []
        for i in range(nx):
            x0, x1 = int(i * W / nx), int((i + 1) * W / nx)
            c = im.crop((x0, y0, x1, y1)).resize((1, 1), Image.BOX).getpixel((0, 0))
            row.append('%9s' % ('%d,%d,%d' % c))
        print('%3d%%' % int((j + 0.5) * 100 / ny) + ''.join(row))

def patch(path, name, u, v, r=0.012):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    x, y = int(u * W), int(v * H)
    rr = max(2, int(r * min(W, H)))
    px = im.crop((max(0, x - rr), max(0, y - rr), min(W, x + rr), min(H, y + rr)))
    m = px.resize((1, 1), Image.BOX).getpixel((0, 0))
    print('PATCH %-18s %s' % (name, '%d,%d,%d' % m))
    return m

def crop(path, out, u0, v0, u1, v1, scale=3):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    box = (int(u0 * W), int(v0 * H), int(u1 * W), int(v1 * H))
    c = im.crop(box)
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    c.save(out)
    print('CROP ->', out, c.size)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'grid':
        grid(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12,
             int(sys.argv[4]) if len(sys.argv) > 4 else 8)
    elif cmd == 'patch':
        # patch <img> <name> <u> <v> [r]
        patch(sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]),
              float(sys.argv[6]) if len(sys.argv) > 6 else 0.012)
    elif cmd == 'crop':
        crop(sys.argv[2], sys.argv[3], *[float(a) for a in sys.argv[4:8]])

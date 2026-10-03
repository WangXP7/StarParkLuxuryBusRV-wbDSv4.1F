# -*- coding: utf-8 -*-
"""Build a compact iteration contact sheet + milestone frames for the repo."""
import os, re, sys
from PIL import Image, ImageDraw

SRC = sys.argv[1] if len(sys.argv) > 1 else 'render/iteration_log'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'render/iter'
MILESTONES = ['shot_v1', 'shot_m01', 'shot_m05', 'shot_m09',
              'shot_m16', 'shot_m24', 'shot_final']

os.makedirs(OUT, exist_ok=True)
files = sorted(f for f in os.listdir(SRC) if f.lower().endswith('.png'))
files.sort(key=lambda f: (0 if 'v1_' in f else 1, f))
print('found', len(files), 'frames')

# --- contact sheet -------------------------------------------------------
CW, CH, COLS = 384, 216, 6
rows = (len(files) + COLS - 1) // COLS
pad, lab = 6, 16
W = COLS * (CW + pad) + pad
H = rows * (CH + lab + pad) + pad
sheet = Image.new('RGB', (W, H), (24, 21, 19))
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(os.path.join(SRC, f)).convert('RGB').resize((CW, CH), Image.LANCZOS)
    c, r = i % COLS, i // COLS
    x, y = pad + c * (CW + pad), pad + r * (CH + lab + pad)
    sheet.paste(im, (x, y))
    name = re.sub(r'^shot_|_beauty\.png$', '', f)
    d.text((x + 2, y + CH + 2), '%02d  %s' % (i + 1, name), fill=(198, 168, 120))
sheet.save(os.path.join(OUT, 'iteration_sheet.jpg'), quality=88)
print('-> iteration_sheet.jpg', sheet.size)

# --- milestone frames ----------------------------------------------------
by_key = {}
for f in files:
    for m in MILESTONES:
        if f.startswith(m + '_'):
            by_key.setdefault(m, f)
for m, f in by_key.items():
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    im = im.resize((1600, int(im.height * 1600 / im.width)), Image.LANCZOS)
    name = re.sub(r'^shot_|_beauty\.png$', '', f)
    p = os.path.join(OUT, '%s.jpg' % name)
    im.save(p, quality=90)
    print('->', p, im.size,
          '%.0f KB' % (os.path.getsize(p) / 1024))

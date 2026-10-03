# -*- coding: utf-8 -*-
"""Stack the reference plate above the render for a direct eyeball comparison."""
import sys
from PIL import Image, ImageDraw

ref, ren, out = sys.argv[1], sys.argv[2], sys.argv[3]
a = Image.open(ref).convert('RGB')
b = Image.open(ren).convert('RGB')
W = 1400
a = a.resize((W, int(a.height * W / a.width)), Image.LANCZOS)
b = b.resize((W, int(b.height * W / b.width)), Image.LANCZOS)
pad = 8
canvas = Image.new('RGB', (W, a.height + b.height + pad * 3), (250, 248, 245))
canvas.paste(a, (0, pad))
canvas.paste(b, (0, a.height + pad * 2))
d = ImageDraw.Draw(canvas)
d.text((10, a.height + pad + 2), 'RENDER', fill=(90, 80, 70))
canvas.save(out)
print('->', out, canvas.size)

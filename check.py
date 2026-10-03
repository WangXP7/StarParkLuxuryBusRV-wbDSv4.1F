# -*- coding: utf-8 -*-
import bpy, sys, os
from mathutils import Vector
D = os.path.dirname(os.path.abspath(__file__))
if D not in sys.path:
    sys.path.insert(0, D)
import rv.lib_mat as LM
import rv.build_body as BB
import rv.build_under as BU
import rv.build_interior as BI
import rv.build_roofkit as BR
import rv.build_detail as BD

bpy.ops.wm.read_factory_settings(use_empty=True)
M = LM.build_all()
grp = {}
grp['body'] = BB.build(M)
grp['under'] = BU.build(M)
grp['inter'] = BI.build(M)
grp['roof'] = BR.build(M)
grp['det'] = BD.build(M)
bpy.context.view_layer.update()
LIM = dict(z=3.90, y=2.30, x=6.35)
bad = []
for k, lst in grp.items():
    for o in lst:
        if o.type != 'MESH':
            continue
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        r = [[min(p[i] for p in bb), max(p[i] for p in bb)] for i in range(3)]
        why = []
        if r[2][1] > LIM['z'] or r[2][0] < -0.10:
            why.append('Z%s' % [round(v, 2) for v in r[2]])
        if abs(r[1][0]) > LIM['y'] or abs(r[1][1]) > LIM['y']:
            why.append('Y%s' % [round(v, 2) for v in r[1]])
        if abs(r[0][0]) > LIM['x'] or abs(r[0][1]) > LIM['x']:
            why.append('X%s' % [round(v, 2) for v in r[0]])
        if why:
            bad.append((k, o.name, ' '.join(why)))
print('TOTAL', sum(len(v) for v in grp.values()), 'BAD', len(bad))
for b in bad[:40]:
    print('BAD', b)

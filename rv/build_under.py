# -*- coding: utf-8 -*-
"""Chassis, axles, wheels, air suspension, driveline and the mid-mounted engine."""
import bpy
from math import radians, sqrt, cos, sin
from mathutils import Vector

from . import spec as S
from .lib_util import box, cyl, sphere, revolve_y, set_origin_geo, mesh_from_pydata, shade_auto

AXLES = (S.AX_F, S.AX_R1, S.AX_R2)


def wheel(name, cx, cy, M):
    """One tyre + bronze rim + brake disc. Returns list of objects."""
    out = []
    sec = [(0.286, -0.150), (0.430, -0.166), (0.508, -0.140), (S.WHEEL_R, -0.078),
           (S.WHEEL_R, 0.078), (0.508, 0.140), (0.430, 0.166), (0.286, 0.150)]
    t = revolve_y(name + '_tyre', sec, cx, cy, S.WHEEL_R, mat=M['tire'], segs=48)
    set_origin_geo(t)
    out.append(t)
    # sidewall bulge ring
    sw = [(0.292, -0.172), (0.500, -0.164), (0.500, -0.150), (0.292, -0.156)]
    a = revolve_y(name + '_sw', sw, cx, cy, S.WHEEL_R, mat=M['tire'], segs=48)
    set_origin_geo(a)
    out.append(a)
    b = revolve_y(name + '_sw2', [(r, -y) for (r, y) in sw], cx, cy, S.WHEEL_R,
                  mat=M['tire'], segs=48)
    set_origin_geo(b)
    out.append(b)
    # rim barrel + face
    rim_sec = [(0.238, -0.168), (0.288, -0.168), (0.288, 0.168), (0.238, 0.168)]
    r = revolve_y(name + '_rim', rim_sec, cx, cy, S.WHEEL_R, mat=M['wheel'], segs=40)
    set_origin_geo(r)
    out.append(r)
    for sgn in (-1, 1):
        fy = cy + sgn * 0.150
        out.append(cyl(name + '_hub%d' % sgn, 0.082, 0.055, (cx, fy, S.WHEEL_R),
                       rot=(radians(90), 0, 0), mat=M['wheel'], segs=20))
        out.append(cyl(name + '_cap%d' % sgn, 0.055, 0.030, (cx, fy + sgn * 0.030, S.WHEEL_R),
                       rot=(radians(90), 0, 0), mat=M['chrome'], segs=18))
        out.append(cyl(name + '_back%d' % sgn, 0.272, 0.030,
                       (cx, cy - sgn * 0.055, S.WHEEL_R),
                       rot=(radians(90), 0, 0), mat=M['black_rough'], segs=30))
        out.append(cyl(name + '_disc%d' % sgn, 0.185, 0.034,
                       (cx, cy - sgn * 0.035, S.WHEEL_R),
                       rot=(radians(90), 0, 0), mat=M['black_rough'], segs=28))
        nsp = 7
        for k in range(nsp):
            a = 360.0 * k / nsp + 12.0
            ar = radians(a)
            rr = 0.185
            px = cx + rr * cos(ar)
            pz = S.WHEEL_R + rr * sin(ar)
            out.append(box(name + '_sp%d_%d' % (sgn, k), (0.070, 0.042, 0.205),
                           (px, fy, pz), rot=(0, -ar, 0), mat=M['wheel'],
                           bevel=0.016, segs=2))
            out.append(box(name + '_spw%d_%d' % (sgn, k), (0.038, 0.046, 0.105),
                           (cx + 0.245 * cos(ar), fy, S.WHEEL_R + 0.245 * sin(ar)),
                           rot=(0, -ar, 0), mat=M['wheel'], bevel=0.012, segs=2))
        out.append(revolve_y(name + '_lip%d' % sgn,
                             [(0.258, 0.0), (0.292, 0.0), (0.292, 0.050),
                              (0.258, 0.062)],
                             cx, fy - sgn * 0.062, S.WHEEL_R, mat=M['wheel'], segs=34))
    return out


def wheels(M):
    out = []
    for i, ax in enumerate(AXLES):
        for s in (-1, 1):
            out += wheel('W%d%s' % (i, 'R' if s > 0 else 'L'), ax,
                         s * S.TRACK, M)
    # wheel-well shells
    for i, ax in enumerate(AXLES):
        for s in (-1, 1):
            h = cyl('Well%d%d' % (i, s), 0.562, 0.40, (ax, s * S.TRACK, S.WHEEL_R),
                    rot=(radians(90), 0, 0), mat=M['black_rough'], segs=20, caps=False)
            out.append(h)
    return out


def axles(M):
    out = []
    for i, ax in enumerate(AXLES):
        out.append(cyl('Axle%d' % i, 0.072, 2.10, (ax, 0, S.WHEEL_R),
                       rot=(radians(90), 0, 0), mat=M['cast'], segs=16))
        out.append(cyl('Diff%d' % i, 0.165, 0.30, (ax, 0.06, S.WHEEL_R),
                       rot=(radians(90), 0, 0), mat=M['cast'], segs=18))
        out.append(sphere('DiffNose%d' % i, 0.115, (ax + 0.22, 0.06, S.WHEEL_R),
                          scale=(1.25, 1.0, 1.0), mat=M['cast']))
        # air spring bellows + shocks at each side
        for s in (-1, 1):
            bx = ax + 0.30
            out.append(cyl('BagA%d%d' % (i, s), 0.145, 0.30, (bx, s * 0.72, 0.72),
                           mat=M['black_rough'], segs=18))
            out.append(cyl('BagB%d%d' % (i, s), 0.125, 0.26, (bx, s * 0.72, 0.99),
                           mat=M['black_rough'], segs=18))
            out.append(cyl('Shock%d%d' % (i, s), 0.045, 0.42, (ax - 0.24, s * 0.66, 0.80),
                           mat=M['chrome'], segs=12))
            out.append(box('Leaf%d%d' % (i, s), (0.80, 0.10, 0.055),
                           (ax, s * 0.86, 0.70), mat=M['cast'], bevel=0.02))
    return out


def chassis(M):
    out = []
    for s in (-1, 1):
        out.append(box('Rail%d' % s, (11.30, 0.115, 0.235), (-0.10, s * 0.615, 0.845),
                       mat=M['cast'], bevel=0.02))
    for x in (-5.20, -4.30, -3.20, -2.00, -0.60, 0.80, 2.10, 3.30, 4.60):
        out.append(box('Xmem%.2f' % x, (0.11, 1.24, 0.16), (x, 0, 0.845),
                       mat=M['cast'], bevel=0.015))
    # driveline
    out.append(cyl('Shaft1', 0.055, 2.30, (0.05, 0.06, 0.690),
                   rot=(0, radians(90), 0), mat=M['alu'], segs=14))
    out.append(cyl('Shaft2', 0.055, 1.85, (-2.20, 0.06, 0.690),
                   rot=(0, radians(90), 0), mat=M['alu'], segs=14))
    # fuel + utility tanks
    out.append(box('FuelTank', (1.70, 0.560, 0.480), (0.35, -0.885, 0.885),
                   mat=M['alu'], bevel=0.05, segs=3))
    out.append(box('FuelStrapA', (0.045, 0.585, 0.520), (-0.20, -0.885, 0.885),
                   mat=M['black_rough']))
    out.append(box('FuelStrapB', (0.045, 0.585, 0.520), (0.90, -0.885, 0.885),
                   mat=M['black_rough']))
    out.append(box('DefTank', (0.62, 0.360, 0.420), (1.55, -0.900, 0.820),
                   mat=M['black_rough'], bevel=0.04))
    out.append(box('BattBox', (0.90, 0.500, 0.400), (-1.55, 0.900, 0.840),
                   mat=M['alu'], bevel=0.03))
    out.append(box('AirTankA', (0.86, 0.340, 0.340), (2.70, -0.900, 0.820),
                   mat=M['chrome'], bevel=0.05, segs=3))
    out.append(box('AirTankB', (0.86, 0.340, 0.340), (-0.70, 0.900, 0.800),
                   mat=M['chrome'], bevel=0.05, segs=3))
    # exhaust line
    out.append(cyl('ExhPipe', 0.058, 3.40, (-2.00, 1.02, 0.760),
                   rot=(0, radians(90), 0), mat=M['alu'], segs=12))
    out.append(box('Muffler', (0.86, 0.360, 0.340), (-4.30, 1.02, 0.760),
                   mat=M['alu'], bevel=0.06, segs=3))
    out.append(cyl('TailPipe', 0.062, 0.62, (-5.55, 1.02, 0.760),
                   rot=(0, radians(90), 0), mat=M['chrome'], segs=12))
    out.append(cyl('TailTip', 0.078, 0.10, (-5.86, 1.02, 0.760),
                   rot=(0, radians(90), 0), mat=M['chrome'], segs=14))
    # underfloor frame deck
    out.append(box('SubFloor', (11.50, 2.400, 0.075), (-0.08, 0, 1.475),
                   mat=M['cast']))
    return out


def engine(M, x=1.30):
    """Inline-6 diesel sitting in the underfloor bay."""
    out = []
    z = 0.760
    out.append(box('EngBlock', (1.34, 0.66, 0.44), (x, 0.0, z), mat=M['cast'],
                   bevel=0.03))
    out.append(box('EngPan', (1.16, 0.56, 0.20), (x, 0.0, z - 0.30), mat=M['alu'],
                   bevel=0.04))
    out.append(box('EngHead', (1.40, 0.60, 0.26), (x, 0.0, z + 0.34), mat=M['cast'],
                   bevel=0.03))
    out.append(box('EngCover', (1.34, 0.50, 0.15), (x, 0.0, z + 0.53), mat=M['black'],
                   bevel=0.04, segs=3))
    out.append(cyl('EngManifold', 0.088, 1.24, (x, 0.40, z + 0.30),
                   rot=(0, radians(90), 0), mat=M['cast'], segs=14))
    for i in range(6):
        px = x - 0.50 + i * 0.20
        out.append(cyl('Injector%d' % i, 0.038, 0.20, (px, 0.0, z + 0.60),
                       mat=M['alu'], segs=10))
        out.append(box('InPort%d' % i, (0.09, 0.34, 0.10), (px, 0.24, z + 0.36),
                       mat=M['cast']))
    out.append(cyl('Turbo', 0.135, 0.24, (x - 0.80, -0.30, z + 0.34),
                   rot=(0, radians(90), 0), mat=M['alu'], segs=16))
    out.append(sphere('TurboSnail', 0.155, (x - 0.80, -0.30, z + 0.34),
                      scale=(0.8, 1.2, 1.0), mat=M['alu']))
    out.append(cyl('Intake', 0.075, 0.90, (x - 0.30, -0.42, z + 0.30),
                   rot=(0, radians(90), 0), mat=M['black_rough'], segs=12))
    out.append(cyl('Crank', 0.075, 0.36, (x + 0.78, 0.0, z),
                   rot=(0, radians(90), 0), mat=M['alu'], segs=14))
    out.append(cyl('Pulley', 0.145, 0.055, (x + 0.95, 0.0, z),
                   rot=(0, radians(90), 0), mat=M['black'], segs=20))
    out.append(cyl('FanHub', 0.075, 0.20, (x + 1.05, 0.0, z + 0.10),
                   rot=(0, radians(90), 0), mat=M['cast'], segs=12))
    for k in range(9):
        a = 360.0 * k / 9.0
        ar = radians(a)
        out.append(box('FanBlade%d' % k, (0.055, 0.020, 0.185),
                       (x + 1.10, 0.235 * cos(ar), z + 0.10 + 0.235 * sin(ar)),
                       rot=(0, -ar, 0), mat=M['black']))
    out.append(box('Radiator', (0.13, 0.94, 0.62), (x + 1.42, 0.0, z + 0.14),
                   mat=M['black_rough']))
    out.append(box('Intercooler', (0.11, 0.86, 0.30), (x + 1.56, 0.0, z - 0.10),
                   mat=M['alu'], bevel=0.02))
    return out


def engine_louvers(M):
    """Louvred access panels so the engine bay reads from outside."""
    out = []
    for s in (-1, 1):
        for side_x in (5.30, -5.10):
            for k in range(6):
                zz = 0.74 + k * 0.115
                out.append(box('Louvre_%d_%.1f_%d' % (s, side_x, k),
                               (0.90, 0.055, 0.038),
                               (side_x, s * (S.Y_SKIRT_OUT - 0.008), zz),
                               rot=(radians(-26) * s, 0, 0), mat=M['black_rough']))
            out.append(box('LouvreFrame_%d_%.1f' % (s, side_x),
                           (1.02, 0.035, 0.740),
                           (side_x, s * (S.Y_SKIRT_OUT - 0.026), 1.045),
                           mat=M['skirt'], bevel=0.015))
    return out


def build(M):
    out = []
    out += chassis(M)
    out += axles(M)
    out += wheels(M)
    out += engine(M)
    out += engine_louvers(M)
    return out

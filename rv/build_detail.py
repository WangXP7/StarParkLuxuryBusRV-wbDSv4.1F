# -*- coding: utf-8 -*-
"""Exterior trim, lamps, mirrors, entry door skin and step."""
import bpy
from math import radians, cos, sin
from . import spec as S
from .lib_util import box, cyl, sphere, revolve_y, shade_auto


def belt_trim(M):
    out = []
    for s in (-1, 1):
        out.append(box('Belt_%d' % s, (11.86, 0.014, 0.072),
                       (0.0, s * (S.HW + 0.005), S.Z_BELT), mat=M['band']))
        out.append(box('Belt2_%d' % s, (11.86, 0.012, 0.018),
                       (0.0, s * (S.HW + 0.005), S.Z_SKIRT_TOP - 0.030), mat=M['band']))
        out.append(box('RoofLine_%d' % s, (11.86, 0.010, 0.030),
                       (0.0, s * 1.008, S.Z_ROOF_TRIM), mat=M['gold']))
    # front + rear continuation of the belt line
    out.append(box('BeltFront', (0.014, 2.30, 0.072), (6.006, 0.0, S.Z_BELT),
                   mat=M['band']))
    out.append(box('BeltRear', (0.014, 2.30, 0.072), (-6.006, 0.0, S.Z_BELT),
                   mat=M['band']))
    # vertical gold accent above the front corner
    for s in (-1, 1):
        out.append(box('FrontAcc_%d' % s, (0.010, 0.030, 1.15),
                       (6.004, s * 1.145, 2.60), mat=M['gold']))
    return out


def front_lights(M):
    out = []
    x = 6.008
    out.append(box('LampBand', (0.030, 2.180, 0.300), (x - 0.008, 0.0, 1.380),
                   mat=M['black'], bevel=0.03))
    for s in (-1, 1):
        out.append(cyl('Proj%d' % s, 0.098, 0.045, (x + 0.010, s * 0.80, 1.385),
                       rot=(0, radians(90), 0), mat=M['lens'], segs=22))
        out.append(cyl('ProjRing%d' % s, 0.118, 0.030, (x + 0.002, s * 0.80, 1.385),
                       rot=(0, radians(90), 0), mat=M['chrome'], segs=24))
        out.append(cyl('ProjInner%d' % s, 0.052, 0.030, (x + 0.014, s * 0.80, 1.385),
                       rot=(0, radians(90), 0), mat=M['led_drl'], segs=16))
        out.append(box('Drl%d' % s, (0.022, 0.560, 0.030), (x + 0.006, s * 0.62, 1.500),
                       mat=M['led_drl']))
        out.append(box('DrlB%d' % s, (0.022, 0.030, 0.150), (x + 0.006, s * 0.905, 1.435),
                       mat=M['led_drl']))
        out.append(box('DrlC%d' % s, (0.022, 0.330, 0.025), (x + 0.006, s * 0.44, 1.275),
                       mat=M['led_drl']))
        out.append(box('Fog%d' % s, (0.024, 0.190, 0.075), (x - 0.004, s * 0.82, 0.985),
                       mat=M['led_drl']))
        out.append(box('FogTrim%d' % s, (0.028, 0.250, 0.130), (x - 0.014, s * 0.82, 0.985),
                       mat=M['skirt'], bevel=0.02))
    return out


def roof_beacon(M):
    return []


def mirrors(M):
    out = []
    for s in (-1, 1):
        # two-piece arm off the A-pillar
        out.append(_tube('MirArmA_%d' % s,
                         [(5.68, s * 1.22, 2.24), (5.62, s * 1.55, 2.42),
                          (5.56, s * 1.88, 2.74)], 0.038, M['black']))
        out.append(_tube('MirArmB_%d' % s,
                         [(5.60, s * 1.20, 3.02), (5.56, s * 1.62, 3.02),
                          (5.53, s * 1.92, 2.90)], 0.032, M['black']))
        out.append(box('MirSpine_%d' % s, (0.055, 0.070, 0.780),
                       (5.560, s * 1.930, 2.640), mat=M['black'], bevel=0.018))
        # main glass head: dark shell, mirror face turned back toward the driver
        out.append(box('MirHead_%d' % s, (0.115, 0.240, 0.660),
                       (5.545, s * 2.030, 2.560), mat=M['roofkit'], bevel=0.035, segs=3))
        out.append(box('MirGlass_%d' % s, (0.030, 0.200, 0.580),
                       (5.480, s * 2.034, 2.560), mat=M['lens']))
        out.append(box('MirRim_%d' % s, (0.022, 0.255, 0.690),
                       (5.498, s * 2.030, 2.560), mat=M['black'], bevel=0.02))
        # convex blind-spot head above
        out.append(box('MirHead2_%d' % s, (0.100, 0.210, 0.330),
                       (5.560, s * 2.030, 3.190), mat=M['roofkit'], bevel=0.03, segs=3))
        out.append(box('MirGlass2_%d' % s, (0.028, 0.170, 0.270),
                       (5.500, s * 2.034, 3.190), mat=M['lens']))
        out.append(box('MirBase_%d' % s, (0.070, 0.090, 0.300),
                       (5.660, s * 1.245, 2.740), rot=(radians(6), 0, 0),
                       mat=M['black'], bevel=0.02))
    return out


def front_extra(M):
    """Brow visor over the screen, lower intake, tow eye, and a front crease."""
    out = []
    out.append(box('Brow', (0.115, 2.230, 0.150), (6.000, 0.0, 3.215),
                   mat=M['body'], bevel=0.045, segs=3))
    out.append(box('BrowUnder', (0.075, 2.120, 0.045), (6.020, 0.0, 3.130),
                   mat=M['skirt']))
    out.append(box('FrontIntake', (0.055, 1.900, 0.170), (6.008, 0.0, 0.985),
                   mat=M['black_rough'], bevel=0.02))
    for k in range(7):
        out.append(box('IntakeBar%d' % k, (0.030, 1.840, 0.055),
                       (6.028, 0.0, 0.910 + k * 0.028), mat=M['skirt']))
    for s in (-1, 1):
        out.append(cyl('TowEye%d' % s, 0.055, 0.075, (6.020, s * 0.46, 0.800),
                       rot=(0, radians(90), 0), mat=M['gold'], segs=16))
    return out


def _tube(name, pts, r, mat):
    from .lib_util import mesh_from_pydata
    verts, faces = [], []
    n = 8
    for i in range(len(pts) - 1):
        p = pts[i]
        q = pts[i + 1]
    rings = []
    import mathutils
    for i, p in enumerate(pts):
        if i == 0:
            d = mathutils.Vector(pts[1]) - mathutils.Vector(pts[0])
        elif i == len(pts) - 1:
            d = mathutils.Vector(pts[-1]) - mathutils.Vector(pts[-2])
        else:
            d = mathutils.Vector(pts[i + 1]) - mathutils.Vector(pts[i - 1])
        d.normalize()
        up = mathutils.Vector((0, 0, 1))
        if abs(d.dot(up)) > 0.95:
            up = mathutils.Vector((1, 0, 0))
        u = d.cross(up).normalized()
        v = u.cross(d).normalized()
        rings.append(len(verts))
        for k in range(n):
            a = 2.0 * 3.141592653589793 * k / n
            verts.append((p[0] + (u.x * cos(a) + v.x * sin(a)) * r,
                          p[1] + (u.y * cos(a) + v.y * sin(a)) * r,
                          p[2] + (u.z * cos(a) + v.z * sin(a)) * r))
    for i in range(len(pts) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(n):
            k2 = (k + 1) % n
            faces.append((a + k, a + k2, b + k2, b + k))
    faces.append(tuple(range(rings[0] + n - 1, rings[0] - 1, -1)))
    a = rings[-1]
    faces.append(tuple(range(a, a + n)))
    return mesh_from_pydata(name, verts, faces, mat, True)


def entry_door(M):
    """Glazed touring door on the vehicle's right (-Y), ahead of the front axle."""
    out = []
    x0, x1, z0, z1 = S.DOOR
    yo, yi = -1.2865, -1.2765
    w = lambda a, b: (b - a)
    parts = [
        ('DoorLow', x0 - 0.075, x1 + 0.075, 1.520, z0 - 0.008),
        ('DoorTop', x0 - 0.075, x1 + 0.075, z1 + 0.008, 3.070),
        ('DoorStileF', x0 - 0.075, x0 - 0.008, z0 - 0.008, z1 + 0.008),
        ('DoorStileR', x1 + 0.008, x1 + 0.075, z0 - 0.008, z1 + 0.008),
    ]
    for nm, a, b, c, d in parts:
        out.append(box(nm, (b - a, 0.010, d - c), ((a + b) * 0.5, (yo + yi) * 0.5,
                                                   (c + d) * 0.5), mat=M['body']))
    out.append(box('DoorSeam', (0.012, 0.020, 1.560), (x0 - 0.078, -1.282, 2.300),
                   mat=M['skirt']))
    out.append(box('DoorSeam2', (0.012, 0.020, 1.560), (x1 + 0.078, -1.282, 2.300),
                   mat=M['skirt']))
    # grab handle + latch
    out.append(box('DoorHandle', (0.055, 0.070, 0.180), (x1 + 0.020, -1.300, 2.260),
                   mat=M['chrome'], bevel=0.02))
    out.append(cyl('DoorBar', 0.016, 0.300, (x0 - 0.030, -1.300, 2.020),
                   rot=(0, radians(90), 0), mat=M['chrome'], segs=12))
    out.append(box('DoorPull', (0.040, 0.030, 0.230), (x0 - 0.030, -1.296, 2.340),
                   mat=M['chrome'], bevel=0.012))
    # entry step + light
    out.append(box('StepWell', (0.74, 0.170, 0.030), ((x0 + x1) * 0.5, -1.130, 0.760),
                   mat=M['black_rough'], bevel=0.02))
    out.append(box('StepEdge', (0.76, 0.030, 0.022), ((x0 + x1) * 0.5, -1.212, 0.780),
                   mat=M['chrome']))
    out.append(box('StepLight', (0.60, 0.020, 0.030), ((x0 + x1) * 0.5, -1.222, 0.855),
                   mat=M['lum_copper']))
    return out


def logo(M):
    out = []
    out.append(box('LogoBase', (0.030, 0.240, 0.240), (6.010, 0.0, 3.280),
                   rot=(radians(45), 0, 0), mat=M['gold'], bevel=0.012))
    out.append(box('LogoRear', (0.030, 0.190, 0.190), (-6.010, 0.0, 2.700),
                   rot=(radians(45), 0, 0), mat=M['gold'], bevel=0.010))
    return out


def build(M):
    out = []
    out += belt_trim(M)
    out += front_lights(M)
    out += mirrors(M)
    out += front_extra(M)
    out += entry_door(M)
    out += logo(M)
    return out

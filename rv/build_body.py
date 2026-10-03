# -*- coding: utf-8 -*-
"""Body shell, glazing, entry door, graphite skirt with real wheel arches."""
import bpy, bmesh
from math import radians, sqrt
from mathutils import Vector

from . import spec as S
from .lib_util import (box, cyl, loft, rrect_profile, flat_cap, band_sweep,
                       mesh_from_pydata, shade_auto, rrect_plate, ring)

BODY = []


# --------------------------------------------------------------- mesh utils
def _bisect(ob, co, no):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                           dist=1e-5, plane_co=Vector(co), plane_no=Vector(no),
                           clear_inner=False, clear_outer=False)
    bm.to_mesh(ob.data)
    bm.free()


def cut_rects(ob, rects):
    """rects: (side, x0, x1, z0, z1) on the flat side walls."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        ay = abs(c.y)
        if ay < 1.19 or ay > 1.34:
            continue
        sd = 1.0 if c.y > 0 else -1.0
        for (si, x0, x1, z0, z1) in rects:
            if si != sd:
                continue
            if x0 + 1e-4 < c.x < x1 - 1e-4 and z0 + 1e-4 < c.z < z1 - 1e-4:
                kill.append(f)
                break
    if kill:
        bmesh.ops.delete(bm, geom=kill, context='FACES')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ob.data)
    bm.free()


def solidify_none(ob):
    pass


# --------------------------------------------------------------- glazing
def xz_plate(name, x0, x1, z0, z1, y0, y1, rc, mat, n=6):
    prof = rrect_profile((x1 - x0) * 0.5, (z1 - z0) * 0.5, rc, rc, n=n, ns=0)
    return loft(name, prof,
                [{'x': y0, 'cy': (x0 + x1) * 0.5, 'cz': (z0 + z1) * 0.5},
                 {'x': y1, 'cy': (x0 + x1) * 0.5, 'cz': (z0 + z1) * 0.5}],
                mat=mat, smooth=False, plane='XZ')


def yz_plate(name, cy0, cy1, z0, z1, x0, x1, rc, mat, n=6):
    prof = rrect_profile((cy1 - cy0) * 0.5, (z1 - z0) * 0.5, rc, rc, n=n, ns=0)
    return loft(name, prof,
                [{'x': x0, 'cy': (cy0 + cy1) * 0.5, 'cz': (z0 + z1) * 0.5},
                 {'x': x1, 'cy': (cy0 + cy1) * 0.5, 'cz': (z0 + z1) * 0.5}],
                mat=mat, smooth=False)


def glazing(M):
    out = []
    for sd in (-1, 1):
        items = [(a, b, c, d, 0.0) for (a, b, c, d) in S.WINDOWS]
        if sd < 0:
            items.append(tuple(S.DOOR) + (0.0125,))      # sits on the door skin
        else:
            items.append(tuple(S.DRIVER_WIN) + (0.0,))
        for i, (x0, x1, z0, z1, off) in enumerate(items):
            hx = (x1 - x0) * 0.5
            hz = (z1 - z0) * 0.5
            cx = (x0 + x1) * 0.5
            cz = (z0 + z1) * 0.5
            out.append(ring('gasket_%d_%d' % (sd, i), hx + 0.075, hz + 0.075,
                            hx - 0.013, hz - 0.013, 0.130,
                            sd * (S.HW - 0.006 + off),
                            sd * (S.HW + 0.006 + off), cx, cz, 'Y', M['black'], n=8))
            gl = xz_plate('glass_%d_%d' % (sd, i), x0 - 0.007, x1 + 0.007,
                          z0 - 0.007, z1 + 0.007, sd * (S.HW + 0.011 + off),
                          sd * (S.HW + 0.023 + off), 0.085, M['glass'])
            out.append(gl)
    return out


# --------------------------------------------------------------- shell
def shell(M):
    prof = rrect_profile(S.HW, S.HH, S.RC, S.RB, n=10, ns=6)
    xs = [-S.X_F + 0.20 * i for i in range(0, 61)]
    st = [{'x': x, 'cz': S.CZ} for x in xs]
    body = loft('BodyShell', prof, st, mat=M['body'], smooth=True, caps=False)
    out = [body]
    out.append(flat_cap('FrontCap', prof, S.X_F, cz=S.CZ,
                        scales=(1.0, 0.972, 0.944, 0.916, 0.888, 0.860),
                        mat=M['body'], open_last=True, smooth=True))
    out.append(flat_cap('RearCap', prof, S.X_R, cz=S.CZ,
                        scales=(1.0, 0.965, 0.930, 0.895, 0.860),
                        mat=M['body'], open_last=False, smooth=True))
    return out


def front_face(M):
    out = []
    # opaque fill above / below the windscreen (tucked behind the cap ring)
    out.append(yz_plate('FrontFillLow', -1.095, 1.095, 1.585, 1.995, 5.986, 5.995,
                        0.03, M['body']))
    out.append(yz_plate('FrontFillHigh', -1.095, 1.095, 3.095, 3.520, 5.986, 5.995,
                        0.03, M['body']))
    # dark windscreen surround + glass
    out.append(yz_plate('WindGasket', -1.112, 1.112, 1.888, 3.172, 5.996, 6.006,
                        0.155, M['black'], n=8))
    out.append(yz_plate('WindGlass', -1.050, 1.050, 1.950, 3.110, 6.004, 6.026,
                        0.130, M['glass_front'], n=8))
    # wiper arms
    for s in (-1, 1):
        out.append(box('Wiper_%d' % s, (0.78, 0.030, 0.028),
                       (5.90, s * 0.52, 1.760), rot=(0, 0, 0), mat=M['black']))
        out.append(cyl('WiperHub_%d' % s, 0.045, 0.05, (5.56, s * 0.52, 1.775),
                       rot=(0, radians(90), 0), mat=M['black'], segs=10))
    return out


def rear_face(M):
    out = []
    out.append(yz_plate('RearWall', -1.16, 1.16, 1.55, 3.55, -5.60, -5.55,
                        0.10, M['wall']))
    out.append(yz_plate('RearGasket', -0.630, 0.630, 2.150, 2.980, -6.008, -5.996,
                        0.075, M['skirt']))
    out.append(yz_plate('RearGlass', -0.560, 0.560, 2.230, 2.900, -6.024, -6.004,
                        0.055, M['glass']))
    # high-level brake light bar
    for s in (-1, 1):
        out.append(box('RearLed_%d' % s, (0.016, 0.30, 0.048),
                       (-6.020, s * 0.62, 3.300), mat=M['led_red']))
    out.append(box('RearLedMid', (0.016, 0.72, 0.048), (-6.020, 0.0, 3.300),
                   mat=M['led_red']))
    # tail light blades
    for s in (-1, 1):
        out.append(box('TailBlade_%d' % s, (0.012, 0.115, 1.10),
                       (-6.030, s * 1.120, 2.100), mat=M['led_red']))
        out.append(box('TailTrim_%d' % s, (0.014, 0.150, 1.18),
                       (-6.022, s * 1.120, 2.100), mat=M['skirt']))
        out.append(box('TailAmber_%d' % s, (0.014, 0.095, 0.115),
                       (-6.026, s * 1.120, 1.470), mat=M['led_amber']))
    return out


def garage_door(M):
    out = []
    out.append(box('GarageDoor', (0.040, 2.240, 0.980), (-6.010, 0.0, 1.100),
                   mat=M['body'], bevel=0.020, segs=2))
    out.append(box('GarageSeam', (0.026, 2.170, 0.030), (-6.032, 0.0, 1.560),
                   mat=M['skirt']))
    out.append(box('GarageHandle', (0.060, 0.230, 0.045), (-6.045, 0.0, 1.140),
                   mat=M['chrome'], bevel=0.012))
    for s in (-1, 1):
        out.append(box('GarageHandleB_%d' % s, (0.045, 0.040, 0.045),
                       (-6.038, s * 0.075, 1.135), mat=M['chrome']))
    return out


# --------------------------------------------------------------- skirt
ARCHES = ((S.AX_F, 0.578), (S.AX_R1, 0.590), (S.AX_R2, 0.590))


def _zbot(x):
    z = S.Z_SKIRT_BOT
    for (cx, ra) in ARCHES:
        d = abs(x - cx)
        if d < ra:
            z = max(z, S.WHEEL_R + sqrt(max(ra * ra - d * d, 0.0)))
    return z


def skirt(M):
    out = []
    xs = []
    x = S.X_R
    while x <= S.X_F + 1e-6:
        xs.append(round(x, 4))
        x += 0.018
    zb = [_zbot(v) for v in xs]
    zt = [S.Z_SKIRT_TOP] * len(xs)
    for sd in (-1, 1):
        out.append(band_sweep('Skirt_%d' % sd, xs, zt, zb,
                              sd * S.Y_SKIRT_OUT, sd * S.Y_SKIRT_IN, M['skirt']))
        # arch lip so the opening reads as a real wheel well
        for (cx, ra) in ARCHES:
            out.append(_arch_lip(sd, cx, ra, M))
    # rear closure + bumper
    out.append(box('RearSkirt', (0.14, 2.444, 0.90), (-5.94, 0.0, 1.07),
                   mat=M['skirt'], bevel=0.03))
    out.append(box('RearBumper', (0.16, 2.470, 0.42), (-5.94, 0.0, 0.83),
                   mat=M['skirt'], bevel=0.05, segs=3))
    # front closure + bumper
    out.append(box('FrontBumper', (0.34, 2.500, 0.34), (5.84, 0.0, 0.79),
                   mat=M['skirt'], bevel=0.07, segs=3))
    out.append(box('FrontSkirt', (0.12, 2.444, 0.30), (5.95, 0.0, 0.79),
                   mat=M['skirt'], bevel=0.03))
    # compartment seams + handles on both flanks
    seg = [(-5.72, -4.62), (-4.45, -3.32), (-1.80, -0.40), (-0.20, 1.20),
           (1.40, 2.86), (3.00, 4.10), (4.20, 5.55)]
    for sd in (-1, 1):
        for i, (a, b) in enumerate(seg):
            c = (a + b) * 0.5
            w = (b - a) - 0.10
            out.append(box('SkirtDoor_%d_%d' % (sd, i), (w, 0.022, 0.800),
                           (c, sd * (S.Y_SKIRT_OUT - 0.009), 1.005),
                           mat=M['skirt'], bevel=0.018, segs=2))
            out.append(box('SkirtSeam_%d_%d' % (sd, i), (w + 0.055, 0.020, 0.018),
                           (c, sd * (S.Y_SKIRT_OUT - 0.004), 1.428), mat=M['black']))
            out.append(box('SkirtSeamB_%d_%d' % (sd, i), (w + 0.055, 0.020, 0.018),
                           (c, sd * (S.Y_SKIRT_OUT - 0.004), 0.592), mat=M['black']))
            out.append(box('SkirtSeamC_%d_%d' % (sd, i), (0.020, 0.020, 0.870),
                           (a + 0.022, sd * (S.Y_SKIRT_OUT - 0.004), 1.005),
                           mat=M['black']))
            out.append(box('SkirtSeamD_%d_%d' % (sd, i), (0.020, 0.020, 0.870),
                           (b - 0.022, sd * (S.Y_SKIRT_OUT - 0.004), 1.005),
                           mat=M['black']))
            if i in (0, 1, 2, 3, 4):
                out.append(box('SkirtPull_%d_%d' % (sd, i), (0.13, 0.026, 0.038),
                               (c + w * 0.30, sd * (S.Y_SKIRT_OUT + 0.006), 1.27),
                               mat=M['chrome'], bevel=0.008))
        out.append(box('ArchTrim_%d' % sd, (1.42, 0.020, 0.040),
                       ((S.AX_R1 + S.AX_R2) * 0.5, sd * (S.Y_SKIRT_OUT + 0.006), 1.185),
                       rot=(0, 0, 0), mat=M['chrome'], bevel=0.010))
        out.append(box('SkirtGap_%d' % sd, (11.80, 0.016, 0.020),
                       (0.0, sd * (S.Y_SKIRT_OUT - 0.002), S.Z_SKIRT_TOP + 0.010),
                       mat=M['black']))
        # amber side markers
        for mx in (-4.90, -2.05, 0.60, 3.10, 4.75):
            out.append(box('Marker_%d_%.1f' % (sd, mx), (0.075, 0.020, 0.042),
                           (mx, sd * (S.Y_SKIRT_OUT - 0.002), 1.40),
                           mat=M['led_amber']))
    return out


def _arch_lip(sd, cx, ra, M):
    """Curved black lip closing the top of the wheel opening."""
    verts, faces = [], []
    n = 16
    y0 = sd * (S.Y_SKIRT_IN - 0.004)
    y1 = sd * (S.Y_SKIRT_OUT + 0.002)
    outer = ra + 0.024
    for i in range(n + 1):
        t = i / float(n)
        # inner arc then outer arc, as a quad strip
        d0 = ra * (1 - 1e-6)
        a = -1.0 + 2.0 * t
        ang = a * radians(78.0)
        ca, sa = __import__('math').cos(ang), __import__('math').sin(ang)
        verts.append((cx + ra * sa * 1.0, y1, S.WHEEL_R + ra * ca))
        verts.append((cx + outer * sa, y1, S.WHEEL_R + outer * ca))
        verts.append((cx + outer * sa, y0, S.WHEEL_R + outer * ca))
        verts.append((cx + ra * sa, y0, S.WHEEL_R + ra * ca))
    for i in range(n):
        a, b = i * 4, (i + 1) * 4
        for k in range(4):
            k2 = (k + 1) % 4
            faces.append((a + k, a + k2, b + k2, b + k))
    faces.append((0, 1, 2, 3))
    a = n * 4
    faces.append((a + 3, a + 2, a + 1, a))
    return mesh_from_pydata('ArchLip_%d_%.2f' % (sd, cx), verts, faces, M['black'])


def build(M):
    """Return every exterior-shell object."""
    out = []
    sh = shell(M)
    body = sh[0]
    rects = []
    for sd in (-1, 1):
        items = list(S.WINDOWS)
        items = items + ([S.DOOR] if sd < 0 else [S.DRIVER_WIN])
        for (x0, x1, z0, z1) in items:
            rects.append((sd, x0, x1, z0, z1))
    xcuts = sorted(set([r[1] for r in rects] + [r[2] for r in rects]))
    for xv in xcuts:
        _bisect(body, (xv, 0, 0), (1, 0, 0))
    for zv in sorted(set([r[3] for r in rects] + [r[4] for r in rects])):
        _bisect(body, (0, 0, zv), (0, 0, 1))
    cut_rects(body, rects)
    shade_auto(body, 34.0)
    out += sh
    out += front_face(M)
    out += rear_face(M)
    out += garage_door(M)
    out += glazing(M)
    out += skirt(M)
    return out

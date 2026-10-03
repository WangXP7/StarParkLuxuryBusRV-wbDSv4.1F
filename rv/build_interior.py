# -*- coding: utf-8 -*-
"""Interior fit-out: cockpit, lounge, galley, bath, raised rear bedroom, ceilings."""
import bpy
from math import radians, cos, sin
from . import spec as S
from .lib_util import box, cyl, sphere, revolve_y, curve_tube, shade_auto

YI = 1.155          # interior wall face
ZF = 1.055          # floor
ZC = S.Z_CEIL       # ceiling 3.045
XR = -5.760
XF = 5.760


def shell(M):
    out = []
    out.append(box('IntFloor', (11.55, 2.310, 0.045), (0.0, 0.0, ZF - 0.022),
                   mat=M['carpet']))
    out.append(box('IntCeil', (11.50, 2.310, 0.055), (0.0, 0.0, ZC + 0.028),
                   mat=M['ceiling']))
    # cove light rails down both sides of the ceiling
    for s in (-1, 1):
        out.append(box('Cove_%d' % s, (11.20, 0.055, 0.045),
                       (0.0, s * 1.075, ZC - 0.030), mat=M['lum_warm']))
        out.append(box('CoveLip_%d' % s, (11.20, 0.055, 0.075),
                       (0.0, s * 0.995, ZC - 0.062), mat=M['trim']))
    # lower interior wall band + window pillars + header band
    bands = [(-5.95, -4.42), (-4.30, -2.30), (-1.79, 0.69), (0.99, 3.59), (4.29, 5.95)]
    for s in (-1, 1):
        out.append(box('WallLow_%d' % s, (11.70, 0.055, 0.520),
                       (0.0, s * (YI + 0.026), ZF + 0.270), mat=M['wall']))
        out.append(box('WallHead_%d' % s, (11.70, 0.055, 0.090),
                       (0.0, s * (YI + 0.026), 3.010), mat=M['wall']))
        for i, (a, b) in enumerate(bands):
            c = (a + b) * 0.5
            out.append(box('Pillar_%d_%d' % (s, i), (b - a, 0.055, 0.940),
                           (c, s * (YI + 0.026), 2.525), mat=M['wall']))
    return out


def cockpit(M):
    out = []
    xd = 5.62
    out.append(box('Dash', (0.42, 2.260, 0.300), (xd, 0.0, 1.640), mat=M['black'],
                   bevel=0.05, segs=3))
    out.append(box('DashPad', (0.34, 2.180, 0.150), (xd - 0.12, 0.0, 1.880),
                   mat=M['leather'], bevel=0.05, segs=3))
    out.append(box('DashTrim', (0.30, 2.140, 0.045), (xd - 0.10, 0.0, 1.760),
                   mat=M['wood'], bevel=0.012))
    out.append(box('Cluster', (0.10, 0.560, 0.240), (xd - 0.24, 0.620, 1.860),
                   rot=(0, 0, 0), mat=M['black'], bevel=0.03))
    out.append(box('NavScr', (0.045, 0.420, 0.280), (xd - 0.20, -0.520, 1.830),
                   mat=M['black'], bevel=0.02))
    out.append(box('NavGlass', (0.012, 0.380, 0.240), (xd - 0.228, -0.520, 1.830),
                   mat=M['lum_white']))
    # steering wheel (left hand drive -> +Y side)
    sw = (xd - 0.32, 0.620, 1.800)
    out.append(cyl('Col', 0.055, 0.34, (sw[0] + 0.10, sw[1], sw[2]),
                   rot=(0, radians(72), 0), mat=M['black'], segs=14))
    out.append(cyl('Wheel', 0.205, 0.045, sw, rot=(0, radians(64), 0),
                   mat=M['black'], segs=28))
    out.append(revolve_y('WheelRim', [(0.185, -0.028), (0.225, -0.028),
                                      (0.225, 0.028), (0.185, 0.028)],
                         sw[0], 0.0, sw[2], mat=M['leather'], segs=28))
    for s in (-1, 1):
        out.append(box('Chair%d' % s, (0.52, 0.60, 0.130),
                       (4.86, s * 0.620, 1.470), mat=M['leather'], bevel=0.05, segs=3))
        out.append(box('ChairBack%d' % s, (0.22, 0.58, 0.760),
                       (4.64, s * 0.620, 1.860), rot=(0, radians(-7), 0),
                       mat=M['leather'], bevel=0.07, segs=3))
        out.append(box('ChairHead%d' % s, (0.16, 0.40, 0.190),
                       (4.56, s * 0.620, 2.290), rot=(0, radians(-7), 0),
                       mat=M['leather'], bevel=0.05, segs=3))
        for a in (-1, 1):
            out.append(box('ChairArm%d%d' % (s, a), (0.42, 0.070, 0.070),
                           (4.86, s * 0.620 + a * 0.300, 1.640),
                           mat=M['black'], bevel=0.02))
        out.append(cyl('ChairPost%d' % s, 0.070, 0.33, (4.86, s * 0.620, 1.245),
                       mat=M['alu'], segs=14))
        out.append(cyl('ChairBase%d' % s, 0.230, 0.045, (4.86, s * 0.620, 1.095),
                       mat=M['alu'], segs=22))
    return out


def lounge(M):
    out = []
    # L-shaped cream sofa along the vehicle's left (+Y)
    out.append(box('SofaA', (2.30, 0.610, 0.300), (2.55, 0.830, 1.320),
                   mat=M['leather'], bevel=0.06, segs=3))
    out.append(box('SofaAB', (2.30, 0.220, 0.640), (2.55, 1.020, 1.640),
                   rot=(radians(-9), 0, 0), mat=M['leather'], bevel=0.07, segs=3))
    out.append(box('SofaB', (0.560, 0.610, 0.300), (3.48, 0.520, 1.320),
                   rot=(0, 0, radians(90)), mat=M['leather'], bevel=0.06, segs=3))
    for i in range(4):
        out.append(box('CushA%d' % i, (0.520, 0.130, 0.400),
                       (1.62 + i * 0.60, 0.985, 1.620), rot=(radians(-9), 0, 0),
                       mat=M['leather'], bevel=0.06, segs=3))
        out.append(box('CushS%d' % i, (0.520, 0.560, 0.150),
                       (1.62 + i * 0.60, 0.840, 1.500), mat=M['leather'],
                       bevel=0.05, segs=3))
    # two facing lounge chairs on the vehicle's right (-Y)
    for i, cx in enumerate((1.55, 2.85)):
        out.append(box('LChair%d' % i, (0.56, 0.580, 0.300), (cx, -0.780, 1.320),
                       mat=M['leather'], bevel=0.06, segs=3))
        out.append(box('LChairB%d' % i, (0.22, 0.560, 0.700),
                       (cx - 0.24, -0.780, 1.660), rot=(0, radians(6), 0),
                       mat=M['leather'], bevel=0.07, segs=3))
        out.append(cyl('LChairP%d' % i, 0.230, 0.045, (cx, -0.780, 1.095),
                       mat=M['alu'], segs=20))
        out.append(cyl('LChairS%d' % i, 0.070, 0.24, (cx, -0.780, 1.215),
                       mat=M['alu'], segs=12))
    # round marble table on a gold pedestal
    out.append(cyl('TableTop', 0.450, 0.055, (2.20, -0.230, 1.520),
                   mat=M['marble'], segs=40))
    out.append(cyl('TableCol', 0.115, 0.430, (2.20, -0.230, 1.285),
                   mat=M['gold'], segs=24))
    out.append(cyl('TableBase', 0.300, 0.035, (2.20, -0.230, 1.085),
                   mat=M['gold'], segs=28))
    out.append(cyl('Vase', 0.070, 0.150, (2.20, -0.230, 1.620),
                   mat=M['marble'], segs=18))
    for k in range(5):
        a = radians(72 * k)
        out.append(box('Leaf%d' % k, (0.090, 0.016, 0.220),
                       (2.20 + 0.05 * cos(a), -0.230 + 0.05 * sin(a), 1.760),
                       rot=(radians(18) * sin(a), radians(-18) * cos(a), 0),
                       mat=M['wall']))
    out.append(box('Rug', (2.60, 1.900, 0.012), (2.30, -0.150, 1.070),
                   mat=M['carpet']))
    return out


def galley(M):
    out = []
    zc = ZF + 0.450
    out.append(box('GalleyCab', (2.30, 0.580, 0.880), (-0.30, -0.855, ZF + 0.440),
                   mat=M['wood'], bevel=0.02))
    out.append(box('GalleyTop', (2.36, 0.640, 0.055), (-0.30, -0.860, ZF + 0.900),
                   mat=M['marble'], bevel=0.012))
    out.append(box('Spash', (2.30, 0.040, 0.480), (-0.30, -1.120, ZF + 1.170),
                   mat=M['marble']))
    out.append(box('Sink', (0.520, 0.360, 0.045), (0.22, -0.870, ZF + 0.912),
                   mat=M['alu'], bevel=0.04, segs=3))
    out.append(cyl('Tap', 0.030, 0.300, (0.22, -1.055, ZF + 1.060),
                   mat=M['gold'], segs=14))
    out.append(cyl('TapArm', 0.024, 0.180, (0.15, -0.990, ZF + 1.205),
                   rot=(radians(70), 0, 0), mat=M['gold'], segs=12))
    out.append(box('Hob', (0.560, 0.400, 0.020), (-0.70, -0.870, ZF + 0.918),
                   mat=M['black'], bevel=0.02))
    for i in range(2):
        for j in range(2):
            out.append(cyl('Burn%d%d' % (i, j), 0.105, 0.014,
                           (-0.86 + i * 0.30, -0.985 + j * 0.230, ZF + 0.930),
                           mat=M['trim'], segs=20))
    for i in range(3):
        out.append(box('UpCab%d' % i, (0.700, 0.360, 0.560),
                       (-1.04 + i * 0.760, -0.985, 2.620), mat=M['wood'],
                       bevel=0.02))
        out.append(box('UpCabDoor%d' % i, (0.640, 0.020, 0.500),
                       (-1.04 + i * 0.760, -0.815, 2.620), mat=M['oak']))
        out.append(cyl('UpCabKnob%d' % i, 0.018, 0.060,
                       (-1.04 + i * 0.760, -0.800, 2.430),
                       rot=(radians(90), 0, 0), mat=M['gold'], segs=10))
    out.append(box('Fridge', (0.720, 0.700, 1.900), (0.62, -0.780, ZF + 0.950),
                   mat=M['alu'], bevel=0.03))
    out.append(box('FridgeSeam', (0.030, 0.030, 1.760), (0.62, -1.128, ZF + 0.950),
                   mat=M['black']))
    out.append(cyl('FridgeBar', 0.018, 0.700, (0.50, -1.145, ZF + 1.180),
                   rot=(0, radians(90), 0), mat=M['gold'], segs=12))
    out.append(box('BarTop', (1.90, 0.430, 0.050), (-0.30, 0.910, ZF + 0.900),
                   mat=M['marble']))
    out.append(box('BarCab', (1.90, 0.400, 0.860), (-0.30, 0.930, ZF + 0.430),
                   mat=M['wood'], bevel=0.02))
    return out


def bath(M):
    out = []
    out.append(box('BathWall', (1.15, 0.070, 2.000), (-1.280, -0.360, ZF + 1.000),
                   mat=M['wood'], bevel=0.02))
    out.append(box('BathDoor', (0.900, 0.060, 1.960), (-1.300, 0.520, ZF + 0.980),
                   mat=M['wood_light'], bevel=0.02))
    out.append(cyl('BathLatch', 0.028, 0.060, (-1.300, 0.560, ZF + 0.980),
                   rot=(radians(90), 0, 0), mat=M['chrome'], segs=12))
    out.append(box('ShowerTray', (0.900, 0.780, 0.075), (-1.180, -0.720, ZF + 0.038),
                   mat=M['marble'], bevel=0.03))
    out.append(box('ShowerGlass', (0.900, 0.030, 1.880), (-1.180, -0.330, ZF + 1.020),
                   mat=M['shower']))
    out.append(box('ShowerGlassS', (0.030, 0.780, 1.880), (-0.730, -0.720, ZF + 1.020),
                   mat=M['shower']))
    out.append(cyl('ShowerHead', 0.075, 0.050, (-1.560, -0.720, ZF + 1.850),
                   rot=(radians(30), 0, 0), mat=M['chrome'], segs=18))
    out.append(box('Vanity', (0.180, 0.720, 0.190), (-1.560, 0.640, ZF + 0.870),
                   mat=M['marble'], bevel=0.02))
    out.append(cyl('Basin', 0.170, 0.130, (-1.520, 0.640, ZF + 0.950),
                   mat=M['marble'], segs=26))
    out.append(cyl('BasinTap', 0.022, 0.240, (-1.600, 0.640, ZF + 1.060),
                   mat=M['gold'], segs=12))
    out.append(box('Mirror', (0.030, 0.560, 0.760), (-1.610, 0.640, ZF + 1.620),
                   mat=M['lens']))
    out.append(box('MirrorLight', (0.030, 0.620, 0.045), (-1.615, 0.640, ZF + 2.030),
                   mat=M['lum_warm']))
    out.append(box('ToiletBase', (0.400, 0.500, 0.300), (-1.450, -0.150, ZF + 0.150),
                   mat=M['marble'], bevel=0.06, segs=3))
    out.append(cyl('ToiletBowl', 0.190, 0.230, (-1.450, -0.150, ZF + 0.360),
                   mat=M['marble'], segs=24))
    out.append(box('ToiletLid', (0.380, 0.460, 0.045), (-1.450, -0.150, ZF + 0.500),
                   mat=M['marble'], bevel=0.02))
    return out


def bedroom(M):
    out = []
    zb = S.Z_BEDDECK
    out.append(box('BedDeck', (4.020, 2.310, 0.070), (-3.830, 0.0, zb - 0.035),
                   mat=M['wood']))
    out.append(box('DeckFace', (0.060, 2.310, 0.560), (-1.830, 0.0, zb - 0.320),
                   mat=M['oak']))
    # steps up from the lounge level
    for i in range(3):
        out.append(box('Step%d' % i, (0.260, 1.100, 0.190),
                       (-1.980 + i * 0.245, -0.150, zb - 0.095 - i * 0.190),
                       mat=M['wood_light'], bevel=0.02))
    out.append(cyl('StepRail', 0.024, 1.020, (-1.960, 0.470, zb + 0.510),
                   rot=(0, 0, 0), mat=M['gold'], segs=12))
    for zz in (zb + 0.150, zb + 0.360, zb + 0.570):
        out.append(cyl('RailPost%.2f' % zz, 0.018, 0.420, (-1.960, 0.470, zz),
                       mat=M['gold'], segs=10))
    # island bed (head against the left wall)
    out.append(box('BedBase', (2.100, 1.760, 0.400), (-4.420, 0.130, zb + 0.200),
                   mat=M['wood'], bevel=0.03))
    out.append(box('Mattress', (2.060, 1.720, 0.260), (-4.420, 0.130, zb + 0.530),
                   mat=M['ceiling'], bevel=0.06, segs=3))
    out.append(box('BedRunner', (0.760, 1.740, 0.075), (-3.760, 0.130, zb + 0.690),
                   mat=M['leather'], bevel=0.03))
    for i, yy in enumerate((0.640, 0.220, -0.200, -0.560)):
        out.append(box('Pillow%d' % i, (0.300, 0.330, 0.150),
                       (-5.130, yy, zb + 0.740), rot=(0, radians(8), 0),
                       mat=M['ceiling'], bevel=0.07, segs=3))
    out.append(box('HeadBoard', (0.080, 1.900, 0.900), (-5.500, 0.130, zb + 0.470),
                   mat=M['wood'], bevel=0.03))
    out.append(box('BedLight', (0.070, 1.640, 0.040), (-5.430, 0.130, zb + 0.960),
                   mat=M['lum_copper']))
    out.append(box('Wardrobe', (1.500, 0.520, 1.560), (-2.700, -0.830, zb + 0.780),
                   mat=M['wood'], bevel=0.02))
    for i in range(2):
        out.append(box('WardDoor%d' % i, (0.660, 0.020, 1.480),
                       (-3.050 + i * 0.700, -1.100, zb + 0.780), mat=M['oak']))
        out.append(cyl('WardKnob%d' % i, 0.018, 0.070,
                       (-3.050 + i * 0.700, -1.115, zb + 0.560),
                       rot=(radians(90), 0, 0), mat=M['gold'], segs=10))
    out.append(box('BedTVCab', (1.700, 0.330, 0.460), (-2.700, 0.960, zb + 0.230),
                   mat=M['wood'], bevel=0.02))
    return out


def overhead(M):
    """Overhead cabinet runs on the far wall. Two jobs: real RV furniture, and
    they block the see-through so the glazing reads as interior, not daylight."""
    out = []
    runs = [
        (1.00, 3.72, 2.235, 2.965, 7),      # lounge
        (-1.82, 0.78, 2.300, 2.965, 5),     # galley
        (-4.42, -2.18, 2.320, 2.965, 4),    # bedroom
    ]
    for (x0, x1, z0, z1, nd) in runs:
        cx = (x0 + x1) * 0.5
        for s in (-1, 1):
            deep = (s > 0)
            dep = 0.185 if deep else 0.105
            zz0 = z0 if deep else z0 + 0.245
            yc = 1.062 if deep else 1.098
            out.append(box('OverCab_%.1f_%d' % (cx, s), (x1 - x0, dep, z1 - zz0),
                           (cx, s * yc, (zz0 + z1) * 0.5), mat=M['wood'],
                           bevel=0.02))
            out.append(box('OverCabLite_%.1f_%d' % (cx, s), (x1 - x0 - 0.10, 0.030, 0.028),
                           (cx, s * (yc - 0.096), zz0 + 0.052), mat=M['lum_copper']))
            for d in range(nd):
                dx = x0 + 0.10 + d * ((x1 - x0) - 0.20) / (nd - 1)
                out.append(box('OverDoor_%.1f_%d_%d' % (cx, s, d),
                               (0.020, 0.030, z1 - zz0 - 0.10),
                               (dx, s * (yc - 0.077), (zz0 + z1) * 0.5),
                               mat=M['oak']))
    for (x0, x1, z0, z1) in S.WINDOWS:
        for sd in (-1, 1):
            out.append(box('AmberBack_%.1f_%d' % (x0, sd),
                           (x1 - x0 + 0.24, 0.026, z1 - z0 + 0.06),
                           ((x0 + x1) * 0.5, sd * 1.232, (z0 + z1) * 0.5),
                           mat=M['lum_amber']))
            # backlit silhouettes, so each window reads as a real room rather
            # than a glowing panel: they sit between the glass and the glow
            W = x1 - x0
            cx = (x0 + x1) * 0.5
            YD = sd * 1.246

            def g(nm, w, h, x, z, mat, d=0.030):
                out.append(box(nm, (w, d, h), (x, YD, z), mat=mat))

            if x0 > 0.5:                          # lounge - sofa, cushions, plant
                g('WSofa_%.1f_%d' % (x0, sd), W - 0.10, 0.30, cx, z0 + 0.20,
                  M['leather'])
                for k in range(3):
                    g('WCsn_%.1f_%d_%d' % (x0, sd, k), 0.52, 0.36,
                      x0 + 0.42 + k * 0.78, z0 + 0.46, M['leather'], 0.040)
                g('WPlt_%.1f_%d' % (x0, sd), 0.20, 0.26, x1 - 0.34, z0 + 0.40,
                  M['wood_light'], 0.060)
                g('WPltL_%.1f_%d' % (x0, sd), 0.28, 0.10, x1 - 0.34, z0 + 0.62,
                  M['wall'], 0.080)
            elif x0 < -1.0:                       # galley - counter, splash, cupboards
                g('WCtr_%.1f_%d' % (x0, sd), W - 0.10, 0.055, cx, z0 + 0.16,
                  M['stone'], 0.075)
                g('WSpl_%.1f_%d' % (x0, sd), W - 0.10, 0.32, cx, z0 + 0.34,
                  M['wood_light'], 0.026)
                g('WUp_%.1f_%d' % (x0, sd), W - 0.10, 0.34, cx, z1 - 0.24, M['oak'])
                for k in range(3):
                    g('WDoor_%.1f_%d_%d' % (x0, sd, k), (W - 0.30) / 3.4, 0.26,
                      x0 + 0.30 + k * (W - 0.60) / 2.0, z1 - 0.24, M['wood_light'],
                      0.020)
                g('WTap_%.1f_%d' % (x0, sd), 0.045, 0.24, cx + 0.30, z0 + 0.30,
                  M['gold'], 0.045)
            else:                                 # bedroom - mattress and pillows
                g('WBed_%.1f_%d' % (x0, sd), W - 0.10, 0.15, cx, z0 + 0.12,
                  M['ceiling'])
                g('WRun_%.1f_%d' % (x0, sd), 0.40, 0.19, x1 - 0.35, z0 + 0.14,
                  M['leather'])
                for k in range(2):
                    g('WPil_%.1f_%d_%d' % (x0, sd, k), 0.46, 0.17,
                      x0 + 0.32 + k * 0.58, z0 + 0.24, M['ceiling'], 0.050)
                g('WHB_%.1f_%d' % (x0, sd), W - 0.06, 0.42, cx, z0 + 0.34,
                  M['oak'], 0.022)
    # backlit marble splash panel behind the galley run (reads through the glass)
    out.append(box('GalleyPanel', (2.50, 0.030, 0.700), (-0.52, 1.130, 1.780),
                   mat=M['marble']))
    out.append(box('GalleyPanelLite', (2.34, 0.030, 0.028), (-0.52, 1.146, 2.120),
                   mat=M['lum_copper']))
    # lounge feature wall
    out.append(box('LoungePanel', (2.40, 0.030, 0.900), (2.36, 1.130, 1.900),
                   mat=M['wood']))
    for i in range(3):
        out.append(box('LoungeSlat%d' % i, (2.24, 0.026, 0.030),
                       (2.36, 1.150, 1.560 + i * 0.300), mat=M['oak']))
    return out


def build(M):
    out = []
    out += shell(M)
    out += overhead(M)
    out += cockpit(M)
    out += lounge(M)
    out += galley(M)
    out += bath(M)
    out += bedroom(M)
    return out


def lights(M):
    """Warm ceiling fixtures + window valance strips - these are what make the
    glazing read as an illuminated interior from outside."""
    out = []
    from .lib_util import box as _box
    for x in (2.60, 1.10, -0.60, -2.60, -4.40):
        for s in (-1, 1):
            out.append(_box('IntLamp_%.1f_%d' % (x, s), (1.05, 0.10, 0.030),
                            (x, s * 0.780, ZC - 0.085), mat=M['lum_warm']))
    out.append(_box('IntLampGal', (1.60, 0.10, 0.030), (-0.30, -1.020, 2.320),
                    mat=M['lum_copper']))
    out.append(_box('IntLampGal2', (1.60, 0.10, 0.030), (-0.30, 0.980, 2.320),
                    mat=M['lum_copper']))
    for (x0, x1, z0, z1) in S.WINDOWS:
        cx = (x0 + x1) * 0.5
        for s in (-1, 1):
            out.append(_box('ValTop_%.1f_%d' % (cx, s), (x1 - x0 - 0.12, 0.030, 0.028),
                            (cx, s * 1.258, z1 - 0.050), mat=M['lum_copper']))
            out.append(_box('ValBot_%.1f_%d' % (cx, s), (x1 - x0 - 0.12, 0.030, 0.028),
                            (cx, s * 1.258, z0 + 0.050), mat=M['lum_copper']))
            out.append(_box('Sill_%.1f_%d' % (cx, s), (x1 - x0 - 0.06, 0.070, 0.055),
                            (cx, s * 1.185, z0 - 0.012), mat=M['oak']))
    return out

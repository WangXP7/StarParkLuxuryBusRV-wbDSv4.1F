# -*- coding: utf-8 -*-
"""Roof kit: drone lift platform, twin AC pods, deck gear and the aft turret."""
import bpy
from math import radians, cos, sin
from . import spec as S
from .lib_util import box, cyl, sphere, revolve_y, shade_auto

Z = S.Z_ROOF


def platform(M):
    out = []
    x0, x1 = 2.45, 4.50
    cx = (x0 + x1) * 0.5
    # trough sunk into the roof crown
    out.append(box('PlatTrough', (x1 - x0, 1.86, 0.170), (cx, 0, Z + 0.010),
                   mat=M['body'], bevel=0.035, segs=3))
    out.append(box('PlatFloor', (x1 - x0 - 0.14, 1.66, 0.035), (cx, 0, Z + 0.078),
                   mat=M['black_rough']))
    for s in (-1, 1):
        # hinged gull-wing lids, standing open
        out.append(box('Lid_%d' % s, (x1 - x0 - 0.16, 0.50, 0.050),
                       (cx, s * 0.545, Z + 0.180),
                       rot=(radians(-38) * s, 0, 0), mat=M['roofkit'], bevel=0.022))
        out.append(box('LidEdge_%d' % s, (x1 - x0 - 0.18, 0.050, 0.065),
                       (cx, s * 0.835, Z + 0.120),
                       rot=(radians(-12) * s, 0, 0), mat=M['roofkit']))
        out.append(cyl('LidHinge_%d' % s, 0.030, 1.60, (cx, s * 0.790, Z + 0.062),
                       rot=(radians(90), 0, 0), mat=M['chrome'], segs=12))
        out.append(cyl('LidArm_%d' % s, 0.026, 0.40, (cx - 0.95, s * 0.585, Z + 0.155),
                       rot=(0, radians(46) * -s, 0), mat=M['chrome'], segs=10))
    # lift deck on four posts
    out.append(box('LiftDeck', (1.26, 1.00, 0.050), (cx, 0, Z + 0.205),
                   mat=M['roofkit'], bevel=0.020))
    for sx in (-1, 1):
        for sy in (-1, 1):
            out.append(cyl('Post%d%d' % (sx, sy), 0.038, 0.145,
                           (cx + sx * 0.48, sy * 0.36, Z + 0.120),
                           mat=M['chrome'], segs=12))
    out.append(box('ChargePad', (0.70, 0.54, 0.050), (cx, 0, Z + 0.252),
                   mat=M['black'], bevel=0.015))
    out.append(box('ChargeLed', (0.60, 0.042, 0.018), (cx, 0.29, Z + 0.256),
                   mat=M['led_drl']))
    return out


def drone(M, cx, cz=Z + 0.720, scale=1.05):
    out = []
    s = scale
    out.append(box('DroneBody', (0.30 * s, 0.20 * s, 0.085 * s), (cx, 0, cz),
                   mat=M['roofkit'], bevel=0.04 * s, segs=3))
    out.append(box('DroneTop', (0.24 * s, 0.16 * s, 0.055 * s), (cx, 0, cz + 0.062 * s),
                   mat=M['black'], bevel=0.03 * s, segs=3))
    for sx in (-1, 1):
        for sy in (-1, 1):
            out.append(cyl('Arm%d%d' % (sx, sy), 0.024 * s, 0.36 * s,
                           (cx + sx * 0.17 * s, sy * 0.20 * s, cz),
                           rot=(radians(90), 0, radians(38) * sx * sy),
                           mat=M['black'], segs=10))
            out.append(cyl('Motor%d%d' % (sx, sy), 0.045 * s, 0.065 * s,
                           (cx + sx * 0.30 * s, sy * 0.28 * s, cz + 0.030 * s),
                           mat=M['roofkit'], segs=14))
            out.append(cyl('Rotor%d%d' % (sx, sy), 0.175 * s, 0.008 * s,
                           (cx + sx * 0.30 * s, sy * 0.28 * s, cz + 0.068 * s),
                           mat=M['black_rough'], segs=28))
            out.append(sphere('Leg%d%d' % (sx, sy), 0.022 * s,
                              (cx + sx * 0.11 * s, sy * 0.09 * s, cz - 0.085 * s),
                              scale=(1, 1, 1.9), mat=M['black']))
    out.append(sphere('Gimbal', 0.070 * s, (cx + 0.14 * s, 0, cz - 0.055 * s),
                      mat=M['roofkit']))
    out.append(cyl('GimbalLens', 0.046 * s, 0.045 * s,
                   (cx + 0.185 * s, 0, cz - 0.050 * s),
                   rot=(0, radians(90), 0), mat=M['lens'], segs=16))
    return out


def roof_gear(M):
    out = []
    # twin climate pods
    for x, w in ((1.05, 1.05), (-0.30, 0.95)):
        out.append(box('Pod%.2f' % x, (w, 0.86, 0.155), (x, -0.04, Z + 0.075),
                       mat=M['body'], bevel=0.055, segs=4))
        out.append(box('PodTop%.2f' % x, (w - 0.16, 0.66, 0.045), (x, -0.04, Z + 0.145),
                       mat=M['black_rough'], bevel=0.02))
        for k in range(5):
            out.append(box('PodFin%.2f_%d' % (x, k), (w - 0.26, 0.045, 0.020),
                           (x, -0.42 + k * 0.19, Z + 0.172), mat=M['skirt']))
    # roof hatch + vents
    out.append(box('RoofHatch', (0.95, 0.72, 0.085), (-1.85, 0.06, Z + 0.045),
                   mat=M['body'], bevel=0.03, segs=3))
    out.append(box('HatchGlass', (0.78, 0.56, 0.035), (-1.85, 0.06, Z + 0.090),
                   mat=M['black']))
    for x in (0.55, -0.95):
        out.append(cyl('Vent%.2f' % x, 0.135, 0.10, (x, 0.55, Z + 0.055),
                       mat=M['alu'], segs=20))
    # aerials
    out.append(cyl('AerialA', 0.022, 0.62, (-5.10, -0.95, Z + 0.31),
                   mat=M['black'], segs=10))
    out.append(cyl('AerialB', 0.018, 0.44, (-5.30, -0.80, Z + 0.22),
                   mat=M['black'], segs=10))
    return out


def turret(M, x=S.TURRET_X):
    out = []
    out.append(cyl('TurBase', 0.470, 0.120, (x, 0.0, Z + 0.045), mat=M['body'],
                   segs=32, bevel=0.03))
    out.append(cyl('TurRing', 0.400, 0.070, (x, 0.0, Z + 0.135), mat=M['gunmetal'],
                   segs=32))
    out.append(box('TurHull', (0.72, 0.60, 0.280), (x, 0.0, Z + 0.290),
                   mat=M['gunmetal'], bevel=0.05, segs=3))
    out.append(box('TurHullTop', (0.56, 0.46, 0.100), (x - 0.03, 0.0, Z + 0.450),
                   mat=M['gunmetal'], bevel=0.04, segs=3))
    # sensor / sight box
    out.append(box('TurSight', (0.20, 0.24, 0.16), (x + 0.30, 0.20, Z + 0.465),
                   mat=M['black'], bevel=0.02))
    out.append(cyl('TurSightLens', 0.055, 0.035, (x + 0.41, 0.20, Z + 0.465),
                   rot=(0, radians(90), 0), mat=M['lens'], segs=16))
    # elevating gun
    ang = radians(-11.0)
    px = x + 0.42
    pz = Z + 0.310
    out.append(box('TurMantlet', (0.26, 0.34, 0.26), (px, 0.0, pz),
                   mat=M['gunmetal'], bevel=0.05, segs=3))
    L = 1.95
    bx = px + 0.13 + L * 0.5 * cos(ang)
    bz = pz + L * 0.5 * sin(ang)
    out.append(cyl('Barrel', 0.074, L, (bx, 0.0, bz), rot=(0, radians(90) - ang, 0),
                   mat=M['gunmetal'], segs=20))
    out.append(cyl('BarrelSleeve', 0.098, 0.68,
                   (px + 0.13 + 0.34 * cos(ang), 0.0, pz + 0.34 * sin(ang)),
                   rot=(0, radians(90) - ang, 0), mat=M['gunmetal'], segs=18))
    mx = px + 0.13 + L * cos(ang)
    mz = pz + L * sin(ang)
    out.append(cyl('Muzzle', 0.100, 0.34, (mx - 0.14 * cos(ang), 0.0,
                                           mz - 0.14 * sin(ang)),
                   rot=(0, radians(90) - ang, 0), mat=M['gunmetal'], segs=20))
    for k in range(6):
        out.append(box('MuzzlePort%d' % k, (0.16, 0.026, 0.062),
                       (mx - 0.14 * cos(ang), 0.0, mz - 0.14 * sin(ang) + 0.062),
                       rot=(0, radians(90) - ang, radians(30) * k),
                       mat=M['black']))
    out.append(cyl('GasTube', 0.042, 0.90,
                   (px + 0.13 + 0.55 * cos(ang), 0.155, pz + 0.55 * sin(ang) + 0.10),
                   rot=(0, radians(90) - ang, 0), mat=M['gunmetal'], segs=12))
    # ammo box on the deck
    out.append(box('AmmoBox', (0.44, 0.34, 0.22), (x - 0.62, 0.0, Z + 0.230),
                   mat=M['gunmetal'], bevel=0.03))
    return out


def build(M):
    out = []
    out += platform(M)
    out += drone(M, 3.45)
    out += roof_gear(M)
    out += turret(M)
    return out

# -*- coding: utf-8 -*-
"""Master dimensions. +X forward, +Y vehicle-right, +Z up. Ground = z0."""

HW = 1.275          # body half width
HH = 1.050          # body half height (upper shell)
RC = 0.500          # top corner radius
RB = 0.050          # bottom corner radius
CZ = 2.570          # upper shell profile centre height
X_F = 6.000         # front face
X_R = -6.000        # rear face
Z_ROOF = CZ + HH    # 3.620
Z_BODY_BOT = CZ - HH  # 1.520
Z_SKIRT_TOP = 1.520
Z_SKIRT_BOT = 0.620
Y_SKIRT_OUT = 1.222
Y_SKIRT_IN = 1.160
Z_BELT = 1.985      # gold pinstripe
Z_ROOF_TRIM = 3.360  # gold line under the roof crown

Z_FLOOR = 1.055     # living-area floor
Z_CEIL = 3.045      # interior ceiling
Z_BEDDECK = 1.620   # raised rear bedroom floor (over the garage)
Z_GARAGE_TOP = 1.520

WHEEL_R = 0.552
WHEEL_W = 0.325
AX_F = 3.600
AX_R1 = -2.550
AX_R2 = -3.920
TRACK = 1.072      # wheel centre offset from CL

# side windows: (x0, x1, z0, z1)
WIN_Z0, WIN_Z1 = 2.060, 2.980
WINDOWS = [
    (1.050, 3.650, WIN_Z0, WIN_Z1),     # A - lounge
    (-1.850, 0.750, WIN_Z0, WIN_Z1),    # B - galley
    (-4.360, -2.240, WIN_Z0, WIN_Z1),   # C - bedroom
]
DRIVER_WIN = (4.360, 5.320, WIN_Z0, WIN_Z1)
DOOR = (4.300, 5.260, WIN_Z0, WIN_Z1)
REAR_WIN = (-0.560, 0.560, 2.230, 2.900)

ROOF_FRONT_PLATFORM = (2.30, 4.55)
DOCK_X = 3.40
TURRET_X = -4.25

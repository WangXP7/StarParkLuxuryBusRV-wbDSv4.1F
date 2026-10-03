# -*- coding: utf-8 -*-
"""StarPark Luxury Coach RV - fully procedural bpy build.

  blender -b --factory-startup --python build.py -- v1 [beauty|cut|under|all]
"""
import bpy, bmesh, sys, os, time
from math import radians

D = os.path.dirname(os.path.abspath(__file__))
if D not in sys.path:
    sys.path.insert(0, D)

import rv.lib_mat as LM
import rv.lib_util as LU
import rv.lib_studio as LS
import rv.spec as S
import rv.build_body as BB
import rv.build_under as BU
import rv.build_interior as BI
import rv.build_roofkit as BR
import rv.build_detail as BD

TAG = 'v1'
VIEW = 'all'
INTG = 0.0
CAM_EL = 9.0
CAM_AZ = -48.0
CAM_F = 45.0
for i, a in enumerate(sys.argv):
    if a == '--':
        rest = sys.argv[i + 1:]
        TAG = rest[0] if rest else TAG
        VIEW = rest[1] if len(rest) > 1 else VIEW
        INTG = float(rest[2]) if len(rest) > 2 else INTG
        CAM_EL = float(rest[3]) if len(rest) > 3 else CAM_EL
        CAM_AZ = float(rest[4]) if len(rest) > 4 else CAM_AZ
        CAM_F = float(rest[5]) if len(rest) > 5 else CAM_F

OUT = os.path.join(D, 'render')
os.makedirs(OUT, exist_ok=True)
RES = (2560, 1440)
SAMPLES = 224

# 3D feature points whose projection is written out so tools/match.py can
# sample this render at exactly the same feature as the reference plate.
ANCHORS = {
    'body_upper':  (4.00, -1.292, 2.62),
    'body_cream':  (0.30, -1.292, 1.76),
    'band':        (0.30, -1.292, 1.985),
    'skirt':       (0.30, -1.235, 1.10),
    'skirt_low':   (0.30, -1.235, 0.84),
    'win_int':     (-0.55, -1.300, 2.52),
    'tire':        (S.AX_F, -(S.TRACK + 0.176), 0.155),
    'rim':         (S.AX_F, -(S.TRACK + 0.178), 0.812),
}


def wipe():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.objects,
              bpy.data.lights, bpy.data.cameras, bpy.data.curves,
              bpy.data.worlds, bpy.data.images):
        for b in list(c):
            try:
                c.remove(b)
            except Exception:
                pass


def group(objs):
    bpy.ops.object.select_all(action='DESELECT')
    live = [o for o in objs if o is not None and o.name in bpy.data.objects]
    for o in live:
        o.select_set(True)
    if live:
        bpy.context.view_layer.objects.active = live[0]


def build_model():
    M = LM.build_all()
    body = BB.build(M)
    under = BU.build(M)
    inter = BI.build(M)
    lamps = BI.lights(M)
    roof = BR.build(M)
    det = BD.build(M)
    return M, {'body': body, 'under': under, 'inter': inter,
               'lamps': lamps, 'roof': roof, 'det': det}


def _slice(ob, ymax=None, zmax=None):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        if (ymax is not None and c.y < ymax) or (zmax is not None and c.z > zmax):
            kill.append(f)
    if kill:
        bmesh.ops.delete(bm, geom=kill, context='FACES')
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(ob.data)
    bm.free()


def cutaway(groups):
    """Quarter-dollhouse cut: drop the near wall + the roof so the whole
    interior fit-out and the underside structure are visible at once."""
    HIDE = ('glass_', 'gasket_', 'Wind', 'RearGlass', 'RearGasket', 'Mir',
            'Belt', 'RoofLine', 'Drone', 'Arm', 'Motor', 'Rotor', 'Leg',
            'Gimbal', 'Tur', 'Barrel', 'Muzzle', 'GasTube', 'Ammo', 'Lid',
            'Plat', 'LiftDeck', 'Charge', 'Pod', 'RoofHatch', 'HatchGlass',
            'Vent', 'Aerial', 'Post', 'Wiper', 'Logo', 'Step', 'Door',
            'FrontFill', 'Garage', 'LampBand', 'Drl', 'Fog', 'Proj', 'Tow',
            'Brow', 'Intake', 'RearLed', 'TailBlade', 'TailTrim', 'TailAmber')
    for o in groups['roof']:
        o.hide_render = True
    SHELL = ('BodyShell', 'FrontCap', 'RearCap', 'Skirt_-1', 'Skirt_1')
    for o in groups['body'] + groups['lamps']:
        if o.name in SHELL:
            _slice(o, ymax=-0.06, zmax=3.16)
            continue
        if o.name.startswith(HIDE):
            o.hide_render = True
    for o in groups['inter']:
        if o.name.startswith(('IntCeil', 'Cove')):
            o.hide_render = True
            continue
        if '-1' in o.name.split('_'):
            o.hide_render = True          # near-side cabinetry, keeps the view open


def studio(M, view):
    LS.build_world()
    LS.build_floor()
    LS.build_lights(scale=1.0)
    return None


def main():
    t0 = time.time()
    wipe()
    M, groups = build_model()
    allobj = []
    for k, v in groups.items():
        allobj += v
    tv = sum(len(o.data.vertices) for o in allobj if o.type == 'MESH')
    tp = sum(len(o.data.polygons) for o in allobj if o.type == 'MESH')
    print('BUILD objs=%d verts=%d polys=%d  %.1fs'
          % (len(allobj), tv, tp, time.time() - t0))

    LS.build_world()
    floor = LS.build_floor()
    LS.INT_GAIN = INTG
    LS.build_lights(scale=1.45, yaw=CAM_AZ)
    ints = LS.build_interior_lights()
    ints += LS.build_window_glow()
    cam = LS.make_camera(focal=CAM_F)

    if VIEW == 'cut':
        for l in ints:
            l.data.energy *= 0.22
        cutaway(groups)
        LS.setup_render(RES[0], RES[1], SAMPLES)
        LS.fit_camera(cam, [o for o in allobj if not o.hide_render],
                      (0.0, 0.0, 1.60), az=-66.0, el=33.0, dist=40.0,
                      target_w=0.86, target_h=0.84)
    elif VIEW == 'under':
        LS.setup_render(RES[0], RES[1], SAMPLES)
        LS.fit_camera(cam, allobj, (0.0, 0.0, 1.35), az=-56.0, el=8.0,
                      dist=34.0, target_w=0.88, target_h=0.80)
    elif VIEW == 'chassis':
        floor.hide_render = True
        LS.setup_render(RES[0], RES[1], SAMPLES)
        LS.fit_camera(cam, allobj, (-0.40, 0.0, 0.90), az=-72.0, el=-17.0,
                      dist=24.0, target_w=0.94, target_h=0.86)
    elif VIEW == 'detail':
        LS.setup_render(RES[0], RES[1], SAMPLES)
        LS.fit_camera(cam, allobj, (-0.60, 0.0, 2.55), az=-38.0, el=6.0,
                      dist=16.0, target_w=1.02, target_h=0.95)
    elif VIEW == 'front':
        LS.setup_render(RES[0], RES[1], SAMPLES)
        LS.fit_camera(cam, allobj, (2.00, 0.0, 2.10), az=-128.0, el=12.0,
                      dist=22.0, target_w=0.90, target_h=0.90)
    else:
        LS.setup_render(RES[0], RES[1], SAMPLES)
        d, t = LS.fit_camera(cam, allobj, (0.0, 0.0, 1.88), az=CAM_AZ, el=CAM_EL,
                             dist=40.0, target_w=1.075, target_h=1.000, verbose=True)
        print('CAM dist=%.2f target=%s' % (d, tuple(round(v, 2) for v in t)))
        try:
            pr = LS.project([ANCHORS[k] for k in ANCHORS], cam.location, t,
                            cam.data.lens, cam.data.sensor_width,
                            RES[0] / float(RES[1]))
            if pr:
                aj = dict((k, [round(pr[i][0], 4), round(1.0 - pr[i][1], 4)])
                          for i, k in enumerate(ANCHORS))
                jp = os.path.join(OUT, 'anchors_%s.json' % TAG)
                import json
                json.dump(aj, open(jp, 'w'), indent=1)
                print('ANCHORS', aj)
        except Exception as e:
            print('ANCH-ERR', e)

    blend = os.path.join(D, 'StarParkLuxuryBusRV_%s.blend' % TAG)
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    png = os.path.join(OUT, 'shot_%s_%s.png' % (TAG, VIEW))
    bpy.context.scene.render.filepath = png
    bpy.ops.render.render(write_still=True)
    try:
        print('PX', LS.readback(png))
    except Exception as e:
        print('PX-ERR', e)
    print('DONE %s %s -> %s  (%.1fs)' % (TAG, VIEW, png, time.time() - t0))


main()

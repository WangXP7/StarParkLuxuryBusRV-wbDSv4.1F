# -*- coding: utf-8 -*-
"""Export the coach as a web-ready GLB.

Procedural node materials do not survive glTF export, so every material is
replaced with a flat PBR counterpart whose colour comes from the *same*
measured palette used by the offline render (rv/lib_mat.TARGET). Objects are
bucketed into logical groups, joined per (group, material) to cut the draw
call count, and prefixed GROUP__ so the web app can toggle them:

    SHELL__     outer skin + glazing  -> x-ray / cutaway toggle
    XD__        cabin dressing behind the windows -> hidden when you go inside
    ROOF__      roof kit
    CHAS__      chassis, driveline, engine, wheels
    INT__       interior fit-out
    BODY__      everything else on the outside

  blender -b --factory-startup --python export_web.py
"""
import bpy, sys, os, json
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
if D not in sys.path:
    sys.path.insert(0, D)

import rv.lib_mat as LM
import rv.lib_util as LU
import rv.spec as S
import rv.build_body as BB
import rv.build_under as BU
import rv.build_interior as BI
import rv.build_roofkit as BR
import rv.build_detail as BD

OUTDIR = os.path.join(D, 'web')
os.makedirs(OUTDIR, exist_ok=True)
GLB = os.path.join(OUTDIR, 'model.glb')


def s2l(c):
    out = []
    for v in c[:3]:
        v = v / 255.0
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return out


T = LM.TARGET
# material key -> (base sRGB, roughness, metallic, alpha, emission sRGB?, emission power)
WEB = {
    'body':       (T['body'], 0.34, 0.05, 1.0, None, 0),
    'band':       (T['band'], 0.42, 0.10, 1.0, None, 0),
    'skirt':      (T['skirt'], 0.46, 0.16, 1.0, None, 0),
    'tire':       (T['tire'], 0.82, 0.00, 1.0, None, 0),
    'wheel':      (T['rim'], 0.30, 1.00, 1.0, None, 0),
    'glass':      (T['glass'], 0.06, 0.00, 0.42, None, 0),
    'glass_front': ((18, 16, 15), 0.06, 0.00, 0.62, None, 0),
    'chrome':     (T['chrome'], 0.14, 1.00, 1.0, None, 0),
    'alu':        ((150, 148, 145), 0.32, 1.00, 1.0, None, 0),
    'roofkit':    (T['roofkit'], 0.46, 0.30, 1.0, None, 0),
    'gunmetal':   (T['roofkit_lo'], 0.42, 0.60, 1.0, None, 0),
    'black':      (T['black'], 0.44, 0.10, 1.0, None, 0),
    'cast':       ((46, 45, 44), 0.62, 0.45, 1.0, None, 0),
    'wood':       (T['wood'], 0.40, 0.00, 1.0, None, 0),
    'wood_light': (T['wood_lt'], 0.40, 0.00, 1.0, None, 0),
    'oak':        ((168, 126, 82), 0.46, 0.00, 1.0, None, 0),
    'leather':    (T['cream'], 0.48, 0.00, 1.0, None, 0),
    'marble':     (T['marble'], 0.16, 0.00, 1.0, None, 0),
    'stone':      ((198, 192, 182), 0.24, 0.00, 1.0, None, 0),
    'carpet':     (T['carpet'], 0.88, 0.00, 1.0, None, 0),
    'ceiling':    ((230, 219, 202), 0.62, 0.00, 1.0, None, 0),
    'wall':       (T['wall'], 0.60, 0.00, 1.0, None, 0),
    'trim':       ((96, 62, 36), 0.42, 0.00, 1.0, None, 0),
    'car':        (T['car'], 0.18, 0.25, 1.0, None, 0),
    'lens':       ((196, 208, 220), 0.06, 0.00, 0.45, None, 0),
    'lens_red':   ((150, 26, 22), 0.06, 0.00, 0.60, None, 0),
    'shower':     ((214, 226, 232), 0.05, 0.00, 0.16, None, 0),
    'lum_warm':   ((255, 214, 156), 0.50, 0.00, 1.0, (255, 206, 140), 2.4),
    'lum_copper': ((255, 176, 108), 0.50, 0.00, 1.0, (255, 168, 96), 2.6),
    'lum_white':  ((255, 248, 236), 0.50, 0.00, 1.0, (255, 246, 232), 1.8),
    'led_red':    ((255, 60, 44), 0.40, 0.00, 1.0, (255, 46, 32), 2.2),
    'led_amber':  ((255, 170, 70), 0.40, 0.00, 1.0, (255, 158, 52), 1.6),
    'led_drl':    ((255, 252, 244), 0.40, 0.00, 1.0, (255, 250, 238), 2.6),
    'amber':      ((255, 170, 96), 0.60, 0.00, 1.0, (255, 152, 74), 1.5),
}

# which source key each lib_mat function produced -> web entry
KEYMAP = {
    'M_body_pearl': 'body', 'M_band_champagne': 'band', 'M_skirt_graphite': 'skirt',
    'M_tire': 'tire', 'M_wheel_bronze': 'wheel', 'M_glass_window': 'glass',
    'M_glass_front': 'glass_front', 'M_chrome': 'chrome', 'M_alu_brushed': 'alu',
    'M_roofkit': 'roofkit', 'M_gunmetal': 'gunmetal', 'M_black_plastic': 'black',
    'M_engine_cast': 'cast', 'M_walnut': 'wood', 'M_walnut_honey': 'wood_light',
    'M_oak_flat': 'oak', 'M_leather_cream': 'leather', 'M_marble_white': 'marble',
    'M_stone_flat': 'stone', 'M_carpet': 'carpet', 'M_ceiling': 'ceiling',
    'M_interior_wall': 'wall', 'M_trim_satin_wood': 'trim', 'M_car_red': 'car',
    'M_lens_head': 'lens', 'M_lens_red': 'lens_red', 'M_glass_shower': 'shower',
    'M_lum_warm': 'lum_warm', 'M_lum_copper': 'lum_copper', 'M_lum_white': 'lum_white',
    'M_led_red': 'led_red', 'M_led_amber': 'led_amber', 'M_led_drl': 'led_drl',
    'M_lum_amber': 'amber', 'M_gold_champagne': 'band',
}

SHELL_NAMES = ('BodyShell', 'FrontCap', 'RearCap', 'Skirt_-1', 'Skirt_1')
XD_PREFIX = ('AmberBack', 'WAlc', 'WMul', 'WSofa', 'WCsn', 'WPlt', 'WPltL', 'WCtr',
             'WSpl', 'WUp', 'WDoor', 'WTap', 'WBed', 'WRun', 'WPil', 'WHB',
             'ValTop', 'ValBot', 'Sill_')
ROOF_PREFIX = ('Plat', 'Lid', 'LiftDeck', 'Post', 'Charge', 'Drone', 'Arm', 'Motor',
               'Rotor', 'Leg', 'Gimbal', 'Pod', 'RoofHatch', 'HatchGlass', 'Vent',
               'Aerial', 'Tur', 'Barrel', 'Muzzle', 'GasTube', 'Ammo')
CHAS_PREFIX = ('Rail', 'Xmem', 'Shaft', 'Fuel', 'Def', 'Batt', 'Air', 'Exh',
               'Muffler', 'Tail', 'Eng', 'Injector', 'InPort', 'Turbo', 'Intake',
               'Crank', 'Pulley', 'Fan', 'Radiator', 'Intercooler', 'Axle', 'Diff',
               'Bag', 'Shock', 'Leaf', 'W0', 'W1', 'W2', 'Well', 'SubFloor',
               'Louvre', 'ArchLip')


def classify(name):
    if name in SHELL_NAMES or name.startswith(('glass_', 'gasket_', 'Wind',
                                               'RearGlass', 'RearGasket')):
        return 'SHELL'
    if name.startswith(XD_PREFIX):
        return 'XD'
    if name.startswith(ROOF_PREFIX):
        return 'ROOF'
    if name.startswith(CHAS_PREFIX):
        return 'CHAS'
    if name.startswith(('Cockpit', 'Dash', 'Cluster', 'Nav', 'Col', 'Wheel',
                        'Chair', 'Sofa', 'Cush', 'LChair', 'Table', 'Vase',
                        'Leaf', 'Rug', 'Galley', 'Sink', 'Tap', 'Hob', 'Burn',
                        'UpCab', 'Fridge', 'Bar', 'Bath', 'Shower', 'Vanity',
                        'Basin', 'Mirror', 'Toilet', 'Bed', 'Deck', 'Step',
                        'Mattress', 'Pillow', 'HeadBoard', 'Ward', 'Int',
                        'OverCab', 'WallLow', 'WallHead', 'Pillar', 'Amb',
                        'Lounge', 'RailPost', 'DeckFace')):
        return 'INT'
    return 'BODY'


# ---------------------------------------------------------------- build
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.objects,
              bpy.data.lights, bpy.data.cameras, bpy.data.curves,
              bpy.data.worlds, bpy.data.images):
        for b in list(c):
            try:
                c.remove(b)
            except Exception:
                pass
    M = LM.build_all()
    objs = []
    objs += BB.build(M)
    objs += BU.build(M)
    objs += BI.build(M)
    objs += BI.lights(M)
    objs += BR.build(M)
    objs += BD.build(M)
    return [o for o in objs if o and o.type == 'MESH']


def make_web_material(libname):
    key = KEYMAP.get(libname)
    if key is None:
        return None
    w = WEB[key]
    name = 'WEB_' + libname
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    lin = s2l(w[0])
    b.inputs['Base Color'].default_value = (lin[0], lin[1], lin[2], 1.0)
    b.inputs['Roughness'].default_value = w[1]
    b.inputs['Metallic'].default_value = w[2]
    if w[3] < 1.0 and 'Alpha' in b.inputs:
        b.inputs['Alpha'].default_value = w[3]
        if hasattr(m, 'surface_render_method'):
            m.surface_render_method = 'DITHERED'
    if w[4]:
        e = s2l(w[4])
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (e[0], e[1], e[2], 1.0)
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = w[5]
    return m


def remap_materials(objs):
    """Swap every slot for its flat web counterpart and tag the group."""
    cache = {}
    for o in objs:
        grp = classify(o.name)
        o['webgroup'] = grp
        newslots = []
        for slot in o.material_slots:
            src = slot.material.name if slot.material else None
            if src not in cache:
                cache[src] = make_web_material(src) if src else None
            newslots.append(cache[src])
        if not newslots:
            continue
        # collapse to a single slot (bucketing by material happens next)
        keep = newslots[0]
        o.data.materials.clear()
        if keep:
            o.data.materials.append(keep)
    return cache


def bucket_and_join(objs):
    buckets = defaultdict(list)
    for o in objs:
        if not o.data.materials:
            continue
        grp = o.get('webgroup', 'BODY')
        if grp == 'SHELL':
            key = ('SHELL', o.name)          # keep shell parts individually named
        else:
            key = (grp, o.data.materials[0].name)
        buckets[key].append(o)

    out = []
    for (grp, tag), group in buckets.items():
        bpy.ops.object.select_all(action='DESELECT')
        live = [o for o in group if o.name in bpy.data.objects]
        if not live:
            continue
        for o in live:
            o.select_set(True)
        bpy.context.view_layer.objects.active = live[0]
        if len(live) > 1:
            try:
                bpy.ops.object.join()
            except Exception as e:
                print('  join failed for', tag, e)
        j = bpy.context.view_layer.objects.active
        short = tag.replace('WEB_', '').replace('M_', '')
        j.name = '%s__%s' % (grp, short)
        out.append(j)
    return out


def main():
    objs = build()
    print('built %d meshes' % len(objs))
    remap_materials(objs)
    joined = bucket_and_join(objs)
    tv = sum(len(o.data.vertices) for o in joined)
    tp = sum(len(o.data.polygons) for o in joined)
    print('joined -> %d meshes, %d verts, %d polys' % (len(joined), tv, tp))

    bpy.ops.object.select_all(action='DESELECT')
    kw = dict(filepath=GLB, export_format='GLB', export_apply=True)
    try:
        bpy.ops.export_scene.gltf(export_extras=True, **kw)
    except TypeError:
        bpy.ops.export_scene.gltf(**kw)
    print('GLB %.1f MB -> %s' % (os.path.getsize(GLB) / 1048576.0, GLB))

    manifest = {'meshes': [{'name': o.name, 'group': o.name.split('__')[0],
                            'verts': len(o.data.vertices),
                            'tris': sum(len(p.vertices) - 2 for p in o.data.polygons)}
                           for o in joined]}
    with open(os.path.join(OUTDIR, 'manifest.json'), 'w') as f:
        json.dump(manifest, f, indent=1)
    print('manifest written')


main()

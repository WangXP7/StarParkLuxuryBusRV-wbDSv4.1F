# -*- coding: utf-8 -*-
"""Fully procedural materials, colour-matched to the reference plate.

Colour model
------------
The scene is lit by a near-uniform warm cream world of radiance ENV. In that
situation a diffuse surface of albedo rho renders at exactly rho * ENV, so

        albedo_linear = target_linear / ENV

`alb()` below does that conversion from an sRGB target, which means every
number in TARGET comes straight off the reference image and the render should
land on it. If a value drifts, correct ENV or the material's specular level,
not the target.
"""
import bpy
from math import radians

# effective warm ambient radiance of the studio world
ENV = (0.930, 0.883, 0.820)

# ---- sampled straight from D_01 (sRGB) ------------------------------------
TARGET = {
    'body':       (235, 218, 202),   # #EBDACA pearl ivory
    'body_sh':    (214, 196, 180),   # shaded side
    'skirt_hi':   (104, 92, 81),     # upper edge of the graphite band
    'skirt':      (86, 74, 66),      # #564A42
    'skirt_lo':   (72, 62, 55),
    'band':       (199, 155, 114),   # #C79B72 champagne waistline
    'band2':      (176, 138, 102),
    'tire':       (33, 28, 25),      # #211C19
    'rim':        (142, 114, 93),    # #8E725D muted bronze
    'rim_hi':     (176, 148, 124),
    'glass':      (40, 30, 24),      # dark warm tint
    'amber':      (237, 180, 98),    # #EDB462 interior glow
    'roofkit':    (69, 64, 58),      # dark warm charcoal
    'roofkit_lo': (48, 44, 40),
    'black':      (26, 24, 23),
    'chrome':     (188, 182, 174),
    'wood':       (112, 74, 44),     # walnut
    'wood_lt':    (158, 116, 74),
    'cream':      (226, 214, 196),   # leather
    'marble':     (216, 210, 200),
    'wall':       (198, 186, 168),
    'carpet':     (150, 133, 112),
    'red':        (232, 62, 48),
    'amber_led':  (255, 176, 72),
    'white_led':  (238, 240, 242),
    'car':        (128, 22, 20),
}


def s2l(c):
    out = []
    for v in c[:3]:
        v = v / 255.0
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def alb(name, k=1.0):
    t = s2l(TARGET[name])
    return (min(t[0] * k / ENV[0], 1.0), min(t[1] * k / ENV[1], 1.0),
            min(t[2] * k / ENV[2], 1.0), 1.0)


def si(node, key, val):
    if key in node.inputs:
        try:
            node.inputs[key].default_value = val
        except Exception:
            pass


def _base(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (620, 0)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.location = (300, 0)
    nt.links.new(b.outputs[0], out.inputs['Surface'])
    return m, nt, b


def _blend(m, dithered=True):
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'DITHERED'
    if hasattr(m, 'use_transparent_shadow'):
        m.use_transparent_shadow = True
    m.use_backface_culling = False


def _tc(nt, x=-1100, y=0):
    t = nt.nodes.new('ShaderNodeTexCoord')
    t.location = (x, y)
    return t


def _map(nt, scale=(1, 1, 1), loc=(0, 0, 0), rot=(0, 0, 0), src=None, x=-900, y=0):
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.location = (x, y)
    mp.inputs['Scale'].default_value = scale
    mp.inputs['Location'].default_value = loc
    mp.inputs['Rotation'].default_value = rot
    if src is not None:
        nt.links.new(src.outputs['Object'], mp.inputs['Vector'])
    return mp


# ------------------------------------------------------------------ surfaces
def body_white():
    """Satin pearl ivory. Low gloss on purpose: the reference body is almost
    flat cream with only a gentle top-down falloff, a mirror finish reads as
    plastic and kills the match."""
    m, nt, b = _base('M_body_pearl')
    si(b, 'Base Color', alb('body', 1.045))
    si(b, 'Metallic', 0.06)
    si(b, 'Roughness', 0.30)
    si(b, 'IOR', 1.46)
    si(b, 'Coat Weight', 0.16)
    si(b, 'Coat Roughness', 0.12)
    si(b, 'Specular IOR Level', 0.42)
    tc = _tc(nt)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-1080, 220)
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.location = (-900, 220)
    mr.inputs['From Min'].default_value = 0.90
    mr.inputs['From Max'].default_value = 3.40
    mr.inputs['To Min'].default_value = 0.930
    mr.inputs['To Max'].default_value = 1.030
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    lum = nt.nodes.new('ShaderNodeMixRGB')
    lum.location = (-720, 220)
    lum.inputs['Fac'].default_value = 1.0
    lum.inputs['Color1'].default_value = (0.0, 0.0, 0.0, 1.0)
    lum.inputs['Color2'].default_value = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(mr.outputs['Result'], lum.inputs['Fac'])
    mixt = nt.nodes.new('ShaderNodeMixRGB')
    mixt.location = (-480, 120)
    mixt.blend_type = 'MULTIPLY'
    mixt.inputs['Fac'].default_value = 1.0
    mixt.inputs['Color1'].default_value = alb('body', 1.062)
    nt.links.new(lum.outputs['Color'], mixt.inputs['Color2'])
    nt.links.new(mixt.outputs['Color'], b.inputs['Base Color'])
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.location = (-720, -340)
    n.inputs['Scale'].default_value = 2.4
    n.inputs['Detail'].default_value = 6.0
    nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.location = (-480, -340)
    rmp.color_ramp.elements[0].position = 0.40
    rmp.color_ramp.elements[0].color = (0.285, 0.285, 0.285, 1)
    rmp.color_ramp.elements[1].position = 0.62
    rmp.color_ramp.elements[1].color = (0.330, 0.330, 0.330, 1)
    nt.links.new(n.outputs['Fac'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], b.inputs['Roughness'])
    return m


def skirt_dark():
    """Graphite lower band. In the reference it is NOT black - it is a warm
    grey-brown with a clear top-to-bottom gradient, lighter at the top edge."""
    m, nt, b = _base('M_skirt_graphite')
    si(b, 'Metallic', 0.18)
    si(b, 'Roughness', 0.44)
    si(b, 'Coat Weight', 0.10)
    si(b, 'Coat Roughness', 0.25)
    tc = _tc(nt)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-900, 0)
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.location = (-700, 0)
    mr.inputs['From Min'].default_value = 0.60
    mr.inputs['From Max'].default_value = 1.52
    mr.inputs['To Min'].default_value = 0.0
    mr.inputs['To Max'].default_value = 1.0
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.location = (-460, 0)
    rmp.color_ramp.elements[0].position = 0.00
    rmp.color_ramp.elements[0].color = alb('skirt_lo', 0.88)
    rmp.color_ramp.elements[1].position = 0.52
    rmp.color_ramp.elements[1].color = alb('skirt', 0.50)
    e3 = rmp.color_ramp.elements.new(1.00)
    e3.color = alb('skirt_hi', 0.44)
    nt.links.new(mr.outputs['Result'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], b.inputs['Base Color'])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.location = (-720, -380)
    nz.inputs['Scale'].default_value = 36.0
    nz.inputs['Detail'].default_value = 8.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-460, -400)
    bump.inputs['Strength'].default_value = 0.08
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def band_champagne():
    """Waistline band. The reference band is soft matte camel paint, not a
    polished gold - keep it non-metallic."""
    m, nt, b = _base('M_band_champagne')
    si(b, 'Base Color', alb('band', 1.24))
    si(b, 'Metallic', 0.0)
    si(b, 'Roughness', 0.42)
    si(b, 'Specular IOR Level', 0.35)
    return m


def gold():
    m, nt, b = _base('M_gold_champagne')
    si(b, 'Base Color', alb('band2'))
    si(b, 'Metallic', 0.85)
    si(b, 'Roughness', 0.26)
    return m


def chrome():
    m, nt, b = _base('M_chrome')
    si(b, 'Base Color', alb('chrome'))
    si(b, 'Metallic', 1.0)
    si(b, 'Roughness', 0.11)
    return m


def alu():
    m, nt, b = _base('M_alu_brushed')
    si(b, 'Base Color', (0.575, 0.560, 0.545, 1.0))
    si(b, 'Metallic', 1.0)
    si(b, 'Roughness', 0.30)
    tc = _tc(nt)
    mp = _map(nt, scale=(1.0, 12.0, 6.0), src=tc, x=-900, y=-300)
    w = nt.nodes.new('ShaderNodeTexNoise')
    w.location = (-660, -300)
    w.inputs['Scale'].default_value = 220.0
    w.inputs['Detail'].default_value = 5.0
    nt.links.new(mp.outputs['Vector'], w.inputs['Vector'])
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.location = (-420, -300)
    rmp.color_ramp.elements[0].position = 0.32
    rmp.color_ramp.elements[0].color = (0.22, 0.22, 0.22, 1)
    rmp.color_ramp.elements[1].position = 0.66
    rmp.color_ramp.elements[1].color = (0.38, 0.38, 0.38, 1)
    nt.links.new(w.outputs['Fac'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], b.inputs['Roughness'])
    return m


def glass_tint():
    """Window glass. Two jobs: stay see-through so the lit cabin reads, and
    darken toward the top of each pane the way the reference plate does (its
    reflection of the tree line). Generated.Z drives the alpha ramp."""
    m, nt, b = _base('M_glass_window')
    si(b, 'Base Color', alb('glass', 1.6))
    si(b, 'Metallic', 0.0)
    si(b, 'Roughness', 0.035)
    si(b, 'IOR', 1.50)
    si(b, 'Coat Weight', 0.55)
    si(b, 'Coat Roughness', 0.02)
    si(b, 'Specular IOR Level', 0.58)
    tc = _tc(nt)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-880, -260)
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.location = (-680, -260)
    mr.inputs['From Min'].default_value = 0.42
    mr.inputs['From Max'].default_value = 0.72
    mr.inputs['To Min'].default_value = 0.215
    mr.inputs['To Max'].default_value = 0.880
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], b.inputs['Alpha'])
    _blend(m)
    return m


def glass_front():
    m, nt, b = _base('M_glass_front')
    si(b, 'Base Color', (0.020, 0.018, 0.017, 1.0))
    si(b, 'Roughness', 0.05)
    si(b, 'IOR', 1.50)
    si(b, 'Alpha', 0.66)
    si(b, 'Coat Weight', 0.55)
    si(b, 'Coat Roughness', 0.02)
    _blend(m)
    return m


def lens(name='M_lens', color=(0.9, 0.94, 1.0, 1.0), alpha=0.45):
    m, nt, b = _base(name)
    si(b, 'Base Color', color)
    si(b, 'Roughness', 0.045)
    si(b, 'IOR', 1.52)
    si(b, 'Alpha', alpha)
    si(b, 'Coat Weight', 0.8)
    si(b, 'Coat Roughness', 0.02)
    _blend(m)
    return m


def emitter(name, color, strength, rough=0.42):
    m, nt, b = _base(name)
    si(b, 'Base Color', (color[0], color[1], color[2], 1.0))
    si(b, 'Roughness', rough)
    si(b, 'Emission Color', (color[0], color[1], color[2], 1.0))
    si(b, 'Emission Strength', strength)
    return m


def walnut(light=False):
    nm = 'M_walnut_honey' if light else 'M_walnut'
    m, nt, b = _base(nm)
    c0 = alb('wood_lt')
    c1 = alb('wood', 0.55)
    if light:
        c0 = alb('wood_lt', 1.25)
        c1 = alb('wood', 0.95)
    si(b, 'Roughness', 0.34)
    si(b, 'Coat Weight', 0.40)
    si(b, 'Coat Roughness', 0.16)
    tc = _tc(nt)
    mp = _map(nt, scale=(1.0, 1.0, 22.0), src=tc, x=-900, y=0)
    w = nt.nodes.new('ShaderNodeTexWave')
    w.location = (-660, 0)
    w.wave_type = 'BANDS'
    w.bands_direction = 'X'
    w.inputs['Scale'].default_value = 1.6
    w.inputs['Distortion'].default_value = 11.0
    w.inputs['Detail'].default_value = 4.0
    w.inputs['Detail Scale'].default_value = 2.6
    nt.links.new(mp.outputs['Vector'], w.inputs['Vector'])
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.location = (-400, 0)
    rmp.color_ramp.elements[0].position = 0.10
    rmp.color_ramp.elements[0].color = c1
    rmp.color_ramp.elements[1].position = 0.78
    rmp.color_ramp.elements[1].color = c0
    e = rmp.color_ramp.elements.new(0.46)
    e.color = [(c1[i] + c0[i]) * 0.5 for i in range(3)] + [1.0]
    nt.links.new(w.outputs['Fac'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (60, -320)
    bump.inputs['Strength'].default_value = 0.09
    nt.links.new(w.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def leather_cream():
    m, nt, b = _base('M_leather_cream')
    si(b, 'Base Color', alb('cream'))
    si(b, 'Roughness', 0.44)
    si(b, 'Coat Weight', 0.14)
    si(b, 'Coat Roughness', 0.30)
    si(b, 'Sheen Weight', 0.22)
    tc = _tc(nt)
    v = nt.nodes.new('ShaderNodeTexVoronoi')
    v.location = (-660, -300)
    v.inputs['Scale'].default_value = 620.0
    nt.links.new(tc.outputs['Object'], v.inputs['Vector'])
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.location = (-660, 60)
    n.inputs['Scale'].default_value = 12.0
    n.inputs['Detail'].default_value = 6.0
    nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMixRGB')
    mix.location = (-420, -220)
    mix.inputs['Fac'].default_value = 0.35
    nt.links.new(v.outputs['Distance'], mix.inputs['Color1'])
    nt.links.new(n.outputs['Fac'], mix.inputs['Color2'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-180, -320)
    bump.inputs['Strength'].default_value = 0.20
    nt.links.new(mix.outputs['Color'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def marble():
    m, nt, b = _base('M_marble_white')
    si(b, 'Base Color', alb('marble'))
    si(b, 'Roughness', 0.13)
    si(b, 'Coat Weight', 0.55)
    si(b, 'Coat Roughness', 0.05)
    tc = _tc(nt)
    mp = _map(nt, scale=(1.0, 1.0, 3.0), src=tc, x=-900, y=0)
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.location = (-660, 0)
    n.inputs['Scale'].default_value = 5.5
    n.inputs['Detail'].default_value = 9.0
    n.inputs['Roughness'].default_value = 0.62
    nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
    w = nt.nodes.new('ShaderNodeTexWave')
    w.location = (-660, -280)
    w.wave_type = 'BANDS'
    w.inputs['Scale'].default_value = 3.2
    w.inputs['Distortion'].default_value = 16.0
    w.inputs['Detail'].default_value = 3.0
    nt.links.new(n.outputs['Fac'], w.inputs['Vector'])
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.location = (-400, -240)
    rmp.color_ramp.elements[0].position = 0.30
    rmp.color_ramp.elements[0].color = alb('marble', 1.08)
    rmp.color_ramp.elements[1].position = 0.60
    rmp.color_ramp.elements[1].color = (0.330, 0.315, 0.300, 1.0)
    nt.links.new(w.outputs['Fac'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], b.inputs['Base Color'])
    return m


def carpet(c0=None):
    m, nt, b = _base('M_carpet')
    si(b, 'Base Color', alb('carpet'))
    si(b, 'Roughness', 0.88)
    si(b, 'Sheen Weight', 0.35)
    tc = _tc(nt)
    v = nt.nodes.new('ShaderNodeTexVoronoi')
    v.location = (-660, -280)
    v.inputs['Scale'].default_value = 1400.0
    nt.links.new(tc.outputs['Object'], v.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-400, -320)
    bump.inputs['Strength'].default_value = 0.30
    nt.links.new(v.outputs['Distance'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def ceiling_mat():
    m, nt, b = _base('M_ceiling')
    si(b, 'Base Color', alb('cream', 1.06))
    si(b, 'Roughness', 0.60)
    return m


def tire():
    m, nt, b = _base('M_tire')
    si(b, 'Base Color', alb('tire'))
    si(b, 'Roughness', 0.80)
    si(b, 'Specular IOR Level', 0.26)
    tc = _tc(nt)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-880, -260)
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    at = nt.nodes.new('ShaderNodeMath')
    at.operation = 'ARCTAN2'
    at.location = (-700, -180)
    nt.links.new(sep.outputs['Z'], at.inputs[0])
    nt.links.new(sep.outputs['X'], at.inputs[1])
    am = nt.nodes.new('ShaderNodeMath')
    am.operation = 'MULTIPLY'
    am.location = (-540, -180)
    am.inputs[1].default_value = 26.0
    nt.links.new(at.outputs[0], am.inputs[0])
    sn = nt.nodes.new('ShaderNodeMath')
    sn.operation = 'SINE'
    sn.location = (-380, -180)
    nt.links.new(am.outputs[0], sn.inputs[0])
    bm = nt.nodes.new('ShaderNodeMath')
    bm.operation = 'MULTIPLY'
    bm.location = (-540, -360)
    bm.inputs[1].default_value = 46.0
    nt.links.new(sep.outputs['Y'], bm.inputs[0])
    sn2 = nt.nodes.new('ShaderNodeMath')
    sn2.operation = 'SINE'
    sn2.location = (-380, -360)
    nt.links.new(bm.outputs[0], sn2.inputs[0])
    mix = nt.nodes.new('ShaderNodeMath')
    mix.operation = 'MULTIPLY'
    mix.location = (-220, -260)
    nt.links.new(sn.outputs[0], mix.inputs[0])
    nt.links.new(sn2.outputs[0], mix.inputs[1])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.location = (-560, -560)
    nz.inputs['Scale'].default_value = 700.0
    nz.inputs['Detail'].default_value = 6.0
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    add = nt.nodes.new('ShaderNodeMath')
    add.operation = 'ADD'
    add.location = (-60, -320)
    nt.links.new(mix.outputs[0], add.inputs[0])
    nt.links.new(nz.outputs['Fac'], add.inputs[1])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (120, -340)
    bump.inputs['Strength'].default_value = 0.26
    nt.links.new(add.outputs[0], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def wheel_bronze():
    m, nt, b = _base('M_wheel_bronze')
    si(b, 'Base Color', alb('rim', 1.22))
    si(b, 'Metallic', 1.0)
    si(b, 'Roughness', 0.36)
    tc = _tc(nt)
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.location = (-660, -300)
    n.inputs['Scale'].default_value = 240.0
    n.inputs['Detail'].default_value = 6.0
    nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.location = (-420, -300)
    rmp.color_ramp.elements[0].position = 0.36
    rmp.color_ramp.elements[0].color = (0.21, 0.21, 0.21, 1)
    rmp.color_ramp.elements[1].position = 0.63
    rmp.color_ramp.elements[1].color = (0.34, 0.34, 0.34, 1)
    nt.links.new(n.outputs['Fac'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], b.inputs['Roughness'])
    return m


def black_plastic(rough=0.42, col=None, key='black'):
    m, nt, b = _base('M_black_plastic')
    si(b, 'Base Color', alb(key))
    si(b, 'Roughness', rough)
    si(b, 'Specular IOR Level', 0.42)
    return m


def roof_kit():
    m, nt, b = _base('M_roofkit')
    si(b, 'Base Color', alb('roofkit'))
    si(b, 'Metallic', 0.45)
    si(b, 'Roughness', 0.46)
    tc = _tc(nt)
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.location = (-660, -300)
    n.inputs['Scale'].default_value = 70.0
    nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-400, -320)
    bump.inputs['Strength'].default_value = 0.07
    nt.links.new(n.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def gunmetal():
    m, nt, b = _base('M_gunmetal')
    si(b, 'Base Color', alb('roofkit_lo'))
    si(b, 'Metallic', 0.70)
    si(b, 'Roughness', 0.40)
    return m


def cast_metal():
    m, nt, b = _base('M_engine_cast')
    si(b, 'Base Color', (0.125, 0.122, 0.118, 1.0))
    si(b, 'Metallic', 0.55)
    si(b, 'Roughness', 0.60)
    tc = _tc(nt)
    v = nt.nodes.new('ShaderNodeTexVoronoi')
    v.location = (-660, -300)
    v.inputs['Scale'].default_value = 110.0
    nt.links.new(tc.outputs['Object'], v.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-400, -320)
    bump.inputs['Strength'].default_value = 0.18
    nt.links.new(v.outputs['Distance'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def car_paint():
    m, nt, b = _base('M_car_red')
    si(b, 'Base Color', alb('car'))
    si(b, 'Metallic', 0.25)
    si(b, 'Roughness', 0.16)
    si(b, 'Coat Weight', 0.9)
    si(b, 'Coat Roughness', 0.03)
    return m


def interior_wall():
    m, nt, b = _base('M_interior_wall')
    si(b, 'Base Color', alb('wall'))
    si(b, 'Roughness', 0.60)
    tc = _tc(nt)
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.location = (-660, -300)
    n.inputs['Scale'].default_value = 26.0
    nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.location = (-400, -320)
    bump.inputs['Strength'].default_value = 0.05
    nt.links.new(n.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m


def trim_satin():
    m, nt, b = _base('M_trim_satin_wood')
    si(b, 'Base Color', alb('wood', 0.75))
    si(b, 'Roughness', 0.40)
    si(b, 'Coat Weight', 0.35)
    return m


def glass_shower():
    m, nt, b = _base('M_glass_shower')
    si(b, 'Base Color', (0.80, 0.84, 0.86, 1.0))
    si(b, 'Roughness', 0.03)
    si(b, 'Alpha', 0.14)
    si(b, 'Coat Weight', 0.9)
    si(b, 'Coat Roughness', 0.02)
    _blend(m)
    return m


def amber_panel():
    """Cabin backdrop seen through the glazing. A pure emission with a
    top-to-bottom ramp: bright warm band low down (the reference plate's
    under-cabinet glow) falling off into the dark upper cabinet zone."""
    m, nt, b = _base('M_lum_amber')
    nt.nodes.remove(b)
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    em = nt.nodes.new('ShaderNodeEmission')
    em.location = (300, 0)
    em.inputs['Strength'].default_value = 1.0
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    tc = _tc(nt)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-880, 0)
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    rmp = nt.nodes.new('ShaderNodeValToRGB')
    rmp.location = (-620, 0)
    rmp.color_ramp.elements[0].position = 0.00
    rmp.color_ramp.elements[0].color = (0.160, 0.062, 0.018, 1.0)
    rmp.color_ramp.elements[1].position = 0.46
    rmp.color_ramp.elements[1].color = (0.330, 0.124, 0.031, 1.0)
    e3 = rmp.color_ramp.elements.new(0.72)
    e3.color = (0.205, 0.082, 0.024, 1.0)
    e4 = rmp.color_ramp.elements.new(1.00)
    e4.color = (0.098, 0.034, 0.010, 1.0)
    nt.links.new(sep.outputs['Z'], rmp.inputs['Fac'])
    nt.links.new(rmp.outputs['Color'], em.inputs['Color'])
    return m


def oak_flat():
    """Untextured warm oak. At the scale a cabin interior is seen through a
    window, grained wood reads as noise - a flat tone reads as joinery."""
    m, nt, b = _base('M_oak_flat')
    si(b, 'Base Color', alb('wood_lt', 1.05))
    si(b, 'Roughness', 0.46)
    si(b, 'Coat Weight', 0.30)
    si(b, 'Coat Roughness', 0.18)
    return m


def stone_flat():
    m, nt, b = _base('M_stone_flat')
    si(b, 'Base Color', alb('marble', 0.86))
    si(b, 'Roughness', 0.22)
    return m


def build_all():
    lib = {}
    lib['body'] = body_white()
    lib['skirt'] = skirt_dark()
    lib['band'] = band_champagne()
    lib['gold'] = gold()
    lib['chrome'] = chrome()
    lib['alu'] = alu()
    lib['glass'] = glass_tint()
    lib['glass_front'] = glass_front()
    lib['lens'] = lens('M_lens_head', (0.86, 0.90, 0.96, 1.0), 0.40)
    lib['lens_red'] = lens('M_lens_red', (0.80, 0.14, 0.12, 1.0), 0.55)
    lib['lum_warm'] = emitter('M_lum_warm', (1.0, 0.795, 0.545), 9.0, 0.5)
    lib['lum_copper'] = emitter('M_lum_copper', (1.0, 0.640, 0.360), 10.5, 0.5)
    lib['lum_amber'] = amber_panel()
    lib['lum_white'] = emitter('M_lum_white', (1.0, 0.965, 0.920), 2.4, 0.5)
    lib['led_red'] = emitter('M_led_red', (1.0, 0.105, 0.075), 1.5, 0.4)
    lib['led_amber'] = emitter('M_led_amber', (1.0, 0.545, 0.145), 1.2, 0.4)
    lib['led_drl'] = emitter('M_led_drl', (1.0, 0.985, 0.955), 1.6, 0.4)
    lib['wood'] = walnut(False)
    lib['wood_light'] = walnut(True)
    lib['leather'] = leather_cream()
    lib['marble'] = marble()
    lib['carpet'] = carpet()
    lib['ceiling'] = ceiling_mat()
    lib['tire'] = tire()
    lib['wheel'] = wheel_bronze()
    lib['black'] = black_plastic()
    lib['black_rough'] = black_plastic(0.68, key='black')
    lib['roofkit'] = roof_kit()
    lib['gunmetal'] = gunmetal()
    lib['cast'] = cast_metal()
    lib['car'] = car_paint()
    lib['wall'] = interior_wall()
    lib['trim'] = trim_satin()
    lib['shower'] = glass_shower()
    lib['oak'] = oak_flat()
    lib['stone'] = stone_flat()
    return lib

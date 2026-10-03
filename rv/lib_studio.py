# -*- coding: utf-8 -*-
"""Studio: gradient world, seamless floor, five-point lighting, auto-framed camera."""
import bpy
import math
from math import radians, sin, cos
from mathutils import Vector, Matrix


def si(node, key, val):
    if key in node.inputs:
        try:
            node.inputs[key].default_value = val
        except Exception:
            pass


# ------------------------------------------------------------------- world
def build_world(zenith=(0.780, 0.740, 0.692), horizon=(0.722, 0.682, 0.634),
                ground=(0.536, 0.504, 0.466)):
    """High-key warm environment. Matched to the reference plate: the vehicle
    sits in a bright cream ambience, so the body reads warm ivory and the
    rims/glass pick up a believable warm reflection instead of grey.

    Rule of thumb that this rig is built around: with a near-uniform world of
    radiance L, a diffuse surface of albedo rho renders at exactly rho*L, so
    target_albedo = target_colour / L.  Keep this in mind when editing."""
    w = bpy.data.worlds.get('RVWorld') or bpy.data.worlds.new('RVWorld')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    out.location = (600, 0)
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.location = (380, 0)
    bg.inputs['Strength'].default_value = 1.0
    nt.links.new(bg.outputs[0], out.inputs['Surface'])

    geo = nt.nodes.new('ShaderNodeNewGeometry')
    geo.location = (-1100, 0)
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    sep.location = (-920, 0)
    nt.links.new(geo.outputs['Incoming'], sep.inputs['Vector'])
    neg = nt.nodes.new('ShaderNodeMath')
    neg.operation = 'MULTIPLY'
    neg.location = (-740, 0)
    neg.inputs[1].default_value = -1.0
    nt.links.new(sep.outputs['Z'], neg.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.location = (-540, 0)
    mr.inputs['From Min'].default_value = -1.0
    mr.inputs['From Max'].default_value = 1.0
    mr.inputs['To Min'].default_value = 0.0
    mr.inputs['To Max'].default_value = 1.0
    nt.links.new(neg.outputs[0], mr.inputs['Value'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-280, 0)
    cr = ramp.color_ramp
    stops = ((0.30, ground), (0.52, horizon), (0.90, zenith))
    cr.elements[0].position = stops[0][0]
    cr.elements[0].color = stops[0][1] + (1.0,)
    cr.elements[1].position = stops[1][0]
    cr.elements[1].color = stops[1][1] + (1.0,)
    e2 = cr.elements.new(stops[2][0])
    e2.color = stops[2][1] + (1.0,)
    nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    return w


# ------------------------------------------------------------------- floor
def build_floor(cream=(1.005, 0.877, 0.753), white=0.90, mix=0.55, size=520.0,
                gloss=0.36):
    """Seamless cream cyclorama. Emission keeps the backdrop dead flat; the
    diffuse layer carries the contact shadow. In the lit area the two layers
    are calibrated to cancel, so the backdrop colour == `cream` exactly."""
    m = bpy.data.materials.new('M_studio_floor')
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    out.location = (600, 0)
    mxs = nt.nodes.new('ShaderNodeMixShader')
    mxs.location = (380, 0)
    mxs.inputs['Fac'].default_value = mix
    sur = nt.nodes.new('ShaderNodeBsdfPrincipled')
    sur.location = (120, -160)
    si(sur, 'Base Color', (white, white * 0.995, white * 0.982, 1.0))
    si(sur, 'Roughness', gloss)
    si(sur, 'Metallic', 0.0)
    si(sur, 'Specular IOR Level', 0.30)
    em = nt.nodes.new('ShaderNodeEmission')
    em.location = (120, 140)
    em.inputs['Color'].default_value = (cream[0], cream[1], cream[2], 1.0)
    em.inputs['Strength'].default_value = 1.0
    nt.links.new(sur.outputs[0], mxs.inputs[1])
    nt.links.new(em.outputs[0], mxs.inputs[2])
    nt.links.new(mxs.outputs[0], out.inputs['Surface'])

    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    fl = bpy.context.active_object
    fl.name = 'STUDIO_floor'
    fl.data.materials.append(m)
    return fl


# ------------------------------------------------------------------- lights
def _light(name, kind, loc, target=(0, 0, 2.0), power=1000.0, size=6.0,
           color=(1, 1, 1), shape='SQUARE', shadow=True):
    d = bpy.data.lights.new(name, kind)
    d.energy = power
    d.color = color
    if hasattr(d, 'use_shadow'):
        d.use_shadow = shadow
    if kind == 'AREA':
        d.shape = shape
        if shape == 'SQUARE':
            d.size = size
        else:
            d.size = size
            d.size_y = size
    elif kind == 'SUN':
        d.angle = radians(size)
    elif kind == 'POINT':
        d.shadow_soft_size = size
    ob = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    v = Vector(target) - Vector(loc)
    # An area light emits along its LOCAL -Z, so -Z must point AT the subject:
    # feed the positive target-minus-location vector. Negating it aims every
    # light away from the model and silently flattens the whole render.
    ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    return ob


def sph(az_deg, el_deg, dist, center=(0, 0, 2.0)):
    a, e = radians(az_deg), radians(el_deg)
    return (center[0] + dist * cos(e) * cos(a),
            center[1] + dist * cos(e) * sin(a),
            center[2] + dist * sin(e))


def build_lights(scale=1.0, center=(0, 0, 2.0), yaw=-62.0):
    """High-key rig for colour matching. The cream world does most of the
    lighting; these only shape the form and cast the ground shadow. Keep the
    total well under the ambient or the measured body colour will drift."""
    L = {}
    L['key'] = _light('L_key', 'AREA', sph(yaw - 34, 50, 40, center), center,
                      power=4600 * scale, size=16.0, color=(1.0, 0.975, 0.935))
    L['fill'] = _light('L_fill', 'AREA', sph(yaw + 62, 14, 56, center), center,
                       power=740 * scale, size=40.0, color=(0.94, 0.955, 1.0),
                       shadow=False)
    L['rim'] = _light('L_rim', 'AREA', sph(yaw + 150, 34, 40, center), center,
                      power=900 * scale, size=18.0, color=(1.0, 0.965, 0.920),
                      shadow=False)
    L['top'] = _light('L_top', 'AREA', (center[0], center[1], center[2] + 44),
                      center, power=360 * scale, size=48.0,
                      color=(1.0, 0.99, 0.970), shadow=False)
    return L


INT_GAIN = 0.0


def build_interior_lights(zs=(2.72,), powers=None, xs=(-3.6, -1.5, 0.8, 3.0)):
    """Warm ceiling wash inside the shell so windows read as glowing rooms."""
    out = []
    px = powers or [430, 470, 455, 420]
    for i, x in enumerate(xs):
        d = bpy.data.lights.new('L_int_%d' % i, 'AREA')
        d.shape = 'RECTANGLE'
        d.size = 2.6
        d.size_y = 0.55
        d.energy = px[i] * INT_GAIN
        d.color = (1.0, 0.815, 0.620)
        ob = bpy.data.objects.new('L_int_%d' % i, d)
        bpy.context.collection.objects.link(ob)
        d.use_shadow = False
        ob.location = (x, 0.0, 2.78)
        ob.rotation_euler = (0.0, 0.0, 0.0)
        out.append(ob)
    return out


WINDOW_LAMPS = [
    (-3.30, 2.52), (0.75, 2.52), (-0.55, 2.52), (2.35, 2.52),
]
WINDOW_LAMPS2 = [(4.78, 2.52), (1.00, 2.52), (-2.40, 2.52)]


def build_window_glow():
    """Small warm floods tucked just inside every window so the glazing reads
    as an illuminated interior rather than a grey slab."""
    out = []
    for (x, z) in WINDOW_LAMPS + WINDOW_LAMPS2:
        for s in (-1, 1):
            d = bpy.data.lights.new('L_win_%.2f_%d' % (x, s), 'AREA')
            d.shape = 'RECTANGLE'
            d.size = 1.90
            d.size_y = 0.55
            d.energy = 260.0 * INT_GAIN
            d.color = (1.0, 0.780, 0.545)
            ob = bpy.data.objects.new('L_win_%.2f_%d' % (x, s), d)
            bpy.context.collection.objects.link(ob)
            d.use_shadow = False
            ob.location = (x, s * 0.860, z - 0.16)
            v = Vector((x, s * 0.05, z - 0.85)) - Vector(ob.location)
            ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
            out.append(ob)
    # galley / bath task lights
    for (x, y, z, p) in ((0.10, -1.00, 2.62, 120), (-1.20, -0.90, 2.55, 110),
                         (-1.45, 0.60, 2.45, 90), (-4.40, 0.0, 2.55, 170)):
        d = bpy.data.lights.new('L_task_%.2f_%.2f' % (x, y), 'AREA')
        d.shape = 'RECTANGLE'
        d.size = 1.30
        d.size_y = 0.55
        d.energy = p * INT_GAIN
        d.color = (1.0, 0.800, 0.580)
        ob = bpy.data.objects.new('L_task_%.2f_%.2f' % (x, y), d)
        bpy.context.collection.objects.link(ob)
        d.use_shadow = False
        ob.location = (x, y, z)
        v = Vector((x, 0.0, 1.30)) - Vector(ob.location)
        ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
        out.append(ob)
    return out


# ------------------------------------------------------------------- camera
def make_camera(focal=85.0, sensor=36.0):
    cd = bpy.data.cameras.new('RVCam')
    cd.lens = focal
    cd.sensor_width = sensor
    cd.sensor_fit = 'AUTO'
    cd.clip_start = 0.4
    cd.clip_end = 900.0
    cam = bpy.data.objects.new('RVCam', cd)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def _corners(objs, dg):
    pts = []
    for ob in objs:
        if ob.type != 'MESH':
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ob.matrix_world
        for v in me.vertices:
            pts.append(mw @ v.co)
        ev.to_mesh_clear()
    return pts


def _cam_frame(loc, tgt):
    fwd = (Vector(tgt) - Vector(loc)).normalized()
    up_ref = Vector((0.0, 0.0, 1.0))
    if abs(fwd.dot(up_ref)) > 0.9995:
        up_ref = Vector((0.0, 1.0, 0.0))
    right = fwd.cross(up_ref).normalized()
    up = right.cross(fwd).normalized()
    return fwd, right, up


def project(pts, loc, tgt, focal, sensor_w, aspect):
    """Manual world->screen projection (u,v in 0..1). Returns None if behind."""
    fwd, right, up = _cam_frame(loc, tgt)
    out = []
    for p in pts:
        d = Vector(p) - Vector(loc)
        z = d.dot(fwd)
        if z <= 0.05:
            return None
        hw = z * (sensor_w * 0.5 / focal)
        hh = hw / aspect if aspect >= 1.0 else hw * aspect
        out.append((0.5 + d.dot(right) / (2.0 * hw), 0.5 + d.dot(up) / (2.0 * hh)))
    return out


def aim(cam, loc, tgt):
    cam.location = Vector(loc)
    v = Vector(tgt) - Vector(loc)
    cam.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    return cam


def fit_camera(cam, objs, center, az, el, dist, target_w=0.78, target_h=0.72,
               iters=8, verbose=False):
    scene = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    pts = _corners(objs, dg)
    if not pts:
        return dist, Vector(center)
    aspect = scene.render.resolution_x / float(scene.render.resolution_y)
    focal = cam.data.lens
    sensor = cam.data.sensor_width
    tgt = Vector(center)
    for k in range(iters):
        loc = Vector(sph(az, el, dist, tgt))
        pr = project(pts, loc, tgt, focal, sensor, aspect)
        if pr is None:
            dist *= 1.6
            continue
        us = [p[0] for p in pr]
        vs = [p[1] for p in pr]
        u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
        cw, ch = max(u1 - u0, 1e-6), max(v1 - v0, 1e-6)
        s = min(target_w / cw, target_h / ch)
        s = max(min(s, 2.0), 0.55)
        if verbose:
            print('FIT %d cov=%.3f,%.3f s=%.3f dist=%.2f' % (k, cw, ch, s, dist))
        dist = dist / s
        hw = dist * (sensor * 0.5 / focal)
        hh = hw / aspect
        right = _cam_frame(loc, tgt)[1]
        up = _cam_frame(loc, tgt)[2]
        cu, cv = (u0 + u1) * 0.5, (v0 + v1) * 0.5
        tgt = tgt + right * ((cu - 0.5) * 2.0 * hw) + up * ((cv - 0.5) * 2.0 * hh)
    loc = Vector(sph(az, el, dist, tgt))
    aim(cam, loc, tgt)
    bpy.context.view_layer.update()
    return dist, tgt


# ------------------------------------------------------------------- render
def setup_render(w=1920, h=1080, samples=160, view_transform='Standard'):
    sc = bpy.context.scene
    sc.render.resolution_x = w
    sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.film_transparent = False
    try:
        sc.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
    ee = sc.eevee
    for k, v in (('taa_render_samples', samples), ('use_raytracing', True),
                 ('use_shadows', True), ('use_volumetric_shadows', False),
                 ('use_gtao', True), ('use_bloom', True),
                 ('shadow_ray_count', 2), ('shadow_step_count', 8)):
        if hasattr(ee, k):
            try:
                setattr(ee, k, v)
            except Exception:
                pass
    if hasattr(ee, 'ray_tracing_options'):
        try:
            ee.ray_tracing_options.resolution_scale = '1'
            ee.ray_tracing_options.use_denoise = True
        except Exception:
            pass
    try:
        sc.view_settings.view_transform = view_transform
    except Exception:
        pass
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    for look in ('None', 'Medium Contrast', 'Medium High Contrast'):
        try:
            sc.view_settings.look = look
            break
        except Exception:
            continue
    sc.render.filter_size = 1.5
    return sc


def s2l(c):
    """sRGB 0-255 tuple -> linear float tuple."""
    out = []
    for v in c[:3]:
        v = v / 255.0
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def l2s(v):
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * (v ** (1 / 2.4)) - 0.055


def l2hex(l):
    return '#%02X%02X%02X' % tuple(int(round(l2s(x) * 255)) for x in l[:3])


def readback(path, corners=((0.06, 0.06), (0.94, 0.06), (0.06, 0.94), (0.94, 0.94))):
    """Return linear pixel samples - top strip = 'sky', bottom = 'floor'."""
    im = bpy.data.images.load(path, check_existing=False)
    W, H = im.size
    px = list(im.pixels)
    out = {}

    def sample(u, v):
        x = int(u * (W - 1))
        y = int((1.0 - v) * (H - 1))
        i = (y * W + x) * 4
        return (px[i], px[i + 1], px[i + 2])

    out['bg_top'] = sample(0.5, 0.045)
    out['bg_bot'] = sample(0.5, 0.965)
    out['fl_left'] = sample(0.06, 0.90)
    out['fl_right'] = sample(0.94, 0.90)
    out['center'] = sample(0.5, 0.5)
    bpy.data.images.remove(im)
    return out


def srgb(x):
    return 12.92 * x if x <= 0.0031308 else 1.055 * (x ** (1 / 2.4)) - 0.055

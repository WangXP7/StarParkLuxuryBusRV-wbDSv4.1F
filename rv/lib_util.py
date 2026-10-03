# -*- coding: utf-8 -*-
"""Geometry helpers - pure bpy/bmesh, no external assets."""
import bpy, bmesh, math
from math import radians, sin, cos, pi
from mathutils import Vector, Matrix, Euler

COLL = None


def set_collection(ob):
    if COLL is not None:
        try:
            for c in list(ob.users_collection):
                c.objects.unlink(ob)
            COLL.objects.link(ob)
        except Exception:
            pass
    return ob


def mesh_from_pydata(name, verts, faces, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False)
    me.update()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ob["rv_part"] = "body"
    return ob


def _finish(name, bm, mat, smooth, bevel, segs):
    if bevel and bevel > 0.0:
        try:
            bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                            offset=bevel, segments=segs, profile=0.5,
                            affect='EDGES', clamp_overlap=True)
        except TypeError:
            bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                            offset=bevel, segments=segs, profile=0.5,
                            clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def box(name, size, loc=(0, 0, 0), rot=(0, 0, 0), mat=None, bevel=0.0, segs=2, smooth=False):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    pre = 1.0
    if bevel and bevel > 0.0:
        try:
            bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                            offset=bevel, segments=segs, profile=0.5,
                            affect='EDGES', clamp_overlap=True)
        except TypeError:
            pass
    bm.transform(Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4())
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def cyl(name, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), axis='Z', segs=24, mat=None,
        smooth=True, caps=True, r2=None, bevel=0.0):
    bm = bmesh.new()
    rr2 = r if r2 is None else r2
    try:
        bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segs,
                              radius1=r, radius2=rr2, depth=depth)
    except TypeError:
        bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=segs,
                              diameter1=r * 2, diameter2=rr2 * 2, depth=depth)
    pre = {'Z': (0, 0, 0), 'X': (0, radians(90), 0), 'Y': (radians(-90), 0, 0)}[axis]
    M = (Matrix.Translation(Vector(loc))
         @ Euler(rot, 'XYZ').to_matrix().to_4x4()
         @ Euler(pre, 'XYZ').to_matrix().to_4x4())
    bm.transform(M)
    return _finish(name, bm, mat, smooth, bevel, 2)


def sphere(name, r, loc=(0, 0, 0), scale=(1, 1, 1), mat=None, segs=24, rings=14, smooth=True):
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    except TypeError:
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, diameter=r * 2)
    bmesh.ops.scale(bm, vec=Vector(scale), verts=bm.verts)
    bm.transform(Matrix.Translation(Vector(loc)))
    return _finish(name, bm, mat, smooth, 0.0, 2)


def rrect_profile(hw, hh, rc, rb=None, n=10, ns=6):
    """CCW rounded-rect profile in (u,v). u = half width, v = half height.
    ns = subdivisions inserted on each straight edge (so side walls can be holed)."""
    rb = rc if rb is None else rb
    pts = []

    def arc(cu, cv, r, a0, a1):
        for i in range(n):
            a = radians(a0 + (a1 - a0) * i / n)
            pts.append((cu + r * cos(a), cv + r * sin(a)))

    def edge(p0, p1):
        for i in range(1, ns + 1):
            t = i / float(ns + 1)
            pts.append((p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t))

    # right edge (bottom -> top)
    edge((hw, -hh + rb), (hw, hh - rc))
    arc(hw - rc, hh - rc, rc, 0, 90)
    edge((hw - rc, hh), (-hw + rc, hh))
    arc(-hw + rc, hh - rc, rc, 90, 180)
    edge((-hw, hh - rc), (-hw, -hh + rb))
    arc(-hw + rb, -hh + rb, rb, 180, 270)
    edge((-hw + rb, -hh), (hw - rb, -hh))
    arc(hw - rb, -hh + rb, rb, 270, 360)
    return pts


def flat_cap(name, prof, x, cz=0.0, cy=0.0, scales=(1.0, 0.9, 0.8), mat=None,
             open_last=False, smooth=False):
    """Concentric scaled copies of a profile laid on a plane at x - a flat end face."""
    verts, faces, rings = [], [], []
    n = len(prof)
    for s in scales:
        rings.append(len(verts))
        for (u, v) in prof:
            verts.append((x, cy + u * s, cz + v * s))
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(n):
            j = (i + 1) % n
            faces.append((a + i, a + j, b + j, b + i))
    if not open_last:
        faces.append(tuple(range(rings[-1], rings[-1] + n)))
    return mesh_from_pydata(name, verts, faces, mat, smooth)


def band_sweep(name, xs, ztop, zbot, y_out, y_in, mat=None, smooth=False):
    """Vertical band whose lower edge follows zbot(x) - used for the skirt/arches."""
    verts, faces = [], []
    for i, x in enumerate(xs):
        zo, zb = ztop[i], zbot[i]
        verts += [(x, y_out, zb), (x, y_in, zb), (x, y_in, zo), (x, y_out, zo)]
    m = len(xs)
    for i in range(m - 1):
        a, b = i * 4, (i + 1) * 4
        for k in range(4):
            k2 = (k + 1) % 4
            faces.append((a + k, a + k2, b + k2, b + k))
    faces.append((0, 1, 2, 3))
    a = (m - 1) * 4
    faces.append((a + 3, a + 2, a + 1, a))
    return mesh_from_pydata(name, verts, faces, mat, smooth)


def rrect_plate(name, hw, hh, rc, x0, x1, cz=0.0, cy=0.0, mat=None, n=8, smooth=False):
    """Flat vertical (YZ-plane) rounded-rect plate with thickness along X."""
    prof = rrect_profile(hw, hh, rc, rc, n=n, ns=0)
    return loft(name, prof, [{'x': x0, 'cy': cy, 'cz': cz},
                             {'x': x1, 'cy': cy, 'cz': cz}], mat=mat, smooth=smooth)


def ring(name, hwo, hho, hwi, hhi, rc, t0, t1, cx=0.0, cz=0.0, ux='X', mat=None, n=10):
    """Flat rounded-rect annulus of width (hwo-hwi) and thickness (t1-t0)
    along the ux axis. ux 'Y': plate lies in XZ (flank). ux 'X': plate in YZ (ends)."""
    po = rrect_profile(hwo, hho, rc, rc, n=n, ns=0)
    pi = rrect_profile(hwi, hhi, rc, rc, n=n, ns=0)
    N = len(po)
    verts = []
    for t in (t0, t1):
        for (u, v) in po:
            verts.append((cx + u, t, cz + v) if ux == 'Y' else (t, cx + u, cz + v))
        for (u, v) in pi:
            verts.append((cx + u, t, cz + v) if ux == 'Y' else (t, cx + u, cz + v))
    faces = []
    for i in range(N):
        j = (i + 1) % N
        faces.append((i, j, 2 * N + j, 2 * N + i))
        faces.append((N + i, N + j, 3 * N + j, 3 * N + i))
        faces.append((i, N + i, N + j, j))
        faces.append((2 * N + i, 3 * N + i, 3 * N + j, 2 * N + j))
    return mesh_from_pydata(name, verts, faces, mat, False)


def loft(name, profile, stations, mat=None, smooth=True, caps=True, plane='YZ'):
    """stations: dicts with x (station axis value), cy, cz, sy, sz.
    plane 'YZ': station->X, u->Y, v->Z   (plates facing front/rear)
    plane 'XZ': station->Y, u->X, v->Z   (plates on the flanks)
    plane 'XY': station->Z, u->X, v->Y   (horizontal plates)"""
    verts, faces, rings = [], [], []
    n = len(profile)
    for st in stations:
        x = st['x']
        cy = st.get('cy', 0.0)
        cz = st.get('cz', 0.0)
        sy = st.get('sy', 1.0)
        sz = st.get('sz', 1.0)
        rings.append(len(verts))
        for (u, v) in profile:
            a, b = cy + u * sy, cz + v * sz
            if plane == 'YZ':
                verts.append((x, a, b))
            elif plane == 'XZ':
                verts.append((a, x, b))
            else:
                verts.append((a, b, x))
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(n):
            j = (i + 1) % n
            faces.append((a + i, a + j, b + j, b + i))
    if caps:
        faces.append(tuple(range(rings[0] + n - 1, rings[0] - 1, -1)))
        faces.append(tuple(range(rings[-1], rings[-1] + n)))
    return mesh_from_pydata(name, verts, faces, mat, smooth)


def panel(name, prof_uv, stations, mat=None, smooth=False):
    """Open (uncapped) lofted panel - for skirts, shells."""
    return loft(name, prof_uv, stations, mat=mat, smooth=smooth, caps=False)


def revolve_y(name, section, cx, cy, cz, mat=None, segs=32, smooth=True,
              close=True, a0=0.0, a1=360.0):
    """Revolve a closed (r,y) section around the Y axis through (cx,cy,cz)."""
    verts, faces = [], []
    m = len(section)
    full = abs(a1 - a0) >= 359.9
    n = segs if full else segs + 1
    for i in range(n):
        a = radians(a0 + (a1 - a0) * i / float(segs))
        ca, sa = cos(a), sin(a)
        for (r, y) in section:
            verts.append((cx + r * ca, cy + y, cz + r * sa))
    for i in range(segs if full else segs):
        a, b = i * m, ((i + 1) % segs) * m if full else (i + 1) * m
        for k in range(m):
            k2 = (k + 1) % m
            faces.append((a + k, a + k2, b + k2, b + k))
    if not full and close:
        faces.append(tuple(range(m - 1, -1, -1)))
        a = segs * m
        faces.append(tuple(range(a, a + m)))
    return mesh_from_pydata(name, verts, faces, mat, smooth)


def set_origin_geo(ob):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    return ob


def curve_tube(name, points, radius, mat=None, res=4, cyclic=False):
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '3D'
    sp = cu.splines.new('POLY')
    sp.points.add(len(points) - 1)
    for i, p in enumerate(points):
        sp.points[i].co = (p[0], p[1], p[2], 1.0)
    sp.use_cyclic_u = cyclic
    cu.bevel_depth = radius
    cu.bevel_resolution = res
    cu.resolution_u = 2
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    if mat is not None:
        cu.materials.append(mat)
    return ob


def arc_pts(cx, cy, r, a0, a1, n=24, z=0.0, x=0.0, plane='XY'):
    out = []
    for i in range(n + 1):
        a = radians(a0 + (a1 - a0) * i / n)
        if plane == 'XY':
            out.append((x + r * cos(a), cy + r * sin(a), z))
        else:
            out.append((x + r * cos(a), cy, z + r * sin(a)))
    return out


def join(objs, name):
    objs = [o for o in objs if o is not None and o.name in bpy.data.objects]
    if not objs:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = name
    return ob


def shade_auto(ob, angle=32.0):
    bpy.ops.object.select_all(action='DESELECT')
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    try:
        bpy.ops.object.shade_auto_smooth(angle=radians(angle))
    except Exception:
        for p in ob.data.polygons:
            p.use_smooth = True


def mark(ob, tag):
    ob["rv_tag"] = tag
    return ob

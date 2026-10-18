# Lab4U hero — the microscope, built from code in Blender (same proportions as the v20 canvas model).
# Run headless:  Blender -b -P microscope.py -- <out.blend> <render.png> [view] [out.glb]
# The .glb (modifiers applied, no lights, camera or floor) is what the site loads: cases/lab4u/3d/microscope.glb
# Coordinates below are the canvas ones (x right, y up, z toward the viewer); J() turns them into Blender's (z up, front = −y).
import bpy, bmesh, math, sys
from math import sin, cos, pi, radians

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT_BLEND = argv[0] if len(argv) > 0 else '/tmp/microscope.blend'
OUT_PNG = argv[1] if len(argv) > 1 else '/tmp/microscope.png'
VIEW = argv[2] if len(argv) > 2 else 'hero'
OUT_GLB = argv[3] if len(argv) > 3 else ''

J = lambda q: (q[0], -q[2], q[1])

# ---------- scene ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------- materials ----------
def mat(name, color, rough=.4, metal=0., coat=0., emit=None, estr=0., trans=0., ior=1.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; I = b.inputs
    I['Base Color'].default_value = (*color, 1); I['Roughness'].default_value = rough; I['Metallic'].default_value = metal
    if coat: I['Coat Weight'].default_value = coat; I['Coat Roughness'].default_value = .08
    if emit: I['Emission Color'].default_value = (*emit, 1); I['Emission Strength'].default_value = estr
    if trans: I['Transmission Weight'].default_value = trans; I['IOR'].default_value = ior
    return m
M = {
    'body':  mat('Enamel', (.44, .46, .48), rough=.14, coat=1.),           # lacquered cast body (on the site: gloss black in the dark theme)
    'dark':  mat('Anodized', (.035, .037, .04), rough=.2, metal=.55, coat=.8),  # stage, knobs, objective barrels
    'chrome': mat('Chrome', (.86, .88, .9), rough=.03, metal=1.),          # rings and objective tips
    'acc':   mat('BandActive', (0., .55, .72), rough=.15, coat=.6),        # the band on the active objective (the site recolours bands by name)
    'band':  mat('Band', (.035, .037, .04), rough=.3, metal=.4),            # the band on the others
    'glass': mat('Slide', (.93, 1., .97), rough=.02, trans=1., ior=1.52),  # the glass slide: clear soda-lime glass
    'lamp':  mat('Lamp', (0., .7, .85), emit=(0., .62, .9), estr=2.2),     # the illuminator and the eye lens
}

def obj_from_bm(name, bm, mats, bevel=.012, parent=None, loc=(0, 0, 0)):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for k in mats: me.materials.append(M[k])
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); ob.location = loc
    if parent: ob.parent = parent
    if bevel:
        bv = ob.modifiers.new('Bevel', 'BEVEL'); bv.width = bevel; bv.segments = 3; bv.limit_method = 'ANGLE'; bv.angle_limit = radians(30); bv.harden_normals = True
    return ob

def lathe(name, prof, n, segmats, xf=lambda q: q, bevel=.01, parent=None, loc=(0, 0, 0)):
    """profile [(r, y)…] from the bottom centre up to the top centre, turned round the local y axis; xf places it"""
    mats = sorted(set(segmats)); bm = bmesh.new(); rings = []
    for r, y in prof:
        rings.append(None if r < 1e-6 else [bm.verts.new(J(xf((cos(i / n * 2 * pi) * r, y, sin(i / n * 2 * pi) * r)))) for i in range(n)])
    for j in range(len(prof) - 1):
        A, B, mi = rings[j], rings[j + 1], mats.index(segmats[j])
        if A is None and B is None: continue
        if A is None or B is None:
            f = bm.faces.new(B if A is None else A); f.material_index = mi; continue
        for i in range(n):
            f = bm.faces.new((A[i], A[(i + 1) % n], B[(i + 1) % n], B[i])); f.material_index = mi
    return obj_from_bm(name, bm, mats, bevel, parent, loc)

def loft(name, rings, k, bevel=.012):
    bm = bmesh.new(); V = [[bm.verts.new(J(q)) for q in r] for r in rings]; n = len(rings[0])
    for j in range(len(V) - 1):
        for i in range(n): bm.faces.new((V[j][i], V[j][(i + 1) % n], V[j + 1][(i + 1) % n], V[j + 1][i]))
    bm.faces.new(V[0]); bm.faces.new(V[-1])
    return obj_from_bm(name, bm, [k], bevel)

def rr(cx, cz, w, d, rad, y, seg=10):
    o = []; hw, hd = w / 2 - rad, d / 2 - rad
    for qx, qz, a0 in ((hw, hd, 0), (-hw, hd, 90), (-hw, -hd, 180), (hw, -hd, 270)):
        for k in range(seg + 1):
            a = radians(a0 + k * 90 / seg); o.append((cx + qx + cos(a) * rad, y, cz + qz + sin(a) * rad))
    return o

def slab(name, cx, cz, w, d, rad, y0, y1, k, bevel=.012):
    return loft(name, [rr(cx, cz, w, d, rad, y0), rr(cx, cz, w, d, rad, y1)], k, bevel)

rotX = lambda a: (lambda q: (q[0], q[1] * cos(a) - q[2] * sin(a), q[1] * sin(a) + q[2] * cos(a)))
at = lambda x, y, z, f=None: (lambda q: (lambda r: (r[0] + x, r[1] + y, r[2] + z))(f(q) if f else q))

# ---------- the microscope ----------
root = bpy.data.objects.new('Microscope', None); sc.collection.objects.link(root)
def own(ob): ob.parent = root; return ob

own(slab('Base', 0, .12, 2.4, 2.0, .42, 0, .3, 'body', bevel=.06))
own(lathe('Illuminator', [(0, .3), (.3, .3), (.3, .36), (.24, .4), (0, .4)], 64, ['chrome'] * 4, at(0, 0, .2)))
own(lathe('Lamp', [(0, .401), (.2, .401), (.2, .406), (0, .406)], 64, ['lamp'] * 3, at(0, 0, .2), bevel=0))

# arm: a rounded section swept up from the back of the base, bowing back and curving forward into the head
AN, SN = 72, 40
path = [(0, .22 + 2.5 * t, -.66 - .2 * sin(pi * t) + .55 * t ** 3) for t in (i / AN for i in range(AN + 1))]
def sec(t):
    hw, hd = .27 - .07 * t, .21 - .03 * t; o = []
    for i in range(SN):
        a = i / SN * 2 * pi; c, s = cos(a), sin(a)
        o.append((math.copysign(abs(c) ** .45, c) * hw, math.copysign(abs(s) ** .45, s) * hd))
    return o
rings = []
for i, q in enumerate(path):
    a, b = path[max(0, i - 1)], path[min(AN, i + 1)]; ty, tz = b[1] - a[1], b[2] - a[2]; l = math.hypot(ty, tz); ny, nz = -tz / l, ty / l
    rings.append([(u, q[1] + ny * v, q[2] + nz * v) for u, v in sec(i / AN)])
own(loft('Arm', rings, 'body', bevel=.02))

# focus knobs on both sides of the arm: coarse (anodized) and fine (enamel)
for sd, nm in ((-1, 'L'), (1, 'R')):
    own(lathe('Knob' + nm, [(0, 0), (.3, 0), (.33, .03), (.33, .13), (.3, .16), (.17, .16), (.17, .28), (.155, .31), (0, .31)], 72,
              ['dark'] * 5 + ['body'] * 3, at(sd * .25, .78, -.8, lambda q, sd=sd: (sd * q[1], q[0], q[2]))))

# stage on its carrier, the slide and two clips on it, the condenser under it
own(slab('Carrier', 0, -.42, .5, .5, .06, 1.02, 1.16, 'body'))
own(slab('Stage', 0, .18, 1.8, 1.42, .08, 1.13, 1.22, 'dark', bevel=.015))
own(slab('Slide', 0, .2, 1.06, .38, .015, 1.22, 1.245, 'glass', bevel=.004))
for sd, nm in ((-1, 'L'), (1, 'R')): own(slab('Clip' + nm, sd * .62, .08, .13, .62, .03, 1.22, 1.27, 'chrome', bevel=.008))
own(lathe('Condenser', [(0, .72), (.13, .72), (.16, .76), (.16, .96), (.19, 1.0), (.19, 1.13), (0, 1.13)], 64, ['dark', 'dark', 'dark', 'chrome', 'chrome', 'chrome'], at(0, 0, .2)))

# head on top of the arm, the eyepiece leaning toward the viewer, the eye lens glowing
own(slab('Head', 0, -.02, .62, .92, .24, 2.48, 2.92, 'body', bevel=.05))
ep = at(0, 2.86, .12, rotX(.62))
own(lathe('Eyepiece', [(0, 0), (.17, 0), (.17, .12), (.13, .17), (.13, .6), (.16, .64), (.16, .86), (.13, .88), (0, .88)], 64,
          ['body', 'body', 'body', 'body', 'chrome', 'dark', 'dark', 'dark'], ep))
own(lathe('EyeLens', [(0, .881), (.1, .881), (.1, .886), (0, .886)], 48, ['lamp'] * 3, ep, bevel=0))

# nosepiece: a pivot (empty) on the vertical axis; three objectives hang .2 off it and turn with it, the one over the slide is active
pivot = bpy.data.objects.new('Nosepiece', None); sc.collection.objects.link(pivot); pivot.parent = root; pivot.location = J((0, 0, 0))
lathe('Turret', [(0, 2.3), (.33, 2.3), (.38, 2.38), (.36, 2.48), (0, 2.48)], 72, ['chrome'] * 4, parent=pivot)
OBJ = [(0, 1.82), (.045, 1.82), (.06, 1.86), (.072, 1.92), (.072, 2.03), (.082, 2.05), (.082, 2.09), (.082, 2.2), (.094, 2.23), (.094, 2.3), (0, 2.3)]
for o in range(3):
    A = o * 2 * pi / 3; band = 'acc' if o == 0 else 'band'
    turn = lambda q, A=A: (q[0] * cos(A) + (q[2] + .2) * sin(A), q[1], -q[0] * sin(A) + (q[2] + .2) * cos(A))
    lathe('Objective%d' % (o + 1), OBJ, 48, ['chrome', 'chrome', 'dark', 'dark', 'chrome', band, 'dark', 'dark', 'chrome', 'chrome'], turn, parent=pivot)

# a floor that only catches the shadow (the render stays transparent, so it sits on either theme)
bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0)); fl = bpy.context.active_object; fl.name = 'ShadowCatcher'; fl.is_shadow_catcher = True

# ---------- light, world, camera ----------
w = bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Color'].default_value = (.012, .013, .015, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1
def area(name, loc, power, size, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'AREA'); d.energy = power; d.size = size; d.color = color
    ob = bpy.data.objects.new(name, d); sc.collection.objects.link(ob); ob.location = loc
    c = ob.constraints.new('TRACK_TO'); c.target = root; return ob
area('Key', (-5, -6, 7), 1100, 5)
area('Rim', (5, 6, 5), 900, 4, (.75, .9, 1))
area('Fill', (7, -3, 1.5), 260, 6)
area('Top', (0, 0, 9), 300, 6)

cam = bpy.data.cameras.new('Cam'); cam.lens = 50; cam.sensor_fit = 'VERTICAL'; cam.sensor_height = 24
co = bpy.data.objects.new('Cam', cam); sc.collection.objects.link(co); sc.camera = co
tgt = bpy.data.objects.new('Target', None); sc.collection.objects.link(tgt); tgt.location = (0, 0, 1.78)
c = co.constraints.new('TRACK_TO'); c.target = tgt
VIEWS = {'hero': (62, 15, 11.2), 'front': (-28, 13, 11.2), 'side': (80, 8, 11.2)}  # azimuth from the front (deg, + = to the right), elevation, distance
az, el, dist = VIEWS.get(VIEW, VIEWS['hero'])
co.location = (dist * cos(radians(el)) * sin(radians(az)), -dist * cos(radians(el)) * cos(radians(az)), 1.78 + dist * sin(radians(el)))

# ---------- render ----------
sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'METAL'; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = 'GPU'
except Exception as e: print('GPU off:', e)
sc.cycles.samples = 96; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1080, 1350
sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
sc.render.filepath = OUT_PNG
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
if OUT_GLB:
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [root] + list(root.children_recursive): ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=OUT_GLB, export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
                              export_lights=False, export_cameras=False, export_extras=False)
    print('GLB', OUT_GLB)
bpy.ops.render.render(write_still=True)
print('DONE', OUT_PNG)

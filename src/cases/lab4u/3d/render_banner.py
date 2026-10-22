# Lab4U — a white microscope as a standalone PNG (transparent background) for banners.
# Opens microscope.blend (built by microscope.py): white lacquer body, black details, an orthographic camera.
# Two passes: the microscope itself, then a small shadow-only pass that is blurred, faded and put under it.
# The result is cropped to the microscope with a margin. The .blend itself is not saved.
# Run:  Blender -b microscope.blend -P render_banner.py -- <out.png> [size] [azimuth] [elevation] [shadow 0..1]
import bpy, sys, os
import numpy as np
from math import radians, sin, cos

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else '/tmp/microscope_white.png'
SIZE = int(argv[1]) if len(argv) > 1 else 4000
AZ = float(argv[2]) if len(argv) > 2 else 45     # degrees from the front, + = to the right
EL = float(argv[3]) if len(argv) > 3 else 30     # degrees above the horizon
SHADOW = float(argv[4]) if len(argv) > 4 else .6
sc = bpy.context.scene

def bsdf(name):
    m = bpy.data.materials.get(name); return m and m.node_tree.nodes.get('Principled BSDF')
# white lacquer body, glossy black details (Andrey, 22.10: «микроскоп прям белый, тёмные детали — чёрные»)
b = bsdf('Enamel'); b.inputs['Base Color'].default_value = (.93, .935, .94, 1); b.inputs['Roughness'].default_value = .18
b.inputs['Coat Weight'].default_value = 1.; b.inputs['Coat Roughness'].default_value = .04
for n in ('Anodized', 'Band'):   # no metal and a thin lacquer: the light studio would turn black metal grey
    b = bsdf(n); b.inputs['Base Color'].default_value = (.008, .009, .01, 1); b.inputs['Metallic'].default_value = 0
    b.inputs['Roughness'].default_value = .2; b.inputs['Coat Weight'].default_value = .3; b.inputs['Coat Roughness'].default_value = .06
    b.inputs['Specular IOR Level'].default_value = .25
# the lamp and the eyepiece lens: a saturated blue, as on the site (#006EA8 lit by #0090D0)
b = bsdf('Lamp'); b.inputs['Base Color'].default_value = (0, .156, .39, 1)
b.inputs['Emission Color'].default_value = (0, .28, .63, 1); b.inputs['Emission Strength'].default_value = .35

# a light studio with one dark flag: a band from ~10° to ~60° above the horizon, all round. The stage (seen from 14–30°)
# mirrors that band and stays black; the chrome sees the bright top and floor around it and reads silver, as on the site
nt = sc.world.node_tree; bg = nt.nodes['Background']
tc = nt.nodes.new('ShaderNodeTexCoord'); xyz = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(tc.outputs['Generated'], xyz.inputs[0])
def ramp(a, b, lo, hi, src):
    m = nt.nodes.new('ShaderNodeMapRange'); m.interpolation_type = 'SMOOTHSTEP'
    for k, v in (('From Min', a), ('From Max', b), ('To Min', lo), ('To Max', hi)): m.inputs[k].default_value = v
    nt.links.new(src, m.inputs['Value']); return m.outputs['Result']
band = nt.nodes.new('ShaderNodeMath'); band.operation = 'MULTIPLY'
nt.links.new(ramp(.14, .26, 0, 1, xyz.outputs['Z']), band.inputs[0]); nt.links.new(ramp(.8, .93, 1, 0, xyz.outputs['Z']), band.inputs[1])
nt.links.new(ramp(0, 1, .7, .012, band.outputs['Value']), bg.inputs['Strength']); bg.inputs['Color'].default_value = (.95, .96, .97, 1)
for ob in bpy.data.objects:
    if ob.type == 'LIGHT' and ob.name != 'Top':   # only the big top light casts: a soft contact shadow, no long band to the side
        ob.data.use_shadow = False
    if ob.type == 'LIGHT' and AZ < 0:   # a view from the left gets the mirrored light, else the rim glares in the stage
        ob.location.x *= -1
sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = .9

# orthographic camera aimed at the middle of the microscope
cam = sc.camera; tgt = bpy.data.objects.get('Target')
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 5.4; cam.data.sensor_fit = 'AUTO'; cam.data.clip_end = 100
D = 30
cam.location = (D * cos(radians(EL)) * sin(radians(AZ)), -D * cos(radians(EL)) * cos(radians(AZ)), 1.72 + D * sin(radians(EL)))
if tgt: tgt.location = (0, 0, 1.72)

sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'METAL'; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = 'GPU'
except Exception as e: print('GPU off:', e)
sc.cycles.use_denoising = True; sc.render.resolution_percentage = 100; sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.color_depth = '8'
catcher = bpy.data.objects['ShadowCatcher']
parts = [o for o in bpy.data.objects if o.type == 'MESH' and o is not catcher]

def render(path, size, samples):
    sc.render.resolution_x = sc.render.resolution_y = size; sc.cycles.samples = samples
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(path); w, h = im.size
    px = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(px); bpy.data.images.remove(im); os.remove(path)
    return px.reshape(h, w, 4)

# pass 1: the microscope alone
catcher.hide_render = True
obj = render(OUT + '.obj.png', SIZE, 256)
# pass 2: only the shadow on the floor (the parts are hidden from the camera but still cast it), at a quarter size
catcher.hide_render = False
for o in parts: o.visible_camera = False
LOW = SIZE // 4
sh = render(OUT + '.sh.png', LOW, 96)[..., 3]

def box(a, r, axis):
    c = np.cumsum(np.pad(a, [(r + 1, r) if i == axis else (0, 0) for i in range(2)], mode='edge'), axis=axis)
    return (np.take(c, range(2 * r + 1, c.shape[axis]), axis) - np.take(c, range(0, c.shape[axis] - 2 * r - 1), axis)) / (2 * r + 1)
r = max(1, LOW // 90)
for _ in range(3): sh = box(box(sh, r, 0), r, 1)      # three box passes ≈ a gaussian: a very soft shadow
def up(a, n):                                          # bilinear upscale to n×n
    i = np.linspace(0, a.shape[0] - 1, n); i0 = np.floor(i).astype(int); i1 = np.minimum(i0 + 1, a.shape[0] - 1); f = (i - i0)[:, None]
    a = a[i0] * (1 - f) + a[i1] * f
    return a[:, i0] * (1 - f.T) + a[:, i1] * f.T
sh = np.clip(up(sh, SIZE) * SHADOW, 0, 1)

# the shadow goes under the microscope: a cool dark grey, straight alpha
a = obj[..., 3:4]; s = sh[..., None] * (1 - a); A = a + s
rgb = (obj[..., :3] * a + np.array([.1, .105, .11]) * s) / np.maximum(A, 1e-6)
out = np.concatenate([rgb, A], -1)

# crop to what is visible, with a margin
ys, xs = np.where(out[..., 3] > .02)
pad = SIZE // 25
y0, y1 = max(0, ys.min() - pad), min(SIZE, ys.max() + pad); x0, x1 = max(0, xs.min() - pad), min(SIZE, xs.max() + pad)
out = np.ascontiguousarray(out[y0:y1, x0:x1], dtype=np.float32)
im = bpy.data.images.new('banner', x1 - x0, y1 - y0, alpha=True); im.pixels.foreach_set(out.ravel())
im.filepath_raw = OUT; im.file_format = 'PNG'; im.save()
print('DONE', OUT, x1 - x0, 'x', y1 - y0)

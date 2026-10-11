import re, os, shutil
from PIL import Image, ImageDraw
# Assemble the FinamX & Limex case: {{img:name}} in the template -> /cases/finam/img/name.webp
# Source PNGs (2x Figma exports) live in raw/ and are not committed; the generated webp files are.
D = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(os.path.dirname(D)))  # repo root
RAW = os.path.join(D, 'raw')
IMG = os.path.join(R, 'cases', 'finam', 'img')
URL = '/cases/finam/img/'
os.makedirs(IMG, exist_ok=True)
t = open(os.path.join(D, 'finam-template.html'), encoding='utf-8').read()
made = {}

def img(name):
    if name in made: return made[name]
    out = os.path.join(IMG, name + '.webp'); src = os.path.join(RAW, name + '.png')
    if os.path.exists(src):
        im = Image.open(src).convert('RGBA')
        maxw = 2400 if im.width > 1500 else 786   # desktop shots 2400 wide, phones stay at 2x (786)
        if im.width > maxw: im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        if name.startswith('m-'):  # phone frames come out of Figma on a white canvas: cut the corners round and transparent
            r = round(80 * im.width / 786); k = 4
            m = Image.new('L', (im.width * k, im.height * k), 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width * k - 1, im.height * k - 1), r * k, fill=255)
            im.putalpha(m.resize(im.size, Image.LANCZOS))
        im.save(out, 'WEBP', quality=84, method=6)
    assert os.path.exists(out), 'missing image ' + name
    w, h = Image.open(out).size
    made[name] = f'{URL}{name}.webp" width="{w // 2}" height="{h // 2}'
    return made[name]

html = re.sub(r'\{\{img:([a-z0-9-]+)\}\}', lambda m: img(m.group(1)), t)
dst = os.path.join(D, 'finam-case.html')
open(dst, 'w', encoding='utf-8').write(html)
size = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG))
print(dst, len(html) // 1024, 'KB;', len(made), 'images', size // 1024, 'KB')

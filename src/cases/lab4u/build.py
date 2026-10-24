import re, os, json, shutil
import struct
# Assemble the Lab4U case: {{img:name}} → src + width/height of /cases/lab4u/img/name.webp, {{EN}} → the English dictionary.
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'out')
R = os.path.dirname(os.path.dirname(os.path.dirname(D)))  # repo root
IMG = os.path.join(R, 'cases', 'lab4u', 'img')
URL = '/cases/lab4u/img/'
t = open(os.path.join(D, 'lab4u-template.html'), encoding='utf-8').read()
EN = json.load(open(os.path.join(D, 'en.json'), encoding='utf-8'))

shutil.rmtree(IMG, ignore_errors=True)
os.makedirs(IMG)
used = set()

def webp_size(p):
    # width/height from the WebP header (VP8 / VP8L / VP8X) — no Pillow needed
    b = open(p, 'rb').read(30); c = b[12:16]
    if c == b'VP8 ': w, h = struct.unpack('<HH', b[26:30]); return w & 0x3fff, h & 0x3fff
    if c == b'VP8L': v = int.from_bytes(b[21:25], 'little'); return (v & 0x3fff) + 1, ((v >> 14) & 0x3fff) + 1
    if c == b'VP8X': return int.from_bytes(b[24:27], 'little') + 1, int.from_bytes(b[27:30], 'little') + 1
    raise ValueError(p)

def rep(m):
    key = m.group(1)
    if key == 'EN':
        return json.dumps(EN, ensure_ascii=False)
    if key.startswith('img:'):
        n = key[4:]; src = os.path.join(OUT, n + '.webp')
        if n not in used:
            shutil.copyfile(src, os.path.join(IMG, n + '.webp')); used.add(n)
        w, h = webp_size(src)
        return f'src="{URL}{n}.webp" width="{w}" height="{h}"'
    raise KeyError(key)

html = re.sub(r'\{\{([^}]+)\}\}', rep, t)

def avif(m):
    # an image with a lossless-sourced out/name.avif next to its WebP: AVIF 4:4:4 keeps the flat UI edges crisp where lossy WebP smeared them,
    # at a smaller size; browsers without AVIF fall back to the WebP in <img>
    tag, name = m.group(0), m.group(1)
    a = os.path.join(OUT, name + '.avif')
    if not os.path.exists(a): return tag
    shutil.copyfile(a, os.path.join(IMG, name + '.avif'))
    return f'<picture><source type="image/avif" srcset="{URL}{name}.avif">{tag}</picture>'
html = re.sub(r'<img [^>]*src="' + re.escape(URL) + r'([\w-]+)\.webp"[^>]*>', avif, html)
shutil.copyfile(os.path.join(OUT, 'cover.webp'), os.path.join(IMG, 'cover.webp'))  # the home page «Cases» row thumbnail
dst = os.path.join(D, 'lab4u-case.html')
open(dst, 'w', encoding='utf-8').write(html)
size = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG))
print(dst, len(html) // 1024, 'KB;', len(used), 'images', size // 1024, 'KB')

import re, os, glob, shutil
# Assemble the Obzhora case: placeholders in the template become links to image files in /cases/obzhora/img/.
# (Images used to be inlined as data URIs — a 5.6 MB page that Telegram would not build a link preview for.)
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'out')
R = os.path.dirname(os.path.dirname(os.path.dirname(D)))  # repo root
IMG = os.path.join(R, 'cases', 'obzhora', 'img')
URL = '/cases/obzhora/img/'
t = open(os.path.join(D, 'obzhora-template.html'), encoding='utf-8').read()

shutil.rmtree(IMG, ignore_errors=True)
os.makedirs(IMG)

def put(path, name):
    shutil.copyfile(path, os.path.join(IMG, name))
    return URL + name

icons = sorted(glob.glob(os.path.join(OUT, 'icons', '*.png')))
icon_url = {}
def ic(n):
    if n not in icon_url:
        icon_url[n] = put(os.path.join(OUT, 'icons', n + '.png'), 'ic-' + n + '.png')
    return icon_url[n]

def iconrow(i):
    names = [os.path.basename(p)[:-4] for p in icons][i::3]
    return ''.join(f'<img src="{ic(n)}" alt="" decoding="async">' for n in names)

def rep(m):
    key = m.group(1)
    if key.startswith('svg:'):
        s = open(os.path.join(OUT, key[4:] + '.svg'), encoding='utf-8').read()
        return re.sub(r'<svg ', '<svg style="width:100%;height:auto" ', s, count=1)
    if key.startswith('ic:'):
        return ic(key[3:])
    if key.startswith('mock:'):
        return put(os.path.join(OUT, 'mock', key[5:] + '.webp'), 'mock-' + key[5:] + '.webp')
    if key.startswith('scr:'):
        return put(os.path.join(OUT, 'screens', key[4:] + '.webp'), 'scr-' + key[4:] + '.webp')
    if key.startswith('iconrow:'):
        return iconrow(int(key[8:]))
    return put(os.path.join(OUT, key + '.webp'), key + '.webp')

html = re.sub(r'\{\{([^}]+)\}\}', rep, t)
dst = os.path.join(D, 'obzhora-case.html')
open(dst, 'w', encoding='utf-8').write(html)
n = len(os.listdir(IMG)); size = sum(os.path.getsize(os.path.join(IMG, f)) for f in os.listdir(IMG))
print(dst, len(html) // 1024, 'KB;', n, 'images', size // 1024, 'KB')

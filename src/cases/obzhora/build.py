import base64, re, os, glob, sys
D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, 'out')
t = open(os.path.join(D, 'obzhora-template.html'), encoding='utf-8').read()

def uri(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()

icons = sorted(glob.glob(os.path.join(OUT, 'icons', '*.png')))
icon_uri = {os.path.basename(p)[:-4]: uri(p, 'image/png') for p in icons}

def iconrow(i):
    names = list(icon_uri)[i::3]
    return ''.join(f'<img src="{icon_uri[n]}" alt="">' for n in names)

def rep(m):
    key = m.group(1)
    if key.startswith('svg:'):
        s = open(os.path.join(OUT, key[4:] + '.svg'), encoding='utf-8').read()
        return re.sub(r'<svg ', '<svg style="width:100%;height:auto" ', s, count=1)
    if key.startswith('ic:'):
        return icon_uri[key[3:]]
    if key.startswith('mock:'):
        return uri(os.path.join(OUT, 'mock', key[5:] + '.webp'), 'image/webp')
    if key.startswith('scr:'):
        return uri(os.path.join(OUT, 'screens', key[4:] + '.webp'), 'image/webp')
    if key.startswith('iconrow:'):
        return iconrow(int(key[8:]))
    return uri(os.path.join(OUT, key + '.webp'), 'image/webp')

html = re.sub(r'\{\{([^}]+)\}\}', rep, t)
dst = os.path.join(D, 'obzhora-case.html')
open(dst, 'w', encoding='utf-8').write(html)
print(dst, len(html) // 1024, 'KB')

# Composite screen PNGs (750x1624, iPhone X @2x) into the iPhone 11 mockup template.
# usage: python3 mock.py <screens_dir> <suffix>   e.g.  mock.py out/screens_dark _d
# writes out/mock/<name><suffix>.webp (545x991). Needs Pillow.
import sys, os, glob
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); M = os.path.join(D, 'out', 'mock')
tpl = Image.open(os.path.join(M, '_tpl.png')); mask = Image.open(os.path.join(M, '_mask.png'))
src, suffix = sys.argv[1], sys.argv[2]
for f in sorted(glob.glob(os.path.join(src, '*.*'))):
    n = os.path.splitext(os.path.basename(f))[0]
    c = tpl.copy(); c.paste(Image.open(f).convert('RGBA'), (205, 93), mask)  # screen offset inside the template
    c.resize((545, 991), Image.LANCZOS).save(os.path.join(M, n + suffix + '.webp'), 'WEBP', quality=86, method=6)
    print(n + suffix)

# -*- coding: utf-8 -*-
# Link previews for the stage: each production card in assets/og/ with a red TEST stamp → tools/og-stage*.jpg
#   og-home.jpg  → og-stage.jpg        (the big stamp, top right — every page without its own card)
#   og-<case>.jpg → og-stage-<case>.jpg (a smaller stamp, top left, clear of the case's hero picture)
# Rendered by headless Chrome (fonts embedded as data URIs). Used only by tools/stage-deploy.sh, never on production
import os, base64, subprocess, tempfile, glob
from PIL import Image
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F=os.path.join(R,'assets','fonts')
b64=lambda p: base64.b64encode(open(p,'rb').read()).decode()
font=f"@font-face{{font-family:'Unbounded';font-weight:200 900;src:url(data:font/woff2;base64,{b64(os.path.join(F,'unbounded-latin-27.woff2'))}) format('woff2')}}"
BIG="right:56px;top:48px;padding:18px 34px 22px;border-radius:22px;font-size:120px"
SMALL="left:44px;top:30px;padding:10px 20px 13px;border-radius:14px;font-size:60px"

def card(src, dst, stamp):
    bg='data:image/jpeg;base64,'+b64(src)
    html=f'''<!doctype html><html><head><meta charset="utf-8"><style>{font}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#0A0A0A}}
.bg{{position:absolute;inset:0;background:url({bg}) center/cover}}
.stamp{{position:absolute;{stamp};background:#E5484D;color:#fff;font-family:'Unbounded';font-weight:800;line-height:1;letter-spacing:-.04em;transform:rotate(-4deg);box-shadow:0 18px 60px rgba(0,0,0,.45)}}
</style></head><body><div class="bg"></div><div class="stamp">TEST</div></body></html>'''
    tmp=tempfile.mkdtemp(); h=os.path.join(tmp,'og.html'); open(h,'w',encoding='utf-8').write(html)
    png=os.path.join(tmp,'og.png')
    subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1',
                    f'--screenshot={png}','--window-size=1200,630','--virtual-time-budget=3000','file://'+h],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    Image.open(png).convert('RGB').save(dst,quality=88,optimize=True); print(os.path.relpath(dst,R))

card(os.path.join(R,'assets','og','og-home.jpg'), os.path.join(R,'tools','og-stage.jpg'), BIG)
for p in sorted(glob.glob(os.path.join(R,'assets','og','og-*.jpg'))):
    name=os.path.basename(p)[3:-4]
    if name!='home': card(p, os.path.join(R,'tools',f'og-stage-{name}.jpg'), SMALL)

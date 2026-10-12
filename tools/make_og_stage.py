# -*- coding: utf-8 -*-
# Link preview for the stage: the production card (assets/og/og-home.jpg) with a big red TEST stamp → tools/og-stage.jpg
# Rendered by headless Chrome (fonts embedded as data URIs). Used only by tools/stage-deploy.sh, never on production
import os, base64, subprocess, tempfile, sys
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F=os.path.join(R,'assets','fonts')
b64=lambda p: base64.b64encode(open(p,'rb').read()).decode()
bg='data:image/jpeg;base64,'+b64(os.path.join(R,'assets','og','og-home.jpg'))
font=f"@font-face{{font-family:'Unbounded';font-weight:200 900;src:url(data:font/woff2;base64,{b64(os.path.join(F,'unbounded-latin-27.woff2'))}) format('woff2')}}"
html=f'''<!doctype html><html><head><meta charset="utf-8"><style>{font}
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#0A0A0A}}
.bg{{position:absolute;inset:0;background:url({bg}) center/cover}}
.stamp{{position:absolute;right:56px;top:48px;padding:18px 34px 22px;border-radius:22px;background:#E5484D;color:#fff;font:800 120px/1 'Unbounded';letter-spacing:-.04em;transform:rotate(-4deg);box-shadow:0 18px 60px rgba(0,0,0,.45)}}
</style></head><body><div class="bg"></div><div class="stamp">TEST</div></body></html>'''
tmp=tempfile.mkdtemp(); h=os.path.join(tmp,'og.html'); open(h,'w',encoding='utf-8').write(html)
png=os.path.join(tmp,'og.png')
subprocess.run(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1',
                f'--screenshot={png}','--window-size=1200,630','--virtual-time-budget=3000','file://'+h],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
from PIL import Image
Image.open(png).convert('RGB').save(os.path.join(R,'tools','og-stage.jpg'),quality=88,optimize=True)
print('tools/og-stage.jpg')

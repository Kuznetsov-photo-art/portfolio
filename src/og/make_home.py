# -*- coding: utf-8 -*-
# Build og-home.html (1200x630) with fonts and the portrait embedded as data URIs, so headless Chrome can render it from file://
import os, base64
R=os.path.expanduser('~/Desktop/portfolio'); F=os.path.join(R,'assets','fonts')
O=os.path.dirname(os.path.abspath(__file__))
b64=lambda p: base64.b64encode(open(p,'rb').read()).decode()
def ff(fam, files, w):
    return '\n'.join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(os.path.join(F,f))}) format('woff2')}}" for f in files)
fonts='\n'.join([ff('Unbounded',['unbounded-cyrillic-25.woff2','unbounded-latin-27.woff2'],'200 900'),
                 ff('Golos Text',['golos-text-cyrillic-1.woff2','golos-text-latin-3.woff2'],'400 600'),
                 ff('JetBrains Mono',['jetbrains-mono-latin-7.woff2'],'400 500')])
img='data:image/webp;base64,'+b64(os.path.join(R,'assets','about','portrait.webp'))
html=f'''<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}
html,body{{margin:0;width:1200px;height:630px;background:#0A0A0A;color:#F2F2F2;overflow:hidden}}
.wrap{{position:relative;width:1200px;height:630px}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(242,242,242,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(242,242,242,.045) 1px,transparent 1px);background-size:60px 60px}}
.t{{position:absolute;left:72px;top:64px;font:400 15px/1 'JetBrains Mono';letter-spacing:.16em;text-transform:uppercase;color:#6B6B6B}}
h1{{position:absolute;left:68px;top:150px;margin:0;font:300 92px/.98 'Unbounded';letter-spacing:-.055em}}
h1 b{{font-weight:800}}
.r{{position:absolute;left:72px;top:372px;font:400 27px/1.35 'Golos Text';color:#A3A3A3;width:600px}}
.u{{position:absolute;left:72px;bottom:60px;font:500 17px/1 'JetBrains Mono';letter-spacing:.14em;text-transform:uppercase;color:#F2F2F2}}
.u i{{display:inline-block;width:10px;height:10px;border-radius:50%;background:#F2F2F2;margin-right:14px;vertical-align:1px}}
canvas{{position:absolute;right:20px;top:50%;transform:translateY(-50%);width:560px;height:560px}}
</style></head><body><div class="wrap"><div class="grid"></div>
<div class="t">Portfolio · 2012–2026</div>
<h1>Андрей<br><b>Кузнецов</b></h1>
<div class="r">Lead Product Designer<br>AI &amp; Design Systems</div>
<div class="u"><i></i>andrewkuznetsov.com</div>
<canvas id="c" width="1120" height="1120"></canvas></div>
<script>
/* same halftone as the About block: ~96 dots across, soft dissolving rim with a sparse scatter */
const im=new Image(); im.onload=()=>{{
  const c=document.getElementById('c'), x=c.getContext('2d'), W=c.width, H=c.height, S=W/96, cols=Math.floor(W/S), rows=Math.floor(H/S);
  const o=document.createElement('canvas'); o.width=cols; o.height=rows; const ox=o.getContext('2d');
  const dh=rows*.94, dw=dh*im.naturalWidth/im.naturalHeight; ox.drawImage(im,(cols-dw)/2,rows-dh,dw,dh);
  const d=ox.getImageData(0,0,cols,rows).data; let seed=7; const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
  x.fillStyle='#F2F2F2'; x.beginPath(); const sp=new Path2D();
  for(let j=0;j<rows;j++)for(let i=0;i<cols;i++){{ const l=d[(j*cols+i)*4]/255, a=d[(j*cols+i)*4+3]; const hx=i*S+S/2, hy=j*S+S/2;
    const cx=hx-W/2, cy=hy-H/2, rr=Math.sqrt(cx*cx+cy*cy)/(W/2), R0=.72; if(rr>1) continue;
    const t=rr<R0?0:(rr-R0)/(1-R0), k=1-t;
    if(a<128){{ if(rr<R0*.85||rnd()>.32*(1-t)) continue; const v=.42*(1-t)+.06, r=S*.7*.52*Math.pow(v,.85); if(r<.35) continue; sp.moveTo(hx+r,hy); sp.arc(hx,hy,r,0,6.283); continue; }}
    if(t>0&&rnd()<t*.85) continue; const r=S*(.45+.55*k)*.52*Math.pow(l,.85); if(r<.35) continue; x.moveTo(hx+r,hy); x.arc(hx,hy,r,0,6.283); }}
  x.fill(); x.globalAlpha=.55; x.fill(sp); document.title='ready';
}}; im.src='{img}';
</script></body></html>'''
open(os.path.join(O,'og-home.html'),'w',encoding='utf-8').write(html); print('ok')

# -*- coding: utf-8 -*-
# Records the live site's first-visit intro (preloader → HERO2 reel → hero) on the desktop layout, frame by frame, with a virtual clock
# (performance.now / requestAnimationFrame / setTimeout / requestIdleCallback are replaced, so every frame is exact) → cap/intro/NNNN.jpg (956×598)
import json, subprocess, time, urllib.request, tempfile, base64, os, io, sys
import websocket
from PIL import Image
LANG=os.environ.get('LANG_SITE','en'); FPS=30; DUR=float(os.environ.get('DUR','17'))
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cap','intro'+('' if LANG=='en' else '_'+LANG)); os.makedirs(OUT,exist_ok=True)
CLOCK=r"""
(()=>{ let VT=0, id=0; const rafs=[], tms=[];
  performance.now=()=>VT; Date.now=(n=>()=>n+VT)(Date.now());
  window.requestAnimationFrame=cb=>{ rafs.push([++id,cb]); return id; };
  window.cancelAnimationFrame=i=>{ const k=rafs.findIndex(r=>r[0]===i); if(k>=0) rafs.splice(k,1); };
  window.setTimeout=(cb,ms=0,...a)=>{ tms.push([++id,VT+(+ms||0),()=>cb(...a)]); return id; };
  window.clearTimeout=i=>{ const k=tms.findIndex(r=>r[0]===i); if(k>=0) tms.splice(k,1); };
  window.requestIdleCallback=(cb)=>window.setTimeout(()=>cb({timeRemaining:()=>50,didTimeout:false}),1);
  window.__step=dt=>{ const end=VT+dt;
    for(;;){ tms.sort((a,b)=>a[1]-b[1]); if(!tms.length||tms[0][1]>end) break; const t=tms.shift(); VT=Math.max(VT,t[1]); try{t[2]();}catch(e){} }
    VT=end; const c=rafs.splice(0); c.forEach(([,f])=>{ try{f(VT);}catch(e){} }); };
  window.__vt=()=>VT;
})();"""
p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9377','--remote-allow-origins=http://127.0.0.1:9377',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9377/json')); break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9377'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True).get('result',{}).get('value')
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=1,mobile=False)
    cmd('Page.addScriptToEvaluateOnNewDocument',source=f"localStorage.setItem('lang','{LANG}');localStorage.setItem('theme','');"+CLOCK)
    cmd('Page.navigate',url='https://andrewkuznetsov.com/'); time.sleep(4)          # fonts, images
    # hide the preloader curtain and the custom cursor; the preloader still runs (it starts the reel)
    js("(()=>{const s=document.createElement('style');s.textContent='.pre{display:none!important}.cur{display:none!important}';document.head.append(s);})()")
    # run the preloader on the virtual clock until the reel starts
    for _ in range(400):
        js('__step(1000/30)')
        if js("document.body.classList.contains('reeling')"): break
    print('reel started at vt', js('__vt()'))
    for i in range(int(DUR*FPS)):
        js('__step(1000/30)'); time.sleep(.01)
        d=cmd('Page.captureScreenshot',format='jpeg',quality=88)['data']
        Image.open(io.BytesIO(base64.b64decode(d))).convert('RGB').resize((956,598),Image.LANCZOS).save(os.path.join(OUT,f'{i:04d}.jpg'),quality=86)
        if i%60==0: print(i,end=' ',flush=True)
    print('\nframes:',len(os.listdir(OUT)))
finally: p.terminate()

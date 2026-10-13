# -*- coding: utf-8 -*-
# The header theme toggle rolling from the moon to the sun — the theme itself does not change. Same clip as m_ctrls (header .ctrls, pad 12, DSF 3),
# transparent → cap/ctrls_roll[_en]/NNNN.png. The knob travels 22 px and turns like a wheel (22/10 rad), the moon hands over to the sun on the way.
import json, subprocess, time, urllib.request, tempfile, base64, os, math
import websocket
LANG=os.environ.get('LANG_SITE','en'); SUF='_en' if LANG=='en' else ''; DSF=3; N=15
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'cap','ctrls_roll'+SUF); os.makedirs(OUT,exist_ok=True)
HIDE=".row .th{visibility:hidden!important}html,body{background:transparent!important}.grain,.cur,.totop,.navfx,#ink,.gridlines,#fgrid,.reel,.pre,.toast{display:none!important}*{transition:none!important}header.nav{position:absolute!important}"
def ease(x): x=min(1,max(0,x)); return x*x*(3-2*x)
p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9381','--remote-allow-origins=http://127.0.0.1:9381',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9381/json')); break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9381'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True).get('result',{}).get('value')
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=DSF,mobile=False)
    cmd('Page.addScriptToEvaluateOnNewDocument',source=f"sessionStorage.setItem('pre','1');localStorage.setItem('lang','{LANG}');localStorage.setItem('theme','')")
    cmd('Page.navigate',url='https://andrewkuznetsov.com/'); time.sleep(5)
    js(f"(()=>{{const s=document.createElement('style');s.textContent={json.dumps(HIDE)};document.head.append(s);scrollTo(0,0);}})()")
    cmd('Emulation.setDefaultBackgroundColorOverride',color={'r':0,'g':0,'b':0,'a':0}); time.sleep(.5)
    x,y,w,h=json.loads(js("JSON.stringify((()=>{const b=document.querySelector('header.nav .ctrls').getBoundingClientRect();return [b.left,b.top,b.width,b.height]})())"))
    pad=12; clip={'x':x-pad,'y':y-pad,'width':w+2*pad,'height':h+2*pad,'scale':1}
    for f in range(N):
        k=ease((f-2)/10)                                          # rests on the moon for 2 frames, rolls over ~0.35 s, rests on the sun
        ang=math.degrees(22/10)*k
        js(f"""(()=>{{const k=document.querySelector('#theme .k'), m=k.querySelector('.moon'), s=k.querySelector('.sun'), p={k:.4f};
          k.style.transform='translateX('+(22*p)+'px) rotate({ang:.2f}deg)';
          m.style.opacity=Math.max(0,1-p*1.6); m.style.transform='scale('+(1-.4*p)+')';
          s.style.opacity=Math.max(0,(p-.35)/.65); s.style.transform='rotate('+(-90*(1-p))+'deg) scale('+(.6+.4*p)+')';}})()""")
        time.sleep(.05)
        d=cmd('Page.captureScreenshot',format='png',clip=clip)['data']; open(os.path.join(OUT,f'{f:04d}.png'),'wb').write(base64.b64decode(d))
    print('toggle frames',N,'clip',[round(v,1) for v in (clip['width'],clip['height'])])
finally: p.terminate()

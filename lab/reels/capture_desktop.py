# -*- coding: utf-8 -*-
# Desktop site (1440×900) as viewport shots for the laptop screen in REEL2: header once, then section shots without it → cap/d_*.png
import json, subprocess, time, urllib.request, tempfile, base64, os
import websocket, sys
TH=sys.argv[1] if len(sys.argv)>1 else ''   # '' dark (site default) | 'light'
SUF='_light' if TH=='light' else ''
LANG=os.environ.get('LANG_SITE','ru'); SUF+='' if LANG=='ru' else '_'+LANG
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cap')
SHOTS=[('hero',None,0),('focus','#focus',260),('work','#work',-40),('archive','#archive',-40),('about','#about',-40),('tl','#tl',-90),('contact','#contact',-120)]
p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9375','--remote-allow-origins=http://127.0.0.1:9375',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9375/json')); break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9375'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True,awaitPromise=True).get('result',{}).get('value')
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=1,mobile=False)
    cmd('Page.addScriptToEvaluateOnNewDocument',source="sessionStorage.setItem('pre','1');localStorage.setItem('lang','"+LANG+"');localStorage.setItem('theme','"+TH+"')")
    cmd('Page.navigate',url='https://andrewkuznetsov.com/'); time.sleep(5)
    js("(async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,80));}scrollTo(0,0);})()"); time.sleep(1.5)
    js("(()=>{const s=document.createElement('style');s.textContent='.row .th{visibility:hidden!important}.grain,.cur,.totop,#ink,.reel,.pre,.toast{display:none!important}.rv,.rv-wait,.tl-wait{opacity:1!important;transform:none!important}html{scroll-behavior:auto!important}';document.head.append(s);})()")
    open(os.path.join(OUT,f'd_header{SUF}.png'),'wb').write(base64.b64decode(cmd('Page.captureScreenshot',format='png',clip={'x':0,'y':0,'width':1440,'height':62,'scale':1})['data']))
    js("(()=>{const s=document.createElement('style');s.textContent='header.nav,.navfx{visibility:hidden!important}';document.head.append(s);})()")
    for sid,sel,off in SHOTS:
        y=0 if not sel else js(f"Math.round(document.querySelector({json.dumps(sel)}).getBoundingClientRect().top+scrollY+({off}))")
        js(f"scrollTo(0,{y})"); time.sleep(2.4 if sid in ('about','focus') else 1.0)
        d=cmd('Page.captureScreenshot',format='jpeg',quality=92)['data']; open(os.path.join(OUT,f'd_{sid}{SUF}.jpg'),'wb').write(base64.b64decode(d)); print(sid,y)
finally: p.terminate()

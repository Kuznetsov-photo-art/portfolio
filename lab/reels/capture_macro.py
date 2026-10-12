# -*- coding: utf-8 -*-
# High-resolution details of the desktop hero/about/contacts (1440 css, ×3) for REEL2 macro shots → cap/m_<id>.png (transparent, dark theme)
import json, subprocess, time, urllib.request, tempfile, base64, os
import websocket
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cap'); os.makedirs(OUT,exist_ok=True)
DSF=3
ITEMS=[('name','#hname',40),('spec','.hero .spec',10),('ctrls','header.nav .ctrls',12),('tag','.h-sub p',8),('portrait','#about .portrait',0),('mail','#contact .c-mail',0),('meta','.h-meta',8)]
HIDE=".row .th{visibility:hidden!important}html,body{background:transparent!important}.grain,.cur,.totop,.navfx,#ink,.gridlines,#fgrid,.reel,.pre,.toast{display:none!important}.rv,.rv-wait,.tl-wait{opacity:1!important;transform:none!important;filter:none!important}*{transition:none!important}header.nav{position:absolute!important}"
p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9374','--remote-allow-origins=http://127.0.0.1:9374',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9374/json')); break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9374'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True,awaitPromise=True).get('result',{}).get('value')
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=DSF,mobile=False)
    cmd('Page.addScriptToEvaluateOnNewDocument',source="sessionStorage.setItem('pre','1');localStorage.setItem('lang','ru');localStorage.setItem('theme','')")
    cmd('Page.navigate',url='https://andrewkuznetsov.com/'); time.sleep(5)
    js("(async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=400){scrollTo(0,y);await new Promise(r=>setTimeout(r,80));}scrollTo(0,0);})()"); time.sleep(1)
    js(f"(()=>{{const s=document.createElement('style');s.textContent={json.dumps(HIDE)};document.head.append(s);}})()")
    cmd('Emulation.setDefaultBackgroundColorOverride',color={'r':0,'g':0,'b':0,'a':0})
    man={}
    for pid,sel,pad in ITEMS:
        js(f"document.querySelector({json.dumps(sel)}).scrollIntoView({{block:'center'}})"); time.sleep(2.6 if pid=='portrait' else .5)
        x,y,w,h,sy=json.loads(js(f"JSON.stringify((()=>{{const b=document.querySelector({json.dumps(sel)}).getBoundingClientRect();return [b.left,b.top,b.width,b.height,scrollY]}})())"))
        x-=pad; y-=pad; w+=2*pad; h+=2*pad
        d=cmd('Page.captureScreenshot',format='png',clip={'x':x,'y':y+sy,'width':w,'height':h,'scale':1},captureBeyondViewport=True)['data']
        open(os.path.join(OUT,f'm_{pid}.png'),'wb').write(base64.b64decode(d)); man[pid]={'w':w,'h':h}
    json.dump(man,open(os.path.join(OUT,'macro.json'),'w'),indent=1); print(man)
finally: p.terminate()

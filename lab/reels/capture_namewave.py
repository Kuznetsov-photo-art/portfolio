# -*- coding: utf-8 -*-
# The site's «rubber» weight wave on the desktop name (letters swell 300 → 850 one after another and settle back), frame by frame,
# cropped to the name block → cap/namewave[_en]/NNNN.jpg + crop.json (css rect at 1440×900). The weights are set directly per frame (no CSS transition),
# so every frame is exact. Timing: stagger 30 ms, rise 250 ms, hold 80 ms, fall 300 ms, the site's cubic-bezier(.2,.8,.2,1)
import json, subprocess, time, urllib.request, tempfile, base64, os, io
import websocket
LANG=os.environ.get('LANG_SITE','en'); FPS=30; DSF=1.5
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cap','namewave'+('_en' if LANG=='en' else '')); os.makedirs(OUT,exist_ok=True)
STG,RISE,HOLD,FALL,PEAK=.03,.25,.08,.30,850
def bez(x,p1=.2,p2=.8,p3=.2,p4=1):
    lo,hi=0.,1.
    for _ in range(40):
        m=(lo+hi)/2; bx=3*m*(1-m)**2*p1+3*m*m*(1-m)*p3+m**3
        if bx<x: lo=m
        else: hi=m
    m=(lo+hi)/2; return 3*m*(1-m)**2*p2+3*m*m*(1-m)*p4+m**3
def weight(i,tau):
    a=tau-i*STG
    if a<=0: return 300
    if a<RISE: return 300+(PEAK-300)*bez(a/RISE)
    if a<RISE+HOLD: return PEAK
    if a<RISE+HOLD+FALL: return PEAK-(PEAK-300)*bez((a-RISE-HOLD)/FALL)
    return 300
p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9378','--remote-allow-origins=http://127.0.0.1:9378',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9378/json')); break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9378'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True).get('result',{}).get('value')
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=DSF,mobile=False)
    cmd('Page.addScriptToEvaluateOnNewDocument',source=f"sessionStorage.setItem('pre','1');localStorage.setItem('lang','{LANG}');localStorage.setItem('theme','')")
    cmd('Page.navigate',url='https://andrewkuznetsov.com/'); time.sleep(6)       # the site's own intro wave has finished by now
    js("(()=>{const s=document.createElement('style');s.textContent='.grain,.cur,.totop,#ink,.reel,.pre,.toast{display:none!important}header.nav,.navfx{visibility:hidden!important}#hname .ch{transition:none!important}';document.head.append(s);scrollTo(0,0);})()")
    time.sleep(.5)
    r=json.loads(js("JSON.stringify((()=>{const b=document.getElementById('hname').getBoundingClientRect();return [b.left,b.top,b.width,b.height]})())"))
    x,y,w,h=r; x0,y0=x-40,y-36; W0,H0=w+60,h+70           # room for the redlines and the wider bold letters
    nch=js("document.querySelectorAll('#hname .ch').length"); total=(nch-1)*STG+RISE+HOLD+FALL; N=int(total*FPS)+2
    for f in range(N):
        tau=f/FPS; ws_=[round(weight(i,tau)) for i in range(nch)]
        js(f"(()=>{{const w={ws_};document.querySelectorAll('#hname .ch').forEach((c,i)=>c.style.setProperty('--w',w[i]));}})()"); time.sleep(.04)
        d=cmd('Page.captureScreenshot',format='jpeg',quality=92,clip={'x':x0,'y':y0,'width':W0,'height':H0,'scale':1})['data']
        open(os.path.join(OUT,f'{f:04d}.jpg'),'wb').write(base64.b64decode(d))
    json.dump({'x':x0,'y':y0,'w':W0,'h':H0,'frames':N,'fps':FPS},open(os.path.join(OUT,'crop.json'),'w'))
    print('chars',nch,'frames',N,'crop',[round(v) for v in (x0,y0,W0,H0)])
finally: p.terminate()

# -*- coding: utf-8 -*-
# Desktop sections for REEL2 (replacing the macro shots): frame sequences with the site's own motion, on a virtual clock
#   cases   — rows get the hover state one after another (title 300→600, letter-spacing, 12 px shift)
#   archive — tile rows drift in opposite directions; one tile is «pressed» and turns to colour (the site's hover)
#   about   — the halftone portrait assembles, lead words light up one by one
# → cap/sec_<name>[_en]/NNNN.jpg + meta.json (clip rect in css px, row/word anchors). DSF 2, 30 fps.
import json, subprocess, time, urllib.request, tempfile, base64, os
import websocket
LANG=os.environ.get('LANG_SITE','en'); SUF='_en' if LANG=='en' else ''; FPS=30; DSF=2
HERE=os.path.dirname(os.path.abspath(__file__))
CLOCK=open(os.path.join(HERE,'capture_intro.py'),encoding='utf-8').read().split('CLOCK=r"""')[1].split('"""')[0]
CSS=(".grain,.cur,.totop,#ink,.reel,.pre,.toast{display:none!important}header.nav,.navfx{visibility:hidden!important}"
     ".rv,.rv-wait,.tl-wait{opacity:1!important;transform:none!important;filter:none!important}"
     ".row,.row h3,.a-in,.a-item img,.a-item .cap,.about .lead .wd{transition:none!important}.row .th{visibility:hidden!important}html{scroll-behavior:auto!important}")
def bez(x,p1=.2,p2=.8,p3=.2,p4=1):
    x=min(1,max(0,x)); lo,hi=0.,1.
    for _ in range(40):
        m=(lo+hi)/2; bx=3*m*(1-m)**2*p1+3*m*m*(1-m)*p3+m**3
        if bx<x: lo=m
        else: hi=m
    m=(lo+hi)/2; return 3*m*(1-m)**2*p2+3*m*m*(1-m)*p4+m**3
p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9379','--remote-allow-origins=http://127.0.0.1:9379',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9379/json')); break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9379'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True).get('result',{}).get('value')
    def shot(path,clip):
        sy=js('scrollY')                                   # clip is in viewport coords; the screenshot clip is in page coords
        d=cmd('Page.captureScreenshot',format='jpeg',quality=90,clip={**clip,'y':clip['y']+sy,'scale':1})['data']; open(path,'wb').write(base64.b64decode(d))
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=DSF,mobile=False)
    cmd('Page.addScriptToEvaluateOnNewDocument',source=f"sessionStorage.setItem('pre','1');localStorage.setItem('lang','{LANG}');localStorage.setItem('theme','');"+CLOCK)
    cmd('Page.navigate',url='https://andrewkuznetsov.com/'); time.sleep(5)
    js(f"(()=>{{const s=document.createElement('style');s.textContent={json.dumps(CSS)};document.head.append(s);}})()")
    for _ in range(10): js('__step(1000/30)')          # let the first layout jobs (line locking, archive setup) run
    def outdir(name):
        d=os.path.join(HERE,'cap',f'sec_{name}{SUF}'); os.makedirs(d,exist_ok=True)
        for f in os.listdir(d): os.remove(os.path.join(d,f))
        return d
    # ---------- cases
    js("scrollTo(0,document.getElementById('work').getBoundingClientRect().top+scrollY-40)"); time.sleep(.6)
    R=json.loads(js("""JSON.stringify((()=>{const rows=[...document.querySelectorAll('#cases .row')].slice(0,4).map(r=>{const b=r.getBoundingClientRect(),h=r.querySelector('h3').getBoundingClientRect();return [b.top,b.bottom,h.top,h.bottom,h.left,h.right];});
      const s=document.querySelector('#work .sec-head').getBoundingClientRect(); return {rows,head:[s.top,s.bottom]};})())"""))
    cy0=R['head'][0]-24; cy1=R['rows'][3][1]+8; clip={'x':24,'y':cy0,'width':1392,'height':cy1-cy0}
    d=outdir('cases'); DUR=1.55; N=int(DUR*FPS)+1; ST=[.12+i*.4 for i in range(4)]
    def hov(i,tau):
        a=tau-ST[i]; up=bez(a/.4) if a>0 else 0
        if i<3: dn=bez((tau-ST[i+1]-.05)/.45) if tau>ST[i+1]+.05 else 0
        else: dn=0
        return up*(1-dn)
    for f in range(N):
        tau=f/FPS; hs=[round(hov(i,tau),4) for i in range(4)]
        js(f"""(()=>{{const h={hs};[...document.querySelectorAll('#cases .row')].slice(0,4).forEach((r,i)=>{{r.style.paddingLeft=(12*h[i])+'px';const t=r.querySelector('h3');t.style.fontVariationSettings="'wght' "+(300+300*h[i]);t.style.letterSpacing=(-.035+.015*h[i])+'em';}});}})()""")
        shot(os.path.join(d,f'{f:04d}.jpg'),clip)
    json.dump({'clip':clip,'rows':[[r[2]-cy0,r[3]-cy0,r[4]-24,r[5]-24] for r in R['rows']],'starts':ST,'frames':N,'fps':FPS},open(os.path.join(d,'meta.json'),'w'))
    js("[...document.querySelectorAll('#cases .row')].forEach(r=>{r.style.paddingLeft='';const t=r.querySelector('h3');t.style.fontVariationSettings='';t.style.letterSpacing='';})")
    print('cases',N,clip)
    # ---------- archive
    js("scrollTo(0,document.getElementById('arch').getBoundingClientRect().top+scrollY-70)"); time.sleep(.6)
    A=json.loads(js("JSON.stringify([...document.querySelectorAll('#arch .arow')].slice(0,3).map(r=>{const b=r.getBoundingClientRect();return [b.top,b.bottom];}))"))
    clip={'x':0,'y':A[0][0]-14,'width':1440,'height':A[2][1]-A[0][0]+28}
    x0=json.loads(js("JSON.stringify(archRows.map(r=>r.x))"))
    d=outdir('archive'); DUR=1.3; N=int(DUR*FPS)+1; SP=150
    def place(tau):
        js(f"""archRows.forEach((r,i)=>{{const half=r.tr.scrollWidth/2; let x={json.dumps(x0)}[i]+r.dir*{SP}*{tau}; while(x<=-half) x+=half; while(x>0) x-=half; r.tr.style.transform='translate3d('+x+'px,0,0)';}})""")
    place(.6)
    tile=js(f"(()=>{{const y=({A[1][0]}+{A[1][1]})/2; const e=document.elementFromPoint(760,y); const a=e&&e.closest('.a-item'); if(!a) return null; a.dataset.press='1'; return true;}})()")
    for f in range(N):
        tau=f/FPS; place(tau); h=bez((tau-.3)/.45) if tau>.3 else 0
        js(f"""(()=>{{const a=document.querySelector('.a-item[data-press]'); if(!a) return; const h={h:.4f}; const i=a.querySelector('.a-in'), im=a.querySelector('img'), c=a.querySelector('.cap');
          i.style.clipPath='inset('+(7*h)+'px round '+(4+3*h)+'px)'; im.style.filter='grayscale('+(1-h)+') contrast(1.05)'; im.style.transform='scale('+(1+.035*h)+')'; if(c) c.style.opacity=h;}})()""")
        shot(os.path.join(d,f'{f:04d}.jpg'),clip)
    json.dump({'clip':clip,'rows':[[r[0]-clip['y'],r[1]-clip['y']] for r in A],'frames':N,'fps':FPS,'pressed':bool(tile)},open(os.path.join(d,'meta.json'),'w'))
    print('archive',N,clip,'pressed',tile)
    # ---------- about
    js("scrollTo(0,document.querySelector('#about .portrait').getBoundingClientRect().top+scrollY-120)"); time.sleep(.8)
    for _ in range(14): js('__step(1000/30)')           # the portrait starts assembling (IntersectionObserver fired on scroll)
    B=json.loads(js("""JSON.stringify((()=>{const p=document.querySelector('#about .portrait').getBoundingClientRect(),l=document.querySelector('#about .lead').getBoundingClientRect(),a=document.querySelector('#about .about').getBoundingClientRect();
      return {p:[p.left,p.top,p.right,p.bottom],l:[l.left,l.top,l.right,l.bottom],a:[a.left,a.right]};})())"""))
    top=min(B['p'][1],B['l'][1])-20; bot=max(B['p'][3],B['l'][3])+20; clip={'x':B['a'][0]-20,'y':top,'width':B['a'][1]-B['a'][0]+40,'height':bot-top}
    nw=js("document.querySelectorAll('#about .lead .wd').length")
    d=outdir('about'); DUR=1.3; N=int(DUR*FPS)+1
    for f in range(N):
        tau=f/FPS; k=round(min(1,max(0,(tau-.05)/1.0))*nw)
        js(f"document.querySelectorAll('#about .lead .wd').forEach((w,i)=>w.classList.toggle('on',i<{k}))")
        if f: js('__step(1000/30)')
        shot(os.path.join(d,f'{f:04d}.jpg'),clip)
    json.dump({'clip':clip,'portrait':[B['p'][0]-clip['x'],B['p'][1]-top,B['p'][2]-clip['x'],B['p'][3]-top],'lead':[B['l'][0]-clip['x'],B['l'][1]-top,B['l'][2]-clip['x'],B['l'][3]-top],'frames':N,'fps':FPS},open(os.path.join(d,'meta.json'),'w'))
    print('about',N,clip,'words',nw)
finally: p.terminate()

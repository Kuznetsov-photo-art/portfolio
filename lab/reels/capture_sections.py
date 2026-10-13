# -*- coding: utf-8 -*-
# Desktop sections for REEL2 (the camera passes between the reveal and the tagline): frame sequences with the site's own motion
#   cases   — all six rows plus what is above the heading (the interface continues beyond the frame); rows 1–4 get the hover state
#             one after another (title 300→600, letter-spacing, 12 px shift)
#   archive — four tile rows drifting in opposite directions, all black-and-white; Techmas kept out of the clip; DSF 3 for the close-up
#   about   — the halftone portrait assembles, lead words light up one by one
# → cap/sec_<name>[_en]/NNNN.jpg + meta.json (clip rect in css px, anchors). Usage: ONLY=cases,archive python capture_sections.py
import json, subprocess, time, urllib.request, tempfile, base64, os
import websocket
ONLY=set(filter(None,os.environ.get('ONLY','cases,archive,about').split(',')))
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
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=180,origin='http://127.0.0.1:9379'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True).get('result',{}).get('value')
    def shot(path,clip,dsf=DSF):           # clip in viewport css px; the screenshot clip is in page coords
        sy=js('scrollY')
        d=cmd('Page.captureScreenshot',format='jpeg',quality=90,captureBeyondViewport=True,clip={**clip,'y':clip['y']+sy,'scale':dsf/DSF})['data']
        open(path,'wb').write(base64.b64decode(d))
    def outdir(name):
        d=os.path.join(HERE,'cap',f'sec_{name}{SUF}'); os.makedirs(d,exist_ok=True)
        for f in os.listdir(d): os.remove(os.path.join(d,f))
        return d
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1440,height=900,deviceScaleFactor=DSF,mobile=False)
    cmd('Page.addScriptToEvaluateOnNewDocument',source=f"sessionStorage.setItem('pre','1');localStorage.setItem('lang','{LANG}');localStorage.setItem('theme','');"+CLOCK)
    cmd('Page.navigate',url='https://andrewkuznetsov.com/'); time.sleep(5)
    js(f"(()=>{{const s=document.createElement('style');s.textContent={json.dumps(CSS)};document.head.append(s);}})()")
    for _ in range(10): js('__step(1000/30)')          # first layout jobs (line locking, archive setup)
    # every archive cover loaded and decoded (lazy images outside the viewport stayed black)
    js("document.querySelectorAll('img').forEach(i=>{i.loading='eager';i.decoding='sync';})")
    for _ in range(80):
        if js("[...document.querySelectorAll('#arch img,#about img')].every(i=>i.complete&&i.naturalWidth)"): break
        time.sleep(.25)
    js("Promise.all([...document.querySelectorAll('#arch img')].map(i=>i.decode().catch(()=>0)))"); time.sleep(1)

    if 'cases' in ONLY:
        js("scrollTo(0,document.getElementById('work').getBoundingClientRect().top+scrollY-260)"); time.sleep(.6)
        R=json.loads(js("""JSON.stringify((()=>{const rows=[...document.querySelectorAll('#cases .row')].map(r=>{const b=r.getBoundingClientRect(),h=r.querySelector('h3').getBoundingClientRect();return [b.top,b.bottom,h.top,h.bottom,h.left,h.right];});
          const s=document.querySelector('#work .sec-head').getBoundingClientRect(); return {rows,head:[s.top,s.bottom]};})())"""))
        cy0=R['head'][0]-1100; cy1=R['rows'][-1][1]+1000; clip={'x':0,'y':cy0,'width':1440,'height':cy1-cy0}   # the site runs on far beyond the frame — no edge ever shows, whatever the tilt
        d=outdir('cases'); DUR=1.55; N=int(DUR*FPS)+1; ST=[.12+i*.4 for i in range(4)]
        def hov(i,tau):
            a=tau-ST[i]; up=bez(a/.4) if a>0 else 0
            dn=(bez((tau-ST[i+1]-.05)/.45) if tau>ST[i+1]+.05 else 0) if i<3 else 0
            return up*(1-dn)
        for f in range(N):
            tau=f/FPS; hs=[round(hov(i,tau),4) for i in range(4)]
            js(f"""(()=>{{const h={hs};[...document.querySelectorAll('#cases .row')].slice(0,4).forEach((r,i)=>{{r.style.paddingLeft=(12*h[i])+'px';const t=r.querySelector('h3');t.style.fontVariationSettings="'wght' "+(300+300*h[i]);t.style.letterSpacing=(-.035+.015*h[i])+'em';}});}})()""")
            shot(os.path.join(d,f'{f:04d}.jpg'),clip)
        json.dump({'clip':clip,'rows':[[r[2]-cy0,r[3]-cy0,r[4],r[5]] for r in R['rows']],'starts':ST,'frames':N,'fps':FPS},open(os.path.join(d,'meta.json'),'w'))
        js("[...document.querySelectorAll('#cases .row')].forEach(r=>{r.style.paddingLeft='';const t=r.querySelector('h3');t.style.fontVariationSettings='';t.style.letterSpacing='';})")
        print('cases',N,{k:round(v) for k,v in clip.items()},'rows',len(R['rows']))

    if 'archive' in ONLY:
        js("scrollTo(0,document.getElementById('arch').getBoundingClientRect().top+scrollY-30)"); time.sleep(.6)
        A=json.loads(js("JSON.stringify([...document.querySelectorAll('#arch .arow')].map(r=>{const b=r.getBoundingClientRect();return [b.top,b.bottom];}))"))
        CX0,CX1=280,1160                                           # a narrower strip, sharp at DSF 3
        clip={'x':CX0,'y':A[0][0]-10,'width':CX1-CX0,'height':A[-1][1]-A[0][0]+20}
        x0=json.loads(js("JSON.stringify(archRows.map(r=>r.x))"))
        DUR=1.3; N=int(DUR*FPS)+1; SP=150
        def place(tau,off):
            js(f"""archRows.forEach((r,i)=>{{const half=r.tr.scrollWidth/2; let x={json.dumps(x0)}[i]+{json.dumps(off)}[i]+r.dir*{SP}*{tau}; while(x<=-half) x+=half; while(x>0) x-=half; r.tr.style.transform='translate3d('+x+'px,0,0)';}})""")
        # keep Techmas out of the strip for the whole pass: shift its row until it never crosses the clip
        off=[0]*len(x0)
        for step in range(40):
            hit=False
            for tau in (0,.33,.66,1.0,1.3):
                place(tau,off)
                bad=json.loads(js(f"JSON.stringify([...document.querySelectorAll('#arch .a-item')].filter(a=>/techmas/i.test(a.querySelector('img')?.src||'')||/techmas/i.test(a.textContent)).map(a=>{{const b=a.getBoundingClientRect(),row=[...document.querySelectorAll('#arch .arow')].indexOf(a.closest('.arow'));return [row,b.left,b.right];}}).filter(v=>v[2]>{CX0-60}&&v[1]<{CX1+60}))"))
                if bad: hit=True; off[bad[0][0]]+=90; break
            if not hit: break
        print('archive offsets',off)
        d=outdir('archive')
        for f in range(N):
            place(f/FPS,off); shot(os.path.join(d,f'{f:04d}.jpg'),clip,dsf=3)
        json.dump({'clip':clip,'rows':[[r[0]-clip['y'],r[1]-clip['y']] for r in A],'frames':N,'fps':FPS,'dsf':3},open(os.path.join(d,'meta.json'),'w'))
        print('archive',N,{k:round(v) for k,v in clip.items()})

    if 'focus' in ONLY:                                     # «What I do»: the weight wave travels across «Product approach», the grid flickers behind
        top=js("document.getElementById('focus').getBoundingClientRect().top+scrollY"); total=js("document.getElementById('focus').offsetHeight-innerHeight"); N3=js("document.querySelectorAll('#fwords .kw').length")
        y0=top+total*((N3-1)/N3+.12); js(f"scrollTo(0,{y0}); focusUpdate(true);"); time.sleep(.3)
        for _ in range(6): js('__step(1000/30)')                                         # IntersectionObserver → the grid loop is visible
        js("focusUpdate(true)"); time.sleep(2.5)                                          # the last word slides in (CSS transition, real time)
        for _ in range(60): js('__step(1000/30)')
        print('grid probe',js("(()=>{const c=document.getElementById('fgrid'),g=c.getContext('2d'),d=g.getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4*97) if(d[i]>40) n++;return [c.width,c.height,n,getComputedStyle(c).opacity,getComputedStyle(c).display]})()"))
        clip={'x':0,'y':0,'width':1440,'height':900}
        d=outdir('focus'); N=16
        for f in range(N):
            lp=.12+.76*f/(N-1); js(f"scrollTo(0,{top+total*((N3-1+lp)/N3)}); focusUpdate();"); js('__step(1000/30)'); time.sleep(.05)
            shot(os.path.join(d,f'{f:04d}.jpg'),clip)
        W=json.loads(js("JSON.stringify((()=>{const w=document.querySelector('#fwords .kw.on').getBoundingClientRect();return [w.left,w.top,w.right,w.bottom]})())"))
        json.dump({'clip':clip,'word':W,'frames':N,'fps':FPS},open(os.path.join(d,'meta.json'),'w'))
        print('focus',N,'word',[round(v) for v in W])

    if 'about' in ONLY:
        js("scrollTo(0,document.querySelector('#about .portrait').getBoundingClientRect().top+scrollY-120)"); time.sleep(.8)
        js("[...document.querySelectorAll('.rv,.rv-wait')].forEach(e=>e.classList.add('in'))")
        for _ in range(9): js('__step(1000/30)')            # the portrait starts assembling (IntersectionObserver fired on scroll)
        B=json.loads(js("""JSON.stringify((()=>{const p=document.querySelector('#about .portrait').getBoundingClientRect(),l=document.querySelector('#about .lead').getBoundingClientRect(),a=document.querySelector('#about .about').getBoundingClientRect();
          return {p:[p.left,p.top,p.right,p.bottom],l:[l.left,l.top,l.right,l.bottom],a:[a.left,a.right]};})())"""))
        top=min(B['p'][1],B['l'][1])-650; bot=max(B['p'][3],B['l'][3])+550; clip={'x':B['a'][0]-20,'y':top,'width':B['a'][1]-B['a'][0]+40,'height':bot-top}
        nw=js("document.querySelectorAll('#about .lead .wd').length")
        d=outdir('about'); DUR=1.3; N=int(DUR*FPS)+1
        for f in range(N):
            tau=f/FPS; k=round(min(1,max(0,(tau-.05)/1.0))*nw)
            js(f"document.querySelectorAll('#about .lead .wd').forEach((w,i)=>w.classList.toggle('on',i<{k}))")
            if f:                                                  # the assembly advances per animation frame: 3 ticks per video frame until it has formed, then 1
                for _ in range(2 if f<=28 else 1): js('__step(1000/30)')   # forms as the camera arrives (~0.9 s), not before
            shot(os.path.join(d,f'{f:04d}.jpg'),clip)
        json.dump({'clip':clip,'portrait':[B['p'][0]-clip['x'],B['p'][1]-top,B['p'][2]-clip['x'],B['p'][3]-top],'lead':[B['l'][0]-clip['x'],B['l'][1]-top,B['l'][2]-clip['x'],B['l'][3]-top],'frames':N,'fps':FPS},open(os.path.join(d,'meta.json'),'w'))
        print('about',N,clip,'words',nw)
finally: p.terminate()

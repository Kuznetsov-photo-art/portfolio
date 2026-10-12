# -*- coding: utf-8 -*-
# Captures the home page (andrewkuznetsov.com, phone layout 390 css px → 1080 px) as separate transparent layers,
# dark and light, plus a manifest with each layer's place on the page. The reel (reel1.html) rebuilds the page from them.
import json, subprocess, time, urllib.request, tempfile, base64, os, sys
import websocket
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'cap'); os.makedirs(OUT,exist_ok=True)
URL='https://andrewkuznetsov.com/'; DSF=1080/390
PIECES=[ # id, selector (first match), extra css to apply before capture
 ('nav','header.nav'),('spec','.hero .spec'),
 *[(f'ch{i}',f'#hname .ch:nth-child({k})' if False else None) for i,k in []],
 ('name1','#hname .ln.a'),('name2','#hname .ln.b'),('tag','.h-sub p'),('meta1','.h-meta .mono:nth-child(1)'),('meta2','.h-meta .mono:nth-child(2)'),
 ('cases_head','#work .sec-head'),('case1','#cases .row:nth-child(1)'),('case2','#cases .row:nth-child(2)'),('case3','#cases .row:nth-child(3)'),('case4','#cases .row:nth-child(4)'),
 ('arch_head','#archive .sec-head'),
 ('about_head','#about .sec-head'),('portrait','#about .portrait'),('lead','#about p.lead'),('skills','#skills'),('stats','#about .stats'),
 ('tl1','#tl .tl:nth-child(1)'),('tl2','#tl .tl:nth-child(2)'),('tl3','#tl .tl:nth-child(3)'),('tl4','#tl .tl:nth-child(4)'),
 ('c_title','#contact h2'),('c_row','#contact .c-row'),('footer','footer'),
]
PIECES=[p for p in PIECES if p[1]]
HIDE="html,body{background:transparent!important}.grain,.cur,.totop,.navfx,#ink,.gridlines,#fgrid,.reel,.pre,.toast{display:none!important}.rv,.rv-wait,.tl-wait{opacity:1!important;transform:none!important;filter:none!important}*{transition:none!important}"
def run(theme):
    p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9371','--remote-allow-origins=http://127.0.0.1:9371',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9371/json')); break
            except Exception: time.sleep(.2)
        ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9371'); n=[0]
        def cmd(m,**pa):
            n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
            while True:
                r=json.loads(ws.recv())
                if r.get('id')==n[0]: return r.get('result',{})
        js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True,awaitPromise=True).get('result',{}).get('value')
        cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=390,height=844,deviceScaleFactor=DSF,mobile=True)
        cmd('Page.addScriptToEvaluateOnNewDocument',source=f"sessionStorage.setItem('pre','1');localStorage.setItem('lang','ru');localStorage.setItem('theme','{theme}')")
        cmd('Page.navigate',url=URL); time.sleep(5)
        js("(async()=>{for(let y=0;y<document.documentElement.scrollHeight;y+=250){scrollTo(0,y);await new Promise(r=>setTimeout(r,90));}scrollTo(0,0);})()"); time.sleep(1)
        js(f"(()=>{{const s=document.createElement('style');s.textContent={json.dumps(HIDE)};document.head.append(s);}})()")
        cmd('Emulation.setDefaultBackgroundColorOverride',color={'r':0,'g':0,'b':0,'a':0})
        man={}
        for pid,sel in PIECES:
            ok=js(f"(()=>{{const e=document.querySelector({json.dumps(sel)}); if(!e) return false; e.scrollIntoView({{block:'center'}}); return true;}})()")
            if not ok: print('missing',pid,sel); continue
            time.sleep(2.6 if pid=='portrait' else .35)
            r=json.loads(js(f"JSON.stringify((()=>{{const b=document.querySelector({json.dumps(sel)}).getBoundingClientRect();return [b.left,b.top,b.width,b.height,scrollY]}})())"))
            x,y,w,h,sy=r
            d=cmd('Page.captureScreenshot',format='png',clip={'x':x,'y':y+sy,'width':w,'height':h,'scale':1},captureBeyondViewport=True)['data']
            open(os.path.join(OUT,f'{pid}_{theme or "dark"}.png'),'wb').write(base64.b64decode(d))
            man[pid]={'x':x,'y':y+sy,'w':w,'h':h}
        # archive tile images (drawn by the reel itself)
        man['_tiles']=json.loads(js("JSON.stringify([...document.querySelectorAll('#arch .a-item img')].slice(0,40).map(i=>i.currentSrc||i.src))"))
        man['_marquee']=json.loads(js("JSON.stringify([...document.querySelectorAll('#mq span')].slice(0,12).map(s=>[s.textContent.trim(),s.classList.contains('o')]))"))
        return man
    finally: p.terminate()
m=run(''); run('light')
json.dump(m,open(os.path.join(OUT,'manifest.json'),'w'),ensure_ascii=False,indent=1)
print(len(m),'pieces')

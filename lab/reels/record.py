# -*- coding: utf-8 -*-
# Renders reel1.html frame by frame in headless Chrome (window.__seek) and muxes it with reel1-beat.wav → video/<name>.mp4
# usage: record.py <page url> <out.mp4>   (the page must be served with /assets/fonts available)
import json, subprocess, time, urllib.request, tempfile, base64, os, sys
import websocket, imageio_ffmpeg
url,out=sys.argv[1],sys.argv[2]; FPS=30; T=20.0
HERE=os.path.dirname(os.path.abspath(__file__)); wav=os.path.join(HERE,'reel1-beat.wav')
p=subprocess.Popen(['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome','--headless=new','--hide-scrollbars','--remote-debugging-port=9373','--remote-allow-origins=http://127.0.0.1:9373',f'--user-data-dir={tempfile.mkdtemp()}','about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
ff=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-i','-','-i',wav,
    '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-profile:v','high','-r',str(FPS),
    '-c:a','aac','-b:a','256k','-shortest','-movflags','+faststart',out],stdin=subprocess.PIPE)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen('http://127.0.0.1:9373/json')); break
        except Exception: time.sleep(.2)
    ws=websocket.create_connection([t for t in tabs if t['type']=='page'][0]['webSocketDebuggerUrl'],timeout=120,origin='http://127.0.0.1:9373'); n=[0]
    def cmd(m,**pa):
        n[0]+=1; ws.send(json.dumps({'id':n[0],'method':m,'params':pa}))
        while True:
            r=json.loads(ws.recv())
            if r.get('id')==n[0]: return r.get('result',{})
    js=lambda e: cmd('Runtime.evaluate',expression=e,returnByValue=True).get('result',{}).get('value')
    cmd('Page.enable'); cmd('Emulation.setDeviceMetricsOverride',width=1080,height=1920,deviceScaleFactor=1,mobile=False)
    cmd('Page.navigate',url=url+'?t=0')
    for _ in range(80):
        time.sleep(.25)
        if js('window.__ready===true'): break
    for i in range(int(T*FPS)):
        js(f'__seek({i/FPS})')
        ff.stdin.write(base64.b64decode(cmd('Page.captureScreenshot',format='jpeg',quality=93)['data']))
        if i%60==0: print(f'{i/FPS:.0f}s',end=' ',flush=True)
finally:
    ff.stdin.close(); ff.wait(); p.terminate()
print('\n',out)

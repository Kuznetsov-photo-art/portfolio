# -*- coding: utf-8 -*-
# REEL2 score — cinematic product-film hybrid, synthesised from scratch (no samples): 120 BPM, D minor, 22 s.
# 0–4 ambient swell + rim-light whoosh · 4 first hit → 4–8 pulse with plucked arps (macro shots) · 8–12 fuller groove (type)
# · 12–14 riser + roll, half-beat of silence · 14–18 drop with wide chords (phone line-up) · 18 braam + boom · 18–22 tail.
import numpy as np, os
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=44100; BPM=120; BEAT=60/BPM; BAR=4*BEAT; DUR=22.0; N=int(SR*DUR)
rng=np.random.default_rng(21)
L=np.zeros(N); R=np.zeros(N); KICKS=[]
def at(t): return int(round(t*SR))
def add(sig,t,g=1.0,pan=0.0):
    i=at(t); j=min(N,i+len(sig))
    if j<=i: return
    s=sig[:j-i]*g; L[i:j]+=s*np.sqrt((1-pan)/2)*1.414; R[i:j]+=s*np.sqrt((1+pan)/2)*1.414
def env(n,a,d): t=np.arange(n)/SR; e=np.exp(-t/d); return e*(np.clip(t/a,0,1) if a>0 else 1)
def lp(x,f,o=2): return sosfilt(butter(o,min(f,SR/2-100),'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,lo,hi,o=2): return sosfilt(butter(o,[lo,min(hi,SR/2-100)],'band',fs=SR,output='sos'),x)
def saw(f,n,det=0.0,voices=1):
    t=np.arange(n)/SR; out=np.zeros(n)
    ds=[0] if voices==1 else np.linspace(-det,det,voices)
    for d in ds: out+=2*((t*f*(1+d)+rng.random())%1.0)-1
    return out/len(ds)
def note(m): return 440*2**((m-69)/12)
# --- instruments
def kick(n=int(.5*SR)):
    t=np.arange(n)/SR; f=40+130*np.exp(-t*40); body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*6.5)
    return np.tanh((body+hp(rng.standard_normal(n),3500)*np.exp(-t*420)*.3)*1.7)
def snap():
    n=int(.25*SR); t=np.arange(n)/SR; return bp(rng.standard_normal(n),1500,7000)*np.exp(-t*38)*.9
def clap():
    n=int(.5*SR); x=bp(rng.standard_normal(n),900,3000); e=np.zeros(n)
    for k,o in enumerate([0,.01,.021]): i=int(o*SR); e[i:]+=np.exp(-np.arange(n-i)/SR/(.01 if k<2 else .15))
    return x*e
def hat(op=False): n=int((.25 if op else .05)*SR); return hp(rng.standard_normal(n),8000,4)*env(n,0,.09 if op else .015)
def boom(d=2.6):
    n=int(d*SR); t=np.arange(n)/SR; f=28+55*np.exp(-t*2.6)
    return np.tanh((np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.3)+lp(rng.standard_normal(n),3000)*np.exp(-t*3)*.3)*1.5)
def whoosh(d,up=True):
    n=int(d*SR); k=np.arange(n)/n; x=rng.standard_normal(n); out=np.zeros(n); seg=1024
    for i in range(0,n,seg):
        kk=k[i] if up else 1-k[i]; c=200+8000*kk**2; out[i:i+seg]=bp(x[i:i+seg],c*.6,c*1.5,1)
    return out*(np.sin(np.pi*k)**1.5 if not up else k**2)
def pad(ms,d,cut=900):
    n=int(d*SR); x=sum(saw(note(m),n,.006,3) for m in ms)/len(ms); return lp(x,cut)*env(n,1.2,d*1.4)
def pluck(m,d=.35):
    n=int(d*SR); t=np.arange(n)/SR; f=note(m)
    x=(np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*2*f*t)+.25*np.sin(2*np.pi*3.01*f*t))*np.exp(-t*9)
    return x*np.clip(t/.003,0,1)
def chord(ms,d=.42,cut=3200):
    n=int(d*SR); x=sum(saw(note(m),n,.012,5) for m in ms)/len(ms); return lp(x,cut)*env(n,.005,.22)
def braam(ms,d=3.2):
    n=int(d*SR); x=sum(saw(note(m),n,.008,5) for m in ms)/len(ms); out=np.zeros(n); seg=2048
    for i in range(0,n,seg): c=250+1800*min(1,i/(.35*SR))*np.exp(-i/SR*.6); out[i:i+seg]=lp(x[i:i+seg],c)
    return np.tanh(out*2.2)*env(n,.02,1.6)
def sub(m,d): n=int(d*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*note(m)*t)*env(n,.01,d*.7)
def bassnote(m,d):
    n=int(d*SR); x=np.tanh(lp(saw(note(m),n)*.7+np.sin(2*np.pi*note(m)*np.arange(n)/SR),600)*1.8); return x*env(n,.004,.14)
bt=lambda b: b*BEAT
# --- 0–4: ambient swell, rim-light whoosh, first hit at 4.0
add(pad([50,57,62,65,69],4.5,700),0,.55)               # D minor 9 haze
add(sub(38,4.0),0,.35)
for k in range(6): add(pluck(86-k*2,.6),.6+k*.45,.08*(1-k/7),pan=(-.5 if k%2 else .5))  # sparkle, falling
add(whoosh(2.2,True),1.6,.35)
add(whoosh(.9,True),3.1,.5)
add(boom(),bt(8),.9); add(kick(),bt(8),.9); KICKS.append(bt(8))
# --- 4–8: pulse + plucked arps with dotted echo (macro shots)
ARP=[62,65,69,72,74,72,69,65]
for b in range(8,16):
    if b%2==0: add(kick(),bt(b),.85); KICKS.append(bt(b))
    if b%4==2: add(snap(),bt(b),.45)
    for s in range(4): add(hat(),bt(b)+s*BEAT/4,.06+.03*(s%2),pan=.3 if s%2 else -.3)
    for h in (0,.5):
        m=ARP[int((b*2+h*2))%8]; p=pluck(m)
        for e in range(3): add(p,bt(b+h)+e*BEAT*.75,.22*(.45**e),pan=(.35 if e%2 else -.2))
for bar_m,b0 in ((38,8),(41,12)): add(sub(bar_m,BAR*1.0),bt(b0),.4)
# --- 8–12: fuller groove (type statements)
PROG=[(38,[62,65,69]),(46,[62,65,70]),(41,[60,65,69]),(43,[62,67,70])]
for i,b in enumerate(range(16,24)):
    add(kick(),bt(b),.95); KICKS.append(bt(b))
    if b%2==1: add(clap(),bt(b),.5)
    add(hat(True),bt(b+.5),.12,pan=.25)
    root=PROG[(i//2)%4][0]
    for h in (0.5,):
        add(bassnote(root,BEAT*.45),bt(b+h),.5)
    m=ARP[(b*2)%8]; add(pluck(m),bt(b),.16,pan=-.3); add(pluck(m+12,.25),bt(b+.5),.1,pan=.3)
add(pad([PROG[0][1][0]-12]+PROG[0][1],4.0,1200),bt(16),.3)
# --- 12–14: riser, snare roll, filter sweep, half-beat of silence before the drop
roll=[0,.5,1,1.5,2,2.25,2.5,2.75,3,3.125,3.25,3.375]
for r in roll: add(snap(),bt(24+r),.25+.45*(r/3.4))
add(whoosh(BAR-BEAT/2,True),bt(24),.6)
n=int((BAR-BEAT/2)*SR); t=np.arange(n)/SR; add(np.sin(2*np.pi*np.cumsum(110*2**(t/1.75*2))/SR)*(t/t[-1])**2*.25,bt(24),1)
# --- 14–18: drop with wide chords (phone line-up)
add(boom(),bt(28),.85)
for i,b in enumerate(range(28,36)):
    add(kick(),bt(b),1.0); KICKS.append(bt(b))
    if b%2==1: add(clap(),bt(b),.6)
    add(hat(True),bt(b+.5),.14,pan=.2); add(hat(),bt(b+.25),.07,pan=-.3); add(hat(),bt(b+.75),.07,pan=.3)
    root,ch=PROG[(i//2)%4]
    add(bassnote(root,BEAT*.45),bt(b+.5),.6)
    if b%2==0:
        c=chord(ch+[ch[0]+12]); add(c,bt(b),.42,pan=-.15)
        for e in range(1,3): add(c,bt(b)+e*BEAT*.75,.42*(.4**e),pan=(.4 if e%2 else -.4))
add(whoosh(.8,True),bt(35.4),.45)
# --- 18: braam + boom, then the tail
add(braam([38,45,50,53,57]),bt(36),.9); add(boom(3.5),bt(36),1.0); add(kick(),bt(36),1.0); KICKS.append(bt(36))
add(pad([50,57,62,65,69],4.0,800),bt(36.5),.25)
for k in range(5): add(pluck(74+[0,3,7,10,12][k],.8),bt(38)+k*.38,.09*(1-k/6),pan=(.4 if k%2 else -.4))
# --- mix: sidechain, room, glue
duck=np.ones(N)
for kt in KICKS:
    i=at(kt); d=np.arange(N-i)/SR; duck[i:]=np.minimum(duck[i:],1-.5*np.exp(-d*8))
def ir(seed,dec=3.0,dur=2.2): r=np.random.default_rng(seed); n=int(dur*SR); return r.standard_normal(n)*np.exp(-np.arange(n)/SR*dec)*.02
L2=L*duck; R2=R*duck
L2=L2+fftconvolve(L2,ir(3))[:N]*.7; R2=R2+fftconvolve(R2,ir(4))[:N]*.7
L2=hp(L2,22); R2=hp(R2,22)
m=np.tanh(np.stack([L2,R2],1)*1.2); m/=np.abs(m).max()/0.89
fn=int(.6*SR); m[-fn:]*=np.linspace(1,0,fn)[:,None]
# a real half-beat of silence before the drop (the reverb tail would fill it otherwise)
g=np.ones(N); i0,i1,i2=at(bt(27.5)-.02),at(bt(27.5)+.03),at(bt(28)-.004); g[i0:i1]=np.linspace(1,.02,i1-i0); g[i1:i2]=.02; m*=g[:,None]
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'reel2-beat.wav')
wavfile.write(out,SR,(m*32767).astype(np.int16)); print(out,f'{DUR}s',f'beat {BEAT}s')

# -*- coding: utf-8 -*-
# REEL2 score v2 — driving, synthesised from scratch (no samples): 128 BPM, F minor, 22.5 s (12 bars of 1.875 s).
# bar 0 filtered drive from the first second · bar 1 filter opens, roll, whoosh · bars 2–3 groove (macro shots, beats 8–15)
# · bars 4–5 groove + stabs (type, beats 16–23) · bar 6 build: kick + 16th roll + riser, half-beat of silence · bars 7–9 DROP
# (line-up, beats 28–39) · bar 10 final impact + stutter echoes · tail.
import numpy as np, os
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR=44100; BPM=128; BEAT=60/BPM; BAR=4*BEAT; DUR=22.5; N=int(SR*DUR)
rng=np.random.default_rng(128)
L=np.zeros(N); R=np.zeros(N); KICKS=[]
FX_L=np.zeros(N); FX_R=np.zeros(N)                     # risers/impacts bypass the sidechain
def at(t): return int(round(t*SR))
def add(sig,t,g=1.0,pan=0.0,fx=False):
    i=at(t); j=min(N,i+len(sig))
    if j<=i or i<0: return
    s=sig[:j-i]*g; a,b=(FX_L,FX_R) if fx else (L,R)
    a[i:j]+=s*np.sqrt((1-pan)/2)*1.414; b[i:j]+=s*np.sqrt((1+pan)/2)*1.414
def env(n,a,d): t=np.arange(n)/SR; e=np.exp(-t/d); return e*(np.clip(t/a,0,1) if a>0 else 1)
def lp(x,f,o=2): return sosfilt(butter(o,min(f,SR/2-100),'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,lo,hi,o=2): return sosfilt(butter(o,[lo,min(hi,SR/2-100)],'band',fs=SR,output='sos'),x)
def saw(f,n,det=0.0,v=1):
    t=np.arange(n)/SR; ds=[0] if v==1 else np.linspace(-det,det,v)
    return sum(2*((t*f*(1+d)+rng.random())%1.0)-1 for d in ds)/len(ds)
def sq(f,n): t=np.arange(n)/SR; return np.sign(np.sin(2*np.pi*f*t))
def note(m): return 440*2**((m-69)/12)
bt=lambda b: b*BEAT
# ---------- instruments
def kick(n=int(.42*SR),hard=1.0):
    t=np.arange(n)/SR; f=44+150*np.exp(-t*46); body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7.5)
    click=hp(rng.standard_normal(n),4000)*np.exp(-t*500)*.45
    return np.tanh((body+click)*2.0*hard)
def clap():
    n=int(.55*SR); x=bp(rng.standard_normal(n),1000,3600); e=np.zeros(n)
    for k,o in enumerate([0,.009,.019,.028]): i=int(o*SR); e[i:]+=np.exp(-np.arange(n-i)/SR/(.008 if k<3 else .18))
    return np.tanh(x*e*1.6)
def snare():
    n=int(.2*SR); t=np.arange(n)/SR
    return np.tanh(bp(rng.standard_normal(n),1500,7500)*np.exp(-t*26)*1.4+np.sin(2*np.pi*200*t)*np.exp(-t*34)*.6)
def hat(op=False,acc=1.0): n=int((.22 if op else .045)*SR); return hp(rng.standard_normal(n),8500,4)*env(n,0,.08 if op else .012)*acc
def shaker(): n=int(.07*SR); return bp(rng.standard_normal(n),5000,12000)*env(n,.01,.02)
def tom(m):
    n=int(.3*SR); t=np.arange(n)/SR; f=note(m)*(1+.6*np.exp(-t*30)); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def impact(d=2.4,g=1.0):
    n=int(d*SR); t=np.arange(n)/SR; f=30+70*np.exp(-t*3.2)
    boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.5); crash=hp(lp(rng.standard_normal(n),9000),300)*np.exp(-t*2.6)*.45
    return np.tanh((boom+crash)*1.6*g)
def riser(d):
    n=int(d*SR); k=np.arange(n)/n; x=rng.standard_normal(n); out=np.zeros(n); seg=1024
    for i in range(0,n,seg): c=300+11000*k[i]**2.4; out[i:i+seg]=bp(x[i:i+seg],c*.6,c*1.5,1)
    tone=saw(1,n)*0; f=110*2**(k*3); tone=np.sin(2*np.pi*np.cumsum(f)/SR)*.3
    return (out*.9+tone)*k**2
def rev_crash(d):
    n=int(d*SR); x=hp(lp(rng.standard_normal(n),10000),400)*np.exp(-np.arange(n)[::-1]/SR*2.2); return x*np.linspace(0,1,n)**2
def downlifter(d):
    n=int(d*SR); k=np.arange(n)/n; x=rng.standard_normal(n); out=np.zeros(n); seg=1024
    for i in range(0,n,seg): c=9000*(1-k[i])**2+200; out[i:i+seg]=bp(x[i:i+seg],c*.6,c*1.5,1)
    return out*(1-k)**1.5
def bass16(m,n_steps=1,cut=900,drive=2.2):
    n=int(BEAT/4*SR*n_steps*.9); f=note(m); x=saw(f,n)*.8+sq(f/2,n)*.35+np.sin(2*np.pi*f*np.arange(n)/SR)*.9
    return np.tanh(lp(x,cut)*drive)*env(n,.002,.07)
def stab(ms,d=.3,cut=4200):
    n=int(d*SR); x=sum(saw(note(m),n,.014,5) for m in ms)/len(ms); return np.tanh(lp(x,cut)*1.6)*env(n,.003,.12)
def pluck(m,d=.3):
    n=int(d*SR); t=np.arange(n)/SR; f=note(m)
    return (np.sin(2*np.pi*f*t)+.6*saw(f,n)*np.exp(-t*25))*np.exp(-t*10)*np.clip(t/.002,0,1)
def pad(ms,d,cut=1200): n=int(d*SR); x=sum(saw(note(m),n,.006,3) for m in ms)/len(ms); return lp(x,cut)*env(n,.8,d)
# ---------- harmony (F minor): Fm – Db – Ab – Eb, one chord per half bar in the drop
CH=[(41,[65,68,72]),(37,[65,68,73]),(44,[63,68,72]),(39,[63,67,70])]
ROLL=[0,0,12,0, 0,12,0,10, 0,0,12,0, 15,12,10,7]     # galloping 16ths, octave jumps
def bass_bar(b,root,cut=900,g=.5):
    for s,o in enumerate(ROLL):
        if s%4==0: continue                            # leave the downbeat to the kick
        add(bass16(root+o,1,cut),bt(b*4)+s*BEAT/4,g)
def drums_bar(b,full=True,clap_on=True,open_h=True):
    for k in range(4):
        add(kick(),bt(b*4+k),1.0); KICKS.append(bt(b*4+k))
        if clap_on and k in (1,3): add(clap(),bt(b*4+k),.62)
        for s in range(4):
            acc=1.0 if s==2 else .55
            add(hat(acc=acc),bt(b*4+k)+s*BEAT/4,.13,pan=.25 if s%2 else -.25)
        if open_h: add(hat(True),bt(b*4+k+.5),.16,pan=.15)
        if full: add(shaker(),bt(b*4+k+.25),.07,pan=-.5); add(shaker(),bt(b*4+k+.75),.07,pan=.5)
# bar 0: driving from the first second, everything low-passed
for k in range(4): add(lp(kick(),900),bt(k),.8); KICKS.append(bt(k))
for k in range(4):
    for s in range(1,4): add(lp(bass16(41+ROLL[k*4+s],1,500),800),bt(k)+s*BEAT/4,.35)
for s in range(16): add(hat(acc=.5),s*BEAT/4,.07,pan=.3 if s%2 else -.3)
add(pad([53,56,60,65],BAR*2,700),0,.3)
# bar 1: filter opens, snare roll, whoosh into the hit
for k in range(4):
    add(kick(),bt(4+k),.9); KICKS.append(bt(4+k))
    for s in range(1,4): add(bass16(41+ROLL[k*4+s],1,400+600*(k*4+s)/16),bt(4+k)+s*BEAT/4,.4)
for s in range(8,16): add(snare(),bt(4)+s*BEAT/4,.18+.04*(s-8))
for s in (12,13,14,15): add(snare(),bt(4)+s*BEAT/4+BEAT/8,.3)
add(riser(BAR),bt(4),.45,fx=True)
add(rev_crash(BEAT*2),bt(6),.45,fx=True)
# bars 2–3: groove (macro shots)
add(impact(),bt(8),.85,fx=True)
for b in (2,3):
    drums_bar(b); bass_bar(b,41 if b==2 else 37)
    for k in range(4):                                  # bright plucks on the offbeats
        m=[72,75,77,80][k]; add(pluck(m),bt(b*4+k+.5),.22,pan=-.3); add(pluck(m),bt(b*4+k+.5)+BEAT*.75,.08,pan=.3)
    add(tom(50),bt(b*4+3.5),.25); add(tom(45),bt(b*4+3.75),.25)
# bars 4–5: groove + stabs (type statements)
for b in (4,5):
    drums_bar(b); bass_bar(b,44 if b==4 else 39,1100,.55)
    for h,(root,ch) in enumerate(CH[(b-4)*2:(b-4)*2+2]):
        st=stab(ch); add(st,bt(b*4+h*2),.4,pan=-.15); add(st,bt(b*4+h*2+1.5),.3,pan=.15)
add(rev_crash(BEAT*2),bt(22),.4,fx=True)
# bar 6: build — kick only, 16th roll, riser, pitch-up; half a beat of silence before the drop
for k in range(4): add(kick(hard=.9),bt(24+k),.85); KICKS.append(bt(24+k))
for s in range(14): add(snare(),bt(24)+s*BEAT/4,.16+.4*(s/14)**1.5)
for s in range(14): add(bass16(41+12*(s%2)+s,1,500+200*s),bt(24)+s*BEAT/4,.3)
add(riser(BAR-BEAT/2),bt(24),.6,fx=True)
# bars 7–9: DROP
add(impact(2.6,1.1),bt(28),1.0,fx=True)
for i,b in enumerate((7,8,9)):
    drums_bar(b);
    for h in range(2):
        root,ch=CH[(i*2+h)%4]
        for s,o in enumerate(ROLL[h*8:h*8+8]):
            if s%4==0: continue
            add(bass16(root+o,1,1400,2.6),bt(b*4+h*2)+s*BEAT/4,.62)
        for off in (0,.75,1.5):                         # syncopated wide stabs
            st=stab(ch+[ch[0]+12],.26,5200); add(st,bt(b*4+h*2+off),.42,pan=(-.25 if off==.75 else .2))
    if b==8: add(rev_crash(BEAT),bt(b*4+3),.35,fx=True)
    add(tom(52),bt(b*4+3.25),.3); add(tom(47),bt(b*4+3.5),.3); add(tom(43),bt(b*4+3.75),.32)
add(downlifter(BAR),bt(28),.3,fx=True)
add(riser(BEAT*3),bt(37),.4,fx=True)
# bar 10: final impact + stutter echoes of the last chord
add(impact(3.2,1.2),bt(40),1.0,fx=True); add(kick(hard=1.1),bt(40),1.0); KICKS.append(bt(40))
st=stab(CH[0][1]+[77],.4,5200)
for k in range(8): add(st,bt(40)+k*BEAT/2,.45*(.72**k),pan=(.5 if k%2 else -.5))
add(pad([53,60,65,68],3.6,900),bt(40),.25)
for k,m in enumerate([77,80,84,89]): add(pluck(m,.6),bt(42)+k*BEAT/2,.12*(1-k/5))
# ---------- mix: hard sidechain, room, glue, silence before the drop
duck=np.ones(N)
for kt in KICKS:
    i=at(kt); d=np.arange(N-i)/SR; duck[i:]=np.minimum(duck[i:],1-.62*np.exp(-d*10))
def ir(seed,dec=3.2,dur=1.8): r=np.random.default_rng(seed); n=int(dur*SR); return r.standard_normal(n)*np.exp(-np.arange(n)/SR*dec)*.018
L2=L*duck+FX_L; R2=R*duck+FX_R
L2=L2+fftconvolve(L2,ir(5))[:N]*.6; R2=R2+fftconvolve(R2,ir(6))[:N]*.6
L2=hp(L2,25); R2=hp(R2,25)
m=np.tanh(np.stack([L2,R2],1)*1.35); m/=np.abs(m).max()/0.9
g=np.ones(N); i0,i1,i2=at(bt(27.5)-.015),at(bt(27.5)+.02),at(bt(28)-.003); g[i0:i1]=np.linspace(1,.01,i1-i0); g[i1:i2]=.01; m*=g[:,None]
fn=int(.8*SR); m[-fn:]*=np.linspace(1,0,fn)[:,None]
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'reel2-beat-v2.wav')
wavfile.write(out,SR,(m*32767).astype(np.int16)); print(out,f'{DUR}s',f'beat {BEAT:.5f}s')

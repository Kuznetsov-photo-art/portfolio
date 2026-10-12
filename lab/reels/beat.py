# -*- coding: utf-8 -*-
# Original bass-heavy track for the reel, synthesised from scratch (no samples, no third-party audio): 124 BPM, F minor, 20 s.
# Bars: 0 intro (pad + ticks) · 1 build (snare roll, riser, gap) · 2–5 drop A · 5→6 reverse swell + impact (theme flip in the video)
#       · 6–8 drop B (stabs with delay) · 9 final impact + tail.  Writes reel1-beat.wav next to this file.
import numpy as np, os, sys
from scipy.signal import butter, sosfilt, fftconvolve
SR=44100; BPM=124; BEAT=60/BPM; BAR=4*BEAT; DUR=20.0; N=int(SR*DUR)
rng=np.random.default_rng(7)
L=np.zeros(N); R=np.zeros(N)
def at(t): return int(round(t*SR))
def add(sig,t,gain=1.0,pan=0.0):
    i=at(t); j=min(N,i+len(sig))
    if j<=i: return
    s=sig[:j-i]*gain; L[i:j]+=s*np.sqrt((1-pan)/2)*1.414; R[i:j]+=s*np.sqrt((1+pan)/2)*1.414
def env(n,a,d): # attack/decay in seconds
    t=np.arange(n)/SR; e=np.exp(-t/d);
    if a>0: e*=np.clip(t/a,0,1)
    return e
def lp(x,f,o=2): return sosfilt(butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return sosfilt(butter(o,f,'high',fs=SR,output='sos'),x)
def bp(x,lo,hi,o=2): return sosfilt(butter(o,[lo,hi],'band',fs=SR,output='sos'),x)
def saw(freq,n,detune=0.0):
    t=np.arange(n)/SR; out=np.zeros(n)
    for d in ([0] if not detune else [-detune,0,detune]):
        ph=(t*freq*(1+d))%1.0; out+=2*ph-1
    return out/(1 if not detune else 3)

# --- instruments ---
def kick(n=int(.45*SR)):
    t=np.arange(n)/SR; f=42+120*np.exp(-t*38); ph=2*np.pi*np.cumsum(f)/SR
    body=np.sin(ph)*np.exp(-t*7.5); click=hp(rng.standard_normal(n),3000)*np.exp(-t*380)*.35
    return np.tanh((body+click)*1.6)
def hat(open_=False):
    n=int((.32 if open_ else .06)*SR); x=hp(rng.standard_normal(n),7000,4)
    return x*env(n,0,.11 if open_ else .018)
def clap():
    n=int(.5*SR); x=bp(rng.standard_normal(n),900,2600); e=np.zeros(n)
    for k,o in enumerate([0,.011,.022]): i=int(o*SR); e[i:]+=np.exp(-np.arange(n-i)/SR/(.012 if k<2 else .16))
    return x*e*.9
def snare():
    n=int(.18*SR); t=np.arange(n)/SR
    return (bp(rng.standard_normal(n),1200,6000)*np.exp(-t*28)+np.sin(2*np.pi*190*t)*np.exp(-t*30)*.5)
def impact(n=int(2.2*SR)):
    t=np.arange(n)/SR; f=30+50*np.exp(-t*3); boom=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*1.6)
    crash=lp(rng.standard_normal(n),5000)*np.exp(-t*2.2)*.35
    return np.tanh((boom+crash)*1.4)
def riser(d):
    n=int(d*SR); t=np.arange(n)/SR; k=t/d
    noise=rng.standard_normal(n); out=np.zeros(n); seg=2048
    for i in range(0,n,seg):  # band-pass sweeping up
        c=300+9000*(k[min(i,n-1)]**2.2); out[i:i+seg]=bp(noise[i:i+seg],c*.7,min(c*1.4,SR/2-100),1)
    tone=np.sin(2*np.pi*np.cumsum(220*2**(k*2))/SR)*.25
    return (out*.8+tone)*(k**2)
def reverse_swell(d):
    n=int(d*SR); x=lp(rng.standard_normal(n),6000)*np.exp(-np.arange(n)[::-1]/SR*3.0)
    return x*np.linspace(0,1,n)**1.5
def pad(freqs,d):
    n=int(d*SR); x=sum(saw(f,n,.004) for f in freqs)/len(freqs)
    return lp(x,900)*env(n,.6,d*1.2)*.5
def stab(freqs,d=.22):
    n=int(d*SR); x=sum(saw(f,n,.006) for f in freqs)/len(freqs)
    return lp(x,2400)*env(n,.004,.09)

# --- arrangement ---
F1,Ab1,Bb1,C2,Db2,Eb1=43.65,51.91,58.27,65.41,69.30,38.89
KICKS=[]
def bar_t(b,beat=0,step=0): return b*BAR+beat*BEAT+step*BEAT/4
# intro pad + ticks
add(pad([174.6,207.7,261.6],BAR*2),0,.55)
for s in range(16): add(hat(),bar_t(0,0,s),.10+.04*(s%2),pan=.3 if s%2 else -.3)
# build: snare roll 8ths→16ths, riser, hats; gap of half a beat before the drop
for s in range(0,12,2): add(snare(),bar_t(1,0,s),.25+.03*s)
for s in range(12,14): add(snare(),bar_t(1,0,s),.6)
for s in range(16): add(hat(),bar_t(1,0,s),.12,pan=.25 if s%2 else -.25)
add(riser(BAR-BEAT/2),bar_t(1),.55)
# bass riff (16 steps): note per step, None = rest
RIFF=[F1,None,F1,F1, None,F1,Ab1,None, F1,None,F1,Eb1, None,F1,C2,Bb1]
def bass_bar(b,gain=1.0):
    for s,f in enumerate(RIFF):
        if f is None: continue
        n=int(BEAT/4*SR*.92); x=np.tanh(lp(saw(f,n)*.8+np.sin(2*np.pi*f*np.arange(n)/SR)*1.0,520)*1.8)
        add(x*env(n,.003,.12),bar_t(b,0,s),.55*gain)
def drums_bar(b,stabs=False,fill=False):
    for beat in range(4):
        add(kick(),bar_t(b,beat),1.0); KICKS.append(bar_t(b,beat))
        add(hat(True),bar_t(b,beat,2),.16,pan=.2)
        add(hat(),bar_t(b,beat,1),.09,pan=-.35); add(hat(),bar_t(b,beat,3),.09,pan=.35)
        if beat in (1,3): add(clap(),bar_t(b,beat),.55)
    if stabs:
        for st,ch in [(0,[349.2,415.3,523.3]),(6,[349.2,415.3,523.3]),(10,[311.1,392.0,466.2]),(14,[277.2,349.2,415.3])]:
            s=stab(ch); add(s,bar_t(b,0,st),.32,pan=-.2)
            for k in range(1,4): add(s,bar_t(b,0,st)+k*BEAT*.75,.32*(.42**k),pan=.35 if k%2 else -.35)  # dotted-8th echo
    if fill:
        for s in (12,13,14,15): add(snare(),bar_t(b,0,s),.35+.08*(s-12))
add(impact(),bar_t(2),.85)
for b in range(2,6):
    drums_bar(b,fill=(b==4)); bass_bar(b)
# 5 → 6: last half bar of bar 5 drops the kick for a reverse swell into the theme flip
add(reverse_swell(BEAT*2),bar_t(5,2),.5)
add(impact(),bar_t(6),.9)
for b in range(6,9):
    drums_bar(b,stabs=True,fill=(b==8)); bass_bar(b,1.08)
# outro: final impact on bar 9 and a decaying stab echo
add(impact(int(2.6*SR)),bar_t(9),1.0); add(kick(),bar_t(9),1.0); KICKS.append(bar_t(9))
s=stab([349.2,415.3,523.3],.5)
for k in range(6): add(s,bar_t(9)+k*BEAT*.75,.4*(.55**k),pan=.4 if k%2 else -.4)
for st in range(0,16,2): add(hat(),bar_t(9,0,st),.05*(1-st/16))

# sidechain: duck everything except kicks/impacts a little after every kick
duck=np.ones(N); t=np.arange(N)/SR
for kt in KICKS:
    i=at(kt); d=np.arange(N-i)/SR; duck[i:]=np.minimum(duck[i:],1-.55*np.exp(-d*9))
# short room reverb on the whole mix (decorrelated L/R), then glue: soft clip + normalise
def ir(seed):
    r=np.random.default_rng(seed); n=int(1.1*SR); return r.standard_normal(n)*np.exp(-np.arange(n)/SR*4.5)*.03
L2=L*duck; R2=R*duck
L2=L2+fftconvolve(L2,ir(1))[:N]*.6; R2=R2+fftconvolve(R2,ir(2))[:N]*.6
L2=hp(L2,25); R2=hp(R2,25)
m=np.tanh(np.stack([L2,R2],1)*1.25); m/=np.abs(m).max()/0.89
fade=np.ones(N); fn=int(.35*SR); fade[-fn:]=np.linspace(1,0,fn); m*=fade[:,None]
from scipy.io import wavfile
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'reel1-beat.wav')
wavfile.write(out,SR,(m*32767).astype(np.int16)); print(out, f'{DUR}s', f'beat {BEAT:.4f}s', f'bar {BAR:.4f}s')

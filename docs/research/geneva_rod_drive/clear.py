import numpy as np, math, pickle, json, sys
import os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import drive as DV
u2=DV.u2; f2=DV.f2; L2=DV.g["L2"]; L1b=DV.g["L1b"]
out=pickle.load(open(DV.SP+"/drive.pkl","rb"))
res={}
for side in (1,-1):
    r,a=out[("V0 model ratio 1, r_h 2.49, MR63 roller",side)]
    Cs=a["Cs"]; prof=a["prof"]; q2t=DV.q2hi+DV.s_q*DV.ts
    PL=DV.axis_off+DV.hL*u2
    # follower zone: roller cylinder r 3.5 (+ eye) at each beta, plus the arm (segment PL->C, width 5) ; heights F2+6.2..F2+10.4
    zone=[]
    for c in Cs[::10]:
        for s in np.linspace(0,1,10): zone.append(PL*(1-s)+c*s)
    zone=np.array(zone)
    # link 2 points (member-2 ref frame) in link 1b's frame over q2 in [q2lo, q2hi - 16.8]
    qs=np.radians(np.linspace(DV.g["q2stops"][0], DV.g["q2stops"][1]-16.8, 116))
    dmin=1e9; qbad=None
    for q in qs:
        X=L2@DV.rotm(u2,q).T
        h=X@u2; rp=np.linalg.norm(X-h[:,None]*u2,axis=1)
        sel=(rp<30)
        if not sel.any(): continue
        Y=X[sel]
        # distance from Y to the zone polyline (as points), minus roller radius 3.0 (plan) ; ignore height (conservative)
        d=np.min(np.linalg.norm(Y[:,None,:]-zone[None,:,:],axis=2))-3.0
        if d<dmin: dmin=d; qbad=math.degrees(q)
    # nose sweep: lobe profile points (link-2 frame) rotated over the q2 range vs the rocker tube (axis_off, radius 5)
    ax=DV.unit(DV.axis_off); dtube=1e9
    for q in qs:
        P=prof@DV.rotm(u2,q).T
        pr=P-(P@u2)[:,None]*u2
        d=np.linalg.norm(pr-DV.axis_off,axis=1).min()-5.0
        dtube=min(dtube,d)
    res[side]=dict(L2_vs_follower_zone_plan_mm=round(float(dmin),1),at_q2=qbad,lobe_vs_rocker_tube_mm=round(float(dtube),2))
print(json.dumps(res))

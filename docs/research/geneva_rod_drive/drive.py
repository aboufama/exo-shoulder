"""Rod-drive red team: exact lobe for the linear law through the real RSSR rod + bell-crank rocker (axis || u2)."""
import os
import numpy as np, math, json, sys
SP=os.path.dirname(os.path.abspath(__file__))
Z=np.load(SP+"/geo.npz"); g={k:Z[k] for k in Z.files}
u1,u2,u3,uK=g["u1"],g["u2"],g["u3"],g["uK"]; f=g["f"]; fK=float(g["fK"]); f2=float(f[1])
HUB_R,UP,T_LINK,CROWN,RUN,capK,bk1,bk2,a1max=[float(x) for x in g["consts"]]
def unit(v): return v/np.linalg.norm(v)
def rotm(ax,a):
    ax=unit(ax); K=np.array([[0,-ax[2],ax[1]],[ax[2],0,-ax[0]],[-ax[1],ax[0],0]]); return np.eye(3)+math.sin(a)*K+(1-math.cos(a))*K@K
D=math.degrees; R_=math.radians
ts=g["law_ts"]; dKl=g["law_dK"]; kK=abs(dKl[-1]/ts[-1]); sp=float(np.sign(dKl[-1])); q2hi=float(g["q2hi"]); s_q=float(g["s_q"])
roc=g["rocker"]; Pb=roc.mean(0); dR=unit(Pb); lev=np.linalg.norm(Pb)
# model's rod (verified, corrected): rocker-top end A_m and horn end B_m
A_m=(lev+19.0+2.5)*dR
hB=fK+CROWN+capK+1.5+2.5          # rod-end centre (head mid-height) over the horn plate on the cap top
capTop=fK+CROWN+capK
# planes
x2=unit(np.cross(u2,np.cross(uK,u2)))   # in the plane _|_ u2, toward K
y2=np.cross(u2,x2)
eK=unit(np.cross(uK,np.cross(u2,uK)))   # in the plane _|_ uK, toward hub 2
fKv=np.cross(uK,eK)
axis_off=Pb-(Pb@u2)*u2                    # rocker axis (|| u2) through the model's rocker base
hL=f2+7.45                                # lobe band mid (F2+6.2 .. F2+8.7), roller centre plane
POST_EXTRA=1.0                            # post grown 19 -> 20 mm: the bell crank moves the rod end, and +1.0 restores the 1 mm rod-to-cap rule (0.87 at +0, 0.99 at +0.5, 1.10 at +1.0)
hT=Pb@u2+21.5+POST_EXTRA                  # top crank pin / rod-end mid height on the rocker
print(json.dumps(dict(f2=f2,fK=fK,lev=lev,rocker_axis_from_u2=float(np.linalg.norm(axis_off)),rocker_base_h=float(Pb@u2),hL=hL,hT=hT,hB=hB,capTop=capTop,
      A_model_vs_parallel_axis_mm=float(np.linalg.norm(A_m-(axis_off+hT*u2))))))
def run(r_h=2.493, a_f=9.0, a_c=9.0, rr=3.0, r_base=10.1, side=+1, verbose=False, label=""):
    PL=axis_off+hL*u2; PT=axis_off+hT*u2
    # follower roller centre at onset: on the circle rho0 = r_base + rr about the u2 axis, a_f from the rocker axis
    rho0=r_base+rr; d0=np.linalg.norm(axis_off)
    ang=math.acos((rho0**2+d0**2-a_f**2)/(2*rho0*d0))  # angle at the u2 axis between the rocker dir and C
    ax_dir=unit(axis_off); bx=ax_dir; by=np.cross(u2,bx)
    C0=hL*u2+rho0*(math.cos(ang)*bx+side*math.sin(ang)*by)
    rf0=unit(C0-PL)                       # follower arm direction at onset
    def C_of(beta): return PL+a_f*(rotm(u2,beta)@rf0)
    # horn / crank phases: at mid stroke, both cranks _|_ to the rod
    tmid=ts[-1]/2; dKmid=sp*kK*tmid
    # rod direction guess from the rocker top axis to the horn centre at mid
    Bc=hB*uK
    dguess=unit(Bc-PT)
    # horn arm at mid: _|_ to the rod's projection on the plane _|_ uK
    dp=unit(dguess-(dguess@uK)*uK); hm=np.cross(uK,dp)       # _|_ dp in plane
    best=None
    for sh in (+1,-1):
        h_mid=sh*hm; h0=rotm(uK,+dKmid)@h_mid                   # horn dir at stop A (link 1a turns by -dK in 1b's frame)
        def B_of(dk): return hB*uK+r_h*(rotm(uK,-dk)@h0)
        # does opening K move the horn end away from the rocker (rod pushed)?  push needs d|B-PT|/d|dK| > 0
        e1=np.linalg.norm(B_of(sp*R_(30))-PT)-np.linalg.norm(B_of(sp*R_(25))-PT)
        if e1<=0: continue
        for sc in (+1,-1):
            dpc=unit(dguess-(dguess@u2)*u2); cm=sc*np.cross(u2,dpc)
            # rocker angle beta: follower outward when ... crank dir at beta: rotm(u2,beta)@c0 ; choose c0 so crank _|_ rod at mid (beta_mid unknown -> iterate)
            c0=cm
            for it in range(6):
                def A_of(beta): return PT+a_c*(rotm(u2,beta)@c0)
                L=np.linalg.norm(A_of(0.0)-B_of(0.0))
                betas=[0.0]; ok=True
                for t in ts[1:]:
                    dk=sp*kK*t; Bt=B_of(dk); b=betas[-1]
                    for _ in range(30):
                        h=1e-6; F=np.linalg.norm(A_of(b)-Bt)-L; dF=(np.linalg.norm(A_of(b+h)-Bt)-L-F)/h
                        if abs(dF)<1e-12: ok=False; break
                        b-=F/dF
                        if abs(F)<1e-10: break
                    betas.append(b)
                betas=np.array(betas)
                bmid=np.interp(tmid,ts,betas)
                # re-centre the crank so it is _|_ the rod at mid stroke
                Am=A_of(bmid); Bm=B_of(dKmid); dr=unit(Bm-Am); dr2=unit(dr-(dr@u2)*u2); want=sc*np.cross(u2,dr2)
                cur=rotm(u2,bmid)@c0
                dphi=math.atan2(np.cross(cur,want)@u2,cur@want)
                if abs(dphi)<1e-4: break
                c0=rotm(u2,dphi)@c0
            # follower: outward motion needed for opening
            Cs=np.array([C_of(b) for b in betas]); rho=np.linalg.norm(Cs-(Cs@u2)[:,None]*u2,axis=1)
            if rho[-1]<=rho[0]: continue
            best=(sh,sc,h0,c0,betas,L,Cs,rho,A_of,B_of); break
        if best: break
    if best is None: return dict(label=label, ok=False)
    sh,sc,h0,c0,betas,L,Cs,rho,A_of,B_of=best
    q2t=q2hi+s_q*ts
    C2=np.array([rotm(u2,-q)@c for q,c in zip(q2t,Cs)])          # pitch curve in link 2's frame
    pc=C2-(C2@u2)[:,None]*u2
    a2x=bx; a2y=by
    polar=np.c_[np.degrees(np.unwrap(np.arctan2(pc@a2y,pc@a2x))),np.linalg.norm(pc,axis=1)]
    T=np.gradient(pc,axis=0); Tn=T/np.linalg.norm(T,axis=1)[:,None]
    N=np.cross(u2,Tn)                                              # in-plane normal (link 2 frame)
    # outward normal (away from the u2 axis side of the lobe = toward the follower)
    sgn=np.sign(np.einsum("ij,ij->i",N,pc)); N=N*sgn[:,None]
    prof=pc-rr*N                                                   # lobe surface (contact) points
    rprof=np.linalg.norm(prof,axis=1)
    # pressure angle: normal (back in 1b frame) vs follower velocity
    N1=np.array([rotm(u2,q)@n for q,n in zip(q2t,N)])
    V=np.array([np.cross(u2,c-PL) for c in Cs]); V=V/np.linalg.norm(V,axis=1)[:,None]
    pa=np.degrees(np.arccos(np.clip(np.abs(np.einsum("ij,ij->i",N1,V)),0,1)))
    # pitch-curve curvature radius (lobe convexity / undercut)
    ds=np.linalg.norm(np.gradient(pc,axis=0),axis=1); dT=np.linalg.norm(np.gradient(Tn,axis=0),axis=1)
    rc_pitch=ds/np.maximum(dT,1e-12)
    # moment arms (mm) and forces from the spring
    As=np.array([A_of(b) for b in betas]); Bs=np.array([B_of(sp*kK*t) for t in ts]); dr=(Bs-As)/np.linalg.norm(Bs-As,axis=1)[:,None]
    mh=np.abs(np.einsum("ij,ij->i",np.cross(Bs-hB*uK,dr),np.tile(uK,(len(ts),1))))   # rod arm about uK
    mc=np.abs(np.einsum("ij,ij->i",np.cross(As-PT,dr),np.tile(u2,(len(ts),1))))      # rod arm about the rocker axis
    mf=np.abs(np.einsum("ij,ij->i",np.cross(Cs-PL,N1),np.tile(u2,(len(ts),1))))     # contact normal arm about the rocker axis
    ml=np.abs(np.einsum("ij,ij->i",np.cross(Cs-(Cs@u2)[:,None]*u2,N1),np.tile(u2,(len(ts),1))))  # contact normal arm about u2 (lobe)
    # misalignment of the rod ends: angle between the rod and the plane _|_ the pin axis
    misK=np.degrees(np.arcsin(np.abs(dr@uK))); misR=np.degrees(np.arcsin(np.abs(dr@u2)))
    # rod vs K cap clearance over the stroke (cap: cylinder r<=10 about uK, axial 0..capTop); rod O3 (r 1.5), sampled
    def cap_clear(Pa,Pb_):
        s=np.linspace(0,1,200)[:,None]; X=Pa*(1-s)+Pb_*s; h=X@uK; r=np.linalg.norm(X-h[:,None]*uK,axis=1)
        # exclude the rod-end eye zone (within 6.5 mm of B): it sits on the horn plate by design
        far=np.linalg.norm(X-Pb_,axis=1)>6.5
        dz=h-capTop; dr_=r-HUB_R
        d=np.where((dr_<=0),dz,np.where(dz<=0,dr_,np.hypot(np.maximum(dr_,0),np.maximum(dz,0))))
        return float((d[far]-1.5).min())
    cc=np.array([cap_clear(a,b) for a,b in zip(As,Bs)])
    # roller-arm vs O20 skirt of hub 2: roller eye edge radius
    rows=dict(label=label, r_h=r_h, a_f=a_f, a_c=a_c, rr=rr, r_base=r_base, L_rod=round(float(L),2), rocker_turn_deg=round(D(abs(betas[-1])),2),
              lift_mm=round(float(rho[-1]-rho[0]),3), pitch_r=[round(float(rho[0]),2),round(float(rho[-1]),2)],
              lobe_r_onset=round(float(rprof[0]),2), lobe_r_end=round(float(rprof[-1]),2), lobe_r_at_dK44=round(float(np.interp(R_(44)/kK,ts,rprof)),2),
              lobe_arc_deg=round(float(abs(polar[-1,0]-polar[0,0])),1),
              pa_deg=[round(float(pa.min()),1),round(float(pa.max()),1)], pa_onset=round(float(pa[0]),1), pa_end=round(float(pa[-1]),1),
              rc_pitch_min=round(float(rc_pitch[2:-2].min()),2), rc_profile_min=round(float(rc_pitch[2:-2].min()-rr),2),
              horn_arm_eff=[round(float(mh.min()),3),round(float(mh.max()),3)], crank_arm_eff=[round(float(mc.min()),2),round(float(mc.max()),2)],
              follower_arm_eff=[round(float(mf.min()),2),round(float(mf.max()),2)], lobe_arm_eff=[round(float(ml.min()),2),round(float(ml.max()),2)],
              rod_misalign_deg=dict(horn=[round(float(misK.min()),1),round(float(misK.max()),1)], rocker=[round(float(misR.min()),1),round(float(misR.max()),1)]),
              rod_cap_clear_min=round(float(cc.min()),2), rod_slide_mm=round(float(np.linalg.norm(As[-1]-As[0])),2), horn_arc_chord_mm=round(float(np.linalg.norm(Bs[-1]-Bs[0])),2),
              A_end_vs_model_mm=round(float(np.linalg.norm(As[0]-A_m)),1))
    # sensitivity: K error per 0.05 mm of rod length (dK/dL) and per 0.05 mm of lobe/follower radial error
    rows["dK_per_0.05mm_rod_deg"]=[round(D(0.05/mh.max()),2),round(D(0.05/mh.min()),2)]
    # follower radial error ds_r -> rocker turn ds_r/(a_f cos) -> rod motion * mc -> dK = .. / mh
    cosf=mf/a_f                                                # share of the follower arm normal to the contact
    gain=(mc/mh)/np.maximum(np.abs(np.einsum("ij,ij->i",N1,V))*a_f,1e-9)    # dK per mm of lobe normal error
    rows["dK_per_0.05mm_lobe_deg"]=[round(D(0.05*gain.min()),2),round(D(0.05*gain.max()),2)]
    rows["_arrays"]=dict(ts=ts,polar=polar,prof=prof,pa=pa,mh=mh,mc=mc,mf=mf,ml=ml,rho=rho,rprof=rprof,betas=betas,dr=dr,As=As,Bs=Bs,Cs=Cs,N1=N1,V=V,rc=rc_pitch,gain=gain,pc=pc)
    return rows
if __name__=="__main__":
    import pickle
    out={}
    for kw in [dict(label="V0 model ratio 1, r_h 2.49, MR63 roller",r_h=2.493,a_f=9.0,a_c=9.0),
               dict(label="V0b r_h 2.49, base r 9 (model r_lobe)",r_h=2.493,a_f=9.0,a_c=9.0,r_base=9.0),
               dict(label="V0s r_h 2.49, sliding O3 nose (rr 1.5)",r_h=2.493,a_f=9.0,a_c=9.0,rr=1.5),
               dict(label="V1 r_h 4.0, ratio 1",r_h=4.0,a_f=9.0,a_c=9.0),
               dict(label="V2 r_h 4.0, crank 14.4 (ratio 1.6)",r_h=4.0,a_f=9.0,a_c=14.4),
               dict(label="V3 r_h 5.0, crank 18 (ratio 2)",r_h=5.0,a_f=9.0,a_c=18.0)]:
        for side in (+1,-1):
            r=run(side=side,**kw); r["side"]=side
            arr=r.pop("_arrays",None); out[(kw["label"],side)]=(r,arr)
            print(json.dumps(r))
    pickle.dump(out,open(SP+"/drive.pkl","wb"))

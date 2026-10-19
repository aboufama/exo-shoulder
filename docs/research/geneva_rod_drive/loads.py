import numpy as np, math, json, pickle, sys
import os
sys.path.insert(0, SP:=os.path.dirname(os.path.abspath(__file__)))
import drive as DV
g=DV.g; u1,u2,u3,uK=DV.u1,DV.u2,DV.u3,DV.uK; D=math.degrees; R_=math.radians
ts=DV.ts; dKl=DV.dKl; kK=DV.kK; sp=DV.sp
res={}
# ---------- fold margin along the law and its sensitivity to a K offset ----------
a2=float(g["a2"])
def law_th_a1e(dk_off):
    q2t=DV.q2hi+DV.s_q*ts; dk=dKl+sp*R_(dk_off)*(ts>0)
    th=[]; a1e=[]
    for q,k in zip(q2t,dk):
        RK=DV.rotm(uK,k); th.append(D(math.acos(np.clip(u1@(RK@(DV.rotm(u2,q)@u3)),-1,1)))); a1e.append(D(math.acos(np.clip(u1@(RK@u2),-1,1))))
    return np.array(th),np.array(a1e)
th0,a0=law_th_a1e(0.0); m0=np.minimum(th0-np.abs(a0-a2),np.minimum(a0+a2,360-a0-a2)-th0)
st=g["kstate"]; tk=g["taken"]; sel=tk&(st==1)
thp=np.degrees(np.arccos(np.clip((g["R1"][:,:,:]@u1)[:,None,:]@np.zeros(3),0,0))) if False else None
# taken stretched poses: their th (pose-fixed) -> margin under a K offset: interpolate the perturbed law at the pose's th
Q_th=None
camt=g["camt"]                     # deg of q2 travel past onset at each pose
th_pose=np.interp(np.radians(camt[sel]),ts,th0)
rows=[]
for off in (-2.0,-1.0,-0.5,0.0,0.5,1.0,2.0):
    th1,a1=law_th_a1e(off); m1=np.minimum(th1-np.abs(a1-a2),np.minimum(a1+a2,360-a1-a2)-th1)
    # at a fixed pose th, the perturbed chain sits where th1(t') = th (th1 monotone on the prefix)
    okm=np.all(np.diff(th1)>0)
    mp=np.interp(th_pose,th1,m1,left=np.nan,right=np.nan)
    rows.append(dict(K_offset_deg=off,law_margin_min=round(float(m1.min()),2),taken_margin_min=round(float(np.nanmin(mp)),2),
                     taken_below5=int(np.sum(mp<5.0)),taken_out_of_prefix=int(np.sum(np.isnan(mp))),monotone=bool(okm)))
res["fold"]=dict(law_margin=[round(float(m0.min()),2),round(float(m0.max()),2)],taken_margin_min=round(float(np.interp(th_pose,th0,m0).min()),2),
                 n_stretched_taken=int(sel.sum()),da1e_dK=round(float(np.gradient(a0,np.degrees(np.abs(dKl)))[5:].mean()),3),sens=rows,
                 msub_min=round(float(g["msub"][sel].min()),2),m3e_min=round(float(g["m3e"][sel].min()),2))
# ---------- gravity moment of the arm about uK (MVP2 support upper bound) ----------
mass=dict(ua=2.17,fa=1.30,ha=0.49)        # 80 kg male, de Leva shares 2.71 / 1.62 / 0.61 %
E=g["E"]; W=g["W"]; gv=np.array([0,-9.81,0])
cua=0.577*E; cfa=E+0.457*(W-E); cha=W+70.0*(W-E)/np.linalg.norm(W-E,axis=1)[:,None]
Mg=(np.cross(cua,mass["ua"]*gv)+np.cross(cfa,mass["fa"]*gv)+np.cross(cha,mass["ha"]*gv))/1000.0   # N.m about GH (thorax frame)
uKw=np.einsum("nij,j->ni",g["R1"],uK)
tauK=np.einsum("ni,ni->n",Mg,uKw)          # gravity moment about K (support moment = -Mg)
# opening sense: K opening = sp*uK rotation of link 1b vs link 1a; load on the distal side tends to open if (-Mg_support...)
# full support: chain carries M_c=-Mg; joint must supply tau_req = M_c.uK ; the load opens K when -sp*tau_req > 0
tau_req=-tauK; open_load=-sp*tau_req
res["armgrav"]=dict(Mg_max_Nm=round(float(np.linalg.norm(Mg[tk],axis=1).max()),2),
    tauK_abs_max_stretched=round(float(np.abs(tauK[sel]).max()),2),open_load_max_stretched=round(float(open_load[sel].max()),2),
    close_load_max_stretched=round(float((-open_load[sel]).max()),2),tauK_abs_max_window=round(float(np.abs(tauK[tk&(st==0)]).max()),2),
    open_load_max_window=round(float(open_load[tk&(st==0)].max()),2))
# ---------- drive forces / stresses for the build variants (side +1) ----------
out=pickle.load(open(SP+"/drive.pkl","rb"))
S0,KS=0.08,0.015                        # clock spring: preload at stop A, rate (N.m/rad) - kit-rule / judge spec
EXT=0.033                               # MVP1 opening load bound on K (judge R17: |M_GH| <= 0.033 N.m on K-closed frames, gravity of the exo)
def hertz(F,R1,R2,l,E1=208e3,n1=0.3,E2=197e3,n2=0.27):
    Es=1/((1-n1**2)/E1+(1-n2**2)/E2); R=1/(1/R1+1/R2); return math.sqrt(F*Es/(math.pi*l*R))
var={}
for key,(r,arr) in out.items():
    if r.get("side")!=1 or not r.get("ok",True): continue
    a=arr; Sp=S0+KS*np.abs(dKl)                                  # spring torque along the stroke
    for case,T in (("spring",Sp),("spring+MVP1",Sp+EXT)):
        Frod=T/(a["mh"]/1000); Fn=Frod*a["mc"]/a["mf"]; tJ2=Fn*a["ml"]/1000
        # profile curvature radius at contact (convex lobe): pitch rc - rr
        Rl=np.maximum(a["rc"]-r["rr"],0.5)
        ph=np.array([hertz(fn,r["rr"],rl,2.2) for fn,rl in zip(Fn,Rl)])
        # horn pin O3 cantilever: lever = plate 1.5 + half the eye housing 2.25 (igubal C1 4.5) -> 3.75 mm
        sig_pin=32*Frod.max()*3.75/(math.pi*3**3)
        # rocker: fixed O5 post 19 mm (17-4PH), rod force at the top (21.5 mm) + follower force at 9 mm: root moment
        Mroot=np.hypot(Frod*21.5,Fn*9.0).max()   # conservative: not vector-summed
        sig_post=32*Mroot/(math.pi*5**3); defl=Frod.max()*21.5**3/(3*197e3*math.pi*5**4/64)
        # crank arm (Ti 3 x 4 section) bending at the root: F*a_c
        sig_crank=6*Frod.max()*r["a_c"]/(3*4**2)
        var.setdefault(r["label"],{})[case]=dict(F_rod_N=[round(float(Frod.min()),1),round(float(Frod.max()),1)],F_follower_N=[round(float(Fn.min()),1),round(float(Fn.max()),1)],
            J2_reflected_Nm=[round(float(tJ2.min()),3),round(float(tJ2.max()),3)],J2_check_kK_tau=[round(float(kK*T.min()),3),round(float(kK*T.max()),3)],
            hertz_MPa=round(float(ph.max()),0),horn_pin_MPa=round(sig_pin,0),post_root_MPa=round(sig_post,0),post_top_defl_um=round(defl*1000,1),crank_root_MPa=round(sig_crank,0))
res["drive"]=var
# MVP2: K load if the exo carried the arm (full support) through K -> rod force at the horn
res["mvp2_rod_force_N_at_r_h_2.49"]=round(res["armgrav"]["open_load_max_stretched"]/0.0018,0)
json.dump(res,open(SP+"/loads.json","w"),indent=1)
print(json.dumps(res,indent=1))
# polar export of the V0 (side +1) lobe
r,a=out[("V0 model ratio 1, r_h 2.49, MR63 roller",1)]
pc=a["pc"]; prof=a["prof"]; ax=DV.unit(DV.axis_off); by=np.cross(u2,ax)
pol=np.c_[np.degrees(ts),np.degrees(np.abs(dKl)),np.degrees(np.unwrap(np.arctan2(pc@by,pc@ax))),np.linalg.norm(pc,axis=1),
          np.degrees(np.unwrap(np.arctan2(prof@by,prof@ax))),np.linalg.norm(prof,axis=1),a["pa"],np.degrees(a["betas"])]
np.savetxt(SP+"/lobe_polar_V0.csv",pol,delimiter=",",fmt="%.4f",header="t_q2_deg,K_open_deg,pitch_az_deg,pitch_r_mm,profile_az_deg,profile_r_mm,pressure_angle_deg,rocker_deg")
print(pol[::24].round(3))

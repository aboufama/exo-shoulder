"""Alignment skeptic instrument (new file, 2026-10-17): fixed-GH ARM-orientation error per mm of in-plane GH drift on
minarc-stop-knuckle-4r (pick1, BDp), the quantity the audit reported only as the knee phi twist (1.69 deg/mm).

Uses tools/alignment_knee_sensing_minarc.py (read only: closure(), coords(), the verifier params and frozen knee centre).
GH drift at fixed arm orientation turns member 3 about u3 (sn || u3 to 1e-4 deg), i.e. the J3 reading moves by
gph deg/mm with J1, K, J2 held (K on stop A or its spring, J2 on its stop). A fixed-GH estimator inverts the 4 hub rows
(J1, J2, J3, K) of the loop Jacobian and reads a GH rotation |inv(H)[:3, J3]| * gph deg/mm that did not happen.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_knee_ghdrift_minarc_skeptic.py <out.json>
"""
import sys, json, os, importlib.util, numpy as np
REPO='/home/user/exo-shoulder'; sys.path.insert(0, REPO+'/tools')
sp=importlib.util.spec_from_file_location('aksm', REPO+'/tools/alignment_knee_sensing_minarc.py'); T=importlib.util.module_from_spec(sp); sp.loader.exec_module(T)
out={}
for cfg in ['pick1','BDp']:
    P=dict(T.KR.PARAMS, **json.load(open(os.path.join(T.VER, f"v_{cfg}_fit60_bench_params.json"))))
    ct=json.load(open(os.path.join(T.VER, f"v_{cfg}_fit60_bench_conn_taken.json")))
    D=T.KR.KRDesign(dict(P)); D.m=np.array(ct["m"],float); D.m[2]=0.0
    Zg,W,POSE,HG=T.R.ws_grid(); HG=np.asarray(HG,float); _=D.ik(HG[:2])
    keys={tuple(round(float(x),1) for x in k) for k in ct["connected_keys"]}
    gsel=np.array([(round(float(p[0]),1),round(float(p[1]),1),round(float(p[2]),1)) in keys for p in POSE])
    Qs=HG; h=1e-4
    q0,ok0,X10,X20,X30,s0=D.ik(Qs); dK0=np.asarray(D._dK,float).copy(); st=np.asarray(D._state).copy()
    E=np.eye(3); cols=[]
    for k in range(3):
        cp=[]
        for sg in (1,-1):
            Qp=np.einsum("ij,njk->nik", T.rotv(sg*h*E[k]), Qs); qp,X2p,spp,_=T.closure(D,Qp,dK0); cp.append(T.coords(D,Qp,qp,X2p,spp,dK0)[0])
        cols.append(T.wrap(cp[0]-cp[1])/(2*h))
    cp=[]
    for sg in (1,-1):
        qp,X2p,spp,dKu=T.closure(D,Qs,dK0+sg*h); cp.append(T.coords(D,Qs,qp,X2p,spp,dKu)[0])
    cols.append(T.wrap(cp[0]-cp[1])/(2*h))
    Z=np.stack(cols,2)          # n,6,4 rows J1,J2,J3,K,qa,qb ; cols GHx,GHy,GHz,dK
    hs=0.01; gph=np.zeros(len(Qs)); 
    for a in range(2):
        dv=np.zeros(3); dv[a]=hs
        Kp=D.knee(s0+dv); Km=D.knee(s0-dv); gph+= (T.wrap(np.asarray(Kp["phi"])-np.asarray(Km["phi"]))/(2*hs))**2
    gph=np.degrees(np.sqrt(gph))
    G=np.full(len(Qs),np.nan)
    for i in range(len(Qs)):
        if not gsel[i]: continue
        Hm=Z[i][:4]; 
        try: inv=np.linalg.inv(Hm)
        except Exception: continue
        G[i]=np.linalg.norm(inv[:3,2])        # GH rotation the estimator infers per unit J3 reading change
    err=G*gph
    sel=gsel&np.isfinite(err)
    r=dict(n=int(sel.sum()), J3_to_arm_gain=[round(float(np.nanmin(G[sel])),3),round(float(np.nanmedian(G[sel])),3),round(float(np.nanmax(G[sel])),3)],
           knee_phi_deg_per_mm=[round(float(gph[sel].min()),3),round(float(np.median(gph[sel])),3),round(float(gph[sel].max()),3)],
           arm_est_err_deg_per_mm=[round(float(err[sel].min()),3),round(float(np.median(err[sel])),3),round(float(err[sel].max()),3)],
           overhead140_arm_est_err_max=round(float(err[sel&(POSE[:,1]>=140)].max()),3),
           at_4mm_max_deg=round(float(4*err[sel].max()),2))
    out[cfg]=r; print(cfg, r)
json.dump(out, open(sys.argv[1],'w'), indent=1)

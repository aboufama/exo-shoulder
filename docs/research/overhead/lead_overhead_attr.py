# Round 301 (overhead track) planner: per-pose attribution of the lead conecut-knee-knuckle-3r on the 28 overhead (ws, elev >= 140) poses of frozen exact Bench(110,360).
# Usage: OMP_NUM_THREADS=1 nice python3 docs/research/overhead/lead_overhead_attr.py <out.json>  (reproduces why fold 88 / contact 4; ~5 min exact)
import os, sys, json, importlib.util, numpy as np
REPO="/home/user/exo-shoulder"
sys.path.insert(0, REPO+"/tools")
sp=importlib.util.spec_from_file_location("vck", REPO+"/docs/concepts/verify/conecut-knee-knuckle-3r.py"); V=importlib.util.module_from_spec(sp); sp.loader.exec_module(V)
P=dict(V.BEST); V.retarget(P)
fit,M1,M,B,r=V.CC._frozen_model(dict(P),110,360)
n=len(B.idx)
attrs={}
for a in dir(M):
    if a.startswith("__"): continue
    try: v=getattr(M,a)
    except Exception: continue
    if isinstance(v,np.ndarray) and v.shape[:1]==(n,): attrs[a]=v.shape
for a in dir(M.D):
    if a.startswith("__"): continue
    try: v=getattr(M.D,a)
    except Exception: continue
    if isinstance(v,np.ndarray) and v.shape[:1]==(n,): attrs["D."+a]=v.shape
print("ATTRS", attrs)
print("why", r.get("why"))
ws=np.array(B.kind)=="ws"; el=np.array([B.poses[j]["elev"] for j in range(n)])
mins=np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(n)])
ov=np.nonzero(ws&(el>=140))[0]
pp=getattr(M,"p",{})
print("a1a2", {k:pp.get(k) for k in ("a1","a2","b1","b2","b3","bvec","J3MIN","J3MAX")})
rows=[]
for j in ov:
    d=dict(i=int(j), plane=B.poses[j]["plane"], elev=B.poses[j]["elev"], axial=B.poses[j]["axial"], min_mm=None if np.isnan(mins[j]) else round(float(mins[j]),2))
    for a in attrs:
        try:
            v=(getattr(M.D,a[2:]) if a.startswith("D.") else getattr(M,a))[j]
            if np.ndim(v)==0: d[a]=round(float(v),2) if np.issubdtype(np.asarray(v).dtype,np.number) else v
        except Exception: pass
    rows.append(d)
json.dump(dict(why=r.get("why"),rows=rows,attrs={k:list(v) for k,v in attrs.items()}), open(sys.argv[1],"w"), default=float, indent=0)
for d in rows: print(json.dumps(d, default=float))

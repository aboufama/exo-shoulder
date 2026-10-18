"""no-knee control for crest-knee-3r: crest-knee's verified seats (J1, J2 home, J3 seat ray) as a plain GH-concentric 3R
through deltoid-crest-j3-3r's build (zc-frontier checks), stack orders probed on Bench(60,160) fast, best worn frozen exact"""
import importlib.util, json, os, sys, numpy as np
REPO="/home/user/exo-shoulder"; sys.path.insert(0, REPO+"/tools")
sp=importlib.util.spec_from_file_location("dc", REPO+"/docs/concepts/models/deltoid-crest-j3-3r.py"); DC=importlib.util.module_from_spec(sp); sys.modules["dc"]=DC; sp.loader.exec_module(DC)
ZC=DC.ZC; K=ZC.K
OUT=sys.argv[1]
r=json.load(open(REPO+"/docs/concepts/rows/crest-knee-3r.json")); bp=r["best_params"]
d0=K.bvec(bp["az1"],bp["el1"]); d1=K.bvec(bp["az2"],bp["el2"])
P2=np.array([-16.88065319, 3.18603888, 57.47328969]); d2=P2/np.linalg.norm(P2)   # crest-knee D.seats['P'][2] (J3 seat ray, scapula frame at rest)
ang=lambda a,b: float(np.degrees(np.arccos(np.clip(np.dot(a,b),-1,1))))
a1=ang(d0,d1); a2=ang(d1,d2); sig=1 if np.dot(d1,np.cross(d0,d2))>=0 else -1
print("a1 %.3f a2 %.3f sigma %d  th_rest %.2f" % (a1,a2,sig,ang(d0,d2)), flush=True)
DC.snap = lambda p: dict(ZC.snap(dict(DC.PARAMS, **p)), in_box=True)   # no crest-box clamp (J3 wd 93.04 sits below its 95 edge)
base=dict(az=bp["az1"], el=bp["el1"], a1=a1, a2=a2, wd=bp["wd"], wa=bp["wa"], sigma=sig, q=0.9572, end_extra=2.9522)
B=K.bench(60,160); res=[]
for inv2 in (0,1):
  for inv3 in (0,1):
    for ee in (2.9522, 8.0):
      p=dict(base, inv2=inv2, inv3=inv3, end_extra=ee); pp,rr=DC.evaluate(B,p)
      row=dict(params={k:pp[k] for k in ("az","el","a1","a2","wd","wa","sigma","inv2","inv3","q","end_extra")}, **{k:rr.get(k) for k in ("gap","near","reach","follow","inband14","inband10","contact","honest","hub_F","inband_member")})
      res.append(row); print(json.dumps(row, default=float), flush=True)
      json.dump(dict(a1=a1,a2=a2,sigma=sig,fast=res), open(OUT,"w"), indent=1, default=float)
best=min(res, key=lambda e: e["gap"])
print("best fast", best["gap"], best["params"], flush=True)
fz=DC.frozen(dict(best["params"]), OUT.replace(".json","_frozen.json"))
json.dump(dict(a1=a1,a2=a2,sigma=sig,fast=res,frozen=dict(wear=fz.get("wear",{}).get("v") if isinstance(fz.get("wear",{}).get("v"),dict) else {k:fz["wear"].get(k) for k in ("gap","reach","follow","inband14","inband10","contact","near")}, score=fz.get("score"), attribution=fz.get("wear_attribution"))), open(OUT,"w"), indent=1, default=float)

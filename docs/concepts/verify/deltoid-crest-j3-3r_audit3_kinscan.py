"""Death re-audit (round 14, 2026-10-18 08:3x UTC): kinematic closure (fold law, margin 5) on Bench(110,360) ws vs Bench(60,160) ws for every honest distinct sweep config"""
import importlib.util, json, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
spec = importlib.util.spec_from_file_location("dcm", os.path.join(REPO, "docs/concepts/models/deltoid-crest-j3-3r.py"))
DC = importlib.util.module_from_spec(spec); sys.modules["dcm"] = DC; spec.loader.exec_module(DC)
ZC, K = DC.ZC, DC.K
t = time.time()
Bs = K.bench(60, 160); Fs = K.frames(Bs)
Bb = K.bench(110, 360); Fb = K.frames(Bb)
print("benches", round(time.time() - t, 1), flush=True)
wss = np.array([k == "ws" for k in Bs.kind]); wsb = np.array([k == "ws" for k in Bb.kind])
elb = np.array([q["elev"] for q in Bb.poses])
s = json.load(open(os.path.join(REPO, "docs/concepts/sweeps/deltoid-crest-j3-3r.json")))
rows = []; seen = set()
for i, r in enumerate(s):
    g = r.get("gap")
    if g is None or g >= 100: continue
    p = DC.snap(r["params"]); p.pop("in_box")
    key = tuple(round(float(p[k]), 1) for k in ("az", "el", "a1", "a2", "wd", "wa")) + (p["sigma"],)
    if key in seen: continue
    seen.add(key)
    ks = ZC.kin(Fs, p)[wss].mean(); kb = ZC.kin(Fb, p)
    rows.append(dict(i=i, gap=g, kin160=round(float(ks), 4), kin360=round(float(kb[wsb].mean()), 4),
                     kin_ov=round(float(kb[wsb & (elb >= 140)].mean()), 3), hub2F=(r.get("hub_F") or {}).get("hub2"),
                     ib2=(r.get("inband_member") or {}).get("hub2"), ib14=r.get("inband14"), reach=r.get("reach"),
                     p={k: p[k] for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "inv2", "inv3", "q", "end_extra")}))
print("distinct honest", len(rows), round(time.time() - t, 1), flush=True)
json.dump(rows, open(sys.argv[1], "w"), default=float)
rows.sort(key=lambda r: -r["kin360"])
print("top kin360:")
for r in rows[:15]: print(r["kin360"], r["kin160"], r["kin_ov"], r["gap"], r["hub2F"], r["ib2"], r["ib14"], r["p"])
good = [r for r in rows if (r["ib2"] or 0) >= 0.8 and (r["ib14"] or 0) >= 0.85]
good.sort(key=lambda r: -r["kin360"])
print("top kin360 with hub2 in band >= 0.8 and ib14 >= 0.85:", len(good))
for r in good[:15]: print(r["kin360"], r["kin160"], r["kin_ov"], r["gap"], r["hub2F"], r["ib2"], r["ib14"], r["p"])
b = min(rows, key=lambda r: r["gap"]); print("fast best", b["kin360"], b["kin160"], b["gap"])

# Skeptic probe (alignment audit of conecut-knee-knuckle-3r, 2026-10-17): which kinematic label (fold / slide / j3stop)
# removes chosen held poses from the score, under the frozen protocol. Usage: python3 tools/alignment_skeptic_why_labels.py lead|stop|nostop
# kinematic 'why' labels on the HELD bench under the frozen protocol (fit on Bench(60,160) fast, then the frozen drive
# m_fix): lead slipper-nose and conecut with / without its J3 stop. Models unchanged; labels only (no metal run).
import os, sys, json, time, importlib.util
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
import numpy as np
def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
which = sys.argv[1]; t = time.time()
import concept_bench as CB
if which == "lead":
    MOD = load("sn_skf", os.path.join(REPO, "docs/concepts/models/slipper-nose-knuckle-3r.py")); Cls = MOD.SNModel
    P = json.load(open(os.path.join(REPO, "docs/alignment/remeasure/slipper-nose-knuckle-3r_held.json")))["params"]
else:
    MOD = load("cc_skf", os.path.join(REPO, "docs/concepts/models/conecut-knee-knuckle-3r.py")); Cls = MOD.CCModel
    P = json.load(open(os.path.join(REPO, "docs/alignment/remeasure/conecut-knee-knuckle-3r_held.json")))["params"]
P = MOD._clamp(dict(MOD.PARAMS, **P))
os.environ.pop("CB_EXACT", None); B1 = CB.Bench(n_clip=60, n_ws=160)
M1 = Cls(B1, dict(P)); r1 = M1.run(); print("fit", which, r1["gap"], round(time.time() - t, 1), flush=True)
P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
if which == "nostop": P2.update(J3MIN=-180.0, J3MAX=999.0)
os.environ["CB_EXACT"] = "1"
PV = load("pv_skf", os.path.join(REPO, "docs/concepts/verify/skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
M = Cls(B, P2); w = np.asarray(M.why)
POSES = [392, 530, 752, 897, 965]
out = dict(which=which, protocol="frozen labels: fit Bench(60,160) fast, m_fix, held bench", fit_gap=r1["gap"], secs=round(time.time() - t, 1),
           counts={k: int((w == k).sum()) for k in set(w.tolist())},
           poses={int(i): dict(why=str(w[i]), ws=[B.poses[i][k] for k in ("plane", "elev", "axial")]) for i in POSES})
if hasattr(M, "q3p"): out["q3p"] = {int(i): round(float(M.q3p[i]), 2) for i in POSES}
print(json.dumps(out, default=float))

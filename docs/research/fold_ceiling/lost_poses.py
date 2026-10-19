"""fold-ceiling step 1: characterise the lost fold poses of a knuckle leader from the RAW per-pose data.

Fits the leader's verified params on Bench(60,160) fast (the frozen protocol's fit), then runs the fitted design's own IK
(D.ik: law + K + knee + slide tolerance, + the drive's dK_lim) on every Bench(110,360) pose and every held-out pose, and
joins the per-pose verdicts of the verified per-pose dumps (docs/alignment/remeasure/<id>_{bench,held}_perpose_claim.json).
Per pose: plane / elev / axial, th = angle(J1, J3), the dyad walls, which wall a lost pose hits, a1e / dK, taken.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/lost_poses.py [roller-longdyad-knuckle-3r] > out
"""
import importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB  # noqa: E402

ID = sys.argv[1] if len(sys.argv) > 1 else "roller-longdyad-knuckle-3r"
sp = importlib.util.spec_from_file_location("lead_model", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
MOD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MOD)
pv = importlib.util.spec_from_file_location("pkpol", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
PV = importlib.util.module_from_spec(pv); pv.loader.exec_module(PV)

claim_b = json.load(open(os.path.join(REPO, "docs", "alignment", "remeasure", f"{ID}_bench_perpose_claim.json")))
claim_h = json.load(open(os.path.join(REPO, "docs", "alignment", "remeasure", f"{ID}_held_perpose_claim.json")))
P = MOD._clamp(dict(MOD.PARAMS, **claim_b["params"]))
B1 = CB.Bench(n_clip=60, n_ws=160); r1, M1 = MOD._report(B1, P); D = M1.D
lim = math.degrees(float(M1._scg["dK_lim"])) if getattr(M1, "_scg", None) else 999.0
Z = CB._poses_all()


def per_pose(B, claim):
    Q = Z["HG"][B.idx].astype(float); k = np.array(B.kind)
    q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s)
    dK = np.degrees(np.abs(np.asarray(D._dK, float))); a1e = np.asarray(D._a1e, float); st = np.asarray(D._state)
    msub = np.asarray(D._msub, float)
    th = np.degrees(np.arccos(np.clip((Q @ D.u[2]) @ D.u[0], -1, 1)))
    a1, a2, amax = D.a1, D.a2, float(D.p["a1max"]); m = 5.0
    lo, hi_stop = abs(a1 - a2) + m, min(amax + a2, 360 - amax - a2) - m
    slide = np.abs(s[:, 2]) <= float(D.p["R_tol"])
    rows = []
    taken = {e["i"]: e for e in claim["poses"]}
    for i in range(len(B.idx)):
        e = taken.get(i, {}); po = B.poses[i]
        assert not e or (abs(e["plane"] - po["plane"]) < 1e-3 and abs(e["elev"] - po["elev"]) < 1e-3), (i, e, po)
        if th[i] < lo: wall = "folded"
        elif th[i] > hi_stop: wall = "stretched_stopB"
        elif not ok[i]: wall = "stretched_law" if th[i] > (a1 + a2 - m) else "closure_other"
        elif dK[i] > lim + 1e-6: wall = "stretched_drive"
        elif not Kn["ok"][i]: wall = "knee"
        elif not slide[i]: wall = "slide"
        else: wall = "in_window"
        rows.append(dict(i=i, kind=k[i], plane=round(po["plane"], 2), elev=round(po["elev"], 2), axial=round(po["axial"], 2),
                         th=round(float(th[i]), 2), a1e=round(float(a1e[i]), 2) if np.isfinite(a1e[i]) else None,
                         dK=round(float(dK[i]), 2) if np.isfinite(dK[i]) else None, state=int(st[i]), msub=round(float(msub[i]), 2),
                         wall=wall, taken=bool(e.get("taken", False)), min_mm=e.get("min_mm"), contact=e.get("contact")))
    return rows


out = dict(id=ID, params=claim_b["params"], a1=round(D.a1, 3), a2=round(D.a2, 3), a1max=float(D.p["a1max"]), dK_lim=round(lim, 2),
           u1=D.u[0].tolist(), u2=D.u[1].tolist(), u3=D.u[2].tolist(), uK=getattr(D, "uK", np.zeros(3)).tolist(),
           window=[round(abs(D.a1 - D.a2) + 5, 2), round(float(D.p["a1max"]) + D.a2 - 5, 2)],
           fit_fast={k: r1[k] for k in ("gap", "reach", "follow", "inband14", "contact")},
           bench=per_pose(CB.Bench(n_clip=110, n_ws=360), claim_b), held=per_pose(PV.held_bench(), claim_h))
json.dump(out, open(os.path.join(HERE, f"lost_poses_{ID}.json"), "w"), indent=0)
for nm in ("bench", "held"):
    R = [r for r in out[nm] if r["kind"] == "ws"]
    from collections import Counter
    print(nm, "ws", len(R), "taken", sum(r["taken"] for r in R), "lost by wall", Counter(r["wall"] for r in R if not r["taken"]))
print("a1 a2 a1max dK_lim window", out["a1"], out["a2"], out["a1max"], out["dK_lim"], out["window"])

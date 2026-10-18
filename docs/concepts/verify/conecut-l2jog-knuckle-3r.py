"""Independent verifier of conecut-l2jog-knuckle-3r (red team: the waist is not a cut).

The claim's WAIST moves link 2's underside samples in the plate plane and keeps each row's height. Link 2 is a kit `free`
member (skin-fitted underside per sample); at the binder (pose 139, sample 13) its section is not straight: rows 0-3 sit at
r 69.55 / 68.43 / 68.86 / 69.20 mm from GH, the edge row 0 the HIGHEST. Carrying row 0's height 1.58 mm inward puts the new
edge up to 0.95 mm ABOVE the original underside there: a hidden local radial lift. A real planform cut (the claim's own
build: a profile cut before bending, cx +0) leaves the new edge ON the original underside. TRUE CUT here: every moved sample
is placed on the original section polyline (4 rows interpolated at its station) at its new across-bar position.

    scan:   CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 <this> scan <bench|held> <scan cache .pkl> <out.json>
            (the claim's own Scan harness, frozen chain worn once, link 2 re-read within 4 mm; rows: control, waist as
             modelled, waist true cut, spec jog as modelled, spec jog true cut)
    frozen: CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 <this> frozen <bench|held> <out perpose.json>
            (the claim's frozen() unchanged, the true-cut waist always on, + a tools/alignment_paired.py-style per-pose dump)
"""

import importlib.util, json, math, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"
sp = importlib.util.spec_from_file_location("l2jog_v", os.path.join(REPO, "docs/concepts/models/conecut-l2jog-knuckle-3r.py"))
L = importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
orig = L.jog_disp

def true_disp(X, rows, P, fr=None):
    fr = fr or L.jog_frame(X, rows)
    D, info = orig(X, rows, P, fr)
    if not P.get("truecut"): return D, info
    cut = np.cumsum([0] + list(rows)); xb, w, a = fr["xb"], fr["w"], fr["a"]; s = fr["s"]
    R = [(X[cut[q]:cut[q + 1]], s[cut[q]:cut[q + 1]]) for q in range(len(rows))]
    Dt = np.zeros_like(D); lift = []
    for i in np.nonzero(np.linalg.norm(D, axis=1) > 1e-9)[0]:
        st = s[i] + float(D[i] @ a)
        Q = np.array([[np.interp(st, sr, Xr[:, j]) for j in range(3)] for Xr, sr in R])     # the original section at station st
        yq = (Q - xb) @ w; o = np.argsort(yq); yq, Q = yq[o], Q[o]
        yn = float((X[i] + D[i] - xb) @ w)
        k = int(np.clip(np.searchsorted(yq, yn) - 1, 0, len(yq) - 2))
        t = (yn - yq[k]) / (yq[k + 1] - yq[k]); Pt = Q[k] + t * (Q[k + 1] - Q[k])
        Dt[i] = Pt - X[i]; lift.append(float((X[i] + D[i] - Pt) @ fr["n"]))
    info = dict(info, truecut=True, model_lift_mm=[round(min(lift), 3), round(max(lift), 3)] if lift else None)
    return Dt, info



def _truecut_always(X, rows, P, fr=None): return true_disp(X, rows, dict(P, truecut=1), fr)


def scan_mode(bench, cache, outp):
    W = dict(dl=1.6, Lf=20.0, T=9.6906, cs=4.6906, rot=3.3949, sgn=1, ff=0.0, dz=0.0)
    J = dict(dl=1.6, Lf=20.0, T=6.2842, cs=1.2842, rot=-2.3611, sgn=1, ff=1.0, dz=0.0)
    SC_ = L.Scan(bench, cache=cache)
    plist = [dict(dl=0.0, dz=0.0), dict(W), dict(W, truecut=1), dict(J), dict(J, truecut=1)]
    names = ["control", "waist_model", "waist_truecut", "jog_model", "jog_truecut"]
    outs = SC_.read_many([dict(L._clamp(dict(L.PARAMS, **P)), truecut=P.get("truecut", 0)) for P in plist])
    res = {}
    for nm, o in zip(names, outs):
        pm = o["pose_min"]
        worst = sorted(((v, k) for k, v in pm.items()), key=lambda t: t[0])[:8]
        res[nm] = dict(gap=o["gap"], reach=o["reach"], contact=o["contact"], near1=o["near1"], p01=o["gap_probe0.1"], p02=o["gap_probe0.2"],
                       p035=o["gap_probe0.35"], l2min=o["l2_min_taken"], jog={k: o["jog"].get(k) for k in ("width_mm", "narrowing_mm", "s_span", "model_lift_mm", "truecut")},
                       watch={str(k): pm.get(k) for k in (139, 224, 225, 252, 345, 898, 458, 150) if k in pm}, worst=[(int(k), v) for v, k in worst],
                       l2={str(k): o["l2"].get(k) for k in (139, 224, 225, 252, 898) if k in o["l2"]})
        print(nm, json.dumps(res[nm], default=float))
    json.dump(dict(bench=bench, mode=SC_.B.mode, n_near=len(SC_.poses), rows=res), open(outp, "w"), indent=1, default=float)


def frozen_mode(wear, outp):
    L.jog_disp = _truecut_always
    import alignment_paired as AP
    row = json.load(open(os.path.join(REPO, "docs/concepts/rows/conecut-l2jog-knuckle-3r.json"))); P = dict(row["best_params"])
    box = {}; orig = L.PK.audit
    def wrapped(M, B):
        a = orig(M, B); box["poses"] = AP._dump_bench(M, B); box["report"] = B.report(); box["jog"] = getattr(M, "_jog_info", None); return a
    L.PK.audit = wrapped; t = time.time()
    r = L.frozen_bench(P) if wear == "bench" else L.frozen_held(P)
    L.PK.audit = orig
    res = dict(id="conecut-l2jog-knuckle-3r+truecut", wear=wear, params=P, frozen=r.get("frozen"), report=box.get("report"), poses=box.get("poses"),
               recomputed=AP.gap_parts(box.get("poses") or []), jog=box.get("jog"), why=r.get("why"), contacts=r.get("contact_poses"),
               audit={k: r.get("audit", {}).get(k) for k in ("gap_near1", "gap_near2", "near_touch_min_mm")}, secs=round(time.time() - t, 1),
               exact=os.environ.get("CB_EXACT") == "1")
    json.dump(res, open(outp, "w"), default=float)
    print(json.dumps({k: res[k] for k in ("wear", "frozen", "recomputed", "jog", "why", "audit", "secs")}, default=float))

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(REPO, "tools"))
    if sys.argv[1] == "scan":
        L.jog_disp = true_disp; scan_mode(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        frozen_mode(sys.argv[2], sys.argv[3])

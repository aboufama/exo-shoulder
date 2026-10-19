"""Alignment continuity flood for kit-built plain 3R claims (S5 static islands), from the claim's per-pose dump.

The design's own verifier (docs/concepts/verify/<id>-skeptic.py) carries the flood (extras(): kNN-8 edges by frame
angle, 2-deg slerp, closure at the 5-deg margin at every step, no joint axis stepping > 10 deg, seeds = taken poses at
the lowest elevation). This tool runs that verifier function UNCHANGED on the claim's taken set as dumped per pose
(docs/alignment/remeasure/<id>_<wear>_perpose.json): the flood is pure kinematics (frames + closure), so no skin
evaluation is redone. The dump's pose order is checked against the rebuilt bench before anything is read.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_kit_flood.py <id> bench|held [--perpose PATH] [--out PATH]
        -> docs/alignment/remeasure/<id>_<wear>_flood.json
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def run(rid, wear, perpose=None, out=None):
    dpath = perpose or os.path.join(AA.REM, f"{rid}_{wear}_perpose.json"); d = json.load(open(dpath))
    V = _load("akf_v_" + rid.replace("-", "_"), os.path.join(AA.VERIFY, rid + "-skeptic.py"))
    ZC, K = V.ZC, V.K
    p = ZC.snap(dict(d["params"])); t0 = time.time()
    B = K.bench(110, 360) if wear == "bench" else V.held_bench(110, 360)
    P = d["poses"]
    if len(P) != len(B.idx): raise SystemExit(f"dump has {len(P)} poses, bench {len(B.idx)}")
    for i, q in enumerate(P):
        b = B.poses[i]
        if q["kind"] != B.kind[i] or any(abs(float(q[k]) - float(b[k])) > 1e-3 for k in ("plane", "elev", "axial")):
            raise SystemExit(f"pose {i} differs between dump and bench: {q} vs {b}")
    F = K.frames(B); B._kitF = F
    B._kit_last = dict(chain=ZC.build(B, F, p))
    B.res = [None if not q["ev"] or q["min_mm"] is None else np.array([float(q["min_mm"])]) for q in P]
    ex = V.extras(B, p)
    fl = ex["flood"]; n_ws = sum(1 for k in B.kind if k == "ws")
    res = dict(id=rid, wear=wear, perpose=os.path.relpath(dpath, REPO), params=p, dump_gap=(d.get("recomputed") or {}).get("gap"),
               th_margin_min_taken=ex["th_margin_min_taken"], th_taken_range=ex["th_taken_range"], flood=fl,
               reach_static=fl["reach_static"], reach_connected=fl["reach_connected"],
               lost_points=round(100 * (max(0.0, .9 - fl["reach_connected"]) - max(0.0, .9 - fl["reach_static"])), 2),
               n_ws=n_ws, secs=round(time.time() - t0, 1), git=AA._git("rev-parse", "--short", "HEAD"),
               method=f"verifier extras() unchanged ({rid}-skeptic.py): kNN-8 by frame angle, 2-deg slerp, closure at the 5-deg margin, "
                      "axis step <= 10 deg; taken set from the per-pose dump")
    path = out or os.path.join(AA.REM, f"{rid}_{wear}_flood.json")
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k not in ("params", "flood")}, default=float),
          json.dumps({k: v for k, v in fl.items() if k != "island_poses"}), fl.get("island_poses"))
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    run(a[0], a[1], a[a.index("--perpose") + 1] if "--perpose" in a else None, a[a.index("--out") + 1] if "--out" in a else None)

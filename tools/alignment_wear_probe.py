"""Alignment probe (read-only on every claim): wear a verified / claimed frozen shape through its OWN verifier harness
(unchanged), capture the worn Bench(110,360) exact per-pose metal distances, and report what the score does NOT see.

The bench's gap reads in-band 2-14 over the CLIP frames only (tools/concept_bench.py report(): `taken = [j for j in cl
if ok(j)]`); the 360 workspace poses count only for reach / contact. So a taken workspace pose (overhead included) can
carry metal at any standoff - 20, 30 mm - at no cost. This probe measures, on the same worn bench:
  * in-band14 / in-band10 over the TAKEN WORKSPACE poses (all, and overhead elev >= 140) - unscored;
  * standoff: share of metal samples > 14 mm and > 20 mm, p95 / max distance, per kind;
  * the clearance floor: taken poses whose lowest metal (incl. the model's walls / crowns, M.cmin) is < 1 / 2 / 3 mm,
    split clip / ws / overhead;
  * reach by elevation band.
It changes no score, no judge and no model; it only reads the bench after the verifier's own frozen_wear ran.

    CB_EXACT=1 nice python3 tools/alignment_wear_probe.py <longdyad|parallelogram|frontload> <out.json>
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

VER = os.path.join(REPO, "docs", "concepts", "verify")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def _capture(pk_mod):
    cap = []; orig = pk_mod.audit
    def wrapped(M, B):
        cap.append((M, B)); return orig(M, B)
    pk_mod.audit = wrapped
    return cap


def analyse(M, B):
    kind = np.array(B.kind); el = np.array([p["elev"] for p in B.poses])
    cmin = getattr(M, "cmin", {}) or {}
    ok = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= 0.0
    out = {"n": len(B.idx), "mode": B.mode, "scored": {k: v for k, v in B.report().items() if k != "poses"}}

    def block(sel, name):
        tk = [j for j in sel if ok(j)]
        if not tk: out[name] = dict(n=len(sel), taken=0); return
        d = np.concatenate([B.res[j] for j in tk])
        lo = np.array([min(float(np.min(B.res[j])), float(cmin.get(j, 1e9))) for j in tk])
        p95 = np.array([float(np.percentile(B.res[j], 95)) for j in tk])
        out[name] = dict(n=len(sel), taken=len(tk), share_taken=round(len(tk) / max(1, len(sel)), 4),
                         inband14=round(float(((d >= 2) & (d <= 14)).mean()), 4), inband10=round(float(((d >= 2) & (d <= 10)).mean()), 4),
                         below2=round(float((d < 2).mean()), 4), over14=round(float((d > 14).mean()), 4), over20=round(float((d > 20).mean()), 4),
                         d_median=round(float(np.median(d)), 2), d_p95=round(float(np.percentile(d, 95)), 2), d_max=round(float(d.max()), 2),
                         pose_p95_median=round(float(np.median(p95)), 2), pose_p95_max=round(float(p95.max()), 2),
                         poses_floor_lt1=int((lo < 1).sum()), poses_floor_lt2=int((lo < 2).sum()), poses_floor_lt3=int((lo < 3).sum()),
                         share_floor_lt2=round(float((lo < 2).mean()), 4),
                         floor_hist_mm={f"{a}-{b}": int(((lo >= a) & (lo < b)).sum()) for a, b in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 6), (6, 10), (10, 99))})
    allj = np.arange(len(B.idx))
    block(allj[kind == "clip"], "clip_scored")
    block(allj[kind == "ws"], "ws_unscored")
    block(allj[(kind == "ws") & (el >= 140)], "ws_overhead140")
    block(allj[(kind == "clip") & (el >= 140)], "clip_overhead140")
    block(allj[(kind == "ws") & (el >= 90) & (el < 140)], "ws_elev90_140")
    block(allj[(kind == "ws") & (el < 90)], "ws_below90")
    bands = {}
    for lo_, hi_ in ((0, 60), (60, 90), (90, 120), (120, 140), (140, 160), (160, 200)):
        s = allj[(kind == "ws") & (el >= lo_) & (el < hi_)]
        if len(s): bands[f"{lo_}-{hi_}"] = [int(sum(ok(j) for j in s)), int(len(s))]
    out["ws_reach_by_elev"] = bands
    con = [j for j in allj if B.res[j] is not None and float(np.min(B.res[j])) < 0]
    out["contact_poses"] = sorted([dict(mm=round(float(np.min(B.res[j])), 2), kind=B.kind[j], plane=B.poses[j]["plane"], elev=B.poses[j]["elev"],
                                        axial=B.poses[j]["axial"]) for j in con], key=lambda r: r["mm"])
    why = getattr(M, "why", None)
    if why is not None:
        ws_oh = allj[(kind == "ws") & (el >= 140)]
        out["ws_overhead_why_not"] = {k: int(sum(1 for j in ws_oh if not ok(j) and why[j] == k)) for k in set(why[j] for j in ws_oh if not ok(j))}
    return out


def run(which):
    if which in ("longdyad", "parallelogram"):
        if which == "longdyad":
            V = _load("al_v_longdyad", os.path.join(VER, "sidecar-longdyad-knuckle-3r.py")); P = dict(V.BEST)
        else:
            W = _load("al_v_pg", os.path.join(VER, "sidecar-parallelogram-knuckle-3r.py")); V = W.V; P = W.PG._prep(dict(W.BEST))
        cap = _capture(V.PK); out = V.frozen_wear(P, "bench", False)
    elif which == "frontload":
        V = _load("al_v_frontload", os.path.join(VER, "frontload-lobe-stopb-knuckle-3r.py")); cap = _capture(V.PK)
        out = V.frozen_wear(V.CorrModel, dict(V.BEST), "bench", False)
    else:
        raise SystemExit("unknown design " + which)
    M, B = cap[-1]
    res = dict(design=which, verifier_frozen=out["frozen"], verifier_audit_near=dict(near1=out["audit"].get("gap_near1"), near2=out["audit"].get("gap_near2"),
               near2_poses=out["audit"].get("near2_poses"), min_mm=out["audit"].get("near_touch_min_mm")), probe=analyse(M, B))
    return res


if __name__ == "__main__":
    t = time.time(); r = run(sys.argv[1]); r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
    json.dump(r, open(sys.argv[2], "w"), indent=1, default=float); print(json.dumps(r, default=float))

"""Adapter: run tools/alignment_wear_probe.py's analyse() on ANY model whose frozen() / frozen_held() ends in a
pin-knee-style PK.audit(M, B) (the knuckle / sidecar / roller-flank families), straight from the model file and the
row's best_params. The model runs UNCHANGED: only PK.audit is wrapped to capture the worn (M, B).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_wear_probe_model.py <id> <bench|held> <out.json>
"""
import json, math, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_wear_probe as W                              # noqa: E402


# the own-state J1-J3 fold margin in the th metric over taken poses (a copy of tools/sidecar_env_polish.py th_margin, which
# follows docs/concepts/verify/minarc-bdp-remeasure.py checks_B; copied so that no polish module is imported)
def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def th_margin(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; a1, a2 = math.degrees(D.a1) if D.a1 < 4 else D.a1, math.degrees(D.a2) if D.a2 < 4 else D.a2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; rows = []
    dK = np.asarray(M.dK, float)
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        m_plain = _dm(th, a1, a2); m_eff = _dm(th, a1e, a2e); m_sub = _dm(th, b1, c)
        rows.append((min(m_sub, m_eff) if forced else m_plain, forced, m_plain, m_eff, m_sub, i, th))
    if not rows: return dict(min=None, n=0)
    own = [r[0] for r in rows]; lo = min(rows)
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)), lt5p5=int(sum(1 for x in own if x < 5.5 - 1e-6)),
                forced=int(sum(r[1] for r in rows)), th_max_taken=round(max(r[6] for r in rows), 2),
                lowest=dict(own=round(lo[0], 3), forced=bool(lo[1]), kind=B.kind[lo[5]], **{k: B.poses[lo[5]][k] for k in ("plane", "elev", "axial")}))


def extras(M, B):
    out = {}
    try:
        out["th_margin_own_state"] = th_margin(M, B)
    except Exception as e:
        out["th_margin_own_state"] = dict(error=repr(e)[:200])
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    try:
        k = np.asarray(M.K["ang"], float)[taken]; out["knee_ang_taken"] = [round(float(k.min()), 2), round(float(k.max()), 2)]
        out["knee_window"] = [float(M.p.get("ang_min")), 180.0 - float(M.p.get("ang_min"))]
    except Exception as e:
        out["knee_ang_taken"] = repr(e)[:200]
    try:
        d = np.degrees(np.abs(np.asarray(M.dK, float)[taken])); out["dK_taken_max_deg"] = round(float(d.max()), 2)
    except Exception as e:
        out["dK_taken_max_deg"] = repr(e)[:200]
    for a in ("_sc_info",):
        v = getattr(M, a, None)
        if isinstance(v, dict): out["sc_info"] = {kk: vv for kk, vv in v.items() if isinstance(vv, (int, float, str, list)) and len(str(vv)) < 300}
    return out


def run(rid, wear):
    row = json.load(open(os.path.join(W.REPO, "docs", "concepts", "rows", rid + ".json")))
    P = dict(row.get("best_params") or {})
    mod = W._load("awpm_" + rid.replace("-", "_"), os.path.join(W.REPO, "docs", "concepts", "models", rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(rid + ": no pin-knee-style audit to capture")
    cap = W._capture(pk)
    out = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    M, B = cap[-1]
    a = out.get("audit") or {}
    return dict(design=rid, wear=wear, model_frozen=out.get("frozen"), fit_fast=out.get("fit_fast"),
                model_audit_near=dict(near1=a.get("gap_near1"), near2=a.get("gap_near2"), near2_poses=a.get("near2_poses"), min_mm=a.get("near_touch_min_mm")),
                probe=W.analyse(M, B), extras=extras(M, B))


if __name__ == "__main__":
    t = time.time(); r = run(sys.argv[1], sys.argv[2]); r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
    json.dump(r, open(sys.argv[3], "w"), indent=1, default=float); print(json.dumps({k: v for k, v in r.items() if k != "probe"}, default=float))

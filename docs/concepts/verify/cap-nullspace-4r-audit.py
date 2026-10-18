"""Audit of cap-nullspace-4r (independent auditor, 2026-10-18): reproduce the claim (fit Bench(60,160) fast, frozen
exact Bench(110,360)), then bound what the binder costs: per-member contact attribution, and the gap with hub 2
(and hub 2 + links 1-2) deleted or set ideal (8 mm), plus the in-band-perfect floor (reach + contact only).
    OMP_NUM_THREADS=1 nice -n 10 [CB_EXACT=1] python3 docs/concepts/verify/cap-nullspace-4r-audit.py wear '<json>' OUT.json
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/cap-nullspace-4r-audit.py ghost '<json>' OUT.json
"""
import functools, importlib.util, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                                    # noqa: E402
import concept_bench as CB                                                 # noqa: E402
spec = importlib.util.spec_from_file_location("cn4", os.path.join(REPO, "docs/concepts/models/cap-nullspace-4r.py"))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)


def bounds(B):
    kl = B._kit_last; ch = kl["chain"]; names = [m.name for m in ch.members]
    sizes = [kl["pts"][n].shape[1] for n in names]; off = np.cumsum([0] + sizes)
    sl = {n: slice(off[i], off[i + 1]) for i, n in enumerate(names)}
    res0 = list(B.res); out = dict(base=B.report())
    att = {}
    for i, d in enumerate(res0):
        if d is None or float(np.min(d)) >= 0: continue
        bad = [n for n in names if float(np.min(d[sl[n]])) < 0]
        for n in bad: att[n] = att.get(n, 0) + 1
    out["contact_members"] = att; out["n_contact_poses"] = sum(1 for d in res0 if d is not None and float(np.min(d)) < 0)

    def variant(drop=(), ideal=()):
        for i, d in enumerate(res0):
            if d is None: B.res[i] = None; continue
            d = d.copy()
            for n in ideal: d[sl[n]] = 8.0
            keep = np.ones(len(d), bool)
            for n in drop: keep[sl[n]] = False
            B.res[i] = d[keep]
        r = B.report(); B.res = list(res0); return {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}
    out["hub2_deleted"] = variant(drop=("hub2",))
    out["hub2_ideal"] = variant(ideal=("hub2",))
    out["J2_members_ideal"] = variant(ideal=("hub2", "link1", "link2"))
    out["all_ideal"] = variant(ideal=tuple(names))
    b = out["base"]; out["floor_inband_perfect"] = round(100 * (max(0, .95 - b["follow"]) + max(0, .90 - b["reach"])) + 100 * b["contact"], 2)
    return out


def wear(p0, outp, fit=(60, 160), big=(110, 360)):
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=1.0 - 1e-4)
    res = dict(params=p0)
    ex = os.environ.pop("CB_EXACT", None)
    try:
        Bf = K.bench(*fit)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    t = time.time(); pf, rf = M.evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    res["fit"] = dict({k: rf.get(k) for k in M.KEYS}, mode=Bf.mode, secs=round(time.time() - t, 1), bounds=bounds(Bf))
    json.dump(res, open(outp, "w"), indent=1, default=float); print("fit", json.dumps(res["fit"], default=float)[:900], flush=True)
    if big is None: return res
    Bb = K.bench(*big); fp = K.fit_profiles; t = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        _, r = M.evaluate(Bb, pf)
    finally:
        K.fit_profiles = fp; K.collisions = coll
    res["frozen"] = dict({k: r.get(k) for k in M.KEYS}, mode=Bb.mode, secs=round(time.time() - t, 1), bounds=bounds(Bb))
    json.dump(res, open(outp, "w"), indent=1, default=float); print("frozen", json.dumps(res["frozen"], default=float)[:1500], flush=True)
    return res


if __name__ == "__main__":
    mode, par, outp = sys.argv[1], json.loads(sys.argv[2]), sys.argv[3]
    p = dict(M.PARAMS, **par)
    if mode == "wear": wear(p, outp)
    elif mode == "fit": wear(p, outp, big=None)
    elif mode == "ghost":
        p["policy"] = "band"; p["connect"] = 0; wear(p, outp, big=None)

#!/usr/bin/env python3
"""Stage 1 of the zc-frontier-3r CAD-context export: rebuild the VERIFIED shape by running the model.

Verifier protocol (docs/concepts/rows/zc-frontier-3r.json "verification", skeptic harness
docs/concepts/verify/zc-frontier-3r-gpu-skeptic.py frozen --fits fit60): the member undersides are FITTED on
Bench(60,160) fast (kit K3 march, quantile q), then FROZEN and worn on Bench(110,360) EXACT -> gap 33.51.

    python3 docs/cad_context/zc-frontier-3r/scripts/fit_and_wear.py OUT_DIR [--no-wear]

Writes OUT_DIR/profile_fit60.npz (the frozen per-sample underside radii, sha256 printed) and OUT_DIR/wear.json
(the exact-wear numbers + per-pose take mask / joint values / pose labels for the range tables).
"""
import hashlib, importlib.util, io, json, os, sys, time
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 4))
PARAMS = dict(az=109.3565, el=65.94, a1=36.7226, a2=69.0575, wd=85.7423, wa=-16.19210000000001, sigma=-1, inv2=0, inv3=1,
              q=0.978, end_extra=1.784)


def model():
    spec = importlib.util.spec_from_file_location("zc_model", os.path.join(REPO, "docs", "concepts", "models", "zc-frontier-3r.py"))
    m = importlib.util.module_from_spec(spec); sys.modules["zc_model"] = m; spec.loader.exec_module(m); return m


def bench(M, nc, nw, exact):
    old = os.environ.get("CB_EXACT")
    if exact: os.environ["CB_EXACT"] = "1"
    else: os.environ.pop("CB_EXACT", None)
    try: return M.K.bench(nc, nw)
    finally:
        if old is None: os.environ.pop("CB_EXACT", None)
        else: os.environ["CB_EXACT"] = old


def prof_digest(prof):
    h = hashlib.sha256()
    for k in sorted(prof): h.update(k.encode()); h.update(np.ascontiguousarray(np.round(prof[k], 6), np.float64).tobytes())
    return h.hexdigest()


def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True); M = model(); t = time.time()
    Bf = bench(M, 60, 160, exact=False); pf, rf = M.evaluate(Bf, dict(PARAMS))
    prof = {k: np.asarray(v, float) for k, v in Bf._kit_last["prof"].items()}
    dig = prof_digest(prof)
    np.savez(os.path.join(out, "profile_fit60.npz"), **prof)
    fit = {k: rf.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest", "hub_F", "mode")}
    res = dict(params=PARAMS, snapped=pf, fit_bench=[60, 160], fit_mode=Bf.mode, fit=fit, profile_sha256=dig,
               fit_secs=round(time.time() - t, 1))
    json.dump(res, open(os.path.join(out, "wear.json"), "w"), indent=1, default=float)
    print("fit", json.dumps(fit, default=float), dig, f"{time.time() - t:.0f}s", flush=True)
    if "--no-wear" in sys.argv: return
    t = time.time(); Bw = bench(M, 110, 360, exact=True)
    pw, rw = M.evaluate(Bw, dict(PARAMS), fixed_prof={k: v.copy() for k, v in prof.items()})
    L = Bw._kit_last; take = np.array([M.SPM._taken(Bw, j) for j in range(len(Bw.res))])
    ch = L["chain"]; q = np.asarray(ch.q, float)
    res.update(wear_bench=[110, 360], wear_mode=Bw.mode, wear={k: rw.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "inband10",
               "contact", "honest", "audit", "hub_F", "min_metal_all_faces", "top_contact_poses", "inband_member")},
               wear_secs=round(time.time() - t, 1),
               poses=dict(kind=list(Bw.kind), clip=list(Bw.clip), global_idx=[int(i) for i in Bw.idx], plane=[p["plane"] for p in Bw.poses],
                          elev=[p["elev"] for p in Bw.poses], axial=[p["axial"] for p in Bw.poses], closes=[bool(x) for x in L["ok"]],
                          kin_ok=[bool(x) for x in np.asarray(ch.ok, bool)], taken=[bool(x) for x in take], q=q.round(4).tolist()))
    json.dump(res, open(os.path.join(out, "wear.json"), "w"), indent=1, default=float)
    print("wear", json.dumps(res["wear"], default=float), f"{time.time() - t:.0f}s", flush=True)


if __name__ == "__main__":
    main()

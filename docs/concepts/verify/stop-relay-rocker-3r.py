"""Adversarial verifier for stop-relay-rocker-3r (2026-10-16). Re-measures one configuration with the model's own checks
(kit K1-K7 + dense K2 on q0..q3, declared slim-hub audit incl. the pivot R0, crown / wall skin check of all four hubs,
near-touch, overhead split) plus the verifier's:

  * CONTINUITY ON THE BIG BENCH: the model's own frozen() wears the shape on Bench(110,360) WITHOUT its connected()
    island filter (only evaluate() applies it), so its queued frozen runs count static relay islands. Here the
    flood fill runs on the big bench too (the frozen shape): a relay pose no continuous motion from mode A reaches is
    not taken;
  * outer-face skin check on EVERY member (top face of each strap, neck, rocker, hub crowns) and near-touch over every
    face with metal < 1 mm counted as contact (the spine-parked verifier's top_check, reused unchanged);
  * 1 mm radial part-part clearance in K6 (the risley-turret verifier's rule) on every task;
  * closure residual (J2 closure and the rocker arc), hub fitted levels F <= 140 mm for all four hubs incl. the pivot;
  * frozen shape (lesson c): fit on Bench(60,160) FAST, every fitted level frozen, worn on Bench(110,360) (CB_EXACT=1);
  * ablation: the same frozen shape with the rocker locked (relay = 0) - what the passive axis is worth.

    CB_EXACT=1 python3 docs/concepts/verify/stop-relay-rocker-3r.py <task> <out.json> '<json params>'
      task: fit60 (Bench(60,160) refit, path from CB_EXACT, with connect) | frozen (Bench(110,360), frozen from the fast fit)
"""
import functools, importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
spec = importlib.util.spec_from_file_location("srr", os.path.join(REPO, "docs", "concepts", "models", "stop-relay-rocker-3r.py"))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
spec2 = importlib.util.spec_from_file_location("spv", os.path.join(HERE, "spine-parked-j2-3r.py"))
SPV = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(SPV)
K = M.K
assert SPV.K is K


def apply_connect(B, p):
    take = np.array([M._taken(B, j) for j in range(len(B.res))]); conn, relayed = M.connected(B, p, take)
    drop = [j for j in range(len(B.res)) if take[j] and B.kind[j] == "ws" and relayed[j] and not conn[j]]
    for j in drop: B.res[j] = None
    B._kit_last["take"] = B._kit_last["take"].copy(); B._kit_last["take"][drop] = False
    relay_taken_ws = int(sum(1 for j in range(len(B.res)) if take[j] and B.kind[j] == "ws" and relayed[j]))
    return dict(islands_dropped=len(drop), relay_ws_taken_static=relay_taken_ws, relay_ws_connected=relay_taken_ws - len(drop))


def run(B, p, fixed_prof=None, connect=True):
    fp = K.fit_profiles
    if fixed_prof is not None:
        K.fit_profiles = lambda B_, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in fixed_prof.items()}
    try:
        r = K.evaluate(B, M.build, p); r = M.declared_audit(r, p)
        static = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        cinfo = apply_connect(B, p) if (connect and p.get("relay", 1)) else None
        r = M.extras(B, r, p)
    finally:
        K.fit_profiles = fp
    keep = {k: v for k, v in r.items() if M.SPM._jsonable(v) and k != "checks"}
    keep["static_no_connect"] = static; keep["connect"] = cinfo
    keep["verifier"] = SPV.top_check(B, r, p)
    ch = B._kit_last["chain"]; okk = np.asarray(ch.ok, bool)
    keep["verifier"]["rocker_residual_deg"] = ch.info.get("rocker_residual_deg")
    keep["verifier"]["modes_all_poses"] = ch.info.get("modes")
    return keep


def main():
    task, out = sys.argv[1], sys.argv[2]
    par = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=1.0 - 1e-4)       # 1 mm radial K6
    p0 = M.snap(dict(M.PARAMS, **par)); res = dict(task=task, params=par, exact=os.environ.get("CB_EXACT") == "1", t0=K.now())
    t = time.time()
    if task == "fit60":
        B = K.bench(60, 160)
        res["run"] = run(B, p0); res["run"]["mode"] = B.mode
    elif task == "frozen":
        ex = os.environ.pop("CB_EXACT", None)
        try:
            Bf = K.bench(60, 160)
        finally:
            if ex is not None: os.environ["CB_EXACT"] = ex
        pf, rf = M.evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        res["fit"] = {k: rf.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "islands_dropped")}
        res["fit"]["mode"] = Bf.mode
        json.dump(res, open(out, "w"), indent=1, default=float); print("fit", res["fit"], flush=True)
        Bb = K.bench(110, 360); res["run"] = run(Bb, pf, prof); res["run"]["mode"] = Bb.mode
    else:
        raise SystemExit("task: fit60 | frozen")
    res["secs"] = round(time.time() - t, 1)
    json.dump(res, open(out, "w"), indent=1, default=float)
    r = res["run"]
    print(task, r["mode"], {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit",
                                                  "gap_near1", "min_metal_skin", "overhead", "taken_relay", "connect",
                                                  "static_no_connect")}, flush=True)
    print("verifier", r["verifier"], flush=True)


if __name__ == "__main__":
    main()

"""Adversarial verifier for spine-parked-j2-3r (2026-10-16). Re-measures one configuration with the model's own checks
(kit K1-K7 + dense K2, declared slim-hub audit, hub crown / wall skin check, near-touch, overhead split) plus the
verifier's:

  * outer-face skin check on EVERY member: the top face of each strap, the neck and the hub crowns (underside + t along
    the ray) - a taken pose with any top-face sample inside the skin becomes a contact pose;
  * near-touch over all faces (underside, crown / wall, top): the gap with metal < 1 mm counted as contact;
  * 1 mm radial part-part clearance in K6 (the risley-turret verifier's rule; the model's frozen() already sets it,
    and it is applied here on every task, incl. the Bench(60,160) exact refit);
  * closure residual and fold margin over the taken poses of the big bench; hub fitted levels F (hub-axis
    accessibility: skin along each axis within 140 mm of GH, nothing above the crown);
  * frozen shape (lesson c): fit on Bench(60,160) FAST, every fitted level frozen, worn on Bench(110,360) (CB_EXACT=1).

    CB_EXACT=1 python3 docs/concepts/verify/spine-parked-j2-3r.py <task> <out.json> '<json params>'
      task: fit60 (Bench(60,160) refit, path from CB_EXACT) | frozen (Bench(110,360), frozen from the fast fit)
"""
import functools, importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
spec = importlib.util.spec_from_file_location("spm", os.path.join(REPO, "docs", "concepts", "models", "spine-parked-j2-3r.py"))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
K = M.K


def top_check(B, r, p):
    """verifier additions on the last K.evaluate: top faces of every member, near-touch over every face, residuals"""
    L = B._kit_last; ch, pts, prof, take = L["chain"], L["pts"], L["prof"], L["take"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    tmin = np.full(len(B.res), np.inf); who = {}
    if len(Pi):
        parts = []
        for m in ch.members:
            X = pts[m.name][Pi]; n = np.linalg.norm(X, axis=-1, keepdims=True); parts.append(X * (n + m.t) / n)
        C = np.concatenate(parts, 1)
        d = K.dist_many(B, np.repeat(Pi, C.shape[1]), C.reshape(-1, 3)).reshape(len(Pi), C.shape[1])
        tmin[Pi] = d.min(1); cut = np.cumsum([0] + [x.shape[1] for x in parts])
        for a, j in enumerate(Pi): who[int(j)] = ch.members[int(np.searchsorted(cut, int(np.argmin(d[a])), side="right") - 1)].name
    bad = [int(j) for j in np.nonzero(tmin < 0)[0]]
    for j in bad: B.res[j] = np.append(B.res[j], tmin[j])
    rv = B.report()
    taken = [j for j in range(len(B.res)) if M._taken(B, j)]
    allmin = sorted((min(float(np.min(B.res[j])), tmin[j]), j) for j in taken)
    save = list(B.res)
    for dd, j in allmin:
        if dd < 1.0: B.res[j] = np.append(B.res[j], -1e-3)
    rn = B.report(); B.res = save
    ok = np.asarray(ch.ok, bool); tk = np.zeros(len(ok), bool); tk[taken] = True
    J = ch.joints
    res = K.closure_residual(J["J1"], J["J3"], J["J2"], p["a1"], p["a2"])
    hubF = {m.name: round(float(prof[m.name][0]), 2) for m in ch.members if m.kind == "flat"}
    lvl = {m.name: dict(med=round(float(np.median(prof[m.name])), 1), max=round(float(np.max(prof[m.name])), 1))
           for m in ch.members if m.kind != "flat"}
    out = dict(v=dict((k, rv[k]) for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")),
               v_near1=dict((k, rn[k]) for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")),
               top_contact_poses=len(bad), top_contact_who=sorted({who[j] for j in bad}),
               top_min=round(float(np.min(tmin[np.isfinite(tmin)])), 2) if np.isfinite(tmin).any() else None,
               min_metal_all_faces=round(float(allmin[0][0]), 2) if allmin else None,
               closure_residual_max_deg=float(np.max(res[tk])) if tk.any() else None,
               hub_F=hubF, strap_levels=lvl, hub_F_ok=all(v <= 140.0 for v in hubF.values()),
               n_taken=len(taken), n=len(B.res))
    return out


def run(B, p, fixed_prof=None):
    fp = K.fit_profiles
    if fixed_prof is not None:
        K.fit_profiles = lambda B_, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in fixed_prof.items()}
    try:
        r = K.evaluate(B, M.build, p); r = M.declared_audit(r, p); r = M.extras(B, r, p)
    finally:
        K.fit_profiles = fp
    keep = {k: v for k, v in r.items() if M._jsonable(v) and k != "checks"}
    keep["verifier"] = top_check(B, r, p)
    return keep


def snap(p):
    """the model's clamps / snaps (M.evaluate) without running it"""
    p = dict(p); p["q"] = min(1.0, max(0.8, float(p["q"]))); p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0))))
    for k in ("rad2", "rad3"): p[k] = min(M.SLIM, key=lambda x: abs(x - float(p[k])))
    return p


def main():
    task, out = sys.argv[1], sys.argv[2]
    par = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=1.0 - 1e-4)       # 1 mm radial K6
    p0 = dict(M.PARAMS, **par); res = dict(task=task, params=par, exact=os.environ.get("CB_EXACT") == "1", t0=K.now())
    t = time.time()
    if task == "fit60":
        B = K.bench(60, 160); pf = snap(p0)
        res["run"] = run(B, pf); res["run"]["mode"] = B.mode
    elif task == "frozen":
        ex = os.environ.pop("CB_EXACT", None)
        try:
            Bf = K.bench(60, 160)
        finally:
            if ex is not None: os.environ["CB_EXACT"] = ex
        pf, rf = M.evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        res["fit"] = {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit")}
        res["fit"]["mode"] = Bf.mode
        json.dump(res, open(out, "w"), indent=1, default=float); print("fit", res["fit"], flush=True)
        Bb = K.bench(110, 360); res["run"] = run(Bb, pf, prof); res["run"]["mode"] = Bb.mode
    else:
        raise SystemExit("task: fit60 | frozen")
    res["secs"] = round(time.time() - t, 1)
    json.dump(res, open(out, "w"), indent=1, default=float)
    r = res["run"]
    print(task, r["mode"], {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit",
                                                  "gap_near1", "min_metal_skin", "overhead", "inband_member")}, flush=True)
    print("verifier", r["verifier"], flush=True)


if __name__ == "__main__":
    main()

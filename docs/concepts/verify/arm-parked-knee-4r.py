"""Adversarial verifier for arm-parked-knee-4r (2026-10-16). Re-measures one configuration with the model's own checks
(kit K1-K7 + dense K2 that re-runs the spring policy between clip frames, hub crown / wall skin check, near-touch,
overhead split) plus the verifier's:

  * outer-face skin check on EVERY member (top face of each strap / neck / hub crown disc = underside + t on the ray);
  * near-touch over all faces (metal < 1 mm counted as contact);
  * 1 mm radial part-part clearance in K6 (risley-turret verifier rule);
  * independent closure: angle(J1, J2) = a1, angle(J2, J3) = a2, angle(J3, J4) = a3 over the taken poses, and the
    J2 stops: angle(J1, J3) inside [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m];
  * hub fitted levels F (hub-axis accessibility <= 140 mm);
  * r12: the J4 torsion-spring coil (OD ~23) modelled as hub 4's disc at r 12 EVERYWHERE (fit, skin underside, crown,
    and K6 part-part clearance) - the model kept r 10 in K6 and called the 2 mm annulus "a stated hole";
  * botharc: the centred spring under two stops has two disjoint feasible knee arcs (d and -d about J4); the model takes
    the arc on dp's side pose by pose, history can leave the knee on the other arc pressed on the stop facing dp. The
    pessimistic bound counts a WORKSPACE pose as reached only if it is taken on both arcs (clips keep the model's arc:
    their dense K2 already rejects a snap between arcs).
  * frozen shape (lesson c): fit on Bench(60,160) FAST, every fitted level frozen, worn on Bench(110,360) (CB_EXACT=1).

    CB_EXACT=1 python3 docs/concepts/verify/arm-parked-knee-4r.py <task> <out.json> '<json params>'
      task: frozen | frozen_r12 | frozen_botharc | frozen_r12_botharc
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
spec = importlib.util.spec_from_file_location("apk", os.path.join(REPO, "docs", "concepts", "models", "arm-parked-knee-4r.py"))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
K = M.K; SPM = M.SPM
D2R = math.pi / 180
SPARE0 = M.spare


def spare_alt(F, p, u1, u4):
    """the OTHER arc: the knee mirrored to -sign(dp), pressed on the stop facing dp (|d| = dlo)"""
    p3, feas, defl, stop = SPARE0(F, p, u1, u4)
    a1, a2, a3 = p["a1"], p["a2"], p["a3"]; mi = p["margin"] + p["inner"]
    th = np.degrees(np.arccos(np.clip((u1 * u4).sum(-1), -1, 1)))
    lo1, hi1 = abs(a1 - a2) + mi, min(a1 + a2, 360 - a1 - a2) - mi
    u4s = K.wdir(p["wd"], p["wa"]); ref = np.array([0.0, -1.0, 0.0]) if abs(u4s[1]) < 0.9 else np.array([0.0, 0.0, -1.0])
    e1 = K.unit(np.cross(u4s, ref)); e2 = np.cross(u4s, e1)
    pp = F.HG(math.cos(a3 * D2R) * u4s + math.sin(a3 * D2R) * (math.cos(p["pz4"] * D2R) * e1 + math.sin(p["pz4"] * D2R) * e2))
    dp = np.radians(K.axis_angle(u4, u1, pp))
    sa, ca = math.sin(a3 * D2R), math.cos(a3 * D2R); st, ct = np.sin(th * D2R), np.cos(th * D2R); den = sa * st + 1e-12
    cmax = (np.cos(lo1 * D2R) - ca * ct) / den
    dlo = np.arccos(np.clip(cmax, -1, 1))
    dsel = -np.where(dp >= 0, 1.0, -1.0) * dlo
    w = K.unit(u1 - (u1 * u4).sum(-1, keepdims=True) * u4); p3a = M.rot(u4, ca * u4 + sa * w, dsel)
    defl = np.degrees(np.abs(dsel - dp)); return p3a, feas, defl, np.ones_like(feas, bool)


def ang(a, b): return np.degrees(np.arccos(np.clip((K.unit(a) * K.unit(b)).sum(-1), -1, 1)))


def top_check(B, r, p):
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
    taken = [j for j in range(len(B.res)) if SPM._taken(B, j)]
    allmin = sorted((min(float(np.min(B.res[j])), tmin[j]), j) for j in taken)
    save = list(B.res)
    for dd, j in allmin:
        if dd < 1.0: B.res[j] = np.append(B.res[j], -1e-3)
    rn = B.report(); B.res = save
    tk = np.zeros(len(B.res), bool); tk[taken] = True
    J = ch.joints; a1, a2, a3 = p["a1"], p["a2"], p["a3"]
    e12 = np.abs(ang(J["J1"], J["J2"]) - a1); e23 = np.abs(ang(J["J2"], J["J3"]) - a2); e34 = np.abs(ang(J["J3"], J["J4"]) - a3)
    w13 = ang(J["J1"], J["J3"]); lo = abs(a1 - a2) + p["margin"]; hi = min(a1 + a2, 360 - a1 - a2) - p["margin"]
    hubF = {m.name: round(float(prof[m.name][0]), 2) for m in ch.members if m.kind == "flat"}
    return dict(v=dict((k, rv[k]) for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")),
                v_near1=dict((k, rn[k]) for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")),
                top_contact_poses=len(bad), top_contact_who=sorted({who[j] for j in bad}),
                min_metal_all_faces=round(float(allmin[0][0]), 2) if allmin else None,
                closure_err_deg=dict(a1=float(e12[tk].max()), a2=float(e23[tk].max()), a3=float(e34[tk].max())) if tk.any() else None,
                stop_window=[lo, hi], w13_taken=[float(w13[tk].min()), float(w13[tk].max())] if tk.any() else None,
                stop_violations=int(((w13 < lo - 1e-6) | (w13 > hi + 1e-6))[tk].sum()),
                hub_F=hubF, hub_F_ok=all(v <= 140.0 for v in hubF.values()), n_taken=len(taken), n=len(B.res))


def ev(B, p, fixed_prof=None):
    fp = K.fit_profiles
    if fixed_prof is not None:
        K.fit_profiles = lambda B_, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in fixed_prof.items()}
    try:
        r = K.evaluate(B, M.build, p); r = SPM.declared_audit(r, p); r = M.extras(B, r, p)
    finally:
        K.fit_profiles = fp
    return r


def keep(r): return {k: v for k, v in r.items() if SPM._jsonable(v) and k != "checks"}


def snap(p, r12):
    p = dict(p); p["q"] = min(1.0, max(0.8, float(p["q"]))); p["s1"] = 1 if float(p["s1"]) >= 0 else -1
    p["margin"] = max(5.0, float(p["margin"])); p["side"] = max(-1, min(1, int(round(float(p.get("side", 0))))))
    p["end_extra"] = min(8.0, max(0.0, float(p.get("end_extra", 0.0)))); p["near"] = 0; p.pop("ow", None)
    for k in ("rad1", "rad2", "rad3", "rad4"): p[k] = 10.0
    if r12: p["rad4"] = 12.0
    return p


def main():
    task, out = sys.argv[1], sys.argv[2]
    par = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    r12 = "r12" in task; both = "botharc" in task
    K.collisions = functools.partial(K.collisions, overlap=1.0 - 1e-4)                  # 1 mm radial K6
    p0 = snap(dict(M.PARAMS, **par), r12)
    res = dict(task=task, params=p0, exact=os.environ.get("CB_EXACT") == "1", t0=K.now(), r12=r12, botharc=both)
    t = time.time()
    ex = os.environ.pop("CB_EXACT", None)
    try:
        Bf = K.bench(60, 160)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    rf = ev(Bf, p0); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    res["fit"] = {k: rf.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "gap_near1")}
    res["fit"]["mode"] = Bf.mode; json.dump(res, open(out, "w"), indent=1, default=float); print("fit", res["fit"], flush=True)
    Bb = K.bench(110, 360)
    if both:
        M.spare = spare_alt
        try:
            ra = ev(Bb, p0, prof); va = top_check(Bb, ra, p0)
        finally:
            M.spare = SPARE0
        alt_ws = {j for j in range(len(Bb.res)) if Bb.kind[j] == "ws" and SPM._taken(Bb, j)}
        res["alt"] = dict(keep(ra), verifier=va)
    r = ev(Bb, p0, prof); v = top_check(Bb, r, p0)
    res["run"] = dict(keep(r), verifier=v, mode=Bb.mode)
    if both:
        ws_model = {j for j in range(len(Bb.res)) if Bb.kind[j] == "ws" and SPM._taken(Bb, j)}
        lost = sorted(ws_model - alt_ws)
        for j in lost: Bb.res[j] = None
        rb = Bb.report()
        res["botharc"] = dict(report={k: rb[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")},
                              ws_model=len(ws_model), ws_alt=len(alt_ws), ws_both=len(ws_model & alt_ws), lost=len(lost),
                              lost_poses=[dict(plane=Bb.poses[j]["plane"], elev=Bb.poses[j]["elev"], axial=Bb.poses[j]["axial"]) for j in lost[:40]])
    res["secs"] = round(time.time() - t, 1)
    json.dump(res, open(out, "w"), indent=1, default=float)
    print(task, Bb.mode, {k: res["run"].get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit",
                                                         "gap_near1", "min_metal_skin", "over_reach", "crown_contact_poses")}, flush=True)
    print("verifier", v, flush=True)
    if both: print("botharc", {k: res["botharc"][k] for k in ("report", "ws_model", "ws_alt", "ws_both", "lost")}, flush=True)


if __name__ == "__main__":
    main()

"""Reach attribution of the round-3 leaders (2026-10-16, docs/research/reach_attribution.md).

Wears a leader's VERIFIED configuration with the verifiers' own frozen-shape protocol (fit on Bench(60,160) FAST, worn on
Bench(110,360) without refit; CB_EXACT=1 for the exact path), runs the model and the verifier's extra checks, and writes
ONE ROW PER POSE: the pose, the J1-J3 axis angle th and the fold window, the conditioning of the 3R at that pose and the
FIRST cause that lost it, in the order the model applies its checks:

    fold (J1-J3 angle outside [|a1-a2| + m, min(a1+a2, 360-a1-a2) - m]; split folded side th < lo / stretched th > hi)
    -> knee / cuff / knuckle closure window (the model's second kinematic window)
    -> flip (continuity along the 10 fps fit clips: a branch jump = the jam of a passive follower)
    -> closure residual >= 0.5 deg
    -> parts (part-part clearance)  -> skin (a pose the fit gave up to the skin: 'skin requirement')
    -> contact (metal < 0 mm in a pose the fit kept; incl. the verifier's top / crown / wall faces)
    -> verifier (closure / boss / knee-hub3 / post checks of the verifier, applied after the model)

Conditioning, from (a1, a2, th) alone (a spherical 3R's orientation Jacobian is U = [u1 u2 u3], Gram = the arc cosines):
    sigma_min = smallest singular value of U (1 / sigma_min = worst joint rate per unit arm rate), mu = the J2 dihedral
    (the transmission angle of the spherical dyad: 0 = folded, 180 = stretched; reported as min(mu, 180 - mu)).

    OMP_NUM_THREADS=1 CB_EXACT=1 nice -n 10 python3 docs/research/reach/attribute.py <leader> <out.json> [--margin M] [--refit]
        leader: pin-knee | raglan | knuckle | spine
        --margin M: the fold margin on the worn bench (deg, default 10 = the bench rule; 7 / 5 = sensitivity, report only)
        --refit:    fit the shape at margin M too (default: the shape stays the margin-10 fit, only the window widens)
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

VDIR = os.path.join(REPO, "docs", "concepts", "verify")
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")


def _load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


def verified_params(leader):
    if leader == "pin-knee": return json.load(open(os.path.join(VDIR, "skin-normal-3r-pin-knee_big_frozen.json")))["params"]
    if leader == "raglan": return json.load(open(os.path.join(VDIR, "raglan-knee-3r_big_frozen.json")))["params"]
    if leader == "knuckle": return json.load(open(os.path.join(VDIR, "skin-normal-3r-knuckle-cufflink.results.json")))["params"]
    if leader == "spine": return json.load(open(os.path.join(VDIR, "spine-parked-j2-3r.results.json")))["G_frozen"]["params"]
    raise SystemExit(leader)


def bench_fast60():
    old = os.environ.pop("CB_EXACT", None)
    try: return CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old


def conditioning(a1, a2, th):
    """sigma_min of U = [u1 u2 u3] and the J2 dihedral mu (deg) of the spherical triangle (a1, a2, th); nan if it does not close"""
    a1, a2, th = (np.radians(np.asarray(x, float)) for x in (a1, a2, th))
    a1, a2, th = np.broadcast_arrays(a1, a2, th)
    G = np.zeros(a1.shape + (3, 3)); G[..., 0, 0] = G[..., 1, 1] = G[..., 2, 2] = 1
    G[..., 0, 1] = G[..., 1, 0] = np.cos(a1); G[..., 1, 2] = G[..., 2, 1] = np.cos(a2); G[..., 0, 2] = G[..., 2, 0] = np.cos(th)
    ev = np.linalg.eigvalsh(G)[..., 0]
    smin = np.where(ev >= 0, np.sqrt(np.clip(ev, 0, None)), np.nan)
    cB = (np.cos(th) - np.cos(a1) * np.cos(a2)) / (np.sin(a1) * np.sin(a2))
    mu = np.where(np.abs(cB) <= 1, np.degrees(np.arccos(np.clip(cB, -1, 1))), np.nan)
    return smin, mu


# ---- the offset-skin-normal family (pin knee, raglan knee, knuckle cufflink): seed module S holds SING ---------------
def run_osn(leader, P, margin, refit, nc, nw):
    if leader == "pin-knee":
        V = _load("v_pin_knee", os.path.join(VDIR, "skin-normal-3r-pin-knee.py")); MK, S = V.MK, V.S; cls = MK.Model; P = dict(P)
    elif leader == "raglan":
        V = _load("v_raglan", os.path.join(VDIR, "raglan-knee-3r.py")); MK, S = V.PK, V.S; cls = V.PK.Model; P = V.RK.clean(P)
    else:
        V = _load("v_knuckle", os.path.join(VDIR, "skin-normal-3r-knuckle-cufflink.py")); MK, S = V.MK, V.MK.S; cls = MK.Model; P = dict(P)
    S.SING = float(margin) if refit else 10.0
    B1 = bench_fast60()
    if leader == "knuckle":
        p1, _ = MK.evaluate(B1, P); M1 = MK.Model(B1, p1); r1 = M1.run()
    else:
        M1 = cls(B1, dict(P)); r1 = M1.run()
        P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    fit = {k: r1[k] for k in KEYS}; fit["mode"] = B1.mode
    S.SING = float(margin)
    B = CB.Bench(n_clip=nc, n_ws=nw)
    if leader == "knuckle":
        M = MK.Frozen(B, M1)
    else:
        class Frozen(cls):
            def fit(self):
                for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                          "Hneed", "Lneed", "hEx", "_Ex", "_h12"):
                    if hasattr(M1, a): setattr(self, a, getattr(M1, a))
                self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
        M = Frozen(B, P2)
    r = M.run(); model = {k: r[k] for k in KEYS}
    why = np.array(M.why, dtype=object).copy()
    if leader == "raglan":
        V.V.MK = V.PK; V.V.S = V.S
        ex, bad = V.V.extra_checks(M, B)
    else:
        ex, bad = V.extra_checks(M, B)
    res_model = list(B.res)
    for i in bad:
        if B.res[i] is not None and float(np.min(B.res[i])) >= 0 and not why[i]: why[i] = "verifier"
        B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(float); D = M.D
    u1, u3 = D.u[0], D.u[2]; a1, a2 = (math.degrees(x) for x in D.A)
    th = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", Q, u3) @ u1, -1, 1)))
    seats = dict(a1=round(a1, 3), a2=round(a2, 3), u1=[round(float(x), 5) for x in u1], u3_home=[round(float(x), 5) for x in u3])
    return dict(B=B, why=why, th=th, a1=a1, a2=a2, model=model, corrected=corrected, fit=fit, seats=seats,
                extra=dict(n_bad=len(bad)), hub_f=[round(float(x), 2) for x in getattr(M, "f", [])])


# ---- spine-parked (kit) ----------------------------------------------------------------------------------------------
def run_spine(P, margin, refit, nc, nw):
    VS = _load("v_spine", os.path.join(VDIR, "spine-parked-j2-3r.py")); M = VS.M; K = VS.K
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=1.0 - 1e-4)          # the verifier's 1 mm radial K6
    p0 = dict(M.PARAMS, **P); p0["margin"] = float(margin) if refit else 10.0
    Bf = bench_fast60()
    pf, rf = M.evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    fit = {k: rf[k] for k in KEYS}; fit["mode"] = Bf.mode
    pf = dict(pf); pf["margin"] = float(margin)
    B = K.bench(nc, nw); r = VS.run(B, pf, prof)
    L = B._kit_last; ch = L["chain"]
    J = ch.joints; th = np.degrees(np.arccos(np.clip(np.einsum("pi,pi->p", K.unit(J["J1"]), K.unit(J["J3"])), -1, 1)))
    kin = np.asarray(ch.ok, bool); cont = np.asarray(L["ok"], bool); hit = np.asarray(L["hit"], bool)
    why = np.array([""] * len(B.idx), dtype=object)
    for i in range(len(B.idx)):
        if not kin[i]: why[i] = "fold"
        elif not cont[i]: why[i] = "flip"
        elif hit[i]: why[i] = "parts"
        elif B.res[i] is None or float(np.min(B.res[i])) < 0: why[i] = "contact"
    rc = B.report(); model = {k: rc[k] for k in KEYS}
    seats = dict(a1=pf["a1"], a2=pf["a2"], az=pf["az"], el=pf["el"], wd=pf["wd"], wa=pf["wa"], q=pf["q"])
    return dict(B=B, why=why, th=th, a1=float(pf["a1"]), a2=float(pf["a2"]), model=model, corrected=model, fit=fit, seats=seats,
                extra=dict(verifier=r.get("verifier")), hub_f=None)


def main():
    a = sys.argv[1:]; leader, outp = a[0], a[1]
    margin = float(a[a.index("--margin") + 1]) if "--margin" in a else 10.0; refit = "--refit" in a
    nc = int(a[a.index("--nc") + 1]) if "--nc" in a else 110; nw = int(a[a.index("--nw") + 1]) if "--nw" in a else 360
    P = verified_params(leader); t0 = time.time()
    R = run_spine(P, margin, refit, nc, nw) if leader == "spine" else run_osn(leader, P, margin, refit, nc, nw)
    B, why, th, a1, a2 = R["B"], R["why"], R["th"], R["a1"], R["a2"]
    lo = abs(a1 - a2) + margin; hi = min(a1 + a2, 360 - a1 - a2) - margin
    smin, mu = conditioning(a1, a2, th)
    el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses])
    rows = []
    for i in range(len(B.idx)):
        taken = B.res[i] is not None and float(np.min(B.res[i])) >= 0
        w = why[i] if not taken else ""
        if not taken and not w: w = "contact"
        cause = w
        if w == "fold": cause = "fold_folded" if th[i] < 0.5 * (lo + hi) else "fold_stretched"
        elif w in ("slide", "knuckle", "cuff"): cause = "closure_window_" + w
        elif w == "flip": cause = "jam_flip"
        elif w == "closure": cause = "closure_residual"
        elif w == "parts": cause = "part_collision"
        elif w == "skin": cause = "skin_requirement"
        p = B.poses[i]
        grp = []
        if el[i] >= 140: grp.append("overhead")
        if pl[i] >= 100 and el[i] >= 40: grp.append("across")
        if "back" in str(B.clip[i]).lower() or (pl[i] < -30 and el[i] > 20): grp.append("behind")
        rows.append(dict(i=i, kind=B.kind[i], clip=str(B.clip[i]), plane=round(p["plane"], 2), elev=round(p["elev"], 2),
                         axial=round(p["axial"], 2), th=round(float(th[i]), 2), taken=bool(taken), cause=cause or None,
                         dmin=round(float(np.min(B.res[i])), 2) if B.res[i] is not None else None,
                         smin=None if not np.isfinite(smin[i]) else round(float(smin[i]), 4),
                         mu=None if not np.isfinite(mu[i]) else round(float(mu[i]), 2), groups=grp))
    summ = {}
    for name, sel in (("ws", lambda r: r["kind"] == "ws"), ("ws_overhead", lambda r: r["kind"] == "ws" and "overhead" in r["groups"]),
                      ("ws_across", lambda r: r["kind"] == "ws" and "across" in r["groups"]),
                      ("ws_behind", lambda r: r["kind"] == "ws" and "behind" in r["groups"]), ("clip", lambda r: r["kind"] == "clip"),
                      ("clip_overhead", lambda r: r["kind"] == "clip" and "overhead" in r["groups"])):
        S_ = [r for r in rows if sel(r)]; c = {}
        for r in S_:
            if not r["taken"]: c[r["cause"]] = c.get(r["cause"], 0) + 1
        summ[name] = dict(n=len(S_), taken=sum(r["taken"] for r in S_), lost=c)
    wsr = [r for r in rows if r["kind"] == "ws"]; ths = np.array([r["th"] for r in wsr])
    out = dict(leader=leader, margin=margin, refit=refit, bench=[nc, nw], mode=B.mode, exact=os.environ.get("CB_EXACT") == "1",
               params=P, seats=R["seats"], window=[round(lo, 2), round(hi, 2)], fit_fast=R["fit"], model=R["model"],
               corrected=R["corrected"], extra=R["extra"], hub_f=R["hub_f"], summary=summ,
               th_ws_pct={str(q): round(float(np.percentile(ths, q)), 1) for q in (0, 1, 5, 10, 50, 90, 95, 99, 100)},
               secs=round(time.time() - t0, 1))
    cols = ["i", "kind", "clip", "plane", "elev", "axial", "th", "taken", "cause", "dmin", "smin", "mu", "groups"]
    out["cols"] = cols; out["rows"] = [[r[c] for c in cols] for r in rows]
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    with open(outp, "w") as fh:
        fh.write(json.dumps({k: v for k, v in out.items() if k != "rows"}, default=float)[:-1] + ', "rows": [\n')
        fh.write(",\n".join(json.dumps(r, default=float) for r in out["rows"]) + "]}\n")
    print(json.dumps(dict(leader=leader, margin=margin, refit=refit, mode=B.mode, window=out["window"], model=R["model"],
                          corrected=R["corrected"], summary=summ, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()

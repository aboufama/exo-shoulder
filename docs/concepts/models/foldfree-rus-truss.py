"""foldfree-rus-truss: the human-closed 3-RUS truss (three active crank hubs on the scapula, three O5 rods to ball
studs on the arm, the wearer's own glenohumeral joint as the closing spherical joint) with every leg seeded from the
fold-free (c, q) pairs of docs/research/fold/ends.json, as a FOLD LEVER for the 3-DOF shoulder.

Why (spherical-linkage view, docs/concepts/foldfree-rus-truss.md):
  * every serial 3R that reproduces the arm's rotation folds when the angle between the scapula-fixed J1 and the
    humerus-fixed J3 leaves [|a1 - a2|, a1 + a2]; ONE fold band for the whole chain;
  * in a 3-RUS truss closed by the user's GH (GH fixed in S on the bench) each leg's triangle GH-T-Q is rigid, so each
    leg is a spherical RRR whose own fold band is angle(c_k, Q_k) in [|beta_k - gamma_k|, beta_k + gamma_k]
    (beta = crank arc, gamma = the T-Q angle set by the rod length): THREE independent fold bands, one per leg, each
    choosable from the fold-free pairs (posterior-horizontal crank axes, posterior arm studs: 100 % of the workspace
    fold-free at 65 / 65), plus one parallel singularity (det of the three leg moment lines GH x (T x Q));
  * mobility (Grubler-Kutzbach on the bench, GH fixed): 3 legs x (R 1 + U 2 + S 3) + GH 3 = 21 joint freedoms,
    3 loops x 6 = 18 constraints -> 3, of which the 3 rod spins are idle (killed by the U's pitch pin) -> the arm's 3
    rotations <-> the 3 crank angles, exactly 3, no undetermined coordinate. A numeric rank check of the 3 x 3 leg
    Jacobian is the model's `det` (>= 0.10 to take a pose).
Every joint is a catalogue part: O20 bearing hubs (12.25 stack), O12 U-joint housings, O12 rod ends on studs, O5 Ti
rods; 0 passive translations. Rotations only, no gears / pulleys / cables.

Geometry, fitting, part checks, continuity and scoring are the verified-in-structure code of
docs/concepts/models/human-closed-crank-rods.py (imported, not copied); this file adds the fold-free seeding, the
per-leg fold diagnostics, the bench_eval hook for tools/cloud_run.py sweep, and the frozen / red-team modes.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/foldfree-rus-truss.py check '<params json>' [--big] [--exact]
"""
import importlib.util, json, math, os, sys, time, types
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))

# Explicit source patches to the base model (each must match exactly once; asserted on load). Option `studs3`: all
# three legs get their own saddle stud on the arm (the base ties leg 0's stud to the user's BOTTOM bar, whose
# location is fixed 60-120 mm down the lateral arm; the fold-free legs want studs at the humeral-head level,
# posterior-medial: leg_bands in docs/concepts/foldfree-rus-truss.md). Ball k is the joint partner of saddle k.
PATCHES = [
    ('    D["q"] = q; D["sad"] = sad\n',
     '    if P.get("studs3"): q = q[1:]\n    D["q"] = q; D["sad"] = sad\n'),
    ('        if x.startswith("ball") and (H_body(y)) and (x == "ball0" and y == "bar" or x != "ball0" and y == f"sad{int(x[4:]) - 1}"): return True\n',
     '        if x.startswith("ball") and (H_body(y)) and ((y == "sad" + x[4:]) if D["P"].get("studs3") else (x == "ball0" and y == "bar" or x != "ball0" and y == f"sad{int(x[4:]) - 1}")): return True\n'),
]


def load_base(extra=(), name="hccr_patched", glb=None):
    src = open(os.path.join(HERE, "human-closed-crank-rods.py")).read()
    for old, new in list(PATCHES) + list(extra):
        n = src.count(old)
        assert n == 1, f"patch target found {n} times: {old[:80]!r}"
        src = src.replace(old, new)
    m = types.ModuleType(name); m.__file__ = os.path.join(HERE, "human-closed-crank-rods.py")
    m.__dict__.update(glb or {})
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


H = load_base()
CB = H.CB

ID = "foldfree-rus-truss"
NAME = "Fold-free human-closed 3-RUS truss: three scapula crank hubs, O5 rods to arm ball studs, the user's GH closes the loop"

# fold-free seed (ends.json: posterior-horizontal crank axis + posterior arm stud is fold-free on 100 % at 65 / 65)
PARAMS = dict(H.PARAMS)
PARAMS.update(hubs=[[-30.0, 8.0], [-24.0, 78.0], [60.0, 75.0]], beta=[50.0, 50.0, 50.0], sigma=[1, 1, 1],
              studs=[[40.0, 75.0], [110.0, 45.0]])

_CTX = {}


def ctx(B):
    k = id(B)
    if k not in _CTX: _CTX.clear(); _CTX[k] = H.Ctx(B)
    return _CTX[k]


def leg_fold(D, X):
    """per leg: share of workspace poses whose closure exists with transmission >= trans (the leg's own fold band),
    and the c-Q angle range over the workspace (deg)"""
    K = D.get("K")
    if K is None: return None
    ws = ~X.clip; out = []
    for k in range(3):
        c = np.einsum("nij,j->ni", X.RS, D["c"][k]); q = np.einsum("nij,j->ni", X.RH, H.unit(D["q"][k]))
        ang = np.degrees(np.arccos(np.clip((c * q).sum(-1), -1, 1)))
        out.append(dict(ok_ws=round(float(K["okk"][ws, k].mean()), 3), ang_ws=[round(float(ang[ws].min()), 1), round(float(ang[ws].max()), 1)]))
    return dict(legs=out, det_ok_ws=round(float((K["det"][ws] >= D["P"]["det"]).mean()), 3),
                all_ok_ws=round(float((K["okk"].all(1) & (K["det"] >= D["P"]["det"]))[ws].mean()), 3))


def bench_eval(B, params):
    P = dict(PARAMS); P.update(params or {})
    X = ctx(B); r, D = H.evaluate(P, X, log=None)
    try: r["fold"] = leg_fold(D, X)
    except Exception as e: r["fold"] = repr(e)
    r["passive_translations"] = 0
    return r


FLAT = ("az0", "el0", "az1", "el1", "az2", "el2", "b0", "b1", "b2", "s1", "t1", "s2", "t2", "s3", "t3", "h_stud")


def nest(p):
    """flat CMA parameters (FLAT, + sg0..sg2 branch signs) -> the model's nested PARAMS"""
    q = {k: v for k, v in p.items() if k not in FLAT and not k.startswith("sg")}
    if "az0" in p: q["hubs"] = [[float(p[f"az{k}"]), float(p[f"el{k}"])] for k in range(3)]
    if "b0" in p: q["beta"] = [float(p[f"b{k}"]) for k in range(3)]
    if "sg0" in p: q["sigma"] = [int(round(p[f"sg{k}"])) for k in range(3)]
    if "t1" in p:
        q["studs3"] = True; q["studs"] = [[float(p[f"s{k}"]), float(p[f"t{k}"])] for k in (1, 2, 3)]
    elif "s2" in p: q["studs"] = [[float(p["s2"]), float(p["t2"])], [float(p["s3"]), float(p["t3"])]]
    for k in ("h_stud",):
        if k in p: q[k] = float(p[k])
    return q


def flat(P):
    out = {}
    for k in range(3):
        out[f"az{k}"], out[f"el{k}"] = P["hubs"][k]; out[f"b{k}"] = P["beta"][k]; out[f"sg{k}"] = P["sigma"][k]
    out["s2"], out["t2"] = P["studs"][0]; out["s3"], out["t3"] = P["studs"][1]; out["s1"] = P["s1"]; out["h_stud"] = P["h_stud"]
    return out


def evaluate(B, p):
    """tools/concept_cma.py hook: flat params -> (params, report). honest = the model's own checks (K3 march, 10 fps
    branch continuity on every crank / U / ball angle, 1 mm part clearance, contact rule) all on, which they always are."""
    q = nest(p); r = bench_eval(B, q); r["honest"] = True
    for k in ("rT", "L", "F"): r.pop(k, None)
    return dict(p), r


def wear(D, X, near=1.0):
    """wear a FROZEN design D (fitted elsewhere) on the bench of X without refitting (lesson c). Returns the report, the
    near-touch report (< near mm counted as contact, lesson d), the overhead split (lesson e) and red-team facts."""
    P = D["P"]; B = X.B; B.reset()
    K = H.kin(D, X.RS, X.RH, P["trans"]); D2 = dict(D); D2["K"] = K
    valid = K["okk"].all(1) & (K["det"] >= P["det"]); D2["valid"] = valid
    bad, cinfo = H.continuity(D2, X); flipped = valid & X.clip & bad
    idx = np.nonzero(valid)[0]; allp = H.parts(D2, X, idx); mins = {}; who = {}; why = {}
    for a, i in enumerate(idx):
        if flipped[i]: B.record(i, None); continue
        M = allp[a]; col = H.collide(M, D2, i)
        if col: why[col] = why.get(col, 0) + 1; B.record(i, None); continue
        names = [m for m in M]; sc = np.concatenate([M[m]["score"] for m in names])
        ex = np.concatenate([M[m]["extra"] for m in names if not M[m].get("user")])
        de = B.dist(i, ex) if len(ex) else np.array([np.inf])
        if de.min() < 0: sc = np.concatenate([sc, ex[np.argmin(de)][None]])
        d = B.record(i, sc); mn = float(min(d.min(), de.min()))
        mins[int(i)] = mn
        o = 0; best = (np.inf, "")
        for m in names:
            n_ = len(M[m]["score"]); dd = d[o:o + n_]; o += n_
            if n_ and dd.min() < best[0]: best = (float(dd.min()), m)
        who[int(i)] = best[1] if best[0] <= de.min() else "contact-only:" + best[1]
    r = B.report()
    ws = np.nonzero(~X.clip)[0]
    arm = np.einsum("nij,j->ni", X.RH, np.array([0.0, -1.0, 0.0]))
    elev = np.degrees(np.arccos(np.clip(arm @ np.array([0.0, 0.0, -1.0]), -1, 1)))
    taken = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(X.n)])
    over = ws[elev[ws] >= 140]
    legbad = [int((~K["okk"][ws, k]).sum()) for k in range(3)]
    detbad = int(((K["det"] < P["det"]) & K["okk"].all(1))[ws].sum())
    tk = [i for i in mins]; mn_i = min(tk, key=lambda i: mins[i]) if tk else None
    red = dict(min_metal_mm=round(mins[mn_i], 2) if mn_i is not None else None, min_pose=mn_i, min_member=who.get(mn_i),
               min_elev=round(float(elev[mn_i]), 1) if mn_i is not None else None,
               worst_det_taken=round(float(K["det"][[i for i in tk]].min()), 3) if tk else None,
               worst_trans_deg_taken=round(float(np.degrees(np.arcsin(np.clip(K["tr"][tk].min(), 0, 1)))), 1) if tk else None,
               fold_ws_by_leg=legbad, parallel_sing_ws=detbad, collide=why, flipped=int(flipped.sum()),
               overhead_n=int(len(over)), overhead_reach=round(float(taken[over].mean()), 3) if len(over) else None,
               rT=[round(x, 1) for x in D["rT"]], L=[round(x, 1) for x in D["L"]], F=[round(x, 1) for x in D["F"]])
    for i, mn in mins.items():                                     # near-touch: < near mm -> contact
        if 0 <= mn < near: B.res[i] = np.append(B.res[i], -0.01)
    rn = B.report(); B.reset()
    return r, rn, red


def frozen(params, nc=110, nw=360, exact=True):
    """fit on Bench(60,160) fast, wear the frozen shape on Bench(nc, nw) (exact path)"""
    P = dict(PARAMS); P.update(params or {})
    old = os.environ.pop("CB_EXACT", None)
    try:
        B0 = CB.Bench(60, 160); X0 = H.Ctx(B0); D = H.build(P, X0)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    if exact: os.environ["CB_EXACT"] = "1"
    B1 = CB.Bench(nc, nw); X1 = H.Ctx(B1)
    r, rn, red = wear(D, X1)
    r0, rn0, red0 = wear(D, X0)
    return dict(fit_bench=[60, 160, B0.mode], wear_bench=[nc, nw, B1.mode], report=r, near_touch=rn, redteam=red,
                fit_report=r0, fit_near_touch=rn0, fit_redteam=red0)



if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "check"
    par = json.loads(a[1]) if len(a) > 1 and a[1].startswith("{") else {}
    if "--exact" in a: os.environ["CB_EXACT"] = "1"
    nc, nw = (110, 360) if "--big" in a else (60, 160)
    t0 = time.time()
    if mode == "frozen":
        out = frozen(par, nc, nw, exact=True)
        print(json.dumps(dict(secs=round(time.time() - t0, 1), **out), indent=1, default=float))
        if len(a) > 2 and not a[2].startswith("-"): json.dump(out, open(a[2], "w"), indent=1, default=float)
        sys.exit(0)
    B = CB.Bench(nc, nw)
    r = bench_eval(B, par)
    print(json.dumps(dict(mode=B.mode, bench=[nc, nw], secs=round(time.time() - t0, 1), report=r), indent=1, default=float))

#!/usr/bin/env python3
"""FINAL POLISH of skin-normal-3r-pin-knee on the verification bench Bench(110,360) (CLAUDE.md rule "Every generation ends
in a full CAD + render of its winner": a wide multi-start optimisation of every free parameter directly on the
verification bench, fast grid cache for the search, the exact path for the claim, on the CPU farm).

Objective = the near-touch gap of the adversarial verifier's CORRECTED set on Bench(110,360), shape fitted there (fast
grid): docs/concepts/verify/skin-normal-3r-pin-knee.py's extra checks (independent 3D closure, knee vs hub 3's upper
half at 1 mm, the E boss vs hubs / links) knock poses out, then MK.audit counts every taken pose with metal (scored
undersides AND walls / crowns / tops / edges) < 1 mm off the skin as contact. The plain corrected gap is logged next to
it. No check is loosened: the verifier's checks and the model's audit run unchanged; this file only drives them.

    python3 tools/knee_polish.py cma --x0 J --label L --out O [--fixed J] [--state S] [--sigma s] [--popsize 16]
                                     [--jobs 2] [--budget-s T] [--seed k] [--obj near1|gap]
    python3 tools/knee_polish.py scan OUT 'LIST OF PARAM DICTS' [--jobs 2]       evaluate a list (e.g. hub combos) on the bench
    python3 tools/knee_polish.py measure TASK OUT 'PARAMS'   TASK: big (refit on Bench(110,360); CB_EXACT=1 -> exact) |
                                     frozen_big (fit Bench(110,360) fast, worn on Bench(110,360), CB_EXACT=1 -> exact) |
                                     held (fit Bench(110,360) fast, worn on a DISJOINT exact bench of 110 + 360 poses) |
                                     s60 (Bench(60,160) fast refit, the screening bench)
    python3 tools/knee_polish.py log RUN1.json [RUN2.json ...]   merge CMA rows into the sweep log (stage polish-big-*), gate
The cache: tools/osn_polish.py assemble 110 360 osnp/b110_360 /tmp/osnpb (farm volume parts, key 14f156cb6fc8).
"""
import importlib.util, json, math, multiprocessing as mp, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "skin-normal-3r-pin-knee"
SWEEP = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
# name: (CMA scale at sigma 1, lower, upper, why). Angles phiE / phib are periodic: never clipped (cos / sin in the model).
FREE = {
    "az1": (4.0, 60.0, 135.0, "J1 seat ray azimuth (scapula frame bvec); axis = the GH ray (exact closure)"),
    "el1": (3.0, 35.0, 80.0, "J1 seat ray elevation"),
    "az2": (6.0, -40.0, 60.0, "J2 home seat ray azimuth; axis = the GH ray; the J2 branch follows from the seats"),
    "el2": (4.0, 20.0, 75.0, "J2 home seat ray elevation"),
    "wd": (4.0, 50.0, 110.0, "J3 seat on the arm: angle from the humerus axis (band frame w_dir)"),
    "wa": (4.0, -45.0, 20.0, "J3 seat azimuth around the humerus"),
    "b3": (0.08, -0.3, 1.0, "J3 axis tilt from the GH ray toward the skin normal (free: the knee closes any planar drift)"),
    "lE": (4.0, 20.0, 90.0, "hub 3 centre -> pin a (E strap + O12 boss; >= O20 rim + boss + 4; <= 90 keeps the pad on the upper-arm cuff - round 1 used <= 60 and stream H pinned it there)"),
    "lc": (4.0, 14.0, 50.0, "pin a -> pin b (knee link; >= two O12 bosses + 2)"),
    "phiE": (12.0, None, None, "E direction in hub 3's plane at mid drift (deg, periodic)"),
    "phib": (12.0, None, None, "knee link direction at mid drift (deg, periodic); with phiE it sets the arm pad and the branch"),
    "ang_min": (3.0, 20.0, 45.0, "knee window [ang_min, 180 - ang_min]: >= 20 deg off both singular postures"),
    "stk": (0.3, 4.5, 6.0, "pin stack: 4.5 = two 2.0 mm Ti plates + washer on the iglidur pin (catalogue IGLIDUR-PIN 4.5-5), "
                           "6.0 = MR63ZZ pair"),
}
DISCRETE = {"rad1": (10.0, 8.5, 7.5), "rad2": (10.0, 8.5, 7.5), "rad3": (10.0, 8.5, 7.5)}
FIXED_NOTE = ("fixed: b1 = b2 = 0 (J1 / J2 on GH rays: the knee is PLANAR and closes the link-2 -> arm motion exactly only "
              "then; a tilt makes the drift non-planar, which two pins parallel to J3 cannot absorb - it would need a passive "
              "translation along the pins), R_tol 0.5 (honesty rule), neck (not a parameter of this design: the E strap "
              "replaced the neck; k4598 at neck 13 and 25 give the same report), BOSS_R / PAD_R 6 (O12 pin bosses), "
              "KNEE_W 10, strap 8 x 3, hub stack 12.25 (MR117-2RS pair), CLEAR 2 / PART_CLEAR 1 / ADJ 0.15 / ramp 60 deg "
              "(rules, not loosened). Hub radii: discrete catalogue set per stream (rad1-3 in {10 O20, 8.5 O17, 7.5 O15}).")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


_V = {}


def verifier():
    if "V" not in _V:
        _V["V"] = _load("knee_verify", os.path.join(REPO, "docs", "concepts", "verify", ID + ".py"))
    return _V["V"]


def base_params():
    return dict(verifier().ROW["best_params"])


def _taken(B, i): return B.res[i] is not None and float(np.min(B.res[i])) >= 0


def score_model(M, B, r, P):
    """the verifier's corrected set + audit on a model that has run on bench B"""
    V = verifier(); MK = V.MK
    ex, bad = V.extra_checks(M, B)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); aud = MK.audit(M, B)
    tk = [i for i in range(len(B.idx)) if _taken(B, i)]
    ang = M.K["ang"][tk] if tk else np.array([90.0])
    lever = float(P["lE"]) * np.sin(np.radians(np.minimum(ang, 180 - ang))) if tk else np.array([0.0])
    B.res = res0
    out = dict(gap=rc["gap"], reach=rc["reach"], follow=rc["follow"], inband14=rc["inband14"], inband10=rc["inband10"],
               contact=rc["contact"], gap_near1=aud["gap_near1"], gap_near2=aud["gap_near2"], near1_poses=aud["near1_poses"],
               near_min=aud["near_touch_min_mm"], model_gap=r["gap"], why=r.get("why"), f=r.get("f"),
               knee_ang=[round(float(ang.min()), 1), round(float(ang.max()), 1)], j3_lever_min=round(float(lever.min()), 1),
               extra_bad=len(bad), closure_bad=ex["closure_bad_poses"], kh3_bad=ex["knee_vs_hub3_upper_bad"], boss_bad=ex["boss_bad"],
               spans=ex["spans_deg"], tr=round(float(M.tr), 1), hubs=list(M.hr), parts_pairs=r.get("parts_pairs"),
               oh140=dict(reach=aud["overhead140"]["reach"], inband14=aud["overhead140"]["inband14"]), mode=B.mode)
    return out, aud, ex


def evaluate(B, p):
    V = verifier(); MK = V.MK; P = base_params(); P.update(p)
    M = MK.Model(B, dict(P))
    if not M.kin_ok.any():
        B.reset(); r = B.report()
        rep = dict(gap=r["gap"], reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, gap_near1=r["gap"],
                   gap_near2=r["gap"], near_min=None, model_gap=r["gap"], why={k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure")},
                   hubs=list(M.hr), mode=B.mode, nothing_closes=True)
        return rep, M, None
    r = M.run(); rep, aud, ex = score_model(M, B, r, P)
    return rep, M, aud


# ---------------------------------------------------------------------------------------------------------------------
# CMA-ES (tools/osn_polish.py's: bounded by clipping + a quadratic penalty, periodic angles free; resumable state)
_W = {}


def _init(nc, nw):
    os.environ.setdefault("OMP_NUM_THREADS", "1"); verifier(); _W["B"] = CB.Bench(nc, nw)


def snap(p):
    q = dict(p)
    for k, lev in DISCRETE.items():
        if k in q: q[k] = float(min(lev, key=lambda v: abs(v - float(q[k]))))
    return q


def _eval(arg):
    tag, p, objk = arg; t0 = time.time()
    try:
        rep, M, a = evaluate(_W["B"], snap(p))
        return dict(tag=tag, params=p, report=rep, obj=float(rep["gap_near1"] if objk == "near1" else rep["gap"]), secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-800:], secs=round(time.time() - t0, 1))


def cma(a):
    keys = [k for k in FREE if k not in json.loads(a.fixed or "{}")]; n = len(keys)
    s0 = np.array([FREE[k][0] for k in keys])
    lo = np.array([FREE[k][1] if FREE[k][1] is not None else -np.inf for k in keys])
    hi = np.array([FREE[k][2] if FREE[k][2] is not None else np.inf for k in keys])
    fixed = json.loads(a.fixed) if a.fixed else {}
    st = json.load(open(a.state)) if a.state and os.path.exists(a.state) else None
    lam = a.popsize; mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1.0 / (w ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3) ** 2 + mueff); cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs; chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
    if st:
        c0 = np.array(st["c0"]); mean = np.array(st["mean"]); sigma = st["sigma"]; C = np.array(st["C"]); pc = np.array(st["pc"])
        ps = np.array(st["ps"]); gen = st["gen"]; best = st["best"]
    else:
        x0 = json.loads(a.x0); bp = base_params(); c0 = np.array([float(x0.get(k, bp.get(k))) for k in keys])
        mean = np.zeros(n); sigma = a.sigma; C = np.eye(n); pc = np.zeros(n); ps = np.zeros(n); gen = 0; best = None
    D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20))

    def to_p(z):
        x = c0 + s0 * z; xc = np.clip(x, lo, hi); pen = float(50.0 * (((x - xc) / s0) ** 2).sum())
        return dict(fixed, **{k: float(round(v, 4)) for k, v in zip(keys, xc)}), pen

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    rows = json.load(open(a.out)) if st and os.path.exists(a.out) else []
    t_start = time.time(); pool = mp.get_context("fork").Pool(a.jobs, initializer=_init, initargs=(a.nc, a.nw))

    def dump():
        json.dump(rows, open(a.out + ".tmp", "w"), indent=1, default=float); os.replace(a.out + ".tmp", a.out)
        json.dump(dict(c0=c0.tolist(), mean=mean.tolist(), sigma=sigma, C=C.tolist(), pc=pc.tolist(), ps=ps.tolist(), gen=gen,
                       best=best, keys=keys, label=a.label, fixed=fixed, obj=a.obj), open(a.state_out + ".tmp", "w"), default=float)
        os.replace(a.state_out + ".tmp", a.state_out)
    if gen == 0:
        p, _ = to_p(np.zeros(n)); r = pool.map(_eval, [(f"{a.label}-g0-x0", p, a.obj)])[0]; r["gen"] = 0; rows.append(r)
        best = dict(obj=r["obj"], params=r["params"], tag=r["tag"]); dump()
        print(f"[{a.label}] x0 {r['obj']:.2f} {r.get('error', '')} {r['secs']}s", flush=True)
    gen_secs = 0.0; stop = ""
    while gen < a.max_gen and time.time() - t_start + gen_secs * 1.15 < a.budget_s:
        gen += 1; tg = time.time(); rng = np.random.default_rng([a.seed, gen])
        Z = rng.standard_normal((lam, n)); Y = (Z * D) @ Bm.T; X = mean + sigma * Y
        pp = [to_p(X[i]) for i in range(lam)]
        res = pool.map(_eval, [(f"{a.label}-g{gen}-{i}", pp[i][0], a.obj) for i in range(lam)])
        f = np.array([r["obj"] + pp[i][1] for i, r in enumerate(res)])
        for r in res: r["gen"] = gen; r["sigma"] = round(sigma, 4); rows.append(r)
        i0 = int(np.argmin([r["obj"] for r in res]))
        if res[i0]["obj"] < best["obj"]: best = dict(obj=res[i0]["obj"], params=res[i0]["params"], tag=res[i0]["tag"])
        idx = np.argsort(f)[:mu]; old = mean.copy(); mean = (w[:, None] * X[idx]).sum(0)
        invsqrtC = Bm @ np.diag(1 / D) @ Bm.T
        ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * invsqrtC @ (mean - old) / sigma
        hsig = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * gen)) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hsig * math.sqrt(cc * (2 - cc) * mueff) * (mean - old) / sigma
        art = (X[idx] - old) / sigma
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hsig) * cc * (2 - cc) * C) + cmu * (art.T * w) @ art
        sigma *= math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        C = np.triu(C) + np.triu(C, 1).T; D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20))
        gen_secs = time.time() - tg; dump()
        print(f"[{a.label}] gen {gen} best-in-gen {min(r['obj'] for r in res):.2f} best {best['obj']:.2f} sigma {sigma:.3f} "
              f"{gen_secs:.0f}s elapsed {time.time() - t_start:.0f}s", flush=True)
        if sigma * D.max() < 0.02: stop = "sigma collapsed"; print("[cma] sigma collapsed: stop", flush=True); break
    pool.close(); dump()
    print(json.dumps(dict(label=a.label, gen=gen, evals=len(rows), best=best, stop=stop), default=float))


def scan(outp, plist, jobs=2, nc=110, nw=360, objk="near1"):
    pool = mp.get_context("fork").Pool(jobs, initializer=_init, initargs=(nc, nw)); t = time.time()
    res = pool.map(_eval, [(f"scan-{i}", p, objk) for i, p in enumerate(plist)]); pool.close()
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True); json.dump(res, open(outp, "w"), indent=1, default=float)
    for r in res:
        rep = r.get("report") or {}
        print(r["tag"], {k: r["params"].get(k) for k in ("rad1", "rad2", "rad3")}, "obj", r["obj"], "gap", rep.get("gap"), "near1", rep.get("gap_near1"),
              "r/f/ib/c", rep.get("reach"), rep.get("follow"), rep.get("inband14"), rep.get("contact"), "why", rep.get("why"), r.get("error", ""), r["secs"], flush=True)
    print(f"scan: {len(res)} configs in {time.time() - t:.0f}s")


# ---------------------------------------------------------------------------------------------------------------------
# measurement protocols (the verifier's model + checks + audit; the exact path with CB_EXACT=1)
def held_bench(nc=110, nw=360):
    import osn_polish as OP
    return OP.held_bench(nc, nw)


def frozen_on(fitB, wearB, P):
    """the verifier's frozen protocol with the fit bench as an argument: fit on fitB, wear that exact shape (heights, knee
    reference m) on wearB without refit (same attribute copy as docs/concepts/verify/skin-normal-3r-pin-knee.py)"""
    V = verifier(); MK = V.MK
    M1 = MK.Model(fitB, dict(P)); r1 = M1.run(); fitrep, _, _ = score_model(M1, fitB, r1, P)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(MK.Model):
        def fit(self):
            for at in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                       "Hneed", "Lneed", "hEx", "_Ex", "_h12"):
                if hasattr(M1, at): setattr(self, at, getattr(M1, at))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    return Frozen(wearB, P2), fitrep, P2


def measure(task, outp, p):
    P = base_params(); P.update(p); P = snap(P); t0 = time.time(); out = dict(task=task, params=P)
    exact = os.environ.get("CB_EXACT") == "1"
    if task in ("s60", "big"):
        nc, nw = (60, 160) if task == "s60" else (110, 360)
        B = CB.Bench(nc, nw); rep, M, a = evaluate(B, P); out["report"] = rep; out["audit"] = a; out["wear_mode"] = B.mode
    elif task in ("frozen_big", "held"):
        old = os.environ.pop("CB_EXACT", None)
        try:
            fitB = CB.Bench(110, 360)
        finally:
            if old is not None: os.environ["CB_EXACT"] = old
        wearB = held_bench() if task == "held" else CB.Bench(110, 360)
        M, fitrep, P2 = frozen_on(fitB, wearB, P); r = M.run(); rep, a, ex = score_model(M, wearB, r, P)
        out["fit"] = fitrep; out["fit_mode"] = fitB.mode; out["report"] = rep; out["audit"] = a; out["extra"] = ex; out["wear_mode"] = wearB.mode
    else:
        raise SystemExit("unknown task " + task)
    out["exact_env"] = exact; out["secs"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True); json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(task=task, report={k: out["report"].get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "mode", "gap_near1", "near_min", "near1_poses")},
                          fit=({k: out["fit"][k] for k in ("gap", "gap_near1", "mode")} if "fit" in out else None), secs=out["secs"]), default=float), flush=True)


def score(gap): return 100.0 * (1.0 - gap / 275.0)


def gate(objs):
    """docs/METHOD.md convergence gate on a history of objectives (in order): < 1 score point gained over the second half,
    < 0.5 over the last third, top-5 within 3 points"""
    s = np.array([score(g) for g in objs]); n = len(s)
    if n < 6: return dict(n=n, ok=False)
    best = np.maximum.accumulate(s)
    gh = float(best[-1] - best[n // 2 - 1]); gt = float(best[-1] - best[n - n // 3 - 1]); top = np.sort(s)[::-1][:5]
    return dict(n=n, gain_half=round(gh, 2), gain_third=round(gt, 2), top5_spread=round(float(top[0] - top[-1]), 2),
                ok=bool(gh < 1.0 and gt < 0.5 and top[0] - top[-1] < 3.0))


def log_rows(files, write=True):
    """merge the polish rows into the sweep log (stage polish-big-<stream>, bench noted); returns the polish history in
    evaluation order (by generation, then stream) and the gate on its objective"""
    d = json.load(open(SWEEP)); have = {r.get("tag") for r in d if str(r.get("stage", "")).startswith("polish-big")}
    k = max(r["k"] for r in d) + 1; base = base_params(); new = []
    rows = []
    for f in files:
        for r in json.load(open(f)): rows.append(r)
    stream = lambda r: r["tag"].rsplit("-", 2)[0]
    rows.sort(key=lambda r: (r.get("gen", 0), stream(r), r["tag"]))
    for r in rows:
        if r["tag"] in have: continue
        rep = r.get("report") or {}
        p = snap(dict(base, **r["params"]))
        row = dict(k=k, t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), stage="polish-big-" + stream(r),
                   bench="Bench(110,360) fast, shape fitted there, verifier checks (3D closure, knee vs hub 3 upper, E boss)",
                   params=p, **{m: rep.get(m) for m in ("inband14", "inband10", "reach", "follow", "contact")},
                   gap=rep.get("gap") if not r.get("error") else None, gap_near1=rep.get("gap_near1"), obj=r["obj"],
                   near_min=rep.get("near_min"), model_gap=rep.get("model_gap"), why=rep.get("why"), knee_ang=rep.get("knee_ang"),
                   j3_lever_min=rep.get("j3_lever_min"), hubs=rep.get("hubs"), honest=not r.get("error"), tag=r["tag"], gen=r.get("gen"),
                   src="polish-big")
        if r.get("error"): row["error"] = r["error"]
        new.append(row); have.add(r["tag"]); k += 1
    if write and new:
        d += new; json.dump(d, open(SWEEP + ".tmp", "w"), indent=1, default=float); os.replace(SWEEP + ".tmp", SWEEP)
    allp = [r for r in d if str(r.get("stage", "")).startswith("polish-big")] if write else new
    hist = [r["obj"] if r.get("obj") is not None else 400.0 for r in allp]
    return allp, gate(hist), len(new)


def main():
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    if a[0] == "log":
        allp, g, nn = log_rows(a[1:]); ok = [r for r in allp if r.get("gap") is not None]; ok.sort(key=lambda r: r["obj"])
        print(f"logged {nn} new rows; polish history {len(allp)}; gate {g}")
        for r in ok[:10]: print(r["k"], r["tag"], "obj", r["obj"], "gap", r["gap"], r["reach"], r["follow"], r["inband14"], r["contact"], r.get("hubs"),
                                {k: r["params"].get(k) for k in FREE})
    elif a[0] == "measure":
        measure(a[1], a[2], json.loads(a[3]) if len(a) > 3 else {})
    elif a[0] == "scan":
        jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
        objk = a[a.index("--obj") + 1] if "--obj" in a else "near1"
        scan(a[1], json.loads(a[2]), jobs, objk=objk)
    elif a[0] == "cma":
        import argparse
        ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
        ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
        ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.5)
        ap.add_argument("--popsize", type=int, default=16); ap.add_argument("--jobs", type=int, default=2)
        ap.add_argument("--budget-s", type=float, default=3000); ap.add_argument("--max-gen", type=int, default=400)
        ap.add_argument("--seed", type=int, default=1); ap.add_argument("--nc", type=int, default=110); ap.add_argument("--nw", type=int, default=360)
        ap.add_argument("--obj", default="near1", choices=("near1", "gap"))
        x = ap.parse_args(a); x.state_out = x.state_out or (x.out + ".state.json"); cma(x)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

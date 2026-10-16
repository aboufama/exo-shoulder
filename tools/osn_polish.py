#!/usr/bin/env python3
"""FINAL POLISH of offset-skin-normal-3r on the verification bench Bench(110,360) (CLAUDE.md rule, user 2026-10-16:
"the winning designs get a big GPU run right just to squeeze out that last possible optimization"). The bench is CPU
(libigl exact path + the signed-distance grid cache), so the CPU farm is the instrument (tools/cloud_run.py).

Objective = the CORRECTED gap of the adversarial verifier (docs/concepts/verify/offset-skin-normal-3r.py: the model's
own checks + outer faces vs skin, link 2 vs member 3) on Bench(110,360), fast grid. No check is loosened: the verifier's
model and audit run unchanged; this file only drives them.

    python3 tools/osn_polish.py buildpart NC NW A B PARTDIR [JOBS]   grid-cache poses [A, B) of Bench(NC, NW) -> PARTDIR
    python3 tools/osn_polish.py assemble NC NW PARTDIR [LOCALDIR]    partials -> LOCALDIR/<key>/{grid,skins}.npy + meta
                                                                     (once per worker, flock), linked as the bench cache
    python3 tools/osn_polish.py cma --x0 J --label L --out O [--state S] [--sigma s] [--popsize 16] [--jobs 2]
                                    [--budget-s T] [--seed k] [--nc 110 --nw 360]
    python3 tools/osn_polish.py measure TASK OUT 'PARAMS'           TASK: big | big_frozen_bigfast | held_frozen_bigfast |
                                                                     s60 (CB_EXACT=1 picks the exact path where it applies)
Free parameters (designer-changeable; bounds keep every hard rule: 2 passive translations, real envelopes, no radial
slide, J1 / J2 on GH rays = b1 = b2 = 0 by the closure theorem): see FREE below.
"""
import fcntl, json, math, multiprocessing as mp, os, shutil, sys, time, traceback
import importlib.util
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

# name: (scale for CMA sigma = 1, lower, upper, why)
FREE = {
    "az1": (4.0, 60.0, 135.0, "J1 seat ray azimuth (scapula frame); axis = the GH ray (exact closure)"),
    "el1": (3.0, 35.0, 80.0, "J1 seat ray elevation"),
    "az2": (6.0, -40.0, 60.0, "J2 home seat ray azimuth; axis = the GH ray; the J2 branch follows from the seats"),
    "el2": (4.0, 20.0, 75.0, "J2 home seat ray elevation"),
    "wd": (4.0, 50.0, 110.0, "J3 seat on the arm, angle from the humerus axis (band frame)"),
    "wa": (4.0, -45.0, 20.0, "J3 seat azimuth around the humerus"),
    "b3": (0.1, -0.3, 1.0, "J3 axis tilt from the GH ray toward the skin normal (line 3 is free by the closure theorem)"),
    "neck": (3.0, 5.0, 30.0, "member-3 neck strap length past hub 3's rim to the stage (8 x 3 strap)"),
    "S_max": (4.0, 4.0, 25.0, "slide travel cap (each slide, mm): shorter rails / less stage metal vs slide-range losses"),
}
FIXED_NOTE = ("fixed: b1 = b2 = 0 (closure theorem: J1 / J2 lines through GH, else radial drift > 0.5 mm), R_tol 0.5 "
              "(honesty rule, no radial slide), inv 1 (inverted along guide), remote 1 + ramp 1 (stage down the arm), centre 1 "
              "and S_auto 1 (stage centre = mid travel, ranges = needed travel + 0.5 mm, both fitted on the bench + every fit-clip "
              "frame), flip3 0/1 (discrete: checked at the start and the best), hub faces / strap undersides (fitted by the model "
              "to the 2 mm clearance rule, not free), CLEAR 2 / PART_CLEAR 1 / ramp 60 deg (rules, not loosened)")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


# ---------------------------------------------------------------------------------------------------------------------
# grid cache in parts (farm) and assembly
def _gp(args):
    import concept_bench as C
    return C._grid_pose(args)


def buildpart(nc, nw, a, b, partdir, jobs=2):
    B = CB.Bench(nc, nw); B.grid = None; n = int(round(2 * CB.HALF / CB.H_GRID)) + 1; b = min(b, len(B.poses))
    os.makedirs(partdir, exist_ok=True); tmpd = os.path.join(os.getcwd(), ".partbuild"); os.makedirs(tmpd, exist_ok=True)
    tmp = os.path.join(tmpd, f"part_{a:04d}_{b:04d}.grid.npy")
    np.lib.format.open_memmap(tmp, mode="w+", dtype=np.int8, shape=(b - a, n, n, n)).flush()
    t = time.time(); Vs = [None] * (b - a); fr = [0.0] * (b - a)
    with mp.get_context("fork").Pool(jobs) as pool:
        for j, frac, V in pool.imap_unordered(_gp, [(B.poses[a + j], tmp, j, n) for j in range(b - a)]):
            Vs[j] = V; fr[j] = frac
    np.save(os.path.join(tmpd, f"part_{a:04d}_{b:04d}.skins.npy"), np.stack(Vs))
    for f in (f"part_{a:04d}_{b:04d}.grid.npy", f"part_{a:04d}_{b:04d}.skins.npy"):
        shutil.copyfile(os.path.join(tmpd, f), os.path.join(partdir, f + ".tmp")); os.replace(os.path.join(partdir, f + ".tmp"), os.path.join(partdir, f))
    json.dump(dict(a=a, b=b, frac=fr, secs=round(time.time() - t, 1)), open(os.path.join(partdir, f"part_{a:04d}_{b:04d}.json"), "w"))
    print(f"buildpart {a}-{b}: {b - a} poses in {time.time() - t:.0f}s, exact share {np.mean(fr):.3f}", flush=True)


def assemble(nc, nw, partdir, localdir=None):
    """partials -> one cache dir (grid.npy, skins.npy, meta.json) and a link at .cache/concept_bench/<key>"""
    idx, _, _, _ = CB._select(nc, nw); key = CB._key(idx); N = len(idx); n = int(round(2 * CB.HALF / CB.H_GRID)) + 1
    dst = os.path.join(localdir or os.path.join("/tmp", "osnpb"), key); os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if not os.path.exists(os.path.join(dst, ".ok")):
            t = time.time(); shutil.rmtree(dst, ignore_errors=True); os.makedirs(dst)
            parts = sorted(f for f in os.listdir(partdir) if f.endswith(".json") and f.startswith("part_"))
            got = np.zeros(N, bool); Vs = [None] * N; fr = []
            G = np.lib.format.open_memmap(os.path.join(dst, "grid.npy"), mode="w+", dtype=np.int8, shape=(N, n, n, n))
            for pj in parts:
                m = json.load(open(os.path.join(partdir, pj))); a, b = m["a"], m["b"]; stem = pj[:-5]
                g = np.load(os.path.join(partdir, stem + ".grid.npy"), mmap_mode="r"); G[a:b] = g
                s = np.load(os.path.join(partdir, stem + ".skins.npy"))
                for j in range(a, b): Vs[j] = s[j - a]
                got[a:b] = True; fr += m["frac"]
            G.flush(); del G
            if not got.all(): raise SystemExit(f"assemble: missing poses {np.nonzero(~got)[0][:10]}")
            np.save(os.path.join(dst, "skins.npy"), np.stack(Vs))
            meta = dict(n_clip=nc, n_ws=nw, poses=N, h=CB.H_GRID, half=CB.HALF, q=CB.Q, exact_share=float(np.mean(fr)),
                        built="farm, tools/osn_polish.py buildpart (concept_bench._grid_pose, same code)", parts=len(parts),
                        created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            json.dump(meta, open(os.path.join(dst, "meta.json"), "w"), indent=1)
            open(os.path.join(dst, ".ok"), "w").write("ok")
            print(f"assemble: {N} poses from {len(parts)} parts in {time.time() - t:.0f}s -> {dst}", flush=True)
    link = os.path.join(CB.CACHE, key); os.makedirs(CB.CACHE, exist_ok=True)
    if not os.path.exists(os.path.join(link, "meta.json")):
        if os.path.islink(link) or os.path.exists(link):
            try: os.remove(link)
            except OSError: shutil.rmtree(link, ignore_errors=True)
        os.symlink(dst, link)
    return dst


# ---------------------------------------------------------------------------------------------------------------------
# evaluation = the verifier's model + audit
_V = {}


def verifier():
    if "V" not in _V:
        _V["V"] = _load("osn_verify", os.path.join(REPO, "docs", "concepts", "verify", "offset-skin-normal-3r.py"))
    return _V["V"]


def base_params():
    V = verifier(); P = dict(V.ROW["best_params"]); return P


def summarise(M, B, r, a, P):
    D = M.D
    out = dict(gap=a["corrected"]["gap"], reach=a["corrected"]["reach"], follow=a["corrected"]["follow"],
               inband14=a["corrected"]["inband14"], inband10=a["corrected"]["inband10"], contact=a["corrected"]["contact"],
               model_gap=r["gap"], why=r.get("why"), S=[M.p.get("S_a"), M.p.get("S_t"), M.p.get("R_r")], f=r.get("f"),
               branch=D.branch, a_deg=[round(math.degrees(x), 1) for x in D.A], tilt_deg=D.seats["tilt_deg"],
               gap_near1=a["gap_near1"], gap_near2=a["gap_near2"], near_min=a["near_touch_min_mm"],
               outer_contact=a["outer_contact_poses"], L2_jams=a.get("L2_member3_jams"),
               oh140=dict(reach=a["overhead140"]["reach"], inband14=a["overhead140"]["inband14_all"]), mode=B.mode)
    return out


def evaluate(B, p):
    V = verifier(); P = base_params(); P.update(p)
    M = V.model_cls(False)(B, dict(P)); r = M.run(); a = V.audit(M, B, r, False)
    return summarise(M, B, r, a, P), M, a


# ---------------------------------------------------------------------------------------------------------------------
# CMA-ES (as tools/concept_cma.py; bounded by clipping + a quadratic penalty; resumable state)
_W = {}


def _init(nc, nw):
    os.environ.setdefault("OMP_NUM_THREADS", "1"); verifier(); _W["B"] = CB.Bench(nc, nw)


def _eval(arg):
    tag, p = arg; t0 = time.time()
    try:
        rep, M, a = evaluate(_W["B"], p)
        return dict(tag=tag, params=p, report=rep, obj=float(rep["gap"]), secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-800:], secs=round(time.time() - t0, 1))


def cma(a):
    keys = list(FREE); n = len(keys)
    s0 = np.array([FREE[k][0] for k in keys]); lo = np.array([FREE[k][1] for k in keys]); hi = np.array([FREE[k][2] for k in keys])
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
        x0 = json.loads(a.x0); c0 = np.array([float(x0.get(k, base_params().get(k, 25.0))) for k in keys])
        mean = np.zeros(n); sigma = a.sigma; C = np.eye(n); pc = np.zeros(n); ps = np.zeros(n); gen = 0; best = None
    D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20))

    def to_p(z):
        x = c0 + s0 * z; xc = np.clip(x, lo, hi); pen = float(50.0 * (((x - xc) / s0) ** 2).sum())
        return dict(fixed, **{k: float(round(v, 4)) for k, v in zip(keys, xc)}), pen

    rows = []; t_start = time.time(); pool = mp.get_context("fork").Pool(a.jobs, initializer=_init, initargs=(a.nc, a.nw))

    def dump():
        json.dump(rows, open(a.out + ".tmp", "w"), indent=1, default=float); os.replace(a.out + ".tmp", a.out)
        json.dump(dict(c0=c0.tolist(), mean=mean.tolist(), sigma=sigma, C=C.tolist(), pc=pc.tolist(), ps=ps.tolist(), gen=gen,
                       best=best, keys=keys, label=a.label), open(a.state_out + ".tmp", "w"), default=float)
        os.replace(a.state_out + ".tmp", a.state_out)
    if gen == 0:
        p, _ = to_p(np.zeros(n)); r = pool.map(_eval, [(f"{a.label}-g0-x0", p)])[0]; r["gen"] = 0; rows.append(r)
        best = dict(obj=r["obj"], params=r["params"], tag=r["tag"]); dump()
        print(f"[{a.label}] x0 {r['obj']:.2f} {r.get('error', '')} {r['secs']}s", flush=True)
    gen_secs = 0.0; stop = ""
    while gen < a.max_gen and time.time() - t_start + gen_secs * 1.15 < a.budget_s:
        gen += 1; tg = time.time(); rng = np.random.default_rng([a.seed, gen])
        Z = rng.standard_normal((lam, n)); Y = (Z * D) @ Bm.T; X = mean + sigma * Y
        pp = [to_p(X[i]) for i in range(lam)]
        res = pool.map(_eval, [(f"{a.label}-g{gen}-{i}", pp[i][0]) for i in range(lam)])
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


# ---------------------------------------------------------------------------------------------------------------------
# measurement protocols (the verifier's model + audit; the exact path with CB_EXACT=1)
def held_bench(nc=110, nw=360, exact=True):
    """a Bench over poses DISJOINT from Bench(110,360): nc fit-clip frames and nw workspace poses from the complement
    (held-out clips Wave / Walking still excluded); exact path (no cache for it)"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
    big, _, _, _ = CB._select(110, 360); bigs = set(big.tolist())
    fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
    cl = np.array([i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in bigs]); ws = np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in bigs])
    cl = cl[np.linspace(0, len(cl) - 1, min(nc, len(cl))).round().astype(int)]; ws = ws[np.linspace(0, len(ws) - 1, min(nw, len(ws))).round().astype(int)]
    B = CB.Bench(20, 20); idx = np.r_[cl, ws]
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws); B.clip = [names[c] for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in P[idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = "held"
    return B


def frozen_on(fitB, wearB, P):
    """the verifier's frozen protocol with the fit bench as an argument: fit on fitB, wear that shape on wearB, no refit"""
    V = verifier(); S = V.S; OSN = V.OSN
    M1 = OSN.Model(fitB, dict(P)); r1 = M1.run(); a1 = V.audit(M1, fitB, r1, False)
    fitrep = summarise(M1, fitB, r1, a1, P)
    P2 = dict(M1.p); P2["S_auto"] = 0

    class Frozen(OSN.Model):
        def __init__(self, B, params):
            super().__init__(B, params)
            self.p["S_a"], self.p["S_t"], self.p["R_r"] = M1.p["S_a"], M1.p["S_t"], M1.p["R_r"]; self.D.m = M1.D.m.copy()
            q, ok, X1, X2, X3, s = self.D.ik(self.Q); self.s = s
            self.why = np.array([""] * len(B.idx), dtype=object); okf = ok.copy(); self.why[~ok] = "fold"
            sok = self.D.slides_ok(s); self.why[ok & ~sok] = "slide"; okf &= sok
            cont = self.continuity(); self.why[okf & ~cont] = "flip"; okf &= cont
            bad = okf & (self.res_deg >= 0.5); self.why[bad] = "closure"; okf &= ~bad; self.kin_ok = okf

        def fit(self):
            for at in ("geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "contact", "cyl", "box", "strap", "cyl_surf",
                       "riser", "riser_h", "riser_pts", "box_strip", "Hneed", "Lneed"):
                if hasattr(M1, at): setattr(self, at, getattr(M1, at))
            self.contact = list(M1.contact)
            self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(wearB, P2)
    return M, fitrep


def measure(task, outp, p):
    V = verifier(); P = base_params(); P.update(p); t0 = time.time(); out = dict(task=task, params=P)
    exact = os.environ.get("CB_EXACT") == "1"
    if task == "s60":
        B = CB.Bench(60, 160); rep, M, a = evaluate(B, p); out["report"] = rep; out["audit"] = a
    elif task == "big":                                              # refit on the big bench (fast or CB_EXACT=1 exact)
        B = CB.Bench(110, 360); rep, M, a = evaluate(B, p); out["report"] = rep; out["audit"] = a
    elif task in ("big_frozen_bigfast", "held_frozen_bigfast", "big_frozen_60fast"):
        nc, nw = (60, 160) if task.endswith("60fast") else (110, 360)
        old = os.environ.pop("CB_EXACT", None)
        try:
            fitB = CB.Bench(nc, nw)
        finally:
            if old is not None: os.environ["CB_EXACT"] = old
        wearB = held_bench() if task.startswith("held") else CB.Bench(110, 360)
        M, fitrep = frozen_on(fitB, wearB, P); r = M.run(); a = V.audit(M, wearB, r, False)
        out["fit"] = fitrep; out["report"] = summarise(M, wearB, r, a, P); out["audit"] = a; out["wear_mode"] = wearB.mode
        out["fit_mode"] = fitB.mode
    else:
        raise SystemExit("unknown task " + task)
    out["exact_env"] = exact; out["secs"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True); json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(task=task, report={k: out["report"][k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "mode", "gap_near1", "near_min")},
                          fit=({k: out["fit"][k] for k in ("gap", "mode")} if "fit" in out else None), secs=out["secs"]), default=float), flush=True)


def score(gap): return 100.0 * (1.0 - gap / 275.0)


def gate(objs):
    """docs/METHOD.md convergence gate on a history of objectives (gap, in order): < 1 score point gained over the second
    half, < 0.5 over the last third, top-5 within 3 points"""
    s = np.array([score(g) for g in objs]); n = len(s)
    if n < 6: return dict(n=n, ok=False)
    best = np.maximum.accumulate(s)
    gh = float(best[-1] - best[n // 2 - 1]); gt = float(best[-1] - best[n - n // 3 - 1]); top = np.sort(s)[::-1][:5]
    return dict(n=n, gain_half=round(gh, 2), gain_third=round(gt, 2), top5_spread=round(float(top[0] - top[-1]), 2),
                ok=bool(gh < 1.0 and gt < 0.5 and top[0] - top[-1] < 3.0))


def log_rows(files, sweep=os.path.join(REPO, "docs", "concepts", "sweeps", "offset-skin-normal-3r.json"), write=True):
    """merge the polish rows (CMA outputs) into the sweep log (stage polish-big-<stream>, bench noted); returns the
    polish history in evaluation order and the gate on it"""
    d = json.load(open(sweep)); have = {r.get("tag") for r in d if str(r.get("stage", "")).startswith("polish-big")}
    k = max(r["k"] for r in d) + 1; base = base_params(); new = []; hist = []
    rows = []
    for f in files:
        for r in json.load(open(f)): rows.append(r)
    rows.sort(key=lambda r: (r.get("gen", 0), r["tag"].split("-")[1], r["tag"]))
    for r in rows:
        rep = r.get("report") or {}
        if r["tag"] in have: continue
        p = dict(base, **r["params"])
        if rep.get("S"): p["S_a"], p["S_t"], p["R_r"] = rep["S"]
        row = dict(k=k, t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), stage="polish-big-" + r["tag"].split("-")[1],
                   bench="Bench(110,360) fast, verifier checks (crowns / strap tops / link 2 vs member 3)", params=p,
                   **{m: rep.get(m) for m in ("inband14", "inband10", "reach", "follow", "contact")}, gap=r["obj"] if not r.get("error") else None,
                   model_gap=rep.get("model_gap"), why=rep.get("why"), S=rep.get("S"), gap_near1=rep.get("gap_near1"),
                   near_min=rep.get("near_min"), honest=not r.get("error"), tag=r["tag"], gen=r.get("gen"))
        if r.get("error"): row["error"] = r["error"]
        new.append(row); k += 1
    if write and new:
        d += new; json.dump(d, open(sweep + ".tmp", "w"), indent=1, default=float); os.replace(sweep + ".tmp", sweep)
    allp = [r for r in d if str(r.get("stage", "")).startswith("polish-big")] if write else new
    hist = [r["gap"] if r.get("gap") is not None else 400.0 for r in allp]
    return allp, gate(hist), len(new)


def main():
    a = sys.argv[1:]
    if a[0] == "log":
        allp, g, nn = log_rows(a[1:]); ok = [r for r in allp if r.get("gap") is not None]; ok.sort(key=lambda r: r["gap"])
        print(f"logged {nn} new rows; polish history {len(allp)}; gate {g}")
        for r in ok[:8]: print(r["k"], r["tag"], r["gap"], r["reach"], r["follow"], r["inband14"], r["contact"], {k: r["params"][k] for k in FREE})
        return
    if a[0] == "buildpart":
        buildpart(int(a[1]), int(a[2]), int(a[3]), int(a[4]), a[5], int(a[6]) if len(a) > 6 else 2)
    elif a[0] == "assemble":
        assemble(int(a[1]), int(a[2]), a[3], a[4] if len(a) > 4 else None)
    elif a[0] == "validate":
        CB.validate(int(a[1]), int(a[2]), int(a[3]) if len(a) > 3 else 20)
    elif a[0] == "measure":
        measure(a[1], a[2], json.loads(a[3]) if len(a) > 3 else {})
    elif a[0] == "cma":
        import argparse
        ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
        ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
        ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.5)
        ap.add_argument("--popsize", type=int, default=16); ap.add_argument("--jobs", type=int, default=2)
        ap.add_argument("--budget-s", type=float, default=1500); ap.add_argument("--max-gen", type=int, default=400)
        ap.add_argument("--seed", type=int, default=1); ap.add_argument("--nc", type=int, default=110); ap.add_argument("--nw", type=int, default=360)
        x = ap.parse_args(a); x.state_out = x.state_out or (x.out + ".state.json"); cma(x)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

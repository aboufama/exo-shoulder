#!/usr/bin/env python3
"""ZERO-COMPLEXITY FRONTIER search (docs/concepts/models/zc-frontier-3r.py): a global Sobol map of the plain spherical 3R
under the user's 2026-10-16 rulings (O20 hubs, fold margin 5, J1 on the back / acromion top), then multi-start CMA on
the verification bench Bench(110,360) (fast grid cache for the search, exact path for the claim).

    python3 tools/zc_frontier.py sobol N OUT.json [--seed s]          N Sobol configs + their fold-law reach on Bench(110,360)
    python3 tools/zc_frontier.py eval CFGS.json OUT.json [--procs 2]  full evaluation (model checks + verifier top_check)
    python3 tools/zc_frontier.py cma --x0 J --out O [--fix J] [--sigma 0.5] [--popsize 8] [--procs 2] [--budget-s T] [--seed k] [--label L]
    python3 tools/zc_frontier.py frozen 'PARAMS' OUT.json             claim: shape fitted on Bench(110,360) FAST, worn on
                                                                      Bench(110,360) EXACT; plus the verifier protocol
                                                                      (fit Bench(60,160) fast -> worn Bench(110,360) exact)
    python3 tools/zc_frontier.py attr 'PARAMS' OUT.json               per-pose attribution on Bench(110,360) (fast fit + wear)
Bench size: ZC_BENCH=110,360 (default). Every row carries the params, the verifier gap (`gap`), near-touch gap (`near`),
the metrics, honest / audit, per-member in-band and the fold-law reach (`kin`).
"""
import argparse, importlib.util, json, math, multiprocessing as mp, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
MODEL = os.path.join(REPO, "docs", "concepts", "models", "zc-frontier-3r.py")
CONT = ("az", "el", "a1", "a2", "wd", "wa", "q", "end_extra")
SCALE = dict(az=6.0, el=4.0, a1=4.0, a2=4.0, wd=4.0, wa=6.0, q=0.03, end_extra=1.5)
_W = {}


def model():
    if "m" not in _W:
        spec = importlib.util.spec_from_file_location("zc_model", MODEL); m = importlib.util.module_from_spec(spec)
        sys.modules["zc_model"] = m; spec.loader.exec_module(m); _W["m"] = m
    return _W["m"]


def bench():
    if "B" not in _W:
        nc, nw = (int(x) for x in os.environ.get("ZC_BENCH", "110,360").split(","))
        M = model(); _W["B"] = M.K.bench(nc, nw)
    return _W["B"]


def kin_share(B, F, p):
    M = model(); ok = M.kin(F, M.snap(p)); ws = np.array([k == "ws" for k in B.kind])
    el = np.array([q["elev"] for q in B.poses])
    return round(float(ok[ws].mean()), 4), round(float(ok[ws & (el >= 140)].mean()), 4), round(float(ok[~ws].mean()), 4)


KEEP = ("gap", "near", "model_gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "hub_F",
        "min_metal_all_faces", "top_contact_poses", "top_contact_who", "inband_member", "overhead", "mode", "closure", "flips",
        "crown_contact_poses", "v_near1")


def eval_one(arg):
    tag, p = arg; t0 = time.time()
    try:
        M = model(); B = bench(); pf, r = M.evaluate(B, dict(p))
        row = dict(tag=tag, params={k: v for k, v in pf.items() if isinstance(v, (int, float, str, bool))},
                   **{k: r.get(k) for k in KEEP}, secs=round(time.time() - t0, 1))
        if r.get("honest") is not None and "verifier" not in r and r.get("gap", 0) >= 200: return row
        return row
    except Exception as e:                                                        # noqa: BLE001
        return dict(tag=tag, params=p, gap=400.0, error=repr(e), trace=traceback.format_exc()[-600:], secs=round(time.time() - t0, 1))


def area_uniform(u, lo, hi):
    """u in [0,1) -> elevation-like angle (deg) with sin uniform between sin(lo) and sin(hi)"""
    s0, s1 = math.sin(math.radians(lo)), math.sin(math.radians(hi)); return math.degrees(math.asin(s0 + u * (s1 - s0)))


def cmd_sobol(a):
    from scipy.stats import qmc
    M = model(); B = M.K.bench(110, 360); F = M.K.frames(B); B._kitF = F
    eng = qmc.Sobol(d=11, scramble=True, seed=a.seed); X = eng.random(a.n * 3); out = []
    for x in X:
        az = -110 + x[0] * 245; el = area_uniform(x[1], -20, 90)
        if not M.seat_ok(az, el): continue
        wd = math.degrees(math.acos(math.cos(math.radians(20)) + x[4] * (math.cos(math.radians(175)) - math.cos(math.radians(20)))))
        p = dict(az=round(az, 3), el=round(el, 3), a1=round(12 + x[2] * 156, 3), a2=round(12 + x[3] * 156, 3), wd=round(wd, 3),
                 wa=round(-180 + x[5] * 360, 3), sigma=1 if x[6] >= 0.5 else -1, inv2=int(x[7] >= 0.5), inv3=int(x[8] >= 0.5),
                 q=round(0.8 + 0.2 * x[9], 4), end_extra=round(8 * x[10] ** 2, 3))
        k = kin_share(B, F, p); out.append(dict(params=p, kin=k[0], kin_over=k[1], kin_clip=k[2]))
        if len(out) >= a.n: break
    json.dump(out, open(a.out, "w")); kk = np.array([o["kin"] for o in out])
    print(f"sobol {len(out)}: kin ws share p50 {np.median(kk):.3f} p90 {np.percentile(kk, 90):.3f} max {kk.max():.3f}; "
          f">= 0.7625: {(kk >= 0.7625).sum()}, >= 0.70: {(kk >= 0.70).sum()}")


def cmd_eval(a):
    cfgs = json.load(open(a.cfgs)); rows = []
    args = [(c.get("tag", f"c{i}"), c["params"] if "params" in c else c) for i, c in enumerate(cfgs)]
    with mp.Pool(a.procs) as pool:
        for r in pool.imap_unordered(eval_one, args):
            rows.append(r)
            if len(rows) % 4 == 0 or len(rows) == len(args):
                json.dump(rows, open(a.out + ".tmp", "w"), default=float); os.replace(a.out + ".tmp", a.out)
    json.dump(rows, open(a.out, "w"), default=float)
    g = sorted(r["gap"] for r in rows); print(f"eval {len(rows)}: best {g[:5]}")


def cmd_cma(a):
    x0 = json.loads(a.x0); fix = json.loads(a.fix); keys = [k for k in CONT if k not in fix]
    n = len(keys); lam = a.popsize; mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1.0 / (w ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3) ** 2 + mueff); cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs; chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
    rng = np.random.default_rng(a.seed); mean = np.zeros(n); sigma = a.sigma
    pc = np.zeros(n); ps = np.zeros(n); C = np.eye(n); Bm = np.eye(n); D = np.ones(n)
    s0 = np.array([SCALE[k] for k in keys]); c0 = np.array([float(x0[k]) for k in keys])
    base = dict(x0, **fix)
    to_p = lambda z: dict(base, **{k: float(round(v, 4)) for k, v in zip(keys, c0 + s0 * z)})
    rows = []; t0 = time.time(); best = (1e9, None)
    pool = mp.Pool(a.procs)
    res = pool.map(eval_one, [(f"{a.label}-g0", to_p(np.zeros(n)))])
    for r in res: r["gen"] = 0; rows.append(r)
    best = (res[0]["gap"], res[0]); gen = 0; gsec = 0.0; stall = 0
    json.dump(rows, open(a.out, "w"), default=float)
    while time.time() - t0 + gsec * 1.2 < a.budget_s:
        gen += 1; tg = time.time()
        Z = rng.standard_normal((lam, n)); Y = (Z * D) @ Bm.T; X = mean + sigma * Y
        res = pool.map(eval_one, [(f"{a.label}-g{gen}-{i}", to_p(X[i])) for i in range(lam)])
        f = np.array([r["gap"] for r in res])
        for r in res: r["gen"] = gen; r["sigma"] = round(sigma, 4); rows.append(r)
        json.dump(rows, open(a.out + ".tmp", "w"), default=float); os.replace(a.out + ".tmp", a.out)
        i0 = int(np.argmin(f))
        if f[i0] < best[0] - 0.05: best = (float(f[i0]), res[i0]); stall = 0
        else: stall += 1
        idx = np.argsort(f)[:mu]; old = mean.copy(); mean = (w[:, None] * X[idx]).sum(0)
        invsqrtC = Bm @ np.diag(1 / D) @ Bm.T
        ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * invsqrtC @ (mean - old) / sigma
        hsig = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * gen)) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hsig * math.sqrt(cc * (2 - cc) * mueff) * (mean - old) / sigma
        art = (X[idx] - old) / sigma
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hsig) * cc * (2 - cc) * C) + cmu * (art.T * w) @ art
        sigma *= math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        C = np.triu(C) + np.triu(C, 1).T; D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20))
        gsec = time.time() - tg
        print(f"[{a.label}] gen {gen} best-in-gen {f.min():.2f} best {best[0]:.2f} sigma {sigma:.3f} {gsec:.0f}s", flush=True)
        if sigma * D.max() < 0.02 or stall >= a.stall: print(f"[{a.label}] stop: sigma {sigma:.4f} stall {stall}", flush=True); break
    pool.close()
    print(json.dumps(dict(label=a.label, gens=gen, evals=len(rows), best_gap=best[0], best=best[1]["params"] if best[1] else None), default=float))


def cmd_frozen(a):
    M = model(); K = M.K; p0 = M.snap(json.loads(a.params)); res = dict(params=p0, t0=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    ex = os.environ.pop("CB_EXACT", None)
    try:
        fits = {"fit110": K.bench(110, 360), "fit60": K.bench(60, 160)}
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    wc, ww = (int(x) for x in os.environ.get("ZC_WEAR", "110,360").split(","))      # 110,1432: out of sample (all ws poses)
    Bb = K.bench(wc, ww); res["wear_mode"] = Bb.mode; res["wear_bench"] = [wc, ww]
    only = os.environ.get("ZC_FITS")                                                  # e.g. fit110: one protocol only
    for name, Bf in fits.items():
        if only and name not in only.split(","): continue
        t = time.time(); pf, rf = M.evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        res[name] = dict(fit_mode=Bf.mode, fit={k: rf.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "contact", "honest")})
        pb, rb = M.evaluate(Bb, dict(p0), fixed_prof=prof)
        res[name]["wear"] = {k: rb.get(k) for k in KEEP}; res[name]["secs"] = round(time.time() - t, 1)
        res[name]["attribution"] = M.attribute(Bb, pb, rb)
        json.dump(res, open(a.out, "w"), indent=1, default=float)
        print(name, Bf.mode, "->", Bb.mode, json.dumps({k: rb.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit")}, default=float), flush=True)


def cmd_levels(a):
    """hub F and 11-station strap levels (max across the strap width) for the motion preview"""
    M = model(); B = bench(); p, r = M.evaluate(B, json.loads(a.params)); L = B._kit_last; out = dict(params=p, gap=r.get("gap"))
    for m in L["chain"].members:
        pr = np.asarray(L["prof"][m.name])
        if m.kind == "flat": out[m.name] = round(float(pr[0]), 1); continue
        ns, nc = m.grid; st = pr.reshape(ns, nc).max(1); x = np.linspace(0, ns - 1, 11)
        out[m.name] = [round(float(np.interp(v, np.arange(ns), st)), 1) for v in x]
    print(json.dumps(out, default=float))


def cmd_attr(a):
    M = model(); B = bench(); p, r = M.evaluate(B, json.loads(a.params)); at = M.attribute(B, p, r)
    json.dump(dict(params=p, report={k: r.get(k) for k in KEEP}, attribution=at), open(a.out, "w"), indent=1, default=float)
    print(json.dumps({k: r.get(k) for k in ("gap", "near", "reach", "inband14", "contact")}), json.dumps(at, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("sobol"); s.add_argument("n", type=int); s.add_argument("out"); s.add_argument("--seed", type=int, default=0)
    s = sp.add_parser("eval"); s.add_argument("cfgs"); s.add_argument("out"); s.add_argument("--procs", type=int, default=2)
    s = sp.add_parser("cma"); s.add_argument("--x0", required=True); s.add_argument("--fix", default="{}"); s.add_argument("--out", required=True)
    s.add_argument("--sigma", type=float, default=0.5); s.add_argument("--popsize", type=int, default=8); s.add_argument("--procs", type=int, default=2)
    s.add_argument("--budget-s", type=float, default=1500); s.add_argument("--seed", type=int, default=1); s.add_argument("--label", default="cma")
    s.add_argument("--stall", type=int, default=12)
    s = sp.add_parser("frozen"); s.add_argument("params"); s.add_argument("out")
    s = sp.add_parser("attr"); s.add_argument("params"); s.add_argument("out")
    s = sp.add_parser("levels"); s.add_argument("params")
    a = ap.parse_args()
    {"sobol": cmd_sobol, "eval": cmd_eval, "cma": cmd_cma, "frozen": cmd_frozen, "attr": cmd_attr, "levels": cmd_levels}[a.cmd](a)

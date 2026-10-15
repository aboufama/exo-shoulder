#!/usr/bin/env python3
"""CMA-ES on a concept_kit model, every generation evaluated in parallel on this machine (meant to run as ONE farm job:
tools/cloud_run.py batch, 8 processes on an 8-vCPU worker, no per-generation round trip).

    python3 tools/concept_cma.py docs/concepts/models/<id>.py --x0 '{"az": .., ...}' --scales '{"az": 8, ...}'
            [--base '{fixed params}'] [--sigma 0.3] [--popsize 8] [--jobs 8] [--budget-s 840] [--max-gen 200]
            [--seed 1] [--rlay rail,stage2] --out results.json

Objective = the bench gap (lower is better) of the honest report; a dishonest report (audit problems, not march, no K2,
no K6) scores gap + 100 so the search never settles there; an error scores 400. Every evaluated configuration is written
incrementally to --out (gen, params incl. the model's design-step outputs, the bench metrics, honest, audit, per member).
--rlay M1,M2 (rail-elbow): the layout radius `r_lay` of the rail parts is set per configuration to the fitted radius
(min of the members' fitted levels, rounded: the conservative side - a larger r_lay than the real radius would shorten the
end stops and the fixing tab), a fix point with at most 2 re-runs, as the polish stage did by hand.
"""
import argparse, json, math, multiprocessing as mp, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
_W = {}


def _init(model_path):
    import importlib.util
    import concept_kit as K
    spec = importlib.util.spec_from_file_location("concept_model", model_path)
    m = importlib.util.module_from_spec(spec); sys.modules["concept_model"] = m; spec.loader.exec_module(m)
    _W.update(m=m, K=K, B=K.bench(60, 160))


def _one(p):
    m, B = _W["m"], _W["B"]; B.reset()
    if hasattr(m, "evaluate"):
        p, r = m.evaluate(B, p)
    else:
        p = dict(m.PARAMS, **p); r = _W["K"].evaluate(B, m.build, p)
    return p, r


def eval_cfg(arg):
    tag, p, rlay = arg; t0 = time.time(); it = []
    try:
        for k in range(3):
            pf, r = _one(p)
            if not rlay: break
            prof = _W["B"]._kit_last["prof"]
            fit = float(min(np.max(prof[n]) for n in rlay if n in prof)); it.append((p.get("r_lay"), round(fit, 1)))
            if abs(fit - p.get("r_lay", 70.0)) <= 1.0 or k == 2: break
            p = dict(p, r_lay=float(round(fit)))
        keep = ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide", "mass_g",
                "honest", "audit", "inband_member", "sample_mm", "residual_deg", "min_margin", "rail_span_deg")
        rep = {k: r.get(k) for k in keep}
        obj = r["gap"] + (0.0 if r.get("honest") else 100.0)
        if rlay and it and it[-1][0] is not None and it[-1][0] > it[-1][1] + 1.0: obj += 100.0   # optimistic layout
        return dict(tag=tag, params={k: v for k, v in pf.items() if isinstance(v, (int, float, str, bool)) or v is None},
                    report=rep, obj=obj, rlay_iter=it, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-800:], secs=round(time.time() - t0, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("--x0", required=True); ap.add_argument("--scales", required=True)
    ap.add_argument("--base", default="{}"); ap.add_argument("--sigma", type=float, default=0.3)
    ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--budget-s", type=float, default=840); ap.add_argument("--max-gen", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--rlay", default="")
    ap.add_argument("--out", required=True); ap.add_argument("--label", default="cma")
    a = ap.parse_args()
    x0 = json.loads(a.x0); sc = json.loads(a.scales); base = json.loads(a.base); keys = list(sc)
    rlay = [s for s in a.rlay.split(",") if s]
    n = len(keys); lam = a.popsize; mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1.0 / (w ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3) ** 2 + mueff); cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs; chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
    rng = np.random.default_rng(a.seed); mean = np.zeros(n); sigma = a.sigma
    pc = np.zeros(n); ps = np.zeros(n); C = np.eye(n); Bm = np.eye(n); D = np.ones(n); eigen_gen = 0
    s0 = np.array([sc[k] for k in keys]); c0 = np.array([float(x0[k]) for k in keys])
    to_p = lambda z: dict(base, **{k: float(round(v, 4)) for k, v in zip(keys, c0 + s0 * z)})
    rows = []; t_start = time.time(); best = (1e9, None)
    pool = mp.Pool(a.jobs, initializer=_init, initargs=(os.path.abspath(a.model),))
    r_lay0 = base.get("r_lay", x0.get("r_lay"))
    # generation 0 re-evaluates the start point (the reference for this run)
    res = pool.map(eval_cfg, [(f"{a.label}-g0-x0", dict(to_p(np.zeros(n)), **({"r_lay": r_lay0} if r_lay0 else {})), rlay)])
    for r in res: r["gen"] = 0; rows.append(r)
    best = (res[0]["obj"], res[0]); cur_rlay = res[0]["params"].get("r_lay", r_lay0)
    json.dump(rows, open(a.out, "w"), indent=1)
    gen = 0; gen_secs = 0.0
    while gen < a.max_gen and time.time() - t_start + gen_secs * 1.2 < a.budget_s:
        gen += 1; tg = time.time()
        Z = rng.standard_normal((lam, n)); Y = (Z * D) @ Bm.T; X = mean + sigma * Y
        args = [(f"{a.label}-g{gen}-{i}", dict(to_p(X[i]), **({"r_lay": cur_rlay} if cur_rlay else {})), rlay) for i in range(lam)]
        res = pool.map(eval_cfg, args)
        f = np.array([r["obj"] for r in res])
        for r in res: r["gen"] = gen; r["sigma"] = round(sigma, 4); rows.append(r)
        json.dump(rows, open(a.out + ".tmp", "w"), indent=1); os.replace(a.out + ".tmp", a.out)
        i0 = int(np.argmin(f))
        if f[i0] < best[0]: best = (float(f[i0]), res[i0]); cur_rlay = res[i0]["params"].get("r_lay", cur_rlay)
        idx = np.argsort(f)[:mu]; old = mean.copy(); mean = (w[:, None] * X[idx]).sum(0)
        invsqrtC = Bm @ np.diag(1 / D) @ Bm.T
        ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * invsqrtC @ (mean - old) / sigma
        hsig = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * gen)) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hsig * math.sqrt(cc * (2 - cc) * mueff) * (mean - old) / sigma
        art = (X[idx] - old) / sigma
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hsig) * cc * (2 - cc) * C) + cmu * (art.T * w) @ art
        sigma *= math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        C = np.triu(C) + np.triu(C, 1).T; D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20))
        gen_secs = time.time() - tg
        print(f"[{a.label}] gen {gen} best-in-gen {f.min():.2f} best {best[0]:.2f} sigma {sigma:.3f} {gen_secs:.0f}s "
              f"elapsed {time.time() - t_start:.0f}s", flush=True)
        if sigma * D.max() < 0.02: print("[cma] sigma collapsed: stop", flush=True); break
    pool.close()
    print(json.dumps(dict(label=a.label, gens=gen, evals=len(rows), best_obj=best[0], best=best[1]["params"] if best[1] else None)))


if __name__ == "__main__":
    main()

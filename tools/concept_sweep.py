#!/usr/bin/env python3
"""Run a list of configurations of one concept model on the common concept bench and write one bench report per
configuration - the same runner locally and on the CPU farm (tools/cloud_run.py sweep), so the numbers are comparable.

    python3 tools/concept_sweep.py docs/concepts/models/<id>.py --configs configs.json --out results.json
            [--jobs N] [--n-clip 60] [--n-ws 160] [--start K --count M]

configs.json: a JSON list of dicts, each a partial parameter set merged over the model's PARAMS ({} = the defaults).
results.json: [{"i": index in configs.json, "config": {...}, "report": B.report() (reach, follow, inband14, inband10,
contact, gap, poses, mode), "secs": s, "error": "..." on failure}, ...] in input order.

How a configuration is evaluated (first hook the model has):
  0. build(B, F, params) -> Chain    a tools/concept_kit.py model (docs/concepts/KIT.md): K.evaluate(B, build, params);
                                     the report keeps the bench metrics + the kit's JSON-able extras (closure, mass_g, ...)
  1. bench_eval(B, params) -> dict   the model's own evaluation on the Bench B (it must leave its result in B, i.e. end
                                     with B.record for every pose, or return a dict with the bench metrics itself);
                                     params = dict(PARAMS, **config). Recommended for new models (fast, vectorised).
  2. metal(pose, frames, params)     the concept_bench contract: per pose the metal sample points or None. params gets
                                     "_bench": B when the model's metal() reads params["_bench"]; B= and i= are passed
                                     when metal() takes them.
Jobs: --jobs N processes (default: FARM_VCPUS/4 on the farm - 4 jobs share an 8-vCPU worker -, else 1); each process
builds its own Bench (the grid cache .cache/concept_bench is memory-mapped, so N processes share it).
"""
import argparse, importlib.util, inspect, json, os, sys, time, traceback

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
_W = {}


def load_model(path):
    path = os.path.abspath(path)
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("concept_model", path)
    m = importlib.util.module_from_spec(spec); sys.modules["concept_model"] = m; spec.loader.exec_module(m)
    return m


def _init(model_path, n_clip, n_ws):
    import concept_bench as CB
    _W["m"] = load_model(model_path); _W["B"] = CB.Bench(n_clip=n_clip, n_ws=n_ws)


def _jsonable(v):
    try:
        json.dumps(v); return True
    except (TypeError, ValueError):
        return False


def _metric_keys():
    return ("reach", "follow", "inband14", "inband10", "contact", "gap")


def eval_one(arg):
    i, cfg = arg; m, B = _W["m"], _W["B"]; t0 = time.time()
    try:
        base = dict(getattr(m, "PARAMS", {}))
        prm = dict(base, **cfg)
        B.reset()
        if not hasattr(m, "bench_eval") and callable(getattr(m, "build", None)) and "concept_kit" in sys.modules:
            import concept_kit as K
            r = K.evaluate(B, m.build, prm)
            rep = {k: v for k, v in r.items() if _jsonable(v)}
        elif hasattr(m, "bench_eval"):
            r = m.bench_eval(B, prm)
            rep = B.report() if not (isinstance(r, dict) and all(k in r for k in _metric_keys())) else r
        elif hasattr(m, "metal"):
            sig = inspect.signature(m.metal).parameters; src = inspect.getsource(m.metal)
            p = dict(prm, _bench=B) if "_bench" in src else prm
            for j, pose in enumerate(B.poses):
                kw = {}
                if "B" in sig: kw["B"] = B
                if "i" in sig: kw["i"] = j
                if "bench" in sig: kw["bench"] = B
                B.record(j, m.metal(pose, B.frames(j), p, **kw))
            rep = B.report()
        else:
            raise RuntimeError("model has neither bench_eval(B, params) nor metal(pose, frames, params)")
        return dict(i=i, config=cfg, report=rep, secs=round(time.time() - t0, 2))
    except Exception as e:                                     # noqa: BLE001 - one bad config must not kill the chunk
        return dict(i=i, config=cfg, report=None, secs=round(time.time() - t0, 2),
                    error=f"{type(e).__name__}: {e}", trace=traceback.format_exc()[-1500:])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model"); ap.add_argument("--configs", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=0); ap.add_argument("--n-clip", type=int, default=60); ap.add_argument("--n-ws", type=int, default=160)
    ap.add_argument("--start", type=int, default=0); ap.add_argument("--count", type=int, default=0)
    a = ap.parse_args()
    cfgs = json.load(open(a.configs))
    if not isinstance(cfgs, list) or not all(isinstance(c, dict) for c in cfgs):
        sys.exit("--configs must be a JSON list of dicts")
    idx = list(range(len(cfgs)))[a.start:(a.start + a.count) if a.count else None]
    jobs = a.jobs or (max(1, int(float(os.environ["FARM_VCPUS"])) // 4) if os.environ.get("FARM_VCPUS") else 1)
    jobs = max(1, min(jobs, len(idx)))
    t0 = time.time(); work = [(i, cfgs[i]) for i in idx]
    if jobs == 1:
        _init(a.model, a.n_clip, a.n_ws); res = [eval_one(w) for w in work]
    else:
        from multiprocessing import get_context
        with get_context("fork").Pool(jobs, initializer=_init, initargs=(a.model, a.n_clip, a.n_ws)) as pool:
            res = pool.map(eval_one, work, chunksize=1)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    tmp = a.out + ".tmp"; json.dump(res, open(tmp, "w"), indent=1); os.replace(tmp, a.out)
    bad = sum(r.get("error") is not None for r in res)
    print(f"concept_sweep: {len(res)} configs ({bad} failed) in {time.time() - t0:.1f}s with {jobs} process(es) -> {a.out}")


if __name__ == "__main__":
    main()

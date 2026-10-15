#!/usr/bin/env python3
"""Re-measure one concept_kit configuration on the large bench (the verifier's protocol): Bench(110, 360), exact path
(set CB_EXACT=1 in the environment), part-part clearance 1 mm radial (K6 overlap 1 mm - 1e-4 instead of 0.5), two ways:

  refit   the model's own procedure on the large bench (design step + underside fit on its 470 poses, as the
          seed-offset-3r-slides verifier did);
  frozen  the geometry (design-step outputs + every member's fitted underside) fitted on the FIT bench (default
          Bench(60, 160)) and frozen, then scored on the large bench: a rigid part does not refit to poses it never saw
          (the annular-ring-3r verifier's protocol).

    CB_EXACT=1 python3 tools/concept_bigbench.py docs/concepts/models/<id>.py --params '{...}' [--mode refit,frozen]
            [--overlap 1.0] [--fit 60,160] [--big 110,360] --out result.json
"""
import argparse, functools, importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                                       # noqa: E402

KEEP = ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide", "mass_g", "honest",
        "audit", "inband_member", "sample_mm", "residual_deg", "min_margin", "poses", "mode")


def load(path):
    spec = importlib.util.spec_from_file_location("concept_model", path)
    m = importlib.util.module_from_spec(spec); sys.modules["concept_model"] = m; spec.loader.exec_module(m); return m


def run(m, B, p):
    if hasattr(m, "evaluate"): return m.evaluate(B, p)
    p = dict(m.PARAMS, **p); return p, K.evaluate(B, m.build, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model"); ap.add_argument("--params", required=True); ap.add_argument("--mode", default="refit,frozen")
    ap.add_argument("--overlap", type=float, default=1.0); ap.add_argument("--fit", default="60,160")
    ap.add_argument("--big", default="110,360"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = load(os.path.abspath(a.model)); p0 = json.loads(a.params)
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=a.overlap - 1e-4)       # 1 mm radial (K6 is 0.5)
    out = dict(model=a.model, params=p0, overlap=a.overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    nb = tuple(int(x) for x in a.big.split(",")); nf = tuple(int(x) for x in a.fit.split(","))
    Bb = K.bench(*nb)
    for mode in a.mode.split(","):
        t0 = time.time()
        if mode == "refit":
            p, r = run(m, Bb, dict(p0))
        elif mode == "frozen":
            Bf = K.bench(*nf); pf, rf = run(m, Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
            out["runs"]["fit"] = dict({k: rf.get(k) for k in KEEP}, bench=list(nf), params={k: v for k, v in pf.items() if not isinstance(v, (dict, list))})
            fp = K.fit_profiles
            K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
            try:
                r = K.evaluate(Bb, m.build, pf); p = pf                                         # design-step outputs frozen too
            finally:
                K.fit_profiles = fp
        else:
            raise ValueError(mode)
        out["runs"][mode] = dict({k: r.get(k) for k in KEEP}, bench=list(nb), secs=round(time.time() - t0, 1),
                                 params={k: v for k, v in p.items() if not isinstance(v, (dict, list))})
        print(mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest")}, flush=True)
        json.dump(out, open(a.out, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()

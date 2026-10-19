"""Death audit #2 (2026-10-18) probe: the catalogue spec's untested item "the neck over hub 2's crown".

The spec (catalogue model_spec) asked for the K7 neck to ride over hub 2's crown, because hub2-neck is the largest
part-part pair (10 of 18 part-part poses of the s12 config on Bench(60,160), elevation 90-150; audit #1). The screen's
build (zc-frontier-3r, inv3 1) only lifts the neck over link 2. This probe changes ONE thing: the neck's K6-by-construction
`over` list also carries hub 2 (and, variant b, hub 1), same 1 mm gap as every other `over` pair. Every check, rule and
bench is unchanged (ZC.evaluate -> run -> K.evaluate + the verifier's top_check).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/deltoid-crest-j3-3r_audit2_neckover.py fast OUT.json
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/deltoid-crest-j3-3r_audit2_neckover.py frozen OUT.json VARIANT
"""
import importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


DC = _load("dc_model", os.path.join(REPO, "docs", "concepts", "models", "deltoid-crest-j3-3r.py"))
ZC = DC.ZC; K = DC.K
BEST = {"az": 97.467, "el": 62.7844, "a1": 40.6347, "a2": 47.4415, "wd": 109.3974, "wa": -1.1276, "q": 0.9581,
        "end_extra": 8.0, "sigma": -1, "inv2": 0, "inv3": 1}           # audit #1 best frozen exact (34.98)
CLAIM = {"az": 108.5603, "el": 64.4969, "a1": 40.4557, "a2": 45.9232, "wd": 104.4082, "wa": -0.3864, "q": 0.9572,
         "end_extra": 2.9522, "sigma": -1, "inv2": 0, "inv3": 1}       # the row's fast claim (26.78 fast, 40.17 frozen)
ORIG = ZC.build
VARIANTS = {"base": [], "neck_over_hub2": [("hub2", 1.0)], "neck_over_hub2_hub1": [("hub2", 1.0), ("hub1", 1.0)]}


def make_build(extra):
    def build(B, F, p):
        ch = ORIG(B, F, p)
        if extra:
            for m in ch.members:
                if m.name == "neck": m.over = list(m.over) + list(extra)
        return ch
    return build


KEYS = ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest", "hub_F", "inband_member",
        "overhead", "min_metal_all_faces")


def run_one(B, p, var, fixed_prof=None):
    ZC.build = make_build(VARIANTS[var])
    try:
        t = time.time(); pf, r = ZC.evaluate(B, dict(p), fixed_prof)
        att = ZC.attribute(B, pf, r)
    finally:
        ZC.build = ORIG
    out = {k: r.get(k) for k in KEYS}; out["secs"] = round(time.time() - t, 1); out["attribution"] = att
    return pf, out


def main():
    task, path = sys.argv[1], sys.argv[2]; res = dict(task=task, t0=K.now() if hasattr(K, "now") else None)
    if task == "fast":
        B = K.bench(60, 160)
        for cname, c in (("best_s12_ee8", BEST), ("claim_s10", CLAIM)):
            for var in VARIANTS:
                _, o = run_one(B, c, var); res[f"{cname}/{var}"] = o
                print(cname, var, json.dumps({k: o[k] for k in KEYS}, default=float), o["secs"], flush=True)
                json.dump(res, open(path, "w"), indent=1, default=float)
    else:   # frozen: fit Bench(60,160) fast with the variant, freeze every level, wear Bench(110,360) exact
        var = sys.argv[3]; c = dict(BEST, **(json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}))
        ex = os.environ.pop("CB_EXACT", None)
        try: Bf = K.bench(60, 160)
        finally:
            if ex is not None: os.environ["CB_EXACT"] = ex
        pf, of = run_one(Bf, c, var); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        res.update(variant=var, params=c, fit={k: of[k] for k in KEYS}); print("fit", json.dumps(res["fit"], default=float), flush=True)
        Bb = K.bench(110, 360); _, ow = run_one(Bb, pf, var, fixed_prof=prof)
        res["wear_mode"] = Bb.mode; res["wear"] = ow; res["score"] = round(100 * (1 - float(ow["gap"]) / 275), 2)
        print("wear", Bb.mode, json.dumps({k: ow[k] for k in KEYS}, default=float), flush=True)
        json.dump(res, open(path, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()

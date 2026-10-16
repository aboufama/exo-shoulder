"""Claim harness for twist-long-a2-knuckle-3r: the designer's variables are mapped to seat parameters by the model's own
prep() (docs/concepts/models/twist-long-a2-knuckle-3r.py), then worn FROZEN through the lead's INDEPENDENT verifier
(docs/concepts/verify/frontload-lobe-stopb-knuckle-3r.py, CorrModel: horn plate on K's cap top, rod clear of the cap,
ROD-hubK per pose; flood fill optional). Fit on Bench(60,160) fast, wear on Bench(110,360) exact or the held-out set.

    CB_EXACT=1 python3 docs/concepts/models/twist-long-a2-knuckle-3r_claim.py '<json>' <bench|held> <out.json> [--flood] [--claim]
"""
import importlib.util, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


T = _load("twist_claim_model", os.path.join(HERE, "twist-long-a2-knuckle-3r.py"))
V = _load("frontload_verifier_for_twist", os.path.join(REPO, "docs", "concepts", "verify", "frontload-lobe-stopb-knuckle-3r.py"))

if __name__ == "__main__":
    par = json.loads(sys.argv[1]); wear = sys.argv[2]; path = sys.argv[3]
    p, info = T.prep(par)
    keep = {k: v for k, v in p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    Model = V.F.FLModel if "--claim" in sys.argv else V.CorrModel
    t = time.time(); out = V.frozen_wear(Model, keep, wear, "--flood" in sys.argv)
    out.update(params=par, seat=info, wear=wear, model="claim" if "--claim" in sys.argv else "corr", secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(wear=wear, fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"), minmetal=out["audit"].get("near_touch_min_mm"),
                          ovh=out["audit"].get("overhead140"), why=out["why"], parts=out.get("parts_ib14"), conn=out.get("connected"), secs=out["secs"]), default=float))

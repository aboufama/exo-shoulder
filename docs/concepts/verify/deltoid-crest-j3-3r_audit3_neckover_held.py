"""Death re-audit (round 14, 2026-10-18): the neck-over-hub-2 variant (deltoid-crest-j3-3r_audit2_neckover.py) at the
v_gap config, fit Bench(60,160) fast, every level frozen, worn on the HELD-OUT poses (the skeptic harness's held_bench,
exact path). Read only for the claim; never used in search or selection.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/deltoid-crest-j3-3r_audit3_neckover_held.py OUT.json
"""
import importlib.util, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


A2 = _load("dc_a2", os.path.join(HERE, "deltoid-crest-j3-3r_audit2_neckover.py"))
SK = _load("dc_sk", os.path.join(HERE, "deltoid-crest-j3-3r-skeptic.py"))
K = A2.K; VAR = "neck_over_hub2"
out = sys.argv[1]; res = dict(variant=VAR, params=A2.BEST, bench="held out (skeptic held_bench, exact)")
ex = os.environ.pop("CB_EXACT", None)
try: Bf = K.bench(60, 160)
finally:
    if ex is not None: os.environ["CB_EXACT"] = ex
pf, of = A2.run_one(Bf, A2.BEST, VAR); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
res["fit"] = {k: of[k] for k in A2.KEYS}; print("fit", json.dumps(res["fit"], default=float), flush=True)
Bh = SK.held_bench(110, 360); _, ow = A2.run_one(Bh, pf, VAR, fixed_prof=prof)
res["wear"] = ow; res["score"] = round(100 * (1 - float(ow["gap"]) / 275), 2)
print("wear held", json.dumps({k: ow[k] for k in A2.KEYS}, default=float), flush=True)
json.dump(res, open(out, "w"), indent=1, default=float)

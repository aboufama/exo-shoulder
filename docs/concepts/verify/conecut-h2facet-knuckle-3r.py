"""Independent verifier of conecut-h2facet-knuckle-3r: the lead conecut-knee-knuckle-3r verifier harness (docs/concepts/verify/conecut-knee-knuckle-3r.py: cam closure, PA with friction, K sense, own-state th margin, C1 own-angle J3 stop, C2 stop web, C4 equal-strap in-band, per-pose dump) worn UNCHANGED on the claim model (its CC module, CCModel = FTModel with the hub-2 facet).
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/conecut-h2facet-knuckle-3r.py <bench|held> out.json [--dump perpose.json] [--set fd=0]"""
import importlib.util, json, os, sys, time
REPO = "/home/user/exo-shoulder"
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
V = _load("v_conecut_for_h2f", os.path.join(REPO, "docs/concepts/verify/conecut-knee-knuckle-3r.py"))
H2 = _load("h2f_claim", os.path.join(REPO, "docs/concepts/models/conecut-h2facet-knuckle-3r.py"))
V.CC = H2.CC     # its CCModel is FTModel (the facet)
row = json.load(open(os.path.join(REPO, "docs/concepts/rows/conecut-h2facet-knuckle-3r.json")))
P = dict(row["best_params"])
for i_, a_ in enumerate(sys.argv):
    if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_)
P = H2._clamp(dict(H2.PARAMS, **P))
P = {k: v for k, v in P.items() if isinstance(v, (int, float, str, bool)) or v is None}
V.retarget(P)
which, path = sys.argv[1], sys.argv[2]
dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
t = time.time(); out = V.wear(P, which, "--flood" in sys.argv, dump)
out.update(wear=which, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=P)
json.dump(out, open(path, "w"), indent=1, default=float)
e = out["extra"]
print(json.dumps(dict(wear=which, fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=out["audit"].get("gap_near1"),
                      minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["overhead"], contacts=out["contacts"],
                      extra={k: e.get(k) for k in ("n_taken", "closure_max_mm", "poses_failing", "why_failing", "th_margin", "wrong_sense")},
                      c4=out.get("c4_inband"), dump=out.get("dump"), secs=out["secs"]), default=float))

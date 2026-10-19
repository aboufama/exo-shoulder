"""Alignment-auditor adapter (new file; nothing it loads is edited): wear conecut-l2jog-knuckle-3r's verified claim
through the LEAD's independent verifier harness (docs/concepts/verify/conecut-knee-knuckle-3r.py: own-state th fold
margin, C1 own-angle J3 stop, C2 stop web, C4 per-part in-band, K sense, per-pose dump, and with --flood the continuity
flood of docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py), the same way
docs/concepts/verify/conecut-h2facet-knuckle-3r.py wears the h2facet claim: the claim model's CC module (whose CCModel is
JogModel, the link-2 waist applied right after the fit) is handed to the harness. Optional --truecut wears the verifier's
true-cut reading (docs/concepts/verify/conecut-l2jog-knuckle-3r.py true_disp: each moved sample on the original section).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_l2jog_verifier_adapter.py <bench|held> out.json [--flood] [--truecut]
"""
import importlib.util, json, os, sys, time
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("v_conecut_for_l2jog_audit", os.path.join(REPO, "docs/concepts/verify/conecut-knee-knuckle-3r.py"))
L2 = _load("l2jog_claim_audit", os.path.join(REPO, "docs/concepts/models/conecut-l2jog-knuckle-3r.py"))
if "--truecut" in sys.argv:
    TV = _load("l2jog_truecut_audit", os.path.join(REPO, "docs/concepts/verify/conecut-l2jog-knuckle-3r.py"))
    TV.L = L2; TV.orig = L2.jog_disp
    L2.jog_disp = lambda X, rows, P, fr=None: TV.true_disp(X, rows, dict(P, truecut=1), fr)
V.CC = L2.CC                                                   # its CCModel is JogModel
row = json.load(open(os.path.join(REPO, "docs/concepts/rows/conecut-l2jog-knuckle-3r.json")))
P = L2._clamp(dict(L2.PARAMS, **row["best_params"]))
P = {k: v for k, v in P.items() if isinstance(v, (int, float, str, bool)) or v is None}
V.retarget(P)
which, path = sys.argv[1], sys.argv[2]
t = time.time(); out = V.wear(P, which, "--flood" in sys.argv, None)
out.update(id="conecut-l2jog-knuckle-3r" + ("+truecut" if "--truecut" in sys.argv else ""), wear=which, secs=round(time.time() - t, 1),
           exact=os.environ.get("CB_EXACT") == "1", params=P,
           note="alignment auditor 2026-10-18: the lead verifier harness worn unchanged on the claim model (tools/alignment_l2jog_verifier_adapter.py)")
json.dump(out, open(path, "w"), indent=1, default=float)
e = out.get("extra") or {}
print(json.dumps(dict(wear=which, frozen=out["frozen"], why=out["why"], near1=(out.get("audit") or {}).get("gap_near1"),
                      ovh=out["overhead"], th=e.get("th_margin"), c4=out.get("c4_inband"),
                      conn={k: (v.get("gap") if isinstance(v, dict) else v) for k, v in (out.get("connected") or {}).items()}, secs=out["secs"]), default=float))

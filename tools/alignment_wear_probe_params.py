"""Adapter: tools/alignment_wear_probe_model.py with a params override, for a verified config that differs from the row's
best_params (e.g. a verifier's re-placed config, rows/<id>.json verification.verified_config). The model runs UNCHANGED:
only PK.audit is wrapped to capture the worn (M, B); the override JSON is merged over the row's best_params.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_wear_probe_params.py <id> <bench|held> <params.json> <out.json>
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_wear_probe_model as WM                       # noqa: E402
W = WM.W


def run(rid, wear, params):
    row = json.load(open(os.path.join(W.REPO, "docs", "concepts", "rows", rid + ".json")))
    P = dict(row.get("best_params") or {}); over = json.load(open(params)); P.update(over)
    mod = W._load("awpp_" + rid.replace("-", "_"), os.path.join(W.REPO, "docs", "concepts", "models", rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(rid + ": no pin-knee-style audit to capture")
    cap = W._capture(pk)
    out = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    M, B = cap[-1]
    a = out.get("audit") or {}
    return dict(design=rid, wear=wear, params_override=over, model_frozen=out.get("frozen"), fit_fast=out.get("fit_fast"),
                model_audit_near=dict(near1=a.get("gap_near1"), near2=a.get("gap_near2"), near2_poses=a.get("near2_poses"), min_mm=a.get("near_touch_min_mm")),
                probe=W.analyse(M, B), extras=WM.extras(M, B))


if __name__ == "__main__":
    t = time.time(); r = run(sys.argv[1], sys.argv[2], sys.argv[3]); r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
    json.dump(r, open(sys.argv[4], "w"), indent=1, default=float); print(json.dumps({k: v for k, v in r.items() if k != "probe"}, default=float))

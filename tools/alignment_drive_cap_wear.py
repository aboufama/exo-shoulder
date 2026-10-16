"""Alignment adapter (read-only on every claim): wear a sidecar-family claim with its drive range CAPPED at a buildable
stop B, through the model's own frozen() / frozen_held() (unchanged), and record the same deep audit as
tools/alignment_audit.py remeasure (near-touch 1 / 2 / 3 mm, metal histogram, band read 3-14 mm, coordinate spans).

Why: a verified number must describe a drive that can be built. The sidecar models end the usable range at dK_lim
(the first |dK| where the modelled rod / crank comes < 1 mm to hub 2 or the transmission drops), with the modelled
O7 ball-link socket. The gen-6 drive red team (docs/research/sidecar_mechanism_redteam.md, finding 2) found the real
catalogue ball link (igus KBRM-02, head O9 x 4) pinches hub 2 past dK ~35.4, so the buildable stop B sits there unless
a custom O7 eye is made. This adapter measures that reading: the model's SCModel._truncate is wrapped so that
dK_lim = min(model dK_lim, cap) on every bench (fit and wear), exactly where the model itself puts stop B. Nothing
else changes; no score, row, judge or model file is written.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_drive_cap_wear.py <id> bench|held <cap_deg> '<params json>' <tag>
        -> docs/alignment/remeasure/<id>_<tag>_<wear>.json
"""
import json, math, os, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                  # noqa: E402


def main(rid, wear, cap_deg, params_json, tag):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json")))
    P = dict(row.get("best_params") or {}); P.update(json.loads(params_json or "{}"))
    mod = AA._load("dcw_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    SC = getattr(mod, "SCModel", None)
    if SC is None or not hasattr(SC, "_truncate"): raise SystemExit(f"{rid}: no sidecar SCModel._truncate to cap")
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    capr = math.radians(float(cap_deg)); seen = {}
    orig_tr = SC._truncate

    def capped(self):
        g = getattr(self, "_scg", None)
        if g is not None and "dK_lim" in g:
            seen.setdefault("dK_lim_model_deg", round(math.degrees(float(g["dK_lim"])), 2))
            g["dK_lim"] = min(float(g["dK_lim"]), capr)
        r = orig_tr(self); seen["n_trunc_last"] = int(getattr(self, "_n_trunc", 0)); return r
    SC._truncate = capped
    box = {}; orig_a = pk.audit

    def wrapped(M, B):
        a = orig_a(M, B); box["deep"] = AA.deep_audit(M, B); box["mode"] = B.mode; return a
    pk.audit = wrapped
    t = time.time()
    try:
        r = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    finally:
        pk.audit = orig_a; SC._truncate = orig_tr
    out = dict(id=rid, wear=wear, tag=tag, cap_deg=float(cap_deg), params=P, cap=seen, frozen=r.get("frozen"), fit_fast=r.get("fit_fast"),
               why=r.get("why"), audit=r.get("audit"), sidecar=r.get("sidecar"), deep=box.get("deep"), mode=box.get("mode"),
               secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
    os.makedirs(AA.REM, exist_ok=True)
    path = os.path.join(AA.REM, f"{rid}_{tag}_{wear}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(id=rid, wear=wear, tag=tag, cap=seen, frozen=out["frozen"],
                          deep={k: v for k, v in (out["deep"] or {}).items() if k not in ("coord_spans", "hist")}, secs=out["secs"]), default=float))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "{}", sys.argv[5] if len(sys.argv) > 5 else "cap")

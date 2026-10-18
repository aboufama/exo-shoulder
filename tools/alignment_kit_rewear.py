"""Alignment re-wear for kit-built models (zc-frontier family) that tools/alignment_audit.py remeasure cannot wrap (no
pin-knee-style audit(M, B)). Read-only on every claim: the model file runs UNCHANGED (its own snap() / evaluate()), the
fit is Bench(60,160) fast with every level frozen (the model's frozen() protocol), the wear is Bench(110,360) (exact with
CB_EXACT=1) or the held-out bench of the design's own verifier (held_bench(): poses disjoint from Bench(110,360)). After
the model's evaluate() the worn bench is read by the audit's own instruments: alignment_audit.deep_audit (near-touch at
1 / 2 / 3 mm, clip metal histogram, band read 3-14 mm) and alignment_wear_probe.analyse (unscored workspace in-band,
overhead in-band, clearance floors, reach by elevation, contact depths). The kit model carries no extra walls (M.cmin
empty); its top-face reading stays in the model's own report (near, min_metal_all_faces), copied alongside.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_kit_rewear.py <id> bench|held [--verifier <path>]
        -> docs/alignment/remeasure/<id>_<wear>.json (remeasure format: frozen, audit, deep, probe)
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402
import alignment_wear_probe as WP                                # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


class _M:            # deep_audit / analyse read M.cmin (no extra walls in the kit build) and M.why (absent)
    cmin = {}


def run(rid, wear, verifier=None):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row["best_params"])
    mod = _load("akr_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    K = mod.K; t0 = time.time()
    p0 = mod.snap(dict(mod.PARAMS, **P)); p0.pop("in_box", None)
    ex = os.environ.pop("CB_EXACT", None)
    try: Bf = K.bench(60, 160)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    pf, rf = mod.evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    fit = {k: rf.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest")}
    print("fit", json.dumps(fit, default=float), flush=True)
    if wear == "bench":
        B = K.bench(110, 360)
    else:
        vpath = verifier or os.path.join(AA.VERIFY, rid + "-skeptic.py")
        V = _load("akr_v_" + rid.replace("-", "_"), vpath); B = V.held_bench(110, 360)
    pb, rb = mod.evaluate(B, dict(p0), fixed_prof=prof)
    rep = {k: rb.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest", "hub_F",
                                  "min_metal_all_faces", "top_contact_poses", "inband_member", "overhead")}
    print("wear", B.mode, json.dumps(rep, default=float), flush=True)
    deep = AA.deep_audit(_M, B)
    kind = np.array(B.kind); el = np.array([p["elev"] for p in B.poses])
    WP.kind, WP.el = kind, el                                     # analyse() reads these module names
    try:
        probe = WP.analyse(_M, B)
    except NameError:
        probe = None
    out = dict(id=rid, wear=wear, params=p0, fit_fast=fit, frozen=rep, parts_ib14=rb.get("inband_member"),
               audit=dict(gap_near1=(rb.get("v_near1") or {}).get("gap", rb.get("near")), near_touch_min_mm=rb.get("min_metal_all_faces"),
                          note="the model's own near-touch (all faces incl. top faces); deep.gap_near* read the bench metal only"),
               deep=deep, probe=probe, mode=B.mode, secs=round(time.time() - t0, 1), exact=os.environ.get("CB_EXACT") == "1",
               git=AA._git("rev-parse", "--short", "HEAD"),
               source=f"tools/alignment_kit_rewear.py: model {rid}.py unchanged (snap + evaluate), fit Bench(60,160) fast frozen, "
                      f"worn {'Bench(110,360)' if wear == 'bench' else 'held_bench(110,360) of the verifier'}")
    path = os.path.join(AA.REM, f"{rid}_{wear}.json"); os.makedirs(AA.REM, exist_ok=True)
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(frozen=rep, deep={k: v for k, v in deep.items() if k != "coord_spans"}, secs=out["secs"], out=path), default=float))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    vp = a[a.index("--verifier") + 1] if "--verifier" in a else None
    run(a[0], a[1], vp)

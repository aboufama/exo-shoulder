"""FINAL POLISH objective for spine-parked-j2-3r (CLAUDE.md "Every generation ends in a full CAD + render": a wide
multi-start optimisation of every free parameter directly on the verification bench). One evaluation = the verifier's
`frozen` task (docs/concepts/verify/spine-parked-j2-3r.py), with the big bench on the fast grid cache:

  1. snap to the real parts (rad1 / rad2 / rad3 in the declared hub set O20 / O17 / O15, sigma +-1, q 0.8-1.0,
     end_extra 0-8: the model's own clamps, plus rad1 - the J1 hub may be slim too, same MR117-2RS pair);
  2. fit on Bench(60,160) FAST (the model's evaluate, 1 mm radial K6 as the verifier sets it), freeze every level;
  3. wear the frozen shape on Bench(110,360) (fast cache in the search; CB_EXACT=1 for the claim) with the verifier's
     checks: kit K1-K7 + dense K2, declared slim-hub audit, hub crown / wall check, 1 mm radial K6, top faces of every
     member, near-touch over every face, hub-axis accessibility (hub F <= 140 mm).

Objective (`gap`, lower is better) = the NEAR-TOUCH gap of the verifier (v_near1: a taken pose whose metal, any face,
comes within 1 mm of the skin counts as contact) - the buildable gap. The plain verifier gap (v) is reported beside it
(`v_gap`). A dishonest report or a hub axis that is not accessible scores +100 (`honest` False).

SPM_BIG=110,1432 (with CB_EXACT=1 SPM_ALLOW_EXACT=1) wears the frozen shape on another bench instead: the out-of-sample
check after a polish that was fitted ON Bench(110,360) (all 1432 workspace-envelope poses, 1072 of them never seen).

Hook for tools/concept_cma.py: evaluate(B, params) -> (params, report) (the B it passes is ignored); REPORT_KEYS lists
the extra keys concept_cma keeps.
    python3 tools/concept_cma.py docs/concepts/verify/spine-parked-j2-3r-polish.py --x0 '{..}' --scales '{..}' ...
    python3 docs/concepts/verify/spine-parked-j2-3r-polish.py '<json params>'     # one evaluation, prints the report
"""
import functools, importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("spm_verify", os.path.join(HERE, "spine-parked-j2-3r.py"))
V = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V)
M, K = V.M, V.K
if not getattr(K.collisions, "_spm_1mm", False):                       # 1 mm radial K6, as the verifier's main() sets it
    K.collisions = functools.partial(K.collisions, overlap=1.0 - 1e-4); K.collisions._spm_1mm = True
HUBS = sorted(M.SLIM)                                                  # 7.5 (O15), 8.5 (O17), 10.0 (O20)
REPORT_KEYS = ("v_gap", "v_near_gap", "v", "v_near1", "min_metal_all_faces", "min_metal_skin", "top_contact_poses",
               "crown_contact_poses", "hub_F", "hub_F_ok", "big_mode", "fit_gap", "overhead", "declared_hubs", "near_low")
_B = {}


def snap(p):
    p = V.snap(dict(M.PARAMS, **p)); p["rad1"] = min(HUBS, key=lambda x: abs(x - float(p["rad1"])))
    for k in ("margin", "width", "t_link", "vm", "near"): p[k] = M.PARAMS[k]          # never loosened (fixed by the rules)
    return p


def benches():
    if not _B:
        ex = os.environ.pop("CB_EXACT", None)
        try:
            _B["fit"] = K.bench(60, 160)                                   # the frozen protocol always fits on the FAST grid
        finally:
            if ex is not None: os.environ["CB_EXACT"] = ex
        nc, nw = (int(x) for x in os.environ.get("SPM_BIG", "110,360").split(","))   # an out-of-sample wear bench, e.g. 110,1432
        _B["big"] = K.bench(nc, nw)
        if _B["big"].mode != "fast" and os.environ.get("SPM_ALLOW_EXACT") != "1" and os.environ.get("CB_EXACT") != "1":
            raise RuntimeError("Bench(110,360) has no fast cache here (tools/bench_cache_farm.py use 110 360)")
    return _B["fit"], _B["big"]


def evaluate(B_unused, params):
    Bf, Bb = benches(); p = snap(params); Bf.reset(); Bb.reset()
    pf, rf = M.evaluate(Bf, dict(p)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    r = V.run(Bb, pf, prof); v = r["verifier"]
    honest = bool(r.get("honest")) and bool(rf.get("honest")) and v["hub_F_ok"]
    out = dict(r)
    out.update(v_gap=v["v"]["gap"], v_near_gap=v["v_near1"]["gap"], v=v["v"], v_near1=v["v_near1"],
               min_metal_all_faces=v["min_metal_all_faces"], top_contact_poses=v["top_contact_poses"], hub_F=v["hub_F"],
               hub_F_ok=v["hub_F_ok"], big_mode=Bb.mode, fit_gap=rf["gap"], honest=honest,
               audit=list(r.get("audit") or []) + ([] if v["hub_F_ok"] else ["hub axis not accessible (F > 140 mm)"]))
    for k in ("reach", "follow", "inband14", "inband10", "contact"): out[k] = v["v_near1"][k]   # the objective's own metrics
    out["gap"] = v["v_near1"]["gap"]
    return pf, out


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if M._jsonable(v)}


if __name__ == "__main__":
    # '<json dict>' or '<json list of dicts | {"label": dict}>' [--out R.json]: one evaluation each, printed (+ written)
    arg = json.loads(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1][:1] in "{[" else (json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {})
    items = list(arg.items()) if isinstance(arg, dict) and all(isinstance(v, dict) for v in arg.values()) and arg else \
        [(str(i), c) for i, c in enumerate(arg if isinstance(arg, list) else [arg])]
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None; res = {}
    for lab, par in items:
        t = time.time(); p, r = evaluate(None, par)
        res[lab] = dict(params={k: v for k, v in p.items() if M._jsonable(v)}, secs=round(time.time() - t, 1),
                        report={k: v for k, v in r.items() if M._jsonable(v) and k not in ("near_low",)})
        print(lab, json.dumps({k: r.get(k) for k in ("gap", "v_gap", "v_near_gap", "fit_gap", "honest", "audit", "min_metal_all_faces", "v",
                                                     "hub_F", "big_mode")}, default=float), f"{time.time() - t:.1f}s", flush=True)
        if out: json.dump(res, open(out, "w"), indent=1, default=float)

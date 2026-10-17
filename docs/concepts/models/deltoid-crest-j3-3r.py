"""deltoid-crest-j3-3r: the deltoid-crest J3 equal-arc spherical 3R, re-measured at O20 / fold margin 5 (closing screen,
round 14, carried round-4 pick; doubles as crest-knee-3r's no-knee control and seeds lens plain-crest-j3-cap).

Chain (complexity 0, 0 passive joints): scapula handler (carries the base directly at the J1 hub ring, CAD ruling 1 of
2026-10-16, so the spec's "base stub under link 1" is not a part any more) -> J1 (ACTIVE R, O20 v5 hub, MR117-2RS pair,
12.25 mm stack, axis through GH, seat on the acromion top / cap pole) -> link 1 (12 x 3 Ti, arc a1) -> J2 (ACTIVE R, O20,
branch sigma) -> link 2 (12 x 3 Ti, arc a2) -> J3 (ACTIVE R, O20, humerus-fixed axis on the DELTOID CREST: wd 95-120,
i.e. 10-35 deg higher on the arm than the leaders' wd 82-86) -> member 3 = hub 3's arm plate + K7 14 x 6 neck rigid to
BOTTOM's bar -> cuff. Stack orders inv2 / inv3 (inv3 = the inverted J3 stack the spec asks for: link 2 on hub 3's
LOWER plate, member 3 on the cap plate bridging over link 2).

Build and every check = docs/concepts/models/zc-frontier-3r.py UNCHANGED (kit K1-K7 + dense K2, O20 audit, hub crown /
wall skin check, near-touch, overhead split, and docs/concepts/verify/spine-parked-j2-3r.py's top_check: top faces of
every member, near-touch over all faces, closure residual, hub-axis accessibility F <= 140 mm, 1 mm radial K6). The
objective `gap` = that verifier's plain gap (+100 if not honest, +200 if the J1 seat breaks ruling 4). This file only
restricts the search to the crest basin (BOX) and adds the coarse sweep / sweep-file writer.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/deltoid-crest-j3-3r.py check ['<json>'] [--attr]
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/deltoid-crest-j3-3r.py coarse N SEED [--procs 2]
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/deltoid-crest-j3-3r.py ingest CMA_OUT.json PHASE
    CMA: python3 tools/concept_cma.py docs/concepts/models/deltoid-crest-j3-3r.py --x0 .. --scales .. --base .. --jobs 2
    frozen exact: CB_EXACT=1 python3 docs/concepts/models/deltoid-crest-j3-3r.py frozen '<json>' OUT.json
"""
import datetime, importlib.util, json, math, multiprocessing as mp, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


ZC = _load("dc_zc", os.path.join(REPO, "docs", "concepts", "models", "zc-frontier-3r.py"))
K = ZC.K
ID = "deltoid-crest-j3-3r"
NAME = "Deltoid-crest J3 equal-arc 3R (O20, margin 5)"
SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
# the crest basin: J1 on the acromion top / cap pole (inside ruling 4), J3 on the deltoid crest, near-equal arcs
BOX = dict(az=(30.0, 120.0), el=(48.0, 80.0), a1=(34.0, 64.0), a2=(38.0, 70.0), wd=(95.0, 120.0), wa=(-20.0, 20.0),
           q=(0.85, 1.0), end_extra=(0.0, 6.0))
SEEDS = dict(  # round-4 seeds (O15 / margin 10 numbers 26.35 fast, 35.90 frozen) and the round-102 cap-pole crest cell
    A=dict(az=94.09, el=61.93, a1=45.06, a2=50.02, wd=108.48, wa=-6.87, q=0.970, end_extra=2.05, sigma=-1, inv2=0, inv3=1),
    B=dict(az=95.37, el=62.54, a1=44.53, a2=50.26, wd=108.87, wa=-3.53, q=0.970, end_extra=2.23, sigma=-1, inv2=0, inv3=1),
    cap=dict(az=55.0, el=62.0, a1=50.0, a2=58.0, wd=98.0, wa=5.0, q=0.97, end_extra=0.0, sigma=-1, inv2=0, inv3=1))
PARAMS = dict(ZC.PARAMS, **SEEDS["A"])
REPORT_KEYS = ("near", "model_gap", "hub_F", "hub_F_ok", "min_metal_all_faces", "top_contact_poses", "overhead", "v_near1",
               "crown_contact_poses", "in_box")
build = ZC.build


def snap(params):
    """ZC.snap (rules never loosened) + the crest box (clamped, so CMA meets the box edge instead of leaving the basin)"""
    p = ZC.snap(dict(PARAMS, **params)); inb = True
    for k, (lo, hi) in BOX.items():
        v = float(p[k])
        if v < lo or v > hi: inb = False
        p[k] = min(hi, max(lo, v))
    p["in_box"] = inb
    return p


def evaluate(B, params, fixed_prof=None):
    p = snap(params); ib = p.pop("in_box")
    p, r = ZC.evaluate(B, p, fixed_prof); r["in_box"] = ib
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if ZC.SPM._jsonable(v)}


def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sweep_row(k, p, r, phase):
    return dict(k=k, t=now(), phase=phase, params={a: v for a, v in p.items() if isinstance(v, (int, float, str, bool))},
                inband14=r.get("inband14"), inband10=r.get("inband10"), reach=r.get("reach"), follow=r.get("follow"),
                contact=r.get("contact"), gap=r.get("gap"), near=r.get("near"), honest=r.get("honest"),
                hub_F=r.get("hub_F"), inband_member=r.get("inband_member"), overhead=r.get("overhead"))


def append_sweep(rows):
    old = json.load(open(SWEEP_OUT)) if os.path.exists(SWEEP_OUT) else []
    k0 = len(old)
    for i, r in enumerate(rows): r["k"] = k0 + i
    json.dump(old + rows, open(SWEEP_OUT + ".tmp", "w"), indent=0, default=float); os.replace(SWEEP_OUT + ".tmp", SWEEP_OUT)


_W = {}


def _one(arg):
    tag, p = arg
    if "B" not in _W: _W["B"] = K.bench(60, 160)
    t0 = time.time()
    try:
        pf, r = evaluate(_W["B"], p); r = {k: v for k, v in r.items() if ZC.SPM._jsonable(v)}
        return tag, pf, r, round(time.time() - t0, 1)
    except Exception as e:                                                        # noqa: BLE001
        return tag, p, dict(gap=400.0, error=repr(e), trace=traceback.format_exc()[-500:]), round(time.time() - t0, 1)


def coarse(n, seed, procs=2):
    """Sobol over BOX x sigma x inv2 x inv3 (+ the three seeds first), Bench(60,160) fast, sweep file appended as it goes"""
    from scipy.stats import qmc
    keys = list(BOX); X = qmc.Sobol(d=len(keys) + 3, scramble=True, seed=seed).random(n)
    cfgs = [dict(s) for s in SEEDS.values()] + [dict(s, inv3=0) for s in SEEDS.values()]
    for x in X:
        c = {k: round(BOX[k][0] + x[i] * (BOX[k][1] - BOX[k][0]), 3) for i, k in enumerate(keys)}
        c.update(sigma=1 if x[-3] >= 0.5 else -1, inv2=int(x[-2] >= 0.5), inv3=int(x[-1] >= 0.35))   # inv3 weighted 65 %
        if ZC.seat_ok(c["az"], c["el"]): cfgs.append(c)
    print(f"coarse: {len(cfgs)} configs", flush=True); best = 1e9; buf = []
    with mp.Pool(procs) as pool:
        for tag, pf, r, s in pool.imap_unordered(_one, [(f"coarse-{i}", c) for i, c in enumerate(cfgs)]):
            buf.append(sweep_row(0, pf, r, "coarse")); best = min(best, float(r.get("gap", 400)))
            print(f"{tag} gap {r.get('gap')} near {r.get('near')} reach {r.get('reach')} ib14 {r.get('inband14')} follow {r.get('follow')} "
                  f"contact {r.get('contact')} hubF {r.get('hub_F')} best {best:.2f} {s}s", flush=True)
            if len(buf) >= 4: append_sweep(buf); buf = []
    if buf: append_sweep(buf)


def ingest(path, phase):
    """append a tools/concept_cma.py output (in order) to the sweep file"""
    rows = json.load(open(path)); out = []
    for r in rows:
        rep = dict(r.get("report") or {}, gap=r.get("obj", 400.0))
        out.append(sweep_row(0, r.get("params", {}), rep, f"{phase}:{r.get('tag')}"))
    append_sweep(out); print(f"ingested {len(out)} rows from {path}")


def frozen(p0, out):
    """fit Bench(60,160) FAST, freeze every level, wear Bench(110,360) (CB_EXACT=1: exact) - zc_frontier's cmd_frozen
    fit60 protocol on this file's snap; + the loss attribution"""
    p0 = snap(p0); p0.pop("in_box")
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, fold_margin=K.FOLD_MARGIN, t0=now())
    ex = os.environ.pop("CB_EXACT", None)
    try: Bf = K.bench(60, 160)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    res["fit"] = {k: rf.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest", "hub_F", "inband_member")}
    res["fit_mode"] = Bf.mode; res["fit_attribution"] = ZC.attribute(Bf, pf, rf)
    json.dump(res, open(out, "w"), indent=1, default=float); print("fit", json.dumps(res["fit"], default=float), flush=True)
    Bb = K.bench(110, 360); t = time.time()
    pb, rb = evaluate(Bb, dict(p0), fixed_prof=prof)
    res["wear_mode"] = Bb.mode; res["wear"] = {k: v for k, v in rb.items() if ZC.SPM._jsonable(v) and k != "checks"}
    res["wear_attribution"] = ZC.attribute(Bb, pb, rb); res["secs"] = round(time.time() - t, 1)
    res["score"] = round(100 * (1 - float(rb["gap"]) / 275), 2)
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("wear", Bb.mode, json.dumps({k: rb.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest",
                                                         "audit", "hub_F", "inband_member", "overhead", "min_metal_all_faces")}, default=float), flush=True)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "coarse":
        pr = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 2
        coarse(int(sys.argv[2]), int(sys.argv[3]), pr); sys.exit()
    if mode == "ingest": ingest(sys.argv[2], sys.argv[3]); sys.exit()
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen": frozen(dict(PARAMS, **par), sys.argv[3]); sys.exit()
    B = K.bench(60, 160); t = time.time(); p, r = evaluate(B, par)
    print(json.dumps({k: r.get(k) for k in ("gap", "near", "model_gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit",
                                            "hub_F", "min_metal_all_faces", "top_contact_poses", "inband_member", "overhead", "mode", "in_box")},
                     default=float), f"{time.time() - t:.1f}s", flush=True)
    if "--attr" in sys.argv: print(json.dumps(ZC.attribute(B, p, r), default=float))

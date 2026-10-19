"""Alignment re-wear for plain kit-built models (a module with build(B, F, p) only: no frozen(), no pin-knee audit(M, B),
no snap() / evaluate(fixed_prof)) - e.g. the round-1 screens (clavicular-front-route). Read-only on every claim: the
model file runs UNCHANGED through the kit's own K.evaluate (march, dense K2, K6, audit), so the fit reproduces the
screen. Then:
  fit60   Bench(60,160) fast (the screen's own bench): the claim's number, per-pose dump (tools/alignment_paired.py
          format), alignment_audit.deep_audit (near-touch 1 / 2 / 3 mm, band read 3-14 mm), wear probe analyse()
          (unscored workspace in-band, overhead, clearance floors, contact depths), min th fold margin over taken poses,
          J1 seat in bvec terms against user ruling 4 (the searches' seat_ok: az -110..135, el -20..90, anterior <= 0.20).
  bench   the fit's profiles FROZEN (K.fit_profiles returns them; a strap whose sample count differs on the wear bench
          is resampled along its length, stated in the output) and worn on Bench(110,360) (exact with CB_EXACT=1).
  held    the same frozen shape worn on poses disjoint from Bench(110,360) (= tools/osn_polish.py held_bench, exact).

    [CB_EXACT=1] OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_kitbuild_rewear.py <id> fit60|bench|held
        -> docs/alignment/remeasure/<id>_<wear>.json (+ <id>_<wear>_perpose.json)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402
import alignment_wear_probe as WP                                # noqa: E402
import alignment_paired as AP                                    # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


class _M:            # deep_audit / analyse read M.cmin (no extra walls in a kit build) and M.why (absent)
    cmin = {}


def held_bench(CB, nc=110, nw=360):
    """= tools/osn_polish.py held_bench: poses DISJOINT from Bench(110,360) (held-out clips still excluded), exact path"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
    big, _, _, _ = CB._select(110, 360); bigs = set(big.tolist())
    fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
    cl = np.array([i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in bigs]); ws = np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in bigs])
    cl = cl[np.linspace(0, len(cl) - 1, min(nc, len(cl))).round().astype(int)]; ws = ws[np.linspace(0, len(ws) - 1, min(nw, len(ws))).round().astype(int)]
    B = CB.Bench(20, 20); idx = np.r_[cl, ws]
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws); B.clip = [names[c] for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in P[idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = "held"
    return B


def seat(K, p):
    """the J1 seat in bvec(az, el) terms (sdir(lat, lon) of the model -> az = atan2(cos lon, sin lon), el = lat) and the
    searches' ruling-4 test (docs/concepts/models/zc-frontier-3r.py seat_ok, tools/gpu_bench.py seat_ok)"""
    lat, lon = float(p["j1lat"]), float(p["j1lon"]); D = math.pi / 180
    az = math.degrees(math.atan2(math.cos(lon * D), math.sin(lon * D))); u = K.bvec(az, lat)
    return dict(sdir=[lat, lon], az=round(az, 2), el=round(lat, 2), anterior=round(float(u[0]), 4), up=round(float(u[1]), 4),
                lateral=round(float(u[2]), 4), az_ok=bool(-110.0 <= az <= 135.0), el_ok=bool(-20.0 <= lat <= 90.0),
                ant_ok=bool(float(u[0]) <= 0.20), seat_ok=bool(-110.0 <= az <= 135.0 and -20.0 <= lat <= 90.0 and float(u[0]) <= 0.20))


def th_margin(K, B, p):
    """min J1-J3 fold margin (th, concept_kit lines 25-30) over the taken poses, from the chain's own joint axes"""
    L = B._kit_last; ch = L["chain"]; tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
    if not tk.any(): return None
    a1, a2 = float(p["a12"]), float(p["a23"])
    j1, j3 = K.unit(np.asarray(ch.joints["J1"], float)), K.unit(np.asarray(ch.joints["J3"], float))
    th = np.degrees(np.arccos(np.clip((j1 * j3).sum(-1), -1, 1)))
    m = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])[tk]
    return dict(min=round(float(m.min()), 3), p05=round(float(np.percentile(m, 5)), 3), n=int(tk.sum()), lt5=int((m < 5).sum()),
                declared=float(p.get("margin", 0)))


def _resample(prof, ch):
    """frozen profiles onto a wear-bench chain: same size -> as is; a strap with another sample count along its length ->
    linear resample along s per across-column (the strap's sample count follows the median arc of the bench's poses)"""
    out, notes = {}, []
    for m in ch.members:
        r = np.asarray(prof[m.name], float); n = m.D.shape[1]
        if len(r) == n: out[m.name] = r.copy(); continue
        if m.grid and len(r) % m.grid[1] == 0:
            nc = m.grid[1]; ns0 = len(r) // nc; R0 = r.reshape(ns0, nc); s0 = np.linspace(0, 1, ns0); s1 = np.linspace(0, 1, m.grid[0])
            out[m.name] = np.stack([np.interp(s1, s0, R0[:, c]) for c in range(nc)], 1).ravel(); notes.append(f"{m.name}: {ns0} -> {m.grid[0]} rows")
        else:
            raise SystemExit(f"{m.name}: frozen profile has {len(r)} samples, wear chain {n}; cannot freeze")
    return out, notes


def run(rid, wear):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json")))
    mod = _load("akb_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py")); K = mod.K
    P = dict(mod.PARAMS, **(row.get("best_params") or {})); t0 = time.time()
    ex = os.environ.pop("CB_EXACT", None)
    try: Bf = K.bench(60, 160)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    rf = K.evaluate(Bf, mod.build, dict(P))
    fit = {k: rf.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips",
                                  "collide", "min_margin", "residual_deg", "inband_member", "mass_g")}
    print("fit", json.dumps(fit, default=float), flush=True)
    out = dict(id=rid, wear=wear, params=P, fit_fast=fit, seat=seat(K, P), git=AA._git("rev-parse", "--short", "HEAD"))
    if wear == "fit60":
        B = Bf; rep = fit; out["pose_report"] = mod.pose_report(B, rf) if hasattr(mod, "pose_report") else None; notes = []
    else:
        prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        B = K.bench(110, 360) if wear == "bench" else held_bench(K.CB)
        F = K.frames(B); B._kitF = F; ch = mod.build(B, F, dict(P)); fixed, notes = _resample(prof, ch)
        fp = K.fit_profiles
        K.fit_profiles = lambda B_, chain, fit_, q=1.0, mode="march": {k: v.copy() for k, v in fixed.items()}
        try:
            rb = K.evaluate(B, mod.build, dict(P))
        finally:
            K.fit_profiles = fp
        rep = {k: rb.get(k) for k in fit}
        out["pose_report"] = mod.pose_report(B, rb) if hasattr(mod, "pose_report") else None
    print("wear", B.mode, json.dumps(rep, default=float), flush=True)
    deep = AA.deep_audit(_M, B)
    WP.kind, WP.el = np.array(B.kind), np.array([p["elev"] for p in B.poses])
    probe = WP.analyse(_M, B)
    poses = AP._dump_bench(_M, B)
    out.update(frozen=rep, parts_ib14=rep.get("inband_member"), deep=deep, probe=probe, th_margin=th_margin(K, B, P),
               resample=notes, mode=B.mode, exact=B.mode == "exact", secs=round(time.time() - t0, 1),
               source=f"tools/alignment_kitbuild_rewear.py: model {rid}.py unchanged (K.evaluate, every kit check on); fit Bench(60,160) fast"
                      + ("" if wear == "fit60" else f", profiles frozen, worn on {'Bench(110,360)' if wear == 'bench' else 'held_bench(110,360)'}"))
    os.makedirs(AA.REM, exist_ok=True)
    path = os.path.join(AA.REM, f"{rid}_{wear}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    pp = os.path.join(AA.REM, f"{rid}_{wear}_perpose.json")
    json.dump(dict(id=rid, wear=("held" if wear == "held" else "bench"), bench=wear, params=P, frozen=dict(gap=rep.get("gap")), poses=poses,
                   recomputed=AP.gap_parts(poses), mode=B.mode, exact=B.mode == "exact", git=out["git"]), open(pp, "w"), default=float)
    print(json.dumps(dict(frozen={k: v for k, v in rep.items() if k != "inband_member"}, th=out["th_margin"], seat=out["seat"],
                          deep={k: v for k, v in deep.items() if k != "coord_spans"}, recomputed=AP.gap_parts(poses), secs=out["secs"], out=path), default=float))
    return out


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])

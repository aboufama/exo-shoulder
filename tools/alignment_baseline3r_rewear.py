"""Alignment re-wear adapter for the swarm's reference row baseline-3r (tools/concept_baseline.py), whose kit rebuild
docs/concepts/models/baseline-3r-kit.py (a build(B, F, p) module with its OWN two convention sets) the generic
tools/alignment_kitbuild_rewear.py cannot drive (it expects <id>.py, best_params, j1lat / a12 parameter names).

Read-only on every claim: the kit model runs UNCHANGED through K.evaluate with either of its own convention sets:
  claim   = the model's BASELINE dict (mode 'outer', no continuity, no collision check: tools/concept_baseline.py, the row)
  honest  = the model's HONEST dict (K3 march, K2 dense continuity, K6 collisions: the kit's honesty rules)
and optional parameter overrides (e.g. sing_deg=5: the user's fold margin since 2026-10-16 - a MEASUREMENT readout,
never an input to the verdict). Waves:
  fit60   Bench(60,160) fast (the row's own bench): the claim's number, per-pose dump, deep_audit (near-touch 1/2/3 mm,
          band read 3-14 mm), wear-probe analyse() (unscored workspace in-band, overhead, clearance floors, contact
          depths), min th fold margin over taken poses.
  bench   the fit60 profiles FROZEN, worn on Bench(110,360) (exact with CB_EXACT=1).
  held    the same frozen shape on poses disjoint from Bench(110,360) (tools/alignment_kitbuild_rewear.held_bench).

    [CB_EXACT=1] OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_baseline3r_rewear.py claim|honest fit60|bench|held [key=val ...]
        -> docs/alignment/remeasure/baseline-3r_<wear>.json for the claim convention with no overrides (the files the
           audit reads), else baseline-3r_<conv>[_<overrides>]_<wear>.json; + the matching _perpose.json dump
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402
import alignment_wear_probe as WP                                # noqa: E402
import alignment_paired as AP                                    # noqa: E402
import alignment_kitbuild_rewear as KB                           # noqa: E402

RID = "baseline-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def th_margin(K, B, p):
    """min J1-J3 fold margin (th, tools/concept_kit.py lines 25-30) over the taken poses, from the chain's joint axes"""
    ch = B._kit_last["chain"]
    tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
    if not tk.any(): return None
    a1, a2 = float(p["a1"]), float(p["a2"])
    j1, j3 = K.unit(np.asarray(ch.joints["J1"], float)), K.unit(np.asarray(ch.joints["J3"], float))
    th = np.degrees(np.arccos(np.clip((j1 * j3).sum(-1), -1, 1)))
    m = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])[tk]
    return dict(min=round(float(m.min()), 3), p05=round(float(np.percentile(m, 5)), 3), n=int(tk.sum()), lt5=int((m < 5).sum()),
                lt10=int((m < 10).sum()), declared=float(p.get("sing_deg", 0)))


def overhead(B):
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    ev = np.array([B.res[i] is not None for i in range(len(B.res))])
    tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.res))])
    ws = kind == "ws"; out = {}
    for lo, hi, nm in ((140, 1e9, "overhead_ge140"), (120, 140, "raised_120_140"), (90, 120, "el_90_120"), (-1e9, 90, "el_lt90")):
        s = ws & (el >= lo) & (el < hi)
        out[nm] = dict(n=int(s.sum()), taken=int((s & tk).sum()), evaluated=int((s & ev).sum()), contact=int((s & ev & ~tk).sum()))
    return out


def run(conv, wear, over):
    mod = _load("ab3r_kit", os.path.join(AA.MODELS, "baseline-3r-kit.py")); K = mod.K
    kw = dict(mod.BASELINE if conv == "claim" else mod.HONEST); P = dict(mod.PARAMS, **over); t0 = time.time()
    ex = os.environ.pop("CB_EXACT", None)
    try: Bf = K.bench(60, 160)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    rf = K.evaluate(Bf, mod.build, dict(P), **kw)
    keys = ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide",
            "residual_deg", "inband_member", "mass_g")
    fit = {k: rf.get(k) for k in keys}
    print("fit", json.dumps(fit, default=float), flush=True)
    out = dict(id=RID, conv=conv, conventions=kw, overrides=over, wear=wear, params=P, fit_fast=fit, git=AA._git("rev-parse", "--short", "HEAD"))
    notes = []
    if wear == "fit60":
        B = Bf; rep = fit
    else:
        prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        B = K.bench(110, 360) if wear == "bench" else KB.held_bench(K.CB)
        F = K.frames(B); B._kitF = F; ch = mod.build(B, F, dict(P)); fixed, notes = KB._resample(prof, ch)
        fp = K.fit_profiles
        K.fit_profiles = lambda B_, chain, fit_, q=1.0, mode="march": {k: v.copy() for k, v in fixed.items()}
        try: rb = K.evaluate(B, mod.build, dict(P), **kw)
        finally: K.fit_profiles = fp
        rep = {k: rb.get(k) for k in keys}
    print("wear", B.mode, json.dumps(rep, default=float), flush=True)
    deep = AA.deep_audit(KB._M, B)
    WP.kind, WP.el = np.array(B.kind), np.array([p["elev"] for p in B.poses])
    probe = WP.analyse(KB._M, B)
    poses = AP._dump_bench(KB._M, B)
    out.update(frozen=rep, parts_ib14=rep.get("inband_member"), deep=deep, probe=probe, th_margin=th_margin(K, B, P), elev=overhead(B),
               resample=notes, mode=B.mode, exact=B.mode == "exact", secs=round(time.time() - t0, 1),
               source=f"tools/alignment_baseline3r_rewear.py: docs/concepts/models/baseline-3r-kit.py unchanged, K.evaluate with its "
                      f"{'BASELINE' if conv == 'claim' else 'HONEST'} conventions; fit Bench(60,160) fast"
                      + ("" if wear == "fit60" else f", profiles frozen, worn on {'Bench(110,360)' if wear == 'bench' else 'held_bench(110,360)'}"))
    tag = "" if (conv == "claim" and not over) else conv + "".join(f"_{k}{v}" for k, v in sorted(over.items())) + "_"
    os.makedirs(AA.REM, exist_ok=True)
    path = os.path.join(AA.REM, f"{RID}_{tag}{wear}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    pp = os.path.join(AA.REM, f"{RID}_{tag}{wear}_perpose.json")
    json.dump(dict(id=RID, wear=("held" if wear == "held" else "bench"), bench=wear, conv=conv, overrides=over, params=P,
                   frozen=dict(gap=rep.get("gap")), poses=poses, recomputed=AP.gap_parts(poses), mode=B.mode, exact=B.mode == "exact",
                   git=out["git"]), open(pp, "w"), default=float)
    print(json.dumps(dict(frozen={k: v for k, v in rep.items() if k != "inband_member"}, th=out["th_margin"], elev=out["elev"],
                          deep={k: v for k, v in deep.items() if k != "coord_spans"}, recomputed=AP.gap_parts(poses), secs=out["secs"], out=path),
                     default=float))
    return out


if __name__ == "__main__":
    ov = {}
    for a in sys.argv[3:]:
        k, v = a.split("="); ov[k] = float(v)
    run(sys.argv[1], sys.argv[2], ov)

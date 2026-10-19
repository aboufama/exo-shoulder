"""Alignment readouts (read-only, model unchanged): baseline-3r claim-convention readouts on Bench(60,160) fast (and held for a few): profile-quantile
spread (the row's best-of-6), sing_deg 5 (user fold margin), hub 1 / all hubs at true O20 (what-if). Read-only.

    [CB_EXACT=1] OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_baseline3r_readouts.py <out_dir> q|qheld|sing5|o20 [fit60,held]
        q / qheld: the row's profile-quantile sweep (p60-p100) on Bench(60,160) / held out; sing5: fold margin 5 deg in th;
        o20: hub 1 (or all hubs) laid out as a true O20 disc at its fitted radius (K.cap_dirs r_ref = that radius).
"""
import json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA
import alignment_baseline3r_rewear as BR
OUT = sys.argv[1]; which = sys.argv[2]; WEARS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["fit60", "held"]
AA.REM = OUT
res = {}
def pick(o):
    f = o["frozen"]; d = o["deep"]
    return dict(gap=f["gap"], reach=f["reach"], inband14=f["inband14"], contact=f["contact"], near1=d["gap_near1"], near2=d["gap_near2"],
                near2_poses=d["near2_poses"], min_mm=d["min_metal_mm"], th_min=(o["th_margin"] or {}).get("min"),
                overhead=o["elev"]["overhead_ge140"], audit=f.get("audit"), parts=o.get("parts_ib14"))
if which == "q":
    for q in (0.6, 0.7, 0.8, 0.9, 0.95, 1.0):
        res[f"q{q}"] = pick(BR.run("claim", "fit60", dict(q=q)))
elif which == "qheld":
    for q in (0.9, 1.0):
        res[f"q{q}_held"] = pick(BR.run("claim", "held", dict(q=q)))
elif which == "sing5":
    for w in ("fit60", "held"):
        res[f"sing5_{w}"] = pick(BR.run("claim", w, dict(sing_deg=5.0)))
elif which == "o20":
    import concept_kit as K
    orig = K.cap_dirs
    # pass 1: fitted hub radii (cap = one radius) from the claim fit
    import importlib
    for mode in ("hub1", "all"):
        ex = os.environ.pop("CB_EXACT", None)
        Bf = K.bench(60, 160)
        if ex is not None: os.environ["CB_EXACT"] = ex
        mod = BR._load("ab3r_kit2", os.path.join(AA.MODELS, "baseline-3r-kit.py"))
        r = K.evaluate(Bf, mod.build, dict(mod.PARAMS), **mod.BASELINE)
        rad = [float(np.max(Bf._kit_last["prof"][f"hub{k + 1}"])) for k in range(3)]
        cnt = {"n": 0}
        def patched(k, rad_=K.HUB_R, step=2.5, r_ref=70.0, _m=mode):
            i = cnt["n"] % 3; cnt["n"] += 1
            if _m == "all" or i == 0: return orig(k, rad_, step, rad[i])
            return orig(k, rad_, step, r_ref)
        K.cap_dirs = patched
        try:
            for w in WEARS:
                cnt["n"] = 0
                res[f"o20_{mode}_{w}"] = dict(pick(BR.run("claim", w, dict(o20=1.0 if mode == "hub1" else 3.0))), hub_radii_mm=[round(x, 1) for x in rad])
        finally:
            K.cap_dirs = orig
json.dump(res, open(os.path.join(OUT, f"spread_{which}_{'_'.join(WEARS)}.json"), "w"), indent=1, default=float)
print(json.dumps(res, default=float))

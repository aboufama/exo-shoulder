"""fold-ceiling step 3b: put a fold-ceiling seat into the VERIFIED leader model (roller-longdyad-knuckle-3r: its drive,
pin knee, cuff, greedy fit, every verifier check) by solving the model's own seat parameters for target axes:
J1 = bvec(az1, el1), J3 = wdir(d3, a3) (b3 = 0: no tilt, then the model's u3 is wdir(wd, wa) - checked), J2 at rest =
the two-circle point at a1 from J1 and a2 from J3 on branch sigma, K dyad bk1 / bk2, a1max.
    python3 docs/research/fold_ceiling/reseat.py '<json target>'   -> prints the model params + its fast fit"""
import importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB; import concept_kit as K  # noqa: E402
ID = "roller-longdyad-knuckle-3r"
sp = importlib.util.spec_from_file_location("lead_model_rs", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
MOD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MOD)
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json")))["best_params"]


def inv_bvec(u): return math.degrees(math.atan2(u[2], -u[0])), math.degrees(math.asin(np.clip(u[1], -1, 1)))


def params_for(t, sigma2=None):
    u1 = K.bvec(t["az1"], t["el1"]); u3 = K.wdir(t["d3"], t["a3"])
    best = None
    for sg in ((-1.0, 1.0) if sigma2 is None else (sigma2,)):
        u2, ok, _ = K.closure(u1[None], u3[None], t["a1"], t["a2"], sg, margin_deg=0.0)
        az2, el2 = inv_bvec(u2[0]); P = dict(LEAD, az1=t["az1"], el1=t["el1"], az2=az2, el2=el2, wd=t["d3"], wa=t["a3"], b3=0.0,
                                             bk1=t["bk1"], bk2=t["a1max"] + 5.0 - t["bk1"] + t.get("bk_slack", 0.3), a1max=t["a1max"])
        P.update({k: v for k, v in t.get("extra", {}).items()})
        yield sg, P


if __name__ == "__main__":
    t = json.loads(sys.argv[1]); B1 = CB.Bench(60, 160)
    for sg, P in params_for(t):
        try:
            r, M = MOD._report(B1, MOD._clamp(dict(MOD.PARAMS, **P))); D = M.D
            print(json.dumps(dict(sigma_rest=sg, a1=round(D.a1, 2), a2=round(D.a2, 2), u3_err=round(math.degrees(math.acos(np.clip(D.u[2] @ K.wdir(t["d3"], t["a3"]), -1, 1))), 2),
                                  branch=D.branch, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), reach=r["reach"], follow=r["follow"], ib=r["inband14"],
                                  contact=r["contact"], why=r.get("why"), honest=r.get("honest"), parts=r.get("parts_ib14"), cam=r.get("cam"), params=P), default=float), flush=True)
        except Exception as e:  # noqa: BLE001
            print("sigma", sg, "FAILED", repr(e)[:300], flush=True)

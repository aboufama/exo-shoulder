"""fold-ceiling step 3c: the window RE-PLACEMENT lever on the verified leader model itself (roller-longdyad-knuckle-3r,
every check unchanged): J2's rest axis is turned about J1 (a1 kept) until the model's own a2 reaches the target, so the
whole J1-J3 window slides up (lo = a2 - a1 + 5, hi = a1max + a2 - 5). kin_ceiling.py: at the leader's seats and width
the 360-pose optimum is a2 ~ 62 (+10 poses in the window) - the fit bench's 160 poses put it at 57.2 (winner's curse).
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/shift_a2.py <a2_target> [fit|frozen|held]"""
import importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB; import concept_kit as K  # noqa: E402
ID = "roller-longdyad-knuckle-3r"
sp = importlib.util.spec_from_file_location("lead_model_sa", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
MOD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MOD)
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json")))["best_params"]
B1 = CB.Bench(60, 160); r0, M0 = MOD._report(B1, MOD._clamp(dict(MOD.PARAMS, **LEAD))); DC = type(M0.D)


def inv_bvec(u): return math.degrees(math.atan2(u[2], -u[0])), math.degrees(math.asin(float(np.clip(u[1], -1, 1))))


def design(P): return DC(MOD._clamp(dict(MOD.PARAMS, **P)))


def params_for_a2(target):
    u1 = K.bvec(LEAD["az1"], LEAD["el1"]); u2 = K.bvec(LEAD["az2"], LEAD["el2"]); best = None
    grid = list(np.arange(-30, 30.01, 3.0))
    for stage in range(2):
      for psi in grid:
        v = K.unit(np.cos(np.radians(psi)) * u2 + np.sin(np.radians(psi)) * np.cross(u1, u2) + (1 - np.cos(np.radians(psi))) * (u1 @ u2) * u1)
        az2, el2 = inv_bvec(v); P = dict(LEAD, az2=az2, el2=el2)
        try: D = design(P)
        except Exception: continue
        e = abs(D.a2 - target) + abs(D.a1 - M0.D.a1)
        if best is None or e < best[0]: best = (e, psi, P, D.a1, D.a2)
      grid = list(best[1] + np.arange(-3, 3.01, 0.25))
    return best


if __name__ == "__main__":
    tgt = float(sys.argv[1]); mode = sys.argv[2] if len(sys.argv) > 2 else "fit"
    e, psi, P, a1, a2 = params_for_a2(tgt)
    print(json.dumps(dict(psi=psi, a1=round(a1, 3), a2=round(a2, 3), lead_a1=round(M0.D.a1, 3), lead_a2=round(M0.D.a2, 3), az2=P["az2"], el2=P["el2"])), flush=True)
    t = time.time()
    if mode == "fit":
        r, M = MOD._report(B1, MOD._clamp(dict(MOD.PARAMS, **P)))
        print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), reach=r["reach"], follow=r["follow"], ib=r["inband14"],
                              contact=r["contact"], why=r.get("why"), honest=r.get("honest"), cam=r.get("cam"), parts=r.get("parts_ib14")), default=float))
    else:
        os.environ["CB_EXACT"] = "1"
        out = MOD.frozen(P) if mode == "frozen" else MOD.frozen_held(P); out["params"] = P; out["secs"] = round(time.time() - t, 1)
        json.dump(out, open(os.path.join(HERE, f"shift_a2_{tgt:g}_{mode}.json"), "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=a.get("overhead140"), secs=out["secs"]), default=float))

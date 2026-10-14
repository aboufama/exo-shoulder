"""CPU checks of the band evaluator's link-arm guard and the pure 3R chain - no skin maps, no GPU, one process.

    python3 test_band_guard.py            (or pytest test_band_guard.py)

1. the pure rules: link_arcs_ok / arm_clear_mm / hub_heights / arms_ok on the r13 reference (docs/FINDINGS.md "Short link")
2. the search samplers (rand_d, mutate) never leave [max(arc_range[0], min_arc), arc_range[1]], for N = 3, 3 + cuff, 4
3. Band.evaluate on a synthetic skin (a sphere round GH, real poses, strided) instead of .cache/maps_s1.pt:
   rejects r13's kinematics with the min-arc error, rejects big hubs on a 36 deg link with the min-arm error, and runs
   the pure 3R chain (N = 3, no cuff: one configuration per pose, chain closure checked) end to end.
4. band_search smoke (pop 4, 2 generations) seeded with r13: seeds lifted to the bound, nothing returned below it.
The synthetic-skin scores mean nothing; only the guard / chain behaviour is tested. ~30 s on 2 threads.
"""
import base64, gzip, hashlib, io, json, math, os, random, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); CONF = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(CONF, "gpu"))
import band_impl as BI

R13_IN = os.path.join(CONF, "band_cad", "inputs", "r13_n4_s1343_1.json")
R13 = {k: v for k, v in json.load(open(R13_IN))["results"][0].items()}
R13_D = {k: R13[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "hm") if k in R13}
R13_GEO = dict(hub_r=11.5, stack=3.15, t_link=5.5, t_lo=3.0, hub_up=4.05, cap_up=3.3, rail_d=10.0)   # gpu_client/r13_cfgs.json


# ---------------------------------------------------------------- 1. pure rules
def test_pure_rules():
    ok, err = BI.link_arcs_ok(R13_D, 35.0, 65.0, 11.5)
    assert not ok and err.startswith("short link") and "link 1 arc 23.9" in err and "link 3 arc 29.6" in err and "link 2" not in err, err
    assert BI.link_arcs_ok(R13_D, 0.0)[0] and BI.link_arcs_ok(R13_D, 23.0)[0]
    assert BI.link_arcs_ok([35.0, 35.0], 35.0)[0]                                       # the bound itself is allowed
    assert not BI.link_arcs_ok(dict(n=4, a=[40.0, 40.0]), 35.0)[0]                       # wrong arc count is reported, not crashed on
    ok3, err3 = BI.link_arcs_ok(dict(n=3, a=[30.0, 60.0], cuff=dict(range=40, branch=1)), 35.0)   # sliding-cuff variant: same rule
    assert not ok3 and "link 1 arc 30.0" in err3
    # mm equivalents (hub seat r 11.5): 35 deg at R_REF 65 / 60 / 55 / 50
    eq = {r: BI.arm_clear_mm(35.0, r, hub_r=11.5) for r in (45, 50, 55, 60, 65, 70, 80)}
    assert abs(eq[65] - 16.09) < 0.02 and abs(eq[60] - 13.08) < 0.02 and abs(eq[55] - 10.08) < 0.02, eq
    assert abs(BI.arc_for_arm(eq[65], 65, 11.5) - 35.0) < 1e-6
    # r13 as fitted: faces / lower from its detail eval -> link 1's hub planes 57.1 / 62.0 mm from GH, ~2 mm between seats
    H = BI.hub_heights(R13["n"], R13["faces"], R13["lower"], R13["stack"])
    ok_m, err_m, clear = BI.arms_ok(R13["a"], H, 10.0, R13["hub_r"])
    assert not ok_m and err_m.startswith("short arm") and abs(H[0][0] - 57.06) < 0.02 and abs(H[0][1] - 61.99) < 0.02 and 1.5 < clear[0] < 2.5, (H, clear)
    # the CAD-side report (band_to_design warns, make_cad_design refuses on it)
    probs = BI.design_link_report(dict(R13_D), [round(c, 2) for c in clear], hub_r=11.5)
    assert len(probs) == 2 and probs[0].startswith("short link") and probs[1].startswith("short arm: link 1 2.1"), probs
    assert BI.design_link_report(dict(R13_D, a=[40.0, 56.1, 40.0]), [12.0, 39.0, 20.0]) == []
    assert BI.design_link_report(dict(R13_D, a=[40.0, 56.1, 40.0]), [8.0, 39.0, 20.0])[0].startswith("short arm: link 1 8.0")
    print("  pure rules: r13 ->", err)
    print("  r13 fitted hub planes (mm from GH):", [tuple(round(z, 1) for z in h) for h in H], " clear between seats (mm):", [round(c, 1) for c in clear])
    print("  35 deg -> clear arm (mm, seat r 11.5) at R:", {r: round(v, 1) for r, v in eq.items()},
          "| seat r 17 at R 65:", round(BI.arm_clear_mm(35.0, 65.0, hub_r=17.0), 1))


# ---------------------------------------------------------------- 2. samplers
def test_samplers(n_rand=3000, n_mut=3000):
    cases = [dict(n=4, arc_range=[6, 90]), dict(n=3, arc_range=[6, 90]), dict(n=3, arc_range=[6, 90], cuff_range=50, search_range=True, w_range=[40, 140]),
             dict(n=4, arc_range=[6, 90], min_arc=40.0), dict(n=4, arc_range=[50, 90]), dict(n=4, arc_range=[6, 90], min_arc=0.0), dict(n=4)]
    for job in cases:
        lo, hi = BI.arc_bounds(job); rng = random.Random(7); rand_d, mutate = BI.make_samplers(job, rng)
        want_lo = max(float(job.get("arc_range", [20, 100])[0]), float(job.get("min_arc", BI.MIN_ARC)))
        assert lo == want_lo, (job, lo)
        A = []
        for _ in range(n_rand):
            g = rand_d(); assert len(g["a"]) == job["n"] - 1 and ("cuff" in g) == bool(job.get("cuff_range")); A += g["a"]
        g = dict(rand_d(), a=[1.0] * (job["n"] - 1))                                     # even a parent far below the bound
        for k in range(n_mut):
            g = mutate(g, max(0.25, 1.0 - k / n_mut) * (3.0 if k % 7 == 0 else 1.0)); A += g["a"]
        A = np.array(A); assert A.min() >= lo - 1e-9 and A.max() <= hi + 1e-9, (job, A.min(), A.max())
        print(f"  samplers {json.dumps({k: v for k, v in job.items() if k != 'w_range'})}: {len(A)} arcs in [{A.min():.2f}, {A.max():.2f}] (bounds [{lo:g}, {hi:g}])")
    try: BI.arc_bounds(dict(arc_range=[6, 30], min_arc=35)); raise AssertionError("empty arc range accepted")
    except ValueError: pass


# ---------------------------------------------------------------- 3. evaluator on a synthetic skin
def synthetic_band(stride=25, skin_r=55.0, **job_extra):
    """Band over the real poses (every stride-th frame) with a sphere of radius skin_r round GH as the skin"""
    import torch; torch.set_num_threads(int(os.environ.get("THREADS", 2)))
    Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(CONF, "band_poses.b64")).read()))), allow_pickle=False)
    keep = np.arange(0, len(Z["POSE"]), stride); dev = torch.device("cpu")
    P = {k: torch.tensor(Z[k][keep], device=dev) for k in ("HG", "RS", "EL", "CID", "FI", "WT")}
    P["POSE"] = Z["POSE"][keep]; P["NAMES"] = [str(x) for x in Z["NAMES"]]
    NP, S = len(keep), BI.MH * BI.MW
    M = dict(r1=torch.full((NP, S), skin_r, dtype=torch.float16), r1c=torch.full((NP, S), skin_r + BI.CLEAR, dtype=torch.float16),
             r2c=torch.full((NP, S), float("inf"), dtype=torch.float16), cs=torch.ones((NP, S), dtype=torch.float16))
    job = dict(dict(poses=f"synthetic sphere {skin_r} stride {stride}", q_step=30, chunk=8, drop_rounds=8, max_rate=360.0), **job_extra)
    BI._CACHE.clear(); BI._CACHE[hashlib.md5(job["poses"].encode()).hexdigest() + str(job.get("spacing", 0.8))] = (M, P)
    B = BI.Band(job, dev); B.job = job
    return B, P


def set_geo(geo):
    old = {k: getattr(BI, k) for k in ("HUB_R", "STACK", "T_LINK", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D")}
    for k, v in geo.items(): setattr(BI, k.upper(), float(v))
    return old


def test_evaluate_guard_and_3r():
    old = set_geo(R13_GEO)
    try:
        B, P = synthetic_band()
        # (a) the r13 reference kinematics: rejected before any work, with the reason
        t0 = time.time(); r = B.evaluate(dict(R13_D))
        assert r["score"] == -1.0 and r["err"].startswith("short link") and "link 1 arc 23.9" in r["err"], r
        print(f"  evaluate(r13) -> score {r['score']}, err: {r['err']}  ({time.time() - t0:.3f}s)")
        # ... and with the rule off it is scored as before (smoke: the guard is the only change)
        B0, _ = synthetic_band(min_arc=0.0, min_arm_mm=0.0)
        r0 = B0.evaluate(dict(R13_D)); assert "err" not in r0 and r0["score"] >= 0 and len(r0["arm_mm"]) == 3, r0
        print(f"  evaluate(r13, min_arc=0, min_arm_mm=0) on the synthetic skin -> score {r0['score']:.3f}, clear between seats {r0['arm_mm']} mm")
        # (b) pure 3R (N = 3, no cuff): zero spare DOF, one configuration per pose
        d3 = dict(n=3, az=30.0, el=55.0, a=[55.0, 70.0], w=[80.0, 0.0], branch=1, order=[0, 1, 0])
        HG = P["HG"]; pins, ok, Q = B.chain(d3, HG)
        assert tuple(pins.shape) == (HG.shape[0], 1, 3, 3) and tuple(Q.shape) == (1, 0), (pins.shape, Q.shape)
        import torch
        p1, p2, p3 = pins[:, 0, 0], pins[:, 0, 1], pins[:, 0, 2]; okv = ok[:, 0]
        W0 = torch.tensor(BI.w_dir(*d3["w"]), dtype=torch.float32)
        assert bool(okv.any()), "3R chain closes in no pose"
        e1 = ((p1 * p2).sum(-1) - math.cos(math.radians(55)))[okv].abs().max(); e2 = ((p2 * p3).sum(-1) - math.cos(math.radians(70)))[okv].abs().max()
        e3 = (p3 - HG @ W0).abs().max(); assert float(e1) < 1e-4 and float(e2) < 1e-4 and float(e3) < 1e-5, (e1, e2, e3)
        t0 = time.time(); r3 = B.evaluate(d3, detail=True)
        assert "err" not in r3 and r3["C"] == 1 and 0.0 <= r3["score"] <= 1.0 and r3["Q"] == [[]] and len(r3["arm_mm"]) == 2, {k: r3[k] for k in ("score", "C", "err") if k in r3}
        print(f"  3R chain: closes in {int(okv.sum())}/{len(okv)} poses (closure err {float(max(e1, e2)):.1e}); evaluate -> score {r3['score']:.3f} "
              f"follow {r3['follow']:.3f}, C = {r3['C']} configuration, clear between seats {r3['arm_mm']} mm ({time.time() - t0:.1f}s)")
        # (c) 3R + sliding cuff and 4R still run; a cuff design with a short link is rejected the same way
        dc = dict(n=3, az=30.0, el=55.0, a=[55.0, 50.0], w=[100.0, 10.0], branch=1, order=[0, 1, 0], cuff=dict(range=30.0, branch=1))
        rc = B.evaluate(dc); assert "err" not in rc and rc["score"] >= 0, rc
        rcs = B.evaluate(dict(dc, a=[30.0, 50.0])); assert rcs["score"] == -1 and rcs["err"].startswith("short link"), rcs
        d4 = dict(n=4, az=30.0, el=55.0, a=[45.0, 50.0, 45.0], w=[85.0, 0.0], branch=1, order=[0, 1, 0, 1])
        r4 = B.evaluate(d4); assert "err" not in r4 and r4["score"] >= 0, r4
        print(f"  3R + cuff -> score {rc['score']:.3f} (C {rc['C']}); with a 30 deg link -> {rcs['err'][:40]}...; 4R -> score {r4['score']:.3f} (C {r4['C']})")
        # (d) the mm rule: seat r 17 on 36 deg links leaves ~3 mm between the hubs although every arc passes 35 deg
        set_geo(dict(hub_r=17.0))
        B17, _ = synthetic_band()
        r17 = B17.evaluate(dict(d4, a=[36.0, 36.0, 36.0]))
        assert r17["score"] == -1 and r17["err"].startswith("short arm") and "score_unchecked" in r17, r17
        print(f"  seat r 17, arcs 36/36/36 -> err: {r17['err'][:150]}... (would have scored {r17['score_unchecked']:.3f})")
    finally:
        set_geo({k.lower(): v for k, v in old.items()}); BI._CACHE.clear()


def test_search_smoke():
    """band_search end to end (tiny: pop 4, 2 generations) seeded with r13: the seed's arcs are lifted to the bound and
    every returned design has arcs >= min_arc; band_eval of r13 reports the reason"""
    old = set_geo(R13_GEO)
    try:
        B, _ = synthetic_band()                                                          # fills the cache run() will find
        job = dict(B.job, mode="band_search", n=4, seed=3, pop=4, gens=2, elite=2, arc_range=[6, 90], init=[dict(R13_D)], **R13_GEO)
        out = BI.run(job)
        A = [x for b in out["best"] for x in b["a"]]
        assert min(A) >= 35.0 - 1e-9 and out["version"] == BI.CODE_VERSION, (min(A), out["version"])
        ev = BI.run(dict(job, mode="band_eval", designs=[dict(R13_D)]))["results"][0]
        assert ev["score"] == -1 and ev["err"].startswith("short link"), ev
        print(f"  search smoke: {out['evals']} evals, best {out['best'][0]['score']:.3f}, smallest arc returned {min(A):.1f} deg; band_eval(r13) err: {ev['err'][:60]}...")
    finally:
        set_geo({k.lower(): v for k, v in old.items()}); BI._CACHE.clear()


if __name__ == "__main__":
    t0 = time.time()
    for f in (test_pure_rules, test_samplers, test_evaluate_guard_and_3r, test_search_smoke):
        print(f.__name__); f()
    print(f"all passed ({time.time() - t0:.0f}s)")

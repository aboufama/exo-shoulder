"""The champion spherical 3R (tools/concept_baseline.py, r20 s1414 #4) rebuilt on the shared kit (tools/concept_kit.py).

Same parameters, same sampling and the same profile rule as the baseline, so on Bench(60, 160) with the baseline's
conventions (mode 'outer', q 0.95, no continuity / collision check) it must give the baseline row (gap 68.93); with
the kit's honesty checks on (K3 march, K2 continuity, K6 collisions) it gives the honest number of the same design.

    OMP_NUM_THREADS=1 python3 docs/concepts/models/baseline-3r-kit.py [--n-clip 60 --n-ws 160] [--sweep]
"""
import math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "baseline-3r-kit"
PARAMS = dict(az=2.4305071427308924, el=80.67633718429899, a1=76.90180446920043, a2=66.74921235407174,
              wd=86.32769021001913, wa=21.829657347343378, sigma=-1, sing_deg=10.0, width=8.0, t_link=3.0,
              neck_deg=25.0, q=0.95)
BASELINE = dict(mode="outer", cont=False, collide=False)     # tools/concept_baseline.py conventions
HONEST = dict(mode="march", cont=True, collide=True)         # the kit's honesty rules (docs/concepts/KIT.md)


def ends(grid, n_end=None):
    """masks (flattened (ns, nc)) of the first / last n_end stations of a strap (baseline: max(2, ns // 6))"""
    ns, nc = grid; e = n_end or max(2, ns // 6); s = np.repeat(np.arange(ns), nc)
    return s < e, s >= ns - e


def build(B, F, p):
    # ---- kinematics: base axis b fixed in the scapula, last axis W fixed in the humerus (band frame), J2 by closure
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["sing_deg"])
    harm = F.HG(np.array([0.0, -1.0, 0.0]))                   # down the arm
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3), K.axis_angle(p3, harm, p2)], -1)

    # ---- members (baseline sampling: straps 2 mm at r_ref 70, cap hubs 2.5 mm; levels: link1 0, link2 up, neck 2 up)
    up = K.STACK + p["t_link"]; w = p["width"]; A1, A2 = p["a1"] * K.D2R, p["a2"] * K.D2R
    ng = p["neck_deg"] * K.D2R
    nk_v = K.unit(math.cos(ng) * p3 + math.sin(ng) * K.unit(harm - (harm * p3).sum(-1, keepdims=True) * p3))
    L1 = K.strap_dirs(p1, p2, A1, width=w); L2 = K.strap_dirs(p2, p3, A2, width=w); NK = K.strap_dirs(p3, nk_v, ng, width=w)
    flat = lambda D: D.reshape(len(D), -1, 3)
    hubs = [K.Member(f"hub{k + 1}", K.cap_dirs(ax), kind="cap", off=off, t=p["t_link"], width=20.0, joints=(f"J{k + 1}",), cell=6.25)
            for k, (ax, off) in enumerate(((p1, 0.0), (p2, 0.0), (p3, up)))]
    # ramps reproduce the baseline exactly: final link underside >= hub level + 2 * (link level - hub level)
    # (the baseline adds the link's stack offset twice at its hub ends - see docs/concepts/KIT.md "baseline quirks")
    links = []
    for nm, D, off, (h0, h1), J in (("link1", L1, 0.0, ("hub1", "hub2"), ("J1", "J2")), ("link2", L2, up, ("hub2", "hub3"), ("J2", "J3")),
                                    ("neck", NK, 2 * up, ("hub3", None), ("J3",))):
        lv = {"hub1": 0.0, "hub2": 0.0, "hub3": up}
        e0, e1 = ends(D.shape[1:3]); ramps = [(e0, h0, 2 * (off - lv[h0]))] + ([(e1, h1, 2 * (off - lv[h1]))] if h1 else [])
        links.append(K.Member(nm, flat(D), t=p["t_link"], width=w, off=off, joints=J, grid=D.shape[1:3], ramps=ramps, strap=True))
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3),
                   info=dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 4) if ok.any() else None))


if __name__ == "__main__":
    a = sys.argv[1:]
    nc = int(a[a.index("--n-clip") + 1]) if "--n-clip" in a else 60; nw = int(a[a.index("--n-ws") + 1]) if "--n-ws" in a else 160
    B = K.bench(nc, nw)
    for tag, kw in (("baseline conventions", BASELINE), ("honest kit checks", HONEST)):
        t = time.time(); r = K.evaluate(B, build, PARAMS, **kw)
        print(f"{tag}: {time.time() - t:.2f} s ({B.mode})", {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact",
                                                                                "closure", "flips", "collide", "mass_g", "inband_member")})
    if "--sweep" in a:                                       # the baseline's own sweep: the profile quantile
        best, rows = K.sweep(B, build, [dict(PARAMS, q=x) for x in (0.6, 0.7, 0.8, 0.9, 0.95, 1.0)],
                             os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json"), **BASELINE)
        print("BEST", best)

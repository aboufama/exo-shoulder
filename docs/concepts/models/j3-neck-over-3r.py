"""j3-neck-over-3r, screened in the j3-side-band lens (round 6, lens 3): the INVERTED J3 STACK on the knuckle chain.

Lead note (round 6): standalone, j3-neck-over-3r is a complexity-0 spherical 3R inside the verified zc ceiling (31.04;
the GPU search covered all four J2 / J3 stack orders), so it is screened ONLY as the J3 side of a knuckle chain, where
minarc variant A (plain spherical chain + spring knuckle K in link 1, complexity 13.5) loses the band on the J3 side
alone (link 2 0.43, hub 3 0.70 at F 101 mm, neck 0.68; hub 1 / K / hub 2 / link 1 0.93-1.00).

Chain (variant A kit rule, docs/concepts/models/minarc-stop-knuckle-4r-a-kitrule.py, loaded UNCHANGED as its own module
copy): scapula handler -> J1 (O20, active R through GH) -> link 1a -> K (O20, passive R, clock spring onto stop A, cap
+capK mm) -> link 1b -> J2 (O20, active R, physical q2 stop dowel in an arc slot) -> link 2 -> J3 (O20, active R,
humerus-fixed axis) -> member 3 (cap plate + K7 neck) -> BOTTOM. 0 passive translations, 1 passive rotation (K).

THE ONE CHANGE (lay 1, default): at hub 3, link 2 is the LOWER (face) member [F, F+3] and member 3 (arm plate + K7
neck) the UPPER (cap) member at F + STACK, its neck bridging >= 1 mm over link 2's swept zone (and over link 1a / 1b)
before it drops to BOTTOM. Variant A had link 2 as the upper member at hub 3 and asked it to pass >= 1 mm over the neck
everywhere (that `over` lifted link 2 to ~109 mm). Annulus-crossing law: link 2 rotates about J3 relative to the arm,
so the arm member leaving hub 3 crosses link 2's swept annulus unless it exits through a free sector; the stack order
decides which one pays. lay 0 = variant A's order (the control, same seats and metal).

Further J3-side levers searched together with the seats (all zero-cost, no part added): the J3 seat wd / wa (incl.
the deltoid-crest seats wd 80-100, wa -15..0), the underside quantile q, and the neck width nw (K7 14 x 6 -> 10 x 6
Ti, MVP1 only).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/j3-neck-over-3r.py check '<json params>'
    CB_EXACT=1 python3 docs/concepts/models/j3-neck-over-3r.py frozen '<json params>' <bench|held> out.json
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
"""
import importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

_sp = importlib.util.spec_from_file_location("minarc_a_kitrule_for_j3neck", os.path.join(HERE, "minarc-stop-knuckle-4r-a-kitrule.py"))
AK = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(AK)
KA, SP = AK.KA, AK.SP

ID = "j3-neck-over-3r"
NAME = "Inverted J3 stack (neck over link 2) on the spring-knuckle chain (minarc variant A kit rule)"
# start = variant A's kit-rule best LA1 (docs/concepts/verify/minarc-kitrule/params_A_LA1_g40_2.json)
LA1 = {"az": 100.6785, "el": 65.4034, "wd": 46.1583, "wa": -6.1871, "a1": 43.8793, "a2": 71.1868, "b1": 30.6983, "b2": 56.392,
       "a1max": 70.3202, "smhi": 6.0944, "smlo": 8.9158, "sK": -1, "sigma": -1, "q": 0.9694, "phys": 1, "capK": 6.0, "near": 1}
PARAMS = dict(AK.PARAMS, **LA1, lay=1, nw=14.0)
_ak_build = AK.build                                          # variant A's own build (lay 0 = the control)
REPORT_KEYS = AK.REPORT_KEYS


def build(B, F, p):
    """= the variant-A kit-rule build (hub K cap capK) with the J3 stack order chosen by p['lay']"""
    if not int(p.get("lay", 1)):
        return _ak_build(B, F, p)
    k = AK.kinematics(F, p); p1, p2, p3, pK, ok = k["p1"], k["p2"], k["p3"], k["pK"], k["ok"]
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), pK), k["psi"], K.axis_angle(p2, pK, p3), K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hubK", pK, "K", t=K.CROWN + float(p.get("capK", 0) or 0)),
            K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]; nw = float(min(14.0, max(10.0, float(p.get("nw", 14.0)))))
    links = [K.strap_member("link1a", p1, pK, ("J1", "K"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hubK", 0.0))),
             K.strap_member("link1b", pK, p2, ("K", "J2"), width=w, t=t, ramp_to=(("hubK", K.STACK + KA.KX), ("hub2", 0.0)),
                            over=[("link1a", 1.0)], end_mm=K.HUB_R + 6.0),
             # link 2: upper member at J2 (over link 1a / 1b as before), LOWER (face) member at J3, no longer over the neck
             K.strap_member("link2", p2, p3, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), ("hub3", 0.0)),
                            over=[("link1a", 1.0), ("link1b", 1.0)]),
             # member 3: cap plate at F + STACK, the K7 neck bridging >= 1 mm over link 2 (and link 1a / 1b) to BOTTOM
             K.strap_member("neck", p3, F.H(K.unit(K.BAR0_H)), ("J3",), width=nw, t=6.0, ramp_to=(("hub3", K.STACK),),
                            over=[("link2", 1.0), ("link1b", 1.0), ("link1a", 1.0)])]
    o = ok
    info = dict(residual_deg=round(float(k["res"][o].max()), 5) if o.any() else None,
                forced_share=round(float((k["state"][o] != 0).mean()), 4) if o.any() else None,
                stretched=int(((k["state"] == 1) & o).sum()), folded=int(((k["state"] == -1) & o).sum()),
                a1e_max=round(float(k["a1e"][o].max()), 2) if o.any() else None,
                psi_range=[round(float(np.abs(k["psi"][o]).min()), 1), round(float(np.abs(k["psi"][o]).max()), 1)] if o.any() else None,
                min_sub_margin=round(float(k["msub"][o & (k["state"] != 0)].min()), 2) if (o & (k["state"] != 0)).any() else None)
    return K.Chain(members=hubs + links, ok=ok, q=q, joints=dict(J1=p1, K=pK, J2=p2, J3=p3), info=info)


# KA.evaluate builds through KA.build; AK.frozen through AK.build: both point here
KA.build = build
AK.build = build


def evaluate(B, params):
    p = dict(PARAMS, **params); p["lay"] = 1 if float(p.get("lay", 1)) >= 0.5 else 0
    p["nw"] = float(min(14.0, max(10.0, float(p.get("nw", 14.0)))))
    p, r = AK.evaluate(B, p)
    r["lay"] = p["lay"]
    return p, r


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SP._jsonable(v)}


def frozen(p0, wear="bench", out=None):
    """AK.frozen (fit Bench(60,160) fast -> wear Bench(110,360) / held out, frozen profiles, continuity flood fill) on this build"""
    p = AK.stops(dict(PARAMS, **p0)); p["lay"] = 1 if float(p.get("lay", 1)) >= 0.5 else 0
    d = AK.frozen(p, wear, None)
    d["model"] = f"docs/concepts/models/{ID}.py"
    if out: json.dump(d, open(out, "w"), indent=1, default=float)
    return d


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        frozen(par, sys.argv[3] if len(sys.argv) > 3 else "bench", sys.argv[4] if len(sys.argv) > 4 else None); sys.exit()
    B = K.bench(60, 160); t = time.time(); p, r = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "collide")}, "plain", r["plain"],
          "kit", r.get("kitrule"), f"{time.time() - t:.1f}s")
    print("per member", r["inband_member"], "| min metal", r.get("min_metal_skin"), "| overhead", r.get("overhead"))
    print("info", {k: r.get(k) for k in ("residual_deg", "forced_share", "stretched", "folded", "a1e_max", "psi_range", "min_sub_margin")})
    print("near", r.get("near_low"))
    if mode == "redteam": KA.redteam(B, p, r)

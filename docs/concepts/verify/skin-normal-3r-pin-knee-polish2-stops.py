"""Independent verification of the skin-normal-3r-pin-knee POLISH 2 claim (C1 = H1-g69-4, 2026-10-16): the polish verifier
harness (docs/concepts/verify/skin-normal-3r-pin-knee-polish.py) and the continuity harness
(docs/concepts/verify/skin-normal-3r-pin-knee-continuity.py) imported UNCHANGED, plus the claimed design's J2 HARD STOPS
m_lo / m_hi (deg past the fold-window edges) - written here by the verifier, not taken from tools/knee_polish2.py:

  * the stop is applied on MK.Design.ik of the harness's own model instance. The J1-J3 angle is computed from the SOLVED
    joint chain (angle between the J1 axis u1 and the J3 axis carried by link 2, R12 u3: a function of q2 only), not
    from the arm orientation, and the pose is refused when it lies outside
    [|a1 - a2| + max(m_lo, rule), min(a1 + a2, 360 - a1 - a2) - max(m_hi, rule)]. The arm-orientation angle (Q u3 vs u1)
    is checked against it on the closed poses (max difference reported).
  * a stop can only narrow the window; the rule (CB_FOLD_MARGIN, 5) stays the floor.

Extra red-team numbers on top of the harness: the stop margins on the taken poses (low and high edge separately), the
knee's distance to its window edges overall and over the overhead poses (elev >= 140), the overhead clip follow, and
the part envelope of the claim (hubs, pin stack, knee link, E strap, knee window) against the catalogue bounds.

    OMP_NUM_THREADS=1 CB_EXACT=1 CB_FOLD_MARGIN=5 python3 docs/concepts/verify/skin-normal-3r-pin-knee-polish2-stops.py \
        claim <fit60|fitbig|held> <out.json> '<json params>'
    ... cont <kin|taken> <fitbig|fit60> <out.json> '<json params>'       (the continuity harness with the stops)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_DIFF = [0.0]


def _load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn)); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


def install(MK):
    """J2 hard stops on MK.Design.ik (verifier's own code; no-op without m_lo / m_hi in the params)"""
    if getattr(MK.Design, "_vstops", False): return
    orig = MK.Design.ik

    def ik(self, Q):
        q, ok, X1, X2, X3, s = orig(self, Q)
        if "m_lo" not in self.p and "m_hi" not in self.p: return q, ok, X1, X2, X3, s
        Q = np.asarray(Q)
        if not len(Q): return q, ok, X1, X2, X3, s
        rule = KIT.FOLD_MARGIN
        mlo = max(float(self.p.get("m_lo", rule)), rule); mhi = max(float(self.p.get("m_hi", rule)), rule)
        u1, u3 = np.asarray(self.u[0], float), np.asarray(self.u[2], float)
        R12 = X2[0]                                                            # link 2 rotation (home -> pose)
        th_chain = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", R12, u3) @ u1, -1, 1)))
        th_arm = np.degrees(np.arccos(np.clip((Q @ u3) @ u1, -1, 1)))
        if ok.any(): _DIFF[0] = max(_DIFF[0], float(np.abs(th_chain - th_arm)[ok].max()))
        a1, a2 = math.degrees(self.A[0]), math.degrees(self.A[1])
        lo, hi = abs(a1 - a2) + mlo, min(a1 + a2, 360 - a1 - a2) - mhi
        return q, ok & (th_chain >= lo) & (th_chain <= hi), X1, X2, X3, s
    MK.Design.ik = ik; MK.Design._vstops = True


def claim(proto, outp, P):
    H = _load("pin_knee_polish_h", "skin-normal-3r-pin-knee-polish.py"); install(H.MK)
    t0 = time.time()
    fitB = H.fast_bench(60, 160) if proto == "fit60" else H.fast_bench(110, 360)
    wearB = H.held_bench() if proto == "held" else CB.Bench(n_clip=110, n_ws=360)
    M, fit, M1 = H.frozen_on(fitB, wearB, P)
    r = M.run(); model = {k: r[k] for k in H.KEYS}
    ex, bad = H.V.extra_checks(M, wearB); res0 = list(wearB.res)
    for i in bad: wearB.res[i] = None
    rc = wearB.report(); corrected = {k: rc[k] for k in H.KEYS}
    aud = H.MK.audit(M, wearB); rt = H.redteam(M, wearB)
    tk = [i for i in range(len(wearB.idx)) if wearB.res[i] is not None and float(np.min(wearB.res[i])) >= 0]
    D = M.D; a1, a2 = math.degrees(D.A[0]), math.degrees(D.A[1]); lo0, hi0 = abs(a1 - a2), min(a1 + a2, 360 - a1 - a2)
    th = np.degrees(np.arccos(np.clip((M.Q[tk] @ D.u[2]) @ D.u[0], -1, 1))) if tk else np.array([np.nan])
    ang = M.K["ang"]; am = float(M.p["ang_min"])
    oh = [i for i in tk if wearB.poses[i]["elev"] >= 140]
    edge = lambda ii: round(float(np.minimum(ang[ii] - am, 180 - am - ang[ii]).min()), 2) if ii else None
    stops = dict(m_lo=P.get("m_lo"), m_hi=P.get("m_hi"), lo_margin_taken=round(float(th.min() - lo0), 2), hi_margin_taken=round(float(hi0 - th.max()), 2),
                 window=[round(lo0, 2), round(hi0, 2)], chain_vs_arm_angle_maxdiff_deg=round(_DIFF[0], 4))
    env = dict(hubs=list(M.hr), o20=all(abs(h - 10.0) < 1e-9 for h in M.hr), stk=float(M.p["stk"]), stk_in_catalogue_range=4.5 <= float(M.p["stk"]) <= 6.0,
               lc=float(M.p["lc"]), lc_ge_two_O12_bosses_plus_2=float(M.p["lc"]) >= 14.0, lE=float(M.p["lE"]), lE_in_20_90=20.0 <= float(M.p["lE"]) <= 90.0,
               ang_min=am, ang_min_ge_20=am >= 20.0, b1=M.p.get("b1"), b2=M.p.get("b2"), R_tol=M.p.get("R_tol"))
    wearB.res = res0
    o = aud["overhead140"]
    out = dict(protocol=proto, params=P, fit_mode=fitB.mode, wear_mode=wearB.mode, n_wear=len(wearB.idx), exact=os.environ.get("CB_EXACT") == "1",
               fold_margin_rule=KIT.FOLD_MARGIN, o20_only=KIT.O20_ONLY, fit=fit, model=model, extra=ex, bad_removed=len(bad), corrected=corrected,
               gap_near1=aud["gap_near1"], near1_poses=aud["near1_poses"], min_metal_mm=aud["near_touch_min_mm"], overhead140=o,
               knee_edge_all_deg=edge(tk), knee_edge_overhead_deg=edge(oh), stops=stops, envelope=env, corrected_audit=aud, redteam=rt,
               secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(protocol=proto, fit=fitB.mode, wear=wearB.mode, n=len(wearB.idx), margin=KIT.FOLD_MARGIN, corrected=corrected,
                          near1=aud["gap_near1"], near1_poses=aud["near1_poses"], min_mm=aud["near_touch_min_mm"], overhead=dict(follow=o["follow"], reach=o["reach"], clip=o["clip"]),
                          knee_edge_oh=out["knee_edge_overhead_deg"], knee_edge_all=out["knee_edge_all_deg"], stops=stops, envelope=env, bad=len(bad),
                          fold_min_taken=rt["fold_margin_min_taken_deg"], knee_ang_taken=rt["knee_ang_taken"], j1_seat=rt["j1_seat"], why=rt["why"],
                          secs=out["secs"]), default=float), flush=True)


def cont(args):
    C = _load("pin_knee_cont_h", "skin-normal-3r-pin-knee-continuity.py"); install(C.MK)
    sys.argv = [sys.argv[0]] + args; C.main()
    print(json.dumps(dict(chain_vs_arm_angle_maxdiff_deg=round(_DIFF[0], 4))), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "claim": claim(a[1], a[2], json.loads(a[3]))
    elif a and a[0] == "cont": cont(a[1:])
    else: raise SystemExit(__doc__)

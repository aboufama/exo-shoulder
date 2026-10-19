"""Independent verifier (skeptic) of sidecar-longdyad-knuckle-3r (the lead's slaved knuckle with a strap-level RSSR
sidecar drive: hub-2 rim lobe -> bell crank on link 1b -> O3 rod + 2 M2 ball links -> horn lug of link 1a at hub K;
link 1b lengthened to bk2 39.2).

The claim's model (docs/concepts/models/sidecar-longdyad-knuckle-3r.py) is loaded UNCHANGED (its law, clamps, pin knee,
stops, the drive-range truncation and every check stay as claimed). The protocol is the claim's frozen one (fit on
Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact), reproduced here so the worn model is in hand. Checks
ADDED by this harness on every TAKEN pose of the worn bench (they are not in the claim):

  1. RSSR CLOSURE IN THE WORLD: the rod (member 8) must meet the horn ball (member 1, link 1a) and the crank tip ball
     (member 9) in each pose: |T1 H0 - T8 H0| and |T9 tip0 - T8 tip0| < 0.5 mm (the bench's closure tolerance).
  2. BALL-LINK TILT: an M2 ball link swivels about +-30 deg off the plane normal to its stud (the rule the
     acromial-rocker-3r screen used): tilt = asin(|rod . stud axis|) at the crank tip (stud axis R9 dR) and at the horn
     (stud axis R1 uK) must stay <= 30 deg; a pose past it is lost ('balllink').
  3. REAL LOBE PRESSURE ANGLE: the lobe is cut to the exact RSSR phi(dK), so its lift is s_arm |phi|; the real
     pressure angle atan(s_arm |dphi/ddK| dK/dq2 / r) over the taken range must stay <= 45 deg (the law's gate used the
     small-angle ratio r_h / La).
  4. CONTINUITY FLOOD FILL (connected_report of docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py, unchanged).

    CB_EXACT=1 python3 docs/concepts/verify/sidecar-longdyad-knuckle-3r.py wear <bench|held> <out.json> [--flood]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


SC = _load("sidecar_claim_v", os.path.join(REPO, "docs", "concepts", "models", "sidecar-longdyad-knuckle-3r.py"))
S, PK = SC.S, SC.PK
unit = S.unit
BEST = {"bk1": 28.9414, "bk2": 39.236, "a1max": 63.1774, "law_mode": "lin", "kK": 1.6232, "r_h": 14.8706, "beta": -86.447,
        "La": 16.5467, "s_arm": 4.3872, "hl": 3.15, "zr": 0.0, "r_lobe": 7.7447, "gam": 0.0, "smhi": 16.5464, "smlo": 5.0,
        "az1": 96.6954, "el1": 67.5865, "az2": 42.2031, "el2": 44.4209, "wd": 67.5003, "wa": -7.3175, "b3": 0.345,
        "ang_min": 26.8823, "lc": 25.6915, "phib": -60.7036}
TILT_MAX, PA_MAX, CLOSE_TOL = 30.0, 45.0, 0.5


def extra_checks(M, B):
    g = M._scg; H0, tip0, dR, uK = g["H0"], g["tip0"], g["dR"], g["uK"]
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    eh, et, tc, th_, bad = [], [], [], [], []
    for i in taken:
        R1, t1 = M.T(1, i); R8, t8 = M.T(8, i); R9, t9 = M.T(9, i)
        hw, rh = R1 @ H0 + t1, R8 @ H0 + t8; tw, rt = R9 @ tip0 + t9, R8 @ tip0 + t8
        eh.append(float(np.linalg.norm(hw - rh))); et.append(float(np.linalg.norm(tw - rt)))
        rd = unit(rh - rt)
        a_c = math.degrees(math.asin(min(1.0, abs(float(rd @ (R9 @ dR)))))); a_h = math.degrees(math.asin(min(1.0, abs(float(rd @ (R1 @ uK))))))
        tc.append(a_c); th_.append(a_h)
        if a_c > TILT_MAX or a_h > TILT_MAX or eh[-1] > CLOSE_TOL or et[-1] > CLOSE_TOL: bad.append(i)
    # real lobe pressure angle over the taken range (lin law: |dK| = kK t, so d|dK|/dq2 = kK)
    P = M.D.p; kg, pg = g["kgrid"], g["phig"]; ratio = np.gradient(pg, kg) if len(kg) > 2 else np.ones(len(kg))
    dKp = np.abs(np.asarray(M.dK, float)); kmax = float(dKp[taken].max()) if taken else 0.0; jt = int(np.searchsorted(kg, kmax)) + 1
    kK = float(P.get("kA", P.get("kK", 0.0))); s_arm = float(P["s_arm"]); rl0 = float(P["r_lobe"])
    r_t = rl0 + s_arm * np.abs(pg[:jt]); pa = np.degrees(np.arctan(s_arm * np.abs(ratio[:jt]) * kK / r_t))
    out = dict(n_taken=len(taken), closure_horn_max_mm=round(max(eh), 4) if eh else None, closure_tip_max_mm=round(max(et), 4) if et else None,
               tilt_crank_max=round(max(tc), 1) if tc else None, tilt_horn_max=round(max(th_), 1) if th_ else None,
               tilt_crank_p95=round(float(np.percentile(tc, 95)), 1) if tc else None, tilt_horn_p95=round(float(np.percentile(th_, 95)), 1) if th_ else None,
               poses_failing=len(bad), poses_failing_ids=bad[:50], pa_real_max=round(float(pa.max()), 2) if len(pa) else None,
               ratio_over_small=[round(float(np.abs(ratio[:jt]).min() * float(P["La"]) / float(P["r_h"])), 3),
                                 round(float(np.abs(ratio[:jt]).max() * float(P["La"]) / float(P["r_h"])), 3)],
               dK_taken_max_deg=round(math.degrees(kmax), 2), dK_lim_deg=round(math.degrees(g.get("dK_lim", 0.0)), 2), why_lim=g.get("why_lim"))
    # corrected report: poses failing the added checks counted as lost (not taken)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    out["corrected"] = {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    B.res = res0
    return out


def frozen_wear(P, wear="bench", flood=False):
    P = SC._clamp(dict(SC.PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = SC.SCModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    fit["extra"] = extra_checks(M1, B1)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(SC.SCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if wear == "held":
        PV = _load("pk_polish_v_sidecar_v", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = PK.audit(M, B)
    ex = extra_checks(M, B)
    th = np.asarray(M.th, float) if hasattr(M, "th") else None
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, n=len(B.idx), why=r.get("why"), parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               audit=aud, extra=ex, sidecar=getattr(M1, "_sc_info", None), min_clear_taken=r.get("min_clear_taken"))
    if flood:
        MECH = _load("minarc_mech_for_sidecar_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = frozen_wear(dict(BEST), wear, "--flood" in sys.argv)
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(wear=wear, fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"), near2=out["audit"].get("gap_near2"),
                              minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"), why=out["why"], extra=out["extra"],
                              conn=out.get("connected"), secs=out["secs"]), default=float))

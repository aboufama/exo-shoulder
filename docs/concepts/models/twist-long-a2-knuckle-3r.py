"""twist-long-a2-knuckle-3r: the verified lead frontload-lobe-stopb-knuckle-3r (knuckle K slaved by the hub-2 rim lobe ->
rocker -> O3 rod -> horn on K's cap, pin knee, O20 stacks, kit fold rule, near-touch objective, the verifier's corrected
cap metal) with the J3 seat RE-CENTRED for reach and the K dyad widened on the bk2 side. No new joint or component type.

THE LEVER (round 8, window geometry). The fold window of the J2 dyad is [|a1A - a2| + 5, a1max + a2 - 5] in th =
angle(J1 axis, J3 axis); axial rotation sweeps th over about +-wd_eff around angle(J1, humerus). Turning the J3 axis
anterior about the humerus (wa > 0) and lengthening a2 moves the overhead axial -135 family off the stretched wall.

PARAMETRISATION (the designer's variables, so CMA moves along the lever):
  * J3 effective axis: e3d / e3a = the J3 axis direction in the humerus frame (wdir(d, a): d from the down-the-arm
    axis, a 0 lateral, +90 anterior). With b3 = 0 the hub sits on that ray (wd = e3d, wa = e3a). With b3 > 0 (axis
    tilted toward the skin normal, line misses GH) the seat ray wd / wa is solved so the TILTED axis equals the effective
    one (fixed-point on the rest skin normal, reported as wd_eff_err). Without e3d the lead's wd / wa / b3 stand.
  * J2 seat from a1t (J1-J2 angle at K stop A) and a2t: d2 = circ_int(u1, a1t, d3_rest, a2t, s) on the branch nearest
    the lead's J2 seat; az2 / el2 derived (b2 = 0, J2 on a GH ray as every knuckle). Without a2t the lead's az2 / el2 stand.
  * K dyad: bk1 ~30, bk2 widened, a1max <= bk1 + bk2 - 5 (the lead's clamp).
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/twist-long-a2-knuckle-3r.py [check] ['<json>']
    ... gate '<json>'    the law-only kill gate (drive metal off): kinematic reach of the model's own IK on Bench(110,360)
    CB_EXACT=1 ... frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("frontload_for_twist", os.path.join(HERE, "frontload-lobe-stopb-knuckle-3r.py"))
F = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(F)
S, PK, KB = F.S, F.PK, F.KB
OSN = PK.OSN
unit = S.unit; D2R = math.pi / 180
ID = "twist-long-a2-knuckle-3r"

LEAD = {"bk1": 30.0536, "bk2": 37.5707, "a1max": 61.7215, "smhi": 14.7672, "smlo": 5.1723, "az1": 95.3594, "el1": 67.6187, "az2": 42.7487, "el2": 43.9031, "wd": 63.5262, "wa": -10.5604, "b3": 0.3825, "ang_min": 27.8606, "r_horn": 2.4709, "r_lobe": 7.3499, "kA": 2.9004, "t1": 6.9414, "kB": 2.7564, "i_rock": 1.0, "law_mode": "seg", "emb_mode": "rod", "capK": 6.0, "tail": 1, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "crown_rule": 1}   # rows/frontload-lobe-stopb-knuckle-3r.json best_params (the verified lead)
PARAMS = dict(F.PARAMS, **LEAD)
# seed A (reach-first): effective J3 wdir(70, 15), a2 66, bk1 30 / bk2 44 / a1max 69, seg law to t_end 100
SEED_A = dict(e3d=70.0, e3a=15.0, b3=0.0, a1t=36.12, a2t=66.0, bk1=30.0, bk2=44.0, a1max=69.0, t_end=100.0)
SEED_B = dict(e3d=88.0, e3a=30.0, b3=0.0, a1t=36.12, a2t=58.0, bk1=30.0, bk2=44.0, a1max=69.0, t_end=100.0)


def wdir(d, a):
    d, a = d * D2R, a * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def wang(v):
    v = unit(v); return math.degrees(math.acos(max(-1, min(1, -v[1])))), math.degrees(math.atan2(v[0], v[2]))


def seats(p):
    """the designer's variables -> the lead's seat parameters (wd, wa, az2, el2); in place, returns info"""
    info = {}
    R = OSN.rest(); Q0 = R["Q0"]
    b3 = float(p.get("b3", 0.0))
    if p.get("e3d") is not None:
        td, ta = float(p["e3d"]), float(p["e3a"])
        wd, wa = td, ta
        if b3 > 1e-6:
            for _ in range(12):
                d3 = OSN.seat(Q0 @ S.w_dir(wd, wa), b3)[1]; ed, ea = wang(Q0.T @ d3)
                if abs(ed - td) < 0.02 and abs(ea - ta) < 0.02: break
                wd += td - ed; wa += ta - ea
            d3 = OSN.seat(Q0 @ S.w_dir(wd, wa), b3)[1]; ed, ea = wang(Q0.T @ d3)
            info["e3_err"] = round(math.hypot(ed - td, ea - ta), 3)
        p["wd"], p["wa"] = float(wd), float(wa)
    if p.get("a2t") is not None:
        u1 = S.bvec(p["az1"], p["el1"])
        d3 = OSN.seat(Q0 @ S.w_dir(p["wd"], p["wa"]), b3)[1]
        ref = S.bvec(LEAD["az2"], LEAD["el2"]); best = None
        for sg in (1.0, -1.0):
            try: d2 = unit(S.circ_int(u1, float(p["a1t"]) * D2R, d3, float(p["a2t"]) * D2R, sg))
            except Exception: continue
            if not np.all(np.isfinite(d2)): continue
            if best is None or d2 @ ref > best @ ref: best = d2
        if best is None:
            info["seat_fail"] = True
        else:
            p["el2"] = math.degrees(math.asin(max(-1, min(1, best[1])))); p["az2"] = math.degrees(math.atan2(best[2], -best[0]))
    return info


def prep(params):
    p = dict(PARAMS, **params); p["b3"] = min(max(float(p.get("b3", 0.0)), 0.0), 0.6)   # tilt toward the skin normal: 0..0.6
    info = seats(p); p = F._clamp(p); return p, info


def _report(B, params):
    p, info = prep(params)
    r, M = F._report(B, p)
    if info.get("seat_fail"): r["honest"] = False; r["gap"] = 275.0
    D = M.D
    r["seat"] = dict(info, wd=round(p["wd"], 3), wa=round(p["wa"], 3), az2=round(p["az2"], 3), el2=round(p["el2"], 3),
                     a1=round(D.a1, 2), a2=round(D.a2, 2), e3=[round(x, 2) for x in wang(D.u[2])])
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def gate(params, tail=0):
    """the law-only kill gate: fit on Bench(60,160) fast with the drive metal OFF (tail 0), then the fitted design's own
    IK (law + K + knee + |s_n| <= R_tol) on every Bench(110,360) workspace pose: kinematic reach and overhead per axial
    family, fold cause per lost pose by wall; and the fast-bench parking (per-part in-band, reach, why)"""
    p, info = prep(dict(params, tail=tail))
    B1 = CB.Bench(n_clip=60, n_ws=160)
    r1, M1 = F._report(B1, p); D = M1.D
    old = os.environ.get("CB_EXACT")
    Z = CB._poses_all()
    B3 = CB.Bench.__new__(CB.Bench) if False else None
    B3 = CB.Bench(n_clip=110, n_ws=360)
    k = np.array(B3.kind); ws = k == "ws"; Q = Z["HG"][B3.idx].astype(float)
    q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s)
    kin = ok & Kn["ok"] & (np.abs(s[:, 2]) <= float(D.p["R_tol"]))
    th = np.degrees(np.arccos(np.clip((Q @ D.u[2]) @ D.u[0], -1, 1)))
    elev = np.array([B3.poses[i]["elev"] for i in range(len(B3.idx))]); ax = np.array([B3.poses[i]["axial"] for i in range(len(B3.idx))])
    ov = ws & (elev >= 140)
    fam = {}
    for a0 in sorted(set(np.round(ax[ov]).astype(int))):
        m = ov & (np.round(ax) == a0); fam[int(a0)] = f"{int(kin[m].sum())}/{int(m.sum())}"
    a1A, a2 = D.a1, D.a2; amax = float(D.p["a1max"])
    lost = ws & ~kin
    walls = dict(folded=int((lost & (th < abs(a1A - a2) + 5)).sum()), stretched=int((lost & (th > amax + a2 - 5)).sum()),
                 law_or_m3e=int((lost & ~ok & (th >= abs(a1A - a2) + 5) & (th <= amax + a2 - 5)).sum()),
                 knee=int((lost & ok & ~(Kn["ok"] & (np.abs(s[:, 2]) <= float(D.p["R_tol"])))).sum()))
    L_ = D.law()
    return dict(kin360=round(float(kin[ws].mean()), 4), ov360=f"{int(kin[ov].sum())}/{int(ov.sum())}", ov_fam=fam, walls=walls,
                th_ws=[round(float(np.percentile(th[ws], q_)), 1) for q_ in (5, 50, 95)], a1=round(a1A, 2), a2=round(a2, 2),
                window=[round(abs(a1A - a2) + 5, 1), round(amax + a2 - 5, 1)],
                law=dict(why_end=L_.get("why_end"), dK_max=round(L_.get("dK_max", 0), 1), th_max=L_.get("th_max"), k_max=L_.get("k_max"),
                         m3e_min=L_.get("m3e_min")),
                fast=dict(gap=r1["gap"], near1=r1.get("gap_near1"), reach=r1["reach"], inband14=r1["inband14"], contact=r1["contact"],
                          why=r1.get("why"), ovh=(r1.get("overhead140") or {}).get("reach"), parts=r1.get("parts_ib14")),
                seat=dict(info, wd=round(p["wd"], 2), wa=round(p["wa"], 2), az2=round(p["az2"], 2), el2=round(p["el2"], 2),
                          e3=[round(x, 2) for x in wang(D.u[2])]))


def frozen(P, nc=110, nw=360):
    p, _ = prep(P); return F.frozen(p, nc, nw)


def frozen_held(P):
    p, _ = prep(P); return F.frozen_held(p)


def frozen_flood(P):
    p, _ = prep(P); return F.frozen_flood(p)


def viz_export(par):
    p, _ = prep(par); return F.viz_export(p)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "gate":
        t = time.time(); out = gate(par, tail=int(par.get("tail", 0))); out["secs"] = round(time.time() - t, 1)
        print(json.dumps(out, default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              minmetal=a.get("near_touch_min_mm"), ovh=a.get("overhead140"), parts=out.get("parts_ib14"),
                              connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"), reach=r["reach"],
                          inband14=r["inband14"], contact=r["contact"], why=r.get("why"), ovh=r.get("overhead140"), drive=r.get("drive"),
                          parts=r.get("parts_ib14"), seat=r.get("seat"), honest=r.get("honest"), secs=round(time.time() - t)), default=float))

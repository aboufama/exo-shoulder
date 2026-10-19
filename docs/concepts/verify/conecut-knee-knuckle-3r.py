"""Independent verifier (skeptic) of conecut-knee-knuckle-3r (the verified lead slipper-nose-knuckle-3r, SN_CELL=lead, with
its two-pin knee re-proportioned - lE 97.14, lc 24.35, phiE 0.75, phib -91.80, MR63ZZ stk 6.0 - and a J3 hard stop on
q3' = q3 + phi in [J3MIN, J3MAX] built as a 2 mm 440C dowel in hub 3's lower plate at r 7.5 in an arc groove under link 2).

The claim's model (docs/concepts/models/conecut-knee-knuckle-3r.py) is loaded UNCHANGED and worn through its own frozen
protocol (CC._frozen_model: fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360) exact / held out). This
harness adds the lead's verifier checks (docs/concepts/verify/slipper-nose-knuckle-3r.py extra_checks: cam closure in the
world, nose vs lug, K sense, pressure angles with friction at 43 and 45, real lobe PA, drive-idle, own-state th margin,
conjugate undercut / relative pole) retargeted at the claim's class, and ADDS for this claim:

  C1. THE STOP ACTS ON J3's OWN ANGLE: per closing pose, the relative rotation link 2 -> member 3 from the model's own
      member transforms (R2^T R3) must be a pure rotation about J3's axis u3 (axis residual), and its signed angle must
      equal the claim's q3' = q3 + phi up to one constant offset (spread of the difference) - else the stop bounds a
      virtual angle (CLAUDE.md: never a virtual angle between non-adjacent bodies).
  C2. STOP BUILDABILITY: groove arc = (J3MAX - J3MIN) + the dowel's own angular width at r 7.5 must leave a web in link 2's
      ring; the min q3' margin to each stop over the taken poses (bench and held), and the number of fit-clip frames cut.
  C3. WHAT THE STOP CUTS: the stopped poses re-evaluated with the stop removed on the SAME frozen shape (metal and
      contact of each stopped pose; a stop that only removes contact poses relabels them - legal for a real stop, but
      reported), and the knee/hub-axis checks they would otherwise fail.
  C4. IN-BAND ATTRIBUTION: the frozen in-band re-weighted with the E strap at the lead's strap sample count (the longer
      strap is real metal, but the point-weighted in-band share rises with any in-band metal added) and the chain-only
      in-band (hubs, links, drive), next to the plain number.
  C5. KNEE / CUFF PLACEMENT: the distance down the humerus of hub 3, pin a (E boss) and pin b (arm pad) at rest, for this
      claim and the lead (the pad must sit on the upper-arm cuff).
  plus the continuity flood (connected_report, unchanged) and the per-pose dump in tools/alignment_paired.py's format.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/conecut-knee-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--dump PATH] [--set k=v ...]
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/conecut-knee-knuckle-3r.py place          (C5, fast bench)
"""
import importlib.util, json, math, os, sys, time, types
import numpy as np

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


VS = _load("slipper_verifier_for_conecut_v", os.path.join(HERE, "slipper-nose-knuckle-3r.py"))         # the lead's verifier
H, LV = VS.H, VS.LV
CC = _load("conecut_claim_v", os.path.join(REPO, "docs", "concepts", "models", "conecut-knee-knuckle-3r.py"))   # loaded LAST
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "slipper-nose-knuckle-3r.json")))["best_params"]


def wr(a): return (a + 180.0) % 360.0 - 180.0


def retarget(P):
    nr = float(CC._clamp(dict(CC.PARAMS, **P))["nose_r"])
    H.RF = types.SimpleNamespace(phi_of=CC.RF.phi_of, dphi_of=CC.RF.dphi_of, ROLL_R=nr, _ring=CC.RF._ring,
                                 RFModel=CC.CCModel, _clamp=CC._clamp, PARAMS=CC.PARAMS)
    H.SC, H.S, H.PK = CC.SC, CC.S, CC.PK
    H.ROLL_R = nr; H.BEST = dict(P)
    return nr


def rot_axis_angle(R):
    c = (np.trace(R) - 1) / 2; a = math.acos(max(-1.0, min(1.0, c)))
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    n = np.linalg.norm(v)
    return (v / n if n > 1e-12 else np.array([0.0, 0.0, 1.0])), a


def c1_own_angle(M, B):
    """C1: R2^T R3 is a rotation about u3 by q3' (+ const)"""
    u3 = np.asarray(M.D.u[2], float); q3p = wr(np.degrees(M.q[:, 2] + M.K["phi"]))
    idx = [i for i in range(len(B.idx)) if bool(M.kin_ok[i]) or M.why[i] == "j3stop"]
    res, diff = [], []
    for i in idx:
        R2, _ = M.T(2, i); R3, _ = M.T(3, i); Rr = R2.T @ R3
        ax, a = rot_axis_angle(Rr)
        s = float(np.sign(ax @ u3)) or 1.0
        # residual: the part of Rr that is not a rotation about u3 (angle between Rr u3 and u3)
        res.append(math.degrees(math.acos(max(-1.0, min(1.0, float((Rr @ u3) @ u3))))))
        diff.append(wr(math.degrees(s * a) - float(q3p[i])))
    diff = np.array(diff); res = np.array(res)
    off = float(np.median(diff)) if len(diff) else 0.0
    return dict(n=len(idx), axis_residual_max_deg=round(float(res.max()), 4) if len(res) else None,
                offset_deg=round(off, 3), spread_max_deg=round(float(np.abs(wr(diff - off)).max()), 4) if len(diff) else None)


def c2_stop(M, B, P):
    lo, hi = float(P["J3MIN"]), float(P["J3MAX"]); r = float(CC.DOWEL_R)
    w = 2 * math.degrees(math.asin(1.05 / r))                  # O2.1 groove over a O2 dowel at r 7.5
    taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    q3p = wr(np.degrees(M.q[:, 2] + M.K["phi"]))
    arc = (hi - lo) + w if hi < 180 else None
    return dict(J3MIN=lo, J3MAX=hi, dowel_width_deg=round(w, 2), groove_arc_deg=None if arc is None else round(arc, 2),
                web_deg=None if arc is None else round(360 - arc, 2),
                q3p_taken=[round(float(q3p[taken].min()), 2), round(float(q3p[taken].max()), 2)] if taken.any() else None,
                margin_lo=round(float(q3p[taken].min() - lo), 2) if taken.any() else None,
                margin_hi=round(float(hi - q3p[taken].max()), 2) if (taken.any() and hi < 180) else None,
                n_stopped=int((np.asarray(M.why) == "j3stop").sum()))


def c3_stopped(M, B):
    """the stopped poses evaluated on the SAME worn shape as if the stop were absent: part clearance (collide), min metal-skin
    distance of the bench metal and of the contact walls (exact path when CB_EXACT=1); the run's state is left untouched"""
    st = [i for i in range(len(B.idx)) if M.why[i] == "j3stop"]
    out = []
    for i in st:
        row = dict(i=i, kind=B.kind[i], pose=[B.poses[i][k] for k in ("plane", "elev", "axial")])
        try:
            cl = float(M.collide(i)); row["part_clear_mm"] = round(cl, 2); row["pair"] = str(min(M.last_clear, key=M.last_clear.get))
        except Exception as e: row["collide_err"] = repr(e)[:120]
        try:
            d = np.asarray(B.dist(i, M.metal_points(i)), float); row["metal_min_mm"] = round(float(d.min()), 2)
            dc = min(float(np.min(B.dist(i, M.world(m, i, Pc)))) for m, Pc in M.contact); row["wall_min_mm"] = round(dc, 2)
        except Exception as e: row["metal_err"] = repr(e)[:120]
        out.append(row)
    return dict(n=len(st), poses=out)


def c4_inband(r, P):
    pi = r.get("parts_ib14") or {}
    if not pi: return {}
    tot = sum(v[2] for v in pi.values()); inb = sum(v[0] * v[2] for v in pi.values())
    nE = pi["E"][2]; fE = pi["E"][0]
    # the strap's sample count scales with its sampled length (r3 + 1 .. lE - BOSS_R + 0.5); the lead's at its own lE
    BR, r3 = 6.0, 10.0                                        # pin-knee BOSS_R, O20 hub radius
    def length(lE): return max(0.0, (lE - BR + 0.5) - (r3 + 1.0))
    w = length(float(LEAD["lE"])) / max(1e-9, length(float(P["lE"])))
    nE2 = nE * w
    ib_eq = (inb - fE * nE * (1 - w)) / (tot - nE * (1 - w))
    chain = [k for k in pi if k not in ("E", "boss", "pad", "knee")]
    ib_chain = sum(pi[k][0] * pi[k][2] for k in chain) / sum(pi[k][2] for k in chain)
    return dict(plain_from_parts=round(inb / tot, 4), E_pts=nE, E_pts_at_lead_lE=round(nE2, 1), w=round(w, 3),
                ib14_equal_strap=round(ib_eq, 4), ib14_chain_only=round(ib_chain, 4),
                gap_equal_strap=round(r["gap"] - 100 * max(0, .90 - r["inband14"]) + 100 * max(0, .90 - ib_eq), 2))


def wear(P, which="bench", flood=False, dump=None):
    nc, nw = (110, 360) if which == "bench" else (-1, -1)
    fit, M1, M, B, r = CC._frozen_model(dict(P), nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = CC.PK.audit(M, B)
    ex = VS.extra_checks(M, M1, B)
    Pc = CC._clamp(dict(CC.PARAMS, **P))
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ov = ws & (elev >= 140)
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, n=len(B.idx), why=r.get("why"), parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               audit=aud, extra=ex, overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())),
               knee=CC.knee_report(M, B, taken=np.isfinite(mins) & (mins >= 0)),
               contacts=[dict(i=int(j), kind=B.kind[j], elev=B.poses[j]["elev"], plane=B.poses[j]["plane"], axial=B.poses[j]["axial"], mm=round(float(mins[j]), 2))
                         for j in range(len(B.idx)) if not np.isnan(mins[j]) and mins[j] < 0])
    for nm, fn in (("c1_own_angle", lambda: c1_own_angle(M, B)), ("c2_stop", lambda: c2_stop(M, B, Pc)), ("c4_inband", lambda: c4_inband(r, Pc))):
        try: out[nm] = fn()
        except Exception as e: out[nm] = dict(error=repr(e)[:300])
    if dump:
        AP = _load("ap_for_conecut_v", os.path.join(REPO, "tools", "alignment_paired.py"))
        poses = AP._dump_bench(M, B)
        json.dump(dict(id=CC.ID, wear=which, params=P, frozen=rep, report=B.report(), poses=poses,
                       recomputed=AP.gap_parts(poses), exact=os.environ.get("CB_EXACT") == "1", note="written by docs/concepts/verify/conecut-knee-knuckle-3r.py"),
                  open(dump, "w"), default=float)
        out["dump"] = dict(path=dump, recomputed=AP.gap_parts(poses))
    if flood:
        MECH = _load("minarc_mech_for_conecut_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    try: out["c3_stopped"] = c3_stopped(M, B)          # last: it re-runs the worn model
    except Exception as e: out["c3_stopped"] = dict(error=repr(e)[:300])
    return out


def place():
    """C5 on the fast fit bench: distance down the humerus axis of hub 3, pin a, pin b (rest = the model's home frame)"""
    old = os.environ.pop("CB_EXACT", None); B = CB.Bench(n_clip=60, n_ws=160)
    out = {}
    for nm, P in (("conecut", dict(BEST)), ("lead", {k: LEAD[k] for k in ("lE", "phiE", "lc", "phib")} | dict(stk=CC.SN.PARAMS.get("stk", 4.85), J3MIN=-180.0, J3MAX=999.0))):
        p = CC._clamp(dict(CC.PARAMS, **P)); M = CC.CCModel(B, dict(p)); D = M.D; K = M.K
        A0 = D.p3(K["A0"])[0]; Bm = D.p3(K["B2"])[0]; c3 = D.c[2]
        h = getattr(D, "h0", None)
        if h is None: h = np.array([0.0, -1.0, 0.0])
        h = np.asarray(h, float) / np.linalg.norm(h)
        out[nm] = dict(lE=p["lE"], lc=p["lc"], stk=p.get("stk"), hub3_down=round(float(c3 @ h), 1), pinA_down=round(float(A0 @ h), 1),
                       pinB_pad_down=round(float(Bm @ h), 1), hub3_r=round(float(np.linalg.norm(c3)), 1), pad_r=round(float(np.linalg.norm(Bm)), 1),
                       h0=[round(float(x), 3) for x in h])
    return out


if __name__ == "__main__":
    P = dict(BEST)
    for i_, a_ in enumerate(sys.argv):
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_)
    retarget(P)
    if sys.argv[1] == "place":
        print(json.dumps(place(), default=float)); sys.exit()
    if sys.argv[1] == "wear":
        which, path = sys.argv[2], sys.argv[3]
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        t = time.time(); out = wear(P, which, "--flood" in sys.argv, dump)
        out.update(wear=which, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=P)
        json.dump(out, open(path, "w"), indent=1, default=float)
        e = out["extra"]
        print(json.dumps(dict(wear=which, fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=out["audit"].get("gap_near1"),
                              minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["overhead"], contacts=out["contacts"], knee=out["knee"],
                              c1=out.get("c1_own_angle"), c2=out.get("c2_stop"), c3=out.get("c3_stopped"), c4=out.get("c4_inband"),
                              extra={k: e.get(k) for k in ("n_taken", "closure_max_mm", "poses_failing", "why_failing", "corrected", "th_margin", "wrong_sense",
                                                           "dK_taken_max_deg", "dK_lim_deg", "pa_rule", "at_pa45_friction", "nose")},
                              conn={k: v for k, v in (out.get("connected") or {}).items() if k != "static"}, dump=out.get("dump"), secs=out["secs"]), default=float))

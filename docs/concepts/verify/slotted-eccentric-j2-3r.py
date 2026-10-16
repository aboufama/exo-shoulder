"""Adversarial verifier for slotted-eccentric-j2-3r (2026-10-16). Re-measures one configuration with the model's own
frozen-shape protocol (fit on Bench(60,160) FAST, every underside / post frozen, worn on Bench(110,360); CB_EXACT=1 for
the exact path; K6 at 1 mm radial) plus the verifier's corrections:

  * K6 shared-joint exemption sized to the REAL joint: the kit exempts samples within HUB_R + 2 = 12 mm of a shared
    joint axis (sized for an O20 hub); at the O10 MR63ZZ knee K only rpin + 2 = 7 mm, at the O7 roller stud G
    3.5 + 2 = 5.5 mm is the bearing's own zone. Applied in the fit (`over` lifts) and in the check.
  * independent rigid-body closure per pose (not the closed forms the model solves with): link 1 {J1, J2}, crank
    {J2, K}, link 2b {K, J3, G} keep their axis angles (and 2b its handedness) within 0.5 deg of the synthetic rest
    configuration, and the roller G, expressed in link 1's polar frame about J2, lies on the slot centreline (the exact
    locus, densely sampled) within 0.3 mm at R_NOM; a pose that fails is not taken.
  * per taken pose: the slot lock angle (internal four-bar mode vs slot tangent) recomputed at the pose itself, and the
    G-K-J2 alignment angle (the singular set) - reported; a pose with lock < 20 deg is not taken (it would back-drive).
  * joint travel over the taken poses (q1, q2, q3, knee, roller azimuth).

    CB_EXACT=1 python3 docs/concepts/verify/slotted-eccentric-j2-3r.py <out.json> '<json params>' [--own] [--lock]
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_spec = importlib.util.spec_from_file_location("slot_model", os.path.join(REPO, "docs", "concepts", "models", "slotted-eccentric-j2-3r.py"))
MD = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(MD)
K = MD.K
STATE = dict(rpin=5.0, clo_max=0.0, n_bad=0, slot_dev_max=0.0, lock_min=None, align_min=None, n_lock_bad=0)
EXEMPT = dict(K=None, G=3.5 + 2.0)


def _near_real(A, Bm, da, db, xa, xb, joints, shared, P, clear):
    """K._near with the shared-joint exemption radius of the REAL joint (knee rpin + 2, stud 5.5, hubs HUB_R + 2)"""
    ma = np.ones(xa.shape, bool); mb = np.ones(xb.shape, bool); sa, sb = K._scale(A, xa), K._scale(Bm, xb)
    for j in shared:
        rj = (STATE["rpin"] + 2.0) if j == "K" else (EXEMPT["G"] if j == "G" else K.HUB_R + 2.0)
        k = K.unit(joints[j][P])
        ma &= np.arccos(np.clip(np.einsum("pmd,pd->pm", da, k), -1, 1)) * xa / sa > rj
        mb &= np.arccos(np.clip(np.einsum("pmd,pd->pm", db, k), -1, 1)) * xb / sb > rj
    ha, hb = A.hw * sa, Bm.hw * sb
    ca, cb = K.unit(da.mean(1)), K.unit(db.mean(1))
    ra = np.arccos(np.clip(np.einsum("pmd,pd->pm", da, ca).min(1), -1, 1)); rb = np.arccos(np.clip(np.einsum("pmd,pd->pm", db, cb).min(1), -1, 1))
    sep = np.arccos(np.clip((ca * cb).sum(-1), -1, 1))
    reach = (ha.max(1) + hb.max(1) + clear) / np.minimum(xa.min(1), xb.min(1))
    k = np.nonzero((sep <= ra + rb + reach + 1e-6) & ma.any(1) & mb.any(1))[0]
    if not len(k): return None
    dot = np.matmul(da[k].astype(np.float32), db[k].astype(np.float32).transpose(0, 2, 1))
    thr = ha[k] + hb[k].max(1)[:, None] + clear
    cmin = (1.0 - 0.5 * (thr / xa[k]) ** 2).astype(np.float32)
    near = (dot > cmin[:, :, None]) & mb[k][:, None, :]
    near &= ma[k][:, :, None]
    return k, near


_BUILD = MD.build
_SD = MD.slot_design
ROLLER_OD, SLOT_FIT, WALL = 5.0, 0.05, 1.95     # MR52ZZ 2 x 5 x 2.5: the slot must take the 5 mm roller, not the 2 mm dowel


def slot_design_real(p):
    """the model's slot with the track widened to the REAL roller: slot = MR52ZZ OD 5 + H7 fit (the model: 2.6 mm,
    i.e. the 2 mm dowel's slot) between 1.95 mm walls -> track width + 2.45 mm"""
    sd = _SD(p)
    if sd.get("passed") and "track" in sd and not sd.get("_real"):
        sd = dict(sd); tr = dict(sd["track"]); tr["width"] = round(tr["width"] + (ROLLER_OD + SLOT_FIT - 2.6), 2)
        sd["track"] = tr; sd["_real"] = True
    return sd


def _slot_curve(p, sd):
    """exact slot centreline in link 1's polar frame about J2 (planar mm at R_NOM), densely sampled over the track run"""
    th, p1, p3, G = MD._synthetic(p)
    lo, hi = sd["track"]["th_track"] if "th_track" in sd["track"] else (sd["lo"], sd["hi"])
    s = (th >= lo - 1e-9) & (th <= hi + 1e-9) & G["ok"]
    P1, P3, P2, KK = p1[s], p3[s], G["p2"][s], G["K"][s]; n = int(s.sum())
    Gw = MD.from_polar(KK, P3, np.full(n, sd["dG"]), np.full(n, sd["gG"]))
    e, eta = MD.ang(P2, Gw), K.axis_angle(P2, P1, Gw)
    rest = dict(a1=float(MD.ang(P1[0:1], P2[0:1])[0]), b=float(MD.ang(P2[0:1], KK[0:1])[0]), c=float(MD.ang(KK[0:1], P3[0:1])[0]),
                kg=float(MD.ang(KK[0:1], Gw[0:1])[0]), jg=float(MD.ang(P3[0:1], Gw[0:1])[0]),
                hand=float(np.sign(np.dot(np.cross(KK[0], P3[0]), Gw[0]))))
    return MD._xy(e, np.unwrap(eta * MD.D2R) / MD.D2R), rest


def build_checked(B, F, p):
    ch = _BUILD(B, F, p)
    if p.get("lock"): return ch
    sd = MD.slot_design(p)
    if not sd.get("passed"): return ch
    S, rest = _slot_curve(p, sd)
    J = {k: K.unit(np.asarray(v, float)) for k, v in ch.joints.items()}
    err = np.abs(MD.ang(J["J1"], J["J2"]) - rest["a1"])
    err = np.maximum(err, np.abs(MD.ang(J["J2"], J["K"]) - rest["b"]))
    err = np.maximum(err, np.abs(MD.ang(J["K"], J["J3"]) - rest["c"]))
    err = np.maximum(err, np.abs(MD.ang(J["K"], J["G"]) - rest["kg"]))
    err = np.maximum(err, np.abs(MD.ang(J["J3"], J["G"]) - rest["jg"]))
    hand = np.sign(np.einsum("pd,pd->p", np.cross(J["K"], J["J3"]), J["G"]))
    err = np.where(hand == rest["hand"], err, 180.0)
    e, eta = MD.ang(J["J2"], J["G"]), K.axis_angle(J["J2"], J["J1"], J["G"])
    eta_u = eta.copy()
    XY = MD._xy(e, eta_u)
    # distance to the dense slot curve (try eta +- 360 for unwrap ambiguity)
    best = np.full(len(e), np.inf)
    for sh in (-360.0, 0.0, 360.0):
        XYs = MD._xy(e, eta_u + sh)
        d = np.min(np.stack([MD._seg_dist(XYs, S[i], S[i + 1]) for i in range(len(S) - 1)], 0), 0); best = np.minimum(best, d)
    ok = np.asarray(ch.ok, bool)
    # lock at the pose itself (the internal four-bar mode at fixed J1, J3)
    dn = 0.05; p1, p2, p3, Kw = J["J1"], J["J2"], J["J3"], J["K"]
    p2a = MD._turn(p1, p2, dn); p2b = MD._turn(p1, p2, -dn); n = len(e)
    bc = (np.full(n, float(p["b"])), np.full(n, float(p["c"])))
    ka = MD.closure_v(p2a, p3, *bc, p["sk"])[0]; kb = MD.closure_v(p2b, p3, *bc, p["sk"])[0]
    Ga = MD.from_polar(ka, p3, np.full(n, sd["dG"]), np.full(n, sd["gG"])); Gb = MD.from_polar(kb, p3, np.full(n, sd["dG"]), np.full(n, sd["gG"]))
    vi = (MD._xy(MD.ang(p2a, Ga), K.axis_angle(p2a, p1, Ga)) - MD._xy(MD.ang(p2b, Gb), K.axis_angle(p2b, p1, Gb))) / (2 * dn)
    # slot tangent at the nearest dense point
    idx = np.linalg.norm(XY[:, None, :] - S[None, :, :], axis=-1).argmin(1)
    Tg = np.gradient(S, axis=0)[idx]; Tg /= np.maximum(np.linalg.norm(Tg, axis=-1, keepdims=True), 1e-9)
    cr = np.abs(vi[:, 0] * Tg[:, 1] - vi[:, 1] * Tg[:, 0]); lock = np.degrees(np.arcsin(np.clip(cr / np.maximum(np.linalg.norm(vi, axis=-1), 1e-9), 0, 1)))
    al = MD.ang(MD.tangent(Kw, p2), MD.tangent(Kw, J["G"])); al = np.minimum(al, 180 - al)
    good = (err < 0.5) & (best < 0.3) & (lock >= 20.0)
    if ok.any():
        STATE["clo_max"] = max(STATE["clo_max"], float(err[ok].max())); STATE["slot_dev_max"] = max(STATE["slot_dev_max"], float(best[ok].max()))
        STATE["lock_min"] = round(float(lock[ok].min()), 2); STATE["align_min"] = round(float(al[ok].min()), 2)
    STATE["n_bad"] = int((ok & ~((err < 0.5) & (best < 0.3))).sum()); STATE["n_lock_bad"] = int((ok & (lock < 20.0)).sum())
    ch.ok = ok & good
    ch.info["verifier"] = dict(closure_max_deg=round(STATE["clo_max"], 4), slot_dev_max_mm=round(STATE["slot_dev_max"], 4),
                               lock_min_deg=STATE["lock_min"], align_min_deg=STATE["align_min"], closure_bad=STATE["n_bad"],
                               lock_bad=STATE["n_lock_bad"])
    return ch


def travel(B):
    L = B._kit_last; ch, take = L["chain"], L["take"]
    if ch.q is None or not take.any(): return {}
    q = np.asarray(ch.q)[take]; names = ("q1", "q2", "q3", "knee", "e_roller", "eta_roller")
    return {n: round(float(np.degrees(np.ptp(np.unwrap(np.radians(q[:, j]))))), 1) for j, n in enumerate(names[:q.shape[1]])}


if __name__ == "__main__":
    out = sys.argv[1]; par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    own = "--own" in sys.argv
    if "--lock" in sys.argv: par["lock"] = 1
    STATE["rpin"] = float(par.get("rpin", MD.PARAMS["rpin"]))
    if not own:
        K._near = _near_real
        MD.build = build_checked
        MD.slot_design = slot_design_real
    p0 = dict(MD.PARAMS, **par)
    res = MD.frozen(p0, out)
    res["verifier"] = dict(own_checks_only=own, exempt_knee_mm=None if own else STATE["rpin"] + 2.0, exempt_stud_mm=None if own else EXEMPT["G"],
                           exempt_hub_mm=K.HUB_R + 2.0, closure_max_deg=round(STATE["clo_max"], 4), slot_dev_max_mm=round(STATE["slot_dev_max"], 4),
                           lock_min_deg_taken=STATE["lock_min"], align_min_deg_taken=STATE["align_min"], closure_bad_last=STATE["n_bad"],
                           lock_bad_last=STATE["n_lock_bad"], fold_margin_param=p0["margin"], kit_fold_margin=K.FOLD_MARGIN, o20_only=K.O20_ONLY)
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("verifier", res["verifier"], flush=True)

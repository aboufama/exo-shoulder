"""slowpole-slot-knuckle-3r (round 501, G1 golden, lens B): the verified lead conecut-knee-knuckle-3r (seats, a2, b3, knee,
J3 dowel stop, O20 stacks, part pairs, near-touch rules loaded UNCHANGED) with its K dyad re-seated to a symmetric long dyad
(bk1 = bk2 = 40, sK -1: the lead's side), a SLOW law (rho = dK / d(-q2) = 0.5, onset th ~57.2, stroke ~30.3 deg) and its
two-stage drive (lobe, bell crank, nose, clock spring, stop-A pin) replaced by ONE crowned pin on hub 2's rotor ring running
in a form-closed dwell-and-rise slot on a link-1a plate.

Built on docs/concepts/models/shortk-onetooth-knuckle-3r.py (dyad re-seat restored after the lead's chain clamp, the law
anchored on the lead's END STATE a1e 54.27 at th 106.3 on exact spherical kinematics, the ghost cell of
onetooth-slowlaw-knuckle-3r: every drive part deleted). This file changes:

  (1) rho floor 0.40 (the parent clamps rho >= 0.5; the spec scans 0.45).
  (2) DKLIM: the drive's own range = the law's end K + DKPAD (spec: stroke 30.3 + 0.7 = 31.0) unless WALL is set: the slot's
      rise ends there (form closure), so the stretched wall is the slot end, not the lead's stop B.
  (3) SMHI_FIX (optional): the spec's typed onset ((a1 + a2) - 57.2 = 37.57); default = the exact law_for() onset, and the
      two are compared in `law` mode (the spec's closed form uses the same anchor, so they must agree to < 0.5 deg).
  (4) `slot` mode (STEP 1): the slot locus in LINK 1a's frame, c(q2) = R(uK, -dK(q2)) R(u2, q2) p0, per 0.05 deg of q2:
      pressure angle (pin velocity relative to the plate vs the wall normal; the pin is on link 2's rotor so its velocity
      relative to link 1a has a component along the slot, which is the sliding direction), wall curvature radius (no
      undercut: >= the pin radius 1.25 mm), the PA span over which the rise can drive K, and the plate's travel.

DOF: 3 ACTIVE (J1, J2, J3 encoded), K slaved (passive R, determined by the slot both ways: form-closed, no spring), knee pins
outside the count, 0 passive translations. No gears / pulleys / cables (MVP1).

    OT_CELL=ghost OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/slowpole-slot-knuckle-3r.py [check] ['<json>']
    ... wear <envsel|bench|held> '<json>' [out.json]      ... law '<json>'      ... slot '<json>' '<slot kw json>'
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("OT_CELL", "ghost")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
_sp = importlib.util.spec_from_file_location("shortk_for_slowpole", os.path.join(HERE, "shortk-onetooth-knuckle-3r.py"))
SK = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SK)
OT, CC, SN, SC, FL, S, CB = SK.OT, SK.CC, SK.SN, SK.SC, SK.FL, SK.S, SK.CB
ID = "slowpole-slot-knuckle-3r"
PARAMS = dict(SK.LEADP); PARAMS.update(bk1=40.0, bk2=40.0, rho=0.5, WALL="slot", DKPAD=0.7)


def _clamp(p):
    b1 = min(max(float(p.get("bk1", 40.0)), 20.0), 50.0); b2 = min(max(float(p.get("bk2", 40.0)), 20.0), 50.0)
    rho = min(max(float(p.get("rho", 0.5)), 0.4), 4.0); wall = str(p.get("WALL", "slot")); pad = float(p.get("DKPAD", 0.7))
    p = CC._clamp(p)                                         # the lead's chain clamp (clamps bk1 / bk2 to an old box: restored below)
    p["bk1"], p["bk2"], p["rho"], p["WALL"], p["DKPAD"] = b1, b2, rho, wall, pad
    L = SK.law_for(dict(p, WALL="lead" if wall == "slot" else wall))
    p["kK"] = p["kA"] = p["kB"] = rho
    p["smhi"] = round(L["smhi"], 6) if not float(p.get("SMHI_FIX", 0) or 0) else float(p["SMHI_FIX"])
    p["DKLIM"] = round(L["k_end"] + pad, 6) if wall == "slot" else round(L["DKLIM"], 6)
    p["DKLIM"] = min(p["DKLIM"], SK._geo(b1, b2)["k_at"](b1 + b2 - 5.0))      # never past K's own dyad fold margin
    p["a1max"] = min(float(p.get("a1max", 58.7678)), b1 + b2 - 5.0)
    p["t_end"] = max(float(p.get("t_end", 75.0)), p["DKLIM"] / rho + 2.0)
    G = SK._geo(b1, b2); a1w = float(G["a1e"](p["DKLIM"])[0])
    p["kdyad_ok"] = int((abs(b1 - b2) + 5.0 <= G["a1"] + 1e-9) and (a1w <= b1 + b2 - 5.0 + 1e-9))
    return p


SK._clamp = _clamp; OT._clamp = _clamp; SC._clamp = _clamp; SK.PARAMS = PARAMS; OT.PARAMS = PARAMS


def law_report(P):
    """the law in closed form on the exact kinematics: onset, stroke, K at th 78, msub along the stroke, the spec's typed onset"""
    P = _clamp(dict(PARAMS, **P)); b1, b2, rho = P["bk1"], P["bk2"], P["rho"]
    L = SK.law_for(dict(P, WALL="lead")); G = SK._geo(b1, b2); an = SK.anchor()
    D = G["D"]; u1, u2, u3 = D.u; uK = D.uK
    s_q = an["s_q"]; q2on = math.radians(L["q2_on"])
    ts = np.radians(np.linspace(0.0, L["k_end"] / rho, 301)); ks = np.degrees(rho * ts)
    q2s = q2on + s_q * ts; ths = np.array([G["th"](q, k)[0] for q, k in zip(q2s, ks)])
    spn = float(np.sign(D.psiA)) or 1.0
    # J1-K-J3 sub-dyad: arcs bk1 (u1-uK) and cK (uK - u3 in link 1b / link 2), margin = min(th - |bk1 - cK|, bk1 + cK - th)
    cK = np.array([math.degrees(math.acos(np.clip(float(uK @ (S.rotm(u2, q)[0] @ u3)), -1, 1))) for q in q2s])
    msub = np.minimum(ths - np.abs(b1 - cK), b1 + cK - ths)
    i78 = int(np.argmin(np.abs(ths - 78.0)))
    s12 = min(G["a1"] + G["a2"], 360 - G["a1"] - G["a2"])
    return dict(bk=[b1, b2], rho=rho, th_on=round(L["th_on"], 3), smhi=round(L["smhi"], 3), smhi_spec_typed=round(s12 - 57.2, 3),
                k_end=round(L["k_end"], 3), dq2=round(math.degrees(ts[-1]), 2), th_end=round(float(ths[-1]), 2), a1e_end=round(L["a1e_end"], 3),
                K_at_th78=round(float(ks[i78]), 2), msub_min=round(float(msub.min()), 2), msub_at=round(float(ths[int(np.argmin(msub))]), 2),
                th_monotone=bool(np.all(np.diff(ths) > 0)), DKLIM=P["DKLIM"], a1=round(G["a1"], 3), a2=round(G["a2"], 3),
                kdyad_ok=P["kdyad_ok"], uK_vs_lead_deg=round(math.degrees(math.acos(np.clip(float(uK @ SK._geo(*SK.LEAD_DYAD)["D"].uK), -1, 1))), 2))


def slot(P=None, r_p=13.5, ph=17.0, dwell=60.0, dq=0.05, mu=0.087, R_mm=61.0, pin_r=1.25):
    """STEP 1: the slot locus in link 1a's frame and its gates (exact spherical kinematics, all axes through GH).
    Frames (the model's _ik_phys / G["th"]): a point fixed in link 2 is, in link 1a's frame, c = R(uK, sp K) R(u2, q2) p0
    (sp = sign psiA; K = |dK| = rho t past the onset, t = s_q (q2 - q2_on)); in link 1b's frame cb = R(u2, q2) p0. The pin
    sits on hub 2's rotor ring (link 2) at r_p mm from u2 (sphere R_mm), phase ph deg about u2 off the u2 -> uK arc AT THE
    STROKE END. The slot is the pin's path in link 1a's frame: DWELL (K = 0, `dwell` deg of q2 before the onset) = an arc
    about u2; RISE = the conjugate path. In link 1b's frame (the common ground of K and J2) the plate point at the pin moves
    v1 = (dK/dq2) d/dK[R(uK, -sp K)] = -sp rho (uK x cb) and the wall normal is n_1b = R(uK, -sp K) n_1a (n_1a: normal of the
    locus, tangent to the sphere). Drive PA (rise) = angle(n_1b, v1): the slot wall pushes the plate along n. Dwell LOCK
    angle = angle(n, uK x cb) over the dwell: a K torque on the plate is reacted by the wall unless this nears 90 (then the
    plate slides along its own slot: K unlocked). Undercut: geodesic curvature radius of the locus >= pin_r. Relative pole:
    min |v_pin - v_plate| over the rise (the locus cusps there; lantern-gear rule)."""
    P = _clamp(dict(PARAMS, **(P or {}))); b1, b2, rho = P["bk1"], P["bk2"], P["rho"]
    L = SK.law_for(dict(P, WALL="lead")); G = SK._geo(b1, b2); an = SK.anchor(); D = G["D"]
    u1, u2, u3 = D.u; uK = D.uK; sp = float(np.sign(D.psiA)) or 1.0; s_q = an["s_q"]
    e = S.unit(np.cross(u2, np.cross(uK, u2))); f = np.cross(u2, e)
    t = r_p / R_mm; kend = math.radians(L["k_end"])
    q2e = math.radians(L["q2_end"]); q2on = math.radians(L["q2_on"])
    pe = math.cos(t) * u2 + math.sin(t) * (math.cos(math.radians(ph)) * e + math.sin(math.radians(ph)) * f)
    p0 = S.rotm(u2, -q2e)[0] @ pe                             # the pin in link 2's frame (link 1b's frame at q2 = 0)
    q2s = q2on + s_q * np.radians(np.arange(-dwell, math.degrees(q2e - q2on) * s_q + 1e-9, dq))
    tt = s_q * (q2s - q2on); K = np.clip(rho * tt, 0.0, kend)
    rise = tt > 1e-9; dKdq = np.where(rise, rho, 0.0)
    cb = np.einsum("nij,j->ni", S.rotm(u2, q2s), p0)          # pin, link 1b frame
    c = np.einsum("nij,nj->ni", S.rotm(uK, sp * K), cb)       # pin, link 1a frame: the slot locus
    tg = np.gradient(c, axis=0); tgn = np.linalg.norm(tg, axis=1); tgu = tg / np.maximum(tgn, 1e-15)[:, None]
    n1a = np.cross(c, tgu); n1b = np.einsum("nij,nj->ni", S.rotm(uK, -sp * K), n1a)
    vK = np.cross(uK, cb)                                     # plate velocity per unit K (direction), link 1b frame
    def ang(nv, v): return np.degrees(np.arccos(np.clip(np.abs(np.einsum("ij,ij->i", nv, v)) / np.maximum(np.linalg.norm(v, axis=1), 1e-15), 0, 1)))
    pa = ang(n1b, vK)
    vpin = s_q * np.cross(u2, cb); vpl = -sp * dKdq[:, None] * vK; vrel = np.linalg.norm(vpin - vpl, axis=1) * R_mm   # mm / rad of q2
    gate = SN.pa_kin(mu)
    d2 = np.gradient(tg, axis=0)
    kg = np.abs(np.einsum("ij,ij->i", c, np.cross(tg, d2))) / np.maximum(tgn ** 3, 1e-30); rc = R_mm / np.maximum(kg, 1e-12)
    ri = np.nonzero(rise)[0]; di = np.nonzero(~rise)[0]
    pa_r = pa[ri]; ok = pa_r <= gate
    span = float(np.sum(ok) * dq)
    run = 0; best = 0
    for o in ok:
        run = run + 1 if o else 0; best = max(best, run)
    h2 = np.einsum("nij,j->ni", S.rotm(uK, sp * K), u2)
    return dict(r_p=r_p, ph=ph, rho=rho, gate=round(gate, 2), dq2_rise=round(len(ri) * dq, 2), k_end=round(L["k_end"], 2),
                pa_rise=[round(float(pa_r.min()), 1), round(float(np.median(pa_r)), 1), round(float(pa_r.max()), 1)],
                pa_rise_at_onset=round(float(pa_r[0]), 1), pa_rise_at_end=round(float(pa_r[-1]), 1),
                pa_span_q2=round(span, 2), pa_longest_run_q2=round(best * dq, 2), pa_frac=round(float(ok.mean()), 3),
                dwell_lock=[round(float(pa[di].min()), 1), round(float(pa[di].max()), 1)],
                rc_min_rise_mm=round(float(rc[ri][3:-3].min()), 3), undercut=bool(rc[ri][3:-3].min() < pin_r),
                vrel_min_mm_per_deg=round(float(vrel[ri].min()) * math.pi / 180, 4),
                slot_len_rise_mm=round(float(np.sum(np.linalg.norm(np.diff(c[ri], axis=0), axis=1)) * R_mm), 2),
                hub2_travel_1a_mm=round(float(np.linalg.norm(h2[ri][-1] - h2[ri][0]) * R_mm), 2),
                pin_r_deg=round(math.degrees(t), 2),
                pin_from_uK_deg=[round(float(np.degrees(np.arccos(np.clip(cb[ri] @ uK, -1, 1))).min()), 2), round(float(np.degrees(np.arccos(np.clip(cb[ri] @ uK, -1, 1))).max()), 2)])


def wear(P, bench="envsel"):
    out, M, B = SK.wear(dict(PARAMS, **P), bench)
    out["id"] = ID; out["law_slowpole"] = law_report(P)
    taken = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
    try:
        th = np.degrees(np.asarray(M.th, float)) if hasattr(M, "th") else None
        if th is not None: out["th_margin_min_taken"] = round(float(np.min(np.minimum(th, 180 - th)[taken])), 3)
    except Exception as e: out["th_margin_err"] = str(e)[:80]
    return out, M, B


def bench_eval(B, params):
    r, M = OT._report(B, dict(PARAMS, **params)); r.pop("params", None); return r


def evaluate(B, params):
    r, M = OT._report(B, dict(PARAMS, **params))
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def viz_export(par): return CC.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[3] if mode == "wear" and len(sys.argv) > 3 else (sys.argv[2] if len(sys.argv) > 2 and mode != "wear" else "{}"))
    if mode == "wear":
        bench = sys.argv[2]; t = time.time(); out, M, B = wear(par, bench); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 4: json.dump(out, open(sys.argv[4], "w"), indent=1, default=float)
        print(json.dumps({k: out.get(k) for k in ("cell", "bench", "fit_fast", "frozen", "why", "near1", "near2", "min_metal", "ws_taken", "n_ws", "ws_contact",
                                                   "overhead", "K_open", "law_slowpole", "kdyad_margin_min_taken", "th_margin_min_taken", "contact_poses", "secs")}, default=float))
        sys.exit()
    if mode == "law":
        print(json.dumps(law_report(par), default=float)); sys.exit()
    if mode == "slot":
        kw = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        print(json.dumps(slot(par, **kw), default=float)); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = OT._report(B, dict(PARAMS, **par))
    print(json.dumps(dict(cell=OT.CELL, gap=r["gap"], near1=r.get("gap_near1"), near2=r.get("gap_near2"), reach=r["reach"], follow=r["follow"],
                          inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"), why=r.get("why"), ovh=r.get("overhead140"),
                          law=r.get("law"), secs=round(time.time() - t, 1)), default=float))

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


def slot(P=None, r_p=13.5, ph=17.0, dq=0.05, mu=0.087, R_mm=61.0, pin_r=1.25):
    """STEP 1: the slot locus in link 1a's frame and its gates. The pin sits on hub 2's rotor ring (link 2) at r_p mm from u2,
    phase ph deg off the u2 -> uK arc (measured at the stroke end, about u2). Over the dwell (K = 0) its path in link 1a's
    frame is an arc about u2; over the rise (K = rho t) the path is c(q2) = R(uK, -sp K) R(u2, q2) p0 (link 1b frame -> link 1a).
    Pressure angle: the plate (link 1a) is driven: the force on the plate acts along the slot-wall normal n at the pin; the
    plate's velocity there for unit q2 is v_a = (dK/dq2) * (-sp uK x c); PA = angle(n, v_a). The pin's own velocity along
    the slot (the sliding speed) is reported too. Undercut: the locus' geodesic curvature radius >= pin_r."""
    P = _clamp(dict(PARAMS, **(P or {}))); b1, b2, rho = P["bk1"], P["bk2"], P["rho"]
    L = SK.law_for(dict(P, WALL="lead")); G = SK._geo(b1, b2); an = SK.anchor(); D = G["D"]
    u1, u2, u3 = D.u; uK = D.uK; sp = float(np.sign(D.psiA)) or 1.0; s_q = an["s_q"]
    e = S.unit(np.cross(u2, np.cross(uK, u2))); f = np.cross(u2, e)
    t = r_p / R_mm
    # pin position in LINK 2 at the stroke end (q2 = q2_end): phase ph off the u2->uK arc; carry it back to q2 = 0 in link 2
    q2e = math.radians(L["q2_end"]); q2on = math.radians(L["q2_on"])
    pe = math.cos(t) * u2 + math.sin(t) * (math.cos(math.radians(ph)) * e + math.sin(math.radians(ph)) * f)
    p0 = S.rotm(u2, -q2e)[0] @ pe                                # pin in link 2's own frame (link 1b frame at q2 = 0)
    # q2 from 60 deg before the onset (dwell) to the end + 2 deg
    q2s = np.radians(np.arange(math.degrees(q2on) - s_q * 60.0, math.degrees(q2e) + s_q * 2.0, s_q * dq))
    tt = s_q * (q2s - q2on); K = np.clip(rho * tt, 0.0, math.radians(L["k_end"]))
    dKdq = np.where((tt > 0) & (K < math.radians(L["k_end"])), rho, 0.0)
    cb = np.einsum("nij,j->ni", S.rotm(u2, q2s), p0)           # pin in link 1b's frame
    c = np.einsum("nij,nj->ni", S.rotm(uK, -sp * K), cb)       # pin in link 1a's frame (the slot locus)
    tg = np.gradient(c, axis=0); tgn = np.linalg.norm(tg, axis=1); tgu = tg / np.maximum(tgn, 1e-15)[:, None]
    n = np.cross(c, tgu)                                       # wall normal (tangent to the sphere, normal to the locus)
    va = dKdq[:, None] * (-sp * np.cross(uK, cb))              # plate point velocity (link 1b frame ~ link 1a frame up to R(uK))
    va = np.einsum("nij,nj->ni", S.rotm(uK, -sp * K), va)      # into link 1a's frame
    vn = np.linalg.norm(va, axis=1)
    pa = np.degrees(np.arccos(np.clip(np.abs(np.einsum("ij,ij->i", n, va)) / np.maximum(vn, 1e-15), 0, 1)))
    gate = SN.pa_kin(mu)
    rise = dKdq > 0
    # geodesic curvature radius of the locus (mm): kappa_g = |c . (c' x c'')| / |c'|^3
    d2 = np.gradient(tg, axis=0)
    kg = np.abs(np.einsum("ij,ij->i", c, np.cross(tg, d2))) / np.maximum(tgn ** 3, 1e-30)
    rc = R_mm / np.maximum(kg, 1e-12)
    pa_ok = pa[rise] <= gate
    span = float(np.degrees(np.sum(pa_ok) * math.radians(dq)))
    first_fail = float(np.degrees(tt[rise][int(np.argmin(pa_ok))])) if not pa_ok.all() else None
    travel = float(np.linalg.norm(c[rise][-1] - c[rise][0]) * R_mm) if rise.any() else 0.0
    # hub 2's centre on the skin-side sphere in link 1a's frame (how far the plate must reach)
    h2 = np.einsum("nij,j->ni", S.rotm(uK, -sp * K), u2)
    h2_travel = float(np.linalg.norm(h2[rise][-1] - h2[rise][0]) * R_mm) if rise.any() else 0.0
    return dict(r_p=r_p, ph=ph, rho=rho, gate=round(gate, 2), dq2_rise=round(float(np.degrees(np.sum(rise) * math.radians(dq))), 2),
                pa_rise_max=round(float(pa[rise].max()), 2) if rise.any() else None, pa_rise_min=round(float(pa[rise].min()), 2) if rise.any() else None,
                pa_span_q2=round(span, 2), pa_first_fail_t=first_fail, rc_min_rise_mm=round(float(rc[rise][2:-2].min()), 3) if rise.sum() > 5 else None,
                undercut=bool(rise.sum() > 5 and rc[rise][2:-2].min() < pin_r), slot_travel_mm=round(travel, 2), hub2_travel_mm=round(h2_travel, 2),
                pin_from_uK_end_deg=round(math.degrees(math.acos(np.clip(float(pe @ uK), -1, 1))), 2))


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

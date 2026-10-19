"""lowarm-kstop-knuckle-3r (round 15, lens B, pick 1): lowarm-halfring-knuckle-3r cell A's verified chain with stage 1 at the
buildable level F+3.9 (glev 2.039, pin a_s 9.8 / psi 150), the link-1b dwell pad DELETED, and the dwell held by
  * the stage-1 groove's INNER wall (blocks +K, the rise side; checked here: rho(K) of the pin about u2 at the dwell exit), and
  * K's OWN stop A inside hub K's O20 stack (an integral 1.3 x 1.6 lug on link 1a's lower plate in a 2.1-wide arc groove
    under link 1b's boss, r 6.45-8.55, F_K+3.15..4.75; the groove's K = 0 end is an M1.6 flat-point set screw on the groove
    tangent, set at assembly; its far end is K-own stop B at 46.6),
  * a link-1b J2 lower-plate pocket where the crank's short arm passes (r 6.3-10 about u2, floor F+1.0), and the gen-9 CAD's
    J2 low-end dowel re-phased to engage at K-eq 46.35 (the slot is cut to 46.9; poses needing K > 46.35 are NOT taken).
3 ACTIVE DOF (J1, J2, J3); K slaved (never read); crank pivot + knee pins passive rotations; 0 passive translations; no
spring / gear / pulley / cable (MVP1).

HARNESS (no new kinematics): tools/alignment_lowarm_s1level.py (T) loads the row's verifier (V), which loads the claim's model
(LM, cell A) and desmo-conecut (DC) UNCHANGED; T re-applies glev after the model's clamp, so stage 1 sits at F+3.9.
The sided dwell play is worn with the kplay red team's PlayDesign (docs/concepts/models/lowarm-halfring-knuckle-3r-kplay.py),
its class source exec'd verbatim into THIS process's module chain (glev hook active): every DWELL pose (dK = 0) gets
K = law + delta, J1 / J2 / J3 re-solve, every body moves; forced poses keep the law value.

SPEC CORRECTION: the catalogue's "P = dict(V.BEST) | LM.CELL_A | ..." keeps V.BEST's l2_lift 1.5 (cell B's lifted link 2),
because CELL_A has no l2_lift key. Cell A (the verified F+3.9 wear, 18.65) has l2_lift 0. P here = CELL_A | KSTOP, l2_lift 0.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lowarm-kstop-knuckle-3r.py geom <out.json>
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/lowarm-kstop-knuckle-3r.py wear <delta_deg> <bench|held> <out.json> [--dump PATH] [--set k=v]
    python3 docs/concepts/models/lowarm-kstop-knuckle-3r.py combine <dumpA.json> <dumpB.json> [...]   (per-pose worst + probes)
"""
import importlib.util, json, math, os, re, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
ID = "lowarm-kstop-knuckle-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


AP = _load("ap_for_kstop", os.path.join(REPO, "tools", "alignment_paired.py"))
GLEV = 2.039
KSTOP = dict(a_s=9.8, psi=150.0, glev=GLEV, kslot=46.9, l2_lift=0.0)
DOWEL_K, STOPB_K, LIM0 = 46.35, 46.6, 47.0
# stop A (hub K frame: r about uK, z over hub K's face FK)
LUG_R, GRV_R, GRV_Z = (6.85, 8.15), (6.45, 8.55), (3.15, 4.75)
MR117_OD_R, M16_MAJOR_R, SCREW_R = 5.5, 0.8, 7.5
# sided hold budget (round-15 judge, catalogue model_spec step 4)
K_PER_MM = 16.485                                   # deg of K per mm of wall-normal motion at the stage-1 pin (cell A, measured)
C10_RATE = 0.40                                     # mm of 203 clearance lost per deg of +K (c10 ring, linear to +0.9)
P203_0 = 0.263
CORNERS = {"P5": (0.005, 0.003), "P0": (0.015, 0.005)}
STATICS = {"worst": 0.158, "RSS": 0.075, "matched": 0.049}
RES = {"P5": 0.005, "P0": 0.005}                    # stop-A set residual (mm at r 7.5); the judge's e- 0.210 (P5) uses 0.005
SLOT = 0.04


def budget():
    """sided dwell play e+ (wall side, statics + half the J2 runout + conc) and e- (stop A range: runout + conc + set residual)"""
    out = {}
    for cn, (kea, conc) in CORNERS.items():
        e_minus = (kea + conc) * K_PER_MM + math.degrees(RES[cn] / SCREW_R) + SLOT
        for sn, st in STATICS.items():
            e_plus = st + 0.5 * (kea + conc) * K_PER_MM + SLOT
            out[f"{cn}_{sn}"] = dict(e_plus=round(e_plus, 3), e_minus=round(e_minus, 3), p203=round(P203_0 - C10_RATE * e_plus, 3),
                                     gate_203=bool(P203_0 - C10_RATE * e_plus >= 0.15 - 1e-9), gate_eminus=bool(e_minus <= 0.29 + 1e-9))
    return out


def _harness():
    T = _load("lowarm_kstop_s1level", os.path.join(REPO, "tools", "alignment_lowarm_s1level.py"))
    T.GLEV[0] = GLEV
    V = T.V; LM = T.LM; DS = T.DS; S = V.S
    FLm = DS.FL; KRm = FLm.G.KR; Base = FLm.G.KR.KB.KDesign
    src = open(os.path.join(HERE, "lowarm-halfring-knuckle-3r-kplay.py")).read()
    a = src.index("PLAY = dict("); b = src.index("FLm.G.KR.KB.KDesign = PlayDesign")
    ns = dict(np=np, math=math, V=V, S=S, KRm=KRm, Base=Base)
    exec(compile(src[a:b], "kplay_PlayDesign(verbatim)", "exec"), ns)
    FLm.G.KR.KB.KDesign = ns["PlayDesign"]
    return T, V, LM, DS, S, ns["PLAY"]


def params(T, LM, sets=None):
    P = dict(LM.CELL_A); P.update(KSTOP); P.update(sets or {})
    return P


def dowel_cut(M, B):
    """J2 low-end dowel at K-eq 46.35: a pose whose K exceeds it cannot be reached (not taken)"""
    dK = np.degrees(np.abs(np.asarray(M.dK, float))); cut = []
    for j in range(len(B.idx)):
        if B.res[j] is not None and dK[j] > DOWEL_K + 1e-9: B.res[j] = None; cut.append(j)
    return cut


def wear(delta, which, dump=None, sets=None):
    T, V, LM, DS, S, PLAY = _harness()
    P = params(T, LM, sets)
    PLAY.update(delta=float(delta), on=True, info={})
    t = time.time()
    res = V.wear(dict(P), which, False, None)
    fit, M1, M, B, r = V.CAP["res"]
    pre = {k: v for k, v in B.report().items() if k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    dK = np.degrees(np.abs(np.asarray(M.dK, float)))
    tk0 = V.taken_of(B)
    cut = dowel_cut(M, B)
    rep = {k: v for k, v in B.report().items() if k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    poses = AP._dump_bench(M, B)
    NAMED = (139, 203, 205, 237, 264, 316, 313)
    named = {int(j): dict(min_mm=poses[j]["min_mm"], cmin=poses[j]["cmin"], taken=poses[j]["taken"], dK=round(float(dK[j]), 3) if j < len(dK) else None)
             for j in NAMED if j < len(poses)} if which == "bench" else None
    out = dict(id=ID, wear=which, delta=float(delta), params=P, exact=os.environ.get("CB_EXACT") == "1", pre_dowel=pre, frozen=rep,
               dowel=dict(K=DOWEL_K, n_cut=len(cut), cut=[dict(i=int(j), kind=B.kind[j], dK=round(float(dK[j]), 3)) for j in cut],
                          dK_taken_max=round(float(max([dK[j] for j in V.taken_of(B)] or [0])), 3), n_taken_pre=len(tk0)),
               play_info=dict(PLAY.get("info", {})), named=named, recomputed=AP.gap_parts(poses),
               verifier={k: res.get(k) for k in ("frozen", "fit_fast", "why", "overhead", "near1", "near2", "minmetal", "n_taken", "contacts",
                                                  "v1_fit_gates", "v3_th_margin", "v4_kplay", "lowarm_fit")},
               s1_geom=T.REC[-1] if T.REC else None, secs=round(time.time() - t, 1),
               claim_frozen_out=res.get("claim_frozen_out"),
               note="frozen protocol of the claim's model (fit Bench(60,160) fast, shape frozen, worn); stage 1 at F+3.9 via T's glev "
                    "hook; dwell K = law + delta on every dwell pose (PlayDesign, kplay red team, verbatim); J2 dowel cut at 46.35")
    if dump:
        json.dump(dict(id=ID, wear=which, delta=float(delta), params=P, frozen=rep, report=B.report(), poses=poses, recomputed=AP.gap_parts(poses),
                       exact=out["exact"], note="written by docs/concepts/models/lowarm-kstop-knuckle-3r.py wear"), open(dump, "w"), default=float)
        out["dump"] = dump
    return out


def combine(paths, probes=(0.0, 0.1, 0.2)):
    """per-pose worst of several worn dumps (a pose is taken only if taken in every one; its metal = the min) + probe readings
    (a taken pose whose metal, main or extra walls, is under the probe counts as contact)"""
    D = [json.load(open(p))["poses"] for p in paths]
    n = len(D[0]); W = []
    for i in range(n):
        rows = [d[i] for d in D]
        eff = lambda r: None if r["min_mm"] is None else min(r["min_mm"], r["cmin"] if r["cmin"] is not None else 9e9)
        rk = lambda r: (0 if r["contact"] else (1 if not r["taken"] else 2), (r.get("nib", 0) / max(r.get("ns", 1), 1)) if r["taken"] else 0,
                        eff(r) if eff(r) is not None else 9e9)
        W.append(dict(min(rows, key=rk)))
    out = {}
    for pr in probes:
        Q = []
        for r in W:
            r2 = dict(r); e = None if r["min_mm"] is None else min(r["min_mm"], r["cmin"] if r["cmin"] is not None else 9e9)
            if pr > 0 and r["taken"] and e is not None and e < pr: r2["taken"] = False; r2["contact"] = True
            Q.append(r2)
        out[f"probe_{pr:.1f}"] = dict(AP.gap_parts(Q), flipped=[r["i"] for r, q in zip(W, Q) if r["taken"] and not q["taken"]])
    named = {i: dict(min_mm=W[i]["min_mm"], cmin=W[i]["cmin"], taken=W[i]["taken"]) for i in (139, 203, 205, 237, 264, 316)}
    return dict(paths=paths, worst=out, named=named)


def geom(outp):
    """3: stop-A geometry inside hub K; 3b: rho(K) of the stage-1 pin about u2 at the dwell exit (which wall blocks +K);
    4: sided budget; 6: M3 (stage-1 level band + the crank's samples inside hub 2's footprint vs the plate notch)"""
    T, V, LM, DS, S, PLAY = _harness()
    PLAY.update(on=False)
    P = params(T, LM)
    os.environ.pop("CB_EXACT", None)
    B1 = V.CB.Bench(n_clip=60, n_ws=160)
    t = time.time()
    r1, M = LM._report_dc(B1, dict(P))
    D = M.D; g = M._scg; dm = M._desmo; RF = LM.RF
    u2 = np.asarray(D.u[1], float); uK = np.asarray(D.uK, float); dR = np.asarray(g["dR"], float); F0 = np.asarray(dm["F0"], float)
    sig, gg, cc = g["sig"], g["g"], g.get("c", 0.0)
    hmid = float(dm["hmid"])
    # ---- 3b: rho(K) at the dwell exit
    Ks = np.radians(np.linspace(0.0, 2.0, 9))
    C = np.einsum("nij,j->ni", S.rotm(dR, sig * RF.phi_of(Ks, gg, cc)), F0)
    rho = np.linalg.norm(C - np.outer(C @ u2, u2), axis=1); z = C @ u2 - hmid
    drho = (rho[1] - rho[0]) / math.degrees(Ks[1] - Ks[0])
    s3b = dict(K_deg=[round(math.degrees(k), 3) for k in Ks], rho_mm=[round(float(x), 4) for x in rho], z_mm=[round(float(x), 4) for x in z],
               drho_dK_mm_per_deg=round(float(drho), 4), wall_blocking_plusK="inner" if drho < 0 else "outer",
               note="dwell groove = circle about u2 at rho(0); +K moves the pin to rho(K); rho falling -> the pin presses the INNER wall, "
                    "which the half ring keeps over the dwell (its outer wall is cut back): +K is blocked by metal that exists")
    # ---- 3: stop A in hub K's O20
    cyl = M.cyl.get("hubK") if hasattr(M, "cyl") else None
    s3 = dict(hub_r=S.HUB_R, lug_r=LUG_R, groove_r=GRV_R, groove_z_over_FK=GRV_Z, stack_lower_plate=[0.0, 3.0], member_from=V.KIT.STACK, crown=V.KIT.CROWN,
              groove_to_seat_wall=round(GRV_R[0] - MR117_OD_R, 3), thread_to_seat_wall=round(SCREW_R - M16_MAJOR_R - MR117_OD_R, 3),
              groove_to_O20_wall=round(S.HUB_R - GRV_R[1], 3), inside_O20=bool(GRV_R[1] <= S.HUB_R - 1.0 and GRV_Z[1] <= V.KIT.CROWN - 1.0),
              lug_clear_radial=[round(LUG_R[0] - GRV_R[0], 3), round(GRV_R[1] - LUG_R[1], 3)],
              groove_arc_deg=round(STOPB_K + math.degrees(1.41 / SCREW_R), 2),
              screw_axis_exit_az_offset_deg=round(math.degrees(math.atan2(math.sqrt(S.HUB_R ** 2 - SCREW_R ** 2), SCREW_R)), 2),
              cyl_hubK=None if cyl is None else str(type(cyl)))
    # free azimuth sector around hub K (link 1a / link 1b bar roots and the stage-2 nose arm) for the access bore exit
    try:
        cK = np.asarray(D.cK if hasattr(D, "cK") else (cyl[1] if cyl is not None else D.c[0]), float)
    except Exception:
        cK = None
    try:
        bx = S.unit(np.cross(uK, [0.3, 0.5, 0.8])); by = np.cross(uK, bx); occ = {}
        for nm in ("L1a", "L1b"):
            if nm in M.link_pts and cK is not None:
                X = np.asarray(M.link_pts[nm][1], float).reshape(-1, 3); w = X - cK; rr = np.linalg.norm(w - np.outer(w @ uK, uK), axis=1)
                sel = (rr > S.HUB_R - 0.5) & (rr < S.HUB_R + 6.0)
                if sel.any():
                    az = np.degrees(np.arctan2(w[sel] @ by, w[sel] @ bx)); occ[nm] = [round(float(np.min(az)), 1), round(float(np.max(az)), 1), int(sel.sum())]
        s3["hubK_frame"] = dict(cK=None if cK is None else [round(float(x), 2) for x in cK], occupied_az=occ)
    except Exception as e:
        s3["hubK_frame_err"] = repr(e)[:200]
    # ---- 6: M3 - crank samples inside hub 2's footprint, in link 1b's frame, over every fit pose (dwell + rise)
    m3 = {}
    try:
        c2 = np.asarray(D.c[1], float); H2 = float(c2 @ u2 + float(M.f[1]))
        bx2 = S.unit(np.cross(u2, [0.3, 0.5, 0.8])); by2 = np.cross(u2, bx2)
        crank = [X for m, X in M.contact if m == 9] + [X for k, (m, X) in M.rigid.items() if m == 9] + [X for k, (m, X) in M.strap.items() if m == 9]
        C9 = np.concatenate([np.asarray(X, float).reshape(-1, 3) for X in crank])
        mLb = M.link_pts["L1b"][0]
        idx = np.nonzero(np.asarray(M.kin_ok, bool))[0]; band = []; dKs = np.degrees(np.abs(np.asarray(M.dK, float)))
        for i in idx:
            R9, t9 = M.T(9, i); Rb, tb = M.T(mLb, i)
            Xb = (C9 @ R9.T + t9 - tb) @ Rb
            w = Xb - c2; lv = Xb @ u2 - H2; rr = np.linalg.norm(w - np.outer(w @ u2, u2), axis=1)
            az = np.degrees(np.arctan2(w @ by2, w @ bx2))
            sel = (rr <= S.HUB_R + 0.15) & (lv < 3.0 + 0.15)
            for a_, r_, l_ in zip(az[sel], rr[sel], lv[sel]): band.append((float(a_), float(r_), float(l_), float(dKs[i])))
        if band:
            A = np.array(band)
            m3 = dict(n_samples_in_plate_band=len(A), az_range=[round(float(A[:, 0].min()), 1), round(float(A[:, 0].max()), 1)],
                      r_range=[round(float(A[:, 1].min()), 2), round(float(A[:, 1].max()), 2)], level_range=[round(float(A[:, 2].min()), 3), round(float(A[:, 2].max()), 3)],
                      K_range=[round(float(A[:, 3].min()), 2), round(float(A[:, 3].max()), 2)],
                      notch_floor=1.0, arm_underside_min_needed=1.15, notch_ok=bool(A[:, 2].min() >= 1.15 - 1e-9 and A[:, 1].min() >= 6.3 - 1e-9))
        else:
            m3 = dict(n_samples_in_plate_band=0)
        m3["s1_rec"] = {k: (T.REC[-1] or {}).get(k) for k in ("groove_layer_over_face_mm", "pin_band_over_face_mm", "arm_root_over_face_mm",
                                                              "arm_pin_end_over_face_mm", "lower_plate_over_face_mm", "pivot_radius_about_u2_mm",
                                                              "l1b_samples_r_le_12", "stage1", "dK_lim", "why_lim")} if T.REC else None
    except Exception as e:
        m3["err"] = repr(e)[:300]
    lw = getattr(M, "_lowarm", None) or {}
    out = dict(id=ID, params=P, fit_fast={k: r1.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1", "why", "desmo_fail")},
               s3b_rho=s3b, s3_stopA=s3, s4_budget=budget(), s6_m3=m3,
               dK_lim=((getattr(M, "_sc_info", None) or {}).get("dK_lim")), why_lim=((getattr(M, "_sc_info", None) or {}).get("why_lim")),
               lowarm_model_gates=lw, secs=round(time.time() - t, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(out, default=float)[:6000])


def gates(outp):
    """7: RC_MIN as a cut and the bind first-fail at a_s +-0.1 x mu 0.12 / 0.15 / 0.17 (fast fit model, the built read)"""
    T, V, LM, DS, S, PLAY = _harness()
    PLAY.update(on=False)
    os.environ.pop("CB_EXACT", None)
    B1 = V.CB.Bench(n_clip=60, n_ws=160); rows = []
    for a_s in (9.7, 9.8, 9.9):
        for mu in (0.12, 0.15, 0.17):
            P = params(T, LM, dict(a_s=a_s, mu=mu)); t = time.time()
            r1, M = LM._report_dc(B1, dict(P))
            info = getattr(M, "_sc_info", None) or {}; d = info.get("desmo") or {}; st1 = d.get("stage1") or {}; sb = d.get("stage1_built") or {}
            ib, fo, re_, ct = r1["inband14"], r1["follow"], r1["reach"], r1["contact"]
            rows.append(dict(a_s=a_s, mu=mu, dK_lim=info.get("dK_lim"), why_lim=info.get("why_lim"), rc_min=st1.get("rc_min"), rc_ok=bool((st1.get("rc_min") or 0) >= 1.0),
                             pin_first_fail_K=sb.get("pin_first_fail_K"), cap_first_fail_K=sb.get("cap_first_fail_K"),
                             bind_ok=bool(min([x for x in (sb.get("pin_first_fail_K"), sb.get("cap_first_fail_K")) if x is not None] or [99]) >= 47.35),
                             pa_pin=st1.get("pa_pin_max"), pa_cap=st1.get("pa_cap_max"), pa_gate=st1.get("pa_gate"), desmo_fail=list(getattr(M, "_desmo_fail", []) or []),
                             fit_plain=round(100 * (max(0, .9 - ib) + max(0, .95 - fo) + max(0, .9 - re_)) + 100 * ct, 2), reach=re_, secs=round(time.time() - t, 1)))
            print(json.dumps(rows[-1], default=float), flush=True)
    json.dump(dict(id=ID, rows=rows, rule="bind first-fail >= 47.35 (dowel 46.35 + 1.0) at a_s +-0.1 and mu 0.17; RC_MIN (rc >= 1.0) is a cut"), open(outp, "w"), indent=1, default=float)


CLAIM_DELTA = 0.264      # the wall-side P5 worst corner; the - side (-0.210) is worn with `wear` and combined per pose


def frozen(P=None, delta=CLAIM_DELTA):
    """the claim's frozen protocol at one sided dwell play (for tools that call mod.frozen: sample_density, verifiers)"""
    T, V, LM, DS, S, PLAY = _harness(); PLAY.update(delta=float(delta), on=True, info={})
    return LM.frozen(params(T, LM, {k: v for k, v in (P or {}).items() if k in KSTOP or k in LM.CELL_A}))


def frozen_held(P=None, delta=CLAIM_DELTA):
    T, V, LM, DS, S, PLAY = _harness(); PLAY.update(delta=float(delta), on=True, info={})
    return LM.frozen_held(params(T, LM, {k: v for k, v in (P or {}).items() if k in KSTOP or k in LM.CELL_A}))


if __name__ == "__main__":
    mode = sys.argv[1]
    sets = {}
    for i_, a_ in enumerate(sys.argv):
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); sets[k_] = float(v_)
    if mode == "geom":
        geom(sys.argv[2])
    elif mode == "wear":
        d, which, outp = float(sys.argv[2]), sys.argv[3], sys.argv[4]
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        o = wear(d, which, dump, sets)
        json.dump(o, open(outp, "w"), indent=1, default=float)
        print(json.dumps({k: o.get(k) for k in ("delta", "wear", "pre_dowel", "frozen", "dowel", "play_info", "named", "recomputed", "secs")}
                         | {"v": {k: (o["verifier"] or {}).get(k) for k in ("why", "overhead", "near1", "minmetal", "contacts", "v3_th_margin")}}, default=float))
    elif mode == "combine":
        print(json.dumps(combine(sys.argv[2:]), default=float, indent=1))
    elif mode == "gates":
        gates(sys.argv[2])
    elif mode == "budget":
        print(json.dumps(budget(), indent=1))

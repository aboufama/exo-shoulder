"""Independent verifier, lens BUILDABILITY AND RED TEAM, for minarc-stop-knuckle-4r variant B config BDp
(docs/concepts/rows/minarc-stop-knuckle-4r.json kitrule_*; model docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py with
kitrule 1, phys 1, capK 6, m3e 1; params docs/concepts/verify/minarc-kitrule/params_floorBD5_phys_cap6.json).
The model and the claim harness are imported UNCHANGED; this file re-derives what it tests from the raw geometry.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/minarc-bdp-buildability.py equil  out.json
        th-scan of the q2-slot + K mechanism: every spring equilibrium (local minimum of |dK| on the self-motion curve at
        fixed arm pose, J2 inside its slot, K inside [stop A, stop B]) vs the model's state; the physical lock (stop B or
        the sub-chain fold) vs the rule cut (m3e / msub >= 5); clip K motion at 10 fps; spring strip stress table.
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/minarc-bdp-buildability.py demand out.json
        spring demand on the fitted shape (fit60): gravity 1 g / 2 g and seal friction along K's opening self-motion at
        every kinematically valid pose (state A and forced), incl. every clip frame.
    OMP_NUM_THREADS=1 CB_EXACT=1 nice -n 10 python3 docs/concepts/verify/minarc-bdp-buildability.py pinch <bench|held> out.json
        frozen fit60 -> worn copy: the cap in the worn copy (crown, samples, contact rings), and the part that is nearest
        the skin at the near-touch poses and on every overhead (elev >= 140) pose, per part; the claim BD (old model) too.
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                    # noqa: E402
import concept_kit as KIT                                     # noqa: E402

D2R = math.pi / 180


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


W = _load("bdp_claim_wear", os.path.join(REPO, "docs/concepts/models/minarc-stop-knuckle-4r-kitrule-wear.py"))
KR, VER = W.KR, W.VER
S, PK = KR.S, KR.PK
PJ = json.load(open(os.path.join(HERE, "minarc-kitrule", "params_floorBD5_phys_cap6.json")))


def rotm(k, a):
    k = np.asarray(k, float); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * (K @ K)


def design():
    P = VER.params_for("B", PJ); D = KR.KRDesign(P)
    Z = CB._poses_all(); Q = Z["HG"].astype(float); D.ik(Q)            # sets q2sgn / q2_stops as the claim does
    return D, P, Z


def roots_dK(D, q2, cth):
    """independent closure: u1 . R(uK, dK) R(u2, q2) u3 = cos th -> both dK roots (rad), NaN where none"""
    u1, u2, u3 = D.u; uK = D.uK
    p = np.array([rotm(u2, a) @ u3 for a in q2])
    A0 = (u1 @ uK) * (p @ uK); Bk = p @ u1 - A0; Ck = np.cross(uK, p) @ u1
    Rk = np.hypot(Bk, Ck); f0 = np.arctan2(Ck, Bk); x = (cth - A0) / Rk
    g = np.where(np.abs(x) <= 1, np.arccos(np.clip(x, -1, 1)), np.nan)
    wrap = lambda a: (a + np.pi) % (2 * np.pi) - np.pi
    return wrap(f0 - g), wrap(f0 + g)


def mode_equil(outp):
    D, P, Z = design(); u1, u2, u3 = D.u; uK = D.uK; m = KIT.FOLD_MARGIN
    sp = float(np.sign(D.psiA)); b1, b2 = float(P["bk1"]), float(P["bk2"])
    cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(b1 * D2R) * math.cos(b2 * D2R)) / (math.sin(b1 * D2R) * math.sin(b2 * D2R))
    dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(D.psiA))
    lo, hi = sorted(D.q2_stops); q2g = np.radians(np.linspace(lo, hi, 2521))        # 0.05 deg
    out = dict(q2_stops_deg=[round(x, 3) for x in D.q2_stops], th_lo=round(D.th_lo, 3), th_hi=round(D.th_hi, 3), dK_stopB_deg=round(math.degrees(dKB), 3),
               a_deg=[round(D.a1, 3), round(D.a2, 3)], psiA_deg=round(math.degrees(D.psiA), 3), q2sgn=D.q2sgn)
    # model's state as a function of th (the state depends on th only: w = Q u3); synthetic arm orientations with R0 u3 = u1
    ths = np.arange(0.0, 180.0, 0.1); rows = []; multi = []; mism = []
    e = np.cross(u3, u1); e /= np.linalg.norm(e); ang0 = math.acos(float(np.clip(u1 @ u3, -1, 1)))
    R0 = rotm(e, ang0); assert np.allclose(R0 @ u3, u1, atol=1e-9)
    n_ = np.cross(u1, [0.3, 0.5, 0.8]); n_ /= np.linalg.norm(n_)
    Qs = np.array([rotm(n_, t * D2R) @ R0 for t in ths])
    q, ok, *_ = D.ik(Qs); st = np.asarray(D._state).copy(); dKm = np.degrees(np.asarray(D._dK)).copy(); m3e = np.asarray(D._m3e).copy(); msub = np.asarray(D._msub).copy()
    thc = np.degrees(np.arccos(np.clip((Qs @ u3) @ u1, -1, 1)))
    # independent closure, parametrised by dK: cos th = A' + B' cos q2 + C' sin q2 with v2 = RK u2, v3 = RK u3
    dKg = sp * np.radians(np.linspace(0.0, math.degrees(dKB), 3142))
    RKs = np.array([rotm(uK, a) for a in dKg]); v2 = RKs @ u2; v3 = RKs @ u3
    Ap = (v2 @ u1) * float(u2 @ u3); Bp = v3 @ u1 - Ap; Cp = np.cross(v2, v3) @ u1; Rp = np.hypot(Bp, Cp); q0p = np.arctan2(Cp, Bp)
    cen = 0.5 * (lo + hi); half = 0.5 * (hi - lo)
    wrapd = lambda a: (a + 180.0) % 360.0 - 180.0
    for j, th in enumerate(thc):
        x = (math.cos(th * D2R) - Ap) / Rp; ex = np.abs(x) <= 1; g = np.arccos(np.clip(x, -1, 1))
        births = []
        for sgn in (1.0, -1.0):
            q2d = np.degrees(q0p + sgn * g); ins = ex & (np.abs(wrapd(q2d - cen)) <= half + 1e-9)
            k_on = np.nonzero(ins & ~np.r_[False, ins[:-1]])[0]
            for k in k_on:
                if k == 0: typ = "A"
                elif not ex[k - 1]: typ = "fold"                       # born at a tangency (J2 at its dyad fold, not on a stop)
                else: typ = "stop_hi" if abs(wrapd(q2d[k] - hi)) < abs(wrapd(q2d[k] - lo)) else "stop_lo"
                births.append((round(float(abs(np.degrees(dKg[k]))), 3), round(float(q2d[k]), 2), typ))
        births.sort(); mer = []
        for b_ in births:
            if mer and abs(b_[0] - mer[-1][0]) < 0.06 and abs(b_[1] - mer[-1][1]) < 0.5: continue
            mer.append(b_)
        gm = mer[0] if mer else None
        row = dict(th=round(float(th), 2), model_ok=bool(ok[j]), model_state=int(st[j]), model_dK=round(float(abs(dKm[j])), 3),
                   m3e=round(float(m3e[j]), 2), msub=round(float(msub[j]), 2) if st[j] != 0 else None,
                   n_equil=len(mer), equil=mer[:6], global_min=gm)
        rows.append(row)
        if len(mer) > 1: multi.append(row)
        if ok[j] and (gm is None or abs(gm[0] - abs(dKm[j])) > 0.1): mism.append(row)
    out["scan"] = dict(n=len(rows), th_range_taken=[min(r["th"] for r in rows if r["model_ok"]), max(r["th"] for r in rows if r["model_ok"])],
                       model_vs_global_min_mismatch=len(mism), mismatch_examples=mism[:8],
                       multiple_equilibria=len(multi), multiple_in_model_ok=sum(1 for r in multi if r["model_ok"]),
                       multi_examples=[r for r in multi if r["model_ok"]][:6] + [r for r in multi if not r["model_ok"]][:6])
    # the stretched lock: where the rules cut vs where the metal physically locks
    fs = [r for r in rows if r["th"] > D.th_hi]
    cut = next((r for r in fs if not r["model_ok"]), None)
    phys = next((r for r in fs if r["global_min"] is None), None)
    out["stretched_end"] = dict(rule_cut_th=cut and cut["th"], rule_cut_row=cut, physical_lock_th=phys and phys["th"],
                                last_physical=[r for r in fs if r["global_min"] is not None][-1:] if fs else None,
                                stopB_reached=[r for r in fs if r["global_min"] and r["global_min"][0] >= math.degrees(dKB) - 0.1][:2],
                                rows_between=[dict(th=r["th"], dK=r["global_min"], m3e=r["m3e"], msub=r["msub"], ok=r["model_ok"]) for r in fs[::5] if r["th"] <= (phys["th"] if phys else 180)][:40])
    # poses of the human data beyond the rule cut: what the wearer meets
    Q = Z["HG"].astype(float); thp = np.degrees(np.arccos(np.clip((Q @ u3) @ u1, -1, 1))); EL = Z["EL"] if "EL" in Z else None
    names = list(Z["NAMES"]); cid = Z["CID"]; POSE = Z["POSE"]
    if cut:
        beyond = thp >= cut["th"]
        out["human_poses_beyond_rule_cut"] = {str(names[c]): int((beyond & (cid == c)).sum()) for c in np.unique(cid)}
        out["human_poses_total"] = {str(names[c]): int((cid == c).sum()) for c in np.unique(cid)}
        if phys:
            bp = thp >= phys["th"]; out["human_poses_beyond_physical_lock"] = {str(names[c]): int((bp & (cid == c)).sum()) for c in np.unique(cid)}
    # clips at 10 fps: K motion (fit + held-out clips)
    fps = float(Z["FPS"]); clips = {}
    for c, nm in enumerate(names):
        if nm.startswith("Workspace"): continue
        ii = np.nonzero(cid == c)[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        qq, okc, *_ = D.ik(Q[ii]); dK = np.degrees(np.asarray(D._dK)); stc = np.asarray(D._state); thc_ = thp[ii]
        rate = np.abs(np.diff(dK)) * fps; acc = np.abs(np.diff(dK, 2)) * fps * fps
        clips[str(nm)] = dict(frames=len(ii), ok=int(okc.sum()), forced=int((okc & (stc != 0)).sum()), dK_max=round(float(np.abs(dK[okc]).max()) if okc.any() else 0, 2),
                              K_rate_max_dps=round(float(rate.max()) if len(rate) else 0, 1), K_acc_max_dps2=round(float(acc.max()) if len(acc) else 0, 0),
                              th_max=round(float(thc_.max()), 2), fit=str(nm) in CB.FIT)
    out["clips"] = clips
    # spring strip 0.3 x 5 mm 1.4310: sigma = 6 M / (b t^2) (uniform bending moment in a spiral strip)
    b, t, E = 5.0, 0.3, 193e3
    EI = E * b * t ** 3 / 12 * 1e-6        # N.m^2 (E MPa * mm^4 -> N.mm^2 -> 1e-6 N.m^2)
    spring = dict(strip_mm=[t, b], EI_Nm2=round(EI, 6), capacity_Nm={str(s): round(s * b * t * t / 6 / 1e3, 4) for s in (1000, 1190, 1330, 1500)})
    tab = []
    for k in (0.010, 0.015, 0.020, 0.030):
        L = EI / k * 1e3                    # active length mm for that rate
        for lab, dKd in (("preload", 0.0), ("bench max 33.95", 33.95), ("held max 34.29", 34.29), ("stop B", math.degrees(dKB))):
            M_ = 0.08 + k * dKd * D2R; tab.append(dict(rate_Nm_rad=k, L_mm=round(L, 0), at=lab, M_Nm=round(M_, 4), sigma_MPa=round(6 * M_ * 1e3 / (b * t * t), 0)))
    spring["table"] = tab
    spring["preload_wind_turns"] = {str(k): round(0.08 / k / (2 * math.pi), 2) for k in (0.010, 0.015, 0.020, 0.030)}
    out["spring"] = spring
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("clips",)}, default=float)[:6000]); print(json.dumps(clips, default=float))


def mode_demand(outp):
    """quasi-static K hold demand on the fitted BDp shape (the mechanism lens's member mass model, re-run here)"""
    MECH = _load("bdp_mech", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
    fitB = VER.PV.fast_bench(60, 160); P = VER.params_for("B", PJ)
    M1 = KR.KModel(fitB, dict(P)); M1.run(); D = M1.D
    mass = MECH.member_mass_model(M1); mass[7] = (mass[7][0] + 4.0, mass[7][1])   # +4 g: 6 mm taller cap + strip (the lens had +2)
    Z = CB._poses_all(); Q = Z["HG"].astype(float)
    q, ok, *_ = D.ik(Q); dK0 = np.asarray(D._dK).copy(); st = np.asarray(D._state)
    opening = float(np.sign(D.psiA)); eps = 0.2 * D2R
    MECH.M = KR.KB                                               # kin() uses the model module's helpers (sub1v / rotmv / unit)
    def coms(dK):
        k = MECH.kin(D, Q, dK); R = {1: k["R1"], 7: k["R1"] @ k["RK"], 2: k["R12"], 3: k["R123"]}; t = {3: k["t3"]}
        return {mm: (gm, np.einsum("nij,j->ni", R[mm], c) + (t[mm] if mm in t else 0)) for mm, (gm, c) in mass.items() if mm in R}, k
    C0, k0 = coms(dK0); Cp, kp = coms(dK0 + opening * eps)
    # kin at dK0 must reproduce the model's pose (J2 on its stop in the forced states)
    q2err = np.degrees(np.abs(PK.wrap(k0["q"][:, 1] - q[:, 1])))
    grad = sum(gm * (Cp[mm][1] - C0[mm][1]) for mm, (gm, _) in Cp.items()) / eps        # g mm / rad along opening
    tau_up = -grad[:, 1] * 9.81e-6; tau_any = np.linalg.norm(grad, axis=1) * 9.81e-6
    dq = np.degrees(np.abs(PK.wrap(kp["q"] - k0["q"]))) / math.degrees(eps)
    okm = ok & (kp["g2"] > 0) & (k0["g2"] > 0) & (q2err < 0.5)
    cid = Z["CID"]; names = list(Z["NAMES"]); clip = ~np.isin(cid, [names.index("Workspace (envelope)")])
    out = dict(masses_g={str(mm): round(g, 1) for mm, (g, _) in mass.items()}, q2_reproduced_bad=int((ok & (q2err >= 0.5)).sum()))
    for nm, sel in (("stopA_all", okm & (st == 0)), ("forced_all", okm & (st != 0)), ("clip_frames", okm & clip), ("clip_forced", okm & clip & (st != 0))):
        if not sel.any(): out[nm] = dict(n=0); continue
        fr = {f"{f:.0f}mNm": round(float((f * 1e-3 * (1 + dq[sel].sum(1))).max()), 4) for f in (1.0, 2.0, 3.0)}
        out[nm] = dict(n=int(sel.sum()), gravity_upright_Nm_max=round(float(tau_up[sel].max()), 4), any_dir_1g_Nm_max=round(float(tau_any[sel].max()), 4),
                       any_dir_2g_Nm_max=round(float(2 * tau_any[sel].max()), 4), friction_Nm_max_per_pair=fr,
                       demand_2g_plus_fric2_Nm_max=round(float((2 * tau_any[sel] + 2e-3 * (1 + dq[sel].sum(1))).max()), 4),
                       ratio_max={j: round(float(dq[sel, i].max()), 2) for i, j in enumerate(("J1", "J2", "J3"))})
    json.dump(out, open(outp, "w"), indent=1, default=float); print(json.dumps(out, default=float))


# ---------------- pinch / cap in the worn copy ----------------
def part_mins(M, B, i):
    """min signed skin distance per part (metal skin-facing samples + contact-only walls / crowns / tops / cap rings)"""
    res = {}
    for nm, (mm, X) in M.rigid.items(): res[f"metal:{nm}"] = (mm, X)
    for nm, (mm, X) in M.link_pts.items(): res[f"metal:{nm}"] = (mm, X)
    hubs = [h[0] for h in M._hubs()]; k = 0; labs = []
    for h in hubs: labs += [f"wall:{h}"] * 4 + [f"crown:{h}"]
    labs += [f"wall:{nm}" for nm in M.link_pts] + ["wall:E", "wall:boss", "wall:boss", "wall:pad", "wall:pad", "top:pad", "rail:knee", "top:knee"]
    for j, (mm, X) in enumerate(M.contact):
        lab = "cap:hubK" if isinstance(M.contact[j], KR._CapT) else (labs[j] if j < len(labs) else f"contact{j}")
        key = lab
        if key in res: X = np.concatenate([res[key][1], X])
        res[key] = (mm, X)
    keys = list(res); Pw = [M.world(res[kk][0], i, res[kk][1]) for kk in keys]
    d = B.dist(i, np.concatenate(Pw)); out = {}; o = 0
    for kk, X in zip(keys, Pw): out[kk] = round(float(d[o:o + len(X)].min()), 2); o += len(X)
    return out


def mode_pinch(which, outp):
    t0 = time.time(); P = VER.params_for("B", PJ)
    fitB = VER.PV.fast_bench(60, 160); wearB = VER.PV.held_bench() if which == "held" else CB.Bench(n_clip=110, n_ws=360)
    calls = []
    a0 = KR.apply_cap
    def logged(Mo, dh): calls.append(type(Mo).__name__); return a0(Mo, dh)
    KR.apply_cap = logged
    M, fitr, M1 = VER.frozen_B(fitB, wearB, P)
    r = M.run()                                                # the claim's own path: KR.KModel.run wraps the frozen fit with apply_cap
    cr = M.cyl_r["hubK"]; mem, cen, ax = M.cyl["hubK"]; _, Xs = M.cyl_surf["hubK"]
    cap = dict(apply_cap_calls=calls, crown_mm=float(getattr(cr, "crown", S.CROWN)), surf_top_mm=round(float(((Xs - cen) @ ax).max()), 3),
               capT_contact_items=sum(1 for c in M.contact if isinstance(c, KR._CapT)), fK=round(float(M.fK), 2),
               M1_crown=float(getattr(M1.cyl_r["hubK"], "crown", S.CROWN)), M1_capT=sum(1 for c in M1.contact if isinstance(c, KR._CapT)))
    kin = np.nonzero(M.kin_ok)[0]
    over = [i for i in kin if float(wearB.poses[i]["elev"]) >= 140]
    named = []
    if which == "bench": named = [8, 9, 10, 11, 118]
    pts = sorted(set(over) | set(named)); rows = []
    for i in pts:
        pm = part_mins(M, wearB, i); low = sorted(pm.items(), key=lambda x: x[1])[:3]
        rows.append(dict(i=int(i), kind=wearB.kind[i], plane=wearB.poses[i]["plane"], elev=round(float(wearB.poses[i]["elev"]), 1), axial=round(float(wearB.poses[i]["axial"]), 1),
                         state=int(M.kstate[i]), dK=round(float(abs(np.degrees(M.dK[i]))), 2), lowest=low, capK=pm.get("cap:hubK"), crownK=pm.get("crown:hubK")))
    capmins = [r["capK"] for r in rows if r["capK"] is not None]
    out = dict(which=which, mode=wearB.mode, cap=cap, fit=fitr, model_run={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}, n_over_kin=len(over), rows=rows,
               cap_min_over_listed=min(capmins) if capmins else None,
               near1_over=[r for r in rows if r["lowest"][0][1] < 1.0], secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(cap=cap, n_over=len(over), near1=[(r["i"], r["kind"], r["plane"], r["elev"], r["axial"], r["state"], r["lowest"]) for r in out["near1_over"]],
                          named=[(r["i"], r["lowest"], r["capK"]) for r in rows if r["i"] in named], cap_min=out["cap_min_over_listed"], secs=out["secs"]), default=float))


def mode_pinch_bd(outp):
    """the refuted claim BD (claim's own model, virtual stops, no cap) at the same raise-overhead frames: which part?"""
    P = VER.params_for("B"); KB0 = _load("bd_claim_model", os.path.join(REPO, "docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py"))
    fitB = VER.PV.fast_bench(60, 160); wearB = CB.Bench(n_clip=110, n_ws=360)
    M1 = KB0.KModel(fitB, dict(P)); M1.run(); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    class Frozen(KB0.KModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid", "Hneed", "Lneed", "hEx", "_Ex", "_h12"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(wearB, P2); M.fit()
    rows = [dict(i=i, lowest=sorted(part_mins(M, wearB, i).items(), key=lambda x: x[1])[:3]) for i in (8, 9, 10, 11)]
    json.dump(rows, open(outp, "w"), indent=1, default=float); print(json.dumps(rows, default=float))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "equil": mode_equil(a[1])
    elif a[0] == "demand": mode_demand(a[1])
    elif a[0] == "pinch": mode_pinch(a[1], a[2])
    elif a[0] == "pinch_bd": mode_pinch_bd(a[1])
    else: raise SystemExit(__doc__)

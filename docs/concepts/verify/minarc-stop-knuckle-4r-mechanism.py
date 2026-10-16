"""Independent verifier, lens MECHANISM / MANUFACTURABILITY / RED TEAM, for minarc-stop-knuckle-4r VARIANT B
(docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py, best_params = CMA stream BD). The model file is not edited;
this harness imports it and swaps only what it tests.

Modes (OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py <mode> [out.json]):
  stops        the J2 "hard stop": is the stop the model applies (on the VIRTUAL angle at J2 between the arcs J2->J1 and
               J2->J3) a stop on J2's own joint angle q2 (link 1b vs link 2, what a dowel in an arc slot at J2 gives)?
               Prints q2 over state A and over the forced states on every pose of the pose file.
  speeds       joint rates (deg/s) on every clip at the clips' real 10 fps (fit + held-out), per joint incl. K.
  spring       quasi-static virtual work on K's self-motion (gravity, any direction at 1 g and 2 g) + the self-motion
               ratios dq_i/dK (bearing friction seen by the spring) + the clock-spring strip's capacity.
  frozen_phys  the frozen Bench(110,360) exact wear with PHYSICAL J2 stops: J2 locked at the q2 of the model's own state-A
               boundary (q2 at phi_hi / phi_lo with K on stop A), K opens to the smallest opening that closes the chain
               (scan + bisection along the self-motion). Two readings: shape fitted by the claim's law and worn with the
               physical stops ("as built"), and shape refitted with the physical stops ("refit").
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("minarc_B_under_test", os.path.join(REPO, "docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py"))
M = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(M)
S, KA, PK = M.S, M.KA, M.PK
D2R = math.pi / 180
ROW = json.load(open(os.path.join(REPO, "docs/concepts/rows/minarc-stop-knuckle-4r.json")))
BP = {k: v for k, v in ROW["best_params"].items() if k not in ("model", "variant")}
PAR = dict(M.PARAMS, **BP)
PAR.update(json.loads(os.environ.get("PAR_OVERRIDE", "{}")))      # e.g. the J2 stops moved to a 5-deg th margin
ORIG_KDESIGN = M.KDesign


def kin(D, Q, dK):
    """the model's own closure (KDesign.ik lines after RK) at a GIVEN knuckle rotation dK (rad, per pose)"""
    u1, u2, u3 = D.u; uK = D.uK; n = len(Q); c3 = D.c[2]
    w = Q @ u3; wu1 = w @ u1
    RK = S.rotm(uK, dK) if n else np.zeros((0, 3, 3))
    v2 = RK @ u2; v3 = RK @ u3
    c12 = v2 @ u1; ca2 = math.cos(D.A[1]); det = 1 - c12 ** 2 + 1e-12
    al = (wu1 - c12 * ca2) / det; be = (ca2 - c12 * wu1) / det; cr = np.cross(np.broadcast_to(u1, v2.shape), v2)
    g2 = (1 - al ** 2 - be ** 2 - 2 * al * be * c12) / np.maximum(np.einsum("ij,ij->i", cr, cr), 1e-12)
    best = None
    for sg in (1.0, -1.0):
        z = al[:, None] * u1 + be[:, None] * v2 + sg * np.sqrt(np.clip(g2, 0, None))[:, None] * cr
        q1 = S.sub1(u1, z, w); R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
        p2 = np.einsum("nij,nj->ni", R1, v2); br = np.sign(np.einsum("ij,ij->i", p2, np.cross(np.broadcast_to(u1, w.shape), w)))
        if best is None: best = [q1.copy(), z.copy(), br]
        else:
            pick = br == D.branch; best[0][pick] = q1[pick]; best[1][pick] = z[pick]
    q1, z = best[0], best[1]
    R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
    q2 = M.sub1v(v2, v3, z); R2p = M.rotmv(v2, q2) if n else np.zeros((0, 3, 3))
    R12 = R1 @ R2p @ RK; vv = M.unit(np.cross(u3, [0.3, 0.5, 0.8]))
    q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv))
    R3 = S.rotm(u3, q3) if n else np.zeros((0, 3, 3)); R123 = R12 @ R3
    t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
    a1e = np.degrees(np.arccos(np.clip(v2 @ u1, -1, 1)))
    return dict(q=np.stack([q1, q2, q3], 1), g2=g2, R1=R1, RK=RK, R12=R12, R123=R123, t3=t3, w=w, a1e=a1e)


def dK_of_a1e(D, a1e):
    b1, b2 = float(D.p["bk1"]), float(D.p["bk2"])
    cpsi = (np.cos(np.asarray(a1e) * D2R) - math.cos(b1 * D2R) * math.cos(b2 * D2R)) / (math.sin(b1 * D2R) * math.sin(b2 * D2R))
    return np.sign(D.psiA) * np.arccos(np.clip(cpsi, -1, 1)) - D.psiA


def q2_stops(D):
    """physical J2 stops = q2 at the model's state-A window ends (K on stop A, virtual phi = phi_hi / phi_lo)"""
    u1, u2, u3 = D.u; g = np.radians(np.arange(-180, 180, 0.002))
    z = np.einsum("nij,j->ni", S.rotm(u2, g), u3); th = np.degrees(np.arccos(np.clip(z @ u1, -1, 1)))
    a1, a2 = D.a1, D.a2
    cphi = (np.cos(th * D2R) - math.cos(a1 * D2R) * math.cos(a2 * D2R)) / (math.sin(a1 * D2R) * math.sin(a2 * D2R))
    phi = np.degrees(np.arccos(np.clip(cphi, -1, 1)))
    return g, phi


class PhysDesign(ORIG_KDESIGN):
    """same chain, same parts; the J2 stops act on J2's own joint angle q2 (a dowel in an arc slot at J2)"""
    Q2LO = Q2HI = None

    def ik(self, Q):
        if not hasattr(self, "uK"): return super().ik(Q)
        P = self.p; n = len(Q)
        dK = np.zeros(n)
        k0 = kin(self, Q, dK)
        lo, hi = self.Q2LO, self.Q2HI
        def feas(k): q2 = np.degrees(k["q"][:, 1]); return (k["g2"] > 0) & (q2 >= lo - 1e-9) & (q2 <= hi + 1e-9)
        fA = feas(k0)
        dKB = float(dK_of_a1e(self, float(P["a1max"])))
        grid = np.linspace(0, dKB, max(2, int(abs(dKB) / (0.25 * D2R)) + 1))
        todo = np.nonzero(~fA)[0]; found = np.full(n, np.nan); prev = np.zeros(n)
        if len(todo):
            Qt = Q[todo]; got = np.zeros(len(todo), bool); fnd = np.full(len(todo), np.nan); lastbad = np.zeros(len(todo))
            for gv in grid[1:]:
                rem = np.nonzero(~got)[0]
                if not len(rem): break
                k = kin(self, Qt[rem], np.full(len(rem), gv)); f = feas(k)
                fnd[rem[f]] = gv; got[rem[f]] = True; lastbad[rem[~f]] = gv
            # bisection between the last infeasible and the first feasible grid value
            idx = np.nonzero(got)[0]
            if len(idx):
                a = lastbad[idx].copy(); b = fnd[idx].copy()
                for _ in range(14):
                    mid = 0.5 * (a + b); k = kin(self, Qt[idx], mid); f = feas(k)
                    b = np.where(f, mid, b); a = np.where(f, a, mid)
                fnd[idx] = b
            found[todo] = fnd
        dK = np.where(fA, 0.0, np.nan_to_num(found, nan=0.0))
        k = kin(self, Q, dK)
        u1 = self.u[0]; w = k["w"]
        th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        q2 = np.degrees(k["q"][:, 1])
        state = np.where(fA, 0, np.where(np.abs(q2 - hi) < np.abs(q2 - lo), 1, -1))
        uKw = np.einsum("nij,j->ni", k["R1"], self.uK); cK = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", uKw, w), -1, 1)))
        b1 = float(P["bk1"])
        msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
        on_stop = (np.abs(q2 - hi) < 0.05) | (np.abs(q2 - lo) < 0.05)      # an opened K must be held by a J2 stop (not a singular closure)
        ok = (fA | (np.isfinite(found) & on_stop)) & (k["g2"] > 0) & bool(self.k_ok)
        ok &= (k["a1e"] <= float(P["a1max"]) + 1e-6)
        ok &= (state == 0) | (msub >= S.SING)
        Z0 = np.zeros((n, 3)); X1 = (k["R1"], Z0); X1b = (k["R1"] @ k["RK"], Z0); X2 = (k["R12"], Z0); X3 = (k["R123"], k["t3"])
        sv = np.einsum("nji,nj->ni", Q, k["t3"]); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        self._X1b, self._dK, self._state, self._a1e, self._msub = X1b, dK, state, np.where(ok, k["a1e"], self.a1), msub
        return k["q"], ok, X1, X2, X3, s


def setup_phys(P):
    D = ORIG_KDESIGN(P)
    g, phi = q2_stops(D)
    Z = CB._poses_all(); q, ok, *_ = D.ik(Z["HG"].astype(float)); st = D._state; q2 = np.degrees(q[:, 1])
    qa = q2[ok & (st == 0)]
    gd = np.degrees(g)
    def near(target_phi, around):
        m = np.abs(gd - around) < 15; j = np.argmin(np.abs(phi[m] - target_phi)); return float(gd[m][j])
    hi_end = near(float(P["phi_hi"]), qa.min()); lo_end = near(float(P["phi_lo"]), qa.max())
    PhysDesign.Q2LO, PhysDesign.Q2HI = min(hi_end, lo_end), max(hi_end, lo_end)
    return dict(q2_stop_stretched=round(hi_end, 3), q2_stop_folded=round(lo_end, 3), stateA_q2=[round(float(qa.min()), 2), round(float(qa.max()), 2)])


def mode_stops():
    D = ORIG_KDESIGN(PAR); Z = CB._poses_all(); names = list(Z["NAMES"])
    q, ok, *_ = D.ik(Z["HG"].astype(float)); st = D._state; q2 = np.degrees(q[:, 1]); dK = np.degrees(D._dK); a1e = D._a1e
    out = dict(stops=setup_phys(PAR))
    for s_, nm in ((0, "A"), (1, "stretched"), (-1, "folded")):
        m = ok & (st == s_)
        if m.any():
            out[nm] = dict(n=int(m.sum()), q2=[round(float(q2[m].min()), 2), round(float(q2[m].max()), 2)],
                           a1e=[round(float(a1e[m].min()), 2), round(float(a1e[m].max()), 2)], dK=[round(float(dK[m].min()), 2), round(float(dK[m].max()), 2)])
    # how far J2 sits off its own stop in the forced states of the claim's law
    lo, hi = PhysDesign.Q2LO, PhysDesign.Q2HI
    m = ok & (st != 0); off = np.minimum(np.abs(q2[m] - lo), np.abs(q2[m] - hi))
    out["forced_q2_off_stop_deg"] = dict(max=round(float(off.max()), 2), p50=round(float(np.median(off)), 2), n_gt_1=int((off > 1).sum()), n=int(m.sum()))
    # physical law on the same poses
    Dp = PhysDesign(PAR); qp, okp, *_ = Dp.ik(Z["HG"].astype(float)); stp = Dp._state; dKp = np.degrees(Dp._dK)
    out["phys"] = dict(ok=int(okp.sum()), claim_ok=int(ok.sum()), states={str(k): int(((stp == k) & okp).sum()) for k in (-1, 0, 1)},
                       ok_lost=int((ok & ~okp).sum()), ok_gained=int((~ok & okp).sum()))
    both = ok & okp & (st != 0)
    out["dK_claim_vs_phys_on_forced"] = dict(n=int(both.sum()), max_abs_diff_deg=round(float(np.abs(dK[both] - dKp[both]).max()), 2) if both.any() else None,
                                             median_abs_diff_deg=round(float(np.median(np.abs(dK[both] - dKp[both]))), 2) if both.any() else None)
    return out


def mode_speeds():
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; fps = float(Z["FPS"])
    out = {"fps": fps}
    for label, Dcls in (("claim_law", ORIG_KDESIGN), ("physical_stops", PhysDesign)):
        if Dcls is PhysDesign: setup_phys(PAR)
        D = Dcls(PAR); res = {}
        for nm in names:
            if nm.startswith("Workspace"): continue
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            Q = Z["HG"][ii].astype(float); q, ok, _, _, _, s = D.ik(Q); dK = D._dK; Kn = D.knee(s); ok = ok & Kn["ok"]
            qq = np.degrees(np.c_[q[:, :3], dK, Kn["qa"], Kn["qb"]])
            arm = np.degrees(np.array([np.arccos(np.clip((np.trace(Q[j].T @ Q[j + 1]) - 1) / 2, -1, 1)) for j in range(len(Q) - 1)]))
            both = ok[:-1] & ok[1:]
            if not both.any(): res[nm] = dict(ok_frames=int(ok.sum()), n=len(ii)); continue
            dq = np.abs(np.degrees(PK.wrap(np.radians(qq[1:] - qq[:-1]))))[both] * fps
            jn = ["J1", "J2", "J3", "K", "pin_a", "pin_b"]
            mx = dq.max(0); j_at = dq.argmax(0)
            ratio = dq / np.maximum(arm[both] * fps, 1.0)[:, None]
            res[nm] = dict(ok_frames=int(ok.sum()), n=len(ii), arm_max_dps=round(float(arm.max() * fps), 1),
                           max_dps={jn[k]: round(float(mx[k]), 1) for k in range(6)},
                           max_ratio_to_arm={jn[k]: round(float(ratio[:, k].max()), 2) for k in range(6)},
                           K_moving_frames=int((dq[:, 3] > 0.5 * fps).sum()))
        out[label] = res
    return out


def member_mass_model(Mod):
    """grams and member-frame centroids: straps 8 x 3 Ti-6Al-4V (4.43 g/cm3) from the fitted link samples; each O20 hub
    10 g split half / half over its two members (+2 g for K's clock-spring cap on link 1b); member 3 = hub-3 half + E strap
    + boss; knee link 3 g"""
    rho = 4.43e-3; out = {}
    def add(m, g, c):
        G, Cm = out.get(m, (0.0, np.zeros(3))); out[m] = (G + g, (Cm * G + c * g) / (G + g))
    for nm, (mem, pts) in Mod.link_pts.items():
        if not len(pts): continue
        area = len(pts) * S.SPACING * 2.0      # 4 rows x 2 mm lateral pitch x SPACING along
        add(mem, area * 3.0 * rho, pts.mean(0))
    for nm, ax, cc, F, mem in Mod._hubs():
        cen = cc + (F + S.CROWN / 2) * ax
        lower = {"hub1": 0, "hubK": 1, "hub2": 7, "hub3": 2}[nm]; upper = {"hub1": 1, "hubK": 7, "hub2": 2, "hub3": 3}[nm]
        if lower != 0: add(lower, 5.0, cen)
        add(upper, 5.0 + (2.0 if nm == "hubK" else 0.0), cen)
    E = Mod.rigid["E"][1]; add(3, len(E) * S.SPACING * 4 * 3.0 * rho, E.mean(0))
    add(3, 2.0, Mod.rigid["boss"][1].mean(0)); add(6, 3.0, Mod.rigid["knee"][1].mean(0))
    return out


def mode_spring():
    B = CB.Bench(n_clip=60, n_ws=160)
    Mod = M.KModel(B, dict(PAR)); Mod.run()
    mass = member_mass_model(Mod)
    D = Mod.D; Z = CB._poses_all(); Q = Z["HG"].astype(float)
    q, ok, *_ = D.ik(Q); dK0 = D._dK.copy(); st = D._state
    eps = 0.2 * D2R; opening = -1.0 if dK_of_a1e(D, D.a1 + 5) < 0 else 1.0
    def coms(dK):
        k = kin(D, Q, dK); R = {1: k["R1"], 7: k["R1"] @ k["RK"], 2: k["R12"], 3: k["R123"]}; t = {1: 0, 7: 0, 2: 0, 3: k["t3"]}
        out = {}
        for m, (gm, c) in mass.items():
            if m in R: out[m] = (gm, np.einsum("nij,j->ni", R[m], c) + (t[m] if not np.isscalar(t[m]) else 0))
        return out, k
    Cp, kp = coms(dK0 + opening * eps); Cm, km = coms(dK0 - opening * eps)
    grad = sum(gm * (Cp[m][1] - Cm[0 if False else m][1]) for m, (gm, _) in Cp.items()) / (2 * eps)   # g*mm per rad
    gN = 9.81e-3 * 1e-3                                       # (g -> kg) * (mm -> m) * 9.81
    tau_up = -grad[:, 1] * 9.81 * 1e-6                        # gravity -y (thorax y up): opening torque N.m = -dU/dK
    tau_any = np.linalg.norm(grad, axis=1) * 9.81 * 1e-6      # worst gravity / acceleration direction, 1 g
    dq = np.degrees(np.abs(PK.wrap(kp["q"] - km["q"]))) / np.degrees(2 * eps)
    okm = ok & (kp["g2"] > 0) & (km["g2"] > 0)
    out = dict(masses_g={str(m): round(g, 1) for m, (g, _) in mass.items()}, total_moving_g=round(sum(g for m, (g, _) in mass.items() if m in (1, 7, 2, 3)), 1))
    for nm, sel in (("stopA", okm & (st == 0)), ("forced", okm & (st != 0))):
        if not sel.any(): continue
        out[nm] = dict(n=int(sel.sum()), gravity_opening_Nm_max=round(float(tau_up[sel].max()), 4),
                       any_dir_1g_Nm_max=round(float(tau_any[sel].max()), 4), any_dir_2g_Nm_max=round(float(2 * tau_any[sel].max()), 4),
                       self_motion_ratio_max={j: round(float(dq[sel, k].max()), 2) for k, j in enumerate(("J1", "J2", "J3"))},
                       self_motion_ratio_p95={j: round(float(np.percentile(dq[sel, k], 95)), 2) for k, j in enumerate(("J1", "J2", "J3"))})
    # friction seen along the self-motion: MR117-2RS pair ~1.0-2.0 mN.m per sealed pair (contact seals), at K and J1-J3
    for f_pair in (1.0e-3, 2.0e-3):
        tf = f_pair * (1 + dq[:, 0] + dq[:, 1] + dq[:, 2])
        out[f"friction_Nm_max_pair{f_pair * 1e3:.0f}mNm"] = round(float(tf[okm].max()), 4)
    # clock spring strip 0.2 x 3 stainless (the row's part): capacity M = sigma b t^2 / 6
    for sig in (1400.0, 2000.0):
        out[f"strip_0.2x3_capacity_Nm_at_{int(sig)}MPa"] = round(sig * 3 * 0.2 ** 2 / 6 / 1e3, 4)
    out["claimed_spring_Nm"] = dict(preload=0.08, rate_per_rad=0.03, at_stopB=round(0.08 + 0.03 * abs(float(dK_of_a1e(D, float(PAR["a1max"])))), 3))
    out["stress_needed_MPa_for_claim_at_stopB"] = round(out["claimed_spring_Nm"]["at_stopB"] * 1e3 * 6 / (3 * 0.2 ** 2), 0)
    return out


class _RK(float):
    """hub K's radius carrying its own (taller) crown: the clock-spring cap on top of the O20 stack"""
    crown = S.CROWN


def cap_k(Mw, dh):
    """hub K's cap dh mm taller (spring cap on the crown side, away from the skin): part-part cylinder, crown samples and
    the skin-contact rings of hub K all use F .. F + CROWN + dh"""
    r = _RK(Mw.cyl_r["hubK"]); r.crown = S.CROWN + dh; Mw.cyl_r["hubK"] = r
    base = Mw.sd_cylr
    def sd_cyl(Pw, cen, ax, r=None):
        rr = max(Mw.hr) if r is None else r
        return base(Pw, cen, ax, rr, getattr(rr, "crown", S.CROWN))
    Mw.sd_cyl = sd_cyl
    mem, cen, ax = Mw.cyl["hubK"]; e, f = S.frame_of(ax); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); H = S.CROWN + dh
    pts = [cen + z * ax + float(r) * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, H, 7)]
    dd = S.disc(float(r), 4.0); pts.append(cen + H * ax + dd[:, :1] * e + dd[:, 1:] * f); Mw.cyl_surf = dict(Mw.cyl_surf); Mw.cyl_surf["hubK"] = (mem, np.concatenate(pts))
    ang32 = np.linspace(0, 2 * np.pi, 32, endpoint=False); ring = float(r) * (np.cos(ang32)[:, None] * e + np.sin(ang32)[:, None] * f)
    extra = [(mem, cen + z * ax + ring) for z in np.linspace(S.CROWN, H, 3)]
    dd2 = S.disc(float(r), 2.0); extra.append((mem, cen + H * ax + dd2[:, :1] * e + dd2[:, 1:] * f))
    Mw.contact = list(Mw.contact) + extra


def frozen_custom(P, fit_cls, wear_cls, nc=110, nw=360, post=None):
    """= the model's frozen(): shape fitted on Bench(60,160) fast with fit_cls, worn on Bench(nc,nw) exact with wear_cls"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M.KDesign = fit_cls
    M1 = M.KModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    class Frozen(M.KModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            if post is not None: post(self)
    M.KDesign = wear_cls
    B = CB.Bench(n_clip=nc, n_ws=nw); Mw = Frozen(B, P2); r = Mw.run()
    M.KDesign = ORIG_KDESIGN
    LAST["M"], LAST["B"] = Mw, B
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    st = Mw.kstate; ko = Mw.kin_ok
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, why=r.get("why"), parts_ib14=r.get("parts_ib14"), audit=PK.audit(Mw, B),
                knuckle=dict(forced_kin=int((ko & (st != 0)).sum()), stretched=int((ko & (st == 1)).sum()), folded=int((ko & (st == -1)).sum())))


LAST = {}


def flood(Mw, B, grid="bench", passive_jump=10.0, active_jump=25.0, step_deg=2.0):
    """the continuity rule (CLAUDE.md, connected() of stop-relay-rocker-3r.py) on this VModel: nodes = taken ws poses;
    edges = grid neighbours (one step in plane / elevation / axial of the bench's ws grid; grid="knn": every taken ws
    pair within 1.6 x the median nearest-neighbour HG angle) whose 2-deg HG slerp closes at every frame (ik ok + knee
    window + radial tolerance), passive K / pin a / pin b never step > passive_jump deg, actives never > active_jump;
    seeds = taken state-A ws poses. -> connected (P,) bool"""
    from scipy.spatial.transform import Rotation as Rot, Slerp
    n = len(B.kind); D = Mw.D; P = Mw.p
    take = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(n)])
    ws = [i for i in range(n) if B.kind[i] == "ws" and take[i]]
    Q = Mw.Q; st = Mw.kstate
    def edge(a, b):
        R2 = Rot.from_matrix(np.stack([Q[a], Q[b]])); ang = np.degrees((R2[0].inv() * R2[1]).magnitude())
        m = max(2, int(math.ceil(ang / step_deg)) + 1); Qs = Slerp([0, 1], R2)(np.linspace(0, 1, m)).as_matrix()
        q, ok, _, _, _, s = D.ik(Qs); dK = D._dK; Kn = D.knee(s); ok = ok & Kn["ok"] & (np.abs(s[:, 2]) <= P["R_tol"])
        if not ok.all(): return False
        qq = np.degrees(np.c_[q[:, :2], q[:, 2] + Kn["phi"], dK, Kn["qa"], Kn["qb"]])
        dq = np.abs(np.degrees(PK.wrap(np.radians(np.diff(qq, axis=0)))))
        return bool((dq[:, 3:] <= passive_jump).all() and (dq[:, :3] <= active_jump).all())
    if grid == "full":
        # kinematic connectivity on the FULL 15-deg envelope grid (1432 poses, the bench's 360 are a 1-in-4 subsample):
        # intermediate nodes = every envelope pose the chain closes at (ik + knee + radial tolerance + closure < 0.5 deg),
        # skin not evaluated there; a bench pose is connected if its envelope node is reached from a state-A node
        Z = Mw.Z; names = list(Z["NAMES"]); allw = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
        Qa = Z["HG"][allw].astype(float); q, oka, _, _, X3, s = D.ik(Qa); sta = D._state.copy(); Kn = D.knee(s)
        c = (np.einsum("nij,nij->n", X3[0], Qa) - 1) / 2; res = np.degrees(np.arccos(np.clip(c, -1, 1)))
        oka = oka & Kn["ok"] & (np.abs(s[:, 2]) <= P["R_tol"]) & (res < 0.5)
        Pz = Z["POSE"][allw]; keyf = {tuple(np.round(Pz[k, :3], 1)): k for k in range(len(allw)) if oka[k]}
        valsf = [sorted(set(np.round(Pz[:, d], 1))) for d in range(3)]
        def edgef(a, b):
            R2 = Rot.from_matrix(np.stack([Qa[a], Qa[b]])); ang = np.degrees((R2[0].inv() * R2[1]).magnitude())
            m = max(2, int(math.ceil(ang / step_deg)) + 1); Qs = Slerp([0, 1], R2)(np.linspace(0, 1, m)).as_matrix()
            q_, ok_, _, _, _, s_ = D.ik(Qs); dK_ = D._dK; K_ = D.knee(s_); ok_ = ok_ & K_["ok"] & (np.abs(s_[:, 2]) <= P["R_tol"])
            if not ok_.all(): return False
            qq = np.degrees(np.c_[q_[:, :2], q_[:, 2] + K_["phi"], dK_, K_["qa"], K_["qb"]])
            dq = np.abs(np.degrees(PK.wrap(np.radians(np.diff(qq, axis=0)))))
            return bool((dq[:, 3:] <= passive_jump).all() and (dq[:, :3] <= active_jump).all())
        connf = np.zeros(len(allw), bool); front = [k for k in range(len(allw)) if oka[k] and sta[k] == 0]
        for k in front: connf[k] = True
        while front:
            nxt = []
            for a in front:
                x = tuple(np.round(Pz[a, :3], 1))
                for d in range(3):
                    j = valsf[d].index(x[d])
                    for jj in (j - 1, j + 1):
                        if 0 <= jj < len(valsf[d]):
                            y = list(x); y[d] = valsf[d][jj]; b = keyf.get(tuple(y))
                            if b is not None and not connf[b] and edgef(a, b): connf[b] = True; nxt.append(b)
            front = nxt
        pos = {int(z): k for k, z in enumerate(allw)}
        conn = np.zeros(n, bool)
        for i in ws: conn[i] = st[i] == 0 or bool(connf[pos[int(B.idx[i])]])
        LAST["full_stats"] = dict(env_ok=int(oka.sum()), env_forced_ok=int((oka & (sta != 0)).sum()), env_forced_connected=int((connf & (sta != 0)).sum()))
        return conn, take
    if grid == "bench":
        key = {(B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"]): i for i in ws}
        vals = [sorted({B.poses[i][k] for i in range(n) if B.kind[i] == "ws"}) for k in ("plane", "elev", "axial")]
        def nbrs(i):
            x = (B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"])
            for d in range(3):
                j = vals[d].index(x[d])
                for jj in (j - 1, j + 1):
                    if 0 <= jj < len(vals[d]):
                        y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                        if t is not None: yield t
    else:
        from scipy.spatial.transform import Rotation as Rot2
        W = np.array(ws); Rw = Rot2.from_matrix(Q[W]); A = np.zeros((len(W), len(W)))
        for k in range(len(W)): A[k] = np.degrees((Rw[k].inv() * Rw).magnitude())
        np.fill_diagonal(A, 1e9); thr = 1.6 * float(np.median(A.min(1)))
        nb = {int(W[k]): [int(W[j]) for j in np.nonzero(A[k] <= thr)[0]] for k in range(len(W))}
        def nbrs(i): return iter(nb.get(int(i), []))
    conn = np.zeros(n, bool); front = [i for i in ws if st[i] == 0]
    for i in front: conn[i] = True
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if not conn[b] and edge(a, b): conn[b] = True; nxt.append(b)
        front = nxt
    return conn, take


def connected_report(Mw, B):
    out = {}
    base = B.report(); out["static"] = {k: base[k] for k in ("gap", "reach", "follow", "inband14", "contact")}
    st = Mw.kstate; ws = np.array([k == "ws" for k in B.kind])
    for grid in ("bench", "knn", "full"):
        conn, take = flood(Mw, B, grid=grid)
        drop = [j for j in range(len(B.res)) if take[j] and ws[j] and not conn[j]]
        save = list(B.res)
        for j in drop: B.res[j] = None
        r = B.report(); B.res = save
        out[f"connected_{grid}"] = dict(gap=r["gap"], reach=r["reach"], dropped=len(drop), dropped_forced=int(sum(st[j] != 0 for j in drop)),
                                        forced_taken=int(sum(1 for j in range(len(B.res)) if take[j] and ws[j] and st[j] != 0)),
                                        forced_taken_connected=int(sum(1 for j in range(len(B.res)) if take[j] and ws[j] and st[j] != 0 and conn[j])))
        if grid == "full": out["connected_full"]["envelope"] = LAST.get("full_stats")
        if grid == "bench":
            # why the literal reading drops: forced taken poses with NO bench-grid neighbour in the 360-pose subsample
            out["connected_bench"]["dropped_with_no_taken_neighbour"] = int(sum(1 for j in drop if not _has_nbr(B, j, take)))
    return out


def _has_nbr(B, i, take):
    n = len(B.kind); ws = [k for k in range(n) if B.kind[k] == "ws" and take[k]]
    key = {(B.poses[k]["plane"], B.poses[k]["elev"], B.poses[k]["axial"]) for k in ws}
    vals = [sorted({B.poses[k][c] for k in range(n) if B.kind[k] == "ws"}) for c in ("plane", "elev", "axial")]
    x = (B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"])
    for d in range(3):
        j = vals[d].index(x[d])
        for jj in (j - 1, j + 1):
            if 0 <= jj < len(vals[d]):
                y = list(x); y[d] = vals[d][jj]
                if tuple(y) in key: return True
    return False


def mode_frozen_phys(which):
    info = setup_phys(PAR)
    if which == "asbuilt": out = frozen_custom(PAR, ORIG_KDESIGN, PhysDesign)
    elif which == "refit": out = frozen_custom(PAR, PhysDesign, PhysDesign)
    elif which.startswith("capK"):                       # capK<dh>[phys]: hub K dh mm taller (+ physical J2 stops)
        dh = float(which[4:].replace("phys", "")); wear = PhysDesign if which.endswith("phys") else ORIG_KDESIGN
        out = frozen_custom(PAR, ORIG_KDESIGN, wear, post=lambda m: cap_k(m, dh))
    else: out = frozen_custom(PAR, ORIG_KDESIGN, ORIG_KDESIGN)
    out["stops"] = info; out["reading"] = which
    if os.environ.get("FLOOD", "1") == "1": out["continuity"] = connected_report(LAST["M"], LAST["B"])
    return out


if __name__ == "__main__":
    mode = sys.argv[1]; t = time.time()
    if mode == "stops": out = mode_stops()
    elif mode == "speeds": out = mode_speeds()
    elif mode == "spring": out = mode_spring()
    elif mode.startswith("frozen_"): out = mode_frozen_phys(mode.split("_", 1)[1])
    else: raise SystemExit(f"unknown mode {mode}")
    out["secs"] = round(time.time() - t, 1)
    s = json.dumps(out, indent=1, default=float); print(s)
    if len(sys.argv) > 2: open(sys.argv[2], "w").write(s)

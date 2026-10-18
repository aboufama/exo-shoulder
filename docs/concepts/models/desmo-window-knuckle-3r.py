"""desmo-window-knuckle-3r (round 104 lens C): desmo-conecut-knuckle-3r cell B with ONLY its stage-1 stack moved so it can be built.

The verified desmo-conecut model (docs/concepts/verify/desmo-conecut-knuckle-3r.py, the verifier's DCModel with the built groove's
blended law in the IK, --blend; frozen exact Bench(110,360) 18.98) puts the stage-1 groove at F2+0.11..1.61 (F2 = hub 2's face
along u2 = M.f[1]), inside link 1b's J2 plate layer F2+0..3.0, and the gen-9 CAD crosses link 1b by 1.39-1.50 mm on every frame
(R6 1.50 FAIL). Here:

  * the groove is cut 1.5 deep into a 440C insert pressed into link 2's UNDERSIDE: insert underside = F2 + lev - 0.75 (lev = the
    groove mid-plane over F2, default 3.9: underside F2+3.15 = 0.15 over link 1b's plate top F2+3.0). The spec's "F+3.15" level
    row of stage1_level_scan.json is a MID-plane level (level_scan's docstring): a groove at mid 3.15 spans 2.4..3.9 and its insert
    would sit inside link 1b's plate over the whole J2 sweep - so the honest level is mid 3.9 (2 legal pins in the CAD's scan, not
    6). Both are scanned here (cmd scan) through the claim model's own stage-1 formulas;
  * the model's own groove synthesis is used unchanged at that level (glev = F2 + lev - zc - 3.15 is set inside the build, the
    claim's clamp [-1, 1.5] bypassed and stated): pitch gate [R_LO 7.06, R_HI 9.94], drift <= 0.6, built-groove pressure angles
    <= 43 - atan(mu 0.15) = 34.47 (pin side wherever the pin moves, cap side outside the blend), crank-free slop <= 0.25; the
    ring / insert sector is sampled by the claim's own code at the new level (rigid outside O20 from HUB_R + 0.25 to
    r_out = pitch_hi + 0.76 + 0.8, contact from the bore) - i.e. the out-of-rim insert metal is priced as metal;
  * the crank is ONE part: boss on link 1b, the short arm (arm_w wide, 1.5 thick) at F2+1.6..3.1 inside a WINDOW milled through
    link 1b's J2 plate over the arm's swept sector (+ win_c a side), the integral O1.5 crowned pin rising from the arm into the
    groove (tip 0.1 under the groove roof). The arm / pin metal replaces the claim's (contact list, member 9); link 1b / hub 2
    samples inside the window band are deleted (reported); the window's inner / outer radius about hub 2's axis and the wall
    left over the O11 (MR117) seat are reported;
  * STOP ORDER (gen-9 VERIFY.md section 5): the drive (groove rise + stage-2 slot) is built and gated to kdrive (default 47.5 deg
    of K), while J2's own dowel window ends at kj2 (default 46.5) and ENGAGES ~0.30 deg of K later (0.14 deg of q2); poses with
    |dK| > kj2 are lost to the J2 stop ('j2stop', applied in _truncate). Pass condition: drive end >= kj2 + 0.30 + 0.25 (K lead).

3 ACTIVE DOF (J1, J2, J3); K slaved; crank pivot, both higher pairs and the knee pins are passive rotations / higher pairs.
0 passive translations, no springs, no gears / pulleys / cables (MVP1).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/desmo-window-knuckle-3r.py check ['<json>']
    ... scan <lev,lev> [out.json]                         (pin scan at the given groove mid-plane levels over F2)
    CB_EXACT=1 ... wear <bench|held> <out.json> ['<json>'] [--dump PATH] [--flood]   (the verifier's wear: frozen protocol)
    hooks: bench_eval(B, params), evaluate(B, params)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "desmo-window-knuckle-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


# the verifier of desmo-conecut WITH its blended IK (--blend: the built groove's law in the IK, as the 18.98 record)
_argv = list(sys.argv); sys.argv = _argv + ["--blend"]
VER = _load("dcverify_for_window", os.path.join(REPO, "docs", "concepts", "verify", "desmo-conecut-knuckle-3r.py"))
sys.argv = _argv
DC, DS, S = VER.DC, VER.DS, VER.S
RF, BM, SC, FL = DC.RF, DC.BM, DC.SC, DC.FL
unit = S.unit
R_LO, R_HI, DRIFT_MAX, GROOVE_W, RING_WALL, BORE_R, PIN_D = DC.R_LO, DC.R_HI, DC.DRIFT_MAX, DC.GROOVE_W, DC.RING_WALL, DC.BORE_R, DC.PIN_D
C_GROOVE, SLOP_MAX = DC.C_GROOVE, DC.SLOP_MAX
GD = 1.5                                                      # groove depth (insert 1.5 thick at the groove)
PLATE_TOP = 3.0                                               # link 1b's J2 plate top over F2 (gen-9 CAD)
ARM_LO, ARM_HI = 1.6, 3.1                                     # the short arm's layer over F2 (inside the window)
SEAT_R = 5.5                                                  # MR117 outer ring O11
ENG_K = 0.30                                                  # J2 dowel engagement past its window, deg of K (0.14 deg of q2 x kK)
K_LEAD = 0.25                                                 # the drawing's K lead / play allowance

ROWB = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "desmo-conecut-knuckle-3r.json")))["best_params"]
WIN = dict(lev=3.9, kdrive=47.5, kj2=46.5, win_c=0.3, arm_w=3.0)
PARAMS = dict(DC.PARAMS); PARAMS.update(ROWB); PARAMS.update(WIN)
# default pin = the CAD scan's best-PA legal pin at mid 3.9 (a_s 9.8, psi 150; PA 29.53, rc 1.024); re-picked by cmd scan
BEST = dict(ROWB); BEST.update(WIN); BEST.update(a_s=9.8, psi=150.0)


def _c(v, lo, hi): return min(max(float(v), lo), hi)


_dcclamp = DC._clamp


def _clamp(p):
    keep = {k: p.get(k, WIN[k]) for k in WIN}
    q = _dcclamp(p)
    q["lev"] = _c(keep["lev"], 0.5, 6.5); q["kdrive"] = _c(keep["kdrive"], 40.0, 60.0); q["kj2"] = _c(keep["kj2"], 30.0, q["kdrive"])
    q["win_c"] = _c(keep["win_c"], 0.15, 1.0); q["arm_w"] = _c(keep["arm_w"], 2.5, 3.5)
    q["kslot"] = q["kdrive"]                                  # the stage-2 slot is cut to the drive end, past J2's engagement
    return q


class WModel(DC.DCModel):
    def _desmo_build_B(self):
        D = self.D; P = D.p; g = self._scg; u2 = unit(D.u[1])
        zc = float(np.asarray(g["PV"], float) @ u2); H2 = float(np.asarray(D.c[1], float) @ u2) + float(self.f[1])
        P["glev"] = H2 + float(P["lev"]) - zc - 3.15          # groove mid-plane at F2 + lev (the claim's clamp bypassed)
        P["kslot"] = float(P["kdrive"])
        super()._desmo_build_B()
        self._window(H2, zc)

    def _window(self, H2, zc):
        """the crank's arm / pin at the window layer, the window cut, the pair checks, the stop order"""
        D = self.D; P = D.p; g = self._scg; info = self._sc_info; dsm = self._desmo
        u2, F0, s0, hmid = unit(dsm["u2"]), np.asarray(dsm["F0"], float), float(dsm["s0"]), float(dsm["hmid"])
        dR, sig, gg, cc = g["dR"], g["sig"], g["g"], g.get("c", 0.0); kgrid = g["kgrid"]; lim = float(g["dK_lim"])
        jl = max(int(np.searchsorted(kgrid, lim + 1e-12)) - 1, 0)
        aw = float(P["arm_w"]); wc = float(P["win_c"])
        # --- replace the claim's pin + arm samples (member 9: pin F0 +- 0.75 u2 and the arm at F0 - 1.0 u2)
        ef, ff = S.frame_of(u2); dd = S.disc(PIN_D / 2, 0.5)
        pin_old = np.concatenate([F0 + zz * u2 + dd[:, :1] * ef + dd[:, 1:] * ff for zz in (-0.75, 0.75)])
        A0o = s0 * dR; seg = np.linspace(0, 1, 8); bn = unit(np.cross(dR, F0 - A0o))
        arm_old = np.array([A0o + t_ * (F0 - A0o) + w_ * bn - 1.0 * u2 for t_ in seg for w_ in (-0.75 * 2, 0.0, 0.75 * 2)])
        old = np.concatenate([pin_old, arm_old]); jx = None
        for j, (m, X) in enumerate(self.contact):
            if m == 9 and len(X) == len(old) and np.allclose(X, old, atol=1e-6): jx = j
        Fp = F0 - (F0 @ u2) * u2                                 # the pin's foot over hub 2's axis plane
        hz = lambda h: Fp + (H2 + h) * u2                        # point on the pin's line at level F2 + h
        # crank axis point at each arm level (the boss is on link 1b's top; the arm runs from the axis to the pin)
        arm, pin = [], []
        for h in (ARM_LO, ARM_HI):
            A = (H2 + h) / float(dR @ u2) * dR; Fh = hz(h); al = unit(Fh - A); ac = unit(np.cross(u2, al))
            for t_ in np.linspace(0, 1, 9):
                for w_ in np.linspace(-aw / 2, aw / 2, 3): arm.append(A + t_ * (Fh - A) + w_ * ac)
        for h in np.arange(ARM_HI, (hmid - H2) + 0.75 - 0.1 + 1e-9, 0.5):
            for d_ in dd: pin.append(hz(h) + d_[0] * ef + d_[1] * ff)
        arm = np.array(arm); pin = np.array(pin).reshape(-1, 3); new = np.concatenate([arm, pin])
        ctrl = (hmid - H2) < PLATE_TOP + 0.9                      # the claim's level (control): keep the claim's arm / pin / plate metal
        if not ctrl:
            if jx is not None: self.contact[jx] = (9, new)
            else: self.contact.append((9, new))
        # --- the window: the arm's footprint (in link 1b's frame, crank turned by phi(K) over [0, lim]) + win_c a side
        phis = sig * RF.phi_of(kgrid[: jl + 1], gg, cc); Rc = S.rotm(dR, phis)
        Ahi = (H2 + ARM_HI) / float(dR @ u2) * dR; Fh = hz(ARM_HI)
        foot = np.array([Ahi + t_ * (Fh - Ahi) + w_ * unit(np.cross(u2, unit(Fh - Ahi))) for t_ in np.linspace(0, 1, 25)
                         for w_ in np.linspace(-aw / 2 - 0.75, aw / 2 + 0.75, 7)] + [Fh + PIN_D / 2 * (math.cos(a) * ef + math.sin(a) * ff) for a in np.linspace(0, 2 * math.pi, 12)])
        sw = np.einsum("kij,pj->kpi", Rc, foot).reshape(-1, 3)   # swept footprint, link 1b frame
        swp = sw - np.outer(sw @ u2, u2); rr = np.linalg.norm(swp, axis=1)
        win = dict(r_in=round(float(rr.min()) - wc, 3), r_out=round(float(rr.max()) + wc, 3), rim_r=float(S.HUB_R),
                   wall_over_O11_seat=round(float(rr.min()) - wc - SEAT_R, 3), past_rim_mm=round(float(rr.max()) + wc - S.HUB_R, 3))
        az = np.degrees(np.arctan2(swp @ ff, swp @ ef)); azu = np.sort(np.mod(az, 360.0)); gaps = np.diff(np.r_[azu, azu[0] + 360.0])
        win["sector_deg"] = round(float(360.0 - gaps.max() + 2 * math.degrees(wc / max(float(rr.min()), 1e-6))), 1)
        Tsw = cKDTree(np.c_[swp @ ef, swp @ ff])
        # link 1b (member of link_pts L1b) and hub 2 samples inside the window band at the plate layer: deleted
        mLb = self.link_pts["L1b"][0]; ndel = 0
        def cut(X):
            if not len(X): return X, 0
            lvl = X @ u2 - H2; Xp = X - np.outer(X @ u2, u2); d, _ = Tsw.query(np.c_[Xp @ ef, Xp @ ff])
            r_ = np.linalg.norm(Xp, axis=1); band = (d <= aw / 2 + wc + 0.75) & (lvl >= -0.5) & (lvl <= PLATE_TOP + 0.5) & (r_ <= win["r_out"] + 0.5)
            return X[~band], int(band.sum())
        for j, (m, X) in enumerate(self.contact):
            if m == mLb and not ctrl: Xn, n_ = cut(X); self.contact[j] = (m, Xn); ndel += n_
        for k_ in list(self.rigid):
            m, X = self.rigid[k_]
            if m == mLb and not ctrl: Xn, n_ = cut(X); self.rigid[k_] = (m, Xn); ndel += n_
        win["n_l1b_samples_deleted"] = ndel
        # --- pair checks (static geometry along u2: both J2 members turn about u2, so layer gaps are fixed)
        ins_lo = hmid - 0.75 - H2; ins_hi = hmid + 0.75 - H2
        # link 1b's highest metal under the insert's annulus (its samples + T_LINK) over the J2 sweep
        r_in_ins = max(float(BORE_R), 0.0); r_out_ins = float(dsm["r_out"])
        Xb = np.concatenate([X for m, X in self.contact if m == mLb] + [X for m, X in self.rigid.values() if m == mLb])
        Xbp = Xb - np.outer(Xb @ u2, u2); rb_ = np.linalg.norm(Xbp, axis=1); lb_ = Xb @ u2 - H2
        ann = (rb_ >= r_in_ins - 0.15) & (rb_ <= r_out_ins + 0.15)
        below = ann & (lb_ < ins_lo)                              # link 1b metal under the insert (its lower plate / strap)
        l1b_top = float(lb_[below].max()) if below.any() else None
        n_slab = int((ann & (lb_ >= ins_lo - 0.15) & (lb_ <= ins_hi + 0.15)).sum())   # link 1b metal inside the insert's slab
        # (link 1b samples far above the slab, e.g. F2+12.25, are its upper J2 cap over link 2's ring: not in the insert's layer)
        pairs = dict(insert_layer=[round(ins_lo, 3), round(ins_hi, 3)], arm_layer=[ARM_LO, ARM_HI],
                     insert_vs_l1b_plate_top=round(ins_lo - PLATE_TOP, 3),
                     l1b_sampled_top_under_insert=round(l1b_top, 3) if l1b_top is not None else None, l1b_samples_in_insert_slab=n_slab,
                     arm_vs_window_wall=round(wc, 3), arm_top_vs_insert=round(ins_lo - ARM_HI, 3),
                     pin_tip_under_roof=0.1, crank_boss_note="boss on link 1b's top outside link 2's pad; crank vs link 2 per pose by the parent's part checks (parts_pairs)")
        fails = []
        if ins_lo - PLATE_TOP < 0.15 - 1e-9: fails.append("insert-l1b-plate")
        if l1b_top is not None: pairs["insert_vs_l1b_sampled_top"] = round(ins_lo - l1b_top, 3)
        if n_slab and not ctrl: fails.append("insert-l1b-slab")
        if ins_lo - ARM_HI < 0.0 - 1e-9: fails.append("arm-insert")
        if win["wall_over_O11_seat"] < 0.8 - 1e-9: fails.append("O11-wall")
        # --- stop order: the drive (groove rise + slot) must outlast J2's own dowel engagement + the K lead
        kj2 = math.radians(float(P["kj2"])); need = math.degrees(kj2) + ENG_K + K_LEAD
        stop = dict(kj2_window=float(P["kj2"]), j2_engage_K=round(math.degrees(kj2) + ENG_K, 2), drive_end_K=round(math.degrees(lim), 2),
                    drive_end_why=g.get("why_lim"), need=round(need, 2), margin=round(math.degrees(lim) - need, 2),
                    order="J2 dowel first" if math.degrees(lim) >= need - 1e-9 else "DRIVE FIRST (stop load through stage 1 / slot)")
        if math.degrees(lim) < need - 1e-9: fails.append("stop-order")
        self._desmo_fail = list(getattr(self, "_desmo_fail", []) or []) + fails
        self._win = dict(window=win, pairs=pairs, stop=stop, fails=fails, lev=float(P["lev"]), glev_eff=round(float(P["glev"]), 3),
                         zc_minus_F2=round(zc - H2, 3), a_s=float(P["a_s"]), psi=float(P["psi"]))
        info["window"] = self._win
        dsm["win"] = self._win

    def _truncate(self):
        """J2 stop B: its dowel window ends at kj2 (< the drive's end kdrive): poses past it are lost to 'j2stop'"""
        g = getattr(self, "_scg", None)
        if g is None or "dK_lim" not in g:
            return super()._truncate()
        lim_d = g["dK_lim"]; g["dK_lim"] = min(lim_d, math.radians(float(self.p.get("kj2", 46.5))))
        try:
            pf0 = set(np.asarray(self.poses_fit).tolist()); super()._truncate()
            lost = pf0 - set(np.asarray(self.poses_fit).tolist())
            dk = np.degrees(np.abs(np.asarray(self.dK, float)))
            for i in lost:
                if dk[i] <= math.degrees(lim_d) + 1e-9: self.why[i] = "j2stop"
        finally:
            g["dK_lim"] = lim_d


# register the model and clamp in every slot the claim's protocol reads
DS.PARAMS = PARAMS; DS._clamp = _clamp; DS.DSModel = WModel
SC.SCModel = WModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = WModel; FL.FLModel_SC = WModel; BM.PARAMS = PARAMS
DC.PARAMS = PARAMS; DC._clamp = _clamp; DC.DCModel = WModel
evaluate, bench_eval = DS.evaluate, DS.bench_eval


def gates(M):
    info = getattr(M, "_sc_info", None) or {}; d = info.get("desmo") or {}
    s1 = d.get("stage1") or {}; s1b = d.get("stage1_built") or {}; sl = d.get("slop") or {}
    return dict(fail=list(getattr(M, "_desmo_fail", []) or []), dK_lim=info.get("dK_lim"), why_lim=info.get("why_lim"),
                pitch=s1.get("pitch"), r_out=s1.get("r_out"), drift=s1.get("drift_max"), rc_min=s1.get("rc_min"), ridge=s1.get("ridge_mm"),
                pa_built_pin=s1b.get("pin_max_moving"), pa_built_cap_out=s1b.get("cap_max_outside_blend"),
                pin_fail_K=s1b.get("pin_first_fail_K"), cap_fail_K=s1b.get("cap_first_fail_K"), lim_by_gate=s1.get("lim_by_gate"),
                n_ring_rigid=s1.get("n_ring_rigid"), ring_az=s1.get("ring_az_deg"),
                kplay=(sl.get("crank_free") or {}).get("max_deg"), kplay_worst=(sl.get("crank_free") or {}).get("worst_tol_c015_deg"),
                slot_slop=(sl.get("slotB") or {}).get("slop_max"), win=getattr(M, "_win", None))


def check(P):
    B = CB.Bench(60, 160); t = time.time()
    r, M = DS._report(B, dict(BEST, **P))
    out = {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    out.update(mode=B.mode, secs=round(time.time() - t, 1), why=r.get("why"), gates=gates(M),
               near1=(r.get("audit") or {}).get("gap_near1") if isinstance(r.get("audit"), dict) else None)
    return out, M, B


def pin_scan(M, levels, a_rng=(7.0, 12.0), step_a=0.1, step_psi=1.0, kdrive=None):
    """stage-1 pin re-placement at groove mid-plane levels over F2, through the claim's OWN stage-1 formulas (built blended groove):
    pin-side PA wherever the pin moves (K in (0, kdrive]), cap-side PA outside the blend, pitch [R_LO, R_HI], drift <= 0.6, the
    groove centreline's min radius (link-2 frame) and the crank-free dwell / rise slop. Rows [a_s, psi, PA max, rc_min, pitch lo,
    pitch hi, slop]"""
    D = M.D; P = D.p; g = M._scg; u2 = unit(D.u[1]); dR, sig, gg, cc, kgrid = g["dR"], g["sig"], g["g"], g.get("c", 0.0), g["kgrid"]
    mu = float(P.get("mu", 0.15)); PAC = 43.0 - math.degrees(math.atan(mu)); dsm = M._desmo; s_th = float(dsm["s_th"]); q_on = float(dsm["q_on"])
    kd = math.radians(float(kdrive if kdrive is not None else P["kdrive"])); sa = abs(s_th)
    hb = math.radians(float(P["blend"])) / sa / 2.0
    zc = float(np.asarray(g["PV"], float) @ u2); H2 = float(np.asarray(D.c[1], float) @ u2) + float(M.f[1])
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1)
    xb = np.arange(-hb - math.radians(2.0) / sa, kd + 1e-9, math.radians(0.05) / sa)
    Kb = np.where(xb <= -hb, 0.0, np.where(xb >= hb, xb, (xb + hb) ** 2 / (4 * hb))); dKb = np.gradient(Kb, xb)
    RCb = S.rotm(dR, sig * RF.phi_of(Kb, gg, cc)); dphb = sig * RF.dphi_of(Kb, gg, cc)
    xg = np.arange(-hb - math.radians(5.0) / sa, kd + 1e-9, math.radians(0.25) / sa)
    Kg = np.where(xg <= -hb, 0.0, np.where(xg >= hb, xg, (xg + hb) ** 2 / (4 * hb)))
    Mx = np.einsum("xij,xjk->xik", S.rotm(u2, -(s_th * xg)), S.rotm(dR, sig * RF.phi_of(Kg, gg, cc)))
    ge, gf = S.frame_of(u2); out = []
    mv = (Kb > 0) & (np.abs(dKb) > 1e-9); capm = xb >= hb
    for lev in levels:
        hm = H2 + lev; R = []
        for a in np.arange(a_rng[0], a_rng[1] + 1e-9, step_a):
            ps = np.radians(np.arange(40.0, 260.0001, step_psi)); v = np.cos(ps)[:, None] * e1 + np.sin(ps)[:, None] * e2
            Fp = ((hm - a * (v @ u2)) / float(dR @ u2))[:, None] * dR + a * v
            Cb = np.einsum("kij,pj->pki", RCb, Fp)
            vp = (dKb * dphb)[None, :, None] * np.cross(dR, Cb); vc = s_th * np.cross(u2, Cb)
            n1 = np.cross(vp - vc, u2); n1 /= np.maximum(np.linalg.norm(n1, axis=2, keepdims=True), 1e-12)
            ang = lambda A, B_: np.degrees(np.arccos(np.clip(np.abs(np.einsum("pki,pki->pk", A, B_)) / (np.linalg.norm(A, axis=2) * np.linalg.norm(B_, axis=2) + 1e-12), 0, 1)))
            paP = np.where(mv[None], ang(n1, np.where(mv[None, :, None], vp, n1)), 0.0); paC = np.where(capm[None], ang(n1, vc), 0.0)
            rho = np.linalg.norm(Cb - (Cb @ u2)[..., None] * u2, axis=2); z = Cb @ u2 - hm
            ok = (rho.min(1) >= R_LO) & (rho.max(1) <= R_HI) & (np.abs(z).max(1) <= DRIFT_MAX)
            pam = np.maximum(paP.max(1), paC.max(1))
            Gx = np.einsum("xij,pj->pxi", Mx, Fp); X, Y = Gx @ ge, Gx @ gf; dx, dy = np.gradient(X, axis=1), np.gradient(Y, axis=1)
            kap = np.abs(dx * np.gradient(dy, axis=1) - dy * np.gradient(dx, axis=1)) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rc = 1.0 / np.maximum(kap.max(1), 1e-9)
            er = Fp - (Fp @ u2)[:, None] * u2; er /= np.linalg.norm(er, axis=1, keepdims=True); vr0 = np.abs(np.einsum("pi,pi->p", np.cross(dR, Fp), er))
            slop = np.degrees(gg * C_GROOVE / np.maximum(vr0, 1e-9))
            for j in np.nonzero(ok)[0]: R.append((round(a, 2), round(math.degrees(ps[j]), 1), round(float(pam[j]), 3), round(float(rc[j]), 3),
                                                   round(float(rho[j].min()), 3), round(float(rho[j].max()), 3), round(float(slop[j]), 3)))
        R = np.array(R) if R else np.zeros((0, 7)); feas = R[(R[:, 2] <= PAC) & (R[:, 3] >= 1.0)] if len(R) else R
        out.append(dict(level=lev, glev=round(H2 + lev - zc - 3.15, 3), candidates=int(len(R)), pa_ok=int((R[:, 2] <= PAC).sum()) if len(R) else 0,
                        rc_ok=int((R[:, 3] >= 1.0).sum()) if len(R) else 0, feasible=feas[np.argsort(feas[:, 5])].tolist() if len(feas) else []))
        print(f"  F2+{lev}: {len(R)} cand, {out[-1]['pa_ok']} PA ok, {out[-1]['rc_ok']} rc ok, {len(feas)} feasible", flush=True)
    return dict(rule=pin_scan.__doc__, gate=round(PAC, 2), kdrive=math.degrees(kd), H2=round(H2, 3), zc=round(zc, 3), levels=out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    if cmd == "check":
        P = json.loads(args[0]) if args else {}
        out, M, B = check(P); print(json.dumps(out, default=float))
    elif cmd == "scan":
        levels = [float(x) for x in args[0].split(",")]; P = json.loads(args[2]) if len(args) > 2 else {}
        out, M, B = check(P)
        res = pin_scan(M, levels); res["check_at"] = out
        if len(args) > 1: json.dump(res, open(args[1], "w"), indent=1, default=float)
        for L in res["levels"]: print(L["level"], json.dumps(L["feasible"][:12]))
    elif cmd == "wear":
        which, path = args[0], args[1]; P = dict(BEST); P.update(json.loads(args[2]) if len(args) > 2 else {})
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        res = VER.wear(P, which, "--flood" in sys.argv, dump)
        fit, M1, M, B, r = VER.CAP["res"]
        res.update(id=ID, exact=os.environ.get("CB_EXACT") == "1", params=P, blend=True, blend_ik=dict(VER._BL), window_gates=gates(M1))
        json.dump(res, open(path, "w"), indent=1, default=float)
        print(json.dumps({k: res.get(k) for k in ("wear", "frozen", "fit_fast", "why", "overhead", "near1", "minmetal", "dK_taken_max", "n_taken", "contacts",
                                                  "v3_th_margin", "secs")} | {"gates": res["window_gates"]}, default=float))

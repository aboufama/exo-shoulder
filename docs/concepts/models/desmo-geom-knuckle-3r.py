"""desmo-geom-knuckle-3r (round 105 lens C): desmo-window-knuckle-3r's buildable level with NEW DRIVE GEOMETRY, so that stage 1
(the groove insert) lies wholly inside hub 2's O20 rim.

Parent: docs/concepts/models/desmo-window-knuckle-3r.py (= the verifier's desmo-conecut DCModel with the blended IK, cell B stage 2,
stage-1 insert on link 2's underside at groove mid-plane F2+3.9, the one-piece crank through a window in link 1b's J2 plate, the
J2-first stop order). Loaded unchanged and subclassed. What this file changes (and nothing else):

  1. CRANK AXIS dR. The parent's rule (sidecar-roller-flank _rod_metal: delta = (HUB_R + 5 + 1) / f2 rad off u2, in the u2-uK
     plane) is replaced by dR(delta, tau) = rot(u2, tau) rot(u2 x uK, delta) u2 - delta = dR_delta deg off hub 2's axis, tau =
     dR_tau deg of azimuth about u2 (0 = the parent's plane). Implemented by re-compiling the parent's _rod_metal source with
     exactly that line replaced (asserted to occur once). dR_delta None = the parent's rule (control: reproduces desmo-window).
  2. CRANK PIVOT HARDWARE. MR52ZZ pair (2 x 5 x 2.5) on an ISO 8734 2 m6 pin in an O8 boss (boss_d 8.0) instead of the parent's
     O10 (MR63ZZ). The boss metal (disc + side rings, the parent's strap / contact entries) is sampled at r = boss_d / 2.
     NEW GATE 'boss-hub2': the boss cylinder (r boss_d/2, zboss .. zboss + BOSS_H along dR) keeps >= 1.0 mm from hub 2's O20
     stack (static: both on link 1b). The parent's CRK-hub2 check skips everything within r2 + 6.5 of hub 2's axis, i.e. the
     boss, so this check is new, not a duplicate.
  3. CRANK LAW. phi = (K / g)(1 + c K) with c = cprog (regressive for c < 0). The parent clamp chain zeroes cprog (slipper-nose's
     lin law); this file restores it after the clamp (c in [-0.09, 0]).
  4. RING GATE 'ring-out-of-rim': pitch_hi + GROOVE_W/2 + RING_WALL <= HUB_R (r_out <= 10.0): no stage-1 metal outside the O20
     rim (desmo-window's out-of-rim sector is what killed it). Asserted: ring2 rigid samples == 0 whenever the gate passes.
  5. ROBUST rc GATE 'rc-robust' (the round-105 judge's hard constraint): the built blended groove's centreline radius >= 1.0 mm
     over the used stroke at every point of a 3 x 3 grid a_s +-0.05 mm x delta +-0.05 deg (corners, edges, nominal: stricter than
     the judge's 4 corners), each with the full stage-1 gates (pitch, drift, built PA) re-evaluated. Computed by s1_metrics, a
     vectorised replica of the claim model's own stage-1 formulas (validated against the model's rc_min / pitch / PA: cmd
     validate).

3 ACTIVE DOF (J1, J2, J3); K slaved (never read); crank pivot, stage-1 pin-in-groove, stage-2 nose-in-slot and the knee pins are
passive rotations / higher pairs. 0 passive translations, no springs, no gears / pulleys / cables (MVP1).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/desmo-geom-knuckle-3r.py check ['<json>']
    ... geo                                      (model geometry: f2, the parent's delta, s_th, H2, zboss)
    ... validate ['<json>']                      (s1_metrics vs the model's own stage-1 report)
    ... s1grid <out.json>                        (the stage-1 feasibility scan over delta, tau, g, c, a_s, psi with the robust gate)
    CB_EXACT=1 ... wear <bench|held> <out.json> ['<json>'] [--dump PATH] [--flood]
    hooks: bench_eval(B, params), evaluate(B, params)
"""
import importlib.util, inspect, json, math, os, sys, textwrap, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "desmo-geom-knuckle-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


W = _load("desmo_window_for_geom", os.path.join(HERE, "desmo-window-knuckle-3r.py"))
VER, DC, DS, S, RF, SC = W.VER, W.DC, W.DS, W.S, W.RF, W.SC
unit = S.unit
R_LO, R_HI, DRIFT_MAX, GROOVE_W, RING_WALL, C_GROOVE, SLOP_MAX = W.R_LO, W.R_HI, W.DRIFT_MAX, W.GROOVE_W, W.RING_WALL, W.C_GROOVE, W.SLOP_MAX
RC_ROBUST = 1.0
RIM_PITCH_MAX = S.HUB_R - GROOVE_W / 2 - RING_WALL           # 8.44: the pitch at which the insert's outer wall meets the O20 rim

# ---------------------------------------------------------------- 1 + 2: the parent's _rod_metal with dR(delta, tau) and the O8 boss
_SRC = textwrap.dedent(inspect.getsource(RF.RFModel._rod_metal))
_REPL = [("g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0); ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)",
          "dR = self._geom_dR(u2, uK, f2)", 1),
         ("S.disc(5.0, 2.0)", "S.disc(self._boss_r(), 2.0)", 1),
         ("_ring(dR * z, 5.0, dR)", "_ring(dR * z, self._boss_r(), dR)", 2)]
for a_, b_, n_ in _REPL:
    assert _SRC.count(a_) == n_, ("parent _rod_metal changed", a_)
    _SRC = _SRC.replace(a_, b_)
_ns = {}
exec(compile(_SRC, "<desmo-geom patched _rod_metal>", "exec"), RF.__dict__, _ns)
RF.RFModel._rod_metal = _ns["_rod_metal"]                     # this process only: the cell-B path calls RF.RFModel._rod_metal(self)


def dR_of(u2, uK, delta_deg, tau_deg):
    ax = unit(np.cross(u2, uK))
    return unit(S.rotm(u2, math.radians(tau_deg))[0] @ (S.rotm(ax, math.radians(delta_deg))[0] @ u2))


def parent_delta(f2): return math.degrees((S.HUB_R + 5.0 + 1.0) / max(f2, 30.0))


GEOM = dict(dR_delta=None, dR_tau=0.0, boss_d=8.0, cprog=0.0, rc_gate=1, rim_gate=1, ring_kit=1)
PARAMS = dict(W.PARAMS); PARAMS.update(GEOM)
# start 1 of the spec (cell B, mu 0.15)
BEST = dict(W.BEST); BEST.update(dict(blend=8.0, dR_delta=13.766, dR_tau=3.8, g=2.44, cprog=-0.057, a_s=8.93, psi=159.8, kdrive=47.5, mu=0.15))


def _c(v, lo, hi): return min(max(float(v), lo), hi)


_wclamp = W._clamp


def _clamp(p):
    keep = {k: p.get(k, GEOM[k]) for k in GEOM}
    if "c_law" in p: keep["cprog"] = p["c_law"]                   # a re-clamp after the parent zeroed cprog keeps the law
    q = _wclamp(p)
    q["dR_delta"] = None if keep["dR_delta"] is None else _c(keep["dR_delta"], 12.0, 18.0)
    q["dR_tau"] = _c(keep["dR_tau"], -8.0, 8.0); q["boss_d"] = _c(keep["boss_d"], 8.0, 10.0)
    q["cprog"] = _c(keep["cprog"], -0.09, 0.0)                   # the parent chain zeroes cprog (lin law): restored here, and
    q["c_law"] = q["cprog"]                                       # carried under a key no parent clamp touches (re-applied in _geom_dR:
    # the model re-clamps its params on construction through the roller-longdyad clamp, which sets cprog 0 - measured: D.p cprog 0.0)
    q["rc_gate"] = int(keep["rc_gate"]); q["rim_gate"] = int(keep["rim_gate"]); q["ring_kit"] = int(keep["ring_kit"])
    return q


class GModel(W.WModel):
    def _geom_dR(self, u2, uK, f2):
        P = self.D.p; dl = P.get("dR_delta")
        if "c_law" in P: P["cprog"] = float(P["c_law"])              # read by the patched _rod_metal a few lines after this call
        if dl is None: dl = parent_delta(f2)
        self._geomv = dict(f2=float(f2), delta=float(dl), tau=float(P.get("dR_tau", 0.0)), parent_delta=round(parent_delta(f2), 4))
        return dR_of(unit(u2), unit(uK), float(dl), float(P.get("dR_tau", 0.0)))

    def _boss_r(self): return float(self.D.p.get("boss_d", 10.0)) / 2.0

    def _desmo_build_B(self):
        super()._desmo_build_B()
        self._ring_kit()
        self._geom_gates()

    def _ring_kit(self):
        """ring_kit=1: the out-of-rim ring2 sector at the kit's 1 pt / 4 mm2 (the desmo-window death audit's ringfix: keep the sampled
        ring nearest the sector's mid radius, 2 mm of arc; conservative). Only matters when the ring is outside the rim (variant W)"""
        if not int(self.D.p.get("ring_kit", 1)) or "ring2" not in self.rigid: return
        m, X = self.rigid["ring2"]; dsm = self._desmo; u2 = unit(dsm["u2"])
        r = np.linalg.norm(X - np.outer(X @ u2, u2), axis=1); rings = np.unique(np.round(r, 3)); rmid = 0.5 * (S.HUB_R + float(dsm["r_out"]))
        rk = rings[np.argmin(np.abs(rings - rmid))]; keep = np.abs(r - rk) < 1e-3
        self.rigid["ring2"] = (m, X[keep]); self._ringkit = dict(n_before=int(len(X)), n_after=int(keep.sum()), kept_ring=float(rk))

    def _geom_gates(self):
        D = self.D; P = D.p; g = self._scg; info = self._sc_info; dsm = self._desmo
        fails = []
        # --- boss vs hub 2's O20 stack (both on link 1b: static)
        mem2, cen2, ax2 = self.cyl["hub2"]; r2 = self.cyl_r["hub2"]; dR, PV = g["dR"], g["PV"]; rb = self._boss_r()
        zb = float(np.linalg.norm(PV))
        ring = np.concatenate([RF._ring(dR * z, rb, dR, 24) for z in np.linspace(zb, zb + SC.BOSS_H, 6)])
        cb = float(self.sd_cyl(ring, cen2, ax2, r=r2).min())
        axd = float(np.linalg.norm(PV - (PV @ unit(D.u[1])) * unit(D.u[1])))
        gv = dict(getattr(self, "_geomv", {}) or {})
        gv.update(boss_r=rb, zboss=round(zb, 3), boss_axis_from_u2=round(axd, 3), boss_vs_hub2=round(cb, 3),
                  spec_rule_delta_min=round(math.degrees((S.HUB_R + rb + 1.0) / max(gv.get("f2", 30.0), 30.0)), 3))
        if cb < 1.0 - 1e-9: fails.append("boss-hub2")
        # --- ring inside the rim
        s1 = (info.get("desmo") or {}).get("stage1") or {}
        r_out = float(dsm["r_out"]); n_ring = len(self.rigid["ring2"][1]) if "ring2" in self.rigid else 0
        gv.update(r_out=round(r_out, 3), ring2_rigid_n=n_ring, rim_margin=round(S.HUB_R - r_out, 3), ring_kit=getattr(self, "_ringkit", None))
        if int(P.get("rim_gate", 1)) and r_out > S.HUB_R + 1e-9: fails.append("ring-out-of-rim")
        if r_out <= S.HUB_R + 1e-9: assert n_ring == 0, "ring inside the rim but ring2 sampled"
        # --- robust rc (3 x 3: a_s +-0.05 x delta +-0.05), full stage-1 gates at each point
        if int(P.get("rc_gate", 1)):
            rob = self.rc_robust()
            gv["rc_robust"] = rob
            if rob["rc_min"] < RC_ROBUST - 1e-9: fails.append("rc-robust")
            if not rob["gates_ok"]: fails.append("s1-robust-gates")
        self._desmo_fail = list(getattr(self, "_desmo_fail", []) or []) + fails
        gv["fails"] = fails
        self._geom = gv; info["geom"] = gv

    def s1_ctx(self):
        D = self.D; P = D.p; g = self._scg; dsm = self._desmo; u2 = unit(D.u[1])
        H2 = float(np.asarray(D.c[1], float) @ u2) + float(self.f[1])
        return dict(u2=u2, uK=unit(np.asarray(g["uK"], float)), H2=H2, s_th=float(dsm["s_th"]), q_on=float(dsm["q_on"]), sig=float(g["sig"]),
                    g=float(g["g"]), c=float(g.get("c", 0.0)), f2=float(self.f[1]), mu=float(P.get("mu", 0.15)), blend=float(P["blend"]),
                    lev=float(P["lev"]), kdrive=float(P["kdrive"]), qdw=self._calib()[2:4])

    def rc_robust(self, da=0.05, dd=0.05):
        P = self.D.p; X = self.s1_ctx(); gv = getattr(self, "_geomv", {}) or {}
        d0, tau = float(gv.get("delta", parent_delta(X["f2"]))), float(P.get("dR_tau", 0.0)); a0 = float(P["a_s"]); ps = float(P["psi"])
        lim = math.degrees(float(self._scg["dK_lim"]))
        rows = []
        for dl in (d0 - dd, d0, d0 + dd):
            m = s1_metrics(X, dR_of(X["u2"], X["uK"], dl, tau), np.array([a0 - da, a0, a0 + da]), np.array([ps] * 3), kd=lim)
            for j in range(3): rows.append(dict(delta=round(dl, 3), a_s=round(a0 + (j - 1) * da, 3), **{k: round(float(v[j]), 3) for k, v in m.items()}))
        rcs = [r["rc"] for r in rows]
        ok = all(r["pitch_lo"] >= R_LO - 1e-9 and r["pitch_hi"] <= R_HI + 1e-9 and r["drift"] <= DRIFT_MAX + 1e-9 and r["pa"] <= r["pac"] + 1e-9
                 for r in rows)
        return dict(rc_min=round(min(rcs), 3), rc_nominal=rows[4]["rc"], pitch_hi_max=round(max(r["pitch_hi"] for r in rows), 3),
                    gates_ok=bool(ok), kd=round(lim, 2), grid=rows)


def s1_metrics(X, dR, a_s, psi, kd=None, lev=None, g=None, c=None, blend=None, pa_step=0.02, chunk=1500):
    """the claim model's stage-1 formulas (desmo-conecut _desmo_build_B, built blended groove), vectorised over pins (a_s, psi):
    pitch lo / hi over the drive, drift, built PA (pin side wherever the pin moves, cap side outside the blend; gate 43 - atan mu),
    the groove centreline's min radius in link 2's frame over the rise (K > 0) and the dwell crank-free slop"""
    u2 = X["u2"]; s_th = X["s_th"]; sig = X["sig"]; gg = X["g"] if g is None else g; cc = X["c"] if c is None else c
    lev = X["lev"] if lev is None else lev; bl = X["blend"] if blend is None else blend; kd = X["kdrive"] if kd is None else kd
    PAC = 43.0 - math.degrees(math.atan(X["mu"])); sa = abs(s_th); hb = math.radians(bl) / sa / 2.0; kdr = math.radians(kd)
    hm = X["H2"] + lev
    a_s = np.atleast_1d(np.asarray(a_s, float)); ps = np.radians(np.atleast_1d(np.asarray(psi, float)))
    if len(a_s) > chunk:
        parts = [s1_metrics(X, dR, a_s[i:i + chunk], np.degrees(ps[i:i + chunk]), kd, lev, g, c, blend, pa_step, chunk) for i in range(0, len(a_s), chunk)]
        return {k: np.concatenate([p_[k] for p_ in parts]) for k in parts[0]}
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1); v = np.cos(ps)[:, None] * e1 + np.sin(ps)[:, None] * e2
    Fp = ((hm - a_s * (v @ u2)) / float(dR @ u2))[:, None] * dR + a_s[:, None] * v
    # built PA (fine grid, as the model: 0.02 deg / s_th)
    xb = np.arange(-hb - math.radians(2.0) / sa, kdr + 1e-9, math.radians(pa_step) / sa)
    Kb = np.where(xb <= -hb, 0.0, np.where(xb >= hb, xb, (xb + hb) ** 2 / (4 * hb))) if hb > 0 else np.maximum(xb, 0.0)
    dKb = np.gradient(Kb, xb); RCb = S.rotm(dR, sig * RF.phi_of(Kb, gg, cc)); dphb = sig * RF.dphi_of(Kb, gg, cc)
    Cb = np.einsum("kij,pj->pki", RCb, Fp)
    vp = (dKb * dphb)[None, :, None] * np.cross(dR, Cb); vc = s_th * np.cross(u2, Cb)
    n1 = np.cross(vp - vc, u2); n1 /= np.maximum(np.linalg.norm(n1, axis=2, keepdims=True), 1e-12)
    mv = (np.linalg.norm(vp, axis=2) > 1e-6) & (Kb[None] > 0)

    def ang(A, B_):
        cs = np.abs(np.einsum("pki,pki->pk", A, B_)) / (np.linalg.norm(A, axis=2) * np.linalg.norm(B_, axis=2) + 1e-12)
        return np.degrees(np.arccos(np.clip(cs, 0, 1)))
    paP = np.where(mv, ang(n1, vp), 0.0); paC = np.where((xb >= hb)[None], ang(n1, vc), 0.0)
    rho = np.linalg.norm(Cb - (Cb @ u2)[..., None] * u2, axis=2); z = Cb @ u2 - hm
    # groove centreline (link 2 frame), 0.25 deg / s_th steps, rise part K > 0 (the model's rcK)
    q_lo, q_hi = X["qdw"]; q_on = X["q_on"]
    x_lo = min((q_lo - q_on) / s_th, (q_hi - q_on) / s_th, 0.0) - math.radians(5.0) / sa
    xg = np.arange(x_lo, kdr + 1e-9, math.radians(0.25) / sa)
    Kg = np.where(xg <= -hb, 0.0, np.where(xg >= hb, xg, (xg + hb) ** 2 / (4 * hb))) if hb > 0 else np.maximum(xg, 0.0)
    Mx = np.einsum("xij,xjk->xik", S.rotm(u2, -(s_th * xg)), S.rotm(dR, sig * RF.phi_of(Kg, gg, cc)))
    ge, gf = S.frame_of(u2); Gx = np.einsum("xij,pj->pxi", Mx, Fp); Xg, Yg = Gx @ ge, Gx @ gf
    dx, dy = np.gradient(Xg, axis=1), np.gradient(Yg, axis=1)
    kap = np.abs(dx * np.gradient(dy, axis=1) - dy * np.gradient(dx, axis=1)) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12)
    rc = 1.0 / np.maximum(np.where((Kg > 0)[None], kap, 0.0).max(1), 1e-9)
    er = Fp - (Fp @ u2)[:, None] * u2; er /= np.linalg.norm(er, axis=1, keepdims=True); vr0 = np.abs(np.einsum("pi,pi->p", np.cross(dR, Fp), er))
    slop = np.degrees(gg * C_GROOVE / np.maximum(vr0, 1e-9))
    return dict(pa=np.maximum(paP.max(1), paC.max(1)), pac=np.full(len(a_s), PAC), rc=rc, pitch_lo=rho.min(1), pitch_hi=rho.max(1),
                drift=np.abs(z).max(1), slop=slop)


# register the model and clamp in every slot the claim's protocol reads
DS.PARAMS = PARAMS; DS._clamp = _clamp; DS.DSModel = GModel
SC.SCModel = GModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
DC.FL.G.KR.KB.KModel = GModel; DC.FL.FLModel_SC = GModel; DC.BM.PARAMS = PARAMS
DC.PARAMS = PARAMS; DC._clamp = _clamp; DC.DCModel = GModel
W.PARAMS = PARAMS; W._clamp = _clamp; W.WModel = GModel
evaluate, bench_eval = DS.evaluate, DS.bench_eval


def gates(M):
    out = W.gates(M); out["geom"] = getattr(M, "_geom", None); return out


def check(P, B=None):
    B = B or CB.Bench(60, 160); t = time.time()
    r, M = DS._report(B, dict(BEST, **P))
    out = {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    out.update(mode=B.mode, secs=round(time.time() - t, 1), why=r.get("why"), honest=r.get("honest", True), plain=r.get("plain"), gap_near1=r.get("gap_near1"),
               min_metal=r.get("min_metal_mm"), gates=gates(M), parts_ib14=r.get("parts_ib14"))
    return out, M, B


def s1grid(M, deltas, taus, gs, cs, a_rng=(7.0, 11.0), step_a=0.05, step_psi=0.5, psi_rng=(60.0, 250.0), extra=None, rim=None):
    """the stage-1 feasibility scan (no bench): for each crank geometry (delta, tau, g, c) every pin (a_s, psi) on the grid that
    passes pitch [R_LO, RIM_PITCH_MAX] (ring inside O20), drift, built PA to kdrive, slop <= 0.25 and rc >= 1.0, then the robust
    3 x 3 rc / gate test on those. extra: mu / blend / kdrive overrides (cell A: mu 0.087, kdrive 53); rim: the pitch cap
    (default RIM_PITCH_MAX 8.44 = 0.8 wall; cell T's 0.6 wall: 8.64)"""
    extra = extra or {}; rim = RIM_PITCH_MAX if rim is None else float(rim); rcr_min = float(extra.get("rc_min", RC_ROBUST))
    X = dict(M.s1_ctx()); kd = float(extra.get("kdrive", X["kdrive"])); out = []
    X["mu"] = float(extra.get("mu", X["mu"])); X["blend"] = float(extra.get("blend", X["blend"]))
    A, PS = np.meshgrid(np.arange(a_rng[0], a_rng[1] + 1e-9, step_a), np.arange(psi_rng[0], psi_rng[1] + 1e-9, step_psi), indexing="ij")
    A, PS = A.ravel(), PS.ravel()
    for dl in deltas:
        for tau in taus:
            dR = dR_of(X["u2"], X["uK"], dl, tau)
            for gg in gs:
                for cc in cs:
                    m = s1_metrics(X, dR, A, PS, kd=kd, g=gg, c=cc, pa_step=0.1)          # coarse PA grid: prefilter (1 deg slack)
                    pre = (m["pitch_lo"] >= R_LO - 0.05) & (m["drift"] <= DRIFT_MAX + 0.05) & (m["pa"] <= m["pac"] + 1.0) & (m["slop"] <= SLOP_MAX + 0.01)
                    if pre.any():
                        mf = s1_metrics(X, dR, A[pre], PS[pre], kd=kd, g=gg, c=cc)          # the model's 0.02-deg grid
                        for k_ in m: m[k_] = m[k_].copy(); m[k_][pre] = mf[k_]
                    base = (m["pitch_lo"] >= R_LO) & (m["drift"] <= DRIFT_MAX) & (m["pa"] <= m["pac"]) & (m["slop"] <= SLOP_MAX)
                    inrim = base & (m["pitch_hi"] <= rim); rcok = inrim & (m["rc"] >= rcr_min)
                    rob = []
                    for j in np.nonzero(rcok)[0]:
                        rr = []
                        for d2 in (dl - 0.05, dl, dl + 0.05):
                            mm = s1_metrics(X, dR_of(X["u2"], X["uK"], d2, tau), np.array([A[j] - 0.05, A[j], A[j] + 0.05]), np.array([PS[j]] * 3), kd=kd, g=gg, c=cc)
                            okk = (mm["pitch_lo"] >= R_LO) & (mm["pitch_hi"] <= rim) & (mm["drift"] <= DRIFT_MAX) & (mm["pa"] <= mm["pac"])
                            rr.append((float(mm["rc"].min()), bool(okk.all()), float(mm["pitch_hi"].max())))
                        rcr = min(r_[0] for r_ in rr); gok = all(r_[1] for r_ in rr)
                        if rcr >= rcr_min and gok:
                            rob.append([round(float(A[j]), 3), round(float(PS[j]), 2), round(float(m["pa"][j]), 2), round(float(m["rc"][j]), 3), round(rcr, 3),
                                        round(float(m["pitch_lo"][j]), 3), round(float(m["pitch_hi"][j]), 3), round(float(m["slop"][j]), 3)])
                    bi = np.nonzero(base)[0]; jb = bi[np.argmin(m["pitch_hi"][bi])] if len(bi) else None
                    row = dict(delta=dl, tau=tau, g=gg, c=cc, mu=X["mu"], blend=X["blend"], kdrive=kd, rim=rim, n_base=int(base.sum()), n_inrim=int(inrim.sum()), n_inrim_rc=int(rcok.sum()),
                               n_robust=len(rob), pitch_hi_min_base=round(float(m["pitch_hi"][base].min()), 3) if base.any() else None,
                               rc_max_inrim=round(float(m["rc"][inrim].max()), 3) if inrim.any() else None,
                               best_base=None if jb is None else [round(float(A[jb]), 3), round(float(PS[jb]), 2), round(float(m["pa"][jb]), 2), round(float(m["rc"][jb]), 3),
                                                                  round(float(m["pitch_lo"][jb]), 3), round(float(m["pitch_hi"][jb]), 3), round(float(m["slop"][jb]), 3)],
                               pa_min_inpitch=round(float(m["pa"][(m["pitch_lo"] >= R_LO) & (m["pitch_hi"] <= rim) & (m["drift"] <= DRIFT_MAX)].min()), 2) if ((m["pitch_lo"] >= R_LO) & (m["pitch_hi"] <= rim) & (m["drift"] <= DRIFT_MAX)).any() else None,
                               robust=sorted(rob, key=lambda r_: r_[6])[:20])
                    out.append(row)
                    print(json.dumps({k: v for k, v in row.items() if k != "robust"}), flush=True)
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    if cmd == "check":
        P = json.loads(args[0]) if args else {}
        out, M, B = check(P); print(json.dumps(out, default=float))
    elif cmd == "geo":
        P = json.loads(args[0]) if args else {}
        out, M, B = check(dict(P, dR_delta=None, dR_tau=0.0, cprog=0.0, rc_gate=0, rim_gate=0))
        X = M.s1_ctx(); print(json.dumps(dict(geom=M._geom, s_th=X["s_th"], H2=X["H2"], f2=X["f2"], sig=X["sig"], gap=out["gap"]), default=float))
    elif cmd == "validate":
        P = json.loads(args[0]) if args else {}
        out, M, B = check(dict(P, rc_gate=0, rim_gate=0)); X = M.s1_ctx(); g = M._scg
        lim = math.degrees(float(g["dK_lim"]))
        m = s1_metrics(X, g["dR"], [float(M.D.p["a_s"])], [float(M.D.p["psi"])], kd=lim)
        s1 = (M._sc_info.get("desmo") or {}).get("stage1") or {}; s1b = (M._sc_info.get("desmo") or {}).get("stage1_built") or {}
        print(json.dumps(dict(replica={k: round(float(v[0]), 3) for k, v in m.items()}, model=dict(pitch=s1.get("pitch"), drift=s1.get("drift_max"),
                              rc_min=s1.get("rc_min"), pa_pin=s1b.get("pin_max_moving"), pa_cap=s1b.get("cap_max_outside_blend"), r_out=s1.get("r_out")),
                              dK_lim=lim, gap=out["gap"], fails=out["gates"]["fail"]), default=float))
    elif cmd == "s1grid":
        path = args[0]; spec = json.loads(args[1]) if len(args) > 1 else {}
        out, M, B = check(dict(rc_gate=0, rim_gate=0))
        res = s1grid(M, spec.get("deltas", [13.75, 13.9, 14.05, 14.2]), spec.get("taus", [-4.0, -2.0, 0.0, 2.0, 4.0]),
                     spec.get("gs", [2.33, 2.39, 2.44, 2.5]), spec.get("cs", [-0.09, -0.057, -0.03, 0.0]),
                     a_rng=tuple(spec.get("a_rng", (7.0, 11.0))), step_a=spec.get("step_a", 0.05), step_psi=spec.get("step_psi", 0.5),
                     psi_rng=tuple(spec.get("psi_rng", (60.0, 250.0))), extra=spec.get("extra"), rim=spec.get("rim"))
        json.dump(dict(rule=s1grid.__doc__, spec=spec, rim_pitch_max=RIM_PITCH_MAX, rc_robust=RC_ROBUST, rows=res), open(path, "w"), indent=1, default=float)
    elif cmd == "wear":
        which, path = args[0], args[1]; P = dict(BEST); P.update(json.loads(args[2]) if len(args) > 2 else {})
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        res = VER.wear(P, which, "--flood" in sys.argv, dump)
        fit, M1, M, B, r = VER.CAP["res"]
        res.update(id=ID, exact=os.environ.get("CB_EXACT") == "1", params=P, blend=True, blend_ik=dict(VER._BL), geom_gates=gates(M1))
        json.dump(res, open(path, "w"), indent=1, default=float)
        print(json.dumps({k: res.get(k) for k in ("wear", "frozen", "fit_fast", "why", "overhead", "near1", "minmetal", "dK_taken_max", "n_taken",
                                                  "contacts", "v3_th_margin", "secs")} | {"geom": (res["geom_gates"] or {}).get("geom")}, default=float))

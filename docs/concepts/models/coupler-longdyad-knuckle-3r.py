"""coupler-longdyad-knuckle-3r (round 11, 2026-10-17; the planner's C4 with the hub-2 lobe kept as stage 1): the slipper-nose
lead's chain (verified seats, stop A, a2, b3 tilt, pin knee) on a LONG K dyad (32/48, stop B a1max <= bk1 + bk2 - 5.5) with
a TWO-STAGE positive-then-force-closed K drive, every axis through GH:

  * stage 1 (the lead's, re-cut): link 2's hub-2 rim LOBE pushes an O2.5 x 8 DLC dowel NOSE pressed into the short lug
    (s_nose = 4.0 mm) of a BELL CRANK that turns on 2 x 683ZZ about dR (an axis through GH, tilted cr_tilt deg from u2
    toward uK, i.e. on link 1b beside hub 2; the boss O10 x 6 stacks on link 1b). Linear law past the onset
    th_hi = a1 + a2 - smhi: |dK| = kK t (t = q2 travel past the onset). Real follower: lift = lift_k s_nose phi (phi the
    crank angle from the stage-2 table), lobe radius r(t) = r_base + lift <= skirt, lobe PA = atan(d lift/dt / r)
    <= 42 - atan(mu) (sliding pair, friction lean included);
  * stage 2 (new): a SPHERICAL 4R - crank (dR) -> long arm (arc cr_a1, azimuth cr_t1 about dR from the dR -> uK great
    circle) -> radial O3 pin -> spherical COUPLER strap (Ti 6 x 3, O9 eyes on 2 x MR63ZZ each) -> radial O3 pin on a
    HORN of link 1a at hub K (arc cr_a3 from uK, azimuth cr_t3). K = K(phi) by continuation, PA at both pins <= 42.
3 ACTIVE DOF (J1, J2, J3 encoded); K slaved (on stop A, or set by q2 through lobe + 4R; K's spiral spring force-closes the
nose on the lobe), never read; 0 passive translations; no gears / pulleys / cables. Passive rotations: K, crank, 2 coupler
pins, 2 knee pins (6). While K rests on stop A the 4R with K fixed has no free coordinate (crank parked, R17).

Built on dogring-draglink-knuckle-3r.py (same parents, its spherical-4R solver, strap / disc samplers, per-pose bodies,
drive-range truncation on every bench, frozen / held / flood claim protocol) - only the input stage is replaced:
the dog sector on u2 (1:1 with q2) becomes the lobe -> nose -> crank on dR (gain split kK = (phi/t) x (dK/dphi)).

Per-pose metal (link 1b frame, carried by T(7, i)): crank = boss underside disc (O10) + long arm (6 wide, 2 mm samples) +
arm-tip eye disc (O8); coupler = strap + two eye discs; horn = lug from hub K's rim to r_h + 4 on link 1a. Levels: boss
stacked on link 1b (its underside at link 1b's top + 0.15); the arm steps down (60-deg ramp) to link 1b's own layer + cr_zr
only where it stays >= W_LINK / 2 + 1 off link 1b's strap over the WHOLE crank swing, else it stays stacked (link 1b top
+ 1 mm); the coupler rides one stack above (+1) or below (-1) the arm-tip eye and the horn eye (dl_a / dl_h), + dl_lift.
Drive range dK_lim: the 4R table end (PA > 42, branch, crank direction reversal), then the swept clearances in link 1b's
frame (arm / coupler / eyes vs hub 2 and hub K housings >= 1 mm, coupler / horn vs link 1b >= 1 mm, boss vs hub 2 >= 1);
J2's stop B dowel sits there and every pose past it is lost on every bench.
Not sampled (stated): the lobe band itself (17-4PH, 3 mm, f2 + 6.2 .. 9.2, r <= 12.8: high on hub 2's housing, ~8 points).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/coupler-longdyad-knuckle-3r.py [check] ['<json>']
    ... synth '<json>'                     (re-synthesise stage 2 on this fit's own u2 / uK / dR)
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json];  ... gate '<json>'
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

os.environ["LS_DRIVE"] = "rssr"
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "coupler-longdyad-knuckle-3r"
_sp = importlib.util.spec_from_file_location("dogring_for_coupler", os.path.join(HERE, "dogring-draglink-knuckle-3r.py"))
DRM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(DRM)
LS, SC, FL, PK, S, RL, KR = DRM.LS, DRM.SC, DRM.FL, DRM.PK, DRM.S, DRM.RL, DRM.KR
unit = S.unit; D2R = math.pi / 180
PA_GATE = 42.0; RATE_MAX = 3.45; RUNG = 0.15; EYE_R = 4.0; DL_W = 6.0; BOSS_R = 5.0
SEED = dict(bk1=32.0, bk2=48.0, a1max=74.5, smhi=20.0, kK=3.6, law2="lin", kB2=3.6, t12=12.0,
            cr_tilt=14.76, cr_a1=27.56, cr_t1=70.68, cr_a3=13.5, cr_t3=-160.46, cr_zr=0.0,
            s_nose=4.0, r_base=10.84, lift_k=0.86, skirt=12.8, mu=0.087,
            dr_hl=0.0, dl_a=1, dl_h=1, dl_lift=0.0, skinfit=0)
PARAMS = dict(DRM.PARAMS); PARAMS.update(SEED)
for k_ in ("dr_a1", "dr_t1", "dr_a3", "dr_t3", "root_off", "ring_layer", "sector_gap", "arm_up", "dr_zr"): PARAMS.pop(k_, None)


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    p = DRM._LS_CLAMP(p)                                     # parent clamp (dyad, inert RSSR fields)
    p["bk1"] = _c(p["bk1"], 26.0, 40.0); p["bk2"] = _c(p["bk2"], 38.0, 56.0)
    p["a1max"] = min(float(p.get("a1max", 99.0)), float(p["bk1"]) + float(p["bk2"]) - 5.5)
    p["smhi"] = _c(p["smhi"], 12.0, 28.0); p["kK"] = _c(p["kK"], 1.0, 6.0); p["kB2"] = _c(p.get("kB2", p["kK"]), 0.5, 6.0)
    p["t12"] = _c(p.get("t12", 12.0), 1.0, 40.0); p["law2"] = "seg" if str(p.get("law2", "lin")) == "seg" else "lin"
    p["cr_tilt"] = _c(p["cr_tilt"], 14.76, 22.0); p["cr_a1"] = _c(p["cr_a1"], 18.0, 34.0); p["cr_t1"] = _c(p["cr_t1"], -120.0, 120.0)
    p["cr_a3"] = _c(p["cr_a3"], 13.5, 20.0); p["cr_t3"] = _c(p["cr_t3"], -180.0, 180.0); p["cr_zr"] = _c(p.get("cr_zr", 0.0), 0.0, 8.0)
    p["s_nose"] = _c(p["s_nose"], 3.5, 4.5); p["r_base"] = _c(p["r_base"], 10.8, 11.2); p["lift_k"] = _c(p.get("lift_k", 0.86), 0.5, 1.0)
    p["skirt"] = _c(p.get("skirt", 12.8), 11.0, 12.8); p["mu"] = _c(p.get("mu", 0.087), 0.05, 0.3)
    p["dr_hl"] = _c(p.get("dr_hl", 0.0), 0.0, 9.0); p["dl_lift"] = _c(p.get("dl_lift", 0.0), 0.0, 8.0)
    p["dl_a"] = 1 if float(p.get("dl_a", 1)) >= 0 else -1; p["dl_h"] = 1 if float(p.get("dl_h", 1)) >= 0 else -1
    p["skinfit"] = 1 if float(p.get("skinfit", 0)) >= 0.5 else 0
    p["law_mode"] = "seg"; p["law_mode_in"] = "coupler"; p["emb_mode"] = "rod"
    return p


def _strap_lv(a, b, lev, w, step=2.0):
    """underside samples of a spherical strap a -> b (unit dirs), width w, per-section underside levels lev (len n);
    returns (points, section index of each point)"""
    om = math.acos(max(-1, min(1, float(a @ b)))); n = len(lev); t = np.linspace(0, 1, n)[:, None]
    C = (np.sin((1 - t) * om) * a + np.sin(t * om) * b) / max(math.sin(om), 1e-9)
    bn = unit(np.cross(a, b)); rr = np.asarray(lev, float)[:, None]; nw = max(2, int(round(w / step)) + 1); pts = []
    for ww in np.linspace(-w / 2 + 0.5, w / 2 - 0.5, nw):
        pts.append(unit(C + (ww / rr) * bn) * rr)
    return np.concatenate(pts), np.tile(np.arange(n), nw)


def crank_axis(D):
    u2, uK = D.u[1], D.uK; ax = unit(np.cross(u2, uK))
    return unit(S.rotm(ax, math.radians(float(D.p["cr_tilt"])))[0] @ u2)


def crank4r(D):
    """stage-2 table on the design D (cached): K grid (rad), signed crank angle phi (rad), push = s_c phi (the nose-lug
    side is chosen so the lobe pushes the crank the way the 4R needs), max PA (deg), usable end (PA <= 42, push monotone)"""
    if getattr(D, "_cr", None) is not None: return D._cr
    P = D.p; uK = D.uK; sp = float(np.sign(D.psiA)) or 1.0; dR = crank_axis(D)
    c1_0 = DRM.pin_dir(dR, uK, float(P["cr_a1"]), float(P["cr_t1"])); c2_0 = DRM.pin_dir(uK, dR, float(P["cr_a3"]), float(P["cr_t3"]))
    res = DRM.solve4r(dR, uK, sp, c1_0, c2_0, kmax=88.0)
    out = dict(ok=False, sp=sp, dR=dR, c1_0=c1_0, c2_0=c2_0, why="no_closure", s_c=1.0)
    if res is not None:
        K, PH, PA = res["K"], res["phi"], res["pa"]
        s_c = float(np.sign(PH[1])) or 1.0; push = s_c * PH
        good = (PA <= PA_GATE) & np.concatenate([[True], np.diff(push) > 1e-9])
        n = int(np.argmin(good)) if not good.all() else len(good)
        why = "table_end" if n == len(good) else ("pressure" if PA[n] > PA_GATE else "direction")
        if n >= 3:
            out.update(ok=True, K=K[:n], phi=PH[:n], push=push[:n], pa=PA[:n], why=why, k_end=float(K[n - 1]), s_c=s_c)
        else:
            out["why"] = why
    D._cr = out
    return out


def cp_law(self):
    """FLDesign.law replaced: |dK| = kK t (or two slopes kK / kB2 at t12, 'seg'), gated per t by the parents' rules (th
    monotone, rate <= 3.45, no lift-off, stop B) + the stage-2 table end + stage 1 on the real follower (lobe radius
    r_base + lift_k s_nose phi <= skirt, lobe PA atan(d lift/dt / r) <= 42 - atan(mu))"""
    if getattr(self, "_law", None) is not None: return self._law
    P = self.p; u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
    cr = crank4r(self); sg = self.q2sgn; q2hi = self._q2_at(self.th_hi, sg)

    def th3(q): return math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
    s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
    cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (
        math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
    dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))
    ts = np.radians(np.arange(0.0, 60.0 + 1e-6, 0.1))
    if P.get("law2") == "seg":
        t1 = float(P["t12"]) * D2R; kabs = float(P["kK"]) * np.minimum(ts, t1) + float(P["kB2"]) * np.maximum(0.0, ts - t1)
    else:
        kabs = float(P["kK"]) * ts
    if cr["ok"]:
        k_end = float(cr["k_end"]); phi = np.interp(np.minimum(kabs, k_end), cr["K"], cr["push"])
    else:
        k_end = 0.0; phi = np.zeros(len(ts))
    lift_mm = float(P["lift_k"]) * float(P["s_nose"]) * phi; r_t = float(P["r_base"]) + lift_mm
    pa1 = np.degrees(np.arctan(np.gradient(lift_mm, ts) / r_t)); pa1_cap = PA_GATE - math.degrees(math.atan(float(P["mu"])))
    q2t = q2hi + s_q * ts

    def th_of(tt, kk):
        R = S.rotm(uK, sp * np.asarray(kk)); R2_ = S.rotm(u2, q2hi + s_q * np.asarray(tt))
        return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2_, u3)) @ u1, -1, 1)))

    def a1e_of(kk):
        return np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", S.rotm(uK, sp * np.asarray(kk)), u2) @ u1, -1, 1)))
    th = th_of(ts, kabs); a1e = a1e_of(kabs)
    dth = np.gradient(th, ts); dk = np.gradient(kabs, ts); h = 1e-4
    a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
    sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k)
    lift = (sC > 1e-9) & (sC < dk - 1e-9)
    rate = 1.0 / np.maximum(np.radians(dth), 1e-12)
    table = kabs <= k_end + 1e-9; lobe_pa = pa1 <= pa1_cap + 1e-9; skirt = r_t <= float(P["skirt"]) + 1e-9
    good = (dth > 0) & (rate <= RATE_MAX) & ~lift & (kabs <= dKB + 1e-9) & table & lobe_pa & skirt
    good[0] = True
    nval = int(np.argmin(good)) if not good.all() else len(good)
    why_end = "t_end"
    if nval < len(good):
        j = nval
        why_end = ("rate" if not (dth[j] > 0 and rate[j] <= RATE_MAX) else "liftoff" if lift[j] else "stopB" if kabs[j] > dKB + 1e-9
                   else ("table:" + cr["why"]) if not table[j] else "lobe_pa" if not lobe_pa[j] else "skirt" if not skirt[j] else "sign")
    m3 = KR.dyad_margin(th, a1e, self.a2)
    self._law = dict(ok=nval > 1 and cr["ok"], side=0.0, Lt=0.0, p0=u2.copy(), ts=ts[:nval], q2t=q2t[:nval], dK=sp * kabs[:nval], th=th[:nval],
                     pa=pa1[:nval], r_c=np.zeros(nval), rate=rate[:nval], emb="rod", q2hi=q2hi, s_q=s_q, why_end=why_end, s_m=1.0,
                     dK_max=float(np.degrees(kabs[:nval].max())) if nval else 0.0, t_max=float(np.degrees(ts[nval - 1])) if nval else 0.0,
                     th_max=float(th[nval - 1]) if nval else None, phi_t=None, dKB=float(np.degrees(dKB)),
                     lobe_r_max=float(r_t[:nval].max()) if nval else None, lift_max=float(lift_mm[:nval].max()) if nval else 0.0,
                     lobe_pa_max=float(pa1[:nval].max()) if nval else 0.0, lobe_pa_cap=pa1_cap,
                     crank_phi_max=float(np.degrees(phi[:nval].max())) if nval else 0.0,
                     m3e_min=float(m3[:nval].min()) if nval else None, k_max=float(dk[:nval].max()) if nval else 0.0, name="coupler")
    return self._law


FL.FLDesign.law = cp_law


class CPModel(DRM.DRModel):
    """per-pose bodies: 9 = bell crank (boss + long arm + tip eye; turns about dR by phi(K)), 8 = coupler (spherical
    rotation carrying (c1_0, c2_0) to (c1, c2)); horn on member 1 (link 1a)"""
    def _rod_metal(self):
        D = self.D; P = D.p; u1, u2, u3 = D.u; uK = D.uK; fK, f2 = float(self.fK), float(self.f[1])
        cr = crank4r(D); sp = cr["sp"]; dR = cr["dR"]; c1_0, c2_0 = cr["c1_0"], cr["c2_0"]
        L1b = self.link_pts["L1b"][1]; L1bU = unit(L1b); L1bN = np.linalg.norm(L1b, axis=1)
        near = L1b[np.argsort(np.linalg.norm(L1bU - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max())
        zboss = lev + S.T_LINK + RUNG                        # boss underside on link 1b's top (sidecar stacking rule)
        e, f = S.frame_of(dR); dd = S.disc(BOSS_R, 2.0)
        boss = dR * zboss + dd[:, :1] * e + dd[:, 1:] * f
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        boss_cyl = np.concatenate([dR * z + BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(zboss, zboss + 6.0, 4)])
        push_end = float(cr["push"][-1]) if cr["ok"] else 0.0; s_c = cr["s_c"]
        WOK = S.W_LINK / 2 + 1.0
        om = math.acos(max(-1, min(1, float(dR @ c1_0)))); na = max(3, int(62.0 * om / 2.0) + 1); ta = np.linspace(0, 1, na)[:, None]
        Ca = (np.sin((1 - ta) * om) * dR + np.sin(ta * om) * c1_0) / max(math.sin(om), 1e-9); bna = unit(np.cross(dR, c1_0))
        ws_ = np.array([-2.5, -0.83, 0.83, 2.5])
        dirs = np.stack([unit(Ca + (w / 62.0) * bna) for w in ws_], 1)          # (na, 4, 3)
        beside = np.ones(na, bool)
        for ph in np.linspace(0.0, s_c * push_end, 9):
            Dp = dirs.reshape(-1, 3) @ S.rotm(dR, ph)[0].T
            dd_ = (np.arccos(np.clip(Dp @ L1bU.T, -1, 1)) * L1bN[None, :]).min(1).reshape(na, 4)
            beside &= dd_.min(1) >= WOK
        jn = np.argmin(np.arccos(np.clip(Ca.reshape(-1, 3) @ L1bU.T, -1, 1)), axis=1); base = L1bN[jn]
        lvl = np.where(beside, base + float(P["cr_zr"]), base + S.T_LINK + 1.0)
        rr_ = np.array([math.acos(max(-1, min(1, float(c @ dR)))) * zboss for c in Ca])
        lvl = np.where(rr_ <= BOSS_R + 1.0, zboss, lvl)                          # the arm root is the boss's own body
        sarc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Ca, axis=0), axis=1) * 62.0)])
        k = math.tan(S.RAMP * D2R)
        lvl = np.max(lvl[None, :] - k * np.abs(sarc[:, None] - sarc[None, :]), axis=1)
        lvK = fK + float(P["dr_hl"]); ek = unit(c2_0 - (c2_0 @ uK) * uK); bk = unit(np.cross(uK, ek))
        rh = float(lvK * math.tan(math.radians(float(P["cr_a3"]))))
        horn = np.array([uK * lvK + r_ * ek + w_ * bk for r_ in np.arange(S.HUB_R + 0.5, rh + EYE_R + 1e-6, 2.0) for w_ in (-3.0, -1.0, 1.0, 3.0)])
        la0 = float(lvl[-1]) + float(P["dl_a"]) * (S.T_LINK + RUNG) + float(P["dl_lift"]); lh0 = lvK + float(P["dl_h"]) * (S.T_LINK + RUNG) + float(P["dl_lift"])
        omc = math.acos(max(-1, min(1, float(unit(c1_0) @ unit(c2_0))))); ncs = max(2, int(0.5 * (la0 + lh0) * omc / 2.0) + 1)
        lvc = la0 + (lh0 - la0) * np.linspace(0, 1, ncs)
        root_keep = (np.linalg.norm(unit(dirs.reshape(-1, 3)) - dR, axis=1) * zboss > BOSS_R - 0.5)

        def build(lvl_, lvc_):
            arm_ = (dirs * lvl_[:, None, None]).reshape(-1, 3)[root_keep]; sec_a = np.repeat(np.arange(na), 4)[root_keep]
            tip_ = DRM._disc(unit(c1_0), float(lvl_[-1]), EYE_R)
            dl_, sec_c = _strap_lv(unit(c1_0), unit(c2_0), lvc_, DL_W)
            eyes_ = np.concatenate([DRM._disc(unit(c1_0), float(lvc_[0]), EYE_R), DRM._disc(unit(c2_0), float(lvc_[-1]), EYE_R)])
            return arm_, sec_a, tip_, dl_, sec_c, eyes_
        arm, sec_a, tip_eye, dl, sec_c, eyes = build(lvl, lvc)
        self._scg = dict(PV=dR * zboss, dR=dR, tip0=c1_0 * float(lvl[-1]), H0=c2_0 * lvK, uK=uK, sp=sp, dog=cr)
        self._sc = None
        fitlog = None
        if int(P.get("skinfit", 0)) and getattr(self, "B", None) is not None and cr["ok"]:
            # SKIN-FITTED drive levels (the chain's own rule: a rigid part clears the highest skin it passes over on the FIT
            # bench's poses, 1 mm): per arm / coupler section the radial raise that keeps every sample >= 1 mm off the skin
            # on every kinematically closed fit pose inside the 4R table, sphere-traced (3 passes; a sample needing > 25 mm
            # in a pose leaves that pose to the contact count); eyes on one pin move together (stack order kept); 60-deg ramps
            Bf = self.B; dKp_ = np.abs(np.asarray(self.dK, float)); kin_ = np.asarray(self.kin_ok, bool)
            kend = float(cr["K"][-1]); poses = [i for i in range(len(Bf.idx)) if kin_[i] and dKp_[i] <= kend + 1e-9]
            ra = np.zeros(na); rc = np.zeros(len(lvc)); CLR, LMAX = 1.0, 25.0
            for it in range(3):
                lvl_t = lvl + ra; lvc_t = lvc + rc
                arm_t, sec_a_t, tip_t, dl_t, sec_c_t, eyes_t = build(lvl_t, lvc_t)
                self.rigid["crank"] = (9, np.concatenate([arm_t, tip_t])); self.rigid["rod"] = (8, np.concatenate([dl_t, eyes_t])); self._sc = None
                Xa = self.rigid["crank"][1]; Xc = self.rigid["rod"][1]
                sa = np.concatenate([sec_a_t, np.full(len(tip_t), na - 1)]); nde = len(eyes_t) // 2
                sc_ = np.concatenate([sec_c_t, np.zeros(nde, int), np.full(len(eyes_t) - nde, len(lvc) - 1)])
                na_ = np.zeros(na); nc_ = np.zeros(len(lvc))
                for i in poses:
                    da = CLR - Bf.dist(i, self.world(9, i, Xa)); dc = CLR - Bf.dist(i, self.world(8, i, Xc))
                    da = np.where(da > LMAX, 0.0, da); dc = np.where(dc > LMAX, 0.0, dc)
                    np.maximum.at(na_, sa, da); np.maximum.at(nc_, sc_, dc)
                stp_a = np.maximum(na_, 0.0); stp_c = np.maximum(nc_, 0.0)
                if stp_a.max() < 0.05 and stp_c.max() < 0.05: break
                ra = ra + stp_a; rc = rc + stp_c
                rr2 = np.array([math.acos(max(-1, min(1, float(c @ dR)))) * zboss for c in Ca]); ra = np.where(rr2 <= BOSS_R + 1.0, 0.0, ra)
                # one pin, one stack: the arm-tip eye and the coupler's c1 eye rise together; the horn end keeps its order
                tip_need = max(ra[-1], rc[0]); ra[-1] = tip_need; rc[0] = tip_need
                if int(P["dl_h"]) < 0: rc[-1] = 0.0
                sa_arc = sarc; ra = np.max(ra[None, :] - k * np.abs(sa_arc[:, None] - sa_arc[None, :]), axis=1)
                carc = np.linspace(0, 1, len(lvc)) * omc * 0.5 * (la0 + lh0)
                rc = np.max(rc[None, :] - k * np.abs(carc[:, None] - carc[None, :]), axis=1)
            lvl = lvl + ra; lvc = lvc + rc
            arm, sec_a, tip_eye, dl, sec_c, eyes = build(lvl, lvc)
            fitlog = dict(arm_raise_max=round(float(ra.max()), 2), cpl_raise_max=round(float(rc.max()), 2), n_poses=len(poses))
            self._scg["tip0"] = c1_0 * float(lvl[-1])
        lv_tip = float(lvl[-1]); la, lh = float(lvc[0]), float(lvc[-1])
        arm_mid = (dirs * (lvl[:, None, None] + 1.5)).reshape(-1, 3)
        crank = np.concatenate([boss, arm, tip_eye])
        dl_all = np.concatenate([dl, eyes]); dl_mid = dl_all + 1.5 * unit(dl_all)
        self._skinfit = fitlog
        self._sc = None
        self.rigid["crank"] = (9, crank)
        self.rigid["rod"] = (8, dl_all)
        self.rigid["horn"] = (1, horn)
        self.rigid.pop("rodends", None); self.rigid.pop("rocker", None)
        self._contact_only(); self._solids()
        self.contact.append((8, dl_all + S.T_LINK * unit(dl_all)))
        self.contact.append((9, np.concatenate([boss_cyl, arm + S.T_LINK * unit(arm), tip_eye + S.T_LINK * unit(tip_eye)])))
        self.contact.append((1, horn + S.T_LINK * uK))
        self.strap["ROD"] = (8, dl_mid)
        self.strap["CRK"] = (9, np.concatenate([boss_cyl, arm_mid, tip_eye + 1.5 * unit(tip_eye)]))
        self.strap["HORN"] = (1, horn + 1.5 * uK)
        self._crown_ok = True
        # ---- the drive's own range: the table end (PA / branch / direction), then clearances swept in link 1b's frame
        lim, why_lim = (float(cr["K"][-1]), "pa/table:" + cr["why"]) if cr["ok"] else (0.0, cr["why"])
        mem2, cen2, ax2 = self.cyl["hub2"]; r2 = self.cyl_r["hub2"]; memK, cenK, axK = self.cyl["hubK"]; rK = self.cyl_r["hubK"]
        L1bS = self.strap["L1b"][1]

        def farX(X, cen, ax, r, pad): w = X - cen; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > r + pad]
        L1b_farB = farX(farX(L1bS, cen2, ax2, r2, 4.0), cenK, axK, rK, 1.0); treeB = cKDTree(L1b_farB) if len(L1b_farB) else None
        boss_hub2 = float(self.sd_cyl(boss_cyl, cen2, ax2, r=r2).min())
        clr = dict(boss_hub2=round(boss_hub2, 2), arm_hub2=99.0, arm_hubK=99.0, dl_hubK=99.0, dl_hub2=99.0, dl_L1b=99.0, horn_L1b=99.0)
        if boss_hub2 < 1.0 - 0.02: lim, why_lim = 0.0, "boss_hub2"     # 0.02: sampling round-off of the 1 mm seat rule
        elif cr["ok"]:
            Kt = cr["K"]; PHt = cr["phi"]; armX = np.concatenate([arm_mid, tip_eye + 1.5 * unit(tip_eye)])
            for j in range(0, len(Kt), 4):
                kk = float(Kt[j]); Rr = S.rotm(dR, float(PHt[j]))[0]
                c1 = Rr @ c1_0; c2 = S.rotm(uK, sp * kk)[0].T @ c2_0
                Rd = self._dl_rot(c1_0, c2_0, c1, c2)
                AR = armX @ Rr.T; DL = dl_mid @ Rd.T
                HN = (horn + 1.5 * uK) @ S.rotm(uK, sp * kk)[0]
                ARf = farX(AR, cen2, ax2, r2, 6.5)
                DLf = farX(farX(DL, cen2, ax2, r2, 4.0), cenK, axK, rK, 1.0); HNf = farX(HN, cenK, axK, rK, 1.0)
                c_ = dict(arm_hub2=float(self.sd_cyl(ARf, cen2, ax2, r=r2).min()) if len(ARf) else 99.0,
                          arm_hubK=float(self.sd_cyl(AR, cenK, axK, r=rK).min()),
                          dl_hubK=float(self.sd_cyl(DL, cenK, axK, r=rK).min()), dl_hub2=float(self.sd_cyl(DL, cen2, ax2, r=r2).min()),
                          dl_L1b=float(treeB.query(DLf)[0].min()) - S.T_LINK if treeB is not None and len(DLf) else 99.0,
                          horn_L1b=float(treeB.query(HNf)[0].min()) - S.T_LINK if treeB is not None and len(HNf) else 99.0)
                for k_, v in c_.items(): clr[k_] = min(clr[k_], v)
                bad = [k_ for k_, v in c_.items() if v < 1.0]
                if bad:
                    lim = float(Kt[max(j - 4, 0)]) if j > 0 else 0.0; why_lim = bad[0]; break
        self._scg.update(dK_lim=lim, why_lim=why_lim, kgrid=cr["K"] if cr["ok"] else np.zeros(2), phig=cr["phi"] if cr["ok"] else np.zeros(2))
        dKp = np.abs(np.asarray(self.dK, float)); taken = np.asarray(self.kin_ok, bool) & (dKp > 1e-9)
        kmax_t = float(dKp[taken].max()) if taken.any() else 0.0
        pa_max_t = float(cr["pa"][cr["K"] <= min(kmax_t, lim) + 1e-9].max()) if cr["ok"] else 0.0
        gK = np.gradient(cr["K"], np.abs(cr["phi"]) + 1e-12) if cr["ok"] else np.zeros(2)
        L_ = D.law()
        self._sc_info = dict(dK_lim=round(math.degrees(lim), 1), why_lim=why_lim, rssr_closed=bool(cr["ok"]), crest_exact=0.0,
                             pa_max_taken=round(pa_max_t, 1), ratio_range=[round(float(np.percentile(gK[1:], 2)), 2), round(float(np.percentile(gK[1:], 98)), 2)] if cr["ok"] else None,
                             phi_max_taken=round(math.degrees(float(np.interp(kmax_t, cr["K"], np.abs(cr["phi"])))) if cr["ok"] else 0.0, 1),
                             boss_level=round(zboss, 1), lev_L1b=round(lev, 1), arm_beside=round(float(beside.mean()), 2), arm_tip_level=round(lv_tip, 1),
                             dl_levels=[round(la, 1), round(lh, 1)], horn_level=round(lvK, 1), r_h=round(rh, 2),
                             dl_len=round(math.degrees(math.acos(max(-1, min(1, float(c1_0 @ c2_0))))) * 0.5 * (la + lh) * D2R, 1),
                             arm_len=round(float(sarc[-1]), 1), clear_min={k_: round(v, 2) for k_, v in clr.items()}, table_why=cr["why"],
                             table_end=round(math.degrees(float(cr.get("k_end", 0.0))), 1), trans_min_taken=round(90.0 - pa_max_t, 1),
                             lobe_pa_max=round(float(L_.get("lobe_pa_max", 0.0)), 1), lobe_pa_cap=round(float(L_.get("lobe_pa_cap", 0.0)), 2),
                             lobe_r_max=round(float(L_.get("lobe_r_max") or 0.0), 2), lift_max=round(float(L_.get("lift_max", 0.0)), 2),
                             crank_phi_max=round(float(L_.get("crank_phi_max", 0.0)), 1), law_end=L_.get("why_end"), skinfit=getattr(self, "_skinfit", None))
        self._rod_info = self._sc_info
        if LS.GHOST: self._ghost()
        self._viz_rod = dict(ring=dR * zboss, ringAx=dR, armA=dR * zboss, armB=c1_0 * lv_tip, rodA=c1_0 * la, rodB=c2_0 * lh, horn=c2_0 * lvK)


SC.SCModel = CPModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; LS.RF.PARAMS = PARAMS; LS.BM.PARAMS = PARAMS
FL.G.KR.KB.KModel = CPModel; FL.FLModel_SC = CPModel
LS.LSModel = CPModel; LS._clamp = _clamp; LS.PARAMS = PARAMS; LS.CELL = "coupler"
_LS_REPORT = DRM._LS_REPORT
DRIVE_PARTS = ("crank", "rod", "horn")


def kopen_drive_contacts(M, B, thr=20.0):
    """per taken-or-contact pose with |dK| > thr: does the DRIVE metal (crank, coupler, horn) go under the skin (< 0) or
    within 1 mm; counted on workspace poses (the kill rule) and clip frames"""
    lim = math.degrees(float(M._scg.get("dK_lim", 0.0))) if getattr(M, "_scg", None) else 0.0
    dKp = np.degrees(np.abs(np.asarray(M.dK, float))); kin = np.asarray(M.kin_ok, bool); out = dict(ws_contact=0, ws_near1=0, clip_contact=0, n_open=0, deepest=0.0, poses=[])
    for i in range(len(B.idx)):
        if not kin[i] or dKp[i] <= thr or dKp[i] > lim + 1e-6: continue
        out["n_open"] += 1; mn = 99.0
        for nm in DRIVE_PARTS:
            if nm in M.rigid and len(M.rigid[nm][1]):
                m, X = M.rigid[nm]; mn = min(mn, float(B.dist(i, M.world(m, i, X)).min()))
        if mn < 0:
            out["ws_contact" if B.kind[i] == "ws" else "clip_contact"] += 1; out["deepest"] = max(out["deepest"], -mn)
            if B.kind[i] == "ws": out["poses"].append(dict(i=i, dK=round(float(dKp[i]), 1), d=round(mn, 2), **{k: B.poses[i][k] for k in ("plane", "elev", "axial")}))
        elif mn < 1 and B.kind[i] == "ws": out["ws_near1"] += 1
    out["deepest"] = round(out["deepest"], 2)
    return out


def drive_inband(M, B):
    """pooled in-band 2-14 of each drive part over the clip frames the bench counted (taken), as the bench reads it"""
    acc = {}
    for i in range(len(B.idx)):
        if B.kind[i] != "clip" or B.res[i] is None or float(np.min(B.res[i])) < 0: continue
        for nm in DRIVE_PARTS:
            if nm in M.rigid and len(M.rigid[nm][1]):
                m, X = M.rigid[nm]; acc.setdefault(nm, []).append(B.dist(i, M.world(m, i, X)))
    out = {nm: round(float(((np.concatenate(v) >= 2) & (np.concatenate(v) <= 14)).mean()), 3) for nm, v in acc.items()}
    if acc:
        al = np.concatenate([np.concatenate(v) for v in acc.values()]); out["drive_all"] = round(float(((al >= 2) & (al <= 14)).mean()), 3)
    return out


def _report(B, params):
    r, M = _LS_REPORT(B, dict(params))
    info = getattr(M, "_sc_info", None) or {}
    r["cam"] = {k: info.get(k) for k in ("dK_lim", "why_lim", "pa_max_taken", "ratio_range", "phi_max_taken", "boss_level", "arm_beside",
                                         "arm_tip_level", "dl_levels", "horn_level", "r_h", "dl_len", "arm_len", "clear_min", "table_why",
                                         "table_end", "lobe_pa_max", "lobe_pa_cap", "lobe_r_max", "lift_max", "crank_phi_max", "law_end", "skinfit")}
    L_ = M.D.law(); r["law"] = dict(why_end=L_.get("why_end"), dK_max=round(L_.get("dK_max", 0.0), 1), th_max=L_.get("th_max"))
    if not info.get("rssr_closed", False): r["honest"] = False; r["drive_fail"] = info.get("why_lim")
    try:
        r["kopen"] = kopen_drive_contacts(M, B); r["drive_ib14"] = drive_inband(M, B)
    except Exception as e: r["kopen"] = dict(error=repr(e)[:200])
    return r, M


LS._report = _report
KOPEN_W = float(os.environ.get("CP_KOPEN_W", "2.0"))       # search objective: near1 gap + this x (K-open ws drive contacts / n_ws) x 100


REPORT_KEYS = ("plain", "gap_plain", "gap_near1", "gap_near2", "min_metal_mm", "why", "cam", "law", "overhead140", "kopen", "drive_ib14", "obj")


def _obj(B, r):
    """the search objective (round-11 plan, lens 1): the 1 mm near-touch gap + a K-open term (K-open workspace poses
    whose DRIVE metal is under the skin or within 1 mm, counted KOPEN_W times as lost poses)"""
    nws = max(1, sum(1 for k in B.kind if k == "ws")); ko = r.get("kopen") or {}
    base = r.get("gap_near1") if r.get("gap_near1") is not None else r["gap"]
    return float(base) + KOPEN_W * 100.0 * float(ko.get("ws_contact", 0) + ko.get("ws_near1", 0)) / nws


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("drive_fail") or r.get("sidecar_fail") or r.get("knee_moved"): r["honest"] = False
    r["gap_plain"] = r["gap"]; r["obj"] = _obj(B, r); r["gap"] = r["obj"]          # CMA minimises r["gap"]: the objective
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); r["drive_kind"] = "coupler"
    r["obj"] = _obj(B, r)
    if r.get("honest") is False: r["gap_honest"] = r["gap"]; r["gap"] = max(float(r["gap"]), 150.0); r["obj"] = max(r["obj"], 150.0)
    return r


gate = LS.gate; frozen = LS.frozen; frozen_held = LS.frozen_held; frozen_flood = LS.frozen_flood; th_margin = LS.th_margin


_CAP = {}
_ORIG_FM = LS._frozen_model


def _fm_capture(P, nc, nw):
    res = _ORIG_FM(P, nc, nw); _CAP["res"] = res; return res


LS._frozen_model = _fm_capture


def frozen_plus(P, nc=110, nw=360):
    """the family's frozen claim (LS.frozen) + this row's kill readings on the SAME frozen model (K-open drive contacts,
    drive in-band)"""
    out = LS.frozen(P, nc, nw); fit, M1, M, B, r = _CAP["res"]
    out["kopen"] = kopen_drive_contacts(M, B); out["drive_ib14"] = drive_inband(M, B)
    return out


def synth(par, n=8000, seed=3):
    """re-synthesise stage 2 on THIS fit's own u2 / uK / dR (the proposer's seeds came from another fit): random pins,
    PA <= 42 and crank monotone to >= 77 deg of K, horn arc a3 >= 13.5, arm arc 22-32, report g and the arm side"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, _clamp(dict(PARAMS, **par))); D = M.D
    uK = D.uK; dR = crank_axis(D); sp = float(np.sign(D.psiA)) or 1.0
    rng = np.random.default_rng(seed); rows = []
    a1 = rng.uniform(22, 32, n); t1 = rng.uniform(-120, 120, n); a3 = rng.uniform(14.7, 19.0, n); t3 = rng.uniform(-180, 180, n)
    for i in range(n):
        c1 = DRM.pin_dir(dR, uK, a1[i], t1[i]); c2 = DRM.pin_dir(uK, dR, a3[i], t3[i])
        cpl = math.degrees(math.acos(max(-1, min(1, float(c1 @ c2)))))
        if cpl < 8 or cpl > 45: continue
        res = DRM.solve4r(dR, uK, sp, c1, c2, kmax=80.0, dk=1.0)
        if res is None or math.degrees(res["K"][-1]) < 77: continue
        n77 = int(np.searchsorted(np.degrees(res["K"]), 77.0)) + 1
        PH = res["phi"]; s_c = float(np.sign(PH[1])) or 1.0; push = s_c * PH
        good = ((res["pa"] <= PA_GATE) & np.concatenate([[True], np.diff(push) > 1e-9]))[:n77]
        if not good.all(): continue
        g = 75.0 / max(math.degrees(float(np.interp(75.0, np.degrees(res["K"]), push))), 1e-6)
        rows.append(dict(cr_a1=round(float(a1[i]), 2), cr_t1=round(float(t1[i]), 2), cr_a3=round(float(a3[i]), 2), cr_t3=round(float(t3[i]), 2),
                         cpl=round(cpl, 1), g=round(g, 2), pa=round(float(res["pa"][:n77].max()), 1)))
    rows.sort(key=lambda d: -d["g"])
    return dict(n=len(rows), rows=rows)


def viz_export(par):
    """geometry for docs/concepts/viz/concepts/coupler-longdyad-knuckle-3r.js: the chain + crank (dR) / coupler / horn"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, _clamp(dict(PARAMS, **par))); D = M.D; P = D.p; L_ = D.law()
    R = lambda v, n=5: [round(float(x), n) for x in v]

    def pts(name, step=3):
        X = M.link_pts[name][1]; return [R(x, 2) for x in X[::step]]
    sub = slice(None, None, 8); vr = M._viz_rod; cr = M._scg["dog"]
    G_ = dict(u=[R(x) for x in D.u], c=[R(x) for x in D.c], uK=R(D.uK), sa=R(D.sa), st=R(D.st), sn=R(D.sn), A=[round(D.a1, 3), round(D.a2, 3)],
              branch=float(D.branch), m=R(D.m), f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), capK=float(P.get("capK", 0)),
              tr=round(float(M.tr), 2), tp=round(float(P["tp"]), 3), RUN=S.RUN, A0=R(M.fr["A0"]), A0m=R(M.fr["A0m"]), Bm=R(M.fr["Bm"]), eE=R(M.fr["eE"]),
              psiA=round(math.degrees(D.psiA), 4), thLo=round(D.th_lo, 4), thHi=round(D.th_hi, 4), q2s=[round(x, 4) for x in D.q2_stops],
              lawTh=R(L_["th"][sub], 3), lawDK=R(np.degrees(L_["dK"][sub]), 3), lawQ2=R(np.degrees(L_["q2t"][sub]), 3), emb="rod",
              dogK=R(np.degrees(cr["K"][::8]), 3) if cr["ok"] else [0, 1], dogPhi=R(np.degrees(cr["phi"][::8]), 3) if cr["ok"] else [0, 0],
              dKlim=round(math.degrees(float(M._scg["dK_lim"])), 2), crankAx=R(vr["ringAx"]), boss=R(vr["ring"], 3), armA=R(vr["armA"], 3), armB=R(vr["armB"], 3),
              rodA=R(vr["rodA"], 3), rodB=R(vr["rodB"], 3), horn=R(vr["horn"], 3), hornRoot=R(D.uK * (float(M.fK) + float(P["dr_hl"])) + 10.5 * unit(vr["horn"] - (vr["horn"] @ D.uK) * D.uK), 3),
              L1a=pts("L1a"), L1b=pts("L1b"), L2=pts("L2", 6))
    keys = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "bk1", "bk2", "a1max", "smhi", "smlo", "capK",
            "kK", "cr_tilt", "cr_a1", "cr_t1", "cr_a3", "cr_t3", "cr_zr", "s_nose", "r_base", "dr_hl", "dl_a", "dl_h", "dl_lift")
    return dict(P={k: P[k] for k in keys if k in P}, G=G_, report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}, plain=r.get("plain"))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "synth":
        out = synth(par, n=int(os.environ.get("CP_SYN_N", "8000")), seed=int(os.environ.get("CP_SYN_SEED", "3"))); print(json.dumps(dict(n=out["n"], top=out["rows"]))); sys.exit()
    if mode == "gate":
        t = time.time(); out = gate(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time()
        if mode == "flood": out = frozen_flood(par)
        else:
            nc, nw = (-1, -1) if mode == "held" else (110, 360)
            out = frozen_plus(par, nc, nw)
        out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), depth={k: v for k, v in (out.get("contact_depth") or {}).items() if k != "per_pose"},
                              kopen={k: v for k, v in (out.get("kopen") or {}).items() if k != "poses"}, drive_ib14=out.get("drive_ib14"), split=out.get("split"),
                              th_margin=out.get("th_margin"), connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), ovh=r.get("overhead140"), cam=r.get("cam"), law=r.get("law"), parts=r.get("parts_ib14"),
                          kopen={k: v for k, v in (r.get("kopen") or {}).items() if k != "poses"}, drive_ib14=r.get("drive_ib14"),
                          clear=getattr(M, "last_clear", None), secs=round(time.time() - t, 1)), default=float))

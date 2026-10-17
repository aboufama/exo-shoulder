"""dogring-draglink-knuckle-3r (round 11, 2026-10-17): the slipper-nose lead's chain (stop A, a2, b3 tilt, pin knee, seats
frozen at the verified values) on a LONG K dyad (34/46, 32/48, 36/44, 38/42; stop B a1max = bk1 + bk2 - 5.5), with the
lead's lobe / bell crank / nose / flank deleted and a POSITIVE coaxial drive in their place:

  * a DOG SECTOR (17-4PH C-ring sector, 3 mm, r 10.2-12.5) turning on hub 2's O20 housing IN LINK 1B'S OWN LAYER (the
    hub's skin-face layer f2 .. f2 + 3), with a C-gap that clears link 1b's root over the whole swing;
  * the DOG is link 2's own root flank (its leading edge in the stretch direction at r 11-13, where link 2 ramps down
    through that layer) - or an O3 dowel at the same place; it meets the sector's end face at the onset th_hi = a1 + a2 -
    smhi and turns the sector 1:1 with q2 past it (same axis: PA 0, no sliding, no lobe); folded side: link 2 walks away;
  * an integral Ti ARM (6 x 3) leaves the sector's far end and runs BESIDE link 1b at link 1b's own level (sidecar rule:
    >= W_LINK / 2 + 1 off its strap over the whole swing, else stacked + 3.15) to an O9 eye at c1 (arc a1, azimuth t1
    about u2 from the u2 -> uK great circle, root azimuth offset root_off);
  * a spherical DRAG LINK (Ti 6 x 3, O9 eyes on 2 x MR63ZZ, radial O3 pins - every axis through GH) from c1 to a HORN pin
    c2 on link 1a at hub K (arc a3 from uK = r_h, azimuth t3). Spherical 4R: ring (u2) - arm - drag link - horn (uK);
    K = K(phi) by continuation, phi = (q2 - q2hi) past the onset.

3 ACTIVE DOF (J1, J2, J3 encoded); K slaved (on stop A, or set by q2 through the dog), never read; 0 passive
translations; no gears, pulleys, cables; one spring (K's spiral spring, the lead's). The sector is parked by the drag link
while K rests on stop A, so no coordinate is undetermined (R17).

Layering (the judge's main risk, priced POOLED by the bench itself - every drive point is a rigid part sample):
  ring_layer 0: sector in hub 2's skin-face layer (f2), link 1b's layer (this build); 1: the spec's control - but the spec's
  'link 1b top + 0.15' at hub 2 IS link 2's root layer (f2 + 3.15), which link 2 sweeps over its whole q2 range, so the
  honest stacked control sits above link 2's root: f2 + 6.3 (inside the 12.25 housing).
  dl_a / dl_h: drag link above (+1) or below (-1) the arm-tip eye / the horn eye; the strap joggles between the two ends.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/dogring-draglink-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json];  ... gate '<json>'
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

os.environ["LS_DRIVE"] = "rssr"                              # the SC (per-pose drive bodies 8 / 9, _truncate) path of the parent
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "dogring-draglink-knuckle-3r"
_sp = importlib.util.spec_from_file_location("longstroke_for_dogring", os.path.join(HERE, "longstroke-slipper-knuckle-3r.py"))
LS = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(LS)
SC, FL, PK, S, RL = LS.SC, LS.SC.FL, LS.PK, LS.S, LS.RL
SCBase = LS.SCBase
KR = FL.KR
unit = S.unit; D2R = math.pi / 180
PA_GATE = 42.0; RATE_MAX = 3.45; RUNG = 0.15; EYE_R = 4.5; ARM_W = 6.0; DL_W = 6.0
RING_RI, RING_RO = 10.2, 12.5

# cell seeds: the judge's 34/46 (spec, arm along link 1b) and the beside-arm synthesis rows (arm on the far side of link 1b)
SEED = dict(bk1=34.0, bk2=46.0, a1max=74.5, smhi=22.0, a1=30.22, t1=61.6, a3=14.53, t3=-9.98, root_off=10.0,
            ring_layer=0, hl=0.0, zr=0.0, dl_a=1, dl_h=1, sector_gap=0.5)
PARAMS = dict(LS.PARAMS); PARAMS.update(SEED)
for k_ in ("La", "r_h", "beta", "gam", "s_arm", "r_lobe", "kK", "kA", "kB"): PARAMS.pop(k_, None)
PARAMS.update(La=20.0, r_h=15.0, beta=-112.0, gam=0.0, s_arm=4.0, r_lobe=7.5, kK=2.0)   # inert: the parent's clamp reads them


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    p = LS._clamp(p)                                         # parent clamp (dyad, inert RSSR fields)
    p["bk1"] = _c(p["bk1"], 26.0, 40.0); p["bk2"] = _c(p["bk2"], 38.0, 56.0)
    p["a1max"] = min(float(p.get("a1max", 99.0)), float(p["bk1"]) + float(p["bk2"]) - 5.5)
    p["smhi"] = _c(p["smhi"], 12.0, 28.0)
    p["a1"] = _c(p["a1"], 20.0, 40.0); p["t1"] = _c(p["t1"], -90.0, 90.0); p["a3"] = _c(p["a3"], 12.0, 20.0)
    p["t3"] = _c(p["t3"], -180.0, 180.0); p["root_off"] = _c(p.get("root_off", 0.0), -30.0, 30.0)
    p["hl"] = _c(p.get("hl", 0.0), 0.0, 3.15); p["zr"] = _c(p.get("zr", 0.0), 0.0, 3.0)
    p["ring_layer"] = int(round(_c(p.get("ring_layer", 0), 0, 1)))
    p["dl_a"] = 1 if float(p.get("dl_a", 1)) >= 0 else -1; p["dl_h"] = 1 if float(p.get("dl_h", 1)) >= 0 else -1
    p["sector_gap"] = _c(p.get("sector_gap", 0.5), 0.15, 3.0)
    p["law_mode"] = "seg"; p["law_mode_in"] = "dog"; p["emb_mode"] = "rod"
    return p


# ---------------------------------------------------------------- spherical 4R (ring on u2 -> arm -> drag link -> horn on uK)
def pin_dir(axis, toward, arc_deg, az_deg):
    axis = unit(axis); t = unit(toward - (toward @ axis) * axis)
    v = math.cos(math.radians(arc_deg)) * axis + math.sin(math.radians(arc_deg)) * t
    return S.rotm(axis, math.radians(az_deg))[0] @ v


def solve4r(a_in, uK, sp, c1_0, c2_0, kmax=88.0, dk=0.25):
    """per K step (deg): ring angle phi (rot(a_in, phi), continuation), PA at both pins; stops at a branch jump / no closure"""
    ca = float(c1_0 @ c2_0); par = (c1_0 @ a_in) * a_in; P = c1_0 - par; Qv = np.cross(a_in, c1_0); prev = 0.0; rows = []
    for k in np.radians(np.arange(0.0, kmax + 1e-9, dk)):
        c2 = S.rotm(uK, sp * k)[0].T @ c2_0
        A, B, C = float(P @ c2), float(Qv @ c2), float(par @ c2); R = math.hypot(A, B)
        if R < 1e-12: break
        x = (ca - C) / R
        if abs(x) > 1: break
        base = math.atan2(B, A); d = math.acos(x); best = None
        for c in (base + d, base - d):
            cc = c + 2 * math.pi * round((prev - c) / (2 * math.pi))
            if best is None or abs(cc - prev) < abs(best - prev): best = cc
        if rows and abs(best - prev) > math.radians(8): break
        prev = best; c1 = S.rotm(a_in, best)[0] @ c1_0
        t1 = unit(c2 - (c2 @ c1) * c1); v1 = unit(np.cross(a_in, c1)); t2 = unit(c1 - (c1 @ c2) * c2); v2 = unit(np.cross(uK, c2))
        pa1 = math.degrees(math.acos(min(1.0, abs(float(t1 @ v1))))); pa2 = math.degrees(math.acos(min(1.0, abs(float(t2 @ v2)))))
        rows.append((k, best, pa1, pa2))
    if len(rows) < 3: return None
    K = np.array([r[0] for r in rows]); PH = np.array([r[1] for r in rows]); PA = np.maximum([r[2] for r in rows], [r[3] for r in rows])
    return dict(K=K, phi=PH, pa=PA, c1_0=c1_0, c2_0=c2_0)


def dog4r(D):
    """the drive's 4R table on the design D (cached): K grid (rad), signed ring angle phi (rad), max PA (deg), usable end
    (PA <= 42, phi monotone in the push direction s_q, no branch jump)"""
    if getattr(D, "_dog", None) is not None: return D._dog
    P = D.p; u1, u2, u3 = D.u; uK = D.uK; sp = float(np.sign(D.psiA)) or 1.0
    c1_0 = pin_dir(u2, uK, float(P["a1"]), float(P["t1"])); c2_0 = pin_dir(uK, u2, float(P["a3"]), float(P["t3"]))
    res = solve4r(u2, uK, sp, c1_0, c2_0)
    sg = D.q2sgn; q2hi = D._q2_at(D.th_hi, sg)

    def th3(q): return math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
    s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
    out = dict(ok=False, s_q=s_q, q2hi=q2hi, sp=sp, c1_0=c1_0, c2_0=c2_0, why="no_closure")
    if res is not None:
        K, PH, PA = res["K"], res["phi"], res["pa"]
        push = s_q * PH                                      # ring turn in the dog's push direction (must grow with K)
        good = (PA <= PA_GATE) & np.concatenate([[True], np.diff(push) > 1e-9])
        n = int(np.argmin(good)) if not good.all() else len(good)
        why = "table_end" if n == len(good) else ("pressure" if PA[n] > PA_GATE else "direction")
        if n >= 3 and push[1] > 0:
            out.update(ok=True, K=K[:n], phi=PH[:n], push=push[:n], pa=PA[:n], why=why, k_end=float(K[n - 1]))
        else:
            out["why"] = "drives_wrong_way" if (len(push) > 1 and push[1] <= 0) else why
    D._dog = out
    return out


def dog_law(self):
    """FLDesign.law replaced: past the onset the ring turns 1:1 with q2 (ring push = t), so K(t) is the 4R table read at
    push = t; the parents' per-t gates (th monotone, rate <= 3.45, no lift-off, stop B) - no lobe pressure / skirt gate"""
    if getattr(self, "_law", None) is not None: return self._law
    P = self.p; u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
    dg = dog4r(self); s_q = dg["s_q"]; q2hi = dg["q2hi"]
    cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (
        math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
    dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))
    if not dg["ok"]:
        ts = np.radians(np.arange(0.0, 0.31, 0.1)); kabs = np.zeros(len(ts))
    else:
        ts = np.radians(np.arange(0.0, math.degrees(float(dg["push"][-1])) + 1e-6, 0.1))
        kabs = np.interp(ts, dg["push"], dg["K"])
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
    good = (dth > 0) & (rate <= RATE_MAX) & ~lift & (kabs <= dKB + 1e-9)
    good[0] = True
    nval = int(np.argmin(good)) if not good.all() else len(good)
    why_end = "table:" + dg["why"]
    if nval < len(good):
        j = nval
        why_end = ("rate" if not (dth[j] > 0 and rate[j] <= RATE_MAX) else "liftoff" if lift[j] else "stopB" if kabs[j] > dKB + 1e-9 else "sign")
    m3 = KR.dyad_margin(th, a1e, self.a2)
    self._law = dict(ok=nval > 1 and dg["ok"], side=0.0, Lt=0.0, p0=u2.copy(), ts=ts[:nval], q2t=q2t[:nval], dK=sp * kabs[:nval], th=th[:nval],
                     pa=np.zeros(nval), r_c=np.zeros(nval), rate=rate[:nval], emb="rod", q2hi=q2hi, s_q=s_q, why_end=why_end, s_m=1.0,
                     dK_max=float(np.degrees(kabs[:nval].max())) if nval else 0.0, t_max=float(np.degrees(ts[nval - 1])) if nval else 0.0,
                     th_max=float(th[nval - 1]) if nval else None, phi_t=None, dKB=float(np.degrees(dKB)), lobe_r_max=None, lift_max=0.0,
                     m3e_min=float(m3[:nval].min()) if nval else None, k_max=float(dk[:nval].max()) if nval else 0.0, name="dog")
    return self._law


FL.FLDesign.law = dog_law


def _strap(a, b, lev_a, lev_b, w, step=2.0):
    """underside samples of a spherical strap a -> b (unit dirs), width w, underside level joggled linearly lev_a -> lev_b"""
    om = math.acos(max(-1, min(1, float(a @ b)))); lm = 0.5 * (lev_a + lev_b)
    n = max(2, int(lm * om / step) + 1); t = np.linspace(0, 1, n)[:, None]
    C = (np.sin((1 - t) * om) * a + np.sin(t * om) * b) / max(math.sin(om), 1e-9)
    bn = unit(np.cross(a, b)); rr = (lev_a + (lev_b - lev_a) * t)
    nw = max(2, int(round(w / step)) + 1); pts = []
    for ww in np.linspace(-w / 2 + 0.5, w / 2 - 0.5, nw):
        pts.append(unit(C + (ww / rr) * bn) * rr)
    return np.concatenate(pts), C


def _disc(axis, lev, r, step=2.0):
    e, f = S.frame_of(axis); dd = S.disc(r, step)
    return axis * lev + dd[:, :1] * e + dd[:, 1:] * f


class DRModel(LS.LSModel):
    """per-pose bodies: 9 = dog sector + arm (turns about u2 by phi(K)), 8 = drag link (spherical rotation carrying
    (c1_0, c2_0) to (c1, c2)); horn on member 1 (link 1a)"""
    def _rod_metal(self):
        D = self.D; P = D.p; u1, u2, u3 = D.u; uK = D.uK; fK, f2 = float(self.fK), float(self.f[1])
        dg = dog4r(D); sp = dg["sp"]; s_q = dg["s_q"]; c1_0, c2_0 = dg["c1_0"], dg["c2_0"]
        L1b = self.link_pts["L1b"][1]; L1bU = unit(L1b); L1bN = np.linalg.norm(L1b, axis=1)
        e2, g2 = S.frame_of(u2)

        def az2(X): X = np.atleast_2d(X); w = X - (X @ u2)[:, None] * u2; return np.degrees(np.arctan2(w @ g2, w @ e2))
        # ---- link 2's root in the ring layer: its leading edge (push direction) at the onset = the sector's lug face
        m2, X2 = self.link_pts["L2"]; h2 = X2 @ u2; rad2 = np.linalg.norm(X2 - h2[:, None] * u2, axis=1)
        lay = (rad2 < RING_RO + 2.0) & (h2 > f2 - 4.5) & (h2 < f2 + 3.0 + 0.15)
        X2r = X2[lay] if lay.any() else X2[np.argsort(rad2)[:4]]
        self._L2ring = X2r
        on = (S.rotm(u2, dg["q2hi"])[0] @ X2r.T).T
        psi_on = s_q * az2(on); ref = float(psi_on[0]); psi_on = ref + ((psi_on - ref + 180) % 360 - 180)
        psi0 = float(psi_on.max())                           # leading edge in the push coordinate psi = s_q * az
        gap_deg = math.degrees(float(P["sector_gap"]) / RING_RO)
        # ---- arm: root on the sector (ring layer), azimuth of c1 + root_off (in the push sense), beside / stacked over link 1b
        az_c1 = float(az2(c1_0)[0]); psi_root = s_q * (az_c1) + float(P["root_off"])
        psi_root = psi0 + ((psi_root - psi0) % 360.0)
        root_dir = unit(u2 * math.cos(math.radians(11.5)) + unit(S.rotm(u2, math.radians(s_q * psi_root))[0] @ e2) * math.sin(math.radians(11.5)))
        arm_half = math.degrees((ARM_W / 2 + 1.0) / RING_RO)
        span = (psi_root - psi0) + arm_half                   # sector: psi0 + gap .. psi_root + arm half width
        zring = f2 if int(P["ring_layer"]) == 0 else f2 + 2 * (S.T_LINK + RUNG)
        push_end = float(dg["push"][-1]) if dg["ok"] else 0.0
        WOK = S.W_LINK / 2 + 1.0
        om = math.acos(max(-1, min(1, float(root_dir @ c1_0)))); na = max(3, int(62.0 * om / 2.0) + 1); ta = np.linspace(0, 1, na)[:, None]
        Ca = (np.sin((1 - ta) * om) * root_dir + np.sin(ta * om) * c1_0) / max(math.sin(om), 1e-9); bna = unit(np.cross(root_dir, c1_0))
        ws_ = np.array([-2.5, -0.83, 0.83, 2.5])
        dirs = np.stack([unit(Ca + (w / 62.0) * bna) for w in ws_], 1)          # (na, 4, 3)
        beside = np.ones(na, bool)
        for ph in np.linspace(0.0, s_q * push_end, 9):
            Dp = dirs.reshape(-1, 3) @ S.rotm(u2, ph)[0].T
            dd = (np.arccos(np.clip(Dp @ L1bU.T, -1, 1)) * L1bN[None, :]).min(1).reshape(na, 4)
            beside &= dd.min(1) >= WOK
        jn = np.argmin(np.arccos(np.clip(Ca.reshape(-1, 3) @ L1bU.T, -1, 1)), axis=1); base = L1bN[jn]
        lvl = np.where(beside, base + float(P["zr"]), base + S.T_LINK + RUNG)
        # near hub 2 the arm is the sector's own body (ring layer) - the root stays at zring out to r 14.5
        rr_ = np.array([math.sin(math.acos(max(-1, min(1, float(c @ u2))))) * 62.0 for c in Ca])
        lvl = np.where(rr_ <= 14.5, zring, lvl)
        sarc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Ca, axis=0), axis=1) * 62.0)])
        k = math.tan(S.RAMP * D2R)
        lvl = np.max(lvl[None, :] - k * np.abs(sarc[:, None] - sarc[None, :]), axis=1)
        arm = (dirs * lvl[:, None, None]).reshape(-1, 3)
        arm_mid = (dirs * (lvl[:, None, None] + 1.5)).reshape(-1, 3)
        lv_tip = float(lvl[-1])
        # ---- sector (annulus r 10.2-12.5 at zring, psi from psi0 + gap to psi0 + span)
        sec = []
        for rr in (10.8, 12.0):
            npts = max(3, int(rr * math.radians(span) / 2.0) + 1)
            for ps in np.linspace(psi0 + gap_deg, psi0 + span, npts):
                d = S.rotm(u2, math.radians(s_q * ps))[0] @ e2
                sec.append(u2 * zring + rr * d)
        sec = np.array(sec); sec_mid = sec + 1.5 * u2
        # ---- horn on link 1a: from hub K's rim to r_h + EYE_R along c2's azimuth about uK, level fK + hl
        lvK = fK + float(P["hl"]); ek = unit(c2_0 - (c2_0 @ uK) * uK); bk = unit(np.cross(uK, ek))
        rh = float(lvK * math.tan(math.radians(float(P["a3"]))))
        horn = np.array([uK * lvK + r_ * ek + w_ * bk for r_ in np.arange(S.HUB_R + 0.5, rh + EYE_R + 1e-6, 2.0) for w_ in (-3.0, -1.0, 1.0, 3.0)])
        horn = np.concatenate([horn, _disc(uK, lvK, 0.01)[:0]]) if len(horn) else horn
        # ---- drag link: eye over / under the arm tip and the horn, joggled strap between
        la = lv_tip + float(P["dl_a"]) * (S.T_LINK + RUNG); lh = lvK + float(P["dl_h"]) * (S.T_LINK + RUNG)
        dl, Cd = _strap(unit(c1_0), unit(c2_0), la, lh, DL_W)
        eyes = np.concatenate([_disc(unit(c1_0), la, EYE_R), _disc(unit(c2_0), lh, EYE_R)])
        dl_all = np.concatenate([dl, eyes]); dl_mid = dl_all + 1.5 * unit(dl_all)
        self._scg = dict(PV=u2 * zring, dR=u2, tip0=c1_0 * lv_tip, H0=c2_0 * lvK, uK=uK, sp=sp, dog=dg)
        self._sc = None
        self.rigid["crank"] = (9, np.concatenate([sec, arm]))
        self.rigid["rod"] = (8, dl_all)
        self.rigid["horn"] = (1, horn)
        self.rigid.pop("rodends", None); self.rigid.pop("rocker", None)
        self._contact_only(); self._solids()
        self.contact.append((8, dl_all + S.T_LINK * unit(dl_all)))
        self.contact.append((9, np.concatenate([sec + S.T_LINK * u2, arm + S.T_LINK * unit(arm)])))
        self.contact.append((1, horn + S.T_LINK * uK))
        far_root = np.linalg.norm(arm_mid - (arm_mid @ u2)[:, None] * u2, axis=1) > RING_RO + 2.0
        self.strap["ROD"] = (8, dl_mid)
        self.strap["CRK"] = (9, arm_mid[far_root] if far_root.any() else arm_mid[-4:])
        self.strap["HORN"] = (1, horn + 1.5 * uK)
        self._ring_mid = sec_mid; self._crown_ok = True
        self._dogg = dict(psi0=psi0, span=span, gap=gap_deg, s_q=s_q, zring=zring)
        # ---- the drive's own range: PA (table), then clearances swept in link 1b's frame over K
        lim, why_lim = (float(dg["K"][-1]), "pa/table:" + dg["why"]) if dg["ok"] else (0.0, dg["why"])
        mem2, cen2, ax2 = self.cyl["hub2"]; r2 = self.cyl_r["hub2"]; memK, cenK, axK = self.cyl["hubK"]; rK = self.cyl_r["hubK"]
        L1bS = self.strap["L1b"][1]
        def farX(X, cen, ax, r, pad): w = X - cen; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > r + pad]
        L1b_farB = farX(farX(L1bS, cen2, ax2, r2, 4.0), cenK, axK, rK, 1.0); treeB = cKDTree(L1b_farB) if len(L1b_farB) else None
        L1b_near2 = L1bS[np.linalg.norm(L1bS - (L1bS @ u2)[:, None] * u2, axis=1) < RING_RO + 4.0]; tree2 = cKDTree(L1b_near2) if len(L1b_near2) else None
        clr = dict(ring_L1b=99.0, dl_hubK=99.0, dl_hub2=99.0, arm_hubK=99.0, dl_L1b=99.0, horn_L1b=99.0)
        if dg["ok"]:
            Kt = dg["K"]; PHt = dg["phi"]
            for j in range(0, len(Kt), 4):
                kk = float(Kt[j]); Rr = S.rotm(u2, float(PHt[j]))[0]
                c1 = Rr @ c1_0; c2 = S.rotm(uK, sp * kk)[0].T @ c2_0
                Rd = self._dl_rot(c1_0, c2_0, c1, c2)
                RG = (np.concatenate([sec_mid, arm_mid[~far_root]]) @ Rr.T) if (~far_root).any() else sec_mid @ Rr.T
                AR = self.strap["CRK"][1] @ Rr.T; DL = dl_mid @ Rd.T
                HN = (horn + 1.5 * uK) @ S.rotm(uK, sp * kk)[0]          # R^T applied as row-vector @ R
                c_ = dict(ring_L1b=float(tree2.query(RG)[0].min()) - S.T_LINK if tree2 is not None else 99.0,
                          dl_hubK=float(self.sd_cyl(DL, cenK, axK, r=rK).min()) - 1.5, dl_hub2=float(self.sd_cyl(DL, cen2, ax2, r=r2).min()) - 1.5,
                          arm_hubK=float(self.sd_cyl(AR, cenK, axK, r=rK).min()) - 1.5,
                          dl_L1b=float(treeB.query(farX(farX(DL, cen2, ax2, r2, 4.0), cenK, axK, rK, 1.0))[0].min()) - S.T_LINK if treeB is not None and len(farX(farX(DL, cen2, ax2, r2, 4.0), cenK, axK, rK, 1.0)) else 99.0,
                          horn_L1b=float(treeB.query(farX(HN, cenK, axK, rK, 1.0))[0].min()) - S.T_LINK if treeB is not None and len(farX(HN, cenK, axK, rK, 1.0)) else 99.0)
                need = dict(ring_L1b=RUNG, dl_hubK=1.0, dl_hub2=1.0, arm_hubK=1.0, dl_L1b=1.0, horn_L1b=1.0)
                for k_, v in c_.items(): clr[k_] = min(clr[k_], v)
                bad = [k_ for k_, v in c_.items() if v < need[k_]]
                if bad:
                    lim = float(Kt[max(j - 4, 0)]) if j > 0 else 0.0; why_lim = bad[0]; break
        self._scg.update(dK_lim=lim, why_lim=why_lim, kgrid=dg["K"] if dg["ok"] else np.zeros(2), phig=dg["phi"] if dg["ok"] else np.zeros(2))
        dKp = np.abs(np.asarray(self.dK, float)); taken = np.asarray(self.kin_ok, bool) & (dKp > 1e-9)
        kmax_t = float(dKp[taken].max()) if taken.any() else 0.0
        pa_t = float(np.interp(min(kmax_t, lim), dg["K"], dg["pa"])) if dg["ok"] else 0.0
        pa_max_t = float(dg["pa"][dg["K"] <= min(kmax_t, lim) + 1e-9].max()) if dg["ok"] else 0.0
        gK = np.gradient(dg["K"], np.abs(dg["phi"]) + 1e-12) if dg["ok"] else np.zeros(1)
        self._sc_info = dict(dK_lim=round(math.degrees(lim), 1), why_lim=why_lim, rssr_closed=bool(dg["ok"]), crest_exact=0.0,
                             pa_max_taken=round(pa_max_t, 1), ratio_range=[round(float(np.percentile(gK[1:], 2)), 2), round(float(np.percentile(gK[1:], 98)), 2)] if dg["ok"] else None,
                             phi_max_taken=round(math.degrees(float(np.interp(kmax_t, dg["K"], np.abs(dg["phi"])))) if dg["ok"] else 0.0, 1),
                             ring_level_rel_f2=round(zring - f2, 2), sector_span=round(span, 1), arm_beside=round(float(beside.mean()), 2),
                             arm_tip_level=round(lv_tip, 1), dl_levels=[round(la, 1), round(lh, 1)], horn_level=round(lvK, 1), r_h=round(rh, 2),
                             dl_len=round(math.degrees(math.acos(max(-1, min(1, float(c1_0 @ c2_0))))) * 0.5 * (la + lh) * D2R, 1),
                             arm_len=round(float(sarc[-1]), 1), clear_min={k_: round(v, 2) for k_, v in clr.items()}, table_why=dg["why"],
                             trans_min_taken=round(90.0 - pa_max_t, 1))
        self._rod_info = self._sc_info
        self._viz_rod = dict(ring=u2 * zring, ringAx=u2, armA=root_dir * zring, armB=c1_0 * lv_tip, rodA=c1_0 * la, rodB=c2_0 * lh, horn=c2_0 * lvK)

    @staticmethod
    def _dl_rot(a0, b0, a1, b1):
        def fr(a, b): e1 = unit(a); e2 = unit(b - (b @ e1) * e1); return np.stack([e1, e2, np.cross(e1, e2)], 1)
        return fr(a1, b1) @ fr(a0, b0).T

    def _sc_pose(self):
        g = self._scg; dg = g["dog"]; n = len(self.dK); dKp = np.abs(np.asarray(self.dK, float))
        if not dg["ok"]:
            I = np.repeat(np.eye(3)[None], n, 0); Z = np.zeros((n, 3)); self._sc = dict(n=n, X={9: (I, Z), 8: (I.copy(), Z)}); return
        php = np.interp(dKp, dg["K"], dg["phi"])
        Rc = S.rotm(g["dR"], php); c1_0, c2_0 = dg["c1_0"], dg["c2_0"]; sp = g["sp"]
        Rd = np.zeros((n, 3, 3))
        for j in range(n):
            c1 = Rc[j] @ c1_0; c2 = S.rotm(g["uK"], sp * dKp[j])[0].T @ c2_0
            Rd[j] = self._dl_rot(c1_0, c2_0, c1, c2)
        self._sc = dict(n=n, X={9: (Rc, np.zeros((n, 3))), 8: (Rd, np.zeros((n, 3)))})

    def _ghost(self):
        nh = len(self.rigid["horn"][1]) if "horn" in self.rigid else -1
        for k_ in ("crank", "rod", "horn"): self.rigid.pop(k_, None)
        self.contact = [(m, X) for (m, X) in self.contact if m not in (8, 9) and not (m == 1 and len(X) == nh)]
        for k_ in ("ROD", "CRK", "HORN"): self.strap.pop(k_, None)
        self._sc_info["ghost"] = True

    def collide(self, i):
        out = super().collide(i)
        if getattr(self, "_dogg", None) is None or not hasattr(self, "_L2ring"): return out
        # the sector vs link 2's root in the ring layer, in link 1b's frame (push coordinate): link 2 may touch the lug face
        # (the dog contact) but never enter the sector, either side round
        g = self._dogg; dg = self._scg["dog"]
        R7, _ = self.T(7, i); R2, _ = self.T(2, i); Rr = R7.T @ R2
        X = self._L2ring @ Rr.T; u2 = self.D.u[1]; e2, g2 = S.frame_of(u2)
        w = X - (X @ u2)[:, None] * u2; psi = g["s_q"] * np.degrees(np.arctan2(w @ g2, w @ e2))
        ph = abs(float(np.interp(abs(float(self.dK[i])), dg["K"], dg["phi"]))) if dg["ok"] else 0.0
        lo = g["psi0"] + math.degrees(ph) + g["gap"] * 0.0; hi = g["psi0"] + g["span"] + math.degrees(ph)
        rel = (psi - lo) % 360.0
        inside = (rel > 0.5) & (rel < (hi - lo))
        d = -float(np.min(np.minimum(rel[inside] - 0.5, (hi - lo) - rel[inside]))) * RING_RO * D2R if inside.any() else 99.0
        self.last_clear["RING-L2"] = round(d, 1)
        return min(out, d)


SC.SCModel = DRModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; LS.RF.PARAMS = PARAMS; LS.BM.PARAMS = PARAMS
FL.G.KR.KB.KModel = DRModel; FL.FLModel_SC = DRModel
LS.LSModel = DRModel; LS._clamp = _clamp; LS.PARAMS = PARAMS; LS.CELL = "dogring"


def _report(B, params):
    r, M = LS._report(B, dict(params))
    info = getattr(M, "_sc_info", None) or {}
    r["cam"] = {k: info.get(k) for k in ("dK_lim", "why_lim", "pa_max_taken", "ratio_range", "phi_max_taken", "ring_level_rel_f2",
                                         "sector_span", "arm_beside", "arm_tip_level", "dl_levels", "horn_level", "r_h", "dl_len",
                                         "arm_len", "clear_min", "table_why")}
    L_ = M.D.law(); r["law"] = dict(why_end=L_.get("why_end"), dK_max=round(L_.get("dK_max", 0.0), 1), th_max=L_.get("th_max"))
    if not info.get("rssr_closed", False): r["honest"] = False; r["drive_fail"] = info.get("why_lim")
    return r, M


LS._report = _report


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("drive_fail") or r.get("sidecar_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); r["drive_kind"] = "dogring"
    if r.get("honest") is False: r["gap_honest"] = r["gap"]; r["gap"] = max(float(r["gap"]), 150.0)
    return r


gate = LS.gate; frozen = LS.frozen; frozen_held = LS.frozen_held; frozen_flood = LS.frozen_flood; th_margin = LS.th_margin


def viz_export(par):
    p = _clamp(dict(PARAMS, **par)); B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, p)
    return dict(params=p, gap=r["gap"], cam=r.get("cam"), viz=getattr(M, "_viz_rod", None))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "gate":
        t = time.time(); out = gate(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), depth={k: v for k, v in (out.get("contact_depth") or {}).items() if k != "per_pose"},
                              th_margin=out.get("th_margin"), connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o))); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), ovh=r.get("overhead140"), cam=r.get("cam"), law=r.get("law"), parts=r.get("parts_ib14"),
                          clear=getattr(M, "last_clear", None), secs=round(time.time() - t, 1)), default=float))

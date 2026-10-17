"""fourbar-longdyad-knuckle-3r (round 11, lens 2, LISTED FOR THE USER'S B1 RULING): the lead's slaved-knuckle chain on the
28 / 50 K dyad at the verified seats (longstroke-slipper-knuckle-3r: J1, link 1a, K, link 1b, J2, link 2, J3 with b3,
member 3, the two-pin knee), with the WHOLE K DRIVE (hub-2 lobe, bell crank, nose / roller, flank, clock spring) deleted
and replaced by a POSITIVE SPHERICAL FOUR-BAR on ground link 1b, all four axes through GH:

    crank   = a radial pin rigid with LINK 2 at arc rc from u2 (azimuth gc at the fold stop q2lo), turning with q2;
    coupler = a rigid spherical arc of length c (a Ti bar concentric with GH) between the crank pin and the horn pin;
    horn    = a radial pin rigid with LINK 1a at arc rh from uK (azimuth gh), so K = f(q2) positively, both ways.

3 ACTIVE DOF (J1, J2, J3 encoded). K is slaved and never read, 0 passive translations, no gears / pulleys / cables, no
spring, no sliding or rolling pair. Passive rotations: K, crank pin, horn pin, 2 knee pins.

THE LAW (closed form, per 0.25 deg of tau = q2 travel from the fold stop in the stretching sense, -60..200 deg):
    pc(tau) on the crank cone about u2; horn azimuth b from A cos b + B sin b = cos c - cos rh (pc . uK), branch br;
    dK = gh - b, K opening kr = sign(psiA) dK, with gh set so that kr(tau = 0) = k0.
    th(tau) from the chain; the usable WINDOW is the longest contiguous tau run with: real closure, horn transmission
    mu_h in [48, 132] (PA <= 42 where the coupler drives K), K inside its stops (-1.5 deg <= kr <= dKB(a1max)), the
    kit dyad margin m3e >= 5, and dth/dtau > 1 / 3.45 (th(q2) monotone, rate <= 3.45).
THE IK (replaces the parents' state-A / forced split): th -> tau on the window, then q2, K, q1, q3 in closed form; every
pose is "forced" (K is never exactly on a stop).
B1 (the fold reading, user's open ruling): p['b1read'] = 'family' (DEFAULT, today's reading: every forced pose also needs the
J1-K-J3 sub-chain margin m_sub >= 5, i.e. min(m_sub, m_eff) >= 5) or 'coupled' (the proposer's reading: m3e >= 5 only,
K positively slaved). Claims are made ONLY under 'family'; 'coupled' numbers are reported as LISTED FOR B1.

THE METAL (strap cell, per pose, all at real size and sampled ~1 point / 4 mm2):
  * crank lug: 3 mm Ti integral with link 2 at link 2's layer at hub 2 (f2 + UP + zc), 6 wide, from hub 2's rim to the
    pin, eye boss O9 (MR63ZZ O6 + 1.5 wall) - member 2, turns with q2;
  * horn lug: 3 mm Ti integral with link 1a at hub K (fK + hl), 6 wide, from hub K's rim to the pin, eye boss O9 - member 1;
  * coupler: 3 x 4 mm Ti arc, its own body (member 8), whose per-pose rotation about GH maps the reference pin pair to
    the pose's pin pair (link 1b frame). Its underside is a linear joggle between the two pin-end floors; each floor =
    max(lug top + 0.15 running gap, link 1b's top + 1.0 non-adjacent clearance at that hub) + zcp. Both eye bosses are
    O9 columns from the lug top to the coupler's top (dowel + spacer + eye), sampled as the coupler's metal.
  (Spec correction: the spec stacks the coupler at link 1b + 3.15, i.e. a 0.15 running gap to link 1b; the coupler is
  not jointed to link 1b, so it gets the 1 mm non-adjacent clearance. The spec's horn eye at r 12.3 puts an O9 eye boss
  2.2 mm into hub K's O20 housing below the crown; rh is therefore swept to >= 15.5 mm lateral and the hub check decides.)
  Part pairs: coupler vs every hub housing (1 mm), vs L1a / L2 / L1b straps (1 mm; 0.15 within 6 mm of its own pins), vs
  knee / pad / E; crank lug vs hub1 / hubK / hub3 / L1a / L1b (outside hub 2's zone) / knee / pad / E; horn lug vs hub2 /
  hub3 / L1b (outside hub K's zone) / L2 / knee / pad / E.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/fourbar-longdyad-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held '<json>' [out.json]          (claim protocol: fit Bench(60,160) fast, frozen, worn)
    ... b1 '<json>'                                         (law-only B1 count by |K| band on Bench(110,360))
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

os.environ["LS_DRIVE"] = "rssr"                               # the sidecar class chain (per-pose bodies); its RSSR metal is not used
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("longstroke_for_fourbar", os.path.join(HERE, "longstroke-slipper-knuckle-3r.py"))
LS = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(LS)
FL, SC, S, PK = LS.FL, LS.SC, LS.S, LS.PK
G = FL.G; KR = G.KR; KB = KR.KB; KIT = G.KIT
unit = S.unit; D2R = math.pi / 180
ID = "fourbar-longdyad-knuckle-3r"
MARG = 5.0
EYE_R = 4.5                                                  # eye boss radius: MR63ZZ (O6) + 1.5 wall
LUG_W = 6.0; CPL_W = 4.0; CPL_T = 3.0
RATE_MAX = 3.45; MU_MIN = 48.0; KSTOP_A = -1.5

# the strap cell seed (proposer: fbs_k2850_off_strap_t43, x = [rc, gc, rh, c, br, k0, gh]) + the judge's knee re-fit
FB_SEED = {"rc": 16.0, "gc": 54.0903, "rh": 11.5967, "c": 38.6253, "br": -1.0, "k0": 22.5886}
KNEE_SEED = {"lE": 74.3, "lc": 15.7, "phiE": 18.4, "phib": -77.8, "ang_min": 26.88}
PARAMS = dict(LS.PARAMS); PARAMS.update(FB_SEED); PARAMS.update(KNEE_SEED)
PARAMS.update(b1read="family", hl=0.0, zc=0.0, zcp=0.0, a1max=72.5)
for _k in ("La", "r_h", "beta", "gam", "s_arm", "r_lobe", "zr", "i_rock", "r_horn"): PARAMS.pop(_k, None)


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    p["chain"] = "free"; p["law_mode"] = "lin"; p["cprog"] = 0.0
    p["bk1"] = _c(p["bk1"], 26.0, 34.0); p["bk2"] = _c(p["bk2"], 38.0, 56.0)
    p["a1max"] = min(float(p["a1max"]), float(p["bk1"]) + float(p["bk2"]) - 5.5)      # stop B >= 5.5 deg off the K dyad stretch
    p["rc"] = _c(p["rc"], 2.0, 26.0); p["rh"] = _c(p["rh"], 2.0, 26.0); p["c"] = _c(p["c"], 10.0, 80.0)
    p["gc"] = float(p["gc"]); p["k0"] = float(p["k0"]); p["br"] = 1.0 if float(p.get("br", -1.0)) > 0 else -1.0
    p["hl"] = _c(p.get("hl", 0.0), 0.0, 3.15); p["zc"] = _c(p.get("zc", 0.0), 0.0, 6.0); p["zcp"] = _c(p.get("zcp", 0.0), 0.0, 8.0)
    p["ang_min"] = max(float(p.get("ang_min", 26.88)), 26.88)
    p["b1read"] = "coupled" if str(p.get("b1read", "family")) == "coupled" else "family"
    # the parents' lobe-law keys stay at harmless values (the lobe is deleted; FL.law() is computed for reports only)
    p["kK"] = max(float(p.get("kK", 2.0)), 0.0); p["kA"] = p["kB"] = p["kK"]; p["t1"] = 6.0; p["law_mode_in"] = "lin"; p["law_mode"] = "seg"
    p["smt"] = max(float(p.get("smt", 12.0)), 5.2)
    p.setdefault("La", 20.0); p.setdefault("s_arm", 5.0); p.setdefault("r_h", 15.0); p.setdefault("r_lobe", 7.5); p.setdefault("beta", -112.0)
    p["i_rock"] = float(p["La"]) / float(p["s_arm"]); p["r_horn"] = float(p["r_h"])
    return p


def _fp(ax, toward):
    e = toward - (toward @ ax) * ax; e = e / np.linalg.norm(e); return e, np.cross(ax, e)


def dyad_margin(th, a1, a2):
    a1 = np.asarray(a1, float)
    return np.minimum.reduce([th - np.abs(a1 - a2), np.minimum(a1 + a2, 360 - a1 - a2) - th])


class FBDesign(FL.FLDesign):
    """the four-bar slaved K: closed-form law table + the generic slaved-K inverse (every pose forced)"""

    def _geomq(self):
        u1, u2, u3 = self.u; sg = self.q2sgn if self.q2sgn is not None else -1.0
        q2lo = self._q2_at(self.th_lo, sg); q2hi = self._q2_at(self.th_hi, sg)
        th3 = lambda q: math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
        s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
        return q2lo, q2hi, s_q

    def dKB(self):
        P = self.p
        cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (
            math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
        return abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))

    def fb_table(self):
        if getattr(self, "_fbT", None) is not None: return self._fbT
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; q2lo, q2hi, s_q = self._geomq(); sp = float(np.sign(self.psiA)) or 1.0
        e2, f2 = _fp(u2, uK); eK, fK = _fp(uK, u2)
        taus = np.radians(np.arange(-60.0, 200.0 + 1e-9, 0.25)); q2 = q2lo + s_q * taus
        al = math.radians(float(P["gc"])) + (q2 - q2lo)
        rc, rh, c = (math.radians(float(P[k])) for k in ("rc", "rh", "c"))
        pc = math.cos(rc) * u2[None] + math.sin(rc) * (np.cos(al)[:, None] * e2 + np.sin(al)[:, None] * f2)
        A = math.sin(rh) * (pc @ eK); Bv = math.sin(rh) * (pc @ fK); Cc = math.cos(c) - math.cos(rh) * (pc @ uK)
        R = np.hypot(A, Bv); x = Cc / np.maximum(R, 1e-12); real = np.abs(x) <= 1 - 1e-9
        be = np.unwrap(np.arctan2(Bv, A) + float(P["br"]) * np.arccos(np.clip(x, -1, 1)))
        i0 = int(np.argmin(np.abs(taus)))
        gh = float(be[i0]) + sp * math.radians(float(P["k0"]))
        kr = sp * (gh - be); dK = sp * kr
        RK = S.rotm(uK, dK); R2 = S.rotm(u2, q2); p3 = np.einsum("nij,j->ni", R2, u3)
        th = np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", RK, p3) @ u1, -1, 1)))
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RK, u2) @ u1, -1, 1)))
        cK = np.degrees(np.arccos(np.clip(p3 @ uK, -1, 1))); b1 = float(P["bk1"])
        msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
        m3e = dyad_margin(th, a1e, self.a2)
        ph = math.cos(rh) * uK[None] + math.sin(rh) * (np.cos(be)[:, None] * eK + np.sin(be)[:, None] * fK)   # horn pin, link 1b frame

        def tang(at, to):
            t = to - np.einsum("ij,ij->i", to, at)[:, None] * at; return t / np.maximum(np.linalg.norm(t, axis=1), 1e-12)[:, None]
        mu_h = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", tang(ph, pc), tang(ph, np.broadcast_to(uK, ph.shape))), -1, 1)))
        mu_c = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", tang(pc, ph), tang(pc, np.broadcast_to(u2, pc.shape))), -1, 1)))
        dKB = self.dKB()
        dth = np.gradient(th, np.degrees(taus))
        ok = real & (mu_h >= MU_MIN) & (mu_h <= 180 - MU_MIN) & (kr >= math.radians(KSTOP_A) - 1e-9) & (kr <= dKB + 1e-9)
        ok &= (m3e >= MARG - 1e-9) & (dth > 1.0 / RATE_MAX)
        best = None; i = 0; n = len(ok)
        while i < n:
            if ok[i]:
                j = i
                while j + 1 < n and ok[j + 1]: j += 1
                span = th[j] - th[i]
                if best is None or span > best[2]: best = (i, j, span)
                i = j + 1
            else: i += 1
        # the horn pin in link 1a's frame (constant) and the crank pin in link 2's body frame (q2 = 0)
        ph0 = math.cos(rh) * uK + math.sin(rh) * (math.cos(gh) * eK + math.sin(gh) * fK)
        pcB = S.rotm(u2, -q2lo)[0] @ pc[i0]
        self._fbT = dict(taus=taus, q2=q2, kr=kr, dK=dK, th=th, a1e=a1e, msub=msub, m3e=m3e, mu_h=mu_h, mu_c=mu_c, real=real, pc=pc,
                         ph=ph, iv=best, q2lo=q2lo, q2hi=q2hi, s_q=s_q, sp=sp, gh=gh, ph0=ph0, pcB=pcB, dKB=dKB, i0=i0)
        return self._fbT

    def law(self):
        """the parents' lobe-law dict (reports only) with the four-bar window written over the keys the chain reads"""
        L = dict(super().law()); T = self.fb_table(); iv = T["iv"]
        if iv is None: L.update(ok=False, why_end="fourbar_window_empty"); return L
        i0, i1, _ = iv
        L.update(ok=True, fourbar=True, th_max=float(T["th"][i1]), dK_max=float(np.degrees(np.abs(T["kr"][i0:i1 + 1]).max())),
                 m3e_min=float(T["m3e"][i0:i1 + 1].min()), why_end="fourbar")
        return L

    def _ik_phys(self, Q):
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]; m = KIT.FOLD_MARGIN
        if self.q2sgn is None: super()._ik_phys(Q)                       # the parents' rule for q2's half-turn (state-A branch)
        T = self.fb_table(); iv = T["iv"]
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        if iv is None:
            i0, i1 = T["i0"], T["i0"]; inr = np.zeros(n, bool)
        else:
            i0, i1, _ = iv; thL = T["th"][i0:i1 + 1]; inr = (th >= thL[0] - 1e-9) & (th <= thL[-1] + 1e-9)
        thL = T["th"][i0:i1 + 1]; tL = T["taus"][i0:i1 + 1]
        tt = np.interp(th, thL, tL) if len(thL) > 1 else np.zeros(n)
        kr = np.interp(tt, T["taus"], T["kr"]); dK = T["sp"] * kr; q2 = T["q2lo"] + T["s_q"] * tt
        Rq = S.rotm(u2, q2) if n else np.zeros((0, 3, 3)); p = Rq @ u3; RK = S.rotm(uK, dK) if n else np.zeros((0, 3, 3))
        q1 = S.sub1(u1, np.einsum("nij,nj->ni", RK, p), w); R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
        R12 = R1 @ RK @ Rq; vv = KR.unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv)); R3 = S.rotm(u3, q3) if n else np.zeros((0, 3, 3))
        R123 = R12 @ R3; t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        cK = np.degrees(np.arccos(np.clip(p @ uK, -1, 1))); b1 = float(P["bk1"])
        msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RK, u2) @ u1, -1, 1)))
        m3e = dyad_margin(th, a1e, self.a2)
        ok = inr & (m3e >= m - 1e-6) & bool(self.k_ok) & bool(self.stops_ok)
        if P.get("b1read", "family") != "coupled": ok &= msub >= m - 1e-6        # today's family reading: min(m_sub, m_eff) >= 5
        Z0 = np.zeros((n, 3)); X1 = (R1, Z0); X1b = (R1 @ RK, Z0); X2 = (R12, Z0); X3 = (R123, t3)
        sv = np.einsum("nji,nj->ni", Q, t3); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        q = np.stack([q1, q2, q3], 1)
        self._X1b, self._dK, self._state, self._a1e = X1b, dK, np.ones(n, int), a1e
        self._msub, self._m3e = msub, m3e; self._camt = np.degrees(tt); self._q2now = q2; self._fb_inr = inr
        return q, ok, X1, X2, X3, s


KB.KDesign = FBDesign; FL.G.KR.KB.KDesign = FBDesign


def _ring(c, r, axv, n=16):
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False); a, b = S.frame_of(axv)
    return c + r * (np.cos(ang)[:, None] * a + np.sin(ang)[:, None] * b)


def _frame2(a, b):
    e1 = unit(a); e2 = b - (b @ e1) * e1; e2 = e2 / np.linalg.norm(e2); return np.stack([e1, e2, np.cross(e1, e2)], 1)


class FBModel(LS.LSModel):
    """the chain's model (sidecar / longstroke class chain) with the four-bar's three bodies as its drive metal"""

    def _truncate(self):
        return                                                   # the four-bar window already bounds K inside its stops

    def _fb_pose(self):
        """per pose: the coupler's rotation in link 1b's frame (maps the reference pin pair to the pose's pin pair)"""
        D = self.D; T = D.fb_table(); u2, uK = D.u[1], D.uK; n = len(self.dK)
        q2 = np.asarray(self.q[:, 1], float); dK = np.asarray(self.dK, float)
        pc = np.einsum("nij,j->ni", S.rotm(u2, q2), T["pcB"]); ph = np.einsum("nji,j->ni", S.rotm(uK, dK), T["ph0"])   # R^T ph0
        F0 = _frame2(self._cref[0], self._cref[1]); Rc = np.zeros((n, 3, 3))
        for j in range(n): Rc[j] = _frame2(pc[j], ph[j]) @ F0.T
        self._fbp = dict(n=n, R=Rc)

    def T(self, m, i):
        if m == 8 and getattr(self, "_cref", None) is not None:
            if getattr(self, "_fbp", None) is None or self._fbp["n"] != len(self.dK): self._fb_pose()
            R7, t7 = super().T(7, i); return R7 @ self._fbp["R"][i], t7
        return super().T(m, i)

    def _rod_metal(self):
        D = self.D; P = D.p; u2, uK = D.u[1], D.uK; T = D.fb_table(); fK, f2 = float(self.fK), float(self.f[1])
        UP, TL, RUN_ = S.UP, S.T_LINK, 0.15
        for k_ in ("rocker", "crank", "rod", "rodends", "horn", "roller", "lug"): self.rigid.pop(k_, None)
        pcB, ph0 = unit(T["pcB"]), unit(T["ph0"])
        # levels: crank lug at link 2's layer at hub 2, horn lug at link 1a's layer at hub K
        lc_ = f2 + UP + float(P["zc"]); lh_ = fK + float(P["hl"])
        fl_c = max(lc_ + TL + RUN_, f2 + TL + 1.0) + float(P["zcp"])            # coupler underside floor at the crank end
        fl_h = max(lh_ + TL + RUN_, fK + UP + TL + 1.0) + float(P["zcp"])       # ... at the horn end (over link 1b's layer at K)

        def lug(ax, pin, lev):
            e = unit(pin - (pin @ ax) * ax); bn = np.cross(ax, e)
            rpin = lev * math.sqrt(max(0.0, 1.0 - float(pin @ ax) ** 2)) / max(float(pin @ ax), 0.2)   # pin's lateral offset at lev
            rs = np.arange(S.HUB_R + 0.5, rpin + 1e-6, S.SPACING)
            # a formed lug: its underside follows the sphere through the hub's layer (radius lev / cos at the rim), not a flat plate
            R0 = math.hypot(lev, S.HUB_R + 0.5)
            pts = [unit(ax * lev + r_ * e + w_ * bn) * R0 for r_ in rs for w_ in np.arange(-LUG_W / 2, LUG_W / 2 + 1e-6, S.SPACING)]
            cen = unit(ax * lev + rpin * e) * R0; a_, b_ = S.frame_of(unit(cen)); dd = S.disc(EYE_R, S.SPACING)
            pts += list(cen + dd[:, :1] * a_ + dd[:, 1:] * b_)
            return np.array(pts), cen, rpin
        crank, cen_c, rpin_c = lug(u2, pcB, lc_)                  # member 2 (link 2's body frame, q2 = 0)
        horn, cen_h, rpin_h = lug(uK, ph0, lh_)                   # member 1 (link 1a's body frame)
        # coupler (member 8): reference = the pin pair at tau = 0 in link 1b's frame
        i0 = T["i0"]; pc_r = unit(T["pc"][i0]); ph_r = unit(T["ph"][i0]); self._cref = (pc_r, ph_r); self._fbp = None
        ang = math.acos(float(np.clip(pc_r @ ph_r, -1, 1))); nrm = unit(np.cross(pc_r, ph_r))
        Lmid = 0.5 * (fl_c + fl_h) * ang; ns = max(3, int(Lmid / S.SPACING) + 1); fs = np.linspace(0, 1, ns)
        dirs = np.array([unit(math.sin((1 - f) * ang) * pc_r + math.sin(f * ang) * ph_r) for f in fs])
        lev = fl_c * (1 - fs) + fl_h * fs
        cpl = np.array([unit(dirs[j] * lev[j] + w_ * nrm) * lev[j] for j in range(ns) for w_ in np.arange(-CPL_W / 2, CPL_W / 2 + 1e-6, S.SPACING)])
        # eye columns of the coupler at both pins (lug top -> coupler top), as the coupler's metal (dowel + spacer + eye)
        def col(pin, z0, z1):
            return np.concatenate([_ring(pin * z / max(float(pin @ pin), 1e-9) ** 0.5, EYE_R, pin) for z in np.linspace(z0, z1, 4)])
        # the eye centres in link 1b's frame at tau = 0: pin directions pc_r / ph_r
        eye_c = col(pc_r, lc_ + TL + RUN_, fl_c + CPL_T); eye_h = col(ph_r, lh_ + TL + RUN_, fl_h + CPL_T)
        a_, b_ = S.frame_of(pc_r); dd = S.disc(EYE_R, S.SPACING); disc_c = pc_r * fl_c + dd[:, :1] * a_ + dd[:, 1:] * b_
        a_, b_ = S.frame_of(ph_r); disc_h = ph_r * fl_h + dd[:, :1] * a_ + dd[:, 1:] * b_
        self.rigid["crank"] = (2, crank); self.rigid["horn"] = (1, horn)
        self.rigid["coupler"] = (8, np.concatenate([cpl, disc_c, disc_h]))
        self._contact_only(); self._solids()
        self.contact.append((2, np.concatenate([crank + TL * unit(crank), _ring(cen_c, EYE_R, u2), _ring(cen_c + TL * u2, EYE_R, u2)])))
        self.contact.append((1, np.concatenate([horn + TL * unit(horn), _ring(cen_h, EYE_R, uK), _ring(cen_h + TL * uK, EYE_R, uK)])))
        self.contact.append((8, np.concatenate([cpl + CPL_T * unit(cpl), eye_c, eye_h, disc_c + CPL_T * pc_r, disc_h + CPL_T * ph_r])))
        self.strap["CRKL"] = (2, crank + (TL / 2) * unit(crank))
        self.strap["HRNL"] = (1, horn + (TL / 2) * unit(horn))
        self.strap["CPL"] = (8, cpl + (CPL_T / 2) * unit(cpl))
        self.strap["CPLE"] = (8, np.concatenate([eye_c, eye_h]))                  # eye columns: surface samples (no half-thickness)
        self._cpl_pins = (pc_r, ph_r)
        self._crown_ok = True
        iv = T["iv"]
        i0w, i1w = (iv[0], iv[1]) if iv else (T["i0"], T["i0"])
        self._scg = dict(dK_lim=float(np.abs(T["kr"][i0w:i1w + 1]).max()) if iv else 0.0, why_lim="fourbar_window")
        self._sc = None
        self._sc_info = dict(fourbar=True, rc=round(float(P["rc"]), 2), gc=round(float(P["gc"]), 2), rh=round(float(P["rh"]), 2), c=round(float(P["c"]), 2),
                             k0=round(float(P["k0"]), 2), gh=round(math.degrees(T["gh"]), 2), crank_pin_r=round(rpin_c, 1), horn_pin_r=round(rpin_h, 1),
                             lug_c_level=round(lc_, 1), lug_h_level=round(lh_, 1), coupler_floor=[round(fl_c, 1), round(fl_h, 1)],
                             coupler_arc_mm=round(Lmid, 1), dK_lim=round(math.degrees(self._scg["dK_lim"]), 1), why_lim="fourbar_window",
                             th_win=[round(float(T["th"][i0w]), 2), round(float(T["th"][i1w]), 2)] if iv else None,
                             mu_h_win=[round(float(T["mu_h"][i0w:i1w + 1].min()), 1), round(float(T["mu_h"][i0w:i1w + 1].max()), 1)] if iv else None,
                             mu_c_win=[round(float(T["mu_c"][i0w:i1w + 1].min()), 1), round(float(T["mu_c"][i0w:i1w + 1].max()), 1)] if iv else None,
                             K_win=[round(float(np.degrees(T["kr"][i0w:i1w + 1].min())), 2), round(float(np.degrees(T["kr"][i0w:i1w + 1].max())), 2)] if iv else None)
        self._rod_info = self._sc_info
        self._viz_rod = dict(crankPin=cen_c, hornPin=cen_h, cplA=pc_r * fl_c, cplB=ph_r * fl_h)

    def collide(self, i):
        out = FL.FLModel.__mro__[1].__mro__[1].collide(self, i)       # the chain's own pairs (KModel: hubs, straps, knee, pad, E)
        if "CPL" not in self.strap: return out
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def ss(A, Bq, extra): return float(cKDTree(Bq).query(A)[0].min()) - extra if len(A) and len(Bq) else 1e9
        def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
        def away(X, pin_w, r):
            d = X - (X @ pin_w)[:, None] * pin_w[None]; return X[np.linalg.norm(d, axis=1) > r]
        CP = tf(*self.strap["CPL"]); CE = tf(*self.strap["CPLE"]); CK = tf(*self.strap["CRKL"]); HN = tf(*self.strap["HRNL"])
        st = {k_: tf(m, X) for k_, (m, X) in self.strap.items() if k_ in ("L1a", "L1b", "L2")}
        R8, _ = self.T(8, i); pcw = R8 @ self._cpl_pins[0]; phw = R8 @ self._cpl_pins[1]
        c = {}
        for hb in ("hub1", "hubK", "hub2", "hub3"): c[f"CPL-{hb}"] = min(vcyl(CP, hb, CPL_T / 2), vcyl(CE, hb))
        c["CPL-L1b"] = min(ss(CP, st["L1b"], CPL_T / 2 + h), ss(CE, st["L1b"], h))
        c["CPL-L1a"] = min(ss(away(CP, phw, EYE_R + 6.0), st["L1a"], CPL_T / 2 + h), ss(away(CE, phw, EYE_R + 1.0), st["L1a"], h))
        c["CPL-L2"] = min(ss(away(CP, pcw, EYE_R + 6.0), st["L2"], CPL_T / 2 + h), ss(away(CE, pcw, EYE_R + 1.0), st["L2"], h))
        c["CPL-CRKL"] = ss(away(CP, pcw, EYE_R + 1.0), away(CK, pcw, EYE_R + 1.0), CPL_T / 2 + h)
        c["CPL-HRNL"] = ss(away(CP, phw, EYE_R + 1.0), away(HN, phw, EYE_R + 1.0), CPL_T / 2 + h)
        for hb in ("hub1", "hubK", "hub3"): c[f"CRKL-{hb}"] = vcyl(CK, hb, h)
        c["CRKL-L1a"] = ss(CK, st["L1a"], 2 * h); c["CRKL-L1b"] = ss(far(CK, "hub2", 4.0), far(st["L1b"], "hub2", 4.0), 2 * h)
        c["CRKL-HRNL"] = ss(CK, HN, 2 * h)
        for hb in ("hub2", "hub3"): c[f"HRNL-{hb}"] = vcyl(HN, hb, h)
        c["HRNL-L1b"] = ss(far(HN, "hubK", 4.0), far(st["L1b"], "hubK", 4.0), 2 * h); c["HRNL-L2"] = ss(HN, st["L2"], 2 * h)
        bx = self._boxes_at_final(i)
        for nm in ("knee", "pad"):
            cen, R, half = bx[nm]
            for k_, X, e_ in (("CPL", CP, CPL_T / 2), ("CRKL", CK, h), ("HRNL", HN, h)):
                c[f"{nm}-{k_}"] = float(self.sd_box(X, cen, R, half).min()) - e_
        Em = tf(*self.Emid)
        for k_, X, e_ in (("CPL", CP, CPL_T / 2), ("CRKL", CK, h), ("HRNL", HN, h)): c[f"E-{k_}"] = ss(Em, X, e_ + h)
        self.last_clear.update({k_: round(v, 1) for k_, v in c.items()})
        return min(out, min(c.values()))


SC.SCModel = FBModel; FL.G.KR.KB.KModel = FBModel; FL.FLModel_SC = FBModel; KB.KModel = FBModel


def b1_bands(M, B):
    """B1 count on the taken poses: min(m_sub, m_eff) < 5 by |K| band"""
    taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))]); ws = np.array(B.kind) == "ws"
    kk = np.degrees(np.abs(np.asarray(M.dK, float))); ms = np.minimum(np.asarray(M.D._msub if len(M.D._msub) == len(kk) else M.msub, float), 99.0)
    return kk, ms, taken, ws


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = G._report(B, p)
    r.pop("drive_idle", None)
    honest = True
    T = M.D.fb_table()
    if T["iv"] is None: honest = False; r["fourbar_fail"] = "window_empty"
    r["plain"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}
    if M.kin_ok.any() and p.get("near2"):
        a = PK.audit(M, B); r["gap_near2"] = a.get("gap_near2"); r["gap_near1"] = a.get("gap_near1", r.get("gap_near1"))
        r["min_metal_mm"] = a.get("near_touch_min_mm", r.get("min_metal_mm"))
        if r["gap_near2"] is not None: r["gap"] = r["gap_near2"]
    r["honest"] = honest and r.get("honest", True) is not False if not r.get("drive_idle") else honest
    r["cam"] = getattr(M, "_sc_info", None)
    r["b1read"] = p["b1read"]
    try: r["ws_inband"] = LS.RL.ws_inband(B)
    except Exception: pass
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); r["drive_kind"] = "fourbar"; return r


def b1_count(params, nc=110, nw=360):
    """law-only (kinematic: law window + knee + slide) taken workspace poses on Bench(nc, nw) under both readings, and the
    family-reading failures by |K| band (0-1, 1-3, 3-6, 6-10, 10-20, >= 20 deg)"""
    p = _clamp(dict(PARAMS, **params)); p["b1read"] = "coupled"
    B1 = CB.Bench(n_clip=60, n_ws=160); r1, M1 = _report(B1, p); D = M1.D
    B3 = CB.Bench(n_clip=nc, n_ws=nw); Z = CB._poses_all(); ws = np.array(B3.kind) == "ws"; Q = Z["HG"][B3.idx].astype(float)
    q, ok, *_r, s = D.ik(Q); Kn = D.knee(s); kin = ok & Kn["ok"] & (np.abs(s[:, 2]) <= float(D.p["R_tol"]))
    kk = np.degrees(np.abs(D._dK)); mm = np.minimum(D._msub, D._m3e); fail = kin & ws & (mm < MARG - 1e-6)
    elev = np.array([B3.poses[i]["elev"] for i in range(len(B3.idx))]); ov = ws & (elev >= 140)
    bands = [(0, 1), (1, 3), (3, 6), (6, 10), (10, 20), (20, 999)]
    out = dict(law_only_coupled=int((kin & ws).sum()), law_only_family=int((kin & ws & ~fail).sum()), n_ws=int(ws.sum()),
               ov_coupled=f"{int((kin & ov).sum())}/{int(ov.sum())}", ov_family=f"{int((kin & ov & ~fail).sum())}/{int(ov.sum())}",
               fails_by_absK={f"{a}-{b}": f"{int((fail & (kk >= a) & (kk < b)).sum())}/{int((kin & ws & (kk >= a) & (kk < b)).sum())}" for a, b in bands},
               msub_lt1=int((kin & ws & (D._msub < 1)).sum()), knee_over=int((ok & ws & ~Kn["ok"]).sum()),
               window=getattr(M1, "_sc_info", {}).get("th_win"), K_win=getattr(M1, "_sc_info", {}).get("K_win"), fit_fast_coupled=dict(gap=r1["gap"], reach=r1["reach"]))
    return out


def _frozen_model(P, nc, nw):
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = FBModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(FBModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_cref", "_cpl_pins"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._fbp = None; self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_fourbar", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); B = PVm.held_bench()
    else:
        B = CB.Bench(n_clip=nc, n_ws=nw)
    M = Frozen(B, P2); r = M.run()
    return fit, M1, M, B, r


def frozen(P, nc=110, nw=360):
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ov = ws & (elev >= 140)
    depth = [round(-float(mins[j]), 3) for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0]
    try: thm = LS.th_margin(M, B)
    except Exception as e: thm = dict(error=repr(e)[:300])
    a = PK.audit(M, B)
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"), th_margin=thm,
                parts_ib14=r.get("parts_ib14"), audit=a, ws_inband=LS.RL.ws_inband(B), split=LS.RL.contact_split(M, B),
                overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())),
                contact_depth=dict(n=len(depth), sum_mm=round(float(np.sum(depth)), 3), max_mm=round(float(np.max(depth)), 3) if depth else 0.0),
                cam=getattr(M1, "_sc_info", None), b1read=M1.p.get("b1read"))


def viz_export(par):
    p = _clamp(dict(PARAMS, **par)); B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, p); D = M.D
    return dict(id=ID, gap=r["gap"], u=[list(map(float, x)) for x in D.u], uK=list(map(float, D.uK)), c=[list(map(float, x)) for x in D.c],
                f=[float(x) for x in M.f], fK=float(M.fK), cam=M._sc_info, viz={k: list(map(float, v)) for k, v in M._viz_rod.items()})


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "b1":
        t = time.time(); out = b1_count(par); out["secs"] = round(time.time() - t, 1); print(json.dumps(out, default=float)); sys.exit()
    if mode in ("frozen", "held"):
        t = time.time(); out = frozen(par) if mode == "frozen" else frozen(par, -1, -1); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=out["overhead"], depth=out["contact_depth"], th_margin=out["th_margin"],
                              parts=out.get("parts_ib14"), secs=out["secs"]), default=float)); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(b1read=r["b1read"], gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), ovh=r.get("overhead140"), cam=r.get("cam"), parts=r.get("parts_ib14"), clear_last=getattr(M, "last_clear", None),
                          secs=round(time.time() - t)), default=float))

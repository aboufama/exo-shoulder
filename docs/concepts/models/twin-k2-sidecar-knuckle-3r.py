"""twin-k2-sidecar-knuckle-3r (round 9): the verified lead sidecar-longdyad-knuckle-3r (A1, 18.91 verified) UNCHANGED up to its
drive wall, plus a second slaved knuckle K2 on LINK 2 near hub 2 that opens past the wall and LENGTHENS the effective arc
a2e = arc(J2, J3), so the stretched fold limit th <= a1e + a2e - 5 rises past the lead's 109.5 deg.

Chain: scapula handler -> J1 (O20, ACTIVE) -> link 1a -> K (O20, slaved by the sidecar RSSR: hub-2 rim lobe 1 -> bell crank on
link 1b -> O3 rod -> horn on 1a) -> link 1b -> J2 (O20, ACTIVE) -> link 2a (member 10: hub 2 to K2; crank 2 on it rides lobe 2,
which is fixed to link 1b's side of hub 2) -> K2 (O20 + clock-spring cap, slaved by q2 only, never read) -> link 2b (member 2:
K2 to hub 3, the J3 housing) -> J3 (O20, ACTIVE) -> member 3 / E -> pin knee (2 passive pins) -> arm pad.
NAMING (stated): the catalogue's "2b = hub 2 to K2, 2a = K2 to hub 3" is swapped here to keep split-knuckle-twosided-3r's
code names: L2a = hub 2 -> K2 (member 10), L2b = K2 -> hub 3 (member 2).
3 ACTIVE DOF (q1, q2, q3 encoders give the pose; K and K2 are functions of q2 only), 0 passive translations.

THE TWIN LAW (exact, per t = q2 travel past the lead's onset q2hi, no spare coordinate - R17):
  K:  dK(t) = the lead's lin law (kK), DWELLING at dK1cap (lobe 1 turns into a constant-radius arc there; default 43.0 =
      the lead's RSSR range end, rod vs hub 2, measured by its own model) - the lead's taken poses are unchanged;
  K2: dK2(t) = the least opening that keeps the dyad margin m3e(th, a1e, a2e) >= smt2 (track law), made monotone and
      rate-capped by lobe 2's pressure angle (tan pa = k2 r_h2 / (i_rock2 r_lobe2) <= tan pa2_max); it starts where the lead's
      law hits m3e = smt2 (smt2 = 5: exactly the lead's drive wall, th ~109.5, the judge's correction - not law end - 2).
  th2(t) = angle(u1, R(uK, dK) R(u2, q2) R(uK2, dK2) u3) must rise monotonically (rate <= 3.45), K2's own dyad keeps 5 deg,
  dK2 <= dK2max (rod RSSR range, 40), lobe 2's crest <= HUB_R + 1.5, no lift-off; a stretched pose is solved by inverting
  th2 on its valid prefix, then q1 / q3 closed form (split-knuckle-twosided-3r's solver, stretched instead of folded).

METAL: everything of the lead (fit per config, drive 1 per-pose RSSR, _truncate past its range) + hub K2 (O20, member 10,
fitted level fK2), L2a / L2b straps (8 x 3, one tangent ramp per hub, the lead's link rule), drive 2: crank-2 boss O10 on
link 2a beside hub 2 toward K2 + O3 rod to a horn lug of link 2b beside hub K2 at strap level (r_h2), M2 ball-link rings.
SIMPLIFICATION (stated, optimistic only on won poses): drive 2's crank and rod are sampled RIGID on link 2a at their rest
pose; on the clip frames and the lead's taken poses K2 sits on stop A so they are exact there; on the won poses (K2 open
0-40 deg) the rod swings by ~dK2 r_h2 / La2 and that swing is not swept.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/twin-k2-sidecar-knuckle-3r.py [check|gate] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/twin-k2-sidecar-knuckle-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("sidecar_for_twin_k2", os.path.join(HERE, "sidecar-longdyad-knuckle-3r.py"))
SC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SC)     # private copy (its FL / G / KR / KB copies too)
FL, G, KR, KB, PK, S = SC.FL, SC.G, SC.KR, SC.KB, SC.PK, SC.S
unit = S.unit; D2R = math.pi / 180
ID = "twin-k2-sidecar-knuckle-3r"
RATE_MAX = G.RATE_MAX
BOSS_R, PAD_R, KNEE_W = PK.BOSS_R, PK.PAD_R, PK.KNEE_W
M2L = 10                                                      # member id of link 2a (hub 2 -> K2); 8 / 9 are drive 1's rod / crank

# the verified lead's A1 (docs/concepts/rows/sidecar-longdyad-knuckle-3r.json best_params), inlined for the farm
A1 = {"bk1": 28.9414, "bk2": 39.236, "a1max": 63.177400000000006, "kK": 1.6232, "r_h": 14.8706, "beta": -86.447, "La": 16.5467, "s_arm": 4.3872, "hl": 3.15, "zr": 0.0, "r_lobe": 7.7447, "smhi": 16.5464, "smlo": 5.0, "az1": 96.6954, "el1": 67.5865, "az2": 42.2031, "el2": 44.4209, "wd": 67.5003, "wa": -7.3175, "b3": 0.345, "ang_min": 26.8823, "lc": 25.6915, "phib": -60.7036, "gam": 0.0, "law_mode": "lin"}
TWIN = dict(k2=1, kK2=0.0, bk3=22.0, bk4=59.0, sK2=1, smt2=5.0, dK1cap=43.0, dK2max=40.0, r_h2=15.5, La2=16.5, s_arm2=4.4, r_lobe2=7.5,
            pa2_max=45.0, capK2=6.0, t_end2=70.0)
PARAMS = dict(SC.PARAMS, **A1); PARAMS.update(TWIN)


def _ang(a, b): return math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b)))))


class TDesign(FL.FLDesign):
    def k2_seat(self):
        P = self.p; u2, u3 = self.u[1], self.u[2]
        b3, b4 = float(P["bk3"]), float(P["bk4"]); s2 = 1.0 if float(P["sK2"]) >= 0 else -1.0
        self.uK2 = unit(S.circ_int(u2, b3 * D2R, u3, b4 * D2R, s2))
        return self.uK2

    def law2(self):
        """the twin law on a t grid (rad of q2 past the lead's q2hi); cached per design"""
        if getattr(self, "_law2", None) is not None: return self._law2
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; m = KIT.FOLD_MARGIN
        uK2 = self.k2_seat(); a2 = self.a2; b3, b4 = float(P["bk3"]), float(P["bk4"])
        L = self.law()
        k_ok = abs(b3 - b4) + m <= a2 <= b3 + b4 - m
        if not P.get("k2") or not L.get("ok") or not k_ok:
            self._law2 = dict(ok=False, why="off" if not P.get("k2") else "law1" if not L.get("ok") else "k2dyad", uK2=uK2); return self._law2
        sp = float(np.sign(self.psiA)) or 1.0; q2hi, s_q = L["q2hi"], L["s_q"]
        cap1 = float(P["dK1cap"]) * D2R
        dt = 0.1; ts = np.radians(np.arange(0.0, float(P["t_end2"]) + 1e-6, dt))
        k1 = np.minimum(np.interp(ts, L["ts"], np.abs(L["dK"])), cap1)
        RK = S.rotm(uK, sp * k1); R2_ = S.rotm(u2, q2hi + s_q * ts)
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RK, u2) @ u1, -1, 1)))
        k2max = float(P["dK2max"]) * D2R
        kg = np.radians(np.arange(0.0, float(P["dK2max"]) + 0.25 + 1e-6, 0.25))
        # sense of K2 that lengthens a2e
        s2 = None
        for sg in (1.0, -1.0):
            a2e_ = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", S.rotm(uK2, sg * kg[:3]), u3) @ u2, -1, 1)))
            if a2e_[-1] > a2e_[0] + 1e-6: s2 = sg; break
        if s2 is None:
            self._law2 = dict(ok=False, why="sign", uK2=uK2); return self._law2
        V3 = np.einsum("kij,j->ki", S.rotm(uK2, s2 * kg), u3)                       # J3 axis in link 2a's frame per K2 opening
        a2g = np.degrees(np.arccos(np.clip(V3 @ u2, -1, 1)))
        W = np.einsum("nij,njk,mk->nmi", RK, R2_, V3)                               # (t, k2) J3 axis in link 1a's frame
        thg = np.degrees(np.arccos(np.clip(W @ u1, -1, 1)))
        m3g = KR.dyad_margin(thg, a1e[:, None], a2g[None, :])
        okg = m3g >= float(P["smt2"]) - 1e-9
        first = np.where(okg.any(1), np.argmax(okg, 1), len(kg) - 1)
        kneed = kg[first]
        tpa = math.tan(float(P["pa2_max"]) * D2R); ir2 = float(P["La2"]) / float(P["s_arm2"]); rh2 = float(P["r_h2"]); rl2 = float(P["r_lobe2"])
        kabs = np.zeros(len(ts)); kK2 = max(float(P.get("kK2", 0.0)), 0.0)
        jon = int(np.argmax(kneed > 0)) if (kneed > 0).any() else len(ts)
        if kK2 > 0: kneed = np.maximum(kneed, kK2 * np.maximum(ts - ts[max(jon - 1, 0)], 0.0) * (np.arange(len(ts)) >= jon))   # at least a linear ramp from the wall
        for j in range(1, len(ts)):
            r_t = rl2 + rh2 * kabs[j - 1] / ir2
            kabs[j] = min(max(kabs[j - 1], kneed[j]), kabs[j - 1] + ir2 * r_t * tpa / rh2 * dt * D2R, k2max)
        v3 = np.einsum("nij,j->ni", S.rotm(uK2, s2 * kabs), u3)
        a2e = np.degrees(np.arccos(np.clip(v3 @ u2, -1, 1)))
        p = np.einsum("nij,nj->ni", R2_, v3); th = np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", RK, p) @ u1, -1, 1)))
        m3e = KR.dyad_margin(th, a1e, a2e)
        cps = (np.cos(a2e * D2R) - math.cos(b3 * D2R) * math.cos(b4 * D2R)) / (math.sin(b3 * D2R) * math.sin(b4 * D2R))
        psi = np.degrees(np.arccos(np.clip(cps, -1, 1))); msK2 = np.minimum(psi, 180 - psi)
        r_t = rl2 + rh2 * kabs / ir2; k_t = np.gradient(kabs, ts); pa = np.degrees(np.arctan(k_t * rh2 / (ir2 * r_t)))
        dth = np.gradient(th, ts); rate = 1.0 / np.maximum(np.radians(dth), 1e-12)
        h = 1e-4
        def th_of(tt, kk):
            RKt = S.rotm(uK, sp * np.minimum(np.interp(tt, L["ts"], np.abs(L["dK"])), cap1)); R2t = S.rotm(u2, q2hi + s_q * tt)
            v = np.einsum("nij,j->ni", S.rotm(uK2, s2 * kk), u3)
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", RKt, np.einsum("nij,nj->ni", R2t, v)) @ u1, -1, 1)))
        a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
        sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k); dk = np.gradient(kabs, ts)
        lift = (sC > 1e-9) & (sC < dk - 1e-9) & (kabs > 1e-6)
        skirt = r_t <= S.HUB_R + 1.5 + 1e-9
        good = (dth > 0) & (rate <= RATE_MAX) & (m3e >= m - 1e-6) & (msK2 >= m - 1e-6) & ~lift & skirt & (pa <= float(P["pa2_max"]) + 1e-6)
        good[0] = True
        nval = int(np.argmin(good)) if not good.all() else len(good); j = min(nval, len(good) - 1)
        why = None if nval == len(good) else ("rate" if not (dth[j] > 0 and rate[j] <= RATE_MAX) else "m3e" if m3e[j] < m else
                                              "K2dyad" if msK2[j] < m else "liftoff" if lift[j] else "skirt" if not skirt[j] else "pressure")
        on = np.nonzero(kabs[:nval] > 1e-9)[0]
        self._law2 = dict(ok=nval > 1 and len(on) > 0, uK2=uK2, s2=s2, sp=sp, q2hi=q2hi, s_q=s_q, ts=ts[:nval], dK=sp * k1[:nval], dK2=s2 * kabs[:nval],
                          th=th[:nval], a1e=a1e[:nval], a2e=a2e[:nval], m3e=m3e[:nval], why_end=why, th_max=float(th[nval - 1]),
                          th_on=float(th[on[0] - 1]) if len(on) else None, dK2_max=float(np.degrees(kabs[:nval].max())),
                          a2e_max=float(a2e[:nval].max()), t_max=float(np.degrees(ts[nval - 1])), psi0=float(psi[0]),
                          pa_max=float(pa[:nval].max()), crest=float(r_t[:nval].max()), dK1_hold=float(np.degrees(k1[:nval].max())))
        return self._law2

    def _ik_phys(self, Q):
        q, ok, X1, X2, X3, s = super()._ik_phys(Q)
        n = len(Q); self._dK2 = np.zeros(n); self._X2a = (X2[0], X2[1]); self._k2pose = np.zeros(n, bool)
        P = self.p
        if not P.get("k2"): return q, ok, X1, X2, X3, s
        L = self.law2()
        if not L.get("ok"): return q, ok, X1, X2, X3, s
        u1, u2, u3 = self.u; uK = self.uK; uK2 = L["uK2"]; c3 = self.c[2]; m = KIT.FOLD_MARGIN; b1 = float(P["bk1"])
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1))); st = self._state
        thL = L["th"]
        idx = np.nonzero((st == 1) & (th >= L["th_on"] - 1e-9) & (th <= thL[-1] + 1e-9))[0]
        if not len(idx): return q, ok, X1, X2, X3, s
        tt = np.interp(th[idx], thL, L["ts"]); q2s = L["q2hi"] + L["s_q"] * tt
        dk1 = np.interp(tt, L["ts"], L["dK"]); dk2 = np.interp(tt, L["ts"], L["dK2"])
        Rq = S.rotm(u2, q2s); RK = S.rotm(uK, dk1); RK2 = S.rotm(uK2, dk2)
        p = np.einsum("nij,nj->ni", Rq, np.einsum("nij,j->ni", RK2, u3))
        q1 = S.sub1(u1, np.einsum("nij,nj->ni", RK, p), w[idx]); R1 = S.rotm(u1, q1)
        R2a = R1 @ RK @ Rq; R12 = R2a @ RK2
        vv = KR.unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (len(idx), 3)), np.einsum("nji,njk,k->ni", R12, Q[idx], vv))
        R3 = S.rotm(u3, q3); R123 = R12 @ R3; t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        sv = np.einsum("nji,nj->ni", Q[idx], t3)
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RK, u2) @ u1, -1, 1)))
        a2e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RK2, u3) @ u2, -1, 1)))
        cK = np.degrees(np.arccos(np.clip(p @ uK, -1, 1)))
        msub = np.minimum.reduce([th[idx] - np.abs(b1 - cK), b1 + cK - th[idx], 360 - b1 - cK - th[idx]])
        m3e = KR.dyad_margin(th[idx], a1e, a2e)
        okn = (msub >= m - 1e-6) & (m3e >= m - 1e-6) & bool(self.k_ok) & bool(self.stops_ok)
        q = q.copy(); ok = ok.copy(); s = s.copy()
        q[idx] = np.stack([q1, q2s, q3], 1); ok[idx] = okn
        s[idx] = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        X1 = (X1[0].copy(), X1[1].copy()); X1[0][idx] = R1
        X2 = (X2[0].copy(), X2[1].copy()); X2[0][idx] = R12; X2[1][idx] = 0.0
        X3 = (X3[0].copy(), X3[1].copy()); X3[0][idx] = R123; X3[1][idx] = t3
        X1b = (self._X1b[0].copy(), self._X1b[1].copy()); X1b[0][idx] = R1 @ RK; self._X1b = X1b
        X2a = (X2[0].copy(), X2[1].copy()); X2a[0][idx] = R2a; self._X2a = X2a
        self._dK = self._dK.copy(); self._dK[idx] = dk1
        self._a1e = self._a1e.copy(); self._a1e[idx] = a1e
        self._msub = self._msub.copy(); self._msub[idx] = msub
        self._m3e = self._m3e.copy(); self._m3e[idx] = m3e
        if hasattr(self, "_camt"): self._camt = self._camt.copy(); self._camt[idx] = np.degrees(tt)
        self._dK2[idx] = dk2; self._k2pose[idx] = True; self._q2now = q[:, 1]
        return q, ok, X1, X2, X3, s


class T2Geo(PK._Geo):
    """link rows over the 5 hubs: L1a (hub1-K, m1), L1b (K-hub2, m7), L2a (hub2-K2, m10), L2b (K2-hub3, m2)"""
    def add_links(self, F):
        D = self.D; U = [D.u[0], D.uK, D.u[1], D.uK2, D.u[2]]; Cc = [D.c[0], np.zeros(3), D.c[1], np.zeros(3), D.c[2]]
        hr = [self.hr[0], S.HUB_R, self.hr[1], S.HUB_R, self.hr[2]]; SP = S.SPACING
        C = [Cc[k] + F[k] * U[k] for k in range(5)]; out = []
        for name, ka, kb, mem in (("L1a", 0, 1, 1), ("L1b", 1, 2, 7), ("L2a", 2, 3, M2L), ("L2b", 3, 4, 2)):
            da, db = unit(C[ka]), unit(C[kb]); R = 0.5 * (np.linalg.norm(C[ka]) + np.linalg.norm(C[kb]))
            ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
            nn = max(4, int(R * ang / SP)); ts = (np.arange(nn) + 0.5) / nn
            dirs = np.array([unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db) for t in ts])
            rows = []
            for v in (-3.0, -1.0, 1.0, 3.0):
                dv = unit(dirs + (v / R) * bn); pts = R * dv
                def off_axis(k): w = pts - Cc[k]; return np.linalg.norm(w - (w @ U[k])[:, None] * U[k], axis=1)
                keep = (off_axis(ka) > hr[ka]) & (off_axis(kb) > hr[kb])
                rows.append((dv, keep, ts * R * ang))
            out.append(dict(name=name, mem=mem, ka=ka, kb=kb, rows=rows, U=U, C=Cc))
        self.links = out
        return out


class _RK2(float):
    crown = S.CROWN


class _Cap2(tuple):
    capk2 = True


def apply_cap2(Mo, dh):
    """hub K2's clock-spring cap dh mm taller (crown side), idempotent"""
    if dh <= 0 or "hubK2" not in getattr(Mo, "cyl", {}): return
    r = _RK2(float(Mo.cyl_r["hubK2"])); r.crown = S.CROWN + dh; Mo.cyl_r = dict(Mo.cyl_r); Mo.cyl_r["hubK2"] = r
    base = Mo.sd_cylr
    def sd_cyl(Pw, cen, ax, r=None):
        rr = max(Mo.hr) if r is None else r
        return base(Pw, cen, ax, rr, getattr(rr, "crown", S.CROWN))
    Mo.sd_cyl = sd_cyl
    mem, cen, ax = Mo.cyl["hubK2"]; e, f = S.frame_of(ax); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); H = S.CROWN + dh
    pts = [cen + z * ax + float(r) * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, H, 7)]
    dd = S.disc(float(r), 4.0); pts.append(cen + H * ax + dd[:, :1] * e + dd[:, 1:] * f); Mo.cyl_surf = dict(Mo.cyl_surf); Mo.cyl_surf["hubK2"] = (mem, np.concatenate(pts))
    ang32 = np.linspace(0, 2 * np.pi, 32, endpoint=False); ring = float(r) * (np.cos(ang32)[:, None] * e + np.sin(ang32)[:, None] * f)
    extra = [_Cap2((mem, cen + z * ax + ring)) for z in np.linspace(S.CROWN, H, 3)]
    dd2 = S.disc(float(r), 2.0); extra.append(_Cap2((mem, cen + H * ax + dd2[:, :1] * e + dd2[:, 1:] * f)))
    Mo.contact = [c for c in Mo.contact if not isinstance(c, _Cap2)] + extra


def _ring(c, r, axv, n=16):
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False); a, b = S.frame_of(axv)
    return c + r * (np.cos(ang)[:, None] * a + np.sin(ang)[:, None] * b)


class TModel(SC.SCModel):
    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, params, verbose)
        self.cyl_r = dict(self.cyl_r); self.cyl_r["hubK2"] = S.HUB_R
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)                       # continuity() overwrote the design's side outputs
        self.X[M2L] = self.D._X2a; self.dK2 = self.D._dK2.copy(); self.k2pose = self.D._k2pose.copy()

    def run(self, B=None):
        dh2 = float(self.p.get("capK2", 0) or 0)
        if dh2 > 0 and self.p.get("k2"):
            fit0 = self.fit
            def fit_cap2(): fit0(); apply_cap2(self, dh2)
            self.fit = fit_cap2
        return super().run()

    def T(self, m, i):
        if m == M2L: R, t = self.X[M2L]; return R[i], t[i]
        return super().T(m, i)

    def _geo(self):
        g = super()._geo(); D = self.D
        if not hasattr(D, "uK2"): D.k2_seat()
        e, f = S.frame_of(D.uK2); d = S.disc(S.HUB_R); g["hubK2"] = (M2L, d[:, :1] * e + d[:, 1:] * f, D.uK2)
        return g

    def _greedy(self, keep0=None, links=True):
        poses = self.poses_fit; kind = np.array([self.B.kind[i] for i in poses]); BIG = S.BIG
        ncl = sum(1 for k in self.B.kind if k == "clip"); nws = len(self.B.kind) - ncl
        H, L = self.Hneed, self.Lneed
        groups = [("g", H["hub1"]), ("g", H["hubK"]), ("g", H["hub2"]), ("g", H["hubK2"]), ("g", H["stack"]), ("g", H["h3"])] + \
                 ([("s", r) for rows in L.values() for r in rows] if links else [])
        keep = np.ones(len(poses), bool) if keep0 is None else keep0.copy()
        for typ, M in groups: keep &= ~(M >= BIG / 2).any(1)
        def score(keep):
            if not keep.any(): return 1e9
            cl = keep & (kind == "clip"); inb = tot = 0
            for typ, M in groups:
                top = M[keep].max() if typ == "g" else M[keep].max(0)
                ex = top - M[cl]; inb += float((ex <= 12.0).sum()); tot += ex.size
            ib = inb / max(tot, 1); fol = cl.sum() / ncl; rch = (keep & (kind == "ws")).sum() / nws; con = (~keep).sum() / len(keep)
            return 100 * (max(0, .9 - ib) + max(0, .95 - fol) + max(0, .9 - rch)) + 100 * con
        cur = score(keep)
        for it in range(60 if self.p.get("drop", 1) else 0):
            best, bk = cur, None
            for typ, M in groups:
                need = np.where(keep, M.max(1), -1e9); order = np.argsort(-need)
                for k in range(1, 9):
                    sel = order[:k]; sel = sel[keep[sel]]
                    if not len(sel): continue
                    k2 = keep.copy(); k2[sel] = False; sc = score(k2)
                    if sc < best - 1e-6: best, bk = sc, k2
            if bk is None: break
            keep = bk; cur = best
        self.drop = ~keep

    def fit(self):
        D = self.D; P = D.p
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g; off_k = P["tp"] + S.RUN
        order = ["hub1", "hubK", "hub2", "hubK2", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        H = {"hub1": res["hub1"], "hubK": res["hubK"], "hub2": res["hub2"], "hubK2": res["hubK2"], "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], res["pad"], res["knee"] - off_k], 1)}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self._greedy(links=False); keep1 = ~self.drop
        F = [H["hub1"][keep1].max(), H["hubK"][keep1].max(), H["hub2"][keep1].max(), H["hubK2"][keep1].max(), H["h3"][keep1].max()]
        geo = T2Geo(D, self.hr); geo.add_links(F); self.geo = geo
        self._tr_fit = H["stack"][keep1].max()
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2b" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        L["E"] = [self._HE]; self.Lneed = L
        self._greedy(keep0=keep1)
        self.finalize()
        self._truncate()

    def finalize(self):
        D = self.D; P = D.p; keep = ~self.drop; g = self.g; off_k = P["tp"] + S.RUN
        H = self.Hneed
        f1 = H["hub1"][keep].max(); fK = H["hubK"][keep].max(); f2 = H["hub2"][keep].max(); fK2 = H["hubK2"][keep].max()
        tr = H["stack"][keep].max(); f3 = H["h3"][keep].max()
        hE = self._HE[keep].max(0) if keep.any() else self._HE.max(0)
        xs, rE, f3, tr = self._E_profile(hE, f3, tr)
        self.f = [f1, f2, f3]; self.fK = fK; self.fK2 = fK2; self.tr = tr; self.zb = tr
        k = math.tan(S.RAMP * D2R); rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in self.Lneed.items()}
        lvl = {("L1a", 0): 0.0, ("L1a", 1): 0.0, ("L1b", 1): S.UP, ("L1b", 2): 0.0, ("L2a", 2): S.UP, ("L2a", 3): 0.0,
               ("L2b", 3): S.UP, ("L2b", 4): S.UP}
        F5 = [f1, fK, f2, fK2, f3]; self.link_pts = {}
        for lk in self.geo.links:
            U, Cc = lk["U"], lk["C"]; pts_all = []
            for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
                r = r.copy(); Sx = sarc
                for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                    idx = np.nonzero(keep_s)[0]
                    if not len(idx): continue
                    j = idx[0] if end == 0 else idx[-1]
                    cen = Cc[kk] + F5[kk] * U[kk]; den = float(dv[j] @ U[kk])
                    rc = (cen @ U[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                    r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
                r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
                pts_all.append(dv[keep_s] * r[keep_s][:, None])
            self.link_pts[lk["name"]] = (lk["mem"], np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))
        sn = D.sn; hx = np.interp(self._Ex, xs, rE); self.hEx = hx; u = D.u
        self.rigid = {"hub1": (0, g["hub1"][1] + f1 * u[0]), "hubK": (1, g["hubK"][1] + fK * D.uK), "hub2": (7, g["hub2"][1] + f2 * u[1]),
                      "hubK2": (M2L, g["hubK2"][1] + fK2 * D.uK2),
                      "hub3": (3, g["hub3"][1] + f3 * u[2]), "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tr * sn),
                      "pad": (5, g["pad"][1] + tr * sn), "knee": (6, g["knee"][1] + (tr + off_k) * sn)}
        self._contact_only(); self._solids()
        self._rod_metal()                                              # drive 1: the lead's sidecar RSSR (per-pose, its own range)
        if P.get("k2") and P.get("drv2", 1): self._rod2_metal()        # drv2 0 = the spec's gate (1)/(2) control: drive-2 metal off

    def _rod2_metal(self):
        """drive 2 (rigid at rest on link 2a, see the docstring): crank-2 boss O10 x 6 on link 2a beside hub 2 toward K2
        (outboard of the hub2-K2 line by 6 mm), long arm La2 3 x 6 lying sideways (outboard, as the lead's crank), O3 rod from the arm tip to a horn
        lug of link 2b beside hub K2 at strap level (r_h2 out, sideways), M2 ball-link rings at both ends"""
        D = self.D; P = D.p; u2, uK2 = D.u[1], D.uK2; fK2, f2 = self.fK2, self.f[1]
        L2a = self.link_pts["L2a"][1]
        if not len(L2a): return
        ax = unit(np.cross(u2, uK2))
        # no room between the two O20 hubs: the crank-2 pivot sits off the hub2-K2 line, at HUB_R + boss r + 1 from BOTH axes
        c2, cK2 = f2 * u2, fK2 * uK2; dmid = 0.5 * float(np.linalg.norm(cK2 - c2)); rr = S.HUB_R + 5.0 + 1.0
        off = math.sqrt(max(rr ** 2 - dmid ** 2, 0.0)) + 0.5
        dR = unit(0.5 * (c2 + cK2) + off * ax)
        near = L2a[np.argsort(np.linalg.norm(unit(L2a) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max())
        zboss = lev + S.T_LINK + SC.RUNG
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0)
        boss = dR * zboss + dd[:, :1] * e + dd[:, 1:] * f
        tK = unit(ax - (ax @ dR) * dR); bn = unit(np.cross(dR, tK)); La2 = float(P["La2"])   # long arm sideways (outboard), as drive 1
        rs = np.arange(5.0, La2 + 1e-6, 2.0); ws_ = np.array([-3.0, -1.0, 1.0, 3.0])
        arm = np.array([dR * zboss + r_ * tK + w_ * bn for r_ in rs for w_ in ws_])
        tip = dR * (zboss + S.T_LINK + SC.ZB) + La2 * tK
        sideK = unit(np.cross(uK2, unit(u2 - (u2 @ uK2) * uK2))) * (1.0 if float(ax @ unit(np.cross(uK2, unit(u2 - (u2 @ uK2) * uK2)))) >= 0 else -1.0)
        lvK = fK2 + S.UP; rh2 = float(P["r_h2"])
        hornP = uK2 * (lvK + S.T_LINK + SC.ZB) + rh2 * sideK
        bnK = unit(np.cross(uK2, sideK))
        horn = np.array([uK2 * lvK + r_ * sideK + w_ * bnK for r_ in np.arange(S.HUB_R + 0.5, rh2 + 4.0 + 1e-6, 2.0) for w_ in (-3.0, -1.0, 1.0, 3.0)])
        Lrod = float(np.linalg.norm(hornP - tip)); nr = max(3, int(Lrod / S.SPACING)); sg = np.linspace(0, 1, nr)[:, None]
        rodc = tip[None] * (1 - sg) + hornP[None] * sg
        self.rigid["crank2"] = (M2L, np.concatenate([boss, arm]))
        self.rigid["rod2"] = (M2L, rodc - 1.5 * unit(rodc))
        self.rigid["horn2"] = (2, horn)
        ends = np.concatenate([_ring(tip - SC.ZB * dR, SC.ER, dR), _ring(hornP - SC.ZB * uK2, SC.ER, uK2)])
        self.rigid["rodends2"] = (M2L, ends)
        endsT = np.concatenate([_ring(tip + 3.5 * dR, SC.ER, dR), _ring(hornP + 3.5 * uK2, SC.ER, uK2)])
        cyl = np.concatenate([_ring(dR * z, 5.0, dR) for z in np.linspace(zboss, zboss + SC.BOSS_H, 4)])
        self.contact.append((M2L, np.concatenate([ends, endsT, cyl, arm + S.T_LINK * dR, rodc + 1.5 * unit(rodc)])))
        self.contact.append((2, horn + S.T_LINK * uK2))
        self.strap["ROD2"] = (M2L, np.concatenate([ends, endsT, rodc]))
        self.strap["CRK2"] = (M2L, np.concatenate([cyl, arm + 1.5 * dR]))
        self.strap["HORN2"] = (2, horn + 1.5 * uK2)
        self._rod2_info = dict(boss_level=round(zboss, 1), rod_len=round(Lrod, 1), r_h2=rh2, La2=La2,
                               hub2_K2_centre_mm=round(float(np.linalg.norm(fK2 * uK2 - f2 * u2)), 1))

    def _hubs(self):
        D = self.D; return [("hub1", D.u[0], D.c[0], self.f[0], 0), ("hubK", D.uK, np.zeros(3), self.fK, 1),
                            ("hub2", D.u[1], D.c[1], self.f[1], 7), ("hubK2", D.uK2, np.zeros(3), self.fK2, M2L),
                            ("hub3", D.u[2], D.c[2], self.f[2], 3)]

    def collide(self, i):
        """min clearance (mm) between non-adjacent parts at pose i (split-knuckle's 5-hub pairs + both drives); adjacent
        pairs below 0.15 mm jam (-1)"""
        fr = self.fr; h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        surf = {k_: tf(m, X) for k_, (m, X) in self.cyl_surf.items()}
        strap = {k_: tf(m, X) for k_, (m, X) in self.strap.items()}
        Em = tf(*self.Emid); bx = self._boxes_at_final(i)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def vbox(X, nm, extra=0.0): cen, R, half = bx[nm]; return float(self.sd_box(X, cen, R, half).min()) - extra if len(X) else 1e9
        def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
        def ss(A, Bq, extra=2 * h): return float(cKDTree(Bq).query(A)[0].min()) - extra if len(A) and len(Bq) else 1e9
        c, adj = {}, {}
        hn = ["hub1", "hubK", "hub2", "hubK2", "hub3"]
        for a in range(5):
            for b in range(a + 1, 5): c[f"{hn[a]}-{hn[b]}"] = vcyl(surf[hn[b]], hn[a])
        ends = {"L1a": ("hub1", "hubK"), "L1b": ("hubK", "hub2"), "L2a": ("hub2", "hubK2"), "L2b": ("hubK2", "hub3")}
        for L, ee in ends.items():
            for hb in hn:
                if hb not in ee: c[f"{L}-{hb}"] = vcyl(strap[L], hb, h)
        c["L1a-L2a"] = ss(strap["L1a"], strap["L2a"]); c["L1a-L2b"] = ss(strap["L1a"], strap["L2b"]); c["L1b-L2b"] = ss(strap["L1b"], strap["L2b"])
        c["L1a-L1b"] = ss(far(strap["L1a"], "hubK", 4), far(strap["L1b"], "hubK", 4))
        c["L1b-L2a"] = ss(far(strap["L1b"], "hub2", 4), far(strap["L2a"], "hub2", 4))
        c["L2a-L2b"] = ss(far(strap["L2a"], "hubK2", 4), far(strap["L2b"], "hubK2", 4))
        for nm in ("knee", "pad"):
            for hb in ("hub1", "hubK", "hub2", "hubK2"): c[f"{nm}-{hb}"] = vbox(surf[hb], nm)
            for L in ends: c[f"{nm}-{L}"] = vbox(strap[L], nm, h)
        c["pad-hub3"] = vbox(surf["hub3"], "pad"); c["pad-E"] = vbox(Em, "pad", h)
        for hb in ("hub1", "hubK", "hub2", "hubK2"): c[f"E-{hb}"] = vcyl(Em, hb, h)
        c["E-L1a"] = ss(Em, strap["L1a"]); c["E-L1b"] = ss(Em, strap["L1b"]); c["E-L2a"] = ss(Em, strap["L2a"])
        L2f = far(strap["L2b"], "hub3", 1)
        if len(L2f): adj["E-L2b"] = ss(Em, L2f)
        adj["knee-hub3"] = vbox(surf["hub3"], "knee")
        pa = tf(3, fr["A0"][None])[0]; Ef = Em[np.linalg.norm(Em - pa, axis=1) > BOSS_R + 0.5]
        adj["knee-E"] = vbox(Ef, "knee", h) if len(Ef) else 1e9
        # drive 1 (the lead's sidecar: rod 8, crank 9 on link 1b, horn on link 1a)
        if "ROD" in strap:
            RD, CK, HN = strap["ROD"], strap["CRK"], strap["HORN"]
            for hb in ("hub1", "hubK2", "hub3"): c[f"ROD-{hb}"] = vcyl(RD, hb)
            c["ROD-hubK"] = vcyl(RD, "hubK"); c["ROD-hub2"] = vcyl(RD, "hub2")
            c["ROD-L1a"] = ss(far(RD, "hubK", 8.0), strap["L1a"], h); c["ROD-L1b"] = ss(far(RD, "hub2", 4), far(strap["L1b"], "hub2", 4), h)
            c["ROD-L2a"] = ss(RD, strap["L2a"], h); c["ROD-L2b"] = ss(RD, strap["L2b"], h)
            for hb in ("hub1", "hubK", "hubK2", "hub3"): c[f"CRK-{hb}"] = vcyl(CK, hb, h)
            c["CRK-hub2"] = vcyl(far(CK, "hub2", 6.5), "hub2", h)
            c["CRK-L1a"] = ss(CK, strap["L1a"], 2 * h); c["CRK-L2a"] = ss(CK, strap["L2a"], 2 * h); c["CRK-L2b"] = ss(CK, strap["L2b"], 2 * h)
            c["HORN-L1b"] = ss(far(HN, "hubK", 1.0), far(strap["L1b"], "hubK", 1.0), 2 * h)
            c["HORN-hub2"] = vcyl(HN, "hub2", h); c["HORN-hubK2"] = vcyl(HN, "hubK2", h)
            c["HORN-L2a"] = ss(HN, strap["L2a"], 2 * h); c["HORN-L2b"] = ss(HN, strap["L2b"], 2 * h)
            for nm in ("knee", "pad"): c[f"{nm}-ROD"] = vbox(RD, nm); c[f"{nm}-CRK"] = vbox(CK, nm, h); c[f"{nm}-HORN"] = vbox(HN, nm, h)
            c["E-ROD"] = ss(Em, RD, h); c["E-CRK"] = ss(Em, CK, 2 * h); c["E-HORN"] = ss(Em, HN, 2 * h)
        # drive 2 (crank 2 + rod 2 on link 2a, horn 2 on link 2b)
        if "ROD2" in strap:
            R2, C2, H2 = strap["ROD2"], strap["CRK2"], strap["HORN2"]
            for hb in ("hub1", "hubK", "hub3"): c[f"ROD2-{hb}"] = vcyl(R2, hb); c[f"CRK2-{hb}"] = vcyl(C2, hb, h); c[f"HORN2-{hb}"] = vcyl(H2, hb, h)
            c["ROD2-hub2"] = vcyl(far(R2, "hub2", 1.0), "hub2"); c["ROD2-hubK2"] = vcyl(far(R2, "hubK2", float(self.p["r_h2"]) - 1.0), "hubK2")
            c["CRK2-hub2"] = vcyl(far(C2, "hub2", 6.5), "hub2", h); c["CRK2-hubK2"] = vcyl(C2, "hubK2", h)
            c["HORN2-hub2"] = vcyl(H2, "hub2", h)
            for L in ("L1a", "L1b", "L2b"): c[f"ROD2-{L}"] = ss(R2, strap[L], h); c[f"CRK2-{L}"] = ss(C2, strap[L], 2 * h)
            c["HORN2-L1a"] = ss(H2, strap["L1a"], 2 * h); c["HORN2-L1b"] = ss(H2, strap["L1b"], 2 * h)
            c["HORN2-L2a"] = ss(far(H2, "hubK2", 1.0), far(strap["L2a"], "hubK2", 1.0), 2 * h)
            for nm in ("knee", "pad"): c[f"{nm}-ROD2"] = vbox(R2, nm); c[f"{nm}-CRK2"] = vbox(C2, nm, h); c[f"{nm}-HORN2"] = vbox(H2, nm, h)
            c["E-ROD2"] = ss(Em, R2, h); c["E-CRK2"] = ss(Em, C2, 2 * h); c["E-HORN2"] = ss(Em, H2, 2 * h)
            if "ROD" in strap:
                c["ROD-ROD2"] = ss(strap["ROD"], R2, 0.0); c["CRK-CRK2"] = ss(strap["CRK"], C2, 2 * h); c["CRK-ROD2"] = ss(strap["CRK"], R2, h)
                c["ROD-CRK2"] = ss(strap["ROD"], C2, h); c["HORN-ROD2"] = ss(strap["HORN"], R2, h); c["ROD-HORN2"] = ss(strap["ROD"], H2, h)
        self.last_clear = {k_: round(v, 1) for k_, v in list(c.items()) + list(adj.items())}
        out = min(c.values())
        if min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out


KB.KDesign = TDesign; KB.KModel = TModel; FL.G.KR.KB.KModel = TModel; FL.G.KR.KB.KDesign = TDesign


def _report(B, params):
    p = dict(PARAMS, **params)
    p["sK2"] = 1 if float(p["sK2"]) >= 0 else -1
    p["bk3"] = min(max(float(p["bk3"]), 12.0), 45.0); p["bk4"] = min(max(float(p["bk4"]), 20.0), 110.0)
    p["r_h2"] = min(max(float(p["r_h2"]), 15.5), 22.0); p["La2"] = min(max(float(p["La2"]), 12.0), 26.0)
    p["s_arm2"] = min(max(float(p["s_arm2"]), 4.0), 6.0); p["r_lobe2"] = min(max(float(p["r_lobe2"]), 7.0), 8.5)
    p["dK2max"] = min(max(float(p["dK2max"]), 0.0), 40.0); p["smt2"] = max(float(p["smt2"]), 5.0)
    r, M = SC._report(B, p)
    D = M.D; ko = M.kin_ok
    L = D.law2() if hasattr(D, "law2") else {}
    k2p = getattr(M, "k2pose", np.zeros(len(B.idx), bool)); dK2 = np.abs(getattr(M, "dK2", np.zeros(len(B.idx))))
    tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    ws = np.array([x == "ws" for x in B.kind]); won = tk & ws & k2p & (dK2 > 1e-6)
    r["k2"] = dict(ok=bool(L.get("ok")), why=L.get("why"), why_end=L.get("why_end"), th_on=round(L["th_on"], 2) if L.get("th_on") else None,
                   th_max=round(L.get("th_max", 0.0), 2), dK2_law_max=round(L.get("dK2_max", 0.0), 1), a2e_max=round(L.get("a2e_max", 0.0), 2),
                   dK1_hold=round(L.get("dK1_hold", 0.0), 1), psi0=round(L.get("psi0", 0.0), 1), pa_max=round(L.get("pa_max", 0.0), 1),
                   crest=round(L.get("crest", 0.0), 2), k2_lawok=int(k2p.sum()), k2_kin=int((ko & k2p & (dK2 > 1e-6)).sum()),
                   won_ws_taken=int(won.sum()), dK2_taken_max=round(float(np.degrees(dK2[won].max())), 1) if won.any() else 0.0,
                   fK2=round(float(getattr(M, "fK2", 0.0)), 1), rod2=getattr(M, "_rod2_info", None))
    if p.get("k2") and r["k2"]["won_ws_taken"] == 0:
        r["k2_idle"] = True; r["honest"] = False              # K2 never opens on a taken pose: the lead + dead metal
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


FROZEN_ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "fK2", "tr", "zb", "_tr_fit", "cyl", "cyl_r", "box", "strap", "cyl_surf", "Emid",
                "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_rod2_info", "sd_cyl")


def _frozen_model(P, nc, nw, exact=True):
    P = dict(PARAMS, **P)
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    r1, M1 = _report(B1, dict(P)); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(TModel):
        def run(self, B=None):                                       # the cap is already in the copied geometry
            return SC.SCModel.run(self)

        def fit(self):
            for a in FROZEN_ATTRS:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if exact: os.environ["CB_EXACT"] = "1"
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_twin", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); B = PVm.held_bench()
    else:
        B = CB.Bench(n_clip=nc, n_ws=nw)
    M = Frozen(B, P2); r = M.run()
    return fit, r, M, B, r1


def frozen(P, nc=110, nw=360):
    fit, r, M, B, r1 = _frozen_model(P, nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array([x == "ws" for x in B.kind]); tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    won = tk & ws & M.k2pose & (np.abs(M.dK2) > 1e-6)
    return dict(fit_fast=fit, fit_k2=r1.get("k2"), frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
                parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), sidecar=getattr(M, "_sc_info", None), rod2=getattr(M, "_rod2_info", None),
                won_ws_taken=int(won.sum()), k2_open_poses=int((M.k2pose & (np.abs(M.dK2) > 1e-6)).sum()),
                dK2_taken_max=round(float(np.degrees(np.abs(M.dK2[won])).max()), 1) if won.any() else 0.0)


def gate(params):
    """the spec's gate (1): law-only coverage. Lead IK (k2 off) vs twin IK on Bench(110,360) (kinematics only: no skin / metal),
    counted from the drive wall; plus the hub2-K2 centre distance at the lead's fitted hub-2 level and a K2 level ~ hub K's"""
    p = dict(PARAMS, **params); out = {}
    old = os.environ.pop("CB_EXACT", None)
    try:
        for nc, nw in ((60, 160), (110, 360)):
            B = CB.Bench(n_clip=nc, n_ws=nw)
            ws = np.array([x == "ws" for x in B.kind]); el = np.array([B.poses[i].get("elev", 0) for i in range(len(B.idx))]) if hasattr(B, "poses") else np.zeros(len(B.idx))
            Q = CB._poses_all()["HG"][B.idx].astype(float); res = {}
            for k2 in (0, 1):
                M = TModel(B, SC._clamp(dict(p, k2=k2))); res[k2] = (np.asarray(M.kin_ok, bool), None, M.D)
            kin0, kin1 = res[0][0], res[1][0]; D = res[1][2]; L = D.law2()
            out[f"{nc}_{nw}"] = dict(kin_ws_lead=round(float(kin0[ws].mean()), 3), kin_ws_twin=round(float(kin1[ws].mean()), 3),
                                     won=int((kin1 & ~kin0 & ws).sum()), lost=int((kin0 & ~kin1).sum()),
                                     ovh_lead=int((kin0 & ws & (el >= 140)).sum()), ovh_twin=int((kin1 & ws & (el >= 140)).sum()), ovh_n=int((ws & (el >= 140)).sum()),
                                     law2={k: (round(v, 2) if isinstance(v, float) else v) for k, v in L.items() if not isinstance(v, np.ndarray)})
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    return out


def viz_export(par):
    """geometry of the fitted design (Bench(60,160)) for docs/concepts/viz/concepts/twin-k2-sidecar-knuckle-3r.js"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, par); D = M.D; P = D.p
    R = lambda v, n=5: [round(float(x), n) for x in v]
    def centre(name):
        lk = [l for l in M.geo.links if l["name"] == name][0]; pts = []
        mem, X = M.link_pts[name]
        for ri in (1, 2):
            dv, ks, _ = lk["rows"][ri]; rr = M.Lneed[name][ri][~M.drop].max(0); pts.append(dv * np.maximum(rr, np.linalg.norm(X, axis=1).min())[:, None])
        c = 0.5 * (pts[0] + pts[1]); return [R(x, 2) for x in c[::2]]
    L2 = D.law2(); sub = slice(None, None, max(1, len(L2["th"]) // 60)) if L2.get("ok") else slice(0, 0)
    vr = getattr(M, "_viz_rod", {}) or {}
    def mid(nm): X = M.rigid[nm][1]; return R(X.mean(0), 3)
    G_ = dict(u=[R(x) for x in D.u], c=[R(x) for x in D.c], uK=R(D.uK), uK2=R(D.uK2), sa=R(D.sa), st=R(D.st), sn=R(D.sn), A=[round(D.a1, 3), round(D.a2, 3)],
              branch=float(D.branch), m=R(D.m), f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), fK2=round(float(M.fK2), 2),
              capK=float(P.get("capK", 0)), capK2=float(P.get("capK2", 0)), tr=round(float(M.tr), 2), tp=round(float(P["tp"]), 3), RUN=S.RUN,
              A0=R(M.fr["A0"]), A0m=R(M.fr["A0m"]), Bm=R(M.fr["Bm"]), eE=R(M.fr["eE"]), psiA=round(math.degrees(D.psiA), 4),
              thLo=round(D.th_lo, 4), thHi=round(D.th_hi, 4), q2s=[round(x, 4) for x in D.q2_stops],
              lawTh=R(L2["th"][sub], 3) if L2.get("ok") else [], lawDK=R(np.degrees(L2["dK"][sub]), 3) if L2.get("ok") else [],
              lawDK2=R(np.degrees(L2["dK2"][sub]), 3) if L2.get("ok") else [],
              lawQ2=R(np.degrees(L2["q2hi"] + L2["s_q"] * L2["ts"][sub]), 3) if L2.get("ok") else [],
              rocker=R(vr.get("rocker", np.zeros(3)), 3), rockerAx=R(vr.get("rockerAx", np.array([0, 0, 1.0]))), rodA=R(vr.get("rodA", np.zeros(3)), 3), rodB=R(vr.get("rodB", np.zeros(3)), 3),
              L1a=centre("L1a"), L1b=centre("L1b"), L2a=centre("L2a"), L2b=centre("L2b"))
    if "rod2" in M.rigid:
        X = M.rigid["rod2"][1]; c2 = M.rigid["crank2"][1][:20].mean(0)
        G_.update(rocker2=R(c2, 3), rocker2Ax=R(unit(c2)), rod2A=R(X[0] + 1.5 * unit(X[0]), 3), rod2B=R(X[-1] + 1.5 * unit(X[-1]), 3))
    keys = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "bk1", "bk2", "sK", "a1max", "smhi", "smlo",
            "capK", "kK", "r_h", "La", "s_arm", "bk3", "bk4", "sK2", "kK2", "smt2", "dK1cap", "dK2max", "capK2", "r_h2", "La2", "s_arm2")
    return dict(P={k: P[k] for k in keys if k in P}, G=G_, report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")})


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "gate":
        print(json.dumps(gate(par), default=float)); sys.exit()
    if mode in ("frozen", "held"):
        t = time.time(); out = frozen(par) if mode == "frozen" else frozen(par, -1, -1); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=a.get("gap_near1"), minmetal=a.get("near_touch_min_mm"),
                              ovh=a.get("overhead140"), won=out["won_ws_taken"], parts=out.get("parts_ib14"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"), reach=r["reach"],
                          inband14=r["inband14"], inband10=r["inband10"], contact=r["contact"], honest=r.get("honest"), why=r.get("why"), ovh=r.get("overhead140"),
                          k2=r.get("k2"), parts=r.get("parts_ib14"), pairs=r.get("parts_pairs"), secs=round(time.time() - t)), default=float))

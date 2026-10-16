"""split-knuckle-twosided-3r (round 7): the verified winner geneva-tail-knuckle-pinknee-3r (rod embodiment: hub-2 rim lobe ->
rocker -> O3 pushrod -> horn on K's cap; K on link 1 opens past the stretched stop) UNCHANGED, plus a second slaved knuckle K2
on LINK 2 near J2 that BENDS link 2 at the FOLDED end, so the effective arc a2e = arc(J2, J3) shortens and the fold limit
th_min = |a1 - a2e| + 5 drops below the winner's th_lo (= |a1 - a2| + smlo, 31.3 deg at the winner).

Chain: scapula handler -> J1 (O20, ACTIVE) -> link 1a -> K (O20 + clock-spring cap, slaved, stretched end) -> link 1b -> J2
(O20, ACTIVE; rotor rim lobe drives K; a SECOND lobe fixed to the stator side drives K2) -> link 2a -> K2 (O20 + clock-spring
cap, slaved, folded end) -> link 2b -> J3 (O20, ACTIVE) -> member 3 -> pin knee (2 passive pins) -> arm pad.
3 ACTIVE DOF (q1, q2, q3 encoders give the pose; K and K2 are functions of q2), 0 passive translations, 4 slaved / passive
rotations (K, K2, 2 knee pins) + the two drives' rockers and rod ends. Members: 0 scapula, 1 link 1a, 7 link 1b, 8 link 2a
(K2 housing, K2's rocker + rod), 2 link 2b (J3 housing), 3 member 3, 5 pad, 6 knee link.

SPEC CORRECTION (stated): the catalogue's "MR63ZZ roller on a 6 x 3 lever on link 2a riding a crown track on hub 2's cap"
cannot drive K2 at the gains the folded side needs. A lever from K2 back to hub 2 is L = bK2a (21-40 deg, 26-49 mm at the
link radius) long, its tip moves SIDEWAYS (perpendicular to link 2's great circle) when K2 turns, so the cam must be a
radial lobe touching it from the side: tan(pa) = L kK2 / r_lobe -> kK2 <= ~0.3 at pa 45. The kinematic gate needs kK2
1.0-1.5. So K2 gets the winner's own embodiment mirrored: a lobe fixed to link 1b (hub 2's STATOR side), a rocker on link
2a beside hub 2, an O3 pushrod to a horn on K2 (low variant `k2_low` 1: the horn is a lug of link 2b beside hub K2 at strap
level, r_horn2 >= 16, rocker ratio i_rock2 <= 3: tan(pa) = kK2 r_horn2 / (i_rock2 r_lobe2); high variant: horn on K2's
cap, tan(pa) = kK2 r_horn2 / r_lobe2).

THE FOLDED LAW (exact, closed form per pose, no spare coordinate - R17). With K on stop A (dK = 0) and J2 past its folded
onset q2lo (the winner's q2 dowel stop, now the onset of the K2 lobe), t = q2 travel past q2lo in the folding sense s_f:
    q2 = q2lo + s_f t,   dK2 = s2 kK2 max(0, t - t0K2)    (constant-pressure spiral lobe; s2 = the sense that bends K2,
                                                            i.e. shortens a2e)
th_f(t) = angle(u1, R(u2, q2) R(uK2, dK2) u3) is pose-independent, so a folded pose (th < th_lo) is solved by inverting th_f
on its valid prefix: th_f strictly FALLING, rate |dq2/dth| <= 3.45, the effective dyad (a1, a2e) keeps the kit's 5-deg
margin, K2's own dyad (bK2a, bK2b) keeps 5 deg (K2 never straight / folded flat), no lift-off (the spring cannot hold K2
off the lobe along the pose's self-motion), dK2 <= stop B2, pressure angle <= pa2_max. Then q1, q3 are closed form.
Clips never reach the folded state on the fit bench (all 8 folded fit poses are workspace poses), so K2 sits on its
dwell (stop A) for every in-band sample and only the folded workspace poses move it.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/split-knuckle-twosided-3r.py [check|gate|redteam] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/split-knuckle-twosided-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("geneva_for_split", os.path.join(HERE, "geneva-tail-knuckle-pinknee-3r.py"))
G = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(G)     # own module copy (its KR / KB copies are private too)
KR, KB, PK, S = G.KR, G.KB, G.PK, G.S
unit = S.unit; D2R = math.pi / 180
ID = "split-knuckle-twosided-3r"
RATE_MAX = 3.45
BOSS_R, PAD_R, KNEE_W = PK.BOSS_R, PK.PAD_R, PK.KNEE_W
REPORT_KEYS = ("k2", "k2_idle", "why", "parts_ib14", "parts_pairs", "plain", "gap_near1", "min_metal_mm", "overhead140", "drive")

# the verified winner (docs/concepts/rows/geneva-tail-knuckle-pinknee-3r.json best_params), rod embodiment
WIN = {"emb_mode": "rod", "kK": 3.1796, "r_horn": 2.4932, "r_lobe": 9.0, "bk1": 31.2491, "bk2": 37.9937, "a1max": 58.3565, "smhi": 13.6865,
       "smlo": 5.2777, "az1": 93.5546, "el1": 67.3642, "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473, "b3": 0.3837, "lE": 67.832,
       "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "capK": 6.0, "tail": 1}
PARAMS = dict(G.PARAMS, **WIN)
PARAMS.update(k2=1, bK2a=37.0, bK2b=62.0, sK2=1, kK2=1.0, t0K2=0.0, B2=60.0, capK2=6.0, k2_low=1, r_horn2=16.0, r_lobe2=9.0, i_rock2=3.0,
              pa2_max=45.0)


def _ang(a, b): return math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b)))))


class SDesign(G.GDesign):
    def law2(self):
        """K2's folded-end law on a t grid (rad of q2 past q2lo); cached per design"""
        if getattr(self, "_law2", None) is not None: return self._law2
        P = self.p; u1, u2, u3 = self.u; m = KIT.FOLD_MARGIN
        b1, b2 = float(P["bK2a"]), float(P["bK2b"]); sK2 = 1.0 if float(P["sK2"]) >= 0 else -1.0
        kK2 = max(0.0, float(P["kK2"])); t0 = max(0.0, float(P.get("t0K2", 0.0)))
        lo = getattr(self, "q2_stops", None)
        if lo is None or not P.get("k2") or kK2 <= 0:
            self._law2 = dict(ok=False, why="off"); return self._law2
        q2lo = math.radians(lo[0])
        uK2 = unit(S.circ_int(u2, b1 * D2R, u3, b2 * D2R, sK2)); self.uK2 = uK2
        a2 = _ang(u2, u3); k_ok = abs(b1 - b2) + m <= a2 <= b1 + b2 - m
        pu2 = u2 - (u2 @ uK2) * uK2; pu3 = u3 - (u3 @ uK2) * uK2
        self.psiA2 = float(math.atan2(float(np.cross(pu2, pu3) @ uK2), float(pu2 @ pu3)))
        if P.get("k2_low"): pa = math.degrees(math.atan(kK2 * float(P["r_horn2"]) / (float(P["i_rock2"]) * float(P["r_lobe2"]))))
        else: pa = math.degrees(math.atan(kK2 * float(P["r_horn2"]) / float(P["r_lobe2"])))
        def th3(q): return _ang(u1, S.rotm(u2, q)[0] @ u3)
        s_f = 1.0 if th3(q2lo + 0.01) < th3(q2lo - 0.01) else -1.0
        ts = np.radians(np.arange(0.0, 90.0 + 1e-9, 0.1)); q2t = q2lo + s_f * ts; td = np.maximum(ts - t0 * D2R, 0.0)
        pick = None
        for s2 in (1.0, -1.0):
            dK = s2 * kK2 * td; v3 = np.einsum("nij,j->ni", S.rotm(uK2, dK), u3); a2e = np.degrees(np.arccos(np.clip(v3 @ u2, -1, 1)))
            if a2e[-1] < a2e[0] - 1e-6: pick = (s2, dK, v3, a2e); break
        if pick is None or not k_ok or pa > float(P["pa2_max"]) + 1e-9:
            self._law2 = dict(ok=False, why="sign" if pick is None else "k2dyad" if not k_ok else "pressure", uK2=uK2, pa=pa); return self._law2
        s2, dK, v3, a2e = pick
        p = np.einsum("nij,nj->ni", S.rotm(u2, q2t), v3); th = np.degrees(np.arccos(np.clip(p @ u1, -1, 1)))
        cps = (np.cos(a2e * D2R) - math.cos(b1 * D2R) * math.cos(b2 * D2R)) / (math.sin(b1 * D2R) * math.sin(b2 * D2R))
        psi = np.degrees(np.arccos(np.clip(cps, -1, 1))); msK2 = np.minimum(psi, 180 - psi)
        dth = np.gradient(th, ts); rate = 1.0 / np.maximum(-np.radians(dth), 1e-12)
        a1 = self.a1; m3e = np.minimum(th - np.abs(a1 - a2e), np.minimum(a1 + a2e, 360 - a1 - a2e) - th)
        h = 1e-4; kabs = np.abs(dK)
        def th_of(tt, kk):
            R = S.rotm(uK2, s2 * kk); R2_ = S.rotm(u2, q2lo + s_f * tt)
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R2_, np.einsum("nij,j->ni", R, u3)) @ u1, -1, 1)))
        a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
        sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k); dk = np.gradient(kabs, ts)
        lift = (sC > 1e-9) & (sC < dk - 1e-9) & (kabs > 1e-6)
        good = (dth < 0) & (rate <= RATE_MAX) & (m3e >= m - 1e-6) & (msK2 >= m - 1e-6) & ~lift & (np.degrees(kabs) <= float(P["B2"]) + 1e-9)
        good[0] = True
        nval = int(np.argmin(good)) if not good.all() else len(good); j = min(nval, len(good) - 1)
        why = None if nval == len(good) else ("rate" if not (dth[j] < 0 and rate[j] <= RATE_MAX) else "m3e" if m3e[j] < m else
                                              "K2dyad" if msK2[j] < m else "liftoff" if lift[j] else "stopB2")
        self._law2 = dict(ok=nval > 1, uK2=uK2, s_f=s_f, s2=s2, q2lo=q2lo, ts=ts[:nval], dK=dK[:nval], th=th[:nval], a2e=a2e[:nval],
                          m3e=m3e[:nval], pa=pa, why_end=why, th_min=float(th[:nval].min()), dK_max=float(np.degrees(kabs[:nval].max())),
                          t_max=float(np.degrees(ts[nval - 1])), psi0=float(abs(math.degrees(self.psiA2))))
        return self._law2

    def _ik_phys(self, Q):
        q, ok, X1, X2, X3, s = super()._ik_phys(Q)
        n = len(Q); self._dK2 = np.zeros(n); self._X2a = (X2[0], X2[1]); self._k2pose = np.zeros(n, bool)
        P = self.p
        if not P.get("k2"): return q, ok, X1, X2, X3, s
        L = self.law2()
        if not L.get("ok"): return q, ok, X1, X2, X3, s
        u1, u2, u3 = self.u; uK2 = L["uK2"]; c3 = self.c[2]
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1))); st = self._state
        thL = L["th"]
        idx = np.nonzero((st == -1) & (th >= thL.min() - 1e-9) & (th < self.th_lo + 1e-9))[0]
        if not len(idx): return q, ok, X1, X2, X3, s
        tt = np.interp(th[idx], thL[::-1], L["ts"][::-1]); q2s = L["q2lo"] + L["s_f"] * tt; dk2 = np.interp(tt, L["ts"], L["dK"])
        Rq = S.rotm(u2, q2s); RK2 = S.rotm(uK2, dk2); p = np.einsum("nij,nj->ni", Rq, np.einsum("nij,j->ni", RK2, u3))
        q1 = S.sub1(u1, p, w[idx]); R1 = S.rotm(u1, q1); R2a = R1 @ Rq; R12 = R2a @ RK2
        vv = KR.unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (len(idx), 3)), np.einsum("nji,njk,k->ni", R12, Q[idx], vv))
        R3 = S.rotm(u3, q3); R123 = R12 @ R3; t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        sv = np.einsum("nji,nj->ni", Q[idx], t3)
        q = q.copy(); ok = ok.copy(); s = s.copy()
        q[idx] = np.stack([q1, q2s, q3], 1); ok[idx] = bool(self.k_ok) & bool(self.stops_ok)
        s[idx] = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        X1 = (X1[0].copy(), X1[1].copy()); X1[0][idx] = R1
        X2 = (X2[0].copy(), X2[1].copy()); X2[0][idx] = R12
        X3 = (X3[0].copy(), X3[1].copy()); X3[0][idx] = R123; X3[1][idx] = t3
        X1b = (self._X1b[0].copy(), self._X1b[1].copy()); X1b[0][idx] = R1; self._X1b = X1b
        X2a = (X2[0].copy(), X2[1].copy()); X2a[0][idx] = R2a; self._X2a = X2a
        self._dK2[idx] = dk2; self._k2pose[idx] = True
        self._msub = self._msub.copy(); self._msub[idx] = 99.0
        self._m3e = self._m3e.copy(); self._m3e[idx] = np.interp(tt, L["ts"], L["m3e"])
        self._q2now = q[:, 1]
        return q, ok, X1, X2, X3, s


class S2Geo(PK._Geo):
    def add_links(self, F):
        D = self.D; U = [D.u[0], D.uK, D.u[1], D.uK2, D.u[2]]; Cc = [D.c[0], np.zeros(3), D.c[1], np.zeros(3), D.c[2]]
        hr = [self.hr[0], S.HUB_R, self.hr[1], S.HUB_R, self.hr[2]]; SP = S.SPACING
        C = [Cc[k] + F[k] * U[k] for k in range(5)]; out = []
        for name, ka, kb, mem in (("L1a", 0, 1, 1), ("L1b", 1, 2, 7), ("L2a", 2, 3, 8), ("L2b", 3, 4, 2)):
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
    """hub K2's clock-spring cap dh mm taller (crown side), idempotent (a frozen copy re-applies it)"""
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


class SModel(G.GModel):
    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, params, verbose)
        self.cyl_r = dict(self.cyl_r); self.cyl_r["hubK2"] = S.HUB_R
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)                       # continuity() overwrote the design's side outputs
        self.X[8] = self.D._X2a; self.dK2 = self.D._dK2.copy(); self.k2pose = self.D._k2pose.copy()

    def run(self, B=None):
        dh2 = float(self.p.get("capK2", 0) or 0)
        if dh2 > 0 and self.p.get("k2"):
            fit0 = self.fit
            def fit_cap2(): fit0(); apply_cap2(self, dh2)
            self.fit = fit_cap2
        return super().run()

    def T(self, m, i):
        if m == 8: R, t = self.X[8]; return R[i], t[i]
        return super().T(m, i)

    def _geo(self):
        g = super()._geo(); D = self.D
        L = D.law2() if D.p.get("k2") else {}
        if "uK2" not in L:                                             # K2 seat even when the law is off (metal still exists)
            D.uK2 = unit(S.circ_int(D.u[1], float(D.p["bK2a"]) * D2R, D.u[2], float(D.p["bK2b"]) * D2R, 1.0 if float(D.p["sK2"]) >= 0 else -1.0))
        e, f = S.frame_of(D.uK2); d = S.disc(S.HUB_R); g["hubK2"] = (8, d[:, :1] * e + d[:, 1:] * f, D.uK2)
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
        geo = S2Geo(D, self.hr); geo.add_links(F); self.geo = geo
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
                      "hubK2": (8, g["hubK2"][1] + fK2 * D.uK2),
                      "hub3": (3, g["hub3"][1] + f3 * u[2]), "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tr * sn),
                      "pad": (5, g["pad"][1] + tr * sn), "knee": (6, g["knee"][1] + (tr + off_k) * sn)}
        self._contact_only(); self._solids()
        # the winner's drive (rocker on link 1b, rod to K's horn) - it uses L1b and calls _contact_only/_solids itself
        self._rod_metal()
        if P.get("k2"): self._rod2_metal()

    def _rod_metal(self):
        # the parent's routine reads link_pts["L2"] nowhere; it needs only L1b, hub 2 and K
        return G.GModel._rod_metal(self)

    def _rod2_metal(self):
        """K2's drive, all on member 8 (link 2a; the rod's horn end turns with K2 only on the folded workspace poses - no clip
        frame moves it): rocker O10 on link 2a beside hub 2 toward K2, O3 rod to the horn (low: a lug of link 2b beside hub
        K2 at strap level r_horn2 out; high: K2's cap mid-height at r_horn2), M3 rod-end heads O10 x 5 at both ends"""
        D = self.D; P = D.p; u2, uK2 = D.u[1], D.uK2; fK2, f2 = self.fK2, self.f[1]; capK2 = float(P.get("capK2", 0) or 0)
        L2a = self.link_pts["L2a"][1]
        if not len(L2a): return
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0)
        ax = unit(np.cross(u2, uK2)); dR = unit(S.rotm(ax, g0)[0] @ u2)
        near = L2a[np.argsort(np.linalg.norm(unit(L2a) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max()) + S.T_LINK
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0)
        self.rigid["rocker2"] = (8, dR * lev + dd[:, :1] * e + dd[:, 1:] * f)
        tK = unit(dR - (dR @ uK2) * uK2)
        if P.get("k2_low"):
            top = dR * (lev + 1.0)
            side = unit(np.cross(uK2, tK))                         # the lug sticks out sideways from hub K2 (horn arm)
            hornP = uK2 * (fK2 + S.UP + S.T_LINK + 1.0) + float(P["r_horn2"]) * side
            rs = np.arange(S.HUB_R, float(P["r_horn2"]) + 5.0 + 1e-6, 2.0); ws_ = np.arange(-3.0, 3.01, 2.0)
            self.rigid["horn2"] = (2, np.array([uK2 * (fK2 + S.UP) + r_ * side + w_ * tK for r_ in rs for w_ in ws_]))
        else:
            top = dR * (lev + 9.0); eK, _ = S.frame_of(uK2); hornP = uK2 * (fK2 + S.CROWN + capK2 * 0.5) + float(P["r_horn2"]) * eK
        n = max(3, int(np.linalg.norm(hornP - top) / S.SPACING)); sg = np.linspace(0, 1, n)[:, None]
        rod = top[None] * (1 - sg) + hornP[None] * sg
        self.rigid["rod2"] = (8, rod - 1.5 * unit(rod))
        ang = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        def ring(c, r, axv): a, b = S.frame_of(axv); return c + r * (np.cos(ang)[:, None] * a + np.sin(ang)[:, None] * b)
        ends = np.concatenate([ring(top, 5.0, dR), ring(hornP, 5.0, uK2), ring(top + 5.0 * dR, 5.0, dR), ring(hornP + 5.0 * uK2, 5.0, uK2)])
        cyl = np.concatenate([ring(dR * z, 5.0, dR) for z in np.linspace(lev, lev + (1.0 if P.get("k2_low") else 9.0), 3)])
        self.rigid["rodends2"] = (8, np.concatenate([ring(top, 5.0, dR), ring(hornP, 5.0, uK2)]))
        self.contact.append((8, np.concatenate([ends, cyl, rod + 1.5 * unit(rod)])))
        if "horn2" in self.rigid: self.contact.append((2, self.rigid["horn2"][1] + S.T_LINK * uK2))
        self.strap["ROD2"] = (8, np.concatenate([ends, cyl, rod]))
        self._rod2_info = dict(rocker_level=round(lev, 1), horn_level=round(float(np.linalg.norm(hornP)), 1), rod_len=round(float(np.linalg.norm(hornP - top)), 1))

    def _hubs(self):
        D = self.D; return [("hub1", D.u[0], D.c[0], self.f[0], 0), ("hubK", D.uK, np.zeros(3), self.fK, 1),
                            ("hub2", D.u[1], D.c[1], self.f[1], 7), ("hubK2", D.uK2, np.zeros(3), self.fK2, 8),
                            ("hub3", D.u[2], D.c[2], self.f[2], 3)]

    def collide(self, i):
        """min clearance (mm) between non-adjacent parts at pose i; adjacent pairs below 0.15 mm jam (-1)"""
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
        # the two drives
        for key, mine, skip in (("ROD", "L1b", ("hubK", "hub2", "L1b")), ("ROD2", "L2a", ("hubK2", "hub2", "L2a"))):
            if key not in strap: continue
            RD = strap[key]
            for hb in hn:
                if hb not in skip: c[f"{key}-{hb}"] = vcyl(RD, hb)
            for L in ends:
                if L in skip: continue
                if key == "ROD2" and L == "L2b": c[f"{key}-L2b"] = ss(far(RD, "hubK2", float(self.p["r_horn2"]) + 6.0), far(strap["L2b"], "hubK2", 4), h)
                elif key == "ROD" and L == "L1a": c[f"{key}-L1a"] = ss(far(RD, "hubK", 8.0), strap["L1a"], h)
                else: c[f"{key}-{L}"] = ss(RD, strap[L], h)
            for nm in ("knee", "pad"): c[f"{nm}-{key}"] = vbox(RD, nm)
            c[f"E-{key}"] = ss(Em, RD, h)
        if "ROD" in strap and "ROD2" in strap: c["ROD-ROD2"] = ss(strap["ROD"], strap["ROD2"], 0.0)
        self.last_clear = {k_: round(v, 1) for k_, v in list(c.items()) + list(adj.items())}
        out = min(c.values())
        if min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out


KB.KDesign = SDesign; KB.KModel = SModel                      # KB._report / KB.frozen build through these module globals


def _report(B, params):
    p = dict(PARAMS, **params)
    p["sK2"] = 1 if float(p["sK2"]) >= 0 else -1
    p["bK2a"] = min(max(float(p["bK2a"]), 15.0), 45.0); p["bK2b"] = min(max(float(p["bK2b"]), 10.0), 110.0)
    r, M = G._report(B, p)
    D = M.D; ko = M.kin_ok
    L = D.law2() if hasattr(D, "law2") else {}
    k2p = getattr(M, "k2pose", np.zeros(len(B.idx), bool))
    tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    ws = np.array([x == "ws" for x in B.kind])
    r["k2"] = dict(ok=bool(L.get("ok")), why=L.get("why"), why_end=L.get("why_end"), th_lo=round(float(D.th_lo), 2),
                   th_min=round(L["th_min"], 2) if L.get("ok") else None, dK2_max=round(L.get("dK_max", 0.0), 1), t_max=round(L.get("t_max", 0.0), 1),
                   a2e_min=round(float(L["a2e"].min()), 1) if L.get("ok") else None, pa=round(L.get("pa", 0.0), 1) if L.get("pa") is not None else None,
                   psi0=round(L.get("psi0", 0.0), 1), folded_lawok=int(k2p.sum()), folded_kin=int((ko & k2p).sum()),
                   folded_ws_taken=int((tk & ws & k2p).sum()), folded_clip=int((k2p & ~ws).sum()),
                   fK2=round(float(getattr(M, "fK2", 0.0)), 1), rod2=getattr(M, "_rod2_info", None))
    if p.get("k2") and r["k2"]["folded_ws_taken"] == 0:
        # measured 16:10 (500 farm configs): a K2 that never engages on a taken pose is the winner + dead metal (24.5 at best,
        # near-straight K2 where a2e cannot fall as fast as th); flagged so tools/concept_cma.py adds 100 and never settles there
        r["k2_idle"] = True; r["honest"] = False
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    p = dict(PARAMS, **P); p["sK2"] = 1 if float(p["sK2"]) >= 0 else -1
    out = KB.frozen(p, nc, nw)
    return out


def gate(params):
    """the lead's kill gate: K2's law-only coverage of the folded poses (fit / verify benches) and the hub levels there"""
    p = dict(PARAMS, **params); out = {}
    for nc, nw in ((60, 160), (110, 360)):
        B = CB.Bench(n_clip=nc, n_ws=nw)
        M = SModel(B, dict(p)); D = M.D; L = D.law2()
        fold = M.kstate == -1
        out[f"{nc}_{nw}"] = dict(folded=int(fold.sum()), law=int(M.k2pose.sum()), kin=int((M.kin_ok & M.k2pose).sum()),
                                 why_folded={w: int(((M.why == w) & fold).sum()) for w in set(M.why[fold])},
                                 th_min=round(L.get("th_min", 99), 2), why_end=L.get("why_end"))
        if nc == 60:
            g = M._geo(); poses = np.nonzero(M.kin_ok)[0]; order = ["hub2", "hubK2", "hub3"]
            items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
            res = dict(zip(order, M.needed(items, poses)))
            isk2 = M.k2pose[poses]; lv = {}
            for n in order:
                hm = res[n].max(1)
                lv[n] = dict(rest_max=round(float(np.percentile(hm[~isk2], 100)), 1), rest_p95=round(float(np.percentile(hm[~isk2], 95)), 1),
                             folded=[round(float(x), 1) for x in hm[isk2]])
            out["levels_fit"] = lv
    return out


def viz_export(par):
    """geometry of the fitted design (Bench(60,160)) for docs/concepts/viz/concepts/split-knuckle-twosided-3r.js"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, par); D = M.D; P = D.p
    R = lambda v, n=5: [round(float(x), n) for x in v]
    def centre(name):
        lk = [l for l in M.geo.links if l["name"] == name][0]; keep = ~M.drop; rows = [rr[keep].max(0) for rr in M.Lneed[name]]
        k = math.tan(S.RAMP * D2R); pts = []
        for ri in (1, 2):
            dv, ks, _ = lk["rows"][ri]; pts.append(dv * rows[ri][:, None])
        c = 0.5 * (pts[0] + pts[1]); return [R(x, 2) for x in c[::2]]
    L1 = D.law(); L2 = D.law2(); sub1 = slice(None, None, max(1, len(L1["th"]) // 40)) if L1.get("ok") else slice(0, 0)
    sub2 = slice(None, None, max(1, len(L2["th"]) // 40)) if L2.get("ok") else slice(0, 0)
    def ends(nm):
        X = M.rigid[nm][1]; return R(X[0] + 1.5 * unit(X[0]), 3), R(X[-1] + 1.5 * unit(X[-1]), 3)
    rk = M.rigid["rocker"][1].mean(0); rodA, rodB = ends("rod")
    G_ = dict(u=[R(x) for x in D.u], c=[R(x) for x in D.c], uK=R(D.uK), uK2=R(D.uK2), sa=R(D.sa), st=R(D.st), sn=R(D.sn), A=[round(D.a1, 3), round(D.a2, 3)],
              branch=float(D.branch), m=R(D.m), f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), fK2=round(float(M.fK2), 2),
              capK=float(P.get("capK", 0)), capK2=float(P.get("capK2", 0)), tr=round(float(M.tr), 2), tp=round(float(P["tp"]), 3), RUN=S.RUN,
              A0=R(M.fr["A0"]), A0m=R(M.fr["A0m"]), Bm=R(M.fr["Bm"]), eE=R(M.fr["eE"]), psiA=round(math.degrees(D.psiA), 4),
              thLo=round(D.th_lo, 4), thHi=round(D.th_hi, 4), q2s=[round(x, 4) for x in D.q2_stops],
              lawTh=R(L1["th"][sub1], 3) if L1.get("ok") else [], lawDK=R(np.degrees(L1["dK"][sub1]), 3) if L1.get("ok") else [],
              lawQ2=R(np.degrees(L1["q2t"][sub1]), 3) if L1.get("ok") else [],
              lawThF=R(L2["th"][sub2], 3) if L2.get("ok") else [], lawDK2F=R(np.degrees(L2["dK"][sub2]), 3) if L2.get("ok") else [],
              lawQ2F=R(np.degrees(L2["q2lo"] + L2["s_f"] * L2["ts"][sub2]), 3) if L2.get("ok") else [],
              rocker=R(rk, 3), rockerAx=R(unit(rk)), rodA=rodA, rodB=rodB,
              L1a=centre("L1a"), L1b=centre("L1b"), L2a=centre("L2a"), L2b=centre("L2b"))
    if "rocker2" in M.rigid:
        rk2 = M.rigid["rocker2"][1].mean(0); a, b = ends("rod2"); G_.update(rocker2=R(rk2, 3), rocker2Ax=R(unit(rk2)), rod2A=a, rod2B=b)
    keys = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "bk1", "bk2", "sK", "a1max", "smhi", "smlo",
            "capK", "emb_mode", "kK", "r_horn", "bK2a", "bK2b", "sK2", "kK2", "t0K2", "B2", "capK2", "k2_low", "r_horn2")
    return dict(P={k: P[k] for k in keys}, G=G_, report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")})


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "gate":
        print(json.dumps(gate(par), default=float)); sys.exit()
    if mode == "frozen":
        t = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=a.get("gap_near1"), minmetal=a.get("near_touch_min_mm"),
                              ovh=a.get("overhead140"), parts=out.get("parts_ib14"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"), reach=r["reach"],
                          inband14=r["inband14"], inband10=r["inband10"], contact=r["contact"], why=r.get("why"), ovh=r.get("overhead140"), k2=r.get("k2"),
                          drive=r.get("drive"), parts=r.get("parts_ib14"), pairs=r.get("parts_pairs"), secs=round(time.time() - t)), default=float))
    if mode == "redteam":
        import importlib
        _c = importlib.util.spec_from_file_location("cu_rt", os.path.join(HERE, "cam-unfold-4th.py")); CU = importlib.util.module_from_spec(_c); _c.loader.exec_module(CU)
        CU.redteam(B, M)

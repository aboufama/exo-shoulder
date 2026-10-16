"""minarc-stop-knuckle-4r, VARIANT B (merged from pin-knee-minarc-knuckle-4r): the verified pin-knee chain
(docs/concepts/models/skin-normal-3r-pin-knee.py: J1 / J2 on GH rays, J3 tilted b3 toward the skin normal, the flat
two-pin knee closing member 3 on the cuff) with link 1 split by the passive, sensed, spring-preloaded O20 knuckle K
and J2 interior-angle hard stops. 0 passive translations; passive rotations: K + the 2 knee pins.

Kinematics (exact, the min-arc law of the variant-A model `law()`): the arm fixes w = Q u3 (J3's direction) and J1;
th = angle(u1, w). a1e = a1 (K on stop A) while the 3R closes with the J2 interior angle phi in [phi_lo, phi_hi], else
J2 rests on its stop and K opens to the smallest a1e >= a1 that closes (<= a1max = stop B). K's rotation delta (about
uK, through GH) carries link 1b, J2, link 2, J3 (and J3's offset c3): v2 = RK u2, v3 = RK u3, c3' = RK c3; then the
spherical 3R (u1, v2, v3) is solved in closed form like the seed's ik (z = R1^T w), member transforms
X1 = R1 (link 1a), X1b = R1 RK (link 1b), X2 = R1 R(v2, q2) RK (link 2), X3 = X2 R(u3, q3) with t3 = X2 (c3 - R3 c3);
the knee absorbs the drift s = Q^T t3 exactly as in the pin knee. Members: 0 scapula, 1 link 1a (+ hub K's housing),
7 link 1b (+ hub 2's housing), 2 link 2, 3 member 3 (hub 3 + E strap + boss), 5 arm pad, 6 knee link.
Checks = the pin knee's (VModel rules: closure < 0.5 deg, 10 fps continuity incl. K and the knee, jam rule, every
non-adjacent pair >= 1 mm, adjacent 0.15 mm, walls / crowns / tops skin-checked) + K: hub K vs every part, L1a / L1b vs
every part (L1a-L1b adjacent at K, L1b-L2 adjacent at J2), the forced sub-chain J1-K-J3 fold margin >= SING.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py [check|redteam] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py frozen '<json>' out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, fn):
    sp = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


PK = _load("pinknee_for_minarc", "skin-normal-3r-pin-knee.py")
KA = _load("minarc_variant_a", "minarc-stop-knuckle-4r.py")
S = PK.S; unit = S.unit; D2R = math.pi / 180
ID = "minarc-stop-knuckle-4r"; VARIANT = "B (pin knee + knuckle)"
REPORT_KEYS = ("knuckle", "why", "knee", "parts_ib14", "parts_pairs", "min_clear_taken", "res_max", "seats")
BOSS_R, PAD_R, KNEE_W = PK.BOSS_R, PK.PAD_R, PK.KNEE_W
PARAMS = dict(PK.PARAMS)
# the pin knee's current best seats (rows/skin-normal-3r-pin-knee.json best_params) + the knuckle
PARAMS.update(az1=101.1634, el1=63.8986, az2=30.153, el2=47.0108, wd=70.3931, wa=-8.1248, b3=0.2842, lE=59.5534, lc=28.2401,
              phiE=-5.8107, phib=-54.914, ang_min=30.4611, stk=5.6815,
              bk1=30.0, bk2=50.0, sK=-1, a1max=70.0, phi_lo=15.0, phi_hi=170.0, mstop=0)


def rotmv(U, a):
    """Rodrigues with a per-pose axis: U (n, 3), a (n,) -> (n, 3, 3)"""
    U = unit(U); a = np.asarray(a, float); n = len(U); Kx = np.zeros((n, 3, 3))
    Kx[:, 0, 1], Kx[:, 0, 2], Kx[:, 1, 0], Kx[:, 1, 2], Kx[:, 2, 0], Kx[:, 2, 1] = -U[:, 2], U[:, 1], U[:, 2], -U[:, 0], -U[:, 1], U[:, 0]
    return np.eye(3)[None] + np.sin(a)[:, None, None] * Kx + (1 - np.cos(a))[:, None, None] * (Kx @ Kx)


def sub1v(U, p, q):
    """angle th with rot(U_i, th) p_i = q_i, per-pose axes"""
    pp = p - np.einsum("ij,ij->i", p, U)[:, None] * U; qq = q - np.einsum("ij,ij->i", q, U)[:, None] * U
    return np.arctan2(np.einsum("ij,ij->i", np.cross(pp, qq), U), np.einsum("ij,ij->i", pp, qq))


class KDesign(PK.Design):
    def __init__(self, params=None):
        super().__init__(params); P = self.p
        u1, u2 = self.u[0], self.u[1]; a1 = math.degrees(self.A[0])
        assert np.linalg.norm(self.c[0]) < 1e-6 and np.linalg.norm(self.c[1]) < 1e-6, "variant B needs J1, J2 on GH rays (b1 = b2 = 0)"
        self.a1 = a1; self.a2 = math.degrees(self.A[1])
        sK = 1.0 if float(P["sK"]) >= 0 else -1.0
        self.uK = unit(S.circ_int(u1, P["bk1"] * D2R, u2, P["bk2"] * D2R, sK))
        pu1 = u1 - (u1 @ self.uK) * self.uK; pu2 = u2 - (u2 @ self.uK) * self.uK
        self.psiA = float(math.atan2(np.cross(pu1, pu2) @ self.uK, pu1 @ pu2))     # signed K angle at stop A (rad)
        self.k_ok = (abs(P["bk1"] - P["bk2"]) + S.SING <= a1 <= P["bk1"] + P["bk2"] - S.SING) and (P["a1max"] <= P["bk1"] + P["bk2"] - S.SING)

    def ik(self, Q):
        if not hasattr(self, "uK"): return super().ik(Q)       # OSN's seat set-up at rest (K on stop A = the plain 3R)
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]
        w = Q @ u3; wu1 = w @ u1
        lp = dict(a1=self.a1, a2=self.a2, phi_lo=max(S.SING, float(P["phi_lo"])), phi_hi=min(180 - S.SING, float(P["phi_hi"])))
        a1e, state, th = KA.law(np.broadcast_to(u1, w.shape), w, lp)
        fin = np.isfinite(a1e); a1s = np.where(fin, a1e, self.a1)
        b1, b2 = float(P["bk1"]), float(P["bk2"])
        cpsi = (np.cos(a1s * D2R) - math.cos(b1 * D2R) * math.cos(b2 * D2R)) / (math.sin(b1 * D2R) * math.sin(b2 * D2R))
        psi_e = np.arccos(np.clip(cpsi, -1, 1)); dK = np.sign(self.psiA) * psi_e - self.psiA
        RK = S.rotm(uK, dK) if n else np.zeros((0, 3, 3))
        v2 = RK @ u2; v3 = RK @ u3
        c12 = v2 @ u1; ca2 = math.cos(self.A[1]); det = 1 - c12 ** 2 + 1e-12
        al = (wu1 - c12 * ca2) / det; be = (ca2 - c12 * wu1) / det; cr = np.cross(np.broadcast_to(u1, v2.shape), v2)
        g2 = (1 - al ** 2 - be ** 2 - 2 * al * be * c12) / np.maximum(np.einsum("ij,ij->i", cr, cr), 1e-12)
        best = None
        for sg in (1.0, -1.0):
            z = al[:, None] * u1 + be[:, None] * v2 + sg * np.sqrt(np.clip(g2, 0, None))[:, None] * cr
            q1 = S.sub1(u1, z, w); R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
            p2 = np.einsum("nij,nj->ni", R1, v2); br = np.sign(np.einsum("ij,ij->i", p2, np.cross(np.broadcast_to(u1, w.shape), w)))
            if best is None: best = [q1.copy(), z.copy(), br]
            else:
                pick = br == self.branch; best[0][pick] = q1[pick]; best[1][pick] = z[pick]
        q1, z = best[0], best[1]
        R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
        q2 = sub1v(v2, v3, z); R2p = rotmv(v2, q2) if n else np.zeros((0, 3, 3))
        R12 = R1 @ R2p @ RK; vv = unit(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv))
        R3 = S.rotm(u3, q3) if n else np.zeros((0, 3, 3)); R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        Z0 = np.zeros((n, 3)); X1 = (R1, Z0); X1b = (R1 @ RK, Z0); X2 = (R12, Z0); X3 = (R123, t3)
        sv = np.einsum("nji,nj->ni", Q, t3); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        # validity: law closes and within stop B, the 3R closes, K's range, the forced sub-chain fold margin
        uKw = np.einsum("nij,j->ni", R1, uK); cK = np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", uKw, w), -1, 1)))
        msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
        ok = fin & (a1s <= float(P["a1max"]) + 1e-9) & (g2 > 0) & bool(self.k_ok)
        ok &= (state == 0) | (msub >= S.SING)
        if P.get("mstop"):
            m3 = np.minimum(th - abs(self.a1 - self.a2), self.a1 + self.a2 - th); ok &= (state != 0) | (m3 >= S.SING)
        self._X1b, self._dK, self._state, self._a1e, self._msub = X1b, dK, state, a1s, msub
        return np.stack([q1, q2, q3], 1), ok, X1, X2, X3, s


class KGeo(PK._Geo):
    def add_links(self, f1, fK, f2, f3):
        D = self.D; U = [D.u[0], D.uK, D.u[1], D.u[2]]; Cc = [D.c[0], np.zeros(3), D.c[1], D.c[2]]; F = [f1, fK, f2, f3]
        hr = [self.hr[0], S.HUB_R, self.hr[1], self.hr[2]]; SP = S.SPACING
        C = [Cc[k] + F[k] * U[k] for k in range(4)]; out = []
        for name, ka, kb, mem in (("L1a", 0, 1, 1), ("L1b", 1, 2, 7), ("L2", 2, 3, 2)):
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


class KModel(PK.Model):
    def __init__(self, B, params=None, verbose=False):
        self.fix = dict(S.VModel.fix)
        self.B = B; self.D = KDesign(params); self.p = self.D.p; self.v = verbose
        P = self.p; P["tp"] = (float(P["stk"]) - S.RUN) / 2
        self.hr = [round(float(P.get(f"rad{k + 1}", S.HUB_R)), 2) for k in range(3)]
        for r_ in self.hr:
            if r_ != S.HUB_R: raise ValueError("O20 only (user 2026-10-16)")
        self.cyl_r = {"hub1": self.hr[0], "hubK": S.HUB_R, "hub2": self.hr[1], "hub3": self.hr[2]}
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)
        X1b, self.dK, self.kstate, self.a1e, self.msub = self.D._X1b, self.D._dK, self.D._state, self.D._a1e, self.D._msub
        names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
        _, okc, _, _, _, sc = self.D.ik(Z["HG"][ii].astype(float))
        sv = np.r_[s[ok], sc[okc]]
        if P.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))
        if P.get("m_fix") is not None: self.D.m = np.array(P["m_fix"], float)
        self.D.m[2] = 0.0
        self.radial_span = round(float(np.ptp(sv[:, 2])), 3) if len(sv) else 0.0
        self.drift_span = [round(float(np.ptp(sv[:, k])), 1) for k in range(2)] if len(sv) else [0, 0]
        self.q, self.X, self.s = q, {1: X1, 2: X2, 3: X3, 7: X1b}, s
        self.K = self.D.knee(s)
        self.why = np.array([""] * len(B.idx), dtype=object)
        okf = ok.copy(); self.why[~ok] = "fold"
        kok = self.K["ok"] & (np.abs(s[:, 2]) <= P["R_tol"]); self.why[ok & ~kok] = "slide"; okf &= kok
        cont = self.continuity(); self.why[okf & ~cont] = "flip"; okf &= cont
        self.kin_ok = okf
        R123 = X3[0]; c = (np.einsum("nij,nij->n", R123, self.Q) - 1) / 2
        self.res_deg = np.degrees(np.arccos(np.clip(c, -1, 1)))
        bad = self.kin_ok & (self.res_deg >= 0.5); self.why[bad] = "closure"; self.kin_ok &= ~bad
        self.riser = None

    def continuity(self):
        """10 fps fit clips: q1, q2, q3' = q3 + phi, pin a, pin b AND the knuckle delta; a step > JUMP breaks it"""
        Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; ok_at = {}
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            q, ok, _, _, _, s = self.D.ik(Z["HG"][ii].astype(float)); dK = self.D._dK; K = self.D.knee(s); ok &= K["ok"]
            qq = np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"], dK]; prev = None
            for j, gi in enumerate(ii):
                good = bool(ok[j])
                if good and prev is not None and np.degrees(np.abs(PK.wrap(qq[j] - qq[prev]))).max() > S.JUMP: good = False
                ok_at[int(gi)] = good; prev = j if ok[j] else None
        return np.array([ok_at.get(int(gi), True) for gi in self.B.idx])

    def T(self, m, i):
        if m == 7: R, t = self.X[7]; return R[i], t[i]
        return super().T(m, i)

    def _geo(self):
        g = super()._geo(); D = self.D
        mem, pts, ax = g["hub2"]; g["hub2"] = (7, pts, ax)                        # hub 2's housing rides on link 1b
        e, f = S.frame_of(D.uK); d = S.disc(S.HUB_R); g["hubK"] = (1, d[:, :1] * e + d[:, 1:] * f, D.uK)
        return g

    def greedy_drop(self, keep0=None, links=True):
        return self._greedy(keep0, links)

    def _greedy(self, keep0=None, links=True):
        """= the seed's greedy_drop with hub K as one more flat group"""
        poses = self.poses_fit; kind = np.array([self.B.kind[i] for i in poses]); BIG = S.BIG
        ncl = sum(1 for k in self.B.kind if k == "clip"); nws = len(self.B.kind) - ncl
        H, L = self.Hneed, self.Lneed
        groups = [("g", H["hub1"]), ("g", H["hubK"]), ("g", H["hub2"]), ("g", H["stack"]), ("g", H["h3"])] + ([("s", r) for rows in L.values() for r in rows] if links else [])
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
        order = ["hub1", "hubK", "hub2", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        H = {"hub1": res["hub1"], "hubK": res["hubK"], "hub2": res["hub2"], "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], res["pad"], res["knee"] - off_k], 1)}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self._greedy(links=False); keep1 = ~self.drop
        f1 = H["hub1"][keep1].max(); fK = H["hubK"][keep1].max(); f2 = H["hub2"][keep1].max(); tr = H["stack"][keep1].max(); f3 = H["h3"][keep1].max()
        geo = KGeo(D, self.hr); geo.add_links(f1, fK, f2, f3); self.geo = geo
        self._tr_fit = tr
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
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
        f1 = H["hub1"][keep].max(); fK = H["hubK"][keep].max(); f2 = H["hub2"][keep].max(); tr = H["stack"][keep].max(); f3 = H["h3"][keep].max()
        hE = self._HE[keep].max(0) if keep.any() else self._HE.max(0)
        xs, rE, f3, tr = self._E_profile(hE, f3, tr)
        self.f = [f1, f2, f3]; self.fK = fK; self.tr = tr; self.zb = tr
        k = math.tan(S.RAMP * D2R); rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in self.Lneed.items()}
        lvl = {("L1a", 0): 0.0, ("L1a", 1): 0.0, ("L1b", 1): S.UP, ("L1b", 2): 0.0, ("L2", 2): S.UP, ("L2", 3): S.UP}
        F4 = [f1, fK, f2, f3]; self.link_pts = {}
        for lk in self.geo.links:
            U, Cc = lk["U"], lk["C"]; pts_all = []
            for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
                r = r.copy(); Sx = sarc
                for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                    idx = np.nonzero(keep_s)[0]
                    if not len(idx): continue
                    j = idx[0] if end == 0 else idx[-1]
                    cen = Cc[kk] + F4[kk] * U[kk]; den = float(dv[j] @ U[kk])
                    rc = (cen @ U[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                    r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
                r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
                pts_all.append(dv[keep_s] * r[keep_s][:, None])
            self.link_pts[lk["name"]] = (lk["mem"], np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))
        sn = D.sn; hx = np.interp(self._Ex, xs, rE); self.hEx = hx; u = D.u
        self.rigid = {"hub1": (0, g["hub1"][1] + f1 * u[0]), "hubK": (1, g["hubK"][1] + fK * D.uK), "hub2": (7, g["hub2"][1] + f2 * u[1]),
                      "hub3": (3, g["hub3"][1] + f3 * u[2]), "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tr * sn),
                      "pad": (5, g["pad"][1] + tr * sn), "knee": (6, g["knee"][1] + (tr + off_k) * sn)}
        self._contact_only(); self._solids()

    def _hubs(self):
        D = self.D; return [("hub1", D.u[0], D.c[0], self.f[0], 0), ("hubK", D.uK, np.zeros(3), self.fK, 1),
                            ("hub2", D.u[1], D.c[1], self.f[1], 7), ("hub3", D.u[2], D.c[2], self.f[2], 3)]

    def _contact_only(self):
        D = self.D; P = D.p; tr = self.tr; tp = P["tp"]; out = []
        ang = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        for nm, ax, cc, F, mem in self._hubs():
            e, f = S.frame_of(ax); rr = self.cyl_r[nm]; ring = rr * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            for z in np.linspace(F, F + S.CROWN, 4): out.append((mem, cc + z * ax + ring))
            dd = S.disc(rr, 2.0); out.append((mem, cc + (F + S.CROWN) * ax + dd[:, :1] * e + dd[:, 1:] * f))
        for nm, (mem, pts) in self.link_pts.items():
            if len(pts): out.append((mem, pts + S.T_LINK * unit(pts)))
        sn = D.sn; out.append((3, self.rigid["E"][1] + S.T_LINK * sn)); fr = self.fr
        for mem, cen, z0, z1, R_ in ((3, fr["A0"], tr, tr + tp, BOSS_R), (5, fr["Bm"], tr, tr + tp, PAD_R)):
            e, f = S.frame_of(sn); ring = R_ * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            for z in (z0, z1): out.append((mem, cen + z * sn + ring))
        out.append((5, self.rigid["pad"][1] + tp * sn))
        z0 = tr + tp + S.RUN; z1 = z0 + tp; lc = float(P["lc"]); L = lc + 2 * BOSS_R; W = KNEE_W; pts = []
        for z in (z0, z1):
            for x in np.arange(-L / 2, L / 2 + 1e-6, S.SPACING): pts += [(x, -W / 2, z), (x, W / 2, z)]
            for y in np.arange(-W / 2, W / 2 + 1e-6, S.SPACING): pts += [(-L / 2, y, z), (L / 2, y, z)]
        a = np.array(pts); cen = fr["A0m"] + (lc / 2) * fr["eK"]
        out.append((6, cen + a[:, :1] * fr["eK"] + a[:, 1:2] * fr["nK"] + a[:, 2:] * sn))
        out.append((6, self.rigid["knee"][1] + tp * sn))
        self.contact = out

    def _solids(self):
        D = self.D
        self.cyl = {nm: (mem, cc + F * ax, ax) for nm, ax, cc, F, mem in self._hubs()}
        self.box = {}
        self.strap = {nm: (mem, pts + (S.T_LINK / 2) * unit(pts)) for nm, (mem, pts) in self.link_pts.items()}
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); self.cyl_surf = {}
        for nm, (mem, cen, ax) in self.cyl.items():
            rr = self.cyl_r[nm]; e, f = S.frame_of(ax)
            pts = [cen + z * ax + rr * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, S.CROWN, 5)]
            dd = S.disc(rr, 4.0); pts.append(cen + S.CROWN * ax + dd[:, :1] * e + dd[:, 1:] * f); self.cyl_surf[nm] = (mem, np.concatenate(pts))
        self.Emid = (3, self.rigid["E"][1] + (S.T_LINK / 2) * D.sn)

    def collide(self, i):
        """min clearance (mm) between non-adjacent parts at pose i; adjacent pairs below 0.15 mm jam (-1)"""
        fr = self.fr; h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k] = (R @ cen + t, R @ ax)
        surf = {k: tf(m, X) for k, (m, X) in self.cyl_surf.items()}
        strap = {k: tf(m, X) for k, (m, X) in self.strap.items()}
        Em = tf(*self.Emid); bx = self._boxes_at_final(i)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def vbox(X, nm, extra=0.0): cen, R, half = bx[nm]; return float(self.sd_box(X, cen, R, half).min()) - extra if len(X) else 1e9
        def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
        def ss(A, Bq): return float(cKDTree(Bq).query(A)[0].min()) - 2 * h if len(A) and len(Bq) else 1e9
        c, adj = {}, {}
        # hubs vs hubs (non-adjacent: no two hub cylinders share a member face except through their joint)
        hn = ["hub1", "hubK", "hub2", "hub3"]
        for a in range(4):
            for b in range(a + 1, 4): c[f"{hn[a]}-{hn[b]}"] = vcyl(surf[hn[b]], hn[a])
        # straps vs hubs they do not end in
        for L, ends in (("L1a", ("hub1", "hubK")), ("L1b", ("hubK", "hub2")), ("L2", ("hub2", "hub3"))):
            for hb in hn:
                if hb not in ends: c[f"{L}-{hb}"] = vcyl(strap[L], hb, h)
        # straps vs straps: L1a-L2 non-adjacent; L1a-L1b adjacent at K, L1b-L2 adjacent at J2 (outside the hub zone: 1 mm)
        c["L1a-L2"] = ss(strap["L1a"], strap["L2"])
        c["L1a-L1b"] = ss(far(strap["L1a"], "hubK", 4), far(strap["L1b"], "hubK", 4))
        c["L1b-L2"] = ss(far(strap["L1b"], "hub2", 4), far(strap["L2"], "hub2", 4))
        for nm in ("knee", "pad"):
            for hb in ("hub1", "hubK", "hub2"): c[f"{nm}-{hb}"] = vbox(surf[hb], nm)
            for L in ("L1a", "L1b", "L2"): c[f"{nm}-{L}"] = vbox(strap[L], nm, h)
        c["pad-hub3"] = vbox(surf["hub3"], "pad"); c["pad-E"] = vbox(Em, "pad", h)
        for hb in ("hub1", "hubK", "hub2"): c[f"E-{hb}"] = vcyl(Em, hb, h)
        c["E-L1a"] = ss(Em, strap["L1a"]); c["E-L1b"] = ss(Em, strap["L1b"])
        L2f = far(strap["L2"], "hub3", 1)
        if len(L2f): adj["E-L2"] = ss(Em, L2f)
        adj["knee-hub3"] = vbox(surf["hub3"], "knee")
        pa = tf(3, fr["A0"][None])[0]; Ef = Em[np.linalg.norm(Em - pa, axis=1) > BOSS_R + 0.5]
        adj["knee-E"] = vbox(Ef, "knee", h) if len(Ef) else 1e9
        self.last_clear = {k: round(v, 1) for k, v in list(c.items()) + list(adj.items())}
        out = min(c.values())
        if min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out


def _report(B, params):
    M = KModel(B, dict(PARAMS, **params))
    if not M.kin_ok.any():
        B.reset(); r = B.report(); r["why"] = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure")}
        r["knee"] = None; r["honest"] = True; r["params"] = M.p; return r, M
    r = M.run(); D = M.D
    r["seats"] = dict(tilt_deg=D.seats["tilt_deg"], a_deg=[round(D.a1, 1), round(D.a2, 1)], rest_err_deg=round(D.rest_err, 4))
    k = M.K["ang"][M.kin_ok]; ko = M.kin_ok
    r["knee"] = dict(ang=[round(float(k.min()), 1), round(float(k.max()), 1)] if len(k) else None, br=M.K["br"], tr=round(M.tr, 1))
    st = M.kstate; ws = np.array([x == "ws" for x in B.kind]); tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    con = np.array([B.res[i] is not None and float(np.min(B.res[i])) < 0 for i in range(len(B.idx))])
    r["knuckle"] = dict(fK=round(float(M.fK), 1), forced_kin=int((ko & (st != 0)).sum()), stretched=int((ko & (st == 1)).sum()), folded=int((ko & (st == -1)).sum()),
                        forced_ws_taken=int((tk & ws & (st != 0)).sum()), forced_ws_contact=int((con & ws & (st != 0)).sum()),
                        a1e_max=round(float(M.a1e[ko].max()), 1) if ko.any() else None,
                        min_sub_margin=round(float(M.msub[ko & (st != 0)].min()), 1) if (ko & (st != 0)).any() else None)
    r["hubs"] = list(M.hr); r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = KModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    class Frozen(KModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
                parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "frozen":
        t = time.time(); out = frozen(dict(PARAMS, **par)); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, dict(PARAMS, **par))
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "knee", r["knee"],
          "knuckle", r.get("knuckle"), "f", r.get("f"), "seats", r.get("seats"), f"{time.time() - t:.0f}s", B.mode)
    print("parts", r.get("parts_ib14"), r.get("parts_pairs"), "min clear", r.get("min_clear_taken"), "res", r.get("res_max"))

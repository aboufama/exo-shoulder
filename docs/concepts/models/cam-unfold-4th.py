"""cam-unfold-4th (round 6 screen, replaces the interrupted round-1 sketch): the verified pin-knee chain with LINK 2 split by a
fourth, PASSIVE, SLAVED O20 hub K whose angle is a fixed function of J2's own angle, K = c(q2), imposed by a groove face cam
on link 1 around hub 2 (the arm-side, sensor-free sibling of minarc-stop-knuckle-4r's spring knuckle in link 1).

Chain: scapula handler -> J1 (O20, ACTIVE, GH ray) -> link 1 (strap, arc a1; its lower plate at J2 carries the cam flange,
O30 x 3.5: groove 10.6-13.7 mm for an O3 iglidur-sleeved follower pin, 1.3 mm outer wall; the groove stays outside hub 2's
O20 housing = the housing rule) -> J2 (O20, ACTIVE, q2 dowel stops at the window ends) -> link 2a (strap, arc bk1; follower
lever at J2 + O2 Ti pushrod on top of the strap) -> K (O20 bearing-pair pin, PASSIVE, slaved: crank 6 mm on link 2b) ->
link 2b (strap, arc bk2) -> J3 (O20, ACTIVE, tilted b3 toward the skin normal) -> member 3 -> flat two-pin knee -> arm pad.
0 passive translations; passive rotations: K (slaved, not sensed) + the 2 knee pins. 3 ACTIVE DOF: K = c(q2) is read from q2.

THE CAM LAW (exact, no spare coordinate - R17). In link 1's frame J3's direction is p(x) = R(u2, q2) R(uK, dK(x)) u3 with
q2 = q2f + d x (x = 0 at the plain dyad's folded point, 180 at its stretched point, on the design's branch) and
dK = sign(psiA) c(x), c >= 0 straightening K (a2e = arc(J2, J3) grows), c < 0 bending it (a2e shrinks):
    c(x) = cs h((x - xs) / ws)   for x > xs,  xs = the plain dyad's x at th = a1 + a2 - mons      (stretched lobe)
         = -cf h((xf - x) / wf)  for x < xf,  xf = the plain dyad's x at th = |a1 - a2| + monf   (folded lobe, cf 0 = none)
         = 0 in between (K on its dwell: a rigid 3R),    h(t) = 3t^2 - 2t^3 on [0, 1], 1 beyond (the cam's top dwell).
th(x) = angle(u1, p(x)) is a 1-D function: the coupled 3R is singular exactly where dth/dx = 0. The window is the largest
x interval around the dwell where (i) the EFFECTIVE dyad (a1, a2e(x)) keeps the kit's J1-J3 fold margin >= FOLD_MARGIN
(5 deg; the kit-rule `m3e` reading), (ii) dth/dx >= gfac x the plain dyad's own gain at its 5-deg margin (the coupled
chain transmits no worse than the 3R at its fold margin), (iii) the branch is kept, (iv) K's interior angle stays in
[FOLD_MARGIN, 180 - FOLD_MARGIN]. th is monotone on the window, so each arm pose has ONE q2 (no branch, no flip); then
q1 = PK1(u1), q3 = PK1(u3), exactly; J2's dowel slot is the window. Cam slope |dc/dx| <= 1.5 cs / ws is capped at `smax`
(pressure angle atan(6 mm crank x slope / 12 mm pitch radius) <= 31 deg at smax 1.2).

Everything else is the verified pin-knee / minarc-B machinery (VModel rules: closure < 0.5 deg, 10 fps continuity incl. K,
jam rule, part-part >= 1 mm non-adjacent / 0.15 mm adjacent, walls / crowns / tops skin-checked, near-touch audit).
Members: 0 scapula, 1 link 1 (+ hub 2's housing and the cam flange), 7 link 2a (+ hub K's housing, the pushrod),
2 link 2b, 3 member 3 (hub 3 + E strap + boss), 5 arm pad, 6 knee link.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/cam-unfold-4th.py [check|table] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/cam-unfold-4th.py frozen '<json>' out.json
    hooks: evaluate(B, params) -> (params, report) for tools/concept_cma.py; bench_eval for tools/concept_sweep.py
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("minarc_b_for_camunfold", os.path.join(HERE, "minarc-stop-knuckle-4r-pinknee.py"))
KB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(KB)      # own module copy
PK, S = KB.PK, KB.S; unit = S.unit; D2R = math.pi / 180
ID = "cam-unfold-4th"; NAME = "Cam-unfolding link: a cam-slaved knee K = c(q2) in link 2 (pin knee closure)"
BOSS_R, PAD_R, KNEE_W = PK.BOSS_R, PK.PAD_R, PK.KNEE_W
REPORT_KEYS = ("cam", "why", "knee", "parts_ib14", "parts_pairs", "min_clear_taken", "res_max", "seats", "gap_near1", "near1_poses",
               "min_metal_mm", "plain", "overhead140")
PARAMS = dict(PK.PARAMS)
# minarc BDp's seats (verify/minarc-kitrule/params_floorBD5_phys_cap6.json) for J1 / J2 / J3 / pin knee
PARAMS.update(az1=95.4669, el1=67.7011, az2=47.212, el2=39.8943, wd=59.8224, wa=-9.0298, b3=0.4579, lE=64.6617, lc=30.3886,
              phiE=-1.5412, phib=-69.7597, ang_min=24.9512, stk=5.2691,
              bk1=35.0, bk2=50.0, sK=-1,               # K on link 2: arc from J2, arc from J3, side of the J2-J3 great circle
              mons=8.0, ws=25.0, cs=25.0,              # stretched lobe: onset margin (deg of th), ramp width (deg of q2), K travel
              monf=8.0, wf=25.0, cf=0.0,               # folded lobe (cf 0 = one-sided cam)
              gfac=1.0, smax=1.5, cam_r=15.0, cam_h=0.0, rod=2.0, near=1)
# cam_r 15 / cam_h 0 = the FLANGE cam (O30 x 3.5 on link 1 at the skin face); cam_r 10 / cam_h 3 = the CROWN cam (a 3 mm grooved
# ring on hub 2's crown, the follower lever from link 2a reaching over it: hub 2 stays O20 but stands 15.25 mm)
XG = np.arange(-60.0, 240.0 + 1e-9, 0.1)                 # x grid (deg)


def smooth(t):
    t = np.clip(t, 0.0, 1.0); return t * t * (3 - 2 * t)


def dyad_margin(th, a1, a2):
    return np.minimum.reduce([th - np.abs(a1 - a2), np.minimum(a1 + a2, 360 - a1 - a2) - th])


class CDesign(KB.KDesign):
    def __init__(self, params=None):
        PK.Design.__init__(self, params); P = self.p
        u1, u2, u3 = self.u
        assert np.linalg.norm(self.c[0]) < 1e-6 and np.linalg.norm(self.c[1]) < 1e-6, "needs J1, J2 on GH rays (b1 = b2 = 0)"
        ang = lambda a, b: math.degrees(math.acos(float(np.clip(a @ b, -1, 1))))
        self.a1 = ang(u1, u2); self.a2 = ang(u2, u3); m = KIT.FOLD_MARGIN
        sK = 1.0 if float(P["sK"]) >= 0 else -1.0; P["sK"] = int(sK)
        b1, b2 = float(P["bk1"]), float(P["bk2"])
        self.uK = unit(S.circ_int(u2, b1 * D2R, u3, b2 * D2R, sK))
        pu2 = u2 - (u2 @ self.uK) * self.uK; pu3 = u3 - (u3 @ self.uK) * self.uK
        self.psiA = float(math.atan2(np.cross(pu2, pu3) @ self.uK, pu2 @ pu3))   # signed K angle (J2 -> J3) at the dwell
        self.k_ok = abs(b1 - b2) + m <= self.a2 <= b1 + b2 - m
        self._table()

    def _c(self, x):
        P = self.p; x = np.asarray(x, float)
        cs, ws, cf, wf = float(P["cs"]), max(1.0, float(P["ws"])), float(P["cf"]), max(1.0, float(P["wf"]))
        return cs * smooth((x - self.xs) / ws) - cf * smooth((self.xf - x) / wf)

    def _table(self):
        """th(x) of the coupled chain on the x grid, the valid window and its inverse"""
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; m = KIT.FOLD_MARGIN; a1, a2 = self.a1, self.a2
        # plain dyad on the full turn: folded / stretched q2 (u3 rotated into the u1-u2 plane), the design's branch
        qq = np.arange(0.0, 360.0, 0.05); p0 = S.rotm(u2, qq * D2R) @ u3
        th0 = np.degrees(np.arccos(np.clip(p0 @ u1, -1, 1)))
        qf = float(qq[np.argmin(th0)]); qs = float(qq[np.argmax(th0)])
        d = 1.0 if (((qs - qf) % 360) < 180) == True else -1.0          # direction of increasing th from folded to stretched
        mid = (qf + d * 90.0) % 360; bm = float(np.sign(np.cross(u1, S.rotm(u2, np.array([mid * D2R]))[0] @ u3) @ u2))
        if bm != float(self.branch): d = -d                             # take the half-turn of the design's branch
        self.q2f, self.d = qf, d
        x0 = np.arange(0.0, 180.0 + 1e-9, 0.05); th0b = np.degrees(np.arccos(np.clip((S.rotm(u2, (qf + d * x0) * D2R) @ u3) @ u1, -1, 1)))
        self.xs = float(np.interp(a1 + a2 - float(P["mons"]), th0b, x0)) if a1 + a2 <= 180 else float(np.interp(min(a1 + a2, 360 - a1 - a2) - float(P["mons"]), th0b, x0))
        self.xf = float(np.interp(abs(a1 - a2) + float(P["monf"]), th0b, x0))
        g0 = np.gradient(th0b, x0)
        gm = [float(np.interp(min(a1 + a2, 360 - a1 - a2) - m, th0b, g0)), float(np.interp(abs(a1 - a2) + m, th0b, g0))]
        self.gmin = float(P["gfac"]) * max(1e-3, min(gm))
        x = XG; c = self._c(x); dK = np.sign(self.psiA) * c * D2R
        q2 = (qf + d * x) * D2R
        v3 = np.einsum("nij,j->ni", S.rotm(uK, dK), u3); p = np.einsum("nij,nj->ni", S.rotm(u2, q2), v3)
        th = np.degrees(np.arccos(np.clip(p @ u1, -1, 1)))
        a2e = np.degrees(np.arccos(np.clip(v3 @ u2, -1, 1)))
        me = dyad_margin(th, a1, a2e); g = np.gradient(th, x)
        br = np.sign(np.einsum("j,nj->n", u2, np.cross(np.broadcast_to(u1, p.shape), p)))
        psi = np.abs(np.degrees(self.psiA)) + c
        slope = np.abs(np.gradient(c, x))
        good = (me >= m) & (g >= self.gmin) & (br == self.branch) & (psi >= m) & (psi <= 180 - m)
        # largest connected run of good x
        best, cur, s0 = (0, 0, -1), 0, 0
        for i, gd in enumerate(np.r_[good, False]):
            if gd and cur == 0: s0 = i
            cur = cur + 1 if gd else 0
            if not gd and i > 0 and good[i - 1] and (i - s0) > best[1] - best[0]: best = (s0, i, 1)
        self.slope_max = float(slope.max())
        self.cam_ok = bool(self.k_ok) and self.slope_max <= float(P["smax"]) + 1e-9 and best[1] - best[0] > 10
        i0, i1 = best[0], best[1]
        self.win = (float(x[i0]), float(x[max(i0, i1 - 1)])) if self.cam_ok else (0.0, 0.0)
        sl = slice(i0, i1)
        self.tx, self.tth, self.tme, self.ta2e, self.tc = x[sl], th[sl], me[sl], a2e[sl], c[sl]
        self.th_win = (float(th[sl].min()), float(th[sl].max())) if self.cam_ok else (0.0, 0.0)
        self.tab_full = dict(x=x, th=th, me=me, g=g, a2e=a2e, c=c, good=good)

    def ik(self, Q):
        if not hasattr(self, "tx"): return PK.Design.ik(self, Q)          # OSN's seat set-up (K on its dwell = the plain 3R)
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        ok = np.full(n, bool(self.cam_ok)) & (th >= self.th_win[0]) & (th <= self.th_win[1])
        if self.cam_ok and len(self.tx) > 1:
            x = np.interp(th, self.tth, self.tx); me = np.interp(th, self.tth, self.tme); a2e = np.interp(th, self.tth, self.ta2e)
        else:
            x = np.zeros(n); me = np.zeros(n); a2e = np.full(n, self.a2)
        c = self._c(x); dK = np.sign(self.psiA) * c * D2R; q2 = (self.q2f + self.d * x) * D2R
        RK = S.rotm(uK, dK) if n else np.zeros((0, 3, 3)); R2 = S.rotm(u2, q2) if n else np.zeros((0, 3, 3))
        p = np.einsum("nij,njk,k->ni", R2, RK, u3)
        q1 = S.sub1(u1, p, w); R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
        R12 = R1 @ R2 @ RK; vv = unit(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv))
        R3 = S.rotm(u3, q3) if n else np.zeros((0, 3, 3)); R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        Z0 = np.zeros((n, 3)); X1 = (R1, Z0); X2a = (R1 @ R2, Z0); X2 = (R12, Z0); X3 = (R123, t3)
        sv = np.einsum("nji,nj->ni", Q, t3); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        state = np.where(c > 1e-6, 1, np.where(c < -1e-6, -1, 0))
        self._X1b, self._dK, self._state, self._a1e, self._msub = X2a, dK, state, a2e, me
        self._x = x
        return np.stack([q1, q2, q3], 1), ok, X1, X2, X3, s


class CGeo(PK._Geo):
    def add_links(self, f1, f2, fK, f3):
        D = self.D; U = [D.u[0], D.u[1], D.uK, D.u[2]]; Cc = [D.c[0], D.c[1], np.zeros(3), D.c[2]]; F = [f1, f2, fK, f3]
        hr = list(self.hr); SP = S.SPACING
        C = [Cc[k] + F[k] * U[k] for k in range(4)]; out = []
        for name, ka, kb, mem in (("L1", 0, 1, 1), ("L2a", 1, 2, 7), ("L2b", 2, 3, 2)):
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


_KM0 = KB.KModel


class CModel(_KM0):
    def __init__(self, B, params=None, verbose=False):
        self.fix = dict(S.VModel.fix)
        self.B = B; self.D = CDesign(params); self.p = self.D.p; self.v = verbose
        P = self.p; P["tp"] = (float(P["stk"]) - S.RUN) / 2
        self.hr = [round(float(P.get(f"rad{k + 1}", S.HUB_R)), 2) for k in range(3)]
        for r_ in self.hr:
            if r_ != S.HUB_R: raise ValueError("O20 only (user 2026-10-16)")
        self.cam_r = float(P["cam_r"])
        self.cyl_r = {"hub1": self.hr[0], "hub2": self.cam_r, "hubK": S.HUB_R, "hub3": self.hr[2]}
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)
        X2a, self.dK, self.kstate, self.a1e, self.msub = self.D._X1b, self.D._dK, self.D._state, self.D._a1e, self.D._msub
        self.xcam = self.D._x
        names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
        _, okc, _, _, _, sc = self.D.ik(Z["HG"][ii].astype(float))
        sv = np.r_[s[ok], sc[okc]]
        if P.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))
        if P.get("m_fix") is not None: self.D.m = np.array(P["m_fix"], float)
        self.D.m[2] = 0.0
        self.radial_span = round(float(np.ptp(sv[:, 2])), 3) if len(sv) else 0.0
        self.drift_span = [round(float(np.ptp(sv[:, k])), 1) for k in range(2)] if len(sv) else [0, 0]
        self.q, self.X, self.s = q, {1: X1, 2: X2, 3: X3, 7: X2a}, s
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

    def _geo(self):
        g = PK.Model._geo(self); D = self.D
        mem, pts, ax = g["hub2"]; e, f = S.frame_of(D.u[1]); d = S.disc(self.cam_r)
        g["hub2"] = (1, D.c[1][None] + d[:, :1] * e + d[:, 1:] * f, D.u[1])           # hub 2 + cam flange (O30) on link 1
        e, f = S.frame_of(D.uK); d = S.disc(S.HUB_R); g["hubK"] = (7, d[:, :1] * e + d[:, 1:] * f, D.uK)
        return g

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
        f1 = H["hub1"][keep1].max(); fK = H["hubK"][keep1].max(); f2 = H["hub2"][keep1].max(); f3 = H["h3"][keep1].max()
        geo = CGeo(D, [self.hr[0], self.cam_r, S.HUB_R, self.hr[2]]); geo.add_links(f1, f2, fK, f3); self.geo = geo
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
        f1 = H["hub1"][keep].max(); fK = H["hubK"][keep].max(); f2 = H["hub2"][keep].max(); tr = H["stack"][keep].max(); f3 = H["h3"][keep].max()
        hE = self._HE[keep].max(0) if keep.any() else self._HE.max(0)
        xs, rE, f3, tr = self._E_profile(hE, f3, tr)
        self.f = [f1, f2, f3]; self.fK = fK; self.tr = tr; self.zb = tr
        k = math.tan(S.RAMP * D2R); rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in self.Lneed.items()}
        lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2a", 1): S.UP, ("L2a", 2): 0.0, ("L2b", 2): S.UP, ("L2b", 3): S.UP}
        F4 = [f1, f2, fK, f3]; self.link_pts = {}; rod = float(P.get("rod", 0) or 0)
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
        # the pushrod (O2 Ti) rides on top of link 2a along its two middle rows: real metal for contact and collisions
        if rod > 0:
            lk = [l for l in self.geo.links if l["name"] == "L2a"][0]; rows = rL["L2a"]; pr = []
            for ri in (1, 2):
                dv, keep_s, _ = lk["rows"][ri]; rr = rows[ri]
                pr.append(dv[keep_s] * (rr[keep_s] + S.T_LINK)[:, None])
            self.rod_pts = (7, np.concatenate(pr) if pr else np.zeros((0, 3)))
        else:
            self.rod_pts = (7, np.zeros((0, 3)))
        sn = D.sn; hx = np.interp(self._Ex, xs, rE); self.hEx = hx; u = D.u
        self.rigid = {"hub1": (0, g["hub1"][1] + f1 * u[0]), "hubK": (7, g["hubK"][1] + fK * D.uK), "hub2": (1, g["hub2"][1] + f2 * u[1]),
                      "hub3": (3, g["hub3"][1] + f3 * u[2]), "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tr * sn),
                      "pad": (5, g["pad"][1] + tr * sn), "knee": (6, g["knee"][1] + (tr + off_k) * sn)}
        self._contact_only(); self._solids()

    def _hubs(self):
        D = self.D; return [("hub1", D.u[0], D.c[0], self.f[0], 0), ("hub2", D.u[1], D.c[1], self.f[1], 1),
                            ("hubK", D.uK, np.zeros(3), self.fK, 7), ("hub3", D.u[2], D.c[2], self.f[2], 3)]

    def _contact_only(self):
        _KM0._contact_only(self)
        mem, pts = self.rod_pts
        if len(pts):                                    # rod crown (2 mm above the strap top)
            self.contact.append((mem, pts + float(self.p.get("rod", 2.0)) * unit(pts)))

    def _solids(self):
        _KM0._solids(self)
        mem, pts = self.rod_pts
        if len(pts):                                    # rod centreline 1 mm above the strap top, as a 3 mm-class strap sample set
            m0, sp = self.strap["L2a"]; self.strap["L2a"] = (m0, np.concatenate([sp, pts + 0.5 * float(self.p.get("rod", 2.0)) * unit(pts)]))

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
        hn = ["hub1", "hub2", "hubK", "hub3"]
        for a in range(4):
            for b in range(a + 1, 4): c[f"{hn[a]}-{hn[b]}"] = vcyl(surf[hn[b]], hn[a])
        for L, ends in (("L1", ("hub1", "hub2")), ("L2a", ("hub2", "hubK")), ("L2b", ("hubK", "hub3"))):
            for hb in hn:
                if hb not in ends: c[f"{L}-{hb}"] = vcyl(strap[L], hb, h)
        c["L1-L2b"] = ss(strap["L1"], strap["L2b"])
        c["L1-L2a"] = ss(far(strap["L1"], "hub2", 4), far(strap["L2a"], "hub2", 4))
        c["L2a-L2b"] = ss(far(strap["L2a"], "hubK", 4), far(strap["L2b"], "hubK", 4))
        for nm in ("knee", "pad"):
            for hb in ("hub1", "hub2", "hubK"): c[f"{nm}-{hb}"] = vbox(surf[hb], nm)
            for L in ("L1", "L2a", "L2b"): c[f"{nm}-{L}"] = vbox(strap[L], nm, h)
        c["pad-hub3"] = vbox(surf["hub3"], "pad"); c["pad-E"] = vbox(Em, "pad", h)
        for hb in ("hub1", "hub2", "hubK"): c[f"E-{hb}"] = vcyl(Em, hb, h)
        c["E-L1"] = ss(Em, strap["L1"]); c["E-L2a"] = ss(Em, strap["L2a"])
        L2f = far(strap["L2b"], "hub3", 1)
        if len(L2f): adj["E-L2b"] = ss(Em, L2f)
        adj["knee-hub3"] = vbox(surf["hub3"], "knee")
        pa = tf(3, fr["A0"][None])[0]; Ef = Em[np.linalg.norm(Em - pa, axis=1) > BOSS_R + 0.5]
        adj["knee-E"] = vbox(Ef, "knee", h) if len(Ef) else 1e9
        self.last_clear = {k: round(v, 1) for k, v in list(c.items()) + list(adj.items())}
        out = min(c.values())
        if min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out


class _RC(float):
    """a hub radius carrying its own (taller) crown"""
    crown = S.CROWN


class _CapT(tuple):
    cap = True


def apply_cap(Mo, name, dh):
    """hub `name` dh mm taller on the crown side (the CROWN CAM: a 3 mm grooved ring on hub 2's crown, follower lever from
    link 2a): part-part cylinder, crown samples and skin-contact rings (idempotent, so a frozen copy carries it too)"""
    if dh <= 0 or name not in getattr(Mo, "cyl", {}): return
    r = _RC(float(Mo.cyl_r[name])); r.crown = S.CROWN + dh; Mo.cyl_r = dict(Mo.cyl_r); Mo.cyl_r[name] = r
    base = Mo.sd_cylr
    def sd_cyl(Pw, cen, ax, r=None):
        rr = max(Mo.hr) if r is None else r
        return base(Pw, cen, ax, rr, getattr(rr, "crown", S.CROWN))
    Mo.sd_cyl = sd_cyl
    mem, cen, ax = Mo.cyl[name]; e, f = S.frame_of(ax); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); H = S.CROWN + dh
    pts = [cen + z * ax + float(r) * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, H, 7)]
    dd = S.disc(float(r), 4.0); pts.append(cen + H * ax + dd[:, :1] * e + dd[:, 1:] * f); Mo.cyl_surf = dict(Mo.cyl_surf); Mo.cyl_surf[name] = (mem, np.concatenate(pts))
    ang32 = np.linspace(0, 2 * np.pi, 32, endpoint=False); ring = float(r) * (np.cos(ang32)[:, None] * e + np.sin(ang32)[:, None] * f)
    extra = [_CapT((mem, cen + z * ax + ring)) for z in np.linspace(S.CROWN, H, 3)]
    dd2 = S.disc(float(r), 2.0); extra.append(_CapT((mem, cen + H * ax + dd2[:, :1] * e + dd2[:, 1:] * f)))
    Mo.contact = [c for c in Mo.contact if not isinstance(c, _CapT)] + extra


def _run(self, B=None):
    dh = float(self.p.get("cam_h", 0) or 0)
    if dh > 0:
        fit0 = self.fit
        def fit_cap(): fit0(); apply_cap(self, "hub2", dh)
        self.fit = fit_cap
    return _KM0.run(self)


CModel.run = _run
KB.KModel = CModel; KB.KDesign = CDesign                    # KB.frozen() / KB._report build through these globals


def _report(B, params):
    p = dict(PARAMS, **params)
    p["sK"] = 1 if float(p["sK"]) >= 0 else -1
    for k in ("mons", "monf"): p[k] = max(KIT.FOLD_MARGIN, float(p[k]))
    for k in ("cs", "cf", "ws", "wf"): p[k] = max(0.0, float(p[k]))
    sm = float(p["smax"])                                    # keep the cam slope (pressure angle) feasible: ws >= 1.5 c / smax
    p["ws"] = max(p["ws"], 1.5 * p["cs"] / sm + 0.01, 1.0); p["wf"] = max(p["wf"], 1.5 * p["cf"] / sm + 0.01, 1.0)
    p["bk1"] = min(max(float(p["bk1"]), 6.0), 80.0); p["bk2"] = min(max(float(p["bk2"]), 6.0), 90.0)
    r, M = KB._report(B, p)
    D = M.D; ko = M.kin_ok
    if ko.any():
        a = PK.audit(M, B); r["gap_near1"] = a["gap_near1"]; r["near1_poses"] = a["near1_poses"]; r["min_metal_mm"] = a["near_touch_min_mm"]
        r["overhead140"] = a["overhead140"]
    else:
        r["gap_near1"] = r["gap"]; r["near1_poses"] = 0; r["min_metal_mm"] = None
    st = M.kstate; tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    ws = np.array([x == "ws" for x in B.kind])
    r.pop("knuckle", None)
    r["cam"] = dict(ok=bool(D.cam_ok), a_deg=[round(D.a1, 2), round(D.a2, 2)], window_x=[round(v, 1) for v in D.win],
                    th_window=[round(v, 1) for v in D.th_win], q2_slot_deg=[round(D.q2f + D.d * v, 1) for v in D.win],
                    xs=round(D.xs, 1), xf=round(D.xf, 1), slope_max=round(D.slope_max, 3), gmin=round(D.gmin, 3),
                    a2e_range=[round(float(D.ta2e.min()), 1), round(float(D.ta2e.max()), 1)] if len(D.ta2e) else None,
                    kin_stretch_lobe=int((ko & (st == 1)).sum()), kin_fold_lobe=int((ko & (st == -1)).sum()),
                    taken_ws_lobe=int((tk & ws & (st != 0)).sum()),
                    min_eff_margin_taken=round(float(M.msub[tk].min()), 2) if tk.any() else None,
                    fK=round(float(getattr(M, "fK", 0.0)), 1) if hasattr(M, "fK") else None)
    r["plain"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}
    if p.get("near"): r["gap"] = r["gap_near1"]
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    out = KB.frozen(dict(PARAMS, **P), nc, nw)
    return out


def redteam(B, M):
    """the pin knee's red-team listing (poses not taken, closest metal, near-touch, named pose groups), unchanged"""
    lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:22]:22s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"
    print("-- poses not taken --")
    for i in [i for i in range(len(B.idx)) if M.why[i]]:
        print(f"  {M.why[i]:7s} {lab(i)}" + (f" clear {M.clear[i]:.1f} ({M.last_pair.get(i)})" if M.why[i] == "parts" else ""))
    names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, X in M.rigid.values()] + [len(X) for _, X in M.link_pts.values()]
    cut = np.cumsum([0] + sizes); low = []; taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    for i in range(len(B.idx)):
        if not taken(i): continue
        d = B.res[i]; j = int(np.argmin(d[:cut[-1]])); low.append((float(d[j]), i, names[int(np.searchsorted(cut, j, side="right") - 1)]))
    low.sort(); print("-- closest metal over taken poses (scored samples) --")
    for dd, i, part in low[:6]: print(f"  {dd:5.2f} mm  {part:6s} {lab(i)}")
    cmin = []
    for i in range(len(B.idx)):
        if taken(i):
            cw = np.concatenate([M.world(m, i, Pc) for m, Pc in M.contact]); cmin.append((float(B.dist(i, cw).min()), i))
    cmin.sort(); print("-- closest contact-only metal (walls, crowns, tops, edges) --", [(round(a, 2), lab(i)) for a, i in cmin[:4]])
    allmin = {i: min([x for x, j in cmin if j == i] + [float(np.min(B.res[i]))]) for i in range(len(B.idx)) if taken(i)}
    for thr in (1.0, 2.0):
        n = sum(1 for v in allmin.values() if v < thr); rr = B.report()
        bad = [i for i, v in allmin.items() if v < thr]; sv = {i: B.res[i] for i in bad}
        for i in bad: B.res[i] = np.r_[B.res[i], -1.0]
        r2 = B.report(); print(f"near-touch: {n} taken poses with metal < {thr} mm -> gap {r2['gap']:.2f} (from {rr['gap']:.2f})")
        for i in bad: B.res[i] = sv[i]
    el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses])
    groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= 140)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                  behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
    print("-- named pose groups: taken / total, median metal-skin mm, in band 2-14 / 2-10 --")
    for gname, ii in groups.items():
        ii = list(ii); tk = [i for i in ii if taken(i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
        print(f"  {gname:9s} {len(tk)}/{len(ii)}  median {float(np.median(dd)):.1f} mm  ib14 {float(((dd >= 2) & (dd <= 14)).mean()):.3f}  ib10 {float(((dd >= 2) & (dd <= 10)).mean()):.3f}  not taken: {[(int(i), M.why[i]) for i in ii if not taken(i)][:10]}")


def viz_export(par):
    """geometry of the fitted design (Bench(60,160)) for docs/concepts/viz/concepts/cam-unfold-4th.js"""
    B = CB.Bench(n_clip=60, n_ws=160); r, M = _report(B, par); D = M.D; P = D.p
    R = lambda v, n=5: [round(float(x), n) for x in v]
    def centre(name):
        lk = [l for l in M.geo.links if l["name"] == name][0]; keep = ~M.drop
        rows = [rr[keep].max(0) for rr in M.Lneed[name]]
        pts = []
        for ri in (1, 2):
            dv, ks, _ = lk["rows"][ri]; pts.append(dv * rows[ri][:, None])
        c = 0.5 * (pts[0] + pts[1]); return [R(x, 2) for x in c[::2]]
    sub = slice(None, None, max(1, len(D.tx) // 160))
    G = dict(u=[R(x) for x in D.u], uK=R(D.uK), c=[R(x) for x in D.c], sa=R(D.sa), st=R(D.st), sn=R(D.sn), A=[round(D.a1, 3), round(D.a2, 3)],
             branch=float(D.branch), m=R(D.m), f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), tr=round(float(M.tr), 2),
             tp=round(float(P["tp"]), 3), RUN=S.RUN, SING=KIT.FOLD_MARGIN, camR=M.cam_r, A0=R(M.fr["A0"]), A0m=R(M.fr["A0m"]), Bm=R(M.fr["Bm"]),
             eE=R(M.fr["eE"]), eK=R(M.fr["eK"]), psiA=round(math.degrees(D.psiA), 4), q2f=D.q2f, d=D.d, xs=round(D.xs, 3), xf=round(D.xf, 3),
             cam=dict(cs=P["cs"], ws=P["ws"], cf=P["cf"], wf=P["wf"]), tx=R(D.tx[sub], 2), tth=R(D.tth[sub], 3), th_win=R(D.th_win, 2),
             L1=centre("L1"), L2a=centre("L2a"), L2b=centre("L2b"))
    keys = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "stk", "ang_min", "bk1", "bk2", "sK", "mons", "ws", "cs", "monf", "wf", "cf")
    return dict(P={k: P[k] for k in keys}, G=G, report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")})


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "viz":
        print(json.dumps(viz_export(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}), default=float)); sys.exit()
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "table":
        D = CDesign(dict(PARAMS, **par)); tf = D.tab_full
        print("a", D.a1, D.a2, "branch", D.branch, "q2f", D.q2f, "d", D.d, "xs", D.xs, "xf", D.xf, "gmin", D.gmin, "win", D.win, "th", D.th_win,
              "slope", D.slope_max, "ok", D.cam_ok, "psiA", math.degrees(D.psiA))
        for xv in np.arange(-40, 230, 10):
            j = int(np.argmin(np.abs(tf["x"] - xv)))
            print(f"x {xv:6.1f} th {tf['th'][j]:6.1f} c {tf['c'][j]:6.1f} a2e {tf['a2e'][j]:6.1f} me {tf['me'][j]:6.1f} g {tf['g'][j]:6.3f} good {tf['good'][j]}")
        sys.exit()
    if mode == "frozen":
        t = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "plain", r["plain"], "near1", r["gap_near1"],
          "why", r["why"], "knee", r["knee"], "cam", r["cam"], f"{time.time() - t:.0f}s", B.mode)
    print("parts", r.get("parts_ib14"), r.get("parts_pairs"), "min clear", r.get("min_clear_taken"), "res", r.get("res_max"), "oh", r.get("overhead140"))
    if mode == "redteam": redteam(B, M)

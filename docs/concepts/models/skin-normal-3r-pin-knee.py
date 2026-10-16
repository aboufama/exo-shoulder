"""Concept model: the leader 3R (offset-skin-normal-3r) closed by a FLAT TWO-PIN KNEE instead of the crossed cuff slides
(id skin-normal-3r-pin-knee). 0 passive translations.

Chain: scapula -> J1 (O20 hub, ACTIVE R, axis on a GH ray) -> link 1 -> J2 (O20 hub, ACTIVE R, axis on a GH ray) ->
link 2 -> J3 (O20 hub, ACTIVE R, axis tilted b3 toward the skin normal, its line misses GH) -> member 3 = hub 3's lower
plate + the E strap (8 x 3 Ti) to pin a -> knee link (flat Ti plate) -> pin b -> arm pad (O12) on the cuff/BOTTOM.
Pins a, b are parallel to J3 (iglidur pin: GSM sleeve + 2 GTM washers on an integral Ti pin, or an MR63ZZ pair).

Kinematics (exact). With J1 and J2 on GH rays the motion of member 3 relative to the arm is, for the leader's sliding
cuff, a pure translation s = Q^T t3 lying in hub 3's plane (the 2-slide closure theorem, docs/concepts/offset-skin-
normal-3r.md; radial part identically 0). Here member 3 may also rotate about the J3 axis by phi: the link-2 -> arm
motion is planar (rotation about d3 + translation in hub 3's plane) and the planar RRR (J3 centre C, pin a, pin b)
closes it in closed form (two circles: |pa - C| = lE, |pa - pb| = lc). q3' = q3 + phi, pin a and pin b angles follow;
loop mobility 3 = the arm's; no undetermined coordinate (R17). The knee angle is kept in [ang_min, 180 - ang_min].

Parts at real size (scapula -> cuff): O20 x 12.25 hubs (v5, MR117 pairs), 8 x 3 straps with skin-fitted undersides
(<= 60 deg ramps), the E strap from hub 3's lower plate (its underside = hub 3's face at the rim) ramping to the E end
boss (O12) at the knee level tr, the arm pad (O12) at tr, the knee link (O12 ends, 10 wide) at tr + tp + RUN, total
pin stack `stk` (5.0 = iglidur pin, 6.0 = MR63ZZ pair); tp = (stk - RUN) / 2 per plate. 2 mm sample grid on every
skin-facing underside; side walls, crowns, tops and edges skin-checked (contact only); part-part clearance >= 1 mm
non-adjacent, >= 0.15 mm adjacent (E vs link 2 at J3, knee vs member 3 at pin a); seed VModel rules (closure < 0.5 deg,
10 fps continuity incl. the knee branch, jam rule).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/skin-normal-3r-pin-knee.py [check|redteam] ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("osn_for_knee", os.path.join(HERE, "offset-skin-normal-3r.py"))
OSN = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(OSN)
S = OSN.S; unit = S.unit; D2R = math.pi / 180
ID = "skin-normal-3r-pin-knee"
NAME = "Leader 3R closed by a flat two-pin knee (0 passive translations)"
BOSS_R, PAD_R, KNEE_W = 6.0, 6.0, 10.0       # O12 pin bosses / arm pad, knee link width

PARAMS = dict(OSN.PARAMS)
PARAMS.update(remote=0, ramp=1, S_auto=0, jam_contact=1, drop=1, slides=1, vfix=1, inv=0, centre=1, R_tol=0.5,
              b1=0.0, b2=0.0,
              az1=95.8565, el1=65.2093, az2=10.8917, el2=54.698, wd=79.148, wa=-13.3653, b3=0.2282,   # leader k4216 seats
              lE=30.0,          # hub 3 centre -> pin a (mm)
              lc=25.0,          # pin a -> pin b (mm)
              phiE=0.0,         # E direction in hub 3's plane at mid drift (deg; 0 = distal along the humerus, 90 = across)
              phib=90.0,        # knee link direction pin a -> pin b at mid drift (deg, same plane basis)
              stk=5.0,          # pin stack (mm): 5.0 iglidur pin over two plates, 6.0 MR63ZZ pair
              ang_min=30.0)     # knee angle window [ang_min, 180 - ang_min]


def rodr(u, a):
    """batched Rodrigues about the fixed unit u: a (n,) -> (n,3,3)"""
    return S.rotm(u, a)


def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi


class Design(OSN.Design):
    def __init__(self, params=None):
        P = dict(PARAMS); P.update(params or {}); super().__init__(P); self.p = P

    def knee(self, s):
        """two-circle closure of the planar RRR in hub 3's plane. s (n,3) drift [a, t, n] -> dict"""
        P = self.p; lE, lc = float(P["lE"]), float(P["lc"]); pe, pb = P["phiE"] * D2R, P["phib"] * D2R
        m2 = self.m[:2]; eE = np.array([math.cos(pe), math.sin(pe)])
        A0 = m2 + lE * eE; B2 = A0 + lc * np.array([math.cos(pb), math.sin(pb)])
        C2 = s[:, :2]; v = B2[None] - C2; d = np.linalg.norm(v, axis=1); gam = np.arctan2(v[:, 1], v[:, 0])
        ca = (lE ** 2 + d ** 2 - lc ** 2) / (2 * lE * np.maximum(d, 1e-9)); al = np.arccos(np.clip(ca, -1, 1))
        v0 = B2 - m2; br = float(np.sign(wrap(pe - math.atan2(v0[1], v0[0]))) or 1.0)
        th = gam + br * al
        pa = C2 + lE * np.stack([np.cos(th), np.sin(th)], 1)
        w = B2[None] - pa; psi = np.arctan2(w[:, 1], w[:, 0])
        cosk = np.einsum("ij,ij->i", C2 - pa, w) / (lE * lc); ang = np.degrees(np.arccos(np.clip(cosk, -1, 1)))
        amin = float(P["ang_min"])
        ok = (d >= abs(lE - lc) + 1.0) & (d <= lE + lc - 1.0) & (ang >= amin) & (ang <= 180 - amin)
        return dict(phi=wrap(th - pe), th=th, pa=pa, psi=psi, ang=ang, ok=ok, A0=A0, B2=B2, br=br,
                    qa=wrap(psi - th), qb=wrap(psi - pb))

    def p3(self, p2, h=0.0):
        """plane coordinates (relative to c3) -> home-frame 3D points at height h along sn"""
        p2 = np.atleast_2d(p2); return self.c[2][None] + p2[:, :1] * self.sa + p2[:, 1:2] * self.st + np.asarray(h)[..., None] * self.sn


class Model(S.VModel):
    ADJ = 0.15

    def __init__(self, B, params=None, verbose=False):
        self.fix = dict(S.VModel.fix)
        self.B = B; self.D = Design(params); self.p = self.D.p; self.v = verbose
        P = self.p; P["tp"] = (float(P["stk"]) - S.RUN) / 2
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)
        names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
        _, okc, _, _, _, sc = self.D.ik(Z["HG"][ii].astype(float))
        sv = np.r_[s[ok], sc[okc]]
        if P.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))   # knee at mid drift = the reference
        self.D.m[2] = 0.0
        self.radial_span = round(float(np.ptp(sv[:, 2])), 3) if len(sv) else 0.0
        self.drift_span = [round(float(np.ptp(sv[:, k])), 1) for k in range(2)] if len(sv) else [0, 0]
        self.q, self.X, self.s = q, {1: X1, 2: X2, 3: X3}, s
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
        """10 fps fit clips: q1, q2, q3' = q3 + phi, pin a, pin b; a step > JUMP (or a knee out of range) breaks it"""
        Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; ok_at = {}
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            q, ok, _, _, _, s = self.D.ik(Z["HG"][ii].astype(float)); K = self.D.knee(s); ok &= K["ok"]
            qq = np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]]; prev = None
            for j, gi in enumerate(ii):
                good = bool(ok[j])
                if good and prev is not None and np.degrees(np.abs(wrap(qq[j] - qq[prev]))).max() > S.JUMP: good = False
                ok_at[int(gi)] = good; prev = j if ok[j] else None
        return np.array([ok_at.get(int(gi), True) for gi in self.B.idx])

    # members: 0 scapula, 1 link 1, 2 link 2, 3 hub 3 + E strap + E boss, 5 arm (pad), 6 knee link
    def T(self, m, i):
        if m == 0: return np.eye(3), np.zeros(3)
        if m in (1, 2): R, t = self.X[m]; return R[i], t[i]
        D = self.D; Q = self.Q[i]; c3 = D.c[2]; sv = self.s[i, 0] * D.sa + self.s[i, 1] * D.st + self.s[i, 2] * D.sn
        if m == 5: return Q, np.zeros(3)
        if m == 3:
            Rp = rodr(D.sn, self.K["phi"][i])[0]; return Q @ Rp, Q @ (c3 + sv - Rp @ c3)
        if m == 6:
            K = self.K; Rd = rodr(D.sn, wrap(K["psi"][i] - D.p["phib"] * D2R))[0]
            pa = D.p3(K["pa"][i])[0] + self.s[i, 2] * D.sn; A0 = D.p3(K["A0"])[0]
            return Q @ Rd, Q @ (pa - Rd @ A0)
        raise ValueError(m)

    # -- geometry (home frame) --
    def _geo(self):
        D = self.D; P = D.p; K = self.K; u, c = D.u, D.c; sn, sa, st = D.sn, D.sa, D.st
        pe = P["phiE"] * D2R; eE = math.cos(pe) * sa + math.sin(pe) * st; nE = np.cross(sn, eE)
        pb = P["phib"] * D2R; eK = math.cos(pb) * sa + math.sin(pb) * st; nK = np.cross(sn, eK)
        g = {}
        for k, mem in ((0, 0), (1, 1), (2, 3)):
            e, f = S.frame_of(u[k]); d = S.disc(S.HUB_R); g[f"hub{k + 1}"] = (mem, c[k][None] + d[:, :1] * e + d[:, 1:] * f, u[k])
        lE = float(P["lE"]); xs = np.arange(S.HUB_R + 1.0, lE - BOSS_R + 0.5, S.SPACING)
        if not len(xs): xs = np.array([S.HUB_R + 1.0])
        ys = np.arange(-S.W_LINK / 2 + 1, S.W_LINK / 2, S.SPACING)
        X, Y = np.meshgrid(xs, ys, indexing="ij"); self._Ex = X.ravel()
        g["E"] = (3, c[2][None] + X.ravel()[:, None] * eE + Y.ravel()[:, None] * nE, sn)
        A0 = D.p3(K["A0"])[0] - (D.m[0] * sa + D.m[1] * st)       # pin a in member-3 home coords (hub 3 at c3)
        d6 = S.disc(BOSS_R); g["boss"] = (3, A0[None] + d6[:, :1] * eE + d6[:, 1:] * nE, sn)
        Bm = D.p3(K["B2"])[0]; g["pad"] = (5, Bm[None] + d6[:, :1] * sa + d6[:, 1:] * st, sn)
        A0m = D.p3(K["A0"])[0]; lc = float(P["lc"])
        r = S.rect(lc + 2 * BOSS_R, KNEE_W); r[:, 0] += lc / 2
        g["knee"] = (6, A0m[None] + r[:, :1] * eK + r[:, 1:] * nK, sn)
        self.fr = dict(eE=eE, nE=nE, eK=eK, nK=nK, A0=A0, A0m=A0m, Bm=Bm)
        return g

    def _boxes_at(self, i):
        """knee link and arm pad boxes (scapula frame) at the first-pass knee level, for link 2 to fly over"""
        D = self.D; P = D.p; tr = self._tr_fit; tp = P["tp"]; fr = self.fr; lc = float(P["lc"])
        out = {}
        Rk = np.stack([fr["eK"], fr["nK"], D.sn], 1); ck = fr["A0m"] + (lc / 2) * fr["eK"] + (tr + tp + S.RUN + tp / 2) * D.sn
        R, t = self.T(6, i); out["knee"] = (R @ ck + t, R @ Rk, np.array([lc / 2 + BOSS_R, KNEE_W / 2, tp / 2]))
        Rp = np.stack([D.sa, D.st, D.sn], 1); cp = fr["Bm"] + (tr + tp / 2) * D.sn
        R, t = self.T(5, i); out["pad"] = (R @ cp + t, R @ Rp, np.array([PAD_R, PAD_R, tp / 2]))
        return out

    def fit(self):
        D = self.D; P = D.p
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g; off_k = P["tp"] + S.RUN
        order = ["hub1", "hub2", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        H = {"hub1": res["hub1"], "hub2": res["hub2"], "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], res["pad"], res["knee"] - off_k], 1)}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self.greedy_drop(links=False); keep1 = ~self.drop
        f1 = H["hub1"][keep1].max(); f2 = H["hub2"][keep1].max(); tr = H["stack"][keep1].max(); f3 = H["h3"][keep1].max()
        geo = S.Geometry.__new__(S.Geometry); geo.D = D; geo.groups = []; geo.add_links(f1, f2, f3); self.geo = geo
        self._tr_fit = tr
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        L["E"] = [self._HE]; self.Lneed = L
        self.greedy_drop(keep0=keep1)
        self.finalize()

    def _E_profile(self, hE, f3, tr):
        """E strap underside per x station: >= the fitted need, = f3 at the rim and = tr at the boss, <= 60 deg ramps;
        raises f3 / tr when the strap cannot meet them (the part rises, never the skin)"""
        x = self._Ex; xs = np.unique(np.round(x, 6)); k = math.tan(S.RAMP * D2R)
        need = np.array([hE[np.isclose(x, v)].max() for v in xs])
        for _ in range(4):
            r = np.maximum(need, np.maximum(f3 - k * np.abs(xs - S.HUB_R), tr - k * np.abs(xs - (float(self.p["lE"]) - BOSS_R))))
            r = np.max(r[None, :] - k * np.abs(xs[:, None] - xs[None, :]), axis=1)
            r0 = r[0] - k * abs(xs[0] - S.HUB_R); r1 = r[-1] - k * abs(float(self.p["lE"]) - BOSS_R - xs[-1])
            ch = False
            if r0 > f3 + 0.15: f3 = r0; ch = True
            if r1 > tr + 0.15: tr = r1; ch = True
            if not ch: break
        return xs, r, f3, tr

    def finalize(self):
        D = self.D; P = D.p; keep = ~self.drop; g = self.g; off_k = P["tp"] + S.RUN
        H = self.Hneed
        f1 = H["hub1"][keep].max(); f2 = H["hub2"][keep].max(); tr = H["stack"][keep].max(); f3 = H["h3"][keep].max()
        hE = self._HE[keep].max(0) if keep.any() else self._HE.max(0)
        xs, rE, f3, tr = self._E_profile(hE, f3, tr)
        self.f = [f1, f2, f3]; self.tr = tr; self.zb = tr
        # links (as the seed's finalize: envelope lower bound, raised to the hub levels with <= 60 deg ramps)
        u, c = D.u, D.c; k = math.tan(S.RAMP * D2R); rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in self.Lneed.items()}
        lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): S.UP, ("L2", 2): S.UP}; F = [f1, f2, f3]; self.link_pts = {}
        for lk in self.geo.links:
            pts_all = []
            for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
                r = r.copy(); Sx = sarc
                for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                    idx = np.nonzero(keep_s)[0]
                    if not len(idx): continue
                    j = idx[0] if end == 0 else idx[-1]
                    cen = c[kk] + F[kk] * u[kk]; den = float(dv[j] @ u[kk])
                    rc = (cen @ u[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                    r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
                r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
                pts_all.append(dv[keep_s] * r[keep_s][:, None])
            self.link_pts[lk["name"]] = (lk["mem"], np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))
        sn = D.sn
        hx = np.interp(self._Ex, xs, rE)
        self.hEx = hx
        self.rigid = {"hub1": (0, g["hub1"][1] + f1 * u[0]), "hub2": (1, g["hub2"][1] + f2 * u[1]), "hub3": (3, g["hub3"][1] + f3 * u[2]),
                      "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tr * sn), "pad": (5, g["pad"][1] + tr * sn),
                      "knee": (6, g["knee"][1] + (tr + off_k) * sn)}
        self._contact_only(); self._solids()

    def _contact_only(self):
        """side walls + crowns of hubs, tops of the straps, edges / tops of boss, pad and knee link (skin check, not scored)"""
        D = self.D; P = D.p; u, c = D.u, D.c; F = self.f; tr = self.tr; tp = P["tp"]; out = []
        ang = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        for k, mem in ((0, 0), (1, 1), (2, 3)):
            e, f = S.frame_of(u[k]); ring = S.HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            for z in np.linspace(F[k], F[k] + S.CROWN, 4): out.append((mem, c[k] + z * u[k] + ring))
            dd = S.disc(S.HUB_R, 2.0); out.append((mem, c[k] + (F[k] + S.CROWN) * u[k] + dd[:, :1] * e + dd[:, 1:] * f))
        for nm, (mem, pts) in self.link_pts.items():
            if len(pts): out.append((mem, pts + S.T_LINK * unit(pts)))
        sn = D.sn; out.append((3, self.rigid["E"][1] + S.T_LINK * sn))
        fr = self.fr
        for mem, cen, z0, z1, R_ in ((3, fr["A0"], tr, tr + tp, BOSS_R), (5, fr["Bm"], tr, tr + tp, PAD_R)):
            e, f = S.frame_of(sn); ring = R_ * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            for z in (z0, z1): out.append((mem, cen + z * sn + ring))
        out.append((5, self.rigid["pad"][1] + tp * sn))
        z0 = tr + tp + S.RUN; z1 = z0 + tp; lc = float(P["lc"]); L = lc + 2 * BOSS_R; W = KNEE_W
        pts = []
        for z in (z0, z1):
            for x in np.arange(-L / 2, L / 2 + 1e-6, S.SPACING): pts += [(x, -W / 2, z), (x, W / 2, z)]
            for y in np.arange(-W / 2, W / 2 + 1e-6, S.SPACING): pts += [(-L / 2, y, z), (L / 2, y, z)]
        a = np.array(pts); cen = fr["A0m"] + (lc / 2) * fr["eK"]
        out.append((6, cen + a[:, :1] * fr["eK"] + a[:, 1:2] * fr["nK"] + a[:, 2:] * sn))
        out.append((6, self.rigid["knee"][1] + tp * sn))
        self.contact = out

    def _solids(self):
        D = self.D; u, c = D.u, D.c; F = self.f
        self.cyl = {"hub1": (0, c[0] + F[0] * u[0], u[0]), "hub2": (1, c[1] + F[1] * u[1], u[1]), "hub3": (3, c[2] + F[2] * u[2], u[2])}
        self.box = {}
        self.strap = {nm: (mem, pts + (S.T_LINK / 2) * unit(pts)) for nm, (mem, pts) in self.link_pts.items()}
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); self.cyl_surf = {}
        for nm, (mem, cen, ax) in self.cyl.items():
            e, f = S.frame_of(ax); pts = [cen + z * ax + S.HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, S.CROWN, 5)]
            dd = S.disc(S.HUB_R, 4.0); pts.append(cen + S.CROWN * ax + dd[:, :1] * e + dd[:, 1:] * f); self.cyl_surf[nm] = (mem, np.concatenate(pts))
        self.Emid = (3, self.rigid["E"][1] + (S.T_LINK / 2) * D.sn)          # E strap mid-surface (half thickness 1.5)

    @staticmethod
    def sd_cylr(Pw, cen, ax, r, h):
        w = Pw - cen; z = w @ ax; rr = np.linalg.norm(w - z[:, None] * ax, axis=1); dr = rr - r; dz = np.maximum(-z, z - h)
        return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))

    def collide(self, i):
        """min clearance (mm) between non-adjacent parts at pose i; adjacent pairs below 0.15 mm jam (-1)"""
        D = self.D; P = D.p; tp = P["tp"]; tr = self.tr; fr = self.fr; h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k] = (R @ cen + t, R @ ax)
        surf = {k: tf(m, X) for k, (m, X) in self.cyl_surf.items()}
        strap = {k: tf(m, X) for k, (m, X) in self.strap.items()}
        Em = tf(*self.Emid)
        bx = self._boxes_at_final(i)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm]).min()) - extra if len(X) else 1e9
        def vbox(X, nm, extra=0.0): cen, R, half = bx[nm]; return float(self.sd_box(X, cen, R, half).min()) - extra if len(X) else 1e9
        c = {}
        c["L2-hub1"] = vcyl(strap["L2"], "hub1", h); c["hub3-hub1"] = vcyl(surf["hub3"], "hub1"); c["L1-hub3"] = vcyl(strap["L1"], "hub3", h)
        c["hub2-hub3"] = vcyl(surf["hub2"], "hub3"); c["hub1-hub2"] = self.hub12()
        cen2, ax2 = cyl["hub2"]
        def far(X, cc, ax, rr): w = X - cc; return np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > rr
        A, Bq = strap["L1"][far(strap["L1"], cen2, ax2, S.HUB_R + 4)], strap["L2"][far(strap["L2"], cen2, ax2, S.HUB_R + 4)]
        if len(A) and len(Bq): c["L1-L2"] = float(cKDTree(Bq).query(A)[0].min()) - 2 * h
        for nm in ("knee", "pad"):                                   # moving knee / arm pad vs every non-adjacent part
            c[f"{nm}-hub1"] = vbox(surf["hub1"], nm); c[f"{nm}-hub2"] = vbox(surf["hub2"], nm)
            c[f"{nm}-L1"] = vbox(strap["L1"], nm, h); c[f"{nm}-L2"] = vbox(strap["L2"], nm, h)
        c["pad-hub3"] = vbox(surf["hub3"], "pad"); c["pad-E"] = vbox(Em, "pad", h)
        c["E-hub1"] = vcyl(Em, "hub1", h); c["E-hub2"] = vcyl(Em, "hub2", h)
        if len(strap["L1"]): c["E-L1"] = float(cKDTree(strap["L1"]).query(Em)[0].min()) - 2 * h
        adj = {}
        c3, ax3 = cyl["hub3"]
        L2f = strap["L2"][far(strap["L2"], c3, ax3, S.HUB_R + 1)]
        if len(L2f): adj["E-L2"] = float(cKDTree(L2f).query(Em)[0].min()) - 2 * h          # adjacent at J3
        adj["knee-hub3"] = vbox(surf["hub3"], "knee")                                      # adjacent at pin a
        pa = tf(3, fr["A0"][None])[0]
        Ef = Em[np.linalg.norm(Em - pa, axis=1) > BOSS_R + 0.5]
        adj["knee-E"] = vbox(Ef, "knee", h) if len(Ef) else 1e9
        self.last_clear = {k: round(v, 1) for k, v in list(c.items()) + list(adj.items())}
        out = min(c.values())
        if min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out

    def _boxes_at_final(self, i):
        tr0 = self._tr_fit; self._tr_fit = self.tr
        try: return self._boxes_at(i)
        finally: self._tr_fit = tr0

    def hub12(self):
        if not hasattr(self, "_h12"):
            D = self.D; u, c = D.u, D.c; C1 = c[0] + self.f[0] * u[0]; C2 = c[1] + self.f[1] * u[1]
            e2, f2 = S.frame_of(u[1]); ang = np.linspace(0, 2 * np.pi, 72, endpoint=False); dd = S.disc(S.HUB_R, 1.0)
            Pp = np.concatenate([C2 + z * u[1] + S.HUB_R * (np.cos(ang)[:, None] * e2 + np.sin(ang)[:, None] * f2) for z in np.linspace(0, S.CROWN, 13)]
                                + [C2 + z * u[1] + dd[:, :1] * e2 + dd[:, 1:] * f2 for z in (0.0, S.CROWN)])
            self._h12 = float(self.sd_cyl(Pp, C1, u[0]).min())
        return self._h12


def _report(B, params):
    M = Model(B, params); r = M.run(); D = M.D
    r["seats"] = dict(tilt_deg=D.seats["tilt_deg"], a_deg=[round(math.degrees(a), 1) for a in D.A],
                      offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c], rest_err_deg=round(D.rest_err, 4))
    k = M.K["ang"][M.kin_ok]
    r["knee"] = dict(ang=[round(float(k.min()), 1), round(float(k.max()), 1)] if len(k) else None, br=M.K["br"],
                     drift_span=M.drift_span, radial_span=M.radial_span, tr=round(M.tr, 1), stk=M.p["stk"])
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    return r, M


def evaluate(B, params):
    """tools/concept_cma.py hook: (params, report)"""
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    """tools/concept_sweep.py hook"""
    r, M = _report(B, params); r.pop("params", None); return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "knee", r["knee"],
          "f", r["f"], "seats", r["seats"], f"{time.time() - t:.0f}s", B.mode)
    print("parts", r["parts_ib14"], r["parts_pairs"], "min clear", r.get("min_clear_taken"), "res", r.get("res_max"))
    if mode == "redteam":
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

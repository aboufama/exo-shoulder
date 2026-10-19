"""Concept model rollcone-hubspot-pinknee-3r: H1 (skin-normal-3r-pin-knee, O20 J1 / J3, flat MR63ZZ two-pin cuff knee)
with hub 2 DELETED and J2 made a strap-held ROLLING CONE PAIR, apex at GH, at H1's hub-2 spot.

Kinematics (exact). Member-1 frame: contact generator at rest c = u2 (H1's J2 axis). Split direction tb = cos(beta) t0 +
sin(beta) (c x t0), t0 = the tangent at c pointing away from u1; ax = c x tb. Sun cone axis uK = R(ax, -alpha_s) c (fixed
in link 1), planet axis v2 = R(ax, sgn alpha_p) c (fixed in link 2; sgn +1 external, -1 internal). Rolling without slip:
relative rotation Rroll(y) = R(uK, x) R(v2, y), x = rho y, rho = sgn sin(alpha_p) / sin(alpha_s) (instantaneous axis =
the contact line R(uK, x) c, checked in `check`). Link 2 = X1 Rroll(y) R(u2, q2_rest): identical to H1 at rest.
IK: w = Q u3 (J3 direction); th(y) = angle(u1, Rroll(y) w0) tabulated over y in [-200, 200] at 0.25 deg, the monotone
segment holding the rest (y = 0) is THE branch; y from th by interpolation; q1 = the u1 rotation taking Rroll(y) w0 to w;
q3 and the knee exactly as H1 (J1, J2 virtual axes all through GH -> the 2-slide / knee closure theorem holds).
Fold reading (one metric, the kit's): instantaneous dyad (u1, contact line, J3): margin = min(th - |a1' - a2'|,
min(a1' + a2', 360 - a1' - a2') - th) >= FOLD_MARGIN, AND the distance of th to the segment extrema >= FOLD_MARGIN.

Metal (scapula -> cuff): hub 1 and hub 3 O20 v5 + links + E strap + knee as H1. J2: SUN band on link 1 (cone about uK,
half angle alpha_s, the wall inside the cone), PLANET band on link 2 (cone about v2), each 2.5 mm Ti wall + 0.15 strap
stack, `bh` mm tall radially from ONE level R_lo per band (no per-direction contour), the two levels within 1.5 mm
(common strap radius); sectors = the taken x / y span + 3 deg each side (+ 4 mm clamp at each end). Skin-facing bottom
edges scored (2 mm grid, 2 rows across the wall); both faces and the top edge contact-checked. Link 1: hub 1 -> sun band
mid sector; link 2: planet band mid sector -> hub 3 (H1 straps, <= 60 deg ramps); a link that arrives above its band's
top lifts the band. Part pairs: sun-planet adjacent (0.15 mm) outside 3 mm of the contact line; bands vs hubs 1/3, the
other link, E, knee, pad non-adjacent (1 mm).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/rollcone-hubspot-pinknee-3r.py [check|redteam|kin] ['<json>'] [--big]
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402
_spec = importlib.util.spec_from_file_location("pk_for_rollcone", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
PK = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(PK)
S = PK.S; OSN = PK.OSN; unit = S.unit; D2R = math.pi / 180; wrap = PK.wrap
ID = "rollcone-hubspot-pinknee-3r"
NAME = "Rolling-cone J2 (strap-held cone pair, apex GH) at H1's hub-2 spot on the pin-knee 3R"
FM = KIT.FOLD_MARGIN
WALL = 2.5 + 0.15                                            # Ti wall + strap stack (mm)
H1 = dict(az1=101.1634, el1=63.8986, az2=30.153, el2=47.0108, wd=70.3931, wa=-8.1248, b3=0.2842, lE=59.5534, lc=28.2401,
          phiE=-5.8107, phib=-54.914, ang_min=30.4611, stk=6.0)
PARAMS = dict(PK.PARAMS); PARAMS.update(H1)
PARAMS.update(alpha_s=25.0, alpha_p=10.0, beta=30.0, sgn=1, bh=8.0, sec_m=3.0, ycap=170.0)


def R(u, a):
    return S.rotm(unit(np.asarray(u, float)), np.atleast_1d(a))


def ang(a, b):
    return np.degrees(np.arccos(np.clip(np.einsum("...i,...i->...", a, b), -1, 1)))


class Design(PK.Design):
    def __init__(self, params=None):
        P = dict(PARAMS); P.update(params or {})
        self._roll = False
        super().__init__(P)
        Q0 = OSN.rest()["Q0"]
        qr, okr, *_ = PK.Design.ik(self, Q0[None]); self.q2r = float(qr[0, 1])
        u1, u2, u3 = self.u; c = u2
        t0 = unit((u1 @ c) * c - u1); tb = unit(math.cos(P["beta"] * D2R) * t0 + math.sin(P["beta"] * D2R) * np.cross(c, t0))
        ax = unit(np.cross(c, tb)); sg = 1.0 if P["sgn"] >= 0 else -1.0
        self.cK = c; self.tb = tb
        self.uK = R(ax, -P["alpha_s"] * D2R)[0] @ c
        self.v2 = R(ax, sg * P["alpha_p"] * D2R)[0] @ c                      # member-1 frame at rest
        self.rho = sg * math.sin(P["alpha_p"] * D2R) / math.sin(P["alpha_s"] * D2R)
        self.R2r = R(u2, self.q2r)[0]
        self.v2h = self.R2r.T @ self.v2                                         # planet axis in link-2 home frame
        self.w0 = self.R2r @ u3
        ys = np.arange(-P["ycap"], P["ycap"] + 1e-9, 0.25)
        Rr = self.Rroll(ys * D2R); wl = Rr @ self.w0; th = ang(wl, u1)
        i0 = int(np.argmin(np.abs(ys))); d = np.sign(np.diff(th)); s0 = d[i0] if d[i0] != 0 else d[i0 - 1]
        a = i0
        while a > 0 and d[a - 1] == s0: a -= 1
        b = i0
        while b < len(d) and d[b] == s0: b += 1
        self.seg = (a, b); ys_, th_ = ys[a:b + 1], th[a:b + 1]
        e_lo, e_hi = bool(a > 0), bool(b < len(d))                            # True: that end is a fold extremum (not the cap)
        if s0 < 0: ys_, th_, e_lo, e_hi = ys_[::-1], th_[::-1], e_hi, e_lo
        self.ys, self.th_tab, self.seg_ext = ys_, th_, (e_lo, e_hi)
        self._roll = True
        _, _, _, X2, _, _ = self.ik(Q0[None]); R12, tt2 = X2[0][0], X2[1][0]
        self.c[2] = OSN.foot(R12.T @ (self.seats["P"][2] - tt2), self.u[2])

    def Rroll(self, y):
        y = np.atleast_1d(y); return R(self.uK, self.rho * y) @ R(self.v2, y)

    def ik(self, Q):
        if not getattr(self, "_roll", False): return PK.Design.ik(self, Q)
        u1, u2, u3 = self.u; n = len(Q); P = self.p
        assert np.linalg.norm(self.c[0]) < 1e-3 and np.linalg.norm(self.c[1]) < 1e-3
        w = Q @ u3; th = ang(w, u1)
        tl, th_ = self.th_tab[0], self.th_tab[-1]
        y = np.interp(th, self.th_tab, self.ys) * D2R
        inside = (th >= tl) & (th <= th_)
        mseg = np.minimum(th - tl if self.seg_ext[0] else np.full(n, 1e9), th_ - th if self.seg_ext[1] else np.full(n, 1e9))
        Rr = self.Rroll(y) if n else np.zeros((0, 3, 3)); wl = Rr @ self.w0
        q1 = S.sub1(u1, wl, w); R1 = R(u1, q1) if n else np.zeros((0, 3, 3))
        R12 = R1 @ Rr @ self.R2r
        cx = np.einsum("nij,j->ni", R(self.uK, self.rho * y), self.cK) if n else np.zeros((0, 3))   # contact line, link-1 frame
        a1 = ang(cx, u1); a2 = ang(cx, wl); thl = ang(wl, u1)
        mdy = np.minimum(thl - np.abs(a1 - a2), np.minimum(a1 + a2, 360 - a1 - a2) - thl)
        self.last_fold = dict(mdy=mdy, mseg=mseg, jac=np.abs(np.einsum("i,ni->n", u1, np.cross(cx, wl))), y=np.degrees(y))
        ok = inside & (mdy >= FM) & (mseg >= FM)
        v = unit(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(v, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, v))
        R3 = R(u3, q3) if n else np.zeros((0, 3, 3)); c3 = self.c[2]
        X1 = (R1, np.zeros((n, 3))); X2 = (R12, np.zeros((n, 3)))
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3); X3 = (R12 @ R3, t3)
        sv = np.einsum("nji,nj->ni", Q, t3); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        return np.stack([q1, y, q3], 1), ok, X1, X2, X3, s


class _RGeo:
    """links: L1 hub 1 -> sun band mid sector (member 1), L2 planet band mid sector -> hub 3 (member 2); seed strap rows"""
    def __init__(self, D, hr, Cs, Cp, f1, f3):
        u, c = D.u, D.c; SP = S.SPACING; self.links = []
        for name, mem, A, Bp, ka, kb in (("L1", 1, c[0] + f1 * u[0], Cs, 0, None), ("L2", 2, Cp, c[2] + f3 * u[2], None, 2)):
            da, db = unit(A), unit(Bp); Rr = 0.5 * (np.linalg.norm(A) + np.linalg.norm(Bp))
            an = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
            nn = max(4, int(Rr * an / SP)); ts = (np.arange(nn) + 0.5) / nn
            dirs = np.array([unit(math.sin((1 - t) * an) * da + math.sin(t * an) * db) for t in ts])
            rows = []
            for vv in (-3.0, -1.0, 1.0, 3.0):
                dv = unit(dirs + (vv / Rr) * bn); pts = Rr * dv; keep = np.ones(len(dv), bool)
                for k in (ka, kb):
                    if k is None: continue
                    w_ = pts - c[k]; keep &= np.linalg.norm(w_ - (w_ @ u[k])[:, None] * u[k], axis=1) > hr[k]
                rows.append((dv, keep, ts * Rr * an))
            self.links.append(dict(name=name, mem=mem, ka=ka, kb=kb, rows=rows, band_end=(-1 if kb is None else 0)))


class Model(PK.Model):
    def __init__(self, B, params=None, verbose=False):
        self.fix = dict(S.VModel.fix)
        self.B = B; self.D = Design(params); self.p = self.D.p; self.v = verbose
        P = self.p; P["tp"] = (float(P["stk"]) - S.RUN) / 2
        self.hr = [10.0, 10.0, 10.0]; self.cyl_r = {"hub1": 10.0, "hub3": 10.0}
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = self.D.ik(self.Q); self.fold = dict(self.D.last_fold)
        names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
        qc, okc, _, _, _, sc = self.D.ik(Z["HG"][ii].astype(float))
        sv = np.r_[s[ok], sc[okc]]
        if P.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))
        if P.get("m_fix") is not None: self.D.m = np.array(P["m_fix"], float)
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
        yy = np.r_[np.degrees(q[self.kin_ok, 1]), np.degrees(qc[okc, 1])]
        if P.get("y_fix") is not None:                           # frozen shape: a pose that rolls the contact off the worn bands
            self.yspan = tuple(P["y_fix"]); yd = np.degrees(q[:, 1])     # is out of the joint's range (recorded as 'slide')
            off = self.kin_ok & ((yd < self.yspan[0]) | (yd > self.yspan[1])); self.why[off] = "slide"; self.kin_ok &= ~off
            self.roll_off = int(off.sum())
        else: self.yspan = (float(yy.min()) - P["sec_m"], float(yy.max()) + P["sec_m"]) if len(yy) else (-5.0, 5.0)

    # members: 0 scapula, 1 link 1 (+ sun band), 2 link 2 (+ planet band), 3 hub 3 + E, 5 arm pad, 6 knee link
    def _band_dirs(self, which, delta_frac):
        """unit directions of a band's surface at fraction delta_frac of the wall (0 = rolling face, 1 = back face)"""
        D = self.D; P = self.p; y0, y1 = self.yspan; Rm = 56.0
        dw = math.degrees(WALL / Rm) * delta_frac
        if which == "sun":
            x0, x1 = sorted((D.rho * y0, D.rho * y1)); axis = D.uK; a = P["alpha_s"] - dw * (1 if P["sgn"] >= 0 else -1) * 1.0
            span = (x0, x1); r_pitch = Rm * math.sin(P["alpha_s"] * D2R)
            if P["sgn"] < 0: a = P["alpha_s"] + dw                              # internal: the ring's wall lies outside the cone
        else:
            span = (-y1, -y0); axis = D.v2h; a = P["alpha_p"] - dw; r_pitch = Rm * math.sin(P["alpha_p"] * D2R)
        ext = math.degrees(4.0 / max(r_pitch, 1.0))                               # 4 mm clamp each end
        n = max(3, int(math.radians(span[1] - span[0] + 2 * ext) * r_pitch / S.SPACING) + 1)
        xs = np.linspace(span[0] - ext, span[1] + ext, n) * D2R
        c0 = D.cK if which == "sun" else D.cK                                    # contact at rest, both home frames
        # a direction at angle a from axis in the axis-c0 plane, then swept about axis
        e = unit(c0 - (c0 @ axis) * axis); base = unit(math.cos(a * D2R) * axis + math.sin(a * D2R) * e)
        return np.einsum("nij,j->ni", R(axis, xs), base), xs

    def _geo(self):
        g = PK.Model._geo(self); g.pop("hub2")
        for nm, mem in (("sun", 1), ("planet", 2)):
            dd = np.concatenate([self._band_dirs(nm, f)[0] for f in (0.1, 0.9)])
            g[nm] = (mem, np.zeros_like(dd), dd)
        return g

    def fit(self):
        D = self.D; P = D.p
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g; off_k = P["tp"] + S.RUN
        order = ["hub1", "sun", "planet", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        self._bandneed = (res["sun"], res["planet"])
        H = {"hub1": res["hub1"], "hub2": np.concatenate([res["sun"], res["planet"] - 0.0], 1), "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], res["pad"], res["knee"] - off_k], 1)}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self.greedy_drop(links=False); keep1 = ~self.drop
        f1 = H["hub1"][keep1].max(); f3 = H["h3"][keep1].max(); tr = H["stack"][keep1].max()
        Rs, Rp = self._levels(keep1)
        self._mk_links(f1, f3, Rs, Rp)
        self._tr_fit = tr
        items, idx = [], []
        for lk in self.geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        L["E"] = [self._HE]; self.Lneed = L
        self.greedy_drop(keep0=keep1)
        self.finalize()

    def _levels(self, keep):
        rs = self._bandneed[0][keep].max(); rp = self._bandneed[1][keep].max()
        rs, rp = max(rs, rp - 1.5), max(rp, rs - 1.5)                           # common strap radius +- 1.5 mm
        return rs, rp

    def _mk_links(self, f1, f3, Rs, Rp):
        D = self.D; P = self.p; zs = 0.5 * float(P["bh"])
        ds, _ = self._band_dirs("sun", 1.0); dp, _ = self._band_dirs("planet", 1.0)
        Cs = ds[len(ds) // 2] * (Rs + zs); Cp = dp[len(dp) // 2] * (Rp + zs)
        self.geo = _RGeo(D, self.hr, Cs, Cp, f1, f3)

    def finalize(self):
        D = self.D; P = D.p; keep = ~self.drop; g = self.g; off_k = P["tp"] + S.RUN
        H = self.Hneed
        f1 = H["hub1"][keep].max(); f3 = H["h3"][keep].max(); tr = H["stack"][keep].max()
        Rs, Rp = self._levels(keep)
        hE = self._HE[keep].max(0) if keep.any() else self._HE.max(0)
        xs, rE, f3, tr = self._E_profile(hE, f3, tr)
        u, c = D.u, D.c; k = math.tan(S.RAMP * D2R); bh = float(P["bh"])
        rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in self.Lneed.items()}
        for _ in range(3):
            self.link_pts = {}; lift = 0.0
            for lk in self.geo.links:
                pts_all = []; Rb = Rs if lk["name"] == "L1" else Rp
                for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
                    r = r.copy(); Sx = sarc; idx = np.nonzero(keep_s)[0]
                    if not len(idx): continue
                    kk = lk["ka"] if lk["ka"] is not None else lk["kb"]; F = f1 if kk == 0 else f3; lv = 0.0 if kk == 0 else S.UP
                    j = idx[0] if lk["ka"] is not None else idx[-1]
                    cen = c[kk] + F * u[kk]; den = float(dv[j] @ u[kk]); rc = (cen @ u[kk] + lv) / max(den, 0.2)
                    r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
                    jb = idx[-1] if lk["ka"] is not None else idx[0]                 # the band end: at least the band bottom
                    r = np.maximum(r, Rb - k * np.abs(Sx - Sx[jb]))
                    r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
                    lift = max(lift, float(r[jb]) + S.T_LINK - (Rb + bh))            # link above the band top
                    pts_all.append(dv[keep_s] * r[keep_s][:, None])
                self.link_pts[lk["name"]] = (lk["mem"], np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))
            break
        self.band_lift = round(max(lift, 0.0), 2)
        self.Rb = (Rs, Rp); self.f = [f1, 0.5 * (Rs + Rp), f3]; self.tr = tr; self.zb = tr
        sn = D.sn; hx = np.interp(self._Ex, xs, rE); self.hEx = hx
        self.rigid = {"hub1": (0, g["hub1"][1] + f1 * u[0]), "sun": (1, g["sun"][2] * Rs), "planet": (2, g["planet"][2] * Rp),
                      "hub3": (3, g["hub3"][1] + f3 * u[2]),
                      "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tr * sn), "pad": (5, g["pad"][1] + tr * sn),
                      "knee": (6, g["knee"][1] + (tr + off_k) * sn)}
        self._contact_only(); self._solids()

    def _band_surf(self, which, Rb, fr_list=(0.0, 0.5, 1.0), rad=None):
        bh = float(self.p["bh"]); rad = np.arange(0.0, bh + 1e-6, S.SPACING) if rad is None else rad
        out = []
        for f in fr_list:
            d, _ = self._band_dirs(which, f)
            for z in rad: out.append(d * (Rb + z))
        return np.concatenate(out)

    def _contact_only(self):
        D = self.D; P = D.p; u, c = D.u, D.c; F = self.f; tr = self.tr; tp = P["tp"]; out = []
        an = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        for k, mem in ((0, 0), (2, 3)):
            e, f = S.frame_of(u[k]); ring = self.hr[k] * (np.cos(an)[:, None] * e + np.sin(an)[:, None] * f)
            for z in np.linspace(F[k], F[k] + S.CROWN, 4): out.append((mem, c[k] + z * u[k] + ring))
            dd = S.disc(self.hr[k], 2.0); out.append((mem, c[k] + (F[k] + S.CROWN) * u[k] + dd[:, :1] * e + dd[:, 1:] * f))
        Rs, Rp = self.Rb
        out.append((1, self._band_surf("sun", Rs, (0.0, 1.0)))); out.append((2, self._band_surf("planet", Rp, (0.0, 1.0))))
        for nm, (mem, pts) in self.link_pts.items():
            if len(pts): out.append((mem, pts + S.T_LINK * unit(pts)))
        sn = D.sn; out.append((3, self.rigid["E"][1] + S.T_LINK * sn))
        fr = self.fr
        for mem, cen, z0, z1, R_ in ((3, fr["A0"], tr, tr + tp, PK.BOSS_R), (5, fr["Bm"], tr, tr + tp, PK.PAD_R)):
            e, f = S.frame_of(sn); ring = R_ * (np.cos(an)[:, None] * e + np.sin(an)[:, None] * f)
            for z in (z0, z1): out.append((mem, cen + z * sn + ring))
        out.append((5, self.rigid["pad"][1] + tp * sn))
        z0 = tr + tp + S.RUN; z1 = z0 + tp; lc = float(P["lc"]); L = lc + 2 * PK.BOSS_R; W = PK.KNEE_W
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
        self.cyl = {"hub1": (0, c[0] + F[0] * u[0], u[0]), "hub3": (3, c[2] + F[2] * u[2], u[2])}
        self.box = {}
        self.strap = {nm: (mem, pts + (S.T_LINK / 2) * unit(pts)) for nm, (mem, pts) in self.link_pts.items()}
        an = np.linspace(0, 2 * np.pi, 24, endpoint=False); self.cyl_surf = {}
        for nm, (mem, cen, ax) in self.cyl.items():
            rr = self.cyl_r[nm]; e, f = S.frame_of(ax)
            pts = [cen + z * ax + rr * (np.cos(an)[:, None] * e + np.sin(an)[:, None] * f) for z in np.linspace(0, S.CROWN, 5)]
            dd = S.disc(rr, 4.0); pts.append(cen + S.CROWN * ax + dd[:, :1] * e + dd[:, 1:] * f); self.cyl_surf[nm] = (mem, np.concatenate(pts))
        Rs, Rp = self.Rb
        self.band_mid = {"sun": (1, self._band_surf("sun", Rs, (0.5,), np.linspace(0, float(self.p["bh"]), 5))),
                         "planet": (2, self._band_surf("planet", Rp, (0.5,), np.linspace(0, float(self.p["bh"]), 5)))}
        self.Emid = (3, self.rigid["E"][1] + (S.T_LINK / 2) * D.sn)

    def collide(self, i):
        D = self.D; h = S.T_LINK / 2; hb = WALL / 2
        def tf(m, X): R_, t = self.T(m, i); return X @ R_.T + t
        cyl = {}
        for k, (m, cen, ax) in self.cyl.items(): R_, t = self.T(m, i); cyl[k] = (R_ @ cen + t, R_ @ ax)
        surf = {k: tf(m, X) for k, (m, X) in self.cyl_surf.items()}
        strap = {k: tf(m, X) for k, (m, X) in self.strap.items()}
        band = {k: tf(m, X) for k, (m, X) in self.band_mid.items()}
        Em = tf(*self.Emid); bx = self._boxes_at_final(i)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def vbox(X, nm, extra=0.0): cen, R_, half = bx[nm]; return float(self.sd_box(X, cen, R_, half).min()) - extra if len(X) else 1e9
        def vpp(A, Bq, extra): return float(cKDTree(Bq).query(A)[0].min()) - extra if len(A) and len(Bq) else 1e9
        cc = {}
        cc["L2-hub1"] = vcyl(strap["L2"], "hub1", h); cc["hub3-hub1"] = vcyl(surf["hub3"], "hub1"); cc["L1-hub3"] = vcyl(strap["L1"], "hub3", h)
        cc["planet-hub1"] = vcyl(band["planet"], "hub1", hb); cc["sun-hub3"] = vcyl(band["sun"], "hub3", hb)
        R1_, _ = self.T(1, i); con = R1_ @ (R(D.uK, D.rho * self.q[i, 1])[0] @ D.cK)          # contact line, scapula frame
        def far_c(X, r):
            w_ = X - (X @ con)[:, None] * con; return X[np.linalg.norm(w_, axis=1) > r]
        cc["L1-L2"] = vpp(far_c(strap["L1"], 12.0), far_c(strap["L2"], 12.0), 2 * h)
        cc["planet-L1"] = vpp(far_c(band["planet"], 6.0), far_c(strap["L1"], 6.0), hb + h)
        cc["sun-L2"] = vpp(far_c(band["sun"], 6.0), far_c(strap["L2"], 6.0), hb + h)
        for nm in ("knee", "pad"):
            cc[f"{nm}-hub1"] = vbox(surf["hub1"], nm); cc[f"{nm}-sun"] = vbox(band["sun"], nm, hb); cc[f"{nm}-planet"] = vbox(band["planet"], nm, hb)
            cc[f"{nm}-L1"] = vbox(strap["L1"], nm, h); cc[f"{nm}-L2"] = vbox(strap["L2"], nm, h)
        cc["pad-hub3"] = vbox(surf["hub3"], "pad"); cc["pad-E"] = vbox(Em, "pad", h)
        cc["E-hub1"] = vcyl(Em, "hub1", h); cc["E-sun"] = vpp(Em, band["sun"], h + hb); cc["E-planet"] = vpp(Em, band["planet"], h + hb)
        cc["E-L1"] = vpp(Em, strap["L1"], 2 * h)
        adj = {}
        c3, ax3 = cyl["hub3"]
        def far(X, ccen, ax, rr): w_ = X - ccen; return np.linalg.norm(w_ - (w_ @ ax)[:, None] * ax, axis=1) > rr
        L2f = strap["L2"][far(strap["L2"], c3, ax3, self.hr[2] + 1)]
        adj["E-L2"] = vpp(Em, L2f, 2 * h)
        adj["knee-hub3"] = vbox(surf["hub3"], "knee")
        fr = self.fr; pa = tf(3, fr["A0"][None])[0]
        Ef = Em[np.linalg.norm(Em - pa, axis=1) > PK.BOSS_R + 0.5]
        adj["knee-E"] = vbox(Ef, "knee", h) if len(Ef) else 1e9
        adj["sun-planet"] = vpp(far_c(band["sun"], 3.0), far_c(band["planet"], 3.0), 2 * hb)       # rolling pair off the contact
        self.last_clear = {k: round(v, 1) for k, v in list(cc.items()) + list(adj.items())}
        out = min(cc.values())
        if min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out

    def hub12(self): return 1e9


def _report(B, params):
    M = Model(B, params)
    if not M.kin_ok.any():
        B.reset(); r = B.report(); r["why"] = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure")}
        r["honest"] = True; return r, M
    r = M.run(); D = M.D; k = M.K["ang"][M.kin_ok]
    tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    r["roll"] = dict(rho=round(D.rho, 4), yspan=[round(v, 1) for v in M.yspan], xspan=[round(D.rho * v, 1) for v in M.yspan],
                     sun_arc_mm=round(abs(D.rho * (M.yspan[1] - M.yspan[0])) * D2R * 56 * math.sin(params.get("alpha_s", PARAMS["alpha_s"]) * D2R), 1),
                     Rb=[round(float(x), 1) for x in M.Rb], band_lift=M.band_lift,
                     th_window=[round(float(D.th_tab.min()), 1), round(float(D.th_tab.max()), 1)],
                     kin_ws=int(sum(1 for i in range(len(B.idx)) if M.kin_ok[i] and B.kind[i] == "ws")),
                     min_mdy_taken=round(float(M.fold["mdy"][tk].min()), 2) if tk else None,
                     min_mseg_taken=round(float(M.fold["mseg"][tk].min()), 2) if tk else None,
                     min_jac_taken=round(float(M.fold["jac"][tk].min()), 3) if tk else None)
    r["knee"] = dict(ang=[round(float(k.min()), 1), round(float(k.max()), 1)] if len(k) else None, tr=round(M.tr, 1))
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); return r


def no_slip_check(D, y_deg):
    """relative angular velocity of the rolling pair lies on the contact line (finite difference), max error deg"""
    err = 0.0
    for y in y_deg:
        a, b = D.Rroll(np.array([y - 0.01, y + 0.01]) * D2R); Rd = b @ a.T
        w_ = np.array([Rd[2, 1] - Rd[1, 2], Rd[0, 2] - Rd[2, 0], Rd[1, 0] - Rd[0, 1]]); w_ = unit(w_)
        con = R(D.uK, D.rho * y * D2R)[0] @ D.cK
        err = max(err, float(np.degrees(np.arccos(min(1.0, abs(w_ @ con))))))
    return err


def frozen(P, nc=110, nw=360):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]; P2["y_fix"] = list(M1.yspan)
    class Frozen(Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "Rb", "band_mid", "band_lift"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array([k == "ws" for k in B.kind]); fl = (M.why == "fold") & ws
    thp = np.degrees(np.arccos(np.clip(np.einsum("ni,i->n", M.Q[fl] @ M.D.u[2], M.D.u[0]), -1, 1)))
    lo, hi = float(M.D.th_tab.min()), float(M.D.th_tab.max())
    tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
                parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), roll_off=getattr(M, "roll_off", None), yspan=list(M.yspan),
                fold_ws=dict(n=int(fl.sum()), folded=int((thp < lo + FM).sum()), stretched=int((thp > hi - FM).sum()), window=[round(lo, 1), round(hi, 1)]),
                min_fold_margin_taken=round(float(np.minimum(M.fold["mdy"], M.fold["mseg"])[tk].min()), 2) if tk else None,
                min_jac_taken=round(float(M.fold["jac"][tk].min()), 3) if tk else None, rho=M.D.rho)


if __name__ == "__main__" and (len(sys.argv) < 2 or sys.argv[1] != "search"):
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        t = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    if mode == "viz":                                             # geometry export for docs/concepts/viz/concepts/<id>.js
        r, M = _report(B, par); D = M.D; L = lambda X, n=2: [[round(float(v), n) for v in p] for p in X]
        U = lambda v: L([v], 6)[0]
        G = dict(u=L(D.u, 6), c=L(D.c, 3), sa=U(D.sa), st=U(D.st), sn=U(D.sn), m=L([D.m])[0], f=[round(float(x), 2) for x in M.f],
                 Rb=[round(float(x), 2) for x in M.Rb], bh=float(M.p["bh"]), tr=round(float(M.tr), 2), tp=M.p["tp"], RUN=S.RUN,
                 uK=U(D.uK), v2=U(D.v2), cK=U(D.cK), q2r=round(math.degrees(D.q2r), 4), rho=round(D.rho, 5),
                 alpha=[M.p["alpha_s"], M.p["alpha_p"]], ylim=[round(float(D.ys.min()), 2), round(float(D.ys.max()), 2)],
                 yspan=[round(v, 2) for v in M.yspan], A0=L([M.fr["A0"]])[0], A0m=L([M.fr["A0m"]])[0], Bm=L([M.fr["Bm"]])[0],
                 eE=U(M.fr["eE"]), eK=U(M.fr["eK"]), FM=FM,
                 L1=L(M.link_pts["L1"][1][::max(1, len(M.link_pts["L1"][1]) // 12)]), L2=L(M.link_pts["L2"][1][::max(1, len(M.link_pts["L2"][1]) // 16)]),
                 gap=r["gap"], reach=r["reach"])
        print(json.dumps(G)); sys.exit()
    if mode == "kin":
        M = Model(B, par); ws = [i for i in range(len(B.idx)) if B.kind[i] == "ws"]
        print("kin ws", int(M.kin_ok[ws].sum()), "/", len(ws), "clip", int(M.kin_ok.sum() - M.kin_ok[ws].sum()), "why",
              {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure")}, "yspan", M.yspan, "rho", M.D.rho,
              "th window", M.D.th_tab.min(), M.D.th_tab.max(), "noslip err deg", no_slip_check(M.D, np.linspace(M.yspan[0], M.yspan[1], 9)))
        sys.exit()
    r, M = _report(B, par)
    if mode == "redteam":                                         # the pose that jams, the point that pinches, the optimistic number
        taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
        lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:20]:20s} pl {B.poses[i]['plane']:6.1f} el {B.poses[i]['elev']:6.1f} ax {B.poses[i]['axial']:6.1f}"
        a = PK.audit(M, B); out = dict(report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, why=r["why"],
                                       roll=r.get("roll"), parts_ib14=r.get("parts_ib14"), parts_pairs=r.get("parts_pairs"),
                                       near_touch=dict(min_mm=a["near_touch_min_mm"], low=a["near_touch_low"], gap1=a["gap_near1"], gap2=a["gap_near2"]),
                                       overhead140=a["overhead140"])
        names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, X in M.rigid.values()] + [len(X) for _, X in M.link_pts.values()]
        cut = np.cumsum([0] + sizes); low = {}
        for i in range(len(B.idx)):
            if not taken(i): continue
            d = B.res[i][:cut[-1]]
            for k, nm in enumerate(names):
                v = float(d[cut[k]:cut[k + 1]].min()) if cut[k + 1] > cut[k] else 1e9
                if v < low.get(nm, (1e9,))[0]: low[nm] = (round(v, 2), lab(i))
        out["closest_per_part"] = low
        el = np.array([pp["elev"] for pp in B.poses]); pl = np.array([pp["plane"] for pp in B.poses])
        groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= 140)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                      behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
        out["groups"] = {}
        for gname, ii in groups.items():
            ii = list(ii); tk = [i for i in ii if taken(i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
            out["groups"][gname] = dict(taken=f"{len(tk)}/{len(ii)}", median_mm=round(float(np.nanmedian(dd)), 1),
                                        ib14=round(float(((dd >= 2) & (dd <= 14)).mean()), 3), not_taken={w: int(sum(1 for i in ii if not taken(i) and M.why[i] == w)) for w in set(M.why[ii]) if w})
        fl = [i for i in range(len(B.idx)) if M.why[i] == "fold" and B.kind[i] == "ws"]
        thp = np.degrees(np.arccos(np.clip(np.einsum("ni,i->n", M.Q[fl] @ M.D.u[2], M.D.u[0]), -1, 1))) if fl else np.zeros(0)
        out["fold_ws"] = dict(n=len(fl), th_below=int((thp < M.D.th_tab.min() + FM).sum()), th_above=int((thp > M.D.th_tab.max() - FM).sum()),
                              window=[round(float(M.D.th_tab.min()), 1), round(float(M.D.th_tab.max()), 1)])
        out["parts_poses"] = [(lab(i), M.last_pair.get(i)) for i in range(len(B.idx)) if M.why[i] == "parts"][:8]
        out["contact_poses"] = [(lab(i), M.why[i]) for i in range(len(B.idx)) if M.why[i] in ("skin", "contact")][:12]
        print(json.dumps(out, default=float, indent=1))
        if len(sys.argv) > 3 and not sys.argv[3].startswith("--"): json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        sys.exit()
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "roll", r.get("roll"),
          "knee", r.get("knee"), f"{time.time() - t:.0f}s", B.mode)
    print("parts", r.get("parts_ib14"), r.get("parts_pairs"), "min clear", r.get("min_clear_taken"), "res", r.get("res_max"))


# ---- search (local, niced, one process per seed): random stage then a diagonal ES from the top, near-touch objective ----
RANGES = dict(alpha_s=(8.0, 35.0), alpha_p=(4.0, 16.0), beta=(-60.0, 60.0), bh=(6.0, 10.0),
              az1=(96.16, 106.16), el1=(58.9, 68.9), az2=(25.15, 35.15), el2=(42.0, 52.0), wd=(65.4, 75.4), wa=(-13.1, -3.1),
              b3=(0.15, 0.40), lE=(51.5, 67.5), lc=(23.2, 33.2), phiE=(-20.8, 9.2), phib=(-69.9, -39.9))


def _score(B, par):
    try:
        r, M = _report(B, par)
        if not M.kin_ok.any(): return dict(gap=999.0, obj=999.0), None
        a = PK.audit(M, B); r["near"] = dict(min_mm=a["near_touch_min_mm"], gap1=a["gap_near1"], gap2=a["gap_near2"], n1=a["near1_poses"])
        r["overhead"] = a["overhead140"]; r["obj"] = a["gap_near1"]
        return r, M
    except Exception as e:                                       # noqa: BLE001
        return dict(gap=400.0, obj=400.0, err=repr(e)[:200]), None


def search(seed, n_rand, n_es, out, start=None):
    rng = np.random.default_rng(seed); B = CB.Bench(n_clip=60, n_ws=160); keys = list(RANGES); hist = []
    lo = np.array([RANGES[k][0] for k in keys]); hi = np.array([RANGES[k][1] for k in keys])
    x0 = np.array([dict(PARAMS, **(start or {}))[k] for k in keys], float)
    def ev(x, tag):
        par = {k: float(round(v, 4)) for k, v in zip(keys, np.clip(x, lo, hi))}
        rho = math.sin(par["alpha_p"] * D2R) / math.sin(par["alpha_s"] * D2R)
        if not 0.15 <= rho <= 1.7: r = dict(gap=999.0, obj=999.0, err="rho out of range")
        else: r, _ = _score(B, par)
        e = dict(k=f"{seed}-{tag}-{len(hist)}", t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=par,
                 **{m: r.get(m) for m in ("inband14", "inband10", "reach", "follow", "contact", "gap", "obj")},
                 near=r.get("near"), roll=r.get("roll"), why=r.get("why"), parts_ib14=r.get("parts_ib14"), err=r.get("err"))
        hist.append((float(r.get("obj", 999.0)), x.copy(), e))
        with open(out, "a") as f: f.write(json.dumps(e, default=float) + "\n")
        print(e["k"], e["gap"], e["obj"], e["reach"], e["inband14"], e["follow"], e["contact"], flush=True)
    ev(x0, "x0")
    for j in range(n_rand):
        x = x0 + rng.normal(0, 0.25, len(keys)) * (hi - lo) if j % 3 else lo + rng.random(len(keys)) * (hi - lo)
        ev(np.clip(x, lo, hi), "r")
    sig = 0.12 * (hi - lo); lam, mu = 6, 3
    for g in range(max(1, n_es // lam)):
        top = sorted(hist, key=lambda h: h[0])[:mu]; m = np.mean([h[1] for h in top], 0)
        for _ in range(lam): ev(np.clip(m + rng.normal(0, 1, len(keys)) * sig, lo, hi), f"es{g}")
        new = sorted(hist, key=lambda h: h[0])[:mu]
        sig *= 0.85 if new[0][0] >= top[0][0] - 1e-9 else 1.05
        sig = np.maximum(sig, 0.01 * (hi - lo))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "search":
    search(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], json.loads(sys.argv[6]) if len(sys.argv) > 6 else None)

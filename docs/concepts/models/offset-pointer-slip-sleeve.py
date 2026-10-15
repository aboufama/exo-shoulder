"""Concept model: OFFSET-CENTRE 2R POINTER + SLIDING TWIST SLEEVE AT THE CUFF, id offset-pointer-slip-sleeve.

Chain (docs/concepts/catalogue.json, entry offset-pointer-slip-sleeve; docs/concepts/offset-pointer-slip-sleeve.md):
  S (scapula handler) -> J1 O20 hub, axis a1 through a centre O (|o| mm from GH, fixed in the scapula frame) -> link 1
  (14 x 4 strap on the great circle about O from a1 to j2) -> J2 O20 hub, axis j2 through O, j2 = branch * unit(a1 x dh)
  -> bar (14 x 4 strap) ending in a rod clamp (boss) on the line O -> C -> O6 rod on that line -> linear-rotary sleeve
  O12 x 25 on the rod (J3 = spin about the rod, ACTIVE; slide lam = |C - O|, passive) -> Hooke U at the cuff (outer axis
  u2 fixed in the cuff, inner axis u1 fixed in the sleeve; 2 passive) -> the user's upper-arm cuff at C (arm-fixed).
ACTIVE DOF 3 (J1, J2, J3), PASSIVE 3 (slide, U pitch, U yaw). The cuff point C = Q C0 fixes dh = unit(C - O) (J1, J2:
the pointer) and lam (the slide); the cuff's orientation relative to the rod fixes the two U angles and J3. Six chain
coordinates for the cuff's six DOF, every passive one set by closure: nothing can sag.

Spec corrections (said in the .md): the catalogue took C0 and the humerus axis from BP.V0, the rig's BIND pose; the
bench's rest frame (Q = I) is the posed rest pose (plane 0, elev 0, axial 0, flex 12.5), where the humerus hangs along
-y. C0 is therefore placed on that skin: station s along the humerus, azimuth caz around it (0 = lateral, + posterior),
rod axis hC mm off the skin. The U neutral is centred on the mean rod direction in the arm frame (not the rest one), and
the U is modelled at real size (ring around the sleeve + two cheeks on the cuff), so hC >= 11 for the ring to clear.

Parts at real size (mm; L1 keep-out level, docs/CAD_STANDARD.md L1), skin-facing surfaces sampled on a 2 mm grid
(~1 point / 4 mm2, the baseline's convention, tools/concept_baseline.py):
  J1 hub   O20 flat disc (lower face) at O + F1 a1, fixed in the scapula frame (base side of J1); wall to F1 + 12.25
           checked for contact.
  link 1   14 x 4 strap on the great circle about O from a1 to j2 (90 deg), underside fitted per sample radially
           from O; upper member at J1 (>= F1 + 4.15 over the hub), lower member at J2 (its J2 end = the J2 hub face F2).
  J2 hub   O20 flat disc at O + F2 j2 (link 1 frame).
  bar      14 x 4 strap in the bar frame [dh, j2, dh x j2]: a cap arc about O from j2 (polar 90 deg from dh) down to
           th_k deg from dh while turning by psi_end about dh, then a straight run along the rod line at azimuth psi_end
           down to the rod clamp; underside fitted per sample along a direction field radial from O on the cap, radial
           from the rod line along the arm (the spec's 'fitted radially from the humerus axis for samples > 100 mm');
           upper member at J2 (>= F2 + 4.15 over the hub). psi_end = the circular mean, over the design poses, of the
           arm's outward direction at the cuff seen in the bar frame (the J3 centre) + dpsi.
  boss     O12 x 10 rod clamp at the bar's end, x in [x_top - 10, x_top], x_top = lam_lo - 15 (spec).
  rod      O6 on the line from x_top to lam_hi + 15 (spec).
  sleeve   O12 x 25 linear-rotary bushing centred at C.
  U ring   annulus around the sleeve, outer radius max(9, yaw clearance + 2.5), 6 wide, at C.
  cheeks   two 3 x 10 plates on the cuff (arm-fixed) beside the ring along u2, feet at the rest skin + 2 (cuff shell).
Axisymmetric parts (rod, boss, sleeve, ring) are sampled on the half facing the arm in each pose (their shape does not
change with the spin) and checked for contact on their whole circumference.
A pose is TAKEN iff: dh is >= 12 deg from +-a1 (pointer singularity); both U angles within +-u_lim; lam inside the rod's
travel window (<= rod_cap, the window that holds the most design poses); along each fit clip (full rate, 10 fps) no
joint or passive coordinate steps > 25 deg between consecutive frames (branch flip); link 1 vs bar, bar vs the J1 hub
and the arm-side parts vs the shoulder-side parts keep >= 1 mm (point clouds through the part thickness); no metal
inside the body (else recorded as contact). Rigid heights are the p-th percentile (pct) over the kinematically valid
bench poses - concept_baseline.py's convention: poses above it are recorded as contact.

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/offset-pointer-slip-sleeve.py [kin|check|sweep|best]
"""
import json, math, os, sys, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
BP = CB.BP
ID = "offset-pointer-slip-sleeve"
D2R = math.pi / 180

# ---- hardware (docs/HARDWARE.md v5 O20 joint; catalogue spec) -----------------------------------------------------
HUB_R, CROWN = 10.0, 12.25
STRAP_W, STRAP_T = 14.0, 4.0                                  # link 1 and bar (spec 14 x 4)
UP = STRAP_T + 0.15                                           # distal member over the proximal member's face at a hub
ROD_R, BOSS_R, BOSS_L = 3.0, 6.0, 10.0
SLV_R, SLV_L = 6.0, 25.0
RING_RO0, RING_W, RING_SEC = 9.0, 6.0, 2.5
CHEEK_T, CHEEK_L, CUFF_T = 3.0, 10.0, 2.0
CLEAR, PART_CLEAR, SP = 2.0, 1.0, 2.0
SING, JUMP = 12.0, 25.0
REST = dict(plane=0.0, elev=0.0, axial=0.0, flex=12.5, pron=0.0)

PARAMS = dict(o=20.0, o_az=14.2, o_el=68.4,      # O = o * bvec(o_az, o_el) (scapula frame); spec unit(-0.36, 0.93, 0.09)
              a1_az=115.0, a1_el=42.8,           # J1 axis bvec(a1_az, a1_el); spec unit(0.31, 0.68, 0.67)
              branch=-1,                         # j2 = branch * unit(a1 x dh); -1: J2 hub on the posterior cap (spec)
              s=200.0, caz=0.0, hC=12.0,         # cuff: station along the humerus (mm), azimuth (deg, 0 lateral, + posterior), rod axis over skin
              u_lim=40.0, rod_cap=70.0,          # U angle limit per axis (deg), slide travel cap (mm)
              dpsi=0.0, th_k=35.0, rho_c=62.0,   # bar routing: azimuth about the rod line vs the J3 centre; cap arc end (deg from dh); nominal radius
              pct=100.0)
SWEEP = dict(o=[0, 5, 10, 15, 20, 30], o_az=[-60, -30, 14.2, 60, 120, 180], o_el=[20, 45, 68.4, 90],
             a1_az=[60, 90, 115, 140, 170], a1_el=[20, 42.8, 60, 75], branch=[-1, 1],
             s=[150, 175, 200, 225, 250], caz=[-60, -30, 0, 30, 60], hC=[11, 12, 14, 16],
             u_lim=[30, 40, 45], rod_cap=[40, 60, 80], dpsi=[-60, -30, 0, 30, 60], th_k=[25, 35, 50], pct=[90, 95, 98, 100])


# ---- small geometry ------------------------------------------------------------------------------------------------
def unit(x): x = np.asarray(x, float); return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi


def perp(u):
    a = unit(np.cross(u, [0.0, 0.0, 1.0]) if abs(u[2]) < 0.9 else np.cross(u, [1.0, 0.0, 0.0])); return a, np.cross(u, a)


def disc(rad=HUB_R, sp=SP):
    g = np.arange(-rad + sp / 2, rad, sp); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rad ** 2
    return np.stack([X[k], Y[k]], 1)


def across(w=STRAP_W, sp=SP):
    return np.arange(-w / 2, w / 2 + 1e-6, sp)


def resample(P, sp=SP):
    """polyline P (m, k) -> parameter values t (on the polyline's index scale) every sp mm of arc length"""
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.r_[0, np.cumsum(seg)]
    n = max(2, int(s[-1] / sp) + 1); ss = np.linspace(0, s[-1], n)
    return np.interp(ss, s, np.arange(len(P)))


_REST_EX = None
def rest_dist(P):
    global _REST_EX
    if _REST_EX is None: _REST_EX = CB._Exact(BP.posed(REST))
    return _REST_EX(P)


_C0_CACHE = {}
def cuff_point(s, caz, hC):
    """rest-frame cuff point C0 (rod axis), its outward skin direction n_C and the skin point under it"""
    k = (round(s, 2), round(caz, 2))
    if k not in _C0_CACHE:
        n = np.array([-math.sin(caz * D2R), 0.0, math.cos(caz * D2R)])        # 0 = lateral (+z), + = posterior (-x)
        a = np.array([0.0, -s, 0.0]); r = 120.0
        for _ in range(80):
            d = float(rest_dist((a + r * n)[None])[0])
            if abs(d) < 0.02: break
            r -= d
        _C0_CACHE[k] = (a, n, r)
    a, n, r = _C0_CACHE[k]
    return a + (r + hC) * n, n, a + r * n


def sd_cyl(P, c0, ax, r, h0, h1):
    w = P - c0; z = w @ ax; rr = np.linalg.norm(w - z[:, None] * ax, axis=1)
    dr = rr - r; dz = np.maximum(h0 - z, z - h1)
    return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))


# ---- the model -----------------------------------------------------------------------------------------------------
class Model:
    def __init__(self, B, params=None):
        P = dict(PARAMS); P.update(params or {}); self.p = P; self.B = B
        Z = CB._poses_all(); self.Z = Z
        self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.kind = np.array(B.kind); n = len(B.idx)
        names = list(Z["NAMES"]); cid = Z["CID"]
        self.clip_ii = {}
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; self.clip_ii[nm] = ii[np.argsort(Z["FI"][ii], kind="stable")]
        self.ws_ii = np.nonzero(cid == names.index("Workspace (envelope)"))[0]
        self.O = P["o"] * bvec(P["o_az"], P["o_el"]); self.a1 = unit(bvec(P["a1_az"], P["a1_el"]))
        self.C0, self.nC, self.skin0 = cuff_point(P["s"], P["caz"], P["hC"])
        self.why = np.array([""] * n, dtype=object)
        self.design()

    # ---- kinematics ------------------------------------------------------------------------------------------------
    def kin(self, HG):
        p, O, a1 = self.p, self.O, self.a1
        C = HG @ self.C0; d = C - O; lam = np.linalg.norm(d, axis=1); dh = d / lam[:, None]
        ang = np.degrees(np.arccos(np.clip(dh @ a1, -1, 1)))
        j2 = p["branch"] * unit(np.cross(a1, dh)); nb = np.cross(dh, j2); k1 = np.cross(a1, j2)
        r_arm = np.einsum("nji,nj->ni", HG, dh)                    # rod direction in the arm (rest) frame
        vout = HG @ self.nC                                       # arm's outward direction at the cuff
        psi_out = np.arctan2((vout * nb).sum(1), (vout * j2).sum(1))
        k = dict(C=C, lam=lam, dh=dh, ang=ang, j2=j2, nb=nb, k1=k1, r_arm=r_arm, psi_out=psi_out,
                 sing_ok=(ang >= SING) & (ang <= 180 - SING))
        if hasattr(self, "e_r"): self._kin_u(HG, k)
        return k

    def _kin_u(self, HG, k):
        r = k["r_arm"]; e_r, u2, e3 = self.e_r, self.u2, self.e3
        alpha = np.arctan2(r @ e3, r @ e_r); beta = np.arcsin(np.clip(r @ u2, -1, 1))
        u1 = unit(np.cross(u2[None], r)); u1w = np.einsum("nij,nj->ni", HG, u1)
        J3 = np.arctan2((u1w * k["nb"]).sum(1), (u1w * k["j2"]).sum(1))
        J1 = np.arctan2((np.cross(self.j2r, k["j2"]) @ self.a1), k["j2"] @ self.j2r)
        J2 = np.arctan2((k["dh"] * k["k1"]).sum(1), k["dh"] @ self.a1)
        k.update(alpha=alpha, beta=beta, J1=J1, J2=J2, J3=J3, q=np.stack([J1, J2, J3, alpha, beta], 1))
        lim = self.p["u_lim"] * D2R
        k["u_ok"] = (np.abs(alpha) <= lim) & (np.abs(beta) <= lim)

    def design(self):
        """design-time choices from the design poses (full-rate fit clips + every workspace pose; never held-out clips):
        the U neutral, the J1 zero, the J3 centre (bar routing azimuth) and the rod's travel window"""
        Z, p = self.Z, self.p
        dz = np.r_[np.concatenate(list(self.clip_ii.values())), self.ws_ii]
        HGd = Z["HG"][dz].astype(float); k = self.kin(HGd); ok = k["sing_ok"]
        self.e_r = unit(k["r_arm"][ok].mean(0))
        self.u2 = unit(np.cross(self.nC, self.e_r)); self.e3 = np.cross(self.e_r, self.u2)
        ncl = sum(len(v) for v in self.clip_ii.values())
        self.j2r = unit(np.median(k["j2"][:ncl][ok[:ncl]], axis=0))
        self._kin_u(HGd, k); ok &= k["u_ok"]
        ps = k["psi_out"][ok]; self.psi_ref = math.atan2(np.sin(ps).mean(), np.cos(ps).mean())
        self.psi_end = self.psi_ref + p["dpsi"] * D2R
        lam = np.sort(k["lam"][ok]); cap = p["rod_cap"]
        if not len(lam): self.lam_lo, self.lam_hi = 0.0, 0.0; self.dead = True; return
        if lam[-1] - lam[0] <= cap: lo, hi = lam[0], lam[-1]
        else:
            j = np.searchsorted(lam, lam + cap, side="right") - np.arange(len(lam)); a = int(np.argmax(j)); lo, hi = lam[a], lam[a] + cap
        self.lam_lo, self.lam_hi = float(lo), float(hi); self.dead = False
        okw = ok & (k["lam"] >= lo - 1e-6) & (k["lam"] <= hi + 1e-6)
        self.beta_max = float(np.abs(k["beta"][okw]).max()) if okw.any() else 0.0
        self.x_top = self.lam_lo - 15.0; self.x_bot = self.lam_hi + 15.0
        yaw = 0.5 * SLV_L * math.sin(self.beta_max) + SLV_R * math.cos(self.beta_max) + 0.5
        self.ring_ro = max(RING_RO0, yaw + RING_SEC); self.cheek_in = self.ring_ro + 0.5
        self.design_cover = float(okw.mean())

    def classify(self):
        k = self.kin(self.HG); self.k = k
        ok = k["sing_ok"].copy(); self.why[:] = ""; self.why[~ok] = "sing"
        self.why[ok & ~k["u_ok"]] = "U"; ok &= k["u_ok"]
        sl = (k["lam"] >= self.lam_lo - 1e-6) & (k["lam"] <= self.lam_hi + 1e-6)
        self.why[ok & ~sl] = "slide"; ok &= sl
        flip_at = {}
        for nm, ii in self.clip_ii.items():
            kk = self.kin(self.Z["HG"][ii].astype(float))
            okf = kk["sing_ok"] & kk["u_ok"] & (kk["lam"] >= self.lam_lo - 1e-6) & (kk["lam"] <= self.lam_hi + 1e-6)
            prev = None
            for j, gi in enumerate(ii):
                f = False
                if okf[j] and prev is not None:
                    f = np.degrees(np.abs(wrap(kk["q"][j] - kk["q"][prev]))).max() > JUMP
                flip_at[int(gi)] = f; prev = j if okf[j] else None
        flip = np.array([flip_at.get(int(gi), False) for gi in self.B.idx]) & (self.kind == "clip")
        self.why[ok & flip] = "flip"; ok &= ~flip
        self.kok = ok
        return ok

    # ---- part samples (body frames) --------------------------------------------------------------------------------
    def build_parts(self):
        """sample points of the fitted parts in their body frames: base X0 (m,3) + fit direction G (m,3) + lower bound"""
        p = self.p; parts = {}
        # J1 hub: scapula frame, flat disc normal a1 (centre O + F1 a1)
        e, f = perp(self.a1); dd = disc()
        parts["hub1"] = dict(frame="S", X=self.O + dd[:, :1] * e + dd[:, 1:] * f, G=np.broadcast_to(self.a1, (len(dd), 3)).copy(), lo=20.0)
        # link 1 + J2 hub: link-1 local frame (x = a1, y = j2, z = a1 x j2), points relative to O
        rr = 62.0; ns = max(3, int(0.5 * math.pi * rr / SP) + 1); s = np.linspace(0, 0.5 * math.pi, ns); cs = across() / rr
        D = np.stack([np.cos(s), np.sin(s), np.zeros_like(s)], 1)
        U = unit(D[:, None, :] * np.cos(cs)[None, :, None] + np.array([0, 0, 1.0])[None, None, :] * np.sin(cs)[None, :, None]).reshape(-1, 3)
        parts["link1"] = dict(frame="L1", X=np.zeros_like(U), G=U, lo=20.0, s=np.repeat(s, len(cs)))
        parts["hub2"] = dict(frame="L1", X=dd[:, 0, None] * np.array([1.0, 0, 0]) + dd[:, 1, None] * np.array([0, 0, 1.0]),
                             G=np.broadcast_to(np.array([0, 1.0, 0]), (len(dd), 3)).copy(), lo=20.0)
        # bar: bar-local frame (x = dh, y = j2, z = dh x j2)
        th_k = p["th_k"] * D2R; pe = self.psi_end; rc = p["rho_c"]
        th = np.linspace(0.5 * math.pi, th_k, 200); ps = np.linspace(0, pe, 200)
        cap = rc * np.stack([np.cos(th), np.sin(th) * np.cos(ps), np.sin(th) * np.sin(ps)], 1)
        rdir = np.array([0.0, math.cos(pe), math.sin(pe)])
        x0, r0 = rc * math.cos(th_k), rc * math.sin(th_k); x1, r1 = self.x_top - BOSS_L, BOSS_R
        tt = np.linspace(0, 1, 200)[1:]
        arm = np.stack([x0 + (x1 - x0) * tt, np.zeros_like(tt), np.zeros_like(tt)], 1) + ((r0 + (r1 - r0) * tt)[:, None] * rdir)
        line = np.r_[cap, arm]; ti = resample(line); idx = np.arange(len(line))
        C = np.stack([np.interp(ti, idx, line[:, j]) for j in range(3)], 1)
        T = unit(np.gradient(C, axis=0))
        xx = C[:, 0]; w = np.clip((xx - x0) / 15.0, 0, 1) * (ti >= len(cap) - 1)       # blend radial-from-O -> radial-from-line
        g_cap = unit(C); g_arm = np.broadcast_to(rdir, C.shape)
        G = unit((1 - w)[:, None] * g_cap + w[:, None] * g_arm)
        G = unit(G - (G * T).sum(1, keepdims=True) * T)                                  # keep the fit direction normal to the strap
        A = unit(np.cross(T, G)); c = across()
        X = (C[:, None, :] + c[None, :, None] * A[:, None, :]).reshape(-1, 3); Gb = np.repeat(G, len(c), 0)
        rperp = np.linalg.norm(X[:, 1:], axis=1)
        lo = np.where(np.repeat(w, len(c)) > 0, BOSS_R - rperp, 20.0 - np.linalg.norm(X, axis=1))   # stay off the rod line / O
        parts["bar"] = dict(frame="BAR", X=X, G=Gb, lo=lo, st=np.repeat(np.arange(len(C)), len(c)), arm=np.repeat(w > 0, len(c)))
        self.bar_center = C; self.parts = parts

    def frame(self, nm, i=None):
        k = self.k
        if nm == "S": return None
        if nm == "L1": R = np.stack([np.broadcast_to(self.a1, k["j2"].shape), k["j2"], k["k1"]], -1)
        elif nm == "BAR": R = np.stack([k["dh"], k["j2"], k["nb"]], -1)
        return R if i is None else R[i]

    def place(self, nm, i, X):
        """body-frame points -> scapula frame for pose i"""
        if nm == "S": return X
        return X @ self.frame(nm, i).T + self.O

    def to_T(self, i, X): return X @ self.RS[i].T

    # ---- fit -------------------------------------------------------------------------------------------------------
    def _d(self, i, PT):
        """distance for tracing: the bench grid inside its box, 'far' (31.75) outside (traced parts sit near the shoulder)"""
        B = self.B
        if B.grid is None: return B.dist(i, PT)
        g = (PT + CB.HALF) / CB.H_GRID; n = B.grid.shape[1]
        inside = np.all((g >= 0) & (g <= n - 1 - 1e-9), axis=1); out = np.full(len(PT), 31.75)
        if inside.any(): out[inside] = B.dist(i, PT[inside])
        return out

    def trace(self, poses, names, iters=30):
        """per pose, the height h along G at which every sample of the named parts sits CLEAR mm off the skin"""
        parts = self.parts; sizes = [len(parts[nm]["X"]) for nm in names]; cut = np.cumsum([0] + sizes)
        lo = np.concatenate([np.broadcast_to(parts[nm]["lo"], (len(parts[nm]["X"]),)) for nm in names])
        out = np.zeros((len(poses), cut[-1]))
        for a, i in enumerate(poses):
            H = np.full(cut[-1], 90.0)
            for _ in range(iters):
                PS = [self.place(nm, i, parts[nm]["X"] + H[cut[k]:cut[k + 1], None] * parts[nm]["G"]) for k, nm in enumerate(names)]
                d = self._d(i, self.to_T(i, np.concatenate(PS))) - CLEAR
                Hn = np.maximum(H - d, lo)
                if np.abs(Hn - H).max() < 0.05: H = Hn; break
                H = Hn
            out[a] = H
        return {nm: out[:, cut[k]:cut[k + 1]] for k, nm in enumerate(names)}

    def red(self, A):
        return np.percentile(A, self.p["pct"], axis=0) if self.p["pct"] < 100 else A.max(0)

    def fit(self):
        good = self.classify(); poses = np.nonzero(good)[0]; self.poses_fit = poses
        if len(poses) < 3: self.dead = True; return
        self.build_parts(); P = self.parts
        need = self.trace(poses, ["hub1", "link1", "hub2", "bar"])
        h = {nm: self.red(v) for nm, v in need.items()}
        self.need = need
        F1 = float(h["hub1"].max())
        # link 1: upper member at J1 (over the hub disc), lower member at J2 (its end = the J2 hub face)
        L = P["link1"]; rr = np.maximum(h["link1"], 30.0); off = np.abs(L["s"]) * rr                # arc distance from a1 (mm)
        hl = h["link1"].copy(); near1 = off < HUB_R + 2; hl[near1] = np.maximum(hl[near1], F1 + UP)
        off2 = np.abs(0.5 * math.pi - L["s"]) * rr; near2 = off2 < HUB_R + 2
        F2 = float(max(h["hub2"].max(), hl[near2].max())); hl[near2] = F2
        hb = h["bar"].copy(); Bp = P["bar"]
        Xb = Bp["X"] + hb[:, None] * Bp["G"]; ax2 = np.array([0, 1.0, 0])
        rad = np.linalg.norm(Xb - (Xb @ ax2)[:, None] * ax2, axis=1); near = (rad < HUB_R + 2) & ((Xb @ ax2) > 0)
        hb[near] = np.maximum(hb[near], F2 + UP)
        self.F1, self.F2, self.h = F1, F2, dict(link1=hl, bar=hb)
        self.dead = False

    # ---- posed geometry --------------------------------------------------------------------------------------------
    def shoulder_parts(self, i, thick=False):
        """scapula-frame sample points of hub1, link1, hub2, bar (+ through the thickness when thick)"""
        P = self.parts; e, f = perp(self.a1); out = {}
        lv = (0.0, STRAP_T / 2, STRAP_T) if thick else (0.0,)
        out["hub1"] = [P["hub1"]["X"] + self.F1 * self.a1]
        out["link1"] = [self.place("L1", i, (self.h["link1"] + z)[:, None] * P["link1"]["G"]) for z in lv]
        out["hub2"] = [self.place("L1", i, P["hub2"]["X"] + self.F2 * np.array([0, 1.0, 0]))]
        out["bar"] = [self.place("BAR", i, P["bar"]["X"] + (self.h["bar"] + z)[:, None] * P["bar"]["G"]) for z in lv]
        return {k: np.concatenate(v) for k, v in out.items()}

    def cyl_pts(self, i, x0, x1, r, half=True, sp=SP):
        """points on a cylinder about the rod line (x from O along dh), the half facing the arm (or all)"""
        k = self.k; dh, j2, nb = k["dh"][i], k["j2"][i], k["nb"][i]
        vin = -(self.HG[i] @ self.nC); vin = unit(vin - (vin @ dh) * dh); vb = np.cross(dh, vin)
        nx = max(2, int((x1 - x0) / sp) + 1); xs = np.linspace(x0, x1, nx)
        span = (0.5 if half else 1.0) * math.pi; na = max(3, int(2 * span * r / sp) + 1)
        ph = np.linspace(-span, span, na, endpoint=not (not half))
        R = r * (np.cos(ph)[:, None] * vin + np.sin(ph)[:, None] * vb)
        return (self.O + xs[:, None, None] * dh + R[None]).reshape(-1, 3)

    def arm_parts(self, i, half=True):
        """rod, boss, sleeve, ring (about the rod line) and the cheeks (arm-fixed) in the scapula frame"""
        k = self.k; lam = k["lam"][i]; out = {}
        out["boss"] = self.cyl_pts(i, self.x_top - BOSS_L, self.x_top, BOSS_R, half)
        out["rod"] = self.cyl_pts(i, self.x_top, self.x_bot, ROD_R, half)
        out["sleeve"] = self.cyl_pts(i, lam - SLV_L / 2, lam + SLV_L / 2, SLV_R, half)
        out["ring"] = self.cyl_pts(i, lam - RING_W / 2, lam + RING_W / 2, self.ring_ro, half)
        out["cheeks"] = self.HG[i] @ self.cheek_rest().T
        return {kk: (v.T if kk == "cheeks" else v) for kk, v in out.items()}

    def cheek_rest(self):
        if not hasattr(self, "_cheeks"):
            g = np.arange(-CHEEK_L / 2 + 1, CHEEK_L / 2, SP); pts = []
            for sgn in (-1, 1):
                for t in np.arange(self.cheek_in + 1.0, self.cheek_in + CHEEK_T, SP):
                    for a in g:
                        X = self.C0 + sgn * t * self.u2 + a * self.e_r
                        r = X - (X @ np.array([0, -1.0, 0])) * np.array([0, -1.0, 0])
                        pts.append(X)
            Q = np.array(pts); n = self.nC
            # feet on the cuff shell: drop each point along -n to the rest skin + CUFF_T
            for _ in range(40):
                d = rest_dist(Q) - CUFF_T; Q = Q - d[:, None] * n
                if np.abs(d).max() < 0.05: break
            self._cheeks = Q
        return self._cheeks

    def scored(self, i):
        sp = self.shoulder_parts(i); ap = self.arm_parts(i)
        return np.concatenate(list(sp.values()) + list(ap.values()))

    def contact_extra(self, i):
        """surfaces checked for contact only: hub walls, full circumference of the rod-line parts"""
        a1 = self.a1; e, f = perp(a1); ang = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        ring = lambda c, ax, ea, fa: np.concatenate([c + z * ax + HUB_R * (np.cos(ang)[:, None] * ea + np.sin(ang)[:, None] * fa) for z in np.linspace(0, CROWN, 4)])
        w1 = ring(self.O + self.F1 * a1, a1, e, f)
        j2 = self.k["j2"][i]; e2, f2 = perp(j2); w2 = ring(self.O + self.F2 * j2, j2, e2, f2)
        ap = self.arm_parts(i, half=False)
        return np.concatenate([w1, w2] + [v for kk, v in ap.items() if kk != "cheeks"])

    def collide(self, i):
        """min clearance (mm) between parts that must not touch; pairs: link1-bar (off the J2 hub), bar-J1 hub,
        shoulder-side vs arm-side parts"""
        from scipy.spatial import cKDTree
        sp = self.shoulder_parts(i, thick=True); res = {}
        Pb = self.parts["bar"]; nb_ = len(Pb["X"])
        # bar samples off the J2 hub disc (the hub stack layers them there)
        Xb = sp["bar"]; j2 = self.k["j2"][i]; rel = Xb - self.O
        rad = np.linalg.norm(rel - (rel @ j2)[:, None] * j2, axis=1); offhub = rad > HUB_R + 3
        L1 = sp["link1"]; rl = L1 - self.O; radl = np.linalg.norm(rl - (rl @ j2)[:, None] * j2, axis=1)
        L1o = L1[radl > HUB_R + 3]
        if offhub.any() and len(L1o): res["link1-bar"] = float(cKDTree(L1o).query(Xb[offhub])[0].min()) - 1.5 + PART_CLEAR
        res["bar-hub1"] = float(sd_cyl(Xb, self.O + self.F1 * self.a1, self.a1, HUB_R, 0.0, CROWN).min())
        ap = self.arm_parts(i, half=False); arm = np.concatenate([ap["sleeve"], ap["ring"], ap["cheeks"]])
        sh = np.concatenate([sp["link1"], sp["hub1"], sp["hub2"], Xb])
        res["arm-shoulder"] = float(cKDTree(sh).query(arm)[0].min()) - 1.5 + PART_CLEAR
        cuff_side = np.concatenate([ap["sleeve"], ap["ring"]])
        res["cheeks-bar"] = float(cKDTree(np.concatenate([Xb, ap["boss"]])).query(ap["cheeks"])[0].min()) - 1.5 + PART_CLEAR
        kk = min(res, key=res.get); return res[kk], kk

    # ---- run -------------------------------------------------------------------------------------------------------
    def run(self):
        B = self.B; B.reset(); t0 = time.time(); n = len(B.idx)
        if self.dead:
            for i in range(n): B.record(i, None)
            r = B.report(); r["why"] = {}; return r
        self.fit()
        if self.dead:
            for i in range(n): B.record(i, None)
            r = B.report(); r["why"] = {kk: int((self.why == kk).sum()) for kk in ("sing", "U", "slide", "flip")}; return r
        self.clear = np.full(n, np.nan); self.cpair = [""] * n; self.parts_d = {}
        for i in range(n):
            if not self.kok[i]: B.record(i, None); continue
            cl, pr = self.collide(i); self.clear[i] = cl; self.cpair[i] = pr
            if cl < PART_CLEAR: self.why[i] = "parts"; B.record(i, None); continue
            sp = self.shoulder_parts(i); ap = self.arm_parts(i)
            names = list(sp) + list(ap); chunks = list(sp.values()) + list(ap.values())
            d = B.record(i, self.to_T(i, np.concatenate(chunks)))
            o = 0
            for nm, c in zip(names, chunks):
                self.parts_d.setdefault(nm, {})[i] = d[o:o + len(c)]; o += len(c)
            dc = float(B.dist(i, self.to_T(i, self.contact_extra(i))).min())
            if dc < 0: B.res[i] = np.r_[d, dc]; self.why[i] = "contact"
            elif float(d.min()) < 0: self.why[i] = "contact"
        r = B.report()
        r["why"] = {kk: int((self.why == kk).sum()) for kk in ("sing", "U", "slide", "flip", "parts", "contact")}
        r["geom"] = dict(F1=round(self.F1 - 0, 1), F2=round(self.F2, 1), lam=[round(self.lam_lo, 1), round(self.lam_hi, 1)],
                         beta_max=round(math.degrees(self.beta_max), 1), ring_ro=round(self.ring_ro, 1),
                         psi_ref=round(math.degrees(self.psi_ref), 1), C0=np.round(self.C0, 1).tolist(),
                         J3_range=self.range_deg("J3"), alpha=self.range_deg("alpha"), beta=self.range_deg("beta"))
        r["part_inband14"] = self.part_inband()
        r["t"] = round(time.time() - t0, 1)
        return r

    def range_deg(self, key):
        v = self.k[key][self.kok]
        if not len(v): return None
        if key == "J3": c = math.atan2(np.sin(v).mean(), np.cos(v).mean()); w = wrap(v - c); return [round(math.degrees(w.min() + c), 1), round(math.degrees(w.max() + c), 1)]
        return [round(math.degrees(v.min()), 1), round(math.degrees(v.max()), 1)]

    def part_inband(self):
        out = {}
        cl = [j for j, kk in enumerate(self.kind) if kk == "clip" and self.B.res[j] is not None and float(np.min(self.B.res[j])) >= 0]
        for nm, dd in self.parts_d.items():
            v = np.concatenate([dd[j] for j in cl if j in dd]) if any(j in dd for j in cl) else np.zeros(0)
            if len(v): out[nm] = dict(n=int(len(v) / max(1, len(cl))), inband14=round(float(np.mean((v >= 2) & (v <= 14))), 3),
                                      med=round(float(np.median(v)), 1), p90=round(float(np.percentile(v, 90)), 1))
        return out


# ---- public API (swarm convention) ------------------------------------------------------------------------------------
_MODELS = {}
def metal(pose, frames, params, B=None, i=None):
    """(k, 3) metal sample points (thorax frame) of bench pose i, or None when the mechanism cannot take it.
    The idealised model needs the whole bench (rigid heights are fitted over its poses), so B and i are required."""
    key = (id(B), json.dumps(params, sort_keys=True))
    if key not in _MODELS:
        M = Model(B, params); M.run(); _MODELS[key] = M
    M = _MODELS[key]
    if M.dead or not M.kok[i] or (M.clear[i] < PART_CLEAR): return None
    return M.to_T(i, M.scored(i))


def evaluate(B, params, log=None):
    M = Model(B, params); r = M.run(); return r, M


def kin_scan(B, params):
    """frames-only check: design window, coverage, why poses fail"""
    M = Model(B, params)
    if M.dead: return dict(dead=True)
    ok = M.classify()
    return dict(cover=round(M.design_cover, 3), lam=[round(M.lam_lo, 1), round(M.lam_hi, 1)], beta_max=round(math.degrees(M.beta_max), 1),
                ok_clip=round(float(ok[M.kind == "clip"].mean()), 3), ok_ws=round(float(ok[M.kind == "ws"].mean()), 3),
                why={kk: int((M.why == kk).sum()) for kk in ("sing", "U", "slide", "flip")},
                J1=M.range_deg("J1"), J2=M.range_deg("J2"), J3=M.range_deg("J3"), alpha=M.range_deg("alpha"), beta=M.range_deg("beta"),
                psi_ref=round(math.degrees(M.psi_ref), 1), C0=np.round(M.C0, 1).tolist())


# ---- sweep driver ----------------------------------------------------------------------------------------------------
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")


def log_entry(entries, k, params, r):
    entries.append(dict(k=k, t=now(), params=params, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                        follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r.get("why"), geom=r.get("geom")))
    tmp = SWEEP_JSON + ".tmp"; json.dump(entries, open(tmp, "w"), indent=1); os.replace(tmp, SWEEP_JSON)


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "check"
    nc = int(a[a.index("--n-clip") + 1]) if "--n-clip" in a else 60; nw = int(a[a.index("--n-ws") + 1]) if "--n-ws" in a else 160
    B = CB.Bench(nc, nw); print("bench", B.mode, len(B.idx), flush=True)
    if mode == "kin":
        print(json.dumps(kin_scan(B, {}), indent=1))
    elif mode == "check":
        r, M = evaluate(B, {}); print(json.dumps(r, indent=1, default=str))

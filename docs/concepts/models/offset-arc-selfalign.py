"""Concept model: SKIN-SHAPED OFFSET ARC + SELF-ALIGNING CUFF STAGE (non-spherical trombone), id offset-arc-selfalign.

Chain (docs/concepts/catalogue.json, entry offset-arc-selfalign; docs/concepts/offset-arc-selfalign.md):
  S (scapula handler) -> J1 thin-section ring about a line parallel to b (offset o1 from GH) -> L1 = the guide (box on
  the ring's upper race) -> J2 = an L2-fixed band bent to a CIRCLE ABOUT A LINE PARALLEL TO p2 (offset o2 from GH) that
  slides through the guide -> L2 = band + connector strap -> J3 O20 v5 hub about a line parallel to W (offset o3) ->
  E = hub lower plate on a passive 3-slide cuff stage (along the humerus / around it / normal) -> H (arm, cuff).
ACTIVE DOF 3 (J1, J2, J3), PASSIVE 3 (the stage). Orientations compose independently of where the axes sit, so every
member's orientation is the spherical chain's: R_L1 = rot(b, q1), R_L2 = R_L1 rot(p2_r, q2), R_H = R_L2 rot(W_r, q3)
(the arm fixes W, p2 follows from the two-circle closure on the design's branch). The axis offsets only translate the
chain end by t_E(pose) = (I - R_L1) o1 + R_L1 (I - R12) o2 + R_L2 (I - R23) o3; the three slides take it up
(s = R_H^T t_E - c in the stage frame, c = the stage's centring), so the slide values are fixed by closure too: no spare.

Parts at real size (mm; L1 keep-out level, docs/CAD_STANDARD.md L1):
  J1 ring   KAA15XL0-class thin-section ring in housings: flat annulus 19-26 mm from the J1 line, 6 mm axial (S / L1),
            underside at z1 (fitted: skin envelope + 2).
  guide     L1 keep-out box 30 (along the band) x 22 (across) x 10 (band underside - 3 .. + 7) at the band point nearest
            the J1 line; spec rule: guide underside >= ring top (z1 + 6) along the J1 axis.
  band      Ti 10 wide x 4 thick, a circle about the J2 line: x(phi) = o2 + (z_a + w) p2_r + (rho + t) u(phi); rho is
            fitted (lowest circle that clears the skin by 2 mm in every pose, the ring by 1 mm and satisfies the guide
            rule); the arc spans the guide azimuths of the fit clips (full rate) +- 12 deg (spec), optionally a quantile
            of the workspace azimuths (arc_ws).
  connector L2 strap 10 x 3 from the band end (phi_lo) to the J3 hub's upper member (F3 + 3.15); free underside: the
            straight ramp, raised where the skin (2 mm) or the stage boxes (1 mm) need it in any pose.
  J3 hub    O20 v5: r 10, lower plate F3 .. F3 + 3 (E), upper member from F3 + 3.15 (L2), crown F3 + 12.25.
  stage     two crossed miniature rolling guides (IKO LWL3 / THK RSR3 class, 4 mm assembly height each; the spec's 8 mm
            block) + a radial pin slide: arm-fixed rail 8 x (20 + 2 S_a) x 3 (H), along-carriage 20 x (20 + 2 S_t) x 2.5
            carrying the across rail (A), across-carriage 20 x 20 x 1.5 (C, 0.5 mm running gaps), radial travel gap
            R_r + s_r, then the hub's lower plate (a wedge when the stage plane is the arm's tangent plane, frame='arm').
            Underside of the stage (rail + carriage overhang) fitted to clear the arm skin by 2 mm in every pose.
Skin-facing undersides (ring, guide, band, connector, rail, carriage overhang) are sampled on a 2 mm grid (1 point /
4 mm2) and scored; side walls, tops, edges, the hub barrel and crown are checked for skin contact only.
A pose is TAKEN iff: the two-circle closure exists with sep in [|A1-A2| + 5, A1 + A2 - 5] deg (trombone spec); the
guide is >= 12 deg inside both band ends; every slide is inside its range; along each fit clip (tracked at the full
10 fps) no joint steps > 25 deg between consecutive frames (branch flip); non-adjacent parts stay >= 1 mm apart
(band / connector / hub vs ring and stage boxes; guide vs stage and hub; ring vs stage and hub); no metal inside the
body (else recorded as contact). Rigid heights are the p-th percentile (pct, default 100 = max) over the
kinematically valid bench poses - concept_baseline.py's convention: poses above it are recorded as contact.

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/offset-arc-selfalign.py [check|kin|sweep N|best]
"""
import json, math, os, sys, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
BP = CB.BP
ID = "offset-arc-selfalign"
D2R = math.pi / 180

# ---- hardware (docs/HARDWARE.md v5 joint; catalogue spec) -----------------------------------------------------------
HUB_R, CROWN, UP, LOWER_T = 10.0, 12.25, 3.15, 3.0
RING_RI, RING_RO, RING_H = 19.0, 26.0, 6.0
GUIDE_L, GUIDE_W, GUIDE_DN, GUIDE_UP = 30.0, 22.0, 3.0, 7.0
BAND_W, BAND_T = 10.0, 4.0
CONN_W, CONN_T = 10.0, 3.0
RAIL_W, RAIL_H, CAR_L, CARA_H, CARC_H, RUN = 8.0, 3.0, 20.0, 2.5, 1.5, 0.5
STACK = RAIL_H + RUN + CARA_H + RUN + CARC_H                  # 8.0 mm: rail underside -> across-carriage top
CLEAR, PART_CLEAR, SP = 2.0, 1.0, 2.0
SING, JUMP, GMARG = 5.0, 25.0, 12.0

PARAMS = dict(az=32.55, el=80.56, wd=71.38, wa=4.78, A1=77.41, A2=81.45, branch=-1,   # champion axes (spec)
              o1m=0.0, o1t=0.0,          # J1 line offset (mm): toward p2 (perp. to b) / across
              o2w=0.0, o2n=0.0,          # J2 line offset (mm): toward W's azimuth about p2 / normal to it
              o3a=0.0, o3t=0.0,          # J3 line offset (mm): along the humerus (perp. to W) / around the arm
              dza=0.0,                   # arc circle shift along the J2 line (mm) from the spherical polar angle A1 at 58 mm
              S_a=20.0, S_t=15.0, R_r=4.0,   # slide half-ranges (spec 15-25 / 10-20 / 3-5)
              frame="arm",               # stage plane: 'arm' (tangent to the arm, wedge under the hub) or 'hub' (perp. to W)
              arc_ws=0.0,                # arc also covers this central share of the workspace guide azimuths (0 = fit clips)
              pct=100.0,                 # percentile of the per-pose needs for rigid heights
              comp=0,                    # 1: J1 / J3 offsets chosen by the minimax LP (radial slide half-range), see Model.compensate
              stage=1)                   # 0: no stage (spherical trombone reference: hub lower plate fixed to the arm)
SWEEP = dict(o2w=[-15, -10, -5, 0, 5, 10, 15], o2n=[-15, -10, -5, 0, 5, 10, 15], o1m=[-10, -5, 0, 5, 10], o1t=[-10, -5, 0, 5, 10],
             o3a=[-12, -6, 0, 6, 12], o3t=[-12, -6, 0, 6, 12], dza=[-8, -4, 0, 4, 8], S_a=[15, 20, 25], S_t=[10, 15, 20],
             R_r=[3, 4, 5], frame=["arm", "hub"], arc_ws=[0, 0.5, 0.8, 0.9], pct=[98, 99, 100])


# ---- small geometry ----------------------------------------------------------------------------------------------
def unit(x): x = np.asarray(x, float); return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def wdir(d, az): return np.array([math.sin(d * D2R) * math.sin(az * D2R), -math.cos(d * D2R), math.sin(d * D2R) * math.cos(az * D2R)])
def mv(A, x): return np.einsum("nij,nj->ni", A, x)


def circ_int(c1, r1, c2, r2, sign):
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n, h2 > 0


def Fr(u, v):
    u = unit(u); w = unit(v - (v * u).sum(-1, keepdims=True) * u); return np.stack([u, w, np.cross(u, w)], -1)


def ang_about(R, u):
    """rotation angle of R (n,3,3) about unit axis u (3,)"""
    a = unit(np.cross(u, [0.31, 0.53, 0.79])); Ra = mv(R, np.broadcast_to(a, (len(R), 3)))
    return np.arctan2(np.cross(a, Ra) @ u, Ra @ a)


def perp(u):
    a = unit(np.cross(u, [0.0, 0.0, 1.0]) if abs(u[2]) < 0.9 else np.cross(u, [1.0, 0.0, 0.0])); return a, np.cross(u, a)


def grid2(L, W, sp=SP):
    a = np.arange(-L / 2 + sp / 2, L / 2 - 1e-9, sp); b = np.arange(-W / 2 + sp / 2, W / 2 - 1e-9, sp)
    X, Y = np.meshgrid(a, b, indexing="ij"); return np.stack([X.ravel(), Y.ravel()], 1)


def sd_box(P, cen, M, half):
    """signed distance of P (k,3) to a box (centre, columns M = its axes, half sizes)"""
    q = np.abs((P - cen) @ M) - half
    return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(1), 0)


def sd_annulus(P, o, ax, ri, ro, z0, z1):
    w = P - o; z = w @ ax; r = np.linalg.norm(w - z[:, None] * ax, axis=1)
    qr = np.maximum(ri - r, r - ro); qz = np.maximum(z0 - z, z - z1)
    return np.where((qr > 0) | (qz > 0), np.hypot(np.maximum(qr, 0), np.maximum(qz, 0)), np.maximum(qr, qz))


def sd_cyl(P, c0, ax, r, h):
    w = P - c0; z = w @ ax; rr = np.linalg.norm(w - z[:, None] * ax, axis=1)
    dr = rr - r; dz = np.maximum(-z, z - h)
    return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))


def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- kinematics ----------------------------------------------------------------------------------------------------
class Kin:
    """axis directions, offsets, member rotations / translations for a batch of arm rotations HG (scapula frame)"""
    def __init__(self, p, HG_ref):
        self.p = p
        self.b = unit(bvec(p["az"], p["el"])); self.W0 = unit(wdir(p["wd"], p["wa"]))
        self.A1, self.A2 = p["A1"] * D2R, p["A2"] * D2R
        self.HG_r = HG_ref
        self.W_r = HG_ref @ self.W0
        p2r, ok = circ_int(self.b[None], self.A1, self.W_r[None], self.A2, float(p["branch"])); self.p2_r = unit(p2r[0])
        b, p2, Wr = self.b, self.p2_r, self.W_r
        self.m1 = unit(p2 - (p2 @ b) * b); self.t1 = np.cross(b, self.m1)
        self.e2 = unit(Wr - (Wr @ p2) * p2); self.e3 = np.cross(p2, self.e2)
        hum = HG_ref @ np.array([0.0, -1.0, 0.0]); self.hum_r = hum
        self.al3 = unit(hum - (hum @ Wr) * Wr); self.tg3 = np.cross(Wr, self.al3)
        self.o1 = p["o1m"] * self.m1 + p["o1t"] * self.t1
        self.o2 = p["o2w"] * self.e2 + p["o2n"] * self.e3
        self.o3 = p["o3a"] * self.al3 + p["o3t"] * self.tg3
        if p.get("frame", "arm") == "hub":
            n = Wr; al = self.al3
        else:
            n = unit(Wr - (Wr @ hum) * hum); al = hum
        self.sn, self.sa = n, al; self.st = np.cross(n, al); self.tilt = math.acos(float(np.clip(Wr @ n, -1, 1)))
        self.Qs = np.stack([self.sa, self.st, self.sn], 1)       # stage axes (columns): along, tangential, normal

    def solve(self, HG):
        b = self.b; n = len(HG); W = HG @ self.W0; p1 = np.broadcast_to(b, W.shape)
        p2, ok = circ_int(p1, self.A1, W, self.A2, float(self.p["branch"]))
        sep = np.degrees(np.arccos(np.clip(W @ b, -1, 1)))
        a1, a2 = self.p["A1"], self.p["A2"]
        ok = ok & (sep >= abs(a1 - a2) + SING) & (sep <= min(a1 + a2, 360 - a1 - a2) - SING)
        F1 = Fr(p1, p2); F2 = Fr(p2, W)
        F1r = Fr(b, self.p2_r); F2r = Fr(self.p2_r, self.W_r)
        RL1 = F1 @ F1r.T; RL2 = F2 @ F2r.T; RH = HG @ self.HG_r.T
        R12 = np.einsum("nji,njk->nik", RL1, RL2); R23 = np.einsum("nji,njk->nik", RL2, RH)
        q = np.stack([ang_about(RL1, b), ang_about(R12, self.p2_r), ang_about(R23, self.W_r)], 1)
        I = np.eye(3)
        t1 = (I - RL1) @ self.o1
        t2 = t1 + mv(RL1, (I - R12) @ self.o2)
        tE = t2 + mv(RL2, (I - R23) @ self.o3)
        dH = np.einsum("nji,nj->ni", RH, tE)                     # E displacement on the arm (humerus reference frame)
        return dict(ok=ok, sep=sep, RL1=RL1, RL2=RL2, RH=RH, t1=t1, t2=t2, tE=tE, q=q, s_raw=dH @ self.Qs)


# ---- the model -----------------------------------------------------------------------------------------------------
class Model:
    def __init__(self, B, params=None, verbose=False):
        P = dict(PARAMS); P.update(params or {}); self.p = P; self.B = B; self.v = verbose
        Z = CB._poses_all(); self.Z = Z
        self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.kind = np.array(B.kind); n = len(B.idx)
        names = list(Z["NAMES"]); cid = Z["CID"]
        self.ref = int(np.nonzero(np.isin(cid, [names.index(x) for x in CB.FIT]))[0][0])   # reference = the first fit-clip frame
        self.clip_ii = {}
        for nm in CB.FIT:                                         # full-rate fit clips: continuity + the arc's azimuth range
            ii = np.nonzero(cid == names.index(nm))[0]; self.clip_ii[nm] = ii[np.argsort(Z["FI"][ii], kind="stable")]
        self.ws_ii = np.nonzero(cid == names.index("Workspace (envelope)"))[0]
        self.why = np.array([""] * n, dtype=object)
        self._solve_all()
        if P.get("comp", 0) and P["stage"]: self.compensate()

    def _solve_all(self):
        Z = self.Z; self.K = Kin(self.p, Z["HG"][self.ref].astype(float))
        self.k = self.K.solve(self.HG)
        self.full = {nm: (ii, self.K.solve(Z["HG"][ii].astype(float))) for nm, ii in self.clip_ii.items()}
        self.kws = self.K.solve(Z["HG"][self.ws_ii].astype(float))

    def compensate(self):
        """minimax LP (the P0 offset-axis LP idea, pipeline/girdle/girdle.py): for the given J2 offset choose the J1 / J3
        offsets (o1m, o1t, o3a, o3t; |component| <= 8.5 so |offset| <= 12 mm) that minimise the radial slide half-range,
        with the along / tangential half-ranges <= S_a / S_t, over the full-rate fit clips + the workspace poses the
        chain takes (closure + guide on the arc). Training poses only; the slides then centre on the same poses."""
        from scipy.optimize import linprog
        P = self.p; free = ["o1m", "o1t", "o3a", "o3t"]
        for k_ in free: P[k_] = 0.0
        self._solve_all(); self.design_kin()
        def sel(k): o, g, _ = self.kin_ok(k); return o & g
        ks = [k for _, k in self.full.values()] + [self.kws]; masks = [sel(k) for k in ks]
        s0 = np.concatenate([k["s_raw"][m] for k, m in zip(ks, masks)])
        F = []
        for v in free:
            q = dict(P); q[v] = 1.0; Kv = Kin(q, self.Z["HG"][self.ref].astype(float)); Kv.o2 = np.zeros(3)
            Kv.o1 = q["o1m"] * Kv.m1 + q["o1t"] * Kv.t1 - (P["o1m"] * Kv.m1 + P["o1t"] * Kv.t1)
            Kv.o3 = q["o3a"] * Kv.al3 + q["o3t"] * Kv.tg3 - (P["o3a"] * Kv.al3 + P["o3t"] * Kv.tg3)
            kk = [Kv.solve(self.Z["HG"][ii].astype(float)) for ii in self.clip_ii.values()] + [Kv.solve(self.Z["HG"][self.ws_ii].astype(float))]
            F.append(np.concatenate([k["s_raw"][m] for k, m in zip(kk, masks)]))
        F = np.stack(F, -1); Pn = len(s0); nv = len(free); nx = nv + 4
        A = []; bb = []
        for comp, lim in ((0, P["S_a"]), (1, P["S_t"])):
            a = np.zeros((Pn, nx)); a[:, :nv] = F[:, comp]; a[:, nv + comp] = -1
            A += [a, -a]; bb += [lim - s0[:, comp], lim + s0[:, comp]]
        a = np.zeros((Pn, nx)); a[:, :nv] = F[:, 2]; a[:, nv + 2] = -1; a[:, -1] = -1
        a2 = -a; a2[:, -1] = -1; A += [a, a2]; bb += [-s0[:, 2], s0[:, 2]]
        cvec = np.zeros(nx); cvec[-1] = 1
        r = linprog(cvec, A_ub=np.concatenate(A), b_ub=np.concatenate(bb), bounds=[(-8.5, 8.5)] * nv + [(None, None)] * 3 + [(0, None)], method="highs")
        if r.success:
            for k_, x in zip(free, r.x[:nv]): P[k_] = round(float(x), 2)
            self.comp_h = round(float(r.x[-1]), 2)
        else: self.comp_h = None
        self._solve_all()

    # ---- design: arc range, slide centring --------------------------------------------------------------------------
    def phi_g(self, q2):
        return self.phiG - q2

    def design_kin(self):
        K, P = self.K, self.p
        za0 = 58.0 * math.cos(K.A1) + P["dza"]; self.za = za0
        g0 = K.o1 + 58.0 * K.b - K.o2                             # azimuth (about the J2 line) of the J1 line at 58 mm
        self.phiG = math.atan2(g0 @ K.e3, g0 @ K.e2)
        ph = np.concatenate([self.phi_g(k["q"][k["ok"], 1]) for _, k in self.full.values()])
        lo, hi = ph.min(), ph.max()
        if P["arc_ws"] > 0:
            pw = self.phi_g(self.kws["q"][self.kws["ok"], 1]); qq = P["arc_ws"]
            lo = min(lo, np.quantile(pw, (1 - qq) / 2)); hi = max(hi, np.quantile(pw, (1 + qq) / 2))
        self.phi_lo, self.phi_hi = lo - GMARG * D2R, hi + GMARG * D2R
        # slide centring over the kinematically valid bench + full-rate clip poses
        S = [self.k["s_raw"][self.k["ok"]]] + [k["s_raw"][k["ok"]] for _, k in self.full.values()]
        S = np.concatenate(S); self.c = 0.5 * (S.max(0) + S.min(0)) if P["stage"] else np.zeros(3)
        if not P["stage"]: self.c = np.zeros(3)

    def kin_ok(self, k):
        P = self.p; ok = k["ok"].copy()
        ph = self.phi_g(k["q"][:, 1]); gok = (ph >= self.phi_lo + GMARG * D2R - 1e-9) & (ph <= self.phi_hi - GMARG * D2R + 1e-9)
        s = k["s_raw"] - self.c
        if P["stage"]: sok = (np.abs(s[:, 0]) <= P["S_a"]) & (np.abs(s[:, 1]) <= P["S_t"]) & (np.abs(s[:, 2]) <= P["R_r"])
        else: sok = np.abs(k["s_raw"]).max(1) <= 0.5               # no stage: the chain must close exactly (offsets 0)
        return ok, gok, sok

    def classify(self):
        ok, gok, sok = self.kin_ok(self.k); n = len(ok)
        self.why[:] = ""; self.why[~ok] = "fold"; self.why[ok & ~gok] = "guide"; self.why[ok & gok & ~sok] = "slide"
        good = ok & gok & sok
        # continuity at full rate
        flip_at = {}
        for nm, (ii, k) in self.full.items():
            o, g, s = self.kin_ok(k); okf = o & g & s; prev = None
            for j, gi in enumerate(ii):
                f = False
                if okf[j] and prev is not None:
                    dq = np.degrees(np.abs((k["q"][j] - k["q"][prev] + np.pi) % (2 * np.pi) - np.pi))
                    f = dq.max() > JUMP
                flip_at[int(gi)] = f; prev = j if okf[j] else None
        flip = np.array([flip_at.get(int(gi), False) for gi in self.B.idx]) & (self.kind == "clip")
        self.why[good & flip] = "flip"; good &= ~flip
        self.kok = good
        return good

    # ---- member transforms -------------------------------------------------------------------------------------------
    def T(self, m, i):
        k = self.k
        if m == "S": return np.eye(3), np.zeros(3)
        if m == "L1": return k["RL1"][i], k["t1"][i]
        if m == "L2": return k["RL2"][i], k["t2"][i]
        if m == "E": return k["RH"][i], k["tE"][i]
        RH = k["RH"][i]; s = k["s_raw"][i] - self.c; K = self.K
        if not self.p["stage"]: return RH, np.zeros(3)
        if m == "H": return RH, np.zeros(3)
        if m == "A": return RH, RH @ (s[0] * K.sa)
        if m == "C": return RH, RH @ (s[0] * K.sa + s[1] * K.st)
        raise ValueError(m)

    def to_S(self, m, i, X):
        R, t = self.T(m, i); return X @ R.T + t

    def to_T(self, m, i, X):
        return self.to_S(m, i, X) @ self.RS[i].T

    # ---- sphere tracing: per-pose heights along fixed directions -----------------------------------------------------
    def trace(self, items, poses, iters=24, h0=None):
        """items: list of (member, base X (m,3), dir N (m,3), start h (m,), avoid-fn or None). Returns per item an array
        (len(poses), m): the height h along N (from X) at which X + h N sits CLEAR mm off the skin (and PART_CLEAR off
        whatever the avoid-fn measures, an SDF of S-frame points) in that pose."""
        sizes = [len(it[1]) for it in items]; cut = np.cumsum([0] + sizes)
        out = np.zeros((len(poses), cut[-1]))
        for a, i in enumerate(poses):
            H = np.concatenate([np.asarray(it[3], float) * np.ones(len(it[1])) for it in items])
            Hp = dp = None
            for _ in range(iters):
                PS = [self.to_S(m, i, X + H[cut[k]:cut[k + 1], None] * N) for k, (m, X, N, *_r) in enumerate(items)]
                d = self.B.dist(i, np.concatenate(PS) @ self.RS[i].T) - CLEAR
                for k, it in enumerate(items):
                    if len(it) > 4 and it[4] is not None:
                        d[cut[k]:cut[k + 1]] = np.minimum(d[cut[k]:cut[k + 1]], it[4](i, PS[k]) - PART_CLEAR)
                if np.abs(d).max() < 0.05: break
                # sphere-tracing step (1-Lipschitz distance) accelerated by a clamped secant slope
                g = np.ones_like(d) if Hp is None else np.clip((dp - d) / np.where(np.abs(Hp - H) > 1e-6, Hp - H, 1e-6), 0.3, 1.0)
                if Hp is not None: g = np.where((np.abs(d) > 25) | (np.abs(dp) > 25), 1.0, g)     # clamped far field: plain step
                Hp, dp = H.copy(), d
                H = H - d / g
            out[a] = H
        return [out[:, cut[k]:cut[k + 1]] for k in range(len(items))]

    def rigid(self, items, poses, h0, iters=16):
        """one shared height for a rigid group: items = list of (member, base X (m,3), dir N (m,3)); per pose the lowest
        h at which every X + h N sits >= CLEAR off the skin (scalar sphere tracing: all samples move by |dh| along unit
        directions, so stepping by the smallest clearance never crosses a level; clamped secant acceleration)"""
        out = np.zeros(len(poses)); h_start = h0
        for a, i in enumerate(poses):
            h = h_start; hp = mp = None
            for _ in range(iters):
                PS = np.concatenate([self.to_S(m, i, X + h * N) for m, X, N in items])
                m_ = float((self.B.dist(i, PS @ self.RS[i].T) - CLEAR).min())
                if abs(m_) < 0.05: break
                g = 1.0
                if hp is not None and abs(hp - h) > 1e-6 and abs(m_) < 25 and abs(mp) < 25: g = min(1.0, max(0.3, (mp - m_) / (hp - h)))
                hp, mp = h, m_; h = h - m_ / g
            out[a] = h; h_start = h + 4.0
        return out

    def red(self, A, axis=0):
        """rigid height from per-pose needs: the pct-th percentile over poses"""
        return np.percentile(A, self.p["pct"], axis=axis) if self.p["pct"] < 100 else A.max(axis)

    # ---- fit -----------------------------------------------------------------------------------------------------------
    def fit(self):
        K, P = self.K, self.p; t0 = time.time()
        self.design_kin(); good = self.classify(); poses = np.nonzero(good)[0]; self.poses_fit = poses
        if len(poses) < 3: self.dead = True; return
        self.dead = False
        b = K.b; e, f = perp(b)
        # 1. J1 ring (S): flat annulus perpendicular to b, underside at z1 along b
        g = grid2(2 * RING_RO, 2 * RING_RO); rr = np.linalg.norm(g, axis=1); g = g[(rr >= RING_RI) & (rr <= RING_RO)]
        Xr = K.o1 + g[:, :1] * e + g[:, 1:] * f
        self.need_ring = self.rigid([("S", Xr, np.broadcast_to(b, Xr.shape))], poses, 60.0)
        self.z1 = float(self.red(self.need_ring))
        self.ring = Xr + self.z1 * b
        # 2. band + guide (rigid circle radius rho about the J2 line)
        p2 = K.p2_r; za = self.za
        nphi = max(8, int((self.phi_hi - self.phi_lo) * 58.0 / SP) + 1)
        phis = np.linspace(self.phi_lo, self.phi_hi, nphi); ws = np.arange(-BAND_W / 2 + SP / 2, BAND_W / 2, SP)
        PH, WW = np.meshgrid(phis, ws, indexing="ij"); PH = PH.ravel(); WW = WW.ravel()
        U = np.cos(PH)[:, None] * K.e2 + np.sin(PH)[:, None] * K.e3
        Xb = K.o2 + (za + WW)[:, None] * p2; self.band_phi, self.band_w, self.band_U = PH, WW, U
        uG = math.cos(self.phiG) * K.e2 + math.sin(self.phiG) * K.e3; tG = -math.sin(self.phiG) * K.e2 + math.cos(self.phiG) * K.e3
        self.uG, self.tG = uG, tG
        gg = grid2(GUIDE_L, GUIDE_W)
        Xg = K.o2 + za * p2 + gg[:, 1:] * p2 + gg[:, :1] * tG - GUIDE_DN * uG
        self.need_band = self.rigid([("L2", Xb, U), ("L1", Xg, np.broadcast_to(uG, Xg.shape))], poses, 60.0)
        rho = float(self.red(self.need_band))
        # guide rule: guide underside >= ring top along the J1 axis (pose independent: L1 turns about the J1 line)
        bu = float(uG @ b)
        if bu > 0.2: rho = max(rho, float(((self.z1 + RING_H - (Xg @ b)) / bu).max()))
        # band over the ring (non-adjacent L2 / S): >= PART_CLEAR over the annulus in every fitted pose
        for _ in range(3):
            worst = 0.0
            for i in poses:
                Y = self.to_S("L2", i, Xb + rho * U); w = Y - K.o1; z = w @ b; r = np.linalg.norm(w - z[:, None] * b, axis=1)
                over = (r >= RING_RI - PART_CLEAR - BAND_W / 2) & (r <= RING_RO + PART_CLEAR + BAND_W / 2)
                if not over.any(): continue
                kz = (self.k["RL2"][i] @ U[over].T).T @ b
                dz = (self.z1 + RING_H + PART_CLEAR) - z[over]
                worst = max(worst, float((dz / np.maximum(kz, 0.2)).max()))
            if worst <= 0.05: break
            rho += worst
        self.rho = rho
        self.band = Xb + rho * U; self.guide = Xg + rho * uG
        self.guide_c = K.o2 + za * p2 + rho * uG                  # band underside centre at the guide
        # 3. stage (H rail, A carriage overhang) and hub height
        if P["stage"]:
            self.fit_stage(poses)
        else:
            self.fit_nostage(poses)
        # 4. connector (L2) from the band end to the hub
        self.fit_connector(poses)
        self.t_fit = time.time() - t0

    def stage_frame(self, lam):
        """hub point P3 on the J3 line and the stage footprint centre for a rail-underside level lam (n-coordinate)"""
        K, P = self.K, self.p; n = K.sn; W = K.W_r
        target = lam + STACK + P["R_r"] - self.c[2] + HUB_R * math.sin(K.tilt)      # P3 . n
        f3 = (target - K.o3 @ n) / float(W @ n); P3 = K.o3 + f3 * W
        Os = P3 - (P3 @ n) * n + self.c[0] * K.sa + self.c[1] * K.st
        return f3, P3, Os

    def stage_parts(self, lam):
        """boxes (member, centre, half) in humerus reference coordinates, stage axes K.Qs"""
        P = self.p; K = self.K; f3, P3, Os = self.stage_frame(lam); n = K.sn
        La = CAR_L + 2 * P["S_a"]; Wt = CAR_L + 2 * P["S_t"]
        z = lam
        bx = {"H": (Os + (z + RAIL_H / 2) * n, np.array([La / 2, RAIL_W / 2, RAIL_H / 2]))}
        z += RAIL_H + RUN; bx["A"] = (Os + (z + CARA_H / 2) * n, np.array([CAR_L / 2, Wt / 2, CARA_H / 2]))
        z += CARA_H + RUN; bx["C"] = (Os + (z + CARC_H / 2) * n, np.array([CAR_L / 2, CAR_L / 2, CARC_H / 2]))
        return bx

    def fit_stage(self, poses):
        K, P = self.K, self.p; n = K.sn
        La = CAR_L + 2 * P["S_a"]; Wt = CAR_L + 2 * P["S_t"]
        lam = 60.0
        for it in range(3):
            f3, P3, Os = self.stage_frame(lam)
            gr = grid2(La, RAIL_W); Xh = Os + gr[:, :1] * K.sa + gr[:, 1:] * K.st
            ga = grid2(CAR_L, Wt); ga = ga[np.abs(ga[:, 1]) > RAIL_W / 2]; Xa = Os + ga[:, :1] * K.sa + ga[:, 1:] * K.st + (RAIL_H + RUN) * n
            self.need_stage = self.rigid([("H", Xh - (Os @ n) * n, np.broadcast_to(n, Xh.shape)), ("A", Xa - (Os @ n) * n, np.broadcast_to(n, Xa.shape))], poses, lam)
            new = float(self.red(self.need_stage))
            if abs(new - lam) < 0.5: lam = new; break
            lam = new
        self.lam = lam; f3, P3, Os = self.stage_frame(lam); self.f3, self.P3 = f3, P3
        gr = grid2(La, RAIL_W); self.rail = Os - (Os @ n) * n + lam * n + gr[:, :1] * K.sa + gr[:, 1:] * K.st
        ga = grid2(CAR_L, Wt); ga = ga[np.abs(ga[:, 1]) > RAIL_W / 2]
        self.carA = Os - (Os @ n) * n + (lam + RAIL_H + RUN) * n + ga[:, :1] * K.sa + ga[:, 1:] * K.st
        self.boxes = self.stage_parts(lam)

    def fit_nostage(self, poses):
        """reference: the hub's lower plate fixed to the arm (BOTTOM stub: 14 x 6 strap 40 mm down the arm)"""
        K = self.K; W = K.W_r; e, f = perp(W)
        d = grid2(2 * HUB_R, 2 * HUB_R); d = d[np.linalg.norm(d, axis=1) <= HUB_R]
        Xd = K.o3 + d[:, :1] * e + d[:, 1:] * f
        st = grid2(40.0, 14.0); st[:, 0] += HUB_R + 20.0
        Xs = K.o3 + st[:, :1] * K.al3 + st[:, 1:] * K.tg3
        self.need_stage = self.rigid([("H", Xd, np.broadcast_to(W, Xd.shape)), ("H", Xs, np.broadcast_to(W, Xs.shape))], poses, 60.0)
        f3 = float(self.red(self.need_stage))
        self.f3 = f3; self.P3 = K.o3 + f3 * W; self.rail = Xd + f3 * W; self.carA = Xs + f3 * W; self.boxes = {}
        self.lam = f3

    def box_sdf_fn(self, names):
        K = self.K
        def fn(i, PS):
            d = np.full(len(PS), 1e9)
            for nm in names:
                if nm not in self.boxes: continue
                cen, half = self.boxes[nm]; R, t = self.T(nm, i)
                d = np.minimum(d, sd_box(PS, R @ cen + t, R @ K.Qs, half))
            return d
        return fn

    def fit_connector(self, poses):
        K = self.K; W = K.W_r; p2 = K.p2_r
        Pa = K.o2 + self.za * p2 + self.rho * (math.cos(self.phi_lo) * K.e2 + math.sin(self.phi_lo) * K.e3)   # band end (underside)
        Hc = self.P3 + UP * W                                     # hub upper member underside, on the J3 line
        v = Pa - Hc; v_perp = unit(v - (v @ W) * W)
        Ph = Hc + HUB_R * v_perp                                  # leave the hub at its rim, toward the band end
        L = float(np.linalg.norm(Pa - Ph)); ns = max(3, int(L / SP) + 1)
        ts = (np.arange(ns) + 0.5) / ns
        axis = unit(Pa - Ph); side = unit(np.cross(axis, unit(0.5 * (Pa + Ph))))
        cw = np.arange(-CONN_W / 2 + SP / 2, CONN_W / 2, SP)
        T_, C_ = np.meshgrid(ts, cw, indexing="ij"); T_ = T_.ravel(); C_ = C_.ravel()
        base = Ph[None] + T_[:, None] * (Pa - Ph)[None] + C_[:, None] * side[None]
        nrm = unit(np.cross(side, axis)); nrm = nrm if nrm @ (0.5 * (Pa + Ph)) > 0 else -nrm
        N = np.broadcast_to(nrm, base.shape)
        avoid = self.box_sdf_fn(["H", "A", "C"]) if self.boxes else None
        (Hn,) = self.trace([("L2", base - 20.0 * N, N, 40.0, avoid)], poses)
        need = self.red(Hn, axis=0) - 20.0                       # per sample: lift above the straight ramp (>= 0 kept)
        self.conn = base + np.maximum(need, 0.0)[:, None] * N
        self.conn_n = nrm; self.conn_lift = float(np.maximum(need, 0).max())

    # ---- geometry for scoring / contact / collision ------------------------------------------------------------------
    def scored(self, i):
        parts = [("S", self.ring), ("L1", self.guide), ("L2", self.band), ("L2", self.conn), ("H", self.rail), ("A", self.carA)]
        return np.concatenate([self.to_T(m, i, X) for m, X in parts])

    def contact_only(self):
        """side walls / tops / edges / hub barrel and crown (member, points) - built once"""
        K = self.K; out = []; b = K.b; e, f = perp(b)
        ang = np.linspace(0, 2 * np.pi, 48, endpoint=False)
        for z in (self.z1 + 0.5, self.z1 + RING_H):                 # ring outer wall
            out.append(("S", K.o1 + z * b + RING_RO * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)))
        g = grid2(GUIDE_L, GUIDE_W, 4.0)                             # guide top + side walls
        top = self.guide_c + g[:, :1] * K.tG + g[:, 1:] * K.p2_r + GUIDE_UP * K.uG; out.append(("L1", top))
        for s in (-1, 1):
            for z in np.linspace(-GUIDE_DN, GUIDE_UP, 4):
                out.append(("L1", self.guide_c + s * GUIDE_L / 2 * K.tG + np.linspace(-GUIDE_W / 2, GUIDE_W / 2, 6)[:, None] * K.p2_r + z * K.uG))
                out.append(("L1", self.guide_c + s * GUIDE_W / 2 * K.p2_r + np.linspace(-GUIDE_L / 2, GUIDE_L / 2, 8)[:, None] * K.tG + z * K.uG))
        Ub = self.band_U[::2]; Xb = self.band[::2]                   # band top and edges
        out.append(("L2", Xb + BAND_T * Ub))
        W = K.W_r; e3, f3_ = perp(W)                                 # hub barrel + crown (L2), lower plate (E)
        for z in np.linspace(UP, CROWN, 4):
            out.append(("L2", self.P3 + z * W + HUB_R * (np.cos(ang)[:, None] * e3 + np.sin(ang)[:, None] * f3_)))
        dd = grid2(2 * HUB_R, 2 * HUB_R, 4.0); dd = dd[np.linalg.norm(dd, axis=1) <= HUB_R]
        out.append(("L2", self.P3 + CROWN * W + dd[:, :1] * e3 + dd[:, 1:] * f3_))
        out.append(("E", self.P3 + 0.5 * W + HUB_R * (np.cos(ang)[:, None] * e3 + np.sin(ang)[:, None] * f3_)))
        out.append(("L2", self.conn + CONN_T * self.conn_n))
        for nm, (cen, half) in self.boxes.items():                    # stage box side walls (edges)
            pts = []
            for z in (-half[2], half[2]):
                for x in np.arange(-half[0], half[0] + 1e-6, SP): pts += [(x, -half[1], z), (x, half[1], z)]
                for y in np.arange(-half[1], half[1] + 1e-6, SP): pts += [(-half[0], y, z), (half[0], y, z)]
            out.append((nm, cen + np.array(pts) @ K.Qs.T))
        return out

    def collide(self, i):
        """min clearance (mm) between non-adjacent parts at pose i and the pair that sets it"""
        K = self.K; res = {}
        L2pts = np.concatenate([self.to_S("L2", i, X) for X in (self.band[::2], self.band[::2] + BAND_T * self.band_U[::2], self.conn[::2],
                                                                 self.conn[::2] + CONN_T * self.conn_n)])
        res["L2-ring"] = float(sd_annulus(L2pts, K.o1, K.b, RING_RI, RING_RO, self.z1, self.z1 + RING_H).min())
        hubL2 = self.to_S("L2", i, self.hub_surf); hubE = self.to_S("E", i, self.hub_surf_E)
        guide = self.to_S("L1", i, self.guide_surf); ring = self.ring_surf
        R2, t2 = self.T("L2", i); RE, tE = self.T("E", i)
        c_l2 = (R2 @ (self.P3 + UP * K.W_r) + t2, R2 @ K.W_r, HUB_R, CROWN - UP)
        c_e = (RE @ self.P3 + tE, RE @ K.W_r, HUB_R, LOWER_T)
        for nm, (cen, half) in self.boxes.items():
            R, t = self.T(nm, i); C = R @ cen + t; M = R @ K.Qs
            if nm != "C": res[f"L2-{nm}"] = float(sd_box(np.concatenate([L2pts, hubL2]), C, M, half).min())
            else: res["L2-C"] = float(sd_box(L2pts, C, M, half).min())
            res[f"guide-{nm}"] = float(sd_box(guide, C, M, half).min())
            res[f"ring-{nm}"] = float(sd_box(ring, C, M, half).min())
            if nm in ("H", "A"): res[f"E-{nm}"] = float(sd_box(hubE, C, M, half).min())
        res["guide-hub"] = float(min(sd_cyl(guide, *c_l2).min(), sd_cyl(guide, *c_e).min()))
        res["ring-hub"] = float(min(sd_cyl(ring, *c_l2).min(), sd_cyl(ring, *c_e).min()))
        k = min(res, key=res.get); return res[k], k

    def surfaces(self):
        K = self.K; W = K.W_r; e3, f3_ = perp(W); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        ring = [self.P3 + z * W + HUB_R * (np.cos(ang)[:, None] * e3 + np.sin(ang)[:, None] * f3_) for z in np.linspace(UP, CROWN, 4)]
        dd = grid2(2 * HUB_R, 2 * HUB_R, 4.0); dd = dd[np.linalg.norm(dd, axis=1) <= HUB_R]
        self.hub_surf = np.concatenate(ring + [self.P3 + CROWN * W + dd[:, :1] * e3 + dd[:, 1:] * f3_, self.P3 + UP * W + dd[:, :1] * e3 + dd[:, 1:] * f3_])
        self.hub_surf_E = np.concatenate([self.P3 + z * W + HUB_R * (np.cos(ang)[:, None] * e3 + np.sin(ang)[:, None] * f3_) for z in (0.0, LOWER_T)]
                                         + [self.P3 + dd[:, :1] * e3 + dd[:, 1:] * f3_])
        g = grid2(GUIDE_L, GUIDE_W, 4.0); gs = []
        for z in (-GUIDE_DN, GUIDE_UP): gs.append(self.guide_c + g[:, :1] * K.tG + g[:, 1:] * K.p2_r + z * K.uG)
        self.guide_surf = np.concatenate(gs)
        b = K.b; e, f = perp(b); ang2 = np.linspace(0, 2 * np.pi, 40, endpoint=False)
        self.ring_surf = np.concatenate([K.o1 + z * b + r * (np.cos(ang2)[:, None] * e + np.sin(ang2)[:, None] * f)
                                         for z in (self.z1, self.z1 + RING_H) for r in (RING_RI, RING_RO)])

    # ---- run -----------------------------------------------------------------------------------------------------------
    def run(self):
        B = self.B; B.reset(); t0 = time.time(); self.fit(); n = len(B.idx)
        if self.dead:
            for i in range(n): B.record(i, None)
            r = B.report(); r["why"] = {k: int((self.why == k).sum()) for k in ("fold", "guide", "slide", "flip")}; return r
        self.surfaces(); co = self.contact_only(); self.clear = np.full(n, np.nan); self.cpair = [""] * n
        for i in range(n):
            if not self.kok[i]: B.record(i, None); continue
            cl, pr = self.collide(i); self.clear[i] = cl; self.cpair[i] = pr
            if cl < PART_CLEAR: self.why[i] = "parts"; B.record(i, None); continue
            d = B.record(i, self.scored(i))
            dc = float(B.dist(i, np.concatenate([self.to_T(m, i, X) for m, X in co])).min())
            if dc < 0: B.res[i] = np.r_[d, dc]; self.why[i] = "contact"
            elif float(d.min()) < 0: self.why[i] = "contact"
        r = B.report()
        r["why"] = {k: int((self.why == k).sum()) for k in ("fold", "guide", "slide", "flip", "parts", "contact")}
        s = (self.k["s_raw"] - self.c)[self.kok]
        r["s_abs_max"] = np.round(np.abs(s).max(0), 1).tolist() if len(s) else None
        r["geom"] = dict(z1=round(self.z1, 1), rho=round(self.rho, 1), arc_deg=[round(self.phi_lo / D2R, 1), round(self.phi_hi / D2R, 1)],
                         lam=round(self.lam, 1), f3=round(self.f3, 1), conn_lift=round(self.conn_lift, 1),
                         R_guide=round(float(np.linalg.norm(self.guide_c)), 1),
                         band_R=[round(float(np.linalg.norm(self.band, axis=1).min()), 1), round(float(np.linalg.norm(self.band, axis=1).max()), 1)])
        r["parts_min"] = {}
        for i in range(n):
            if self.cpair[i]: r["parts_min"][self.cpair[i]] = r["parts_min"].get(self.cpair[i], 0) + int(self.clear[i] < PART_CLEAR)
        r["t"] = round(time.time() - t0, 1)
        return r

    def metal_points(self, i):
        return self.scored(i)

    def part_inband(self):
        """per part: share of its samples 2-14 mm over the taken clip frames (diagnostic)"""
        B = self.B; parts = [("ring", "S", self.ring), ("guide", "L1", self.guide), ("band", "L2", self.band), ("conn", "L2", self.conn),
                             ("rail", "H", self.rail), ("carA", "A", self.carA)]
        out = {}
        taken = [i for i in range(len(B.idx)) if B.kind[i] == "clip" and B.res[i] is not None and float(np.min(B.res[i])) >= 0]
        for nm, m, X in parts:
            d = np.concatenate([B.dist(i, self.to_T(m, i, X)) for i in taken]) if taken else np.zeros(0)
            out[nm] = dict(n=len(X), ib14=round(float(np.mean((d >= 2) & (d <= 14))), 3) if len(d) else None,
                           med=round(float(np.median(d)), 1) if len(d) else None)
        return out


_MODELS = {}
def metal(pose, frames, params, B=None, i=None):
    """bench API: metal sample points of the fitted design at bench pose i (or None if not taken). The design is fitted
    once per params on the bench (rigid heights from the kinematically valid bench poses)."""
    key = json.dumps(params, sort_keys=True)
    if key not in _MODELS:
        B = B or CB.Bench(n_clip=60, n_ws=160); M = Model(B, params); M.run(); _MODELS[key] = M
    M = _MODELS[key]
    if i is None: i = next(j for j, p in enumerate(M.B.poses) if p == pose)
    return None if M.B.res[i] is None or float(np.min(M.B.res[i])) < 0 else M.metal_points(i)


# ---- sweep driver -------------------------------------------------------------------------------------------------
SWEEP_FILE = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def evaluate(B, params, log=None):
    M = Model(B, params); r = M.run(); r["params"] = dict(M.p)
    if log is not None:
        log.append(dict(k=len(log), t=now(), params=dict(M.p), inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                        follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r.get("why"), s_abs_max=r.get("s_abs_max"),
                        geom=r.get("geom")))
    return r, M


def kin_scan(B, params):
    M = Model(B, params); M.design_kin(); good = M.classify(); kind = M.kind
    s = (M.k["s_raw"] - M.c)[M.k["ok"]]
    return dict(clip=round(float(good[kind == "clip"].mean()), 3), ws=round(float(good[kind == "ws"].mean()), 3),
                why={k: int((M.why == k).sum()) for k in ("fold", "guide", "slide", "flip")},
                s_half=np.round(0.5 * (s.max(0) - s.min(0)), 1).tolist(), arc=[round(M.phi_lo / D2R, 1), round(M.phi_hi / D2R, 1)])


def sweep(B, budget=150, stages=None):
    """coarse -> refine inside the morphology; every evaluated configuration is appended to SWEEP_FILE as it finishes"""
    os.makedirs(os.path.dirname(SWEEP_FILE), exist_ok=True)
    log = json.load(open(SWEEP_FILE)) if os.path.exists(SWEEP_FILE) else []
    def key(par): q = dict(PARAMS); q.update(par); return json.dumps(q, sort_keys=True)
    done = {key(e["req"]): e for e in log if "req" in e}
    def run(par):
        kq = key(par)
        if kq in done: return done[kq]
        if len(log) >= budget: return None
        t = time.time(); r, M = evaluate(B, par, log); log[-1]["req"] = par; done[kq] = log[-1]
        log[-1]["comp_h"] = getattr(M, "comp_h", None)
        json.dump(log, open(SWEEP_FILE + ".tmp", "w"), indent=1); os.replace(SWEEP_FILE + ".tmp", SWEEP_FILE)
        print(f"[{len(log):3d}] gap {r['gap']:6.2f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} "
              f"ib10 {r['inband10']:.3f} contact {r['contact']:.3f} why {r.get('why')} geom {r.get('geom')} {par} ({time.time() - t:.0f} s)", flush=True)
        return log[-1]
    def best(filt=lambda e: True):
        c = [e for e in log if filt(e)]; return min(c, key=lambda e: e["gap"]) if c else None
    # stage 0: references (spherical trombone without / with the idle stage)
    run(dict(stage=0)); run(dict()); run(dict(frame="hub"))
    # stage 1: the skin-shaped arc - J2 line offset (o2w toward W's azimuth, o2n normal), J1 / J3 offsets by the LP
    for o2w in (-12, -6, 6, 12):
        for o2n in (-10, 0, 10):
            run(dict(o2w=o2w, o2n=o2n, comp=1))
    b1 = best(lambda e: e["req"].get("stage", 1) == 1)["req"]
    # stage 2: arc coverage of the workspace, frame, slide ranges, arc axial shift
    for k, vals in (("arc_ws", (0.5, 0.8, 0.9)), ("frame", ("hub",)), ("dza", (-6, -3, 3, 6)), ("R_r", (3.0, 5.0)),
                    ("S_a", (15.0, 25.0)), ("S_t", (10.0, 20.0))):
        cur = best(lambda e: e["req"].get("stage", 1) == 1)["req"]
        for v in vals:
            q = dict(cur); q[k] = v; run(q)
    # stage 3: coordinate refinement around the best (J2 offset by 3 mm, LP compensation on/off, percentile)
    for rnd in range(3):
        cur = best(lambda e: e["req"].get("stage", 1) == 1); improved = False
        for k, st in (("o2w", 3.0), ("o2n", 3.0), ("dza", 2.0)):
            for sg in (-1, 1):
                q = dict(cur["req"]); q[k] = q.get(k, 0.0) + sg * st
                if abs(q[k]) > 15: continue
                e = run(q)
                if e is None: return log
                if e["gap"] < cur["gap"] - 1e-9: improved = True
        if not improved: break
    cur = best(lambda e: e["req"].get("stage", 1) == 1)["req"]
    for pc in (99.0, 98.0):
        q = dict(cur); q["pct"] = pc; run(q)
    return log


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "kin":
        B = CB.Bench(n_clip=60, n_ws=160)
        for par in (dict(), dict(stage=0), dict(o2w=10), dict(o2w=-10), dict(o2n=10), dict(o2n=-10), dict(o1m=5), dict(o1t=5),
                    dict(o3a=10), dict(o3t=10), dict(frame="hub", o2w=10), dict(frame="hub", o2n=10), dict(arc_ws=0.9)):
            print(par, kin_scan(B, par), flush=True)
        sys.exit()
    nc, nw = (20, 40) if mode == "check" else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); print("bench", B.mode, len(B.idx), flush=True)
    if mode == "sweep":
        sweep(B, budget=int(sys.argv[2]) if len(sys.argv) > 2 else 150)
    if mode == "check":
        for par in (dict(stage=0), dict(), dict(o2w=10)):
            r, M = evaluate(B, par); print(par, json.dumps({k: v for k, v in r.items() if k != "params"}), flush=True)
            print("   parts", M.part_inband() if not M.dead else None, flush=True)

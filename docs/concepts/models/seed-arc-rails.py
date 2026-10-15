"""seed-arc-rails: arc rails about the GH centre instead of hubs (3 ACTIVE DOF; the cuff's passive slide is set by
closure and sits at its nominal place on the bench, whose GH is fixed in the scapula frame).

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre (a spherical 3R):
    base (scapula handler) = RAIL 1: circular arc about axis u1 (fixed in the scapula frame S), at polar angle rho1
        from u1 on a sphere of radius R1 about GH (rho1 = 90: a great circle, the catalogue spec; rho1 < 90: a "crown"
        lying around the u1 direction)
    -> CARRIAGE 1 (20 x 12 x 8 block straddling rail 1; its place along the rail = joint 1, q1 about u1)
    -> LINK 1 (8 x 3 strap, rigid with carriage 1) -> RAIL 2: arc about u2 (twist a12 from u1) at polar rho2, radius
        R2, fixed to link 1 at one point (the mount); the catalogue spec is rho1 = rho2 = 90, a12 = 90 with carriage 1
        on rail 2's great circle (the "meridian through carriage 1"), so link 1 has zero length there
    -> CARRIAGE 2 (joint 2, q2 about u2) -> LINK 2 (strap) -> C-RING CARRIAGE (20 x 12 x 8)
    -> C-RING (8 x 4 rail, an open circle about the humerus long axis at polar rho3 on the sphere R3) FIXED TO THE CUFF
        (joint 3 = the arm's axial rotation q3) -> cuff (the user's part).
DOF: three rotations about axes through GH (u1, u2, humerus axis): 3 active, each carriage's place on its rail is the
joint angle. Closure (seed-2r-cring's two-circle closure): u2 is a12 from u1 and a23 from the humerus axis d; two
branches, the design keeps one; q3 from the rest of the humerus rotation.
Spec changes (docs/concepts/seed-arc-rails.md): the C-ring is fixed to the cuff and its carriage to body 2 (the ring
always sits at the same place on the arm); every rail lies on a sphere about GH (the only way a carriage can roll on a
circle about an axis through GH); links join carriage 1 -> rail 2 mount and carriage 2 -> ring carriage (zero-length
link 1 in the spec layout); rail 2 is cut around its mount (carriage 2 cannot pass the part that holds the rail);
small-circle rails (rho < 90) are added because the measured great-circle layout cannot lie on the skin.

Geometry (idealised; every part at its real size; skin-facing faces sampled on a 2 mm grid = 1 point / 4 mm2, the
baseline's convention, tools/concept_baseline.py):
  * rails 8 wide x 4 radial at constant distance from GH; carriages 20 along x 12 across x 8 radial with the skin
    face at the rail's skin face (V-wheels at the rail level); links 8 x 3 straps on the great circle between the
    parts they join;
  * radii fitted with the baseline's rule: rail i (with its carriage) at the p-th percentile, over the kinematically
    valid bench poses, of the smallest radius keeping every one of its samples >= CLEAR (2 mm) off the skin; links
    per station along the strap the same way (shaped straps like the baseline links); link 2 can ride over carriage
    2's top (br_up = 1, needed when it runs along rail 2);
  * rail extents: the central `cov` share of the joint values the bench poses need (design branch) + the carriage.
Taken (bench rules): closure on the design branch with the band evaluator's 10 deg singularity margin; every
carriage inside its rail; fit-clip frames followed on EVERY 10 fps frame of the clip (no joint jump > FLIP deg since
the last followed frame, as seed-2r-cring); no interference between parts without a sliding interface (volume samples
>= 1 mm apart). Contact: any skin-facing sample < 0 mm, plus top / edge samples (one appended when inside).

    python3 docs/concepts/models/seed-arc-rails.py check     # default design on Bench(20, 40)
    python3 docs/concepts/models/seed-arc-rails.py sweep     # coarse -> refine sweep on Bench(60, 160)
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "seed-arc-rails"
D2R = math.pi / 180
RAIL_W, RAIL_T = 8.0, 4.0                       # rail section (spec)
CAR_L, CAR_W, CAR_T = 20.0, 12.0, 8.0           # carriage block (spec)
LK_W, LK_T = 8.0, 3.0                           # link strap
SP = 2.0                                        # sample grid (1 point / 4 mm2)
SING = 10.0                                     # deg, fold singularity margin (band evaluator default)
FLIP = 30.0                                     # deg per 10 fps frame: larger joint jump = branch flip, not followed
CLEAR = 2.0                                     # mm: fitted radii keep every sample this far from the skin
MOUNT = 2.0                                     # mm gap between a carriage and the part that holds its rail
GAP_PART = 1.0                                  # mm: clearance between parts without a sliding interface
Y_ARM = np.array([0.0, -1.0, 0.0])              # humerus long axis in the HG frame (concept_baseline convention)
Z_ARM = np.array([0.0, 0.0, 1.0])               # azimuth reference on the C-ring (HG frame)

# spec layout: great-circle rail 1, meridian rail 2 through carriage 1 (a12 = 90, phi1 = 90, rho2 = 90)
PARAMS = dict(u_az=123.0, u_el=44.4, a12=90.0, a23=90.0, branch=1, rho1=90.0, phi1=90.0, rho2=90.0, phi2=75.0, rho3=50.0,
              ring_c=None, ring_on="cuff", cuff_az=90.0, cov=0.95, p=100.0, br_up=1, R_est=60.0, w_delta=0.0, w_az=0.0)
SWEEP = dict(u_az=(0, 360), u_el=(-90, 90), a12=(60, 100), a23=(60, 100), branch=(-1, 1), rho1=(15, 90), phi1=(-90, 90),
             rho2=(15, 90), phi2=(-180, 180), rho3=(25, 65), ring_c=(-90, 90), ring_on=("cuff", "body2"), cuff_az=(-180, 180),
             cov=(0.8, 1.0), p=(50, 100), br_up=(0, 1))


def bvec(az, el):                               # concept_baseline.bvec: az from posterior(-x) toward lateral(+z)
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dir(delta, az):                            # concept_baseline.w_dir: humerus-fixed axis, delta from the long axis
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def rod(k, th):
    """rotations about the fixed unit axis k (3,) by angles th (n,) -> (n, 3, 3)"""
    th = np.atleast_1d(th); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3)[None] + np.sin(th)[:, None, None] * K[None] + (1 - np.cos(th))[:, None, None] * (K @ K)[None]


def ang_about(w, p, q):
    """signed angle (rad) that rotates p onto q about the unit axis w (broadcasting)"""
    pp = p - (p * w).sum(-1, keepdims=True) * w; qq = q - (q * w).sum(-1, keepdims=True) * w
    return np.arctan2((w * np.cross(pp, qq)).sum(-1), (pp * qq).sum(-1))


def perp(v, a):
    return unit(v - (v @ a) * a)


def wrapd(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def circ_range(a_deg, cov):
    """central `cov` share of circular angles (deg): (centre, lo, hi), lo <= 0 <= hi relative to the centre"""
    a = np.asarray(a_deg, float)
    if not len(a): return 0.0, 0.0, 0.0
    s = np.sort(wrapd(a)); g = np.diff(np.r_[s, s[0] + 360]); k = int(np.argmax(g))
    c0 = s[(k + 1) % len(s)]
    rel = np.sort(wrapd(a - c0) % 360)
    lo, hi = np.quantile(rel, [(1 - cov) / 2, 1 - (1 - cov) / 2]) if cov < 1 else (rel[0], rel[-1])
    return float(wrapd(c0 + (lo + hi) / 2)), float(-(hi - lo) / 2), float((hi - lo) / 2)


# ---------------------------------------------------------------- sampled surfaces (unit directions; radius applied later)
def arc_dirs(a, b, rho, t0, t1, r, width, step=SP):
    """arc of the circle at polar rho (rad) about axis a, azimuth t (rad) from b (b _|_ a), t0..t1, on the sphere of
    radius r: (n_along, n_across, 3) unit directions of a strip `width` wide (across = the meridian direction)"""
    ab = np.cross(a, b); rr = max(r * math.sin(rho), 1e-6)
    n = max(2, int(math.ceil(abs(t1 - t0) * rr / step)) + 1); t = np.linspace(t0, t1, n)
    D = math.cos(rho) * a + math.sin(rho) * (np.cos(t)[:, None] * b + np.sin(t)[:, None] * ab)
    E = -math.sin(rho) * a + math.cos(rho) * (np.cos(t)[:, None] * b + np.sin(t)[:, None] * ab)
    c = np.linspace(-width / 2, width / 2, max(2, int(round(width / step)) + 1)) / r
    return unit(D[:, None, :] + c[None, :, None] * E[:, None, :])


def gc_dirs(x0, x1, s0_mm, s1_mm, r, width=LK_W, step=SP):
    """strap on the great circle x0 -> x1, from s0_mm past x0 to s1_mm short of x1 (sphere radius r): (n, nc, 3) or None"""
    ang = math.acos(float(np.clip(x0 @ x1, -1, 1))); a0 = s0_mm / r; a1 = ang - s1_mm / r
    if a1 - a0 < step / r: return None
    t = unit(x1 - (x1 @ x0) * x0); nrm = unit(np.cross(x0, t))
    s = np.linspace(a0, a1, max(2, int(math.ceil((a1 - a0) * r / step)) + 1))
    D = np.cos(s)[:, None] * x0 + np.sin(s)[:, None] * t
    c = np.linspace(-width / 2, width / 2, int(round(width / step)) + 1) / r
    return unit(D[:, None, :] + c[None, :, None] * nrm[None, None, :])


def block_dirs(x0, t, n, r, L=CAR_L, W=CAR_W, step=SP):
    """block footprint centred on direction x0, along t, across n (unit tangents), on the sphere of radius r: (nL, nW, 3)"""
    s = np.linspace(-L / 2, L / 2, int(round(L / step)) + 1); c = np.linspace(-W / 2, W / 2, int(round(W / step)) + 1)
    return unit(x0[None, None] + (s[:, None, None] * t + c[None, :, None] * n) / r)


def rim(D2):
    """edge samples of a (n_along, n_across, 3) strip: both long edges and both ends (side faces)"""
    return np.concatenate([D2[:, 0], D2[:, -1], D2[0], D2[-1]])


_TOK = itertools.count()


# ---------------------------------------------------------------- design
class Design:
    def __init__(self, p, B, HG, RS, status_clip, passes=1):
        self.p = p = dict(PARAMS, **p); self.B = B; self.HG = HG; self.RS = RS; self.n = len(HG); self.status_clip = status_clip
        self.W = w_dir(p["w_delta"], p["w_az"])                                 # rail-3 axis fixed in the humerus (0 = long axis: C-ring)
        self.Z = Z_ARM if p["w_delta"] < 45 else perp(Y_ARM, self.W)             # azimuth reference about W (arm frame)
        self.u1 = bvec(p["u_az"], p["u_el"])
        ref = np.array([0.0, 1.0, 0.0]) if abs(self.u1[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
        e1 = perp(ref, self.u1); a12, a23 = p["a12"] * D2R, p["a23"] * D2R
        self.u2 = math.cos(a12) * self.u1 + math.sin(a12) * e1                    # joint-2 axis at q1 = 0 (body 1)
        self.p3 = unit(math.cos(a23) * self.u2 - math.sin(a23) * perp(self.u1, self.u2))   # humerus axis at q2 = 0 (body 2)
        r1, r2, r3 = p["rho1"] * D2R, p["rho2"] * D2R, p["rho3"] * D2R
        self.c1 = rod(self.u1, np.array([p["phi1"] * D2R]))[0] @ (math.cos(r1) * self.u1 + math.sin(r1) * perp(self.u2, self.u1))
        self.e2 = perp(self.p3, self.u2)                                         # azimuth reference about u2 (toward the arm)
        self.d2 = rod(self.u2, np.array([p["phi2"] * D2R]))[0] @ (math.cos(r2) * self.u2 + math.sin(r2) * self.e2)
        self.g0 = unit(math.cos(r3) * self.p3 + math.sin(r3) * perp(self.d2, self.p3))   # C-ring carriage (body 2)
        ca = p["cuff_az"] * D2R                                                  # ring_on = body2: cuff carriage on the arm (arm frame)
        self.c_arm = math.cos(r3) * self.W + math.sin(r3) * (math.cos(ca) * self.Z + math.sin(ca) * np.cross(self.W, self.Z))
        if p["ring_c"] is not None and p["ring_on"] == "cuff":                    # turn the ring carriage about the arm axis so the
            K0 = self.ik()                                                       # ring's span is centred at ring_c (arm frame, 0 =
            c0 = circ_range(K0["q"][K0["ok"], 2], 1.0)[0]                         # lateral at rest): the C opens on the far side
            self.phi3 = wrapd(p["ring_c"] - c0)
            self.g0 = rod(self.p3, np.array([self.phi3 * D2R]))[0] @ self.g0
        else: self.phi3 = 0.0
        self.att = math.atan2(float(np.cross(self.e2, self.c1) @ self.u2), float(self.e2 @ self.c1)) / D2R  # rail-2 mount azimuth
        self.ok_cfg = math.acos(float(np.clip(self.d2 @ self.p3, -1, 1))) / D2R - p["rho3"] >= 12.0
        self.ik()
        self.Rg = dict(R1=p["R_est"], R2=p["R_est"], R3=p["R_est"])
        for k in range(passes):
            if k: self.Rg = {g: float(np.clip(v, 30.0, 150.0)) for g, v in self.R.items()}
            self.extents(); self.fit()

    # ---- kinematics ------------------------------------------------------------------------------------------------
    def ik(self, HG=None):
        """two-circle closure on the design branch -> q (deg: q1, q2, ring azimuth), a2 (carriage-2 azimuth), ok"""
        store = HG is None; HG = self.HG if HG is None else HG; p = self.p
        u1 = self.u1; d = HG @ self.W; a1, a2 = p["a12"] * D2R, p["a23"] * D2R
        c = np.clip(d @ u1, -1, 1); s2 = 1 - c * c + 1e-12
        al = (math.cos(a1) - c * math.cos(a2)) / s2; be = (math.cos(a2) - c * math.cos(a1)) / s2
        pp = al[:, None] * u1 + be[:, None] * d; h2 = 1 - (pp * pp).sum(-1)
        u2 = unit(pp + p["branch"] * np.sqrt(np.clip(h2, 0, None))[:, None] * unit(np.cross(u1, d)))
        ang = np.arccos(c); lo = abs(a1 - a2) + SING * D2R; hi = min(a1 + a2, 2 * math.pi - a1 - a2) - SING * D2R
        ok = (h2 > 0) & (ang >= lo) & (ang <= hi)
        q1 = ang_about(u1, self.u2, u2)
        A1 = rod(u1, q1)
        q2 = ang_about(u2, A1 @ self.p3, d)
        A2 = A1 @ rod(self.u2, q2)
        N = np.swapaxes(A2, 1, 2) @ HG                                           # arm frame -> body-2 zero frame
        rc = np.einsum("nji,j->ni", N, self.g0)                                  # ring carriage in the arm frame
        tr = ang_about(self.W, self.Z, rc)
        if p["ring_on"] == "body2":                                              # cuff carriage azimuth on the body-2 ring, from the mount
            tr = ang_about(self.p3, self.g0, N @ self.c_arm)
        out = dict(q=np.stack([q1, q2, tr], 1) / D2R, ok=ok, A1=A1, A2=A2)
        out["a2"] = wrapd(out["q"][:, 1] + p["phi2"])                            # carriage-2 azimuth about u2 (from e2)
        if store: self.K = out
        return out

    # ---- rails sized to the needed range ----------------------------------------------------------------------------
    def link1_len(self):
        att = math.cos(self.p["rho2"] * D2R) * self.u2 + math.sin(self.p["rho2"] * D2R) * perp(self.c1, self.u2)
        return math.acos(float(np.clip(att @ self.c1, -1, 1))) * self.p["R_est"]

    def extents(self):
        p = self.p; K = self.K; v = K["ok"]; R1, R2, R3 = self.Rg["R1"], self.Rg["R2"], self.Rg["R3"]
        self.token = next(_TOK); self.__dict__.pop("_static", None)
        s1, s2, s3 = math.sin(p["rho1"] * D2R), math.sin(p["rho2"] * D2R), math.sin(p["rho3"] * D2R)
        self.q1c, self.q1lo, self.q1hi = circ_range(K["q"][v, 0], p["cov"])
        # rail 2: carriage 2 may not come within `ex` of the mount (link 1 / carriage 1 hold the rail there)
        ex = ((LK_W if self.link1_len() > 0.5 else CAR_W) / 2 + MOUNT + CAR_L / 2) / (R2 * s2) / D2R
        rel = wrapd(K["a2"][v] - self.att) % 360
        rel = rel[(rel >= ex) & (rel <= 360 - ex)]
        if len(rel): lo, hi = np.quantile(rel, [(1 - p["cov"]) / 2, 1 - (1 - p["cov"]) / 2]) if p["cov"] < 1 else (rel.min(), rel.max())
        else: lo = hi = 180.0
        self.a2lo, self.a2hi = float(lo), float(hi)
        self.trc, self.trlo, self.trhi = circ_range(K["q"][v, 2], p["cov"])
        if p["ring_on"] == "body2":                                              # the link-2 mount blocks the cuff carriage, as on rail 2
            ex3 = (LK_W / 2 + MOUNT + CAR_L / 2) / (R3 * s3) / D2R
            rel = wrapd(K["q"][v, 2]) % 360; rel = rel[(rel >= ex3) & (rel <= 360 - ex3)]
            if len(rel): lo3, hi3 = np.quantile(rel, [(1 - p["cov"]) / 2, 1 - (1 - p["cov"]) / 2]) if p["cov"] < 1 else (rel.min(), rel.max())
            else: lo3 = hi3 = 180.0
            self.trc, self.trlo, self.trhi = 0.0, float(lo3), float(hi3)
        h1, h2, h3 = (CAR_L / 2 / (r * s) / D2R for r, s in ((R1, s1), (R2, s2), (R3, s3)))
        self.rail1 = (self.q1c + self.q1lo - h1, self.q1c + self.q1hi + h1)
        self.rail2 = (max(self.a2lo - h2, ex - h2), min(self.a2hi + h2, 360 - ex + h2))
        self.ring = (self.trc + self.trlo - h3, self.trc + self.trhi + h3)
        self.span = dict(rail1=round(min(360.0, self.rail1[1] - self.rail1[0]), 1), rail2=round(self.rail2[1] - self.rail2[0], 1),
                         ring=round(min(360.0, self.ring[1] - self.ring[0]), 1))

    def in_range(self, K):
        r1 = wrapd(K["q"][:, 0] - self.q1c); r2 = wrapd(K["a2"] - self.att) % 360
        rt = wrapd(K["q"][:, 2]) % 360 if self.p["ring_on"] == "body2" else wrapd(K["q"][:, 2] - self.trc)
        return ((r1 >= self.q1lo - 1e-6) & (r1 <= self.q1hi + 1e-6) & (r2 >= self.a2lo - 1e-6) & (r2 <= self.a2hi + 1e-6)
                & (rt >= self.trlo - 1e-6) & (rt <= self.trhi + 1e-6))

    # ---- geometry ----------------------------------------------------------------------------------------------------
    def _az1(self):
        """azimuth (deg) of carriage 1 about u1 at q1 = 0, from the reference perp(u2, u1)"""
        b1 = perp(self.u2, self.u1); return math.atan2(float(np.cross(b1, self.c1) @ self.u1), float(b1 @ self.c1)) / D2R

    def static(self):
        if hasattr(self, "_static"): return self._static
        p = self.p; R1, R2, R3 = self.Rg["R1"], self.Rg["R2"], self.Rg["R3"]; S = {}
        b1 = perp(self.u2, self.u1)                                              # azimuth reference about u1
        S["rail1"] = arc_dirs(self.u1, b1, p["rho1"] * D2R, (self.rail1[0] + self._az1()) * D2R, (self.rail1[1] + self._az1()) * D2R, R1, RAIL_W)
        S["car1"] = block_dirs(self.c1, unit(np.cross(self.u1, self.c1)), perp(self.u1, self.c1), R1)
        a0, a1_ = self.att + self.rail2[0], self.att + self.rail2[1]
        S["rail2"] = arc_dirs(self.u2, self.e2, p["rho2"] * D2R, a0 * D2R, a1_ * D2R, R2, RAIL_W)
        att = math.cos(p["rho2"] * D2R) * self.u2 + math.sin(p["rho2"] * D2R) * perp(self.c1, self.u2)
        S["link1"] = gc_dirs(self.c1, att, CAR_W / 2 + 0.5, RAIL_W / 2 + 0.5, (R1 + R2) / 2) if self.link1_len() > CAR_W / 2 + RAIL_W / 2 + 2 else None
        S["car2"] = block_dirs(self.d2, unit(np.cross(self.u2, self.d2)), perp(self.u2, self.d2), R2)
        tdir = perp(self.p3, self.d2); t2 = unit(np.cross(self.u2, self.d2)); n2 = perp(self.u2, self.d2)
        foot = min(CAR_L / 2 / max(abs(tdir @ t2), 1e-6), CAR_W / 2 / max(abs(tdir @ n2), 1e-6))
        S["link2"] = gc_dirs(self.d2, self.g0, foot + 0.5, CAR_W / 2 + 0.5, (R2 + R3) / 2)
        rt = unit(np.cross(self.p3, self.g0))
        if p["ring_on"] == "body2":                                              # ring on body 2, carriage on the cuff (arm frame)
            S["ring"] = arc_dirs(self.p3, perp(self.g0, self.p3), p["rho3"] * D2R, self.ring[0] * D2R, self.ring[1] * D2R, R3, RAIL_W)
            S["ringcar"] = block_dirs(self.c_arm, unit(np.cross(self.W, self.c_arm)), perp(self.W, self.c_arm), R3)
        else:
            S["ringcar"] = block_dirs(self.g0, rt, perp(self.p3, self.g0), R3)
            S["ring"] = arc_dirs(self.W, self.Z, p["rho3"] * D2R, self.ring[0] * D2R, self.ring[1] * D2R, R3, RAIL_W)   # arm frame
        self._static = S; return S

    def dirs(self, i):
        """per pose i: name -> unit dirs (n_along, n_across, 3) in the scapula frame, or None"""
        S = self.static(); K = self.K; A1 = K["A1"][i]; A2 = K["A2"][i]; HG = self.HG[i]
        T = lambda X, M: None if X is None else X @ M.T
        return dict(rail1=S["rail1"], car1=T(S["car1"], A1), link1=T(S["link1"], A1), rail2=T(S["rail2"], A1),
                    car2=T(S["car2"], A2), link2=T(S["link2"], A2),
                    ringcar=T(S["ringcar"], HG if self.p["ring_on"] == "body2" else A2), ring=T(S["ring"], A2 if self.p["ring_on"] == "body2" else HG))

    # ---- radii fitted to the skin (the baseline's rule: percentile over valid poses + clearance) -----------------------
    GROUPS = dict(R1=("rail1", "car1"), R2=("rail2", "car2"), R3=("ring", "ringcar"))

    def fit(self):
        p = self.p; K = self.K
        valid = K["ok"] & self.in_range(K) & self.ok_cfg & np.array([k in ("clip", "ws") for k in self.B.kind]); self.valid = valid
        need = {g: np.full(self.n, np.inf) for g in self.GROUPS}; lk = {"link1": [], "link2": []}
        for i in np.nonzero(valid)[0]:
            D = self.dirs(i); RSi = self.RS[i]; blocks = []
            for g, names in self.GROUPS.items(): blocks.append((g, np.concatenate([D[k].reshape(-1, 3) for k in names])))
            for k in lk:
                if D[k] is not None: blocks += [((k, j), D[k][j]) for j in range(D[k].shape[0])]      # one radius per station
            r = self._need(i, [b_ for _, b_ in blocks], RSi)
            for (key, _), rv in zip(blocks, r):
                if isinstance(key, tuple):
                    if key[1] == 0: lk[key[0]].append([])
                    lk[key[0]][-1].append(rv)
                else: need[key][i] = rv
        self.need = need; self.lk = lk; self.set_p(p["p"])

    def set_p(self, q):
        """radii at the q-th percentile of the per-pose needs (+ CLEAR): the baseline's profile rule"""
        self.p["p"] = q; valid = self.valid; need = self.need
        pc = lambda x: np.nan_to_num(np.minimum(np.percentile(np.minimum(x, 999.0), q, axis=0) + CLEAR, 999.0), nan=999.0)
        self.R = {g: float(pc(need[g][valid])) if valid.any() else 999.0 for g in self.GROUPS}
        self.RL = {k: (pc(np.array(v)) if v else None) for k, v in self.lk.items()}
        if self.p["br_up"] and self.RL["link2"] is not None: self.RL["link2"] = np.maximum(self.RL["link2"], self.R["R2"] + CAR_T)

    def _need(self, i, groups, RSi, lo=20.0, hi=250.0, it=60):
        """for each group of unit directions (scapula frame): the smallest radius at which every sample is >= CLEAR off the
        skin of pose i (inf above hi). Per sample: sphere tracing outward from lo (the distance is 1-Lipschitz, so a step
        of CLEAR - d never jumps over a free radius); group radius = the largest; then checked at that radius and, if a
        sample is back inside (a ray re-entering the head or trunk), scanned upward in 2 mm steps."""
        U = np.concatenate(groups) @ RSi.T; r = np.full(len(U), lo); act = np.ones(len(U), bool)
        for _ in range(it):
            if not act.any(): break
            d = self.B.dist(i, U[act] * r[act, None]); a = np.nonzero(act)[0]
            done = d >= CLEAR; act[a[done]] = False; r[a[~done]] += np.maximum(CLEAR - d[~done], 0.25)
            act &= r <= hi
        r[act] = np.inf; r[r > hi] = np.inf
        out = []; o = 0
        for G in groups:
            m = len(G); rg = float(r[o:o + m].max()); Ug = U[o:o + m]; o += m
            while np.isfinite(rg) and rg <= hi and self.B.dist(i, Ug * rg).min() < CLEAR: rg += 2.0
            out.append(rg - CLEAR if rg <= hi else np.inf)
        return out

    # ---- pose -> metal ------------------------------------------------------------------------------------------------
    def parts_xyz(self, i):
        """name -> (skin-facing samples, top/edge samples, volume samples), thorax frame"""
        D = self.dirs(i); RSi = self.RS[i]; out = {}
        lv = dict(rail1=("R1", RAIL_T), car1=("R1", CAR_T), rail2=("R2", RAIL_T), car2=("R2", CAR_T), ring=("R3", RAIL_T), ringcar=("R3", CAR_T))
        for k, (g, t) in lv.items():
            U = D[k]; r = self.R[g]
            face = U.reshape(-1, 3) * r; top = U.reshape(-1, 3) * (r + t)
            other = np.concatenate([top, rim(U) * (r + t / 2)])
            out[k] = (face @ RSi.T, other @ RSi.T, np.concatenate([face, U.reshape(-1, 3) * (r + t / 2), top]) @ RSi.T)
        for k in ("link1", "link2"):
            U = D[k]
            if U is None: continue
            r = self.RL[k][:, None, None]
            face = (U * r).reshape(-1, 3); top = (U * (r + LK_T)).reshape(-1, 3)
            other = np.concatenate([top, rim(U * (r + LK_T / 2))])
            out[k] = (face @ RSi.T, other @ RSi.T, np.concatenate([face, (U * (r + LK_T / 2)).reshape(-1, 3), top]) @ RSi.T)
        return out

    PAIRS = [("rail1", x) for x in ("link1", "rail2", "car2", "link2", "ringcar", "ring")] + \
            [("car1", x) for x in ("car2", "link2", "ringcar", "ring")] + [("link1", x) for x in ("car2", "link2", "ringcar", "ring")] + \
            [("rail2", x) for x in ("link2", "ringcar", "ring")] + [("car2", "ring"), ("link2", "ring")]

    PAIRS_B2 = [("rail1", x) for x in ("link1", "rail2", "car2", "link2", "ringcar", "ring")] + \
               [("car1", x) for x in ("car2", "link2", "ringcar", "ring")] + [("link1", x) for x in ("car2", "link2", "ringcar", "ring")] + \
               [("rail2", x) for x in ("link2", "ringcar", "ring")] + [("car2", "ringcar"), ("link2", "ringcar")]

    def interfere(self, P):
        for a, b in (self.PAIRS_B2 if self.p["ring_on"] == "body2" else self.PAIRS):
            if a not in P or b not in P: continue
            A, Bv = P[a][2], P[b][2]
            ca, cb = A.mean(0), Bv.mean(0)
            if np.linalg.norm(ca - cb) > np.linalg.norm(A - ca, axis=1).max() + np.linalg.norm(Bv - cb, axis=1).max() + 2 * GAP_PART: continue
            if cKDTree(A).query(Bv, distance_upper_bound=GAP_PART)[0].min() < GAP_PART: return f"{a}/{b}"
        return None

    def metal(self, i):
        """(points or None, reason)"""
        K = self.K; B = self.B
        if not self.ok_cfg: return None, "config"
        if not K["ok"][i]: return None, "closure"
        if not self.in_range(dict(q=K["q"][i:i + 1], a2=K["a2"][i:i + 1]))[0]: return None, "off rail"
        if B.kind[i] == "clip":
            ok, why = self.status_clip(self, int(B.idx[i]))
            if not ok: return None, why
        if max(self.R.values()) >= 200 or any(v is not None and v.max() >= 200 for v in self.RL.values()): return None, "no radius"
        P = self.parts_xyz(i)
        w = self.interfere(P)
        if w: return None, "interference " + w
        face = np.concatenate([v[0] for v in P.values()]); other = np.concatenate([v[1] for v in P.values()])
        do = B.dist(i, other)
        if do.min() < 0: face = np.r_[face, other[np.argmin(do)][None]]
        return face, ""


# ---------------------------------------------------------------- clip continuity on every 10 fps frame
class ClipStatus:
    def __init__(self):
        Z = CB._poses_all(); self.names = list(Z["NAMES"]); self.cid = Z["CID"]; self.HG = Z["HG"].astype(float); self.cache = {}

    def __call__(self, D, j):
        if D.token not in self.cache:
            st = {}
            for n in CB.FIT:
                ix = np.nonzero(self.cid == self.names.index(n))[0]
                K = D.ik(self.HG[ix]); inr = D.in_range(K); last = None
                for k, jj in enumerate(ix):
                    if not K["ok"][k]: st[int(jj)] = (False, "closure"); continue
                    if not inr[k]: st[int(jj)] = (False, "off rail"); continue
                    q = K["q"][k]
                    if last is not None and np.abs(wrapd(q - last)).max() > FLIP: st[int(jj)] = (False, "flip"); continue
                    st[int(jj)] = (True, ""); last = q
            self.cache = {D.token: st}
        return self.cache[D.token].get(j, (False, "missing"))


def run(p, B, HG, RS, cs, passes=2, ps=None):
    """evaluate one geometry at one or several profile percentiles ps (the fit is shared) -> [(report, params)], Design"""
    t = time.time(); D = Design(p, B, HG, RS, cs, passes); out = []
    for q in (ps or [p["p"]]):
        D.set_p(q); B.reset(); why = {}; t1 = time.time()
        for i in range(len(B.poses)):
            if B.kind[i] not in ("clip", "ws"): continue
            P, w = D.metal(i)
            if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None)
            else:
                d = B.record(i, P)
                if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
        r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1); t = time.time()
        r["shape"] = dict({g: round(v, 1) for g, v in D.R.items()},
                          L1=None if D.RL["link1"] is None else [round(float(D.RL["link1"].min()), 1), round(float(D.RL["link1"].max()), 1)],
                          L2=None if D.RL["link2"] is None else [round(float(D.RL["link2"].min()), 1), round(float(D.RL["link2"].max()), 1)],
                          span=D.span, kin_valid=round(float(D.valid.mean()), 3), closure=round(float(D.K["ok"].mean()), 3))
        out.append((r, dict(p, p=q)))
    return out, D


def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) of the concept for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = json.dumps(prm, sort_keys=True)
    if key not in _cache:
        Z = CB._poses_all(); _cache.clear(); _cache[key] = Design(prm, B, Z["HG"][B.idx].astype(float), Z["RS"][B.idx].astype(float), ClipStatus())
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
KEYS = ('u_az', 'u_el', 'a12', 'a23', 'w_delta', 'w_az', 'branch', 'rho1', 'phi1', 'rho2', 'phi2', 'rho3', 'ring_c', 'ring_on', 'cuff_az', 'cov', 'p', 'br_up')


def sweep(configs, B, out=SWEEP_OUT, tag="", passes=2, ps=None):
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float); cs = ClipStatus()
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: res, D = run(p, B, HG, RS, cs, passes, ps)
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", p, e, flush=True); continue
        for r, pq in res:
            row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=pq, inband14=r["inband14"], inband10=r["inband10"],
                       reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r["shape"], mode=r["mode"], stage=tag)
            rows.append(row); json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
            print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
                  f"contact {r['contact']:.3f} | {r['why']} | {r['shape']} | {r['secs']} s | " + " ".join(f"{k}={pq[k]}" for k in KEYS), flush=True)
    return rows


def stage_configs(stage, rows=None):
    """the sweep, coarse -> refine. A: the catalogue spec (great-circle rails); B: crowns (small-circle rails 1, 2);
    C: one-at-a-time refinement around the best B geometry"""
    U1 = [(123.0, 44.4), (2.4, 80.7), (90.0, 30.0), (-60.0, 40.0)]          # singularity-optimal, baseline's base axis, lateral-up, posterior-up
    if stage == "A":
        out = [dict(u_az=a, u_el=e, branch=br, phi2=f2, cov=0.8) for (a, e) in U1 for br in (1, -1) for f2 in (75.0, -75.0)]
        return out + [dict(u_az=123.0, u_el=44.4, branch=br, phi2=75.0 * br, cov=0.6) for br in (1, -1)]
    crown = dict(rho1=15.0, phi1=0.0, rho2=20.0, phi2=0.0, a12=90.0, a23=90.0, ring_c=0.0, br_up=0)
    if stage == "B":
        return [dict(crown, u_az=a, u_el=e, branch=br, rho3=r3, cov=cv) for (a, e) in U1[:2] + [(60.0, 60.0)] for br in (1, -1)
                for r3 in (20.0, 30.0) for cv in (0.7, 0.9)]
    best = min((r for r in rows if r["stage"] in ("B", "C")), key=lambda r: r["gap"])["params"]
    base = {k: v for k, v in best.items() if k != "p"}
    var = dict(a12=(80.0, 100.0), a23=(80.0, 100.0), rho1=(10.0, 25.0), rho2=(12.0, 30.0), rho3=(15.0, 25.0, 35.0), ring_c=(-45.0, 45.0),
               cov=(0.6, 0.8, 0.95), phi1=(-30.0, 30.0), phi2=(-30.0, 30.0))
    return [dict(base, **{k: x}) for k, xs in var.items() for x in xs if x != base.get(k)]


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40)
        sweep([dict(PARAMS)], B, out=os.path.join(os.environ.get("ARC_TMP", "/tmp"), "arc_check.json"), tag="check", ps=[90, 100])
    elif a[0] == "sweep":
        B = CB.Bench(n_clip=60, n_ws=160); print("bench mode", B.mode, flush=True)
        for st in (a[1:] or ["A", "B", "C"]):
            rows = json.load(open(SWEEP_OUT)) if os.path.exists(SWEEP_OUT) else []
            ps = [80.0, 90.0, 100.0] if st == "A" else [50.0, 70.0, 90.0, 100.0]
            sweep(stage_configs(st, rows), B, tag=st, ps=ps)

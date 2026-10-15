"""seed-rcm-parallelogram: scapula base -> R1 (axis through GH) -> planar DOUBLE PARALLELOGRAM whose remote centre of
motion (a remote AXIS, all its joints parallel) passes through GH -> C-ring (axial bearing on the upper arm) -> cuff.
Idealised model on the common concept bench (tools/concept_bench.py), conventions copied from tools/concept_baseline.py.

KINEMATICS (exact, closed form, residual 0 where it closes). Three active joints, all axes through GH:
  axis 1  u1 fixed in the scapula frame;  axis 2  a2 at alpha1 from u1, turning with joint 1;  axis 3  the humerus
  long axis d (HG (0,-1,0)), at alpha2 from a2 - the C-ring. a2 = two-cone intersection (u1 at alpha1, d at alpha2) on
  the design's branch; joint 3 = the carriage angle on the rail. Two orders (the spec's and one improvement):
  * order "yaw" (the catalogue spec): joint 1 = an O20 hub on u1 on the skin; joint 2 = the RCM parallelogram, its
    plane normal to a2 (so the plane turns with R1); joint 3 = the ring.
  * order "rcm" (improvement, see the .md): joint 1 = the RCM parallelogram with its plane FIXED on the scapula
    (normal u1, so the bars always lie on the same patch of the back / shoulder); joint 2 = an O20 hub on a2;
    joint 3 = the ring.
  The parallelogram (7 parallel revolute joints, 6 links incl. ground, 1 DOF by Gruebler): in its plane, with O the
  RCM (pierce point of the axis), C = r_C u(theta + phi_C) on the output O-link, A = rho_A u(psi_A) on the ground,
  A' = (1 - lam) A, B = A + C, B' = A' + C, B2 = A + (1 + mu) C, C2 = (1 + mu) C:  link 1 A-B-B2, crank A'-B',
  link 2 B-B'-C (always parallel to OA), link 2' B2-C2, output C-C2. O-A-B-C and B-B2-C2-C are parallelograms, so the
  output turns exactly like link 1, about O. psi_A = theta_mid + phi_C + gamma0 (gamma0 = the opening at the median
  pose); a pose needs the opening inside [eps, 180 - eps] (no collapse / flip) - a joint limit.
  Continuity: every fit-clip frame at 10 fps on the design branch; a joint step > MAX_STEP deg between consecutive
  frames is a flip -> that frame is not followed.

GEOMETRY (idealised, real sizes; baseline conventions: skin-facing undersides sampled every 2 mm along and across,
hub bottoms as discs on a 2.5 mm grid; each sample's height is fixed in its link = the p-th percentile over the valid
bench poses of the outermost skin crossing along a body-fixed line, + 2 mm; hubs flat; at each joint the upper member
rides on the lower one):
  parallelogram bars 8 x 4 mm, two layers (ground, link 2, link 2' below; link 1, crank, output above: the grid of
  bars is bipartite), heights fitted ALONG THE PLANE NORMAL (planar motion keeps every point's height): bent bars;
  passive pivots 14 mm x 8.5 mm (two layers + 0.5), the active parallelogram input A an O20 (r 10, 12.25 stack);
  links rotating about an axis through GH (yaw-order ground arm, output arm, J2 output) 10 x 4 mm straps fitted
  radially; O20 hubs on u1 (yaw) / a2 (rcm); the ring: C-rail on the cuff, 6 mm radial x 10 mm axial, circular
  (radius = the fitted maximum over its arc), arc `rail_arc` deg centred on the carriage's mean angle; carriage 30 mm
  arc x 16 mm axial, outside the rail (its overhangs face the skin). A pose is NOT taken if: no closure, parallelogram
  opening outside [eps, 180 - eps], carriage off the rail, a flip (clips), two non-adjacent parts closer than 1 mm
  (in-plane bar / disc distances for the parallelogram, 3-D sample clouds for the rest).

    python3 docs/concepts/models/seed-rcm-parallelogram.py [--quick] [--sweep] [--n-clip 60 --n-ws 160]
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "seed-rcm-parallelogram"
D2R = math.pi / 180
MAX_STEP = 30.0                                              # deg per 10 fps frame: a larger joint step is a flip
PARAMS = dict(order="yaw", u_plane=135.0, u_elev=55.0, alpha1=90.0, alpha2=90.0, branch=1, hub_end=-1,
              rho_A=45.0, r_C=35.0, phi_C=0.0, gamma0=90.0, lam=0.45, mu=0.6, eps=15.0,
              ring_l=110.0, ring="C", rail_arc=220.0, clear=2.0, pct=90.0)
SWEEP = dict(order=["yaw", "rcm"], u_plane=[-60, 180], u_elev=[20, 160], alpha1=[60, 120], alpha2=[60, 120], branch=[-1, 1],
             hub_end=[-1, 1], rho_A=[25, 70], r_C=[20, 70], phi_C=[-40, 40], gamma0=[-150, 150], lam=[0.3, 0.7], mu=[0.3, 1.0],
             ring_l=[80, 160], ring=["C", "full"], rail_arc=[180, 240], pct=[60, 100])
W_BAR, T_BAR, R_PIV, R_O20 = 8.0, 4.0, 7.0, 10.0             # parallelogram bars, passive pivot radius, O20 hub radius
W_STRAP, T_STRAP = 10.0, 4.0                                 # straps (links turning about an axis through GH)
UP_PIV, UP_O20 = T_BAR + 0.5, 3.15 + T_STRAP                 # upper member above the lower one at a pivot / an O20
RAIL_T, RAIL_W, CAR_W, CAR_L = 6.0, 10.0, 16.0, 30.0           # C-rail section, carriage size
RING_T = 6.35                                                 # full ring: thin-section bearing 6.35 x 6.35 (e.g. a 4.75" bore Reali-Slim)


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)
def dot(a, b): return (a * b).sum(-1)
def dirvec(plane, elev):                                      # where a humerus at (plane, elev) points (rig convention)
    e, p = elev * D2R, plane * D2R
    return np.array([math.sin(e) * math.sin(p), -math.cos(e), math.sin(e) * math.cos(p)])
def perp_ref(v):
    r = np.where(np.abs(v[..., 1:2]) < 0.9, np.array([0.0, 1, 0]), np.array([1.0, 0, 0]))
    return unit(r - dot(r, v)[..., None] * v)
def wrap(a): return (a + 180.0) % 360.0 - 180.0


# ------------------------------------------------------------------ kinematics (scapula frame S)
def cones(u1, d, a1, a2, br):
    """a2-axis on the cone of half-angle a1 round u1 and a2 round d (P, 3), closes (P,)"""
    c = np.clip(dot(u1, d), -1, 1); den = 1 - c * c + 1e-12
    A = (math.cos(a1) - c * math.cos(a2)) / den; Bc = (math.cos(a2) - c * math.cos(a1)) / den
    v = A[:, None] * u1 + Bc[:, None] * d; h2 = 1 - dot(v, v)
    n = unit(np.cross(u1, d))
    return unit(v + br * np.sqrt(np.clip(h2, 0, None))[:, None] * n), h2 > 1e-6


def kin(prm, HG, RS):
    """per-pose frames in the S frame: dict of (P, 3) vectors + joint angles (deg) + validity"""
    P = len(HG); u1 = np.broadcast_to(dirvec(prm["u_plane"], prm["u_elev"]), (P, 3)).copy()
    d = unit(HG @ np.array([0.0, -1, 0]))
    a2, ok = cones(u1, d, prm["alpha1"] * D2R, prm["alpha2"] * D2R, float(prm["branch"]))
    K = dict(u1=u1, d=d, a2=a2, ok=ok, HG=HG, RS=RS)
    if prm["order"] == "yaw":
        p = a2; g1 = unit(u1 - dot(u1, p)[:, None] * p); eo = unit(d - dot(d, p)[:, None] * p)
        e1u = perp_ref(u1[0])[None].repeat(P, 0); e2u = np.cross(u1, e1u); n2 = unit(p - dot(p, u1)[:, None] * u1)
        th1 = np.degrees(np.arctan2(dot(n2, e2u), dot(n2, e1u)))
        ncar = unit(p - dot(p, d)[:, None] * d)                 # carriage on the linkage side of the ring
    else:
        p = u1; g1 = perp_ref(u1[0])[None].repeat(P, 0); eo = unit(a2 - dot(a2, p)[:, None] * p)
        th1 = None
        ncar = unit(a2 - dot(a2, d)[:, None] * d)               # carriage under the J2 output arm
    g2 = np.cross(p, g1); th = np.degrees(np.arctan2(dot(eo, g2), dot(eo, g1)))
    if th1 is None:
        th1 = th; r = unit(p - dot(p, a2)[:, None] * a2); dp = unit(d - dot(d, a2)[:, None] * a2)
        th2 = np.degrees(np.arctan2(dot(dp, np.cross(a2, r)), dot(dp, r)))
    else:
        th2 = th
    loc = np.einsum("pji,pj->pi", HG, ncar)                    # carriage direction in the humerus frame
    th3 = np.degrees(np.arctan2(loc[:, 2], loc[:, 0]))
    K.update(p=p, g1=g1, g2=g2, eo=eo, th=th, th1=th1, th2=th2, th3=th3, ncar=ncar)
    return K


def best_window(a, width):
    """centre (deg) of the window of `width` deg that holds most of the angles a (deg)"""
    if not len(a): return 0.0
    c = np.arange(-180, 180, 2.0); cnt = (np.abs(wrap(a[None] - c[:, None])) <= width / 2).sum(1)
    return float(c[int(np.argmax(cnt))])


def clip_flips(prm, Z, fit_names):
    """{global pose index: True if the design-branch solution jumps > MAX_STEP deg into that frame (10 fps)}"""
    names = list(Z["NAMES"]); cid = Z["CID"]; flips = {}
    for nm in fit_names:
        g = np.nonzero(cid == names.index(nm))[0]; g = g[np.argsort(Z["FI"][g], kind="stable")]
        K = kin(prm, Z["HG"][g].astype(float), Z["RS"][g].astype(float))
        J = np.stack([K["th1"], K["th2"], K["th3"]], 1); st = np.abs(wrap(np.diff(J, axis=0))).max(1)
        bad = np.r_[False, (st > MAX_STEP) | ~K["ok"][1:] | ~K["ok"][:-1]]
        for gi, b in zip(g, bad): flips[int(gi)] = bool(b)
    return flips


# ------------------------------------------------------------------ geometry: stations (body-fixed lines) per pose
def ribbon_2d(P0, P1, width, step=2.0):
    """in-plane stations of a bar P0 -> P1 (P, 2) each: (P, n, 2) points, n_s, n_c"""
    L = np.linalg.norm(P1 - P0, axis=-1).max(); ns = max(2, int(L / step) + 1); s = np.linspace(0, 1, ns)
    t = unit(P1 - P0); nrm = np.stack([-t[:, 1], t[:, 0]], 1); cs = np.arange(-width / 2, width / 2 + 1e-6, step)
    X = P0[:, None, None] + s[None, :, None, None] * (P1 - P0)[:, None, None] + cs[None, None, :, None] * nrm[:, None, None]
    return X.reshape(len(P0), -1, 2), ns, len(cs)


def disc_2d(c, rad, step=2.5):
    g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rad ** 2
    return c[:, None] + np.stack([X[k], Y[k]], 1)[None]


def arc_dirs(u, v, width, step=2.0, r_ref=70.0):
    """unit directions of a strap on the great circle u -> v (P, 3): (P, ns*nc, 3), ns, nc (as concept_baseline)"""
    ang = np.arccos(np.clip(dot(u, v), -1, 1)); ns = max(3, int(ang.max() * r_ref / step) + 1); s = np.linspace(0, 1, ns)
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u)); th = s[None] * ang[:, None]
    D = np.cos(th)[..., None] * u[:, None] + np.sin(th)[..., None] * e2[:, None]
    cs = np.arange(-width / 2, width / 2 + 1e-6, step) / r_ref
    D = unit(D[:, :, None] * np.cos(cs)[None, None, :, None] + nrm[:, None, None] * np.sin(cs)[None, None, :, None])
    return D.reshape(len(u), -1, 3), ns, len(cs)


def disc_dirs(u, rad, r_ref, step=2.5):
    g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rad ** 2
    a = perp_ref(u); b = np.cross(u, a)
    return unit(u[:, None] + (X[k] / r_ref)[None, :, None] * a[:, None] + (Y[k] / r_ref)[None, :, None] * b[:, None])


def seg_dist(P0, P1, Q0, Q1):
    """min distance between 2-D segments, batched (P, 2) each"""
    def pt_seg(X, A, Bq):
        AB = Bq - A; t = np.clip(dot(X - A, AB) / (dot(AB, AB) + 1e-12), 0, 1); return np.linalg.norm(X - A - t[:, None] * AB, axis=1)
    def cross2(a, b): return a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]
    r = P1 - P0; s = Q1 - Q0; den = cross2(r, s); qp = Q0 - P0
    with np.errstate(divide="ignore", invalid="ignore"):
        t = cross2(qp, s) / den; u = cross2(qp, r) / den
    inter = (np.abs(den) > 1e-9) & (t >= 0) & (t <= 1) & (u >= 0) & (u <= 1)
    m = np.minimum(np.minimum(pt_seg(P0, Q0, Q1), pt_seg(P1, Q0, Q1)), np.minimum(pt_seg(Q0, P0, P1), pt_seg(Q1, P0, P1)))
    return np.where(inter, 0.0, m)


class Model:
    """one configuration on one bench: kinematics, stations, fitted profiles, per-pose metal"""

    def __init__(self, prm, B, Z=None, log=print):
        self.prm = dict(PARAMS, **prm); self.B = B; self.Z = Z if Z is not None else CB._poses_all(); self.log = log
        pr = self.prm; Z = self.Z
        HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float); self.RS = RS
        K = self.K = kin(pr, HG, RS); Pn = len(HG)
        flips = clip_flips(pr, Z, CB.FIT)
        self.flip = np.array([flips.get(int(g), False) if k == "clip" else False for g, k in zip(B.idx, B.kind)])
        ok = K["ok"].copy()
        # parallelogram geometry (2-D, ground basis g1, g2)
        th = K["th"]; th_mid = best_window(th[ok], 180 - 2 * pr["eps"])
        psiA = (th_mid + pr["phi_C"] + pr["gamma0"]) * D2R; self.th_mid = th_mid
        u2 = lambda a: np.stack([np.cos(a), np.sin(a)], -1)
        C = pr["r_C"] * u2((th + pr["phi_C"]) * D2R); A = np.broadcast_to(pr["rho_A"] * u2(np.array(psiA)), (Pn, 2)).copy()
        J = dict(A=A, Ap=(1 - pr["lam"]) * A, B=A + C, Bp=(1 - pr["lam"]) * A + C, B2=A + (1 + pr["mu"]) * C, C=C, C2=(1 + pr["mu"]) * C)
        self.J = J
        gam = (pr["psiA_deg"] if "psiA_deg" in pr else math.degrees(psiA)) - (th + pr["phi_C"])
        sg = 1.0 if math.sin(pr["gamma0"] * D2R) >= 0 else -1.0
        self.open_ok = sg * np.sin(gam * D2R) >= math.sin(pr["eps"] * D2R)
        # ring: carriage angle on the rail (arm frame), rail centred on its circular mean over the closing poses
        th3 = K["th3"]; okc = ok & self.open_ok
        car_half = math.degrees(CAR_L / 2 / 60.0); self.full = pr.get("ring", "C") == "full"
        self.phi_rail = best_window(th3[okc], pr["rail_arc"] - 2 * car_half)
        self.rt = RING_T if self.full else RAIL_T
        self.rail_ok = np.ones(len(th3), bool) if self.full else np.abs(wrap(th3 - self.phi_rail)) <= pr["rail_arc"] / 2 - car_half
        self.valid = ok & self.open_ok & self.rail_ok & ~self.flip
        self.planar_ok = self._planar_clearance()
        self.valid &= self.planar_ok
        self._stations()

    # ---- in-plane clearance of the parallelogram (bars as 8 mm capsules, pivots as discs)
    def _planar_clearance(self):
        J = self.J; bars = dict(G=("A", "Ap"), L1=("A", "B2"), K=("Ap", "Bp"), L2=("B", "C"), L2p=("B2", "C2"), O=("C", "C2"))
        joints = dict(A=("G", "L1"), Ap=("G", "K"), B=("L1", "L2"), Bp=("K", "L2"), B2=("L1", "L2p"), C=("L2", "O"), C2=("L2p", "O"))
        rad = {j: (R_O20 if j == "A" else R_PIV) for j in joints}
        ok = np.ones(len(J["A"]), bool); names = list(bars)
        for i, a in enumerate(names):
            for b in names[i + 1:]:
                if any(a in own and b in own for own in joints.values()): continue     # adjacent (share a joint)
                ok &= seg_dist(J[bars[a][0]], J[bars[a][1]], J[bars[b][0]], J[bars[b][1]]) >= W_BAR + 1.0
        for j, own in joints.items():
            for b in names:
                if b in own: continue
                ok &= seg_dist(J[j], J[j], J[bars[b][0]], J[bars[b][1]]) >= rad[j] + W_BAR / 2 + 1.0
        js = list(joints)
        for i, a in enumerate(js):
            for b in js[i + 1:]:
                ok &= np.linalg.norm(J[a] - J[b], axis=1) >= rad[a] + rad[b] + 1.0
        return ok

    # ---- stations: name -> dict(base (P,m,3) S frame, dir (P,m,3), kind, body, ns, nc)
    def _stations(self):
        pr = self.prm; K = self.K; J = self.J; Pn = len(K["d"]); p = K["p"]; g1, g2 = K["g1"], K["g2"]
        to3 = lambda X: X[..., 0:1] * g1[:, None] + X[..., 1:2] * g2[:, None]
        S = {}
        def planar(name, body, X, ns=None, nc=None, layer=0):
            S[name] = dict(base=to3(X), dir=np.broadcast_to(p[:, None], X.shape[:2] + (3,)), kind="p", body=body, ns=ns, nc=nc, layer=layer)
        bars = dict(G=("A", "Ap", 0), L1=("A", "B2", 1), K=("Ap", "Bp", 1), L2=("B", "C", 0), L2p=("B2", "C2", 0), O=("C", "C2", 1))
        for nm, (a, b, lay) in bars.items():
            X, ns, nc = ribbon_2d(J[a], J[b], W_BAR); planar("bar_" + nm, nm, X, ns, nc, lay)
        for j in J:
            planar("hub_" + j, "hub_" + j, disc_2d(J[j], R_O20 if j == "A" else R_PIV))
        r_ref = 70.0
        if pr["order"] == "yaw":
            hub_ax = pr["hub_end"] * K["u1"]
            Dh = disc_dirs(hub_ax, R_O20, 62.0); S["hub_R1"] = dict(base=np.zeros_like(Dh), dir=Dh, kind="r", body="hub_R1")
            Adir = unit(to3(J["A"][:, None])[:, 0] + 60.0 * p)
            D, ns, nc = arc_dirs(Adir, hub_ax, W_STRAP); S["arm_G"] = dict(base=np.zeros_like(D), dir=D, kind="r", body="G", ns=ns, nc=nc)
            C2dir = unit(to3(J["C2"][:, None])[:, 0] + 60.0 * p); head = C2dir
        else:
            a2 = K["a2"]
            Dh = disc_dirs(a2, R_O20, 62.0); S["hub_J2"] = dict(base=np.zeros_like(Dh), dir=Dh, kind="r", body="hub_J2")
            C2dir = unit(to3(J["C2"][:, None])[:, 0] + 60.0 * p)
            D, ns, nc = arc_dirs(C2dir, a2, W_STRAP); S["arm_O"] = dict(base=np.zeros_like(D), dir=D, kind="r", body="O", ns=ns, nc=nc)
            head = a2
        # carriage target direction (from GH) at the ring level; the arm to it is a strap fitted radially
        car_dir = unit(pr["ring_l"] * K["d"] + 62.0 * K["ncar"])
        D, ns, nc = arc_dirs(head, car_dir, W_STRAP)
        S["arm_out"] = dict(base=np.zeros_like(D), dir=D, kind="r", body="O" if pr["order"] == "yaw" else "J2", ns=ns, nc=nc)
        # rail (arm-fixed): circle at ring_l round the humerus axis, arc rail_arc centred on phi_rail; lines radial from the axis
        arc = 360.0 if self.full else pr["rail_arc"]; n_ang = int(arc * D2R * 60 / 2.0) + 1
        ang = (self.phi_rail + np.linspace(-arc / 2, arc / 2, n_ang, endpoint=not self.full)) * D2R
        zs = np.linspace(-RING_T / 2 + 0.5, RING_T / 2 - 0.5, 3) if self.full else np.arange(-RAIL_W / 2 + 1, RAIL_W / 2, 2.0)
        loc_dir = np.stack([np.cos(ang), np.zeros_like(ang), np.sin(ang)], 1)          # humerus frame, long axis -y
        HG = K["HG"]; Dw = np.einsum("pij,aj->pai", HG, loc_dir)
        base = (pr["ring_l"] + zs)[None, None, :, None] * K["d"][:, None, None, :] + 0 * Dw[:, :, None]
        S["rail"] = dict(base=np.broadcast_to(base, (Pn, n_ang, len(zs), 3)).reshape(Pn, -1, 3),
                         dir=np.broadcast_to(Dw[:, :, None], (Pn, n_ang, len(zs), 3)).reshape(Pn, -1, 3), kind="a", body="rail")
        self.S = S
        if self.full: return
        # carriage (on the output / J2 output): an arc of CAR_L mm round the carriage direction, overhang rows only
        ca = np.linspace(-CAR_L / 2, CAR_L / 2, int(CAR_L / 2) + 1) / 62.0; zc = np.array([-CAR_W / 2, -CAR_W / 2 + 2, CAR_W / 2 - 2, CAR_W / 2])
        tdir = unit(np.cross(K["d"], K["ncar"]))
        Dc = unit(np.cos(ca)[None, :, None] * K["ncar"][:, None] + np.sin(ca)[None, :, None] * tdir[:, None])
        bc = (pr["ring_l"] + zc)[None, None, :, None] * K["d"][:, None, None, :]
        S["carriage"] = dict(base=np.broadcast_to(bc, (Pn, len(ca), len(zc), 3)).reshape(Pn, -1, 3),
                             dir=np.broadcast_to(Dc[:, :, None], (Pn, len(ca), len(zc), 3)).reshape(Pn, -1, 3), kind="c", body="car")
        self.S = S

    # ---- skin crossings along every station line, every valid pose
    def crossings(self, D=None):
        t0 = time.time()
        for i in np.nonzero(self.valid)[0]: self.cross_pose(int(i), D)
        self.t_cross = time.time() - t0
        return self.X

    def cross_pose(self, i, D=None):
        """skin crossings of every station line in pose i (D(i, P): signed distance; default the bench's)"""
        names = list(self.S)
        if not hasattr(self, "X"):
            self.X = {nm: np.zeros(self.S[nm]["base"].shape[:2]) for nm in names}
        X = self.X; D = D if D is not None else self.B.dist
        if True:
            RS = self.RS[i]; bases = []; dirs = []; hmax = []; hmin = []
            for nm in names:
                if self.S[nm]["kind"] == "c": continue
                st = self.S[nm]; bases.append(st["base"][i] @ RS.T); dirs.append(st["dir"][i] @ RS.T); m = len(st["base"][i])
                hmax.append(np.full(m, {"p": 170.0, "r": 170.0, "a": 100.0, "c": 100.0}[st["kind"]]))
                hmin.append(np.full(m, {"p": 15.0, "r": 15.0, "a": 20.0, "c": 20.0}[st["kind"]]))
            b = np.concatenate(bases); u = np.concatenate(dirs); h = np.concatenate(hmax); lo = np.concatenate(hmin)
            out = trace(D, int(i), b, u, h, lo); o = 0
            for nm in names:
                if self.S[nm]["kind"] == "c": continue
                m = len(self.S[nm]["base"][i]); X[nm][i] = out[o:o + m]; o += m

    def profiles(self, pct):
        """station heights (fixed in their links) for percentile pct; rail radius; joint levels"""
        pr = self.prm; v = self.valid; X = self.X; c = pr["clear"]
        def q(a):
            if not v.any(): return np.zeros(a.shape[1])
            x = a[v]; x = np.where(np.isnan(x), np.nanmax(np.where(np.isnan(x), -np.inf, x)) if np.isfinite(x).any() else 0.0, x)   # blocked: the worst seen
            return np.percentile(x, pct, axis=0) + c
        H = {nm: q(X[nm]) for nm in X if nm not in ("rail", "carriage")}
        lev = {}
        for j in ("A", "Ap", "B", "Bp", "B2", "C", "C2"):
            lev[j] = float(H["hub_" + j].max()); H["hub_" + j][:] = lev[j]
        hubR = "hub_R1" if pr["order"] == "yaw" else "hub_J2"; H[hubR][:] = H[hubR].max()
        lower = dict(A="G", Ap="G", B="L2", Bp="L2", B2="L2p", C="L2", C2="L2p")
        bars = dict(G=("A", "Ap", 0), L1=("A", "B2", 1), K=("Ap", "Bp", 1), L2=("B", "C", 0), L2p=("B2", "C2", 0), O=("C", "C2", 1))
        for nm, (a, b, lay) in bars.items():                         # bar ends sit on their pivots, upper layer on top
            st = self.S["bar_" + nm]; pr_ = H["bar_" + nm].reshape(st["ns"], st["nc"]); L = np.linalg.norm(self.J[b][0] - self.J[a][0])
            ne = max(1, int(math.ceil((R_O20 + 2) / max(L / (st["ns"] - 1), 1e-6))))
            for j, sl in ((a, slice(0, ne)), (b, slice(st["ns"] - ne, st["ns"]))):
                up = 0.0 if lower[j] == nm else (UP_O20 if j == "A" else UP_PIV)
                pr_[sl] = np.maximum(pr_[sl], lev[j] + up)
            H["bar_" + nm] = pr_.reshape(-1)
        # radial straps: ends on their hubs (radius of the hub point at the member's level)
        def raise_ends(nm, r0=None, r1=None):
            st = self.S[nm]; pr_ = H[nm].reshape(st["ns"], st["nc"]); ne = max(2, st["ns"] // 6)
            if r0 is not None: pr_[:ne] = np.maximum(pr_[:ne], r0)
            if r1 is not None: pr_[-ne:] = np.maximum(pr_[-ne:], r1)
            H[nm] = pr_.reshape(-1)
        rho = lambda j, h: float(np.hypot(np.linalg.norm(self.J[j][0]), h))
        xr = X["rail"][v] if v.any() else np.full((1, X["rail"].shape[1]), 60.0)
        with np.errstate(all="ignore"):
            col = np.nanpercentile(xr, pct, axis=0)            # blocked (rail start inside the trunk): left to the contact test
        self.r_ring = float(np.nanmax(col) + c) if np.isfinite(col).any() else 60.0
        car_r = math.hypot(pr["ring_l"], self.r_ring + self.rt + 0.5)
        if pr["order"] == "yaw":
            raise_ends("arm_G", rho("A", lev["A"]), float(H["hub_R1"].max()) + UP_O20)
            raise_ends("arm_out", rho("C2", lev["C2"] + UP_PIV), car_r)
        else:
            raise_ends("arm_O", rho("C2", lev["C2"] + UP_PIV), float(H["hub_J2"].max()))
            raise_ends("arm_out", float(H["hub_J2"].max()) + UP_O20, car_r)
        H["rail"] = np.full(X["rail"].shape[1], self.r_ring)
        if "carriage" in X: H["carriage"] = np.full(X["carriage"].shape[1], self.r_ring + RAIL_T + 0.5)
        self.H = H; self.lev = lev
        return H

    def points(self, i, by_body=False):
        """metal sample points of pose i in the thorax frame (k, 3), or None if the pose is not taken"""
        if not self.valid[i]: return None
        RS = self.RS[i]; parts = {}
        for nm, st in self.S.items():
            Pp = st["base"][i] + self.H[nm][:, None] * st["dir"][i]; parts.setdefault(st["body"], []).append(Pp @ RS.T)
        parts = {k: np.concatenate(v) for k, v in parts.items()}
        if not self._clear3d(parts): return None
        return parts if by_body else np.concatenate(list(parts.values()))

    def _clear3d(self, parts):
        """3-D clearance of the non-planar parts (straps, hubs, rail, carriage) against every non-adjacent body"""
        yaw = self.prm["order"] == "yaw"
        adj = {("G", "hub_R1"), ("G", "hub_A"), ("G", "hub_Ap"), ("G", "L1"), ("G", "K"), ("O", "hub_C"), ("O", "hub_C2"), ("O", "L2"), ("O", "L2p"),
               ("car", "rail"), ("car", "O"), ("car", "J2"), ("O", "hub_J2"), ("J2", "hub_J2"), ("O", "J2")}
        for j, (a, b) in dict(A=("G", "L1"), Ap=("G", "K"), B=("L1", "L2"), Bp=("K", "L2"), B2=("L1", "L2p"), C=("L2", "O"), C2=("L2p", "O")).items():
            adj |= {("hub_" + j, a), ("hub_" + j, b)}
        if self.full: adj |= {("O", "rail"), ("J2", "rail")}           # the arm is fixed to the outer race
        adj |= {(b, a) for a, b in adj}
        free = ["G", "hub_R1", "rail"] if yaw else ["J2", "hub_J2", "rail", "O"]
        trees = {}
        for a in free:
            if a not in parts: continue
            ta = trees.setdefault(a, cKDTree(parts[a]))
            for b, Pb in parts.items():
                if b == a or (a, b) in adj: continue
                if b in free and free.index(b) < free.index(a): continue
                dmin = ta.query(Pb, k=1, distance_upper_bound=T_STRAP + 1.0)[0].min()
                if dmin < T_STRAP + 1.0: return False
        return True


def trace(D, i, base, u, h_max, h_min):
    """outermost skin crossing along lines base + h u (k, 3), inward from h_max (sphere tracing on the signed distance
    D(i, P)); h_min where there is none, NaN if the start is already inside the body (blocked)"""
    h = h_max.copy(); act = np.ones(len(h), bool); hit = np.zeros(len(h), bool)
    d0 = D(i, base + h[:, None] * u); blocked = d0 < 0; act &= ~blocked
    for _ in range(80):
        if not act.any(): break
        a = np.nonzero(act)[0]; d = D(i, base[a] + h[a, None] * u[a])
        done = d < 0.3; hit[a[done]] = True; act[a[done]] = False
        h[a[~done]] -= np.maximum(d[~done], 0.5); act &= h >= h_min
    return np.where(blocked, np.nan, np.where(hit, h, h_min))


class ApproxSkin:
    """SCREENING-ONLY signed distance (used to rank configurations fast while the machine is loaded; every reported
    number is re-measured with the bench's own distance): nearest dense skin sample (judge/sdist.Mesh samples, h mm,
    on the skin within r mm of GH) with the sign of that sample's pseudo-normal. One pose at a time."""
    def __init__(self, B, V=None, h=2.0, r=240.0, store=None):
        self.B, self.V, self.h, self.r, self.cur = B, V, h, r, None
        self.store = None
        if store and os.path.exists(store):
            z = np.load(store); self.store = (z["S"], z["N"], z["off"])

    def samples(self, i):
        from sdist import Mesh
        V = np.asarray(self.V[i], float) if self.V is not None else self.B._verts(i); F = CB.BP.F
        keep = (np.linalg.norm(V, axis=1) < self.r)[F].all(1); M = Mesh(V, F[keep], self.h)
        used = np.zeros(len(V), bool); used[F[keep]] = True; sel = np.r_[used, np.ones(len(M.S) - len(V), bool)]
        N = np.r_[M.Nv, M.Nf[M.owner]] if len(M.owner) else M.Nv
        return M.S[sel].astype(np.float32), N[sel].astype(np.float32)

    def build_store(self, path):
        S, N, off = [], [], [0]
        for i in range(len(self.B.poses)):
            a, b = self.samples(i); S.append(a); N.append(b); off.append(off[-1] + len(a))
        np.savez(path, S=np.concatenate(S), N=np.concatenate(N), off=np.array(off)); self.store = None

    def load(self, i):
        if self.cur == i: return
        if self.store is not None:
            S, N, off = self.store; self.S = np.asarray(S[off[i]:off[i + 1]], float); self.N = np.asarray(N[off[i]:off[i + 1]], float)
        else:
            self.S, self.N = (np.asarray(x, float) for x in self.samples(i))
        self.tree = cKDTree(self.S); self.cur = i

    def __call__(self, i, P):
        self.load(i); P = np.asarray(P, float); shp = P.shape[:-1]; P = P.reshape(-1, 3)
        d, j = self.tree.query(P); sg = np.sign(((P - self.S[j]) * self.N[j]).sum(1)); sg[sg == 0] = 1
        return (sg * d).reshape(shp)


def run_batch(prms, B, D=None, pcts=(80, 90, 100), Z=None, log=print):
    """evaluate several configurations pose-major (one skin in memory at a time). D: distance (default the bench's).
    Returns [best report per configuration] (each with 'pct', 'diag')."""
    Z = Z if Z is not None else CB._poses_all(); D = D if D is not None else B.dist; t0 = time.time()
    models = []
    for p in prms:
        try: models.append(Model(p, B, Z))
        except Exception as e: log(f"  model failed {p}: {e}"); models.append(None)
    for i in range(len(B.poses)):
        for M in models:
            if M is not None and M.valid[i]: M.cross_pose(i, D)
    t1 = time.time(); Hs = []
    for M in models:
        if M is None or not hasattr(M, "X"): Hs.append(None); continue
        h = {}
        for pct in pcts:
            M.profiles(pct); h[pct] = (dict((k, v.copy()) for k, v in M.H.items()), M.r_ring, dict(M.lev))
        Hs.append(h)
    res = [{pct: [None] * len(B.poses) for pct in pcts} for _ in models]
    for i in range(len(B.poses)):
        for k, M in enumerate(models):
            if Hs[k] is None: continue
            for pct in pcts:
                M.H, M.r_ring, M.lev = Hs[k][pct]; P = M.points(i)
                res[k][pct][i] = None if P is None else D(i, P)
    out = []
    for k, M in enumerate(models):
        if Hs[k] is None:
            out.append(dict(reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, gap=999.0, pct=None, diag="no valid pose")); continue
        best = None
        for pct in pcts:
            B.res = res[k][pct]; r = B.report(); r["pct"] = pct
            if best is None or r["gap"] < best["gap"]: best = r
        best["diag"] = dict(closes=round(float(M.K["ok"].mean()), 3), open_ok=round(float(M.open_ok.mean()), 3), rail_ok=round(float(M.rail_ok.mean()), 3),
                            flips=int(M.flip.sum()), planar_ok=round(float(M.planar_ok.mean()), 3), valid=round(float(M.valid.mean()), 3))
        M.H, M.r_ring, M.lev = Hs[k][best["pct"]]; best["r_ring"] = round(M.r_ring, 1)
        out.append(best)
    B.reset(); log(f"  batch of {len(prms)}: {time.time() - t0:.0f} s (crossings {t1 - t0:.0f} s)")
    return out, models


def evaluate(prm, B, pcts=(70, 80, 90, 95, 100), Z=None, log=print, keep_model=False):
    """build, fit, score every pct; returns the best report (+ the model)"""
    t0 = time.time(); M = Model(prm, B, Z, log); M.crossings(); best = None; t1 = time.time()
    for pct in pcts:
        M.profiles(pct); B.reset()
        for i in range(len(B.poses)): B.record(i, M.points(i))
        r = B.report(); r["pct"] = pct
        r["kin_valid"] = round(float(M.valid.mean()), 3)
        if best is None or r["gap"] < best["gap"]: best = r
    best["secs"] = round(time.time() - t0, 1); best["secs_cross"] = round(t1 - t0, 1)
    best["diag"] = dict(closes=round(float(M.K["ok"].mean()), 3), open_ok=round(float(M.open_ok.mean()), 3), rail_ok=round(float(M.rail_ok.mean()), 3),
                        flips=int(M.flip.sum()), planar_ok=round(float(M.planar_ok.mean()), 3), valid=round(float(M.valid.mean()), 3))
    return (best, M) if keep_model else best


def kin_scan(B, Z=None, orders=("yaw", "rcm"), alphas=(60, 75, 90, 105, 120), step=20, rail_arc=220.0, eps=15.0, log=print):
    """kinematics only (no geometry, no skin): share of bench clip frames / workspace poses where the chain closes,
    does not flip, the parallelogram opening stays in its best [eps, 180-eps] window and (C-rail) the carriage on its
    best rail_arc window. An upper bound on follow / reach for every geometry with these axes."""
    Z = Z if Z is not None else CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float)
    cl = np.array([k == "clip" for k in B.kind]); names = list(Z["NAMES"]); rows = []
    seqs = []
    for nm in CB.FIT:
        g = np.nonzero(Z["CID"] == names.index(nm))[0]; seqs.append(g[np.argsort(Z["FI"][g], kind="stable")])
    allg = np.concatenate(seqs); pos = {int(gg): j for j, gg in enumerate(allg)}; bidx = np.array([pos.get(int(gg), -1) for gg in B.idx])
    HGa = Z["HG"][allg].astype(float); RSa = Z["RS"][allg].astype(float); starts = np.cumsum([0] + [len(s_) for s_ in seqs])[:-1]
    car_half = math.degrees(CAR_L / 2 / 60.0)
    for order in orders:
        for up in range(-90, 181, step):
            for ue in range(0, 181, step):
                if ue in (0, 180) and up != -90: continue
                for a1 in alphas:
                    for a2 in alphas:
                        for br in (-1, 1):
                            prm = dict(PARAMS, order=order, u_plane=up, u_elev=ue, alpha1=a1, alpha2=a2, branch=br)
                            K = kin(prm, HG, RS); Ka = kin(prm, HGa, RSa)
                            J = np.stack([Ka["th1"], Ka["th2"], Ka["th3"]], 1); st = np.r_[0, np.abs(wrap(np.diff(J, axis=0))).max(1)]
                            st[starts] = 0; flip = (st > MAX_STEP) | ~Ka["ok"]; fl = np.where(bidx >= 0, flip[np.clip(bidx, 0, None)], False)
                            ok = K["ok"] & ~fl; thc = best_window(K["th"][ok], 180 - 2 * eps)
                            ok &= np.abs(wrap(K["th"] - thc)) <= 90 - eps
                            okC = ok & (np.abs(wrap(K["th3"] - best_window(K["th3"][ok], rail_arc - 2 * car_half))) <= rail_arc / 2 - car_half)
                            th_ok = K["th"][ok]; span = float(np.ptp(wrap(th_ok - thc))) if ok.any() else 0.0
                            r = dict(order=order, u_plane=up, u_elev=ue, alpha1=a1, alpha2=a2, branch=br,
                                     follow_full=round(float(ok[cl].mean()), 3), reach_full=round(float(ok[~cl].mean()), 3),
                                     follow_C=round(float(okC[cl].mean()), 3), reach_C=round(float(okC[~cl].mean()), 3), pitch_span=round(span, 1))
                            r["kgap_full"] = round(100 * (max(0, .95 - r["follow_full"]) + max(0, .9 - r["reach_full"])), 1)
                            r["kgap_C"] = round(100 * (max(0, .95 - r["follow_C"]) + max(0, .9 - r["reach_C"])), 1)
                            rows.append(r)
    return rows


_CACHE = {}
def metal(pose, frames, params=None):
    """bench API: metal points (k, 3) of pose `pose` (a dict from Bench.poses) or None. Profiles are fitted on the
    default bench (60 clip frames, 160 workspace poses) at params['pct']; a pose outside it gets the nearest bench pose's."""
    prm = dict(PARAMS, **(params or {})); key = json.dumps(prm, sort_keys=True)
    if key not in _CACHE:
        B = CB.Bench(60, 160); M = Model(prm, B); M.crossings(); M.profiles(prm["pct"]); _CACHE[key] = M
    M = _CACHE[key]; P = np.array([[q["plane"], q["elev"], q["axial"]] for q in M.B.poses])
    i = int(np.argmin(np.abs(P - [pose["plane"], pose["elev"], pose["axial"]]).sum(1)))
    return M.points(i)


def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
# axis candidates from kin_scan on Bench(60, 160) (kinematic gap 0 for that ring, smallest parallelogram pitch span; the
# span sets the bar offsets the 14 mm pivots need: opening >= 90 - span / 2)
AXES = [dict(order="yaw", u_plane=-50, u_elev=160, alpha1=90, alpha2=90, ring="full", span=96.5),
        dict(order="yaw", u_plane=50, u_elev=40, alpha1=75, alpha2=90, ring="full", span=101.5),
        dict(order="yaw", u_plane=30, u_elev=140, alpha1=90, alpha2=90, ring="C", span=112.1),
        dict(order="yaw", u_plane=30, u_elev=80, alpha1=90, alpha2=90, ring="C", span=117.0),
        dict(order="rcm", u_plane=-70, u_elev=60, alpha1=90, alpha2=90, ring="full", span=147.7),
        dict(order="rcm", u_plane=50, u_elev=120, alpha1=75, alpha2=75, ring="C", span=146.8)]


def sample_geometry(ax, rng, n):
    """n geometries for one axis candidate, inside the range where the 14 mm pivots can clear (opening >= 90 - span/2)"""
    s_ = max(math.cos(ax["span"] / 2 * D2R), 0.2); out = []
    for _ in range(n):
        lam = rng.uniform(0.35, 0.7); r_C = rng.uniform(15 / s_, 15 / s_ + 25); rho = max(rng.uniform(15 / s_ / lam, 15 / s_ / lam + 25), 20.0)
        mu = rng.uniform(12 / s_ / r_C, 12 / s_ / r_C + 0.4)
        p = {k: v for k, v in ax.items() if k != "span"}
        p.update(branch=int(rng.choice([-1, 1])), hub_end=int(rng.choice([-1, 1])), rho_A=round(rho, 1), r_C=round(r_C, 1), lam=round(lam, 2), mu=round(mu, 2),
                 phi_C=round(rng.uniform(-30, 30), 1), gamma0=round(float(rng.choice([-90, 90])) + rng.uniform(-15, 15), 1), eps=10.0,
                 ring_l=round(rng.uniform(90, 150), 1), rail_arc=round(rng.uniform(200, 240), 1))
        out.append(p)
    return out


def log_sweep(entries, path=SWEEP_JSON):
    old = json.load(open(path)) if os.path.exists(path) else []
    for e in entries: e["k"] = len(old); old.append(e)
    json.dump(old, open(path + ".tmp", "w"), indent=0); os.replace(path + ".tmp", path)


def sweep(B, D, dist_label, n_per_axis=14, batch=12, seed=0, log=print):
    rng = np.random.default_rng(seed); cfgs = []
    for ax in AXES: cfgs += sample_geometry(ax, rng, n_per_axis)
    return run_list(cfgs, B, D, dist_label, batch, log)


def run_list(cfgs, B, D, dist_label, batch=12, log=print):
    allr = []
    for b0 in range(0, len(cfgs), batch):
        part = cfgs[b0:b0 + batch]; res, _ = run_batch(part, B, D=D, log=log)
        ent = [dict(t=now(), params=p, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"], follow=r["follow"], contact=r["contact"],
                    gap=r["gap"], pct=r.get("pct"), dist=dist_label, diag=r.get("diag"), r_ring=r.get("r_ring")) for p, r in zip(part, res)]
        log_sweep(ent); allr += ent
        bb = min(ent, key=lambda e: e["gap"]); log(f"  {b0 + len(part)}/{len(cfgs)}  batch best gap {bb['gap']}  {json.dumps(bb['params'])}")
    return allr


def refine(best, rng, n):
    out = []
    for _ in range(n):
        p = dict(best)
        for k, sc in (("rho_A", 6), ("r_C", 4), ("lam", 0.05), ("mu", 0.08), ("phi_C", 6), ("gamma0", 6), ("ring_l", 10), ("rail_arc", 10), ("u_plane", 6), ("u_elev", 6)):
            if rng.random() < 0.6: p[k] = round(float(p[k] + rng.normal(0, sc)), 2)
        p["lam"] = float(np.clip(p["lam"], 0.2, 0.85)); p["rail_arc"] = float(np.clip(p["rail_arc"], 180, 250)); out.append(p)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    nc = int(a[a.index("--n-clip") + 1]) if "--n-clip" in a else (20 if "--quick" in a else 60)
    nw = int(a[a.index("--n-ws") + 1]) if "--n-ws" in a else (40 if "--quick" in a else 160)
    B = CB.Bench(nc, nw); print("bench", B.mode, len(B.poses), flush=True)
    if "--sweep" in a or "--refine" in a:
        store = a[a.index("--approx") + 1] if "--approx" in a else None
        D = ApproxSkin(B, store=store) if store else None; label = "approx-screen" if store else "bench-" + B.mode
        if "--sweep" in a:
            sweep(B, D, label, n_per_axis=int(a[a.index("--n") + 1]) if "--n" in a else 14)
        if "--refine" in a:
            rows = [e for e in json.load(open(SWEEP_JSON)) if e["dist"] == label]; rows.sort(key=lambda e: e["gap"])
            rng = np.random.default_rng(len(rows)); cfgs = []
            for e in rows[:3]: cfgs += refine(e["params"], rng, 8)
            run_list(cfgs, B, D, label)
    elif "--verify" in a:                                    # re-measure the best screened configurations with the bench's distance
        rows = [e for e in json.load(open(SWEEP_JSON)) if e["dist"].startswith("approx")]; rows.sort(key=lambda e: e["gap"])
        top = int(a[a.index("--verify") + 1]); run_list([e["params"] for e in rows[:top]], B, None, "bench-" + B.mode, batch=top)
    else:
        r = evaluate(PARAMS, B); print(json.dumps(r))

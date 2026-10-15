"""rus-tripod-gh-centre: a 3-RUS tripod that uses the wearer's own GH as the spherical centre (concept screen).

Topology (docs/concepts/catalogue.json, id rus-tripod-gh-centre). Scapula frame S (the user's scapula handler) ->
three legs in parallel -> humerus H; there is no exo joint at GH, the anatomical GH closes the loop:
    S -> base frame (three O20 v5 hub lower plates + 12 x 3 Ti brackets on the scapula skin)
      -> ACTIVE R: crank hub i (O20 v5, axis n_i near the skin normal, NOT through GH), crank radius rc_i
      -> passive U at the crank tip (miniature cardan, keep-out sphere O12; 1st axis = n_i, 2nd = n_i x chord)
      -> rigid curved strut i (Ti tube O6, chord L_i, bent away from the body in the plane of n_i and the chord)
      -> passive S (ball O8-10 in a cup O14 x 10 = a 14 mm boss on the arm strip; or a cardan + spin bearing)
      -> arm strip (14 x 3 Ti, arm-fixed, from BOTTOM's bar to the three ball bosses) -> H.
DOF: each R-U-S leg has 6 joint DOF and imposes one constraint |c_i(phi_i) - b_i| = L_i; GH removes the arm's three
translations, so the three crank angles set the three arm rotations. ACTIVE 3 (the cranks), PASSIVE 15 (3 x (U 2 +
S 3)), every passive coordinate set by the closure (the U blocks the strut's spin about its chord, so a curved strut
cannot swing round; the S spin is the only idle coordinate and it is the strut's spin about its own chord axis at
the ball, which is fixed by the U at the other end - no sag).

Model (thorax mm, GH = origin; S / H rotations = B.frames(i)['S'][0] / ['H'][0], which equal the pose file's RS and
RS @ HG @ RH^T - the arm frame used here (a, z_L, y_L) is the band evaluator's HG frame, the one BOTTOM's bar is
defined in):
  * K1 legs (closed form, residual 0): P = Rs P_i (crank centre on the hub axis at the U-centre level), n = Rs n_i,
    Bv = Rh b_i; X = Bv - P; rhs = (rc^2 + |X|^2 - L^2) / (2 rc rho_xy); |rhs| > 1 -> no closure;
    phi = atan2(y, x) + br acos(rhs); crank tip c; chord e_s = (Bv - c) / L.
  * K2 validity per pose: closure on all three legs; crank-strut angle >= 15 deg from collinear (dead centre);
    U bend (chord elevation out of the crank plane) within +-U_LIM of its mid-range; ball: chord direction in the
    arm frame within BALL_LIM of the socket axis (the axis = the centre of the smallest cone over the fit poses);
    Type-II conditioning sigma_min([B_i x e_i]) / 100 mm >= 0.15 (spec); along each fit clip at the pose file's full
    rate (10 fps) no crank / U / ball angle jumps > 30 deg between consecutive frames (a jump = a frame not followed).
  * K3 parts at their real size (details in the .md): O20 v5 hubs (lower plate skin face F, upper member F + 3.15,
    crown F + 12.25, disc r 10), crank plate 12 wide x 4 from the hub to the U boss, optionally dished toward the skin
    by `dip` deg; U keep-out sphere O12; strut O6 tube; ball boss O14 at the arm strip; arm strip 14 x 3 from BOTTOM's
    bar to each ball; base brackets 12 x 3 joining the hubs (S-fixed).
  * K4 rigid-part fits (EF): every rigid part's skin-facing shape is fixed in the part's own frame and fitted as the
    quantile q (S / H-fixed parts: q = 1, they ride stable skin) of the per-pose requirement + 2 mm clearance; poses
    above the quantile show up as contact. Struts: the bulge h(t) along v_out (the component of n perpendicular to the
    chord, i.e. in the strut frame - the spec's "rays from GH" would deform a rigid strut pose by pose; corrected).
  * K5 self-collision (>= 1 mm between non-adjacent parts): strut-strut, strut-other crank / hub / ball boss,
    crank-crank, crank-other hub, crank-bracket.
  * scored metal (bench in-band): skin-facing samples on a ~2 mm grid (1 point / 4 mm2) of every part (hub lower
    discs, crank undersides, strut underside lanes, ball bosses, arm strip, brackets). Contact-only: U spheres, hub
    crowns, cup tops.

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/rus-tripod-gh-centre.py kin      # kinematic screen
    ... rus-tripod-gh-centre.py check     # a few poses on the bench, diagnostics
    ... rus-tripod-gh-centre.py sweep     # Bench(60, 160) sweep -> sweeps/<id>.json, rows/<id>.json
"""
import json, math, os, sys, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                  # noqa: E402
BP = CB.BP

ID = "rus-tripod-gh-centre"
NAME = "3-RUS tripod that uses the wearer's own GH as the spherical centre"
D2R = math.pi / 180
HUB_R, HUB_UP, HUB_TOP = 10.0, 3.15, 12.25          # O20 v5 hub
CR_W, CR_T = 12.0, 4.0                                # crank plate
U_R = 6.0                                             # U keep-out sphere O12
H_U = HUB_UP + U_R                                    # U centre above F (flat crank)
ST_R = 3.0                                            # strut tube O6
CUP_R = 7.0                                           # ball boss / cup O14
AS_W, AS_T = 14.0, 3.0                                # arm strip
BR_W, BR_T = 12.0, 3.0                                # base brackets
SP = 2.0                                              # sample spacing
CLR = 2.0                                             # fit clearance
GAP = 1.0                                             # min distance between non-adjacent parts
FLIP = 30.0                                           # deg per frame (10 fps)
DEAD = 15.0                                           # crank-strut angle off collinear, deg
SIG = 0.15                                            # sigma_min / 100 mm
U_LIM, BALL_LIM = 40.0, 40.0                          # cardan half-range about its mid, ball cone half-angle (deg)
WB = np.array([0.0, -0.0713, 0.9975]); WB /= np.linalg.norm(WB)              # BOTTOM's bar (evaluator HG frame)
DB = np.array([0.0, -0.9975, -0.0713]); DB = DB - (DB @ WB) * WB; DB /= np.linalg.norm(DB)
ZBAR, DBAR0, DBAR1, BAR_HW, BAR_T = 67.5, 40.0, 200.0, 16.0, 6.5

# legs: site (lat, lon) S-local, tilt of the crank axis from the outward skin normal (deg, azimuth deg), rc, dip (deg),
# ball (s, th), standoff over the arm strip (mm, >= CUP_R), branch, L (None = best for closure)
PARAMS = dict(
    legs=[dict(site=(66.0, -68.0), tilt=(0.0, 0.0), rc=40.0, ball=(150.0, 0.0), br=1, L=None),
          dict(site=(0.0, -112.0), tilt=(0.0, 0.0), rc=40.0, ball=(120.0, 70.0), br=1, L=None),
          dict(site=(50.0, 10.0), tilt=(0.0, 0.0), rc=40.0, ball=(110.0, -70.0), br=1, L=None)],
    dip=0.0, standoff=CUP_R, q=0.95, nst=16)
SWEEP = dict(site_dome=((50, 80), (-100, -40)), site_post=((-10, 10), (-125, -100)), site_acro=((40, 60), (-10, 30)),
             tilt=((0, 40), (0, 360)), rc=(20, 55), ball_s=(80, 180), ball_th=(-90, 90), standoff=(7, 12), br=(-1, 1),
             q=(0.85, 1.0), dip=(0, 20))


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def dS(lat, lon):
    la, lo = lat * D2R, lon * D2R
    return np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)])


def perp(u):
    a = np.array([1.0, 0.0, 0.0]) if abs(u[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = unit(a - (a @ u) * u); return e1, np.cross(u, e1)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------------------------------------ arm frame
_L = BP._rig().L
RH = np.array(_L["rest_humerus"])
A_AX = unit(np.array(_L["elbow"], float))                                   # humerus axis (bind coords)
Z_L = unit(RH @ np.array([0.0, 0.0, 1.0]) - (RH @ np.array([0.0, 0.0, 1.0]) @ A_AX) * A_AX)   # lateral
Y_L = np.cross(A_AX, Z_L)                                                    # posterior


def arm_dir(th):
    return math.cos(th * D2R) * Z_L + math.sin(th * D2R) * Y_L


def arm_pt(s, th, rho):
    return s * A_AX + rho * arm_dir(th)


def bar_pts(step=4.0):
    """BOTTOM's bar underside centre line in bind coords"""
    d = np.arange(DBAR0, DBAR1 + 1e-6, step)
    return (RH @ (ZBAR * WB[:, None] + DB[:, None] * d[None])).T


# ------------------------------------------------------------------------------------------------ pose data
class Poses:
    """Rs, Rh for the bench poses and for every frame of the fit clips (full rate) + the map bench -> clip frames"""
    def __init__(self, B):
        self.B = B; Z = CB._poses_all(); r = BP._rig()
        n = len(B.poses); self.Rs = np.empty((n, 3, 3)); self.Rh = np.empty((n, 3, 3))
        for i in range(n):
            f = B.frames(i); self.Rs[i] = f["S"][0]; self.Rh[i] = f["H"][0]
        names = list(Z["NAMES"]); fit = [names.index(c) for c in CB.FIT]
        self.cidx = np.nonzero(np.isin(Z["CID"], fit))[0]                    # every fit-clip frame (file order)
        self.cid = Z["CID"][self.cidx]; m = len(self.cidx)
        self.cRs = np.empty((m, 3, 3)); self.cRh = np.empty((m, 3, 3))
        for k, j in enumerate(self.cidx):
            p = Z["POSE"][j]; pose = dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4]))
            (T, S, H, Fa, Pr), lift = BP.segs(r.L, r.s, pose); self.cRs[k] = S[0]; self.cRh[k] = H[0]
        pos = {int(j): k for k, j in enumerate(self.cidx)}
        self.bench2c = np.array([pos.get(int(j), -1) for j in B.idx])        # bench index -> full-rate clip frame (or -1)
        self.ws = np.array([k == "ws" for k in B.kind]); self.cl = ~self.ws


# ------------------------------------------------------------------------------------------------ skin rays
def ray_skin(dist, O, D, r0=20.0, r1=170.0, step=5.0, nb=4):
    """outermost crossing (inside -> outside) along rays O + r D, r in [r0, r1] (O (m, 3) or (3,), D (m, 3)):
    5 mm ladder of the signed distance + nb bisection steps; nan if the ray never leaves the body"""
    D = np.asarray(D, float); O = np.broadcast_to(np.asarray(O, float), D.shape)
    rr = np.arange(r0, r1 + 1e-6, step); X = O[:, None] + rr[None, :, None] * D[:, None]
    d = dist(X.reshape(-1, 3)).reshape(len(D), len(rr))
    ins = d < 0; out = np.full(len(D), np.nan)
    last = np.where(ins.any(1), len(rr) - 1 - np.argmax(ins[:, ::-1], 1), -1)  # last inside sample
    ok = (last >= 0) & (last < len(rr) - 1)
    lo = rr[np.clip(last, 0, len(rr) - 1)].copy(); hi = lo + step
    for _ in range(nb):
        mid = (lo + hi) / 2; dm = dist((O + mid[:, None] * D)).reshape(-1)
        lo = np.where(dm < 0, mid, lo); hi = np.where(dm < 0, hi, mid)
    out[ok] = ((lo + hi) / 2)[ok]
    out[last < 0] = r0                                                       # never inside on the ladder
    return out


# ------------------------------------------------------------------------------------------------ kinematics
def leg_kin(P0, n0, rc, b0, L, br, Rs, Rh):
    """one leg over N poses: S-local crank centre P0 (3,), axis n0, rc, arm point b0 (bind coords), chord L, branch.
    -> dict of (N, ...) arrays; ok = closure"""
    e10, e20 = perp(n0)
    P = Rs @ P0; n = Rs @ n0; e1 = Rs @ e10; e2 = Rs @ e20; Bv = Rh @ b0
    X = Bv - P; x = (X * e1).sum(-1); y = (X * e2).sum(-1); rho = np.hypot(x, y)
    rhs = (rc ** 2 + (X * X).sum(-1) - L ** 2) / (2 * rc * np.maximum(rho, 1e-9))
    ok = np.abs(rhs) <= 1
    phi = np.arctan2(y, x) + br * np.arccos(np.clip(rhs, -1, 1))
    rh_ = np.cos(phi)[:, None] * e1 + np.sin(phi)[:, None] * e2
    c = P + rc * rh_; es = (Bv - c) / L
    dead = np.arccos(np.clip(np.abs((es * rh_).sum(-1)), 0, 1)) / D2R       # crank-strut angle off collinear
    uel = np.arcsin(np.clip((es * n).sum(-1), -1, 1)) / D2R                # chord elevation out of the crank plane
    uaz = np.arctan2((es * np.cross(n, rh_)).sum(-1), (es * rh_).sum(-1)) / D2R   # chord azimuth vs the crank
    darm = np.einsum("nji,nj->ni", Rh, -es)                                  # ball -> crank, arm frame (bind coords)
    return dict(P=P, n=n, e1=e1, e2=e2, Bv=Bv, phi=phi, c=c, es=es, ok=ok, dead=dead, uel=uel, uaz=uaz, darm=darm, rhs=rhs, r=rh_)


def min_cone(D, iters=60):
    """approximate centre of the smallest cone holding unit vectors D (m, 3): (axis, half-angle deg)"""
    if not len(D): return np.array([0, 0, 1.0]), 0.0
    c = unit(D.mean(0))
    for k in range(iters):                                                   # Badoiu-Clarkson on the sphere
        j = np.argmin(D @ c); c = unit(c + (D[j] - c) / (k + 2))
    return c, float(np.degrees(np.arccos(np.clip((D @ c).min(), -1, 1))))


def best_L(Rs, Rh, P0, n0, rc, b0, mask):
    """chord length maximising the share of mask poses with closure and >= DEAD margin (scan)"""
    Bv = np.einsum("nij,j->ni", Rh, b0); P = np.einsum("nij,j->ni", Rs, P0); dmin = np.linalg.norm(Bv - P, axis=1)
    lo, hi = np.percentile(dmin[mask], 2), np.percentile(dmin[mask], 98)
    best = (-1, None)
    for L in np.linspace(max(lo - rc, 20), hi + rc, 60):
        k1 = leg_kin(P0, n0, rc, b0, L, 1, Rs[mask], Rh[mask]); s = np.mean(k1["ok"] & (k1["dead"] >= DEAD))
        if s > best[0]: best = (s, L)
    return best[1]


def L_interval(Rs, Rh, P0, n0, rc, b0):
    """per pose the chord-length interval with closure: [|X|-ish min, max] for the crank angle range (N, 2)"""
    e10, e20 = perp(n0)
    P = Rs @ P0; e1 = Rs @ e10; e2 = Rs @ e20; Bv = Rh @ b0; X = Bv - P
    rho = np.hypot((X * e1).sum(-1), (X * e2).sum(-1)); X2 = (X * X).sum(-1)
    return np.sqrt(np.maximum(rc ** 2 + X2 - 2 * rc * rho, 0)), np.sqrt(rc ** 2 + X2 + 2 * rc * rho)


def pick_L(lo, hi, w, margin):
    """chord length maximising the weighted count of poses with lo + margin <= L <= hi - margin"""
    a, b = lo + margin, hi - margin; cand = np.unique(np.r_[a, b])
    if not len(cand): return float(np.median((lo + hi) / 2))
    cnt = ((cand[:, None] >= a[None]) & (cand[:, None] <= b[None])) @ w
    k = np.argmax(cnt); best = cand[cnt >= cnt[k] - 1e-9]
    return float(np.median(best))


def window(x, width, w=None):
    """centre of the window of the given width holding the most of x (weights w)"""
    if not len(x): return 0.0
    xs = np.sort(x); j = np.searchsorted(xs, xs + width, side="right") - np.arange(len(xs)); k = int(np.argmax(j))
    return float(xs[k] + width / 2)

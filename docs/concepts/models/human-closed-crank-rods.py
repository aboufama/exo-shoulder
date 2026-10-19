"""human-closed-crank-rods: three dome cranks and three thin rods to arm studs, the user's own GH joint closing the
loop (a 3-RUS truss), concept screen on tools/concept_bench.py.

Topology (docs/concepts/catalogue.json, id human-closed-crank-rods):
    S (scapula handler) -> 3 crank hubs on the dome (ACTIVE revolutes, O20 v5; axes c_k through GH, fixed in S, joined
    by S-fixed base brackets) -> crank (K5 strap, arc beta) -> crank-tip U-joint at T_k (passive, 2: a swivel about the
    radial at T + a pitch pin; O12 housing) -> O5 Ti rod (rigid, its shape fitted, see below) -> ball stud at Q_k
    (passive, 3; O12 rod-end housing) on an arm-fixed saddle (t 4, joined to the user's BOTTOM bar) -> humerus H.
    The exo has no joint at GH: the human glenohumeral joint closes the loop.
DOF: 3 ACTIVE (the crank angles; the only coordinates sensed / driven) + 15 PASSIVE (2 U + 3 ball per leg). Given the
    arm's pose every passive coordinate is set by it (|T(theta) - Q| = L on a fixed branch; the U kills the rod spin),
    so nothing is an undriven spare. With the arm free (6 DOF) the three legs each impose one constraint once the cranks
    are fixed; on the bench GH is fixed in S, so the arm's 3 rotations <-> the 3 crank angles (exactly 3 DOF).

Bench-exact observation (stated in docs/concepts/human-closed-crank-rods.md): with GH fixed, |T| (crank-tip radius),
|Q| (arm stud radius) and L are constant, so the triangle GH-T-Q is RIGID: each rod is a body rotating about GH, the
U-joint acts as a revolute about OT (its pitch stays constant) and the ball as a revolute about OQ. On the bench the
truss is therefore a spherical 3-RRR parallel mechanism (the SPM family) whose distal links are thin rods reaching
far down the arm; its extra passive freedoms only absorb GH translation (off the bench).

Model (thorax mm, origin GH; RS / RH = B.frames(i)['S' / 'H'][0]; full-rate clip frames from the pose file with the
same frames: RH = RS @ HG @ C, C the constant offset measured on the bench):
  * crank k: tip T = r_T (cos beta c + sin beta (cos th e1 + sin th e2)) (S-frame basis, then RS). Closed form IK:
    A cos th + B sin th = C (catalogue model_spec), branch sigma_k fixed per design.
  * rod length L_k (SPEC FIX): the spec took L at the rest pose with the crank pointing at the stud - that is the
    crank's DEAD CENTRE (|T - Q| stationary), so every leg would start singular. Here L_k is the value that maximises
    the share of bench poses whose closure exists with transmission >= 15 deg on the leg's branch (interval stabbing,
    clip frames weighted 1/n_clip, workspace 1/n_ws).
  * transmission (SPEC FIX): the dead centre is the rod PERPENDICULAR to the tip velocity dT/dth (then the rod force
    makes no crank torque and the two branches meet), so the check is |cos angle(dT/dth, rod)| >= sin 15 deg (the
    spec's |sin| < sin 15 rejected the good, aligned case).
  * conditioning: |det[unit(T_k x Q_k)]| >= det (spec: the rods' moment lines about GH).
  * parts at their real size, every rigid part's skin-facing face fitted per K3 (march along a line: the first t with
    B.dist >= clear and >= 0 over the next 15 mm; percentile p over the kinematically valid bench poses):
      - O20 v5 hubs: flat disc r 10, lower face F_k along c_k (K4); stack 12.25 to the crown (contact-only rim / crown);
      - base brackets (SPEC ADDITION, the spec left the three hubs unconnected): 12 x 3 S-fixed straps on the two
        shortest great-circle edges between the hubs (the hubs' lower members, underside F at each hub);
      - cranks: K5 strap 12 x 3 from the hub (underside F + 3.15 over the hub disc) along the arc beta, 6 mm past T;
        K3 in the crank frame (S rotated by th_k about c_k), 60 deg ramp limit; r_T = crank tip underside + 3 + 6 + 1
        (the U housing r 6 rides on the strap: catalogue 'K3 requirement + 10'), iterated with the IK (3 passes);
      - rods: O5 tubes. The rod's frame (chord T -> Q, the in-plane outward normal, the plane normal) is rigid (see
        above; off the bench the U's first axis radial at T keeps the bow plane through GH), so its centreline offset
        y(x) from the chord is K3-fitted along the in-plane normal (SPEC IMPROVEMENT over the spec's circular bow of
        sagitta h: the fitted bow is the lowest rigid rod that clears the skin; bow='arc' keeps the spec's arc), with a
        60 deg slope limit from both joint ends (the rod passes through T and Q). Skin-facing samples: 4 points on the
        lower half circumference every 2 mm (1 point / 4 mm2), excluding the 6 mm inside each housing; top half
        contact-only;
      - joints: U housing sphere r 6 at T (on the crank tip, covered by the strap) and rod-end housing r 6 at Q on a
        stud (r 7 disc) on the saddle - contact-only (their skin side is covered by the strap / saddle);
      - arm saddle (t 4, 14 wide): H-fixed straps around the arm at the stud level from the BOTTOM bar (theta 0) to each
        saddle stud (+7 mm), K3-fitted along horizontal rays from the humerus axis (the arm's normal; rays from GH are
        ~60 deg oblique there) over all bench poses; ball centre Q = saddle top + h_stud. Leg 1's stud sits on BOTTOM
        (q1 = (67.5 + h1) Wb + s1 Db, catalogue K7), BOTTOM itself is the user's part (not scored).
  * taken iff: closure on the design branch; transmission and conditioning; no two non-adjacent parts closer than 1 mm
    (point clouds with their half-thicknesses; joint partners exempt within hub radius + 2 / housing radius + 3 mm of
    their joint; BOTTOM's bar (14 x 6, from 40 mm down) counted as an obstacle for the rods); along each fit clip at its
    full 10 fps no joint value (crank, U swivel, ball spin) jumps > 25 deg between kinematically valid frames (K2); then
    the bench's contact rule on every metal sample (contact-only samples add their deepest point when inside).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/human-closed-crank-rods.py check [n_clip n_ws]
    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/human-closed-crank-rods.py sweep       # Bench(60, 160)
"""
import copy, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "human-closed-crank-rods"
NAME = "Human-closed 3-RUS truss: dome cranks and thin rods to arm studs"
D2R = math.pi / 180
HUB_R, HUB_UP, HUB_TOP, PLATE_T = 10.0, 3.15, 12.25, 3.0      # O20 v5 (docs/HARDWARE.md)
CR_W, CR_T = 12.0, 3.0                                        # crank strap (K5)
BR_W, BR_T = 12.0, 3.0                                        # base bracket strap
ROD_R = 2.5                                                   # O5 tube
UJ_R, BALL_R, STUD_R = 6.0, 6.0, 7.0                          # O12 housings, stud disc
SAD_W, SAD_T = 14.0, 4.0                                      # arm saddle plate
BAR_W, BAR_T, BAR_Z, BAR_S0 = 14.0, 6.0, 67.5, 40.0           # BOTTOM bar (user part, obstacle only)
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713])
SP = 2.0                                                      # sample spacing (1 point / 4 mm2)
GAP = 1.0                                                     # clearance between non-adjacent parts
CLIMB = math.tan(60 * D2R)
FLIP = 25.0                                                   # K2 deg between consecutive valid 10 fps frames

PARAMS = dict(hubs=[[60.0, 75.0], [-10.0, 40.0], [150.0, 40.0]],   # crank hub axes (az, el) in S (bvec)
              beta=[35.0, 35.0, 35.0],                              # crank arc (deg)
              sigma=[1, 1, 1],                                      # IK branch per leg
              s1=80.0, h1=8.0,                                      # leg 1 stud on BOTTOM: s1 down the bar, ball centre h1 over the bar underside
              studs=[[110.0, 45.0], [100.0, -15.0]],                # legs 2, 3: (s mm down the arm, theta deg about it, + posterior)
              h_stud=7.0,                                           # ball centre over the saddle top (mm)
              p=100.0, clear=2.0, trans=15.0, det=0.10, bow="fit", sag=0.0, dL=[0.0, 0.0, 0.0])
SWEEP = dict(hub_az_el="3 x (az, el) around the spec's dome points", beta=(20, 45), sigma="8 sign triples",
             s1=(60, 120), studs="s 60-170, theta -20..+62", h_stud=(5, 12), p=(80, 100), clear=(2, 3), bow=("fit", "arc"))


def bvec(az, el):
    a, e = az * D2R, el * D2R
    return np.array([-math.cos(e) * math.cos(a), math.sin(e), math.cos(e) * math.sin(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def perp(u):
    a = np.array([0.0, 0.0, 1.0]) if abs(u[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = unit(a - (a @ u) * u); return e1, np.cross(u, e1)


def wrapd(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def env60(y, s):
    """upper Lipschitz envelope of a profile y over arc length s (slope <= tan 60): the strap cannot kink faster"""
    y = np.asarray(y, float); out = y.copy()
    for j in range(len(y)):
        out = np.maximum(out, y[j] - CLIMB * np.abs(s - s[j]))
    return out


# ------------------------------------------------------------------------------------------------ bench context
class Ctx:
    """bench + rotations of every bench pose and of every full-rate (10 fps) fit-clip frame"""
    def __init__(self, B):
        self.B = B; n = len(B.poses); self.n = n
        self.RS = np.stack([B.frames(i)["S"][0] for i in range(n)]); self.RH = np.stack([B.frames(i)["H"][0] for i in range(n)])
        self.clip = np.array([k == "clip" for k in B.kind]); self.nc = int(self.clip.sum()); self.nw = n - self.nc
        Z = CB._poses_all(); names = list(Z["NAMES"]); j0 = B.idx[0]
        C = (Z["RS"][j0] @ Z["HG"][j0]).T @ self.RH[0]
        fit_ids = [names.index(c) for c in CB.FIT]
        self.fclips = []                                                   # [(name, full-rate Z indices in time order)]
        for c in fit_ids:
            ix = np.nonzero(Z["CID"] == c)[0]; ix = ix[np.argsort(Z["FI"][ix])]; self.fclips.append((names[c], ix))
        fidx = np.concatenate([ix for _, ix in self.fclips]); self.fidx = fidx
        self.fRS = Z["RS"][fidx].astype(float); self.fRH = Z["RS"][fidx].astype(float) @ Z["HG"][fidx].astype(float) @ C
        pos = {int(z): j for j, z in enumerate(fidx)}
        self.bench_to_full = np.array([pos.get(int(B.idx[i]), -1) for i in range(n)])
        self.w = np.where(self.clip, 1.0 / max(self.nc, 1), 1.0 / max(self.nw, 1))

    def dist(self, I, P):
        """signed distance of points P (len(I), m, 3) in poses I"""
        out = np.empty(P.shape[:-1])
        for a, i in enumerate(I): out[a] = self.B.dist(int(i), P[a])
        return out

    def march(self, I, base, dirs, t0, t1=220.0, clear=2.0, look=15.0, it=80):
        """K3 requirement: per pose I[a] and line (base, dir) (len(I), m, 3): the first t >= t0 with dist >= clear and
        dist >= 0 over [t, t + look]; t1 if none (sphere tracing with the 1-Lipschitz signed distance)"""
        n, m = base.shape[:2]; t = np.full((n, m), float(t0)); ph = np.zeros((n, m), np.int8); ts = t.copy(); act = np.ones((n, m), bool)
        for _ in range(it):
            if not act.any(): break
            for a in range(n):
                ka = np.nonzero(act[a])[0]
                if not len(ka): continue
                P = base[a, ka] + t[a, ka, None] * dirs[a, ka]; d = self.B.dist(int(I[a]), P)
                p0 = ph[a, ka] == 0
                # phase 0: looking for dist >= clear
                hit = p0 & (d >= clear); ts[a, ka[hit]] = t[a, ka[hit]]; ph[a, ka[hit]] = 1
                st0 = p0 & ~hit; t[a, ka[st0]] += np.maximum(clear - d[st0], 0.5)
                # phase 1: verify >= 0 over [ts, ts + look]
                p1 = ~p0
                bad = p1 & (d < 0); ph[a, ka[bad]] = 0; t[a, ka[bad]] += np.maximum(clear - d[bad], 0.5)
                good = p1 & ~bad; t[a, ka[good]] += np.maximum(d[good], 0.5)
                done = good & (t[a, ka] > ts[a, ka] + look); act[a, ka[done]] = False
                # newly found (phase 1) lines step from ts: do it now
                st1 = hit; t[a, ka[st1]] += np.maximum(d[st1], 0.5)
                over = t[a, ka] > t1; act[a, ka[over & (ph[a, ka] == 0)]] = False
        res = np.where(ph == 1, ts, t1)
        return res


# ------------------------------------------------------------------------------------------------ kinematics
def kin(D, RS, RH, trans_deg=15.0):
    """per pose: theta (n,3) rad, T, Q (n,3,3), leg validity (n,3), transmission (n,3), det (n,), U swivel, ball spin (deg)"""
    n = len(RS); th = np.zeros((n, 3)); T = np.zeros((n, 3, 3)); Q = np.zeros((n, 3, 3)); okk = np.zeros((n, 3), bool)
    tr = np.zeros((n, 3)); sw = np.zeros((n, 3)); spn = np.zeros((n, 3))
    for k in range(3):
        c = RS @ D["c"][k]; e1 = RS @ D["e1"][k]; e2 = RS @ D["e2"][k]; b = D["beta"][k] * D2R; rT = D["rT"][k]
        O = rT * math.cos(b) * c; rho = rT * math.sin(b); q = RH @ D["q"][k]; OQ = O - q
        A = 2 * rho * (e1 * OQ).sum(-1); Bc = 2 * rho * (e2 * OQ).sum(-1); Cc = D["L"][k] ** 2 - (OQ * OQ).sum(-1) - rho ** 2
        Rr = np.hypot(A, Bc) + 1e-12; ratio = Cc / Rr; cl = np.abs(ratio) <= 1.0
        t = np.arctan2(Bc, A) + D["sigma"][k] * np.arccos(np.clip(ratio, -1, 1))
        Tk = O + rho * (np.cos(t)[:, None] * e1 + np.sin(t)[:, None] * e2)
        v = unit(np.cross(c, Tk)); rod = unit(q - Tk); trk = np.abs((v * rod).sum(-1))
        th[:, k] = t; T[:, k] = Tk; Q[:, k] = q; tr[:, k] = trk; okk[:, k] = cl & (trk >= math.sin(trans_deg * D2R))
        # U swivel: rod direction about the radial at T, from the crank's tip tangent (away from the hub)
        rT_u = unit(Tk); tg = unit(np.cross(np.cross(c, Tk), Tk)) * -1.0       # tangent at T pointing away from c
        tg = unit(Tk - c * (Tk * c).sum(-1, keepdims=True) * 0) ; tg = unit(np.cross(rT_u, np.cross(c, rT_u)))
        tg = -tg                                                                 # away from the hub axis
        b2 = np.cross(rT_u, tg); sw[:, k] = np.degrees(np.arctan2((rod * b2).sum(-1), (rod * tg).sum(-1)))
        # ball spin: rod direction about OQ in the humerus frame
        rodH = np.einsum("nji,nj->ni", RH, -rod); qh = unit(D["q"][k]); f1, f2 = perp(qh)
        spn[:, k] = np.degrees(np.arctan2(rodH @ f2, rodH @ f1))
    M = unit(np.cross(T, Q)); det = np.abs(np.linalg.det(M))
    return dict(th=th, T=T, Q=Q, okk=okk, tr=tr, det=det, sw=sw, spn=spn)


def stab_L(c, e1, e2, beta, rT, q, sigma, RS, RH, w, trans_deg, Lgrid=None):
    """rod length maximising the weighted share of poses with closure and transmission >= trans on the branch"""
    b = beta * D2R; cc = RS @ c; E1 = RS @ e1; E2 = RS @ e2; O = rT * math.cos(b) * cc; rho = rT * math.sin(b); Q = RH @ q
    OQ = O - Q; A = 2 * rho * (E1 * OQ).sum(-1); Bc = 2 * rho * (E2 * OQ).sum(-1); base = (OQ * OQ).sum(-1) + rho ** 2
    dmin = np.sqrt(np.maximum(base - np.hypot(A, Bc), 0)); dmax = np.sqrt(base + np.hypot(A, Bc))
    if Lgrid is None: Lgrid = np.arange(math.floor(dmin.min()), math.ceil(dmax.max()) + 1, 1.0)
    Cc = Lgrid[:, None] ** 2 - base[None]; Rr = np.hypot(A, Bc)[None] + 1e-12; ratio = Cc / Rr
    t = np.arctan2(Bc, A)[None] + sigma * np.arccos(np.clip(ratio, -1, 1))
    Tk = O[None] + rho * (np.cos(t)[..., None] * E1[None] + np.sin(t)[..., None] * E2[None])
    v = unit(np.cross(cc[None], Tk)); rod = unit(Q[None] - Tk); trk = np.abs((v * rod).sum(-1))
    ok = (np.abs(ratio) <= 1) & (trk >= math.sin(trans_deg * D2R)); sc = (ok * w[None]).sum(1)
    best = sc.max(); j = np.nonzero(sc >= best - 1e-9)[0]; j = j[len(j) // 2]
    return float(Lgrid[j]), float(best)


# ------------------------------------------------------------------------------------------------ design (fitting)
def arc_dirs(c, e, alphas, across, r_ref):
    """directions on the great circle c -> e (unit, e perpendicular to c) at angles alphas, offsets across (mm at r_ref)"""
    nrm = np.cross(c, e)
    D = np.cos(alphas)[:, None] * c + np.sin(alphas)[:, None] * e
    return unit(D[:, None, :] + (np.asarray(across) / r_ref)[None, :, None] * nrm[None, None, :])     # (ns, nc, 3)


def build(params, X, log=None):
    """fit every rigid part to the bench (X: Ctx) and solve the kinematics; returns the design dict"""
    P = dict(PARAMS); P.update(params or {}); B = X.B; n = X.n; clear = P["clear"]; pct = P["p"]
    D = dict(P=P, c=[], e1=[], e2=[], beta=list(P["beta"]), sigma=list(P["sigma"]))
    for az, el in P["hubs"]:
        c = bvec(az, el); e1, e2 = perp(c); D["c"].append(c); D["e1"].append(e1); D["e2"].append(e2)
    allI = np.arange(n)
    # ---- arm saddle and studs (H-fixed, over all bench poses)
    sad = []; q = [P["h1"] * WB + BAR_Z * WB + P["s1"] * DB]
    q[0] = (BAR_Z + P["h1"]) * WB + P["s1"] * DB
    for s, thd in P["studs"]:
        th0 = thd * D2R; ext = (STUD_R + 1.0) / 50.0
        lo, hi = min(0.0, th0) - ext, max(0.0, th0) + ext
        ths = np.linspace(lo, hi, max(3, int(round((hi - lo) * 52 / SP)) + 1)); ys = -s + np.arange(-SAD_W / 2 + 1, SAD_W / 2, SP)
        TH, Y = np.meshgrid(ths, ys, indexing="ij")
        nH = np.stack([-np.sin(TH), np.zeros_like(TH), np.cos(TH)], -1).reshape(-1, 3); bH = np.stack([0 * TH, Y, 0 * TH], -1).reshape(-1, 3)
        base = np.einsum("nij,mj->nmi", X.RH, bH); dirs = np.einsum("nij,mj->nmi", X.RH, nH)
        req = X.march(allI, base, dirs, 15.0, 160.0, clear)
        rho = np.percentile(req, pct, axis=0)
        sad.append(dict(nH=nH, bH=bH, rho=rho, shape=TH.shape))
        # stud on the saddle at (s, theta): the saddle underside under the stud centre
        jj = np.argmin(np.abs(ths - th0)); rr = rho.reshape(TH.shape)[jj].max()
        nq = np.array([-math.sin(th0), 0.0, math.cos(th0)]); q.append(np.array([0.0, -s, 0.0]) + (rr + SAD_T + P["h_stud"]) * nq)
    D["q"] = q; D["sad"] = sad
    # ---- iterate hubs / brackets / cranks / r_T / L with the kinematic validity
    valid = np.ones(n, bool); rT = [None] * 3
    ccirc = np.linspace(0, 2 * math.pi, 24, endpoint=False)
    for k in range(3):                                                    # initial r_T: tip circle requirement
        b = D["beta"][k] * D2R; dS = unit(math.cos(b) * D["c"][k] + math.sin(b) * (np.cos(ccirc)[:, None] * D["e1"][k] + np.sin(ccirc)[:, None] * D["e2"][k]))
        dd = np.einsum("nij,mj->nmi", X.RS, dS); req = X.march(allI, 0 * dd, dd, 15.0, 220.0, clear)
        rT[k] = float(np.median(np.percentile(req, pct, axis=0))) + CR_T + UJ_R + 1.0
    D["rT"] = rT
    for it in range(3):
        I = np.nonzero(valid)[0]
        if len(I) < 5: I = allI
        # hubs: flat disc, lower face F along c (lines parallel to c)
        g = np.arange(-HUB_R, HUB_R + 1e-6, SP); GX, GY = np.meshgrid(g, g); kk = GX ** 2 + GY ** 2 <= HUB_R ** 2 + 1e-9
        GX, GY = GX[kk], GY[kk]; D["F"] = []; D["hub_xy"] = (GX, GY)
        for k in range(3):
            c, e1, e2 = D["c"][k], D["e1"][k], D["e2"][k]; bS = GX[:, None] * e1 + GY[:, None] * e2
            base = np.einsum("nij,mj->nmi", X.RS[I], bS); dirs = np.broadcast_to((X.RS[I] @ c)[:, None, :], base.shape).copy()
            req = X.march(I, base, dirs, 15.0, 220.0, clear); D["F"].append(float(np.percentile(req, pct, axis=0).max()))
        # brackets: the two shortest edges between hubs
        pairs = sorted([(math.acos(np.clip(D["c"][a] @ D["c"][b], -1, 1)), a, b) for a, b in ((0, 1), (0, 2), (1, 2))])[:2]
        D["br"] = []
        for ang, a, bb in pairs:
            ca, cb = D["c"][a], D["c"][bb]; e = unit(cb - (cb @ ca) * ca); Fm = 0.5 * (D["F"][a] + D["F"][bb])
            alphas = np.linspace(0, ang, max(3, int(ang * Fm / SP) + 1)); across = np.arange(-BR_W / 2, BR_W / 2 + 1e-6, SP)
            dS = arc_dirs(ca, e, alphas, across, Fm); ns, nc = dS.shape[:2]
            dd = np.einsum("nij,mj->nmi", X.RS[I], dS.reshape(-1, 3)); req = X.march(I, 0 * dd, dd, 15.0, 220.0, clear)
            prof = np.percentile(req, pct, axis=0).reshape(ns, nc).max(1)
            s = alphas * Fm
            ina = alphas * D["F"][a] < HUB_R; inb = (ang - alphas) * D["F"][bb] < HUB_R
            plate = np.where(ina, D["F"][a] / np.cos(alphas), np.where(inb, D["F"][bb] / np.cos(ang - alphas), -1e9))
            prof = env60(np.maximum(prof, plate), s)
            D["br"].append(dict(a=a, b=bb, alphas=alphas, across=across, e=e, ca=ca, rho=prof, score=~(ina | inb), Fm=Fm))
        # cranks: stations from the hub axis to beta + 6 mm past T, K3 in the crank frame
        for k in range(3): D.setdefault("L", [0.0] * 3)
        for k in range(3):
            D["L"][k], _ = stab_L(D["c"][k], D["e1"][k], D["e2"][k], D["beta"][k], D["rT"][k], D["q"][k], D["sigma"][k], X.RS, X.RH, X.w, P["trans"])
            D["L"][k] += P["dL"][k]
        K = kin(D, X.RS, X.RH, P["trans"]); valid = K["okk"].all(1) & (K["det"] >= P["det"])
        I = np.nonzero(valid)[0]
        if len(I) < 5: break
        D["cr"] = []
        for k in range(3):
            c, e1 = D["c"][k], D["e1"][k]; b = D["beta"][k] * D2R; r0 = D["rT"][k]
            alphas = np.linspace(0, b + 6.0 / r0, max(3, int((b * r0 + 6.0) / SP) + 1)); across = np.arange(-CR_W / 2, CR_W / 2 + 1e-6, SP)
            dS = arc_dirs(c, e1, alphas, across, r0); ns, nc = dS.shape[:2]
            Rk = crank_rot(D, k, K["th"][I, k], X.RS[I])
            dd = np.einsum("nij,mj->nmi", Rk, dS.reshape(-1, 3)); req = X.march(I, 0 * dd, dd, 15.0, 220.0, clear)
            prof = np.percentile(req, pct, axis=0).reshape(ns, nc).max(1)
            Fh = D["F"][k] + HUB_UP; onhub = alphas * Fh < HUB_R
            plate = np.where(onhub, Fh / np.cos(alphas), -1e9); prof = np.where(onhub, plate, prof)
            prof = env60(np.maximum(prof, plate), alphas * r0)
            tip = int(np.argmin(np.abs(alphas - b)))
            D["cr"].append(dict(alphas=alphas, across=across, rho=prof, score=~onhub))
            D["rT"][k] = float(prof[tip:].max()) + CR_T + UJ_R + 1.0
        if log: log(f"    iter {it}: valid {valid.mean():.2f} rT {np.round(D['rT'], 1)} L {np.round(D['L'], 1)} F {np.round(D['F'], 1)}")
    # final L and kinematics with the final r_T
    for k in range(3):
        D["L"][k], _ = stab_L(D["c"][k], D["e1"][k], D["e2"][k], D["beta"][k], D["rT"][k], D["q"][k], D["sigma"][k], X.RS, X.RH, X.w, P["trans"])
        D["L"][k] += P["dL"][k]
    K = kin(D, X.RS, X.RH, P["trans"]); valid = K["okk"].all(1) & (K["det"] >= P["det"]); D["K"] = K; D["valid"] = valid
    if "cr" not in D: D["dead"] = "no kinematically valid pose"; return D
    # rods: centreline offset y(x) from the chord along the in-plane outward normal, K3 over the valid poses
    I = np.nonzero(valid)[0]; D["rod"] = []
    for k in range(3):
        T = K["T"][:, k]; Q = K["Q"][:, k]; L = D["L"][k]; dch = unit(Q - T); nrm = unit(np.cross(T, Q)); up = unit(np.cross(nrm, dch))
        up = np.where(((up * (T + Q)).sum(-1) < 0)[:, None], -up, up)
        xs = np.linspace(0, L, max(3, int(L / SP) + 1))
        if P["bow"] == "arc":
            h = P["sag"]; R = (h * h + L * L / 4) / (2 * h) if h > 1e-6 else None
            y = np.zeros_like(xs) if R is None else np.sqrt(np.maximum(R * R - (xs - L / 2) ** 2, 0)) - (R - h)
        elif len(I):
            acr = np.array([-2.0, 0.0, 2.0]); dep = np.array([1.5, 2.5, 1.5])
            base = T[I, None, None, :] + xs[None, :, None, None] * dch[I, None, None, :] + acr[None, None, :, None] * nrm[I, None, None, :]
            dirs = np.broadcast_to(up[I, None, None, :], base.shape)
            req = X.march(I, base.reshape(len(I), -1, 3), dirs.reshape(len(I), -1, 3).copy(), -25.0, 160.0, clear)
            req = req.reshape(len(I), len(xs), 3) + dep[None, None, :]
            y = np.percentile(req.max(2), pct, axis=0)
            y = env60(y, xs); ends = np.minimum(xs, L - xs)
            y = np.minimum(np.maximum(y, -CLIMB * ends), CLIMB * ends)
        else:
            y = np.zeros_like(xs)
        D["rod"].append(dict(xs=xs, y=y))
    return D


def crank_rot(D, k, th, RS):
    """rotation (n,3,3) mapping the crank's S-frame reference shape (theta = 0) to the thorax: RS @ Rot(c, theta)"""
    c = D["c"][k]; Kx = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    R = np.eye(3)[None] + np.sin(th)[:, None, None] * Kx[None] + (1 - np.cos(th))[:, None, None] * (Kx @ Kx)[None]
    return RS @ R


# ------------------------------------------------------------------------------------------------ parts per pose
def sphere_pts(n=26):
    i = np.arange(n) + 0.5; phi = np.arccos(1 - 2 * i / n); th = math.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


SPH = sphere_pts(40)


def parts(D, X, idx):
    """metal of the bench poses idx: per pose a dict of members: name -> dict(score (m,3) skin-facing samples,
    extra (m,3) contact-only samples, core (m,3) collision points, rad (half-thickness mm), kind)"""
    K = D["K"]; out = []
    GX, GY = D["hub_xy"]
    for i in idx:
        RS = X.RS[i]; RH = X.RH[i]; M = {}
        for k in range(3):                                               # hubs
            c = RS @ D["c"][k]; e1 = RS @ D["e1"][k]; e2 = RS @ D["e2"][k]; F = D["F"][k]
            disc = F * c + GX[:, None] * e1 + GY[:, None] * e2
            a = np.linspace(0, 2 * math.pi, 16, endpoint=False); rim = HUB_R * (np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2)
            lv = np.array([0.0, 4.0, 8.0, HUB_TOP]); cyl = (F + lv[:, None, None]) * c + rim[None]
            core = np.concatenate([cyl.reshape(-1, 3), (F + HUB_TOP) * c + 0.6 * GX[:, None] * e1 + 0.6 * GY[:, None] * e2, disc])
            M[f"hub{k}"] = dict(score=disc, extra=np.concatenate([cyl.reshape(-1, 3), (F + HUB_TOP) * c + 0.8 * GX[:, None] * e1 + 0.8 * GY[:, None] * e2]),
                                core=core, rad=1.0, hub=(F * c, c))
        for j, br in enumerate(D["br"]):                                 # base brackets (S-fixed)
            dS = arc_dirs(br["ca"], br["e"], br["alphas"], br["across"], br["Fm"]); d = dS @ RS.T
            und = d * br["rho"][:, None, None]; sc = br["score"]
            M[f"br{j}"] = dict(score=und[sc].reshape(-1, 3), extra=(d * (br["rho"] + BR_T)[:, None, None])[sc].reshape(-1, 3),
                               core=(d * (br["rho"] + BR_T / 2)[:, None, None])[sc].reshape(-1, 3), rad=BR_T / 2, pair=(br["a"], br["b"]))
        for k in range(3):                                               # cranks, U, rods, balls
            cr = D["cr"][k]; R = crank_rot(D, k, K["th"][i:i + 1, k], RS[None])[0]
            dS = arc_dirs(D["c"][k], D["e1"][k], cr["alphas"], cr["across"], D["rT"][k]); d = dS @ R.T
            und = d * cr["rho"][:, None, None]; sc = cr["score"]
            M[f"crank{k}"] = dict(score=und[sc].reshape(-1, 3), extra=(d * (cr["rho"] + CR_T)[:, None, None])[sc].reshape(-1, 3),
                                  core=(d * (cr["rho"] + CR_T / 2)[:, None, None])[sc].reshape(-1, 3), rad=CR_T / 2)
            T = K["T"][i, k]; Q = K["Q"][i, k]
            M[f"U{k}"] = dict(score=np.zeros((0, 3)), extra=T + UJ_R * SPH, core=T[None], rad=UJ_R)
            M[f"ball{k}"] = dict(score=np.zeros((0, 3)), extra=Q + BALL_R * SPH, core=Q[None], rad=BALL_R)
            rd = D["rod"][k]; dch = unit(Q - T); nrm = unit(np.cross(T, Q)); up = unit(np.cross(nrm, dch))
            if up @ (T + Q) < 0: up = -up
            C = T + rd["xs"][:, None] * dch + rd["y"][:, None] * up
            keep = (np.linalg.norm(C - T, axis=1) > UJ_R) & (np.linalg.norm(C - Q, axis=1) > BALL_R)
            ph = np.array([-67.5, -22.5, 22.5, 67.5]) * D2R; pt = np.array([112.5, 157.5, -157.5, -112.5]) * D2R
            lo = C[keep, None, :] + ROD_R * (-np.cos(ph)[None, :, None] * up + np.sin(ph)[None, :, None] * nrm)
            hi = C[keep, None, :] + ROD_R * (-np.cos(pt)[None, :, None] * up + np.sin(pt)[None, :, None] * nrm)
            M[f"rod{k}"] = dict(score=lo.reshape(-1, 3), extra=hi.reshape(-1, 3), core=C, rad=ROD_R)
        for j, sd in enumerate(D["sad"]):                                # saddle straps (H-fixed)
            und = (sd["bH"] + sd["rho"][:, None] * sd["nH"]) @ RH.T; top = (sd["bH"] + (sd["rho"] + SAD_T)[:, None] * sd["nH"]) @ RH.T
            mid = (sd["bH"] + (sd["rho"] + SAD_T / 2)[:, None] * sd["nH"]) @ RH.T
            M[f"sad{j}"] = dict(score=und, extra=top, core=mid, rad=SAD_T / 2)
        ss = np.arange(BAR_S0, 200.0, SP); aa = np.arange(-BAR_W / 2 + 1, BAR_W / 2, SP)            # BOTTOM bar (obstacle)
        lat = np.cross(WB, DB); bar = ((BAR_Z + BAR_T / 2) * WB + ss[:, None, None] * DB + aa[None, :, None] * lat).reshape(-1, 3) @ RH.T
        M["bar"] = dict(score=np.zeros((0, 3)), extra=np.zeros((0, 3)), core=bar, rad=BAR_T / 2, user=True)
        out.append(M)
    return out


def adjacent(a, b, D):
    """True when two members are joined (never checked); else None or an exemption (point, radius)"""
    S_body = lambda m: m.startswith("hub") or m.startswith("br")
    H_body = lambda m: m.startswith("sad") or m == "bar"
    if S_body(a) and S_body(b): return True
    if H_body(a) and H_body(b): return True
    for x, y in ((a, b), (b, a)):
        if x.startswith("hub") and y == "crank" + x[3:]: return True
        if x.startswith("U") and y in ("crank" + x[1:], "rod" + x[1:]): return True
        if x.startswith("ball") and y == "rod" + x[4:]: return True
        if x.startswith("ball") and (H_body(y)) and (x == "ball0" and y == "bar" or x != "ball0" and y == f"sad{int(x[4:]) - 1}"): return True
    return False


def exempt_zones(a, b, M, D, i):
    """points near a shared joint where two members may touch (joint partners): list of (centre, radius)"""
    z = []
    for x, y in ((a, b), (b, a)):
        if x.startswith("crank") and y.startswith("br"):
            k = int(x[5:]); pa = M[y]["pair"]
            if k in pa: z.append((M[f"hub{k}"]["hub"][0], HUB_R + 2.0))
        if x.startswith("crank") and y.startswith("rod") and x[5:] == y[3:]:
            z.append((D["K"]["T"][i, int(x[5:])], UJ_R + 3.0))
        if x.startswith("rod") and (y.startswith("sad") or y == "bar"):
            k = int(x[3:]); z.append((D["K"]["Q"][i, k], BALL_R + STUD_R))
        if x.startswith("U") and y.startswith("br"): pass
    return z


def collide(M, D, i):
    """True if two non-adjacent members come within GAP of each other (half-thickness point clouds)"""
    names = list(M.keys()); trees = {}
    for a_ in range(len(names)):
        for b_ in range(a_ + 1, len(names)):
            a, b = names[a_], names[b_]
            if adjacent(a, b, D): continue
            Pa, Pb = M[a]["core"], M[b]["core"]
            if not len(Pa) or not len(Pb): continue
            lim = M[a]["rad"] + M[b]["rad"] + GAP
            zones = exempt_zones(a, b, M, D, i)
            if zones:
                ka = np.ones(len(Pa), bool); kb = np.ones(len(Pb), bool)
                for cz, rz in zones:
                    ka &= np.linalg.norm(Pa - cz, axis=1) > rz; kb &= np.linalg.norm(Pb - cz, axis=1) > rz
                Pa, Pb = Pa[ka], Pb[kb]
                if not len(Pa) or not len(Pb): continue
            lo = np.minimum(Pa.min(0), Pa.min(0));
            if np.any(Pa.min(0) - lim > Pb.max(0)) or np.any(Pb.min(0) - lim > Pa.max(0)): continue
            if a not in trees: trees[a] = cKDTree(M[a]["core"])
            dd, _ = cKDTree(Pa).query(Pb, k=1, distance_upper_bound=lim)
            if np.isfinite(dd).any() and dd.min() < lim: return f"{a}/{b}"
    return None


def continuity(D, X):
    """bench clip frames not followed because a joint jumps > FLIP deg (K2) along the full-rate clip"""
    P = D["P"]; K = kin(D, X.fRS, X.fRH, P["trans"]); ok = K["okk"].all(1) & (K["det"] >= P["det"])
    J = np.concatenate([np.degrees(K["th"]), K["sw"], K["spn"]], 1); flip = np.zeros(len(ok), bool); o = 0
    for _, ix in X.fclips:
        prev = None
        for j in range(o, o + len(ix)):
            if not ok[j]: continue
            if prev is not None and np.abs(wrapd(J[j] - J[prev])).max() > FLIP: flip[j] = True
            prev = j
        o += len(ix)
    bad = np.zeros(X.n, bool); m = X.bench_to_full >= 0
    bad[m] = flip[X.bench_to_full[m]] | ~ok[X.bench_to_full[m]]
    return bad, dict(full_valid=float(ok.mean()), flips=int(flip.sum()))


def evaluate(params, X, log=print, detail=False):
    t0 = time.time(); D = build(params, X, log=None)
    B = X.B; B.reset(); P = D["P"]
    if "dead" in D:
        r = B.report(); r.update(dead=D["dead"]); return r, D
    valid = D["valid"].copy(); bad, cinfo = continuity(D, X); flipped = valid & X.clip & bad
    ncol = 0; why = {}; per = {}
    allp = parts(D, X, np.nonzero(valid)[0])
    for a, i in enumerate(np.nonzero(valid)[0]):
        if flipped[i]: B.record(i, None); continue
        M = allp[a]; col = collide(M, D, i)
        if col: ncol += 1; why[col] = why.get(col, 0) + 1; B.record(i, None); continue
        sc = np.concatenate([M[m]["score"] for m in M]); ex = np.concatenate([M[m]["extra"] for m in M if not M[m].get("user")])
        de = B.dist(i, ex)
        if de.min() < 0: sc = np.concatenate([sc, ex[np.argmin(de)][None]])
        d = B.record(i, sc)
        if detail:
            o = 0
            for m in M:
                n_ = len(M[m]["score"]); dd = d[o:o + n_]; o += n_
                if n_ and i in np.nonzero(X.clip)[0]: per.setdefault(m.rstrip("0123456789"), []).append(dd)
    r = B.report()
    r.update(kin_valid=round(float(valid.mean()), 3), kin_valid_ws=round(float(valid[~X.clip].mean()), 3), kin_valid_clip=round(float(valid[X.clip].mean()), 3),
             collided=ncol, flipped=int(flipped.sum()), coll_pairs=dict(sorted(why.items(), key=lambda x: -x[1])[:4]), full_rate=cinfo,
             rT=[round(x, 1) for x in D["rT"]], L=[round(x, 1) for x in D["L"]], F=[round(x, 1) for x in D["F"]], secs=round(time.time() - t0, 1))
    if detail and per:
        r["per_member"] = {m: dict(n=int(sum(len(x) for x in v)), inband14=round(float(np.mean(np.concatenate(v) >= 2) * 0 + np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 14))), 3),
                                    med=round(float(np.median(np.concatenate(v))), 1)) for m, v in per.items()}
    return r, D


# ------------------------------------------------------------------------------------------------ single-pose API
_DESIGNS = {}


def metal(pose, frames, params=None, bench=None):
    """(k, 3) metal sample points (skin-facing faces) of the design `params` for one pose, or None when the chain does
    not close / is singular / collides. The rigid parts are fitted on `bench` (default Bench(60, 160)); clip continuity
    needs the clip and is applied by evaluate()."""
    key = json.dumps(params or {}, sort_keys=True)
    if key not in _DESIGNS:
        X = Ctx(bench or CB.Bench(60, 160)); _DESIGNS[key] = (build(params, X), X)
    D, X = _DESIGNS[key]
    RS = frames["S"][0][None]; RH = frames["H"][0][None]; P = D["P"]
    K = kin(D, RS, RH, P["trans"])
    if not (K["okk"].all() and K["det"][0] >= P["det"]): return None
    X2 = copy.copy(X); X2.RS = RS; X2.RH = RH
    D2 = dict(D); D2["K"] = K
    M = parts(D2, X2, [0])[0]
    if collide(M, D2, 0): return None
    return np.concatenate([M[m]["score"] for m in M])


# ------------------------------------------------------------------------------------------------ main
def write_sweep(rows):
    p = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json"); json.dump(rows, open(p + ".tmp", "w"), indent=1); os.replace(p + ".tmp", p)


def sweep_entry(k, params, r):
    return dict(k=k, t=now(), params=params, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"], follow=r["follow"],
                contact=r["contact"], gap=r["gap"], kin_valid=r.get("kin_valid"), collided=r.get("collided"), flipped=r.get("flipped"))


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "check"
    if mode == "check":
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (20, 40)
        X = Ctx(CB.Bench(nc, nw)); print("bench", X.B.mode, X.n)
        r, D = evaluate({}, X, detail=True); print(json.dumps(r, indent=1))

"""Concept model: POSTERIOR MAX-MARGIN CARDAN (id posterior-max-margin-cardan), docs/concepts/catalogue.json.

A spherical 3R (every axis through the GH centre) with both link arcs at 90 deg (a Cardan), placed so that the line
of the first axis stays as far as possible from the arm's last axis over the functional workspace (the largest
singularity margin any spherical 3R can have), with the whole chain behind the frontal plane:
  scapula base (S) -> J1 (O20 hub, axis b fixed in the scapula, pole low on the infraspinatus)
  -> link 1 (90 deg strap up the back of the scapula) -> J2 (O20 hub, pole p2 = sigma (b x w)/|b x w| on the
  posterior-superior shoulder) -> link 2 (90 deg strap down the posterior deltoid) -> J3 (O20 hub, axis W fixed in the
  humerus, pole on the posterior upper arm) -> arm-end plate + 14 x 6 neck to BOTTOM's bar.

DOF: 3 ACTIVE (J1-J3), 0 PASSIVE. With a1 = a2 = 90 the closure is p2 = sigma (b x w)/|b x w| in closed form,
q2 = theta = angle(b, w), q1 / q3 follow; the chain has no spare coordinate (3 joints, 3 arm rotations).

Model (catalogue model_spec K0-K7, kept; departures are listed in docs/concepts/posterior-max-margin-cardan.md):
  * pose frames: RS = the scapula rotation, RH = RS @ HG (the band evaluator's humerus frame - the frame w_dir and
    BOTTOM's bar are defined in; it differs from body_pose's rest-humerus frame by a constant 12.2 deg, so it is a
    re-labelling of W, not a different mechanism). tools/concept_baseline.py uses the same RS / HG.
  * K3 skin-fitted undersides: per sample direction u (fixed in its member) and fit pose i the requirement r_i = the
    first t >= 15 mm along the ray from GH with B.dist >= 2 mm and >= 0 over [t, t + 15] (sphere-traced, 1 mm
    resolution); the underside = quantile_q of r_i over the fit poses (every bench pose the chain closes in).
  * samples: every skin-facing underside on a 2 mm grid at its own height (1 point / 4 mm2): links 12 mm wide
    (6 lanes) x 3 mm, the neck 14 mm (7 lanes) x 6 mm, hub discs (R 10 mm) on a 2 mm grid.
  * K4 O20 hub with a WEDGE seat: the lower member's underside under the disc is fitted to the skin; the bearing's
    lower face F = the highest point of that underside along the axis; lower plate [F, F + 3], upper member from
    F + 3.15, crown F + 12.25 (docs/HARDWARE.md v5). Variants: 'tilt' (planar underside perpendicular to the mean
    skin normal), 'flat' (plain disc perpendicular to the axis at F).
  * K5 straps: the upper member sits flat on its hub plate (F + 3.15) over the hub footprint and may not climb faster
    than 60 deg anywhere along its length (the profile is the smallest 60 deg-Lipschitz envelope of the fitted
    requirement); a hub whose plate cannot ramp clear of the skin next to it is raised.
  * K6 self-collision: members as centre-line samples with radial intervals [underside, top] and half-widths; two
    members that do not share a joint (or joint partners beyond hub radius + 2 mm of their joint) collide when two
    samples are within (half-widths + 1 mm) and their intervals overlap (+ 0.5 mm). BOTTOM's bar is an obstacle.
  * a pose is TAKEN iff: the chain closes (margin >= 5 deg), no joint jumps > 25 deg between consecutive 10 fps frames
    of its fit clip (K2, checked at the full frame rate), no self-collision, and no metal - undersides AND tops /
    crowns / hub walls - inside the body (a top that dips into the body is recorded as contact).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/posterior-max-margin-cardan.py [check|sweep|best|plot]
"""
import json, math, os, sys, time, datetime
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "posterior-max-margin-cardan"
NAME = "Posterior max-margin Cardan"
D2R = math.pi / 180
# ---- hardware (docs/HARDWARE.md v5, catalogue K4-K7) ----------------------------------------------------------------
HUB_R, PLATE, UP, CROWN = 10.0, 3.0, 3.15, 12.25          # O20 hub: radius, lower plate, upper member underside, crown (from F)
CLEAR, FREE, T0, T1 = 2.0, 15.0, 15.0, 220.0              # K3: clearance, free run above, march window (mm from GH)
SP = 2.0                                                   # sample spacing (mm) -> 1 point / 4 mm2
RAMP = math.tan(60 * D2R)                                  # K5 climb limit
JUMP, MIN_MARGIN = 25.0, 5.0                               # K2 / K1 (deg)
NECK_W, NECK_T = 14.0, 6.0                                 # K7 neck
WB = np.array([0.0, -0.0713, 0.9975]); WB /= np.linalg.norm(WB)
DB = np.array([0.0, -0.9975, -0.0713]); DB = DB - (DB @ WB) * WB; DB /= np.linalg.norm(DB)
ZBAR, DBAR0, DBAR1, BAR_HW, BAR_T = 67.5, 40.0, 200.0, 16.0, 6.5    # BOTTOM's bar (humerus frame), user part
TI = 4.43e-3                                               # g / mm3

PARAMS = dict(b_az=-28.0, b_el=-19.0, w_d=42.0, w_a=-64.0,   # catalogue seed: b = bvec(-28, -19), W = wdir(42, -64)
              sigma=1, seat="wedge", j2_top="link2", j3_low="armend", q=1.0, width=12.0, t_link=3.0)
# sweep: (b, W) from the top of the singularity-margin landscape (margin >= ~26 deg over all fit + workspace poses,
# computed by margin_landscape()), the branch, the hub seat, the stacking order at J2 / J3, the quantile, the width
SWEEP = dict(bW="margin_landscape() top set, posterior poles (J1 posterior-inferior-medial, J3 posterior arm)",
             sigma=[1, -1], seat=["wedge", "tilt", "flat"], j2_top=["link1", "link2"], j3_low=["armend", "link2"],
             q=[1.0, 0.97, 0.93, 0.9, 0.85], width=[12.0, 8.0])


# ---- small geometry ----------------------------------------------------------------------------------------------
def unit(x): x = np.asarray(x, float); return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def wdir(d, a): return np.array([math.sin(d * D2R) * math.sin(a * D2R), -math.cos(d * D2R), math.sin(d * D2R) * math.cos(a * D2R)])
def az_el(b): return math.degrees(math.atan2(b[2], -b[0])), math.degrees(math.asin(max(-1, min(1, b[1]))))
def d_a(w): return math.degrees(math.acos(max(-1, min(1, -w[1])))), math.degrees(math.atan2(w[0], w[2]))


def perp_basis(a):
    a = unit(a); r = np.array([0.0, 0.0, 1.0]) if abs(a[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    e1 = unit(np.cross(a, r)); return e1, np.cross(a, e1)


def slerp(u, v, s):
    """unit vectors on the great circle from u to v at fractions s (n,)"""
    om = math.acos(max(-1.0, min(1.0, float(u @ v)))); s = np.atleast_1d(s)
    if om < 1e-9: return np.repeat(u[None], len(s), 0)
    return unit((np.sin((1 - s) * om)[:, None] * u + np.sin(s * om)[:, None] * v) / math.sin(om))


def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---- poses ---------------------------------------------------------------------------------------------------------
class Rig:
    """bench poses (RS, RH) + the full-rate fit clips for the continuity check"""
    def __init__(self, B):
        Z = CB._poses_all(); self.B = B; self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.RH = self.RS @ Z["HG"][B.idx].astype(float)
        names = list(Z["NAMES"]); cid = Z["CID"]
        self.fit_clips = [names.index(n) for n in CB.FIT]
        self.full = {}                                       # clip id -> Z indices in time order
        for c in self.fit_clips:
            ii = np.nonzero(cid == c)[0]; self.full[c] = ii[np.argsort(Z["FI"][ii])]
        allc = np.concatenate(list(self.full.values()))
        self.RSf = Z["RS"][allc].astype(float); self.RHf = self.RSf @ Z["HG"][allc].astype(float); self.allc = allc
        ws = np.nonzero(cid == names.index("Workspace (envelope)"))[0]
        self.RSw = Z["RS"][ws].astype(float); self.RHw = self.RSw @ Z["HG"][ws].astype(float)


def margin_landscape(n=1500, top=60, seed_b=(-30.0, -16.0), seed_w=(36.0, -72.0), cone=35.0):
    """singularity margin min over every fit-clip frame and workspace pose of min(theta, 180 - theta), theta =
    angle(b, w): Fibonacci grids of b (scapula frame) and W (humerus frame) inside `cone` deg of the posterior seeds;
    returns the top configurations [(margin, b_az, b_el, w_d, w_a)] sorted by margin"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
    m = np.isin(cid, [names.index(x) for x in CB.FIT] + [names.index("Workspace (envelope)")]); HG = Z["HG"][m].astype(float)
    i = np.arange(n * 8) + 0.5; phi = np.arccos(1 - 2 * i / (n * 8)); th = math.pi * (1 + 5 ** 0.5) * i
    F = np.stack([np.cos(th) * np.sin(phi), np.cos(phi), np.sin(th) * np.sin(phi)], 1)
    b0, w0 = bvec(*seed_b), wdir(*seed_w)
    Bs = F[F @ b0 > math.cos(cone * D2R)]; Ws = F[F @ w0 > math.cos(cone * D2R)]
    out = []
    for b in Bs:
        V = np.einsum("pji,j->pi", HG, b); c = np.abs(V @ Ws.T).max(0); mg = np.degrees(np.arccos(np.clip(c, -1, 1)))
        for j in np.argsort(-mg)[:3]: out.append((float(mg[j]), *az_el(b), *d_a(Ws[j])))
    out.sort(reverse=True); return out[:top]


def margin_of(b, W, RS, RH):
    w = np.einsum("pij,j->pi", RH, W); p1 = np.einsum("pij,j->pi", RS, b)
    th = np.degrees(np.arccos(np.clip((w * p1).sum(-1), -1, 1))); return np.minimum(th, 180 - th), th


# ---- kinematics ----------------------------------------------------------------------------------------------------
def chain(par, RS, RH):
    """Cardan closure: poles p1, p2, p3 (P, 3) in the thorax, joint values q (P, 3) deg, margin (P,) deg"""
    b = unit(bvec(par["b_az"], par["b_el"])); W = unit(wdir(par["w_d"], par["w_a"]))
    p1 = np.einsum("pij,j->pi", RS, b); p3 = np.einsum("pij,j->pi", RH, W)
    c = np.clip((p1 * p3).sum(-1), -1, 1); th = np.degrees(np.arccos(c)); mg = np.minimum(th, 180 - th)
    p2 = float(par["sigma"]) * unit(np.cross(p1, p3))
    e1, e2 = perp_basis(b); f1, f2 = perp_basis(W)
    p2s = np.einsum("pji,pj->pi", RS, p2); p2h = np.einsum("pji,pj->pi", RH, p2)
    q1 = np.degrees(np.arctan2(p2s @ e2, p2s @ e1)); q3 = np.degrees(np.arctan2(p2h @ f2, p2h @ f1))
    q2 = np.degrees(np.arctan2(np.einsum("pi,pi->p", np.cross(p1, p3), p2), c))
    return dict(p1=p1, p2=p2, p3=p3, q=np.stack([q1, q2, q3], 1), margin=mg, theta=th, b=b, W=W)


def frames(ch, RS, RH):
    p1, p2, p3 = ch["p1"], ch["p2"], ch["p3"]
    return dict(S=RS, H=RH, L1=np.stack([p1, p2, np.cross(p1, p2)], -1), L2=np.stack([p3, p2, np.cross(p3, p2)], -1))


def flips(par, rig):
    """K2 at the full 10 fps: per fit-clip frame, True if a joint jumps > JUMP deg from the previous frame (wrapped);
    returns {Z index: flip}, the largest step (deg)"""
    ch = chain(par, rig.RSf, rig.RHf); q = ch["q"]; out = {}; mx = 0.0; o = 0
    for c, ii in rig.full.items():
        qq = q[o:o + len(ii)]; o += len(ii)
        dq = np.abs((np.diff(qq, axis=0) + 180) % 360 - 180).max(1) if len(ii) > 1 else np.zeros(0)
        mx = max(mx, float(dq.max()) if len(dq) else 0.0)
        out[int(ii[0])] = False
        for k in range(1, len(ii)): out[int(ii[k])] = bool(dq[k - 1] > JUMP)
    return out, mx


# ---- K3 requirement: sphere-traced march ---------------------------------------------------------------------------
def req(B, i, D):
    """first t in [T0, T1] along unit rays D (n, 3) from GH with dist >= CLEAR at t and >= 0 over [t, t + FREE]"""
    n = len(D); t = np.full(n, T0); cand = np.full(n, -1.0); r = np.full(n, T1); act = np.arange(n)
    for _ in range(200):
        if not len(act): break
        ta = t[act]; ca = cand[act]; d = B.dist(i, D[act] * ta[:, None]); nt = ta.copy()
        srch = ca < 0
        A = srch & (d < CLEAR); nt[A] = ta[A] + np.maximum(CLEAR - d[A], 1.0)
        Bm = srch & (d >= CLEAR); ca[Bm] = ta[Bm]; nt[Bm] = ta[Bm] + np.maximum(d[Bm], 1.0)
        C = ~srch & (d >= 0); nt[C] = ta[C] + np.maximum(d[C], 1.0)
        Dm = ~srch & (d < 0); ca[Dm] = -1.0; nt[Dm] = ta[Dm] + np.maximum(CLEAR - d[Dm], 1.0)
        fin = (ca >= 0) & ((nt >= ca + FREE) | (nt > T1))
        r[act[fin]] = ca[fin]
        out = ~fin & (nt > T1)
        t[act] = nt; cand[act] = ca
        act = act[~(fin | out)]
    return r


def requirements(B, poses, groups, F):
    """groups: [(frame name, U local (m, 3))] -> list of (len(poses), m) requirement arrays"""
    sizes = [len(U) for _, U in groups]; out = [np.zeros((len(poses), s)) for s in sizes]
    for k, i in enumerate(poses):
        D = np.concatenate([np.einsum("ij,mj->mi", F[fn][i], U) for fn, U in groups])
        r = req(B, int(i), D); o = 0
        for g, s in enumerate(sizes): out[g][k] = r[o:o + s]; o += s
    return out


# ---- layout: sample directions of every member in its own frame -------------------------------------------------------
LOCAL_AX = dict(S=None, H=None)                  # filled per design: J1 axis in S = b, J3 axis in H = W


def strap_center(u, v, n_deg=1.0):
    om = math.degrees(math.acos(max(-1.0, min(1.0, float(u @ v))))); s = np.linspace(0, 1, max(3, int(om / n_deg) + 1))
    return s * om * D2R, slerp(u, v, s)


def strap_rows(u, v, r_of_s, s_c, width):
    """2 mm rows along the great circle u -> v at the fitted height r(s), lanes 2 mm apart across"""
    r_c = r_of_s; L = np.r_[0, np.cumsum(np.hypot(np.diff(s_c) * 0.5 * (r_c[1:] + r_c[:-1]), np.diff(r_c)))]
    marks = np.arange(SP / 2, L[-1], SP); s_rows = np.interp(marks, L, s_c); r_rows = np.interp(marks, L, r_c)
    om = s_c[-1]; d = slerp(u, v, s_rows / max(om, 1e-9)); nrm = unit(np.cross(u, v))
    lanes = np.arange(-width / 2 + SP / 2, width / 2 - 1e-6, SP)
    ang = lanes[None, :] / r_rows[:, None]
    U = unit(np.cos(ang)[..., None] * d[:, None, :] + np.sin(ang)[..., None] * nrm[None, None, :])      # (rows, lanes, 3)
    return dict(U=U, s=s_rows, L=marks, lanes=lanes, d=d, r_est=r_rows)


def disc_dirs(a, h):
    e1, e2 = perp_basis(a); g = np.arange(-HUB_R + SP / 2, HUB_R, SP); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= HUB_R ** 2
    X, Y = X[k], Y[k]; U = unit(h * a[None] + X[:, None] * e1[None] + Y[:, None] * e2[None])
    return dict(U=U, xy=np.stack([X, Y], 1), a=a, e1=e1, e2=e2, h=h)


class Design:
    """geometry of one (b, W, sigma) placement: requirements computed once, variants (q, seat, stacking, width) cheap"""
    def __init__(self, B, rig, par, log=print):
        self.B, self.rig, self.par = B, rig, dict(par); t0 = time.time()
        self.ch = chain(par, rig.RS, rig.RH); self.F = frames(self.ch, rig.RS, rig.RH)
        self.fl, self.maxjump = flips(par, rig)
        self.flip = np.array([self.fl.get(int(z), False) for z in B.idx])
        self.closes = self.ch["margin"] >= MIN_MARGIN
        self.fit = np.nonzero(self.closes)[0]
        b, W = self.ch["b"], self.ch["W"]; ex, ey = np.eye(3)[0], np.eye(3)[1]
        pb = ZBAR * WB + DBAR0 * DB; self.pb_u = unit(pb)
        # axes in each member's local frame
        self.ax = {("S", 1): b, ("L1", 1): ex, ("L1", 2): ey, ("L2", 2): ey, ("L2", 3): ex, ("H", 3): W}
        # pass A: centre lines at 1 deg (links, neck) and the three axes
        sc1, C1 = strap_center(ex, ey); sc2, C2 = strap_center(ey, ex)
        scn, CN = strap_center(W, self.pb_u)
        gA = [("L1", C1), ("L2", C2), ("H", CN)]
        RA = requirements(B, self.fit, gA, self.F)
        rq = lambda R: np.quantile(R, 0.9, axis=0)
        self.cl = dict(link1=(ex, ey, sc1, rq(RA[0])), link2=(ey, ex, sc2, rq(RA[1])), neck=(W, self.pb_u, scn, rq(RA[2])))
        # pass B: 2 mm samples (12 mm links, 14 mm neck) and the hub discs in each candidate lower member
        self.st = {nm: strap_rows(u, v, r, s, NECK_W if nm == "neck" else 12.0) for nm, (u, v, s, r) in self.cl.items()}
        h1, h2, h3 = self.cl["link1"][3][0], self.cl["link1"][3][-1], self.cl["link2"][3][-1]
        self.discs = {("S", 1): disc_dirs(b, h1), ("L1", 2): disc_dirs(ey, h2), ("L2", 2): disc_dirs(ey, h2),
                      ("L2", 3): disc_dirs(ex, h3), ("H", 3): disc_dirs(W, h3)}
        frame_of = dict(link1="L1", link2="L2", neck="H")
        gB = [(frame_of[nm], v["U"].reshape(-1, 3)) for nm, v in self.st.items()] + [(k[0], v["U"]) for k, v in self.discs.items()]
        RB = requirements(B, self.fit, gB, self.F); o = 0
        for nm, v in self.st.items(): v["R"] = RB[o].reshape(len(self.fit), *v["U"].shape[:2]); o += 1
        for k, v in self.discs.items(): v["R"] = RB[o]; o += 1
        allR = np.concatenate([v["R"].reshape(len(self.fit), -1) for v in self.st.values()] + [v["R"] for v in self.discs.values()], 1)
        self.cost = np.maximum(0.0, allR - np.quantile(allR, 0.9, axis=0)).sum(1)
        self.order = np.argsort(-self.cost)                  # rows of the fit poses, the hardest first
        self.secs = time.time() - t0
        log(f"  geometry {self.secs:.0f} s: fit poses {len(self.fit)}/{len(B.poses)}, margin {self.ch['margin'].min():.1f}-"
            f"{self.ch['margin'].max():.1f}, max 10 fps step {self.maxjump:.1f} deg, samples {sum(len(u) for _, u in gB)}")

    # ---- a variant: heights of every part ----------------------------------------------------------------------
    def kept(self, var):
        """fit poses that shape the parts: all closing poses, minus the `drop` share whose skin pushes hardest"""
        n = int(round(float(var.get("drop", 0.0)) * len(self.fit)))
        return np.sort(self.order[n:])

    def fitq(self, R, var, keep):
        return np.quantile(R[keep], var["q"], axis=0) if var["q"] < 1 else R[keep].max(0)

    def build(self, var):
        q, seat, width, t_link = var["q"], var["seat"], var["width"], var["t_link"]
        keep = self.kept(var)                                 # rows of the requirement arrays (fit-pose order)
        lower = {1: "S", 2: "L1" if var["j2_top"] == "link2" else "L2", 3: "H" if var["j3_low"] == "armend" else "L2"}
        member_of = dict(S="base", L1="link1", L2="link2", H="armend")
        hub = {}
        for k in (1, 2, 3):                                    # wedge / tilt / flat underside under each disc
            dsc = self.discs[(lower[k], k)]; rho = self.fitq(dsc["R"], var, keep); a = dsc["a"]; U = dsc["U"]
            ca = U @ a
            if seat == "wedge": rr = rho
            elif seat == "flat": rr = (rho * ca).max() / ca
            else:                                              # tilt: plane fitted to the wedge points, lowered to clear
                P = rho[:, None] * U; c = P.mean(0); n = np.linalg.svd(P - c)[2][2]; n = n if n @ a > 0 else -n
                tt = (P @ n).max(); rr = tt / (U @ n)
            Fk = float((rr * ca).max())
            hub[k] = dict(lower=lower[k], low_member=member_of[lower[k]], U=U, a=a, r=rr, F=Fk, xy=dsc["xy"], e1=dsc["e1"], e2=dsc["e2"],
                          wedge=float((rr * ca).max() - (rr * ca).min()), F0=Fk)
        upper = {1: "L1", 2: "L2" if lower[2] == "L1" else "L1", 3: "L2" if lower[3] == "H" else "H"}
        for k in (1, 2, 3): hub[k]["upper"] = upper[k]; hub[k]["up_member"] = member_of[upper[k]]
        rho = {}
        for nm, st in self.st.items():
            lane_ok = np.abs(st["lanes"]) <= (NECK_W if nm == "neck" else width) / 2
            rho[nm] = (lane_ok, self.fitq(st["R"][:, :, lane_ok], var, keep))
        extra = {nm: np.zeros(len(st["L"])) for nm, st in self.st.items()}
        # stacking at the shared joints: the upper member's strap rides over the lower member's strap where they overlap
        name_of = dict(L1="link1", L2="link2", H="neck")
        pairs = [(2, name_of[lower[2]], name_of[upper[2]]), (3, name_of[lower[3]], name_of[upper[3]])]
        fitp = self.fit[keep]
        for it in range(6):
            straps, raised = self._straps(hub, rho, extra, width, t_link)
            grew = False
            for k, lo, up in pairs:
                need = self._stack(straps[lo], straps[up], k, fitp)
                if (need > extra[up] + 0.25).any(): extra[up] = np.maximum(extra[up], need); grew = True
            if not raised and not grew: break
        return dict(hub=hub, straps=straps, var=dict(var), keep=keep, stack_raise={nm: float(v.max()) for nm, v in extra.items()})

    def _straps(self, hub, rho, extra, width, t_link):
        ends = dict(link1=((1, "L1"), (2, "L1")), link2=((2, "L2"), (3, "L2")), neck=((3, "H"), None))
        raised = False; straps = {}
        for nm, st in self.st.items():
            lane_ok, rh = rho[nm]; U = st["U"][:, lane_ok]
            Lb = np.maximum(rh, extra[nm][:, None]); keep = np.ones(rh.shape, bool); plate = np.zeros(rh.shape)
            ins = {}
            for e in ends[nm]:
                if e is None: continue
                k, fr = e; h = hub[k]; a = self.ax[(fr, k)]
                lat = np.linalg.norm(U * st["r_est"][:, None, None] - (U @ a)[..., None] * a * st["r_est"][:, None, None], axis=-1)
                inside = lat < HUB_R; ins[k] = inside
                if h["lower"] == fr: keep &= ~inside                    # the disc (wedge) is this member's end
                else:
                    pl = (h["F"] + UP) / np.clip(U @ a, 0.2, None); plate = np.where(inside, pl, plate)
                    Lb = np.where(inside, np.maximum(Lb, pl), Lb)
            if nm == "neck":                                            # the neck's end meets BOTTOM's bar underside
                last = np.zeros(rh.shape, bool); last[-2:] = True
                Lb = np.where(last, np.maximum(Lb, ZBAR / np.clip(U @ WB, 0.2, None)), Lb)
            s = st["L"]; env = np.max(Lb[None, :, :] - RAMP * np.abs(s[:, None, None] - s[None, :, None]), axis=1)
            for e in ends[nm]:                                          # a pinned plate pushed up -> raise the hub
                if e is None: continue
                k, fr = e; h = hub[k]
                if h["lower"] != fr and ins[k].any():
                    a = self.ax[(fr, k)]; ex_ = float(((env - plate) * np.clip(U @ a, 0.2, None))[ins[k]].max())
                    if ex_ > 0.25: h["F"] += ex_; raised = True
            straps[nm] = dict(U=U, u=env, keep=keep, frame=dict(link1="L1", link2="L2", neck="H")[nm],
                              t=NECK_T if nm == "neck" else t_link, hw=(NECK_W if nm == "neck" else width) / 2, d=st["d"], L=s)
        return straps, raised

    def _stack(self, lo_s, up_s, k, poses):
        """per row of the upper strap: the underside radius it needs to ride 0.5 mm over the lower strap's top wherever
        the two overlap in plan beyond the joint's exemption zone, over the fit poses"""
        need = np.zeros(len(up_s["d"])); a_u = self.ax[(up_s["frame"], k)]; a_l = self.ax[(lo_s["frame"], k)]
        ul = up_s["u"].min(1); ll = lo_s["u"].min(1); lh = lo_s["u"].max(1) + lo_s["t"]
        mu = np.arccos(np.clip(up_s["d"] @ a_u, -1, 1)) * ul > HUB_R + 2.0; ml = np.arccos(np.clip(lo_s["d"] @ a_l, -1, 1)) * ll > HUB_R + 2.0
        if not mu.any() or not ml.any(): return need
        du, dl = up_s["d"][mu], lo_s["d"][ml]; lim = up_s["hw"] + lo_s["hw"] + 1.0
        for i in poses:
            Du = du @ self.F[up_s["frame"]][i].T; Dl = dl @ self.F[lo_s["frame"]][i].T
            ang = np.arccos(np.clip(Du @ Dl.T, -1, 1)); rr = 0.5 * (ul[mu][:, None] + ll[ml][None, :])
            near = ang * rr < lim
            if near.any():
                rq = np.where(near, lh[ml][None, :] + 0.6, 0.0).max(1); idx = np.nonzero(mu)[0]; need[idx] = np.maximum(need[idx], rq)
        return need

    # ---- per pose ------------------------------------------------------------------------------------------------
    def bodies(self, G, i):
        """collision bodies of pose i: {member: (dirs (n, 3), lo (n,), hi (n,), hw (n,), dist-from-joint {k: (n,)})}"""
        F = self.F; out = {}
        def add(mem, D, lo, hi, hw, jd):
            if mem not in out: out[mem] = [[], [], [], [], {}]
            o = out[mem]; n0 = sum(len(x) for x in o[0]); o[0].append(D); o[1].append(lo); o[2].append(hi); o[3].append(hw)
            for k, v in jd.items():
                o[4].setdefault(k, [np.full(n0, 1e9)]).append(v)
            for k in o[4]:
                if k not in jd: o[4][k].append(np.full(len(D), 1e9))
        member_of = dict(S="base", L1="link1", L2="link2", H="armend")
        for nm, s in G["straps"].items():
            R = F[s["frame"]][i]; D = s["d"] @ R.T; uu = s["u"]; lo = uu.min(1); hi = uu.max(1) + s["t"]
            jd = {}
            for k in (1, 2, 3):
                key = (s["frame"], k)
                if key in self.ax: jd[k] = np.degrees(np.arccos(np.clip(s["d"] @ self.ax[key], -1, 1))) * D2R * lo
            add(member_of[s["frame"]], D, lo, hi, np.full(len(D), s["hw"]), jd)
        for k, h in G["hub"].items():
            a_low = F[h["lower"]][i] @ h["a"]
            add(h["low_member"], a_low[None], np.array([(h["r"] * (h["U"] @ h["a"])).min()]), np.array([h["F"] + PLATE]), np.array([HUB_R]), {k: np.zeros(1)})
            add(h["up_member"], a_low[None], np.array([h["F"] + UP]), np.array([h["F"] + CROWN]), np.array([HUB_R]), {k: np.zeros(1)})
        R = self.F["H"][i]; dd = np.arange(DBAR0, DBAR1, 4.0); P = (ZBAR * WB[None] + dd[:, None] * DB[None]) @ R.T
        rr = np.linalg.norm(P, axis=1); add("bar", P / rr[:, None], rr, rr + BAR_T, np.full(len(dd), BAR_HW), {})
        return {m: (np.concatenate(v[0]), np.concatenate(v[1]), np.concatenate(v[2]), np.concatenate(v[3]),
                    {k: np.concatenate(x) for k, x in v[4].items()}) for m, v in out.items()}

    ADJ = {("base", "link1"): 1, ("link1", "link2"): 2, ("link2", "armend"): 3}

    def collide(self, G, i):
        bd = self.bodies(G, i); ms = list(bd)
        for x in range(len(ms)):
            for y in range(x + 1, len(ms)):
                a, b = ms[x], ms[y]
                if {a, b} == {"armend", "bar"}: continue                      # the neck lands on the bar
                k = self.ADJ.get((a, b)) or self.ADJ.get((b, a))
                Da, la, ha, wa, ja = bd[a]; Db, lb, hb, wb, jb = bd[b]
                ma = np.ones(len(Da), bool); mb = np.ones(len(Db), bool)
                if k:
                    ma &= ja.get(k, np.full(len(Da), 1e9)) > HUB_R + 2.0; mb &= jb.get(k, np.full(len(Db), 1e9)) > HUB_R + 2.0
                if not ma.any() or not mb.any(): continue
                ang = np.arccos(np.clip(Da[ma] @ Db[mb].T, -1, 1)); rr = 0.5 * (la[ma][:, None] + lb[mb][None, :])
                near = ang * rr < wa[ma][:, None] + wb[mb][None, :] + 1.0
                ov = np.minimum(ha[ma][:, None], hb[mb][None, :]) - np.maximum(la[ma][:, None], lb[mb][None, :]) + 0.5 > 0
                if (near & ov).any(): return f"{a}-{b}"
        return None

    def metal(self, G, i):
        """skin-facing sample points (k, 3) of pose i, member labels, and the non-facing metal (tops, crowns, walls)"""
        F = self.F; P, lab, T = [], [], []
        member_of = dict(S="base", L1="link1", L2="link2", H="armend")
        for nm, s in G["straps"].items():
            R = F[s["frame"]][i]; D = s["U"] @ R.T; uu = s["u"]
            P.append((D * uu[..., None])[s["keep"]]); lab += [nm] * int(s["keep"].sum())
            T.append((D * (uu + s["t"])[..., None])[s["keep"]])
        for k, h in G["hub"].items():
            R = F[h["lower"]][i]; D = h["U"] @ R.T
            P.append(D * h["r"][:, None]); lab += [f"hub{k}"] * len(D)
            a = R @ h["a"]; e1 = R @ h["e1"]; e2 = R @ h["e2"]; xy = h["xy"]
            T.append(a[None] * (h["F"] + CROWN) + xy[:, :1] * e1 + xy[:, 1:] * e2)              # crown
            ph = np.linspace(0, 2 * math.pi, 24, endpoint=False)
            for z in (h["F"], h["F"] + PLATE, h["F"] + 0.5 * (UP + CROWN), h["F"] + CROWN):        # walls
                T.append(a[None] * z + HUB_R * (np.cos(ph)[:, None] * e1 + np.sin(ph)[:, None] * e2))
        return np.concatenate(P), np.array(lab), np.concatenate(T)

    def evaluate(self, G, B=None, keep_d=False):
        B = B or self.B; B.reset(); why = dict(closure=0, flip=0, collision=0, skin=0, top=0); per = {}; dmin = []
        for i in range(len(B.poses)):
            if not self.closes[i]: B.record(i, None); why["closure"] += 1; continue
            if B.kind[i] == "clip" and self.flip[i]: B.record(i, None); why["flip"] += 1; continue
            c = self.collide(G, i)
            if c: B.record(i, None); why["collision"] += 1; continue
            P, lab, T = self.metal(G, i); d = B.record(i, P)
            dt = B.dist(i, T)
            if float(dt.min()) < 0 <= float(d.min()):
                B.res[i] = np.r_[d, dt.min()]; why["top"] += 1
            elif float(d.min()) < 0: why["skin"] += 1
            if B.kind[i] == "clip" and float(B.res[i].min()) >= 0:
                for m in np.unique(lab): per.setdefault(m, []).append(d[lab == m])
        r = B.report(); r["why_not"] = why
        r["members"] = {m: dict(n=int(sum(len(x) for x in v) / max(1, len(v))), inband14=round(float(np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 14))), 3),
                                inband10=round(float(np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 10))), 3),
                                median=round(float(np.median(np.concatenate(v))), 1)) for m, v in per.items()}
        return r

    def info(self, G):
        hub = G["hub"]; out = {}
        for k, h in hub.items():
            ca = h["U"] @ h["a"]; z = h["r"] * ca
            out[f"J{k}"] = dict(F=round(h["F"], 1), wedge=round(h["wedge"], 1), F_minus_lowest=round(h["F"] - float(z.min()), 1),
                                crown_over_lowest=round(h["F"] + CROWN - float(z.min()), 1), lower=h["low_member"], upper=h["up_member"])
        st = G["straps"]; m = 0.0
        for nm, s in st.items(): m += float(s["keep"].sum()) * SP * SP * s["t"] * TI
        for k, h in hub.items(): m += float((h["F"] + PLATE - h["r"] * (h["U"] @ h["a"])).sum()) * SP * SP * TI
        out["mass_g_links_neck_wedges"] = round(m, 1)
        m55 = m + sum(float(s["keep"].sum()) * SP * SP * (5.5 - s["t"]) * TI for nm, s in st.items() if nm != "neck")
        out["mass_g_at_5.5mm_links"] = round(m55, 1)
        out["margin_bench"] = [round(float(self.ch["margin"].min()), 1), round(float(self.ch["margin"].max()), 1)]
        out["theta_bench"] = [round(float(self.ch["theta"].min()), 1), round(float(self.ch["theta"].max()), 1)]
        mw, _ = margin_of(self.ch["b"], self.ch["W"], self.rig.RSw, self.rig.RHw); mf, _ = margin_of(self.ch["b"], self.ch["W"], self.rig.RSf, self.rig.RHf)
        out["margin_all_ws_fit"] = round(float(min(mw.min(), mf.min())), 1)
        out["max_step_10fps_deg"] = round(self.maxjump, 1)
        out["pole_radius_rest"] = [round(float(self.cl["link1"][3][0]), 1), round(float(self.cl["link1"][3][-1]), 1), round(float(self.cl["link2"][3][-1]), 1)]
        return out


# ---- sweep driver ----------------------------------------------------------------------------------------------------
def variants(stack=(("link2", "armend"), ("link1", "armend"), ("link2", "link2"), ("link1", "link2")), seat="wedge", width=12.0,
             fits=((1.0, 0.0), (0.97, 0.0), (0.93, 0.0), (1.0, 0.03), (1.0, 0.06), (1.0, 0.1))):
    """fits: (q, drop) - the catalogue's per-sample quantile q, or q = 1 over the fit poses minus the `drop` share whose
    skin pushes hardest (pose-coherent: a dropped pose is lost whole, every other pose stays clear)"""
    return [dict(q=q, drop=dr, seat=seat, j2_top=j2, j3_low=j3, width=width, t_link=3.0) for q, dr in fits for j2, j3 in stack]


def run_sweep(B, placements, var_list, path_json, log=print, k0=0):
    rig = Rig(B); res = json.load(open(path_json)) if os.path.exists(path_json) else []
    k = len(res); best = None
    for pl in placements:
        par = dict(PARAMS); par.update(pl)
        log(f"placement {pl}")
        try: D = Design(B, rig, par, log=log)
        except Exception as e: log(f"  failed: {e!r}"); continue
        for v in var_list:
            G = D.build(v); r = D.evaluate(G)
            entry = dict(k=k, t=now(), params={**pl, **v}, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"], follow=r["follow"],
                         contact=r["contact"], gap=r["gap"], why_not=r["why_not"], info=D.info(G), mode=r["mode"])
            res.append(entry); k += 1
            json.dump(res, open(path_json + ".tmp", "w"), indent=0); os.replace(path_json + ".tmp", path_json)
            log(f"  {v} -> gap {r['gap']} reach {r['reach']} follow {r['follow']} in14 {r['inband14']} in10 {r['inband10']} contact {r['contact']} {r['why_not']}")
            if best is None or r["gap"] < best[0]: best = (r["gap"], entry)
    return res, best


def plot(D, G, poses, out, title=""):
    """posterior and lateral views of the skin (grey) and the metal (undersides by member, tops faint) at given poses"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    B = D.B; cols = dict(link1="#2a6fdb", link2="#d9480f", neck="#7b2cbf", hub1="#0b7a3e", hub2="#0b7a3e", hub3="#0b7a3e")
    fig, ax = plt.subplots(len(poses), 2, figsize=(10, 4.6 * len(poses)))
    ax = np.atleast_2d(ax)
    for r, (i, lbl) in enumerate(poses):
        V, _ = B.skin(i); V = np.asarray(V); V = V[np.linalg.norm(V, axis=1) < 230]
        P, lab, T = D.metal(G, i); d = B.dist(i, P); dt = B.dist(i, T)
        for c, (h, v, nm) in enumerate(((2, 1, "posterior view (z lateral, y up)"), (0, 1, "lateral view (x anterior, y up)"))):
            a = ax[r, c]; sk = V[::3]
            if c == 0: sk = sk[sk[:, 0] < 15]
            else: sk = sk[sk[:, 2] > -10]
            a.scatter(sk[:, h], sk[:, v], s=0.3, c="#bbbbbb", lw=0)
            a.scatter(T[:, h], T[:, v], s=0.4, c="#999999", lw=0, alpha=0.4)
            for m in np.unique(lab):
                k = lab == m; a.scatter(P[k, h], P[k, v], s=1.2, c=cols.get(m, "k"), lw=0, label=m)
            bad = d < 0
            if bad.any(): a.scatter(P[bad, h], P[bad, v], s=6, c="red", marker="x", lw=0.8, label="inside body")
            a.set_aspect("equal"); a.set_xlim(-240, 240) if c == 0 else a.set_xlim(-240, 240); a.set_ylim(-260, 200)
            a.set_title(f"{lbl}: {nm}\nin-band 2-14 {np.mean((d >= 2) & (d <= 14)):.0%}, min {d.min():.1f} mm, tops min {dt.min():.1f} mm", fontsize=8)
            a.tick_params(labelsize=7)
        if r == 0: ax[0, 0].legend(fontsize=7, markerscale=5, loc="lower left")
    fig.suptitle(title, fontsize=9); fig.tight_layout(); fig.savefig(out, dpi=110); plt.close(fig)


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    if a[0] == "landscape":
        for x in margin_landscape(top=int(a[1]) if len(a) > 1 else 40): print([round(v, 1) for v in x])
    elif a[0] == "sweep":                                   # stage 1: placements x stacking x quantile on Bench(60, 160)
        stage = a[1] if len(a) > 1 else "1"
        B = CB.Bench(60, 160); print("bench", B.mode, len(B.poses), flush=True)
        path = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
        if stage == "1":
            top = [(-35.5, -17.6, 30.1, -76.8), (-30.4, -21.1, 35.4, -66.7), (-40.0, -12.0, 34.0, -88.6), (-25.6, -20.8, 33.5, -60.8),
                   (-30.1, -15.0, 40.7, -71.8), (-41.4, -16.5, 31.5, -87.4)]
            pls = [dict(b_az=-28.0, b_el=-19.0, w_d=42.0, w_a=-64.0, sigma=1)] + [dict(b_az=x[0], b_el=x[1], w_d=x[2], w_a=x[3], sigma=1) for x in top]
            pls.append(dict(b_az=-28.0, b_el=-19.0, w_d=42.0, w_a=-64.0, sigma=-1))
            run_sweep(B, pls, variants(), path, log=lambda s: print(s, flush=True))
        else:                                               # stage 2: a JSON list of placements + variants from argv
            spec = json.load(open(a[2])); run_sweep(B, spec["placements"], spec["variants"], path, log=lambda s: print(s, flush=True))
    elif a[0] == "plot":                                    # plot <params json> <out png>
        p = json.loads(a[1]); B = CB.Bench(60, 160); rig = Rig(B); par = dict(PARAMS); par.update(p)
        D = Design(B, rig, par); G = D.build(par); r = D.evaluate(G); print(r)
        ii = {k: j for j, k in enumerate(B.kind)}
        def pick(fn):
            return min(range(len(B.poses)), key=fn)
        rest = pick(lambda j: B.poses[j]["elev"] + (0 if B.kind[j] == "clip" else 50))
        over = pick(lambda j: -B.poses[j]["elev"] + (0 if D.closes[j] else 999))
        across = pick(lambda j: abs(B.poses[j]["plane"] - 120) + abs(B.poses[j]["elev"] - 90) / 2)
        back = pick(lambda j: (0 if "back" in B.clip[j] else 500) - B.poses[j]["axial"] * 0 + abs(B.poses[j]["elev"] - 40))
        plot(D, G, [(rest, f"rest #{rest} {B.poses[rest]}"), (over, f"overhead #{over} {B.poses[over]}"),
                    (across, f"across #{across} {B.poses[across]}"), (back, f"behind back #{back} {B.poses[back]}")], a[2],
             title=f"{NAME}: {p}\nreach {r['reach']} follow {r['follow']} in14 {r['inband14']} in10 {r['inband10']} contact {r['contact']} gap {r['gap']}")
    elif a[0] == "check":                                   # small bench, the catalogue seed, a few variants
        nc, nw = (int(a[1]), int(a[2])) if len(a) > 2 else (20, 40)
        B = CB.Bench(nc, nw); rig = Rig(B); print("bench", B.mode, len(B.poses))
        D = Design(B, rig, PARAMS)
        for v in variants()[:4]:
            G = D.build(v); r = D.evaluate(G); print(v, {k: r[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "gap", "why_not")})
            print("   ", r["members"]); print("   ", D.info(G))

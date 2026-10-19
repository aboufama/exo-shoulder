"""Concept model: BREATHING HUBS (id breathing-hubs) - the champion spherical 3R (every joint axis through the GH centre,
O20 hubs, strap links; tools/concept_baseline.py geometry and kinematics) whose J2 and / or J3 hub blocks float along
their own axis on short radial stages, each lift positively driven by a groove face cam whose input is a joint angle:
lift2 = c2(q1) (cam ring around J1 on the base, follower on link 1's root, pushrod along link 1 to a bell crank at the
J2 stage) or c2(q2) (cam ring around J2), lift3 = c3(q3) (cam ring around J3 between link 2's J3 end and the neck).

DOF: 3 ACTIVE (q1, q2, q3 - the spherical 3R's angles; the arm sets them through the two-circle closure on the design's
branch). 2 PASSIVE (the lifts): every axis passes through GH, so moving a pin block along its own axis changes no axis
direction and no joint angle; each lift is a fixed function of a joint angle through a positive (groove) cam, i.e. set
by the closure, never spare, never measured or powered, cannot sag unpowered. With J2 or J3 alone breathing: 1 passive.

Parts at real size (mm), the baseline's conventions (tools/concept_baseline.py) so the rigid control reproduces it:
  * hubs: O20 discs (r 10) on each axis, sampled like the baseline (2.5 mm grid, spherical cap at the hub level); the
    stack (lower plate face F -> cap crown F + 12.25, docs/HARDWARE.md v5) is checked for skin contact (walls + crown,
    contact-only) and for part collisions (exact cylinder);
  * cam rings: the spec's O32 x 3 mm ramp ring = annulus r 12-16 around the cam's joint, skin face at that joint's
    hub level (it rises with the hub it belongs to), sampled + scored like the hub disc, its walls contact-only;
  * links: 8 mm x 3 mm straps on the great circle between the joint axes (baseline arc_dirs), underside fixed in the
    link except over the stages; link 2 + stack offset and the link ends on their hubs exactly as the baseline;
    the neck (arm-end strap, humerus-fixed, 25 deg) as the baseline; link tops (+3 mm) contact-only;
  * stages (SPEC CORRECTION): the catalogue's 0.6 x 12 x 30 mm Ti leaves cannot travel 8-15 mm (fixed-guided leaf
    stress 3 E t d / L^2 = 3300 MPa at 15 mm, Ti yield ~900): modelled as a PINNED parallelogram (two 3 mm bars, 4 mm
    apart radially, length Ls, tangent to the sphere at mid-travel -> tangential axis shift Ls (1 - cos asin(T / 2 Ls)),
    reported, absorbed by the passive cuff slides). A pinned bar lifts its points LINEARLY with the distance from its
    root pivot, so the stage underside = fixed profile + ramp(v) x lift, v = 0 at the stage root, 1 at the hub
    footprint (w = 1 over the hub / link-end zone); the upper bar (+4 mm) is contact-only; the pushrod (1.5 mm, on top
    of link 1) contact-only.
Fitting (the baseline's percentile rule with the lift subtracted): every part sample's fixed radius = p-th percentile
over the FIT poses of (outermost skin radius under it - its lift weight x lift) + 2 mm; hubs (and their cam rings) flat
at the max of that over their samples. Cam: bin the input angle (4 deg), env(bin) = p-th percentile of the hub's need
(max over its disc + ring samples) over the bin and its two neighbours, F0 = max(min env, max env - T), c = clip(env -
F0, 0, T), then the slope limit |dc/dq| <= k mm/rad by a forward and a backward running max (the minimal slope-limited
majorant), linear between bin centres, constant beyond the fitted range. Fit = clip poses + EVEN workspace poses; the
ODD workspace poses are out of sample (reach_odd reported). 'fit_all' fits on every pose like the baseline.
Taken iff: closure on the branch with sing_deg margin; along each fit clip at the full 10 fps no joint steps > 25 deg
between consecutive frames (a flip = that frame not followed); every lift within [0, T] (by construction); no two
non-adjacent parts within 1 mm (hub stacks + cam rings as exact cylinders, straps as sampled mid-surfaces with their
half thickness; link 1 / link 2 and link 2 / neck adjacent at their shared joint: >= 0.15 running gap outside it);
no metal sample (scored or contact-only) inside the body (the bench's contact rule).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/breathing-hubs.py [diag|check|sweep|best|sketch] [chain]
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_baseline as BL                                # noqa: E402

ID = "breathing-hubs"; NAME = "Breathing hubs: cam-slaved radial joint stages on a spherical 3R"
D2R = math.pi / 180
CHAINS = {"r20_s1414_4": dict(az=BL.CHAMP["az"], el=BL.CHAMP["el"], a=list(BL.CHAMP["a"]), w=list(BL.CHAMP["w"]), branch=-1),
          "r18_s1392_1": dict(az=32.55159237005438, el=80.5631251310032, a=[77.40737955825345, 81.44799921589232], w=[71.38254048198503, 4.778729451604692], branch=-1),
          "agD_wbox_1": dict(az=61.11396484246086, el=84.79012323988644, a=[72.89803435585966, 60.006082882592224], w=[100.0, -7.084132311065103], branch=-1)}
HUB_R, STACK, T_LINK, WIDTH, CLEAR, NECK = 10.0, 3.15, 3.0, 8.0, 2.0, 25.0     # = BL.CHAMP
UP = STACK + T_LINK                                          # baseline: distal link rides + 6.15 on the proximal one
CREST = 12.25                                                # O20 v5: lower plate face -> cap crown
CAM_RI, CAM_RO, CAM_H = 12.0, 16.0, 3.0                      # O32 x 3 mm cam ring
BAR_T, BAR_GAP, ROD = 3.0, 4.0, 1.5                          # stage bars (thickness, radial spacing), pushrod
PART_CLEAR, RUN_GAP, JUMP, BIN = 1.0, 0.15, 25.0, 4.0
R_REF = 70.0                                                 # baseline arc / disc reference radius

PARAMS = dict(chain="r20_s1414_4", sing=10.0, pct=100.0, breathe="J2J3", in2="q1", in3="q3", T2=15.0, T3=15.0,
              slope=12.0, Ls=30.0, mid=0.0, fit_all=False, skin="outer")
SWEEP = dict(chain=list(CHAINS), sing=[8, 10, 12, 15], pct=[90, 95, 98, 100], breathe=["none", "J2", "J3", "J2J3"],
             in2=["q1", "q2"], in3=["q3", "q2"], T2=[8, 12, 15, 20], T3=[8, 12, 15, 20], slope=[6, 9, 12, 15],
             Ls=[20, 30, 40], mid=[0, 10], skin=["outer", "inner"])


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def plog(*a): print(*a, flush=True)


# ---- kinematics (BL.pins in the scapula frame + joint angles) ----------------------------------------------------------
def kin_S(d, HG, sing):
    A = [x * D2R for x in d["a"]]; b = BL.bvec(d["az"], d["el"]); W0 = BL.w_dir(*d["w"]); n = len(HG)
    p1 = np.ascontiguousarray(np.broadcast_to(b, (n, 3))); p3 = HG @ W0
    p2, ok = BL.circ_int(p1, A[0], p3, A[1], float(d["branch"]))
    ok = ok & BL.tri_ok(p1, p3, A[0], A[1], sing * D2R)

    def ang(ax, a, c):
        a_ = a - (a * ax).sum(-1, keepdims=True) * ax; c_ = c - (c * ax).sum(-1, keepdims=True) * ax
        return np.arctan2((np.cross(a_, c_) * ax).sum(-1), (a_ * c_).sum(-1))
    r1 = np.broadcast_to(unit(np.cross(b, [1.0, 0.0, 0.0])), (n, 3)); hv = HG @ unit(np.cross(W0, [0.0, 1.0, 0.0]))
    q = np.stack([ang(p1, r1, p2), ang(p2, p1, p3), ang(p3, p2, hv)], 1)
    return np.stack([p1, p2, p3], 1), ok, q


def continuity(d, Z, idx, sing):
    """every fit clip at its full 10 fps: a frame is not followed if a joint steps > JUMP deg from the previous frame"""
    names = list(Z["NAMES"]); cid = Z["CID"]; good = {}; flips = 0
    for nm in CB.FIT:
        ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        _, ok, q = kin_S(d, Z["HG"][ii].astype(float), sing); prev = None
        for j, gi in enumerate(ii):
            g = bool(ok[j])
            if g and prev is not None:
                dq = np.degrees(np.abs((q[j] - q[prev] + np.pi) % (2 * np.pi) - np.pi))
                if dq.max() > JUMP: g = False; flips += 1
            good[int(gi)] = g; prev = j if ok[j] else None
    return np.array([good.get(int(g), True) for g in idx]), flips


def annulus_dirs(u, ri, ro, step=2.5):
    """unit directions under an annulus ri <= r <= ro about axis u (P, 3), same basis / grid rule as BL.disc_dirs"""
    g = np.arange(-ro, ro + 1e-6, step); X, Y = np.meshgrid(g, g); rr = np.hypot(X, Y); keep = (rr <= ro) & (rr >= ri)
    X, Y = X[keep] / R_REF, Y[keep] / R_REF
    a = unit(np.cross(u, np.array([0.0, 0.0, 1.0]) + 1e-3)); b = np.cross(u, a)
    return unit(u[:, None] + X[None, :, None] * a[:, None] + Y[None, :, None] * b[:, None])


def circle_pts(P, z, r, n_min=6, sp=2.0):
    """ring of points of radius r about axis P (3,) at axial level z"""
    a = unit(np.cross(P, np.array([0.0, 0.0, 1.0]) + 1e-3)); b = np.cross(P, a)
    n = max(n_min, int(math.ceil(2 * math.pi * r / sp))); ps = 2 * math.pi * (np.arange(n) + 0.5) / n
    return z * P + r * (np.cos(ps)[:, None] * a + np.sin(ps)[:, None] * b)


def cyl_sdf(X, P, z0, z1, ro, ri=0.0):
    """signed distance to the solid (annular) cylinder about the axis P through GH, axial z0..z1, radius ri..ro"""
    a = X @ P; rho = np.linalg.norm(X - a[:, None] * P, axis=1)
    qx = np.abs(rho - (ri + ro) / 2) - (ro - ri) / 2; qy = np.abs(a - (z0 + z1) / 2) - (z1 - z0) / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)


# ---- precompute per (chain, sing): axes, angles, validity, sample directions, outermost skin radius per sample -----------
class Pre:
    PARTS = ("link1", "link2", "neck", "hub1", "hub2", "hub3", "cam1", "cam2", "cam3")

    def __init__(self, B, chain, sing, log=plog, limit=None):
        t0 = time.time(); Z = CB._poses_all(); self.B = B; d = CHAINS[chain]; self.d = d
        HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float); n = len(B.idx)
        PS, ok, q = kin_S(d, HG, sing); cont, flips = continuity(d, Z, B.idx, sing)
        self.ok_kin, self.cont, self.flips = ok, cont, flips; self.ok = ok & cont
        if limit is not None: self.ok[limit:] = False; self.ok_kin = self.ok_kin.copy(); self.ok_kin[limit:] = False
        self.limit = limit
        self.P = np.einsum("pij,pkj->pki", RS, PS); self.q = q
        self.harm = np.einsum("pij,j->pi", RS @ HG, np.array([0.0, -1.0, 0.0]))
        A = [x * D2R for x in d["a"]]; self.A = A; P = self.P
        ng = NECK * D2R; nk_v = unit(np.cos(ng) * P[:, 2] + np.sin(ng) * unit(self.harm - (self.harm * P[:, 2]).sum(-1, keepdims=True) * P[:, 2]))
        L1 = BL.arc_dirs(P[:, 0], P[:, 1], A[0], width=WIDTH); L2 = BL.arc_dirs(P[:, 1], P[:, 2], A[1], width=WIDTH)
        NK = BL.arc_dirs(P[:, 2], nk_v, ng, width=WIDTH)
        self.shape = dict(link1=L1.shape[1:3], link2=L2.shape[1:3], neck=NK.shape[1:3])
        self.ang = dict(link1=A[0], link2=A[1], neck=ng)
        self.D = dict(link1=L1.reshape(n, -1, 3), link2=L2.reshape(n, -1, 3), neck=NK.reshape(n, -1, 3))
        for k in range(3):
            self.D[f"hub{k + 1}"] = BL.disc_dirs(P[:, k], HUB_R)
            self.D[f"cam{k + 1}"] = annulus_dirs(P[:, k], CAM_RI, CAM_RO)
        self.Rs = {s: {nm: np.zeros(v.shape[:2]) for nm, v in self.D.items()} for s in ("outer", "inner")}
        valid = np.nonzero(self.ok_kin)[0]
        for i in valid:
            allD = np.concatenate([self.D[nm][i] for nm in self.PARTS])
            for s, rr in (("outer", BL.skin_radius(B, int(i), allD)), ("inner", skin_exit(B, int(i), allD))):
                o = 0
                for nm in self.PARTS:
                    m = self.D[nm].shape[1]; self.Rs[s][nm][i] = rr[o:o + m]; o += m
        self.R = self.Rs["outer"]
        log(f"  pre {chain} sing {sing}: {int(self.ok.sum())}/{n} valid (fold {int((~ok).sum())}, flip frames {int((ok & ~cont).sum())} bench / "
            f"{flips} full-rate), {time.time() - t0:.0f} s ({B.mode})")

    def need(self, hub, cam=False, clear=CLEAR):
        """per pose: the level a flat hub (+ its cam ring) at joint `hub` (1..3) needs (max over its samples) + clear"""
        R = self.R[f"hub{hub}"]
        if cam: R = np.concatenate([R, self.R[f"cam{hub}"]], 1)
        return R.max(1) + clear


def skin_exit(B, i, D, r0=25.0, r_max=260.0):
    """radius where the ray from the GH centre first EXITS the body (the shoulder's own skin), marching outward;
    unlike BL.skin_radius (the OUTERMOST crossing) it ignores body parts further out along the ray (the raised arm, the
    head) - whether a part placed there is squeezed by them is left to the exact contact check on every metal surface"""
    r = np.full(len(D), r0); act = np.ones(len(D), bool)
    for _ in range(80):
        if not act.any(): break
        a = np.nonzero(act)[0]; d = B.dist(i, D[a] * r[a, None])
        out = d >= 0.0; act[a[out]] = False
        r[a[~out]] += np.maximum(-d[~out], 0.3)
        act &= r < r_max
    return r


def wrap_center(q, sel):
    """unwrap an angle array about the circular mean of q[sel] (rad)"""
    c = math.atan2(np.sin(q[sel]).mean(), np.cos(q[sel]).mean()); return (q - c + np.pi) % (2 * np.pi) - np.pi


def fit_cam(qv, need, fit, T, slope, pct=100.0, binw=BIN):
    """slope-limited cam lift c(q) (mm) >= need - F0 binned; returns (lift per pose, info)"""
    qd = np.degrees(qv); f = np.nonzero(fit)[0]
    lo, hi = qd[f].min(), qd[f].max(); nb = max(1, int(math.ceil((hi - lo) / binw + 1e-9)))
    b = np.clip(((qd[f] - lo) / binw).astype(int), 0, nb - 1); env = np.full(nb, np.nan); spread = []
    for k in range(nb):
        m = (b >= k - 1) & (b <= k + 1)
        if m.any(): env[k] = np.percentile(need[f][m], pct)
        mk = b == k
        if mk.sum() >= 2: spread.append(float(need[f][mk].max() - need[f][mk].min()))
    good = np.isfinite(env); xc = lo + (np.arange(nb) + 0.5) * binw
    env = np.interp(xc, xc[good], env[good])
    F0 = max(env.min(), env.max() - T); c = np.clip(env - F0, 0, T); s = slope * binw * D2R
    for k in range(1, nb): c[k] = max(c[k], c[k - 1] - s)
    for k in range(nb - 2, -1, -1): c[k] = max(c[k], c[k + 1] - s)
    lift = np.interp(qd, xc, c)
    return lift, dict(xc=xc, c=c, F0=F0, spread_med=float(np.median(spread)) if spread else 0.0,
                      spread_p90=float(np.percentile(spread, 90)) if spread else 0.0, range_deg=float(hi - lo))


# ---- a configuration ---------------------------------------------------------------------------------------------------
class Config:
    def __init__(self, pre, prm, B):
        self.pre = pre; self.p = prm; P = pre; n = len(P.ok); self.R = P.Rs[prm["skin"]]
        ws = np.array([k == "ws" for k in B.kind]); wsi = np.cumsum(ws) - 1
        self.fitset = P.ok & (np.ones(n, bool) if prm["fit_all"] else (~ws | (ws & (wsi % 2 == 0))))
        br = prm["breathe"]; self.b2 = "J2" in br; self.b3 = "J3" in br
        self.cam_at = set()
        z = np.zeros(n); self.lift2 = z.copy(); self.lift3 = z.copy(); self.info = {}
        qin = lambda nm: wrap_center(P.q[:, int(nm[1]) - 1], self.fitset)
        if self.b2:
            cj = 1 if prm["in2"] == "q1" else 2; self.cam_at.add(cj)
            nd = P.need(2, cam=(cj == 2))
            self.lift2, self.info["c2"] = fit_cam(qin(prm["in2"]), nd, self.fitset, prm["T2"], prm["slope"], prm["pct"])
        if self.b3:
            cj = 3 if prm["in3"] == "q3" else 2; self.cam_at.add(cj)
            nd = P.need(3, cam=(cj == 3))
            self.lift3, self.info["c3"] = fit_cam(qin(prm["in3"]), nd, self.fitset, prm["T3"], prm["slope"], prm["pct"])
        self.mid = z.copy()
        if prm["mid"] > 0:                                   # level 2: link 2 mid-span four-bar on its own cam track (input in3)
            ns, nc = P.shape["link2"]; u = np.repeat(np.linspace(0, 1, ns), nc); sel = (u >= 0.35) & (u <= 0.65)
            nd = P.R["link2"][:, sel].max(1) + CLEAR
            self.mid, self.info["m2"] = fit_cam(qin(prm["in3"]), nd, self.fitset, prm["mid"], prm["slope"], prm["pct"])
            if prm["in3"] == "q2": self.cam_at.add(2)
        self.off = dict(link1=0.0, link2=UP, neck=2 * UP, hub1=0.0, hub2=0.0, hub3=UP, cam1=0.0, cam2=0.0, cam3=UP)
        self.W = self.weights()
        self.fit()

    def weights(self):
        """lift weights per sample: (w2, w3, wmid) for each part"""
        P = self.pre; W = {}; Ls = self.p["Ls"]
        for nm in ("link1", "link2", "neck"):
            ns, nc = P.shape[nm]; th = np.linspace(0, 1, ns) * P.ang[nm] * R_REF      # mm along the link from its start
            L = P.ang[nm] * R_REF; end = max(2, ns // 6); zone = th[end - 1] if ns > 1 else 0.0
            zone = max(zone, HUB_R)
            free = L - 2 * zone if nm == "link2" else L - zone
            ls = max(4.0, min(Ls, free / (2 if nm == "link2" else 1)))
            ramp_from = lambda d: np.clip(1 - (d - zone) / ls, 0, 1)                    # linear (pinned bar), 1 in the hub zone
            w2 = np.zeros(ns); w3 = np.zeros(ns); wm = np.zeros(ns)
            if nm == "link1" and self.b2: w2 = ramp_from(L - th)
            if nm == "link2":
                if self.b2: w2 = ramp_from(th)
                if self.b3: w3 = ramp_from(L - th)
                u = th / L; wm = 4 * u * (1 - u) * (1 - w2) * (1 - w3) if self.p["mid"] > 0 else wm
            if nm == "neck" and self.b3: w3 = ramp_from(th)
            W[nm] = tuple(np.repeat(x, nc) for x in (w2, w3, wm))
        for k in (1, 2, 3):
            for nm in (f"hub{k}", f"cam{k}"):
                m = P.D[nm].shape[1]; o = np.ones(m); zr = np.zeros(m)
                W[nm] = (o if (k == 2 and self.b2) else zr, o if (k == 3 and self.b3) else zr, zr)
        return W

    def lift_of(self, nm):
        w2, w3, wm = self.W[nm]
        return self.lift2[:, None] * w2[None] + self.lift3[:, None] * w3[None] + self.mid[:, None] * wm[None]

    def fit(self):
        P = self.pre; f = np.nonzero(self.fitset)[0]; pct = self.p["pct"]; prof = {}
        parts = ["link1", "link2", "neck", "hub1", "hub2", "hub3"] + [f"cam{k}" for k in sorted(self.cam_at)]
        self.parts = parts
        for nm in parts: prof[nm] = np.percentile((P.R[nm] - self.lift_of(nm))[f], pct, axis=0) + CLEAR
        for k in (1, 2, 3):                                   # flat hubs (+ their cam ring at the same level)
            lv = prof[f"hub{k}"].max()
            if f"cam{k}" in prof: lv = max(lv, prof[f"cam{k}"].max()); prof[f"cam{k}"] = np.full_like(prof[f"cam{k}"], lv)
            prof[f"hub{k}"] = np.full_like(prof[f"hub{k}"], lv)
        hub_of = {"link1": ("hub1", "hub2"), "link2": ("hub2", "hub3"), "neck": ("hub3", None)}
        for nm, (h0, h1) in hub_of.items():                   # link ends sit on their hubs (= tools/concept_baseline.py)
            ns, nc = P.shape[nm]; pr = prof[nm].reshape(ns, nc); end = max(2, ns // 6)
            pr[:end] = np.maximum(pr[:end], prof[h0].max() + self.off[nm] - self.off[h0])
            if h1: pr[-end:] = np.maximum(pr[-end:], prof[h1].max() + self.off[nm] - self.off[h1])
            prof[nm] = pr.reshape(-1)
        self.prof = prof
        self.level = {k: float(prof[f"hub{k}"][0]) for k in (1, 2, 3)}

    def radius(self, nm, i):
        return self.prof[nm] + self.lift_of(nm)[i] + self.off[nm]

    def metal(self, i):
        """(scored points, contact-only points, parts for collisions) of bench pose i (thorax frame)"""
        P = self.pre; sc, co, parts = [], [], {}
        for nm in self.parts:
            r = self.radius(nm, i); X = P.D[nm][i] * r[:, None]; sc.append(X)
            if nm.startswith("link") or nm == "neck":
                top = P.D[nm][i] * (r + T_LINK)[:, None]; co.append(top); parts[nm] = X + T_LINK / 2 * P.D[nm][i]
                w2, w3, _ = self.W[nm]; st = (w2 > 0) & (w2 < 1) | (w3 > 0) & (w3 < 1)
                if st.any(): co.append(P.D[nm][i][st] * (r[st] + BAR_T + BAR_GAP)[:, None])     # stage upper bar
        for k in (1, 2, 3):                                   # hub stacks: walls + crown (contact-only), cylinders
            ax = P.P[i, k - 1]; z = self.radius(f"hub{k}", i)[0]
            co.append(np.concatenate([circle_pts(ax, z + h, HUB_R) for h in np.arange(0, CREST + 1e-6, 2.0)]
                                     + [circle_pts(ax, z + CREST, r) for r in np.arange(0, HUB_R, 2.0)]))
            parts[f"hub{k}"] = ("cyl", ax, z, z + CREST, HUB_R, 0.0)
            if k in self.cam_at:
                co.append(np.concatenate([circle_pts(ax, z + h, CAM_RO) for h in (0.0, 1.5, CAM_H)] + [circle_pts(ax, z + CAM_H, r) for r in (12.0, 14.0)]))
                parts[f"cam{k}"] = ("cyl", ax, z, z + CAM_H, CAM_RO, CAM_RI)
        if 1 in self.cam_at and self.b2 and self.p["in2"] == "q1":   # pushrod on top of link 1 (centre line)
            ns, nc = P.shape["link1"]; cl = np.arange(ns) * nc + nc // 2
            co.append(P.D["link1"][i][cl] * (self.radius("link1", i)[cl] + T_LINK + ROD)[:, None])
        if 3 in self.cam_at and self.p["in3"] == "q2" and self.b3:   # pushrod on top of link 2
            ns, nc = P.shape["link2"]; cl = np.arange(ns) * nc + nc // 2
            co.append(P.D["link2"][i][cl] * (self.radius("link2", i)[cl] + T_LINK + ROD)[:, None])
        return np.concatenate(sc), np.concatenate(co), parts

    def collide(self, i, parts):
        """first non-adjacent pair closer than PART_CLEAR, or None"""
        cyl = {k: v for k, v in parts.items() if isinstance(v, tuple)}
        adj = {("hub1", "link1"), ("cam1", "link1"), ("hub2", "link1"), ("hub2", "link2"), ("cam2", "link1"), ("cam2", "link2"),
               ("hub3", "link2"), ("hub3", "neck"), ("cam3", "link2"), ("cam3", "neck"), ("hub1", "cam1"), ("hub2", "cam2"), ("hub3", "cam3")}
        for a, ca in cyl.items():
            for b, X in parts.items():
                if a == b or (a, b) in adj or (b, a) in adj or a[-1] == b[-1] and b.startswith(("hub", "cam")): continue
                if isinstance(X, tuple):
                    if b < a: continue
                    cb = X; pts = np.concatenate([circle_pts(cb[1], z, cb[4]) for z in np.linspace(cb[2], cb[3], 4)]
                                                 + [circle_pts(cb[1], cb[3], r) for r in np.arange(0, cb[4], 3.0)])
                    if cyl_sdf(pts, *ca[1:]).min() < PART_CLEAR: return a + "-" + b
                elif len(X) and cyl_sdf(X, *ca[1:]).min() < T_LINK / 2 + PART_CLEAR: return a + "-" + b
        for a, b, gap in (("link1", "link2", RUN_GAP), ("link2", "neck", RUN_GAP), ("link1", "neck", PART_CLEAR)):
            dmin = cKDTree(parts[a]).query(parts[b], k=1)[0].min()
            if dmin < T_LINK + gap - 0.1: return a + "-" + b
        return None


def evaluate(B, pre, prm, details=False):
    C = Config(pre, prm, B); B.reset(); why = {}
    for i in range(len(B.idx)):
        if not pre.ok[i]:
            k = "fold" if not pre.ok_kin[i] else "flip"; why[k] = why.get(k, 0) + 1; continue
        sc, co, parts = C.metal(i)
        c = C.collide(i, parts)
        if c: why["self:" + c] = why.get("self:" + c, 0) + 1; continue
        d = B.dist(i, np.concatenate([sc, co])); ds, dc = d[:len(sc)], d[len(sc):]
        B.res[i] = np.concatenate([ds, dc[dc < 0]])
        if float(d.min()) < 0: why["contact" if ds.min() < 0 else "contact(walls/tops)"] = why.get("contact" if ds.min() < 0 else "contact(walls/tops)", 0) + 1
    r = B.report(); r["why"] = why; r["level"] = {k: round(v, 1) for k, v in C.level.items()}
    ws = [j for j, k in enumerate(B.kind) if k == "ws"]; odd = [j for n_, j in enumerate(ws) if n_ % 2 == 1]
    okp = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= 0
    r["reach_odd"] = round(float(np.mean([okp(j) for j in odd])), 4)
    for nm, inf in C.info.items():
        r[nm] = dict(F0=round(inf["F0"], 1), lift_max=round(float(inf["c"].max()), 1), spread_med=round(inf["spread_med"], 1),
                     spread_p90=round(inf["spread_p90"], 1), range_deg=round(inf["range_deg"], 0))
    r["lift_mean"] = [round(float(C.lift2[pre.ok].mean()), 2), round(float(C.lift3[pre.ok].mean()), 2)]
    T = max(prm["T2"] if C.b2 else 0, prm["T3"] if C.b3 else 0); Ls = prm["Ls"]
    r["axis_shift_mm"] = round(Ls * (1 - math.cos(math.asin(min(1.0, T / 2 / Ls)))), 2) if T > 0 else 0.0
    if details:
        cl = [j for j, k in enumerate(B.kind) if k == "clip" and okp(j)]; per = {}
        for j in cl:
            for nm in C.parts:
                X = pre.D[nm][j] * C.radius(nm, j)[:, None]; per.setdefault(nm, []).append(B.dist(j, X))
        r["parts"] = {nm: dict(n=int(np.mean([len(x) for x in v])), inband14=round(float(np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 14))), 3),
                               med=round(float(np.median(np.concatenate(v))), 1)) for nm, v in per.items()}
    return r, C


# ---- diagnostics: is the hub's need a function of the cam input? ---------------------------------------------------------
def diag(B, chain="r20_s1414_4", sing=10.0, limit=None):
    pre = Pre(B, chain, sing, limit=limit); ok = pre.ok; out = {}
    for hub, cams in ((2, ("q1", "q2", "q3")), (3, ("q3", "q2", "q1"))):
        nd = pre.need(hub)
        out[f"J{hub} need"] = dict(min=round(float(nd[ok].min()), 1), p10=round(float(np.percentile(nd[ok], 10)), 1), med=round(float(np.median(nd[ok])), 1),
                                    p90=round(float(np.percentile(nd[ok], 90)), 1), max=round(float(nd[ok].max()), 1))
        for qn in cams:
            qv = wrap_center(pre.q[:, int(qn[1]) - 1], ok)
            for T in (15.0, 30.0):
                lift, inf = fit_cam(qv, nd, ok, T, 12.0)
                F0 = float(np.max(nd[ok] - lift[ok])); hgt = F0 + lift
                out[f"J{hub} by {qn} T{T:.0f}"] = dict(range_deg=round(inf["range_deg"]), spread_med=round(inf["spread_med"], 1), spread_p90=round(inf["spread_p90"], 1),
                                                       rigid_gap_mean=round(float((nd[ok].max() - nd[ok]).mean()), 1),
                                                       cam_gap_mean=round(float((hgt[ok] - nd[ok]).mean()), 1), lift_max=round(float(lift[ok].max()), 1))
    for k, v in out.items(): plog(f"  {k}: {v}")
    return pre, out


# ---- sweep -------------------------------------------------------------------------------------------------------------
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")


class Runner:
    def __init__(self, B, log=plog, fresh=True):
        self.B = B; self.log = log; self.pres = {}
        self.entries = [] if fresh or not os.path.exists(SWEEP_JSON) else json.load(open(SWEEP_JSON))

    def pre(self, prm):
        key = (prm["chain"], float(prm["sing"]))
        if key not in self.pres:
            if len(self.pres) > 4: self.pres.pop(next(iter(self.pres)))
            self.pres[key] = Pre(self.B, prm["chain"], float(prm["sing"]), log=self.log)
        return self.pres[key]

    def run(self, over, tag="", record=True):
        prm = dict(PARAMS); prm.update(over)
        for e in self.entries:
            if e["params"] == prm: return e
        t = time.time(); r, C = evaluate(self.B, self.pre(prm), prm)
        e = dict(k=len(self.entries), t=now(), params=prm, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                 follow=r["follow"], contact=r["contact"], gap=r["gap"], reach_odd=r["reach_odd"], level=r["level"],
                 c2=r.get("c2"), c3=r.get("c3"), lift_mean=r["lift_mean"], axis_shift_mm=r["axis_shift_mm"], why=r["why"], tag=tag)
        if record:
            self.entries.append(e)
            os.makedirs(os.path.dirname(SWEEP_JSON), exist_ok=True)
            json.dump(self.entries, open(SWEEP_JSON + ".tmp", "w"), indent=0); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
        short = {k: v for k, v in prm.items() if v != PARAMS[k]}
        self.log(f"[{e['k']:3d}] gap {e['gap']:6.2f}  ib14 {e['inband14']:.3f} ib10 {e['inband10']:.3f} reach {e['reach']:.3f} (odd {e['reach_odd']:.3f}) "
                 f"follow {e['follow']:.3f} contact {e['contact']:.3f}  lv {e['level']} c2 {e['c2']} c3 {e['c3']}  {short}  {tag}  ({time.time() - t:.1f} s) {e['why']}")
        return e

    def best(self, filt=lambda e: True):
        c = [e for e in self.entries if filt(e)]; return min(c, key=lambda e: e["gap"]) if c else None


def breathes(e): return e["params"]["breathe"] != "none"


def sweep(B):
    R = Runner(B, plog, fresh=os.environ.get("BH_FRESH", "1") == "1")
    ctrl = lambda prm: dict(prm, breathe="none")
    # A: champion chain, layouts x inputs x percentile (each with its rigid control)
    for pct in (100, 98, 95, 90):
        R.run(dict(breathe="none", pct=pct), "A control")
        for br, i2, i3 in (("J2", "q1", "q3"), ("J2", "q2", "q3"), ("J3", "q1", "q3"), ("J3", "q1", "q2"), ("J2J3", "q1", "q3"), ("J2J3", "q2", "q3")):
            R.run(dict(breathe=br, in2=i2, in3=i3, pct=pct), "A layout")
    cur = dict(R.best(breathes)["params"])
    # B: travel and slope
    for T in (8, 12, 20, 25):
        R.run(dict(cur, T2=T, T3=T), "B travel")
    cur = dict(R.best(breathes)["params"])
    for T2 in (8, 12, 15, 20, 25):
        R.run(dict(cur, T2=T2), "B T2")
    cur = dict(R.best(breathes)["params"])
    for T3 in (8, 12, 15, 20, 25):
        R.run(dict(cur, T3=T3), "B T3")
    cur = dict(R.best(breathes)["params"])
    for s in (6, 9, 15, 20):
        R.run(dict(cur, slope=s), "B slope")
    cur = dict(R.best(breathes)["params"])
    for ls in (20, 40):
        R.run(dict(cur, Ls=ls), "B stage")
    R.run(dict(cur, mid=10.0), "B mid-span morph")
    cur = dict(R.best(breathes)["params"])
    # C: base chains and singular margin (each with its control)
    for ch in CHAINS:
        for sg in (8, 10, 12, 15):
            for pct in sorted({float(cur["pct"]), 100.0}):
                R.run(dict(cur, chain=ch, sing=sg, pct=pct), "C chain"); R.run(ctrl(dict(cur, chain=ch, sing=sg, pct=pct)), "C control")
    cur = dict(R.best(breathes)["params"])
    # D: refine at the best chain
    for pct in (85, 90, 95, 98, 100):
        R.run(dict(cur, pct=pct), "D pct"); R.run(ctrl(dict(cur, pct=pct)), "D control")
    cur = dict(R.best(breathes)["params"])
    for br, i2, i3 in (("J2", "q1", "q3"), ("J2", "q2", "q3"), ("J3", "q1", "q3"), ("J2J3", "q1", "q3"), ("J2J3", "q2", "q3"), ("J2J3", "q1", "q2"), ("J2J3", "q2", "q2")):
        R.run(dict(cur, breathe=br, in2=i2, in3=i3), "D layout")
    cur = dict(R.best(breathes)["params"])
    for T in (10, 15, 20, 25):
        R.run(dict(cur, T2=T, T3=T), "D travel")
    for s in (9, 12, 15):
        R.run(dict(cur, slope=s), "D slope")
    best = R.best(breathes); plog("BEST BREATHING", json.dumps(best))
    ctl = R.run(ctrl(best["params"]), "control of best"); plog("ITS CONTROL", json.dumps(ctl))
    ins = R.run(dict(best["params"], fit_all=True), "best, fit on all (baseline protocol)"); R.run(ctrl(ins["params"]), "control, fit on all")
    return R


def check(B, prm=None, limit=None):
    prm = dict(PARAMS, **(prm or {})); pre = Pre(B, prm["chain"], prm["sing"], limit=limit)
    for over in (dict(), dict(breathe="none"), dict(fit_all=True), dict(breathe="none", fit_all=True)):
        p2 = dict(prm, **over); r, C = evaluate(B, pre, p2, details=True)
        plog(json.dumps({k: v for k, v in p2.items() if v != PARAMS.get(k)}), json.dumps(r, default=str))
        taken = [i for i in range(len(B.idx)) if pre.ok[i]]
        el = np.array([B.poses[i]["elev"] for i in taken]); pl = np.array([B.poses[i]["plane"] for i in taken])
        named = dict(rest=taken[int(np.argmin(el))], overhead=taken[int(np.argmax(el))], across=taken[int(np.argmax(pl))])
        bb = [i for i in taken if B.clip[i] == "Reach back pocket"]
        if bb: named["behind back"] = bb[len(bb) // 2]
        for nm, i in named.items():
            sc, co, parts = C.metal(i); d = B.dist(i, sc); dc = B.dist(i, co)
            plog(f"   {nm:12s} {({k: round(v) for k, v in B.poses[i].items()})} q {np.round(np.degrees(pre.q[i]))} lift2 {C.lift2[i]:.1f} lift3 {C.lift3[i]:.1f} -> "
                 f"{len(sc)} pts, in band 14 {np.mean((d >= 2) & (d <= 14)):.2f}, min {d.min():.1f} / contact-only min {dc.min():.1f}, median {np.median(d):.1f}, self {C.collide(i, parts)}")
    return pre


def sketch(B, prm, path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    pre = Pre(B, prm["chain"], prm["sing"]); r, C = evaluate(B, pre, prm)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    rest = min(taken, key=lambda i: B.poses[i]["elev"]); top = max(taken, key=lambda i: B.poses[i]["elev"])
    cols = dict(hub1="#d1495b", hub2="#edae49", hub3="#00798c", link1="#66a182", link2="#8d6a9f", neck="#30638e", cam1="#aa3377", cam2="#aa3377", cam3="#aa3377")
    fig = plt.figure(figsize=(13, 9))
    for k, i in enumerate((rest, top)):
        ax = fig.add_subplot(2, 2, k + 1, projection="3d"); V, F = B.skin(i); V = np.asarray(V)
        near = V[np.linalg.norm(V, axis=1) < 150][::7]; ax.scatter(near[:, 2], near[:, 0], near[:, 1], s=0.3, c="#bbbbbb", alpha=0.3)
        for nm in C.parts:
            X = pre.D[nm][i] * C.radius(nm, i)[:, None]; ax.scatter(X[:, 2], X[:, 0], X[:, 1], s=1.0, c=cols[nm], label=nm)
        p = B.poses[i]; ax.set_title(f"{'rest' if k == 0 else 'highest pose taken'}: plane {p['plane']:.0f}, elev {p['elev']:.0f}, axial {p['axial']:.0f}; "
                                     f"lift2 {C.lift2[i]:.1f}, lift3 {C.lift3[i]:.1f} mm", fontsize=9)
        ax.view_init(elev=22, azim=-50 if k == 0 else -30); ax.set_xlabel("z lateral"); ax.set_ylabel("x anterior"); ax.set_zlabel("y up")
        ax.set_box_aspect((1, 1, 1)); ax.set_xlim(-80, 120); ax.set_ylim(-110, 90); ax.set_zlim(-90, 110)
        if k == 0: ax.legend(fontsize=7, markerscale=5, loc="upper left")
    for k, (nm, hub) in enumerate((("c2", 2), ("c3", 3))):
        ax = fig.add_subplot(2, 2, 3 + k)
        if nm not in C.info: ax.set_axis_off(); continue
        inp = prm["in2"] if hub == 2 else prm["in3"]; qv = np.degrees(wrap_center(pre.q[:, int(inp[1]) - 1], C.fitset))
        nd = pre.need(hub, cam=(hub in C.cam_at)); ok = pre.ok; lv = C.level[hub]
        ax.scatter(qv[ok], nd[ok], s=6, c="#888888", label="need per pose (flat hub + cam ring, +2 mm)")
        ax.axhline(lv, color="#d1495b", lw=1, ls="--", label="hub level, lift 0")
        ax.plot(C.info[nm]["xc"], lv + C.info[nm]["c"], color="#00798c", lw=2, label=f"hub level + cam lift (slope <= {prm['slope']} mm/rad)")
        ax.axhline(nd[ok].max(), color="#30638e", lw=1, ls=":", label="rigid hub (max need)")
        ax.set_xlabel(f"cam input {inp} (deg, centred)"); ax.set_ylabel("radius from GH (mm)"); ax.set_title(f"J{hub} cam", fontsize=9); ax.legend(fontsize=7)
    fig.suptitle(f"{ID}: {prm['chain']} sing {prm['sing']}, breathe {prm['breathe']} (in {prm['in2']}/{prm['in3']}), T {prm['T2']}/{prm['T3']} mm, slope {prm['slope']}, "
                 f"p{prm['pct']:.0f}; gap {r['gap']}, in band 14 {r['inband14']}, reach {r['reach']}, follow {r['follow']}", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=100); plt.close(fig); return r


def dev_bench():
    """the bench on the partial cache while it builds (first n poses written)"""
    B = CB.Bench(n_clip=60, n_ws=160)
    if B.grid is None:
        p = os.path.join(CB.CACHE, B.key, "grid.tmp.npy")
        if os.path.exists(p):
            g = np.load(p, mmap_mode="r"); B.grid = g; B.mode = "fast-partial"
            n = sum(1 for j in range(g.shape[0]) if g[j, 0, 0, 0] != 0); return B, n
    return B, None


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "dev-diag":
        B, lim = dev_bench(); plog("bench", B.mode, "limit", lim); diag(B, sys.argv[2] if len(sys.argv) > 2 else "r20_s1414_4", limit=lim)
    elif mode == "dev-check":
        B, lim = dev_bench(); plog("bench", B.mode, "limit", lim); check(B, json.loads(sys.argv[2]) if len(sys.argv) > 2 else None, limit=lim)
    elif mode == "diag":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode); diag(B, sys.argv[2] if len(sys.argv) > 2 else "r20_s1414_4")
    elif mode == "check":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode); check(B, json.loads(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif mode == "sweep":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode, len(B.idx)); sweep(B)
    elif mode == "sketch":
        B = CB.Bench(n_clip=60, n_ws=160); prm = dict(PARAMS, **json.loads(sys.argv[2])) if len(sys.argv) > 2 else dict(PARAMS)
        plog(sketch(B, prm, os.path.join(REPO, "docs", "concepts", "img", f"{ID}.png")))

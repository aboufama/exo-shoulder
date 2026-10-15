"""fivebar-roll: spherical five-bar pointer (two base-driven cranks + two couplers closing on one arm hub at the
arm-fixed axis W) plus an active roll of the arm about W. Spec: docs/concepts/catalogue.json entry "fivebar-roll".

Topology (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    S (scapula handler) -- A1 O20 hub, axis u1 (ACTIVE) -> crank 1 (arc a1) -- B1 elbow pin P14, axis e1 (passive)
                         -> coupler 1 (arc c1) -- C at W (passive) / D at W (ACTIVE roll) -> arm-end plate + neck
    S                   -- A2 O20 hub, axis u2 (ACTIVE) -> crank 2 (arc a2) -- B2 elbow pin, axis e2 (passive)
                         -> coupler 2 (arc c2) -- C at W
DOF (spherical Gruebler): 6 bodies (S, crank 1, crank 2, coupler 1, coupler 2, arm), 6 revolutes:
3 (6 - 1 - 6) + 6 = 3. The 5R loop sets W's direction (2), D the roll about W (1). Given the arm pose, W = RS HG W0 is
known; each elbow is the intersection of the cone a_k about u_k with the cone c_k about W on branch sigma_k; C and D
follow. Active: A1, A2, D. Passive (set by the closure): B1, B2, C. No undriven spare coordinate.

Conventions copied from tools/concept_baseline.py (the swarm's reference):
  * frames: scapula RS and humerus-in-scapula HG of each bench pose from the evaluator's pose file (CB._poses_all()),
    thorax = RS @ (scapula-frame vector); bvec / w_dir as band_impl; down-the-arm axis HG (0, -1, 0);
  * straps: great-circle arcs between their two joint axes, 8 mm wide x 3 mm, underside sampled every 2 mm along and
    across at r_ref 70 mm (~1 point / 4 mm2); the neck is a 25 deg strap from W toward the humerus axis, fixed to the
    arm (baseline neck_deg);
  * rigid shapes: each sample's radius is the p-th percentile, over the kinematically valid poses, of the OUTERMOST
    skin radius along its direction (sphere tracing on B.dist), + 2 mm clearance; a sweep over p trades reach against
    closeness (the worst poses become contact poses), as in the baseline;
  * layer step at an O20 joint: the upper member's underside 6.15 mm (3.15 stack + 3 link) above the lower one's.
Real sizes (spec, docs/HARDWARE.md):
  * base hubs: O20, flat discs r 10 at the max level over the disc, crown 12.25 (coaxial variant: one disc r 12 with
    the two cranks stacked, crown 16);
  * elbow pins P14: flat discs r 7, crank = lower member, coupler underside 3.15 above it, crown 8;
  * arm hub at W: two bearing rows, flat disc r 12; three stacked bodies (arm plate, coupler 1, coupler 2 - coupler 1
    in the middle because it carries both C and D), layers 0 / 6.15 / 12.3, crown 16.3; order 'arm_low' (arm plate
    on the skin) or 'arm_top' (coupler 2 on the skin, the arm plate on top);
  * near a hub a strap sits on the hub at its layer over the hub radius + 2 mm land, then ramps down to its own
    fitted profile at <= 45 deg (spec improvement: the baseline lifts the whole upper link by the layer step).
Taken (honesty rules): both legs close with the leg-singularity margin (tri_ok, `margin` deg), the couplers' planes
at W at least `par` deg apart (parallel singularity), the elbows at least `sep` deg apart; clip frames are followed
along EVERY 10 fps frame of the clip between consecutive bench frames (all valid, no joint jump > 25 deg between
consecutive 10 fps frames); no two parts closer than 1 mm unless they share a joint (and then only within the joint's
hub radius + 2 mm of its axis): sampled volumes [r, r + t], lateral test 1.5 mm; contact: skin-facing undersides are
recorded; tops and crowns are checked too (any inside point is appended so the pose counts as contact).

    python3 docs/concepts/models/fivebar-roll.py kin            # kinematic screen of the seed configs (no skin)
    python3 docs/concepts/models/fivebar-roll.py check [nc nw]  # seed config on a bench, a few named poses printed
    python3 docs/concepts/models/fivebar-roll.py sweep          # the sweep on Bench(60, 160): sweeps/, rows/
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402
import concept_baseline as BL                                              # noqa: E402

ID = "fivebar-roll"
D2R = math.pi / 180
T, WID = 3.0, 8.0                                                          # strap section (baseline)
UP = 3.15 + 3.0                                                            # O20 layer step (baseline)
UP_E = 3.15                                                                # P14 elbow: coupler underside over the crank
HUB = dict(base=(10.0, 12.25), coax=(12.0, 16.0), elbow=(7.0, 8.0), w=(12.0, 2 * UP + T + 1.0))   # (radius, crown)
LAND, SLOPE = 2.0, 1.0
SP, R_REF = 2.0, 70.0
LAT, RAD_CLR = 1.5, 1.0                                                    # collision: lateral test, radial clearance
JUMP = 25.0
H0 = 65.0                                                                  # nominal disc height for its sample rays

PARAMS = dict(u1=(-60.0, 40.0), u2=(-40.0, 40.0), a1=60.0, a2=60.0, c1=120.0, c2=120.0, w=(60.0, 30.0),
              s1=1, s2=-1, margin=8.0, par=12.0, sep=17.0, worder="arm_low", neck_deg=25.0, pct=90, clear=2.0)
SWEEP = dict(u1=("az -90..180", "el 35..75"), u2=("az -90..180", "el 35..75", "coaxial allowed"), a=(40, 70), c=(50, 130),
             w=("delta 60..115", "az -60..+20"), s=(1, -1), par=(8, 15), worder=("arm_low", "arm_top"), pct=(70, 80, 90, 95, 100))
PART = ["BH1", "BH2", "K1", "K2", "E1", "E2", "C1", "C2", "WH", "N"]


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def tang(at, to):
    return unit(to - (to * at).sum(-1, keepdims=True) * at)


def sangle(at, a, b):
    ta, tb = tang(at, a), tang(at, b)
    return np.degrees(np.arctan2((at * np.cross(ta, tb)).sum(-1), (ta * tb).sum(-1)))


def coax(p):
    return tuple(p["u1"]) == tuple(p["u2"])


# ------------------------------------------------------------------------------------------------ kinematics
def kin(p, HG):
    """scapula-frame axes and validity for humerus rotations HG (N, 3, 3): dict(u1, u2, e1, e2, W, harm, ok, q (N, 6))"""
    N = len(HG); u1 = np.broadcast_to(BL.bvec(*p["u1"]), (N, 3)); u2 = np.broadcast_to(BL.bvec(*p["u2"]), (N, 3))
    W = np.einsum("nij,j->ni", HG, BL.w_dir(*p["w"])); harm = np.einsum("nij,j->ni", HG, np.array([0.0, -1.0, 0.0]))
    m = p["margin"] * D2R; e, okl = [], []
    for u, a, c, s in ((u1, p["a1"], p["c1"], p["s1"]), (u2, p["a2"], p["c2"], p["s2"])):
        ek, h = BL.circ_int(u, a * D2R, W, c * D2R, float(s)); e.append(unit(ek)); okl.append(h & BL.tri_ok(u, W, a * D2R, c * D2R, m))
    e1, e2 = e
    n1, n2 = unit(np.cross(e1, W)), unit(np.cross(e2, W))
    okp = np.linalg.norm(np.cross(n1, n2), axis=-1) >= math.sin(p["par"] * D2R)
    oks = np.arccos(np.clip((e1 * e2).sum(-1), -1, 1)) >= p["sep"] * D2R
    ok = okl[0] & okl[1] & okp & oks
    r1 = tang(u1, np.broadcast_to(np.array([0.0, 1.0, 0.3]), (N, 3))); r2 = tang(u2, np.broadcast_to(np.array([0.0, 1.0, 0.3]), (N, 3)))
    q = np.stack([sangle(u1, r1, e1), sangle(u2, r2, e2), sangle(e1, u1, W), sangle(e2, u2, W), sangle(W, e1, e2), sangle(W, e1, harm)], -1)
    return dict(u1=u1, u2=u2, e1=e1, e2=e2, W=W, harm=harm, ok=ok, q=q, okl=okl, okp=okp, oks=oks)


class Rig:
    """bench poses + the full 10 fps fit clips (for the follow check)"""
    def __init__(self, B):
        self.B = B; Z = CB._poses_all(); self.Z = Z
        self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.kind = np.array(B.kind); self.n = len(B.idx)
        names = list(Z["NAMES"]); fit = [names.index(n) for n in CB.FIT]
        self.zc = np.nonzero(np.isin(Z["CID"], fit))[0]                     # every fit-clip frame (10 fps)
        self.HGc = Z["HG"][self.zc].astype(float); pos = {z: k for k, z in enumerate(self.zc)}
        self.path = {}                                                        # bench j -> indices into zc from prev bench frame
        for c, js in B.clip_order().items():
            for a, b in zip([None] + js[:-1], js):
                zb = pos[int(B.idx[b])]
                za = pos[int(B.idx[a])] if a is not None else zb
                self.path[b] = np.arange(za, zb + 1)

    def taken_kin(self, p):
        """(kinematics on the bench poses, ok mask incl. the follow-path check for clip frames)"""
        K = kin(p, self.HG); ok = K["ok"].copy()
        Kc = kin(p, self.HGc); okc = Kc["ok"]; qc = Kc["q"]
        dq = np.abs((np.diff(qc, axis=0) + 180) % 360 - 180).max(1); jump = np.r_[False, dq > JUMP]
        for j, path in self.path.items():
            if not ok[j]: continue
            sub = path[1:] if len(path) > 1 else path
            if not okc[path].all() or jump[sub].any() and len(path) > 1: ok[j] = False
        return K, ok


def kin_cover(p, rig):
    K, ok = rig.taken_kin(p); cl = rig.kind == "clip"
    return dict(ws=float(ok[~cl].mean()), clip=float(ok[cl].mean()), kin_only=float(K["ok"].mean()))


# ------------------------------------------------------------------------------------------------ geometry
def disc_grid(r):
    g = np.arange(-r, r + 1e-6, SP); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= r * r + 1e-9
    return X[k], Y[k]


def disc_frame(k, ref):
    a = tang(k, ref); return a, np.cross(k, a)


def parts_dirs(p, K):
    """per part (scapula frame): dict name -> dict(kind, D (N, m, 3) sample rays, extra geometry)"""
    N = len(K["W"]); out = {}
    u1, u2, e1, e2, W, harm = (K[k] for k in ("u1", "u2", "e1", "e2", "W", "harm"))
    fixed_ref = np.broadcast_to(np.array([0.0, 1.0, 0.3]), (N, 3))
    hubs = [("BH1", u1, fixed_ref, "coax" if coax(p) else "base")]
    if not coax(p): hubs.append(("BH2", u2, fixed_ref, "base"))
    hubs += [("E1", e1, u1, "elbow"), ("E2", e2, u2, "elbow"), ("WH", W, harm, "w")]
    for nm, k, ref, typ in hubs:
        r, crown = HUB[typ]; gx, gy = disc_grid(r); a, b = disc_frame(k, ref)
        X = gx[None, :, None] * a[:, None] + gy[None, :, None] * b[:, None]
        out[nm] = dict(kind="disc", k=k, X=X, rx=np.hypot(gx, gy), r=r, crown=crown, D=unit(H0 * k[:, None] + X))
    ng = p["neck_deg"] * D2R; nk_v = unit(math.cos(ng) * W + math.sin(ng) * tang(W, harm))
    for nm, a0, a1, ang in (("K1", u1, e1, p["a1"] * D2R), ("K2", u2, e2, p["a2"] * D2R), ("C1", e1, W, p["c1"] * D2R),
                            ("C2", e2, W, p["c2"] * D2R), ("N", W, nk_v, ng)):
        D = BL.arc_dirs(a0, a1, ang, ds_mm=SP, width=WID, r_ref=R_REF)
        ns, nc = D.shape[1], D.shape[2]
        s = np.linspace(0, 1, ns) * ang                                      # arc angle from the start axis
        out[nm] = dict(kind="strap", D=D.reshape(N, -1, 3), ns=ns, nc=nc, s=np.repeat(s, nc), ang=ang)
    return out


def layers(p):
    """member -> list of (hub, layer offset over the hub's lower face); hub of the start, hub of the end"""
    L = {}
    if coax(p): L["K1"] = [("BH1", 0.0, "start"), ("E1", 0.0, "end")]; L["K2"] = [("BH1", UP, "start"), ("E2", 0.0, "end")]
    else: L["K1"] = [("BH1", 0.0, "start"), ("E1", 0.0, "end")]; L["K2"] = [("BH2", 0.0, "start"), ("E2", 0.0, "end")]
    if p["worder"] == "arm_low": lw = dict(N=0.0, C1=UP, C2=2 * UP)
    else: lw = dict(C2=0.0, C1=UP, N=2 * UP)
    L["C1"] = [("E1", UP_E, "start"), ("WH", lw["C1"], "end")]; L["C2"] = [("E2", UP_E, "start"), ("WH", lw["C2"], "end")]
    L["N"] = [("WH", lw["N"], "start")]
    return L


def skin_radius(B, i, D, r_max=250.0):
    """outermost skin radius along unit rays D (k, 3) from GH in pose i (the baseline's sphere tracing, r_max inside the grid box)"""
    r = np.full(len(D), r_max); act = np.ones(len(D), bool); hit = np.zeros(len(D), bool)
    for _ in range(60):
        if not act.any(): break
        a = np.nonzero(act)[0]; d = B.dist(i, D[a] * r[a, None])
        done = d < 0.3; hit[a[done]] = True; act[a[done]] = False
        r[a[~done]] -= np.maximum(d[~done], 0.5)
        act &= ~(r < 15)
    return np.where(hit, r, 0.0)


def fit_radii(B, rig, P, ok, log=None):
    """outermost skin radius under every sample of every part, every kinematically valid pose: name -> (N, m)"""
    names = list(P); R = {nm: np.zeros(P[nm]["D"].shape[:2]) for nm in names}
    for i in np.nonzero(ok)[0]:
        allD = np.concatenate([np.einsum("ij,mj->mi", rig.RS[i], P[nm]["D"][i]) for nm in names])
        rr = skin_radius(B, int(i), allD); o = 0
        for nm in names:
            m = P[nm]["D"].shape[1]; R[nm][i] = rr[o:o + m]; o += m
    return R


def shapes(p, P, R, okfit):
    """rigid shapes: disc levels H (lower face along the axis) and strap radii r (m,) per part"""
    pct, clr = p["pct"], p["clear"]; Sh = {}
    for nm, d in P.items():
        prof = np.percentile(R[nm][okfit], pct, axis=0) + clr
        if d["kind"] == "disc":                                               # flat disc: every sample clear
            Sh[nm] = dict(H=float(np.max(np.sqrt(np.maximum(prof ** 2 - d["rx"] ** 2, 0)))))
        else:
            Sh[nm] = dict(r=prof.copy())
    for nm, lst in layers(p).items():
        d = P[nm]; r = Sh[nm]["r"]; s = d["s"]
        for hub, off, end in lst:
            hr = P[hub]["r"]; L = Sh[hub]["H"] + off
            ang = s if end == "start" else d["ang"] - s                      # arc angle from that hub's axis
            # across offset of the sample (c index) adds to the lateral distance from the axis
            x = ang * L                                                       # mm along the arc from the axis
            on = x <= hr + LAND
            need = np.where(on, np.sqrt(L ** 2 + np.minimum(x, hr) ** 2), L - SLOPE * (x - hr - LAND))
            r[:] = np.maximum(r, need)
        Sh[nm]["r"] = r
    return Sh


ADJ_FULL = {("BH1", "BH2"), ("BH1", "K1"), ("BH2", "K2"), ("E1", "K1"), ("E1", "C1"), ("E2", "K2"), ("E2", "C2"),
            ("WH", "C1"), ("WH", "C2"), ("WH", "N")}
ADJ_NEAR = {("K1", "C1"): "E1", ("K2", "C2"): "E2", ("C1", "C2"): "WH", ("C1", "N"): "WH", ("C2", "N"): "WH"}


def metal(p, P, Sh, K, i, RS):
    """pose i: underside points (skin-facing, recorded), collision volumes, top points (thorax frame)"""
    under, owner_u, vol_d, vol_lo, vol_hi, vol_o, tops = [], [], [], [], [], [], []
    for nm, d in P.items():
        if d["kind"] == "disc":
            H = Sh[nm]["H"]; pts = H * d["k"][i] + d["X"][i]
            nrm = np.linalg.norm(pts, axis=1); dd = pts / nrm[:, None]
            under.append(pts); owner_u += [nm] * len(pts)
            vol_d.append(dd); vol_lo.append(nrm); vol_hi.append(nrm + d["crown"]); vol_o += [nm] * len(pts)
            tops.append(pts + d["crown"] * d["k"][i])
        else:
            r = Sh[nm]["r"]; pts = d["D"][i] * r[:, None]
            # skin-facing: outside the footprint of the hubs this strap sits on
            keep = np.ones(len(pts), bool)
            for hub, off, end in layers(p)[nm]:
                ax = P[hub]["k"][i]; lat = np.linalg.norm(np.cross(d["D"][i], ax), axis=1) * r
                keep &= ~((lat < P[hub]["r"]) & ((d["D"][i] @ ax) > 0))
            under.append(pts[keep]); owner_u += [nm] * int(keep.sum())
            vol_d.append(d["D"][i]); vol_lo.append(r); vol_hi.append(r + T); vol_o += [nm] * len(pts)
            tops.append(d["D"][i] * (r + T)[:, None])
    U = np.concatenate(under) @ RS.T; Tp = np.concatenate(tops) @ RS.T
    return U, np.array(owner_u), (np.concatenate(vol_d), np.concatenate(vol_lo), np.concatenate(vol_hi), np.array(vol_o)), Tp


def collide(V, hubs, ret_pairs=False):
    """True if two parts that do not share a joint (or share it but away from it) come closer than the clearance"""
    D, lo, hi, own = V
    tree = cKDTree(D); prs = tree.query_pairs(LAT / 40.0, output_type="ndarray")
    if not len(prs): return (False, []) if ret_pairs else False
    a, b = prs[:, 0], prs[:, 1]; oa, ob = own[a], own[b]
    m = oa != ob
    a, b, oa, ob = a[m], b[m], oa[m], ob[m]
    rm = 0.5 * (lo[a] + lo[b]); lat = np.linalg.norm(D[a] - D[b], axis=1) * rm
    rad = (lo[a] < hi[b] + RAD_CLR) & (lo[b] < hi[a] + RAD_CLR)
    hit = (lat < LAT) & rad
    if not hit.any(): return (False, []) if ret_pairs else False
    a, b, oa, ob = a[hit], b[hit], oa[hit], ob[hit]
    bad = np.ones(len(a), bool)
    for t, (x, y) in enumerate(zip(oa, ob)):
        key = (x, y) if (x, y) in ADJ_FULL or (x, y) in ADJ_NEAR else (y, x)
        if key in ADJ_FULL: bad[t] = False; continue
        if key in ADJ_NEAR:
            ax, hr = hubs[ADJ_NEAR[key]]; lim = hr + 2.0
            la = np.linalg.norm(np.cross(D[a[t]], ax)) * lo[a[t]]; lb = np.linalg.norm(np.cross(D[b[t]], ax)) * lo[b[t]]
            if la < lim and lb < lim: bad[t] = False
    if ret_pairs: return bool(bad.any()), sorted({(x, y) for x, y, z in zip(oa, ob, bad) if z})
    return bool(bad.any())


def evaluate(p, B, rig, log=None, detail=False):
    """one configuration on bench B: bench report + extras"""
    t0 = time.time()
    K, ok = rig.taken_kin(p); okfit = K["ok"].copy()
    if okfit.sum() < 5:
        B.reset(); r = B.report(); r.update(kin_ws=0.0, kin_clip=0.0, n_coll=0, secs=round(time.time() - t0, 1)); return r
    P = parts_dirs(p, K)
    R = fit_radii(B, rig, P, okfit)
    Sh = shapes(p, P, R, okfit)
    B.reset(); n_coll = 0; per = {}; coll_pairs = {}
    for i in range(rig.n):
        if not ok[i]: B.record(i, None); continue
        U, own, V, Tp = metal(p, P, Sh, K, i, rig.RS[i])
        c = collide((V[0] @ rig.RS[i].T, V[1], V[2], V[3]), _rot_hubs(P, rig.RS[i], i), ret_pairs=detail)
        if detail:
            c, pr = c
            for x in pr: coll_pairs[x] = coll_pairs.get(x, 0) + 1
        if c: n_coll += 1; B.record(i, None); continue
        dt = B.dist(i, Tp); extra = Tp[dt < 0]
        d = B.record(i, np.concatenate([U, extra[np.argsort(B.dist(i, extra))[:1]]]) if len(extra) else U)
        if detail and rig.kind[i] == "clip" and d is not None and d.min() >= 0:
            for nm in np.unique(own):
                dd = d[:len(own)][own == nm]; per.setdefault(nm, []).append(dd)
    r = B.report()
    r.update(kin_ws=round(float(ok[rig.kind == "ws"].mean()), 4), kin_clip=round(float(ok[rig.kind == "clip"].mean()), 4),
             n_coll=n_coll, secs=round(time.time() - t0, 1))
    if detail:
        cat = {nm: np.concatenate(v) for nm, v in per.items()}
        r["per_part"] = {nm: dict(n=len(v), inband14=round(float(np.mean((v >= 2) & (v <= 14))), 3), median=round(float(np.median(v)), 1))
                         for nm, v in cat.items()}
        r["levels"] = {nm: round(Sh[nm]["H"], 1) for nm in Sh if "H" in Sh[nm]}
        r["coll_pairs"] = {f"{a}-{b}": n for (a, b), n in coll_pairs.items()}
        r["mass_g"] = mass(p, P, Sh)
    return r


def _rot_hubs(P, RS, i):
    """hub axis (thorax frame) and radius of pose i, for the collision exemptions"""
    return {k: (RS @ v["k"][i], v["r"]) for k, v in P.items() if v["kind"] == "disc"}


def mass(p, P, Sh, rho=4.43e-3):
    """Ti mass (g) of straps (8 x 3 at their mean radius) - hubs excluded (bearing hardware)"""
    m = 0.0
    for nm, d in P.items():
        if d["kind"] == "strap": m += d["ang"] * float(np.mean(Sh[nm]["r"])) * WID * T * rho
    return round(m, 1)

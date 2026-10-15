"""Concept model: ANNULAR-RING 3R (id annular-ring-3r) - the champion's spherical 3R (every joint axis through the GH
centre, tools/concept_baseline.py kinematics) with each revolute realised as an OPEN-BORE thin-section ring bearing
coaxial with its joint axis, so the skin dome under the axis pierce point rises into the bore instead of lifting a
solid hub. The links leave from the ring rims.

Chain (scapula handler -> user's upper-arm cuff):
    base --J1 ring about b (lower race = base, upper race = link 1)--> link 1 (strap on the great circle P1 -> P2)
    --J2 ring about p2 (lower race = link 1, upper race = link 2)--> link 2 (strap P2 -> P3)
    --J3 ring about W (upper race = link 2, lower race = the arm side)--> arm stub (strap fixed to the humerus, toward
    the elbow) -> user's cuff.
DOF: 3 ACTIVE (the three ring angles = the three joint angles of the spherical 3R; the arm sets them uniquely through
the two-circle closure on the design's branch), 0 PASSIVE. Nothing is spare, nothing can sag on its own.

Parts at real size (mm):
  * ring k: a solid annulus about its axis: bore radius rho_k (open, no metal inside), radial width w and axial height
    h of the HOUSED ring (Kaydon Reali-Slim KAA, 4.76 section: w 9, h 8, lower race housing 0..4, upper 4..8; KA, 6.35
    section: w 10.6, h 9.6, split 4.8). rho_k = 0 is the A/B TWIN: the O20 v5 hub (docs/HARDWARE.md: disc r 10,
    12.25 stack, upper member from 3.15). The ring is FLAT (a plane normal to its axis) at axial height z_k from GH.
  * links: straps of width `width`, 3 mm thick, on the great circle between the two axes, starting at the outer rim
    of each ring (the strap end is cut on the ring's outer cylinder); underside r(s, c) fixed in the link.
  * arm stub: the same strap from the J3 ring rim toward the elbow, to max(neck_deg from P3, rim + 10 mm), humerus-fixed
    (the baseline's "neck"; the spec's BOTTOM stub).
Fitting (the baseline's percentile rule, made true-distance): per pose, every part is traced in from outside along its
own placement direction until its samples sit CLEAR (2.2) mm off the skin - a ring as one flat body along its axis
(the first crossing of the union of its circles = the max over the circles, so needs are precomputed per 1 mm circle),
a strap sample along its ray from GH. The part's fixed shape = the p-th percentile over the kinematically valid bench
poses (p swept, as in tools/concept_baseline.py). Link ends: the underside meets the ring at its attachment level
(J1 upper race z1 + split, J2 lower race z2 / upper race z2 + split, J3 upper race z3 + split, stub on the J3 lower
race z3) and ramps toward the envelope at <= 35 deg (max(envelope, rim level - tan35 * s)).
Metal sampled (~1 point / 4 mm2, 2 mm grid): SCORED (skin-facing, as the baseline): ring / hub undersides, strap
undersides. CONTACT-ONLY (every other surface): ring inner (bore) walls, outer walls, tops / hub crowns - a contact-only
sample inside the body is appended to the record so the bench counts the pose as contact.
Taken iff: closure on the branch with the evaluator's 10 deg fold / stretch margin; along each fit clip at its full
10 fps no joint steps > 25 deg between consecutive frames (a flip = that frame not followed); no two non-adjacent
parts within 1 mm (rings as exact solids of revolution, straps as 3 mm mid-surfaces; the two straps meeting at a joint
- adjacent members - at least the joint's 0.15 mm running gap apart outside the ring); then the bench's contact rule (any metal < 0 mm = contact = not taken).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/annular-ring-3r.py [check|sweep|best|sketch]
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_baseline as BL                                # noqa: E402

ID = "annular-ring-3r"; NAME = "Annular-ring 3R: open-bore thin-section rings at every joint axis"
D2R = math.pi / 180
SP, R_REF = 2.0, 75.0                     # sample grid (1 point / 4 mm2); nominal radius of the strap direction grid
CLEAR, PART_CLEAR, T_LINK = 2.2, 1.0, 3.0  # fit target off the skin (2 + 0.2 sampling margin), part-part, strap
RUN_GAP = 0.15                             # adjacent members outside their shared joint (the v5 joint's running gap)
RAMP, SING, JUMP = 35.0, 10.0, 25.0        # strap ramp off a ring (deg), fold margin (deg), largest joint step / frame
Z0_RING, R0_LINK = (115.0, 95.0, 80.0), (150.0, 120.0, 100.0)   # tracing starts (mm from GH along the axis / ray)
RHO_MAX = 46                               # ring circles precomputed for rho = 0..RHO_MAX mm
OFFS = np.arange(-6, 7)                    # strap across offsets precomputed (mm at R_REF)
STUB_MAX = 55.0                            # deg of stub arc precomputed
RING_SEC = {4.76: (9.0, 8.0, 4.0), 6.35: (10.6, 9.6, 4.8)}   # section -> housed radial width, axial height, race split
HUB = (0.0, 10.0, 12.25, 3.15)             # twin: O20 v5 hub (ri, ro, stack, upper member level)
KAA = [12.7, 19.05, 25.4, 31.75]           # Reali-Slim KAA10 / 15 / 20 / 25 bore radii (4.76 section)
KA = [25.4, 31.75]                         # Reali-Slim KA020 / 025 bore radii (6.35 section)

PARAMS = dict(rho1=19.05, rho2=19.05, rho3=19.05, sec=4.76, width=8.0, pct=100.0, neck_deg=25.0,
              daz=0.0, delv=0.0, dA1=0.0, dA2=0.0, dwd=0.0, dwa=0.0)
SWEEP = dict(rho1=[0] + KAA, rho2=[0] + KAA, rho3=[0] + KAA, sec=[4.76, 6.35], width=[8, 10, 12, 14], pct=[85, 90, 95, 98, 100],
             daz=[-10, 0, 10], delv=[-10, 0, 10], dA1=[-10, 0, 10], dA2=[-10, 0, 10], dwd=[-10, 0, 10], dwa=[-10, 0, 10])
AXES = ("daz", "delv", "dA1", "dA2", "dwd", "dwa")


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def axes_of(p):
    C = BL.CHAMP
    return dict(az=C["az"] + p["daz"], el=C["el"] + p["delv"], a=[C["a"][0] + p["dA1"], C["a"][1] + p["dA2"]],
                w=[C["w"][0] + p["dwd"], C["w"][1] + p["dwa"]], branch=C["branch"], sing_deg=SING)


def ring_geo(rho, sec):
    """(ri, ro, h, split) of the housed ring / the O20 hub (rho 0)"""
    if rho <= 0: return HUB
    w, h, lo = RING_SEC[float(sec)]; return (float(rho), float(rho) + w, h, lo)


def perp_basis(P):
    """two unit vectors normal to each row of P (n, 3)"""
    a = np.where(np.abs(P[:, 2:3]) < 0.9, np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]))
    q1 = unit(np.cross(P, a)); return q1, np.cross(P, q1)


# ---- kinematics (= tools/concept_baseline.py pins(), in the scapula frame, + joint angles for continuity) ------------
def kin_S(d, HG):
    A = [x * D2R for x in d["a"]]; b = BL.bvec(d["az"], d["el"]); W0 = BL.w_dir(*d["w"]); n = len(HG)
    p1 = np.ascontiguousarray(np.broadcast_to(b, (n, 3))); p3 = HG @ W0
    p2, ok = BL.circ_int(p1, A[0], p3, A[1], float(d["branch"]))
    ok = ok & BL.tri_ok(p1, p3, A[0], A[1], d["sing_deg"] * D2R)

    def ang(ax, a, c):
        a_ = a - (a * ax).sum(-1, keepdims=True) * ax; c_ = c - (c * ax).sum(-1, keepdims=True) * ax
        return np.arctan2((np.cross(a_, c_) * ax).sum(-1), (a_ * c_).sum(-1))
    r1 = np.broadcast_to(unit(np.cross(b, [1.0, 0.0, 0.0])), (n, 3)); hv = HG @ unit(np.cross(W0, [0.0, 1.0, 0.0]))
    q = np.stack([ang(p1, r1, p2), ang(p2, p1, p3), ang(p3, p2, hv)], 1)
    return np.stack([p1, p2, p3], 1), ok, q


def continuity(d, Z, idx):
    """every fit clip at its full 10 fps: a frame is not followed if its joint step from the previous frame (taken
    kinematically) exceeds JUMP. Returns per bench index (True for workspace poses) and the number of flips."""
    names = list(Z["NAMES"]); cid = Z["CID"]; good = {}; flips = 0
    for nm in CB.FIT:
        ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        _, ok, q = kin_S(d, Z["HG"][ii].astype(float)); prev = None
        for j, gi in enumerate(ii):
            g = bool(ok[j])
            if g and prev is not None:
                dq = np.degrees(np.abs((q[j] - q[prev] + np.pi) % (2 * np.pi) - np.pi))
                if dq.max() > JUMP: g = False; flips += 1
            good[int(gi)] = g; prev = j if ok[j] else None
    return np.array([good.get(int(g), True) for g in idx]), flips


# ---- tracing: place a rigid sample group as far in as CLEAR allows (sphere tracing from outside) -----------------------
def trace(B, i, base, dirs, starts, t0, target=CLEAR, iters=60, tol=0.03):
    """points X = base + t_g dirs, groups = contiguous runs starting at `starts`; per group the first t (from t0 inward)
    where the group's min signed distance = target. nan if the group starts inside (distance < target at t0)."""
    ng = len(starts); t = np.full(ng, float(t0)); act = np.ones(ng, bool); gid = np.repeat(np.arange(ng), np.diff(np.r_[starts, len(base)]))
    bad = np.zeros(ng, bool)
    for it in range(iters):
        sel = act[gid]; X = base[sel] + t[gid[sel], None] * dirs[sel]
        d = B.dist(i, X); g = gid[sel]
        st = np.r_[0, np.nonzero(np.diff(g))[0] + 1]; m = np.minimum.reduceat(d, st); ga = g[st]
        step = m - target
        if it == 0: bad[ga[step < 0]] = True; act[ga[step < 0]] = False; step = np.where(step < 0, 0, step)
        t[ga] -= step; done = step < tol; act[ga[done]] = False
        if not act.any(): break
    t[bad] = np.nan; return t


def trace_multi(B, i, base, dirs, starts, t0s, **kw):
    """trace from the first start; groups that start inside another body part (head, neck, the other side of the
    trunk) are retried from the lower starts (nan if they start inside at every start)"""
    t = trace(B, i, base, dirs, starts, t0s[0], **kw)
    for t0 in t0s[1:]:
        bad = np.nonzero(np.isnan(t))[0]
        if not len(bad): break
        ends = np.r_[starts[1:], len(base)]; idx = np.concatenate([np.arange(starts[g], ends[g]) for g in bad])
        sub_st = np.r_[0, np.cumsum(ends[bad] - starts[bad])[:-1]]
        t[bad] = trace(B, i, base[idx], dirs[idx], sub_st, t0, **kw)
    return t


def circle_set():
    """local (rho, psi) of the 1 mm circles 0..RHO_MAX, 2 mm apart along each circle; group starts"""
    rr, pp, st = [], [], []
    for r in range(RHO_MAX + 1):
        n = 1 if r == 0 else max(6, int(math.ceil(2 * math.pi * r / SP)))
        st.append(len(rr)); ps = 2 * math.pi * (np.arange(n) + 0.5) / n
        rr += [float(r)] * n; pp += list(ps)
    return np.array(rr), np.array(pp), np.array(st)


def strap_dirs(u, v, ang_max):
    """direction grid of a strap on the great circle u -> v (P, 3): (P, len(OFFS), nth, 3) and the centre-line angles"""
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u)); dth = SP / R_REF
    th = (np.arange(int(ang_max / dth)) + 0.5) * dth
    D = np.cos(th)[None, :, None] * u[:, None] + np.sin(th)[None, :, None] * e2[:, None]          # (P, nth, 3)
    cs = OFFS / R_REF
    return unit(D[:, None] * np.cos(cs)[None, :, None, None] + nrm[:, None, None, :] * np.sin(cs)[None, :, None, None]), th


class Pre:
    """per axes setting: thorax axes per bench pose, kinematic validity, ring circle needs, strap sample needs"""
    def __init__(self, B, d, log=print, limit=None):
        t0 = time.time(); Z = CB._poses_all(); self.B = B; self.d = d
        HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float); n = len(B.idx)
        PS, ok, q = kin_S(d, HG); cont, flips = continuity(d, Z, B.idx)
        self.ok_kin, self.cont, self.flips = ok, cont, flips; self.ok = ok & cont
        if limit is not None: self.ok[limit:] = False                         # dev only (partial cache)
        self.P = np.einsum("pij,pkj->pki", RS, PS); self.harm = np.einsum("pij,j->pi", RS @ HG, np.array([0.0, -1.0, 0.0]))
        self.A = [x * D2R for x in d["a"]]; self.q = q
        rr, pp, st = circle_set(); self.crho = np.arange(RHO_MAX + 1)
        self.cneed = np.full((n, 3, RHO_MAX + 1), np.nan)
        self.S = {}
        for nm, (a, b, amax) in dict(L1=(0, 1, self.A[0]), L2=(1, 2, self.A[1]), stub=(2, None, STUB_MAX * D2R)).items():
            v = self.P[:, b] if b is not None else self.harm
            D, th = strap_dirs(self.P[:, a], v, amax)
            ang_a = np.degrees(np.arccos(np.clip((D * self.P[:, a][:, None, None]).sum(-1), -1, 1)))
            ang_b = np.degrees(np.arccos(np.clip((D * self.P[:, b][:, None, None]).sum(-1), -1, 1))) if b is not None else None
            self.S[nm] = dict(D=D, th=th, a=a, b=b, ang_a=ang_a[np.argmax(self.ok)] if self.ok.any() else ang_a[0],
                              ang_b=(ang_b[np.argmax(self.ok)] if self.ok.any() else ang_b[0]) if b is not None else None,
                              need=np.full(D.shape[:3], np.nan))
        for i in np.nonzero(self.ok)[0]:
            for k in range(3):
                P = self.P[i, k][None]; q1, q2 = perp_basis(P)
                base = rr[:, None] * (np.cos(pp)[:, None] * q1 + np.sin(pp)[:, None] * q2)
                self.cneed[i, k] = trace_multi(B, int(i), base, np.broadcast_to(P, base.shape), st, Z0_RING)
            for nm, s in self.S.items():
                D = s["D"][i].reshape(-1, 3)
                s["need"][i] = trace_multi(B, int(i), np.zeros_like(D), D, np.arange(len(D)), R0_LINK).reshape(s["D"].shape[1:3])
        nanr = np.isnan(self.cneed[self.ok]).any(-1).mean(0) if self.ok.any() else 0
        log(f"  pre: {int(self.ok.sum())}/{n} poses kinematically valid (fold {int((~ok).sum())}, flips {int((ok & ~cont).sum())} "
            f"bench frames / {flips} full-rate), ring-trace start-inside share {np.round(nanr, 3)}, {time.time() - t0:.0f} s ({B.mode})")


# ---- a configuration ---------------------------------------------------------------------------------------------------
def ring_points(P, z, ri, ro, h):
    """surface samples of a ring at axis P (3,) (thorax), bottom at z: (bottom face (scored), other faces)"""
    q1, q2 = perp_basis(P[None]); q1, q2 = q1[0], q2[0]

    def circ(r, zo):
        n = max(3, int(math.ceil(2 * math.pi * r / SP))) if r > 0 else 1; ps = 2 * math.pi * (np.arange(n) + 0.5) / n
        return (z + zo) * P + r * (np.cos(ps)[:, None] * q1 + np.sin(ps)[:, None] * q2)
    rad = np.arange(ri + 1.0, ro, SP)
    bot = np.concatenate([circ(r, 0.0) for r in rad]); top = np.concatenate([circ(r, h) for r in rad])
    zs = np.linspace(0, h, int(math.ceil(h / SP)) + 1)
    walls = [circ(ro, zo) for zo in zs] + ([circ(ri, zo) for zo in zs] if ri > 0 else [])
    return bot, np.concatenate([top] + walls)


def ring_sdf(X, P, z, ri, ro, h):
    """exact signed distance to the solid annulus (solid of revolution about the axis P through GH)"""
    a = X @ P; rho = np.linalg.norm(X - a[:, None] * P, axis=1)
    qx = np.abs(rho - (ri + ro) / 2) - (ro - ri) / 2; qy = np.abs(a - z - h / 2) - h / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)


class Config:
    def __init__(self, pre, prm):
        self.pre = pre; self.p = prm; P = pre
        self.rings = [ring_geo(prm[f"rho{k + 1}"], prm["sec"]) for k in range(3)]
        fit = np.nonzero(P.ok)[0]; pct = prm["pct"]; self.fit = fit
        self.z = []
        for k, (ri, ro, h, lo) in enumerate(self.rings):
            sel = (P.crho >= math.floor(ri)) & (P.crho <= math.ceil(ro))
            need = P.cneed[fit][:, k][:, sel].max(1); need = need[np.isfinite(need)]
            self.z.append(float(np.percentile(need, pct)) if len(need) else np.nan)
        w = prm["width"]; hw = w / 2 - 1; rows = np.nonzero((np.abs(OFFS) <= hw + 1e-9) & (np.abs((OFFS - hw) % 2) < 1e-9))[0]
        lvl = dict(L1=((0, self.rings[0][3]), (1, 0.0)), L2=((1, self.rings[1][3]), (2, self.rings[2][3])), stub=((2, 0.0), None))
        kr = math.tan(RAMP * D2R); self.strap = {}; self.riser = 0.0
        for nm, s in P.S.items():
            need = s["need"][fit][:, rows]; ok = np.isfinite(need)
            with np.errstate(all="ignore"), __import__("warnings").catch_warnings():
                __import__("warnings").simplefilter("ignore"); env = np.nanpercentile(np.where(ok, need, np.nan), pct, axis=0)
            (ka, la), eb = lvl[nm]
            za, roa = self.z[ka], self.rings[ka][1]; ra = math.hypot(za + la, roa); al = math.degrees(math.atan2(roa, za + la))
            angA = s["ang_a"][rows]; keep = angA > al; h = np.maximum(env, ra - kr * np.radians(angA - al) * ra)
            if eb is not None:
                kb, lb = eb; zb, rob = self.z[kb], self.rings[kb][1]; rb = math.hypot(zb + lb, rob); bl = math.degrees(math.atan2(rob, zb + lb))
                angB = s["ang_b"][rows]; keep &= angB > bl; h = np.maximum(h, rb - kr * np.radians(angB - bl) * rb)
            else:
                ext = max(prm["neck_deg"] * D2R, math.radians(al) + 10.0 / ra)
                keep &= (s["th"][None, :] <= ext)
            keep &= np.isfinite(h)
            self.strap[nm] = dict(rows=rows, keep=keep, h=h)
        # rings: local sample templates are built per pose (axis-dependent); strap samples per pose from P.S[...]["D"]

    def metal(self, i):
        """(scored points, contact-only points, parts dict for self-collision) of bench pose i in the thorax frame"""
        P = self.pre; parts = {}
        sc, co = [], []
        for k, (ri, ro, h, lo) in enumerate(self.rings):
            bot, oth = ring_points(P.P[i, k], self.z[k], ri, ro, h); sc.append(bot); co.append(oth)
            parts[f"R{k + 1}"] = (bot, oth)
        for nm, s in self.strap.items():
            D = P.S[nm]["D"][i][s["rows"]]; X = (s["h"][..., None] * D)[s["keep"]]; sc.append(X)
            parts[nm] = X + T_LINK / 2 * unit(X)
        return np.concatenate(sc), np.concatenate(co), parts

    def collide(self, i, parts):
        """first non-adjacent pair closer than PART_CLEAR, or None"""
        P = self.pre
        R = {f"R{k + 1}": (P.P[i, k], self.z[k], *self.rings[k][:3]) for k in range(3)}
        for a, b in (("R1", "R2"), ("R1", "R3"), ("R2", "R3")):
            pts = np.concatenate(parts[b])
            if ring_sdf(pts, *R[a]).min() < PART_CLEAR: return a + "-" + b
        for r, s in (("R1", "L2"), ("R1", "stub"), ("R3", "L1"), ("R2", "stub")):
            if len(parts[s]) and ring_sdf(parts[s], *R[r]).min() < T_LINK / 2 + PART_CLEAR: return r + "-" + s
        for a, b, gap in (("L1", "L2", RUN_GAP), ("L2", "stub", RUN_GAP), ("L1", "stub", PART_CLEAR)):   # adjacent: running gap
            if len(parts[a]) and len(parts[b]):
                dmin = cKDTree(parts[a]).query(parts[b], k=1)[0].min()
                if dmin < T_LINK + gap - 0.1: return a + "-" + b
        return None


def evaluate(B, pre, prm, details=False):
    """score one configuration on the bench; returns the report (+ reasons)"""
    C = Config(pre, prm); B.reset(); why = {}
    if not all(np.isfinite(C.z)):
        r = B.report(); r["why"] = {"ring not placeable": len(B.idx)}; return r, C
    for i in range(len(B.idx)):
        if not pre.ok[i]: why["fold" if not pre.ok_kin[i] else "flip"] = why.get("fold" if not pre.ok_kin[i] else "flip", 0) + 1; continue
        sc, co, parts = C.metal(i)
        c = C.collide(i, parts)
        if c: why["self:" + c] = why.get("self:" + c, 0) + 1; continue
        d = B.dist(i, np.concatenate([sc, co])); ds, dc = d[:len(sc)], d[len(sc):]
        B.res[i] = np.concatenate([ds, dc[dc < 0]])
        if float(d.min()) < 0: why["contact"] = why.get("contact", 0) + 1
    r = B.report(); r["why"] = why; r["z"] = [round(x, 2) for x in C.z]
    r["n_pts"] = int(np.mean([len(x) for x in B.res if x is not None])) if any(x is not None for x in B.res) else 0
    if details:
        cl = [j for j, k in enumerate(B.kind) if k == "clip" and B.res[j] is not None and float(np.min(B.res[j])) >= 0]
        per = {}
        for j in cl:
            sc, co, parts = C.metal(j); d = B.dist(j, sc); o = 0
            for nm, X in [(f"R{k + 1}", parts[f"R{k + 1}"][0]) for k in range(3)] + [(nm, None) for nm in C.strap]:
                m = len(X) if X is not None else int(C.strap[nm]["keep"].sum())
                per.setdefault(nm, []).append(d[o:o + m]); o += m
        r["parts"] = {nm: dict(n=int(np.mean([len(x) for x in v])), inband14=round(float(np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 14))), 3),
                               med=round(float(np.median(np.concatenate(v))), 1)) for nm, v in per.items()}
    return r, C


# ---- sweep -------------------------------------------------------------------------------------------------------------
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")


def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class Runner:
    def __init__(self, B, log=print, fresh=True):
        self.B = B; self.log = log; self.pres = {}
        self.entries = [] if fresh or not os.path.exists(SWEEP_JSON) else json.load(open(SWEEP_JSON))

    def pre(self, prm):
        key = tuple(prm[k] for k in AXES)
        if key not in self.pres:
            if len(self.pres) > 3: self.pres.pop(next(iter(self.pres)))
            self.pres[key] = Pre(self.B, axes_of(prm), log=self.log)
        return self.pres[key]

    def run(self, over, tag=""):
        prm = dict(PARAMS); prm.update(over)
        for e in self.entries:
            if e["params"] == prm: return e
        t = time.time(); r, C = evaluate(self.B, self.pre(prm), prm)
        e = dict(k=len(self.entries), t=now(), params=prm, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                 follow=r["follow"], contact=r["contact"], gap=r["gap"], z=r.get("z"), why=r.get("why"), tag=tag)
        self.entries.append(e)
        os.makedirs(os.path.dirname(SWEEP_JSON), exist_ok=True)
        json.dump(self.entries, open(SWEEP_JSON + ".tmp", "w"), indent=0); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
        short = {k: v for k, v in prm.items() if v != PARAMS[k]}
        self.log(f"[{e['k']:3d}] gap {e['gap']:6.2f}  ib14 {e['inband14']:.3f} ib10 {e['inband10']:.3f} reach {e['reach']:.3f} "
                 f"follow {e['follow']:.3f} contact {e['contact']:.3f}  z {e['z']}  {short}  {tag}  ({time.time() - t:.1f} s) {e['why']}")
        return e

    def best(self, filt=lambda e: True):
        c = [e for e in self.entries if filt(e)]; return min(c, key=lambda e: e["gap"]) if c else None


def plog(*a): print(*a, flush=True)


def has_ring(e): return any(e["params"][f"rho{k}"] > 0 for k in (1, 2, 3))


def twin_of(prm): return dict(prm, rho1=0, rho2=0, rho3=0)


def sweep(B):
    """coarse -> refine inside the morphology (at least one ring); every ring configuration's O20-hub twin (same axes,
    width, percentile) is run next to it, so the ring's own effect is measured, not the axes'"""
    R = Runner(B, plog)
    bestR = lambda: R.best(has_ring)
    # stage A: which joints get rings (KAA15, bore 19.05) vs the twin, percentile scan (the champion's axes)
    layouts = [("twin", dict(rho1=0, rho2=0, rho3=0)), ("all KAA15", dict(rho1=19.05, rho2=19.05, rho3=19.05)),
               ("J2 only", dict(rho1=0, rho2=19.05, rho3=0)), ("J2+J3", dict(rho1=0, rho2=19.05, rho3=19.05)),
               ("J1 only", dict(rho1=19.05, rho2=0, rho3=0)), ("J3 only", dict(rho1=0, rho2=0, rho3=19.05))]
    for nm, lay in layouts:
        for pct in (90, 95, 98, 100): R.run(dict(lay, pct=pct), "A " + nm)
    # stage B: bore radius per joint (coordinate descent from the best ring layout; 0 = O20 hub)
    cur = dict(bestR()["params"])
    for rnd in range(2):
        improved = False
        for k in ("rho2", "rho3", "rho1"):
            for v in [0] + KAA:
                if v == cur[k]: continue
                e = R.run(dict(cur, **{k: v}), f"B{rnd} {k}")
                if has_ring(e) and e["gap"] < R.run(cur, "B cur")["gap"] - 1e-9: cur = dict(e["params"]); improved = True
        if not improved: break
    for pct in (85, 90, 95, 98, 100): R.run(dict(cur, pct=pct), "B pct")
    cur = dict(bestR()["params"])
    if any(cur[f"rho{k}"] >= 25.4 for k in (1, 2, 3)): R.run(dict(cur, sec=6.35), "B sec")
    # stage C: strap width (ring and twin)
    for w in (10, 12, 14):
        R.run(dict(cur, width=w), "C width"); R.run(twin_of(dict(cur, width=w)), "C width twin")
    cur = dict(bestR()["params"])
    # stage D: the champion axes +-10 deg, one at a time, ring and twin
    for k in AXES:
        for v in (-10, 10):
            for pct in sorted({95.0, float(cur["pct"])}):
                R.run(dict(cur, **{k: v}, pct=pct), "D axes"); R.run(twin_of(dict(cur, **{k: v}, pct=pct)), "D axes twin")
    rng = np.random.default_rng(7)
    for _ in range(int(os.environ.get("AR_RANDOM", "6"))):
        cand = dict(bestR()["params"])
        for k in AXES: cand[k] = float(rng.choice([-10, -5, 0, 5, 10]))
        R.run(cand, "D random"); R.run(twin_of(cand), "D random twin")
    # stage E: the bores again at the best axes
    cur = dict(bestR()["params"])
    for k in ("rho1", "rho2", "rho3"):
        for v in [0] + KAA:
            if v != cur[k]: R.run(dict(cur, **{k: v}), "E bores")
    best = bestR(); plog("BEST RING", json.dumps(best))
    tw = R.run(twin_of(best["params"]), "twin of best"); plog("ITS TWIN", json.dumps(tw))
    plog("BEST OVERALL", json.dumps(R.best()))
    return R


def check(B, prm=None, limit=None):
    prm = dict(PARAMS, **(prm or {})); pre = Pre(B, axes_of(prm), log=plog, limit=limit)
    for over in (dict(), dict(rho1=0, rho2=0, rho3=0)):
        p2 = dict(prm, **over); r, C = evaluate(B, pre, p2, details=True)
        plog(json.dumps({k: v for k, v in p2.items() if v != PARAMS.get(k)}), json.dumps(r, default=str))
        # named poses
        taken = [i for i in range(len(B.idx)) if pre.ok[i]]
        if not taken: continue
        el = np.array([B.poses[i]["elev"] for i in taken]); pl = np.array([B.poses[i]["plane"] for i in taken])
        named = dict(rest=taken[int(np.argmin(el))], overhead=taken[int(np.argmax(el))], across=taken[int(np.argmax(pl))])
        bb = [i for i in taken if B.clip[i] == "Reach back pocket"]
        if bb: named["behind back"] = bb[len(bb) // 2]
        for nm, i in named.items():
            sc, co, parts = C.metal(i); d = B.dist(i, sc); dc = B.dist(i, co)
            plog(f"   {nm:12s} pose {B.poses[i]} -> scored {len(sc)} pts, in band 14 {np.mean((d >= 2) & (d <= 14)):.2f}, "
                 f"min {d.min():.1f} / walls+tops min {dc.min():.1f}, median {np.median(d):.1f}, self {C.collide(i, parts)}")
    return pre


def profile(B, prm=None):
    """the spec's premise, measured: a flat ring normal to its axis must sit at the max over its circles of the height
    each circle needs; if the skin were a dome about the pierce point that height would FALL with rho"""
    prm = dict(PARAMS, **(prm or {})); pre = Pre(B, axes_of(prm), log=plog); ok = np.nonzero(pre.ok)[0]; out = {}
    for k in range(3):
        C = pre.cneed[ok, k]; rows = {}
        for r in (0, 5, 10, 15, 19, 22, 25, 28, 32, 36, 41):
            c = C[:, r]; rows[r] = [round(float(np.nanmedian(c)), 1), round(float(np.nanpercentile(c, 95)), 1), round(float(np.nanmax(c)), 1)]
        hub = C[:, 0:11].max(1); ring = C[:, 19:29].max(1); dlt = ring - hub
        lowest = np.nanargmin(C[:, :29], axis=1)
        out[f"J{k + 1}"] = dict(need_by_rho_median_p95_max=rows, ring_minus_hub_median=round(float(np.nanmedian(dlt)), 1),
                                ring_minus_hub_p10_p90=[round(float(np.nanpercentile(dlt, 10)), 1), round(float(np.nanpercentile(dlt, 90)), 1)],
                                share_poses_ring_lower_than_hub=round(float(np.nanmean(dlt < 0)), 3),
                                share_poses_lowest_circle_is_centre=round(float(np.mean(lowest <= 2)), 3))
        plog(f"J{k + 1}", json.dumps(out[f"J{k + 1}"]))
    return out


def sketch(B, prm, path):
    """matplotlib sketch of the configuration at rest and at the highest pose taken, with the skin"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    pre = Pre(B, axes_of(prm), log=plog); r, C = evaluate(B, pre, prm)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    rest = min(taken, key=lambda i: B.poses[i]["elev"]); top = max(taken, key=lambda i: B.poses[i]["elev"])
    cols = dict(R1="#d1495b", R2="#edae49", R3="#00798c", L1="#66a182", L2="#8d6a9f", stub="#30638e")
    fig = plt.figure(figsize=(12, 5.6))
    for k, i in enumerate((rest, top)):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d"); V, F = B.skin(i); V = np.asarray(V)
        near = V[np.linalg.norm(V, axis=1) < 150][::7]; ax.scatter(near[:, 2], near[:, 0], near[:, 1], s=0.3, c="#bbbbbb", alpha=0.3)
        sc, co, parts = C.metal(i)
        for nm, X in parts.items():
            X = np.concatenate(X) if isinstance(X, tuple) else X
            if len(X): ax.scatter(X[:, 2], X[:, 0], X[:, 1], s=1.0, c=cols[nm], label=nm)
        p = B.poses[i]; ax.set_title(f"{'rest' if k == 0 else 'highest pose taken'}: plane {p['plane']:.0f}, elev {p['elev']:.0f}, axial {p['axial']:.0f}", fontsize=9)
        ax.view_init(elev=22, azim=-50 if k == 0 else -30); ax.set_xlabel("z lateral"); ax.set_ylabel("x anterior"); ax.set_zlabel("y up")
        ax.set_box_aspect((1, 1, 1)); ax.set_xlim(-80, 120); ax.set_ylim(-110, 90); ax.set_zlim(-90, 110)
        if k == 0: ax.legend(fontsize=7, markerscale=5, loc="upper left")
    fig.suptitle(f"{ID}: bores {prm['rho1']}/{prm['rho2']}/{prm['rho3']} mm (0 = O20 hub), width {prm['width']}, p{prm['pct']:.0f}; "
                 f"gap {r['gap']}, in band 14 {r['inband14']}, reach {r['reach']}, follow {r['follow']}", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig); return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "dev":                     # debug on the partial cache (first n poses whose grid is written)
        B = CB.Bench(n_clip=60, n_ws=160)
        if B.grid is None:
            g = np.load(os.path.join(CB.CACHE, B.key, "grid.tmp.npy"), mmap_mode="r"); B.grid = g; B.mode = "fast-partial"
        lim = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        check(B, limit=lim)
    elif mode == "check":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode, len(B.idx)); check(B)
    elif mode == "profile":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode, len(B.idx)); profile(B)
    elif mode == "sweep":
        B = CB.Bench(n_clip=60, n_ws=160); plog("bench", B.mode, len(B.idx)); sweep(B)
    elif mode == "sketch":
        B = CB.Bench(n_clip=60, n_ws=160); prm = dict(PARAMS, **json.loads(sys.argv[2])) if len(sys.argv) > 2 else dict(PARAMS)
        plog(sketch(B, prm, os.path.join(REPO, "docs", "concepts", "img", f"{ID}.png")))

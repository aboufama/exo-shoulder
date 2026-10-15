"""Concept model: CAM-UNFOLDING LINK (id cam-unfold-4th) - the champion's spherical 3R with a slaved knee in link 2.

Chain (scapula handler -> user's upper-arm cuff), every joint axis through the GH centre:
    base --J1 (O20 hub, ACTIVE, axis b)--> link 1 (strap p1 -> p2, arc a1; carries an O28 x 3 mm groove face cam
    around J2) --J2 (O20 hub, ACTIVE)--> link 2a (strap p2 -> p4, arc alpha; MR52 follower on a lever + O2 Ti pushrod
    on top) --J4 (cross-spring flexure pivot, 12 x 12 x 6 mm block, PASSIVE, axis p4; its angle SLAVED q4 = c(q2) by the
    cam)--> link 2b (strap p4 -> p3, arc beta) --J3 (O20 hub, ACTIVE, axis W fixed in the humerus)--> arm stub
    (strap of neck_deg toward the elbow, humerus-fixed) -> user's cuff.
DOF: 3 ACTIVE (q1, q2, q3) + 1 PASSIVE SLAVED (q4 = c(q2), imposed by a positive-drive groove cam: J4 cannot move
unless J2 moves, so it is not a spare coordinate and cannot sag). Arm orientation = 3 numbers = 3 hub angles.

Kinematics (exact, vectorised; improves the spec's least-squares IK). In link 2a's frame p2, p4 are fixed and
p3(q4) = Rot(p4, q4) p3_straight, so the effective arc a2e(q4) = angle(p2, p3) and the angle phi(q4) at p2 between
the great circles p2->p4 and p2->p3 are closed-form functions of q4 alone. For a pose (p1 = b, p3 = HG W0, scapula
frame) and a trial q4: p2 = two-circle closure (a1 about p1, a2e(q4) about p3, the design's branch, the evaluator's
10 deg fold / stretch margin), q2 = psi = (angle at p2 from p1 to p3) - phi(q4). The pose's knee angle is a root of
    r(q4) = c(q2(q4)) - q4,   c(q2) = c0 + pchip(knots over the q2 range, values in [-rng, rng])
over the flexure range [c0 - rng, c0 + rng]; |c - c0| <= rng implies r changes sign across the range, so a root
exists whenever the closure is valid across it. All roots are found on a 0.1 deg grid and polished by secant steps
(residual < 1e-9 rad). Several roots = several assembly states: on the clips the root is tracked from the previous
frame at the full 10 fps (a frame whose tracked root vanished, or whose joint step exceeds 25 deg, is a flip = not
followed); for workspace poses (no history) the root nearest c(q2) of the straight-knee guess is taken.
c0 = 0 and zero knots with alpha + beta = a2 reproduce tools/concept_baseline.py exactly (checked: same axes).
The spec's convention (knee straight at the lowest pose, c relative) is the special case c0 = 0; c0 != 0 (a flexure
whose neutral is bent) is needed for the knee to LENGTHEN link 2 overhead (a straight knee is the longest a2e), so
the sweep adds c0 and the straight arc alpha + beta = a2 + dS (spec improvement, stated in the doc).

Parts at real size (tools/concept_baseline.py conventions: underside samples ~1 point / 4 mm2, radial profile fixed in
the part = p-th percentile over the kinematically valid poses of the outermost skin radius under the sample + 2 mm;
hubs flat at their max; link ends sit on their hubs; levels: up = stack 3.15 + link 3.0 = 6.15 mm per joint):
  hub1 O20 (level 0) | link1 strap 8 wide (0) | hub2 O20 + cam ring O28 (one flat disc r 14, level 0, 3 mm cam on
  link 1) | link2a strap (up) | flexure halves 6 x 12 mm each side of p4, flat, 6 mm tall (up) | link2b strap (up) |
  hub3 O20 (up) | arm stub strap (2 up).
Self-collision (non-adjacent bodies, >= 1 mm): bodies 0 base, 1 link1 + cam (+ J1/J2 hubs), 2a, 2b, 3 arm stub; every
part is a radial interval over its footprint (straps 3 mm, flexure 6 mm, cam 3 mm, hubs 12.25 mm stack, the v5 O20
hub); a pair is in collision when two footprint samples lie within 2.5 mm tangentially (1 mm + sampling) and their
radial intervals are less than 1 mm apart. Not taken: no valid root in the flexure range, a flip, a collision, or
any metal sample inside the body (the bench's contact rule).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/cam-unfold-4th.py [check|sweep|best]
"""
import json, math, os, sys, time
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_baseline as BL                                # noqa: E402

ID = "cam-unfold-4th"; NAME = "Cam-unfolding link: a slaved flexure knee in link 2"
D2R = math.pi / 180
SING, JUMP, Q4_JUMP = 10.0, 25.0, 4.0     # fold margin (deg), largest joint step / frame at 10 fps, knee root jump (deg)
UP = 3.15 + 3.0                           # level step per joint (stack + link), as the baseline
T_LINK, T_FLEX, T_CAM, H_HUB = 3.0, 6.0, 3.0, 12.25
PART_CLEAR, TAN_NEAR = 1.0, 2.5
CHAINS = dict(champ=dict(az=BL.CHAMP["az"], el=BL.CHAMP["el"], a=list(BL.CHAMP["a"]), w=list(BL.CHAMP["w"]), branch=-1),
              final=dict(az=32.55, el=80.56, a=[77.41, 81.45], w=[71.38, 4.78], branch=-1))
PARAMS = dict(chain="champ", f=0.5, dS=0.0, c0=0.0, knots=[0.0, 0.0, 0.0, 0.0, 0.0], rng=18.0, slope=0.6, pct=100.0,
              width=8.0, neck_deg=25.0, hub_r=10.0, cam_r=14.0, flex=12.0)
SWEEP = dict(chain=["champ", "final"], f=[0.3, 0.4, 0.5, 0.6, 0.7], dS=[0, 6, 12, 18, 24], c0=[-30, -18, 0, 18, 30],
             knots="5 values in [-rng, rng], |dc/dq2| <= 0.6", rng=[12, 16, 18, 20], pct=[60, 70, 80, 90, 95, 100])


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def ang(ax, a, c):
    """signed angle about unit axis ax from a to c (projected on the plane normal to ax)"""
    a_ = a - (a * ax).sum(-1, keepdims=True) * ax; c_ = c - (c * ax).sum(-1, keepdims=True) * ax
    return np.arctan2((np.cross(a_, c_) * ax).sum(-1), (a_ * c_).sum(-1))


def wrap(x): return (x + np.pi) % (2 * np.pi) - np.pi


def knee_tables(al, be, q4):
    """link-2a frame (p2 = x, p4 in the xy plane at alpha): effective arc a2e and the angle phi at p2 from p4 to p3"""
    q4 = np.asarray(q4, float); s = al + be
    p3 = (np.array([math.cos(s), math.sin(s), 0.0]) * np.cos(q4)[..., None] + np.array([0.0, 0.0, math.sin(be)]) * np.sin(q4)[..., None]
          + np.array([math.cos(al), math.sin(al), 0.0]) * (math.cos(be) * (1 - np.cos(q4)))[..., None])
    return np.arccos(np.clip(p3[..., 0], -1, 1)), np.arctan2(p3[..., 2], p3[..., 1])


class Cam:
    """c(q2) = c0 + pchip through the knots (values deg, positions over [lo, hi] rad), held constant outside"""
    def __init__(self, d, lo, hi):
        self.c0 = d["c0"] * D2R; self.lo, self.hi = lo, hi; k = np.asarray(d["knots"], float) * D2R
        self.x = np.linspace(lo, hi, len(k)); self.f = PchipInterpolator(self.x, k); self.df = self.f.derivative()
        xx = np.linspace(lo, hi, 400); self.max_slope = float(np.abs(self.df(xx)).max())

    def __call__(self, q2):
        return self.c0 + self.f(np.clip(q2, self.lo, self.hi))


def chain_of(d):
    C = dict(CHAINS[d["chain"]]); C.update({k: d[k] for k in ("az", "el", "a", "w") if k in d}); return C


def closure(d, HG, q4, ref):
    """for poses HG (n, 3, 3) and knee angles q4 (n,) [rad]: axes p1, p2, p4, p3 (n, 4, 3), validity, q2 (rel. ref)"""
    C = chain_of(d); A1 = C["a"][0] * D2R; S = (C["a"][1] + d["dS"]) * D2R; al, be = d["f"] * S, (1 - d["f"]) * S
    b = BL.bvec(C["az"], C["el"]); W0 = BL.w_dir(*C["w"]); n = len(HG)
    p1 = np.broadcast_to(b, (n, 3)); p3 = HG @ W0
    a2e, phi = knee_tables(al, be, q4)
    cd = np.clip((p1 * p3).sum(-1), -1, 1); n13 = unit(np.cross(p1, p3)); den = 1 - cd ** 2 + 1e-12
    ca = (np.cos(A1) - cd * np.cos(a2e)) / den; cb = (np.cos(a2e) - cd * np.cos(A1)) / den
    p = ca[:, None] * p1 + cb[:, None] * p3; h2 = 1 - (p * p).sum(-1)
    p2 = p + C["branch"] * np.sqrt(np.clip(h2, 0, None))[:, None] * n13
    th = np.arccos(cd); sg = SING * D2R
    ok = (h2 > 0) & (th >= np.abs(A1 - a2e) + sg) & (th <= np.minimum(A1 + a2e, 2 * np.pi - A1 - a2e) - sg)
    psi = ang(p2, p1, p3) - phi                              # angle at p2 from p1 to p4 = J2's angle
    t3 = unit(p3 - (p3 * p2).sum(-1, keepdims=True) * p2)
    c, s_ = np.cos(-phi)[:, None], np.sin(-phi)[:, None]    # rotate t3 by -phi about p2 -> t4
    t4 = t3 * c + np.cross(p2, t3) * s_ + p2 * (p2 * t3).sum(-1, keepdims=True) * (1 - c)
    p4 = math.cos(al) * p2 + math.sin(al) * unit(t4)
    return np.stack([p1, p2, p4, p3], 1), ok, wrap(psi - ref)


def solve(d, HG, cam, ref, prev=None, grid_step=0.1):
    """knee roots for poses HG: returns q4 (n,), ok (n,), nroots (n,), axes (n, 4, 3), q2 (n,).
    prev (n,) or None: root nearest prev is taken (clip tracking); else nearest the straight-knee guess."""
    n = len(HG); c0 = d["c0"] * D2R; R = d["rng"] * D2R
    g = c0 + np.arange(-R, R + 1e-9, grid_step * D2R); m = len(g)
    HGr = np.repeat(HG, m, 0); G = np.tile(g, n)
    _, okg, q2g = closure(d, HGr, G, ref)
    res = (cam(q2g) - G).reshape(n, m); okg = okg.reshape(n, m)
    sc = (np.sign(res[:, :-1]) != np.sign(res[:, 1:])) & okg[:, :-1] & okg[:, 1:]
    q4 = np.full(n, np.nan); nroots = sc.sum(1)
    guess = np.asarray(prev, float) if prev is not None else np.full(n, np.nan)
    for i in range(n):
        js = np.nonzero(sc[i])[0]
        if not len(js): continue
        rts = g[js] - res[i, js] * (g[js + 1] - g[js]) / (res[i, js + 1] - res[i, js])
        if not np.isnan(guess[i]): q4[i] = rts[np.argmin(np.abs(rts - guess[i]))]
        else:
            k0 = np.argmin(np.abs(g - c0)); gs = cam(q2g.reshape(n, m)[i, k0]) if okg[i, k0] else c0
            q4[i] = rts[np.argmin(np.abs(rts - gs))]
    have = ~np.isnan(q4); x = np.where(have, q4, c0)
    for _ in range(6):                                       # secant / Newton polish
        h = 1e-6
        _, o0, a0 = closure(d, HG, x, ref); _, o1, a1 = closure(d, HG, x + h, ref)
        r0 = cam(a0) - x; r1 = cam(a1) - (x + h); dr = (r1 - r0) / h
        x = np.where(have & (np.abs(dr) > 1e-9), x - r0 / np.where(np.abs(dr) > 1e-9, dr, 1), x)
    Pax, okp, q2 = closure(d, HG, x, ref)
    r = np.abs(cam(q2) - x)
    ok = have & okp & (r < 1e-7) & (np.abs(x - c0) <= R + 1e-9)
    return x, ok, nroots, Pax, q2


def joint_q(Pax, HG, W0, b):
    """joint angles q1, q2', q4', q3 for continuity checks (q2'/q4' from geometry, re-derived)"""
    p1, p2, p4, p3 = Pax[:, 0], Pax[:, 1], Pax[:, 2], Pax[:, 3]; n = len(Pax)
    r1 = np.broadcast_to(unit(np.cross(b, [1.0, 0.0, 0.0])), (n, 3)); hv = HG @ unit(np.cross(W0, [0.0, 1.0, 0.0]))
    return np.stack([ang(p1, r1, p2), ang(p2, p1, p4), ang(p4, p2, p3), ang(p3, p4, hv)], 1)


class Model:
    """kinematics on the bench poses + the full-rate fit clips for one parameter set"""
    def __init__(self, d, Z, idx):
        self.d = d; C = chain_of(d); self.C = C; self.Z = Z; self.idx = idx
        self.b = BL.bvec(C["az"], C["el"]); self.W0 = BL.w_dir(*C["w"])
        HG = Z["HG"].astype(float)
        # J2 reference and knot span: q2 over the valid poses of the straight-knee (c = c0 constant) chain
        dd = dict(d); dd["knots"] = [0.0] * len(d["knots"])
        _, ok0, q20 = closure(dd, HG, np.full(len(HG), d["c0"] * D2R), 0.0)
        self.ref = float(np.median(q20[ok0])) if ok0.any() else 0.0
        q2r = wrap(q20[ok0] - self.ref)
        lo, hi = (np.percentile(q2r, 1), np.percentile(q2r, 99)) if ok0.any() else (-1.0, 1.0)
        self.cam = Cam(d, lo, hi)

    def bench(self):
        HG = self.Z["HG"][self.idx].astype(float)
        q4, ok, nr, Pax, q2 = solve(self.d, HG, self.cam, self.ref)
        return q4, ok, nr, Pax, q2

    def clips(self):
        """full-rate fit clips: root tracking; returns {Z index: followed?}, flips, multi-root frames"""
        Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; good = {}; flips = 0; multi = 0; qd = {}
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            HG = Z["HG"][ii].astype(float)
            q4a, oka, nra, Pa, _ = solve(self.d, HG, self.cam, self.ref)        # all frames, default root (for nroots)
            multi += int((nra > 1).sum())
            prev_q4 = None; prev_q = None
            for j, gi in enumerate(ii):
                if nra[j] > 1 and prev_q4 is not None:
                    q4j, okj, _, Pj, _ = solve(self.d, HG[j:j + 1], self.cam, self.ref, prev=np.array([prev_q4]))
                    q4j, okj, Pj = q4j[0], bool(okj[0]), Pj
                else:
                    q4j, okj, Pj = q4a[j], bool(oka[j]), Pa[j:j + 1]
                g = okj
                if okj:
                    qj = joint_q(Pj, HG[j:j + 1], self.W0, self.b)[0]
                    if prev_q is not None:
                        dq = np.degrees(np.abs(wrap(qj - prev_q)))
                        if dq.max() > JUMP or abs(q4j - prev_q4) / D2R > Q4_JUMP: g = False; flips += 1
                    prev_q, prev_q4 = qj, q4j
                else:
                    prev_q = prev_q4 = None
                good[int(gi)] = g; qd[int(gi)] = q4j
        return good, flips, multi, qd


# ---- geometry ----------------------------------------------------------------------------------------------------
def parts_of(d, Pt, harm):
    """sample directions of every part (thorax frame): name -> (dirs (n, m, 3), level, thickness (m,), bodies, kind)"""
    C = chain_of(d); A1 = C["a"][0] * D2R; S = (C["a"][1] + d["dS"]) * D2R; al, be = d["f"] * S, (1 - d["f"]) * S
    p1, p2, p4, p3 = Pt[:, 0], Pt[:, 1], Pt[:, 2], Pt[:, 3]; w = d["width"]; n = len(Pt)
    out = {}
    out["hub1"] = (BL.disc_dirs(p1, d["hub_r"]), 0.0, H_HUB, (0, 1), "flat")
    out["link1"] = (BL.arc_dirs(p1, p2, A1, width=w), 0.0, T_LINK, (1,), "strap")
    D = BL.disc_dirs(p2, d["cam_r"]); u = p2[:, None]; rr = np.linalg.norm(D - (D * u).sum(-1, keepdims=True) * u, axis=-1) / (D * u).sum(-1) * 70.0
    out["hub2cam"] = (D, 0.0, np.where(rr[0] <= d["hub_r"] + 1e-6, H_HUB, T_CAM), (1, 2), "flat")
    out["link2a"] = (BL.arc_dirs(p2, p4, al, width=w), UP, T_LINK, (2,), "strap")
    hf = d["flex"] / 2 / 70.0
    out["flexA"] = (BL.arc_dirs(p4, p2, hf, width=d["flex"]), UP, T_FLEX, (2, 3), "flex")
    out["flexB"] = (BL.arc_dirs(p4, p3, hf, width=d["flex"]), UP, T_FLEX, (2, 3), "flex")
    out["link2b"] = (BL.arc_dirs(p4, p3, be, width=w), UP, T_LINK, (3,), "strap")
    out["hub3"] = (BL.disc_dirs(p3, d["hub_r"]), UP, H_HUB, (3, 4), "flat")
    ng = d["neck_deg"] * D2R
    nk_v = unit(np.cos(ng) * p3 + np.sin(ng) * unit(harm - (harm * p3).sum(-1, keepdims=True) * p3))
    out["neck"] = (BL.arc_dirs(p3, nk_v, ng, width=w), 2 * UP, T_LINK, (4,), "strap")
    res = {}
    for k, (Dd, lev, th, bod, kind) in out.items():
        Dd = Dd.reshape(n, -1, 3); m = Dd.shape[1]; th = np.broadcast_to(np.asarray(th, float), (m,)).copy()
        res[k] = dict(D=Dd, lev=lev, th=th, bodies=bod, kind=kind, ns=(BL.arc_dirs(p1[:1], p2[:1], A1, width=w).shape[1] if k == "link1" else None))
    # strap sample counts along (for the end-on-hub rule)
    for k, (u_, v_, a_) in dict(link1=(p1, p2, A1), link2a=(p2, p4, al), link2b=(p4, p3, be), neck=(p3, nk_v, ng)).items():
        res[k]["ns"] = BL.arc_dirs(u_[:1], v_[:1], a_, width=w).shape[1]
    return res


ENDS = dict(link1=("hub1", "hub2cam"), link2a=("hub2cam", "flex"), link2b=("flex", "hub3"), neck=("hub3", None))


def fit_profiles(parts, R, valid, pct, clear=2.0):
    """the baseline's rule: per sample the pct-th percentile over the valid poses of the outermost skin radius + clear;
    hubs / cam / flexure flat at their max; link ends (1/6 of the strap, >= 2 samples) sit on their hub (the baseline's
    level arithmetic, kept identical so the comparison is like for like)"""
    prof = {k: np.percentile(R[k][valid], pct, axis=0) + clear for k in parts}
    for k in ("hub1", "hub2cam", "hub3"): prof[k] = np.full_like(prof[k], prof[k].max())
    fl = max(prof["flexA"].max(), prof["flexB"].max()); prof["flexA"] = np.full_like(prof["flexA"], fl); prof["flexB"] = np.full_like(prof["flexB"], fl)
    for k, (h0, h1) in ENDS.items():
        n_s = parts[k]["ns"]; pr = prof[k].reshape(n_s, -1); end = max(2, n_s // 6)
        for h, sl in ((h0, slice(0, end)), (h1, slice(n_s - end, n_s))):
            if h is None: continue
            hk = "flexA" if h == "flex" else h
            pr[sl] = np.maximum(pr[sl], prof[hk].max() + parts[k]["lev"] - parts[hk]["lev"])
        prof[k] = pr.reshape(-1)
    return prof


def near_pairs(parts, i, r_nom=80.0):
    """candidate sample pairs of non-adjacent bodies' parts in pose i (footprints within TAN_NEAR mm at r_nom)"""
    out = []; ks = list(parts)
    for a in range(len(ks)):
        for b in range(a + 1, len(ks)):
            pa, pb = parts[ks[a]], parts[ks[b]]; ba, bb = set(pa["bodies"]), set(pb["bodies"])
            if ba & bb or any(abs(x - y) == 1 for x in ba for y in bb): continue      # same or adjacent bodies
            T = cKDTree(pb["D"][i] * r_nom); L = T.query_ball_point(pa["D"][i] * r_nom, TAN_NEAR)
            ia = np.repeat(np.arange(len(L)), [len(x) for x in L]); jb = np.concatenate([np.asarray(x, int) for x in L]) if len(ia) else np.zeros(0, int)
            if len(ia): out.append((ks[a], ks[b], ia, jb))
    return out


def collide(parts, prof, pairs):
    """first pair of non-adjacent parts whose radial intervals over nearby footprint samples are < PART_CLEAR apart"""
    for ka, kb, ia, jb in pairs:
        a0 = prof[ka][ia] + parts[ka]["lev"]; a1 = a0 + parts[ka]["th"][ia]
        b0 = prof[kb][jb] + parts[kb]["lev"]; b1 = b0 + parts[kb]["th"][jb]
        if (np.maximum(a0 - b1, b0 - a1) < PART_CLEAR).any(): return (ka, kb)
    return None


class Eval:
    """one bench (+ its poses' RS / HG) shared by every configuration"""
    def __init__(self, n_clip=60, n_ws=160):
        self.B = CB.Bench(n_clip, n_ws); self.Z = CB._poses_all(); B = self.B
        self.HG = self.Z["HG"][B.idx].astype(float); self.RS = self.Z["RS"][B.idx].astype(float)
        self.harm = np.einsum("pij,j->pi", self.RS @ self.HG, np.array([0.0, -1.0, 0.0]))

    def run(self, d, pcts=(60, 70, 80, 90, 95, 100), log=None, detail=False):
        B = self.B; t0 = time.time()
        M = Model(d, self.Z, B.idx)
        if M.cam.max_slope > d["slope"] + 1e-6: return dict(skipped=f"cam slope {M.cam.max_slope:.2f} > {d['slope']}")
        q4, ok, nr, Pax, q2 = M.bench()
        good, flips, multi, _ = M.clips()
        fol = np.array([good.get(int(g), True) for g in B.idx])
        valid = ok & fol
        Pt = np.einsum("pij,pkj->pki", self.RS, Pax)
        parts = parts_of(d, Pt, self.harm)
        R = {k: np.zeros(p["D"].shape[:2]) for k, p in parts.items()}
        vi = np.nonzero(valid)[0]
        for i in vi:
            allD = np.concatenate([p["D"][i] for p in parts.values()]); rr = BL.skin_radius(B, int(i), allD); o = 0
            for k, p in parts.items():
                m = p["D"].shape[1]; R[k][i] = rr[o:o + m]; o += m
        NP = {int(i): near_pairs(parts, int(i)) for i in vi}
        best = None; rows = []
        for pc in pcts:
            prof = fit_profiles(parts, R, vi, pc)
            B.reset(); ncol = 0; cpairs = {}
            for i in range(len(Pt)):
                if not valid[i]: B.record(i, None); continue
                c = collide(parts, prof, NP[i])
                if c: ncol += 1; cpairs[c] = cpairs.get(c, 0) + 1; B.record(i, None); continue
                B.record(i, np.concatenate([p["D"][i] * (prof[k] + p["lev"])[:, None] for k, p in parts.items()]))
            r = B.report(); r.update(pct=pc, collisions=ncol, cpairs={f"{a}/{b}": v for (a, b), v in cpairs.items()})
            rows.append(r)
            if best is None or r["gap"] < best["gap"]: best = r
        a2e = np.degrees([np.arccos(np.clip((Pax[valid, 1] * Pax[valid, 3]).sum(-1), -1, 1))])
        best.update(kin_ok=round(float(ok.mean()), 4), flips=flips, multi_root=multi, a2e=[round(float(a2e.min()), 1), round(float(a2e.max()), 1)],
                    q4=[round(float(np.degrees(np.nanmin(q4[valid]))), 1), round(float(np.degrees(np.nanmax(q4[valid]))), 1)],
                    cam_slope=round(M.cam.max_slope, 3), secs=round(time.time() - t0, 1))
        if detail: best["rows"] = rows; best["_state"] = (M, Pt, parts, R, valid)
        return best


def auto_dS(d):
    """straight-arc extension so that the neutral (bent c0) knee keeps the base chain's a2"""
    C = chain_of(d); a2 = C["a"][1] * D2R; f = d["f"]
    lo, hi = 0.0, 60.0
    for _ in range(50):
        m = 0.5 * (lo + hi); S = a2 + m * D2R
        if knee_tables(f * S, (1 - f) * S, d["c0"] * D2R)[0] < a2: lo = m
        else: hi = m
    return round(0.5 * (lo + hi), 3)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "kin":
    Z = CB._poses_all(); B = CB.Bench(60, 160)
    for d in (PARAMS, dict(PARAMS, knots=[-10, -5, 0, 5, 10]), dict(PARAMS, c0=-18, dS=12, knots=[0, 6, 12, 18, 18])):
        M = Model(d, Z, B.idx); q4, ok, nr, Pax, q2 = M.bench()
        _, okb, _ = BL.pins(dict(BL.CHAMP), Z["HG"][B.idx].astype(float), np.broadcast_to(np.eye(3), (len(B.idx), 3, 3)))
        g, fl, mu, _ = M.clips()
        print(d["c0"], d["dS"], d["knots"], "ok", ok.mean().round(3), "baseline ok", okb.mean().round(3), "nroots", np.bincount(nr),
              "q4 deg", np.round(np.degrees([np.nanmin(q4), np.nanmax(q4)]), 1), "cam slope", round(M.cam.max_slope, 2), "flips", fl, "multi", mu)

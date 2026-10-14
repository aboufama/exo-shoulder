"""Conformal D4 evaluator: links shaped to the skin instead of concentric shells.

Only the joint AXES must pass through the shoulder centre. Each link is a rigid ribbon whose skin-side surface height
h(l) (radius from the GH centre, per point l of its footprint in its own frame) is the lowest that clears the skin by
C mm in every pose it covers; each joint's stacked hubs sit as low as their footprint allows. Per pose the spare joint
J1 is chosen to keep every link under its envelope. Reported: coverage and the skin gap (h - skin radius) over every
link point in every covered pose - the user wants it within 10 mm.

Maps: radial_maps.npz (radial_maps.py): per direction from the GH centre, first skin exit r1, next re-entry r2, and
the clearance band [r1c, r2c] (>= 3 mm from every skin point); trunk per elevation bin (thorax frame), arm in the
canonical humerus frame.
"""
import json, math, os
import numpy as np
os.environ.setdefault("H_LEN", "325")
import design_search as D, design_search_families as F
from design_search_pivots import w_dir

HERE = os.path.dirname(os.path.abspath(__file__))
_M = np.load(os.path.join(HERE, "radial_maps.npz")); RES = math.radians(float(_M["res"])); ELEVS = _M["elevs"]
def _fix(r1): r1 = r1.copy(); r1[~np.isfinite(r1)] = 0.0; return r1
T_R1, T_R1C, T_R2C = _fix(_M["t_r1"]), _M["t_r1c"], _M["t_r2c"]
A_R1, A_R1C, A_R2C = _fix(_M["a_r1"]), _M["a_r1c"], _M["a_r2c"]
NH, NW = A_R1.shape


def _cosmap(r1):
    """cos of the angle between the ray and the skin normal (normal gap = radial gap * cos)"""
    r = np.where(r1 > 0, r1, np.nan); lat = (np.arange(r.shape[-2]) + 0.5) * RES - math.pi / 2
    dlat = np.gradient(r, RES, axis=-2); dlon = np.gradient(r, RES, axis=-1) / np.maximum(np.cos(lat), 0.05)[:, None]
    c = r / np.sqrt(r ** 2 + dlat ** 2 + dlon ** 2)
    return np.nan_to_num(np.clip(c, 0.2, 1.0), nan=1.0).astype(np.float32)
T_COS = np.stack([_cosmap(m) for m in T_R1]); A_COS = _cosmap(A_R1)

POSES = D.POSES
PL = np.array([p[0] for p in POSES]); EL = np.array([p[1] for p in POSES]); AX = np.array([p[2] for p in POSES])
HG = np.array([p[3] for p in POSES]); RS = np.array([p[4] for p in POSES])
EB = np.array([int(np.argmin(np.abs(ELEVS - e))) for e in EL])

HUB_R, HW, T_IN, T_OUT, J_STACK = 17.0, 7.0, 5.0, 5.5, 14.1   # mm
R_REF = float(os.environ.get("R_REF", 100.0))                                                  # footprint angular sizes are set at this radius


def pix(w):
    """w (..., 3) unit -> flat pixel index"""
    lon = np.arctan2(w[..., 2], w[..., 0]); lat = np.arcsin(np.clip(w[..., 1], -1, 1))
    j = np.clip(((lon + math.pi) / RES).astype(np.int32), 0, NW - 1); i = np.clip(((lat + math.pi / 2) / RES).astype(np.int32), 0, NH - 1)
    return i * NW + j


def footprint(theta, n_arc=16):
    """sample points of a link in its local frame (start pin = x, end pin at angle theta in the xy plane): centreline +
    both strip edges, hub rings at both ends. Returns (dirs (M,3), arc parameter s in [0,1], lateral w mm, kind)"""
    pts, ss, wws, kind = [], [], [], []
    a0 = (HUB_R + 5.0) / R_REF; a1 = theta - a0
    for s in np.linspace(a0, a1, n_arc):
        for w in (-HW, 0.0, HW):
            d = np.array([math.cos(s), math.sin(s), w / R_REF]); pts.append(d / np.linalg.norm(d)); ss.append(s / theta); wws.append(w); kind.append(0)
    for end, ang in ((0, 0.0), (1, theta)):
        c = np.array([math.cos(ang), math.sin(ang), 0.0]); t1 = np.array([-math.sin(ang), math.cos(ang), 0.0]); t2 = np.array([0, 0, 1.0])
        for k in range(9):
            if k == 0: d = c
            else:
                phi = 2 * math.pi * (k - 1) / 8; rr = HUB_R / R_REF
                d = math.cos(rr) * c + math.sin(rr) * (math.cos(phi) * t1 + math.sin(phi) * t2)
            pts.append(d / np.linalg.norm(d)); ss.append(float(end)); wws.append(0.0); kind.append(1 + end)
    return np.array(pts), np.array(ss), np.array(wws), np.array(kind)


def link_frame(a, c):
    """(..., 3, 3): columns x = a, y = in-plane toward c, z = normal"""
    n = c - (a * c).sum(-1, keepdims=True) * a; n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-12
    return np.stack([a, n, np.cross(a, n)], -1)


class Design:
    def __init__(self, d):
        self.d = d; self.b = np.asarray(d["b"], float); self.a = [d[k] * D.D2R for k in ("a1", "a2", "a3")]
        self.W = w_dir(d["delta"], d["waz"]); self.branch = d.get("branch", 1)
        e = np.cross(self.b, [0.0, 1, 0]); e /= np.linalg.norm(e); self.e, self.f = e, np.cross(self.b, e)
        self.fp = [footprint(t) for t in self.a]

    def pins(self, idx, qs):
        """pins for poses idx x spare angles qs: dict of (P, Q, 3) and ok (P, Q)"""
        Hg = HG[idx]; u4 = Hg @ self.W                                                # (P, 3)
        c2 = math.cos(self.a[0]) * self.b + math.sin(self.a[0]) * (np.cos(qs)[:, None] * self.e + np.sin(qs)[:, None] * self.f)   # (Q, 3)
        C2 = np.broadcast_to(c2[None], (len(idx), len(qs), 3)); U4 = np.broadcast_to(u4[:, None], C2.shape); B = np.broadcast_to(self.b, C2.shape)
        c3, ok = F.circ_int(C2, self.a[1], U4, self.a[2], self.branch)
        ok &= F.triangle_ok(C2, U4, self.a[1], self.a[2]) & F.triangle_ok(B, c3, self.a[0], self.a[1]) & (np.abs((B * U4).sum(-1)) <= math.cos(F.SING))
        return dict(b=B, c2=C2, c3=c3, u4=U4), ok

    def sample(self, idx, qs):
        """per pose x q x link point: lo (required skin-side radius), hi (re-entry limit), skin radius"""
        P, ok = self.pins(idx, qs); out = []
        Rs = RS[idx]; Hg = HG[idx]; eb = EB[idx]
        for k, (A_, B_) in enumerate((("b", "c2"), ("c2", "c3"), ("c3", "u4"))):
            Fm = link_frame(P[A_], P[B_]); L = self.fp[k][0]                            # (P,Q,3,3), (M,3)
            w = np.einsum("pqij,mj->pqmi", Fm, L)                                         # scapula frame dirs
            wt = np.einsum("pij,pqmj->pqmi", Rs, w); wh = np.einsum("pji,pqmj->pqmi", Hg, w)
            it = pix(wt); ih = pix(wh); e3 = eb[:, None, None]
            lo = np.maximum(T_R1C[e3, it // NW, it % NW], A_R1C.ravel()[ih])
            hi = np.minimum(T_R2C[e3, it // NW, it % NW], A_R2C.ravel()[ih])
            skt, ska = T_R1[e3, it // NW, it % NW], A_R1.ravel()[ih]
            sk = np.maximum(skt, ska); cs = np.where(skt >= ska, T_COS[e3, it // NW, it % NW], A_COS.ravel()[ih])
            out.append((lo, hi, sk, cs))
        return out, ok, P


def evaluate(d, stride=3, q_step=10, gap=10.0, keep=0.97, iters=3, full=False):
    """returns dict: cov (fraction of all natural poses covered), gap stats over covered poses, joint heights"""
    Dz = Design(d); idx = np.arange(0, len(POSES), stride); qs = np.radians(np.arange(0, 360, q_step))
    S, ok, P = Dz.sample(idx, qs)
    big = 1e4
    # per (pose, q): feasibility needs ok; envelope per link point = quantile of required heights over chosen configs
    LO_MAX = 150.0                                                  # a link point needing more radius than this is impossible
    lo = [np.where(ok[..., None], s[0], big) for s in S]
    bad = np.zeros(ok.shape, bool)
    for k in range(3): bad |= (lo[k] > LO_MAX).any(-1)
    ok = ok & ~bad; lo = [np.where(ok[..., None], l, big) for l in lo]
    hi = [s[1] for s in S]; sk = [s[2] for s in S]
    # initial choice: q that minimises the worst required height above the pose's own skin (lowest 'stretch')
    def choose(env):
        cost = np.zeros(ok.shape)
        for k in range(3):
            exc = np.maximum(0.0, lo[k] - env[k][None, None, :]); cost = np.maximum(cost, exc.max(-1))
        cost = np.where(ok, cost, big); qbest = cost.argmin(1); return qbest, cost[np.arange(len(idx)), qbest]
    env = [np.full(len(Dz.fp[k][0]), 0.0) for k in range(3)]
    q_sel, c_sel = choose(env)
    for it in range(iters):
        valid = c_sel < big / 2
        env = []
        for k in range(3):
            L = lo[k][np.arange(len(idx)), q_sel][valid]                                  # (Pv, M)
            env.append(np.quantile(L, keep, axis=0) if len(L) else np.full(lo[k].shape[-1], big))
        q_sel, c_sel = choose(env)
    covered = c_sel <= 1e-6
    # hi limit (re-entry): link outer surface must stay below
    for k, t in zip(range(3), (T_OUT, T_IN, T_OUT)):
        H = hi[k][np.arange(len(idx)), q_sel]; covered &= (env[k][None, :] + t <= H).all(-1)
    gaps = []
    for k in range(3):
        Sk = sk[k][np.arange(len(idx)), q_sel][covered]; g = env[k][None, :] - Sk; gaps.append(g)
    G = np.concatenate([g.ravel() for g in gaps]) if covered.any() else np.array([99.0])
    out = dict(d, cov=float(covered.mean()), gap_p50=float(np.median(G)), gap_p90=float(np.percentile(G, 90)), gap_max=float(G.max()),
               within=float((G <= gap).mean()), env_mean=[float(e.mean()) for e in env])
    if full: out.update(env=[e.tolist() for e in env], q_sel=q_sel.tolist(), covered=covered.tolist(), idx=idx.tolist())
    return out


if __name__ == "__main__":
    import sys, time
    for f in sys.argv[1:]:
        d = json.load(open(f))[0]; t0 = time.time(); r = evaluate(d)
        print(f"{os.path.basename(f)}: cov {100 * r['cov']:.1f}%  gap p50 {r['gap_p50']:.1f}  p90 {r['gap_p90']:.1f}  max {r['gap_max']:.1f} mm,"
              f" within 10 mm {100 * r['within']:.0f}%  env mean {np.round(r['env_mean'], 1)}  ({time.time() - t0:.1f}s)")


# ---------------------------------------------------------------- "hug at rest" evaluation
REST = int(np.nonzero((PL == 0) & (EL == 0) & (AX == 0))[0][0])          # arm hanging, canonical humerus frame
STACK = 6.0                                                             # outer member's hub face above the inner one (5 plate + 1 washer)
RAMP = math.tan(math.radians(35.0))                                     # steepest climb a ribbon makes off its joint


def evaluate_rest(d, G=10.0, stride=4, q_step=15, q_rest_step=30, z_j4=None, full=False):
    """Links capped at (rest-pose skin + G) everywhere, joint stacks capped so the upper member's face is also within
    G at rest; a pose is covered if some spare-joint angle keeps every link point >= C mm off the skin under those caps
    (and below re-entry). d['order'] = (o1, o2, o3): 1 -> the first-named member is the inner one at J1 (base|l1),
    J2 (l1|l2), J3 (l2|l3); at J4 the arm link (BOTTOM, hub face z_j4) is inner and l3 outer."""
    Dz = Design(d); order = d.get("order", (1, 0, 1))
    idx = np.r_[REST, np.arange(0, len(POSES), stride)]; qs = np.radians(np.arange(0, 360, q_step))
    S, ok, P = Dz.sample(idx, qs)
    big = 1e4
    best = None
    kinds = [Dz.fp[k][3] for k in range(3)]
    # member role at each hub of each link: link k start hub joint = k+1, end hub joint = k+2
    def outer_at(k, end):
        J = k + 1 + end                                   # 1-based joint index
        if J == 1: return order[0] == 1                   # base inner -> l1 outer
        if J == 2: return (order[1] == 1) if k == 1 else (order[1] == 0)    # l1|l2: o2=1 -> l1 inner -> l2 outer
        if J == 3: return (order[2] == 1) if k == 2 else (order[2] == 0)
        return True                                       # J4: l3 outer over BOTTOM
    rest_q = np.arange(0, len(qs), max(1, int(q_rest_step / q_step)))
    for qr in rest_q:
        if not ok[0, qr]: continue
        caps = []; okp = ok[1:].copy()
        for k in range(3):
            lo, hi, sk, cs = S[k]; skr = sk[0, qr]; csr = np.maximum(cs[0, qr], 0.5); cap = skr + G / csr
            # hub points: the stack is capped by the lowest rest skin over the disc; inner face <= cap - STACK
            for end in (0, 1):
                m = kinds[k] == 1 + end
                if not m.any(): continue
                # the stack's lower face: as close as the rest skin allows (>= rest clearance over the whole disc)
                face = max(lo[0, qr][m].max(), (skr[m] + G / csr[m]).min())
                if k == 2 and end == 1 and z_j4 is not None: face = z_j4                # BOTTOM's fixed hub is the lower member
                cap = cap.copy(); cap[m] = face                                          # clearance is needed at the lower face
            # buildability: near each joint the ribbon only climbs at <= RAMP from that joint's face
            kind_k = kinds[k]; s_k = Dz.fp[k][1]; th_k = Dz.a[k]
            faceA = cap[kind_k == 1].max() + (STACK if outer_at(k, 0) else 0.0)
            faceB = cap[kind_k == 2].max() + ((STACK + (1.5 if k == 2 else 0.0)) if outer_at(k, 1) else 0.0)
            dA = s_k * th_k * (faceA + 3.0); dB = (1 - s_k) * th_k * (faceB + 3.0)
            lim = np.minimum(faceA + RAMP * np.maximum(dA - (HUB_R + 6.0), 0), faceB + RAMP * np.maximum(dB - (HUB_R + 6.0), 0))
            cap = np.where(kind_k == 0, np.minimum(cap, lim), cap)
            caps.append(cap)
            if (lo[0, qr] > cap + 1e-6).any(): okp[:] = False; break
            okp &= (lo[1:] <= cap[None, None, :]).all(-1) & ((cap + (T_IN if k == 1 else T_OUT))[None, None, :] <= hi[1:]).all(-1)
        if len(caps) < 3: continue
        cov_mask = okp.any(1); cov = float(cov_mask.mean())
        if best is None or cov > best[0]: best = (cov, qr, caps, cov_mask, okp)
    if best is None: return dict(d, cov=0.0)
    cov, qr, caps, cov_mask, okp = best
    # gaps over covered poses (choose per pose the q with the lowest worst gap among the valid ones)
    gaps = []
    gsum = np.zeros(okp.shape)
    for k in range(3): gsum = np.maximum(gsum, ((caps[k][None, None, :] - S[k][2][1:]) * S[k][3][1:]).max(-1))
    qsel = np.where(okp, gsum, big).argmin(1); ar = np.arange(okp.shape[0])
    for k in range(3):
        G_ = (caps[k][None, :] - S[k][2][1:][ar, qsel]) * S[k][3][1:][ar, qsel]; gaps.append(G_[cov_mask])
    Gall = np.concatenate([g.ravel() for g in gaps]) if cov_mask.any() else np.array([99.0])
    out = dict(d, cov=cov, q_rest=float(np.degrees(qs[qr])), gap_p50=float(np.median(Gall)), gap_p90=float(np.percentile(Gall, 90)),
               gap_max=float(Gall.max()), per_link_p50=[float(np.median(g)) if g.size else 99 for g in gaps])
    if full: out.update(caps=[c.tolist() for c in caps], cov_mask=cov_mask.tolist(), idx=idx[1:].tolist())
    return out


def export_envelope(d, G=10.0, z_j4=67.5, stack=6.0, out=None):
    """full-resolution envelope for the CAD: per link the lowest skin-side height at every footprint point that clears
    every covered pose (with the per-pose spare angle chosen), each joint's lower-face height, the rest spare angle."""
    global STACK
    STACK = stack
    r = evaluate_rest(d, G=G, stride=1, q_step=6, q_rest_step=6, z_j4=z_j4, full=True)
    Dz = Design(d); idx = np.array(r["idx"]); qs = np.radians(np.arange(0, 360, 6)); cov = np.array(r["cov_mask"])
    S, ok, P = Dz.sample(idx, qs); caps = [np.array(c) for c in r["caps"]]
    okp = ok.copy()
    for k in range(3):
        okp &= (S[k][0] <= caps[k][None, None, :]).all(-1)
    # per pose: q with the smallest worst gap among the valid ones
    gw = np.zeros(okp.shape)
    for k in range(3): gw = np.maximum(gw, ((caps[k][None, None, :] - S[k][2]) * S[k][3]).max(-1))
    qsel = np.where(okp, gw, 1e9).argmin(1); good = okp[np.arange(len(idx)), qsel] & cov
    env = []
    for k in range(3):
        L = S[k][0][np.arange(len(idx)), qsel][good]; env.append(np.maximum(L.max(0), 0.0))
    # rest pose (with the rest spare angle) is always included
    Sr, okr, Pr = Dz.sample(np.array([REST]), np.radians([r["q_rest"]]))
    for k in range(3): env[k] = np.maximum(env[k], Sr[k][0][0, 0])
    res = dict(design=d, G=G, z_j4=z_j4, stack=stack, cov=r["cov"], q_rest=r["q_rest"], env=[e.tolist() for e in env], caps=r["caps"],
               fp=[dict(dirs=Dz.fp[k][0].tolist(), s=Dz.fp[k][1].tolist(), w=Dz.fp[k][2].tolist(), kind=Dz.fp[k][3].tolist()) for k in range(3)],
               rest_pins={k: v[0, 0].tolist() for k, v in Pr.items()}, covered_idx=idx[good].tolist(), qsel=qsel[good].tolist(),
               gap_p50=r["gap_p50"], gap_p90=r["gap_p90"], per_link_p50=r["per_link_p50"])
    if out: json.dump(res, open(out, "w"))
    return res

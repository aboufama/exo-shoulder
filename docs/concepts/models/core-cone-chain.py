"""core-cone-chain: a spherical 3-DOF chain whose three joints are conical rolling-contact pairs (CORE) instead of
pinned O20 hubs, every part in ONE layer over the skin. Concept screen on tools/concept_bench.py (idealised geometry,
every part at its real size). Spec: docs/concepts/catalogue.json id core-cone-chain; write-up docs/concepts/core-cone-chain.md.

Topology: scapula base (disc A1 + a stub to the handler) =J1= link 1 (disc B1 - strap S1 - disc A2) =J2= link 2
(disc B2 - strap S2 - disc A3) =J3= arm end (disc B3 + neck strap to BOTTOM, fixed in the humerus).
Joint k = two cone frustums with their apex at the GH centre, axes cA_k (proximal body) and cB_k (distal body),
half-angles bA, bB, touching along a generator; crossed bands make the motion a one-parameter roll psi_k:
    distal = proximal . Rot(cA_k, psi_k) Rot(cB_k, c_k psi_k),   c_k = sin bA / sin bB  (c = 1: equal cones)
(disc B orbits disc A by psi and spins c.psi; relative turn ~ (1 + c) psi). 3 ACTIVE coordinates (psi1..3), no
passive one, no idle body (DOF count in the .md).

Kinematics (all in the scapula frame, like the band evaluator / tools/concept_baseline.py): the reference spherical
3R (b fixed in the scapula, W fixed in the humerus, two-circle closure on the design's branch, the baseline's sing_deg
margin) gives joint values q over every fit-clip frame (full rate) and every bench pose; the reference configuration is
each joint's mid-range q_mid (largest-gap rule on the circle), its axes m1, m2, m3 are the pair mean axes, Q0 the arm
orientation there. Pair k: n_k = default in-plane direction (J1: toward J2; J2 / J3: from the incoming to the outgoing
member, i.e. unit(t_out - t_in)) turned by n_k deg about m_k. cA = cos bA m - sin bA n, cB = cos bB m + sin bB n,
bA = atan(rho / F_k), bB = atan(ratio rho / F_k), F_k = the joint's skin-face radius (p-th percentile of the skin
radius over a rho disc on the 3R axis + clear). IK: batched Newton on rotvec(HG R(psi)^T) from the 3R seed
psi = dq / (1 + c); accepted if the residual < 1e-6 rad, |psi_k| <= psi_max, the solution stays within 20 deg of the
3R seed (same branch) and the 3R is >= sing_deg from its fold / stretch singularity.

Geometry (mm, thorax frame of the bench, origin GH), sampled exactly like tools/concept_baseline.py (straps 2 mm along
and across at r_ref 70 mm, discs a 2.5 mm grid at r_ref 70 mm), skin-facing faces only:
  * discs: angular radius bA / bB around cA / cB (physical radius rho at F), flat face, `disc_h` tall (collisions);
    both discs of a pair share one face radius (rolling cones must overlap radially) = max of the two requirements;
  * straps `width` x `t_link` on the great circle between the disc centres of a body, trimmed at the disc rims;
    rows within `end_mm` of a disc rim sit at least at that disc's face (same layer, attached to the disc's side);
  * base stub: `stub` mm of strap from disc A1 on -n1 (the handler attachment; body 0);
  * neck: strap from disc B3 to the baseline's neck end (J3 axis turned neck_deg toward the arm axis), body 3.
  Radial profile of every sample fixed in its body = p-th percentile over the taken poses of the outermost skin radius
  under it (concept_baseline.skin_radius) + clear; the sweep over p trades contact against closeness exactly as the
  baseline does. Single layer: no member rides on another, the neck and link 2 are at the skin like link 1.
Taken pose: IK accepted, no two parts of different bodies (except the rolling partners A_k / B_k) closer than
part_clear (capsule footprints in the tangent layer: discs radius rho, straps half-width), no metal inside the body
(bench contact), and for clip frames: every full-rate frame of the clip between the previous bench frame and this one
passes the same kinematic + collision checks with no joint step > 20 deg between consecutive frames (no branch flip).

    python3 docs/concepts/models/core-cone-chain.py check [n_clip n_ws]   # IK / geometry checks, a few named poses
    python3 docs/concepts/models/core-cone-chain.py sweep                 # sweeps/core-cone-chain.json, rows/
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                        # noqa: E402
import concept_baseline as BL                                     # noqa: E402

ID = "core-cone-chain"
D2R = math.pi / 180
R_REF = 70.0                                                      # mm -> rad for sample spacing (the baseline's)
SEEDS = dict(champ=dict(az=BL.CHAMP["az"], el=BL.CHAMP["el"], a=list(BL.CHAMP["a"]), w=list(BL.CHAMP["w"]), branch=-1),
             final=dict(az=32.55, el=80.56, a=[77.41, 81.45], w=[71.38, 4.78], branch=-1))
PARAMS = dict(seed="champ", sing_deg=10.0, rho=7.0, ratio=1.0, disc_h=4.5, psi_max=85.0, n1=0.0, n2=0.0, n3=0.0,
              width=8.0, t_link=3.0, clear=2.0, neck_deg=25.0, stub=10.0, part_clear=1.0, end_mm=6.0, pct=90)
SWEEP = dict(seed=("champ", "final"), rho=(5.0, 10.0), ratio=(0.7, 1.4), psi_max=(70.0, 95.0), n1=(-90, 90), n2=(-90, 90),
             n3=(-90, 90), pct=(60, 70, 80, 85, 90, 95, 100), width=(8.0, 14.0))
PCTS = (60, 70, 80, 85, 90, 95, 100)
FIT_IDS = None


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-15)


def rotm(ax, ang):
    """Rodrigues, batched: ax (..., 3) or (3,), ang (...) -> (..., 3, 3)"""
    ang = np.asarray(ang, float); ax = np.broadcast_to(np.asarray(ax, float), ang.shape + (3,))
    x, y, z = ax[..., 0], ax[..., 1], ax[..., 2]; c, s = np.cos(ang), np.sin(ang); C = 1 - c
    return np.stack([np.stack([c + x * x * C, x * y * C - z * s, x * z * C + y * s], -1),
                     np.stack([y * x * C + z * s, c + y * y * C, y * z * C - x * s], -1),
                     np.stack([z * x * C - y * s, z * y * C + x * s, c + z * z * C], -1)], -2)


def sang(u, v, ax):
    """signed angle about ax from u to v (projected), batched"""
    ax = np.broadcast_to(ax, np.broadcast_shapes(np.shape(u), np.shape(v)))
    pu = u - (u * ax).sum(-1, keepdims=True) * ax; pv = v - (v * ax).sum(-1, keepdims=True) * ax
    return np.arctan2((ax * np.cross(pu, pv)).sum(-1), (pu * pv).sum(-1))


def tang(m, v): return unit(v - (m * v).sum(-1, keepdims=True) * m)


def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi


def mid_range(q):
    """middle of the occupied arc of angles q (largest-gap rule) and the arc length"""
    s = np.sort(wrap(q)); g = np.diff(np.r_[s, s[0] + 2 * math.pi]); k = int(np.argmax(g))
    lo = s[(k + 1) % len(s)]; span = 2 * math.pi - g[k]
    return wrap(lo + span / 2), span


# ---- data ----------------------------------------------------------------------------------------------------------
class Data:
    """poses for kinematics: every fit-clip frame (full rate, for continuity) + the bench's workspace poses"""
    def __init__(self, B):
        Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
        fit = [names.index(n) for n in CB.FIT]
        fit_frames = np.nonzero(np.isin(cid, fit))[0]
        ws_b = np.array([z for z, k in zip(B.idx, B.kind) if k == "ws"], int)
        self.K = np.unique(np.r_[fit_frames, ws_b, B.idx])               # Z indices
        self.pos = {int(z): j for j, z in enumerate(self.K)}
        self.HG = Z["HG"][self.K].astype(float); self.RS = Z["RS"][self.K].astype(float)
        self.bk = np.array([self.pos[int(z)] for z in B.idx])          # bench pose -> row of K
        self.cid = cid; self.Zidx = B.idx
        # clip segments: for each bench clip frame, the K rows from the previous bench frame of the clip (or the
        # clip start) up to it, in time order
        self.seg = {}
        for c, js in B.clip_order().items():
            zc = np.nonzero(cid == names.index(c))[0]; prev = zc[0]
            for j in js:
                z = int(B.idx[j]); self.seg[j] = [self.pos[int(t)] for t in range(int(prev), z + 1)]; prev = z


# ---- kinematics ----------------------------------------------------------------------------------------------------
def ref_chain(seed, D, sing_deg):
    """3R closed form on every K pose: joint values q (n, 3), validity, and the mid-range reference config"""
    s = SEEDS[seed]; A = [x * D2R for x in s["a"]]; b = BL.bvec(s["az"], s["el"]); W0 = BL.w_dir(*s["w"]); n = len(D.HG)
    p1 = np.broadcast_to(b, (n, 3)); p3 = D.HG @ W0
    p2, ok = BL.circ_int(p1, A[0], p3, A[1], float(s["branch"]))
    ok = ok & BL.tri_ok(p1, p3, A[0], A[1], sing_deg * D2R)
    r0 = int(np.nonzero(ok)[0][0]); m20, m30, Q00 = p2[r0], p3[r0], D.HG[r0]
    q1 = sang(np.broadcast_to(m20, (n, 3)), p2, b); R1 = rotm(b, q1)
    p3b = np.einsum("nji,nj->ni", R1, p3); q2 = sang(np.broadcast_to(m30, (n, 3)), p3b, m20)
    R2 = R1 @ rotm(m20, q2)
    x0 = unit(np.cross(m30, [0.3, 0.5, 0.8])); Hb = np.einsum("nji,njk->nik", R2, D.HG) @ Q00.T
    q3 = sang(np.broadcast_to(x0, (n, 3)), Hb @ x0, m30)
    q = np.stack([q1, q2, q3], 1); qm = np.zeros(3); span = np.zeros(3)
    for k in range(3): qm[k], span[k] = mid_range(q[ok, k])
    T1 = rotm(b, qm[0]); T2 = T1 @ rotm(m20, qm[1])
    m = np.stack([b, T1 @ m20, T2 @ m30])
    Q0 = T2 @ rotm(m30, qm[2]) @ Q00
    dq = wrap(q - qm[None])
    # check the POE identity on the valid poses
    Rchk = rotm(m[0], dq[:, 0]) @ rotm(m[1], dq[:, 1]) @ rotm(m[2], dq[:, 2]) @ Q0
    err = np.linalg.norm(Rchk - D.HG, axis=(1, 2))[ok]
    assert err.max() < 1e-6, err.max()
    return dict(m=m, Q0=Q0, dq=dq, ok=ok, span=span, b=b, W0=W0)


def pair_axes(m, Q0, prm, F):
    """per joint: n_k, cA_k, cB_k, bA, bB, c (spin factor); and the neck end e0 (scapula coords, reference config)"""
    h0 = Q0 @ np.array([0.0, -1.0, 0.0]); ng = prm["neck_deg"] * D2R
    e0 = math.cos(ng) * m[2] + math.sin(ng) * tang(m[2], h0)
    nd = [tang(m[0], m[1]), unit(tang(m[1], m[2]) - tang(m[1], m[0])), unit(tang(m[2], e0) - tang(m[2], m[1]))]
    out = []
    for k in range(3):
        n = rotm(m[k], prm[f"n{k + 1}"] * D2R) @ nd[k]
        bA = math.atan(prm["rho"] / F[k]); bB = math.atan(prm["ratio"] * prm["rho"] / F[k])
        cA = math.cos(bA) * m[k] - math.sin(bA) * n; cB = math.cos(bB) * m[k] + math.sin(bB) * n
        out.append(dict(n=n, cA=cA, cB=cB, bA=bA, bB=bB, c=math.sin(bA) / math.sin(bB)))
    return out, e0


def fk(P, Q0, psi):
    """body rotations (n, 4, 3, 3) (scapula coords, relative to the reference config), the arm orientation and the
    spatial Jacobian (n, 3, 3)"""
    n = len(psi); Bd = [np.broadcast_to(np.eye(3), (n, 3, 3))]; cols = []; T = Bd[0]
    for k in range(3):
        EA = rotm(P[k]["cA"], psi[:, k]); col = np.einsum("nij,j->ni", T, P[k]["cA"]); T = T @ EA
        col = col + P[k]["c"] * np.einsum("nij,j->ni", T, P[k]["cB"]); T = T @ rotm(P[k]["cB"], P[k]["c"] * psi[:, k])
        Bd.append(T); cols.append(col)
    return np.stack(Bd, 1), T @ Q0, np.stack(cols, -1)


def ik(P, Q0, HG, seed, iters=30):
    psi = seed.copy(); n = len(psi)
    for _ in range(iters):
        _, R, J = fk(P, Q0, psi)
        e = Rotation.from_matrix(HG @ np.transpose(R, (0, 2, 1))).as_rotvec()
        dt = np.linalg.solve(J + 1e-12 * np.eye(3), e[..., None])[..., 0]
        dt = np.clip(dt, -0.3, 0.3); psi = psi + dt
        if np.abs(e).max() < 1e-12: break
    Bd, R, J = fk(P, Q0, psi)
    res = np.linalg.norm(Rotation.from_matrix(HG @ np.transpose(R, (0, 2, 1))).as_rotvec(), axis=1)
    return psi, Bd, res, J


# ---- parts ---------------------------------------------------------------------------------------------------------
def arc_samples(u, v, a0, a1, width, r_ref=R_REF, ds=2.0):
    """strap on the great circle u -> v between arc angles a0 .. a1 (rad): sample dirs (ns*nc, 3), centreline (nl, 3),
    along-index per sample, arc angle per sample"""
    nrm = unit(np.cross(u, v)); e2 = unit(np.cross(nrm, u)); ang = max(a1 - a0, 1e-6)
    ns = max(3, int(ang * r_ref / ds) + 1); th = np.linspace(a0, a1, ns)
    C = np.cos(th)[:, None] * u + np.sin(th)[:, None] * e2
    cs = np.arange(-width / 2, width / 2 + 1e-6, 2.0) / r_ref
    S = unit(C[:, None, :] * np.cos(cs)[None, :, None] + nrm[None, None, :] * np.sin(cs)[None, :, None])
    nl = max(3, int(ang * 85.0 / 2.0) + 1); thl = np.linspace(a0, a1, nl)
    CL = np.cos(thl)[:, None] * u + np.sin(thl)[:, None] * e2
    return S.reshape(-1, 3), CL, np.repeat(th, len(cs))


def disc_samples(c, beta, r_ref=R_REF, step=2.5):
    rad = beta * r_ref; g = np.arange(-rad, rad + 1e-6, step); g = g - g.mean()
    X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad ** 2 + 1e-9
    if keep.sum() == 0: keep = (X == X.flat[np.argmin(np.abs(X) + np.abs(Y))]) & (Y == Y.flat[np.argmin(np.abs(X) + np.abs(Y))])
    X, Y = X[keep] / r_ref, Y[keep] / r_ref
    a = unit(np.cross(c, [0.0, 0.0, 1.0])); b = np.cross(c, a)
    return unit(c[None] + X[:, None] * a[None] + Y[:, None] * b[None])


def ang(u, v): return float(np.arccos(np.clip(np.dot(u, v), -1, 1)))


def build_parts(P, e0, prm):
    """parts in the reference config (scapula coords): dict name -> body, samples, centreline, half-width (mm),
    kind, and for straps the arc angle of each sample from each end and the attached disc names"""
    w = prm["width"]; parts = {}
    for k in range(3):
        parts[f"A{k + 1}"] = dict(body=k, kind="disc", S=disc_samples(P[k]["cA"], P[k]["bA"]), CL=P[k]["cA"][None],
                                  hw=prm["rho"], beta=P[k]["bA"])
        parts[f"B{k + 1}"] = dict(body=k + 1, kind="disc", S=disc_samples(P[k]["cB"], P[k]["bB"]), CL=P[k]["cB"][None],
                                  hw=prm["ratio"] * prm["rho"], beta=P[k]["bB"])
    # base stub on -n1 from disc A1's rim
    u = P[0]["cA"]; v = unit(u * math.cos(0.3) - P[0]["n"] * math.sin(0.3))
    a0 = P[0]["bA"]; a1 = a0 + prm["stub"] / 85.0
    S, CL, th = arc_samples(u, v, a0, a1, w)
    parts["stub"] = dict(body=0, kind="strap", S=S, CL=CL, hw=w / 2, th=th, ends=(("A1", a0), (None, a1)))
    for k, (da, db) in enumerate((("B1", "A2"), ("B2", "A3"))):
        u, v = parts[da]["CL"][0], parts[db]["CL"][0]; L = ang(u, v)
        a0, a1 = parts[da]["beta"], L - parts[db]["beta"]
        S, CL, th = arc_samples(u, v, a0, a1, w)
        parts[f"S{k + 1}"] = dict(body=k + 1, kind="strap", S=S, CL=CL, hw=w / 2, th=th, ends=((da, a0), (db, a1)))
    u = parts["B3"]["CL"][0]; L = ang(u, e0); a0 = parts["B3"]["beta"]
    S, CL, th = arc_samples(u, e0, a0, max(L, a0 + 0.05), w)
    parts["neck"] = dict(body=3, kind="strap", S=S, CL=CL, hw=w / 2, th=th, ends=(("B3", a0), (None, L)))
    return parts


def collisions(parts, Bd, prm, r_conv=85.0):
    """(n,) bool: some pair of parts on different bodies (rolling partners excepted) closer than part_clear"""
    names = list(parts); n = len(Bd); bad = np.zeros(n, bool); worst = {}
    posed = {nm: np.einsum("nij,kj->nki", Bd[:, parts[nm]["body"]], parts[nm]["CL"]) for nm in names}
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            pa, pb = parts[a], parts[b_]
            if pa["body"] == pb["body"]: continue
            if a[0] in "AB" and b_[0] in "AB" and a[1] == b_[1]: continue          # rolling partners
            dots = np.einsum("nki,nli->nkl", posed[a], posed[b_])
            d = np.arccos(np.clip(dots.max(axis=(1, 2)), -1, 1)) * r_conv - pa["hw"] - pb["hw"]
            hit = d < prm["part_clear"]; bad |= hit
            if hit.any(): worst[f"{a}-{b_}"] = int(hit.sum())
    return bad, worst


# ---- the model -----------------------------------------------------------------------------------------------------
class Model:
    def __init__(self, B, log=print):
        self.B = B; self.D = Data(B); self.log = log; self._ref = {}; self._F = {}
        self.RSb = self.D.RS[self.D.bk]

    def ref(self, seed, sing):
        if (seed, sing) not in self._ref: self._ref[(seed, sing)] = ref_chain(seed, self.D, sing)
        return self._ref[(seed, sing)]

    def faces(self, seed, sing, rho, clear, pct=95):
        """F_k: skin-face radius estimate of each joint (pct-percentile of the outermost skin radius over a rho disc on
        the 3R axis over the valid bench poses, + clear)"""
        key = (seed, sing, rho, clear)
        if key not in self._F:
            rf = self.ref(seed, sing); D = self.D; ok = rf["ok"][D.bk]
            dq = rf["dq"][D.bk]; m = rf["m"]
            T1 = rotm(m[0], dq[:, 0]); T2 = T1 @ rotm(m[1], dq[:, 1])
            ax = [np.broadcast_to(m[0], (len(dq), 3)), T1 @ m[1], T2 @ m[2]]
            F = []
            for k in range(3):
                rr = []
                for i in np.nonzero(ok)[0]:
                    d = disc_samples(ax[k][i], rho / 85.0)
                    rr.append(BL.skin_radius(self.B, int(i), d @ self.RSb[i].T).max())
                F.append(float(np.percentile(rr, pct)) + clear)
            self._F[key] = F; self.log(f"  faces {seed} rho {rho}: F = {np.round(F, 1)}")
        return self._F[key]

    def kin(self, prm):
        """kinematic validity on every K pose and the posed body rotations"""
        rf = self.ref(prm["seed"], prm["sing_deg"]); F = self.faces(prm["seed"], prm["sing_deg"], prm["rho"], prm["clear"])
        P, e0 = pair_axes(rf["m"], rf["Q0"], prm, F)
        cs = np.array([p["c"] for p in P]); seed = rf["dq"] / (1 + cs)[None]
        psi, Bd, res, J = ik(P, rf["Q0"], self.D.HG, seed)
        ok3 = rf["ok"]; conv = res < 1e-6
        rng = np.all(np.abs(psi) <= prm["psi_max"] * D2R, 1); br = np.all(np.abs(psi - seed) < 20 * D2R, 1)
        parts = build_parts(P, e0, prm)
        col, worst = collisions(parts, Bd, prm)
        kin_ok = ok3 & conv & rng & br & ~col
        return dict(P=P, e0=e0, F=F, psi=psi, Bd=Bd, res=res, parts=parts, ok3=ok3, conv=conv, rng=rng, br=br, col=col,
                    worst=worst, kin_ok=kin_ok, span=rf["span"])

    def taken_kin(self, K):
        """bench pose -> kinematically taken (clip frames: the whole segment since the previous bench frame)"""
        D = self.D; out = np.zeros(len(D.bk), bool); flips = 0
        for j, row in enumerate(D.bk):
            if self.B.kind[j] == "ws": out[j] = K["kin_ok"][row]; continue
            seg = D.seg[j]; ok = bool(K["kin_ok"][seg[1:]].all()) if len(seg) > 1 else bool(K["kin_ok"][row])
            if ok and len(seg) > 1:
                ps = K["psi"][seg]; okp = K["kin_ok"][seg]
                st = np.abs(np.diff(ps, axis=0)).max(1) > 20 * D2R; st &= okp[:-1]
                if st.any(): ok = False; flips += 1
            out[j] = ok
        return out, flips

    def evaluate(self, prm, pcts=PCTS):
        t0 = time.time(); K = self.kin(prm); B = self.B; D = self.D
        tk, flips = self.taken_kin(K)
        parts = K["parts"]; names = list(parts)
        Bb = K["Bd"][D.bk]                                              # (nb, 4, 3, 3)
        dirs = {nm: np.einsum("nij,kj->nki", self.RSb @ Bb[:, parts[nm]["body"]], parts[nm]["S"]) for nm in names}
        valid = np.nonzero(tk)[0]
        R = {nm: np.zeros(dirs[nm].shape[:2]) for nm in names}
        for i in valid:
            allD = np.concatenate([dirs[nm][i] for nm in names]); rr = BL.skin_radius(B, int(i), allD); o = 0
            for nm in names:
                k = dirs[nm].shape[1]; R[nm][i] = rr[o:o + k]; o += k
        rows = []
        for p in pcts:
            prof = self.profile(R, valid, parts, p, prm)
            B.reset()
            for i in range(len(D.bk)):
                if not tk[i]: B.record(i, None); continue
                B.record(i, np.concatenate([dirs[nm][i] * prof[nm][:, None] for nm in names]))
            r = B.report(); r["pct"] = p; rows.append(r)
        nb = len(D.bk); lost = dict(sing=int((~K["ok3"][D.bk]).sum()), ik=int((K["ok3"] & ~K["conv"])[D.bk].sum()),
                                   range=int((K["ok3"] & K["conv"] & ~K["rng"])[D.bk].sum()),
                                   collision=int((K["ok3"] & K["conv"] & K["rng"] & K["col"])[D.bk].sum()),
                                   segment=int((K["kin_ok"][D.bk] & ~tk).sum()), flips=flips, n=nb)
        extra = dict(F=[round(f, 1) for f in K["F"]], span_deg=[round(s / D2R, 1) for s in K["span"]], lost=lost,
                     worst={k: v for k, v in sorted(K["worst"].items(), key=lambda x: -x[1])[:5]},
                     psi_absmax_deg=[round(float(np.abs(K["psi"][K["kin_ok"], k]).max()) / D2R, 1) if K["kin_ok"].any() else None for k in range(3)],
                     n_pts=int(sum(parts[nm]["S"].shape[0] for nm in names)), sec=round(time.time() - t0, 1))
        return rows, extra, K, R, valid

    @staticmethod
    def profile(R, valid, parts, p, prm):
        prof = {nm: np.percentile(R[nm][valid], p, axis=0) + prm["clear"] if len(valid) else np.full(R[nm].shape[1], 80.0)
                for nm in parts}
        for k in range(1, 4):                                         # flat discs, both partners at one face radius
            f = max(prof[f"A{k}"].max(), prof[f"B{k}"].max()); prof[f"A{k}"][:] = f; prof[f"B{k}"][:] = f
        for nm, pt in parts.items():                                  # strap rows near a disc sit at least at its face
            if pt["kind"] != "strap": continue
            for dn, a in pt["ends"]:
                if dn is None: continue
                near = np.abs(pt["th"] - a) * 85.0 <= prm["end_mm"]
                prof[nm][near] = np.maximum(prof[nm][near], prof[dn][0])
        return prof


def best_of(rows):
    return min(rows, key=lambda r: r["gap"])


# ---- CLI -----------------------------------------------------------------------------------------------------------
def check(n_clip=20, n_ws=40):
    B = CB.Bench(n_clip, n_ws); M = Model(B); prm = dict(PARAMS)
    print("bench", B.mode, len(B.idx), "poses; K", len(M.D.K))
    rf = M.ref(prm["seed"], prm["sing_deg"])
    print("3R joint spans (deg):", np.round(rf["span"] / D2R, 1), "valid", rf["ok"].mean().round(3))
    K = M.kin(prm)
    print("F", np.round(K["F"], 1), "beta", [round(p["bA"] / D2R, 2) for p in K["P"]])
    print("IK conv", K["conv"][K["ok3"]].mean().round(4), "max res", K["res"][K["ok3"]].max(), "range ok", K["rng"][K["ok3"]].mean().round(3),
          "branch ok", K["br"][K["ok3"]].mean().round(3), "collision", K["col"][K["ok3"]].mean().round(3), K["worst"])
    print("psi range (deg):", [np.round(np.percentile(K["psi"][K["ok3"], k] / D2R, [0, 50, 100]), 1).tolist() for k in range(3)])
    # numeric check of the rolling: contact point of A and B stays on both cones; the relative motion of each pair
    for k in range(3):
        p = K["P"][k]; i = int(np.nonzero(K["kin_ok"])[0][5]); Bd = K["Bd"][i]
        cA = Bd[k] @ p["cA"]; cB = Bd[k + 1] @ p["cB"]
        print(f"  J{k + 1}: angle(cA, cB) = {math.degrees(ang(cA, cB)):.3f} (bA + bB = {math.degrees(p['bA'] + p['bB']):.3f})")
    # rolling without slip: the instantaneous relative rotation axis of each pair is its contact generator
    for k in range(3):
        p = K["P"][k]; ps = 0.7; h = 1e-6
        Rr = lambda x: rotm(p["cA"], x) @ rotm(p["cB"], p["c"] * x)
        W = (Rr(ps + h) - Rr(ps - h)) / (2 * h) @ Rr(ps).T; w = unit(np.array([W[2, 1], W[0, 2], W[1, 0]]))
        g = rotm(p["cA"], ps) @ unit(math.sin(p["bB"]) * p["cA"] + math.sin(p["bA"]) * p["cB"])
        print(f"  no-slip J{k + 1}: angle(instant axis, contact generator) at psi 40 deg = {math.degrees(ang(w, g)):.2e} deg")
    rows, extra, K, R, valid = M.evaluate(prm)
    for r in rows: print(r)
    print(extra)
    # named poses
    po = B.poses; el = np.array([p["elev"] for p in po]); pl = np.array([p["plane"] for p in po])
    for nm, j in (("rest", int(np.argmin(el))), ("overhead", int(np.argmax(el))),
                  ("across body", int(np.argmax(np.where(el > 60, pl, -1e9)))), ("behind back", int(np.argmin(pl)))):
        row = M.D.bk[j]
        print(f"  {nm:12s} bench {j:3d} pose {dict((k, round(v)) for k, v in po[j].items())} kin_ok {bool(K['kin_ok'][row])} "
              f"psi {np.round(K['psi'][row] / D2R, 1)} col {bool(K['col'][row])}")


def run_sweep(n_clip=60, n_ws=160):
    B = CB.Bench(n_clip, n_ws); M = Model(B); log = print
    log(f"bench {B.mode} {len(B.idx)} poses, K {len(M.D.K)}")
    sw_path = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
    out = json.load(open(sw_path)) if os.path.exists(sw_path) and "--resume" in sys.argv else []
    done = {json.dumps(e["params_in"], sort_keys=True) for e in out if "params_in" in e}

    def ev(prm):
        key = json.dumps(prm, sort_keys=True)
        if key in done: return [e for e in out if json.dumps(e.get("params_in"), sort_keys=True) == key][0]
        rows, extra, K, R, valid = M.evaluate(prm); b = best_of(rows)
        e = dict(k=len(out), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=dict(prm, pct=b["pct"]), params_in=prm,
                 inband14=b["inband14"], inband10=b["inband10"], reach=b["reach"], follow=b["follow"], contact=b["contact"], gap=b["gap"],
                 by_pct=[dict(pct=r["pct"], gap=r["gap"], reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r["inband10"],
                              contact=r["contact"]) for r in rows], extra=extra, mode=B.mode)
        out.append(e); done.add(key)
        json.dump(out, open(sw_path, "w"), indent=1)
        log(f"[{e['k']:3d}] gap {e['gap']:6.2f} reach {e['reach']:.3f} follow {e['follow']:.3f} in14 {e['inband14']:.3f} "
            f"in10 {e['inband10']:.3f} cont {e['contact']:.3f} p{b['pct']} | {extra['lost']} {extra['sec']}s | "
            + " ".join(f"{k}={prm[k]}" for k in ("seed", "rho", "ratio", "psi_max", "n1", "n2", "n3", "width") if k in prm))
        return e

    base = dict(PARAMS)
    # stage 1: seed chain x pair orientation (coarse), equal cones rho 7
    best = None
    for seed in ("champ", "final"):
        for n1 in (-60, 0, 60):
            for n2 in (-60, 0, 60):
                for n3 in (-60, 0, 60):
                    e = ev(dict(base, seed=seed, n1=n1, n2=n2, n3=n3))
                    if best is None or e["gap"] < best["gap"]: best = e
    # stage 2: refine pair orientation around the best, one joint at a time
    for rnd in range(2):
        for k in ("n1", "n2", "n3"):
            for d in ((-30, -15, 15, 30) if rnd == 0 else (-8, 8)):
                prm = dict(best["params_in"]); prm[k] = prm[k] + d
                e = ev(prm)
                if e["gap"] < best["gap"]: best = e
    # stage 3: disc size, rolling ratio, psi limit, strap width
    for k, vals in (("rho", (5.0, 6.0, 8.0, 10.0)), ("ratio", (0.7, 0.85, 1.2, 1.4)), ("psi_max", (70.0, 78.0, 90.0, 95.0)),
                    ("width", (6.0, 10.0, 14.0)), ("disc_h", (6.0,))):
        for v in vals:
            prm = dict(best["params_in"]); prm[k] = v
            e = ev(prm)
            if e["gap"] < best["gap"]: best = e
    log("BEST", json.dumps({k: best[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "params")}))
    return out, best


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    a = sys.argv[1:]
    if not a or a[0] == "check":
        check(*(int(x) for x in a[1:3])) if len(a) >= 3 else check()
    elif a[0] == "sweep":
        run_sweep(*(int(x) for x in a[1:3] if x.isdigit())) if len(a) >= 3 and a[1].isdigit() else run_sweep()

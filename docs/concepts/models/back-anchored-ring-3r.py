"""Concept model: BACK-ANCHORED RING-ENDED 3R (id back-anchored-ring-3r, docs/concepts/catalogue.json, ideation E).

A spherical 3R (every joint axis through the GH centre) that leaves the top of the shoulder bare:
    scapula handler -> J1 (thin-section RING, axis u1 fixed in the scapula, pointing posterior-medial-down, the ring
    lying on the infraspinous fossa) -> link 1 (strap over the posterior deltoid) -> J2 (O20 v5 hub, axis v placed by
    closure, nominally at the posterolateral acromion corner) -> link 2 (strap down the back of the arm) -> J3 (second
    thin-section RING, axis j3 fixed in the humerus, piercing the lateral / posterolateral arm at s3, th3) -> cuff.
DOF: 3 ACTIVE (J1-J3), 0 PASSIVE. For each arm orientation, v is fixed by the two-cone closure (angle a12 from u,
a23 from w) on the design's branch, and the three joint angles follow. There is no spare coordinate, so nothing can
sag when unpowered.

Model (catalogue model_spec kept, with these departures, each argued in docs/concepts/back-anchored-ring-3r.md):
  * Rings and hubs are FLAT solids normal to their axis at a fitted axial height (a real bearing), not spherical
    annuli at a radius. Housed 4.76-section ring (Reali-Slim KAA): radial width 9 mm (pitch +-4.5), axial stack 8 mm,
    rotating race from +4.8. O20 v5 hub: disc r 10, lower member skin face F, upper member from F + 3.15, crown
    F + 12.25. p = 0 makes a joint an O20 hub, so the sweep can test the spec's rings against hubs (the spec's arm ring
    turns out to sit ~63 deg to the arm's skin, see the doc).
  * Fit (the baseline's percentile rule, true-distance version): every rigid part is traced in from outside along its
    own placement direction (rings / hubs as one flat body along their axis, strap samples along their ray from GH)
    until its samples sit CLEAR = 2.2 mm off the skin. The part's fixed height / profile = the q-th percentile over the
    kinematically valid bench poses (q swept, as tools/concept_baseline.py sweeps its p).
  * Straps 14 x 5.5 Ti (spec). Link 1 runs on the great circle u -> v from the J1 ring's outer rim (at its rotating race,
    h1 + 4.8) to the J2 hub rim (at F2); link 2 from the hub rim (at F2 + 5.65: on the boss, above link 1's full 5.5 mm
    plus the 0.15 running gap; the spec's F + 3.15 assumed 3 mm plates) to the J3 ring's outer rim (h3 + 4.8). A strap
    may leave its joint level at <= 60 deg (spec): profile = max(envelope, joint level - tan60 * distance).
  * Metal sampled on a 2 mm grid (~1 point / 4 mm2). SCORED (skin-facing, as the baseline): ring / hub undersides and
    strap undersides. CONTACT-ONLY: ring tops and inner / outer walls, hub crown and wall, strap tops - any of them
    inside the body is appended to the record, so the bench counts the pose as contact (squeeze included).
  * A pose is TAKEN iff the chain closes on its branch with the baseline's 10 deg fold / stretch margin (tri_ok);
    along each fit clip at its full 10 fps no joint steps > 25 deg between consecutive frames (a flip = a frame not
    followed); no two non-adjacent parts within 1 mm (J1 ring vs J2 hub, link 2, J3 ring; J2 hub vs J3 ring; link 1
    vs J3 ring) and link 1 / link 2 (adjacent at J2) not overlapping outside the hub (0.15 gap); then the bench's
    contact rule (any metal < 0 mm = contact = not taken).
  * Frames: B.frames(i) (body_pose): S-fixed u1 -> Rs u1, arm-fixed j3 -> Rh j3, arm point (s, th, 60) in the rig's
    arm frame (spec). GH does not translate relative to the scapula on the bench (R10 is judged elsewhere).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/back-anchored-ring-3r.py [check|kin|sweep|best|sketch]
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
BP = CB.BP

ID = "back-anchored-ring-3r"
NAME = "Back-anchored ring-ended 3R (top of the shoulder left bare)"
D2R = math.pi / 180
SP = 2.0                                  # sample spacing mm (1 point / 4 mm2)
CLEAR, PART_CLEAR, RUN_GAP = 2.2, 1.0, 0.15
SING, JUMP, RAMP = 10.0, 25.0, 60.0       # fold / stretch margin (deg, baseline tri_ok), largest joint step / frame, strap ramp
RING_W, RING_H, RING_SPLIT = 9.0, 8.0, 4.8       # housed 4.76-section thin ring
HUB_R, HUB_UP, HUB_CROWN = 10.0, 3.15, 12.25     # O20 v5
T0S = (225.0, 170.0, 120.0)               # tracing starts (mm from GH); a group starting inside the body retries lower
KAA = dict(KAA15=21.4, KAA17=24.6, KAA20=27.9, KAA25=34.1)   # pitch radii (mm) of 4.76-section Reali-Slim rings

PARAMS = dict(lat1=-10.0, lon1=-120.0, p1=27.9, a12=90.0, a23=90.0, s3=120.0, th3=40.0, p3=27.9, br=1, q=98.0, width=14.0, t_link=5.5)
SWEEP = dict(lat1=[-25, -15, -10, -5, 0, 5], lon1=[-130, -120, -110, -100, -90], p1=[0, 21.4, 24.6, 27.9], a12=[70, 80, 90, 100, 110],
             a23=[70, 80, 90, 100, 110], s3=[100, 120, 140, 160], th3=[-20, 0, 20, 40, 60], p3=[0, 21.4, 24.6, 27.9], br=[-1, 1],
             q=[90, 95, 98, 100])


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def sdir(lat, lon):
    la, lo = lat * D2R, lon * D2R
    return np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)])


_AF = None
def arm_frame():
    """(a humerus axis, z lateral, y posterior) in the rig's humerus-local frame (spec)"""
    global _AF
    if _AF is None:
        L = BP._rig().L; a = unit(np.array(L["elbow"], float)); z = np.array(L["rest_humerus"], float) @ np.array([0.0, 0.0, 1.0])
        z = unit(z - (z @ a) * a); _AF = (a, z, np.cross(a, z))
    return _AF


def arm_point(s, th, rho=60.0):
    a, z, y = arm_frame(); t = th * D2R
    return s * a + rho * (math.cos(t) * z + math.sin(t) * y)


def perp_basis(P):
    a = np.where(np.abs(P[..., 2:3]) < 0.9, np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0]))
    q1 = unit(np.cross(P, a)); return q1, np.cross(P, q1)


# ---- frames -------------------------------------------------------------------------------------------------------
_ZF = None
def all_frames():
    """RS, RH (body_pose frames) for every row of the pose file: RH = RS @ HG @ rest_humerus^T (checked = B.frames H)"""
    global _ZF
    if _ZF is None:
        Z = CB._poses_all(); RS = Z["RS"].astype(float); RH = RS @ Z["HG"].astype(float) @ np.array(BP._rig().L["rest_humerus"], float).T
        _ZF = (Z, RS, RH)
    return _ZF


# ---- kinematics ---------------------------------------------------------------------------------------------------
def kin(prm, RS, RH):
    """u, v, w (n, 3), ok (closure + 10 deg fold/stretch margin), serial margin (deg), joint angles q (n, 3) rad"""
    u1 = sdir(prm["lat1"], prm["lon1"]); j3 = unit(arm_point(prm["s3"], prm["th3"]))
    al, ga = prm["a12"] * D2R, prm["a23"] * D2R
    u = RS @ u1; w = RH @ j3; k = (u * w).sum(-1); D = 1 - k ** 2; Ds = np.where(D < 1e-9, 1e-9, D)
    x = (math.cos(al) - k * math.cos(ga)) / Ds; y = (math.cos(ga) - k * math.cos(al)) / Ds
    z2 = (1 - x ** 2 - y ** 2 - 2 * x * y * k) / Ds
    v = unit(x[:, None] * u + y[:, None] * w + prm["br"] * np.sqrt(np.clip(z2, 0, None))[:, None] * np.cross(u, w))
    th = np.degrees(np.arccos(np.clip(k, -1, 1)))
    lo = abs(prm["a12"] - prm["a23"]) + SING; hi = min(prm["a12"] + prm["a23"], 360 - prm["a12"] - prm["a23"]) - SING
    ok = (D > 1e-6) & (z2 > 0) & (th >= lo) & (th <= hi)
    marg = np.degrees(np.arcsin(np.clip(np.abs((u * np.cross(v, w)).sum(-1)) / math.sin(ga), 0, 1)))

    def ang(ax, a, c):
        a_ = a - (a * ax).sum(-1, keepdims=True) * ax; c_ = c - (c * ax).sum(-1, keepdims=True) * ax
        return np.arctan2((np.cross(a_, c_) * ax).sum(-1), (a_ * c_).sum(-1))
    r1 = RS @ unit(np.cross(u1, [0.3, 0.9, 0.1])); r3 = RH @ unit(np.cross(j3, [0.2, 0.1, 0.95]))
    q = np.stack([ang(u, r1, v), ang(v, u, w), ang(w, r3, v)], 1)
    return u, v, w, ok, marg, q


def continuity(prm, idx):
    """fit clips at their full 10 fps: a frame is not followed if a joint steps > JUMP from the previous (kinematically
    taken) frame. Returns a bool per bench index (True for workspace poses), and the number of flips."""
    Z, RS, RH = all_frames(); names = list(Z["NAMES"]); cid = Z["CID"]; good = {}; flips = 0
    for nm in CB.FIT:
        ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        _, _, _, ok, _, q = kin(prm, RS[ii], RH[ii]); prev = None
        for j, gi in enumerate(ii):
            g = bool(ok[j])
            if g and prev is not None:
                dq = np.degrees(np.abs((q[j] - q[prev] + np.pi) % (2 * np.pi) - np.pi))
                if dq.max() > JUMP: g = False; flips += 1
            good[int(gi)] = g; prev = j if ok[j] else None
    return np.array([good.get(int(g), True) for g in idx]), flips


# ---- part geometry (local) ----------------------------------------------------------------------------------------
def joint_geo(p):
    """(ri, ro, stack, link level) of a joint: a housed thin ring of pitch radius p, or the O20 v5 hub (p = 0)"""
    if p <= 0: return 0.0, HUB_R, HUB_CROWN, HUB_UP
    return p - RING_W / 2, p + RING_W / 2, RING_H, RING_SPLIT


def annulus(ri, ro):
    """(rho, psi) samples of a flat annulus / disc on a 2 mm grid"""
    if ri <= 0:
        g = np.arange(-ro + SP / 2, ro, SP); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= ro ** 2
        return np.hypot(X[k], Y[k]), np.arctan2(Y[k], X[k])
    n = max(1, int(round((ro - ri) / SP))); rr, pp = [], []
    for j in range(n):
        r = ri + (j + 0.5) * (ro - ri) / n; m = max(6, int(math.ceil(2 * math.pi * r / SP)))
        rr += [r] * m; pp += list(2 * math.pi * (np.arange(m) + 0.5) / m)
    return np.array(rr), np.array(pp)


def wall(r, h):
    m = max(6, int(math.ceil(2 * math.pi * r / SP))); zz = np.linspace(0, h, max(2, int(math.ceil(h / SP)) + 1))
    P, Zz = np.meshgrid(2 * math.pi * (np.arange(m) + 0.5) / m, zz); return np.full(P.size, r), P.ravel(), Zz.ravel()


def joint_samples(p):
    """local samples of a joint: scored underside (rho, psi, z) and contact-only (top, walls)"""
    ri, ro, h, _ = joint_geo(p); r, ps = annulus(ri, ro); und = (r, ps, np.zeros_like(r))
    top = (r, ps, np.full_like(r, h)); ws = [wall(ro, h)] + ([wall(ri, h)] if ri > 0 else [])
    co = tuple(np.concatenate([x[k] for x in [top] + ws]) for k in range(3))
    return und, co


def place(ax, loc, h):
    """local (rho, psi, z) about axis ax (3,) at underside height h -> (k, 3)"""
    q1, q2 = perp_basis(ax[None]); q1, q2 = q1[0], q2[0]; r, ps, z = loc
    return (h + z)[:, None] * ax + (r * np.cos(ps))[:, None] * q1 + (r * np.sin(ps))[:, None] * q2


# ---- tracing ------------------------------------------------------------------------------------------------------
def trace(B, i, base, dirs, gid, ng, t0s=T0S, target=CLEAR, iters=60, tol=0.05):
    """group sphere tracing: points X = base + t_g dirs (sorted by group gid); per group the first t from t0 inward with
    min distance = target. A group starting inside the body (head, trunk, the arm beyond) retries from the next start;
    nan if it starts inside at every start."""
    t_out = np.full(ng, np.nan); todo = np.arange(ng)
    for t0 in t0s:
        if not len(todo): break
        t = np.full(ng, float(t0)); act = np.zeros(ng, bool); act[todo] = True; bad = np.zeros(ng, bool)
        for it in range(iters):
            sel = act[gid]
            if not sel.any(): break
            X = base[sel] + t[gid[sel], None] * dirs[sel]; d = B.dist(i, X); g = gid[sel]
            st = np.r_[0, np.nonzero(np.diff(g))[0] + 1]; m = np.minimum.reduceat(d, st); ga = g[st]; step = m - target
            if it == 0:
                b = step < 0; bad[ga[b]] = True; act[ga[b]] = False; step = np.where(b, 0.0, step)
            t[ga] -= step; done = (np.abs(step) < tol) | (t[ga] < 15.0); act[ga[done]] = False
        good = np.zeros(ng, bool); good[todo] = ~bad[todo]; t_out[good] = t[good]; todo = todo[bad[todo]]
    return t_out


# ---- straps ---------------------------------------------------------------------------------------------------------
def strap_grid(th0, th1, r0, r1, width):
    """centre-line angles th (ns,), across angles g (ns, nc), arc distance from each end (mm) for a strap from angle th0
    (radius r0) to th1 (radius r1) on its great circle"""
    Rm = 0.5 * (r0 + r1); n = max(3, int(math.ceil((th1 - th0) * Rm / SP)))
    th = th0 + (np.arange(n) + 0.5) * (th1 - th0) / n; R = r0 + (r1 - r0) * (th - th0) / max(th1 - th0, 1e-9)
    c = np.arange(-width / 2 + SP / 2, width / 2, SP)
    return th, c[None, :] / R[:, None], (th - th0) * R, (th1 - th) * R, R


def strap_dirs(e0, e1, th, g):
    """directions (P, ns, nc, 3) of strap samples in the frame of (e0 start axis, e1 end axis) per pose"""
    en = unit(np.cross(e0, e1)); et = np.cross(en, e0)
    C = np.cos(th)[None, :, None] * e0[:, None] + np.sin(th)[None, :, None] * et[:, None]
    return unit(C[:, :, None, :] * np.cos(g)[None, :, :, None] + en[:, None, None, :] * np.sin(g)[None, :, :, None])


def strap_local(X, e0, e1):
    """(theta along, gamma across, r) of points X (k, 3) in a strap frame"""
    en = unit(np.cross(e0, e1)); et = np.cross(en, e0); r = np.linalg.norm(X, axis=1); d = X / r[:, None]
    return np.arctan2(d @ et, d @ e0), np.arcsin(np.clip(d @ en, -1, 1)), r


# ---- the model ----------------------------------------------------------------------------------------------------
class Model:
    """kinematics + fitted part shapes of one configuration on one bench"""
    def __init__(self, B, prm, cache=None, log=None):
        self.B = B; self.p = prm = dict(PARAMS, **prm); n = len(B.idx); cache = cache if cache is not None else {}
        Z, RSa, RHa = all_frames(); RS = RSa[B.idx]; RH = RHa[B.idx]
        self.u, self.v, self.w, self.ok_kin, self.marg, self.q = kin(prm, RS, RH)
        self.cont, self.flips = continuity(prm, B.idx); self.ok = self.ok_kin & self.cont; ok = np.nonzero(self.ok)[0]
        self.g = [joint_geo(prm["p1"]), joint_geo(0.0), joint_geo(prm["p3"])]
        self.js = [joint_samples(prm["p1"]), joint_samples(0.0), joint_samples(prm["p3"])]
        axes = [self.u, self.v, self.w]
        # pass 1: joints (J1 and J3 needs depend only on their own axis and size: cached across configurations)
        keys = [("J1", prm["lat1"], prm["lon1"], prm["p1"]), ("J2",) + tuple(sorted(prm.items())), ("J3", prm["s3"], prm["th3"], prm["p3"])]
        self.need = np.full((n, 3), np.nan)
        for k in range(3):
            ck = cache.get(keys[k], {})
            for i in ok:
                if i not in ck:
                    und = self.js[k][0]; base = place(axes[k][i], und, 0.0); dirs = np.broadcast_to(axes[k][i], base.shape)
                    ck[i] = trace(B, int(i), base, dirs, np.zeros(len(base), int), 1)[0]
                self.need[i, k] = ck[i]
            cache[keys[k]] = ck
        q = prm["q"]
        nd = np.where(np.isnan(self.need[ok]), T0S[0], self.need[ok])
        self.h = np.percentile(nd, q, axis=0) if len(ok) else np.full(3, T0S[0])
        h1, F2, h3 = self.h; (ri1, ro1, H1, S1), _, (ri3, ro3, H3, S3) = self.g
        up2 = prm["t_link"] + RUN_GAP
        # strap ends: link 1 from the J1 outer rim at its rotating race to the J2 hub rim at F2; link 2 from the hub rim
        # at F2 + up2 to the J3 outer rim at its rotating race
        a12, a23 = prm["a12"] * D2R, prm["a23"] * D2R
        e = dict(L1=(math.atan2(ro1, h1 + S1), a12 - math.atan2(HUB_R, F2), math.hypot(h1 + S1, ro1), math.hypot(F2, HUB_R)),
                 L2=(math.atan2(HUB_R, F2 + up2), a23 - math.atan2(ro3, h3 + S3), math.hypot(F2 + up2, HUB_R), math.hypot(h3 + S3, ro3)))
        self.S = {}
        for nm, (th0, th1, r0, r1) in e.items():
            if th1 - th0 < 2 * SP / max(r0, r1):
                self.S[nm] = None; continue
            th, gm, d0, d1, R = strap_grid(th0, th1, r0, r1, prm["width"])
            self.S[nm] = dict(th=th, g=gm, d0=d0, d1=d1, r0=r0, r1=r1, th0=th0, th1=th1, R=R,
                              e=(self.u, self.v) if nm == "L1" else (self.v, self.w))
        # pass 2: strap envelopes (per sample: the q-th percentile of the radius where it sits CLEAR off the skin)
        for nm, s in self.S.items():
            if s is None: continue
            D = strap_dirs(s["e"][0], s["e"][1], s["th"], s["g"]); s["D"] = D
            need = np.full(D.shape[:3], np.nan)
            for i in ok:
                Di = D[i].reshape(-1, 3)
                need[i] = trace(B, int(i), np.zeros_like(Di), Di, np.arange(len(Di)), len(Di)).reshape(D.shape[1:3])
            nd = np.where(np.isnan(need[ok]), T0S[0], need[ok])
            env = np.percentile(nd, q, axis=0) if len(ok) else np.full(D.shape[1:3], T0S[0])
            kr = math.tan(RAMP * D2R)
            prof = np.maximum(env, (s["r0"] - kr * s["d0"])[:, None]); prof = np.maximum(prof, (s["r1"] - kr * s["d1"])[:, None])
            s["env"] = env; s["prof"] = prof
        self.cache = cache

    # ---- per pose ---------------------------------------------------------------------------------------------------
    def parts(self, i):
        """per part: (scored underside points, contact-only points) in the thorax frame for pose i"""
        axes = [self.u[i], self.v[i], self.w[i]]; out = {}
        for k, nm in enumerate(("J1", "J2", "J3")):
            und, co = self.js[k]; out[nm] = (place(axes[k], und, self.h[k]), place(axes[k], co, self.h[k]))
        t = self.p["t_link"]
        for nm, s in self.S.items():
            if s is None: continue
            D = s["D"][i]; out[nm] = ((s["prof"][..., None] * D).reshape(-1, 3), ((s["prof"] + t)[..., None] * D).reshape(-1, 3))
        return out

    def solids(self, i):
        """analytic solids: joints as (axis, z0, z1, rho0, rho1), straps as (e0, e1, th0, th1, half-width mm, prof grid)"""
        axes = [self.u[i], self.v[i], self.w[i]]; J = {}
        for k, nm in enumerate(("J1", "J2", "J3")):
            ri, ro, h, _ = self.g[k]; J[nm] = (axes[k], self.h[k], self.h[k] + h, ri, ro)
        return J

    def in_joint(self, X, sol, m):
        ax, z0, z1, r0, r1 = sol; z = X @ ax; rr = np.linalg.norm(X - z[:, None] * ax, axis=1)
        return (z >= z0 - m) & (z <= z1 + m) & (rr >= r0 - m) & (rr <= r1 + m)

    def in_strap(self, X, nm, i, m):
        s = self.S[nm]; e0, e1 = s["e"][0][i], s["e"][1][i]; th, gm, r = strap_local(X, e0, e1)
        R = np.interp(th, s["th"], s["R"]); hw = self.p["width"] / 2
        inside = (th >= s["th0"] - m / R) & (th <= s["th1"] + m / R) & (np.abs(gm) * R <= hw + m)
        if not inside.any(): return inside
        a = np.clip(np.searchsorted(s["th"], th) , 0, len(s["th"]) - 1)
        c = np.arange(-hw + SP / 2, hw, SP); b = np.clip(np.round((gm * R - c[0]) / SP).astype(int), 0, len(c) - 1)
        lo = s["prof"][a, b]
        return inside & (r >= lo - m) & (r <= lo + self.p["t_link"] + m)

    def collide(self, i, P):
        """self-collision in pose i (P = parts(i)): which pair, or None"""
        J = self.solids(i); allp = {nm: np.concatenate(v) for nm, v in P.items()}
        def mid(nm):
            if nm not in self.S or self.S[nm] is None: return allp[nm]
            a, b = P[nm]; return np.concatenate([a, b, 0.5 * (a + b)])
        for a, b in (("J1", "J2"), ("J1", "J3"), ("J2", "J3")):
            if self.in_joint(allp[a], J[b], PART_CLEAR).any() or self.in_joint(allp[b], J[a], PART_CLEAR).any(): return f"{a}-{b}"
        for jn, sn in (("J1", "L2"), ("J3", "L1")):
            if self.S.get(sn) is None: continue
            if self.in_joint(mid(sn), J[jn], PART_CLEAR).any() or self.in_strap(allp[jn], sn, i, PART_CLEAR).any(): return f"{jn}-{sn}"
        if self.S.get("L1") is not None and self.S.get("L2") is not None:
            X = mid("L2"); ax = self.v[i]; z = X @ ax; rr = np.linalg.norm(X - z[:, None] * ax, axis=1)
            X = X[rr > HUB_R + 0.5]
            if len(X) and self.in_strap(X, "L1", i, RUN_GAP).any(): return "L1-L2"
        return None

    def metal(self, i, details=False):
        """(points to record or None, info)"""
        if not self.ok[i]: return None, "kin" if not self.ok_kin[i] else "flip"
        P = self.parts(i); c = self.collide(i, P)
        if c: return None, "self " + c
        sc = np.concatenate([v[0] for v in P.values()]); co = np.concatenate([v[1] for v in P.values()])
        dc = self.B.dist(i, co); bad = co[dc < 0]
        info = "ok"
        if len(bad):
            info = "top/wall in body: " + ",".join(nm for nm, v in P.items() if (self.B.dist(i, v[1]) < 0).any())
        return (np.concatenate([sc, bad]) if len(bad) else sc), info


def evaluate(B, prm, cache=None, details=False):
    M = Model(B, prm, cache)
    B.reset(); why = {}; per = {}
    for i in range(len(B.idx)):
        X, info = M.metal(i); d = B.record(i, X)
        if X is not None and d is not None and d.min() < 0 and info == "ok": info = "underside in body"
        why[info.split(":")[0]] = why.get(info.split(":")[0], 0) + 1; per[i] = info
    r = B.report()
    ok = M.ok_kin
    r.update(margin_p5=round(float(np.percentile(M.marg[ok], 5)), 1) if ok.any() else None,
             margin_min=round(float(M.marg[ok].min()), 1) if ok.any() else None, flips=M.flips,
             kin_ws=round(float(np.mean([M.ok[j] for j, k in enumerate(B.kind) if k == "ws"])), 4),
             kin_clip=round(float(np.mean([M.ok[j] for j, k in enumerate(B.kind) if k == "clip"])), 4),
             h=[round(float(x), 1) for x in M.h], why=why,
             squeeze=round(float(np.mean([("J2" in per[i] or "L2" in per[i]) and "body" in per[i] for i in range(len(B.idx)) if M.ok[i]])), 4) if M.ok.any() else None)
    if details: return r, M, per
    return r


# ---- bench helpers ------------------------------------------------------------------------------------------------
def bench(n_clip=60, n_ws=160):
    return CB.Bench(n_clip=n_clip, n_ws=n_ws)


SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
def plog(*a): print(*a, flush=True)


class Runner:
    def __init__(self, B, fresh=False):
        self.B = B; self.cache = {}
        self.entries = json.load(open(SWEEP_JSON)) if (not fresh and os.path.exists(SWEEP_JSON)) else []
        self.done = {json.dumps(e["params"], sort_keys=True): e for e in self.entries}

    def run(self, over, tag=""):
        prm = dict(PARAMS, **over); key = json.dumps(prm, sort_keys=True)
        if key in self.done: return self.done[key]
        t = time.time(); r = evaluate(self.B, prm, self.cache)
        e = dict(k=len(self.entries), t=now(), params=prm, inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                 follow=r["follow"], contact=r["contact"], gap=r["gap"], margin_p5=r["margin_p5"], flips=r["flips"], h=r["h"],
                 squeeze=r["squeeze"], why=r["why"], kin_ws=r["kin_ws"], kin_clip=r["kin_clip"], tag=tag, secs=round(time.time() - t, 1))
        self.entries.append(e); self.done[key] = e
        os.makedirs(os.path.dirname(SWEEP_JSON), exist_ok=True)
        json.dump(self.entries, open(SWEEP_JSON + ".tmp", "w"), indent=0); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
        plog(f"[{e['k']:3d}] gap {e['gap']:6.2f} reach {e['reach']:.3f} follow {e['follow']:.3f} ib14 {e['inband14']:.3f} ib10 {e['inband10']:.3f} "
             f"contact {e['contact']:.3f} kin {e['kin_ws']:.2f}/{e['kin_clip']:.2f} h {e['h']} {e['why']} {tag} "
             f"{json.dumps({k: v for k, v in over.items()})} ({e['secs']} s)")
        return e

    def best(self, filt=lambda e: True):
        c = [e for e in self.entries if filt(e)]; return min(c, key=lambda e: e["gap"]) if c else None


def kin_screen(B, grid=None, top=15):
    """kinematics only (closure, 10 deg margin, continuity): share of workspace / clip poses the chain can take"""
    rows = []
    g = grid or dict(lat1=SWEEP["lat1"], lon1=SWEEP["lon1"], a12=[70, 90, 110], a23=[70, 90, 110], s3=SWEEP["s3"], th3=SWEEP["th3"], br=[-1, 1])
    import itertools
    ks = list(g); Z, RSa, RHa = all_frames()
    for vals in itertools.product(*[g[k] for k in ks]):
        prm = dict(PARAMS, **dict(zip(ks, vals)))
        u, v, w, ok, marg, q = kin(prm, RSa[B.idx], RHa[B.idx]); cont, fl = continuity(prm, B.idx); okc = ok & cont
        ws = np.array([k == "ws" for k in B.kind])
        rows.append(dict(prm={k: prm[k] for k in ks}, ws=float(okc[ws].mean()), clip=float(okc[~ws].mean()), flips=fl,
                         m5=float(np.percentile(marg[ok], 5)) if ok.any() else 0.0))
    rows.sort(key=lambda r: -(r["ws"] + r["clip"]))
    return rows


def check(B, prm=None):
    prm = dict(PARAMS, **(prm or {})); r, M, per = evaluate(B, prm, details=True)
    plog(json.dumps({k: v for k, v in r.items()}, default=str))
    taken = [i for i in range(len(B.idx)) if M.ok[i]]
    el = np.array([B.poses[i]["elev"] for i in taken]); pl = np.array([B.poses[i]["plane"] for i in taken])
    named = dict(rest=taken[int(np.argmin(el))], overhead=taken[int(np.argmax(el))], across=taken[int(np.argmax(pl))])
    bb = [i for i in taken if B.clip[i] == "Reach back pocket"]
    if bb: named["behind back"] = bb[len(bb) // 2]
    for nm, i in named.items():
        P = M.parts(i)
        s = "  ".join(f"{k}: {np.mean((d >= 2) & (d <= 14)):.2f} [{d.min():.1f},{np.median(d):.1f},{d.max():.1f}]" for k, v in P.items() for d in [B.dist(i, v[0])])
        plog(f"  {nm:12s} {B.poses[i]} {per[i]} | {s}")
    return r, M, per


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    a = sys.argv[1:]; mode = a[0] if a else "check"
    nc = int(a[1]) if len(a) > 1 else 60; nw = int(a[2]) if len(a) > 2 else 160
    if mode == "kin":
        B = bench(nc, nw); rows = kin_screen(B)
        for r in rows[:30]: plog(json.dumps(r))
    elif mode == "check":
        B = bench(nc, nw); plog("bench", B.mode, len(B.idx)); check(B)
    elif mode == "sweep":
        import importlib; B = bench(nc, nw); plog("bench", B.mode, len(B.idx))
        from_sweep = __import__("runpy")
        sw = os.path.join(HERE, "_barr3r_sweep.py")
        from_sweep.run_path(sw, init_globals=dict(M=sys.modules[__name__], B=B))

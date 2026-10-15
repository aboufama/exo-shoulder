"""skin-stretch-scissor: a tapered spherical lazy-tongs from a hub on the scapula top to a hub on the lateral deltoid
(3 ACTIVE DOF: J1 hub, the scissor's span, J3 hub; 3N+2 passive scissor pivots / slots, all set by the scissor's
own mobility 1).

Topology (scapula handler -> user's upper-arm cuff), every pivot axis radial through the GH centre:
    S --J1 (O20 v5 hub, axis b fixed in the scapula frame)--> L1 = J1's upper member (a slotted plate)
      --scissor: N spherical scissor units along the great circle b -> W, root pinned / slotted on L1, tip pinned /
        slotted on L2 (the scissor's one DOF = its angular span ss)-->
    L2 = J3's upper member (a slotted plate) --J3 (O20 v5 hub, axis W = HG W0, fixed in the humerus)--> lower member
      = humerus-fixed disc + BOTTOM stub (14 x 6 mm, 40 mm down the lateral arm) -> cuff (user's part).
DOF: J1 (rotation about b), the scissor (a 1-DOF spherical motion between L1 and L2 that opens the angle b-W) and J3
(rotation about W) = 3 active; the 3N-2 internal pivots and the 4 pin / slot joints at the ends are functions of the
scissor's span (a lazy-tongs has mobility 1), so nothing can sag. A spherical 3R with A1 ~ A2 ~ 90 deg.

SPEC CORRECTION (stated in docs/concepts/skin-stretch-scissor.md): a lazy-tongs held by ONE pin and ONE lateral slot at
each end is a scissor lift: the pinned edge (+u nodes) stays put, but the centreline wanders sideways by (u_ref - u) as
the tongs open (u = the half opening of the end node pair). Held that way the tip plate does not rotate purely about
p2 = b x W (the catalogue's A1 = A2 = 90 deg idealisation); the true relative motion of L2 w.r.t. L1 is
    F(ss) = R_XZ(phi0) R_XY(a) R_XZ(ss) R_XY(-a) R_XZ(phi1),  a = u_ref - u(ss)
(local frame: X = hub axis, Y = lateral, Z = along the scissor) and the closure solves angle(b, W) = g(ss) for ss
(1-D, monotonic), then J1 from the azimuth and J3 from the twist. That is what is modelled (exact, residual checked).
A centred mount (both end nodes in one slot + the first centre pivot in a long slot) needs a ~(dmax-dmin)/2 r long stem
on each plate; the two stems collide overhead, so the spec's pin + slot is kept.

Geometry (idealised, every part at its real size; skin-facing surfaces sampled like tools/concept_baseline.py: straps
every 2 mm along x 2 mm across incl. edges, discs on a 2.5 mm grid, plates on a 2 mm grid):
  * hubs: O20 v5 (docs/HARDWARE.md): lower plate face F at rJ (fitted), lower plate F..F+3, upper boss F+3.15..F+12.25.
  * mode 'over' (spec: scissor root on J1's upper plate at the hub axis): the upper member's plate is a flat slotted
    cap over the boss (underside F+11.75 over the PCB, 3 mm) -> scissor end nodes at F+15.75 (1 mm washer).
    mode 'beside' (improvement): the plate is at the boss level (F+3.15..F+6.15) and the scissor root line sits d0 mm
    from the hub axis along the scissor (clear of the boss + O8 pivot bosses) -> end nodes at F+7.15.
    Plate footprint: the O20 disc + a 10 mm wide lateral bar holding the pin (+u_ref) and the slot (down to u_ref-2u_max)
    + (beside) a 10 mm neck from the boss to the root line.
  * scissor: 2N Ti bars 6 x 2 mm, layer A (+u -> -u) underside at r(f), layer B at r(f) + pitch; O8 pivot bosses
    spanning [r(f), r(f) + 5.5] at every node. Node radius r(f) constant per node (f = fraction along the scissor never
    changes), piecewise linear in f with kpu knots per unit -> every bar is a rigid (bent) part. r(f) fitted like the
    baseline's links: p-th percentile over the kinematically valid bench poses of the smallest radius keeping every bar
    / boss sample >= 2 mm from the skin, and >= 1 mm above the plates where it passes over them; end knots = plate
    top + 1. taper=0: one radius for every node (the spec's 'taper off').
  * stub: humerus-fixed 14 x 6 strap from the J3 disc edge 40 mm toward the elbow, rows fitted to the arm skin.
Taken (bench rules): closure (residual < 0.5 deg), scissor span inside [fold limit, N (lam - 3 deg)] where the fold limit
is analytic (same-layer bars >= 7 mm apart centre to centre = 6 mm bar + 1 mm, O8 bosses >= 9 mm apart, a boss >= 8 mm
from any bar it does not carry), no interference >= 1 mm between non-adjacent parts (J1 member vs J3 member + stub;
scissor vs both members except its own end pins in their slots), every clip frame at 10 fps followed with no joint jump
> 30 deg since the last followed frame. Contact: any skin-facing sample < 0, plus any top / side sample inside.

    python3 docs/concepts/models/skin-stretch-scissor.py check      # a few poses on Bench(20, 40), numbers + reasons
    python3 docs/concepts/models/skin-stretch-scissor.py sweep      # coarse -> refine sweep on Bench(60, 160)
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402

ID = "skin-stretch-scissor"
D2R = math.pi / 180
HUB_R, STACK, CAP, LOW_T = 10.0, 3.15, 12.25, 3.0   # O20 v5 joint (docs/HARDWARE.md)
H_OVER = 11.75                                      # 'over': slotted flat cap underside above F (over the PCB)
PLATE_T = 3.0
BAR_W, BAR_T = 6.0, 2.0                             # Ti scissor bars
BOSS_R, BOSS_H = 4.0, 5.5                           # O8 pivot bosses
STUB_W, STUB_T, STUB_L = 14.0, 6.0, 40.0            # BOTTOM stub
SLOT_W = 10.0                                       # plate's lateral slot bar width
SP, SP_DISC = 2.0, 2.5                              # sample grids (baseline convention)
CLEAR, GAP_PART, FLIP = 2.0, 1.0, 30.0
STRETCH = 3.0                                       # deg: not taken when ss / N > lam - 3
R_EST = 65.0                                        # mm, only for angle <-> mm before the radii are fitted
Y_ARM = np.array([0.0, -1.0, 0.0])

PARAMS = dict(b_az=32.55, b_el=80.56, w_d=71.38, w_az=4.78, N=4, lam=32.0, mode="over", d0=15.0, d1=15.0, kpu=4,
              pitch=2.5, p=95.0, taper=1, u_ref=None)
SWEEP = dict(N=(3, 6), lam=(24, 50), mode=("over", "beside"), b_az=(0, 60), b_el=(65, 90), w_d=(55, 95), w_az=(-20, 30),
             p=(85, 100), pitch=(2.5, 3.0), taper=(0, 1), kpu=(2, 4))


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def wdir(d, az):
    d, a = d * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def _rot(a, kind):
    a = np.asarray(a, float); c, s = np.cos(a), np.sin(a); z = np.zeros_like(c); o = np.ones_like(c)
    if kind == "XZ": rows = ([c, z, -s], [z, o, z], [s, z, c])        # X -> Z by a (about -Y)
    elif kind == "XY": rows = ([c, -s, z], [s, c, z], [z, z, o])      # X -> Y by a (about Z)
    else: rows = ([o, z, z], [z, c, -s], [z, s, c])                   # about X
    return np.stack([np.stack(r, -1) for r in rows], -2)


rXZ = lambda a: _rot(a, "XZ"); rXY = lambda a: _rot(a, "XY"); rX = lambda a: _rot(a, "X")


def ang_about(w, p, q):
    pp = p - (p * w).sum(-1, keepdims=True) * w; qq = q - (q * w).sum(-1, keepdims=True) * w
    return np.arctan2((w * np.cross(pp, qq)).sum(-1), (pp * qq).sum(-1))


def wrapd(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


def disc_grid(rad, step=SP_DISC):
    g = np.arange(-rad, rad + 1e-6, step); Y, Z = np.meshgrid(g, g); k = Y ** 2 + Z ** 2 <= rad ** 2 + 1e-9
    return np.stack([Y[k], Z[k]], 1)


def tangent_dirs(F, yz, r):
    """unit directions of tangent-plane offsets yz (k, 2) mm around F's X axis (F (3, 3) columns X, Y, Z) at radius r"""
    return unit(F[:, 0][None] + (yz[:, :1] * F[:, 1][None] + yz[:, 1:] * F[:, 2][None]) / r)


def rim_yz(rad, step=SP):
    n = max(8, int(math.ceil(2 * math.pi * rad / step))); t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.stack([rad * np.cos(t), rad * np.sin(t)], 1)


# ======================================================================================================== design
class Design:
    def __init__(self, p, B, HG, RS):
        self.p = p = dict(PARAMS, **p); self.B = B; self.HG = HG; self.RS = RS; self.n = len(HG)
        self.N = N = int(p["N"]); self.lam = p["lam"] * D2R
        self.b = bvec(p["b_az"], p["b_el"]); self.W0 = wdir(p["w_d"], p["w_az"])
        self.over = p["mode"] == "over"
        self.h_plate = H_OVER if self.over else STACK
        self.d0 = 0.0 if self.over else float(p["d0"]); self.d1 = 0.0 if self.over else float(p["d1"])
        self.phi0, self.phi1 = self.d0 / R_EST, self.d1 / R_EST
        e = np.array([0.0, 0.0, 1.0]) if abs(self.b[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
        Y = unit(np.cross(self.b, e)); self.L1ref = np.stack([self.b, Y, np.cross(self.b, Y)], 1)
        y3 = Y_ARM - (Y_ARM @ self.W0) * self.W0; self.y3 = unit(y3); self.n3 = np.cross(self.W0, self.y3)
        self.ss_max = N * (self.lam - STRETCH * D2R)
        self.cfg_ok = self.ss_max > 0.05
        # u_ref: middle of the end-node half opening over the fit clips (approx. span = sigma - phi0 - phi1)
        sig = np.arccos(np.clip((HG @ self.W0) @ self.b, -1, 1))
        cl = np.array([k == "clip" for k in B.kind])
        ssa = np.clip(sig[cl] - self.phi0 - self.phi1, 0.02, self.ss_max)
        ua = self.u_of(ssa)
        self.u_ref = float(p["u_ref"]) * D2R if p.get("u_ref") is not None else float((ua.min() + ua.max()) / 2)
        self.table()
        self.rad = None                                                    # fitted radii (None: R_EST everywhere)
        self.fold_tab(); self.K = self.kin(HG); self.fit(); self.fold_tab(); self.K = self.kin(HG)

    # ---- kinematics -----------------------------------------------------------------------------------------------
    def u_of(self, ss):
        c2 = (1 + math.cos(self.lam)) / (1 + np.cos(np.asarray(ss) / self.N))
        return np.arccos(np.sqrt(np.clip(c2, 0, 1)))

    def FL2(self, ss):
        """L2's hub frame in L1's local frame for scissor spans ss (k,) -> (k, 3, 3)"""
        ss = np.atleast_1d(ss); a = self.u_ref - self.u_of(ss)
        return rXZ(np.full_like(ss, self.phi0)) @ rXY(a) @ rXZ(ss) @ rXY(-a) @ rXZ(np.full_like(ss, self.phi1))

    def table(self):
        ss = np.linspace(0.2 * D2R, self.ss_max, 3000); F = self.FL2(ss); g = np.arccos(np.clip(F[:, 0, 0], -1, 1))
        mono = np.r_[True, np.diff(g) > 0]; k = np.argmin(mono) if not mono.all() else len(g)
        self.t_ss, self.t_g = ss[:k], g[:k]

    def fold_tab(self):
        """analytic scissor self-interference (same-layer bars, bosses) on a grid of spans -> smallest foldable span"""
        ss = np.linspace(self.t_ss[0], self.t_ss[-1], 240); ok = np.array([self.fold_ok(s) for s in ss])
        bad = np.nonzero(~ok)[0]
        self.ss_fold = float(ss[bad.max() + 1]) if len(bad) and bad.max() + 1 < len(ss) else (float(ss[0]) if not len(bad) else 9.0)
        self.fold_grid = (ss, ok)

    def rf(self, f):
        if self.rad is None: return np.full_like(np.asarray(f, float), R_EST)
        return np.interp(f, self.kf, self.kr)

    def nodes_local(self, ss, u):
        """scissor nodes in the scissor's own root frame: end nodes (N+1, 2, 3) (+u, -u) and centres (N, 3)"""
        N = self.N; f = np.arange(N + 1) / N; fc = (np.arange(N) + 0.5) / N
        E = np.stack([np.stack([np.cos(f * ss) * math.cos(u), s * np.full_like(f, math.sin(u)), np.sin(f * ss) * math.cos(u)], -1) for s in (1, -1)], 1)
        C = np.stack([np.cos(fc * ss), np.zeros_like(fc), np.sin(fc * ss)], -1)
        return E, C, f, fc

    def bars(self, ss, u):
        """[(layer 0/1, unit k, P, Q, attached node ids)] ; node ids: end (k, s) -> 2k + (s<0), centre k -> 2(N+1) + k"""
        E, C, f, fc = self.nodes_local(ss, u); out = []
        for k in range(self.N):
            out.append((0, k, E[k, 0], E[k + 1, 1], (2 * k, 2 * (k + 1) + 1, 2 * (self.N + 1) + k)))
            out.append((1, k, E[k, 1], E[k + 1, 0], (2 * k + 1, 2 * (k + 1), 2 * (self.N + 1) + k)))
        return out, E, C, f, fc

    def fold_ok(self, ss):
        u = float(self.u_of(ss)); bars, E, C, f, fc = self.bars(ss, u)
        nd = np.concatenate([E.reshape(-1, 3), C]); nf = np.r_[np.repeat(f, 2), fc]; rn = self.rf(nf)
        A = np.arccos(np.clip(nd @ nd.T, -1, 1)) * np.minimum(rn[:, None], rn[None]); np.fill_diagonal(A, 1e9)
        if A.min() < 2 * BOSS_R + GAP_PART: return False
        s = np.linspace(0, 1, 41); lamb = math.acos(np.clip(bars[0][2] @ bars[0][3], -1, 1))
        poly = []
        for (ly, k, P, Q, att) in bars:
            D = (np.sin((1 - s) * lamb)[:, None] * P + np.sin(s * lamb)[:, None] * Q) / math.sin(lamb)
            poly.append((ly, k, unit(D), self.rf(k / self.N + s / self.N), att))
        for (ly, k, D, r, att) in poly:                                    # boss vs a bar it does not carry
            m = np.ones(len(nd), bool); m[list(att)] = False
            d = np.arccos(np.clip(nd[m] @ D.T, -1, 1)) * np.minimum(rn[m][:, None], r[None])
            if d.min() < BOSS_R + BAR_W / 2 + GAP_PART: return False
        for (l1, k1, D1, r1, _), (l2, k2, D2, r2, _) in itertools.combinations(poly, 2):
            if l1 != l2: continue                                          # other layer: radially separated by pitch
            d = np.arccos(np.clip(D1 @ D2.T, -1, 1)) * np.minimum(r1[:, None], r2[None])
            if d.min() < BAR_W + GAP_PART: return False
        return True

    def kin(self, HG):
        W = HG @ self.W0; sig = np.arccos(np.clip(W @ self.b, -1, 1))
        inr = (sig >= self.t_g[0]) & (sig <= self.t_g[-1])
        ss = np.interp(sig, self.t_g, self.t_ss)
        F = self.FL2(ss); wl = F[:, :, 0]
        a = W @ self.L1ref                                                 # W in L1ref coords
        q1 = np.arctan2(a[:, 2], a[:, 1]) - np.arctan2(wl[:, 2], wl[:, 1])
        L1 = self.L1ref[None] @ rX(q1); L2 = L1 @ F
        res = np.arccos(np.clip((L2[:, :, 0] * W).sum(-1), -1, 1)) / D2R
        q3 = ang_about(W, HG @ self.y3, L2[:, :, 1])
        ok = inr & (res < 0.5) & (ss >= self.ss_fold) & (ss <= self.ss_max + 1e-9) & self.cfg_ok
        return dict(sig=sig, ss=ss, u=self.u_of(ss), L1=L1, L2=L2, F=F, q=np.stack([q1 / D2R, ss / D2R, q3 / D2R], 1), ok=ok, res=res, W=W)

    # ---- geometry (unit directions in L1-local / L2-local / humerus frames; radii applied per part) ---------------
    def scissor_samples(self, ss, u, fit=False):
        """skin-facing samples of bars + bosses in the scissor root frame: dirs (k, 3), f (k,), layer offset (k,),
        node flag (k,: -1 bar, else node id); and volume samples (dirs, radius offsets above r(f), f, end-node flag)"""
        bars, E, C, f, fc = self.bars(ss, u)
        D_, F_, O_, V_ = [], [], [], []
        vd, vf, vo, ve = [], [], [], []
        lamb = math.acos(np.clip(bars[0][2] @ bars[0][3], -1, 1)); pitch = self.p["pitch"]
        for (ly, k, P, Q, att) in bars:
            r0 = float(np.mean(self.rf(np.linspace(k / self.N, (k + 1) / self.N, 5))))
            n_al = max(3, int(math.ceil(lamb * r0 / SP)) + 1); s = np.linspace(0, 1, n_al)
            D = (np.sin((1 - s) * lamb)[:, None] * P + np.sin(s * lamb)[:, None] * Q) / math.sin(lamb)
            n = unit(np.cross(P, Q)); fs = k / self.N + s / self.N; rr = self.rf(fs) + ly * pitch
            c = np.arange(-BAR_W / 2, BAR_W / 2 + 1e-6, SP)
            Dd = unit(D[:, None, :] + (c[None, :, None] / rr[:, None, None]) * n[None, None, :])
            al = np.minimum.reduce([np.abs(s - 0) * lamb * rr, np.abs(s - 0.5) * lamb * rr, np.abs(s - 1) * lamb * rr])
            keep = np.sqrt(al[:, None] ** 2 + c[None, :] ** 2) >= BOSS_R
            fm = np.broadcast_to(fs[:, None], keep.shape)
            D_.append(Dd[keep]); F_.append(fm[keep]); O_.append(np.full(keep.sum(), ly * pitch))
            # volume: underside + top of the whole bar
            vd += [Dd.reshape(-1, 3)] * 2; vf += [np.broadcast_to(fs[:, None], keep.shape).reshape(-1)] * 2
            vo += [np.full(Dd.shape[0] * Dd.shape[1], ly * pitch), np.full(Dd.shape[0] * Dd.shape[1], ly * pitch + BAR_T)]
            ve += [np.zeros(Dd.shape[0] * Dd.shape[1], bool)] * 2
        nd = np.concatenate([E.reshape(-1, 3), C]); nf = np.r_[np.repeat(f, 2), fc]
        endn = np.r_[np.repeat((f == 0) | (f == 1), 2), np.zeros(len(fc), bool)]
        g = disc_grid(BOSS_R); rim = rim_yz(BOSS_R)
        for j, (d, fj) in enumerate(zip(nd, nf)):
            tz = unit(np.cross(d, np.array([0.0, 1.0, 0.0])) + 1e-9); ty = np.cross(tz, d); Fj = np.stack([d, ty, tz], 1)
            rj = float(self.rf(fj)); dd = tangent_dirs(Fj, g, rj)
            D_.append(dd); F_.append(np.full(len(dd), fj)); O_.append(np.zeros(len(dd)))
            dr = tangent_dirs(Fj, rim, rj)
            for h in (0.0, BOSS_H / 2, BOSS_H):
                vd.append(dr); vf.append(np.full(len(dr), fj)); vo.append(np.full(len(dr), h)); ve.append(np.full(len(dr), endn[j]))
            vd.append(dd); vf.append(np.full(len(dd), fj)); vo.append(np.full(len(dd), BOSS_H)); ve.append(np.full(len(dd), endn[j]))
        face = (np.concatenate(D_), np.concatenate(F_), np.concatenate(O_))
        vol = (np.concatenate(vd), np.concatenate(vf), np.concatenate(vo), np.concatenate(ve))
        return face, vol

    def plate_yz(self, r, d0):
        """plate footprint in its hub's local tangent plane (mm): all points, and the disc mask; z along the scissor
        measured from the hub toward the scissor (L2's is mirrored by the caller)"""
        ur = self.u_ref * r; y_lo = (self.u_ref - 2 * self.u_hi) * r - BOSS_R - 1; y_hi = ur + BOSS_R + 1
        g = np.arange(-40, 40 + 1e-6, SP); Y, Z = np.meshgrid(g, g); Y, Z = Y.ravel(), Z.ravel()
        disc = Y ** 2 + Z ** 2 <= HUB_R ** 2
        bar = (np.abs(Z - d0) <= SLOT_W / 2) & (Y >= y_lo) & (Y <= y_hi)
        neck = (Z >= 0) & (Z <= d0) & (np.abs(Y) <= SLOT_W / 2) if d0 > 0 else np.zeros_like(disc)
        m = disc | bar | neck
        return np.stack([Y[m], Z[m]], 1), disc[m]

    # ---- radii fitted to the skin -------------------------------------------------------------------------------
    def _bisect(self, i, D, gid, off, ng, lo=20.0, hi=200.0, it=60):
        """per group: smallest radius r (marching OUT from inside the body, so a far re-entry - torso, head - never
        counts) such that every sample (r + its offset) * dir is >= CLEAR from the skin. Safe steps: the signed
        distance is 1-Lipschitz, so no group can clear before r + (CLEAR - min dist). inf when none <= hi."""
        r = np.full(ng, lo); act = np.ones(ng, bool)
        for _ in range(it):
            sel = act[gid]
            if not sel.any(): break
            d = self.B.dist(i, D[sel] * (r[gid[sel]] + off[sel])[:, None]); m = np.full(ng, np.inf); np.minimum.at(m, gid[sel], d)
            ok = act & (m >= CLEAR - 0.05); act &= ~ok
            r = np.where(act, r + np.maximum(CLEAR - np.where(np.isfinite(m), m, CLEAR), 0.3), r)
            act &= r <= hi
        return np.where(r <= hi, r, np.inf)

    def fit(self):
        K = self.K; p = self.p; valid = np.nonzero(K["ok"])[0]; self.valid0 = K["ok"].copy()
        self.u_hi = float(K["u"][valid].max()) if len(valid) else self.u_ref
        nb = 16 * self.N; self.fb = (np.arange(nb) + 0.5) / nb
        yz, disc = self.plate_yz(R_EST, self.d0); yz3, disc3 = self.plate_yz(R_EST, self.d1)
        sy = np.arange(HUB_R + 1.5, STUB_L + 1e-6, SP); sc = np.arange(-STUB_W / 2, STUB_W / 2 + 1e-6, SP); self.stub_s = sy
        th = sy / R_EST; Dst = np.cos(th)[:, None, None] * self.W0 + np.sin(th)[:, None, None] * self.y3
        self.stub_H = unit(Dst + (sc[None, :, None] / R_EST) * self.n3)  # (rows, across, 3) humerus frame
        gd = disc_grid(HUB_R); self.gd = gd
        need = dict(J1=np.full(self.n, np.inf), J3=np.full(self.n, np.inf)); need_st = np.full((self.n, len(sy)), np.inf)
        need_f = np.full((self.n, nb), -np.inf)
        FJ1 = self.L1ref
        for i in valid:
            Rs = self.RS[i]; L1 = K["L1"][i]; L2 = K["L2"][i]; HGi = self.HG[i]
            FW = np.stack([K["W"][i], HGi @ self.y3, HGi @ self.n3], 1)
            dJ1 = tangent_dirs(FJ1, gd, R_EST); dP1 = tangent_dirs(L1, yz[~disc], R_EST)
            dJ3 = tangent_dirs(FW, gd, R_EST); yz2 = yz3[~disc3] * np.array([1.0, -1.0]); dP2 = tangent_dirs(L2, yz2, R_EST)
            dst = self.stub_H.reshape(-1, 3) @ HGi.T
            face, _ = self.scissor_samples(K["ss"][i], K["u"][i])
            Fr = L1 @ rXZ(self.phi0) @ rXY(self.u_ref - K["u"][i]); dsc = face[0] @ Fr.T
            D = np.concatenate([dJ1, dP1, dJ3, dP2, dst, dsc]) @ Rs.T
            ns = len(sy); nsc = len(dsc); nst = dst.shape[0]
            gid = np.r_[np.zeros(len(dJ1) + len(dP1), int), np.ones(len(dJ3) + len(dP2), int),
                        2 + np.repeat(np.arange(ns), len(sc)), 2 + ns + np.arange(nsc)]
            off = np.r_[np.zeros(len(dJ1)), np.full(len(dP1), self.h_plate), np.zeros(len(dJ3)), np.full(len(dP2), self.h_plate),
                        np.zeros(nst), face[2]]
            r = self._bisect(int(i), D, gid, off, 2 + ns + nsc)
            need["J1"][i], need["J3"][i] = r[0], r[1]; need_st[i] = r[2:2 + ns]
            rs = r[2 + ns:]                                                # scissor sample needs (already minus the offset)
            fbin = np.minimum((face[1] * nb).astype(int), nb - 1)
            req = np.full(nb, -np.inf); np.maximum.at(req, fbin, rs); need_f[i] = req
            # over-plate flags (geometric): which bins pass over the L1 / L2 plates (dilated by 1 mm + half bar)
            self._over_flags(i, dsc, face, fbin, nb, L1, L2)
        q = p["p"]; pc = lambda x: float(np.percentile(np.minimum(x[valid], 999.0), q)) if len(valid) else 999.0
        rJ1, rJ3 = pc(need["J1"]), pc(need["J3"])
        stub = np.percentile(np.minimum(need_st[valid], 999.0), q, axis=0) if len(valid) else np.full(len(sy), 999.0)
        stub = np.maximum(stub, rJ3 - (sy - HUB_R))                        # leaves the disc at <= 45 deg
        stub[0] = max(stub[0], rJ3)
        top1, top3 = rJ1 + self.h_plate + PLATE_T, rJ3 + self.h_plate + PLATE_T
        req = need_f.copy()
        for i in valid:
            o1, o3 = self.flags[i]
            req[i] = np.maximum(req[i], np.where(o1 > -1e8, top1 + 1 + o1, -np.inf))
            req[i] = np.maximum(req[i], np.where(o3 > -1e8, top3 + 1 + o3, -np.inf))
        rq = req[valid]; rq = np.where(rq == -np.inf, 0.0, np.where(rq == np.inf, 999.0, rq))
        Rf = np.percentile(rq, q, axis=0) if len(valid) else np.full(nb, 999.0)
        Kn = int(p["kpu"]) * self.N; kf = np.linspace(0, 1, Kn + 1); kr = np.zeros(Kn + 1)
        for j in range(Kn + 1):
            lo, hi = kf[max(j - 1, 0)], kf[min(j + 1, Kn)]
            m = (self.fb >= lo) & (self.fb <= hi); kr[j] = Rf[m].max() if m.any() else 0.0
        kr[0] = max(kr[0], top1 + 1); kr[-1] = max(kr[-1], top3 + 1)
        if not int(p["taper"]): kr[:] = kr.max()
        self.kf, self.kr = kf, kr; self.rad = dict(J1=rJ1, J3=rJ3, stub=stub, top1=top1, top3=top3)
        self.need = need

    def _over_flags(self, i, dsc, face, fbin, nb, L1, L2):
        """per bin: largest (1 - layer offset) requirement flag over the L1 / L2 plate footprints, else -inf"""
        if not hasattr(self, "flags"): self.flags = {}
        out = []
        for L, mir, d0 in ((L1, 1.0, self.d0), (L2, -1.0, self.d1)):
            loc = dsc @ L                                                  # local coords (X hub axis)
            y = loc[:, 1] / np.maximum(loc[:, 0], 1e-6) * R_EST; z = mir * loc[:, 2] / np.maximum(loc[:, 0], 1e-6) * R_EST
            pad = 1.0
            disc = y ** 2 + z ** 2 <= (HUB_R + pad) ** 2
            ur = self.u_ref * R_EST; y_lo = (self.u_ref - 2 * self.u_hi) * R_EST - BOSS_R - 1 - pad; y_hi = ur + BOSS_R + 1 + pad
            bar = (np.abs(z - d0) <= SLOT_W / 2 + pad) & (y >= y_lo) & (y <= y_hi)
            neck = (z >= 0) & (z <= d0) & (np.abs(y) <= SLOT_W / 2 + pad) if d0 > 0 else np.zeros_like(disc)
            m = (disc | bar | neck) & (loc[:, 0] > 0)
            fl = np.full(nb, -np.inf); np.maximum.at(fl, fbin[m], -face[2][m]); out.append(fl)
        self.flags[i] = tuple(out)

    # ---- pose -> parts ------------------------------------------------------------------------------------------
    def parts(self, i):
        """per part: (skin-facing points, other points) in the thorax frame"""
        K = self.K; R = self.rad; Rs = self.RS[i]; HGi = self.HG[i]; L1 = K["L1"][i]; L2 = K["L2"][i]
        FW = np.stack([K["W"][i], HGi @ self.y3, HGi @ self.n3], 1); out = {}
        hp, rJ1, rJ3 = self.h_plate, R["J1"], R["J3"]
        gd = self.gd; rim = rim_yz(HUB_R)
        # J1 member (S-fixed lower disc) and J1 upper member (boss + plate)
        d = tangent_dirs(self.L1ref, gd, rJ1); dr = tangent_dirs(self.L1ref, rim, rJ1)
        out["J1low"] = (d * rJ1, np.concatenate([d * (rJ1 + LOW_T), dr * rJ1, dr * (rJ1 + LOW_T)]))
        yz, disc = self.plate_yz(rJ1 + hp, self.d0)
        dp = tangent_dirs(L1, yz, rJ1 + hp); dr = tangent_dirs(L1, rim, rJ1)
        btop = rJ1 + (H_OVER if self.over else CAP)
        out["J1up"] = (dp[~disc] * (rJ1 + hp), np.concatenate([dp * (rJ1 + hp + PLATE_T), dp[disc] * (rJ1 + hp), tangent_dirs(L1, gd, btop) * btop]
                                                         + [dr * (rJ1 + h) for h in np.linspace(STACK, btop - rJ1, 4)]))
        # J3: humerus-fixed lower disc + stub; upper member (boss + L2 plate)
        d = tangent_dirs(FW, gd, rJ3); dr = tangent_dirs(FW, rim, rJ3)
        st = self.stub_H @ HGi.T; rr = self.rad["stub"][:, None, None]
        sface = (st * rr).reshape(-1, 3); stop = (st * (rr + STUB_T)).reshape(-1, 3)
        sside = np.concatenate([(st[:, [0, -1]] * (rr + h)).reshape(-1, 3) for h in (STUB_T / 3, 2 * STUB_T / 3)])
        out["J3low"] = (np.concatenate([d * rJ3, sface]), np.concatenate([d * (rJ3 + LOW_T), dr * rJ3, dr * (rJ3 + LOW_T), stop, sside]))
        yz, disc = self.plate_yz(rJ3 + hp, self.d1); yz = yz * np.array([1.0, -1.0])
        dp = tangent_dirs(L2, yz, rJ3 + hp); dr = tangent_dirs(L2, rim, rJ3); btop = rJ3 + (H_OVER if self.over else CAP)
        out["J3up"] = (dp[~disc] * (rJ3 + hp), np.concatenate([dp * (rJ3 + hp + PLATE_T), dp[disc] * (rJ3 + hp), tangent_dirs(L2, gd, btop) * btop]
                                                         + [dr * (rJ3 + h) for h in np.linspace(STACK, btop - rJ3, 4)]))
        # scissor
        face, vol = self.scissor_samples(K["ss"][i], K["u"][i])
        Fr = L1 @ rXZ(self.phi0) @ rXY(self.u_ref - K["u"][i])
        fp = (face[0] @ Fr.T) * (self.rf(face[1]) + face[2])[:, None]
        vp = (vol[0] @ Fr.T) * (self.rf(vol[1]) + vol[2])[:, None]
        out["scissor"] = (fp, vp[~vol[3]]); out["pins"] = (np.zeros((0, 3)), vp[vol[3]])
        return {k: (a @ Rs.T, b @ Rs.T) for k, (a, b) in out.items()}

    PAIRS = [("J1low", "J3low"), ("J1low", "J3up"), ("J1up", "J3low"), ("J1up", "J3up"), ("scissor", "J1low"),
             ("scissor", "J1up"), ("scissor", "J3low"), ("scissor", "J3up"), ("J3up", "J3low_stub"), ("pins", "J3low_stub")]

    def interfere(self, P):
        allp = {k: np.concatenate([a, b]) for k, (a, b) in P.items()}
        for a, b in self.PAIRS:
            if b == "J3low_stub":
                B_ = self._stub_pts
                if a == "J3up": A_ = allp["J3up"]
                else: A_ = allp["pins"]
            else:
                A_, B_ = allp[a], allp[b]
            if not len(A_) or not len(B_): continue
            ca, cb = A_.mean(0), B_.mean(0)
            if np.linalg.norm(ca - cb) > np.linalg.norm(A_ - ca, axis=1).max() + np.linalg.norm(B_ - cb, axis=1).max() + 3: continue
            if cKDTree(B_).query(A_, distance_upper_bound=GAP_PART)[0].min() < GAP_PART - 1e-6: return f"{a}/{b}"
        return None

    def metal(self, i, status=None):
        K = self.K; B = self.B
        if not self.cfg_ok: return None, "config"
        if not K["ok"][i]:
            ss = K["ss"][i]; sig = K["sig"][i]
            if sig < self.t_g[0] or ss < self.ss_fold: return None, "fold"
            if sig > self.t_g[-1] or ss > self.ss_max: return None, "stretch"
            return None, "closure"
        if B.kind[i] == "clip" and status is not None:
            ok, why = status.get(int(B.idx[i]), (False, "missing"))
            if not ok: return None, why
        if max(self.rad["J1"], self.rad["J3"], self.kr.max()) > 200: return None, "no radius"
        P = self.parts(i)
        HGi = self.HG[i]; st = self.stub_H[:, :, :] @ HGi.T; rr = self.rad["stub"][:, None, None]
        self._stub_pts = np.concatenate([(st * (rr + h)).reshape(-1, 3) for h in (0, STUB_T / 2, STUB_T)]) @ self.RS[i].T
        w = self.interfere(P)
        if w: return None, "interference " + w
        face = np.concatenate([v[0] for v in P.values()]); other = np.concatenate([v[1] for v in P.values()])
        do = B.dist(i, other)
        if do.min() < 0: face = np.r_[face, other[np.argmin(do)][None]]
        return face, ""


# ======================================================================================================== clips
def clip_status(D):
    """every fit-clip frame at 10 fps: closure, span inside [fold, stretch], no joint jump > FLIP since the last
    followed frame -> {dataset index: (ok, reason)}"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; HGa = Z["HG"].astype(float); st = {}; mx = 0.0
    for nme in CB.FIT:
        ix = np.nonzero(cid == names.index(nme))[0]; K = D.kin(HGa[ix]); last = None
        for k, j in enumerate(ix):
            if not K["ok"][k]: st[int(j)] = (False, "kin"); continue
            q = K["q"][k]
            if last is not None:
                stp = float(np.abs(wrapd(q - last)).max()); mx = max(mx, stp)
                if stp > FLIP: st[int(j)] = (False, "flip"); continue
            st[int(j)] = (True, ""); last = q
    D.max_step = mx
    return st


def run(p, B, HG, RS):
    t = time.time(); D = Design(p, B, HG, RS); st = clip_status(D); B.reset(); why = {}
    for i in range(len(B.poses)):
        P, w = D.metal(i, st)
        if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None)
        else:
            d = B.record(i, P)
            if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1)
    K = D.K; v = K["ok"]
    r["shape"] = dict(rJ1=round(D.rad["J1"], 1), rJ3=round(D.rad["J3"], 1), r_knots=[round(float(x), 1) for x in D.kr],
                      stub=[round(float(D.rad["stub"].min()), 1), round(float(D.rad["stub"].max()), 1)],
                      ss_fold=round(D.ss_fold / D2R, 1), ss_max=round(D.ss_max / D2R, 1), sig_rng=[round(float(D.t_g[0] / D2R), 1), round(float(D.t_g[-1] / D2R), 1)],
                      u_ref=round(D.u_ref / D2R, 1), u_hi=round(D.u_hi / D2R, 1), kin_valid=round(float(v.mean()), 3),
                      max_step=round(D.max_step, 1), width_fold=round(2 * D.u_hi * float(np.mean(D.kr)), 1))
    return r, D


def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) of the concept for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = json.dumps(prm, sort_keys=True)
    if key not in _cache:
        Z = CB._poses_all(); _cache.clear(); D = Design(prm, B, Z["HG"][B.idx].astype(float), Z["RS"][B.idx].astype(float))
        _cache[key] = (D, clip_status(D))
    D, st = _cache[key]
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return D.metal(i, st)[0]


def pick_poses(B):
    """bench indices of a rest, an overhead, an across-the-body and a behind-the-back pose"""
    E = np.array([q["elev"] for q in B.poses]); Pl = np.array([q["plane"] for q in B.poses]); Ax = np.array([q["axial"] for q in B.poses])
    out = dict(rest=int(np.argmin(E + 0.2 * np.abs(Pl - 30))), overhead=int(np.argmax(E)))
    across = [j for j in range(len(E)) if 60 <= E[j] <= 110]; out["across"] = int(max(across, key=lambda j: Pl[j])) if across else 0
    bb = [j for j, c in enumerate(B.clip) if c == "Reach back pocket"]
    out["behind back"] = int(bb[len(bb) // 2]) if bb else int(np.argmin(Pl))
    return out


def sketch(D, B, out_png, st=None):
    """matplotlib sketch: skin (grey) + metal samples coloured by distance to the skin, four poses"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    picks = pick_poses(B); fig, axs = plt.subplots(1, 4, figsize=(18, 5))
    v = unit(np.array([0.25, 0.45, 1.0])); e1 = unit(np.cross([0.0, 1.0, 0.0], v)); e2 = np.cross(v, e1)
    for ax, (nm, i) in zip(axs, picks.items()):
        V, _ = B.skin(i); V = np.asarray(V); sel = (np.linalg.norm(V, axis=1) < 170) & ((V @ v) > -20)
        Vs = V[sel][::3]; ax.scatter(Vs @ e1, Vs @ e2, s=0.3, c="0.75", rasterized=True)
        P, why = D.metal(i, st)
        if P is None:
            K = D.K
            if K["ok"][i]: P = np.concatenate([a for a, b in D.parts(i).values()])
        if P is not None:
            d = B.dist(i, P); c = np.where(d < 0, "red", np.where(d <= 10, "tab:green", np.where(d <= 14, "gold", "tab:orange")))
            o = np.argsort(P @ v); ax.scatter((P @ e1)[o], (P @ e2)[o], s=1.5, c=c[o])
            ib = float(np.mean((d >= 2) & (d <= 14)))
        else: ib = float("nan")
        q = B.poses[i]
        ax.set_title(f"{nm}: plane {q['plane']:.0f} elev {q['elev']:.0f} axial {q['axial']:.0f}\n"
                     + (f"in band 14: {ib:.0%}, sigma {D.K['sig'][i] / D2R:.0f} deg" if P is not None else f"not taken ({why})"), fontsize=9)
        ax.set_aspect("equal"); ax.axis("off")
    fig.suptitle(f"{ID}: green 2-10 mm, gold 10-14, orange > 14, red inside; view from lateral-anterior-above", fontsize=10)
    fig.tight_layout(); fig.savefig(out_png, dpi=110); plt.close(fig)


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def sweep(configs, B, out=SWEEP_OUT, tag=""):
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float)
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r, D = run(p, B, HG, RS)
        except Exception as e:
            import traceback; traceback.print_exc(); print("ERR", p, e, flush=True); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r["shape"], mode=r["mode"], stage=tag)
        rows.append(row); json.dump(rows, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
              f"contact {r['contact']:.3f} | {r['why']} | {r['shape']} | {r['secs']} s | "
              + " ".join(f"{k}={p[k]}" for k in ('mode', 'N', 'lam', 'b_az', 'b_el', 'w_d', 'w_az', 'p', 'pitch', 'taper', 'kpu')), flush=True)
    return rows


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40)
        tmp = os.environ.get("SC_TMP", "/tmp")
        sweep([dict(PARAMS)] + [dict(PARAMS, mode="beside")], B, out=os.path.join(tmp, "scissor_check.json"), tag="check")

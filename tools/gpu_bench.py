#!/usr/bin/env python3
"""GPU (torch) port of the concept bench FAST path for the ZERO-COMPLEXITY family: three active pins whose axes meet at
GH, O20 hubs, 12 x 3 straps on great circles, the K7 14 x 6 neck to BOTTOM's bar - i.e. docs/concepts/models/zc-frontier-3r.py
(= spine-parked-j2-3r's kit build + stack orders inv2 / inv3, the 1 mm radial K6, the hub crown / wall check and the
verifier's top-face check) evaluated exactly as its CPU path does, for THOUSANDS of configurations per call.

    python3 tools/gpu_bench.py pack 110 360                  frames / continuity tables of a bench -> .cache/gpu_bench/
    python3 tools/gpu_bench.py eval CFGS.json OUT.json [--bench 110,360] [--fit 60,160] [--chunk 48] [--device cuda]
    python3 tools/gpu_bench.py parity --n 50 --bench 110,360 [--fit 60,160] --out P.json [--procs 8] [--leaders]
    python3 tools/gpu_bench.py speed --n 512 --bench 110,360

What is computed (each step = the CPU kit's, in float64 except the K6 dot products which the kit also does in float32):
  K1 closure (fold margin 5 deg, user ruling 1) -> K2 dense continuity (slerped frames between consecutive taken clip
  frames, <= 2 deg per step, joint values and axes jump <= 25 deg; the slerp tables come from scipy, as in the kit) ->
  K3 skin-requirement march (1 mm lattice, 2 mm clearance, 15 mm window) on every hub-disc / strap sample over the
  fit poses -> per-sample quantile q (numpy's linear rule) -> hub levels, strap ramps to the hub stack (12.25 mm hubs,
  3.15 mm stack), `over` (link 2 over link 1 and the neck, or the inverted stack orders), 60 deg climb limit ->
  member points on the wear bench -> K6 part-part collisions (1 mm lateral, 1 mm radial (overlap 0.9999), joint
  partners exempt within 12 mm of the shared axis) -> signed distance on the per-pose int8 grid (trilinear, the
  kit's dist_many) of the skin faces, hub crowns + walls (31 angles x 6 levels) and every member's top face ->
  reach / follow / in-band 2-14 / 2-10 / contact / gap; the honesty audit's sampling rule (median spacing <= 4 mm)
  and hub_F <= 140 mm (+100 when violated), the seat rule (J1 on the back / acromion top, else 200).
Protocols: same-bench (fit = wear, the golden search on Bench(110,360)) or frozen (fit on --fit, worn on --bench).
Points outside the +-260 mm grid box (the CPU falls back to the exact libigl path there) are counted per config
(`outside`); they do not occur for this family's metal.
"""
import json, math, os, sys, time
import numpy as np
import torch

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, ".cache", "concept_bench")
PACKS = os.path.join(REPO, ".cache", "gpu_bench")
D2R = math.pi / 180
HUB_R, STACK, CROWN = 10.0, 3.15, 12.25
H_GRID, HALF, Q = 4.0, 260.0, 0.25
MARGIN = 5.0
CROWN_LEVELS = (2.0, 4.0, 6.0, 8.0, 10.0, 12.25)
N_WALL = max(16, int(round(2 * math.pi * HUB_R / 2.0)))
WB = np.array([0.0, -0.0713, 0.9975]); DB = np.array([0.0, -0.9975, -0.0713])
BAR0_H = 67.5 * WB + 40.0 * DB
PARAMS = dict(az=95.8565, el=65.2093, a1=37.6, a2=73.6, wd=84.8, wa=-11.37, sigma=-1, inv2=0, inv3=0, q=0.97, end_extra=0.0)
BOUNDS = dict(az=(-110.0, 135.0), el=(-20.0, 90.0), a1=(12.0, 168.0), a2=(12.0, 168.0), wd=(20.0, 175.0),
              wa=(-180.0, 180.0), q=(0.8, 1.0), end_extra=(0.0, 8.0))
ANT_MAX = 0.20


def snap(p):
    """= zc-frontier-3r.snap (the rules are never loosened: margin 5, O20, 12 x 3 straps)"""
    p = dict(PARAMS, **p)
    for k, (lo, hi) in BOUNDS.items():
        if k == "wa": p[k] = (float(p[k]) + 180.0) % 360.0 - 180.0
        else: p[k] = min(hi, max(lo, float(p[k])))
    p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    for k in ("inv2", "inv3"): p[k] = 1 if float(p[k]) >= 0.5 else 0
    return p


def bvec_np(az, el):
    az, el = np.asarray(az, float) * D2R, np.asarray(el, float) * D2R
    return np.stack([-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)], -1)


def seat_ok(az, el):
    u = bvec_np(az, el)
    return bool(-110.0 <= az <= 135.0 and -20.0 <= el <= 90.0 and u[0] <= ANT_MAX)


# ---- bench packs (CPU side, once per bench) --------------------------------------------------------------------------
def pack_path(nc, nw): return os.path.join(PACKS, f"pack_{nc}_{nw}.npz")


def make_pack(nc, nw):
    """frames (RS, RHG, RH), pose kinds, clip order and the slerp tables of every in-clip pair (kit _slerp_frames)"""
    from scipy.spatial.transform import Rotation as R
    sys.path.insert(0, os.path.join(REPO, "tools")); os.environ.setdefault("CB_QUIET_EXACT", "1")
    import concept_kit as K
    B = K.bench(nc, nw); F = K.frames(B)
    co = B.clip_order(); clips = [np.array(v, np.int64) for v in co.values()]
    P = len(B.idx); cidx = np.full(P, -1, np.int64); cl = np.nonzero(F.clip)[0]; cidx[cl] = np.arange(len(cl))
    nC = len(cl); RVS = np.zeros((nC, nC, 3)); RVH = np.zeros((nC, nC, 3)); NS = np.zeros((nC, nC), np.int64)
    RSo = R.from_matrix(F.RS).as_matrix(); RHo = R.from_matrix(F.RHG).as_matrix()
    for js in clips:
        for a in range(len(js)):
            for b in range(a + 1, len(js)):
                j0, j1 = js[a], js[b]
                ang = max(np.degrees(R.from_matrix(X[j0].T @ X[j1]).magnitude()) for X in (F.RS, F.RHG))
                n = int(min(90, max(2, math.ceil(ang / 2.0) + 1)))
                rs = R.from_matrix(np.stack([F.RS[j0], F.RS[j1]])); rh = R.from_matrix(np.stack([F.RHG[j0], F.RHG[j1]]))
                RVS[cidx[j0], cidx[j1]] = (rs[0].inv() * rs[1]).as_rotvec(); RVH[cidx[j0], cidx[j1]] = (rh[0].inv() * rh[1]).as_rotvec()
                NS[cidx[j0], cidx[j1]] = n
    os.makedirs(PACKS, exist_ok=True)
    np.savez(pack_path(nc, nw), RS=F.RS, RHG=F.RHG, RH=F.RH, RSo=RSo, RHo=RHo, clip=F.clip, ws=F.ws, key=B.key,
             clips=np.concatenate(clips), clip_len=np.array([len(c) for c in clips]), cidx=cidx, RVS=RVS, RVH=RVH, NS=NS,
             elev=np.array([p["elev"] for p in B.poses]))
    return pack_path(nc, nw)


class GBench:
    """one bench on the device: frames, continuity tables and the int8 signed-distance grid"""
    def __init__(self, nc, nw, device="cuda", grid_dir=None):
        if not os.path.exists(pack_path(nc, nw)): make_pack(nc, nw)
        Z = np.load(pack_path(nc, nw)); self.dev = device; self.nc, self.nw = nc, nw
        T = lambda x, dt=torch.float64: torch.as_tensor(np.asarray(x), dtype=dt, device=device)
        self.RS, self.RHG, self.RH = T(Z["RS"]), T(Z["RHG"]), T(Z["RH"]); self.RSo, self.RHo = T(Z["RSo"]), T(Z["RHo"])
        self.clip = T(Z["clip"], torch.bool); self.ws = T(Z["ws"], torch.bool); self.key = str(Z["key"])
        self.P = len(Z["RS"]); L = Z["clip_len"]; o = np.r_[0, np.cumsum(L)]
        self.clips = [Z["clips"][o[i]:o[i + 1]].tolist() for i in range(len(L))]
        self.cidx = Z["cidx"]; self.cidx_t = T(Z["cidx"], torch.int64); self.RVS, self.RVH, self.NS = T(Z["RVS"]), T(Z["RVH"]), T(Z["NS"], torch.int64)
        d = grid_dir or os.path.join(CACHE, self.key)
        g = np.load(os.path.join(d, "grid.npy"), mmap_mode="r"); self.n = g.shape[1]
        self.G = torch.empty(g.size, dtype=torch.int8, device=device)
        step = 32                                                    # copy in slices (bounded host memory)
        for i in range(0, g.shape[0], step):
            a = torch.from_numpy(np.ascontiguousarray(g[i:i + step]).reshape(-1))
            self.G[i * self.n ** 3:i * self.n ** 3 + a.numel()] = a.to(device)
        self.outside = 0

    def dist(self, I, X):
        """signed distance (mm) of points X (N, 3) float64, each in pose I (N,): concept_kit.dist_many's trilinear formula"""
        n = self.n; g = (X + HALF) / H_GRID
        ins = ((g >= 0) & (g <= n - 1 - 1e-9)).all(-1)
        self.outside += int((~ins).sum())
        g = g.clamp(0, n - 1 - 1e-9); i0 = torch.floor(g); f = g - i0; i0 = i0.long()
        fx, fy, fz = f.unbind(-1)
        base = ((I * n + i0[..., 0]) * n + i0[..., 1]) * n + i0[..., 2]
        v = torch.zeros_like(fx)
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    w = (fx if dx else 1 - fx) * (fy if dy else 1 - fy) * (fz if dz else 1 - fz)
                    v = v + self.G[base + (dx * n + dy) * n + dz].to(torch.float64) * w
        return v * Q


# ---- vector helpers (the kit's, batched) ---------------------------------------------------------------------------
def unit(x): return x / (torch.linalg.norm(x, dim=-1, keepdim=True) + 1e-12)
def dot(a, b): return (a * b).sum(-1)


def bvec(az, el):
    az, el = az * D2R, el * D2R
    return torch.stack([-torch.cos(el) * torch.cos(az), torch.sin(el), torch.cos(el) * torch.sin(az)], -1)


def wdir(d, a):
    d, a = d * D2R, a * D2R
    return torch.stack([torch.sin(d) * torch.sin(a), -torch.cos(d), torch.sin(d) * torch.cos(a)], -1)


def closure(b, w, a1, a2, sigma, margin_deg=MARGIN):
    """K1 batched: b, w (..., 3); a1, a2, sigma broadcastable to b[..., 0]"""
    b, w = unit(b), unit(w); c = dot(b, w).clamp(-1, 1); n = unit(torch.linalg.cross(b, w)); A1, A2 = a1 * D2R, a2 * D2R
    den = 1 - c ** 2 + 1e-12; A = (torch.cos(A1) - c * torch.cos(A2)) / den; Bq = (torch.cos(A2) - c * torch.cos(A1)) / den
    p0 = A[..., None] * b + Bq[..., None] * w; h2 = 1 - (p0 * p0).sum(-1)
    p = p0 + (sigma * torch.sqrt(h2.clamp(min=0)))[..., None] * n
    th = torch.rad2deg(torch.arccos(c))
    margin = torch.minimum(torch.minimum(th - (a1 - a2).abs(), a1 + a2 - th), 360 - a1 - a2 - th)
    return p, (h2 > 0) & (margin >= margin_deg)


def axis_angle(k, ref, v):
    r = ref - dot(ref, k)[..., None] * k; w = v - dot(v, k)[..., None] * k
    return torch.rad2deg(torch.atan2(dot(torch.linalg.cross(r, w), k), dot(r, w)))


def rodrigues(rv):
    """rotation matrices (..., 3, 3) of rotation vectors (..., 3)"""
    th = torch.linalg.norm(rv, dim=-1); k = rv / th.clamp(min=1e-300)[..., None]
    Kx = torch.zeros(rv.shape[:-1] + (3, 3), dtype=rv.dtype, device=rv.device)
    Kx[..., 0, 1], Kx[..., 0, 2], Kx[..., 1, 2] = -k[..., 2], k[..., 1], -k[..., 0]
    Kx[..., 1, 0], Kx[..., 2, 0], Kx[..., 2, 1] = k[..., 2], -k[..., 1], k[..., 0]
    I = torch.eye(3, dtype=rv.dtype, device=rv.device).expand_as(Kx)
    s, c = torch.sin(th)[..., None, None], torch.cos(th)[..., None, None]
    return I + s * Kx + (1 - c) * (Kx @ Kx)


def mv(R, u):
    """R (..., 3, 3) @ u (..., 3)"""
    return (R @ u[..., None])[..., 0]


# ---- the chain -----------------------------------------------------------------------------------------------------
def kin(RS, RHG, pr):
    """axes p1, p2, p3 (C, P, 3) and closure ok (C, P) of a config batch pr on frames (P, 3, 3)"""
    u1 = bvec(pr["az"], pr["el"]); u3 = wdir(pr["wd"], pr["wa"])
    p1 = torch.einsum("pij,cj->cpi", RS, u1); p3 = torch.einsum("pij,cj->cpi", RHG, u3)
    p2, ok = closure(p1, p3, pr["a1"][:, None], pr["a2"][:, None], pr["sigma"][:, None])
    return p1, p2, p3, ok


def continuity(Bn, pr, ok, jump_deg=25.0):
    """K2 dense (concept_kit.continuity_dense) for a config batch: ok (C, P) -> ok2"""
    ok2 = ok.clone(); C = ok.shape[0]; dev = ok.device; ar = torch.arange(C, device=dev)
    u1 = bvec(pr["az"], pr["el"]); u3 = wdir(pr["wd"], pr["wa"])
    ex = torch.tensor([1.0, 0, 0], dtype=torch.float64, device=dev); ey = torch.tensor([0.0, -1, 0], dtype=torch.float64, device=dev)
    for js in Bn.clips:
        prev = torch.full((C,), -1, dtype=torch.int64, device=dev)
        for j in js:
            cand = ok2[:, j] & (prev >= 0)
            cc = torch.nonzero(cand)[:, 0]
            if len(cc):
                p0 = prev[cc]; a = Bn.cidx_t[p0]; b = int(Bn.cidx[j])
                n = Bn.NS[a, b]; nmax = int(n.max()); k = torch.arange(nmax, device=dev, dtype=torch.float64)
                valid = k[None, :] < n[:, None]
                s = torch.where(valid, k[None, :] / (n[:, None] - 1).to(torch.float64), torch.ones_like(k[None, :]))
                RSt = Bn.RSo[p0][:, None] @ rodrigues(Bn.RVS[a, b][:, None, :] * s[..., None])     # (m, nmax, 3, 3)
                RHt = Bn.RHo[p0][:, None] @ rodrigues(Bn.RVH[a, b][:, None, :] * s[..., None])
                q1 = mv(RSt, u1[cc][:, None, :].expand(-1, nmax, -1)); q3 = mv(RHt, u3[cc][:, None, :].expand(-1, nmax, -1))
                q2, okt = closure(q1, q3, pr["a1"][cc][:, None], pr["a2"][cc][:, None], pr["sigma"][cc][:, None])
                jq = torch.stack([axis_angle(q1, RSt[..., :, 0], q2), axis_angle(q2, q1, q3), axis_angle(q3, mv(RHt, ey.expand(q3.shape)), q2)], -1)
                d = torch.diff(jq, dim=1); d = torch.remainder(d + 180.0, 360.0) - 180.0
                vpair = valid[:, 1:]
                jmp = torch.where(vpair[..., None], d.abs(), torch.zeros_like(d)).amax((1, 2))
                for ax in (q1, q2, q3):
                    u = unit(ax); ang = torch.rad2deg(torch.arccos(dot(u[:, 1:], u[:, :-1]).clamp(-1, 1)))
                    jmp = torch.maximum(jmp, torch.where(vpair, ang, torch.zeros_like(ang)).amax(1))
                allok = (okt | ~valid).all(1)
                good = allok & (jmp <= jump_deg)
                bad = cc[~good]
                ok2[bad, j] = False
            prev = torch.where(ok2[:, j], torch.full_like(prev, j), prev)
    return ok2


def strap(u, v, width):
    """K5 strap layout (concept_kit.strap_dirs) padded per batch: u, v (C, P, 3) -> D (C, P, NS, nc, 3), ns (C,)"""
    u, v = unit(u), unit(v); ang = torch.arccos(dot(u, v).clamp(-1, 1))
    med = torch.quantile(ang, 0.5, dim=1)                      # numpy median (mean of the two middle values)
    ns = torch.clamp(torch.floor(med * 70.0 / 2.0).long() + 1, min=3); NS = int(ns.max())
    k = torch.arange(NS, device=u.device, dtype=torch.float64)
    keff = torch.minimum(k[None, :], (ns - 1)[:, None].to(torch.float64))     # padded rows repeat the last sample
    s = keff / (ns - 1)[:, None].to(torch.float64)
    nrm = unit(torch.linalg.cross(u, v)); e2 = unit(torch.linalg.cross(nrm, u)); th = s[:, None, :] * ang[..., None]
    Dd = torch.cos(th)[..., None] * u[:, :, None] + torch.sin(th)[..., None] * e2[:, :, None]
    cs = torch.as_tensor(np.arange(-width / 2, width / 2 + 1e-6, 2.0) / 70.0, device=u.device)
    D = unit(Dd[:, :, :, None, :] * torch.cos(cs)[None, None, None, :, None] + nrm[:, :, None, None, :] * torch.sin(cs)[None, None, None, :, None])
    return D, ns


def disc_xy(rad=HUB_R, step=2.0):
    g = np.arange(-rad, rad + 1e-6, step); X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad ** 2 + 1e-9
    return np.stack([X[keep], Y[keep]], -1)


def plane_frame(k):
    ref = torch.tensor([0.0, 0.0, 1.0], dtype=k.dtype, device=k.device) + 1e-3
    a = unit(torch.linalg.cross(k, ref.expand_as(k))); return a, torch.linalg.cross(k, a)


class Chain:
    """the members of a config batch (one stack order) on one bench's frames"""
    def __init__(self, Bn, pr, inv2, inv3):
        dev = Bn.RS.device; self.C = len(pr["az"])
        p1, p2, p3, ok = kin(Bn.RS, Bn.RHG, pr); self.ok = ok; self.J = dict(J1=p1, J2=p2, J3=p3)
        xy = torch.as_tensor(disc_xy(), device=dev); self.xy = xy
        self.hub = {}
        for name, ax in (("hub1", p1), ("hub2", p2), ("hub3", p3)):
            k = unit(ax); a, b = plane_frame(k); self.hub[name] = (k, a, b)
        end = HUB_R + 2.0 + pr["end_extra"]
        nend = torch.ceil(end / 2.0).long() + 1
        l1_at2, l2_at2 = (STACK, 0.0) if inv2 else (0.0, STACK)
        l2_at3, nk_at3 = (0.0, STACK) if inv3 else (STACK, 0.0)
        over1 = [("link2", 1.0)] if inv2 else []
        over2 = ([] if inv2 else [("link1", 1.0)]) + ([] if inv3 else [("neck", 1.0)])
        overn = [("link2", 1.0)] if inv3 else []
        bar = unit(torch.einsum("pij,j->pi", Bn.RH, torch.as_tensor(BAR0_H / np.linalg.norm(BAR0_H), device=dev)))
        self.straps = {}
        for name, u, v, w, t, joints, ramps, over, ne in (
                ("link1", p1, p2, 12.0, 3.0, ("J1", "J2"), (("hub1", STACK), ("hub2", l1_at2)), over1, nend),
                ("link2", p2, p3, 12.0, 3.0, ("J2", "J3"), (("hub2", l2_at2), ("hub3", l2_at3)), over2, nend),
                ("neck", p3, bar.expand_as(p3), 14.0, 6.0, ("J3",), (("hub3", nk_at3), (None, 0)), overn, torch.full_like(nend, 7))):
            D, ns = strap(u, v, w)
            self.straps[name] = dict(D=D, ns=ns, nc=D.shape[3], NS=D.shape[2], t=t, joints=joints, ramps=ramps, over=over, nend=ne)
        deps = {"link1": over1, "link2": over2, "neck": overn}; order, left = [], ["link1", "neck", "link2"]
        while left:
            for n in left:
                if all(o in order for o, _ in deps[n]): order.append(n); left.remove(n); break
        self.order = ["hub1", "hub2", "hub3"] + order
        self.tk = dict(hub1=CROWN, hub2=CROWN, hub3=CROWN, **{n: self.straps[n]["t"] for n in self.straps})
        self.mj = dict(hub1=("J1",), hub2=("J2",), hub3=("J3",), **{n: self.straps[n]["joints"] for n in self.straps})

    def rays(self, name, ci, pi):
        """K3 rays (origin O, direction D) (n, m, 3) of member `name` for the items (config ci, pose pi)"""
        if name.startswith("hub"):
            k, a, b = (x[ci, pi] for x in self.hub[name]); m = len(self.xy)
            O = self.xy[None, :, :1] * a[:, None, :] + self.xy[None, :, 1:] * b[:, None, :]
            return O, k[:, None, :].expand(-1, m, -1)
        D = self.straps[name]["D"][ci, pi]; D = D.reshape(D.shape[0], -1, 3); return torch.zeros_like(D), D

    def points(self, name, rho, ci, pi):
        """metal sample points (n, m, 3) at the fitted underside rho (C, m) for items (ci, pi)"""
        if name.startswith("hub"):
            O, k = self.rays(name, ci, pi); return rho[ci, :1, None] * k + O
        D = self.straps[name]["D"][ci, pi]; D = D.reshape(D.shape[0], -1, 3); return D * rho[ci][:, :, None]

    def weight(self, name):
        """(C, m) 1 for real samples, 0 for the padding rows of a strap"""
        if name.startswith("hub"): return torch.ones(self.C, len(self.xy), dtype=torch.float64, device=self.xy.device)
        s = self.straps[name]; k = torch.arange(s["NS"], device=self.xy.device)
        w = (k[None, :] < s["ns"][:, None]).to(torch.float64)
        return w[:, :, None].expand(-1, -1, s["nc"]).reshape(self.C, -1)


# ---- K3 march + profiles -------------------------------------------------------------------------------------------
def requirement(Bn, I, O, D, t0=15.0, t1=220.0, clr=2.0, win=15.0):
    """concept_kit.requirement mode 'march' (exact replica of its integer-step logic) for rays (N, 3)"""
    N = len(D); dev = D.device
    t = torch.full((N,), t0, dtype=torch.float64, device=dev); c = t.clone(); chk = torch.zeros(N, dtype=torch.bool, device=dev)
    res = torch.full((N,), float("inf"), dtype=torch.float64, device=dev); act = torch.ones(N, dtype=torch.bool, device=dev)
    a = torch.arange(N, device=dev)
    for _ in range(400):
        if not len(a): break
        ck = chk[a]; x = torch.where(ck, c[a], t[a]); d = Bn.dist(I[a], O[a] + D[a] * x[:, None])
        ta, ca = t[a], c[a]
        s = ~ck; good = s & (d >= clr); sbad = s & ~(d >= clr)
        cbad = ck & (d < 0); cgood = ck & ~(d < 0)
        up_good = ta + torch.clamp(torch.floor(d), min=1.0)
        up_t = ta + torch.clamp(torch.ceil(clr - d - 1e-9), min=1.0)
        up_cbad = ca + torch.clamp(torch.ceil(clr - d - 1e-9), min=1.0)
        up_cgood = ca + torch.clamp(torch.floor(d), min=1.0)
        nchk = torch.where(good, True, torch.where(cbad, False, ck))
        nc = torch.where(good, up_good, torch.where(cgood, up_cgood, ca))
        nt = torch.where(sbad, up_t, torch.where(cbad, up_cbad, ta))
        chk[a] = nchk; c[a] = nc; t[a] = nt
        done = nchk & (nc > nt + win); res[a[done]] = nt[done]
        keep = ~done & ~(nt > t1); act[a[~keep]] = False; a = a[keep]
    return res


def lerp_quantile(R, valid, q):
    """np.quantile(R[valid], q, axis=0) per config: R (C, P, m) (inf = 400), valid (C, P); q (C,) - numpy 'linear'"""
    R = torch.where(torch.isfinite(R), R, torch.full_like(R, 400.0))
    big = torch.where(valid[..., None], R, torch.full_like(R, float("inf")))
    S, _ = torch.sort(big, dim=1); n = valid.sum(1)                       # (C,)
    out = torch.full((R.shape[0], R.shape[2]), 400.0, dtype=R.dtype, device=R.device)
    has = n > 0
    vi = q * (n - 1).to(torch.float64); lo = torch.floor(vi).long(); hi = torch.minimum(lo + 1, (n - 1).clamp(min=0))
    lo = lo.clamp(min=0); g = (vi - lo.to(torch.float64))[:, None]
    A = torch.gather(S, 1, lo[:, None, None].expand(-1, 1, S.shape[2]))[:, 0]
    Bv = torch.gather(S, 1, hi[:, None, None].expand(-1, 1, S.shape[2]))[:, 0]
    diff = Bv - A; L = torch.where(g >= 0.5, Bv - diff * (1 - g), A + diff * g)
    mx = torch.where(valid[..., None], R, torch.full_like(R, -float("inf"))).amax(1)
    L = torch.where((q >= 1)[:, None], mx, L)
    return torch.where(has[:, None], L, out)


def near_mask(da, db, xa, xb, sa, sb, ka, kb, clear=1.0):
    """concept_kit._near (without its prefilter, which only skips poses that cannot be near): items (n, m, 3) x (n, k, 3)"""
    ha, hb = sa, sb                                                 # hw = 1 for every member
    thr = ha + hb.amax(1)[:, None] + clear
    cmin = (1.0 - 0.5 * (thr / xa) ** 2).to(torch.float32)
    dd = torch.bmm(da.to(torch.float32), db.to(torch.float32).transpose(1, 2))
    return (dd > cmin[:, :, None]) & kb[:, None, :] & ka[:, :, None]


def exempt(dirs, x, s, axes):
    """samples outside the 12 mm shared-joint zone (True = checked): dirs (n, m, 3), x, s (n, m), axes [(n, 3)]"""
    keep = torch.ones(x.shape, dtype=torch.bool, device=x.device)
    for k in axes:
        k = unit(k); keep &= torch.arccos(torch.einsum("nmd,nd->nm", dirs, k).clamp(-1, 1)) * x / s > HUB_R + 2
    return keep


def items_chunks(ci, pi, size):
    for o in range(0, len(ci), size): yield ci[o:o + size], pi[o:o + size]


RAYS = int(os.environ.get("GB_RAYS", 0)) or None        # rays per march call (default: 4M on cuda, 256k on cpu)


def fit_profiles(Bn, ch, okf, pr):
    """concept_kit.fit_profiles for the batch: {member: rho (C, m)}"""
    C = ch.C; ci, pi = torch.nonzero(okf, as_tuple=True); raw = {}
    for name in ch.order:
        O, D = ch.rays(name, ci[:1], pi[:1]); m = D.shape[1]
        R = torch.full((C, Bn.P, m), float("inf"), dtype=torch.float64, device=okf.device)
        rays = RAYS or (4_000_000 if okf.is_cuda else 262_144)
        for c0, p0 in items_chunks(ci, pi, max(1, rays // m)):
            O, D = ch.rays(name, c0, p0); n = len(c0)
            r = requirement(Bn, p0[:, None].expand(-1, m).reshape(-1), O.reshape(-1, 3), D.reshape(-1, 3)).reshape(n, m)
            R[c0, p0] = r
        raw[name] = lerp_quantile(R, okf, pr["q"])
    prof, level = {}, {}
    sl = math.tan(60 * D2R)
    order = sorted(ch.order, key=lambda n: (n in ch.straps and len(ch.straps[n]["over"]) > 0, n in ch.straps))
    for name in order:
        r = raw[name].clone()
        if name.startswith("hub"):
            r[:] = r.amax(1, keepdim=True); prof[name] = r; level[name] = r[:, 0]; continue
        s = ch.straps[name]; NS, nc = s["NS"], s["nc"]; sidx = torch.arange(NS, device=r.device).repeat_interleave(nc)
        for (h, dz), first in zip(s["ramps"], (True, False)):
            if not h: continue
            msk = (sidx[None, :] < s["nend"][:, None]) if first else (sidx[None, :] >= (s["ns"] - s["nend"])[:, None])
            r = torch.where(msk, torch.maximum(r, (level[h] + dz)[:, None]), r)
        if s["over"]: r = _over(Bn, ch, name, r, prof, okf, ci, pi)
        R2 = _pad_last(r.reshape(C, NS, nc), s["ns"]); x = torch.arange(NS, device=r.device, dtype=torch.float64) * 2.0
        R2 = (R2[:, None, :, :] - sl * (x[:, None] - x[None, :]).abs()[None, :, :, None]).amax(2)
        prof[name] = _pad_last(R2, s["ns"]).reshape(C, -1); level[name] = prof[name].amax(1)
    return prof


def _pad_last(R2, ns):
    """padding rows (s >= ns) := the last real row (they are duplicates of the last strap sample)"""
    k = torch.arange(R2.shape[1], device=R2.device); idx = torch.minimum(k[None, :], (ns - 1)[:, None])
    return torch.gather(R2, 1, idx[:, :, None].expand(-1, -1, R2.shape[2]))


def _over(Bn, ch, name, r, prof, okf, ci, pi, clear=1.0, item_chunk=1024):
    s = ch.straps[name]; need = torch.full_like(r, -float("inf"))
    for oname, gap in s["over"]:
        shared = set(s["joints"]) & set(ch.mj[oname])
        for c0, p0 in items_chunks(ci, pi, item_chunk):
            da = s["D"][c0, p0].reshape(len(c0), -1, 3); xa = r[c0]; sa = torch.clamp(xa / 70.0, min=1.0)
            po = ch.points(oname, prof[oname], c0, p0); xo = torch.linalg.norm(po, dim=-1); do = po / xo[..., None]
            sb = torch.clamp(xo / 70.0, min=1.0) if not oname.startswith("hub") else torch.ones_like(xo)
            axes = [ch.J[j][c0, p0] for j in shared]
            nm = near_mask(da, do, xa, xb=xo, sa=sa, sb=sb, ka=exempt(da, xa, sa, axes), kb=exempt(do, xo, sb, axes), clear=clear)
            top = torch.where(nm, (xo + ch.tk[oname] + gap)[:, None, :], torch.full_like(nm, -float("inf"), dtype=torch.float64)).amax(2)
            need.index_reduce_(0, c0, top, "amax", include_self=True)
    need = torch.where(torch.isfinite(need), need, torch.zeros_like(need))
    return torch.maximum(r, need)


# ---- K6 + scoring --------------------------------------------------------------------------------------------------
def collisions(ch, pts, ok, overlap, clear=1.0, item_chunk=512):
    """concept_kit.collisions for the batch: pts {member: (C, P, m, 3)} -> hit (C, P)"""
    hit = torch.zeros_like(ok); ci, pi = torch.nonzero(ok, as_tuple=True); M = ch.order
    if not len(ci): return hit
    for ia in range(len(M)):
        for ib in range(ia + 1, len(M)):
            A, Bm = M[ia], M[ib]; shared = set(ch.mj[A]) & set(ch.mj[Bm]); tA, tB = ch.tk[A], ch.tk[Bm]
            for c0, p0 in items_chunks(ci, pi, item_chunk):
                XA, XB = pts[A][c0, p0], pts[Bm][c0, p0]; xa, xb = torch.linalg.norm(XA, dim=-1), torch.linalg.norm(XB, dim=-1)
                da, db = XA / xa[..., None], XB / xb[..., None]
                sa = torch.ones_like(xa) if A.startswith("hub") else torch.clamp(xa / 70.0, min=1.0)
                sb = torch.ones_like(xb) if Bm.startswith("hub") else torch.clamp(xb / 70.0, min=1.0)
                axes = [ch.J[j][c0, p0] for j in shared]
                nm = near_mask(da, db, xa, xb, sa, sb, exempt(da, xa, sa, axes), exempt(db, xb, sb, axes), clear)
                ov = (xa[:, :, None] < xb[:, None, :] + tB + overlap) & (xb[:, None, :] < xa[:, :, None] + tA + overlap)
                h = (nm & ov).flatten(1).any(1)
                hit[c0[h], p0[h]] = True
    return hit


def crown_pts(ch, name, F0, ci, pi):
    k, a, b = (x[ci, pi] for x in ch.hub[name]); f = F0[ci][:, None, None]; xy = ch.xy
    crown = (f + CROWN) * k[:, None, :] + xy[None, :, :1] * a[:, None, :] + xy[None, :, 1:] * b[:, None, :]
    ang = torch.linspace(0, 2 * math.pi, N_WALL + 1, dtype=torch.float64, device=k.device)[:-1]
    c, s = HUB_R * torch.cos(ang), HUB_R * torch.sin(ang)
    wall = [(f + h) * k[:, None, :] + c[None, :, None] * a[:, None, :] + s[None, :, None] * b[:, None, :] for h in CROWN_LEVELS]
    return torch.cat([crown] + wall, 1)


def score(Bw, ch, prof, okw, overlap, item_chunk=1024):
    """wear: collisions, skin faces / crowns / tops, metrics -> dict of (C,) tensors"""
    C, P = okw.shape; dev = okw.device
    ci, pi = torch.nonzero(okw, as_tuple=True)
    pts = {}
    for n in ch.order:
        m = prof[n].shape[1]; X = torch.zeros((C, P, m, 3), dtype=torch.float64, device=dev)
        for c0, p0 in items_chunks(ci, pi, 8192): X[c0, p0] = ch.points(n, prof[n], c0, p0)
        pts[n] = X
    hit = collisions(ch, pts, okw, overlap)
    take = okw & ~hit
    W = torch.cat([ch.weight(n) for n in ch.order], 1)                       # (C, M)
    fmin = torch.full((C, P), float("inf"), dtype=torch.float64, device=dev); cmin = fmin.clone(); tmin = fmin.clone()
    in14 = torch.zeros((C, P), dtype=torch.float64, device=dev); in10 = in14.clone()
    ci, pi = torch.nonzero(take, as_tuple=True)
    for c0, p0 in items_chunks(ci, pi, item_chunk):
        X = torch.cat([pts[n][c0, p0] for n in ch.order], 1); n_, m_ = X.shape[:2]
        d = Bw.dist(p0[:, None].expand(-1, m_).reshape(-1), X.reshape(-1, 3)).reshape(n_, m_)
        fmin[c0, p0] = d.amin(1); w = W[c0]
        in14[c0, p0] = (w * ((d >= 2) & (d <= 14))).sum(1); in10[c0, p0] = (w * ((d >= 2) & (d <= 10))).sum(1)
        CR = torch.cat([crown_pts(ch, h, prof[h][:, 0], c0, p0) for h in ("hub1", "hub2", "hub3")], 1)
        dc = Bw.dist(p0[:, None].expand(-1, CR.shape[1]).reshape(-1), CR.reshape(-1, 3)).reshape(n_, -1)
        cmin[c0, p0] = dc.amin(1)
        tops = []
        for n in ch.order:
            Xn = pts[n][c0, p0]; nn = torch.linalg.norm(Xn, dim=-1, keepdim=True); tops.append(Xn * (nn + ch.tk[n]) / nn)
        T = torch.cat(tops, 1); dt = Bw.dist(p0[:, None].expand(-1, T.shape[1]).reshape(-1), T.reshape(-1, 3)).reshape(n_, -1)
        tmin[c0, p0] = dt.amin(1)
    good = take & (fmin >= 0) & (cmin >= 0) & (tmin >= 0)
    clip, ws = Bw.clip[None, :], Bw.ws[None, :]
    reach = (good & ws).sum(1) / ws.sum(); follow = (good & clip).sum(1) / clip.sum()
    nw = (good & clip).to(torch.float64) * W.sum(1, keepdim=True)
    den = nw.sum(1); ib14 = torch.where(den > 0, (in14 * (good & clip)).sum(1) / den.clamp(min=1e-9), torch.zeros_like(den))
    ib10 = torch.where(den > 0, (in10 * (good & clip)).sum(1) / den.clamp(min=1e-9), torch.zeros_like(den))
    ntake = take.sum(1); contact = torch.where(ntake > 0, (take & ~((fmin >= 0) & (cmin >= 0) & (tmin >= 0))).sum(1) / ntake.clamp(min=1), torch.zeros_like(reach))
    # audit: median nearest-neighbour spacing of every member's points at the first taken (else closing) pose <= 4 mm
    sel = torch.where(take.any(1, keepdim=True), take, okw); i0 = torch.where(sel.any(1), sel.to(torch.int64).argmax(1), torch.zeros(C, dtype=torch.int64, device=dev))
    sparse = torch.zeros(C, dtype=torch.bool, device=dev); ar = torch.arange(C, device=dev)
    for n in ch.order:
        X = pts[n][ar, i0]
        if not okw[ar, i0].all():                                               # pose 0 not closing: rebuild its points
            X = ch.points(n, prof[n], ar, i0)
        w = ch.weight(n) > 0; D2 = ((X[:, :, None, :] - X[:, None, :, :]) ** 2).sum(-1)
        eye = torch.eye(X.shape[1], dtype=torch.bool, device=dev)[None]
        D2 = torch.where(eye | ~w[:, None, :], torch.full_like(D2, float("inf")), D2)
        nn = torch.sqrt(D2.amin(2)); nn = torch.where(w, nn, torch.full_like(nn, float("nan")))
        med = torch.nanquantile(nn, 0.5, dim=1)
        sparse |= torch.round(med * 100) / 100 > 4.0
    hubF = torch.stack([prof[h][:, 0] for h in ("hub1", "hub2", "hub3")], 1)
    return dict(reach=reach, follow=follow, inband14=ib14, inband10=ib10, contact=contact, sparse=sparse, hubF=hubF,
                ok=okw.to(torch.float64).mean(1), collide=torch.where(okw.any(1), (hit & okw).sum(1) / okw.sum(1).clamp(min=1), torch.zeros_like(reach)))


def gap_of(ib14, follow, reach, contact):
    return round(100 * (max(0.0, .90 - ib14) + max(0.0, .95 - follow) + max(0.0, .90 - reach)) + 100 * contact, 2)


# ---- driver --------------------------------------------------------------------------------------------------------
def evaluate(configs, Bw, Bf=None, chunk=48, overlap=1.0 - 1e-4, log=None):
    """configs: list of param dicts (zc-frontier-3r's). Bw = wear bench, Bf = fit bench (None = same bench). -> rows"""
    Bf = Bf or Bw; dev = Bw.RS.device; out = [None] * len(configs); ps = [snap(c) for c in configs]
    todo = []
    for i, p in enumerate(ps):
        if not seat_ok(p["az"], p["el"]): out[i] = dict(params=p, gap=200.0, honest=False, audit=["J1 seat outside the back / acromion-top region (ruling 4)"])
        else: todo.append(i)
    groups = {}
    for i in todo: groups.setdefault((ps[i]["inv2"], ps[i]["inv3"]), []).append(i)
    for (inv2, inv3), idx in groups.items():
        for o in range(0, len(idx), chunk):
            ii = idx[o:o + chunk]; t0 = time.time()
            pr = {k: torch.tensor([float(ps[i][k]) for i in ii], dtype=torch.float64, device=dev)
                  for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "q", "end_extra")}
            Bw.outside = Bf.outside = 0
            chf = Chain(Bf, pr, inv2, inv3); okf = continuity(Bf, pr, chf.ok)
            prof = fit_profiles(Bf, chf, okf, pr)
            if Bf is Bw: chw, okw = chf, okf
            else:
                chw = Chain(Bw, pr, inv2, inv3); okw = continuity(Bw, pr, chw.ok)
                for n in chw.straps:
                    if chw.straps[n]["NS"] != chf.straps[n]["NS"] or not torch.equal(chw.straps[n]["ns"], chf.straps[n]["ns"]):
                        raise ValueError(f"{n}: strap sample count differs between the fit and the wear bench")
            S = score(Bw, chw, prof, okw, overlap)
            S = {k: v.cpu().numpy() for k, v in S.items()}
            for a, i in enumerate(ii):
                r = {k: round(float(S[k][a]), 4) for k in ("reach", "follow", "inband14", "inband10", "contact")}
                v = gap_of(r["inband14"], r["follow"], r["reach"], r["contact"])
                hubF = [round(float(x), 2) for x in S["hubF"][a]]; hub_ok = all(x <= 140.0 for x in hubF); honest = not bool(S["sparse"][a])
                out[i] = dict(params=ps[i], gap=round(v + (0.0 if (honest and hub_ok) else 100.0), 2), v_gap=v, honest=honest and hub_ok,
                              sparse=bool(S["sparse"][a]), hub_F=hubF, hub_F_ok=hub_ok, closure_k2=round(float(S["ok"][a]), 4),
                              collide=round(float(S["collide"][a]), 4), outside=int(Bw.outside + Bf.outside), **r)
            if log: log(f"  group inv2={inv2} inv3={inv3}: {len(ii)} configs in {time.time() - t0:.1f} s")
    return out


# ---- CPU reference (the kit model itself) --------------------------------------------------------------------------
def cpu_eval(args):
    """zc-frontier-3r evaluate on the CPU (fast cache); frozen: fit bench -> fixed_prof -> wear bench"""
    p, wear, fit = args
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    import importlib.util
    if "zcm" not in globals():
        spec = importlib.util.spec_from_file_location("zc_model_ref", os.path.join(REPO, "docs", "concepts", "models", "zc-frontier-3r.py"))
        m = importlib.util.module_from_spec(spec); sys.modules["zc_model_ref"] = m; spec.loader.exec_module(m); globals()["zcm"] = m
        globals()["_benches"] = {}
    M = globals()["zcm"]; BB = globals()["_benches"]
    get = lambda nb: BB.setdefault(nb, M.K.bench(*nb))
    t = time.time(); prof = None
    if fit and tuple(fit) != tuple(wear):
        Bf = get(tuple(fit)); _, rf = M.evaluate(Bf, dict(p))
        prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()} if "chain" in getattr(Bf, "_kit_last", {}) and rf.get("gap", 0) < 200 else None
    Bw = get(tuple(wear)); _, r = M.evaluate(Bw, dict(p), fixed_prof=prof)
    keep = ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "hub_F")
    return {k: r.get(k) for k in keep} | dict(v_gap=(r.get("v") or {}).get("gap"), secs=round(time.time() - t, 2), mode=Bw.mode)


def random_configs(n, seed=0):
    """configs inside the rulings (seat region, bounds), biased to the closing region of the fold law"""
    rng = np.random.default_rng(seed); out = []
    while len(out) < n:
        p = dict(az=rng.uniform(-110, 135), el=rng.uniform(-20, 90), a1=rng.uniform(25, 110), a2=rng.uniform(30, 120),
                 wd=rng.uniform(40, 150), wa=rng.uniform(-180, 180), sigma=int(rng.choice([-1, 1])), q=float(rng.uniform(0.85, 1.0)),
                 end_extra=float(rng.uniform(0, 6)), inv2=int(rng.random() < 0.25), inv3=int(rng.random() < 0.25))
        if seat_ok(p["az"], p["el"]): out.append(p)
    return out


LEADERS = [  # spine-parked k7008's axes at O20 / margin 5 (zc start), the spine-parked polish, fold-sph3r / raglan bests
    dict(PARAMS),
    dict(az=105.4303, el=66.9934, a1=38.2422, a2=73.7679, wd=88.0898, wa=-13.2634, q=0.9838, end_extra=0.2905, sigma=-1, inv2=0, inv3=0),
    dict(az=28.338, el=65.3972, a1=83.5065, a2=62.9048, wd=94.3254, wa=-9.3721, sigma=-1, q=0.9805, end_extra=0.0, inv2=0, inv3=0),
    dict(az=8.6354, el=81.5826, a1=79.7193, a2=61.5935, wd=94.1683, wa=-0.8536, sigma=-1, q=1.0, end_extra=0.0, inv2=0, inv3=0),
]


def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("args", nargs="*")
    ap.add_argument("--bench", default="110,360"); ap.add_argument("--fit", default=None); ap.add_argument("--chunk", type=int, default=48)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu"); ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--out"); ap.add_argument("--procs", type=int, default=4); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--leaders", action="store_true"); ap.add_argument("--extra")
    a = ap.parse_args()
    wear = tuple(int(x) for x in a.bench.split(",")); fit = tuple(int(x) for x in a.fit.split(",")) if a.fit else None
    if a.cmd == "pack":
        print(make_pack(int(a.args[0]), int(a.args[1]))); return
    log = lambda s: print(s, flush=True)
    t = time.time(); Bw = GBench(*wear, device=a.device); Bf = GBench(*fit, device=a.device) if fit and fit != wear else None
    log(f"benches on {a.device} in {time.time() - t:.1f} s (grid {Bw.G.numel() / 1e9:.2f} G voxels)")
    if a.cmd == "eval":
        cf = json.load(open(a.args[0])); t = time.time(); rows = evaluate(cf, Bw, Bf, a.chunk, log=log)
        json.dump(dict(bench=list(wear), fit=list(fit) if fit else None, device=a.device, secs=round(time.time() - t, 2), rows=rows),
                  open(a.args[1], "w"), indent=1)
        log(f"{len(cf)} configs in {time.time() - t:.1f} s")
    elif a.cmd == "speed":
        cf = random_configs(a.n, a.seed + 7)
        evaluate(cf[:8], Bw, Bf, a.chunk)                                # warm-up
        if a.device == "cuda": torch.cuda.synchronize()
        t = time.time(); evaluate(cf, Bw, Bf, a.chunk, log=log)
        if a.device == "cuda": torch.cuda.synchronize()
        dt = time.time() - t; res = dict(n=len(cf), secs=round(dt, 2), evals_per_s=round(len(cf) / dt, 3), device=a.device, chunk=a.chunk,
                                        gpu=torch.cuda.get_device_name(0) if a.device == "cuda" else None, bench=list(wear), fit=list(fit) if fit else None)
        log(json.dumps(res))
        if a.out: json.dump(res, open(a.out, "w"), indent=1)
    elif a.cmd == "parity":
        cf = random_configs(a.n, a.seed) + (LEADERS if a.leaders else [])
        if a.extra: cf += json.load(open(a.extra))
        t = time.time(); g = evaluate(cf, Bw, Bf, a.chunk, log=log); tg = time.time() - t
        log(f"GPU {len(cf)} configs in {tg:.1f} s")
        import multiprocessing as mp
        t = time.time()
        with mp.get_context("fork").Pool(a.procs) as pool:
            c = pool.map(cpu_eval, [(p, wear, fit) for p in cf], chunksize=1)
        tc = time.time() - t; log(f"CPU {len(cf)} configs in {tc:.1f} s on {a.procs} processes")
        keys = ("gap", "reach", "follow", "inband14", "inband10", "contact")
        diff = {k: [abs(float(x[k]) - float(y[k])) for x, y in zip(g, c) if x.get(k) is not None and y.get(k) is not None] for k in keys}
        rows = [dict(params=x["params"], gpu={k: x.get(k) for k in keys + ("honest", "hub_F", "outside")}, cpu=y) for x, y in zip(g, c)]
        summ = dict(n=len(cf), bench=list(wear), fit=list(fit) if fit else None, max_abs_diff={k: round(max(v), 4) if v else None for k, v in diff.items()},
                    n_gap_diff_gt_1=sum(1 for v in diff["gap"] if v > 1.0), gpu_secs=round(tg, 2), cpu_secs=round(tc, 2), cpu_procs=a.procs,
                    cpu_secs_per_config_per_proc=round(tc * a.procs / len(cf), 2), device=a.device)
        log(json.dumps(summ))
        if a.out: json.dump(dict(summary=summ, rows=rows), open(a.out, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()

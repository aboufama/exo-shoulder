#!/usr/bin/env python3
"""GPU (torch) port of the PIN-KNEE family's bench path: docs/concepts/models/skin-normal-3r-pin-knee.py (J1 / J2 on GH-ray
seats, J3 on a tilted skin seat b3, member 3 = hub 3's lower plate + E strap + E boss, the planar two-pin knee closed in
closed form, the arm pad on the cuff) + its adversarial verifier's checks (docs/concepts/verify/skin-normal-3r-pin-knee.py
extra_checks) + the model's near-touch audit, evaluated exactly as tools/knee_polish.py evaluates a configuration.

    python3 tools/gpu_bench_knee.py eval CFGS.json OUT.json [--bench 110,360] [--fit 60,160] [--margin 5] [--device cuda]
    python3 tools/gpu_bench_knee.py parity --n 50 --bench 110,360 [--fit 60,160] --out P.json [--procs 12] [--leaders]
    python3 tools/gpu_bench_knee.py speed --n 64 --bench 110,360 [--workers 12]
    python3 tools/gpu_bench_knee.py cma <tools/knee_polish.py cma arguments>     knee_polish's CMA, evaluated on the device
    python3 tools/gpu_bench_knee.py table P1.json [P2.json]                      markdown parity rows
(docs/research/golden/README.md "Pin-knee port": parity 0.0 on 53-54 configs x 2 protocols; ~0.26-0.9 s per config vs
~8-11 s for the kit; pod jobs pipeline/gpu_pod/knee*.sh)

How (an accelerated kit, not a re-model): the CPU kit's own code builds every configuration - the seats on the rest skin
(libigl), the spherical IK, the knee closure and its window, 10 fps continuity, the part geometry (_geo, the link straps,
the E profile, finalize, contact-only samples, solids), the greedy pose drop, the report, the near-touch audit and the
knee_polish objective - and this file replaces ONLY the per-pose loops with batched torch code on the device:
  * S.Model.needed (the sphere-traced skin requirement of every sample in every pose, the 1-Lipschitz trace with its
    per-pose break rule, the inside-at-start BIG rule, the slab test against the knee / pad boxes for link 2),
  * the model's run loop (_run_batched: part-part clearance of every non-adjacent pair incl. the adjacent 0.15 mm pairs
    E-L2 / knee-hub 3 / knee-E, the jam rule, metal + contact-only distances, B.res, cmin, why),
  * the verifier's extra_checks (independent 3D closure, knee vs hub 3's upper half, the E boss vs hubs / links),
  * Bench.dist: concept_bench's trilinear formula on the int8 grid (same corner order, float32 corners x float64
    weights), points outside the +-260 mm box handed to the kit's exact (libigl) path.
Plus two bit-identical CPU-side speed-ups (GBK_FAST_CPU=1, default): the seats' rest-skin libigl trees built once
(ExactCached) and the IK's per-frame rotations batched (ik_vec); and raglan-knee-3r's routed links (r1t / r1d / r2t /
r2d / rc) installed on the verifier's model in the port AND the CPU reference.
Margin = the fold margin (CB_FOLD_MARGIN, set before the kit is imported; 5 = the user's ruling). Hubs: O20 only.
Protocols: same-bench (fit = wear) or frozen (fit on --fit, worn on --bench without refit = knee_polish.frozen_on).
"""
import json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1", "gap_near2", "model_gap")
ANT_MAX = 0.20
_MOD = {}


def kit(margin=None):
    """import the CPU kit (knee_polish -> verifier -> model -> seed) once, at the requested fold margin"""
    if "KP" in _MOD: return _MOD["KP"]
    if margin is not None: os.environ["CB_FOLD_MARGIN"] = str(float(margin))
    os.environ.setdefault("CB_QUIET_EXACT", "1")
    import knee_polish as KP
    KP.verifier(); _MOD["KP"] = KP
    _route(KP)
    return KP


def _route(KP):
    """raglan-knee-3r's routed links (r1t / r1d / r2t / r2d / rc) on the verifier's pin-knee model: the raglan model's own
    routed_add_links (docs/concepts/models/raglan-knee-3r.py, loaded as a private copy) whenever |r1d| or |r2d| >= 0.25,
    else the pin knee's own great-circle links bit for bit (the same dispatch the raglan model installs on its copy).
    Installed in the port AND in the CPU reference, so both evaluate the same kit code."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("raglan_for_port", os.path.join(REPO, "docs", "concepts", "models", "raglan-knee-3r.py"))
    RG = importlib.util.module_from_spec(spec); spec.loader.exec_module(RG); _MOD["RG"] = RG
    MKm = KP.verifier().MK; base = MKm._Geo.add_links
    def add_links(self, f1, f2, f3):
        if all(abs(float(self.D.p.get(k, 0.0) or 0.0)) < 0.25 for k in ("r1d", "r2d")): return base(self, f1, f2, f3)
        return RG.routed_add_links(self, f1, f2, f3)
    MKm._Geo.add_links = add_links


def prep(p):
    """raglan route parameters clamped as raglan-knee-3r.clean does (only when present)"""
    q = dict(p)
    for k in ("r1t", "r2t"):
        if k in q: q[k] = min(0.85, max(0.15, float(q[k])))
    for k in ("r1d", "r2d"):
        if k in q: q[k] = min(60.0, max(-60.0, float(q[k])))
    if "rc" in q: q["rc"] = min(40.0, max(6.0, float(q["rc"])))
    return q


# ---- the device grid (concept_bench.Bench.dist) -----------------------------------------------------------------------
class GridDev:
    def __init__(self, B, device, G=None):
        import torch
        self.torch = torch; self.B = B; self.dev = device
        import concept_bench as CB
        self.HALF, self.H, self.Q = CB.HALF, CB.H_GRID, CB.Q
        g = B.grid; self.n = int(g.shape[1]); self.P = int(g.shape[0])
        if G is not None: self.G = G
        else:
            self.G = torch.empty(g.size, dtype=torch.int8, device=device); step = 32; n3 = self.n ** 3
            for i in range(0, g.shape[0], step):
                a = torch.from_numpy(np.array(g[i:i + step]).reshape(-1))   # a writable copy of the memmap slice; self.G[i * n3:i * n3 + a.numel()] = a.to(device)
        self.outside = 0

    def dist(self, I, X):
        """I (N,) long pose index, X (N, 3) float64 -> (N,) float64, = Bench.dist"""
        torch = self.torch; n = self.n
        g = (X + self.HALF) / self.H
        ins = ((g >= 0) & (g <= n - 1 - 1e-9)).all(-1)
        out = torch.empty(X.shape[0], dtype=torch.float64, device=X.device)
        if bool(ins.any()):
            gi = g[ins]; i0f = torch.floor(gi); f = gi - i0f; i0 = i0f.long(); Ii = I[ins]
            fx, fy, fz = f.unbind(-1); x0, y0, z0 = i0.unbind(-1)
            base = ((Ii * n + x0) * n + y0) * n + z0
            def c(dx, dy, dz): return self.G[base + (dx * n + dy) * n + dz].to(torch.float32).to(torch.float64)
            v = (c(0, 0, 0) * (1 - fx) * (1 - fy) * (1 - fz) + c(1, 0, 0) * fx * (1 - fy) * (1 - fz) + c(0, 1, 0) * (1 - fx) * fy * (1 - fz)
                 + c(0, 0, 1) * (1 - fx) * (1 - fy) * fz + c(1, 1, 0) * fx * fy * (1 - fz) + c(1, 0, 1) * fx * (1 - fy) * fz
                 + c(0, 1, 1) * (1 - fx) * fy * fz + c(1, 1, 1) * fx * fy * fz)
            out[ins] = v * self.Q
        if not bool(ins.all()):
            J = torch.nonzero(~ins)[:, 0]; Ic = I[J].cpu().numpy(); Xc = X[J].cpu().numpy(); o = np.empty(len(J)); self.outside += len(J)
            for i in np.unique(Ic):
                m = Ic == i; o[m] = self.B._exact(int(i), Xc[m])
            out[J] = torch.as_tensor(o, dtype=torch.float64, device=X.device)
        return out


# ---- member transforms of a model, all bench poses at once (numpy, the model's T(m, i) arithmetic) ---------------------
def transforms(M):
    if getattr(M, "_Tall", None) is not None and M._Tall[0] is M.K: return M._Tall[1]
    MKS = _MOD["KP"].verifier().MK
    D = M.D; Q = M.Q; n = len(Q); s = M.s; K = M.K; c3 = D.c[2]
    out = {0: (np.broadcast_to(np.eye(3), (n, 3, 3)).copy(), np.zeros((n, 3)))}
    for m in (1, 2): R, t = M.X[m]; out[m] = (np.asarray(R, float), np.asarray(t, float))
    out[5] = (Q.copy(), np.zeros((n, 3)))
    sv = s[:, 0, None] * D.sa + s[:, 1, None] * D.st + s[:, 2, None] * D.sn
    Rp = MKS.rodr(D.sn, K["phi"]); R3 = Q @ Rp
    t3 = (Q @ (c3[None] + sv - (Rp @ c3))[..., None])[..., 0]
    out[3] = (R3, t3)
    Rd = MKS.rodr(D.sn, MKS.wrap(K["psi"] - D.p["phib"] * MKS.D2R))
    pa = D.p3(K["pa"]) + s[:, 2, None] * D.sn; A0 = D.p3(K["A0"])[0]
    out[6] = (Q @ Rd, (Q @ (pa - Rd @ A0)[..., None])[..., 0])
    M._Tall = (K, out)
    return out


def T_dev(M, dev):
    import torch
    key = ("_Tdev", str(dev))
    if getattr(M, "_Tdk", None) is not None and M._Tdk[0] is M.K and M._Tdk[1] == key: return M._Tdk[2]
    Tn = transforms(M)
    out = {m: (torch.as_tensor(R, dtype=torch.float64, device=dev), torch.as_tensor(t, dtype=torch.float64, device=dev)) for m, (R, t) in Tn.items()}
    out["RS"] = torch.as_tensor(np.asarray(M.RS, float), dtype=torch.float64, device=dev)
    M._Tdk = (M.K, key, out)
    return out


def _apply(R, t, X):
    """X (k, 3) home or (n, k, 3) -> (n, k, 3) = X @ R.T + t per pose"""
    if X.dim() == 2: X = X[None].expand(R.shape[0], -1, -1)
    return X @ R.transpose(1, 2) + t[:, None, :]


# ---- S.Model.needed, batched over poses ---------------------------------------------------------------------------------
def needed(self, items, poses, iters=16, lift_max=35.0):
    import torch
    S = _MOD["KP"].verifier().MK.S
    gd = self.B._gd; dev = gd.dev; Td = T_dev(self, dev)
    sizes = [len(it[1]) for it in items]; cut = np.cumsum([0] + sizes); Mt = int(cut[-1])
    boxes_of = [it[4] if len(it) > 4 else () for it in items]
    BpN = [(int(it[0]), torch.as_tensor(np.asarray(it[1], float), device=dev), torch.as_tensor(np.asarray(it[2], float), device=dev)) for it in items]

    def points(pi, h):
        """pi (n,) bench pose indices (long), h (n, Mt) -> world points (n, Mt, 3)"""
        blocks = []
        for k, (m, Bp, N) in enumerate(BpN):
            hk = h[:, cut[k]:cut[k + 1]]
            X = Bp[None] + hk[..., None] * N[None]
            R, t = Td[m]; blocks.append(_apply(R[pi], t[pi], X))
        P = torch.cat(blocks, 1)
        return P @ Td["RS"][pi].transpose(1, 2)

    def trace(pi, h, active):
        n = len(pi); done = torch.zeros(n, dtype=torch.bool, device=dev); ins0 = None
        for it_ in range(iters):
            a = torch.nonzero(~done)[:, 0]
            if not len(a): break
            P = points(pi[a], h[a]); I = pi[a][:, None].expand(-1, Mt).reshape(-1)
            d = gd.dist(I, P.reshape(-1, 3)).reshape(len(a), Mt) - S.CLEAR
            if it_ == 0 and active: ins0 = d < -S.CLEAR
            step = d - 0.05; h[a] = h[a] - step
            done[a] = step.abs().amax(1) < 0.05
        if any(boxes_of):
            bx = boxes_dev(self, pi, self._tr_fit, dev)
            for k, names in enumerate(boxes_of):
                if not names: continue
                m, Bp, N = BpN[k]; R_, t_ = Td[m]; R_ = R_[pi]; t_ = t_[pi]
                o = _apply(R_, t_, Bp); nv = N[None].expand(len(pi), -1, -1) @ R_.transpose(1, 2)
                for nm in names:
                    cen, R, half = bx[nm]; hh = half + S.PART_CLEAR + 0.6
                    ol = (o - cen[:, None, :]) @ R; nl = nv @ R; nl = torch.where(nl.abs() < 1e-9, torch.full_like(nl, 1e-9), nl)
                    t1 = (-hh - ol) / nl; t2 = (hh - ol) / nl
                    tn = torch.minimum(t1, t2).amax(-1); tf = torch.maximum(t1, t2).amin(-1); hit = tn <= tf
                    hs = h[:, cut[k]:cut[k + 1]]
                    h[:, cut[k]:cut[k + 1]] = torch.where(hit, torch.maximum(hs, tf), hs)
        return h, ins0

    poses = np.asarray(poses); rest = min(poses, key=lambda i: self.B.poses[i]["elev"])
    h0 = torch.as_tensor(np.concatenate([np.full(n, it[3]) for it, n in zip(items, sizes)]), dtype=torch.float64, device=dev)[None].clone()
    h_rest, _ = trace(torch.as_tensor([int(rest)], device=dev), h0, False)
    pi = torch.as_tensor(poses.astype(np.int64), device=dev)
    h = (h_rest + lift_max).expand(len(pi), -1).clone()
    h, ins = trace(pi, h, True)
    H = torch.where(ins, torch.full_like(h, S.BIG), h).cpu().numpy()
    return [H[:, cut[k]:cut[k + 1]] for k in range(len(items))]


def boxes_dev(M, pi, tr, dev):
    """MK.Model._boxes_at (knee link + arm pad boxes) for the poses pi at knee level tr: {name: (cen (n,3), R (n,3,3), half (3,))}"""
    import torch
    MKm = _MOD["KP"].verifier().MK; S = MKm.S
    D = M.D; P = D.p; tp = P["tp"]; fr = M.fr; lc = float(P["lc"]); Td = T_dev(M, dev)
    T = lambda x: torch.as_tensor(np.asarray(x, float), dtype=torch.float64, device=dev)
    Rk = np.stack([fr["eK"], fr["nK"], D.sn], 1); ck = fr["A0m"] + (lc / 2) * fr["eK"] + (tr + tp + S.RUN + tp / 2) * D.sn
    R, t = Td[6]; R = R[pi]; t = t[pi]
    out = {"knee": ((R @ T(ck)) + t, R @ T(Rk), T([lc / 2 + MKm.BOSS_R, MKm.KNEE_W / 2, tp / 2]))}
    Rp = np.stack([D.sa, D.st, D.sn], 1); cp = fr["Bm"] + (tr + tp / 2) * D.sn
    R, t = Td[5]; R = R[pi]; t = t[pi]
    out["pad"] = ((R @ T(cp)) + t, R @ T(Rp), T([MKm.PAD_R, MKm.PAD_R, tp / 2]))
    return out


# ---- signed distances to solids, batched ------------------------------------------------------------------------------
def sd_cylr(Pw, cen, ax, r, h):
    """Pw (n, k, 3), cen / ax (n, 3) -> (n, k)"""
    import torch
    w = Pw - cen[:, None, :]; z = (w * ax[:, None, :]).sum(-1); rr = torch.linalg.norm(w - z[..., None] * ax[:, None, :], dim=-1)
    dr = rr - r; dz = torch.maximum(-z, z - h)
    return torch.where((dr > 0) | (dz > 0), torch.hypot(dr.clamp(min=0), dz.clamp(min=0)), torch.maximum(dr, dz))


def sd_box(Pw, cen, R, half):
    import torch
    w = (Pw - cen[:, None, :]) @ R; q = w.abs() - half
    return torch.linalg.norm(q.clamp(min=0), dim=-1) + q.amax(-1).clamp(max=0)


def nn_min(A, Bq, ma=None, mb=None, chunk=64):
    """min over pairs of |a - b| per pose (n,), masks (n, ka) / (n, kb) (False = left out); inf when nothing is left"""
    import torch
    n = A.shape[0]; out = torch.full((n,), float("inf"), dtype=torch.float64, device=A.device)
    if A.shape[1] == 0 or Bq.shape[1] == 0: return out
    for o in range(0, n, chunk):
        a, b = A[o:o + chunk], Bq[o:o + chunk]
        d = torch.sqrt(((a[:, :, None, :] - b[:, None, :, :]) ** 2).sum(-1))
        if ma is not None: d = torch.where(ma[o:o + chunk][:, :, None], d, torch.full_like(d, float("inf")))
        if mb is not None: d = torch.where(mb[o:o + chunk][:, None, :], d, torch.full_like(d, float("inf")))
        out[o:o + chunk] = d.flatten(1).amin(1)
    return out


def _far(X, cen, ax, r):
    w = X - cen[:, None, :]; z = (w * ax[:, None, :]).sum(-1)
    import torch
    return torch.linalg.norm(w - z[..., None] * ax[:, None, :], dim=-1) > r


def collide_all(M, pi, dev):
    """MK.Model.collide for the poses pi: (clear (n,) numpy, names list, values (n, k) numpy incl. adjacent entries)"""
    import torch
    MKm = _MOD["KP"].verifier().MK; S = MKm.S
    Td = T_dev(M, dev); n = len(pi); h = S.T_LINK / 2; INF = float("inf")
    TT = lambda x: torch.as_tensor(np.asarray(x, float), dtype=torch.float64, device=dev)
    def tf(m, X): R, t = Td[m]; return _apply(R[pi], t[pi], TT(X))
    cyl = {}
    for k, (m, cen, ax) in M.cyl.items():
        R, t = Td[m]; cyl[k] = ((R[pi] @ TT(cen)) + t[pi], R[pi] @ TT(ax))
    surf = {k: tf(m, X) for k, (m, X) in M.cyl_surf.items()}
    strap = {k: tf(m, X) for k, (m, X) in M.strap.items()}
    Em = tf(*M.Emid)
    bx = boxes_dev(M, pi, M.tr, dev)
    big = torch.full((n,), 1e9, dtype=torch.float64, device=dev)
    def vcyl(X, nm, extra=0.0):
        if X.shape[1] == 0: return big
        return sd_cylr(X, *cyl[nm], M.cyl_r[nm], S.CROWN).amin(1) - extra
    def vbox(X, nm, extra=0.0):
        if X.shape[1] == 0: return big
        cen, R, half = bx[nm]; return sd_box(X, cen, R, half).amin(1) - extra
    c = {}
    c["L2-hub1"] = vcyl(strap["L2"], "hub1", h); c["hub3-hub1"] = vcyl(surf["hub3"], "hub1"); c["L1-hub3"] = vcyl(strap["L1"], "hub3", h)
    c["hub2-hub3"] = vcyl(surf["hub2"], "hub3"); c["hub1-hub2"] = torch.full((n,), float(M.hub12()), dtype=torch.float64, device=dev)
    cen2, ax2 = cyl["hub2"]
    fa = _far(strap["L1"], cen2, ax2, M.hr[1] + 4); fb = _far(strap["L2"], cen2, ax2, M.hr[1] + 4)
    v = nn_min(strap["L1"], strap["L2"], fa, fb)
    c["L1-L2"] = torch.where(torch.isfinite(v), v - 2 * h, torch.full_like(v, INF))
    for nm in ("knee", "pad"):
        c[f"{nm}-hub1"] = vbox(surf["hub1"], nm); c[f"{nm}-hub2"] = vbox(surf["hub2"], nm)
        c[f"{nm}-L1"] = vbox(strap["L1"], nm, h); c[f"{nm}-L2"] = vbox(strap["L2"], nm, h)
    c["pad-hub3"] = vbox(surf["hub3"], "pad"); c["pad-E"] = vbox(Em, "pad", h)
    c["E-hub1"] = vcyl(Em, "hub1", h); c["E-hub2"] = vcyl(Em, "hub2", h)
    if strap["L1"].shape[1]: c["E-L1"] = nn_min(Em, strap["L1"]) - 2 * h
    adj = {}
    c3, ax3 = cyl["hub3"]; f3 = _far(strap["L2"], c3, ax3, M.hr[2] + 1)
    v = nn_min(Em, strap["L2"], None, f3); adj["E-L2"] = torch.where(torch.isfinite(v), v - 2 * h, torch.full_like(v, INF))
    adj["knee-hub3"] = vbox(surf["hub3"], "knee")
    pa = tf(3, M.fr["A0"][None])[:, 0]
    ef = torch.linalg.norm(Em - pa[:, None, :], dim=-1) > MKm.BOSS_R + 0.5
    cen, R, half = bx["knee"]; dk = sd_box(Em, cen, R, half) - h
    dk = torch.where(ef, dk, torch.full_like(dk, INF)).amin(1)
    adj["knee-E"] = torch.where(ef.any(1), dk, big)
    C = torch.stack(list(c.values()), 1); A = torch.stack(list(adj.values()), 1)
    out = C.amin(1)
    out = torch.where(A.amin(1) < M.ADJ, torch.minimum(out, torch.full_like(out, -1.0)), out)
    names = list(c) + list(adj); vals = torch.cat([C, A], 1)
    return out.cpu().numpy(), names, vals.cpu().numpy()


# ---- the run loop (MK._run_batched), batched over poses ------------------------------------------------------------------
def run(self, B=None):
    import torch
    MKm = _MOD["KP"].verifier().MK; S = MKm.S
    B = self.B; B.reset(); t0 = time.time(); gd = B._gd; dev = gd.dev
    self.fit()
    pf = np.asarray(self.poses_fit); valid = set(pf.tolist()); dropped = set(pf[self.drop].tolist())
    self.clear = np.full(len(B.idx), np.nan); self.last_pair = {}; self.cmin = {}
    if len(pf):
        pi = torch.as_tensor(pf.astype(np.int64), device=dev)
        cl, names, vals = collide_all(self, pi, dev)
        for a, i in enumerate(pf):
            self.clear[i] = cl[a]
            lc = {nm: round(float(v), 1) for nm, v in zip(names, vals[a]) if math.isfinite(v)}
            self.last_pair[i] = min(lc, key=lc.get) if lc else None
        jam = bool(self.p.get("jam_contact"))
        take = np.array([not (cl[a] < S.PART_CLEAR and not (jam and i in dropped)) for a, i in enumerate(pf)], bool)
        for a, i in enumerate(pf):
            if not take[a]: self.why[i] = "parts"
        tk = pf[take]
        if len(tk):
            Td = T_dev(self, dev); pt = torch.as_tensor(tk.astype(np.int64), device=dev)
            TT = lambda x: torch.as_tensor(np.asarray(x, float), dtype=torch.float64, device=dev)
            def world(m, X): R, t = Td[m]; return _apply(R[pt], t[pt], TT(X)) @ Td["RS"][pt].transpose(1, 2)
            mp = [world(m, X) for m, X in self.rigid.values()] + [world(m, X) for m, X in self.link_pts.values()]
            cw = [world(m, Pc) for m, Pc in self.contact]
            P = torch.cat(mp + cw, 1); nm_ = sum(x.shape[1] for x in mp); k = P.shape[1]
            dd = gd.dist(pt[:, None].expand(-1, k).reshape(-1), P.reshape(-1, 3)).reshape(len(tk), k)
            d = dd[:, :nm_].cpu().numpy()
            dc = dd[:, nm_:].amin(1).cpu().numpy() if k > nm_ else np.full(len(tk), 1e9)
            for a, i in enumerate(tk):
                B.res[i] = d[a]; self.cmin[i] = float(dc[a])
                if dc[a] < 0: B.res[i] = np.r_[d[a], dc[a]]
                if min(float(dc[a]), float(d[a].min())) < 0: self.why[i] = "skin" if i in dropped else "contact"
    r = B.report(); r["f"] = [round(float(x), 1) for x in self.f]; r["t"] = round(time.time() - t0, 1)
    return r


# ---- the verifier's extra_checks, batched ---------------------------------------------------------------------------------
def extra_checks(M, B):
    import torch
    V = _MOD["KP"].verifier(); MKm = V.MK; S = MKm.S
    D = M.D; P = D.p; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tr = M.tr; tp = P["tp"]; h = S.T_LINK / 2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    out = dict(axis_sn_vs_u3_deg=round(math.degrees(math.acos(min(1, abs(float(sn @ u[2]))))), 4))
    if not taken:
        out.update(closure_max={}, closure_bad_poses=0, res_deg_max_taken=None, knee_vs_hub3_upper_low=[], knee_vs_hub3_upper_bad=0,
                   boss_low=[], boss_bad=0, spans_deg=dict(q3=None, pin_a=None, pin_b=None), pad={})
        return out, set()
    dev = B._gd.dev; Td = T_dev(M, dev); pi = torch.as_tensor(np.array(taken, np.int64), device=dev)
    TT = lambda x: torch.as_tensor(np.asarray(x, float), dtype=torch.float64, device=dev)
    _, X = M.cyl_surf["hub3"]; cen3 = c[2] + M.f[2] * u[2]; zz = (X - cen3) @ u[2]; H3up = X[zz >= S.UP - 1e-6]
    e, f = S.frame_of(sn); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(MKm.BOSS_R, 1.0)
    boss = np.concatenate([fr["A0"] + z * sn + MKm.BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in (tr, tr + tp / 2, tr + tp)]
                          + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (tr, tr + tp)])
    (R2, t2), (R3, t3), (R6, t6), (R5, t5) = [(Td[m][0][pi], Td[m][1][pi]) for m in (2, 3, 6, 5)]
    mv = lambda R, x: (R @ TT(x))
    e1 = torch.linalg.norm((mv(R2, c[2]) + t2) - (mv(R3, c[2]) + t3), dim=-1)
    Rr = R2.transpose(1, 2) @ R3; u3 = TT(u[2]); snt = TT(sn)
    deg = lambda x: torch.rad2deg(torch.arccos(x.clamp(max=1.0)))
    e2 = deg(((Rr @ u3) * u3).sum(-1))
    e3 = torch.linalg.norm((mv(R3, fr["A0"]) + t3) - (mv(R6, fr["A0m"]) + t6), dim=-1)
    e4 = torch.linalg.norm((mv(R6, fr["Bm"]) + t6) - (mv(R5, fr["Bm"]) + t5), dim=-1)
    e5 = torch.maximum(deg((((R3.transpose(1, 2) @ R6) @ snt) * snt).sum(-1)), deg((((R6.transpose(1, 2) @ R5) @ snt) * snt).sum(-1)))
    clo = {k: round(float(v.amax()), 4) for k, v in zip(("hub3c", "rot3_axis", "pin_a", "pin_b", "knee_rot_axis"), (e1, e2, e3, e4, e5))}
    clo["arm_rot"] = 0.0
    bad_close = (e1 > 0.5) | (e3 > 0.5) | (e4 > 0.5) | (e2 > 0.5) | (e5 > 0.5)
    bx = boxes_dev(M, pi, M.tr, dev); kc, kR, kh = bx["knee"]
    d_kh3 = sd_box(_apply(R3, t3, TT(H3up)), kc, kR, kh).amin(1); bad_kh3 = d_kh3 < S.PART_CLEAR
    bw = _apply(R3, t3, TT(boss))
    cyl = {}
    for k, (m, cc, ax) in M.cyl.items():
        R, t = Td[m]; cyl[k] = ((R[pi] @ TT(cc)) + t[pi], R[pi] @ TT(ax))
    st = {k: _apply(Td[m][0][pi], Td[m][1][pi], TT(X)) for k, (m, X) in M.strap.items()}
    rmax = max(M.hr)
    v = {"boss-hub1": sd_cylr(bw, *cyl["hub1"], rmax, S.CROWN).amin(1), "boss-hub2": sd_cylr(bw, *cyl["hub2"], rmax, S.CROWN).amin(1)}
    if st["L1"].shape[1]: v["boss-L1"] = nn_min(bw, st["L1"]) - h
    c3w, ax3 = cyl["hub3"]; far = _far(st["L2"], c3w, ax3, S.HUB_R + 1)
    vL2 = nn_min(bw, st["L2"], None, far); vL2 = torch.where(far.any(1), vL2 - h, torch.full_like(vL2, 1e9))
    V_ = torch.stack(list(v.values()), 1); vmin = V_.amin(1)
    bad_boss = (vmin < S.PART_CLEAR) | (vL2 < M.ADJ)
    tk = np.array(taken)
    bc, bk, bb = bad_close.cpu().numpy(), bad_kh3.cpu().numpy(), bad_boss.cpu().numpy()
    out["closure_max"] = clo; out["closure_bad_poses"] = int(bc.sum())
    out["res_deg_max_taken"] = round(float(M.res_deg[taken].max()), 4)
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    dk = d_kh3.cpu().numpy(); o = np.argsort(dk, kind="stable")[:5]
    out["knee_vs_hub3_upper_low"] = [dict(mm=round(float(dk[j]), 2), **lab(tk[j])) for j in o]; out["knee_vs_hub3_upper_bad"] = int(bk.sum())
    lb = torch.minimum(vmin, vL2).cpu().numpy(); o = np.argsort(lb, kind="stable")[:5]
    out["boss_low"] = [dict(mm=round(float(lb[j]), 2), **lab(tk[j])) for j in o]; out["boss_bad"] = int(bb.sum())
    q3 = M.q[tk, 2] - M.K["phi"][tk]; qa = M.K["qa"][tk]; qb = M.K["qb"][tk]
    span = lambda a: round(math.degrees(float(np.ptp(np.unwrap(np.array(a, float))))), 1) if len(a) else None
    out["spans_deg"] = dict(q3=span(q3), pin_a=span(qa), pin_b=span(qb))
    Bm = fr["Bm"]
    out["pad"] = dict(home_dist_from_GH=round(float(np.linalg.norm(Bm)), 1), tr=round(float(tr), 2),
                      c3_dist_from_GH=round(float(np.linalg.norm(c[2])), 1), pad_minus_c3=[round(float(x), 1) for x in (Bm - c[2]) @ np.stack([D.sa, D.st, sn], 1)])
    return out, set(tk[bc].tolist()) | set(tk[bk].tolist()) | set(tk[bb].tolist())


# ---- patching + benches ------------------------------------------------------------------------------------------------
class ExactCached:
    """concept_bench._Exact for the REST skin (the seats) with its libigl trees built once: the same AABB squared distance
    (sub-mesh Fs, full mesh beyond 1.7 x HALF) and the same fast-winding-number BVH (default accuracy) the one-shot calls
    rebuild on every call - bit-for-bit the same numbers (checked: max |diff| 0.0 on 6.5k points), 5-10x faster"""
    def __init__(self, ex):
        import concept_bench as CB
        igl = ex.igl; self.ex = ex; self.HALF = CB.HALF; self.V, self.F, self.Fs = ex.V, ex.F, ex.Fs
        self.bvh = igl.FastWindingNumberBVH(); self.bvh.init(ex.V, ex.F)
        self.ts = igl.AABB(); self.ts.init(ex.V, ex.Fs); self.tf = igl.AABB(); self.tf.init(ex.V, ex.F)

    def __call__(self, P):
        P = np.ascontiguousarray(P, float).reshape(-1, 3)
        if not len(P): return np.zeros(0)
        far = np.linalg.norm(P, axis=1) > self.HALF * 1.7
        U = np.empty(len(P))
        if (~far).any(): U[~far] = np.sqrt(self.ts.squared_distance(self.V, self.Fs, np.ascontiguousarray(P[~far]))[0])
        if far.any(): U[far] = np.sqrt(self.tf.squared_distance(self.V, self.F, np.ascontiguousarray(P[far]))[0])
        W = self.bvh.winding_number(P)
        return np.where(W > 0.5, -np.abs(U), np.abs(U))


def ik_vec(self, Q):
    """S.Design.ik with the per-frame rotm stacks batched (rotm is elementwise: the same arithmetic per frame)"""
    S = _MOD["KP"].verifier().MK.S; rotm, sub1, unit = S.rotm, S.sub1, S.unit
    u1, u2, u3 = self.u; n = len(Q)
    w = Q @ u3; c12 = u1 @ u2
    M = np.array([[1, c12], [c12, 1]]); ab = np.linalg.solve(M, np.stack([w @ u1, np.full(n, u2 @ u3)]))
    al, be = ab; cr = np.cross(u1, u2); g2 = (1 - al ** 2 - be ** 2 - 2 * al * be * c12) / (cr @ cr)
    th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
    a1, a2 = np.degrees(self.A[0]), np.degrees(self.A[1])
    ok = (th >= abs(a1 - a2) + S.SING) & (th <= min(a1 + a2, 360 - a1 - a2) - S.SING) & (g2 > 0)
    best = None
    for sg in (1.0, -1.0):
        z = al[:, None] * u1 + be[:, None] * u2 + sg * np.sqrt(np.clip(g2, 0, None))[:, None] * cr
        q1 = sub1(u1, z, w); q2 = sub1(u2, np.broadcast_to(u3, z.shape), z)
        R1 = rotm(u1, q1) if n else np.zeros((0, 3, 3))
        p2 = R1 @ u2; br = np.sign(np.einsum("ij,ij->i", p2, np.cross(np.broadcast_to(u1, w.shape), w)))
        if best is None: best = [q1.copy(), q2.copy(), br]
        else:
            pick = br == self.branch; best[0][pick] = q1[pick]; best[1][pick] = q2[pick]
    q1, q2 = best[0], best[1]
    R1 = rotm(u1, q1) if n else np.zeros((0, 3, 3))
    R2 = rotm(u2, q2) if n else np.zeros((0, 3, 3))
    R12 = R1 @ R2; v = unit(np.cross(u3, [0.3, 0.5, 0.8]))
    q3 = sub1(u3, np.broadcast_to(v, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, v))
    R3 = rotm(u3, q3) if n else np.zeros((0, 3, 3))
    c1, c2, c3 = self.c
    t1 = c1 - R1 @ c1; X1 = (R1, t1)
    t2 = np.einsum("nij,nj->ni", R1, c2[None] - R2 @ c2 - c1[None]) + c1; X2 = (R12, t2)
    R123 = R12 @ R3
    t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3) + t2; X3 = (R123, t3)
    sv = np.einsum("nji,nj->ni", Q, t3)
    s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
    return np.stack([q1, q2, q3], 1), ok, X1, X2, X3, s


def patch(KP, fast_cpu=True):
    V = KP.verifier(); MKm = V.MK
    MKm.S.Model.needed = needed; MKm.S.Model.run = run; V.extra_checks = extra_checks
    if fast_cpu and os.environ.get("GBK_FAST_CPU", "1") == "1":     # bit-identical CPU-side speed-ups (seats, IK)
        R = MKm.OSN.rest()
        if not isinstance(R["ex"], ExactCached): R["ex"] = ExactCached(R["ex"])
        MKm.S.Design.ik = ik_vec


def bench(nc, nw, device, G=None):
    """the kit's CPU Bench (fast cache) with the device grid attached"""
    import concept_bench as CB
    old = os.environ.pop("CB_EXACT", None)
    try: B = CB.Bench(nc, nw)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    if B.grid is None: raise SystemExit(f"no fast cache for Bench({nc},{nw})")
    B._gd = GridDev(B, device, G); return B


def seat_ok(p):
    import concept_kit as KIT
    return float(KIT.bvec(p["az1"], p["el1"])[0]) <= ANT_MAX


def evaluate_one(p, Bw, Bf=None):
    """knee_polish.evaluate (same bench) or frozen_on (fit Bf -> wear Bw) + score_model -> report dict"""
    KP = kit(); t = time.time(); p0 = p; p = prep(p)
    try:
        if not seat_ok(dict(KP.base_params(), **p)): return dict(params=p0, gap=200.0, gap_near1=200.0, error="J1 seat outside the back / acromion-top region")
        if Bf is None:
            rep, M, aud = KP.evaluate(Bw, p)
        else:
            P = KP.base_params(); P.update(p); P = KP.snap(P)
            M1 = KP.verifier().MK.Model(Bf, dict(P))
            if not M1.kin_ok.any(): return dict(params=p, gap=None, error="nothing closes on the fit bench", secs=round(time.time() - t, 2))
            M, fitrep, P2 = KP.frozen_on(Bf, Bw, P); r = M.run()
            if not M.kin_ok.any(): return dict(params=p, gap=None, error="nothing closes on the wear bench", secs=round(time.time() - t, 2))
            rep, aud, ex = KP.score_model(M, Bw, r, P)
        out = {k: rep.get(k) for k in KEYS + ("near_min", "near1_poses", "why", "extra_bad", "knee_ang", "tr", "f")}
        out.update(params=p0, secs=round(time.time() - t, 2))
        return out
    except Exception as e:                                                       # noqa: BLE001
        import traceback
        return dict(params=p, gap=None, error=f"{type(e).__name__}: {e}"[:300], trace=traceback.format_exc()[-1500:], secs=round(time.time() - t, 2))


# ---- the CPU reference (the kit unpatched, in spawned processes) -----------------------------------------------------------
def cpu_ref(args):
    p, wear, fit, margin = args
    os.environ["OMP_NUM_THREADS"] = "1"; KP = kit(margin); t = time.time(); p = prep(p)
    import concept_bench as CB
    try:
        if not seat_ok(dict(KP.base_params(), **p)): return dict(gap=200.0, gap_near1=200.0, error="seat")
        if not fit or tuple(fit) == tuple(wear):
            rep, M, aud = KP.evaluate(CB.Bench(*wear), p)
        else:
            P = KP.base_params(); P.update(p); P = KP.snap(P)
            Bf = CB.Bench(*fit); M1 = KP.verifier().MK.Model(Bf, dict(P))
            if not M1.kin_ok.any(): return dict(gap=None, error="nothing closes on the fit bench")
            Bw = CB.Bench(*wear); M, fitrep, P2 = KP.frozen_on(Bf, Bw, P); r = M.run()
            if not M.kin_ok.any(): return dict(gap=None, error="nothing closes on the wear bench")
            rep, aud, ex = KP.score_model(M, Bw, r, P)
        out = {k: rep.get(k) for k in KEYS + ("near_min", "near1_poses", "why", "extra_bad")}
        out["secs"] = round(time.time() - t, 2); return out
    except Exception as e:                                                       # noqa: BLE001
        return dict(gap=None, error=f"{type(e).__name__}: {e}"[:300], secs=round(time.time() - t, 2))


def _cpu_idx(a): return a[0], cpu_ref(a[1])


# ---- configurations --------------------------------------------------------------------------------------------------
def leaders():
    KP = kit(); r = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "skin-normal-3r-pin-knee.json")))
    out = [("H1", dict(r["best_params"])), ("k4598", {k: v for k, v in r["best_params_previous"].items() if k != "neck"})]
    p5 = (r.get("rebase_polish_m5") or {}).get("P5", {}).get("params")
    if p5: out.append(("P5", dict(p5)))
    if os.environ.get("GBK_RAGLAN", "1") == "1":
        try:
            rg = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "raglan-knee-3r.json")))["best_params"]
            keep = set(KP.FREE) | {"r1t", "r1d", "r2t", "r2d", "rc", "rad1", "rad2", "rad3"}
            out.append(("raglan", {k: v for k, v in rg.items() if k in keep}))
        except Exception: pass                                                    # noqa: BLE001
    return out


def random_configs(n, seed=0, around=None, scale=1.0):
    """configs inside the rulings: knee_polish FREE bounds, O20 hubs, J1 seat on the back / acromion top"""
    KP = kit(); rng = np.random.default_rng(seed); out = []
    base = around or KP.base_params()
    while len(out) < n:
        p = {}
        for k, (sc, lo, hi, _) in KP.FREE.items():
            if around is not None: v = float(base[k]) + rng.normal() * sc * scale
            elif lo is None: v = float(rng.uniform(-180, 180))
            else: v = float(rng.uniform(lo, hi))
            if lo is not None: v = min(hi, max(lo, v))
            p[k] = round(v, 4)
        p.update(rad1=10.0, rad2=10.0, rad3=10.0)
        if seat_ok(p): out.append(p)
    return out


def mixed_configs(n, seed=0):
    """parity / speed set: 4/5 near the three leaders (H1, P5, k4598) at 0.5 / 1 / 2 / 3 x the polish's CMA scale, 1/5
    uniform in the polish bounds - every one inside the rulings (O20, J1 seat region, knee_polish FREE bounds)"""
    L = [p for nm, p in leaders() if nm in ("H1", "k4598", "P5")]; n_uni = max(2, n // 5); out = []
    for k in range(n - n_uni):
        out += random_configs(1, seed * 1000 + k, around=dict(kit().base_params(), **L[k % len(L)]), scale=(0.5, 1.0, 2.0, 3.0)[k % 4])
    return out + random_configs(n_uni, seed * 1000 + 999)


_WG = {}


def _gpu_init(wear, fit, margin, device):
    os.environ["OMP_NUM_THREADS"] = "1"; KP = kit(margin); patch(KP)
    _WG["Bw"] = bench(*wear, device); _WG["Bf"] = bench(*fit, device) if fit and tuple(fit) != tuple(wear) else None


def _gpu_eval(a):
    k, p = a; return k, evaluate_one(p, _WG["Bw"], _WG["Bf"])


def gpu_pool(workers, wear, fit, margin, device):
    import multiprocessing as mp
    return mp.get_context("spawn").Pool(workers, initializer=_gpu_init, initargs=(wear, fit, margin, device))


def _cma_init(nc, nw):
    """knee_polish's pool initializer with the device grid + the batched loops (fork: the parent never touched CUDA)"""
    os.environ.setdefault("OMP_NUM_THREADS", "1"); KP = kit(); patch(KP)
    dev = os.environ.get("GBK_DEVICE", "cuda"); KP._W["B"] = bench(nc, nw, dev)


def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("args", nargs="*")
    ap.add_argument("--bench", default="110,360"); ap.add_argument("--fit", default=None); ap.add_argument("--margin", type=float, default=5.0)
    ap.add_argument("--device", default=None); ap.add_argument("--n", type=int, default=50); ap.add_argument("--out")
    ap.add_argument("--procs", type=int, default=4); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--leaders", action="store_true")
    ap.add_argument("--near", type=float, default=0.0, help="random configs within `near` x the CMA scale around H1 (0 = uniform in the bounds)")
    ap.add_argument("--cpu-from", dest="cpu_from"); ap.add_argument("--mix", action="store_true"); ap.add_argument("--workers", type=int, default=0)
    if len(sys.argv) > 1 and sys.argv[1] == "cma":                    # knee_polish's CMA (same objective / rows / state) on the device
        KP = kit(float(os.environ.get("CB_FOLD_MARGIN", 5.0))); KP._init = _cma_init; sys.argv = [sys.argv[0]] + sys.argv[1:]
        import argparse as _ap
        c = _ap.ArgumentParser(); c.add_argument("cmd"); c.add_argument("--x0", default="{}"); c.add_argument("--fixed", default="")
        c.add_argument("--label", required=True); c.add_argument("--out", required=True); c.add_argument("--state", default="")
        c.add_argument("--state-out", default=""); c.add_argument("--sigma", type=float, default=0.5)
        c.add_argument("--popsize", type=int, default=16); c.add_argument("--jobs", type=int, default=2)
        c.add_argument("--budget-s", type=float, default=3000); c.add_argument("--max-gen", type=int, default=400)
        c.add_argument("--seed", type=int, default=1); c.add_argument("--nc", type=int, default=110); c.add_argument("--nw", type=int, default=360)
        c.add_argument("--obj", default="near1", choices=("near1", "gap"))
        x = c.parse_args(sys.argv[1:]); x.state_out = x.state_out or (x.out + ".state.json"); KP.cma(x); return
    a = ap.parse_args()
    KP = kit(a.margin); patch(KP)
    import torch
    dev = a.device or ("cuda" if torch.cuda.is_available() else "cpu")
    wear = tuple(int(x) for x in a.bench.split(",")); fit = tuple(int(x) for x in a.fit.split(",")) if a.fit else None
    log = lambda s: print(s, flush=True)
    if a.cmd == "table":
        for f in a.args:
            d = json.load(open(f)); S_ = d["summary"]; md = S_["max_abs_diff"]
            print(f"| {'fit ' + str(tuple(S_['fit'])) + ' -> ' if S_.get('fit') else 'same '}{tuple(S_['bench'])} | {S_['n']} | "
                  + " | ".join(str(md.get(k)) for k in ("gap", "gap_near1", "reach", "follow", "inband14", "inband10", "contact"))
                  + f" | {S_['n_gap_diff_gt_05']} | {S_['gpu_secs']} | {S_['cpu_secs']} ({S_['cpu_procs']}) |")
        return
    if a.cmd == "speed":                                              # evals/s of a worker pool on the device (after warm-up)
        cf = mixed_configs(a.n, a.seed + 7); gp = gpu_pool(a.workers or 1, wear, fit, a.margin, dev)
        gp.map(_gpu_eval, list(enumerate(cf[:a.workers or 1])), chunksize=1)
        t = time.time(); R = gp.map(_gpu_eval, list(enumerate(cf)), chunksize=1); dt = time.time() - t; gp.close()
        secs = [r.get("secs") for _, r in R if r.get("secs")]
        res = dict(n=len(cf), secs=round(dt, 2), evals_per_s=round(len(cf) / dt, 3), workers=a.workers or 1, device=dev, bench=list(wear),
                   fit=list(fit) if fit else None, margin=a.margin, s_per_config_median=round(float(np.median(secs)), 2) if secs else None,
                   errors=sum(1 for _, r in R if r.get("gap") is None), gpu=(torch.cuda.get_device_name(0) if dev == "cuda" else None), nproc=os.cpu_count())
        log(json.dumps(res))
        if a.out: json.dump(res, open(a.out, "w"), indent=1)
        return
    t = time.time(); Bw = bench(*wear, dev) if not a.workers else None; Bf = bench(*fit, dev) if fit and fit != wear and not a.workers else None
    log(f"benches on {dev} in {time.time() - t:.1f} s; margin {os.environ.get('CB_FOLD_MARGIN')}")
    if a.cmd == "eval":
        cf = json.load(open(a.args[0])); rows = []
        for p in cf:
            r = evaluate_one(p, Bw, Bf); rows.append(r); log(f"  gap {r.get('gap')} near1 {r.get('gap_near1')} ({r.get('secs')} s) {r.get('error', '')}")
        json.dump(dict(bench=list(wear), fit=list(fit) if fit else None, device=dev, margin=a.margin, rows=rows), open(a.args[1], "w"), indent=1, default=float)
    elif a.cmd == "parity":
        named = (leaders() if a.leaders else [])
        rnd = mixed_configs(a.n, a.seed) if a.mix else random_configs(a.n, a.seed, around=(KP.base_params() if a.near else None), scale=a.near or 1.0)
        cf = [p for _, p in named] + rnd; tags = [nm for nm, _ in named] + [f"r{k}" for k in range(len(rnd))]
        import multiprocessing as mp
        ctx = mp.get_context("spawn"); pool = ctx.Pool(a.procs)
        known = {}
        if a.cpu_from and os.path.exists(a.cpu_from):
            for r in json.load(open(a.cpu_from))["rows"]: known[json.dumps(r["params"], sort_keys=True)] = r["cpu"]
        todo = [k for k, p in enumerate(cf) if json.dumps(p, sort_keys=True) not in known]
        tc0 = time.time(); fut = pool.imap_unordered(_cpu_idx, [(k, (cf[k], wear, fit, a.margin)) for k in todo], chunksize=1)
        t = time.time(); g = [None] * len(cf)
        if a.workers:
            gp = gpu_pool(a.workers, wear, fit, a.margin, dev)
            for j, (k, r) in enumerate(gp.imap_unordered(_gpu_eval, list(enumerate(cf)), chunksize=1)):
                g[k] = r; log(f"  GPU {j + 1}/{len(cf)} {tags[k]}: gap {r.get('gap')} near1 {r.get('gap_near1')} ({r.get('secs')} s) {r.get('error', '')}")
            gp.close()
        else:
            for k, p in enumerate(cf):
                r = evaluate_one(p, Bw, Bf); g[k] = r
                log(f"  GPU {k + 1}/{len(cf)} {tags[k]}: gap {r.get('gap')} near1 {r.get('gap_near1')} ({r.get('secs')} s) {r.get('error', '')}")
        tg = time.time() - t; log(f"GPU {len(cf)} configs in {tg:.1f} s ({a.workers or 1} worker(s))")
        c = [known.get(json.dumps(p, sort_keys=True)) for p in cf]
        for j, (k, r) in enumerate(fut):
            c[k] = r; log(f"  CPU {j + 1}/{len(todo)} {tags[k]}: gap cpu {r.get('gap')} gpu {g[k].get('gap')} | near1 cpu {r.get('gap_near1')} gpu {g[k].get('gap_near1')} ({r.get('secs')} s)")
        tc = time.time() - tc0; pool.close()
        keys = ("gap", "gap_near1", "gap_near2", "model_gap", "reach", "follow", "inband14", "inband10", "contact")
        both = [(x, y) for x, y in zip(g, c) if x.get("gap") is not None and y.get("gap") is not None]
        diff = {k: [abs(float(x[k]) - float(y[k])) for x, y in both if x.get(k) is not None and y.get(k) is not None] for k in keys}
        rows = [dict(tag=tg_, params=p, gpu={k: x.get(k) for k in keys + ("error", "secs", "why")}, cpu=y) for tg_, p, x, y in zip(tags, cf, g, c)]
        summ = dict(n=len(cf), n_compared=len(both), bench=list(wear), fit=list(fit) if fit else None, margin=a.margin,
                    max_abs_diff={k: round(max(v), 4) if v else None for k, v in diff.items()},
                    n_gap_diff_gt_05=sum(1 for v in diff["gap"] if v > 0.5), n_near1_diff_gt_05=sum(1 for v in diff["gap_near1"] if v > 0.5),
                    n_errors_gpu=sum(1 for x in g if x.get("gap") is None), n_errors_cpu=sum(1 for y in c if y and y.get("gap") is None),
                    gpu_secs=round(tg, 2), cpu_secs=round(tc, 2), cpu_procs=a.procs, device=dev,
                    leaders={tg_: dict(gpu=x.get("gap"), cpu=(y or {}).get("gap"), gpu_near1=x.get("gap_near1"), cpu_near1=(y or {}).get("gap_near1")) for tg_, x, y in zip(tags, g, c) if not tg_.startswith("r")})
        log(json.dumps(summ))
        if a.out: json.dump(dict(summary=summ, rows=rows), open(a.out, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()

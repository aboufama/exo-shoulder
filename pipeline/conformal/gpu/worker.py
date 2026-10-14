"""RunPod Flash worker: GPU evaluator + evolutionary search for the conformal D4 shoulder (avg/conformal.py port).

Job: {"maps": <b64 gzip npz from pack_maps>, "mode": "eval" | "search", ...}; mode "band_eval" / "band_search" -> band_impl.run
  eval:   {"designs": [...]}  -> per design: cov, gap stats (matches conformal.evaluate_rest at 0.5 deg maps)
  search: {"seed", "gens", "pop", "elite", "weights": {...}, "init": [designs]}  -> best designs + Pareto archive
Designs: {"az","el","a1","a2","a3","branch","order":[o1,o2,o3]}; J4 axis W (canonical humerus frame) and the BOTTOM hub
height z_j4 come with the job ("W", "z_j4"); G = rest-pose skin gap cap (mm).
"""
from runpod_flash import Endpoint, GpuGroup


@Endpoint(name="exo-band10", gpu=[GpuGroup.ADA_24, GpuGroup.AMPERE_24, GpuGroup.ADA_48_PRO, GpuGroup.AMPERE_48], workers=(0, 6),
          idle_timeout=120, execution_timeout_ms=5400000, dependencies=["numpy", "scipy"])
async def conformal_job(job: dict):
    import base64, gzip, io, math, time, random, hashlib
    import numpy as np
    try:
        import torch
    except ImportError:                                                     # base image without torch
        import subprocess, sys
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "torch"], check=True); import torch
    if str(job.get("mode", "")).startswith("band"):                       # band evaluator / search (band_impl.py)
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import band_impl
        return band_impl.run(job)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu"); t0 = time.time()
    f32 = torch.float32
    # ---------------------------------------------------------------- maps (cached per warm worker)
    global _CACHE
    try: _CACHE
    except NameError: _CACHE = {}
    src = job.get("skin") or job["maps"]
    key = hashlib.md5(src[:4096].encode()).hexdigest() + str(len(src))
    if key not in _CACHE and job.get("skin"):
        # ---- exact radial maps from the skin mesh (same algorithm as avg/radial_maps.py), 0.25 deg
        import json as _json
        from scipy.spatial import cKDTree
        from scipy.ndimage import minimum_filter, uniform_filter
        SK = _json.loads(gzip.decompress(base64.b64decode(job["skin"])).decode()); Lm = SK["L"]; Ssc = SK["scale"]; sk = SK["skin"]
        dec = lambda s_, t_: np.frombuffer(base64.b64decode(s_), dtype=t_)
        Fc = dec(sk["idx"], np.uint32 if sk["i32"] else np.uint16).reshape(-1, 3).astype(int)
        PRE = SK.get("posed")                                                # skin already posed locally (current body rig)
        if PRE is None:
            Vv = dec(sk["pos"], np.int16).reshape(-1, 3) / 10.0
            wi = dec(sk["wi"], np.uint8).reshape(-1, 2).astype(int); ww = dec(sk["ww"], np.uint8) / 255.0
        RESd = 0.25; NWd, NHd = int(360 / RESd), int(180 / RESd)
        def rot(ax_, a_):
            ax_ = np.asarray(ax_, float); ax_ = ax_ / np.linalg.norm(ax_)
            K = np.array([[0, -ax_[2], ax_[1]], [ax_[2], 0, -ax_[0]], [-ax_[1], ax_[0], 0]]); return np.eye(3) + math.sin(a_) * K + (1 - math.cos(a_)) * K @ K
        def scap(elev):
            n_ = [math.cos(30 * math.pi / 180), 0, -math.sin(30 * math.pi / 180)]
            return rot([0, 0, 1], 0.12 * elev * math.pi / 180) @ rot(n_, -0.36 * max(0, elev - 20) * math.pi / 180)
        def segs(pose):
            d2r = math.pi / 180; lift = np.array([0, 0.2 * max(0, pose["elev"] - 30) * Ssc, 0])
            Rh = rot([0, 1, 0], pose["plane"] * d2r) @ rot([1, 0, 0], -pose["elev"] * d2r) @ rot([0, 1, 0], pose["axial"] * d2r)
            T_ = (np.eye(3), -lift); Sg = (scap(pose["elev"]), np.zeros(3)); H_ = (Rh @ np.array(Lm["rest_humerus"]).T, np.zeros(3))
            ap = lambda A_, p_: A_[0] @ p_ + A_[1]
            E_ = ap(H_, np.array(Lm["elbow"])); ax_ = H_[0] @ np.array(Lm["elbow_axis"])
            Rf = rot(ax_, (pose["flex"] - Lm["rest_flex"]) * d2r); Fs = (Rf @ H_[0], Rf @ H_[1] + E_ - Rf @ E_)
            rh, uh = ap(Fs, np.array(Lm["radial_head"])), ap(Fs, np.array(Lm["ulnar_head"]))
            Rp = rot(rh - uh, (pose["pron"] + 90) * d2r); Pp = (Rp @ Fs[0], Rp @ Fs[1] + rh - Rp @ rh)
            return [T_, Sg, H_, Fs, Pp]
        def posed(pose):
            sg = segs(pose); Ra = np.stack([sg[k][0] for k in range(5)]); ta = np.stack([sg[k][1] for k in range(5)])
            A_ = np.einsum("nij,nj->ni", Ra[wi[:, 0]], Vv) + ta[wi[:, 0]]; B_ = np.einsum("nij,nj->ni", Ra[wi[:, 1]], Vv) + ta[wi[:, 1]]
            return ww[:, None] * A_ + (1 - ww[:, None]) * B_
        if PRE is None:
            armw = np.where(wi[:, 0] >= 2, ww, 0) + np.where(wi[:, 1] >= 2, 1 - ww, 0); ARMF = (armw > 0.5)[Fc].sum(1) >= 2
        else:
            ARMF = dec(PRE["armf"], np.uint8).astype(bool)
            PV = {k: dec(v, np.int16).reshape(-1, 3) / 10.0 for k, v in PRE["verts"].items()}   # "e0".."e180", "arm"
        def samples(Pv, faces, R_MAX=480.0, seed=0):
            A_, B_, C_ = Pv[faces[:, 0]], Pv[faces[:, 1]], Pv[faces[:, 2]]
            rc = np.linalg.norm((A_ + B_ + C_) / 3, axis=1); keep = rc < R_MAX; A_, B_, C_, rc = A_[keep], B_[keep], C_[keep], rc[keep]
            area = 0.5 * np.linalg.norm(np.cross(B_ - A_, C_ - A_), axis=1); spacing = np.maximum(0.25, rc * math.radians(RESd) * 0.6)
            nn = np.clip(np.ceil(area / spacing ** 2 * 2.0), 1, 4000).astype(int); out = []
            for lo_ in range(0, len(A_), 20000):
                sl = slice(lo_, lo_ + 20000); n_ = nn[sl]; idx = np.repeat(np.arange(len(n_)), n_)
                uu = np.random.default_rng(seed + lo_).random((len(idx), 2)); fl = uu.sum(1) > 1; uu[fl] = 1 - uu[fl]
                out.append(A_[sl][idx] + uu[:, :1] * (B_[sl][idx] - A_[sl][idx]) + uu[:, 1:] * (C_[sl][idx] - A_[sl][idx])); out += [A_[sl], B_[sl], C_[sl]]
            return np.concatenate(out)
        LAT_LO, LAT_HI = -75.0, 90.0
        def ray_maps(Pv, faces, c=3.0):
            Q = samples(Pv, faces); r = np.linalg.norm(Q, axis=1); lon = np.arctan2(Q[:, 2], Q[:, 0]); lat = np.arcsin(np.clip(Q[:, 1] / r, -1, 1))
            j = np.clip(((lon + math.pi) / math.radians(RESd)).astype(int), 0, NWd - 1); i = np.clip(((lat + math.pi / 2) / math.radians(RESd)).astype(int), 0, NHd - 1)
            r1 = np.full((NHd, NWd), np.inf, np.float32); np.minimum.at(r1, (i, j), r.astype(np.float32))
            fin = np.isfinite(r1); mn = minimum_filter(np.where(fin, r1, 1e9), size=3, mode="wrap")
            hole = ~fin & (uniform_filter(fin.astype(float), size=3, mode="wrap") > 0.5); r1[hole] = mn[hole]
            beyond = r > r1[i, j] + 4.0; r2 = np.full((NHd, NWd), np.inf, np.float32); np.minimum.at(r2, (i[beyond], j[beyond]), r[beyond].astype(np.float32))
            tree = cKDTree(Q); rows = np.arange(int((LAT_LO + 90) / RESd), int((LAT_HI + 90) / RESd))
            la = (rows + 0.5) * math.radians(RESd) - math.pi / 2; lo = (np.arange(NWd) + 0.5) * math.radians(RESd) - math.pi
            LA, LO = np.meshgrid(la, lo, indexing="ij"); U = np.stack([np.cos(LA) * np.cos(LO), np.sin(LA), np.cos(LA) * np.sin(LO)], -1).reshape(-1, 3)
            R1 = r1[rows].ravel(); R2 = r2[rows].ravel(); steps = np.arange(0.0, 14.01, 0.25)
            def march(base, sign):
                idx = np.nonzero(np.isfinite(base))[0]; done = np.zeros(len(idx), bool); res = base[idx] + sign * 14.0
                for s_ in steps:
                    td = ~done
                    if not td.any(): break
                    pts = U[idx[td]] * (base[idx[td]] + sign * s_)[:, None]; d_, _ = tree.query(pts, workers=-1)
                    h = d_ >= c; kk_ = np.nonzero(td)[0][h]; res[kk_] = base[idx[kk_]] + sign * s_; done[kk_] = True
                return idx, res
            r1c = np.zeros_like(R1); r2c = np.full_like(R2, np.inf)
            ii, rr = march(R1, +1); r1c[ii] = rr; ii, rr = march(R2, -1); r2c[ii] = rr
            f1 = np.zeros((NHd, NWd), np.float32); f2 = np.full((NHd, NWd), np.inf, np.float32); f1[rows] = r1c.reshape(len(rows), NWd); f2[rows] = r2c.reshape(len(rows), NWd)
            r1[~np.isfinite(r1)] = 0.0
            return r1[rows], f1[rows], f2[rows]
        elevs = list(range(0, 181, 15)); TT = [[], [], []]
        for e_ in elevs:
            m3 = ray_maps(PV[f"e{e_}"] if PRE is not None else posed(dict(plane=30, elev=e_, axial=0, flex=30, pron=0)), Fc[~ARMF])
            for kk_ in range(3): TT[kk_].append(m3[kk_])
        am = ray_maps(PV["arm"] if PRE is not None else posed(dict(plane=0, elev=0, axial=0, flex=30, pron=0)), Fc[ARMF])
        M = {"t_r1": torch.tensor(np.stack(TT[0]), device=dev), "t_r1c": torch.tensor(np.stack(TT[1]), device=dev), "t_r2c": torch.tensor(np.stack(TT[2]), device=dev),
             "a_r1": torch.tensor(am[0], device=dev), "a_r1c": torch.tensor(am[1], device=dev), "a_r2c": torch.tensor(am[2], device=dev)}
        RES = RESd * math.pi / 180; LAT0 = LAT_LO * math.pi / 180
        def cosmap(r1):
            r = torch.where(r1 > 0, r1, torch.full_like(r1, float("nan")))
            H = r.shape[-2]; lat = LAT0 + (torch.arange(H, device=dev, dtype=f32) + 0.5) * RES
            dlat = torch.gradient(r, spacing=RES, dim=-2)[0]; dlon = torch.gradient(r, spacing=RES, dim=-1)[0] / torch.clamp(torch.cos(lat), min=0.05)[:, None]
            c = r / torch.sqrt(r ** 2 + dlat ** 2 + dlon ** 2); return torch.nan_to_num(torch.clamp(c, 0.2, 1.0), nan=1.0)
        M["t_cos"] = torch.stack([cosmap(m) for m in M["t_r1"]]); M["a_cos"] = cosmap(M["a_r1"])
        Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(job["poses"]))))
        P = {k: torch.tensor(Z[k], device=dev) for k in ("PL", "EL", "AX", "HG", "RS", "ELEVS")}
        P["EB"] = torch.argmin(torch.abs(P["ELEVS"][None, :] - P["EL"][:, None]), dim=1)
        P["REST"] = int(torch.nonzero((P["PL"] == 0) & (P["EL"] == 0) & (P["AX"] == 0))[0, 0])
        _CACHE.clear(); _CACHE[key] = (M, P, RES, LAT0); print(f"exact maps built in {time.time() - t0:.0f}s", flush=True)
    if key not in _CACHE:
        Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(job["maps"]))))
        def m16(a):
            a = Z[a].astype(np.float32) / 10.0; a[a >= 6553.45] = np.inf; return torch.tensor(a, device=dev)
        M = {k: m16(k) for k in ("t_r1", "t_r1c", "t_r2c", "a_r1", "a_r1c", "a_r2c")}
        RES = float(Z["res"]) * math.pi / 180 if float(Z["res"]) > 0.05 else float(Z["res"]); LAT0 = float(Z["lat0"]) * math.pi / 180
        def cosmap(r1):
            r = torch.where(r1 > 0, r1, torch.full_like(r1, float("nan")))
            H = r.shape[-2]; lat = LAT0 + (torch.arange(H, device=dev, dtype=f32) + 0.5) * RES
            dlat = torch.gradient(r, spacing=RES, dim=-2)[0]; dlon = torch.gradient(r, spacing=RES, dim=-1)[0] / torch.clamp(torch.cos(lat), min=0.05)[:, None]
            c = r / torch.sqrt(r ** 2 + dlat ** 2 + dlon ** 2); return torch.nan_to_num(torch.clamp(c, 0.2, 1.0), nan=1.0)
        M["t_cos"] = torch.stack([cosmap(m) for m in M["t_r1"]]); M["a_cos"] = cosmap(M["a_r1"])
        P = {k: torch.tensor(Z[k], device=dev) for k in ("PL", "EL", "AX", "HG", "RS", "ELEVS")}
        P["EB"] = torch.argmin(torch.abs(P["ELEVS"][None, :] - P["EL"][:, None]), dim=1)
        P["REST"] = int(torch.nonzero((P["PL"] == 0) & (P["EL"] == 0) & (P["AX"] == 0))[0, 0])
        _CACHE.clear(); _CACHE[key] = (M, P, RES, LAT0)
    M, P, RES, LAT0 = _CACHE[key]
    NH, NW = M["a_r1"].shape
    HUB_R, HW, R_REF, T_IN, T_OUT = float(job.get("hub_r", 17.0)), 7.0, float(job.get("r_ref", 100.0)), 5.0, 5.5   # r_ref: radius the footprint angles are set at
    SING = 12.0 * math.pi / 180; D2R = math.pi / 180
    G = float(job.get("G", 10.0)); ZJ4 = float(job.get("z_j4", 67.5)); STACK = float(job.get("stack", 6.0))
    W = torch.tensor(job["W"], device=dev, dtype=f32)
    q_step = float(job.get("q_step", 6)); q_rest_step = float(job.get("q_rest_step", 30))
    QS = torch.arange(0, 360, q_step, device=dev, dtype=f32) * D2R; NQ = len(QS)
    RQ = list(range(0, NQ, max(1, int(round(q_rest_step / q_step)))))
    stride = int(job.get("stride", 1)); IDX = torch.arange(0, len(P["PL"]), stride, device=dev)
    HGs, RSs, EBs = P["HG"][IDX], P["RS"][IDX], P["EB"][IDX]; REST = P["REST"]

    def pix(w):
        lon = torch.atan2(w[..., 2], w[..., 0]); lat = torch.asin(torch.clamp(w[..., 1], -1, 1))
        j = torch.clamp(((lon + math.pi) / RES).long(), 0, NW - 1); i = torch.clamp(((lat - LAT0) / RES).long(), 0, NH - 1)
        return i, j

    RAMP = math.tan(math.radians(float(job.get("ramp_deg", 35.0))))
    def footprint(theta, n_arc=16):
        pts, kind, spar = [], [], []
        a0 = (HUB_R + 5.0) / R_REF; a1 = theta - a0
        for s in np.linspace(a0, max(a0 + 1e-3, a1), n_arc):
            for w in (-HW, 0.0, HW):
                d = np.array([math.cos(s), math.sin(s), w / R_REF]); pts.append(d / np.linalg.norm(d)); kind.append(0); spar.append(s / theta)
        for end, ang in ((0, 0.0), (1, theta)):
            c = np.array([math.cos(ang), math.sin(ang), 0.0]); t1 = np.array([-math.sin(ang), math.cos(ang), 0.0]); t2 = np.array([0, 0, 1.0])
            for k in range(9):
                if k == 0: d = c
                else:
                    phi = 2 * math.pi * (k - 1) / 8; rr = HUB_R / R_REF
                    d = math.cos(rr) * c + math.sin(rr) * (math.cos(phi) * t1 + math.sin(phi) * t2)
                pts.append(d / np.linalg.norm(d)); kind.append(1 + end); spar.append(float(end))
        return torch.tensor(np.array(pts), device=dev, dtype=f32), torch.tensor(kind, device=dev), torch.tensor(spar, device=dev, dtype=f32)

    def unit(x): return x / (torch.linalg.norm(x, dim=-1, keepdim=True) + 1e-12)

    def circ_int(c1, r1, c2, r2, sign):
        d = torch.clamp((c1 * c2).sum(-1), -1, 1); n = unit(torch.cross(c1, c2, dim=-1))
        den = 1 - d ** 2 + 1e-12
        a = (math.cos(r1) - d * math.cos(r2)) / den; b = (math.cos(r2) - d * math.cos(r1)) / den
        p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
        return p + sign * torch.sqrt(torch.clamp(h2, min=0))[..., None] * n, h2 > 0

    def tri_ok(x, y, a, b):
        t = torch.arccos(torch.clamp((x * y).sum(-1), -1, 1))
        return (t >= abs(a - b) + SING) & (t <= min(a + b, 2 * math.pi - a - b) - SING)

    TH = 5.5; MARG = 1.0
    WB = unit(W); _d = torch.tensor(job.get("bar_dir", [0.0, -1.0, 0.0]), device=dev, dtype=f32)
    DB = unit(_d - (_d @ WB) * WB); EBv = torch.cross(WB, DB, dim=-1)                      # BOTTOM frame (canonical humerus)
    JOG0, JOG1 = float(job.get("jog0", 34.0)), float(job.get("jog1", 56.0)); DJOG = float(job.get("jog", 8.6)); TBOT = 6.5
    def collisions(caps, FR, WD, WH, FPL, S, A, order, outer_at):
        """(N,Q) True where two members overlap: links vs links (outside a shared joint's stack), links vs BOTTOM"""
        heights = []
        for k in range(3):
            h = caps[k].clone(); kind = S[k][4]
            for end in (0, 1):
                if outer_at(k, end): h[kind == 1 + end] += STACK + (1.5 if k + 1 + end == 4 else 0.0)
            heights.append(h)
        hit = torch.zeros(FR[0].shape[:2], dtype=torch.bool, device=dev)
        rh = HUB_R / R_REF
        for i in range(3):
            for j in range(3):
                if i == j: continue
                # points of i in j's local frame
                lj = torch.einsum("nqji,nqmj->nqmi", FR[j], WD[i])                        # (N,Q,M,3) local coords in j
                phi = torch.atan2(lj[..., 1], lj[..., 0]); lat = torch.asin(torch.clamp(lj[..., 2], -1, 1)); th = A[j]
                c0 = torch.stack([torch.ones_like(phi), torch.zeros_like(phi), torch.zeros_like(phi)], -1)
                dA = torch.arccos(torch.clamp(lj[..., 0], -1, 1))
                dBv = torch.arccos(torch.clamp(lj[..., 0] * math.cos(th) + lj[..., 1] * math.sin(th), -1, 1))
                inside = ((phi >= 0) & (phi <= th) & (torch.abs(lat) <= HW / R_REF + 0.01)) | (dA <= rh) | (dBv <= rh)
                # j's height at the nearest footprint sample
                near = torch.einsum("nqmi,ki->nqmk", lj, FPL[j]).argmax(-1); hj = heights[j][near]
                hi_ = heights[i][None, None, :].expand_as(hj)
                over = inside & (hi_ < hj + TH + MARG) & (hj < hi_ + TH + MARG)
                # shared joint: i and j adjacent -> ignore the stack zone around that joint
                if abs(j - i) == 1:
                    pin = FR[max(i, j)][..., :, 0]                                            # shared pin = start pin of the later link
                    dd = torch.arccos(torch.clamp((WD[i] * pin[:, :, None, :]).sum(-1), -1, 1))
                    over &= dd > (HUB_R + 4.0) / R_REF
                hit |= over.any(-1)
        # links vs BOTTOM (rigid in the humerus frame): slab perpendicular to W along the bar
        for i in range(3):
            wh = WH[i]; h = heights[i][None, None, :]
            zc = (wh * WB).sum(-1); dc = (wh * DB).sum(-1); ec = (wh * EBv).sum(-1)
            zl = h * zc; dl = h * dc; el = h * ec                                             # point coords in BOTTOM frame
            rho = torch.sqrt(dl ** 2 + el ** 2)
            inplan = (rho <= HUB_R + 1.0) | ((torch.abs(el) <= 16.0) & (dl >= 0) & (dl <= 220.0))
            t_ = torch.clamp((dl - JOG0) / (JOG1 - JOG0), 0, 1); t_ = 10 * t_ ** 3 - 15 * t_ ** 4 + 6 * t_ ** 5
            zlo = ZJ4 + DJOG * t_; zhi = zlo + TBOT
            over = inplan & (zl < zhi + MARG) & (zl + TH > zlo - MARG) & (zc > 0)
            if i == 2:                                                                        # l3 stacks on BOTTOM's hub
                over &= rho > HUB_R + 4.0
            hit |= over.any(-1)
        return hit

    def bvec(az, el):
        return [-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)]

    def evaluate(d, want_detail=False):
        b = torch.tensor(bvec(d["az"], d["el"]), device=dev, dtype=f32); A = [d[k] * D2R for k in ("a1", "a2", "a3")]
        br = float(d["branch"]); order = d.get("order", [1, 1, 0])
        e = unit(torch.cross(b, torch.tensor([0.0, 1, 0], device=dev), dim=-1)); fv = torch.cross(b, e, dim=-1)
        u4 = HGs @ W                                                                     # (N,3)
        c2 = math.cos(A[0]) * b + math.sin(A[0]) * (torch.cos(QS)[:, None] * e + torch.sin(QS)[:, None] * fv)   # (Q,3)
        N = len(u4); C2 = c2[None].expand(N, NQ, 3); U4 = u4[:, None].expand(N, NQ, 3); B = b.expand(N, NQ, 3)
        c3, ok = circ_int(C2, A[1], U4, A[2], br)
        ok = ok & tri_ok(C2, U4, A[1], A[2]) & tri_ok(B, c3, A[0], A[1]) & (torch.abs((B * U4).sum(-1)) <= math.cos(SING))
        pins = {"b": B, "c2": C2, "c3": c3, "u4": U4}
        S = []; FR, WD, WH, FPL = [], [], [], []; sfp = []
        for k, (pa, pb) in enumerate((("b", "c2"), ("c2", "c3"), ("c3", "u4"))):
            a_, c_ = pins[pa], pins[pb]; n_ = unit(c_ - (a_ * c_).sum(-1, keepdim=True) * a_)
            Fm = torch.stack([a_, n_, torch.cross(a_, n_, dim=-1)], -1)                # (N,Q,3,3)
            L, kind, sp_ = footprint(A[k]); sfp.append(sp_)
            w = torch.einsum("nqij,mj->nqmi", Fm, L)
            wt = torch.einsum("nij,nqmj->nqmi", RSs, w); wh = torch.einsum("nji,nqmj->nqmi", HGs, w)
            it, jt = pix(wt); ia, ja = pix(wh); eb = EBs[:, None, None].expand_as(it)
            lo = torch.maximum(M["t_r1c"][eb, it, jt], M["a_r1c"][ia, ja]); hi = torch.minimum(M["t_r2c"][eb, it, jt], M["a_r2c"][ia, ja])
            skt, ska = M["t_r1"][eb, it, jt], M["a_r1"][ia, ja]; sk = torch.maximum(skt, ska)
            cs = torch.where(skt >= ska, M["t_cos"][eb, it, jt], M["a_cos"][ia, ja])
            S.append((lo, hi, sk, cs, kind)); FR.append(Fm); WD.append(w); WH.append(wh); FPL.append(L)
        del wt
        # rest pose index within IDX
        ri = int(torch.nonzero(IDX == REST)[0, 0]) if (IDX == REST).any() else None
        if ri is None: return dict(cov=0.0)
        def outer_at(k, end):
            J = k + 1 + end
            if J == 1: return order[0] == 1
            if J == 2: return (order[1] == 1) if k == 1 else (order[1] == 0)
            if J == 3: return (order[2] == 1) if k == 2 else (order[2] == 0)
            return True
        best = None; wts = job.get("weights", {})
        for qr in RQ:
            if not bool(ok[ri, qr]): continue
            caps = []; okp = ok.clone(); fail = False
            for k in range(3):
                lo, hi, sk, cs, kind = S[k]; skr = sk[ri, qr]; csr = torch.clamp(cs[ri, qr], min=0.5); cap = skr + G / csr
                for end in (0, 1):
                    m = kind == 1 + end
                    face = torch.maximum(lo[ri, qr][m].max(), (skr[m] + G / csr[m]).min())
                    if k == 2 and end == 1: face = torch.tensor(ZJ4, device=dev)
                    cap = cap.clone(); cap[m] = face
                # buildability: near each joint the ribbon can only climb at <= RAMP from that joint's face
                faceA = cap[kind == 1].max() + (STACK if outer_at(k, 0) else 0.0)
                faceB = cap[kind == 2].max() + (STACK + (1.5 if k == 2 else 0.0) if outer_at(k, 1) else 0.0)
                dA = sfp[k] * A[k] * (faceA + 3.0); dB = (1 - sfp[k]) * A[k] * (faceB + 3.0)
                lim = torch.minimum(faceA + RAMP * torch.clamp(dA - (HUB_R + 6.0), min=0), faceB + RAMP * torch.clamp(dB - (HUB_R + 6.0), min=0))
                m0 = kind == 0; cap = torch.where(m0, torch.minimum(cap, lim), cap)
                caps.append(cap)
                if bool((lo[ri, qr] > cap + 1e-4).any()): fail = True; break
                tk = T_IN if k == 1 else T_OUT
                okp &= (lo <= cap).all(-1) & ((cap + tk) <= hi).all(-1)
            if fail: continue
            if job.get("collide", True): okp &= ~collisions(caps, FR, WD, WH, FPL, S, A, order, outer_at)
            covm = okp.any(1); cov = float(covm.float().mean())
            if cov <= 0: continue
            gw = torch.zeros(okp.shape, device=dev)
            for k in range(3): gw = torch.maximum(gw, ((caps[k] - S[k][2]) * S[k][3]).max(-1).values)
            qsel = torch.where(okp, gw, torch.full_like(gw, 1e9)).argmin(1); ar = torch.arange(len(qsel), device=dev)
            gl = []
            for k in range(3):
                g = (caps[k][None, :] - S[k][2][ar, qsel]) * S[k][3][ar, qsel]; gl.append(g[covm])
            allg = torch.cat([g.reshape(-1) for g in gl])
            p50 = float(torch.median(allg)); p90 = float(torch.quantile(allg[:min(len(allg), 16000000)], 0.9))
            per = [float(torch.median(g)) for g in gl]
            worst = max(per)
            s = cov * (1 - wts.get("w_link", 0.6) * min(1.0, max(0.0, (worst - G) / wts.get("link_scale", 15.0)))) \
                    * (1 - wts.get("w_p90", 0.3) * min(1.0, max(0.0, (p90 - wts.get("p90_ref", 25.0)) / 50.0)))
            if best is None or s > best["score"]:
                best = dict(score=s, cov=cov, q_rest=float(QS[qr]) / D2R, gap_p50=p50, gap_p90=p90, per_link_p50=per)
        return best or dict(cov=0.0, score=0.0)

    if job.get("mode") == "eval":
        out = []
        for d in job["designs"]:
            r = evaluate(d); out.append(dict(d, **r))
        return {"results": out, "secs": time.time() - t0, "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"}

    # ---------------------------------------------------------------- evolutionary search
    rng = random.Random(job.get("seed", 1))
    lo_b = dict(a=30.0, el=-15.0); hi_b = dict(a=120.0, el=90.0)
    def feas(g):
        b = bvec(g["az"], g["el"])
        return -15 <= g["el"] <= 90 and all(30 <= g[k] <= 120 for k in ("a1", "a2", "a3")) and b[0] <= 0.35 and b[1] >= -0.25
    def rand_d():
        while True:
            g = dict(az=rng.uniform(0, 360), el=rng.uniform(-15, 90), a1=rng.uniform(30, 120), a2=rng.uniform(30, 120), a3=rng.uniform(30, 120),
                     branch=rng.choice([-1, 1]), order=[rng.randint(0, 1) for _ in range(3)])
            if feas(g): return g
    def mutate(g, s):
        for _ in range(100):
            n = dict(az=(g["az"] + rng.gauss(0, 30 * s)) % 360, el=g["el"] + rng.gauss(0, 12 * s), a1=g["a1"] + rng.gauss(0, 10 * s),
                     a2=g["a2"] + rng.gauss(0, 10 * s), a3=g["a3"] + rng.gauss(0, 10 * s),
                     branch=g["branch"] if rng.random() > 0.12 else -g["branch"], order=[o if rng.random() > 0.12 else 1 - o for o in g["order"]])
            if feas(n): return n
        return g
    def cross(g1, g2):
        n = {k: (g1[k] if rng.random() < 0.5 else g2[k]) for k in ("az", "el", "a1", "a2", "a3", "branch")}
        n["order"] = [g1["order"][i] if rng.random() < 0.5 else g2["order"][i] for i in range(3)]
        return n if feas(n) else g1
    POP, ELITE, GENS = int(job.get("pop", 96)), int(job.get("elite", 16)), int(job.get("gens", 40))
    pop = [rand_d() for _ in range(POP)] + [dict(x) for x in job.get("init", [])]
    archive = []
    def score_all(gs):
        res = []
        for g in gs:
            try: r = evaluate(g)
            except Exception as ex: r = dict(cov=0.0, score=0.0, err=str(ex)[:200])
            rr = dict(g, **r); res.append(rr)
            if r.get("cov", 0) > 0: archive.append(rr)
        return res
    cur = sorted(score_all(pop), key=lambda r: -r.get("score", 0))[:ELITE]; sig = 1.0; hist = []
    for gen in range(GENS):
        kids = []
        for _ in range(POP):
            p1 = rng.choice(cur); p2 = rng.choice(cur)
            kids.append(mutate(cross(p1, p2) if rng.random() < 0.3 else p1, sig))
        prev = cur[0]["score"]
        cur = sorted(cur + score_all(kids), key=lambda r: -r.get("score", 0))[:ELITE]
        sig = max(0.2, sig * (0.9 if cur[0]["score"] <= prev + 1e-4 else 1.0))
        hist.append(round(cur[0]["score"], 4))
        if time.time() - t0 > float(job.get("max_secs", 4800)): break
    # Pareto front: coverage vs worst-link median gap
    pts = sorted(archive, key=lambda r: (-r["cov"]))
    front, best_gap = [], 1e9
    for r in pts:
        wg = max(r["per_link_p50"])
        if wg < best_gap - 0.05: front.append(r); best_gap = wg
    return {"best": cur, "front": front[:60], "hist": hist, "evals": len(archive), "secs": time.time() - t0,
            "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"}

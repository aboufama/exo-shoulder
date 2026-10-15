"""Band evaluator + evolutionary search for spherical N-R shoulder chains (GPU, torch).

The score is the one in full-exo/score_design.py, computed parametrically (no CAD):
  frame score = share (by area) of the mechanism's skin-facing underside that is 2..10 mm (normal gap) off the skin,
                if some spare-joint configuration keeps every member >= 2 mm off the skin, below any re-entry and
                collision-free; 0 if the exo has to be held there
  score       = weighted mean over the clip frames (overhead-type clips weighted up)

Chain: joints J1..JN, every axis through the GH centre. J1 axis b fixed in the scapula (base plate), JN axis W fixed on
the arm (BOTTOM's hub block), links k = 1..N-1 between pins p_k and p_k+1 with arc a_k. N-3 spare DOF: p_2..p_N-2
follow from the joint angles q (pose independent), p_N-1 from the two-circle closure (branch +-1).
Members: base (hub disc at J1), links (hub disc at both pins + ribbon), BOTTOM (lower member at JN, arm-fixed).
Each joint stacks a lower member (flat face F_J) and an upper one (F_J + STACK). Link undersides are free per sample
(shaped to the skin), hub faces are flat, ribbons leave each hub at <= RAMP.

Shape fitting per design (alternating): configs <- best feasible per frame given the shape; shape <- envelope of the
lower bounds over the frames kept, dropping the frames that force the shape up the most while that raises the score.

Job: {"mode": "band_eval" | "band_search", "skin": <b64 gz json from avg/radial_maps_v2.py>, "poses": <b64 from
pack_band.py>, "designs": [...] | search params, "n": N, "q_step": deg, ...}

Every link must have a real arm (docs/FINDINGS.md "Short link"): job keys "min_arc" (deg, default MIN_ARC = 35; raises
the lower end of "arc_range" in the search and rejects shorter links in evaluate before any work) and "min_arm_mm" (mm,
default MIN_ARM_MM = 10; clear gap between a link's two hub seats at the fitted hub heights, checked after the shape
fit). A rejected design scores -1 with "err" saying why; 0 switches a rule off (to re-score an old design).
N = 3 without a cuff is the pure 3R chain: no spare DOF (one configuration per pose, p2 from the two-circle closure).
"""
import base64, gzip, io, json, math, time, random, hashlib
try:
    import numpy as np                                         # the Flash build imports this file without numpy
except ImportError:
    np = None

_CACHE = {}
CODE_VERSION = "band-2026-10-15z (job key hw: link half-width; range first: score x min(1, workspace share / target)^w; why poses are lost; fit_clips; guards; pure 3R chain)"
RESD = 0.25; NWD, NHD = 1440, 720; LAT_LO, LAT_HI = -75.0, 90.0; CLEAR = 3.0
ROW0, ROW1 = int((LAT_LO + 90) / RESD), int((LAT_HI + 90) / RESD)
HUB_R, HW, T_LINK, STACK, T_W, T_BOT = 17.0, 7.0, 5.5, 6.0, 1.0, 6.5
T_LO, HUB_UP, CAP_UP, RAIL_D = 3.5, 5.05, 3.62, 4.0          # lower plate under the seat, upper hub, cap crown over it, cuff rail depth
D2R = math.pi / 180
# every link needs a real arm (docs/FINDINGS.md "Short link": r13's link 1 spanned 23.9 deg, its two hubs side by side).
# Job keys "min_arc" (deg) and "min_arm_mm" (mm); 0 switches a rule off (e.g. to re-score an old design).
MIN_ARC = 35.0          # smallest link arc, deg (the user's rule, ~35 deg at R ~60 mm)
MIN_ARM_MM = 10.0       # smallest clear gap between a link's two hub seats at the fitted hub heights, mm


# ---------------------------------------------------------------- link-arm guard (pure python: no torch, no maps)
def arm_clear_mm(a_deg, r0, r1=None, hub_r=None):
    """clear gap (mm) between the two hub seats of a link of arc a_deg whose hub centres sit r0 and r1 mm from the GH
    centre on their axes: straight distance between the hub centres minus two seat radii. This is how docs/FINDINGS.md
    measured the r13 short link (hub centres 24.7 mm apart, 1.7 mm between the O23 seats of radius 11.5)."""
    r1 = r0 if r1 is None else r1; hub_r = HUB_R if hub_r is None else hub_r
    return math.sqrt(max(0.0, r0 * r0 + r1 * r1 - 2 * r0 * r1 * math.cos(a_deg * D2R))) - 2 * hub_r


def arc_for_arm(arm_mm, r, hub_r=None):
    """smallest arc (deg) that leaves arm_mm clear between the hub seats with both hub centres r mm from GH"""
    hub_r = HUB_R if hub_r is None else hub_r
    x = (arm_mm + 2 * hub_r) / (2 * r)
    return 180.0 if x >= 1 else 2 * math.degrees(math.asin(x))


def link_arcs_ok(design, min_arc=MIN_ARC, r_ref=None, hub_r=None):
    """(ok, err) for the kinematic rule: every link (the N-1 arcs of design["a"]; plain N-R and sliding-cuff variants
    alike) spans >= min_arc deg. design: a design dict or the list of arcs. err names each short link and, for scale,
    its clear arm at r_ref (default 65 mm, the evaluator's R_REF) with seat radius hub_r (default HUB_R)."""
    a = design["a"] if isinstance(design, dict) else design
    if isinstance(design, dict) and "n" in design and len(a) != int(design["n"]) - 1:
        return False, f"design has {len(a)} link arcs for n = {design['n']} joints (needs n - 1)"
    bad = [(k + 1, float(x)) for k, x in enumerate(a) if float(x) < float(min_arc) - 1e-9]
    if not bad: return True, ""
    r_ref = 65.0 if r_ref is None else r_ref; hub_r = HUB_R if hub_r is None else hub_r
    return False, ("short link: " + ", ".join(f"link {k} arc {x:.1f} deg ({arm_clear_mm(x, r_ref, hub_r=hub_r):.1f} mm between hub seats at R {r_ref:g})"
                                              for k, x in bad) + f" < min_arc {float(min_arc):g} deg (docs/FINDINGS.md 'Short link'; min_arc=0 scores it anyway)")


def hub_heights(n, faces, lower, stack=None):
    """[(z_start, z_end)] per link k = 1..n-1: distance from GH of the link's hub plane at either joint, the way
    fit_shape lays the stack out (lower member at the joint face F_J, upper member at F_J + STACK; link n-1 rides on
    BOTTOM's hub at face F_n). faces / lower: the evaluator's fitted faces and lower-member map (int or str keys)."""
    stack = STACK if stack is None else stack
    F = {int(k): float(v) for k, v in faces.items() if str(k).isdigit() and v is not None}
    L = {int(k): int(v) for k, v in lower.items()}
    def z(mi, J): return F[n] if J == n else F[J] + (0.0 if L.get(J) == mi else stack)
    return [(z(mi, mi), z(mi, mi + 1)) for mi in range(1, n)]


def arms_ok(a, heights, min_arm_mm=MIN_ARM_MM, hub_r=None):
    """(ok, err, clear) for the physical rule: the clear gap between each link's hub seats (arm_clear_mm at the fitted
    hub heights) is >= min_arm_mm (<= 0: rule off). clear: mm per link."""
    hub_r = HUB_R if hub_r is None else hub_r
    clear = [arm_clear_mm(float(x), z0, z1, hub_r) for x, (z0, z1) in zip(a, heights)]
    bad = [(k + 1, c) for k, c in enumerate(clear) if float(min_arm_mm) > 0 and c < float(min_arm_mm) - 1e-9]
    if not bad: return True, "", clear
    return False, ("short arm: " + ", ".join(f"link {k} {c:.1f} mm between hub seats (arc {float(a[k - 1]):.1f} deg, hubs {heights[k - 1][0]:.1f} / "
                                             f"{heights[k - 1][1]:.1f} mm from GH, seat r {hub_r:g})" for k, c in bad)
                   + f" < min_arm_mm {float(min_arm_mm):g} (min_arm_mm=0 scores it anyway)"), clear


def design_link_report(design, arm_mm=None, min_arc=MIN_ARC, min_arm_mm=MIN_ARM_MM, r_ref=65.0, hub_r=None):
    """problems (list of str, empty = fine) of a searched design before it becomes CAD: links below min_arc deg and,
    when the clear gaps between hub seats are known (arm_mm, mm per link), arms below min_arm_mm"""
    probs = []
    ok, err = link_arcs_ok(design, min_arc, r_ref, hub_r)
    if not ok: probs.append(err)
    if arm_mm is not None and float(min_arm_mm) > 0:
        bad = [(k + 1, float(c)) for k, c in enumerate(arm_mm) if float(c) < float(min_arm_mm) - 1e-9]
        if bad: probs.append("short arm: " + ", ".join(f"link {k} {c:.1f} mm between hub seats" for k, c in bad) + f" < min_arm_mm {float(min_arm_mm):g}")
    return probs


def arc_bounds(job):
    """(lo, hi) arc bounds (deg) for the search samplers: arc_range with its lower end raised to min_arc"""
    amin, amax = [float(x) for x in job.get("arc_range", [20.0, 100.0])]
    lo = max(amin, float(job.get("min_arc", MIN_ARC)))
    if lo > amax: raise ValueError(f"min_arc / arc_range leave no arcs: [{lo:g}, {amax:g}] deg")
    return lo, amax


def make_samplers(job, rng):
    """the evolutionary search's (rand_d, mutate) for job["n"] joints: every arc they return lies in arc_bounds(job)"""
    N = int(job["n"]); free_w = job.get("free_w", True); amin, amax = arc_bounds(job)
    crange = job.get("cuff_range")                                    # sliding cuff on the upper arm (deg either way)
    def rand_d():
        g = dict(n=N, az=rng.uniform(0, 360), el=rng.uniform(-10, 90), a=[rng.uniform(amin, amax) for _ in range(N - 1)],
                 w=[rng.uniform(40, 140), rng.uniform(-90, 90)] if free_w else list(job.get("w0", [85.9, 0.0])),
                 branch=rng.choice([-1, 1]), order=[rng.randint(0, 1) for _ in range(N)])
        if crange: g["cuff"] = dict(range=float(rng.uniform(15, crange)) if job.get("search_range") else float(crange), branch=rng.choice([-1, 1]))
        if crange and job.get("w_range"): g["w"][0] = rng.uniform(*job["w_range"])
        return g
    def mutate(g, s):
        n = json.loads(json.dumps(g))
        n["az"] = (n["az"] + rng.gauss(0, 25 * s)) % 360; n["el"] = min(90, max(-10, n["el"] + rng.gauss(0, 10 * s)))
        n["a"] = [min(amax, max(amin, x + rng.gauss(0, 8 * s))) for x in n["a"]]
        if free_w: n["w"] = [min(170, max(10, n["w"][0] + rng.gauss(0, 10 * s))), n["w"][1] + rng.gauss(0, 20 * s)]
        if rng.random() < 0.1 * s: n["branch"] = -n["branch"]
        for k in range(N):
            if rng.random() < 0.08 * s: n["order"][k] = 1 - n["order"][k]
        if job.get("search_hm"): n["hm"] = min(4.0, max(0.8, n.get("hm", job.get("hub_margin", 2.0)) + rng.gauss(0, 0.4 * s)))
        if crange:
            n.setdefault("cuff", dict(range=float(crange), branch=1))
            n["cuff"]["range"] = (min(float(crange), max(10.0, n["cuff"]["range"] + rng.gauss(0, 8 * s))) if job.get("search_range") else float(crange))
            if job.get("w_range"): n["w"][0] = min(job["w_range"][1], max(job["w_range"][0], n["w"][0]))
            if rng.random() < 0.1 * s: n["cuff"]["branch"] = -n["cuff"].get("branch", 1)
        return n
    return rand_d, mutate


# ---------------------------------------------------------------- per-frame skin maps (GPU, exact)
MRES = 0.5                                                     # deg per map pixel
MH, MW = int((LAT_HI - LAT_LO) / MRES), int(360 / MRES)


def skin_samples(spacing=0.8, r_max=260.0, seed=0):
    """fixed barycentric samples on the render-skin faces near the shoulder (chosen at rest, ~spacing mm apart)"""
    import body_pose as BP
    F = BP.F; V0 = BP.V0
    near = np.nonzero(np.linalg.norm(V0[F].mean(1), axis=1) < r_max)[0]
    A0 = 0.5 * np.linalg.norm(np.cross(V0[F[near, 1]] - V0[F[near, 0]], V0[F[near, 2]] - V0[F[near, 0]]), axis=1)
    n = np.maximum(1, np.ceil(A0 / spacing ** 2)).astype(int); fi = np.repeat(near, n)
    uv = np.random.default_rng(seed).random((len(fi), 2)); fl = uv.sum(1) > 1; uv[fl] = 1 - uv[fl]
    return F, fi, uv


def build_frame_maps(POSE, dev, c=CLEAR, spacing=0.8, log=print):
    """for every frame: r1 (first skin exit from the GH centre, 0 = none), r1c (band start: >= c mm off the first
    sheet), r2c (band end before a re-entry sheet, inf = none), cs (cos of the skin slope along the ray). All skin
    (trunk and arm, posed by body_pose for that exact frame); clearance by splatting c-balls round every sample."""
    import torch, body_pose as BP
    t0 = time.time(); F, fi, uv = skin_samples(spacing)
    Ft = torch.tensor(F[fi], device=dev); U = torch.tensor(uv, device=dev, dtype=torch.float32)
    RES = MRES * D2R; LAT0 = LAT_LO * D2R
    lat_c = LAT0 + (torch.arange(MH, device=dev, dtype=torch.float32) + 0.5) * RES; lon_c = -math.pi + (torch.arange(MW, device=dev, dtype=torch.float32) + 0.5) * RES
    PIX = torch.stack([torch.cos(lat_c)[:, None] * torch.cos(lon_c)[None], torch.sin(lat_c)[:, None].expand(MH, MW), torch.cos(lat_c)[:, None] * torch.sin(lon_c)[None]], -1).reshape(-1, 3)
    S = MH * MW; NPf = len(POSE)
    R1 = torch.zeros((NPf, S), dtype=torch.float16, device=dev); R1C = torch.zeros_like(R1); R2C = torch.full_like(R1, float("inf")); CS = torch.ones_like(R1)
    for p in range(NPf):
        pl, el, ax, fx, pr = [float(x) for x in POSE[p]]
        X = torch.tensor(BP.posed(dict(plane=pl, elev=el, axial=ax, flex=fx, pron=pr)), device=dev, dtype=torch.float32)
        A_, B_, C_ = X[Ft[:, 0]], X[Ft[:, 1]], X[Ft[:, 2]]
        Q = A_ + U[:, :1] * (B_ - A_) + U[:, 1:] * (C_ - A_)
        rho = torch.linalg.norm(Q, dim=1); w = Q / rho[:, None]
        lat = torch.asin(torch.clamp(w[:, 1], -1, 1)); lon = torch.atan2(w[:, 2], w[:, 0])
        ii = torch.floor((lat - LAT0) / RES).long(); jj = torch.floor((lon + math.pi) / RES).long() % MW
        inr = (ii >= -40) & (ii < MH + 40)
        # first sheet: min radius over the pixel and its 1-ring (fills sampling holes)
        r1 = torch.full((S,), float("inf"), device=dev)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i2 = ii + di; ok = inr & (i2 >= 0) & (i2 < MH); idx = i2[ok] * MW + (jj[ok] + dj) % MW
                r1.scatter_reduce_(0, idx, rho[ok], "amin")
        r2 = torch.full((S,), float("inf"), device=dev)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                i2 = ii + di; ok = inr & (i2 >= 0) & (i2 < MH); idx = i2[ok] * MW + (jj[ok] + dj) % MW
                far = rho[ok] > r1[idx] + 4.0
                r2.scatter_reduce_(0, idx[far], rho[ok][far], "amin")
        # clearance band: splat the exit / entry radius of every sample's c-ball onto the rays it crosses
        r1c = torch.where(torch.isfinite(r1), r1 + 0.0, torch.zeros_like(r1)); r2c = torch.full((S,), float("inf"), device=dev)
        Ki = torch.ceil(torch.asin(torch.clamp(c / rho, max=1.0)) / RES).long() + 1
        Kj = torch.ceil(Ki.float() / torch.clamp(torch.cos(lat), min=0.02)).long()
        for kmax in (4, 8, 16, 32, 64, MW // 2):
            sel = inr & (Kj <= kmax) & (Kj > (kmax // 2 if kmax > 4 else -1))
            if not bool(sel.any()): continue
            iis, jjs, rs, ws, kis = ii[sel], jj[sel], rho[sel], w[sel], Ki[sel]
            ki = int(kis.max()); oi, oj = torch.meshgrid(torch.arange(-ki, ki + 1, device=dev), torch.arange(-kmax, kmax + 1, device=dev), indexing="ij")
            oi, oj = oi.reshape(-1), oj.reshape(-1); O = len(oi); step = max(1, int(2.5e7 // O))
            for s0 in range(0, len(rs), step):
                sl_ = slice(s0, s0 + step)
                i2 = iis[sl_, None] + oi[None]; ok = (i2 >= 0) & (i2 < MH) & (oi.abs()[None] <= kis[sl_, None])
                idx = (i2.clamp(0, MH - 1) * MW + (jjs[sl_, None] + oj[None]) % MW)
                cd = (ws[sl_, None, :] * PIX[idx]).sum(-1); tt = rs[sl_, None] ** 2 * torch.clamp(1 - cd ** 2, min=0)
                hit = ok & (tt < c * c) & (cd > 0)
                idx = idx[hit]; ro = rs[sl_, None].expand_as(cd)[hit]; cdh = cd[hit]; root = torch.sqrt(c * c - tt[hit])
                mid = 0.5 * (r1[idx] + torch.where(torch.isfinite(r2[idx]), r2[idx], r1[idx] + 1e3))
                first = ro < mid
                r1c.scatter_reduce_(0, idx[first], ro[first] * cdh[first] + root[first], "amax")
                r2c.scatter_reduce_(0, idx[~first], ro[~first] * cdh[~first] - root[~first], "amin")
        r1z = torch.where(torch.isfinite(r1), r1, torch.zeros_like(r1))
        r1c = torch.where(torch.isfinite(r1), torch.maximum(r1c, r1z + c), torch.zeros_like(r1c))
        # slope: cos of the angle between the ray and the skin normal, from the r1 gradient
        rr = torch.where(r1z > 0, r1z, torch.full_like(r1z, float("nan"))).reshape(MH, MW)
        dlat = torch.gradient(rr, spacing=RES, dim=0)[0]; dlon = torch.gradient(rr, spacing=RES, dim=1)[0] / torch.clamp(torch.cos(lat_c), min=0.05)[:, None]
        cs = torch.nan_to_num(torch.clamp(rr / torch.sqrt(rr ** 2 + dlat ** 2 + dlon ** 2), 0.2, 1.0), nan=1.0).reshape(-1)
        R1[p] = r1z.half(); R1C[p] = r1c.half(); R2C[p] = r2c.half(); CS[p] = cs.half()
        if p % 50 == 0: log(f"frame maps {p}/{NPf} {time.time() - t0:.0f}s ({len(rho)} skin samples)")
    return dict(r1=R1, r1c=R1C, r2c=R2C, cs=CS)


def load_poses(b64, dev):
    import torch
    Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(b64))), allow_pickle=False)
    P = {k: torch.tensor(Z[k], device=dev) for k in ("HG", "RS", "EL", "CID", "FI", "WT")}
    P["POSE"] = Z["POSE"]; P["NAMES"] = [str(x) for x in Z["NAMES"]]
    P["ENVELOPE"] = [str(x) for x in Z["ENVELOPE"]] if "ENVELOPE" in Z.files else []    # pack_envelope.py: clear, don't score
    return P


# ---------------------------------------------------------------- the evaluator
class Band:
    def __init__(self, job, dev):
        import torch
        self.t = torch; self.dev = dev; self.f32 = torch.float32
        key = hashlib.md5(job["poses"].encode()).hexdigest() + str(job.get("spacing", 0.8))
        if key not in _CACHE:
            t0 = time.time(); P = load_poses(job["poses"], dev)
            if job.get("stride"):
                k = int(job["stride"]); keep = np.arange(0, len(P["POSE"]), k)
                P = {kk: (v[keep] if hasattr(v, "shape") and len(v) == len(P["POSE"]) else v) for kk, v in P.items()}
            mc = job.get("maps_cache")
            if mc and __import__("os").path.exists(mc):
                import torch as _t; Z = _t.load(mc); M = {k: v.to(dev) for k, v in Z.items()}
            else:
                M = build_frame_maps(P["POSE"], dev, spacing=float(job.get("spacing", 0.8)))
                if mc: import torch as _t; _t.save({k: v.cpu() for k, v in M.items()}, mc)
            _CACHE.clear(); _CACHE[key] = (M, P); print(f"frame maps built in {time.time() - t0:.0f}s", flush=True)
        self.M, self.P = _CACHE[key]; self.S = MH * MW; self.stride = int(job.get("stride") or 1)
        cid, fi = self.P["CID"].cpu().numpy(), self.P["FI"].cpu().numpy()
        env = set(self.P.get("ENVELOPE", [])); self.env_ids = [k for k, n in enumerate(self.P["NAMES"]) if n in env]
        self.clip_frames = [np.nonzero(cid == k)[0][np.argsort(fi[cid == k])].tolist() for k in range(len(self.P["NAMES"])) if k not in self.env_ids]
        self.env_mask = (sum((self.P["CID"] == k) for k in self.env_ids) > 0) if self.env_ids else self.t.zeros(len(self.P["CID"]), dtype=self.t.bool, device=dev)
        self.env_weight = float(job.get("env_weight", 1.0))                # score x (share of envelope poses feasible) ** env_weight
        self.env_target = float(job.get("env_target", 1.0))                # user: "90% range first" -> share / target, capped at 1
        self.P["FPS_EFF"] = 10.0 / self.stride; self.max_rate = float(job.get("max_rate", 180.0))       # deg/s per spare joint
        self.G = float(job.get("G", 10.0)); self.R_REF = float(job.get("r_ref", 65.0)); self.RAMP = math.tan(math.radians(float(job.get("ramp_deg", 35.0))))
        self.SING = float(job.get("sing_deg", 10.0)) * D2R; self.q_step = float(job.get("q_step", 10.0))
        self.chunk = int(job.get("chunk", 48)); self.drop_rounds = int(job.get("drop_rounds", 80))
        fc = job.get("fit_clips")                                          # held-out split: shape, BOTTOM face and the kept
        nm = list(self.P["NAMES"]); self.fit_clips = [n for n in nm if n in fc] if fc else None     # iteration see these clips only
        self.fit_mask = (sum((self.P["CID"] == k) for k, n in enumerate(nm) if n in fc) > 0) if fc else self.t.ones(len(self.P["CID"]), dtype=self.t.bool, device=dev)
        self.fit_mask = self.fit_mask | self.env_mask                     # the envelope always shapes the design
        self.hub_relief = float(job.get("hub_relief", 0.0))                # mm the contoured hub underside may drop below the flat face
        self.balance = float(job.get("balance", 0.0))                      # blend in the mean of the 3 worst clips
        self.hub_margin0 = float(job.get("hub_margin", 2.0))               # contoured undersides keep this much spare clearance
        self.hub_margin = self.hub_margin0
        bar = job.get("bar", {})
        self.Wbar = self._unit(torch.tensor(bar.get("W", [0.0, -0.0713, 0.9975]), device=dev, dtype=self.f32))
        d_ = torch.tensor(bar.get("dir", [0.0, -0.9975, -0.0713]), device=dev, dtype=self.f32)
        self.Dbar = self._unit(d_ - (d_ @ self.Wbar) * self.Wbar); self.Ebar = torch.cross(self.Wbar, self.Dbar, dim=-1)
        self.zbar = float(bar.get("z0", 67.5)); self.jog = (float(bar.get("jog0", 34.0)), float(bar.get("jog1", 56.0)), float(bar.get("jog", 8.6)))
        self.WT = self.P["WT"]
        self.b_ant_max = float(job.get("b_ant_max", 0.15)); self.neck_cfg = job.get("neck"); self.mount_dir = job.get("mount_dir", [0.0, 0.6, -0.8])
        self.min_arc = float(job.get("min_arc", MIN_ARC)); self.min_arm = float(job.get("min_arm_mm", MIN_ARM_MM))   # every link has a real arm

    # -- helpers
    def _unit(self, x): return x / (self.t.linalg.norm(x, dim=-1, keepdim=True) + 1e-12)
    def pix(self, w):
        t = self.t
        lon = t.atan2(w[..., 2], w[..., 0]); lat = t.asin(t.clamp(w[..., 1], -1, 1))
        j = t.floor((lon + math.pi) / (MRES * D2R)).long() % MW; i = t.clamp(t.floor((lat - LAT_LO * D2R) / (MRES * D2R)).long(), 0, MH - 1)
        return i * MW + j
    def look(self, name, fidx, flat):
        """map `name` of frame fidx (broadcast) at flat pixel index"""
        return self.M[name].view(-1)[fidx * self.S + flat].float()

    def footprint(self, theta, hubs=(True, True), ribbon=True):
        """samples of a link in its local frame (start pin = x, end pin at angle theta in xy). Returns dict of tensors:
        dirs (I,3), kind (0 ribbon / 1 start hub / 2 end hub), cosa (hub: cos of the angle off the hub axis), dA/dB
        (mm along the arc from either end), w (area weight), col (collision centreline samples: index list), crad"""
        R = self.R_REF; pts, kind, cosa, dA, dB, wt = [], [], [], [], [], []; ring = []
        s0 = math.atan((HUB_R + 0.75) / R); ns = max(3, int(round((theta - 2 * s0) * R / 5.0)))
        ss = np.linspace(s0, max(s0 + 1e-3, theta - s0), ns)
        for s in (ss if ribbon else []):
            for w in (-HW + 0.5, 0.0, HW - 0.5):
                d = np.array([math.cos(s), math.sin(s), w / R]); pts.append(d / np.linalg.norm(d)); kind.append(0); cosa.append(1.0)
                dA.append(s * R); dB.append((theta - s) * R); wt.append(2 * HW * (ss[-1] - ss[0]) * R / max(1, ns - 1) / 3 if ns > 1 else 1.0); ring.append(0)
        for end, ang in ((0, 0.0), (1, theta)):
            if not hubs[end]: continue
            c = np.array([math.cos(ang), math.sin(ang), 0.0]); t1 = np.array([-math.sin(ang), math.cos(ang), 0.0]); t2 = np.array([0, 0, 1.0])
            RINGS = ((0.0, 1), (0.55 * HUB_R, 8), (HUB_R - 1.5, 12), (HUB_R - 0.4, 16)); NH = sum(n_ for _, n_ in RINGS)
            for ri, (rr, nphi) in enumerate(RINGS):
                for k in range(nphi):
                    ring.append(ri)
                    phi = 2 * math.pi * k / nphi; al = math.atan(rr / R)
                    d = math.cos(al) * c + math.sin(al) * (math.cos(phi) * t1 + math.sin(phi) * t2)
                    pts.append(d / np.linalg.norm(d)); kind.append(1 + end); cosa.append(math.cos(al)); dA.append(0.0); dB.append(0.0)
                    wt.append(math.pi * HUB_R ** 2 / NH)
        t = self.t
        out = dict(dirs=t.tensor(np.array(pts), device=self.dev, dtype=self.f32), kind=t.tensor(kind, device=self.dev),
                   cosa=t.tensor(cosa, device=self.dev, dtype=self.f32), dA=t.tensor(dA, device=self.dev, dtype=self.f32),
                   dB=t.tensor(dB, device=self.dev, dtype=self.f32), w=t.tensor(wt, device=self.dev, dtype=self.f32), ring=t.tensor(ring, device=self.dev))
        kd = np.array(kind); cen = [i for i in range(len(kind)) if kd[i] == 0 and i % 3 == 1]
        hubc = [i for i in range(len(kind)) if kd[i] > 0 and (i == 0 or kd[i - 1] != kd[i])]
        out["col"] = t.tensor(cen + hubc, device=self.dev); out["crad"] = t.tensor([HW] * len(cen) + [HUB_R] * len(hubc), device=self.dev, dtype=self.f32)
        out["ckind"] = t.tensor([0] * len(cen) + [int(kd[i]) for i in hubc], device=self.dev)
        return out

    def chain(self, d, HG):
        """pins (Pn, C, N, 3) in the scapula frame + validity (Pn, C) for poses with humerus rotations HG (Pn,3,3).
        Optional sliding cuff (d["cuff"] = {"range": deg, "branch": +-1}): JN's axis W turns about the humerus axis by
        phi (the cuff slides round the arm). N >= 4: phi is one more spare coordinate of the grid. N == 3: phi closes the
        chain (p3 on W's cone round the humerus with angle a2 to p2), the base joint angle is the spare.
        N == 3 without a cuff is the pure 3R chain (3 DOF): m = 0, a single configuration (C = 1, Q of shape (1, 0)),
        p2 from the two-circle closure of b and HG W on the design's branch; tri_ok keeps J2 sing_deg away from the
        3R singularity (all three axes coplanar). Nothing else is spare, so joint speeds are not limited (max_rate)."""
        t = self.t; N = d["n"]; A = [x * D2R for x in d["a"]]; cuff = d.get("cuff")
        b = t.tensor(bvec(d["az"], d["el"]), device=self.dev, dtype=self.f32)
        W0 = t.tensor(w_dir(*d["w"]), device=self.dev, dtype=self.f32); hA = t.tensor([0.0, -1.0, 0.0], device=self.dev)
        qs = t.arange(0, 360, self.q_step, device=self.dev, dtype=self.f32) * D2R; nq = len(qs)
        m = N - 3 if not (cuff and N == 3) else 1                    # spare joint angles along the chain
        dims, wraps = [nq] * m, [True] * m; axes = [qs] * m
        if cuff and N >= 4:
            rg = float(cuff.get("range", 90.0)); ph = t.arange(-rg, rg + 1e-6, self.q_step, device=self.dev, dtype=self.f32) * D2R
            dims.append(len(ph)); wraps.append(False); axes.append(ph)
        Q = t.zeros((1, 0), device=self.dev) if not axes else t.stack(t.meshgrid(*axes, indexing="ij"), -1).reshape(-1, len(axes))
        C = Q.shape[0]; self._grid = (dims, wraps)
        e = self._unit(t.cross(b, t.tensor([0.0, 1.0, 0.0], device=self.dev), dim=-1)); f = t.cross(b, e, dim=-1)
        pins = [b.expand(C, 3)]
        for k in range(m):                                            # p_{k+2} from p_{k+1} at joint angle Q[:, k]
            pk = pins[-1]
            if k == 0: ek, fk = e.expand(C, 3), f.expand(C, 3)
            else: prev = pins[-2]; ek = self._unit(prev - (prev * pk).sum(-1, keepdim=True) * pk); fk = t.cross(pk, ek, dim=-1)
            pins.append(math.cos(A[k]) * pk + math.sin(A[k]) * (t.cos(Q[:, k])[:, None] * ek + t.sin(Q[:, k])[:, None] * fk))
        Pn = HG.shape[0]
        def rot_about(axis, ang, v):                                  # Rodrigues, batched over ang
            ca, sa = t.cos(ang)[..., None], t.sin(ang)[..., None]
            return v * ca + t.cross(axis.expand_as(v), v, dim=-1) * sa + axis * (axis * v).sum(-1, keepdim=True) * (1 - ca)
        if cuff and N == 3:
            # p3 = HG W(phi): cos(a2) = p2 . p3  ->  A cos(phi) + B sin(phi) = Cc
            h = (HG @ hA)[:, None].expand(Pn, C, 3); w0 = (HG @ W0)[:, None].expand(Pn, C, 3)
            cd = (w0 * h).sum(-1, keepdim=True); wp = w0 - cd * h; ws = t.cross(h, wp, dim=-1)          # cone: cd h + cos phi wp + sin phi ws
            p2 = pins[-1][None].expand(Pn, C, 3)
            Aa = (p2 * wp).sum(-1); Bb = (p2 * ws).sum(-1); Cc = math.cos(A[1]) - cd[..., 0] * (p2 * h).sum(-1)
            rr = t.sqrt(Aa ** 2 + Bb ** 2) + 1e-9; ok = (Cc / rr).abs() <= 1.0
            phi = t.atan2(Bb, Aa) + float(cuff.get("branch", 1)) * t.acos(t.clamp(Cc / rr, -1, 1))
            phi = (phi + math.pi) % (2 * math.pi) - math.pi; rg = float(cuff.get("range", 90.0)) * D2R
            ok &= phi.abs() <= rg
            pz = cd * h + t.cos(phi)[..., None] * wp + t.sin(phi)[..., None] * ws
            P = t.stack([pins[0][None].expand(Pn, C, 3), p2, pz], 2)
            self._phi = phi
        else:
            if cuff and N >= 4: Wc = rot_about(hA, Q[:, -1], W0.expand(C, 3)); pz = t.einsum("pij,cj->pci", HG, Wc)
            else: pz = (HG @ W0)[:, None].expand(Pn, C, 3)
            pa = pins[-1][None].expand(Pn, C, 3)
            pc, ok = circ_int(t, pa, A[N - 3], pz, A[N - 2], float(d["branch"]))
            P = t.stack([p[None].expand(Pn, C, 3) for p in pins] + [pc, pz], 2)
        for k in range(1, N - 1):                                     # every inner joint away from its fold / stretch singularity
            ok &= tri_ok(t, P[:, :, k - 1], P[:, :, k + 1], A[k - 1], A[k], self.SING)
        return P, ok, Q

    @staticmethod
    def _reject(err, **extra):
        """result of a design that is infeasible before / regardless of the score"""
        return dict(dict(score=-1.0, follow=0.0, in_band=0.0, score_plain=0.0, score_unweighted=0.0, follow_unweighted=0.0, zj4=0.0, C=0, clips={}, err=err), **extra)

    def evaluate(self, d, detail=False):
        self.hub_margin = float(d.get("hm", self.hub_margin0))                # per-design contour margin (searched)
        ok_, err_ = link_arcs_ok(d, self.min_arc, self.R_REF, HUB_R)          # every link a real arm (FINDINGS "Short link")
        if not ok_: return self._reject(err_)
        if bvec(d["az"], d["el"])[0] > self.b_ant_max:                       # J1 on the front of the shoulder: no back anchor
            return self._reject("J1 anterior")
        t = self.t; N = d["n"]; A = [x * D2R for x in d["a"]]; order = d.get("order", [1] * N)
        HG, RS = self.P["HG"], self.P["RS"]; NP = HG.shape[0]
        # members: 0 = base (hub at J1 only), k = 1..N-1 links. lower[J] = which member is lower at joint J (1..N-1)
        FP = [self.footprint(0.0, hubs=(False, True), ribbon=False)] + [self.footprint(A[k], (True, True)) for k in range(N - 1)]
        lower = {J: (J - 1 if order[J - 1] == 1 else J) for J in range(1, N)}                  # member index
        # sample bookkeeping: member, joint of each hub sample, scored?
        segs = []
        for mi, fp in enumerate(FP):
            kind = fp["kind"]
            J_of = t.where(kind == 1, t.full_like(kind, mi), t.where(kind == 2, t.full_like(kind, mi + 1), t.zeros_like(kind)))
            if mi == 0: J_of = t.where(kind == 2, t.ones_like(kind), J_of)
            segs.append(J_of)
        # ---- per (pose, config, sample) bounds, chunked over poses
        LO, CAP, HI, VALID, COLD = [], [], [], [], []
        Qgrid = None
        for c0 in range(0, NP, self.chunk):
            sl = slice(c0, min(NP, c0 + self.chunk)); hg, rs = HG[sl], RS[sl]
            fidx = t.arange(sl.start, sl.stop, device=self.dev)
            pins, ok, Qgrid = self.chain(d, hg); Pn, C = ok.shape
            lo_l, cap_l, hi_l, cold = [], [], [], []
            for mi, fp in enumerate(FP):
                if mi == 0:
                    a_ = pins[:, :, 0]; ref = pins[:, :, 1]; n_ = self._unit(ref - (a_ * ref).sum(-1, keepdim=True) * a_)
                    Fm = t.stack([a_, n_, t.cross(a_, n_, dim=-1)], -1); loc = fp["dirs"]                # base hub around b
                else:
                    a_ = pins[:, :, mi - 1]; c_ = pins[:, :, mi]; n_ = self._unit(c_ - (a_ * c_).sum(-1, keepdim=True) * a_)
                    Fm = t.stack([a_, n_, t.cross(a_, n_, dim=-1)], -1); loc = fp["dirs"]
                w = t.einsum("pcij,mj->pcmi", Fm, loc)                                                # scapula frame
                it = self.pix(t.einsum("pij,pcmj->pcmi", rs, w)); fx = fidx[:, None, None].expand_as(it)    # thorax frame = map frame
                sk, cs = self.look("r1", fx, it), self.look("cs", fx, it)
                lo_l.append((self.look("r1c", fx, it) - 1.0).half())                                     # >= 2 mm off the skin
                cap_l.append((sk + self.G / t.clamp(cs, min=0.35)).half())                              # normal gap <= G
                hi_l.append((self.look("r2c", fx, it) + 0.5 - T_LINK).half())                            # top below any re-entry
                cold.append(w[:, :, fp["col"]].half())
            cold = dict(w=cold, hg=hg)
            LO.append(t.cat(lo_l, 2)); CAP.append(t.cat(cap_l, 2)); HI.append(t.cat(hi_l, 2)); VALID.append(ok); COLD.append(cold)
        LO = t.cat(LO, 0).float(); CAP = t.cat(CAP, 0).float(); HI = t.cat(HI, 0).float(); VALID = t.cat(VALID, 0)
        # sliding cuff: an arm-fixed guide rail round the humerus axis carries JN's carriage. It is shoulder metal too:
        # arc of W's cone over the cuff range (+ the carriage's half-width), 12 mm wide; contoured underside, turned top
        self._rail = None
        cuff = d.get("cuff")
        if cuff:
            W0 = t.tensor(w_dir(*d["w"]), device=self.dev, dtype=self.f32); hA = t.tensor([0.0, -1.0, 0.0], device=self.dev)
            dl_ = math.acos(max(-1.0, min(1.0, float(W0 @ hA)))); sd = max(math.sin(dl_), 0.2)
            rg = float(cuff.get("range", 90.0)) * D2R + math.atan(HUB_R / self.R_REF) / sd
            phs = t.arange(-rg, rg + 1e-6, 4.0 * D2R, device=self.dev); ax2 = self._unit(t.cross(hA, W0, dim=-1))   # meridian tilt axis
            dirs_r, wr = [], []
            for off_ in (-5.0, 0.0, 5.0):
                c_, s_ = math.cos(off_ / self.R_REF), math.sin(off_ / self.R_REF)
                Wt = W0 * c_ + t.cross(ax2, W0, dim=-1) * s_                                       # tilted toward / away from the arm axis
                for ph_ in phs:
                    ca, sa = math.cos(float(ph_)), math.sin(float(ph_))
                    v = Wt * ca + t.cross(hA, Wt, dim=-1) * sa + hA * (hA @ Wt) * (1 - ca); dirs_r.append(v)
                    wr.append(4.0 * D2R * self.R_REF * sd * 12.0 / 3.0)
            DR = t.stack(dirs_r); wr = t.tensor(wr, device=self.dev, dtype=self.f32)
            wt_r = t.einsum("pij,pjk,mk->pmi", RS, HG, DR); flat = self.pix(wt_r); fx = t.arange(NP, device=self.dev)[:, None].expand_as(flat)
            sk_r, cs_r = self.look("r1", fx, flat), self.look("cs", fx, flat)
            self._rail = dict(LO=self.look("r1c", fx, flat) - 1.0, CAP=sk_r + self.G / t.clamp(cs_r, min=0.35), w=wr, dirs=DR)
        lower_ = {J: (J - 1 if order[J - 1] == 1 else J) for J in range(1, N)}
        self._aux = self.aux_parts(d, lower_)
        for ax_ in self._aux:
            dirs = ax_["dirs"]
            wt_ = t.einsum("pij,pjk,mk->pmi", RS, HG, dirs) if ax_["frame"] == "can" else t.einsum("pij,mj->pmi", RS, dirs)
            flat = self.pix(wt_); fx = t.arange(NP, device=self.dev)[:, None].expand_as(flat)
            ax_["LO"] = self.look("r1c", fx, flat) - 1.0; ax_["CAP"] = self.look("r1", fx, flat) + self.G / t.clamp(self.look("cs", fx, flat), min=0.35)
            ax_["col"] = t.arange(1, dirs.shape[0], 3, device=self.dev)                          # centre row
        C = VALID.shape[1]
        sizes = [fp["dirs"].shape[0] for fp in FP]; offs = np.r_[0, np.cumsum(sizes)]
        I = int(offs[-1])
        # sample attributes over the concatenated index
        kindA = t.cat([fp["kind"] for fp in FP]); cosA = t.cat([fp["cosa"] for fp in FP]); dAA = t.cat([fp["dA"] for fp in FP]); dBA = t.cat([fp["dB"] for fp in FP])
        wA = t.cat([fp["w"] for fp in FP]); memA = t.cat([t.full((s,), mi, device=self.dev) for mi, s in enumerate(sizes)]); JA = t.cat(segs)
        self._ringA = t.cat([fp["ring"] for fp in FP])
        hubm = kindA > 0
        # which hub samples are on the lower member of their joint (scored + define the face), upper ones (face + STACK)
        is_low = t.zeros(I, dtype=t.bool, device=self.dev); is_bot = t.zeros(I, dtype=t.bool, device=self.dev)
        for J in range(1, N + 1):
            mJ = hubm & (JA == J)
            if J == N: is_bot |= mJ; continue                                                        # link N-1 sits on BOTTOM
            is_low |= mJ & (memA == lower[J])
        scored = (kindA == 0) | is_low | is_bot                     # at JN the lowest metal is BOTTOM's hub (face zj4): scored there
        wS = t.where(scored, wA, t.zeros_like(wA))
        # BOTTOM hub face: clear of the arm skin under the disc at every bin (arm-fixed)  -> link N-1 face on top
        self._zj4_fixed = d.get("zj4_fixed")                                                       # None: fitted with the shape
        zj4 = self._zj4_fixed if self._zj4_fixed is not None else self.bottom_face(d)
        F_top_bottom = zj4 + T_BOT + T_W
        self._bot_gap = (zj4 - F_top_bottom)                                   # scored height offset of the JN samples (BOTTOM's disc under link N-1)
        # ---- collisions need heights: computed inside the loop
        rng_iters = int(d.get("iters", 4)); WT = self.WT; BIG = 1e4; ar = t.arange(NP, device=self.dev)
        # spare-joint paths are continuous along every clip (<= max_rate deg/s): the shape is fitted to such paths
        NBR = self.neighbours(None, Qgrid)
        wn = wA / wA.sum()
        init_mode = d.get("init_path", "hug")
        if init_mode == "hug": val0 = t.where(VALID, -(LO * wn).sum(-1), t.full((NP, C), -BIG, device=self.dev))          # hug: lowest skin
        else:                                                                                       # 'band': most samples with a non-empty band
            val0 = t.where(VALID, ((CAP - LO).clamp(min=0, max=8.0) * wn).sum(-1), t.full((NP, C), -BIG, device=self.dev))
        path = self.dp_path(val0, NBR); keep = self.fit_mask.clone()          # fit_clips: held-out frames never shape the design
        best = None
        for it_ in range(rng_iters):
            h, S, sc, zj4 = self.fit_shape(LO[ar, path], CAP[ar, path], keep, wS, kindA, cosA, dAA, dBA, JA, memA, is_low, is_bot, F_top_bottom, N, lower)
            hl = t.where(is_bot, self._bot_under, h)                                                   # lowest metal (BOTTOM's disc at JN)
            if __import__('os').environ.get('BAND_DEBUG2'):
                for mi_ in range(N):
                    o0 = int(offs[mi_]); kk_ = kindA[o0:int(offs[mi_ + 1])]; hh_ = h[o0:int(offs[mi_ + 1])]
                    print(f'      member {mi_}: hub-centre h', [round(float(hh_[(kk_ == q_).nonzero()[0, 0]]), 1) for q_ in (1, 2) if bool((kk_ == q_).any())], 'is_low', [bool(is_low[o0 + int((kk_ == q_).nonzero()[0, 0])]) for q_ in (1, 2) if bool((kk_ == q_).any())], flush=True)
            feas = VALID & (LO <= hl[None, None] + 1e-3).all(-1) & (h[None, None] <= HI + 1e-3).all(-1)
            if __import__('os').environ.get('BAND_DEBUG'):
                f_lo = VALID & (LO <= hl[None, None] + 1e-3).all(-1); f_hi = VALID & (h[None, None] <= HI + 1e-3).all(-1); col = self.collisions(COLD, FP, h, offs, N, lower, Qgrid, d)
                print(f"    lo-ok {float(f_lo.any(1).float().mean()):.2f} hi-ok {float(f_hi.any(1).float().mean()):.2f} nocol {float((VALID & ~col).any(1).float().mean()):.2f}", flush=True)
            colm = self.collisions(COLD, FP, h, offs, N, lower, Qgrid, d)
            if bool(self.env_mask.any()):                                                          # why workspace poses are lost (per constraint)
                f_lo_ = (LO <= hl[None, None] + 1e-3).all(-1); f_hi_ = (h[None, None] <= HI + 1e-3).all(-1)
            feas &= ~colm
            share = ((hl[None, None] <= CAP + 1e-3).float() * wS).sum(-1); den = wS.sum()
            if self._rail is not None:
                ru = self._faces_full["rail_under"]; rw = self._rail["w"]
                rail_in = ((ru[None] <= self._rail["CAP"] + 1e-3).float() * rw).sum(-1)               # (NP,)
                share = share + rail_in[:, None]; den = den + rw.sum()
                feas = feas & (self._rail["LO"] <= ru[None] + 1e-3).all(-1)[:, None]
            for ax_, u_ in zip(self._aux, self._faces_full["aux_under"]):
                share = share + ((u_[None] <= ax_["CAP"] + 1e-3).float() * ax_["w"]).sum(-1)[:, None]; den = den + ax_["w"].sum()
                feas = feas & (ax_["LO"] <= u_[None] + 1e-3).all(-1)[:, None]
            share = share / den
            viol = (t.clamp(LO - hl[None, None], min=0) * wn).sum(-1)                                  # mm below the shape, area-weighted
            val = t.where(feas, 1.0 + share, t.where(VALID, -0.05 * viol, t.full_like(share, -BIG)))
            path = self.dp_path(val, NBR)
            fe = feas[ar, path]; frame = t.where(fe, share[ar, path], t.zeros_like(share[:, 0]))
            env_why = None
            if bool(self.env_mask.any()):
                em = self.env_mask; pv = path[em]; ae = ar[em]
                env_why = dict(kinematics=float((~VALID[ae, pv]).float().mean()), skin_above_shape=float((VALID[ae, pv] & ~f_lo_[ae, pv]).float().mean()),
                               squeezed_top=float((VALID[ae, pv] & ~f_hi_[ae, pv]).float().mean()), part_collision=float((VALID[ae, pv] & colm[ae, pv]).float().mean()))
            score = float((frame * WT).sum() / WT.sum()); follow = float((fe.float() * WT).sum() / WT.sum())
            env_follow = float(fe[self.env_mask].float().mean()) if bool(self.env_mask.any()) else None
            if self.balance > 0:                                                                       # favour designs good in every clip
                cs_ = sorted(float(frame[t.tensor(fr_, device=self.dev)].mean()) for fr_ in self.clip_frames)
                score = (1 - self.balance) * score + self.balance * sum(cs_[:3]) / 3
            if env_follow is not None: score = score * min(1.0, env_follow / self.env_target) ** self.env_weight   # range first: full credit from the target up
            if __import__('os').environ.get('BAND_DEBUG'): print(f'  iter {it_}: fit {sc:.3f} -> path score {score:.3f} follow {follow:.3f} valid-any {float(VALID.any(1).float().mean()):.2f} feas-any {float(feas.any(1).float().mean()):.2f} zj4 {zj4:.1f}', flush=True)
            fm = self.fit_mask; sel = float((frame * WT)[fm].sum() / WT[fm].sum()) if self.fit_clips else score
            if best is None or sel > best["sel"]:
                best = dict(sel=sel, score=score, follow=follow, env_follow=env_follow, env_why=env_why, h=h.clone(), zj4=zj4, bot_under=self._bot_under.clone(), faces=dict(self._faces),
                            rail_under=(self._faces_full["rail_under"].clone() if self._rail is not None else None), frame=frame.clone(), cfg=path.clone(), feas=fe.clone(),
                            feas_all=feas.clone() if detail else None, share_all=share.clone() if detail else None)
        if __import__('os').environ.get('BAND_STASH'):                                             # analysis hook (pipeline/conformal/inband_ceiling.py)
            self._stash = dict(LO=LO, CAP=CAP, cfg=best["cfg"], feas=best["feas"], h=best["h"], bot_under=best["bot_under"], wS=wS, memA=memA, kindA=kindA, is_bot=is_bot, is_low=is_low, scored=scored)
        # the physical arm rule at the fitted hub heights: the deg rule alone lets hubs near GH (or big hubs) touch
        arm_ok_, arm_err, arm_mm = arms_ok(d["a"], hub_heights(N, best["faces"], lower, STACK), self.min_arm, HUB_R)
        arm_mm = [round(c, 2) for c in arm_mm]
        if not arm_ok_: return self._reject(arm_err, arm_mm=arm_mm, score_unchecked=best["score"], follow_unchecked=best["follow"])
        out = dict(score=best["score"], follow=best["follow"], score_plain=float((best["frame"] * WT).sum() / WT.sum()),
                   score_unweighted=float(best["frame"][~self.env_mask].mean()), follow_unweighted=float(best["feas"][~self.env_mask].float().mean()),
                   in_band=float(best["frame"][best["feas"] & ~self.env_mask].mean()) if bool((best["feas"] & ~self.env_mask).any()) else 0.0, zj4=float(best["zj4"]), C=C, arm_mm=arm_mm,
                   min_arc=self.min_arc, min_arm_mm=self.min_arm)
        if self.fit_clips:
            fm = self.fit_mask; out["fit_clips"] = self.fit_clips; out["score_fit"] = best["sel"]
            out["follow_fit"] = float((best["feas"].float() * WT)[fm].sum() / WT[fm].sum())
        names = self.P["NAMES"]; cid = self.P["CID"]
        out["clips"] = {names[k]: dict(score=float(best["frame"][cid == k].mean()), follow=float(best["feas"][cid == k].float().mean())) for k in range(len(names)) if k not in self.env_ids}
        if self.env_ids: out["envelope"] = dict(poses=int(self.env_mask.sum()), follow=best["env_follow"], weight=self.env_weight, target=self.env_target, lost_because=best["env_why"])
        if detail or d.get("diag"):
            # where the in-band share is lost: per sample class, over the followed frames of the best path
            hb = best["h"]; cfgb = best["cfg"]; fe = best["feas"]
            hs = t.where(is_bot, best["bot_under"], hb)
            CAPp = CAP[ar, cfgb][fe]; LOp = LO[ar, cfgb][fe]
            # normal gap = (h - skin) * cs, with skin = CAP - G/cs  ->  gap = G - (CAP - h) * cs  (cs recovered from CAP & r1 is not stored: use CAP-h)
            over = (hs[None] - CAPp)                                                                 # > 0: more than G off
            cls = t.where(is_bot, t.full_like(kindA, 3), t.where(kindA == 0, t.zeros_like(kindA), t.where(is_low, t.ones_like(kindA), t.full_like(kindA, 2))))
            diag = {}
            for c_, nm in ((0, "ribbons"), (1, "lower hubs"), (3, "BOTTOM hub (JN)")):
                mm = (cls == c_) & scored
                if not bool(mm.any()) or not bool(fe.any()): continue
                o = over[:, mm]; w_ = wS[mm][None].expand_as(o)
                diag[nm] = dict(area_share=float(wS[mm].sum() / wS.sum()), in_band=float(((o <= 1e-3).float() * w_).sum() / w_.sum()),
                                too_far_mm_median=float(o[o > 0].median()) if bool((o > 0).any()) else 0.0)
            for mi in range(N):
                mm = (memA == mi) & scored
                if bool(mm.any()) and bool(fe.any()): o = over[:, mm]; w_ = wS[mm][None].expand_as(o); diag[f"member {mi}"] = float(((o <= 1e-3).float() * w_).sum() / w_.sum())
            out["diag"] = diag
        if detail:
            out["h"] = best["h"].tolist(); out["cfg"] = best["cfg"].tolist(); out["feasible"] = best["feas"].tolist(); out["frame"] = best["frame"].tolist()
            out["sizes"] = sizes; out["kind"] = kindA.tolist(); out["Q"] = Qgrid.tolist()
            out["dirs_local"] = [fp["dirs"].tolist() for fp in FP]; out["cosa"] = cosA.tolist(); out["lower"] = {str(k): v for k, v in lower.items()}
            fa = best["feas_all"].cpu().numpy(); sa = np.round(best["share_all"].clamp(0, 1).cpu().numpy() * 255).astype(np.uint8)
            out["feas_all"] = base64.b64encode(np.packbits(fa, axis=None).tobytes()).decode(); out["share_all"] = base64.b64encode(sa.tobytes()).decode()
            out["PC"] = list(fa.shape); out["q_step"] = self.q_step; out["stride"] = self.stride
            out["faces"] = {str(k): v for k, v in best["faces"].items()}; out["bot_under"] = best["bot_under"].tolist(); out["is_low"] = is_low.tolist(); out["is_bot"] = is_bot.tolist()
            out["hub_r"] = HUB_R; out["stack"] = STACK; out["t_link"] = T_LINK; out["cuff"] = d.get("cuff"); out["hm"] = self.hub_margin
            if self._rail is not None: out["rail_dirs"] = self._rail["dirs"].tolist(); out["rail_under"] = best["rail_under"].tolist()
        return out

    def neighbours(self, m, Qgrid):
        """(C, nb) configuration indices reachable in one frame: every grid coordinate moves <= K steps (spare joints
        wrap round, the cuff angle does not)"""
        t = self.t; dims, wraps = self._grid
        if not dims: return t.zeros((1, 1), dtype=t.long, device=self.dev)
        fps = float(self.P.get("FPS_EFF", 10.0)); K = max(1, int(math.ceil(self.max_rate / fps / self.q_step - 1e-9)))
        md = len(dims); MI = t.stack(t.meshgrid(*[t.arange(n_, device=self.dev) for n_ in dims], indexing="ij"), -1).reshape(-1, md)
        off = t.stack(t.meshgrid(*[t.arange(-K, K + 1, device=self.dev)] * md, indexing="ij"), -1).reshape(-1, md)
        nb = MI[:, None, :] + off[None]
        for k_ in range(md):
            if wraps[k_]: nb[..., k_] %= dims[k_]
            else: nb[..., k_] = nb[..., k_].clamp(0, dims[k_] - 1)
        mul = t.tensor([int(np.prod(dims[k_ + 1:])) for k_ in range(md)], device=self.dev)
        return (nb * mul).sum(-1)
    def dp_path(self, val, NBR):
        """per clip: the configuration path maximising the summed frame values, moving only to neighbours"""
        t = self.t; path = t.zeros(val.shape[0], dtype=t.long, device=self.dev)
        for fr in self.clip_frames:
            V = val[fr[0]].clone(); ptrs = []
            for f in fr[1:]:
                cand = V[NBR]; bv, bi = cand.max(1); ptrs.append(NBR.gather(1, bi[:, None])[:, 0]); V = bv + val[f]
            c = int(V.argmax()); path[fr[-1]] = c
            for k in range(len(fr) - 2, -1, -1): c = int(ptrs[k][c]); path[fr[k]] = c
        if bool(self.env_mask.any()): path = t.where(self.env_mask, val.argmax(1), path)        # no time order: best per pose
        return path

    def aux_parts(self, d, lower):
        """arm-fixed neck from JN's hub (or the cuff track's end) to BOTTOM's cut end, and the base's mounting tab toward
        the back plate when the base is the lower member at J1. Directions only (heights are fitted like ribbons)."""
        t = self.t; out = []; R = self.R_REF
        nk = self.neck_cfg
        if nk is not None:
            W0 = np.array(w_dir(*d["w"])); pb = np.array(nk["p_bar"], float); eb = pb / np.linalg.norm(pb); hA = np.array([0.0, -1.0, 0.0])
            cuff = d.get("cuff")
            if cuff:                                                                         # the track end nearer the bar
                dl_ = math.acos(max(-1.0, min(1.0, float(W0 @ hA)))); sd = max(math.sin(dl_), 0.2)
                rg = float(cuff.get("range", 90.0)) * D2R + math.atan(HUB_R / R) / sd
                ends = []
                for sg in (-1, 1):
                    ph = sg * rg; v = W0 * math.cos(ph) + np.cross(hA, W0) * math.sin(ph) + hA * (hA @ W0) * (1 - math.cos(ph)); ends.append(v)
                s0 = min(ends, key=lambda v: np.linalg.norm(v - eb))
            else:                                                                            # leave the JN hub toward the bar
                tw = eb - (eb @ W0) * W0; tw /= np.linalg.norm(tw) + 1e-12; al = math.atan((HUB_R + 3.0) / R); s0 = math.cos(al) * W0 + math.sin(al) * tw
            om = math.acos(max(-1.0, min(1.0, float(s0 @ eb)))); L = om * R; ns = max(3, int(L / 5.0))
            dirs, dA, dB, w = [], [], [], []
            for k in range(ns + 1):
                u = k / ns; v = (math.sin((1 - u) * om) * s0 + math.sin(u * om) * eb) / max(math.sin(om), 1e-6); v /= np.linalg.norm(v)
                tg = eb - (eb @ v) * v; tg /= np.linalg.norm(tg) + 1e-12; nl = np.cross(v, tg)
                for wo in (-5.0, 0.0, 5.0):
                    q = v + nl * wo / R; dirs.append(q / np.linalg.norm(q)); dA.append(u * L); dB.append((1 - u) * L); w.append(14.0 * L / ns / 3)
            out.append(dict(name="neck", frame="can", dirs=t.tensor(np.array(dirs), device=self.dev, dtype=self.f32), dA=t.tensor(dA, device=self.dev, dtype=self.f32),
                            dB=t.tensor(dB, device=self.dev, dtype=self.f32), w=t.tensor(w, device=self.dev, dtype=self.f32), thick=T_BOT, rad=7.0,
                            h_end=float(nk["r_under"]), start="rail" if cuff else "hub"))
        if lower.get(1) == 0:                                                                # base under link 1: tab toward the back plate
            b = np.array(bvec(d["az"], d["el"])); um = np.array(self.mount_dir, float); um = um - (um @ b) * b; um /= np.linalg.norm(um) + 1e-12; ul = np.cross(b, um)
            dirs, dA, w = [], [], []
            for r_ in np.arange(HUB_R + 2.0, HUB_R + 14.0, 3.0):
                for wo in (-5.0, 0.0, 5.0):
                    q = b * R + um * r_ + ul * wo; dirs.append(q / np.linalg.norm(q)); dA.append(r_); w.append(14.0 * 3.0 / 3)
            out.append(dict(name="tab", frame="scap", dirs=t.tensor(np.array(dirs), device=self.dev, dtype=self.f32), dA=t.tensor(dA, device=self.dev, dtype=self.f32),
                            dB=t.full((len(dA),), 1e3, device=self.dev), w=t.tensor(w, device=self.dev, dtype=self.f32), thick=T_LINK, rad=7.0, h_end=None, start="J1"))
        return out

    def bottom_face(self, d):
        """lower face radius of BOTTOM's hub disc at JN (arm-fixed): >= 3 mm (+0.5) off the skin over the disc in
        every frame (deltoid bulge, acromion and trunk when the arm is raised)"""
        t = self.t; W = t.tensor(w_dir(*d["w"]), device=self.dev, dtype=self.f32)
        fp = self.footprint(0.0, hubs=(True, False), ribbon=False)
        tmp = t.tensor([1.0, 0, 0], device=self.dev) if abs(float(W[0])) < 0.9 else t.tensor([0, 1.0, 0], device=self.dev)
        n_ = self._unit(tmp - (tmp @ W) * W); Fm = t.stack([W, n_, t.cross(W, n_, dim=-1)], -1)
        dirs = (Fm @ fp["dirs"].T).T; cosa = fp["cosa"]                                           # canonical humerus frame
        HG, RS = self.P["HG"], self.P["RS"]; NP = HG.shape[0]
        wt = t.einsum("pij,pjk,mk->pmi", RS, HG, dirs)                                            # thorax = RS HG w
        flat = self.pix(wt); fx = t.arange(NP, device=self.dev)[:, None].expand_as(flat)
        return float((self.look("r1c", fx, flat) * cosa[None])[self.fit_mask & ~self.env_mask].max()) + 0.5

    def fit_shape(self, Lsel, Csel, keep, wS, kindA, cosA, dAA, dBA, JA, memA, is_low, is_bot, F_bot, N, lower):
        """shape h (I,) from the chosen configs' lower bounds: envelope over the frames kept, greedily dropping the
        frame that forces the shape up the most while the score improves; hubs flat, ribbons ramp-limited"""
        t = self.t; WT = self.WT; NP, I = Lsel.shape; I0 = I
        NR = 0
        if self._rail is not None:                                                             # rail samples join the fit (free-shape points)
            R_ = self._rail; NR = R_["LO"].shape[1]
            Lsel = t.cat([Lsel, R_["LO"]], 1); Csel = t.cat([Csel, R_["CAP"]], 1); wS = t.cat([wS, R_["w"]])
            pad = lambda v, val: t.cat([v, t.full((NR,), val, device=self.dev, dtype=v.dtype)])
            kindA, cosA, dAA, dBA, JA, memA = pad(kindA, -1), pad(cosA, 1.0), pad(dAA, 1e3), pad(dBA, 1e3), pad(JA, 0), pad(memA, -1)
            is_low, is_bot = pad(is_low, False), pad(is_bot, False); I = I0 + NR
        rail_m = t.zeros(I, dtype=t.bool, device=self.dev)
        if NR: rail_m[I0:] = True
        S = keep.clone()
        def shape_of(S):
            Lm = t.where(S[:, None], Lsel, t.full_like(Lsel, -1e4)).max(0).values               # envelope (I,)
            rib = kindA == 0
            if self._zj4_fixed is None:                                                         # BOTTOM's disc clears the kept frames only
                zb = (t.where(S[:, None], Lsel, t.full_like(Lsel, -1e4))[:, is_bot] * cosA[is_bot][None]).max()
            else: zb = t.tensor(self._zj4_fixed, device=self.dev)
            rail_under = None
            if NR:                                                                              # carriage rides 0.5 mm over the rail's turned top
                rail_under = Lm[rail_m] + self.hub_margin; zb = t.maximum(zb, rail_under.max() + RAIL_D + 0.5)
            Fb = zb + T_BOT + T_W
            Fj = {}
            for J in range(1, N):
                m_lo = is_low & (JA == J); m_up = (kindA > 0) & (JA == J) & ~is_low
                Fj[J] = t.maximum((Lm[m_lo] * cosA[m_lo]).max(), (Lm[m_up] * cosA[m_up]).max() - STACK)
            for _pass in range(3):
                h = Lm.clone(); faces = {}
                for J in range(1, N):
                    m_lo = is_low & (JA == J); m_up = (kindA > 0) & (JA == J) & ~is_low; F = Fj[J]; faces[J] = F
                    # lower member: flat washer seat on top; its skin-side underside may follow the skin (contoured)
                    h = t.where(m_lo, (t.minimum(F / cosA, t.maximum(Lm + self.hub_margin, F / cosA - self.hub_relief)) if self.hub_relief > 0 else F / cosA), h)
                    h = t.where(m_up, (F + STACK) / cosA, h)
                h = t.where(is_bot, Fb / cosA, h); faces[N] = Fb; faces["zj4"] = zb                   # link N-1 sits on BOTTOM's hub
                # ribbons leave each hub plate at <= RAMP (buildable loft): raise them where needed
                for mi in range(1, N):
                    Jst, Jen = mi, mi + 1
                    Fst = faces[Jst] + (0.0 if lower.get(Jst) == mi else STACK)
                    Fen = faces[N] if Jen == N else faces[Jen] + (0.0 if lower.get(Jen) == mi else STACK)
                    mm = rib & (memA == mi)
                    lim = t.maximum(Fst - self.RAMP * t.clamp(dAA - (HUB_R + 6.0), min=0), Fen - self.RAMP * t.clamp(dBA - (HUB_R + 6.0), min=0))
                    h = t.where(mm, t.maximum(h, lim), h)
                # the lower member's ribbon must pass under the upper member's stack near each joint: raise faces, redo
                moved = False
                for J in range(1, N):
                    lo_m = lower[J]
                    if lo_m <= 0: continue
                    dJ = dAA if J == lo_m else dBA; near = rib & (memA == lo_m) & (dJ < HUB_R + 2.5)
                    if not bool(near.any()): continue
                    req = h[near].max() + T_LO - STACK + 0.1                                      # rim of the lower plate under the upper hub
                    if float(req) > float(Fj[J]) + 1e-3: Fj[J] = req; moved = True
                if not moved: break
            if self.hub_relief > 0 and self._rail is None:                                     # BOTTOM / cuff hub: arm-side part, link N-1 turns on it ->
                bu = zb / cosA                                                                  # its contour is axisymmetric (one height per ring, turned)
                for ri in (0, 1, 2, 3):
                    mr = is_bot & (self._ringA == ri)
                    if bool(mr.any()):
                        zr = ((Lm[mr] + self.hub_margin) * cosA[mr]).max()                       # ring height along the axis
                        bu = t.where(mr, t.minimum(zb / cosA, t.maximum(zr / cosA, zb / cosA - self.hub_relief)), bu)
                faces["bot_under"] = bu
            else: faces["bot_under"] = zb / cosA
            faces["rail_under"] = rail_under
            aux_u = []
            for ax_ in self._aux:                                                                 # neck / tab: hug the kept frames, ramp out of their start
                La = t.where(S[:, None], ax_["LO"], t.full_like(ax_["LO"], -1e4)).max(0).values + self.hub_margin
                hs0 = zb if ax_["start"] == "hub" else ((rail_under.max() + 4.0 - 4.0) if (ax_["start"] == "rail" and rail_under is not None) else (Fj[1] if 1 in Fj else zb))
                u_ = t.maximum(La, hs0 - self.RAMP * t.clamp(ax_["dA"] - 6.0, min=0))
                if ax_["h_end"] is not None: u_ = t.maximum(u_, t.tensor(ax_["h_end"], device=self.dev) - self.RAMP * t.clamp(ax_["dB"] - 6.0, min=0))
                aux_u.append(u_)
            faces["aux_under"] = aux_u
            return h, faces
        def score_of(h, S, faces):
            hs = t.where(is_bot, faces["bot_under"], h)                                            # lowest metal at JN: BOTTOM's disc
            if NR: hs = t.cat([hs[:I0], faces["rail_under"]])                                       # the rail's contoured underside
            inb = ((hs[None] <= Csel + 1e-3).float() * wS).sum(-1)
            ok = keep & (Lsel <= hs[None] + 1e-3).all(-1)                                      # every frame the shape fits
            den = wS.sum()
            for ax_, u_ in zip(self._aux, faces["aux_under"]):
                inb = inb + ((u_[None] <= ax_["CAP"] + 1e-3).float() * ax_["w"]).sum(-1); ok = ok & (ax_["LO"] <= u_[None] + 1e-3).all(-1); den = den + ax_["w"].sum()
            inb = inb / den
            sc_ = float((t.where(ok, inb, t.zeros_like(inb)) * WT).sum() / WT.sum())
            if bool(envm.any()): sc_ *= min(1.0, float((ok & envm).sum()) / float(envm.sum()) / self.env_target) ** self.env_weight     # workspace share vs target
            return sc_
        # coherent drops first: frames ranked by how far they push the envelope above the typical frame
        med = t.where(keep[:, None], Lsel, t.full_like(Lsel, float("nan"))).nanmedian(0).values
        diff = ((Lsel - med[None]).clamp(min=0) * wS).sum(1); diff = t.where(keep, diff, t.full_like(diff, float("inf")))
        envm = self.env_mask & keep; dk = keep                                # envelope poses may be given up, at a price (score_of)
        WTd = t.where(envm, WT[~self.env_mask].mean() if bool((~self.env_mask).any()) else t.ones_like(WT), WT) if bool(envm.any()) else WT
        best = None
        for tau in (1.0, 0.97, 0.94, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.5, 0.4, 0.3):
            thr = t.quantile(diff[dk], tau) if int(dk.sum()) > 1 else diff.max()
            St = keep & (diff <= thr + 1e-6)
            if int(St.sum()) == 0: continue
            h, faces = shape_of(St); s = score_of(h, St, faces)
            if best is None or s > best[0]: best = (s, h, St.clone(), faces)
        S = best[2].clone(); stall = 0
        for r in range(self.drop_rounds):
            if int(S.sum()) <= 1: break
            Lm = t.where(S[:, None], Lsel, t.full_like(Lsel, -1e4))
            top2 = Lm.topk(2, dim=0); excess = (top2.values[0] - top2.values[1]) * wS             # how far each arg-max frame pushes
            push = t.zeros(NP, device=self.dev).index_add_(0, top2.indices[0], excess)
            p_drop = int((push / t.clamp(WTd, min=1e-6)).argmax())
            if not S[p_drop]: break
            S[p_drop] = False
            h, faces = shape_of(S); s = score_of(h, S, faces)
            if s > best[0] + 1e-5: best = (s, h, S.clone(), faces); stall = 0
            else:
                stall += 1
                if stall >= 25: break
        best = (best[0], best[1][:I0], best[2], best[3])
        if NR: best[3]["bot_under"] = best[3]["bot_under"][:I0]
        self._bot_under = best[3]["bot_under"]; self._faces_full = best[3]; self._faces = {k: (float(v) if not hasattr(v, "shape") or v.dim() == 0 else None) for k, v in best[3].items() if k not in ("bot_under", "rail_under", "aux_under") and v is not None}
        return best[1], best[2], best[0], float(best[3]["zj4"])

    def collisions(self, COLD, FP, h, offs, N, lower, Qgrid, d):
        """(NP, C) True where two parts overlap: centreline samples closer in plan than their half-widths while their
        RADIAL INTERVALS overlap (+0.6 mm): ribbons h..h+4 (h+3.5 at a hub rim), lower hubs skin side..seat, upper hubs
        hub underside..cap crown (v3.1), link N-1's JN hub down to BOTTOM's hub / the carriage; plus the arm-fixed neck,
        the cuff rail and the base's tab. At a shared joint the stack decides (hub vs the other member exempt, coaxial
        plates may run 0.15 apart). Links vs the BOTTOM bar beyond its neck as before."""
        t = self.t; R = self.R_REF; out = []; F = self._faces_full
        def FJ(J): return F[J] if J in F else None
        ivs = []
        for mi, fp in enumerate(FP):
            col = fp["col"]; hs = h[int(offs[mi]):int(offs[mi + 1])][col]; kd = fp["ckind"]; dA = fp["dA"][col]; dB = fp["dB"][col]
            near_rim = (kd == 0) & (t.minimum(dA, dB) < HUB_R + 6.0)
            bot = hs.clone(); top = hs + t.where(near_rim, t.full_like(hs, T_LO), t.full_like(hs, T_LINK))
            for k_ in range(len(col)):
                if int(kd[k_]) == 0: continue
                J = (mi if int(kd[k_]) == 1 else mi + 1) if mi > 0 else 1
                if J == N:                                                                       # link N-1 on BOTTOM's hub / the carriage
                    bot[k_] = F["zj4"]; top[k_] = F[N] + HUB_UP + CAP_UP
                elif lower.get(J) == mi: top[k_] = F[J] + T_LO
                else: bot[k_] = F[J] + STACK; top[k_] = F[J] + STACK + HUB_UP + CAP_UP
            ivs.append((bot, top, kd, dA, dB))
        aux = []
        for ax_, u_ in zip(self._aux, F.get("aux_under", [])):
            c = ax_["col"]; aux.append((ax_, u_[c], u_[c] + (T_LO if ax_["name"] == "tab" else ax_["thick"]), ax_["dirs"][c], ax_["dA"][c]))
        if self._rail is not None and F.get("rail_under") is not None:
            ru = F["rail_under"]; c = t.arange(0, ru.shape[0], 1, device=self.dev); top_r = ru.max() + RAIL_D
            aux.append((dict(name="rail", frame="can", rad=6.0), ru[c], top_r.expand_as(ru[c]), self._rail["dirs"][c], t.full_like(ru[c], 1e3)))
        WB, DB, EB = self.Wbar, self.Dbar, self.Ebar; j0, j1, dj = self.jog; free_w = abs(d["w"][0] - 85.9) > 0.5 or abs(d["w"][1]) > 0.5
        rads = [fp["crad"] for fp in FP]
        for ch in COLD:
            cold, hg = ch["w"], ch["hg"]; Pn, C = cold[0].shape[:2]; hit = t.zeros((Pn, C), dtype=t.bool, device=self.dev)
            for i in range(len(FP)):
                bi, ti, ki, dAi, dBi = ivs[i]
                for j in range(i + 1, len(FP)):
                    bj, tj, kj, dAj, dBj = ivs[j]
                    ang = t.arccos(t.clamp(t.einsum("pcmi,pcni->pcmn", cold[i].float(), cold[j].float()), -1, 1)) * R
                    clr = t.full((len(bi), len(bj)), 0.6, device=self.dev)
                    ok_pair = t.ones((len(bi), len(bj)), dtype=t.bool, device=self.dev)
                    if j == i + 1:                                                               # shared joint J = i + 1 (i's end hub, j's start hub)
                        hub_i = (ki == 2)[:, None]; hub_j = (kj == 1)[None, :]
                        near_j = (dAj < HUB_R + HW)[None, :]; near_i = (dBi < HUB_R + HW)[:, None]
                        ok_pair &= ~(hub_i & hub_j) & ~(hub_i & near_j) & ~(hub_j & near_i)
                        coax = ((ki == 0) & (dBi < HUB_R + 15.0))[:, None] & ((kj == 0) & (dAj < HUB_R + 15.0))[None, :]
                        clr = t.where(coax, t.full_like(clr, -0.05), clr)
                    ivo = t.minimum(ti[:, None], tj[None, :]) - t.maximum(bi[:, None], bj[None, :]) + clr
                    over = (ang < (rads[i][:, None] + rads[j][None, :] - 1.0)) & (ivo > 0)[None, None] & ok_pair[None, None]
                    hit |= over.reshape(Pn, C, -1).any(-1)
            for i in range(len(FP)):                                                             # links / base vs neck, rail, tab
                bi, ti, ki, dAi, dBi = ivs[i]
                wc = t.einsum("pji,pcmj->pcmi", hg, cold[i].float())                              # canonical humerus frame
                for ax_, ub, ut, adir, adA in aux:
                    if ax_["name"] == "tab" and i == 0: continue
                    src = wc if ax_["frame"] == "can" else cold[i].float()
                    ang = t.arccos(t.clamp(t.einsum("pcmi,ni->pcmn", src, adir), -1, 1)) * R
                    clr = t.full((len(bi), len(ub)), 0.6, device=self.dev); ok_pair = t.ones_like(clr, dtype=t.bool)
                    if ax_["name"] == "neck" and i == N - 1:                                      # link N-1's JN plate over BOTTOM's hub and the neck root
                        ok_pair &= ~(((ki == 2) | (dBi < HUB_R + HW))[:, None] & (adA < 15.0)[None, :])
                    if ax_["name"] == "rail" and i == N - 1:                                      # the carriage rides 0.5 over the rail by design
                        ok_pair &= ~(ki == 2)[:, None]
                    if ax_["name"] == "tab" and i == 1:                                           # link 1 over the base tab at J1
                        ok_pair &= ~(ki == 1)[:, None]; clr = t.where(((ki == 0) & (dAi < HUB_R + 15.0))[:, None].expand_as(clr), t.full_like(clr, -0.05), clr)
                    ivo = t.minimum(ti[:, None], ut[None, :]) - t.maximum(bi[:, None], ub[None, :]) + clr
                    rr = rads[i][:, None] + float(ax_["rad"]) - 1.0
                    over = (ang < rr) & (ivo > 0)[None, None] & ok_pair[None, None]
                    hit |= over.reshape(Pn, C, -1).any(-1)
            hs = [h[int(offs[mi]):int(offs[mi + 1])][fp["col"]] for mi, fp in enumerate(FP)]
            for i in range(1, len(FP)):                                    # links vs the BOTTOM bar (humerus frame), beyond the neck
                wh = t.einsum("pji,pcmj->pcmi", hg, cold[i].float()) * hs[i][None, None, :, None]
                zl, dl, el = (wh * WB).sum(-1), (wh * DB).sum(-1), (wh * EB).sum(-1)
                s_ = t.clamp((dl - j0) / (j1 - j0), 0, 1); s_ = 10 * s_ ** 3 - 15 * s_ ** 4 + 6 * s_ ** 5
                zlo = self.zbar + dj * s_
                inplan = (el.abs() <= 16.0) & (dl >= (40.0 if free_w else 0.0)) & (dl <= 220.0)
                if not free_w: inplan |= t.sqrt(dl ** 2 + el ** 2) <= HUB_R + 1.0
                over = inplan & (zl < zlo + T_BOT + 1.0) & (zl + T_LINK > zlo - 1.0)
                if i == N - 1: over &= t.sqrt(dl ** 2 + el ** 2) > HUB_R + 4.0      # its own hub sits on BOTTOM
                hit |= over.any(-1)
            out.append(hit)
        return t.cat(out, 0)

def bvec(az, el):
    return [-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)]

def w_dir(delta, az):
    d, a = delta * D2R, az * D2R
    return [math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)]

def circ_int(t, c1, r1, c2, r2, sign):
    dd = t.clamp((c1 * c2).sum(-1), -1, 1); n = c1.new_tensor(0) + t.cross(c1, c2, dim=-1); n = n / (t.linalg.norm(n, dim=-1, keepdim=True) + 1e-12)
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return p + sign * t.sqrt(t.clamp(h2, min=0))[..., None] * n, h2 > 0

def tri_ok(t, x, y, a, b, sing):
    th = t.arccos(t.clamp((x * y).sum(-1), -1, 1))
    return (th >= abs(a - b) + sing) & (th <= min(a + b, 2 * math.pi - a - b) - sing)


# ---------------------------------------------------------------- search
def run(job):
    import torch
    g = globals()                                                     # per-job geometry overrides (sensitivity studies)
    for k in ("HUB_R", "HW", "T_LINK", "STACK", "T_W", "T_BOT", "T_LO", "HUB_UP", "CAP_UP", "RAIL_D"):     # HW: link half-width (MVP1: tiny loads -> narrow links)
        if k.lower() in job: g[k] = float(job[k.lower()])
    dev = torch.device("cuda" if torch.cuda.is_available() else ("mps" if job.get("mps") and torch.backends.mps.is_available() else "cpu"))
    t0 = time.time(); B = Band(job, dev)
    devname = torch.cuda.get_device_name(0) if torch.cuda.is_available() else str(dev)
    if job["mode"] == "band_eval":
        res = [dict(d, **B.evaluate(d, detail=job.get("detail", False))) for d in job["designs"]]
        return {"results": res, "secs": time.time() - t0, "device": devname, "version": CODE_VERSION}
    # evolutionary search for one chain length
    rng = random.Random(job.get("seed", 1)); N = int(job["n"])
    crange = job.get("cuff_range")                                    # sliding cuff on the upper arm (deg either way)
    rand_d, mutate = make_samplers(job, rng); amin, amax = arc_bounds(job)
    print(f"link arcs searched in [{amin:g}, {amax:g}] deg (min_arc {B.min_arc:g}), min arm {B.min_arm:g} mm between hub seats", flush=True)
    def fit(g):
        try: r = B.evaluate(g)
        except Exception as e: r = dict(score=-1.0, err=str(e)[:200])
        return r
    inits = [json.loads(json.dumps(dict(x, n=N))) for x in job.get("init", []) if len(x.get("a", [])) == N - 1]
    for x in inits:                                                   # seeds from older searches: arcs into the searched range
        a0 = list(x["a"]); x["a"] = [min(amax, max(amin, float(v))) for v in a0]
        if x["a"] != a0: print(f"init arcs {[round(v, 1) for v in a0]} -> {[round(v, 1) for v in x['a']]} (arc bounds)", flush=True)
    if crange:
        for x in inits: x.setdefault("cuff", dict(range=float(crange), branch=1))
    pop = [dict(g=g, r=fit(g)) for g in (inits + [rand_d() for _ in range(job.get("pop", 64))])]
    hist = []; evals = len(pop); max_secs = float(job.get("max_secs", 3000))
    for gen in range(job.get("gens", 60)):
        pop.sort(key=lambda x: -x["r"].get("score", -1)); elite = pop[:job.get("elite", 12)]
        hist.append(dict(gen=gen, best=elite[0]["r"].get("score"), follow=elite[0]["r"].get("follow"), secs=time.time() - t0))
        print(f"gen {gen} best {elite[0]['r'].get('score'):.4f} follow {elite[0]['r'].get('follow'):.3f} evals {evals} {time.time() - t0:.0f}s", flush=True)
        if time.time() - t0 > max_secs: break
        s = max(0.25, 1.0 - gen / max(1, job.get("gens", 60)))
        kids = []
        for _ in range(job.get("pop", 64)):
            if rng.random() < 0.15: kids.append(rand_d())
            else: kids.append(mutate(rng.choice(elite)["g"], s))
        pop = elite + [dict(g=g, r=fit(g)) for g in kids]; evals += len(kids)
    pop.sort(key=lambda x: -x["r"].get("score", -1))
    top = [dict(x["g"], **{k: v for k, v in x["r"].items()}) for x in pop[:8]]
    return {"best": top, "hist": hist, "evals": evals, "secs": time.time() - t0, "device": devname, "version": CODE_VERSION}

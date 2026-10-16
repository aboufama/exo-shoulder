#!/usr/bin/env python3
"""Massive GPU polish of the PIN-KNEE family (skin-normal-3r-pin-knee) over several GPU pods that share the farm volume.

Objective = the near-touch gap (metal < 1 mm counts as contact) of the adversarial verifier's corrected set on
Bench(110,360), same-bench protocol (shape fitted there, fast grid), evaluated by the GPU port tools/gpu_bench_knee.py
(the CPU kit's own code with its per-pose loops batched on the device; parity 0.0 on 54 configs x 2 protocols), plus a
follow penalty (100 x the clip frames lost: every overhead clip frame must stay followed). Free: every continuous
parameter of tools/knee_polish.py FREE (seats az1 el1 az2 el2 wd wa b3, knee lE lc phiE phib, knee window ang_min, pin
stack stk) AND the fold margin (>= 5 deg, the user's floor; S.SING set per evaluation, the same global the CPU kit's IK
reads from CB_FOLD_MARGIN). Fixed by the rulings: O20 hubs (rad 10), J1 seat on the back / acromion top (anterior
component <= 0.20, rejected before evaluation), b1 = b2 = 0, the knee branch (fixed sign, 10 fps continuity incl. pin a
/ pin b, window [ang_min, 180 - ang_min]).

Stages (every pod runs the same driver; work is shared through O_EXCL claim files on the volume, so a pod that never
boots or dies costs only its claimed chunk):
  1. seeds   : H1, P5, HW, k4598, raglan-knee-3r's seats (straight links), G2, G3 (the in-sample GPU bests) at margin 5
  2. sobol   : scrambled Sobol boxes around the leaders' basins (+-1 / 2.5 / 3 x the polish's CMA scale, margin 5-8) and
               wide over the FREE bounds (margin 5-12), in chunks of 512 claimed by the pods; points outside the grid box
               use the conservative bound d(clamped) - |offset| (never optimistic; the final numbers use the exact path)
  3. basins  : the best 30 distinct points (distance > R_BASIN in CMA-scale units, angles periodic) -> CMA (knee_polish's
               algorithm, lambda 12) in each, lockstep over a pod's claimed basins, to convergence (sigma x max axis <
               0.02, or no gain > 0.02 over 40 generations); further basins (31..60) are claimed while time remains
  4. final   : top 30 distinct over everything re-evaluated with the port's EXACT outside path (= the CPU kit), the
               top 10 + H1 handed to the CPU kit: docs/concepts/verify/skin-normal-3r-pin-knee-polish.py fit60 / fitbig /
               held (CB_EXACT=1, CB_FOLD_MARGIN = the config's margin) and the continuity flood fill
               (skin-normal-3r-pin-knee-continuity.py kin fitbig) - claimed by every pod's CPUs; then each pod removes
               itself.

    python3 tools/gpu_knee_search.py run --out DIR [--bench 110,360] [--device cuda] [--workers W]
        deadlines (epoch s, env): GKS_T_SOBOL GKS_T_CMA GKS_T_VERIFY ; sizes: GKS_SCALE (1.0 = 110k Sobol points)
    python3 tools/gpu_knee_search.py points            print the Sobol plan (counts per region, seat rejections)
    python3 tools/gpu_knee_search.py summary DIR OUT.json     merge a fetched run directory into one summary
"""
import glob, json, math, os, sys, time, traceback
from collections import deque
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

FREE_KEYS = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "ang_min", "stk")
KEYS = FREE_KEYS + ("margin",)
PERIODIC = ("phiE", "phib")
MARGIN = (1.0, 5.0, 15.0)                     # CMA scale, floor (the user's 5 deg), ceiling
R_BASIN = 2.5                                 # basin separation, CMA-scale units
R_DISTINCT = 1.5                              # distinct finalists
LAM = 12
CHUNK = 512


def spec():
    """(scale, lo, hi) arrays over KEYS from tools/knee_polish.py FREE (+ margin); periodic angles get [-180, 180)"""
    import knee_polish as KP
    sc, lo, hi = [], [], []
    for k in FREE_KEYS:
        s, l, h, _ = KP.FREE[k]; sc.append(s); lo.append(-180.0 if l is None else l); hi.append(180.0 if h is None else h)
    sc.append(MARGIN[0]); lo.append(MARGIN[1]); hi.append(MARGIN[2])
    return np.array(sc), np.array(lo), np.array(hi)


def wrap180(a): return (np.asarray(a) + 180.0) % 360.0 - 180.0


PER_MASK = np.array([k in PERIODIC for k in KEYS])


def to_vec(p, margin=5.0):
    return np.array([float(p[k]) if k != "margin" else float(p.get("margin", margin)) for k in KEYS])


def to_dict(x):
    return {k: float(round(float(v), 4)) for k, v in zip(KEYS, x)}


def ndist(x, Y, sc):
    """distance in CMA-scale units (periodic angles wrapped) from x (n,) to rows of Y (m, n)"""
    d = (np.asarray(Y) - x[None]); d[:, PER_MASK] = wrap180(d[:, PER_MASK]); return np.sqrt(((d / sc[None]) ** 2).sum(1))


# ---- seeds -------------------------------------------------------------------------------------------------------------
def seeds():
    r = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "skin-normal-3r-pin-knee.json")))
    out = {"H1": r["best_params"], "k4598": r["best_params_previous"]}
    p5 = (r.get("rebase_polish_m5") or {}).get("P5", {}).get("params")
    if p5: out["P5"] = p5
    out["HW"] = dict(lE=57.5413, lc=24.7817, phiE=-8.543, phib=-62.1137, stk=5.4462, ang_min=33.4102, az1=102.0772, el1=63.6132,
                     az2=35.2676, el2=44.5151, wd=70.8671, wa=-5.7376, b3=0.3536)          # polish-big-HW HW-g58-11 (sweep log)
    try:
        rg = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "raglan-knee-3r.json")))["best_params"]
        out["raglan_seats"] = {k: rg[k] for k in FREE_KEYS}                                 # straight links (no route)
    except Exception: pass                                                                   # noqa: BLE001
    # the in-sample GPU polish bests (docs/research/golden/knee_cma_G3.json G3-g115-2 20.81, knee_cma_G2.json G2-g171-14 21.89)
    out["G3"] = dict(az1=98.2985, el1=64.7969, az2=33.5049, el2=44.7883, wd=63.9916, wa=-9.3012, b3=0.3252, lE=72.1759, lc=37.5419,
                     phiE=-4.4957, phib=-56.7105, ang_min=24.2314, stk=5.6834)
    out["G2"] = dict(az1=98.8874, el1=64.43, az2=31.6274, el2=45.468, wd=66.9189, wa=-5.3373, b3=0.3001, lE=61.1612, lc=28.0627,
                     phiE=-5.8986, phib=-61.4857, ang_min=35.3222, stk=5.6269)
    return {k: {kk: float(v[kk]) for kk in FREE_KEYS} | {"margin": 5.0} for k, v in out.items()}


# ---- the Sobol plan ----------------------------------------------------------------------------------------------------
REGIONS = (  # name, centre seed (None = wide), half-width in CMA scales, margin range, log2 count
    ("G3w", "G3", 3.0, (5.0, 8.0), 15), ("G3n", "G3", 1.0, (5.0, 6.5), 13), ("H1w", "H1", 3.0, (5.0, 8.0), 13),
    ("P5w", "P5", 3.0, (5.0, 8.0), 13), ("G2w", "G2", 2.5, (5.0, 8.0), 13), ("HWw", "HW", 2.5, (5.0, 8.0), 12),
    ("k4598w", "k4598", 3.0, (5.0, 8.0), 12), ("ragw", "raglan_seats", 3.0, (5.0, 8.0), 12), ("wide", None, None, (5.0, 12.0), 15),
)


def sobol_points(scale=1.0):
    """every Sobol point of the plan inside the rulings (J1 seat), interleaved over the regions by a fixed permutation
    (a truncated run still covers every region); -> (X (N, 14), region names (N,))"""
    from scipy.stats import qmc
    import concept_kit as KIT
    sc, lo, hi = spec(); S = seeds(); X, R = [], []
    for j, (nm, c, hw, (mlo, mhi), l2) in enumerate(REGIONS):
        if c is not None and c not in S: continue
        n = 2 ** max(4, int(round(l2 + math.log2(scale))))
        u = qmc.Sobol(len(KEYS), scramble=True, seed=1000 + j).random(n)
        if c is None:
            x = lo + u * (hi - lo)
        else:
            x0 = to_vec(S[c]); x = x0[None] + (2 * u - 1) * hw * sc[None]
            x[:, ~PER_MASK] = np.clip(x[:, ~PER_MASK], lo[~PER_MASK], hi[~PER_MASK])
        x[:, -1] = mlo + u[:, -1] * (mhi - mlo)
        x[:, PER_MASK] = wrap180(x[:, PER_MASK])
        ok = np.array([float(KIT.bvec(a, e)[0]) <= 0.20 for a, e in zip(x[:, 0], x[:, 1])])
        X.append(x[ok]); R += [nm] * int(ok.sum())
    X = np.concatenate(X); R = np.array(R); perm = np.random.default_rng(7).permutation(len(X))
    return np.round(X[perm], 4), R[perm]


# ---- workers (GPU port, one bench per process) -------------------------------------------------------------------------
_W = {}


def _bound_patch(GB):
    """screen mode for points outside the grid box: d(x) >= d(x_clamped) - |x - x_clamped| (1-Lipschitz), never optimistic"""
    if getattr(GB.GridDev, "_gks_bound", False): return
    orig = GB.GridDev.dist

    def dist(self, I, X):
        if getattr(self, "mode_out", "exact") != "bound": return orig(self, I, X)
        lo = -float(self.HALF); hi = (self.n - 1 - 1e-6) * float(self.H) - float(self.HALF)
        Xc = X.clamp(min=lo, max=hi); off = (X - Xc).norm(dim=-1)
        m = off > 0
        if bool(m.any()): self.n_bound = getattr(self, "n_bound", 0) + int(m.sum())
        return orig(self, I, Xc) - off
    GB.GridDev.dist = dist; GB.GridDev._gks_bound = True


def _w_init(nc, nw, device):
    os.environ["OMP_NUM_THREADS"] = "1"
    import gpu_bench_knee as GB
    KP = GB.kit(5.0); GB.patch(KP); _bound_patch(GB)
    _W.update(GB=GB, KP=KP, S=KP.verifier().MK.S, B=GB.bench(nc, nw, device))


def objective(r):
    return float(r["gap_near1"]) + 100.0 * max(0.0, 1.0 - float(r["follow"]))


def _eval(a):
    tag, p, mode = a; t = time.time()
    try:
        S, B, GB = _W["S"], _W["B"], _W["GB"]; m = float(p["margin"])
        if m < MARGIN[1] - 1e-9: return dict(tag=tag, p=p, err="margin < 5", obj=400.0)
        S.SING = m; gd = B._gd; gd.mode_out = mode; nb0 = getattr(gd, "n_bound", 0); no0 = gd.outside
        r = GB.evaluate_one({k: v for k, v in p.items() if k != "margin"}, B)
        out = dict(tag=tag, p=p, secs=round(time.time() - t, 2), nb=getattr(gd, "n_bound", 0) - nb0, nx=gd.outside - no0, mode=mode)
        if r.get("gap") is None or r.get("error") or r.get("gap_near1") is None:
            out.update(err=str(r.get("error", "no gap"))[:120], obj=400.0); return out
        for k in ("gap", "gap_near1", "gap_near2", "reach", "follow", "inband14", "inband10", "contact", "near_min", "near1_poses", "knee_ang", "extra_bad"):
            v = r.get(k); out[k] = (round(float(v), 4) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
        out["obj"] = round(objective(r), 4); return out
    except Exception as e:                                                                   # noqa: BLE001
        return dict(tag=tag, p=p, err=f"{type(e).__name__}: {e}"[:200], trace=traceback.format_exc()[-600:], obj=400.0, secs=round(time.time() - t, 2))


# ---- claims on the shared volume ---------------------------------------------------------------------------------------
def claim(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, (os.environ.get("RUNPOD_POD_ID", "local") + f" {time.time():.0f}").encode()); os.close(fd); return True
    except FileExistsError:
        return False


def jdump(obj, path):
    tmp = path + f".{os.getpid()}.tmp"; json.dump(obj, open(tmp, "w"), default=float); os.replace(tmp, path)


class Log:
    def __init__(self, path): self.f = open(path, "a"); self.n = 0

    def write(self, rows):
        for r in rows: self.f.write(json.dumps(r, default=float) + "\n")
        self.n += len(rows); self.f.flush(); os.fsync(self.f.fileno())


def read_jsonl(pattern):
    out = []
    for f in sorted(glob.glob(pattern)):
        for line in open(f):
            line = line.strip()
            if not line: continue
            try: out.append(json.loads(line))
            except Exception: pass                                                           # noqa: BLE001  (a torn last line)
    return out


# ---- CMA (tools/knee_polish.py's update; bounded by clipping + quadratic penalty; periodic angles wrapped) ---------------
class CMA:
    def __init__(self, x0, sigma, seed, sc, lo, hi, lam=LAM):
        n = len(x0); self.n = n; self.c0 = np.array(x0, float); self.sc, self.lo, self.hi = sc, lo, hi; self.lam = lam; self.mu = mu = lam // 2
        w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); self.w = w / w.sum(); self.mueff = mueff = 1.0 / (self.w ** 2).sum()
        self.cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); self.cs = (mueff + 2) / (n + mueff + 5)
        self.c1 = 2 / ((n + 1.3) ** 2 + mueff); self.cmu = min(1 - self.c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
        self.damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + self.cs; self.chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
        self.mean = np.zeros(n); self.sigma = sigma; self.C = np.eye(n); self.pc = np.zeros(n); self.ps = np.zeros(n); self.gen = 0
        self.D = np.ones(n); self.B = np.eye(n); self.seed = seed; self.best = None; self.best_gen = 0; self.hist = []

    def to_p(self, z):
        x = self.c0 + self.sc * z; free = ~PER_MASK; xc = x.copy(); xc[free] = np.clip(x[free], self.lo[free], self.hi[free])
        pen = float(50.0 * ((((x - xc) / self.sc)[free]) ** 2).sum()); xc[PER_MASK] = wrap180(xc[PER_MASK]); return to_dict(xc), pen

    def ask(self):
        self.gen += 1; rng = np.random.default_rng([self.seed, self.gen]); Z = rng.standard_normal((self.lam, self.n))
        self.X = self.mean + self.sigma * ((Z * self.D) @ self.B.T); return [self.to_p(x) for x in self.X]

    def tell(self, f, rows):
        f = np.asarray(f, float); i0 = int(np.argmin(f))
        if self.best is None or f[i0] < self.best["f"] - 0.02: self.best_gen = self.gen
        if self.best is None or f[i0] < self.best["f"]: self.best = dict(f=float(f[i0]), row=rows[i0], gen=self.gen)
        self.hist.append(round(float(f.min()), 3))
        idx = np.argsort(f)[:self.mu]; old = self.mean.copy(); X = self.X; self.mean = (self.w[:, None] * X[idx]).sum(0)
        invsqrtC = self.B @ np.diag(1 / self.D) @ self.B.T; cs, cc = self.cs, self.cc
        self.ps = (1 - cs) * self.ps + math.sqrt(cs * (2 - cs) * self.mueff) * invsqrtC @ (self.mean - old) / self.sigma
        hsig = np.linalg.norm(self.ps) / math.sqrt(1 - (1 - cs) ** (2 * self.gen)) / self.chiN < 1.4 + 2 / (self.n + 1)
        self.pc = (1 - cc) * self.pc + hsig * math.sqrt(cc * (2 - cc) * self.mueff) * (self.mean - old) / self.sigma
        art = (X[idx] - old) / self.sigma
        self.C = (1 - self.c1 - self.cmu) * self.C + self.c1 * (np.outer(self.pc, self.pc) + (1 - hsig) * cc * (2 - cc) * self.C) + self.cmu * (art.T * self.w) @ art
        self.sigma *= math.exp((cs / self.damps) * (np.linalg.norm(self.ps) / self.chiN - 1))
        self.C = np.triu(self.C) + np.triu(self.C, 1).T; D2, self.B = np.linalg.eigh(self.C); self.D = np.sqrt(np.maximum(D2, 1e-20))

    def stop(self):
        if self.sigma * self.D.max() < 0.02: return "sigma collapsed"
        if self.gen - self.best_gen >= 40: return "no gain > 0.02 in 40 generations"
        return ""


# ---- the pool feeder ---------------------------------------------------------------------------------------------------
def feed(pool, items, W, on_result, deadline=None):
    """apply_async with at most 3 W in flight; items is an iterator (pulled lazily); returns the number evaluated"""
    pend = deque(); n = 0; it = iter(items)
    while True:
        while len(pend) < 3 * W and (deadline is None or time.time() < deadline):
            try: a = next(it)
            except StopIteration: break
            pend.append(pool.apply_async(_eval, (a,)))
        if not pend: break
        r = pend.popleft().get(); n += 1; on_result(r)
    return n


def pick_distinct(rows, sc, k, rad, key="obj"):
    rows = sorted([r for r in rows if r.get("err") is None and r.get(key) is not None], key=lambda r: r[key]); out, V = [], []
    for r in rows:
        x = to_vec(r["p"])
        if V and ndist(x, np.array(V), sc).min() <= rad: continue
        out.append(r); V.append(x)
        if len(out) >= k: break
    return out


# ---- the run -----------------------------------------------------------------------------------------------------------
def run(a):
    import multiprocessing as mp
    OUT = a.out; os.makedirs(OUT, exist_ok=True); me = os.environ.get("RUNPOD_POD_ID", "local")
    T_SOB = float(os.environ.get("GKS_T_SOBOL", time.time() + 1800)); T_CMA = float(os.environ.get("GKS_T_CMA", T_SOB + 1500))
    T_VER = float(os.environ.get("GKS_T_VERIFY", T_CMA + 1800)); scale = float(os.environ.get("GKS_SCALE", 1.0))
    log = lambda s: print(f"[{time.strftime('%H:%M:%S', time.gmtime())} {me}] {s}", flush=True)
    open(os.path.join(OUT, f"alive_{me}"), "w").write(f"{time.time():.0f}")
    nc, nw = (int(x) for x in a.bench.split(","))
    ncpu = len(os.sched_getaffinity(0))
    try:
        q = open("/sys/fs/cgroup/cpu.max").read().split()
        if q[0] != "max": ncpu = min(ncpu, max(1, int(int(q[0]) / int(q[1]))))
    except Exception: pass                                                                   # noqa: BLE001
    W = a.workers or max(2, ncpu - 1); log(f"cpus {ncpu} workers {W} bench {nc},{nw} device {a.device} scale {scale}; deadlines sobol {T_SOB - time.time():.0f}s cma {T_CMA - time.time():.0f}s verify {T_VER - time.time():.0f}s")
    sc, lo, hi = spec(); S = seeds()
    pool = mp.get_context("spawn").Pool(W, initializer=_w_init, initargs=(nc, nw, a.device))
    # 1. seeds + 2. Sobol chunks
    X, R = sobol_points(scale); nch = (len(X) + CHUNK - 1) // CHUNK; log(f"sobol plan {len(X)} points, {nch} chunks")
    LS = Log(os.path.join(OUT, f"sobol_{me}.jsonl"))
    if claim(os.path.join(OUT, "claims", "seeds")):
        res = pool.map(_eval, [(f"seed-{k}", p, "exact") for k, p in S.items()]); LS.write(res)
        for r in res: log(f"seed {r['tag']}: obj {r.get('obj')} near1 {r.get('gap_near1')} gap {r.get('gap')} reach {r.get('reach')} follow {r.get('follow')} {r.get('err', '')}")

    def sob_items():
        for c in range(nch):
            if time.time() >= T_SOB: return
            if not claim(os.path.join(OUT, "claims", f"s{c}")): continue
            for i in range(c * CHUNK, min(len(X), (c + 1) * CHUNK)):
                yield (f"sob-{R[i]}-{i}", to_dict(X[i]), "bound")
    buf = []; t0 = time.time(); best = [400.0]

    def on_sob(r):
        buf.append(r); best[0] = min(best[0], r.get("obj", 400.0))
        if len(buf) >= 256:
            LS.write(buf); buf.clear(); log(f"sobol {LS.n} evals ({LS.n / (time.time() - t0):.1f}/s) best obj {best[0]:.2f}")
    feed(pool, sob_items(), W, on_sob, deadline=T_SOB); LS.write(buf); buf.clear()
    open(os.path.join(OUT, f"sobol_{me}.done"), "w").write(f"{LS.n}"); log(f"sobol done: {LS.n} evals in {time.time() - t0:.0f}s")
    # 3. basins (one pod computes them; the others wait)
    while time.time() < T_SOB + 300:
        alive = [os.path.basename(f)[6:] for f in glob.glob(os.path.join(OUT, "alive_*"))]
        if all(os.path.exists(os.path.join(OUT, f"sobol_{x}.done")) for x in alive): break
        time.sleep(10)
    bpath = os.path.join(OUT, "basins.json")
    if claim(os.path.join(OUT, "claims", "basins")):
        rows = read_jsonl(os.path.join(OUT, "sobol_*.jsonl")); B = pick_distinct(rows, sc, 60, R_BASIN)
        jdump(dict(n_rows=len(rows), basins=[dict(j=j, tag=r["tag"], obj=r["obj"], p=r["p"]) for j, r in enumerate(B)]), bpath)
        log(f"basins from {len(rows)} rows: " + ", ".join(f"{r['tag']} {r['obj']:.2f}" for r in B[:30]))
    while not os.path.exists(bpath): time.sleep(5)
    time.sleep(2); basins = json.load(open(bpath))["basins"]
    alive = sorted(os.path.basename(f)[6:] for f in glob.glob(os.path.join(OUT, "alive_*"))); rank = alive.index(me) if me in alive else 0
    quota = max(1, math.ceil(min(30, len(basins)) / max(1, len(alive))))
    LC = Log(os.path.join(OUT, f"cma_{me}.jsonl")); act = []

    def take(prefer):
        for j in prefer:
            if j < len(basins) and claim(os.path.join(OUT, "claims", f"b{j}")):
                b = basins[j]; cm = CMA(to_vec(b["p"]), 0.6, 9000 + j, sc, lo, hi); cm.j = j; cm.tag0 = b["tag"]; return cm
        return None
    order = [j for j in range(min(30, len(basins))) if j % max(1, len(alive)) == rank] + list(range(len(basins)))
    while len(act) < quota:
        cm = take(order)
        if cm is None: break
        act.append(cm)
    log(f"cma: {len(act)} basins {[c.j for c in act]} (alive {len(alive)}, rank {rank})"); done = []
    while act and time.time() < T_CMA:
        tg = time.time(); items = []
        for cm in act:
            for i, (p, pen) in enumerate(cm.ask()): items.append((cm, i, p, pen))
        res = pool.map(_eval, [(f"cma-b{cm.j}-g{cm.gen}-{i}", p, "bound") for cm, i, p, pen in items], chunksize=1)
        LC.write([dict(r, b=cm.j, g=cm.gen, pen=round(pen, 4)) for r, (cm, i, p, pen) in zip(res, items)])
        k = 0
        for cm in act:
            f = [res[k + i]["obj"] + items[k + i][3] for i in range(cm.lam)]; cm.tell(f, res[k:k + cm.lam]); k += cm.lam
        fin = [cm for cm in act if cm.stop()]
        for cm in fin:
            act.remove(cm); done.append(cm)
            log(f"basin {cm.j} ({cm.tag0}) done at gen {cm.gen}: best {cm.best['f']:.2f} ({cm.stop()})")
            if T_CMA - time.time() > 300:
                nx = take(range(len(basins)))
                if nx is not None: act.append(nx); log(f"basin {nx.j} claimed")
        if act and act[0].gen % 10 == 0:
            log(f"cma gen {act[0].gen}: {len(act)} active, {LC.n} evals, gen {time.time() - tg:.1f}s, bests " + " ".join(f"b{c.j}:{c.best['f']:.2f}" for c in act))
    for cm in act + done:
        jdump(dict(j=cm.j, tag0=cm.tag0, gen=cm.gen, best=cm.best, stop=cm.stop() or "deadline", sigma=cm.sigma, hist=cm.hist), os.path.join(OUT, f"basin_{cm.j}.json"))
    open(os.path.join(OUT, f"cma_{me}.done"), "w").write(f"{LC.n}"); log(f"cma done: {LC.n} evals")
    pool.close(); pool.terminate()


def final(a):
    """4. final (a separate process, so a fix dropped on the volume applies): the top 30 distinct over every row
    re-evaluated with the port's EXACT outside path by one pod, the top 10 + H1 -> verification jobs for every pod's CPUs"""
    import multiprocessing as mp
    OUT = a.out; me = os.environ.get("RUNPOD_POD_ID", "local"); sc, lo, hi = spec(); S = seeds()
    T_CMA = float(os.environ.get("GKS_T_CMA", time.time())); T_VER = float(os.environ.get("GKS_T_VERIFY", T_CMA + 1800))
    log = lambda s: print(f"[{time.strftime('%H:%M:%S', time.gmtime())} {me}] {s}", flush=True)
    nc, nw = (int(x) for x in a.bench.split(","))
    ncpu = len(os.sched_getaffinity(0))
    try:
        q = open("/sys/fs/cgroup/cpu.max").read().split()
        if q[0] != "max": ncpu = min(ncpu, max(1, int(int(q[0]) / int(q[1]))))
    except Exception: pass                                                                   # noqa: BLE001
    W = a.workers or max(2, ncpu - 1)
    alive = sorted(os.path.basename(f)[6:] for f in glob.glob(os.path.join(OUT, "alive_*")))
    vpath = os.path.join(OUT, "verify_jobs.json")
    if claim(os.path.join(OUT, "claims", "final")):
        pool = mp.get_context("spawn").Pool(W, initializer=_w_init, initargs=(nc, nw, a.device))
        while time.time() < T_CMA + 240:
            if all(os.path.exists(os.path.join(OUT, f"cma_{x}.done")) for x in alive): break
            time.sleep(10)
        rows = read_jsonl(os.path.join(OUT, "sobol_*.jsonl")) + read_jsonl(os.path.join(OUT, "cma_*.jsonl"))
        top = pick_distinct(rows, sc, 30, R_DISTINCT)
        rex = pool.map(_eval, [(f"re-{r['tag']}", r["p"], "exact") for r in top], chunksize=1)
        for r, s in zip(rex, top): r["src"] = s["tag"]; r["obj_search"] = s["obj"]
        jdump(dict(n_rows=len(rows), reeval=rex), os.path.join(OUT, "reeval.json"))
        fin = pick_distinct([r for r in rex if r.get("err") is None and float(r.get("follow") or 0) >= 0.999], sc, 10, R_DISTINCT)
        h1 = dict(S["H1"]); jobs = []
        for nm, p in [(f"F{k + 1}", r["p"]) for k, r in enumerate(fin)] + [("H1", h1)]:
            for proto in ("held", "fitbig", "fit60", "cont"):
                jobs.append(dict(id=f"{nm}_{proto}", name=nm, proto=proto, p=p))
        jobs.sort(key=lambda j: ("held", "fitbig", "fit60", "cont").index(j["proto"]))
        jdump(dict(finalists=[dict(name=f"F{k + 1}", src=r["src"], obj=r["obj"], gap=r.get("gap"), p=r["p"]) for k, r in enumerate(fin)], jobs=jobs), vpath)
        log("finalists: " + ", ".join(f"F{k + 1} {r['src']} near1 {r.get('gap_near1')} gap {r.get('gap')} m {r['p']['margin']}" for k, r in enumerate(fin)))
        pool.close(); pool.terminate()
    while not os.path.exists(vpath) and time.time() < T_VER: time.sleep(10)
    if not os.path.exists(vpath): log("no verification jobs: exit"); return
    time.sleep(2); verify(json.load(open(vpath))["jobs"], OUT, ncpu, T_VER, log)


def verify(jobs, OUT, ncpu, T_VER, log):
    """the CPU kit, unpatched, in fresh processes (CB_EXACT=1, CB_FOLD_MARGIN = the config's margin)"""
    import subprocess
    mem = 0
    try: mem = int(open("/sys/fs/cgroup/memory.max").read().strip()) / 2 ** 30
    except Exception: pass                                                                   # noqa: BLE001
    if not mem or mem > 1e6:
        mem = float(os.popen("free -g | awk '/Mem/ {print $2}'").read().strip() or 32)
    slots = max(1, min(ncpu, int(mem / 3.0))); log(f"verify: {len(jobs)} jobs, {slots} slots (mem {mem:.0f} GB)")
    vd = os.path.join(OUT, "verify"); os.makedirs(vd, exist_ok=True); run_ = []

    def start(j):
        p = dict(j["p"]); m = float(p.pop("margin", 5.0)); env = dict(os.environ, CB_EXACT="1", CB_FOLD_MARGIN=str(m), OMP_NUM_THREADS="1",
                                                                       IGL_NUM_THREADS="1", CB_QUIET_EXACT="1")
        o = os.path.join(vd, j["id"] + ".json"); lg = open(os.path.join(vd, j["id"] + ".log"), "w")
        if j["proto"] == "cont":
            cmd = [sys.executable, os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-continuity.py"), "kin", "fitbig", o, json.dumps(p)]
        else:
            cmd = [sys.executable, os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"), j["proto"], o, json.dumps(p)]
        return subprocess.Popen(cmd, env=env, stdout=lg, stderr=subprocess.STDOUT, cwd=REPO), j, time.time()
    q = list(jobs)
    while True:
        while len(run_) < slots and q and time.time() < T_VER:
            j = q.pop(0)
            if claim(os.path.join(OUT, "claims", "v_" + j["id"])): run_.append(start(j)); log(f"verify start {j['id']}")
        if not run_: break
        time.sleep(5)
        for pr, j, t in list(run_):
            if pr.poll() is not None:
                run_.remove((pr, j, t)); log(f"verify done {j['id']} rc {pr.returncode} {time.time() - t:.0f}s")
            elif time.time() > T_VER:
                pr.kill(); run_.remove((pr, j, t)); log(f"verify killed at the deadline {j['id']}")
    log("verify: nothing left for this pod")


# ---- summary (local, after fetching the run directory) -----------------------------------------------------------------
def summary(d, outp):
    sc, lo, hi = spec()
    sob = read_jsonl(os.path.join(d, "sobol_*.jsonl")); cma = read_jsonl(os.path.join(d, "cma_*.jsonl"))
    ok = lambda rows: [r for r in rows if r.get("err") is None]
    reg = {}
    for r in sob:
        nm = r["tag"].split("-")[1] if r["tag"].startswith("sob-") else "seed"; g = reg.setdefault(nm, dict(n=0, ok=0, best=400.0, lt30=0, lt25=0))
        g["n"] += 1
        if r.get("err") is None:
            g["ok"] += 1; g["best"] = min(g["best"], r["obj"]); g["lt30"] += r["obj"] < 30; g["lt25"] += r["obj"] < 25
    bas = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(d, "basin_*.json")))]
    out = dict(n_sobol=len(sob), n_cma=len(cma), n_total=len(sob) + len(cma), n_ok=len(ok(sob)) + len(ok(cma)), regions=reg,
               basins=[dict(j=b["j"], tag0=b["tag0"], gen=b["gen"], best=b["best"]["f"] if b.get("best") else None, stop=b["stop"],
                            p=(b.get("best") or {}).get("row", {}).get("p")) for b in bas],
               secs_median=float(np.median([r.get("secs", 0) for r in sob + cma if r.get("secs")])) if sob else None)
    if os.path.exists(os.path.join(d, "reeval.json")): out["reeval"] = json.load(open(os.path.join(d, "reeval.json")))["reeval"]
    if os.path.exists(os.path.join(d, "verify_jobs.json")): out["finalists"] = json.load(open(os.path.join(d, "verify_jobs.json")))["finalists"]
    V = {}
    for f in sorted(glob.glob(os.path.join(d, "verify", "*.json"))):
        try: V[os.path.basename(f)[:-5]] = json.load(open(f))
        except Exception: pass                                                               # noqa: BLE001
    out["verify"] = V
    json.dump(out, open(outp, "w"), indent=1, default=float); print(json.dumps({k: v for k, v in out.items() if k not in ("reeval", "verify", "basins")}, default=float)[:3000])


def main():
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("args", nargs="*"); ap.add_argument("--out")
    ap.add_argument("--bench", default="110,360"); ap.add_argument("--device", default="cuda"); ap.add_argument("--workers", type=int, default=0)
    a = ap.parse_args()
    if a.cmd == "points":
        X, R = sobol_points(float(os.environ.get("GKS_SCALE", 1.0))); u, c = np.unique(R, return_counts=True)
        print(len(X), dict(zip(u.tolist(), c.tolist()))); print({k: {kk: round(v, 2) for kk, v in p.items()} for k, p in seeds().items()})
    elif a.cmd == "run": run(a)
    elif a.cmd == "final": final(a)
    elif a.cmd == "summary": summary(a.args[0], a.args[1])
    else: raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

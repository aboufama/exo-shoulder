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
    python3 tools/gpu_knee_search.py digest DIR OUT.json      compact digest of a run directory (+ OUT_all.npz of every evaluation)
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
LAM = int(os.environ.get("GKS_LAM", 12))
N_BASINS = int(os.environ.get("GKS_BASINS", 30))
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


def gpu_slots(ncpu, per_gb=max(2.8, float(os.environ.get("GKS_GB_PER_WORKER", 2.8)))):
    """workers the device memory holds: each worker keeps its own int8 grid of the bench (470 poses x 131^3 = 1.06 GB on
    Bench(110,360)) + a CUDA context + the batch temporaries: measured 2.0-2.6 GB per worker on the RTX PRO 4500 (14
    workers ran out of its 31.4 GB), so 2.8 GB is budgeted; capped by the CPUs"""
    try:
        mb = float(os.popen("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits").read().split()[0])
        return max(1, min(ncpu - 1, int((mb / 1024.0 - 2.0) / per_gb)))
    except Exception:                                                                        # noqa: BLE001
        return max(2, ncpu - 1)


def objective(r):
    return float(r["gap_near1"]) + 100.0 * max(0.0, 1.0 - float(r["follow"]))


def _eval(a):
    tag, p, mode = a; t = time.time()
    try:
        S, B, GB = _W["S"], _W["B"], _W["GB"]; m = float(p["margin"])
        if m < MARGIN[1] - 1e-9: return dict(tag=tag, p=p, err="margin < 5", obj=400.0)
        S.SING = m; gd = B._gd; gd.mode_out = mode; nb0 = getattr(gd, "n_bound", 0); no0 = gd.outside
        r = GB.evaluate_one({k: v for k, v in p.items() if k != "margin"}, B)
        if r.get("error") and cuda_err(dict(err=str(r["error"]))):                          # free the cache, retry once
            import torch
            torch.cuda.empty_cache(); r = GB.evaluate_one({k: v for k, v in p.items() if k != "margin"}, B)
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


def cuda_err(r): return bool(r.get("err")) and any(w in r["err"] for w in ("CUDA", "cuda", "out of memory", "AcceleratorError"))


def dedupe(rows):
    """one row per (tag, params): a row that closed beats an error row (a restarted pod re-evaluates its CUDA-error rows);
    the params are part of the key because CMA tags repeat across restarts (basin numbering of the first run)"""
    best = {}
    for r in rows:
        t = (r.get("tag"), json.dumps(r.get("p"), sort_keys=True)); o = best.get(t)
        if o is None or (o.get("err") is not None and r.get("err") is None): best[t] = r
    return list(best.values())


def dedupe_last(rows):
    """CMA rows: one row per tag, the LAST one written wins (a restarted pod re-uses the tag scheme cma-b<j>-g<gen>-<i>
    for its new basins; rows of the first, out-of-memory run come earlier in the same file)"""
    best = {}
    for r in rows: best[r.get("tag")] = r
    return list(best.values())


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

    def state(self):
        return dict(c0=self.c0.tolist(), mean=self.mean.tolist(), sigma=self.sigma, C=self.C.tolist(), pc=self.pc.tolist(), ps=self.ps.tolist(),
                    gen=self.gen, seed=self.seed, best=self.best, best_gen=self.best_gen, hist=self.hist)

    def load(self, st):
        self.c0 = np.array(st["c0"]); self.mean = np.array(st["mean"]); self.sigma = st["sigma"]; self.C = np.array(st["C"])
        self.pc = np.array(st["pc"]); self.ps = np.array(st["ps"]); self.gen = st["gen"]; self.seed = st["seed"]; self.best = st["best"]
        self.best_gen = st["best_gen"]; self.hist = st["hist"]; D2, self.B = np.linalg.eigh(self.C); self.D = np.sqrt(np.maximum(D2, 1e-20))

    def stop(self):
        if self.sigma * self.D.max() < 0.02: return "sigma collapsed"
        if self.gen - self.best_gen >= 40: return "no gain > 0.02 in 40 generations"
        return ""


# ---- the pool feeder ---------------------------------------------------------------------------------------------------
class Deadlines:
    """GKS_T_SOBOL / GKS_T_CMA / GKS_T_VERIFY from the environment, overridden by $OUT/deadlines.json on the volume
    ({"sob": epoch, "cma": epoch, "ver": epoch}, re-read every 20 s): the schedule can be pulled in without a restart"""
    def __init__(self, out):
        self.f = os.path.join(out, "deadlines.json"); self.t = 0.0; self.d = {}
        sob = float(os.environ.get("GKS_T_SOBOL", time.time() + 1800)); cma = float(os.environ.get("GKS_T_CMA", sob + 1500))
        self.env = dict(sob=sob, cma=cma, ver=float(os.environ.get("GKS_T_VERIFY", cma + 1800)))

    def __call__(self, k):
        if time.time() - self.t > 20:
            self.t = time.time()
            try: self.d = json.load(open(self.f))
            except Exception: pass                                                           # noqa: BLE001
        return float(self.d.get(k, self.env[k]))


def dead_pods(out):
    """pods terminated by the lead ($OUT/dead.txt, one id per line): their unfinished chunks are re-run by a live pod"""
    try: return {x.strip() for x in open(os.path.join(out, "dead.txt")) if x.strip()}
    except OSError: return set()


def alive_pods(out):
    return sorted(x for x in (os.path.basename(f)[6:] for f in glob.glob(os.path.join(out, "alive_*"))) if x not in dead_pods(out))


def feed(pool, items, W, on_result, deadline=None):
    """apply_async with at most 3 W in flight; items is an iterator (pulled lazily); deadline: a callable -> epoch s"""
    pend = deque(); n = 0; it = iter(items)
    while True:
        while len(pend) < 3 * W and (deadline is None or time.time() < deadline()):
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
    DL = Deadlines(OUT); scale = float(os.environ.get("GKS_SCALE", 1.0))
    log = lambda s: print(f"[{time.strftime('%H:%M:%S', time.gmtime())} {me}] {s}", flush=True)
    open(os.path.join(OUT, f"alive_{me}"), "w").write(f"{time.time():.0f}")
    nc, nw = (int(x) for x in a.bench.split(","))
    ncpu = len(os.sched_getaffinity(0))
    try:
        q = open("/sys/fs/cgroup/cpu.max").read().split()
        if q[0] != "max": ncpu = min(ncpu, max(1, int(int(q[0]) / int(q[1]))))
    except Exception: pass                                                                   # noqa: BLE001
    W = a.workers or (gpu_slots(ncpu) if a.device == "cuda" else max(2, ncpu - 1)); log(f"cpus {ncpu} workers {W} bench {nc},{nw} device {a.device} scale {scale}; deadlines sobol {DL('sob') - time.time():.0f}s cma {DL('cma') - time.time():.0f}s verify {DL('ver') - time.time():.0f}s")
    sc, lo, hi = spec(); S = seeds()
    pool = mp.get_context("spawn").Pool(W, initializer=_w_init, initargs=(nc, nw, a.device))
    # 1. seeds + 2. Sobol chunks
    X, R = sobol_points(scale); nch = (len(X) + CHUNK - 1) // CHUNK; log(f"sobol plan {len(X)} points, {nch} chunks")
    LS = Log(os.path.join(OUT, f"sobol_{me}.jsonl"))
    if claim(os.path.join(OUT, "claims", "seeds")):
        res = pool.map(_eval, [(f"seed-{k}", p, "exact") for k, p in S.items()]); LS.write(res)
        for r in res: log(f"seed {r['tag']}: obj {r.get('obj')} near1 {r.get('gap_near1')} gap {r.get('gap')} reach {r.get('reach')} follow {r.get('follow')} {r.get('err', '')}")

    own = os.path.join(OUT, f"sobol_{me}.jsonl")
    prev = read_jsonl(own) if os.path.exists(own) else []
    okt = {r["tag"] for r in prev if r.get("err") is None}
    retry = [r for r in dedupe(prev) if cuda_err(r) and r["tag"] not in okt]
    if retry: log(f"restart: re-evaluating {len(retry)} rows that failed on a CUDA error (of {len(prev)} rows)")
    for dp in sorted(dead_pods(OUT)):                     # a terminated pod: its CUDA-error rows + the rest of its claimed chunks
        op = os.path.join(OUT, "claims", f"orph_{dp}")
        if dp == me: continue
        if not claim(op):                                 # a restarted pod takes back the orphans it had claimed
            try:
                if open(op).read().split()[0] != me: continue
            except (OSError, IndexError): continue
        allrows = dedupe(read_jsonl(os.path.join(OUT, "sobol_*.jsonl"))); okt2 = {r["tag"] for r in allrows if r.get("err") is None}
        dr = [r for r in dedupe(read_jsonl(os.path.join(OUT, f"sobol_{dp}.jsonl"))) if cuda_err(r) and r["tag"] not in okt2]
        have = {r["tag"] for r in allrows}; miss = []
        for c in range(nch):
            cp = os.path.join(OUT, "claims", f"s{c}")
            try: owner = open(cp).read().split()[0]
            except (OSError, IndexError): continue
            if owner != dp: continue
            for i in range(c * CHUNK, min(len(X), (c + 1) * CHUNK)):
                if f"sob-{R[i]}-{i}" not in have: miss.append(dict(tag=f"sob-{R[i]}-{i}", p=to_dict(X[i])))
        retry += dr + miss; log(f"dead pod {dp}: re-running {len(dr)} CUDA-error rows + {len(miss)} unevaluated points of its chunks")

    def sob_items():
        for r in retry:
            if time.time() >= DL("sob"): return
            yield (r["tag"], r["p"], "exact" if r["tag"].startswith("seed-") else "bound")
        for c in range(nch):
            if time.time() >= DL("sob"): return
            if not claim(os.path.join(OUT, "claims", f"s{c}")): continue
            for i in range(c * CHUNK, min(len(X), (c + 1) * CHUNK)):
                yield (f"sob-{R[i]}-{i}", to_dict(X[i]), "bound")
    buf = []; t0 = time.time(); best = [400.0]

    def on_sob(r):
        buf.append(r); best[0] = min(best[0], r.get("obj", 400.0))
        if len(buf) >= 256:
            LS.write(buf); buf.clear(); log(f"sobol {LS.n} evals ({LS.n / (time.time() - t0):.1f}/s) best obj {best[0]:.2f}")
    feed(pool, sob_items(), W, on_sob, deadline=lambda: DL("sob")); LS.write(buf); buf.clear()
    open(os.path.join(OUT, f"sobol2_{me}.done"), "w").write(f"{LS.n}"); log(f"sobol done: {LS.n} evals in {time.time() - t0:.0f}s")
    # 3. basins (one pod computes them; the others wait)
    while time.time() < DL("sob") + 300:
        alive = alive_pods(OUT)
        if all(os.path.exists(os.path.join(OUT, f"sobol2_{x}.done")) for x in alive): break
        time.sleep(10)
    bpath = os.path.join(OUT, "basins_r2.json")
    if claim(os.path.join(OUT, "claims", "basins_r2")):
        rows = dedupe(read_jsonl(os.path.join(OUT, "sobol_*.jsonl"))); B = pick_distinct(rows, sc, 60, R_BASIN)
        jdump(dict(n_rows=len(rows), basins=[dict(j=j, tag=r["tag"], obj=r["obj"], p=r["p"]) for j, r in enumerate(B)]), bpath)
        log(f"basins from {len(rows)} rows: " + ", ".join(f"{r['tag']} {r['obj']:.2f}" for r in B[:30]))
    while not os.path.exists(bpath): time.sleep(5)
    time.sleep(2); basins = json.load(open(bpath))["basins"]
    alive = alive_pods(OUT); rank = alive.index(me) if me in alive else 0
    quota = max(1, math.ceil(min(N_BASINS, len(basins)) / max(1, len(alive))))
    LC = Log(os.path.join(OUT, f"cma_{me}.jsonl")); act = []

    def take(prefer, resume=False):
        for j in prefer:
            if j >= len(basins): continue
            cp = os.path.join(OUT, "claims", f"r2b{j}")
            if resume:                                    # a restarted pod resumes ITS unfinished basins (state file, else best row)
                try: mine = open(cp).read().split()[0] == me
                except (OSError, IndexError): mine = False
                if not mine or os.path.exists(os.path.join(OUT, f"basin_{j}.json")): continue
            elif not claim(cp): continue
            b = basins[j]; cm = CMA(to_vec(b["p"]), 0.6, 9000 + j, sc, lo, hi); cm.j = j; cm.tag0 = b["tag"]
            if resume:
                stf = os.path.join(OUT, f"cmastate_{j}.json")
                if os.path.exists(stf):
                    cm.load(json.load(open(stf))); log(f"basin {j} resumed from its state at gen {cm.gen} (best {cm.best['f'] if cm.best else None})")
                else:
                    rr = [r for r in read_jsonl(os.path.join(OUT, f"cma_{me}.jsonl")) if r.get("b") == j]
                    okr = [r for r in rr if r.get("err") is None]
                    if okr:
                        bst = min(okr, key=lambda r: r["obj"] + r.get("pen", 0)); cm = CMA(to_vec(bst["p"]), 0.3, 9100 + j, sc, lo, hi); cm.j = j; cm.tag0 = b["tag"]
                        cm.gen = max(r.get("g", 0) for r in rr); cm.best = dict(f=bst["obj"] + bst.get("pen", 0), row=bst, gen=bst.get("g", 0)); cm.best_gen = cm.gen
                        log(f"basin {j} resumed from its best row {bst['tag']} ({bst['obj']:.2f}) at gen {cm.gen}, sigma 0.3")
            return cm
        return None
    for j in range(len(basins)):
        cm = take([j], resume=True)
        if cm is not None: act.append(cm)
    order = [j for j in range(min(N_BASINS, len(basins))) if j % max(1, len(alive)) == rank] + list(range(len(basins)))
    while len(act) < quota:
        cm = take(order)
        if cm is None: break
        act.append(cm)
    log(f"cma: {len(act)} basins {[c.j for c in act]} (alive {len(alive)}, rank {rank})"); done = []
    while act and time.time() < DL("cma"):
        tg = time.time(); items = []
        for cm in act:
            for i, (p, pen) in enumerate(cm.ask()): items.append((cm, i, p, pen))
        res = pool.map(_eval, [(f"cma-b{cm.j}-g{cm.gen}-{i}", p, "bound") for cm, i, p, pen in items], chunksize=1)
        LC.write([dict(r, b=cm.j, g=cm.gen, pen=round(pen, 4)) for r, (cm, i, p, pen) in zip(res, items)])
        k = 0
        for cm in act:
            f = [res[k + i]["obj"] + items[k + i][3] for i in range(cm.lam)]; cm.tell(f, res[k:k + cm.lam]); k += cm.lam
            try: jdump(cm.state(), os.path.join(OUT, f"cmastate_{cm.j}.json"))
            except Exception: pass                                                           # noqa: BLE001
        fin = [cm for cm in act if cm.stop()]
        for cm in fin:
            act.remove(cm); done.append(cm)
            jdump(dict(j=cm.j, tag0=cm.tag0, gen=cm.gen, best=cm.best, stop=cm.stop(), sigma=cm.sigma, hist=cm.hist), os.path.join(OUT, f"basin_{cm.j}.json"))
            log(f"basin {cm.j} ({cm.tag0}) done at gen {cm.gen}: best {cm.best['f']:.2f} ({cm.stop()})")
            if DL("cma") - time.time() > 300:
                nx = take(range(len(basins)))
                if nx is not None: act.append(nx); log(f"basin {nx.j} claimed")
        if act and act[0].gen % 10 == 0:
            log(f"cma gen {act[0].gen}: {len(act)} active, {LC.n} evals, gen {time.time() - tg:.1f}s, bests " + " ".join(f"b{c.j}:{c.best['f']:.2f}" for c in act))
    for cm in act + done:
        jdump(dict(j=cm.j, tag0=cm.tag0, gen=cm.gen, best=cm.best, stop=cm.stop() or "deadline", sigma=cm.sigma, hist=cm.hist), os.path.join(OUT, f"basin_{cm.j}.json"))
    open(os.path.join(OUT, f"cma2_{me}.done"), "w").write(f"{LC.n}"); log(f"cma done: {LC.n} evals")
    pool.close(); pool.terminate()


def final(a):
    """4. final (a separate process, so a fix dropped on the volume applies): the top 30 distinct over every row
    re-evaluated with the port's EXACT outside path by one pod, the top 10 + H1 -> verification jobs for every pod's CPUs"""
    import multiprocessing as mp
    OUT = a.out; me = os.environ.get("RUNPOD_POD_ID", "local"); sc, lo, hi = spec(); S = seeds()
    DL = Deadlines(OUT)
    log = lambda s: print(f"[{time.strftime('%H:%M:%S', time.gmtime())} {me}] {s}", flush=True)
    nc, nw = (int(x) for x in a.bench.split(","))
    ncpu = len(os.sched_getaffinity(0))
    try:
        q = open("/sys/fs/cgroup/cpu.max").read().split()
        if q[0] != "max": ncpu = min(ncpu, max(1, int(int(q[0]) / int(q[1]))))
    except Exception: pass                                                                   # noqa: BLE001
    W = a.workers or (gpu_slots(ncpu) if a.device == "cuda" else max(2, ncpu - 1))
    alive = alive_pods(OUT)
    vpath = os.path.join(OUT, "verify_jobs.json")
    if claim(os.path.join(OUT, "claims", "final_r2")):
        pool = mp.get_context("spawn").Pool(W, initializer=_w_init, initargs=(nc, nw, a.device))
        while time.time() < DL("cma") + 240:
            if all(os.path.exists(os.path.join(OUT, f"cma2_{x}.done")) for x in alive_pods(OUT)): break
            time.sleep(10)
        rows = dedupe(read_jsonl(os.path.join(OUT, "sobol_*.jsonl"))) + read_jsonl(os.path.join(OUT, "cma_*.jsonl"))   # every CMA row is an evaluation of its own params
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
    while not os.path.exists(vpath) and time.time() < DL("ver"): time.sleep(10)
    if not os.path.exists(vpath): log("no verification jobs: exit"); return
    time.sleep(2); verify(json.load(open(vpath))["jobs"], OUT, ncpu, DL, log)


def verify(jobs, OUT, ncpu, DL, log):
    """the CPU kit, unpatched, in fresh processes (CB_EXACT=1, CB_FOLD_MARGIN = the config's margin)"""
    import subprocess
    mem = 0
    try: mem = int(open("/sys/fs/cgroup/memory.max").read().strip()) / 2 ** 30
    except Exception: pass                                                                   # noqa: BLE001
    if not mem or mem > 1e6:
        mem = float(os.popen("free -g | awk '/Mem/ {print $2}'").read().strip() or 32)
    slots = max(1, min(ncpu - 1, int(mem / float(os.environ.get("GKS_GB_PER_VERIFY", 4.5))))); log(f"verify: {len(jobs)} jobs, {slots} slots (mem {mem:.0f} GB)")
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
        while len(run_) < slots and q and time.time() < DL("ver"):
            j = q.pop(0)
            if claim(os.path.join(OUT, "claims", "v_" + j["id"])): run_.append(start(j)); log(f"verify start {j['id']}")
        if not run_: break
        time.sleep(5)
        for pr, j, t in list(run_):
            if pr.poll() is not None:
                run_.remove((pr, j, t)); log(f"verify done {j['id']} rc {pr.returncode} {time.time() - t:.0f}s")
            elif time.time() > DL("ver"):
                pr.kill(); run_.remove((pr, j, t)); log(f"verify killed at the deadline {j['id']}")
    log("verify: nothing left for this pod")


# ---- digest (on the volume, through a farm job) + log (local) ---------------------------------------------------------
MET = ("obj", "gap_near1", "gap", "reach", "follow", "inband14", "inband10", "contact", "near_min")


def digest(d, outp):
    """compact digest of a run directory: counts, per-region stats, the top 2000 Sobol rows, per-basin best-per-generation,
    the basins, the exact re-evaluation, the finalists and every verification output; + an npz of every evaluation"""
    sob_raw = read_jsonl(os.path.join(d, "sobol_*.jsonl")); cma_raw = read_jsonl(os.path.join(d, "cma_*.jsonl"))
    sob, cma = dedupe(sob_raw), cma_raw
    n_cuda = dict(sobol=sum(1 for r in sob if cuda_err(r)), cma=sum(1 for r in cma if cuda_err(r)), raw_rows=len(sob_raw) + len(cma_raw))
    reg = {}
    for r in sob:
        nm = r["tag"].split("-")[1] if r["tag"].startswith("sob-") else "seed"; g = reg.setdefault(nm, dict(n=0, ok=0, best=400.0, lt30=0, lt25=0, lt22=0))
        g["n"] += 1
        if r.get("err") is None:
            g["ok"] += 1; g["best"] = min(g["best"], r["obj"]); g["lt30"] += r["obj"] < 30; g["lt25"] += r["obj"] < 25; g["lt22"] += r["obj"] < 22
    slim = lambda r: {k: r.get(k) for k in ("tag", "p", "secs", "nb", "err", "b", "g", "pen", "near1_poses", "knee_ang", "gap_near2") + MET if r.get(k) is not None}
    ok = sorted([r for r in sob if r.get("err") is None], key=lambda r: r["obj"])
    traj = {}
    for r in cma:
        b = r.get("b"); g = r.get("g")
        if b is None: continue
        cur = traj.setdefault(b, {}).get(g)
        if r.get("err") is None and (cur is None or r["obj"] + r.get("pen", 0) < cur["obj"] + cur.get("pen", 0)): traj[b][g] = slim(r)
    bas = []
    b2 = os.path.join(d, "basins_r2.json"); want = {b["j"]: b["tag"] for b in json.load(open(b2))["basins"]} if os.path.exists(b2) else None
    for f in sorted(glob.glob(os.path.join(d, "basin_*.json"))):
        b = json.load(open(f))
        if want is not None and want.get(b["j"]) != b["tag0"]: continue                     # a stale basin of the first (OOM) run
        bas.append(dict(j=b["j"], tag0=b["tag0"], gen=b["gen"], stop=b["stop"], sigma=b["sigma"],
                                                best=slim(b["best"]["row"]) if b.get("best") else None, best_f=(b.get("best") or {}).get("f"), hist=b.get("hist")))
    secs = [r["secs"] for r in sob + cma if r.get("secs")]
    out = dict(run=d, n_cuda_err=n_cuda, n_sobol=len(sob), n_cma=len(cma), n_total=len(sob) + len(cma), n_ok=sum(1 for r in sob + cma if r.get("err") is None),
               n_bound=sum(1 for r in sob + cma if r.get("nb")), secs_median=float(np.median(secs)) if secs else None, regions=reg,
               sobol_top=[slim(r) for r in ok[:2000]], seeds=[slim(r) for r in sob if r["tag"].startswith("seed-")],
               cma_top=[slim(r) for r in sorted([r for r in cma if r.get("err") is None], key=lambda r: r["obj"])[:500]], basin_runs=sorted(bas, key=lambda b: b["j"]),
               logs={os.path.basename(f): open(f).read()[-6000:] for f in glob.glob(os.path.join(d, "log_*.txt"))},
               alive=[os.path.basename(f)[6:] for f in glob.glob(os.path.join(d, "alive_*"))])
    for nm, f in (("basins", "basins_r2.json"), ("reeval", "reeval.json"), ("verify_jobs", "verify_jobs.json")):
        f = os.path.join(d, f)
        if os.path.exists(f): out[nm] = json.load(open(f))
    V = {}
    for f in sorted(glob.glob(os.path.join(d, "verify", "*.json"))):
        try: V[os.path.basename(f)[:-5]] = json.load(open(f))
        except Exception as e: V[os.path.basename(f)[:-5]] = dict(error=repr(e))                 # noqa: BLE001
    out["verify"] = V; out["verify_logs"] = {os.path.basename(f): open(f).read()[-1500:] for f in glob.glob(os.path.join(d, "verify", "*.log"))}
    json.dump(out, open(outp, "w"), default=float)
    A = np.array([[float(r["p"][k]) for k in KEYS] + [float(r.get(m) if r.get(m) is not None else np.nan) for m in MET[:8]]
                  + [1.0 if r["tag"].startswith("cma-") else 0.0] for r in sob + cma if r.get("p")], np.float32)
    np.savez_compressed(outp[:-5] + "_all.npz", A=A, cols=np.array(list(KEYS) + list(MET[:8]) + ["is_cma"]))
    print(json.dumps({k: out[k] for k in ("n_sobol", "n_cma", "n_total", "n_ok", "n_bound", "secs_median", "regions", "alive")}, default=float))


def vsum(V, nm):
    """the verification numbers of one finalist (polish harness fit60 / fitbig / held + continuity)"""
    o = {}
    for proto in ("fitbig", "fit60", "held"):
        v = V.get(f"{nm}_{proto}") or {}
        if "corrected" not in v: o[proto] = dict(missing=True, error=v.get("error")); continue
        c, a, rt = v["corrected"], v.get("corrected_audit") or {}, v.get("redteam") or {}
        o[proto] = dict(gap=c["gap"], gap_near1=a.get("gap_near1"), reach=c["reach"], follow=c["follow"], inband14=c["inband14"],
                        inband10=c["inband10"], contact=c["contact"], near1_poses=a.get("near1_poses"), min_metal_mm=a.get("near_touch_min_mm"),
                        overhead140=a.get("overhead140"), fit_gap=(v.get("fit") or {}).get("gap"), fit_mode=v.get("fit_mode"), wear_mode=v.get("wear_mode"),
                        n_wear=v.get("n_wear"), margin=v.get("fold_margin"), bad_removed=v.get("bad_removed"),
                        fold_margin_min_taken=rt.get("fold_margin_min_taken_deg"), knee_ang=rt.get("knee_ang_taken"),
                        knee_sing_min=rt.get("knee_sing_dist_min_deg"), arm_side_lt1=(rt.get("arm_side") or {}).get("lt1"),
                        j1_seat=rt.get("j1_seat"), hubs=rt.get("hubs"), secs=v.get("secs"))
    c = V.get(f"{nm}_cont") or {}
    if c.get("grid"):
        o["continuity"] = dict(grid=c["grid"], bench110_360=c.get("bench110_360"), knee_branch_signs=c.get("knee_branch_signs"), edges=c.get("edges"))
    else: o["continuity"] = dict(missing=True)
    return o


def log(dig_path, cost=None):
    """merge a digest into the sweep log (stage gpu-knee-*) and the rows file (key gpu_knee_massive); re-reads both files
    right before writing (other workflows write them too)"""
    import knee_polish as KP
    D = json.load(open(dig_path)); base = KP.base_params(); t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    bench = ("Bench(110,360) fast, same-bench (shape fitted there); GPU port tools/gpu_bench_knee.py (the CPU kit's code, per-pose loops "
             "on the device, parity 0.0); verifier checks + near-touch audit; fold margin = params.margin; O20; J1 back / acromion top")
    full = lambda p: dict(base, **{k: v for k, v in p.items() if k != "margin"}, margin=p.get("margin", 5.0))
    rows = []

    def add(stage, r, **kw):
        rows.append(dict(t=t, stage=stage, bench=bench, params=full(r["p"]), **{m: r.get(m) for m in ("inband14", "inband10", "reach", "follow", "contact", "gap", "gap_near1", "obj", "near_min")},
                         honest=r.get("err") is None, tag=r["tag"], src="gpu-knee", **kw))
    for r in D.get("seeds", []): add("gpu-knee-seed", r)
    for r in D.get("sobol_top", [])[:300]: add("gpu-knee-sobol", r, outside_bound=bool(r.get("nb")))
    for r in D.get("cma_top", [])[:200]: add("gpu-knee-cma", r, gen=r.get("g"), basin=r.get("b"))
    for b in D.get("basin_runs", []):
        if b.get("best"): add(f"gpu-knee-cma-b{b['j']}", b["best"], gen=b["gen"], basin_best=True, stop=b["stop"])
    for r in (D.get("reeval") or {}).get("reeval", []): add("gpu-knee-reeval", r, search_tag=r.get("src"), obj_search=r.get("obj_search"), path="exact outside")
    V = D.get("verify") or {}; fins = (D.get("verify_jobs") or {}).get("finalists", [])
    for f in fins + [dict(name="H1", p=seeds()["H1"], src="H1")]:
        vs = vsum(V, f["name"]); fb = vs.get("fitbig", {})
        rows.append(dict(t=t, stage="gpu-knee-verify", bench="CPU kit exact frozen: fit Bench(110,360) fast -> wear Bench(110,360) exact (fitbig); also fit60 and held "
                         "(docs/concepts/verify/skin-normal-3r-pin-knee-polish.py, CB_EXACT=1, CB_FOLD_MARGIN = params.margin) + continuity",
                         params=full(f["p"]), gap=fb.get("gap"), gap_near1=fb.get("gap_near1"), reach=fb.get("reach"), follow=fb.get("follow"),
                         inband14=fb.get("inband14"), inband10=fb.get("inband10"), contact=fb.get("contact"), honest=not fb.get("missing"),
                         tag=f"verify-{f['name']}", src="gpu-knee", search_tag=f.get("src"), verify=vs))
    rows.append(dict(t=t, stage="gpu-knee-summary", tag="gpu-knee-summary", src="gpu-knee", n_sobol=D["n_sobol"], n_cma=D["n_cma"], n_total=D["n_total"],
                     n_ok=D["n_ok"], regions=D["regions"], secs_median=D["secs_median"], pods=D.get("alive"), cost=cost))
    SW = os.environ.get("GKS_SWEEP") or os.path.join(REPO, "docs", "concepts", "sweeps", "skin-normal-3r-pin-knee.json")
    d = json.load(open(SW)); have = {r.get("tag") + "|" + str(r.get("stage")) for r in d if str(r.get("stage", "")).startswith("gpu-knee")}
    k = max(r.get("k", 0) for r in d) + 1; new = []
    for r in rows:
        if r["tag"] + "|" + r["stage"] in have: continue
        new.append(dict(k=k, **r)); k += 1
    d += new; json.dump(d, open(SW + ".tmp", "w"), indent=1, default=float); os.replace(SW + ".tmp", SW)
    print(f"sweep log: {len(new)} new gpu-knee rows (k {new[0]['k'] if new else '-'}..{k - 1})")
    return rows


def report(dig_path):
    """markdown tables of a digest (doc section / FINDINGS)"""
    D = json.load(open(dig_path)); L = []
    L.append(f"Evaluations: {D['n_total']:,} ({D['n_sobol']:,} seeds + Sobol, {D['n_cma']:,} CMA), {D['n_ok']:,} closed a report; "
             f"{D['n_bound']:,} used the outside-grid bound; median {D['secs_median']:.2f} s per evaluation per worker; pods {len(D.get('alive') or [])}.")
    L.append("\n| region | evaluated | closed | best obj | < 30 | < 25 | < 22 |\n|---|---|---|---|---|---|---|")
    for k, g in sorted(D["regions"].items(), key=lambda kv: kv[1]["best"]):
        L.append(f"| {k} | {g['n']:,} | {g['ok']:,} | {g['best']:.2f} | {g['lt30']:,} | {g['lt25']:,} | {g['lt22']:,} |")
    L.append("\n| basin | start | start obj | gens | stop | best obj | near1 | gap | reach | follow | in-band 14 | margin |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    st = {b["j"]: b for b in (D.get("basins") or {}).get("basins", [])}
    bl = D.get("basin_runs") or []
    for b in sorted(bl, key=lambda b: b["best_f"] if b.get("best_f") is not None else 999)[:30]:
        r = b.get("best") or {}; s0 = st.get(b["j"], {})
        L.append(f"| b{b['j']} | {b['tag0']} | {s0.get('obj', '')} | {b['gen']} | {b['stop']} | {b['best_f']:.2f} | {r.get('gap_near1')} | {r.get('gap')} | {r.get('reach')} | "
                 f"{r.get('follow')} | {r.get('inband14')} | {(r.get('p') or {}).get('margin')} |")
    V = D.get("verify") or {}; fins = (D.get("verify_jobs") or {}).get("finalists", [])
    if fins:
        L.append("\n| config | search tag | GPU obj | margin | fitbig gap / near1 | fit60 gap / near1 | held gap / near1 | reach / follow / in-band 14 (fitbig) | "
                 "min metal mm | connected reach (grid) | islands |\n|---|---|---|---|---|---|---|---|---|---|---|")
        for f in fins + [dict(name="H1", src="H1 (verified leader)", obj=None, p=dict(seeds()["H1"]))]:
            vs = vsum(V, f["name"]); g = lambda pr, k: (vs.get(pr) or {}).get(k)
            c = (vs.get("continuity") or {}).get("grid") or {}
            L.append(f"| {f['name']} | {f['src']} | {f['obj'] if f['obj'] is not None else '-'} | {f['p'].get('margin', 5.0)} | "
                     f"{g('fitbig', 'gap')} / {g('fitbig', 'gap_near1')} | {g('fit60', 'gap')} / {g('fit60', 'gap_near1')} | {g('held', 'gap')} / {g('held', 'gap_near1')} | "
                     f"{g('fitbig', 'reach')} / {g('fitbig', 'follow')} / {g('fitbig', 'inband14')} | {g('fitbig', 'min_metal_mm')} | "
                     f"{c.get('connected_reach')} | {c.get('islands')} |")
    return "\n".join(L)


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
    elif a.cmd == "digest": digest(a.args[0], a.args[1])
    elif a.cmd == "log": log(a.args[0], a.args[1] if len(a.args) > 1 else None)
    elif a.cmd == "report": print(report(a.args[0]))
    else: raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

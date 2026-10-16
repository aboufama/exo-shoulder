#!/usr/bin/env python3
"""CROSS-FIT FINAL POLISH: a model-agnostic final-polish objective + CMA driver whose score of a parameter set is the
near-touch gap on poses the frozen SHAPE was NOT fitted on (CLAUDE.md "The fold margin is read in ONE metric ...":
final polishes score only poses the shape was not fitted on, 2-fold cross-fit; "Search on the near-touch gap"; the
continuity rule; "Keep the held-out split held out").

Why: every in-sample polish of the pin knee lost ~5 points held out (P5 21.92 polish bench vs 28.96 held out, C1 23.04
vs 28.22, GPU F7 20.81 vs 27.22; H1 itself 24.48 vs 28.55). The shape (link heights, knee reference, hub heights) is
FITTED on the bench poses, so a same-bench objective rewards parameters whose fitted shape just clears those poses.

The pose pool = the search poses only: Bench(110,360) U Bench(60,160) (634 poses: fit-clip frames + workspace poses).
The verifier's held-out set (every fit-clip frame and workspace pose OUTSIDE both benches, 1154 poses; the held-out clips
Wave / Walking never) is never touched here (asserted). The pool is split into 2 folds by a fixed seed (XFIT_SEED,
default 20261016), STRATIFIED: clip frames per (clip, region), workspace poses per region, regions = overhead
(elev >= 140), across-body (plane >= 100, elev >= 40), behind-the-back (clip name has "back", or plane < -30 and
elev > 20), else elevation bands of 35 deg; each stratum is shuffled and dealt alternately, so every clip and every
region sits in both folds.

Objective of a parameter set p (lower is better):
    for (A, B) in ((0, 1), (1, 0)):  fit the shape on fold A (fast grid)  ->  wear it FROZEN on fold B (fast grid)
                                     -> the model's verifier checks knock poses out -> continuity: workspace poses not
                                        reachable from the rest region by the kinematic flood fill are not taken
                                     -> the model's audit: near-touch gap (metal < 1 mm = contact) on fold B
    obj = mean of the two out-of-fold near-touch gaps (+ XFIT_OH_PEN per overhead clip frame lost, default 0)
The in-fold (in-sample) numbers are logged next to it, so the in-sample vs out-of-fold drop is visible per row.

Continuity (CLAUDE.md "Reach must be reachable by moving"): for models with passive / stopped joints the plug-in gives
its kinematics; the flood fill is the verifier's (docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py `conn`, kinematic
nodes): the 1432-pose workspace grid, 2-deg slerp edges seeded at elevation 0 (and K on stop A for the knuckle), no joint
step > 10 deg, knee branch constant. It runs once per fold fit (the knee reference m is the fold's).

Plug-ins:
  knee   : skin-normal-3r-pin-knee (tools/knee_polish.py model + the adversarial verifier's extra checks + MK.audit);
           FREE = tools/knee_polish.py FREE + `margin` (the J1-J3 fold margin, >= 5 = the user's floor, set on the IK's
           SING per evaluation like the GPU search; the claim runs with CB_FOLD_MARGIN = margin).
  minarc : minarc-stop-knuckle-4r BDp (docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py, kitrule 1 phys 1 capK 6
           m3e 1; the claim harness models/minarc-stop-knuckle-4r-kitrule-wear.py's checks: the remeasure verifier's
           extra checks + the kit margin in every state + the physical q2 slot); FREE = the knee's + bk1 bk2 a1max smhi smlo.

    python3 tools/crossfit_polish.py folds                                 print the split (sizes per stratum)
    python3 tools/crossfit_polish.py score PLUGIN OUT '[{"tag":..,"params":{..}}, ...]' [--jobs 2]
                                                                           cross-fit objective of a list of configs
    python3 tools/crossfit_polish.py cma PLUGIN --x0 '{..}' --label L --out O.json [--sigma 0.4] [--popsize 12]
                                     [--jobs 6] [--budget-s T] [--max-evals N] [--max-gen G] [--seed k] [--patience 12]
    python3 tools/crossfit_polish.py best O1.json [O2.json ...]           best rows over runs (by the objective)
    python3 tools/crossfit_polish.py farm PLUGIN [--starts a,b,c] [--label L] [--budget-s 1800] [--max-evals 700]
                                     [--popsize 8] [--sigma 0.4] [--patience 10] [--dry-run]
        ONE COMMAND for a final polish on the CPU farm: one job per start (8 processes, Bench(110,360) cache linked),
        jobs written to docs/research/crossfit/jobs_<label>.json, then tools/cloud_run.py batch (unless --dry-run).
        Starts: "base" (the plug-in's base: H1 / BDp) and any key of docs/research/crossfit/refs.json; for minarc a ref
        start moves only its seat + knee keys (tools/knee_polish.py FREE) onto BDp (the knuckle keys stay BDp's).
Env: XFIT_SEED (fold seed), XFIT_DIR (derived fold grid caches, default /tmp/xfit), XFIT_CONN (1 = continuity on, default),
XFIT_OH_PEN (gap points per overhead clip frame lost out of fold, default 0), XFIT_SRC ("110,360;60,160" default; a
local smoke test may use "60,160"). On the farm prefix with "$(python3 tools/bench_cache_farm.py use 110 360)" so
Bench(110,360) is fast (Bench(60,160)'s cache is in the shipped .cache).
"""
import fcntl, importlib.util, json, math, multiprocessing as mp, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

SEED = int(os.environ.get("XFIT_SEED", 20261016))
SRC = tuple(tuple(int(x) for x in s.split(",")) for s in os.environ.get("XFIT_SRC", "110,360;60,160").split(";"))
XDIR = os.environ.get("XFIT_DIR", "/tmp/xfit")
CONN = os.environ.get("XFIT_CONN", "1") == "1"
OH_PEN = float(os.environ.get("XFIT_OH_PEN", 0.0))
ALLOWED_SRC = {(110, 360), (60, 160)}                        # the search benches; the verifier's held-out set is their complement
assert set(SRC) <= ALLOWED_SRC, f"XFIT_SRC {SRC}: only the search benches {ALLOWED_SRC} (the held-out set stays held out)"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


def _fast(nc, nw):
    old = os.environ.pop("CB_EXACT", None)
    try: return CB.Bench(nc, nw)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old


# ---------------------------------------------------------------------------------------------------------------------
# pose pool, strata, folds
def region(name, kind, pose):
    el, pl = float(pose[1]), float(pose[0])
    if el >= 140: return "overhead"
    if pl >= 100 and el >= 40: return "across"
    if (kind == "clip" and "back" in name.lower()) or (pl < -30 and el > 20): return "behind"
    return f"el{int(min(el, 139.9) // 35)}"


def pool():
    """global pose indices of the search benches (union) -> (source bench, local index); asserts the held-out split"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
    src = {}
    for nc, nw in SRC:
        for j, g in enumerate(CB._select(nc, nw)[0].tolist()): src.setdefault(int(g), ((nc, nw), j))
    held = set()
    for nm in ("Wave", "Walking arm swing"):
        if nm in names: held.add(names.index(nm))
    assert not any(int(cid[g]) in held for g in src), "held-out clip in the pool"
    used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
    assert set(src) <= used, "pool pose outside the search benches (would touch the verifier's held-out set)"
    return src


def folds(src=None, seed=SEED):
    """{global idx: 0 | 1}, stratified (clip frames per (clip, region); workspace per region), seeded"""
    src = src or pool(); Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
    ws_id = names.index("Workspace (envelope)"); strata = {}
    for g in sorted(src):
        kind = "ws" if int(cid[g]) == ws_id else "clip"; nm = names[int(cid[g])]
        strata.setdefault((kind, nm if kind == "clip" else "ws", region(nm, kind, P[g])), []).append(g)
    rng = np.random.default_rng(seed); out = {}; tog = 0
    for k in sorted(strata):
        mem = np.array(strata[k])[rng.permutation(len(strata[k]))]
        for j, g in enumerate(mem): out[int(g)] = (j + tog) % 2
        if len(mem) % 2: tog ^= 1                             # odd strata alternate which fold gets the extra pose
    return out, strata


class SubBench(CB.Bench):
    """a Bench on any subset of the search poses (global indices), fast grid gathered from the source benches' caches
    into a derived per-subset cache (XFIT_DIR/<key>, built once per machine, flock-guarded, shared read-only by mmap)"""
    def __init__(self, gidx, src, parents, tag=""):
        Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
        fit_ids = [names.index(n) for n in CB.FIT]; ws_id = names.index("Workspace (envelope)")
        cl = sorted(int(g) for g in gidx if int(cid[g]) in fit_ids); ws = sorted(int(g) for g in gidx if int(cid[g]) == ws_id)
        assert len(cl) + len(ws) == len(gidx)
        idx = np.array(cl + ws, int)
        self.idx = idx; self.kind = ["clip"] * len(cl) + ["ws"] * len(ws); self.clip = [names[c] for c in cid[idx]]
        self.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in P[idx]]
        self.res = [None] * len(idx); self._skin = {}; self._ex = {}; self._frames = {}; self.tag = tag
        self.key = "xfit-" + CB._key(idx); self.grid = None; self._V = None; self.mode = "exact"
        par = [parents[src[int(g)][0]] for g in idx]
        if os.environ.get("CB_EXACT") != "1" and all(p.grid is not None for p in par):
            self.grid, self._V = _derived(self.key, idx, src, parents); self.mode = "fast"
        elif os.environ.get("CB_EXACT") != "1":
            print(f"crossfit: a source bench has no fast cache -> fold {tag} runs EXACT (slow)", file=sys.stderr)


def _derived(key, idx, src, parents):
    d = os.path.join(XDIR, key); os.makedirs(XDIR, exist_ok=True)
    with open(d + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        if not os.path.exists(os.path.join(d, "meta.json")):
            os.makedirs(d, exist_ok=True); n = parents[src[int(idx[0])][0]].grid.shape[1]
            G = np.lib.format.open_memmap(os.path.join(d, "grid.tmp.npy"), mode="w+", dtype=np.int8, shape=(len(idx), n, n, n))
            for j, g in enumerate(idx):
                pk, li = src[int(g)]; G[j] = parents[pk].grid[li]
            G.flush(); del G; os.replace(os.path.join(d, "grid.tmp.npy"), os.path.join(d, "grid.npy"))
            if all(getattr(parents[src[int(g)][0]], "_V", None) is not None for g in idx):
                Vs = np.stack([np.asarray(parents[src[int(g)][0]]._V[src[int(g)][1]], np.float32) for g in idx])
                np.save(os.path.join(d, "skins.tmp.npy"), Vs); os.replace(os.path.join(d, "skins.tmp.npy"), os.path.join(d, "skins.npy"))
            json.dump(dict(poses=len(idx), idx=[int(x) for x in idx], src={str(k): [list(src[int(k)][0]), src[int(k)][1]] for k in idx},
                           created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())), open(os.path.join(d, "meta.json"), "w"))
        fcntl.flock(lk, fcntl.LOCK_UN)
    grid = np.load(os.path.join(d, "grid.npy"), mmap_mode="r")
    V = np.load(os.path.join(d, "skins.npy"), mmap_mode="r") if os.path.exists(os.path.join(d, "skins.npy")) else None
    return grid, V


def fold_benches():
    src = pool(); fo, _ = folds(src); parents = {s: _fast(*s) for s in SRC}
    Bs = [SubBench([g for g, f in fo.items() if f == k], src, parents, tag=f"fold{k}") for k in (0, 1)]
    if any(B.mode != "fast" for B in Bs) and os.environ.get("CB_EXACT") != "1" and os.environ.get("XFIT_ALLOW_EXACT") != "1":
        raise RuntimeError("a fold is not on the fast grid (link Bench(110,360): eval \"$(python3 tools/bench_cache_farm.py use 110 360)\"); "
                           "XFIT_ALLOW_EXACT=1 runs exact on purpose")
    return Bs


# ---------------------------------------------------------------------------------------------------------------------
# continuity: the verifier's kinematic flood fill (remeasure `conn`), workspace grid, seeded at the rest region
_WS = {}


def _ws_grid():
    if not _WS:
        Z = CB._poses_all(); names = list(Z["NAMES"]); W = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
        POSE = Z["POSE"][W]; _WS.update(W=W, POSE=POSE, HG=Z["HG"][W].astype(float),
                                        key={(float(x[0]), float(x[1]), float(x[2])): i for i, x in enumerate(POSE)},
                                        vals=[sorted(set(POSE[:, k].tolist())) for k in range(3)])
    return _WS


def _edges(step=2.0):
    """the workspace grid's undirected neighbour edges (remeasure.conn's nbrs, axial wrap included) and their 2-deg slerp
    samples, concatenated (built once per process: the poses never change)"""
    G = _ws_grid()
    if "E" in G: return G
    from scipy.spatial.transform import Rotation as Rot, Slerp
    POSE, HG, key, vals = G["POSE"], G["HG"], G["key"], G["vals"]

    def nbrs(i):
        x = [float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])]
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if d == 2 and jj == len(vals[2]) and vals[2][-1] == 180.0: jj = 1
                if d == 2 and jj == -1 and vals[2][0] == -180.0: jj = len(vals[2]) - 2
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                    if t is not None: yield t
        if x[2] in (180.0, -180.0):
            t = key.get((x[0], x[1], -x[2]))
            if t is not None: yield t
    E = sorted({(min(a, b), max(a, b)) for a in range(len(POSE)) for b in nbrs(a) if a != b})
    Qs, off = [], [0]
    for a, b in E:
        angd = np.degrees((Rot.from_matrix(HG[a]).inv() * Rot.from_matrix(HG[b])).magnitude())
        n = max(2, int(math.ceil(angd / step)) + 1)
        Qs.append(Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()); off.append(off[-1] + n)
    G.update(E=np.array(E, int), EQ=np.concatenate(Qs), EOFF=np.array(off, int))
    adj = {}
    for k, (a, b) in enumerate(E): adj.setdefault(a, []).append((b, k)); adj.setdefault(b, []).append((a, k))
    G["ADJ"] = adj
    return G


def flood(kin, step=2.0, jump=10.0, seed_state0=True):
    """connected workspace keys {(plane, elev, axial)} from elevation 0 (state 0 when seed_state0) - remeasure.conn's law
    (2-deg slerp edges, every sample closes, no joint step > jump, knee branch sign constant), every edge between two
    closed nodes evaluated in ONE vectorised kinematics call; edges are direction-symmetric, so the flood = the
    connected component of the seeds, as in conn"""
    G = _edges(step); POSE, HG, E, EQ, OFF, ADJ = G["POSE"], G["HG"], G["E"], G["EQ"], G["EOFF"], G["ADJ"]
    ok, qq, sgn, st = kin(HG)
    live = np.nonzero(ok[E[:, 0]] & ok[E[:, 1]])[0]; good = np.zeros(len(E), bool)
    if len(live):
        sel = np.concatenate([np.arange(OFF[k], OFF[k + 1]) for k in live]); lens = OFF[live + 1] - OFF[live]
        o, q, sg, _ = kin(EQ[sel]); st0 = np.r_[0, np.cumsum(lens)[:-1]]
        allok = np.logical_and.reduceat(o, st0)
        dq = np.abs((np.diff(q, axis=0) + 180) % 360 - 180).max(1); dq = np.r_[dq, 0.0]
        dq[np.cumsum(lens) - 1] = 0.0                          # no step across two edges
        jmp = np.maximum.reduceat(dq, st0) <= jump
        sgc = np.maximum.reduceat(sg, st0) == np.minimum.reduceat(sg, st0)
        good[live] = allok & jmp & sgc
    elev = POSE[:, 1]; cn = np.zeros(len(POSE), bool)
    front = [i for i in range(len(POSE)) if ok[i] and elev[i] == 0 and (not seed_state0 or st[i] == 0)]; cn[front] = True
    while front:
        nxt = []
        for a in front:
            for b, k in ADJ.get(a, ()):
                if ok[b] and not cn[b] and good[k]: cn[b] = True; nxt.append(b)
        front = nxt
    return {(float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])) for i in np.nonzero(cn)[0]}, int(ok.sum()), int(cn.sum())


def _knee_sign(K, s):
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]
    return np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])


def _closed(X3, Q):
    R123 = X3[0]; c = (np.einsum("nij,nij->n", R123, Q) - 1) / 2
    return np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5


# ---------------------------------------------------------------------------------------------------------------------
# plug-ins: fit (shape on a bench), frozen (wear that shape on another bench), checks (verifier knock-outs), audit
FROZEN_ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                "Hneed", "Lneed", "hEx", "_Ex", "_h12")


def _frozen(Cls, M1, wearB):
    """the verifiers' frozen hand-over on an already fitted M1 (same attribute list as
    docs/concepts/verify/skin-normal-3r-pin-knee-polish.py frozen_on / minarc remeasure frozen_B)"""
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Cls):
        def fit(self):
            for a in FROZEN_ATTRS:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    return Frozen(wearB, P2)


class KneePlugin:
    name = "knee"; ID = "skin-normal-3r-pin-knee"

    def __init__(self):
        import knee_polish as KP
        self.KP = KP; self.V = KP.verifier(); self.MK = self.V.MK; self.S = self.MK.S
        self.FREE = dict(KP.FREE); self.FREE["margin"] = (0.3, 5.0, 12.0, "J1-J3 fold margin (S.SING per evaluation; >= 5 = the user's floor)")
        self.DISCRETE = dict(KP.DISCRETE)

    def base(self):
        P = self.KP.base_params(); P.setdefault("margin", 5.0); return P

    def full(self, p):
        P = self.base(); P.update(p); P = self.KP.snap(P); P["margin"] = max(5.0, float(P.get("margin", 5.0))); return P

    def prep(self, P): self.S.SING = max(KIT.FOLD_MARGIN, float(P["margin"]))

    def model_params(self, P): return {k: v for k, v in P.items() if k != "margin"}

    def fit(self, B, P):
        M1 = self.MK.Model(B, self.model_params(P))
        if not M1.kin_ok.any(): return M1, None
        return M1, M1.run()

    def frozen(self, M1, B): return _frozen(self.MK.Model, M1, B)

    def checks(self, M, B): return self.V.extra_checks(M, B)

    def audit(self, M, B): return self.MK.audit(M, B)

    def kin(self, M1):
        D = self.MK.Design(dict(M1.p)); D.m = np.array(M1.D.m, float).copy(); D.m[2] = 0.0; R_tol = float(M1.p["R_tol"])

        def k(Q):                                             # = remeasure kin_H
            q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
            ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol) & _closed(X3, Q)
            qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]])
            return ok, qq, _knee_sign(K, s), np.zeros(len(Q), int)
        return k

    def claim_env(self, P): return {"CB_FOLD_MARGIN": str(max(5.0, float(P.get("margin", 5.0))))}


class MinarcPlugin:
    name = "minarc"; ID = "minarc-stop-knuckle-4r"
    PARAMS_FILE = os.path.join(REPO, "docs", "concepts", "verify", "minarc-kitrule", "params_floorBD5_phys_cap6.json")

    def __init__(self):
        import knee_polish as KP
        self.W = _load("xfit_minarc_wear", os.path.join(REPO, "docs", "concepts", "models", "minarc-stop-knuckle-4r-kitrule-wear.py"))
        self.KR = self.W.KR; self.VER = self.W.VER; self.S = self.KR.S
        self.FREE = dict(KP.FREE)
        self.FREE.update(bk1=(3.0, 15.0, 70.0, "knuckle K -> J1 arc (deg)"), bk2=(3.0, 15.0, 80.0, "knuckle K -> J2 arc (deg)"),
                         a1max=(3.0, 40.0, 100.0, "largest effective J1-J2 arc (stop B)"),
                         smhi=(1.0, 5.0, 20.0, "stretched J2 stop in the kit margin metric (>= 5 = the user's floor)"),
                         smlo=(1.0, 5.0, 20.0, "folded J2 stop in the kit margin metric (>= 5)"))
        self.DISCRETE = dict(KP.DISCRETE)

    def base(self): return dict(self.KR.PARAMS, **json.load(open(self.PARAMS_FILE)))

    def full(self, p):
        P = self.base(); P.update(p)
        for k, lev in self.DISCRETE.items():
            if k in P: P[k] = float(min(lev, key=lambda v: abs(v - float(P[k]))))
        P["sK"] = 1 if float(P["sK"]) >= 0 else -1; P["smhi"] = max(5.0, float(P["smhi"])); P["smlo"] = max(5.0, float(P["smlo"]))
        return P

    def prep(self, P): pass

    def fit(self, B, P):
        M1 = self.KR.KModel(B, dict(P))
        if not M1.kin_ok.any(): return M1, None
        return M1, M1.run()

    def frozen(self, M1, B): return _frozen(self.KR.KModel, M1, B)

    def checks(self, M, B): return self.W.extra_checks_kit(M, B)

    def audit(self, M, B): return self.KR.PK.audit(M, B)

    def kin(self, M1):
        D = self.KR.KDesign(dict(M1.p)); D.m = np.array(M1.D.m, float).copy(); D.m[2] = 0.0; R_tol = float(M1.p["R_tol"])
        return lambda Q: self.VER.kin_B(D, Q, R_tol)

    def claim_env(self, P): return {"CB_FOLD_MARGIN": "5"}


PLUGINS = dict(knee=KneePlugin, minarc=MinarcPlugin)


# ---------------------------------------------------------------------------------------------------------------------
# the cross-fit objective
def _taken(B, i): return B.res[i] is not None and float(np.min(B.res[i])) >= 0


def score_on(pl, M, B, conn):
    """verifier knock-outs, then the continuity drop (workspace poses not in the connected set), then report + audit"""
    ex, bad = pl.checks(M, B); res0 = list(B.res)
    for i in bad: B.res[i] = None
    unconn = 0
    if conn is not None:
        for i in range(len(B.idx)):
            if B.kind[i] == "ws" and _taken(B, i):
                p = B.poses[i]
                if (float(p["plane"]), float(p["elev"]), float(p["axial"])) not in conn: B.res[i] = None; unconn += 1
    rc = B.report(); aud = pl.audit(M, B); oh = aud.get("overhead140") or {}
    lost = int(round(oh["clip"] * (1 - (oh.get("follow") or 0.0)))) if oh.get("clip") else 0
    B.res = res0
    return dict(gap=rc["gap"], gap_near1=aud["gap_near1"], reach=rc["reach"], follow=rc["follow"], inband14=rc["inband14"],
                inband10=rc["inband10"], contact=rc["contact"], near1_poses=aud.get("near1_poses"), near_min=aud.get("near_touch_min_mm"),
                oh_follow=oh.get("follow"), oh_reach=oh.get("reach"), oh_lost=lost, bad=len(bad), unconnected=unconn, n=len(B.idx), mode=B.mode)


def xfit(pl, benches, p):
    P = pl.full(p); pl.prep(P); out = dict(folds=[])
    for a, b in ((0, 1), (1, 0)):
        BA, BB = benches[a], benches[b]; t0 = time.time()
        M1, r1 = pl.fit(BA, P)
        if r1 is None:
            BB.reset(); r = BB.report()
            out["folds"].append(dict(fit=a, oof=dict(gap=r["gap"], gap_near1=r["gap"] + 50.0, oh_lost=0), ins=None, nothing_closes=True)); continue
        conn, nodes, ncn = (None, None, None)
        if CONN: conn, nodes, ncn = flood(pl.kin(M1))
        ins = score_on(pl, M1, BA, conn)
        Mf = pl.frozen(M1, BB); Mf.run(); oof = score_on(pl, Mf, BB, conn)
        out["folds"].append(dict(fit=a, ins=ins, oof=oof, conn=dict(nodes=nodes, connected=ncn), secs=round(time.time() - t0, 1)))
    oo = [f["oof"] for f in out["folds"]]
    out["obj"] = round(float(np.mean([o["gap_near1"] + OH_PEN * o.get("oh_lost", 0) for o in oo])), 3)
    out["oof_near1"] = round(float(np.mean([o["gap_near1"] for o in oo])), 3)
    out["oof_gap"] = round(float(np.mean([o["gap"] for o in oo])), 3)
    ii = [f["ins"] for f in out["folds"] if f.get("ins")]
    out["ins_near1"] = round(float(np.mean([o["gap_near1"] for o in ii])), 3) if len(ii) == 2 else None
    out["drop_near1"] = round(out["oof_near1"] - out["ins_near1"], 3) if out["ins_near1"] is not None else None
    return out


# ---------------------------------------------------------------------------------------------------------------------
# workers + CMA-ES (tools/knee_polish.py's update: clipping + quadratic penalty, periodic angles free)
_W = {}


def _init(plname):
    os.environ.setdefault("OMP_NUM_THREADS", "1"); _W["pl"] = PLUGINS[plname](); _W["B"] = fold_benches()


def _eval(arg):
    tag, p = arg; t0 = time.time()
    try:
        r = xfit(_W["pl"], _W["B"], p)
        return dict(tag=tag, params=p, obj=r["obj"], xfit=r, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-1200:], secs=round(time.time() - t0, 1))


def score_list(plname, outp, items, jobs):
    pool_ = mp.get_context("fork").Pool(jobs, initializer=_init, initargs=(plname,)); t = time.time()
    res = pool_.map(_eval, [(it.get("tag", f"s{i}"), it["params"]) for i, it in enumerate(items)]); pool_.close()
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True); json.dump(res, open(outp, "w"), indent=1, default=float)
    for r in res:
        x = r.get("xfit") or {}
        print(r["tag"], "obj", r["obj"], "oof near1", x.get("oof_near1"), "oof gap", x.get("oof_gap"), "in-fold near1", x.get("ins_near1"),
              "drop", x.get("drop_near1"), r.get("error", ""), r["secs"], "s", flush=True)
    print(f"scored {len(res)} in {time.time() - t:.0f}s")


def cma(a):
    PL = PLUGINS[a.plugin]; free = PL().FREE if not hasattr(PL, "_free") else PL._free
    fixed = json.loads(a.fixed) if a.fixed else {}
    keys = [k for k in free if k not in fixed]; n = len(keys)
    s0 = np.array([free[k][0] for k in keys])
    lo = np.array([free[k][1] if free[k][1] is not None else -np.inf for k in keys])
    hi = np.array([free[k][2] if free[k][2] is not None else np.inf for k in keys])
    st = json.load(open(a.state)) if a.state and os.path.exists(a.state) else None
    lam = a.popsize; mu = lam // 2
    w = np.log(mu + 0.5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1.0 / (w ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5)
    c1 = 2 / ((n + 1.3) ** 2 + mueff); cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
    damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs; chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
    if st:
        c0 = np.array(st["c0"]); mean = np.array(st["mean"]); sigma = st["sigma"]; C = np.array(st["C"]); pc = np.array(st["pc"])
        ps = np.array(st["ps"]); gen = st["gen"]; best = st["best"]; stall = st.get("stall", 0)
    else:
        x0 = json.loads(a.x0); base = PL().base(); c0 = np.array([float(x0.get(k, base.get(k, 5.0 if k == "margin" else 0.0))) for k in keys])
        mean = np.zeros(n); sigma = a.sigma; C = np.eye(n); pc = np.zeros(n); ps = np.zeros(n); gen = 0; best = None; stall = 0
    D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20))

    def to_p(z):
        x = c0 + s0 * z; xc = np.clip(x, lo, hi); pen = float(50.0 * (((x - xc) / s0) ** 2).sum())
        return dict(fixed, **{k: float(round(v, 4)) for k, v in zip(keys, xc)}), pen

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    rows = json.load(open(a.out)) if st and os.path.exists(a.out) else []
    t_start = time.time(); pool_ = mp.get_context("fork").Pool(a.jobs, initializer=_init, initargs=(a.plugin,))
    state_out = a.state_out or (a.out + ".state.json")

    def dump():
        json.dump(rows, open(a.out + ".tmp", "w"), indent=1, default=float); os.replace(a.out + ".tmp", a.out)
        json.dump(dict(c0=c0.tolist(), mean=mean.tolist(), sigma=sigma, C=C.tolist(), pc=pc.tolist(), ps=ps.tolist(), gen=gen, best=best,
                       stall=stall, keys=keys, label=a.label, fixed=fixed, plugin=a.plugin, seed_folds=SEED), open(state_out + ".tmp", "w"), default=float)
        os.replace(state_out + ".tmp", state_out)
    if gen == 0:
        p, _ = to_p(np.zeros(n)); r = pool_.map(_eval, [(f"{a.label}-g0-x0", p)])[0]; r["gen"] = 0; rows.append(r)
        best = dict(obj=r["obj"], params=r["params"], tag=r["tag"]); dump()
        print(f"[{a.label}] x0 {r['obj']:.2f} (in-fold {(r.get('xfit') or {}).get('ins_near1')}) {r.get('error', '')} {r['secs']}s", flush=True)
    gen_secs = 0.0; stop = ""
    while gen < a.max_gen and len(rows) + lam <= a.max_evals and time.time() - t_start + gen_secs * 1.15 < a.budget_s:
        gen += 1; tg = time.time(); rng = np.random.default_rng([a.seed, gen])
        Z = rng.standard_normal((lam, n)); Y = (Z * D) @ Bm.T; X = mean + sigma * Y
        pp = [to_p(X[i]) for i in range(lam)]
        res = pool_.map(_eval, [(f"{a.label}-g{gen}-{i}", pp[i][0]) for i in range(lam)])
        f = np.array([r["obj"] + pp[i][1] for i, r in enumerate(res)])
        for r in res: r["gen"] = gen; r["sigma"] = round(sigma, 4); rows.append(r)
        i0 = int(np.argmin([r["obj"] for r in res]))
        if res[i0]["obj"] < best["obj"] - 0.02: best = dict(obj=res[i0]["obj"], params=res[i0]["params"], tag=res[i0]["tag"]); stall = 0
        else:
            stall += 1
            if res[i0]["obj"] < best["obj"]: best = dict(obj=res[i0]["obj"], params=res[i0]["params"], tag=res[i0]["tag"])
        idx = np.argsort(f)[:mu]; old = mean.copy(); mean = (w[:, None] * X[idx]).sum(0)
        invsqrtC = Bm @ np.diag(1 / D) @ Bm.T
        ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * invsqrtC @ (mean - old) / sigma
        hsig = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * gen)) / chiN < 1.4 + 2 / (n + 1)
        pc = (1 - cc) * pc + hsig * math.sqrt(cc * (2 - cc) * mueff) * (mean - old) / sigma
        art = (X[idx] - old) / sigma
        C = (1 - c1 - cmu) * C + c1 * (np.outer(pc, pc) + (1 - hsig) * cc * (2 - cc) * C) + cmu * (art.T * w) @ art
        sigma *= math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1))
        C = np.triu(C) + np.triu(C, 1).T; D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20))
        gen_secs = time.time() - tg; dump()
        print(f"[{a.label}] gen {gen} best-in-gen {min(r['obj'] for r in res):.2f} best {best['obj']:.2f} sigma {sigma:.3f} stall {stall} "
              f"{gen_secs:.0f}s elapsed {time.time() - t_start:.0f}s evals {len(rows)}", flush=True)
        if sigma * D.max() < 0.02: stop = "sigma collapsed"; break
        if stall >= a.patience: stop = f"no gain > 0.02 in {a.patience} generations"; break
    stop = stop or ("max evals" if len(rows) + lam > a.max_evals else "budget / max gen")
    pool_.close(); dump()
    print(json.dumps(dict(label=a.label, gen=gen, evals=len(rows), best=best, stop=stop), default=float), flush=True)


def best_rows(files, k=8):
    rows = []
    for f in files:
        for r in json.load(open(f)):
            if not r.get("error"): rows.append(r)
    rows.sort(key=lambda r: r["obj"])
    for r in rows[:k]:
        x = r["xfit"]; print(r["tag"], "obj", r["obj"], "oof gap", x["oof_gap"], "in-fold near1", x["ins_near1"], "drop", x["drop_near1"],
                             json.dumps({kk: (round(v, 4) if isinstance(v, float) else v) for kk, v in r["params"].items()}))
    return rows[:k]


SEAT_KEYS = ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "lE", "lc", "phiE", "phib", "ang_min", "stk")


def farm(a):
    refs = json.load(open(os.path.join(REPO, "docs", "research", "crossfit", "refs.json")))
    label = a.label or f"xf-{a.plugin}-{time.strftime('%H%M')}"; d = "docs/research/crossfit"
    use = 'eval "$(python3 tools/bench_cache_farm.py use 110 360)" && '; env = dict(OMP_NUM_THREADS="1", IGL_NUM_THREADS="1")
    jobs = []
    for k, st in enumerate(a.starts.split(",")):
        if st == "base": x0 = {}
        elif a.plugin == "minarc": x0 = {kk: refs[st][kk] for kk in SEAT_KEYS if kk in refs[st]}
        else: x0 = dict(refs[st])
        lab = f"{label}-{st}"; out = f"{d}/cma_{lab}"
        cmd = (use + f"python3 tools/crossfit_polish.py cma {a.plugin} --x0 '{json.dumps(x0)}' --label {lab} --out {out}.json --sigma {a.sigma} "
               f"--popsize {a.popsize} --jobs 8 --max-evals {a.max_evals} --budget-s {a.budget_s} --patience {a.patience} --seed {k + 11} "
               f"> {out}.log 2>&1; tail -3 {out}.log")
        jobs.append(dict(tag=f"xfit-{lab}", cmd=cmd, out=[f"{out}*"], env=env, timeout=int(a.budget_s) + 600))
    jp = os.path.join(REPO, d, f"jobs_{label}.json"); os.makedirs(os.path.dirname(jp), exist_ok=True)
    json.dump(jobs, open(jp, "w"), indent=1); print("jobs:", os.path.relpath(jp, REPO), len(jobs), "x 8 processes")
    if not a.dry_run:
        import subprocess
        subprocess.run([sys.executable, os.path.join(REPO, "tools", "cloud_run.py"), "batch", jp], check=False)
        print("next: python3 tools/crossfit_polish.py best " + " ".join(f"{d}/cma_{label}-{st}.json" for st in a.starts.split(",")))


def main():
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    if a[0] == "folds":
        src = pool(); fo, strata = folds(src)
        print(f"pool {len(src)} poses (sources {SRC}), seed {SEED}: fold0 {sum(1 for v in fo.values() if v == 0)}, fold1 {sum(1 for v in fo.values() if v == 1)}")
        for k in sorted(strata):
            m = strata[k]; print(" ", k, len(m), "->", [sum(1 for g in m if fo[g] == f) for f in (0, 1)])
    elif a[0] == "score":
        jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
        score_list(a[1], a[2], json.loads(a[3]) if not os.path.exists(a[3]) else json.load(open(a[3])), jobs)
    elif a[0] == "best":
        best_rows(a[1:])
    elif a[0] == "cma":
        import argparse
        ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("plugin", choices=sorted(PLUGINS))
        ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
        ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
        ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.4)
        ap.add_argument("--popsize", type=int, default=12); ap.add_argument("--jobs", type=int, default=6)
        ap.add_argument("--budget-s", type=float, default=2400); ap.add_argument("--max-gen", type=int, default=400)
        ap.add_argument("--max-evals", type=int, default=700); ap.add_argument("--patience", type=int, default=12)
        ap.add_argument("--seed", type=int, default=1)
        cma(ap.parse_args(a))
    elif a[0] == "farm":
        import argparse
        ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("plugin", choices=sorted(PLUGINS))
        ap.add_argument("--starts", default="base,F2,F7"); ap.add_argument("--label", default="")
        ap.add_argument("--budget-s", type=float, default=1800); ap.add_argument("--max-evals", type=int, default=700)
        ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--sigma", type=float, default=0.4)
        ap.add_argument("--patience", type=int, default=10); ap.add_argument("--dry-run", action="store_true")
        farm(ap.parse_args(a))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

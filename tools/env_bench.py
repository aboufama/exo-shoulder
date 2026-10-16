#!/usr/bin/env python3
"""ENVELOPE SEARCH BENCH ('env'): a fresh stratified random sample of the CONTINUOUS workspace envelope, the search bench of
final polishes (CLAUDE.md "The fold margin is read in ONE metric ...": the held-out drop of every polish so far is the
search benches' axially skewed workspace sample - Bench linspace over the grid order, |axial| >= 150 deg 6 % vs 11 % held
out - so final polishes search on a representative envelope sample and claim on the held-out set).

The envelope = the one the workspace grid samples (pipeline/conformal/gpu_client/pack_envelope.py --functional): plane
-90..150, elevation 0..170, humeral rotation r = axial + plane -90..90, inside rt_common.plausible (elevation ceiling per
plane) and the functional rotation limits. The grid is that envelope on a 15-deg lattice (1432 poses).

Draw (seeded, deterministic): every grid pose owns its 15-deg cell (plane / elevation / r +- 7.5, clipped to the box).
Cells are allocated to strata (region x axial band of the cell's grid pose; regions = tools/crossfit_polish.region) in
proportion to the grid (largest remainder), cells are picked at random inside each stratum, and one pose is drawn
uniformly inside each picked cell (rejection on the envelope law). A draw is REJECTED when it lies within 2 deg of any
held-out pose (the verifier's 1154: every fit-clip frame and workspace pose outside Bench(110,360) and Bench(60,160)) -
in each coordinate (plane, elevation, axial, axial wrapped) OR in humerus orientation (geodesic, catches the low-elevation
plane / axial degeneracy) - or within 2 deg of a pose of another draw (env and envsel stay disjoint). The lead's ruling:
fresh draws near held-out poses are fine (the target is the envelope distribution); reusing or near-duplicating them
(< 2 deg) is not. Each fresh pose gets the rig's humerus / scapula frames exactly as the grid does (design_search Ry Rx Ry
+ scapula rhythm), elbow 90, forearm neutral.

Benches: the clip frames of Bench(110,360) (never Wave / Walking) + the fresh workspace poses.
  env    : seed 1, 420 workspace poses - the search bench (fit AND score: the shape over-fit test of the cross-fit study
           measured in-fold = out-of-fold, so the search scores in-sample on a representative sample)
  envsel : seed 2, 360 workspace poses - the PICK-SELECTION bench (fit env -> wear envsel frozen): CMA selects on the
           noise of a fixed pool, so picks are ranked on an independent draw

Install (every process that scores on these benches): `import env_bench as EB; EB.install()` appends the fresh poses to
concept_bench._poses_all() under the clip name "Envelope sample (fresh)" (not a fit clip, not the grid: every grid /
held-out / clip computation is unchanged) and EB.bench("env") returns the Bench (fast grid if its cache is linked).

    python3 tools/env_bench.py make                      draw both benches -> docs/research/minarc_final_polish/env_poses.npz + table
    python3 tools/env_bench.py table                     the distribution table (grid / held out / Bench(110,360) / env / envsel)
    python3 tools/env_bench.py jobs <env|envsel> [--chunks 8 --procs 2]   farm part jobs (cache on the farm volume)
    python3 tools/env_bench.py part <name> --j0 a --j1 b --procs p | assemble <name> | use <name> | key <name>
"""
import json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

OUTD = os.path.join(REPO, "docs", "research", "minarc_final_polish")
NPZ = os.path.join(OUTD, "env_poses.npz")
NAME = "Envelope sample (fresh)"
DRAWS = {"env": dict(seed=1, n_ws=420), "envsel": dict(seed=2, n_ws=360)}
VOL = "/runpod-volume/exo-farm/shared/bench"
INC = ["tools/concept_bench.py", "tools/env_bench.py", "pipeline/avg", "data/raw/split.json", "pipeline/conformal/band_poses_wsf.b64",
       "docs/research/minarc_final_polish/env_poses.npz"]
EXCL = 2.0                                                   # deg: no fresh pose this close to a held-out pose (or another draw's)
_Z0 = CB._poses_all                                          # the original archive reader


# ---------------------------------------------------------------------------------------------------------------------
# the envelope law (pack_envelope.py --functional + rt_common.plausible), continuous
def plausible(pl, el):
    pl, el = np.asarray(pl, float), np.asarray(el, float)
    emax = np.where(pl <= -30, 60.0, np.where(pl < 0, 60 + (pl + 30) * 110 / 30, np.where(pl <= 120, 170.0, 170 - 1.5 * (pl - 120))))
    return el <= emax


def functional(pl, el, r):
    lo = np.where(pl < -30, -20.0, np.where(pl > 120, -30.0, np.where(el > 100, -45.0, -65.0)))
    hi = np.where((pl >= -30) & (pl <= 120) & (el > 100), 30.0, 90.0)
    return (r >= lo) & (r <= hi)


def inside(pl, el, r):
    pl, el, r = (np.asarray(x, float) for x in (pl, el, r))
    return (pl >= -90) & (pl <= 150) & (el >= 0) & (el <= 170) & (r >= -90) & (r <= 90) & plausible(pl, el) & functional(pl, el, r)


def _ds():
    if "D" not in _DS:
        c = os.getcwd(); os.chdir(os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, os.getcwd())
        try:
            import design_search as D
        finally: os.chdir(c)
        _DS["D"] = D
    return _DS["D"]


_DS = {}


def frames_of(pl, el, ax):
    """(H thorax humerus, HG scapula-frame humerus, RS scapula) of a pose - pack_envelope.py's construction"""
    D = _ds(); H = D.Ry(pl * D.D2R) @ D.Rx(-el * D.D2R) @ D.Ry(ax * D.D2R); Rs = D.scapula(el); return H, Rs.T @ H, Rs


def region(pose):
    el, pl = float(pose[1]), float(pose[0])
    if el >= 140: return "overhead"
    if pl >= 100 and el >= 40: return "across"
    if pl < -30 and el > 20: return "behind"
    return f"el{int(min(el, 139.9) // 35)}"


def axband(ax):
    a = abs(float(ax))
    return ">=150" if a >= 150 else f"{int(a // 45) * 45}-{int(a // 45) * 45 + 45}"


def sband(ax):
    """signed axial band (deg): edges -150 -90 -45 0 45 90 150 (a lattice value on an edge goes to the outer band)"""
    a = float(ax)
    for lo, nm in ((150, "+150..180"), (90, "+90..150"), (45, "+45..90"), (0, "+0..45")):
        if a >= lo: return nm
    for hi, nm in ((-150, "-180..-150"), (-90, "-150..-90"), (-45, "-90..-45")):
        if a <= hi: return nm
    return "-45..0"


def stratum(p):
    """elevation band x plane band x signed axial band, with the table's edges (a lattice value on an edge goes up)"""
    pl, el, ax = float(p[0]), float(p[1]), float(p[2])
    eb = 0 if el < 45 else 1 if el < 90 else 2 if el < 140 else 3
    pb = 0 if pl < 0 else 1 if pl < 60 else 2 if pl < 100 else 3
    return (eb, pb, sband(ax))


def wrap(a): return (np.asarray(a, float) + 180.0) % 360.0 - 180.0


# ---------------------------------------------------------------------------------------------------------------------
# held-out set (the verifier's: docs/concepts/verify/skin-normal-3r-pin-knee-polish.py held_bench, rebuilt the same way)
def held_idx():
    Z = _Z0(); names = list(Z["NAMES"]); cid = Z["CID"]
    used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
    fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
    cl = [i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in used]
    ws = [i for i in np.nonzero(cid == ws_id)[0] if i not in used]
    return np.array(cl + ws, int), np.array(ws, int)


def _hum_thorax(Z, idx):
    """thorax-frame humerus of archive poses = RS @ HG"""
    return np.einsum("nij,njk->nik", Z["RS"][idx].astype(float), Z["HG"][idx].astype(float))


def _geo(Ha, Hb):
    """(na, nb) geodesic angle (deg) between rotation sets"""
    tr = np.einsum("aij,bij->ab", Ha, Hb)
    return np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1)))


def draw(seed, n_ws, avoid=None):
    """one stratified fresh draw; avoid = extra (n, 3) poses + (n, 3, 3) thorax humeri to keep >= EXCL away from"""
    Z = _Z0(); names = list(Z["NAMES"]); W = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    G = Z["POSE"][W, :3].astype(float); Rg = G[:, 2] + G[:, 0]
    hidx, _ = held_idx(); HP = Z["POSE"][hidx, :3].astype(float); HH = _hum_thorax(Z, hidx)
    if avoid is not None: HP = np.r_[HP, avoid[0]]; HH = np.r_[HH, avoid[1]]
    # strata on the DRAWN pose's own values (elevation band x plane band x signed axial band), quotas = the grid's shares: the held-out set is
    # lattice-weighted (its boundary rows - e.g. |axial| 150-180 at the plane / rotation limits - carry full weight), so a
    # plain uniform draw in the continuous envelope would under-sample them again (measured: 6.7 % |axial| >= 150 vs 9.4 %)
    strata = {}
    for k, p in enumerate(G): strata.setdefault(stratum(p), []).append(k)
    keys = sorted(strata); quota = np.array([len(strata[k]) for k in keys], float) * n_ws / len(G)
    alloc = np.floor(quota).astype(int); rem = n_ws - alloc.sum()
    alloc[np.argsort(-(quota - alloc), kind="stable")[:rem]] += 1
    rng = np.random.default_rng([20261016, seed]); out = []; rej = dict(envelope=0, other_stratum=0, fallback_cell=0, held_coord=0, held_geo=0, self_dup=0)
    for k, n in zip(keys, alloc):
        got = 0; tries = 0
        while got < n:
            tries += 1; assert tries < 200000, f"stratum {k}: {got}/{n}"
            c = int(rng.choice(strata[k])); pl0, el0, r0 = G[c, 0], G[c, 1], Rg[c]
            pl = rng.uniform(max(-90, pl0 - 7.5), min(150, pl0 + 7.5)); el = rng.uniform(max(0, el0 - 7.5), min(170, el0 + 7.5))
            r = rng.uniform(max(-90, r0 - 7.5), min(90, r0 + 7.5)); ax = r - pl
            if not inside(pl, el, r): rej["envelope"] += 1; continue
            if stratum((pl, el, ax)) != k:
                if tries < 3000: rej["other_stratum"] += 1; continue
                rej["fallback_cell"] += 1                  # a lattice-edge stratum with ~no continuous volume: the cell's draw counts
            d = np.abs(np.c_[HP[:, 0] - pl, HP[:, 1] - el, wrap(HP[:, 2] - ax)]).max(1)
            if (d < EXCL).any(): rej["held_coord"] += 1; continue
            if out and (np.abs(np.c_[[o[0] - pl for o in out], [o[1] - el for o in out], wrap([o[2] - ax for o in out])]).max(1) < EXCL).any():
                rej["self_dup"] += 1; continue
            H, HGm, Rs = frames_of(pl, el, ax)
            if (_geo(H[None], HH)[0] < EXCL).any(): rej["held_geo"] += 1; continue
            out.append((pl, el, ax, c, H, HGm, Rs, k)); got += 1
    P = np.array([[o[0], o[1], o[2], 90.0, 0.0] for o in out]); cell = np.array([o[3] for o in out])
    return P, np.array([o[4] for o in out]), np.array([o[5] for o in out]), np.array([o[6] for o in out]), cell, rej


def make():
    os.makedirs(OUTD, exist_ok=True); D = {}; t = time.time(); avoid = None; meta = {}
    for name in ("env", "envsel"):
        cfg = DRAWS[name]; P, H, HG, RS, cell, rej = draw(cfg["seed"], cfg["n_ws"], avoid)
        D[name] = (P, H, HG, RS, cell); meta[name] = dict(cfg, rejected=rej, n=len(P))
        avoid = (np.r_[avoid[0], P[:, :3]], np.r_[avoid[1], H]) if avoid is not None else (P[:, :3], H)
    # HG rebuild check of the construction on the grid (must be 0)
    Z = _Z0(); names = list(Z["NAMES"]); W = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    err = max(float(np.abs(frames_of(*Z["POSE"][g, :3].astype(float))[1] - Z["HG"][g]).max()) for g in W[::37])
    np.savez_compressed(NPZ, **{f"{n}_{k}": v for n, (P, H, HG, RS, cell) in D.items() for k, v in (("POSE", P), ("HG", HG), ("RS", RS), ("cell", cell))},
                        meta=json.dumps(dict(meta, hg_rebuild_err=err, excl_deg=EXCL, created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))))
    print("wrote", os.path.relpath(NPZ, REPO), {n: len(v[0]) for n, v in D.items()}, f"HG rebuild err {err:.2e}", f"{time.time() - t:.0f}s")
    print(json.dumps(meta))


# ---------------------------------------------------------------------------------------------------------------------
# install: the fresh poses appended to the pose archive, + the Bench objects
_ZX = {}


def _load_npz():
    if "npz" not in _ZX: _ZX["npz"] = dict(np.load(NPZ, allow_pickle=False))
    return _ZX["npz"]


def install():
    """patch concept_bench._poses_all -> the archive + both fresh draws (new clip name; idempotent); returns {name: global idx}"""
    if "Z" in _ZX: return _ZX["gidx"]
    Z = dict(_Z0()); E = _load_npz(); names = [str(x) for x in Z["NAMES"]]; cid = len(names); n0 = len(Z["HG"]); gidx = {}
    for name in ("env", "envsel"):
        P = E[f"{name}_POSE"]; n = len(P); gidx[name] = np.arange(len(Z["HG"]), len(Z["HG"]) + n)
        Z["HG"] = np.concatenate([Z["HG"], E[f"{name}_HG"].astype(Z["HG"].dtype)]); Z["RS"] = np.concatenate([Z["RS"], E[f"{name}_RS"].astype(Z["RS"].dtype)])
        Z["EL"] = np.concatenate([Z["EL"], P[:, 1].astype(Z["EL"].dtype)]); Z["CID"] = np.concatenate([Z["CID"], np.full(n, cid, Z["CID"].dtype)])
        Z["FI"] = np.concatenate([Z["FI"], np.arange(n, dtype=Z["FI"].dtype)]); Z["WT"] = np.concatenate([Z["WT"], np.zeros(n, Z["WT"].dtype)])
        Z["POSE"] = np.concatenate([Z["POSE"], P.astype(Z["POSE"].dtype)])
    Z["NAMES"] = np.array(names + [NAME]); _ZX.update(Z=Z, gidx=gidx, n0=n0)
    CB._poses_all = lambda: _ZX["Z"]
    return gidx


def key_of(name):
    gidx = install(); idx = np.r_[CB._select(110, 360)[0][:110], gidx[name]]
    return "env-" + CB._key(idx) + "-" + name, idx


def bench(name, exact=None):
    """the Bench: Bench(110,360)'s 110 clip frames + the draw's workspace poses (kind 'ws'); fast grid when the cache exists
    (.cache/concept_bench/<key>) unless CB_EXACT=1 / exact=True"""
    key, idx = key_of(name); Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
    old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"
    try: B = CB.Bench(20, 20)
    finally:
        if old is None: os.environ.pop("CB_EXACT")
        else: os.environ["CB_EXACT"] = old
    nc = int(np.isin(cid[idx], [names.index(n) for n in CB.FIT]).sum()); assert nc == 110
    B.idx = idx; B.kind = ["clip"] * nc + ["ws"] * (len(idx) - nc); B.clip = [str(names[c]) for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in Z["POSE"][idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = key
    d = os.path.join(CB.CACHE, key)
    want_exact = exact if exact is not None else os.environ.get("CB_EXACT") == "1"
    if not want_exact and os.path.exists(os.path.join(d, "meta.json")):
        B.meta = json.load(open(os.path.join(d, "meta.json"))); B.grid = np.load(os.path.join(d, "grid.npy"), mmap_mode="r")
        B._V = np.load(os.path.join(d, "skins.npy"), mmap_mode="r") if os.path.exists(os.path.join(d, "skins.npy")) else None; B.mode = "fast"
    # the held-out split stays held out: no bench pose is a held-out pose
    hidx, _ = held_idx(); assert not (set(idx.tolist()) & set(hidx.tolist()))
    held_clips = {names.index(x) for x in ("Wave", "Walking arm swing")}; assert not any(int(c) in held_clips for c in cid[idx])
    return B


# ---------------------------------------------------------------------------------------------------------------------
# the distribution table
def table(out_json=None):
    install(); Z = CB._poses_all(); names = list(Z["NAMES"]); W = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    _, hws = held_idx(); b110 = [g for g in CB._select(110, 360)[0] if g in set(W.tolist())]
    b60 = [g for g in CB._select(60, 160)[0] if g in set(W.tolist())]
    sets = dict(grid=W, held_ws=hws, b110_ws=np.array(b110), b60_ws=np.array(b60), env_ws=key_of("env")[1][110:], envsel_ws=key_of("envsel")[1][110:])
    rows = {}
    for nm, ii in sets.items():
        P = Z["POSE"][ii].astype(float); ax = np.abs(P[:, 2]); el = P[:, 1]; pl = P[:, 0]; reg = np.array([region(p) for p in P])
        r = dict(n=len(ii), ax_ge150=np.mean(ax >= 150), ax_0_45=np.mean(ax < 45), ax_45_90=np.mean((ax >= 45) & (ax < 90)),
                 ax_90_150=np.mean((ax >= 90) & (ax < 150)), ax_m90_m45=np.mean((P[:, 2] >= -90) & (P[:, 2] < -45)),
                 overhead=np.mean(reg == "overhead"), across=np.mean(reg == "across"), behind=np.mean(reg == "behind"),
                 el_lt45=np.mean(el < 45), el_45_90=np.mean((el >= 45) & (el < 90)), el_90_140=np.mean((el >= 90) & (el < 140)),
                 pl_lt0=np.mean(pl < 0), pl_0_60=np.mean((pl >= 0) & (pl < 60)), pl_60_100=np.mean((pl >= 60) & (pl < 100)), pl_ge100=np.mean(pl >= 100),
                 mean_axial=float(P[:, 2].mean()), mean_elev=float(el.mean()), mean_plane=float(pl.mean()))
        rows[nm] = {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in r.items()}
    # proximity to the held-out set (min over the fresh poses): coordinates and humerus orientation
    hidx, _ = held_idx(); HP = Z["POSE"][hidx, :3].astype(float); HH = _hum_thorax(Z, hidx)
    for nm in ("env", "envsel"):
        ii = key_of(nm)[1][110:]; P = Z["POSE"][ii, :3].astype(float); Hn = _hum_thorax(Z, ii)
        dc = np.array([np.abs(np.c_[HP[:, 0] - p[0], HP[:, 1] - p[1], wrap(HP[:, 2] - p[2])]).max(1).min() for p in P])
        dg = _geo(Hn, HH).min(1)
        rows[nm + "_ws"]["min_cheb_to_held_deg"] = round(float(dc.min()), 3); rows[nm + "_ws"]["min_geo_to_held_deg"] = round(float(dg.min()), 3)
        rows[nm + "_ws"]["median_geo_to_held_deg"] = round(float(np.median(dg)), 2)
    cols = ["n", "ax_ge150", "ax_0_45", "ax_45_90", "ax_90_150", "ax_m90_m45", "overhead", "across", "behind", "el_lt45", "el_45_90", "el_90_140",
            "pl_lt0", "pl_0_60", "pl_60_100", "pl_ge100", "mean_axial"]
    print("| set | " + " | ".join(cols) + " |"); print("|---" * (len(cols) + 1) + "|")
    for nm, r in rows.items(): print(f"| {nm} | " + " | ".join(str(r[c]) for c in cols) + " |")
    for nm in ("env_ws", "envsel_ws"): print(nm, {k: rows[nm][k] for k in ("min_cheb_to_held_deg", "min_geo_to_held_deg", "median_geo_to_held_deg")})
    if out_json: json.dump(rows, open(out_json, "w"), indent=1)
    return rows


# ---------------------------------------------------------------------------------------------------------------------
# farm cache: same grids as tools/concept_bench.py --build (same _grid_pose), parts on the volume, assembled, linked
def part(name, j0, j1, procs):
    from multiprocessing import Pool
    B = bench(name, exact=True); key = B.key; d = os.path.join(VOL, key); os.makedirs(d, exist_ok=True)
    n = int(round(2 * CB.HALF / CB.H_GRID)) + 1; j1 = min(j1, len(B.poses)); tmp = f"/tmp/ebf_{key}_{j0}.npy"
    np.lib.format.open_memmap(tmp, mode="w+", dtype=np.int8, shape=(len(B.poses), n, n, n)).flush()
    t = time.time(); Vs = {}; fr = []
    with Pool(procs) as pool:
        for j, frac, V in pool.imap_unordered(CB._grid_pose, [(B.poses[j], tmp, j, n) for j in range(j0, j1)]):
            Vs[j] = V; fr.append(frac)
    G = np.load(tmp, mmap_mode="r")[j0:j1]
    np.save(os.path.join(d, f"part_{j0:04d}.tmp.npy"), np.ascontiguousarray(G)); os.replace(os.path.join(d, f"part_{j0:04d}.tmp.npy"), os.path.join(d, f"part_{j0:04d}.npy"))
    np.save(os.path.join(d, f"skins_{j0:04d}.npy"), np.stack([Vs[j] for j in range(j0, j1)]))
    json.dump(dict(j0=j0, j1=j1, frac=float(np.mean(fr)), secs=round(time.time() - t, 1)), open(os.path.join(d, f"part_{j0:04d}.json"), "w"))
    os.remove(tmp); print("part", key, j0, j1, round(time.time() - t, 1), "s", flush=True)


def assemble(name):
    key, idx = key_of(name); N = len(idx); d = os.path.join(VOL, key); n = int(round(2 * CB.HALF / CB.H_GRID)) + 1
    info = [json.load(open(os.path.join(d, f))) for f in sorted(os.listdir(d)) if f.startswith("part_") and f.endswith(".json")]
    cov = sorted((i["j0"], i["j1"]) for i in info); have = np.zeros(N, bool)
    for a, b in cov: have[a:b] = True
    if not have.all(): sys.exit(f"missing poses: {np.nonzero(~have)[0][:20]}")
    g = np.lib.format.open_memmap(os.path.join(d, "grid.tmp.npy"), mode="w+", dtype=np.int8, shape=(N, n, n, n)); S = None
    for a, b in cov:
        g[a:b] = np.load(os.path.join(d, f"part_{a:04d}.npy")); s = np.load(os.path.join(d, f"skins_{a:04d}.npy"))
        if S is None: S = np.zeros((N,) + s.shape[1:], np.float32)
        S[a:b] = s
    g.flush(); del g
    np.save(os.path.join(d, "skins.tmp.npy"), S); os.replace(os.path.join(d, "skins.tmp.npy"), os.path.join(d, "skins.npy"))
    os.replace(os.path.join(d, "grid.tmp.npy"), os.path.join(d, "grid.npy"))
    meta = dict(bench=name, poses=N, h=CB.H_GRID, half=CB.HALF, q=CB.Q, exact_share=float(np.mean([i["frac"] for i in info])),
                secs=round(sum(i["secs"] for i in info), 1), created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), built=f"farm, tools/env_bench.py ({len(info)} parts)")
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1); print("assembled", d, meta, flush=True)


def validate(name, n_poses=12):
    B = bench(name); assert B.grid is not None, "no cache"
    rng = np.random.default_rng(1); errs = []; sg = []
    for i in rng.choice(len(B.poses), min(n_poses, len(B.poses)), replace=False):
        V = np.asarray(B._V[i], float); near = V[np.linalg.norm(V, axis=1) < 240]
        P = near[rng.choice(len(near), 1500)] + rng.normal(0, 1, (1500, 3)) * rng.uniform(0, 18, (1500, 1))
        a = B.dist(i, P); b = B._exact(i, P); sel = np.abs(b) <= 20; errs.append(np.abs(a - b)[sel]); far = np.abs(b) > 1; sg.append((np.sign(a) == np.sign(b))[far])
    e = np.concatenate(errs); s = np.concatenate(sg)
    out = dict(bench=name, key=B.key, points=int(len(e)), max_err_0_20mm=round(float(e.max()), 3), p99=round(float(np.percentile(e, 99)), 3),
               mean=round(float(e.mean()), 4), sign_agree_beyond_1mm=round(float(s.mean()), 5))
    print(json.dumps(out)); return out


def use(name):
    key, _ = key_of(name); src = os.path.join(VOL, key); loc = f"/tmp/bench-{key}"
    return (f'( flock 7; [ -f {loc}/meta.json ] || {{ rm -rf {loc}.tmp && mkdir -p {loc}.tmp && cp {src}/grid.npy {src}/skins.npy {loc}.tmp/ '
            f'&& cp {src}/meta.json {loc}.tmp/ && rm -rf {loc} && mv {loc}.tmp {loc}; }} ) 7>/tmp/bench-{key}.lock; '
            f'mkdir -p .cache/concept_bench && ln -sfn {loc} .cache/concept_bench/{key}')


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    if not a: raise SystemExit(__doc__)
    if a[0] == "make": make(); table(os.path.join(OUTD, "env_table.json"))
    elif a[0] == "table": table(os.path.join(OUTD, "env_table.json") if "--save" in a else None)
    elif a[0] == "part": part(a[1], opt("--j0", 0), opt("--j1", 10 ** 6), opt("--procs", 2))
    elif a[0] == "assemble": assemble(a[1])
    elif a[0] == "validate": validate(a[1])
    elif a[0] == "use": print(use(a[1]))
    elif a[0] == "key": print(key_of(a[1])[0])
    elif a[0] == "jobs":
        name = a[1]; key, idx = key_of(name); N = len(idx); ch = opt("--chunks", 8); procs = opt("--procs", 2); step = -(-N // ch)
        if "--assemble" in a:
            jobs = [dict(cmd=f"python3 tools/env_bench.py assemble {name} && {use(name)} && python3 tools/env_bench.py validate {name}", tag=f"ebf-asm-{name}", include=INC, base=False)]
        else:
            jobs = [dict(cmd=f"python3 tools/env_bench.py part {name} --j0 {j0} --j1 {min(N, j0 + step)} --procs {procs}", tag=f"ebf-{name}-{j0:04d}",
                         include=INC, base=False, env=dict(IGL_NUM_THREADS="1")) for j0 in range(0, N, step)]
        print(json.dumps(jobs, indent=1))
    else: raise SystemExit(__doc__)

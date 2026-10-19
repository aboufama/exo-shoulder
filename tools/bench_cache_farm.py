#!/usr/bin/env python3
"""Build a concept_bench signed-distance cache for a large bench (e.g. Bench(110,360)) on the CPU farm, in parallel
chunks of poses, into a persistent directory on the farm's network volume - and use it from farm jobs.

    # 1. parts: one farm job per chunk of poses (each runs `--procs` processes), written to the volume
    python3 tools/bench_cache_farm.py jobs 110 360 --chunks 10 --procs 2 > jobs.json
    RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch jobs.json --no-base
    # 2. assemble the parts into grid.npy / skins.npy / meta.json (one job), then validate against the exact path
    #    (the commands are printed by `jobs ... --assemble` / `--validate`)
    # 3. in a farm job: eval "$(python3 tools/bench_cache_farm.py use 110 360)"  -> copies the cache once per worker to
    #    /tmp (flock-guarded) and links it at .cache/concept_bench/<key> for tools/concept_bench.py (fast path)

The grids are the same as `tools/concept_bench.py --build` (same _grid_pose code, same key); only the work split and
the storage differ. Volume dir: /runpod-volume/exo-farm/shared/bench/<key>/.
"""
import json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
VOL = "/runpod-volume/exo-farm/shared/bench"
INC = ["tools/concept_bench.py", "tools/bench_cache_farm.py", "pipeline/avg", "data/raw/split.json", "pipeline/conformal/band_poses_wsf.b64"]


def key_of(nc, nw):
    import concept_bench as CB
    idx, *_ = CB._select(nc, nw); return CB._key(idx), len(idx)


def part(nc, nw, j0, j1, procs):
    import concept_bench as CB
    from multiprocessing import Pool
    B = CB.Bench(nc, nw); B.grid = None; key = B.key; d = os.path.join(VOL, key); os.makedirs(d, exist_ok=True)
    n = int(round(2 * CB.HALF / CB.H_GRID)) + 1; j1 = min(j1, len(B.poses))
    tmp = f"/tmp/bcf_{key}_{j0}.npy"
    np.lib.format.open_memmap(tmp, mode="w+", dtype=np.int8, shape=(len(B.poses), n, n, n)).flush()
    t = time.time(); Vs = {}; fr = []
    with Pool(procs) as pool:
        for j, frac, V in pool.imap_unordered(CB._grid_pose, [(B.poses[j], tmp, j, n) for j in range(j0, j1)]):
            Vs[j] = V; fr.append(frac)
    G = np.load(tmp, mmap_mode="r")[j0:j1]
    np.save(os.path.join(d, f"part_{j0:04d}.tmp.npy"), np.ascontiguousarray(G))
    os.replace(os.path.join(d, f"part_{j0:04d}.tmp.npy"), os.path.join(d, f"part_{j0:04d}.npy"))
    np.save(os.path.join(d, f"skins_{j0:04d}.npy"), np.stack([Vs[j] for j in range(j0, j1)]))
    json.dump(dict(j0=j0, j1=j1, frac=float(np.mean(fr)), secs=round(time.time() - t, 1)), open(os.path.join(d, f"part_{j0:04d}.json"), "w"))
    os.remove(tmp); print("part", key, j0, j1, round(time.time() - t, 1), "s", flush=True)


def assemble(nc, nw):
    import concept_bench as CB
    key, N = key_of(nc, nw); d = os.path.join(VOL, key); n = int(round(2 * CB.HALF / CB.H_GRID)) + 1
    parts = sorted(f for f in os.listdir(d) if f.startswith("part_") and f.endswith(".json"))
    info = [json.load(open(os.path.join(d, f))) for f in parts]; cov = sorted((i["j0"], i["j1"]) for i in info)
    have = np.zeros(N, bool)
    for a, b in cov: have[a:b] = True
    if not have.all(): sys.exit(f"missing poses: {np.nonzero(~have)[0][:20]}")
    g = np.lib.format.open_memmap(os.path.join(d, "grid.tmp.npy"), mode="w+", dtype=np.int8, shape=(N, n, n, n))
    S = None
    for a, b in cov:
        g[a:b] = np.load(os.path.join(d, f"part_{a:04d}.npy")); s = np.load(os.path.join(d, f"skins_{a:04d}.npy"))
        if S is None: S = np.zeros((N,) + s.shape[1:], np.float32)
        S[a:b] = s
    g.flush(); del g
    np.save(os.path.join(d, "skins.tmp.npy"), S); os.replace(os.path.join(d, "skins.tmp.npy"), os.path.join(d, "skins.npy"))
    os.replace(os.path.join(d, "grid.tmp.npy"), os.path.join(d, "grid.npy"))
    meta = dict(n_clip=nc, n_ws=nw, poses=N, h=CB.H_GRID, half=CB.HALF, q=CB.Q, exact_share=float(np.mean([i["frac"] for i in info])),
                secs=round(sum(i["secs"] for i in info), 1), created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                built="farm, tools/bench_cache_farm.py (%d parts)" % len(info))
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1); print("assembled", d, meta, flush=True)


def use(nc, nw):
    """bash snippet: copy the volume cache to worker-local disk once (flock), link it into this job's tree"""
    key, _ = key_of(nc, nw); src = os.path.join(VOL, key); loc = f"/tmp/bench-{key}"
    return (f'( flock 7; [ -f {loc}/meta.json ] || {{ rm -rf {loc}.tmp && mkdir -p {loc}.tmp && cp {src}/grid.npy {src}/skins.npy {loc}.tmp/ '
            f'&& cp {src}/meta.json {loc}.tmp/ && rm -rf {loc} && mv {loc}.tmp {loc}; }} ) 7>/tmp/bench-{key}.lock; '
            f'mkdir -p .cache/concept_bench && ln -sfn {loc} .cache/concept_bench/{key}')


if __name__ == "__main__":
    a = sys.argv[1:]; what, nc, nw = a[0], int(a[1]), int(a[2])
    opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    if what == "part": part(nc, nw, opt("--j0", 0), opt("--j1", 10 ** 6), opt("--procs", 2))
    elif what == "assemble": assemble(nc, nw)
    elif what == "use": print(use(nc, nw))
    elif what == "key": print(key_of(nc, nw))
    elif what == "jobs":
        key, N = key_of(nc, nw); ch = opt("--chunks", 10); procs = opt("--procs", 2); step = -(-N // ch)
        if "--assemble" in a:
            jobs = [dict(cmd=f"python3 tools/bench_cache_farm.py assemble {nc} {nw} && ls -la {VOL}/{key}", tag=f"bcf-asm-{key}", include=INC, base=False)]
        elif "--validate" in a:
            jobs = [dict(cmd=f'{use(nc, nw)} && python3 tools/concept_bench.py --validate {nc} {nw} && cp .cache/concept_bench/{key}/meta.json /tmp/bcf_meta.json; cat {VOL}/{key}/meta.json',
                         tag=f"bcf-val-{key}", include=INC, base=False, env=dict(IGL_NUM_THREADS="2"))]
        else:
            jobs = [dict(cmd=f"python3 tools/bench_cache_farm.py part {nc} {nw} --j0 {j0} --j1 {min(N, j0 + step)} --procs {procs}",
                         tag=f"bcf-{key}-{j0:04d}", include=INC, base=False, env=dict(IGL_NUM_THREADS="1")) for j0 in range(0, N, step)]
        print(json.dumps(jobs, indent=1))

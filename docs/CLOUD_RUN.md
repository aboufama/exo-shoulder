# Cloud CPU farm: run a judge or a sweep on RunPod in one command

The 4-core box is the project's bottleneck (load 20-40 with a dozen agents). CPU-heavy, parallel work goes to a
serverless CPU endpoint on RunPod (`exo-cpu1`, code in `pipeline/cloud/`), driven by `tools/cloud_run.py` (stdlib only).

## One command

```bash
python3 tools/cloud_run.py judge cad_r18_n3_s1392_1_f300 fast          # tools/judge_all.sh <id> fast on the farm
python3 tools/cloud_run.py run --include docs/concepts/models --out 'docs/concepts/sweeps/*.json' -- \
        "python3 docs/concepts/models/seed-2r-cring.py check"             # any bash command, files back into the tree
python3 tools/cloud_run.py batch jobs.json                              # N jobs at once (4 slots today: 1 job per worker, 8 vCPU each)
python3 tools/cloud_run.py ping                                         # worker facts: python, packages, CPU, volume
python3 tools/cloud_run.py sweep docs/concepts/models/<id>.py --configs configs.json --out results.json   # bench sweep
```

## For screening agents (concept-bench sweeps on the farm)

Copy-paste (the key is read from the file, never typed or echoed; the RUNPOD_API_KEY env var in some containers is a
stale placeholder, so always pass it like this):

```bash
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py sweep docs/concepts/models/<id>.py \
    --configs /path/configs.json --out /path/results.json [--chunk N] [--jobs-per-chunk J] [--n-clip 60 --n-ws 160]
python3 tools/concept_sweep.py docs/concepts/models/<id>.py --configs configs.json --out results.json --jobs 2   # same, locally
```

- `configs.json` = a JSON list of partial parameter dicts (merged over the model's `PARAMS`). `results.json` = one entry
  per config in input order: `{i, config, report, secs}` (+ `error`, `trace` when that config raised). `report` is the
  bench report (reach, follow, inband14, inband10, contact, gap, poses, mode; kit models add closure, mass_g, flips...).
- The model contract (`tools/concept_sweep.py`, first hook found): a concept_kit model's `build(B, F, params)` (scored
  with `K.evaluate`), else `bench_eval(B, params) -> report`, else the bench's `metal(pose, frames, params)`.
  `tools/concept_baseline_sweep.py` is the adapter for the champion 3R (`tools/concept_baseline.py`).
- **Slots today: 4 jobs x 8 processes = 32 configs at once** (4 workers x 8 vCPU; one job per worker). Root cause, measured
  2026-10-15 21:43-21:50 UTC: the 3.12 build (farm-2, `max_concurrency=4`) IS live, but the Flash CPU image boots its own
  `/app/handler.py`, which imports the generated `handler_exo-cpu1.py` as a module and calls
  `runpod.serverless.start({"handler": handler})` without the generated `concurrency_modifier`, and runpod 1.10.1 has no
  env var for it - so every worker takes ONE job (12 sleep-20 jobs: 3 per worker, strictly sequential, wall 121 s). A plain
  redeploy cannot fix it. The fix (farm-3, "Redeploy in place" below) is built. A canary passed: the module is imported,
  then `start()` is called the way the image calls it, then `JobScaler.set_scale()` gives concurrency 4. It ran locally on
  runpod 1.12.0 (the image has 1.10.1 and the same JobScaler path, source read on a worker). It waits for the user's go:
  deploying to the shared endpoint was refused by this session's permission policy. After it lands: 4 workers x 4 jobs =
  **16 job slots**, still 32 vCPU in all (2 per job). Sweeps then make chunks of `max(ceil(n / 16), min(n, 2))` configs and
  run 2 processes each (set `CLOUD_JOBS_PER_WORKER=4`, the default once farm-3 is verified). Until then `sweep` makes
  chunks of `max(ceil(n / 4), min(n, 8))` configs (fill one worker's 8
  processes before taking another worker: a job bills the whole worker) and runs each with up to 8 processes
  (`--jobs-per-chunk`, `--chunk` override) and `IGL_NUM_THREADS=1`. Verified 19:33 UTC, 8 champion configs: 1 chunk x 8
  processes = wall 44 s, 42 worker-s ($0.0034), 1 slot; the old `ceil(n/4)` split (4 chunks x 2) = wall 30 s, 92 worker-s
  ($0.0074), all 4 shared slots. Pass `--chunk 2` when latency matters more than cost and the queue is empty. The 4 workers are
  shared by every agent: a sweep queues behind other agents' batches (seen 19:00-19:15: 31 map jobs + a sweep, queue 15). Each job ships only what a bench sweep reads (the model, tools/, judge/, pipeline/avg/, the pose
  files, split.json, docs/concepts/models/: 29 MB, uploaded once ever); `--full-base` ships the whole repo. The configs
  travel inside the command (no upload round trip). The bench grid cache `.cache/concept_bench` (562 MB, key
  0089c747c10f) is in the farm's CAS since 18:10 UTC; each worker copies it once to local disk and every job symlinks
  it read-only. If the local cache is rebuilt, its new blobs upload once (~140 MB gzip, ~40 s).
- **When to use the farm**: only when it saves >= 3x wall-clock. Fixed cost per sweep: ~10-30 s (job setup, worker
  cold start, queue behind other agents' jobs - the farm is shared, 4 jobs at once in all). Rule of thumb from the measurements
  below (champion 3R via concept_baseline_sweep, ~25 s per config here; kit models ~1-5 s): a sweep whose local time is > ~2 min (e.g. >= 50 kit configs, or >= 10 configs of a 10-s model) goes to the
  farm; a handful of 1-3 s configs stays local. Never more than one sweep per agent at a time (the 4 workers are shared).
- **Same numbers**: 70 configuration runs compared local vs farm (45 of the champion 3R via concept_baseline_sweep, 25
  of docs/concepts/models/baseline-3r-kit.py): max abs difference 0 on every metric (reach, follow, inband14, inband10,
  contact, gap, pct, mass_g, closure, flips, collide, residual_deg) - the reports are byte-identical.

`jobs.json` is a list of `{"cmd": ..., "tag": ..., "design": [ids], "include": [paths], "out": [globs], "env": {...}}`.
Options for `run`/`batch`/`judge`: `--design ID` (ships `pipeline/full-exo/designs/ID`, git-ignored files included, the
viewer-only `parts/` and `preview/` left out), `--include PATH` (file or dir, git-ignored ok), `--out GLOB` (what comes
back; only files the job created or changed), `--outdir DIR` (write them there instead of the tree, e.g. to compare with
a local run), `--env K=V`, `--timeout S`, `--bench-cache` (ship `.cache/concept_bench`, the bench's distance grids).

Every job prints: return code, run seconds, CPU, the $ it cost, the last log lines; the full log is in
`~/.cache/cloud_run/logs/<tag>.log`. The batch line gives wall-clock, the parallel speed-up and the billed worker-seconds.

## When to use it (user, 2026-10-15: "as cheap as possible if it provides a big speed up")

- Send work here only when the batch saves >= 3x wall-clock over this box: judge_all on a design, a concept sweep,
  several designs or seeds at once. A single job of < 1 min stays local. The client prints the local load: when the box
  is not saturated (load < cores) and the batch is one short job, run it locally.
- Jobs run with `OMP_NUM_THREADS=1` by default (set `--env OMP_NUM_THREADS=8` for a numpy-heavy job that has a worker to itself).
- Not on the farm (yet): `judge/fea.py` (CalculiX and gmsh are not in the worker image; `judge` sets `SKIP_FEA=1`) and
  `judge/part_validity.py` on STEP parts (cadquery/OCP not in the image: it fails on the farm, its local JSON is kept).
  Run those two locally.

## How it works

- **Files**: the job ships git-tracked + untracked-not-ignored files (renders, media and other designs left out) plus
  whatever `--design`/`--include` names. Each file is a blob named by its sha256 in a content-addressed store on the
  endpoint's network volume (`exo-farm-cas`, 20 GB, EU-RO-1): uploaded once ever by small `put` jobs (gzip, <= 6 MB per
  job to stay under RunPod's 10 MB request limit), then reused by every job and worker. A later job uploads only the
  files that changed. `~/.cache/cloud_run/known_blobs.json` remembers what the farm has (delete it to force a re-check).
- **Run**: the worker copies the job's files into a fresh directory, puts its own python first on `PATH`, runs the
  command with `bash -c`, and returns the files matching `--out` that are new or changed (sha-checked on both ends).
- **Never shipped** (hard deny in the client, also for `--include`): `data/raw/private/` (personal data), anything named
  like a key (`.runpod_key`, `*.key`, `.env`, `*.pem`, `id_*`), the user's `personal-shoulder-diagnosis` folder, symlinks
  leaving the repo. Secret-like `--env` names are refused; the worker strips KEY/SECRET/TOKEN variables from the
  command's environment. The API key comes from `RUNPOD_API_KEY` or `~/.runpod_key` and is never printed.
- **Same numbers as local**: the job's python is the image's CPython 3.12 with the local versions pinned (numpy 2.0.2,
  scipy 1.13.1, trimesh 4.12.2, libigl 2.6.3, networkx 3.6.1, rtree 1.4.1, mujoco 3.16.0, pillow 12.3.0; locally CPython
  3.11 with the same versions). Validation below and in "For screening agents".

## Worker python (diagnosis 2026-10-15 18:00 UTC, and the fix in use)

- **Symptom**: `ping` reported python 3.12.14 but `numpy: missing ImportError`, scipy / trimesh / igl / mujoco missing.
- **Cause (measured with a diagnostic job)**: the bundle the endpoint runs is the 15:13 UTC build made with
  `--python-version 3.11` (`/app/flash_manifest.json`: `"python_version": "3.11"`, `/app/numpy/_core/
  _multiarray_umath.cpython-311-x86_64-linux-gnu.so`) on the `runpod/flash-cpu:py3.12` image - CPython 3.12 cannot load
  cp311 extension modules (numpy then says "you should not try to import numpy from its source directory"). The later
  3.12 redeploy never landed (the NetworkVolume undeploy error). A local `flash build --python-version 3.12` is correct
  (cp312 wheels, 108 MB), so a redeploy fixes the bundle.
- **Redeploy status (corrected 21:50 UTC)**: the 18:05 `flash deploy` DID land the code: it made the 3.12 build
  (cmv9uml2f) the active build of the Flash env `cloud/production` before its endpoint reconcile failed (it tried to
  provision a NEW endpoint, refused by the account worker quota of 10), and workers unpack the env's active build when they
  boot. `ping` 21:41: handler python 3.12.14, numpy 2.0.2 importable, `farm-2`. The pinned tar below stays in use
  (same versions; harmless).
- **Fix in use (no endpoint change)**: the pinned packages for CPython 3.12 were pip-installed by a farm job into the
  volume and packed as one tar, `/runpod-volume/exo-farm/py312/v1.tar` (425 MB; rebuild: `cloud_run.py pyenv`). Every job
  extracts it once per worker to `/tmp/farm-py312-v1` (2.2 s, flock-guarded) and puts it first on `PYTHONPATH`
  (importing straight from the network volume costs 11.8 s per process; from local disk 0.6 s). The broken `/app`
  packages stay on the path behind it and are never reached.
- **libigl threads**: libigl sizes its pool from `hardware_concurrency()` = the host's 192 cores, not the job's 8-vCPU
  quota; a bench configuration took 55 s instead of 8 s. Every job now exports `IGL_NUM_THREADS` = vCPUs /
  `CLOUD_JOBS_PER_WORKER` (= 8 today, 1 job per worker; 2 after a redeploy with 4 jobs per worker; 1 in sweeps, which run
  one process per vCPU) unless the job sets it. Measured on the same
  20-config chunk: 692 s -> 89 s, identical reports.

## Redeploy in place (no new endpoint, same queue)

`tools/farm_redeploy.py` does what `flash deploy` does minus the endpoint reconcile: uploads `.flash/artifact.tar.gz` as a
new build of app `cloud`, makes it the active build of env `production`, stores the manifest with the existing endpoint
id, and writes the new source fingerprint into the endpoint template's env (the env var flash itself uses), so RunPod
replaces the workers as they finish their jobs. The queue belongs to the endpoint, so queued jobs are kept. It also sets
executionTimeoutMs 3600000. `status` shows the active build, `rollback <build id>` restores one (farm-2 = cmv9uml2f).

```bash
cd pipeline/cloud && RUNPOD_API_KEY="$(cat ~/.runpod_key)" flash build --python-version 3.12      # farm-3 is built (21:52 UTC)
cd ../.. && RUNPOD_API_KEY="$(cat ~/.runpod_key)" ~/.local/share/uv/tools/runpod-flash/bin/python tools/farm_redeploy.py deploy
# verify: 12-16 sleep-20 jobs show 4 at once per worker and ping says farm-3; then CLOUD_JOBS_PER_WORKER default -> 4 in tools/cloud_run.py
```

farm-3 = farm-2 + `pipeline/cloud/farm_worker.py` wrapping `runpod.serverless.start` at import (worker only, guarded by
try/except: any failure leaves the stock 1-job behaviour) to add `concurrency_modifier: 4`. The generated handler module
is imported before `/app/handler.py` calls `start()`. **Needs the user's go**: the in-place deploy and the fallback quota
rebalance (exo-band23 workersMax 0, exo-cpu1 6: +50 % workers) were both refused by this session's permission policy
("Production Deploy" / "Modify Shared Resources").

## Endpoint, cost, hygiene

| item | value |
|---|---|
| endpoint | `exo-cpu1` n1f5v21dfrco3b (Flash app `cloud`, env `production`, `pipeline/cloud/farm_worker.py`; redeploy: "Redeploy in place") |
| instance | cpu3c-8-16 (8 vCPU, 16 GB), fallback cpu5c-8-16 |
| rate | $0.288/h per worker = $0.036 per vCPU-h (the lowest RunPod serverless CPU rate; cpu5c $0.336/h) |
| scaling | workersMin 0, workersMax 4 (account quota 10 across all endpoints), idle 10 s, 1 job per worker today (the image ignores max_concurrency; 4 after the farm-3 redeploy), executionTimeoutMs 0 (`farm_redeploy.py deploy` sets 3600000) |
| storage | network volume `exo-farm-cas` 20 GB, EU-RO-1: $1.40/month |

`python3 tools/runpod_guard.py audit | enforce` covers it (workersMin 0, idle <= 10 s, workersMax <= 10, volume listed).
Per-run costs are logged in `docs/RUNPOD_COSTS.md`.

## Validation (cloud vs local, same design, same commands)

See the "CPU farm" section of `docs/RUNPOD_COSTS.md` for the measured run: R2 body contact (`judge/body_contact.py
--step 6`) and `score_design.py` (10 mm and 14 mm bands) on `cad_r18_n3_s1392_1_f300`, run locally and on the farm.

## Measured (2026-10-15 18:10-19:15 UTC; local box: 4 cores, load 12-28 from the other agents)

| workload | local (`concept_sweep --jobs 2`, nice 10) | farm job (compute / wall incl. setup, queue-free) | speed-up | $ per chunk (cpu3c, whole worker) |
|---|---|---|---|---|
| 20 configs, champion 3R (concept_baseline_sweep, pcts 90/95/100) | 515 s | 89 s / 109 s (2 processes, before the 1-job-per-worker finding) | 4.7x | $0.0087 |
| same, 8 processes on one worker (the `sweep` default since 19:05) | 515 s | **35 s / 37 s** | **14.7x** | $0.0037 |
| same, before the libigl thread fix | - | 692 s / 705 s | 0.7x | $0.057 |
| 20 configs, docs/concepts/models/baseline-3r-kit.py | 100 s | 17.5 s / 31 s on the worker (2 processes) | 3.2x on the worker | $0.0032 |

- Per CPU-hour: $0.036 per vCPU-h (cpu3c-8-16, $0.288 per worker-hour); a farm job holds a whole worker today.
- Overheads that decide whether the farm pays: job setup 2 s (sweep file set, 29 MB) or 11-13 s (whole repo); first job
  on a worker +2.2 s (package tar) + ~3 s (bench grids copy); cold start of a worker 5-40 s; uploads of new files go
  through `have`/`put` jobs that wait in the same queue as everybody's compute (kit5: 17 min behind a 31-job batch).
- Same numbers: 70 configuration runs local vs farm (champion 3R: 5 + 20 + 20 at 8 processes; baseline-3r-kit: 5 + 20),
  every metric identical (max abs difference 0).
- The real bottleneck is the shared queue, not compute: the c20 chunk above computed in 35 s but its wall was 1103 s,
  because its `have` / `put` upload jobs waited 17 min behind another agent's 31-job batch on the same 4 workers. Keep
  the shipped files unchanged between sweeps (uploads are then skipped) and do not start a sweep while a big batch runs
  (`RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/runpod_guard.py audit` shows the exo-cpu1 queue).
- Independent verification (19:24-19:52 UTC, a second agent, own configs): champion 3R via concept_baseline_sweep, 8 new
  configs (hub_r, width, clear, stack/t_link, branch, neck_deg, az/el, pcts 90/95/100; gaps 67.95-183.05): 80 values,
  0 differences local vs farm, twice (4 x 2 and 1 x 8 chunks). Local `--jobs 2` at load 26-31: 276 s; farm 30 s wall
  ($0.0074) or 44 s wall ($0.0034, 1 worker). deltoid-oval-track (metal() hook), 8 configs: identical (a dead concept,
  every config reach 0 / gap 275, the same as the model's own run()); local 67 s, farm 17 s ($0.0031). `judge
  cad_r18_n3_s1392_1_f300 fast`: rc 0, 1504 s wall, 1497 worker-s ($0.12); 148 of 151 scorecard fields equal the tree's;
  R1 differs in the 17th digit (0.4085815614067577 vs ...767), R9 NOT RUN (no FEA on the farm). Rates re-read from
  GraphQL `cpuFlavors.specifics.slsPrice` (EU-RO-1): cpu3c-8-16 $0.288/h, cpu5c-8-16 $0.336/h, cpu3c-2-4 $0.072/h (cpu3c
  is $0.036 per vCPU-h at every size).
- `judge` works: `cloud_run.py judge cad_r13_n4_s1343_1 fast` -> rc 0 in 1226 s on one worker ($0.10), full scorecard;
  R1-R8 values equal the tree's scorecard (14 h old); R10 / R11 now measured because the judges gained them since then
  (a measurement change, not a design change); R9 not run (SKIP_FEA on the farm).
- Concurrency and queue (2026-10-15 21:43-22:07 UTC): 12 `sleep 20` jobs on the 4 workers ran 3 per worker strictly in
  sequence (max 1 concurrent per worker, wall 121 s; 4 jobs per worker would take ~25 s). At 21:50-22:00 the farm held
  4 long jobs in progress with 12-15 queued: a 0-s diagnostic job waited 102 s, and the on-farm canary (a 2-s job,
  submitted 21:50) was still queued when its client gave up at 900 s. Every agent's sweep, upload (`have` / `put`) and ping shares these 4 slots. That is the case for the
  16-slot fix.

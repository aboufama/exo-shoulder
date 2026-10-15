# Cloud CPU farm: run a judge or a sweep on RunPod in one command

The 4-core box is the project's bottleneck (load 20-40 with a dozen agents). CPU-heavy, parallel work goes to a
serverless CPU endpoint on RunPod (`exo-cpu1`, code in `pipeline/cloud/`), driven by `tools/cloud_run.py` (stdlib only).

## One command

```bash
python3 tools/cloud_run.py judge cad_r18_n3_s1392_1_f300 fast          # tools/judge_all.sh <id> fast on the farm
python3 tools/cloud_run.py run --include docs/concepts/models --out 'docs/concepts/sweeps/*.json' -- \
        "python3 docs/concepts/models/seed-2r-cring.py check"             # any bash command, files back into the tree
python3 tools/cloud_run.py batch jobs.json                              # N jobs at once (16 slots: 4 workers x 4 jobs)
python3 tools/cloud_run.py ping                                         # worker facts: python, packages, CPU, volume
```

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
- **Same numbers as local**: the worker runs CPython 3.11 with the local versions pinned (numpy 2.0.2, scipy 1.13.1,
  trimesh 4.12.2, libigl 2.6.3, networkx 3.6.1, rtree 1.4.1, mujoco 3.16.0). Validation below.

## Endpoint, cost, hygiene

| item | value |
|---|---|
| endpoint | `exo-cpu1` (Flash, `pipeline/cloud/farm_worker.py`, deploy: `cd pipeline/cloud && flash deploy --python-version 3.11`) |
| instance | cpu3c-8-16 (8 vCPU, 16 GB), fallback cpu5c-8-16 |
| rate | $0.288/h per worker = $0.036 per vCPU-h (the lowest RunPod serverless CPU rate; cpu5c $0.336/h) |
| scaling | workersMin 0, workersMax 4 (account quota 10 across all endpoints), idle 10 s, 4 jobs per worker, 1 h runaway limit |
| storage | network volume `exo-farm-cas` 20 GB, EU-RO-1: $1.40/month |

`python3 tools/runpod_guard.py audit | enforce` covers it (workersMin 0, idle <= 10 s, workersMax <= 10, volume listed).
Per-run costs are logged in `docs/RUNPOD_COSTS.md`.

## Validation (cloud vs local, same design, same commands)

See the "CPU farm" section of `docs/RUNPOD_COSTS.md` for the measured run: R2 body contact (`judge/body_contact.py
--step 6`) and `score_design.py` (10 mm and 14 mm bands) on `cad_r18_n3_s1392_1_f300`, run locally and on the farm.

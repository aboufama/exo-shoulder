# RunPod cost log and recommendations

Owner: the RunPod cost-efficiency agent (session 2026-10-15). Tool: `python3 tools/runpod_guard.py audit | enforce | watch`
(stdlib only, key from `~/.runpod_key` or `RUNPOD_API_KEY`, never printed). Budget for the session: plan ~$2, hard cap $5
above the starting point (balance $56.71, spend/hr $0.078 = idle storage of the nine exited `crl-*` pods, not ours).

## Log (one row per audit / batch)

| time (UTC) | endpoint | GPU pool | worker-s | spend/hr | balance before -> after | inefficiencies found | fixed |
|---|---|---|---|---|---|---|---|
| 10-15 00:35 | all exo-* | band11: ADA_24 (4090) + AMPERE_24 (A5000, L4, 3090); blender: ADA_24 | n/a (nothing finished) | 0.768 at 00:34 (4 band11 workers booting), 0.078 from 00:36 | 56.71 -> 56.70 | (1) band11: 1 job queued, 0 running, 4 workers idle/ready for >4 min (not starting); (2) GPU priority order puts the 4090 first (highest per-second rate); (3) `executionTimeoutMs` = 0 on band11 (decorator value 5400000 not applied -> no server-side kill for a hung job); (4) scaler QUEUE_DELAY/4 s booted 4 workers for 1 queued job; (5) old exo-band8/9/10 idleTimeout 120 s (workersMax already 0) | (5) idleTimeout -> 30 s via `enforce`; (1)-(4) reported to the lead, not changed (outside the allowed tuning list or needs the lead's OK) |
| 10-15 00:43 | exo-band11 -> exo-band12 | band11 failed smoke job (py3.11 bundle on py3.12 workers); band12 = AMPERE_24 (A5000, L4, 3090), exec timeout 3900000 ms | smoke job ~1 worker | 0.768 while 4 band11 workers booted (00:34 and 00:43), back to 0.078 | 56.71 -> 56.69 | 4 workers booted for 1 queued job (QUEUE_DELAY/4 s); band11 workers kept initializing ~1 min after workersMax was set to 0, fully gone 00:44; band12 pool still contains the slow L4 | lead moved to band12 (24 GB Ampere only, timeout set); band11 workersMax 0; guard now treats band11 as superseded |
| 10-15 00:47-00:53 | exo-band12 | 24 GB Ampere (A5000/L4/3090) | ~4 x 220 s (boot ~90 s + ~100 s job + 30 s idle) = ~900 | 2.84 with 4 running | 56.69 -> 56.53 (~$0.16 incl. boot of next batch) | **WASTED**: first r14 batch (4 jobs) failed after ~100 s on a client payload bug (held-out clips left empty in the clip table, IndexError in dp_path); each job paid cold start + map build before failing. Lesson: run the payload through a 1-job `band_eval` stride-heavy smoke test (or locally) before fanning out 4 workers | fixed client side by the lead, batch resubmitted 00:53 |
| 10-15 00:53-01:28 | exo-band12 | gpuTypeIds A5000+3090 (set by lead 00:47); all 4 jobs actually ran on RTX PRO 6000 Blackwell MIG 1g.24gb | 4 jobs: search 1339-1730 s + ~200 s setup each = ~6600 + 1 eval job 111 s | 2.84 with 4 running, 0.078 from 01:28 | 56.53 -> 55.28 = $1.25 | none: 4 workers busy ~27 min, all reaped by 01:28 (health listed 1 run / 3 idle "ghost" workers for 10 more min while spend/hr was already 0.078 - stale report, not billing) | - |
| 10-15 01:37-02:12 | exo-band12 | A5000+3090 list; all 4 jobs on RTX PRO 6000 Blackwell MIG 1g.24gb | 4 jobs x 1802-1826 s (+ ~90 s cold start + 30 s idle) = ~7800 worker-s | 2.84 with 4 running, 0.078 from 02:12 | 55.27 -> 53.81 = $1.46 ($0.365/job) | none: all 4 jobs ended together at max_secs (no stragglers), workers reaped by 02:12; r15 = 16338 evals -> $0.089 per 1000 evals | - |
| 10-15 02:22 | all exo-* | - | - | 0.078 | 53.77 | final audit: workersMin 0 everywhere, band8-11 at workersMax 0, band12/blender idle 30 s; health still lists 4 idle workers on band12 and on the user's blender endpoint, but the account counter is at the 0.078 baseline (listed, not billed) | `enforce`: nothing left to fix |

## State seen at the first audit

- `exo-band8/9/10`: workersMin 0, workersMax 0 (superseded, correct). `exo-blender-cycles` (user): workersMin 0, workersMax 4,
  idle 30 s; it showed 2-4 workers "running"/"idle" with an empty queue and 456 completed jobs (the user's render batch draining) -
  not touched. `exo-band11`: workersMin 0, workersMax 4, idle 30 s, flashboot on.
- Nine `crl-*` pods are EXITED (the user's, not touched): their storage is the standing $0.078/h (~$1.9/day).

## GPU tier: what the job needs and what it should run on

Job facts (from `band_impl.py` and the stored results): 2-4 GB VRAM for the maps cache, torch kernels plus numpy posing (CPU part),
per-job setup 1-3 min (maps rebuilt each job), then a search that stops at `max_secs` or when the generations are done. Past jobs
(on RTX PRO 6000 Blackwell MIG slices) took 870-1250 s (r5, ended by generations) and 2650-3040 s (r9, ended by max_secs 3000), about
1.2 evals/s. Typical job: 15-50 min.

Flash pools (from `runpod_flash/core/resources/gpu.py`) and RunPod's published serverless flex rate (per second, standard workers;
verify in the console, the API does not expose serverless rates; pod prices below come from the GraphQL `gpuTypes` query today):

| Flash pool | GPUs | VRAM | mem. bandwidth | flex $/s (published) | $/h | 45-min job | 4 jobs | pod secure $/h (API) |
|---|---|---|---|---|---|---|---|---|
| AMPERE_16 | A4000, A4500, RTX 4000 Ada, RTX 2000 Ada | 16-20 GB | 224-640 GB/s | 0.00016 | 0.58 | $0.43 | $1.73 | 0.25 / 0.25 / 0.28 / 0.24 |
| AMPERE_24 | A5000, 3090, L4 | 24 GB | 768 / 936 / 300 GB/s | 0.00019 | 0.68 | $0.51 | $2.05 | 0.27 / 0.50 / 0.59 |
| ADA_24 | RTX 4090 | 24 GB | 1008 GB/s | 0.00031 | 1.12 | $0.84 | $3.35 | 0.89 |

Reading: the job fits in 16 GB, so VRAM is not the constraint. The cheapest sensible choice is AMPERE_24 restricted to A5000 and 3090
(the L4 has 300 GB/s, the slowest of the pool at the same price). The 4090 costs 1.63x per second; it only pays if it is >1.63x faster
on this job, which a partly CPU-bound numpy/torch mix will not reach. AMPERE_16 saves another 16% per second but contains cards with
224-448 GB/s; because the search stops at a fixed `max_secs` the dollars are fixed and a slower card simply does fewer evaluations,
so the 16 GB pool is only a win if the job is CPU-bound. Decide with data, not by guess: after the first results, compute
`$ per 1000 evals = rate_per_s * secs / evals * 1000` from each result's `device`, `secs`, `evals` (see the table when filled).

| device (from result json) | secs | evals | evals/s | rate $/s | $ per 1000 evals (search secs + ~200 s setup) |
|---|---|---|---|---|---|
| RTX PRO 6000 Blackwell MIG 1g.24gb (r14 3R seed jobs, band12) | 1339-1454 | 2932 | 2.0-2.2 | 0.00019 (account counter: $0.69/h per worker) | $0.10-0.11 |
| RTX PRO 6000 Blackwell MIG 1g.24gb (r14 4R control) | 1730 | 2929 | 1.7 | 0.00019 | $0.12 |
| RTX PRO 6000 Blackwell MIG 1g.24gb (r15 3R seed jobs, band12) | 1802-1826 | 3840-4297 | 2.1-2.4 | 0.00019 | $0.089 (whole batch, billed incl. cold start) |
| RTX PRO 6000 Blackwell MIG 2g.48gb (r9, old endpoints, 48 GB pool) | 2660-2930 | 3244-3250 | 1.1-1.2 | not measured (48 GB pool, higher rate) | - |

Observation: although band12's `gpuTypeIds` is [A5000, 3090], every r14 job reported a Blackwell MIG 1g.24gb slice, so the REST list acts
as a preference/VRAM class, not a strict filter, and the billing was the 24 GB rate ($0.69/h per worker, exactly the GraphQL secure price
of that MIG type and the published 24 GB flex rate). That slice is the fast, cheap case for this job (2 evals/s at $0.69/h); there is
no reason to move to the 16 GB pool or to pay for a 4090 unless a later result shows the job is GPU-bound on that slice.

## Other settings

- **Idle timeout 30 s: keep.** For one parallel batch the cold start is paid once per worker whatever the timeout; idle billing is
  at most 30 s x workers x $0.00019 = $0.02 per batch. Do not go lower than ~5 s (the next queued job may land right after one ends).
- **Flashboot on: keep** (faster re-spawn of a recently used worker image).
- **Scaler:** QUEUE_DELAY/4 s adds a worker whenever the oldest job waits >4 s, up to workersMax, so 1-2 jobs can still boot 4
  workers (seen at 00:34: 4 workers for 1 job, spend/hr 0.768 for ~2 min). Prefer REQUEST_COUNT with value 1 (one worker per queued
  request) or set workersMax = number of jobs. Not changed by the guard (not on its allowed list).
- **Execution timeout:** the endpoint reports 0 although `worker.py` asks for 5400000 ms (90 min). `band_impl` stops itself at
  `max_secs` (default 3000 s), so only a hang is unprotected. Suggested: PATCH `executionTimeoutMs` = (max_secs + 600) * 1000, or pass the
  per-job policy; the guard `watch` flags any job that runs > max_secs + 10 min without a completion.
- **Batching seeds per worker vs parallel cold starts:** a cold start plus map build is ~3 min of billed time per worker (3 x 60 s x
  $0.00019/s = $0.03 per worker at AMPERE_24 rates, 4 workers = $0.12). Running the 4 seeds serially in one worker would save 3 of those
  (about $0.09) but make the batch 4x slower in wall-clock. Parallel is right; batching only matters for dozens of short (<5 min) jobs.

## Standing rules for the lead (cheap habits)

1. After every batch: `python3 tools/runpod_guard.py enforce` (workersMin 0, idle <= 30 s, old endpoints at max 0), then `audit`.
2. Set workersMax = number of parallel jobs (not the quota of 10).
3. New endpoint per code change; the old one goes to workersMax 0 (the guard does this for band8/9/10).
4. `workersMin` > 0 only to start a stuck queue, and back to 0 right after.

## Session summary (2026-10-15, 00:33-02:22 UTC)

- **Total spent: $2.94** (balance 56.71 -> 53.77), cap was $5, plan ~$2. Breakdown: failed smoke/payload runs ~$0.18 (of which the
  payload-bug batch ~$0.16 was pure waste), r14 batch $1.25, r15 batch $1.46, remainder = standing storage of the `crl-*` pods
  ($0.078/h x 2 h = $0.16, not ours).
- **Found and fixed:** old exo-band8/9/10 idleTimeout 120 s -> 30 s (enforce); band11 retired (workersMax 0, lead) after its py3.11
  bundle failed on py3.12 workers; GPU list moved from [4090, A5000, L4, 3090] to [A5000, 3090] (lead, on the guard's advice); execution
  timeout 0 -> 3900000 ms on band12 (lead). No workersMin > 0, no stuck queue, no idle billing leak, no straggler job at any poll.
- **Found, not changed:** scaler QUEUE_DELAY/4 s boots 4 workers for a single job (smoke tests, the eval job); health keeps listing
  "idle/running" ghost workers for up to ~10 min after a batch while the account counter is already at baseline (the guard compares
  against spend/hr before it calls it a leak); the REST `gpuTypeIds` list is a preference, not a filter (all jobs landed on a Blackwell
  MIG 1g.24gb slice at the 24 GB rate).
- **Waste to avoid next time:** the failed r14 batch (~$0.16) paid 4 cold starts + map builds to fail on an IndexError. Smoke-test the
  payload on one job (or locally) before fanning out 4 workers; a 1-job `band_eval` costs ~$0.03.

## Recommendations (with numbers)

1. **Keep the 24 GB tier, no 4090.** $0.69/h per worker, 2.0-2.4 evals/s, $0.09-0.11 per 1000 evals. A 4090 would cost 1.6x per second
   (about $1.12/h) and the job is only partly GPU-bound; the 16 GB pool saves 16% per second but offers slower cards (224-448 GB/s) and
   the search is time-boxed, so it would just do fewer evals for the same money. Re-test only if a profile shows the job GPU-bound.
2. **Parallel jobs, one per worker, workersMax = number of jobs.** Cold start + map build is ~3 min per worker (~$0.03); 4 jobs of 30 min
   cost $1.4-1.5 total regardless of batching. Batching seeds serially would only save ~$0.09 and quadruple wall-clock.
3. **max_secs 1800 is the right size**: 4 x 30 min = $1.46 per batch; every job ended at its max_secs (r15) or by generations (r14).
   Use `max_secs` + 10 min as `executionTimeoutMs` (already 3900000 on band12).
4. **idleTimeout 30 s, flashboot on, workersMin 0**: idle cost per batch <= 4 x 30 s x $0.00019 = $0.02.
5. **Scaler:** switch to REQUEST_COUNT with value 1 for batches smaller than workersMax (would have saved the 3 surplus worker boots on
   every smoke/eval job, ~$0.02-0.03 each); irrelevant for full batches of 4.
6. After each batch run `python3 tools/runpod_guard.py enforce && python3 tools/runpod_guard.py audit`; for unattended runs
   `python3 tools/runpod_guard.py watch --ep <endpoint> --max-secs <max_secs> --log <file>` exits 2 on idle billing, a stuck queue or a
   job that outlives max_secs + 10 min, and runs `enforce` itself when the queue is empty for 3 polls.

# freek-oracle-route-knuckle-4r cell B: final polish on an envelope bench (2026-10-18, local, 120-min box)

Self-measured. A polished config replaces the verified config only after an independent verifier confirms a held-out
gain of at least 1 gap point (CLAUDE.md final-polish rule). This file never edits the row, the model, the verifier or a
judge. The CPU farm was closed (CLAUDE.md (7), budget spent): everything ran on the shared 4-core box, niced, at most
2 processes, OMP_NUM_THREADS=1, $0.

@@ANSWER@@

## 1. The search bench: `envh` (a measurement choice, stated)

The `env` bench (`tools/env_bench.py`, `docs/research/minarc_final_polish.md`) has its fast cache only on the farm
volume. A local rebuild of its 530 poses ran at about 12 s per pose per process on the shared box (load 7-10 on 4 cores),
i.e. about 53 min of the 120-min box. So this polish searches on **envh**:

* the **60 clip frames of Bench(60,160)** (their fast cache is local; they are the verified protocol's own fit frames, never
  Wave / Walking);
* the **first stride-2 pass of env's 420 fresh workspace poses** (env positions 110, 112, ..., 528 = 210 poses). env lists
  its draws stratum by stratum, so a stride keeps every stratum's share. Built locally pose by pose
  (`.cache/envposes/env`, 2 processes, 09:05-09:21 UTC; 19 rows salvaged from a first contiguous build that was stopped).
* **Held-out split held out**: `bench_envh()` asserts that no envh pose is a held-out pose; env's draws keep >= 2.04 deg
  (orientation) / 2.23 deg (coordinates) from every held-out pose (the env table).

**The distribution** (workspace poses only; `docs/research/freek_env_polish/env_table.json`):

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead (el >= 140) | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| Bench(60,160) ws | 160 | 2.5 % | 28.1 % | 7.5 % | 16.9 % | 6.3 % | 36.3 % | 23.8 % | 26.9 % | -26.1 |
| env ws | 420 | 9.3 % | 23.1 % | 7.1 % | 17.1 % | 6.0 % | 35.7 % | 24.0 % | 27.4 % | -34.0 |
| **envh ws** | 210 | **9.5 %** | 23.3 % | 7.1 % | 17.1 % | 5.7 % | 35.7 % | 23.8 % | 27.1 % | -33.6 |

envh matches the full grid on every band within sampling error. **Its cost is noise:** a 210-pose reach share has a
binomial standard error of about 0.029, i.e. about 3 gap points (env's 420: about 2). A search on envh can buy closure that
is sampling noise. This is why every number that decides anything below is a claim number (exact, frozen, held out).

@@BODY@@

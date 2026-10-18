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

## 2. The verified config on envh

The verified config (k33 seats + cell B, q3max 86 in the model's q3 = own angle q3' 96.87; priced: J2 stops 7.877 /
7.829, stop B a1max 76.04, no rule cut) re-scored through the polish objective (fast, continuity on, one fold reading):

| protocol | plain gap | near-touch gap (1 mm) | reach | follow | ib14 | contact poses / summed depth | overhead ws taken | J3 stop engaged (taken) |
|---|---|---|---|---|---|---|---|---|
| fit envh -> score envh (in-sample, fast) | 15.54 | 15.54 | 0.781 | 0.95 | 0.899 | 8 / 17.28 mm | 5 / 15 | 17 |
| fit Bench(60,160) -> wear envh frozen (fast) | 14.75 | 18.39 | 0.786 | 0.95 | 0.897 | 7 / 16.78 mm | 5 / 15 | 17 |
| fit Bench(60,160) -> Bench(60,160) in-sample (fast) | 9.56 | 9.56 | 0.838 | 0.95 | 0.897 | 6 / 24.29 mm | 3 / 12 | 20 |
| on file: fit Bench(60,160) -> Bench(110,360) exact (verified) | 16.20 | 21.01 | 0.778 | 0.955 | 0.898 | 15 / 78.55 mm | 8 / 28 | 32 |
| on file: fit Bench(60,160) -> held out exact (verified reading) | 21.89 | 25.85 | 0.735 | 0.960 | 0.896 | 47 / 232.2 mm | 15 / 71 | 61 |

The fast fit-bench number 9.56 is the claim's own (reproduced exactly by this harness). On envh the verified config sits at
14.75-15.54 plain: the gap between its fit-bench 9.56 and every other bench is the P1 finding (the stop was placed on the
claim bench's binders), measured once more. The exact env re-score (fit envh fast -> wear envh exact) is the last item of
the claim queue (section 4).

## 3. The polish

**Objective** (`tools/freek_env_polish.py`, lower is better):
1. `P` = k33 nominal (`docs/concepts/verify/skinnormal-shortk-knuckle-4r/cand_k33.json`) + q3max + the free parameters;
   stops smhi / smlo >= 5.0 (the user's floor); stop B a1max <= bk1 + bk2 - 5.51 (the K-dyad repair of the family).
2. **Priced** like the verified row (`env_polish.priced`): each J2 stop drawn s + 0.5, read at CB_FOLD_MARGIN 5.5; K's stop B
   drawn where the 5-deg rule first cuts the stretched branch. The verified config has no cut; the polished picks do
   (pick1: dK cut 75.9 -> a1max 76.09 nominal is built as 70.71), so the pricing binds on them, not on the verified config.
3. **a** = fit on envh FAST, scored in-sample. **b** = fit on Bench(60,160) FAST (the verified protocol's fit), worn
   FROZEN on envh FAST. The slipper polish measured that an env-fit gain is a fit-protocol artifact unless the
   Bench(60,160)-fit shape travels too, so both shapes are scored.
4. **Continuity** on both: the verifier's one-reading flood (`kin_nodes_model`: state 2's moving chain is J1-K-J2) on the
   1432-pose grid, plus every fresh envh pose joined to the connected grid by a 2-deg slerp edge to one of its 6 nearest
   connected grid nodes (same law: every sample closes, no joint step > 10 deg, knee branch constant).
5. **Score**: the near-touch gap (metal < 1 mm = contact). obj = (a + b) / 2
   + claim-fit guard max(0, g60_near - a - 3) (fired on 2 of 161 tries)
   + depth guard 0.1 x max(0, summed contact depth on envh - the verified config's 17.28 mm) (fired on 20).
6. **Free** (11): q3max (the J3 dowel: a search variable on envh only, never placed from the claim bench's or the held-out
   binders, audit P1), smhi, smlo, a1max, bk1, bk2, az2, el2, wd, wa, b3. **Fixed**: the J1 seat az1 / el1 (the verified
   seat sits in the user's J1 region, back of the shoulder + acromion top; no seat-region check exists, so it is not moved),
   the two-pin knee lE / lc / phiE / phib / stk and its window ang_min (built rules), O20 hubs, the great-circle link 2.

**Run.** One CMA start at the verified config (crossfit_polish's driver), popsize 8, sigma 0.5, 2 processes, 09:21-09:43
UTC: 161 tries in 20 generations, 0 errors, median 14.9 s per try. Stopped on patience (no gain > 0.02 in 10 generations),
sigma 0.50 -> 0.295 (not collapsed).

**Convergence gate: passes, with a caveat.** Best 14.06 (x0 16.97). Gain over the second half of the tries 0.54 (< 1), over
the last third 0.00 (< 0.5), top-5 spread 0.77 (<= 3). One start only: this is a local optimum of a noisy 210-pose
objective, not a global one, and sigma never collapsed.

**What moved** (best rows): bk2 52 -> 48.9-51.1 (shorter K -> J2 arc), b3 0.40 -> 0.29-0.32 (J3 axis tilt), wa -9.6 ->
-9.9..-13.8, az2 44.4 -> 42.0-54.2, J2 stops 7.0-8.1 (nominal), q3max 84.6-86.3 (the stop barely moved: 86 sits near the
envh optimum too). On envh the gain is mostly contact: summed depth 17.28 -> 4.1-5.5 mm, contact poses 8 -> 3-4, follow
0.95 -> 1.00 on the 60 clip frames. The Bench(60,160) in-sample number gets WORSE (9.56 -> 12.0-12.8): the verified config
is the Bench(60,160) optimum.

**Picks** (`docs/research/freek_env_polish/picks/`): the best rows by objective, each >= 1 CMA step from the others in some
parameter (no envsel cache exists locally, so no independent pick-selection draw; the claim is the only arbiter):

| pick | row | obj | a near / plain | b near / plain | Bench(60,160) in-sample near | envh contacts / depth | q3max | smhi / smlo | a1max (priced) | bk1 / bk2 | az2 / el2 | wd / wa / b3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VER | - | 16.97 | 15.54 / 15.54 | 18.39 / 14.75 | 9.56 | 8 / 17.28 | 86 | 7.377 / 7.329 | 76.04 (76.04) | 32 / 52 | 44.40 / 43.87 | 66.60 / -9.63 / 0.40 |
| pick1 | fe1-g10-7 | 14.06 | 13.60 / 12.69 | 14.51 / 12.69 | 12.72 | 4 / 5.45 | 84.77 | 7.647 / 8.084 | 76.09 (70.71) | 29.33 / 48.85 | 48.92 / 41.35 | 66.72 / -13.75 / 0.293 |
| pick2 | fe1-g13-3 | 14.89 | 14.09 / 13.21 | 15.68 / 12.14 | 12.84 | 3 / 5.48 | 86.26 | 7.876 / 7.722 | 74.90 (72.80) | 29.05 / 49.91 | 42.00 / 43.61 | 67.13 / -12.84 / 0.294 |
| pick3 | fe1-g8-5 | 15.10 | 13.46 / 12.55 | 16.73 / 11.32 | 12.00 | 3 / 4.13 | 84.63 | 7.326 / 7.022 | 76.98 (74.05) | 32.21 / 51.06 | 54.19 / 39.43 | 68.24 / -9.95 / 0.323 |

@@CLAIMS@@

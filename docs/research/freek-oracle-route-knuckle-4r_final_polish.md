# freek-oracle-route-knuckle-4r cell B: final polish on an envelope bench (2026-10-18, local, 120-min box)

Self-measured. A polished config replaces the verified config only after an independent verifier confirms a held-out
gain of at least 1 gap point (CLAUDE.md final-polish rule). This file never edits the row, the model, the verifier or a
judge. The CPU farm was closed (CLAUDE.md (7), budget spent): everything ran on the shared 4-core box, niced, at most
2 processes, OMP_NUM_THREADS=1, $0.

## Answer

* **The polish gains, and no config reaches 95.** The best verified-protocol number of this 4-joint design after the
  polish is **15.40** (pick1, score 94.40; fit Bench(60,160) -> Bench(110,360) exact, frozen, priced, one fold reading),
  against the verified 16.20. That is still 1.65 gap points short of 95 (gap <= 13.75). Held out (1154 poses, the CAD
  shape) the picks reach 18.90-21.17 against the verified 21.89. This is the measured answer for the open 3-DOF-vs-95
  question on this morphology: one converged local polish moves it 0.8 points on the bench and 0.7-3.0 held out, not
  the 2.45 points it needs.
* **Held-out gain over the verified config, the CAD shape (fit Bench(60,160) -> held out exact):** pick1 **+1.39**
  (P better 0.89), pick2 +0.73, pick3 **+2.99** (P 0.998). With the shape fitted on envh: +2.06 / +0.28 / +2.21. On the
  verified protocol: +0.81 / -0.45 / +0.28.
* **Which config goes to a verifier.** pick1 is the pre-claim primary (rank 1 by the objective; picks fixed at 09:43:09,
  before any claim number). It clears the 1-point rule held out on both fit protocols, but on the stop-refusal side reading
  its CAD-shape held-out gain is +0.76 and its bench gain is 0: part of its gain is the J3 dowel refusing poses that would
  otherwise be contacts. pick3 has the stronger held-out number (+2.99; +2.28 on the side reading), but it is the best of
  three on the held-out set, so that number carries the selection. Both are candidates for an independent verifier;
  **neither replaces the verified config until one confirms** (CLAUDE.md final-polish rule). The row stays at 16.20.
* **The 3-joint lead stays the lead** (user ruling 2026-10-17: the 3-joint leaders are the real leaders; complexity 33.25
  against 18.5). For the record of that decision: polished (pick1, pick3), this 4-joint design beats the lead by 2.4-2.9 on the bench
  (P 0.93-0.99) and 1.9-3.5 held out (P 0.97-0.999), where the verified row was a coin flip (P 0.62 held out).
* **The watch items:** contact depth halves (bench 78.55 -> 39.47 mm, held 232.2 -> 127.92 mm, pick1) but stays about 2x the
  lead's; stop refusals of kit contacts get WORSE (bench 1 -> 4, held 4 -> 10); the fold margin holds (one reading min
  5.56-5.59, 0 poses under 5; the family reading improves); continuity drops 0 poses everywhere.

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
claim bench's binders), measured once more. The exact env re-score (fit envh fast -> wear envh exact) reads 15.45 against the fast
15.54: the local cache is within 0.09 of the exact path.

## 3. The polish

**Objective** (`tools/freek_env_polish.py`, lower is better):
1. `P` = k33 nominal (`docs/concepts/verify/skinnormal-shortk-knuckle-4r/cand_k33.json`) + q3max + the free parameters;
   stops smhi / smlo >= 5.0 (the user's floor); stop B a1max <= bk1 + bk2 - 5.51 (the K-dyad repair of the family).
2. **Priced** like the verified row (`env_polish.priced`): each J2 stop drawn s + 0.5, read at CB_FOLD_MARGIN 5.5; K's stop B
   drawn where the 5-deg rule first cuts the stretched branch. The verified config has no cut; the polished picks do
   (pick1: its 76.09 is first capped by the K-dyad repair to 72.67, then the rule cut at dK 75.9 / th 122.7 builds stop B at 70.71), so the pricing binds on them, not on the verified config.
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

| pick | row | obj | a near / plain | b near / plain | Bench(60,160) in-sample near | envh contacts / depth | q3max | smhi / smlo | a1max nominal -> K-dyad cap -> priced | bk1 / bk2 | az2 / el2 | wd / wa / b3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VER | - | 16.97 | 15.54 / 15.54 | 18.39 / 14.75 | 9.56 | 8 / 17.28 | 86 | 7.377 / 7.329 | 76.04 -> 76.04 -> 76.04 | 32 / 52 | 44.40 / 43.87 | 66.60 / -9.63 / 0.40 |
| pick1 | fe1-g10-7 | 14.06 | 13.60 / 12.69 | 14.51 / 12.69 | 12.72 | 4 / 5.45 | 84.77 | 7.647 / 8.084 | 76.09 -> 72.67 -> 70.71 | 29.33 / 48.85 | 48.92 / 41.35 | 66.72 / -13.75 / 0.293 |
| pick2 | fe1-g13-3 | 14.89 | 14.09 / 13.21 | 15.68 / 12.14 | 12.84 | 3 / 5.48 | 86.26 | 7.876 / 7.722 | 74.90 -> 73.45 -> 72.80 | 29.05 / 49.91 | 42.00 / 43.61 | 67.13 / -12.84 / 0.294 |
| pick3 | fe1-g8-5 | 15.10 | 13.46 / 12.55 | 16.73 / 11.32 | 12.00 | 3 / 4.13 | 84.63 | 7.326 / 7.022 | 76.98 -> 76.98 -> 74.05 | 32.21 / 51.06 | 54.19 / 39.43 | 68.24 / -9.95 / 0.323 |

## 4. The claims (exact, frozen, priced, one fold reading)

The claim harness (`tools/freek_env_polish.py claim`) is the verifier's own path: `RM.freeze` (fit FAST, wear EXACT
frozen) -> `Mk.run()` -> near-touch -> the verifier's `flood_connected` with `kin_nodes_model` (the verified one fold
reading), plus a per-pose dump (`alignment_paired._dump_bench`), the th margins on both readings, J3's own angle at the
engaged poses and the stop-refusal side reading. **It reproduces the verified config on the verified protocol exactly**:
16.20 / near 21.01 / 15 contacts / 78.55 mm / min th 5.91 / family min 0.14 (`local/claim_VER_fit60_bench.json`).
All 13 claims ran locally, at most 2 at a time, 09:43-10:17 UTC (2-5 min each).

**Gap (plain, connected = static: 0 workspace poses dropped by continuity in every claim):**

| config | verified protocol: fit Bench(60,160) -> Bench(110,360) | held out, fit Bench(60,160) (the CAD shape) | held out, fit envh | fit envh -> envh exact (search-bench check) |
|---|---|---|---|---|
| VER (verified) | **16.20** (score 94.11) | **21.89** (on file; this harness: reproduced 21.89) | 22.30 | 15.45 (fast in-sample 15.54: the cache is within 0.09) |
| pick1 (obj rank 1) | **15.40** (94.40) | **20.50** | **20.24** | - |
| pick2 (rank 2) | 16.65 (93.95) | 21.17 | 22.02 | - |
| pick3 (rank 3) | 15.93 (94.21) | **18.90** | 20.09 | - |
| lead conecut-knee-knuckle-3r (3 joints) | 18.28 | 22.38 | - | - |

**Held-out gain over the verified config** (paired bootstrap over poses within kind, `alignment_paired.compare_sets`,
`summary.json`; positive = better than VER; the per-pose dumps recompute each gap to within 0.01 of the claim):

| pick | verified protocol (bench) | held out, fit60 (CAD shape) | held out, env fit (like for like) | held out env fit vs VER's verified held (cross-protocol) |
|---|---|---|---|---|
| pick1 | +0.81 (CI90 -1.84..+5.54, P 0.73) | **+1.39** (CI90 -0.43..+3.71, P 0.89) | **+2.06** (CI90 +0.20..+4.65, P 0.97) | +1.66 (P 0.93) |
| pick2 | -0.45 (P better 0.54: a skewed bootstrap) | +0.72 (P 0.86) | +0.28 (P 0.72) | -0.12 (P 0.55) |
| pick3 | +0.28 (P 0.67) | **+2.99** (CI90 +1.36..+5.49, P 0.998) | **+2.21** (CI90 +0.56..+4.96, P 0.98) | +1.81 (P 0.97) |

**Against the 3-joint lead** (same benches): pick1 -2.89 bench (P better 0.985), -2.14 held env fit (P 0.99); pick3 -2.36
bench (0.93), -2.29 held (0.98). VER's own lead was -2.08 bench (P 0.745) / -0.49 held (P 0.62).

**Where the gain comes from** (pick1 vs VER, Bench(110,360)): contact 0.0375 -> 0.0179 (-1.96 points), in-band 0.8977 ->
0.9008 (-0.23), reach 0.778 -> 0.764 (+1.39 worse); follow 0.955 -> 1.000 (no gap effect above 0.95). Held out (fit60): the
same pattern. The polish buys contact, not reach: overhead taken 8 / 28 bench on every config; held out 15 -> 18 (pick1) /
21 (pick3) of 71.

## 5. The watch items (the audit's list, each config)

| config / wear | contact poses / summed depth | J3 stop: own angle q3' at engaged poses | stop-refused poses / of them kit contacts / side-reading gap | min th, one reading (under 5) | min th, family reading (under 5) | continuity |
|---|---|---|---|---|---|---|
| VER bench | 15 / 78.55 mm | 96.87 | 6 / 1 / 16.44 | 5.91 (0) | 0.14 (7) | 0 dropped, 0 islands |
| VER held fit60 | 47 / 232.2 mm | 96.87 | 19 / 4 / 22.30 | 6.50 (0) | 0.01 (13) | 0 / 0 |
| VER held env | 50 / 241.47 | 96.98 | 19 / 3 / 22.60 | 6.38 (0) | 0.01 (13) | 0 / 0 |
| pick1 bench | **7 / 39.47** | 92.99 | 6 / **4** / **16.39** | 5.59 (0) | **5.59 (0)** | 0 / 0 |
| pick1 held fit60 | **29 / 127.92** | 92.99 | 14 / **10** / 21.54 | 5.58 (0) | 0.70 (6) | 0 / 0 |
| pick1 held env | 29 / 134.76 | 93.10 | 14 / **11** / 21.37 | 5.58 (0) | 0.70 (6) | 0 dropped, 1 island |
| pick2 bench | 10 / 70.81 | 93.46 | 7 / 1 / 16.89 | 5.91 (0) | 0.29 (8) | 0 / 0 |
| pick2 held fit60 | 35 / 197.94 | 93.46 | 19 / 5 / 21.68 | 5.94 (0) | 0.29 (18) | 0 / 0 |
| pick3 bench | 7 / 32.95 | 94.21 | 6 / 4 / 16.92 | 6.29 (0) | 6.29 (0) | 0 / 0 |
| pick3 held fit60 | 28 / 146.71 | 94.14-94.21 | 13 / 11 / 20.02 | 5.56 (0) | 0.03 (7) | 0 / 0 |
| lead bench / held | 4 / 20.24; 14 / 60.97 | - | - | - | - | - |

* **Contact depth: better, still about 2x the lead.** pick1 halves the summed depth on the bench (78.55 -> 39.47 mm) and
  held out (232.2 -> 127.92 mm); the lead is at 20.24 / 60.97.
* **Stop refusals of kit contacts: WORSE.** The polished dowel sits about 4 deg lower on J3's own angle (92.99 vs 96.87)
  and refuses more poses that, without it, would press metal into the arm: bench 1 -> 4, held 3-5 -> 10-11. Counting
  them as contacts (audit proposal B; the kit is worn with the SAME frozen shape and the dowel removed), pick1's bench
  gain vanishes (16.44 -> 16.39) and its held-out gain shrinks to **+0.76 with the CAD shape** (fit60, 22.30 -> 21.54,
  under the 1-point rule) and +1.23 with the env fit (22.60 -> 21.37). pick3 keeps **+2.28** held out on that reading
  (fit60, 22.30 -> 20.02; env fit +1.59) but reads 0.48 worse than VER on the bench (16.92). A stop is better than metal in the arm, but on this reading most of the bench gain is the stop
  refusing contact poses. Note: the audit's side reading (16.68) counted poses 343 and 423 from the kit's own fit; worn
  with the claim's frozen shape, 423 is a kit refusal, not a contact, so VER reads 16.44 here.
* **Fold margin: holds.** Every taken pose of every config keeps th >= 5 on the one reading (min 5.56, pick3 held; 0 under
  5 everywhere; the priced J2 stops are read at 5.5). The family reading (J1-K-J3 sub-chain in state 2, report only) is
  better for pick1 than for VER: bench min 0.14 -> 5.59 (7 -> 0 poses under 5), held 0.01 -> 0.70 (13 -> 6).
* **J3 stop placement (P1).** q3max was a search variable on envh only (84.77 for pick1 = own angle 92.99 at all 23 / 43
  engaged bench / held poses: the groove is cut at 92.99, not at the model's 84.77). It was never placed from the claim
  bench's or the held-out binders. The picks were fixed by the objective rank at 09:43:09 UTC, before any claim number
  existed (file times in `local/`); they were not committed before the claims.
* **Continuity.** 0 workspace poses dropped on every claim; the one-reading flood connects 1109-1137 grid nodes with 0-1
  islands. The envh fresh poses: 167-173 of 210 joined by edges in the search; every taken one was joined.

**A second start (seed 2, convergence check, 10:17-10:28 UTC).** Same objective and x0, budget 840 s; the box slowed
to 2-3 min per generation, so it ran 6 generations, 49 tries. Best 14.69 (fe2-g4-7: q3max 86.70, bk2 50.98, b3 0.315,
wa -12.65) - the same basin and direction as the first start (whose best at 49 tries was 14.82; final 14.06). Not
better than pick1, so not claimed. It supports the gate (two starts move the same parameters the same way) but does not
make the optimum global.

## 6. Next

1. **Independent verifier** on pick1 (pre-claim primary) and pick3 (held-out selected): re-wear both protocols with its
   own harness, and rank them on a draw nobody selected on - envsel (360 fresh poses; its cache is on the closed farm
   volume, a local build is about 25 min on 2 processes with `tools/freek_env_polish.py`'s per-pose builder pattern).
2. **The stop-refusal reading needs a ruling** (audit proposal B): on it, pick1's CAD-shape held-out gain is +0.76 and
   the bench gain 0. If the lead rules refusals of contact poses count as contacts, the search objective should count
   them too; pick3 survives that reading (+2.28).
3. The audit's open physical checks carry over unchanged to any polished config: R17 with the state-2 spring hold, the
   dowel force, the cuff twist with the stop engaged. The polished dowel sits at own angle 92.99 (pick1) / 94.21 (pick3).
4. Search space left closed: the J1 seat (no seat-region check tool), the knee geometry, a longer second start (fe2
   stopped at 49 tries on the box's load). Opening the J1 seat needs a check of the user's J1 region first.

## Files

* `tools/freek_env_polish.py`: envh bench, objective, CMA (crossfit_polish's driver), gate, picks, claim (per-pose dump,
  both fold readings, J3 own angle, stop-refusal side reading).
* `docs/research/freek_env_polish/`: `env_table.json`, `envh.json` (the envh pose list), `picks/` (pick1-3 + VER nominal
  params, `picks.json`), `local/` (`cma_fe1.json` + log + state, `gate.json`, `x0_envh.json`, 13 `claim_*.json` with
  `_perpose.json` dumps and logs), `summarize.py` -> `summary.json` (claims table + every paired comparison).
* Local cache (git-ignored): `.cache/envposes/env/` (per-pose fast grids of env positions), `.cache/concept_bench/envh-491cc8b49f3d`.

## Cost

$0 farm (closed). Local, niced, at most 2 processes: envh cache 16 min x 2, CMA 22 min x 2, claims 34 min x 2, second start 11 min x 2. The box was shared with a discovery loop and
the alignment auditor (load 3-10 on 4 cores).

# sidecar-longdyad-knuckle-3r final polish on the envelope bench (2026-10-16)

Self-measured. The round-8 winner (verified 18.91, score 93.12, held out 22.67) is polished on the representative
envelope bench `env` and claimed on the held-out set and on the verified protocol through the verifier's own harness
(`docs/concepts/verify/sidecar-longdyad-knuckle-3r.py`, imported unchanged; `tools/sidecar_env_polish.py claim` only
swaps the fit bench and reads the th margin out of the same worn model). A polished config replaces the CAD's config only
after an independent verifier confirms a held-out gain >= 1 gap point AND it beats the verified config on the plain gap
and at 2 mm (the user's dominance gate, 2026-10-16 ~21:05).

**Verdict: no pick replaces the verified config.** Measured held-out gain over the verified config: +2.32 / +2.39 /
+2.45 plain when the shape is fitted on env, but **-0.31 / -0.71 / -0.55 when the shape is fitted on Bench(60,160)**,
the verified protocol's fit. The env-fit gain is an artifact of the fit protocol. Fitting the shape on env makes the
verified config itself 2.59 points worse held out (23.29 -> 25.88, priced), and the picks were tuned to that fit. The
verified config, fitted as verified, beats every pick held out under either fit (23.29 vs the best pick's 23.43). On
the verified protocol no pick passes the dominance gate. pick1 is 0.76 better plain but 3.32 worse at 1 mm and 4.60
worse at 2 mm: its gain is metal moved into the 0-2 mm shell. pick2 and pick3 lose on the plain gap. The robust gain
(the best pick's worse of the two fits) is **-0.31**. That is below the 1-point rule, so no verifier run is needed and
the verified config stays the CAD config. Cost: about $0.47 on the farm (budget $2).

## 1. The search bench: `env`, reused

The cache exists on the farm volume (`env-72d21f5aa2e5-env`, `env-fc171830d1d7-envsel`, built and validated for the
minarc polish: max fast-vs-exact error 1.86 mm, sign agreement beyond 1 mm 1.0). The draw is frozen
(`docs/research/minarc_final_polish/env_poses.npz`): the 110 clip frames of Bench(110,360) (never Wave / Walking) + 420
fresh workspace poses (env, the search bench) and an independent 360-pose draw (envsel, the pick-selection bench), each
stratified on the grid's elevation x plane x signed-axial shares, no pose within 2 deg of a held-out pose.

Distribution of the workspace poses (`docs/research/sidecar_env_polish/env_table.json`):

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead (el >= 140) | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| Bench(60,160) ws | 160 | 2.5 % | 28.1 % | 7.5 % | 16.9 % | 6.2 % | 36.2 % | 23.8 % | 26.9 % | -26.1 |
| **env** ws | 420 | **9.3 %** | 23.1 % | 7.1 % | 17.1 % | 5.9 % | 35.7 % | 24.1 % | 27.4 % | -34.0 |
| **envsel** ws | 360 | **9.7 %** | 22.8 % | 7.2 % | 16.9 % | 6.9 % | 36.1 % | 23.6 % | 26.7 % | -33.4 |

Closest fresh pose to any held-out pose: env 2.23 deg (coordinates) / 2.04 deg (humerus orientation), envsel 2.07 /
2.03; median 7.5 deg. The fit bench of the verified protocol, Bench(60,160), carries a quarter of the envelope's
extreme-axial share (2.5 % vs 9.4 %).

## 2. The rules as implemented (`tools/sidecar_env_polish.py`)

* **Model and metal:** the claim's model (`docs/concepts/models/sidecar-longdyad-knuckle-3r.py`), loaded by the
  verifier's harness, unchanged: O20 hubs everywhere, the RSSR closed per pose, the drive-range truncation, the
  harness's ball-link tilt / closure / lobe pressure-angle checks.
* **Pricing (stops as variables, >= 5.0, built +0.5).** In this family the J2 dowels are the folded dowel at
  th_lo = |a1 - a2| + smlo and the stretched dowel at the end of the slaved law, which the kit rule ends where m3e /
  msub reach the margin. The priced reading is the minarc judge's: smlo + 0.5 and the whole reading at
  CB_FOLD_MARGIN 5.5 (the stretched dowel's +0.5). K's stop B is read at the K dyad's margin at the same 5.5:
  a1max' = min(a1max, bk1 + bk2 - 5.5). The model's own k_ok refuses a1max > bk1 + bk2 - margin, and the verified
  a1max sits exactly at bk1 + bk2 - 5, so the 5.5 reading without this step closes no pose at all. smhi is the lobe's
  onset (a cam feature, not a dowel): bounded >= 5.0, unpriced.
* **Free parameters (23):** the dyad (bk1, bk2, a1max), the law (kK), the drive (r_h, beta, La, s_arm, hl, zr, r_lobe),
  the stops (smhi, smlo >= 5.0), the seats (az1, el1, az2, el2, wd, wa, b3, lc, phib) and the knee window ang_min,
  bounded below by the verified 26.88 (the knee window may not widen past what the verifier passed). Law 'lin' and
  the crank phase gam 0 stay as verified.
* **Objective** (lower is better): fit the priced config FAST on env (in-sample: the cross-fit study measured in-fold =
  out-of-fold), drop the workspace poses the continuity flood does not connect, the model's audit -> near-touch gap at
  1 mm, plus:
  * the claim-fit guard: the same config fitted FAST on Bench(60,160) and scored in-sample there;
    obj += max(0, g60 - env_near1 - 3);
  * a 2-mm shell guard (the user's 21:05 rulings): obj += max(0, env_near2 - 26.25), 26.25 = the verified config's own
    in-sample env 2-mm number. Points bought by moving metal into the 1-2 mm shell are paid back one for one;
  * +100 for a dishonest report (RSSR does not close, crest off the skirt) or a taken pose whose own-state th margin is
    under the reading's margin (checked, never fired).
* **Continuity:** the verifier's full-grid flood (minarc-stop-knuckle-4r-mechanism.py, grid "full", same law: 2-deg
  slerp edges, passive joints never step > 10 deg, actives > 25, seeds = state-A nodes) on the 1432-pose grid, plus
  every fresh env pose with K open joined to the connected grid by an edge to one of its 6 nearest connected grid
  nodes under the same law. A fresh pose with K on stop A is a seed, as in the verifier.
* **Logged, not optimised:** the env-fitted shape worn FROZEN on envsel, the pick-selection numbers.
* **th margin** (the J1-J3 angle's distance from the dyad's fold, from the member frames, the minarc remeasure's
  own-state reading: the plain dyad with K on stop A, min(m_sub, m_eff) with K open) on every taken pose.

Check of the wrapper: the claim command, unpriced at margin 5, reproduces the verified number to the digit
(fit Bench(60,160) -> Bench(110,360) exact: 18.91, near-touch 20.00 / 34.03, kNN flood 21.72, full flood 18.91;
`docs/research/sidecar_env_polish/local/claim_BEST_nominal_fit60_bench.json`). It also reads the min th margin over the
taken poses, which was not on file: **5.232 deg** (verified config, margin-5 reading; 0 poses under 5, 2 under 5.5;
the lowest is a K-open workspace pose at plane 150, elevation 30, axial -150).

## 3. Re-score of the verified config on env (step 2)

Fit env FAST -> wear env EXACT (frozen), continuity with the fresh-pose edges (`farm/rescore_BEST_*.json`):

| reading | env fit, in-sample fast (plain / 1 mm / 2 mm) | env worn exact (plain / 1 mm / 2 mm) | reach | in-band14 | in-band10 | contact | overhead | min th |
|---|---|---|---|---|---|---|---|---|
| priced (smlo 5.5, margin 5.5, a1max 62.68) | 20.69 / 21.64 / 26.25 | **20.55** / 22.46 / 30.87 | 0.729 | 0.873 | 0.482 | 0.007 | 10/30 | 6.04 |
| unpriced (margin 5, as verified) | 20.21 / 21.16 / 25.76 | 20.07 / 21.97 / 30.37 | 0.733 | 0.873 | 0.482 | 0.007 | 10/30 | 5.36 |

Next to the verified 18.91 / 20.00 / 34.03 (fit Bench(60,160) -> Bench(110,360)) and held out 22.67 / 25.75 / 37.24.
* Pricing costs the verified config 0.48 plain on env (fold 99 -> 101 lost workspace poses).
* env predicts the held-out plain gap within 2.1 points (20.55 vs 22.67); Bench(110,360) is 3.8 off. The 2-mm number
  does not transfer: 30.87 on env vs 37.24 held out.
* Continuity: 1017 grid nodes close, every K-open grid node connected (400 / 400); all 306 taken fresh poses joined
  (129 with K open), 0 dropped.

## 4. The polish (step 3)

Farm, 8 CMA runs from the verified config, popsize 8, 2 processes each, patience 12 generations, budget 2400 s
(`farm/cma_scp-*.json`). 1216 configurations, 0 errors, 9-14 s each. 145 closed no pose (objective 400).

| run | sigma (start -> end) | evals | stop | best objective (row) | its envsel near 1 mm / 2 mm / plain |
|---|---|---|---|---|---|
| s1 | 0.3 -> 0.241 | 121 | no gain > 0.02 in 12 generations | 19.71 (g3-1) | 24.58 / 30.85 / 22.36 |
| s2 | 0.3 -> 0.155 | 201 | same | 20.20 (g13-5) | **22.86 / 29.94 / 21.21** |
| s3 | 0.3 -> 0.188 | 193 | same | 20.48 (g12-0) | 23.41 / 30.17 / 21.76 |
| s4 | 0.3 -> 0.197 | 225 | same | **19.64** (g16-5) | 24.19 / 32.38 / 22.53 |
| w5 | 0.5 -> 0.409 | 97 | same | 21.64 (x0) | 23.64 / 31.28 / 22.54 |
| w6 | 0.5 -> 0.362 | 185 | same | 21.12 (g11-5) | 25.06 / 30.14 / 23.60 |
| w7 | 0.5 -> 0.417 | 97 | same | 21.64 (x0) | 23.64 / 31.28 / 22.54 |
| w8 | 0.6 -> 0.442 | 97 | same | 21.64 (x0) | 23.64 / 31.28 / 22.54 |
| verified (x0) | | | | 21.64 | 23.64 / 31.28 / 22.54 |

**Convergence gate** (`tools/sidecar_env_polish.py gate`): combined over all 1216 tries in generation order, the best
gained 0.07 over the second half and 0.07 over the last third, top 5 within 0.39: **passes**. Per run it passes on 7 of
8 (w5: top-5 spread 3.31). Every run stopped on the patience rule well inside its budget; sigma did not collapse
(0.16-0.44). Three wide runs (sigma 0.5-0.6) never beat the verified config in 97 tries: the verified config sits in a
narrow basin of this objective.

**Selection on noise is the size of the gain.** Over the 969 rows that closed, the env objective and the envsel
near-touch correlate at 0.85 (plain 0.96, 2 mm 0.97): the two draws agree on the coarse landscape. At the top they do
not: the 40 best rows by the objective average 20.53 in-sample but 24.32 on envsel, 0.68 WORSE than the verified
config's 23.64. The objective's best (s4-g16-5, 19.64) is 0.55 worse on envsel. 50 rows beat the verified config on
envsel at 1 mm, 34 of them also at 2 mm, 27 also on the plain gap.

**Picks** (registered on envsel and committed in 604a8ae before the claim batch ran): candidates = the best 15 rows by
the objective of each run; a candidate may not be worse than the verified config at 2 mm on envsel (the dominance
gate's 2-mm half, read before any held-out number); ranked by the envsel 1-mm number; the top 3 that differ by >= 0.5
CMA scale units in some parameter (`docs/research/sidecar_env_polish/picks/`).

| pick | row | objective (env 1 mm) | env plain / 2 mm | envsel 1 mm / 2 mm / plain | Bench(60,160) in-sample 1 mm |
|---|---|---|---|---|---|
| verified | x0 | 21.64 | 20.69 / 26.25 | 23.64 / 31.28 / 22.54 | 12.08 |
| pick1 | s2-g13-5 | 20.20 | 19.24 / 25.30 | 22.86 / 29.94 / 21.21 | 16.04 |
| pick2 | s3-g12-0 | 20.48 (env 1 mm 20.21 + shell 0.27) | 19.73 / 26.52 | 23.41 / 30.17 / 21.76 | 13.53 |
| pick3 | s4-g19-4 | 20.03 (env 1 mm 19.78 + shell 0.25) | 19.31 / 26.50 | 23.47 / 29.62 / 21.82 | 14.66 |

What moved (nominal; the claim prices them). All small: the polish stays in the verified basin.

| key | verified | pick1 | pick2 | pick3 |
|---|---|---|---|---|
| bk1 / bk2 / a1max | 28.94 / 39.24 / 63.18 | 29.56 / 38.09 / 62.67 | 28.93 / 39.84 / 62.66 | 28.92 / 40.07 / 61.34 |
| kK | 1.623 | 1.691 | 1.648 | 1.388 |
| r_h / beta | 14.87 / -86.4 | 15.16 / -87.2 | 15.27 / -85.0 | 15.96 / -89.2 |
| La / s_arm | 16.55 / 4.39 | 17.36 / 4.28 | 16.22 / 4.47 | 15.41 / 4.15 |
| hl / zr / r_lobe | 3.15 / 0.00 / 7.74 | 3.04 / 0.32 / 7.85 | 3.02 / 0.34 / 7.68 | 2.84 / 0.41 / 7.75 |
| smhi / smlo (nominal; smlo built +0.5) | 16.55 / 5.00 | 16.96 / 5.03 | 16.10 / 5.47 | 17.93 / 5.01 |
| az1 / el1 | 96.70 / 67.59 | 97.02 / 67.06 | 95.66 / 67.06 | 96.06 / 67.30 |
| az2 / el2 | 42.20 / 44.42 | 42.05 / 44.61 | 40.97 / 44.21 | 41.13 / 44.42 |
| wd / wa / b3 | 67.50 / -7.32 / 0.345 | 68.65 / -7.56 / 0.333 | 66.82 / -7.86 / 0.332 | 67.31 / -7.33 / 0.326 |
| ang_min / lc / phib | 26.88 / 25.69 / -60.70 | 27.14 / 24.86 / -56.45 | 27.22 / 25.50 / -59.45 | 27.47 / 25.23 / -57.31 |

Common moves: the horn radius r_h +0.3..1.1 mm (toward the 15.5 mm the verifier's red team asked for at the horn
socket vs hub K), the arm joggle zr +0.3..0.4 mm, phib +1..4 deg, ang_min +0.3..0.6 (a narrower knee window).

## 5. The claim (step 4)

**Batch 1** (`farm/jobs_claim.json`, 10 jobs): the 3 picks and the verified config, each on two protocols, priced:
* fit env FAST -> wear the 1154 held-out poses EXACT;
* fit Bench(60,160) FAST -> wear Bench(110,360) EXACT (the verified protocol).
The batch also ran the unpriced margin-5 reading of the verified config and pick1 on env -> held.

**Batch 2** (`farm/jobs_claim2.json`, 5 jobs) was needed once batch 1 showed the env fit penalising the verified
config. It ran all 4 configs fit Bench(60,160) -> held out, priced: the fit protocol of the verified held-out
22.67. It also ran pick1 unpriced on the same protocol. The picks were fixed before either batch ran.

Each cell gives gap / near-touch 1 mm / near-touch 2 mm. All runs use the verifier's harness with its continuity flood
fill: 0 taken poses dropped by the full-grid flood in every run, and 0 poses failing its added checks (RSSR closure,
ball-link tilt <= 30, lobe pressure angle <= 45).

| config | fit env -> held out | fit Bench(60,160) -> Bench(110,360) (verified protocol) | fit Bench(60,160) -> held out |
|---|---|---|---|
| verified, priced | 25.88 / 26.54 / 36.04 | **19.36** / 20.45 / 34.63 (score 92.96) | **23.29** / 26.39 / 38.29 |
| verified, unpriced (margin 5) | 25.14 / 25.80 / 35.25 | 18.91 / 20.00 / 34.03 (= verified, reproduced) | 22.67 / 25.75 / 37.24 (verifier) |
| pick1 (s2-g13-5), priced | 23.56 / 25.33 / 35.29 | 18.60 / **23.77** / **39.23** | 23.60 / 27.90 / 44.48 |
| pick1, unpriced (margin 5) | 22.82 / 24.81 / 34.71 | - | 22.67 / 25.98 / 35.04 |
| pick2 (s3-g12-0), priced | 23.49 / 24.60 / 35.20 | 20.43 / 21.35 / 31.52 | 24.00 / 27.22 / 33.70 |
| pick3 (s4-g19-4), priced | 23.43 / 24.90 / 33.12 | 21.03 / 23.22 / 41.96 | 23.84 / 27.35 / 43.68 |

Gain over the verified config on the same protocol and pricing (positive = better):

| pick | held out, fit env (plain / 1 mm / 2 mm) | held out, fit Bench(60,160) | verified protocol, Bench(110,360) | dominance gate (plain AND 2 mm, verified protocol) |
|---|---|---|---|---|
| pick1 | +2.32 / +1.21 / +0.75 | **-0.31** / -1.51 / -6.19 | +0.76 / -3.32 / -4.60 | fails (2 mm -4.60; 12 poses < 1 mm, min metal 0.07 mm) |
| pick2 | +2.39 / +1.94 / +0.84 | -0.71 / -0.83 / +4.59 | -1.07 / -0.90 / +3.11 | fails (plain -1.07) |
| pick3 | +2.45 / +1.64 / +2.92 | -0.55 / -0.96 / -5.39 | -1.67 / -2.77 / -7.33 | fails (plain and 2 mm) |

**Why the env-fit gain is not a design gain.** In the minarc polish the env fit improved BDp's held-out number
(24.18 -> 23.68). Here it does the opposite. The verified config fitted on env loses in-band held out (0.871 vs
0.896 fitted on Bench(60,160)), at equal reach (0.680 both, priced). The picks recover the
in-band under the env fit (0.892) but not under the Bench(60,160) fit (0.888-0.898). Whether a fitted shape travels
depends on the design, not only on the bench. The CAD builds one shape. Compared at the best fit of each config, the
verified config (23.29) beats every pick (best 23.43, pick3 on the env fit).

**Components of the decisive comparison** (fit Bench(60,160) -> held out, priced). Each cell gives reach /
in-band14 / in-band10 / contact / overhead / kNN-connected gap:
* verified: 0.680 / 0.896 / 0.536 / 0.008 / 17/71 / 30.92;
* pick1: 0.675 / 0.898 / 0.542 / 0.009 / 14/71 / 31.14;
* pick2: 0.682 / 0.888 / 0.532 / 0.009 / 18/71 / 30.58;
* pick3: 0.680 / 0.890 / 0.537 / 0.008 / 17/71 / 31.47.

Reach does not move. The polish found no fold relief, so the fold (266-268 of 952 held-out workspace poses) is still
the limiter.

**Rules on every claimed run:**
* **th margin** (own state, from the member frames): the min over taken poses is 5.50-6.09 deg on every priced run,
  with 0 poses under the 5.5 priced rule. The verified config's min th margin under the verified reading (margin 5,
  nominal stops) is **5.232** on Bench(110,360), 0 poses under 5. Unpriced env -> held gives 5.021 (verified) and
  5.087 (pick1).
* **Continuity:** the full-grid flood fill keeps the static number in every run (0 dropped). The kNN graph gives
  23.01 (verified), 21.95 / 24.09 / 24.40 (picks) on the verified protocol and 30.58-31.47 held out (verified
  30.92).
* **Drive:** taken K opening dK 33.7-37.6 deg, inside each config's drive range (35.8-45.8). The range ends at
  ROD-hub2 for the verified config, pick2 and pick3, and at the transmission limit for pick1. Transmission >= 38.1
  deg; ball-link tilt <= 23.8 deg (<= 30); lobe pressure angle <= 41.9 deg (<= 45).
* **O20** at every hub (the model's hubs, unchanged). The J1 seat moves less than 1.1 deg in azimuth and 0.6 deg in
  elevation in every pick.

**The pricing as a measurement change** (not a design change): reading the verified config with built stops (smlo
5.5, margin 5.5, a1max 62.68) costs 0.45 on the verified bench (18.91 -> 19.36, score 93.12 -> 92.96) and 0.62 held
out (22.67 -> 23.29). The min th margin rises 5.23 -> 5.51.

## 6. What this measured, and what happens next

1. **The verified config stays the CAD config** (gen-6 CAD on `best_params`). Its built-stop reading belongs on the
   row: 19.36 priced (score 92.96), held out 23.29, min th margin 5.232 unpriced / 5.513 priced.
2. **A final-polish objective must fit the shape the CAD will build.** The env bench was built to fix the workspace
   sample, and it does: env predicts held out within 2.1 points vs Bench(110,360)'s 3.8. But scoring the polish
   in-sample on an env-fitted shape optimises a shape protocol the claim does not use. The next polish objective:
   fit the shape on the claim's fit bench (Bench(60,160)), wear it FROZEN on env (fast), and select on envsel the same
   way. That is the claim's own protocol on a representative sample.
3. **Selection on noise again sets the size of the in-sample gain.** The top 40 rows average 20.53 in-sample against
   24.32 on envsel, worse than the verified config's 23.64. The envsel filter (1 mm rank, 2 mm guard) did its job:
   all 3 picks beat the verified config on envsel at both thresholds, and on the env-fit held-out protocol at all
   three numbers.
4. **The basin is narrow.** Wide CMA runs (sigma 0.5-0.6) found nothing better than the verified config in 97 tries
   each. The losses are fold (86-91 of 360 on the bench), and parameter polish does not move reach. The reach lever is
   the a2 / J3 re-seat named in the row (twist-long-a2 on this drive and dyad), not a polish.
5. **For the CAD.** Every pick moved the horn radius r_h up (15.2-16.0 vs 14.87). That is toward the >= 15.5 mm the
   verifier's red team asked for at the M2 socket vs hub K (1.37 mm). A single-parameter check, r_h 15.5 on the
   verified config through this claim harness, is the cheap next measurement before the CAD fixes the horn.

## Cost

Farm exo-cpu1 (cpu3c $0.288 / worker-h; cpu5c about 15 % more):

| batch | billed | $ (cpu3c / cpu5c) |
|---|---|---|
| CMA 8 runs + re-score x2 | 3562 worker-s | 0.285 / 0.332 |
| claim batch 1 (10 jobs) | 1563 worker-s | 0.125 / 0.146 |
| claim batch 2 (5 jobs) | 751 worker-s | 0.060 / 0.070 |
| **total** | | **about $0.47 / $0.55** (+ cold starts; budget $2.00) |

Local: 1 process at a time (smoke test, the reproduction of 18.91).

## Files

* `tools/sidecar_env_polish.py`: the objective, the priced reading, the full-grid flood with fresh-pose edges, the CMA
  driver (tools/crossfit_polish.py's), picks, gate, re-score and the claim wrapper around the verifier's harness.
* `docs/research/sidecar_env_polish/env_table.json`: the distribution table.
* `docs/research/sidecar_env_polish/farm/`: job files, CMA rows (`cma_scp-*.json` + state + log), the re-scores
  (`rescore_BEST_*`) and the claims (`claim_*`, `claim2_*`).
* `docs/research/sidecar_env_polish/picks/`: pick1-3, nominal free parameters + the full config (the claim prices
  them).
* `docs/research/sidecar_env_polish/local/claim_BEST_nominal_fit60_bench.json`: the wrapper's reproduction of the
  verified 18.91.


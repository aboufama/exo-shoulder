# minarc BDp final polish on a representative envelope bench (2026-10-16)

Self-measured. Every held-out number below comes from the minarc judge's own harness
(`docs/concepts/verify/minarc-bdp-remeasure.py`, imported unchanged) with the judge's built-stop pricing; only the
benches are swapped (`tools/env_polish.py claim`). A config replaces BDp's CAD config only after an independent
verifier confirms a held-out gain of at least 1 gap point (CLAUDE.md final-polish rule).

## Why

Every polish so far lost about 5 points held out. The cross-fit study (`docs/research/crossfit_polish.md`) measured
the cause: the search benches pick their workspace poses by `linspace` over the grid order, which under-samples axial
rotation (|axial| >= 150 deg is 6-7.5 % of the bench vs 11 % of the held-out set). A polish then buys closure on the
bench that turns into skin contact elsewhere. The fix is a search bench drawn from the whole workspace envelope.

## 1. The bench: `env` (tools/env_bench.py)

**The envelope.** The one the workspace grid samples (`pipeline/conformal/gpu_client/pack_envelope.py --functional`):
* plane -90..150, elevation 0..170, humeral rotation r = axial + plane -90..90;
* inside `rt_common.plausible` (elevation ceiling per plane) and the functional rotation limits.

The grid is this envelope on a 15-deg lattice (1432 poses).

**The draw** (seeded, deterministic; `python3 tools/env_bench.py make`):
* **Cells.** Every grid pose owns its 15-deg cell (plane / elevation / r +- 7.5, clipped to the box). A fresh pose is
  uniform inside a cell and must satisfy the envelope law.
* **Strata on the drawn pose's own values.** Elevation band x plane band x signed axial band (edges -150 -90 -45 0 45
  90 150). The quotas are the grid's shares (largest remainder).
  * Why not one draw per random cell: the grid is lattice-weighted. Its boundary rows (e.g. |axial| 150-180 at the
    plane / rotation limits) carry full weight, and the held-out set is a subset of that grid.
  * A plain uniform draw in the continuous envelope under-samples those rows again. Measured on the first version:
    6.7 % |axial| >= 150 vs the grid's 9.4 %.
  * Two lattice-edge strata have almost no continuous volume (e.g. elevation < 45, plane 0-60, axial +90..150 needs
    r = 90 and plane = 0 exactly). After 3000 tries they accept a draw from their own cells: 2 poses per draw.
* **The held-out set stays held out.** A draw is rejected if it lies within 2 deg of any held-out pose (the verifier's
  1154: every fit-clip frame and workspace pose outside Bench(110,360) and Bench(60,160)). The test is twice:
  * in each coordinate (Chebyshev on plane / elevation / axial, axial wrapped);
  * in humerus orientation (geodesic), which catches the low-elevation degeneracy of plane vs axial.

  Draws within 2 deg of an already drawn pose are also rejected, so env and envsel are disjoint. The lead's ruling:
  fresh draws near held-out poses are fine; reusing or near-duplicating them is not.
  * Rejected: env 5 by coordinates + 2 by orientation, envsel 10 + 4.
  * Closest fresh pose to any held-out pose: env 2.23 deg (coordinates) / 2.04 deg (orientation), envsel 2.07 / 2.03.
  * Median orientation distance to the nearest held-out pose: 7.5 deg.
* **Frames.** Each fresh pose gets the rig's frames exactly as the grid does: `design_search` Ry Rx Ry + scapula
  rhythm, elbow 90, forearm neutral (HG rebuild error on the grid 3e-8).
* **Benches.** The 110 clip frames of Bench(110,360) (never Wave / Walking) + the fresh workspace poses.
  * **env**: 420 poses (seed 1), the search bench.
  * **envsel**: 360 poses (seed 2), the pick-selection bench (fit env -> wear envsel frozen). CMA selects on the noise
    of a fixed pool, so the picks are ranked on an independent draw.
* **Installation.** `tools/env_bench.py install()` appends the draws to `concept_bench._poses_all()` under a new clip
  name. They are not a fit clip and not the grid, so every grid, held-out and clip computation is unchanged.

**The table** (workspace poses only; `docs/research/minarc_final_polish/env_table.json`):

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead (el >= 140) | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| Bench(60,160) ws | 160 | 2.5 % | 28.1 % | 7.5 % | 16.9 % | 6.3 % | 36.3 % | 23.8 % | 26.9 % | -26.1 |
| **env** ws | 420 | **9.3 %** | 23.1 % | 7.1 % | 17.1 % | 6.0 % | 35.7 % | 24.0 % | 27.4 % | -34.0 |
| **envsel** ws | 360 | **9.7 %** | 22.8 % | 7.2 % | 16.9 % | 6.9 % | 36.1 % | 23.6 % | 26.7 % | -33.4 |

(The axial -90..-45 share in `crossfit_polish.md` was 33.1 % for the pool; it counted a different band.) env and
envsel match the full grid within sampling error on every band.

Note: the held-out set is the grid MINUS the linspace benches. So it is skewed the OTHER way (11.0 % vs the grid's
9.4 %): it carries the extremes the benches lack. A representative sample of the envelope predicts the grid, not that
complement exactly.

**Fast caches** (farm; `tools/env_bench.py jobs / assemble / validate / use`):
* The same grids as `concept_bench --build` (same `_grid_pose`), 14 part jobs: 530 + 470 poses, wall 9.5 min (queued
  behind other agents), $0.10.
* Validation against the exact path (12 poses, ~17k points within 20 mm of the skin):
  * env: max error 1.86 mm, p99 1.14 mm, mean 0.12 mm, sign agreement beyond 1 mm 1.0;
  * envsel: 1.94 / 1.16 / 0.12 mm, sign agreement 0.99986.
* Keys `env-72d21f5aa2e5-env`, `env-fc171830d1d7-envsel`, on the farm volume.

**Sampling noise is the size of the effect.** The kinematic closure share (fold window + knee + closure, the flood
fill's node law) per pose set:

| config | Bench(110,360) ws | env | envsel | full grid | held out ws |
|---|---|---|---|---|---|
| BDp (priced stops) | 0.733 | 0.731 | 0.706 | 0.719 | 0.704 |
| H1 | 0.689 | 0.691 | 0.667 | 0.675 | 0.658 |

(`docs/research/minarc_final_polish/kin_closure.json`, Bench(60,160) knee reference, run at CB_FOLD_MARGIN 5.5.)
* The binomial standard error of a 420-pose share is about 0.022, i.e. about 2 reach points = 2 gap points. env and
  envsel differ by 2.5 points: both are fair draws of the envelope, and their spread IS that noise.
* Bench(110,360)'s closure surplus over held out (2.9 / 3.1 points) is about 1.3 standard errors. The skew is real
  (the axial table), but a 420-pose bench cannot resolve it better than about +- 2 points.

## 2. Does `env` predict held out better than Bench(110,360)?

Re-scored through the judge's harness: fit FAST on the protocol's fit bench, worn EXACT, frozen shape, continuity on.
BDp carries the judge's built-stop pricing (stops 5.5, stop B at dK 34.47, CB_FOLD_MARGIN 5.5). H1 is unpriced at
margin 5, as in the judge's ruling. Outputs: `farm/rescore_*`.

| config | protocol | search-bench number (gap / near-touch) | held out, 1154 poses (gap / near-touch) | bench -> held drop |
|---|---|---|---|---|
| BDp | fit Bench(60,160) -> wear Bench(110,360) (the verified protocol; judge) | 19.54 / 26.44 | 24.18 / 28.86 | **+4.64** |
| BDp | fit env -> wear env | 22.32 / 24.75 | 23.68 / 26.87 | **+1.36** |
| H1 | fit Bench(60,160) -> wear Bench(110,360) (judge) | 27.20 / 31.75 | 31.39 / 34.66 | **+4.19** |
| H1 | fit env -> wear env | 24.87 / 27.69 | 30.04 / 32.83 | **+5.17** |

**Verdict: not a reliable improvement as a predictor.**
* BDp: env predicts its held-out number within 1.4 points (Bench(110,360): 4.6).
* H1: env is off by 5.2 points (Bench(110,360): 4.2). Its reach on env is 0.674 vs 0.627 held out, which matches its
  kinematic closure: 0.691 on env vs 0.658 held out.
* Mean absolute error: env 3.3, Bench(110,360) 4.4. With two configs and a 2-point sampling error per 420-pose draw,
  this difference is noise.
* The ranking is compressed. The BDp - H1 difference is 6.4 points held out (fit env), 2.6 on env and 7.7 on
  Bench(110,360).

The reach term carries the drop: env over held-out reach is +1.96 points for BDp and +4.67 for H1. In-band and follow
agree within 0.3 points. Contact moves the other way for BDp (-0.9). That is the ~2-point binomial noise of a 420-pose
reach share, plus the held-out set's own skew (see the table above).

**Measurement change, not a design change.** Fitting the shape on env instead of Bench(60,160) lowers the held-out
gap of both configs:
* BDp 24.18 -> 23.68 (-0.50);
* H1 31.39 -> 30.04 (-1.35).

A shape fitted on more, representative workspace poses travels better. The claim below compares every config,
BDp included, on the same protocol.

**Rules on the re-score.**
* Own-state J1-J3 margin: min 5.505 (env) / 5.525 (held), 0 poses under the rule.
* Continuity: grid 1024 / 1024 nodes connected, 0 islands, 898 / 898 edges. The fresh env poses joined the
  connected grid by edges for 305 / 420; the other 115 are not closed nodes. 0 taken poses dropped.
* Overhead workspace taken: 6 / 30 on env, 17 / 71 held out.

## 3. The polish

**Objective** (`tools/env_polish.py`, lower is better; the crossfit tool's minarc plug-in and CMA driver, patched to
this objective):
1. The plug-in's `full(p)`: O20 hubs, stops smhi / smlo >= 5.0 (the user's floor) as variables, knee window ang_min
   >= BDp's 24.95. docs/research/knee_window shows the window at H1's 30.46 changes nothing for BDp, so BDp's bound
   holds.
2. **Priced like the judge.**
   * Each J2 stop is drawn s +0.5 / -0. Its worst built case s + 0.5 is read with the all-state rule at 5.5
     (CB_FOLD_MARGIN 5.5), as in the judge's m5p5 runs.
   * K's stop B is drawn where the 5-deg rule cuts the stretched branch: a1max' = min(a1max, a1max at the cut). The cut
     comes from the buildability lens' equilibrium scan, at margin 5 with the nominal stops.
   * For BDp this reproduces the judge's priced parameters: cut at th 108.5, dK 34.47, a1max 54.748 (judge 54.748).
3. Fit FAST on env, in-sample. The cross-fit study measured in-fold = out-of-fold, so on a representative sample the
   in-sample score is the right one.
4. **Continuity.** The crossfit tool's vectorised flood fill on the 1432-pose grid (the verifier's law). Each fresh pose
   is joined to the connected grid by a 2-deg slerp edge to one of its 6 nearest connected grid nodes. The same law
   applies: every sample closes, no joint step > 10 deg, knee branch constant and equal to the seeds'.
5. The claim harness's knock-outs. The score is the near-touch gap (metal < 1 mm = contact).
6. **Claim-fit guard.** The same config fitted on Bench(60,160) (the verified protocol's fit) is scored in-sample;
   obj += max(0, g60_near - env_near - 3). It fired on 27 of the 787 rows; 10 more closed no pose at all (objective 400).
7. **Logged, not optimised.** The env-fitted shape worn FROZEN on envsel: the pick-selection number.

**Run.**
* Farm: 3 CMA starts x 8 processes, popsize 8, sigma 0.4, patience 10 generations, budget 1500 s, at most 640
  evaluations.
* Starts:
  * BDp;
  * BDp with the F2 seats + knee (crossfit refs.json; ang_min raised to 24.95);
  * BDp with the F7 seats + knee.
* 787 evaluations, 0 errors, about 16-27 s per generation of 8.

| start | evals | stop | x0 objective (env near) / envsel near | best objective | its envsel near / plain | best envsel near among the start's top 15 |
|---|---|---|---|---|---|---|
| BDp | 145 | no gain > 0.02 in 10 generations (sigma 0.31) | 24.98 / 29.13 | 20.83 (g8-4) | 24.52 / 23.43 | 23.93 (g15-7) |
| F2 | 337 | same (sigma 0.13) | 26.24 / 28.62 | 21.83 (g32-6) | 27.31 / 24.57 | 27.31 |
| F7 | 305 | same (sigma 0.21) | 24.14 / 26.69 | **18.02** (g28-4) | 24.76 / 21.57 | 23.58 (g35-6) |

**Convergence gate.** Every start stopped on the patience rule, well inside its budget, but sigma did not collapse
(0.13-0.31). The best value of the last third of each run vs the first two thirds:
* BDp: +0.00;
* F2: -0.38;
* F7: -1.05.

The three starts end in different basins (18.0 / 20.8 / 21.8). This is a multi-start local optimum, not a global
one. Sampling noise also blunts the objective: the env in-sample gain over BDp is 6.96 for the F7 best, but its gain on
the independent envsel draw is only 4.37 (near-touch).

**Picks.** The candidates are the best 15 rows by the objective of each start. They are ranked by the envsel
near-touch number, and the top 3 that differ by >= 1 CMA step in some parameter are kept
(`docs/research/minarc_final_polish/picks/`):

| pick | row | objective (env near) | envsel near / plain | Bench(60,160) in-sample near | J1 seat (anterior, up) |
|---|---|---|---|---|---|
| BDp | - | 24.98 | 29.13 / 24.29 | 15.29 | 0.036, 0.925 |
| pick1 | F7-g35-6 | 18.93 | 23.58 / 21.98 | 15.94 | 0.076, 0.926 |
| pick2 | BDp-g15-7 | 22.25 | 23.93 / 22.85 | 14.47 | 0.002, 0.931 |
| pick3 | BDp-g9-5 | 22.51 | 24.04 / 22.40 | 13.44 | 0.016, 0.933 |

(H1's J1 seat: anterior 0.085, accepted. All picks sit on the acromion top.)

**What moved.** The stops as variables went to 5.1-6.9 deg. Smaller common moves: J2 seat az2 +1.5..6, hub 3 ->
pin a lE +2..9 mm, knee window ang_min 25.1-26.1.

| key | BDp | pick1 | pick2 | pick3 |
|---|---|---|---|---|
| az1 / el1 | 95.47 / 67.70 | 101.64 / 67.86 | 90.34 / 68.59 | 92.57 / 68.98 |
| az2 / el2 | 47.21 / 39.89 | 48.69 / 42.04 | 49.58 / 40.23 | 53.23 / 42.24 |
| wd / wa / b3 | 59.82 / -9.03 / 0.458 | 66.60 / -9.63 / 0.335 | 58.91 / -6.66 / 0.416 | 57.96 / -8.15 / 0.373 |
| lE / lc | 64.66 / 30.39 | 73.87 / 28.70 | 67.27 / 31.55 | 66.43 / 28.55 |
| phiE / phib | -1.54 / -69.76 | 1.36 / -53.15 | 5.46 / -64.54 | -1.26 / -64.57 |
| ang_min / stk | 24.95 / 5.27 | 26.15 / 5.79 | 26.01 / 5.23 | 25.10 / 5.47 |
| bk1 / bk2 / a1max | 30.16 / 47.01 / 66.16 | 33.81 / 47.89 / 68.01 | 30.55 / 48.62 / 63.72 | 28.50 / 44.46 / 64.80 |
| smhi / smlo (nominal; built +0.5) | 5.0 / 5.0 | 6.88 / 6.83 | 5.77 / 5.10 | 6.04 / 5.62 |

## 4. The claim

**One farm batch** (`farm/jobs_claim.json`): the 3 picks + BDp, each on 2 protocols. The judge's harness was used,
imported unchanged, with the judge's built-stop pricing (`tools/env_polish.py claim`):
* fit env FAST -> wear the 1154 held-out poses EXACT;
* fit Bench(60,160) FAST -> wear Bench(110,360) EXACT (the verified protocol).

**Follow-up batch** (`farm/jobs_claim2.json`):
* pick1 fit Bench(60,160) -> held out, priced: the protocol of BDp's verified 24.18;
* the unpriced readings at margin 5 (nominal stops, stop B as designed), to check that the priced reading is the
  worst.

Outputs: `farm/claim_*.json`, `farm/claim2_*.json`.

| config | fit env -> held out (gap / near) | fit 60 -> Bench(110,360) (gap / near) | fit 60 -> held out (gap / near) | held-out gain over BDp (env fit / fit 60) |
|---|---|---|---|---|
| BDp (priced) | 23.68 / 26.87 | **19.54** / 26.44 (= the judge's verified number, to the digit) | 24.18 / 28.86 (judge) | - |
| **pick1** F7-g35-6 (priced) | **21.31 / 23.02** | **18.40 / 23.36** (score 93.31) | **22.69 / 26.73** | **+2.37 / +1.49** (near-touch +3.85 / +2.13) |
| pick2 BDp-g15-7 (priced) | 23.68 / 25.66 | 21.42 / 23.02 | - | 0.00 / - |
| pick3 BDp-g9-5 (priced) | 24.51 / 26.51 | 21.77 / 24.47 | - | -0.83 / - |
| BDp (unpriced, margin 5) | 22.85 / 26.00 | 19.06 (judge) | 23.24 (judge) | - |
| pick1 (unpriced, margin 5) | 20.91 / 21.97 | 17.77 / 22.82 | - | - |

For both configs the priced reading is the worse one, so the priced number is the claim. On the verified bench
protocol, pick1 gains 1.14 (19.54 -> 18.40).

**pick1 under the rules** (both protocols):
* Own-state J1-J3 margin: min 5.586 (held) / 5.623 (bench) against the 5.5 priced rule; 0 poses under it.
* Q2 slot, K one-sided, spring equilibrium: 0 knocked out; 0 forced poses with a lower equilibrium.
* Continuity: grid 1106 / 1106 nodes connected, 0 islands, 991 / 991 edges, 0 taken poses dropped. The overhead
  grid nodes rise from 32 to 44.
* O20 everywhere. J1 seat on the acromion top: anterior 0.076, up 0.926; H1's accepted seat has anterior 0.085.
* Priced stops: J2 slot drawn at 6.88 / 6.83 deg (built +0.5). K's stop B is drawn at the 5-deg rule cut, dK 56.65
  deg (th 118.9; the as-designed stop B is at dK 60.42).

**Components, held out** (env fit, priced; pick1 vs BDp):
* reach 0.728 vs 0.683 (+4.5 points);
* follow 1.0 vs 1.0;
* in-band 2-14 0.889 vs 0.891;
* in-band 2-10 0.497 vs 0.574 (R1-aim worse);
* contact 0.030 vs 0.011 (+1.9 points);
* near-touch poses 8 vs 20.

The gain is reach, partly paid back in skin contact.

**Red team (open; for the verifier).**
* **Skin contact roughly triples.** 3.0-3.8 % of taken poses put metal inside the body, against BDp's 1.1 %. The gap
  counts those poses as not taken, but "zero contact" is a hard bench target. Where they are (clip vs workspace,
  which part) is not attributed here.
* **K swings almost twice as far.** dK reaches 56.6 deg vs BDp's 34.1; 213 vs 141 held-out poses sit in the
  stretched state. The clock spring then winds further: the buildability lens sized BDp's spring for its stop B at
  34.5 deg. The forced sub-chain's J1 swing per frame, already flagged for BDp (20-40 deg / frame before stop B), needs
  re-measuring.
* **R1-aim drops.** In-band 2-10 mm falls from 0.57 to 0.50.
* **Selection.** pick1 was chosen on envsel, a draw independent of the search. The held-out set was read only by
  this claim batch, once, for 4 configs. Its in-sample env objective (18.93) still overstates its held-out
  near-touch (23.02) by 4.1 points.

**What the envsel draw bought.** Both the search objective and the pick-selection number rank the 4 claimed configs
in their held-out order, but only the selection number is calibrated:

| config | env objective (in-sample near) | envsel near (independent draw) | held near (env fit) |
|---|---|---|---|
| pick1 | 18.93 | 23.58 | 23.02 |
| pick2 | 22.25 | 23.93 | 25.66 |
| pick3 | 22.51 | 24.04 | 26.51 |
| BDp | 24.98 | 29.13 | 26.87 |

* The in-sample objective is optimistic for every config (by 1.9 for BDp and 3.4-4.1 for the polished ones): the
  selection-on-noise effect the cross-fit check predicted.
* The envsel number misses by 0.6-2.5 in both directions (mean 1.75).
* **An independent draw for pick selection is the part of this instrument that works.** The representative sample
  alone does not stop the in-sample optimism of a polish.

**Verdict.**
* pick1 gains **+2.37** gap points held out over BDp on the env-fit protocol, and **+1.49** on BDp's own verified
  protocol (fit Bench(60,160)).
* It gains +1.14 on the verified bench protocol (19.54 -> 18.40, score 92.89 -> 93.31).
* Self-measured. Under the CLAUDE.md final-polish rule, pick1 replaces BDp's CAD config only after an independent
  verifier confirms the >= 1 held-out gain and clears the red-team items above (contact, K travel, spring).
* pick2 and pick3 do not beat BDp held out.
* Params: `docs/research/minarc_final_polish/picks/pick1.json` (nominal; the claim prices it).

## Cost

Farm exo-cpu1 (cpu3c rate, $0.288 / worker-h; the cpu5c fallback is about 15 % more):

| batch | billed | $ |
|---|---|---|
| fast caches env + envsel (14 parts) | 1245 worker-s | 0.100 |
| assemble + validate | 48 worker-s | 0.004 |
| CMA 3 starts + re-score 4 | 2468 worker-s | 0.198 |
| claim, 8 jobs | 1995 worker-s | 0.160 |
| claim follow-up, 4 jobs | 1523 worker-s | 0.122 |
| **total** | | **about $0.58** (cpu5c up to $0.67; budget $2.00) |

The RunPod balance went from $6.91 to $6.08 over the session, shared with other agents. Local work: at most 1
process.

## Files

* `tools/env_bench.py` - the draw, the table, the farm cache (parts / assemble / validate / use).
* `tools/env_polish.py` - the objective, the CMA driver (tools/crossfit_polish.py's, patched), the stop pricing, the
  fresh-pose continuity, the claim wrapper.
* `docs/research/minarc_final_polish/env_poses.npz` - both draws (poses, humerus / scapula frames, source cell).
  It is frozen: the fast-cache key hashes the pose indices, so a redraw needs a new cache.
* `docs/research/minarc_final_polish/env_table.json` - the distribution table.
* `docs/research/minarc_final_polish/farm/` - job files, CMA rows (`cma_envp-*.json`), re-score and claim outputs.
* `docs/research/minarc_final_polish/picks/` - the picks' nominal parameters (the claim prices them).

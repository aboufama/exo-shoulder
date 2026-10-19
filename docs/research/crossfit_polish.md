# Cross-fit final polish (tools/crossfit_polish.py)

2026-10-16. Self-measured: the held-out numbers below come from the polish verifier harness
(`docs/concepts/verify/skin-normal-3r-pin-knee-polish.py`, imported unchanged), but this task ran it itself. A config
replaces a CAD's config only after an independent verifier confirms the gain.

## Why

Every in-sample polish of the pin knee lost about 5 points held out. All numbers are fit Bench(110,360), worn exact:

| config | polish bench (the search's own poses) | held out (1154 disjoint poses) | gain over H1 held out |
|---|---|---|---|
| H1 | 24.48 | 28.55 | - |
| P5 (polish 1, margin 5) | 21.92 | 28.96 (shape fitted exact; H1 29.12 on that protocol) | +0.16 |
| C1 (polish 2, mixed 110/360 + 60/160 objective) | 23.04 | 28.22 | +0.33 |
| F7 (GPU gks1, 10^5 configs) | 20.81 | 27.22 | +1.33 |

The model FITS its shape to the bench poses: link heights, hub heights and the knee reference. So a same-bench
objective rewards parameters whose fitted shape just clears those exact poses. Adding a second bench to the objective
(polish 2) did not help, because the shape was fitted on that bench too.

## The objective

* **Pose pool.** The search poses only: Bench(110,360) U Bench(60,160), 634 poses (fit-clip frames + workspace).
  * The verifier's held-out set is every pose outside both benches (1154). It is never read; the tool asserts this.
  * The held-out clips (Wave, Walking) never enter.
* **Two folds.** Fixed seed 20261016 (`XFIT_SEED`), 317 + 317 poses, stratified. The strata:
  * clip frames per (clip, region);
  * workspace poses per region.

  The regions are: overhead (elevation >= 140), across-body (plane >= 100, elevation >= 40), behind-the-back (a
  "back" clip, or plane < -30 and elevation > 20), and otherwise 35-deg elevation bands. Every clip and every region
  sits in both folds (`python3 tools/crossfit_polish.py folds` prints the table). Each fold gets its own fast grid,
  gathered from the two benches' caches into a derived cache (`XFIT_DIR`, default /tmp/xfit; built once per machine,
  flock-guarded, mmap-shared).
* **Score of a parameter set.** For each order (A, B) of the folds:
  1. fit the shape on fold A (fast);
  2. run the continuity flood fill on that fitted shape (see below);
  3. wear the shape FROZEN on fold B (the verifiers' frozen hand-over, same attribute list);
  4. apply the model's verifier knock-outs (pin knee: 3D closure, knee vs hub 3, E boss; minarc: the claim harness's
     checks incl. the kit margin in every state and the q2 dowel slot);
  5. drop the workspace poses the flood fill does not connect;
  6. take the near-touch gap from the model's audit (metal < 1 mm counts as contact).

  **objective = the mean of the two out-of-fold near-touch gaps.** The in-fold near-touch gap is logged next to it, so
  every row carries its in-sample vs out-of-fold drop. An optional `XFIT_OH_PEN` adds points per overhead clip frame
  lost; it defaults to 0.
* **Continuity.** The rule "Reach must be reachable by moving" is the verifier's kinematic flood fill (remeasure
  `conn`):
  * the 1432-pose workspace grid, 2-deg slerp edges, seeds at elevation 0 (K on stop A for the knuckle);
  * no joint step > 10 deg, knee branch sign constant.

  The fill is vectorised: every edge between two closed nodes goes through ONE kinematics call, and it gives the same
  set as the per-edge law (checked: 955 / 955 nodes on H1). Cost: about 5 s per fold fit on this box, a third of an
  evaluation.
* **Plug-ins.**
  * `knee`: tools/knee_polish.py FREE + `margin`, set on the IK's SING per evaluation as the GPU search did. The claim
    runs with CB_FOLD_MARGIN = margin.
  * `minarc`: BDp's kit-rule model (kitrule 1, phys 1, capK 6, m3e 1), FREE = the knee's 13 + bk1, bk2, a1max, smhi,
    smlo. The stops are >= 5 = the user's floor.
* **Driver.** CMA-ES with tools/knee_polish.py's update (clip + quadratic penalty, periodic angles free). Stops on
  sigma collapse, on no gain > 0.02 in `--patience` generations, at `--max-evals`, or at the time budget. State is
  resumable.

## Experiment: is it worth it? (pin knee)

**Verdict: NOT worth it as built.** On the pin knee the cross-fit picks are WORSE than H1 held out (-0.95 and
-1.04), where the in-sample picks gained +0.16 to +1.33. Across 7 configs the cross-fit objective does not rank the
held-out outcome at all (Spearman rho -0.07 against the held-out near-touch gap, -0.25 against the plain gap). The
in-sample objective does better (0.50 / 0.39). The measured reason is below: the drop is not shape over-fit, so a
split of the search poses cannot see it.

**What ran.** Farm exo-cpu1, 3 CMA starts x 8 processes, popsize 8, sigma 0.4, patience 10 generations, 1000 s.
* 587 cross-fit evaluations in all, 0 errors, median 18 s each:
  * from H1: 193, stopped on patience;
  * from F2: 297, stopped by the time budget;
  * from F7: 97, stopped on patience.
* The best of each start (XP1 from F2, XP2 from F7, XP3 from H1) went through the polish verifier harness, unchanged:
  * `held` and `fitbig`: fit Bench(110,360) fast, worn EXACT, CB_FOLD_MARGIN = the config's margin;
  * the continuity harness `kin fitbig`.
* H1 and P5 were re-run held out in the same session. H1 reproduces 28.55 / 31.06 to the digit.
* Farm cost about $0.18 in all.

| config | cross-fit objective (out-of-fold near-touch) / in-fold | polish bench: fit 110/360, worn exact, 470 poses (gap / near-touch) | HELD OUT, 1154 poses (gap / near-touch) | held-out gain over H1 (plain) | bench -> held drop (plain) |
|---|---|---|---|---|---|
| H1 | 28.13 / 26.81 | 24.48 / 25.59 | 28.55 / 31.06 | - | 4.07 |
| P5 (polish 1) | 28.63 / 28.50 | 21.92 / 22.47 (shape fitted exact) | 28.82 / 31.26 (fast fit; 28.96 with the shape fitted exact) | -0.27 (+0.16 with the shape fitted exact) | 7.0 |
| C1 (polish 2; cross-fit scored without its 5.40 / 5.12 stops) | 23.15 / 23.91 | 23.04 / 24.15 | 28.22 / 30.02 | +0.33 | 5.18 |
| F2 (GPU gks1) | 24.08 / 22.05 | 20.26 / 20.81 | 27.65 / 29.25 | +0.90 | 7.39 |
| F7 (GPU gks1) | 24.69 / 24.10 | 20.81 / 21.91 | 27.22 / 29.04 | +1.33 | 6.41 |
| **XP1** (cross-fit, from F2; XF2-g34-6, margin 5.11) | **22.90** / 24.56 | 21.53 / 23.18 | **29.50 / 32.22** | **-0.95** | 7.97 |
| **XP2** (cross-fit, from F7; XF7-g2-7, margin 5.13) | 23.85 / 22.62 | 21.63 / 22.73 | **29.59 / 30.95** | **-1.04** | 7.96 |
| XP3 (cross-fit, from H1; XH1-g14-0, margin 5.34) | 25.25 / 24.61 | **56.02 / 56.02** (the claim fit collapses: in-band 14 0.61, follow 0.91) | 61.67 / 62.36 | -33.1 | - |

* **The drop.** The cross-fit picks drop 8.0 points from the polish bench to held out, and 6.6 / 7.1 (XP1 / XP2)
  from their own objective to held out.
* **Rules.** All picks hold the rules:
  * fold margin >= 5.2 deg over the taken poses held out;
  * J1 seat anterior 0.06-0.07;
  * O20 hubs;
  * the continuity flood fill on the full 1432-pose grid: XP1 1011 / 1012 connected, XP2 988 / 989, XP3 966 / 966.

**Why it fails (measured).**
1. **The shape does not over-fit poses inside the search distribution.** Over all 587 rows, the in-fold and
   out-of-fold near-touch gaps correlate at 0.984, and the mean drop is +0.04 points. A pose the shape was not fitted
   on, but which comes from the same sample, scores like a fitted one.
2. **The held-out drop is a shift between distributions, mostly in kinematic reach.** The benches pick workspace poses
   by `linspace` over the grid order, which aliases the axial axis:
   * The pool's workspace poses carry 6.0 % with |axial| >= 150 deg; the held-out set carries 11.0 %.
   * The pool carries 33.1 % at axial -90..-45; the held-out set 27.9 %.

   Kinematic closure (fold window + knee + closure, `docs/research/crossfit/kin_closure_diag.json`), pool workspace
   vs held-out workspace:

   | config | pool | held out | drop (points) |
   |---|---|---|---|
   | H1 | 0.710 | 0.662 | 4.9 |
   | P5 | 0.754 | 0.685 | 6.9 |
   | F2 | 0.727 | 0.659 | 6.9 |
   | F7 | 0.729 | 0.667 | 6.2 |
   | XP1 | 0.750 | 0.689 | 6.1 |

   Every polish adds 1.2-2.0 points more closure on the pool than held out. The shape fitted on the pool then lands
   metal on the extra held-out poses it closes: contact held out is 0.019-0.031, against H1's 0.011. The held-out
   reach ranking follows closure; the contact eats the gain.
3. **A split of the pool sees neither effect.** Both folds carry the same aliasing, so the cross-fit objective is an
   in-sample objective plus noise from 317-pose folds. CMA then selects on that noise: XP1's out-of-fold 22.90 is
   the luckiest fold pair, not a better design.
4. **New failure: the claim fit can collapse.** XP3 is fine on both 317-pose fold fits (out of fold 25.25). Its shape
   fitted on all of Bench(110,360) - the shape a claim builds - collapses (56.02). The tool now carries a **claim-fit
   guard**, on by default: the shape is also fitted on Bench(110,360) and scored in-sample, and
   `obj += max(0, claim near-touch - out-of-fold - 3)`. Re-score of the references and picks with the guard:
   on the farm (`docs/research/crossfit/score_guard.json`), the guard costs nothing for H1 / P5 / C1 / F2 / F7 / XP1 / XP2
   (penalty 0; their claim fits score 20.85-25.68 near-touch in-sample) and lifts XP3 from 25.25 to 53.09
   (claim fit 56.09). It adds one fit per evaluation (about +40 % time).

**What would work instead (next instrument, not built here).** Search on a pose set that represents the whole
workspace envelope, not the aliased linspace subsample. A FRESH jittered sample of the envelope works: every grid
pose +- U(7.5 deg) on plane / elevation / axial, seed 7, 4 x 1432 poses, no grid pose reused, built from the rig
(`design_search` Ry Rx Ry + scapula rhythm, HG rebuild error 0.0). Its kinematic closure matches the full grid to
0.005 for every config (H1 0.683 vs 0.678; P5 0.709 vs 0.708; F7 0.685 vs 0.688). That sample needs its own fast
grid cache (`tools/bench_cache_farm.py` parts on the farm, about 3 min, about $0.05 per 500 poses). The held-out set
stays untouched: no held-out pose is scored, and the fresh poses are new draws from the same envelope. Whether new
draws within 7.5 deg of held-out poses are acceptable as search poses is the lead's call; say it with the claim.


## Recipe: the minarc BDp final polish (ready, NOT launched)

**Read the experiment first.** On the pin knee this objective did not beat H1 held out. Expect the same on minarc,
whose drop is also about 4 points (BDp 19.06 frozen vs 23.24 held out). Run it only as specified below, with the
held-out acceptance. The better use of the farm money is the fresh-envelope search bench described above, then this
same driver with that bench as a source. `XFIT_SRC` takes only the two search benches today; adding a third source
is a small change in `pool()`.

One command (3 farm jobs x 8 processes; the Bench(110,360) cache is linked in each job):

    python3 tools/crossfit_polish.py farm minarc --label minarc-BDp-xfit --starts base,F2,F7 \
        --budget-s 1800 --max-evals 700 --popsize 8 --sigma 0.4 --patience 10

* **Starts.**
  * `base` = BDp: docs/concepts/verify/minarc-kitrule/params_floorBD5_phys_cap6.json.
  * `F2` / `F7` = the gks1 finalists' seats and knee (az1 el1 az2 el2 wd wa b3 lE lc phiE phib ang_min stk, from
    docs/research/crossfit/refs.json) moved onto BDp. The knuckle (bk1 bk2 sK a1max), the stops (smhi smlo) and the
    switches (kitrule phys capK m3e near) stay BDp's.
* **Budget.** At most 700 evaluations per start (2100 in all) and 1800 s of wall time per start.
  * Measured: the pin knee took a median 18 s per evaluation on the farm (317-pose folds, flood fill on). The claim-fit
    guard adds about 40 %. minarc took 22 s on this loaded box on 110-pose folds.
  * Expect about 30 s per generation of 8, so 1800 s gives about 60 generations, about 480 evaluations per start.
  * Cost: 3 workers x 0.5 h x $0.288 = about $0.45.
* **Stopping rule.**
  * Per start: sigma x max axis < 0.02, OR no gain > 0.02 in 10 generations, OR 700 evaluations, OR 1800 s.
  * Then `python3 tools/crossfit_polish.py best docs/research/crossfit/cma_minarc-BDp-xfit-*.json` lists the best
    rows by the out-of-fold objective.
* **Claim and acceptance.**
  * Take the top 3 distinct rows plus BDp, in ONE farm batch, through the claim harness
    `docs/concepts/models/minarc-stop-knuckle-4r-kitrule-wear.py`:
    * `conn fitbig` (continuity);
    * `wear fitbig bench` (in-sample);
    * `wear fitbig held` (the 1154 held-out poses);
    * CB_EXACT=1.
  * A pick replaces BDp only if an independent verifier confirms a gain >= 1 gap point HELD OUT (CLAUDE.md final
    polish rule).
  * If no start beats BDp's own objective by >= 1 point, BDp stays. That outcome is also an answer: BDp is already
    at the cross-fit optimum.

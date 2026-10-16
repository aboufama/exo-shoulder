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

RESULTS_PLACEHOLDER

## Recipe: the minarc BDp final polish (ready, NOT launched)

One command (3 farm jobs x 8 processes; the Bench(110,360) cache is linked in each job):

    python3 tools/crossfit_polish.py farm minarc --label minarc-BDp-xfit --starts base,F2,F7 \
        --budget-s 1800 --max-evals 700 --popsize 8 --sigma 0.4 --patience 10

* **Starts.**
  * `base` = BDp: docs/concepts/verify/minarc-kitrule/params_floorBD5_phys_cap6.json.
  * `F2` / `F7` = the gks1 finalists' seats and knee (az1 el1 az2 el2 wd wa b3 lE lc phiE phib ang_min stk, from
    docs/research/crossfit/refs.json) moved onto BDp. The knuckle (bk1 bk2 sK a1max), the stops (smhi smlo) and the
    switches (kitrule phys capK m3e near) stay BDp's.
* **Budget.** At most 700 evaluations per start (2100 in all) and 30 min of wall time.
  * The minarc evaluation measured about 22 s on this loaded box on 110-pose folds; 317-pose folds on the farm take
    about the same.
  * Cost: about 3 workers x 0.5 h x $0.288 = about $0.45.
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

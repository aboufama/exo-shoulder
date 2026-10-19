# Cross-fit final polish - independent check (2026-10-16)

Checker of the experiment in `docs/research/crossfit_polish.md` (tool `tools/crossfit_polish.py`, commit 14199bc).
Task: (1) the held-out set never enters the objective, the folds or the choice of pick; (2) the folds are fixed and
stratified as claimed; (3) re-measure the cross-fit pick and H1 held out with
`docs/concepts/verify/skin-normal-3r-pin-knee-polish.py held` (exact wear), compare with the claim; (4) does "not worth
it" follow from the numbers. Outputs: `docs/research/crossfit_check/`.

## Verdict

**"Not worth it" is CONFIRMED (not refuted), and the held-out numbers reproduce. Two of the supporting statements are
corrected. The diagnosis is only half right, and that changes the recommended next instrument.**

| config | claim, held out (gap / near-touch) | re-measured here | contact | fold margin min (taken) | J1 anterior | hubs |
|---|---|---|---|---|---|---|
| H1 (margin 5) | 28.55 / 31.06 | **28.55 / 31.06** | 0.011 | 5.32 | 0.085 | O20 x3 |
| XP1 (cross-fit best, margin 5.11) | 29.50 / 32.22 | **29.50 / 32.22** | 0.024 | 5.32 | 0.061 | O20 x3 |
| XP2 (margin 5.13) | 29.59 / 30.95 | **29.59 / 30.95** | 0.019 | 5.20 | 0.070 | O20 x3 |
| XP1 at margin 5.0 | - | 29.50 / 32.22 (the margin bump changes nothing) | 0.024 | 5.32 | 0.061 | O20 x3 |

* Every number reproduces to the digit, including the fit-bench gaps (H1 24.57, XP1 23.22, XP2 22.28).
* The cross-fit objective, re-scored on the farm with the current tool (guard on), also reproduces: H1 28.13
  (in-fold 26.805), XP1 22.895 (in-fold 24.555).
* XP1 is 0.95 points WORSE than H1 held out. XP2 is 1.04 points worse. No pick meets the >= 1 point gain rule.

## (1) The held-out set stays out - read and run

* `pool()` takes the poses of `CB._select(110,360)` and `CB._select(60,160)` only. It asserts that no Wave / Walking
  frame and no pose outside the two benches is in the pool. Re-run here: pool 634, held-out set 1154, overlap 0.
  The fold caches are gathered from the two benches' own grids. `Bench(60,160).idx` equals `_select` order (checked),
  so the gather maps each pose to its own grid.
* The claim-fit guard fits on Bench(110,360), a search bench. Its trigger (XP3) was seen on `fitbig` (56.02, a
  search-bench number), not on the held-out run.
* **The picks are the objective's argmins.** XP1 = XF2-g34-6 (22.895), XP2 = XF7-g2-7 (23.85), XP3 = XH1-g14-0
  (25.25): each is the lowest `obj` of its run (re-read from `cma_*.json`, 587 rows, 0 errors). No held-out number
  chose a pick.
* Two leaks, both small, neither a held-out SKIN number:
  * **Continuity.** The flood fill (`flood()`) runs on the full 1432-pose workspace grid. That grid includes the 952
    held-out workspace poses. Their kinematic closure (fold window + knee + closure, no skin) decides which pool
    poses count as connected. That is the continuity rule's own definition (the verifier's `conn` uses the same grid),
    but strictly the objective sees held-out kinematics.
  * **Starts.** F2 / F7 were picked as starts after the gks1 verifier had measured them held out (27.65 / 27.22). That
    is start selection, not pick selection. It biases the starts toward held-out-good configs, which makes the
    negative result (the picks end worse than their starts) stronger, not weaker.

## (2) The folds are fixed and stratified - confirmed

`python3 tools/crossfit_polish.py folds`, run twice in separate processes: identical split (sha1 of the sorted
{pose: fold} map `566cd54b56` both times), fold 0 / 1 = 317 / 317.

* 27 strata. Every stratum is split within +-1 pose.
* The one singleton stratum (Reach a high shelf, el1, 1 pose) necessarily sits in one fold.
* All six fit clips and all 7 regions appear in both folds.
* Both folds carry the same axial mix: |axial| >= 150 deg is 4.4 % / 4.7 %, and axial -90..-45 is 39.4 % / 41.6 %.
  So, as claimed, a split cannot see the pool's axial skew.

## (3) Held out, re-measured on the farm

The verifier harness was run unchanged, through `held` (fit Bench(110,360) FAST, wear EXACT on 1154 poses,
CB_EXACT=1, CB_FOLD_MARGIN = the config's margin). It ran in a fresh batch (`crossfit_check/jobs_check.json`).

* All 4 held runs: n = 1154, fit mode fast, wear mode exact, `bad_removed` 0 (the adversarial verifier's
  knock-outs found nothing).
* Rules hold on every run:
  * fold margin >= 5.20 deg over the taken poses;
  * J1 seat anterior <= 0.085, i.e. back of the shoulder / acromion top;
  * O20 hubs at all three joints.
* Farm: one batch of 5 jobs on 2 workers, wall 335 s, about $0.05. Nothing is left running.

## (4) Does "not worth it" follow?

**Yes. The decisive numbers are each pick against its own start, held out:**

* XP1 (from F2): 29.50 against F2's 27.65. It lost 1.85 points.
* XP2 (from F7): 29.59 against F7's 27.22. It lost 2.37 points.
* XP2 is XF7-g2-7, found in generation 2. The run then stalled for 10 generations. So XP2 is a near-random
  perturbation of F7, chosen on fold noise.
* No pick beats H1 by >= 1 point held out. Both lose to it.

**The rank correlations reproduce, but carry no weight.** Over the 7 configs, the cross-fit objective's Spearman
correlation with held out is -0.071 (near-touch) / -0.250 (plain); the in-sample bench's is 0.500 / 0.393. With
n = 7, |rho| must reach about 0.79 for p < 0.05, so none of the four is distinguishable from 0. They do not show
that the in-sample objective ranks better. What they show is that neither objective ranks held out.

## Corrections to the experiment's statements

1. **In-fold against out-of-fold.** The doc says "over all 587 rows ... correlate at 0.984, mean drop +0.04".
   * Over all 587 rows: Pearson 0.996, mean out-of-fold minus in-fold -1.51. This is dominated by degenerate rows
     (14 rows have a gap >= 100, up to 375; 6 sit at exactly -100).
   * 0.984 / +0.04 is the subset with both gaps < 100 (573 rows).
   * On the working range (both < 40, 554 rows): **0.854, mean +0.17, median +0.22** points.
   * The conclusion stands: fitting the shape on a pose costs about 0.2 points on a sibling pose from the same
     sample, not 5. But the honest figure is 0.85 / +0.2, not 0.984 / +0.04.
2. **The diagnosis: the axial skew is the common part of the drop, not the whole of it.**
   * The axial numbers reproduce (workspace poses only): |axial| >= 150 is 6.0 % of the pool against 11.0 % held out
     and 9.4 % on the full grid. Axial -90..-45 is 33.1 % / 27.9 % / 29.7 %.
   * Kinematic closure (the same instrument as `kin_closure_diag.py`) also reproduces to the digit for H1 / P5 / C1 /
     F2 / F7 / XP1 / XP2.
   * **The claim never had a control.** Every one of those configs was polished on the pool. A pool-minus-held
     closure gap therefore cannot separate a skewed sample from selection on the sample.
   * The control here (`crossfit_check/closure_control.py` -> `closure_control.json`) adds 16 configs never optimised
     on any bench: random draws around H1, z ~ N(0, 1.5) in the FREE step units.

   | configs | pool - held closure | after re-weighting held to the pool's axial mix |
   |---|---|---|
   | 16 unoptimised draws (mean) | 0.036 | **0.006** |
   | 7 polished: H1 P5 C1 F2 F7 XP1 XP2 (mean) | 0.062 | **0.027** |

   * The axial skew explains the unoptimised configs' gap almost entirely (0.036 -> 0.006). That part is common to
     every config.
   * The polished configs carry about 0.026 more closure gap, and axial re-weighting does not remove it (0.027 against
     0.006). That residual is **selection on the pool's particular poses**. Any search that scores a fixed pose set
     earns it, and a split of that set cannot see it, because both folds are the same set.
   * So the drop is about 60 % sample skew (all configs) plus about 40 % search over-fit to the fixed sample (polishes
     only). This agrees with H1's 4.07 drop against 5.2-8.0 for the harder polishes.
3. **The held-out set is itself skewed.** It is the complement of the linspace pick, so it over-weights
   |axial| >= 150 against the full envelope (11.0 % against 9.4 %). Held-out numbers are therefore slightly
   pessimistic for the true envelope. That is fine as a guard, but it is not the population.

## What this means for the next instrument (the lead's call)

* **The fresh jittered envelope bench is necessary but not sufficient.**
  * It removes the common (skew) part.
  * Searched on as a FIXED sample, it will be over-fit again by selection, about 0.02-0.03 closure here. That is
    worth ~2-3 gap points.
* **Add a second, disjoint fresh draw used only to CHOOSE the pick.** For example: the top 10 rows of the search,
  re-scored frozen on a validation draw the search never scored. Then accept on the held-out set as now.
  * Alternatively, re-draw the search poses every few generations, so CMA cannot lock onto one sample.
* **The rule.** CLAUDE.md's "final polishes score only poses the shape was not fitted on (2-fold cross-fit)" guards
  against shape over-fit. That over-fit is measured at about 0.2 points. The rule does nothing against the two
  effects that cost the 5 points.
  * Suggested rewording: search on an envelope sample representative of the whole workspace, choose the pick on a
    second sample the search never scored, accept held out.
  * This is a rule change, so it is for the user to see.
* **The minarc BDp recipe.** As written (`jobs_minarc-BDp-xfit.json`) it inherits both effects. Running it is
  expected to reproduce the pin-knee outcome. I agree it should not be launched as is.

## Files

* `docs/research/crossfit_check/jobs_check.json`: the farm batch (held H1 / XP1 / XP2 / XP1 at margin 5, cross-fit
  re-score of H1 and XP1).
* `docs/research/crossfit_check/held_*.json|log` and `xfit_score.json|log`: the outputs.
* `docs/research/crossfit_check/closure_control.py` and `closure_control.json`: the unoptimised-draw control
  (local, kinematics only, about 2 min).

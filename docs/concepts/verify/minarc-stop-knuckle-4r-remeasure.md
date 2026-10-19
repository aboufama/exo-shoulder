# minarc-stop-knuckle-4r variant B: independent re-measure (2026-10-16)

Lens: **re-measure the number**. Harness: `docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py` (the model
`docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py` imported unchanged; H1 run through the pin knee's verified
harness functions unchanged). Raw outputs: `docs/concepts/verify/minarc-remeasure/`.

Claim under test (row `docs/concepts/rows/minarc-stop-knuckle-4r.json`, `best_params`, CMA stream BD): frozen exact gap
15.42 on Bench(110,360) (score 94.4; reach 0.769, follow 1.0, in-band14 0.899, contact 0.023; near-touch 22.17;
min metal 0.05 mm), fast Bench(60,160) 6.19.

## Protocol (same as the pin knee H1 verification)

* Fit: the shape is fitted on Bench(60,160) FAST (`fit60`: the round-3 protocol; H1 = 27.20 at margin 5), or on
  Bench(110,360) FAST (`fitbig`: the polish protocol; H1 = 24.48 at margin 5 / 26.45 at margin 10). The frozen shape is
  the hub heights, knuckle hub, link profiles, E strap, stack and knee centre m. It is handed over with the same
  attribute list as `skin-normal-3r-pin-knee-polish.py frozen_on`, plus `fK`.
* Wear: Bench(110,360) EXACT (`CB_EXACT=1`), or the pin knee's disjoint held-out bench (`held`: 1154 poses, every
  fit-clip frame and workspace pose outside Bench(110,360) and Bench(60,160); Wave / Walking stay out). Fold margin from
  `CB_FOLD_MARGIN`, O20 hubs only.
* Verifier checks for B (written here, independent of the model's closed form):
  * per-joint rotation axes: link 1a about u1, 1a to 1b about uK, 1b to link 2 about u2, link 2 to member 3 about u3;
  * hub 3 centre, both knee pins and both knee rotation axes;
  * K is one-sided between its stops: dK has the sign of psiA and stays at or below stop B;
  * the J2 interior angle, re-computed from the member frames, stays inside [phi_lo, phi_hi];
  * the E boss against hub 1, hub K, hub 2, L1a and L1b (>= 1 mm) and against L2 (adjacent, 0.15 mm);
  * the knee link against the upper part of hub 3 (>= 1 mm).

  Any pose that fails is knocked out.
* Continuity rule: a flood fill over the full 1432-pose workspace grid. Edges are 2-deg slerp steps; no step of
  q1 / q2 / q3' / pin a / pin b / **dK** may exceed 10 deg; the knee branch sign stays constant. The strict seeds are the
  elevation-0 poses with **K on stop A**. Reach is scored on the taken AND connected workspace poses only.

## Results

### (1) The claimed number reproduces exactly: fit60 -> Bench(110,360) exact, fold margin 5

| | gap | score | reach | follow | in-band14 | in-band10 | contact | near-touch gap (metal < 1 mm = contact) | poses < 1 mm | min metal |
|---|---|---|---|---|---|---|---|---|---|---|
| claim (BD) | 15.42 | 94.4 | 0.769 | 1.0 | 0.899 | 0.581 | 0.023 | 22.17 | - | 0.05 mm |
| **re-measured, verifier checks** | **15.42** | **94.39** | 0.7694 | 1.0 | 0.8991 | 0.5805 | 0.0227 | **22.17** | 14 | 0.05 mm |
| **+ continuity rule (connected only)** | **15.42** | **94.39** | 0.7694 | 1.0 | 0.8991 | 0.5805 | 0.0227 | 22.17 | 14 | 0.05 mm |

* The fast fit (Bench(60,160)) is 6.19, which matches the claim. The verifier checks knock out 0 poses: closure residuals
  stay <= 0.02 deg on every axis; K stays one-sided (dK from -58.65 to 0, stop B at 62.83 from stop A); the J2 interior
  angle stays in [12.28, 162.70], exactly at the stops; boss and knee-vs-hub-3 conflicts are 0.
* Taken poses by state: K on stop A 337, stretched (J2 on phi_hi, K open) 49, folded 1. The forced sub-chain J1-K-J3
  margin is at least 7.42 deg.
* Why poses are lost on the 470-pose bench: fold 56, slide 16, parts 2, contact 9. Overhead >= 140 deg: workspace reach
  0.286 (8/28), follow 1.0.
* Near-touch: the 0.05 mm minimum is on the overhead clip frames at plane 30, elevation 150, axial -60 (4 frames under
  0.3 mm).
* Hubs O20 x 4 (hub K included); f = 49.4 / 62.1 / 80.7 mm, tr = 89.1 mm.
* The run is deterministic: the local run (`local_wear_B_fit60_bench_m5.json`) gives the digits above.

### (2) Continuity rule: the number survives

The full-grid flood fill (`conn_B_fit60_m5.json`; strict seeds at elevation 0 with K on stop A) gives:

* 1143 kinematic nodes and 1143 connected, 0 islands. All 237 stretched-state and 11 folded-state nodes are reached by
  continuous motion from the rest region.
* 1974 edges tested: 2 refused on the fold or window; none for a joint jump (dK included) or a knee branch change.
* On the worn bench, 277 workspace poses are taken and 0 are taken but unconnected, so the gap stays 15.42.
* The held-out bench gives the same picture: 716 taken workspace poses, 0 unconnected.
* For reference, H1 (`conn_H1_fit60_m5.json`) has 971 nodes, all connected. At fitbig it has 985 nodes and 984
  connected, which reproduces the earlier pin-knee continuity verifier's numbers exactly (985 / 984 / 253).
* Caveat: edges are checked kinematically (closure, windows, stops, jumps), not for contact along the edge. This matches
  the pin-knee and stop-relay `connected()` harnesses. The contact-aware version (nodes = poses taken when the shape is
  worn exact on all 1432 workspace poses) is queued on the farm as `conntaken_*_fit60_m5.json`.

### (3) Held out: B beats H1 by 13 points (same harness, same frozen fit60 shape, margin 5, exact, 1154 disjoint poses)

| | gap | score | reach | follow | in-band14 | contact | near-touch gap | poses < 1 mm | min metal | overhead reach | overhead follow |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **B (BD)** | **18.22** | 93.37 | 0.7521 | 1.0 | 0.8963 | 0.0306 | 24.07 | 31 | 0.05 mm | 0.225 | 1.0 |
| H1 | 31.39 | 88.59 | 0.6197 | 0.9653 | 0.8937 | 0.0273 | 34.66 | 15 | 0.09 mm | 0.127 | 0.632 |

* The verifier checks remove 0 poses for either design. B's in-sample to held-out drop is 15.42 -> 18.22 (+2.80);
  H1's is 27.20 -> 31.39 (+4.19).
* H1's earlier held-out readings, 30.73 (fitbig, margin 10) and 29.12 (exact fit, margin 5), use different fit
  protocols. B beats all of them by more than 10 points.

### (4) Margin 10 reading (`CB_FOLD_MARGIN=10`, fit60, exact, continuity applied)

**B: 15.70** (score 94.29; reach 0.7667, follow 1.0, in-band14 0.899, contact 0.023; near-touch 22.46; 0 poses
unconnected). For comparison, H1 at margin 10 is 28.21 (fit60) or 26.45 (fitbig, polish). The margin barely moves B
because its J2 stops (12.28 / 162.70 deg interior angle) already sit inside [10, 170] in the model's phi reading. Only
the forced sub-chain margin bites: 1 folded pose and 1 workspace pose are lost.

### (5) Red team: the fold margin is read in a different metric than H1's, and the number depends on it

The kit defines the rule in one place (`tools/concept_kit.py` lines 25-29, "THE J1-J3 FOLD MARGIN"): a 3R, or any
J1 -> J2 -> J3 dyad, takes a pose only if th = angle(J1, J3) lies in [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m],
with m = 5 (the user's ruling of 2026-10-16). H1 and every verified row are measured this way.

Variant B instead clamps the J2 *interior angle* phi to [m, 180 - m] and carries J2 hard stops at phi = 12.28 / 162.70.
With K on stop A the chain is the plain 3R with a1 = 38.07 and a2 = 58.75, so those stops sit at a J1-J3 fold margin of
**1.88 deg (folded) and 1.37 deg (stretched)**. In the kit's metric, 5 deg corresponds to phi = 20.8 / 146.6, and
10 deg to phi = 31.1 / 132.0.

Measured on the taken poses:

| poses | min fold margin in state A | state-A poses under 5 deg | state-A poses under 10 deg |
|---|---|---|---|
| Bench(110,360) | 1.97 deg | 25 | 65 |
| held out | 1.51 deg | 44 | 154 |

At the stretched stop, J2 turns **6.35 deg per deg** of J1-J3 motion. H1's worst case at its 5-deg margin is 3.15 deg per
deg. This is the "feel near the edge" the user asked to red-team, and the stop is hit at twice H1's worst rate ratio.

The same configuration under the kit's rule (`mstop=1`: the J1-J2-J3 dyad keeps a 5-deg margin in state A; the forced
J1-K-J3 sub-chain keeps its own 5 deg):

| reading (fit60 -> Bench(110,360) exact, margin 5) | gap | score | reach | follow | near-touch gap |
|---|---|---|---|---|---|
| claim's phi-stop reading, continuity applied | **15.42** | 94.39 | 0.769 | 1.0 | 22.17 |
| kit rule, static | 21.33 | 92.24 | 0.708 | 0.973 | 31.15 |
| **kit rule, continuity applied (seeds at elevation 0 with K on stop A)** | **35.56** | 87.07 | 0.569 | 0.973 | 44.78 |

Under the kit's rule, going from state A to the stretched state means crossing phi in [146.6, 162.7] with K still on
stop A. That band sits under 5 deg of fold margin, so it is forbidden, and the knuckle-open region becomes an island.
The flood fill confirms it: 822 of 1070 grid nodes are reachable from rest, and 50 taken bench workspace poses are
dropped. If any elevation-0 pose may seed the fill, 1059 of 1070 nodes are reached (264 of 265 on the bench), close to
the static 21.33. But the stretched poses at the arm's side are themselves reached from rest only through the forbidden
band.

The agent's own re-optimised conservative stream (BB, `mstop 1`) reached 21.40 static. Its continuity was not run.

## Verdict

**REFUTED as a verified beat of H1 under the rules as they stand; the number itself reproduces.**

* Under the model's own law, the number reproduces to the digit:
  * 15.42 at margin 5, and it survives the continuity rule;
  * 15.70 at margin 10;
  * held out, 18.22 against H1's 31.39 under the same harness and frozen protocol;
  * the verifier's independent closure, stop and boss checks remove nothing.

  The re-measure lens criteria are met *in the model's reading*.
* That reading replaces the kit's 5-deg J1-J3 fold margin with a 5-deg J2 interior-angle margin plus hard stops. This
  lets the 3R dyad come within 1.37 deg of its fold, at a J2 rate ratio of 6.35. The reach is bought by shrinking the
  singularity margin in the metric H1 is measured in. CLAUDE.md forbids that without a red team and the user's say.
* Under the kit's rule, the same configuration scores 21.33 static and **35.56 with the continuity rule**. That is
  worse than H1's 27.20 under the same protocol.
* **What would flip it:** a user ruling that a J2 hard stop at least 5 deg short of the fold in *interior angle* meets
  the fold margin. With that ruling, B stands at 15.42 (score 94.4), held out 18.22. The open red-team item is then the
  stop impact: J2 reaches the stretched stop at a 6.35 rate ratio.

  Without it, the knuckle family needs phi_hi <= 146.6 for these arcs, so that the stop engages at a 5-deg J1-J3 margin.
  It then needs a re-optimisation scored with the continuity rule; the BB stream is the starting point.

## Farm cross-check (19 jobs, all ok; outputs `minarc-remeasure/wear_*.json`, `conntaken_*.json`)

The farm runs every reading above again and gets the same digits as the local runs. Farm cost: ~$0.54 (cpu3c).

Note: on the farm the fitbig fit fell back to EXACT, because there is no fast cache for Bench(110,360) key 14f156cb6fc8.
The P5 verifier had the same fallback. H1's fitbig numbers therefore match the P5 verifier (25.03 / 29.12), not the
polish row (24.48 / 26.45 / 30.73, fitted fast).

Gap / near-touch gap; worn exact, verifier checks applied.

| reading | margin | B gap | B near-touch | H1 gap | H1 near-touch |
|---|---|---|---|---|---|
| fit60, Bench(110,360) | 5 | **15.42** | 22.17 | 27.20 | 31.75 |
| fit60, Bench(110,360) | 10 | 15.70 | 22.46 | 28.21 | 33.77 |
| fit60, held out | 5 | **18.22** | 24.07 | 31.39 | 34.66 |
| fit60, held out | 10 | 18.56 | 24.22 | 32.96 | 37.99 |
| fitbig (exact fit), Bench(110,360) | 5 | 15.37 | 20.05 | 25.03 | 26.14 |
| fitbig (exact fit), Bench(110,360) | 10 | 15.66 | 20.34 | 26.87 | 26.87 |
| fitbig (exact fit), held out | 5 | 18.25 | 23.01 | 29.12 | 31.85 |
| fitbig (exact fit), held out | 10 | 18.59 | 23.17 | 31.03 | 32.91 |
| fit60, kit fold rule (`mstop=1`), static / continuity | 5 | 21.33 / **35.56** | 31.15 / 44.78 | (27.20) | |

Contact-aware continuity, with nodes = poses taken when the fit60 shape is worn exact on all 1432 workspace poses and the
verifier checks applied:

* B: 1097 of 1097 nodes connected (874 with K on stop A, 215 stretched, 8 folded), 0 islands, 0 edges refused; the bench
  keeps 277 of 277.
* H1: 913 of 913 connected; the bench keeps 237 of 237.

So, in the claim's own fold reading, contact does not cut off any taken pose either.

Wall-clock note: the shared scratchpad's `jobs.json` belonged to another workflow, and this verifier's job list
overwrote it at 09:03 UTC. That batch had already started at 09:02:41, from its own copy. This verifier's list is now
kept as `minarc-remeasure/farm_jobs.json`.

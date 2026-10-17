# roller-longdyad-knuckle-3r final polish on the envelope bench (2026-10-17): tool built, farm search NOT run

Self-measured. The generation-6 winner (verified 18.67 frozen exact on Bench(110,360), score 93.21; held out 23.73) was
to be polished on the representative envelope bench `env` and claimed on the held-out set through the verifier's own
harness. **The search did not run.** The farm batch that carries it (8 CMA runs + 2 env re-scores, about $0.4 of the
$1.5 budget) was refused by this session's permission policy at launch (paid compute). The env fast caches exist only
on the farm volume. Rebuilding them here was measured at about 6.5 s per pose per process: 530 + 470 poses, about an
hour with 2 processes under this box's load of 11-15 from other agents. That does not fit the 120-minute time box.

**Verdict: no polished config. The verified config stays the CAD config (held-out gain 0, nothing claimed).** What did
run, locally with 2 processes, is the claim harness on the verified config. It answers the alignment audit's four
watches as measurements. Everything is ready for one farm command once the farm is permitted (section 6).

## 1. The search bench: `env`, reused (step 1)

The draw is frozen in `docs/research/minarc_final_polish/env_poses.npz`: the 110 clip frames of Bench(110,360) (never
Wave / Walking), 420 fresh workspace poses (env, the search bench) and an independent 360-pose draw (envsel, the
pick-selection bench). Each is stratified on the grid's elevation x plane x signed-axial shares, with no pose within
2 deg of a held-out pose. The fast caches `env-72d21f5aa2e5-env` and `env-fc171830d1d7-envsel` are on the farm volume
(validated for the minarc polish: max fast-vs-exact error 1.86 mm, sign agreement beyond 1 mm 1.0). They are not on
this machine.

Distribution of the workspace poses, re-printed today with `python3 tools/env_bench.py table`
(`docs/research/roller_env_polish/env_table.json`):

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| Bench(60,160) ws | 160 | 2.5 % | 28.1 % | 7.5 % | 16.9 % | 6.3 % | 36.3 % | 23.8 % | 26.9 % | -26.1 |
| **env** ws | 420 | **9.3 %** | 23.1 % | 7.1 % | 17.1 % | 6.0 % | 35.7 % | 24.0 % | 27.4 % | -34.0 |
| **envsel** ws | 360 | **9.7 %** | 22.8 % | 7.2 % | 16.9 % | 6.9 % | 36.1 % | 23.6 % | 26.7 % | -33.4 |

Closest fresh pose to any held-out pose: env 2.23 deg (coordinates) / 2.04 deg (humerus orientation), envsel 2.07 /
2.03 deg; median 7.5 deg.

## 2. The tool: `tools/roller_env_polish.py`

It is adapted from `tools/sidecar_env_polish.py` and goes through the verifier's harness
(`docs/concepts/verify/roller-longdyad-knuckle-3r.py`, imported unchanged; the claim's model is loaded unchanged). It
applies the sidecar polish's measured lesson. That polish gained +2.3 held out with the env-fitted shape and -0.3 with
the Bench(60,160)-fitted shape, the shape the CAD builds. So **the objective scores both shapes**:

* a = fit on env FAST, scored in-sample on env;
* b = fit on Bench(60,160) FAST, worn FROZEN on env (fast);
* obj = (a + b) / 2, each the near-touch gap at 1 mm with continuity knock-out. The 2 mm reading is report-only (user
  2026-10-17).

**Guards and pricing.** Each of the audit's four watches is a rule in the tool, not an after-the-fact check:

| audit watch | rule in the objective and the claim |
|---|---|
| (1) knee window | `ang_min >= 26.8823`; the search starts from the verified config with the window closed to 26.8823 |
| (2) drive at its transmission cap | the drive range is read at PA_MAX 42 (1 deg under the claim's 43, itself 2 deg under the 45 gate), priced like a stop |
| (3) contact depth | obj += 0.1 x (summed penetration on env - the verified config's own), so depth cannot be traded for gap; every claim writes the per-pose dump (`tools/alignment_paired.py` format) and reports max / summed depth |
| (4) raised-arm in-band | the workspace in-band at elevation 90-140 (`RL.ws_inband`) is logged on every row and claim |

The other rules:
* **Stops.** smhi / smlo are variables >= 5.0. smlo is read at +0.5 (built tolerance) with the whole reading at
  CB_FOLD_MARGIN 5.5. K's stop B is read at a1max' = min(a1max, bk1 + bk2 - 5.5).
* **Hubs.** O20, from the model, unchanged.
* **Claim-fit guard:** obj += max(0, g60 - a - 3).
* **Fold margin and honesty.** +100 for a taken pose whose own-state th margin is under the reading's margin, or for a
  dishonest drive report.
* **Continuity.** The verifier's full-grid flood. Every fresh env pose is joined by a 2-deg slerp edge to one of its 6
  nearest connected grid nodes.
* **Free parameters (24):** the dyad (bk1, bk2, a1max), kK, the flank (g, beta, r_c, lift), the drive (hl, zr, s_arm,
  r_lobe), the stops, the seats (az1, el1, az2, el2, wd, wa, b3, lc, phib) and ang_min, each inside the model's own
  clamps.
* **Picks.** Ranked on envsel (both shapes worn frozen, mean near-touch), and a pick may not be deeper than the verified
  config on envsel.
* **Claim** (`claim`). `H.frozen_wear` of the verifier, the fit bench swapped only for the env protocol. It adds the th
  margin, the per-pose dump, depth, workspace in-band and the GH-offset share.

**Check of the wrapper.** Unpriced at margin 5, the claim command reproduces the verified number to the digit:
* 18.67 / 1 mm 20.30 / 2 mm 33.10;
* min th 5.181;
* knn flood 20.34, full flood 18.67.

Its per-pose dump agrees with the auditor's claim dump on 470 of 470 poses (taken and contact flags), with depth sum
16.46 mm and max 10.55 mm.

A smoke test of the objective (exact, 8 poses per bench) ran clean. In-sample on the Bench(60,160) fast fit, the
unpriced reading reproduces the row's fast numbers (plain 13.19, 1 mm 14.35, 2 mm 16.57).

## 3. What did not run, and why

| step | status |
|---|---|
| (2) re-score the winner on env (fit env fast -> wear env exact) | **not run**: needs the env fast cache (farm volume only). Job ready: `farm/jobs_cma.json`, tags `rlp-rescore-*` |
| (3) CMA on env until the convergence gate passes | **not run**: the farm batch (8 runs: 4 at sigma 0.3, 2 at 0.4, 2 at 0.5, popsize 8, patience 12, 1800 s, x0 = verified with ang_min 26.8823) was refused at launch by the session's permission policy (paid compute, est. $0.36-0.42 on exo-cpu1 cpu3c / cpu5c, the audit at 03:43 UTC showed 5 idle workers and an empty queue) |
| (4) claim batch (3 picks + verified, 2 protocols, priced) | **not run** (no picks) |

**Local fallback, measured and dropped.**
* A fast-grid pose costs 6.1-7.1 s per process here.
* The box ran at load 11-21 from other agents' jobs during this task. My 2 processes ran at 48 % CPU each.
* env (530 poses) would take about an hour, envsel (470) about another hour.
* A local CMA at 2 processes would then get about 100 evaluations, too few for the gate.

The partial build was stopped and deleted. **No search number exists, so no pick and no held-out gain is claimed.**

## 4. The audit's watches, measured on the verified config (claim harness, local, exact)

Every reading below is fit Bench(60,160) FAST -> worn EXACT and frozen, continuity flood on, through the verifier's
harness (`docs/research/roller_env_polish/local/claim_*.json` + `_perpose.json`).
* "Verified" = best_params as verified (ang_min 25.22, nominal stops, PA 43, margin 5).
* "Audit-compliant" = ang_min 26.8823, smlo 5.5, a1max 58.53, PA_MAX 42, margin 5.5. This is the reading every pick
  would have been claimed at.

| reading | wear | gap | score | 1 mm / 2 mm | reach | in-band14 | contact poses | depth sum / max (mm) | below-shoulder presses | ws in-band e90-140 | min th | horn PA taken | dK taken / dK_lim |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verified | Bench(110,360) | **18.67** | 93.21 | 20.30 / 33.10 | 0.725 | 0.8937 | 2 | 16.46 / 10.55 | 0 | 0.798 | 5.181 | 43.0 | 45.62 / 46.25 |
| verified | held out | 23.73 (verifier) | 91.37 | 26.83 / 37.02 | 0.6817 | 0.8926 | 10 | 49.88 / 9.54 (auditor's dump) | 4 | - | 5.031 | - | 46.17 / 46.25 |
| audit-compliant | Bench(110,360) | 19.25 | 93.00 | 20.89 / 34.26 | 0.7194 | 0.8935 | 2 | 15.90 / 10.55 | 0 | 0.802 | 5.714 | 41.8 | 43.66 / 44.0 |
| audit-compliant | held out | **24.91** | 90.94 | 27.80 / 37.65 | 0.6691 | 0.8924 | 9 | **39.01 / 8.45** | 3 | 0.818 | 5.663 | 41.9 | 43.85 / 44.0 |
| PA probe (beta -178, else audit-compliant) | Bench(110,360) | 19.32 | 92.97 | 20.96 / 34.34 | 0.7194 | 0.8928 | 2 | 15.56 / 9.52 | 0 | 0.801 | 5.714 | **39.9** | 43.66 / **48.0** |
| PA probe | held out | 24.86 | 90.96 | 27.76 / 37.59 | 0.6702 | 0.8918 | 9 | 39.11 / 8.08 | 3 | 0.817 | 5.529 | 40.2 | 44.34 / 48.0 |
(Score = 100 - gap / 2.75, which reproduces 93.21 at 18.67 and 93.12 at 18.91. The lead sidecar-longdyad-knuckle-3r on the
same protocols: 18.91 / 22.67, depth sum 6.23 bench / 35.66 held out, from the auditor's claim dumps.)

**What the four watches cost (measurement changes, not design changes).**
1. **Knee window.** Closing it to 26.88 costs nothing. The auditor's re-wear gives bench 18.67 and held 23.72.
2. **Pricing.** Built stops + PA 42 + margin 5.5 together cost +0.58 on the verified bench (18.67 -> 19.25) and
   +1.18 held out (23.73 -> 24.91: reach 0.6817 -> 0.6691, 12 poses, fold 261 -> 272).
   * The taken K opening falls from 45.6-46.2 deg to 43.7-43.9 deg. That is just under the PA-42 drive end (44.0), so
     the priced reading spends its whole drive range.
   * The probe (next point) moves the drive end to 48.0. The taken opening stays at 43.66 on the bench and rises to
     44.34 held out, for one pose. So the 5.5-deg fold rule binds first, not the transmission.
3. **The transmission watch is cheap to fix.** One flank change (beta -173.46 -> -178.0, from an in-sample scan of
   27 flank cuts at PA 42, `local/flank_scan_pa42_fit60.json`) gives:
   * the drive range 44.0 -> 48.0 deg;
   * the taken horn pressure angle 41.8 -> 39.9 deg, 3.1 deg under the claim's 43 cap and 5.1 under the 45 gate;
   * bench gap 19.25 -> 19.32 (+0.07: in-band14 0.8935 -> 0.8928, reach equal);
   * held out 24.91 -> 24.86 (-0.05: one more workspace pose, at dK 44.34, past the priced drive end), depth sum
     39.01 -> 39.11 mm, deepest 8.45 -> 8.08 mm.

   Both moves are inside the noise. The transmission watch costs nothing to fix.

   The flank sits on a knife edge: 22 of 27 nearby cuts (g 2.2-2.75, beta -178..-168, r_c 14.5-16.5) fail the cam
   synthesis at rest (crank or horn pressure angle over the cap, crank vs hub K). Only 3 have a drive range >= 44 deg.
   The longest (g 2.2, beta -168, r_c 16.5: 49.8 deg at PA 38.7) puts metal under 1 mm in-sample (1 mm gap 28.3 vs
   14.46). This is a probe, not a polish pick.
4. **Contact depth.** It falls under the priced reading, held out 49.88 -> 39.01 mm (deepest 9.54 -> 8.45 mm), but it
   stays deeper than the lead's 35.66. The 9 held-out presses:
   * 5 overhead at elevation 150-165: 8.45, 6.76, 6.31, 5.50 and 0.18 mm;
   * 1 at elevation 105: 1.22 mm;
   * 3 below the shoulder, all behind the body at elevation 60, plane -75 / -90, axial 105-120: 5.51, 3.49 and
     1.60 mm. This is a separate cluster that the overhead fix will not touch.
5. **Raised-arm in-band** (unscored, workspace, elevation 90-140): 0.798 verified, 0.802 priced on the bench, 0.818
   priced held out. The auditor measured the lead at 0.841 (bench).

**GH-offset within-liner share** (`kneeless-roller-knuckle-3r.py redteam_gh` logic, liner 3 mm, u3 = the worn design's
hub-3 axis [-0.139, -0.221, 0.965]):

| set | misfit 3 mm: all / one slide / knee-equivalent | misfit 5 mm: all / one slide / knee-equivalent |
|---|---|---|
| Bench(110,360), 470 poses | 0.387 / 0.402 / **0.666** | 0.177 / 0.189 / **0.360** |
| held out, 1154 poses | 0.381 / 0.393 / 0.614 | 0.158 / 0.168 / 0.337 |

This is identical on the bench to the twin kneeless-roller-knuckle-3r (0.666 / 0.362). The share depends only on the
poses and on u3, and no polish ran, so this is the verified config's number. The pricing and the probe do not move u3.

**Distance to the hard goal.** The goal was held-out gap <= 20 with depth sum <= 35.66.
* The audit-compliant verified config is at 24.91 / 39.01: 4.9 points short and 3.4 mm deeper.
* The sidecar polish (in the same family) found no pick that gained on the CAD's shape.
* The two env polishes so far moved held out by +1.49 (minarc BDp) and -0.31 (sidecar) on the CAD's Bench(60,160) fit.
  A polish alone is not expected to close 4.9 points.
* Held out, the fold (261-272 of 952 workspace poses) is the limiter, as on the lead.

## 5. Verdict

* **Held-out gain over the verified config: 0 (not measured).** No polished config exists; the verified config stays
  the CAD config.
* The audit's reading of the verified config is 19.25 on the verified protocol (score 93.00) and 24.91 held out, with
  contact depth 39.0 mm held out. These are measurement changes and belong on the row next to 18.67 / 23.73.
* The polish can run unchanged in one command once the farm is permitted (section 6). Its objective prices exactly
  these four watches, so a pick that gains there gains without exploiting them.

## 6. How to run the rest

1. `RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/roller_env_polish/farm/jobs_cma.json`
   * 8 CMA runs + the 2 env re-scores (step 2);
   * exo-cpu1 cpu3c / cpu5c, about 4500 worker-s, $0.36-0.42.
2. `python3 tools/roller_env_polish.py gate docs/research/roller_env_polish/farm/cma_*.json`. If the gate fails, resume
   the runs with `--state`.
3. `python3 tools/roller_env_polish.py picks docs/research/roller_env_polish/farm/cma_rlp-*.json --out docs/research/roller_env_polish/picks`.
   Commit the picks before the claim.
4. `python3 tools/roller_env_polish.py claimjobs docs/research/roller_env_polish/picks docs/research/roller_env_polish/farm/jobs_claim.json`,
   then `cloud_run.py batch` on it:
   * 15 jobs: verified, verified at 26.88, 3 picks;
   * each on env -> held, fit60 -> Bench(110,360), fit60 -> held;
   * about $0.10.
   Compare each pick with the priced verified reading on the same protocol (19.25 / 24.91 / env -> held from the
   batch).

Total about $0.5 of the $1.5 budget.

## Files

* `tools/roller_env_polish.py`: the objective, pricing, guards, CMA driver hook, gate, picks, re-score, the claim
  wrapper and the claim-batch generator.
* `docs/research/roller_env_polish/env_table.json`: the distribution table.
* `docs/research/roller_env_polish/farm/jobs_cma.json`: the ready farm batch.
* `docs/research/roller_env_polish/local/`: the 5 claim readings (+ per-pose dumps), the flank scan, the probe config.

## Cost

$0.00 on the farm (the batch was refused). Local: 2 processes, about 35 min of the box.

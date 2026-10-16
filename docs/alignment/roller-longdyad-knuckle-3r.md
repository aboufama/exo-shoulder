# Alignment audit: roller-longdyad-knuckle-3r

Hourly audit, 2026-10-16 22:45-22:55 UTC (ledger entry 22:53:06Z, `by auditor`, run `audit:roller-longdyad-knuckle-3r`).
Reference design for every comparison: the verified lead, sidecar-longdyad-knuckle-3r.

## Verdict: WATCH

- **What the row claims.** Status screened, self-measured. The headline field `gap` is the fast Bench(60,160) number,
  13.19. The frozen exact claim on Bench(110,360) is 18.67 plain, 20.30 at 1 mm and 33.10 at 2 mm. Held out it is
  23.73. Complexity is 43.75.
- **Re-measured.** Every one of those numbers reproduces to the digit. The model was run unchanged, on the farm, in
  exact mode.
- **Verdict.** The ledger tool computed **watch**: 3 tool checks plus 7 judgement findings, all at watch level. None is
  gamed.
- **Not a lead change.** The design's own verdict says the same thing. Against the lead it passes the A1 dominance gate
  (plain AND 2 mm) on a margin smaller than one workspace pose, and it loses held out under the same harness.
- **What it really is.** A level-score, lower-complexity point (43.75 vs 49) with a much better 3 mm clearance floor.
  Its raised-arm workspace standoff is worse, and its two contact poses are deeper.

| Frozen exact (this audit) | plain | 1 mm | 2 mm | 3 mm | band 3-14 | held out | held 1 mm | held 2 mm | held 3 mm | cx |
|---|---|---|---|---|---|---|---|---|---|---|
| roller-longdyad (F2) | 18.67 | 20.30 | 33.10 | 107.65 | 18.84 | 23.73 | 26.83 | 37.02 | 101.03 | 43.75 |
| lead sidecar-longdyad | 18.91 | 20.00 | 34.03 | 155.98 | 19.22 | 22.67 | 25.75 | 37.24 | 163.09 | 49 |

Sources:
- This design: `docs/alignment/remeasure/roller-longdyad-knuckle-3r_bench.json` and `_held.json`.
- The lead: `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_bench.json`, plus
  `docs/alignment/live_audit_2026-10-16/ref_sidecar-longdyad-knuckle-3r_held_same_harness.json`. The lead's held-out
  run was re-worn by this audit through the same `alignment_audit remeasure` path and reproduces the verifier's
  22.67 / 25.75 / 37.24.

The comparison is unpriced against unpriced. The lead's priced reading, with the build tolerance on its stops, is
19.36 plain / 23.29 held out. Its gen-6 r_h 15.5 reading is 18.92 / 22.69. This design has no priced reading on file.

## What the wearer gets (measured, frozen exact Bench(110,360); held-out set in brackets)

**Reach**
- Overall reach is 0.725, 261 of 360 workspace poses, the same as the lead (held out 0.6817, 649 of 952; the lead
  657).
- Overhead (elev >= 140): 8 of 28 taken, the same as the lead (held out 18 of 71). The 20 overhead poses are lost to
  fold 14, slide 4 and contact 2.
- Raised arm (elev >= 90): 46 of 113, against the lead's 45 (held out 114 of 300).
- By elevation band, taken / total:

  | elevation (deg) | taken / total |
  |---|---|
  | 0-60 | 158 / 172 |
  | 60-90 | 57 / 75 |
  | 90-120 | 26 / 51 |
  | 120-140 | 12 / 34 |
  | 140-160 | 5 / 13 |
  | 160-200 | 3 / 15 |

**Clearance floor**
- Taken poses with metal under 1 mm: 3 of 371, against the lead's 2 (held out 14 of 851).
- Under 2 mm: 30, against the lead's 26: 5 clip and 25 workspace poses. Held out it is 66.
- Under 3 mm: 133, against the lead's 178 (held out 274 vs 427). This is the design's real gain.
- 10th-percentile per-pose minimum metal overhead: 1.82 mm, against the lead's 1.02 (held out 1.50 vs 0.64).
- Lowest metal on a taken pose: 0.07 mm, at workspace pose (plane -60, elev 60, axial 105).

**Contact**
- 2 contact poses. They are -10.55 mm at (15, 165, -60) and -5.91 mm at (30, 165, -60).
- The lead has 4, at -4.61 / -0.77 / -0.74 / -0.11 mm.
- Held out there are 10, the deepest -9.54 mm at (30, 165, -45). All the deep ones are overhead.
- Which part presses was not measured.

**In-band**
- Scored (clip frames): in-band14 0.8937, against the lead's 0.8966.
- Unscored workspace: 0.854 overall, against the lead's 0.874.
- At elev 90-140: 0.798, against the lead's 0.841.
- Overhead: 0.937, against the lead's 0.926.
- Clip metal histogram: 0.01 % of samples at 1-2 mm and 0.18 % at 2-3 mm; 10.6 % sit above 14 mm.

**Mechanism feel**
- Springs: one clock-spring cap on K. It force-closes both rolling pairs (the lobe follower and the roller on the
  flank). No R17 or dynamics run exists, so the spring torque, K lag and cuff twist are unmeasured.
- Stops: J2 smlo 5.0 / smhi 16.84; K stop B a1max 58.77.
- Fold margin, own-state, in `th`: minimum 5.181 deg over 371 taken poses. No pose is under 5 and 2 are under 5.5. The
  lowest is the forced workspace pose (60, 120, -105). The lead's is 5.232.
- Near-singular postures:
  - The horn pressure angle reaches 43.0 (= PA_MAX) at the last taken K step, dK 45.62 of 46.2.
  - The knee reaches 151.92 deg on the bench (153.16 held out), against the lead's 146.14 (150.86).
- Continuity flood:
  - full grid: 18.67, 0 dropped;
  - knn: 20.34, 6 dropped (the lead's is 21.72);
  - bench graph: 50.29, 113 forced poses dropped (the lead's is 43.4).

  Full and knn are within the rule. The lead's own bench-graph flood is also far off, so the rule names the full
  flood. Source: `docs/alignment/remeasure/roller-longdyad-knuckle-3r_flood.json`.
- Drive: K moves 45.62 deg over the taken poses. It is not idle.
- Smallest hardware clearances: bent arm to hub K 1.14 mm, roller to hub K 2.02 mm.

Probe files:
- `docs/alignment/live_audit_2026-10-16/probe_roller-longdyad-knuckle-3r.json`;
- `_held.json`;
- `_th.json`: th margin, knee span and drive info, through the new adapter `tools/alignment_wear_probe_model.py`.

## Findings

### P1: the A1 dominance pass is a sub-pose margin that reverses held out (watch)

- **Evidence.** The plain gain is +0.24, which is 0.86 of one workspace pose at 0.278 points per pose. All of it is
  contact-pose count: 2 contact poses against 4 is worth +0.53, and the in-band loss costs -0.29. Reach is identical.
  The 2 mm gain is +0.93. At 1 mm the design is behind by -0.30. Held out under the same harness it is behind by -1.06
  (8 fewer taken poses) and by -1.08 at 1 mm; at 2 mm it is +0.22.
- **Why the exo is not better by this number.** These differences are pose-sampling noise in both directions. The
  design does have a real, wearer-relevant advantage: 45 fewer bench poses and 153 fewer held-out poses with metal
  under 3 mm. The score does not see that advantage, so the lead is not shown to be better for the wearer either.
- **Action.** Do not promote on these numbers: the gain is below the 1-point rule. If it goes to a verifier, it goes
  as a complexity Pareto point (cx 43.75 vs 49 at a level score), and the verifier reports 3 mm and held out next to
  plain and 2 mm.

### R1: the dashboard shows only the fast 13.19, score 95.20 (watch)

- **Evidence.** The row's frozen exact claim (18.67, score 93.21) sits under the key `frozen`. `tools/dash_build.py`
  line 409 reads only `frozen_exact` / `frozen_exact_gap`. So `docs/dashboard/data/morphs.json` has `frozen_gap` null,
  and the public and simple boards fall back to basis 'fast'.
- **Effect.** The board shows a best-of-7236 fast number above the golden 95 line. It is labelled 'fast' and sorted
  below the verified rows, so it does not outrank them.
- **The row name.** It still advertises the lever ("lift the lead's drive-stroke wall"). The row's own verdict calls
  that lever dead, and the claimed config's taken th max is 106.3 against the lead's 109.22.
- **Action.** For the lead: expose the self-measured frozen number on the board (proposal C), and rename the row or
  add the verdict to its name. This auditor edits no row or dashboard.

### NEW-contact-depth: depth-blind contact (watch; proposed catalogue entry T5, live audit L6)

- **Evidence.** The plain gain is exactly 2 fewer contact poses, but the remaining contact is 2.3x deeper: -10.55 mm
  against the lead's -4.61 mm, and a depth sum of 16.46 mm against 6.23 mm. Held out there are 10 poses, the deepest
  -9.54 mm.
- **Why it is not better.** A 10 mm press at elev 165 is felt, and possibly bruises, in the region the user ranks
  first.
- **Action.** Report contact depths with every claim (proposal B), and attribute these two poses to a part.
- **Proposed catalogue entry T5. Depth-blind contact.**
  - Looks like: a plain gain that comes from fewer contact poses while the remaining ones go deeper.
  - Detect: the max and summed contact depth against the reference.
  - Here: roller-longdyad -10.55 / 16.46 mm against the lead's -4.61 / 6.23 mm; pick1 -14.6 mm (live audit L6).

### NEW-ws-inband: worse raised-arm standoff, which the score does not see (watch; live audit L2)

- **Evidence.** On the claim bench, the workspace in-band is 0.854 against 0.874. At elev 90-140 it is 0.798 against
  0.841. The design doc reported only the fit-bench reading (0.825 / 0.757 vs 0.837 / 0.762, "no hidden gain"), which
  under-states the raised-arm deficit by about 3.8 points.
- **Action.** Claims report the workspace in-band on the claim bench, not the fit bench.

### G4: the drive at its transmission cap (watch)

- **Evidence.** The horn pressure angle is 43.0 = PA_MAX at the last taken K step. The K stroke is limited by the
  pressure angle (dK_lim 46.2, taken 45.62). The 2-degree cushion under 45 is exactly the allowance for K slop and the
  flank tolerance. The clearances are 1.14 / 2.02 mm to hub K.
- **Action.** Before any CAD, the R17 slaved coupling plus a force check at that step. A sensitivity run at PA_MAX 41
  would show what the cushion buys.

### T4: the knee window walked toward straight, but the score does not depend on it (watch)

- **Evidence.** ang_min has no bound in the model's `_clamp` chain. The search moved it from 26.88 (the lead's
  verified value) to 25.22. The taken knee runs 5.8 deg further toward straight than the lead's.
- **Re-wear.**

  | ang_min | plain | 1 mm | 2 mm | reach | overhead |
  |---|---|---|---|---|---|
  | 25.22 (claimed) | 18.67 | 20.30 | 33.10 | 0.725 | 8 / 28 |
  | 26.88 (the lead's) | 18.67 | 20.30 | 33.10 | 0.725 | 8 / 28 |
  | 30.46 (H1's) | 18.71 | 20.36 | 36.76 | 0.7167 | 7 / 28 |

  So the walk buys nothing against the lead. Files: `docs/alignment/remeasure/roller-longdyad-knuckle-3r_angmin*.json`.
- **Action.** Bound ang_min at 26.88 in the family (proposal E). This claim is unchanged by it.

### M5: K's hold is a single clock spring closing two rolling pairs, with no dynamics check (watch)

- **Evidence.** K is scored at its slaved value. The cam synthesis checks lift-off kinematically, but no R17 run exists
  for this id. The new slaved-coordinate coupling in `judge/dynamics.py` (5d6b819, 9f28755) is the instrument.
- **Action.** Required before any CAD.

## Tool checks (`docs/alignment/roller-longdyad-knuckle-3r.json`, with `--ref sidecar-longdyad-knuckle-3r`)

**At watch**
- `held_out`: the row has no verified gap, because it is screened. Measured held out is 23.73, +5.06 over its own
  frozen bench.
- `continuity`: the tool does not read the flood that this audit measured.
- `fold_margin`: the tool does not read the th margin that this audit measured (5.181).

**Ok**
- `near_touch`: 14.43 points live in the 1-2 mm shell, against the lead's 15.12; band 3-14 gives 18.84.
- `dominance`: +0.24 plain / +0.93 at 2 mm.
- `idle`: the dK span is 45.6 deg.
- `sampling`:
  - sample-weighted in-band 0.894 against part-weighted 0.923;
  - L1a is thinly sampled (8 samples, 0.981 in band);
  - the crank is 0.797 in band on 129 samples (the lead's crank is 0.91);
  - L2 is 0.736.
- `complexity`: recomputed 43.75. The mechanism record carries confidence "medium", so it is a hand count.
- `reporting`: ok as far as the tool can see; the dashboard defect is finding R1.
- `judge_change`: none.
- `rules`: O20 MR117-2RS hubs, 0 passive translations, 3 active DOF.

## Patterns walked and found clean

- **T1 / G1 / T2.** Shell and band: see the checks above.
- **T3.** Own-state th min is 5.181, with 0 poses under 5.
- **S1 / P1.** Covered by finding P1.
- **S2 / S3.** Every declared moving body has a sampled group, including the roller's stub head.
- **S5.** The full flood loses 0 and the knn flood 1.67.
- **M1 / M2.** Every joint maps to a real part: MR117-2RS hubs, an MR63ZZ roller and crank pair, and iglidur knee
  pins. The conjugate flank is 5-axis or wire-EDM, which is plausible.
- **M3.** Pair clearances are in the model: 1.14 mm minimum.
- **M4.** The drive moves.
- **P2.** The search uses only the fast bench; `frozen_held` appears only in the 'held' mode.
- **P3 / R3.** 7236 configs; the row reports a top-5 spread of 0.05, convergence 0.00 / 0.00, and fast to frozen
  +5.48.
- **P4.** The row's 2 commits touch no measurement file.
- **G5 / G6.** Complexity is recomputed equal. The sensed passives are the 2 knee pins, the same as the lead's. The
  merges (the lug into link 1a, the lobe into hub 2's cap, the roller pin into the crank) trade part count for 5-axis
  or EDM machining. That is noted, not flagged.

## Numbers not obtained

- The per-part attribution of the 2 bench and 10 held-out contact poses: the probe has no part split for the claimed
  config.
- The lead's held-out contact depths: the lead's held-out probe was not run.
- The spring torque, K lag and cuff twist (R17): no dynamics run exists for this id.
- A priced reading of this design (stop build tolerance, as the lead's 19.36): not run.

## Proposals (not applied; each is a measurement or reporting change for the lead / the user)

**A. Tighten the A1 dominance gate.** A lead change needs a plain gain AND a 2 mm gain of at least 1 point each (the
polish rule), and a held-out gap under the same harness that is not worse.

| comparison | plain | 2 mm | held out | today's A1 | proposed gate |
|---|---|---|---|---|---|
| roller-longdyad vs the lead | +0.24 | +0.93 | -1.06 | passes | blocked |
| longdyad vs frontload | +3.81 to +3.91 | +9.95 | +4.08 | passes | still passes |
| parallelogram vs longdyad | -0.22 | | | fails (not a lead) | fails (not a lead) |

The longdyad plain gain is +3.81 in the audit tool's reading and +3.91 in ROUNDS.md line 891. The other verified rows
have no 2 mm reading on file.

**B. Report contact depth beside the contact count** (max, sum, count deeper than 3 mm; live audit P5).

| design | contact poses | max depth | depth sum | poses deeper than 3 mm |
|---|---|---|---|---|
| this design | 2 | 10.55 mm | 16.46 mm | 2 |
| the lead | 4 | 4.61 mm | 6.23 mm | 1 |

Other rows are not measured here.

**C. Show self-measured frozen claims on the board.** Rows put their self-measured frozen exact claim under
`frozen_exact`, or `tools/dash_build.py` also reads `frozen.gap` when `frozen.bench` names an exact Bench(110,360).
- Effect: this row's board number moves from 95.20 (fast) to 93.21 (self).
- No score changes.

**D. Let the audit tool read the measurements this audit made.** `tools/alignment_audit.py` reads
`docs/alignment/remeasure/<id>_flood.json` and the probe's th margin.
- Effect on this row: `continuity` becomes ok (full flood = static 18.67, knn +1.67) and `fold_margin` becomes ok
  (5.181).
- This is a tool change, not a metric change.

**E. Bound ang_min in the knuckle family at the lead's verified 26.88,** or report the taken knee maximum with every
claim.
- Effect on this row: none (18.67 / 20.30 / 33.10 identical).
- Other rows are not re-worn here.

## Next

The design is not promotable as a lead on these numbers. If the loop wants it as a complexity Pareto point, the steps
are:

1. An independent verifier.
2. The R17 slaved-coupling run.
3. A part attribution of the -10.55 mm overhead contact.
4. A PA_MAX 41 sensitivity run.

Re-audit when any of those lands, or when the row changes.

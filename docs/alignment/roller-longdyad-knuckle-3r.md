# Alignment audit: roller-longdyad-knuckle-3r

Audit of 2026-10-17 01:42-02:05 UTC (ledger entry 2026-10-17T01:56:25Z, `by auditor`, run
`audit:roller-longdyad-knuckle-3r`). It replaces the screen-time audit of 2026-10-16 22:54 UTC.

Why it ran: the design is now verified (v_gap 18.67, score 93.21) and ROUNDS.md "Round 9 results" names it the
round-9 winner, by 0.24 over the round-8 lead sidecar-longdyad-knuckle-3r (18.91). It is worse held out (23.73 against
22.67). The question was whether the 0.24 is a real gain or a bench artifact.

The user's 2026-10-17 rulings apply:
- The 2 mm near-touch A1 dominance gate is retired, and the plain verified gap decides. This audit cites the 2 mm reading
  as information only.
- A sensed joint is a joint.
- All checks stay kinematic.

## Verdict: WATCH (the 0.24 is a tie, not a gain)

- **The claim.** The verified gap is 18.67 (score 93.21), frozen exact on Bench(110,360). The verifier also measured 1 mm
  20.30, 2 mm 33.10 and held out 23.73. The claim reproduced to the digit in the 2026-10-16 re-wear
  (`docs/alignment/remeasure/roller-longdyad-knuckle-3r_bench.json` and `_held.json`). The claimed parameters have not
  changed since: `best_params` is identical in commits 31e8446 and 70c2230.
- **The ledger verdict is watch:** 1 tool check plus 8 judgement findings, none of them gamed.
- **The 0.24 is not a measurable gain.**
  - On the bench, the paired per-pose noise of the gap difference is SD 1.36 points, and the difference's 90 % interval
    is [-2.62, +1.77].
  - The 2.6x larger held-out set leans the other way: the lead is better by 1.06 on the claim protocol and by 0.69 on a
    perturbed fit.
  - Pooled over bench and held out, the lead is better by 0.41-0.7. The probability that this design is the better
    one is 0.23-0.29.
  - None of these intervals excludes zero.
- **Why this is not "gamed":**
  - Neither design is measurably better on the score.
  - This design is simpler: complexity 43.75 against 49.
  - It has far fewer poses with metal at 2-3 mm.
  - So the ranking does not demonstrably put it above a design that is better for the wearer.
- **What to call it.** Under the plain-gap rule the label "winner" follows mechanically, but it rests on noise. It
  should read as a tie and a complexity Pareto point, and its 0.24 is not progress toward 95.

## What the wearer gets

All numbers below are measured on the claim protocol (frozen exact Bench(110,360)), with the held-out set in
brackets, unless marked.

**Reach**
- Overall: 261 of 360 workspace poses (0.725), equal to the lead. Held out it is 649 of 952 (0.6817), against the
  lead's 657.
- Overhead (elev >= 140): 8 of 28 taken (18 of 71 held out). Of the 20 overhead poses lost, 14 are lost to the fold,
  4 to the slide and 2 to contact.
- Raised arm (elev >= 90): 46 of 113 (114 of 300 held out).
- Paired re-wear, perturbed fit: the held-out shortfall comes from below elevation 90. There the lead takes 18 poses
  this design misses, against 8 the other way. At elevation 90-140 this design takes 12 the lead misses, against 9.
  Overhead is 1 against 1.

**Metal under 2 mm on taken poses**
- 30 on the bench (5 clip, 25 workspace), against the lead's 26. Held out it is 66.
- In the paired re-wear (perturbed fit): 26 against 23 on the bench and 66 against 56 held out.
- Under 1 mm: 3 (14 held out).
- Under 3 mm: 133, against the lead's 178 (274 against 427 held out). This is the design's real clearance gain, and it
  lives only in the 2-3 mm shell.

**Contact**
- 2 contact poses on the bench, the deepest -10.55 mm at (plane 15, elev 165, axial -60), then -5.91 mm.
- The lead has 4, at -4.61, -0.77, -0.74 and -0.11 mm.
- Held out, in the paired re-wear: 10 poses with a depth sum of 49.88 mm, the deepest -9.58 mm. The lead has 11 poses
  with a depth sum of 35.25 mm, the deepest -8.31 mm.
- All deep presses are overhead.

**Workspace in-band (unscored)**
- 0.854 overall, against the lead's 0.874.
- At elevation 90-140: 0.798, against the lead's 0.841.
- Overhead: 0.937, against the lead's 0.926.

Source: `docs/alignment/live_audit_2026-10-16/probe_*`.

**Springs and stops**
- One clock-spring cap on K force-closes both rolling pairs. The lead's RSSR has the same cap.
- Stops: J2 at 5.0 / 16.84, and K stop B at a1max 58.77.
- Cuff twist and spring lag: not measured (no dynamics run, and all checks stay kinematic).

**Near-singular postures**
- The horn pressure angle reaches 43.0, exactly PA_MAX, at the last taken K step (dK 45.62 of 46.25).
- The knee reaches 151.92 deg (153.16 held out).
- The fold margin in th is at least 5.181 (5.031 held out), with no pose under 5.
- The continuity flood keeps 18.67 on the full grid and gives 20.34 on knn.

**Complexity:** 43.75, recomputed equal. Joints: 3 active, K slaved by the cam (not read), and 2 sensed knee pins at
the cuff.

## Findings (`docs/alignment/roller-longdyad-knuckle-3r.findings.json`)

### S1 (watch): the "win by 0.24" is inside the bench's noise and reverses held out

**Evidence on the claim protocol**
- On the bench, the 0.24 splits as follows:
  - 2 fewer contact poses: +0.53;
  - in-band: -0.29;
  - reach: equal.
- Held out, the lead is better by 1.06: 8 more of 952 poses reached, contact equal at 10 against 10, in-band -0.21.

**Evidence from the new paired tool**
- The tool is `tools/alignment_paired.py`. It dumps both designs pose by pose on the same poses, with the models
  unchanged, run on the farm.
- The farm had no fast grid cache, so the fit-60 shape was fitted on exact distances. That is a perturbed fit, not the
  claim protocol.
- Results:

  | set | this design | lead | difference | paired bootstrap | P(this design better) |
  |---|---|---|---|---|---|
  | bench | 19.34 | 19.66 | this design ahead by 0.32 | SD 1.36, 90 % interval [-2.62, +1.77] | 0.61 |
  | held out | 24.28 | 23.60 | lead ahead by 0.69 | 90 % interval [-0.80, +2.09] | 0.23 |
  | pooled | 22.90 | 22.49 | lead ahead by 0.41 | 90 % interval [-0.78, +1.61] | 0.29 |

- On the bench, the equal reach hides 8 + 8 discordant poses.
- The perturbed fit by itself moves each design by 0.67-0.92 points, which is 3 times the margin. The bench-ahead /
  held-behind pattern reproduces under it.
- Files: `docs/alignment/remeasure/roller-longdyad-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_exactfit.json`,
  plus the four `*_perpose.json` files.

**Why the exo is not shown to be better.** Neither design is measurably better on the score. Out of sample, the lead
is more likely the better one.

**Action**
- Report the design as tied with the lead: a complexity Pareto point.
- Its next polish claims held out (as ROUNDS.md already says), and so does any polish of the lead.
- Not gamed, for the reasons in the verdict.

### NEW-contact-depth (watch): proposed catalogue entry T5, depth-blind contact

**Evidence**
- The whole contact-term gain is 2 fewer contact poses, but the presses that remain are deeper:
  - bench: depth sum 16.46 mm against 6.23 mm, deepest -10.55 mm against -4.61 mm;
  - held out: sum 49.88 mm against 35.25 mm, deepest -9.58 mm against -8.31 mm.
- All of them are at elevation 150-165.

**Action.** Report the depth sum and the maximum depth with every claim. Attribute the press to a part: not done here,
because the dump has no per-part split.

### NEW-ws-inband (watch): the raised-arm standoff is worse, and the score does not see it

**Evidence**
- Workspace in-band at elevation 90-140 is 0.798 against 0.841.
- The scored clip in-band is lower on both sets: 0.8937 against 0.8966, and 0.8926 against 0.8947.
- Metal under 2 mm is level or worse: 66 against 56 held out on the perturbed fit, and 66 against 63 on the claim
  protocol.

**Action.** Claims report the workspace in-band on the claim bench.

### S2 (watch): a more real envelope improves the number

**Evidence**
- The verifier's envelope correction adds 19 real metal points: the O5 roller head and the lug's flank-edge strip.
- The gap goes from 18.67 to 18.56, because in-band14 rises from 0.8937 to 0.8948.
- ROUNDS.md prints "envelope-corrected 18.56" beside the winner. The lead has no envelope-corrected reading.
- Source: `docs/concepts/verify/roller-longdyad-knuckle-3r_v_bench_frozen_env.json`.

**Why it matters.** Adding real metal should never be a gain. A 0.11 sampling choice is half the margin.

**Action.** Never quote 18.56 as the claim. See proposal D.

### G4 (watch): the drive sits at its transmission cap

The horn pressure angle is 43.0 = PA_MAX at dK 45.62 of 46.25. The tightest clearances are 1.14 mm (bent arm to hub K)
and 2.02 mm (roller to hub K). This is a geometric margin; the dynamics of the step are outside the metrics by the
user's ruling.

### T4 (watch, measured harmless): search bounds hit

- ang_min walked from 26.88 to 25.22. Re-worn at 26.88, the claim is identical.
- bk1 sits on its lower bound (26) and bk2 next to its own (38.03).
- a1max sits 0.26 under bk1 + bk2 - 5. The lead also sits on that limit.
- The K dyad keeps an interior angle of about 133 deg, and the th margin holds (5.181).
- So no singular margin is spent. The optimum may lie outside the box.

### M5 (watch): one clock spring force-closes two rolling pairs

Closure is checked only kinematically (0.0 mm). The lead shares the same cap, so this does not rank the two designs.
It is for MVP1 and the CAD.

### G5 (watch): the sensed knee pins after the 2026-10-17 ruling

- The mechanism record lists the 2 encoded knee pins as `sensed_passive`. The complexity check treats them as cuff-side
  passives outside the DOF count, which gives 3 + 2 = 5 read coordinates.
- The CLAUDE.md exemption names passive self-aligning slides at the cuff. Whether encoded pins also stay outside the
  count is not covered by "a sensed joint is a joint".
- The knee is identical to the lead's, so this changes no ranking.
- It is the user's question, and it applies to the whole knuckle family.

## Tool checks (`docs/alignment/roller-longdyad-knuckle-3r.json`, `--ref sidecar-longdyad-knuckle-3r`)

**Ok:** held_out (+5.06), fast_frozen (+5.48), near_touch (14.43 points in the 1-2 mm shell), dominance (reported
only, as the gate is retired), continuity (full 18.67, knn 20.34), idle (dK 45.62), sampling (L1a has 8 samples),
complexity (43.75), reporting, judge_change and rules.

**Watch:** fold_margin. The tool does not read the row's `verification.th_margin_min` (bench 5.181, held out 5.031,
no pose under 5). The design meets the rule; the tool misses the record.

## Patterns walked and found clean

| pattern | why it is clean |
|---|---|
| T1 / G1 | The 1-2 mm shell holds 14.43 points, under the watch threshold. |
| T2 | Band 3-14 gives 18.84. |
| T3 | The th margin is 5.181, with no pose under 5. |
| S3 | Every moving body is sampled, including the roller's stub head. |
| S5 | The full flood loses 0. |
| M1 / M2 | Real parts at O20, with MR117-2RS and MR63ZZ bearings. |
| M3 | Pair clearances are in the model. |
| M4 | The drive moves. |
| P2 | `frozen_held` is only a wear mode. |
| P3 / R3 | Top-5 spread 0.05; a single frozen wear. |
| P4 | No measurement file changed in the row's 3 commits. |
| R1 / R4 | The dashboard now shows v_gap 18.67. The fast-only defect of 2026-10-16 is gone. |
| R2 | Not applicable. |

## New pattern (proposed catalogue entry P5): a re-wear environment that silently changes the protocol

**Looks like:** a re-measurement run where the frozen protocol's fast fit bench has no grid cache. The model then fits
the frozen shape on exact distances. The re-wear prints a warning, then reports different numbers as if they were the
claim.

**Why it matters:** this is how "re-measure until lucky" happens by accident. In this audit it moved the numbers as
follows:

| design | bench | held out |
|---|---|---|
| this design | 18.67 -> 19.34 | 23.73 -> 24.28 |
| the lead | 18.91 -> 19.66 | 22.67 -> 23.60 |

**Cause:** in this fresh container the local `.cache/concept_bench` is empty. `tools/cloud_run.py` links only the
local cache files, so the farm jobs had no cache either.

**Detect:** a re-wear is valid as a claim reproduction only if its `fit_fast` equals the row's `fast.plain`.

## Proposals (not applied; measurement or reporting changes for the lead or the user)

**A. A lead change needs a gain outside the paired noise.** Two forms:
- the pooled bench + held-out paired 90 % interval excludes 0; or
- more simply, the held-out gap under the same harness is not worse.

Measured effect:
- On this design: the round-9 lead change is blocked (pooled P(better) 0.29, held out worse by 1.06).
- longdyad over frontload still passes: held out 22.67 against 26.65.
- No other verified row is a lead candidate.

This would tighten a rule the user set on 2026-10-17, so it is the user's call.

**B. Report contact depth beside the contact count** (maximum, sum, and count deeper than 3 mm).

| design | bench (max / sum) | held out (max / sum) |
|---|---|---|
| this design | 10.55 / 16.46 mm | 9.58 / 49.88 mm |
| the lead | 4.61 / 6.23 mm | 8.31 / 35.25 mm |

Other rows are not measured.

**C. Retire the `dominance` check's "gamed" level in `tools/alignment_audit.py`** to match the user's ruling, keeping
it as a reported reading.
- Effect: sidecar-parallelogram and roller-flank lose the dominance part of their gamed verdicts. Their near_touch
  readings stay.
- ALIGNMENT.md section 4 A1 and G5 should carry the 2026-10-17 rulings. This audit's attempt to annotate ALIGNMENT.md
  was refused by the session's permission policy, so the lead should make that edit.

**D. Score in-band per part area, not per sample count,** so that a correction adding real metal cannot lower the gap.
- Effect here: the 18.67 / 18.56 pair collapses to one number.
- Other rows are not measured.

**E. Farm re-wears ship or fetch the fit-bench cache, and refuse to run a frozen claim on the exact fit path**
(pattern P5).
- Effect: none on any score. It only stops non-protocol numbers being read as claims.

## Numbers not obtained

- **The paired per-pose comparison on the exact claim protocol.** The fast cache is missing locally and on the farm
  link. The paired numbers above are on the perturbed fit; the claim-protocol totals come from the 2026-10-16 re-wear
  files.
- **The part attribution of the contact presses:** the dump records no per-part split.
- **The lead's held-out workspace in-band at elevation 90-140:** no probe for it exists.
- **Spring torque, K lag and cuff twist:** out of scope by the kinematic ruling, and not run.

Farm cost of this audit: 4 jobs, about 500 worker-s, $0.04.

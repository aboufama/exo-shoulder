# Alignment audit: sidecar-longdyad-knuckle-3r (verified, round-8 lead, reference for round 9)

Audit of 2026-10-17 ~01:45-02:00 UTC, in the fresh session after the old one hit its usage limit. Ledger entry
2026-10-17T01:56:50Z (`by auditor`, run `audit:sidecar-longdyad-knuckle-3r`). It edited no bench, judge, kit, model,
row, dashboard or CLAUDE.md, and wrote no new tool. The earlier audit (2026-10-16 22:45 UTC, commit 67e8480) is
superseded by this one; its measurements are reused where the claim has not moved.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **18.91**, score 93.12, frozen exact Bench(110,360), fit Bench(60,160); held out 22.67.
- **Ledger reasons** (all watch): two from the tool (near_touch, reporting) and seven from the judgement pass (S1,
  NEW-sensed-knee-pins, NEW-catalogue-drive, NEW-unpriced-stops, G1, M5, R1). None is gamed.
- **No re-wear this time, by the rule.** The row's last commit is b3d426a (2026-10-16 22:03 UTC); the re-wears in
  `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_*.json` were committed at 22:52 UTC and reproduced 18.91 /
  held 22.67 to the digit. `git diff 63167c0 HEAD` (the verification commit to now) shows no change to
  `tools/concept_bench.py`, `tools/concept_kit.py`, `tools/env_bench.py`, `pipeline/avg/body_pose.py`,
  `data/raw/split.json`, this model or its parent model. Only `judge/dynamics.py` changed (R17's slaved coupling), and
  R17 is not in the gap. So the number on file is the number the current bench gives.
- **What changed since the last audit is the rules, not the design.** The user retired the 2 mm dominance gate (A1) and
  ruled that a sensed joint is a joint (CLAUDE.md "User decisions 2026-10-17"). This audit re-reads every finding under
  those rules. No ledger reason of this design now cites A1 or 2 mm as a gate.

## The lead question (round 9): is roller-longdyad's 0.24 real?

Seen from this design's side, under the same harness (exact, 371 bench poses fit / 1154 held-out poses):

| design | plain | held out | held 1 mm | reach (bench) | in-band14 | contact poses | cx |
|---|---|---|---|---|---|---|---|
| roller-longdyad-knuckle-3r | **18.67** | 23.73 | 26.83 | 0.725 (261) | 0.8937 | 2 (deepest -10.55 mm) | 43.75 |
| sidecar-longdyad-knuckle-3r (this) | 18.91 | 22.67 | 25.75 | 0.725 (261) | 0.8966 | 4 (deepest -4.61 mm) | 49 |
| sidecar-parallelogram-knuckle-3r | 19.13 | **22.03** | **24.44** | 0.7194 (259) | 0.9049 | 4 | 49 |

Sources: rows (`v_gap`, `v_reach`, `v_inband14`, `held_out`); `docs/concepts/verify/*_v_held_frozen.json` (all three
n 1154, exact); `docs/alignment/roller-longdyad-knuckle-3r.md`; this design's `remeasure/..._probe.json`.

- **Not a bench artefact.** Both designs were verified on the same bench code (no measurement file changed between
  the two verifications, see above).
- **But not a better exo either.** One workspace pose is worth 0.278 gap points. The plain differences among the top
  three are 0.24 and 0.22, each under one pose, and held out reverses the whole order (22.03 < 22.67 < 23.73).
  Roller-longdyad's gain is 2 fewer contact poses, with the remaining contact 2.3x deeper.
- **The concurrent roller-longdyad audit's paired re-wear agrees** (`remeasure/roller-longdyad-knuckle-3r_vs_
  sidecar-longdyad-knuckle-3r_paired_exactfit.json`; an exact-fit variant, so its levels are 19.34 / 19.66, not the
  verified 18.67 / 18.91): on the bench each design takes 8 workspace poses the other does not, the difference is all
  contact (-0.53) against in-band (+0.21), and the paired bootstrap 90 % interval is [-2.62, +1.77]; pooled bench plus
  held out, roller-longdyad is better with probability 0.29.
- **This design's own lead was the same kind of number.** Its round-8 lead over sidecar-parallelogram is 0.22 plain
  (2 more workspace poses, less in-band), and it is 0.64 behind parallelogram held out (same reach 0.6901, in-band
  0.8947 vs 0.9031). That lead rested on the 2 mm column (34.03 vs 50.14), which the user has now retired.
- **Reading for the lead.** Under the user's rule (plain verified gap decides) roller-longdyad is the lead, and the
  rule is applied correctly. The three rows are a tie within one workspace pose; nothing in the bench number says one
  is better for the wearer than another. What does separate them for the wearer is outside the score: roller-longdyad
  is simpler (43.75) and keeps metal off the skin at 3 mm far better (133 vs 178 bench poses under 3 mm), but presses
  deeper where it touches; parallelogram generalises best but hugs at 1-2 mm; this design sits between.

## What the wearer gets (measured; files from the 2026-10-16 re-wears, unchanged claim)

| item | value | file |
|---|---|---|
| Overhead reach (elev >= 140), workspace | **8 / 28 taken** on the bench (lost: fold 14, slide 4, contact 2); 18 / 71 held out | `remeasure/..._bench.json` audit.overhead140; row held_out |
| Raised-arm reach by elevation (taken / total) | 0-60: 161/172; 60-90: 55/75; 90-120: 25/51; 120-140: 12/34; 140-160: 5/13; 160-200: **3/15** | `remeasure/..._probe.json` ws_reach_by_elev |
| Taken poses with metal < 2 mm | 26 of 371 bench, 63 of 859 held out. Overhead: 8 of 10 clip frames, 5 of 8 taken workspace poses | `_bench.json` / `_held.json` deep; `_probe.json` |
| Metal < 1 mm / < 3 mm | < 1 mm: 2 bench, 14 held out (min 0.28 / 0.14 mm). < 3 mm: 178 bench, 427 held out | same |
| Deepest contact | **-4.61 mm at plane 30 / elev 165 / axial -60** (overhead); then -0.77 (60, 150, -105), -0.74 (-60, 60, 105), -0.11 (15, 135, -60). Held out 10 contact poses. Which part presses: not measured | `_probe.json` contact_poses |
| Workspace in-band (unscored) | 2-14 mm 0.874 over 261 taken workspace poses; overhead 0.926; clips 0.897 | `_probe.json` ws_unscored |
| Fold margin (th) | min 5.232 deg over taken poses (no build tolerance on the stops) | row final_polish |
| Continuity | full flood 18.91 (0 dropped), knn 21.72 | `verify/..._v_bench_frozen.json` |
| Springs / stops | one K clock spring, 0.08 N.m preload; J2 stops smlo 5.0 / smhi 16.55; K stop B a1max 63.18 never binds | row best_params; red team |
| Cuff twist, K lag, lift-off | **not measured**: R17 with the slaved coupling has not run (no `judge/` under `pipeline/full-exo/designs/l1_sidecar-longdyad/`) | - |
| Near-singular postures | knee angle up to 146.1 deg bench (150.9 held out); crank swing 31.6-33.2 deg; transmission >= 30 gated | `_bench.json` coord_spans K.ang; verifier |
| DOF / complexity | 3 active (J1, J2, J3), K slaved and never read, 0 passive translations, pin knee with 2 sensed pins; complexity 49 (recomputed) | `docs/alignment/sidecar-longdyad-knuckle-3r.json` |

Numbers this audit could not get: cuff twist / K lag / lift-off (R17 not run on this design); which part makes each
contact (the probe records the pose, not the part; not re-run because the claim did not move and the local cache is
rebuilding); the priced-plus-catalogue-drive combined wear (never run).

## Findings

### S1 (watch): a sub-pose ranking that reverses held out

- **Evidence.** The table above. Plain margins 0.24 and 0.22 against 0.278 per pose; held out the order reverses
  (parallelogram 22.03, this design 22.67, roller-longdyad 23.73), and again at 1 mm held out (24.44 / 25.75 / 26.83).
- **Why the exo is not actually better.** Whichever of the three the plain gap puts first, the bench cannot tell them
  apart; the ranking is pose sampling. With A1 retired, nothing but sampling now separates this design from
  parallelogram.
- **Why watch.** No design that is clearly better for the wearer is ranked below this one: parallelogram wins held out
  but hugs at 1-2 mm (held-out 2 mm 48.71 vs 37.24).
- **Action.** Proposal P-1 below.

### NEW-sensed-knee-pins (watch): the knee's two encoder-read pins and the 2026-10-17 ruling

- **Evidence.** The mechanism record keeps the pin knee's 2 sensed pins as sensed passives outside the DOF count, as
  cuff-side self-aligning freedoms (CLAUDE.md, 2026-10-15). The user's 2026-10-17 ruling: "Sensed 4 joint does not count
  as passive obviously". ROUNDS.md round 6 already lists the asymmetry (sensed K counts active, sensed knee pins
  passive) as needing the user's say.
- **Measured effect if the knee pins counted as joints** (`tools/simplicity.py` on each record, sensed moved to
  active): every pin-knee row becomes 5 DOF, over the cap of 4, and complexity rises by 38. This design 49 -> 87,
  roller-longdyad 43.75 -> 81.75, parallelogram 49 -> 87, roller-flank 45.25 -> 83.25, frontload 49 -> 87. Only the
  kneeless rows (21.07 / 21.11, no sensed pins) would remain 3-joint designs within the cap.
- **Why watch, not gamed.** The cuff-side rule is an explicit user ruling and the 2026-10-17 quote names the
  shoulder-chain 4th joint. The order among the pin-knee rows does not change.
- **Action.** The lead should put the question to the user: do the two knee-pin encoders make the knee pins joints
  under the DOF cap? (A cuff IMU instead of the encoders is the alternative listed in round 6.)

### NEW-catalogue-drive (watch, still open)

- **Evidence.** With the catalogue M2 ball link (KBRM-02, O9 x 4) and the build spec's stop B at dK 35.4, the same
  harness gives 19.76 (score 92.81) / 1 mm 20.85, held out 23.53 / 26.63 (`remeasure/..._rh155cap354_*.json`). The
  gen-6 CAD still has no judge output, so the custom O7 crank-tip eye that would keep 18.91 is unjudged.
- **Why not better.** 0.85 of the number belongs to a part that has not been built or judged. On buildable readings
  roller-longdyad (envelope-corrected 18.56, ROUNDS round 9) is ahead by about 1.2, not 0.24.
- **Action.** Judge the gen-6 L1's crank-tip and horn eyes at 1 mm; then 18.91 or 19.76 is the build's number.

### NEW-unpriced-stops (watch)

- **Evidence.** smlo 5.0 and a1max 63.1774 = bk1 + bk2 - 5 exactly; min th margin 5.232; priced (+0.5 on the stops,
  CB_FOLD_MARGIN 5.5) 19.36 / held 23.29 (row final_polish.priced).
- **Change under the new rules.** minarc pick1 (priced) is now 4-active, so the "within 0.51" comparison is moot; the
  round-9 comparison with roller-longdyad (also smlo 5.0, unpriced) is like-for-like. The dashboard still mixes priced
  and unpriced verified numbers.
- **Action.** Show which verified numbers carry build-tolerance pricing (proposal P-b of the 22:45 audit, unchanged).

### G1 (watch): metal hugs the skin overhead (for the wearer, not a gate)

- **Evidence.** Overhead 8 of 10 clip frames and 5 of 8 taken workspace poses with metal < 2 mm; overhead p10 min
  metal 1.02 mm bench, 0.64 mm held out; 15.12 points in the 1-2 mm shell (11.49 held out).
- **Why not better.** On a real, bulging arm, 1-2 mm overhead is metal on skin. The user ruled 2 mm is not a gate, so
  this is reported for the wearer only.
- **Action.** Keep reporting the overhead floor; hub 3 (in-band 0.60) and L2 (0.75) are the out-of-band parts.

### M5 (watch): one spring holds the drive, R17 not run

- **Evidence.** K's 0.08 N.m clock spring keeps the whole drive train in compression; lift-off above ~30 rad/s2 of q2 is
  an estimate. No R17 output for this design.
- **Action.** Run R17 with the slaved entry on the gen-6 L1: K against its law, lift-off, cuff twist.

### R1 (watch): stale text

- **Evidence.** Row and dashboard verdict still open "SCREENED, a candidate for the verifier"; the dashboard row carries
  the fast 10.3 / reach 0.80 in its gap / reach fields; HANDOFF line 81 "no polish, no CAD", line 97 "within 0.51" of
  minarc pick1.
- **Action.** Refresh at the next dashboard / HANDOFF update.

## Patterns checked and clean

| pattern | result |
|---|---|
| T1 / T2 | contact line held at 1 mm; band read 3-14 mm costs 0.31 bench / 0.33 held out |
| T3 | th margin 5.232 on file in the one metric |
| T4 | a1max at its clamp, but stop B never binds (row limiter); polish kept ang_min at 26.88 |
| S2 / S3 | part-weighted in-band 0.923 >= sample-weighted 0.897; crank, rod and horn sampled (rod 13, L1a 12 samples, both in band) |
| S5 | full flood 0 dropped |
| M1 / M2 / M3 / M4 | 0 passive translations; O20 hubs; RSSR closure, ball-link tilt, pressure angle drop 0 poses; crank swings 31.6-33.2 deg |
| P1 (in-sample) / P2 / P3 / R3 | held out +3.76 (< 6); polish picks registered before the held-out claim; number reproduced 4 times exactly |
| P4 | no measurement file changed in the row's 4 commits, nor since the verification (only judge/dynamics.py, outside the gap) |
| R2 / R4 | dashboard shows v_gap 18.91 |
| G2 / G3 | K preload 0.08 N.m, J2 step 0.13-0.20 N.m (red team); twist unmeasured (M5) |
| G5 / G6 | complexity 49 recomputed; K is slaved, never read, so it is not a sensed 4th joint. The knee pins are NEW-sensed-knee-pins |

## Proposals (not applied; measurement / reporting changes for the lead or the user)

- **P-1. A lead change needs a margin of at least one workspace pose (0.28) on the plain verified gap, or no held-out
  loss.** This replaces the retired A1 gate's role with no near-touch term. Measured effect on the verified rows (exact
  bench, held out n 1154): roller-longdyad (18.67, held 23.73) would not replace this design (18.91, held 22.67): plain
  margin 0.24 < 0.28 and held out -1.06. This design would not have replaced parallelogram on these rules (0.22 < 0.28,
  held -0.64). frontload -> this design (3.91 plain, +4.08 held) passes. kneeless-roller (21.07 / 24.59) and
  kneeless-sidecar (21.11 / 25.34) are behind on both. This is a tightening of a rule, so it is the user's call.
- **P-2. Ask the user whether the knee's sensed pins are joints** (NEW-sensed-knee-pins). Effect: see the finding;
  every pin-knee row would leave the DOF cap.
- **P-3. ALIGNMENT.md wording** (for the lead, not edited by this audit, since other auditors run on the same file):
  mark A1 "RETIRED 2026-10-17 (plain verified gap decides; contact stays < 1 mm)"; in G1 "Detect", drop `dominance` as
  a gate and keep it as a report; in G5 / G6, state that minarc pick1 is 4-active by the user's ruling and that the
  knee-pin question (P-2) is open.

## Cost

No farm jobs, no local re-wear (claim unchanged). About 15 min of reading and table work.

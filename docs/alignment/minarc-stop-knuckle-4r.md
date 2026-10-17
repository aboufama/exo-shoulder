# Alignment audit: minarc-stop-knuckle-4r (2026-10-17, simplicity v2 metric-change audit)

Auditor run `audit:minarc-stop-knuckle-4r`, hourly 04:03 UTC. It audits commit 3ceacea (2026-10-17 03:40 UTC), which
put the user's ruling "if no encoders are needed, it doesn't count as added complexity" into `tools/simplicity.py` v2.
An unsensed two-pin cuff knee is taken out before scoring, and its 2 encoders are dropped. Bench gaps did not change.

## Verdict and claim

- **Ledger verdict: WATCH.** `tools/alignment_ledger.py` printed it in entry 2026-10-17T04:27:34Z of
  `docs/alignment/ledger.jsonl`. The tool verdict is WATCH, with 4 tool reasons and 12 judgement findings, all 'watch'.
- **Claim:** `polished_gap` **18.40** (score 93.31, pick1). The row's `v_gap` is 19.54 (BDp). Neither moved since
  the 02:21 re-wear, which reproduced both to the digit.
- **In one line:** the v2 subtraction is faithful for this row, and its premise holds. With the 4 hub encoders the
  CAD carries, the knee pins are determined at every taken pose. So the complexity drop (52.0 -> 32.5) is not gamed,
  and no ranking or tie-break moves. The earlier wearer findings stand unchanged: a 4th joint for 1-2 workspace poses, overhead traded,
  deeper contact and a spring with a narrow window (findings 1-3 and 9).

## Metric change (simplicity v2) audited for this row

**(1) Faithfulness of the subtraction.**
- The row's record: active 4, passive_rot 2, bodies 6, joints 6, sensed 0 (was 2), 1 spring, made 14, bought 16.
- v1 gives 52.0: 25 for the 4th active joint, 2 passive rotations, 10 for 2 sensed pins, 3 bodies, 3 joints, 3 for
  the spring, 3.5 for made parts and 2.5 for bought parts.
- v2 gives 32.5: 25 + 1 body + 1 joint + 3 for the spring + 1.5 made + 1.0 bought, and the knee scores 0.
  Kutzbach M = 3, and the tool raises no flags.
- What is left after the template is taken out (bodies 4, joints 4, passive rot 0, made 10, bought 10) is **exactly**
  this row's knee-less variant-A record (`mechanism_A`: bodies 4, joints 4, made 10, bought 10, with K then counted as
  a sensed passive). The record was built as "the pin knee + K", so the subtraction removes the knee it added and
  nothing else: no over-count and no under-count against the record.
- Against the built CAD (`pipeline/full-exo/designs/l1_minarc-pick1/parts_full.json`, L1 keep-out), the knee is: the
  knee link (40.7 x 10 x 2.65 mm Ti, with its window-stop tooth and web made in one piece), the arm pad (pin b plate),
  the pad mount to BOTTOM, 2 DIN 6799 e-clips and 2 GTM 0.5 mm washers. The pins and bushings are not listed at L1.
  That is 3-5 made and 4-6 bought parts against the template's 4 made and 6 bought: at most 1 part either way, worth
  0.5 points. The knee carries no encoder in the CAD; K carries the "4th encoder".
- No MR63ZZ pairs and no shared knee plate: pin a's lower plate is the E strap's boss (member 3), as in the pin knee
  the template was counted from.

**(2) Determinacy without the knee encoders** (`tools/alignment_knee_sensing_minarc.py`, new; output
`docs/alignment/remeasure/minarc-stop-knuckle-4r_{pick1,BDp}_knee_determinacy.json`).
- Method. The loop with GH taken as a ball joint has 4 freedoms: the arm's 3 rotations plus the self-motion of the
  spherical 4-bar J1-K-J2-J3. The tool builds the null-space Jacobian from the model's own closure, at a prescribed K.
  That closure matches the model's phys ik to 6e-10 deg. The hub rows are J1, J2, J3 and K. sigma_min is the
  smallest singular value of those rows of the orthonormal null space, the same quantity as the pin knee's 0.39.

| set | pick1 sigma_min (min / p5 / median), condition max | BDp sigma_min (min), condition max |
|---|---|---|
| contact-aware taken grid poses (pick1 1056 / BDp 1005, the verifier's conn_taken nodes) | **0.369** / 0.490 / 0.529, 2.54 | **0.096**, 9.83 (worst forced pose 150 / 120 / -75, dK -27.5 deg) |
| taken overhead (elevation >= 140; 20 / 26) | 0.390, 2.41 | 0.117, 8.12 |
| every library pose the frozen design closes (1556 / 1481 of 1883; contains every taken bench, held-out and clip pose) | 0.284, 3.30 | 0.084, 11.26 |
| K's encoder dropped (K free, J1-J3 read) | 0 at every pose | 0 at every pose |
| K from its spring / stop law, unsensed (J1-J3 read) | 0 on the 294 forced poses (J2 sits on its stop and reads nothing); state A min 0.380 | 0 on the 204 forced poses |
| hub-only arm-twist error per mm of in-plane GH drift (R10; the pins absorb it) | max 1.69 deg / mm, median 0.79 | max 1.91, median 0.92 |

- The calibration is skin-normal-3r-pin-knee: 0.39 in its doc (lines 565-568) and 0.383 when re-run with
  `tools/alignment_knee_sensing.py`. pick1 matches it. BDp is determined at every pose, but up to 4x worse
  conditioned: an encoder error can become up to about 10x that error in a knee pin or the GH estimate.
- **The premise holds for this row.** The 4 hub encoders fix every passive coordinate at every taken pose. K's own
  encoder is needed: with it dropped, sigma_min is 0 everywhere. That encoder is in the CAD and is paid for by the
  25 points of the 4th active joint, so nothing is hidden. The R10 caveat that made the pin knee keep its pin
  encoders in v1 still applies: GH translation is not in the model.

**(3) Rankings and tie-breaks.**
- v1 -> v2 moves minarc, sidecar-longdyad and roller-longdyad by the same -19.5 (52 / 49 / 43.75 -> 32.5 / 29.5 /
  24.25). Their gaps stay +3.0 and +8.25, so round 9's tie-break (roller-longdyad 24.25 vs sidecar-longdyad 29.5)
  is unchanged.
- minarc is the most complex of the 9 rows with v_gap <= 23 in both versions.
- On (v_gap, complexity), roller-longdyad dominates it in both versions (18.67 / 24.25 vs 19.54 / 32.5). With the
  polished 18.40 it sits on the front in both versions.
- Its only closer neighbour is arm-parked-knee-4r, which has no knee: 32.25 in both versions, 0.25 below minarc
  (19.75 below under v1). That row has the worse gap (26.71), so no choice flips.
- Outside this row, v2 does change the (v_gap, complexity) front: kneeless-roller-knuckle-3r (21.07 / 23.75) drops
  off it, and skin-normal-3r-pin-knee (27.20 / 0) joins it. This is reported for the lead; it is not this design's
  finding.

## What the wearer gets (measured, unchanged since the 02:21 re-wear; the claim did not move)

Re-worn here, fit Bench(60,160) fast -> frozen -> Bench(110,360) exact, through the verifier's harness unchanged
and on the 1154 held-out poses (fit-60 shape). Both configs reproduce their verified gaps to the digit: pick1 18.40 /
22.69, BDp 19.54 / 24.18. The sidecar-longdyad column is its own re-wear (`remeasure/sidecar-longdyad-knuckle-3r_*`).

| measure | pick1 (claim 18.40) | BDp (v_gap 19.54) | sidecar-longdyad, 3 joints (18.91) |
|---|---|---|---|
| overhead workspace taken (elevation >= 140), bench | **7 / 28** | 8 / 28 | 8 / 28 |
| overhead workspace taken, held out (fit-60) | **12 / 71** | 16 / 71 | not measured |
| overhead poses lost to contact, bench / held out | 5 / 16 | 2 / 7 | 2 / - |
| workspace taken (bench) / reach | 270 / 360, 0.750 | 260 / 360, 0.722 | 261 / 360, 0.725 |
| raised-arm reach by band, bench (taken / total) | 90-120: 28 / 51; 120-140: 13 / 34; 140-160: 5 / 13; 160+: 2 / 15 | 25 / 51; 13 / 34; 5 / 13; 3 / 15 | 25 / 51; 12 / 34; 5 / 13; 3 / 15 |
| taken poses with metal < 1 / 2 / 3 mm (bench, of 380 / 370 / 371) | 13 / 38 / 171 | 15 / 36 / 168 | 2 / 26 / 178 |
| taken overhead workspace poses with metal < 1 / 2 / 3 mm | 4 / 6 / 7 of 7 (held 6 / 11 / 12 of 12) | 2 / 7 / 8 of 8 (held 6 / 14 / 16 of 16) | 1 / 5 / 8 of 8 |
| gap at 1 / 2 / 3 mm near-touch (reported, not a gate) | 23.36 / 41.29 / 156.01 | 26.44 / 41.69 / 152.61 | 20.00 / 34.03 / 155.98 |
| same, held out | 26.73 / 47.94 / 162.57 | 28.86 / 45.68 / 160.71 | 25.75 / 37.24 / 163.09 |
| contact poses (metal inside the skin), bench; deepest | 11; **-13.17 mm** (overhead, elevation 165) | 4; -6.41 mm | 4; -4.61 mm |
| contact poses, held out (fit-60); deepest | 35; **-14.61 mm** (hub K wall in the deltoid) | 13; -7.27 mm | 11; -8.31 mm |
| workspace in-band 2-14 (unscored), all / overhead | 0.858 / 0.925 | 0.867 / 0.875 | 0.874 / 0.926 |
| clip in-band 2-14 (scored) / 2-10 | 0.894 / 0.564 | 0.893 / 0.594 | 0.897 / - |
| K open on taken poses (bench) | 86 of 380, up to 56.2 deg; 12 clip frames; **0 at elevation >= 140** (held out: 209 of 887, up to 56.6 deg; 0 of 31 at >= 140) | 61 of 370, up to 34.0 deg; 6 clip frames; 0 at >= 140 | no K joint (K slaved) |
| held out gap (fit-60) / at 1 mm | 22.69 / 26.73 | 24.18 / 28.86 | 22.67 / 25.75 |


Sources: this audit's re-wear `docs/alignment/remeasure/minarc-stop-knuckle-4r_{pick1,BDp}_probe_{bench,held}.json`
(`tools/alignment_wear_probe_minarc.py`, new; it runs `docs/concepts/verify/minarc-final-polish-verify.py` unchanged
and only wraps the harness's `near_touch` to capture the worn bench), and the verifier files in
`docs/research/minarc_final_polish/verify/`.

- **Springs:** one clock spring at K. The bench treats K as geometry. As built (0.04 N.m preload) it passes R17 upright
  only: Reach a high shelf drifts 3.72 deg upright, but 4.12-7.70 deg with gravity across the thorax (fails the 5-deg
  rule in 3 of 4 directions). At 0.08 N.m it lags 9.28 deg upright (`docs/research/pick1_k_hold_check.md`).
- **Stops:** J2 dowel slot at the 5-deg J1-J3 margin (+0.5 built); K stop B at dK 56.65 deg; knee window ang_min
  26.14 in the model, 30.5 in the CAD.
- **Cuff twist:** 2.00 deg upright on R17; up to 3.83 deg with the thorax tilted.
- **Near-singular postures:** own-state J1-J3 margin min 5.623 (bench) / 5.586 (held out) at the 5.5 priced rule;
  107 of 380 taken bench poses under 10 deg. In forced poses the plain dyad is 22.8 deg past its own fold: the margin
  exists only because K opens. J1 swings up to 31 deg per 10-fps frame at the clips' peak arm speed. The taken knee
  reaches 152.75 deg held out, 27.3 deg from straight.

## Findings

Each finding is in `docs/alignment/minarc-stop-knuckle-4r.findings.json` with its evidence. All are 'watch'.

1. **G6, a 4th sensed joint against 3 active joints.**
   - Evidence: plain, pick1 is 18.40 against roller-longdyad 18.67 (+0.27, under one workspace pose = 0.278) and
     sidecar-longdyad 18.91 (+0.51). On the same held-out protocol (fit Bench(60,160), wear the 1154 held-out poses
     exact) it is 22.69 against sidecar-parallelogram 22.03, sidecar-longdyad 22.67 and roller-longdyad 23.73. At
     1 mm it is 23.36 against 20.00 / 20.22 / 20.30 on the bench, and 26.73 against 25.75 / 24.44 / 26.83 held out.
   - Why it is not a better exo: the 4th joint buys 9 workspace poses on the bench (reach 0.750 vs 0.725), none
     overhead (7 of 28 vs sidecar-longdyad's 8 of 28). It costs a joint, complexity 32.5 vs 29.5 under simplicity v2 (52 vs 49 under v1; the 19.5-point knee subtraction is the same for both), and contact
     (11 vs 4 bench poses with metal inside the skin, deepest -13.17 vs -4.61 mm).
   - Action: none on the score. README's "Best verified overall" line should say the lead it holds is plain-only and
     within one to two poses; the user's ruling already names the 3-joint rows as the leaders.
2. **NEW-overhead-traded, the polish gained reach away from overhead.**
   - Evidence: pick1 replaced BDp (19.54 -> 18.40 bench, 24.18 -> 22.69 held out) but takes fewer overhead workspace
     poses (elevation >= 140): bench 7 vs 8 of 28; held out 12 vs 16 of 71 (fit-60 shape), 16 vs 17 (env-fit shape).
     Its gain is about 35 held-out workspace poses at mid and low elevation (reach 0.7195 vs 0.6828). The polish
     note's "overhead grid nodes rise from 32 to 44" counts kinematic closures, not poses the wearer takes.
   - Why it is not a better exo: the goal puts overhead first; the gap weighs every workspace pose equally.
   - Action: proposal B1. Not gamed, because BDp loses about 35 held-out workspace poses.
3. **NEW-depth-blind-contact, the new reach comes with deeper metal in the arm next to it.**
   - Evidence: contact poses bench 11 vs BDp 4 (deepest -13.17 vs -6.41 mm, both overhead at elevation 165); held
     out 35 vs 13 (fit-60), 28 vs 9 (env fit); deepest -14.61 vs -7.27 mm. The deepest is the side wall of hub K's
     18.25 mm stack in the raised deltoid; next is the knee link and pad 10 mm into the chest wall with the arm across
     the body. R1-aim (in-band 2-10) held out 0.563 vs 0.593. In-band never samples hub K's cap.
   - Why it is not a better exo: "never touching" is the first line of the goal; the score charges a 14.6 mm press and
     a 0.1 mm graze the same, and both only as poses not taken.
   - Action: proposal B2. Not gamed: no clip frame touches, and BDp cannot close 19 of pick1's 28 env-fit contact poses.
4. **G5, complexity after simplicity v2.** v2 gives 32.5 (v1 52.0). The template subtraction leaves exactly
   this row's knee-less variant-A record (bodies 4, joints 4, made 10, bought 10) with K active, so it removes the knee
   the record added and nothing else. Against the pick1 CAD's knee parts the template is within one part either way
   (0.5 points). Stale text: the row's `complexity` field is still 33.0 (recomputed 32.5) and `mechanism.notes` still
   says 'sensed passive 2 = the knee pins' while `sensed_passive` is 0. Action: proposal B4.
5. **R2, stale leader text and a mixed row.** The row's and the dashboard's verdict strings still open with "VERIFIED
   LEADER" (BDp 19.54). The dashboard pairs pick1's v_gap 18.40 with BDp's verdict, held-out and complexity text. The
   sweep record is still the refuted 6.19. The tool's reason "the dashboard flatters the design" (18.4 vs 19.54) is
   partly a false positive: 18.40 is independently confirmed, only stored in `polished_gap`, not `v_gap`.
6. **NEW-mixed-protocol, held-out numbers from two protocols side by side.** README shows pick1 "held out 21.31"
   (env fit) next to sidecar-longdyad "held out 22.67" (fit 60). On one protocol they tie (22.69 vs 22.67). The env
   fit flatters minarc by 1.38 and makes sidecar-longdyad's verified config 2.59 worse
   (`docs/research/sidecar-longdyad-knuckle-3r_final_polish.md`). Minor P2 note: 2 env poses sit 1.66 / 1.97 deg
   from held-out poses; the fit-60 protocol does not use env, so pick1's +1.49 over BDp stands. Action: proposal B3.
7. **T4, the knee window below the polish lesson.** The polish's ang_min floor was BDp's 24.95; pick1 sits at 26.14,
   below the >= 30 FINDINGS set for polishes after the GPU-knee case. Held out the knee reaches 152.75 deg (27.3 deg
   from straight; window margin 1.11 deg), with 4 taken held-out poses past H1's 149.5. The CAD's 30.5 stop removes
   them, and the verified held-out number was not re-scored for it (about 0.4 points). Action: proposal B5.
8. **G4, near-singular postures.** 107 of 380 taken bench poses sit under 10 deg of J1-J3 margin; in the 86 forced
   poses the plain dyad is 22.8 deg past its fold, so the margin depends on K opening freely; J1 swings up to 31 deg
   per 10-fps frame at the clips' peak arm speed. Action: the MuJoCo feel check before the spring is frozen.
9. **M5 / G3, a spring with a narrow window.** The score treats K as geometry. As built, 0.04 N.m passes R17 only
   upright (drift 3.72 deg); with gravity across the thorax it drifts 4.12-7.70 deg (fails in 3 of 4 directions) and
   the cuff twists up to 3.83 deg. 0.08 N.m lags 9.28 deg upright. pick1's K moves 15.8 deg at 52 deg/s on "Reach a
   high shelf" where BDp's moves 0.85 deg. Action: a posture sweep in R17 (proposal in pick1_k_hold_check.md).
10. **T1, metal parked just outside the contact line (reported; the user does not gate on it).** pick1 has 13 taken
    bench poses under 1 mm (4.96 points live in the 0-1 mm shell), 38 under 2 mm (22.89 points in the 0-2 mm shell),
    and every one of its 7 taken overhead workspace poses has metal under 3 mm; overhead p10 lowest metal 0.56 mm.
    sidecar-longdyad: 2 / 26 poses, overhead p10 1.02 mm. Under the retired A1 gate this would be 'gamed' against
    sidecar-longdyad (0.51 ahead plain, 7.26 behind at 2 mm). Per the user's 2026-10-17 ruling it is information only.
11. **NEW-hub-only-sensing, the v2 premise re-run for this design.** See the metric-change section: with the 4 hub
    encoders the CAD carries, both knee pins and the GH rotation are determined at every taken pose (pick1 sigma_min
    0.369, condition <= 2.54; BDp 0.096, condition 9.83). K's own encoder is needed and is already paid for (25 points).
    Caveat: GH drift is absorbed by the pins, so the hub-only arm twist errs by up to 1.69 deg per mm of drift.
12. **P4, the complexity judge changed in the same commit as the row.** 3ceacea changed `tools/simplicity.py` and this
    row's mechanism record together (52.0 -> 32.5). It is stated as a measurement change and follows the user's
    ruling. The tool's `judge_change` check reads 'ok' because it follows only gap moves. Action: proposal B7.

## Checks of the tool (`docs/alignment/minarc-stop-knuckle-4r.json`, 04:16 UTC)

`python3 tools/alignment_audit.py audit minarc-stop-knuckle-4r --ref sidecar-longdyad-knuckle-3r` gives WATCH:
- `contact_depth` watch: pick1 has 11 bench contact poses, deepest 13.17 mm, against sidecar-longdyad's 4 and 6.23 mm.
  Held out it has 35 poses, deepest 14.61 mm.
- `sampling` watch: no per-part in-band record on file.
- `complexity` watch: recomputed 32.5 (v2) against the row's 33.0 (finding G5).
- `reporting` watch: the dashboard shows 18.40 against v_gap 19.54, and the sweep record 6.19 (finding R2).
- `held_out`, `fast_frozen`, `near_touch` (BDp in the slot), `dominance` (retired A1 gate; decides nothing),
  `continuity`, `fold_margin` (5.007), `idle`, `rules`: ok. `judge_change` is ok because it follows only gap moves
  (finding P4).

## Proposals (measurement or reporting changes for the lead or the user; none applied, none used in the verdict)

- **B1. Report overhead taken poses with every claim, and flag a polish that loses them.** Each claim states the
  workspace poses at elevation >= 140 it takes (closed, no contact, connected), bench and held out, next to the gap.
  The user ruled on 2026-10-16 that the score stays as is for overhead ("keep reporting overhead taken / 28"), so
  this is reporting only: a polish swap states its overhead taken poses before and after.
  - Measured: minarc pick1 against BDp loses overhead poses (held out 12 vs 16 of 71 with the fit-60 shape, 16 vs 17
    with the env-fit shape; bench 7 vs 8 of 28). No other verified row has a polish swap (the sidecar-longdyad polish
    was already rejected). Overhead taken on the bench, for reference: sidecar-longdyad 8 of 28
    (`remeasure/sidecar-longdyad-knuckle-3r_probe.json`); other rows are not measured.
- **B2. Report the deepest contact and the contact poses deeper than 3 mm with every claim.** The contact term
  counts a 14.6 mm press like a 0.1 mm graze. Reporting only; any depth weighting is the user's call.
  - Measured (bench): pick1 11 contact poses, deepest -13.17 mm; BDp 4, -6.41 mm; sidecar-longdyad 4, -4.61 mm.
    Held out (fit-60 shape): pick1 35, -14.61 mm; BDp 13, -7.27 mm.
- **B3. Compare held-out numbers only within one fit protocol in status lines.** README's "held out 21.31" (env fit)
  sits next to sidecar-longdyad's 22.67 (fit 60). Effect: minarc's line reads 22.69 (fit 60), a tie with 22.67.
- **B4. Recompute a row's `complexity` in the same commit that changes its mechanism record.** Effect today: minarc
  33.0 -> 32.5 (v2), and its `mechanism.notes` should drop 'sensed passive 2 = the knee pins'.
- **B5. Hold the knee window at the CAD's stop (ang_min 30.5) in claims, or re-score the claim with it.** Effect:
  pick1 loses about 4 held-out poses (about 0.4 gap points held out), 0 on the bench; BDp 1 held-out pose.
- **B6. Keep the knee encoders' points on a row whose hub-only sensing is ill-conditioned (proposal, a tightening).**
  For example, if sigma_min < 0.2 on the taken poses, then +10 is charged. Measured effect: pick1 (0.369) 32.5,
  unchanged; BDp (0.096) 42.5. Other rows need the same check (roller-longdyad 0.250 / 0.246 from its audit). This is
  the user's call; it is not used in the verdict.
- **B7. `judge_change` should also follow complexity moves.** A commit that changes `tools/simplicity.py` and a row's
  mechanism record together should be listed, as gap moves are. Effect today: it lists 3ceacea on the 13 pin-knee rows
  as a stated measurement change ('watch'); no verdict moves.

## Questions for the user

- Does "it doesn't count as added complexity" cover the whole two-pin knee (pins, knee link, arm pad, 2 rotations:
  9.5 points), or only its 2 encoders (10 points)? v2 takes out both (19.5 points). For the pin knee the earlier doc
  said "9.5 if the user accepts hub-only sensing".
- Hub-only sensing assumes GH does not translate. The knee absorbs GH drift, and the arm-twist reading then errs by up
  to 1.69 deg per mm of drift on pick1. Is that accuracy acceptable for MVP2's control, or should a cuff IMU or the
  knee encoders come back there?
- Should a row whose hub-only sensing is ill-conditioned keep its knee encoders in the count (proposal B6: BDp sigma_min
  0.096 vs pick1 0.369)?

## Not measured, and why

- **No re-wear in this run.** The row's last commit (3ceacea, 03:40) changed only the mechanism record. The params,
  `v_gap` 19.54, `polished_gap` 18.40 and the model files are untouched, and bench gaps did not change. The 02:21
  re-wear (`remeasure/minarc-stop-knuckle-4r_{pick1,BDp}_probe_{bench,held}.json`) reproduced both claims to the digit
  and stands. Farm spend in this run: $0.
- The determinacy check uses the model's kinematics only. GH translation (R10) and encoder resolution are not modelled.
  The per-mm twist figure is the only drift number.
- Per-part sample counts (S2): still not exported by the harness (the tool's `sampling` stays 'watch').
- Clip frames were checked as part of the library superset (all 1883 library poses, 1556 closed), not as the exact
  taken clip set.

---

## Skeptic (2026-10-17, 02:30-02:40 UTC, git 14dd5d1)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and changed
no score. It re-derived every number from the verifier files (`docs/research/minarc_final_polish/verify/v_*`), the
audit's re-wear files (`docs/alignment/remeasure/minarc-stop-knuckle-4r_*`), the rows and `tools/simplicity.py`.
No re-wear was needed: every number in the reasons was on file and was reproduced. Farm $0.

**Final verdict (ledger, `stage skeptic`, 2026-10-17T02:39:15Z): WATCH.** One of the 15 reasons was refuted
(`continuity`). The other 14 stand, all at 'watch'. The claim is 18.40 (pick1).

**Rulings** (also in `docs/alignment/minarc-stop-knuckle-4r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| near_touch | no | **Numbers.** `_bench.json` (config BDp) gives 19.54 / 26.44 / 41.69 / 152.61, the same as the verifier. **Threshold.** TH shell2_watch 15 is applied to n2 - plain = 22.15, as documented. **Label correction.** 22.15 is the 0-2 mm shell; the strict 1-2 mm shell is 15.25. **Keyed to BDp, not the claim.** pick1's own numbers are 22.89 (0-2 mm) and 17.93 (1-2 mm), both in the watch band. **Wearer.** 38 taken bench poses sit under 2 mm. It is not a gate (user, 2026-10-17). |
| continuity | **yes** | **The connected numbers are on file; the tool misses them only because of its record format.** `v_pick1_fit60_bench_conn.json`: 1105 / 1105 grid nodes, 0 islands, 990 / 990 edges, bench ws 281 / 281. `_conn_taken.json`: 1056 / 1056 nodes, ws 270 / 270. `_pick1_probe_{bench,held}.json` contact_aware_verifier: 0 / 0 dropped, gap 18.40 / 22.69. BDp is likewise 0 / 0 at 19.54 / 24.18. **Result.** Connected minus static is 0.00 everywhere, under TH conn_watch 1.0. **knn flood.** Not on file, but the tool's rule only uses it to raise a watch, so 'ok' does not need it. |
| sampling | no | **Missing measurement.** `parts_ib14` is null in the remeasure files and absent from every verify file. The row has fractions only, for the older configs BD / BA (hub3 0.664, L2 0.779). There are no sample counts, and nothing for pick1 or BDp. Not measured in this time box. |
| complexity | no | **Recomputed.** `simplicity.py` on the row mechanism gives **52.0** (+25 for the 4th active DOF, +10 for 2 sensed passives). The row field says 33.0. **Shown.** The dashboard shows 52.0; HANDOFF lines 79-80 say 33. |
| reporting | no | **First half, a false positive.** After the 02:28 refresh, morphs.json has v_config 'pick1', v_gap 18.4, v_reach 0.75, v_contact 0.0281, v_inband14 0.8941: pick1's confirmed numbers. **Second half stands.** gap / sweep_gap 6.19 (score 97.75), reach 0.8438 from the sweep, and the verdict string 'VERIFIED LEADER ... BDp 19.54'. |
| G6 | no | **Numbers.** Confirmed from the files. **Correction (apples to apples).** pick1 is judge-priced: CB_FOLD_MARGIN 5.5, J2 slot +0.5. The 3-joint reference numbers are unpriced (smlo 5.0). Priced the same way, sidecar-longdyad reads 19.36 bench and 23.29 held out (`final_polish.priced`). Like-for-like, pick1 leads it by **0.96 bench and 0.60 held out**, so "held out it does not lead" is wrong against longdyad. At 1 mm pick1 still trails priced longdyad (23.36 vs 20.45 bench, 26.73 vs 26.39 held). Held out at 1 mm it beats roller (26.73 vs 26.83). **Wearer points stand.** A 4th joint at the cap, overhead 7 vs 8 of 28, contact 11 vs 4 poses. |
| NEW-overhead-traded | no | **Overhead taken.** overhead140_ws: 7 / 28 vs 8 (bench), 12 / 71 vs 16 (fit-60 held), 16 / 71 vs 17 (env held). **Lost to contact.** 5 vs 2 bench, 16 vs 7 held. **K overhead.** K is open on 0 overhead ws / clip poses. **Size.** 1 pose on the bench, 4 of 71 held out. |
| NEW-depth-blind-contact | no | **contact_raw.** 11 / -13.17 vs 4 / -6.41 bench; 35 / -14.61 vs 13 / -7.27 fit-60 held; 28 / -14.58 vs 9 / -7.27 env held. All are ws poses, no clip frame. 5 of the 11 bench contacts are at elevation >= 150. **Fold losses.** 70 vs 86 bench, 209 vs 257 held: pick1 closes more poses and loses more of them to contact. |
| G5 | no | **Stale field.** The row says 33.0; HANDOFF 79-80 say 33; simplicity.py gives 52.0. **Knee pins.** Counted active, simplicity.py gives **90.0 at 6 DOF**, over the cap. CLAUDE.md line 18 names K only. A5 keeps cuff-side passives out of the count. The question is open. |
| R2 | no | **Stale text.** The row verdict / v_verdict and the dashboard verdict open "VERIFIED LEADER ... BDp 19.54", next to v_config pick1, and the sweep shows 6.19. **Caveat.** 18.40 itself is confirmed. |
| NEW-mixed-protocol | no | **README.** Line 33 says 21.31 (env fit); line 36 says 22.67 (fit-60): confirmed. **Correction.** The finding's "tie" (22.69 vs 22.67) also mixes stop pricing. Priced, longdyad held out is 23.29, so pick1 leads by 0.60. README's implied 1.36 overstates that by 0.76. |
| T4 | no | **Knee.** ang_min 26.1449, held knee max 152.746, margin 1.109, 4 poses past H1 (BDp 1). **Correction.** "BDp 4.66" is BDp's **bench** margin; held vs held it is 1.11 vs **2.67**. **Size.** 4 / 952 held ws poses = about 0.42 points. |
| G4 | no | **Margins.** min own 5.623 / 5.586; lt10 107 of 380 (held 273 of 887); plain dyad on forced poses -22.763. **Swing.** J1 gain 3.30 / 2.29, 31 deg per frame. **Context.** BDp swings more (3.41 / 2.55 / 35 deg) with lt10 98 of 370, so this is not a polish regression. |
| M5 | no | **Hold check.** Drift 3.72 upright and 5.69 / 6.12 / 4.12 / 7.70 tilted (3 of 4 over 5); twist up to 3.83; 9.28 at 0.08 N.m. **Red team.** Demand 0.048 N.m; Reach a high shelf moves K 15.8 deg vs BDp 0.85. **Mitigating.** At 2 g upright, K lifts at most 0.47 deg. The tilted cases are a robustness sweep, not the judge's R17 posture. |
| T1 | no | **Numbers.** 18.40 / 23.36 / 41.29 / 156.01; 13 / 38 / 171 poses; the 7 overhead ws floors are 4 / 2 / 1 in the 0-1 / 1-2 / 2-3 mm bins. **Correction.** Priced against longdyad, pick1 is 0.96 ahead plain and 6.66 behind at 2 mm (not 0.51 / 7.26). Information only. |

**Correction that runs through G6, T1 and NEW-mixed-protocol** (stop pricing, not a design change):
- pick1 and BDp are read at the judge's built-stop pricing: rule 5.5, J2 slot +0.5 (`rows polished_pricing`;
  probe `fold_margin_env` 5.5).
- The 3-joint numbers they are set against (18.91, 18.67, 19.13; 22.67, 23.73, 22.03) are unpriced (smlo 5.0). The
  sidecar-longdyad skeptic's NEW-unpriced-stops finding says so.
- Like-for-like, against sidecar-longdyad's own priced reading (19.36 / 23.29 / 1 mm 20.45 / 26.39 / 2 mm 34.63),
  pick1's lead is **+0.96 bench and +0.60 held out**. That is about 3.5 and 2 workspace poses, larger than the
  audit says.
- No priced number is on file for roller-longdyad or sidecar-parallelogram.
- This favours minarc, but it does not change any level. The 4th joint, the deeper contact and the overhead count
  are wearer facts either way.
- Proposal for the next audit (a measurement change, not used here): compare a priced claim only with priced
  references, or price both.

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **K runs to within 0.1 deg of stop B, and stop B carries no build tolerance.**
   - Stop B sits at the 5-deg rule cut, dK 56.652 (`rows polished_pricing`).
   - The taken K reaches 56.244 deg on the bench and **56.551 deg held out**, 0.10 deg from the stop
     (`_pick1_probe_{bench,held}.json` K_open_deg_taken.max).
   - The J2 slot is priced +0.5 for machining; stop B is not.
   - A stop B that engages 0.5 deg early would cut every pose that needs K above 56.15 deg. The count is not
     measured, because the probe stores only the maximum.
   - This is the same pattern as roller-longdyad's dK 46.17 of 46.25: a coordinate parked at its cutoff.
   - Proposal (measurement change): re-wear pick1 with stop B at 56.15 and report the delta.
2. **The audit report contradicts itself about the slot file.**
   - "Not measured" says pick1's bench output is written to `remeasure/minarc-stop-knuckle-4r_bench.json`.
   - That file's `config` field is BDp (19.54), as the "Checks of the tool" section states correctly.
   - So the tool's `near_touch`, `held_out` and `fast_frozen` checks describe BDp, not the claim. pick1's own
     numbers put those checks at the same levels (near_touch watch 22.89; held drop 4.29; fast drop 12.21 < 14).

**Notes** (not gaming):
- No new gaming pattern was found.
- The refuted `continuity` reason is a format gap in the tool, which reads only a `connected_full` / `connected_knn`
  dict. Both floods of the verifier are on file and drop 0 poses. A tool fix (read `connected.dropped_unconnected` and
  the `_conn*.json` files) is a change to the tool and is left to its owner.

## Skeptic (2026-10-17, 04:30-04:45 UTC, simplicity v2 metric-change audit)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and changed
no score. It re-derived each reason from the probe files, the verifier files, the rows, `tools/simplicity.py` and the
pick1 CAD parts list. It re-ran the auditor's determinacy tool on both configs. Local CPU only, at most 2 processes.
Farm spend $0.

**Final verdict (ledger, `stage skeptic`, 2026-10-17T04:44:39Z): WATCH.** None of the 16 reasons was refuted, and
all stand at 'watch'. The claim is 18.40 (pick1).

**Re-measured here:**
- `tools/alignment_knee_sensing_minarc.py` re-run on pick1 and BDp. Every summary matches the committed files to the
  digit: pick1 0.3691 / cond 2.54 on 1056 taken grid poses, 0.3902 overhead, 0.2839 on the library; BDp 0.0958 / 9.83.
- The finite-difference step was varied from 1e-3 to 1e-5. sigma_min did not change to 4 digits.
- simplicity v1 / v2 was recomputed for every row that has a v_gap, along with the (v_gap, complexity) fronts.
- New: `tools/alignment_knee_ghdrift_minarc_skeptic.py`, output
  `docs/alignment/remeasure/minarc-stop-knuckle-4r_skeptic_ghdrift_arm.json` (see missed item 1).

**Rulings** (also in `docs/alignment/minarc-stop-knuckle-4r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| contact_depth | no | **Re-derived** from the probes' `contact_poses`: bench 11 poses, 34.43 mm summed, deepest -13.17; held out 35 poses, 126.1 mm, deepest -14.61. sidecar-longdyad `_perpose_claim`: 4 poses / 6.23 mm / deepest -4.61 on the bench; 10 / 35.66 / -8.37 held out. **Threshold.** TH depth_ratio 2.0 and floor 5 mm, applied to summed depth: x5.53 (+28.2 mm) and x3.54 (+90.4 mm). **Label slip.** In the condensed reason, "6.23 mm" is the reference's summed depth; its deepest is 4.61 mm. |
| sampling | no | No per-part sample counts in any probe or verify file. Not measured. |
| complexity | no | v2 gives 32.5 against the row's 33.0. The mismatch is over the check's 0.01 tolerance. **Direction.** The stale field overstates complexity by 0.5, so it does not flatter the design. The dashboard already shows 32.5. The notes are stale. |
| reporting | no | morphs.json (04:28): the 18.4 half is the named false positive. The second half is true: sweep_gap 6.19 sits 13.35 under the verified number, and the verdict text is "VERIFIED LEADER ... BDp". |
| G6 | no | Numbers confirmed. Complexity v2: 32.5 / 29.5 / 24.25 (v1: 52 / 49 / 43.75). The earlier pricing correction still applies: pick1 leads priced longdyad by +0.96 bench and +0.60 held out. It is still a 4th joint for a few workspace poses, none of them overhead. |
| NEW-overhead-traded | no | overhead140_ws taken: 7 vs 8 of 28 (bench), 12 vs 16 of 71 (fit-60 held out), 16 vs 17 (env fit). why_not: contact 5. K is open on 0 of 7 ws and 0 of 10 clip poses at elevation >= 140. |
| NEW-depth-blind-contact | no | contact_raw: 11 vs 4 bench (-13.17 vs -6.41); 35 vs 13 fit-60 held out; 28 vs 9 env-fit held out. 5 of 11 bench and 16 of 35 held-out contacts are at elevation >= 150. |
| G5 | no | The subtraction leaves B 4, J 4, R 0, made 10, bought 10, which is exactly mechanism_A. In the CAD (parts 15-22) the knee has no encoder, no MR63ZZ and no shared plate; the template is within 1 part. The stale 33.0 and notes are confirmed. |
| R2 | no | The row's verdict / v_verdict and the dashboard verdict open "VERIFIED LEADER" (BDp). The dashboard row mixes pick1 and BDp. |
| NEW-mixed-protocol | no | README line 33 gives 21.31 (env fit, `polished_held_out.env_fit`). Line 36 gives 22.67 (fit-60). |
| T4 | no | verifier.knee held out: ang_min 26.1449, max 152.746, margin 1.109, outside_H1 4 (BDp: 2.665, 1). |
| G4 | no | th_margin_own_state: min 5.623, lt10 107, plain dyad on forced -22.763 (BDp: lt10 98, -10.867). |
| M5 | no | k_hold_check line 16: 5.69 / 6.12 / 4.12 / 7.70. Line 48: twist 3.83. CAD part 6 still names a 0.08 N.m preload (already known). |
| T1 | no | near1 / 2 / 3 poses: 13 / 38 / 171. All 7 overhead ws poses are under 3 mm (4 under 1 mm). |
| NEW-hub-only-sensing | no | **Reproduced** to the digit, stable over the FD step. **Structure.** In the null space K's row is (0, 0, 0, 1), so hub4 determinacy reduces to forward kinematics of J1-J3 at fixed K. K's encoder is required on forced poses. **R10 caveat is larger than reported:** see missed item 1. |
| P4 | no | c_judge_change compares only gap / v_gap, confirmed in the code. Every knee row moves by -19.5. The tie-break is unchanged. The v2 front is roller-longdyad, rim-lobe, geneva-tail and skin-normal (plus minarc at 18.40). There is no flip that involves minarc. |

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **The R10 caveat understates the arm error that hub-only sensing makes under GH drift.**
   - What the audit reported: the knee's member-3 twist, 1.69 deg/mm (pick1) and 1.91 (BDp).
   - What a fixed-GH estimator gets wrong: it inverts the 4 hub rows and reads a GH rotation that did not happen.
     That error is the twist times the gain from J3 to the arm.
   - pick1: median 0.68, max **2.03 deg/mm** (overhead 1.84); **8.1 deg at R10's 4 mm**.
   - BDp: median 0.70, max **7.66 deg/mm** (overhead 6.19), 30.6 deg at 4 mm. Its ill-conditioned poses
     (sigma_min 0.096) amplify the drift up to 4x.
   - Assumptions: sn is parallel to u3 within 1.2e-4 deg; J1, K and J2 are held by their stop or spring.
   - This matches the sidecar-longdyad skeptic's finding: 0.73-2.41 deg/mm, up to 9.6 deg at 4 mm.
   - It does not change the v2 count. It tells the user what dropping the knee encoders costs once GH translates.
   - Tool: `tools/alignment_knee_ghdrift_minarc_skeptic.py`. Output:
     `remeasure/minarc-stop-knuckle-4r_skeptic_ghdrift_arm.json`.
2. **A label slip in the condensed contact_depth reason.**
   - It sets pick1's deepest contact (13.17 mm) against sidecar-longdyad's "6.23 mm". 6.23 is the reference's
     *summed* depth.
   - The reference's deepest contact is 4.61 mm bench and 8.37 mm held out (`_perpose_claim`). The audit's table says
     -8.31.
   - The check itself compares summed depths correctly.
3. **Carried over, still open:** K reaches 56.55 deg held out, against stop B at 56.65 deg, and stop B carries no build
   tolerance (02:40 skeptic, missed item 1). Not re-measured here.

**Questions for the user** (added to the audit's):
- Under GH drift, hub-only sensing reads up to about 2 deg of false arm rotation per mm on pick1, and up to 7.7 on BDp.
  Is that acceptable for MVP2 control? Or should "no encoders needed" be conditional on a bound on that error, for
  example under 1 deg/mm at the taken poses? That bound would be a tightening, and it would be measured per row.

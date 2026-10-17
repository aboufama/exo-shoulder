# Alignment audit: desmo-slipper-knuckle-3r

Auditor run `audit:desmo-slipper-knuckle-3r`, 2026-10-17 17:20-17:50 UTC (discovery round 12, slice r12-A verified this
design this round). Reference: slipper-nose-knuckle-3r, the verified 3-active lead (18.49), whose drive this design
rebuilds without its clock spring. Tool VERSION 2026-10-17.4. Farm closed (the 12-hour budget line was reached before
this audit), so every re-wear ran locally, niced, at most 2 processes.

## Verdict and claim

- **Claim:** v_gap **18.95** (score 93.11), Bench(110,360) exact, frozen shape, the independent verifier's number at a
  RE-PLACED stage-1 pin (a_s 9.5, psi 150) with the groove's blended onset law in the IK. Held out 23.90. The claim's
  own placement (a_s 9.25, psi 154: 18.63) failed its own 0.25-deg crank-free slop gate under the verifier's dense
  scan (`docs/concepts/rows/desmo-slipper-knuckle-3r.json` verification).
- **Ledger verdict: WATCH** (2026-10-17T17:46:26Z, claim 18.95 v_gap) (`docs/alignment/ledger.jsonl`, entry by auditor, run
  `audit:desmo-slipper-knuckle-3r`). The tool's own verdict is watch (reporting only: the dashboard's sweep best 12.79 sits 6.16 below the verified number); the judgement pass adds 8 watch
  findings and no gamed one.
- **In one line:** the verified number is honest and reproduces (19.00 through the model's own IK, 18.95 with the
  verifier's blended IK); the design is not ranked above a better one (it is 0.46 behind the lead on the same poses).
  Its real gain - no clock spring, so no preload, no spring lag, no M5 hold problem - is one the score cannot see, and
  so is its new risk: the sliding stage 1 jams outright at mu 0.14, where the lead's rolling stage 1 loses 1.9 points.

## What the wearer gets (measured)

Re-worn here with the model UNCHANGED (`tools/alignment_audit.py remeasure`, only `PK.audit` wrapped) at the verified
placement, passed by hand (`docs/alignment/remeasure/desmo-slipper-knuckle-3r_vconfig_params.json`) because the row's
best_params is the refuted placement (finding 3). The model's own IK uses the linear K law, the verifier's the blended
law; the 0.05 difference is the one the verifier measured on the claim placement (-0.04).

| | desmo-slipper (this audit, verified placement) | lead slipper-nose (its audit) |
|---|---|---|
| frozen exact Bench(110,360), model IK / verifier IK | 19.0 / 18.95 (reach 0.725, in-band14 0.8904, contact 0.0054; 575.9 s) | 18.49 |
| held out, model IK | 23.95 (verifier 23.90); reach 0.6828, in-band14 0.8893, contact 0.0116; near 1 / 2 mm 27.04 / 37.52 | 23.45 (verifier 23.45) |
| reach, workspace | 261 / 360 (0.725); held 650 / 952 | 261 / 360; held 650 / 952 |
| overhead (elev >= 140) taken / total | 8 / 28 (held 18 / 71) | 8 / 28 (held 18 / 71) |
| raised arm (elev >= 90) | 46 / 113 (held 114 / 300) | 46 / 113 (held 114 / 300) |
| taken poses with metal < 1 / 2 / 3 mm, bench | 3 / 30 / 100 (9 overhead under 2 mm) | 3 / 30 / 100 |
| taken poses with metal < 2 mm, held out | 67 (< 1 mm: 14; 18 overhead) | 67 (< 1 mm: 14) |
| contact poses, bench | 2: 9.01 mm at (15, 165, -60), 5.72 mm at (30, 165, -60); sum 14.72 mm | 2: 9.01 / 5.74 mm, sum 14.75 mm |
| contact poses, held out | 10, sum 46.14 mm, deepest 9.05 mm at (30, 165, -45); 4 below elev 150: 3.49 / 5.51 / 1.60 mm at elev 60, 1.22 mm at (15, 105, 15) | 10, sum 46.12 mm, deepest 9.06 mm |
| workspace in-band 2-14 (unscored), all / elev 90-140 / overhead | 0.8534 / 0.8009 / 0.9378 (over 14 mm: 0.1447 / 0.1983 / 0.06; p95 19.98 mm, max 30.8 mm at elev 90-140 / all) | 0.856 / 0.8004 / 0.94 (over 14 mm 0.142 / 0.1987 / 0.0577) |
| fold margin in th, min over taken (K on its law) | 5.181 deg (held 5.006) | 5.181 deg (held 5.006) |
| lowest metal, overhead p10 | 1.82 mm | 1.82 mm |

Files: `docs/alignment/remeasure/desmo-slipper-knuckle-3r_{bench,held,probe_bench,mu_cliff}.json` (this audit) and the verifier's per-pose dumps `docs/alignment/remeasure/desmo-slipper-knuckle-3r_{bench,held}_perpose.json` (recomputed 18.94 / 23.91).

- **Clip metal histogram (scored frames, bench):** 0.01 % of samples under 2 mm, 0.15 % at 2-3 mm, 10.9 % over 14 mm.
  Reading the band as 3-14 mm costs 0.15 points (19.15): the band edge is not exploited (T2 clean).
- **Near-touch (report-only, user ruling 2026-10-17):** 1 mm 20.63, 2 mm 33.50, 3 mm 83.87 (bench); 14.50 points live
  in the 1-2 mm shell, under the 15-point T1 watch line, and the lead's 14.53. The lowest metal, 0.072 mm, is the
  lead's own pose 139 on the cuff end E.
- **Springs:** none. The clock spring, its 6-mm cap, stop A and the stage-1 roller are gone; K is held both ways by the
  groove (stage 1) and the two-walled slot (stage 2). This is a real gain for the wearer that the score does not show:
  the lead's spring lagged 0.42-0.53 deg and its forward-stroke bound fails the judge's gate by 0.0008 deg at mu 0.15
  (the lead's own M5 watch).
- **Stops:** the slot's end cap is stop A, the groove's dwell holds K at rest; the drive range ends at K 49.5 (stage-2
  horn pressure angle, as on the lead). Taken K reaches 45.62 deg (held 46.27).
- **Friction (new, measured here):** the stage-1 pin's cap-side pressure angle is 35.25 deg at the dwell exit, which K crosses on its way to
  any of the 188 taken bench poses that need it off rest. The drive
  holds to mu 0.135 and jams from mu 0.14 (model rule; 0.172 under the judge's 45-deg rule): K never leaves the dwell and
  the fast gap goes 14.84 -> 86.71. The lead at mu 0.15 keeps 43.0 deg of drive and 14.88
  (`docs/alignment/remeasure/desmo-slipper-knuckle-3r_mu_cliff.json`).
- **K slop / cuff twist:** crank-free K play 0.188 deg worst inside the taken range at nominal fit (verifier's dense
  scan), about 0.36 deg in series with the slot, 0.48 at the groove's worst tolerance. Not on the bench (the models carry
  no slop state).
- **Near-singular postures:** min fold margin in th 5.181 deg bench, 5.006 held out, read with K on its law; the K play
  costs about 0.1 deg (finding T3). Stage-1 pin-side pressure angle up to 31.2 deg over K 0-46 (verified placement, mu 0.12
  run); cap side 35.25 at the dwell exit (the binder, see Friction).
- **Continuity:** static 18.95 = full flood 18.95; knn flood 20.62 (+1.67, the lead +1.67); bench-graph flood 51.97 (the
  graph's sparsity, as on every row of this family).
- **Complexity:** 15.75 (tools/simplicity.py v2.2, recomputed) against the lead's 18.25. The count is honest or
  conservative: the record copies the lead's 4 passive rotations / 8 joints, and the row's own note says that if one of
  them is the lead's stage-1 roller spin (which this design no longer has) the count is 13.75; counting the
  ground-crown pin as a made part instead of a bought one adds 0.75. Either way it stays under the lead's 18.25.

Not measured, and why: the arm-vs-hub-2-stack clearance (no geometry of the J2 seat stack in the model; finding M3);
the wear of the 0.23-mm groove ridge and its contact stress (no contact-mechanics model of the groove; finding
NEW-silent-check); the fold margin with K offset by its play per pose (the models carry no slop state; finding T3);
m_sub at rest (the lead's G4) was not re-measured - by construction it is the lead's (same seats, law and rest poses),
but K at rest is now held positively by the groove's dwell instead of a spring on stop A; the held-out wear probe (time box; the held-out re-wear itself ran: 23.95).

## Findings

Each finding is in `docs/alignment/desmo-slipper-knuckle-3r.findings.json` with its evidence. All are watch. None is
gamed: no measurement shows the number ranking this design above a design that is better for the wearer (it ranks
0.46 below the lead on identical poses, losses and contacts, and its complexity edge is real), and no hard rule is
broken (3 active DOF, 0 passive translations, O20 hubs, fold margin 5.006 deg at nominal K).

1. **NEW-friction-cliff (new pattern).** The spring-free drive trades the lead's rolling stage 1 for a sliding pin parked
   0.91 deg under its friction-dependent jam gate at mu 0.12. At mu 0.14 the cap-side pressure angle at the dwell exit
   (35.25 deg, crossed whenever K leaves its rest: 188 of the 371 taken bench poses need K off rest) exceeds 43 - atan(mu) = 35.03 and the drive cannot leave the
   dwell: fast plain 86.71, reach 0.344. The lead loses 1.9 points at mu 0.15. Why the exo is not better than its
   number says: the number is read at mu 0.087; a dry or worn groove is a jammed shoulder. Action: a mu column (0.12 /
   0.15) on every sliding-drive claim; re-place stage 1 for cap-side margin at the dwell exit, or keep the stage-1
   follower and delete only the spring (the spring alone is worth 3 points of the design's 2.5-point net complexity gain).
2. **NEW-silent-check.** The model declares a groove-centreline-radius gate (RC_MIN 1.5 mm, "cuts dK_lim") and never
   enforces it. Enforced, it would stop K at 0.5-0.8 deg at the verified placement (rc 0.99-1.0 mm over the whole onset
   corner). The verifier replaced it by a dense play scan (passes, 0.188 deg inside the taken range), which answers slop
   but not wear: the groove's inner wall at the onset corner is a 0.23-mm ridge loaded at every dwell exit. The onset
   blend that softens the corner sits at its search-box edge (10 of 0-10). Action: enforce the gate or retire it with
   its measured reason; state the ridge and its stress on the L1 CAD.
3. **NEW-refuted-best-params (new pattern).** best_params, gap 13.19, reach 0.775 and the verdict line "paired TIE"
   are the claim placement the verifier refuted on determinacy; v_gap 18.95 is a placement stored only in
   verification.verified_config. Every tool reading best_params (this audit's own remeasure and probe, the viz preview,
   a polish, the CAD) builds the failing placement unless told otherwise. Nothing on the leaderboard is flattered (the
   verified number is the worse one); the risk is building the wrong exo. Action: verified placement into best_params
   (claim's kept as claim_params), or the tools read verified_config.
4. **R2.** The dashboard (rebuilt 17:43: verified, 18.95) still shows a sweep best of 12.79 for this design (score
   95.35, over the golden 95 line); until the rebuild it read "screened" with no verified number. That number is fast, read with the dense outer-wall sampling the screener measured at -0.31 (in-band
   padding), at a placement between two the verifier's dense scan refuted. On the sweep column the design reads ahead
   of the lead (12.79 vs 13.00); verified it is behind (18.95 vs 18.49). Action: sweep rows record their sampling
   convention and slop reading.
5. **T3.** Held-out min fold margin 5.006 deg with K on its law; the drive's 0.36-0.48 deg of K play costs about 0.1 deg
   of th, so the held-out minimum is under 5 with play (verifier's estimate). Same class as the lead's spring lag, smaller.
6. **M3.** The 9.5-mm short arm and the pin pass through hub 2's O20 footprint in the layer of link 1b's J2 seat; no
   check covers them against the hub-2 stack. A 5 x 4 x 1.5 mm relief pocket is assumed, not shown.
7. **T5 (carried).** Two overhead contacts at 9.01 and 5.72 mm deep (sum 14.72 mm, x2.36 the default reference's 6.23
   mm); held out 10, sum 46.14 mm, deepest 9.05 mm. The lead's own contacts, unchanged by the drive.
8. **NEW-ws-inband (carried).** The gap reads in-band on clip frames only. On taken workspace poses at elevation 90-140, 0.8009 of the metal is in 2-14 mm and 0.1983 is above 14 mm (p95 19.98 mm), against 0.8004 / 0.1987 on the lead and 0.8904 on the scored clip frames. Same metal, same poses as the lead; carried.

## Patterns walked and found clean

- **T1 / G1 (metal hugging):** 14.50 points in the 1-2 mm shell (under 15), and 30 taken poses under 2 mm, the same 30
  as the lead (paired dumps). **T2:** band read as 3-14 mm costs 0.15. **T4:** no singularity margin moved by the
  search; the bound at the box edge (blend 10) spends groove radius, not a fold margin (finding 2).
- **S1 / P1:** held out +4.95 (23.90 vs 18.95), the lead's +4.96. **S2:** sample-weighted in-band 0.891 vs part-weighted
  0.898; the ring sector (19 samples at the verified placement, 0.533 in band, median 13.9 mm) and the slot's outer wall
  (horn 61 samples vs the lead's 23) are sampled, and the whole 0.46 against the lead is theirs, all in-band; the short arm and pin are contact-only samples sitting under the ring
  (conservative). **S3:** every declared moving body is sampled (crank 129, horn 61, ring2 19, L1a 8 ...). **S5:**
  full flood = static.
- **M1 / M2:** O20 at every hub, 0 passive translations, every joint a component (ISO 8734 pins, MR63ZZ crank pair).
  **M4:** K moves 45.62 deg; the crank moves with it (phi = dK / g, about 19 deg). **M5:** no spring (see finding 1
  for the positive drive's own failure mode).
- **P2:** the search ran on the fast bench only (near2 objective); the verifier chose its placement by the slop gate
  and friction, not by a held-out number. **P3 / R3:** convergence gate 0.00 / 0.00 / 0.00 over 136 configs (near2 flat
  at the lead's 16.47); one frozen claim, one verifier re-placement with its reason. **P4:** no bench / judge / metric
  file in the row's 3 commits.
- **R1:** status verified with verifier files on disk; the verified number is the verifier's, not the claim's.
- **G2 / G3:** no spring; cuff twist from K play only (<= 0.48 deg of K). **G5 / G6:** complexity recomputed 15.75 =
  row; 3 active DOF, nothing sensed.

## Cross-design check: is the lead's rim lobe unsampled metal? (no)

The screener wrote that the lead's hub-2 rim lobe "was never sampled past O20", so that this design "pays for metal the
lead got for free" (`docs/concepts/desmo-slipper-knuckle-3r.md` item 1). If true, that would be S3 on the reference and
the paired +0.46 against this design would be a sampling artefact. Checked: the lead's lobe crest is 9.62 mm from hub
2's axis on every verifier wear (`docs/concepts/verify/slipper-nose-knuckle-3r_v_bench_frozen.json` and 7 sibling
files, crest_exact), inside the sampled O20 envelope, and its follower roller is sampled (group 'roller', 19 samples,
identical in both re-wears). The lead's spring-loaded follower rides ON the lobe and needs no outer wall; this design's
two-walled groove does (pitch 9.49 + 0.76 + 0.8 = ring to r 11.05 at the verified placement, 19 samples, 0.533 in band,
median 13.9 mm). So the ring sector is new metal, the +0.46 is a fair price of positive return, and the "11.5 skirt"
is the desmo model's own allowance (SKIRT_R = HUB_R + 1.5), not metal on the lead. No finding against the lead.

## Proposals (measurement or reporting changes; none is an input to the verdict)

- **P-1 (catalogue M6, NEW-friction-cliff):** every claim with a sliding drive pair reports its drive range at mu 0.12
  and 0.15 next to the claim's mu, and the friction at which the range collapses. Measured effect on the verified rows
  with sliding drives: this design jams at 0.14 (fast 14.84 -> 86.71); the lead keeps 43.0 deg at 0.15 (fast 13.00 ->
  14.88); other rows not measured here.
- **P-2 (catalogue R5 - the reporting family, not requirement R5 - NEW-refuted-best-params):** a row whose verifier re-places or corrects the config carries the
  verified config in best_params (the claim's in claim_params), and its headline gap / reach / verdict fields read the
  verified numbers. Effect on the verified rows today: only this row has verification.verified_config.
- **P-3:** sweep rows (docs/concepts/sweeps/*.json) record their metal-sampling convention, and the dashboard shows a
  sweep best only with that convention, or re-read at the claim's density.

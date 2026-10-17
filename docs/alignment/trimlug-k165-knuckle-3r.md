# Alignment audit: trimlug-k165-knuckle-3r

Auditor run 2026-10-17 12:46-13:20 UTC (discovery round 11, slice r11-B). Ledger entry `by auditor`, run
`audit:trimlug-k165-knuckle-3r`. Checks: `docs/alignment/trimlug-k165-knuckle-3r.json` (tool VERSION 2026-10-17.2,
`--ref slipper-nose-knuckle-3r`). Findings: `docs/alignment/trimlug-k165-knuckle-3r.findings.json`.

## Verdict: WATCH (no gamed reason; the number is the lead's, and the exo is a little better than the lead where the score does not look)

- **The claim:** v_gap 18.51 (score 93.27), frozen exact Bench(110,360), verified 2026-10-17 12:25 UTC. The design is
  the verified lead slipper-nose-knuckle-3r (18.49) with its horn lug cut back to the farthest flank contact + 1.5 mm
  (r_K <= 21.27 mm). Nothing else changes: drive law, nose, seats, cam table and dK_lim 49.8 are the lead's.
- **Re-worn here, with the model unchanged** (`tools/alignment_trimlug_adapter.py`, a new adapter that wears the claim
  once per bench through the three audit readers; CB_EXACT=1; bench local, held out on the farm):
  - bench 18.51 (reach 0.725 = 261/360, follow 1.0, ib14 0.8953, contact 0.0054 = 2 poses), the claim to the digit
    (`docs/alignment/remeasure/trimlug-k165-knuckle-3r_bench.json`);
  - held out HELD_GAP_PLACEHOLDER (`..._held.json`);
  - near-touch at 1 / 2 / 3 mm: 20.14 / 33.02 / 83.17 (3 / 30 / 100 taken poses); in-band read as 3-14 mm: 18.66.
- **Against the lead, pose by pose** (`docs/alignment/remeasure/trimlug-k165-knuckle-3r_vs_slipper-nose-knuckle-3r_paired_claim.json`):
  - the two take the SAME poses: 0 of 470 bench poses differ in taken or contact (and PAIRED_LEAD_HELD_PLACEHOLDER);
  - the metal floor rises on 60 bench poses (+0.06 to +1.56 mm) and falls on none;
  - the +0.02 gap is all in-band: 3 of the 23 scored lug samples are cut, and they were in band.
- **Reasons, all watch:** 3 tool checks (`continuity`, `idle`, `reporting`) and 7 judgement findings (S1, T5, M5, G4,
  NEW-ws-inband, NEW-stale-complexity-ruler, R1). Five of the findings are carried unchanged from the lead family; one
  (S1) is new and applies to the lead too; one is record-keeping. Two of the tool watches are instrument artefacts,
  measured below (`continuity`: the flood is clean; `idle`: the known knee false positive).

What the trim buys is real and the score cannot see it: contact DEPTH. Pose 264 (30, 165, -60) presses 4.18 mm into the
arm instead of 5.74; the held-out contacts sum HELD_T5_PLACEHOLDER. The score charges the design 0.02 for it, so the
design sits second, behind its own parent. Nothing here ranks it above a design that is better for the wearer.

## What the wearer gets (measured, Bench(110,360) exact unless stated)

| quantity | trimlug (this audit) | lead slipper-nose | file |
|---|---|---|---|
| reach (taken / 360) | 261 (0.725) | 261 | `remeasure/trimlug-k165-knuckle-3r_probe_bench.json` |
| overhead, elev >= 140 | 8 / 28 (0.286): 5/13 at 140-160, 3/15 at 160-200 | 8 / 28 | same, `ws_reach_by_elev` |
| why overhead poses are lost | fold 14, knee slide 4, contact 2 | same | `ws_overhead_why_not` |
| raised arm, elev 90-140 | 38 / 85 (0.447): 26/51 at 90-120, 12/34 at 120-140 | same | same |
| overhead taken poses with metal < 2 / < 3 mm | 4 of 8 / 8 of 8 | 4 / 8 | `ws_overhead140` floor counts |
| all taken poses with metal < 1 / 2 / 3 mm | 3 / 30 / 100 of 371 | 3 / 30 / 100 | `remeasure/..._bench.json` deep |
| min metal over taken poses | 0.072 mm | 0.07 | same |
| contact poses (bench) | 2: 237 (15,165,-60) 9.01 mm (crank; lug 8.35; hub K 2.65), 264 (30,165,-60) 4.18 mm (lug top) | 2: 9.01, 5.74 | `..._bench_perpose.json`, row t5 |
| contact depth sum, bench / held | 13.19 mm / HELD_T5_PLACEHOLDER | 14.75 / 46.12 | per-pose dumps |
| workspace in-band, all taken ws (unscored) | 0.8559, 14.2 % of metal above 14 mm | 0.8560 | `ws_unscored` |
| raised-arm in-band (unscored, elev 90-140) | 0.8002, 19.9 % above 14 mm, p95 20.16 mm, max 30.8 mm | 0.8004 | `ws_elev90_140` |
| held out: in-band of the raised arm | WS_HELD_PLACEHOLDER | 0.822 | `..._probe_held.json` |
| continuity flood (rule 2026-10-16) | full 18.51 (0 dropped), knn 20.18 (6 forced poses), literal bench graph 50.13 | full 18.49, knn 20.16 | `remeasure/trimlug-k165-knuckle-3r_flood_bench.json` |
| fold margin (family reading, th) | 5.181 deg bench (2 poses under 5.5), 5.006 held | same | probe extras; `verify/..._v_held_frozen.json` |
| J1-K-J3 sub-chain margin with K at rest | 106 of 204 rest poses under 5 deg, 50 under 1 deg, min 0.000 (pose 227) | identical pose by pose (max difference 0.000 deg) | `remeasure/..._msub_rest_bench.json` |
| cuff knee | 86.2-151.9 deg over taken poses, window 25.2-154.8 (2.9 deg from its stop) | same | probe extras |
| drive | dK taken 45.62 of 49.8 deg; horn PA 35.8 + friction 4.97 = 40.77 deg (cap 43); crank 34.47 | same | `verify/..._v_bench_frozen.json` |
| springs / cuff twist | one clock spring 0.08 N.m + 0.03 N.m/rad; no R17, dynamics or cuff-twist number on file | same | (not measured) |
| complexity | 22.25 shown; 18.25 with the cuff-knee loop recorded the lead family's way | 22.25 / 18.25 | `tools/simplicity.py` |

Numbers I could not get: cuff twist and spring lag (no dynamics judge has worn this family; R17 is the instrument);
the m_sub rest probe held out (bench only, time box); contact depth under a bulging, real arm (the skin model is rigid).

## Findings

### S1 (watch, new; applies to the lead too): the bench order against sidecar-longdyad flips held out

SEE_S1_PLACEHOLDER

### T5 (watch, carried, improved here): depth-blind contact

T5_MD_PLACEHOLDER

### M5 (watch, carried): one clock spring against a sliding nose, not measured

The lead's upheld finding, unchanged. The spring (0.08 N.m + 0.03 N.m/rad) force-closes the drive through a sliding
O2.37 nose at an assumed mu 0.087 (horn 35.8 + 4.97 = 40.77 deg against the 43 cap, crank 34.47). No dynamics or
preload number is on file. The trim cuts lug metal behind the flank only (verifier T1: the dowel's contact line stays on
retained metal with 2.53 mm to the cut, 1.99 mm over the full stroke), so the risk is the lead's, neither bought nor
reduced. Action: R17 / a preload sweep on the slipper family before CAD.

### G4 (watch, carried): near-singular sub-chain with K at rest

Re-measured pose by pose here (`remeasure/trimlug-k165-knuckle-3r_msub_rest_bench.json`, the model unchanged). With K
at rest on stop A (204 of 371 taken bench poses) the J1-K-J3 sub-chain margin m_sub is under 5 deg on 106 poses, under
1 deg on 50, minimum 0.000 deg at (15, 75, 15). With K moved it is >= 10.8 deg. The claim's fold reading (5.181 bench,
5.006 held) reads m_plain at rest (min 5.389), not m_sub: the open B1 question for the user. The maximum difference to
the lead over the 371 shared poses is 0.000 deg, so this design neither buys nor fixes it. The knee peaks at 151.92 deg
against a 154.78 stop. Action: the user's ruling on B1, which applies to the whole slipper / roller family.

### NEW-ws-inband (watch, carried): the raised-arm standoff the score does not read

The gap reads in-band on clip frames only. On the taken workspace poses at elev 90-140 (38 of 85) this design holds
0.8002 of its metal in 2-14 mm and 19.9 % above 14 mm (p95 20.16 mm, max 30.8 mm): the lead 0.8004, sidecar-longdyad
0.841. Held out WS_HELD_PLACEHOLDER. The trim does not touch it. Action: none for this design; the proposal stands on
the lead's audit.

### NEW-stale-complexity-ruler (watch, carried): the record understates the simplification

The row copies the lead's mechanism record, which charges the cuff knee's closure loop in `closed_loops 3`. Recomputed
here with `tools/simplicity.py` v2.2: 22.25 as recorded, 18.25 with the loop recorded under `cuff_knee` the way
roller-longdyad records it. The dashboard therefore shows this family 2.0 more complex than roller-longdyad (20.25) where
like-for-like it is 2.0 simpler. Reporting against the design. Action: fix the lead's and this row's record (writer's
job, not the auditor's).

### R1 (watch): the row's text

- The row verdict says 5 of the 10 held-out contacts are lug-deepest and 1.2-1.7 mm shallower; the design doc lists 4,
  and the verifier's per-pose reading agrees with 4.
- The headline `gap` 13.02 / `reach` 0.775 are the fit bench's (Bench(60,160) fast), which has no contact pose: the
  bench on which the design's whole subject is invisible. The dashboard's sweep line shows 13.00-13.06 for this id; the
  sweep best 13.02 reads as score 95.27, above the user's golden 95 line, against the verified 93.27 (the tool's
  `reporting` check).
- The limiter calls pose 237 "hub K's disc plus the crank"; the trimmed lug is also 8.35 mm in the skin there.
- `n_configs` 45 against 31 entries in the sweep file (one timestamp); the 14 two-pose exact checks are not on file.

None of it moves the verified number, and every record calls the design "not a lead change". Action: correct the row
text; keep fit-bench numbers out of the headline columns (proposal R-a below).

## Tool checks, read

- `held_out` ok: 23.47 vs 18.51 (+4.96), under the 6-point watch line.
- `fast_frozen` ok: 13.02 -> 18.51 (+5.49).
- `near_touch` ok: re-measured 18.51 / 20.14 / 33.02 / 83.17; 14.51 points live in the 0-2 mm shell (watch at 15).
  Before the re-wear this check read the verifier's LEAD CONTROL file (`_v_bench_lead.json`, 18.49), not the claim's
  (proposal I-a).
- `contact_depth` ok: bench 13.19 mm over 2 poses vs the lead's 14.75 (x0.89); CD_HELD_PLACEHOLDER.
- `dominance` ok: vs the lead plain -0.02, 2 mm +0.00.
- `continuity` watch: no flood "on file" in a shape the tool reads. Measured here: full 18.51, 0 poses dropped (knn 20.18,
  6 forced poses dropped; the lead 18.49 / 20.16). The taken set is the lead's pose for pose and the kinematics are the
  lead's (the trim edits metal only), so this is the lead's flood. Not a design issue (proposal I-b).
- `idle` watch: "knee asserted rigid but moves 65.71 deg". The third occurrence of the same instrument false positive
  (refuted on groove-desmo and on slipper-nose): the model only READS `knee_moved`; the 65.71 deg is the pin knee's
  designed motion (86.21-151.92 deg in its 25.22-154.78 window). K moves 45.61 deg, the crank 19.3 deg (proposal I-c).
- `sampling` ok: sample-weighted 0.895 vs part-weighted 0.924; L1a thinly sampled (8), as the lead.
- `complexity`, `judge_change`, `fold_margin`, `rules` ok.

## Patterns walked and found absent (with the measurement)

- T1 / G1: no shift of metal toward the cutoff: 1 / 2 / 3 mm counts identical to the lead (3 / 30 / 100). The family's
  overhead metal does hug the skin (4 of the 8 taken overhead poses under 2 mm, all 8 under 3 mm), reported, not a
  finding (user 2026-10-17: near-touch is reported only; the 0-2 mm shell is 14.51 points, under the 15 line).
- T2: band read 3-14 mm costs +0.15 (18.66).
- T3 / T4: no bound moved; the th reading is the rule's own (5.181 / 5.006), the knee window and stops are the lead's.
- S2 / S3: no new body; the dense 0.5 mm contact-only lug copy (648 samples) samples the trim edge; lead + dense =
  18.49 / T5 14.74, so the copy hides nothing on the bench, and it is 0.22 mm STRICTER held out (46.35 vs 46.13 sparse).
- S5: flood clean (above).
- M1 / M2: no new part; the trim is a cut on link 1a's existing lug; O20 hubs unchanged; the lead's verifier showed the
  stock O2.5 dowel holds 18.49.
- M3: the dense lug was worn against every member at every taken pose by the verifier: crank 0.153 mm (the lead's
  designed 0.15 running gap over the lug), nose 0.424 mm (its own sliding pair), everything else >= 20.96 mm.
- M4: K 45.6 deg, crank 19.3 deg.
- P1: the trim was designed on the two claim-bench contact poses (237 / 264), but its depth gain travels held out
  (HELD_T5_DELTA_PLACEHOLDER), and the pick (wall 1.5) is not the best-T5 column (wall 1.0: 12.67 / 38.71) - it was chosen on the
  wall, not on a number.
- P2: no search touched the held-out set; five configs were worn held out as columns and the pick is not the held best.
- P3: farm + local verifier repeat identical; this audit's re-wear identical (18.51).
- P4: the dense lug copy is a measurement change made with the design; it is reported as its own column and compared
  dense-to-dense (the held depth gain is 5.76 dense-to-dense, 5.54 against the lead's sparse 46.13).
- R3: the grid spread is reported (fast 13.00-13.40, top-5 spread 0.004 score points).
- G2 / G3: not measurable without R17 (see M5).

## New pattern (proposed catalogue entry)

**S6. The in-band term pays for dead metal (the trim penalty).**
- **Looks like:** removing metal that the mechanism does not use, and that sits in the 2-14 mm band most of the time,
  raises the gap; adding filler metal in band lowers it.
- **Why not better:** the wearer feels the part's height and its worst pose, not the share of its samples in band. Here
  the cut lug is the metal that pressed 5.74 mm into the arm at pose 264.
- **Detect:** `sampling` already reports part-weighted against sample-weighted in-band; flag a design change whose gap
  moves only through the in-band term while its metal floor rises (or falls) on every changed pose.
- **Here:** trimlug +0.02 for cutting 3 in-band lug samples that caused a 1.56 mm deeper press (taken set identical, floor
  up on 60 poses, down on none); the kneeless wedge column of slipper-nose -1.06 for 4.73 g of filler under an unmoved
  crown (`slipper-nose-knuckle-3r.md`, NEW-filler-metal, a control column, not a claim).

## Proposals (not applied; each is a measurement or reporting change for the lead / the user)

- **I-a (tool reading).** `near_touch` takes the newest non-held verifier file with a `gap_near1`; when the verifier
  also wears a control (here `_v_bench_lead.json`, trim off), the check reads the control. Prefer the file whose frozen
  gap equals the row's v_gap (+-0.05). Effect here: 18.49 -> 18.51 plain, shell 14.53 -> 14.51, no level change.
- **I-b (tool reading).** `continuity` should read `docs/alignment/remeasure/<id>_flood_*.json` (`connected` with
  `connected_full`) when its own `frozen.gap` reproduces the claim. Effect here: watch -> ok (full 18.51, 0 dropped).
- **I-c (tool reading, third false positive).** `idle` matches the text `knee_moved` anywhere in the model; match only
  an assignment, or skip when `mechanism.cuff_knee.pins > 0`. Effect: the idle watch disappears here, on slipper-nose and
  on groove-desmo (each refuted by its skeptic).
- **R-a (reporting).** Rows and the dashboard's sweep line should not show a fit-bench gap as a score when the claim
  bench is different (13.02 / 95.27 here, 13.0 / 95.27 on the lead).
- **S6 reading (metric, for the user).** Score in-band part-weighted instead of sample-weighted. Measured on the 16
  verified rows whose audits carry per-part in-band (gap with the verified in-band term replaced by the part-weighted
  one): slipper-nose 18.49 -> 18.04, trimlug 18.51 -> 18.04, roller-longdyad 18.67 -> 18.04, dipped-law 18.64 -> 18.57,
  sidecar-longdyad 18.91 -> 18.57, sidecar-parallelogram 19.13 -> 19.13, sidecar-roller-flank 20.08 -> 19.11,
  kneeless-roller 21.07 -> 20.12, kneeless-sidecar 21.11 -> 19.95, groove-desmo 22.64 -> 22.50, frontload 22.82 ->
  28.45, geneva-tail 23.57 -> 29.26, cam-unfold-4th 26.70 -> 31.56, skin-normal-3r-pin-knee 27.20 -> 26.73, raglan 27.82
  -> 27.28, k-rim-lobe-stub 44.79 -> 52.04 (part lists from each `docs/alignment/<id>.json` sampling check; 9 verified
  rows have none on file). It removes the trim penalty (trimlug ties its parent) and punishes rows with a far-off,
  lightly sampled part; it also LOOSENS the knuckle family (part-weighted in-band >= 0.90 caps the term at 0). A
  measurement change; the user's call, not an input to this verdict.

## What happens next

- The trim is worth keeping in the lead's CAD (a cut, no part, no joint): pose 264 presses 1.56 mm less; held out the
  contacts sum HELD_T5_DELTA2_PLACEHOLDER less. It does not clear 264 (the lug band behind the stroke end, the crank's
  side wall and hub 2's housing all stay in), so overhead stays 8 / 28.
- The S1 flip is the family's: the next audit of slipper-nose should carry it, and the round planner should read the
  pooled bench + held order before naming a winner between the slipper family and sidecar-longdyad.
- The three instrument fixes (I-a, I-b, I-c) belong to the audit tool's owner; each needs `selftest` after the change.

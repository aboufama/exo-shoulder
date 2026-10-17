# Alignment audit: trimlug-k165-knuckle-3r

Auditor run 2026-10-17 12:46-13:07 UTC (discovery round 11, slice r11-B). Ledger entry 2026-10-17T13:06:57Z, `by auditor`, run
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
  - held out 23.47 (reach 0.6828, 10 contact poses; farm, 744 s, ~$0.07; `..._held.json`), near-touch 26.56 / 36.97 / 79.28;
  - near-touch at 1 / 2 / 3 mm: 20.14 / 33.02 / 83.17 (3 / 30 / 100 taken poses); in-band read as 3-14 mm: 18.66.
- **Against the lead, pose by pose** (`docs/alignment/remeasure/trimlug-k165-knuckle-3r_vs_slipper-nose-knuckle-3r_paired_claim.json`):
  - the two take the SAME poses: 0 of 470 bench poses differ in taken or contact (and 0 of 1154 held out; the same 10 held contact poses);
  - the metal floor rises on 60 bench poses (+0.06 to +1.56 mm) and falls on none;
  - the +0.02 gap is all in-band: 3 of the 23 scored lug samples are cut, and they were in band.
- **Reasons, all watch:** 3 tool checks (`continuity`, `idle`, `reporting`) and 7 judgement findings (S1, T5, M5, G4,
  NEW-ws-inband, NEW-stale-complexity-ruler, R1). Five of the findings are carried unchanged from the lead family; one
  (S1) is new and applies to the lead too; one is record-keeping. Two of the tool watches are instrument artefacts,
  measured below (`continuity`: the flood is clean; `idle`: the known knee false positive).

What the trim buys is real and the score cannot see it: contact DEPTH. Pose 264 (30, 165, -60) presses 4.18 mm into the
arm instead of 5.74; the held-out contacts sum 40.58 mm instead of 46.12 (the same 10 poses; 4 of them 0.9-1.7 mm shallower). The score charges the design 0.02 for it, so the
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
| contact depth sum, bench / held | 13.19 mm / 40.58 mm (10 poses, deepest 9.05 at (30,165,-45), 7 deeper than 3 mm) | 14.75 / 46.12 | per-pose dumps |
| workspace in-band, all taken ws (unscored) | 0.8559, 14.2 % of metal above 14 mm | 0.8560 | `ws_unscored` |
| raised-arm in-band (unscored, elev 90-140) | 0.8002, 19.9 % above 14 mm, p95 20.16 mm, max 30.8 mm | 0.8004 | `ws_elev90_140` |
| held out: raised-arm in-band; overhead taken; overhead poses under 2 / 3 mm | 0.8218; 18 / 71; 10 / 18 of 18 | 0.8218; 18 / 71; 10 / 18 | `..._probe_held.json` |
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

Paired per pose on the claim dumps of both designs
(`remeasure/trimlug-k165-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_claim.json`, 4000 bootstrap resamples within
kind; diff = trimlug - sidecar-longdyad, negative = trimlug better):

| wear | diff | reach | in-band | contact | 90 % interval | P(trimlug better) |
|---|---|---|---|---|---|---|
| bench | -0.40 | 0.00 | +0.13 | **-0.53** (2 contact poses vs 4) | [-2.74, +1.67] | 0.64 |
| held out | **+0.81** | +0.74 (21 poses only trimlug takes, 28 only sidecar) | +0.07 | +0.01 | [-0.68, +2.16] | 0.19 |
| pooled bench + held | +0.47 | +0.53 | +0.09 | -0.15 | [-0.77, +1.62] | 0.27 |

- **Why it matters:** the leaderboard puts the slipper family (18.49 / 18.51) above sidecar-longdyad (18.91). The whole
  bench margin is two fewer contact poses, and those two press deep (13.19 mm summed against 6.23 mm over 4, see T5).
  Out of sample the order reverses (23.47 against 22.67; at 1 mm 26.56 against 25.75), and the pooled data favour
  sidecar-longdyad with P 0.73.
- **Why it is only watch:** neither interval excludes 0, and sidecar-longdyad is not better on every count for the
  wearer: at 2 mm it is worse (34.03 against 33.02 bench, 37.24 against 36.97 held) and it touches on 4 bench poses.
- **Action:** the round planner and the closer should read the pooled bench + held order between the slipper family
  and sidecar-longdyad before naming a winner; the next audit of slipper-nose should carry this finding.

### T5 (watch, carried, improved here): depth-blind contact

- **Bench** (per-pose dump of this re-wear): 2 contacts, 237 (15, 165, -60) 9.01 mm (the crank; the trimmed lug is
  also 8.35 mm in, hub K's disc 2.65) and 264 (30, 165, -60) 4.18 mm (the lug top; the lead 5.74). Sum 13.19 mm against
  the lead's 14.75.
- **Held out:** the lead's same 10 contact poses, sum 40.58 mm against 46.12; deepest 9.05 mm at (30, 165, -45), the
  crank, untouched; 7 deeper than 3 mm. Four get shallower: (15, 150, -60) 7.07 -> 6.13, (60, 165, -30) 6.87 -> 5.15,
  (45, 165, -45) 5.80 -> 4.18, (30, 150, -45) 5.33 -> 4.07. Four, not the row's five.
- **Why it matters:** the score is blind to depth both ways. It does not reward this design for pressing 1.56 / 5.54 mm
  less (it charges +0.02), and it ranks the family above sidecar-longdyad, which presses 6.23 mm over 4 bench poses
  (x2.12, +6.96 mm: past the tool's own T5 margin) and 35.66 held (x1.14).
- **Why it is only watch:** T5 never gives gamed (user 2026-10-17), and sidecar-longdyad is worse at 2 mm.
- **Action:** none for this design; it is the depth fix the family needed. Pose 264 needs the lug to end at r_K ~18
  (dK ~35, the stroke wall), a 0.5 mm narrower crank tip and a 0.3 mm flat on hub 2, per the design's own limiter.

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
0.841. Held out 0.8218 / 17.6 % above 14 mm (the lead 0.8218). The trim does not touch it. Action: none for this design; the proposal stands on
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
- `contact_depth` ok: bench 13.19 mm over 2 poses vs the lead's 14.75 (x0.89); held 40.58 mm over 10 vs 46.12 (x0.88).
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
  (held out -5.54 mm on the same 10 poses, against -1.56 on the bench), and the pick (wall 1.5) is not the best-T5 column (wall 1.0: 12.67 / 38.71) - it was chosen on the
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
  contacts sum 5.54 mm less (46.12 -> 40.58). It does not clear 264 (the lug band behind the stroke end, the crank's
  side wall and hub 2's housing all stay in), so overhead stays 8 / 28.
- The S1 flip is the family's: the next audit of slipper-nose should carry it, and the round planner should read the
  pooled bench + held order before naming a winner between the slipper family and sidecar-longdyad.
- The three instrument fixes (I-a, I-b, I-c) belong to the audit tool's owner; each needs `selftest` after the change.

## Skeptic (2026-10-17 13:08-13:20 UTC)

Ledger entry 2026-10-17T13:18:11Z, `by skeptic`, run `skeptic:trimlug-k165-knuckle-3r`. Rulings:
`docs/alignment/trimlug-k165-knuckle-3r.rulings.json`.

**Final verdict: WATCH.** 6 of the 10 reasons are upheld: reporting, T5, M5, G4, NEW-ws-inband, R1. 4 are refuted
with evidence: continuity, idle, S1, NEW-stale-complexity-ruler. No reason reaches gamed.

What I re-measured or re-derived (models unchanged):

- **The continuity flood, re-run by me.** Same lead-module `frozen_flood`, model class TLModel, CB_EXACT=1, 144.7 s,
  output in scratch, not committed. It matches the file on record exactly: full 18.51 with 0 dropped, knn 20.18 with 6
  dropped, bench graph 50.13 with 113 dropped.
- **The paired bootstrap against sidecar-longdyad,** re-run with seeds 1-3:
  - bench -0.40, interval [-2.76, +1.69], P 0.62-0.63;
  - held out +0.81, interval [-0.65, +2.17], P 0.18-0.19.
- **Contact depth from the dumps:** bench 13.19 / 14.75 / 6.23 mm (trimlug / lead / sidecar-longdyad), held out
  40.58 / 46.12 / 35.66. Four held-out contacts get shallower, not five.
- **Against the lead, pose by pose:** 0 of 470 bench and 0 of 1154 held-out poses differ in taken or contact. The metal
  floor rises on 60 bench and 135 held-out poses and falls on none.
- **Complexity, recomputed** with `tools/simplicity.py` v2.2: 22.25 as recorded, 18.25 with the roller-longdyad
  convention.

### Rulings

| key | ruling | evidence (short; full text in the rulings file) |
|---|---|---|
| continuity | **refuted** | The flood is on file (`remeasure/..._flood_bench.json` `connected.connected_full`: 18.51, 0 dropped) and my re-run is identical. The tool's own rule reads full (loss 0.00 <= 1.0); knn +1.67 is under the 3.0 escalation line, so the check reads ok. Same as the lead (18.49 / 20.16). The watch comes from the tool not reading the file (I-b). Process gap: the verifier's files carry no `connected` key. |
| idle | **refuted** | The model only reads `knee_moved` (line 167; SN_CELL lead at line 37); only the kneeless models set it. The 65.71 deg is the pin knee's designed travel, 86.21-151.92 inside [25.22, 154.78]. K moves 45.61 deg and the crank 19.3, both far above 2.0. The third occurrence (I-c). |
| reporting | upheld | Status verified, but the verdict text starts "screened -". The dashboard shows sweep 13.02 (score 95.27) against verified 18.51, and gap 13.02 / reach 0.775 from the fit bench. |
| S1 | **refuted** | The numbers reproduce, but the watch level does not follow. The documented S1 line is the held-out drop: +4.96 against TH 6.0, and the tool reads ok. Every interval includes 0, so neither the bench win nor the held-out loss is established. Ranking on pooled bench + held out would be a rule change (proposal only). The pair's order flips with the flood reading: knn 20.18 vs 21.72, bench graph 50.13 vs 43.40. The contact-count share is T5's. 0 poses differ from the lead. |
| T5 | upheld | The documented margin is met against sidecar-longdyad on the bench: x2.12 and +6.96 mm. Both sides are claim dumps on an unchanged bench. The rank over sidecar is exactly the trade of 2 deep presses for 4 shallow ones. Correction: at 237 the 8.35 mm is the body-1 contact group; the rigid horn reads 6.75 mm. |
| M5 | upheld | No R17 or dynamics output exists. The red team (`docs/research/slipper_mechanism_redteam.md`) is quasi-static: return factor 92-158, hysteresis <= 0.020 N.m. It also measures the lag M5 is about: K lag -0.42 to -0.53 deg takes the held-out th margin to 4.950-4.966 unless a +0.75 deg K lead is built in, and the claim's model does not carry that lead. |
| G4 | upheld | Confirmed: m_sub at rest is under 5 deg on 106 of 204 poses, min 0.000. The active chain at rest passes (m_plain 5.389), but m_sub at rest is the open B1 question for the user and depends on K holding its stop (M5). |
| NEW-ws-inband | upheld | Confirmed. Raised-arm in-band 0.8002, 19.9 % of the metal above 14 mm, max 30.8 mm (held out 0.8218). The 2-14 mm band is the goal's own. |
| NEW-stale-complexity-ruler | **refuted** | The measurement is right (22.25 vs 18.25), but the error overstates this design by 4.0. It cannot raise its score or rank, and G5 is the opposite direction (complexity hidden). The tool's complexity check reads ok. The record fix stays a writer's action. |
| R1 | upheld | Confirmed, and the errors flatter the design: 5 vs 4 shallower contacts; fit-bench gap and reach as the headline; the lug left out of the limiter at 237; n_configs 45 against 31 sweep entries. |

### Missed by the audit (not counted in this verdict; for the next audit)

1. **The held-out fold margin depends on the K lag of a real build.** Applies to the whole slipper family, the lead too.
   - The claim reads min th 5.006 deg held out (`verify/trimlug-k165-knuckle-3r_v_held_frozen.json`
     `extra.th_margin.min`, at ws (135, 30, -135), a forced pose). That is 0.006 deg above the user's 5 deg rule.
   - The red team's slaved-law re-solve (`docs/research/slipper_mechanism_redteam.md`, verdict item 2 and finding 9;
     committed a3b0434 before this audit's ledger entry) predicts a systematic K lag of -0.42 to -0.53 deg, with
     +-0.24 deg random. A lag of only 0.07-0.1 deg puts a held-out pose under 5 deg, and -0.5 to -0.7 deg reads
     4.966-4.950 with 2 poses under 5.
   - The +0.75 deg K lead that fixes it is a build instruction. The claim's model does not carry it.
   - Pattern: M5 / T3. A spring-slaved coordinate scored at its planned value, on a margin that sits at the rule's edge.
2. **The modelled lobe follower is not the real part.** Pattern M1 / M2, the gen-6 drive carried by the family.
   - The red team (lines 53-56 and 185-186) finds the modelled follower (s_arm 4.0 on r 8.27) inside hub 2's O20.
   - The real part is an MR63ZZ on a 6.5 mm arm at psi 216, with the lobe ring at r 10.79-12.77.
   - The real lobe ring, the follower plate and the 10 mm straddle boss are unsampled ("the CAD sweep decides them").
   - So the claim's metal does not include parts the build must carry. The audit's M1 / M2 walk read "no new part" and
     missed this.
3. **The verifier skipped the continuity flood the 2026-10-16 rule asks of it.** No
   `docs/concepts/verify/trimlug-k165-knuckle-3r_*.json` has a `connected` block. The audit's flood (re-run here) is
   clean, so nothing is lost. It is a protocol gap, not a number.

Reported, not a finding:
- The model's `t5()` part breakdown covers only `M.rigid` / `M.contact`. At 3 of the 10 held-out contacts the deepest
  member is unnamed: 224 (-90, 60, 105) depth 3.49 with listed parts to 1.70; 252 (-75, 60, 105) depth 1.60 with none;
  820 (75, 150, -90) depth 0.18 with none.
- Two of those (224 and 252), and 225 (5.51 mm), are elevation-60 contacts at plane -90 / -75, not overhead.

### What happens next

- Fix the audit tool (I-b, I-c), then run `selftest`. This row's refuted `continuity` / `idle` rulings will hold it to ok.
- R17 on the slipper CAD at mu 0.087 / 0.12 / 0.15, as M5 asks.
- Re-measure the held-out th margin with the +0.75 deg K lead and with the worst-case lag as claim columns.
- Re-wear the claim with the real follower, lobe ring and straddle boss sampled.
- Correct the row text: 4 contacts, not 5; fit-bench numbers out of the headline; the limiter at 237; n_configs.
- Fix the complexity record (cuff_knee.closed_loops).

# Alignment audit: baseline-3r (2026-10-19)

Auditor: the alignment auditor (hourly backlog audit, the oldest backlog item; no earlier ledger entry). Tool
`tools/alignment_audit.py` VERSION 2026-10-19.1. Ledger entry: `python3 tools/alignment_ledger.py get baseline-3r`.

## Verdict: WATCH (the ledger's verdict; the tool alone also reads watch)

The claim is the screened row's gap **68.93** (score 74.93): the swarm's reference, "the bar to beat", a plain
spherical 3R (O20 hubs, 8 x 3 mm straps) written by `tools/concept_baseline.py` on 2026-10-15 15:59 UTC on
Bench(60,160) fast, and rebuilt unchanged in `docs/concepts/models/baseline-3r-kit.py`. Nothing in it is gamed: it is
not a leader, it is not shown as verified, and its number does not rank it above a design that is better for the
wearer. It carries seven watch-level findings. Most of them say the bar is measured under a protocol the rows compared
with it do not use.

Re-measured here with the model file unchanged (new adapter `tools/alignment_baseline3r_rewear.py`; the generic
kit re-wear tool expects other parameter names):

| wear | gap | reach | follow | in-band 14 | contact | near 1 mm | near 2 mm (poses) | file |
|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast, the claim's conventions | 68.93 (reproduced to the digit) | 0.775 | 1.000 | 0.4381 | 0.1024 | 70.04 | 99.21 (24) | `remeasure/baseline-3r_fit60.json` |
| same, kit honest (K3 march, K2 dense, K6) | 70.27 | 0.775 | 1.000 | 0.4247 | 0.1024 | 70.27 | 71.83 (2) | `remeasure/baseline-3r_honest_fit60.json` |
| claim frozen on Bench(110,360) exact | **73.76** | 0.7389 | 1.000 | 0.4367 | 0.1132 | 74.79 | 116.93 (66) | `remeasure/baseline-3r_bench.json` |
| claim frozen held out (disjoint poses, exact) | 74.42 | 0.7278 | 1.000 | 0.4380 | 0.1100 | 75.98 | 117.01 (63) | `remeasure/baseline-3r_held.json` |

- Fast to frozen exact costs +4.83 points. Held out costs a further +0.66, so the fit is not tuned to its sample.
- The fit's profiles are frozen for the wear; no strap changed its sample count, so nothing was resampled.
- The per-pose dumps reproduce each gap within 0.01: `_fit60_perpose.json` 68.94, `_bench_perpose.json` 73.76,
  `_held_perpose.json` 74.43.
- The honest run finds 0 flips (K2 dense) and 0 collisions (K6), so the claim's skipped checks hide no jam or clash.
  The 1.34-point difference comes from the 'outer' ray rule, which reads the skin less accurately than the march.

## What the wearer gets (measured)

- **Overhead:** 9 of 28 workspace poses at elev >= 140 are taken on the exact bench, and 7 of 26 held out. 11 of
  the 28 are in contact (9 of 26 held out). On the claim bench it is 4 of 12. By elevation band (taken / total, exact
  bench): 120-140 17/34, 90-120 34/51, below 90 206/247.
- **Raised arm:** 34 of 51 poses at elev 90-120 and 17 of 34 at 120-140 are taken (exact bench).
- **Taken poses with metal under 2 mm:** 66 of 376 on the exact bench (17 of them at elev >= 140) and 63 of 372 held
  out. Every taken pose has its lowest metal under 3 mm (376 of 376). The profile rule is "outermost skin radius + 2
  mm", so this follows by construction.
- **Deepest contact:** 28.63 mm on the exact bench (ws plane 0, elev 120, axial -15) and 28.93 mm held out (elev 120,
  axial -30). There are 48 contact poses summing 526.66 mm on the bench, 41 of them deeper than 3 mm. Held out there
  are 46 poses summing 548.95 mm.
- **Workspace in-band (unscored):** 0.405 over the 124 taken workspace poses on the claim bench, and 0.678 on the 4
  taken overhead poses. Metal median 16.6 mm. 37 % of samples are more than 20 mm off the skin, and the p95 sits at
  the fast cache's 31.75 mm cap (`remeasure/baseline-3r_fit60.json` probe). Hub 2 is never in band: its median metal is at or
  beyond the 31.8 mm cap.
- **Springs, stops, cuff twist:** there are none. It is three free pins and a rigid arm-end. The bench has no GH
  translation and no cuff slide is modelled, so cuff twist from GH slip is not measured. The same holds for every
  design on this bench.
- **Near-singular postures:** none. The min `th` margin is 10.10 deg on the claim and exact benches (p05 16.0) and
  12.12 deg held out, against a declared `sing_deg` of 10. 0 taken poses are under 5 deg or 10 deg.
- **J1 seat:** bvec(2.43, 80.68) = (-0.162, 0.987, 0.007). That is on top of the acromion, slightly posterior, so it
  meets ruling 4 (anterior <= 0.20).
- **Joint motion:** J1, J2 and J3 sweep 352, 349 and 349 deg (circular span over taken poses), so no joint is idle.
  The pins have no stops.

## Findings

1. **P1 in-sample, self-measured bar (watch).** 68.93 is fitted and picked on Bench(60,160) fast and never verified.
   Worn frozen it reads 73.76 on the exact bench and 74.42 held out. The +5.49 held drop is below the +6 watch line,
   but every verified row it is compared with is a frozen exact number. Why the exo is not better: no change, the
   number simply is not on the leaderboard's harness. Action: state the bar as 73.76 / 74.42 (frozen exact) next to
   verified rows.
2. **R3 best-of-6 without the spread (watch).** The p60-p100 profile quantiles read 142.75 / 115.46 / 88.59 / 73.20 /
   68.93 / 74.21 fast. The p95 pick also wins held out (p90 79.14, p95 74.42, p100 79.72), so the choice is sound.
   The spread is now on file (`remeasure/baseline-3r_readouts.json`).
3. **T5 depth-blind contact (watch).** On the claim bench there are 21 contact poses, summing 220.83 mm. The deepest
   is 28.37 mm at elev 150, and 15 are deeper than 3 mm. The lead conecut-knee-knuckle-3r has 20.24 mm over 4 poses
   (x10.91). The p95 pick trades contact for in-band: it takes 3x the contact poses of p100 (0.1024 vs 0.0341 fast,
   0.110 vs 0.038 held). Why not better: metal 28 mm into the arm overhead blocks the arm. The score counts that as one
   pose.
4. **G1 metal hugging by construction (watch).** Every taken pose has its lowest metal under 3 mm. 43.17 points of the
   exact-bench gap live in the 1-2 mm shell. Within its own sweep, p95 beats p100 by 5.28 plain (5.30 held) but loses
   by 9.76 at 2 mm (29.66 held). Near-touch has been report-only since the user's 2026-10-17 ruling, so this stays a
   watch.
5. **S2 sample weighting (watch).** Part-weighted in-band is 0.3646 and sample-weighted is 0.4381, a difference of
   7.35 points (watch line 3, gamed line 8). The parts, with their sample counts out of 667 per pose:

   | part | samples | in-band | notes |
   |---|---|---|---|
   | link1 | 235 | 0.72 | |
   | link2 | 205 | 0.33 | |
   | neck | 80 | 0.015 | median metal 23.5 mm |
   | hub1 | 49 | 0.996 | |
   | hub2 | 49 | 0.00 | median metal >= 31.8 mm |
   | hub3 | 49 | 0.13 | |

   Hub 2 is a bump the wearer feels, however few samples it has.
6. **M2 hub 1 smaller than O20 (watch).** The cap disc is laid out at r_ref 70 mm, so at its fitted 52.3 mm it covers
   54 % of an O20 disc and reaches 7.4 mm. The kit's own audit flags this on every wear, and the row's name says "O20
   hubs". As a what-if, hub 1 was laid out as a true O20 disc (model unchanged, `K.cap_dirs` r_ref = the hub's radius,
   `tools/alignment_baseline3r_readouts.py o20`). The plain gap stays 68.93, but 34 poses instead of 24 have metal
   under 2 mm (2 mm gap 99.21 -> 117.06). The slim hub buys no plain points; it hides near-touch. Hub 2 is the
   opposite quirk: a 31 mm disc at 107 mm. With all three hubs at true O20 the gap is 66.69 (-2.24).
7. **NEW-stale-bar (watch; new catalogue entry proposed below).** The reference is measured under a protocol that no
   row compared with it uses:
   - the 'outer' ray rule with no K2 / K6 (kit honest 70.27, +1.34);
   - a 10 deg fold margin, while the user's rule has been 5 deg since 2026-10-16 (at 5 deg: 67.12 fast, 71.51 held);
   - fast and in-sample, while the leaderboard uses frozen exact numbers (73.76 / 74.42);
   - an oversized hub 2 (-2.24).

   46 events say "vs baseline 68.93" against honest kit screens. For example, pointer-cslide's 69.84 honest is called
   "level with the champion (68.93)", while the honest baseline reads 70.27. The shifts partly cancel. No design
   proven better for the wearer is ranked below the bar (pointer-cslide weighs 741 g with reach 0.50), so this stays a
   watch.

Checks the tool reads as watch that my pass does not support as findings:
- **judge_change (P4).** 12a6c0e is the 2026-10-15 handoff bulk commit. The judge files it touched (`judge/fea.py`,
  `fea_sizing.py`, `requirements.json`, `scorecard.py`) are the CAD judges' R9 FEA; none of them enters the concept
  bench gap. The number reproduces to the digit on today's bench.
- **fold_margin.** It reads only the row and the verifier files, and this design has no verifier files. The margin
  was measured here: 10.10 / 12.12 deg.
- **held_out.** The row has no v_gap.

Patterns walked and not present:
- **T2:** the band read as 3-14 mm gives 75.50 against 73.76.
- **T3 / T4 / G4:** `th` >= 10.1 deg, and `sing_deg` is fixed rather than searched.
- **S1:** held out is +0.66 over the exact bench.
- **S3:** the declared bodies (link 1, link 2, arm-end) are all sampled. The base rides the handler at the J1 ring
  (CAD ruling 1).
- **S5:** there is no passive coordinate, and K2 finds 0 flips.
- **M1:** the kit template at real part sizes reads 69.29 (KIT.md).
- **M3:** K6 finds 0 collisions.
- **M4:** the joints sweep 349-352 deg.
- **M5 / G2 / G3:** there are no springs.
- **P2:** held-out poses are not used in the sweep.
- **P3:** one measurement, reproduced three times identically.
- **R1 / R2 / R4:** the dashboard row matches (screened, 68.93, v_gap null).
- **G5 / G6:** `tools/simplicity.py` gives 0, and the cuff slides are outside the count by the user's ruling.

**T5 instrument note (VERSION 2026-10-19.1).** This is the first T5 reading of this design. The reference reading it
compares with, the lead's 20.24 mm over 4 poses, comes from the type-guarded paired-file reader. Under the reader
before 702373b, the comparison with the lead was vacuous. There is no earlier reading of this design to differ from.

**Numbers not obtained, and why:**
- Held-out per-pose depths for the claim's own bench (68.93). The held wear is a different pose set, and the T5
  reader only reads files whose gap reproduces the claim. The held depths are in `_held_perpose.json` (74.43).
- The O20 what-ifs held out. Time box: the exact held wear takes 7.5 min per configuration at load 27.
- Hub 2 metal distances beyond 31.75 mm (the fast cache's cap).
- Cuff twist and GH-translation effects: the bench has no GH translation.
- Dynamics (R17): no springs to test.

## Proposals (proposals only; each is a measurement or reporting change for the lead or the user)

- **A. Restate the bar on the leaderboard's harness.** Show the reference as frozen exact 73.76 / held 74.42 (claim
  conventions), or honest kit, beside the fast 68.93. Measured effect on verified rows: none of their numbers move.
  Their lead over the bar grows by +4.83 (bench) or +5.49 (held), against the fast 68.93.
- **B. Re-measure the bar at the user's 5 deg fold margin.** That gives 67.12 fast and 71.51 held, a measurement
  change of -1.81 / -2.91. No verified row moves.
- **C. Catalogue entry NEW-stale-bar** (section R): "A reference row measured under a protocol the rows compared with
  it do not use (other conventions, an older margin, fast in-sample vs frozen exact). Detect: a row with
  `is_baseline` whose checks or margin differ from the compared rows', or with no frozen exact wear. Here:
  baseline-3r 68.93 (outer, 10 deg, fast) vs honest 70.27, at 5 deg 67.12, frozen exact 73.76."
- **D. fold_margin should also read `docs/alignment/remeasure/<id>_*.json` `th_margin`.** Effect on this row: the
  check would go from watch to ok (10.10 deg). A tool change, so its VERSION would be bumped and the selftest run.

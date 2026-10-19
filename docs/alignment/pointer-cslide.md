# Alignment audit: pointer-cslide (2R donut pointer + shoulder-side wire-race C-slide)

Auditor run 2026-10-19, tool `tools/alignment_audit.py` VERSION 2026-10-19.1, hourly backlog audit (no ledger entry
before this one). Row: `docs/concepts/rows/pointer-cslide.json`, status **screened**, last row commit c414721
(2026-10-16 03:12, mechanism census). No verifier files exist.

## Verdict and the claim

- **Claim:** gap **69.84** (score 74.60) on Bench(60,160) fast. It is self-measured, the best of 479 configs, and the
  convergence gate did NOT pass. reach 0.50, follow 0.9333, in-band14 0.674, in-band10 0.521, contact 0.0556.
- **Ledger verdict: watch** (the tool's checks plus 12 judgement findings, all watch). No finding reaches 'gamed' under
  the rule "measured proof that the number ranks the design above one that is better for the wearer, or a hard rule
  broken". The closest is NEW-inband-padding (below): its same-design twin without the filler has 1.3 points more
  contact, so it is not cleanly better for the wearer.
- **Re-wear:** `tools/alignment_audit.py remeasure` does not support this model (no `frozen()`; it is a kit model).
  A new probe, `tools/alignment_wear_probe_pointer_cslide.py`, runs the model unchanged with the row's best_params:
  - It reproduces the claim exactly on the fast fit: 69.84, `docs/alignment/remeasure/pointer-cslide_probe_fitfast.json`.
  - It freezes the fitted shape (window, radii, saddle and neck profiles) through the model's own params-keyed cache, then
    wears it on Bench(110,360) exact and on the held-out bench.
  - **Those two exact wears did not finish in the time box.** The box ran at load ~25 on 4 cores and each process got
    25-35 % of a core. I stopped the held wear twice to free a slot for the counterfactual and clash runs (the 2-process
    limit). The bench wear reached its own 1500 s wall timeout after about 8 CPU-min and wrote nothing.
    The farm was not used: the CPU-farm approval is spent (CLAUDE.md rule 7, exo-cpu1 workersMax 0).
  - So the exact-bench gap, the held-out gap and the true standoff of the parts above the fast grid's 31.75 mm clamp are
    **not measured**.

## What the wearer gets (measured, Bench(60,160) fast, the claim's own shape)

| quantity | value | file |
|---|---|---|
| overhead reach (workspace, elev >= 140), taken / total | **0 / 12** (9 J3 window, 2 collide, 1 contact) | probe_fitfast `overhead_ws140*` |
| raised-arm reach (elev >= 90, all poses) | 34 / 67 | probe_fitfast `raised_arm_reach` |
| taken poses with metal < 1 / 2 / 3 mm (of 136 contact-free) | 4 / 19 / 61 | probe_fitfast `taken_floor_lt` |
| near-touch gap at 1 / 2 / 3 mm (plain 69.84) | 76.34 / 106.17 / 185.41 | probe_fitfast `near_touch` |
| contact poses, summed depth, deepest | 8, 72.56 mm, **15.67 mm: hub 1 + link 1 inside the deltoid at abduction 150** | probe_fitfast `contact_poses` |
| unscored workspace in-band14 (80 taken ws poses) | 0.545 (44.6 % of metal > 14 mm, 24.7 % > 20 mm) | probe_fitfast `probe.ws_unscored` |
| shoe / track (the twist bearing) off the arm | shoe 29.4 mm median, track top 29.4 mm median, shoe crown >= 31.7 mm | probe_fitfast, saddle_counterfactual |
| hub 1 off the arm | >= 31.7 mm in every clip frame (the fast grid clamps at 31.75) | probe_fitfast `inband_member` |
| fold margin (th, min over taken poses) | 38.55 deg (p05 41.6; the model rejects < 15) | probe_fitfast `singular_margin_*` |
| springs / stops | none / a J3 travel window of 97.9 deg (taken poses reach its edge: margin -0.0 deg) | probe_fitfast |
| cuff twist | none modelled (no spring-held coordinate) | |
| mass | 741 g Ti (the saddle body); 275 g with the spec's cylinder band | saddle_counterfactual |

## Findings (docs/alignment/pointer-cslide.findings.json)

1. **NEW-inband-padding (watch). About 49 points come from a filler body's underside.**
   - The test: the same params on the same fast bench, with only the model's `saddle` switch flipped
     (`remeasure/pointer-cslide_saddle_counterfactual.json`).
   - With the saddle (the claim): gap 69.84, in-band 0.674. With the spec's cylinder band: gap 120.30, in-band 0.182.
     Reach (0.50) and follow (0.9333) are identical. Contact is 0.0556 with the saddle and 0.0685 without.
   - Only the band's in-band moves (0.0006 -> 0.849). The parts that move with the arm do not get closer: the shoe stays
     at 0.00 and hub 1 at 0.017.
   - The track's outer face stays 29.4 mm off the skin (31.5 mm for the cylinder). The filler is 23.3 mm thick at the
     median (max 31.4) and adds 466 g.
   - Why the exo is not better: the twist bearing is just as proud and heavier, but the score says 50 points better.
   - Action: the row verdict and the design doc's "New knowledge 2" should state this price. "New knowledge 2" currently
     offers the saddle as a trick for "any arc rail or ring bearing in the catalogue". Any design that copies it should
     report the outer-face standoff.
2. **S2 (watch). In-band is weighted by sample.**
   - Sample-weighted in-band is 0.674; part-weighted it is 0.414 (+26.0 points). The band (1470) and the neck (200) hold
     65 % of the samples.
   - Mostly out of band: hub 1, the shoe, link 1 and hub 2 (607 samples, 23.5 %).
   - The tool's +8-point threshold would read gamed. I hold it at watch: every part is sampled at the kit's density
     (2 x 2 mm), so this is area weighting, not sparse sampling. The wearer-side cost is finding 1.
3. **NEW-oob-standoff (watch). The twist bearing and hub 1 ride about 30 mm off the arm.**
   - The bearing is structural (a circle about the twist axis, sized by the fattest skin it passes). In-band counts a
     sample at 15 mm and one at 31 mm alike.
   - 32 % of the scored metal is above 14 mm and 19 % above 20 mm.
4. **T1 (watch). 29.8 gap points live in the 1-2 mm shell** (near-touch at 2 mm: 106.17). This is reported only:
   near-touch is not a gate (user, 2026-10-17).
5. **T2 (watch). The skin-fitted members are fitted at the band's 2 mm edge by construction.** `radial_req` uses
   clr = 2.0 mm, and every scored clip frame has its lowest metal below 4 mm. In-band10 is 0.52; the aim is 10 mm.
6. **G1 (watch). The neck and the saddle hug.**
   - Of the 61 taken poses with metal < 3 mm, the neck is below 3 mm in 44 and the band in 34.
   - The neck is a 14 mm strap fitted to the 98th-percentile pose, on an arm that bulges.
7. **T5 (watch). 8 contact poses, 72.56 mm summed, 7 of them deeper than 3 mm.** They are in the overhead (hub 1 /
   link 1, 15.7 mm), extension (hub 2, 12.9 mm) and across-body (band / neck, 11.4 mm) poses.
   - The tool reads it at x3.58 the lead's 20.24 mm over 4. The claim's bench is smaller, so this understates the
     excess.
   - **Instrument change 2026-10-19.1:** for this design T5 read "not measured" before this audit (no records). Now it
     reads the new fast-fit probe. The type guard changes only the reference side: the lead's 20.24 mm is now read.
8. **P1 / S1 (watch). The claim is in-sample by construction.**
   - The J3 window (cov 0.661 of the scoring poses: c 27.4, T 97.9 deg) and the band / shoe / neck radii (quantiles
     0.991 / 0.983) are fitted on the same 220 poses that score them, as the best of 479 configs.
   - The taken poses sit on the window's edge.
   - The window is a twist range, and the search benches under-sample |axial| >= 150 (S1). So a held-out loss is likely,
     but it is not measured (see Re-wear).
9. **M2 (watch). The declared J3 component cannot carry the stroke.**
   - In a non-recirculating caged-ball shoe the cage walks T/2 relative to the shoe: 48.97 deg, against a 39.46 deg shoe.
     It leaves the shoe for any cage length.
   - A long enough shoe lengthens the band (now 141 deg) toward the torso-free limit of 150-180 deg.
   - A plain iglidur shoe fits the modelled 2 + 6 + 2 envelope, and complexity is unchanged at 2.75. So the number may
     stand, but the component list should change.
10. **S3 (watch). The shoe-to-neck riser is not sampled.**
    - The riser is a wall about 25 mm radial x 14 mm wide, from the track at s+15 down to the neck at s+19 (the
      'down' neck does not use `neck_from`).
    - Estimate: about 88 out-of-band samples, about +2.2 gap points (not run).
11. **NEW-ws-inband (watch). Unscored workspace in-band is 0.545**, and overhead is 0 / 12.
12. **NEW-skin-wrapped-body (watch). The saddle's underside is a surface fitted to skin data.** It is a 14 x 105 grid of
    per-sample quantile radii. The CAD rule "no surfaces fitted or shrink-wrapped to skin data" forbids that. A
    buildable approximation sits at or above it; its in-band is unmeasured.

Patterns checked and not present:
- **T3, G4 (fold margin):** the min th margin is 38.55 deg, measured in `th` (`K.closure` margin), well above 5.
- **T4 (search bounds):** `sing` is fixed at 15 and the taken poses stay above 38 deg.
- **M1 (virtual parts):** 0 passive translations, O20 hubs.
- **M3 (unchecked clashes):** no sample of link 2, link 1, hub 1, hub 2 or the neck lies inside, or within 1 mm of,
  the shoe's crown-to-track volume in any of the 144 taken poses (`remeasure/pointer-cslide_shoe_clash.json`).
- **M4 (idle joints):** the J3 window is 98 deg and is used to its edges.
- **M5, G2, G3 (springs, cuff twist):** there are no springs.
- **P2 (held-out leakage):** the kit refuses held-out clips, and the model never imports `held_bench`.
- **P3, R3 (best-of-many):** the row reports top-5 within 1.06 and the ungated convergence.
- **P4 (judge changed with the design):** the tool found no bench, judge or metric change in the row's 3 commits.
- **R1, R2, R4 (reporting):** the row is shown as screened. The dashboard shows 69.84 with no v_ fields, and its
  complexity 2.75 matches `tools/simplicity.py`.
- **G5, G6 (complexity):** 3 active joints.

Not measured, and why:
- **S5 / NEW-plain3r-islands:** no continuity flood exists for kit models. A plain 3R with a hard J3 window can still
  hold islands.
- **S4:** instrument-wide.
- **Exact-bench and held-out numbers:** see Re-wear.

## Proposals (measurement changes, not applied, not inputs to the verdict)

- **A. Outer-face standoff for thick bodies.**
  - The rule: for any member whose radial thickness exceeds the kit strap (3 mm) or the O20 stack (12.25 mm), also
    report in-band read at its outer face, or at skin face + local thickness.
  - Measured effect here: the band's outer face is 29.4 mm off at the median, so the band would go from 0.85 to about
    0.0x in band, which is the saddle=0 reading (gap ~120).
  - Effect on the verified rows: **not measured in this time box**. They use 3 mm straps and O20 hubs only, so the
    expected shift is zero by this rule's own threshold. A run of `tools/sample_density.py` style member listings over the
    verified rows would confirm that.
- **B. Catalogue entry.** M6? / S8 "padding body": a filler that adds in-band samples under a part that stays out of
  band. It is detected by switching the filler off at the same params; it was also seen as NEW-inband-padding on
  kneeless-roller and NEW-inband-dilution on proxtrack.

## Next

- Finish the exact wears when the box is idle (they take about 10 CPU-min each on this model):
  `CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_pointer_cslide.py bench|held <dir>`.
  Then copy the result to `docs/alignment/remeasure/pointer-cslide_probe_{bench,held}.json` and re-run the audit.
- Whoever continues the design's CMA (the row's `farmcma`) should claim with the saddle off as well as on, and report
  both.

## Skeptic (2026-10-19 04:20-04:34 UTC): final verdict WATCH

Re-measured with the model unchanged and the row's best_params, on the claim's own Bench(60,160) fast with its own
shape. The probe re-fit reproduces every number in `remeasure/pointer-cslide_probe_fitfast.json`, all identical:

| quantity | value |
|---|---|
| gap | 69.84 |
| near-touch at 1 / 2 / 3 mm | 76.34 / 106.17 / 185.41 |
| min th margin over taken poses | 38.55 |
| contact | 8 poses, 72.56 mm summed |
| sample counts | identical |
| per-part in-band | identical |

The saddle counterfactual re-run is file-identical to `remeasure/pointer-cslide_saddle_counterfactual.json`. New
measurements are in `remeasure/pointer-cslide_skeptic_extra.json` (`tools/alignment_skeptic_extra_pointer_cslide.py`).
The exact Bench(110,360) and held-out frozen wears again did not finish. They ran as 2 niced processes at load 14-17 on
4 cores, 3.6 CPU-min each, and I stopped them at the time box. No farm (the approval is spent).

### Rulings (`docs/alignment/pointer-cslide.rulings.json`)

| key | refuted | evidence (short) |
|---|---|---|
| held_out | no | Not measured. No v_gap and no held-out number on file. My frozen exact wears did not finish (above). |
| near_touch | **yes** | On file: `probe_fitfast.json` near_touch gives 76.34 / 106.17 / 185.41, re-measured identically. With the numbers on file the documented level is ok (report-only since 2026-10-17; `c_near_touch`). The shell size is carried by T1. |
| contact_depth | no | 8 poses, 72.56 mm, deepest 15.67 (hub1 / link1 at ws 0/150/0), re-measured. The pairing is cross-bench: a 220-pose fast fit against the lead's 470-pose exact dump (4 poses, 20.24 mm). It understates the excess: 0.330 vs 0.043 mm per pose (x7.7), and +52.3 mm is 10x the 5 mm floor. Held depths: not on file, true. |
| fold_margin | **yes** | `K.closure` (`concept_kit.py` 88-97) margin is the line 25-30 `th` reading. Min over the 136 taken poses is 38.55 deg (p05 41.64; `probe_fitfast` singular_margin_min_taken), re-measured, > 5. |
| sampling | no | The per-part record exists (`probe_fitfast` sample_counts + inband_member). Through c_sampling's own arithmetic it reads +26.0 points sample- vs part-weighted, past TH part_weight_gamed 8. S3's riser is an unsampled body, and it is now measured. |
| NEW-inband-padding | no | Re-run identical: 69.84 vs 120.30, an in-band term of 49.17 points, 48.3 of them from the band's underside. The outer face stays 29.4 mm off. New: 741 g is past R8 (<= 500 g); the 275 g twin is under it. |
| S2 | no | 0.6739 sample-weighted vs 0.4136 part-weighted, re-derived. |
| NEW-oob-standoff | no | over14 0.3239, over20 0.1908; shoe 29.4 mm, hub1 >= 31.7 mm (clamp). |
| T1 | no | 29.83 points in the 1-2 mm shell (36.33 between 0 and 2 mm), over the documented 15. 19 of 136 taken poses are < 2 mm. |
| T2 | no | Clip floor histogram 1 / 8 / 28 / 19: all 56 taken clip frames have a floor < 4 mm. in-band10 0.521. The 2 mm march is kit-wide (KIT.md K3), but the cost is the wearer's. |
| G1 | no | Below 3 mm: neck 44, band 34. Below 2 mm: band 9, neck 8, link1 6, link2 3. |
| T5 | no | As contact_depth. The instrument statement is right: under 2026-10-18.1 the lead's reference raised and T5 read ok. It now fires watch. This needs both the type guard and the new probe file. |
| P1 | no | design() fits the window and all quantile radii on the scored poses. Best of 479, gate not converged, window edge -0.0 deg. Off-bench still unmeasured. |
| M2 | **yes** | "For any cage length" is false. Use a cage longer than the shoe: Lc = Ls + T/2 = 39.46 + 48.97 = 88.43 deg keeps the shoe over cage-held balls through the stroke. Over the stroke the cage spans Lc + T/2 = T + Ls = 137.41 deg. That is the band arc 141.51 (`angles()`: T + Ls + 2 x 2.05 stop) less its stops, and the cage meets the stop face together with the shoe. The declared caged-ball J3 (custom cage, anti-creep: row mechanism.notes) fits the band unchanged. |
| S3 | no | **Measured lower bound +1.18.** The shoe at rho 81.83 drops to the neck's first row at radius 54.2-54.7 over 4 mm: a 27.45 mm step at 81.7 deg, past K5's 60 deg. A K5-consistent riser (neck rows raised to the 60-deg line, no new wall samples) lifts 7 rows. Neck in-band goes 0.9945 -> 0.8419 and the gap 69.84 -> ~71.02. Wall samples would add to that. |
| NEW-ws-inband | no | ws in-band 0.5446, over14 0.4462. Overhead ws 0 / 12; raised 34 / 67. |
| NEW-skin-wrapped-body | no | Not steeper than a kit strap: max step 46.3 deg axial and 38.7 deg circumferential, 0 % past 60. It is a doubly-curved 26 mm x 141 deg underside on a 6.0-31.4 mm body carrying ~48 in-band points, which a constant-section strap is not. No buildable line/arc version has been worn. |

### Missed by the audit (not counted in this verdict; for the next audit)

1. **The J1 seat breaks user ruling 4, and no reason says so.**
   - best_params give a J1 of az 120.431, el 35.415, so `K.bvec` = (0.4128, 0.5795, 0.7027).
   - The anterior component is 0.4128, over ANT_MAX 0.20. `seat_ok` (`docs/concepts/models/zc-frontier-3r.py` lines 56-62) fails it.
   - The model's docstring puts J1 "over the anterior acromion". Ruling 4 allows back of the shoulder and acromion top only, with no front seats.
   - The row predates the ruling: t_screened 2026-10-15T22:36, the ruling 2026-10-16 ~05:50.
   - Its `farmcma` loop searches az +-25 and el +-20 about this seat with no `seat_ok`, so continuing the loop as the audit's Next suggests keeps searching forbidden seats.
   - The clavicular-front-route skeptic (90129e8) found the same gap in this audit, and ruled the same test gamed on that row.
2. **The saddle is past R8.** 741.2 g against REQUIREMENTS.md R8's <= 500 g custom-part budget; the saddle=0 twin is 274.7 g. So the 49 in-band points are bought with a requirement, not only with mass.
3. **The shoe-to-neck step breaks the K5 60-deg climb rule** (81.7 deg over 4 mm). S3 called it unsampled. It is also unbuildable as modelled. The kit-consistent fix costs >= 1.18 points (above).
4. **The near_touch, fold_margin and sampling checks fire on missing fields when the numbers are on file in the probe.**
   - `probe_fitfast` carries near_touch, singular_margin_min_taken and sample_counts + inband_member.
   - The tool reads none of them (FOLD_KEY does not match `singular_margin_min_taken`; c_sampling wants `parts_ib14`).
   - Read correctly, sampling would be **gamed** by the tool's own +8 threshold (+26.0), which the auditor held at watch on judgement (area weighting at kit density).

### Final verdict (ledger, skeptic entry 2026-10-19T04:33:33Z): **WATCH**

Refuted: near_touch, fold_margin and judgement:M2. Upheld (14): held_out, contact_depth, sampling, NEW-inband-padding,
S2, NEW-oob-standoff, T1, T2, G1, T5, P1, S3, NEW-ws-inband and NEW-skin-wrapped-body. The worst upheld level is watch.

**T5 now reads differently** (instrument 2026-10-19.1 + the new probe file): ok, "no depth of the lead on file", before;
watch, x3.58 the lead's summed depth, now.

Next: run the frozen exact and held wears when the box is below load ~6. Each needs > 8 CPU-min:
`CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_pointer_cslide.py bench|held <dir>`.
Then pair T5 on Bench(110,360) with the lead's `_bench_perpose.json`. Decide the seat (missed 1) before any more of
this design's CMA runs.

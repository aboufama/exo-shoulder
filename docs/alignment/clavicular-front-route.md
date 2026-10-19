# Alignment audit: clavicular-front-route (2026-10-19)

Auditor: the alignment auditor (hourly backlog audit; no earlier ledger entry). Tool `tools/alignment_audit.py`
VERSION 2026-10-19.1. Ledger entry: `python3 tools/alignment_ledger.py get clavicular-front-route`.

## Verdict: GAMED (the ledger's verdict; the tool alone reads watch)

The claim is the screened row's gap **68.26** (score 75.18). It was self-measured on Bench(60,160) fast, with no
verifier, on 2026-10-15 22:07 UTC. The number does not stand as evidence of a better exo. The J1 seat sits on the
front of the shoulder, which the user's ruling 4 (2026-10-16 ~05:50 UTC: "J1 seats: back of the shoulder + acromion top
only ... no seats over the front / clavicle") forbids. The row came before the ruling, so nobody broke the rule on
purpose. But the board still compares it with seat-abiding designs as an equal.

Re-measured here, with the model file unchanged throughout:

| wear | gap | reach | follow | in-band 14 | contact | near 1 mm | near 2 mm | near 3 mm | file |
|---|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast (the claim) | 68.26 (reproduced to the digit) | 0.875 | 0.950 | 0.309 | 0.066 | 75.13 | 79.77 | 233.37 | `remeasure/clavicular-front-route_fit60.json` |
| frozen on Bench(110,360) exact | **75.92** | 0.856 | 0.918 | 0.306 | 0.089 | 78.92 | 89.96 | 227.25 | `remeasure/clavicular-front-route_bench.json` |
| frozen held out (disjoint poses, exact) | 77.24 | 0.839 | 0.927 | 0.308 | 0.096 | 82.86 | 93.77 | 225.56 | `remeasure/clavicular-front-route_held.json` |

- Fast to frozen exact costs +7.66 points. That is the self-measured to worn drop, below the tool's 14-point watch line.
- Held out costs +1.32 over the exact bench, so there is no in-sample tuning signal.
- The fit's profiles are frozen. On the wear benches no strap changed its sample count, so nothing was resampled.
- The per-pose dumps reproduce each gap within 0.01: `_fit60_perpose.json` 68.26, `_bench_perpose.json` 75.93,
  `_held_perpose.json` 77.25.

## What the wearer gets (measured)

- **Overhead:** 5 of 28 workspace poses at elev >= 140 are taken on Bench(110,360) exact, and 5 of 26 held out.
  By elevation band (taken / total): 140-160 3/13, 160-200 2/15, 120-140 19/34. Link 1 folds into the head and neck.
  The overhead clip class takes 7 of 38 poses, with 5 K6 collisions.
- **Raised arm:** 41 of 51 poses at elev 90-120 and 19 of 34 at 120-140 (exact bench).
- **Metal hugging:** 3 of 101 taken clip frames and 20 of 308 taken workspace poses have their lowest metal under
  2 mm (exact bench). Under 3 mm: 232 of 409 taken poses. The kit march's 2 mm clearance puts the lowest sample of
  each rigid part at 2-4 mm in most poses, so this is a kit-wide floor and not this design's doing. For comparison,
  the lead's 3 mm gap reads 86.16 against plain 18.28. Near-touch is report-only since 2026-10-17.
- **Deepest contact:** 47.62 mm into the skin at ws plane 30, elev 165, axial -60 (exact bench). On the claim's bench
  it is 21.08 mm in raise overhead (clip plane 30, elev 150): link 1 into the head and neck. Across the body, hub 1
  and the bridge press 5.0-6.5 mm into the forearm (plane 135-150, elev 120-135).
  - Exact bench: 40 contact poses, summed 401.86 mm, 26 deeper than 3 mm.
  - Held out: 43 contact poses, 444.43 mm.
- **Workspace in-band (unscored):** 0.337 on the 308 taken workspace poses, with 66 % of the metal above 14 mm and
  57 % above 20 mm (median 29 mm).
- **Per-part in-band** (exact bench): hub 1 0.056, hub 2 0.000, hub 3 0.194, link 1 0.014, link 2 0.007,
  bridge_a 1.000, bridge_b 0.515, neck 0.587.
  - The hub levels are 78.8 mm (hub 1), **151.0 mm (hub 2)** and 68.0 mm (hub 3) from GH. The moving 3R floats
    ~10 cm off the shoulder.
- **Springs, stops, cuff twist:** none. It is a plain spherical 3R, with no knee and no cuff slide modelled.
- **Singular postures:** the minimum fold margin in `th` over the taken poses is 11.04 deg on the fast bench,
  10.76 deg on the exact bench and 12.82 deg held out. The declared margin is 7.3 deg and no pose sits under 5 deg.
  This number exists only in the re-wear files: the tool's fold_margin check reads rows and verifier files, so it
  still says "not on file".
- **Joints:** J1 spans 174 deg, J2 135 deg and J3 357 deg over the taken poses. No joint is idle.
- **Complexity:** 0.5 (recomputed with tools/simplicity.py). 3 DOF, O20 hubs, 0 passive translations.

## Findings

1. **NEW-seat-rule (gamed).** The J1 seat is outside ruling 4.
   - Evidence:
     - k368 has J1 at sdir(66.3, -105.5), which is bvec(az -164.5, el 66.3), with anterior component 0.387.
     - The searches' own ruling-4 test fails it on both az and anterior. That test is `seat_ok`
       (`docs/concepts/models/zc-frontier-3r.py` lines 59-62, `tools/gpu_bench.py` lines 64-66): az -110..135,
       el -20..90, anterior <= 0.20, with a +200 penalty.
     - None of the 440 sweep entries sits inside the allowed region. The spec's own AC-front seat has anterior 0.754.
     - The handler cannot carry J1 there. The model therefore runs a 14 x 3 base bridge from the handler side
       sdir(45, 90), over the acromion top sdir(65, 20), to the seat.
   - Why it is not better: the user's scapula handler cannot reach this seat, so the 68.26 belongs to a base that
     cannot be built on the user's handler. Yet it ranks the row 0.67 points ahead of the champion baseline (68.93).
     The champion's J1, bvec(2.4, 80.7) with anterior -0.161, is inside the rule. The row's verdict calls them "level".
   - Action, for the lead:
     - Mark the row "outside ruling 4" and keep its measured lesson: the AC front is not quiet in the scapula frame,
       and the forearm covers it across the body.
     - Do not count the 68.26 against seat-abiding designs.
     - If the route is ever re-run with `seat_ok` enforced, the sweep's own trend says it converges onto the top seat,
       which is the zc-frontier family.

2. **NEW-static-padding (watch).** The in-band comes mostly from static base metal, not from the mechanism.
   - Evidence (`remeasure/clavicular-front-route_fit60_bridgeshare.json`, `tools/alignment_bridge_share.py`, Bench(60,160) fast):
     - In-band 14 is 0.3088 with all parts.
     - Without the two bridge straps it is 0.1449, and the gap goes from 68.26 to 84.65 (+16.39).
     - With the hubs and links alone it is 0.033, and the gap is 95.84.
     - bridge_a has 208 samples, 100 % in band, median 3.92 mm. bridge_b has 216 samples, 52 % in band.
     - Link 1 (357 samples) is 1.7 % in band, link 2 (322 samples) 0.7 %.
   - Why it is not better: the sample-weighted in-band rewards any well-fitting static strap added to a design. Here
     the strap exists only because the seat is forbidden. The parts that move with the arm stay 113-155 mm off the
     skin.
   - Why watch and not gamed: the champion's own part split is not on file, so the ranking flip (84.65 against 68.93)
     is not proven like-for-like. The row discloses the effect itself.
   - Proposed catalogue entry **S7, static metal padding the in-band**:
     - Looks like: a design's in-band rises with base / scapula-fixed metal that rides at 2-6 mm, while its moving
       parts sit far out of band.
     - Detect: report in-band over moving members only, next to the scored in-band.

3. **R2 (watch).** The dashboard's "Sweep best gap" shows a non-honest entry.
   - The column reads 65.53 (k414, cmaC-g1), an entry the kit marked honest: false.
   - `tools/dash_build.py` lines 523-527 take the minimum over every sweep entry that is not passed over, whatever
     its `honest` flag.
   - The best honest entry is 65.71 (k434). The row's 68.26 is older than the CMA polish that found it, so the claim
     is stale, though in the direction of under-claiming.
   - Why watch: 0.18 points, and the column is labelled unreviewed.
   - Action: the dashboard builder could skip entries with honest: false (a reporting change for the lead).

4. **T5 (watch).** The contact is deep, and the score prices it only by count.
   - Exact bench: 40 poses, 401.86 mm summed, deepest 47.62 mm. The lead on the same bench presses 20.24 mm over
     4 poses (x19.9).
   - Held out: 43 poses, 444.43 mm, deepest 36.03 mm.
   - q = 0.98 accepts 2 % of the fit poses below requirement by construction.
   - Why not better: metal 20-48 mm into the head, neck or forearm is a blocked arm, not a liner squeeze.

Patterns walked and not present:
- **Thresholds and margins:**
  - T1 / G1: the 2 mm shell is 14.04 points on the exact bench, below the 15 watch line.
  - T2: reading the band as 3-14 mm adds +0.91.
  - T3: the fold margin is read in `th`, min 10.76 deg.
  - T4: the search bounds were j1lat 55-75 and 30-55 and margin around 7. The best config is not at a bound and the
    margin is not spent.
- **Sampling:**
  - S1 / P1: held out is +1.32.
  - S3: every moving body is sampled (link 1, link 2, hub 3 + neck), and so is the bridge.
  - S5: plain 3R, so no flood is needed.
- **Model-reality gaps:**
  - M1 / M2: O20 K4 discs, and the kit audit is clean.
  - M3: link 1 over the bridge and the bridge lap joint are enforced by `over`, with K6 on.
  - M4: no joint is idle.
  - M5: no springs.
- **Protocol:**
  - P2: no held-out pose in the search (`K.evaluate` raises on one).
  - P3 / R3: the row reports best of 128 v2 configs plus a CMA, with its top-5 spread of 3.81.
  - P4: neither commit touched a bench, judge or kit file.
- **Reporting and goal:**
  - R1 / R4: the board labels 68.26 "Self / fast gap (unverified)", and v_gap is null.
  - G2-G6: no spring, no knee, no 4th joint, and complexity 0.5 matches the mechanism.

## The T5 instrument change (VERSION 2026-10-19.1, 702373b)

- **What changed:** the change type-guards the paired-file reader.
- **Effect here:** none, because no paired file names this design.
- **Why T5 reads differently anyway:**
  - Before this audit it read "not measured", because there was no dump.
  - It now reads the claim's own fast-bench dump, which reproduces 68.26: 14 poses, 123.42 mm, deepest 21.08 mm.
  - The change comes from the new dump, not from the instrument.

## Instruments added (new files only)

- **`tools/alignment_kitbuild_rewear.py`:** re-wear for plain kit-built models, i.e. models with only `build()`, no
  `frozen()` and no pin-knee audit. It works as follows:
  - fit on Bench(60,160) fast through `K.evaluate` unchanged;
  - freeze the profiles by patching `K.fit_profiles` (the zc-frontier `fixed_prof` protocol);
  - wear on Bench(110,360) exact, or on the osn held bench;
  - write the remeasure file, the per-pose dump, `deep_audit`, the wear probe, the `th` margin, and the J1 seat against
    `seat_ok`.
- **`tools/alignment_bridge_share.py`:** per-part in-band and the gap with static base parts left out.

Not measured, and why:
- Sample density (`tools/sample_density.py`): out of the time box.
- A flood: not required for a plain 3R.
- Any verifier number: the row has none.

## Proposals (measurement or reporting changes, not applied)

- **A. Add the ruling-4 seat test to the tool's `rules` check.** For a 3R base, use az -110..135, el -20..90 and
  anterior <= 0.20, read from `az`/`el`, `az1`/`el1` or `j1lat`/`j1lon`. Measured effect:
  - All 20 verified rows whose best params carry a seat pass. 17 verified rows inherit their seat from the model
    file and cannot be read from the row (the knuckle family is the acromion-top family).
  - Of all 49 rows with seat params, 3 fail: clavicular-front-route (screened 68.26), pointer-cslide (screened 69.84,
    bvec(120.4, 35.4), anterior 0.413) and seed-2r-cring (dead).
  - No verified number moves.
- **B. Report the in-band over moving members next to the scored in-band (S7).** Effect here: 0.309 -> 0.033. It was
  not measured on the verified rows in this audit.
- **C. Pair T5 readings by bench, not only by wear label.** Today a fast-bench dump is compared with the reference's
  exact-bench dump.

## Skeptic (2026-10-19 04:20 UTC)

The skeptic re-measured every reason and did not trust the auditor's numbers. The model file was unchanged throughout.

**What was re-run.** The skeptic used its own scripts, not `tools/alignment_kitbuild_rewear.py`.
- **Fit:** the fit on Bench(60,160) fast through `K.evaluate` reproduced 68.26 (reach 0.875, follow 0.95, in-band 0.3088, contact 0.0664).
- **Frozen wears:** the fit's profiles were frozen by patching `K.fit_profiles`, with 0 strap size mismatches.
  - On Bench(110,360) exact: **75.92**.
  - On the disjoint held bench (a copy of `tools/osn_polish.py held_bench`), exact: **77.24**.
- **Fold margin:** `th` was computed from the built chain's own J1 and J3 over the taken poses.
  - Fast: 11.040 (197 taken).
  - Exact: 10.757 (409 taken).
  - Held: 12.824 (404 taken).
  - No pose is under 5 on any bench.
- **Contact depth:**
  - Exact: 40 poses, 401.84 mm, deepest 47.62 mm.
  - Held: 43 poses, 444.42 mm, deepest 36.03 mm.
- **Compute:** local only, 2 niced processes, no farm spend.

### Rulings

| key | level | refuted | evidence (short) |
|---|---|---|---|
| held_out | watch | **yes** | Fires only because `v_gap` is null (`alignment_audit.py` line 222). The drop it guards is on file: `_bench.json` frozen.gap 75.92, `_held.json` 77.24, +1.32. Reproduced from the per-pose dumps and by the skeptic's own re-wear (75.92 / 77.24). That is below TH held_watch 6.0. |
| contact_depth | watch | no | Measurement right: the fast re-run has 14 poses, 123.42 mm, deepest 21.08. The tool's line pairs the 220-pose fast dump with the lead's 470-pose exact dump. The same-bench pairing is stronger: 401.84 mm over 40 poses against the lead's 20.24 mm over 4 (`conecut-knee-knuckle-3r_bench_perpose.json`), x19.9. "Held depths not on file" is wrong (`_held_perpose.json`: 43 poses, 444.43 mm), but the lead's held dump is a different bench (1154 poses), so there is no paired held reading. |
| fold_margin | watch | **yes** | `K.closure` (`concept_kit.py` 88-96) keeps a pose only at a `th` margin >= `margin_deg` = 7.3 (best_params.margin), so 7.3 > 5 holds by construction. On file: `_fit60.json` fit_fast.min_margin 11.04 and th_margin 11.04; `_bench.json` th_margin 10.757; `_held.json` th_margin 12.824; lt5 0 everywhere. Re-measured identically. |
| sampling | watch | no | The counts are on file (`_fit60_bridgeshare.json` sizes: hub 81 each, bridge_b 216, bridge_a 208, link1 357, link2 322, neck 232). Sample-weighted against part-weighted is +0.84, under 3. But c_sampling's out-of-band list is non-empty (hub1 0.07, hub2 0, hub3 0.20, link1 0.02, link2 0.01), and that alone sets watch (line 669). |
| judgement:NEW-seat-rule | **gamed** | no | (a) Measurement: the model's own sdir(66.3, -105.5) = (0.3873, 0.9157, -0.1074), equal to bvec(-164.5, 66.3). (b) Threshold: anterior <= 0.20 is the project-wide ruling-4 encoding (ANT_MAX in `zc-frontier-3r.py`, `gpu_bench.py`, `gpu_bench_knee.py`; legal_j1 in `isoceles-shortdyad-pinknee-3r.py`); this seat is 1.94x the line. (c) Comparison: the champion baseline (68.93) is on the same fast bench and its seat passes (anterior -0.162). (d) Wearer cost: the handler cannot carry the seat, the design needs a bridge, and the forearm lies on the seat across the body. CLAUDE.md treats slim-hub numbers the same way ("do not stand under this rule"). |
| judgement:NEW-static-padding | watch | no | Re-derived from the bridgeshare counts: 0.1449 without the bridge, 0.033 mechanism only, 0.3088 all, gap 84.65 without the bridge. The documented part-weighted check reads only +0.84, so this is a new pattern and watch is right. |
| judgement:R2 | watch | no | `morphs.json` sweep_gap 65.53 = k414, honest false; the best honest entry is k434 at 65.71. `dash_build.py` line 523 has no honest filter. |
| judgement:T5 | watch | no | Reproduced on the same bench and the same 470 poses as the lead: x19.9. Report-only by rule. |

### Missed by the auditor

These do not change this verdict. They are for the next audit.

1. **pointer-cslide breaks the same ruling-4 test, and its audit did not flag it.**
   - Its best_params az 120.431, el 35.415 is the J1 seat (`docs/concepts/models/pointer-cslide.py` line 103: `a1 = F.S(K.bvec(p["az"], p["el"]))`).
   - That seat has anterior 0.4128 > 0.20; az is inside -110..135.
   - Its audit at 2026-10-19T03:57Z (verdict watch, 17 reasons) has no seat reason, and `docs/alignment/pointer-cslide.md` does not mention the seat.
   - The two audits ran 31 min apart and ruled the same rule differently. This audit's proposal A even names pointer-cslide as failing.
2. **A reporting error in Finding 2.** "The parts that move with the arm stay 113-155 mm off the skin" gives GH radii (the row's limiter), not skin clearance.
   - The exact-bench metal-to-skin distance tops out at 107.83 mm, with p95 98 mm (`_bench.json` probe.ws_unscored).
   - The fast-bench per-part "med 31.75" values in `_fit60_bridgeshare.json` are the SDF cache clamp (`tools/concept_bench.py` lines 23 and 49: +-31.75 mm). They are lower bounds, not medians.
3. **The tool's sampling and contact_depth readers miss files that exist.**
   - c_sampling says "per-part sample counts not on file", but `_fit60_bridgeshare.json` carries them.
   - c_contact_depth says "held depths not on file", but `_held_perpose.json` exists.
   - The tool reads neither file. With the counts, sampling still reads watch, on the out-of-band parts.
4. **The held_out and fold_margin checks fire on missing fields when the numbers exist in the re-wear files.**
   - The held drop (+1.32) and `th` (min 10.757) are in `remeasure/_bench.json` and `_held.json`, but c_held_out keys on `v_gap` and c_fold_margin does not read remeasure `th_margin`.
   - Both are tool false positives on screened rows (compare the inband-rssr and longstroke-slipper rulings).

**T5 instrument note (2026-10-19.1, 702373b):** the skeptic confirms no change here. No paired file names this design, and the reference dump `conecut-knee-knuckle-3r_bench_perpose.json` reads 4 poses, 20.24 mm as before.

### Final verdict (ledger, skeptic entry 2026-10-19T04:20:02Z): **GAMED**

`judgement:NEW-seat-rule` is upheld. Refuted: held_out and fold_margin. Upheld: contact_depth, sampling, NEW-seat-rule, NEW-static-padding, R2 and T5.

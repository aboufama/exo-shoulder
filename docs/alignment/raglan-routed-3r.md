# Alignment audit: raglan-routed-3r (plain spherical 3R, link 1 bent 38 deg in planform)

Auditor pass 2026-10-19 ~01:40-02:15 UTC, tool VERSION 2026-10-18.1. Why it was due: the row is a screened row with no
ledger entry. The row last changed at 2026-10-16 03:20 (4d221f1, the mechanism census). Its claim was screened at 03:10
that day and has not moved since.

## Verdict: WATCH (claim gap 42.72 fast; self-measured frozen exact 50.06)

The ledger verdict is WATCH. There is no gamed reason (`python3 tools/alignment_ledger.py get raglan-routed-3r`).

- **Checks:** 4 watch, from `docs/alignment/raglan-routed-3r.json`: held_out, near_touch, fold_margin and sampling.
  - All four are "nothing on file in the form the tool reads". The row has no verifier and no v_gap.
  - The row stores its near-touch numbers and its per-part in-band under keys the tool does not parse (`near_touch`,
    `frozen_big.gap_near1`, `inband_member`).
- **Judgement findings:** 4 watch: R4, T1, S2 and NEW-oob-standoff.

The row's claim is the fast number, 42.72 (score 84.5). Its honest number is its own frozen exact wear on
Bench(110,360), 50.06 (score 81.8), and that number has never been independently verified. Nothing in either number
ranks this design above a design that is better for the wearer:
- The board sinks fast-basis rows below every verified one.
- At 50.06 it sits behind every verified 3-joint leader. The verified lead is 18.28, and k-rim-lobe-stub-knuckle-3r is
  44.79 verified.

On the evidence on file, this is an honest, mediocre plain 3R. Its one real gain is a routing gain, and the designer
measured it as mostly real.

| check | level | measured |
|---|---|---|
| held_out | watch | no verified bench gap; no held-out wear on file. The re-wear started this pass did not finish (see "Re-wear") |
| fast_frozen | ok | no verified pair. Row fast 42.72 -> self-measured frozen exact 50.06 (+7.34), under the 14-point watch level |
| near_touch | watch (report only) | the tool found no record it parses. Row: fast 42.72 -> 43.85 at < 1 mm (min 0.98 mm); frozen 50.06 -> 52.16 at < 1 mm (min 0.64 mm, 4 poses < 1 mm) |
| contact_depth | ok | no per-pose dump on file. Frozen contact 0.0075 = 3 poses of 470 (crown / wall contacts at elevation 150-165); depth not measured |
| dominance | ok | no reference given |
| continuity | ok | no passive coordinate; flood not required |
| fold_margin | watch | no min-th reading on file. The claim was searched and worn at margin 10 deg in th (`best_params.margin` 10.0, `K.closure(margin_deg)` on th = angle(J1, J3)), so no taken pose can sit closer than 10 deg to the fold. That is double the user's 5 deg rule (see "Fold margin") |
| idle | ok | 3 closure-set joints; a spherical 3R that follows a 3-DOF arm moves all three |
| sampling | watch | the tool found no per-part record it reads. Row `inband_member`: hub1 1.00, hub2 0.00, hub3 0.674, link1 0.602, link2 0.051, neck 0.655; part-weighted 0.497 vs sample-weighted 0.504 (+0.71 gap points). Every declared body is sampled (3 moving bodies: link 1, link 2, arm-end = hub-3 plate + neck) |
| density | ok | not measured (`tools/sample_density.py` needs a pin-knee model). The kit samples straps at 2 x 2 mm and discs on a 2 mm grid by construction |
| complexity | ok | recomputed 0.0 (three pins on bearing pairs, three links, nothing passive) |
| reporting | ok | no verifier files; the dashboard status (screened) matches the row |
| judge_change | ok | no bench / judge / metric file in the 2 commits that touched the row |
| rules | ok | O20 hubs (K.hub_member, HUB_R 10), margin 10 >= 5, 0 passive translations, 3 DOF |

## What the wearer gets (measured, files named)

These numbers are from the row's frozen exact wear (`rows/raglan-routed-3r.json` frozen_big / exact_frozen_summary) and
the design doc's red team (`docs/concepts/raglan-routed-3r.md`), Bench(110,360) exact, shape frozen from the
Bench(60,160) fit.

- **Overhead reach** (workspace, elevation >= 140): 13 of 28 taken (0.464). In-band 0.56 over the taken overhead poses.
- **Raised arm:** the jam band sits in the middle of everyday raising. 60 poses are lost to the fold, mostly at
  elevation 75-165 with axial -45..-15; one example is plane 0, elevation 120, axial -15. Across-the-body poses at plane
  90-105 with axial -120..-150 are also lost. A raise with mild internal rotation is blocked. Named groups on the big
  bench:

  | group | taken | median metal-skin | in-band |
  |---|---|---|---|
  | overhead | 23 / 38 | 11.0 mm | 0.56 |
  | across the body | 42 / 78 | 18.5 mm | 0.33 |
  | behind the back | 34 / 40 | 12.5 mm | 0.58 |
  | rest | 5 / 5 | 16.9 mm | 0.39 |
- **Total:** 71 of 470 poses not taken: fold / K2 60, part-part K6 8 (link 2 over link 1), crown contact 3.
- **Taken poses with metal < 2 mm:** not measured; the re-wear that measures it did not finish. On file: 4 taken poses
  < 1 mm, the lowest 0.64 mm at ws plane 15, elevation 45, axial -75 (pose #220).
- **Deepest contact:** not measured (no per-pose dump). Contact is 3 poses of 470, all hub crown / wall contacts at
  elevation 150-165.
- **Profile:** in-band 2-14 mm is 0.504 of clip metal.
  - Hub 2 is never in band. It sits 128 mm from GH; its disc need is a median 68 mm, so it stands about 60 mm off the
    back of the shoulder in the median pose.
  - Link 2 is out of band in 95 % of its samples.
  - Workspace in-band (unscored) was not measured; it needs the re-wear.
- **Springs / stops / cuff twist / singular postures:**
  - Springs: none.
  - Stops: none modelled. A plain 3R has no stop; the fold band is a jam, not a stop.
  - Cuff twist: none. The cuff is rigid on BOTTOM, with no knee and no slide.
  - Near-singular postures: none within 10 deg of th's fold, by the closure margin.
  - GH translation is not on the bench. The row's mechanism note leaves it to the user's cuff slides / liner, outside
    the count and outside the model. This is project-wide; see the proposals.

## Findings (each in `raglan-routed-3r.findings.json`)

**R4, watch: the board shows the fast number.** The row's own frozen exact claim is 50.06, stored under `frozen_big` and
`exact_frozen_summary`. `tools/dash_build.py` lines 505-508 read only `frozen_exact_gap`, `frozen_gap`,
`frozen_exact.gap`, `frozen.gap` and `claim.gap`. So `morphs.json` has `frozen_gap: null`, and the page shows 42.72
(score 84.5) instead of 50.06 (81.8). This is the same class as the inband-rssr and freek-oracle-route R4 findings.

The long name ("on far-end hubs (posterior J1 line ...)") describes the seed, not the claim:
- k3484 has e = +1 +1 +1, with no far-end hub.
- Its J1 is at bvec(8.6, 81.6), on the acromion top.

Why not worse: a fast-basis row sinks below every verified row (`docs/dashboard/simple/index.html` line 238), so it
outranks no verified design. Action:
- Store the claim as `frozen_exact_gap`, or let the builder read `frozen_big` / `exact_frozen_summary`.
- Rename the row to "plain 3R, link 1 bent 38 deg in planform".

**T1, watch: a plain-gap optimum with metal at 0.6-1 mm.** The CMA searched the plain gap: `obj == gap` on 4154 of the
4396 entries of `sweeps/raglan-routed-3r.json`, and the other 242 are +100 penalties. The near-touch objective became
the rule four hours after this screen (CLAUDE.md, b85eb07, 07:18 vs 03:10). The cost on file:
- fast: +1.13 at < 1 mm;
- frozen exact: +2.10, with 4 taken poses under 1 mm and the lowest at 0.64 mm.

The 2 mm and 3 mm shells were not measured (see "Re-wear"). Why the exo is not better by these points: a pose taken at
0.64 mm is metal on a real, bulging arm. Action: any polish or verification of this row searches and claims on the
near-touch gap.

**S2, watch: two of six parts out of band, and part of the routing gain is dilution.** Hub 2 is at 0.00 in band and
link 2 at 0.05.
- Part-weighted in-band is 0.497, against the scored 0.504.
- The routed link 1 has 340 samples against 245 straight. At the straight count k3484 scores 43.97, not 42.72: 1.25
  points of the routing gain are extra in-band metal outweighing the floating hub (the design doc's own dilution
  check).

The remaining +5.9 points against straight links at the same axes are real: link 1 goes from 0.36 to 0.60 in band.
Why watch: under the 3-point threshold, measured and published by the designer, and hub 2 is still charged in full.
Action: none beyond reporting the corrected 43.97 beside the fast number.

**NEW-oob-standoff, watch (new pattern; proposed catalogue entry S7 "out-of-band depth blindness").** The in-band term
cannot tell metal at 15 mm from metal at 60 mm. Once a part is out of band, how far it rides does not change the gap.
Here hub 2 stands about 60 mm off the back in the median pose (F 128 mm vs a disc need of 68 mm median), and link 2
spans from it. The score would be identical with hub 2 at 16 mm.

The design does not buy points with this: the lever that would lower hub 2 (per-part quantile qh2) was measured to cost
reach (0.97 -> 49.63). But the gap hides the design's largest profile defect from anyone who reads only the number.
Action: report a per-part standoff beside in-band (proposal 2).

Patterns walked and not present:
- T2: not measured.
- T3: the margin is on th itself, at 10 deg.
- T4: no singular bound. The search box edges hit are strap width 8 mm (the kit's narrowest strap, the osn leader's
  section) and q 1.0, neither a singular posture.
- T5: not measurable; 3 shallow-pattern crown contacts.
- S1 / P1: no held out on file.
- S3: all 3 moving bodies are sampled.
- S5: no passive coordinate.
- M1 / M2: O20 everywhere, 8 x 3 Ti straps, 0 passive translations.
- M3: K6 at 1 mm radial in the frozen wear, stricter than the search's 0.5 mm, plus crown and wall checks.
- M4: three closure-set joints.
- M5, G2, G3: no spring.
- P2: the search used the kit's `K.bench` (fit clips only; `K.evaluate` refuses held-out clips).
- P3 / R3: the spread is reported (streams 42.72 / 43.60 / 43.86 / 44.16), and the frozen wear ran once.
- P4: no judge change.
- R1 / R2: status screened, nothing shown as verified.
- G4: 10 deg margin.
- G5 / G6: complexity 0 recomputed, 3 joints.

## Fold margin (measurement change, not a finding)

The claim was searched and worn at the old 10 deg rule (`best_params.margin` 10.0). The model's PARAMS were routed to the
5 deg `K.FOLD_MARGIN` at 06:05 (17d6027, FINDINGS "Rebase"), but the row was never re-measured at 5 deg. Its numbers are
therefore conservative on reach: 60 of the 71 frozen losses are fold / K2 poses. Re-measuring at 5 deg is a measurement
change. It belongs to the lead or a verifier (`tools/alignment_raglan_rewear.py raglan-routed-3r bench --margin 5` writes
it as a separate `_m5` file), never as this row's claim without a verifier.

## Re-wear (step 2): started, not finished

There was no remeasure file. `tools/alignment_audit.py remeasure` cannot wrap this model: it is a kit model whose frozen()
is fold-sph3r's, with no pin-knee audit(M, B). So this pass added a NEW read-only adapter,
`tools/alignment_raglan_rewear.py`. It runs the model unchanged through its own `fs().frozen()` and wraps only
`concept_kit.bench`, to capture the worn bench and to swap in the held bench. It then reads the bench with the audit's
own instruments:
- `deep_audit`: near-touch at 1 / 2 / 3 mm with the crown / wall samples, and the band read as 3-14 mm;
- `alignment_wear_probe.analyse`: unscored workspace in-band, overhead, clearance floors;
- the per-pose th margin;
- per-part samples, in-band and min metal;
- a per-pose dump for the T5 depth check.

The bench and held wears were started at 01:42 with CB_EXACT=1, nice 10, 1 thread each. Under CB_EXACT=1 the
Bench(60,160) fit also runs on the exact path, which is how the row's own 50.06 was made ("the fit, re-run on the exact
path, reproduces 42.73"). With the box at load 21-31 on 4 cores, both processes were still in the exact fit after 11.5
CPU minutes each (27 wall minutes). I stopped them at 02:09, by PID, at the end of the time box. Neither reached the
wear, and neither wrote a file.

Numbers I could not get, and why: the 2 mm / 3 mm near-touch, the band read as 3-14 mm, taken poses < 2 mm, contact
depth, workspace in-band, per-pose th margin and the held-out gap. All need that re-wear. The farm is closed: the $8
CPU-farm budget is spent and exo-cpu1 workersMax is 0 until the user renews (CLAUDE.md decision 7). The adapter is
committed, so the next audit (or a verifier) can run

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_raglan_rewear.py raglan-routed-3r bench   # then held

on a quieter box or on the farm. That run writes `docs/alignment/remeasure/raglan-routed-3r_{bench,held}[_perpose].json`
in the forms `alignment_audit.py audit` reads: `deep`, `parts_ib14` and `frozen.gap`.

## Proposals (proposals only; none is an input to this verdict)

1. **Reporting, no score change:** `tools/dash_build.py` should also read `frozen_big.gap` and
   `exact_frozen_summary.gap`. Or rows should normalise their self-measured frozen claim to `frozen_exact_gap`.
   - Effect, measured by grepping every row in docs/concepts/rows for those two keys: only this row's display changes, from
     42.72 (fast) to 50.06 (self).
   - The other two rows that carry the keys already show a verified number: acromion-pointer-arm-ctrack (dead, v_gap
     65.66) and raglan-knee-3r (verified, v_gap 27.82). The page reads frozen_gap only for non-verified rows.
2. **Reporting, no score change (catalogue S7):** rows and the board report per-part standoff, the median and p95
   metal-skin distance over taken poses, beside per-part in-band. Out-of-band metal at 60 mm and at 16 mm then no
   longer read the same. This changes no gap, so it needs no re-measure of the verified rows.
3. **Project-wide note, for the lead:** the bench has no GH translation. A plain 3R's tracking of the real, translating
   GH is left to cuff slides / liner that are outside the count and outside the model. Per the row's mechanism note,
   "if counted, +2 passive_trans, crossed". This is allowed by the user's 2026-10-15 scope (passive self-aligning
   slides at the cuff, outside the count). It is recorded here only because it is the one place where a plain 3R's
   "0 passive DOF" relies on hardware the model does not carry.

## Skeptic (2026-10-19 ~02:20-02:35 UTC)

**Final verdict: WATCH.** This is the verdict `python3 tools/alignment_ledger.py skeptic raglan-routed-3r` printed (ledger
entry 2026-10-19T02:33:36Z).
- **Refuted, with evidence (2):** near_touch and fold_margin.
- **Upheld (6):** held_out, sampling, R4, T1, S2 and NEW-oob-standoff.
- **Files:** rulings in `raglan-routed-3r.rulings.json`; my measurements in `raglan-routed-3r.skeptic.json`.

**What I ran.** The model was unchanged, with the row's best_params (k3484), at OMP_NUM_THREADS=1, nice 10.
- **Fold margin:** `axes()` on Bench(60,160) and Bench(110,360), frames and closure only.
- **Fast-bench re-evaluation:** `evaluate()` on Bench(60,160) with the fast grid. It reproduces the claim exactly: gap
  42.72, near1 43.85, min 0.98 mm, and the same inband_member. On top of it I ran `alignment_audit.deep_audit` (with the
  model's crown points), per-part counts and standoffs, and four attribution variants.
- **Not run:** the exact held wear. It needs the exact Bench(60,160) fit first, which did not finish in the audit's
  11.5 CPU minutes.

### Rulings

| key | ruling | evidence |
|---|---|---|
| held_out | upheld | v_gap and every v_* are null, there are no verifier files and no held remeasure. `c_held_out` returns watch when v_gap is None. Not measured here. |
| near_touch | **refuted** | On file in `rows/raglan-routed-3r.json`: `near_touch.gap_metal_lt1_as_contact` 43.85 (plain 42.72, min 0.98 mm) and `frozen_big.gap_near1` 52.16 (plain 50.06, min 0.64 mm). Re-measured on fast: plain 42.72, < 1 mm 43.85 (1 pose), < 2 mm 44.99 (2 poses), so the 1-2 mm shell holds 1.14 points; band read as 3-14 mm 43.34. With a record, `c_near_touch` reads ok (report only since 2026-10-17). |
| fold_margin | **refuted** | Measured min th margin over closing poses: 10.136 deg on Bench(60,160) (202 closing, taken 199) and 10.031 deg on Bench(110,360) (410 closing). 0 closing poses are under 10 deg. `ok` needs margin >= margin_deg (`concept_kit.py` line 96), so taken is a subset of closing and its min is >= 10.03 deg. That is >= 5, so the check reads ok. |
| sampling | upheld | Measured per part (samples / in-band): hub1 81 / 1.00, hub2 81 / 0.00, hub3 81 / 0.674, link1 340 / 0.602, link2 185 / 0.051, neck 248 / 0.655. Every body is sampled and none is under 16 samples. Sample-weighted vs part-weighted is +0.70 points, under 3. But `c_sampling` reads watch when any part is < 0.5 in band (hub2, link2), so the level stands on the record. |
| judgement:R4 | upheld | morphs.json has gap 42.72 and frozen_gap null. The builder's cands (`dash_build.py` lines 505-507) have no frozen_big or exact_frozen_summary. The fast basis is in sink 2 (`index.html` line 238). best_params are e = +1 +1 +1 with J1 at el 81.6, so the name describes the seed. Of the 8 rows that mention these keys, only this row's display would change. |
| judgement:T1 | upheld | Sweep: 4154 / 4396 entries have obj == gap, 242 are +100 penalties, 0 are in between. b85eb07 is 07:18:01; the screen ended 03:11:01. Fast near1 +1.13 and near2 +2.27. New: the routing turn is what brings metal under 1 mm. The straight link at the same axes has min 2.00 mm and near1 = plain (49.89). |
| judgement:S2 | upheld, corrected | link1 has 340 samples routed vs 245 straight. Part-weighted is 0.4969 vs 0.5039. Re-derived from measured counts and fractions, with link1 at 245: **43.73, so dilution is 1.01 points**, not the design doc's 1.25 / 43.97. Either is under 3. |
| judgement:NEW-oob-standoff | upheld | Hub 2 over taken clip poses: min 19.74 mm metal-skin, median 31.75 mm, which is the fast grid's read clamp (`concept_bench.py` line 49, +-31.75 mm). Hub 2 is therefore more than 31 mm off the skin in at least half the clip poses. Link 2 is > 14 mm on 94.9 % of its samples. The "about 60 mm" is the radial need difference (F 128 vs a median need of 68), not a metal-skin reading. |

### Missed (for the next audit; not counted in this verdict)

1. **Routing gets credit for the strap width and an axis move (attribution, not apples to apples).**
   - The row's verdict compares "50.06 ... vs 57.99 for the straight-link 3R at k2221's axes, same protocol", and the
     design doc says "-7.9 gap points against the straight-link 3R".
   - That reference is k2221 at **12 mm** straps. The claim is k3484's axes at **8 mm**, the clamp floor in `clean()`.
   - Measured on Bench(60,160) fast at k3484's axes:

     | strap width | routed | straight |
     |---|---|---|
     | 8 mm | 42.72 | 49.89 |
     | 12 mm | 47.09 | 53.06 |

   - So the width alone is worth **4.37 points** routed and 3.17 straight. Routing itself is worth 7.17 at 8 mm and
     5.97 at 12 mm, or 6.04 when read at near1 at 8 mm.
   - The model's docstring still says "a constant 12 x 3 section", while the claim uses 8 x 3.
   - No frozen straight-link wear at k3484 is on file, so the frozen "-7.9 from routing" mixes three things: routing,
     the 12 -> 8 mm width change and the axis move.
   - The score is not inflated; the story told about the lever is.
2. **The routing is what puts metal under 1 mm.** Straight links at the same axes have min metal 2.00 mm and
   near1 = plain. Routed, the min is 0.98 mm at 8 mm and 0.74 mm at 12 mm (+2.28 near1).
3. **Instrument blind spot in `_near_numbers`.** It accepts a row's gap_near1 record only when that record's plain gap
   is within 0.5 of v_gap, and a null v_gap reads as 0. So every screened row with a near-touch record reads "no
   near-touch measurement on file".
   - The cause is the null v_gap, not that the tool cannot parse the keys.
   - Proposal (a tool change, measured on this row only): when v_gap is null, compare against the row's gap or its
     self-measured frozen claim. This row then reads ok, from frozen_big 50.06 / 52.16.
4. **Limit of the S7 standoff proposal.** The fast grid clamps distances at +-31.75 mm. A per-part standoff read from
   `Bench.res` saturates: hub 2 and link 2 both have their median at the clamp. A standoff report needs the exact path,
   or the ray-need difference F - need.
5. **The 3 mm near-touch shell tells nothing on kit rows.** The kit's per-cell q = 1.0 underside puts some cell at its
   own worst pose's 2 mm floor in every pose. As a result, 199 of 199 taken fast poses have metal < 3 mm
   (gap_near3 375.0), while only 0.6 % of clip samples lie at 2-3 mm. This is not gaming, since 2 mm is the band floor.
   Read the band as 3-14 mm instead (43.34, +0.62).
6. **Correction to "Fold margin" above.** A re-wear at 5 deg can win back at most **8 poses**, not 60:
   - Only 8 of 470 big-bench poses, and 1 of 220 fast poses, have a th margin in [5, 10) deg.
   - The other 52 of the 60 fold losses do not close at 5 deg either.
   - So the 10 deg wear is conservative by at most 8 poses (1.7 %).

**Next:** the exact held wear is still the open measurement:
`CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_raglan_rewear.py raglan-routed-3r held`. Run it on a
quiet box, or on the farm once the user renews the budget. Until then, held_out stays a watch, because the row has no
verifier.

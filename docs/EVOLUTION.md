# Design evolution (for the final time-lapse visual)

The user, 2026-10-15: "it would be cool to track progress over time to see the evolution in design for a cool
visual, take note of this as this will be useful in a few days when the design is finalized".

So every judged design is recorded here, in order, with what changed and why, and `pipeline/evolution/` keeps a
snapshot per entry (viewer screenshots at the same poses and camera, plus its scorecard numbers), so the final visual
can morph / cut from the first design to the last on one camera. Rules: same camera, same poses (rest, raise overhead
peak, reach back pocket peak), same mannequin look (matte black, faceless) and part colours (bead-blasted metal,
iglidur orange) for every snapshot; numbers from the outside judges only; measurement changes marked as such.
`tools/progress_history.py` gives the metric curves over time from git (the dashboard's over-time charts).

| when (UTC) | design | DOF | what changed | score 2-10 mm | score 2-14 mm | note |
|---|---|---|---|---|---|---|
| 10-09..13 | `final` (first conformal CAD), r7-r13 band designs | 4-5 | archive github.com/aboufama/exo-arm | 8.1 % (first CAD) | - | older scorer; see docs/FINDINGS.md score history |
| 10-14 15:45 | `cad_r13_n4_s1343_1` | 4 | reference 4R fair CAD at the start of this repo | 29.6 % | - | |
| 10-14 22:29 | `l1_3r_offset` | 3 | P0's thorax-plate 3R, L1 build | 0.05 % | - | counter-example: hubs inside the arm |
| 10-15 01:35 | `l1_r14_3r_s1351_1` | 3 | first GPU-searched 3R, hug builder | 35.4 % | - | |
| 10-15 01:45 | `band_r14_3r_s1351_1` | 3 | same 3R built from the evaluator's fitted shape | 52.8 % | 64.5 % | best 3-DOF so far; fails reach back pocket |
| 10-15 01:45 | `cad_r13_n4_s1343_1` | 4 | turned skin-fitted JN hub + neck fixes | 32.0 % | 51.8 % | |
| 10-15 02:55 | `band_r14_4r_s1354_0` | 4 | GPU-searched 4R, L1 build | 49.7 % | 75.1 % | follows every clip |
| 10-15 05:10 | `band_r16_3r_s1373_1` | 3 | links must clear the skin over the plausible ROM (workspace envelope), L1 | 42.6 % | 55.3 % | 46.6 % of the functional workspace (R16); moves freely (R17) |
| 10-15 06:50 | r18 s1394 #1 (not kept) | 3 | range first (functional workspace, weight 4) | - | - | stand-off: J3 169 mm over the skin, link 2 twisted in CAD (counter-example) |
| 10-15 07:30 | `cad_r18_n3_s1394_0` (as built, not kept) | 3 | first fair CAD of a range-first design; scored at O17 hubs, built O23 | 13.2 % | - | judge stopped after R1: follows 76 %, 17 % in band at 10 mm |
| 10-15 07:50 | `cad_r17_n3_s1381_0` (as built, not kept) | 3 | balanced pick (64.7 % workspace, 38.9 % in band in the evaluator) | 12.1 % | - | judge stopped after R1: l1 x l2 collisions cut follow to 63 % (dominated) |
| 10-15 08:34 | `cad_r18_n3_s1392_1` | 3 | range pick at the real O23 hub, swept links | 13.5 % | 27.3 % | moves freely; follows 76 %; R16 45.8 % |
| 10-15 08:50 | **`cad_r18_n3_s1392_1_f300`** | 3 | same chain, smooth fair-field links (FAIR_LAM 300): **the rendered final of the night** | 15.3 % | 32.6 % | follows 80 %, overhead to 138 deg; R16 46.7 %; film in renders/2026-10-15_final_3R |
| 10-15 22:45 | `l1_seed-offset-3r-slides` | 3 (+3 passive cuff slides) | first new morphology from the concept bench taken to L1 CAD: offset 3R axes + along / across / radial self-aligning slides at the cuff, the CMA best k 403 (bench gap 54.95 vs the champion's 68.93); snapshot pipeline/evolution/l1_seed-offset-3r-slides/ | - | 53.7 % | follows 88.7 % (champion 98.2 %): the CMA's direction deltas put the top 44 % of Raise overhead into the J2 fold (overhead 36.4 % vs 48.7 %); ties the champion's R1 (54.1 %) |
| 10-15 23:05 | `param2_r20_n3_s1414_4` (v2) | 3 | the champion 3R redrawn in the user's own style: bent 8 x 3 bars from line/arc sketches, flat pads, lines-and-arcs U cuff (no loft), BOTTOM fused with the J3 arm end into one 5-axis part; snapshot pipeline/evolution/param2_r20_n3_s1414_4/ | 17.3 % | 32.9 % | before -> after the cuff/BOTTOM change: R1 34.0 -> 32.9 %, R16 74.2 -> 80.2 %, R6 0.0 -> 4.38 mm (the new cuff's distal end meets the user's FOREARM CUFF at elbow flexion, Drink from a cup); 6 of 19 pass; modelling paused, the user re-models it from drawings |
| 10-16 00:20 | `l1_rail-elbow` | 3 | concept-bench leader rail-elbow k2221 (CMA-converged, gap 56.25): J2 is a 2-stage telescopic curved rail on link 1, link 2 a carriage; L1 keep-out CAD from the kit model's own samples (pipeline/concept_l1/build_kit_l1.py, kinematics reproduced to 0.15 mm); snapshot pipeline/evolution/l1_rail-elbow/ | 22.9 % | 44.9 % | not MVP1-legal (stage 2 needs a 2:1 drive); the rail rides 127-148 mm from GH: overhead 33.4 % (champion 48.7 %); R6 2.85 mm and R16 45.8 % from the kit's J3 hub-zone overlap; 6 of 19 pass |
| 10-16 00:20 | **`l1_3r-k2221`** | 3 | the decisive control: the plain spherical 3R (kit `_template`, O20 hubs, 12 x 3 straps, neck) at rail-elbow k2221's axes (bench 51.33), same builder; snapshot pipeline/evolution/l1_3r-k2221/ | **27.6 %** | **56.1 %** | first concept-bench design to beat the built champion on R1 (54.1 %) and R1-aim (23.0 %); overhead level (48.2 vs 48.7 %); R16 39.2 % and R6 2.85 mm (same J3 hub-zone flaw), R17 fails on Wave only (l1-l2 contact); 5 of 19 pass |
| 10-16 01:35 | **`l1_offset-skin-normal-3r`** | 3 (+2 passive cuff slides, 2 catalogue guides) | first BUILDABLE concept-bench leader at L1: offset-skin-normal-3r k4216 (verified v_gap 42.59 vs the champion's 66.97): J1 / J2 on GH rays, J3 tilted toward the skin normal (line 7 mm off GH), 2 crossed THK RSR3M guides at the cuff (along guide inverted: block on the cuff, rail rides with carriage A), real 10.5 mm stack; kinematics reproduced to 1e-4 mm (pipeline/concept_l1/build_osn_l1.py); snapshot pipeline/evolution/l1_offset-skin-normal-3r/ | **42.0 %** | **78.7 %** | best built R1 / R1-aim so far (k2221 56.1 / 27.6, champion param2 32.9 / 17.3); R6 0.0 mm, R7, R17 pass (7 of 19, most yet); follows 90.9 %: the J2 fold holds Raise overhead above elev ~66 deg (R4 36.0 %), R16 57.5 %; 79 g |

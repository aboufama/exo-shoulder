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
| 10-15 07:30 | `cad_r18_n3_s1394_0` (as built) | 3 | first fair CAD of a range-first design; scored at O17 hubs, built O23 | 13.2 % | - | judge stopped after R1: follows 76 %, 17 % in band at 10 mm |

# Gen-6 fix: R7 strip glue, link 1a's climb in the L1, the drive's working end, R17 at 2x, cleanups (2026-10-17)

Design: roller-longdyad-knuckle-3r (verified 18.67 / score 93.21, held out 23.72 at ang_min 26.88). Builds:
`pipeline/full-exo/designs/l1_roller-longdyad` (L1, `pipeline/concept_l1/build_roller_l1.py`) and
`user_roller_longdyad` (full CAD, `pipeline/conformal/param_cad/user_style_roller.py`). The fix list is the independent
check's (`pipeline/full-exo/designs/user_roller_longdyad/VERIFY.md`, `judge/vs_l1.json`): (a) R1 -1.0 vs the L1,
(b) R7 link 1b, (c) R17 twist at 2x clip speed, (d) no judged frame at the drive's working end, (e) link 2's stale
groove, (f) the lobe ring's wall, (g) the two pins, (h) link 1a under the model's strap in the dyad gap.


## 1. R7: the shared strip glue (design-side fix, regression-checked)

**Root cause (measured).** `user_style_minarc.profile_link_split` builds links 1b / 2 as 4 side-view strips glued side by
side. Where two neighbouring strips share a stretch of profile exactly, the exact glue (`US.glue`) leaves **zero-area
faces** on the strip plane: a face bounded by the same line and the same arc twice (gen-6 link 1b: 8 of them). They are
valid in memory (`isValid()` True, which is all the builder checked) and fail BRepCheck once the part is written to STEP
and read back (link 1b: 1-3 faces, the judge's R7 FAIL; gen-5 link 1a: 2 faces). The builder accepted on the wrong test.

**Fix (shared builder, `pipeline/conformal/param_cad/user_style_minarc.py`).**
- `step_bad_faces(s)`: R7's own test in memory (STEP write, read back, BRepCheck per face, solid count) + zero-area count.
- `glue_strips(parts)`: candidates exact glue -> fuzzy fuse 1e-4 -> 1e-3 mm (coincident strip edges merge into one edge);
  a candidate with zero-area faces is re-sewn without them (`drop_zero_faces`: sewing at 1e-4 closes the zero-width gap,
  kept only if one valid solid of the same volume to 0.1 %); the first candidate that passes the STEP round trip with no
  zero-area face wins, else the old one-profile fallback.
- `sliver_free(body)`: the same re-sew on a finished part (later fuses / cuts can leave one), gated by the STEP test.
- Effect on the geometry: <= 0.001 mm (fuzzy value); no profile, station or level changes.

**Regression (part_validity's own test on every link part; gen 4b / 5 run with glue v1 = exact / fuzzy candidates, before the
re-sew step was added - `strip_glue_regression_v1_*.json`; the committed `pipeline/conformal/param_cad/strip_glue_regression.py`
re-runs it on the final code, queued; gen 6 = the final code in the rebuilt CAD):**

| build | link 1a | link 1b | link 2 | before |
|---|---|---|---|---|
| gen 4b user_minarc_bdp | exact, 0 bad | fuzzy 1e-4, 0 bad | exact (+ re-sew), 0 bad | R7 PASS |
| gen 4b user_minarc_pick1 | fuzzy 1e-4 (was the one-profile fallback), 0 bad | one profile (as before: no glue holds), 0 bad | exact, 0 bad | R7 PASS |
| gen 5 user_geneva_rod | fuzzy 1e-4, 0 bad (**was R7 FAIL, 2 faces**) | fuzzy 1e-4, 0 bad | exact, 0 bad | R7 FAIL |
| gen 6 user_roller_longdyad | (chain, not strips) 0 bad | fuzzy 1e-3, 0 bad (**was 1-3 bad**) | exact + re-sewn, 0 bad | R7 FAIL |

pick1's link 1a now glues as 4 strips where it fell back to one profile: a geometry change for its next rebuild (closer to
the strap), stated. Results: `docs/research/roller-longdyad-gen6_fix/strip_glue_regression_v1_*.json`.

## 2. R6 on the L1 and link 1a's climb (DESIGN change, L1)

The L1 drew link 1a's strap as the model's fitted slab, whose hub-footprint lift rises INSIDE the base's J1 upper boss
(R6 0.98 mm, every frame). The full CAD already drew link 1a as a line/arc chain starting at J1's skirt. Now there is one
source: `build_roller_l1.link1a_path` (J1 seat at J1's skirt **+ 0.15** (was 0.2 in the full CAD), concave R2 bend, ramp
<= 60 deg (60.0 used), convex R2 bend onto the K pad plane, 0.2 run, K seat solved >= hr + 0.05), used by the L1's strap
keep-out (`link1a_strap_mesh`, the 8 x 3 section swept along it, 3 mm into each pad) and by `user_style_roller.link1a_path`.

| L1 (fast judges, farm, FEA skipped) | before | after |
|---|---|---|
| R1 | 81.9 % | 82.0 % |
| R1-aim | 48.5 % | 48.6 % |
| R4 | 74.4 % | 74.5 % |
| R6 | 0.98 mm FAIL | **0.0 PASS** |
| R7 / R16 / R17 / R11 | PASS / 64.2 % / PASS / 0.39 | same |
| passing | 7 / 19 | **8 / 19** |

(h) stays as a stated deviation: the chain runs up to 4.40 mm under the model's strap in the dyad gap (it climbs from
J1's level where the model's strap is lifted over J1's footprint). Both builds now carry it, so the judges see it.

## 3. The drive's working end (measurement: new check, no design change)

`user_style_roller.working_end` (also `--working-end-only`, -> `judge/working_end.json`): the posed drive pairs and the
drive skin over the workspace's **115 closing, feasible poses at |dK| 29.39-46.25** (the cap), the range no clip frame
reaches. **No clash.** Rolling pairs closed on all 58 driven poses (follower on lobe -0.007..-0.028 mm, roller on flank
-0.000..-0.011: contact, inside R6's 0.15). Tightest running clearances: crank vs link 1a 0.108 mm (dK -44.87), follower
pin clip vs the lobe ring 0.113 (dK -41.28), crank vs link 1b 0.15, link 1a vs link 1b / hub J1 0.15 (the stack rules).
Drive skin minimum **2.491 mm** (the crank, workspace pose 56) against the >= 0.3 rule; roller 5.93, flank pin 5.12.
The full step-1 R16 run (judge/workspace.py --step 1) was not repeated here; the verifier's step-1 run stands (64.2 %).

## 4. R1 vs the L1 (partly done)

- **Arm straight run through the model's stations** (`user_style_roller.arm_profile`, `ROLLER_ARM=profile`): one
  side-view line/arc sketch in the plane through GH spanned by dR and the arc's tangent point, underside through the
  model's arm rows (root at the boss + 1.0, <= 60-deg ramp, lifted 0.26 over link 1b's BUILT bar over the swing), R2
  tangent rounds, extruded 6 across: levels 67.79 -> **58.98** -> 63.35 (the chord held 63.35+). Built as
  `user_roller_longdyad_arm` (valid crank, 96 parts) and judged fast on the farm: **R1 80.9 -> 81.2, R4 72.9 -> 73.5**,
  R1-aim 47.6, R6 0.0 PASS, R2 ours 17.67 (= the main build), R16 64.2, R17 PASS: the dk share of the attribution (+0.31)
  comes back. NOT adopted yet (builder default stays `chord`): its R7 and the builder's drive-skin / working-end checks
  were not run on it inside the box (the arm dips 4.4 mm lower; the drive-skin rule is >= 0.3 mm on every frame).
- **Lobe band lower**: not done. The lobe sits at F2 + 9.8..12.8 because the crank boss is raised 3.97 mm (link 1b's
  built bar top under the O10 footprint is 66.64 vs the model's 62.82; the L1's slab raises it 3.55 too). The follower
  rides the boss top, so the band only drops with the boss: that needs link 1b's bar lowered under the boss (its lift at
  hub K's footprint) or the follower beside the boss (a_s >= 8.1, the red team's 8.5 option, nose 13.19): a cam re-synthesis.
- **pick3's robust flank**: not adopted. pick3 is a different config (bk1 26.8, smhi 18.2, zr 3.77): fit60 ->
  Bench(110,360) 21.64 vs the verified 18.67, far above the 0.1 allowance; a flank-only transfer (beta / r_c / g on the
  verified shape) needs its own bench + verification run.

## 5. R17 at 2x clip speed (root cause: the exported mesh, fixed in the builder)

The full CAD's twist at 2x (5.16 / 5.22 deg) was not inertia of the real parts: **link 2's exported mesh was open** (zero-
area slivers left by the strip glue tessellate to nothing: a 10.6 mm seam), so `judge/dynamics.py mass_props` (seam
> 5 mm) took the split pieces' convex hulls: **l2 116.9 g / 26.4 cm3** against ~30 g real (link_inertia_about_gh l2 6.0e-4
vs the L1's 1.96e-4). The sliver fix (section 1) closes all but a 3.0 mm seam, under the judge's 5 mm whole-part rule:
the judge's own `mass_props` on the rebuilt exo.glb now gives **l2 29.42 g / 6.64 cm3** (L1 32.6 g). The R17 re-run is
**measured**: twist at 2x 5.16 / 5.22 -> **4.10 / 4.02 deg** (mu 0.005 / 0.002; L1 4.09 / 4.01), M_GH 0.143, cuff 0.63 N.
Not changed (reported): the CAD's knee still draws IGLIDUR pins (user_style_pinknee) while
CLAUDE.md now asks for MR63ZZ pairs, and the dynamics judge assumes rolling bearings at every joint and does not model the
knee stop (its own note: "the knee pins are free") although this CAD carries the stop tooth at 153.12 deg.

## 6. Cleanups

- (e) link 2's stale O18 groove at F+6.15..8.95 removed (the lobe ring seats on the J2 cap skirt at F2 + 9.8..12.8):
  link 2 4.42 -> 4.57 cm3.
- (g) flank roller pin named for what is drawn: **ISO 2341-A 3 x 6** (shank 6.0 under the O5 x 1 head; A: no split-pin
  hole, it is pressed); the crank pivot pin now sits in a real **O3 bore through link 1b** (the cut passes the STEP round
  trip on the fuzzy-glued bar; the first build could not cut it).
- Materials (bookkeeping, R8): `material()` matched "dowel hole(s)" in the names of links 1b / 2 and "683ZZ" in the
  crank's, so they were weighed as steel; numbered machined parts now take their stated alloy. Custom mass 181.0 ->
  149.6 g (R8 total 243.8 -> 212.4 g), a measurement correction, not a design change.
- (f) **lobe ring wall NOT fixed**: dwell r 10.886 over the O20 bore (0.89 mm in the sketch plane, 0.78 measured). The
  dwell is the follower's free-running locus (0.1 under it), so it cannot grow; the bore sits on the J2 cap's thin
  threaded skirt (r 9.0..10.0) below U1 = F+10.25. Cheapest real fix: turn the cap's solid crown section (F+10.25..12.25,
  r 4.5..10) to O19 and step the ring's bore there (wall 1.39 mm over 2 / 3 of the band) - a two-part change, queued.

## 7. Scorecard, full CAD (tools/judge_all.sh user_roller_longdyad fast, FEA skipped as before)

R1 / R1-aim / R4 / R2 / R16 / R11 from the farm run of the rebuilt CAD; R7 (judge/part_validity.py), R6 (part_contact
--step 3) and R17 (dynamics) re-run locally on the same files after the farm upload (the farm worker read the old
part_validity.json it was shipped); scorecard by judge/scorecard.py.

| | before (gen 6, verified) | after | what moved it |
|---|---|---|---|
| R1 | 80.9 % | 80.9 % | design (link 1a clr 0.2 -> 0.15, link 2 groove filled): no change |
| R1-aim | 47.5 % | 47.6 % | design |
| R4 | 72.9 % | 72.9 % | - |
| R2 | 24.87 (user's cuff; ours 17.67) | same | - |
| R6 | 0.0 PASS | 0.0 PASS (link 2 now tested as a container) | measurement got stricter, design holds |
| R7 | **FAIL** (link 1b, STEP) | **PASS** (49 / 49) | design (strip glue) |
| R8 | 243.8 g | 212.4 g | MEASUREMENT (material bookkeeping) |
| R11 | 0.249 kPa | 0.262 kPa | MEASUREMENT (l2 mass now the real one) |
| R16 | 64.2 % | 64.2 % | - |
| R17 | PASS, 2x twist 5.16 / 5.22 | PASS, 2x twist 4.10 / 4.02 | MEASUREMENT (closed link-2 mesh; the metal is the same) |
| passing | 7 / 19 | **8 / 19** | R7 |

Arm option (`user_roller_longdyad_arm`, not adopted): R1 81.2, R4 73.5, the rest as above (R7 not run).
L1 (`l1_roller-longdyad`): 7 -> 8 of 19 (R6), R1 81.9 -> 82.0 (section 2). The full CAD still trails its L1 by 1.1 on R1
(0.8 with the arm option): the real lobe ring (section 4) is the rest.

## Open (next)

- Adopt the arm option after its R7 and drive-skin / working-end runs; lower the lobe band (boss under link 1b, or the
  a_s 8.1+ follower beside the boss with a re-synthesised cam).
- Lobe ring wall (f): cap crown turned to O19 + stepped ring bore (two-part change).
- Knee: MR63ZZ pin pairs in user_style_pinknee (CLAUDE.md), and the dynamics judge's knee stop (judge change: the
  judge owner's call, reported here, not edited).
- Re-run `strip_glue_regression.py` on the final glue code for gen 4b / gen 5 (v1 results here); flank-only pick3
  transfer needs a bench run.
- Farm spend this task: 3 judge jobs, $0.11 shared / $0.52 alone (exo-cpu1, cpu3c), within the $0.6 cap.

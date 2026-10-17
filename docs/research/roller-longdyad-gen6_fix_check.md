# Independent check of the gen-6 fix (roller-longdyad-knuckle-3r, 2026-10-17)

Checks `docs/research/roller-longdyad-gen6_fix.md` (commits 5a3c8e4, 09e19b8, ef087c4; builders committed in the WIP
commits b9e2003 / 8c0194d / baf62e0). Builds: `pipeline/full-exo/designs/user_roller_longdyad` (full CAD, rebuilt
09:25), `l1_roller-longdyad` (L1). Every number below comes from an outside judge run by this check, or from a direct
measurement of the committed STEP / glb files. Outputs are in `docs/research/roller-longdyad-gen6_fix_check/`.

**Verdict: NOT REFUTED.** The four claimed moves reproduce exactly: R7 PASS, L1 R6 PASS, the R17 twist correction and
the pick3 rejection. But the claim leans on a step-1 workspace run that never existed. The first step-1 R16 run on
this CAD (this check) finds **10 poses with a part inside the body**, two of them link 2 at the drive's working end.
Their attribution is in section 3. Other issues: link 1a still carries a degenerate face that R7 does not catch, and
two cleanup labels are wrong (sections 2 and 6).

## 1. Judges re-run on the claimed configuration

| requirement (judge) | claimed | this check | how |
|---|---|---|---|
| R7, full CAD (judge/part_validity.py) | PASS, 49 / 49 | **PASS, 49 / 49, 0 bad faces**, JSON identical to the committed one | local |
| R6, L1 (judge/part_contact.py) | 0.0 PASS (step 3) | **0.0 mm PASS at step 1** (every frame, every clip: 1337 frames x 2804 pairs, 990k samples) | local, 2 jobs |
| R6, full CAD (judge/part_contact.py) | 0.0 PASS (step 3) | **0.0 mm PASS at step 1** (1337 frames x 5506 pairs, 1.59M samples; 1 open part closed as a container) | farm |
| R17, full CAD (judge/dynamics.py, all 23 cases) | PASS; 2x twist 4.10 / 4.02 deg | **PASS; 2x twist 4.10 / 4.02 deg** (mu 0.005 / 0.002); 1x 4.08 / 4.00; M_GH 0.143 N.m; F 0.63 N. Every nominal number matches the committed run | local, 2 jobs |
| R16, full CAD (judge/workspace.py) | 64.2 % (step 12, 120 poses) | **70.3 % at step 1** (1432 poses): chain does not close 29.1 %, **body contact 0.7 % (10 poses)**, part interference 0.0 % | farm |

The R16 difference (64.2 % to 70.3 %) is sampling, not a design change: step 12 judges 120 of the 1432 poses.
None of the 10 body-contact poses (k 34, 35, 75, 487, 500, 506, 609, 614, 723, 832) is a multiple of 12, so the
step-12 run never saw them.

**The fix document says "the verifier's step-1 result stands (64.2 %)". That is wrong.** VERIFY.md reports R16 at
step 12 (120 poses) and says only that a step-1 run *would* cover |dK| 42.4..46.25. No step-1 run existed before this
check. The working end had been covered only by the builder's own `working_end()` check, which is self-assessment.

## 2. Failure cost reproduced (one case each)

- **The mass the R17 judge read for link 2.** I ran judge/dynamics.py `mass_props` on the pre-fix exo.glb (8e60d0e,
  the last exo.glb before the rebuild):
  - pre-fix: group l2 **116.91 g / 26.39 cm3**. Link 2's mesh is open with a **10.62 mm** seam, so the judge falls
    back to the convex hulls of the split pieces (link 2 alone reads 107.7 g).
  - rebuilt: **29.42 g / 6.64 cm3**, seam 2.99 mm. Link 2 alone reads 20.24 g, which is its B-rep volume (4.571 cm3)
    times Ti density. The claim reproduces exactly.
- **R7 on link 1b.** The pre-fix link 1b STEP (8e60d0e and 456da59) gives 1 face failing BRepCheck, `isValid()` False,
  and 9 zero-area faces. The rebuilt one gives 0 bad faces and 0 zero-area faces.
- **Material bookkeeping.** In the pre-fix parts table, link 1b, link 2 and the crank were weighed as steel (24.46 /
  34.70 / 9.25 g). The rebuilt table has 13.8 / 20.25 / 5.25 g in Ti. Confirmed.
- **The pivot bore.** The rebuilt link 1b has a coaxial r 1.500 bore along the pivot pin's axis (axis offset
  0.002 mm). The pin has 0.000 mm3 overlap with link 1b, and every pin-axis point lies outside the link. The STEP the
  verifier judged (456da59) had no bore. History note: an earlier WIP build (8b56094 / 8e60d0e) already had it.

## 3. Body contact at step 1: attribution

The judged pose triples are [plane, elevation, axial] in degrees.

| k | pose | depth | part | dK |
|---|---|---|---|---|
| 506 | [15, 165, -60] | 10.44 mm | link 1a | 0 |
| 500 | [15, 150, -60] | 9.23 | link 1a | 0 |
| 832 | [60, 165, -30] | 7.66 | link 1a | 0 |
| 609 / 614 / 723 | elev 150-165 | 6.4-6.5 | link 1a | 0 |
| 35 | [-90, 60, 120] | **5.93** | **link 2** | **43.1** (working end) |
| 34 | [-90, 60, 105] | 3.92 | link 2 | 20.7 |
| 75 | [-75, 60, 105] | 2.03 | link 2 | 25.4 |
| 487 | [15, 105, 15] | 1.01 | link 1b | 0 |

All 115 closing poses at |dK| >= 29.3 (up to 46.25) have **0.0 mm part interference**. This is an outside judge
agreeing with `working_end()` on parts. One of those poses (k 35) puts link 2 5.93 mm into the body.

ATTRIBUTION_PLACEHOLDER

## 4. Gap claim on the bench (Bench(110,360) exact, frozen, margin 5)

`tools/roller_env_polish.py claim fit60 bench`, CB_EXACT=1, CB_FOLD_MARGIN=5, run on the farm:

| config | stops | gap | follow | depth (n / sum) |
|---|---|---|---|---|
| verified (BEST) | nominal (PA 43) | **18.67**, the verified number exactly | 1.0 | 2 / 16.5 |
| verified, ang_min 26.88 (BEST_am) | priced (smlo + 0.5, a1max <= bk1 + bk2 - 5, PA 42) | **19.25** | 1.0 | 2 / 15.9 |
| pick3 | priced | **21.65** | 0.9636 | 9 / 18.1 |

The fix document rejected pick3 because "21.64 vs the verified 18.67". That compares two protocols: pick3 with priced
stops against the verified config with nominal stops. On the same protocol (priced, margin 5) the gap is **+2.40**
(21.65 vs 19.25), not +2.97. The rejection holds: the gap is far above the 0.1 allowance, and pick3 also loses clip
follow (0.9636).

## 5. Builder fixes applied, no lofts

- **`user_style_minarc.py`** has `step_bad_faces`, `GLUE_FUZZ = (None, 1e-4, 1e-3)`, `drop_zero_faces`,
  `glue_strips` and `sliver_free`. `profile_link_split` now glues only through `glue_strips`.
- **`user_style_roller.py`:**
  - `link1a_path` returns `RL1.link1a_path(M)`.
  - `sliver_free` runs on links 1b and 2.
  - The groove cut is gone (`LOBE_Z` is kept only as a comment).
  - The flank pin is named ISO 2341-A; the `--working-end-only` option and the alloy-based `material()` are present.
  - `build.json` records:
    - link 1b: exact glue 2 bad / 8 zero-area, fuzzy 1e-4 invalid, fuzzy 1e-3 accepted with 0 / 0;
    - link 2: exact glue + re-sew, then 1 more zero-area face removed by `sliver_free`;
    - the pivot bore was cut.
- **`build_roller_l1.py`** has `L1A_PATH` (clr_J1 0.15, ramp 60 deg), `link1a_path` and `link1a_strap_mesh`.
- **No lofts reachable.** No `loft` / `makeLoft` / `ThruSections` call exists in `user_style_roller`, `user_style_minarc`,
  `user_style_pinknee`, `user_style`, `sketch2d`, `build_roller_l1` or `build_minarc_l1`. The only loft in the import
  chain is `param_build.strap_solid`, and only `param_build.main()` calls it. The user-style builders use
  `PB.joint_parts / revolved / axis_frame / disc_face`, none of which lofts.
- **Glue regression on the FINAL code.** The fix stored only v1 results. I ran `strip_glue_regression.py` locally:
  - gen-5 `user_geneva_rod`: link 1a passes (exact glue + re-sewn; it was R7 FAIL, 2 faces); link 1b passes; link 2
    passes the STEP test but **keeps 1 zero-area face**;
  - gen-4b `user_minarc_pick1`: link 1a passes (fuzzy 1e-4, 4 strips); link 1b passes; link 2 passes but **keeps 1
    zero-area face**;
  - gen-4b bdp: not re-run (time box).
  - Outputs: `strip_glue_regression_final_*.json`.

## 6. Real parts at real sizes

- Bearings (MR117-2RS, 683ZZ, MR63ZZ), ISO 8734 dowels, DIN 6799 clips and ISO 2341-A 3 x 6 (d 3: dk 5, k 1; l 6 is
  a catalogue length) are all real catalogue parts. Densities are standard (Ti 4.43, 17-4PH 7.8).
- **The crank pivot pin's fit is mislabelled.** The parts table and build.json say "O3 h6 **pressed** in an O3 **H7**
  bore". H7/h6 is a sliding clearance fit (0 to +16 um), not a press fit. The pin is held only by its DIN 6799 clip
  and can turn in link 1b's Ti bore under the crank's load. Use an ISO 8734 m6 dowel (or call for H7/p6), as the
  stop dowels already do.
- The flank pin "ISO 2341-A ... pressed" has the same problem: ISO 2341 pins are made to h11, which cannot hold a
  press fit. Retain it (a clip groove) or switch to an m6 ground pin.
- The module docstring of `user_style_roller.py` (line 31) and its `--l1` report string (line 821) still say
  "ISO 2341-B 3 x 8". The parts and STEP names are correct.
- The fix relies on no new curve, torque or force. R17 uses the judge's own MuJoCo model (rolling bearings,
  mu_eff 0.005 nominal, sourced in judge/dynamics.py).

## 7. Red team: where each fix stops working

1. **R7: parts that never go through the glue.**
   - Link 1a in this CAD is the chain plus pads (`US.glue`), and `sliver_free` is not applied to it. Its STEP holds a
     **degenerate face** (area -2.2e-19 mm2, two 2e-9 mm edges). It passes R7, but after one more write and read the
     solid's volume reads **8.4e167 mm3**. A third pass drops the face, and the volume returns to 2847 mm3.
   - A supplier's CAM or mass report that re-exports would get nonsense.
   - The gen-4b / gen-5 link 2 also keep 1 zero-area face (section 5). That is the same class that opened gen-6's
     link 2 mesh and quadrupled its judged mass.
   - Fix: call `sliver_free` on every link (1a included) in the shared builders, not only in `user_style_roller`.
2. **R7: the fuzz.** Link 1b is accepted at the 1e-3 mm fuzzy fuse, but its STEP has a vertex with **0.018 mm**
   tolerance (at [-27.73, 45.44, 27.26], group frame). That is 18 times the "<= 0.001 mm" the fix states as its
   geometric effect. Four planar faces of about 1e-3 mm2 remain, and link 2 keeps 13 faces under 0.01 mm2 and 16
   edges under 0.01 mm. Each schema (AP203 / AP214 / AP242) survives a second round trip (0 bad faces, volume change
   3e-4 mm3), so this is DFM hygiene, not an R7 risk. If a shared-chain rebuild finds no clean candidate, the builder
   falls back to the one-profile bar and only prints it. That fallback changes R1 silently.
3. **R17: the measurement fix sits 2 mm from the judge's threshold.** Link 2's remaining open seam is 2.99 mm against
   `mass_props`' 5.0 mm whole-part rule. A rebuild with slightly different slivers reopens the hull fallback, and the
   twist at 2x went to 5.2 deg the last time that happened.
   - Margin on the rule: 0.90 / 0.98 deg (4.10 / 4.02 vs 5.0).
   - The CAD's knee draws iglidur plain pins, while the judge's nominal case assumes rolling bearings at every joint.
     The all-plain cases (mu 0.06) give 16.8-20.2 deg, and no mixed rolling + iglidur-knee case exists.
   - Judge observations for its owner (not edited): `dynamics.density()` weighs the MR117 / 683ZZ bearings outside
     H / F as Ti (0.75 g, where the parts table gives 1.32 g). The judge has no knee stop.
4. **Working end: running clearances below the machining tolerance.** `working_end()` reports crank to link 1a
   **0.108 mm** (dK -44.87), follower clip to lobe ring 0.113 mm (dK -41.28), and crank to link 1b 0.15 mm.
   - ISO 2768-m on these 5-axis Ti parts is +-0.1 mm (f: +-0.05).
   - The crank's own tilt on 2 x 683ZZ (radial play about 0.01 mm over a 6 mm boss, about 25 mm to the arm) adds about
     0.05 mm.
   - So the crank-link 1a pair closes at |dK| > 44 for a plausible stack. Call for f-class tolerances on these faces, or
     open the gap to >= 0.3 mm.
   - R6's 0.15 mm allowance would not catch a 0.1 mm rub.
5. **L1 link 1a climb.** It starts 0.15 mm radially outside the J1 boss and 0.15 mm under its skirt. The pair is
   coaxial with J1, so the gap does not change with motion, and the MR117 tilt is about 0.005 mm. It holds up to about
   +-0.07 mm per part.

## 8. Issues for the next builder pass (not edited here)

- Run `sliver_free` on link 1a and on every link in the gen-4b / gen-5 and shared-chain builders, and re-run R7 plus
  a second STEP round trip.
- Address the step-1 body contacts. Link 1a reaches 10.4 mm at overhead (elevation 150-165). Link 2 reaches 5.9 mm at
  the working end (pose k 35, dK 43.1). Attribution is in section 3; tools/judge_all.sh only runs R16 at step 4 / 12.
- Fix the crank pivot pin fit (an m6 dowel, or H7/p6) and the flank pin retention. Update the stale ISO 2341-B
  strings.
- Specify tolerances on the crank-link 1a gap (0.108 mm at dK -44.87).
- Correct the fix document: the "verifier's step-1 R16" never existed, and the pick3 gap is +2.40 on a like-for-like
  protocol.

## Spend

- Farm:
  - 3 bench claims: $0.016.
  - CAD R6 + R16 at step 1: $0.048.
  - 3 glue jobs that failed (the farm image has no cadquery): $0.008.
  - 2 R16 attribution jobs: ATTR_COST.
  - Total about TOTAL_COST, under the $0.6 cap.
- Local: at most 2 processes, niced.

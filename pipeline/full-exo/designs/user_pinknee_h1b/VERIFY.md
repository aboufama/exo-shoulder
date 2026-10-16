# Independent check: user_pinknee_h1b (the gen-3 CAD rebuilt so its bars follow the verified model's strap)

Checker (a skeptic), 2026-10-16 12:32-13:45 UTC. What I tested: the builder's claim in commits 0336225 / 9303730 (and
the lead's WIP commits e469b3c, 2bd6201 that carry the builder, sketch2d and judge/part_validity.py): bars machined to
hug the model strap, DIN 6799 pin land, the R7 judge fix, and the before / after scorecard.

Everything below is re-measured from the files in this directory and user_pinknee_h1/ with my own scripts (session
scratchpad vfy_pkb/: dev.py, climb.py, pins.py, groove2.py, flyfast.py, l1hit.py; not in the repo). The judges ran on the farm with
`--outdir` (scratch) and R7 locally on copies, so no judge file in the tree was overwritten. I changed nothing in the
design.

**Verdict: NOT REFUTED.** Every re-run judge reproduces the claimed scorecard exactly (R1 76.72 %, R1-aim 35.79 %, R4
71.23 %, R6 0.0 mm, R16 61.67 %, R7 PASS, 8 of 19), and the claimed bar-over-model residual is what I measure.

What holds:
- The bar-over-model numbers reproduce to 0.01 mm (link 1 4.13 -> 2.58 mm, link 2 10.90 -> 5.56 mm), and the kinematics
  are still the model's (clip G / T vs the model chain 5.0e-7 / 4.8e-5 mm at 8 clip frames).
- R7 reproduces row for row (29 / 29); the judge change skips only the user's untouched parts and catalogue screws.
- No loft is reachable; both bars are a single section swept on a line / arc wire; the tight bends are on parts
  labelled "5-axis machined from solid".
- The pins have the 1.0 mm land and stand 0.9 mm proud; no knee-side part comes within 36 mm of link 2 (1616 frames).

Corrections and notes (none changes a requirement's status): see "Corrections" at the end.

## 1. Bar over the model strap, 8 clip frames (both designs posed the judges' way)

Method: the frozen H1 shape worn (`pinknee_shape.wear(".cache/pk_shapes/h1_b110_360_m5.pkl")`), the model chain
(`build_pinknee_l1.chain`) at 8 followed clip frames, exo.glb posed by `scene_export.posed_scene` on clips.json.
`M.link_pts` are the model strap's UNDERSIDE samples (radial from the member origin). Two measures per sample:
- (u) libigl unsigned distance to the built bar part alone (D8-02 / D8-03);
- (r) radial lift: a ray from the posed member origin along the sample's direction, first hit on the built bar;
  lift = r_hit - r_model (+ = bar underside above the model strap). Per station I report the lift at the CLOSEST
  column (a flat bar resting on the strap's highest column; comparable to the claim's in-plane measure (b)) and the
  spread across the 8 mm width (the cross-width tilt).

Frames (identical in both clips.json): Raise overhead 78 (the highest followed frame, elev 150), Reach back pocket 72
(plane -80, behind the back), Comb hair 105, Wash opposite shoulder 81 (across the body), Walking 0 (arm at the side),
Reach a high shelf 75, Drink 72, Wave 63. Every number below is the same at all 8 frames to 0.001 mm (the bars are rigid
on their members and the clip transforms equal the model chain).

"Outside the hub zones" = model samples more than hr + 3 mm off both hub axes of that link (the L1's lifted zone + 0.5);
this keeps the ramp feet in (L1 stations 15.2-27.3, L2 15.2-76.1 in the model's station coordinate), so it is a little
wider than the claim's "between the hub zones".

| measure | link 1 h1 -> h1b | link 2 h1 -> h1b | claim |
|---|---|---|---|
| (u) max, all samples | 4.131 -> **2.575** mm | 10.904 -> **5.561** mm | 4.13 -> 2.58 / 10.90 -> 5.56 |
| (u) outside the hub zones, max / mean | 4.13 / 2.74 -> **2.08 / 0.89** | 10.90 / 4.96 -> **5.56 / 1.89** | 2.08 / 0.98; 4.73 / 1.70 (their narrower span) |
| (r) closest column, max / mean over the stations | 6.26 / 3.23 -> **1.51 / 0.66** | 9.44 / 3.98 -> **5.26 / 0.90** | in-plane 1.45 / 0.48; 5.22 / 0.45 |
| stations with the closest column within 0.5 / 1.0 mm | 0 / 0 of 7 -> **3 / 6 of 7** | 5 / 6 of 31 -> **22 / 24 of 31** | span 62 / 87 %; 86 / 89 % |
| cross-width tilt (max - min lift per station), max / mean | 1.22 / 0.70 (unchanged) | 4.07 / 2.33 (unchanged) | 1.22 / 0.82; 2.96 / 2.22 |
| (r) min lift outside the zones (bar never below the strap there) | +1.72 -> **+0.15** | +0.02 -> **+0.08** | - |
| model samples inside the bar (signed distance) | 0 -> **0.29** mm | 0 -> **0.29** mm | 0.29 (seat plate, inside the footprints) |

Where the residual sits (closest-column lift, h1b):
- link 1: 1.51 mm at the J1 end of the span (station 15.2, the foot of J1's drop), 0.84 at 17.2, then 0.15-0.78.
- link 2: 3.70 / 2.60 / 1.64 mm at stations 15.2 / 17.2 / 19.3 (the foot of the drop after J2's footprint), 0.08-0.26 mm
  from 23 to 66, then 0.79 / 2.23 / **5.26** / 4.96 / 2.66 mm at 68-76 (the J3 ramp foot).

**Check 1 holds.** The claimed deviation numbers reproduce, and the residual is where the claim says it is: the two
ramp feet on link 2, J1's drop on link 1, and the cross-width tilt that a flat (untwisted) bar cannot follow. My tilt
figure for link 2 (4.07 mm max) is higher than the claim's 2.96 because my zone keeps the J3 ramp stations, where the
radial ray meets the sloped bar obliquely; the mean agrees (2.33 vs 2.22).

## 2. The judges, re-run

Farm: `python3 tools/cloud_run.py judge user_pinknee_h1b fast --outdir <scratch>` (SKIP_FEA, as the claim): job 1255 s on
1 worker, ~$0.10-0.12 (log in the session's cloud_run logs, tag vfy_pinknee_h1b). R7 does not run on the farm (no
cadquery there: `ModuleNotFoundError`), so the farm scorecard takes R7 from the tree; I ran R7 locally with OCC on a copy
(section 3).

What came back:
- score.json, score_14mm.json, scorecard.json / .md and two more judge files came back **byte-identical** to the
  committed ones (cloud_run: "6 rewritten byte-identical to the tree").
- workspace.json and body_contact.json: identical apart from timing fields; part_contact.json: identical apart from
  setup / CPU seconds; dynamics.json: identical values, only the order of the `lock_clips` lists differs.

| req | claim (h1b) | my re-run | h1 (its VERIFY.md re-run) |
|---|---|---|---|
| R1 (2-14 mm) | 76.72 % | **76.72 %** (in-band 0.7672, overall 75.7 %) | 71.40 % |
| R1-aim (2-10 mm) | 35.79 % | **35.79 %** (overall 35.3 %) | 32.85 % |
| R3 follow | 98.7 % | **98.67 %** | 98.67 % |
| R4 overhead (Raise overhead, 14 mm band) | 71.23 %, min gap 1.79 mm | **71.23 %**, median gap 12.50, min gap **1.79 mm** | 68.67 %, min 1.78 |
| R6 | 0.0 mm, 451 x 2586 | **0.0 mm**, 451 frames x 2586 ordered pairs, 1.39 M samples | 0.0 |
| R16 | 61.67 % | **61.67 %** (closure 34.2 %, body 4.2 %, parts 0.8 %) | 61.67 % |
| R2 | 24.87 mm (user's forearm cuff); ours 17.67, attributable 4.71 | **24.87**; ours 17.67, attributable 4.71 (D8-06) | same |
| R7 | PASS 29 / 29 | **PASS**, 29 / 29 (local OCC, identical rows) | PASS |
| R8 / R11 / R17 | 178.0 g / 0.213 kPa / PASS | **178.0 g / 0.213 kPa / PASS** | 178.9 / 0.303 |

Per clip (14 mm band) the re-run equals the claimed clip scores (byte-identical score_14mm.json): Raise overhead 71.2,
Drink 76.2, Comb hair 83.3, Reach a high shelf 85.4, Wash opposite shoulder 54.2, Reach back pocket 91.5, Wave 62.8,
Walking 91.7 %.

**Check 2 holds: every re-run value equals the claim; 8 of 19 pass.** The before / after attribution is right: the
judges, step, clips, frozen shape and L1 frames are the same for h1 and h1b, so R1 +5.3, R1-aim +2.9, R4 +2.6 are the
design change.

## 3. The R7 change (judge/part_validity.py)

Read in full (diff a3eb02a..e469b3c) and run on copies.

- **Skip list:** only H / F parts whose names start with the user's own unmodified part names (TOP, MIDDLE, FOREARM,
  Hex, M4 ULTRA, IGUS, 5mm, Revolve, CirPattern) or that are catalogue screws ("ISO 10642" or "screw" in the name).
  I listed every H / F node of h1b and of the L1 l1_skin-normal-3r-pin-knee-h1. Every skipped node is one of the user's
  parts as they come from the user's model or a catalogue screw; no project part name starts with those prefixes or
  contains "screw". BOTTOM is judged (cut, the only user part we may modify). Nothing of the user's untouched parts is
  judged.
- **L1 branch** (l1_skin-normal-3r-pin-knee-h1, local run on a copy): 17 parts judged, 5 arm-fixed (the project's
  upper-arm cuff, cut BOTTOM, pad mount, pin b retainer, arm pad). All pass except **BOTTOM: 7 pieces, not closed**,
  exactly as claimed. R7 FAIL, and its scorecard reads 7 of 19.
- **STEP branch** (h1b, local OCC run on a copy): 29 STEP files, all valid single solids, 0 bad faces; my
  part_validity.json is identical to the committed one row for row; coverage 29 custom parts (3 arm-fixed: D8-06,
  pin b thrust washer, upper-arm cuff), none missing. The catalogue E-clips (DIN 6799) and ISO 10642 screws carry no
  STEP and are excluded from coverage, which is right for catalogue parts. Note that five STEPs tessellate non-watertight
  at the judge's 0.02 mm (the three dome caps, D8-06, the cuff): R7's STEP branch does not require it (OCC validity is
  the test), the L1 branch does - the two branches use different criteria, as before the change.
- **Scope of the measurement change is wider than stated.** The cut BOTTOM mesh is inherited by every L1 from
  l1_seed-offset-3r-slides (`build_pinknee_l1.USER_SRC`; same 7-piece mesh). Re-run on copies, the new judge also fails
  **l1_skin-normal-3r-pin-knee** and **l1_offset-skin-normal-3r**, whose committed scorecards still say R7 PASS (stale
  until re-judged). The same mesh sits in l1_seed-offset-3r-slides, l1_3r-k2221, l1_rail-elbow,
  l1_skin-normal-3r-pin-knee-k4598-m5 and the gen-4 **l1_minarc-bdp** (being judged on the farm now), so their R7 will
  read FAIL too. The cure is in the shared L1 path: drop the 6 stray triangles and close the cut face of the inherited
  BOTTOM mesh once, then re-judge.

**Check 3 holds** (the judge now judges what it should and skips only the user's untouched parts), with the scope note.

## 4. No lofts; bend radii, ramps, machined parts stated

- **Static trace** of the new code: sketch2d.hug_chain / hug_chain_pieces (numeric fitters: least squares + SLSQP over
  line / tangent-arc chains, no CAD calls) and user_style_pinknee.hug_fit / ring_root_R. Both bars are built by
  `US.bar_swept` (one constant rounded-rectangle section, BRepOffsetAPI_MakePipeShell on a line / three-point-arc wire,
  fixed binormal = the sketch normal), then cut / fused with plates and bores. grep for loft / ThruSections /
  interpPlate / spline / BRepFill / twist / GeomAPI in the builder, sketch2d and the fixup: no hit except the builder's
  own "no lofts" docstrings. The rest of the call graph is h1's, traced by the h1 verifier. **No loft is reachable.**
- **Radii** (build.json, cross-checked against the segment curvatures): link 1 centre-line R 16 / 25 / **3** / 120 / 4
  (inner 1.5 mm); link 2 R 3.5 / 18.5 / 12.5 / 440 / 95 / 17.5 / 610 / 20.5 / 82.5 / 11 / 6.5 / 10.5 (inner **2.0 mm**).
  Both are below the 15 mm bent-bar rule, which the ruling allows only on a part 5-axis machined from solid **and stated
  on the part**: both names in parts_full.json / exo.glb / the STEP say "5-axis machined from solid Ti-6Al-4V ... bends
  down to R3 (R3.5) on the centre line, below the 15 mm bent-bar rule". Holds.
- **Ramps:** builder 59.48 / 59.63 deg (in the bar plane, against the circle about the sketch origin). My own measure,
  the slope of the built underside against the local sphere about the posed member origin along each model column,
  outside the 12.5 mm seat footprint: link 1 **60.9 deg** (stations 26.8-27.3, the J2 end), link 2 **58.7 deg**.
  Link 1's 0.9 deg over is the difference of reference (the bar plane does not contain the member origin; my rays are
  3-D), not a second ramp; I count the 60 deg ruling as met within that ~1 deg. (h1's bent link 2 measured 68 deg the
  same way at its J3 end; h1b removed that.)

**Check 4 holds.**

## 5. Pins, groove land, link 2 fly-over

- **Pin land** (exo.glb, along the axis of each E-clip; the pin cross-section fitted per slice): the O4 pins carry an
  O3.2 groove exactly under the 0.6 mm clip, then **1.0 mm** of pin to the end face (0.7 mm at O4 + a 0.3 mm chamfer);
  the end face stands **0.9 mm** proud of the knee link's outer face. h1: 0.1 mm past the clip, flush with the knee
  (as C2 of h1's VERIFY said). Same for pin a (member 3) and pin b (D8-06). As claimed. Note: DIN 6799 gives the land
  n >= 1.0 mm for the 3.2 groove; the 1.0 here includes the 0.3 chamfer (0.7 mm at full diameter). For an unpowered
  knee pin with a thrust washer this is fine, but the drawing should say which; a 1.3 mm land costs 0.3 mm more height.
- **Fly-over** (pins.py): link 2 (bar alone, and the whole l2 group incl. the J2 / J3 caps) against every knee-side
  part - knee link + both sleeves, both clips + washers, member 3's pin-a boss region (within 8 mm of pin a), D8-06
  BOTTOM + pad + pin b - posed by scene_export.frame_xforms at every 2nd clip frame plus every eval-feasible workspace
  pose: **1616 frames** (671 clip frames + 945 eval-feasible workspace poses;
  the claim says 1146 for "every 2nd clip frame + every eval-feasible pose" - its count differs from mine, its
  conclusion does not). Method (flyfast.py): link 2 kept in its own frame (KD-tree on its vertices), every knee-side
  part's vertices mapped into it per pose, refined to the exact libigl point-to-mesh distance below 5 mm.

  | knee-side part (h1b, longer pins) | closest approach to link 2 (bar and whole l2 group) | where |
  |---|---|---|
  | knee link D8-05 | **38.5 mm** | workspace pose 374 |
  | pin a thrust washer / E-clip / sleeve | **41.0 / 42.3 / 42.4 mm** | same pose |
  | D8-06 BOTTOM + pad + pin b | **50.2 mm** | same pose |
  | pin b thrust washer / sleeve / E-clip | **53.2 / 54.5 / 54.7 mm** | same pose |
  | member 3's pin-a boss region (within 8 mm of pin a) | **36.0 mm** | workspace pose 374 |
  | member 3 whole (for reference) | 0.15 mm to the bar at J3 (the designed running gap), 0.0 to the l2 group (the J3 bearings seated on member 3's O7 pin, a static fit judged by R6) | |

  The 0.9 mm the pins now stand proud changes nothing here: the nearest knee-side metal (member 3's pin-a boss) is 36 mm from
  link 2 in every pose. (The claim's "> 4 mm" is right and very conservative.) I did not re-run h1 to completion (the h1 pass was
  stopped to save time; h1's pins are 0.9 mm shorter, so h1 can only be farther).

**Check 5 holds.**

## Corrections

1. **R7's measurement change reaches every L1**, not only l1_skin-normal-3r-pin-knee-h1 (section 3). Two committed L1
   scorecards (l1_skin-normal-3r-pin-knee, l1_offset-skin-normal-3r) still show R7 PASS and fail it when re-judged;
   the gen-4 l1_minarc-bdp will fail it on the same inherited BOTTOM mesh. Fix the shared mesh, then re-judge.
2. **R16's reason is imprecise.** The claim says R16 "cannot move" because the workspace judge poses the L1 frames. The
   judge does pose the built parts (exo.glb) for body contact and part interference; R16 stays at 61.67 % because its
   binding failures are chain closure (34.2 %), five poses where **link 1** enters the body (0.70-3.27 mm, poses 23 / 30 /
   39 / 40 / 49 at step 12) and one link 2 / member 3 interference - and those are identical in h1 and h1b to 0.01 mm.
   I located the link-1 hits myself (rig body posed by body_pose, libigl signed distance): the deepest vertex is at
   9.8-10.0 mm off the J2 axis in all five poses, i.e. the rim of link 1's O20 J2 ring / plate, which the rebuild did
   not move (pose 40 = plane 15 / elev 90 / axial 60: 3.27 mm, 835 vertices deeper than 0.5 mm). That is a lever for
   R16 (and R2) the claim does not list.
3. The 0.5 mm bar target is not met (disclosed). Measured by me: link 2 is 5.3 mm over at the J3 ramp foot and 3.7 mm
   over just after J2's footprint; link 1 1.5 mm at J1's drop.
4. The pin land includes the chamfer (section 5).
5. The fly-over frame count: every 2nd clip frame + every eval-feasible workspace pose is 671 + 945 = 1616 frames here,
   not 1146; the conclusion (no knee-side part near link 2) holds with a far larger margin than "> 4 mm" (36 mm).

## What next

- The fix that buys the most: link 2's two ramp feet (5.3 / 3.7 mm) - a 2 mm centre-line bend at each ramp end or
  leaving J2's level earlier (R6 over the J2 sweep), then the cross-width tilt (tilt the bar plane to the strap's mean
  tilt, or two flat facets; no twisted sweep). The CAD is still 3.4 R1 points (6.5 R1-aim, 2.9 R4) below its L1; this residual is the
  measured candidate, to be confirmed by re-judging after the fix.
- Repair the inherited cut BOTTOM mesh in the L1 path and re-judge every L1's R7 (stale PASS on two scorecards).
- R16 / R2: the five link-1 body hits at the rim of link 1's O20 J2 ring (Corrections 2).

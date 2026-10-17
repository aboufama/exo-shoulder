# Independent check: user_conecut_knee (the generation-8 winner's full CAD)

Checker (a skeptic), 2026-10-17 22:26-23:10 UTC, inside the 45-min box. What I tested:
- the full CAD as committed at 966caa7 (exo.glb md5 bd4fe8b9…, unchanged since 821f329);
- its builder `pipeline/conformal/param_cad/user_style_conecut.py`;
- the L1 builder it imports, `pipeline/concept_l1/build_conecut_l1.py` (which retargets `build_slipper_l1.py` at the verified
  CCModel, SN_CELL=lead).

**How I ran it.** I changed nothing in the design. The judges ran on a byte copy in the session scratchpad
(`judge/common.design_dir` takes a path), so nothing of mine lands in the design tree except this file. Local only: niced,
OMP_NUM_THREADS=1, at most two of my processes at a time, one worker each (`--jobs 1`). No farm and no GPU: spend $0. The box
ran at load 11-16 from other agents' jobs the whole time.

**My scripts** (session scratchpad `vfy_cc/`, not committed):
- `kin_indep_cc.py` is model-free: it reads only exo.glb, clips.json, workspace.json and build.json.
- `kin_vfy_cc.py` runs the claim's CCModel (`build_conecut_l1.fit()`, SN_CELL=lead, fit gap 12.5 as claimed), posed by the
  model's OWN run state, against the CAD's parts (the gen-7 check, plus picks at the J3 and knee extremes).
- `knee_pin_cc.py`: pin a (member 3) against its MR63ZZ pair (knee link) on every judged frame.
- `stops_cc.py`: each stop dowel turned about its own joint's bearing axis against the slotted part (winding number + exact
  distance), engagement angle at both window ends.

## Verdict

**NOT REFUTED.** R1 81.6 / R1-aim 52.7 / R4 74.1 reproduce to the digit.

- **Re-run judges reproduce the scorecard exactly:**
  - R6 0.0 mm (451 frames x 7002 pairs);
  - R7 PASS (55 custom parts, none missing);
  - R17 PASS, with all 19 dynamics cases identical to the committed file (nominal M_GH 0.126 N.m, 0.57 N, twist 3.99 deg).
- **The kinematics are the verified model's to 0.002 deg.** CAD bearing axes against the judged frames: <= 0.0014 deg and
  0.0002 mm on 2372 frames. K equals the law to 0.0017 deg, the crank angle / |dK| = 1/g, q3' = q3 + phi to 0.001 deg, and
  knee pin a sits on its bearing pair to 0.0003 mm.
- **The J3 hard stop is real as built.** The exported dowel engages the groove ends within 0.02 deg of J3MIN / J3MAX; the
  workspace keeps 0.745 / 2.99 deg of margin and the clips 49.5 / 21.3. The K / J2 stops engage 0.16 deg past (the 0.02 mm
  design clearance), so the slot-end correction is real.
- **The re-proportioned knee does what the claim says:** the knee angle tops out at 107.1 deg on the workspace, 47.7 deg
  under the knee stop (gen 7: 1.6).
- **No loft reaches an exported part.** The B-spline surfaces in the links' STEP files come from the 0.5 mm edge fillets.
- **Every bought part has its catalogue size.** The D1 / D2 / D3 / O3 / O4 items, the knee stop +-0.02, the wear line
  mu <= 0.105 and the J3 dowel / groove fits are on the drawing.
- **Against the CAD's own goals, as disclosed:**
  - the bars ride 0.70-1.63 mm outside the model's straps, all outward, so criterion (1) fails for the bars and holds for
    joints, frames and laws;
  - R1 is -0.39 against the L1;
  - two builder checks (drive skin over all frames, working end) are not on file.
- **No stills exist**, so criterion (5) cannot be checked.

## 1. Posed parts against the verified model

**Model-free (kin_indep_cc.py).** Each joint's axis taken from the CAD's own bearing mesh (PCA of one bearing, rest pose),
compared with the relative rotation of the judged frames: 1035 closing workspace poses + 1337 clip frames = 2372 frames.

| joint (bearing) | axis deviation max | translation residual \|T_rel - (I - R_rel) c\| | angle range on the frames |
|---|---|---|---|
| J1 (MR117) | 0.0009 deg | 0.0001 mm | -127.61..149.18 deg |
| K (MR117) | 0.0014 deg | 0.0001 mm | -46.27..0 deg |
| J2 (MR117) | 0.0012 deg | 0.0001 mm | -101.18..14.21 deg (q2 = -angle) |
| J3 (MR117) | 0.0013 deg | 0.0002 mm | -119.75..111.16 deg (q3' = -angle) |
| crank pivot (683ZZ) | 0.0012 deg | 0.0001 mm | -19.33..0 deg |
| knee pin a (MR63ZZ) | 0.0010 deg | see the knee row below | |

**Slaved and coupled coordinates.**
- K against the build.json law (as a function of q2): max error 0.0017 deg over 2372 frames (law q2 -15.94..7.279, dK
  0..-50.0; the frames reach dK -46.27).
- Crank angle / |dK| = 0.4178-0.4179 on 971 driven frames = 1/g (g 2.3934, the model's law); dwell frames <= 0.196 deg.
- J3: q3' read off the frames equals the stored q3 + knee phi to 0.001 deg. Workspace q3' -111.159..119.752 against the
  window -111.9036 / 122.7417: margins 0.745 / 2.989 deg, no frame outside. Clips -62.40..101.41 (as claimed).
- Knee pin a: the frames' l3 -> l4 angle equals the stored pin_a to 0.0006 deg (constant offset). Posed, the centre of pin a's MR63ZZ pair (knee link) lies 0.0003 mm off pin a's axis (member 3) on all 2372 frames, axes within 0.09 deg (PCA of a grooved pin); the l3 -> l4 motion keeps one fixed point to 0.0003 mm. (The knee link's rest geometry sits 11.8 mm off the pin in the glb's rest frame; the frames carry it onto the pin, so the posed parts are right.)
- Knee angle: workspace 59.27..107.07, clips 59.27..91.81 deg; the physical knee stop at 154.78 is 47.7 deg away (gen 7:
  1.6 deg). The re-proportioned knee does what the claim says.
- The claim's D.ik through `build_conecut_l1.chain` re-derives 12 random closing workspace poses: rotation entries to 5.0e-7,
  translations to 5.0e-5 mm. Slaved law vs the stored frames on 1035 poses (522 with K stretched): 0.0017 deg.

**Model metal against the built solids (kin_vfy_cc.py).** Twelve picks, all taken on the fit bench: arm at the side
[-90,0,75], highest = overhead [45,165,-90], behind the back [-90,30,105], across the body [150,45,-60], drive extreme
[90,120,-90] (dK -46.25), overhead raise peak [30,150,-60], J3 q3' min [-15,75,90] (-98.43) and max [60,165,-90] (116.77),
knee min [-15,60,-15] / max [60,165,-90], low front reach [15,15,30]. Each part is rigid in its member frame, so the numbers
are the same at every pose. "Outside" = distance to the CAD part for samples NOT inside it (winding number).

| model sample set | max outside | p95 | share > 0.5 mm | of those, CAD nearer GH than the model by > 0.25 |
|---|---|---|---|---|
| L1a strap, E boss, arm pad | 0.000 | 0.000 | 0 | - |
| nose ("roller" samples) | 0.003 | 0.002 | 0 | - |
| hub1 / hub3 | 0.143 / 0.100 | 0 | 0 | - |
| L1b strap | 0.702 | 0.581 | 11 % | 0 |
| knee | 0.850 | 0.000 | 1.1 % | 0 |
| flank lug ("horn") | 1.009 | 0.495 | 8.7 % | 0 |
| E strap | 1.330 | 1.038 | 17 % | 0 |
| hub K / hub 2 (stop-slot bands) | 1.419 / 1.420 | 0.90 / 0.88 | 15 / 11 % | 0 |
| L2 strap | 1.627 | 0.845 | 22 % | 0 |
| crank | 7.538 | 7.154 | 34 % | 0 (the model artefact: its arm root inside link 1b's strap, gen 6-7 7.12-7.54) |

- Every miss is OUTWARD: no sample more than 0.5 mm outside has the CAD lying nearer GH than the model by more than 0.25 mm.
  The bars ride high, never nearer the skin. This is what the builder reports.
- The builder's table lists hub K / hub 2 as 0.0; its own build.json per-pose record carries them as "(slot band)" 1.4195 /
  1.4199 and excludes the band from the joint-feature reading. Same number, disclosed in build.json, not in the summary.
- **Criterion (1) holds for frames, joints, slaved laws and the drive tip. It does NOT hold for the bars** (L2 1.63, E 1.33,
  horn 1.01, knee 0.85, L1b 0.70 > 0.5 mm), as the builder discloses. Against gen 7: L2 improved (2.08 -> 1.63), the E strap
  got worse (0.52 -> 1.33, the longer lE 97 strap).
- The build.json flag is now named `joint_features_and_frames_within_0p5` and sits beside
  `model_metal_within_0p5_except_crank: false`, which closes gen-7 finding 4.

## 2. Real size, real component

**Bought parts.** Mesh volumes match the catalogue envelopes (parts_full.json):

| part | built volume | envelope |
|---|---|---|
| MR117-2RS 7x11x3 (8) | 0.169 cm3 | 0.170 |
| 683ZZ 3x7x3 (2) | 0.094 | 0.094 |
| MR63ZZ 3x6x2.5 (4 knee + follower) | 0.053 | 0.053 |
| ISO 8734 2 m6 x 5, ground to 3.90 (J3 stop) | 0.012 | pi x 1^2 x 3.90 = 0.0123 |
| ISO 8734 3 m6 x 10 faced to 9.7 (knee pins) | 0.067 | 0.069 less chamfers |
| ISO 8734 2.5 m6 x 6 (nose) | 0.029 | 0.029 |
| O3 stop dowels faced to 5.65 (K x2, J2) | 0.040 | 0.040 |
| inner-ring spacer O3.1 x O4.5 x 0.175 | 0.0015 | 0.0015 |

- Gen-7 drawing item (a) is closed: the knee pins now read "3 m6 x 10 faced to 9.7" (a stock length).
- The J3 stop dowel is a stock ISO 8734 2 x 5 ground to 3.90; its hole is a real reamed through hole in member 3 (the
  dowel's skin end recessed 0.10), and its groove is cut inside link 2's O20 ring. One solid each, valid.
- The fits table (design.json, 17 entries) carries: J3 dowel press (reamed 2.000 -0.005/0), groove 2.10 +0.02/0 x 1.00
  +0.05/0 with R1.05 ends INSIDE the stop angles, true position 0.02, acceptance bands -112.40..-111.25 / 119.85..123.78 on
  the J3 encoder, rating 1.8 N.m; knee stop face +-0.02; wear line mu <= 0.105.
- D1: one entry for the crank running faces (+-0.02), and it says the 2768-f line is removed. D2: the K-phase band is stated
  as RSS with the linear low end (-0.02, onset +0.73). D3: spacer + O5 land + shim + wave washer are in the CAD and the
  parts list; posed running gaps crank-1a 0.106, crank-2 0.109, crank-1b 0.150 (build.json drive_posed), all > the 0.04
  two-face stack.
- Open drawing items: the wave washer (O3.2 x O6, 0.08 strip, free 0.40) has no supplier part number (disclosed); the O4.5 OD
  of the inner-ring spacer / shims (here and in gen 7's follower and knee stacks) should be checked against the 683ZZ /
  MR63ZZ maker's maximum inner-ring abutment diameter so they cannot rub a shield. I did not have the catalogue table.
- User parts: TOP, MIDDLE, FOREARM CUFF and their hardware are in the glb untouched; only BOTTOM is cut (D8-06).

## 3. No lofts

- The new builder adds no import beyond `build_conecut_l1` (the model plus the gen-7 L1) and `user_style_slipper` (the gen-7
  builder whose 21-module import graph the gen-7 check walked: its only loft sites, `param_build.makeLoft`, are reached only
  from `param_build.main()`, never called on this path).
- Every new solid in `user_style_conecut.py` is a threePointArc sketch extruded (the corrected slot cutter, the J3 groove),
  a revolve of a line profile (the J3 dowel, spacer, shim, wave washer, clip) or a disc; the copied `link1a_body` uses the
  gen-7 `bar_swept` (one section on a line/arc path) and `plate_R`.
- B-spline SURFACES in the STEP files: link 2 168 (gen 7: 141), link 1b 18 (27), BOTTOM 34 (34, the user's own part). On the
  links they come from `US.rounded` (0.5 mm fillets on the 2.5-D profile edges: OCC blends at curved edges and corners),
  not from a loft. Fillets are allowed. Links 1a, member 3, crank, knee link, lobe ring and base carry none.
- The part names state the process where the ruling needs it: link 2 "5-axis / 3+2 machined from solid, drop 68.0 deg at J2
  (<= 70)", link 1a "R2 centre-line bends: 5-axis machined from solid, tighter than the 15 mm bent-bar rule", link 1b
  machined from solid at 59.5 deg.

## 4. Re-run judges (local, current judges, the scorecard's steps)

| Req | claim | re-run | match |
|---|---|---|---|
| R1 | 81.6 % | 81.5559 % (score_design BANDS 10,14, step 3; 38 min at load 13-16) | yes, to the digit |
| R1-aim | 52.7 % | 52.7206 % | yes |
| R4 | 74.1 % | 74.1314 % (Raise overhead at 14 mm); every clip's score identical to score.json / score_14mm.json | yes |
| R6 | 0.0 mm (step 3, 451 frames x 7002 pairs) | 0.0 mm: 451 frames x 7002 ordered pairs, 1 599 578 samples, 0 > 0.15 mm (654 s) | yes |
| R7 | PASS (55 custom, none missing) | all_ok True, 55 custom parts (3 arm-fixed), missing STEP none | yes |
| R16 | 66.7 % | not re-run (stopped to keep the 2-process cap for the stop check; the claim equals the L1's) | - |
| R17 | PASS (M_GH 0.126, F 0.57 N, twist 3.99 deg) | PASS: all 19 per-case rows identical to the committed file (nominal 0.126 N.m / 0.57 N / 3.99 deg, law err 0.12, lift-off 0.0006) | yes |

- M5 forward bound (judge_m5/): I read the three files, not re-run: nominal twist 4.5399 / 4.6660 / 4.7722 deg at mu
  0.087 / 0.105 / 0.12, all under the unrounded 5.0 gate (the claim's 4.540 / 4.666 / 4.772). The thinnest is 0.23 deg.

## 5. Stops as built (stops_cc.py, on the exported meshes)

Each dowel was turned about its own joint's bearing axis against the slotted part in 0.01-deg steps from 1.5 deg inside the
window. "Engage" is the first angle with depth > 2 um.

| stop (dowel -> slotted part) | window (deg) | engage past the window | depth 0.25 / 2 deg past | clearance 1 deg inside |
|---|---|---|---|---|
| K dowel 1 and 2 -> link 1a | -62.849 / 0.000 | 0.16 / 0.16 deg | 0.015 / 0.251 mm | 0.046 mm |
| J2 dowel -> link 1b | -15.94 / 102.068 | 0.16 / 0.16 deg | 0.014-0.015 / 0.251 mm | 0.046-0.047 mm |
| J3 dowel -> link 2 groove | -111.9036 / 122.7417 | 0.02 / 0.02 deg (= my step) | 0.033 / 0.262 mm | 0.047 mm |

- **The builder's stop claim holds.** K and J2 engage the 0.02 mm design clearance past their windows (the builder: 0.14;
  my 0.16 is my 2 um threshold plus a 0.01 step). The J3 groove engages at the stop angle within my step, so it is a real
  hard stop well inside the 0.585 / 0.74 deg held margins. The R1.05 ends really are drawn INSIDE the stop angles.
- Inside the windows every dowel floats 0.044-0.049 mm clear (the 0.05 per-side running clearance).
- I did NOT re-measure the builder's new finding that the shared `USM.arc_slot_cutter` makes the gen-4..7 CADs' stops engage
  about 0.88 deg late. `stops_cc.py` runs on any design dir and can check user_slipper_nose next.

## 6. Stills

- No stills exist (no render; GPU stills need the user's separate yes). The only image is the evolution snapshot
  (pipeline/evolution/user_conecut_knee/snapshot.png): a grey schematic of this design at rest, raise peak and back-pocket
  peak, not a render.
- So criterion (5) cannot be checked: the matte faceless mannequin, no black parts, no part through the skin, the look-audit
  fixes. The glb carries no materials; D8-06 is specified clear anodised, never black.

## Findings for the fix list (before any render)

1. **The bars are not within 0.5 mm of the model's straps** (L2 1.63 / E 1.33 / horn 1.01 / knee 0.85 / L1b 0.70 mm, all
   outward). This is the disclosed cause of R1 -0.39 against the L1. The E strap is new against gen 7 (0.52 -> 1.33, the lE 97
   strap under member 3's upper hull at r 125-134 from GH). The builder's fix route (lower link 2 onto the strap stations at
   r 63-72) addresses the larger half.
2. **The summary table understates hub K / hub 2** (0.0 there, 1.42 in the stop-slot bands); build.json has the band numbers.
   Write them in the summary, as the gen-7 check did.
3. **Check the O4.5 OD of the inner-ring spacer and shims** against the 683ZZ / MR63ZZ maximum inner-ring abutment
   diameter (a shield rub risk), and give the wave washer a supplier part number (disclosed).
4. **Two builder checks are still not on file** for this build (disclosed): the drive-to-skin distance over all 1337 frames
   and the working-end pairs. The drive geometry is gen 7's (1.90 / 1.85 mm there); R2 judged every part against the body.
5. **R16 was not re-run here**, and nothing judges the full CAD with the knee stop's own tolerance; at 47.7 deg of margin the
   knee stop no longer matters.
6. **No stills**: criterion (5) waits for the user's yes on a GPU render.

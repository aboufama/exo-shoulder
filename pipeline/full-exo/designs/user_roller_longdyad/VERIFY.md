# Independent check: user_roller_longdyad (the generation-6 winner's full CAD)

Checker (a skeptic), 2026-10-17 07:39-08:45 UTC (over the 45-min box: the box was shared). Tested: the full CAD as committed at 0b5063a (exo.glb md5 c1578c53,
unchanged since 8e60d0e), its builder `pipeline/conformal/param_cad/user_style_roller.py`, and the L1 builder it imports
(`pipeline/concept_l1/build_roller_l1.py`). I changed nothing in the design: the judged files were backed up first, the
judges re-ran in the tree, and every re-written file came out identical to the committed one, or was restored.
My scripts are in the session scratchpad (`verify/`) and are not committed:
- `kin_indep.py`: reads only exo.glb, clips.json and build.json's law. For each joint, the hub axis fitted to the CAD
  bearings is compared with the relative rotation of the judged frames, on all 1337 frames. Also: K against the law, the
  crank angle against |dK| / g, and the rolling pairs and crank clearances, signed, on every frame.
- `skin_indep.py`: the drive parts, the lobe ring and link 1a, posed by `scene_export.frame_xforms` (the judges' path)
  and measured signed against `body_pose.posed` (the judges' skin).
- `skin_target.py`: the same sweep on the builder's worst frames.
- `ring_wall.py`: lobe-ring wall over its bore, link 2 near hub 2, and the extents of the bought parts.

The shared box sat at load 11-26 the whole time, so judges ran niced with one worker each, at most two at a time.

**Verdict: NOT REFUTED on the numbers.**
- **Every judge I re-ran reproduces exactly:** R1 80.9 / R1-aim 47.5 / R4 72.9, R6 0.0 PASS, R7 FAIL on link 1b only,
  R16 64.2, R17 PASS.
- **The kinematics are the model's to 0.003 deg:** CAD hub axes against the judged frames, K against the law on every
  frame, and the crank angle against |dK| / g.
- **Both rolling pairs stay closed on every judged frame.** The claim checked 42 frames; I checked all of them.
- **The drive's skin minimum reproduces:** 1.836 mm at the lobe ring, Raise overhead 78.
- **The CAD still does not meet its own hard goal on R1** (-1.0 against the L1, disclosed). **No stills exist**, so
  check (5) cannot be done.

Two of the CAD's statements are over-stated, and there are new findings. None of them changes a requirement's status,
but they belong on the fix list before renders:
1. **"Posed parts reproduce the model within 0.5 mm" holds for the joint features only** (section 1). The build's
   `kinematics_exact.all_within_0p5 = true` flag tests joint features and frames, nothing else. The model's metal is
   up to 7.65 mm from the built crank, 2.08 from link 2, 1.86 from the knee link, 1.42 in the K / J2 slot bands, 1.08
   from link 1a and 0.75 from the flank lug, at every pose. The crank, lug, strap and link 1a numbers are disclosed;
   knee, link 2 and slot bands are not. They are of the same size in the gen-4b / gen-5 full CADs: knee 1.19-1.40,
   link 2 1.85-2.41.
2. **No judged clip frame reaches the drive's working end** (section 2). In clips.json, dK only reaches -29.31 deg
   and q2 only -6.33, against the cap at dK -46.25 / q2 -14.20. So "drive skin >= 0.3 mm over all 1337 frames" and the
   R6 PASS say nothing about the crank and roller over the last 17 deg of K. R16's closing poses reach |dK| 42.4
   (body 0, parts 0). The last 4 deg before the cap are checked only by the builder's one bench pose, and that pose
   compares metal against the model, not clearances.
3. **R17 regresses against the L1 at 2x clip speed, and the scorecard does not say so** (section 4). At the same
   rolling friction (mu 0.005 and 0.002), the L1 is free at speed 2 (twist 4.01 / 4.09 deg). The full CAD is not:
   twist 5.16 / 5.22 deg, over the 5-deg rule. The R17 verdict reads only the speed-1 nominal case, so it still
   passes. "Slightly better" (vs_l1.json) is true only at speed 1. This comes from the real parts' mass and inertia
   (243.8 vs 109.2 g).
4. **Link 2 still carries the groove cut for the OLD lobe-ring seat** (section 3). `LOBE_Z = (6.15, 8.75)` is stale:
   the ring was moved up to F2 + 9.79..12.82 on the flat J2 cap, but `build_links` still turns link 2's J2 ring to O18
   over F2 + 6.15..8.95. That groove holds nothing now. The module docstring and the link-2 part name still describe
   the old seat.
5. **The lobe ring's wall over its O20 bore is 0.78 mm at the dwell** (section 3). It is a 17-4PH shell, wire-cut at
   a 14.8-deg taper, and the cap carries the 29-46 N follower force through the bore fit. Add it to the DFM list.
6. **The flank roller pin is named "ISO 2341-B 3 x 8" but drawn 3 x 6** (7.0 mm overall with a 1 mm head). Type B also
   carries a split-pin hole, which a pin pressed into the arm does not need.
7. **The committed R7 file judged an older link 1b STEP** (269 faces; the tree's STEP has 265, replaced at 07:27).
   The verdict is the same.
8. **Pre-existing in the inherited parts, unchanged:**
   - The base description says the handler bracket threads onto the J1 spigot "in place of the dome cap", yet the J1
     dome cap is exported on the same spigot.
   - D8-06 is called "hard-anodised" 7075. On 7075 that finish comes out dark grey to black, which conflicts with the
     "no black parts" look rule if the part is built as named.

## 1. The posed parts and the model

**Frames: exact.** The hub axes are fitted to the CAD bearing meshes in exo.glb (J1 on base, K on l1b, J2 on l2, the
crank's 683ZZ pair on dk). Each is compared with the relative rotation of the judged frames, using clips.json `G` /
`T` through the judges' own parametrisation, on all 1337 frames:

| joint (parent -> child) | axis deviation, max | hub centre moved by the relative motion, max |
|---|---|---|
| J1 (base -> l1a) | 0.0029 deg | 0.00009 mm |
| K (l1a -> l1b) | 0.00235 deg | 0.0001 mm |
| J2 (l1b -> l2) | 0.00266 deg | 0.00011 mm |
| crank pivot (l1b -> dk) | 0.00303 deg | 0.00012 mm |

So every CAD joint turns about its own bearing axis in the judged motion. The CAD and the judged frames cannot drift
apart.

**Slaved coordinate: exact.**
- The judged dK against build.json's law, on 471 driven frames: 0.0021 deg max (json q / dK), and 0.0007 deg from
  my own axis angles. The 866 dwell frames sit at dK 0.
- The crank angle against |dK| / g (g 2.4696): 4e-5 deg max, phi 0..11.87 deg.

This reproduces the L1's "0.0021 deg on 471 driven frames".

**Model metal at the builder's 9 bench poses** (build.json `check`: side, first, middle, highest, 2nd highest, behind
the back, across the body, overhead raise peak, K most open at dK -46.25). I checked the per-part numbers and the
code that makes them (`check_frames`, a copy of USM's).
- **Joint features:** 0.144 mm. **Frames:** 1.2e-4 mm.
- **Other parts:** crank 7.65, link 2 2.08, knee link 1.86, K and J2 slot bands 1.42, link 1a 1.08, horn / lug 0.75,
  E strap 0.52, link 1b 0.71 mm. The values are the same at every pose (rigid parts in exact frames), so this is shape,
  not kinematics.
- **The "4.4 mm below the model" figure for link 1a** comes from `links['link 1a'].vs_model` (6 stations, min -4.43 /
  mean -1.59 mm). The pose check cannot see it: "L1a outside hub zones" has 0 samples, because the whole 26-deg dyad
  lies inside the two hub zones.
- **Verdict on criterion (1):** the kinematics are the verified model's. The metal is not the model's within 0.5 mm
  for the crank, both new links and the knee link. The crank, lug, straps and link 1a are disclosed and argued (the red
  team's real follower; the stack raise). The knee link 1.86 and link 2 2.08 are not mentioned in the claim.

## 2. The drive

**Rolling pairs on every judged frame** (signed; negative = inside; dense surface samples):

| pair | frames | driven (471): min .. max of the per-frame min | dwell (866) | driven frames with a gap > 0.05 / inside < -0.05 |
|---|---|---|---|---|
| flank roller MR63ZZ / link 1a's flank lug | 1337 | -0.015 .. -0.001 mm | -0.012 | 0 / 0 |
| lobe follower MR63ZZ / lobe ring | 1337 | -0.042 .. +0.001 mm | -0.041 .. +0.376 (runs free on the dwell) | 0 / 0 |
| bell crank / link 1a | 451 (every 3rd) | 0.109 .. 0.126 mm | 0.126 | - |
| bell crank / lobe ring | 451 | 0.428 .. 0.942 mm | 0.587 .. 1.003 | - |
| bell crank / link 2 | 451 | 1.737 .. 2.209 mm | 1.734 .. 1.738 | - |

- **Both rolling pairs stay closed on every judged frame, not only on the claim's 42.** The small negatives
  (<= 0.042 mm) are tessellation of the curved faces.
- **Crank / link 1a:** 0.109 mm at Wash opposite shoulder frame 72 (dK -23.7) reproduces the claim's 0.108. It is
  positive, but it is a 0.11 mm running gap between the crank and link 1a, which tolerances must hold.

**Where the judged frames do not reach.**
- **K (dK):** clips.json spans 0 .. -29.31 deg. The law runs to -46.25 (stop B, horn pressure angle 43.0 = PA_MAX)
  and the flank to -48.25.
- **q2:** the clips span -6.33 .. 80.18, inside the window -14.20 .. 102.07.
- **What that leaves:** any frame-based check (R1, R2, R6, the builder's drive skin sweep, my contact and skin
  sweeps) sees the crank and roller only up to phi 11.87 of the 18.73 deg they can reach.
- **The cap region:** the builder's `posed_drive_check` covers it only at the frames of largest |dK| in the clips
  (29.3). The one bench pose at dK -46.25 checks metal against the model, not clearance to skin or to other parts.
  R16's workspace poses are the only judge that can reach it.
- **What R16 covers there:** of its 120 judged poses, those that close reach |dK| 42.38 at most (4 poses past 29.3,
  all at body 0 / parts 0). The poses past the law (dK -48.7..-56.1, q2 < -14.2, beyond the J2 stop) do not close and
  count as chain_does_not_close.
- **Untested:** |dK| 42.4..46.25, the last 4 deg before the transmission cap, at body or part clearance. workspace.json
  holds 115 closing poses with |dK| 29.3..46.25, so a step-1 R16 run would cover it.
- **Rigid parts are always covered:** the lobe ring (on l2) and the flank lug (on l1a) are rigid, so all of their
  metal is in every frame.

**Skin, the drive (independent sweep):**
160 frames: Raise overhead 60-100, Comb hair 88-108, Reach a high shelf 70-80, and every 15th frame of every clip.
The full every-2nd-frame sweep was stopped at 37 min under load. The targets are the builder's per-part worst frames.

| part | min skin distance (mm), where | builder's all-frame sweep |
|---|---|---|
| D9-02 lobe ring | **1.836**, Raise overhead 78 | 1.836, same frame |
| D8-02a link 1a (with the flank lug) | 1.901, Raise overhead 78 | 1.901 |
| D9-01 bell crank | 5.443, Comb hair 92 | 5.435 |
| flank roller pin head | 5.562, Comb hair 105 | 5.562 |
| flank roller MR63ZZ | 6.363, Comb hair 105 | 6.363 |
| crank pivot pin / its clip (not in the builder's sweep) | 10.93 / 17.15 | - |
| follower, its pin and clip, crank bearings | >= 13.7 | same |

0 frames under 0.3 mm. **The drive's 0.3 mm skin rule reproduces (min 1.84 mm)**, within the frames' dK range (see
above).

**The 0.3 mm skin rule against the gen-5 failure mode.** The gen-5 ring entered the skin at its profile end, i.e.
the contact at stop B, at Raise overhead frames 78-83. Here the ring is rigid on l2, so its end is measured in every
frame whatever dK is. The pass therefore does cover the gen-5 failure mode for the ring.

**K beyond the flank, not checked by anything:**
- K's own stop slots allow dK down to -62.85 (`stops.K`). The flank ends at -48.25 and the J2 stop holds the law at
  -46.25.
- K can open past the law only by lift-off. In the nominal dynamics, lift-off happens on 0.18 % of frames. In the
  friction-stress cases (f 0.2-0.5), K departs from the law by 30-52 deg on 46-69 % of frames.
- No check poses link 1a at dK -48..-63 with the crank anywhere in its range. Nobody has looked at the lug's sweep
  there against the crank, link 1b or the K cap.

## 3. Parts: real size, real components, no lofts

**Bought parts, extents from the meshes:**
| part | measured extents (mm) | catalogue |
|---|---|---|
| flank roller, lobe follower: MR63ZZ | 2.5 x 6.0 x 6.0 | 3 x 6 x 2.5: yes |
| crank bearings: 683ZZ (both) | 3.0 x 7.0 x 7.0 | 3 x 7 x 3: yes |
| K bearing: MR117-2RS | 3.0 x 11.0 x 11.0 | 7 x 11 x 3: yes |
| K / J2 stop dowels: ISO 8734 O3 | 3 x 3 x 5.65 | O3 x 6, faced to 5.65 (stated) |
| DIN 6799 clips on the O3 pins | 0.6 x 6.0 x 6.0 | size 2.3: yes |
| iglidur sleeve / washer (pin a) | 1.48 x 5.5 / 0.5 x 8 | GSM-0405-03 faced to 1.48 (stated) / GTM 4 x 8 x 0.5 (stated "confirm the size") |
| flank roller pin "ISO 2341-B 3 x 8" | 5 x 5 x **7.0 overall** (head 1.0, so a 6 mm shank) | **named 3 x 8, drawn 3 x 6** (6 is a catalogue length for d 3, so the name is what is wrong, or it is drawn 2 mm short; type B also has a split-pin hole, which a pin pressed into the arm does not need) |
| crank pivot pin O3 | 3 x 3 x 10.55 | ground pin, length free |

- **Catalogue:** MR63ZZ 3 x 6 x 2.5, 683ZZ 3 x 7 x 3, MR117-2RS 7 x 11 x 3, ISO 2341-B d 3 (head O5 x 1), ISO 8734
  O3 x 6, DIN 6799 2.3 (shaft 3-4) and 3.2 (shaft 4-5, O7.3 x 0.6) all match the catalogues.
- **The crank pivot pin** is drawn overlapping link 1b, which has no bore for it (disclosed). The link 1b STEP
  therefore has no pivot bore, and a drawing taken from it would be wrong.

**Lobe ring and link 2:**
- **Lobe ring band:** F2 + 9.79..12.82, on the J2 cap's O20 skirt. The bore is in metal all round, 360 deg at every
  height.
- **Ring wall over the O20 bore: 0.78 mm min, 0.82 at p5, 4.04 max** (ray march, 1-deg x 9 heights). At the dwell the
  17-4PH ring is a 0.78 mm shell, wire-cut at a 14.8-deg taper. It is buildable, but it belongs on the DFM list: the
  red team's follower force is 29-46 N, carried by the cap through the bore fit.
- **Link 2's J2 ring:** the radius is <= 9.0 mm over F2 + 6.5..9.0 (11.4 below F2 + 6.15). This is the O18 groove,
  turned for the old ring seat (`LOBE_Z = (6.15, 8.75)`), and nothing sits in it now (finding 4). It is metal removed
  for nothing, and an open step under the J2 cap skirt.

**No lofts reachable from the builder.**
- *Static scan:* every repo module the builder loads (25 of them) was scanned for `loft(`, `makeLoft`,
  `ThruSections`, `spline(` and BSpline construction.
- *makeLoft:* only `param_build.strap_solid` and `param_build.main` call it, and neither is called on this path.
- *Spline:* `param_build.cap_shape` builds a spline-dome cap. It is reached through `US.hardware -> PB.joint_parts`,
  and `USM.hubs` drops it (`if " cap " in n: continue`), so it is computed and thrown away, never exported.
- *g2cad's BSpline helpers:* not called on this path.
- *Exported STEPs:* B-spline surfaces appear only in link 1b (27), link 2 (156) and D8-06 (34, the user's BOTTOM).
  The two links are the unchanged 4-strip minarc bars with rounds. user_minarc_bdp (48 / 216) and user_geneva_rod
  (24 / 183) have the same kind, from rounds and sweeps, not lofts. Link 1a, the crank, the lobe ring and the knee
  link have none.

## 4. Judges re-run

**Method.** Same steps as the claim (judge_all fast). R1 and R6 ran in the tree after a backup; both rewrote their
files byte-identical in content.

| req | claim | re-run | |
|---|---|---|---|
| R1 (2-14 mm) | 80.9 % | **80.9 %** (0.80923, every clip identical) | reproduces |
| R1-aim (2-10) | 47.5 % | **47.5 %** (0.47528) | reproduces |
| R4 (Raise overhead) | 72.9 % | **72.9 %** | reproduces |
| R6 | 0.0 mm PASS | **0.0 mm PASS** (451 frames x 5506 pairs, 0 > 0.15 mm; JSON identical but run time) | reproduces |
| R7 | FAIL (link 1b) | **FAIL**: link 1b only, 3 bad faces after STEP re-import; the other 48 custom STEPs pass | reproduces, but see below |
| R17 | PASS | **PASS**: nominal mu 0.005 speed 1, M_GH 0.11 N.m, cuff 0.49 N, twist 3.33 deg, K vs law 0.115 deg, lift-off 0.18 %; chain vs the clips' G 0.000 deg | reproduces exactly (every case's numbers identical; the JSON differs only in run time, jobs and clip order) |
| R16 | 64.2 % | **64.2 %** (120 poses, step 12): chain_does_not_close 35.8 %, body 0 %, parts 0 %; evaluator agreement 100 % | reproduces (JSON identical but run time) |

**R7 is judged on an older STEP.**
- The committed part_validity.json (06:57) read a link 1b STEP with 269 faces and 3.117 cm3. The STEP in the tree
  was replaced at 07:27 (a WIP sweep, 456da59) and has 265 faces and 3.120 cm3, presumably from the export experiments
  the claim lists.
- The verdict is the same either way (3 bad faces), and every other row is identical. I restored the committed file.
- **Not watertight on the judge's tessellation:** the J1 / J3 caps, link 1a, link 2, D8-06 and the cuff. That is
  reported, not graded.

**R1 against the L1.** The full CAD loses 1.0 against its L1 (81.9), so the hard goal "loses nothing on R1" is not
met. The claim says so, and attributes it by group swap to the lobe ring (l2, +0.64) and the crank (dk, +0.31). I did
not re-run the swap.

**R17 at 2x speed** (the committed dynamics.json and my re-run agree):

| case | L1 twist / free | full CAD twist / free |
|---|---|---|
| mu 0.005, speed 1 (nominal) | 4.07 / yes | 3.33 / yes |
| mu 0.005, speed 2 | 4.09 / yes | **5.16 / NO** |
| mu 0.002, speed 2 | 4.01 / yes | **5.22 / NO** |

## 5. Stills

**None exist.** The workflow held the paid stills for the user's approval (CLAUDE.md: a cheap motion preview first),
and no motion preview was made either. Item (5) cannot be checked. The generation therefore does not yet end in "a
full CAD + render of its winner". `pipeline/evolution/user_roller_longdyad/snapshot.png` is the evolution schematic,
not a render.

## 6. Reproducibility notes

- **Untracked input.** The build read `pipeline/full-exo/designs/band_r20_n3_s1414_4/clips.json`, which is
  git-ignored and was re-created by hand from param_r20 (dated 05:57). `frames.load()` uses it for the arm-side frames.
  A fresh clone cannot rebuild this CAD without it.
- **Ear search not run.** It needs `.cache/maps_s1.pt`, which is missing here. "No ears" is therefore untested, not
  measured: the same outcome as gen 5, but for a different reason.

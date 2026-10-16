# Independent verification: user_osn_k4216 (generation-2 winner, full CAD in the user's style + stills)

Verifier, 2026-10-16 05:23-06:15 UTC. The claim under test: the builder's report (commits c9b8f01, e1a3c87) and the
stills in renders/2026-10-16_userstyle_osn_k4216. Everything below was re-measured from the files in this directory
with my own scripts (kept in the session scratchpad, not in the repo). Nothing in the design was changed.

**Verdict: NOT REFUTED.** Checks 1, 2, 3 and 5 hold on the points that matter. The kinematics are the verified
model's to the digit, the guides and hub stacks are real catalogue parts at their real size, and the builder has no
loft or fitted surface. Check 4 is only partly verified: part validity and R3 reproduce exactly, but R1, R2, R4 and R6
did not finish on the overloaded box. The stills show this CAD on a matte,
faceless mannequin. The claim also understates or leaves out some things; they are listed under "Corrections" below.
None of them changes a requirement's status.

## 1. Built parts posed by clips.json vs the verified model

Method: `build_osn_l1.fit((60,160), 4216)` (gap **32.61**, reproduced). I posed exo.glb with the judges' own path,
`scene_export.posed_scene` (clip frames) or `scene_export.frame_xforms` (workspace.json poses). I then sampled every
metal group of the verified model (`M.rigid` + `M.link_pts`) at the same pose with `L1B.chain` + `M.world`. The
distance is libigl signed distance to the union of the posed built parts (> 0 = model metal outside the built metal).

I checked 7 poses, all followed, all closing, with closure residual <= 0.0002 deg:
- Comb hair peak (78, 143, -67)
- Reach a high shelf peak (82, 132, -82)
- Raise overhead, highest followed frame (30, 66, -43)
- Wash opposite shoulder peak (140, 60, -50)
- Reach back pocket, most extended (-80, 39, 101): behind the back
- Workspace (75, 165, -75): overhead
- Workspace (45, 165, -90): overhead, the bench's highest

| group | max outside built metal, every pose | note |
|---|---|---|
| clips.json G / T vs the model chain | **0.0 / 0.0 mm** | the transforms are the model's exactly |
| hub 1 / hub 2 / hub 3 | 0.144 / 0.143 / 0.144 mm | cap domes and rounds |
| neck (member 3) | 0.170 mm | |
| bridge | 0.000 mm | |
| link 1 strap (L1) | 4.0 mm | the bar sits above the L1 strap: a deliberate shape change, as claimed |
| link 2 strap (L2) | 10.2 mm | the same, at J3: the 35 deg ramp vs the model's 60 deg, as claimed |
| stage: model 'rail' / 'carA' / 'strip' samples | **5.2 / 7.1 / 2.5 mm** | **not reported in the claim** (see C1) |

Every number is the same at all 7 poses to 0.005 mm. The differences are shape differences, not kinematic ones.
**Check 1 holds.**

Stage, measured directly:
- **Real stage inside the model's envelope.** I ran a box test of each posed built guide part against the model's stage
  boxes (arm-fixed block 20 x 20 x 4, carriage A 20 x 35 x 4 with the rail strip 32.6 x 8, carriage B 20 x 20 x 4). The
  real 8 x 12 RSR3M stage is smaller and lies inside them, with these exceptions:
  - Carriage A: -1.0 mm (inside).
  - Carriage B: 0.2 mm out.
  - Along block: 0.24-0.5 mm out.
  - Across rail top: 0.6 mm out.
  - Along rail ends: **1.6 mm** out, toward the skin (see C1).
- **Guide engagement.** I took the extreme slide frames of all clips and all 903 feasible workspace poses: Comb hair 62,
  Reach back pocket 24, and workspace poses 289 and 1349 (along d = -6.03 of +-6.3). At each one the blocks stay fully on
  their rails, with at least **1.27 mm** margin along and **1.49 mm** across.

## 2. Real components at their real size

Measured as oriented boxes of the exo.glb parts. Masses use the claimed densities.
- **Bearings:** MR117-2RS, 3 x 11 OD. A real ISO miniature bearing (7 x 11 x 3).
- **Hub stack:**
  - Cap O20 x 3.45, spacers 0.6, nut 0.9.
  - Each stack is 4.89 g: 2 x 1.32 + 2.01 + spacers and nut.
- **Rails:** 3 x 2.6 x **26.6** and 3 x 2.6 x **29.0**. These equal travel + block + 2 (12.6 + 12 + 2, 15 + 12 + 2).
- **Blocks:** 8 x 12 x 3 body on H 4 with H1 1. This is the THK RSR3M catalogue envelope in tools/hardware_catalogue.json.
- **Stack:** 1.5 base, 1.5-4.5 block, 2.9-5.5 inverted rail, 5.5-6.5 adapter, 6.5-9.1 across rail, 7.5-10.5 carriage B.
  Total **10.5 mm**, consistent with H 4 / H1 1.
- **Carriage A:** 1.0 mm plate, 22.3 x 24.1.
- **Custom-part masses:** reproduce the claim to 0.1 g.
  - link 1: 3145.6 mm3, 13.9 g
  - link 2: 4514.1 mm3, 20.0 g
  - member 3: 2638.6 mm3, 11.7 g
  - base: 3730.6 mm3, 16.5 g
  - BOTTOM + stage: 26686.9 mm3 x 2.81, 75.0 g
  - cuff: 28304.6 mm3 x 2.68, 75.9 g
- **Every joint maps to a component.** The 3 pins are bearing pairs. The 2 passive translations are 2 catalogue miniature
  guides, crossed and shown to fit at 10.5 mm. There is no radial slide.

**Check 2 holds.** Small notes are in C4 and C5.

## 3. No lofts or fitted surfaces

I grepped the builder and every module it calls: user_style_osn.py, user_style.py, param_build.py (only revolved,
axis_frame, joint_parts, cap_shape, Envelope, disc_face), sketch2d.py, build_osn_l1.py and band_cad/arm_end.py. I
searched for loft, makeLoft, ThruSections, interpPlate, MakeFilling, PointsToBSplineSurface, spline and bezier.
- **param_build.py's lofts are never called.** `strap_solid` / makeLoft (l.117-123) and the neck loft in `main()` (l.194)
  are not reached from this builder.
- **arm_end's conformal G2 cuff shell (fitted) is filtered out.** user_style_osn.py l.372 skips "UPPER ARM CUFF" and its
  screws, and the cuff is rebuilt by `US.upper_cuff` from one line/arc U sketch.
- **The bars** are `bar_swept`: one constant rounded-rectangle section swept along a line / tangent-arc wire, with the
  binormal fixed to the sketch plane (no twist).
- **The pads, rings, member 3, base tab, plate and tongue** are extrudes and revolves of line/arc sketches.

**Check 3 holds.** The one non-arc curve is noted in C6.

## 4. Part validity and the cheapest judges, re-run

I re-ran these locally, niced, on a scratch copy of this directory that has since been deleted. The box was at load
31-39 on 4 cores from other agents the whole time, so only the cheap rows finished inside the time box:

| row | scorecard | re-run | within 2 points |
|---|---|---|---|
| R7 part_validity | all_ok True, 29 parts | **all_ok True, 29 parts; the part_validity.json is identical** | yes |
| R3 follow | 90.9 % | **90.9 %** (410 of 451 frames at step 3, from clips.json) | yes |
| R4 overhead | 24.6 % | follow factor **0.4262** reproduced; in-band part not re-run | partly |
| R1 / R1-aim / R4 in-band | 49.0 / 22.3 % | **not finished** (score_design stopped after 29 min at ~27 % of one core) | - |
| R6 | 0.85 mm | **not finished** (part_contact --step 3 stopped after 24 min at ~7 % CPU per worker; a targeted base-tab vs link-1 winding-number re-measure did not finish either) | - |
| R2 (ours, attributable) | 7.55 mm | **not re-run** (queued behind R1) | - |

I also checked that the judges' own output files in judge/ and score*.json agree with the scorecard. This is
consistency, not a re-measurement:
- score_14mm.json: in_band 0.4903, so R1 = 49.0.
- score.json: 0.2234, so R1-aim = 22.3.
- Raise overhead clip score: 0.2457, so R4 = 24.6.
- part_contact.json: 0.85 mm, base tab in link 1, step 1, 1337 frames.
- body_contact.json: attributable ours 7.55 mm (upper cuff), user's 24.0 mm (FOREARM CUFF).

**Check 4 is only partly verified.** R7 and R3 are reproduced exactly. R1, R2, R4 and R6 still need an independent
re-run on the farm: `tools/cloud_run.py judge user_osn_k4216 fast`. Nothing I measured contradicts them.

## 5. The stills (all 12 looked at)

- **Mannequin.** Matte charcoal black, faceless smooth head, and the muscles read: back, deltoid and trapezius in
  rest_back_lateral. It has no gloss highlights, so the 10-15 glossy look is fixed. render_stills.py sets base 0.028,
  rough 0.9, spec 0.2, no coat.
- **No black exo parts.** The parts are bead-blasted metal (alu shader roughness 0.38 + blast bump), polished screws
  and ground-steel guides and bearings.
- **This CAD is the one shown.**
  - shots.json names `pipeline/full-exo/designs/user_osn_k4216`.
  - exo.glb (04:17) predates the renders (05:20).
  - The geometry in the images is this design: the 2-hole scapula tab, the three O20 hubs, the 8 x 3 bent bars, the
    ramped member 3, the plus-shaped carriage A on crossed miniature rails, BOTTOM with the stage, and the U cuff.
- **A part goes through the body in one still: `hero_shelf_chain.jpg`.** The base-tab terminal visibly pierces the
  skin. The README and the claim disclose this (1.64 mm, the same as the judges at shelf frame 78). It is a real design
  fault, not a render error.
- **The overhead hero is workspace pose 608 (30, 150, -60), not a clip frame.** It is disclosed in the README.
  workspace.json confirms closes = True, eval_feasible = True, slides (-11.16, -3.94) = d (-5.5, -5.5) from mid travel,
  within +-6.3 / +-7.5.
- **Cosmetic artefacts:**
  - Star-shaped shading on the hub end faces in parts_cuff_stage, hero_overhead_chain and rest_lateral_chain.
  - Crumpled shading on the 3 mm guide parts in parts_cuff_stage.
  - These are tessellation and normal artefacts, not geometry.
  - The big flat parts (cuffs, BOTTOM) read more polished than bead-blasted under the softboxes.

**Check 5 holds.**

## Corrections to the claim (none flips a requirement)

- **C1. The kinematic check left out the stage.**
  - `check` / `check_clips` compare only hub 1-3, neck and bridge. The verified model's stage samples ('rail', 'carA',
    'strip') lie up to 5.2 / 7.1 / 2.5 mm outside the built metal at every pose.
  - The cause is that the model's stage is a generic 20 x 20 x 4 carriage stack, 13.5 mm tall. The build uses the real
    8 x 12 RSR3M stack, 10.5 mm tall.
  - So the built stage is smaller and 3 mm lower than the verified model's. Only the inverted along rail's overhanging
    ends sit 1.6 mm skinward of the model's strip layer.
  - "Kinematics = the verified model's" is right. "Metal within 0.17 mm" is right only for the groups it lists. The
    stage is a further shape change and should be reported next to the link shape change.
- **C2. "Raise overhead peak" and "Raise overhead middle" are the same pose, (30, 65.9, -42.9).**
  - They are frames 36 and 144, before and after the hold.
  - Neither is overhead. The design holds every Raise overhead frame from elevation 66 deg to the top.
  - Overhead coverage in the check comes from Comb hair 143, shelf 132 and the bench poses. I added two workspace poses
    at elevation 165.
- **C3. R6: the claim says "Wave frame 72 (6 frames)".** judge/part_contact.json (step 1) says 22 frames from Wave 71,
  at a constant 0.85 mm: the chain is held there.
- **C4. "M1.6 x 2.5 ISO 10642" does not exist.** ISO 10642 starts at M3. An M1.6 countersunk screw is ISO 7046-1 /
  DIN 965 (cross recess), or a hex-socket special. The part is real; the designation is wrong.
- **C5. The modelled RSR3M block is a solid 1.66 g; the catalogue says 1.1 g.** This is conservative. The rails are 7 %
  light against 5.5 g/100 mm, which is negligible.
- **C6. The O20 G2 dome cap's revolve profile has one 2-point tangent spline** (param_build.cap_shape l.67). It is not
  a loft or a fitted surface. It is the v5 hub hardware the user's earlier build already carries. Strictly, it is not
  line/arc.
- **C7. Open meshes in exo.glb.** Link 2 is open (claimed). So are both rails, which the judges see as non-manifold, and
  the caps, BOTTOM and cuff (watertight False in the STEP tessellation). R7 is unaffected because it runs on STEP. The
  mesh-based judges (R17's convex-hull fallback) are affected, as the claim says.

## Next

- Build the gen-3 winner (pin knee k4598) through this builder with fixes 1-3 from the claim.
- Have the builder's `check_clips` also sample the model's stage groups and report them as a shape change.
- Close meshes in the judges' units (metres, float32) before export.

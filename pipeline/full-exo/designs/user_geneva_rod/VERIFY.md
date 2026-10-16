# Independent check: user_geneva_rod (the generation-5 winner's full CAD) and its 22 stills

Checker (a skeptic), 2026-10-16 ~21:40-22:20 UTC. Tested: the full CAD at commit cae6a6e (exo.glb of 20:53, unchanged
since), its builder `pipeline/conformal/param_cad/user_style_geneva.py`, the L1 builder it imports
(`pipeline/concept_l1/build_geneva_l1.py`), and the stills in `renders/2026-10-16_userstyle_geneva_rod/` (commit
ef88ad4). I changed nothing in the design. My scripts are in the session scratchpad `vfy_g5/` and are not committed:
- `kin_check.py`: CAD meshes posed by the verified model's OWN member transforms (no builder chain) against the model
  metal; the judged frame path against the model; K against the lobe law; roller-on-lobe contact in every judged frame;
  CAD-to-skin clearance at the check poses.
- `fdiag.py`: the model's frames against the judged frame path, group by group.
- `lobeskin.py`: signed skin distance of every chain part over the judged clip frames (every 2nd frame).
- R1 re-run on a scratch copy of the design dir (`score_design.py <copy> 3`, BANDS=10,14), so no judged file in the
  tree was overwritten; R7 run in the tree and the committed file restored (the re-run is byte-identical anyway).

**Verdict: NOT REFUTED on what the CAD claims** - the kinematics are the verified model's, K follows the lobe law in
every judged frame, the drive's roller really sits on the lobe in every driven frame, and every judged number I re-ran
reproduces. **Five corrections / new findings** below change no requirement's status but must be fixed before this
CAD is called buildable or re-rendered:
1. **The igubal parts are not at their catalogue size, and at real size they do not fit** (section 2).
2. **The DIN 6799 clips on the O3 drive pins have no groove and a 0.5-0.6 mm land** (section 2).
3. **The lobe ring is more metal than the verified model wore, and it enters the judge skin at the overhead peak**
   (sections 1 and 4).
4. **The R1-loss cause "arm-side parts scored as H" is wrong:** H scores no samples at all (section 4).
5. **build.json flags link 1a invalid at build time,** so the "valid before tessellation" statement does not hold for
   the solid the build recorded (section 4).

## 1. The posed parts reproduce the verified model

The fit is the L1's `build_geneva_l1.fit()` (the verifier's CorrModel + BEST on Bench(60,160) fast). My re-run gives
the claim's numbers: near-touch gap 16.73, tr 88.137, knee centre m (-15.315, 2.409), hub levels f 49.866 / 60.236 /
80.928, fK 58.019; law kK 3.1796, onset q2hi -5.011 deg, t_end 16.8 deg, dK at stop B 53.417 deg, pressure angle 41.37
deg.

Nine bench poses (taken), each posed two ways: (a) the model's OWN member transforms at its bench state, (b) the judges'
path (`MIN.chain` -> `frame_dict` -> `scene_export.frame_xforms`).

| pose (plane, elev, axial) | dK model / law (deg) | q2 (deg) | (a) vs (b), chain groups | nearest skin, our chain (CAD posed by (a)) |
|---|---|---|---|---|
| arm at side (-90, 0, 75) | 0 / 0 | -3.64 | 5.7e-5 mm | l3 3.19 mm |
| highest taken (45, 165, -90) | 0 / 0 | 9.06 | 5.0e-5 mm | l1a 1.74 mm |
| **overhead raise peak (30, 150, -60)** | 0 / 0 | 75.52 | 7.5e-5 mm | **l2 0.23 mm INSIDE (16 samples)**, l1a 1.13, l1b 2.75 |
| behind the back (-90, 30, 105) | 5.567 / 5.567 | -6.76 | 4.5e-5 mm | l2 2.60 mm |
| across the body (150, 45, -60) | 12.068 / 12.069 | -8.81 | 5.1e-5 mm | l1a 6.47 mm |
| **K most driven (75, 30, -135)** | **42.580 / 42.581** | -18.40 | 5.0e-5 mm | l3 1.89 mm |
| **K driven, 2nd (105, 120, -90)** | **42.188 / 42.188** | -18.28 | 5.7e-5 mm | l1b 2.08 mm |
| K half driven (30, 0, -75) | 10.584 / 10.584 | -8.34 | 5.9e-5 mm | l3 2.72 mm |

(The base frame is the scapula rotation by construction; my first pass compared it with identity, a bug in my script,
not in the CAD.)

**Model metal against the CAD posed by the model's own transforms** (identical at all nine poses to 0.001 mm):

| model metal | how far it sits outside the CAD |
|---|---|
| hub discs J1 / K / J2 / J3 | 0.144 / 0 / 0 / 0 mm |
| E strap, E boss, arm pad | 0.178 / 0 / 0 mm |
| hub K / hub 2 discs in the stop-slot band | 1.42 mm (the real slot void) |
| knee-link plate | 1.194 mm at the corners (less metal than the model, as gen 4's 1.40) |
| rocker / rod / rod-end heads | 2.17 / 10.59 / 7.31 mm (deliberate: the bell crank replaces the model's immovable post, red-team finding 1) |

**Bars against the model straps,** outside the hub zones (unsigned distance to the bar's own group):

| link | samples | max | mean | share within 0.5 mm | samples inside the bar |
|---|---|---|---|---|---|
| L1a | 10 | 0.17 mm | 0.10 mm | 100 % | 2 |
| L1b | 28 | 0.57 mm | 0.30 mm | 86 % | 0 |
| L2 | 128 | 0.82 mm | 0.30 mm | 77 % | 0 |

In the hub zones the bars sit up to 1.85 mm over the model strap (link 2), the hub-zone lift the claim states.

**K in the CAD equals the lobe law, everywhere it is judged.** Read off the judged frames (K from l1a / l1b, q2 from
l1b / l2):

| file | frames | K driven | max abs(K - law(q2)) | max dK | K off stop A when not driven |
|---|---|---|---|---|---|
| clips.json | 1337 | 213 | 0.001 deg | 16.2 deg | 0.000 deg |
| workspace.json | 1432 | 420 | 0.0009 deg | 44.5 deg | 0.024 deg |

**The drive really carries that law.** In every one of those frames I posed the MR63ZZ roller (group dk) and the lobe
ring (group l2) from the judged frames and measured the roller centre to the lobe surface: **2.999-3.000 mm on every
driven frame** (the roller radius is 3.0), and 2.998-3.007 mm in the dwell. So the bell crank's per-frame RSSR posing
puts the roller on the lobe exactly, and K = law(q2) is what the built cam and rod would produce. Nothing lifts off
and nothing interpenetrates beyond 0.002 mm.

**Extra metal at the lobe (correction 3).** The verified model's lobe runs r 9 -> 11.32 mm (1.32 mm past the O20 skirt)
and dwells inside the skirt. The CAD's lobe, solved for the real roller follower, runs r 10.74 -> 12.87 mm (2.87 mm
past the skirt) and dwells at r 10.1. That is up to 1.55 mm more metal than the metal the verified score wore, on the
part of hub 2 that faces the raised deltoid. At the overhead peak bench pose link 2's group is 0.23 mm inside the
judge skin. The model alone has 0.039 mm of clearance there (gen 4 measured the same hub-2 pinch at 0.038 mm). See
section 4 for which part does it on the clips.

## 2. Every part has real size and a real component

| part | component | real? | finding |
|---|---|---|---|
| hubs J1 / K / J2 / J3 | v5 O20 stack, MR117-2RS pair, M7 ring nut, M18 x 0.5 caps | yes | K cap flat-crowned (F+18.25), horn-hub counterbore, O5.6 arbor bore |
| K clock spring | 0.3 x 5 1.4310 +C1900, 145.6 mm, 9 half-turns | yes | as gen 4 (checked there: rate 0.0147 N.m/rad, 1184 MPa at stop B) |
| lobe ring D9-01 | 17-4PH H900, wire-EDM, 8 three-point arcs | machinable | O1 key dowel not modelled (stated) |
| follower | MR63ZZ 3 x 6 x 2.5 on an O3 h6 pin pressed in the follower arm | yes | **nothing retains the roller below** (the pin ends at the roller's lower face): press-fit the inner race or add a head |
| bell crank D9-02 | Ti tube O10 on 2x MR85ZZ (5 x 8 x 2.5) on an O5 17-4PH post | yes | **no clip or shoulder over the post top**, though bearing 2 is "wave-washer preloaded": the preload needs a reaction |
| rod D9-03 | Ti dog-bone, centres 36.94, O13 x 4 eyes | machinable | see igubal |
| rod ends | igus igubal KGLM-03 class: housing O10, ball on the pin | **not at real size** | **correction 1** below |
| horn D9-04 / D9-05 | Ti hub O9.4 x 1.2 (DD bore) + plate O13 x 1.4, 2x M1.6 ISO 7046 in +-5 deg slots | yes | the M1.6 thread in the 1.2 mm hub has 1.2 mm of engagement (0.75 d): marginal, state it |
| K stops | opposed O3 x 6 ISO 8734 dowels, 0 .. -53.64 deg | yes | the law ends at 53.42, so stop B sits 0.22 deg past it |
| J2 stop | one O3 dowel, -21.81 .. 93.40 deg, push limit 4.3 N.m | yes | as gen 4b |
| pins a / b | IGLIDUR-PIN stacks, GSM-0405-03 sleeves, DIN 6799-3.2 on a 1.0 mm land | yes | as gen 3 / 4 |
| drive pins (horn, crank) | O3 h6 + DIN 6799 RS 2.3 | clip is real | **correction 2** below |

**Correction 1: the igubal parts are not at catalogue size, and at catalogue size they do not fit.** The drive red team's
build spec (docs/research/geneva_rod_drive_redteam.md, finding 3 and section 5) is two igus igubal KGLM-03 (3 bore, O10,
**6 wide**) pressed into **O13 x 6** eyes. The CAD builds O13 x **4** eyes (`EYE_H 4.0`) and **3.9 mm** balls. The CAD
agent lists "balls 4 mm wide against 6 mm" under "not modelled", but not what it costs:
- at the horn, the eye's lower face is 0.5 mm over the horn plate (build.json `eye_B_bottom_over_plate_mm` 0.5), so a
  6 mm ball on the same rod line sits 0.5 mm into the plate;
- at the crank, the tube top was lowered to 0.5 mm under the eye, so a 6 mm ball sits 0.5 mm into the bell crank;
- both pin clips sit 0.7 mm past the 4 mm eye face, inside a 6 mm ball's face.
So the rod line has to move by >= 0.5-1 mm at both ends. The rod-to-K-cap (1.18 mm) and rod-to-horn-plate (0.17 mm)
clearances, the 29 deg crank-pin tilt and the RSSR closure then have to be re-solved and re-judged. The rule is that
every joint carries its real envelope, and this one does not yet.

**Correction 2: drive-pin clips without a groove, on too short a land.** The crank pin ends 3.8 mm from the eye centre
and its clip sits at 2.7-3.3, a **0.5 mm** land. The horn pin ends at F+26.15 and its clip at about F+24.95-25.55, a
**0.6 mm** land. Neither pin has the clip groove cut: the clip ring overlaps the pin solid. The knee pins in this same
CAD use the project's DIN 6799 rule (groove + 1.0 mm land), and the drive pins should too.

## 3. No lofts

**Statically.** `user_style_geneva.py` calls no loft, spline, ThruSections, interpPlate or parametric surface. Its
new parts are line / threePointArc sketches, extrudes and revolves (lobe ring: 8 three-point arcs + lines, extruded;
crank, rod, horn: discs, stadia, revolves). `drive.py` (the red team's) is numeric only. From `param_build` it uses
`revolved`, `axis_frame`, `BAND`, `Envelope`. The one spline path is the same as gen 4's: `US.hardware` ->
`param_build.joint_parts` -> `cap_shape` (G2 dome `.spline`). `hubs_geneva` drops that cap (`if " cap " in n:
continue`) and builds the torispherical or flat line / arc caps instead, so no exported part carries it.

**Dynamically: not re-run.** This builder took about 7 h with OCC crashes and a hang, which does not fit a 45-min box.
The gen-4 trapped rebuild (VERIFY.md of user_minarc_bdp) found 0 loft calls and 4 discarded spline calls on exactly
this imported path.

## 4. The judges re-run

| requirement | claimed | re-run | how |
|---|---|---|---|
| R1 (2-14 mm) | 80.3 % | **80.295 %** (score_14mm.json byte-identical) | local, step 3, scratch copy |
| R1-aim (2-10 mm) | 49.8 % | **49.797 %** (score.json byte-identical) | same run |
| R4 (Raise overhead, 14 mm) | 73.8 % | **73.83 %** (min gap 0.2 mm: see correction 3) | same run |
| R6 | 0.0 mm | not re-run (see below); committed output read: 1337 frames x 7138 pairs incl. dk / dr, max depth 0.0 | - |
| R16 | 72.6 % | **72.63 %**, per-pose results identical to the committed file (358 poses; does not close 26.5 %, body 0.8 %, parts 0.0 %) | local, step 4, scratch copy |
| R7 | FAIL (link 1a) | **FAIL, byte-identical**: 25_D8-02a_link_1a.step valid False, 2 bad faces of 132, not watertight; every other part one valid solid; coverage 59 custom, none missing | local OCC |
| R17 | NOT RUN (KeyError 'l1') | **reproduced**: the general chain refuses group 'dk' ("no place in the serial chain rule base, l<k>[a-z], cuff"), falls back to the spherical judge, which stops on KeyError 'l1' | local |

The farm batch for R1 / R6 / R16 died after its upload step: the client was gone, and the jobs, if they were
submitted, are abandoned. I did not resubmit, because of the $0.6 cap. That cost at most about $0.04. R1 and R16 then
ran locally.

**Correction 4: H scores nothing.** score_design.py on this design scores 8 groups (base, l1a, l1b, l2, l3, l4, dk, dr).
The arm-fixed group H contributes **0 samples**, because none of its metal is within 110 mm of GH. The committed
score_14mm.json says the same (`groups_scored` 8). So the CAD agent's candidate cause for the R1 loss against the L1,
"arm-side parts (cuff, D8-06) scored as H metal within 110 mm", is excluded.

**Which part enters the skin (correction 3, measured).** `lobeskin2.py` takes the signed distance of every chain part
(groups l1a, l1b, l2, l3, l4, dk, dr) to the judge skin. It covers every frame of Raise overhead and every 3rd frame of
Comb hair and Reach a high shelf.
- **Only the D9-01 lobe ring is inside the skin: -0.233 mm at Raise overhead frame 102.**
- Next nearest: link 1a +1.13 mm, the J2 cap +2.25, link 1b +2.36, the link 2 bar +2.52 mm.
- The drive groups stay clear: pushrod +5.07, crank igubal housing +6.57 mm.
So the Raise-overhead minimum gap dropping from 1.1 mm (L1) to 0.24 mm (full CAD) is the lobe ring's extra radius. It
is metal about 0.23 mm into the skin, not 0.24 mm of clearance: the judge's min_gap is unsigned. That costs at most
the frames where the ring is under 2 mm. It does not explain the -0.8 R1 points across all clips; the dk / dr groups
and the link-2 strip lift are the remaining candidates, still unattributed.

**Correction 5: R7 link 1a.** build.json's own `invalid_or_multi_solid` lists link 1a at build time. The claim that "the
same STEP is valid when checked before tessellation" therefore does not describe the solid the build recorded. Either
way R7 fails on it.

## 5. The stills (all 22 looked at)

I viewed every image on 2 x 2 contact sheets at 1200 x 675, and zoomed into the drive in hero_overhead_chain and
parts_drive_oblique.

| check | result |
|---|---|
| mannequin matte black, faceless | yes in all 22: no gloss, a blank head. Back and deltoid muscles read faintly (rest_back_*, parts_four_hubs_posterior) |
| no black parts | parts are Ti-grey blasted metal, igubal housings and knee crescents iglidur orange, bearings steel. **Two near-black readings.** (a) The polished pin heads and clips in the igubal eyes mirror the black body and read black (hero_overhead_chain, parts_drive_oblique, kopen_drive_closeup). (b) The J2 cap reads dark grey in the armpit shadow (hero_overhead_chain). Neither is a black material. A satin finish on the pin heads, or a fill from below, fixes them |
| no part through the skin | none visible. The lobe ring's 0.23 mm entry at the overhead peak (section 1) is hidden under the J2 cap in every overhead framing. The display rig's own tears and crumples show in kopen_back, hero_overhead_chain, hero_shelf_mid and hero_shelf_chain (README row 6) |
| the design shown is this CAD | yes. shots.json names designs/user_geneva_rod, the scenes were built at 21:35 from the exo.glb of 20:53 (unchanged since), and the horn, pushrod, bell crank with its roller, the lobe sliver, the flat K cap and the knee all match the parts list |
| look-audit fixes applied | Base-contrast look: the caps show gradients and rims, not blown-out white discs. Muscles read. Macros are sharp, with no foreground smear. Bodyless lobe side views exist. **Still visible, as the README says:** strip facets on link 2 (parts_drive_lobe_macro, kopen_drive_lobe_macro), the big flat pad / cuff slabs in every hero, featureless caps, the lobe hard to see |

The README's caveat stands: these stills show a CAD that loses R1 to its L1 and fails R7. They are fine as a
progress view. They should not go out as the generation-5 winner image until corrections 1-3 and R7 are fixed.

## What to do next (in order)

1. Re-lay the drive at the real KGLM-03 width (6 mm balls, O13 x 6 eyes). Raise the rod line, re-solve the RSSR and the
   crank-pin tilt, and re-check the rod-to-cap and rod-to-plate clearances.
2. Bring the lobe's skin side in: trim the dwell / return arc that faces the deltoid, or move the band up the hub. Then
   re-judge R1 / R4 at the overhead peak.
3. Cut DIN 6799 grooves on the horn and crank pins, with a 1.0 mm land. Retain the roller and the bell crank (clip or
   shoulder on the post top).
4. Fix link 1a's K-pad faces (R7).
5. Add the coupling term to judge/dynamics.py for a slaved K and the dk / dr groups (R17, R11).
6. Re-shoot with look 2, with the polished pin heads satin.

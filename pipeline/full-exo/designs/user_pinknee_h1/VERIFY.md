# Independent verification: user_pinknee_h1 (generation-3 winner, polished H1, full CAD in the user's style + stills)

Verifier, 2026-10-16 10:26-10:55 UTC. What I tested:
- the builder's report (commits 765c477, 7f748f7, and the parent's WIP sweeps 80c6ef1, 0195692);
- the stills in renders/2026-10-16_userstyle_pinknee_h1 (ebe81b0).

I re-measured everything below from the files in this directory, with my own scripts. The scripts are in the session
scratchpad (vfy_pk/), not in the repo. I ran the judges on a copy of the design (locally) and through the farm with
`--outdir` (scratch), so the builder's judge/*.json files were not overwritten. I changed nothing in the design.

**Verdict: NOT REFUTED.** All five checks hold on the points the claim makes:
- The kinematics are the verified model's to 5e-5 mm.
- The joint hardware is real catalogue parts at their real size.
- The builder reaches no loft.
- Every re-run judge reproduces the scorecard within 0.3 points.
- The stills show this CAD on a matte, faceless mannequin.

The main defect is the one the builder reported itself. The link bars do not reproduce the model's straps within
0.5 mm: they ride up to 4.1 mm (link 1) and 10.9 mm (link 2) above them. That is why this CAD loses R1 / R1-aim / R4
against its own L1. The claim also misses or overstates a few smaller things, listed under "Corrections". None of them
changes a requirement's status.

## 1. Built parts posed by clips.json vs the verified model

Method:
- I wore the frozen H1 shape with `pinknee_shape.wear(".cache/pk_shapes/h1_b110_360_m5.pkl")`: tr 84.72, f [51.70, 61.31,
  76.30], the build's own shape.
- I ran the model chain (`build_pinknee_l1.chain`) on the clip poses.
- I posed exo.glb with the judges' own path, `scene_export.posed_scene` (clips.json G / T).
- Distance: libigl point-to-mesh distance from each group of model metal samples to the union of the posed built parts
  (F excluded).
- Model metal samples: `M.rigid` (hubs, E strap, E boss, arm pad, knee), `M.link_pts` (L1, L2 straps), plus the model's
  `M.contact` outer envelope.

Six followed clip frames:

| frame | pose (plane, elev, axial) | knee deg |
|---|---|---|
| Raise overhead 78, the highest followed frame | (30, 150, -60) | 144.12 |
| Reach back pocket 72, behind the back | (-80, 39, 101) | 116.81 |
| Comb hair 105 | (78, 143, -67) | 133.25 |
| Wash opposite shoulder 81, across the body | (145, 46, -69) | 101.92 |
| Walking 0, arm at the side | (90, 4, -90) | 101.35 |
| Reach a high shelf 75 | (82, 132, -82) | 135.16 |

| group | max distance to built metal, every frame | note |
|---|---|---|
| clips.json G / T vs the model chain | **5e-7 (R) / 5e-5 mm (t)** | closure residual <= 0.0002 deg; the clip's knee angle equals the model's to 0.01 deg |
| hub 1 / hub 2 / hub 3 | 0.144 / 0.144 / 0.000 mm | cap domes and rounds |
| E strap / E boss / arm pad | 0.124 / 0.000 / 0.000 mm | |
| knee link | 1.24 mm (p95 0.0) | samples at the pin centres, inside the bores the pins fill; the claim said 1.75 over its 11 poses |
| link 1 strap (L1) | **4.13 mm** (p95 3.95) | the bar rides above the model's strap: the shape change the claim states |
| link 2 strap (L2) | **10.84 mm** (p95 9.90) | the same, largest at J3 (claim 10.90) |
| model contact envelope (hub walls / crowns, strap tops) | 7.9 mm max, p95 2.2 mm | follows from the bars |

Every number is the same at all six frames to 0.005 mm. The kinematics and every joint feature reproduce the model.
The bars do not reproduce it within 0.5 mm, and the claim says so (build.json `within_0p5` False).

**Check 1 holds for kinematics and joint features. It fails the 0.5 mm bar for the two link bars, as disclosed.** That
shape change is the measured cost below: R1 -8.5 against the L1.

## 2. Real components at their real size

I measured oriented boxes and volumes of the posed exo.glb parts.
- **Hub stacks (J1-J3), all O20 (user ruling "Keep O20 only"):**
  - 2x MR117-2RS: 10.99 x 3.0, 169.5 mm3 each (7 x 11 x 3, real ISO miniature bearings).
  - Cap O20 x 3.45.
  - Outer spacer 0.6, inner spacer 0.6, ring nut M7x0.5 0.9. The same v5 stack as gen 2.
- **Knee link:** 40.24 x 10.0 x 2.59. This equals lc 28.24 + 2 x 6 boss radius, at stk/2.
- **Pin stack:**
  - iglidur sleeve O5.5 x 1.89. The volume, 20.9 mm3, matches a 4 / 5.5 sleeve 1.89 long.
  - Thrust washer O8 x 0.5 (18.2 mm3).
  - DIN 6799-3.2 E-clip 7.3 x 6.93 x 0.6 (16.1 mm3).
- **Stack order along the pin axis** (0 = the knee's outer face, away from the skin): clip 0.1-0.7 in the 0.7 counterbore,
  sleeve 0.7-2.59, washer 2.59-3.09, boss / pad 3.09-5.68. The stack is **5.68 mm**, as claimed.
- **Base:** 20.0 x 20.0 x 7.07, 1466 mm3 (6.49 g Ti). The O20 ring and the spigot, with no tab and no ears.
- **Cuff screws:** M4x6 ISO 10642, head 7.89, length 6.0.
- **Masses** reproduce parts_full.json: knee 880 mm3 = 3.9 g Ti; member 3 2668 mm3 = 11.8 g; link 1 3166 mm3 = 14.0 g.
- **Every joint maps to a component:**
  - 3 pins on MR117-2RS pairs.
  - 2 knee pins on iglidur G sleeves (igus GSM-0405-03) with thrust washers, retained by DIN 6799 clips.
  - 0 passive translations.
- R7 (my local run with OCC, on a copy): 28 STEP files, all valid single solids with 0 bad faces. This is **identical**
  to the builder's part_validity.json, row for row.

**Check 2 holds.** Small notes are in C2 and C3.

## 3. No lofts or fitted surfaces

Static trace of the builder and everything it calls:
- user_style_pinknee.py, fixup_pinknee_export.py, user_style.py, sketch2d, cad_helpers, and param_build (only
  `revolved`, `joint_parts`, `disc_face`, `axis_frame`).
- I searched for `loft`, `makeLoft`, `ThruSections`, `interpPlate`, `spline`, `makeSpline*`, `GeomAPI*`, `BRepFill`,
  `twistExtrude` and `parametricSurface`.
- param_build.py has two `makeLoft` calls, in `strap_solid` and in its `main` neck. Neither is reachable: no function
  this builder calls calls them.
- `bar_swept` is one constant rounded-rectangle section swept by `BRepOffsetAPI_MakePipeShell` along a wire of lines and
  three-point arcs, with a fixed binormal. That is one section on a line/arc path, with no twist.

Member 3's E strap underside is a 12-vertex polyline with about 1 mm rounds: the upper hull of the model's E profile at
2 mm stations, extruded. That is a sketch of lines and arcs, not a fitted surface. It follows the model's strap, not the
skin directly.

**Check 3 holds.**

## 4. Part validity and the cheapest judges, re-run

Two runs:
- **Farm:** `tools/cloud_run.py judge user_pinknee_h1 fast --outdir <scratch>`. Job 895 s, about $0.07-0.08. SKIP_FEA, as
  in the claim.
- **Local:** `score_design.py` (14 mm band) on a copy, and R7 locally.

Both are on the current files, after the pin-a sleeve fix.

| req | claim | re-run | difference |
|---|---|---|---|
| R1 (2-14 mm) | 71.57 % | **71.40 %** (farm and local agree) | -0.17 |
| R1-aim (2-10 mm) | 33.06 % | **32.85 %** | -0.21 |
| R3 | 98.67 % | 98.67 % | 0 |
| R4 overhead | 68.99 % | **68.67 %** (median gap 12.52 mm, min 1.78 mm) | -0.32 |
| R2 | 24.87 mm (F forearm cuff, the user's) | 24.87 mm | 0 |
| R2 ours, plain / attributable | 17.67 / 4.71 mm | 17.67 / 4.71 mm | 0 |
| R6 | 0.0 mm, 451 frames x 2586 pairs | 0.0 mm, 451 x 2586 | 0 |
| R7 | PASS | PASS (identical rows) | - |
| R11 / R16 / R17 | 0.303 kPa / 61.67 % / PASS | 0.303 / 61.67 % / PASS | 0 |

**Check 4 holds: every value is within 0.32 points, and 8 of 19 pass.** I did not re-check the claim that the L1
re-judged at step 12 gives exactly 61.7 % (R16).

## 5. The renders

I looked at all 16 JPGs at full size.
- **Mannequin:** matte charcoal, faceless (smooth head, no features), muscles readable (rest_back_lateral).
- **Exo parts:** satin bead-blasted metal. The iglidur orange shows as crescents in the bores.
- **No black parts** (but see C4).
- **The design shown is this CAD:**
  - three O20 hubs;
  - machined link 1, with the wavy pocketed bar on the J1-J2 span;
  - bent link 2;
  - member 3 with the E strap and boss;
  - the flat two-pin knee link;
  - the 62 deg pad mount into the cut BOTTOM;
  - the base with no tab;
  - the trimmed upper-arm cuff with its screws.
- **Poses** (shots.json, design = this directory): the hero overhead is Raise overhead frame 78. Its knee is 144.1 deg,
  equal to my chain's 144.12.
- **Clearance:** no exo part passes through the body in any shot. shots.json's clearance block agrees with the farm R2
  run. Our links / hubs / knee are >= 1.76 mm clear (link 1, overhead).
- **The H group** shows 34-39 samples up to 1.74 mm inside the skin. These are at the elbow end of the user's BOTTOM bar,
  the known R2 liner contact, which the README discloses.
- **Artifacts** (both disclosed, neither is exo geometry):
  - the dark notch at the forearm-cuff rim (the mannequin's forearm inside the user's forearm cuff);
  - the jagged axilla skin in hero_overhead_chain, hero_shelf_back and hero_shelf_chain (the rig folding).

**Check 5 holds.**

## Corrections (none changes a status)

- **C1. Stale scorecard values.** The scorecard's R1 / R1-aim / R4 are pre-fix farm values. The current files give 71.4 /
  32.8 / 68.7 %, each 0.2-0.3 lower. Both judges and the farm agree on these.
- **C2. The E-clip has no retaining land.** The integral O4 pins (member 3's pin a, and pin b on the BOTTOM part) end
  flush with the knee link's outer face. That is only 0.1 mm beyond the clip's outer face. DIN 6799 needs a land of about
  1 mm beyond the groove on a 3.2 clip. As built, there is no material to cut the groove's outer wall into, so the clip
  cannot be retained.
  - The real pins stand about 0.9-1 mm proud of the knee's outer face. That is what the L1 modelled (RET 0.9).
  - So "nothing stands above the knee plate" is optimistic by about 1 mm, on the side away from the skin.
  - The skin judges do not move. Re-check the link-2 fly-over clearance when the pins are lengthened.
- **C3. Hardware that is not quite catalogue.** The GSM-0405-03 sleeve (b1 = 3 mm) is faced to 1.89 mm, so it is a
  modified catalogue part. The thrust washer size (GTM-0408-005 "class") is still to be confirmed. Both are disclosed.
- **C4. The polished E-clips read near-black** in the knee macros (parts_knee_macro, parts_knee_rest_macro,
  parts_knee_top), because they mirror the dark studio. The material is right (polished A2). On screen it fights the
  "no black parts" look, so a lighter environment or a satin clip would fix the stills. The claim mentions it.
- **C5. "Our new parts add 0" to R2 is true only on the attributable metric.** The new upper-arm cuff and its screws sit
  17.67 / 17.64 mm inside the rig body in Wash opposite shoulder (frames 78-126). That is in the chest, where the rig's
  own upper arm passes about 90 mm into the trunk (judge/body_regions.py), so the attributable depth is 0. The plain
  depth is the scorecard's "this project's parts 17.67 mm".

## What this means

The generation-3 CAD stands as built and judged: 8 of 19.
- It still owes the L1's R1 (80.1 %) and R4 (74.2 %). The measured cause is the bars, confirmed here: up to 4.1 mm
  (link 1) and 10.9 mm (link 2) above the strap the evaluator scored.
- The builder's next lever (PK_LINK2_MACHINED=1, link 2 machined to follow the strap) targets exactly the 10.9 mm group.
- Lengthen both knee pins by about 1 mm for the clip land (C2) in the same rebuild.

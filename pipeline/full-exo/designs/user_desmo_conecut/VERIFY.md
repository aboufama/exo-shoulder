# Independent check: user_desmo_conecut (the generation-9 winner's full CAD)

Checker (a skeptic), 2026-10-18 04:44-05:29 UTC, inside the 45-min box. What I tested:
- the full CAD as committed (exo.glb md5 d4b8d1ac..., unchanged since 9c391e3; build.json / design.json at efbcaaf; the
  judge outputs and scorecard at c17a426);
- its builder `pipeline/conformal/param_cad/user_style_desmo.py` (md5 5510adcd...);
- the L1 builder it imports, `pipeline/concept_l1/build_desmo_l1.py` (md5 53801ae6...). That file retargets the gen-8 / gen-7
  builders at the verifier's DCModel.

**How I ran it.** I changed nothing in the design. The judges ran on a byte copy in the session scratchpad
(`judge/common.design_dir` and `score_design.py` both take a path), so this file is the only thing of mine in the design tree.
- Local only: nice 15, OMP_NUM_THREADS=1, at most two of my processes at a time, one worker each (`--jobs 1`).
- No farm, no GPU: spend $0.
- The box ran at load 9-18 the whole time (two discovery-loop gates plus the CAD's own judge chain).

**My scripts** (session scratchpad `vdesmo/`, not committed):
- `kin_indep_dc.py` is model-free: it reads only exo.glb, clips.json, workspace.json and build.json.
- `kin_vfy_dc.py` is the gen-8 check pointed at this design. It runs the claim's own DCModel (`build_desmo_l1.fit()`, the
  verifier's model with the blended IK; fit gap 13.27 on Bench(60,160) fast) and poses the CAD's parts by the model's own run
  state. It now also covers the model's stage-1 / plate contact samples.

## Verdict

**NOT REFUTED as a record of the verified model. NOT a buildable mechanism, as the CAD itself says.**

What reproduces:
- **Re-run judges match the scorecard** (section 4):
  - R6 1.50 mm FAIL: the same 8 violating pairs at the same depths and worst frames, 451 frames x 6510 pairs;
  - R7 PASS: all_ok, 52 custom parts, no STEP missing;
  - R1 81.76 / R1-aim 52.26 / R4 74.78, to the digit, every clip identical;
  - R16 24.2 %, identical;
  - R17 PASS, nominal case identical (M_GH 0.122 N.m, 0.51 N, twist 3.97 deg).
- **The kinematics are the verified model's** (section 1):
  - every bearing axis matches the judged frames to 0.0012 deg and 0.0002 mm on 2372 frames;
  - K follows the slaved law to 0.0017 deg (1130 driven frames);
  - the crank angle is a single-valued function of K, at most 0.02 deg off zero in the dwell;
  - the claim's own chain re-derives the workspace frames to 5e-5 mm;
  - link 1a's nose and the stage-1 pin are each held between two walls of their slots on every frame I checked.
- **No loft can reach an exported part.** The new drive parts carry no B-spline surface.
- **User parts are untouched:** all 37 are identical to gen 8's. Only BOTTOM is cut, as D8-06.

What does not hold:
- **Criterion (2) fails, and the CAD discloses it.** The stage-1 insert, pin, short arm and link 2's roof sit inside link 1b's
  J2 plate and strap by 1.39-1.50 mm on every frame.
  - The short arm D9-03 has no connection to the crank. The judges still move it rigidly with the crank, because it is in group
    dk.
  - So the drive as built cannot transmit, and R16 falls from gen 8's 66.7 % to 24.2 %. I attributed all 51 failing closing
    poses to those pairs.
- **New finding 1: the stop loads go through the drive.** The CAD's stop geometry, and also the drawing's K-lead fix as written,
  route the J2 low-end stop load through the drive (section 5). This contradicts the drawing note "every stop load
  bypasses stage 1".
- **New finding 2: the pin is not crowned in the CAD.** The "crowned R4" stage-1 pin is a plain cylinder in the CAD. Its posed
  overlap with the groove is 0.023 mm.
- **Criterion (1) fails for the bars** (L2 1.63, E 1.33, L1b 0.70, knee 0.85 mm, all outward), as it did in gen 8 and as
  disclosed.
- **No stills exist,** so criterion (5) cannot be checked.

## 1. Posed parts against the verified model

**Model-free check (kin_indep_dc.py).** Each joint's axis comes from the CAD's own bearing (PCA, rest pose) and is compared with
the relative rotation of the judged frames. Frames: 1035 closing workspace poses + 1337 clip frames = 2372.

| joint (bearing) | axis deviation max | translation residual | angle range on the frames |
|---|---|---|---|
| J1 (MR117) | 0.0009 deg | 0.0001 mm | -127.61..149.18 deg |
| K (MR117) | 0.0009 deg | 0.0001 mm | -46.27..0 deg |
| J2 (MR117) | 0.0012 deg | 0.0001 mm | -101.18..14.21 deg (q2 = -angle: -14.207..101.181, inside the window -14.315 / 102.068) |
| J3 (MR117) | 0.0011 deg | 0.0002 mm | q3' -111.159..119.752 on the workspace, window -111.9036 / 122.7417, 0 frames outside |
| crank (MR63ZZ) | 0.0010 deg | 0.0001 mm | 0..19.33 deg |
| knee pin a (MR63ZZ) | 0.0010 deg | 11.8 mm (gen 8's rest-frame convention: the knee link's rest geometry sits off the pin in the glb; gen 8 showed the pin on its pair to 0.0003 mm) | -19.63..28.17 deg |

- **K against the build.json law** (a function of q2): max error 0.0017 deg on 2372 frames, 1130 of them driven. The stored dK
  matches the frames to 0.0005 deg. The frames reach dK -46.268, against the law end at -46.5.
- **Crank against K:** single-valued. The spread within 0.25-deg bins of |dK| is 0.10 deg (the bin width times the slope), with
  no monotonicity break over 0.3 deg. In the dwell the crank stays within 0.021 deg of zero.
- **Stage 2:** link 1a's nose-dowel axis, posed in the crank frame, has crank walls on both sides on 791 of 791 frames checked
  (every 3rd).
  - Axis-to-wall distance: 0.743-0.760 mm.
  - So the O1.5 nose overlaps the 1.52 slot by at most 0.007 mm. This is the builder's "-0.007".
- **Stage 1:** the pin axis, posed in link 2's frame, has insert walls on both sides on 791 of 791 frames.
  - Axis-to-wall distance inside the slot: 0.727-0.760 mm.
  - So the pin overlaps the groove by at most 0.023 mm. This is the builder's "-0.022", and it comes from finding 2.
- **Knee:** knee angle 59.27..107.07 deg on the workspace, 47.7 deg under the knee stop (= gen 8).

**Model metal against the built solids (kin_vfy_dc.py).** Twelve picks, all taken on the fit bench:

| pick | bench pose | (plane, elev, axial) | dK |
|---|---|---|---|
| arm at the side | 60 | [-90, 0, 75] | |
| highest / overhead | 140 | [45, 165, -90] | |
| behind the back | 62 | [-90, 30, 105] | |
| across the body | 214 | [150, 45, -60] | |
| drive extreme | 174 | [90, 120, -90] | -46.25 |
| overhead raise peak | 5 | [30, 150, -60] | |
| J3 q3' min | 91 | | |
| J3 q3' max / knee max | 152 | | |
| knee min | 89 | | |
| low front reach | 107 | | |

Each part is rigid in its member frame, so the numbers are the same at every pose. "Outside" means the distance to the CAD part
for samples NOT inside it (winding number).

| model sample set | max outside | p95 | share > 0.5 mm | of those, CAD nearer GH by > 0.25 |
|---|---|---|---|---|
| L1a, boss (nose), pad, ring2 (stage-1 sector), horn | 0.00-0.04 | 0 | 0 | - |
| hub1 / hub3 | 0.144 / 0.100 | 0.007 / 0 | 0 | 0 |
| tip plate | 0.126 | 0.108 | 0 | 0 |
| L1b strap | 0.702 | 0.581 | 11 % | 0 |
| knee | 0.850 | 0 | 1.1 % | 0 |
| E strap | 1.330 | 1.038 | 17 % | 0 |
| hub K / hub 2 (stop-slot bands) | 1.419 / 1.420 | 0.90 / 0.88 | 15 / 11 % | 0 |
| L2 strap | 1.627 | 0.845 | 22 % | 0 |
| crank | 6.787 | 4.468 | 32 % | 3.8 % (by at most 0.91 mm) |
| model stage-1 pin + short arm (contact set) | 0.157 | 0.109 | 0 | 0 |
| model cap ring at its level (contact set, link 2) | 0.661 | 0.660 | 18 % | 0 |

- **These reproduce the builder's table to the digit.** One exception carried over from gen 8 (gen-8 finding 2, still open):
  the summary lists hub K / hub 2 as 0.0, while build.json's per-pose record has 1.4195 / 1.4196 in the stop-slot bands.
- **Crank.** The builder calls its 6.79 mm "the model's arm samples past the trimmed tip".
  - The p95 of 4.47 mm and a 32 % share > 0.5 mm say more than the tip is involved.
  - The crank boss is raised 3.96 mm over the model's (build.json crank.raised_over_model_mm), so it can sit on link 1b's strap.
    That raise is a disclosed metal change away from the skin.
  - 3.8 % of the crank samples have the CAD nearer GH by up to 0.91 mm. I did not localise them.
- **The model's contact sample sets** lie 1-5.8 mm outside the CAD, with the CAD nearer GH. Several of them are the model's
  samples offset outward by T_LINK or 3 mm (`pts + T_LINK * unit(pts)` in the models).
  - They are outward envelopes the CAD does not fill.
  - The skin-side sets of the same members (L2 / E / L1b / hubs) have a CAD-nearer-GH share of 0, so no CAD metal sits nearer
    the skin than the model's bottom metal there.
  - The crank's 3.8 % is the one exception and is not localised (above).
- **Judges' frames against the claim's chain** (12 random closing workspace poses): rotation entries to 5.0e-7, translations
  to 5.0e-5 mm.
- **Slaved law against the stored frames** (1035 workspace poses, 553 of them stretched): 0.0017 deg.

**Criterion (1) holds for frames, joints, the slaved law and both drive closures. It does NOT hold for the bars or the crank**
(disclosed). All bar misses are outward.

## 2. Real size, real component

Bought parts carry their catalogue envelopes (parts_full.json, the same items as gen 8 where shared):
- MR117-2RS 7x11x3 (8), 0.169 cm3;
- MR63ZZ 3x6x2.5 (2 crank + 4 knee), 0.053;
- ISO 8734 O3 stop dowels, the J3 2 m6 x 5 dowel, knee pins 3 m6 x 10;
- the nose ISO 8734 1.5 m6 x 5;
- DIN 6799 RS 2.3 clips.

**Findings on parts:**
1. **D9-03, the stage-1 short arm, is not attached to anything.** The CAD says so on the part. It hangs under link 1b's strap
   while the crank boss sits on top, so no real assembly joins them. It is a placeholder for the verified model's metal, not a
   component.
   - Together with the insert / pin / roof crossing link 1b by 1.39-1.50 mm, the stage-1 half of the drive cannot be made as
     modelled.
   - The CAD's main finding stands: stage 1 has to move, and the discovery loop owns that.
   - I read stage1_level_scan.json and did not re-run it. Its own rows show 2 feasible pins at F+3.9 (PA 29.5, groove radius
     1.024) and 0 at F+4.6 and above, so "a groove in link 2's own layer at <= F+3.9" is the scan's only open door, as the CAD
     says.
2. **The stage-1 pin is not crowned in the CAD.**
   - The STEP has one cylindrical surface and two cones (chamfers); there is no toroidal or spherical crown.
   - The crown (R4, end drop 0.039 mm) exists only in the part name and the fits table. The posed straight pin therefore
     overlaps the 1.52 groove by 0.023 mm across the 4.76-deg tilt.
   - The drawing is right. The CAD solid is not the drawn part.
3. **The K cap's material is mislabelled.** Its name ends "(Ti-6Al-4V)", but parts_full.json gives "1.4310 spring steel
   (polished)" and 3.78 g, against 2.12 g for the other Ti caps.
   - Cause: `user_style_slipper.material()` maps any name containing "clock spring" to spring steel, and the new name says "NO
     clock spring".
   - R8 is high by 1.66 g. A render would show this cap polished, not bead blasted.
4. **The insert key dowel** ("keyed by an ISO 8734 1 m6 x 4 dowel") is in the fits table only. It is not a part in the CAD.
5. **The cap-ring sector runs 0.96 mm past O20** (r 6.05..10.96 over 123.9 deg), as disclosed. The verified model also samples
   it outside O20 (`ring_sk` from HUB_R + 0.25 to r_out), so the claim counted this metal.

## 3. No lofts

- Neither new builder calls loft, spline, twistExtrude or a surface fill. `user_style_desmo.py` uses only lineTo /
  threePointArc / extrude / revolve / cut, plus the gen-7/8 helpers. The gen-7 / gen-8 checks walked those helpers'
  21-module import graph: their only loft site, `param_build.makeLoft`, is never reached on this path.
- B-spline surfaces in the STEP files:
  - link 2: 174 (gen 8: 168; the roof adds fillet blends);
  - link 1b: 24 (gen 8: 18);
  - BOTTOM: 34 (the user's own part).
- These come from the 0.5 mm `US.rounded` fillets, which are allowed. The new drive parts carry none: the insert has 59
  cylindrical faces (the 29-arc line/arc slot); the crank has cylinders, cones and spheres; the short arm, pin and nose are
  cylinders.

## 4. Re-run judges (local, current judges, the scorecard's steps)

| Req | claim (scorecard, c17a426) | re-run | match |
|---|---|---|---|
| R1 | 81.8 % | 81.7556 % (score_design BANDS 10,14, step 3; 22 min at load 14-18) | yes, to the digit |
| R1-aim | 52.3 % | 52.2631 % | yes |
| R4 | 74.8 % | 74.78 % (Raise overhead at 14 mm). All 8 clips are identical to score.json / score_14mm.json (min gap 1.6 mm in Raise overhead, near-touch reported only) | yes |
| R6 | 1.50 mm FAIL (451 frames x 6510 pairs) | 1.50 mm FAIL: the same 8 violations, same depths and worst frames, pair by pair (557 s) | yes |
| R7 | PASS (52 custom, none missing) | all_ok True, 52 custom parts (3 arm-fixed), missing STEP none | yes |
| R16 | 24.2 % FAIL | 24.2 %: does not close 33.3 %, body 0.0 %, part interference 42.5 %, evaluator agreement 57 % (step 12, --jobs 1) | yes |
| R17 | PASS (nominal M_GH 0.122 N.m, 0.51 N, twist 3.97 deg) | PASS, nominal case re-run (`--quick --jobs 1`): M_GH 0.122 N.m, F 0.51 N, twist 3.97 deg, K law error 0.06 deg, lift-off 0.000, drive 0.071 N.m. The krate0.01 case 0.118 / 0.49 / 3.87 is identical. The 17 comparison cases were not re-run (box). | yes (nominal) |

- **Against its own L1** (judge/vs_l1.json, which I read):
  - R1 -0.44, R1-aim -0.77 and R4 -0.76 against l1_desmo-conecut (82.2 / 53.0 / 75.5): the same order as gen 8's -0.39, from the
    bars riding outward;
  - R6 +0.02 mm (1.48 -> 1.50, the same conflict);
  - R16 +10.8 (13.3 -> 24.2);
  - 7 of 19 pass on both.
- **Against gen 8's full CAD:** R1 81.6 -> 81.8, R4 74.1 -> 74.8, R6 0.0 -> 1.50, R16 66.7 -> 24.2.

- **R6 attribution** (my run and the committed file agree pair by pair): every violation is a stage-1 part against link 1b.

| part | against link 1b |
|---|---|
| short arm D9-03 | 1.50 / 0.72 mm |
| pin | 1.47 / 0.65 mm |
| insert | 1.42 / 0.64 mm |
| link 2's roof | 1.39 / 1.39 mm |

  Nothing else interferes. The drive's running pairs are clear of R6's 0.15 tolerance: nose / slot -0.007, pin / groove -0.023.
- **R16 attribution** (judge/workspace.json): 120 poses.
  - 40 do not close (= gen 8).
  - 29 pass.
  - 51 fail on part interference beyond the rest overlap (up to +0.53 mm of motion). In every one of the 51, the interfering
    pairs are the six ordered stage-1 / roof pairs against link 1b above.
  - With stage 1 moved, R16 would be expected back at gen 8's 66.7 %. That is an inference, not measured.
- **R17 cannot see K's free play.** The dynamics judge holds K to its law by "form" closure (build.json slaved, `closure:
  form`).
  - The judge's closure is a stiff constraint, not a backlash model. K's law error is 0.055 deg in the nominal case (gen 8's
    sprung K: 0.12), lift-off share is 0.0 in all 19 cases, and the error reaches 2.7-11.0 deg only in the plain-bearing /
    constant-friction comparison cases (f0.5, mu 0.25-0.37), which fail on twist for every design (gen 8: 2.7-53 deg).
  - So R17 does not answer whether a spring-free K chatters or drifts.
  - The one-sided free-play band the build states (0.217 / 0.276 deg, the red team's numbers) is not simulated anywhere.
  - As built, with no K lead in the geometry (finding 1), that band takes held-out th from 5.006 to about 4.89-4.99: one held
    pose under 5 (red-team re-solve 4.986; audit T3 4.915 / 4.893).
- **Process:** both the L1's and the full CAD's R17 ran with judge/dynamics.py's default 4 workers (`jobs: 4` in both
  dynamics.json; I saw four dynamics.py processes at 04:49). The claims say "one process, --jobs 1". `judge1.sh` passes --jobs 1
  to every judge except dynamics.py.

## 5. Stops as built: the J2 low-end stop load goes through the drive (new)

Read from build.json and the builder, no new geometry:
- The **stage-1 groove's rise ends at dK_lim = 46.5** (`groove_law`: x runs to `lim`; groove_q2_deg low end -14.282), and the
  **stage-2 slot's far end is "stop B at dK 46.5"** (D9-01's name; plate slot 3.90 long).
- The **J2 dowel's low window is -14.315** (= K_law 46.5) and it **engages at -14.455**
  (stop_engagement_built: 0.14 deg past, the 0.02 mm clearance), that is at K_law of about 46.80 (kK 2.1534).
- So, as built, the groove end and the slot end stop the J2 low end about 0.3 deg of K before J2's own dowel touches. A shove
  at the drive extreme (pose [90, 120, -90], dK -46.25, 0.23 deg of K from the ends) loads the O1.5 stage-1 pin and short arm and
  the O1.5 nose in the slot end. The "J2 stop rated 4.3 N.m" (build.json j2_push_limit) does not apply at this end.
- **The drawing's fix as written does not cure this.** The fits note asks for a +0.25 deg K lead (insert key +0.116 deg of q2),
  the slot to kslot 46.9 and J2 stop B at K_law 46.30, and says "every stop load bypasses stage 1".
  - The lead moves the groove end to K_law 46.25.
  - The J2 dowel at a 46.30 window still engages 0.14 deg of q2 (0.30 deg of K) later, at K_law of about 46.60.
  - So stage 1's groove end would still stop first, by about 0.35 deg of K. With the lead, the held extreme (K 46.27) would also
    sit at the groove end.
  - **The groove's rise must also be extended past the dowel's engagement**: to at least kslot 46.9. The red team puts the
    stage-1 pressure-angle limit at K 47.50, so there is room.
  - The red team's slot-only arithmetic missed the groove end. It belongs on the drawing.
- At the high end (q2 102.068), the groove's dwell now runs to 103.068, past the J2 dowel's engagement at 102.208. That end is
  clean.

## 6. Stills

- No stills exist (no render: GPU stills need the user's separate yes). Criterion (5) cannot be checked: matte faceless
  mannequin, no black parts, no part through the skin, the look-audit fixes.
- If one is rendered: the K cap would come out polished (part finding 3), and D8-06 is specified clear anodised, never black.

## Findings for the fix list

1. **Stage 1 cannot be built where the verified model puts it.**
   - R6 1.50 and R16 24.2 % are all this conflict; the short arm D9-03 floats.
   - This goes to the discovery loop with the CAD's level scan (the only feasible door is a groove at <= F+3.9 in link 2's
     layer, with the arm passing link 1b's plate and strap root). Re-verify after the move.
2. **J2's low-end stop must engage before both drive ends.**
   - Extend the groove's rise to about 46.9 (inside PA 47.5) together with kslot 46.9.
   - Then place J2 stop B so that its dowel's ENGAGEMENT, not its window, comes before 46.5 + lead.
   - Correct the fits note, which now claims a bypass that neither the CAD nor the note's own numbers give.
3. **Model the crown on the stage-1 pin** (an R4 arc in the revolve profile) so the solid is the drawn part. Fix the K cap
   material map ("NO clock spring" matches "clock spring"). Add the insert key dowel as a part.
4. **Put the hub K / hub 2 stop-slot band (1.42 mm) in the summary table** (gen-8 finding 2, repeated).
5. **R17 needs a free-play case for the spring-free K** (form closure plus a 0.22-0.28 deg backlash band) before anyone calls the
   desmo K "chatter-free". Until then, K play costs the held-out fold margin (th 4.89-4.99 at one pose without the lead).
6. **Process: run dynamics.py with --jobs 1** when the cap is two processes.

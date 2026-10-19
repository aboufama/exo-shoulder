# Independent check: user_minarc_pick1 (the gen-4b full CAD on the verified polished config pick1) and its L1

Checker (a skeptic), 2026-10-16 18:18-18:35 UTC. Tested: the full CAD `user_minarc_pick1` and the L1 `l1_minarc-pick1` as
committed at 0906330 (builder `pipeline/conformal/param_cad/user_style_minarc.py`, L1 `pipeline/concept_l1/build_minarc_l1.py`).

I re-measured everything with my own scripts (session scratchpad `vfy_p1/`, not committed):
- `kin_check.py`: the verified model's OWN member transforms vs the posed exo.glb through the judges' frame path, model
  metal vs the posed parts, dowel windows, clip provenance, skin clearance.
- `hw_check.py`, `hub_env.py`, `kslot.py`, `knee_ang.py`: spring / magnet / dowel fits, hub heights, stop slots vs the bar
  roots, knee angles over the clips and the R16 workspace.
- `noloft_build.py`: a full rebuild to scratch with every loft / spline entry point trapped.
- `dyn_pre.py`: R17 at another K preload, on the full CAD.

R1 / R1-aim / R4 / R6 / R16 / R17 ran on the farm with `--outdir` in scratch (no file in the tree overwritten). R7 ran
locally; its output is unchanged. I changed nothing in the design.

**Verdict: NOT REFUTED.** Every judged number reproduces exactly. Both CADs sit on the verified pick1 model's kinematics.
Two claims need correcting, and neither changes a requirement's status:
- **Preload 0.05 is not a pass on the full CAD.** The preload sweep ran on the L1 only. On the full CAD, preload 0.05 gives
  a K drift of **5.04 deg** (rate 0.015) and **5.01 deg** (rate 0.010) on Reach a high shelf. Both are over the 5.0 deg
  limit; the L1 gives 4.96 / 4.93 deg. Option 2 of the claim's R17 issue is a fail on the CAD by 0.01-0.04 deg. Either
  way the result sits on the limit, so a preload change is no fix.
- **"Joint geometry <= 0.144 mm" leaves out two parts.** The E strap's model metal sits up to 0.62 mm outside the CAD, and
  the knee plate's up to 1.70 mm (section 1). Both are less metal than the model, so they add no contact.

No measurement changed in this task: no judge, skin model or motion set differs from the claim's run.

## 1. The posed parts reproduce the verified model

**The fit reproduces.** I fitted pick1 (build.json params, a1max 66.4696) on Bench(60,160) fast at fold margin 5.5:

| quantity | value |
|---|---|
| near-touch gap | 15.94 |
| plain gap | 11.57 |
| hub levels J1 / K / J2 / J3 | 49.11 / 57.90 / 60.71 / 79.97 mm |
| tr | 87.16 |
| knee centre m | (-12.574, 0.669) |

**The poses.** I checked 7 distinct bench poses, 3 of them with K forced open. At each one I compared the model's own
member transforms with the judges' frames (`build_minarc_l1.chain`, then `frame_dict`, then `scene_export.frame_xforms`).

| pose (plane, elev, axial) | state | dK (deg) | q2 (deg) | frames vs model | closest skin, our chain (CAD) | (L1) |
|---|---|---|---|---|---|---|
| arm at side (-90, 0, 75) | A | 0 | -5.87 | 3.5e-5 mm | l1a 2.57 mm | l1a 2.42 |
| highest taken (45, 165, -90) | A | 0 | 1.96 | 6.3e-5 mm | l1b 0.74 mm | l2 0.53 |
| overhead raise peak (30, 150, -60), Raise overhead | A | 0 | 66.91 | 4.9e-5 mm | l1a 0.67 mm | l1a 0.58 |
| behind the back (-90, 30, 105) | A | 0 | -10.87 | 5.3e-5 mm | l1a 3.77 mm | l3 3.43 |
| across the body (150, 45, -60) | A | 0 | -15.64 | 4.8e-5 mm | l1a 6.45 mm | l1a 4.60 |
| **K most open taken** (120, 120, -90) | forced | **-52.49** (stop B -56.65) | -15.85 (on its stop) | 5.9e-5 mm | l1b 1.95 mm | l1b 1.73 |
| K partly open (-15, 0, 105) | forced | -13.61 | -15.85 (on its stop) | 5.5e-5 mm | l1b 5.46 mm | l1a 4.24 |

- **Dowels.** K and q2 stay inside their windows at every pose (-56.652..0 and -15.848..97.419 deg).
- **Skin.** No part of our chain (base, l1a, l1b, l2, l3, l4) is inside the skin at any check pose, on either design. The
  arm-fixed D8-06 (the user's BOTTOM fused with our pad mount) is inside the rig skin by 1.9-4.0 mm at every pose, and by
  25.1 mm across the body. That is the known R2 liner and rig-arm finding, the same as BDp.
- **Clip provenance.** The judged clips.json matches a fresh chain solve to max |dG| 5e-7 and |dT| 5e-5 mm over 1900 group
  frames. These include every frame of Reach a high shelf and of Wash opposite shoulder, the two clips where K opens.

**Model metal against the posed parts.** All poses give the same numbers.

| model metal | L1 | full CAD (outside the part) | BDp CAD |
|---|---|---|---|
| hub discs J1 / K / J2 / J3 | 0 | 0.144 / 0 / 0 / 0 mm | 0.144 / 0 / 0 / 0 |
| E boss, arm pad | 0 | 0 | 0 |
| **E strap** | 0 | **0.616 mm, 4 of 116 samples over 0.5** | 0.536 |
| **knee-link plate** | 0 | **1.703 mm, 3 of 100 samples** | 1.397 |
| hub K / J2 discs in the stop-slot band | 0 | 1.42 mm (the real slot void) | 1.42 |

- The L1 carries the model's metal exactly; its claim of <= 0.0001 mm holds.
- On the CAD, the E strap and knee plate both exceed the 0.5 mm line. They are less metal than the model, so they add no
  contact. The builder's own log prints both ("all rigid 1.703: E 0.62, knee 1.70"), but the claim's summary does not.
  Both grew since BDp.

**Bars against the model strap.** Strap samples outside the hub zones:

| link | max | mean | share within 0.5 mm | samples inside the bar |
|---|---|---|---|---|
| 1a | 0.19 mm | 0.10 mm | 100 % | **2 of 10** |
| 1b | 0.94 mm | 0.33 mm | 75 % | 0 |
| 2 | 1.16 mm | 0.40 mm | 62 % | 0 |

- The maxima equal the claim's.
- Link 1a's bar dips up to 0.21 mm below the model strap, toward the skin; build.json's own `over_L1_min` is -0.209. That
  is inside 0.5 mm, but it is metal nearer the skin than the verified model.

**Hub heights.** The tops are F + 12.25 mm at J1 / J2 / J3 and F + 18.25 mm at K. All four hubs are O20, equal to the
model (CROWN 12.25, capK 6).

## 2. Every part has real size and a real component

**K clock spring:** a 0.3 x 5 strip, 215.2 mm long, 13 half-turns.

| fit | measured |
|---|---|
| spring to chamber wall | 0.043 mm |
| spring to arbor | 0.099 mm |
| spring to ring nut | 0.30 mm |
| magnet in its pocket | 0.024 mm |

Hand check with E = 190 GPa:
- rate = E b t^3 / (12 L) = 0.0099 N.m/rad;
- 0.08 N.m of preload needs 462 deg (1.28 turns) of pre-wind;
- the moment at stop B is 0.090 N.m, so the bending stress is 6M / (b t^2) = 1197 MPa. That is under the ~1400-1500 MPa
  static allowable of +C1900;
- coil budget: wound solid on the R2.5 arbor the strip takes about 8.9 turns, and about 4.7 against the R8 wall. That
  leaves 4.2 turns against the 1.44 needed.

**Stops.**
- K is an opposed pair of O3 dowels at homes 66 / 246 deg. The J2 stop is one dowel at 205 deg.
- Dowel to slot: 0.047 mm radial clearance in every slot. The press fits read 0.000-0.001 mm.
- The K slots in link 1a are clear of link 1a's strap root:
  - dowel centres sweep 9.3-66 and 189.3-246 deg;
  - the root window is 280-330 deg;
  - the clearance is 22 deg or more in my 5-deg bins (the claim says 17.2).
- The BDp finding is fixed.
- The J2 slot (178-314 deg) is 86 deg or more from link 1b's J2 root (40-90 deg).

**J2 push limit.** The arithmetic reproduces:
- 4.34 N.m = 2 x 280 N x 7.75 mm;
- 6 N.m gives 774 N, so s0 = 0.72;
- the dowel bending stress is about 410 MPa at the 1.4 mm lever, an SF of about 3.7.

Two caveats:
- C0 280 N is the repo's table value (`judge/fea.py` HW_V5), not re-sourced from a catalogue.
- Equal sharing across the pair is optimistic if the dowel's load line sits off the pair's centre.

**Knee stop at 149.5 deg.**
- The stop tooth is in both designs.
- Clips reach at most 131.58 deg (from the clip frames).
- **The R16 workspace set reaches 149.0 deg** (1094 closing poses, 3 at 148 deg or more): 0.5 deg from the stop, where the
  claim's own table gives 0.06 mm of tooth clearance. The claim quoted only the Bench(110,360) maximum (143.56).
- R16 reproduces with the tooth in, so the stop costs nothing there today. It has no margin, though.
- The claim's "0.68 mm at 143.6 deg" is the L1's figure. The CAD's knee_stop_check.json reads 0.50 there, where the thrust
  washer gap governs.

**R7.**
- Re-run locally: 41 of 41 custom STEP parts are valid single solids and `all_ok` is True.
- The output equals the committed file.
- Coverage: 41 custom parts (3 arm-fixed), none missing.

## 3. No lofts

**The trapped rebuild.**
- I rebuilt the full CAD to scratch in 569 s with `--skip-base-search`. The ear search is moot: no ear clears link 1a, and
  the base came out identical.
- These entry points were trapped: `cq.Workplane.loft / spline / splineApprox / interpPlate / parametricCurve /
  parametricSurface / sweep`, `cq.Solid.makeLoft`, `cq.Edge.makeSpline*`, `cq.Face.makeNSidedSurface` and
  `BRepOffsetAPI_ThruSections`.
- **0 loft and 0 ThruSections calls.**
- The only spline path is the same as BDp's: `user_style.hardware` -> `param_build.joint_parts` -> `cap_shape`, 4 calls.
  `hubs()` drops that cap, and no exported part is a G2 dome.
- The rebuild gives the same 86 parts with identical volumes. Its own check repeats the claim's: 9 poses, frames 8.7e-5 mm,
  joint features 0.1444 mm, dowels in their slots.

**B-spline faces in the STEP files.**

| part | B_SPLINE_SURFACE count | BDp |
|---|---|---|
| link 1a | 24 | none |
| link 1b | 54 | |
| link 2 | 210 | |
| D8-06 | 34 | |

- With no loft call in the run, these are OCC blends from the rounds and ring-root fillets, plus the user's BOTTOM.
- Link 1a's 24 are new since BDp. They come from the edge rounds on its one-profile fallback bar.
- I did not attribute them face by face.

## 4. The judges re-run (farm, $0.063; R7 local)

| requirement | claimed | re-run | how |
|---|---|---|---|
| R1 (2-14 mm) | 80.5 % | **80.5 %** (score_14mm.json byte-identical) | farm, step 3, 422 s |
| R1-aim (2-10 mm) | 47.2 % | **47.2 %** (score.json byte-identical) | same run |
| R4 (Raise overhead, 14 mm) | 71.0 % | **71.0 %** | same run |
| R6 | 0.0 mm | **0.0 mm** (1337 frames x 4064 pairs, 0 above 0.15 mm) | farm, step 1 |
| R16 | 74.0 % | **74.0 %** (358 poses; does not close 24.0 %, body 2.0 %, parts 0.0 %); identical to the tree | farm, step 4 |
| R7 | PASS | **PASS** (41 of 41) | local OCC |
| R17 (CAD) | FAIL, drift 9.35 | **FAIL**: M_GH 0.144 N.m, F 0.62 N, twist 4.68 deg, K drift **9.35 deg** | farm |
| R17 (L1) | FAIL, drift 9.28 | **FAIL**: 0.142 N.m, 0.62 N, 4.64 deg, **9.28 deg** | farm |

**R17 detail.**
- Both dynamics.json files equal the tree's in every value; only the order of the lock-clip lists and the timings differ.
- **Preload sensitivity on the CAD** (my run: nominal case, Reach a high shelf):

  | preload | rate 0.015 | rate 0.010 | L1 (claim) |
  |---|---|---|---|
  | 0.05 N.m | 5.04 deg, **FAIL** | 5.01 deg, **FAIL** | 4.96 / 4.93 deg, pass |

**R16 body contact is 2.0 % against BDp's 0.8 %.** This is the red team's extreme-pose contact (28 held-out contact poses
against 9), showing up in the built workspace.

## Corrections (none changes a requirement's status)

1. **R17 option "preload 0.05" fails on the CAD:** 5.04 / 5.01 deg against the 5.0 limit. The sweep in
   docs/research/gen4b_k_preload_sweep.json is the L1's. The remaining ways forward are:
   - accept and disclose the drift fail (K is sensed);
   - change K's law, for example less preload with a detent;
   - build BDp.
2. **Model metal outside the CAD beyond 0.5 mm:** E strap 0.62 mm, knee plate 1.70 mm. The claim's "<= 0.144 mm" covers
   only hubs, boss and pad.
3. **Link 1a's bar sits up to 0.21 mm below the model strap,** toward the skin.
4. **The R8 mass bug persists** (keyword materials, as BDp).
   - Link 1a is billed as NdFeB at 21.30 g; it is Ti at 12.58 g.
   - Links 1b and 2 are billed as steel at 26.78 and 36.05 g; they are Ti at 15.11 and 20.34 g.
   - Custom mass is 142.1 g, not 178.2.
   - **R8 is 203.7 g, not 239.8.** It still passes.
5. **design.json's note is stale** (copied from BDp).
   - It says K opens on 8 frames of one clip, dK <= 2.2 deg, and that R17 models K on stop A.
   - The clips actually open K on 116 frames: Reach a high shelf 77 frames to 15.82 deg, and Wash opposite shoulder 39
     frames to 6.19 deg.
   - R17 does model K, and K's drift is the fail.
6. **BDp catalogue corrections not carried over.**
   - "or wire EDM" is still on link 2's 4-strip bar. It is true only for the one-profile bars 1a and 1b.
   - The dowel is still "ISO 8734 O3 x 5.65". Use 3 x 6 and deepen the hole 0.35 mm, or grind it.
   - The magnet is still "O3 x 1.4". Use 3 x 1.5.
   - The discarded spline cap call still runs.
7. **The knee stop is 0.5 deg above R16's workspace maximum** (149.0 deg), not 6 deg as the bench-only figure suggests.

## Red team: open items (not judged; flagged)

- **New: K dowel 2's press hole sits under link 1b's strap root.**
  - The hole is at home 246 deg, spanning about 235-257 deg at r 6.25-9.25 in the K upper boss.
  - Link 1b's strap leaves its K pad at 225-275 deg (r 10.6-14).
  - The slot fix cleared link 1a's root, but the opposed dowel now sits under the upper member's root, with the ~0.75 mm
    walls to the rim and to the bearing seat noted for BDp.
  - Check it in R9 (FEA), or turn the pair about 30 deg. The slots stay clear of link 1a's root by 22 deg or more, but a
    turn must re-check it.
- **The spring-to-chamber-wall clearance is 0.043 mm.** Wall friction near stop A can add hysteresis to a K that already
  fails R17 by drift.
- **The R17 fail and the 1.04x hold margin at 0.05 N.m bracket K's spring law from both sides.** Too much preload: K lags
  its plan. Too little: K leaves stop A. A preload change cannot pass both with margin.
- **Still open, as disclosed:**
  - R9 and R10 not run;
  - 4 held-out poses past the knee stop not re-scored;
  - strap fidelity of links 1b and 2 (0.94 / 1.16 mm);
  - no ear clears link 1a.

Spend: $0.063 on the farm (R1 / R1-aim / R4, R6, R16, R17 for the CAD and the L1), no GPU. Local work stayed within 3
processes at nice 10.

# Independent check: user_slipper_nose (the generation-7 winner's full CAD)

Checker (a skeptic), 2026-10-17 15:15-15:45 UTC, inside the 45-min box. What I tested:
- the full CAD as committed at c93c86a (exo.glb md5 1fe4ba5a…, unchanged since db95242);
- its builder `pipeline/conformal/param_cad/user_style_slipper.py`;
- the L1 builder it imports, `pipeline/concept_l1/build_slipper_l1.py`.

**How I ran it.** I changed nothing in the design. The judges ran on a byte copy, `designs/vfy_slipper_nose` (exo.glb, clips,
workspace, design, build, parts_full, step/). The lead's 15:21 sweep commit (8f69bd6) picked that copy up, and this
commit removes it from the tree. Local runs only: niced, at most two of my processes at a time, one worker each. No farm
and no GPU, so the spend was $0.

**My scripts** are in the session scratchpad and are not committed:
- `kin_indep.py` is model-free. It reads only exo.glb, clips.json, workspace.json and build.json's law.
- `kin_vfy.py` runs the claim's SNModel (SN_CELL=lead, `build_slipper_l1.fit()`), posed by the model's OWN run state
  (no swap_in), against the CAD's parts.

## Verdict: NOT REFUTED on the numbers. Criterion (1) holds for the joints and the drive tip only, as disclosed.

- **Every judge I re-ran reproduces the scorecard to the digit:**
  - R1 81.1 %, R1-aim 47.4 %, R4 73.1 %;
  - R6 0.0 mm PASS;
  - R7 PASS (52 of 52 parts);
  - R16 64.2 %;
  - R17 PASS (all 19 dynamics cases identical).
- **The kinematics are the verified model's to 0.002 deg.** I checked the CAD's own bearings against the judged frames on all
  2356 frames, K against the law, and the crank against |dK| / g.
- **No loft or spline reaches an exported part.**
- **What still stands against the CAD's own goals** (all disclosed by the builder):
  - R1 is -0.94 against its own L1;
  - the bars are not within 0.5 mm of the model's straps (link 2 up to 2.08 mm, crank 7.5 mm, a model artefact);
  - the R17 forward bound at mu 0.15 sits on the 5.0 deg line, and it fails the judge's new unrounded gate (section 4).
- **Check (5) cannot be done: no stills exist** (no_render).

## 1. Posed parts against the verified model

**Model-free check (kin_indep.py).** I took the axis of each joint from the CAD's own bearing mesh: PCA of one bearing, rest
pose. I compared it with the relative rotation of the judged frames: 1019 closing workspace poses plus 1337 clip frames, 2356
frames in all.

| joint (bearing) | frames | axis deviation max | translation residual \|T_rel - (I - R_rel) c\| | angle range |
|---|---|---|---|---|
| J1 (MR117) | 2356 | 0.0009 deg | 0.0001 mm | -149.2..127.6 deg |
| K (MR117) | 2356 | 0.0014 deg | 0.0001 mm | -46.27..0 deg |
| J2 (MR117) | 2356 | 0.0012 deg | 0.0001 mm | -101.2..14.2 deg |
| J3 (MR117) | 2356 | 0.0018 deg | 0.0002 mm | -105.7..114.0 deg |
| crank pivot (683ZZ) | 2356 | 0.0010 deg | 0.0001 mm | -19.33..0 deg |

**Slaved coordinates.**
- K against the build.json law, as a function of q2: max error 0.0017 deg over 2356 frames. The law spans q2 -15.82..7.28 and
  dK down to -49.75.
- Crank angle / |dK| = 0.4178-0.4179 on 964 driven frames. That is 1/g, with g 2.3934, the model's law.
- On dwell frames the crank stays within 0.20 deg.
- Re-deriving 12 random closing workspace poses through the claim's own chain (D.ik): rotation entries match to 5e-7 and
  translations to 5e-5 mm.

**Joint limits and stops on the judged frames.**
- q2 runs from -14.21 to 101.18, inside the J2 stops at -15.82 / 102.07.
- dK reaches -46.27, inside stop B at -62.85; the drive's own end is -49.75.
- The knee angle runs 86.2-153.2 deg, inside the physical knee stop at 154.78 = 180 - ang_min. The workspace's margin to that
  stop is only 1.6 deg; the clips stay at or below 130.6.

**Model metal against the built solids (kin_vfy.py).**
- Seven distinct fit-bench poses, all taken:
  - arm at the side [-90, 0, 75];
  - highest / overhead [45, 165, -90];
  - behind the back [-90, 30, 105];
  - across the body [150, 45, -60];
  - the drive extreme [90, 120, -90] at dK -46.25;
  - the raise peak [30, 150, -60];
  - low front reach [15, 15, 30].
- Each part is rigid in its member frame, so the numbers are the same at every pose.
- "Outside" means the distance to the CAD part for samples NOT inside it (winding number). The builder's list uses the
  unsigned distance, which also counts samples buried inside the solid. Its "link 1a 1.12 mm" is all inside: the outside
  maximum is 0.000.

| model sample set | max outside | p95 | share > 0.5 mm | within 0.5? |
|---|---|---|---|---|
| L1a strap | 0.000 | 0.000 | 0 | yes |
| nose ("roller" samples) | 0.003 | 0.002 | 0 | yes |
| hub1 / hub3 / E boss / arm pad | 0.144 / 0 / 0 / 0 | ≤ 0.007 | 0 | yes |
| E strap | 0.524 | 0.477 | 3.9 % | no, by 0.02 |
| L1b strap | 0.705 | 0.583 | 11 % | no |
| flank lug ("horn") | 0.985 | 0.490 | 4.4 % | no |
| knee | 1.349 | 0.000 | 1.2 % | no (a few edge samples) |
| hub K / hub 2, slot bands included | 1.42 | 0.90 | 12-15 % | no: the model samples solid plate where the stop slots are cut |
| L2 strap | 2.082 | 0.950 | 29 % | **no** |
| crank | 7.535 | 6.785 | 32 % | **no**: the model artefact, its arm root inside link 1b's strap (gen-6 L1 7.12) |

**Direction of these misses.**
- Every miss on L1b, L2, the lug, E and the crank is OUTWARD.
- No sample is more than 0.5 mm outside with the CAD lying nearer GH than the model by more than 0.25 mm.
- So the built bars and crank ride higher than the model, which is what costs R1 its -0.94.
- Outward is not always safe. At overhead elevation 150-165, outward runs into the bunched tissue. R16's step-1 attribution
  has the build 0.5-1.4 mm deeper than the model on 7 poses, all of them already lost by the model at 1.07-8.50 mm.

**`kinematics_exact.all_within_0p5 = true` in build.json covers joint features and frames only.**
- The gen-6 check found the same; the gen-7 builder now discloses the per-part numbers in its issues.
- The flag's name still over-states the result.

## 2. Real size, real component

**Bought parts.** Mesh volumes match the catalogue envelopes:

| part | built volume | catalogue envelope |
|---|---|---|
| MR117-2RS 7x11x3 | 0.169 cm3 | 0.170 |
| 683ZZ 3x7x3 | 0.094 | 0.094 |
| MR63ZZ 3x6x2.5 | 0.053 | 0.053 |
| ISO 8734 O2.5 x 6 nose | 0.029 | 0.029 |
| O3 stop dowels faced to 5.65 | 0.040 | 0.040 |
| DIN 6799 RS 2.3 clip (O6 x 0.6, slot) | 0.012 | ≈ 0.012 |

- The knee is real: each pin carries 2 x MR63ZZ in an O9 x 5.5 boss, with a DIN 6799 clip and shims. The stop tooth sits at
  154.78.
- The fit-spec table in design.json covers the nose press, the pins, the bearing seats, the stop dowels, the lobe key and the
  running faces (carry-over (d) closed).

Small drawing items:
- (a) Knee pins "ISO 8734 3 m6 x 9.2". 9.2 mm is not a stock length (8 / 10), so it should read "10 faced to 9.2", as the
  stop dowels do.
- (b) The STEP set has no files for the stock pins, clips and shims (k 41, 43, 47, 48, 51, 55, 56). The spacer and the knee
  bearings are exported under truncated names (`44_pin_a.step` is the spacer). R7 still counts 52 custom parts with none
  missing.
- (c) The nose is the stock O2.5 (r 1.25), not the verified r 1.1839.
  - The verifier's r125 dump scores bench 18.49, the same as the claim (in-band10 0.5162 against 0.5163).
  - The law does not depend on the nose, so the judged frames stand.
  - The r 1.25 held-out wear is not on file.

User parts: TOP, MIDDLE, FOREARM CUFF and their hardware have the same 29 volumes as the gen-6 CAD. Only BOTTOM is cut (D8-06).

## 3. No lofts

I walked the import graph of user_style_slipper.py: 21 local modules.

**Loft and spline calls in that graph.**
- `param_build.makeLoft` appears twice: `strap_solid` and the neck. Both are called only from `param_build.main()`, and
  this builder never calls it.
- `param_build.cap_shape` has a 2-D `.spline` in a revolve profile. It is built inside `PB.joint_parts` → `US.hardware`,
  but `hubs()` drops every " cap " entry and builds the caps from `USM.cap_v5` tangent arcs / `cap_k_plain`.
- No exported part name carries "G2 dome".
- g2cad (Bezier and B-spline) is imported through cad_helpers but never called on this path.

**How the exported parts are made.**
- Links: line / tangent-arc sketches extruded, or `bar_swept` (one section on a line/arc path with a fixed binormal).
- Lobe ring: threePointArc chain extruded.
- Clock spring: half-turn arcs.
- Flank: a 4-arc section extruded.

Carry-over (c) is closed. `step_clean` runs the STEP round trip on all 58 parts, with `USM.sliver_free` on any part that has
zero-area faces. All 58 came back clean on the first round trip, so sliver_free was wired in but never triggered.

## 4. Re-run judges (local, current judges, same steps as the scorecard)

| Req | claim | re-run | match |
|---|---|---|---|
| R1 | 81.1 % | 81.1 % (score_design BANDS 10,14; 15.8 min) | yes |
| R1-aim | 47.4 % | 47.4 % | yes |
| R4 | 73.1 % | 73.1 % | yes |
| R6 | 0.0 mm | 0.0 mm (step 3: 451 frames x 6370 pairs; 0 violations) | yes |
| R7 | PASS | all_ok, 52 custom parts, none missing | yes |
| R16 | 64.2 % | 64.2 % (120 poses: closure fails 35.8 %, body 0, parts 0) | yes |
| R17 | PASS | PASS (nominal M_GH 0.129 N.m, F 0.58 N, twist 4.04 deg, K against its law 0.139, lift-off 0) | yes |

R17 notes:
- My run used dynamics.py as changed at 15:21 (8f69bd6), whose gates now compare unrounded values. The nominal twist is
  4.0425 deg, so it passes.
- All 19 per-case rows equal the committed file's.
- **The M5 forward bound at mu 0.15 (judge_m5/forward_bound_mu150.json) reads 5.00 rounded. The 15:17 audit reads it as
  5.00081 deg. Under the new unrounded gate that bound FAILS, by 0.0008 deg.**
  - It is a bound (preload and rate / eta), not the judged R17, and at mu 0.12 it reads 4.78.
  - It is still the design's thinnest number. The design's claim of "exactly the 5.0 limit" should read "fails the gate
    by 0.0008 deg at mu 0.15, passes at mu <= 0.12".

Working end (the drive pairs on the 116 workspace closing poses at |dK| 29.4-46.3): see the addendum below.

## 5. Stills

- No stills exist (no_render). The only image is the evolution snapshot (pipeline/evolution/user_slipper_nose/snapshot.png),
  a grey schematic, not a render.
- So I could not check the matte faceless mannequin, the no-black-parts rule, parts through the skin, or the look-audit fixes.
- The glb carries no materials; colours are assigned at render time.
- D8-06 is specified clear anodised, never black.

## Findings for the fix list (before any render)

1. **R1 -0.94 against the L1** (disclosed, re-measured). Section 1 shows where it comes from: link 2 has 29 % of its model samples
   more than 0.5 mm outside the bar (max 2.08). The L1b, lug and E misses are all outward. The builder's fix route
   (link 2 MARGIN 0; trim the E strap and the lug web to the L1 envelope) addresses exactly these.
2. **The R17 forward bound at mu 0.15 fails the new unrounded gate by 0.0008 deg.** Pass line mu <= 0.12, as the HANDOFF
   wear line (mu <= 0.105) already suggests.
3. **Running gaps of 0.086-0.123 mm** between the crank and links 1a / 1b / 2, with ISO 2768-f (+-0.05) on both faces.
   A worst-case stack of two faces is 0.10 mm, so the 0.086 mm crank to link 1b gap can close. The fix is ±0.02 on those
   faces or a gap of at least 0.15.
4. **The `all_within_0p5` flag is misleading** (joint features only). Rename it, or add the per-part outside table above.
5. **Knee stop margin on the workspace is 1.6 deg** (153.2 against 154.78). No judged frame touches it, but a red team of the
   stop's tolerance (tooth position ±) belongs on the drawing.
6. **Small drawing items:** the knee pins (non-stock length), and the STEP names and coverage of stock hardware.

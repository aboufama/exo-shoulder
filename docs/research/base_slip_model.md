# R10 for a girdle mount: the base slipping over the scapula

**Question.** The user decided (2026-10-15) that the base rides the scapula on their own scapula handler. R10 asks for
the worst-frame misalignment between the GH centre and the centre the chain carries, caused by the handler slipping
over the bone, at most 4 mm. Until now `judge/base_mount.py` said NOT RUN for a girdle mount. This note is the model
behind the number it now reports (`judge/base_slip.py`). It is a literature model. Nothing in it is fitted to a design.

**Result for the final design (cad_r18_n3_s1392_1_f300, every 7th frame of the 8 clips).** Central law: **15.2 mm
worst frame** (Raise overhead at 150 deg). p95 13.7 mm; 40 % of frames are over 4 mm. Low law 5.5 mm, high law 23.1 mm.
**R10 FAILS under all three laws.** Below 60 deg of elevation the central law is 4.3 mm, below 90 deg 6.8 mm, below
120 deg 9.6 mm. Per clip:

| clip | central law, worst frame (mm) |
|---|---|
| Raise overhead | 15.2 |
| Comb hair | 13.9 |
| Reach a high shelf | 11.9 |
| Wave (held out) | 7.5 |
| Drink from a cup | 4.3 |
| Wash opposite shoulder | 3.7 |
| Reach back pocket | 3.3 |
| Walking arm swing (held out) | 1.5 |

The number does not depend on the design. A spherical chain whose centre is fixed in the handler sees the handler's
slip in full, whatever its links look like. Only the handler (its grip and footprint), the motions, or a passive
slider can change R10. The rest of this note explains why the number is what it is.

## 1. Model

The handler is treated as a rigid body held on the skin over the flat of the acromion. The measured analogue is the
acromion marker cluster (AMC) of motion capture, or the acromion-mounted electromagnetic sensor. Relative to the bone
it slips in two ways:

- it rotates by small error angles about the three ISB scapula axes (Wu et al. 2005: Xs anterior, Ys superior, Zs
  lateral along the spine): internal/external rotation about Ys, upward rotation about Xs, posterior tilt about Zs;
- its centre A translates by d.

The chain's centre sits at the GH centre at rest and is fixed in the handler. It is carried to

    c = A + R_err (GH - A) + d,     misalignment = |(R_err - I) r + d|,     r = GH - A

Both GH and A ride the scapula, so the lever r is fixed in the scapula frame. The misalignment therefore depends only
on the error angles and on r.

- **Error angles.** These are published AMC-vs-bone errors, which depend on humerothoracic elevation and plane (below).
- **Lever r.** This comes from the OpenSim Seth 2016 scapula, using the model's own markers: acromial angle `aa`, AC
  joint `ac`, and the GH joint centre in the scapula body. They are expressed in the model's ISB scapula axes
  (`model_facts.json`, `frame_mapping`) and scaled by 1.093 to the rig's AC-GH distance (45.6 mm rig / 41.7 mm Seth).
  A = the midpoint of `aa` and `ac` (the flat of the acromion), which gives **r = (20.1, -34.0, 21.1) mm, |r| = 44.8 mm**.
- **Base position check.** The design's base part centroid is 57 mm from GH, on top of the acromion, which agrees with
  this lever.

## 2. Literature numbers (acromion skin sensor / cluster vs the bone)

| source | method | what it gives |
|---|---|---|
| Karduna et al. 2001, J Biomech Eng 123:184-190 (full text, Table 1; via gh_translation_literature.md section 7) | electromagnetic sensor on the acromion vs bone pins, n = 8 | RMS errors over the motions: upward rotation 4.4-6.3 deg, posterior tilt 6.6-8.6 deg, internal/external rotation 6.2-11.4 deg, growing "up to 25 degrees at maximal elevation"; good "especially below 120 degrees" |
| van Andel et al. 2009, Gait Posture | AMC vs scapula locator | <= 6 deg in flexion and abduction, 8.4 deg max in extreme positions; elevation should not exceed 100 deg |
| Lempereur et al. 2014, J Biomech (systematic review, 19 papers) | AMC, single calibration at rest | ~5 deg (flexion) and ~7 deg (abduction) accuracy below 90-100 deg elevation |
| Warner et al. 2015, J Vis Exp | AMC | valid to 120 deg; above that "the measurement error becomes too large" |
| McQuade & Smidt 1998 (as cited by Matsui et al. 2006; not re-read) | acromial module | 4.2 mm skin slippage |
| Matsui et al. 2006, J Orthop Sci | MRI, skin markers vs bone | the acromion marker deviated least (the abstract's "39 mm" is most likely 3.9 mm; verify in the full text) |

## 3. Three laws

All three are in `judge/base_slip.py`. Elevation e and plane p are taken from the clip's "want" pose (the person's
motion). p runs from 0 (abduction) to 90 (flexion).

- **central (R10's number).**
  - Below 100 deg: the error is 0 with the arm hanging (the handler is fitted there, as an AMC is calibrated) and grows
    linearly to 7 deg (abduction) .. 5 deg (flexion) on every axis at 100 deg (Lempereur).
  - 100 to 120 deg: linear to Karduna's per-axis RMS upper ends (UR 6.3, PT 8.6, IR/ER 11.4 deg).
  - 120 to 150 deg: IR/ER rises linearly to 25 deg (Karduna's maximum); UR and PT stay where they are.
  - Translation: |d| = 4.2 mm x min(e, 150)/150.
  - The axes are combined root-sum-square, as independent errors.
- **low (optimistic).** The review's best case: from 0 at rest to 5 deg on every axis at 100 deg, held there with no
  growth overhead, and no translation. RSS.
- **high (upper bound).**
  - The central angles, read as biases that are already present just above rest (no ramp from 0).
  - Combined with the worst signs: exact ISB Y-X-Z composite rotation, all 8 sign patterns.
  - The translation is added in the worst direction.

Error angles and the resulting misalignment (mm, lever above):

| plane | elev | UR | IR/ER | PT | slip | central | low | high |
|---|---|---|---|---|---|---|---|---|
| 0 | 30 | 2.1 | 2.1 | 2.1 | 0.8 | 2.5 | 1.7 | 10.5 |
| 0 | 60 | 4.2 | 4.2 | 4.2 | 1.7 | 4.9 | 3.3 | 11.3 |
| 0 | 90 | 6.3 | 6.3 | 6.3 | 2.5 | 7.4 | 5.0 | 12.1 |
| 90 | 90 | 4.5 | 4.5 | 4.5 | 2.5 | 5.6 | 5.0 | 9.4 |
| 0 | 120 | 6.3 | 11.4 | 8.6 | 3.4 | 10.0 | 5.5 | 15.7 |
| 0 | 150 | 6.3 | 25.0 | 8.6 | 4.2 | 15.2 | 5.5 | 23.1 |

**Worst frame (Raise overhead, plane 30 / elevation 150 / axial -60): 15.2 mm.** The components are:

- UR 4.4 mm;
- IR/ER 12.6 mm;
- PT 5.9 mm;
- slip 4.2 mm.

IR/ER about the superior axis dominates overhead. The lever is mostly inferior, but its 29 mm anterior-lateral
component swings with that rotation.

## 4. Checks

`python3 judge/base_slip.py` runs the self-checks:

- one axis at a time against 2|r| sin(a/2);
- a rotation about an axis parallel to the lever moves nothing;
- zero lever leaves only the slip;
- zero at the fitting posture;
- the symmetry of equal angles;
- low <= central <= high.

All pass.

The numbers agree with the back-of-envelope in gh_translation_literature.md section 7: "4-8 mm below 100-120 deg,
about 20 mm above".

**Anchor sensitivity (central law, worst frame).**

| A on | mm |
|---|---|
| the AC joint | 13.8 |
| the flat of the acromion | 15.2 |
| the acromial angle | 21.6 (longer lever) |

## 5. Uncertainty and what is not in the model

- **No data for a rigid saddle.** The handler is the user's own part and its footprint is unknown here. A rigid saddle
  gripping the acromion and the scapular spine, with a larger base over bony landmarks, plausibly tracks better than a
  5 cm AMC. No published number exists for one. The low law is the only allowance for that, and even it fails above
  ~90 deg (5.0-5.5 mm).
- **Means, not worst subjects.** The literature errors are RMS and mean differences over subjects, so the worst subject
  is worse.
- **Planes outside 0-90 deg are clamped.** Cross-body (Wash opposite shoulder, ~140 deg) and behind the back (Reach back
  pocket, < 0) have no AMC validation. van Andel's 8.4 deg maximum was in "extreme positions", so these clips are
  probably understated.
- **Elevation above 150 deg** is held at the 150 deg values.
- **Linear translation slip.** It is assumed to grow linearly with elevation, and its direction is unknown, so it adds
  in RSS (central) or in the worst direction (high).
- **Not in R10's definition, but on top of it:**
  - GH translation inside the glenoid, 2.9-4.3 mm during elevation (Dal Maso 2015, bone pins; gh_translation_literature.md
    section 5).
  - Slip of the handler under load. MVP1 is unpowered, so the load is small. The MVP2 assist reaction could rotate a
    skin-held saddle by 3-10 deg at 10 N.m (sim_to_real_gaps.md: 2.7-8 mm at the GH).
- **Static, not dynamic.** Static AMC errors are used. Dynamic errors (Karduna is dynamic) are of the same order.

## 6. What could move R10, in the order a skeptic would ask for it

1. **Measure the user's own handler.** Mount markers on the handler and on palpated bony landmarks (AA, TS, AI), with
   OpenCap plus a scapula locator at 3-4 static elevations, or use the double-calibration method (Brochard et al. 2011).
   That replaces this literature law with the user's own data.
2. **A torque-free passive slider (the user's exception).** Put it on the handler along the dominant error direction.
   The best single direction is (0.56, 0.01, -0.83) in ISB scapula axes, anterior-medial in the scapular plane. A
   numerical search over 4000 directions puts it there, and it cuts the central worst frame from 15.2 to 7.0 mm. It is
   still over 4 mm, so it is not a fix on its own. **Update 2026-10-15 (`judge/base_stage.py`, design side; this model
   unchanged):** 7.0 mm assumes the slider is set perfectly. Set by the arm through the chain's closure (the only thing
   that can set it), it is 10 mm: an arm brace knows the GH centre along the humerus only (Hamming 2012 cuff errors 0-4
   deg on a 325 mm lever). A 3-axis stage set by a spring-loaded follower on the lateral acromion (bone, 32 mm above GH)
   removes the IR/ER swing: 7.3 mm. With the user's systematic slip calibrated out (f ~ 0.32, double-calibration
   literature) it is **2.3 mm** (4.6 mm if only the angles are repeatable). No uncalibrated skin reference passes:
   the 4.2 mm slip at 150 deg is over 4 mm on its own. Table and caveats in docs/FINDINGS.md ("R10 on the scapula
   handler").
3. **A threshold change.** That is the user's call, never the agent's. 4 mm is "half the 2-10 mm band", and the user
   confirmed it on 2026-10-15.

## References

- Karduna AR, McClure PW, Michener LA, Sennett B (2001). Dynamic measurements of three-dimensional scapular kinematics:
  a validation study. J Biomech Eng 123:184-190.
- van Andel C, van Hutten K, Eversdijk M, Veeger D, Harlaar J (2009). Recording scapular motion using an acromion
  marker cluster. Gait Posture 29:123-128.
- Lempereur M, Brochard S, Leboeuf F, Rémy-Néris O (2014). Validity and reliability of 3D marker based scapular motion
  analysis: a systematic review. J Biomech 47:2219-2230.
- Warner MB, Chappell PH, Stokes MJ (2015). Measurement of dynamic scapular kinematics using an acromion marker cluster
  to minimize skin movement artifact. J Vis Exp 96:51717.
- Matsui K, Shimada K, Andrew PD (2006). Deviation of skin marker from bone target during movement of the scapula.
  J Orthop Sci 11:180-184.
- McQuade KJ, Smidt GL (1998). Dynamic scapulohumeral rhythm: the effects of external resistance during elevation of
  the arm in the scapular plane. J Orthop Sports Phys Ther 27:125-133 (cited via Matsui 2006).
- Brochard S, Lempereur M, Rémy-Néris O (2011). Double calibration: an accurate, reliable and easy-to-use method for 3D
  scapular motion analysis. J Biomech 44:751-754.
- Wu G et al. (2005). ISB recommendation on definitions of joint coordinate systems of various joints for the reporting
  of human joint motion - Part II: shoulder, elbow, wrist and hand. J Biomech 38:981-992.
- Seth A, Matias R, Veloso AP, Delp SL (2016). A biomechanical model of the scapulothoracic joint to accurately capture
  scapular kinematics during shoulder movements. PLoS One 11:e0141028 (model in .cache/ext/seth2016, licence accepted by
  the user; facts in pipeline/girdle/opensim_seth/model_facts.json).
- Dal Maso F et al. (2015). Glenohumeral translations during range-of-motion movements, activities of daily living, and
  sports activities in healthy participants. Clin Biomech 30:1002-1007.

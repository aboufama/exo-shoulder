# GH-centre translation vs the thorax from OpenSim: Seth et al. 2016 model driven by published shoulder rhythm

Research note, 2026-10-14. It runs the generic Seth et al. 2016 scapulothoracic shoulder model in OpenSim 4.6, drives the
clavicle and scapula with the published mean Ludewig 2009 angles, and records the GH centre in the thorax. The result is a
third girdle law next to the rig's (`pipeline/avg/body_pose.py` `segs()`) and the teammate's rigid chain
(`pipeline/girdle/girdle.py` `lift_literature`, from `docs/research/gh_translation_literature.md`).

Nothing was downloaded. The model was already in `.cache/ext/seth2016/` with the user's approval and licence acceptance.
scipy 1.17.1 was pip-installed into the isolated OpenSim venv. No repo file outside `pipeline/girdle/opensim_seth/` and this
note was changed.

**Conventions.** Same as the teammate's note:

- Frame: ISB thorax, mm, **x anterior, y superior, z lateral (right)**, right shoulder.
- theta = humerothoracic elevation (deg). p = ISB plane of elevation: 0 abduction, 40 scaption, 90 flexion.
- Displacements are from the plane's arm-hanging (0 deg) posture, as in `lift_literature`.
- `*` marks rows where the published angle curves are extrapolated: below 15 deg, and beyond the last data point
  (abduction 135, scaption 138, flexion 132 deg).

---

## 1. Result (primary settings)

Settings: equal angle weights; girdle coordinate ranges relaxed (section 2.4). GH displacement in mm, ant / sup / lat;
negative = posterior / inferior / medial.

| Plane | 30 deg | 60 deg | 90 deg | 120 deg | 150 deg * |
|---|---|---|---|---|---|
| abduction | -5.5 / 7.7 / -0.2 | -8.7 / 18.7 / -1.8 | **-10.2 / 28.9 / -4.9** | **-11.1 / 40.9 / -10.6** | -13.2 / 51.0 / -18.4 |
| scaption | 3.0 / 7.4 / 1.0 | 2.0 / 17.4 / -0.2 | **0.5 / 25.5 / -2.8** | **-4.6 / 35.5 / -7.2** | -10.7 / 46.2 / -15.5 |
| flexion | 1.5 / 1.7 / 0.4 | 3.7 / 11.6 / -0.8 | **4.1 / 20.3 / -3.6** | **-5.8 / 26.3 / -7.0** | -21.9 / 36.1 / -14.5 |

Against the other two laws, at 90 and 120 deg (from `compare.py`):

| Plane | theta | Seth (OpenSim) | rig `segs()` | `lift_literature` | Seth - rig (abs) | Seth - lit (abs) | Seth x 1.224 (rig size) |
|---|---|---|---|---|---|---|---|
| abduction | 90 | -10.2 / 28.9 / -4.9 | 0 / 12.7 / 0 | -24.6 / 37.9 / -22.0 | -10.2 / 16.2 / -4.9 (19.8) | 14.4 / -9.0 / 17.1 (24.1) | -12.5 / 35.3 / -6.0 |
| abduction | 120 | -11.1 / 40.9 / -10.6 | 0 / 19.0 / 0 | -24.4 / 49.2 / -27.7 | -11.1 / 21.8 / -10.6 (26.7) | 13.4 / -8.3 / 17.1 (23.2) | -13.6 / 50.0 / -12.9 |
| scaption | 90 | 0.5 / 25.5 / -2.8 | 0 / 12.7 / 0 | -5.1 / 35.6 / -12.2 | 0.5 / 12.9 / -2.8 (13.2) | 5.7 / -10.1 / 9.4 (14.9) | 0.6 / 31.2 / -3.4 |
| scaption | 120 | -4.6 / 35.5 / -7.2 | 0 / 19.0 / 0 | -10.4 / 45.7 / -18.2 | -4.6 / 16.5 / -7.2 (18.6) | 5.8 / -10.2 / 11.0 (16.1) | -5.6 / 43.4 / -8.8 |
| flexion | 90 | 4.1 / 20.3 / -3.6 | 0 / 12.7 / 0 | -5.0 / 24.2 / -10.7 | 4.1 / 7.6 / -3.6 (9.4) | 9.1 / -3.9 / 7.1 (12.2) | 5.1 / 24.9 / -4.4 |
| flexion | 120 | -5.8 / 26.3 / -7.0 | 0 / 19.0 / 0 | -12.2 / 35.9 / -17.2 | -5.8 / 7.3 / -7.0 (11.7) | 6.4 / -9.6 / 10.2 (15.4) | -7.1 / 32.2 / -8.6 |

The three laws compare as follows:

- **Superior:** Seth lies between the rig and `lift_literature`. At 90 deg it is 1.6-2.3x the rig and 0.71-0.84x
  `lift_literature`.
- **Medial:** Seth shows 3-5 mm at 90 deg and 7-11 mm at 120 deg. `lift_literature` shows 11-22 and 17-28 mm.
- **Posterior:** Seth shows 10-11 mm in abduction. `lift_literature` shows 24-25 mm. In scaption and flexion Seth stays
  within +-6 mm up to 120 deg.
- **Size:** scaling by the girdle-size ratio (rig SC-GH 170.5 mm / Seth 139.3 mm = 1.224) gives superior values within
  0.7-4.4 mm of `lift_literature` at 90-120 deg. AP and ML still differ by 5-16 mm.

Why the difference to `lift_literature`: an exact decomposition, step by step (section 4).

| Plane, 90 deg | `lift_literature` -> chain (quadratic-fit error) | clavicle 154 -> 125.2 mm | AC-to-GH vector rig -> Seth | angle residuals of the constrained model | chain -> OpenSim | total Seth - lit |
|---|---|---|---|---|---|---|
| abduction | 1.0 / -0.3 / 0.2 | 6.9 / -3.6 / 5.4 | 0.5 / -2.9 / 0.7 | 5.9 / -2.3 / 11.0 | 0.1 / 0.0 / -0.1 | 14.4 / -9.0 / 17.1 |
| scaption | 0.3 / -0.8 / 0.3 | 4.0 / -3.2 / 2.8 | 0.1 / -2.8 / 0.9 | 1.2 / -3.3 / 5.5 | 0.0 / 0.0 / -0.1 | 5.7 / -10.1 / 9.4 |
| flexion | 3.4 / 1.2 / 0.4 | 3.8 / -1.5 / 1.8 | 0.0 / -2.7 / 1.1 | 2.0 / -0.8 / 3.9 | 0.0 / 0.0 / -0.1 | 9.1 / -3.9 / 7.1 |

The table is usable as a law: `pipeline/girdle/opensim_seth/gh_seth.json` keys `planes_deg` [0, 40, 90], `elev_deg`
[0..150 step 10], `gh_mm` [plane][elev][ant, sup, lat], `extrapolated`. `seth_law.py` `lift_seth(P, variant, scale)`
interpolates it bilinearly (numpy only; runs in the repo's python).

---

## 2. Method

### 2.1 Model, loading

- Model: `.cache/ext/seth2016/x/ShoulderModel/ScapulothorachicJoint_Shoulder.osim`, OpenSim 3.2 format (XML version 30000).
- It loads **unchanged** in OpenSim 4.6 (4.6-2026-06-22). OpenSim upgrades the XML in memory: joints move into the
  JointSet with offset frames, and the 3.2 plugin's `ScapulothoracicJoint` maps onto OpenSim 4.6's built-in class. No
  converted copy was needed, so `.cache/ext/seth2016/converted/` was not created.
- The only load messages: 27 hand-bone `.vtp` display files are missing (hand display only), and two harmless component-set
  renames.
- One in-memory change, for the primary run only: the six girdle coordinates get the range +-90 deg with `clamped = false`
  (section 2.4). The file on disk is never edited.

**Check (a): built-in joint = plugin.** I re-implemented the plugin's `addToSystem` (from
`ScapulothoracicJointPlugin/source/ScapulothoracicJoint.cpp`) in numpy. Its chain is:

- a Simbody `Ellipsoid` mobiliser, with the x/y radii swapped and an extra +90 deg about z on both frames;
- a winging `Pin`, about the axis (-sin d, cos d, 0) through the winging origin;
- a `Weld` to the scapula.

That reproduces OpenSim 4.6's scapula pose at 200 random coordinate sets to 3e-13 (mm and rotation-matrix units). This
holds with Simbody's ellipsoid point mapping p = (a n_x, b n_y, c n_z), n = the M frame's z axis. On that mapping the
contact point lies exactly on the ellipsoid, but z is only approximately the surface normal. The scapula contact point
satisfies (x/a)^2 + (y/b)^2 + (z/c)^2 = 1.000000.

### 2.2 Model facts (`model_facts.py` -> `model_facts.json`)

| Item | Value |
|---|---|
| Bodies | ground, thorax (20 kg), clavicle, scapula, humerus, ulna, radius, hand |
| ground_thorax | CustomJoint, 6 coordinates, all locked at 0 (thorax = ground) |
| sternoclavicular | CustomJoint, universal: `clav_prot` about (0.0153, 0.9893, -0.1451), then `clav_elev` about (-0.9945, 0, -0.1050) (clavicle frame). SC at (6.3, 6.9, 25.5) mm from IJ (model thorax frame). No axial rotation. |
| scapulothoracic | ScapulothoracicJoint: `scapula_abduction`, `scapula_elevation`, `scapula_upward_rot` (Euler angles of the ellipsoid mobiliser) and `scapula_winging` (pin) |
| Ellipsoid | radii x / y / z = 70 / 150 / 70 mm; centre (-20, -17.3, 70) mm in the thorax, rotated -0.87 rad about y; winging axis origin (0, 0), direction 0 rad |
| Scapula offset frame | (-59.82, -39.04, -56.0) mm, body-XYZ (-0.5181, -1.1416, -0.2854) rad (= the `ScapulaThoracicContactPt` marker) |
| glenohumeral | CustomJoint, scapula -> humerus: `shoulder_elv` about (-0.993, -0.079, 0.088), then `plane_of_elev` about (0.083, 0.065, 0.994), then `axial_rot` about (-0.085, 0.995, -0.058); no translations; joint at (-9.55, -34.0, 9.0) mm in the scapula |
| Coordinate ranges | `clav_prot`, `clav_elev`, `scapula_abduction`, `scapula_elevation`, `scapula_upward_rot`: +-45 deg, clamped. `scapula_winging`: +-45 deg, not clamped. `shoulder_elv`: -90..145 deg. `plane_of_elev`: -90..180 deg. `axial_rot`: +-180 deg. All defaults 0, except `shoulder_elv` 10 deg. |
| Soft limits | `CoordinateLimitForce` (dynamics only): `clav_elev` -20..25 deg, `clav_prot` -10..25 deg, `scapula_upward_rot` -20..50 deg, `shoulder_elv` -85..180 deg |
| AC constraint | `PointConstraint` "AC": clavicle point (-29.24, 20.24, 120.05) mm == scapula point (-13.57, 0.11, -15.23) mm, removing 3 DOF |
| Girdle DOF | 6 coordinates - 3 = **3 DOF** |
| Markers (bony landmarks) | thorax ij, c7, t8, px; clavicle sc (origin), acc; scapula ac, aa, ts, ai; humerus gu (origin), EpL, EpM |
| Default posture (after `initSystem` assembly) | clavicle retraction 10.4 / elevation 8.1; scapula IR 42.6 / UR -9.4 / PT -9.6 deg (ISB, section 2.3) |

**Check (b): GH centre = humerus origin.** The humerus origin stays at (-9.55, -34.0, 9.0) mm in the scapula frame over 50
random GH postures (motion 0.0 mm); this equals the GH joint location in the scapula. The marker `gu` sits at the humerus
origin. A sphere fit of the humeral-head cap of `humerus.vtp` (59 vertices) gives the centre 2.0 mm from the origin,
r 23.4 mm, rms 1.6 mm.

**Girdle geometry, Seth vs rig.**

| Quantity | Seth | Rig |
|---|---|---|
| SC to AC joint centre (clavicle length) | 125.2 mm | 156.4 mm (`lift_literature` uses 154 mm) |
| SC to `acc` marker | 121.8 mm | - |
| AC-to-GH vector, ISB thorax, at the Table I rest fit | (12.5, -35.1, 19.4) mm, abs 42.0 | (16.2, -34.9, 24.5) mm, abs 46.0 |
| SC to GH, at the Table I rest fit | 139.3 mm | 170.5 mm |
| IJ to GH, default posture | 161.6 mm | 190.6 mm |

### 2.3 Frames and angle conventions (ISB, Wu et al. 2005)

All ISB frames are built from the model's own landmark markers, so the model's body-frame conventions do not enter the
angles.

- **Thorax.** Origin IJ. Yt runs from mid(PX, T8) to mid(IJ, C7). Zt is normal to the (IJ, C7, mid(PX, T8)) plane, pointing
  right. Xt = Yt x Zt.
  - The ISB thorax is the model thorax frame rotated **+7.86 deg about z** (Yt leans posteriorly).
  - Results are given in the ISB frame. The model-frame vectors are in `gh_mm_model_thorax`.
  - Example, abduction 90 deg: ISB (-10.2, 28.9, -4.9), model frame (-14.1, 27.2, -4.9).
- **Clavicle.** Zc runs from SC to AC (markers `sc`, `acc`). Xc is perpendicular to Zc and Yt.
  - Angles: Y-X-Z vs the thorax. Retraction = -(1st), elevation = -(2nd).
  - Only the Zc direction enters. The model has no clavicle axial rotation, and that does not move the AC.
- **Scapula.** Origin AA. Zs runs from TS to AA. Xs = (AA - TS) x (AI - TS), pointing anterior. Ys = Zs x Xs.
  - Angles: Y-X-Z vs the thorax. Internal rotation = +(1st), upward rotation = -(2nd), posterior tilt = +(3rd).
  - These are Ludewig's reporting signs, as in the teammate's chain.
  - The ISB scapula frame is the scapula body frame rotated by a fixed 28.6 deg.
- **Humerus.** Yh runs from mid(EpL, EpM) to GH. Xh is normal to the (EpL, EpM, GH) plane, pointing anterior. Zh = Xh x Yh.
  - Angles: Y-X-Y vs the thorax. Plane = 1st, elevation = -(2nd).
  - The ISB humerus frame is the humerus body frame rotated by a fixed 2.3 deg.
- **Sign check.** At the fitted rest, the model reaches IR 38.5 / UR 3.4 / PT -6.9 deg against the targets 41.1 / 5.4 /
  -13.5. Every residual is below 7 deg with the same signs as the targets.

### 2.4 Driving the model (`run_seth_gh.py` -> `gh_seth.json`)

**Inputs.**

- The Ludewig 2009 bone-pin means, read off Fig. 5-A / 5-C [F]. These are the same numbers and the same interpolation as
  the teammate's chain, copied unchanged into `ludewig2009.py`.
- Below 15 deg: the 15-30 deg slope is extrapolated. Beyond the end of range: the last segment is extrapolated.
- The arm-hanging (0 deg) posture is that extrapolation. Table I relaxed standing is reported as an alternative anchor.

**Girdle fit.** For each plane and theta (0..150 deg, 10 deg steps, continuation from the previous posture):

- `scipy.optimize.least_squares` over the 6 girdle coordinates.
- Residuals: the 5 angle errors (deg, weight 1), plus the AC constraint error x 100 per mm.
- Then OpenSim `Model.assemble` closes the AC constraint exactly.
- The AC error at the end is <= 2e-12 mm in every primary posture, and <= 3e-8 mm in the clamped variant.

**Humerus.** `shoulder_elv` and `plane_of_elev` are solved so that the humerus long axis has the target ISB plane and
elevation (direction error < 1e-4 deg), with `axial_rot` = 0 (the model's neutral). This does not move the GH centre
(check (b)). The girdle depends only on elevation, as in the published curves.

**Outputs.** GH = humerus origin; also the AC joint centre (clavicle side), the clavicle tip (`acc`) and the acromial angle
(`aa`), all in the ISB thorax.

**Variants.**

| Variant | Weights (ret, elev, IR, UR, PT) | Coordinate ranges |
|---|---|---|
| primary | 1, 1, 1, 1, 1 | girdle relaxed to +-90 deg, unclamped |
| clamped | 1, 1, 1, 1, 1 | as distributed (+-45 deg) |
| w_clav | 10, 10, 1, 1, 1 | relaxed |
| w_scap | 1, 1, 10, 10, 10 | relaxed |

Why relax the ranges: the published upward rotation needs `scapula_upward_rot` = 45.2-46.1 deg at 90 deg elevation (all
three planes), 55-59 deg at 120 deg and 68-71 deg at 150 deg. The distributed clamp stops it at 45 deg. That +-45 deg (+-0.785
rad) is the same range given to all six girdle coordinates, and the model's own soft limit for upward rotation starts at
50 deg.

**Runtime.** About 13 s, one process.

---

## 3. Results in detail

### 3.1 GH displacement, full table (primary; `gh_seth.json` `gh_mm`)

| theta | abduction (p = 0) | scaption (p = 40) | flexion (p = 90) |
|---|---|---|---|
| 0 * | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| 10 * | -1.9 / 2.3 / 0.1 | 1.0 / 2.2 / 0.5 | 0.5 / 0.4 / 0.2 |
| 20 | -4.2 / 4.5 / -0.1 | 3.1 / 3.9 / 0.9 | 0.7 / 0.7 / 0.4 |
| 30 | -5.5 / 7.7 / -0.2 | 3.0 / 7.4 / 1.0 | 1.5 / 1.7 / 0.4 |
| 40 | -6.7 / 11.2 / -0.6 | 2.7 / 10.9 / 0.8 | 2.9 / 5.4 / 0.1 |
| 50 | -7.8 / 15.1 / -1.1 | 2.7 / 14.7 / 0.4 | 3.6 / 8.8 / -0.3 |
| 60 | -8.7 / 18.7 / -1.8 | 2.0 / 17.4 / -0.2 | 3.7 / 11.6 / -0.8 |
| 70 | -9.3 / 21.7 / -2.6 | 1.6 / 20.3 / -0.9 | 3.9 / 15.3 / -1.6 |
| 80 | -9.9 / 25.0 / -3.6 | 1.1 / 23.2 / -1.8 | 3.9 / 18.4 / -2.6 |
| 90 | -10.2 / 28.9 / -4.9 | 0.5 / 25.5 / -2.8 | 4.1 / 20.3 / -3.6 |
| 100 | -10.5 / 32.9 / -6.4 | -0.1 / 28.8 / -4.0 | 3.4 / 23.4 / -4.8 |
| 110 | -10.6 / 37.3 / -8.4 | -0.8 / 31.6 / -5.2 | 1.6 / 26.2 / -6.2 |
| 120 | -11.1 / 40.9 / -10.6 | -4.6 / 35.5 / -7.2 | -5.8 / 26.3 / -7.0 |
| 130 | -11.7 / 44.3 / -12.9 | -6.2 / 39.0 / -9.7 | -10.7 / 30.3 / -9.4 |
| 140 * | -12.4 / 47.6 / -15.6 | -8.2 / 42.5 / -12.5 | -16.3 / 33.2 / -11.8 |
| 150 * | -13.2 / 51.0 / -18.4 | -10.7 / 46.2 / -15.5 | -21.9 / 36.1 / -14.5 |

The flexion step from 110 to 120 deg (AP +1.6 -> -5.8 mm) follows the input: Ludewig's flexion retraction jumps from 28 to
32 deg and IR drops from 47.5 to 43.5 deg between 110 and 120 deg [F].

### 3.2 Angle residuals (target - reached is negative when the model reaches less; deg, ret / elev / IR / UR / PT)

| Plane | theta | target | reached | residual | RMS |
|---|---|---|---|---|---|
| abduction | 0 * | 23.0 / 11.0 / 32.0 / 6.0 / -14.5 | 21.0 / 14.3 / 30.4 / 4.8 / -10.2 | -2.0 / 3.3 / -1.6 / -1.2 / 4.3 | 2.7 |
| abduction | 30 | 31.0 / 14.0 / 31.0 / 15.0 / -10.5 | 25.8 / 15.7 / 27.6 / 15.1 / -6.9 | -5.2 / 1.7 / -3.4 / 0.1 / 3.6 | 3.3 |
| abduction | 60 | 37.0 / 17.0 / 30.5 / 25.0 / -6.0 | 30.0 / 18.1 / 26.4 / 26.1 / -3.3 | -7.0 / 1.1 / -4.1 / 1.1 / 2.7 | 3.9 |
| abduction | 90 | 41.0 / 18.5 / 30.5 / 34.5 / -1.5 | 33.5 / 19.9 / 26.4 / 36.0 / 0.9 | -7.5 / 1.4 / -4.1 / 1.5 / 2.4 | 4.1 |
| abduction | 120 | 44.0 / 19.5 / 30.8 / 46.0 / 4.0 | 37.4 / 21.8 / 27.6 / 47.3 / 6.2 | -6.6 / 2.3 / -3.2 / 1.3 / 2.2 | 3.6 |
| abduction | 150 * | 46.2 / 19.6 / 30.3 / 58.0 / 10.3 | 41.6 / 22.6 / 28.5 / 58.7 / 12.3 | -4.6 / 3.0 / -1.8 / 0.7 / 2.0 | 2.7 |
| scaption | 0 * | 22.0 / 9.0 / 35.5 / 6.0 / -15.5 | 19.3 / 13.6 / 33.2 / 4.2 / -9.5 | -2.7 / 4.6 / -2.3 / -1.8 / 6.0 | 3.8 |
| scaption | 30 | 25.0 / 12.0 / 38.5 / 15.0 / -10.5 | 21.0 / 15.0 / 35.3 / 14.2 / -5.9 | -4.0 / 3.0 / -3.2 / -0.8 / 4.7 | 3.4 |
| scaption | 60 | 29.0 / 14.5 / 39.0 / 25.0 / -6.0 | 24.3 / 17.0 / 35.6 / 24.8 / -2.1 | -4.7 / 2.5 / -3.4 / -0.2 / 3.9 | 3.3 |
| scaption | 90 | 32.0 / 15.5 / 39.0 / 34.0 / -1.5 | 27.5 / 18.1 / 36.0 / 33.9 / 2.0 | -4.5 / 2.6 / -3.0 / -0.1 / 3.5 | 3.1 |
| scaption | 120 | 36.5 / 17.0 / 37.0 / 43.0 / 2.5 | 32.1 / 19.8 / 34.4 / 43.1 / 5.5 | -4.5 / 2.8 / -2.6 / 0.1 / 3.0 | 3.0 |
| scaption | 150 * | 41.1 / 18.2 / 34.7 / 55.7 / 11.2 | 37.9 / 20.2 / 33.2 / 56.1 / 12.6 | -3.2 / 1.9 / -1.5 / 0.4 / 1.4 | 1.9 |
| flexion | 0 * | 17.0 / 11.0 / 41.5 / 6.0 / -15.0 | 14.8 / 14.9 / 39.3 / 4.4 / -10.0 | -2.2 / 3.9 / -2.2 / -1.6 / 5.0 | 3.2 |
| flexion | 30 | 21.0 / 10.0 / 44.5 / 15.0 / -10.0 | 17.3 / 13.8 / 41.0 / 13.6 / -4.3 | -3.7 / 3.9 / -3.5 / -1.4 / 5.7 | 3.9 |
| flexion | 60 | 23.0 / 12.5 / 46.5 / 24.5 / -5.5 | 19.3 / 15.9 / 43.0 / 23.4 / -0.7 | -3.7 / 3.4 / -3.5 / -1.1 / 4.8 | 3.5 |
| flexion | 90 | 25.5 / 14.0 / 48.0 / 33.5 / -0.5 | 21.8 / 17.2 / 44.7 / 32.9 / 3.6 | -3.7 / 3.2 / -3.3 / -0.6 / 4.1 | 3.2 |
| flexion | 120 | 32.0 / 14.5 / 43.5 / 42.0 / 5.0 | 28.0 / 17.0 / 40.7 / 42.0 / 7.9 | -4.0 / 2.5 / -2.8 / -0.0 / 3.0 | 2.8 |
| flexion | 150 * | 39.8 / 15.9 / 33.9 / 54.0 / 13.0 | 37.2 / 17.3 / 32.6 / 54.2 / 14.2 | -2.7 / 1.4 / -1.3 / 0.2 / 1.2 | 1.6 |

**Residuals over all 48 postures.**

- Mean residual (ret / elev / IR / UR / PT): -4.4 / +2.7 / -3.0 / -0.2 / +3.6 deg.
- Largest residual: 7.7 deg (retraction, abduction). Largest RMS: 4.2 deg.

**The trade-off when one group is matched.** A 3-DOF girdle cannot meet 5 angles.

- **Scapula weighted 10x:** the scapula angles are met to < 0.15 deg. The clavicle is then 3-11 deg less retracted and
  2.5-12 deg more elevated than published; at rest it is 8.5-11.9 deg more elevated.
- **Clavicle weighted 10x:** the clavicle angles are met to < 0.35 deg. The scapula is then 3-15 deg less internally
  rotated and 3.5-10 deg less anteriorly tilted.

### 3.3 Other points, and other anchors and frames (primary; mm, ant / sup / lat)

| Plane | theta | GH | AC joint | clavicle tip (`acc`) | acromial angle (`aa`) | GH from Table I rest | GH, model thorax frame |
|---|---|---|---|---|---|---|---|
| abduction | 30 | -5.5 / 7.7 / -0.2 | -8.9 / 3.0 / -4.8 | -8.7 / 3.0 / -4.6 | -9.4 / 1.9 / -5.5 | -18.3 / 15.8 / -1.6 | -6.5 / 6.8 / -0.2 |
| abduction | 60 | -8.7 / 18.7 / -1.8 | -15.9 / 7.9 / -10.2 | -15.5 / 7.7 / -9.9 | -15.8 / 6.0 / -10.3 | -21.5 / 26.8 / -3.2 | -11.2 / 17.3 / -1.8 |
| abduction | 90 | -10.2 / 28.9 / -4.9 | -21.4 / 11.7 / -15.2 | -20.9 / 11.4 / -14.7 | -19.7 / 9.0 / -13.6 | -23.1 / 37.0 / -6.2 | -14.1 / 27.2 / -4.9 |
| abduction | 120 | -11.1 / 40.9 / -10.6 | -26.9 / 15.5 / -21.0 | -26.3 / 15.2 / -20.3 | -22.4 / 12.7 / -16.6 | -23.9 / 49.0 / -12.0 | -16.6 / 39.0 / -10.6 |
| abduction | 150 * | -13.2 / 51.0 / -18.4 | -33.0 / 17.1 / -26.9 | -32.3 / 16.7 / -26.0 | -24.8 / 15.0 / -19.4 | -26.1 / 59.1 / -19.8 | -20.1 / 48.7 / -18.4 |
| scaption | 30 | 3.0 / 7.4 / 1.0 | -3.0 / 3.0 / -1.9 | -3.0 / 2.9 / -1.9 | -1.3 / 1.6 / -0.3 | -5.3 / 13.7 / 0.3 | 1.9 / 7.7 / 1.0 |
| scaption | 60 | 2.0 / 17.4 / -0.2 | -9.0 / 7.2 / -5.8 | -8.8 / 7.0 / -5.6 | -5.8 / 4.9 / -2.9 | -6.3 / 23.8 / -0.9 | -0.4 / 17.5 / -0.2 |
| scaption | 90 | 0.5 / 25.5 / -2.8 | -14.7 / 9.4 / -9.4 | -14.3 / 9.2 / -9.0 | -9.5 / 6.3 / -5.0 | -7.8 / 31.9 / -3.5 | -3.0 / 25.4 / -2.8 |
| scaption | 120 | -4.6 / 35.5 / -7.2 | -22.2 / 12.9 / -15.1 | -21.7 / 12.6 / -14.6 | -15.9 / 9.9 / -9.8 | -12.9 / 41.8 / -7.9 | -9.4 / 34.5 / -7.2 |
| scaption | 150 * | -10.7 / 46.2 / -15.5 | -31.9 / 13.8 / -22.3 | -31.1 / 13.4 / -21.6 | -22.1 / 11.3 / -14.7 | -19.0 / 52.5 / -16.2 | -16.9 / 44.3 / -15.5 |
| flexion | 30 | 1.5 / 1.7 / 0.4 | -5.3 / -2.2 / -0.9 | -5.1 / -2.2 / -0.9 | -3.3 / -4.9 / 0.4 | 4.7 / 11.0 / 0.9 | 1.2 / 1.9 / 0.4 |
| flexion | 60 | 3.7 / 11.6 / -0.8 | -8.8 / 2.2 / -3.3 | -8.6 / 2.1 / -3.2 | -4.3 / -1.4 / -0.3 | 6.9 / 20.8 / -0.3 | 2.1 / 11.9 / -0.8 |
| flexion | 90 | 4.1 / 20.3 / -3.6 | -13.4 / 4.9 / -6.0 | -13.1 / 4.8 / -5.8 | -5.9 / 0.5 / -1.2 | 7.3 / 29.6 / -3.0 | 1.3 / 20.7 / -3.6 |
| flexion | 120 | -5.8 / 26.3 / -7.0 | -25.3 / 4.4 / -11.3 | -24.6 / 4.3 / -11.0 | -17.3 / -0.2 / -6.4 | -2.7 / 35.6 / -6.5 | -9.4 / 25.3 / -7.0 |
| flexion | 150 * | -21.9 / 36.1 / -14.5 | -41.2 / 5.0 / -21.8 | -40.2 / 4.9 / -21.1 | -33.9 / 1.1 / -17.0 | -18.7 / 45.4 / -14.0 | -26.6 / 32.8 / -14.5 |

- In every row the AC joint moves more posteriorly, more medially and less superiorly than GH, and the acromial angle moves
  more posteriorly and less superiorly than GH. At 90 deg scaption the acromial angle rises 6.3 mm while GH rises 25.5 mm.
- The anchor matters. With the arm-hanging posture taken at Ludewig Table I relaxed standing instead of the extrapolated
  0 deg curves, abduction 90 deg changes from (-10.2, 28.9, -4.9) to (-23.1, 37.0, -6.2). The difference is the posture gap
  at rest: Table I clavicle elevation 5.9 deg vs 11.0 deg extrapolated to 0 deg, and retraction 19.2 vs 23.0 deg in
  abduction. The teammate's note flags the same gap (its section 4).

### 3.4 Fitting variants (mm, ant / sup / lat; last column RMS residual in deg)

| Plane | theta | primary | clamped (as distributed) | w_clav | w_scap | RMS: primary / clamped / w_clav / w_scap |
|---|---|---|---|---|---|---|
| abduction | 30 | -5.5 / 7.7 / -0.2 | -5.5 / 7.7 / -0.2 | -12.9 / 12.5 / -1.7 | -3.2 / 4.6 / 0.0 | 3.3 / 3.3 / 5.2 / 4.5 |
| abduction | 60 | -8.7 / 18.7 / -1.8 | -8.7 / 18.7 / -1.8 | -20.1 / 26.4 / -5.1 | -5.9 / 11.7 / -1.3 | 3.9 / 3.9 / 7.0 / 4.9 |
| abduction | 90 | -10.2 / 28.9 / -4.9 | -10.5 / 27.5 / -4.5 | -22.5 / 36.5 / -8.9 | -8.0 / 19.8 / -4.1 | 4.1 / 4.1 / 7.7 / 4.9 |
| abduction | 120 | -11.1 / 40.9 / -10.6 | -13.7 / 24.7 / -4.8 | -21.5 / 46.6 / -14.0 | -10.8 / 30.7 / -9.9 | 3.6 / 7.2 / 7.3 / 4.2 |
| abduction | 150 * | -13.2 / 51.0 / -18.4 | -17.5 / 20.0 / -5.2 | -19.8 / 54.7 / -20.1 | -15.6 / 41.1 / -18.4 | 2.7 / 12.3 / 6.3 / 3.1 |
| scaption | 30 | 3.0 / 7.4 / 1.0 | 3.0 / 7.4 / 1.0 | -0.7 / 11.7 / 1.2 | 3.5 / 3.7 / 0.5 | 3.4 / 3.4 / 4.6 / 5.1 |
| scaption | 60 | 2.0 / 17.4 / -0.2 | 2.0 / 17.4 / -0.2 | -3.4 / 23.6 / -0.1 | 2.0 / 11.0 / -1.0 | 3.3 / 3.3 / 5.0 / 4.7 |
| scaption | 90 | 0.5 / 25.5 / -2.8 | 0.5 / 25.3 / -2.7 | -4.5 / 31.8 / -2.6 | -0.8 / 17.6 / -3.7 | 3.1 / 3.1 / 4.9 / 4.2 |
| scaption | 120 | -4.6 / 35.5 / -7.2 | -6.0 / 24.1 / -3.2 | -9.7 / 41.7 / -7.4 | -7.3 / 25.4 / -8.0 | 2.9 / 5.4 / 5.1 / 3.8 |
| scaption | 150 * | -10.7 / 46.2 / -15.5 | -13.5 / 18.0 / -3.9 | -13.0 / 54.0 / -15.7 | -15.3 / 31.5 / -15.4 | 1.9 / 11.3 / 4.0 / 2.2 |
| flexion | 30 | 1.5 / 1.7 / 0.4 | 1.5 / 1.7 / 0.4 | -2.0 / 2.4 / 0.2 | 3.5 / 4.2 / -0.1 | 3.9 / 3.9 / 4.9 / 6.0 |
| flexion | 60 | 3.7 / 11.5 / -0.8 | 3.7 / 11.5 / -0.8 | -0.2 / 13.6 / -0.4 | 4.5 / 11.4 / -2.0 | 3.5 / 3.5 / 4.7 / 5.3 |
| flexion | 90 | 4.1 / 20.3 / -3.6 | 4.1 / 20.0 / -3.5 | 0.0 / 23.1 / -2.9 | 3.7 / 17.4 / -4.9 | 3.2 / 3.2 / 4.5 / 4.6 |
| flexion | 120 | -5.8 / 26.3 / -7.0 | -6.8 / 15.0 / -3.1 | -10.6 / 31.2 / -7.1 | -7.5 / 19.4 / -7.3 | 2.8 / 5.3 / 4.5 / 3.7 |
| flexion | 150 * | -21.9 / 36.1 / -14.5 | -25.0 / 9.6 / -4.9 | -23.6 / 43.1 / -15.2 | -26.0 / 24.1 / -14.0 | 1.6 / 10.4 / 3.1 / 1.8 |

- **Fit weighting.** At 90 deg, the superior GH ranges over 19.8-36.5 mm (abduction), 17.6-31.8 mm (scaption) and
  17.4-23.1 mm (flexion) across w_scap .. w_clav. This spread comes from the model structure (3 DOF for 5 angles), not
  from the data.
- **Clamp.** With the distributed +-45 deg clamp, `scapula_upward_rot` sits at its bound from 90 deg in every plane. The
  superior GH then falls with elevation: abduction 27.5 mm at 90, 24.7 at 120, 20.0 at 150 deg.

---

## 4. Why Seth differs from `lift_literature` (decomposition; `compare.py` -> `compare.json`)

Steps, each changing one thing (all are displacements from the plane's 0 deg posture):

- **A:** `lift_literature`.
- **B:** the teammate's rigid chain itself (same maths as its scratch `gh_lit.py`), with the same angles. B - A is the
  quadratic-fit error.
- **C:** clavicle length 154 -> 125.2 mm (Seth SC to AC joint).
- **D:** rig AC-to-GH vector -> the Seth one (12.5, -35.1, 19.4) mm.
- **E:** the target angles -> the angles the Seth model actually reaches (section 3.2).
- **F:** OpenSim. F - E is the chain approximation of the model (the AC joint centre lies 0.55 deg off the SC-to-`acc`
  axis).

| Plane | theta | A | B - A | C - B (clavicle length) | D - C (AC-to-GH vector) | E - D (angle residuals) | F - E | F |
|---|---|---|---|---|---|---|---|---|
| abduction | 30 | -12.4 / 13.3 / -8.1 | -1.1 / -0.6 / 0.3 | 3.3 / -1.5 / 2.1 | 0.1 / -0.9 / 0.1 | 4.5 / -2.6 / 5.5 | 0.0 / 0.0 / 0.0 | -5.5 / 7.7 / -0.2 |
| abduction | 60 | -20.6 / 26.0 / -15.5 | 0.0 / 0.9 / -0.2 | 5.5 / -2.9 / 4.0 | 0.3 / -1.9 / 0.3 | 6.0 / -3.3 / 9.6 | 0.0 / 0.0 / -0.1 | -8.7 / 18.7 / -1.8 |
| abduction | 90 | -24.6 / 37.9 / -22.0 | 1.0 / -0.3 / 0.2 | 6.9 / -3.6 / 5.4 | 0.5 / -2.9 / 0.7 | 5.9 / -2.3 / 11.0 | 0.1 / 0.0 / -0.1 | -10.2 / 28.9 / -4.9 |
| abduction | 120 | -24.4 / 49.2 / -27.7 | 0.1 / 0.2 / -0.2 | 7.8 / -4.1 / 6.5 | 0.8 / -3.8 / 1.3 | 4.5 / -0.5 / 9.6 | 0.1 / -0.1 / -0.1 | -11.1 / 40.9 / -10.6 |
| abduction | 150 * | -20.1 / 59.7 / -32.6 | -5.1 / -0.1 / -1.4 | 8.5 / -4.2 / 7.2 | 1.2 / -4.7 / 2.1 | 2.1 / 0.3 / 6.3 | 0.1 / -0.1 / -0.2 | -13.2 / 51.0 / -18.4 |
| scaption | 30 | 0.1 / 12.8 / -3.1 | 0.4 / -0.1 / -0.2 | 1.2 / -1.5 / 0.8 | -0.2 / -0.9 / 0.3 | 1.5 / -2.9 / 3.1 | 0.0 / 0.0 / 0.0 | 3.0 / 7.4 / 1.0 |
| scaption | 60 | -1.6 / 24.7 / -7.1 | -1.1 / 1.0 / -0.7 | 2.9 / -2.7 / 2.0 | -0.1 / -1.9 / 0.6 | 1.9 / -3.5 / 5.1 | 0.0 / 0.0 / -0.1 | 2.0 / 17.4 / -0.2 |
| scaption | 90 | -5.1 / 35.6 / -12.2 | 0.3 / -0.8 / 0.3 | 4.0 / -3.2 / 2.8 | 0.1 / -2.8 / 0.9 | 1.2 / -3.3 / 5.5 | 0.0 / 0.0 / -0.1 | 0.5 / 25.5 / -2.8 |
| scaption | 120 | -10.4 / 45.7 / -18.2 | -1.3 / 0.0 / -0.2 | 5.7 / -3.9 / 4.2 | 0.6 / -3.6 / 1.2 | 0.7 / -2.7 / 5.8 | 0.1 / 0.0 / -0.1 | -4.6 / 35.5 / -7.2 |
| scaption | 150 * | -17.5 / 54.9 / -25.3 | 0.4 / 4.7 / -3.4 | 7.3 / -4.5 / 5.8 | 1.2 / -4.5 / 1.9 | -2.2 / -4.4 / 5.6 | 0.1 / 0.0 / -0.1 | -10.7 / 46.2 / -15.5 |
| flexion | 30 | 1.1 / 6.2 / -2.1 | -4.0 / -4.1 / -0.4 | 1.9 / 0.5 / 0.6 | -0.2 / -0.9 / 0.3 | 2.7 / 0.0 / 2.0 | 0.0 / 0.0 / 0.0 | 1.5 / 1.7 / 0.4 |
| flexion | 60 | -0.6 / 14.3 / -5.7 | -0.6 / 0.5 / 0.0 | 2.7 / -0.7 / 1.2 | -0.2 / -1.9 / 0.7 | 2.4 / -0.6 / 3.0 | 0.0 / 0.0 / 0.0 | 3.7 / 11.6 / -0.8 |
| flexion | 90 | -5.0 / 24.2 / -10.7 | 3.4 / 1.2 / 0.4 | 3.8 / -1.5 / 1.8 | 0.0 / -2.7 / 1.1 | 2.0 / -0.8 / 3.9 | 0.0 / 0.0 / -0.1 | 4.1 / 20.3 / -3.6 |
| flexion | 120 | -12.2 / 35.9 / -17.2 | -2.5 / -2.4 / -0.2 | 6.5 / -1.7 / 3.4 | 0.6 / -3.5 / 1.2 | 1.7 / -2.0 / 5.9 | 0.0 / 0.0 / -0.1 | -5.8 / 26.3 / -7.0 |
| flexion | 150 * | -22.1 / 49.5 / -25.2 | -9.1 / -2.1 / -2.0 | 9.5 / -2.4 / 5.8 | 1.7 / -4.4 / 1.4 | -1.9 / -4.4 / 5.6 | 0.1 / 0.0 / -0.1 | -21.9 / 36.1 / -14.5 |

What the steps show at 90-120 deg:

- **Clavicle length** (125.2 vs 154 mm, a factor of 0.81 on the clavicle-carried motion): 4-8 mm less posterior, 1.5-4 mm
  less superior, 2-6.5 mm less medial.
- **AC-to-GH vector:** the Seth vector is 4.0 mm shorter and 5 mm less lateral than the rig's. It gives 2.7-3.8 mm less
  superior.
- **Angle residuals** (the generic ellipsoid and AC geometry cannot reach the published combination; mainly retraction
  3.7-7.5 deg short): 4-11 mm less medial, 0.7-6 mm less posterior, 0.5-3.3 mm less superior.
- **Chain vs model:** <= 0.2 mm. So `lift_literature`'s chain reproduces the OpenSim model exactly once it is given the
  model's geometry and the angles the model can reach.
- **Quadratic fit:** `lift_literature`'s own fit error is <= 4.1 mm per component up to 120 deg (largest at flexion
  30 deg). It is 3.4-9.1 mm at 150 deg, beyond its stated validity of 0-135 deg.

Rig law vs Seth: |Seth - rig| = 9.4-19.8 mm at 90 deg and 11.7-26.7 mm at 120 deg, of which 7.3-21.8 mm is superior (rig
smaller) and the rest AP and ML (rig zero).

---

## 5. Sensitivity (`gh_seth.json` `sensitivity`; `compare.json` `chain_sensitivity`)

**Method.** Each published mean angle was moved by +-1 SD at the elevated posture with the rest fixed, unscaled at every
elevation. The SDs:

- **Scapula:** McClure et al. 2001 (bone pins, n = 8, scaption; SDs of the full-range change): UR 4.8, PT 13, IR 12.8 deg
  (their external-rotation SD).
- **Clavicle:** the note gives only SEs, so +-5 deg retraction and +-5 deg elevation, by the task's rule.

GH change in mm (ant / sup / lat, "+SD ; -SD"):

**(a) Through the 3-DOF model fit.** The model shares a one-angle change among all angles. For example, +5 deg retraction
reaches only +1.5 deg retraction, and +13 deg posterior tilt also lowers the clavicle 5.4 deg.

| Plane | theta | ret +-5 | elev +-5 | IR +-12.8 | UR +-4.8 | PT +-13 | RSS | abs RSS |
|---|---|---|---|---|---|---|---|---|
| abduction | 90 | -2.9 / 1.0 / -0.9 ; 3.0 / -0.9 / 0.9 | 0.3 / 7.7 / -1.5 ; -0.4 / -8.4 / 1.1 | 14.5 / 3.5 / 0.6 ; -14.6 / -1.7 / -2.9 | 0.3 / 5.5 / -1.8 ; -0.4 / -5.5 / 1.4 | 0.1 / -8.4 / -0.1 ; 0.1 / 10.1 / -1.4 | 14.9 / 14.7 / 4.1 | 21.4 |
| abduction | 120 | -2.5 / 2.1 / -1.3 ; 2.7 / -1.9 / 1.2 | -0.2 / 7.0 / -2.1 ; -0.0 / -8.2 / 1.9 | 13.2 / 4.4 / -0.7 ; -13.6 / -2.3 / -1.8 | -0.0 / 5.5 / -2.7 ; -0.1 / -5.6 / 2.4 | -0.3 / -8.3 / -0.3 ; 0.4 / 10.0 / -1.4 | 13.9 / 14.9 / 4.4 | 20.8 |
| scaption | 90 | -3.3 / 0.8 / -0.6 ; 3.5 / -0.7 / 0.5 | 0.4 / 7.6 / -1.3 ; -0.5 / -8.4 / 0.8 | 14.5 / 4.1 / -1.0 ; -15.0 / -2.0 / -1.2 | -0.1 / 5.3 / -1.7 ; -0.1 / -5.3 / 1.3 | 0.9 / -8.7 / -0.6 ; -0.6 / 10.5 / -1.0 | 15.5 / 15.1 / 2.7 | 21.8 |
| scaption | 120 | -3.0 / 1.6 / -0.9 ; 3.2 / -1.5 / 0.8 | -0.0 / 7.2 / -1.7 ; -0.2 / -8.3 / 1.4 | 13.6 / 5.0 / -1.5 ; -14.3 / -2.6 / -0.9 | -0.3 / 5.4 / -2.4 ; 0.1 / -5.4 / 2.0 | 0.4 / -8.6 / -0.5 ; -0.2 / 10.3 / -1.1 | 14.6 / 15.2 / 3.6 | 21.4 |
| flexion | 90 | -3.8 / 0.7 / -0.2 ; 4.0 / -0.6 / 0.1 | 0.5 / 7.7 / -1.2 ; -0.7 / -8.5 / 0.8 | 14.0 / 5.3 / -2.7 ; -15.0 / -2.8 / 0.6 | -0.4 / 5.3 / -1.7 ; 0.2 / -5.3 / 1.4 | 1.7 / -8.8 / -1.0 ; -1.3 / 10.7 / -0.6 | 15.7 / 15.6 / 3.6 | 22.4 |
| flexion | 120 | -3.4 / 1.3 / -0.6 ; 3.6 / -1.2 / 0.5 | 0.1 / 7.5 / -1.4 ; -0.3 / -8.7 / 1.1 | 13.5 / 5.7 / -2.4 ; -14.5 / -2.9 / 0.1 | -0.5 / 5.4 / -2.2 ; 0.3 / -5.4 / 1.9 | 1.1 / -8.4 / -1.1 ; -0.7 / 10.4 / -0.5 | 15.0 / 15.7 / 3.8 | 22.1 |

At 30, 60 and 150 deg the abs RSS is 19.2-22.1 mm (`gh_seth.json`).

**(b) Through the unconstrained rigid chain with Seth geometry** (each angle moves on its own): abs RSS 20.5-20.9 mm at
90-120 deg, split 12.4-13.3 / 11.1-11.4 / 11.0-12.3 mm (ant / sup / lat). With the rig geometry (154 mm clavicle) it is
24.0-24.3 mm.

**Common offsets cancel.** The same +SD offset applied to both the rest and the elevated posture changes the displacement
by <= 6.3 mm.

**Per degree, through the model fit** (scaption 90 deg; mm/deg, ant / sup / lat):

| Angle | mm/deg |
|---|---|
| ret | -0.69 / 0.15 / -0.11 |
| elev | 0.09 / 1.61 / -0.21 |
| IR | 1.15 / 0.24 / 0.01 |
| UR | 0.00 / 1.10 / -0.31 |
| PT | 0.06 / -0.74 / 0.02 |

These SDs are SDs of the full-range change, applied at every elevation. If the SD of the change grows linearly with
elevation, multiply by theta / theta_end (theta_end = 132-138 deg; 0.65-0.68 at 90 deg).

---

## 6. Caveats

- **Generic, unscaled model.** Its dimensions come from Holzbaur et al. 2005: SC to GH 139.3 mm vs 170.5 mm in the rig;
  clavicle 125.2 vs 156.4 mm. A uniform scale multiplies every displacement by s (angles unchanged), with s = 1.224 for
  SC-GH or 1.249 for the clavicle. The rig's proportions differ (its AC-GH / clavicle ratio is 0.29 vs Seth's 0.34), so
  uniform scaling is approximate. OpenSim's ScaleTool would need rig landmarks (IJ, C7, PX, T8, AA, TS, AI) that are not
  available here.
- **Constrained girdle.** 3 DOF cannot reproduce 5 published mean angles: residual RMS 1.6-4.2 deg, up to 7.7 deg in
  retraction. The fit weighting moves superior GH by up to 17 mm at 90 deg (section 3.4). Seth et al. tracked their single
  subject with a subject-fitted ellipsoid, which was not done here.
- **Coordinate clamp.** The distributed model cannot follow the published upward rotation above about 90 deg. The primary
  results relax that range in memory.
- **Inputs.** The angle inputs are figure readings (+-1 deg) of population means. A mean angle set pushed through a
  nonlinear model is not the mean GH. Below 15 deg and above 132-138 deg the angle curves are extrapolated. The anchor
  (extrapolated 0 deg vs Table I rest) changes the displacement by up to 13 mm AP and 8 mm superior in abduction
  (`gh_mm_rel_tableI_rest`).
- **Frames.** Results are in the model's ISB thorax. Its 7.86 deg tilt from the model's thorax body frame moves up to
  5.8 mm between AP and superior up to 120 deg, and 7.2 mm at 150 deg (section 3.3). How the rig's thorax frame relates to ISB is not checked here; the
  teammate's chain assumed they are equal.
- **Not modelled:** GH translation within the glenoid (the GH centre is fixed in the scapula; the teammate's note gives
  +1-12 mm from imaging and bone pins), AC translation (the AC is a ball joint), and clavicle axial rotation (it does not
  move the AC).
- **Humerus axial rotation** does not affect GH here, because the girdle is a function of elevation only; real
  axial-rotation effects on the rhythm are not represented.
- **No validation against bone-pin data.** The restricted data were not used (section 7). The model was checked only
  against its own plugin source (check (a)) and the GH centre against the humeral-head mesh (check (b)).

---

## 7. Licence, data restriction, citations

- **Model licence.** Seth et al. model and materials: Stanford Digital Repository https://purl.stanford.edu/br087nj9017,
  **CC BY-NC-SA 3.0** (attribution, non-commercial, share-alike); the user accepted it. The derived tables
  (`gh_seth.json`, this note) are derivatives of the model and carry the same terms. The plugin source is Apache 2.0 (its
  header).
- **Data restriction (respected).** The dataset's experimental bone-pin data (Ludewig et al.) may only be used to verify
  the Seth model itself. They were not used:
  - The ExperimentalData folder, the IK `.mot` files and the subject-scaled models were deleted before this work.
  - The archive `.cache/ext/seth2016/ScapulothoracicModelAnalysisPLOS2015.zip` is still on disk and was **not opened**.
    It probably contains those data; the lead may want to delete it.
  - Only the generic model and published summary means (Ludewig 2009 figures and Table I; McClure 2001 SDs, as reported in
    the teammate's note) were used.

**Citations.**

- Seth A, Matias R, Veloso AP, Delp SL (2016). A biomechanical model of the scapulothoracic joint to accurately capture
  scapular kinematics during shoulder movements. *PLoS One* 11(1):e0141028. https://doi.org/10.1371/journal.pone.0141028
- Holzbaur KRS, Murray WM, Delp SL (2005). A model of the upper extremity for simulating musculoskeletal surgery and
  analyzing neuromuscular control. *Ann Biomed Eng* 33:829-840 (the model's segment dimensions, per its credits).
- Seth A, Hicks JL, Uchida TK, et al. (2018). OpenSim: simulating musculoskeletal dynamics and neuromuscular control to
  study human and animal movement. *PLoS Comput Biol* 14(7):e1006223 (OpenSim 4).
- Ludewig PM, Phadke V, Braman JP, Hassett DR, Cieminski CJ, LaPrade RF (2009). Motion of the shoulder complex during
  multiplanar humeral elevation. *J Bone Joint Surg Am* 91(2):378-389.
- McClure PW, Michener LA, Sennett BJ, Karduna AR (2001). Direct 3-dimensional measurement of scapular kinematics during
  dynamic movements in vivo. *J Shoulder Elbow Surg* 10(3):269-277.
- Wu G, van der Helm FCT, Veeger HEJ, et al. (2005). ISB recommendation on definitions of joint coordinate systems of
  various joints for the reporting of human joint motion, Part II: shoulder, elbow, wrist and hand. *J Biomech*
  38:981-992.

---

## 8. Files (`pipeline/girdle/opensim_seth/`)

| File | Contents |
|---|---|
| `seth_model.py` | model loading, ISB frames and angles, girdle and humerus fits (OpenSim venv) |
| `ludewig2009.py` | published angle inputs, interpolation and extrapolation, SDs |
| `model_facts.py` -> `model_facts.json` | task 1 and checks (a) and (b) |
| `run_seth_gh.py` -> `gh_seth.json` | tasks 2, 3 and 5. `gh_mm` grid (primary); `table` rows with targets, reached angles, residuals, coordinates, AC / clavicle tip / AA, alternative anchor and frame; `variants`; `sensitivity` |
| `compare.py` -> `compare.json` | task 4, the decomposition and the chain sensitivity (repo python, uses `segs()` and `lift_literature` directly) |
| `seth_law.py` | `lift_seth(P, variant="primary", scale=1.0)`: bilinear interpolation of the table |

Run order:

```
.cache/opensim-venv/bin/python pipeline/girdle/opensim_seth/model_facts.py
.cache/opensim-venv/bin/python pipeline/girdle/opensim_seth/run_seth_gh.py
python3 pipeline/girdle/opensim_seth/compare.py
```

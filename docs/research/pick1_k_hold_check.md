# Independent check: pick1 K hold (preload 0.08 -> 0.04 N.m) - NOT REFUTED, with two red-team findings (2026-10-16)

Claim checked: `docs/research/pick1_k_hold.md` (commits 6990fcd, cb6130a; the judge and design.json edits sit in the WIP
commit 871bc00). Scripts and outputs of this check: `docs/research/pick1_k_hold_check/`. Every run imports
`judge/dynamics.py` unchanged; nothing in `judge/` was edited by this check.

## Verdict

| item | claim | re-measured here | verdict |
|---|---|---|---|
| R17 L1 `l1_minarc-pick1` (preload 0.04) | PASS, drift 3.68, twist 1.98, M_GH 0.061, F 0.30 | PASS, drift 3.68 (rate 0.010: 3.61), twist 1.98, M_GH 0.061, F 0.30, lags > 10 deg 0 | reproduced exactly |
| R17 CAD `user_minarc_pick1` | PASS, drift 3.72, twist 2.00, M_GH 0.062, F 0.31 | PASS, drift 3.72 (rate 0.010: 3.67), twist 2.00, M_GH 0.062, F 0.31, lags 0 | reproduced exactly |
| every other clip | 0.02-0.75 deg | 0.02 (6 clips), Wash opposite shoulder 0.73 / 0.75 | reproduced |
| hold at stop A, 2 g upright (CAD) | no lift > 0.5 deg; max 0.47 (Wash) | max lift 0.473 deg (Wash), share > 0.5 deg = 0 on all 8 clips; shelf drift 2.27 | reproduced |
| hold at stop A, 1 g pointed 4 other ways (new) | (claimed from the demand script: 1 g any direction 0.0295 < 0.040) | no clip lifts K (max lift <= 0.10 deg) with gravity along thorax +x, -x, +z, -z | confirmed by a second instrument |
| **R17 drift with the thorax tilted (new)** | "1.3 deg under the 5-deg rule" | Reach a high shelf at 1 g pointed along thorax +x / -x / +z / -z: **5.69 / 6.12 / 4.12 / 7.70 deg** | **the margin is upright-only** (finding 1) |
| lag cost on proximity (L1, preload 0.08, Reach a high shelf) | 2-14 87.85 -> 87.98 %, 2-10 66.61 -> 65.17 %, clearance 1.61 -> 1.78 mm, no touch | 87.65 -> 87.87 %, 66.72 -> 65.26 %, 1.61 -> 1.79 mm, no metal inside (all 575k skin samples, step 3, MuJoCo kinematics) | reproduced |
| R8 CAD | 239.8 -> 203.8 g | all 86 part names match exactly one MATERIALS row; Ti links = volume x 4.43; sum 203.8 g | reproduced |
| catalogue fixes | applied in the builder for the next build | in `user_style_minarc.py`; the built `exo.glb` / `parts_full.json` still carry the old names (as the claim says) | applied in code only (finding 2) |
| lofts | none | `param_build.makeLoft` is reachable only from `strap_solid` / `main`, which the minarc chain never calls (it uses `axis_frame`, `disc_face`, `joint_parts`, `revolved`); the diff adds no geometry call | none reachable |
| gap claim from re-planning | none made ((c) not run) | the bench model's K is geometric (the preload appears in the models only as text), so the verified 18.40 does not depend on the preload | nothing to reproduce |

## 1. R17 re-run (the claimed configuration, both designs)

`python3 judge/dynamics.py <design> --quick --jobs 1 --out ...` (nominal case: rolling bearings mu 0.005, tau0 0.001,
speed 1, hub tilt; both rates 0.015 and 0.010). The judge read the preload from the design
(`preload_source: design.json build_fixes.spring.preload`, 0.04). The output is in `r17_l1_quick.json` and
`r17_cad_quick.json`. The numbers match the claim to the last digit. `moves_freely_nominal` is True on both.

One note on the measurement: the judge's R17 verdict uses the 0.015 N.m/rad rate. The design declares 0.010. At 0.010
the drift is smaller (3.61 / 3.67), so the verdict does not depend on that choice.

The judge change (it reads the declared preload, else 0.08) applies only to designs that declare a preload. A scan of
every `design.json` finds only the two pick1 designs. So "no earlier number moves" holds.

## 2. Hold at stop A, and red-team finding 1: the R17 margin is upright-only

`hold_check.py` runs the judge's own simulation on the CAD at preload 0.04. It replaces only the gravity vector, in the
thorax rig frame (x anterior, y up, z right), and checks it actually changed.

| gravity | lift where the plan has K on stop A (max deg) | Reach a high shelf drift | Wash drift | worst twist |
|---|---|---|---|---|
| 1 g upright (the judge) | none | 3.72 | 0.75 | 2.00 |
| 2 g upright (the claim's case) | 0.47 (Wash), share > 0.5 deg = 0 | 2.27 | 0.69 | 2.65 |
| 1 g along +x (bent forward 90 deg) | none | **5.69** | 1.75 | 2.83 |
| 1 g along -x (lying supine) | none | **6.12** | 1.56 | 3.28 |
| 1 g along +z (lying on the right side) | 0.10 | 4.12 | 0.80 | 2.09 |
| 1 g along -z (lying on the left side) | none | **7.70** | 2.61 | 3.83 |
| 2 g along +x / -x | none / 0.26 (Wash) | 5.56 / 6.91 | 1.91 / 1.47 | 2.75 / 3.72 |

* **The hold itself holds.** At 1 g, in any of the five directions, no clip lifts K off stop A where the plan keeps it
  there. At 2 g along +-x it still does not. This independently supports the claim's demand numbers (1 g in any
  direction: 0.0295 < 0.040 N.m). The clips do not visit the workspace's worst state-A pose (elevation 165, 0.0355 N.m
  at 2 g), so that pose rests on the demand script alone.
* **The R17 drift pass needs gravity to help.** Upright, gravity pulls K open on Reach a high shelf. That pull is
  worth about 2-4 deg of drift. With the same thorax-relative motion and gravity across the thorax, the clip drifts
  4.1-7.7 deg. It fails the 5-deg rule in three of four directions, and cuff twist rises to 3.8 deg.
* R17 is defined on the upright clips, so the claim's PASS stands as judged. But "1.3 deg of margin" is a statement
  about upright use only. A wearer who reaches overhead lying down or leaning forward meets the same breakaway lag that
  failed gen-4b.
* As the claim says, the drift peak is set by stop-A torque minus gravity's help at breakaway. Lowering the preload
  further trades hold margin for drift and does not remove the posture dependence. The lever that does remove it is the
  claim's untested (c): plan K on the spring's own trajectory, so it stays shut until the chain forces it open. The
  drift is then measured against a plan the hardware actually follows. Section 1 of the claim prices that at about
  1.4 points of the 10-mm band on one clip, and section 3 here reproduces it (1.46).

**Demand script frame (`demand_real_g.py`).** The script puts gravity in the scapula frame as `scap(elev, 0)^T`
applied to (0, -1, 0). Checked against the bench pose set: its `HG` equals `scap(P[:, 1], 0)^T humerus(P[:, :3])` to
1e-7. So the "real direction" uses the same frame as the kinematics, and column 1 of `POSE` is the elevation. The
script was not re-run here; the gravity-direction runs in the dynamics judge above are the second instrument.

**Hold component.** The hold is the existing custom clock spring: 0.3 x 5 mm 1.4310 strip, 217 mm long, from a spring
maker's drawing. It has no catalogue part number. Its torque curve is the beam formula k = E b t^3 / (12 L), with
E = 193 GPa, giving 0.0100 N.m/rad. The preload is the free-angle offset the maker winds in. All of this is
**computed, not measured or sourced from a datasheet.** I re-derived the stress figure: M = 0.04 + 0.010 x 0.989 rad =
0.0499 N.m, and sigma = 6M / (b t^2) = 665 MPa, matching the claim's 670.

The claim does not state a tolerance. Drift rises about 0.13 deg per mN.m of preload (0.035 -> 2.97, 0.040 -> 3.72,
0.045 -> 4.35), so R17 fails above about 0.050 N.m, i.e. +24 %. At -15 % (0.034 N.m), the hold is 0.96x the 2 g
real-direction worst pose. Coil-to-coil and wall friction are not modelled. They oppose opening, which adds to drift,
and they oppose return. **Put the torque at stop A on the spring drawing as 0.040 +-0.004 N.m and measure it on a
torque gauge before assembly.**

## 3. Lag effect re-score (reproduction on one clip)

`lag_check.py` takes a different path from the claim's `k_hold.py`:

* The members are posed by MuJoCo's own kinematics: the judge's MJCF with qpos set to the planned or simulated angles,
  then xmat / xpos read back. The claim uses a numpy FK.
* Simulated angles are interpolated at each frame's path parameter. The claim takes the nearest sample.
* Proximity uses `score_design.py`'s metric at its own sampling: every skin sample (the claim used every 4th), every
  3rd frame (the claim used every 2nd).
* The cuff deviation is applied to the arm parts, as in the claim.

Design `l1_minarc-pick1`, preload 0.08, Reach a high shelf:

| | in-band 2-14 | in-band 2-10 | min covered gap | min skin-to-metal | frames with metal inside the skin |
|---|---|---|---|---|---|
| planned (this check) | 87.65 % | 66.72 % | 1.61 mm | 1.61 mm | 0 |
| simulated (this check) | 87.87 % | 65.26 % | 1.79 mm | 1.79 mm | 0 |
| planned (claim) | 87.85 % | 66.61 % | 1.71 (exact clearance 1.61) | - | 0 |
| simulated (claim) | 87.98 % | 65.17 % | 1.87 (exact clearance 1.78) | - | 0 |
| K lag > 1 deg (25 frames here / 38 in the claim) | 77.28 -> 77.67 % | 68.63 -> 64.47 % | | | |

* MuJoCo's kinematics reproduce the clip's member frames to 1.5e-6, and the simulation reproduces drift 9.28 and
  twist 4.64.
* The simulated K matches the claim's to 0.06 deg on the 27 frames both runs score. On those frames the band
  averages agree within 0.22 points.
* With 4x the skin samples and a different frame step, **the claim's section 1 reproduces.** The lagging K moves the
  metal about 0.18 mm *away* from the skin. The 14-mm band does not change (+0.2 points). The 10-mm band loses 1.46
  points (claim 1.44), and 4.2 points on the lag frames. No frame touches.
* The "inside" count here is a crude normal-side test (metal points within 3 mm of a skin sample, on its inner side),
  not the R2 winding number. The claim's exact R2-instrument figure (0 frames inside) is consistent with it.

Out: `lag_l1_p0.08_shelf.json`.

## 4. R8 and the catalogue fixes, and red-team finding 2

**R8.** `material_of()` matches each part's leading identifier. Applied to all 86 part names of
`user_minarc_pick1/parts_full.json`, every name matches exactly one row. Links 1a / 1b / 2 are Ti-6Al-4V at
vol x 4.43 g/cm3: 12.58 / 15.11 / 20.34 g. The parts sum to 203.8 g, which is R8 on the scorecard.

**`user_minarc_bdp` was not re-billed.** It still lists link 1a as NdFeB (20.98 g) and links 1b / 2 as hardened steel
(26.18 / 37.78 g), for 239.1 g. At Ti density the sum is about 202.6 g. R8 passes either way, but BDp's dashboard
mass is about 36 g high.

**Finding 2: the built record contradicts the declared design until the rebuild.** The claim says the old names stay
until the next build, and they do. The CAD's `parts_full.json` / `exo.glb` still say:

* "K clock spring ... 0.08 N.m preload", while `design.json` declares 0.04;
* dowels "ISO 8734 O3 x 5.65";
* magnet "O3 x 1.4".

Two catalogue notes for that rebuild, both to be confirmed against a supplier listing rather than taken from here:

* The new dowel callout is "O3 x 6 m6 hardened, faced to 5.65 mm". A hardened m6 pin (about 60 HRC) is shortened by
  grinding, not by lathe facing. I also recall the ISO 8734 length table for d = 3 starting at 8 mm, but did not
  confirm it. A 3 x 6 hardened pin is commonly sold under DIN 6325. A stock 3 x 6 with the press hole 0.35 mm deeper
  avoids the extra operation.
* The "stock O3 x 1.5 diametric" magnet has no part number.

**Lofts.** None reachable (see the verdict table).

## 5. Open, for the lead

1. Finding 1: R17's margin holds upright only. Run (c) to remove the posture dependence: plan K on the spring's own
   trajectory, then re-judge R17 and the proximity. Otherwise, state "upright use" as an MVP1 limit.
2. Put the preload tolerance and an incoming torque check on the spring drawing (section 2).
3. Rebuild `user_minarc_pick1` so the part names match the declared 0.04 preload and the new stock callouts. Re-bill
   `user_minarc_bdp` with the material table.
4. Still open from the claim: the K dowel pair under link 1b's strap root.

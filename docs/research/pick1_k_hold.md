# pick1: what K's lag costs, and the K hold that passes R17 (2026-10-16)

Gen-4b (`l1_minarc-pick1`, `user_minarc_pick1`) failed R17 on one number: on "Reach a high shelf" the plan opens K to
15.8 deg, but in the dynamics judge K sits on stop A for 66 % of the clip and lags the plan by 9.28 deg (L1) / 9.35 deg
(CAD), over the 5-deg rule. The 0.08 N.m clock-spring preload holds K shut longer than the cuff tissue can push
(0.03 N.m/deg torsion), so the cuff twists instead.

* Harness: `docs/research/pick1_k_hold/k_hold.py`. It imports `judge/dynamics.py` unchanged and adds any extra K
  torque law through MuJoCo's passive-force callback. Mode `sim` gives K drift and lift per clip. Mode `lag` gives
  proximity planned vs simulated.
* Demand: `docs/research/pick1_k_hold/demand_real_g.py` imports the red team's harness unchanged.
* Outputs: `docs/research/pick1_k_hold/*.json`.

## 1. What the lag costs (it is cosmetic for proximity)

**Method.** The clip is simulated in the judge's nominal case (rolling bearings mu 0.005, 1 g, speed 1, preload 0.08).
At each clip frame, the simulated joint angles are read and the members are posed by forward kinematics through the
judge's fitted hinges, starting from the clip's own base.

* The FK reproduces the clip's planned frames to 3e-6.
* The arm-fixed parts (H) get the simulated cuff deviation from the bone: twist up to 4.64 deg.
* Proximity is score_design.py's metric on the same skin samples (every 4th of its samples, every 2nd frame).
* Clearance and depth come from the R2 instrument (`judge/sdist.py`: exact closest point plus winding number).

| clip (L1, preload 0.08) | | in-band 2-14 | in-band 2-10 | min covered gap | min metal-skin clearance | frames inside the body |
|---|---|---|---|---|---|---|
| Reach a high shelf (all frames) | planned | 87.85 % | 66.61 % | 1.71 mm | 1.61 mm | 0 |
| | **simulated** | **87.98 %** | **65.17 %** | **1.87 mm** | **1.78 mm** | **0** |
| the 38 frames K lags > 1 deg | planned | 78.02 % | 68.84 % | 1.71 | 1.61 | 0 |
| | simulated | 78.16 % | 64.65 % | 1.87 | 1.78 | 0 |
| Wash opposite shoulder (all frames) | planned | 59.36 % | 27.29 % | 2.40 | 2.36 | 0 |
| | simulated | 59.35 % | 27.73 % | 2.40 | 2.36 | 0 |

**Verdict: the R17 failure is about tracking, not about proximity.**

* The lagging K holds the metal slightly *farther* from the skin: +0.17 mm at the closest point.
* The 14-mm band does not change. The 10-mm band loses 1.4 points on Reach a high shelf (4.2 points on the lag frames).
* No frame touches.
* J2 rides its q2 stop in both the planned and the simulated chain (margin 0.0 / -0.02 deg, the joint limit's
  softness). The lag does not push the dyad past its built stop.

What the lag does cost is the cuff: 4.6 deg of twist on the arm, against the 5-deg rule, and a plan that the geometric
judges assume but the arm does not drive.

## 2. The hold: measured, not argued

| K law (L1 unless marked; nominal case) | hold at stop A | Reach a high shelf drift | Wash drift | twist | M_GH peak |
|---|---|---|---|---|---|
| clock spring 0.08 (gen-4b) | 0.080 | 9.28 | 2.42 | 4.64 | 0.142 |
| clock spring 0.06 (the earlier sweep) | 0.060 | 6.38 | 1.52 | 3.23 | 0.099 |
| clock spring 0.05 | 0.050 | 4.96 (CAD 5.04) | 1.11 | 2.60 | 0.080 |
| (a) detent: 0.03 spring + 0.035 flank detent (full to 0.5 deg, 0 at 2 deg) | 0.065 | 7.15 | 1.73 | 3.48 | 0.107 |
| (b) two-rate: 0.03 spring + 0.035 helper leaf unloaded at 1.5 deg | 0.065 | 7.08 | 1.62 | 3.45 | 0.106 |
| clock spring 0.045, CAD | 0.045 | 4.35 | 0.96 | 2.31 | 0.071 |
| **clock spring 0.040, CAD** | **0.040** | **3.72** | **0.75** | **2.00** | **0.062** |
| clock spring 0.040, L1 | 0.040 | 3.68 | 0.73 | 1.98 | 0.061 |
| clock spring 0.035, L1 | 0.035 | 2.97 | 0.50 | 1.60 | 0.051 |

(Rate 0.015 N.m/rad nominal; the 0.010 rate gives the same numbers within 0.07 deg.)

**A detent or a two-rate spring does not help.** Both drift like a plain spring with the same torque at stop A
(0.065 N.m: 7.1 deg, between the 0.06 and 0.08 plain springs). The peak drift happens at breakaway. The arm must twist
the cuff until the reflected torque equals the hold at stop A, about 0.0074 N.m per degree of lag. What K does after it
leaves stop A does not change that peak.

**So the two targets in the brief conflict:**

* Drift <= 4 deg on the CAD needs a hold of at most about 0.042 N.m at stop A.
* 1.3x the red team's 0.048 N.m needs 0.062 N.m.

No passive law that depends only on K's angle can meet both. Only re-planning (c) or a different K transmission at the
breakaway poses could. The question then is whether the plan needs 0.048 N.m at all.

**It does not.** The 0.048 N.m is the worst-direction envelope: 2 g pointed in whatever direction pulls hardest, plus
2 mN.m per sealed pair. `demand_real_g.py` repeats the red team's generalized-force method, unchanged, with gravity in
its real direction (thorax -y through the scapula law) over all 1594 state-A poses:

| state-A demand (N.m) | 1 g real direction | 2 g real direction | 1 g any direction | 2 g any direction (red team) |
|---|---|---|---|---|
| all poses (clips + workspace + envelope) | 0.023 | 0.0355 | 0.0295 | 0.0478 |
| clip frames | 0.0157 | 0.025 | 0.0205 | 0.0333 |

* Gravity pulls K open in every state-A pose, so the hold is needed. But the worst real case is at elevation 165
  (plane 45, axial -30) and needs 0.0355 N.m at 2 g.
* In the dynamics judge at **2 g, real direction, every clip, preload 0.040 (CAD)**, K never leaves stop A where the
  plan has it there:
  * The largest lift is 0.47 deg, on Wash opposite shoulder.
  * The share of frames lifted more than 0.5 deg is 0 on all 8 clips.
  * Reach a high shelf drifts 2.27 deg, because gravity helps K open.
* At 1 g, real direction, no clip lifts K either.

**Chosen hold: the same clock spring at 0.040 N.m preload.** It adds no parts and no complexity
(`tools/simplicity.py` is unchanged).

* **R17 drift:** 3.72 deg on the CAD and 3.68 on the L1, with 1.3 deg of margin to the rule. Every other clip is at
  0.02-0.75 deg.
* **Hold margin:**
  * 1.74x the 1 g real-direction demand;
  * 1.36x the 1 g any-direction demand;
  * 1.13x the 2 g real-direction worst pose;
  * 0.84x the red team's 2 g any-direction envelope. That envelope is not a load the plan sees.
* **Spring:** 0.010 N.m/rad, 217 mm of 0.3 x 5 mm 1.4310, now wound 0.64 turns of preload instead of 1.27.
  * Bending stress at stop B is about 670 MPa (M = 0.04 + 0.010 x 0.989 rad), against 1198 MPa at 0.08. It now fits
    even +C1700's 0.7 Rm with 44 % margin.
  * The part geometry is unchanged.

**Red team on the choice:**

* Below the worst-direction envelope, a jolt over 1.13x the 2 g real-direction demand can lift K momentarily. K is
  sensed (the 4th encoder), so the controller knows. The spring returns it, because the 1 g demand is 0.023 < 0.040.
* The CAD's spring has 0.043 mm wall clearance, flagged by the verifier. Wall friction now acts against half the
  preload. It is not modelled here. If the prototype shows hysteresis, open the chamber 0.2 mm.
* (c) Re-planning K was not run. The cheapest lever needs no new plan, and section 1 shows that following the spring's
  own trajectory costs about 1.4 points of 10-mm band on one clip and nothing at 14 mm.

## 3. Re-judged: l1_minarc-pick1 and user_minarc_pick1 (design change: K preload 0.08 -> 0.04 N.m)

Preload measurement change, stated: until now `judge/dynamics.py` used the constant 0.08 N.m for every knuckle. It
now reads the preload the design declares in `design.json` `build_fixes.spring.preload`, and falls back to 0.08.

* Only the two pick1 designs declare a preload. They declared 0.08, so no earlier number moves.
* The judge records the preload and its source in `dynamics.json` `chain.springs`.
* The design change is made separately: both pick1 `design.json` files now declare 0.04. Both builders take
  `--spring-preload`; the CAD builder takes it from its L1 by default.

| | before (0.08) L1 | after (0.04) L1 | before CAD | after CAD |
|---|---|---|---|---|
| R17 | FAIL (drift 9.28) | **PASS** (3.68; twist 1.98; M_GH 0.061 N.m; F 0.30 N; no lag > 10 deg) | FAIL (9.35) | see the CAD scorecard (section 5) |
| R11 | 0.404 kPa | 0.344 kPa | - | - |
| R1 / R1-aim / R4 / R16 | 80.8 / 48.7 / 71.8 / 74.0 % | unchanged (same geometry) | 80.5 / 47.2 / 71.0 / 74.0 % | unchanged |
| pass count | 6 / 19 | **7 / 19** | 6 / 19 | see section 5 |

## 4. Builder fixes (pipeline/conformal/param_cad/user_style_minarc.py)

* **Material from a table.** `MATERIALS` holds one row per part kind, matched on the part's identifier at the start of
  its name. Words further on ("O3 magnet pocket", "2 dowel holes") no longer decide the material. A part that matches
  no row, or more than one, stops the build.
  * Re-billed in place on the built volumes of `user_minarc_pick1/parts_full.json`; the geometry is unchanged.
  * Link 1a: NdFeB 21.30 g -> Ti 12.58 g. Link 1b: steel 26.78 -> Ti 15.11 g. Link 2: steel 36.05 -> Ti 20.34 g.
  * Custom mass: 178.2 -> 142.1 g, the verifier's number. **R8 is re-judged in section 5.**
* **Stock sizes.**
  * Dowels are now "ISO 8734 O3 x 6 m6 hardened (stock length), faced to 5.65 mm": a stock part with one facing op, so
    the press depth stays 3 mm and no hole moves.
  * The K encoder magnet is a stock O3 x 1.5 diametric (was 1.4), seated on the O3.05 x 1.6 pocket floor.
  * A multi-strip bar (link 2: 4 side-view sketches side by side) now reads "3+2-axis milling" instead of "or wire
    EDM". The one-profile bars 1a and 1b keep wire EDM.
  * These names change on the next build. The current exo.glb still carries the old names.
* **K's dowel pair is NOT turned. Open, with the reason measured:**
  * The opposed pair sits at homes 66 / 246 deg.
  * Keeping dowel 2's press hole (+-11 deg) plus a 1.5 mm wall (+-11 deg at r 7.75) off link 1b's strap root
    (225-275 deg) needs a home <= 23 or >= 117 deg. That is a turn of -43 / +51 deg.
  * The verifier measured only 22 deg of slot clearance to link 1a's root, so an opposed (180 deg) pair cannot clear
    both roots by turning alone.
  * The fix needs the L1 builder's slot placement (`build_minarc_l1.py`, line ~175) to search a non-opposed pair:
    2 dowels about 150 deg apart still form a couple with a small radial residual. Or it needs the hole moved inboard
    to r 6.75. Either change needs an L1 rebuild, the CAD rebuild, and R6 / R7 / R9.

## 5. Next

1. CAD re-judge of R17 / R8 (scorecard of `user_minarc_pick1`, this commit).
2. The K pair as a non-opposed search in `build_minarc_l1.py` and a rebuild of both designs. That rebuild carries the
   new part names.
3. A verifier re-measures section 2: the 2 g real-direction sims and `demand_real_g.py`.

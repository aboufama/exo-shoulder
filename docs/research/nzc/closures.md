# Near-zero closures: which cheap passive additions exist, and what they can buy (2026-10-16)

Track NEAR-ZERO CLOSURES of the golden push (user, 2026-10-16 ~05:50 UTC: "The golden solution is something 95% plus with
complexity at 0 (or near)"). Target: gap <= 13.75 on Bench(110,360) exact, frozen shape, margin 5, O20 hubs, at the
lowest complexity (tools/simplicity.py, the user's weights: passive translation 2, sliding pair 1, passive rotation 1,
sensed passive 5). Reference: the zero-complexity class tops out at 31.04 frozen exact (docs/concepts/zc-frontier-3r.md),
capped by hub 2, which cannot park in band once the shorter arc opens the fold window (>= ~45 deg).

Files: `j2knee_gate.py` (ray-parking gate), `docs/concepts/models/virtual-j2-knee-3r.py` (kit model),
`vj2_local_sweep.py` + `docs/concepts/sweeps/virtual-j2-knee-3r.json` (first screen), farm gate outputs
`gate_b110_s<seat>.json` (Bench(110,360), 6 J1 seats; landing after this commit).

## 1. Which 1- and 2-passive closures of a 3R through the wearer's GH exist (theory, checked numerically)

Setting: three active pins (lines L1, L2, L3), k passive joints between link 3 and the arm, the arm a rotation about GH
(the bench has no GH translation). Loop freedoms 3 + k + 3, 6 constraints. With q locked the loop is rigid iff the
passive screws are independent modulo rotations about GH, i.e. their moments about GH (pin: (c - GH) x u; slide: s)
are linearly independent. Full mobility 3 needs the active joints' moments to stay in the span of the passive ones at
every closed configuration.

* **No 1-passive closure exists except degenerate ones** (the passive locked at 0, or an active joint locked). One passive
  needs every moment in one line, i.e. all joint lines in one plane through GH, which any finite rotation about one of
  those lines breaks. Directly: a J3 line off GH leaves link 3 a drift (R3^T - I) c3 against the arm - a circle in the
  plane normal to u3, 2-D, never 1-D; a J2 line off GH adds R3^T (R2^T - I) c2, whose u3 component is
  (cos q2 - 1)(u3 . c2) - sin q2 u3 . (u2 x c2), zero for all q2 only if u2 || u3 (orientation rank lost). **So "one slider
  along the arm" cannot close any offset 3R exactly**; a slider is only ever the second freedom of a planar pair.
* **2-passive closures: exactly the planar family.** Every joint must be on a GH line or parallel to ONE direction w (the
  invariant is the w-height of GH); the two passives (pins || w, or slides normal to w, RR / RP / PP) sit next to the one
  active joint || w and close a planar 3-freedom group. Three placements:
  - distal, w = u3: the pin knee / osn 2-slide cuff (the 2-slide closure theorem, offset-skin-normal-3r.md);
  - **middle, w = u2: the virtual-J2 knee (new here)** - J2 is a planar pin triple (1 active + 2 passive pins || w) and
    link 2 turns about the VIRTUAL w-line through GH, so hub 2 no longer sits on the w-ray;
  - proximal, w = u1: a base-side knee (hub 1 is not a cap: 0.98 in band in every leader - no value).
* **None of them moves the fold.** The passives only re-parametrise the active rotation about w (theta = q_w + qa + qb),
  so the orientation is still the spherical 3R (u1, w, u3) and the fold law holds unchanged. **No <= 2-passive closure
  widens the fold window.** A passive rotation NOT parallel to an active axis is needed for that, and it brings the
  count to >= 3 passives (the Jarrasse-Morel isostatic arm fixation: 2 pins normal to the arm + 1 slide whose direction has
  a component along GH -> U-centre - along the humerus when the U sits on the arm), or a 4th active joint (25 points).
  What a planar closure CAN buy is parking: the middle placement decouples hub 2's location from the J2 direction,
  which is exactly the zero-complexity cap.
* **Sensing.** On a rigid-GH body the three active encoders determine the arm (locked loop rigid) iff the two passive
  pins and the virtual axis are not collinear in the knee plane: |sin angle(OA, OB)| > 0 (OA, OB = the pins' offsets
  from the w-line). Measured on the untuned virtual-J2 knee (a1 52 / a2 70, Bench(60,160)): |sin| min 0.017, p5 0.116,
  median 0.588; the smallest singular value of d(q1, qJ2, q3)/d(arm rotation) min 0.019, p5 0.113, median 0.397 - the
  reading goes singular where the knee lines up through the virtual centre, so the model now requires |sin| >= 0.17
  (RIG_MIN). Under real GH translation the knee absorbs the in-plane part and theta = q_w + qa + qb is no longer known
  from the three encoders: the pins must be read (census rule: the pin knee counts 2 sensed passives) or replaced by
  slides (PP: exact twist, 2 passive translations + crossed rails). A knee whose angles do NOT enter the reading would
  have to be a pure translator (slides or parallelograms: +1 loop each) - no pin pair qualifies.

Complexity (tools/simplicity.py v1): virtual-J2 knee = 19.0 with both pins sensed (5 bodies, 5 joints, 2 passive
rotations, 2 sensed; 11 made / 10 bought), 9.0 if bench-exact unsensed pins were accepted - the same class as the pin
knee (19.5 / 9.5). It only matters if it beats the pin knee's verified numbers.

## 2. Ray-parking gate of the virtual-J2 knee (j2knee_gate.py)

For seats / arcs whose fold window opens, where can a pin fixed in LINK 1 (the active J2, O20 disc: centre + 8 rim
samples, each marched along w from its true offset, one level = quantile 0.97 over the closing poses, in band = level -
requirement <= 12 mm) and a pin fixed in LINK 2 (pin b, O12 disc in the gate) sit, at >= 17 mm apart, hub 2 >= 24 deg
from hub 1, knee span ratio <= 3.5? Bench(60,160) fast, margin 5, J1 bvec(109.36, 65.94) / J3 wdir(85.74, -16.19) (the
zc optimum's seats):

| arcs a1 / a2 | fold-law reach (160-pose ws) | hub 2 ON the w-ray: in band, level | best link-1 pin (rho, psi): in band, level | best link-2 pin | pin spacing min-max |
|---|---|---|---|---|---|
| 52 / 70 (sigma -1) | 0.819 | 0.03 at 123 mm | (28, 30): 0.958 at 53 mm | (12, 30): 0.969 at 63 mm | 17.6 - 38.7 mm |
| 58 / 80 (sigma -1) | 0.875 | 0.03 at 176 mm | (44, 30): 0.855 at 39 mm | (20, 60): 0.905 at 61 mm | 24.0 - 58.4 mm |
| either, sigma +1 | 0.819 / 0.875 | 0.01-0.08 | no pair >= 0.85 | | |

**The pins pass:** 20-30 mm beside the w-line the skin along w is 50-110 mm lower than on it, so both pin discs park in
band where hub 2 on the ray cannot (0.03). (160-pose bench: the 360-pose reach is ~0.06-0.08 lower, the winner's curse
measured in reach_attribution.md; the Bench(110,360) gate over 6 J1 seats is on the farm.)

## 3. First honest screen of the model (Bench(60,160) fast, every kit check: march, dense K2, K6 1 mm radial, audit)

Model `docs/concepts/models/virtual-j2-knee-3r.py`: J1 / J3 O20 hubs on GH rays; J2 O20 hub at the link-1 offset; pins a,
b O20 (O20-only applied to the passive pins too, conservative); crank and knee link = flat 3 mm Ti plates normal to w with
O20 ring ends, one fitted level each (K4 march from the true offset: a kit extension, `O0` per-pose plane origin);
stack link 1 / crank at J2, crank / knee at a, knee / link 2 at b; 12 x 3 straps; K7 neck; K6 exemption at the offset
pins taken through the fitted pin centres; closure exact (closed form; fold residual 0.0).

| config | gap | reach | follow | in-band 14 | contact | collide | in band: hub1 / hub2 / hub3 / crank / pin a / knee / pin b / link1 / neck / link2 |
|---|---|---|---|---|---|---|---|
| gate best pair (a1 52, a2 70, P (28, 30), Pb (12, 30), la = lk = 24) | 103.68 | 0.538 | 0.80 | 0.405 | 0.029 | 0.28 | 0.98 / 0.64 / 0.80 / 0.26 / 0.16 / **0.00** / **0.00** / 0.94 / 0.83 / **0.10** |
| best of the first random batch (22 configs so far, local, pre-RIG_MIN) | 103.68 | | | | | | |

**What it says (measured):** the pins park, the PLATES do not. The knee link and the crank are rigid flat plates that
sweep the knee plane around the virtual axis; one level along w must clear the highest skin anywhere under that sweep
(knee 94 mm, crank 56), so the knee link, pin b (stacked on it) and link 2 (stacked on pin b) float - the gate's
pin-only view was optimistic, and this is the virtual-pole four-bar's finding again ("the J2 neighbourhood is the worst
skin in every frame"; the planar double-parallelogram RCM was rejected there for the same reason). Collisions (link 2
over the knee / crank, 0.07-0.20 of poses) take another 0.28 of the closing poses.

Not a ceiling yet: 22 random configs is not a search. What would decide it, in order: (1) the Bench(110,360) gate over the
6 J1 seats (on the farm); (2) a plate-footprint gate - the swept area of crank + knee link at their ONE level, short
la / lk (21-26 mm) with the knee folded toward the quiet side; (3) a farm CMA on the near-touch gap from the gate's best
pairs; (4) only then frozen exact. Its complexity (19.0 sensed) is the pin knee's, so the bar is the pin knee (verified
27.20 at margin 5; P5 21.79 self-measured), not the zc class.

## 4. Red team

* The gate is pins only and centre + rim rays; the full model shows the plates are the cap - the gate number is an upper
  bound, not a prediction (its 0.96 became hub 2 0.64 with collisions and the stack).
* O20 at the passive pins is conservative; iglidur pins (5 mm stack, as in the pin knee) would lower the knee stack by
  ~7 mm, which does not rescue a plate fitted at 94 mm against skin at ~55.
* The rigidity margin (RIG_MIN 0.17) was added after the first 22 sweep configs; those configs are pre-margin.
* Bench(60,160) fast throughout; nothing here is on the verification bench yet.

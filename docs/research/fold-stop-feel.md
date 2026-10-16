# Feel of the near-fold J2 stop (minarc-stop-knuckle-4r B vs the pin knee H1), measured

2026-10-16. Script: `docs/research/fold_stop_feel.py`. Raw output: `docs/research/fold/stop_feel_T3.json`. Context:
`docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.md`, red team (5).

**Question for the user.** Variant B's J2 hard stop lets the J1-J2-J3 dyad come within **1.37 deg** of its fold
(1.88 deg on the folded side). Does that meet the 5-deg fold margin? The numbers below are what the wearer would feel.

## Method (quasi-static Jacobian analysis in numpy; no dynamics engine)

* **Chain model.** Every chain is spherical about GH: J1, K and J2 sit on GH rays, and J3's axis passes through GH (its
  offset is taken up by the knee). Member angular velocities and joint torques are therefore moments about GH in one
  3-space. Joint angles come from each model's own `ik`, imported unchanged, with the knee centre m frozen from the
  fit60 shape in the re-measure files.
* **Designs.** Three are measured:
  * **B as claimed**: `best_params`, phi stops at 12.28 / 162.70.
  * **B at the kit rule**: the same parameters with the phi stops moved to the kit's 5-deg J1-J3 margin for
    a1 = 38.07 and a2 = 58.75, i.e. **20.79 / 146.61**. Both stops are moved, because the folded stop at 12.28 breaks
    the same rule.
  * **H1**: the pin knee, `v_polish_params`, with its 5-deg window. Its stops would sit at phi 21.72 / 149.65.
* **Clips.** The six fit clips at the frame rate stored with the pose set: `Z["FPS"]` = **10 fps**, which is the clip
  keyframes resampled over their real duration (`pipeline/conformal/gpu_client/pack_band.py`). That gives 356 frames
  and 312 consecutive pairs per design.
  * Rates come from finite differences.
  * The arm's angular velocity is the rotation vector of Q(k+1) Q(k)^T divided by dt.
  * Accelerations are second differences of keyframe-interpolated data, so they are indicative only.
* **Friction.** Each O20 joint is a preloaded MR117-2RS pair (7 x 11 x 3, contact seals), modelled as Coulomb
  **T = 3 N.mm** per joint. Each knee pin also gets 3 N.mm. The `judge/dynamics.py` reference values are 1 N.mm for
  rolling bearings and 5 N.mm sealed.
  * Statics of the moving joints: u_i . tau = T sgn(qdot_i), so tau = A^-T f, where A holds the world joint axes.
  * The knee pins add their dissipated power.
  * Cuff force = |tau| / |GH to cuff pin b|. That distance is 120.7 mm for B and 118.0 mm for H1.
  * Every friction number scales linearly with T. Multiply by 3.3 for a pessimistic 10 N.mm per sealed pair.
* **K hold.** The torque the chain puts on K in the opening sense has two parts:
  * friction, worst over the friction signs: T ||A^-1 uK||_1;
  * the links' weight: the moments of links 1b and 2 about uK, with world +y up (checked: at elevation 0 the
    humerus points to -y), and the cuff moment closing J1-J3.

  The spring preload must exceed the sum minus K's own friction. Otherwise the rate-independent quasi-static motion,
  which minimises dissipation plus spring and gravity power over the self-motion, opens K before J2 reaches its stop.
* **Stop impact.** The arm's motion is prescribed and continues through the contact. The chain jumps from its state-A
  joint rates, A^-1 w, to the rates with J2 locked: [u1 uK u3]^-1 w for B, or the arm's th-component blocked for H1.
  * Energy lost = 1/2 sum dw_b^T I_b dw_b. This is Carnot's theorem for a plastic impact under a prescribed motion.
  * I_b is taken about GH from the sampled metal: Ti straps 8 x 3 mm at 0.106 g/mm along the hub-to-hub arcs, and O20
    stacks of 6.0 g lower + 9.1 g upper from the `docs/HARDWARE.md` levels. Body masses: B 1a 18.4 g, 1b 20.8 g,
    link 2 28.5 g; H1 link 1 19.8 g, link 2 28.4 g.
  * "Simple" = 1/2 I_2 qdot_2^2 about J2, using the task's definition.

## Results (T = 3 N.mm per joint and per pin)

| design | min fold margin, kit metric (stop / clips / workspace state A) | peak J2 rate ratio (at the stop / on the clips) | peak J2 speed on the clips; at the stop for the clips' peak th-rate / peak arm speed | peak J2 accel on the clips | cuff force from bearing friction: at the stop; clips peak / p99; workspace peak / p99 | stop impact energy at the clips' peak th-rate (60 deg/s) / at the peak arm speed (127 deg/s) | spring K preload needed vs available |
|---|---|---|---|---|---|---|---|
| **B as claimed** (phi 12.28 / 162.70) | **1.37** / 4.02 / 1.51 deg | **6.36** / 2.94 | 108 deg/s; **379 / 805 deg/s** | 526 deg/s2 | **0.39 N**; 0.28 / 0.27 N; 0.40 / 0.33 N | **1.2 / 5.5 mJ** (simple 8.8) | **45 N.mm** (friction 23 + weight 25, minus K friction 3; 100 N.mm at T = 10). Available: about 90-160 N.mm fatigue-rated from a d 1.0-1.2 mm music-wire spring at D 15.5 mm with 4-7 mm of body. That needs 100-198 N.mm at full opening, which exceeds the fatigue rating of the 4-6 mm candidates. |
| **B at the kit rule** (phi 20.79 / 146.61) | **5.00** / 4.02 / 5.05 deg | **3.45** / 2.94 | 108 deg/s; 205 / 437 deg/s | 611 deg/s2 | 0.20 N; 0.28 / 0.27 N; 0.24 / 0.20 N | 0.47 / 2.1 mJ (simple 2.6) | **33 N.mm** (friction 13 + weight 20); 77-125 N.mm at full opening, which fits d 1.0 with N 4-5 or d 1.2 with N 5 within the fatigue rating |
| **H1** pin knee (window 5 deg; stops at phi 21.72 / 149.65) | 5.00 / 10.64 / 5.17 deg | 3.15 / 1.64 | 89 deg/s; 184 / 399 deg/s | 461 deg/s2 | 0.20 N; 0.19 / 0.19 N; 0.23 / 0.20 N | chain only 0.21 / 0.97 mJ (simple 2.0); **the stop blocks the arm itself** | n/a (no K) |

Reading the numbers:

1. **Rate ratio.** J2 turns 6.36 deg per deg of J1-J3 motion at B's stop, against 3.45 at the kit-rule stop and 3.15 for
   H1. On the clips B never reaches the stop (max phi 150.2, peak ratio 2.94). The clips do take B's state A to a
   **4.02-deg** fold margin, which is under 5. H1 stays at 10.64 deg or more on the clips.
2. **Friction amplification is not a feel problem with rolling bearings.**
   * The worst cuff force from bearing friction is **0.39 N at B's stop**, against 0.20 N for the kit rule and H1.
   * On the clips it is 0.28 N against 0.19 N. R17 allows 5 N.
   * At a pessimistic 10 N.mm per sealed pair, B's stop needs 1.3 N.
   * B doubles the friction force at the stop, but the force stays small in absolute terms. With plain bearings
     (load-dependent mu, `docs/research/dynamics_judge.md` item 4) the factor of 2 would matter.
3. **Impact.**
   * Approached at the clips' peak J1-J3 rate (60 deg/s), B's J2 hits its stop at **379 deg/s** and loses 1.2 mJ.
     The kit rule gives 205 deg/s and 0.47 mJ; H1 gives 184 deg/s and 0.21 mJ for the chain only.
   * At the clips' peak arm speed (127 deg/s) the figures are 805 / 437 / 399 deg/s and 5.5 / 2.1 / 1.0 mJ.
   * B's impact energy is **2.6x the kit rule's and 5.7x H1's chain-only impact**. In absolute terms it is a few mJ,
     which is a click at the stop, not a blow.
   * On the clips the kit-rule variant reaches its stop twice, in Wash opposite shoulder, at a J2 speed of only
     6-19 deg/s.
   * H1's stop is a different event. With no K, the stop ends the arm's range, so the arm itself must stop: about
     190 mJ at 60 deg/s, using a 4 kg arm with about 0.35 kg m2 about GH (an estimate). Both B variants keep the arm
     moving and switch to K.
4. **Spring and state choice.**
   * K stays on stop A only if the spring preload beats the chain's opening torque. That torque is **45 N.mm for B**
     (33 for the kit rule) at T = 3, and grows to about 100 N.mm at T = 10. Half of it is the links' own weight.
   * Near the fold, J2 friction amplified by the rate ratio pushes K open. With less preload, K opens *before* J2
     reaches its stop. That is a different state from the model's, because K's opening then depends on the friction
     sign and the weight direction instead of on the arm.
   * At the stop the chain does **not jam**. The J1-K-J3 sub-chain is well conditioned there (condition number 3.9 for
     B, 4.3 for the kit rule), and K opens at 2.1-2.3 rad per rad of J1-J3 motion.
   * Once K is open, the wearer pushes the spring through that ratio. At B's preload this is about 0.8 N at the cuff on
     contact and about 1.7 N at full opening (63 deg). That is a felt but sub-R17 step from 0.4 N.
   * A catalogue-class torsion spring for this duty needs 45 N.mm of preload over 63 deg of stroke. In music wire,
     d 1.0-1.2 mm on D 15.5 mm, that means 4-7 mm of axial body. It does not fit inside the v5 O20 stack (bearings and
     sensor fill 3.65-11.75 mm), so hub K grows. B's duty (100-198 N.mm at full opening) exceeds the fatigue rating of
     the shorter candidates. The kit-rule duty fits d 1.0 with N 4-5. These are sized from the spring formulas; a
     catalogue part number is still to be matched.
5. **Red team: the model's J2 "stop" is not a stop on J2.**
   * In the stretched state the model holds the interior angle phi at phi_hi while K opens. Measured on the workspace
     grid, the J2 joint angle q2 drifts **0 to +14.3 deg** for B (0 to +15.1 for the kit rule) away from its contact
     value as dK goes 0 to -61 deg (correlation -0.98). The drift is in the direction that leaves the stop. The reason:
     phi is measured to J1's axis, and that axis moves in link 1b's frame when K turns.
   * A physical hard stop on J2 fixes q2. In that case the spring keeps J2 pressed on the stop, and the stretched
     poses take a different configuration: q2 fixed, K and the link positions changed.
   * So the 237 stretched grid nodes and the 49 stretched bench poses behind B's 15.42 (and the kit variant's forced
     region) are measured under a law the hardware does not produce. That law would need a constraint linking link 2
     to link 1a's J1 direction across K, which is not a catalogue stop.
   * This needs a re-measure under the q2-stop law before any ruling makes B's number stand.

## Verdict (numbers for the user's ruling)

* **Feel.** The 1.37-deg stop doubles the friction amplification and the J2 contact speed, and gives 2.6x the kit
  rule's impact energy. In absolute terms all of these are small with rolling bearings: 0.4 N of friction at the cuff,
  1-5 mJ per contact, and no jam. A wearer would most likely feel a light click and a spring step of about 0.4-0.8 N
  as K takes over, not a hard stop.
* **What gets worse.**
  * The spring must hold 45 N.mm against the near-fold friction and the weight, against 33 N.mm for the kit rule. Its
    duty exceeds a fatigue-rated spring that fits in a short hub.
  * J2 sees 805 deg/s impacts at the arm's peak speed, against 437 deg/s for the kit rule. That means stop-face wear
    and bumper sizing.
  * Plain bearings would turn B's 2x amplification into a real problem.
* **The bigger issue is (5), not feel.** The model's stop law keeps phi constant, and a real J2 stop cannot do that.
  B's 15.42 (and any kit-rule re-optimisation of this model) must be re-measured with a q2 stop before the fold-margin
  ruling can make it a verified number.

# desmo-slipper-knuckle-3r - Desmo slipper (round 12, judge pick 2)

The verified lead slipper-nose-knuckle-3r (18.49 frozen exact, Bench(110,360)) with its force closure removed:
no clock spring on K, no stop-A pin and no stage-1 roller. Both drive stages are positive both ways:

* stage 1 (hub 2 -> crank): a crowned 440C O1.5 pin, pressed in the crank's short arm, runs in a 1.52 x 1.5 groove cut
  in the underside of hub 2's cap ring (link 2);
* stage 2 (crank -> link 1a, cell A): the verified O2.5 slipper nose runs in a two-walled slot. The slot is the swept
  envelope of the nose (the union of nose discs + 0.01 mm) with the convex material corners closed to R >= rho_e.

3 active DOF (J1, J2, J3). K is slaved and never read. 0 passive translations, 0 springs.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Treat the groove as a 3-D cam, not a planar one. The pin turns about dR, and dR is tilted off u2, so the pin
     drifts along u2 and tilts across the groove. Measure that drift and tilt, then decide the crown from the numbers.
   * Calibrate the cam's sense from the model's own pose transforms, not from a formula. The "with" vs "against"
     arrangement moves the groove pressure angle from about 30 deg to about 78 deg, and one sign error flips the verdict.
     Here the relative rotation of link 2 about u2 per unit K is fitted by regression on the fit bench's taken poses.
   * Measure the slop the wearer would feel: K play with the crank held, and with the crank free in its groove
     clearance. Measure both directions, including the reversal at the dwell exit.
   * Count the new metal honestly. The lead's rim lobe was never sampled past O20. The groove ring's outer wall
     (r <= 10.98) is sampled here as link-2 metal, so this design pays for metal the lead got for free.
   * Keep the lead's seats and law. The gain is complexity (15.75 vs 18.25), so the bench target is a paired tie,
     not a new gap.
2. **Rawest material.** The posed skin itself: the signed-distance cache behind Bench(60,160) and the exact path
   behind Bench(110,360). Also the pose transforms of every body on every bench pose, which give the pin's path in
   link 2's frame directly (no digested cam table). Two further sources: the skin-motion map
   pipeline/conformal/analysis/skin_motion_map_14.json for the hub-2 deltoid region, and the verified lead's geometry
   (docs/research/slipper_mechanism/geo_bench.npz) as a cross-check of the synthesis.
3. **Methods and tools.**
   * Exact spherical-cam synthesis per 0.25 deg of K on the model's own axes: both pressure angles with friction
     (43 - atan(mu)), curvature and cusp, axial drift.
   * Morphological slot check: the nose disc must stay inside the union of swept discs, with K stepped by bisection
     to 0.005 deg.
   * Built on tools/concept_bench.py and the lead's verified model chain, loaded unchanged
     (slipper-nose -> roller-longdyad -> sidecar-roller-flank -> sidecar core), with the frozen-shape claim protocol.
   * The farm (tools/cloud_run.py) for sweeps, then CMA-ES from the top configurations.
4. **What, other than me, shows the number is right.**
   * The bench itself (fast, then exact frozen).
   * A control run: this file with the desmo additions switched off must reproduce the lead's 13.0 fast.
   * The adversarial verifier (docs/concepts/verify/slipper-nose-knuckle-3r.py retargeted).
   * The red-team pose list below: rest, overhead, across the body, behind the back, the lead's two contact poses
     237 / 264, and the dwell-exit reversal.

## What was built

docs/concepts/models/desmo-slipper-knuckle-3r.py wraps the verified lead model (slipper-nose-knuckle-3r.py, SN_CELL=lead),
which is loaded unchanged. Every lead check still runs: the per-0.25-deg stage-2 cam synthesis, friction in the
pressure-angle budget, the cusp check, the lug and arm clearances, the drive-range truncation, the O20 stacks, the part
pairs and the kit fold rule. The file adds the following.

* **capK 0**: the clock spring and its 6 mm cap are gone. The lead model's stop A carried no metal, so deleting it changes
  no sample.
* **Stage 1, exact 3-D.**
  * The pin F0 = s dR + a_s v sits at the cap level PV.u2 + 3.15 + glev and turns sig phi(K) about dR.
  * Link 2 turns about u2 relative to link 1b at s_th per unit K. **s_th is measured** by regression of R_L1b^T R_L2 on
    the fit bench's 90 moving poses: s_th = -0.4644 = -1/kK, rms 0.000 deg. The sense is measured, not assumed.
  * Gates per K step: pitch radius in [7.06, 9.94], both pressure angles <= 43 - atan(0.087) = 38.03, axial drift
    <= 0.6 mm. Each one cuts dK_lim like the parent's limiters.
  * The groove centreline in link 2's frame is built over the dwell plus the rise, with the onset corner blended.
  * The ring sector outside hub 2's O20 (r 10 -> pitch + 1.56) is sampled as link-2 metal. The whole ring, the pin and the
    short arm go on the contact list.
  * Link 2's strap outside O20 + 1.5 is checked against the short arm and the pin in true 3-D, per taken pose: >= 1 mm,
    else the pose is lost.
* **Stage 2, cell A.**
  * The outer wall is the swept envelope of the nose (offsets -(1.25 + 0.01 + s) n, end caps, path filter), sampled as horn
    metal and checked against the low arm per K step.
  * The outer-wall (closing-drive) pressure angles are gated at 38.03.
* **Slop and jam, measured in the model.**
  * Crank HELD: K0 on a 0.5-deg grid, both directions, K bisected to 0.005 deg until the nose disc leaves the union of
    path discs. rho_e 1.0 and 3.5. This includes the reversal at K0 = 0, the dwell exit.
  * Crank FREE, link 2 fixed: the milled groove is the union of O1.52 discs along the blended centreline, and the O1.5 pin
    disc is bisected in K at the dwell, the onset corner and the rise.
  * Gate: one-sided <= 0.25 deg in each case. A failed gate makes the configuration not honest (gap 275 in the sweep).
* Cell B, the pinned-horn inversion, is **not built**. The time went to the stage-1 finding below.

Control: with DS_CONTROL=1, this file reproduces the lead's fast numbers exactly: plain 13.00 and near-touch
objective 16.47.

## The measured finding: the spec's stage-1 placement does not hold K

At the spec's placement (a_s 8.625, psi 184, the proposer's "only a_s ~8.6 reaches 49.75" band), the stroke and the
pressure angles reproduce the proposer: PA cap side 36.2, pitch 7.98 -> 9.41, pa_cap limit at K 53.75. **But the pin
moves WITH the cap.** At K 0, |v_pin| = 3.60 and |v_cap| = 3.70 mm/rad, only 8.3 deg apart, and |v_rel| = 0.54 mm/rad.
That gives the low pressure angle, but it costs two things:

* **The dwell does not hold the crank.** The dwell groove is a circle about u2, and the pin's crank-driven velocity is
  nearly tangent to it. K play with the crank free is g c / |v_F . e_r| = **1.12 deg** at the nominal 0.01 mm clearance,
  4.5x the 0.25 gate.
* **The onset corner is a near-cusp.** The groove turns 50-55 deg while |v_rel| collapses from 7.98 to 1.15 mm per rad of
  q2. Blended over 4 deg of q2, the centreline radius is 0.03 mm, well below the pin's 0.75. The milled groove
  (union of discs) then leaves a pocket, and the K play there is **2.2-3.7 deg** (+K side).

The re-placement fixes both. A grid of 76 configurations (a_s 8.5-9.75, psi 148-158, glev -0.5 / 0, blends 4-10) found
psi 148-156, where the pin's crank motion has a radial component in the dwell:

| a_s 9.25, psi 154, glev -0.5, blend 10 | value |
|---|---|
| dwell / rise / onset-corner K play (crank free, c 0.01) | 0.190 / 0.188 / 0.245 deg (worst tolerance c 0.015: 0.367) |
| slot slop (crank held), rho_e 1.0 / 3.5 | 0.115 / 0.265 deg; engagement PA <= 19.8 (no jam) |
| held + free in series | 0.36 deg (the lead's spring-preloaded K had none; its lag under load was 0.42-0.53) |
| pitch / outer wall | 9.08 (constant) / 10.64 (inside the lead's 11.5 skirt) |
| PA pin / cap (gate 38.03) | 37.91 / 31.37; drive limit 49.75 (pa_pin) vs the parent's 49.5; dK_lim 49.5 >= 46.3 |
| pin tilt across the groove | 4.84 deg -> crowned pin needed (as the spec said) |
| stage-2 outer-wall PA (closing) crank / horn | 29.5 / 32.2; outer wall vs low arm 20.6 mm |
| link-2 exit vs short arm | 13.65 mm min, 0 poses lost |

The blend that the corner needs is **10 deg of q2**: the groove leads the linear law by up to 2.61 deg of K around the
onset. **The bench's IK does not carry this lead**: it uses the linear law. A K lead opens the dyad earlier, so the
stretched-side fold margin only grows, but the metal near the onset sits up to 2.6 deg of K away from where the bench
puts it. A verifier should re-run with the blended law in the IK.

## Numbers (Bench(60,160) fast, then the claim protocol)

| config | plain gap | near2 objective | reach | ib14 | ib10 | contact |
|---|---|---|---|---|---|---|
| lead through this file (DS_CONTROL=1) | 13.00 | 16.47 | 0.775 | 0.895 | 0.513 | 0 |
| spec placement a_s 8.625 psi 184 (fails the slop gate) | 13.65 | 17.21 | 0.775 | 0.8885 | | 0 |
| **best: a_s 9.25 psi 154 glev -0.5 blend 10** | **12.88** | **16.47** | 0.775 | 0.8962 | 0.5245 | 0 |

Attribution on the fast bench (ablations of the best configuration):

* **capK 6 -> 0 changes nothing.** keep_cap=1 gives identical numbers, because the cap is never the skin-facing metal.
* **The ring sector costs 0.33.** ring_rigid=0 gives 12.55 instead of 12.88. It has 9 samples, median 13.9 mm, 51 % in band.
* **Wall sampling density is worth 0.31 and is a measurement effect.** The sweep ran with groove-desmo's dense outer-wall
  sampling: rows at 0.3 / 1.0 / 1.5 mm and a 1.5 mm step, about 1 pt / 1 mm^2. That adds 111 in-band horn points and
  gives 12.88. At the standard ~1 pt / 3-4 mm^2 (one row, 2 mm step) the result is **13.19, +0.19 over the lead's 13.00**.
  The model now defaults to the standard density, and the claim below is re-run with it. The ranking of stage-1
  placements does not depend on it.

Convergence gate on the near-touch objective, 136 configurations (76-config farm grid, then 5 ES generations of 12 on
the farm): gain over the 2nd half 0.00 points, over the last third 0.00, top-5 spread 0.00. **Passes.** The landscape is
flat at the lead's own 16.47: stage-1 placement only moves the ring sector and the gates.

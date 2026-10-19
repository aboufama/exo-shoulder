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

## Claim protocol (frozen shape fitted on Bench(60,160) fast, worn on Bench(110,360) EXACT; farm, then local)

Everything was run through this same file. The lead control is DS_CONTROL=1.

| | frozen exact Bench(110,360) | held out | flood full / knn | near1 | min metal |
|---|---|---|---|---|---|
| lead through this file (control) | **18.49** (reach 0.725, ib14 0.8955, contact 0.0054) | **23.45** | (18.49 / 20.16 lead row) | 20.12 | 0.07 |
| desmo, dense wall sampling (sweep convention) | 18.25 (reach 0.725, ib14 0.8979, contact 0.0054) | 23.20 | 18.25 / 19.92 | 19.88 | 0.07 |
| desmo, standard wall sampling (the claim) | see "Claim at standard density" below | | | | |

In every column the reach, the losses and the contacts are identical to the lead: fold 88, knee slide 9, contact 2
(poses 237 / 264 at elev 165, the lead's lug and crank), overhead 8 / 28, dK taken max 45.62 (held 46.27). On every
taken pose the link-2 exit stays >= 11.89 mm from the short arm (371 bench / 852 held poses). Held out, the ring sector
shows up inside 2 of the lead's own 10 contact poses (m2:ring2) and creates no new contact pose. The dense-wall -0.24
comes entirely from in-band, from the extra in-band wall samples, so it is a measurement effect and not a design gain.

## Red team (own best configuration, frozen exact wear, tools: the model's redteam mode + the slop maps)

* **The pose that jams.** No jam was found. Engagement pressure angles stay <= 19.8 at the slot (both rho_e) and <= 26.1
  at the K0 = 0 reversal, against a 38.03 budget. The binder is **slop, not jam**. With the crank free, K play peaks at
  0.245 deg at x0 = +8 deg past the onset (the corner exit). It reaches 0.367 at the worst groove tolerance (c 0.015),
  and 0.36 in series with the slot's 0.115. That passes the 0.25 gate at nominal fit only. The lead's spring had no play
  but lagged 0.42-0.53 deg under load, so the two are comparable in size and opposite in kind (play vs lag).
* **The point that pinches.**
  * The lead's two dwell contacts remain: pose 237 (crank -9.0, lug -8.5 mm) and pose 264 (lug -5.7 mm). Deleting the
    spring cannot touch them.
  * The new ring sector sits at 3.42 mm at its lowest taken pose (230), and hub 2 is lower there (1.02).
  * The lowest taken pose overall is 139 at 0.07 mm, on the cuff end E: the lead's own.
* **The optimistic numbers.**
  1. The dense wall sampling (-0.31 fast), now removed.
  2. The 10-deg q2 onset blend: the groove leads the linear K law by up to 2.61 deg of K, which the bench IK does not
     carry. It is benign for the stretched margin and unmodelled for the metal.
  3. The proposer's spec placement (a_s 8.625, psi 184) passes every gate the spec listed (stroke, PA, pitch, drift) and
     fails the one it did not list: crank-free play 1.12 deg in the dwell and up to 3.7 deg at the onset corner.
* **Named poses** (frozen exact):
  * Taken: rest (dK 4.6, lowest the horn at 3.57 mm), overhead axial -135 (dK 5.8, lowest hub K at 2.94), across the body
    at plane 120 / elev 90 (horn 3.38).
  * Lost: overhead axial 0 (knee slide), plane-90 overhead, extreme internal rotation, behind the back, abduction 90 and
    extreme external rotation (all fold, the lead's walls).

## Claim at standard density (the number this row reports)

Configuration: a_s 9.25, psi 154, glev -0.5, blend 10 deg of q2, outer wall one row at 0.75 mm every 2.0 mm (about
1 pt / 3 mm^2). Run locally, niced, after the farm hit the 12-hour budget line (balance $24.22, exo-cpu1 workersMax 0).

| | lead through this file | **desmo** | delta |
|---|---|---|---|
| fast Bench(60,160) plain / near2 objective | 13.00 / 16.47 | 13.19 / 16.63 | +0.19 |
| **frozen exact Bench(110,360)** | 18.49 (score 93.28) | **18.63 (score 93.23)** | **+0.14** |
| reach / follow / ib14 / ib10 / contact | 0.725 / 1.0 / 0.8955 / 0.5162 / 0.0054 | 0.725 / 1.0 / 0.8941 / 0.5182 / 0.0054 | in-band only |
| held out | 23.45 | 23.59 | +0.14 |
| near1 (metal < 1 mm = contact), bench / held | 20.12 / 26.54 | 20.26 / 26.68 | +0.14 |
| why lost (bench): fold / slide / contact | 88 / 9 / 2 | 88 / 9 / 2 | 0 |
| overhead taken (elev >= 140) | 8 / 28 | 8 / 28 | 0 |
| flood full / knn (kinematics unchanged) | 18.49 / 20.16 | 18.25 / 19.92 at dense sampling (full = static, 0 dropped) | same drops as the lead |
| complexity (tools/simplicity.py v2.2, the lead's record convention) | 18.25 | **15.75** | -2.5 |

**Verdict: a paired tie with the lead.** It loses 0.14 gap points, all of it from in-band: 9 ring-sector samples at
51 % in band, plus the outer wall. In return it removes the clock spring, the spring cap, stop A and the stage-1
roller, so complexity falls from 18.25 to 15.75. With no spring, the ledger's M5 watch (a spring force-closing a
sliding nose) and the spring-lag problem in the fold margin both go away. In their place come 0.245 deg of K play at
nominal fit (0.36 in series with the slot) and an onset blend the bench does not model.

## What happens next (for the verifier and the loop)

1. **Verifier.** Retarget docs/concepts/verify/slipper-nose-knuckle-3r.py at DSModel.
   * Re-measure the crank-free play with the real groove tolerance.
   * **Put the blended onset law (10 deg of q2, up to a 2.61 deg K lead) into the IK.** This is the one unmodelled
     effect.
   * Run the paired tie rule against 18.49 on the same poses, and the T5 per-pose dump
     (`python3 tools/alignment_paired.py dump`).
2. **The slop margin.** A larger lever (a_s 9.5-9.75, psi 148-152) brings the crank-free play down to 0.16-0.18 deg.
   The cost is r_out 10.9-11.3 (more ring metal, about +0.2-0.3 fast). Pick it if the verifier counts tolerance.
3. **Cell B (pinned horn), not built.** It deletes the 6 mm lug band, which is the lowest part on 71 taken poses.
   That is the only lever here that could make this design better than a tie on the bench.
4. **L1 CAD.** Use the lead's builder: swap the stage-1 roller for a pin, cut the cap groove, add the slot's outer wall.

## Verification (independent skeptic, 2026-10-17)

**Verdict: VERIFIED, not refuted.** Corrected frozen exact Bench(110,360): **18.95 (score 93.11)** against the
champion's 75.94 on the same bench (risley-turret verifier checks, the reference the lead's verification used). Held
out: 23.90. No hard rule is broken. Against the lead it does **not** tie in its own favour: it is +0.46 on the bench and
+0.45 held out, all of it in-band, on identical poses and contacts.

Harness: docs/concepts/verify/desmo-slipper-knuckle-3r.py. It loads the claim's model unchanged, as the last module, and
retargets the lead's verifier (docs/concepts/verify/slipper-nose-knuckle-3r.py) at DSModel. That verifier runs N1-N3
(pressure angle with friction at every taken pose, conjugate undercut, relative pole), the closure in the world, nose vs
lug, K sense and the th margin. The harness adds the continuity flood and per-pose dumps in tools/alignment_paired.py
format. A dense groove probe is in docs/concepts/verify/desmo-slipper-knuckle-3r_groove_scan.py. Everything ran
locally, niced, at most 2 processes (the farm is past its budget line).

| run (frozen exact Bench(110,360) unless noted) | gap | reach | ib14 | ib10 | contact | why lost (fold / slide / contact) | flood full / knn |
|---|---|---|---|---|---|---|---|
| claim config, claim IK (reproduction) | 18.63 | 0.725 | 0.8941 | 0.5182 | 0.0054 | 88 / 9 / 2 | 18.63 / 20.30 |
| claim config, blended onset law in the IK | 18.59 | 0.725 | 0.8945 | 0.5191 | 0.0054 | 88 / 9 / 2 | |
| **verified: pin re-placed a_s 9.5, psi 150, blended IK** | **18.95** | 0.725 | 0.8909 | 0.5148 | 0.0054 | 88 / 9 / 2 | 18.95 / 20.62 |
| verified config, held out | 23.90 | 0.6828 | 0.8898 | 0.5137 | 0.0116 | 260 / 32 / 10 | |
| lead slipper-nose (reference) | 18.49 / held 23.45 | 0.725 | 0.8955 | 0.5163 | 0.0054 | 88 / 9 / 2 | 18.49 / 20.16 |

**What held up.**

* The claim reproduces exactly: 18.63.
* Every check the lead's verifier runs is clean on all 371 bench and 852 held poses:
  * closure 0.0 mm and 0 failing poses;
  * pressure angle plus friction (atan 0.087) <= 43: horn 40.87, crank 34.47 on the bench (horn 41.27 held), and <= 45;
  * no N2 undercut;
  * wrong sense 0;
  * dK taken 45.62 against a limit of 49.5.
* The th margin minimum is 5.181 on the bench and 5.006 held out, the lead's own numbers.
* Overhead taken is 8/28, also the lead's.
* The two contacts sit at the lead's poses and depths: 237 at -9.0 mm and 264 at -5.72 mm. Held out, there are 10
  contacts with 46.13 mm total depth, against the lead's 46.12.
* Complexity reproduces with tools/simplicity.py v2.2: 15.75, against the lead's 18.25.

**What did not.**

1. **The claimed config fails its own determinacy gate under a dense scan.**
   * Method: the claim's own union-of-discs groove test with the crank FREE, evaluated every 0.25 deg of the K law in
     both directions. That is 223 points, against the claim's 9 points up to K 15 and a smooth-groove formula beyond.
   * Result: K play reaches **0.273 deg at K 42** at the nominal c 0.01. It exceeds 0.25 at 10 points: K 6.5-7.3 (the
     corner exit), K 41.75-45.25 (the late rise, inside the taken range) and K 49.4.
   * Cause: the pin moves more and more with the cap, so the centreline radius in link 2's frame falls to
     **0.46-0.63 mm in the late rise, below the pin's 0.75**. The milled groove then has no inner wall there.
   * The docstring lists a "centreline radius >= 1.5" gate. It is computed (rc_min 0.37) but never enforced.
   * By the claim's own rule (free play > 0.25 deg -> not honest) the claimed config is out.
   * Re-placements, dense:

     | placement | dense max | result |
     |---|---|---|
     | a_s 9.5, psi 150 | 0.241 | pass |
     | a_s 9.75, psi 148 | 0.228 | pass, but friction-fragile (below) |
     | a_s 9.25, psi 150 | 0.252 | fail |
     | a_s 9.5, psi 154 | 0.280 | fail |

   * At mu 0.12, a_s 9.75 / psi 148 fails the stage-1 cap-side pressure angle at the dwell exit (dK_lim 0, fast 99.88).
     a_s 9.5 / psi 150 holds to K 46.0 at mu 0.12, where stage 2 binds first, as on the lead.
   * The verified number is therefore a_s 9.5, psi 150. It costs **+0.36**, all of it from more ring metal.
2. **The bench IK does not follow the groove (the claim flagged this; now measured).**
   * The claim's IK uses the linear K law, but its groove leads that law by up to 2.69 deg of K over 10 deg of q2. So on
     the claim's poses the crank's pin sits **up to 0.156 mm off its own groove**: 83 of 184 fit poses are beyond the
     0.01 clearance and 17 are beyond 0.05 mm.
   * The harness's BlendDesign solves those poses on the blended table (t, K) with the parent's closure and fold
     margins. It also restricts the cam calibration to the linear part, so the groove geometry is unchanged.
   * With BlendDesign the pin sits on the groove: 0.020 mm, the centreline sample spacing. The number moves by -0.04.
     The effect is benign, as the claim said.
3. **Paired comparison with the lead** (docs/alignment/remeasure/desmo-slipper-knuckle-3r_vs_slipper-nose-knuckle-3r_paired.json):

   | config | bench | held | pooled |
   |---|---|---|---|
   | verified | +0.46 (CI90 [0.00, +0.56]) | +0.45 (CI90 [0.00, +0.53]) | +0.45, P(desmo better) 0.00 |
   | claim | +0.15 (CI90 [0.00, +0.25]) | | |

   * Every point of the difference is in-band, from the ring sector and the outer wall.
   * There are zero discordant poses: the same ws poses are taken and the contacts are the same.
   * The gain is complexity only: -2.5.

**Watch (not refutations).**

* **Unmodelled clash.** The 9.5 mm short arm and the pin enter hub 2's O20 footprint under link 2's ring, in the layer of
  link 1b's J2 seat. No check covers the arm against the hub-2 stack: l2_check excludes r < 11.5. Link 1b's J2 boss needs
  a relief pocket of about 5 x 4 x 1.5 mm, and the L1 CAD must show it.
* **Arm and pin are contact samples only.** They are not in-band samples. They sit about 1 mm below the ring, whose median
  is 13.9 mm, so they would read in band. Leaving them out is conservative.
* **K play costs fold margin.**
  * Play in series: about 0.36 deg at nominal fit and about 0.48 at c 0.015.
  * Cost: about 0.1 deg of fold margin (da1e/dK 0.22-0.38). The bench margin goes from 5.181 to about 5.08, and held out
    5.006 drops below 5.
  * This is the same class of risk as the lead's spring lag, which was larger (0.42-0.53).
* **Stage 1 now slides where the lead rolled.** The pin pressure angle is about 38 against the 38.03 gate at mu 0.087,
  so the friction coefficient of the 440C pin in the DLC groove carries the margin.

**Next.**

* Re-run the stage-1 placement search with the dense slop gate and the centreline-radius gate enforced, and with mu 0.12
  as a robustness column. The nearest passing placement costs 0.36, so a cheaper one may exist.
* Build cell B (the pinned horn), which deletes the lug band. It is the only lever here that can beat the lead on the
  bench.
* Add the arm-vs-hub-2 pocket to the L1 CAD.

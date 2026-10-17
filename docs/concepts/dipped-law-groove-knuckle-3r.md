# dipped-law-groove-knuckle-3r: a dipped K law that lifts hub 2 off the bunched deltoid

Round 10, lens 3. The lead (roller-longdyad-knuckle-3r) slaves the knuckle K to q2 through the hub-2 lobe, the bell
crank, the roller and the flank. Its law is monotone: K rests on stop A until the stretched rise.

Here the lobe gets a **dip** in the mid-folded band (th ~45-62). K closes below the old stop A, so the effective first
link a1e shortens and hub 2 rides up toward hub 1. K reopens to 0 before the folded wall and rises on the stretched side
exactly as before.

- **Lead cell**: the lead with kneewin's centred knee (lE 82, lc 27, phiE 3.8, phib -96.6, ang_min 20). Its only measured
  failure, 19.33 frozen, was hub 2 in the skin on poses 182 and 203.
- **Control cell**: kneeless-roller.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - **Use a C1-smooth dip, not the spec's parabola.** The spec's bump, a1e = a1 - D max(0, 1 - x^2), has a slope
     discontinuity of 2D/w deg/deg at both band edges. A cam cannot follow that without an acceleration spike. At the
     follower it is a kink in the lobe, which sets a pressure-angle and contact-stress spike exactly where the dwell ends.
     I use (1 - x^2)^2: zero slope at both edges, the same peak D, a half-width w. The parabola stays available as a
     switch (dip_shape 0) for the control.
   - **Synthesise the cam over the negative K range in the world.** Extend the flank synthesis and every drive
     clearance (crank vs hub K, roller vs hub K, the low arm vs the swinging lug) down to -D_K - 1 deg. Then the backward
     crank swing is checked, not assumed. The lobe crest grows by s_arm D_K / g, and that growth goes into the
     lobe-skirt rule.
   - **Check that the dip is a function of q2, not of th.** The lobe sits on hub 2, so the cam reads q2. Over the band,
     th(q2) must stay strictly monotone with dq2/dth <= 3.45 on a 0.25-deg grid, and the lobe's own pressure angle must
     stay <= 43, otherwise it is not a cam.
   - **Test everything the dip moves, not only hub 2.** That means links 1a / 1b, hub K, the crank (backward), the
     roller, the horn lug, and the hub 1-hub 2 centre distance at the folded knuckle. Use the design's own per-part
     split, applied per pose to the band poses.
2. **The rawest material.**
   - The posed skin through the bench's exact signed distance (CB_EXACT=1) on every Bench(110,360) pose and every clip
     frame in th 36-72.
   - The lead's own IK branch per pose: th, dK, a1e, m3e, the knee state.
   - The per-pose metal minimum per part, before and after the dip, on the same poses.
   - Not the judge's hub-2-only table, and not twosided.py's elevation-rule branch. Both are re-derived here through the
     design's own ik.
3. **The methods and tools.**
   - The lead's model code, loaded unchanged. A design subclass replaces only the state-A branch of the IK and the drive
     synthesis range.
   - The frozen protocol: fit on Bench(60,160) fast, freeze, wear on Bench(110,360) exact, and on the held-out set.
   - D = 0 controls that must reproduce 19.33 and 18.67.
   - A farm sweep over D, th_c and w, then a CMA-ES around the top, with the convergence gate.
4. **What, other than me, shows the number is right.**
   - The bench, and the frozen exact Bench(110,360) wear (plain, 1 mm, 2 mm) next to the D = 0 control from the same
     code.
   - The round's roller-flank verifier, docs/concepts/verify/roller-longdyad-knuckle-3r.py. It checks cam closure, the
     pressure angles, and K inside the drive's range.
   - A red-team pose list: 182, 203, 205 and 230, the dip-band clip frames, and the deep pair 208 / 211.

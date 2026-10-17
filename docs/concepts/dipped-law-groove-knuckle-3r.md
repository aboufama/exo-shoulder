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

## Verdict (screened 2026-10-17 ~04:45 UTC)

**Level with the lead, not a lead change.** At the best dip, frozen exact Bench(110,360) is **18.64** (score 93.22).
The lead is 18.67 and this cell's own D = 0 control is 19.33. The difference, -0.03, is under the 1-point rule.

The dip works the way the judge predicted: it lifts hub 2 and removes skin contacts. The best dip is dipD 1, th_c 53,
w 12, with the bent arm built at the dip floor. Against the control:

- Contact poses 6 -> 4.
- But the roller-flank drive pays with stretched stroke: dK_lim 46.2 -> 43.8, fold losses 88 -> 90.
- Reach 0.725 is unchanged, overhead 8/28 is unchanged, in-band 14 rises 0.8976 -> 0.8993.
- The recovered pose 203 sits at 0.48 mm. At 1 mm counted as contact, the dip gives 20.81 against the lead's 20.30, and
  the 2 mm gap is 35.69 against the lead's 33.10.
- Deeper dips lose: dipD 4 gives 21.10.
- **Held out, the dip loses.** dipD 1 gives 24.07 against its own D = 0 control at 22.97 (fold 261 -> 273, contacts 17
  = 17) and the lead's 23.73. The bench gain is the two poses 182 and 203. The stroke cost carries over to the held-out
  set; the contact gain does not.
- Side finding: the centred-knee control (kneewin), rejected on the bench at 19.33 against 18.67, is 0.76 better than the
  lead held out (22.97 against 23.73).

The one roller and flank must carry K both ways. The flank's usable stroke under the 43-degree pressure-angle rule is
~46 deg of K, counted from where the bent arm is built. A dip of D degrees of a1e needs ~2.35 D degrees of K below the old
stop A, and that comes straight off the stretched end. The arm cannot be built at the old rest and swung backward:

- it closes on hub K's cylinder at 0.18 mm per degree of backward swing (1.14 mm at rest, under 1 mm by -0.75 deg);
- the flank cusps below about -5 deg.

So the arm has to be built at the dip floor (dip_ref 1), and that moves the whole pressure-angle curve up.

| lead cell (lead + kneewin centred knee), same code | fast plain | fast near-2 mm | dK_lim | frozen exact Bench(110,360) |
|---|---|---|---|---|
| dipD 0 (control = kneewin) | 14.28 | 20.20 | 46.2 | 19.33 (kneewin, reproduced fast to the digit) |
| **dipD 1, th_c 53, w 12, arm at floor (best)** | 15.39 | 23.71 | 43.8 | **18.64** (1 mm 20.81, 2 mm 35.69) |
| dipD 1, th_c 50, w 8 (best D > 0, fast) | 15.26 | 28.11 | 43.5 | |
| dipD 2 (3 band shapes) | 15.90 | 34.5-35.6 | 41.0-41.2 | |
| dipD 3 (3 band shapes) | 17.17 | 48.3-51.8 | 38.5-38.8 | |
| dipD 4, th_c 53, w 12, arm at floor | 16.64 | 60.58 | 36.5 | **21.10** |
| lead roller-longdyad-knuckle-3r (verified) | 13.19 | | 46.25 | 18.67 |

Frozen exact Bench(110,360), dipD 4, compared with its own D = 0 control (kneewin 19.33):

- Contact poses 6 -> 3. This is the dip's gain, about the 2-3 poses the judge sized.
- Fold losses 88 -> 101. The stretched drive wall drops with dK_lim (46.2 -> 36.5).
- Reach 0.725 -> 0.697. Overhead (elev >= 140) stays at 8/28. In-band 14 0.8976 -> 0.9031; in-band 10 0.5152 -> 0.5316.
- Parts: 5 E-L2 jams, the centred knee's (unchanged).
- Minimum metal 0.07 mm at workspace (-60, 60, 105), the same pose and depth as the lead.
- Near-touch: 2 mm gap 78.38 (83 poses under 2 mm), 1 mm gap 22.75.

## What was measured

1. **Faithful model on the lead's code** (docs/concepts/models/dipped-law-groove-knuckle-3r.py).
   - The state-A branch of the design's own IK runs on a1e(th) = a1 - D b(x).
   - The design's closure branch is used, not twosided.py's elevation rule.
   - D = 0 reproduces kneewin's fast numbers exactly: 14.28 / 0.7812 / 0.8972 / 0.0212.
   - Spec fixes:
     - The parabola is replaced by a C1 bump (the parabola kinks at the band edges).
     - msub is not required on dipped poses. It is the stretched law's free-K rule. State-A poses sit at msub 0.2-0.6, and
       requiring it threw away every dipped pose.
     - The cam is checked as a function of q2: monotone, rate <= 1.9 against 3.45, lobe pressure angle <= 25 at D 8.
       The lobe dip is only 0.07-0.53 mm deep.
2. **The drive over the closing range.**
   - The roller-flank synthesis now runs over [-D_K - 1, dK_lim].
   - Built at the old rest (dip_ref 0), the dip stops at -0.75 deg (CRK-hubK) and the flank cusps at -5 to -8 deg. Every
     dipped pose past -0.75 is truncated: fast plain 39.45 at D 4.
   - r_c 16-18 clears hub K (2.3-3.2 mm), but at rest the flank cusps or the horn pressure angle reaches 40-102 deg.
     The flank is sharply tuned at the lead's r_c 15.22.
   - Built at the dip floor (dip_ref 1), the closing side is clean down to the floor at every D tried (1-4). dK_lim then
     falls about 1:1 with the floor: 46.2 -> 43.8 / 41.2 / 38.8 / 36.5 at floors -2.4 / -4.7 / -7.1 / -9.4.
3. **What else the dip moves.** Fast bench, D 4, dip_ref 1, all 41 dipped poses kept:
   - Hub 2 is farther on 21 poses and closer on 15. The fitted hub-2 level changes too, so the judge's "never closer"
     check, which held the geometry fixed, does not carry over.
   - Crank, roller and horn are closer on 20-25 poses, by up to 1.8 mm. Hub K is closer on 10.
   - Links 1a and 1b barely move.
   - In-band 14 rises slightly (0.8972 -> 0.9018). There are 25 clip frames in th 36-72 on the fit bench.
4. **The farm.** A 242-configuration LHS co-fitting the drive (r_c, beta, g, lift, hl, s_arm, zr, kK) with the dip at
   dip_ref 0 went out at 04:03 UTC. The endpoint showed 16 jobs in progress and no completions for over 30 min, so it had
   not returned when the time box closed. The 1-D trade above (10 configurations) ran locally, one process.

## Red team (own best)

- **The pose that jams.** No jam comes from the dip: the 5 E-L2 jams are the centred knee's (184, 208, 209, 211, 238).
  The drive's tightest clearance moves to the arm vs hub K at the dip floor: 1.04 mm at -10 deg, the edge of the 1 mm
  rule.
- **The point that pinches.** 0.07 mm at (-60, 60, 105), unchanged from the lead. With the dip, 83 poses carry metal
  under 2 mm (near-2 gap 78.38). The crank's built-at-floor phase lowers the arm over the deltoid on the dipped poses.
- **The optimistic number.** The judge's 18.24 (= 19.33 - 2 x 0.548) assumed nothing else moves. The flank stroke moves:
  -9.4 deg of dK_lim at D 4 is 13 more fold poses. Even D 1 (floor -2.4 deg) costs 2.4 deg of stroke, about 2-4 poses
  of the 360 bench, which is about the 1-2 hub-2 poses it can lift.

## New knowledge (predicts beyond this morphology)

- **On a single slaved flank, any non-monotone K law spends the same stroke as the stretched rise.** The roller-flank's
  PA-capped stroke (~46 deg at the lead's seats) is a budget measured from the arm's build phase, not from stop A.
  A dip floor at -k costs k of stretched stroke, at ~2.35 deg of K per deg of a1e on the lead's dyad (bk1 26, bk2 38).
- **The dip needs the total stroke the round-9 long flank was refuted at.** Keeping the lead's 46 deg on the stretched
  side and adding a 4-deg dip needs ~55.6 deg in total. That is exactly the 55-57.5 deg regime where the flank boss sits
  on the deltoid (roller-longdyad-knuckle-3r: 88-94 contact poses, co-fits walk back to 42-47). So co-fitting the drive
  is predicted not to rescue this embodiment.
- **The lever needs a second, independent K input below stop A.** Two candidates: a groove + nose desmodromic pair on
  hub 2's cap (embodiment 2: its stroke is not the flank's), or a dip in stop A itself. Either pays for the dip outside
  the flank's budget.
- **The bent arm concentric with hub K is a one-sided design.** Backward swing closes on hub K at 0.18 mm/deg. Any law
  that runs the crank below its build phase must move the build phase.

## Files

- Model: docs/concepts/models/dipped-law-groove-knuckle-3r.py. Modes: check / split / frozen / held / flood / viz.
- Sweep: docs/concepts/sweeps/dipped-law-groove-knuckle-3r.json.
- Row: docs/concepts/rows/dipped-law-groove-knuckle-3r.json.
- Preview: docs/concepts/viz/concepts/dipped-law-groove-knuckle-3r.js (best D > 0 config: dipD 1, th_c 50, w 8, arm at
  the floor).

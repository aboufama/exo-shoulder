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

## Verification (independent skeptic, 2026-10-17 ~06:10 UTC)

**Verdict: VERIFIED (not refuted). v_gap 18.64 (score 93.22) on Bench(110,360) exact, fit-60 shape frozen. The
champion spherical 3R scores 75.94 on the same bench (risley-turret verifier; 66.97 through the knuckle code and
checks).** Level with the lead, and not a lead change.

Harness: `docs/concepts/verify/dipped-law-groove-knuckle-3r.py`. It loads the claim's model unchanged and runs the
round's roller-flank verifier protocol (fit on Bench(60,160) fast, freeze, wear on Bench(110,360) exact and on the
held-out set), retargeted at `DipModel`.

The parent verifier's per-pose drive checks read |dK| and build the crank at K = 0, which is wrong for this design. The
dip runs K negative and builds the crank at the dip floor, so read that way every dipped pose would look like
wrong-sense or off-flank. The harness rewrites those checks on the signed opening and the build phase kref.

It also adds checks that no parent verifier had:

- **Frame consistency:** J2's axis must agree between link 1b and link 2, J3's axis between link 2 and member 3. K's
  angle read from the frames must equal dK, and a1e read from the frames must equal a1 - dip(th).
- **Lobe cam closure:** every taken state-A pose must sit on the cam curve (q2 from the frames, K) of the dipped
  closure at its own th.
- **Single-valued cam:** q2(th) must be monotone over the whole dwell [th_lo, th_hi], not only over the band.
- **Coupled rate:** dq2/dth at each dipped taken pose.
- **Envelope:** a run with the lug's flank-edge strip rebuilt on the signed flank path.
- **Control:** the same harness run on the D = 0 control.

All wears ran locally, one process at a time (nice, OMP 1, 2-4 min each). The farm rule (>= 3x saving) did not apply,
and the claimant had seen the farm queue stall. Outputs are in `docs/concepts/verify/dipped-law-groove-knuckle-3r_v_*.json`.

| frozen exact | plain | 1 mm | 2 mm | reach | follow | ib14 | ib10 | contact | min metal |
|---|---|---|---|---|---|---|---|---|---|
| Bench(110,360), claim's sampling | **18.64** | 20.81 | 35.69 | 0.725 | 1.0 | 0.8993 | 0.5197 | 0.0107 | 0.07 mm |
| Bench(110,360), envelope-corrected (lug flank-edge strip on the signed path) | 18.57 | 20.74 | 35.69 | 0.725 | 1.0 | 0.9002 | 0.5234 | 0.0107 | 0.07 mm |
| held out | 24.07 | 26.94 | 38.72 | 0.681 | 1.0 | 0.8982 | 0.5188 | 0.0196 | 0.33 mm |
| D = 0 control (kneewin), same harness, Bench(110,360) | 19.33 | 20.96 | 35.08 | 0.725 | 1.0 | 0.8976 | 0.5152 | 0.0159 | 0.07 mm |
| lead roller-longdyad-knuckle-3r (verified) | 18.67 | 20.30 | 33.10 | 0.725 | 1.0 | 0.8937 | 0.5132 | 0.0054 | 0.07 mm |
| champion spherical 3R, same bench (risley-turret verifier) | 75.94 | | | | | | | | |

The claim's frozen bench, held-out and D = 0 numbers all reproduce to the digit. The fast fit numbers also reproduce:
15.39 for the dip and 14.28 for the control.

**Checks on every taken pose: 0 of 371 fail on the bench and 0 of 850 held out, at a pressure-angle rule of 43 and of
45 degrees.**

- **Roller-flank drive, on the signed K:**
  - Cam closure in the world is 0.0 mm.
  - The roller centre stays at least 3.733 mm from the lug's mid-shell (roller radius 3.0).
  - K stays inside the drive's range [-3.0, 43.75]. Taken poses span -2.37 to 43.66 on the bench and up to 42.52 held
    out.
  - Pressure angles: crank 8.3, horn 42.9.
  - Lobe pressure angle: 23.2 on the stretched rise, 2.1 on the dip.
  - The drive is not idle.
- **Frames:** every consistency error is <= 0.0001 deg, and a1e equals a1 - dip(th) exactly.
- **Lobe cam closure:**
  - q2 and K sit on the cam curve to 0.0 deg on every taken state-A pose (85 dipped on the bench, 203 held out).
  - The cam is single-valued over the whole dwell: q2(th) is monotone on th 24.7-77.9 with rate <= 2.29. That maximum
    is at the folded end of the dwell, where K = 0, so it is not caused by the dip.
  - The coupled rate at dipped taken poses is <= 1.764, against the 3.45 limit.
- **Continuity flood:** the full grid drops 0 poses (18.64). The knn grid drops 6 (20.32; the lead is 20.34).
- **Fold margin:** under its literal rule, the lead verifier's `th_margin` fails 84 bench and 202 held-out poses. That
  rule takes min(m_sub, m_eff) on every pose where K is off its rest. Every failing pose is dipped, with m_sub
  0.20 / 0.18. This is not a singularity of this chain:
  - With K slaved to q2, the active Jacobian [s1, s2 + K'(q2) sK, s3] is singular iff the coupled dth/dq2 = 0. Rotations
    about s1 and s3 leave th unchanged, so the q2 column changes th exactly when it lies outside span(s1, s3).
  - m_sub ~ 0 only says that K moves th little. In the dip, J2 does the moving: q2 spans 40 deg while K moves 2.4 deg.
  - The coupled reading uses m_eff on the dipped poses (min 21.7 bench, 21.4 held out) and the lead's rule elsewhere.
    Its minimum is 5.389 on the bench and 5.406 held out, with 0 poses under 5. Together with the coupled rate <= 1.76,
    this means the claim's correction (msub not required on dipped poses) stands.
  - The D = 0 control reads 5.181, with 0 under 5, the same as the lead.
  - Family verifiers should carry the coupled-rate check for any non-monotone K law.

**What the dip is worth.** Measured with this harness, against its own control on the same code:

| | dip vs control |
|---|---|
| bench | 0.69 better (contact poses 6 -> 4, fold 88 -> 90, reach 261/360 unchanged, overhead 8/28 unchanged) |
| 1 mm | 0.15 better |
| 2 mm | 0.61 worse |
| held out | 1.10 worse (fold 261 -> 273, contacts 17 = 17) |

Against the lead:

| | dip vs lead |
|---|---|
| bench | 0.03 better (under the 1-point rule) |
| 1 mm | 0.51 worse |
| 2 mm | 2.59 worse |
| held out | 0.34 worse |

**Issues the verifier raises.** None of them breaks a hard rule.

1. **The dip is a 0.068 mm feature on the lobe.** 10 um of lobe-profile error is 0.35 deg of K, against a 2.37 deg dip
   floor: 15 % of the dip per 10 um. The follower's MR63ZZ radial play is in that range. The two bench poses the dip
   recovers sit on that tolerance, and pose 203 ends at 0.48 mm.
2. **The gain does not generalise.** It is 2 contact poses on the bench. Held out, the stroke cost (dK_lim 46.25 ->
   43.75) wins.
3. **The motion preview shows th_c 50 / w 8,** the best D > 0 fast configuration. The row's best_params are th_c 53 /
   w 12, the configuration whose frozen number is claimed.
4. **The search is not converged.** The 242-configuration farm co-fit of the drive did not return, so "screened, not
   dead" is right. The claim's prediction (deep dips cannot be rescued by the flank) is untested.

**Hard rules hold:**

- 3 active DOF (J1, J2, J3).
- K is slaved by the spring-closed lobe and the roller-flank. It is never read and sits on the cam curve at every taken
  pose.
- The knee pins are closed by the cuff.
- 0 passive translations.
- No gears, pulleys or cables.
- Parts are at the lead's verified sizes, with the crank, roller and lug posed at the signed K.

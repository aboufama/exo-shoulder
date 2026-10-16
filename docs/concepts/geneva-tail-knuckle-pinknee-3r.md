# geneva-tail-knuckle-pinknee-3r: a one-tooth Geneva tail that slaves the knuckle to q2

Status: screened (round 6). Model: `docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py`. Sweep:
`docs/concepts/sweeps/geneva-tail-knuckle-pinknee-3r.json`. Row: `docs/concepts/rows/geneva-tail-knuckle-pinknee-3r.json`.
Motion preview: `docs/concepts/viz/concepts/geneva-tail-knuckle-pinknee-3r.js`.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Write the drive as the exact spatial contact, not a planar ratio. Every axis passes through GH, so the roller centre
     and the flank both live on the unit sphere. The law is then exact in 3-D: a flank half-plane through K's axis, and the
     roller on a small circle about u2. The pressure angle and the contact radius fall out of the same geometry.
   - Check the passive coordinate's equilibrium, not just the law: could the spring park K off the roller at a smaller
     opening along the pose's self-motion curve? If it can, q2 no longer gives K.
   - Price the swept volume of the rigid tail before tuning anything. A part rigid with link 2 turns about u2 through
     J2's whole range. Its height is set by the highest skin under its whole sweep cone, and by link 1b, which it crosses.
     That surface of revolution is the honest stacking rule.
   - Treat the tail length as a seat variable. L_t is about bk2, so the tail is short only if K sits near J2.
2. **The rawest material.** The posed skins of the bench itself: the signed distance of every tail sample on every pose,
   from the bench's `needed()` trace on the skin and not from a digested atlas. Also the fit clips' frame order for
   continuity, and the workspace poses for reach.
3. **Methods and tools.**
   - A closed-form law on a 0.1-deg q2 grid.
   - Th_law inversion: the J1-J3 angle along the law is independent of the pose, so a stretched pose is solved by
     interpolation.
   - Per-t gates: monotone, rate, pressure angle, tooth extent, stop B and lift-off.
   - The kit-rule B model's checks: closure, continuity, fold margins of 5 deg, every part pair, and the near-touch
     objective.
   - The farm for LHS and CMA. The frozen exact Bench(110,360) for the claim.
4. **What, other than me, shows the number is right.**
   - The bench, with skin distance on every sample.
   - The judge's law-only reproduction: 14.34 fast at LB1 here, against the judge's 13.79-14.34.
   - The red-team pose list: rest, overhead, across the body and behind the back, with the tail-tip skin heights.
   - The verifier harness of minarc B, which this model subclasses unchanged except for the stretched state and the
     tail.

## The mechanism

- minarc B under the kit rule, using the physical q2 stop, the K cap (+6 mm) and the pin knee.
- The stretched J2 stop is replaced by a drive. Link 2's strap continues past hub 2 as a rigid tail of arc L_t, with an
  MR63ZZ roller at its tip.
- One flank fixed to link 1a takes the roller. Past the onset q2hi, which sits at smhi from the fold, the roller turns K
  open by dK(q2). K is never read.
- The folded side has no tooth.
- Count: 0 passive translations. Passive rotations: K (slaved) and the 2 knee pins.

### Exact law

The parameters are:

- **t:** the q2 travel past the onset.
- **p(t) = R(u2, q2hi + s t) p0:** the roller centre, in link 1b's frame.
- **az, p_perp:** the azimuth and perpendicular distance of the roller about uK.

The flank azimuth that keeps the roller tangent is `az_pl = az + s_m asin(rho / |p_perp|)`, and the law is
`dK = -(az_pl(t) - az_pl(0))`.

The tail tip p0 is placed by two variables:

- **d_mm:** the closest approach of the roller to K's axis.
- **psi_c:** the q2 travel at which that closest approach happens.

The side is chosen so that the pushed flank opens K. The flank must be inside the roller's path ("inside", L_t = bk2 - d)
or outside it.

### Gates per t

The valid prefix ends at the q2 dowel, stop B. A t is valid only if all of these hold:

- th rises;
- dq2/dth <= 3.45;
- the pressure angle is <= 45 deg;
- the contact radius is <= 10 mm on the cap (crown) or <= lug_max (beside);
- |dK| <= K's stop B;
- the spring cannot park K off the roller along the self-motion curve.

At LB1 with psi_c 0 (closest approach at the onset), the pressure angle hits 45 at dK 17 deg. With psi_c 6 (a Geneva
entry), dK reaches 56 deg inside 45 deg of pressure angle.

### Tail metal

- **LT** is an 8 x 3 strap on member 2, skin-fitted like every link and counted in band.
- It ramps at 60 deg from hub 2's upper level to a tip floor:
  - crown embodiment: the roller bottom sits at K's cap top + 1 mm, and the strap at + 3 mm above that;
  - beside embodiment (d >= 14 mm): the roller runs beside hub K against a lug on link 1a (lug sampled), and the strap
    sits at link 1a's top + 1 mm.
- The tail is stacked over link 1b by the surface-of-revolution rule. At each angular distance from u2, it clears every
  link-1b point at that distance by 1 mm.
- The roller boss (O8 x 3) hangs below the tip. It is skin-checked and in band.
- Part pairs: LT and the roller against hub 1, K (the cap counts, exempt only while the law says the parts touch), hub 3,
  L1a, L1b, the knee, the pad and E, at >= 1 mm.

## Measurements (Bench(60,160) fast, near-touch objective)

| config | gap | reach | in-band14 | contact | note |
|---|---|---|---|---|---|
| LB1, law only, psi_c 0 | 23.01 | 0.688 | 0.908 | 0.018 | closest approach at the onset: pressure gate at dK 17 |
| LB1, law only, psi_c 6 | **14.34** | 0.794 | 0.900 | 0.037 | reproduces the judge's law-only 13.79-14.34 |
| LB1 + tail, crown (d 7) | 56.48 | 0.700 | 0.848 | 0.162 | tail in band 0.25 (median 20.6 mm), roller 0.04; 30 poses dropped |
| LB1 + tail, beside (d 15) | 39.24 | 0.706 | 0.861 | 0.093 | tail in band 0.15 (23.6 mm), roller 0.10 |

**The decisive unknown (the tail metal) is measured.** At the judge's seats it costs 25-42 points, against the kill
threshold of 4.

The reason is geometric. A tail of L_t ~ 41 deg (~46 mm) rigid with link 2 sweeps a cone of half-angle L_t about u2
through J2's whole range. Its tip passes over skin that needs it 92 mm from GH (the trapezius side), while hub K's base
sits at 55 mm. The tail also has to stack over link 1b, which it crosses.

The sweep below searches the seats where the tail can be short (bk2 small, i.e. K close to J2).

## Search (farm, Bench(60,160) fast, near-touch objective)

- **Stage 1, LHS 256:** bk1 20-60, bk2 20-50, a1max 42-75, smhi 5-14, smlo 5-10, d 5-18 mm, psi_c 0-12 deg; seats at LB1.
  Best 30.18 (beside, bk2 34.5, L_t 22 deg).
- **Stage 2, 256 perturbations of the top 8:** half of them also move the J1 / J2 / J3 seats. Best **28.66** (crown, bk1
  35.92, bk2 26.54, a1max 50.16, smhi 10.21, smlo 6.17, d 8.54 mm, psi_c 3.62).
  - Reach 0.713, in-band 0.874, contact 0.040.
  - The law alone at the same seats gives 18.88, so the tail costs 9.8 points there.
- **Gate (506 tries):** the best gained 0.55 score points over the second half and 0.02 over the last third, and the
  top-5 spread is 0.55. That passes, but only over a 2-stage search; CMA was not run inside the time box.

| config | fast gap (near-touch) | law only, same seats | tail cost |
|---|---|---|---|
| LB1, crown d 7 | 56.48 | 14.34 | +42.1 |
| LB1, beside d 15 | 39.24 | ~14.5 | +24.7 |
| best (stage 2), crown | **28.66** | 18.88 | +9.8 |

## Red team

1. **The pose that sets the tail's height.** One workspace pose (plane -30, elevation 60) alone needs the tip 92 mm from
   GH. Hub K sits at 55-60 mm. Coupling the tip need into every tail row of the greedy pose drop dropped more poses and
   scored worse (35.15 against 30.72), so the better pose choice was kept. Either way the rigid height is the maximum
   over the poses kept.
2. **The optimistic numbers:**
   - r_law = 70 mm in the law; the real tip radius differs (the rho / r effect is under 0.5 deg).
   - K's stack flip is not applied to the link levels: L1a and L1b swap 3.15 mm at K.
   - The lug of the beside embodiment is sampled for the skin, but not for part pairs.
3. **The point that pinches:**
   - The roller axis is fixed in the tail, which turns about u2 at 26-47 deg to uK. A cylindrical roller would therefore
     edge-load the flank, so a crowned roller with point contact is needed.
   - At dK > 45 deg, the radial flank's pressure angle passes 45. The law's valid prefix ends there, which is the
     physical stop B.
4. **Local against farm:** 30.72 locally against 30.18 on the farm at the coarse best (0.5 points).

## The merged fallback embodiment: lobe -> rocker -> pushrod ("rod", built after the tail failed its gate)

The tail cost more than 4 points, so per the spec the fallback was built in the same model (`emb_mode` "rod"). The drive
chain is:

1. A constant-pressure spiral lobe on hub 2's rotor rim (link 2, r_lobe 9 mm inside the O20 stack).
2. A rocker on link 1b beside hub 2 (O10 x 9; its base disc is sampled and counted in band).
3. An O3 pushrod with M3 rod-end heads (O10, both ends sampled).
4. A horn of radius r_horn on K's cap (link 1a, flipped stack).

The law is dK = kK t past the onset. The lobe profile makes it linear, with tan(pa) = kK r_horn / r_lobe. The same
gates apply as for the tail (rate, pressure angle <= 45, K stop B, lift-off), and the end of the valid prefix is the q2
dowel, stop B.

Nothing in this embodiment sweeps over the skin: the rocker, rod and horn ride on link 1b / K and move a few mm. The rod
is sampled rigid with link 1b; its 1-2 mm slide and the horn's arc are ignored.

A "rod-low" variant was also built. The rod runs at strap level against a horn lug on link 1a (r_horn >= 16 mm) and needs
a rocker ratio of 3, so kK <= 1.7. It is also sampled.

| config (Bench(60,160) fast) | near-touch gap | plain | reach | in-band14 | contact | min metal |
|---|---|---|---|---|---|---|
| LB1 seats, kK 3, r_horn 2.6, law only (no drive metal) | 15.71 | 14.55 | 0.781 | 0.905 | 0.027 | 0.40 |
| LB1 seats, kK 3, r_horn 2.6, + rod metal | 20.37 | 19.21 | 0.781 | 0.853 | 0.027 | 0.40 |
| rod LHS 256, best | 21.18 | 20.03 | 0.781 | 0.850 | 0.032 | 0.78 |
| rod-low LHS 256, best (kK 1.56, r_horn 16.9) | 19.94 | 19.94 | 0.738 | 0.885 | 0.022 | 1.82 |
| **rod CMA (4 x 8-process farm jobs, 1957 tries with r_horn >= 2.45), best** | **16.53** | 16.53 | 0.794 | 0.846 | 0.005 | 1.05 |

The rod CMA best has these parameters:

- drive: kK 3.18, r_horn 2.49, pressure angle 41.4;
- knuckle and stops: bk1 31.25, bk2 37.99, a1max 58.36, smhi 13.69, smlo 5.28;
- seats: az1 93.55, el1 67.36, az2 43.46, el2 43.31, wd 63.34, wa -9.65, b3 0.384;
- knee: lE 67.83, lc 25.81, phiE -2.79, phib -65.67, stk 4.85, ang_min 27.85.

At that best, K is driven up to 42.6 deg on 68 stretched poses, the rate dq2/dth stays <= 0.58, and follow is 1.0.

**Gate on the rod search** (LHS + CMA in order, 1957 tries): the best gained 0.36 score points over the second half and
0.00 over the last third, and the top-5 spread is 0.19. It passes.

The drive metal costs about 4.7 points at LB1, against 25-42 for the tail. The rod-end heads sit 20-22 mm over the skin
(0 % in band), and the rocker sits at 0.94.

**The tail CMA was an objective loophole (red team).** Its best rows (16.10 fast) are designs where the drive never
engages: the tooth lies outside r <= 10 mm at the onset, so the law has no valid prefix. That leaves an idle K and a
plain 3R window at smhi 5, and with bk2 ~ 20 deg link 1b has no exposed strap. Those rows are NOT this morphology. They
are excluded, and the tail embodiment's honest best stays the stage-2 28.66.

Two lessons for every slaved-knuckle search:

- The objective must require the drive to engage, for example 100 points when stretched_kin = 0.
- The kit should flag a link with no sampled metal.

## Frozen check (Bench(110,360) exact; shape fit on Bench(60,160) fast and worn without refit, the round-3 protocol)

| design | fit (fast) | frozen gap | score | reach | in-band14 | contact | near-touch | overhead | min metal |
|---|---|---|---|---|---|---|---|---|---|
| **rod CMA best** | 16.53 | **23.37** | 91.5 | 0.731 | 0.846 | 0.011 | 25.01 | 8/28 | 0.45 mm |
| rod, LB1 seats, kK 3 | 19.21 | 26.98 | 90.2 | 0.717 | 0.853 | 0.035 | 29.56 | 7/28 | 0.02 mm |
| tail, stage-2 best (crown) | 28.66 | 37.00 | 86.5 | 0.656 | 0.874 | 0.059 | 39.79 | 5/28 | 0.56 mm |
| tail, LHS best (beside) | 30.72 | 39.99 | 85.5 | 0.653 | 0.852 | 0.064 | 42.22 | 5/28 | 0.54 mm |
| H1 (verified, 3 active), same protocol | | 27.20 | 90.1 | | | | | | |

The rod best's lost poses, frozen, are fold 84, slide 8, parts 1 and contact 4. The fold is still the main loss: K's
stop B sits at a1max 58, and the folded side has no lobe.

## Verdict

**Screened. The FALLBACK embodiment is the first 3-active design measured below H1 frozen exact**: 23.37 against
H1's 27.20 on the same protocol. It is unverified, and its complexity is 42.5 against H1's 21.5. **The Geneva-tail
embodiment is not viable.**

- **The idea holds.** K slaved to q2, sensor-free, with an exact law, no lift-off and a pressure angle <= 45 deg, buys
  reach: 0.73 frozen at in-band 0.85.
- **Where the metal goes decides it.** A follower rigid with link 2 must be priced by its swept surface of revolution
  about u2, not by its pose at engagement. The tail costs 10-42 points. A lobe inside hub 2's own stack, driving a
  pushrod that rides link 1b, costs ~4.7.
- **Lesson that predicts beyond this morphology:** put every coupling element inside an existing O20 stack or on a link
  that does not turn relative to its neighbour's sweep. Never put it on a member that sweeps J2's range.
- **Before any claim (for the verifier):**
  - the independent harness on the rod best;
  - the continuity flood fill;
  - held-out clips;
  - the rod's slide and horn arc;
  - spring against gravity, and the reflected J2 torque kK tau_K.
- **Next levers:**
  - A folded-side lobe. The rod drive can take a second lobe for free on the same rim, which the tail could not. It
    attacks the 84 fold losses directly. The judge measured +0.6 fast for two lobes on the law.
  - Lower rod-end heads, for example a horn under the cap's spring at the crown level: the rod-end samples are 0 % in
    band.
  - Hub 3, which is 0.59 in band, as in every pin-knee chain.

## Verification (independent skeptic, 2026-10-16)

The verdict is **VERIFIED, not refuted**. The corrected v_gap is **23.57** on Bench(110,360), exact path, frozen shape
(score 91.4). The champion measures 64.93 on the same bench and protocol
(docs/concepts/verify/minarc-skeptic/champbig_frozen_m5.json, the same frozen-wear protocol with the kit checks;
75.94 under the risley checks).

- **Harness:** docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py. It loads the claim's model unchanged, as its own
  module copy.
- **Outputs:** `docs/concepts/verify/geneva-tail-knuckle-pinknee-3r_{claim,corr}_{bench,held}_frozen.json`. They were
  run on the farm (4 jobs, about $0.03).

### Reproduction

The rod best reproduces to the digit: 16.53 fast near-touch and 23.37 frozen exact.

### Corrections

**1. The horn was inside the spring cap (hard geometry).**

- The claim put the rod-end head on K's horn at the cap's mid-height, r_horn 2.49 mm off K's axis.
- That +6 mm cap is the clock spring's housing, so an O10 head there would sit in the spring's coils and arbor.
- The rod was never checked against hub K. It ran **5.9 mm into the cap**, and the head ran 3 mm into it.
- Corrected:
  - The horn moves onto a 1.5 mm plate on the cap top.
  - The rod meets both rod-end heads at their mid-height.
  - The rocker post grows from 9 to **19 mm**, the minimum at which the straight rod clears the cap by 1 mm. The cap is a
    cylinder about uK, so this clearance does not depend on the pose.
  - ROD vs hub K is now checked at the 1 mm rule.
- Cost: +0.20 fast (16.73) and +0.20 frozen (23.57). The rod and its heads were already out of band (now 29-30 mm over
  the skin), so they lose very little.

**2. Continuity flood fill (the CLAUDE.md rule; flood() from minarc-stop-knuckle-4r-mechanism.py, unchanged):**

| grid | poses dropped | gap |
|---|---|---|
| full 15-deg envelope grid (1432 poses) | 0 (all 406 forced envelope nodes connect to state A) | 23.57 |
| knn | 9 | 26.10 |
| literal bench grid | 82 (16 of them have no taken neighbour in the 360-pose subsample) | 46.65 |

On the full grid, every forced pose connects to state A, so the static number stands. K is a monotone function of q2,
so it has no branch to jump.

**3. Bench artefacts.** The claim is already on the exact path. The closure residual is <= 0.015 deg on the taken poses.
The drive engages on 123 stretched poses (K up to 44.0 deg taken; the law runs to 53.4 deg and ends on stop B), so it
is not an idle-drive row. Overhead reach is 8 of 28, the same as the claim.

### Corrected numbers (frozen exact Bench(110,360))

| | gap | reach | follow | in-band14 | in-band10 | contact | near-touch | min metal | overhead |
|---|---|---|---|---|---|---|---|---|---|
| claim as modelled | 23.37 | 0.731 | 1.0 | 0.846 | 0.532 | 0.011 | 25.01 | 0.45 | 8/28 |
| **corrected** | **23.57** | 0.731 | 1.0 | 0.844 | 0.531 | 0.011 | 25.21 | 0.45 | 8/28 |
| corrected, held out | 28.12 | 0.691 | 1.0 | 0.843 | 0.529 | 0.015 | 30.31 | 0.21 | 0.27 |

The held-out row uses clips and workspace poses disjoint from both benches.

The lost poses on the bench are fold 84, slide 8, parts 1 and contact 4. **The fold is still the limiter.**

### Against the same protocol

| design | active DOF | frozen | held out |
|---|---|---|---|
| this design | 3 | 23.57 | 28.12 |
| H1 | 3 | 27.20 | 31.39 |
| minarc pick1 | 4 (K sensed) | 18.40 | 21.31-22.69 |
| minarc BDp | 4 (K sensed) | 19.54 | 24.18 |

This is the best verified **3-active** number, but it costs complexity 42.5 against H1's 21.5.

### Rules

- 3 active DOF: K is slaved by the lobe and is never read.
- No passive coordinate is left undetermined: the cam is spring-closed, and the kinematic lift-off gate holds.
- 0 passive translations.
- No gears, pulleys or cables: it uses a cam, a rocker and a pushrod.

### Open (not scored)

- Rod-end and lobe play maps to K error of about 1.2 deg per 0.05 mm at r_horn 2.49 mm.
- At full stroke the lobe reaches about 10.9 mm radius, 0.9 mm past the O20 skirt. This is not modelled.
- The rod's horn arc (<= 1.9 mm) is not modelled.
- The rod is sampled as a line (16 points against the ~25 that 1 point per 4 mm2 would give), which is negligible here.
- Not checked: the spring against the arm's gravity torque, and the reflected J2 torque (3.18 tau_K).

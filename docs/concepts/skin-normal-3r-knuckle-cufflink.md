# skin-normal-3r-knuckle-cufflink - all-skin-normal 3R closed by three pins (J2 knuckle + pinned cuff link)

## Deeper version (answered before modelling, 2026-10-16 01:55 UTC; refined 02:20 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** Solve both passive sub-loops in closed
   form instead of by grid + secant, so branch, authority and toggle are explicit: the knuckle's radial closure is a
   single sinusoid in qk (lk rho cos(Phi - qk) = c0 - s_n + lk rho cos Phi, two roots, keep one sign of sin = one
   assembly mode, authority lk rho |sin| >= 5 mm/rad keeps it away from toggle), and the cuff link is a two-circle
   intersection (E-arm circle about J3's line, link circle about the arm pin) on a fixed elbow sign with the elbow
   angle kept 25 deg off straight / folded. Choose c0 and the knuckle mid AUTOMATICALLY from the fit set (maximise
   poses with a valid root inside +-35 deg), and centre the cuff on the mid in-plane drift, so the sweep searches
   seats, not bookkeeping. Keep the family a strict superset of the verified controls: b1 = b2 = 0 makes the knuckle
   idle (constant radial) and the design collapses to the zero-passive spherical 3R at those seats (41.73 exact) plus
   the pinned cuff instead of the 2 guides (45.31 / 42.59). Make the cuff parts one flat rotor plate (hub 3 + E arm)
   and flat pinned plates: no skin-shaped plates on the new parts. **What the knuckle really buys** (02:20): with
   b1, b2 > 0 the axis DIRECTIONS (which alone set the J2 fold, i.e. reach) are decoupled from the hub SEATS (which set
   in-band) - on the b = 0 subfamily a hub must sit where its axis pierces the skin. The rail-elbow control showed
   re-tuned axis directions alone are worth ~17 gap points; the knuckle is the price of that decoupling, so it must be
   paid in measured points (its crank and boss stack) and compared with the knuckle-free controls.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (grid, then the
   exact libigl path for the frozen check), the rest-pose skin and its face normals for the seats (libigl exact), the
   fit clips at their full 10 fps for continuity of all 6 joint values (q1, q2 - qk, q3 + psi, qk, qa, qb) and for
   the design steps (c0, mid drift), pipeline/conformal/band_poses_wsf.b64 for the rotations. Not the snh sweep
   record (its in-band premise is the risk under test).
3. **Specific methods and tools.** Paden-Kahan spherical IK of the axis directions + exact screw drift of the line
   offsets (the verified seed: S.Design.ik), closed-form knuckle and two-circle cuff closure, Grubler-Kutzbach mobility
   (7 bodies, 6 x 1-DOF joints + GH: M = 3, no redundancy), sphere tracing on the signed-distance grid for every
   underside (S.Model.needed), exact cylinder signed distances + mid-surface kd-trees for part-part clearance,
   tools/cloud_run.py sweep + tools/concept_cma.py on the cloud CPU farm.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses as the baseline 68.93 and
   the controls), the in-model controls (b1 = b2 = 0 at the leader seats), the frozen-shape wear on Bench(110,360)
   exact (lesson c), the adversarial verifier, and the red-team list below (the pose that jams, the point that
   pinches, the optimistic number).

(Model, sweep, red team and verdict below, filled as measured.)

## Spec corrections (said, then built)

* **Where the crank points (a bug found and fixed, 02:18 UTC).** The first model aimed the crank (alk = 0) along
  c3 - c2, the difference of the two LINE FEET (a few mm, an arbitrary direction), not along link 2. The crank then
  stood off the link's path, its boss swept a lk-radius circle over the rising deltoid and had to clear the highest
  skin it passed (the proximity-atlas rule): flat crank in band 0.02 at 25 mm, link 2b on top of it at 0.62; gap 50.28
  (flat) / 46.01 (strap) at the leader seats with the knuckle idle, and the first farm sweep (288 configs, stage
  `coarse-farm` in the sweep file) found 36.33 at best. Fixed: alk = 0 is the direction from the knuckle hub toward
  the next hub in the q = 0 layout (nominal hub levels 50 / 61 / 73 mm), so the crank is the root of link 2. The same
  idle control then scores 30.57 (crank strap lk 20: crank in band 0.92, link 2b 0.81, in-band14 0.872); everything
  after k 291 in the sweep file is the corrected model.
* **Knuckle site.** The spec allows the knuckle at J1 or J2 (`kat`). At J1 (hub 1's rotor on the scapula dome) the boss
  circle is skin-fixed (27.60 with the knuckle idle, crank in band 1.00) - but a J1 knuckle translates link 1b AND hub
  2 by Delta, so once b1 > 0 makes it swing (qk -36..+30 deg) hub 2 rides 32 mm over the skin (in band 0.01; gap
  51.96 at b1 0.6). The J2 knuckle moves only link 2b; hub 3 and the cuff keep their radial seat by construction.
* **What the knuckle buys is reach, through b1 - not in-band through square hubs.** At the leader seats the hubs
  already sit in band (hub 1 1.00, hub 2 1.00, hub 3 0.77 at b = 0); squaring them to the skin is worth nothing there.
  Kinematic scan (Bench(60,160), design step + both closures + 10 fps continuity, no parts; LE 30, lc 25):

  | seats | b1 | b2 | ws fold-free + closable | clip | fold (of 220) | radial span |
  |---|---|---|---|---|---|---|
  | leader | 0 | 0 | 0.719 | 0.967 | 47 | 0 (knuckle idle) |
  | leader | 0 | 0.6 | 0.469 | 0.767 | 99 | 13.0 mm |
  | leader | 0.4 | 0 | 0.775 | 1.000 | 36 | 13.2 mm |
  | leader | 0.6 | 0 | 0.812 (lk 40) | 1.000 | 30 | 19.3 mm, qk -17..+15 deg |
  | snh | 0.6 | 0 | 0.794 (lk 40) | 1.000 | 33 | 18.2 mm |

  Tilting J1's axis toward the dome's skin normal (b1) opens the J2 fold window (the J1-J3 axis angle); tilting J2 (b2)
  closes it. The knuckle is the price of that decoupling: with b1 > 0 line 1 misses GH, the radial drift appears
  (13-19 mm span) and only the knuckle (or a radial slide, which does not exist at this height) closes it.

## Model (docs/concepts/models/skin-normal-3r-knuckle-cufflink.py)

Built on the verified leader's Design (seats, closed-form spherical IK, line offsets) and the seed's VModel (closure
< 0.5 deg / 0.5 mm, jam rule, fitted undersides, greedy pose dropping recorded as contact). Members: 0 scapula + hub 1,
1 link 1 + hub 2 stator, 4 crank (hub 2 rotor + knuckle boss), 2 link 2b (laps over the boss, +3.15), 3 hub 3 rotor
plate + E arm (one flat plate, riser at hub 3's rim when its level differs), 6 cuff link (flat, O12 bosses), 5 arm pad
(flat 16 x 16 on the cuff). Closed-form closures: knuckle lk rho cos(Phi - qk) = c0 - s_n + lk rho cos Phi (one
assembly mode, authority >= 5 mm/rad, |qk - mid| <= 35 deg), cuff two-circle on one elbow sign (25-155 deg). Every one
of the 6 joint values continuous at 10 fps on the fit clips (step <= 25 deg). Part-part: 1 mm non-adjacent, 0.15 mm
adjacent (crank / crank strap vs link 1 at J2, link 2b vs crank strap at the knuckle, link 2b vs E arm at J3). Pins:
IGLIDUR-PIN (O4 Ti pin, GSM sleeve, 2 GTM washers), modelled as 3 mm plates + 0.15 + 1 mm head (7.15 mm stack, more
than the catalogue's 4.5-5). 3 active, 3 passive rotations, 0 passive translations.

## Sweep (Bench(60,160) fast, every configuration in docs/concepts/sweeps/skin-normal-3r-knuckle-cufflink.json)

| stage | configs | best gap | notes |
|---|---|---|---|
| local-check (first model) | 3 | 93.62 | snh seats, flat crank aimed along the line-foot difference |
| coarse-farm (first model) | 288 | 36.33 | b1 = b2 = 0.2, crank strap lk 20; random configs never in the top 14 |
| local-search (corrected model) | 81 | **28.64** (k 351) | from the knuckle-idle control 30.57; b1 0.007, b2 0.015, qk swing 3 deg |
| local-search, b1 fixed 0.3 | 36 | 45.10 (k 403) | seats, cuff, crank free around a working knuckle (qk -8..+32 deg): the search buys in-band back by re-tuning the seats until the fold is back at 47 |
| coarse-v2-farm (corrected model) | 224 | 27.60 (k 437) | J1 knuckle, b1 = b2 = 0: the knuckle IDLE (qk 0); J2 idle control 30.57; no random config in the top 12 |
| cma-farm B0 (J2, from b1 0.15) | 425 | 25.72 | b1 0.147, b2 -0.171, lk 20.1, alk -40; gate 1.58 / 0.39 / 0.42 (2nd half NOT met) |
| cma-farm B1 (J1, from the idle 27.60) | 289 | **24.47** (k 1187) | b1 0.011, b2 -0.084, lk 21.4, alk -22; gate 0.00 / 0.00 / 0.14 (converged) |
| cma-farm B2 (J2, from b1 0.35) | 593 | 25.97 | b1 0.167, b2 0.090, lk 17.1, alk -34; gate 0.46 / 0.07 / 0.09 (converged) |
| cma-farm B3 (J2, snh seats, from b1 0.6) | 289 | 28.64 | b1 0.411, b2 0.192, lk 17.0; gate 2.39 / 2.39 / 0.88 (not converged) |

**The knuckle earns measured points at small b (CMA, 03:20 UTC).** Knuckle LOCKED controls (b1 = b2 = 0, every other
parameter as found): B1 26.91 vs 24.47 working (J1 knuckle swings -5.7..+2.8 deg; fold 53 -> 49) = +2.44 points; B2
32.93 vs 25.97 working (J2 knuckle swings -15.2..+11.0 deg; fold 59 -> 49) = +6.96 points. The lever is a small
axis-direction decoupling (|b| <= 0.17, line offsets 0.2-1.5 mm at J1/J2), not the square-to-skin hubs of the spec.
The large-b basin (b1 >= 0.3) stays 4-90 points worse.

The b1 lever, measured with every part (leader seats, b2 0, J2 knuckle, crank strap lk 20, coarse v2):

| b1 | gap | reach | in-band14 | fold | skin | parts | cuff |
|---|---|---|---|---|---|---|---|
| 0.0 | 30.57 | 0.669 | 0.872 | 47 | 8 | 0 | 0 |
| 0.2 | 45.76 | 0.631 | 0.787 | 42 | 13 | 1 | 1 |
| 0.4 | 87.47 | 0.613 | 0.606 | 36 | 21 | 14 | 4 |
| 0.6 | 115.13 | 0.619 | 0.416 | 30 | 16 | 20 | 13 |
| 0.8 | 114.32 | 0.575 | 0.404 | 28 | 16 | 15 | 19 |

The fold falls 47 -> 28 as predicted, but reach does NOT rise: the poses the fold gives back are lost to skin contact,
part clashes and the cuff dyad's range, because once line 1 misses GH the knuckle swings (qk spans 30-50 deg), link
2b and the crank boss sweep the deltoid, and the cuff's in-plane drift grows past what a 30 / 25 dyad spans. In-band
collapses with them (0.87 -> 0.40).

Best configuration k 351: leader seats with J2 nudged (az2 12.43, wd 80.91), b1 0.007, b2 0.0145, b3 0.228, crank strap
lk 20 along link 2, E arm 31.7 at phE 2.8, cuff link 25 at dB -86.2. reach 0.675, follow 1.000, in-band14 0.879,
in-band10 0.463, contact 0.040 -> gap 28.64 (score 89.59). Parts in band (share, median mm): hubs 1.00 / 0.98 / 0.85,
crank boss 0.98 (10.4), crank strap 0.70, link 1 0.91, link 2b 0.81, E arm 0.86, cuff link 0.73, pad 0.90. Knuckle
qk 17.8..21.1 deg (idle), authority p1 6.5 mm/rad; cuff drift 23 x 23 mm, elbow 63-128 deg, rotor turn psi +-22 deg.

Convergence gate (local-search stream, 81 tries): gain over the 2nd half 0.70 score points (< 1: pass), over the last
third 0.69 (> 0.5: NOT passed), top-5 spread 0.25 (< 3: pass). The b1 = 0.3 stream (stopped at 36 tries, 45.10): 1.79 / 1.79 / 4.88 - not converged, 16 points behind.

## Red team (own best, k 351)

* **The optimistic number.** 28.64 is a design whose knuckle does not move (qk swing 3 deg): it is the pin-knee leader
  (2 pins, 26.34 fast / 33.84 exact) plus a third pin and a crank strap, i.e. a slightly worse copy of an existing row.
  Every configuration where the knuckle does real work (b1 >= 0.3) is >= 20 gap points worse (49.98 best at b1 0.3 after
  the seats and cuff were re-tuned around it; 52-105 at the leader seats).
* **The point that pinches.** Lowest metal over taken poses (walls, crowns, pin heads included): 0.08 mm at #179
  (across the body, plane 105, elevation 30, axial -135), 0.26 mm at #100, 0.40 mm at #79, 0.68 mm at #112: 4 poses
  under 1 mm -> gap 33.43 if near-touch counts as contact.
* **The pose that jams / the overhead.** Elevation >= 140: 7 of 17 taken (reach 0.17, in-band14 0.94 where taken); the
  J2 fold takes 5 of the 10 misses. Across the body: reach 0.58, in-band14 0.48 (median 14.6 mm - the across-body
  poses lift the cuff side). Behind the back: reach 0.40.
* **The floppy pin.** The knuckle is set only by the cuff's radial constraint. At authority 6.5 mm/rad (p1) a 3 mm
  cuff-liner give lets the knuckle and link 2b swing 0.46 rad (26 deg) unpowered; at the idle optimum the knuckle is
  a pure liability (lock it = the pin knee).

## Frozen wear on Bench(110,360) exact (lesson c)

NOT BACK inside the time box (03:40 UTC). Running: the farm job kc-frozen-C (B1, B2, B0 bests; the farm queue held
its upload 5 + 5 min) and a local single-process run of B1 (`CB_EXACT=1 python3
docs/concepts/models/skin-normal-3r-knuckle-cufflink.py frozen '<B1 params>' <out.json>`, 20+ min under a load of
7-44 on 4 cores). Its fit step reproduced 24.47 exactly. Until a frozen exact number exists the 24.47 is a FAST-bench
number only: for scale, the pin knee went 26.34 fast -> 33.84 exact frozen and the 2-slide leader 32.61 -> 42.59; the
J2-fold boundary is tuned to the 160 workspace poses in every one of these CMA runs (lesson c), so expect +7..+10.

## Verdict (03:25 UTC, after the CMA)

**Screened; a fast-bench leader candidate, claim pending the frozen exact wear.** Best k 1187 (J1-site knuckle, CMA B1,
converged): 24.47 on Bench(60,160) fast = score 91.10 (reach 0.694, follow 0.967, in-band14 0.868, in-band10 0.510,
contact 0.006), 1.87 points under the pin-knee leader's 26.34 at the same rules; J2-site best 25.97 (B2, converged).
Red team k 1187 (fast): near-touch min 0.04 mm at #63 (plane -90, elev 45, axial 120 - behind the back), 3 poses
< 1 mm -> gap 28.10 if near-touch counts as contact; elevation >= 140 reach 0.17 (7 of 17; 6 misses are the J2 fold),
in-band14 0.91 where taken; across the body reach 0.58, in-band14 0.48 (median 14.3 mm); behind the back reach 0.60.
Knuckle authority p1 7.6 mm/rad (= 23 deg of free swing per 3 mm of liner give: a stiffness the unpowered MVP1 must
show on the bench). Cuff dyad: elbow 100-149 deg (31 deg off straight at its limit), rotor turn psi -15..+11 deg.

Measured, not assumed:
1. The spec's premise (square-to-skin hubs buy in-band) is false at the leader seats: the hubs are already in band at
   b = 0 (1.00 / 1.00 / 0.77-0.87); large b moves hub 2 out of band and loses 15-90 points.
2. The real lever is a SMALL axis-direction decoupling (|b| <= 0.17) that the knuckle closes: +2.4 (J1 site) / +7.0
   (J2 site) gap points over the knuckle-locked control at the same seats, through the J2 fold (53 -> 49, 59 -> 49).
3. The J1 knuckle's boss rides a skin-fixed circle on the dome (crank in band 1.00, 7.1 mm) - the cheapest place for
   a closure pin on the chain; a J2-rotor boss sweeps the deltoid.
4. New knowledge beyond this morphology: (a) b1 (J1 tilted toward the dome normal) is a genuine fold lever (47 -> 28
   of 220 at b1 0.8, kinematics) but only small b survives the parts; (b) a closure-set pin is only as stiff as its
   authority times the cuff liner - size the authority floor against the liner, not against toggle alone; (c) the
   first model's crank pointed along the line-foot difference: a 15-point modelling error, caught by the knuckle-idle
   control (always run the locked control).

What next (loop): the frozen exact wear of B1 / B2 / B0 (farm job kc-frozen-C, queued 03:20 UTC) decides the claim
against the pin knee's 33.84 exact; then the adversarial verifier (docs/concepts/verify/offset-skin-normal-3r.py
pattern), a CMA polish of B0 (not converged) and a wider J1-site CMA (the converged B1 basin was reached from the idle
seed only - seed it from B0 / B2 seats too). The red-team pose #63 (behind the back, 0.04 mm) is the first fix.


## Verification (adversarial verifier, 2026-10-16 04:10 UTC)

Harness: `docs/concepts/verify/skin-normal-3r-knuckle-cufflink.py`. Results:
`docs/concepts/verify/skin-normal-3r-knuckle-cufflink.results.json`. Protocol: the k1187 shape is fit on Bench(60,160)
fast and reproduces 24.47. It is then worn frozen (no refit, the design-step values c0, knuckle branch and cuff mid
kept) on Bench(110,360), exact path (CB_EXACT=1), on the farm (1188 s, about $0.10).

| | gap | score | reach | follow | ib14 | ib10 | contact |
|---|---|---|---|---|---|---|---|
| claim, Bench(60,160) fast | 24.47 | 91.10 | 0.694 | 0.967 | 0.868 | 0.510 | 0.006 |
| model's checks, frozen Bench(110,360) exact | 31.89 | 88.40 | 0.617 | 0.964 | 0.871 | 0.517 | 0.006 |
| **verifier's corrected checks, same run** | **31.89** | **88.40** | 0.617 | 0.964 | 0.871 | 0.517 | 0.006 |
| metal < 1 mm counted as contact | 33.05 | 87.98 | | | | | |
| champion 3R, same bench (kit checks + 1 mm radial, risley-turret verifier) | 75.94 | 72.39 | | | | | |
| champion 3R through the OSN VModel code | 66.97 | 75.65 | | | | | |

The verifier's checks, all re-measured:
1. **DOF.** Grubler M = 6(7 - 1 - 7) + 6 + 3 = 3. There are 3 active O20 hubs, 3 passive pins (the knuckle parallel
   to J1, and pins a and b parallel to J3) and 0 passive translations. Every passive coordinate is set by the rigid
   closure (one assembly mode per closure). No gears, pulleys or cables.
2. **Independent 3D closure.** Each pose taken is checked from the member transforms, not from the closed form the
   model solves with. The checks are: the knuckle pin as carried by the crank vs by link 1, J2's line, J3's line,
   pin a as carried by the rotor vs by the cuff link (the along-axis offset stays constant), pin b, and the rotor axis
   vs the arm axis. Worst case: 0.000 mm and 0.016 deg, so 0 poses fail.
3. **Parts the model only skin-checked.** The knuckle post, the pin a post, the pin b post (pad up to the cuff link
   plus the head) and the E-arm riser are now solids in the part-part check. Each is checked against every
   non-adjacent part at >= 1 mm (hubs as exact cylinders, plates and straps with their half thickness, the other
   posts), and the pin a post against link 2 at 0.15 mm. Minimum: 6.46 mm (the pin a post vs the pad, overhead), so
   0 poses fail.
4. **Adjacent pairs the model never checked.** E arm vs cuff link (away from pin a) and cuff link vs arm pad (away from
   pin b), each at >= 0.15 mm. Minimum: 0.18 mm (cuff link vs pad, which sit exactly one running gap apart), so
   0 poses fail.
5. **Spans over the poses taken.** Knuckle -5.6..+3.4 deg, rotor turn psi -10.7..+11.1 deg, cuff elbow
   100.4..138.4 deg (more than 25 deg from straight and from folded).
6. **Arm pad.** The pad sits 59 mm from GH in the cuff plane, at 79 mm along J3's axis. That puts it on the lateral
   upper arm about 60 mm below GH, i.e. on the deltoid, not mid-humerus. This is stated, not scored.
7. **Bench artefact.** None was found. The exact path agrees with the model's own frozen exact run (31.89, the
   agent's local run, identical to the digit).

Result: the corrected checks remove no pose, so the claim's FROZEN number stands. The FAST number does not: frozen
exact gives 31.89 (score 88.40, up 7.4 from the fast number), which is below the score-90 target (gap <= 27.5). It is
behind the pin knee's verified 30.35, and level with raglan-knee-3r's unverified frozen 31.52. It is far ahead of the
champion (75.94 / 66.97). NOT REFUTED; status verified.

Where the points go on the big bench (measured):
- The J2 fold takes 136 of 470 poses.
- Overhead (elevation >= 140): reach 0.25, in-band14 0.91 where taken.
- Across the body: reach 0.29, in-band14 0.57.
- Behind the back: reach 0.68.
- Parts that drop out of band: hub 3 (0.74), link 1 (0.63), cuff link (0.81).
- Near-touch: 0.19 mm at #317 (plane 60, elevation 150), 2 poses under 1 mm.

### Red team: what the frozen number does not show

- **Liner swing (R17).** The knuckle is set only through the cuff liner. Its authority is as low as 6.8 mm/rad over
  the big bench (p1 8.0). The test swings the knuckle by +-g / authority per pose (the liner giving g mm radially),
  moves link 1, hubs 2-3, the rotor and the crank, and leaves the arm side in place (Bench(60,160) fast, base 24.47):

  | liner give | knuckle swing | chain shift | gap (+ / -) | contact poses |
  |---|---|---|---|---|
  | 1 mm | 8 deg | 3.0 mm | 23.66 / 27.25 | 1 / 1 |
  | 2 mm | 16 deg | 6.0 mm | 27.28 / 34.00 | 5 / 3 |
  | 3 mm | 24 deg | 8.9 mm | 47.83 / 37.46 | 19 / 3 |

  The knuckle amplifies the liner's give about 3x at the chain. The "<= 3 mm radial to the liner" allowance therefore
  costs 13-23 gap points here, where a design with no closure-set rotation pays none. Fix: an authority floor of at
  least 15 mm/rad (a longer crank, or the J2 site), a preload spring on the knuckle, or a cuff zone with < 1 mm give.
- **Readout (R5 active-DOF rule).** The knuckle is parallel to J1, and the cuff pins turn the rotor about J3, so the
  arm's angles are hub reading + passive angle. From the 3 hub encoders alone (rigid closure), 1 mm of cuff
  disturbance (liner give, or GH translation against the scapula) moves the implied J1 angle by 2.9 deg median and
  8.0 deg max, and the implied arm twist by 1.4 deg. A spherical 3R with cuff SLIDES has none of this, because its
  orientation readout does not depend on the slides. So in practice the 3 pins need encoders to track the arm. The
  model already lists them as sensed_passive 3. Under the user's counting rule (REQUIREMENTS.md: joints that must be
  powered or position-measured for the device to work count as active), that is an exposure to 6 active DOF. The
  user should rule on it. It is not scored here, and the same question applies to the pin knee's 2 cuff pins.
- **MVP2 torque path.** J1's torque reaches link 1 through a free knuckle, so it is reacted by a radial (skin-normal)
  force at the cuff. That means lost motion equal to the liner swing above.

Next: wear the B2 (J2-site) and B0 shapes frozen (the farm job kc-frozen-C). Search with an authority floor of 15 mm/rad
and liner-swing robustness inside the objective (score the worst of the +-2 mm swings). Fix #317.

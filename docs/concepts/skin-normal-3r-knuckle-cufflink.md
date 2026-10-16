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
| CMA B0-B3 (farm) | queued | - | farm queue 57 deep at 02:39 UTC; filled below if back inside the time box |

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

FROZEN_PLACEHOLDER

## Verdict (02:59 UTC, time box)

**Screened, dominated - the knuckle never earns its place.** Measured on the bench with every part at real size:

1. The premise under test (skin-normal hubs live in band, so a closure joint that permits them buys in-band) is false at
   the leader's seats: the hubs are already in band there (1.00 / 1.00 / 0.77-0.87 at b = 0); squaring them buys
   nothing and moves hub 2 out of band (0.14-0.30 at b1 0.3-0.5).
2. What the knuckle really permits is axis directions decoupled from the seats (b1), and that lever is real for the
   kinematics - the J2 fold falls 47 -> 28 of 220 poses at b1 0.8 (fold-free ws 0.72 -> 0.81 at b1 0.6, kinematics
   only) - but with the parts on, the knuckle must swing 30-50 deg, its boss and link 2b sweep the deltoid and the cuff
   dyad runs out of range, so reach stays at 0.58-0.62 and in-band falls to 0.40. Best working-knuckle configuration
   45.10 (b1 0.3, re-tuned seats, not converged) vs 28.64 idle.
3. The optimum is the knuckle idle (qk swing 0-3 deg): 27.60 (J1 site) / 28.64 (J2 site) on Bench(60,160) fast, i.e. the
   pin-knee leader (26.34 fast, 33.84 exact, 2 pins) plus a third pin and a crank strap. By the tie rule (fewer passive
   joints) and on the number, skin-normal-3r-pin-knee dominates it.
4. New knowledge that predicts beyond this morphology: (a) b1 (J1 tilted toward the dome normal) is a genuine fold lever,
   ~19 poses of 220, for any design that can close a radial drift of 13-21 mm without height - a radial closure through
   a pin on the J2 rotor cannot, because every rotor part sweeps a circle of the deltoid; a closure joint must sit where
   its body's skin is fixed (the cuff or the scapula), and a J1-site knuckle moves hub 2 instead. (b) A closure-set pin
   is only as stiff as its authority times the cuff liner: 6.5 mm/rad at p1 means 26 deg of free swing per 3 mm of liner
   give - any closure-set passive joint needs its authority floor sized against the liner, not against toggle alone.

What next (loop): the CMA streams B0-B3 (farm, queued) refine the idle and b1 basins; if a working-knuckle stream does not
reach the idle optimum the morphology is dead by the gate. The b1 fold lever belongs to a design that takes the radial
drift at the CUFF (where it is skin-fixed): e.g. the pin-knee leader with a cuff-side closure for the radial component
(a third, skin-normal pin dyad stands up; a flexure or the <= 3 mm liner allowance does not cover 13 mm) - worth a
kinematic check of how small b1 still buys most of the fold (b1 0.2: 47 -> 42).

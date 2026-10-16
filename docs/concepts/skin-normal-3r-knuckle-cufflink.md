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

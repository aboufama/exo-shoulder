# lead-relay-backbridge-4r - back-of-shoulder J0 with a link-0 bridge over the knuckle (4 joints)

Round 103 (J3, track jump), judge pick 2. Lens 1 (relay under the lead's frozen chain), the "larger a0" clause of the
PASS rule: J0 sits outside hub 2's orbit about J1, and link 0 bridges over the knuckle to J1's housing.
**4 counted joints (J0 + J1 + J2 + J3); the user prefers 3.** 0 passive translations.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Separate what the relay can buy from
   what its metal costs, before wearing anything. Hub 0 is scapula-fixed and axisymmetric about J0's axis, so its
   distance to the skin does not depend on q0 or on the chain. Its in-band share on the clip frames is therefore a
   property of the SEAT alone, and the clip frames never relay (follow is 1.0 at q0 = 0). That gives a closed-form
   lower bound on the gap of EVERY seat in the sweep space: the in-band with hub 0 (and link 0 at its best case)
   plus the kinematic upper bound on new workspace takes (any q0 in the legal travel, zero-size metal). A seat whose
   bound is over the bar is dead without a sweep, and the bound covers the whole sweep_params grid
   (a0 x azu x window x route), not one wear. Second, the designer asks whether link 0 must go OVER the chain at all.
   A planform turn that enters J1's housing through the azimuth sector the chain never sweeps would let link 0 ride
   low. So measure the chain's azimuthal occupancy about J1 before choosing the route.
2. **The rawest material.** The posed skin itself: exact signed distance on Bench(110,360) through libigl, with no
   fast cache. The lead's frozen metal as the kit fits it on Bench(60,160): every hub disc, strap and crank sample.
   The fit-bench skin decides r0 and link 0's height profile. The per-pose taken / contact list of the lead
   (docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json). Not the judge's arithmetic (884 / 1121):
   the in-band is re-measured from the samples.
3. **Methods and tools.**
   - tools/concept_bench.py, exact path, Bench(110,360) for the claim and Bench(60,160) fast for the fit and for
     picking the window.
   - The lead's model docs/concepts/models/conecut-knee-knuckle-3r.py, loaded unchanged and frozen.
   - The relay wrapper: HG patched to Rc^T Q per relayed pose, T(m, i) premultiplied by Rc, |dK| <= dK_lim, and a
     sub-chain margin >= 5 deg.
   - Hub 0 as an O20 cylinder (r 10, stack 12.25) with the kit's disc sampling (81 points, 1 / 4 mm2) plus wall and
     crown contact samples.
   - Link 0 as a 12 x 3 strap sampled on a 2 mm grid. Its height comes station by station from the fit-bench skin
     and the chain's swept samples, under the 60-deg climb-ramp limit.
   - A per-pose part check: hub 0 / link 0 against every chain sample, 1 mm non-adjacent clearance, with J1's
     footprint treated as adjacent.
4. **What, other than me, shows the number is right.**
   - The bench report itself: in-band, reach, follow and contact from bench samples, not from arithmetic.
   - The per-part in-band table (hub 0 and link 0 shown separately), and the gap with and without them.
   - The judge's prediction (~25-29 frozen), stated before the wear.
   - A red-team list: the behind-back and extension poses where hub 0 is closest, the relayed poses that hit the
     skin (kept as contacts), and the near-touch reading.
   - The round's adversarial verifier re-runs this file's `wear` mode.

## The model (docs/concepts/models/lead-relay-backbridge-4r.py)

- **The lead, unchanged and frozen.** The lead is fitted on Bench(60,160) fast (gap 12.50, as on file) and worn on
  Bench(110,360) exact.
- **The relay (policy ii).** A workspace pose the lead cannot close at q0 = 0 relays to the least |q0| inside the stop
  window at which the chain closes. Closing means: knee, J3 stop, |dK| <= dK_lim, and a J0-J1-J3 sub-chain margin
  >= 5 deg.
  - The window [lo, hi] is picked on Bench(60,160) with the metal on (never on the claim bench), inside the J1
    seat-rule travel.
  - A relayed pose whose metal enters the skin is a CONTACT.
- **Hub 0.** O20 (r 10, stack 12.25), 81 underside samples (the kit's disc, 1 per 4 mm2), with wall and crown contact
  samples. Its underside r0 is the lowest radius at which the disc clears the fit-bench skin by 2 mm on every fit pose.
  The model reports how many fit poses the chain enters hub 0 there; those poses are lost as 'parts' on the bench.
- **Link 0.** A 12 x 3 bar sampled on a 2 mm grid (7 across). At each station along the route, its underside is set
  by whichever is higher:
  - the fit-bench skin + 2 mm under all 7 lateral samples;
  - the highest chain sample within half width + 2 mm, + 1 mm, + strap half thickness, over every taken fit pose
    (the relayed ones included).

  The profile then gets the 60-deg ramp envelope, and the ends land on hub 0's and hub 1's crowns.
- **The per-pose part check.** Hub 0 and link 0 are checked against every chain sample at 1 mm. Member-1 parts
  inside hub 1's footprint + 4 mm are treated as adjacent at J1.

## Results (frozen exact Bench(110,360); lead 18.28 on the same checks)

| seat (a0 / azu) | window (fit bench) | gap with metal | score | reach (ws) | ib14 | contacts | parts lost | ghost (zero-size J0, same window) |
|---|---|---|---|---|---|---|---|---|
| **60 / 330** (clash-free, the spec's decisive wear) | [-7, 0] | **32.13** | 88.32 | 0.725 (261) | 0.772 | 7 | 4 (link 0 x L2) | 18.22 (265, 7 contacts) |
| 55 / 345 (hub 0 most in band at a short link) | [-22, 8] | 34.01 | 87.63 | 0.694 (250) | 0.795 | 11 | 24 (hub 0 x chain on 17 fit poses) | 17.16 (274, 13 contacts) |
| 70 / 330 (the "larger a0") | [-7, 0] | 35.42 | 87.12 | 0.728 (262) | 0.737 | 7 | 4 (link 0 x L2) | 17.94 (266, 7 contacts) |
| 60 / 0 (the proposer's best far ghost) | [-22, 1] | 38.64 | 85.95 | 0.722 (260) | 0.720 | 11 | 17 (hub 0 x chain on 7 fit poses) | 16.35 (276, 12 contacts) |

Per part, from the bench's own in-band table (clip frames, q0 = 0 on every clip frame since follow is 1.0):

| seat | hub 0 r0 (mm) | hub 0 in band / median | link 0 length / samples | link 0 in band / median | link 0 min skin (all taken) | gap with hub 0 + link 0 left out of in-band |
|---|---|---|---|---|---|---|
| 60 / 330 | 76.0 | 0.811 / 10.9 mm | 48.0 mm / 168 | **0.000** / 25.8 mm | 14.71 mm | 19.35 |
| 55 / 345 | 67.5 | 0.884 / 11.4 mm | 38.9 mm / 140 | **0.000** / 27.7 mm | 19.66 mm | 23.52 |
| 70 / 330 | 84.5 | 0.733 / 11.4 mm | 63.6 mm / 224 | **0.017** / 24.3 mm | 11.27 mm | 19.07 |
| 60 / 0 | 75.5 | 0.023 / 20.9 mm | 47.8 mm / 168 | **0.000** / 30.3 mm | 18.67 mm | 20.67 |

The chain alone keeps its 0.9011 in band at every seat. The in-band collapse is link 0's, not hub 0's.

## Link 0 cannot ride in the band: every route is set by the chain (fit bench, a0 60 / azu 330)

| route | length | samples | stations set by chain / skin | height over the rest skin (mm) | ib14 on the fit clips |
|---|---|---|---|---|---|
| great circle c -> u1 | 48.0 | 168 | 24 / 0 | 19.5-29.7 | 0.000 (median 25.8) |
| planform turn -20 deg | 60.1 | 217 | 31 / 0 | 21.0-31.7 | 0.000 (median 28.6) |
| planform turn -40 deg | 88.4 | 315 | 45 / 0 | 24.2-31.8 | 0.000 (median 31.7) |
| planform turn +20 deg | 60.1 | 217 | 31 / 0 | 15.4-29.8 | 0.129 (median 21.7) |
| planform turn +40 deg | 88.4 | 315 | 7 / 38 | 18.0-31.8 | 0.129 (median 31.5) |

Why every route rides high:

- Hub 1 is ringed by the chain's own sweep. Hub K and link 1a orbit J1 at ~15 deg; hub 2, link 1b, the crank and
  link 2 sweep the 37-57 deg annulus. Their crowns sit at hub level + 12.25 stack, 20-24 mm over the skin.
- Hub 0 is outside hub 2's orbit, so link 0 must cross that sweep to reach J1's housing.
- At every approach azimuth tried (0, +-20, +-40 deg off the great circle), the chain occupies the crossing on some
  taken pose. Link 0's underside therefore rides at crown + 1 mm + 1.5 mm, which is 22-30 mm over the skin.
- 0 % of a 140-315-sample bar is in band. That alone costs +9.7 points at 140 samples and +11.5 at 168:
  ib14 <= (884 + 81) / (1062 + n). The relay's best ghost gain on this host is 1.9 points (16.35 vs 18.28).
- So no seat outside hub 2's orbit can come under the lead, or under the 17.5 bar, while link 0 reaches hub 1 over
  the chain:
  - 18.28 - 1.9 + 9.7 = 26.1 even at a 100 % in-band hub 0;
  - the measured best is 32.13.

**Correction to the judge's arithmetic.** The judge put hub 0 at 0 % in band, 16-20 mm over the resting skin. On the
clip frames it is 73-88 % in band (median 10.9-11.4 mm) at azu 330 / 345. What collapses the in-band is the bridge:
168 samples at 0 %. The judge's ~25-29 sat under the measured 32.13, because the bar is sampled at the kit's honest
density (1 per 4 mm2, 7 across a 12 mm bar).

## Red team on the best cell (60 / 330)

- **Optimistic number?** The window was picked on Bench(60,160), and the claim bench's relays went 3 taken, 3 contact.
  The ghost at the same window is 18.22, so the relay buys nothing.
  - The continuity flood was not run. It could only remove relay takes, so the number can only get worse.
  - With link 0 sampled as sparsely as the lead's L1b (36 samples per 8 x 3 strap), ib14 is
    (884 + 66) / (1062 + 36) = 0.865, which gives about 23 (ghost 18.22 + 3.5 + 1.1 for the 4 jams). That is still over 17.5.
- **The pose that jams.** Link 0 against link 2 at poses 178 / 204 / 220 / 229, which the lead takes. The fit-bench
  profile misses link 2's swept top on the claim bench.
  - At 55 / 345 and 60 / 0, hub 0 sits inside the chain's sweep at its skin-set seat: 17 / 7 fit poses clash, and
    24 / 17 claim poses are lost.
  - The chain-clear seat is r0 83 / 96 mm, 25-40 mm proud.
- **The point that pinches.** Hub 0 comes within 2.82 mm of the skin, never in the behind-back poses the spec feared.
  The closest are overhead at elev 150-165, axial -60 / -75: 291, 318, 345, 8-10. There the deltoid / supraspinatus
  bunches toward the scapular spine.
  - At 55 / 345, hub 0 comes to 1.84 mm.
  - Near-touch (metal < 1 mm counts as contact): 33.19.
- **Overhead.** 8 / 28 at every seat, the lead's own count. The relay takes no overhead pose: the J1 seat rule caps
  the travel at +16-23 deg, and the folded overhead poses need the opposite sign.

## Verdict

**DEAD (gate 0, KILL by the round's pre-registered rule: > 17.5 frozen exact at every seat worn).**

- Best: 32.13 (score 88.32) at a0 60 / azu 330, against the lead's 18.28. 4 joints, cx 50.75, 0 passive
  translations.
- The binding part is link 0: 0-1.7 % in band, 140-224 samples riding 24-30 mm over the skin, because it must bridge
  the chain's swept annulus to reach hub 1.
- This closes lens 1's "larger a0" clause with a number. A relay J0 outside hub 2's orbit pays ~10-12 in-band points
  for a link that cannot ride in the band, against a measured relay gain of <= 1.9.
- The only relay geometry without a bridge is J0 inside J1's footprint, which is lead-relay-wobble-4r. It dies by
  hub 1's lift (judge 103).

**New knowledge (predicts beyond this morphology).** Any part that must reach a hub from outside that hub's
neighbours' swept annulus rides at the neighbours' crown height + clearance: ~22-30 mm for O20 stacks. It is out of
the 2-14 band for its whole crossing, so the in-band price is set by its sample count (length x width at
1 per 4 mm2), not by the hub it carries.
- Remote relay hubs, base bridges and "over the knuckle" links are therefore priced before they are built:
  ~+0.2 points per mm of 12 mm bar at the lead's 1062-sample pool (11.5 points at 48 mm).
- Put new hubs INSIDE a footprint, or on the skin side of the annulus where the chain never passes. Never across it.

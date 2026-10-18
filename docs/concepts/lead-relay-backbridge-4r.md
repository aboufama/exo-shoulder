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

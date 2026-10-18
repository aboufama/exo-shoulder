# kfree-armarc-relay-4r - plain O20 3R at the lead's seats + one-sided arm-arc relay (counted 4th R), no knuckle, no drive

Round 104 (J4, track jump), lens A "guide-price-close", the survivor's simplicity column. Model:
`docs/concepts/models/kfree-armarc-relay-4r.py`. Sweep: `docs/concepts/sweeps/kfree-armarc-relay-4r.json`. Row:
`docs/concepts/rows/kfree-armarc-relay-4r.json`. Preview: `docs/concepts/viz/concepts/kfree-armarc-relay-4r.js`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Price the relay against its own
   control before anything else: the same frozen lead metal with K welded and no relay (PHI 0). Every point the relay buys
   is measured against that number, not against the lead. Then split the relay's cost into its two physical parts, each
   measured: (a) the ideal relay (rotation only, no track / shell / carriage metal, no lift) as a lower bound on the gap
   for this morphology at any hardware, and (b) the hardware (the track radius about the axis, the arm-side stack's
   lift onto the carriage, the arc length). If (a) is not under the kill line, no hardware choice can save it. A designer
   would also check where the arc lies (deltoid crest, axilla side, torso) before sweeping the axis, because the track
   radius is set by the highest skin over the arc.
2. **Rawest material.** The posed skin itself (the bench's signed-distance field per pose through `CB.Bench.dist`),
   the motion clips (Bench(60,160) fit clips, Bench(110,360) exact), the lead's fitted metal in its own model
   (conecut-knee-knuckle-3r: O20 stacks, pin knee, J3 dowel stop), the proposer's lost-pose list
   (docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json) and the per-pose dumps written here.
   The relay track radius comes from ray marches through the posed arm skin per fit-clip frame (p90 over frames), not from
   a digested ring radius.
3. **Methods and tools.** tools/concept_bench.py (the outside judge), the lead's own model loaded unchanged with K welded
   (law onset moved to the plain wall, smhi 5, plus a gate |dK| <= 0.1 deg), the relay wrapper of armarc-relay-knuckle-4r
   (least-phi relay solve on every lost pose of either wall, track + shell + carriage sampled metal, the arm-side lift onto
   the carriage, jams), the kit model (tools/concept_kit.py) only to reproduce the proposer's nok_metal counts, and the
   frozen-shape protocol (fit Bench(60,160) fast, worn Bench(110,360) exact).
4. **What, other than me, shows the number is right.** The bench (Bench(110,360) exact, frozen), the adversarial verifier
   with the 18.28 bar, the alignment auditor's ledger, and the red-team pose list below (the relayed poses that end in
   contact or jams, the largest relayed phi, the folded-side relays the spring cannot refuse).

## The morphology

At rest three O20 hubs sit at the verified lead's seats (J1 back of the shoulder / acromion top bvec(95.39, 67.90), J2
over the posterior deltoid, J3 on the lateral arm; a1 37.55, a2 57.22). Link 1 is one bent bar (hub K, bell crank, nose,
horn deleted). The cuff knee is the lead's. BOTTOM's pad rides a carriage on a circular track about an arm-fixed axis
through GH (tilt / azimuth swept), held on a zero dowel by a constant-force spring, end dowel at PHI. When the arm leaves
the plain dyad's window (th > a1 + a2 - 5 = 89.77 stretched, th < |a1 - a2| + 5 folded) the arm turns the carriage to the
least phi in [0, PHI] at which every gate of the welded chain passes. A spring relay cannot choose its wall: a pose whose
least-phi state ends in metal on metal is a jam, counted lost.

DOF: 4 counted joints (J1, J2, J3, relay), 0 passive translations, knee pins a / b passive (outside the count).

## Modelling notes (what changed from the spec, and why)

* **The kit model reproduces the proposer exactly but cannot score this design.** `repro` (kit CONTROL metal, profiles
  fitted without the relay, worn exact on Bench(110,360)) gives +30: 54 relayed / 10 collide / 1 contact / 44 clean;
  +45: 68 / 15 / 1 / 53; +60: 83 / 15 / 1 / 68 - identical to nok_metal_out.json. But the kit's q 1.0 metal parks hub 2
  at 171 mm from GH even with no relay (kit CONTROL fast gap 74.45, K welded 102.98, against the lead's own model 12.50),
  so its in-band is meaningless. The score is taken from the lead's own model instead (spec: "Base: conecut-knee-knuckle-3r
  with K welded at stop A").
* **K welded properly.** The lead's linear K law opens from th = a1 + a2 - smhi (smhi 16.84, i.e. 12 deg before the
  plain wall). Gating on |dK| = 0 with the lead's law loses every pose in [77.9, 89.8] that a welded dyad closes (first run:
  reach 0.344). The law onset is moved to the plain wall (smhi 5), so K sits on stop A wherever the welded dyad closes, and
  the gate |dK| <= 0.1 deg is the welded window.
* **Drive metal deleted** (crank, nose, horn removed from the rigid and contact lists); hub K and link 1a / 1b at stop A
  stay as metal (the spec's first pass, as the kit did). Shape frozen from the phi = 0 fit.
* **Window shift psi2** (docs/research/fold_ceiling/shift_a2.py's lever): J2's rest axis is turned about J1 by psi2, which
  keeps a1 and changes a2 (psi2 -9 -> a2 61.8-62.1). It moves the welded wall from th 89.77 to ~94.4. Searched with the
  relay parameters.
* **Track station ds** (bracket instead of lift) was added to one ES (es4, 61 configurations). It found nothing better than
  19.55 fast: the best ds run was 23.87 near-touch.

## Results

### Bench(60,160) fast, lead shape frozen from the phi = 0 fit

Sweep: docs/concepts/sweeps/kfree-armarc-relay-4r.json, 402 entries, 387 of them with relay hardware.

| configuration | gap | near-touch | reach | in-band 14 | contact | note |
|---|---|---|---|---|---|---|
| welded plain 3R, PHI 0 (control) | 39.80 | 39.79 | 0.569 | 0.942 | 0 | the relay's own control |
| welded plain 3R, PHI 0, psi2 -16 | 23.65 | 23.65 | 0.681 | 0.943 | 0.018 | window shift alone |
| ideal relay (no metal, no lift), PHI 45 / 60 / 75, psi2 0 | 14.20 / 11.69 / 8.53 | | 0.769 / 0.794 / 0.825 | 0.928 | 0.010 | |
| ideal relay, PHI 75, psi2 -14 | **3.53** | 4.65 | 0.894 | 0.912 | 0.029 | bound |
| ideal relay at the best axis, PHI 19.4 / 45 / 75 | 17.27 / 11.57 / 9.25 | 18.37 / 13.77 / 13.63 | 0.744 / 0.800 / 0.838 | 0.935 | | same axis, psi2 -8.92 |
| hardware, long axis (tilt 0), PHI 60 | 56.21 | 64.29 | 0.738 | 0.569 | 0.069 | lift 17.0 mm |
| hardware, tilt 12 / taz 235, PHI 60, psi2 0 | 109.46 | 113.99 | 0.506 | 0.846 | 0.080 | 40 jams (E strap on the track), follow 0.38 |
| hardware, best axis, PHI 45, psi2 -8.92 | 27.97 | 35.68 | 0.731 | 0.917 | 0.094 | no jams; 14 contacts, 9 of them the track in the torso at phi = 0 |
| hardware, best axis, PHI 30 | 22.93 | | | | | |
| **hardware, best (near-touch objective)**: PHI 19.42 / tilt 12.05 / taz 236.92 / psi2 -8.92 | **18.45** | **19.55** | 0.7375 | 0.9027 (chain only 0.8653) | 0.022 | lift 5.39 mm, R_t 75.4, arc 44.6 deg / 58.7 mm; overhead 1/12 |
| hardware, best plain gap: PHI 19.07 / tilt 11.73 / taz 238.34 / psi2 -9.28 | 16.64 | 20.08 | | | | |
| the spec's V-roller carriage (tilt 9 / taz 268 / PHI 32) | 34.95 | 36.14 | 0.700 | 0.779 | 0.028 | |

Axis scan (scratch axscan.py: 1 fit, then relay_geometry + a kinematic relay count over 85 axes x 4 PHI):
- The lowest lift at PHI 60 is 4.87 mm (tilt 16 / taz 210, R_t 88.9). That axis jams: 130 jams, all the E strap on
  the track at phi = 0.
- Next lowest: 5.96 (tilt 12 / taz 210), 7.74 (tilt 8 / taz 240).
- Every tilt-0 to tilt-4 axis lifts 12-23 mm.

### Bench(110,360) exact, frozen (the kill test)

Config: the es3 best (PHI 18.88 / tilt 12.23 / taz 239.85 / psi2 -9.53, fast 19.55). The converged best (k 381) is
within 1.1 fast points of it. Dump: docs/research/fold_ceiling/kfree_armarc_frozen_exact.json.

| | gap | near-touch | reach | ws taken | in-band 14 | contact | overhead |
|---|---|---|---|---|---|---|---|
| **this design** | **26.42** | 27.53 | 0.6722 | 242/360 | 0.8885 | 0.0249 | 6/28 |
| same, chain-only in-band (relay shell kept out of the share) | 30.6 | | | | 0.8467 | | |
| lead conecut-knee-knuckle-3r (verified) | 18.28 | | 0.7278 | 262/360 | 0.9012 | 0.0106 | 8/28 |
| ideal relay, PHI 75 / psi2 -14 (bound, no hardware) | 10.22 | 12.77 | 0.8444 | 304/360 | 0.9106 | 0.0466 | 14/28 |

Where this design loses its 118 workspace poses (frozen):
- fold: 103 (no welded solution within PHI 17.3);
- contact: 9 (4 of them relayed);
- J3 stop: 4;
- parts: 2;
- jams: 0.

Other numbers from the frozen run:
- relayed: 26 ws, 22 taken;
- largest relayed phi taken: 17.31 deg;
- minimum metal over taken poses: 0.865 mm;
- lift 5.92 mm, R_t 75.0, arc 44.3 deg.

**Verdict: DEAD.** 26.42 is above the pre-registered kill at 17.5, and above the lead's 18.28 (champion 75.94 on the
same bench).

## Why it dies (measured)

1. **The relay kinematics are excellent.** A cuff relay of 75 deg does K's job and more: 10.22 frozen exact with no
   hardware, against the lead's 18.28. With a free relay, the plain O20 3R at the lead's seats needs no knuckle and no
   drive.
2. **The arm-fixed arc that would do it cannot exist next to the torso.**
   - At the only low-lift axis family (tilt ~12 toward taz ~237; lift 5.4-5.9 mm), the relay must turn toward the medial
     arm. sgn -1 is kinematically wrong: ideal PHI 60 with sgn -1 scores 44.31 fast.
   - At PHI 45 the track (70 deg, 93 mm) sits in the chest at phi = 0, i.e. un-relayed. Across the body (plane 135-150,
     elev 15-75, axial -45..-60) it reaches -0.5 to -10.1 mm (7 of 8 poses below -7). With the arm at the side and axial 60-120 it reaches -5.6 mm.
     The ideal relay keeps these poses clean (+4.2 to +6.4 mm).
   - A spring relay cannot lift its own track off the chest.
3. **The converged optimum therefore keeps the arc short** (PHI ~19). There the ideal relay is only 17.27 fast, and the
   hardware adds the knee stack's lift onto the carriage. The chain's own in-band falls 0.935 -> 0.865, so the relay
   shell's 100 % in-band dilutes the headline (the lead's NEW-strap-dilution class).
4. **Other axes are worse.**
   - Low tilt (0-4): the circle about the GH-elbow line floats 12-23 mm.
   - High tilt / taz 210: the E strap lies on the track at phi = 0 (130 jams).
   - Long arcs at psi2 0: 40-41 jams in un-relayed clips (follow 0.38).

## Red team (own best)

- **Pose that jams.**
  - Kit model: 15 folded-side hub-1 collisions at +45 / +60. In the lead's own metal they become 1-4 'parts' poses.
  - Fast best: 0 hardware jams.
  - The jam cliff sits next to the optimum: psi2 0 at the same axis gives 40 jams at PHI 45-60.
- **Point that pinches.** The un-relayed track in the chest across the body (-10.1 mm at plane 150 / elev 45 /
  axial -60, PHI 45). At the best config, the frozen minimum metal over taken poses is 0.865 mm: a near-touch pose.
- **Optimistic numbers.**
  - The headline in-band counts the shell (100 % in band). Chain-only is 26.42 -> 30.6 frozen.
  - The arm-side lift is radial about a_r, an approximation that keeps the knee closure.
  - The relay friction / hysteresis of the slotted plain guide is not modelled.
  - The continuity flood was not run. It can only drop relayed poses, so the number can only get worse.
  - The metal was fitted on a superset of poses (the welded fit still sees K-open poses past the wall). This is
    conservative for contact.
  - Hub K + links 1a / 1b are kept as metal (first pass, pessimistic for in-band by at most hub K's samples).
- **Gravity determinacy** was not run. It is dead before the spring matters. The sibling's 0.042 N.m at PHI 20 applies to
  this arc.

## Convergence gate

Near-touch objective; 387 relay-hardware configurations; local ES (es1-es5) + axis scan; farm closed. In score points:

| | near-touch objective | plain gap |
|---|---|---|
| gain over the second half | 0.425 | 1.058 |
| gain over the last third | 0.425 | 1.058 |
| top-5 spread | 0.193 | 0.451 |

The near-touch gate PASSED.

## New knowledge

- A cuff relay can replace the knuckle K kinematically, and with margin: an ideal 75-deg relay at the lead's seats scores
  10.22 frozen exact against the knuckle's 18.28.
- Any arm-fixed circular guide long enough to do it must wrap the medial arm, and it meets the torso when un-relayed.
- So the relay's arc length is capped by the torso (~45 deg at R_t 75 on this subject), not by the lift.
- A K-free design that keeps the relay's kinematics needs a relay whose ARM-SIDE metal does not cover the medial arc when
  it is not turned. That means a guide that travels WITH the carriage: a short curved rail riding on rollers fixed to the
  arm at only 2-3 lateral stations, so the long element moves. That moving element then meets the torso only when
  relayed, i.e. in the stretched poses, which are the lateral / overhead ones.

That last variant is the next lever for this column. It is not modelled here.

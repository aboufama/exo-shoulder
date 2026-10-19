# slowpole-slot-knuckle-3r - slow-pole cam-slot knuckle (round 501, G1 golden, lens B)

**Status: DEAD at step 0** (see the verdict below).

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do here that the spec does not ask for.** Check the drive's kinematic
   possibility before the bench, in closed form, over every pin placement, not at the proposer's one point. A pin on
   link 2 driving a slot on link 1a at a CONSTANT ratio has a FIXED relative pole P in link 1b's frame (Kennedy). The
   slot's normal at the pin always passes through P, so the pressure angle on the plate is |90 - angle(uK, C, P)|. A
   low PA needs the pin near the Thales circle over uK-P, while the pin runs 60 deg round u2. That band is narrow, so
   the scan has to cover r 4-45 mm and every phase, at 0.05-0.1 deg of q2 (the onetooth row's lesson: a 0.76 deg grid
   steps over the pole spike). Two more checks the spec does not ask for:
   - **The dwell lock.** The slot's dwell arc locks K only while uK x C has a component along the arc's normal. The pin
     turns 60 deg about u2 over the dwell, so its phase relative to uK changes, and the lock can pass through 90 deg
     (unlocked).
   - **The law shape.** A form-closed slot can carry any K(q2), not only the ghost's linear law. If the constant-ratio
     law fails the PA gate, the designer's move is a variable-ratio (Geneva-like) law that moves the pole with the pin.
     That changes the ghost, and the free-K oracle (17.69) still bounds it.
2. **Rawest material.** The posed-skin signed-distance fields and motion clips of every bench through
   tools/concept_bench.py, on the exact path for the frozen wear: Bench(110,360) exact, and envsel
   (docs/research/minarc_final_polish/env_poses.npz, selection only). The lead's verified model code
   (docs/concepts/models/conecut-knee-knuckle-3r.py), loaded unchanged, for the exact chain kinematics: the law, the
   pole and the slot locus are computed from its unit axes D.u / D.uK, not from the proposer's planar lens. I did not use
   the proposer's digested numbers (slowlaw.py: planar-ish closed form, typed anchor th 106.5).
3. **Specific methods and tools.**
   - Exact spherical kinematics, with all axes through GH. Link 1a sees a link-2 point at c = R(uK, sp K) R(u2, q2) p0,
     the model's _ik_phys convention, checked against G["th"].
   - The slot locus with its normal, its geodesic curvature radius (undercut) and its PA against the plate velocity
     uK x C in link 1b's frame, and the relative-pole distance.
   - The kit's ghost harness (onetooth / shortk: every drive part deleted, the law anchored on the lead's END STATE,
     a1e 54.27 at th 106.3).
   - The frozen protocol: fit on Bench(60,160) fast, freeze, then wear exact.
4. **What, other than me, shows the number is right.**
   - The bench, Bench(110,360) exact frozen.
   - The paired control: the lead's own law through the same ghost harness reads 18.28 / 262, the verified lead
     (onetooth row), so the harness error cancels.
   - The pre-registered kill: ghost > 19.0 or < 258 workspace takes; slot PA span < 60.5 deg of q2.
   - A red-team list of the lost poses (th, dK, why).

## Model

`docs/concepts/models/slowpole-slot-knuckle-3r.py`, built on `shortk-onetooth-knuckle-3r.py` and its parent
`onetooth-slowlaw-knuckle-3r.py` (the verified lead loaded unchanged).

- `OT_CELL=ghost`: every drive part is deleted (lobe, crank, nose, horn, strap sets, crank gates), so a ghost number is a
  BOUND for the morphology, never a claim.
- The K dyad is restored after the lead's chain clamp, which boxes bk1 / bk2 to [26, 32] / [38, 48] (the J7 trap). The
  wear asserts the dyad the model ran: `bk_model`, and KDesign(40/40) gives uK 14.57 deg from the lead's.
- The law |dK| = rho t is anchored on the lead's END STATE: a1e 54.27 at th 106.3, read from the lead's kinematics.
- The drive range DKLIM is the law's end K + 0.7 deg, because the slot's rise end is the stretched stop (WALL=slot).
- Modes:
  - `law`: the closed form on exact kinematics (onset, stroke, K at th 78, msub, uK shift).
  - `slot`: constant-ratio slot locus, PA, undercut, dwell lock, relative pole, hub-2 travel in link 1a.
  - `varlaw`: the variable-ratio law a single pin can carry at PA <= 38.
  - `slotgeo`: preview geometry.
  - `wear`: fit Bench(60,160) fast, freeze, wear exact.
- This is a **law and dyad change, not a metric change**. No bench, judge or kit file was touched.

### Spec corrections (measured)

- **Onset.** The exact onset on 40/40, rho 0.5 is th **56.82**, not 57.2: the proposer typed the end th as 106.5, but the
  lead's kinematics give 106.30. The stroke is 30.29 deg over 60.58 deg of q2.
- **K at th 78** is 12.62 deg, outside the spec's 12.1 +- 0.5 by 0.02 deg. This follows from the same anchor.
- **msub min** is 5.93 (spec 6.1). The cells that pass msub >= 5:
  - 40/40 at rho 0.5 / 0.55 / 0.6;
  - 42/42 at rho 0.5.

  The cells that fail:
  - 38/42 at rho 0.5 (4.55);
  - 40/40 at rho 0.45 (4.25).
- **Hub-2 travel.** Hub 2 moves 20.46 mm relative to the link-1a plate over the stroke, which reproduces the judge's 20.5.

## Step 0 - law-only ghost (drive metal deleted; Bench(110,360) exact frozen; fit Bench(60,160) fast)

| cell | uK vs lead | onset th | msub min | fit fast | **frozen exact** | ws takes | contacts | ib14 | hub K ib14 (median mm) | L1a / L1b ib14 | overhead |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lead (control, onetooth row) | 0 | 77.9 | 10.75 | 12.50 | **18.28** | 262 | 4 | 0.901 | 0.992 (7.9) | - | 8/28 |
| **40/40 rho 0.5 (spec)** | 14.57 | 56.82 | 5.93 | 33.40 | **40.17** | 254 | 17 | 0.738 | **0.033 (45.7)** | 0.18 / 0.32 | 4/28 |
| 34/40 rho 0.67 (limiter variant) | 8.08 | 63.12 | 6.16 | 13.12 | 19.38 | 260 | 6 | 0.918 | - | - | 7/28 |
| **32/38 rho 0.67 (limiter variant)** | 6.41 | 59.26 | 5.00 | 13.12 | **18.83** | 261 | 5 | 0.920 | - | - | 8/28 |
| **32/38 rho 0.84 (slot law at pin r 18)** | 6.41 | 65.77 | 7.75 | 13.12 | **18.83** | 261 | 5 | 0.908 | 0.973 | 0.98 / 0.95 | 8/28 |
| 32/38 rho 1.04 (slot law at pin r 20) | 6.41 | 70.47 | 10.22 | 13.12 | 18.83 | 261 | 5 | 0.918 | 0.972 | 0.98 / 0.91 | 8/28 |

All of these are fit on Bench(60,160) fast, frozen, and worn on Bench(110,360) exact. Every number is a ghost, so it
bounds the morphology from above. It is not a claim. The 32/38 rho 0.84 row reads near1 19.92 (the lead's is 19.92),
near2 34.64 (the lead's is 34.84), min metal 0.07 mm and fold 88 (the lead's is 88).

**The spec cell dies on hub K, not on the law.** On 40/40, uK sits 14.6 deg from the lead's K axis. Hub K is fixed on
link 1a along that axis, so it has to clear the highest skin it ever passes over. That puts it **45.7 mm (median) off
the skin**: 3 % of poses are in band, and it still touches on 17 poses (overhead IR, plane 30-75 elev 135-165). Links
1a and 1b follow it, at 0.18 / 0.32 in band. Reach is close to the lead's: 254 takes against 262, with fold 88 in both.
The slow law itself is not the cost:

- On the 32/38 dyad, rho 0.67, 0.84 and 1.04 read **exactly 18.83** (261 takes, the same 5 contact poses).
- The shortk row's 34/30 dyad reads 18.83 at every rho from 1.1 to 2.5.
- The onetooth row lost takes at rho 0.8-0.9 on the lead's dyad because msub fell below 5 there. With msub >= 5,
  the law's onset does not matter.

The re-seat costs the lead one take and one contact: 18.83 against 18.28. Pose 139 is the new contact (plane -60,
elev 60, axial 105, 0.2-0.5 mm), on hub K / hub 2. The other four are the lead's own (205, 237, 264, 316, hub 2).

**Where the hub-K cliff sits.** The uK shift is 6.4 deg at 32/38 (18.83), 8.1 deg at 34/40 (19.38) and 14.6 deg at
40/40 (40.17). A slow law needs msub >= 5, and msub grows with bk1. So the slowest law the kill gate allows lives on
dyads within ~7 deg of the lead's K axis.

## Step 1a - can ONE pin in ONE slot carry the law? (closed form, exact spherical kinematics)

`slot`, `varlaw` and `dwell` modes. The gate is PA <= 43 - atan(0.087) = 38.03 deg (crowned 440C pin on DLC, sliding).

1. **Constant ratio: no.** At a constant rho the relative pole P is fixed in link 1b's frame, and the slot normal always
   passes through it. The PA-passing band is the neighbourhood of the Thales circle over uK-P, and a pin turning round
   u2 cannot stay in that band for the whole stroke.
   - **40/40, rho 0.5.** Over 3,024 placements per cell (r 4-45 mm x 5 deg phase, 4 cells), the longest PA-passing run
     is **49.5 of the 60.5 deg of q2** needed. At r <= 20 mm (a lug on hub 2's rotor) it is **46.4**.
   - The spec pin (r 13.5, phase 17) passes only 26.45 deg (PA 56 at the onset).
   - The other cells: rho 0.55 47.1 / 55.0, rho 0.6 44.8 / 50.4, 42/42 50.3 / 56.8.
   - On 32/38, rho 0.67, the best run is 39.8 of 55.8.
   - **The spec's slot drive fails its own kill** (PA span < 60.5 deg of q2).
2. **Variable ratio: yes.** A form-closed slot can carry any monotone K(q2). Integrating backward from the end state,
   with the largest ratio whose PA <= 38 at each 0.25 deg of q2, finds the latest-onset law a given pin can carry:
   - **40/40, pin r 13.5 / phase -60.** rho 0.38-0.56 (mean 0.508) completes 30.3 deg of K over 59.75 deg of q2 from
     th 57.49 (msub 6.24). That is the spec's law with a ratio that varies +-0.1.
   - Below r 11 no law completes, because the pin is too close to u2.
   - Faster laws need bigger radii: r 16 (onset 65.8), r 20 (onset 73.7).
   - **32/38.** 73 of 576 placements complete (r 8-20).
3. **The dwell lock kills the slow placements.** The dwell arc (concentric with u2) reacts a K torque with lock angle
   angle(n, uK x C). It reaches 90 deg (K unlocked: the plate slides along its own arc) where the pin crosses the
   u2-uK great circle. At the 40/40 r 13.5 / phase -60 law, the pin is on that circle at the onset: **lock max 89.1 deg**.
   On 32/38, 8 placements keep lock <= 80 deg and msub >= 5:
   - **pin r 18 / phase 5**: law rho 0.62-0.94 (mean 0.84), onset th 66.1, lock <= 36.3, play 0.08 deg per 0.05 mm of slot clearance;
   - **pin r 20 / phase 5**: rho 0.82-1.14 (mean 1.04), onset th 70.8, lock <= 31.1.

   The constant-ratio ghosts at rho 0.84 and 1.04 stand in for these two laws: same onset, same end state, same
   stroke. Both read 18.83.

## Red team (own best cell: 32/38, pin r 18 / phase 5, the rho 0.62-0.94 slot law)

- **The optimistic number: PA rides the gate.** The greedy law sits at PA = 38.0 over part of the stroke, with zero
  margin. With margin the same pin still carries the stroke:

  | PA gate | onset th | msub | rho range |
  |---|---|---|---|
  | 35 | 64.4 | 7.1 | 0.54-0.92 |
  | 32 | 62.5 | 6.3 | 0.46-0.90 |

  Both onsets stay inside the band where the ghost reads 18.83 (onset 59.3-70.5 all read 18.83).
- **The constant-ratio stand-in.** The ghost runs a constant rho with the slot law's onset and end. On 32/38 the law
  does not move the number (three rho values give identical takes and contact poses), so the stand-in is safe.
- **The pose that jams.** At the spec's slow placements, the dwell lock goes to 89 deg (K unlocked at the onset). At r 18 /
  phase 5 it is <= 36.3 deg, with 0.08 deg of K play per 0.05 mm of slot clearance.
- **Undercut.** The constant-ratio locus at r 18 has its minimum curvature radius at 2.19 mm, against a pin radius of
  1.25 (no undercut). The relative-pole approach is 0.049 mm per deg.
- **The point that pinches.** The chain's new contact is pose 139 (plane -60, elev 60, axial 105: across-the-body ER),
  0.2-0.5 mm into the skin at hub K / hub 2. The worst contact is the lead's own pose 237 (15 / 165 / -60), -5.45 mm on hub 2.
- **The drive metal** is the real test: see step 1b. It fails.

## Step 1b - the drive metal (proxy on the frozen ghost's 371 taken poses, Bench(110,360) exact)

Script: scratch `slowpole/metal.py`. It places an O6 x 3 lug with an O2.5 pin, 2 mm proud, on hub 2's rotor (link 2)
at the pin radius, plus the slot plate (locus +-3 mm, 1.5 mm thick, at the pin top) on link 1a. Each face is
skin-checked with the bench's signed distance, using the shortk row's metal-proxy transforms. The level is the lug's
underside above hub 2's skin-side face f2 = 62.2 mm.

| pin (r mm / phase) | lug level | lug contacts (min mm) | pin contacts (min) | plate contacts (min) |
|---|---|---|---|---|
| 18 / 5 (the slot law's pin) | hub face (0) | 31 (-8.3) | 19 (-7.1) | 30 (-10.1) |
| 18 / 5 | top of the stack (+9.25) | 20 (-10.6) | 16 (-9.2) | 23 (-12.0) |
| 13.5 / 5 (closest legal lug) | +9.25 | 14 (-5.6) | 12 (-3.9) | 15 (-6.3) |

The worst poses are always the same overhead set: the clip frames 7-12 at plane 30 / elev 142-150 / axial -60, plus
ws 287 (45 / 120 / -30) and 290 (45 / 150 / -45). There the arm's own bulk rises beside hub 2, so raising the lug makes
it worse. The lead's link-2 sweep proxy shows the same: 2 contacts at -14 mm for a link-2 point 12 deg from u2. The spec's
kill is > 4 sweep contacts; this is 12-31.

Caveat: only phase 5 was skin-checked. The other lock-safe, PA-passing placements on 32/38 are r 18-20 at phase 5-15,
next to it, so a fix by phase alone is not expected.

## Verdict

**DEAD.** Two pre-registered kills are met.

1. **The spec cell fails step 0.** On a 40/40 dyad with rho 0.5, the law-only ghost reads **40.17** frozen exact
   Bench(110,360): 254 ws takes and 17 contacts, against the 19.0 / 258 gate. The cause is hub K. The long symmetric
   dyad moves K's axis 14.6 deg, to where hub K must stand 45.7 mm off the skin.
2. **The limiter variant survives step 0 but fails step 1.**
   - **Step 0.** On 32/38 (uK 6.4 deg off the lead's), the ghost bound is **18.83** at any law from rho 0.67 to 1.04:
     261 takes, 5 contacts, ib14 0.908-0.920, overhead 8/28. That is the lead's 18.28 minus one take and plus one
     contact.
   - **The constant-ratio slot.** It cannot carry the law at PA <= 38 at any pin placement.
   - **The variable-ratio slot.** It can (rho 0.62-0.94 at a pin r 18 mm / phase 5, onset th 66, dwell lock <= 36 deg).
   - **The metal.** The pin lug and slot plate sit 4-12 mm inside the skin on 12-31 overhead poses.

Even as a ghost the row cannot pass the lead (18.83 > 18.28), and the free-K oracle caps it at 17.69. Its only possible
value was the Pareto cell, cx 10.75 at <= 18.95. The ghost leaves 0.12 points of room there, and the drive metal costs
far more.

**Convergence gate (stated, not passed):**
- 5 ghost configurations;
- best gain over the second half 0.0 points and over the last third 0.0;
- top-5 spread 7.75 score points (21.3 gap, the 40/40 spec cell included);
- 0.20 points over the four limiter variants.

The death rests on the pre-registered kills and on the closed-form scans, which are exhaustive over pin placements
(12,672 constant-ratio and 576 variable-ratio slots), not on a search optimum.

## New knowledge (predicts beyond this row)

1. **A slow K law is free on a mid dyad; a long dyad is not.** With msub >= 5, the law's onset and rate do not move the
   ghost: 32/38 reads 18.83 at rho 0.67 / 0.84 / 1.04, and 34/30 reads 18.83 at rho 1.1-2.5. What costs points is
   where uK sits. The hub-K proximity cliff:

   | uK shift from the lead | ghost |
   |---|---|
   | 6.4 deg | 18.83 |
   | 8.1 deg | 19.38 |
   | 14.6 deg | 40.17 (hub K in band 0.03, 45.7 mm median) |

   So any re-seated-K drive must keep uK within ~7 deg of the lead's.
2. **A single pin in a slot cannot hold a constant ratio over a long stroke.** The relative pole is fixed, so the PA
   band is the Thales neighbourhood of uK-P. With a variable ratio the pole moves with the pin, and one pin then carries
   the full stroke from r ~11 mm upward (faster laws need larger r).
3. **A dwell arc concentric with J2 unlocks K where the pin crosses the J2-K great circle** (lock angle 90). A
   form-closed dwell-and-rise slot needs the pin's whole phase sweep (dwell + rise, ~100-120 deg about u2) on one side
   of that circle. That rules out the slow, small-radius placements.
4. **Any link-2-mounted drive element outside hub 2's rim (r >= 13.5 mm) goes 4-12 mm into the skin at overhead IR**
   (plane 30-45, elev 142-150, axial -45 to -60), because the arm rises beside hub 2. Raising the element makes it
   worse. Drives for K must live on link 1a / 1b or inside hub 2's rim.

## What next

The fold lever cannot come from a re-seated K with a link-2 pin. The open cells are a K drive whose drive element stays
on links 1a / 1b or inside hub 2's O20 rim (the lead's lobe class, priced 18.5), and round 301's mirrored-K crossover.

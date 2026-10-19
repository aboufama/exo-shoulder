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

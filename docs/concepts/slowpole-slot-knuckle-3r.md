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

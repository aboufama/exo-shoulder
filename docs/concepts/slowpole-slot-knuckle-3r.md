# slowpole-slot-knuckle-3r - slow-pole cam-slot knuckle (round 501, G1 golden, lens B)

**Status: in progress (step 0 ghost running).**

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

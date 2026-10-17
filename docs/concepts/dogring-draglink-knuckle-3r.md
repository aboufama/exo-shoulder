# dogring-draglink-knuckle-3r - dog sector + spherical drag link driving the slaved knuckle K

## Deeper version (answered before the work)

1. **What a top mechanism designer would do that the spec does not ask for.** Lay the drive out in the *layers that
   already exist* before pricing it: at hub 2 link 1b is the LOWER member (f2 .. f2+3) and link 2 the UPPER (f2+3.15 ..
   f2+6.15, measured on the model's own link samples); at hub K link 1a is lower (fK) and link 1b upper (fK+3.15), and
   both links ramp DOWN to the skin within r 11.5-14 of each hub. So (a) the spec's ring "at link 1b's top + 0.15" is
   link 2's root layer, which link 2 sweeps over its whole q2 range - physically impossible; the honest stacked control
   sits above link 2 (f2 + 6.3); (b) a ring in the skin-face layer (f2) must be a C-SECTOR that clears link 1b's root
   over the swing, and then the DOG can be link 2's own root flank (it ramps down through that layer at r 11-13) - no
   dowel, PA 0, no sliding; (c) the arm, the drag link and the horn must swing ~35 deg (arm) and ~75 deg (horn)
   RELATIVE TO LINK 1B, which owns the corridor between hub 2 and hub K - so the binding check is not the PA table but
   the swept clearance of each drive body against link 1b over the drive's own range. Synthesis must be done on the
   fitted design's own u2 / uK (the judge's seeds came from another fit and fail PA at K = 0 here).
2. **Rawest material.** The posed skin itself through the bench's grid distance (every drive point is a rigid-part
   sample priced pooled by the bench, not a side harness), the motion clips of Bench(60,160) / Bench(110,360) and the 952
   held-out poses, the model's own link / hub samples (levels and azimuths read off them, not from docs).
3. **Methods and tools.** Spherical 4R closure by continuation (all axes through GH) with PA at both pins; vectorised
   synthesis per K-dyad cell on the fitted u2 / uK (~23k candidates per cell); the parents' per-t law gates (th monotone,
   rate <= 3.45, lift-off, stop B); swept-volume clearance of sector / arm / drag link / horn vs link 1b, hub 2, hub K in
   link 1b's frame over K = 0 .. table end -> dK_lim (stop B dowel there, every pose past it lost on every bench); per-pose
   collide() with the family's 1 mm rule; the CPU farm for every batch; frozen exact Bench(110,360) for the claim.
4. **What shows the number is right, other than me.** tools/concept_bench.py (the outside judge; pooled in-band over all
   metal points), the frozen-exact protocol of the family (fit fast, freeze, wear on Bench(110,360) exact), the held-out
   bench, and the round-11 verifier / red team (pose list: rest, overhead elev >= 140, across the body, behind the back).

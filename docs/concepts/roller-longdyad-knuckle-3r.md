# roller-longdyad-knuckle-3r: the re-cut roller flank on the long K dyad

Round 9, pick 1. The judge sized the lever as the drive stroke: the lead's taken th max is 109.2, which is the RSSR
stroke wall, not stop B. A re-cut flank (dK_lim 56-64) should raise that wall to 117.5-120.2. Complexity 44.0
(lead 49). 3 active DOF, K slaved and never read, 0 passive translations.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Check that the wall is really the drive. On a slaved knuckle, three things end the stretched window: the drive's
     stroke (dK_lim), stop B (a1max), and the J1-J2-J3 dyad margin of the effective first link a1e(dK). The law
     decides that third one: where K sits as q2 grows. A longer flank is worth nothing if the law opens K too slowly to
     keep m3e >= 5. So the gate also logs m3e and the law gain kK per lost pose, not only dK_lim.
   - Treat the flank boss's height over the skin as a design variable from the start. The no-refit wear put the horn on
     the skin on 88 of 89 contact poses.
   - Size the pressure angles against the real K slop.
   - Count the roller's retaining head as metal on the skin side.
2. **The rawest material.**
   - The posed skin through the bench's exact signed distance: the Bench(110,360) poses and the clips.
   - The lead's own IK, per pose: th, dK, a1e, m3e, msub, knee state.
   - Not the judge's wall table. That table assumes a1 is held and the law keeps up, and it is re-derived here.
3. **The methods and tools.**
   - The lead's and the roller-flank model's code, loaded unchanged. The cam is synthesised per 0.25 deg of K, with
     both pressure angles, lift-off, cusp, contact on the lug, and arm / roller / lug clearances.
   - A law-only gate on Bench(110,360) via the fitted design's own IK.
   - A per-part contact split.
   - The farm for the sweep and CMA-ES on the 2 mm near-touch gap.
   - Frozen exact wear on Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench, and the frozen exact Bench(110,360) wear (plain, 1 mm and 2 mm).
   - The round's verifier harness (docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py style). It re-checks cam
     closure in the world, the roller never inside the lug, and K inside the drive's range.
   - A red-team pose list: overhead axial -135, the far flank end, and the poses at the new wall.

## Status

Modelling (see the row docs/concepts/rows/roller-longdyad-knuckle-3r.json for the numbers as they land).

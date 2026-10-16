# twin-k2-sidecar-knuckle-3r - a second slaved knuckle K2 on link 2, opened past the lead's drive wall

## Deeper-version answers (written first, 2026-10-16 21:30 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the space before the mechanism:
   the twin knuckle puts a 5th O20 stack within ~22 mm of hub 2 on the bend side, beside a crank that already lives there
   (the lead's drive 1). So the first measurement is not the law but the *sweep* - which bodies pass over hub 2's
   neighbourhood as q2 turns (crank 1 on link 1b, crank 2 + hub K2 on link 2a) - and whether hub K2 can park in band
   on the posterior-lateral cap at all. Then: run the spec's law-only gate and the metal with drive 2 OFF as a control,
   so the cost of the K2 stack alone is separated from the cost of its drive; and use a *track* law (least K2 opening
   that keeps m3e at smt2) so the extension is monotone - the lead's 267 taken poses cannot change.
2. **Rawest material.** The bench's posed skin (CB requirement along every hub ray, exact path on Bench(110,360)), the
   clip frames themselves, and the lead's own per-pose IK (th, a1e, dK, m3e per pose) - not the proposer's crude
   parking map. The drive wall is re-derived from the lead's law table (m3e hits 5 at t 23.7, th 109.5, dK 38.5), not
   copied from the judge's note.
3. **Methods / tools.** The lead's model (sidecar-longdyad-knuckle-3r.py, verified code) as the parent class; the
   split-knuckle-twosided-3r machinery (5-hub fit, L2a / L2b straps, hubK2 cap, 5-hub collision pairs) re-based on it;
   a vectorised (t, dK2) grid for the twin law; tools/cloud_run.py for the sweep; the lead's frozen protocol
   (fit Bench(60,160) fast, worn on Bench(110,360) exact) for the claim.
4. **What, other than me, shows the number is right.** The bench (concept_bench), the lead's own verified number
   reproduced through this file with K2 off (control), the per-part in-band / pair counts the bench reports, and a red
   team pose list (the poses K2 opens on, the crank-crank and hub K2 - hub 1 pairs).

(The measured record follows below; it is appended as the screen runs.)

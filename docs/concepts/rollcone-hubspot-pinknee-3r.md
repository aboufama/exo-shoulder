# rollcone-hubspot-pinknee-3r - rolling-cone J2 at H1's hub-2 spot (round 501, G1)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the rolling pair as what it is
   kinematically - a 2R (sun axis uK, planet axis v2, both through GH) with a fixed linear coupling x = rho y - and
   read its singularity in the SAME metric as every verified row: the instantaneous dyad (u1, contact line, J3) margin
   >= 5 deg, plus the segment-extremum margin. Model the metal as what a strap-held pair can be: two conical walls at
   ONE radius each (a common strap radius +- 1.5 mm), no per-direction contour, and make the links reach the walls (a
   link that cannot meet its band lifts the band). Then search where the metal, not the ghost, wins: the band
   geometry (half angles, split plane beta, rest-zero) jointly with H1's seats and knee, on the near-touch objective.
2. **Rawest material.** The posed skin itself through the bench's exact signed distance (tools/concept_bench.py, the
   per-pose sphere-traced need of every band sample), the 10 fps fit clips for continuity, the rest-pose skin for the
   seats (offset-skin-normal-3r seat()), H1's verified best_params as the start - not the judge's ray-rule digest.
3. **Methods and tools.** H1's model (skin-normal-3r-pin-knee.py: O20 hubs 1/3, kit near-touch, closure, jam rule,
   knee window) subclassed; rolling IK by tabulating th(y) on the rest segment (0.25 deg) and interpolating;
   one-level-per-part band fitting through the seed's needed()/greedy_drop() (both bands in ONE level group);
   collisions band-band (outside the contact line, adjacent 0.15 mm), band-hub, band-link, band-knee; local
   random + CMA-ES on Bench(60,160) fast, frozen exact read on Bench(110,360).
4. **What shows the number is right, other than me.** The bench's report (gap from its own distances), the frozen
   exact Bench(110,360) wear, the auditor / verifier re-run of this model file, and the red-team pose list
   (redteam mode: poses not taken with cause, closest metal per part, near-touch at 1 / 2 mm, named pose groups).

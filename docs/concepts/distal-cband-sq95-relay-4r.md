# distal-cband-sq95-relay-4r: distal C-band relay at s 0.70 on the knee-less O20 3R (round 401 K1, lens C)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Read the strap as the part that decides the row, not the ring. A ~220 mm bar from hub 3 to s 0.70 runs past the
     deltoid bunching at the top and into the across-body torso zone at the bottom; the ring at s 0.70 is the easy part
     (the arm is round there). So the strap gate goes first and its losses are attributed per station along the strap.
   - Separate the band's two jobs: the underside follows the skin per (azimuth, width) while the race top is ONE surface
     of revolution about the relay axis. The carriage rides the race, so the carriage height over skin is set by the
     WORST skin per azimuth over all poses, not by the median. Price that with the race quantile as a design variable
     (q 1 = no in-sample band contact but a floating carriage; q < 1 = carriage in band, some poses lost as contacts).
   - Fit the band per POSE, not per ray: a pose with other skin (torso, forearm) over the band is lost as a whole; letting
     its clean rays still set the race max floats the carriage for everyone.
   - The strap's first 10 mm is hub 3's lower plate: model the strap from the plate rim, with its underside never below
     its own fitted requirement (a joggle onto the plate where the deltoid stands proud).
2. **The rawest material.** The posed skin itself through B.dist / K.requirement (exact signed distance of every metal
   sample, rays marched from the relay axis per (psi, w) at the station and from GH along the strap); the relayed
   humerus frames from the least-phi solve on the whole archive; the lead's own fitted chain metal (conecut CC model
   samples, frozen). Not the req60 / band.py digests (one 6-mm slice about the GH-elbow line, no strap, no link metal).
3. **The specific methods and tools.** insertion-cband-relay-4r.py's ideal + J4 hardware machinery (imported, not
   copied; it sits on kfree-armarc-relay-4r.py lead_eval: K welded through the |dK| <= 0.1 deg gate, drive stripped,
   knee-side samples dropped), with this row's station, axis, race arc and sampling radius; the frozen protocol (fit on
   Bench(60,160) fast, wear exact on Bench(110,360)); the th fold margin in the one metric; analytic beam theory for the
   strap deflection (12 x 3 Ti-6Al-4V, E 114 GPa, cantilever from hub 3).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, exact path on
   Bench(110,360)), the judge's pre-registered gates (strap gate; ideal > 14.0; hardware > 17.0), the round's adversarial
   verifier and the alignment auditor, and the red-team pose list below (deep across-body IR over the posterolateral
   distal arm, abduction / IR at the strap's hub end, the race's worst azimuth).

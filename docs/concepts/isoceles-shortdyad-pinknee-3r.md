# isoceles-shortdyad-pinknee-3r: the cx-0 knee-class frontier (round 501, G1 golden, lens A)

H1's morphology (plain O20 3R, J1 / J2 on GH rays, J3 tilted b3 toward the skin normal, closed at the cuff by the flat
MR63ZZ two-pin knee - cx 0) re-seated in the three knee-class cells the round-501 proposer found: seed A isoceles short
dyad (a1 40.5 / a2 44.9, J1 lateral acromion top, hub 2 posterolateral), seed B posterior slot (a1 47.5 / a2 73.4),
seed C pole-J1 (a1 64.3 / a2 45.8). 3 active joints, 2 passive pins (cuff knee, outside the count), 0 passive
translations. Model: docs/concepts/models/isoceles-shortdyad-pinknee-3r.py (crest-knee-3r.py imported unchanged + the
a1 / a2 re-solve + h2clip + the conditioning report).

## Deeper-version answers (written first, 02:50 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the J2 seat as an OUTPUT, not
   a parameter: solve az2 / el2 from J1's ray, J3's tilted axis and the cell's arcs at every b3 (the proposer's 45.82
   read ran b3 0.2 at a2 43.8 - the cell was never measured). (b) Test the cuff end first and with both knee forms the
   kit has (flat, and the joggled knee kj=1 that puts the E boss and the arm pad at their own levels), because the
   proposer's coarse read had E 0.66 / boss 0.52 / knee 0.61 in band - the chain itself is in band. (c) Report the
   fold conditioning |u1 . (u2 x w)| beside the score: an isoceles dyad near its folded edge splits one arm motion
   between q1 and q3 (feel, and the powered product's torque), so a score bought on badly conditioned poses is not the
   same score. (d) Not chase 95 here: the proposer's own frontier puts take >= 0.74 at hub 2 <= 0.54 in band, so the
   honest question is a cx-0 Pareto point over H1 (27.20 verified), and the fold (40 of 220 fast poses at every b3)
   is the wall to attribute, not to tune to the sample.
2. **Rawest material.** The posed skin through the signed-distance grids (Bench(60,160) fast cache 0089c747c10f for the
   search, Bench(110,360) exact for the claim), the per-pose per-sample needs the model computes (Hneed / Lneed: the
   level each piece of metal must sit at in each pose), the per-pose th / q / knee angle arrays and the bench's
   why-not labels - not the proposer's digested bound table.
3. **Methods and tools.** The verified pin-knee VModel checks (closure < 0.5 deg, 10 fps continuity incl. the knee
   branch, jam rule, part-part clearances, near-touch, crowns / walls contact-only) via crest-knee-3r.py; the re-solve
   (spherical-triangle closed form, the posteromedial-knuckle algebra); a Sobol coarse sweep over the spec's box, then
   CMA-ES (tools/concept_cma.py, near-touch objective) from the top; the convergence gate from the sweep in time order;
   claim = the frozen search-bench shape worn on Bench(110,360) exact.
4. **What else shows the number is right.** tools/concept_bench.py (not this code); H1's verified number through the
   same base code; the verifier harness docs/concepts/verify/crest-knee-3r.py (it builds the same CK model); the
   red-team list below (lowest metal pose, the worst-conditioned takes, overhead / across / behind-the-back poses).

# crest-knee-3r: deltoid-crest seats on the pin-knee chain

Round-14 lens 3 (crest-pinknee-cx0), catalogue row crest-knee-3r (round-4 pick). A PLAIN O20 3R (three pins on bearing
pairs, no drive, no spring) with the two-pin MR63ZZ cuff knee (cx 0 under simplicity v2.2), moved from the verified
pin knee's back-of-shoulder seats (H1, k4598) to the deltoid-crest seats, with link 2 flying over the whole member 3
and an optional J3 own-angle stop. 3 active joints, 2 passive pins (cuff knee, outside the count), 0 passive
translations.

## Deeper-version answers (written first)

1. **What a top mechanism designer would do that the spec does not ask for.** The spec says "run the pin-knee model
   unchanged at the crest seats". The literal antcrest seats (J1 bvec(55, 62)) are already measured dead (hub-2 need
   50-400 mm; 86.12 fast with E in the free sector, hub 2 at 192.8 mm; round14_ideation section 5). A designer would
   (a) let J1 / J2 / J3 move inside the crest basin jointly with the knee instead of fixing seats and tuning only the
   knee, because the knee's free sector, link 2's fly-over and hub 2's level are coupled; (b) treat link 2's crossing
   of member 3 as a real layer order (fly-over of the E strap + boss, not only knee + pad); (c) carry the J3 window as
   a physical dowel-in-slot stop on J3's own angle and freeze it from search to claim; (d) put the knee pins at their
   build stack (MR63ZZ pair, stk 6.0, the lead's build rule) and the knee window at >= 25.22 deg (rule edge) from the
   start; (e) pair everything against H1 run through the SAME code (23.64 fast here) so a gain is a seat gain, not a
   check change.
2. **Rawest material.** The posed skin itself through the bench's signed-distance grid (Bench(60,160) fast cache
   0089c747c10f; Bench(110,360) exact path), the 10 fps fit clips for continuity (CB.FIT), the per-pose dumps of the
   model's own IK (q1, q2, q3' = q3 + phi, knee angle, drift), and the J2-exit / skin-motion data of the antcrest
   basin (round-102 judge's j2exit, round14_ideation section 5) - not the digested "fold 20-24 of 220" summary.
3. **Methods and tools.** docs/concepts/models/skin-normal-3r-pin-knee.py unchanged (its Design / closed-form IK /
   two-circle knee / VModel rules / part-part clearances / contact-only walls and crowns) subclassed in
   docs/concepts/models/crest-knee-3r.py (fly-over E box, J3 window with a frozen claim path, frozen() that copies the
   whole fitted shape). Search: local CMA-ES (numpy, own implementation; the farm is closed) on Bench(60,160) fast with
   the near-touch gap as objective (scored samples < 1 mm on a taken pose count as contact), two independent starts
   (cells C1 and C3). Claim: frozen shape on Bench(110,360) exact; red team with the model's redteam pass (closest
   metal, contact-only walls, near-touch at 1 / 2 mm, rest / overhead / across / behind groups).
4. **What else shows the number is right.** The bench (tools/concept_bench.py, not this file's code), the H1 control
   through the same code (23.64 fast, matches the alignment re-measure), the frozen exact Bench(110,360) run, the
   round-14 judge's J3-stop control table (section 4: a stop gain that only relabels near-zero overhead touches at a
   0.5 deg band does not count), and the adversarial verifier (docs/concepts/verify/) that re-runs the claim.

## Status

(filled in at the end of the time box)

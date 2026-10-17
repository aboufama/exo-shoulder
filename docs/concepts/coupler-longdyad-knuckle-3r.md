# coupler-longdyad-knuckle-3r - hub-2 lobe + crank on dR + spherical-4R coupler driving the slaved knuckle K

## Deeper version (answered before the work)

1. **What a top mechanism designer would do that the spec does not ask for.** Before pricing PA tables, ask *where the
   crank tip and the coupler physically go relative to the skin*. The spec's stage 2 swings a 30 mm arm 27-37 deg about
   an axis on link 1b and sends a 35-45 mm coupler across to hub K; every PA-legal geometry points the arm SIDEWAYS
   (t1 = +-55..110 deg off the dR -> K line), i.e. off link 1b's skin-fitted corridor onto the deltoid / the anterior
   shoulder. The chain's own links are levelled to clear the highest skin they pass over (the proximity atlas rule);
   a drive that lives beside them must obey the same rule, so the honest test is (a) the drive at link 1b's level
   (what the proposer priced: contacts) and (b) the drive SKIN-FITTED like the chain (raise each section until it
   clears every fit pose by 1 mm: contacts gone, in-band priced). If (b) costs > 14 mm of lift somewhere the drive
   cannot be both clear and in band, and that is the verdict. Second: re-synthesise stage 2 on THIS fit's u2 / uK / dR
   (the seed pins came from another fit), with the horn eye clear of hub K's O20 + 1 mm (r_h >= 15, a3 >= 14.7 - the
   spec's 13.5 floor puts the coupler eye 0.07-0.9 mm from hub K's housing). Third: the lobe skirt (12.8) caps the
   crank angle at 32.6 deg (s_nose 4) - the stage-1 wall the round-11 plan predicts; s_nose 3.5 lifts it to 37 deg.
2. **Rawest material.** The posed skin itself through the bench's grid distance (every drive sample is a rigid-part
   sample priced pooled by the bench, and the skin-fit raise is sphere-traced against the same distance field on the
   fit bench's poses), the motion clips of Bench(60,160) / Bench(110,360) and the 952 held-out poses, the model's own
   link 1b / hub samples (levels, layers), the proposer's own scratch harness (coupler_lens/metal.py) as a cross-check.
3. **Methods and tools.** Spherical 4R closure by continuation (all axes through GH) with PA at both pins (the dogring
   row's solver, reused); per-fit re-synthesis (12k + 8k random pin sets, 4R table PA <= 42 and crank monotone to
   K >= 77); the parents' per-t law gates plus stage 1 on the real follower (lobe radius, lobe PA <= 42 - atan(mu));
   swept clearances in link 1b's frame (drive range dK_lim, stop B there); per-pose collide with the family's 1 mm
   rule; the CPU farm for the coarse sweep (256) and ONE CMA batch (4 starts); frozen exact Bench(110,360) + held out.
4. **What shows the number is right, other than me.** tools/concept_bench.py (pooled in-band over all metal points,
   contact on metal < 0), the family's frozen-exact protocol (fit fast, freeze, wear on Bench(110,360) exact), the
   held-out bench, the K-open drive-contact count (the lead note's kill rule) read on the same bench distances, and the
   round-11 verifier / red team (rest, overhead elev >= 140, across the body, behind the back).

(Verdict, numbers and red team below - written after the measurements.)

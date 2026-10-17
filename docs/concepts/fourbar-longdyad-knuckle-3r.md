# fourbar-longdyad-knuckle-3r - toggle four-bar knuckle (strap cell), LISTED FOR THE USER'S B1 RULING

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the four-bar as a *stacking* problem
   before a *law* problem: a spherical four-bar on ground link 1b puts a third layer (the coupler) on top of link 1b and
   two eye columns beside two O20 housings. The designer would (a) check that each eye boss (O9 for an MR63ZZ eye, not
   just the O3 pin) clears the hub housings below the crown, (b) give the coupler the 1 mm non-adjacent clearance to
   link 1b (it is not jointed to link 1b; the spec's +3.15 is a running gap), and (c) price the stack height as in-band
   loss before trusting any law-only count. Second: read B1 as a *sub-chain singularity* question - m_sub < 5 means the
   J1-K-J3 sub-chain is near its own fold, so even a positively slaved K sees th become insensitive to K there; the
   coupled reading is physically defensible only if the four-bar's own transmission at the horn holds through those
   poses (mu_h is gated at 48-132 here for exactly that reason).
2. **Rawest material.** The bench's posed skin itself (tools/concept_bench.py exact path and its grid cache), the motion
   clips through the bench's clip frames, the fit / held-out split; not the parking estimates or the proposer's law-only
   counts (those were synthesised against Bench(110,360) workspace poses - the verification sample - so they are not an
   independent check; held-out is).
3. **Methods and tools.** Closed-form spherical four-bar (crank cone about u2, horn azimuth from A cos b + B sin b = C),
   the generic slaved-K inverse (th -> tau -> q2, K, q1, q3), the lead's verified chain model (longstroke-slipper ->
   roller-longdyad -> sidecar -> frontload -> geneva-pinknee -> minarc kit-rule classes) with its skin, in-band,
   near-touch and part-pair checks, per-pose bodies for the coupler (member 8, its rotation about GH from the pin pair),
   the farm sweep (tools/cloud_run.py) and the frozen claim protocol.
4. **What shows the number is right, other than me.** The bench (Bench(60,160) fast, then the frozen shape on
   Bench(110,360) exact and held out), the verifier harness pattern (frozen + audit near-touch + th_margin), the B1 count
   by |K| band, and a red-team pose list (overhead cone, across-the-body, behind-the-back, the toggle frames).

(Results, limiter and red team below are filled in as measured.)

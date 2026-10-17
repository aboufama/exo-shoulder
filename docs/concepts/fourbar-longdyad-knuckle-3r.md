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

## What was built (docs/concepts/models/fourbar-longdyad-knuckle-3r.py)

The lead's chain on the 28/50 (or 30-32/48) K dyad at the verified seats, loaded unchanged from
longstroke-slipper-knuckle-3r.py and its parents (skin, in band, near-touch audit, part pairs, knee, O20 stacks). The K
drive (hub-2 lobe, bell crank, nose / roller, flank, clock spring) is deleted. In its place:

* **law**: the closed-form spherical four-bar on ground link 1b (crank cone about u2, horn azimuth from
  A cos b + B sin b = cos c - cos rh (pc . uK), branch br), tabulated per 0.25 deg of q2 travel; the usable window is
  the longest run with real closure, horn transmission 48-132 deg (PA <= 42 where the coupler drives K), K inside its
  stops (-1.5 deg .. stop B at a1max <= bk1 + bk2 - 5.5), kit dyad margin m3e >= 5 and th(q2) monotone with rate <= 3.45.
  The seed reproduces the proposer's numbers exactly (window th 6.22-122.67, K -1.12..79.15, mu_h 59.5-129.0);
* **IK**: th -> tau on the window -> q2, K, q1, q3 in closed form; every pose is forced (K is never parked on a stop);
* **B1 switch** `b1read`: `family` (default, today's reading, the row's numbers: min(m_sub, m_eff) >= 5 on every forced
  pose) or `coupled` (m3e >= 5 only; LISTED FOR B1, never claimed);
* **metal, per pose, real size**: crank lug (3 mm Ti, 6 wide, formed to the sphere, integral with link 2 at link 2's
  layer at hub 2, O9 eye boss = MR63ZZ + 1.5 wall; turns with q2), horn lug (same, link 1a at hub K, + hl), coupler (3 x 4
  mm Ti arc, member 8, its own per-pose rotation about GH mapping the reference pin pair onto the pose's pin pair; a
  linear joggle between two pin-end floors = max(lug top + 0.15, link 1b's top + 1.0) + zcp; O9 eye columns from lug to
  coupler top sampled as the coupler's metal). Part pairs: coupler vs all four hub housings, L1a / L1b / L2 (1 mm; 0.15
  only within the eye of its own pin), both lugs, knee / pad / E; lugs vs the hubs and straps they are not part of.
  `clay=1` (coupler in link 1b's own layer, beside it) was added and measured: it collides with link 1b (121 of 160
  poses on the family best) - the coupler of a useful four-bar runs along link 1b, so it must be stacked over it.

### Spec corrections (measured, not assumed)

1. **The strap seed is not buildable as specified.** Its horn pin sits 11.3 mm off hub K's axis, so the O9 eye boss of an
   MR63ZZ eye reaches 0.7 mm INTO hub K's O20 housing below its crown (CPL-hubK -0.7 mm): every pose is lost (gap 375
   under both readings, 114-187 of 160+60 poses binding on CPL-hubK). A horn eye beside an O20 housing needs >= 15.5 mm
   lateral; rh was swept 15.5-24 deg and the four-bar re-synthesised (the proposer's law-only numbers do not transfer).
2. **The coupler is not jointed to link 1b**, so it gets the 1 mm non-adjacent clearance over link 1b, not the spec's
   0.15 running gap (+0.85 mm of stack).
3. **The judge's knee re-fit for the strap cell (lE 74.3, lc 15.7, phiE 18.4, phib -77.8) hits pad-E on 109 poses** of
   the fit bench; the lead's knee (ang_min raised to 26.88) and swept knees are used instead.
4. The proposer's four-bar seeds were synthesised by counting law-only poses ON Bench(110,360) - the verification
   sample (lesson c). Here every search runs on Bench(60,160); Bench(110,360) frozen and the held-out bench are the checks.

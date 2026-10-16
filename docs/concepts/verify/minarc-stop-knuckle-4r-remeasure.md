# minarc-stop-knuckle-4r variant B: independent re-measure (2026-10-16)

Lens: **re-measure the number**. Harness: `docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py` (the model
`docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py` imported unchanged; H1 run through the pin knee's verified
harness functions unchanged). Raw outputs: `docs/concepts/verify/minarc-remeasure/`.

Claim under test (row `docs/concepts/rows/minarc-stop-knuckle-4r.json`, `best_params`, CMA stream BD): frozen exact gap
15.42 on Bench(110,360) (score 94.4; reach 0.769, follow 1.0, in-band14 0.899, contact 0.023; near-touch 22.17;
min metal 0.05 mm), fast Bench(60,160) 6.19.

## Protocol (same as the pin knee H1 verification)

* Fit: the shape is fitted on Bench(60,160) FAST (`fit60`: the round-3 protocol; H1 = 27.20 at margin 5), or on
  Bench(110,360) FAST (`fitbig`: the polish protocol; H1 = 24.48 at margin 5 / 26.45 at margin 10). The frozen shape is
  the hub heights, knuckle hub, link profiles, E strap, stack and knee centre m. It is handed over with the same
  attribute list as `skin-normal-3r-pin-knee-polish.py frozen_on`, plus `fK`.
* Wear: Bench(110,360) EXACT (`CB_EXACT=1`), or the pin knee's disjoint held-out bench (`held`: 1154 poses, every
  fit-clip frame and workspace pose outside Bench(110,360) and Bench(60,160); Wave / Walking stay out). Fold margin from
  `CB_FOLD_MARGIN`, O20 hubs only.
* Verifier checks for B (written here, independent of the model's closed form):
  * per-joint rotation axes: link 1a about u1, 1a to 1b about uK, 1b to link 2 about u2, link 2 to member 3 about u3;
  * hub 3 centre, both knee pins and both knee rotation axes;
  * K is one-sided between its stops: dK has the sign of psiA and stays at or below stop B;
  * the J2 interior angle, re-computed from the member frames, stays inside [phi_lo, phi_hi];
  * the E boss against hub 1, hub K, hub 2, L1a and L1b (>= 1 mm) and against L2 (adjacent, 0.15 mm);
  * the knee link against the upper part of hub 3 (>= 1 mm).

  Any pose that fails is knocked out.
* Continuity rule: a flood fill over the full 1432-pose workspace grid. Edges are 2-deg slerp steps; no step of
  q1 / q2 / q3' / pin a / pin b / **dK** may exceed 10 deg; the knee branch sign stays constant. The strict seeds are the
  elevation-0 poses with **K on stop A**. Reach is scored on the taken AND connected workspace poses only.

## Results

(filled below)

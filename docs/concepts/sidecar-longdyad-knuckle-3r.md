# sidecar-longdyad-knuckle-3r

Sidecar drive on a longer K dyad. Link 1b is lengthened (bk2 42-48) and stop B is raised toward a1max 70-75. The
wide-dyad 35/45 lever is merged in as a check cell. Round 8, pick 4.

Model: `docs/concepts/models/sidecar-longdyad-knuckle-3r.py`. Sweep: `docs/concepts/sweeps/sidecar-longdyad-knuckle-3r.json`.
Row: `docs/concepts/rows/sidecar-longdyad-knuckle-3r.json`. Preview: `docs/concepts/viz/concepts/sidecar-longdyad-knuckle-3r.js`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the sidecar as what it is: a spatial RSSR loop (crank pin on link 1b, ball - rod - ball, horn on link 1a,
     whose axes are not parallel). The proposer sampled it at rest and used the small-angle gain r_h dK = La phi.
     A designer closes the loop per pose. They read off the real ratio dphi/ddK and the transmission angle over the
     taken K range, and gate both.
   - Phase the crank (a pre-rotation `gam` of the arm) so the swing straddles 90 deg of transmission. This costs
     nothing in parts.
   - Stack the crank honestly. Its pin sits in link 1b, so its boss rides on link 1b's top plus the running gap. Only
     the long arm may joggle down beside link 1b, and only where it clears the strap over the whole swing. The
     proposer's boss sat inside link 1b.
   - Ask first whether stop B binds at all before buying a1max. The judge said the lead's taken a1e stops near 54.7.
2. **Rawest material.** The bench's posed skin itself: the signed-distance grids of every bench pose, via
   `tools/concept_bench.py`. Also the per-pose K state, th, m3e and msub from the model's own IK, and the per-part
   minimum metal-to-skin distance over the taken poses. These are not the round's summaries. The held-out clips stay
   held out.
3. **Methods and tools.**
   - RSSR closure on a phi grid with continuation, per bench pose. The rod and crank are separate bodies, members 8 and 9.
   - Fold losses attributed by wall per lost workspace pose: law end (skirt / lift-off / stop B), m3e, msub, folded, mid.
   - CMA-ES on the near-touch gap, run on the farm (`tools/concept_cma.py`, 8 runs).
   - Then the frozen shape worn on Bench(110,360) exact, and held out.
4. **What other than me shows the number is right.**
   - The bench, Bench(60,160) fast for the search and Bench(110,360) exact for the frozen claim.
   - The round's adversarial verifier, which re-runs the frozen claim through its own harness.
   - Same-harness controls: the sidecar on the lead's dyad (pick 1's cell, run D) and the lead's verified 22.82.
   - A red-team pose list: the overhead poses, the poses where metal sits under 1 mm, and the transmission minimum.

## Model (what changed from the proposer's sketch, and why)

- It is built on the verified lead's module: `frontload-lobe-stopb-knuckle-3r.py`, loaded as its own copy, with its
  per-t gated lobe law. The 'lin' law is the parent's seg law with kA = kB = kK. That keeps the skirt (crest
  <= 11.5) and pressure-angle gates per t, which the parent's 'lin' fallback did not have.
- **Bell crank.** It runs on an MR63ZZ pair whose pin sits in link 1b, beside hub 2 (6 mm off the rim).
  - The boss is O10 x 6, with its underside at link 1b's top + 0.15.
  - The long arm is La 12-26 mm, 3 mm thick and 6 mm wide. It joggles down at 60 deg to link 1b's underside + zr only
    where it is >= W_LINK / 2 + 1 mm clear of link 1b's strap over the swing.
  - The short arm is s_arm 4-6 on the hub-2 rim lobe, with i_rock = La / s_arm.
- **Horn.** A lug of link 1a at hub K, radius r_h 13-22, azimuth beta from link 1b's direction, underside hl over
  K's base level.
- **Rod.** O3 Ti with M2 ball links. The ball centres sit 3 mm over the arm top and over the horn top.
  - A low-ball variant (balls under the arm) was measured. It drives the rod into the skin on 110 of 160 poses: dead.
- **Per-pose placement.** The RSSR is closed in link 1b's frame, and the rod and crank are sampled where they sit in
  each pose.
  - Gates: the loop must close, the transmission must be >= 30 deg over the taken K range, and the exact crest must
    stay <= 11.75.
  - Part pairs checked at 1 mm:
    - rod vs hub K, hub 2 and link 1b;
    - crank vs hubs 1/K/3 and links 1a/2;
    - crank boss and long arm vs hub 2;
    - horn vs link 1b (outside hub K), hub 2 and link 2;
    - knee, pad and E vs crank and horn;
    - plus the parent's ROD vs hub 1/3, links 1a/2, knee, pad and E.
- 3 active (J1, J2, J3), K slaved and never read, 0 passive translations. Same parts count as pick 1 (complexity 49.0).

## Gate (Bench(60,160) fast, lead seats, near-touch gap; fold losses split by wall)

(filled in below as measured)

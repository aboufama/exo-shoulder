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

The lead's seats are held fixed and only the dyad and drive change. "near" is the near-touch gap and "plain" the plain
gap. Wall split of the lost workspace poses:

- **law end**: th past the law's last valid point;
- **m3e**: the effective dyad margin < 5;
- **folded**: J2 on its dowel;
- **mid**: the window.

| cell (bk1 / bk2 / a1max, drive) | near | plain | reach | in-band14 | law end | m3e | folded | mid | th law max | dK taken | trans min |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lead dyad 30.05 / 37.57 / 61.72, La 20 r_h 15 beta -90 (pick 1's cell, run D) | 19.52 | 13.50 | 0.775 | 0.895 | 14 (skirt) | 8 | 8 | 3 | 121.9 | 36.9 | 36.1 |
| 30 / 38 / 63 (La 22, s_arm 4, r_lobe 7) | 22.10 | 16.08 | 0.763 | 0.893 | 13 (lift-off) | 9 | 8 | 3 | 123.8 | 37.0 | 31.7 |
| 30 / 38 / **60** | 22.10 | 16.08 | 0.763 | 0.893 | 14 (stop B) | 8 | 8 | 3 | 121.8 | 37.0 | 31.7 |
| 30 / 41 / 66 | 20.61 | 15.21 | 0.775 | 0.889 | 12 (lift-off) | 8 | 8 | 3 | 126.5 | 40.4 | **29.3** |
| 30 / 41 / **63** | 20.61 | 15.21 | 0.775 | 0.889 | 12 (stop B) | 8 | 8 | 3 | 124.9 | 40.4 | 29.3 |
| 30 / 44 / 69 | 18.54 | 14.63 | 0.775 | 0.902 | 10 (lift-off) | 8 | 8 | 3 | 129.2 | 43.5 | **26.7** |
| 30 / 44 / **66** | 18.54 | 14.63 | 0.775 | 0.902 | 11 (stop B) | 7 | 8 | 3 | 128.0 | 43.5 | 26.7 |
| 30 / 47 / 72 | 18.54 | 17.38 | 0.769 | 0.902 | 10 (lift-off) | 7 | 8 | 3 | 132.1 | 49.0 | **21.6** |
| 30 / 47 / **69** | 18.54 | 17.38 | 0.769 | 0.902 | 10 (stop B) | 7 | 8 | 3 | 131.0 | 49.0 | 21.6 |
| wide-dyad check cell 35 / 45 / 75 (La 24) | 63.70 | 39.79 | 0.700 | 0.891 | 9 (lift-off) | 9 | 8 | 3 | 132.3 | 39.1 | 27.1 |
| 30 / 44 / 66, La 20 s_arm 5 r_lobe 7.5, beta -90 | 18.54 | 12.31 | 0.788 | 0.903 | 13 (skirt) | 5 | 8 | 3 | 123.7 | 43.5 | 30.5 |
| same + crank phase gam +15 | 19.32 | 14.20 | 0.769 | 0.905 | 13 (skirt) | 5 | 8 | 3 | 123.7 | 43.5 | 37.1 |
| 30 / 47 / 72 + gam +15 (La 20) | 18.16 | 15.82 | 0.769 | 0.903 | 13 (skirt) | 4 | 8 | 3 | 123.9 | 49.0 | 33.1 |
| proposer's beta -112 at bk2 44 (La 20) | 26.29 | 13.59 | 0.781 | 0.899 | | | | | | 43.5 | 53.1 |
| balls under the arm / horn (rod at strap level - 3) | 228.14 | 203.94 | 0.381 | 0.763 | | | | | | | |

What the gate measured:

1. **Stop B never binds.** Lowering a1max by 3 deg (bk1 + bk2 - 8 instead of - 5) gives identical metrics in every
   cell. The law ends at lift-off (or at the lobe skirt) before stop B, as the judge's check 3 predicted. Raising
   a1max buys nothing by itself.
2. **The stretched poses beyond th ~132 sit behind the a2 wall, not the K dyad.** At the gam-15 seed the lost
   stretched poses are at th 100, 110, 116, 118, 118, 120, 123, 124, 127, 128, 132, 133, 134, 139, 140, 142, 143, 147,
   152 and 157. bk2 47 with its law to th 132.1 wins one of them (116). The poses at th >= 133 need
   a1e >= th - a2 + 5 = 76-100 at a2 62.2, which is beyond any a1max <= 75. The poses at th 124-132 are lost to m3e,
   because the law's K opening lags th there. That is the law shape, which the pressure-angle cap
   kK <= i_rock r_lobe / r_h bounds.
3. **The longer dyad wins 4 fold poses (30 -> 26) but only 0-2 reach poses fast.** Skin, parts and contact take back
   the rest. Near-touch improves ~1 point (19.52 -> 18.54) at equal drive. In-band rises 0.895 -> 0.902, mostly the
   longer rod's share.
4. **The real RSSR transmission degrades with the K opening.** A strap-level sidecar is a spatial RSSR whose horn
   swings dK. At gam 0 the minimum transmission angle over the taken range falls 36.1 -> 29.3 -> 26.7 -> 21.6 as bk2
   goes 37.6 -> 41 -> 44 -> 47. The small-angle gain r_h / La holds only to 0.35-0.68 of its value: it is a
   nonlinear ratio. Phasing the crank by +15 deg restores 33-37 deg and a near-constant ratio (0.75-0.79) at a cost of
   ~0.8 near-touch. Without the phase, every cell past bk2 41 fails a 30-deg transmission gate. The proposer's
   rest-only model could not see this.
5. **The wide-dyad cell (35 / 45 / 75) is dead.** Contact 0.12 (19 poses) confirms the judge's check 6 in this
   harness.
6. **Hanging the ball links under the arm and horn puts the rod into the skin** on 110 of 160 poses. The rod has to
   ride over the arm, so the sidecar's in-band floor is the crank stack plus the ball height.

GATE VERDICT: the spec's pass (a cell with fold losses <= 26, in-band >= 0.90 and min metal >= 1 mm at the near-touch
rule) is met on fold losses and in-band (bk2 44-47). It is NOT met on min metal: 0.03-0.96 mm untuned, with crank,
horn and rod ends among the < 1 mm parts. CMA (near-touch objective) runs from the passing cells, as the spec says.

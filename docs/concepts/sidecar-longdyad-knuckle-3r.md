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

## Frozen references before the CMA (fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact)

The lead's same-protocol numbers are 22.82 plain, 24.46 near-touch, held out 26.75 / 29.39 (verify/frontload-...).

| config | fast plain / near | frozen plain | score | reach | in-band14 | contact | near-touch 1 mm / 2 mm | overhead | why (fold / slide / parts / contact) | held out |
|---|---|---|---|---|---|---|---|---|---|---|
| bk 30 / 44 / 66, La 20 r_h 15 beta -90 gam 0 (dK_lim 44.0, transmission) | 12.31 / 18.54 | **20.46** | 92.56 | 0.717 | 0.903 | 0.021 | 27.23 / 49.66 | 7/28 | 84 / 8 / 2 / 8 | |
| same + gam +15 (old model, before truncation) | 14.20 / 19.32 | 21.06 | 92.34 | 0.706 | 0.905 | 0.016 | 27.35 / 50.44 | 7/28 | 82 / 8 / 10 (ROD-hub2 8) / 6 | 24.98 (near 31.66; ROD-hub2 24) |

Untuned, the strap-level sidecar plus the longer dyad buys the in-band half the planner priced. Frozen in-band is
0.903-0.905 vs 0.855, and frozen plain gains 1.8-2.4 points over the lead. Two costs come with it:

- near-touch is worse by ~2.8 (metal within 1 mm on 14 frozen poses);
- reach does not move: 0.706-0.717 vs 0.728 frozen.

## Red team (measured)

- **Rod into hub 2.** Phasing the crank (+15) to buy transmission swings the rod into hub 2's housing past dK ~42. The
  fit bench never got there, but the frozen bench lost 8 poses and held out lost 24 (ROD-hub2). The fix is in the
  model: the drive's usable range ends at the first dK where the transmission < 30 deg or the rod / crank comes
  < 1 mm to hub 2 or link 1b. Stop B sits there, and poses past it are lost on every bench. A designer would place the
  q2 dowel there; the K dyad's a1max is not the binding stop.
- **Transmission.** The longer the dyad, the larger the dK the drive must carry (dK taken 37 -> 49 for bk2 38 -> 47).
  The strap-level RSSR's transmission falls below 30 deg past bk2 ~41 at zero phase. The longdyad lever and this drive
  fight each other.
- **The ball links cannot hang under the arm.** Measured: the rod enters the skin on 110 of 160 poses.
- **Stop B never binds.** See the gate.

## Search (farm, CMA-ES on the near-touch gap, Bench(60,160) fast; 8 runs, 7248 configurations)

| run | seed | best fast (near = plain) | bk1 / bk2 / a1max | reach | in-band14 | gate (gain 2nd half / last third / top-5 spread, score pts) |
|---|---|---|---|---|---|---|
| **A1** | bk 30 / 44 / 66, La 20, gam 0 | **10.30** | 28.9 / **39.2** / 63.2 | 0.800 | 0.897 | 0.29 / 0.13 / 0.01 (passes) |
| A2 | same, other random seed | 11.60 | 29.2 / 45.5 / 61.3 | 0.800 | 0.901 | 0.00 / 0.00 / 0.00 |
| B | 30 / 47 / 70, La 22, s_arm 4 | 12.05 | 28.9 / 46.6 / 70.5 | 0.800 | 0.896 | 0.49 / 0.49 / 0.05 |
| C | wide-dyad 35 / 45 / 75 | 13.50 | 28.7 / 44.3 / 67.9 | 0.781 | 0.902 | 0.56 / 0.00 / 0.00 |
| D (control) | the lead's dyad 30.05 / 37.57 / 61.72 | 10.63 | 28.6 / **34.6** / 58.3 | 0.794 | 0.901 | 0.64 / 0.39 / 0.12 |
| E | 30 / 44 / 66, gam +15 | 11.07 | 27.4 / 39.3 / 61.8 | 0.794 | 0.896 | 0.65 / 0.51 / 0.08 |
| F | 30 / 47 / 72, gam +15 | 12.59 | 27.3 / 43.0 / 65.3 | 0.794 | 0.891 | 0.27 / 0.27 / 0.08 |
| G | 30 / 44 / 69, La 22, r_h 16 | 11.57 | 25.0 / 41.4 / 61.4 | 0.788 | 0.897 | 0.52 / 0.17 / 0.13 |

Every seed at bk2 44-47 walks back. The best basin is bk2 39-41 (A1, E, G), above the lead's 37.6 and the sidecar
control's 34.6. The convergence gate passes on the best run A1 and on the combined search: < 1 point over the second
half, < 0.5 over the last third, top 5 within 3. Every best re-evaluates identically on the final model (drive-range
truncation included; it does not bite at these configurations). The stop B dyad margin is never what ends the law:
at A1 the law ends at the lobe skirt (th 119.3), and the drive's own range at dK 43.0 (rod vs hub 2) is beyond every
taken pose (dK 38.1).

Best configuration (A1): bk1 28.94, bk2 39.24, a1max 63.18, kK 1.623 (linear law, per-t gated), r_h 14.87,
beta -86.4, La 16.55, s_arm 4.39 (i_rock 3.77), hl 3.15 (the horn on link 1a's own layer), zr 0.0 (the arm's free end
at link 1b's underside level, beside the strap), r_lobe 7.74, gam 0, smhi 16.55, smlo 5.0, az1 96.70, el1 67.59,
az2 42.20, el2 44.42, wd 67.50, wa -7.32, b3 0.345, ang_min 26.88, lc 25.69, phib -60.70.

At A1 the drive's internals hold:
- transmission >= 38.8 deg over the taken range;
- real ratio dphi/ddK 0.74-0.88 against a small-angle 0.90;
- exact lobe crest 10.16 mm, inside the O20 skirt;
- rod 26.8 mm;
- K slop from 0.05 mm of ball-link play: 0.05 / 14.9 rad = 0.19 deg.

## Claim (frozen shape fit on Bench(60,160) fast, worn on Bench(110,360) exact; self-measured, verifier pending)

| design | fast | frozen plain | score | reach | in-band14 | in-band10 | contact | near-touch 1 mm / 2 mm | min metal | overhead | why (fold / slide / parts / contact) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **A1 (this row)** | 10.30 | **18.91** | **93.12** | 0.725 | 0.897 | 0.534 | 0.011 | **20.00** / 34.03 | 0.28 mm (2 poses < 1 mm) | 8/28 | 86 / 7 / 2 (E-L2) / 4 |
| D: the same sidecar on the lead's dyad basin (bk2 34.6) | 10.63 | 19.97 | 92.74 | 0.711 | 0.902 | 0.521 | 0.011 | 21.61 / 35.91 | 0.56 mm | 8/28 | 91 / 9 / 0 / 4 |
| verified lead frontload-lobe-stopb-knuckle-3r (same protocol) | 15.68 | 22.82 | 91.70 | 0.728 | 0.855 | 0.558 | 0.011 | 24.46 / 44.08 | 0.30 mm | 8/28 | 86 / 7 / 1 / 4 |

Attribution:

- **Drive.** The strap-level sidecar puts the drive metal in band: rod 0.893, rod ends 0.962, crank 0.910, horn
  0.964, against the lead's rod and rod ends at 0 %. Frozen in-band goes 0.855 -> 0.897, which is the in-band half of
  the planner's arithmetic (planned 0.905, gap ~18.3).
- **Longer dyad.** The longdyad lever, measured against its own control D, is worth 1.06 plain / 1.61 near-touch
  frozen: 5 fold poses (91 -> 86) and reach +0.014. It does not reach the lead's reach: 0.725 vs 0.728, overhead 8/28
  both.
- **The reach half of 95 is untouched.** The poses past th ~132 need a1e >= th - a2 + 5 = 76-100 at a2 62. That is
  pick 3's lever (twist-long-a2), not this one.

## Red team of the best configuration (A1)

- **The point that pinches.**
  - The horn's ball-link socket sits 1.37 mm off hub K's housing in every pose (ROD-hubK, the tightest part pair),
    at r_h 14.87. That meets the judge's flagged cup-to-hub-K pinch at 1 mm + 0.37. A catalogued M2 socket larger
    than O7 would break it, so take r_h >= 15.5 or a smaller socket (the CAD must check).
  - knee-E 1.37 mm is inherited from the lead.
- **The metal that grazes the skin.** The near-touch CMA parks parts at the 1 mm rule's edge. On the fit bench:
  - horn 1.00 mm (4 poses < 2 mm);
  - crank arm 1.24 mm (2 poses);
  - hub 1 1.29 mm;
  - hub K 1.65 mm.

  Frozen, two workspace poses go under 1 mm: 0.28 mm at plane 45 / elev 150 / axial -45, and 0.38 mm at plane 15 /
  elev 90 / axial 30. At 2 mm the near-touch gap is 34.03, against the lead's 44.08.
- **The pose that jams.** The drive's own range ends at dK 43.0, where the rod meets hub 2's housing. Taken poses use
  at most dK 38.1 (fit) and stay inside it frozen. Stop B (the q2 dowel) belongs at that dK, not at the K dyad's
  a1max 63.2: the dyad margin is never reached.
- **The optimistic number.**
  - Fast 10.30 -> frozen 18.91 (8.6 points). That is the same drop as the lead's 15.57 -> 22.72; the fast bench's
    workspace sample under-samples axial rotation (CLAUDE.md).
  - The claim is plain 18.91. Near-touch is 20.00.
  - Held out and flood fill are below.
- **Lever attribution, not the bench.**
  - The sidecar drive is pick 1's lever. On its own (D) it gives 19.97 frozen.
  - This row's own lever, the longer link 1b, adds 1.06 frozen plain. That is just above the 1-point rule and needs
    the verifier.

## Held out (the frozen shape worn on every fit-clip frame and workspace pose in neither bench)

| design | held-out plain | near-touch 1 mm / 2 mm | reach | in-band14 | contact | overhead |
|---|---|---|---|---|---|---|
| **A1** | **22.67** | 25.75 / 37.24 | 0.690 | 0.895 | 0.012 | 18/71 |
| verified lead (same protocol) | 26.75 | 29.39 / - | 0.692 | 0.854 | 0.013 | - |
| untuned seed (gam +15, before the drive-range rule) | 24.98 | 31.66 / - | 0.672 | 0.903 | 0.022 | 13/71 |

The gain holds out of sample: +4.08 plain and +3.64 near-touch over the lead. Reach is equal to the lead's again,
so the whole gain is in-band.

## What happens next

1. **Verify A1.** Wear it through the round's verifier harness with this model file. The verifier should re-check:
   - the RSSR per-pose placement and the drive-range truncation;
   - the horn socket vs hub K's housing at the catalogued M2 socket envelope;
   - pick 1's own claim on the same drive. If pick 1's per-pose model differs, the two must agree on the drive metal.
2. **Wear pick 3's a2 / J3 re-seat (twist-long-a2) on A1's drive and dyad.** That is the reach half: the poses past th
   132 are an a2 wall. Gate it law-only first, then CMA on the near-touch gap from A1.
3. **If the 1-point rule holds against D only marginally (1.06)**, keep A1 as the drive + dyad reference and fold the
   bk2 lever into pick 1's polish as one more free parameter. It is not a separate morphology.

## Continuity (frozen wear, the round-6 verifier's flood fill)

Full grid: 18.91 with 0 poses dropped; every forced (K-open) pose is connected (99 / 99). Nearest-neighbour graph:
21.72 (10 dropped). Bench grid: 43.40. The lead on the same protocol scores full 22.82, knn 25.63, bench grid 46.09.
The fold margin follows the kit rule: msub and m3e stay >= 5 deg of th in every taken state, with physical q2
dowels, as the lead.

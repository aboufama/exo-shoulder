# kfree-o20pin-highexit-relay-4r - O20 axis-exit pin relay at the high anterolateral exit (round 401, K1)

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the pin's price where it is paid
   before building it: (a) a relay about a GH-through line is kinematically a pure re-orientation of member 3, so the
   IDEAL bound (no R4 / bar / lug metal) on the lead-quality chain is the ceiling the hardware can only lose from; read it
   first and kill on it. (b) The R4 stack is coaxial with the relay line, so its disc is rotation-invariant: the boss
   cost is set by ONE number, the line's maximum skin exit over every pose (its standoff), and the spread of that exit
   (48-79 mm) is a direct in-band price. A designer would read that spread from the posed skin per pose before drawing
   the boss, and treat the boss as a flat O20 face (not a skin-fitted cap, which no bearing stack has). (c) Steering
   stops are real only inside the least-phi solve; check that the dowels are honoured there and not clamped after.
2. **Rawest material.** The posed skin itself through the bench's signed-distance field (K.requirement / dist_many
   along the relay line and along every bar / boss / lug sample ray per pose), the fit-clip frames and workspace poses
   of Bench(60,160) / envsel / Bench(110,360) exact (held-out untouched), the lead's own fitted metal (conecut's
   CCModel, frozen), and the 2-deg slerp continuity flood on the 1432-pose envelope grid - not the kit summaries
   (kit control 60.55).
3. **Methods and tools.** The lead-quality ideal path of docs/concepts/models/insertion-cband-relay-4r.py (kfree
   lead_eval: K welded, drive stripped, knee-side samples dropped, J3 seat asserted in M1.p), the least-phi relay
   solve of armarc-relay-knuckle-4r.py with the J2 / J3 own-angle dowels inside the gate, envsel for picks and ONE
   frozen exact Bench(110,360) per claim, AR.flood_relay for the continuity rule, explicit R4 / bar / lug sampled metal
   with a 1 mm non-adjacent jam check, th margin in the ONE metric (angle(J1, J3) vs the welded window).
4. **What, other than me, shows the number is right.** The bench (envsel pick, Bench(110,360) exact frozen claim), the
   adversarial verifier (re-runs the claim and the held-out), the alignment auditor (T1-T5: near-touch, th margin,
   contact depth vs the lead's 20.24 mm), and the red-team pose list below (relayed overhead poses, the az 50-55 chest
   cliff partners at the R4 / lug, folded-wall relays, link 2 over the bar).

## The morphology (as modelled)

Scapula -> J1 (O20, GH ray, the lead's seat bvec(95.39, 67.90), a1 37.552) -> link 1 (one bent 12 x 3 Ti bar, K welded:
no knuckle, no drive) -> J2 (O20, own-angle fold dowels at the 5-deg th margin) -> link 2 (12 x 3 Ti) -> J3 (O20 on a GH ray,
b3 0) -> member 3 (hub 3's lower plate + one bent 10 x 3 Ti bar) -> **R4** (a 4th O20 v5 stack on an MR117-2RS pair, axis =
the GH-through line wdir(55, 45), placed where that line leaves the anterolateral arm: max skin exit + 2 mm over the disc)
-> lug (10 x 3 Ti, part of BOTTOM) -> BOTTOM -> arm. R4 is the counted 4th joint (4 joints, cap 4), one-sided [0, PHI]:
a clock spring holds member 3 on its zero dowel; least-phi physics with the J2 / J3 own-angle dowels inside the gate.
0 passive joints, 0 passive translations, complexity 31.75 (judge, tools/simplicity.py v2.2).

**Spec corrections made here.** (1) The line's sign: raxis(55, 45) points UP the arm into the trunk; R4 sits on the same
line where it leaves the arm, along -raxis = wdir(55, 45) (anterior, down, lateral). (2) The R4 boss is a FLAT O20 face
normal to the line at the disc's max-exit height, not a skin-fitted cap (no bearing stack has a contoured face), with its
side wall sampled. (3) The J3 seat: the spec's champion seat (77.25, -8.2) puts hub 3 in band 0.44 (median 14.7 mm) on the
lead's fitted metal; the spec's second cell, lens A's (84, -15), reads hub 3 0.79 and is the operating point.
(4) BARMIN (the J3 bar-clearance dowel) is a J3 own-angle limit, so it is folded into the J3 window [J3MIN, J3MAX].

## Measured (model docs/concepts/models/kfree-o20pin-highexit-relay-4r.py; sweep docs/concepts/sweeps/kfree-o20pin-highexit-relay-4r.json)

Lead-quality chain (conecut's own fitted metal, frozen, K welded, drive stripped, knee-side samples dropped), relay about
raxis(55, 45), sgn +1 (sgn -1: kin 253 vs 294 / 360 envsel, 45.87). Held-out untouched.

| cell | bench | gap | reach | follow | ib14 | contact | overhead | notes |
|---|---|---|---|---|---|---|---|---|
| IDEAL, J3 (77.25, -8.2), a2 64.56, PHI 75 | envsel | 21.99 | 0.781 | 0.955 | 0.844 | 0.045 | 3/26 | hub 3 ib 0.44, L2 0.78 |
| IDEAL, same | Bench(110,360) exact frozen | 18.22 | 0.806 | 0.955 | 0.844 | 0.032 | 10/28 | fails the 14.0 gate |
| **IDEAL, J3 (84, -15), a2 55.78, PHI 75** | envsel | **12.36** | 0.789 | 1.000 | 0.914 | 0.013 | 8/26 | hub 3 0.79, L2 0.82 |
| **IDEAL, same** | **Bench(110,360) exact frozen** | **10.27** | 0.817 | 1.000 | 0.914 | 0.019 | 10/28 | passes 14.0; 8 contacts / 30.1 mm |
| IDEAL steered (PHI 60, Q2MAX 100, J3 [-100, 115]) | envsel | 14.92 | 0.761 | 1.000 | 0.913 | 0.010 | 8/26 | near2 21.03 (best) |
| **HARDWARE** (R4 boss rB 86, bar to the crown, q 1, lug) | Bench(110,360) exact frozen | **56.42** | 0.756 | 0.855 | 0.687 | 0.112 | 6/28 | boss ib 0.19, bar 0.60, 39 bar-contact poses |
| HARDWARE steered, bar on R4's lower plate, q_bar 0.97 | envsel | 52.20 | 0.725 | 0.855 | 0.734 | 0.085 | 7/26 | bar ib 0.76, 29 bar-contact poses |

Ideal at (84, -15) on Bench(110,360): lost 66 / 360 ws = fold 50 (no welded solution within PHI 75), J3 stop 8, contact 8
(hub 1 2, hub 2 2, hub K 2, L2 1, contact-only 1; depth max 8.75 mm at (15, 165, -60)); relayed taken 82 (phi p90 60.8,
max 74.9 deg); th margin min 5.001 on every taken pose; near-touch 11.77 (1 mm) / 27.01 (2 mm); link 2 in band 0.823.

## Verdict: DEAD at the hardware kill (> 17.0); the ideal passes

The relay itself works: the ideal bound at the (84, -15) seat is 10.27 frozen exact, the relay crown (10.22) reproduced at
b3 0, with follow 1.0 and in-band 0.914. What kills the pin is where an O20 pin on an arm-fixed GH-through line must
sit: coaxial with the line, it has to clear the line's MAXIMUM skin exit over every pose, and the exit spans 48-78 mm as
the deltoid moves under a humerus-fixed line. The boss floats a median 18.8 mm (in band 0.19). The 86-mm bar from hub 3
(r 72) to R4 swings with member 3 by up to 75 deg, so at q 1 it floats (in band 0.60) and still meets the bunched
anterolateral deltoid on 39 Bench(110,360) poses (plane 45-80, elevation 100-145, axial -58..-90, depth <= 2.3 mm: the
fit set does not cover the relayed skin). A weightless perfect bar with a disc-only boss still bounds the hardware at
~18.8 (> 17.0), so the boss alone is the kill.

**Line scan (new knowledge, predicts beyond this row).** Over 120 GH-through lines (de 25-80, ae -45..105) on
Bench(60,160), a coaxial O20 disc at the line's max exit floats a median 14-20 mm on EVERY line (exit spread p5 -> max
20-25 mm). The best boss centre in-band is 0.60 at wdir(35, 0) (lateral, 122 mm out), 0.51 at (40, 0), and 0.26 at the
spec's 55/45. No line inside the sweep range (de 45-58, ae 40-50) rescues the boss: an axis-exit pin on any GH-through line
pays ~10-15 in-band points before its bar is counted. A relay guide must therefore ride ON the skin's moving envelope (a
rolling carriage with its own compliance) or sit where the line's exit barely moves (lateral distal, de 35-40, ae 0 -
the distal-ring lever), not at a fixed pin height.

## Red team (own best config)

- **The point that pinches:** the member-3 bar over the anterolateral deltoid, 0.05 mm min on taken poses, 42 taken poses
  < 2 mm, 39 contact poses (clip frames 42-54: plane 57-78, elev 107-143, axial ~-60). Lowering it (q 0.97, lower plate)
  raises in-band to 0.76 but keeps 29 contact poses.
- **The pose that jams:** none found - bar / boss vs hubs 1, 2, K and links 1, 2, the lug vs those + hub 3, and the lug vs the
  bar outside the stack keep >= 1 mm on every pose (0 jams).
- **The optimistic number:** the ideal 10.27 has no R4 metal at all, and its hub 3 (0.79) is fitted in-sample on
  Bench(60,160) at the (84, -15) seat; the hardware read is ONE unswept geometry (great-circle bar, no planform turn).
  Spring preload vs gravity per pose is not modelled.
- **Chest cliff partners** (the boss alone, arm-fixed, worn on EVERY Bench(110,360) pose, closing or not; scratch cliff.py):
  ae 45 / 46.5 / 50 / 55 -> 3 / 4 / 4 / 29 poses in the skin, worst at the across-body pose (150, 120, -180) -21.96 / -21.82 / -21.38 / -65.24 mm. On closing poses the
  boss keeps >= 2.4 mm (those poses are lost to the fold first), so the cliff is latent at ae 45-50; at ae 55 the line's max exit jumps to 170 mm (it meets the chest on fit poses) and
  the boss stands off the arm entirely - the measured az 50-55 cliff, 5-10 deg from the spec's line.
- **Continuity flood** (ideal, claim params, 1432-pose envelope grid): static 1173, connected 1172 (relayed 312 / 311).
- **Shoulder slip** (standing price, not scored): misfit p95 4.83 / max 5.14 mm at a 3 mm GH offset; this build assumes a
  3 mm liner.

## What next

The ideal at (84, -15) is a free lesson for every knee-less relay: J3 at lens A's seat with a2 ~56 holds hub 3 at 0.79 in
band and follow 1.0 while the relay takes 82 poses. Carry the seat to a relay guide whose metal does not stand at a
line's max exit: the distal lateral station (line de 35-40, ae 0, boss centre in band 0.51-0.60) or a carriage riding on
the arm's moving envelope with a liner.

## Audit (2026-10-19, death auditor): the death STANDS; one sub-claim corrected

**Verdict: dead, kept.** The hardware number reproduces exactly and no modelling bug or convention fix brings it near the
pre-registered kill (> 17.0) or the lead (18.28). Measured reason in one line: R4 must stand at its arm-fixed line's
maximum skin exit (rB 86 mm against an exit p50 of 65 mm), so the boss floats ~19 mm and the member-3 bar has to climb
~20 mm from hub 3 (r 66) to R4's plate. Even with the boss walls moved to contact-only and every bar contact deleted,
the bound is 25.85. Passing 17.0 would need the bar >= 0.873 in band with zero contacts; the best bar measured is 0.756
with 29 contacts.

- **Reproduction.** The audit harness, docs/concepts/verify/kfree-o20pin-highexit-relay-4r_audit.py, wraps the row's
  own `run()` and does not append to the sweep. On Bench(110,360) exact frozen it re-measures the hardware at gap
  **56.42** (reach 0.7556, follow 0.8545, ib14 0.6874, contact 0.1117, 46 contacts) and the ideal at 10.27. Both match
  the claim to 4 decimals.
- **Convergence gate.** The gate is not met. The sweep has 6 cells in order: 21.99, 45.87, 12.36, 18.22, 56.42, 52.20.
  That gives 0 score points gained over the second half, 0 over the last third, and a top-5 spread of 14.5 points. Only
  2 of the cells are hardware cells, and they mix ideal and hardware readings and two benches. CMA was not run: the farm
  is closed (balance past the budget line), and one frozen exact wear takes 33 min of wall time on this box at load
  ~25. The death therefore rests on the structural bound below, not on convergence. The free parameters CMA would tune
  (seat, PHI, stops) are already at the ideal 10.27. The hardware price sits on top of that, and only the line choice
  moves it; the agent's 120-line scan covers the line choice (best boss in band anywhere is 0.60).
- **Model read.**
  - The frames are consistent: RHG and RH differ by the constant C, so R4 is rigidly arm-fixed.
  - The relay rotation and its sign match `Zr`.
  - The bar is in the member-3 frame and the boss is coaxial, so it is invariant under the relay.
  - The lug is contact-only, like BOTTOM.
  - The jam rule matches the spec, and the fit uses Bench(60,160) only (frozen protocol; held-out untouched).
  - I found no bug that flatters or penalises the claim beyond the item below.
- **Finding 1 (strictness, corrects a sub-claim).** The boss puts its 64 side-wall samples into the in-band pool with
  its 81 disc samples. The kit's hubs (`K.hub_member`: an 81-sample disc) and the lead score only the disc in band;
  their walls and crowns are contact-only. Under the agent's convention the "weightless perfect bar" bound is 26.4 /
  18.8. That bound is not a lower bound: a sampled bar that sat in band would RAISE the pooled in-band. Read with walls
  in the pool and a perfect bar, the bound is 18.54. Read with the kit's convention (disc-only boss at 0.19-0.30 in band)
  and a perfect, contact-free bar, it is **12.35-13.48 (< 17.0)**. So the claim's "the boss alone is the kill" is
  over-stated. The kill is the boss together with the bar. Arithmetic from the row's own per-part numbers: chain 452
  samples at 0.914, ideal reach 0.8167, contact 0.0194, bar 258 samples:

  | bound (Bench(110,360) exact frozen, ideal taken set) | pooled ib14 | gap |
  |---|---|---|
  | claim: walls in pool, weightless bar | 0.738 | 26.43 |
  | claim: disc 0.26, weightless bar | 0.815 | 18.81 |
  | walls in pool, bar 100 % in band, no bar contact | 0.817 | 18.54 |
  | kit convention (disc only 0.19 / 0.30), bar 100 % in band, no bar contact | 0.868 / 0.879 | **13.48 / 12.35** |
  | kit convention, bar as measured (0.602), every bar contact deleted | 0.744 | **25.85** |
  | kit convention, best bar measured (0.756, lower plate, q 0.97), every bar contact deleted | 0.795 | **20.82** |
  | kill line 17.0 requires: bar in band >= **0.873** with 0 contacts | 0.833 | 17.0 |

- **Why the bar cannot reach 0.873.** The bar runs from hub 3's lower plate (underside r ~66) to R4's lower or crown
  plate (r 86 or 95). The skin under its R4 end sits at the line's exit (p50 65, spread 48-78), so that end floats
  14-30 mm on most poses. At q 1 the bar is still under-fit on 39 Bench(110,360) poses. The `_fitted` out_mm 15 filter
  drops rays more than 15 mm above the median: that is the bunched deltoid at plane 57-78 / elev 107-143. If those rays
  were kept, the bar would sit higher and float more, not less.
- **Stale criterion, stated.** The template's refutation test (gap within 10 of 68.93 on Bench(60,160)) is a round-3
  number. Read literally, the 56.42 hardware already "beats" it. It is superseded by round 401's pre-registered kill
  (17.0) and the lead (18.28), which are the lines this audit rules on. refuted = false.
- **Not run.** The measured disc-only and q_boss 0.95 / 0.9 variants were not run: the harness was stopped after 42 min
  with only its BASE pass done, because the box was at load ~25. The bounds above are arithmetic on measured per-part
  numbers. The variants can be run with `python3 docs/concepts/verify/kfree-o20pin-highexit-relay-4r_audit.py b110
  walls,perfectbar,nobarcontact,q:0.95 <out.json>` once the box or farm frees up.
- **What carries forward.** The ideal 10.27 at lens A's J3 seat (84, -15) with a2 ~56 stands as the agent measured it
  (flood 1172 / 1173). It is the seat every knee-less relay should start from. The pin's metal belongs where the exit
  barely moves (de 35-40, ae 0: boss 0.51-0.60), with a short bar. Lowering the lowest-complexity guide's bar float
  matters more than its line.

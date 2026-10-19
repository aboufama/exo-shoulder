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
   CMA-ES (tools/concept_cma.py, near-touch objective) from the top (as run: the Sobol pass was stopped after 6 of 101
   because 4 of 6 random knee proportions do not close at all - 275-375 - and the box shares 4 cores at load 11-24; the
   CMA started from the proposer's seed instead); the convergence gate from the sweep in time order;
   claim = the frozen search-bench shape worn on Bench(110,360) exact.
4. **What else shows the number is right.** tools/concept_bench.py (not this code); H1's verified number through the
   same base code; the verifier harness docs/concepts/verify/crest-knee-3r.py (it builds the same CK model); the
   red-team list below (lowest metal pose, the worst-conditioned takes, overhead / across / behind-the-back poses).

## What was measured (02:43-03:35 UTC, local, <= 2 niced processes, farm closed; box load 11-24 on 4 cores)

All search numbers on Bench(60,160) fast (cache 0089c747c10f); the claim is the frozen search shape worn on
Bench(110,360) EXACT and on the verifier's held-out bench (docs/concepts/verify/crest-knee-3r.py held_bench), one read
each, never selected on. Kit rules on: O20 hubs only, fold margin 5 deg in th, MR63ZZ knee (stk 6.0, ang_min >= 25.22,
physical knee window), J3 own-angle dowel stop (window fitted on the search bench and frozen), link 2 flies over member 3.

**The a1 / a2 re-solve works as specified.** The cells' arcs at b3 = 0 reproduce the spec (A 40.47 / 44.87, B 47.54 /
73.37, B2b 45.91 / 62.64, C 64.34 / 45.81, branch -1 for all). At b3 0.2 seed A's J2 seat moves bvec(36.72, 34.75) ->
(35.67, 35.48) and a2 stays 44.87 (the proposer's read had a2 43.8).

**Step 0, the three seeds at the proposer's knee (lE 97, lc 24.4, phiE 15; phib -60 / -92 / 120), flat knee:**

| seed | b3 0 / 0.2 / 0.3 plain gap | reach | ib14 | contact | limiter |
|---|---|---|---|---|---|
| A isoceles | 39.06 / 43.23 / 90.89 | 0.64 / 0.63 / 0.53 | 0.78 / 0.78 / 0.71 | 0.012-0.047 | fold 40 of 220 at every b3; E 0.66 / boss 0.52 / knee 0.61 in band |
| B posterior slot | 55.45 / 54.64 / 56.67 | 0.61-0.67 | 0.65-0.75 | 0.047-0.056 | in-band and contact (9 skin, 10-20 parts) |
| B2b | 81.82 / 83.78 / 91.41 | 0.64-0.66 | 0.56-0.58 | 0.045-0.059 | follow 0.68-0.75 (25-28 parts) |
| C pole-J1 | 93.55 / 112.87 / 137.31 | 0.40-0.55 | 0.65-0.80 | 0.23-0.28 | 37-38 skin poses, follow 0.58-0.72 |

Seed A with the joggled knee (kj=1, E boss and arm pad at their own levels) at b3 0: 35.60 / near-touch 36.85. B, B2b
and C were left at step 0 (time box, 2 processes): each is 19-58 points behind A at the same coarse knee, and the
spec's seed-B extras (routed link 2, H2 facet) are not in this model. They are NOT measured dead (no converged sweep).

**Kinematics of seed A (Bench(110,360) poses, no parts):** window [9.4, 80.3]; 264 / 360 workspace poses fold-free,
110 / 110 clip frames; the 93 lost are STRETCHED (th > 80.3: plane 105-150 across the body, |axial| > 100), 3 folded;
overhead 17 / 28 fold-free.

**Step 1, CMA-ES on seed A** (tools/concept_cma.py, lambda 8, 2 processes, near-touch objective, 11 free: a1, a2, J1
az / el, J3 wd / wa, b3, lE, lc, phiE, phib; kj = 1; 19 generations, 153 evaluations, 25 min). The sweep file holds
every configuration in order (172 incl. the probes).
- Best (isoA-g18-0): near-touch **23.05** / plain **21.85** fast; reach 0.7125, follow 0.967, ib14 0.886, ib10 0.511,
  contact 0.017.
- Params: a1 40.97, a2 **53.63**, J1 bvec(83.21, 61.03), J2 seat (re-solved) bvec(21.91, 41.63), J3 wdir(101.93,
  -0.33), b3 0.122, lE 115.0 (the model's clamp; spec box 50-110), lc 33.03, phiE 0.43, phib -70.58, kj 1 (tr_a 39.35,
  tr_b 33.06: a 6.3 mm joggle), hub faces f 53.3 / 63.0 / 64.2 mm.
- **The descent left the isoceles box at once**: every point gained came with a2 44.9 -> 53.6 (a1 stays ~41), i.e.
  the window's stretched edge 80.3 -> 94.6, and with a longer E strap (lE 97 -> 115). Hub 2 stays 0.96 in band at a2
  53.6, so the posterolateral J2 seat tolerates a longer link 2 than the proposer's frontier allowed.
- **Convergence gate NOT passed** (near-touch objective, score points, time order): gain over the second half 4.36
  (needs < 1), over the last third 1.15 (needs < 0.5), top-5 spread 1.15 (passes, < 3). Plain gap: 4.79 / 0.44. The run
  was still descending (gen 11 -> 18: 31.89 -> 23.05) when the first budget ended it.
- **Resume (03:28-03:40, isoA2, sigma 0.4 from isoA-g18-0, 10 generations, 81 evaluations):** best isoA2-g9-1
  near-touch 22.52 / plain 19.63 fast (reach 0.744, follow 1.0, ib14 **0.871**, contact 0.011; a1 39.81, a2 53.86, J1
  bvec(84.58, 62.81), lE 115 again at the clamp). Its ib14 is below the pre-registered 0.88, so the pick (and the one
  frozen read) stays isoA-g18-0. **Gate over all 253 configurations: 1.34 / 0.19 / 0.32** - the last third and the
  top-5 pass, the second half fails by 0.34 (plain 1.25 / 0.81 / 0.84). The basin is nearly closed at fast ~22.5.

**The claim read (pre-registered pick: best near-touch at ib14 >= 0.88 = isoA-g18-0), frozen shape, exact:**

| bench | gap | score | reach | follow | ib14 | ib10 | contact | overhead ws | min metal | near-touch 1 mm gap |
|---|---|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast (fit) | 21.85 | 92.05 | 0.7125 | 0.967 | 0.886 | 0.511 | 0.017 | - | - | 23.05 |
| Bench(110,360) exact frozen | **27.91** | **89.85** | 0.6611 (238/360) | 0.9818 | 0.8824 | 0.5138 | 0.0226 | 9 / 28 | 0.28 mm | 31.83 (7 poses < 1 mm) |
| held out exact frozen | 30.30 | 88.98 | 0.6528 | 0.9909 | 0.8806 | 0.5082 | 0.0364 | 8 / 26 | 0.31 mm | 31.42 (2 poses) |

Fit -> frozen loses 6.06 points (reach 0.71 -> 0.66: the fast bench's fold boundary is tuned to its 160 poses, lesson
(c) again). Against H1's verified 27.20 (cx 0) this is **0.71 points short of the pass line (< 27.20)**.

Bench(110,360) attribution (not taken: fold 82, J3 stop 29, contact 8, parts 5; parts pairs knee-E 2, L2-hub1 3):
- overhead (elev >= 140) workspace 9 / 28 taken: fold 10, J3 stop 8, contact 1; overhead clips 10 / 10; overhead
  ib14 0.919;
- across the body (plane >= 100) 50 / 91: fold 40; |axial| >= 120: 26 / 77 (fold 50);
- behind the back (plane <= -20) 40 / 54: fold 10, J3 stop 2, contact 2; rest / low 125 / 128.
- Per part in band (14 mm): hub1 0.997, hub2 0.96, hub3 0.857, E strap 0.776, boss 0.958, pad 1.0, knee 0.888, L1
  0.971, L2 0.846.
- Fold conditioning over the taken poses: min |u1 . (u2 x w)| **0.187** (H1 0.233): 9 takes below H1's worst (3 of them
  clip frames); held 0.179 (14 below, 3 clip). Min th margin 5.07 deg (held 5.67).

## Red team (own best)

- **The pose that pinches:** workspace pose 237 (plane 15, elev 165, axial -60, overhead) at 0.28 mm metal-skin, then
  281 (45 / 75 / 15) 0.37 mm, 431 (135 / 30 / -150) 0.63 mm. 7 big-bench takes sit under 1 mm: the plain 27.91 becomes
  31.83 when they count as contact.
- **The optimistic number:** the fast fit 21.85 (frozen 27.91, held 30.30). The pick sits on a parameter clamp (lE 115),
  so the true optimum wants an even longer E strap; the CMA had not converged.
- **The poses that jam:** knee-E (2) and L2-hub1 (3) part pairs; 8 contact poses on the big bench, 13 held.
- **The feel:** 9 taken poses (3 clip frames) sit below H1's conditioning floor - one arm motion split between q1 and q3
  near the stretched edge; the unpowered MVP1 tracks them, the powered product pays it in J1 / J3 torque.
- **The J3 stop:** 29 big-bench poses (8 overhead) are blocked by the frozen J3 window (width 265.1 deg from 269.1).
  Attribution read (same frozen shape, NO J3 stop, labelled diagnostic, not a claim): 28.36 (reach 0.675, contact
  0.041): of the 29, ~13 become takes (overhead 11 / 28) but 17 become part hits - E strap vs link 2 16, knee-E 3 -
  and 7 more contact. The stop is what keeps link 2 off member 3: it earns 0.45 points; widening the window buys the
  overhead only if link 2 is re-routed over the E strap there.

## Verdict

Screened, not dead: frozen exact **27.91** (score 89.85) at **cx 0**, 0 passive translations, 3 active - 0.71 points
behind H1's verified 27.20, held 30.30. Not a pass yet and not converged (gate 1.34 / 0.19 / 0.32 after the resume: one of three fails). The proposer's
isoceles cell is not where this class wants to be: the descent took a2 to 53.6. No cx-0 95 here: the fold (82 of 470
big-bench poses, 50 of them at |axial| >= 120) bounds reach, as the proposer's own frontier said.

## Next (what the loop should run)

1. Resume the CMA from isoA-g18-0 (sigma 0.5, lE box to 125 with the E strap's real length checked against the cuff
   and BOTTOM, a2 box to 60) until the gate passes; then ONE frozen + ONE held read and the verifier
   (docs/concepts/verify/crest-knee-3r-joggle.py harness builds the same CK.JogModel) with the T5 per-pose dumps
   (tools/alignment_paired.py dump) - not written here (time box).
2. The J3 stop window: re-fit it with a margin on the search bench (j3stop_margin 5-10) - see the diagnostic above.
3. Seeds B / C: knee-only CMA at their seats before any verdict (step 0 only so far).

## Verification (independent verifier, 2026-10-19 04:18-04:34 UTC, local exact, <= 2 niced processes)

Harness: `docs/concepts/verify/isoceles-shortdyad-pinknee-3r.py`. It does not run the claimant's model file. It builds the
claimed configuration (the claim read's `params_resolved`, every key, J2 seat as re-solved) in the crest-knee verifier's own
instance of the model, switched to `CK.JogModel`
(`docs/concepts/verify/crest-knee-3r.py` + `crest-knee-3r-joggle.py` -> `crest-knee-3r.py` -> `skin-normal-3r-pin-knee.py`).
The protocol is frozen shape: fit on Bench(60,160) FAST, then worn without refit on Bench(110,360) and on the disjoint
held-out bench, both CB_EXACT=1.

| read | gap | score | reach | follow | ib14 | ib10 | contact | overhead ws |
|---|---|---|---|---|---|---|---|---|
| claim, frozen exact Bench(110,360) | 27.91 | 89.85 | 0.6611 | 0.9818 | 0.8824 | 0.5138 | 0.0226 | 9/28 |
| **verifier, same bench, all checks** | **27.91** | **89.85** | 0.6611 | 0.9818 | 0.8824 | 0.5138 | 0.0226 (8 poses) | 9/28 |
| verifier, connected set (flood) | 27.90 | 89.85 | 0.6611 | 0.9818 | 0.8824 | | 0.0226 | |
| verifier, held out, all checks | 30.30 | 88.98 | 0.6528 | 0.9909 | 0.8806 | 0.5082 | 0.0364 (13 poses) | 8/26 |
| champion spherical 3R, same bench + protocol (re-run here, fold margin 5) | 64.93 | 76.39 | 0.7278 | 0.9182 | 0.565 | 0.3504 | 0.1103 | |

Checks, all on the corrected taken set:

- **DOF.** 3 active O20 hubs (rad 10 at all three, ruling 2). The cuff knee is 2 MR63ZZ pins, stack 6, outside the count
  (decision 5). The knee is set by the closure: knee angle 105.1-112.8 deg taken, inside [25.22, 154.78]. No
  undetermined coordinate, 0 passive translations, no springs, loops, gears, pulleys or cables.
- **Seats.** The J2 re-solve is exact: angle(u1, u2) = 40.9681 = a1 and angle(u2, u3) = 53.6261 = a2, on branch -1 as
  claimed. J1 sits at bvec(83.2, 61.0) with anterior -0.057, legal under ruling 4 (az -110..135, el -20..90, anterior
  <= 0.20). Hub centres sit 53.3 / 63.0 / 64.2 mm from GH.
- **Pin-knee extra checks.** Independent 3D closure max 0.023 deg. Knee vs hub 3 upper: 0 bad. E boss vs hubs / links: 0 bad.
  The arm pad sits 129.6 mm from GH on the humerus, so the 115 mm E strap ends on the cuff.
- **Crest checks.** J3 window [269.13, +265.13]: 0 taken poses outside it, min margin 4.85 bench / 1.0 held. th fold
  margin min 5.072 bench / 5.667 held (rule 5). Radial drift 0. Closure residual max 0.015 deg.
- **Joggle checks.** Step 6.29 mm over a 21.0 mm ramp (16.7 deg). A bent 3 mm bar with R15 can rise 7.57 mm, so it is
  buildable bent. Knee, pad and boss samples follow the joggle law exactly (0.0 mm error). Every knee slice clears hubs
  1 / 2 and L1 / L2 by >= 54 mm, and the pad clears the boss and strap by >= 19.7 mm. 0 bad poses.
  **Removed by all checks: 0 poses** (bench and held).
- **Continuity flood.** Full 1432-pose workspace grid, J3 window and knee branch as walls, 2-deg slerp edges, no step
  > 10 deg. 983 kinematic nodes, 982 connected, 1 island at (-15, 105, 45), which is not a bench pose. 811 / 811 edges
  passed. **0 bench or held poses dropped**: connected = static.
- **Per-pose dumps (T5 rule).** `docs/alignment/remeasure/isoceles-shortdyad-pinknee-3r_v_bench_perpose.json` recomputes
  27.90 and `..._v_held_perpose.json` recomputes 30.30. Both are within +-0.05 of the claim.

Red team (this verifier):

- **Contact depth (T5).** Bench: 8 contacts, depth sum 27.47 mm. Held: 13 contacts, depth sum 51.06 mm. The lead's T5
  is 20.24 mm. Attribution by part (`..._v_contact_parts.json`):
  - The shallow contacts (0.1-3.5 mm, elev 60-90) are hub 2's wall or crown on the posterior shoulder.
  - The deep ones are the cuff knee + arm pad pressed into the torso with the arm across the body, low, in full internal
    rotation: bench pose 405 (plane 120, elev 30, axial -180) at -14.35 mm; held poses 378 / 431 / 454 (plane 105-150,
    elev 30, axial -165) at -14.4 / -12.0 / -9.1 mm.
  - The gap already charges them as contact. They are not a refutation, but that sector would be felt hard.
- **Knee-over-strap stack.** The joggled knee rides over the E strap at pin a with a constant 0.25 mm gap at every
  taken pose (bench and held; rule 0.15). That makes it a joint-stack running gap, set by a shim, not a pose-dependent
  near miss. The tolerance probe shows a stack error of 0.1 mm closes it at 145 of 346 taken poses, and 0.2 mm at all
  of them (`..._v_tolprobe_bench.json`, `..._v_tolprobe_held.json`). The CAD must hold this stack with a thrust washer,
  as at every hub.
- **Near touch** (reported, not a gate): 1 mm near-touch gap 31.83 bench / 31.42 held. Minimum 0.28 mm, at overhead
  pose 237 (15 / 165 / -60), on a crown or wall.
- **Conditioning.** min |u1.(u2 x w)| is 0.187 bench / 0.179 held, with 9 / 14 takes below H1's 0.233. The fold margin
  in th holds at >= 5.07 deg, which is the user's rule, so this is a feel / torque watch item for the powered product.
- **Selection.** The pre-registered rule (best near-touch at ib14 >= 0.88 over the 253-config sweep) does pick
  isoA-g18-0 (near-touch 23.05). The better-scoring isoA2-g9-1 (19.63 plain) has ib14 0.871 and was correctly not
  picked. One held read.

**Verdict: VERIFIED at 27.91 (score 89.85), held 30.30. Not refuted** (champion 64.93 on the same bench and checks, re-run
here). All checks remove 0 poses and the flood drops 0. At cx 0 it is the second verified cx-0 design, 0.71 behind H1's 27.20
and ahead of crest-knee 31.50. It is not a leader (the lead is conecut-knee-knuckle-3r at 18.28) and not a 95 (95 needs
gap <= 13.75). Its limiter is still the J2 fold: 82 ws poses, 10 of them overhead. The J3 stop costs 29 more.

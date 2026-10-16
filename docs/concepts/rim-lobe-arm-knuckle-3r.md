# rim-lobe-arm-knuckle-3r - direct-pair knuckle (K's follower arm on a link-2 lobe plate)

Round 7, lens direct-drive-knuckle (a), groove-arm-knuckle-3r merged in as the 'groove' embodiment.
Model: docs/concepts/models/rim-lobe-arm-knuckle-3r.py (on the verified winner geneva-tail-knuckle-pinknee-3r, rod
embodiment, with its rocker / pushrod / rod ends / horn deleted and replaced by a lug on link 1a, a follower and a
cam plate on link 2).

## Deeper-version prompt (answered before modelling, 2026-10-16 15:45 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the LAYER STACK as the design,
   not the cam law. The pair (lug on link 1a, plate on link 2) lives between two hub stacks that already put link 1b
   at hub 2's floor and link 2 one layer up; whichever of lug / roller / plate is stacked on top of the other two sits
   ~2 layers (6-7 mm) above the floor and leaves the 2-14 mm band - that is exactly why the rod drive was 0 % in band.
   So (a) put the lug at the BOTTOM layer, skin-fitted like a link and run beside link 1b (a0 off the K-J2 line), with
   the roller standing up from it into link 2's own layer, so the plate is just link 2's ring widened - no extra layer
   at all; (b) keep the spec's 'lug above the plate' as the control; (c) compute the pair exactly on the sphere
   (pressure angle from the relative velocity, pitch curvature, undercut / lap check over every q2 the bench visits),
   not with tan(pa) = kK r_horn / r_lobe; (d) size the K spring for force closure before claiming the roller.
2. **Rawest material.** The posed skin itself (the signed-distance cache behind tools/concept_bench.py: every metal
   sample of lug / roller / plate is sphere-traced against the skin of every bench pose, not a digested clearance
   map), the fit clips at 10 fps (continuity of q1, q2, q3, K and both knee pins), the 160 / 360 workspace poses, and
   the verified winner's own per-part in-band numbers (verify/geneva-tail-knuckle-pinknee-3r_corr_bench_frozen.json)
   as the baseline the drive must beat part by part.
3. **Methods and tools.** tools/concept_bench.py Bench(60,160) fast cache for the search, CB_EXACT=1 Bench(110,360)
   frozen for the claim; the winner's model (kit-rule B, phys q2 stop, near-touch objective, VModel checks) loaded as a
   module copy; exact spherical cam synthesis (pitch curve C(t) = R(u2,-q2(t)) R(uK,-dK(t)) p_arm in link 2's frame);
   the cloud CPU farm (tools/cloud_run.py) for the coarse sweep and CMA (tools/concept_cma.py) on the near-touch gap.
4. **What other than me shows the number is right.** The bench (an outside judge), the adversarial verifier
   (docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py protocol: frozen exact, held out, continuity flood fill),
   and a red-team pose list: rest, overhead (elev >= 140), across-the-body, behind-the-back, the law's last valid t
   (stop B), the onset (roller touching the lobe start), and the plate's sweep over hub K and link 1b at every q2.

## Verdict: DEAD at its kill gate - converged best fast near-touch 20.57 against the gate 15.5 (rod winner 16.53, law-only bound 14.38)

Bench(60,160) fast, near-touch objective, the verified winner's chain (seats, pin knee, capK 6) with the rocker /
pushrod / rod ends / horn deleted and the direct pair modelled as real metal. 1591 configurations (sweeps json):
1 seed + 44 local + farm LHS 224 + two farm CMA-ES runs (657 + 665 evaluations, $0.07 in all).

| embodiment / layering | configs | best near-touch | reach | in band 14 | contact | what sets it |
|---|---|---|---|---|---|---|
| spec seed (a0 2, L_arm 23.5, kK 0.6, smhi 28) | 1 | 135.63 | 0.244 | 0.969 | 0 | pressure angle 90 deg at the onset: the drive never engages (idle) |
| **roller, lug LOW, CMA run b (converged)** | 665 | **20.57** (plain 20.57) | 0.731 | 0.863 | 0 | reach (fold 39 of 160 ws, overhead 2/12) + the plate 8 % in band |
| roller, lug LOW, CMA run a (other basin, converged) | 657 | 24.94 | - | - | - | a0 3.4: a near-dead pair, short law |
| roller, lug LOW, LHS / local (no plate cap) | 132 | 26.05 | 0.694 | 0.863 | 0.018 | the plate floats over a far pose (148 mm, 0 % in band) |
| roller, lug HIGH (spec: a layer over the plate) | 63 | 26.97 | 0.694 | 0.854 | 0.018 | lug a third layer, 0 % in band; or LUG-PLATE on 71-125 poses |
| roller, lug LOW, a0 20 (lug along link 1b) | 12 | 105-157 | 0.19-0.41 | 0.83-0.90 | 0-0.03 | LUG-L1b on 87-138 of 160 poses |
| groove (dwell + rise, no spring) | 58 | 95.51 | - | - | - | the 93-deg dwell flange sweeps the body (plate need 177 mm) |

**Best configuration** (roller, lug low): kK 0.6515, smhi 26.57, a1max 56.38, bk1 28.59, bk2 37.14, L_arm 27.99,
a0 26.66, rho_max 31.05, rr 2.5, capK 6. Law: onset th 70.7, dK up to 25.9 deg (ends at rho_max; th_max 101.2),
pressure angle <= 32.2, rate <= 1.44, min convex pitch radius 11.7 mm (no undercut), lap check = rr (contact only).
Plate: 29-deg sector, pitch 19.1-31.0 mm off u2, flat at link 2's ring level (63.4 mm along u2). Per part in band:
lug 0.63 (median 10.2 mm), plate 0.08 (18.3 mm), hub 3 0.69, L2 0.80, hub K 0.98. Stretched poses driven 111,
folded 0. Min metal 1.05 mm. Complexity 35.25 (tools/simplicity.py, full record) against the rod's 46.75.

**Convergence gate (CMA run b, the best basin): gain over the second half 0.11 score points (< 1), over the last
third 0.09 (< 0.5), top-5 spread 0.02 (< 3): passes.** Run a converged in a worse basin (24.94; gains 0.0 / 0.0).

**Frozen exact Bench(110,360)** (shape fitted on Bench(60,160), worn frozen, farm job,
docs/concepts/verify/rim-lobe-arm-knuckle-3r_best_big_frozen.json): **plain 26.21 (score 90.47), near-touch 27.89**,
reach 0.681, follow 1.0, in band 0.863 (10 mm: 0.607), contact 0.006, min metal 0.45 mm, overhead 8/28; lost: fold 106,
knee window 7, contact 2. Same protocol, the rod winner: 23.37 plain / 25.01 near-touch (verified 23.57): the direct
pair is 2.8 points worse frozen. Self-measured, not verified (the design is dead at its gate).

### Why, measured (in the order a designer meets them)

1. **The spec's geometry cannot drive.** With the follower arm aimed at J2 (a0 ~ 2 deg) the follower moves tangent to
   the cam's own rotation, so the relative velocity is parallel to the follower velocity and the pressure angle is
   90 deg at the onset (exact spherical pair, `law()`): the seed is an idle drive (135.63). A usable pair needs the
   arm 20-35 deg off the K-J2 line (pa 6-40 deg measured; the optimum sits at a0 26.7), which puts the follower
   19 mm from u2 (not 14.3) and lets the law carry it outward by L_arm x dK (28 mm x 0.45 rad = 12 mm) to 31 mm.
   tan(pa) = kK r_horn / r_lobe (the rocker formula) does not describe a direct arm-on-lobe pair.
2. **The lobe sits where the skin is either too high or too low for a flat plate.** Per radius from u2 (plane need,
   max over the kept poses): 10-25 mm 56-60 mm (under link 2's ring level 63.4), 25-30 mm 66.1, 30-35 mm 73.6. Past
   ~27 mm the plate must rise off the ring (and the fit floats it); inside, it stays at the ring level, which is
   18 mm over the skin there (8 % in band). The optimiser caps the follower at 31 mm (rho_max): dK 25.9 instead of
   the judge's 36, so reach 0.731 instead of 0.756 law-only.
3. **The lug must leave hub K on its own azimuth.** Lug and link 1b share the K -> J2 corridor: at a0 <= 20 the lug is in
   link 1b's layer (87-138 of 160 poses lost to LUG-L1b); stacked over the plate (the spec's layering) it is a third
   layer (0 % in band, or LUG-PLATE). At a0 26.7 it clears link 1b by 1.4 mm and link 2 by 1.1 mm.
4. **Groove**: the dwell flange (93-deg sector, both walls) sweeps the body over the whole state-A q2 range: plate need
   177 mm; best 95.51.

So the direct pair costs 6.2 points over its own law-only bound (14.38 -> 20.57) and is 4.0 points WORSE than the rod
drive it replaces (16.53), although it is simpler (35.25 vs 46.75): the pair must sit where the cam radius is large
(pressure angle), and the law it can carry inside the skin's 27-mm ring is shorter than the rod's.

### Red team (of my own best number)

- Closest drive metal to the skin over the 177 taken poses: the lug at 2.05 mm (workspace poses at 75-90 deg
  elevation, e.g. bench poses 136, 161); the plate 2.6 mm; the roller 12 mm. No skin contact, no near-touch loss.
- Tightest part pairs: LUG-L2 1.1 mm, LUG-L1b 1.4, LUG-PLATE 1.6, PL-hubK 2.8 (all >= 1 mm; LUG-L2 has 0.1 mm of
  tolerance budget - a real jam risk at the stretched end).
- Overhead (elev >= 140): 2 of 12 taken (fold 8, knee window 2). The design does not move the overhead problem.
- The roller axis is fixed in link 1a, K's axis is 37 deg from J2's: the roller cannot stay parallel to the plate's
  edge, so a crowned roller with point contact (Hertz stress on a 2.5-mm roller) is needed.
- Force closure (K clock spring vs gravity + cuff load) was NOT measured (moot after the gate).
- The pressure angle uses the pitch level r_law 62 mm; the plate sits at 63.4-65 (< 1 deg effect).
- The 26.05 LHS figure is a floating plate (a pose whose plate ray runs through the body kept the plate at 148 mm) -
  replaced by the CMA's 20.57, whose plate sits at its ring level.

### New knowledge (predicts beyond this morphology)

- **A direct cam pair between two O20 stacks ~38 deg apart is pressure-angle bound**: the follower must sit >= ~19 mm
  from the cam axis with its arm >= 20 deg off the line of centres, and the lobe grows outward by L_arm x dK. On this
  body the skin under hub 2's surroundings is low inside ~25 mm and high beyond 27 mm, so a flat plate there is
  either 18 mm over the skin (8 % in band) or lifted off the ring: a swept disc costs more in-band than a strap of the
  same area. Rotating the drive into a strap (rocker + rod) or putting the big part on the member that moves least
  (k-rim stub) is the way to carry a slaved-K law.
- **A lug that runs along an existing link** (link 1a's lug along link 1b) either stacks a layer (out of band) or
  collides; a slaved-K follower must leave hub K at >= ~25 deg from link 1b.
- **The low-gain law needs dK >= ~30 deg to beat the rod**: at dK 25.9 (rho_max-capped) reach is 0.731, at 36 (law-only,
  no metal) 0.756.

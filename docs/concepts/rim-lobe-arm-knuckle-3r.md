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

## Verdict: DEAD at its kill gate (fast near-touch 26.05 against the gate 15.5; the judge's law-only bound 14.38)

Bench(60,160) fast, near-touch objective, the verified winner's chain (seats, K arcs bk1 31.25 / bk2 37.99, pin knee,
capK 6) with the rocker / pushrod / rod ends / horn deleted and the direct pair modelled as real metal.

| embodiment / layering | configs | best near-touch | reach | in band 14 | contact | what sets it |
|---|---|---|---|---|---|---|
| spec seed (a0 2, L_arm 23.5, kK 0.6, smhi 28) | 1 | 135.63 | 0.244 | 0.969 | 0 | pressure angle 90 deg at the onset: the drive never engages (idle) |
| roller, lug LOW (bottom layer), rho_max 27 | 112 + 20 local | **26.05** | 0.694 | 0.863 | 0.018 | plate + lug 0 % in band (plate 148 mm off GH: it floats over the body) |
| roller, lug HIGH (spec: a layer over the plate) | 56 + 7 local | 26.97 | 0.694 | 0.854 | 0.018 | the same, one layer higher |
| roller, lug LOW, plate held at its ring level (rho_max 24-28) | 6 local | 105.6-157 | 0.19-0.40 | 0.85-0.90 | 0 | the lug hits link 1b (LUG-L1b on 87-138 of 160 poses) |
| groove (dwell + rise, no spring) | 56 farm + 2 local | 95.51 | - | - | - | the dwell flange (93 deg sector) sweeps over the body: plate need 177 mm |

(The rows are in docs/concepts/sweeps/rim-lobe-arm-knuckle-3r.json; farm LHS 224 configs, $0.02; CMA runs below.)

### Why, measured (in the order a designer meets them)

1. **The spec's geometry cannot drive.** With the follower arm aimed at J2 (a0 ~ 2 deg) the follower moves tangent to
   the cam's own rotation, so the relative velocity is parallel to the follower velocity and the pressure angle is
   90 deg at the onset (exact spherical pair, `law()`): the seed is an idle drive (135.63). The low-pressure-angle
   pair needs the arm ~15-35 deg off the K-J2 line (pa 6-40 deg measured), which puts the follower 18-30 mm from u2
   (not 14.3) and lets the low-gain law carry it out to 27-46 mm from u2 by its end (spec: 24.1 / outer 26.6).
   tan(pa) = kK r_horn / r_lobe (the rocker formula) does not describe a direct arm-on-lobe pair.
2. **The lobe's outer end sits over high skin.** Per radius from u2 (plate plane need, max over the kept poses):
   10-25 mm 56-60 mm (= at or under link 2's ring level 63.4), 25-30 mm 66.1, 30-35 mm 73.6. A flat wire-EDM plate is set
   by its outer end, so it rides 10-25 mm above hub 2's level and is 0-2 % in band; the lug that carries the roller
   into the plate's layer follows it (0-32 % in band). Capping the follower's radius (rho_max) keeps the plate at the
   ring level but shortens the law (dK 15-21 deg vs 36), and then the lug -
3. **- collides with link 1b.** Lug and link 1b share the K -> J2 corridor. Below the plate the lug is in link 1b's
   layer (87-138 of 160 poses lost to LUG-L1b); above it (the spec's layering) it is a third layer (0 % in band).
4. **Groove**: the dwell flange (93 deg sector, both walls) sweeps the body over the whole state-A q2 range: plate need
   177 mm; best 95.51.

So the drive metal costs >= 11.7 points over the law-only bound (14.38 -> 26.05), against the rod's 4.74: the direct
pair is WORSE than the rocker + pushrod it replaces, not better, because the pair must sit where the cam radius is
large (pressure angle) and a cam plate is a swept disc, not a strap. Complexity priced from the full record
(tools/simplicity.py): 35.25 (roller) - it would have been simpler, but not at a usable score.

### Red team (of my own best number)

- The 26.05 config is NOT buildable as fitted: the greedy kept a pose whose plate ray runs ~90 mm through the body, so
  the plate level went to 148.5 mm (a part flying 90 mm off the skin). The number is optimistic as a design; it is the
  ceiling of "drive metal out of the way" (it equals the plate counted at 0 % in band), and it still misses the gate by
  10.5 points.
- The pressure angle is computed at r_law 62 mm; the real plate level differs by a few mm (< 1 deg effect).
- The roller axis cannot stay parallel to u2 (K's axis is 38 deg from J2's): a crowned roller / point contact (the
  winner's note 5 applies).
- Force closure (K spring vs cuff load) was NOT measured: moot after the gate.
- What would revive it: a lobe that stays inside 25 mm of u2 at pa <= 45 deg needs kK * L_arm small and the arm near
  perpendicular to the follower radius, i.e. K much closer to J2 (bk2 << 35) - which is the k-rim-lobe-stub geometry
  (pick 2), not this one.

### New knowledge (predicts beyond this morphology)

- **A cam pair between two O20 stacks 38 deg apart is pressure-angle bound to a follower radius >= ~18 mm and, at
  low gain, a lobe out to >= 27 mm from the cam axis.** Any cam on hub 2 driving K directly sweeps a disc of that
  radius around J2, and the skin under the outer 25-35 mm of that disc is 6-14 mm higher than under the hub (this
  chain, these seats). A swept disc costs far more in-band than a strap of the same area: rotate the drive into a
  strap (rocker + rod, as the winner does) or put the big part on the member that moves least (k-rim stub).
- **Lugs that run along an existing link** (here link 1a's lug along link 1b) either stack a layer (out of band) or
  collide; a slaved-K drive must leave hub K on a different azimuth from link 1b.

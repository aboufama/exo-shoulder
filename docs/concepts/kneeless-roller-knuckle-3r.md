# kneeless-roller-knuckle-3r - the roller-flank knuckle with J3 on a GH ray and the pin knee deleted

Round 9, lens 3 (simplest drive). Status: **screened, converged (5914 configs); a complexity Pareto point, not a lead change; NOT verified.**

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.** (a) Prove the knee is dead before
   deleting it: with J1, J2 and J3 all on GH rays the chain is a pure spherical 3R about GH, member 3 rotates with the
   arm and the drift s = Q^T t3 is identically 0, so the knee angle must be constant to machine precision on every pose
   of every bench - assert it (ptp < 0.5 deg), never assume it. (b) Do not just glue the old knee plate on: the knee
   link sat one pin stack (tp + RUN ~ 2.5 mm) above the boss / pad; as one bracket it drops to the boss level, so the
   whole arm-end bracket gets a fresh height fit (it can sit lower = more in band 2-10, or meet the skin). (c) Re-seat
   J3 freely: with b3 0 the J3 seat (wd, wa) and the bracket outline (lE, phiE, lc, phib) are the only things that move
   hub 3 off the deltoid; the planform may even shorten the bracket to a single strap (lc -> small). (d) Count the
   real cost of rigid closure: the scapula handler's tracking error and the humeral-head translation that the knee used
   to absorb now go into the cuff liner - red-team it with a GH offset of 3 / 5 / 10 mm instead of trusting the bench.
2. **The rawest material.** The posed skin itself (pipeline/avg body + bench signed-distance grids in
   .cache/concept_bench, the exact libigl path for claims), the motion clips (data/raw split, Bench(60,160) fit clips and
   the Bench(110,360) / held-out poses), the skin-motion map pipeline/conformal/analysis/skin_motion_map_14.json for
   where hub 3 can sit on the lateral arm, and the proximity atlas data (docs/research/proximity_atlas.md tables) for the
   hub-3 obliquity ceiling on a GH ray - not the round summaries.
3. **Methods and tools.** The verified roller-flank model loaded unchanged (spherical cam synthesis per 0.25 deg of K,
   pressure angles, lift-off, cusp, arm / roller / lug clearances, drive-range truncation, kit fold rule, O20 stacks)
   via the round-9 wrapper (PA <= 43, roller stub head, 2 mm near-touch objective, workspace in-band); this file only
   forces b3 0, turns the knee into one rigid bracket and asserts it never moves. Search: coarse farm sweep, then
   CMA-ES (tools/concept_cma.py) on the farm from the top configs until the convergence gate passes; frozen exact
   Bench(110,360), held out, flood fill, per-part split, tools/simplicity.py.
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py) is the judge; the frozen
   exact Bench(110,360) wear of the fit shape is the claim protocol; an adversarial verifier re-runs it; the red-team pose
   list (overhead axial -135 / 0, hub 3 over the deltoid crest, bracket into the chest at extreme internal rotation,
   GH offset 3 / 5 / 10 mm) and the alignment audit against the lead (sidecar-longdyad-knuckle-3r) look for the
   optimistic number.

## Mechanism (as modelled)

scapula handler -> J1 (ACTIVE R, O20, acromion top, GH ray) -> link 1a (with the conjugate flank lug) -> K (PASSIVE R,
O20 + clock-spring cap, stop A / drive stop B, slaved, never read) -> link 1b -> J2 (ACTIVE R, O20, GH ray) -> link 2 ->
J3 (ACTIVE R, O20, **axis on a GH ray, b3 0**) -> **one rigid Ti bracket** (hub 3's lower plate + the E run + the former
knee link, 3 mm Ti-6Al-4V, 8-10 wide, bent from line / arc sketches) -> arm pad on BOTTOM -> arm.
Drive loop (unchanged from the verified roller-flank row): hub-2 rim lobe -> bell crank (MR63ZZ pair on link 1b) ->
bent long arm -> MR63ZZ roller -> conjugate spherical flank on link 1a; K's clock spring keeps both cam pairs closed.
3 active DOF, passive rotations K + crank + roller (all determined: K by the lobe / flank, the crank by the lobe, the
roller spins), 0 passive translations, 0 sensed passive coordinates (the pin knee's two encoders are gone).

**Why the knee carries nothing (exact; asserted on every bench).** J1, J2 (b1 = b2 = 0) and J3 (b3 = 0) all lie on GH
rays: c3 = 0, so t3 = R12 (c3 - R3 c3) = 0 and the drift s = Q^T t3 = 0 on every pose. Member 3 is rigid with the arm;
the planar knee closure at s = 0 is its rest configuration. The model asserts ptp(knee angle) < 0.5 deg and |s| < 0.05 mm
on every pose (measured: 0.0000 deg, 0.0000 mm, c3 = 0.00000 mm on the seed, every coarse config and every CMA config).

**Model** (`docs/concepts/models/kneeless-roller-knuckle-3r.py`): the round-9 roller wrapper
(roller-longdyad-knuckle-3r.py: PA <= 43, the roller's stub head as metal, 2 mm near-touch objective, workspace in-band,
per-part contact split) and under it the verified roller-flank model, loaded unchanged; this file forces b3 0, drops the
knee window (a rigid bracket has no knee angle), re-samples the former knee link at the bracket level tr (it no longer
sits one pin stack - tp + RUN ~ 2.5 mm - above the boss / pad; re-fitted against the skin), 3 mm thick, rebuilds its
contact-only edges / top and its part-pair box at that level, drops knee-vs-E and pad-vs-E (one body), keeps the
bracket >= 0.15 mm off hub 3's cylinder (link 2's half turns over it) and >= 1 mm off every other part. Spec deviation
(stated): the 'lead' chain of the parent would force the frontload dyad; chain 'free' with bk2 34-48 is used so the
roller row's own dyad (27.7 / 35.7) is the start point. PA_MAX is the round-9 43 deg (not the verified row's 45): the
seed's flank then ends at dK 49.0 (pressure_horn) instead of 56.2.

## Result (best configuration = CMA stream A2, the fast-bench best)

| bench | plain gap | 1 mm | 2 mm | reach | follow | in-band 14 | in-band 10 | contact | overhead taken | min metal |
|---|---|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast (fit) | 16.70 | 17.84 | 20.02 | 0.775 | 1.0 | 0.890 | 0.554 | 0.032 | 1/12 | 0.72 mm |
| **Bench(110,360) exact, frozen** | **21.07** (score 92.34) | 23.23 | **32.25** | 0.725 | 1.0 | 0.891 | 0.558 | 0.026 | 7/28 | 0.01 mm |
| held out, frozen | 24.59 | 27.20 | 36.06 | 0.694 | 1.0 | 0.889 | 0.558 | 0.029 | 16/71 | 0.11 mm |
| lead sidecar-longdyad (verified) | 18.91 | 20.00 | 34.03 | 0.725 | 1.0 | 0.897 | 0.534 | 0.011 | 8/28 | 0.28 mm |
| roller-flank (verified, with knee) | 20.08 | 21.17 | 46.82 | 0.722 | 1.0 | 0.890 | 0.513 | 0.013 | 8/28 | 0.32 mm |

Flood fill (continuity): full 21.07 (0 dropped), knn 23.35 (8 dropped). Min fold margin over taken poses (th, kit
metric) 5.14 deg. Drive: dK_lim 46.8 (pressure_horn at PA 43), taken PA crank 9.3 / horn 42.5 (0.5 deg inside the
round-9 cushion), flank radius >= 4.3, arm vs hub K 1.53 mm, roller vs hub K 3.08 mm. Knee assertion: ptp 0.000 deg,
|s| 0.000 mm on every pose of every bench. Workspace in-band (unscored, fit bench): 0.839 all / 0.814 at elevation
90-140 (the lead, same formula, fit bench: 0.837 / 0.762; the planner's 0.874 / 0.841 bar is not met).
Frozen wear of the other stream bests: C2 22.06 (2 mm 32.72, held out 24.89), B2 21.75 (hub 3 0.734 in band, 2 mm 35.64),
D2 22.37, round-1 C 21.53 (2 mm 37.07, held out 25.55). The fast-to-frozen penalty is only +3.6 to +4.4 here (the
knee family usually pays 8.4-9.0).

**Lost poses, frozen (99 of 360): fold 86, contact 10, parts 3.** Overhead 7/28 (fold 15, contact 4, parts 2).
Red team (frozen exact, per-part minima at every metal-lost pose, `redteam` mode): 9 of the 13 metal-lost poses are
**hub 2's crown** sinking into the raised deltoid / trapezius in scapular-plane abduction 90-165 (plane -15..15:
-0.7 to -23 mm), 2 the flank lug (elev 165, axial -60: -4.8 / -12.0 mm), 2 link 2 (behind the body / plane 60 elev 150).
The bracket and hub 3 never touch the skin; the lowest taken pose (plane 90, elev 135, axial -90) has hub 2's crown edge
at 0.08 mm. Named poses: overhead axial -90 taken (hub 3 / bracket at 1.7 mm), overhead axial -15 and -120, across the
body with extreme internal rotation, behind the back, abduction 90 and extreme external rotation are all FOLD (the dyad),
not metal.

**Per-part in-band (frozen, 2-14 mm):** hub 3 0.505 (median 13.9 mm: the GH-ray hub sits 28.6 deg oblique to the
deltoid at wd 74 - the obliquity law, hub 3 0.64 at 30 deg with a knee), L2 ~0.74, crank ~0.82; every other part >= 0.9.
The bracket itself (E run + former knee link + pad) is 0.92-1.0 in band: lowering the old knee link by the pin stack
(~2.4 mm) costs nothing.

**GH-offset red team (the misfit the knee used to absorb; `redteam_gh`, 470 poses x 26 directions, worst direction per
pose):** with the true GH 3 mm off the chain's centre the bracket-to-arm misfit is median 3.4 / p90 4.8 / max 5.9 mm (39 %
of poses within a 3 mm liner); 5 mm: 5.7 / 8.0 / 9.8 (18 %); 10 mm: 11.3 / 16.1 / 19.7 (8 %). One cuff slide along the
humerus barely helps (40 / 19 / 8 %): the misfit is mostly across the arm. For comparison, a planar knee in hub 3's plane
would leave only the component along hub 3's axis: 2.3 / max 5.5 mm at 3 mm (67 % within the liner). So deleting the
knee roughly multiplies the liner's misalignment load by 1.5 at the median - the bench cannot see this; it needs the
user's tracking-error number (scapula handler 5-7 deg below 100-120 deg elevation, humeral head 1-3 mm) before CAD.

## Convergence gate (binding) - PASSED

5914 configurations: coarse farm LHS 258 (11 params, drive frozen; best 2 mm 25.83), CMA round 1 (4 farm streams, 2636
tries; A/B/C drive frozen, D drive + dyad free; best 2 mm 23.29), CMA round 2 (4 streams from the round-1 bests, 23
params incl. the J1 seat and the drive; 3020 tries; best 2 mm 20.02). Over all 5656 CMA tries in order: best gained
**0.32** score points over the second half (< 1), **0.17** over the last third (< 0.5); top-5 spread of the best stream
**0.09** (< 3). Per stream (2nd half / last third / top-5): A2 0.91 / 0.34 / 0.09, C2 0.15 / 0.15 / 0.07, D2 0.24 / 0.24 /
0.06, B2 0.19 / 0.19 / 0.34.

## The design gate of the spec - FAILED (measured)

fast 2 mm <= 15.0: 20.02 (fail); fast plain <= 13.0: 16.70 (fail); contact <= 0.015: 0.032 (fail); hub 3 in band >= 0.60:
0.50 (fail; only the wd 85 family B2 reaches 0.73, and it is 0.7 worse frozen); workspace in-band >= 0.874 / 0.841:
0.839 / 0.814 (fail); knee assertion: holds. The proposer's "worn as-is 23.43 -> crude re-seat 19.47 fast" and the
expected "fast 13-15 after the re-fit" did not happen: the co-fit stops at fast plain ~16.3-16.7.

## Verdict

**A complexity Pareto point, not a lead change.** Frozen exact 21.07 (score 92.34), 2 mm 32.25 (better than the lead's
34.03 and the roller row's 46.82), held out 24.59, at complexity **23.75** (lead 49, roller row 45.25): about half the
complexity for +2.2 plain points / +3.2 at 1 mm / -1.8 at 2 mm / +1.9 held out vs the lead. On the verified
complexity front it would sit between H1 (27.20 at cx 19.5) and minarc pick1 (18.40 at cx 33). It needs the
adversarial verifier, the alignment audit (--ref sidecar-longdyad-knuckle-3r) and the user's misalignment budget
before it can be called anything more.

**Limiter, measured:** the J2 fold (86 of 360 frozen, same as every knuckle row) and hub 2's crown in scapular-plane
abduction (9 of 13 metal-lost poses); in-band: hub 3 obliquity on a GH ray (0.50). The kneeless change itself is free
on the bench (the bracket is in band and never touches); what it costs is the b3 tilt: the knee rows tilt J3 0.33-0.38
toward the skin normal, which puts hub 3 square on the deltoid and moves the dyad. That is ~3.5 fast plain points
(roller-longdyad, same drive, knee: 13.19 fast) and +2.2 frozen vs the lead.

## New knowledge (predicts beyond this morphology)

1. **The pin knee's job is the b3 tilt, not closure slack.** With b3 = 0 the knee is provably idle (drift 0 exactly) and
   deleting it is free on the bench (bracket in band 0.92-1.0, no contact); every point lost is the GH-ray hub 3's
   obliquity and the re-fit dyad. The knee is worth about 2.2 frozen gap points (3.5 fast) plus a 1.5x smaller liner
   misfit under GH-centre error - that is the price list for any "drop the knee" proposal.
2. **Fast-to-frozen penalty shrinks without the knee:** +4.4 here vs +8.4-9.0 for the knee rows (the knee window and
   slide losses tuned to the 160-pose sample were part of the over-fit).
3. **A GH-ray J3 moves the metal problem upstream:** the bracket and hub 3 never touch; the metal-lost poses are hub 2's
   crown (scapular-plane abduction 90-165) and the flank lug - a hub-2 crown lever (cap height, lobe ring) is what
   would help this class, not the bracket.
4. **Rigid closure + real misalignment:** a 3 mm GH-centre error already exceeds a 3 mm liner on 61 % of poses for a
   rigid spherical chain (worst direction); a single along-arm cuff slide does not fix it (the misfit is across the arm).

## Next

Verifier on A2 (claim file: docs/concepts/rows/kneeless-roller-knuckle-3r.json best_params; harness = this model's
`frozen` / `held` / `flood` / `redteam` modes, CB_EXACT=1, on the farm). Then the alignment audit vs the lead. The
lever to try on this class: hub 2's crown (the 9 metal-lost poses) - e.g. the twin kneeless-sidecar's hub-2 geometry,
or a lower hub-2 cap; and the user's misalignment number decides whether a knee-free cuff is wearable at all.

## Verification

**VERIFIED** (2026-10-16 ~23:25 UTC, independent skeptic, harness `docs/concepts/verify/kneeless-roller-knuckle-3r.py`,
farm, ~$0.02). Not refuted, and not a lead.

The claim's model was loaded unchanged. The harness retargets the round's roller verifiers
(`verify/roller-longdyad-knuckle-3r.py` on `verify/sidecar-roller-flank-knuckle-3r.py`) at this model's class, clamp, params
and best config, and adds the kneeless-sidecar verifier's rigid-bracket and re-collision checks. Protocol: fit on
Bench(60,160) fast, shape frozen, worn on Bench(110,360) with CB_EXACT=1 (and on the held-out set).

**Checks added, and what they found (taken poses of the worn bench)**

| check | result | poses removed |
|---|---|---|
| cam closure in the world (roller centre on the flank's synthesised path) | 0.0 mm | 0 |
| roller vs lug metal (>= roller radius); K sense | min 3.30 mm; wrong sense 0 | 0 |
| pressure angles at each pose (claim's 43 deg; also re-read at 45) | crank 8.8 / horn 41.5 deg (held out 42.5); 0 fail at either cap | 0 |
| real lobe pressure angle | 33.1 deg | 0 |
| K inside the flank's range | dK taken 43.5 deg (held out 45.8) of dK_lim 46.75 | 0 |
| rigid bracket, from the body transforms (member 3 and the bracket plate in the pad frame) | drift 0.000 mm over all taken poses | 0 |
| every taken pose re-collided (non-adjacent >= 1 mm, adjacent >= 0.15 mm) | min 1.53 mm (crank vs hub K); E-L2 3.7 mm (1.4 held out) | 0 |
| fold margin in the one metric (th) | min 5.41 deg (held out 5.09); 0 poses under 5 | 0 |

**Numbers**

| bench | gap | reach | follow | ib14 | ib10 | contact | 1 mm | 2 mm | overhead | min metal |
|---|---|---|---|---|---|---|---|---|---|---|
| Bench(110,360) exact, frozen | **21.07** (score 92.34) | 0.725 | 1.0 | 0.891 | 0.558 | 0.026 | 23.23 | 32.25 | 7/28 | 0.01 mm |
| same, roller-pin head + lug edge strip added (`--head`) | 20.95 | 0.725 | 1.0 | 0.892 | 0.561 | 0.026 | 23.11 | 32.14 | 7/28 | 0.01 mm |
| held out, frozen | 24.59 | 0.694 | 1.0 | 0.889 | 0.558 | 0.029 | 27.20 | 36.06 | 16/71 | 0.11 mm |

- The claim's frozen numbers reproduce exactly; the added checks remove nothing. The verified number is the plain wear, 21.07.
- Lost poses on Bench(110,360): fold 86, contact 10, parts 3 (overhead: fold 15, contact 4, parts 2).
- Continuity flood fill: full 21.07 (0 dropped), knn 23.35 (8 dropped), bench grid 49.5 (the lead: 18.91 / 21.72 / 43.4).
- The knee is idle: the model's own report (ptp 0.000 deg, |s| 0.000 mm) and the independent transform check agree.

**Champion on the same bench: 75.94** (risley-turret table; 66.97 through the knuckle code and checks). This design beats
it by about 55 gap points.

**Against the lead: fails the A1 dominance gate.** The lead (sidecar-longdyad-knuckle-3r) scores 18.91 plain and 34.03 at
2 mm. This design is better at 2 mm (32.25) but worse plain (21.07) and worse held out (24.59 against 22.67). It stands as a
verified complexity Pareto point at complexity 23.75 (lead 49), next to kneeless-sidecar (21.11 at complexity 28): the two
knee-free rows land within 0.04 gap points of each other.

**Watch items (red team)**

1. **Unscored workspace in-band (gaming pattern L2).** 0.855 overall and 0.828 at elevation 90-140 on the worn bench, below
   the lead's 0.874 / 0.841 bars. Hub 3 is 0.505 in band (median 13.9 mm) and link 2 0.71.
2. **Metal at the skin.** A taken pose has metal at 0.01 mm (hub 2's crown, the class's metal limiter); 1 mm counted as
   contact costs +2.2 gap points.
3. **The drive sits at its caps held out.** The horn pressure angle reaches 42.5 against 43, and dK 45.8 against 46.75.
   A CAD tolerance on the flank or roller must be priced before build.
4. **No closure slack for GH error.** The rigid bracket puts all GH-centre misfit on the cuff liner (claim's red team:
   3 mm of GH error gives median 3.4, p90 4.8 mm misfit). This needs the user's tracking-error budget before CAD.
5. **K on stop A.** K sits on its spring stop on 499 of 863 held-out taken poses, so stop-A hold under gravity (the R17
   lag seen on pick1) must be judged in CAD.

# minarc-stop-knuckle-4r, variant B: independent verifier, lens mechanism / manufacturability / red team

Claim under test: `docs/concepts/rows/minarc-stop-knuckle-4r.json`, variant B, best_params (CMA stream BD), model
`docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py`. The claim: frozen shape worn on Bench(110,360) exact, gap 15.42
(score 94.4; reach 0.769, follow 1.0, in-band14 0.899, contact 0.023; near-touch 22.17; min metal 0.05 mm),
complexity 33. The verified leader it would beat is the pin knee H1: 24.48 at margin 5 (polish protocol), 27.20 on the
round-3 protocol.

- Harness: `docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py`. It imports the model unchanged and swaps only the
  part under test.
- Raw outputs: `.cache/minarc_verify_mech/*.json` (git-ignored).
- Runs: local (at most 2 processes) and the exo-cpu1 farm (7 jobs, about $0.15).

## Reproduction

The frozen exact BD reproduces to the digit, both locally and on the farm: **15.42** (reach 0.7694, follow 1.0,
in-band14 0.8991, in-band10 0.5805, contact 0.0227). Near-touch is 22.17 and the minimum metal is 0.05 mm, on the
raise-overhead clip at plane 30 / elevation 150 / axial -60. Poses lost: fold 56, slide 16, contact 9, parts 2.

## 1. DOF and whether K is determined

- **Count.** The shoulder chain has J1, K, J2 and J3: four revolutes, of which three are active. The two-pin knee at the
  cuff is the H1 closure, already verified and counted as cuff self-alignment.
  - So the chain sits at the user's cap of 4, not at the preferred 3.
  - K is a fourth joint in the chain. It is passive, spring-held and sensed, with 0 passive translations.
- **Determined.** Yes, under the model's own law. Each pose gets exactly one state: K on stop A (a rigid 3R), or J2 on
  a stop with K at the smallest opening that closes.
  - The bench does not pick the better of two states per pose. The 3R branch is fixed (`self.branch`) and K's sign is
    fixed (`sign(psiA)`).
- **Where K actually works.** K never moves on any clip, fit or held-out (speeds mode: K rate 0 deg/s on all 8 clips).
  Every forced state the bench scores (273 envelope poses, 50 taken on the big bench) is a static workspace pose.
  - So the knuckle's whole gain is static workspace reach, and the continuity rule (section 5) decides whether that
    gain is real.

## 2. The J2 "hard stop" is not a stop on J2 (a modelling error, priced: no cost)

- **What the model stops.** `KA.law` puts the J2 stop on the VIRTUAL interior angle at J2, between the arcs J2->J1 and
  J2->J3. J1 sits on link 1a, which is not a body J2 joins.
- **What a real stop limits.** The row and the doc describe "a dowel in an arc slot" at J2. That limits J2's own joint
  angle q2, the angle of link 2 relative to link 1b.
- **Measured** (stops mode, all 1883 poses):
  - In state A, q2 spans [-40.20, 109.19] deg. The q2 values of the model's own window ends are -41.07 (phi_hi) and
    109.35 (phi_lo).
  - In the claim's forced states, J2 sits up to **14.48 deg off its own stop** (median 1.72; 152 of 273 poses are more
    than 1 deg off).
  - So the modelled configurations are not equilibria of a dowel stop: J2 is free there and K is not on a stop, so the
    spring would move the chain.
- **The physical law.** J2 locked at q2 = -41.07 or 109.35, with K opening to the smallest closing angle (scan plus
  bisection along the self-motion).
  - K's angle changes by up to 6.02 deg (median 0.63).
  - 15 more envelope poses close and none are lost.
- **Priced, frozen Bench(110,360) exact (farm):**
  - As built (the claim's fitted shape, worn with physical stops): **14.85** (reach 0.775, near-touch 21.58).
  - Refit with physical stops: **15.30** (fast 6.64).
  - The error does not cost points. The model must still be fixed before anything is built from it.

## 3. The spring (the part as specified does not exist; a real one fits, priced: no cost)

- **The claim's spring.** The row specifies a clock spring strip of 0.2 x 3 mm stainless, about 4 turns. The doc gives
  0.08 N.m preload and 0.03 N.m/rad, so 0.113 N.m at stop B (dK -61 deg).
  - A 0.2 x 3 strip carries M = sigma b t^2 / 6 = **0.028-0.040 N.m** at 1400-2000 MPa.
  - The claimed torque needs **4000 MPa at preload and 5650 MPa at stop B**. That is not a real spring.
- **Demand, measured by virtual work along K's self-motion** (spring mode):
  - Masses: 8 x 3 Ti straps from the fitted samples, 10 g per O20 hub split across its two members, +2 g for the cap.
    Moving members weigh 61 g.
  - Gravity's opening torque: at most 0.0113 N.m with the thorax upright; 0.018 N.m in the worst direction at 1 g;
    **0.037 N.m at 2 g**.
  - Seal friction along the self-motion: MR117-2RS pairs at 1-2 mN.m each, weighted by the self-motion ratios (J1 moves
    up to 4.6 deg per deg of K). That is **0.010-0.020 N.m**.
  - Returning K to stop A therefore needs at least 0.038 N.m quasi-static and about 0.057 N.m at 2 g.
  - The 0.2 x 3 strip falls short at 2 g. K would lift off stop A in brisk moves and could stay open (hysteresis).
- **A real spring.** A 0.3 x 5 mm 1.4310 strip, 4-5 turns: 1070 MPa at 0.08 N.m and about 1500 MPa at stop B. It fits
  a cap of about O16 x 6 mm.
  - That cap does not fit inside the O20 12.25 mm stack, so hub K grows about 6 mm on its crown side.
- **Priced.** Hub K was re-solidified 6 mm taller (cylinder, crown samples, skin rings), with the hook checked: the
  knee-hubK clearance moved 64.9 -> 64.3 mm.
  - Frozen exact: **15.42**, unchanged. Hub K's nearest parts are hub 1 at 9.7 mm and link 2 at 30.5 mm.
  - With physical stops as well: **14.85**, the same as physical stops alone.
- **K free (the spring yielding).** Not re-run. With the 0.3 x 5 strip, the preload of 0.08 N.m exceeds the 2 g demand
  of 0.057 N.m at every pose, so no pose crosses.

## 4. Parts at real size

- Hub K is an O20 disc and wall at its fitted level fK, with the 12.25 mm crown (+6 mm cap in section 3).
- Links 1a and 1b are 8 x 3 straps, with the L1a-L1b and L1b-L2 adjacency rules. Hub 2's housing rides on link 1b.
- Stops:
  - K's stop dowel: an arc slot covering 61 deg of travel at about 8 mm radius, 9 mm of arc. It fits the O20 face.
  - J2's stop dowel: an arc slot covering 150 deg of q2 at about 8 mm radius, 21 mm of arc. It fits.
  - Neither is sampled as metal, but both lie inside the hub envelope.
- No zero-height parts were found.

## 4b. Speeds, the jam and the pinch (red team)

- **Clips at their real 10 fps** (fit plus held-out, speeds mode):
  - Largest joint rates: J1 125.6 deg/s (wash opposite shoulder), J2 206.1 deg/s (wave, held out), J3 137.9 deg/s,
    knee pin a 184.1 deg/s.
  - Ratio to the arm's own angular speed: at most 2.95.
  - **K: 0 deg/s.** No clip asks any joint to snap.
- **The gallery-loop note** (J1 at 20-40 deg/frame before stop B) is a workspace path through the forced region, where
  the sub-chain J1-K-J3 nears its fold. There J1 turns up to 4.6 deg per deg of K (section 3).
  - The continuity flood fill (section 5) drops any edge on which K or a knee pin steps more than 10 deg per 2 deg of
    arm motion, or an active joint more than 25 deg.
- **The jam.** At stop B with J2 on its stop, the chain is a locked 2-joint chain: it is the reach boundary, not a pose
  inside it.
- **The pinch.** 0.05 mm of metal on the raise-overhead clip (plane 30, elevation 150, axial -60), reproduced. Near-touch
  is 22.17 (as built with physical stops: 21.58).

## 5. Continuity rule ("reach must be reachable by moving")

The claim scored static reach only. The model's `continuity()` checks only the fit clips at 10 fps, and K never moves
on any clip. So the rule's flood fill was run here on the frozen big bench, in three readings:
- edges are 2-deg HG slerps;
- every frame must close (ik, knee window, radial tolerance);
- K, pin a and pin b may never step more than 10 deg, and the actives never more than 25 deg;
- the seeds are the taken state-A workspace poses.

| reading | gap | reach | forced taken poses connected |
|---|---|---|---|
| static (claim) | 15.42 | 0.7694 | 50 / 50 (not checked) |
| literal `connected()`: grid neighbours inside the Bench(110,360) 360-pose set | 24.79 | 0.6778 | 17 / 50 |
| nearest neighbours (edges up to 1.6 x the median nearest-neighbour HG angle) | 16.27 | 0.7611 | 47 / 50 |
| **full 15-deg envelope grid** (1432 poses; intermediate nodes = every pose the chain closes at) | **15.42** | 0.7694 | **50 / 50** |

- **The literal reading is a sampling artifact.**
  - The bench's 360 workspace poses are a 1-in-3-to-4 subsample of the envelope grid.
  - 11 of the 33 poses it drops have no taken grid neighbour in the subsample at all. The rest sit on chains the
    subsample cuts.
- **On the full envelope grid the forced region is connected.** All 248 kinematically valid forced envelope poses are
  reached from the state-A region with no K or knee step above 10 deg per 2 deg of arm motion.
- **Caveat.** Skin contact is not evaluated at the intermediate envelope nodes that are not bench poses. The bench never
  checks between its own samples for any design either.
- **Verdict on continuity:** holds, at no cost.
- **Protocol note for the lead.** `connected()` run on a subsampled bench under-connects any design. The stop-relay
  verdict used that reading, so it should be re-checked on the full envelope grid
  (`flood(..., grid="full")` in this harness).

## 6. The J2 stops sit 1.4-1.9 deg from the J2 dyad's fold (below the user's 5-deg bound)

- **Where BD's stops sit.** phi_lo 12.28 and phi_hi 162.70, at a1 38.07 and a2 58.75. In state A the J2 dyad reaches
  **1.37 deg** (stretched) and **1.88 deg** (folded) of th from its fold before a stop engages.
- **The rule.** CLAUDE.md: "the user's 5 deg is the lower bound for the plain fold window". With K on stop A, the chain
  is exactly a plain 3R.
  - The doc's own red-team item 5 names this the open stop-guard question.
- **Measured exposure:**
  - 8 clip frames run inside the 5-deg margin (wash opposite shoulder, down to 4.02 deg). These are frames the wearer
    feels.
  - 80 state-A envelope poses run inside it, down to 1.51 deg.
- **Priced: margin-equivalent stops** (the doc's own second reading; local, frozen Bench(110,360) exact).
  - The stops move to phi 20.793 / 146.614, so the dyad never comes within 5 deg of its fold and K opens exactly there.
  - Same BD seats. The shape is refit on Bench(60,160) fast with these stops, then worn frozen.
  - Result: **18.45** (fast 10.83; reach 0.7472, follow 1.0, in-band14 0.889, contact 0.0207; near-touch 24.26; min
    metal 0.05 mm). On the full envelope grid the connected gap is also 18.45 (64 of 64 forced poses connected).
  - **Cost: +3.03 gap points over the claim's 15.42.**
- **Not re-optimised.** A CMA run with the stops held at the 5-deg margin might recover part of this. That run was not
  done here.
  - The agent's own BB stream (mstop 1) is a different reading, 21.40: it rejects the near-fold state-A poses instead
    of opening K there.
- **Fully buildable and compliant** (5-deg stops + physical J2 stop + hub K 6 mm taller; local, frozen exact):
  **17.32**.
  - fast 10.83; reach 0.7583, follow 1.0, in-band14 0.889, in-band10 0.583, contact 0.0205.
  - near-touch 23.10; min metal 0.05 mm.
  - On the full envelope grid 68 of 68 forced poses are connected, so the connected gap is also 17.32.
  - The physical stop gains 1.13 points here.

## Summary of prices (frozen Bench(110,360) exact, same BD seats)

| configuration | gap | score | reach | near-touch | cost vs 15.42 |
|---|---|---|---|---|---|
| claim as modelled (reproduced, local + farm) | 15.42 | 94.4 | 0.7694 | 22.17 | - |
| physical J2 stop, claim's shape (as built) | 14.85 | 94.6 | 0.775 | 21.58 | -0.57 |
| physical J2 stop, refit | 15.30 | 94.4 | 0.775 | 22.05 | -0.12 |
| hub K 6 mm taller (real spring cap) | 15.42 | 94.4 | 0.7694 | 22.17 | 0.00 |
| cap + physical stop | 14.85 | 94.6 | 0.775 | 21.58 | -0.57 |
| J2 stops at the 5-deg fold margin (claim's virtual stop law) | 18.45 | 93.3 | 0.7472 | 24.26 | **+3.03** |
| **5-deg stops + physical stop + 6 mm cap (buildable and compliant)** | **17.32** | **93.7** | 0.7583 | 23.10 | +1.90 |
| continuity, literal `connected()` on the subsampled bench (artifact) | 24.79 | 91.0 | 0.6778 | - | +9.37 |
| continuity, full envelope grid | 15.42 | 94.4 | 0.7694 | - | 0.00 |

## Verdict: REFUTED as claimed (15.42); the corrected design measures 17.32

**Why the claim does not stand.**
1. **Not buildable as modelled.**
   - The J2 "hard stop" acts on a virtual angle that no dowel at J2 can stop. In the claim's forced states J2 is up to
     14.5 deg off its own stop.
   - The specified clock spring (0.2 x 3 mm strip) cannot make the specified 0.08-0.113 N.m: it would need 4000-5650 MPa
     against a capacity of 0.028-0.040 N.m.
2. **It runs the J2 dyad to 1.37 / 1.88 deg of its fold**, below the user's 5-deg bound. CLAUDE.md also says never to
   shrink the singularity margin to buy reach without a red team and the user's say.
   - Priced in the claim's own model: +3.03 gap points.

**What does stand.**
- **The fixed design scores 17.32** (score 93.7), measured here on Bench(110,360) exact with the shape frozen from
  Bench(60,160) fast. The fixes are a q2 stop dowel at J2, J2 stops at the 5-deg margin, and a 0.3 x 5 mm clock
  spring in a 6 mm taller K cap.
  - That beats the verified H1 (24.48 at margin 5) by 7.2 points.
  - Near-touch is 23.10, but the minimum metal is still 0.05 mm (raise-overhead clip).
  - 4 revolutes sit in the shoulder chain (the cap, not the preferred 3), with 0 passive translations. Complexity is 33
    (+ the cap).
  - Before it is re-claimed it needs:
    - the model fix (q2 stops) in `minarc-stop-knuckle-4r-pinknee.py`;
    - a near-touch CMA with the stops held at a margin of 5 deg or more;
    - the held-out bench;
    - an independent verifier on the corrected row.
- **Sound as claimed:**
  - Continuity on the full envelope grid.
  - Joint speeds: no snap on any clip, and K never moves on a clip.
  - Determinedness: one state per pose.
  - The spring once resized: it covers the 2 g plus friction demand of 0.057 N.m with a 0.08 N.m preload, at zero bench
    cost.

**Red-team leftovers.**
- **The pinch.** 0.05 mm on the overhead raise; the CMA searched the plain gap, not the near-touch gap.
- **Stiffness near stop B.** The sub-chain J1-K-J3 nears its fold there, and J1 turns up to 4.6 deg per deg of K. It is
  felt only on workspace paths, never on a clip.
- **The stop B / J2-stop limit.** The arm can load the O2 dowels with its full torque; they need a strength check in
  the L1 CAD.


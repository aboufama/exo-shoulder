# geneva-tail-knuckle-3r: Geneva-tail knuckle on the plain spherical chain with a crest-basin J3

Round 6, pick 2 (docs/concepts/round6_ideation.md). Model: docs/concepts/models/geneva-tail-knuckle-3r.py.
Status: being screened (this file is updated as the numbers land).

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Gate on the hubs first. Before tuning any cam, they would check that hub 2, hub K and hub 3 can sit in the band in
     state A at all. A Geneva law cannot rescue a chain whose J3 side floats off the skin.
   - Count the fold poses the tooth has to win, and price them. They would measure how many stretched poses exist at
     these seats and how many of those the tail can drive past the onset without lift-off, before paying for the tail.
   - Choose a one-sided or a two-sided drive from data. The folded side gets a tooth only if the folded poses are worth
     the metal.
   - Prefer the crown embodiment, where the roller runs over hub K's cap and needs no lug, because it keeps the tail short.
2. **The rawest material.**
   - The posed skin itself, through the bench's signed-distance cache, read by `K.requirement`. This is the hub-level
     march along each axis per pose: the raw "how high must this hub sit" number.
   - The motion clips: the bench's 60 / 110 clips and the workspace grid.
   - The fold law at each pose, computed from (u1, u3) directly. These are not digested in-band summaries.
   - The crest-basin hub-3 map is re-derived on the posed skin (hub_need per pose), not quoted.
3. **The specific methods and tools.**
   - The kit-rule variant-A model (tools/concept_kit.py K1-K7) for the chain.
   - The exact one-tooth spherical contact law, ported from geneva-tail-knuckle-pinknee-3r. It includes the pressure-angle,
     tooth-radius, rate and lift-off checks.
   - park.py-style hub_need pre-gates.
   - A Latin-hypercube screen and then CMA-ES on the farm (tools/cloud_run.py, Bench(60,160)). The objective is the
     near-touch gap.
   - The frozen wear on Bench(110,360) exact with the strict continuity flood fill: K on stop A at elevation 0, a 2-deg
     slerp, and no joint jump above 10 deg.
4. **What, other than me, shows the number is right.**
   - The bench (tools/concept_bench.py) and the kit's honesty audit.
   - The frozen exact wear on the big bench.
   - The adversarial verifier.
   - A red-team pose list: the pose that jams, the minimum metal-to-skin point, and the overhead split.

## The crest-seat convention clash, resolved by measurement

The clash: on the locked control, `knuckle-crest-hub3-4r` measured hub 2 at 0.04 in band at the deltoid-crest seats,
while `deltoid-crest-j3-3r` had claimed 0.82-0.997. It is **not a convention clash. It is the O20-only hub rule.**

I re-ran the crest lens's own script (scratchpad lensj2/lay.py through docs/concepts/models/spine-parked-j2-3r.py) at
crest seed B (az 95.37, el 62.54, a1 44.53, a2 50.26, wd 108.87, wa -3.53, inv3 / neck over), and the zc-frontier plain
3R at seed A. The results:

| hubs | margin | hub 2 in band | hub 2 level F | gap (fast) |
|---|---|---|---|---|
| O15 (CB_ALLOW_SLIM=1) | 10 | **0.9975** | in band | 28.24 |
| O15 (CB_ALLOW_SLIM=1) | 5 | **0.9976** | in band | 22.90 |
| O20 (the rule) | 10 | 0.0005 | 86.9 mm | 80.17 |
| O20 (the rule) | 5 | 0.0325 | 77.9 mm | 69.65 |
| O20, zc-frontier plain 3R, seed A, margin 5 | 5 | 0.0386 | 76.2 mm | 71.21 |

- The variant-A / knuckle model and the zc-frontier plain 3R agree to the digit, so the knuckle model is not the cause.
- At these seats hub 2 sits where 2.5 mm more disc radius raises its fitted level by about 25-30 mm.
- The crest basin is an O15-only basin. Under "Keep O20 only" it is closed.
- The hub-3 crest map (all-fit 0.85 at wdir(94, -15)) still stands, but no O20 hub 2 lives with it at these seats.

## The model (docs/concepts/models/geneva-tail-knuckle-3r.py)

- **Base.** It is built on the kit-rule variant-A model (minarc-stop-knuckle-4r-a-kitrule.py), loaded as its own module
  copy. That model supplies the kit's J1-J3 fold rule at 5 deg, the near-touch objective, hub K's +6 mm clock-spring
  cap, the strict continuity flood fill and the frozen wear.
- **The law.** The exact one-tooth spherical contact law is ported from geneva-tail-knuckle-pinknee-3r and rewritten for
  the variant-A chain. Every step is a rotation about an axis through GH.
  - The roller centre turns with link 2 about u2 and touches ONE half-plane flank. The flank passes through uK and is
    fixed to link 1a.
  - The roller's side is chosen so that the pushed flank opens K.
  - th_law(q) is pose independent and is inverted per pose. Its valid prefix needs all of these:
    - th rising, with dq/dth <= 3.45;
    - pressure angle <= 45 deg;
    - contact radius <= HUB_R (crown) or the lug length (beside);
    - a1e <= a1max (stop B);
    - the dyad margin m3e >= 5 and the forced sub-chain margin msub >= 5;
    - no lift-off along the pose's self-motion.
  - The folded side has no tooth: a J2 dowel, and the poses beyond it are lost.
- **The metal, which the spec did not fully specify.** Three changes:
  - **K's stack is flipped**, so link 1a is the upper member at K and carries the tooth.
  - **Crown embodiment** (closest approach d < 14 mm): the roller (O8 x 4) rides over K's cap with its bottom >= the cap
    top + 1.2 mm.
  - **Beside embodiment** (d >= 14 mm): a 6 mm **lug** on link 1a runs along the flank from K's axis to the largest
    contact radius + 3 mm. It sits at link 1a's level, over link 1b + 1 mm. The roller runs at the lug's level.
  - The **tail** is an 8 x 3 Ti strap, rigid with link 2, from hub 2 to the roller. It passes over link 1a, link 1b,
    hub K and the lug, each + 1 mm.
  - Every sample is skin-fitted, in band and K6-checked like a link.
  - Roller and lug share a pseudo-joint "D" on the roller axis. This exempts their designed contact from K6 within 12 mm
    of the roller axis. It is optimistic for state-A poses in which the roller passes the back of the lug; that is
    stated, not modelled.
- **A config with no working drive** scores +100 and is marked dishonest. Without a drive it is a plain 3R with a stuck
  K and no tail, which is not this design.
- **Search space:** the seats, the arcs, K's placement (b1, b2), a1max, the onset smhi, smlo, d, psi_c, q, inv3 and
  end_extra.

## What the law and the tail measured (new knowledge)

1. **The onset margin is the law's fuel.** The driven state must keep the dyad margin a1e + a2 - th >= 5. Since q2 keeps
   moving past the onset, q2 eats that margin. The law therefore ends at m3e unless the onset sits well inside the
   window.
   - At the LA1 seats, onset smhi 6: the law covers th 109 -> 117-131.
   - At smhi 13-20: it covers th 100-102 -> 129-137, matching the sensed stop law's 136.5.
   - The best configurations all sit at smhi 13-19. Most poses are then DRIVEN, including 56 of the 57 rest poses
     (K is open at rest).
2. **The drive ratio and the tail length trade one-for-one.**
   - A fast drive (crown, d 7 mm) needs the roller on a long tail. The tip is 39-47 deg from u2.
   - A short tail (tip 13-20 deg) gives a slow drive (lever ratio about 0.45). It ends at th <= 121.
   - In between, the beside embodiment at d 14-22 mm (tip 27-40 deg) reaches th 126-137.
3. **The tail sweep is the metal cost.** The tail is rigid with link 2, so it turns with q2 across the whole state-A
   window. Its tip sweeps a circle about 40 deg in radius around hub 2.
   - At LA1, the skin under the roller needs a level of 135-152 mm from GH (p50-max over the fit poses), against hub
     K's 55 mm.
   - Tail and roller sit 0-24 % in band in every configuration measured.
   - At the best configuration the tail metal (tail + roller + lug) costs **9.3 gap points**: 39.36 with it against
     30.02 with the law alone at the same parameters.

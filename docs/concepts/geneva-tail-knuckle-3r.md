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

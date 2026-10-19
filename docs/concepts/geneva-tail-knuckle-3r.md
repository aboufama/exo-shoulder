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

## The search (farm), and the convergence gate

| stage | configs | best near-touch gap (fast, Bench(60,160)) | note |
|---|---|---|---|
| LA1 control (the proposer's seats, d 7, onset 6.1) | 3 | 67.45 (law only, no tail: 51.03; sensed stop law: 30.03) | the law covers th 109 -> 117 only |
| LHS-1 on the farm (tail metal; crown d 4-13) | 300 | 54.97 (no drive) / 57.88 (drive ok) | drive valid in 83 of 300 |
| gate LHS-2, law only (no tail: an upper bound on reach) | 300 | - | hubs >= 0.8 with a drive: 8 configs, max reach 0.66; reach >= 0.72: max min-hub 0.765 |
| CMA, 6 streams x 16 on the farm (tail metal, near-touch) | 11270 | **39.39** (stream s4) | gate passed (below) |
| gate CMA, 4 streams (max plain reach s.t. hub 2 / K / hub 3 >= 0.8, law only) | 6676 | reach 0.825 at hub 3 0.802 | the literal kill gate is passed, law only |

The convergence gate, all six streams merged in generation order:
- the best gained 0.23 score points over the second half (< 1);
- it gained 0.20 points over the last third (< 0.5);
- the top 5 lie within 0.01 points (< 3).

It is converged.

**Best configuration (s4), re-measured on the final model:**
- Parameters: az 92.11, el 63.02, wd 36.33, wa -4.76, a1 40.83, a2 74.39, b1 33.44, b2 55.70, a1max 71.62, smhi 13.26,
  smlo 7.19, d 19.49 mm (beside), psi_c 11.53, q 0.965, inv3 0, end_extra 0, sigma -1, sK -1.
- **Gap 39.36 near-touch = plain** (score 85.7). Reach 0.825, follow 0.95, in-band14 0.673, in-band10 0.392, contact
  0.091. Minimum metal 1.13 mm. Overhead ws reach 4 of 12.
- Drive: tail tip 39.7 deg from u2. K opens up to 49.6 deg over 23.6 deg of q2. Th runs 101.95 -> 136.61 and ends on the
  m3e margin. Peak pressure angle 41 deg; contact radius up to 21.7 mm on the lug.
- In band per part:
  - hub 1 1.00, hub K 0.99, hub 2 0.92, link 1a 0.93, link 1b 0.99, lug 0.98;
  - **hub 3 0.75, link 2 0.33, neck 0.23, tail 0.15, roller 0.03**.

Two measurements at the same parameters:
- Law only, without the tail metal: 30.02 (reach 0.85, in-band 0.72). The tail metal costs 9.3 points.
- The sensed stop law in place of the Geneva law: 53.5.

The kill-gate configurations (hub 3 >= 0.8 at reach 0.825, law only) score **75.19** near-touch (52.7 plain) once the
tail is built: contact 0.24, link 2 0.37, neck 0.21.

## Red team (own best)

- **The pose that jams.** The folded side has no tooth: J2 sits on its dowel. On the fast bench, 3 of the 17 overhead
  poses (th ~36) and the across-body poses past the law end (th 147-159, m3e) do not close. Of the 17 overhead poses,
  6 are taken and 8 close but touch the skin.
- **The point that pinches.** On the fast bench, metal comes within 1.13 mm at ws (plane -75, elev 15, axial 150), a
  behind-the-back reach. On the big bench frozen, the minimum is **0.31 mm** (static).
- **Optimistic numbers, stated.**
  - The roller-lug K6 exemption within 12 mm of the roller axis also covers state-A passes behind the lug.
  - The crown embodiment's tooth blade is not modelled as metal.
  - Lift-off uses the pinknee model's self-motion slope test.
  - The fast fit (39.36) loses about 14 points when worn frozen (next section).
- **Feel at rest.** 56 of the 57 rest poses are DRIVEN: K is held open by the roller against the clock spring. The
  wearer's resting arm carries the spring torque through the chain. This is small (0.3 x 5 mm strip), but it is
  unlike every other knuckle design, which rests on stop A.
- **Continuity rule.** The strict flood fill seeds at elevation 0 with K on stop A. There is NO such pose here (every
  elevation-0 pose is driven), so the strict rule gives reach 0 by construction. K is a function of q2 everywhere (the
  law is continuous at the onset, with no branch). The seed-any flood fill is the meaningful reading, and both are
  reported.

## Frozen wear (lesson c) and held out

The best shape was fit on Bench(60,160) fast, its profiles frozen, and worn on the exact path. Jobs ran on the farm:

| bench | gap (plain) | score | reach | follow | in-band14 | contact | near-touch | min metal | overhead ws reach |
|---|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fit, fast | 39.36 | 85.7 | 0.825 | 0.95 | 0.673 | 0.091 | 39.36 | 1.13 mm | 4/12 |
| **Bench(110,360) exact, frozen** | **53.32** | **80.6** | 0.739 | 0.936 | 0.675 | 0.134 | 55.88 | 0.31 mm | 10/28 |
| held-out bench, exact, frozen | 59.55 | 78.4 | 0.707 | 0.931 | 0.674 | 0.158 | 62.80 | 0.12 mm | 19/71 |

- The continuity flood fill, seed-any (2-deg slerp, no joint jump > 10 deg), connects all 1270 closing workspace nodes,
  so 0 poses are dropped.
- The strict seed (K on stop A at elevation 0) has no seed, because every elevation-0 pose is driven. It would read
  149.46 by construction.

## Verdict: DEAD (converged, every number measured)

- **Bests.** Fast 39.36. Frozen exact on the big bench 53.32 (score 80.6). Held out 59.55. Complexity 14.0
  (tools/simplicity.py), 0 passive translations, 3 active.
- **Against the bars.** Every bar is far ahead:
  - zc-frontier's verified 31.04 at complexity 0;
  - H1's 24.48 at complexity 21.5;
  - minarc's 18.40 / 19.54.
- **The kill gate.** It is passed, but only law-only and only at hub 3 0.80. At those seats the J3-side straps leave the
  band (link 2 0.37, neck 0.21), and with the honest tail the same configuration scores 75.19.
- **Limiters, measured.**
  1. **The J3 side.** Link 2 is 0.33 and the neck 0.23 in band at every seat with reach >= 0.8 (hub 3 0.75). The
     crest basin that was meant to fix hub 3 is O15-only.
  2. **The tail sweep.** The tail is rigid with link 2, so its tip, about 40 deg from u2, sweeps the whole state-A
     window. That metal costs 9.3 points at the best shape.
  3. **The fold side has no tooth.** The overhead poses with th ~36 are lost.
- **What did work.** The exact one-tooth law reaches as far as the sensed stop law: th to 136.6, and 0.825 reach fast
  with the law alone at 30.02. A determined K is no longer the problem. The metal that carries the determination is.

## What next (for the loop)

- The tail sweep is a property of every link-2-mounted driver. A driver that does not orbit hub 2 removes it:
  - a roller on link 1b, with the tooth on link 2 near hub 2 (the roles swapped), so that only a short lug orbits;
  - or a crown cam on hub 2 (cam-unfold-4th's C3 measured 22.02 fast with the pin knee).
- The J3 side needs the pin knee or a different J3 seat family. The plain neck at wd ~36 cannot sit in band under O20.
- Do not spend more on the crest basin under O20.

## Audit (2026-10-16, adversarial auditor)

Verdict: the death STANDS. The tail sweep costs 9.3 points, and the plain J3 side (neck 0.23, link 2 0.33 in band) keeps in-band at 0.67. Both were measured and reproduced.

- **Reproduced.** The claimed best params through `geneva-tail-knuckle-3r.py check` on Bench(60,160) fast give gap 39.34 (claim 39.36): reach 0.825, follow 0.95, in-band14 0.673, contact 0.091 and minimum metal 1.11 mm. The drive is the beside embodiment; the law runs th 101.96 -> 136.63 and ends on m3e. Overhead: 6 of 17 taken.
- **Convergence gate.** I ran it on the 9416 honest CMA tries. Excluded: the SENSED reference, the gate-objective search and the +100 penalised entries. Results:
  - the best gained 0.80 score points over the second half (limit < 1);
  - it gained 0.23 over the last third (limit < 0.5);
  - the top 5 lie within 0.01 points.
  
  The sweep is CONVERGED. The plain sweep-order reading also includes the LHS and gate entries; that reading gives 0.80 / 0.77, because the streams are interleaved.
- **Model read.** I checked the contact law (pressure angle, lift-off, rate, m3e / msub), the tail / roller / lug metal and the no-drive penalty against the kit-rule A parent. None of them shows a bug or an over-strict check. The roller-lug contact is exempted from K6 near D, which is optimistic, not strict.
- **Parameter coverage.** The J3-side options were searched:
  - inv3 = 1: 5795 tries, best 41.5 (reach 0.71, neck 0.69, link 2 0.78);
  - inv3 = 0: best 39.39.
  
  The crest basin is closed by the O20-only rule.
- **Upper bound.** With the sensed law and no tail (4 active, reference only), the same chain scores 30.03 fast. That is still behind H1 (24.48 verified) and minarc B (18.45 frozen). Removing every honesty cost would not make this a leader.
- **Note on the task's stale criterion.** The template's "within 10 of 68.93" bar would be met trivially (39.34 < 68.93). The death is judged against the verified leaders, not the round-1 champion.

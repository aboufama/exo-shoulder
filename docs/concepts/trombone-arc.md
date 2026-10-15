# Trombone arc (trombone-arc)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the band as a surface of revolution
   about p2 only where it actually passes the guide; the band end that never enters the guide is a free skin-fitted
   connector. Pick the axes (b, W, A1, A2) so the skin under the band's sweep is as uniform in radius as possible
   (a constant-radius band can only be in band where the skin under it is within 12 mm of its highest point), and let
   A1 = A2 so the band circle runs straight into the J3 hub with no separate link. Size the band ends from the guide
   positions the poses really need, and accept a few poses rather than a 90 mm tail.
2. **Rawest material.** The posed skin of every bench pose (Bench(60,160) grid SDF of the rig skin, K3 march along each
   metal ray), the fit-clip frames in time order (continuity along the interpolated motion), the everyday workspace
   poses. Not the digested baseline scorecard.
3. **Methods and tools.** tools/concept_kit.py: K1 two-circle closure (closed form), K3 march for undersides, K4 O20
   hub, K5/K7 straps and BOTTOM neck, K6 part-part collisions, K2 dense continuity; per-pose guide azimuth from the L2
   frame; sweep coarse (axes, A1/A2, arc range, band quantile) then refine around the best.
4. **What other than me shows the number is right.** The bench (B.report via K.evaluate, honest audit on), the
   adversarial verifier, and a red-team pose list (overhead, across-body, behind-back, the pose of the longest tail,
   the pose of closest band-to-skin and closest band-to-arm) reported below.

## Verdict: dead (honest best gap 91.57 against the champion's 68.93; not worth a GPU sweep)

All numbers below use Bench(60,160) on the fast grid cache with the kit's honest checks: K3 march, K2 dense
continuity, K6 collisions, a clean audit, and q 0.95 like the baseline. The sweep covered 133 configurations
(`docs/concepts/sweeps/trombone-arc.json`, in order). 37 of them are honest and non-degenerate. Model:
`docs/concepts/models/trombone-arc.py`, rebuilt on `tools/concept_kit.py`. The partial model from the interrupted
session was replaced, because it used its own fit and checks.

| configuration | gap | reach | follow | in-band 14 | in-band 10 | contact | note |
|---|---|---|---|---|---|---|---|
| spec as written: champion axes, KAA15XL0 ring, single-stage band | 192-275 | 0.03-0.30 | 0.03-0.45 | 0.17-0.21 | | | band at 400 mm (tail inside neck/head), ring at 68-103 mm |
| single stage, O20 hub J1, b lateral-posterior | 91.33 | 0.78 | 0.90 | 0.23 | | 0.077 | **degenerate**: band at 400 mm, 1.7 kg, sparse-sampling audit. Rejected |
| 2-stage telescoping, b bvec(60,30) | 106.29 | 0.76 | 0.82 | 0.20 | 0.09 | 0.095 | first honest one |
| **2-stage telescoping, b bvec(45,25), goff 15, A1=A2=90** | **91.57** | 0.744 | 0.917 | 0.286 | 0.108 | 0.112 | best (k 130) |

In-band 14 per member in the best configuration: guide 0.76, neck 0.70, hub3 0.65, hub1 0.17, arm1 0.14, sleeve
0.024, band 0.001, connector 0.0. The sleeve's skin face sits at 97 mm and the band at 100 mm. The arc spans
147 deg (248 mm at that radius), and the tail past the guide runs 12-109 mm. Ti mass is 179 g. The closure residual
is 0 and the minimum closure margin 26 deg. K2 found 2 flips.

## The measured limiter (rawest material: the posed skin along the band's own path)

A rigid band that slides through ONE guide must be a surface of revolution about p2, so it sits at a single radius R_a
from GH. In the L1 frame it occupies +-(J2 range + guide) around the guide. The K3 requirement along that circle,
taken over all closing bench poses, is in the table below. s is the offset from the guide in deg; + is the tail side,
away from the arm.

| axes | s = -70 | -30 | -10 | +10 | +30 | +50 | +70 | +90 |
|---|---|---|---|---|---|---|---|---|
| champion b (el 81), p50 | 53 | 44 | 47 | 53 | 64 | 80 | 88 | 102 |
| champion b, p95 | 72 | 51 | 50 | 54 | 144 | 400 | 400 | 400 |
| b bvec(90,40), A=90, p80 | 67 | 58 | 55 | 54 | 55 | 56 | 64 | 105 |
| b bvec(90,40), A=90, p95 | 74 | 64 | 59 | 68 | 93 | 97 | 97 | 400 |

The J2 range is at least the range of the b-W separation: 77 deg on the clips and ~150 deg on the workspace
(minimal with A1 = A2 = 90 deg). So in overhead poses the tail has to run 90-140 deg past the guide, and from
+30-50 deg on the skin under it climbs from ~50 mm to the trapezius, neck and head (400 = no exit within 220 mm).
A single-stage band therefore has to float above the head, or every pose touches.
The 2-stage telescoping arc (the spec's variant) halves the tail. It is the first realisation that fits at all,
but its sleeve still has to clear the highest trunk skin it sweeps over (97 mm), against skin at 45-60 mm.
That is the same limit as the 3R links ("a rigid part clears the highest skin it ever passes over"), made worse,
because a sliding arc passes over MORE skin than a link: its own length plus its stroke.

Spec corrections (measured):
- The KAA15XL0 ring at the S-top: its 52 mm footprint fits at 68-72 mm (per-pose max 59-103 mm). The arm rises over
  the acromion overhead and the trapezius rises medially. The band must then pass 15 mm over it. An O20 hub at b
  with the guide offset 15-22 deg across the band (on an L1 strap) is better, and was used for the best result.
- The arc ends must be constant params (the band is one part). Deriving them per evaluation from all poses breaks
  pose locality. They are set from the guide-azimuth percentiles before the build.
- A band quantile below 1 per sample does not trade a few poses: each tail sample is inside the body in different
  poses, so nearly every pose becomes a contact pose (qb 0.8 gives gap 275).

## Red team (best configuration)

- Pinch / contact: ws plane -15 elev 75 axial -45 (the sleeve 19.7 mm inside the body); ws plane 30 elev 150 axial 0 (the band 16.3 mm
  inside); ws plane -15 elev 75 axial 90 (the sleeve 13 mm inside); ws plane 0 elev 150 axial 0 (the guide 10.8 mm inside).
- Jam / branch: clip plane 77-78, elev 141-143, axial -67 (overhead with strong internal rotation) is dropped by dense
  K2: a joint axis jumps more than 25 deg per 2 deg step near the closure's edge.
- Overhead (elev >= 140): 13 of 17 taken. Lost: the 2 clip frames above, plus ws plane 45-60 elev 165 axial -90.
- Not modelled, and conservative to leave out: the sleeve's upper wall and the guide's upper roller cap (not
  skin-facing, above the band), the 2:1 cable pulleys (inside the sleeve section), and the guide arms' 4 mm bridge to
  the ring (ring variant only).

## What predicts beyond this morphology

- Any rail or arc that slides through a fixed-size carriage is a constant-radius body over its whole length PLUS its
  stroke. Its in-band ceiling is set by the highest skin in that swept region (here the trapezius/neck, 80-400 mm).
  Sliding realisations only pay off where the swept skin is near-spherical about GH: the deltoid cap
  (humerus-fixed) and +-30 deg around the acromion. They do not pay off on the trunk side.
- Measured tail map: from the S-top, skin under a GH-centred circle stays within 50-60 mm only up to ~+30 deg toward
  the trunk (champion b). A lateral-posterior b (bvec(90,40)) extends this to ~+50-70 deg (p80).
- A1 = A2 = 90 deg minimises the J2 stroke (equal to the separation range). The champion's 77/67 deg costs 120 deg
  of stroke on the clips instead of 77-96 deg.

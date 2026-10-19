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

## Verdict: dead (honest best gap 88.29 against the champion's 68.93; not worth a GPU sweep)

All numbers below use Bench(60,160) on the fast grid cache with the kit's honest checks: K3 march, K2 dense
continuity, K6 collisions, a clean audit, and q 0.95 like the baseline. The sweep covered 144 configurations
(`docs/concepts/sweeps/trombone-arc.json`, in order). Only k >= 133 lay the band out at its fitted radius; the others
lay it out at Rn 56. For a band fitted at 97-131 mm, that samples it 2-4x too sparsely, and those rows read up to
7 points too good (k 130: 91.57, re-laid at its true radius: 97.47). The row quotes only true-radius configurations. Model:
`docs/concepts/models/trombone-arc.py`, rebuilt on `tools/concept_kit.py`. The partial model from the interrupted
session was replaced, because it used its own fit and checks.

| configuration | gap | reach | follow | in-band 14 | in-band 10 | contact | note |
|---|---|---|---|---|---|---|---|
| spec as written: champion axes, KAA15XL0 ring, single-stage band | 192-275 | 0.03-0.30 | 0.03-0.45 | 0.17-0.21 | | | band at 400 mm (tail inside neck/head), ring at 68-103 mm |
| single stage, O20 hub J1, b lateral-posterior | 91.33 | 0.78 | 0.90 | 0.23 | | 0.077 | **degenerate**: band at 400 mm, 1.7 kg, sparse-sampling audit. Rejected |
| 2-stage telescoping, b bvec(60,30) | 106.29 | 0.76 | 0.82 | 0.20 | 0.09 | 0.095 | first honest one |
| 2-stage telescoping, b bvec(45,25), goff 15, A1=A2=90, laid out at Rn 56 | 91.57 | 0.744 | 0.917 | 0.286 | 0.108 | 0.112 | k 130: band sampled too sparsely. Re-laid at Rn 97: 97.47 |
| **2-stage telescoping, b bvec(45,30), goff 22, A1=A2=90, band quantile 1.0, Rn 106 (true radius)** | **88.29** | 0.775 | 0.900 | 0.279 | 0.102 | 0.087 | **best (k 143)** |

In-band 14 per member in the best configuration (k 143): guide 0.84, hub1 0.81, neck 0.68, hub3 0.62, arm1 0.52,
connector 0.009, sleeve 0.001, band 0.0. The band sits at 110.6 mm. The arc spans 130 deg (233 mm at that radius),
and the tail past the guide runs 1-101 mm. The guide's skin face is at 60 mm, so the guide is a ~50 mm pedestal under
the sleeve. That is real metal; its mass is not counted. Ti mass is 138 g. The closure residual is 0 and the minimum
closure margin 28 deg. K2 found 2 flips, and K6 removes 0.5 % of the poses.

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
but its sleeve still has to clear the highest trunk skin it sweeps over (106-110 mm), against skin at 45-60 mm.
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

## Red team (best configuration, k 143)

- Pinch / contact: ws plane 15 and 30, elev 150, axial 0: the connector is 26 / 22 mm inside the body (overhead, where
  the band's arm-side end meets the hub). ws plane 0 elev 150 axial 0: the band is 16.8 mm inside. ws plane -15 elev 105
  axial 45: hub1 is 5.5 mm inside. ws plane 75 elev 165 axial -90: hub3 is 3.9 mm inside.
- Jam (part-part collision, K6): ws plane -15 elev 75 axial -45.
- Branch / continuity: clip plane 77-78, elev 141-143, axial -67 (overhead with strong internal rotation) is dropped by
  dense K2.
- Overhead (elev >= 140): 14 of 17 taken. Lost: the 2 clip frames above and ws plane 45 elev 165 axial -90.
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

## Audit (2026-10-15T19:46:15Z, independent re-measurement)

Verdict: **the death stands**. The measured reason is that the telescoping sleeve and band are 53 % of the metal samples
(898 of 1684), and both are 0 % in band, because they must sit at R_a 110.6 mm to clear the highest trunk skin they sweep over.

- **Reproduction.** k 143 re-run on Bench(60,160) (fast cache, K3 march, K2 dense, K6, audit clean) gives gap 88.29,
  reach 0.775, follow 0.900, in-band 14 0.2793, in-band 10 0.102 and contact 0.0872. Every value is identical to the row.
- **Conventions.** The model is built on tools/concept_kit.py, which reproduces the baseline row exactly (KIT.md). The
  kit's honest checks score the champion at 70.27 rather than 68.93. That is a 1.3 point stricter reference, and it
  cannot explain an 18 point deficit. I found no modelling bug in axes/closure, the guide-on-band range test, the
  sleeve/band ramps or the arc range.
- **What a fix could buy.** If the sleeve and band were removed from the count, the remaining members are 60 % in band,
  which would give gap of about 56. So the whole verdict rests on the band radius. The tail map in this file (skin
  climbs from 50 mm to 90-400 mm within +30-50 deg past the guide) explains that radius. Raising the band quantile or
  the layout radius does not change it.
- **Missed-region probe** (src = arc-end percentiles, Rn = layout radius; the 80 mm rows are sampled sparsely and so read too well):

| src | Rn | gap | reach | follow | in-band 14 | contact | R_a |
|---|---|---|---|---|---|---|---|
| p5-95 | 106 | 88.29 | 0.775 | 0.90 | 0.279 | 0.087 | 110.6 |
| p10-90 | 106 | 101.61 | 0.681 | 0.85 | 0.288 | 0.086 | 105.6 |
| p10-95 | 106 | 94.49 | 0.750 | 0.85 | 0.286 | 0.081 | 110.6 |
| p25-75 | 106 | 147.37 | 0.419 | 0.55 | 0.390 | 0.083 | 79.6 |
| p5-95 | 80 (sparse) | 84.9 | 0.775 | 0.90 | 0.313 | 0.087 | 112.6 |

  A shorter arc lowers the band only to about 80 mm, still about 25 mm over the skin, and it loses reach and follow
  faster than it gains in-band share.
- **Minor issues found** (none would revive the design). (1) src p15-85 and p5-80 return gap 275 with reach = follow = 0.
  That looks like a degenerate fit when the arc misses the clip guide range; it should be reported as "no taken
  frames", not scored. (2) The guide's ~50 mm pedestal under the sleeve is not modelled as metal and its mass is not
  counted. This flatters the design. (3) Rows k < 133 laid out at Rn 56 are sampled sparsely (already noted above).

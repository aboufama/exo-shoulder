# Annular-ring 3R (annular-ring-3r)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Test the premise before the design:
   measure whether the skin under each joint's axis pierce point really is a dome over the whole motion (the bore
   only pays if the highest skin under the footprint is near the axis). Measure every joint against its own O20 hub
   (the A/B twin, per joint, same chain and same checks) instead of all-or-nothing. Put the strap roots where they
   physically are (a lug at the ring's race level, as a 3-D point, not a radius), check the bore and outer walls for
   contact, and treat the ring zone (both races and the roots) as the joint-partner zone for part-part clearance.
2. **Rawest material.** The posed skin itself (signed distance on every bench pose, fast grid cache), marched along
   each joint axis at every annulus sample (no digested summaries); the six fit clips walked by the kit's dense
   continuity; `pipeline/conformal/analysis/skin_motion_map_14.json` and the J1 seat obliquity map of the sibling
   back-anchored-ring-3r doc for where a GH-centred ray meets the skin square.
3. **Methods and tools.** `tools/concept_kit.py` (K1 two-circle closure, K3 per-sample march, K4-style flat fit of
   the annulus along its own axis, K5 straps with the 60 deg climb, K6 collisions with the ring partner zone, K2 dense
   continuity, audit); vectorised sweeps on Bench(60, 160), fast grid cache, coarse then refined; a per-annulus
   height profile of the skin along each axis to test the dome premise directly.
4. **What other than me shows the number is right.** The bench (the same scoring as the 68.93 baseline row), the
   kit's honesty audit, the in-model twin (all three O20 hubs: reproduces the kit template's 69.29 exactly), the
   adversarial verifier on the exact path / full bench, and a red-team pose list (rest, overhead, across-the-body,
   behind-the-back) with the part that pinches per pose.

## Model (docs/concepts/models/annular-ring-3r.py, on tools/concept_kit.py)

Spherical 3R with the baseline champion's axes (`concept_baseline.CHAMP`; the spec's A2 81.45 is not the champion's
66.75, corrected). 3 ACTIVE (the three ring angles), 0 PASSIVE; J2 by the K1 closure on branch -1, K2 dense
continuity along the six fit clips. Per joint either a **flat open-bore ring** (Reali-Slim KAA 4.76 section housed 9 x
8 mm, lower race housing = proximal member, upper = distal at + 4; KA 6.35: 10.6 x 9.6, split 4.8; underside on a
2 mm grid + both edge circles, fitted along its own axis like a K4 hub) or the **O20 twin** (kit K4 hub), so every
ring is measured against its own hub in the same chain. Straps (12 x 3) start at the ring rim + a 2 mm lug, at the
race level as a true 3-D point (two passes: the strap roots use the ring level of the first pass; h_err 0 on every
config). Neck: 14 x 6 to BOTTOM's bar from the J3 rim. Bore and outer walls checked for contact on every taken pose.
K6: the kit rule, with the joint-partner zone of a ring = its outer radius + lug + 2 mm (the O20 analog is 12 mm;
without it every strap root on its own ring is a false collision).

**Variant (the deeper version): skirt.** The lower race housing belongs to the proximal member, which does not
rotate relative to it, so it need not be flat: `skirt=1` extends it down to the skin as a 2 mm contoured shell fixed
in the proximal frame (J1: scapula, J2: link 1, J3: humerus), K3 per-sample underside, walls from its edges up to the
ring plane checked for contact.

## Results (Bench(60, 160), fast grid cache, K3 march, K2 dense, K6 on, audit clean; 55 configurations, in order, in
`docs/concepts/sweeps/annular-ring-3r.json`)

| k | configuration | gap | reach | follow | in-band 14 | in-band 10 | contact |
|---|---|---|---|---|---|---|---|
| 0 | twin: three O20 hubs, q 0.95 (= kit template) | 69.29 | 0.7625 | 1.000 | 0.4568 | 0.2975 | 0.1122 |
| 1-4 | ring at J1 only, bore r 12.7 / 19.05 / 25.4 / 31.75 | 79.8 / 96.6 / 99.2 / 98.0 | | | | | |
| 5-8 | ring at J2 only, same bores | 76.1 / 81.8 / 83.6 / 86.3 | | | | | |
| 9-12 | ring at J3 only, same bores | 74.9 / 78.2 / 82.4 / 86.7 | | | | | |
| 13-16 | rings at all three (the spec) | 91.6 / 104.9 / 111.6 / 112.0 | | | | | |
| 38 | ring J1 r 12.7 + skirt, q 0.95 | 67.58 | 0.7438 | 0.9167 | 0.5349 | 0.3917 | 0.1212 |
| 54 | twin, q 1.0 | 65.05 | 0.9062 | 1.000 | 0.2495 | 0.1575 | 0.0 |
| **52** | **ring J1 r 12.7 + skirt, hubs at J2 / J3, q 1.0** | **57.81** | 0.8875 | 0.9167 | 0.3728 | 0.2933 | 0.0051 |

Fitted levels (mm from GH along the axis): J1 hub 54, ring r 12.7: 58, r 19.05: 100, r 25.4: 109, r 31.75: 117; J2
hub 104.8, rings 111.8-118.4; J3 hub 66, rings 68-68.8. Section 6.35 (k32, k33), strap width 10 / 14 (k34, k35) and
the axes +-10 deg (k36, k44-49, ring at J3) do not change the picture (best 70.58 with el +10).

## What the bore does, measured

* **The dome premise fails at every joint.** A flat annulus must clear the highest skin under its whole footprint
  in every fit pose. At J1 the trapezius / neck rises medially within 19-28 mm of the pierce point (the ring stands at
  100 mm where the hub stands at 54). At J2 the axis wanders over the scapula and the trunk, so the max over poses is
  set by poses whose bulge is not centred on the axis (ring 112-118 vs hub 105). At J3 (lateral deltoid) the skin
  really is a dome (ring 68 vs hub 66) - and that is where the flat ring's outer half floats above the falling flanks
  (in-band 0.19-0.37 vs the hub's 0.60). A flat ring loses either way: off a dome it stands higher, on a dome its rim
  floats. The 4.25 mm it saves on the stack is not scored (crowns are not sampled) and the upper race split (4 vs
  3.15) and the rim offset put the distal strap roots higher than on a hub.
* **The skirt is what wins, not the bore.** k52 beats its own twin at the same q (65.05) by 7.2 points only through
  skirt 1 (98.5 % in band, scapula-fixed, the skin under it barely moves in the scapula frame). hub 2 is at 161 mm
  (0 % in band) and link 1 / link 2 are 0.2 / 1 % in band in that config: the 3R limiter (rigid links over the
  highest skin they pass) is untouched. In-band is a share of samples, so skin-hugging metal anywhere raises it.

## Red team (k52)

| pose class | bench poses | taken | lost: no closure / continuity | lost: part-part | contact |
|---|---|---|---|---|---|
| rest (elev < 25) | 58 | 58 | 0 | 0 | 0 |
| overhead (elev >= 140) | 17 | 11 | 3 | 3 | 0 |
| across the body (plane >= 100) | 38 | 35 | 2 | 0 | 1: the J1 bore wall, -0.4 mm, at plane 150 / elev 120 / axial -60 (the trapezius rises into the bore) |
| behind the back | 20 | 15 | 5 | 0 | 0 |
| other | 87 | 78 | 5 | 4 | 0 |

The pinch is the bore wall itself: the skin the bore was meant to swallow rises into it across the body. The jams
are the closure margin overhead / behind the back (the champion's) and K6 part-part clearance overhead (3 of 17; pair not broken down in this run).

## Verdict

Screened. Best honest gap 57.81 (k52) vs 68.93 baseline and 65.05 for its own O20 twin at the same q, but the open
bore loses to the O20 hub at every joint and every bore size (stage A); the gain comes from the skin-contoured
skirt under the J1 ring, which any design can put under its base-side joint. Not worth a GPU sweep of ring sizes;
worth transplanting the skirt (a skin-hugging lower housing on the proximal member of J1) to the champion and
sweeping the champion's axes with it.

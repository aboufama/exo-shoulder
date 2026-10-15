# Proximity (R1): where the covered skin is lost, and which levers move it

Agent D, 2026-10-15 10:45-11:40 UTC. Design: the final `cad_r18_n3_s1392_1_f300` (R1 40.9 % at 2-14 mm, R1-aim 19.1 %,
R3 79.8 %, R16 46.7 %). Every number below comes from an outside judge or the band evaluator, never from opinion.
Measurement changes are marked **[measurement]** and are not design progress.

Tools (all new, `pipeline/conformal/analysis/`):

| file | what it measures |
|---|---|
| `r1_decompose.py` | the R1 judge itself (score_design.py's skin samples, metal samples, covered-skin rule and clip weighting, reproduces R1 41.0 % vs the judge's 40.9 %) with every covered skin point tagged by part, hub / ribbon zone, gap class, clip, elevation, trunk vs arm skin; too-far gaps split into *slack* (the metal could come down that far and still clear the skin by 2 mm in every followed frame) and *motion* (the rest: the skin under a rigid part moves away from it); `lowered` = R1 if every metal point sat at its own worst-frame 2 mm (an upper bound for any reshaping on this path). `WS_STEP=12` adds the workspace poses' clearance. |
| `proximity_variants.py` | the band evaluator on CPU (cached clip maps), one lever at a time, per sample class (ribbon of each link, lower hub of each joint, BOTTOM's hub, neck, tab): in band achieved / ceiling (inband_ceiling.py's bound), lift over the lowest legal underside, radial skin motion under it. `FILL_HOLES=1`: maps with the pole holes filled. |
| `map_holes.py` | the evaluator maps' sampling holes near the pole and the fill; `band_impl_fill_holes.patch` = the same fill for band_impl.py (job key `fill_holes`) |
| `skin_motion_map.py` | for a part fixed in the humerus frame (BOTTOM's JN hub) or the scapula frame (base hub): radial skin motion and in-band ceiling per direction (point and flat O23 disc), fit clips only |
| `local_w_search.py` | CPU local search of the chain with the JN axis W boxed on low-motion skin vs free |

## 1. The R1 judge, decomposed (cad_r18_n3_s1392_1_f300, 2-14 mm, frame step 6)

**Nothing is too close: 0.0 % of the covered skin is under 2 mm. Every lost point is too far.** Gap histogram of the
covered skin: 2-14 mm 41 %, 14-22 mm 25 %, 22-30 mm 12 %, 30-60 mm 22 %.

| part / zone | share of covered skin | in band | lost (pts of R1) | too-far excess median | of it: slack + motion (mm) | lowered |
|---|---|---|---|---|---|---|
| link 1, J2 hub zone (lower plate of J2) | 18.5 % | **0.7 %** | 18.4 | 20.6 mm | 9.6 + 12.2 | 5.3 % |
| link 2, ribbon | 18.6 % | 13.7 % | 16.1 | 7.3 mm | 3.3 + 4.6 | 34.4 % |
| BOTTOM + neck + JN hub: hub zone | 19.5 % | 60.8 % | 7.6 | 5.0 mm | 4.8 + 10.4 | 84.8 % |
| BOTTOM + neck + JN hub: neck / bar | 14.7 % | 35.4 % | 9.5 | 4.9 mm | 2.7 + 3.4 | 54.4 % |
| base, J1 hub zone | 12.1 % | 81.7 % | 2.2 | 18.3 mm | 7.8 + 12.0 | 82.3 % |
| link 1, ribbon | 9.2 % | 72.9 % | 2.5 | 2.1 mm | 1.9 + 0.8 | 87.3 % |
| base, ribbon / tab | 5.5 % | 84.3 % | 0.9 | 1.3 mm | 2.6 + 5.8 | 96.7 % |
| J3 washer A (arm side) | 1.3 % | 2.1 % | 1.3 | 7.2 mm | 7.6 + 5.0 | 70.9 % |
| **all** | 100 % | **41.0 %** | 59.0 | | | **56.2 %** |

- **Three zones carry 87 % of the loss**: the J2 joint (18 pts), link 2's ribbon (16 pts) and the arm-end part
  (BOTTOM's JN hub + neck, 17 pts). The base (J1) is fine: 82 % in band.
- **Even a perfect reshaping of every part on this joint path reaches only 56 %** (each metal point at its own
  worst-frame 2 mm, same followed frames). The other 44 points are *motion*: rigid metal over skin whose distance from
  it changes by more than the 12 mm the band allows (14 - 2). The J2 zone cannot be fixed by shape at all (5 % even
  lowered): J2 sweeps over skin whose radius from the GH centre runs 58-93 mm across the clips it follows.
- By skin: 77 % of the covered skin is trunk / scapula skin (35 % in band), 23 % arm skin (61 %). By elevation the
  worst band is 30-60 deg (26 % in band), not overhead (46 % at 120+ deg).
- Which frames hold the metal up (the frame setting each too-far point's clearance): Reach back pocket 36 %, Raise
  overhead 22 %, Reach a high shelf 20 %, **Wave 16 % (a held-out clip)** - see 5.

## 2. The evaluator view: per class achieved vs ceiling (CPU, clip poses, fit clips shape the design)

On CPU the evaluator has only the 8 clips' maps (`.cache/maps_s1.pt`); the shape is fitted to the fit clips without
the workspace envelope. Same design, same kinematics (pure 3R: one configuration per pose).

| | in band (G 14) | follow | ceiling |
|---|---|---|---|
| GPU, wsf payload (det2 #1, the CAD's input): workspace envelope shapes the links | 28.6 % | 83.2 % | - |
| CPU, clips only, raw maps | 58.6 % | 74.0 % | 78.5 % |
| CPU, clips only, holes filled **[measurement]** | 67.5 % | 74.1 % | 86.6 % |

Per class (CPU, filled, G 14): ribbon link 1 78.6 / ceiling 96.4 % (skin motion 10.8 mm); ribbon link 2 58.2 / 88.3
(18.1 mm); lower hub J1 98.4 / 98.4 (3.9 mm); lower hub J2 59.7 / 71.4 (20.3 mm); BOTTOM hub J3 41.8 / 70.5 (21.8 mm,
lift 6.1); neck 63.6 / 90.1 (21.7 mm, lift 5.6). The same ranking as the CAD judge: J2, BOTTOM's hub and link 2.

**The range-first fit is the largest single design choice against R1.** The hub faces the CAD builds come from the
wsf fit: J2's flat face 102.7 mm from GH, BOTTOM's zj4 85.8 mm. The clip frames the design follows need only 93.3 /
79.2 mm (the median frame needs 68 mm at J2); the clips-only fit puts them at 77.6 / 79.2 but drops frames (follow
74 % vs 83 %; Raise overhead 46 % vs 69 %). The CAD shows the same thing: `members_1.log` puts l1's J2 plate 9.6 mm
above its clip need. Lowering J2 / BOTTOM to the clip need is a trade against R16 (the workspace poses that hold them
up), not a free gain.

## 3. Evaluator measurement problem: holes in the skin maps near the pole **[measurement]**

`build_frame_maps` bins ~0.8 mm skin samples into 0.5 x 0.5 deg pixels and fills holes with the 1-ring only, but a
pixel spans 0.5 cos(lat) deg of longitude. Share of pixels with no skin (all 451 frames), cached -> filled:
lat 40: 9.4 -> 2.0 %, 60: 20.7 -> 2.1 %, 70: 37.5 -> 3.4 %, 80: 57.6 -> 5.8 %, 88: 86.8 -> 8.1 %. Exact ray casts on the
posed skin (450 hole pixels in 3 frames): the ray hits skin 40-70 mm out in 100 % of them (70 % in one band), and the
fill agrees with the exact distance to 0.14-1.14 mm median (p95 0.4-2.4 mm). Effects: no clearance constraint over
the top of the shoulder (LO = -1: metal may sit inside the skin there) and never in band there (CAP = G / cs). On this
design the J1 hub reads 61.6 % in band (raw) vs 98.4 % (filled); the whole design 58.6 -> 67.5 %. The search has been
steered away from the top of the shoulder for in-band and left unguarded there for clearance.
Patch for the lead: `pipeline/conformal/analysis/band_impl_fill_holes.patch` (`fill_pole_holes`, job key
`fill_holes`, part of the map-cache key; tested bit-identical to map_holes.fill on 40 frames). Deploy as a new
endpoint, re-evaluate the final as a measurement change before comparing designs.

## 4. Levers, one at a time (evaluator, CPU, clips-only fit; in-band at G 14 / G 10 vs baseline 67.5 / 51.7 filled)

| lever | in band G14 | G10 | note |
|---|---|---|---|
| hub_r 10 + v5 stack (O20, hub_up 7.1, cap_up 2.0) | +2.2 | +1.9 | the stack heights alone: 0.0 (they only enter collisions) |
| hub_r 8.5 (O17) | +4.1 | +3.4 | |
| lower hubs flat (relief 0) | -4.4 | -2.9 | the contoured underside is worth ~4 pts |
| **relief 3.65 mm = what the CAD can build** (members.py: skin side contoured only 6.5 - 2.85 mm below the face) vs the 11.5 the evaluator assumes | -2.6 | -1.8 | evaluator/CAD mismatch at the lower hubs (J1, J2) |
| hub margin 1.0 / 0.5 (design 2.8) | +1.0 / +1.3 | +1.6 / +2.0 | evaluator only: the CAD rebuilds the contour with its own 0.5 mm margin |
| links hw 4 / 3 (design 5) | -0.1 / -0.6 | -0.6 / -1.3 | raw maps; narrower links do not help proximity (they help mass and collisions) |
| ramp 70 / 80 deg (design 60) | +1.3 / +1.9 | +2.8 / +4.1 | raw maps; steeper hub-to-ribbon transitions (CAD fairness cost) |

All shape / hardware levers together are worth about +6-10 points in the evaluator. None changes the ceiling much
(78.5-80.6 % raw, 86.6-88 % filled): **R1 >= 90 % needs a different joint path, not better parts.**

## 5. Joint placement over low-motion skin (`skin_motion_map.py`, filled maps, fit clips)

- **Base hub J1** (scapula frame): radial skin motion 1.8 mm, point and flat-disc ceiling 100 %. Already right.
- **BOTTOM's hub JN** (arm-fixed, W = (71.4 deg, 4.8 deg)): on the deltoid belly, 23.4 mm of skin motion, point ceiling
  67 %, flat O23 disc ceiling **39.5 %**. The best arm-fixed spot for a flat O23 hub: **W ~ (112 deg, -15 deg)**, 22 deg
  above the perpendicular toward the acromion edge, 60 mm from GH: 12.2 mm motion, point ceiling 99.4 %, **disc ceiling
  94.1 %** (neighbours (106-114, -12..-21) all 90-94 %). Only 27.5 % of the humerus-frame directions with skin reach a
  90 % point ceiling (median motion 30 mm): the arm is mostly bad ground for a rigid hub.
- J2 rides on link 1 (moves against both the scapula and the arm): its path, not a frame, decides its motion (here
  20 mm, ceiling 71 %). A search term for it: the evaluator's per-sample skin motion (`proximity_variants.py`).
- CPU local search, W boxed at (100-120, -30-0) vs free (`local_w_search.py`, clips-only fit, filled maps; range not
  judged on CPU): see the results table in 7.

## 6. Other findings

- **Held-out leak in the CAD stage**: `fair_cad/envelope.py` shapes the links on every followed frame of every clip
  in clips.json, Wave and Walking arm swing included; the evaluator respects `fit_clips`. On the final, 16 % of the
  too-far skin sits under metal whose clearance is set by a Wave frame. Fix (owner of envelope.py): skip clips not in
  the input's `fit_clips` when collecting `self.frames`. This is a measurement / integrity fix, not a design change.
- The R1 judge is skin-centric: metal far from the skin covers more skin (the normal cone widens), so a stand-off part
  counts more than its size (l1's J2 plate, 23 mm across, covers 18.5 % of the covered skin at 35 mm).
- GH translation: the rig moves the trunk by -lift and rotates the scapula about GH, so in this rig the chain sees no
  GH translation; passive cuff slides cannot change R1 here (they matter for real bodies, R10 / R14).

## 7. Results still running at hand-off / not done

- `local_w_search.py` boxed vs free: see `local_w_search_wbox.json` / `local_w_search_wfree.json` (first 60 boxed
  evals: fit score 0.548 vs the baseline's 0.533, in band 75.0 % vs 67.5 %, follow 69.0 % vs 74.1 % - not yet a
  better design: it buys proximity with follow).
- Not run: the GPU search with W fixed on the low-motion spot (`wfix_cfgs.json`: r18 geometry at hub_r 11.5, range
  first, free_w false, w0 (112, -15), 41 warm seeds; AMPERE_24 on exo-band19, ~20 min + cold start, est. $0.22) - the
  launch was refused by the session's permission classifier, so no paid compute was used. No CAD was built: CAD
  confirmation of a relocated JN needs that search (or wsf maps on CPU) for its workspace numbers.

## Next levers, in order

1. Deploy the map-hole fill and re-score (measurement), then search with a proximity term that sees the path's skin
   motion (per-sample radial motion or the ceiling) and W seeded / boxed on the low-motion spot (112, -15).
2. A J2 path over low-relief skin (J2 is 18 points of R1 by itself and unfixable by shape on this path).
3. Build the deeper lower-hub contour the evaluator assumes (11.5 mm, members.py) or tell the evaluator the CAD's
   3.65 mm: either way the two must agree (2.6 points).
4. O20 / O17 hubs (+2-4 points), ramp 70-80 deg (+1-2), drop the held-out frames from the CAD envelope.

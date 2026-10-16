# j2-arc-sector-3r - spherical 3R whose J2 is a link-1 arc-rail sector with a link-2 roller carriage

Lens "round3: J2 as a short curved rail with a real carriage, on a fold-free axis layout", family "spherical 3R
(virtual-axis J2)". Model `docs/concepts/models/j2-arc-sector-3r.py`, sweep log `docs/concepts/sweeps/j2-arc-sector-3r.json`,
row `docs/concepts/rows/j2-arc-sector-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the rail as a *surface of revolution about the J2 axis that hugs the body*, not as the spec's flat ring
     normal to p2. A carriage rolling about p2 only needs its running edges to be circles about p2. A conical V-edge
     band tangent to the sphere around GH (a lathe-turned constant section revolved about p2, no loft) keeps the whole
     8 mm width at one distance from GH. The flat ring stands up to 8 sin(beta) mm proud across its width.
   - Ask where the rail and the carriage *may* live before sweeping. A rigid rail fixed in link 1 must clear the
     highest skin it ever passes over in link 1's frame. A carriage fixed in link 2 must do the same in link 2's frame.
     So build two ceiling maps on the cone about p2 (link-1 frame for the rail, link-2 frame for the carriage and link
     2's root) and put the rail where both are low.
   - Count the rail's real length: travel + carriage + 2 end stops + the tab where link 1 laps on. This is the
     spec's risk (2), and it decides the morphology (below).
   - Run the hub control at identical axes (the rail-elbow lesson) in the same file.
2. **Rawest material.**
   - The posed skin itself: the bench's signed-distance grids on Bench(60,160) (fast cache) and the exact path for
     Bench(110,360).
   - The motion clips (training split only).
   - The K3 march per ray in each frame, used for the ceiling maps (no digested atlas numbers).
   - pipeline/conformal/analysis/skin_motion_map_14.json and the proximity atlas only as cross-checks.
3. **Methods and tools.**
   - tools/concept_kit.py: closure, members, K2 dense continuity, K3 march, K4 hubs, K6 collisions, audit.
   - fold-sph3r.py's crown, near-touch, overhead and frozen big-bench harness, imported rather than copied.
   - Ceiling maps in the link-1 and link-2 frames (scratch script, numbers below).
   - The farm for the sweep (tools/cloud_run.py sweep) and CMA-ES (tools/concept_cma.py), with the convergence gate.
4. **What, other than me, shows the number is right.**
   - The bench (outside judge).
   - The hub control at identical axes, which reproduces the catalogue's 73.57 to the digit.
   - The frozen shape on Bench(110,360) exact.
   - The verifier's harness, and the red-team pose list (rest, overhead, across, behind; closest metal; crowns and
     tops of the rail and carriage).

## What it is (as modelled)

```
base -> J1 (O20 hub, axis p1 = S bvec(az, el)) -> link 1 (12 x 3 Ti strap) + RAIL SECTOR (one rigid body; link 1 laps
onto an 8 mm tab at one rail end on a 1.1 mm shim) -> J2 = the carriage rolling on the rail about the virtual axis p2
(two-circle closure a1 / a2; NO hub and NO metal at the J2 axis point) -> CARRIAGE + link 2 (12 x 3 strap bolted on the
carriage plate) -> J3 (O20 hub, axis p3 = HG wdir(wd, wa)) -> K7 neck 14 x 6 -> BOTTOM -> cuff
```

- **Passive translations 0, passive DOF 0, cuff slides 0**, 3 active joints (closure residual 0.0 deg).
- **J2 component.** A Ti-6Al-4V conical V-edge ring sector (8 wide x 4 thick), lathe-turned about p2 and cut to the
  sector, running edges ground at 90 deg. Its underside is a band of the cone tangent to the sphere about GH at cone
  half-angle beta about p2, at ONE distance rho from GH (fitted: the K3 march, max over the band and every fit pose,
  quantile q).
- **Carriage.** 4 MR63ZZ-based V-rollers (OD 6) on M3 shoulder pins, 2 of them eccentric (preload). They sit beside
  the rail edges: two strips 4-10 mm from the rail centre line, 16 mm long, flush with the rail underside, 4 mm tall.
  A 20 x 16 x 4 plate sits 0.6 mm over the rail top, 8.6 mm over the rail underside in all. J2 sensing is a multipole
  strip plus a hall sensor in the plate.
- **Rail length** = J2 travel + half a carriage + a 3 mm end stop at each end + the 8 mm tab.
- **Travel** = the central `cov` share of the carriage azimuths over the closing poses (design step, frozen with
  the parameters).
- **Spec corrected.** The spec's flat ring normal to p2 is replaced by the cone tangent to the GH sphere. The flat
  ring tilts beta against the skin across its width (8 sin(beta) = 4 mm proud at beta 30); the cone keeps the band
  at one level. Both are a constant section revolved about p2.
- **K6.** Every pair is checked except two:
  - the running pair (rail, carriage plate) and the bolted carriage-link 2 body, within 12 mm of the carriage centre
    (pseudo-joint `Wcar`; the 20 x 16 footprint's farthest sample is 11.4 mm out);
  - link 1 laps on the rail tab with 1.1 mm clearance by construction, so it holds the big-bench 1 mm radial rule.

  Link 1 bridges over the carriage plate (`over`, +1 mm) wherever it crosses the carriage path. Link 2 sits over
  the rail (+1), the plate (+0.6), link 1 (+1) and the neck (+1).
- **Extra checks** (`fold-sph3r.py` harness, imported):
  - hub crowns and walls are skin-checked;
  - the rail top (+4) and plate top (+8.6) are skin-checked;
  - near-touch: metal closer than 1 mm counts as contact;
  - overhead (elevation >= 140) is reported separately;
  - frozen shape on Bench(110,360) exact.

## Hub control at identical axes (the rail-elbow lesson)

Spec axes bvec(95.86, 65.21), a1 60 / a2 80, wdir(79.15, -13.37), sigma -1, q 0.98. The hub version (fold-sph3r
build) reproduces the catalogue's **73.57** exactly:

| reach | follow | in-band 14 | in-band 10 | contact | honest |
|---|---|---|---|---|---|
| 0.819 | 1.0 | 0.281 | 0.162 | 0.035 | yes |

Per member in band: hub 1 1.00, hub 2 0.05, hub 3 0.57, link 1 0.01, link 2 0.03, neck 0.77. On the other branch
(sigma +1) the hub version scores 89.72 and is not honest.

## Ceiling maps on the cone about p2 (raw skin, K3 march, q 0.98 over the closing poses; Bench(60,160))

A rigid part fixed in a frame must clear the highest skin it ever passes over in that frame. For every direction
(psi about p2, beta off p2) the map gives the q98 level and the share of closing poses in which that level is
2-14 mm from the skin. psi is measured from p1 in link 1's frame (rail) and from p3 in link 2's frame (carriage,
link 2's root).

**Spec axes, link-1 frame (rail).** One window, psi -48 .. +60 at beta 22-46, is 100 % in band at a level of
53-61 mm. Outside it lies a band psi ~ +80 .. +210 where the rail would sit inside the arm in some pose (level
"400" = never clears within 220 mm). The poses that cause it are the Raise-overhead frames (plane 30, elevation
125-150, axial -55 .. -60) and workspace plane 45 / elevation 135.

**Spec axes, link-2 frame (carriage).** The carriage window is chi = 36 .. 96 deg at beta 22-34 (100 % in band,
level 60-66). The spec's chi = +90 is at its edge.

**Fold-sph3r best axes** (bvec(28.3, 65.4), 83.5 / 62.9). Both maps are far worse: the link-1 frame is at most
0.7 in band at beta 52-58, and the link-2 frame at most 0.8.

**J2 travel.** The J2 angle ranges 104 deg (p2-p98) at the spec axes and 108 deg at the fold axes.

### The bound this sets (measured, not assumed)

The rail must span J2 travel + E, where E = 2 x (8 + 3) + 8 mm of carriage, stops and tab, i.e. 30 mm of arc at
radius rho sin(beta). The table gives the longest window (contiguous psi with every cell >= 0.9 in band), the
travel left after E, and the best share of closing poses that travel can serve (any chi places it).

| beta | window | E | travel left | share of closing poses served | x closure 0.90 = reach bound |
|---|---|---|---|---|---|
| 28 | 114 | 61 | 53 | 0.76 | 0.68 |
| 34 | 108 | 51 | 57 | 0.80 | 0.72 |
| **40** | 108 | 45 | 63 | 0.84 | **0.76** |
| 46 | 90 | 40 | 50 | 0.73 | 0.65 |
| 52 | 84 | 36 | 48 | 0.71 | 0.64 |

- Relaxing the window to cells >= 0.5 in band gives a bound of 0.81-0.82 (beta 46-52), which is the hub
  version's own reach.
- **A rail that is in band cannot also keep the reach.** At these axes its reach is capped at ~0.76 before hub 1,
  link 1 / link 2 collisions and contact take their share; R5 asks for 0.90.
- At beta 40 with a1 60, hub 1 also stands in the roller strips' path: the strips reach 49.5 deg off p2, and hub 1's
  edge is at 48.3 deg. K6 rejects 106 of 123 closing poses unless the rail rides over the hub crown or a1 grows.

## Round-3 screen (2026-10-16 02:05-03:20 UTC, restart after the container restart)

Model fix before the sweep: the rail's layout radius `r_lay` (which sets the angular length of the carriage, the end
stops and the tab, and the sample spacing) is now a fix point on the rail's fitted level (`r_lay = floor(level)`, up to
2 re-runs; a config whose r_lay stays above its fitted level is marked not honest). Before the fix every probe laid
the rail out at 60 mm while it was fitted at 100-140 mm: the stops and the carriage were 2x too short in angle and the
audit flagged sparse sampling.

### Coarse farm sweep (268 configs, Bench(60,160) fast, 3 axis families x rail / carriage / link-2 waypoint)

- Families: spec axes +-(az 85-110, a1 50-66, a2 70-90, ...), the fold-sph3r leader's axes +-, a wide random set
  (sigma +-1), and 18 anchors (spec and fold axes x beta 28/40/52 x chi 0/60/90). Half carry a two-segment link 2
  (waypoint w_psi / w_beta in link 2's frame, planform turn, no loft).
- **65 % of the configs: the rail never clears the skin** (fitted level 400 = some pose puts the arm through the rail's
  sector within 220 mm). Of the rest, the rail's level is median 125 mm, minimum 72 mm from GH.
- Honest configs: 49 / 268 (the rest: sparse sampling, i.e. the rail parked far out).
- **Best honest: k114, gap 71.53** (score 73.99): reach 0.838, follow 0.883, in-band 14 0.335, contact 0.021; near-1 mm
  gap 76.13; overhead (elev >= 140): reach 0.33, in-band 0.38. Axes bvec(23.4, 62.0), a1 85.0 / a2 63.0,
  wdir(98.3, -8.1), beta 19.7, chi 43.3, cov 0.96. Rail level 139 mm, 116 mm of rail.
- **In band per member over all 49 honest configs (max / p90 / median): rail 0.030 / 0.008 / 0.000, carriage
  0.002 / 0 / 0, link 1 0.51 / 0.29 / 0.02, link 2 0.26 / 0.11 / 0.04 (with a waypoint: second segment 0.45 / 0.22 /
  0.09)**, hub 1 1.0, hub 3 0.88 / 0.80 / 0.64, neck 0.93 / 0.85 / 0.77.

### Hub control at identical axes (the rail-elbow lesson)

At k114's axes (local re-run of the rail: 71.12) the hub version scores **57.75** (reach 0.869, in-band 14 0.451,
contact 0.030; hub 2 0.0, link 1 0.37, link 2 0.08). **The rail loses 13.4 gap points to its own hub control.** At the
spec axes: rail 84.81 (beta 40, chi 60) vs hub 73.57.

### Why (measured): the J2 rail is a body of revolution, so it lives at ONE level over J2's whole travel

- A carriage rolling about p2 needs running edges that are circles about p2: the rail is a constant section revolved
  about p2, at one distance from GH along its whole length. Its level is the highest skin it ever passes over in link
  1's frame, maximised over the whole sector.
- The sector must span J2's travel (104-108 deg p2-p98 at both axis families) plus the carriage, 2 end stops and the
  tab (30 mm of arc): about 150 deg at beta 40.
- The link-1-frame ceiling maps (raw skin, K3 march, q 0.98 over the closing poses): the longest window whose cells
  are >= 0.9 in band is 108 deg (spec axes, beta 34-40) and ~40 deg (fold axes, beta 64-70, right next to hub 1). A
  150 deg sector always reaches skin that rises 40-90 mm higher (or passes through the arm: level 400).
- The carriage and link 2's root inherit the rail's level (plate at rail + 4.6 mm, link 2 climbs down at <= 60 deg),
  so link 2 cannot use the link-2-frame window either: that map has 70-84 % cells at fold axes (psi -12..+48, beta
  46-64), but link 2 starts 60-80 mm above them.
- The hub needs ~23 mm of footprint at the J2 point; the rail needs ~150 deg of arc. A rail cannot beat the hub on
  in-band, and when its travel is cut to fit the window, reach falls (spec axes: an in-band rail caps reach at ~0.76).

### Red team of the best coarse config (k114, Bench(60,160))

- **The optimistic number.** The r_lay fix point is not unique: started at 60 mm the rail settles at 132-139 mm and
  scores 71.12-71.53; started at 132 mm it scores 72.20 (level 138.0). Spread ~1 gap point; the farm number (71.53)
  is quoted.
- **The point that pinches.** Closest metal 0.24 mm at workspace plane 60 / elevation 165 / axial -90 (overhead);
  0.56 and 0.71 mm at elevation 165 too. With metal < 1 mm counted as contact the gap is 76.13-76.80. Two hub crowns
  sit 4.1 mm inside the skin (those poses count as contact).
- **The poses that jam.** 34 of 160 workspace poses are not taken: 29 by the J2 fold / K2 branch flip (overhead
  plane 0-45 elev 135, axial -45; plane 105-120 elev 150-165 axial -90..-135), 4 by contact (elev 150 axial 0), 1
  by K6.
- **Named pose groups** (taken / total, in band 2-14): rest 5/5, 0.25; overhead 6/17, 0.38; across the body 29/36,
  0.21; behind the back 18/19, 0.36. **Overhead (elev >= 140): reach 0.33.**
- **Where the rail is.** Level 138 mm from GH, i.e. ~30 mm (median) off the skin in every pose; 0.0 in band. The
  carriage plate is at 142.6 mm. 120 mm of Ti arc rail and a 20 x 16 carriage, both out of band: the "no metal at
  the J2 point" idea moves metal off the worst spot onto a longer arc that is worse.

### The trade the rail actually offers (local probes, spec axes, beta 34, chi 90 = the rail centred in its window)

| travel share `cov` | rail in band | rail level | in-band 14 (all metal) | reach | follow | gap |
|---|---|---|---|---|---|---|
| 0.60 | **0.998** | 59 mm | **0.612** | 0.463 | 0.767 | 92.51 |
| 0.75 | 0.539 | 63 mm | 0.486 | 0.600 | 0.883 | 80.03 |
| 0.95 (beta 40, chi 60) | 0.001 | 104 mm | 0.245 | 0.750 | 1.0 | 84.81 |
| hub control (same axes) | - | - | 0.281 | 0.819 | 1.0 | 73.57 |

- **A rail inside its window is in band** (0.998 at 59 mm, and it lifts the whole design to 0.61 in band, twice the
  hub control's 0.28). This is the one real gain the morphology has.
- But inside the window the J2 travel is ~38 deg of the 104 the workspace needs: reach 0.46. Every degree of travel
  added beyond the window lifts the whole rail (one level), so in-band collapses before reach recovers. No point on
  this curve beats the hub control (73.57).
- At beta 40 the roller strips run into hub 1 (K6 0.79 of closing poses) unless the rail rides over hub 1's crown.

### Variants that would remove the limiter (reasoned, not built in this time box)

1. **Two-stage arc (half-speed cage).** A curved telescopic slide whose middle stage is driven at half the J2 angle
   by rolling contact (the roller cage of a crossed-roller way moves at exactly half the relative speed, no gear): each
   stage spans travel / 2 + its carriage, at its own level, in link 1's frame and in a half-angle frame. It halves
   the arc each rigid body needs (~75 deg each, inside the 108 deg window). Risks: no catalogue curved telescopic way at
   this size (custom), a third body at a third level, cage creep (crossed-roller cages walk without a rack - the
   cage's rack-and-pinion fix is a gear, MVP1 forbids it).
2. **Axes chosen for small J2 travel.** The sweep left axes free (az, el, a1, a2, wd, wa) and never found J2 travel
   below ~100 deg at reach >= 0.8: the workspace needs it.
3. **The rail in link 2's frame** (carriage on link 1): the link-2-frame windows are narrower (~60-70 deg at >= 0.7
   in band), so it is worse.

## Verdict (2026-10-16 03:25 UTC): DEAD - the rail does not beat its own hub control

- **Best honest (Bench(60,160) fast, kit checks + crown/top skin checks): k114, gap 71.53** (score 73.99; local
  re-runs 71.12 / 72.20 from different r_lay starts): reach 0.838, follow 0.883, in-band 14 0.335, in-band 10 0.23,
  contact 0.021; near-1 mm gap 76.1; overhead (elev >= 140) reach 0.33, in-band 0.38. 0 passive DOF, 0 passive
  translations, 3 active.
- **The hub version at identical axes scores 57.75**: the rail costs 13.4 gap points. At the spec axes: 84.81 vs 73.57.
- **Lead-note kill test:** link 2 never routes above 0.6 in band (max 0.26 over 49 honest configs; 0.45 for the second
  segment of a two-segment planform-turn link 2), because link 2 starts at the carriage, which sits on the rail's one
  level.
- **Convergence gate** (288 configs in evaluation order, score points): +0.15 over the second half, +0.15 over the last
  third, top-5 within 1.89 -> passes on the numbers. It is a weak pass: the history is a random coarse sweep plus
  probes. Eight CMA-ES streams (4 near full travel, 4 with the travel share free 0.5-0.9) were submitted to the farm
  (.cache/j2a/jobs_cma5.json) but had not returned at the time box. The first two waves failed in seconds: the worker
  had no `.cache/j2a/` directory for `--out` (the same bug lost the previous session's two CMA streams). The frozen
  Bench(110,360) exact run of k114 (.cache/j2a/jobs_big_k114r.json) was also still queued. No big-bench number is
  claimed.
- **The measured limiter, which predicts beyond this morphology:** any joint realised as a guided arc about a
  virtual axis (an arc rail, a curved guide, a slewing segment) is a body of revolution about that axis. It sits at ONE
  distance from the centre over its whole travel plus carriage, stops and tab (~150 deg for J2 here). It must clear
  the highest skin over that whole sector in its frame. The intermediate link frames of a spherical 3R have in-band
  windows of only 40-108 deg. A hub needs ~23 mm at the axis point; an arc rail needs the window. Inside the window the
  rail is perfectly in band (0.998 at 59 mm; whole design in band 0.61, twice the hub's 0.28), but the travel then
  covers ~38 of the 104 deg the workspace needs (reach 0.46).
- **What next (not this morphology):** the in-window result says a virtual-axis joint pays off only if its travel fits
  the frame's window. Pair it with a joint layout whose J2 travel is <= ~60 deg, or split the travel over two bodies
  (variant 1 above, if a gear-free half-speed coupling at this size exists). Otherwise keep the hub at J2 and work on
  link 2 (fold-sph3r, skin-normal-3r-pin-knee).

## Audit (2026-10-16 ~03:40 UTC, independent auditor)

- **Gate:** the 288-config history passes the gate's numbers only because the best was found early by the random
  coarse sweep and the rest were probes and re-runs; no CMA stream ever returned (the farm jobs were lost at the
  container restart, logs end at "upload done"). Worse, the best per cone half-angle band is monotone: beta 12-20:
  71.12, 20-30: 74.38, 30-45: 78.99, 45-76: 82.16, so the optimum sat at the `beta >= 12` clamp. That is not a real
  convergence.
- **Re-measured at the clamp** (Bench(60,160) fast, the model's own `evaluate`, all checks on; entries `audit-local` in
  the sweep): k114 axes, beta 13 -> 69.00; beta 12 -> 68.50; beta 12, cov 0.99 -> **66.30** (honest). chi 0 / 90 / 180 /
  -90 -> 75.6 / 74.6 / 84.5 / 79.4; s1 -1 -> 70.5; cov 0.93 -> 72.2; over_hub1 -> 68.5.
- **So the absolute number beats the 68.93 champion, but the rail adds nothing:** in each of these configurations the
  rail sits at 147-152 mm from GH, in band 0.0 (rail) and 0.0 (carriage) - a hoop parked about 9 cm off the skin. The
  gain is the re-tuned axes; the hub version at identical axes scores 57.75. The sweep walks toward beta -> 0, i.e.
  toward the hub, which is the rail's own limit with a smaller footprint.
- **Verdict: death upheld, on dominance, not on the absolute number.** Measured reason: an arc rail about the virtual
  J2 axis must stand at one level over a ~150 deg sector. Every configuration found so far either leaves the band
  (0 % in band at 147-152 mm) or trades the reach away. The best rail (66.30) still loses 8.6 gap points to the plain
  O20 hub at the same axes (57.75).
- Tooling note confirmed: the CMA farm jobs need `mkdir -p` for their `--out` directory.

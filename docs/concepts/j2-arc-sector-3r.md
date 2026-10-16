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

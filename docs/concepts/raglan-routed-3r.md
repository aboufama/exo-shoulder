# raglan-routed-3r - plain 3R whose links follow the lines of least skin motion (raglan seams), measured in the link's own frame

Model: `docs/concepts/models/raglan-routed-3r.py` (kit model; `check | parity | map | redteam | frozen` modes).
Sweep: `docs/concepts/sweeps/raglan-routed-3r.json` (coarse farm sweep + every CMA try, in order).
Scan tool (new): `tools/hub_band_scan.py` (three-hub band scan). Sister morphology (killed): `docs/concepts/far-end-posterior-3r.md`.

## Depth answers (before modelling)

1. **What a top pattern maker / orthotic fitter would do here.** A pattern maker never puts a seam on the shortest
   line between two points. Seams go where the cloth does not move against the body: the raglan seam runs from the
   neck to the underarm so the sleeve head never sits on the moving shoulder point; space-suit and BioSuit designers
   route their tension members along Iberall's lines of non-extension. An orthotist casts the limb in the positions of
   use, puts hinges on stable landmarks, relieves the prominences, and grades the pattern before cutting. Here the
   "garment pieces" are the two rigid links and the "seam ends" are the hubs. So: (a) MEASURE, in each link's own
   moving frame, which directions keep one skin distance over every pose the chain takes (the raglan map), and draft
   the link along the low-motion line with a planform turn (constant section, lines and tangent arcs, no loft);
   (b) GRADE the pattern before cutting: scan the whole layout space for places where all three hubs can be pinned in
   one 12 mm band (the three-hub band scan), instead of tuning the known layouts; (c) try the far end of every axis
   line as the hub seat (a bearing can sit at either end; sister morphology, killed).
2. **Rawest material.** The posed skin of every bench pose as the signed-distance grid (Bench(60, 160) fast; the
   verdict on Bench(110, 360) exact); the K3 requirement (2 mm clearance + 15 mm free window) along every ray of the
   link frame in every closing pose; the O20 disc's 9-point requirement along every candidate hub axis in every pose.
   The scapula / humerus skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) is the same quantity in
   the two body frames; links live in neither, so it is recomputed per link.
3. **Instrument.** The concept kit (K0-K7: exact spherical closure, flat O20 hubs with the 12.25 stack, straps with
   skin-fitted undersides and the 60 deg climb limit, K7 neck, K2 dense continuity, K6 collisions, honesty audit) +
   the verified fold-sph3r checks (hub crown / wall skin check, near-touch, overhead) imported, not copied; the raglan
   map (`map` mode); the three-hub band scan on the farm (130 546 layouts); CMA-ES on the farm
   (tools/concept_cma.py); the frozen large-bench protocol (fit on Bench(60, 160), freeze every underside, wear on
   Bench(110, 360) exact, K6 at 1 mm radial).
4. **Outside judge.** tools/concept_bench.py through the kit (the 68.93 baseline's poses and metrics); parity with
   `_template.py` to 4 decimals at e = +1, d = 0 (69.29 / 65.05) and with the fold-sph3r k2221 control (51.33); the
   kit audit (it flags links parked at 400 mm as sparse); the frozen Bench(110, 360) exact run; the adversarial
   verifier.

## Mechanism (every joint a real component, 0 passive DOF)

| element | component | envelope in the model |
|---|---|---|
| J1, J2, J3 (active R) | MR117-2RS bearing pair in an O20 hub (docs/HARDWARE.md v5 joint), axes concurrent at GH | flat O20 disc at the fitted level F, 12.25 mm stack F -> crown; crown + wall skin-checked |
| link 1, link 2 | 8 x 3 mm Ti strap (the osn leader's section), ONE planform turn per link: two great-circle legs hub -> W -> hub, the corner a tangent arc in the planform; constant section, no loft, no twist | skin-fitted underside per sample, <= 60 deg climb, hub ramps, link 2 over link 1 and the neck (+1 mm) |
| neck (arm-end) | 14 x 6 mm strap from hub 3 to BOTTOM's bar (K7) | as above |

The turn W = cos(d) slerp(h_a, h_b, t) + sin(d) n_ab is fixed in the link (n_ab = the normal of the link's own hub
plane), so the link is one rigid machined piece. No slide, no cuff translation: passive translations 0. Every joint
value is set by the closure (no undetermined coordinate). MVP1 unpowered: three pins + two bent straps.

## Raglan map (the measurement)

For a layout, every cell (t along the link, d off its great circle) of each link's frame gets, over the poses the
chain closes in: `top` = share of poses within 12 mm of the cell's own maximum need (what a q = 1 underside gets),
`ceiling` = the best 12 mm window (reachable with q < 1), `inf` = share of poses whose ray never clears the body.

| layout | link | great circle (top, mid-span) | best region | what it says |
|---|---|---|---|---|
| plain 3R k2221 (51.33) | link 1 (82.5 deg) | 0.02-0.46 | 0.60-0.68 at d +30..+40, t 0.35-0.65 | the straight link crosses the posterior acromion edge, whose distance swings > 12 mm; bowing it 30-40 deg toward the shoulder point keeps it over skin that rides with link 1 |
| | link 2 (65.4 deg) | 0.01-0.17 | 0.5-0.77 only near hub 3 (t >= 0.65) | the middle of link 2 is out at every d: link 2 is pinned up by hub 2 (F 145 mm), not by its route |
| champion axes (65.05) | link 1 | 0.36 (route mean) | 0.69 (route mean) | same: link 1 wants a 25 deg lateral bow |
| fold-free posterior bvec(-24, 4) | both | 0 (inf 0.1-0.2 almost everywhere) | - | links through the neck / chest in 10-20 % of poses (sister morphology killed) |
| graded layout G (below) | link 1 (40 deg) | 0.77 | 0.77 (straight is best) | |
| | link 2 (100 deg) | <= 0.2 beyond t 0.25 | ceiling 0.4-0.7 | the long link 2 runs down the deltoid to a low hub 3 |

## Coarse sweep and CMA (farm, Bench(60, 160) fast grid, honest kit checks)

- Coarse, 288 routes x widths at k2221's axes: great circle 51.33 (12 mm) / 48.20 (8 mm); best route 46.19
  (link 1 turned +35 deg at t 0.65, 8 mm): link 1 in band 0.37 -> 0.52. Link 2 untouched (0.05).
- CMA round 1, 4 streams (A, B from the coarse best at q 1.0 / 0.97; C wider; D from the champion's axes), 4108 tries,
  axes + routes free: **42.72** (stream D; A 43.86, C 43.60, B 44.16) - all streams in the same basin (J1 el 80-82,
  J3 wdir(93-96, -1..3), arcs 79-90 / 61-71, link 1 turned 30-48 deg).

Best (k3484, stream D): J1 bvec(8.6, 81.6), J3 wdir(94.2, -0.9), a1 79.7, a2 61.6, sigma -1; link 1 turned 38.1 deg at
t 0.79, link 2 straight (-1.7 deg); 8 x 3 straps; q 1.0.

| Bench(60, 160) fast | gap | score | reach | follow | in-band 14 | in-band 10 | contact | min metal-skin | gap (<1 mm = contact) |
|---|---|---|---|---|---|---|---|---|---|
| k2221 control (fold-sph3r, 12 mm, great circle) | 51.33 | 81.3 | 0.894 | 1.000 | 0.393 | 0.240 | 0 | | |
| raglan best k3484 | **42.72** | 84.5 | 0.869 | 1.000 | 0.504 | 0.293 | 0 | 0.98 mm | 43.85 |

Per part (clip poses): hub 1 1.00, hub 2 **0.00** (F 128 mm), hub 3 0.67, link 1 0.60, link 2 0.05, neck 0.65.
Crowns: 0 contact poses (min 0.98 mm). Mass 132 g Ti (166 g with 5.5 mm straps). Overhead (elev >= 140, 12 ws poses):
reach 0.50, in-band 14 0.53.

On the body (lowest-elevation pose): hub 1 on top of the shoulder (el 82), hub 2 behind it (az 168, horizontal, 128 mm
from GH), hub 3 on the lateral arm; link 1 does not drop straight down the back (great circle az 168) but bows out to
az 128 (posterior-lateral, over the posterior deltoid) before turning in to hub 2 - a raglan line.

Gate on the whole history (coarse + round 1, 4396 tries, score = 100 (1 - gap / 275)): best gained 0.32 score points
over the second half, 0.13 over the last third, top 5 within 0.03: **converged** in this basin.

## Three-hub band scan (grading the pattern)

`tools/hub_band_scan.py` on the farm (24 slices): 432 J1 lines x both ends, 408 J3 directions (whole sphere, so both
ends), arcs 30..130 x 30..130, both branches, hub 2 at either end of its line; the O20 disc's 9-point need along each
axis in every pose; a layout's hub band = share of poses within 12 mm below the max need over the poses it closes in.
130 546 layouts close in >= 60 % of poses.

- **Every leader's hub 2 is out of band (0 %) because its J2 ray sweeps the deltoid / acromion.** The scan finds one
  family that keeps all three hubs in band at once: J1 bvec(80-90, 64) (lateral, over the acromion), J3 wdir(40, 0)
  (40 deg off the humerus axis, lateral: hub 3 low on the lateral arm), a1 40-50, a2 100-110, sigma -1: hub 2 in band
  0.74 at F 65 mm, hub 3 0.70, hub 1 0.77 = closure 0.77 (the fold takes the rest).
- In the full kit model (layout G = bvec(80, 64), wdir(40, 0), 40 / 100): hub 2 0.74 (first plain 3R with hub 2 in
  band), link 1 0.87, but link 2 (100 deg, from the acromion down the deltoid to hub 3) 0.005 and reach 0.74:
  gap 73.99. The raglan map of link 2 shows no route that holds (top <= 0.2 beyond 25 % of its span).
- No far-end hub (e1 = -1 or e2 = -1) appears in the top 50.
- v1 of the scan used hub 2's centre ray only and read hub 2 at 0.88 / F 65; the kit's full disc put it at 83 mm
  (0 %): on sloping skin the O20 rim lifts a GH-ray hub by ~20 mm. v2 (the numbers above) uses the 9-point disc.

## Levers measured dead at the best (Bench(60, 160) fast)

- **Placing hub 2 (and link 2) lower and giving up the poses that lift them** (per-part quantile qh2 = ql2): 0.97
  49.63, 0.93 57.94, 0.90 62.11, 0.85 71.62 (vs 42.72). Hub 2 stays <= 9 % in band: its need is broad, not a few
  outliers (centre ray median 64, p95 109, max 120 mm; the O20 rim adds 4-12 mm: disc 68 / 121 / 128). At k2221 the
  same (disc 72 / 130 / 145). In the graded family G the disc need is 56 / 62 / 65: in band 0.97 of its closing poses.
- **Far-end hubs** (all 8 end choices, sister morphology): every far end lies in the torso, axilla or neck.

## Round 2 (CMA from the graded family + a 2-turn polish)

The first launch (01:55) was lost in the container restart (02:03; the batch client died with it). Relaunched 02:07
(`jobs_cma2`: E / F from the graded family G at q 1.0 / 0.97, G from a middle layout, H = k3484 + a second turn per
link, and the frozen big-bench wear of k3484). Measured afterwards: those batch jobs did not link the bench grid cache
(`link: [".cache/concept_bench"]`), so on the farm they run on the EXACT distance path (a pin-knee CMA generation
took 660-1060 s instead of ~20 s): their gaps are not comparable with the fast-grid numbers above and stay out of the
best and the gate (stage suffix `-exactpath`). The frozen wear is unaffected (its large bench is exact by design; its
fit then runs on the exact path too, the conservative side).

Outcome: E returned 1 generation (9 tries, best 114.19 on the exact path, graded family); F, G, H hit the 3000 s farm
timeout after their first generation. The graded family stays at 73.99 (fast, coarse) and is not pursued further:
the round-1 gate on the k3484 basin stands (converged).

## Frozen on Bench(110, 360) exact (lesson c) and red team

k3484, shape fitted on Bench(60, 160) and worn without refit on Bench(110, 360) exact (fold-sph3r's frozen protocol,
K6 at 1 mm radial; `.cache/raglan/big_rgD.json`; the fit, re-run on the exact path, reproduces 42.73):

| bench | gap | score | reach | follow | in-band 14 | in-band 10 | contact | gap, metal < 1 mm as contact | min metal-skin | crown contact poses |
|---|---|---|---|---|---|---|---|---|---|---|
| Bench(60, 160) fit | 42.73 | 84.5 | 0.869 | 1.000 | 0.504 | 0.294 | 0 | 45.00 | 0.77 mm | 0 |
| **Bench(110, 360) exact, frozen** | **50.06** | 81.8 | 0.803 | 1.000 | 0.504 | 0.295 | 0.0075 | 52.16 | 0.64 mm | 3 |
| straight links at k2221's axes (fold-sph3r, same protocol) | 57.99 | 78.9 | | | | | | | | |

So routing holds on the large bench: -7.9 gap points against the straight-link 3R, in-band unchanged by the transfer
(0.504 -> 0.504). The best plain spherical 3R (no passive DOF at all) is now 50.06 frozen; the pin knee (33.84) and
osn (42.59) stay ahead.

Red team (big bench):
* **The pose that jams**: 71 of 470 not taken - fold / K2 60 (e.g. plane 0, elevation 120, axial -15; the band of
  elevation 75-165 with axial -45..-15, and across-the-body plane 90-105 with axial -120..-150), K6 parts 8 (link 2
  over link 1 at plane -15..15, elevation 75-165, axial +15..+30), contact 3 (elevation 150-165 crowns).
* **The point that pinches**: 0.64 mm, ws plane 15, elevation 45, axial -75 (pose #220); 4 taken poses come within
  1 mm (gap 52.16 with them counted as contact).
* **Overhead** (elevation >= 140): reach 0.46 (13 of 28 workspace poses), in-band 0.56.
* **Optimistic numbers**: the fast-to-exact transfer costs 7.3 points (reach 0.869 -> 0.803: more fold poses on the
  denser bench); dilution 1.25 points (section above).
* Named groups (big bench): rest 5 / 5 taken (median 16.9 mm, in-band 0.39), overhead 23 / 38 (11.0 mm, 0.56), across
  42 / 78 (18.5 mm, 0.33), behind the back 34 / 40 (12.5 mm, 0.58). Hub 2 stays 0 % in band, link 2 5 %.


## Red team: dilution (the number that is optimistic)

In-band 14 is a share of metal samples, so a longer link that sits in band lowers the gap by diluting the parts that
do not (the annular-ring skirt artefact). k3484's link 1 has 340 samples routed against 245 straight at the same axes.
Weighted at the straight count, k3484 scores **43.97** (not 42.72); the same axes with straight links score 49.89. So
routing is mostly real here (+5.9 gap points: link 1 0.36 -> 0.60 in band) and 1.25 points are dilution. On the
leader (raglan-knee-3r) the ratio is the other way round: +0.45 real, +1.1 dilution.

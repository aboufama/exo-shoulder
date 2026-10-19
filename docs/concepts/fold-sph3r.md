# fold-sph3r - Spherical 3R on fold-frontier axes

Lens "fold-frontier", family "spherical 3R". Model: `docs/concepts/models/fold-sph3r.py`. Sweep log:
`docs/concepts/sweeps/fold-sph3r.json`. Row: `docs/concepts/rows/fold-sph3r.json`.

## What it is (the most buildable morphology)

* Three pins, each on a preloaded bearing pair in an O20 hub (docs/HARDWARE.md v5 joint: MR117-2RS pair, 12.25 mm
  from the lower member's skin face F to the crown). The three axes meet at GH.
* Link 1 and link 2 are 12 x 3 mm straps on great circles; link 2 passes over link 1 and the neck (>= 1 mm, K6 by
  construction).
* Member 3 is the arm-end plate + the 14 x 6 mm neck, rigid to BOTTOM's bar (K7).
* **Passive translations in the chain: 0. Cuff slides: 0. Liner compliance claimed: 0 mm.** On the bench the arm
  rotates about a fixed GH in the scapula frame (tools/concept_bench.py, origin = GH), so a spherical chain closes
  exactly (closure residual 0.0 deg). The real GH translation (R10) is not on this bench; when it is, it goes to the
  cuff slides the project already allows, outside the count.
* Every joint is a real component at its real envelope: the hub is the O20 v5 stack, sampled at its real size and
  fitted level (K4). There is no rail, carriage or slide to size.

The kinematics and members are `docs/concepts/models/_template.py` build() unchanged. The controls in the sweep log
reproduce the known numbers to the digit (Bench(60,160), fast grid):
- the template at the champion's axes: 65.05 at q 1.0 and 69.29 at q 0.95;
- the 3R at rail-elbow k1530's axes: 51.97;
- the 3R at rail-elbow k2221's axes: 51.33.

### Lessons carried, and what this model adds

| lesson | how |
|---|---|
| (a) real components, passive translations counted | 3 O20 hubs at the v5 stack; 0 passive translations, 0 cuff slides |
| (b) part checks on | K6 every member pair (incl. hubs at their 12.25 mm thickness and the neck), `over` for link 2, dense K2 continuity (2-deg steps, 25 deg jump rule on every joint value and axis), fold margin 10 deg (the jam rule of a 3R: J2 never within 10 deg of its fold), member 3 = hub 3 plate + neck rigid to BOTTOM, kit audit (hub size, sampling density, pose locality) |
| (d) crowns skin-checked | **added**: the kit fits and scores only each hub's skin face (the disc at F). The model also places the crown disc (F + 12.25) and the cylinder wall (r 10 mm, 32 angles x 6 levels F + 2 ... F + 12.25) in every taken pose. A pose where any of them is inside the skin becomes a contact pose. Reported: `crown_contact_poses`, `crown_min` |
| (d) near-touch | **added**: `min_metal_skin` over taken poses (face + crown + wall), and `gap_near1` (any metal < 1 mm counted as contact) |
| (e) overhead | **added**: `overhead` = reach over the workspace poses with elevation >= 140 deg, and in-band 2-14 / 2-10 over every taken pose with elevation >= 140 |
| (c) frozen shape on the big bench | **added**: `fold-sph3r.py frozen` = tools/concept_bigbench.py "frozen" (fit on Bench(60,160), freeze every underside, wear on Bench(110,360) exact, K6 at 1 mm radial) + the checks above |
| per part | **added**: `redteam` prints in-band per member, each hub's fitted level and body direction, the pose / ray that lifts each strap, the not-taken poses by cause, and the named pose groups |

The crown check matters: in stage 1, **47 % of the frontier configurations had at least one taken pose where a hub
crown or wall was inside the skin** (up to 72 poses), although every hub face was clear. The kit's 15 mm clear window
above each face sample does not hold when the hub sits higher than a sample's own requirement (a rigid hub sits at
the max over poses). At the known 3R axes (k1530, k2221, the champion at q 1.0) the crowns clear by 2.3-3.5 mm in every
taken pose. At q 0.95 the champion has 12 crown-contact poses (crown min -24 mm); its face already marks them as
contact poses, so the gap does not change.

## Stage 1: the frontier seeds (792 configurations, farm)

Setup:
- Every frontier.json layout with a1 + a2 in 85-140: 396 layouts, the top 3 distinct (J1, J3) per (a1, a2).
- Both branches (sigma +-1), q 1.0, fold margin 10, 12 x 3 straps.
- Bench(60,160), fast grid.
- Farm: 24 jobs, wall 28 min (375 s of it the upload queue behind another agent), $0.37.

| | gap | reach | follow | in-band 14 | contact | hub1 / hub2 / hub3 / link1 / link2 / neck in band |
|---|---|---|---|---|---|---|
| best (a1 75, a2 65, J1 bvec(114, 64), J3 wdir(90, 0), sigma -1) | **74.40** | 0.925 | 1.000 | 0.170 | 0.014 | 0 / 0 / 0.52 / 0 / 0 / 0.62 |
| best with J1 near horizontal (60 / 50, bvec(114, 16), wdir(65, -12), +1) | 77.04 | 0.913 | 1.000 | 0.149 | 0.019 | 0 / 0 / 0.43 / 0 / 0 / 0.71 |
| the frontier's 50 / 50 best (bvec(132, 16), wdir(75, 24), +1) | 87.52 | 0.888 | 0.950 | 0.103 | 0.066 | 0 / 0.03 / 0.12 / 0 / 0 / 0.47 |
| median of 792 | 118.1 | 0.719 | | 0.088 | | |
| control: plain 3R at k2221's axes | **51.33** | 0.894 | 1.000 | 0.393 | 0 | 1.0 / 0 / 0.68 / 0.37 / 0.05 / 0.66 |

### Where each layout loses in-band (per part, per body region, per pose)

By J1 elevation (the frontier's anterolateral J1 is el 16-28):

| J1 el | n | median gap | median reach (frontier's orientation-level ws share) | median mass | hub1 / hub2 / hub3 / link1 / link2 / neck median in band |
|---|---|---|---|---|---|
| 16-33 | 356 | 118.5 | 0.744 (0.894) | 966 g | 0 / 0 / 0.03 / 0 / 0 / 0.37 |
| 34-56 | 280 | 119.0 | 0.719 (0.856) | 768 g | 0 / 0 / 0.23 / 0 / 0 / 0.51 |
| 57-90 | 156 | 113.2 | 0.694 (0.794) | 710 g | 0 / 0 / 0.35 / 0 / 0 / 0.60 |

* **Hub 1 (scapula-fixed).** On the frontier's near-horizontal anterolateral ray, hub 1 is never in band.
  - Seed B: with the arm overhead (elevation 150, plane 0-15) the J1 ray lies within 9-16 deg of the humerus long
    axis, i.e. inside the arm. No position within 220 mm clears the skin, so the rigid hub is lifted to 400 mm. The
    frontier's 50 / 50 best does the same in 3 poses (elevation 150-165).
  - The cause is geometric. The fold-free J1 points near the middle of the humerus's workspace cone, because that is
    what keeps the J1-J3 angle in band. The middle of that cone is where the arm passes.
  - At J1 el 57-90 (over the acromion), hub 1 parks at 46-52 mm, in band in 100 % of poses, as in the champion.
* **Hub 2.** At the frontier layouts it floats at 109-400 mm.
  - Seed A: in 2 poses (elevation 135, plane 0-15, axial -45) the J2 ray points 124-136 deg away from the humerus
    axis, into the trunk, and never clears. Hub 2 is lifted to 400 mm.
  - Hub 2 is out of band in every pose of every frontier seed.
  - The same holds at the known 3R axes (hub 2 0 % in band at k2221, F 145 mm). It is the 3R's standing weakness.
* **Links.** 80 % of the frontier configurations have links fitted beyond 150 mm (Ti mass > 300 g; median 966 g at
  J1 el 16-33).
  - The links ramp up to the floating hub 2.
  - Their own sweep crosses the neck and chest: in seed A both straps sit at 355-381 mm.
  - Every link sample is out of band in every pose. The audit flags the strap sampling as sparse (> 4 mm spacing at
    that radius), which is why only 11 % of stage-1 reports are `honest`.
* **Hub 3 and the neck (humerus-fixed)** are the only parts in band: hub 3 on wdir(90, 0) parks at 70 mm (52 % in band).
  The poses that lift it are Raise-overhead frames with elevation 3-125 deg.
* **Poses not taken (seed A):** 12 of 220 (fold / K2 8, K6 1, contact 3). Overhead (elevation >= 140) reach is 0.50.
  - The fold frontier's promise mostly survives: reach 0.925 against the frontier's 0.95.
  - The proximity does not survive.

### Hub parking on the frontier (new tool, tools/fold_parking.py -> docs/research/fold/hub_parking.json)

A necessary condition the fold frontier does not check: each hub's centre ray (through GH) must clear the skin at a
level that stays within ~12 mm of its lowest requirement over the poses the chain closes in. The check is orientation
only (no links), 792 frontier layouts x branches, Bench(60,160):

* J1 ray never clears (inside the arm or the trunk) in at least one closing pose:
  - 39 % of the layouts with J1 el 16-33;
  - 3 % at el 34-56;
  - 0 % at el 57-90.
* J2 ray never clears in some pose: 26-39 % of the layouts, at every J1 elevation.
* Median rigid-hub level: hub 1 108 mm, hub 2 156 mm, hub 3 90 mm. Median share of poses in band (max - req <= 12):
  hub 1 0.02, hub 2 0.05, hub 3 0.38.
* 230 of 792 layouts park all three centre rays below 150 mm. The best of them have J1 over the acromion (el 64-80),
  a short a1 (30-40), a long a2 (100-110) and J3 low on the arm (wd 40). Example: a1 35, a2 105, J1 bvec(102, 72),
  J3 wdir(40, 0) parks hubs 1 / 2 / 3 at 46 / 56 / 107 mm, in band in 100 / 100 / 81 % of the closing poses.
  - Their stage-1 gaps are no better (median 115, best 78.3): the long link 2 sweeps the arm and chest.
* The known 3R axes, for reference: k1530 (sigma -1) hubs at 51 / 126 / 66 mm, in band 1.00 / 0.06 / 0.71; the
  champion (sigma -1) 50 / 142 / 69 mm, 1.00 / 0.02 / 0.44.

**Answer to the open question.** Hubs on the frontier's rays do not stay in the 2-14 mm band:
- The anterolateral, near-horizontal J1 that buys the fold-free workspace is the ray along which the arm moves.
- J2 lands inside the arm or the trunk in a third of the frontier layouts.

The fold frontier and the proximity optimum sit in different places for a concurrent chain. This is a trade-off
between the two objectives, not a limit of the search.

## Stage 2: variants of the top 20 seeds + controls (54 configurations, farm)

Setup: q 0.95 / 0.97 on the top 20 distinct seeds, strap width 10 mm on the top 10, and the four controls.

| | gap | reach | in-band 14 | contact | gap with < 1 mm = contact | crown-contact poses |
|---|---|---|---|---|---|---|
| best frontier variant: a1 75, a2 60, bvec(114, 64), wdir(90, 12), sigma -1, q 0.95 | 70.90 | 0.781 | 0.448 | 0.105 | 84.48 | 15 |
| frontier seed A, q 0.95 | 72.57 | 0.794 | 0.400 | 0.120 | 90.68 | 20 |
| frontier seed A, 10 mm straps | 72.91 | 0.925 | 0.185 | 0.014 | 72.91 | 0 |
| control k2221 axes, q 1.0 | **51.33** | 0.894 | 0.393 | 0 | 51.33 | 0 |
| control k1530 axes, q 1.0 | 51.97 | 0.888 | 0.393 | 0 | 51.97 | 0 |
| control champion axes, q 1.0 / 0.95 | 65.05 / 69.29 | 0.906 / 0.763 | 0.250 / 0.457 | 0 / 0.112 | 65.05 / 73.74 | 0 / 12 |

With q < 1, the score buys in-band with contact poses. The near-touch rule takes most of it back: 70.90 becomes 84.48.

<!-- CMA, frozen, red team, comparison: below -->

## Frozen shape on Bench(110,360), exact (lesson c; farm, `fold-sph3r.py frozen`)

The geometry is fitted on Bench(60,160) on the exact path, every underside is frozen, and the shape is worn on the 470
poses of Bench(110,360), exact, with K6 at 1 mm radial. This is the verifier's protocol plus the crown, near-touch and
overhead checks. Wall time 21 min on 2 vCPU.

| | fast Bench(60,160) | exact fit Bench(60,160) | **frozen Bench(110,360) exact** | reach | in-band 14 / 10 | contact | min metal-skin | crown-contact poses | overhead (elev >= 140) reach / in-band 14 |
|---|---|---|---|---|---|---|---|---|---|
| plain 3R at k2221's axes (the 51.33 control) | 51.33 | 51.36 | **57.99** | 0.839 | 0.393 / 0.241 | 0.012 | 1.69 mm | 2 (crown min -27 mm) | 0.39 (11 / 28) / 0.48 |
| plain 3R at k1530's axes | 51.97 | 51.99 | **60.03** (= the earlier verifier's 60.03, concept_bigbench) | 0.817 | 0.393 / 0.226 | 0.010 | 0.91 mm (near-touch gap 61.08) | 2 (crown min -60 mm) | 0.46 / 0.47 |
| frontier seed A (75 / 65, bvec(114, 64), wdir(90, 0)) | 74.40 | 74.47 | **78.11** | 0.869 | 0.170 / 0.073 | 0.021 | 0.89 mm (78.61) | 3 | 0.50 / 0.23 |
| CMA G (q 1.0) | 49.03 | | pending (farm, `.cache/fsph3r/big_cmaG.json`) | | | | | | |
| CMA F (q 0.9805) | 44.72 | | pending (farm, `.cache/fsph3r/big_cmaF.json`) | | | | | | |

Big-bench crown checks found crown-contact poses at every axis set (2-3 poses, up to 60 mm deep). Those are unseen
poses where a frozen hub's crown runs into the arm. The poses become contact poses, so the gap above already counts
them.

Per part on the big bench (k2221): hub 1 100 % in band (F 52 mm, over the acromion), hub 2 0 % (F 145 mm, posterolateral,
median 73 mm off the skin), hub 3 69 %, link 1 37 %, link 2 5 %, neck 65 %. Poses not taken: 58 of 470 (fold / K2 50,
K6 3, contact 5). The closest metal is a face at 1.69 mm at plane 15, elev 135, axial -60. That pose is unseen by the
fit, so the frozen underside is 0.3 mm short of the 2 mm rule there. The < 1 mm near-touch rule changes nothing
(gap_near1 57.99).

## CMA-ES on the farm (tools/concept_cma.py; 6 streams, 4790 tries)

Setup:
- Popsize 8, 4 processes per job, budget 1500 s.
- Coordinates and scales: az 8, el 6, a1 5, a2 5, wd 6, wa 8 deg; stream F also q, scale 0.03 (clipped to <= 1).
- Fixed: fold margin 10, 12 x 3 straps, branch per stream.
- A dishonest report costs +100.
- Farm cost of the batch: $0.46.

| stream | start | sigma | tries | best gap | where it went | gate (score pts: 2nd half / last third / top 5) |
|---|---|---|---|---|---|---|
| A | frontier best 74.4 (75 / 65, bvec(114, 64), wdir(90, 0), -1) | 0.4 | 185 | 170.35 (= 70.35 + 100: links beyond 4 mm sampling) | stayed on the frontier; 60 s per try (links outside the grid box) | 0.41 / 0.20 / 0.28 |
| B | J1 near horizontal (60 / 50, bvec(114, 16), wdir(65, -12), +1) | 0.4 | 913 | 59.33 | J1 climbed el 16 -> 37, a1 / a2 55 / 54, wdir(93, -19); hub 1 still 0 % in band, hub 2 21 %, hub 3 86 % | 0.48 / 0.17 / 0.01 |
| D | hub 1 in band (45 / 95, bvec(114, 76), wdir(50, 12), -1) | 0.4 | 945 | 59.64 | bvec(88, 61), 57 / 87, wdir(57, -15); hub 1 98 % in band, link 2 1 % | 2.16 / 0.39 / 0.08 (not converged alone) |
| E | k1530's axes (51.97) | 0.5 | 1097 | 50.30 | bvec(12, 77), 81 / 64, wdir(94, -6): stayed at the known 3R basin | 0.12 / 0.00 / 0.00 |
| **F** | k1530's axes, **q free** | 0.4 | 1193 | **44.72** | bvec(28.3, 65.4), 83.5 / 62.9, wdir(94.3, -9.4), q 0.9805 | 0.38 / 0.15 / 0.01 |
| G | k2221's axes (51.33) | 0.3 | 457 | **49.03** (q 1.0) | bvec(29.1, 79.4), 82.6 / 65.3, wdir(95.5, -3.3) | 0.00 / 0.00 / 0.13 |

**Gate on the whole CMA history** (4790 tries ordered by generation): best gained 0.60 score points over the second
half and 0.29 over the last third; the top 5 are within 0.01. **Converged.** Every stream converged alone except D,
which is still 15 points behind.

* The streams seeded on the frontier (A, B, D) all walked away from it and stopped at 59-70.
* Both bridge streams from the known 3R axes (E, G) stayed in the known basin, J1 over the acromion (el 65-80).

### The two bests (Bench(60,160), fast grid, kit checks, crown check)

| | gap | score | reach | follow | in-band 14 / 10 | contact | gap with < 1 mm = contact | min metal-skin | overhead reach / in-band 14 | hub1 / hub2 / hub3 / link1 / link2 / neck in band | Ti mass |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F k5170 (q 0.9805) | **44.72** | 83.7 | 0.900 | 0.967 | 0.458 / 0.318 | 0.005 | **53.66** | **0.00 mm** | 0.50 / 0.43 | 1.0 / 0 / 0.87 / 0.39 / 0.10 / 0.78 | 172 g |
| G (q 1.0) | 49.03 | 82.2 | 0.900 | 1.000 | 0.410 / 0.253 | 0 | 49.03 | 1.37 mm (crown / wall; faces >= 2.00) | 0.42 / 0.46 | 1.0 / 0 / 0.80 / 0.36 / 0.06 / 0.69 | 173 g |

F's gain over G comes from q < 1. The undersides are fitted to the 98th percentile of the poses, so in 8 workspace
poses metal sits 0.00-0.9 mm from the skin (elevation 165, plane 45-75; plane 0, elevation 60). With the near-touch
rule (lesson d) F scores 53.66, worse than G. **G is the best shape that survives lesson (d).**

## Red team (F and G, Bench(60,160); `fold-sph3r.py redteam`)

* **Jam / fold.** 15-17 of 220 poses are lost to the J2 fold (margin 10 deg) or K2, the same poses at all three axis
  sets. Overhead (elevation >= 140) reach is 0.42-0.50: 5-7 of the 12 workspace poses up there fold. Overhead is
  this morphology's weak point. The frontier layouts that would keep those poses push hub 1 and hub 2 into the arm and
  trunk (above).
* **Pinch point.**
  - F: a skin face at 0.00 mm (plane 60, elev 165, axial -90); 0.28 mm at plane 0, elev 60, axial -60.
  - G: faces never below 2.00 mm. The closest metal is a hub crown or wall at 1.37 mm.
  - G frozen on the big bench: see below.
* **What lifts the links.** In G, link 1 and link 2 are lifted to 149-156 mm in one pose (plane 0, elev 60, axial
  -60). There they lie on a ray at thorax az -131, el -11 to -14 (posterior-medial, slightly down) over the back. In
  13-14 % of poses some strap sample needs > 100 mm.
  - Link 2 is 6 % in band, at a median 116 mm.
  - Hub 2 is 0 % in band at F 154 mm (posterolateral, horizontal). Its centre ray has no position near the skin that
    holds in every pose.
  - Hub 2 and link 2 are the limiter, as in the champion.
* **Near-touch gap:** G 49.03 (unchanged), F 53.66.

## Comparison (same benches)

| design | passive translations | Bench(60,160) fast | Bench(110,360) exact, frozen |
|---|---|---|---|
| champion 3R (baseline conventions, rows/baseline-3r.json) | 0 | 68.93 | 75.94 |
| plain 3R at the champion's axes, kit checks (this model, control) | 0 | 65.05 | |
| plain 3R at rail-elbow k2221's axes (the 51.33) | 0 | 51.33 | 57.99 |
| frontier-seeded best, before CMA (q 0.95 / q 1.0) | 0 | 70.90 / 74.40 | 78.11 (q 1.0) |
| **fold-sph3r CMA G (q 1.0, near-touch clean)** | 0 | **49.03** | pending |
| fold-sph3r CMA F (q 0.98) | 0 | 44.72 (near-touch 53.66) | pending |
| leader offset-skin-normal-3r k4216 (2 cuff slides) | 2 | 32.61 | 42.59 (its verifier) |

## Verdict

* **Screened.** This is the best plain spherical 3R measured so far: 49.03 at q 1.0 (score 82.2) and 44.72 at q 0.98
  (score 83.7, near-touch 53.66).
  - It beats the champion and the 51.33 control.
  - It has no passive translation.
  - It does not reach 90+ (gap <= 27.5). It stays 12-16 points behind the 2-slide osn leader on the screening bench.
* **The fold frontier does not transfer to a concurrent chain.**
  - The frontier's own layouts score 70-170.
  - CMA walks every frontier start back toward J1 over the acromion (el 37-79).
  - The best result came from the known basin, not from the frontier.
  - Reason: the rays that keep the J1-J3 angle in band are the rays the arm and the trunk occupy. The fold frontier
    must be intersected with hub parking (tools/fold_parking.py) before it seeds any concurrent morphology.
* **Limiter (measured):** hub 2 and link 2.
  - Hub 2 is 0 % in band at every axis set: F 145-154 mm, posterolateral, horizontal.
  - Link 2 is 5-10 % in band, at a median 116 mm, lifted by the posterior-medial pose (plane 0, elev 60, axial -60).
  - Overhead reach is 0.42-0.50: the fold.
  - A concurrent J2 cannot follow the skin.
  - With no slide, every axis must pass through GH (the osn closure theorem with zero slides), so this morphology has
    no further freedom. The cheapest way out is the osn one: J3 offset and tilted toward the skin normal, with 2
    cuff slides in hub 3's plane (14 points there).
  - The plain spherical 3R tops out near 49 on this bench (score 82): the 6-coordinate CMA converged from 6 starts.

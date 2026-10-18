# freek-oracle-route-knuckle-4r - Free-K oracle bound with an anterior link-2 corridor (round 104, lens B, an INSTRUMENT, never a claim)

## Deeper-version answers (written first, 2026-10-18 05:33 UTC)

1. **What a top mechanism designer would do that the spec does not ask.** Before building any K determination (cells B / C),
   bound it: a per-pose oracle that picks the best K on the legal self-motion is the ceiling of EVERY K law, spring, stop or
   sensed 4th joint at these seats. The designer would also ask which lost poses the oracle can reach at all: K's stop B is
   the same for the oracle as for the kit, so a pose refused for the fold (K past stop B) stays refused - the oracle can only
   turn CONTACT (and near-touch) poses into takes. So the bound is "kit takes + rescued contacts", and the 95 arithmetic
   (+17 takes) is out of reach unless the corridor also clears metal-parked stretched poses. Second thing not asked: score
   the oracle's pick on the FULL model checks (part-part pairs, knee, band), not on skin distance alone, because max-min skin
   distance can push link 2 into member 3 or out of the band.
2. **Rawest material.** The posed skin itself through the bench's exact signed distance (`W.dist`, CB_EXACT=1) per pose and
   per K sample, the motion clips' frames (Bench(110,360) clip frames for follow and in-band), the 1432-pose workspace grid
   for continuity; not the proposer's interpolated (s, v) clearance field (field2.npz) - that field is used only to choose
   the corridor's sweep range.
3. **Methods and tools.** The verified k33 harness unchanged (minarc kitrule + skinnormal-shortk pricing, frozen hand-over
   by __dict__ diff from docs/concepts/verify/minarc-bdp-remeasure.py), a closed-form free-K self-motion (J2 off its stop:
   K angle -> a1e on the K dyad -> the (a1e, a2) dyad closure, same assembly branch), exact skin distance per sample,
   then ONE composed run of the frozen model with the per-pose K table so every check of the model applies; corridor as a
   planform offset of link 2's rows on the sphere, refitted by the model's own needed() + ramp profile.
4. **Who else shows the number is right.** The bench (Bench(60,160) fast for the sweep, Bench(110,360) exact frozen for
   the bound), the round's adversarial verifier and the alignment auditor; a red-team list (the binder poses 117 / 127 /
   129 / 139 / 148 / 316 / 343 / 369 / 423 / 119 with hub 2, L1b, L2, hub K distances at the oracle's pick) is on file so
   any reader can re-measure it.

## Verdict (the bound of record, frozen exact Bench(110,360), k33 shape)

**Free-K oracle: 17.25 connected plain (16.96 static), 21.46 near-touch; kit at the same shape 18.61 / 23.36. Pre-registered
gate FAIL** (280 connected takes but ~21 contacts; 5 binders - 117 / 119 / 129 / 343 / 423 - touch the skin at EVERY legal K).
The oracle rescues exactly 3 poses (148 at 0.46 mm, 316 at 2.40, 369 at 1.56). The anterior link-2 corridor makes it worse
(+12 deg: 18.71 connected). So every K-side lever at these seats - any K law, spring, J3 stop, J3 spring or a sensed free K -
is bounded by 17.25 plain / 21.46 near-touch; the wall is where hub 2 and link 2 park at the ER binders, not K.

## What was built (docs/concepts/models/freek-oracle-route-knuckle-4r.py)

The verified skinnormal-shortk / minarc kitrule harness, imported unchanged (the k33 priced params of
docs/concepts/verify/skinnormal-shortk-knuckle-4r/c_k33_fit60_bench_params.json; frozen hand-over by the remeasure
harness's __dict__ diff; fit Bench(60,160) fast -> frozen -> Bench(110,360) exact), plus:

* **Free-K self-motion in closed form** (`ODesign.free_solve`): K at |dK| -> a1e on the K dyad -> the (a1e, a2) dyad closes on
  the arm's J3 axis (same assembly branch as state A) -> q3, member 3, the knee slide vector. Legal iff the closure exists,
  the effective dyad keeps the 5.5-deg J1-J3 margin, |dK| <= stop B (82.0 deg) and J2's own angle q2 sits inside its slot
  (stretched end moved to the 5.5-deg rule for the bound: a ceiling, the kit's priced stop is at 7.877).
* **The oracle, run-based** (`oracle_runs`, the instrument of record): for every stretched pose (th > th_hi; 136 of the 470
  Bench(110,360) poses) 7 samples of |dK| from the 5.5-deg floor to stop B (+ the kit's own K), each sample a full run of the
  frozen model on a sub-bench of those poses, so EVERY check applies (knee window, knee slide residual, member 3 and the knee
  moving with K, part pairs, skin incl. hub crowns, clip continuity with the dK jump rule on the fit clips). Per pose the pick:
  taken-and-clear beats contact; among taken the larger min(metal distance, 2.5 mm); ties -> nearest the kit's K; then ONE
  composed run of the frozen model with the per-pose table.
* **Corridor route** for link 2 (`RouteGeo`: rows bow by v(s) = rA sin(pi s / 2 rsp) to the peak, back to the great circle at
  rsr; +bn = anterior-superior, bn = (0.884, 0.375, 0.279) in the thorax frame at rest, span 69.1 deg); the model's own
  needed() + ramp profile refits the bar on the routed rows, so the corridor's in-band and near-touch cost is measured.
* **Connected bound**: a taken ws pose counts only if its grid node is in the k33 kinematic flood-fill set
  (c_k33_fit60_bench_conn.json, 1138 nodes, all 290 Bench(110,360) kinematic nodes connected; the route changes no kinematics)
  and every sampled K between the kit's and the oracle's pick is kinematically legal at that pose.

### Spec corrections (said plainly)

1. The spec's literal oracle (max-min skin distance over hub 2, L1b, L2, hub K) misses that **member 3 and the knee move with
   K**: J3's line misses GH (|c3| ~ 15 mm), so t3 = R12 (c3 - R3 c3) and the knee slide vector change with K. Picks made on
   members 1 / 1b / 2 alone were optimistic (v1 rows of the sweep, superseded). The run-based oracle replaces it (the scan
   stays as FO_HOW=scan).
2. **Red team on my own first oracle (v2a)**: its pick rule ranked "lost" above "contact", so 5 contact poses (117, 119, 129,
   343, 423) "escaped" to a K sample the model REFUSES (the floor sample reads 'fold') and were scored as lost poses instead of
   contacts: 15.27 plain / 15.55 connected, optimistic by 1.7 points. A refused K is not a place the mechanism can park; the
   corrected rule (v2b) lets only legal configurations compete and keeps the kit's state when none is legal. All numbers below
   are v2b; the v2a rows in the sweep file are tagged as superseded.
3. The oracle acts on the stretched state only (as specified). State-A contacts (e.g. 230 at 0.09 mm, the k33 near-touch
   minimum 15/90/30) are not offered to it; a fully free K could also open there - not covered by this bound.

## Results

### Cell A, frozen exact Bench(110,360) at the k33 shape, route 0 (the bound of record)

| reading | gap | score | ws taken | reach | ib14 | follow | contact | near-touch gap (metal < 1 mm = contact) |
|---|---|---|---|---|---|---|---|---|
| kit (K slaved: J2 on its stop, minimal K) - reproduces the verified wear | 18.61 | 93.23 | 277 | 0.7694 | 0.8965 | 0.9455 | 0.0475 | 23.36 |
| ORACLE static (v2b) | 16.96 | 93.83 | 281 | 0.7806 | 0.8990 | 0.9455 | 0.0447 | 21.17 |
| ORACLE connected (v2b) | **17.25** | 93.73 | 280 | 0.7778 | 0.8990 | 0.9455 | 0.0448 | **21.46** |

Taken poses clear of the skin by >= 0.2 mm: 384; by >= 1 mm: 377 (8 near-touch poses, min 0.092 mm - a state-A pose the oracle
does not touch). The oracle moved K at 36 poses (27 of them taken in the free state).

**Pre-registered gate: FAIL.** >= 279 takes - yes (280 connected) - but at ~21 contacts, not <= 4; and 5 of the binders are
in contact at EVERY legal K.

### The binder table (oracle samples, frozen exact; distance = min metal-skin over every member, mm)

| pose (plane / elev / axial) | th | kit dK | oracle pick | best legal outcome |
|---|---|---|---|---|
| 117 (-90 / 45 / 135) | 112.3 | 50.1 | 48.1 | contact -1.14 at every legal K (floor refused) |
| 119 (-90 / 60 / 135) | 119.9 | 64.4 | 61.8 | contact -10.74 |
| 127 (-75 / 45 / 120) | 102.7 | 31.5 | kit | taken 1.27 |
| 129 (-75 / 60 / 120) | 108.5 | 42.9 | 41.7 | contact -5.87 (K >= 66 refused: knee slide) |
| 139 (-60 / 60 / 105) | 97.5 | 20.8 | kit | taken 0.55 (near-touch) |
| 148 (-45 / 45 / 135) | 121.7 | 67.9 | 62.1 | **rescued** 0.46 (inside the 1 mm shell) |
| 316 (60 / 150 / -105) | 105.9 | 37.9 | 73.1 | **rescued** 2.40 |
| 343 (75 / 150 / -105) | 115.0 | 55.1 | 82.0 (stop B) | contact -0.19 at stop B |
| 369 (90 / 135 / -90) | 108.0 | 42.0 | 73.8 | **rescued** 1.56 |
| 423 (120 / 135 / -90) | 119.5 | 63.8 | 77.8 | contact -1.33 |

Also never clear at any legal K: 405 (-10.85) and 459 (-6.91). The rescues are exactly 3 (148, 316, 369); the proposer's
"~282 takes" was 281 static / 280 connected.

**The ER / IR split is real and points the wrong way for a J3 determination:** the external-rotation binders (117 / 119 / 129 /
148, plane -90..-45, axial 120-135) want LESS K (all picks below the kit, toward the 5.5-deg floor) - and still touch at the
floor; the internal-rotation binders (316 / 343 / 369 / 423, plane 60-120, axial -90..-105) want MORE K (73-82 = stop B). Only
the IR side is rescued (316, 369), the ER side is a wall at every K.

### Corridor (lens B's route), Bench(60,160) fast, oracle v2b (sweep rows k 51-60)

| config | oracle gap (near-touch) | plain | ib14 | kit at the same route |
|---|---|---|---|---|
| route 0 (k33) | 11.18 | 11.18 | 0.8973 | 12.18 |
| rA +4 (peak 25, back 48) | 11.15 | 11.15 | 0.8976 | 12.16 |
| rA +8 (anterior, the spec's corridor) | 13.73 | 11.46 | 0.8945 | 13.60 |
| rA -4 / -8 (posterior) | 12.05 / 11.44 | 10.91 / 11.44 | 0.9013 / 0.8947 | 12.85 / 12.31 |
| rA -6.8 / 25.2 / 51.8 (the superseded v2a search's best, re-run v2b) | 11.29 | 11.29 | 0.8962 | 12.16 |
| seeds k56 / stopb80 / skinnormal_r / k8 (route 0) | 13.47 / 11.82 / 12.37 / 15.22 | 12.34 / 11.82 / 11.22 / 9.54 | | 13.57 / 12.83 / 12.49 / 15.53 |

The anterior corridor buys nothing the oracle can use on the fit bench and costs near-touch from +8 deg on (link 2 rides closer
to the skin elsewhere: the proposer's in-band proxy 0.864 -> 0.814 at +8 was the right sign). The exact frozen check of the
spec's +12 corridor at the binders is in "Corridor, exact" below.

### Corridor, exact (the spec's anterior corridor at the binders): rA +12, peak s 25, back on the great circle at s 55

Frozen exact Bench(110,360), refitted shape, oracle v2b (saved: docs/concepts/verify/freek-oracle-route-knuckle-4r/wear3_rA12_25_55.json):

| reading | gap | ws taken | ib14 | contact | near-touch |
|---|---|---|---|---|---|
| kit at the corridor shape | 20.18 | 277 | 0.8808 | 0.0475 | 25.45 |
| oracle static | 18.42 | 281 | 0.8844 | 0.0447 | 23.15 |
| oracle connected | 18.71 | 280 | 0.8844 | 0.0448 | 23.45 |

It does what the proposer said at the ER binders and no more: best legal metal 117 -1.14 -> -0.46, 129 -5.87 -> -4.17, 119 -10.74
-> -8.48, 148 0.46 -> 1.76 (now clears 1 mm) - all still in the skin except 148 - while the IR side loses (316 2.40 -> 1.19, 369
1.56 -> 0.54, 343 -0.19 -> -2.48) and link 2's in-band falls 0.899 -> 0.884 (+1.5 gap). Net: 17.25 -> 18.71 connected. The
"129 to +0.90 at +12 deg" of the proposer's interpolated field is -4.17 on the exact skin with every check on: the field
(Hf - Hb + 2 at 2-deg (s, v) cells) was optimistic by ~5 mm at 129.

### Cells B / C (conditional): trigger met on the plain reading only, NOT built in this time box

The plain connected bound (17.25) is 0.53 under the 17.78 trigger; the near-touch connected bound (21.46, the round's search
objective) is not. The oracle data bound them further, before any build:

* Only the IR rescues (316, 369) lie in a J3 stop's direction (more K). The ER side wants LESS K than the kit and touches at the
  floor anyway, so neither a J3 stop nor a J3-centring spring can take it. Cell B's ceiling is therefore ~17.6 plain (2 takes and
  2 contacts off 18.61) if it opens nothing else - 0.2 under the trigger, 0.7 under the lead, for a 4th counted joint
  (+25 complexity).
* **q3 in the model's OWN J3 convention** (vref = unit(u3 x (0.3, 0.5, 0.8)), `S.sub1` as in `_ik_phys`): the IR binders sit at
  q3 99-113 at the kit, and the K that rescues them puts q3 at 77-82 (dq3/ddK ~ -0.67); the ER binders at q3 -60..-82. A cell-B
  groove end belongs at q3max ~ 78-82 deg in this convention (kscan3's reference is a different one). Per-binder values:
  the numbers are in the table below (computed with ODesign.free_solve on the k33 design).

| pose | q3 at kit | q3 at floor / kit / pick | dK floor / kit / pick |
|---|---|---|---|
| 117 | -60.9 | -51.8 / -60.9 / -59.0 | 41.3 / 50.1 / 48.1 |
| 129 | -82.0 | -72.4 / -82.0 / -80.9 | 33.7 / 42.9 / 41.7 |
| 148 | -67.0 | -61.1 / -67.0 / -61.1 | 62.1 / 67.9 / 62.1 |
| 316 | 106.1 | 115.8 / 106.1 / 82.4 | 28.5 / 37.9 / 73.1 |
| 343 | 109.2 | 117.7 / 109.2 / 91.1 | 46.9 / 55.1 / 82.0 |
| 369 | 98.9 | 108.5 / 98.9 / 77.2 | 32.7 / 42.0 / 73.8 |
| 423 | 112.6 | 119.5 / 112.6 / 102.1 | 57.0 / 63.8 / 77.8 |

## Limiter (measured)

Metal parking at the seats, not K. At the ER binders (plane -90..-45, elev 45-60, axial 120-135) every legal K leaves link 2 /
hub 2 in the skin (117 -1.14, 129 -5.87 - K >= 66 is refused there by the knee slide residual - 119 -10.74); at the IR binders
343 / 423 the best is stop B and still -0.19 / -1.33. The K self-motion rotates link 1b / hub 2 / link 2 about axes that all pass
near GH, and at these poses it sweeps them along the skin instead of off it: the second wall is set by where hub 2 and link 2
PARK (seats, link-2 path radius, hub-2 standoff), so the jump track's next lever is a seat / standoff move (e.g. hub 2's f2 and
link 2's height profile refitted for the ER binders, measured by the same oracle as a ceiling) - not another K law.

## Red team (my own number)

* **Optimistic pick rule** - found and fixed (v2a -> v2b, 1.7 points; see spec corrections).
* **Slot end moved to 5.5 deg** - optimistic by construction (a bound); the kit's priced stop is at 7.877.
* **Static vs connected** - 1 ws pose dropped by the connected rule (17.25 vs 16.96).
* **Near-touch** - 8 taken poses under 1 mm (139 at 0.55, 148 at 0.46, 230 at 0.09, ...); the near-touch connected bound 21.46 sits
  above the 18.28 bar (which is a plain reading), so on the round's search objective the oracle does not even reach the bar.
* **Fit-bench in-sample** - the fast numbers (11.18) are the oracle on its own fit bench; the frozen exact bound is the number of
  record.
* **Not covered** - state-A contacts (a fully free K could open there too) and held-out poses (not run: a bound is not a claim).

## Next

* Cells B / C are not worth their 4th joint at these seats: ceiling ~17.6 plain for B, both under 21 near-touch. Record them as
  bounded by A.
* Point the oracle at the seats instead: hub 2 / link 2 parking at the ER binders is the wall. The instrument here (run-based,
  legal-only, connected) can bound any seat move the same way in ~10 min of exact compute per shape.

## Files and reproduction

* Model: docs/concepts/models/freek-oracle-route-knuckle-4r.py; sweep: docs/concepts/sweeps/freek-oracle-route-knuckle-4r.json
  (rows k 0-10 v1 scan, k 11-50 v2a - both superseded and tagged; k 51-60 v2b of record); row:
  docs/concepts/rows/freek-oracle-route-knuckle-4r.json; preview: docs/concepts/viz/concepts/freek-oracle-route-knuckle-4r.js.
* Saved outputs: docs/concepts/verify/freek-oracle-route-knuckle-4r/wear3_r0.json (+ _perpose.json: every sample of every
  stretched pose, the pick table, the per-pose lowest metal), binder_q3.json, wear2a_r0_superseded.json (the optimistic v2a).
* Bound of record (fit fast -> frozen exact, ~10 min locally):
  `CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/freek-oracle-route-knuckle-4r.py wear '{}' OUT.json`
  (wear3_r0 was composed from the v2a run's saved sample records with the corrected rule: `FO_PRE=<v2a OUT.json>`).
* Fast sweep: `... freek-oracle-route-knuckle-4r.py sweep '[{"rA": 8, "rsp": 25, "rsr": 48}, {"seed": "stopb80"}]'`.

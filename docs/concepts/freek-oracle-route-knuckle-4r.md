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

## Verdict (frozen exact Bench(110,360), k33 shape)

**Cell A (the free-K oracle, an instrument): 17.25 connected plain (16.96 static), 21.46 near-touch; kit at the same shape 18.61 /
23.36. Pre-registered gate FAIL** (280 connected takes but ~21 contacts; 5 binders - 117 / 119 / 129 / 343 / 423 - touch the skin
at EVERY legal K). It rescues exactly 3 poses (148 at 0.46 mm, 316 at 2.40, 369 at 1.56). The anterior link-2 corridor makes it
worse (+12 deg: 18.71 connected). The ER wall (117 / 119 / 129 / 148) is where hub 2 and link 2 park, not K.

**Cell B (built, since the plain bound met the 17.78 trigger): a dowel stop on J3's own angle at q3max 86 (model convention),
K opening to hold it: 16.20 static / 17.35 connected plain (score 93.69), 22.19 near-touch, 276 connected ws takes, 4 counted
joints, complexity ~33.25.** The first 4-DOF row under the lead's 18.28 on the plain reading (by 0.93) - but **held out (1154
disjoint poses, frozen, connected) it reads 22.67 vs its own kit 23.37 and the lead's 22.38: it does NOT beat the lead held
out.** NOT verified; near-touch 22.19; overhead 5 / 28.

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

### Cell B, BUILT and measured (the trigger was met on the plain reading: bound 17.25 <= 17.78)

The plain connected bound (17.25) is 0.53 under the 17.78 trigger (the near-touch bound 21.46 is not), so cell B was built in the
time left: **a dowel stop on J3's OWN angle at q3max** (`ODesign.j3stop`, param `q3max`, deg in the MODEL's J3 convention:
`S.sub1` about u3 from vref = unit(u3 x (0.3, 0.5, 0.8)) - not kscan3's reference). Where the slaved state's q3 exceeds q3max
(state A or stretched), K opens along the free self-motion to the FIRST K where q3 = q3max (0.5-deg scan from the current K
up to stop B + linear refine); J2 keeps its own priced slot (stretched end 7.877, checked); no crossing before stop B -> the
pose is refused (the arm is stopped by the J3 dowel with K on stop B, exactly as the kit refuses past stop B). Determinacy: the
K clock spring pulls K down and q3 rises as K falls (dq3/ddK ~ -0.67 at the IR binders), so the lowest K with q3 <= q3max is the
spring's equilibrium - one state per pose. Hardware: an ISO 8734 2 m6 dowel at r 7.5 in a 2.1 x 1.0 groove inside J3's O20
stack (the catalogue entry); complexity ~33.25 (shortk 32.5 + dowel 0.25 + groove 0.5), 4 counted joints.

Fit Bench(60,160) fast WITH the law -> frozen -> Bench(110,360) exact; continuity = the remeasure harness's kinematic flood fill
(`RM.kin_nodes` + `RM.flood`, 2-deg slerp edges, jump 10 deg incl. dK) run on THIS design:

| q3max (model's J3 convention) | static gap | connected gap | ws taken static / connected | ib14 | follow | contact | near-touch (connected) | overhead >= 140 taken |
|---|---|---|---|---|---|---|---|---|
| off (the kit, k33) | 18.61 | 18.61 | 277 / 277 | 0.8965 | 0.9455 | 0.0475 | 23.36 | 6 / 28 (k33 verify file) |
| 80 | 17.00 | 17.86 | 279 / 276 | 0.8996 | 0.9455 | 0.0404 | 22.70 | 6 / 28 |
| **86** | **16.20** | **17.35** | 280 / 276 | 0.8977 | 0.9545 | 0.0379 | **22.19** | 5 / 28 |

Flood fill (q3max 86): 1108 kinematic nodes, all connected (0 islands), 979 edges tested, 3 refused by the rule, 0 by jumps;
4 taken bench ws poses are not kinematic nodes under the verifier's stricter per-node rules (they include the J1-K-J3 sub-chain
margin, which does not bind a free J2 - not attributed further in this box), so the connected reading is the conservative one.
Fast Bench(60,160) sweep of q3max 70-95 (rows k 61-68): 16.72 / 11.72 / 10.66 / 10.75 / 10.16 / **9.56** / 10.74 / 10.84
(kit 12.18) - 86 picked there, then worn frozen.

Binders under cell B (q3max 86, frozen exact; mm): 316 +1.12 and 369 +0.31 taken, 343 and 423 now REFUSED by the stop (they were
contacts: refused = lost reach, not contact), 148 -0.67, 117 -1.80, 129 -6.37, 119 -12.0 still in the skin, 127 +1.19, 139 +0.42.

**What cell B is and is not.** It is a determined 4-DOF realisation that lands at **17.35 connected (score 93.69) frozen exact,
0.93 under the lead's 18.28** - the first 4-DOF row on file under the bar - at near-touch 22.19, complexity ~33.25 vs the lead's
18.5 at 3 DOF, and with the overhead count at 5 / 28 (k33 kit 6 / 28, the lead 8 / 28). It beats the static oracle bound at q3max 86
(16.20 vs 16.96) because a stop may REFUSE a pose (343, 423 turn from contact into lost reach) where the oracle had to keep the
mechanism somewhere legal; the connected readings agree within 0.1 (17.35 vs 17.25). Held out (1154 poses, frozen exact, flood fill): 21.89 static / 22.67 connected (near-touch 26.22) vs the kit's 23.37 / 23.37 and
the lead's 22.38 (files cellB_q3max86_held.json, kit_k33_held.json). Not run: the J3-stop force (the dowel at r 7.5 takes the arm's torque about J3: the M5 class check the lead's
watch list carries), the spring-equilibrium scan of the verifier (`checks_B`'s 'lower_inside' test, which assumes J2 on a stop).
The ER wall is untouched by cell B (117 / 119 / 129 / 148), so cell C (a J3-centring spring) cannot do better on those poses.

#### q3 of the binders in the model's own J3 convention (for whoever builds cells B / C next)

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

* **Verify cell B (q3max 86)** with an independent verifier: held-out (launched at the end of this box), the J3-stop force through
  the dowel at r 7.5 (M5 class), the spring-equilibrium red team adapted to a free J2, the 4 taken-but-not-node poses, and
  q3max 83-90 frozen exact (only 80 and 86 were worn). Its ranking question is the user's DOF rule: a 4th counted joint at
  ~33 complexity for ~0.9 plain points over a 3-DOF lead at 18.5.
* Cell C (J3-centring spring) cannot touch the ER wall either; build it only if cell B verifies and its stop force is the problem.
* Point the oracle at the SEATS: hub 2 / link 2 parking at the ER binders (117 / 119 / 129 / 148) is the wall for every K-side
  lever; the run-based, legal-only, connected oracle bounds any seat move in ~10 min of exact compute per shape.

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

## Verification (skeptic, 2026-10-18 ~07:45 UTC)

**Result: not refuted. The numbers reproduce exactly. The row stays "screened"**, because the alignment ledger marks it
GAMED (P1, `docs/alignment/freek-oracle-route-knuckle-4r.md`), and CLAUDE.md says a gamed design cannot be called verified
until that finding is resolved. It is 4 DOF, so under the user's 2026-10-17 ruling it is not a leader in any case.
Champion on Bench(110,360) exact: 75.94 (risley-turret checks). This row's harness is the stricter k33 kit harness. The bar
that matters is the 3-DOF lead's 18.28 (held 22.38). Harness: `docs/concepts/verify/freek-oracle-route-knuckle-4r-verify.py`.
Outputs: `docs/concepts/verify/freek-oracle-route-knuckle-4r/verify_*.json` and the per-pose dumps
`docs/alignment/remeasure/freek-oracle-route-knuckle-4r_{bench,held}_perpose.json`, which recompute to 16.21 / 21.89.

| reading (cell B, q3max 86, frozen exact) | bench gap | held gap (1154) | ws taken bench / held |
|---|---|---|---|
| reproduced, static (the model's own code, unchanged) | 16.20 | 21.89 | 280 / 700 |
| reproduced, connected as claimed (claim's flood) | 17.35 | 22.67 | 276 / 693 |
| **one fold reading = the model's (flood re-run with the state-2 rule)** | **16.20** | **21.89** | 280 / 700 (0 dropped) |
| one fold reading = the family's, applied to clips too (auditor T3, not re-run) | 20.68 | 24.56 | - |
| lead conecut-knee-knuckle-3r | 18.28 | 22.38 | 262 / 659 |

Checks:

1. **DOF.** 4 counted joints: J1, K (sensed, with a clock spring to stop A), J2 and J3. That is inside the 4-DOF cap, with 0
   passive translations. The two knee pins carry no encoders and are outside the count. K is never left undetermined:
   - state A: K sits on stop A;
   - state 1: J2 is on its own-angle stop and K takes its smallest opening;
   - state 2: J3 is on its dowel, and with J3 locked the J1-K-J2 wrist is a 3R, so K is fixed. The spring presses J3 into
     the dowel because dq3/ddK < 0 at every crossing.

   **No hard rule is broken.** The design still loses the ranking to the 3-joint lead under the user's 2026-10-17 ruling.
2. **J3 stop reading (new check).** The model reads the stop on q3 = the angle of the cuff relative to link 2. J3's own angle
   (link 2 -> member 3) is q3' = q3 + phi.
   - The knee drift s = R3^T (c3 - R3 c3) depends on q3 alone, so phi is a function of q3. At all 32 bench / 61 held
     stop-engaged poses, phi = 10.87 deg exactly.
   - So the stop IS a dowel on J3's own angle, at **q3' = 96.87 deg**. The CAD groove must be cut there, not at 86.
   - A dowel at q3' 86 is a different, worse design: fast 11.22 plain / 12.36 near, against 9.56.
   - Fit-bench sweep of a q3'-reading stop (74 / 80 / 86 / 92 / 98 / 104): 20.62 / 20.97 / 12.36 / 10.75 / 9.59 / 10.84
     near-touch. 98 reproduces the claim's 9.56, which confirms the mapping (`verify_q3own_stop_fit60.json`).
3. **Fold margin read two ways (the auditor's T3, ruled here).** The model scores state 2 on the effective dyad's th
   margin: min 9.60 bench / 8.62 held. The claim's flood applies the family margin min(m_sub, m_eff) to every forced state,
   where m_sub is the J1-K-J3 sub-chain with J2 rigid (state 1's moving chain).
   - Under that reading, 8 taken bench poses sit below 5.5, all in state 2: the 4 ws poses 291 / 315 / 317 / 344 (which the
     flood drops) and the 4 clip frames 12 / 47 / 49 / 52 (0.76-4.28, still scored as taken). Held out the count is 13.
   - In state 2, J2 is free, and the chain that moves is the J1-K-J2 wrist. It is **>= 35.99 deg from coplanar** on the
     bench (37.56 held). For comparison, the state-A J1-J2-J3 chain gets as close as 23.1 deg.
   - So the J1-K-J3 margin is not a singularity of the state-2 mechanism. Ruling: the model's reading.
   - Re-running the flood with that one reading connects all 1136 nodes: 0 islands, 0 rule refusals, 0 jump refusals with
     dK included, 0 branch refusals. Connected = static = **16.20 bench / 21.89 held**. The claim's 17.35 / 22.67 mixed the
     two readings.
   - If the lead prefers the family reading, the consistent numbers are the auditor's 20.68 / 24.56, behind the lead.
   - Files: `verify_margins_{bench,held}.json`, `verify_onereading_{bench,held}.json`.
4. **Parts, sampling, pose-taking.** Cell B adds no skin-facing metal: the dowel and its groove sit inside J3's O20 stack. So
   the verified k33 kit harness applies unchanged:
   - metal and sampling: O20 hubs incl. crowns, links at their real section, member 3 and the knee, contact rings;
   - pose rules: closure < 0.5 deg, knee window, slide residual, part pairs, fit-clip continuity incl. dK.

   The oracle table is off in law mode (`ODesign.TAB = None`). q3max was picked on the fit bench (rows k 61-68), not on the
   claim bench. The binder-informed range is the auditor's P1.
5. **Paired vs the lead (static dumps, `verify_paired_vs_lead_static.json`).** Neither difference is significant: the gains
   are coin flips.

   | wear | cell B minus lead | CI90 | P(better) |
   |---|---|---|---|
   | bench | -2.08 | [-4.99, 2.98] | 0.745 |
   | held out | -0.49 | [-2.70, 2.13] | 0.62 |

   Cell B buys reach (+24 / +63 ws takes only it gets) and pays in contact: 13 / 37 contact poses only it has, against 2 / 4
   only the lead has.

Open (not run here):
- the J3 dowel force and the K-spring hold (R17 lag, preload);
- cuff twist with the stop engaged;
- the auditor's NEW-stop-refusal pricing: 343 / 423 are refused at the dowel, worth 0.48;
- convergence: a 1-D, 8-point q3max sweep, with the farm closed.

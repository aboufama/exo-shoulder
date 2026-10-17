# Acromion-pole relay 4R (acromion-relay-4r)

Round 101 (J1), pick 2. A plain O20 spherical 3R whose J1 walks the acromion-cap rim on a spring-centred J0 at the cap
pole. Its role this round is threefold:

- the plain-host control for pinknee-scapular-relay-4r (it isolates what the relay is worth without the pin knee);
- the shared full-grid continuity flood (`tools/spare_flood.py`), built and validated here;
- the stop-relay class re-measured under that corrected flood, reported as an INSTRUMENT change.

acromion-twinspring-4r is merged in as the "twin" determination cell (policy 1).

## Deeper-version prompt (answered before modelling, 2026-10-17 ~17:31 UTC)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Before tuning the relay, ask whether the relay can move the binder at all. The plain 3R's binder is hub 2, and
     J2 lies on the a2-circle about the humerus-fixed J3. A base-side spare moves J1, and through J1 it only slides
     J2 along that same circle. So measure hub 2's skin requirement per pose, with and without the relay, before
     spending CMA time.
   - Treat the instrument as a design input. The stop-relay died partly on a 360-node graph (157 components), so the
     flood has to be right before any number means anything.
   - Report the relay's worth in poses (static vs connected, overhead / 28), not just in gap points.
   - State the feel: the spring torque at the extreme relay poses, as cuff force.
2. **The rawest material.**
   - The posed skin itself, through the bench's signed-distance requirement along each hub axis
     (`K.requirement`, the K3 march).
   - The full 1432-node envelope grid of the workspace clip (`concept_bench._poses_all`, HG rotations), not the
     bench's 360 subsample.
   - The motion clips (follow).
   - The lead's lost poses (`docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json`).
   - The skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`, for the 1-3 mm spread at the cap
     pole that justifies seating J0 there.
3. **Methods and tools.**
   - tools/concept_kit.py: closure, O20 hubs, straps, K1-K7, dense K2 on q0..q3.
   - stop-relay-rocker-3r's crown / wall / near-touch extras.
   - The path-tracked full-grid flood `tools/spare_flood.py`.
   - CMA-ES (`tools/concept_cma.py`) on Bench(60,160) fast with the near-touch objective, islands dropped.
   - A frozen exact wear on Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench (Bench(60,160) fast, then Bench(110,360) exact frozen).
   - The flood validated against the judge's independent `graph.py` numbers: 0.67 on the 360-node graph, 0.91 on the
     full grid for the stop-relay section-5 setup.
   - The control: the same chain with T = 0 (relay locked) through the same code.
   - The red-team pose list below (rest, overhead, across the body, behind the back, the nearest-touch poses).
   - The adversarial verifier and the alignment auditor.

## The model (docs/concepts/models/acromion-relay-4r.py, on tools/concept_kit.py)

The chain, from the scapula handler to the cuff:

- **J0**: counted joint. O20 hub, axis c = bvec(az_c, el_c) through GH, at the acromion / supraspinatus cap pole
  (el_c 80-89.5). A preloaded double-leg torsion spring centres it against a base dowel, with own-angle stops at
  +-T.
- **link 0**: 12 x 3 Ti strap, arc a0. J1 rests at u1r = bvec(az_c, el_c - a0), on the cap rim below the pole.
- **J1**: O20.
- **link 1**: arc a1.
- **J2**: O20, with own-angle stops at a fold margin of m_lo / m_hi in th from each fold.
- **link 2**: arc a2.
- **J3**: O20, humerus-fixed, wdir(wd, wa).
- **K7 neck** to BOTTOM.

Totals: 4 joints, 0 passive, 0 passive translations, no slides, cables or gears. The metal is every hub at the real
O20 stack, with crowns and walls skin-checked, every strap at 12 x 3, and the neck.

**Determination (R17).**

- **Clamp, policy 0.** q0 is the least-|q0| state that keeps J2 inside [lo, hi]. While J2 is strictly inside its
  stops, the spring preload holds q0 = 0, and the chain is exactly the plain 3R. While J2 sits on a stop, the arm has
  pushed J0 the least amount. The J0-J1-J3 sub-chain then keeps >= m_sw (5) of fold margin.
- **Twin, policy 1, the merged acromion-twinspring-4r.** q0 is the local energy minimum of
  (q0 rad)^2 + k2 (psi2(th) - psi2r)^2, reached by descent from 0.

**Where the spec was corrected.**

- J1's whole travel must stay inside the J1 seat rule (az -110..135, el >= -20, x <= 0.2). The spec says to reject
  configurations that leave it. The model instead cuts T to the largest symmetric travel that stays inside, a design
  step reported as T_eff. Rejection would only have thrown away CMA samples.
- The flood seeds are every q0 = 0 grid node (the plain chain's region), not only the low-elevation nodes. This is
  the stop-relay / minarc convention: mode-A poses are the plain 3R, which no plain-3R row has to flood. The
  rest-only seeding reads within 0.003 of it (validation below).

**Continuity.** A ws pose with q0 != 0 counts only if the full-grid flood reaches its grid node in a state within
2 deg of the pose's own q0. Clip frames go through the kit's dense K2 on q0..q3. Held-out envelope poses are flood
transit nodes only: kinematics, no skin, nothing scored or tuned on them.

## The shared full-grid flood (tools/spare_flood.py): validation and the stop-relay re-measure

The flood runs on the full 15-deg envelope grid: 1432 nodes (17 planes x 12 elevations x <= 25 axial). The Bench(110,
360) ws poses are a 1-in-4 subsample of it.

- **Edges:** 2-deg HG slerps between grid neighbours.
- **State:** the spare's q0 is path-tracked, with up to 6 states per node.
- **Clamp step:** pushed to the nearest feasible q0 (<= 10 deg, otherwise a snap), then relaxed toward 0 inside the
  feasible component. The sub-chain margin is checked while J2 is on a stop.
- **Option:** one-sided relay (relay_lo / relay_hi), for the stop-relay's overhead-only cell.

Validation on the stop-relay section-5 setup (C-stream seats u1r = bvec(98.84, 64.44), J3 wdir(83.01, -15.19), a1 41.76
/ a2 72.34, m 10, T 75, pivot tilted 40 deg at phi 120). Kinematic, Bench(110,360) ws nodes, 3 s per flood:

| instrument | ws reach | overhead / 28 |
|---|---|---|
| plain (q0 = 0) | 0.650 | 11 |
| static (pose-local least-|q0|) | 0.922 | 24 |
| old instrument: flood on the 360 bench nodes only, mode-A seeds | **0.669** | 11 |
| full grid, rest seeds (elev <= 30) | **0.908** | 23 |
| full grid, mode-A seeds | **0.911** | 24 |
| T 0 control, full grid | 0.647 | 10 |

The flood reproduces the judge's reference numbers (~0.67 sparse, ~0.91 full) and the proposer's (0.669 / 0.908).
The stop-relay's "static gains are islands" verdict (its section 5: connected 0.667, overhead 0.393 for all 72 pivots)
was the 360-node instrument. On the full grid, 0.91 of the ws poses are reachable by continuous motion, and 23-24 of
the 28 overhead poses.

### The stop-relay re-measured under the full-grid flood (INSTRUMENT change, the design is unchanged)

stop-relay-rocker-3r C best (k4771: seats 98.84 / 64.44, a1 41.76 / a2 72.34, J3 wdir(83.01, -15.19), beta 28.83,
phi 324.51, m_lo 10.73 / m_hi 10.25, qmax 69.1, overhead-relay only), all hubs at O20 (the user's ruling: no O15).
Measured on Bench(60,160) fast with the kit checks, its own model file, and only connected() swapped:

| instrument | gap | reach | relay ws poses taken | islands dropped |
|---|---|---|---|---|
| static (connect 0) | 43.09 | 0.675 | 7 | - |
| old connected() (360-node bench graph) | **47.75** | 0.631 | 0 | 7 |
| full-grid flood (tools/spare_flood.py) | **43.09** | 0.675 | 7 | **0** |

The kinematic picture on Bench(110,360) ws: plain 0.644, sparse 0.647, static = full-grid connected = 0.764, and
overhead 11 -> 16 / 28.

- Under the corrected instrument, every static relay pose of the C best is reachable by continuous motion. The
  instrument change is worth 4.66 gap points on this config.
- The proposer quoted 43.37 -> 38.75. The direction and the sign agree; that pair was not reproduced on this config.
- The stop-relay's death still stands on its numbers. Its relay was lo-side only, and Bench(60,160) overhead reach is
  0 / 12 even statically. Its hub 2 is 0.70 in band at the back-of-shoulder seat, and reach is its limiter.

## Results (Bench(60,160) fast, kit checks K1-K7 + dense K2 on q0..q3, crowns / walls of all 4 hubs, near-touch objective, islands dropped by the full-grid flood)

Gate 0 is two CMA-ES runs: clampA from the pole60 cell and clampC from the pole20 cell, both sigma -1. A twin-cell run
was started and stopped after 1 configuration because the first twin flood was slow. Totals: 555 configurations,
sweep `docs/concepts/sweeps/acromion-relay-4r.json`.

**Best (clampC-g31-1)**, near-touch **42.74** (score 84.46), plain 41.62:

- Metrics: reach 0.875, follow 1.0, in-band14 0.503, in-band10 0.333, contact 0.005, min metal-skin 0.63 mm.
- Overhead: ws 6 / 12, clip 5 / 5.
- Margins: min th margin 5.05, min sub-chain margin 7.91.
- J0: q0 -11.5..+38.5 (T_eff 47). Relay ws poses taken: 14, and the flood dropped 0 islands (grid connectivity 0.836).

Parameters: az_c 43.15, el_c 88.23, a0 28.30, T 47.4, a1 50.21, a2 60.26, wd 92.03, wa -9.03, sigma -1, q 0.997,
m_lo 5.0, m_hi 5.01, lift1 1.08, lift2 1.08, end_extra 0.

Per member in band: hub 0 1.00, hub 1 1.00, **hub 2 0.06**, hub 3 0.72, link 0 1.00, **link 1 0.23, link 2 0.05**,
neck 0.72.

**The kill.** The best was 43.72 at 300 evaluations and 42.74 at 555. Both are above the lead's 30 line, so the class
DIES AT GATE 0 with that number, inside the judge's expected 38-45 range.

**Convergence gate** (merged, time order): +0.36 over the second half, +0.36 over the last third, top-5 spread 0.13 ->
converged. Per run: clampC 0.36 / 0.36 / 0.13, clampA 1.30 / 0.77 / 0.80 (best 45.82).

| configuration (same code, Bench(60,160) fast) | gap | reach | ib14 | note |
|---|---|---|---|---|
| proposer's pole20 45/70 cell (connect 0, plain gap) | **45.82** | 0.831 | 0.531 | reproduces the proposer's kit number exactly |
| best, relay on (flood) | **42.74** | 0.875 | 0.503 | |
| best, static (connect 0) | 42.74 | 0.875 | 0.503 | the flood drops nothing |
| **control: best with T 0 (relay locked = plain 3R)** | **51.58** | 0.788 | 0.502 | the relay is worth 8.84 gap points, all of it reach (+14 ws poses) |
| twin cell k2 0.5 / 2 / 8 at the best | 45.73 / 52.28 / 55.60 | 0.875-0.881 | 0.468 / 0.439 / 0.396 | J0 moves on 189-192 taken poses, hub 1 in band falls to 0.79 / 0.43, worse at every k2 |

## The binder, measured on the raw skin

Each pose's hub-2 requirement comes from the K3 march along hub 2's axis, over the taken Bench(60,160) poses at the
best config. The T 0 control is evaluated through the same code.

| | hub 2 fitted level F | link 1 / link 2 max level | hub 2 requirement p50 / p90 / max | hub 2 in band |
|---|---|---|---|---|
| best (relay on) | **124 mm** | 124 / 128 | 60 / 82 / 116 mm | 0.01 (ray proxy), 0.06 (all disc samples) |
| control T 0 | **124 mm** | 124 / 128 | 60 / 83 / 116 mm | 0.01 |

The poses that set hub 2's level:

| pose (plane, elevation, axial) | J2 position (S frame, az / el) | requirement |
|---|---|---|
| ws (-75, 60, +60), behind the body | 32 / 10 (posterior-lateral, low) | 116 mm |
| ws (0..30, 150, 0), overhead | 112-124 / 35-42 | 107-113 mm |
| ws (0, 105, 0) | | 110 mm |
| clip (30, 150, -60) | -37 / 42 | 109 mm |

**q0 = 0 on every one of them.** The binding poses sit inside the plain J2 window, where the spring holds J0 at rest
by construction. The relay never engages there, and the levels are identical with T = 0. A base-side spare cannot
move this binder:

- It acts only where J2 is on a stop.
- Where it does act, it slides J2 along its a2-circle about the humerus-fixed J3.
- Hub 2's level is set by mode-A poses in which J2 crosses the deltoid / acromion skin 107-116 mm out.

The relay's whole worth is reach: 0.788 -> 0.875, worth 8.84 gap points. It moves neither the in-band (0.502 ->
0.503) nor hub 2.

The champion-family numbers make the same point. At the stop-relay's back-of-shoulder seat, a 41.8 / 72.3 dyad keeps
hub 2 0.70 in band but reaches only 0.675. At the cap pole, a 50 / 60 dyad reaches 0.875 with hub 2 at 0.06. On
these two cells, the plain O20 3R trades reach against hub 2's height. The spare buys reach on top of either one;
it does not break the trade.

## Red team (own best config)

- **The pose that pinches.** ws (-75, 60, +60), behind the body with external rotation: metal 0.63 mm from the skin.
  It is the same pose that sets hub 2's level. The overhead poses (plane 0-75, elevation 150-165) are taken at
  1.58-2.06 mm, at the lower edge of the band.
- **The poses that jam** (not closable at margin 5). Across the body at elevation 90 with IR (plane 105-120, axial
  -120), and overhead at plane 90-120, elevation 150-165. These are the J2 fold windows that the relay's
  sub-chain margin (>= 5) refuses to relay through.
- **The motion preview** (docs/concepts/viz/concepts/acromion-relay-4r.js, `node docs/concepts/viz/test.mjs`) runs
  the rest -> raise -> overhead -> abduction -> across -> behind loop. It flags 3 frames where J2 sits on its low stop
  and J0 cannot relay (the J0-J1-J3 sub-chain is within 5 deg of its own fold). It also flags 1 least-|q0| root switch
  that a real J0 cannot follow. Both are drawn red, not smoothed. The flood applies the same rule to the ws grid, and
  the bench's ws relay poses were all reachable (0 islands).
- **The optimistic number.** The fit-bench 42.74 reads 44.63 with K6 at 1 mm radial clearance (the frozen protocol).
  The frozen exact Bench(110,360) wear is below.
- **Feel.** Max |q0| over taken poses is 38.5 deg. With the clock-spring pair (0.08 N.m preload, 0.015 N.m/rad),
  J0 needs 0.090 N.m, which is 0.69 N at the cuff (130 mm) while J2 sits on a stop. The twin cell is felt
  continuously: J0 moves on 189-192 / 201 taken poses.
- **Not done (time box).** The per-pose hub-2 table on the lead's 88 fold losses
  (docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json). The binder table above answers the same
  question on this chain's own fit poses: the relay does not engage where hub 2 is bound.

## Frozen exact wear (Bench(110,360), CB_EXACT=1, levels fitted on Bench(60,160), K6 at 1 mm radial)

| | gap (plain) | near-touch | reach | overhead / 28 | follow | ib14 / ib10 | contact | min metal |
|---|---|---|---|---|---|---|---|---|
| fit, Bench(60,160) fast, K6 1 mm | 44.63 (near-touch) | | 0.856 | | 1.0 | 0.503 | 0.005 | |
| **frozen exact Bench(110,360)** | **51.83** (score 81.15) | 53.94 | **0.789** (284 / 360) | **10** | 1.0 | 0.503 / 0.337 | 0.010 | 0.51 mm |

More from the frozen wear:

- Relay ws poses taken: 17. Islands dropped by the flood: 0.
- Min th margin 5.00, min sub-chain margin 5.57. q0 range -36.5..44.0.
- Per member in band: hub 2 0.057, link 1 0.23, link 2 0.05.
- For reference: the lead is 18.49, and the champion through the same checks is 66.97-75.94.

**Control, same shape with T 0 (J0 locked = plain O20 3R), frozen exact:** 56.40 plain / 58.56 near-touch, reach 0.742,
overhead 10 / 28, ib14 0.502, contact 0.008.

On the big bench the relay is worth **4.57 gap points**: +17 ws poses of reach, **0 overhead poses**, and in-band
unchanged. The relay poses are stretched / IR-across poses, not overhead. Where the folded overhead poses are
lost, J2's stop sub-chain cannot relay them at margin 5.

## Verdict

**DEAD at gate 0.** The near-touch gap is 42.74 (plain 41.62, score 84.46) on Bench(60,160) fast, after 555
configurations. The sweep is converged, and the number is well above the lead's 30 kill line at 300 evaluations. The
judge expected 38-45; this is inside it.

What the class taught (new knowledge, beyond this morphology):

1. **The continuity instrument.**
   - A spring-centred base spare's static relay poses are reachable by continuous motion once the flood runs on the
     full 1432-node envelope grid: stop-relay 0.764 = static on Bench(110,360), and 0 islands at this chain's best.
   - The stop-relay's "islands" were the 360-node graph: 157 components, 47.75 -> 43.09 on its C best at O20.
   - Every future redundant / relay / spring design should use `tools/spare_flood.py` (or the minarc verifier's
     `flood(grid="full")`), never a flood over the bench poses alone.
2. **A base-side spare buys reach only.**
   - The relay engages only where J2 is on a stop.
   - The plain 3R's in-band binder (hub 2 / links 1-2 out at 124-128 mm) is set by mode-A poses: behind the body
     with ER, and overhead in the scapular plane. The spring holds J0 at rest there.
   - So reach +0.09 on the fit bench (8.8 gap points), and +0.047 frozen exact (4.6 points, 0 overhead poses);
     in-band +0.001. The twin spring, which moves J0 everywhere, costs hub 1 / link 0
     in-band and loses 3-13 points.
   - This bounds pinknee-scapular-relay-4r too. The relay can add at most the host's fold-limited reach. Whether
     that survives depends on the host's hub 2 staying at its own level on the relay poses (the judge's 0.53-0.68
     survival).
3. **The plain O20 3R's reach / hub-2 trade at two seats.**
   - Back-of-shoulder seat, 41.8 / 72.3 dyad: hub 2 0.70 in band, reach 0.68.
   - Acromion-cap pole, 50 / 60 dyad: hub 2 0.06 in band, reach 0.88.
   - Neither seat gets both. The lead's knuckle family is what breaks the trade.

**What happens next (altitude).**

- Nothing more on this class. The flood is shared: pinknee-scapular-relay-4r uses `tools/spare_flood.py` with its own
  q0 policy.
- The open lever this control points at is the one the round plan lists first: remove th's axial dependence with a
  humerus-axial J3, which changes which poses bind hub 2. A base-side relay does not change them.

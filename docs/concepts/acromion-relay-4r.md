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

## Results

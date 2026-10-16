# Discovery rounds

One section per round: **plan** (written by the round's planner), **picks** (the ideation judge), **results** and
**lessons** (the round's closer). Score = 100 (1 - gap / 275) on Bench(110,360) exact with the frozen-shape protocol
(fit Bench(60,160) fast, wear the shape on Bench(110,360) exact). A number counts only after an independent verifier
re-measures it. Score 95 = gap 13.75. Complexity (tools/simplicity.py, docs/SIMPLICITY.md) is shown next to the score
and is not folded into it.

Rounds 1-4 below were backfilled by the round-5 planner from the catalogue, the rows, docs/concepts/events.jsonl and
docs/concepts/round3_ideation.md. Rounds 5+ are written as they run (scratchpad `discovery-loop.js`).

## Rounds 1-2 (2026-10-15): morphology swarm and seeds (backfill)

- **Plan**: seed families (distributed DOF, remote centre, closed loop, serial topology, body hugging), then ~60
  catalogue morphologies screened with the shared kit (tools/concept_kit.py) and verifiers.
- **Results**: almost every rail / ring / shell / parallel family died on one radius over a moving skin. Examples
  (verified or screened gaps): crown-ring 82.37, meridian-goniometer 102.5, seed-arc-rails 73.0, rail-elbow 64.7,
  seed-spm-3rrr 193.44. Survivors: the spherical 3R champion (75.94 on Bench(110,360) exact; 66.97 under the round-3
  verifier's check set), seed-offset-3r-slides (verified 66.47), offset-skin-normal-3r (osn k4216, verified 42.59).
- **Lessons**: rigid metal in band needs hubs on GH rays at quiet skin. One-radius tracks cannot follow the skin.
  Every 3R loses the same poses to the J2 fold (docs/FINDINGS.md "The J2 fold is not a hard limit").

## Round 3 (2026-10-16 ~01:00-04:10 UTC)

- **Plan / lenses**: self-alignment / loop closure through cheap rotational passive joints; a zero-passive spherical
  chain that parks hub 2 by placement; a graded-fraction J1 behind / on top of the scapula; J2 as a short curved rail.
- **Picks**: spine-parked-j2-3r, skin-normal-3r-pin-knee, skin-normal-3r-knuckle-cufflink, closure-set-arc-knee-3r,
  acromial-rocker-3r, j2-arc-sector-3r (docs/concepts/round3_ideation.md).
- **Results (verified, Bench(110,360) exact frozen)**:

  | design | v_gap | score | reach | in-band14 | complexity |
  |---|---|---|---|---|---|
  | skin-normal-3r-pin-knee k4598 | 30.35 | 88.96 | 0.606 | 0.904 | 21.5 |
  | raglan-knee-3r k1284 | 31.52 | 88.54 | 0.600 | 0.902 | 21.5 |
  | skin-normal-3r-knuckle-cufflink k1187 | 31.89 | 88.40 | 0.617 | 0.871 | 32.25 |
  | spine-parked-j2-3r k7008 | 34.29 | 87.53 | 0.594 | 0.878 | 0 |

  Died: closure-set-arc-knee-3r refuted at 75.28 (in-band 0.49), acromial-rocker-3r 125.84 (the rod passes its dead
  point), j2-arc-sector-3r 71.53 (the rail is 0.03 in band).
- **Lessons**: every 3-joint class is capped by the fold at 0.59-0.62 frozen reach. Seats, knees, slides and routes do
  not move the fold. The fast-to-frozen reach loss (0.694 -> 0.606) comes from the pose sample: the window was tuned on
  160 poses and is worn on 360. It is not a skin effect. The honest pin stack costs ~1.2 gap per mm.

## Round 4 (in flight at the time of the round-5 plan, 2026-10-16 ~05:30 UTC)

- **Plan / lenses** (aimed at the J2 fold): j2-path (hub 2 on scapula-side skin at fold-free axes, virtual J2s),
  fold-lever (a determined coordinate that moves the fold boundary), four-dof (an honest 4th joint), hardware
  (thin-section parts, low stacks).
- **Screening at the time of writing**: stop-relay-rocker-3r (first best 35.24 fast, coarse 37.14) and
  dwell-fourbar-knee-3r (lead proxy 21.8) in slice r4-A. The round-4 judge's picks are still to land in the
  catalogue.
- **Measured by the four-dof lens (self-measured, NOT verified)**: a spring-centred, sensed 4th joint on the
  spine-parked seats (park4) scores frozen exact gap 22.36 (score 91.87). Reach 0.750, in-band14 0.864, contact
  0.038 (7 crown contacts). In band: link 3 0.51, hub 4 0.86. The 4th joint moves on 20 % of poses (deflection p95
  56 mm). Ring 4th: 37.40.
- **Results / lessons**: to be written by the round-4 closer.

## Round 5 plan (2026-10-16 ~05:30 UTC, track main, lead verified gap 30.35)

### State

- **Leader**: skin-normal-3r-pin-knee k4598, v_gap 30.35 (score 88.96). Reach 0.606, in-band14 0.904, follow 1.0,
  contact 0.009, 0 passive translations, complexity 21.5 (10 of it is the two sensed knee pins). The simplest
  verified design is spine-parked-j2-3r: 34.29 at complexity 0. Final polishes of both are running on
  Bench(110,360).
- **Where the leader loses poses** (docs/research/reach/summary.json): it takes 218 of 360 workspace poses.
  - 76 are lost **stretched**: th = angle(J1, J3) above a1 + a2 - 10 = 102 deg. These include 47 of the 68
    across-body poses.
  - 57 are lost **folded** (th below 42).
  - Only 9 are lost to contact, part collisions or the slide window.
  - Overhead: 7 of 28 taken. Every clip frame is taken (110 of 110).
  - The fold costs ~29 of the 30.35 gap points (reach 0.611 alone costs 28.9, docs/concepts/round3_ideation.md).
- **What 95 needs**: reach >= ~0.77 at in-band >= 0.88, follow ~1.0 and ~0 contact.
- **Kinematic ceilings** (docs/research/reach_attribution.md, m = 10 deg):
  - The leaders' window is 42-102 deg. The workspace needs th 26-140 deg (5-95 %), and overhead alone spans 18-146
    deg, off both ends, so only a wider or a second window rescues overhead.
  - Plain 3R, best seats at the leaders' arcs: 0.74-0.78. Local seat re-tuning of +-15 deg adds 0.036-0.064.
  - A wider a1 sends hub 2 off the skin: 93-115 mm off GH at the pin-knee seats, 186-400 mm at the spine-parked
    seats for a1 >= 55.
  - Per-pose-free J1 rocker of travel beta: 0.77-0.81 at beta 20, 0.84-0.88 at beta 30.
  - Two-state arc relay in link 1 (a1 -> a1' 77-84): 0.93-0.95, overhead 0.89-1.00. It has never been modelled.
  - Relay on a2 (a2' 129-132): 0.82-0.84.
  - A coupled schedule is <= the per-pose-free rocker of the same travel.
  - A redundant 4R folds only with all four axes coplanar (~1.0).
- **Margin (a measurement fact, not a design lever)**: for the leader, the in-window share is 0.631 at m = 10,
  0.681 at m = 5 and 0.722 at m = 2. The bench keeps m = 10. Any change to m would be a measurement change and has
  to be reported apart from design gains.
- **What died, and why**:
  - Fold-free seats lose the band: spine-parked anterolateral seats reach 0.89 at in-band 0.15-0.30.
  - The stop-relay deltoid-pivot relay reaches 0.95 kinematically at in-band 0.20.
  - The closure-set arc knee: in-band 0.49 and branch jumps.
  - The acromial rocker rod passes its dead point in 61-171 of 220 poses.
  - J2 arc rails, crown rings, tracks and shells: one radius over moving skin.
  - Two cuff slides buy nothing over zero passives on the exact bench (osn 43.36 vs 41.73).
  - Free spare joints sag within 0.1 s unpowered (docs/FINDINGS.md "Unpowered tracking (MVP1) needs exactly 3 DOF").
- **Open levers**:
  - A 4th coordinate that is determined: a detent or relay, a schedule, or a loop.
  - Seats chosen so that a lever's second state parks its hubs on quiet skin.
  - Lower complexity on the leaders: unsensed passives, no springs.

### Lenses

1. **keemink-4r-band (reach)**: a redundant non-orthogonal 4R (Keemink et al. 2018, IEEE TNSRE 26(4):817-829) laid
   out as a whole for the 1 cm band, inside the 4-joint cap.
   - **Determination**: the spare coordinate must be determined without a free joint. Measure, per pose, the
     null-space interval that closes and keeps every member in band. Then take the cheapest determination that covers
     >= 90 %, in this order: a two-position detent or hard-stop relay (model the link-1 a1 -> 77-84 relay first), a
     J2-driven schedule, and only last a spring-centred sensed 4th.
   - **Difference from round 4's park4**: park4 is the spine-parked 3R with a spring-centred 4th bolted on. Here all
     four axes and the hub rays are placed together, the singular coplanar set is put outside the workspace, and the
     switch is checked for continuity and sag with judge/dynamics.py.
2. **reseat-for-union (reach, from the placement side)**: Harmony / MGA / CADEN-7 place singularities by tilting
   axes. Here, choose J1's seat on the user's scapula handler and J3's seat on the humerus so that:
   - the poses the chain gives up are the ones the bench needs least, and
   - every hub, in every state of the lever, sits at a GH-ray pierce point over quiet skin in the poses it serves:
     either pierce point of its axis line, or a bearing pair split onto both.
   - Measure seat sets first with ceilings.py, relay_parking.py and the skin-motion map / proximity atlas.
   - A seat set wins only when it lets a lever's second state park its hubs in band. The 3R seat ceiling alone
     (0.74-0.78) cannot reach 0.77 after the band costs.
3. **determined-lever-lowcx (low complexity)**: the simplest fold lever that tracks unpowered.
   - **Rules**: 0 springs or flexures, 0 sensed passives (the arm's orientation must be an exact function of q1-q3),
     0 passive translations. Extra coordinates are set by pin / rod-end loops, with at most one roller-in-slot.
   - **Directions**:
     - a spherical four-bar base whose coupler is link 1, so a1 varies with the crank (coupler-path-j1);
     - a scapula-fixed slot that steers a 4R's spare joint, with dwell (cam-coupled-4r);
     - a pin parallelogram knee that is orientation-neutral, so it needs no encoders (saves 10 of the pin knee's 21.5
       complexity points);
     - merged bodies.
   - **Target**: score >= 95 at complexity well below 21.5.

### Carried over (ideated or interrupted, never screened)

- **coupler-path-j1** (ideated 2026-10-15, before the fold law). As a fold lever: J2's axis direction runs along a
  spherical four-bar coupler curve instead of a circle about J1. Pins only, so no spring and no sensor. Test the
  window per configuration by IK first.
- **cam-coupled-4r** (modelling interrupted 2026-10-15). A determined 4R with an S-fixed slot. Re-seed it from park4's
  frozen parameters (a1 37.6, a2 60, a3 22.3) and fit the slot to park4's per-pose 4th angle. Risks: the slot plate in
  band, and a coupled schedule is <= the free 4th.

### Elsewhere, not to be duplicated

- stop-relay-rocker-3r and dwell-fourbar-knee-3r (slice r4-A).
- skin-normal-3r-pin-knee and spine-parked-j2-3r (final polish on Bench(110,360)).
- The round-4 judge's picks, still landing, including the four-dof park4 4R.

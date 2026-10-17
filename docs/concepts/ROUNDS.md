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

## Round 5 results (2026-10-16 ~07:12-10:55 UTC; cut short by the lead, written by the round-6 planner from the files)

The lead stopped the round at 10:55 UTC: its last modelling agent (cam-coupled-4r) had run 2h20m against a 75-min
box. Picks: minarc-stop-knuckle-4r (variant B = pin-knee-minarc-knuckle-4r merged) and short-a2-arc-slide-3r (round-5
judge, docs/concepts/round5_ideation.md); carried: coupler-path-j1, cam-coupled-4r.

| design | best fast Bench(60,160) | frozen exact Bench(110,360) | verifier | complexity | status |
|---|---|---|---|---|---|
| minarc-stop-knuckle-4r B (pin knee + spring knuckle K + J2 stops) | 6.19 | claimed 15.42; **18.45 with the stops at the 5-deg margin** (reach 0.747, in-band14 0.889, contact 0.021, near-touch 24.26; held out 22.27 vs H1 31.39) | REFUTED as claimed (stops 1.37 / 1.88 deg from the J1-J3 fold); 18.45 from 3 harnesses, continuity 0 dropped; a q2 stop + 0.3x5 spring 17.32 (1 lens) | 33 | kit-rule claim in flight elsewhere |
| minarc-stop-knuckle-4r A (plain spherical chain + K) | 22.17 (reach 0.856, in-band 0.78; near-touch 41.79) | - | - | 13.5 | kit-rule CMA in flight elsewhere |
| short-a2-arc-slide-3r | 29.38 | 41.19 (self) | REFUTED 55.3 (real slide stack: hub 3 +1.6 mm; the sensed slide makes it 4 active) | 14.75 | refuted |
| coupler-path-j1 | bound 20.58 = the leader's 20.63; honest 30.52 | - | DEAD (8937 configs, 6 gated streams collapse B0 onto A0; audit confirmed) | - | dead |
| cam-coupled-4r | 41.66 RED-TEAMED (groove cuts J1's O20 housing; 176.8 with the housing rule); **50.67 honest** under the rule (reach 0.90, follow 0.95, in-band14 0.40) | - | - | 11.75 | screened, not a contender (rows/cam-coupled-4r.json) |

Measured beside the round: the zero-complexity class ceiling VERIFIED at 31.04 (fit-110) / 33.51 (verifier fit-60)
by a GPU near-exhaustive search (560 k Sobol + 130 CMA; frontier in-band 0.89 / 0.76 / 0.64 / 0.52 at reach 0.63 /
0.70 / 0.75 / 0.80); polish 2: H1 stays (C1 23.04 vs 24.48 in-sample, +0.33 held out); fold-widening 3-passive
coupled J1 rocker: kinematic reach 0.731 -> 0.842 connected, 0.775 with hub 2 parked in band (gate 0.78), not
catalogued; fold-stop feel at B's 1.37-deg stop: J2 rate ratio 6.36 (kit rule 3.45, H1 3.15), cuff friction 0.39 N.

Lessons:
1. **Fold margins are read in the kit's J1-J3 metric, and stops act on a joint's own angle.** Minarc's interior-angle
   clamp put its stops 1.4-1.9 deg from the fold (15.42 vs 18.45 at the true 5 deg); its "J2 stop" acted on a virtual
   angle that no dowel can stop (q2 drifts 14.3 deg as K opens).
2. **A passive coordinate that must be read to know the arm pose is an ACTIVE DOF** (the user's counting rule): the
   Hall-sensed slide made short-a2 a 4-active design, and the skeptic counts minarc's K (sensed in its forced states)
   as 4 active. A fold lever that keeps 3 active needs its extra coordinate to be a function of the three readings.
3. **The knuckle is the only lever that has lifted frozen reach above 0.74 at in-band >= 0.88** (+6-9 points over H1
   at its seats; held out 22.27 vs 31.39). K never moves on the clips: its gain is static workspace reach. Without the
   pin knee (variant A) the J3 side loses the band (link 2 0.43, hub 3 0.70, neck 0.68).
4. **Base-side schedules give the window and float hubs 2 / 3.** A coupler covers 0.967 of the poses by IK vs a plain
   circle's 0.978 (the window is set by arcs, not path); a slot that fixes the spare un-fixes J3 from the humerus.
5. **K6 cannot see a groove that shares a body with a hub** (joint partners within 12 mm of J1 are exempt): any slot
   or cam on a hub's body gets the housing rule before its number is reported.
6. In-sample polishes lose ~5 points held out: final polishes score held-out poses (2-fold cross-fit).
7. Time boxes hold: report the measured reason and stop when the red team kills the number.

## Round 6 plan (2026-10-16 ~11:10 UTC, track main, lead verified gap 24.48)

### State

- **Verified leaders** (Bench(110,360) exact, frozen shape, margin 5, O20):
  - skin-normal-3r-pin-knee H1 (polished): **24.48** (score 91.1) on the polish protocol; 27.20 on the round-3 protocol
    (fit Bench(60,160)); held out 30.73 (31.39 in the minarc harness). Reach 0.658, in-band14 0.895. Complexity ~21.5,
    10 of it for the two sensed knee pins. Gen-3 CAD (user_pinknee_h1) not refuted, 8 of 19 judges.
  - raglan-knee-3r 27.82; skin-normal-3r-knuckle-cufflink 29.10; zero complexity: zc-frontier-3r 31.04 / 33.51 = the
    class ceiling (verified); arm-parked-knee-4r 26.71 is 4 active (fails R5-aim).
  - **Best measured, not a verified leader:** minarc B at the 5-deg margin 18.45 (score 93.3), held out 22.27,
    complexity 33, counted 4 active (K sensed). Its kit-rule claim and verifier run elsewhere.
- **Measured limiters.**
  - Every 3-active verified design: the fold, 94-96 % of the lost workspace. Overhead reach is 0.25-0.29; overhead
    needs th = angle(J1, J3) of 18-146 deg, off both ends of every 3R window.
  - Zero-complexity frontier: in-band 0.89 / 0.76 / 0.64 / 0.52 at reach 0.63 / 0.70 / 0.75 / 0.80. At complexity 0
    the window 95 needs puts hub 2 + link 2 or the J3 side over skin spanning more than the 12 mm band.
  - minarc B at 5 deg loses 56 poses to the fold (stretched past stop B, a1max 66; folded with J1 ~ J3), 16 to the
    knee window, 9 to contact; overhead 8 of 28; hub 3 0.66 and link 2 0.78 in band; min metal 0.05 mm overhead.
  - minarc A (13.5): in-band 0.78, all on the J3 side (link 2 0.43, hub 3 0.70 at F 101 mm, neck 0.68; hub 1 / K /
    hub 2 / link 1 0.93-1.00).
  - Parking: a second fold state needs hub 2 at median 70-73 mm, p90 153-226 (state A 51-57); 27-35 % of the
    rescued poses park at 60 mm.
- **What 95 needs from the best measured design**: 18.45 -> 13.75, i.e. +0.05 reach (0.747 -> ~0.80) at in-band
  0.889, or overhead 8 -> ~20 of 28, with contact <= 0.01.
- **Dead, with the reason**: base-side schedules (coupler-path-j1: arcs set the window; cam-coupled-4r: hubs 2 / 3
  roam, groove on hub 1's crown); slides under a hub (short-a2: hub 3 0.33 in band, sensed = 4 active); slotted
  eccentric K (115.21: knee / track leave the band); dwell four-bar (37.66: moves only the window's low end); stop
  relay rocker (static islands); longer knee link (0); 2 cuff slides; closure-set arc knee; acromial rocker (dead
  point); any 1- or 2-passive closure (re-parametrises the rotation about w, the fold law is unchanged).
- **Open levers**: a K that the three readings determine (3 active); knuckle seats chosen for the overhead and the
  J1-J3 alignment set; the J3 side in band without the pin knee; the coupled J1 rocker with the hub-2 gate (0.775,
  0.005 short of its gate).

### Lenses

1. **cam-stop-knuckle (determination: 3 active, no K sensor, complexity <= 12).** The one-sided relay's (q2, K) set
   is an L (K on stop A, or J2 on its stop): one scalar. Make it a curve K = max(K_A, c(q2)) that q2's encoder reads:
   the J2 hard stop becomes a cam lobe on link 2's side of hub 2. Past q2 = s it bears on a follower on link 1b and
   opens K as q2 keeps turning, with the spring holding K on stop A or on the lobe. Force closure acts near the
   stretched end only, with no slot over the full travel and no track plate (the parts that sank the slotted
   eccentric and the dwell four-bar). Other determined laws: a lobe reading q1; an RSSR rod (round-5 rank 3, in-band
   proxy 0.79); one draw-wire reading across K and J2 (sensing only). Gates before metal:
   - th(q2) is monotone through the lobe, and the 5-deg margin holds in the J1-J3 metric with stops on q2's own angle;
   - the pressure angle stays <= 45 deg, and the J2 rate ratio stays near H1's 3.15 (kit rule 3.45);
   - the lobe + follower fit inside hub 2's O20 envelope (housing rule).

   Then run the kit, the near-touch CMA, frozen exact and the full-grid flood fill.
2. **overhead-seat-knuckle (reach >= 0.77 at in-band >= 0.88).** Place the whole knuckle chain for the overhead and
   across-body ends, as a redundant non-orthogonal 4R (Keemink 2018 TNSRE 26(4)) whose singular sets are put outside
   the workspace by axis placement. The pin-knee seats it inherited were not chosen for that. Levers:
   - J1 on the back of the shoulder (posteromedial: the kinematically best seats, never tried with a knuckle), so the
     J1-J3 alignment set leaves the overhead cone;
   - a1max raised past 66, with the open state's hub-2 / link-1b parking gate measured first;
   - an arm-side K (link 2 split, a min-arc law on a2) if it parks better;
   - a two-sided K only if it is determined without a sensor.

   Target: frozen exact reach >= 0.77 and overhead >= 14 of 28, at in-band >= 0.88 and contact <= 0.01.
3. **j3-side-band (the 4th joint replaces the pin knee).** Variant A's in-band loss is the J3 side alone. Fix it with
   zero-cost levers searched together with the seats, as a new morphology id (variant A's own CMA runs elsewhere):
   - the inverted J3 stack (j3-neck-over-3r: +0.023 in-band on the spine-parked 3R);
   - deltoid-crest J3 seats;
   - raglan link-2 routing (raglan-knee-3r 27.82);
   - a short member 3 (crest-knee's 65 mm);
   - the underside quantile q.

   Target: in-band >= 0.88 at frozen reach >= 0.75, complexity <= 14 (<= 9 with lens 1's sensor-free K).

### Carried over (catalogue, ideated or interrupted, never screened)

- **cam-unfold-4th** (round 1, modelling interrupted; docs/concepts/models/cam-unfold-4th.py exists). Link 2 with a
  cam-slaved knee K = c(q2) from a cam ring around J2: the closest catalogued sensor-free knuckle. Screen it as lens
  1's arm-side variant: a pin on a bearing pair instead of the +-18 deg flexure (minarc's K travels ~28 deg), a
  one-sided lobe near the stretched end, minarc's seats.
- **j3-neck-over-3r** (round-4 judge pick). Standalone it is a complexity-0 3R inside the verified zc ceiling (the GPU
  search covered all four stack orders). Screen it only as lens 3's J3 side on a knuckle chain.
- Not carried: deltoid-crest-j3-3r and crest-knee-3r (their judge red teams measured +0.017 frozen reach, ~1-2
  points); slotted-eccentric-pin-knee-3r (its plain-3R sibling refuted at 115.21, in-band slack 0.003).

### Elsewhere, not to be duplicated

- minarc-stop-knuckle-4r: kit-rule claims of A and B (models/minarc-stop-knuckle-4r-kitrule*.py,
  verify/minarc-kitrule/), then a verifier.
- skin-normal-3r-pin-knee: the GPU massive polish (tools/gpu_knee_search.py) and the gen-3 CAD fix (user_pinknee_h1b).

### Needs the user's say (listed, not screened)

- A fold margin below 5 deg: minarc's 15.42 sits at 1.4 deg.
- Whether a sensed passive used only for static extremes may count as passive. The rule today counts it active, so
  minarc B and arm-parked-knee-4r are 4 active and fail R5-aim.
- J1 seats off the back of the shoulder and the acromion top.
- A radial slide that lets hub 2 change level with the state. It stands up by its travel plus block, which is against
  the 1 cm rule.

## Round 6 results (2026-10-16 ~11:10-14:31 UTC; closed by the round-6 closer)

Picks (round-6 judge, docs/concepts/round6_ideation.md): geneva-tail-knuckle-pinknee-3r (pick 1, with
lobe-rocker-pushrod-knuckle-3r merged in as its fallback embodiment) and geneva-tail-knuckle-3r (pick 2, with the
crest-basin seats of knuckle-crest-hub3-4r). Carried over: cam-unfold-4th (lens 1's arm-side variant) and
j3-neck-over-3r (lens 3). Lens 2's candidates (alignment-free-knuckle-4r, alignment-free-swivel-4r,
across-end-knuckle-4r) were rejected at ideation: each has a sensed K (4 active), and the J3 side refuses them (hub 2 /
link 2 at 0.00-0.20 in band).

All numbers below are frozen exact on Bench(110,360), at the 5-deg margin with O20 hubs only, fitted on Bench(60,160)
(the round-3 protocol), and confirmed by an independent verifier.

| design | fast Bench(60,160) | frozen exact (verified) | held out | active | complexity | status |
|---|---|---|---|---|---|---|
| **geneva-tail-knuckle-pinknee-3r** (rod embodiment) | 16.53 | **23.57** (score 91.43). Reach 0.731, follow 1.0, in-band14 0.844, contact 0.011, near-touch 25.21, overhead 8/28. | 28.12 | 3 (K driven by a lobe, never read) | 42.5 | **verified: round winner** |
| cam-unfold-4th (C3 crown cam, two-sided lobe) | 22.02 | 26.70 (score 90.29). Reach 0.656, in-band14 0.889, contact 0.012, near-touch 28.40, overhead 8/28. | - | 3 (K = c(q2)) | 33.75 | verified, not a leader (ties H1 27.20) |
| j3-neck-over-3r (variant A + inverted J3 stack, C6) | 22.87 | 28.46 (score 89.65). Reach 0.739, in-band14 0.835, contact 0.058, min metal 0.00 mm, overhead reach 0.18. | - | **4** (K sensed) | 13.5 | verified, not a contender |
| geneva-tail-knuckle-3r (beside tail, no pin knee) | 39.36 (39.34 reproduced) | 53.32 (score 80.6, self) | 59.55 | 3 | 14.0 | DEAD (death audited: gate converged, no model bug) |

Same-protocol references: H1 27.20 (24.48 on the polish protocol, held out 31.39 in the minarc harness); minarc BDp
19.54 and pick1 18.40, both verified but 4 active (K sensed); the zero-complexity ceiling is 31.04.

**Winner: geneva-tail-knuckle-pinknee-3r**, verified at 23.57 (score 91.43), 0 passive translations, complexity 42.5.

- **Against the previous verified lead (24.48):** it beats it, by 0.91 across protocols. On the same protocol it beats
  H1 by 3.63 (27.20) and held out by 3.27 (31.39). It is the new leader of the 3-active class.
- **Against the 4-active knuckle:** the sensed minarc pick1 / BDp (18.40 / 19.54) is still 4-5 points ahead.
- **What the verifier changed:** the claim was 23.37. The verifier found the horn and rod-end head inside K's +6 mm
  spring cap and rod vs hub K unchecked; fixed, this costs +0.20. The full-grid continuity drops 0 poses.
- **Open buildability items (not scored):**
  - the lobe reaches ~10.9 mm radius, 0.9 mm past the O20 skirt;
  - the pressure angle is 41.4 deg;
  - rod-end play gives ~1.2 deg of K per 0.05 mm;
  - the spring against gravity and the reflected J2 torque (3.18 tau_K) are not checked.

Lessons (measured):

1. **A determined K works: the fold relief is now 3 active.** Two sensor-free laws are verified at 3 active:
   - a lobe in hub 2's O20 stack driving a rocker, pushrod and horn: 23.57;
   - a two-sided crown cam K = c(q2): 26.70.

   Each pays for it in complexity (42.5 / 33.75 vs H1 21.5). Neither matches the sensed stop law: on the same chain the
   sensed K is 4-5 points better (pick1 18.40, BDp 19.54).
2. **Swept-volume rule.** A follower rigid with link 2 sweeps a surface of revolution about u2 through J2's whole range,
   and that sweep, not its pose at engagement, sets its height over the skin.
   - The Geneva tail cost 10-42 points on pick 1 (best 37.00 frozen) and 9.3 points on pick 2.
   - A lobe inside hub 2's own stack cost ~4.7.

   Put coupling elements inside existing hub stacks, or on members that do not sweep a joint's range.
3. **Fold levers belong on link 1 or at J2, never on link 2** (cam-unfold-4th K-atlas, 175 poses). A hub on link 2
   moves with q1 x q2 and sweeps a 2-D skin patch:
   - it is in band only 21-40 deg from J2 (0.75-0.77);
   - toward J1 it clashes with hub 1;
   - along link 2's line it has no leverage on a2.

   The same O20 disc on link 1 is >= 0.92 in band over a wide arc.
4. **A positive-drive cam allows a TWO-SIDED fold law**, which a spring knuckle cannot have. On cam-unfold-4th the
   folded-end lobe took 18 fit poses and gave most of the +8.8 points over its same-seat controls (rigid K 30.81, no K
   30.85).
   - The winner has no folded-side lobe.
   - 84 of its 112 lost frozen poses are fold.
5. **Hub obliquity law.** A flat O20 hub on a GH ray is in band only if its axis meets the skin within ~25-30 deg of
   the skin normal: the 20 mm disc spans 20 tan(theta) mm against the 12 mm band. Measured on hub 3: 0.64 / 0.69 / 0.82
   in band at 39 / 30 / 16 deg.
   - The J3 seats that fix this (wd 58-71) cost overhead: reach 0.36-0.39 -> 0.18-0.25.
   - Without the pin knee, the J3 side and the overhead cannot both be bought by seat choice: j3-neck-over 28.46 at 4
     active; geneva-tail-knuckle-3r with link 2 0.33 and the neck 0.23 in band.
6. **O20-only closes the crest basin.** At the same crest seats hub 2 is 0.9975 in band at O15 and 0.03 at O20.
   - The 2.5 mm larger disc radius over the crest ridge lifts the fitted level by 25-30 mm.
   - Re-measure every O15-era basin at O20 before building on it.
7. **Stack order is a free lever only with a free exit sector.**
   - Neck over link 2 gains +2 to +5 frozen points when link 2 crosses the arm member's exit on < 2 % of poses.
   - It loses 0.7 at ~5 %.
   - Apply this to the gen-4 knuckle CAD.
8. **Search loopholes and part pairs.**
   - A slaved-spare objective that does not require the drive to engage settles on idle-drive rows: 16.10, a plain 3R
     plus a spare hub with an unscored link 1b. Penalise stretched_kin = 0, flag any link with 0 samples, and bound
     r_horn >= 2.5.
   - The verifier caught a horn inside K's spring cap. Check every new part against every hub stack before claiming.
9. **Pressure angles at O20 size.**
   - A lobe inside O20 caps the gain kK at ~3-3.5.
   - The crown cam at slope 1.5 runs at ~41 deg (23 deg with a 2:1 lever).
   - A one-tooth Geneva entry (psi_c 4-8) reaches dK 56 within 45 deg.
10. **Fast to frozen still loses 4.7-7 points** (22.02 -> 26.70, 16.53 -> 23.37, 22.87 -> 28.46): the 160-pose sample
    effect. Overhead is 8 of 28 on every round-6 design; no lever this round opened the overhead end of the window.

Next (round 7, verified best 23.57, score 91.4, so 95 is not reached and score stays the objective):

1. **Two-sided law on the winner.** Add a folded-side lobe on the same hub-2 rim of the rod embodiment. This is lesson 4
   applied on link 1, where lesson 3 puts K in band. It attacks the 84 fold losses.
   - Target: frozen reach >= 0.80 at in-band >= 0.85 and contact <= 0.01, i.e. gap <= 16 (score 94.2).
   - Lower the rod-end heads, whose 51 samples sit 0 % in band at 20-22 mm.
   - Lift hub 3 from 0.59 in band.
2. **Simplicity at the same law.** Drive K's horn directly from the hub-2 lobe, with K next to hub 2 and no rocker, rod
   or rod ends, or use cam-unfold-4th's crown cam with a 2:1 lever on link 1.
   - Price the result with tools/simplicity.py against 42.5.
   - It only counts at a gap within 1 point of 23.57.
3. **Overhead (8 of 28 everywhere).** Overhead needs th past both ends of the window. Open the window there by measuring
   the two-sided lobe's overhead share first, before any seat search.
4. **Lead's standing duties.** These are not for the round:
   - the final polish, then the generation CAD and stills of the winner;
   - EVOLUTION.md entries for the four round-6 designs (none yet).

## Round 7 plan (2026-10-16 ~14:45 UTC, track main, lead verified gap 23.57)

### State

- **Score arithmetic** (tools/concept_bench.py `gap_of`): gap = 100 [(0.90 - in-band14)+ + (0.95 - follow)+ +
  (0.90 - reach)+ + contact]. The winner: 5.57 + 0 + 16.94 + 1.06 = 23.57. With follow 1.0 and contact 0.01, score 95
  (gap 13.75) needs reach >= 0.775 at in-band 0.90, >= 0.8025 at 0.88, >= 0.8325 at 0.85. The round-6 closer's target
  (reach 0.80, in-band 0.85, contact 0.01) is gap 16, score 94.2.
- **Verified leaders** (Bench(110,360) exact, frozen, margin 5, O20, fit Bench(60,160)):
  - geneva-tail-knuckle-pinknee-3r, rod embodiment: **23.57** (score 91.43), 3 active (K slaved by hub-2 lobe -> rocker
    -> O3 pushrod -> M3 rod ends -> horn), 0 passive translations, complexity 42.5 (hand count). Reach 0.731, in-band14
    0.844, contact 0.011, near-touch 25.21, overhead 8/28; held out 28.12. Params: kK 3.18, r_horn 2.49, r_lobe 9,
    pressure angle 41.4, bk1 31.25, bk2 37.99, a1max 58.36, smhi 13.69, smlo 5.28.
  - cam-unfold-4th 26.70 (3 active, cx 33.75); H1 27.20 same protocol (24.48 polish protocol, cx 19.5-21.5);
    j3-neck-over-3r 28.46 (4 active); zero-complexity ceiling 31.04 / 33.51.
  - Sensed knuckle, verified but 4 active (fails R5-aim): minarc pick1 18.40, BDp 19.54.
- **Where the winner loses** (verifier json `verify/geneva-tail-knuckle-pinknee-3r_corr_bench_frozen.json`):
  - workspace: 263 of 360 taken; lost fold 84, knee window (slide) 8, contact 4, parts 1: 97 lost (the round-6 text says
    "84 of 112"; the verifier json counts 97). The drive engages on 123 stretched poses and on 0 folded (`folded_kin` 0); the law
    ends on stop B at dK 53.4, th_max 116.9; overhead needs th 18-146.
  - overhead (elev >= 140): 8 of 28 taken; lost fold 14, slide 4, contact 2. Held out: 19 of 71, lost fold 37,
    **slide 13**, contact 2 (the knee window is a quarter of the held-out overhead loss).
  - in band per part (samples): hub 1 0.99, hub K 0.95, hub 2 0.99, **hub 3 0.59** (80, 13.0 mm), E 0.95, knee 0.98,
    rocker 0.93 (21), **rod 0.00 (16) and rod ends 0.00 (32) at 29-30 mm**, L1a 0.95, L1b 0.93, **L2 0.77** (144).
  - **Sample arithmetic (not a measurement):** without the rocker, rod and rod ends, in-band14 is 696 / 779 = 0.894
    at the same reach, i.e. gap ~18.6 (score 93.2). Hub 3 at 0.82 (the obliquity law at 16 deg) adds ~+0.024. So a
    drive with no out-of-band metal puts in-band at ~0.90, and 95 becomes a reach problem: +16 workspace poses
    (0.731 -> 0.775) of the 84 fold losses, at contact <= 0.01.
- **Measured on the folded side, so far:**
  - On link 1 the fold window is th in [|a1(K) - a2| + 5, a1(K) + a2 - 5]. With a1 < a2 (pin-knee arcs ~40 / 73) the
    folded relief needs a1(K) to RISE toward a2: K OPENS at the folded end too, the same sign as at the stretched end.
    The folded lobe on the winner is a second rise on hub 2's rim at q2's folded end. On link 2 (cam-unfold-4th) it
    lowers a2e instead; that took 18 folded fit poses there.
  - **Kill risk, measured:** the round-6 judge's two-lobe run at LB1 (kK 6, smhi 8; round6_ideation.md section 1) took
    41 stretched and **1** folded pose (13.70 vs 14.34 one-tooth, +0.64 fast). The folded side may hold few poses that
    a K-opened a1 rescues with hub 2 still in band. Measure before any metal.
- **Pressure-angle physics** (lesson 9): tan(pa) = kK r_horn / r_lobe. The winner's kK 3.18 needs r_horn 2.49 at
  r_lobe 9. A follower on K that reaches hub 2's rim directly has r_horn ~ the K-to-rim distance (>= ~11 mm between
  adjacent O20 stacks), so kK <= ~0.8-1.2 at 45 deg. Low gain is measured viable: rod-low (kK 1.56, r_horn 16.9)
  LHS 19.94 fast, in-band 0.885, reach 0.738, against the rod's LHS 21.18; only the rod was CMA'd (16.53).
- **Complexity bookkeeping:** the winner's row carries a non-standard mechanism record, so tools/simplicity.py prices
  it at **12.0** and the dashboard shows 12.0 and v_gap 23.04 (no v_contact; it uses the fit contact 0.0053), against
  the hand count 42.5 and the verified 23.57. Of the 42.5, the pin knee is 19.5 (10 of it the two sensed knee pins,
  whose angles add to the twist), and the drive (rocker, rod, two rod ends, 2 extra loops x 4, spring, parts) ~20.
- **Dead, with the reason** (adds to round 6's list):
  - the Geneva tail (swept cone about u2: 10-42 points);
  - a hub on link 2 (sweeps a q1 x q2 patch; in band only 21-40 deg from J2);
  - a knuckle without the pin knee (J3 side: link 2 0.33, neck 0.23);
  - O15-era crest basins (0.03 in band at O20);
  - K = c(q1) is coupler-path-j1 by another name (a J2 path set by q1: dead, arcs set the window);
  - idle-drive search optima (16.10, plain 3R plus an unscored spare).
- **Open levers:**
  - the folded-side second rise (gated above);
  - stop B 10.9 deg short of the K dyad's straight line (bk1 + bk2 = 69.2; the 5-deg margin allows ~64);
  - a drive with no out-of-band metal (in-band +0.05 by arithmetic, complexity -10 to -15);
  - hub 3 (0.59) and L2 (0.77);
  - the knee window on overhead (4 bench / 13 held-out losses);
  - the 4.7-7 point fast-to-frozen loss (the 160-pose fit sample; the lead's env-bench polish, not this round).

### Lenses

1. **two-rise-lobe (reach >= 0.80 at in-band >= 0.85, contact <= 0.01: gap <= 16; stretch 95).** A second rise on
   the winner's hub-2 rim, so K opens at q2's folded end too, searched as a new id on the rod carrier.
   - First, before any CMA (~15 min, kinematic + parking on the frozen winner):
     - split the 84 fold losses into stretched-past-stop-B and folded (J1 ~ J3);
     - for each folded loss, the a1(K) that closes it, and hub 2 / hub K / L1b levels at that K;
     - law-only, with the second rise and no metal, folded fit poses taken.
   - **Kill gate:** < 10 folded fit poses taken law-only, or their hub 2 / K out of band (< 0.8), means the lens
     reports the measured reason and stops (the judge's LB1 run took 1).
   - Then search, together: the second rise (onset smlo', gain kK_lo inside the 45-deg pressure angle on the same
     r_lobe), stop B / a1max up to the K dyad's 5-deg margin, a2, the seats, the rod-end heads lowered under the
     crown (now 29-30 mm, 0 % in band), and hub 3.
   - Rules: near-touch objective; an idle drive scores 100 (stretched_kin = 0 or folded_kin = 0 on a two-rise row);
     the 5-deg margin in the J1-J3 metric with stops on q2's own angle; rate <= 3.45; every new part checked against
     every hub stack incl. K's +6 mm spring cap; the lobe's radius checked against the O20 skirt (the winner's is
     0.9 mm past it).
   - Claims report frozen exact, near-touch, overhead x/28, folded_kin and the full-grid continuity flood fill. A
     two-rise law is still monotone per side, but it has two branches in q2; check the flood fill for jumps at the
     law's minimum.
2. **direct-drive-knuckle (low complexity at the same reach: cx <= ~30 vs 42.5, gap within 1 of 23.57).** Drive K
   from the hub-2 lobe with no rocker, pushrod or rod ends.
   - Embodiments, in order:
     - (a) K's follower arm or roller rides hub 2's rim lobe directly, with K moved next to hub 2 (bk2 small). By the
       pressure-angle law kK <= ~0.8-1.2, so the onset (smhi), stop B and bk1 / bk2 are re-fitted for low gain (the
       rod-low precedent, 19.94 fast at kK 1.56);
     - (b) cam-unfold-4th's crown cam moved to link 1 with a 2:1 lever (23 deg pressure angle; crown hardware +5 hub
       2 / +3 hub K, measured);
     - (c) the lobe on K's rim and the follower on link 1b at hub 2 (the inverse pair), if it parks better.
   - Its in-band upside is measured arithmetic: removing the 0 %-in-band rod metal gives ~0.894 at equal reach (gap
     ~18.6). So this lens can beat the winner as well as simplify it.
   - Gates before metal: kK, pressure angle <= 45, the follower's swept volume (lesson 2: it sits on link 1 and sweeps
     only K's few degrees), the housing rule for a profile on a hub body, force closure (the K spring keeps the
     follower on the lobe against gravity over the whole law; no lift-off).
   - Price every embodiment with tools/simplicity.py from a FULL mechanism record (bodies, joints, loops, springs,
     parts), and write the same full record for the winner first so the comparison is tool against tool.
   - If lens 1's gate passes, the second rise goes on the same rim.
3. **overhead-end (overhead >= 14 of 28 at in-band >= 0.88).** Overhead is 8 of 28 on every round-6 design. Attribute
   before choosing a lever, on the frozen winner chain.
   - For each of the 20 bench and 52 held-out lost overhead poses, measure:
     - th needed against [th_min(K), th_max(K)];
     - the K that would close it;
     - hub 2 / hub K / hub 3 / L2 levels at that K (parking);
     - the knee-window demand (ang_min 27.85).
   - Then take the lever it names, in this order:
     - (a) stretched end: stop B from a1max 58.4 toward ~64, with the lobe re-cut for the extra travel inside 45
       deg;
     - (b) the knee window for the slide losses (4 bench / 13 held out; the longer knee link measured 0 on H1, so try
       ang_min and the knee's seat, not lc);
     - (c) only then seats: J1 on the back of the shoulder (the user's allowed set: back + acromion top), where the
       J1-J3 alignment set leaves the overhead cone (alignment-free-knuckle-4r: kinematic 0.953, overhead 26/28),
       now with a determined K and the in-band headroom of lens 2.
   - The folded-end share comes from lens 1's split; share files, do not duplicate the run.
   - Target: frozen exact overhead >= 14 / 28 and reach >= 0.775, at in-band >= 0.88 and contact <= 0.01.

Every lens:
- writes docs/concepts/viz/concepts/<id>.js and passes `node docs/concepts/viz/test.mjs <id>` before the row is called
  screened;
- reports plain and near-touch, fast and frozen exact, held out, the continuity flood fill (full grid), and
  tools/simplicity.py;
- is time-boxed to 75 min of modelling; on a red-team kill it reports the measured reason and stops.

### Carried over (catalogue, ideated, never screened)

None. The round-4 judge picks:
- deltoid-crest-j3-3r and crest-knee-3r are O15 crest-basin designs, closed by round-6 lesson 6 (hub 2 0.9975 at O15
  -> 0.03 at O20); their judge red team measured +0.017 frozen reach;
- slotted-eccentric-pin-knee-3r: its sibling was refuted at 115.21.

The round 1-2 ideation entries are either families dead in rounds 1-2 (rails, telescopes, SPMs, tracks) or hubless
joints that the "Keep O20 only" ruling excludes (cruciate-knuckle-3r, rolling-cone-3r).

### Elsewhere, not to be duplicated

- geneva-tail-knuckle-pinknee-3r itself: the lead's final polish and the gen-5 CAD, deferred until this round closes.
  The round's variants take new ids.
- minarc-stop-knuckle-4r: the gen-4 CAD (user_minarc_bdp v2, farm judge running) and gen-4b on pick1.

### Lead bookkeeping (not the round's)

- Fill the winner's mechanism record in tools/simplicity.py's schema (the tool says 12.0, the hand count 42.5).
- Add v_contact 0.0106 to the row (the dashboard shows v_gap 23.04 against the verified 23.57).
- EVOLUTION.md entries for the four round-6 designs.
- The winner's open buildability items: lobe radius past the skirt, the 41.4-deg pressure angle, rod-end play, spring
  vs gravity, the reflected J2 torque 3.18 tau_K.

### Needs the user's say (listed, not screened)

- **A cuff IMU instead of the two knee-pin encoders.** The pin knee would drop from 19.5 to ~11.5 (docs/SIMPLICITY.md)
  and the winner to ~34.5. Related: the rule counts a sensed K as active (4 active) but the pin knee's sensed twist
  pins as passive (3 active), and that asymmetry should be stated as a rule.
- A fold margin below 5 deg (unchanged).
- A sensed passive used only for static extremes counting as passive: minarc pick1 18.40 would then be 3 active.

## Round 7 results (2026-10-16 ~15:33-17:15 UTC; closed by the round-7 closer)

Picks (round-7 judge, docs/concepts/round7_ideation.md):
- rim-lobe-arm-knuckle-3r (pick 1, direct-drive lens, with groove-arm merged in as its 'groove' embodiment);
- k-rim-lobe-stub-knuckle-3r (pick 2, direct-drive lens, the inverse pair);
- split-knuckle-twosided-3r (pick 3, the only surviving folded-side lever);
- frontload-lobe-stopb-knuckle-3r (pick 4, the stretched-side / overhead-end control, gated at fast < 16.0).

Dead at ideation, measured by its own proposer: two-rise-lobe-pinknee-3r, the lens-1 lead. msub at the folded onset is
2.14 deg, so it takes 0 poses under the winner's rules. With metal fitted, hub 2 needs 63-70 mm (against 60.2), and the
fast gap goes 16.53 -> 18.61. A 750-design re-seat scan found 33.46 at best. long-a2-bilobe was rejected as a duplicate
of it. recentred-knee-geneva-3r was not picked (a parameter tweak, +2 of 28 overhead, kinematics only). Its lc / phib /
phiE / lE go to the lead's env-bench polish.

All numbers below are frozen exact on Bench(110,360), at the 5-deg margin with O20 hubs only, fitted on Bench(60,160)
(the round-3 protocol). Every row was re-measured by an independent verifier.

| design | fast Bench(60,160), near-touch | frozen exact (verified) | held out | active | complexity (tool) | status |
|---|---|---|---|---|---|---|
| **frontload-lobe-stopb-knuckle-3r** (best = the winner's rod drive, 1:1, seats re-fitted) | 15.57 (verifier 15.68 with the spring-cap metal) | **22.82** (score 91.70). Reach 0.728, follow 1.0, in-band14 0.855, in-band10 0.558, contact 0.011, near-touch 24.46, overhead 8/28, fold losses 86. | 26.75 | 3 (K slaved, never read) | 49 (the winner's mechanism; 46.75 for the winner's full record, 42.5 by hand) | **verified: round winner** (a seat re-fit) |
| rim-lobe-arm-knuckle-3r (roller on a link-2 lobe plate, low lug) | 20.57 (reproduced exactly) | 26.21 self-measured (score 90.47). Reach 0.681, in-band14 0.863, near-touch 27.89, fold losses 106. | - | 3 | 35.25 | DEAD at its kill gate (15.5); death audited |
| split-knuckle-twosided-3r (K2 on link 2, mirrored rod drive) | 26.62 | 34.18 (score 87.6). Reach 0.728, in-band14 0.746, contact 0.016, near-touch 36.89, fold losses 84 (= the winner's). | - | 3 | 68.5 | DEAD; death audited |
| k-rim-lobe-stub-knuckle-3r (lobe on link 1a, roller on a link-2 stub) | 36.82 (plain 30.79) | 44.79 (score 83.7). Reach 0.622, follow 0.873, in-band14 0.826, contact 0.018, near-touch 53.51, overhead 5/28. | - | 3 | 34.0 (hand) | verified, not a contender (kill gate failed by 21) |

Same-protocol references: the round-6 winner geneva-tail-knuckle-pinknee-3r 23.57 (held out 28.12); its linear law
re-fitted under the same rules (frontload's control E) 22.92 frozen, self-measured; H1 27.20; sensed minarc pick1 18.40 /
BDp 19.54 (4 active); zero-complexity ceiling 31.04.

**Winner: frontload-lobe-stopb-knuckle-3r, verified at 22.82 (score 91.70)**, with 0 passive translations. Its gap
beats the previous verified lead (23.57) by 0.75, so the verified lead number moves to 22.82, but it is not a new
mechanism:
- **Control.** The best configuration is the round-6 winner's own rod drive (1:1 rocker, nearly linear law: kA / kB
  1.05) on re-fitted seats. The CMA control E re-fits the winner's linear law under the same rules and scores 15.54 fast /
  22.92 frozen / 26.66 held out, against the pick's 15.57 / 22.72 / 26.65 (claim side).
- **Lever-by-lever controls.** The front-loaded law gives 0.01 frozen, stop B raised to a1max 61.7 gives 0.00, and the
  2:1 rocker loses ~1.2 fast.
- **1-point rule.** The gain is below the rule (CLAUDE.md) for a polished config to replace the CAD's config. Held out
  it is 1.37 (26.75 vs 28.12).
- **Red team (closer, from the verifier's own audit):** the re-fit buys in-band by sitting closer to the skin.
  - At the 1 mm near-touch rule it is 0.75 better: 24.46 vs 25.21 bench, 29.39 vs 30.31 held out.
  - Counting metal under 2 mm as contact, it is 5.2 points WORSE: 44.08 (34 poses) vs 38.84 (28) bench, and 46.73 (80)
    vs 42.01 (61) held out.
  - Min metal 0.30 mm (winner 0.45), 0.14 mm held out.
  - The margin is thin and should be priced before any CAD swap.
- **Open buildability items:**
  - the lobe crest is 10.26 mm, 0.26 mm past hub 2's O20 skirt (the winner's is 10.9);
  - the pressure angle is 44.3 against the 45 limit;
  - the law prefix dips to m3e 0.58 deg at its end (every taken pose keeps >= 5);
  - K slop is 1.16 deg per 0.05 mm of rod-end play.

Lessons (measured):

1. **At O20 spacing, the rod (a strap) is the cheapest carrier of a slaved-K law.**
   - **The prize.** The rod drive's metal costs 4.74 fast points (law-only 11.79 vs 16.53, re-measured). The laws a
     compact direct pair can carry give 2.0-2.6 of those back (14.38 / 13.76).
   - **Direct pair (rim-lobe-arm).** An arm aimed along the K-J2 line has a 90-deg pressure angle and is an idle drive
     (135.63). A usable arm sits 20-35 deg off that line, so its follower is >= 19 mm from u2.
   - **Why the plate fails.** The skin under hub 2 is low within ~25 mm of u2 and 6-14 mm higher beyond ~27 mm, so a
     plate swept about J2 is either 18 mm over the skin (8 % in band) or lifted off the ring level. The optimum caps the
     follower at 31 mm, so dK is 25.9 deg (against 36 law-only) and reach is 0.731.
   - **Verdict.** The direct pair is 4.0 fast / 2.8 frozen points worse than the rod, and 11.5 complexity points
     simpler (35.25 vs 46.75). A drive must carry >= ~30 deg of K to beat the rod.
   - **Groove (positive, no spring).** Its 93-deg dwell flange sweeps the body: best 95.51.
2. **The swept-volume rule holds at 24-28 mm too.**
   - The inverse pair (stub rigid with link 2) pays for link 2's whole q2 sweep. Link 1b is the upper member at K, so
     link 1b, the lobe and the stub stack in three layers ~8 mm above link 1b's in-band level: the lobe is 0 % in band,
     the stub 11 %, the roller 17 %.
   - The beside-link-1b variant puts the lobe 100 % in band, but the roller rides into link 2's skin sweep (best 57.2).
   - Frozen, the roller-vs-lobe collisions in state A grow from 9 to 32 poses (follow 0.873).
   - Rule: no follower rigid with link 2, at any radius (Geneva tail 38 mm, stub 24-28 mm: both ~20 points or more).
3. **The folded side is closed.** It holds 23 of the 84 frozen fold losses (8 of 160 fit poses, <= 5.0 fast gap points
   and <= +0.064 reach).
   - **On link 1 (two-rise lobe):** msub 2.14 deg at the onset, and hub 2 is pushed into the body (63-70 mm needed).
   - **On link 2 (K2):** the law engages only when K2 rests bent at psi0 <= 135 deg. At those seats an O20 hub on link 2
     is <= 0.12 in band and 70-116 mm from GH. Its cheapest metal costs 5.8 points, more than the whole prize.
   - **Where K2 does engage,** the folded end lays link 2 back over link 1, onto the stretched-side drive (ROD-hubK2
     -5.2 mm, hubK-hubK2 -0.7 mm).
   - Rule: folded-side relief comes from the existing chain (seats, smlo, a2), never from another hub.
4. **The stretched side is walled, not law-limited.**
   - Stretched losses on the fit bench: 6 at the m3e wall plus lift-off, and 13 at th 124-157 past the K dyad's
     straight-line wall (a1max + a2 - 5).
   - How fast K can open is capped by the lift-off gate (K's self-motion slope at fixed th) as well as by the pressure
     angle: every margin-tracking law below smt 12 ends on lift-off.
   - Raising stop B buys nothing (taken poses never use K past 44.7 deg). A 2:1 rocker's clevis arm must clear hub K's
     crown and so sits 9-12 mm over link 1b (-1.2 fast).
   - Frozen fold losses are 84-86 on every rod-drive variant this round, and 105-106 on the direct pairs (smaller dK).
     No law or drive change moved them.
5. **The winner's seats had re-fit headroom:** 0.6-0.75 frozen and 1.37 held out. Most of it is hub K in band (0.945 ->
   0.976) and the lobe pulled inside the O20 skirt (r_lobe 9 -> 7.35). That is polish territory, and the 2 mm red team
   above shows that part of it is proximity.
6. **Metal rules: missed again, now fixed in the harnesses.**
   - K's spring cap is a cylinder (HUB_R, CROWN + capK). A crown-top check is not enough: the frontload claim's rod
     ran 4.85 mm inside the cap.
   - A rod that crosses K must clear crown top + 2 mm within HUB_R + 2 of K's axis. The winner's own rod ran 2.6 mm
     into the crown; the rule costs it 0.10.
   - Every swept-plate model needs a plate-height cap. Without one, the greedy fit floats a part 90 mm.
   - Both checks belong in the shared kit, not in each harness.
7. **Search hygiene.**
   - Spare-idle optima reappeared: split-knuckle's sweep minimum 22.34 is K2-idle. The idle-drive penalty must cover
     every slaved spare, not only K.
   - A sweep file that concatenates runs hides per-run convergence (rim-lobe: 0.85 combined against 0.11 / 0.09 on run
     b). Gate each run separately.
8. **Fast to frozen still loses 5.6-14 points.**
   - 15.57 -> 22.82, 20.57 -> 26.21, 26.62 -> 34.18, 30.79 -> 44.79 (the last driven by state-A collisions).
   - Overhead is 8 of 28 on every rod-drive design (5 of 28 on the stub). The frozen winner loses 20 overhead poses:
     fold 15, slide 3, contact 2.
   - No round-7 lever touched the overhead end. The overhead-end lens's seat lever (J1 on the back of the shoulder) was
     never screened.

Next (round 8; verified best 22.82, score 91.70, so 95 is not reached and score stays the objective):

1. **Change the fold window's geometry, not K's law.** Rounds 6-7 measured every lever on K (law shape, stop B,
   rocker ratio, direct pairs, a folded-side lobe, K2). Frozen fold losses never moved off 84-86, and the walls that
   bind are geometric:
   - the K dyad's straight line, a1max + a2 - 5 (13 fit poses at th 124-157);
   - the m3e / lift-off wall (6);
   - the folded |a1 - a2| + 5.

   The levers left, in order:
   - **(a) J1 seat on the back of the shoulder** (the user's allowed set), where the J1-J3 alignment set leaves the
     overhead cone (alignment-free-knuckle-4r: kinematic 0.953, overhead 26/28), now with the determined rod-drive K
     and the pin knee. Kill gate first: hub 2 / link 2 in band >= 0.8 at those seats (round 6 measured 0.00-0.20 on
     the J3 side).
   - **(b) a2 61-68 with the stretched-only lobe** (untested; it moves the straight-line wall by Delta a2).
   - **(c) the knee window** for the overhead slide losses (3-4 bench / 13 held out), via lc 34 / phib -75 (+5 bench /
     +18 held-out workspace poses, kinematic).

   Target: frozen overhead >= 14/28 and reach >= 0.775 at in-band >= 0.88 and contact <= 0.01.
2. **Do not screen again:**
   - direct pairs between O20 stacks, followers rigid with link 2, and folded-side hubs (lessons 1-3);
   - front-load / stop-B laws (lesson 4).

   A simpler drive must beat the rod's 4.74 points of metal while carrying >= 30 deg of K. Nothing measured so far
   does.
3. **The lead's polish, not the round's:**
   - the env-bench polish of the rod-drive knuckle, seeded from the frontload re-fit with lc / phib / phiE / lE free
     (recentred-knee), priced at the 1 mm and 2 mm near-touch;
   - the verifier, then the gen-5 CAD and stills if the gain is >= 1 point;
   - EVOLUTION.md entries for the round-6 and round-7 designs;
   - the shared-kit spring-cap and plate-cap checks (lesson 6).
4. **Complexity:** the 3-active knuckle class sits at 42.5-49. The golden 95 at ~0 complexity is out of reach of every
   measured class: zero-complexity ceiling 31.04, knuckle 22.82.

### Needs the user's say (unchanged)

- A cuff IMU instead of the two knee-pin encoders: the pin knee 19.5 -> ~11.5, the winner ~34.5.
- A fold margin below 5 deg.
- A sensed passive used only for static extremes counting as passive (minarc pick1 18.40 would be 3 active).
- New, rule question: is msub needed for a cam-slaved K? It is moot for the two-rise lobe (its metal kills it).

## Round 8 plan (2026-10-16 ~17:15 UTC, track main, lead verified gap 22.82)

### State

- **Verified lead** (Bench(110,360) exact, frozen, margin 5, O20, fit Bench(60,160)): frontload-lobe-stopb-knuckle-3r
  **22.82** (score 91.70). It is the round-6 rod drive on re-fitted seats: 3 active (K slaved, never read), 0 passive
  translations, complexity 49 (tool). The numbers: reach 0.728, follow 1.0, in-band14 0.855, contact 0.011, near-touch
  24.46 (2 mm: 44.08), overhead 8/28, held out 26.75. Next on the same protocol: geneva-tail-knuckle-pinknee-3r 23.57
  (cx 42.5-46.75), cam-unfold-4th 26.70 (cx 33.75), H1 27.20 (cx 19.5). The 4-active sensed minarc pick1 is 18.40
  (cx 33), and the zero-complexity ceiling is 31.04.
- **The gap, split** (verifier json `verify/frontload-lobe-stopb-knuckle-3r_corr_bench_frozen.json`): 22.82 = in-band
  4.54 + reach 17.22 + contact 1.06.
  - **Workspace lost:** 98 of 360 (fold 86, knee window 7, contact 4, parts 1).
  - **Overhead lost:** 20 of 28 (fold 15, slide 3, contact 2).
  - **Drive:** it engages on 130 stretched poses and 0 folded. Taken poses use dK <= 44.3 of the law's 67.4. The
    full-grid flood fill drops 0.
- **Sample arithmetic (not a measurement):** the rod (15 samples) and rod ends (32) sit 0 % in band at 28 mm.
  - Without them, in-band is 723.8 / 800 = 0.905, and the gap is 18.28 (score 93.35) at the same reach.
  - At that in-band, 95 needs reach 0.773 at contact 0.011: +16 of the 86 fold poses.
  - So the drive's height is half of the distance to 95, and the fold geometry is the other half.
  - In band per part: hub 3 0.60 (80 samples), L2 0.78 (144), rocker 0.94; everything else >= 0.96.
- **Fold walls (measured rounds 6-7, unchanged by every K-law lever):**
  - stretched: the K dyad's straight line a1max + a2 - 5, 13 fit poses at th 124-157 (a1max <= bk1 + bk2 - 5 = 62.6);
  - the m3e / lift-off wall: 6 fit poses;
  - folded: |a1(K) - a2| + 5, 8 fit poses / 23 frozen. Folded-side relief is closed: msub 2.14 deg, hub 2 needs 63-70
    mm, K2's metal costs more than the prize.
  - Frozen fold losses were 84-86 on every rod variant.
- **Window arithmetic (not a measurement):**
  - With J3 at wd ~63.5 off the humerus (hub 3's obliquity law keeps wd >= ~60 for an O20 disc in band), the arm's
    axial rotation sweeps th over about +-wd around angle(J1, humerus). That is why the overhead poses span th 18-146.
  - The window [|a1e - a2| + 5, a1e + a2 - 5] is 2 min(a1e, a2) - 10 wide. Covering 128 deg needs min(a1e, a2) >= 69
    at the overhead K state. The winner has a1e 40 -> <= 62 and a2 ~61-66.
  - So the overhead end needs wider arcs at overhead, or a J1 seat that centres the overhead th set in the window. A
    law change gives neither.
- **Measured against the re-seat (lever a):**
  - zc-frontier S-streams started at back seats (0, 45) / (30, 60): they walk back to the acromion top, or stay
    wide-window at P0 57.92 (reach 0.85, in-band 0.42) and P30 59.67.
  - The posterior J1 line in the pin-knee family: 122.45, in-band 0.17-0.25, contact 0.23-0.29. Skin, not fold, takes
    the poses.
  - zc Awide: a1 forced to 52 walks back to 36.7.
  - alignment-free-knuckle-4r: hub 2 0.00 and link 2 0.065 in band at distal J3 seats (J1 on the acromion top).
  - Kinematic headroom inside the J1 ruling: 0.942 at arcs 50/50, J1 az -5..3 el 0, J3 d 110 a -96..-100
    (reach_attribution section 6).
  - A knuckle at back seats has never been measured; the knuckle bends link 1 and so moves hub 2's parking.
- **Measured for the drive height:**
  - rod-low (a strap-level rod to a horn lug on link 1a, r_horn 16.9, 3:1 rocker, kK 1.56): LHS 19.94 fast, in-band
    0.885, reach 0.738, against the rod's LHS 21.18. Only the rod was CMA'd (16.53).
  - Law-only (no drive metal) vs rod metal on the same law: 15.71 vs 20.37 near-touch. The drive's metal costs ~4.7
    fast.
  - A 2:1 clevis arm over hub K's crown sits 9-12 mm over link 1b (-1.2 fast).
  - Direct pairs carry only 25.9 deg of K (rod 36 law-only). A drive must carry >= ~30 deg.
- **Law shape is worth <= 0.2 frozen:** front-load 0.01, stop B 0.00, linear re-fit 22.92 vs 22.72. A drive can change
  its law shape without losing that.
- **Complexity (tool):** frontload 49 = 6 passive rotations, 2 sensed knee pins (10), 3 loops (12), the K spring (3),
  bodies / joints / parts.
  - The two sensed knee pins (10) need the user's say (cuff IMU).
  - The drive's lobe pair, rocker, spring and their loop are the part this round can remove.
- **Dead, with the reason** (adds nothing new; do not screen again):
  - direct pairs between O20 stacks;
  - followers rigid with link 2 at any radius;
  - folded-side hubs and lobes;
  - front-load / stop-B laws;
  - the Geneva tail;
  - hubs on link 2;
  - a knuckle without the pin knee on the J3 side (link 2 0.33, neck 0.23);
  - O15 crest basins;
  - K = c(q1);
  - groove / dwell flanges (95.51).
- **Stale rows:** offset-axis-skin-hubs, seed-rcm-parallelogram and virtual-pole-4bar-j1 / -j2 still say "modelling"
  in morphs.json. They date from 01:00-04:00 UTC, and the virtual-pole pair was killed at 01:58. Nothing runs on them.

### Lenses

1. **window-geometry (reach >= 0.775 and overhead >= 14/28 at in-band >= 0.88, contact <= 0.01).** Move the walls,
   not the law. On the frontload rod-drive knuckle with the pin knee, walk J1 from the acromion top toward the back of
   the shoulder (az1 95 -> 0, el1 67 -> 0, inside the ruling), and widen a2 (61-72) and bk1 + bk2 (to ~80, so a1max
   reaches ~75). This is levers (a) and (b) as one geometric scan.
   - **Kill gate first** (law-only, no drive metal, <= 20 min). Grid: az1 {95, 75, 55, 35, 15} x el1 {67, 45, 25} x
     a2 {61, 65, 69}, K's law to stop B at the dyad's 5-deg margin. Per cell, measure:
     - kinematic workspace reach and overhead x/28 on Bench(110,360);
     - hub 2 / hub K / L1b / L2 in band with K at rest and K open (parking).
   - The gate passes on a cell with kinematic reach >= 0.82, overhead >= 16/28 and those four parts >= 0.8. Else:
     report the per-part map (which part leaves the band, by how many mm, at which poses) and stop. That closes levers
     (a) and (b) with data.
   - Then CMA from the passing cells on the near-touch objective. Free: seats, a2, bk1 / bk2, smhi, law gain, a1max.
     Rules: the idle-drive penalty; the kit's spring-cap / rod-over-crown / plate-cap checks; rate <= 3.45; pressure
     angle <= 45.
   - Attribute every overhead pose won or lost.
2. **strap-level-drive (in-band >= 0.89 at reach >= 0.725: gap <= ~19, the other half of 95).** Put the K drive's metal
   in band: the rod is the cheapest carrier, and only its height is wrong. Embodiments, in order:
   - (a) the rod-low CMA (never run), with the K dyad re-fitted for low gain (bk1 / bk2, smhi, onset, a1max) and the
     rocker ratio 2-3;
   - (b) a horn that leaves K's stack sideways at link 1b's level, with a rod beside link 1b at strap level crossing
     no crown;
   - (c) a rocker whose clevis arm runs beside hub K's crown, not over it.

   Gates before metal:
   - the drive carries >= 30 deg of K on taken poses;
   - pressure angle <= 45;
   - the rod and horn checked against every stack, incl. K's +6 mm spring cap and the crown rule;
   - K slop from rod-end play priced;
   - lift-off.

   Report rod / rod ends / horn in band per part. Hub 3 (0.60) and L2 (0.78) are open in-band headroom: try the hub-3
   crest seat (obliquity 16 deg, 0.82) only if the drive alone stops short of 0.89. If lens 1 passes its gate, wear
   this drive on its seats.
3. **crank-rod-knuckle (low complexity at the same reach: cx <= ~38 by the tool vs 49, frozen gap within 1 of
   22.82).** Replace the lobe, follower, rocker and K's spring with a positive spherical four-bar:
   - a crank pin rigid with link 2 inside hub 2's O20 stack (r <= 7.5, the lobe's own radius and swept volume);
   - an O3 rod to K's horn;
   - K is determined everywhere, so it needs no spring and no force closure. The stops stay as safety stops.

   The law comes from the four-bar. With the crank and rod collinear at q2's folded end, dK/dq2 ~ 0 there, so the
   four-bar has a quadratic onset in place of the dwell. Law shape is worth <= 0.2 frozen (State); the risk is the
   gain:
   - the lobe opens 44 deg over ~15 deg of q2 (kK ~2.9);
   - a four-bar from near-toggle averages kK ~1 unless r_horn ~2.5;
   - kK 1.56 lost 0.043 reach at LHS (rod-low).

   Gates:
   - law-only fast within 1.0 of the lobe law's law-only score on the same seats;
   - transmission angle >= 45 deg over the used q2 range;
   - no assembly-mode change in the full-grid flood fill;
   - the crank pin / rod end vs every stack;
   - K inside its stops over the whole q2 range.

   Price it with tools/simplicity.py from a full mechanism record, against frontload's 49. If lens 2 finds a
   strap-level route, the crank-rod uses it.

Every lens:
- writes docs/concepts/viz/concepts/<id>.js and passes `node docs/concepts/viz/test.mjs <id>` before the row is called
  screened;
- reports plain and near-touch at 1 and 2 mm, fast and frozen exact, held out, the full-grid continuity flood fill,
  overhead x/28, the per-part in-band and tools/simplicity.py;
- takes a new id (frontload / geneva-tail rows are the lead's);
- gates each CMA run separately;
- is time-boxed to 75 min of modelling. On a kill it reports the measured reason and stops.

### Carried over (catalogue, ideated, never screened)

None. The round-4 judge picks stay closed:
- deltoid-crest-j3-3r and crest-knee-3r are O15 crest basins (hub 2 0.9975 -> 0.03 at O20). Their hub-3 crest seat is
  available to lens 2 as a seat option, not as a design.
- slotted-eccentric-pin-knee-3r: its sibling was refuted at 115.21.

The rest of the ideated catalogue is families dead in rounds 1-2 (rails, telescopes, SPMs, tracks, pointers) or hubless
joints excluded by "Keep O20 only".

### Elsewhere, not to be duplicated

- frontload-lobe-stopb-knuckle-3r / geneva-tail-knuckle-pinknee-3r: the lead's env-bench polish (seeded from the
  frontload re-fit, with lc / phib / phiE / lE free: the knee-window lever (c), recentred-knee lc 34 / phib -75), priced
  at the 1 mm and 2 mm near-touch. Then the verifier, and the gen-5 CAD if the gain is >= 1 point.
- minarc-stop-knuckle-4r: the gen-4b CAD on pick1 (l1_minarc-pick1 build running).

### Lead bookkeeping (not the round's)

- EVOLUTION.md entries for the round 6-7 designs.
- The spring-cap and plate-cap checks in the shared kit.
- Clear the four stale "modelling" rows.

### Needs the user's say (listed, not screened)

- A cuff IMU in place of the two knee-pin encoders: the pin knee 19.5 -> ~11.5, frontload 49 -> ~41.
- A fold margin below 5 deg.
- A sensed passive used only at static extremes counting as passive (minarc pick1 18.40 would be 3 active).
- Whether msub applies to a cam-slaved (or four-bar-slaved) K.

## Round 8 results (2026-10-16 ~17:15-20:31 UTC; closed by the round-8 closer)

Picks (round-8 judge, docs/concepts/round8_ideation.md):
- sidecar-parallelogram-knuckle-3r (pick 1, strap-level-drive lens: a sidecar bell crank + M2 ball-link rod at strap
  level, the lead's chain and K dyad unchanged);
- sidecar-roller-flank-knuckle-3r (pick 2, strap-level-drive lens: rodless, an MR63 roller on a conjugate flank of link
  1a's horn);
- twist-long-a2-knuckle-3r (pick 3, window-geometry lens: J3 re-seat + a2 58-66 + wide K dyad; crest-j3-wide-dyad
  merged as seed B);
- sidecar-longdyad-knuckle-3r (pick 4, strap-level-drive x window-geometry: the sidecar on a longer link 1b; wide-dyad
  merged as a check cell).

Parked for the user at ideation: crank-rod-knuckle-3r and bighorn-crank-rod-knuckle-3r (cx 36; msub question). Not
picked: lost-motion-swivel-knuckle-3r (0 expected gain, 1 passive translation; revisit only when complexity becomes the
objective).

All numbers below are frozen exact on Bench(110,360), at the 5-deg margin with O20 hubs only, fitted on Bench(60,160)
(the round-3 protocol). Every row was re-measured by an independent verifier, and the round-8 sidecars were re-worn a
third time by the alignment auditor (docs/ALIGNMENT.md, `docs/alignment/remeasure/`): all reproduce to the digit.

| design | fast Bench(60,160), near-touch | frozen exact (verified) | near-touch 1 / 2 mm | held out | complexity (tool) | status |
|---|---|---|---|---|---|---|
| **sidecar-longdyad-knuckle-3r** (bk1 28.9 / bk2 39.2 / a1max 63.2, sidecar kK 1.62, r_h 14.9) | 10.30 (= plain) | **18.91** (score 93.12). Reach 0.725, follow 1.0, in-band14 0.897, in-band10 0.534, contact 0.011, overhead 8/28; lost: fold 86, slide 7, contact 4, parts 2. Flood full 18.91 (0 dropped), knn 21.72. | 20.00 / **34.03** | 22.67 | 49 | **verified: round winner, new verified lead** |
| sidecar-parallelogram-knuckle-3r (the lead's dyad, r_h floor 15.5, RC ball links) | 10.63 (209 ties) | 19.13 (score 93.04). Reach 0.719, in-band14 0.905, contact 0.011, overhead 8/28, fold 88. | 20.22 / 50.14 | **22.03** | 49 | verified; 2 mm shell gamed (alignment audit) |
| sidecar-roller-flank-knuckle-3r (beta -175, g 2.28, 130-deg wrapped arm) | 11.73 | 20.08 (score 92.70). Reach 0.722, in-band14 0.890, contact 0.013, overhead 8/28, fold 87. Real envelope 19.96. | 21.17 / 46.82 | 22.35 | **45.25** | verified; the simplest strap-level drive |
| twist-long-a2-knuckle-3r (C0: lead axis + wide dyad bk2 45.2) | 16.74 | 24.46 (score 91.10). Reach 0.733, follow 0.955, in-band14 0.851, contact 0.029. | 27.70 / 37.84 | 28.44 (A2) | 49 | DEAD (converged over 4869 CMA configs); death audited |

Same-protocol references: the round-7 lead frontload-lobe-stopb-knuckle-3r 22.82 (near-touch 24.46 / 44.08, held out
26.75); geneva-tail-knuckle-pinknee-3r 23.57 (2 mm 38.84); H1 27.20; the 4-active sensed minarc pick1 18.40 (cx 33 by
its row, 52 counting K as the 4th active DOF, ALIGNMENT.md G5); zero-complexity ceiling 31.04.

**Winner: sidecar-longdyad-knuckle-3r, verified at 18.91 (score 93.12)**: 3 active (K slaved by the lobe and the RSSR
sidecar, never read), 0 passive translations, complexity 49. It beats the previous verified lead (22.82) by **3.91**,
so the verified lead number moves to 18.91. The tie rules are not needed: parallelogram is 0.22 behind (19.13) and
roller-flank 1.17 behind (20.08, at 3.75 lower complexity). Why longdyad and not parallelogram, beyond the 0.22:
- **2 mm red team.** longdyad is the only round-8 row that is also better than the previous lead with metal under 2 mm
  counted as contact: 34.03 vs frontload 44.08 (and geneva 38.84). parallelogram is 6.06 worse than frontload there
  (50.14, 44 taken poses at 1-2 mm); the alignment audit calls its lead "gamed on the 1-2 mm shell" and longdyad's "real".
- **Held out** parallelogram is 0.64 better (22.03 vs 22.67). The two share the drive; the only difference is the K
  dyad, whose length is worth under 1 point and flips sign held out (lesson 2). Not a lever either way.
- **Over the 1-point rule.** The gain is 3.91 frozen and 4.08 held out (22.67 vs 26.75), so the generation-winner CAD
  and stills run on it (after the final polish below).

Open items on the winner (verifier + audit), to settle in the polish / CAD:
- the M2 ball centre sits 3 mm over the arm and horn tops (the low end); at 4 / 4.5 mm the fit gap is 10.69 / 10.84 and
  the rod's in-band falls 0.89 -> 0.62 / 0.52;
- the crank's short arm and its follower are not sampled metal;
- the lobe works at r 7.7-10.2 mm inside hub 2's O20 housing (link 1b): the follower needs a window, and at a 16 mm
  pivot offset it is a sliding pad on an ~8 mm arm, so 'rolling_pairs 1' becomes a sliding pair;
- the horn socket is 1.37 mm off hub K's housing at r_h 14.9 (CAD: r_h >= 15.5 or a smaller socket);
- min metal 0.28 mm frozen, 0.14 mm held out (priced in the near-touch columns);
- the RC acetal M2 ball link is load-bearing (all-metal GE4E ends cost 6.8 fast) and is not yet in
  tools/hardware_catalogue.json.

Lessons (measured):

1. **The in-band half of 95 is done, and it came from the drive's height, as priced.** The round-8 plan's arithmetic
   said the crown-high rod (0 % in band) was worth 4.54 frozen; the strap-level sidecar puts the rod at 0.89, rod ends
   0.96, crank 0.91 and delivers 3.69-3.91 frozen (roller flank 2.74) and 4.1-4.7 held out, on every dyad and both drive
   types (RSSR rod, roller flank). In-band14 is now 0.890-0.905 on all three drive rows. The remaining in-band headroom is the lead's own
   chain: hub 3 0.60 and L2 0.75.
2. **The gap is now reach, and the fold did not move.** longdyad's 18.91 = in-band 0.34 + reach 17.50 + contact 1.07.
   Fold losses: 86 / 88 / 87 / 76 (twist C0) of 360, against 84-86 on every rod variant in rounds 6-7. Overhead is 8/28
   on all four rows (20 lost: roller-flank fold 14 / slide 3 / contact 3, frontload 15 / 3 / 2). Score 95 at in-band 0.90 and
   contact 0.011 needs reach 0.775: **+18-19 of the ~99 lost workspace poses**.
3. **K-dyad length is not a lever (< 1 point, sign flips held out).** CMA walked bk2 from 44-47 back to 39-41 in every
   stream: the RSSR's transmission falls 36 -> 22 deg as bk2 goes 37.6 -> 47, and the +15-deg crank phase that restores
   it swings the rod into hub 2 past dK ~42 (8 frozen / 24 held-out poses, invisible on the fit bench). The wide cell
   (35 / 45 / 75) is dead at contact 0.12. Stop B never binds (a1max -3 changes nothing); the law ends at the lobe skirt
   or lift-off first, and the stretched poses past th ~132 need a1e 76-100, i.e. they sit behind the a2 wall.
4. **The J3 side cannot re-centre the window inside the band.** twist-long-a2's law-only kill gate measured real
   kinematic headroom (reach 0.814-0.825, overhead 17-21/28, against the lead's 0.742 / 10 through the same IK), but
   parking failed: J2's GH ray follows the J3 seat (hub 2 0.68, L2 0.49-0.62), or a parked J2 grows a2 to 69-77 and
   link 2 / hub 3 ride over the deltoid (contact 0.06-0.07). Frozen, the wide window wins 10 fold poses (76 vs 86) and
   loses them again to contact (+7), knee slide (+5) and clip follow (0.955) on the same overhead / stretched poses.
   Every free CMA stream walked the twist back to -8..+2 deg (the lead sits at -6.8). Fixed at +8: frozen reach 0.742
   (the highest of the round) at in-band 0.828, 27.54.
5. **A rodless roller-flank drive works and is the simplest strap-level drive (cx 45.25 vs 49), 1.17 behind the rod.**
   It is a spherical cam: lugs must be shells about GH, and both pressure angles stay <= 45 iff the speed ratio a lies
   in [1/(cos t + sin t), cos t + sin t] (t = angle between the contact velocities). The only workable geometry is the
   pitch point (t ~3 deg), which forces a 130-deg arm wrapped around hub K. It carries 51.7 deg of K at pressure angles
   6.3 / 41.0 (the RSSR sidecar carries 37.3, with its own range ending at dK 41-43). Progressive laws cusp at the pitch
   point (every stream drove c to 0). A drive swap changes the metal and contact terms, never the fold.
6. **The 1 mm near-touch objective moved the metal to 1-2 mm.** parallelogram (50.14 at 2 mm, 44 poses in the shell)
   and roller-flank (46.82) are worse than frontload at 2 mm; only longdyad (34.03) is better. Per pose, 169-178 of
   ~370 taken poses on both sidecars have some metal under 3 mm (ALIGNMENT.md finding 4). Searches need the 2 mm
   objective, or the dominance gate (plain AND 2 mm), before CAD.
7. **Fast to frozen widened to 8.4-9.0 points** (10.30 -> 18.91, 10.63 -> 19.13, 11.73 -> 20.08, 16.74 -> 25.70)
   against round 7's 7.25. The fit bench takes reach 0.79-0.80 and overhead 2/12; frozen takes 0.72-0.73 and 8/28. A
   fast-bench gain under 1 point did not survive frozen (roller P1d 11.25 -> 20.48 vs P1 11.73 -> 20.08). The fit bench
   under-samples the overhead end that decides reach now; the final polish must use the representative envelope bench.
8. **Kill gates must include parking.** The window arithmetic alone over-predicted twist by +0.07 kinematic reach that
   became +0.005 frozen. Future gates run the model's own IK and the per-part in-band (hub 2, hub 3, L2) together.
9. **Pipeline findings (alignment audit, same hour):** the dashboard recomputed v_gap without the contact term
   (longdyad shown 17.84 vs verified 18.91); minarc's row counts its sensed K as passive (cx 33 -> 52 as a 4th active);
   12 of 17 verified rows have no held-out number and 16 no min-th margin on file. A farm claim batch sat 22 min in
   upload behind other sweeps; the frozen / held-out / flood claims ran locally in ~10 min.

Next (round 9; verified best 18.91, score 93.12, so 95 is not reached and score stays the objective - complexity second):

1. **Reach, by making the wide window parkable (target: frozen reach >= 0.775, overhead >= 14/28 at in-band >= 0.89,
   contact <= 0.011, 2 mm near-touch no worse than 34.03).** The kinematic headroom is measured (0.81-0.83, lesson 4);
   what kills it is metal over the overhead / stretched poses: hub 3 (0.35-0.60 in band), L2 (0.49-0.79), hub 2 when J2
   follows the J3 seat, and knee slide when b3 tilts. Levers, in order:
   - **(a) the J1 seat on the back of the shoulder for the knuckle** (round 8 lens-1 lever (a): planned, never run;
     twist took the J3 side). Law-only kill gate with parking on the winner's model: az1 {95, 75, 55, 35} x el1
     {67, 45, 25}, kinematic reach, overhead x/28 and hub 2 / hub K / L1b / L2 / hub 3 in band.
   - **(b) a lower hub 3 / L2 embodiment under the wide window**: the hub-3 crest seat (obliquity 16 deg, 0.82 in band,
     round-8 State), b3 0 with the knee drift taken by the knee window (lc 34 / phib -75), on twist's seed A / B.
   - **(c) the roller-flank drive on a longer dyad** (bk2 42-47): the rod sidecar's transmission walls the dyad at
     dK ~41-43, the roller carries 52 deg of K at pa <= 45. Cheap cell, cx 45.25.
2. **The winner's final polish, then the generation-winner CAD** (the lead's, not the round's): the representative
   envelope bench, the 2 mm near-touch objective, the ball centre at 4-4.5 mm, the crank short arm, follower and lobe
   window modelled as metal, r_h >= 15.5; the verifier; the L1 / user-style CAD and stills; EVOLUTION.md; the RC M2
   ball link in tools/hardware_catalogue.json.
3. **Do not screen again:** K-dyad length alone, a J3 twist on the knuckle, stop B / law-shape levers, the wide cell
   35 / 45 / 75, all-metal GE4E ball links, progressive laws at a pitch point; plus the round-7 list (direct pairs
   between O20 stacks, followers rigid with link 2, folded-side hubs and lobes, the Geneva tail).
4. **Complexity (second objective):** the 3-active class sits at 45.25-49 (roller-flank lowest). The cx-36 route
   (crank-rod / bighorn, positive four-bar K) waits on the msub ruling; lost-motion swivel (cx 43, 1 passive
   translation) waits on score >= 95.

### Needs the user's say (unchanged, plus one)

- A cuff IMU instead of the two knee-pin encoders (the pin knee 19.5 -> ~11.5; the winner 49 -> ~41).
- A fold margin below 5 deg.
- A sensed passive used only at static extremes counting as passive (minarc pick1 18.40 would be 3 active).
- Whether msub applies to a K positively slaved from q2 (a "no" opens crank-rod / bighorn at cx 36).
- New: the 2 mm near-touch as the claim column / dominance gate (ALIGNMENT.md A1) - it would rank longdyad first by 4.8.

## Round 9 plan (2026-10-16 ~20:35 UTC, track main, lead verified gap 18.91)

### State

- **Verified lead** (Bench(110,360) exact, frozen, margin 5, O20, fit Bench(60,160)): sidecar-longdyad-knuckle-3r
  **18.91** (score 93.12). 3 active (K slaved by the hub-2 lobe and the strap-level RSSR sidecar, never read), 0 passive
  translations, complexity 49.
  - Numbers: reach 0.725, follow 1.0, in-band14 0.897, in-band10 0.534, contact 0.011.
  - Near-touch 20.00 at 1 mm and 34.03 at 2 mm (26 poses under 2 mm); min metal 0.28 mm.
  - Lost 99 of 360: fold 86, slide 7, contact 4, parts 2 (E-L2).
  - Overhead 8/28 (lost fold 14, slide 4, contact 2).
  - Held out 22.67: reach 0.690, overhead 18/71 (lost fold 37, slide 11, contact 5).
  - Flood fill full 18.91 (0 dropped), knn 21.72.
  - Verifier json `verify/sidecar-longdyad-knuckle-3r_v_bench_frozen.json`.
- **Same protocol, verified:**

  | design | gap | note |
  |---|---|---|
  | minarc pick1 | 18.40 | 4-active sensed; cx 33 (52 under ALIGNMENT A5) |
  | sidecar-parallelogram | 19.13 | 2 mm 50.14: shell gamed |
  | sidecar-roller-flank | 20.08 | cx 45.25, held out 22.35 |
  | frontload | 22.82 | |
  | geneva rod | 23.57 | |
  | H1 | 27.20 | cx 19.5 |
  | zero-complexity ceiling | 31.04 | cx 0 |

- **Score arithmetic** (tools/dash_build.py line 37): gap = 100 (max(0, 0.90 - ib14) + max(0, 0.95 - follow) +
  max(0, 0.90 - reach)) + 100 contact.
  - In-band above 0.90 is worth 0 points.
  - One workspace pose of 360 is worth 0.278 points. Each 0.01 of in-band below 0.90 costs 1 point, i.e. 3.6 poses.
  - **95 (gap 13.75)** needs reach 0.777 at in-band 0.897 and contact 0.011, which is +19 poses. At in-band 0.88 it
    needs reach 0.797 (+26 poses).
  - So the part headroom (hub 3 0.599 of 80 samples at a median 13.0 mm; L2 0.749 of 132 at 11.6) is not a lever on
    its own. It is a budget: a reach lever may spend in-band down to 0.90, and it must buy more poses than it spends.
  - Every other part is >= 0.91 (crank 0.91, rod 0.89).
  - **The bench's in-band14 is scored on the clips only** (live alignment audit, commit 984b0b3,
    docs/alignment/live_audit_2026-10-16.md). On the lead's taken workspace poses, unscored, it is 0.874, and 0.841 at
    elevation 90-140. A won workspace pose therefore adds reach and contact, never in-band. Metal that leaves the band
    on the poses a lens wins is invisible to the gap: that is gaming pattern L2. Every lens reports the unscored
    workspace in-band, overall and at elevation 90-140, and may not fall below the lead's 0.874 / 0.841.
  - The same audit finds 95 reachable without overhead (overhead is 7.8 % of reach), and metal under 2 mm on 13-15 of
    the 18 taken overhead poses. Overhead stays in each lens's target as the user's own priority, not as a score lever.
- **Complexity 49, by item** (tools/simplicity.py):

  | item | points |
  |---|---|
  | 3 loops (drive RSSR, K closure, knee closure) | 12 |
  | 2 sensed knee pins | 10 |
  | 10 joints | 7 |
  | 6 passive rotations | 6 |
  | custom parts | 4.5 |
  | 7 bodies | 4 |
  | K spring | 3 |
  | catalogue parts | 2.5 |

  - The drive alone (lobe, bell crank, rod, ball links, horn, spring, its loop) is ~14-16 of the 49.
  - The roller flank drops it to 45.25.
  - Lower than ~41 needs a user ruling: the cuff IMU (-8), or msub for a positively slaved K (crank-rod / bighorn,
    cx 36).
- **Fold walls on the lead (unchanged since round 6):**
  - Stretched wall: a1max + a2 - 5. The poses past th ~132 need a1e 76-100 at a2 62.
  - The law ends at the lobe skirt (th 119.3).
  - The RSSR's own range ends at dK 43.0 (rod vs hub 2). Taken poses reach dK 38.1.
  - Stop B never binds.
  - Fold losses: 86-88 of 360 on every round-8 drive row, 84-86 on every rod variant (rounds 6-7).
- **Measured kinematic headroom, and why it was not parkable** (twist-long-a2, round 8):
  - Law-only reach 0.814-0.825 and overhead 17-21/28, against 0.742 / 10 through the same IK.
  - With J2 following the J3 seat: hub 2 0.68, hub 3 0.35-0.60, L2 0.49-0.62, and knee-E collides on every pose at
    seed B with b3 0.
  - With J2 parked: a2 69-77 and contact 0.06-0.07.
  - Frozen: +10 fold poses, re-lost to contact (+7), knee slide (+5) and clip follow (0.955).
  - CMA (4869 configs, converged) walked the twist back to -8..+2 deg in every stream.
  - That screen ran on frontload's crown-high rod drive. The strap-level sidecar has never been worn on the
    wide-window seeds.
- **J1 back seat, measured so far, on other families only:**
  - zc S-streams from (0, 45) / (30, 60) walk back to the acromion top (P0 57.92: reach 0.85 at in-band 0.42).
  - The posterior J1 line in the pin-knee family scored 122.45. Fold dropped from 47 to 6-20 poses, but 46-69 of 220
    poses hit skin, and no per-part split was taken.
  - alignment-free-knuckle-4r: hub 2 0.00 and L2 0.065 in band at distal J3 seats.
  - The 3R kinematic headroom inside the ruling is 0.942 (reach_attribution section 6).
  - **A knuckle at a back seat has never been measured.** It was round-8 lens-1 lever (a), never run. The knuckle bends
    link 1 at hub K, so hub 2's parking at a back seat is an open question. The lead's J1 is at az1 96.7 / el1 67.6.
- **Hub obliquity law:** hub 3 sits 0.64 / 0.69 / 0.82 in band at 39 / 30 / 16 deg. The J3 seats that fix it (wd
  58-71) cost overhead.
- **Protocol lessons:**
  - Fast to frozen is now 8.4-9.0 points: the fit bench takes overhead 2/12, frozen 8/28.
  - A 1 mm objective parks metal at 1-2 mm (parallelogram 50.14 at 2 mm).
  - Kinematic gates over-predict by the parking term (+0.07 kinematic became +0.005 frozen reach).
  - So every search this round uses the representative envelope bench (tools/env_bench.py) and the 2 mm near-touch
    objective, and every gate includes parking.
- **Do not screen again:**
  - K-dyad length alone;
  - the J3 twist as a search variable;
  - stop-B and law-shape levers;
  - the 35/45/75 cell;
  - GE4E all-metal links;
  - progressive laws at a pitch point;
  - the round-7 list: direct pairs between O20 stacks, followers rigid with link 2, folded-side hubs and lobes, the
    Geneva tail, hubs on link 2, O15 crest basins, K = c(q1), groove / dwell flanges.
- **Stale rows:** offset-axis-skin-hubs, seed-rcm-parallelogram and virtual-pole-4bar-j1 / -j2 still say "modelling".
  Nothing runs on them.

### Lenses

1. **back-seat-knuckle (reach; target: frozen reach >= 0.775 and overhead >= 14/28 at in-band >= 0.89, contact <=
   0.011, 2 mm <= 34.03).** Centre the overhead th set in the knuckle's window from the J1 side. This is lever (a),
   inside the ruling (back of the shoulder + acromion top, no front seats). Suggested id:
   backseat-sidecar-knuckle-3r.
   - **Model:** the lead's model, A1 config, with the drive metal off for the gate.
   - **Kill gate, <= 25 min:**
     - Grid: az1 {95, 75, 55, 35} x el1 {67, 45, 25}. Cell (95, 67) is the control.
     - Per cell, a short re-fit (<= 200 evals, fit bench) of J2 / J3 seats, a2 and bk1 / bk2, with the law held. A
       cell is never judged at the acromion seats' J2 / J3.
     - Measure: kinematic reach and overhead x/28 on Bench(110,360) poses; hub 2 / hub K / L1b / L2 / hub 3 / hub 1 /
       L1a in band (K at rest and open); per-part skin contacts at the lost and the newly won poses; the law-only 2 mm
       fast gap with parking.
     - **Pass** on a cell with kinematic reach >= 0.80 and overhead >= 14/28, every part >= 0.80 in band, and a
       law-only 2 mm gap at least 1.5 better than the control's.
     - **Else** report the per-part map (which part leaves the band, by how many mm, at which poses) and stop. That
       closes lever (a) for the knuckle with data.
   - **Low-complexity check, same grid, law-only:** wear H1 (pin knee, cx 19.5) as a side cell. It shows whether a
     back seat lifts the simpler class too (its posterior line died at 122.45, but the middle cells were never
     measured).
   - **Then CMA** from the passing cells: envelope bench, 2 mm objective, drive metal on.
     - Buildability floor: r_h >= 15.5, ball centre >= 4 mm, crank short arm and follower as metal.
     - Free: J1 seat inside the ruling, J2 / J3 seats, a2, bk1 / bk2, a1max, drive geometry.
   - Attribute every overhead pose won or lost by cause and part.
   - **Red team:** link 1a / hub 1 over the scapular spine and the posterior deltoid in extension and behind-the-back
     poses; the scapula handler's reach at the new seat.

2. **spend-the-band (reach from the J3 end, a different angle; same target).** The twist's kinematic headroom (0.81-0.83,
   overhead 17-21/28) died on contact, knee slide and follow, never measured with the strap-level drive. The in-band
   surplus above 0.90 is free to spend. Suggested id: widewin-sidecar-knuckle-3r.
   - **Setup:** wear the lead's sidecar drive and dyad on twist seed A (wdir(70,15), a2 66) and seed B (wdir(82-88,30),
     a2 58). The J3 axis is HELD at the seed inside a +-3 deg box. It is a constraint, not a search variable: free
     CMAs walked it back, and that is not re-asked.
   - **Free (metal and knee only):**
     - hub 3 at the crest seat (obliquity <= 16 deg, 0.82 in band) or b3 0;
     - the knee window (lc 34 / phib -75, ang_min) taking the knee drift;
     - hub 2's level;
     - an L2 planform turn from the raglan map in L2's own frame (one tangent arc, constant 8 x 3 section);
     - the drive geometry.
   - **Kill gate, <= 25 min, no CMA:**
     - First wear seeds A / B as they are with the sidecar drive and split the twist's +7 contact / +5 slide / follow
       by part and pose.
     - Then a <= 300-eval fit-bench re-fit of the free metal.
     - **Pass:** frozen-shape envelope-bench reach >= 0.76 at in-band >= 0.88, contact <= 0.015, knee-E collisions 0
       and follow >= 0.99.
     - **Else** stop with the per-part / per-pose map. That closes lever (b) and the J3 side for the knuckle.
   - **Then CMA:** envelope bench, 2 mm, same floor as lens 1.
   - **Red team:** the overhead axial -135 / 0 families, across the body, behind the back, the knee window extremes,
     and min `th` margin over the taken poses.

3. **simplest-drive (low complexity at the lead's reach, and the stretched wall; target: complexity by the tool <= 44
   at frozen gap <= 19.9 and 2 mm <= 36; stretch: <= 18.91).**
   - **Rule:** no user ruling may be assumed (no msub-free positive drive, no cuff IMU).
   - **Base:** the roller flank (verified 20.08, cx 45.25: rodless, carries 52 deg of K at pressure angles 6.3 / 41.0,
     no dK 41-43 rod-vs-hub-2 wall) worn on the lead's longer dyad and seats (bk2 39-47, a1max up to ~72; never the
     35/45/75 cell).
   - **Simplifications, each priced with tools/simplicity.py from a full mechanism record:**
     - the crank pivot on link 1b past hub K, giving a short straight arm instead of the 130-deg wrap (roller-flank
       doc "What next");
     - the horn flank machined into link 1a (one part fewer);
     - the pivot pin coaxial with an existing stack;
     - weird is welcome: any force closure that drops the K spring, or a lobe that is also the K stop, provided K
       stays determined and continuity holds.
   - **Gate, <= 20 min, fit bench, 2 mm objective:**
     - both pressure angles <= 45 over dK >= 45 at bk2 >= 42;
     - the arm clear of hub K / link 1b / skin;
     - >= 4 stretched fit poses regained (13 sit at th 124-157 behind a1max + a2 - 5);
     - or cx <= 44 at the lead's fast 10.30 + 1.
     Else report and stop.
   - **Then CMA:** envelope bench, 2 mm. Red team the roller's cantilever stiffness under ~2.5 N and lift-off.

Every lens:
- takes a new id;
- writes docs/concepts/viz/concepts/<id>.js and passes `node docs/concepts/viz/test.mjs <id>` + thumbs before the row is
  called screened;
- reports plain and near-touch at 1 and 2 mm, fast and frozen exact, held out, full + knn flood fill, overhead x/28,
  per-part in-band, the min `th` margin and tools/simplicity.py;
- runs `tools/alignment_audit.py audit <id> --ref sidecar-longdyad-knuckle-3r` before its verifier;
- gates each CMA run separately;
- is time-boxed to 75 min of modelling, and on a kill reports the measured reason and stops.

### Carried over (catalogue, ideated, never screened)

None.
- The round-4 judge picks stay closed. deltoid-crest-j3-3r and crest-knee-3r are O15 crest basins; their hub-3 crest
  seat is a seat option inside lens 2. slotted-eccentric-pin-knee-3r: its sibling was refuted at 115.21.
- The other 25 ideated entries are families dead in rounds 1-2 (telescopes, rails, SPMs, tracks, pointers, tapes) or
  hubless joints excluded by "Keep O20 only".
- crank-rod / bighorn (cx 36) wait on the msub ruling. lost-motion-swivel (cx 43, 1 passive translation, 0 expected
  gain) waits on score >= 95.

### Elsewhere, not to be duplicated

- **sidecar-longdyad-knuckle-3r:** the lead's final polish, then its verifier, the generation-winner CAD + stills,
  EVOLUTION.md, and the RC M2 ball link in tools/hardware_catalogue.json. The polish settings:
  - envelope bench, 2 mm objective;
  - ball centre 4-4.5 mm;
  - crank short arm, follower and lobe window as metal;
  - r_h >= 15.5.
- **geneva-tail-knuckle-pinknee-3r:** the gen-5 CAD (user_geneva_rod, wf_14bb06ea-22e).
- **The alignment auditor** (wf_0729deda-636, audit:live) re-wears rows. It is not a design screen.

### Needs the user's say (listed, not screened)

- A cuff IMU in place of the two knee-pin encoders (winner 49 -> ~41).
- A fold margin below 5 deg.
- A sensed passive used only at static extremes counting as passive.
- msub for a positively slaved K: a "no" opens crank-rod / bighorn at cx 36.
- The 2 mm near-touch as the claim column / dominance gate (ALIGNMENT A1).
- A per-pose worst-point cap (ALIGNMENT A3: 48 % of the lead's taken poses have metal under 3 mm).

**Alignment ledger at 22:45 UTC (round-9 note, `python3 tools/alignment_ledger.py latest`).**
- gamed: seed-offset-3r-slides only (3 passive translations; shown as Flagged).
- watch (relevant to round 9):
  - sidecar-longdyad-knuckle-3r (lead): metal close to the skin, near-touch 1 mm 20.00 / 2 mm 34.03 / 3 mm 155.98.
  - sidecar-parallelogram-knuckle-3r: a continuity spread, static 19.13 vs knn 22.21.
  - sidecar-roller-flank-knuckle-3r: no held-out number on file.
- Every round-9 claim goes through the A1 dominance gate: it must beat the lead plain AND at 2 mm. roller-longdyad's self-measured 18.67 / 2 mm 33.10 passes that gate but is worse at 1 mm (20.30) and held out (23.73).
- Audit run wf_2c9de6ed-0a4 covers four designs: roller-longdyad, the lead, kneeless-roller, and geneva-rod's new R17 slaved-coordinate judge change.

## Round 9 results (2026-10-16 ~20:35-23:36 UTC; the closer never ran - the session hit its usage limit; written by the 2026-10-17 lead from the rows, events and ledger)

| design | verified gap (score) | held out | complexity | ledger | note |
|---|---|---|---|---|---|
| roller-longdyad-knuckle-3r | **18.67 (93.21)** | 23.73 | see row | watch | lead's long dyad with a roller drive for K; envelope-corrected 18.56 |
| sidecar-longdyad-knuckle-3r (round-8 lead) | 18.91 (93.12) | 22.67 | 49 | watch | reference |
| kneeless-roller-knuckle-3r | 21.07 (92.34) | 24.59 | 23.75 | **gamed** (idle: re-measured K.ang span 0.0 deg) - skeptic pending | knee -> rigid bracket |
| kneeless-sidecar-knuckle-3r | 21.11 (92.32) | 25.34 | ~27 | - | knee -> rigid 3 mm bracket |
| twin-k2-sidecar-knuckle-3r | dead (60.86 fast / 67.32 frozen) | - | - | - | second knuckle hub cannot sit close to the skin |

**Winner: a TIE (corrected 2026-10-17 ~02:45 UTC by the alignment audit wf_824e062d-913, all five rows final WATCH,
none gamed).** roller-longdyad-knuckle-3r reads 18.67 vs the lead's 18.91, but paired per-pose on the exact claim
protocol (`tools/alignment_paired.py`, docs/alignment/remeasure/*_paired_claim.json) the 0.24 is inside the bench's
noise: bench 90 % interval [-2.62, +1.73]; held out the lead is better by 1.06 (P(roller better) 0.135; pooled 0.191).
On buildable readings (catalogue KBRM-02 ball link + priced stops: the lead 19.76 / 19.36, held out 23.53) roller is
~1.2 ahead; at the 1 mm contact line the order reverses (lead 20.00, roller 20.30). By the tie-break (fewer passive
translations, then complexity) roller-longdyad (cx 43.75 vs 49) is the nominal winner, but no lead change is claimed.
The original line read: winner roller-longdyad-knuckle-3r 18.67 (score 93.21), by 0.24 over the
round-8 lead. The user retired the 2 mm A1 dominance gate on 2026-10-17 (CLAUDE.md), so the plain verified gap decides.
Honest caveat: it is worse held out (23.73 vs 22.67), so the gain does not generalise yet; its final polish must claim
held out. The user ruled the same day that a sensed joint is a joint: minarc pick1 (18.40) is a 4-active design, so
the 3-joint designs are the leaders.

**Lessons.** (1) Replacing the pin knee by one rigid bracket costs ~2.2 gap points on the bench (+0.86 held out) and
halves complexity (49 -> 24-27) - BUT the bench's GH is an ideal fixed point, so the knee's real job is unscored: under a
3 mm GH-centre error 66.6 % of postures stay within a 3 mm liner with the planar knee against 38.7 % without it (5 mm:
36.2 % vs 17.7 %; docs/alignment/remeasure/*_ghoffset.json). The knee-free rows also press deeper (summed contact depth
27-44 mm vs the lead's 6.2) and stand off worse at elevation 90-140 (in-band 0.80 vs 0.84). The audit's other open items:
contact counts poses not depth (proposed T5); the pin-knee window is [ang_min, 180 - ang_min] (roller-longdyad's knee
runs to 153 deg for no score - restore ang_min >= 26.88); drive caps sit at their limit (dK 46.17 of 46.25, PA 43). (2) The K drive's form (sidecar RSSR vs roller flank) moves the gap by <= 0.3: K's law is
worked out; reach at the J2 fold (86 of 360 workspace poses, 20 of 28 overhead) is still the whole gap to 95.

**Next focus (round 10).** Reach first, simplicity second (the user: fewer joints and parts matter because the final
product drives and tracks every joint - planner context only, all work stays kinematic). Attack the fold geometry, not
K's law: (a) the a2 wall - poses past th ~132 need a1e 76-100 at a2 62; (b) the J1 seat toward the back of the
shoulder, inside the allowed seats; (c) CORRECTED 2026-10-17 by the audit: do NOT steer to the knee-free class on bench score alone - any knee-free
or knee-changing claim must also report the GH-offset within-liner share (3 mm and 5 mm GH-centre error, the
docs/alignment/remeasure/*_ghoffset.json harness) and summed contact depth beside the gap. Whether the encoded knee
pins count as joints (if yes every pin-knee row is 5 DOF, over the cap) is with the user. Target: frozen reach >= 0.775, overhead >= 14/28 at in-band14 >= 0.88, contact <= 0.01; score >= 95
(gap <= 13.75). Report plain gap, held out, complexity (2 mm near-touch no longer required). Dead directions: HANDOFF
section 5 and twin-k2.

## Round 10 plan (2026-10-17, track main, lead verified gap 18.67)

### State

- **Lead (best verified gap, not gamed):** roller-longdyad-knuckle-3r **18.67** (score 93.21), Bench(110,360) exact
  frozen, margin 5, O20, fit Bench(60,160).
  - Reach 0.725 (261/360), follow 1.0, in-band14 0.8937, in-band10 0.513, contact 0.0054. Gap = in-band 0.63 + reach
    17.5 + contact 0.54.
  - Lost 99: fold 88, slide (knee) 9, contact 2. Overhead 8/28 (lost fold 14, slide 4, contact 2).
  - Held out 23.73 (lead-before 22.67). Flood full 18.67 / knn 20.34. Min th margin 5.18 (0 poses under 5).
  - Drive: dK taken 45.6 of dK_lim 46.25, horn PA 42.7.
  - 3 active, 0 passive translations, complexity 43.75. Parts in band: hub 3 0.739, L2 0.736, crank 0.797, rest >= 0.93.
  - **Ledger: watch** (`alignment_ledger.py get` exit 0; audit re-running). Carry these reasons:
    - its 0.24 over sidecar-longdyad is 2 contact poses (0.86 of a pose), with identical reach (261, overhead 8);
    - it is worse held out (-1.06) and at 1 mm (-0.30);
    - it fails the 1-point rule, so its "win" is noise, not a better exo;
    - continuity / fold-margin records are missing from the audited row.
- **Same protocol, verified:**

  | design | gap | held out | cx | ledger / note |
  |---|---|---|---|---|
  | sidecar-longdyad-knuckle-3r | 18.91 | 22.67 | 49 | watch: 15.12 points in the 1-2 mm shell; 3 mm 155.98 |
  | sidecar-parallelogram | 19.13 | 22.03 | 49 | watch (continuity knn 22.21) |
  | sidecar-roller-flank | 20.08 | 22.35 | 45.25 | watch |
  | kneeless-roller-knuckle-3r | 21.07 | 24.59 | 23.75 | **gamed**: idle check reads the deleted knee's constant angle; skeptic pending |
  | kneeless-sidecar-knuckle-3r | 21.11 | 25.34 | 28 | no entry; workspace in-band 0.809 / 0.740 at elev 90-140, below the lead's 0.874 / 0.841 (pattern L2) |
  | H1 pin knee | 27.20 | - | 19.5 | |
  | zero-complexity ceiling | 31.04 | - | 0 | |
  | minarc pick1 | 18.40 | - | 33 | 4 active (sensed K): not a 3-joint lead |

- **95 arithmetic.** Gap 13.75 needs reach 0.774 at the lead's in-band and contact: +18 workspace poses
  (0.278 points each). At in-band 0.88: reach 0.788 (+23).
  - In-band is scored on the clips only. Every lens must also report the unscored workspace in-band, which may not
    fall below 0.874 overall / 0.841 at elev 90-140.
- **Where the 88 fold poses sit** (round-9 judge, sidecar lead, same walls on the roller):
  - 22 below the folded wall (th < 30.5 = a2 - a1 + 5);
  - ~64 above the drive-stroke wall (th ~109.5-112);
  - the overhead set spans th 18-146: 7-9 folded at th 24-37, 10 stretched at 110-142;
  - raising the stretched wall gains +6 / +13 / +16 / +27 poses at th 113.5 / 117.6 / 120.2 / 129.4, but only +1 to +3
    of them are overhead;
  - poses past th ~132 need a1e 76-100.
- **Closed with measured reasons (do not rescreen):**
  - J1 re-seats (back 20.29 / 61.21 / 73.21 vs control 10.30; eave 27.92; crown-lateral 25.29). Round 9's "Next
    focus (b)" re-lists the back seat, but round9_ideation.md measured it dead.
  - The J3 twist / wide window (K range dK 82; no strap-level drive carries more than 52).
  - The long-stroke flank: the dK 55-57.5 boss sits on the deltoid (88-94 contact poses), and co-fits walk back to
    dK 42-47.
  - Twin K2 (67.32 frozen; hub K2 0.09-0.57 in band).
  - K-law shape, stop B, dyad length, two-rise and folded-side lobes, hubs on link 2.
  - In-sample and env-fit polishes (no pick travels).
- **What is still open, from the data:**
  - (1) The 4-joint class is the only class with frozen reach >= 0.77 (arm-parked-knee-4r 0.772 at in-band 0.799,
    contact 0.035; park4 0.750 at 0.864). minarc's free K cut fold losses to 56 (vs 88), but it pays a knee window of
    16 and contact 9. The redundant 4R's kinematic headroom is ~1.0; the cost is entirely parking (hub 4 0.51, link 3
    0.32 when the 4th hub sits on the deltoid).
  - (2) The lead's non-fold losses (knee slide 9, of which 4 overhead, plus contact 2) are 3.1 points that no lever
    has targeted on the knuckle. The pin knee's longer lc measured 0, but only on H1.
  - (3) The first drive-wall step (+6 poses at th 113.5, needing dK ~48-50) is inside the roller's measured PA 43 if
    the flank contact stays within r ~24 mm of hub K's axis. The dK 55+ flank that died ran to r 30-33.
  - (4) Simplicity: deleting the knee costs ~2.2 frozen points (the b3 tilt: hub 3 at 0.50-0.55 in band on a GH ray,
    plus E-L2 parts 8 frozen / 17 held out) and halves complexity. The drive is ~14-16 of the knuckle's points.
- **Fresh container:** the local .cache bench is rebuilding (~20 min). Gates run first on the CPU farm
  (tools/cloud_run.py). RunPod balance ~$34: keep each batch small and set workersMin to 0 after it.

### Lenses

1. **fourth-joint-window (reach, Keemink 2018 TNSRE 26(4) inside the 4-joint cap).** Target: frozen reach >= 0.78,
   in-band14 >= 0.88, workspace in-band >= 0.874 / 0.841, contact <= 0.01, gap <= 13.75.
   - **Topology:** the knuckle chain J1-K-J2-J3 as a redundant non-orthogonal 4R. K is a joint: sensed, 4 active. It
     is determined for MVP1 by a centring spring and stops acting on its own angle, scored with the continuity flood.
   - **The Keemink step nobody has run:** free all four axis rest angles (bk1, bk2, a2, J3 tilt / seat) jointly, so the
     fold set lands outside the workspace. Resolve the redundancy by the spring's static law: no per-pose-free K.
   - **Park every hub:** no hub on the deltoid (park4's failure). Use the lead's strap-level hardware.
   - **Gate, <= 25 min:** law-only per-pose reach with the static K law on Bench(110,360), plus per-part parking. It
     passes at kinematic >= 0.82 with hub 2 / hub K / hub 3 / L2 >= 0.80 in band.
   - **Labelling:** 4 joints. The user wants 3 first, so it is reported as the 4-joint route to 95, never as a 3-joint
     lead, with complexity by tools/simplicity.py.
   - **Red team:** the spring's two feasible arcs (arm-parked snap events), drift under gravity across the thorax
     (pick1 4.1-7.7 deg), and the stop feel.
2. **knee-window-and-first-wall (reach, 3 joints, small sure steps; suggested id: kneewin-roller-knuckle-3r).**
   Target: frozen gap <= 15.5 at in-band >= 0.885, held out <= 22.67; stretch 13.75.
   - **Regain the in-window losses first:** split the lead's 9 slide + 2 contact poses by the binding knee constraint
     (pin-a / pin-b limit, knee closure, E-L2 clearance). Re-cut the knee window (lc, phib, ang_min, pin offsets, knee
     stops) on the knuckle. The lc lever measured 0 only on H1.
   - **Then lift the stroke wall one step:** dK 48-50 at bk2 39-41 with the conjugate flank held inside r <= 24 mm of
     hub K's axis and PA <= 43. That is +6 poses at th 113.5.
   - **Gate:** law-only plus parking on Bench(110,360), >= +9 of these poses kept with metal on.
   - **Kill:** report the per-pose binding constraint and stop.
   - **Red team:** the overhead axial -135 / 0 families; the knee at its window edges under a 3 mm GH offset.
3. **simplest-fold (low complexity at the lead's reach; suggested id: bare-roller-knuckle-3r).** Target: complexity
   <= 22 at verified gap <= 19.9 (stretch <= 18.67), workspace in-band >= 0.874 / 0.841, 0 sensed passives,
   0 passive translations.
   - **Base:** kneeless-sidecar (cx 28, not gamed) or kneeless-roller (cx 23.75; its 'gamed' idle finding must be
     resolved by the skeptic before it is called a base).
   - **Regain the 2.2 points the knee bought:**
     - a J3 seat where the GH ray meets the deltoid at <= 16 deg (0.82 in band), priced against the overhead cost;
     - route the bracket's E leg off link 2 (E-L2 0.15 mm costs 8 frozen / 17 held-out poses).
   - **Cut complexity:**
     - drop the K spring with a positive (desmodromic) double flank or a stop that is also the lobe;
     - merge lobe, stop and hub cap;
     - every merge priced by tools/simplicity.py.
   - **Carry the kneeless watch reasons:** GH-centre liner misfit (38.7 % within 3 mm), workspace in-band, the
     unproven spring-closed cam, and the drive PA 42.5 / 43.
   - **Gate, <= 20 min, fit bench:** cx <= 24 and fast within +1 of kneeless-roller's 16.70. Else report and stop.

**Every lens:**
- takes a new id;
- writes its motion preview (docs/concepts/viz/concepts/<id>.js, test.mjs and thumbs) before the row is called
  screened;
- reports plain gap fast and frozen exact, held out, the full + knn flood, overhead x/28, per-part and workspace
  in-band, min th margin and tools/simplicity.py. The 2 mm near-touch is optional; contact stays metal < 1 mm;
- searches on the envelope bench, fits the shape on the claim's fit bench and claims held out;
- runs `tools/alignment_audit.py audit <id> --ref roller-longdyad-knuckle-3r` before its verifier;
- has a 75-min modelling box. On a kill it reports the measured reason and stops.

### Carried over (catalogue, ideated, never screened)

None. The round-4 picks stay closed:
- deltoid-crest-j3-3r and crest-knee-3r: the crest seat is an option inside lens 3;
- slotted-eccentric-pin-knee-3r: its sibling was refuted at 115.21.

breathing-hubs (a radial lift of hub 2, the relay's parking fix) fails the standing-slide rule: 8-15 mm of travel plus
the block puts metal out of band in the low state. offset-axis-skin-hubs needs 3 passive translations. The rest are
families dead in rounds 1-2.

### Elsewhere, not to be duplicated

- roller-longdyad-knuckle-3r: the alignment re-audit (uncommitted docs/alignment files), its final polish (claim held
  out) and the generation-winner CAD + stills.
- kneeless-roller-knuckle-3r: the skeptic ruling on the idle 'gamed' finding.
- sidecar-longdyad-knuckle-3r: the gen-6 CAD, which was never built.

## Round 10 results (2026-10-17 ~03:50-07:20 UTC, track main, closer)

All numbers are frozen exact on Bench(110,360), fitted on Bench(60,160), and re-measured by an independent verifier.
Ledger verdicts were re-read with `tools/alignment_ledger.py get <id>` at 07:18 UTC, just before naming the winner.
Complexity is tools/simplicity.py v2.2 as run at close.

| design (lens) | verified gap (score) | held out | reach / overhead | cx | ledger | outcome |
|---|---|---|---|---|---|---|
| **slipper-nose-knuckle-3r** (3: nose for roller) | **18.49 (93.28)** | 23.45 | 0.725 / 8 of 28 | 22.25 (18.25 like-for-like) | **watch** (exit 0) | **winner**; Pareto move of the lead |
| skinnormal-shortk-knuckle-4r (1: 4th joint) | 18.58 (93.24) | 22.43 | 0.742 / 8 of 28 | 32.5, 4 active | no entry (dead, not audited) | dead by the kill rule (>= pick1's 18.40); verifier upheld |
| dipped-law-groove-knuckle-3r (2: dip below stop A) | 18.64 (93.22) | 24.07 | 0.725 / 8 of 28 | 24.25 | **gamed** (exit 3) | passed over; cannot be called verified or a leader |
| groove-desmo-knuckle-3r (3: spring-free K) | 22.64 (91.77); claim 19.29 refuted | 28.90 (audit 28.77) | 0.681 / 8 of 28 | 18.25 | watch (exit 0) | verified at the corrected stop B; behind the lead by 3.97 |
| roller-longdyad-knuckle-3r (previous lead) | 18.67 (93.21) | 23.73 | 0.725 / 8 of 28 | 20.25 | watch | reference |

**Winner: slipper-nose-knuckle-3r, v_gap 18.49 (score 93.28), ledger WATCH. It beats the previous verified lead
18.67 by 0.18, so it becomes the verified lead under the "best verified gap, not gamed" rule. That is not a reach
gain.**
- Same 261 workspace poses and the same 2 contact poses as the lead: reach 0.725, overhead 8/28, follow 1.0.
- All of the 0.18 is in-band (ib14 0.8955 vs 0.8937). The gap splits as reach 17.50 + in-band 0.45 + contact 0.54.
- Paired per-pose against the lead (claim dumps):
  - bench -0.18, 90 % interval [-0.26, 0.00], P(slipper better) 0.70;
  - held out 23.45 vs 23.73, -0.28, interval [-0.47, 0.00], P 0.94.
- It is below the 1-point rule. The verifier attributes the 0.18 to the drive-arm re-fit (beta -176.7, r_c 15.37,
  lift 0.79), not to the nose: the lead's own MR63ZZ roller worn on the same re-fit arm scores 18.36. That 18.36 is
  a verifier attribution run, not a claimed or audited row.
- The nose deletes the roller (-2.0 complexity like-for-like) and raises the metal floor on 93 of 371 bench poses
  and 224 of 851 held-out poses, and on no bench pose is it lower. Taken poses under 3 mm: 100 vs 133 on the bench,
  198 vs 273 held out.
- Ties did not decide anything: every row has 0 passive translations.
- Passed over: dipped-law-groove-knuckle-3r (18.64) is gamed. It is behind the winner anyway. Measured reasons:
  - **fold_margin**: minimum fold margin on file 0.184 deg held out (0.204 on the bench). Under the family reading
    min(m_sub, m_eff) with K off its rest, 84 of 371 bench and 202 of 850 held-out taken poses fail.
  - **T3**: the design's own model waives m_sub on dipped poses, and its verifier wrote the coupled reading that
    accepts the waiver.
  - **P1**: the gain is in-sample. Against its own D=0 control it is 0.70 better on the bench (P 0.80, not
    significant) and 1.10 worse held out (24.07 vs 22.97, P(dip better) 0.000).
  - It stays gamed until the user rules on B1: does m_sub at K's rest, or the coupled reading, decide the fold rule?

**Alignment (every watch reason of the round's designs, as upheld by the skeptics).**
- **slipper-nose-knuckle-3r: WATCH, 6 reasons upheld, 2 refuted.**
  - *reporting*: the row verdict text still reads "screened -" although the status is verified. The dashboard shows
    the sweep best 13.0 (score 95.27), 5.49 below the verified 18.49.
  - *M5*: the lead's clock spring (0.08 N.m + 0.03 N.m/rad) force-closes a SLIDING nose. The return stroke runs at
    crank PA 29.5 + 4.97 friction = 34.47 deg; the lead's rolling crank side runs at 8.2.
    - No R17 / preload / lift-off number exists; there is only a hand calculation (drag 0.01-0.02 N.m).
    - mu 0.087 is assumed, with the wear test pending. The score holds to mu 0.12.
  - *G4* (family, identical pose by pose to the lead):
    - with K at rest (204 of 371 bench poses), m_sub is under 5 deg on 106 poses and under 1 deg on 50;
    - minimum 0.000 deg at pose 227 (plane 15, elev 75, axial 15);
    - the reported fold margin 5.181 / 5.006 reads m_plain, so this waits on the user's B1 ruling;
    - the knee runs to 151.92 of its 154.78 window.
  - *T5*: the 2 overhead bench contacts at elev 165 press 9.01 + 5.74 = 14.75 mm (lead 16.46). Held out: 10 contacts,
    46.12 mm (lead 49.88). sidecar-longdyad presses only 6.23 mm summed, so this design is 2.37x deeper and +8.52 mm,
    past the T5 margin.
  - *NEW-ws-inband* (unscored): raised-arm workspace in-band at elev 90-140 is 0.800, with 0.199 of the metal above
    14 mm (max 30.8 mm). Lead 0.798, sidecar-longdyad 0.841; held out 0.822.
  - *NEW-stale-complexity-ruler*: the row's 22.25 charges the cuff-knee loop, which the lead's record frees. Like-for-
    like it is 18.25 vs the lead's 20.25, but the dashboard shows it 2.0 MORE complex.
  - Missed by the audit, written down by the skeptic:
    - the dashboard shows the verified row contact-free, because it has no v_contact (12 verified rows share this gap);
    - the hand-calculated contact stress used a 3.5 mm flank radius, where the verifier measured 1.285 mm at rest;
    - the horn margin under the 43 cap is 1.9 deg, not 2.2.
- **groove-desmo-knuckle-3r: WATCH, 12 reasons upheld, 1 refuted.**
  - *held_out / S1*: 28.77 held out vs 22.64 on the bench, +6.13, over the +6 line (the lead drops +5.06). Stop B at
    32.25 deg loses 37 held-out poses against 12 on the bench.
  - *reporting / R1*: the row verdict, the doc and the dashboard still show the refuted 19.29: +0.62 vs the lead,
    held out 24.96, slop +-0.54 deg, sweep best 17.21.
  - *NEW-planar-gate*: the planar, linear groove-fit gate was worth 3.35 points. The true crest is 8.93 against the
    claim's own 8.44 window, and the groove PA is 36.17 in 3-D (the claim said 30.5).
    - The planar gate is still live in the model file, so any search run on that model gets the 3.35 back.
  - *M2*: a straight O1.5 dowel binds: it tilts 4.2 deg, giving 0.108 mm of run-out against 0.02 mm of clearance.
    - With a 1.61 groove the gap is 23.77; with 1.59, 23.48.
    - Either way it falls behind frontload's 22.82.
  - *G5*: the closed two-walled roller slot is counted as rolling. Counted as a track pair it is 19.25, an edge of
    1.0, not 2.0.
  - *M5*: K slop of +-1.6-2.0 deg is never read; the skeptic derives +-0.9-1.0 deg but did not measure it.
  - *G4*: the groove PA is 36.17 against a 37.29 gate, so it passes only for mu <= 0.12. Dry steel at mu 0.15 fails.
  - *M3*: two features are unchecked: the pocket in link 1b and the groove's onset corner.
  - *T5*: 2 bench contacts, 10.97 + 6.03 = 17.0 mm; held out 8 contacts, 44.81 mm.
  - *NEW-ws-inband*: 0.781 vs the lead's 0.798.
  - Skeptic, missed: the knee runs past H1's 149.54-deg window, and the verified wear output still carries
    uncut-stroke values.
- **dipped-law-groove-knuckle-3r: GAMED** (fold_margin, T3, P1, above). Its watch reasons:
  - *dominance*: -2.59 at 2 mm;
  - *P4*: the fold reading changed in the model and verifier commits;
  - *NEW-contact-for-inband*: held-out contacts are a strict superset of the lead's, 17 vs 10 poses, 81.20 vs 49.88 mm;
  - *T1*: recovered pose 203 sits at 0.48 mm, and 5 of the 8 taken overhead poses have metal under 2 mm;
  - *M5*: a spring-closed 0.068 mm dip with no closure check;
  - *NEW-sub-tolerance-feature*: 10 um of lobe error = 0.35 deg of K, against a 2.37 deg floor;
  - *G4*: horn PA 43.0 at the cap, and the arm clears hub K by 1.04 mm;
  - *NEW-preview-not-claim*: the preview was rendered at th_c 50 / w 8 and carries no dipD;
  - *S5*: knn flood 20.32 (+1.68).
  - Skeptic additions:
    - half of the bench contact gain is the dip no longer reaching overhead pose 316;
    - pose 182 is still in contact;
    - 83 of the 84 dipped bench poses already have m_sub < 5 deg in the D=0 control (min 0.205).
- **skinnormal-shortk-knuckle-4r**: no ledger entry (dead and not audited). Its verifier found no modelling bug.
- **roller-longdyad-knuckle-3r** (previous lead): WATCH. Its reasons stand as listed in the round-10 plan, and the
  slipper inherits G4, T5 and NEW-ws-inband pose for pose.

**Lessons (measured).**
1. **Reach did not move this round.** Every 3-joint row takes the lead's 261 workspace poses and 8/28 overhead. The 88
   fold poses are untouched: 73 stretched at the K-drive stroke wall (th ~106.6) and 15 folded.
2. **A 4th joint that acts only past the 3R wall trades fold for contact about 1:1** (skinnormal family, 7 frozen
   claims).
   - Fold / contact loss goes 74 / 8 -> 59 / 19 -> 55 / 19 -> 50 / 24 as K opens. Reach gains about +2.8 points, and
     contact plus follow give back about +3.2.
   - The folded state takes 0 poses: the K sub-chain's own fold is |bk1 - cK| + 5.5 = 32.8 deg, against th_lo 29.7,
     whichever way K turns.
   - The fast Bench(60,160) score no longer ranks this class: fast 12.18-16.14 became frozen 18.58-21.05, in a
     scrambled order.
   - Frozen reach = law-only reach minus 19-28 poses, and the loss grows with K's opening.
3. **On one slaved flank, the PA-43-capped stroke (~46 deg) is one budget.** A dip below stop A spends it: dK_lim
   falls 46.2 -> 43.8 / 41.2 / 38.8 / 36.5 at D 1 / 2 / 3 / 4, about one stretched fold pose per degree of K.
4. **A small hardened nose beats a bearing roller at equal points.**
   - A smaller follower radius lowers the horn PA, worth about +2.3 deg of stroke per -0.5 mm.
   - Re-fitting the drive at the honest friction (mu 0.087) costs 0 points; capping the PA on the old flank costs
     +1.23.
   - Drive-only re-fits transfer to the frozen and held-out benches. Seat re-fits do not (CMA B: 19.81 frozen,
     24.78 held out).
   - The lead's stroke was not the binding wall at mu <= 0.05: dK_lim 46.5 -> 60 bought 0 poses, because K's dyad
     window (a1max) caps first. **Stroke must grow together with a1max / bk.**
5. **A desmodromic (spring-free) K needs the follower >= R + rho_min off the relative pole.** Here that costs
   ~5 deg of stroke. The planar groove gate under-read the 3-D crest by 0.69 mm, which was worth 3.35 points: check
   cam crests in the worn frames, not in a planar model.
6. **A knuckle stop B within 5.5 deg of the K dyad's stretch refuses every pose at the verifier's priced margin,**
   but scores normally at 5.0. Cap a1max at bk1 + bk2 - 5.5.

**Next focus (round 11).** The score has not reached 95: the best verified gap is 18.49, and 95 needs 13.75. Reach
stays first: +18 workspace poses at the lead's in-band and contact (0.278 points each).
- **Why the stroke.** The measured lever is the K drive's stroke on a longer K dyad. docs/research/fold_ceiling.md
  (exact one-level parking, calibrated 0.722 vs 0.725) estimates:
  - 57.5 deg on 32 / 48: reach 0.767, score ~94.7;
  - ~75 deg on 32 / 48 (or 28 / 50): 0.775-0.778, score ~95.0-95.1, with held out +0.067.
  - These are estimates before the drive's own metal.
  - One-sided contacts cap at 46.5-51.8 deg (involute arc of action). The bilateral RSSR reached 77.2 deg at
    transmission >= 48 in docs/research/longstroke_drive.md (longstroke-slipper-knuckle-3r, in progress elsewhere,
    not to be duplicated).
- **So round 11 attacks the stretched wall with a ~75 deg slaved K on a 28-32 / 48-50 dyad (a1max raised with it),
  using the drive metal parked.** Lens-1's warning applies directly: every pose won with K far open cost about one
  contact pose.
  - Select on a frozen objective, or on a contact proxy that knows K is open, never on fast alone.
  - Report the per-pose fold / contact / slide split against the law-only ceiling.
  - Respect a1max <= bk1 + bk2 - 5.5.
- **Stack the free gains on whatever wins:** the nose (-2.0 cx, floor raised on 93 poses) and the re-fit arm (the
  roller on it scores 18.36).
- **The 15 folded-side poses** (scapular-plane overhead, th 7.7-22) are not moved by K in any layout measured. They
  need their own lever, and a2 re-placement is refuted (a2 60: 20.84).
- **Open with the user before any claim that rests on them:** B1 (m_sub at K's rest vs the coupled reading), and the
  slipper's record fixes (verdict text, v_contact, like-for-like complexity).
- **Do not rescreen:** the dip below stop A, the planar groove gate, the spring-held spare 4R past the 3R wall, and
  stroke beyond the a1max window without lengthening the dyad.

## Round 11 plan (2026-10-17 ~07:25 UTC, track main, lead verified gap 18.49)

### State

- **Lead (best verified gap, not gamed):** slipper-nose-knuckle-3r **18.49** (score 93.28), Bench(110,360) exact
  frozen, fit Bench(60,160), margin 5, O20. Ledger **watch** (`alignment_ledger.py get`: exit 0).
  - Reach 0.725 (261/360), overhead 8/28, follow 1.0, ib14 0.8955, contact 0.0054 (2 poses). Gap = reach 17.50 +
    in-band 0.45 + contact 0.54. Held out 23.45. Flood full / knn 18.49 / 20.16.
  - Lost 99: fold 88 (73 stretched at th >= 106.6, 15 folded at th 7.7-22), knee slide 9, contact 2. Overhead
    losses 20: stretched 9, folded 5, knee 4, contact 2.
  - Drive: O2.37 nose on the re-fit flank, mu 0.087, PA + friction 40.8 <= 43, dK_lim 49.8. K's dyad window (a1max)
    binds before the drive: 52.8-60 deg of flank at lower mu bought 0 poses.
  - 3 active, 0 passive translations. Complexity 22.25 on the record, 18.25 like-for-like (the lead roller 20.25).
  - **Watch reasons carried (do not buy points the same way):**
    - M5: a clock spring force-closes a SLIDING nose (return stroke at crank PA 34.47 with friction vs 8.2 rolling);
      no R17 / preload / lift-off number;
    - G4 (family): with K on stop A (204 of 371 bench poses) m_sub < 5 deg on 106, < 1 deg on 50, min 0.000 at
      (15, 75, 15); the fold margin on file (5.181 / 5.006) reads m_plain. This is the user's open B1 question;
    - T5: the 2 elev-165 contacts press 9.01 + 5.74 = 14.75 mm (held out 10 contacts, 46.12 mm), 2.37x
      sidecar-longdyad's 6.23 mm;
    - NEW-ws-inband (unscored): raised-arm workspace in-band 0.800 at elev 90-140, 0.199 of the metal above 14 mm
      (max 30.8 mm); sidecar-longdyad 0.841;
    - reporting: verdict text "screened -", no v_contact, complexity shown 22.25 vs 18.25 like-for-like; the
      dashboard shows sweep best 13.0 (95.27), 5.49 below the verified number.
- **Same protocol, verified (ledger):**

  | design | gap | held out | cx | note |
  |---|---|---|---|---|
  | dipped-law-groove-knuckle-3r | 18.64 | 24.07 | 24.25 | **gamed** (fold margin 0.184, m_sub waiver, P1 in-sample): not a leader |
  | roller-longdyad-knuckle-3r | 18.67 | 23.73 | 20.25 | watch; same 261 poses; the roller on the re-fit arm 18.36 (attribution run, not a claim) |
  | sidecar-longdyad-knuckle-3r | 18.91 | 22.67 | 25.5 | watch; shallowest contacts (6.23 mm), ws-inband 0.841 |
  | sidecar-parallelogram-knuckle-3r | 19.13 | 22.03 | 25.5 | watch (knn flood 22.21) |
  | kneeless-roller / -sidecar | 21.07 / 21.11 | 24.59 / 25.34 | 23.75 / 28 | watch; GH-offset liner 38.7 % vs 66.6 % with the knee |
  | groove-desmo-knuckle-3r | 22.64 | 28.77-28.90 | 18.25 | watch; spring-free K, held out +6.13 |
  | minarc pick1 / skinnormal-shortk-4r | 18.40 / 18.58 | - / 22.43 | 32.5 | 4 active (a sensed joint is a joint): not 3-joint leads |

- **95 arithmetic.** Gap 13.75 = +18 workspace poses at the lead's in-band and contact (0.278 points each); at
  ib14 0.88, +23. Every pose won with K far open has cost about one contact pose so far (lens 1, round 10).
- **The stretched wall (73 bench / 211 held out):** internal rotation >= 90 across the body (64 of 73). It is the K
  drive's stroke on a short K dyad (dK 46 -> a1e 54.3 -> th 106.6), and K's window (a1max) right behind it.
  - fold_ceiling exact one-level parking, calibrated 0.722 vs verified 0.725 (held 0.695 vs 0.682). The window holds
    272 today; 28 / 50 at 57.5 deg: 290 (R_est +4 0.761, ~94.6); 28 / 50 at 75: 298 (0.772, ~95.0, held +0.067);
    **32 / 48 at 75: 300 (0.775 -> est. verified 0.778, ~95.1)**. Before the drive's metal and the knee.
  - Binding parts on the new poses at +4 mm: hub 2 18/29, link 2 near J2 20/29, link 1b 23/29. +8 mm halves the
    parts' in-band.
  - **The drive (longstroke_drive.md, in progress elsewhere):** one-sided contacts cap at the involute arc of action:
    nose 46.5, roller 51.8 (its contact walks to r 31 mm, the deltoid), groove 41.2. The phased RSSR reaches 77.2
    (PA <= 42, transmission >= 48; crank-tip PA never under ~27: the rod's lean). The spherical-4R coupler (C4: an arc
    on two radial pins, all four axes through GH) has a PA-42 range of 78.5 kinematically, cx 28.0 vs the RSSR's
    30.5. It is not modelled with metal.
  - **NEW wall, stage 1 (longstroke_drive.md section 1):** the hub-2 rim lobe that writes K's law must keep its crest
    inside hub 2's O20 + 1.5 skirt (r_lobe + s_arm phi <= 11.5) and its PA <= 42. On 28 / 50 with a 77-deg stage 2,
    the linear law kK 1.96 closes 267 / 360, kK 2.3 closes 272, kK >= 2.7 kills the lobe at its base radius,
    two-slope 1.8 / 2.8 gives 269, the 'track' law 194-229. The window holds 298: **26 poses sit between the law and
    the window** (knee, closure at the margin, the law's slope). A long stage 2 alone does not reach 95.
- **The folded side and the overhead cone (26 poses, 11 of the 20 overhead losses):** scapular-plane abduction,
  plane -20..45, elev 90-165.
  - 15 folded (th 7.7-22 vs the wall |a1 - a2| + 5 = 24.67). Hub 2 is the wall there: its disc clears 4 of 15 at
    F2 62 mm (median need 71; held out 21 of 46).
  - 9 knee slide (R_tol; plane -15..15, elev 90-165, external rotation 15-45). The knee runs to 151.92 of its
    154.78 window; the build rule holds ang_min >= 26.88.
  - 2 contacts at elev 165 (plane 15 / 30, axial -60): the horn lug on hub K / the crank, 9.01 + 5.74 mm.
  - Dead for this cone, measured: K in any layout (the K sub-chain's own fold |bk1 - cK| + 5.5 = 32.8 vs th_lo 29.7,
    0 poses); a2 re-placement (a2 60: 20.84, held 24.17, parts in-band 0.55-0.63); J1 re-seats (back 20.29-73.21,
    eave 27.92, crown-lateral 25.29); folded-side lobes; the longer knee link on H1 (0); the centred-knee control
    (19.33 bench, but held out 22.97 vs the lead's 23.73 - the only held-out gain on file).
- **Complexity (second objective):** the 3-active class runs 18.25-25.5 like-for-like; the drive is ~14-16 of a
  knuckle's points (lobe, follower, crank, spring, stage-2 pair). The positive four-bar K (crank-rod / bighorn, cx 36
  on the old ruler) was parked in rounds 8-9 on the msub question, which is now B1.
- **Closed with measured reasons (do not rescreen):** the dip below stop A (one budget with the stroke; gamed); the
  planar groove gate (3-D crest +0.69 mm = 3.35 points); a spring-held spare 4R past the 3R wall (1:1 fold-for-
  contact; fast does not rank the class: fast 12.18-16.14 -> frozen 18.58-21.05, scrambled); stroke beyond the a1max
  window without a longer dyad (dK_lim 46.5 -> 60 bought 0); stop B within 5.5 deg of the K dyad's stretch (refuses
  every pose at the priced margin: keep a1max <= bk1 + bk2 - 5.5); re-placing the window; seat re-fits judged on the
  fit bench (CMA B 19.81 frozen, 24.78 held); per-part relaxations that drop uncleared poses (fold_ceiling section 5);
  twin K2; J3 twist; in-sample and env-fit polishes.
- **Machinery:** fresh container, the local .cache bench rebuilds (~20 min): gates run first on the CPU farm
  (tools/cloud_run.py, exo-cpu1). Farm spend approved $8 per 12 h until ~17:20 UTC; RunPod balance ~$34. Small
  batches, `tools/runpod_guard.py audit` before and after, workersMin 0 after each batch.

### Lenses

1. **coupler-longstroke (reach, the stretched wall, both stages; suggested id: coupler-longdyad-knuckle-3r).**
   Target: frozen exact gap <= 13.75 (reach >= 0.775, ib14 >= 0.88, contact <= 0.01), held out <= 22.67.
   - **The pair the RSSR agent is not building:** stage 2 as the spherical-4R coupler (C4): an arc coupler on two
     radial MR63ZZ pins, all four axes through GH, no rod lean, the swing phased to straddle the 90-deg transmission.
     Seeds: the verified seats (stop A 37.55, a2 57.22), K dyad 32 / 48 (then 28 / 50), a1max <= bk1 + bk2 - 5.5,
     stroke >= 75 deg with every PA <= 42.
   - **Fix stage 1 in the same model:** split the gain so the lobe stays legal - a higher stage-2 ratio g lowers the
     lobe's PA (tan pa = kK s_arm / (g r)) and its lift; or let the coupler's own ratio rise toward the stretched end
     so a linear lobe suffices. Report the law-only closure against the 298-300 window.
   - **Gates, <= 25 min each, farm:**
     - A, law-only on Bench(110,360) exact kinematics with the real stage 1 + stage 2: >= 290 / 360 closed (the lobe
       law today: 272).
     - B, the exact one-level parking (`docs/research/fold_ceiling/parking_k.py`) with the coupler, its pins and the
       crank sampled as parts: R_est(+4) >= 0.765 and parts in-band >= 0.755; coupler parts >= 0.85 in band.
   - **Search and select:** the fast bench does not rank K-open designs. Search on the 1 mm near-touch gap plus a
     K-open term (metal under 1 mm on any fit pose with dK > 20 counted twice); select the top 8 by frozen exact
     wear, never by fast.
   - **Stack the free gains:** the drive-arm re-fit (the lead roller on it: 18.36) and the stock O2.5 nose wherever a
     contact follower remains (stage 1), its PA + friction <= 43.
   - **Report:** per-pose fold (stretched / folded) / contact / slide against the law-only ceiling and the window;
     contact depth (T5, vs the lead's 14.75 mm); m_plain, m_sub (rest and moved), m_eff and the family reading
     (`tools/alignment_msub_rest_probe_model.py`); raised-arm workspace in-band (not below the lead's 0.800).
   - **Coordinate:** read docs/research/longstroke_drive.md and events.jsonl first. If the longstroke agent has started
     C4 with metal, do not duplicate it: take the stage-1 law (gain split) on its model instead, under this id.
   - **Kill:** gate A < 280 or gate B < 0.755: report the binding stage and part, and stop.
   - **Red team:** the coupler's assembly mode across the full-grid flood (no branch change); the coupler arc and pins
     against hub 2's crown and link 1b in the K-open poses; K slop from pin play at 75 deg of stroke.
2. **lobe-free four-bar (low complexity at the same reach; suggested id: fourbar-longdyad-knuckle-3r).** Target:
   complexity <= 15 by tools/simplicity.py v2.2 (lead 18.25 like-for-like), frozen gap <= 18.49 (stretch <= 16),
   0 springs, 0 sliding pairs, 0 sensed passives, 0 passive translations.
   - **Topology:** delete the whole drive (lobe, follower, crank, spring, nose). A positive spherical four-bar from
     q2 to K: ground = link 1b, input = a crank pin rigid with link 2 inside hub 2's O20 stack (r <= 7.5), output =
     link 1a's horn, coupler = the C4 arc on two radial pins (not two ball links: fewer passive rotations). K is
     determined everywhere, positively, so it needs no force closure (M5 disappears).
   - **The law is the risk, measured:** a four-bar from near-toggle averages kK ~1 unless r_horn ~2.5, and kK 1.56
     lost 0.043 reach (round 8). On the 32 / 48 dyad the stroke may open early (law shape was worth <= 0.2 frozen);
     size the four-bar for the window, not for the lobe's dwell.
   - **The fold reading, without waiting on B1:** a positively slaved K is never at rest, so the strict reading
     min(m_sub, m_eff) >= 5 must hold on every taken pose. Gate it; a design that passes it rests on no ruling.
   - **Gate, <= 25 min, farm:** law-only Bench(110,360) closure >= 272 / 360 (the lobe law's), transmission >= 48
     over the used q2 range, strict fold reading failing <= 5 taken poses, and cx <= 15 from a full mechanism record.
   - **Kill:** report the binding term (gain, transmission, m_sub) and stop. If only m_sub fails, list the design for
     the user's B1 ruling with the count; do not claim it.
   - **Red team:** the toggle near the folded end (dead point under a disturbance); the crank pin in hub 2's stack;
     the full-grid flood (assembly mode).
3. **overhead-cone (reach, the OTHER wall; suggested id: conehub-knuckle-3r).** Target: >= +6 of the 26
   scapular-plane overhead-cone losses taken frozen on the lead's drive (gap <= 16.9, overhead >= 12/28) with no loss
   elsewhere; a stackable delta for lens 1 / the RSSR.
   - **Lever: move hub 2's DISC and the knee, not the window** (K and a2 are measured dead here). Cheap first, each
     priced by an exact per-part march on the 26 poses plus every clip frame:
     - (a) a hub-2 axis tilt b2 off the GH ray (the lead already tilts J3 by b3; the cuff knee takes the drift), chosen
       so the disc lies along the bunched deltoid in the cone. Price the knee load: the knee must stay inside
       [ang_min, 180 - ang_min] with ang_min >= 26.88;
     - (b) a knee re-cut aimed at the 9 overhead knee poses (lc, phib, pin offsets), claimed held out: the centred
       knee is the only held-out gain on file (22.97 vs 23.73);
     - (c) the 2 elev-165 contacts: move the horn lug / crank off hub K's crown there.
   - **Gate, <= 25 min, farm:** law-only plus exact per-part parking: >= +6 of the 26 closed and cleared, hub 2 /
     link 1b / link 2 in band >= the lead's at +4, the knee inside its window, 0 new losses on the other 334 poses.
   - **Report:** the GH-offset liner share (3 / 5 mm, docs/alignment/remeasure/*_ghoffset.json harness) for any knee
     change, contact depth, raised-arm workspace in-band, the min th and m_sub margins.
   - **Kill:** fewer than +3 poses at the gate: report which part binds each of the 26 and stop.
   - **Red team:** the knee at its window edges under a 3 mm GH-centre error; the hub-2 tilt's cuff twist at the
     knee pins (MR63ZZ pairs).

**Every lens:**
- takes a new id and never re-screens an id in the exclude list below;
- writes its motion preview (docs/concepts/viz/concepts/<id>.js, `node docs/concepts/viz/test.mjs <id>`,
  `node docs/concepts/viz/thumbs.mjs`) before the row is called screened;
- reports plain gap fast and frozen exact, held out, flood full + knn, overhead x/28, per-part and workspace in-band,
  min th margin, m_sub (rest / moved), contact depth, v_contact and tools/simplicity.py v2.2 like-for-like with the
  lead; the 2 mm near-touch is optional, contact stays metal < 1 mm;
- writes the verifier's per-pose dump (`tools/alignment_paired.py dump`, bench and held out, +-0.05);
- searches on the envelope bench, fits the shape on Bench(60,160), selects frozen and claims held out;
- runs `tools/alignment_audit.py audit <id> --ref slipper-nose-knuckle-3r` before its verifier;
- has a 75-min modelling box; on a kill it reports the measured reason and stops.

### Carried over (catalogue, ideated, never screened)

None. The round-4 picks stay closed (deltoid-crest-j3-3r and crest-knee-3r: the crest seat; slotted-eccentric-pin-knee-3r:
its sibling refuted at 115.21). The other 25 ideated entries are families dead in rounds 1-2 (telescopes, rails, SPMs,
pauldrons, tapes). crank-rod / bighorn (never catalogued, parked on msub) are revived inside lens 2.

### Elsewhere, not to be duplicated

- longstroke-slipper-knuckle-3r: the RSSR long-stroke drive (77.2 deg), CMA on the farm (jobs_cma1 / jobs_cma2),
  docs/research/longstroke_drive.md.
- roller-longdyad-knuckle-3r: the gen-6 user-style CAD (user_style_roller.py) and its R1 attribution.
- slipper-nose-knuckle-3r: the round-10 winner's final polish and generation CAD (the lead's).

### Lead bookkeeping (not the round's)

- Fix slipper-nose-knuckle-3r's record: verdict text (verified, not "screened -"), v_contact 0.0054, complexity
  like-for-like (18.25), the dashboard sweep-best display.
- Its M5 action: R17 on the return stroke at mu 0.087 / 0.12 / 0.15 when CAD exists; the wear test before CAD.

### Needs the user's say (listed, not screened)

- **B1:** does m_sub at K's rest, or the coupled reading, decide the fold rule? It decides G4 for the whole family
  (lead included) and whether a positively slaved K must pass m_sub. Lens 2 is gated on the strict reading so it
  needs no ruling; no claim rests on the lenient one.

## Round 11 results (2026-10-17 ~07:25-13:25 UTC, track main, closer)

All numbers are frozen exact on Bench(110,360), fitted on Bench(60,160), and re-measured by an independent verifier.
Ledger verdicts were re-read with `tools/alignment_ledger.py get <id>` at 13:19 UTC, just before naming the winner.
Complexity is tools/simplicity.py v2.2. Every row has 3 active joints and 0 passive translations, so the tie rules
decided nothing.

| design (lens) | verified gap (score) | held out | reach / overhead | cx | ledger | outcome |
|---|---|---|---|---|---|---|
| **trimlug-k165-knuckle-3r** (3c: overhead contacts, run as a T5 polish of the lead) | **18.51 (93.27)** | 23.47 | 0.725 / 8 of 28 | 22.25 (18.25 like-for-like) | **watch** (exit 0) | **winner**; not a lead change (+0.02 behind 18.49) |
| coupler-longdyad-knuckle-3r (1: spherical-4R coupler, C4) | 23.87 (91.32) | 29.73 (CMA best C1) | 0.739 / 4 of 28 | 6 passive rotations, no record | no entry (dead, not audited) | dead by the hard kill; verifier upheld the death |
| fourbar-longdyad-knuckle-3r (2: lobe-free four-bar) | 51.75 (81.18) | 55.30 | 0.617 / 8 of 28 | 14.0 | no entry (dead, not audited) | dead under the strict B1 reading; verifier upheld the death |
| dogring-draglink-knuckle-3r (1: coaxial dog + drag link) | **97.83 (64.43)**; claim 22.64 refuted | 101.1 (claim 25.36) | 0.347 / 4 of 28 | 25.25-27.25 (skeptic; no record) | watch (exit 0) | refuted: unchecked arm-vs-link-1b clash |
| slipper-nose-knuckle-3r (lead, reference) | 18.49 (93.28) | 23.45 | 0.725 / 8 of 28 | 22.25 (18.25) | watch | stays the verified lead |

**Winner: trimlug-k165-knuckle-3r, v_gap 18.51 (score 93.27), ledger WATCH (exit 0, final skeptic verdict 13:18 UTC).
It does NOT beat the previous verified lead 18.49 (slipper-nose-knuckle-3r): it is 0.02 behind, so the lead does not
change.** It is the only round-11 design whose own number an independent verifier confirmed as a working design; the
other two confirmed numbers are deaths (23.87, 51.75) and the fourth claim was refuted.
- It is the lead with the horn-lug band trimmed at r_K <= 21.27 mm (the farthest flank contact over the drive's range,
  19.77 at dK_lim 49.8, plus a 1.5 mm wall). It is one cut on the existing link 1a: no new part, no complexity change.
- Same 261 workspace poses, the same 2 contact poses (237 and 264, both elev 165) and the same 8/28 overhead as the
  lead; 0 of 1624 poses differ in taken or contact (skeptic). The +0.02 is in-band bookkeeping: 3 in-band lug samples
  were removed.
- What it buys is contact DEPTH (T5), not score: bench 14.74 -> 13.18 mm (pose 264: 5.74 -> 4.18), held out 46.35 ->
  40.59 mm over the same 10 contacts. Trim 1.0 gives 12.67 / 38.71 at the same gap but leaves a 1.0 mm wall.
- Trim checks (verifier T1-T5): the contact line stays on retained metal (edge margin 2.53 mm, 1.99 over the full
  stroke), back thickness >= 4.30 mm behind every contact, lug connectivity equal to the lead's, dense lug against every
  member at every taken pose equals the lead's minima (crank 0.153, nose 0.424, others >= 20.96 mm).
- The spec's main lever is refuted: a radial lift makes both elev-165 contacts DEEPER (T5 16.07), the crank underside
  cut gains 0.02 mm and costs 0.21 fast in-band, and the hub-2 cap edge break misses (the contact is on the housing
  wall, 8.17 mm up its 12.25 mm crown).
- Generation CAD: the winner is the lead plus one cut, so its generation CAD is the slipper-nose CAD (in progress,
  `pipeline/full-exo/designs/l1_slipper-nose/`) with the link-1a lug trimmed at r_K 21.27 mm. No separate build.
- Passed over as gamed: none. No round-11 design is gamed.
- Not a round-11 lens row, recorded so the next planner reads the state right: inband-rssr-knuckle-3r's polish pick3
  (complexity 28.5) was CONFIRMED by its verifier at 18.33 priced / 22.86 held out, and the lead ruled it a TIE with
  slipper-nose at 12:45 UTC (unpriced 18.32 / 23.54 vs 18.49 / 23.45, paired held CI [-0.83, +1.31]; pick3 chosen best
  of 3 after the claims were known; it needs r_h >= 15.65 with the catalogue O9 head). Ledger WATCH (13:18 UTC).

**Alignment (every watch reason of the round's designs, as upheld by the skeptics).**
- **trimlug-k165-knuckle-3r: WATCH, 6 reasons upheld, 4 refuted** (continuity: flood re-run full 18.51 with 0 dropped,
  knn 20.18; idle: the knee_moved false positive; S1: held-out drop 4.96 < 6.0 and the pair CIs include 0;
  NEW-stale-complexity-ruler: the record overstates complexity by 4.0, against the design).
  - *reporting*: the row verdict text still reads "screened -" on a verified row; the dashboard sweep best 13.02 reads
    as score 95.27, above the user's 95, while the verified number is 18.51 (93.27).
  - *T5*: contact depth still counts nowhere in the score. Bench: 2 contacts, pose 237 at 9.01 mm (crank; the trimmed
    lug is also 8.35 mm deep there) and pose 264 at 4.18 mm (lead 5.74); sum 13.19 vs 14.75. Held out: the same 10
    contact poses, 40.58 vs 46.12 mm; 4 of them (not the row's 5) are 0.9-1.7 mm shallower. It is still 2.12x
    (+6.96 mm) sidecar-longdyad's 6.23 mm.
  - *M5* (carried from the lead): one clock spring (0.08 N.m + 0.03 N.m/rad) force-closes a sliding nose at an assumed
    mu 0.087 (horn PA 40.77, crank 34.47 deg effective). No R17, dynamics or preload number is on file.
  - *G4* (family): with K at rest, m_sub < 5 deg on 106 of 204 poses and < 1 deg on 50, minimum 0.000 at (15, 75, 15).
    The claim's 5.181 / 5.006 reads m_plain. Identical to the lead (largest difference 0.000 deg). Waits on B1.
  - *NEW-ws-inband* (unscored): raised-arm workspace in-band at elev 90-140 is 0.8002 on the bench with 19.9 % of the
    metal above 14 mm (p95 20.16 mm), 0.8218 held out; the lead reads the same, sidecar-longdyad 0.841.
  - *R1*: errors in the row text. It says 5 held-out contacts are lug-deepest (the doc, the verifier and the audit dump
    say 4); its headline 13.02 / reach 0.775 is the fit bench, which has no contact pose; the limiter leaves out the
    lug's 8.35 mm at pose 237; n_configs is 45 but the sweep file holds 31 entries with one timestamp.
  - Missed by the audit, written down by the skeptic: (a) the held-out fold margin 5.006 deg is 0.006 above the rule;
    the slipper red team's predicted K lag of 0.42-0.53 deg takes it to 4.95-4.97 unless the build carries the
    +0.75 deg K lead, which the claim's model does not; (b) the modelled lobe follower sits inside hub 2's O20 and the
    real lobe ring, follower and straddle boss are not sampled; (c) the verifier skipped the required continuity
    flood (the audit's flood is clean, so a process gap, not a lost number).
  - Wearer: overhead 8/28 on the bench (5 of 13 at elev 140-160, 3 of 15 at 160-200), 18/71 held out; raised arm 38/85
    and 96/229; taken poses under 2 mm 30/371 bench and 67/852 held; 4 of the 8 taken overhead poses under 2 mm; min
    metal 0.07 mm. Paired against sidecar-longdyad: P 0.62-0.63 bench, 0.18-0.19 held out, every interval includes 0.
- **dogring-draglink-knuckle-3r: WATCH, 8 reasons upheld, 5 refuted** (continuity: the flood was run for the first time
  and drops 0 poses, 97.83 full and knn; fast_frozen: fast 17.19 -> frozen 22.64 is +5.45, inside the verified rows'
  4.6-14; idle: false positive; NEW-silent-check: the skipped RING-L2 check costs 0 poses; G1: near-touch is
  report-only).
  - *M3*: the claimed 22.64 / 25.36 was bought by an unchecked clash. The arm (member 9) turns with the dog ring about
    J2 by up to -31.5 deg at K 44 and passes over link 1b's root ramp at r 15.2 mm: -0.18 mm overlap, under the
    0.15 mm running gap on 183 of 374 taken bench poses and 442 of 872 held out. collide() has no arm-vs-link-1b pair
    and the arm's stacked level is read only at phi 0. Corrected: 97.83 (held 101.1).
  - *sampling*: sample-weighted in-band 0.864 vs part-weighted 0.852 (+1.23 points); the horn is 0.23 in band (median
    16.8 mm, 3.4 % of the samples).
  - *M2*: the drag-link eyes are modelled O8 against the stated O9 on 2 x MR63ZZ; with EYE_R 4.5 the claim reads 22.76
    and the corrected number 97.95 (+0.12).
  - *M5*: the dog is one-sided, so K's spiral spring back-drives horn -> drag link -> arm -> sector through the 4R on
    the return (pa_max_taken 35.5 deg, table end 42); no R17 or dynamics number.
  - *R3*: the claim was selected "by frozen" among at least 4 frozen-exact wears (22.64, 24.34, 29.84, 26.07); only the
    fast numbers are in the sweep file.
  - *complexity / G5*: no mechanism record, so the dashboard shows null; built from the note's counts it is
    25.25-27.25, 3-5 points above the lead's 22.25.
  - *reporting*: the dashboard sweep best 17.19 (93.75) sits 80.64 below the verified 97.83.
  - Missed by the audit (skeptic): the 97.83 on record is worn with the drive parked (every surviving pose has K
    <= 2.8 deg, held 2.5), and the refuted claim's knn flood lost 2.83 points, just under the 3-point escalation.
  - Wearer (corrected wear): overhead 4/28 bench and 13/71 held (lead 8/28, 18/71); raised arm 21/85 and 62/229.
- **coupler-longdyad-knuckle-3r** and **fourbar-longdyad-knuckle-3r**: no ledger entry (dead, not audited). Their
  verifiers found no modelling bug. Watch points they raised, not ledger reasons: the coupler pick sits on a 0.1 mm
  knife edge (cr_zr 7.9 puts the crank arm 0.99 mm over hub K's crown on 116-118 poses: gap 144.98), and its kill
  rule as worded is literally false (k100 / 108 / 112 / 120 pass it at gap >= 225; it holds for every working config).
  The four-bar's CRKL-L1b pair is held to 1.0 mm where 0.15 may apply (0 poses on either best; bounded by the ghosts
  43.95 / 26.26).

**Lessons (measured).**
1. **Reach did not move for the second round running.** No verified 3-joint row takes more than the lead's 261 / 360.
   The two long-stroke lens-1 drives either lost their gain to their own metal (coupler: +5 poses = -1.4 gap, but
   -3.9 in-band and +2.8 contact) or bought it with an unchecked clash (dogring).
2. **A long-stroke K drive must stay inside link 1b's corridor.** Every spherical 4R that reaches K >= 75 deg at
   PA <= 42 from a crank beside hub 2 points its arm 55-110 deg off link 1b, where the skin rises up to ~33 mm above
   link 1b's skin-fitted level: the drive either touches (including with K parked) or, raised or on the far side,
   leaves the band (drive in-band <= 0.56 at <= 2 K-open contacts). Swung back over the corridor (t1 ~25) it reaches
   at most 0.729 drive in-band, and the PA-legal stroke shortens to 60-65 deg - the stroke the lead already has.
3. **The horn pin of any J2-to-K spherical 4R with PA <= 42 up to K >= 60 sits at t3 in [-110, +35] deg from link
   1b's direction** (0 of ~3000 survivors outside, on four K-dyad cells). K's swing therefore always carries the horn
   across link 1b's root band: a linkage drive must stack its horn above link 1b's root, or link 1b's root ramp must
   start beyond r_h + 4.
4. **Every pair of members in relative motion needs a per-pose check across the whole swing.** The dogring claim
   passed because collide() had no arm-vs-link-1b pair and the stacked level was read at rest only; a second check
   was silently skipped because the frozen copy of the model did not carry the attributes it read. A model-level
   pair-coverage probe is missing from the toolkit.
5. **Under the strict B1 reading a positively slaved K is worthless near rest.** Every four-bar pose under |K| ~20 deg
   fails m_sub on the 28-32 / 48-50 dyad, so the best four-bar holds K at 27.6-53.8 deg; on the raise-overhead clip
   frames hub 2 then needs 80.6 mm from GH (lead ~62) and is in band on 0.10 of them (median 24 mm off the skin). The chain alone, drive metal deleted, scores 43.95 (26.26
   under the coupled reading). The lobe-free low-complexity path is closed unless the user rules B1 the lenient way,
   and even then it is behind (coupled frozen 36.46).
6. **Overhead contacts come from the side and from above, not from below.** A radial lift away from GH makes them
   deeper; moving the same samples 1 mm toward K's axis gains 0.9-1.0 mm. The lug band behind the end of the flank's
   stroke is the lead's overhead contact limiter and it is tied to K's stroke: any lever that buys stroke pushes it
   further out.
7. **The fast bench is blind to the stretched wall, for the third time** (longstroke ghost, dogring, coupler).
   On Bench(60,160) every stroke from 46 to 87 deg reaches the same 0.7875; on Bench(110,360) the longer strokes come
   back as contacts (26 vs 9). The coupler's K-open contacts read 1 fast, 2 on Bench(110,360) and 11 held out: any
   kill or select rule that counts K-open contacts must be read held out.
8. **Process:** the verify template's refutation bar ("within 10 of the round-3 champion's 68.93", or 75.94 / 66.97 by
   other champions' verifiers) is stale - every round-11 design clears it, and the verifiers judged against the lead
   18.49 instead. The trimlug verifier skipped the continuity flood the rules require.

**Next focus (round 12).** The score has not reached 95: the best verified gap is 18.49 (slipper-nose; inband-rssr
pick3 18.33 is ruled a tie), 95 needs 13.75. Reach stays first: +18 workspace poses at the lead's in-band and contact.
- **Attack the overhead cone, the lens round 11 never built** (lens 3 a / b: only lever c ran, as trimlug). The 26
  scapular-plane overhead-cone losses (15 folded at th 7.7-22, 9 knee slide, 2 contact) are 11 of the 20 overhead
  losses and are untouched by every K drive measured. Measured reason to expect points: hub 2's disc clears only 4 of
  the 15 folded poses at F2 62 mm against a median need of 71; the knee runs to 151.92 of its 154.78 window; the centred
  knee is the only held-out gain on file (22.97 vs 23.73). Levers in order: (a) a hub-2 axis tilt b2 off the GH ray so
  the disc lies along the bunched deltoid, the knee taking the drift inside [ang_min, 180 - ang_min] with ang_min >=
  26.88; (b) a knee re-cut aimed at the 9 knee-slide poses, claimed held out; (c) the lateral (r_K, plan-view) relief
  of the elev-165 parts, not a lift (lesson 6). Gate: >= +6 of the 26 closed and cleared on the lead's drive with 0
  new losses elsewhere.
- **If the stretched wall is attacked again, use only the in-band drive and the corridor rule.** inband-rssr's drive
  metal costs 0.29 points; its long-dyad report-only row regains 20 held-out fold poses but gives them back in overhead
  contact depth (29.3 vs 10.8 mm). So the next stretched-wall step is that drive on the long dyad WITH the overhead
  parts relieved laterally, searched on the envelope bench and selected held out - never a new drive beside link 1b
  (lesson 2) and never a slaved-everywhere K under the strict reading (lesson 5).
- **Machinery before the next claims:** a pair-coverage probe (every member pair in relative motion has a per-pose
  check over the full swing, and the frozen copy carries every attribute collide() reads); the verify template's bar
  set to the current lead 18.49 and its tie rule; the continuity flood made a hard step of the verifier.
- **Complexity:** nothing new under the lead's 18.25 like-for-like survived (the four-bar at 14 is dead at 51.75).
  The lowest verified complexity at the lead's reach is still the lead family.
- **Do not rescreen:** a K drive with its crank or arm beside link 1b (coupler, 1540 configs); a slaved-everywhere K
  under the strict reading (four-bar, 2520 configs); a radial lift of overhead drive metal; underside-only cuts for
  side-wall contacts.

### Needs the user's say (unchanged)

- **B1:** does m_sub at K's rest, or the coupled reading, decide the fold rule? It decides G4 for the whole family and
  is now the only thing that could reopen the lobe-free four-bar (coupled frozen 36.46, still 18 points behind).

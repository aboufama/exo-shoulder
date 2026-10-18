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
  parts relieved laterally, searched on the envelope bench and selected on the envelope-selection draw (envsel), then
  CLAIMED held out [lead 2026-10-17 20:25: was "selected held out" - selecting on held-out poses leaks the split;
  alignment skeptic 20:15, P2] - never a new drive beside link 1b
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

## Round 12 plan (2026-10-17 ~13:40 UTC, track main, lead verified gap 18.49)

### State

- **Lead (best verified gap, not gamed):** slipper-nose-knuckle-3r **18.49** (score 93.28), Bench(110,360) exact
  frozen, fit Bench(60,160), margin 5, O20; held out 23.45; flood full / knn 18.49 / 20.16. Ledger **watch** (exit 0).
  - Reach 0.725 (261/360), overhead 8/28, follow 1.0, ib14 0.8955, contact 0.0054 (2 poses). Gap = reach 17.50 +
    in-band 0.45 + contact 0.54. Complexity 22.25 recorded (18.25 like-for-like): R 4, loops 3, bodies 5, joints 8,
    1 sliding + 1 rolling pair, 1 clock spring.
  - Lost 99: fold 88 (73 stretched at th >= 106.6, 15 folded at th 7.7-22), knee slide 9, contact 2 (poses 237 / 264,
    elev 165). Overhead losses 20: stretched 9, folded 5, knee 4, contact 2.
  - Watch reasons carried (do not buy points the same way): **M5** (a clock spring force-closes a sliding nose; the
    drive red team retired it quasi-statically, R17 on CAD still to run); **G4** (K at rest: m_sub < 5 on 106 of 204
    poses; the claim reads m_plain 5.181 / 5.006; B1 is the user's); **T5** (2 contacts press 9.01 + 5.74 mm; held out
    10 contacts 46.12 mm); **held-out margin 5.006** breaks under the predicted 0.42-0.53 deg K lag unless the build
    carries the +0.75 deg K lead; **NEW-ws-inband** (elev 90-140 in-band 0.800, sidecar 0.841); **reporting** (sweep
    best 13.0 shown as 95.27).
- **Same protocol, verified:** trimlug-k165 18.51 / 23.47 (the lead + one lug cut; T5 13.18 / 40.59 mm; watch);
  inband-rssr pick3 18.33 priced / 22.86 held (unpriced 18.32 / 23.54; **ruled a tie** with the lead, paired held CI
  [-0.83, +1.31]; cx 28.5; overhead contact depth held 4 poses / 8.4 mm; drive metal costs 0.29 points); roller-longdyad
  18.67 / 23.73 (cx 20.25); sidecar-longdyad 18.91 / 22.67 (shallowest contacts 6.23 mm); groove-desmo 22.64 / 28.77
  (**spring-free**, cx 18.25, stroke capped at 41.2 by the horn PA); kneeless-roller / -sidecar 21.07 / 21.11.
  4-active (a sensed joint is a joint): minarc pick1 18.40, skinnormal-shortk-4r 18.58, cx 32.5 - not 3-joint leads.
  **Gamed:** dipped-law-groove-knuckle-3r 18.64 (fold margin 0.184), seed-offset-3r-slides.
- **95 arithmetic:** gap 13.75 = +18 workspace poses at the lead's in-band and contact (0.278 points each); at ib14
  0.88, +23. No verified 3-joint row has taken more than 261 / 360 for two rounds.
- **The stretched wall (73 bench / 211 held out; internal rotation >= 90 across the body on 64 of 73).** The lead's
  window [24.67, 106.6] holds 272. 28 / 50 at a 75 deg stroke holds 298, 32 / 48 holds 300 (est. reach 0.778, ~95.1)
  before drive metal and knee. **The measured binder is STAGE 1, not stage 2:** the hub-2 rim lobe must keep its crest
  inside O20 + 1.5 skirt (r_lobe + s_arm phi <= 11.5) at PA <= 42; with a 77 deg stage 2 on 28 / 50, kK 1.96 closes
  267, kK 2.3 closes 272, kK >= 2.7 kills the lobe at its base radius, two-slope 269: **26 poses sit between the law
  and the window.** Stage 2 is solved: the in-band RSSR reaches 77.2 (PA <= 42) and its metal costs 0.29 points.
  The in-band long-dyad report row (29.0 / 44.6 / 68.1, kK 2.82) reads bench 20.44 (fold 87, slide 13, 3 contacts
  10.77 mm), held 23.72 (fold 251 vs pick3's 263: +12; 9 contacts 40.86 mm, 29.3 of them overhead), env -> held 23.03:
  it gains fold poses and gives them back in overhead contact and knee slides.
- **The overhead cone (26 scapular-plane losses, plane -20..45, elev 90-165; 11 of the 20 overhead losses):**
  - 15 folded (th 7.7-22) sit behind TWO walls: the window's low wall |a1 - a2| + 5 = 24.67 AND hub 2's disc (clears
    4 of 15 at F2 62 mm, median need 71; held 21 of 46; F2 +4 mm takes 26 % of clip frames out of band, +6 mm 76 %).
    Measured dead for them: K in any layout (K sub-chain fold 32.8 vs th_lo 29.7), a2 re-placement (a2 60: 20.84 /
    24.17), J1 re-seats, folded-side lobes.
  - **Red team of round 11's lever (a), closed form (this planner; the lens confirms on the model in 10 min):** the
    planar two-pin knee (pins parallel to J3) closes exactly only with J1 and J2 on GH rays (J3's line is free;
    docs/concepts/skin-normal-3r-pin-knee.md line 312). Tilting J2 by b2 puts GH on a circle of radius d = F2 sin b2
    about J2 in member 2's frame; its component along u3, 2 d sin(a2) sin(dq2 / 2), is out of the knee's plane. At
    F2 62, a2 57.2, dq2 100-120 deg, R_tol 0.5 mm allows b2 <= ~0.3-0.4 deg. A real tilt needs a cuff slide along u3
    (1 passive translation, rail = travel + block, ~14.5 mm travel at b2 10 deg; +3 cx), and even then the 15 folded
    stay behind the kinematic low wall (a tilt only re-places a1 / a2, measured dead).
  - 9 knee slides (R_tol; plane -15..15, elev 90-165, external rotation 15-45): the knee runs to 151.92 of its
    [25.22, 154.78] window (held 153.16). The centred knee is the only held-out gain on file (22.97 vs 23.73, but 19.33
    on the bench). b3 (J3 tilt) makes the knee's in-plane drift; deleting it cost ~2.2 frozen points (kneeless).
  - 2 contacts at elev 165 (trimlug): 237 crank 9.01 + lug 8.35 mm, 264 lug 4.18 mm. Clearing 264 by trim needs the
    flank to stop at dK ~35 (the stroke wall). Lateral relief is the open direction: 1 mm toward K's axis gains
    0.9-1.0 mm; the crank tip's outer wall needs ~0.5 mm narrower, hub 2's housing wall a ~0.3 mm flat. A radial lift
    makes both deeper (T5 16.07).
- **Complexity (second objective):** nothing under the lead's 18.25 like-for-like survived round 11 (four-bar cx 14
  dead at 51.75 under strict B1). The drive is ~14-16 of a knuckle's points: stage-1 roller follower (R + body + joint =
  3), clock spring 3, the loops 4 each. groove-desmo proved a spring-free K at 18.25 but its two-walled slot needs the
  ROLL_R 2.5 roller >= ~2 mm off the crank / link-1a pole (path radius 1.03-1.84 toward the free side at K 0-7), and
  the horn PA then ends the stroke at 41.2 (lead 46.2, slipper 49.8).
- **Closed with measured reasons (do not rescreen):** a K drive with its crank or arm beside link 1b (coupler, 1540
  configs: skin up to 33 mm above link 1b's level; over the corridor the PA-legal stroke is 60-65); a K slaved
  everywhere under the strict reading (four-bar, 2520 configs); radial lifts of overhead metal; underside-only cuts for
  side-wall contacts; the dip below stop A (gamed); a spring-held spare 4R (1:1 fold for contact); stroke beyond the
  a1max window; stop B within 5.5 deg of the K dyad's stretch; re-placing the window; seat re-fits judged on the fit
  bench; per-part relaxations; twin K2; J3 twist; in-sample and env-fit polishes; hub-2 tilt with the planar knee
  (above).
- **Machinery (open, before the next claims):** (1) a pair-coverage probe: every member pair in relative motion has a
  per-pose check over its full swing, and the frozen copy carries every attribute those checks read (dogring's 75-point
  hole and the silently skipped RING-L2); (2) the verify template still bars against the round-3 champion
  (tools/workflows/exo-screen.js line 24: BASE 68.93 / BIG 75.94): verifiers judge against the lead 18.49 and its tie
  rule (paired pooled 90 % CI including 0 = tie); (3) the continuity flood (2-deg slerp, `connected()` in
  docs/concepts/models/stop-relay-rocker-3r.py) is a hard verifier step (the trimlug verifier skipped it). Until the lead
  lands (1)-(3) in the tools, every lens and verifier below does them by hand.
- **Farm:** [LEAD 13:56 UTC: STALE - the CLAUDE.md (7) budget is spent at balance $24.63 vs the $24.40 line; run LOCALLY, <= 2 niced processes, no new farm batches unless the user renews] RunPod ~$34; small batches on exo-cpu1, `tools/runpod_guard.py audit` before and after, workersMin 0. The
  local .cache bench is rebuilding: gates run on the farm first.

### Lenses

1. **The stretched wall through stage 1 (reach >= 0.77; suggested id: longdyad-inband-relief-knuckle-3r).** Target:
   frozen exact gap <= 15.5 (stretch 13.75), reach >= 0.77 at ib14 >= 0.88, <= 2 contact poses, held out <= 22.4.
   - **Start from inband-rssr-knuckle-3r's model** (switches eta / clay / zc / bl_c / bl_h; crank on link 1b's
     joggled ear, radial crank stud) on the 28 / 50 or 32 / 48 K dyad, a1max <= bk1 + bk2 - 5.5, stop A 37.55,
     a2 57.22 (verified seats).
   - **Attack the 26 law-vs-window poses (the measured binder): split the gain** so the rim lobe stays legal. Low lobe
     slope kK (<= 2.3, crest inside O20 + 1.5) and the RSSR's own ratio g rising toward the stretched end (progressive:
     phase the crank so dK/dphi grows near K 40-75 at PA <= 42), or a two-slope lobe with the steep part carried by
     the RSSR. Report law-only closure against the 298-300 window.
   - **Relieve the overhead parts laterally, never by a lift** (lesson 6): hub K / horn / rod at elev 150-165 toward
     K's axis in plan view; carry the trimlug cut (lug ends at the farthest flank contact + 1.5 mm wall).
   - **Free the knee in the same search** (lc, phib, b3, pin offsets; ang_min >= 25.22): the long-dyad row's slides
     went 10 -> 13.
   - **Gate A, <= 25 min, farm:** law-only plus exact one-level parking (docs/research/fold_ceiling/parking_k.py) with
     the real stage 1 + RSSR and the crank / rod / sockets / hub K sampled: >= 288 / 360 closed and cleared at +4 mm,
     parts in band >= 0.755.
   - **Search and select:** CMA on the jittered envelope bench (tools/env_bench.py, tools/inband_env_polish.py; never
     the held-out poses) on the 1 mm near-touch gap plus a K-open term (metal < 1 mm at dK > 20 counted twice);
     **pre-register the pick** on its env frozen wear before any Bench(110,360) or held-out number (the fast bench is
     blind to the stretched wall, lesson 7). Claim frozen exact Bench(110,360) and held out.
   - **Kill:** gate A < 282, or the pre-registered pick's held-out overhead contact depth > 2x the lead's (> 92 mm
     summed): report the binding element (lobe crest, lobe PA, RSSR PA, socket cone 25.5 / 30, the part) and stop.
   - **Red team:** the socket cone (25.5 deg used of ~30; a 25 deg short-neck link binds); r_h knife edge (+0.25 build);
     the K lag at the long stroke against th >= 5 held out; the full-grid flood (no branch change).
2. **The overhead cone, non-fold losses (reach, the other side of the window; suggested id: conecut-knee-knuckle-3r).**
   Target: >= +5 of the 11 non-fold cone losses (9 knee slides + 2 contacts) taken frozen on the lead's drive, 0 new
   losses elsewhere: gap <= 17.1, overhead >= 11/28, a stackable delta for lens 1.
   - **Step 0 (10 min, report even if it kills (a)):** confirm the b2 closure arithmetic on the lead's model (u3
     drift vs b2 over the taken q2 range). Build a b2 tilt only with a u3 cuff slide (1 passive translation, real
     miniature-guide envelope, rail = travel + block) and only if the exact per-part march shows it takes >= 4 folded
     poses through BOTH walls; otherwise drop it with the number.
   - **(b) Knee re-cut** aimed at the 9 slides: lc, phib, pin offsets and b3 jointly, ang_min >= 25.22 (no knee-margin
     relaxation), MR63ZZ-pair pins at their real envelope. Select on the envelope bench, claim held out; the centred
     knee (19.33 / 22.97) is the control to beat on both.
   - **(c) Lateral relief at elev 165:** the crank tip's outer wall (-0.5 mm width), hub 2's housing flat (0.3 mm), the
     lug band moved toward K's axis in plan view; read the distance gradient per sample first.
   - **Gate, <= 25 min, farm:** exact per-part march on the 26 cone poses plus every clip frame: >= +4 of the 11 cleared,
     knee inside its window, 0 new losses on the other 334 workspace poses.
   - **Report:** GH-offset liner share (3 / 5 mm, docs/alignment/remeasure/*_ghoffset.json harness) for any knee change,
     contact depth (T5), raised-arm workspace in-band, min th and m_sub margins.
   - **Kill:** fewer than +3 at the gate: report the part that binds each of the 11 and stop.
   - **Red team:** the knee at its window edges under a 3 mm GH-centre error; cuff twist at the knee pins.
3. **Spring-free, roller-free K drive (low complexity at the lead's reach; suggested id: desmo-slipper-knuckle-3r).**
   Target: complexity <= 17.25 recorded (13.25 like-for-like; lead 22.25 / 18.25) by tools/simplicity.py v2.2 with a
   full mechanism record, frozen exact <= 18.49 or a paired tie with it, reach >= 0.725, held out <= 23.45; 0 springs,
   0 passive translations, 0 sensed passives.
   - **Topology:** the lead with both stages made positive and both followers made noses. Stage 1: groove-desmo's hub-2
     groove (gate 0 passed: real PA 30.5, link 2 clear >= 1.22 mm) with a hardened nose instead of the roller (-1 R,
     -1 body, -1 joint, +1 sliding pair). Stage 2: the slipper nose (O2.37, r 1.18) in a two-walled slot in link 1a's
     boss. Delete the clock spring (-3) and with it M5. The law keeps the lead's dwell (K = 0 on stop A for
     th <= a1 + a2 - 5), so K at rest is the lead's state, not a K slaved everywhere (lesson 5 does not apply; report
     m_sub as the lead does).
   - **The measured bet:** the slot's outer wall undercuts where the follower path turns toward the free side with a
     radius below the follower's own (groove-desmo: path radius 1.03-1.84 at K 0-7 vs ROLL_R 2.5; knife edge below
     ROLL_R + 3.5). The nose's r 1.18 (O2: 1.0) needs ~1 mm less offset from the pole, so the horn-PA stroke cap
     should move from 41.2 toward 46-49.8. Map it first (drive-only pole map, beta x r_c x g x nose offset, groove-desmo's
     scratchpad method) with PA + friction <= 43 on BOTH walls at mu 0.087 / 0.12 / 0.15.
   - **Gate, <= 25 min, farm:** a cusp-free, knife-edge-free slot (wall radius >= 3.5 mm or concave) with dK_lim >= 46
     and law-only closure >= 272 / 360.
   - **Fallback (claimable on its own, report it either way):** stage-1 nose only, spring kept (cx 20.25 / 16.25
     like-for-like) if the slot gate fails.
   - **Kill:** dK_lim < 44 on every cusp-free cell: report the binding wall and stop.
   - **Red team:** jam in the slot (both walls, reversal at the dwell exit); slot clearance as K slop against the
     held-out margin 5.006 (price it; the +0.75 deg K lead is in the build); wire-EDM of a two-walled conjugate slot
     (4-axis, ruling parallelism <= 5 um); wear of a nose in a groove at 1e6 cycles.

**Every lens:**
- takes a new id and never re-screens an id in the exclude list below;
- writes its pair-coverage table into the row (every member pair in relative motion, the check that covers it, over
  which swing, and that the frozen copy carries the attributes) before claiming;
- writes its motion preview (docs/concepts/viz/concepts/<id>.js, `node docs/concepts/viz/test.mjs <id>`,
  `node docs/concepts/viz/thumbs.mjs`) before the row is called screened;
- reports plain gap fast and frozen exact, held out, flood full + knn, overhead x/28, per-part and workspace in-band,
  min th margin, m_sub (rest / moved), contact depth (T5), v_contact and tools/simplicity.py v2.2 like-for-like with the
  lead; contact stays metal < 1 mm, near-touch report-only;
- writes the per-pose dump (`tools/alignment_paired.py dump`, bench and held out, +-0.05) and a paired comparison with
  slipper-nose-knuckle-3r;
- searches on the envelope bench, fits the shape on Bench(60,160), pre-registers its pick, claims frozen and held out;
- runs `tools/alignment_audit.py audit <id> --ref slipper-nose-knuckle-3r` before its verifier; the verifier judges
  against 18.49 with the tie rule and runs the continuity flood;
- has a 75-min modelling box; on a kill it reports the measured reason and stops.

### Carried over (catalogue, ideated, never screened)

None. The round-4 picks stay closed (deltoid-crest-j3-3r, crest-knee-3r: the crest seat; slotted-eccentric-pin-knee-3r:
its sibling refuted at 115.21); the other 25 ideated entries are families dead in rounds 1-2. The O20-only hub rule
keeps rolling-cone-3r closed.

### Elsewhere, not to be duplicated

- slipper-nose-knuckle-3r: its env polish (docs/research/slipper_env_polish/, pick1 claim) and the gen-7 L1 / user CAD
  (pipeline/full-exo/designs/l1_slipper-nose/); trimlug-k165-knuckle-3r's CAD is that CAD plus the lug cut.
- inband-rssr-knuckle-3r: polished pick3 (CAD config r_h 15.9 with the O9 head); lens 1 builds on its model under a new
  id and does not touch its row.
- roller-longdyad-knuckle-3r: gen-6 user-style CAD.

### Needs the user's say (unchanged)

- **B1:** does m_sub at K's rest, or the coupled reading, decide the fold rule? It decides G4 for the whole family;
  no lens here rests on the lenient reading.

## Round 12 results (2026-10-17 ~13:40-18:05 UTC, track main, closer)

All numbers are frozen exact on Bench(110,360), fitted on Bench(60,160), and re-measured by an independent verifier.
Ledger verdicts were re-read with `tools/alignment_ledger.py get <id>` at 17:59 UTC, just before naming the winner:
conecut-knee and desmo-slipper exit 0 (WATCH); spiral-lobe and desmo-vrocker exit 2 (no entry: dead, not audited).
Complexity is tools/simplicity.py v2.2. Every row has 3 active joints and 0 passive translations. The farm sat at its
budget line all round, so every claim, verification and audit ran locally (<= 2 niced processes).

| design (lens) | verified gap (score) | held out | reach / overhead | cx | ledger | outcome |
|---|---|---|---|---|---|---|
| **conecut-knee-knuckle-3r** (2: overhead cone; re-centred knee + J3 dowel stop) | **18.28 (93.35)** | **22.38** | 0.728 (262/360) / 8 of 28 | 18.5 | **watch** (exit 0; 10 upheld, 1 refuted) | **winner**; a measured TIE with the lead, not a lead change |
| desmo-slipper-knuckle-3r (3: spring-free, roller-free K drive) | 18.95 (93.11); claim 18.63 refuted on its own slop gate | 23.90 | 0.725 (261/360) / 8 of 28 | **15.75** | watch (exit 0; 9 upheld, 0 refuted) | verified, +0.46 behind the lead (in-band only); lowest verified complexity at the lead's reach |
| spiral-lobe-longdyad-knuckle-3r (1: stretched wall, gain split) | ghost 17.86 (8 contacts); with its own drive metal 38.56 (verifier) | - | 0.747 ghost; 0.692 / 4 of 28 with metal | 24.5 | no entry (dead) | dead at gate 0; death upheld and found worse |
| desmo-vrocker-longdyad-knuckle-3r (pick 4: lens 3 x lens 1) | ghost 17.23 (6 contacts); <= 4-contact cells 18.85-18.87 | - | 0.747 ghost / 8 of 28 | 16.0 | no entry (dead) | dead at gate 3 (and the gate-4 bound); death upheld |
| slipper-nose-knuckle-3r (lead, reference) | 18.49 (93.28) | 23.45 | 0.725 (261/360) / 8 of 28 | 18.25 | watch | stays the verified lead |

**Winner: conecut-knee-knuckle-3r, v_gap 18.28 (score 93.35), held out 22.38, complexity 18.5, ledger WATCH (exit 0,
final skeptic verdict 2026-10-17T17:57:13Z). It does NOT replace the verified lead 18.49 (slipper-nose-knuckle-3r):
it is 0.21 lower, but by the round's own tie rule (paired pooled 90 % CI including 0 = tie) it is a measured tie.**
- Paired against the lead (per-pose dumps on file): bench -0.20, CI90 [-1.05, +0.80], P 0.60; held -1.08,
  CI90 [-1.86, +0.06], P 0.935; pooled -0.82, CI90 [-1.46, +0.09], P 0.918.
- The bench edge is not a better exo. Weighted at the lead's E-strap sample count (104 of 164 points), the bench reads
  18.67, 0.18 BEHIND the lead. The only new bench pose (203) has metal 0.26 mm off the skin (cmin) and is worth
  0.55 points, more than the whole edge. The held-out edge survives at equal strap (22.90 vs 23.45, 11 held poses at
  0.76-3.68 mm metal). The skeptic refuted the one reason against it (NEW-stop-relabel: the lead's knee window removes
  the same held poses, so like for like the stop's held edge is 0).
- Tie break against the round's other verified design: complexity would favour desmo-slipper (15.75 vs 18.5), but the
  two are not tied. Closer's paired comparison (`docs/alignment/remeasure/conecut-knee-knuckle-3r_vs_desmo-slipper-knuckle-3r_paired.json`):
  bench -0.66, CI90 [-1.49, +0.74]; held -1.53, CI90 [-2.29, -0.19]; pooled -1.28, CI90 [-1.90, -0.13], P 0.967.
  Conecut is measurably ahead, so the tie rules decide nothing.
- What it delivers that holds: the knee never binds (window margin 11.4 / 13.2 mm vs the lead's 0.33; 0 held knee
  slides vs 32), the knee link carries 12 N per N.m vs 31.6 (two-force member, d_perp = lE sin(knee angle)), and the
  J3 end is a buildable 2 mm 440C dowel at r 7.5 in hub 3's lower plate (250.7-deg groove, 109-deg web, 133 N per N.m,
  shear safety factor 2.6 at 10 N.m) acting on J3's own angle (axis residual <= 0.015 deg).
- **Generation CAD:** the winner is the lead's chain and drive with a new knee and one dowel, so its generation CAD is
  the gen-7 slipper-nose CAD (`pipeline/full-exo/designs/l1_slipper-nose/`) with the knee re-cut (lE 97.14, lc 24.35,
  phiE 0.75, phib -91.80, ang_min 25.22, MR63ZZ pairs at stk 6.0) and the dowel stop [-111.90, 122.74] on q3'. On that
  CAD, measure the new knee's cuff twist and R17 (M5 below), never measured for this row.
- **Lead bookkeeping (not the closer's to write):** the dashboard headline currently crowns this tie (NEW-tie-headline:
  morphs.json carries it at 18.28 with no ruling). The lead writes `leader_ruling: "tie: slipper-nose-knuckle-3r |
  ledger 2026-10-17T17:57:13Z | ..."` in the row. Also: desmo-slipper's best_params still holds the refuted claim
  placement (a_s 9.25 / psi 154); the verified one (a_s 9.5 / psi 150) lives only in verification.verified_config.
- Passed over as gamed: none. No round-12 design is gamed.

**Alignment (every watch reason of the round's designs, as upheld by the skeptics).**
- **conecut-knee-knuckle-3r: WATCH, 10 upheld, 1 refuted** (NEW-stop-relabel, above).
  - *dominance* (report only, A1 retired): +0.21 plain, but -1.82 at the 2 mm near-touch.
  - *reporting*: the row's verdict text still reads as a self-measured screen; the dashboard sweep best 12.5 reads as
    score 95.45, 5.78 under the verified 18.28.
  - *T1*: the bench edge rests on pose 203 (ws 0, 90, 45) at 0.26 mm (cmin; 0.72 sampled), a -0.03 mm contact in the
    no-stop control, worth 0.55 points. Taken poses under 1 / 2 / 3 mm: 3 / 33 / 105 (lead 3 / 30 / 100). The 11 new
    held poses sit at 0.76-3.68 mm, 6 under 2 mm. Near-touch vs the lead: bench 1 mm 19.92 / 20.12, 2 mm 34.84 / 33.02,
    3 mm 86.16 / 83.15; held 25.23 / 26.54, 37.10 / 36.95, 83.12 / 79.25.
  - *NEW-strap-dilution* (proposed catalogue entry S6): E strap 67.8 -> 97.1 mm takes it from 104 to 164 samples per
    pose at 97.9 % in band; point-weighted in-band 0.8955 -> 0.9012 while the chain's own metal gets worse (chain-only
    0.859 vs 0.869, held 0.857; hub 2 0.912 vs 0.953; crank 0.801 vs 0.818). Equal strap: bench 18.67, held 22.90.
  - *T5*: bench 4 contacts / 20.24 mm, deepest 8.93 at (15, 165, -60) (lead 2 / 14.75; x3.25 / +14.01 mm against
    sidecar-longdyad's 6.23). New bench contacts 205 (hub 2, -4.28 mm, a lead knee slide) and 316 (link 2, -1.23).
    Held: 14 / 60.97 mm, deepest 9.86 at (45, 165, -30), 9 deeper than 3 mm (lead 10 / 46.12); new held contacts 835
    (90, 15, -150) -3.55 and 978 (120, 15, -165) -1.33 on arm-pad and knee-link metal, poses the lead takes at
    0.81 / 0.62 mm.
  - *NEW-tie-headline*: above (lead ruling needed).
  - *M5* (carried from the lead): the K clock spring, law and drive are the lead's (dK [-0.796, 0] rad, a1e
    [37.55, 54.26] deg); the lead's R17 forward bound fails the unrounded 5.0-deg gate by 0.0008 deg at mu 0.15. The
    new knee runs 59-107 deg (lead 86-152); its cuff twist and R17 are unmeasured (no CAD, no dynamics run).
  - *G4* (carried): with K at rest, the lead's m_sub < 5 deg on 106 of 204 rest poses and < 1 on 50; not re-measured.
  - *T3*: the stop is on J3's own angle (clean), but the held th margin is 5.006, 0.006 above the line, on the lead's K
    law; a +-0.3 deg K-phase build error crosses it.
  - *NEW-ws-inband* (better than the lead): elev 90-140 taken ws poses 83.2 % in band, 16.8 % above 14 mm (p95
    20.04, max 30.74 mm) vs the lead's 80.0 / 19.9 %; held 84.8 / 14.9 % (max 31.46). Overhead 8/28 bench, 18/71 held.
  - Skeptic's missed item: the upper stop cuts 5 held would-be contacts, not 3, and any stop-relabel test (T6) must be
    applied to both designs.
- **desmo-slipper-knuckle-3r: WATCH, 9 upheld, 0 refuted.**
  - *reporting* and *R2*: the dashboard sweep best 12.79 reads as score 95.35 (above the golden 95), 6.16 under the
    verified 18.95. It is a fast number with dense outer-wall sampling (-0.31 of in-band padding) at a_s 9.21 / psi
    152.9, between two placements the dense scan refuted.
  - *NEW-friction-cliff*: at the verified placement the stage-1 pin's cap-side PA is 35.25 deg at the dwell exit,
    crossed by every K-open pose (188 of 371 taken). It holds to mu 0.135 (dK_lim 44.5, fast 14.84) and jams from mu
    0.14 (dK_lim 0, fast 86.71, reach 0.344). The lead's rolling stage 1 keeps dK_lim 43.0 / fast 14.88 at mu 0.15.
  - *NEW-silent-check*: the declared groove centreline radius gate (RC_MIN 1.5 mm) is computed and never enforced:
    0.37 mm at the claim placement (below the 0.75 mm pin radius: no inner wall), 0.99-1.0 mm over the onset corner at
    the verified one, a 0.23 mm ridge loaded at every dwell exit. Enforced as written, K could not leave the dwell.
  - *NEW-refuted-best-params*: the row's best_params, headline 13.19 / 0.775 and "paired TIE" verdict are the
    refuted placement; tools that read best_params build the placement that fails.
  - *T3*: K play in series ~0.36 deg nominal (groove 0.24 + slot 0.115), 0.48 at worst tolerance, ~0.1 deg of th:
    the held minimum 5.006 falls under 5 (estimate; the models carry no slop state).
  - *M3*: the 9.5 mm short arm and O1.5 pin enter hub 2's O20 footprint in link 1b's J2-seat layer; no check covers
    them against the hub-2 stack (l2_check excludes r < 11.5). A ~5 x 4 x 1.5 mm relief pocket is assumed, not shown.
  - *T5* (the lead's contacts, unchanged): bench 9.01 + 5.72 = 14.72 mm (x2.36 the 6.23 reference); held 10 contacts,
    46.14 mm, deepest 9.05 at (30, 165, -45).
  - *NEW-ws-inband* (carried): elev 90-140 in-band 0.8009, 19.83 % above 14 mm (p95 19.98 mm), lead 0.8004.
  - Skeptic's missed item: the model reads the stage-1 PA gate on the LINEAR K law, not the blended groove it builds.
    On the built groove the cap-side angle is 89 deg at the dwell exit and above the claim-mu gate up to K 8.1 (pin side
    peaks 30.9). Either the mu 0.136 cliff is an artefact, or the design already fails its own gate at mu 0.087. Nobody
    has shown the dwell exit transmits under friction.
  - Wearer: overhead 8/28 bench, 18/71 held (the lead's); raised arm 46/113 (held 114/300); taken poses under 2 mm
    30/371 (9 overhead), under 1 mm 3; held 67/852 and 14.
- **spiral-lobe-longdyad / desmo-vrocker-longdyad:** no ledger entry (dead). Verifier notes, not ledger reasons:
  spiral's convergence gate passes on law-only moves (+0.36 / 0.00 / 0.37) and says little; its death estimate
  (>= 18.5 with metal) was unmeasured and is now measured at 38.56 (40 contacts: horn 29, rod 18, hub 2 / ear 4; depth
  sum 88.1, max 8.3 mm); a perfectly re-placed drive would land ~18.15 with >= 8 contacts. desmo-vrocker's gate 1
  (0 conjugate pairs as specified) was not independently re-derived; gate 3 and the gate-4 bound each kill it alone.
  Both verifiers flagged the template's refutation bar (68.93 on Bench(60,160)) as stale and judged against the lead.

**Lessons (measured).**
1. **The knuckle family's reach cap is a SEAT cap, measured from both sides.** Best chain ghost on file (no drive
   metal): 17.23 (32/48, kK 2.4, onset 14, cap 56; 269 taken, 6 contacts). 34/48: 17.86 (8). Every cell with <= 4
   contacts reads 18.85-19.71; the ghost never takes more than 270. The same five contacts (117, 127, 129, 139 at plane
   -90..-60 / elev 45-60 / axial 105-135, and 316 at 60 / 150 / -105; link 2 to -7.7 mm, hub 2's rim to -3.8) appear in
   every cell at onset 12-14, whatever the gain (2.3-2.8), cap (56-64), dyad (30/49, 32/48, 34/48) or J3 stop, and
   two of them DEEPEN as K falls: link 2 sits low over the posterior deltoid at pick3's seats. Correction to the lead
   directive: 17.86 is not the family ceiling (17.23 is), but no cell meets <= 17.5 with <= 4 contacts.
2. **A slaved K makes stop B a th cut.** K = f(th), so a stop cannot separate chain contacts (K 29.5-64.8) from takes
   (the same K range). The least-opening (track) law sheds all 12 chain contacts but folds 14-15 stretched poses at
   th 110-115; why they still fold is open.
3. **Real drive metal on the long dyad is not a 0.3-point tax.** spiral-lobe with pick3's drive placement: 17.86 ghost
   -> 38.56 (40 contacts). Re-placing pick3's drive on its own dyad cut 7.57 -> 0.29 points; nobody has re-placed one
   on 34/48.
4. **A J3 stop never takes a pose; it relabels.** The dowel is worth 1.10 against the no-stop control (19.38), but
   every stopped bench pose also clashes the E strap with link 2 and puts metal 0.95-14.5 mm into the skin. Held out
   the lead's knee window removes the same poses as "slide": relabel comparisons must be symmetric.
5. **In-band is sample-weighted, so a longer member dilutes.** conecut's E strap (104 -> 164 samples) is worth 0.39
   bench points by itself (18.28 vs 18.67 at equal strap); desmo's dense outer wall read 0.31 lower fast. Every claim
   that adds or lengthens in-band metal states its sampling density and is compared at equal sample counts (S6).
6. **Size the knee on held-out low-elevation extreme rotation.** lE 101 / lc 31 takes 20 held contacts (9 arm pad /
   knee link) at elev 15, axial -135..-165 (held-out poses 764 / 835 / 907 / 978 / 1047), which the fast bench never
   samples; [lead 2026-10-17 20:25: STRUCK "those poses belong in the envelope search bench" - they are HELD-OUT poses;
   draw fresh low-elevation extreme-rotation poses for the envelope bench instead (tools/env_bench.py, >= 2 deg from
   every held-out pose); alignment skeptic 20:15, P2]. A long knee link needs MR63ZZ stk 6.0 (stk 4.85: knee-vs-E clash
   on 329 poses).
7. **A desmodromic groove has a determinacy failure no PA or stroke gate catches.** Crank-free K play is
   g c / |v_F . e_r|; the follower needs a radial velocity component of ~40 deg in the dwell (psi 148-156 here; the
   spec's psi 184 gave 1.12 deg in the dwell and 2.2-3.7 at the onset corner). A 9-point slop scan missed 0.273 deg at
   K 42 that a 223-point scan found; the groove radius gate was declared and never enforced; the PA gate was read on the
   linear law, not the built groove. Passing the dense gate cost +0.36, all in-band. The cam sense is exactly -1/kK.
8. **Deleting K's clock spring changes no bench number** (the cap is never skin-facing): its value is complexity
   (3 points) and the M5 risk - but the sliding stage 1 that replaces the roller jams at mu 0.14, where the rolling
   stage 1 holds at 0.15. Complexity bought by turning a rolling pair into a sliding pair must carry a mu column.
9. **Reach did not move for the third round.** The best verified take count is 262 (conecut: +1 pose at 0.26 mm).
10. **Process:** both machinery items the round-12 plan put before the claims are still by hand. The verify template
    still bars against 68.93 / 75.94 (every verifier judged against the lead instead); pair coverage failed again
    (desmo's arm and pin vs the hub-2 stack, M3; after dogring's arm vs link 1b in round 11). The models carry no slop
    state, so the fold margin under K play is estimated, not measured. A row's best_params kept a refuted placement.

**Next focus (round 13).** The score has not reached 95: the best verified gap is 18.28 (conecut, a tie with the
lead's 18.49); 95 needs 13.75, i.e. +18 workspace poses at the lead's in-band and contact. Under the lead directive
(16:20 UTC) the main track spends at most ONE lens in the knuckle family, on complexity or overhead contact depth, and
does not duplicate the jump track (axial J3 / arm-track, scapular relays).
- **The one knuckle lens: complexity, by stacking the spring-free drive on the conecut knee** (suggested id
  desmo-conecut-knuckle-3r; expected cx 16.0 = desmo 15.75 + the dowel). Measured reason: desmo's +0.46 against the
  lead is in-band only (ring sector outside O20 0.33 fast, dense-gate placement 0.36) on identical takes and contacts,
  while conecut's knee is measurably ahead of desmo (pooled -1.28, CI90 [-1.90, -0.13]) and keeps 0.55 held out at
  equal strap. Target: a paired pooled tie with the lead (CI90 includes 0) at cx <= 16.0, held out <= 23.45.
  Gates enforced IN the model, not reported: dense crank-free slop <= 0.25 deg (>= 200 points both ways over the full
  taken K range); groove centreline radius gate enforced (or retired with a measured reason and the ridge stress on
  the part); stage-1 PA read on the BUILT (blended) groove; dK_lim >= 44 at mu 0.15 (the lead's roller holds 43.0
  there); the short arm's relief pocket in link 1b's J2 boss modelled and checked against the hub-2 stack; K play
  carried into th per pose (both signs) held out; best_params = the verified placement. Fallback (claim either way):
  keep a stage-1 roller in a two-walled groove and delete only the spring. Kill: no stage-1 placement passes every gate
  with dK_lim >= 44 at mu 0.15 - report the binding gate and stop.
- **Reach (for the lead's ruling, not a main-track lens under the directive):** the only reach lever the round's data
  names for this family is the seats. The 5-pose binder is invariant to dyad, gain, cap, onset, drive and J3 stop, and
  two of its contacts deepen as K falls, so only a J2 seat or K axis that moves hub 2 and link 2 ALONG the posterior
  deltoid could move it. A 30-45 min chain-ghost gate (frozen exact, judged on the envelope bench, never the fit
  bench): <= 17.5 with <= 4 contacts and >= 274 takes, or the family is closed for reach with that number.
- **Machinery before the next claim** (open since the round-12 plan, measured again this round): the verify template's
  bar set to the lead 18.49 and the pooled-CI tie rule; a pair-coverage probe in the toolkit; the continuity flood as a
  hard verifier step; slop state in the models (K play into the th margin); a mu column for every sliding pair; equal-
  sample in-band comparisons (S6); best_params = the verified config.
- **Do not rescreen:** K law / gain / onset / stop B / cap / dyad cells on pick3's seats (26 cells, spiral and
  v-rocker); a J3 stop as a reach lever; stacked conjugate lobes without base-ring relief; the desmo spec placement
  (psi 184); long knee links at stk 4.85; a 9-point slop scan.

### Needs the user's say (unchanged)

- **B1:** does m_sub at K's rest, or the coupled reading, decide the fold rule? It still decides G4 for the whole
  family, conecut and desmo-slipper included.

## LEAD DIRECTIVE (2026-10-17 ~16:20 UTC, after the user: "I didn't see any progress overnight, please keep pushing, I hate stagnation")

- The slaved-knuckle 3R family's ceiling is MEASURED: the long-dyad ghost (ideal drive, no drive metal) reads 17.86 at
  best (spiral-lobe-longdyad gate 0, 15:47; with <= 4 contacts <= 260 taken = 19.4-19.7). The binder is hub 2 / link 2
  in the posterior deltoid at K 29-65. Score 95 (gap 13.75) is not inside the family at these seats.
- A second loop runs on **track jump** (workflow wf_b950a9cb-03e, rounds 101-103, written here as "Round J1-J3"):
  new morphology classes that remove the binder, each gated by a ghost bound before any hardware modelling.
- **Main track, round 13 onward:** spend at most ONE lens inside the knuckle family (complexity or overhead contact
  depth, not reach), and do not duplicate the jump track's lenses - read its plan here first.

## Round J1 plan (round 101, track jump; 2026-10-17 ~16:25 UTC, lead verified gap 18.49)

### State

- **Lead (best verified, not gamed):** slipper-nose-knuckle-3r **18.49** (score 93.28) frozen exact Bench(110,360),
  held out 23.45, reach 0.725 (261/360), overhead 8/28, ib14 0.8955, 2 contact poses (T5 9.01 + 5.74 mm), cx 22.25
  (18.25 like-for-like). Ledger WATCH: M5 (clock spring force-closes a sliding nose), G4 (m_sub < 5 at K rest on 106 of
  204 poses; B1 is the user's), T5 (contact depth unscored), held-out th margin 5.006 vs a predicted 0.42-0.53 deg K
  lag, NEW-ws-inband (elev 90-140 in-band 0.800), reporting (sweep best 13.0 shown as 95.27). Ties / same family:
  trimlug-k165 18.51, inband-rssr pick3 18.33 (ruled a tie), roller-longdyad 18.67, sidecar-longdyad 18.91.
  4-active (a sensed joint is a joint): minarc pick1 18.40, skinnormal-shortk-4r 18.58 (dead: 1:1 fold-for-contact).
  Gamed: dipped-law-groove (fold margin 0.184), seed-offset-3r-slides. Do not buy points the way the watch reasons do
  (unscored depth, a margin read in a different angle, a free per-pose policy without the continuity flood).
- **The family is capped (measured):** the long-dyad ghost with an ideal drive and no drive metal reads 17.86 at best
  (spiral-lobe gate 0, 269 taken / 8 contacts; every <= 4-contact cell <= 260 taken = 19.4-19.7). Binder: hub 2 /
  link 2 into the posterior deltoid (to -15.3 mm) at K 29-65, clusters plane -90..-60 / elev 45-60 / axial +105..+135
  and the overhead IR fan plane 60-120 / elev 135-165 / axial -105..-90. 95 = gap 13.75 = +18 workspace poses at the
  lead's in-band.
- **Why the stretched wall exists (fold_ceiling.md):** 64 of the 73 stretched bench losses (held 211) are internal
  rotation >= 90 across the body: axial rotation swings the humerus-fixed J3 away from J1, so th = angle(J1, J3) depends
  on axial rotation. The folded 15 (th 7.7-22) are scapular-plane overhead, behind hub 2's disc (4 of 15 clear).
- **New planner measurement (Bench(110,360), 360 ws poses, kit frames, 1 min):** with J3 COAXIAL with the humerus,
  th no longer depends on axial rotation. Over J1 seats bvec(az -90..180, el 0..90) the narrowest th span is
  **95.5 deg at bvec(30, 70) (acromion top): th 78.1-173.6** (95 %: 81.5-171.5); bvec(0, 60) 75.2-174.5; bvec(20, 60)
  77.6-175.5. So a1 + a2 = 180 (window [|a1 - a2| + 5, 175]) holds **every** workspace pose kinematically at the 5 deg
  margin for |a1 - a2| <= 73, with 1.4 deg to spare at the anti-pole (the arm near -u1: hanging / adducted, a
  near-gimbal-lock). A J3 12 deg off the arm axis: span 95.5 (bvec(0, 60)); 25 deg: 89.8 (bvec(-40, 50)); 40 deg: 85.8
  (bvec(-40, 30)). The kinematic room is not the problem anywhere (FINDINGS: a >= 80-deg window holds 0.99 at allowed
  seats); every class so far died on WHERE hub 2 must sit.
- **Classes tried and dead, with the reason (do not rescreen as is):** long-arc / fold-free 3R (fold-sph3r 44.72 fast:
  hub 2 0 % in band at F 145-154; raglan-routed 42.72: hub 2 F 128); rings at the hubs (annular-ring 77.99: hub 2 at
  161 mm); 2R pointer + C-slide twist (pointer-cslide 69.84, reach 0.50: twist travel 165 deg needed vs a 98-deg window;
  a band fixed in the pointing frame has only a 150-180 deg torso-free sector at s 120-160, chest / axilla / head block
  the rest in 25-60 % of poses; shoe 27-31 mm off the arm); rod-sleeve twist near the deltoid (offset-pointer-slip-sleeve
  76.42: the rod clamp sinks 0.27 mm per mm into the deltoid); arc slides / rails (j2-arc-sector 66.3, short-a2-arc-slide
  55.3, trombone-arc 88.29, rail-elbow 64.7, scapular-race 78.54); spare joint on the deltoid (arm-parked-knee-4r 26.71:
  hub 4 0.51 in band); stop-switched J1 relay (stop-relay-rocker 50.36: relay entry at its own fold); redundant 4R
  spring-centred (park4 lens, self-measured 22.36 at ib 0.864); K as the 4th joint (minarc 18.40, skinnormal-shortk-4r
  18.58: 1:1 fold for contact); spherical parallel / RUS trusses (seed-spm 193, foldfree-rus / coaxial-rus 275).
- **Levers that look open:** (1) remove th's axial dependence (J3 on the humerus axis, a real thin-section ring or a
  GH-aimed rod-sleeve far down the arm), never measured as a 3-joint ring at the distal arm; (2) a base-side spare on
  bony scapula skin (acromion / spine: 2-5 mm skin spread) that walks J1 between the two allowed seat regions so the
  stretched chain lies over the acromion and the deltoid cap (a sphere about GH within 4.7 mm) instead of the
  posterior deltoid. Per-pose-free J1 rocker, kinematic: beta 20 0.77-0.81, beta 30 0.84-0.88, overhead 0.68-0.82.
- **Compute:** farm CLOSED (CLAUDE.md (7)); local only, niced, <= 2 processes per agent, OMP_NUM_THREADS=1. The local
  Bench(110,360) fast cache is missing (the exact path runs; build it with `concept_bench --build 110 360` once, niced,
  if a lens needs many frozen wears).

### Lenses

1. **Humerus-axial J3 (reach AND low complexity, 3 joints; suggested id axial-ring-gimbal-3r).** A 2R on O20 hubs
   (J1 acromion top / back, bvec(30, 70) or bvec(0, 60) as seeds, a1 + a2 = 180, |a1 - a2| <= 73) whose third joint is
   coaxial (cell R) or near-coaxial (cell S) with the humerus. Cell R: a closed thin-section ring bearing round the
   distal upper arm at s 200-260 where the skin radius is 40-50 mm (catalogue part, e.g. Kaydon Reali-Slim KA040AR0:
   bore 101.6, OD 111.1, width 4.76 mm, ~45 g; sample its real section as metal all the way round). Cell S: the
   catalogue's cuff-sleeve-3r, an O5 rod in an MR85-pair sleeve at s ~230 whose axis aims at GH (~12 deg off the arm
   axis; the sleeve's axial float is 1 passive translation). Link 2 is a spar fixed in the pointing frame down the
   lateral arm. Hypothesis: the IR-across-body stretched wall disappears by construction (th span 78-174 for every
   axial angle); the open question is proximity: the ring's medial arc vs chest / waist in adducted, across-body and
   behind-back poses, the spar over a non-round arm (skin radius 38-73 mm about the humeral axis at s 90-120), hub 2 on
   a GH ray >= 54 deg from both J1 and the arm. Gate 0 (30-45 min): ghost fit on Bench(60,160) fast, frozen exact
   Bench(110,360), with hubs 1-2 O20 at their stack, link 1 and the spar as 3 mm bent bars at real height, the ring or
   sleeve at its real envelope, the cuff's one slide (or a stated liner share); per-pose table of every loss by cause
   (anti-pole margin, ring vs torso, spar, hub 2). Bar: reach >= 0.80 or gap <= 15 with <= 4 contact poses; > 17.5
   dies with its number. Report overhead / 28, the min th margin over taken poses (5 deg, read in th), the anti-pole
   J1 / J2 rates, complexity (tools/simplicity.py; expected ~0-3: 3 bearings, no spring, lobe or knee). Red team: the
   near-gimbal-lock at th 173.6 (rates ~1/sin(margin)), donning (the hand through a 101.6 bore), the ring under arm
   flexion bulge, continuity flood (no branch change across the anti-pole).
2. **Scapular spare that routes the stretched chain over the acromion (reach, 4 joints; suggested id
   acromion-relay-4r).** A redundant non-orthogonal spherical 4R (Keemink 2018, TNSRE 26(4)): J0 on bony scapula skin
   (spine / acromion, O20) carries a PLAIN 3R (pin chain, no knuckle, no lobe) so J1 walks between the back-of-shoulder
   and acromion-top seats; the self-motion is held by a centring spring and two dowel-in-slot stops on J0's own angle.
   4 DOF: compare like-for-like with minarc pick1 18.40 / skinnormal-shortk-4r 18.58 and state that the user prefers
   3. Distinct from the dead 4Rs: the spare sits on bone, not on the deltoid (arm-parked hub 4 0.51), it is not a
   knuckle in link 1 (the 1:1 fold-for-contact), and it is free between stops, not stop-switched (stop-relay). Gate 0:
   per-pose-free J0 within its travel (upper bound) then the spring-centred policy, both with the continuity flood
   (2-deg slerp, no spare jump > 10 deg, no branch change; report static and connected), ghost metal = 4 O20 hubs +
   links at real height; per-pose: where hub 2 / link 2 sit on the 73 stretched and 15 folded losses of the lead. Same
   bar (reach >= 0.80 or gap <= 15, <= 4 contacts; dies > 17.5); the park4 lens's 22.36 is the number to beat by >= 5.
   Red team: the spring's preload vs the arm's own torque at the stops (feel), the J0-J1 sub-chain fold, the base on
   the scapula handler (J1 seat rule: back / acromion top only).

### Carried (ideated, never screened)

- armband-pointer and cuff-sleeve-3r (lens 1's cells R and S), acromion-pointer-arm-ctrack (the user's own 2-hub
  gimbal + an arm-skin axial track; lens 1's fallback if the ring stands off a non-round arm).
- Round-4 picks passed over with reason: deltoid-crest-j3-3r (seeds 26.35 fast / 35.90 frozen on O15 hubs, now O20
  only), crest-knee-3r and slotted-eccentric-pin-knee-3r (pin-knee family, fold-capped at verified reach 0.606; the
  eccentric's parent refuted at 115.21): none can reach the 17.5 ghost bar.

### Elsewhere, not to be duplicated

- Main track round 12: desmo-slipper-knuckle-3r (modelling), conecut-knee-knuckle-3r (CMA running),
  desmo-vrocker-longdyad-knuckle-3r (round-12 pick 4); slipper-nose-knuckle-3r / trimlug-k165 (gen-7 CAD fix pass).

## Round 13 plan (2026-10-17 ~18:10 UTC, track main, lead verified gap 18.49)

Planner's read of the files at 18:05-18:10 UTC. Ledger exits re-read: slipper-nose, conecut-knee and desmo-slipper
exit 0 (WATCH); gamed: dipped-law-groove-knuckle-3r (fold margin 0.184), seed-offset-3r-slides. Under the lead directive
(16:20 UTC) this round spends ONE lens in the knuckle family (complexity) and one time-boxed reach gate that the round-12
closer sent to the lead; everything that moves the base or replaces J3 belongs to the jump track.

### State

- **Verified lead (reference for the audit): slipper-nose-knuckle-3r 18.49** (score 93.28), held out 23.45, reach 0.725
  (261/360), overhead 8/28 (held 18/71), ib14 0.8955, 2 contact poses (T5 9.01 + 5.74 mm), cx 18.25. Bench losses: fold
  88, knee slide 9, contact 2; held: fold 260, slide 32, contact 10. Watch: T5 depth unscored; M5 (clock spring
  force-closes the sliding nose; R17 forward bound misses the unrounded 5.0 by 0.0008 deg at mu 0.15); G4 (m_sub < 5 at
  K rest on 106/204 poses, B1 is the user's call); held th margin 5.006; NEW-ws-inband (elev 90-140 in-band 0.800,
  19.9 % above 14 mm); reporting (sweep 13.0 shown as 95.27).
- **Lowest verified number, ruled a TIE (8e50534, 18:05): conecut-knee-knuckle-3r 18.28** (93.35), held 22.38, cx 18.5,
  262/360. Paired vs lead pooled -0.82, CI90 [-1.46, +0.09]. The edge is E-strap in-band dilution (equal strap 18.67 /
  held 22.90) plus pose 203 at 0.26 mm (worth 0.55); contact deeper (bench 4 / 20.24 mm, held 14 / 60.97 vs 10 /
  46.12); held th margin 5.006 (a +-0.3 deg K phase crosses it). What holds: the knee never binds (window margin 11.4 /
  13.2 mm vs 0.33; 0 held slides vs 32), knee link 12 N per N.m vs 31.6, J3 2 mm 440C dowel on its own angle.
- **desmo-slipper-knuckle-3r 18.95** (93.11), held 23.90, **cx 15.75** (lowest at the lead's reach). +0.46 vs lead, all
  in-band (ring sector outside O20 0.33 fast, dense-gate placement 0.36), takes and contacts identical. Watch: friction
  cliff (sliding stage 1 holds to mu 0.135, dK_lim 44.5; jams at 0.14, fast 86.71; the lead's roller holds 43.0 at
  0.15); groove radius gate declared, never enforced (rc 0.99 at the verified placement, 0.23 mm ridge); stage-1 PA read
  on the linear law (built groove: cap side 89 deg at the dwell exit); M3 short arm / O1.5 pin vs the hub-2 stack
  unchecked (l2_check skips r < 11.5); T3 K play ~0.36 deg nominal (0.48 worst) -> ~0.1 deg of th, held min would fall
  under 5; best_params still the refuted claim placement (a_s 9.25 / psi 154; verified a_s 9.5 / psi 150).
- Other ties / same family: trimlug-k165 18.51, inband-rssr 18.33 (tie), roller-longdyad 18.67, sidecar-longdyad 18.91,
  sidecar-parallelogram 19.13. 4 active (a sensed joint is a joint): minarc-stop-knuckle-4r 18.40.
- **Complexity frontier (v2.2):** skin-normal-3r-pin-knee 27.2 at cx 0 (score 90.1, reach 0.658, ib14 0.895, contact
  0.026), raglan-knee 27.82 at cx 0, geneva-tail-pinknee 23.57 at cx 12, desmo-slipper 18.95 at 15.75, lead 18.25.
  Knuckle cx is mostly closed loops (2 x 4) + 3 joints beyond 3 + 2 passive rotations; the spring is 3, a sliding pair 1.
- **The limiter is the J2 fold, both walls.** Bench fold 88 = 73 stretched (th 107-176; 64 are internal rotation >= 90
  across the body) + 15 folded (th 7.7-22, scapular-plane overhead). The stretched wall is the K drive's stroke (taken
  poses end at th 106.3: a1e 54.3 at dK 45.6 of 46.25). 95 = gap 13.75 = +18 workspace poses at the lead's in-band and
  contact (reach ~0.775).
- **The family's reach cap is a seat cap (round 12, measured):** best long-dyad chain ghost 17.23 (32/48, kK 2.4, onset
  14, cap 56; 269 taken, 6 contacts); every <= 4-contact cell 18.85-19.71 and never > 270 taken. The same 5-pose
  binder (117, 127, 129, 139 at plane -90..-60 / elev 45-60 / axial +105..+135; 316 at 60 / 150 / -105; link 2 to
  -7.7 mm, hub 2 rim to -3.8) in every cell, invariant to dyad, gain, cap, onset, drive and J3 stop; two deepen as K
  falls. Real drive metal on the long dyad: 38.56 (40 contacts) with pick3's drive placement unrefit.
- **Dead, do not rescreen:** K law / gain / onset / stop B / cap / dyad cells on pick3's seats (26 cells); a J3 stop as
  a reach lever (it relabels, never takes); stacked conjugate lobes without base-ring relief; desmo spec placement (psi
  184); long knee links at stk 4.85; 9-point slop scans; humerus-axial J3 rings / spars / epicondyle hubs (J1: ring in
  contact on 169-204 / 220 poses; epicondyle axis 12.8-16 mm inside the skin); scapular relays on a plain 3R
  (acromion-relay-4r gate 0 41.62 fast, hub 2 0.06 in band).
- **Machinery still by hand** (open since round 11): exo-screen.js still words the verify bar as 68.93 / 75.94 (LEAD
  comes from this plan's lead_gap 18.49; the verifier judges against it with the pooled-CI tie rule); no pair-coverage
  probe; continuity flood not a hard step; no slop state in the models; no mu column for sliding pairs; no equal-sample
  in-band comparison (S6); best_params can hold a refuted placement.
- **Lead bookkeeping status:** conecut's leader_ruling is written (8e50534). Still open for the lead: desmo-slipper's
  best_params -> the verified placement; generation-12 CAD = the gen-7 slipper-nose CAD + conecut knee re-cut (lE 97.14,
  lc 24.35, phiE 0.75, phib -91.80, ang_min 25.22, MR63ZZ pairs stk 6.0) + dowel [-111.90, 122.74] on q3', with the new
  knee's cuff twist and R17 measured (M5).
- **Compute:** the farm approval window ended ~17:20 UTC and the balance sat at the $24.40 line ($24.14 at 17:07), so
  local only unless the user renews: <= 2 niced processes per agent, OMP_NUM_THREADS=1. Box load ~17 on 4 cores at
  18:08 (jump-track CMAs, trimlug R16 judge, gen-7 CAD scoring).

### Lenses

1. **LENS complexity-desmo-conecut (the one knuckle lens; suggested id desmo-conecut-knuckle-3r, expected cx 16.0).**
   Stack desmo-slipper's spring-free, roller-free K drive (crowned O1.5 stage-1 pin in the 3-D skirt groove under hub
   2's cap ring, verified placement a_s 9.5 / psi 150 / blend 10, two-walled slot round the O2.5 nose; no clock spring,
   no stop A, no stage-1 roller) on conecut's knee and J3 dowel. Why: desmo's +0.46 vs the lead is all in-band on
   identical takes and contacts, and conecut's knee is measurably ahead of desmo (pooled -1.28, CI90 [-1.90, -0.13]).
   Target: pooled paired tie with the lead (CI90 includes 0) at cx <= 16.0, held out <= 23.45. Gates enforced IN the
   model (a failing gate rejects the placement, never a footnote): dense crank-free slop <= 0.25 deg (>= 200 points,
   both directions, full taken K range); groove centreline radius >= 1.5 mm (or retired with a measured reason and the
   ridge stress on the part); stage-1 PA read on the BUILT blended groove; dK_lim >= 44 at mu 0.15 with a mu column
   (0.087 / 0.12 / 0.135 / 0.15); the short arm's relief pocket in link 1b's J2 boss modelled as metal and checked
   against the hub-2 stack (pair probe including r < 11.5); K play carried into th per pose (both signs), held out, min
   th >= 5 (a th re-margin by K phase or stop is allowed and priced); best_params = the verified placement. Report at
   equal E-strap samples (S6) next to the plain number, per-pose dumps (tools/alignment_paired.py dump, bench and held),
   T5 depth, the motion preview. Fallback (claim either way): keep a stage-1 roller in a two-walled groove and delete
   only the spring. Kill: no stage-1 placement passes every gate with dK_lim >= 44 at mu 0.15 - report the binding gate.
2. **LENS reach-hub2-seat-ghost (reach >= 0.77 at ib14 >= 0.88; the gate the round-12 closer sent to the lead).** The
   5-pose binder moves only if hub 2 and link 2 slide ALONG the posterior deltoid. Cells, all on the best long-dyad
   ghosts (32/48 kK 2.4 onset 14 cap 56: 17.23 / 6; 34/48 kK 2.8: 17.86 / 8): (a) hub-2 seat (az2 / el2) along the
   deltoid's long axis; (b) K axis re-aim (bk1 / bk2 / psiA) so the a1e path parks hub 2 off the binder; (c) link 2
   routed by a planform turn + 60-deg climb (inner radius >= 15 mm) over the five poses. J1 seats stay in the allowed
   region (back / acromion top); no new joint, no spring. One 30-45 min gate: chain ghost (hubs O20 at their stack,
   3 mm bent bars at real height, knee as built, ideal drive), searched on the envelope bench (never the fit bench,
   never held out), judged frozen exact on Bench(110,360) with a per-pose table for 117 / 127 / 129 / 139 / 316 and
   every new loss, min th margin in th, continuity flood. Bar: <= 17.5 with <= 4 contacts and >= 274 takes. Pass: one
   hardware cell (drive re-placed on its own dyad, round-12 lesson 3) inside the round. Fail: the family is closed for
   reach with that number, written to FINDINGS.

### Carried (ideated, never screened)

- None for the main track. The round-4 picks (deltoid-crest-j3-3r, crest-knee-3r, slotted-eccentric-pin-knee-3r) were
  passed over with measured reasons in the J1 plan (O15 seeds, pin-knee fold cap); armband-pointer, cuff-sleeve-3r and
  acromion-pointer-arm-ctrack carry J1's forwarded numbers and belong to the jump track.

### Elsewhere, not to be duplicated

- Jump track (round J1): acromion-relay-4r (frozen wear running), acromion-pointer-arm-ctrack (CMA running; twin shoes
  89.55 fast), pinknee-scapular-relay-4r (pick 1, expected 18-22); armband-pointer / cuff-sleeve-3r forwarded. J1's
  lesson for the next jump: move hub 2 itself, not the base.
- Lead: generation-12 CAD (slipper-nose CAD + conecut knee + dowel), user_trimlug_k165 R16 judging, desmo best_params.

## LEAD NOTE (2026-10-17 ~18:21 UTC): leader change by the user's rule

- **conecut-knee-knuckle-3r is the verified lead: 18.28 (score 93.35), held out 22.38**, complexity 18.5, ledger
  WATCH. The lead's "tie" ruling (CI includes 0) is withdrawn: the 18:21 skeptic showed it was the lead's own rule,
  never the user's, applied to challengers only. The user's rule (plain verified gap) decides; a noise / tie rule is
  put to the user. Caveats: bench edge mostly E-strap dilution (18.67 at equal strap); held edge survives (22.90).
- Planners: the reference for "beat the lead" is now 18.28 / 22.38.

## Round J1 results (round 101, track jump; 2026-10-17 ~16:25-19:55 UTC, closer)

Ledger re-read with `tools/alignment_ledger.py get <id>` at 19:54 UTC, just before naming the winner: all five round-J1
designs exit 2 (no entry: dead rows, never audited; the round's audit pass recorded nothing). Complexity is
tools/simplicity.py v2.2 (the row's own figure in brackets where they differ). Every verifier upheld its death (0 of 5
refuted). The farm was closed all round, so every claim, verification and bound ran locally (<= 2 niced processes).
"Fast" = Bench(60,160) fast; "frozen" = frozen exact Bench(110,360), the verification protocol.

| design (lens) | verified number | frozen | reach / overhead | act / P / cx | ledger | outcome |
|---|---|---|---|---|---|---|
| pinknee-scapular-relay-4r (2, pick 1: spare J0 under the pin-knee host H1) | 31.06 fast (score 88.71) | not finished (stopped in the time box) | 0.675 fast / 0-1 of 12 | 4 / 0 / 40.5 (row 31.5) | exit 2 | dead at gate 0; ghost J0 (no metal, no seat rule) 18.30, seat-legal 18.62 |
| acromion-relay-4r (2: spare J0 under a plain O20 3R; control + instrument) | 42.74 near-touch / 41.62 plain fast | 51.83 (claimant's; not re-run by the verifier), reach 0.789 (284/360), overhead 10/28 | 0.875 fast | 4 / 0 / 0 (row 31.5; stale record) | exit 2 | dead at gate 0; over 668 configs hub 2 <= 0.12 and ib14 <= 0.68 in band |
| acromion-pointer-arm-ctrack (1, fallback: back-of-shoulder gimbal + twin shoes on an arm-fixed circular race) | 58.71 fast | **65.66 verified**: reach 0.783 (282/360), 34 contacts, overhead 4/28, min th margin 5.89 | 0.825 fast | 3 / 0 / 1 | exit 2 | dead at gate 0; ghost with no shoe, hub-1 or tine-2 metal 44.53 |
| cuff-sleeve-3r (1, cell S: GH-aimed rod in a sleeve at s 230) | 110.96 fast | not finished | 0.763 fast / 0 of 12 | 3 / 1 / 4 | exit 2 | dead at gate 0; ghost with no spar or crank 101.02 |
| armband-pointer (1, cell R: closed ring bearing round the distal arm) | 212.62 fast | bound only: >= 67.0 on the humerus axis | 0.581 fast | 3 / 0 / 0.5 | exit 2 | dead at gate 0; any rigid ring >= 72.2 with ideal stops, >= 90.9 without |
| conecut-knee-knuckle-3r (lead since the 18:21 lead note; reference) | 18.28 frozen (93.35), held 22.38 | - | 0.728 (262/360) / 8 of 28 | 3 / 0 / 18.5 | watch | stays the verified lead |

**Winner: none eligible. Every round-J1 design died at gate 0, and every verifier upheld the death.** The best number a
verifier confirmed is pinknee-scapular-relay-4r's 31.06 on the fast bench (4 active, 0 passive translations, cx 40.5).
That is not on the verification protocol: its frozen wear never finished. Even the verifier's ghost bound with a
zero-size J0 is 18.30 fast at a front seat the J1 seat rule forbids, and 18.62 at a legal seat, both above the 17.5
gate. The only frozen number a verifier confirmed this round is acromion-pointer-arm-ctrack's 65.66 (score 76.12).
**Neither beats the previous verified lead 18.49 (slipper-nose-knuckle-3r) or the current one, 18.28
(conecut-knee-knuckle-3r).** No generation CAD for J1: a dead gate-0 row is not a build candidate, so the generation
CAD of record stays the lead's. Passed over as gamed: none (no round-J1 design has a ledger entry).

**Alignment.** The ledger holds no verdict, and so no watch reason, for any round-J1 design (5 of 5 exit 2 at 19:54
UTC). The verifiers' own findings are carried here at watch level, with the numbers:
- **pinknee-scapular-relay-4r**
  - *reporting:* the claim message gave follow 0.95 and contact 0.04; the run reproduces 0.9167 and 0.0523. The row
    file has the right values.
  - *convergence:* the gate was not met (+2.70 score over the 2nd half, +0.49 over the last third, top-5 spread 1.05).
    It was replaced by the ghost-J0 bound (40 placements at T 60, a0 15-60 x azu 0-315), not by more search.
  - *stale host row:* skin-normal-3r-pin-knee.json still lists 20.63 / follow 1.0 / contact 0. Under the current
    checks the same H1 scores 23.64 / 0.95 / 0.0343.
  - *flood over-promise:* the kinematic flood's 0.83-0.90 connected reach left out J0's metal. Besides that, the relay
    un-folds 26-29 of the host's 36 fold losses, but only 5-10 of those poses survive the host's knee / slide, skin
    and L1-L2 checks.
  - *complexity:* the simplicity tool reads 40.5 and the row 31.5.
- **acromion-relay-4r**
  - *coverage:* all 555 claimed configs sat on the sigma -1 branch. The verifier closed it: sigma +1 CMA best 52.20,
    and a both-branch LHS (96 configs) best 56.45.
  - *lenient:* hub 0 has no +5 mm J0 spring stack.
  - *reporting:* the doc's three twin-policy numbers (45.73 / 52.28 / 55.60) are not in the sweep file; the v_* fields
    are fast reproductions, and the frozen 51.83 was not re-run.
  - *complexity:* the mechanism record is stale. tools/simplicity.py reads cx 0 with 3 active (no J0, no spring); the
    row says 31.5 with 4 active.
- **acromion-pointer-arm-ctrack**
  - *modelling slip, neutral:* the shoe's angular size was set at r 50, but the race sits at r ~94. Corrected: 59.86,
    and 60.53-62.58 at a re-tuned thc.
  - *convergence:* now 2.16 / 0.00 / 0.48 after 70 more CMA configs (best 60.46).
  - *search box:* every top-30 config sits on el -20. That is the J1 seat rule, not a missed region.
- **cuff-sleeve-3r**
  - *search box:* CMA_BOX el 20-85 excluded the best seat (el 0). Re-run at el 0-85: 129.98 best.
  - *wrong stated cause:* hub 2 is the pole of the (p1, e3) great circle, so J3 never enters it. Its 0 % in band comes
    from that pole, not from the arm's twist. The number is right.
  - *reporting:* the end event says 15 configs; the row has 14 (24 with the audit's runs).
- **armband-pointer**
  - *bound favoured the design:* the claim's ring bound of 57.7 dropped ring-less poses without charging contact, but a
    closed ring cannot vanish. Charged: >= 90.9 with no stops and >= 72.2 with generous stops.
  - *coverage:* proximal tilted stations (s 200-220) read 66.2-83.1.
  - *over-strict, cannot rescue:* the ring's skin face is modelled as a circle.
  - *instrument:* the 31.8 mm median skin distance is the fast cache's clamp, not a measurement.
- **Process, all rows:**
  - three of five verifiers again found the verify template's refutation bar stale (68.93 + 10 = 78.93);
  - four of five claims ran without convergence;
  - three of five frozen wears were stopped inside the time box (no local Bench(110,360) fast cache).

**What the round measured (lessons).**
1. **No rigid closed loop can ride round this upper arm.** The medial arm meets the flank on 19-27 % of poses, and the
   flexed forearm fills the ring plane near the elbow. The bound covers every station s 200-300, every axis within
   16 deg of the humerus and every bore up to 112 mm: no ring exists on >= 43 % of clip frames and >= 29 % of the
   workspace, so any ring is >= 72.2 even with ideal stops. The humerus axis also sits off-centre (58-74 mm posterior
   vs 34-46 mm medial), so a coaxial ring floats >= 20 mm off the medial skin. ARMin / NESM-style closed humeral rings
   are out for this wearer.
2. **The arm's torso-free arc is ~105 deg at every station from s 25 to 240** (<= 2 % of poses blocked). The pointing
   frame's free sector is 150-180 deg.
3. **Any 2R pointer plus an arm-axial J3 parks hub 2 at the pole of the (p1, e3) great circle** (0.00-0.03 in band),
   and any pointing-frame link down the arm rides a 184-269 deg twist (in band 0.04-0.51, falling with station). Ghost
   bounds: sleeve class with no spar or crank 101.02; arm-race class with hubs and links only 53.83; arm-race class
   with no shoe, hub-1 or tine-2 metal 44.53.
4. **Twin shoes break a C-slide's window wall.** Two shoes rigid on the moving member, `twin` deg apart, carry
   A - shoe + twin of rotation on one race of arc A, with no new joint. Reach ceiling went 0.54 -> 0.92-0.96. This is
   reusable for any open-ring idea.
5. **A base-side spare buys reach only.**
   - acromion-relay-4r: the relay is worth +4.57 frozen (+17 ws poses, 0 overhead poses) and in-band +0.001.
   - pinknee-scapular-relay-4r: a zero-size J0 is bounded at 18.30 / 18.62 seat-legal. With real metal, every
     placement jams on hub 2's orbit about J1, which has radius a1 + ~25 deg and covers every allowed back and
     acromion seat.
   - The relay class needs a short a1 (<= ~20 deg) or a J0 stacked coaxially under J1 (one hub stack higher).
6. **The plain O20 3R trades reach against hub 2's height across the two seats measured.**
   - Back seat, 41.8 / 72.3 dyad: hub 2 0.70 in band, reach 0.68.
   - Acromion-cap pole, 50 / 60 dyad: hub 2 0.06 in band (F 124 mm), reach 0.875 fast.
   - At the cap pole, hub 2's level is set by mode-A poses with J2 off its stops: (-75, 60, +60) 116 mm,
     (0..30, 150, 0) 107-113 mm, (0, 105, 0) 110 mm.
7. **Instruments now on file:**
   - tools/spare_flood.py: a full 1432-node path-tracked flood, 3 s per flood, validated 0.669 sparse vs 0.908 / 0.911
     full.
   - `armband-pointer.py bound2`: a pre-screen for any arm-encircling part.
   - docs/concepts/verify/pinknee-scapular-relay-4r-audit.py: a ~4-min ghost-J0 bound for any relay on a
     pin-knee-class host.
8. **J1's two levers are both closed by measurement.** The humerus-axial J3 (lens 1) moves the binder onto hub 2's
   pole. The scapular spare (lens 2) moves the base, not hub 2. The planner's open question ("move hub 2 itself, not
   the base") is the lever left, and the main track's round-13 ghost (proximal-j3-geodesic-knuckle-3r: J3 seat up the
   lateral deltoid, 16.72 frozen unrefit, 11.44 fast after a knee re-fit) is the first measurement that hub 2 moving
   per seat beats the 17.5 gate.

**Next focus (round J2, track jump).** The score has not reached 95. The best verified gap is 18.28 (conecut), and 95
needs 13.75: reach >= 0.8025 at ib14 0.88 (289 of 360 taken vs 262), with ~0 contact. Close in the catalogue, with
the numbers above: arm-encircling rigid parts, pointing-frame spars down the arm, 2R pointer + any arm-axial J3, arm-
fixed races, base-side spares / relays on O20 hosts with a1 >= 40.
- **Instrument first, 30 min, no hardware: the hub-2-free ceiling.** Take the plain O20 3R at both measured seats (back
  41.8 / 72.3, cap pole 50 / 60) and set hub 2 and links 1-2 at their per-pose skin requirement (the K3 march along
  hub 2's axis, the ideal of every mechanism that moves hub 2 per pose). Wear it frozen exact on Bench(110,360) with
  the continuity flood, and report taken / 360, overhead / 28, contacts, and the losses by cause (jam, fold, contact).
  - Measured reason: every J1 class died on where hub 2 must sit (0-0.12 in band), and the cap pole reaches 0.875 fast
    at hub 2 0.06. Nobody has measured what the cap pole's reach is worth once hub 2 is free.
  - If the ceiling is > 13.75 at both seats, no hub-2-moving class can reach 95 there, and J2 attacks the jams /
    folds (the reach term) instead.
  - If it is <= 13.75 (with <= 4 contacts), J2's lenses are the cheapest real mechanisms that realise that level.
- **Lens A (outside field, orthotics): a polycentric J2.** A spherical four-bar in place of the J2 revolute, so the J2
  axis is virtual and its two pins sit off the binder (orthotic polycentric hinges are built this way). Gate 0 is a
  ghost with the four-bar's two O20 pin stacks at their real height; the bar is the track's gate, <= 17.5 with
  <= 4 contacts. Complexity: 1 closed loop + 2 pins, against the knuckle family's 18.5.
- **Lens B: the cap-pole seat itself** (a seat class no verified row uses). The plain cap-pole chain plus the cheapest
  per-pose hub-2 lift the ceiling allows. It is distinct from main round 13, which moves J3's seat on pick3's
  back-of-shoulder J1, and it must not reuse the knuckle drives (track rule).
- **Machinery before the next claim:**
  - set the verify template's bar to the lead 18.28;
  - build the local Bench(110,360) fast cache once, niced (3 of 5 frozen wears died in the box);
  - fix the simplicity mechanism records for acromion-relay-4r and pinknee-scapular-relay-4r;
  - relabel skin-normal-3r-pin-knee's row to 23.64 under the current checks;
  - every claim message's numbers come from the row file.

## Round 102 plan (Round J2, track jump; 2026-10-17 ~20:00 UTC, lead verified gap 18.28)

### State

- **Lead (best verified, not gamed): conecut-knee-knuckle-3r 18.28** (score 93.35) frozen exact Bench(110,360), held
  22.38, reach 0.7278 (262/360), ib14 0.9012, follow 1.0, contact 0.0106, overhead 8/28, cx 18.5. Ledger WATCH:
  bench edge mostly E-strap dilution (18.67 at equal strap), T5 contact depth unscored (bench 4 poses / 20.24 mm), held
  th margin 5.006, NEW-self-reference (T5 reference is now this row), reporting (sweep 12.5 shown as 95.45). Next:
  slipper-nose 18.49, desmo-slipper 18.95 (cx 15.75, friction cliff at mu 0.14). Gamed: dipped-law-groove (fold margin
  0.184), seed-offset-3r-slides. Lenses must not buy points through unscored depth, a margin read in another angle,
  strap dilution or a per-pose policy without the continuity flood.
- **The 95 arithmetic, corrected** (gap_of, tools/concept_bench.py line 53): at the lead's ib14 0.90 and contact 0.0106,
  95 needs reach 0.7731 (279/360, +17 poses); at ib14 0.88 and 0 contact, 0.7825 (282/360). The J1 closer's
  "0.8025 / 289" carries a 2-point slip.
- **Planner measurement (Bench(110,360) ws, closure at the 5-deg margin, no metal, no flood; 1 min):** the plain 3R's
  KINEMATIC reach, an upper bound on the hub-2-free ceiling at fixed dyads. Back seat bvec(97.3, 64.6) 41.7/72.1:
  250/360 (0.694; folded 44, stretched 66) -> gap >= 20.6 at perfect in-band: dead for 95 whatever hub 2 does. Cap pole
  J1 bvec(43.2, 59.9) 50.2/60.3, J3 wdir(92.0, -9.0): 281/360 (0.781; folded 8, stretched 71) -> gap >= 11.9; the same
  seats with metal frozen read 267/360 (T-0 control 56.40). Best-placed th window at the cap seats: W 90 -> 0.803,
  W 100 -> 0.844, W 110 -> 0.878, W 120 -> 0.911 (W = 2 min(a1, a2) - 10). So 95 is open at the cap pole only with a
  window >= ~95 deg (min(a1, a2) >= ~53) AND J2 metal that is in band - exactly what every revolute J2 has failed.
- **Why a revolute J2 fails there:** at the cap pole hub 2's level is set by mode-A poses whose J2 ray exits the
  deltoid / acromion skin 107-116 mm from GH ((-75, 60, +60) 116; (0..30, 150, 0) 107-113; (0, 105, 0) 110): metal ON
  the J2 axis must sit there. Over 668 cap-pole configs hub 2 <= 0.12 in band, ib14 <= 0.68. A radial per-pose lift
  does not escape it: by the manufacturable-joints rule a skin-normal slide stands up by travel + block, so a ~45 mm
  lift rides 60 mm tall at every pose. The lever left is a J2 with NO metal on its axis (virtual J2).
- **Virtual J2, what is on file (round 1-2, FINDINGS ~line 975):** virtual-pole-4bar-j2 at zc seats 52/70: a link-1 pin
  28 mm off the w-line parks 0.958 in band at 53 mm, a link-2 pin 0.969 at 63 mm (hub 2 on the ray: 0.03 at 123 mm).
  It died at 103.68 (22 configs, "not a ceiling yet"; coarse 145.94 vs plain 51.97) because the crank / knee PLATES
  were swept round the virtual axis at one level (94 mm, 0 % in band). The four-bar SHIFTS the fold window (span 81.9 vs
  80.7), it does not widen it. Arc-rail and ring J2s are dead (j2-arc-sector 66.3, annular-ring 77.99).
- **Main track measurement to build on, not duplicate:** proximal-j3-geodesic-knuckle-3r (J3 seat up the lateral
  deltoid, knuckle ghost with an ideal drive): 11.44 fast (reach 0.806, ib14 0.905) after a knee re-fit; frozen exact
  16.72 unrefit. First evidence that a J3 seat move takes poses; it still carries the knuckle drive.
- **Dead classes (J1, closed in the catalogue):** rigid arm-encircling parts (>= 72.2 with ideal stops); 2R pointer +
  arm-axial J3 and pointing-frame spars (hub 2 0-0.03 in band; sleeve ghost 101.02); arm-fixed races (ghost 44.53);
  base-side spares / relays on O20 hosts with a1 >= 40 (reach only: ghost 18.30 / 18.62; acromion-relay +17 ws, ib
  +0.001). Knuckle drive / law / flank / lobe variants belong to neither lens here (track rule).
- **Machinery (open, the lead's or the first free agent's, before the next claim):** verify template's bar -> 18.28
  (still 68.93 + 10); build the local Bench(110,360) fast cache once, niced (`concept_bench --build 110 360`; 3 of 5
  frozen wears died in J1's box); simplicity mechanism records for acromion-relay-4r (reads cx 0, 3 active; should be
  4 active) and pinknee-scapular-relay-4r (tool 40.5 vs row 31.5); skin-normal-3r-pin-knee row -> 23.64 / 0.95 /
  0.0343 under the current checks; every claim message's numbers come from its row file.
- **Compute:** farm closed; local only, niced, <= 2 processes per agent, OMP_NUM_THREADS=1.

### Lenses

0. **Instrument first (30 min, no hardware; the J1 closer's step 1, now narrowed):** wear the cap-pole plain O20 3R
   frozen exact on Bench(110,360) with hub 2 and links 1-2 removed (ideal), hub 1, hub 3 and the neck at their real
   metal, the continuity flood on, at windows 90 / 100 / 110 (dyads 50/60, 55/65, 60/70, J3 re-fit per dyad on
   Bench(60,160) fast). Report taken / 360, overhead / 28, contacts, losses by cause, and the per-pose J2-ray skin exit
   (K3 march on the J2 ray): the share of taken poses whose J2 ray exits > 75 mm is the share no revolute J2 can serve.
   Lenses 1-2 start on the current numbers and switch when this lands.
1. **LENS virtual-j2 (reach >= 0.78 at ib14 >= 0.88; suggested id remote-pole-fourbar-j2-3r).** J2 as an OPEN
   spherical four-bar (all four pin axes through GH) whose instant pole is the J2 axis and lies OUTSIDE the linkage, so
   no metal sits on the J2 ray. The two link-1 pins and two coupler pins are O20 stacks parked on the low skin off the
   ray (round 1: 0.958 / 0.969 in band at 53 / 63 mm). The cranks are 3 mm bent bars at their real height with climb
   ramps (60 deg, inner radius >= 15 mm), never plates swept round the pole (round 1's death). Seats: the cap pole
   (window >= 95). This is the orthotic polycentric hinge, built as orthotists build it: the pole path (centrode) is the
   design variable. Gate 0 (30-45 min): ghost fit on Bench(60,160) fast, frozen exact Bench(110,360), all four pin
   stacks + cranks as metal, continuity flood, transmission angle >= 30 deg over the taken J2 range. Bar: reach >= 0.80
   or gap <= 15 with <= 4 contacts; > 17.5 dies with its number and the binding part. Report overhead / 28, min th margin
   (in th, the coupler's effective J1-J3 angle), complexity (tools/simplicity.py: 1 closed loop + 2 bodies + 3 pins,
   0 passive translations, no spring). Red team: the pose where the pole leaves the linkage's working range (the
   four-bar's own fold), donning, crank flutter at the transmission limit.
2. **LENS plain-crest-j3 (low complexity, cx ~0, at the same reach; suggested id cap-crest-j3-plain-3r, seeded by the
   round-4 pick deltoid-crest-j3-3r).** A PLAIN O20 3R (three pins on bearing pairs, no drive, no knee spring, no lobe)
   at the cap-pole / acromion-top seats with J3 moved up the lateral deltoid (the crest) - main round 13's measured
   lever, without the knuckle. Question: how much of proximal-j3's 11.44 fast survives with a fixed a1 and a window
   >= 95? Distinct from round 13 (knuckle drive, back-of-shoulder J1) and from deltoid-crest-j3's O15 seeds (26.35 fast
   / 35.90 frozen; re-measure at O20). Gate 0 as lens 1; same bar. Per-pose table of the cap pole's binder poses
   ((-75, 60, +60), (0..30, 150, 0), (0, 105, 0)) and every new loss. Red team: J3's stack on the deltoid crest under
   abduction bulge; the near-gimbal-lock at the stretched wall.

### Carried (ideated, never screened)

- deltoid-crest-j3-3r (round-4 pick; lens 2's seed, re-measure at O20).
- cruciate-knuckle-3r (crossed four-bar joints): only as lens 1's crossed cell with O20 pins (hubless rolling joints
  stay out under "Keep O20 only"); round 1 measured the crossed knee plates at 0 % in band, so it runs only if the open
  cell passes.

### Elsewhere, not to be duplicated

- Main round 13: proximal-j3-geodesic-knuckle-3r (CMA on the knuckle ghost), desmo-conecut-knuckle-3r (pre-registered
  claim, cell B). Lead: generation-12 CAD (slipper-nose CAD + conecut knee + dowel).

## Round 13 results (2026-10-17 ~18:10-21:35 UTC, track main, closer)

All numbers are frozen exact on Bench(110,360), fitted on Bench(60,160), and re-measured by an independent verifier.
Ledger verdicts were re-read with `tools/alignment_ledger.py get <id>` at 21:33 UTC, just before naming the winner:
desmo-conecut-knuckle-3r exit 0 (WATCH, skeptic 21:28:48Z); proximal-j3-geodesic-knuckle-3r exit 2 (no entry: dead, not
audited); the references slipper-nose, conecut-knee and desmo-slipper exit 0 (WATCH). Complexity is tools/simplicity.py
v2.2. Both rows have 3 active joints and 0 passive translations. The farm was closed (budget line), so every claim,
verification and audit ran locally (<= 2 niced processes). New this round: the closer's paired comparisons
`docs/alignment/remeasure/desmo-conecut-knuckle-3r_vs_{conecut-knee,slipper-nose,desmo-slipper}-knuckle-3r_paired.json`
(tools/alignment_paired.py compare on the verifier's blended-IK dumps, 4000 boots; diff = this design minus the other,
negative = this design better).

| design (lens) | verified gap (score) | held out | reach / overhead | cx | ledger | outcome |
|---|---|---|---|---|---|---|
| **desmo-conecut-knuckle-3r** (1: complexity; desmo stage 1 + INVERTED stage 2 on conecut's knee and dowel) | **18.98 (93.10)**; claim 19.04 reproduced (linear-law IK) | **23.19** (claim 23.24) | 0.728 (262/360) / 8 of 28 (held 18/71) | **16.5** | **watch** (exit 0; 12 upheld, 2 refuted) | **winner**; not a lead: +0.70 behind conecut, +0.49 behind slipper-nose |
| proximal-j3-geodesic-knuckle-3r (2: reach; J3 seat up the lateral deltoid, ghost drive) | ghost only: 16.52 claimed, **16.91 at the knee rule** (no K-drive metal: never a claim) | - | 0.747 ghost (269/360 at the rule) / 6 of 28 | 16.0 | no entry (dead) | dead at gate 1 (takes 269 < 274); death upheld and made firmer |
| conecut-knee-knuckle-3r (verified lead since the 18:21 LEAD NOTE, reference) | 18.28 (93.35) | 22.38 | 0.728 (262/360) / 8 of 28 | 18.5 | watch | stays the verified lead |
| slipper-nose-knuckle-3r (the plan's lead_gap, reference) | 18.49 (93.28) | 23.45 | 0.725 (261/360) / 8 of 28 | 18.25 | watch | - |

**Winner: desmo-conecut-knuckle-3r, v_gap 18.98 (score 93.10), held out 23.19, complexity 16.5, 0 passive
translations, ledger WATCH (exit 0, final skeptic verdict 2026-10-17T21:28:48Z). It does NOT beat the previous verified
lead 18.49 (slipper-nose-knuckle-3r; +0.49 worse), nor the current verified lead 18.28 (conecut-knee-knuckle-3r, LEAD NOTE
18:21; +0.70 worse). No lead change.** It is the only verified design of the round, so no tie break applies.
- Passed over: proximal-j3-geodesic-knuckle-3r's 16.91 is a lower number but not eligible: it is a GHOST (no K-drive metal
  sampled), its row is status dead, and it misses its own pre-registered take bar (269 < 274). Not gamed (no ledger
  entry); the verifier marked it "never a claim". Passed over as gamed: none. No round-13 design is gamed.
- Paired against conecut (the lead): bench +0.70 (CI90 [0.00, +0.93]), held +0.81 ([0.00, +0.89]), pooled +0.77
  ([0.00, +0.88]), P(this better) 0.00. The split is 100 % in-band: 0 discordant takes, 0 discordant contacts (the same
  262 bench takes and contact poses 205 / 237 / 264 / 316). The verifier's decomposition: desmo stage 1's cap-ring
  sector outside O20 (19 samples at 0.54 in band) +0.67, the inversion (crank-tip plate, boss) +0.09; without the ring
  sector it reads 18.37.
- Paired against slipper-nose (the plan's 18.49): bench +0.51 ([-0.40, +1.21]), held -0.26 ([-1.16, +0.51]), pooled
  -0.05 ([-0.75, +0.55]), P 0.62: worse on the bench, a held-out coin flip (it takes 11 held poses slipper-nose loses,
  contacts on 4 that slipper-nose does not).
- Paired against desmo-slipper (the complexity frontier, cx 15.75): bench +0.05 ([-0.74, +0.89]), held -0.72
  ([-1.54, +0.14]), pooled -0.50 ([-1.14, +0.16]), P 0.89. So desmo-conecut is not dominated: +0.75 complexity buys
  0.72 held-out points (conecut's knee: 0 knee slides) and a stage 2 that holds mu 0.15.
- What it delivers that holds: the first desmo-family drive whose stage 2 holds mu 0.15 (inverted slot: nose fixed in
  link 1a, slot in the crank tip; PA stroke 64.5 deg of K at mu 0.15, 61.0 at 0.20; pocket PAs 25.5 / 32.0 vs gate
  34.47; slot slop 0.04 deg); no spring, roller, lug band or outer wall; the slot end is a real stop B (46.5) between
  the two bodies of its pair. Shallower contact than conecut on the SAME four poses: bench T5 16.15 mm (conecut 20.24),
  264 at -1.17 vs -5.80; held 14 contacts / 43.84 mm (conecut 60.97).
- **Generation CAD (lead's):** the winner is conecut's chain, knee and dowel with the K drive swapped, so its CAD is the
  gen-8 CAD `user_conecut_knee` (building now) with desmo stage 1 (O1.5 crowned pin in the blended 3-D groove under hub
  2's cap ring, pressed 440C ring insert, a_s 9.529 / psi 149.71 / blend 10) and the inverted stage 2 (O1.5 440C nose
  pressed in link 1a, 3.7 mm two-walled slot in the crank tip, kslot 46.5, seat r_c 16.176 / beta -177.169). That CAD is
  where the G3 watch (R17, cuff twist, drag of two sliding pairs at mu 0.15) and the M3 relief pocket get measured. It
  is not a lead, so whether to build it before a better row lands is the lead's call.
- **Row bookkeeping (lead's, from the audit):** the row's top-level verdict still reads as the screen ("passes every
  drive gate at mu 0.15 on BOTH stages"); the verified wording is "mu 0.15 nominal only; a_s +0.07 mm binds stage 1 at
  K 44.75". The dashboard sweep best 86.19 is a failing linear-read sweep record. proximal-j3's row: near_touch min
  0.66 mm should read 0.30 (ws pose 230, plane 15 / elev 90 / axial 30).

**Alignment (every watch reason of the round's designs, as upheld by the skeptic).**
- **desmo-conecut-knuckle-3r: WATCH, 12 upheld, 2 refuted** (S2 part-weighted in-band +0.79 < the 3.0 watch line;
  T1 near-touch, report-only by the user's 2026-10-17 ruling).
  - *continuity*: static 23.19 = full-envelope flood 23.19 (0 dropped, the rule's flood); the kNN flood reads 32.18
    held (84 forced poses dropped, -8.99) and 24.47 on the bench file's flood. On the bench file the kNN check reads
    20.67 vs 18.98 (-1.69), the same as every sibling; no sibling has a held kNN flood on file, and the full flood
    evaluates no skin at its intermediate envelope nodes, so whether the 84 held poses' stepping stones are contact-free
    is unmeasured.
  - *reporting* / *R1*: the row verdict text is the screen's; the dashboard carries it and a failing sweep best 86.19
    (reach 0.344). A label: the ranking reads v_gap.
  - *NEW-pa-reread*: the "mu 0.15 on BOTH stages" claim rests on reading stage 1 on the built blended groove. The cap
    (back-drive) side is gated only outside the blend (K 0-10.72 of 46.5): inside it the built cap PA is above the
    family gate 34.47 from K 0 to 9.0, above 60 to K 3.14, and self-locking (> 81.47) only to K 0.33. The rest pose
    (dK 4.6, cap PA ~52.7) and the taken overhead pose at axial -135 (dK 5.8, ~47) sit in that ungated band. On the
    family's linear read the same placement fails at K 0 (cap 35.05 vs 34.47; fast 86.52) and its friction limit is
    mu ~0.139, desmo-slipper's. The score does not move (fast 13.31 at mu 0.087 or 0.135, linear). Genuine gain: stage 2.
  - *NEW-friction-cliff*: at mu 0.15 stage 1's forward PA sits 0.07 mm from a bind: a_s 9.60 binds at K 44.75 (fast
    14.56, +1.25), a_s 9.65 at 43.0 (15.17), psi +0.5 deg at 46.0 (13.94), mu 0.17 at 45.5 (14.56); the held stroke needs
    K 46.27 (nominal bind 47.5). All flat at mu 0.087.
  - *NEW-silent-check*: RC_MIN 1.5 is declared, never cut on: rc_min 1.01 at K 0.25, 0.247 mm ridge (440C insert,
    ~1.5 GPa line-contact Hertz at 25 N). Worst-tolerance crank-free slop 0.281 deg (groove c 0.015) is over the claim's
    own 0.25 gate (nominal 0.187 at K 44).
  - *M3*: the stage-1 short arm (a_s 9.529) and O1.5 pin enter hub 2's O20 footprint in link 1b's J2-seat layer, unchecked
    (relief pocket 5 x 4 x 1.5 mm assumed); the crank-tip plate rides exactly 0.150 mm over link 1a's boss on all 372
    bench poses (a stack error > ~0.13 mm makes it rub, no friction carried); plate to hub K's O20 1.23 mm (a ~0.25 mm
    crank-pivot error reaches the 1.0 mm gate).
  - *T3*: held min th margin 5.006 at pose 1054 (ws 135 / 30 / -135, dK 46.27, dth/dK 0.403), bench 5.181; the dense
    nominal K play 0.227 deg takes it to ~4.92 (worst tolerance ~4.89), under the 5-deg rule. Same as conecut and
    desmo-slipper.
  - *NEW-ws-inband* (family-wide): on taken workspace poses at elev 90-140 (unscored) 0.8308 in band, 16.83 % above
    14 mm (p95 20.06, max 30.74 mm) vs 0.8924 on the scored clip frames; overhead 0.9333 in band, but 4 of 8 taken
    overhead poses have metal under 2 mm. Same metal as conecut (0.8315), ahead of slipper-nose (0.8004).
  - *G4*: m_sub span over taken poses [10.81, 99.0], identical to conecut / slipper-nose; at K rest under 1 deg on 50 of
    205 rest poses (skeptic's new measurement, `docs/alignment/remeasure/desmo-conecut-knuckle-3r_msub_rest_bench.json`).
    B1 is the user's call.
  - *G3*: no CAD, no R17 / dynamics run, no cuff twist, no drag reading: nobody has measured the force flow through
    the ungated back-drive band.
  - *P2* (negligible): the slot length 46.5 was argued from a held-out stroke (46.27); it equals the displaced lead's
    dK_lim 46.5; a bench-only cut at ~45.75 would lose >= 3 held poses (>= +0.3 held points); the bench claim does not
    depend on it.
  - Wearer: overhead 8/28 bench (lost: fold 14, contact 3, J3 stop 3), 18/71 held; raised arm (elev >= 90) 47/113
    bench, 123/300 held; taken poses under 2 mm 33/372 bench (3 under 1 mm, closest 0.072 mm at pose 139) and 71/861
    held (13 under 1 mm, closest 0.325); deepest contact 9.47 mm at bench pose 237 (plane 15, elev 165: the crank -9.42
    and the tip plate -5.87).
- **proximal-j3-geodesic-knuckle-3r:** no ledger entry (dead). Verifier findings, carried as notes: (1) the claimed
  config k211 spends the knee singularity margin (ang_min 22.26 vs the round's rule 25.22, 0.26 deg off the search box
  floor 22.0; the top-8 configs all at 22.0-23.2): at the rule it reads 16.91, 269 taken (claimed 271), 12 knee slides
  (claimed 8), overhead 6/28 (claimed 8) - the +2 takes and +2 overhead were margin, not seat; (2) protocol deviation:
  the pre-registered gate said search on the envelope bench, the search ran on Bench(60,160) fast, and the re-fit knee
  lost on envsel (19.75 / 10 contacts vs 18.84 / 7 unrefit; knee link 4.9-7.8 mm into the skin at axial -166);
  (3) the row's near-touch minimum is misreported (0.66 vs 0.30 mm); (4) the verdict's drive argument misread round 12:
  a re-placed drive costs ~0.3, so a gate-2 cell at the rule could read ~17.2 - a score question (behind 18.28 by ~1.1
  or a tie), not a reach rescue.

**Lessons (measured).**
1. **The back-of-shoulder knuckle family is closed for reach.** Moving J3's seat up the lateral deltoid moved the
   round-12 binder 2-4 mm out of the skin (117 / 127 cleared, 129 -7.72 -> -3.79 mm) but frozen takes stayed at
   269-271 for every seat, knee and law (269 at the knee rule), against the pre-registered 274 and the 279 that 95
   needs. With round 12's ghost maximum of 270, two rounds and ~40 cells say the same: the cap is the fold at the
   stretched wall (73 bench poses, th up to 176; dK 52.6 of the 57-deg cap), and what binds is radial (link 2 over the
   deltoid crest at 129, hub K overhead at 264), not lateral (a +-1.5 mm bar offset moves 129 <= 0.4 mm). The jump-track
   planner's bound agrees: the plain O20 3R's kinematic reach at the back seat is 250/360 (gap >= 20.6 at perfect
   in-band), at the cap pole 281/360.
2. **A search box whose floor sits below a rule is a margin leak.** proximal-j3's knee box started at ang_min 22.0
   against the round's 25.22 rule; the optimiser went to the floor and bought +2 takes and +2 overhead poses with the
   singularity margin. Every rule bound (ang_min, th 5 deg, O20, stops) is a hard box edge, never a starting point.
3. **The fit-bench sampling bias reaches the cuff knee.** A knee re-fit on Bench(60,160) lengthened the E strap and knee
   (lE 67.8 -> 84-90) and lost 0.9 on envsel through the knee link at axial -166 across the body, while on
   Bench(110,360) it looked like a near-touch win (under-1-mm takes 7 -> 2). Knee re-fits run on the envelope bench or
   carry an |axial| >= 150 contact gate.
4. **Inverting a slipper stage fixes its friction limit, at a geometric price.** With the nose fixed in the driven link
   and the slot in the crank, stage 2's PA stroke at mu 0.15 goes from 43.25 to 64.5 deg of K; the nose's relative path
   runs ~3.7 mm toward the K axis, so the crank-tip plate needs a plate-vs-hub gate (the seat moved r_c 15.37 -> 16.18;
   r_c >= 17 fails the inverted PA at rest). The new limit is stage 1, and it depends on how its PA is read: linear law
   mu ~0.139, built groove 0.15 at nominal (0.07 mm from a bind), with a 35-81 deg back-drive band from K 0.33 to 9.0
   that neither reading gates.
5. **Drive variants are not reach levers; they move in-band by sample weight.** Cutting the slot to 49.75 left fast
   reach at 0.775; desmo-conecut and conecut share every take and contact (0 discordant poses). The whole +0.70 is
   desmo stage 1's cap-ring sector outside O20 (+0.67, 19 samples at 0.54 in band) plus the inversion (+0.09). That
   sector is the measured lever for a cx-16.5 design at conecut's number (18.37 without it).
6. **Same contact poses, shallower contact:** the inverted drive cuts T5 depth on conecut's four poses (bench 20.24 ->
   16.15 mm; 264 -5.80 -> -1.17; held 60.97 -> 43.84 mm) without moving the score: depth stays unscored (T5).
7. **Reach did not move for the fourth round.** Best verified take count: 262 (conecut, desmo-conecut).
8. **Process:** the verify template still bars against 68.93 / 75.94 (both verifiers judged against the lead instead);
   a row kept the screen's verdict text after verification; a row misreported its near-touch minimum; a search box
   floor sat under a rule; the pre-registered search bench was not used. The models still carry no slop state (K play
   into th is estimated: held ~4.92).

**Next focus (round 14).** The score has not reached 95: the best verified gap is 18.28 (conecut-knee-knuckle-3r, the
lead); 95 needs 13.75, i.e. 279/360 takes at the lead's in-band and contact (+17 poses). This round closed the main
track's last reach question with numbers: the back-of-shoulder knuckle caps at 269-271 takes (lesson 1), and the plain
3R's kinematic reach there is 250. The only seat with a measured path to 95 is the cap pole (281/360 kinematic,
window >= ~95 deg needed), which is the jump track's round J2 (virtual-J2 four-bar, plain crest J3) - do not duplicate it.
Under the lead directive the main track spends one lens in the knuckle family, on complexity or overhead contact depth:
- **Lens 1, complexity (measured lever +0.67):** desmo-conecut with stage 1's cap-ring sector kept inside hub 2's O20
  footprint (or under its stack), at cx <= 16.5. The decomposition reads 18.37 without the sector (conecut 18.28); a
  passing cell is a 2-point-simpler design at the lead's number. Gates, enforced IN the model: stage-1 forward PA bind
  >= 1 deg of K above the held stroke at a_s +-0.1 mm, psi +-0.5 deg and mu 0.17 (today 0.07 mm from a bind); RC_MIN
  enforced (or retired with the insert's Hertz stress on the part); the back-drive band K 0.33-9.0 given a gate or a
  measured force (R17-style) instead of an exemption; the stage-1 arm's relief pocket modelled as metal and checked
  against the hub-2 stack; plate-vs-horn running gap >= 0.25 mm; K play into th per pose (held min >= 5); report at equal
  samples (S6) and paired against conecut. Kill: no stage-1 placement keeps the sector inside O20 with dK_lim >= 46.3 at
  mu 0.15 - report the binding gate.
- **Lens 2, overhead contact depth (the family's 4 shared contacts):** 237 (plane 15, elev 165: crank -9.42, plate
  -5.87), 205 (hub 2 -4.28, cap ring -3.64), 316 (link 2 -1.23), 264 (hub K -1.17). They are identical on conecut,
  desmo-conecut and the round-12 cells and are the T5 watch on every leader. In the paired split two contacts were
  worth +0.53 against slipper-nose, so clearing all four without losing a take is worth ~1 point (conecut ~17.2).
  Per-pose attribution first (which part, which coordinate), then only levers that move the metal (crank / plate
  routing at 237, hub-2 cap ring at 205); a stop that turns a contact into a fold is a relabel and does not count.
- **Reach (not a main-track lens):** port the K drive (the fold-window widener) onto the jump track's cap-pole J2 only if
  J2's gate 0 passes (<= 15 or reach >= 0.80 with <= 4 contacts).
- **Machinery before the next claim:** every rule bound as a hard search-box edge (ang_min >= 25.22, th >= 5, O20); the
  verify template's bar -> 18.28; the row verdict rewritten from the verification block on verify; near-touch columns
  computed from the dumps; slop state in the models; the pre-registered search bench enforced by the runner.
- **Do not rescreen:** J3 / hub-K / link-2 seat moves on the back-of-shoulder long-dyad chain (proximal-j3: 269 at the
  rule); link-2 bar offsets (+-1.5 mm moves the binder <= 0.4 mm); the wrap region wd 74-78 / wa -22..-12 (13.87 vs
  11.44 fast); knee re-fits on Bench(60,160) without an |axial| >= 150 gate; stage-2 slot length as a reach lever.

### Needs the user's say (unchanged)

- **B1:** does m_sub at K's rest, or the coupled reading, decide the fold rule? It still decides G4 for the whole
  family (desmo-conecut: 50 of 205 rest poses under 1 deg, like conecut).

## Round 14 plan (2026-10-17 ~21:45 UTC, track main, lead verified gap 18.28)

Planner's read of the files at 21:35-21:45 UTC. Ledger exits re-read: conecut-knee-knuckle-3r and
desmo-conecut-knuckle-3r exit 0 (WATCH); crest-knee-3r exit 2 (no entry); gamed: dipped-law-groove-knuckle-3r (fold
margin 0.184), seed-offset-3r-slides. The lead directive (16:20 UTC) still caps main at ONE lens inside the knuckle
family at the back-of-shoulder seats, so the round-13 closer's two lenses (complexity, overhead contacts) run as two
cells of ONE row: the contacts they target are mostly the drive's own metal (205's cap ring, 237's crank and plate).
The jump track's round-102 judge routed two things here (docs/concepts/round102_ideation.md section 6):
cap-plateau-knuckle-3r ("main round 14's seat cell, hub-2 tail gate first") and the antcrest basin for crest-knee-3r.

### State

- **Lead (best verified, not gamed): conecut-knee-knuckle-3r 18.28** (score 93.35) frozen exact Bench(110,360), held
  22.38, reach 0.7278 (262/360), ib14 0.9012, follow 1.0, contact 0.0106 (4 poses), overhead 8/28, cx 18.5, 3 active,
  0 passive translations. Watch (carry into every summary): bench edge over slipper-nose mostly E-strap dilution
  (18.67 / held 22.90 at equal strap); T5 depth unscored (bench 4 poses / 20.24 mm, held 14 / 60.97); held th margin
  5.006 (K play ~0.23 deg puts it near 4.92); NEW-ws-inband (taken elev 90-140 poses 0.8315 in band); dashboard sweep
  12.5 shown as 95.45; G4 m_sub at K rest (B1, the user's call); NEW-self-reference (T5 reference is the row itself).
- **Round-13 winner, not a lead: desmo-conecut-knuckle-3r 18.98** (93.10), held 23.19, **cx 16.5**, same 262 takes and
  4 contact poses as conecut (0 discordant). Paired vs conecut +0.70 bench / +0.81 held, 100 % in-band: desmo stage 1's
  cap-ring sector outside O20 (19 samples at 0.54 in band) +0.67, the inversion +0.09; ib14 0.8924 (0.76 points under the
  0.90 knee of the gap). Watch: NEW-pa-reread (built-groove cap PA ungated K 0.33-9.0 at 35-81 deg; linear read mu
  ~0.139), NEW-friction-cliff (a_s +0.07 mm binds at K 44.75; psi +0.5 deg at 46.0; mu 0.17 at 45.5; held stroke needs
  46.27), NEW-silent-check (RC_MIN 1.5 never cut: rc 1.01, 0.247 mm ridge; worst-tolerance slop 0.281 > its 0.25 gate),
  M3 (relief pocket 5 x 4 x 1.5 assumed; plate 0.150 mm over link 1a's boss; plate to hub K 1.23 mm), T3 (held th 5.006
  -> ~4.92 with K play), continuity (kNN flood held 32.18 vs 23.19), G3 (no R17 / drag / cuff twist).
- Others at the lead's reach: slipper-nose 18.49 / 23.45 (cx 18.25), trimlug-k165 18.51, inband-rssr 18.33 (polished),
  roller-longdyad 18.67, desmo-slipper 18.95 / 23.90 (cx 15.75; jams at mu 0.14). 4 active: minarc-stop-knuckle-4r
  18.40 (polished). **Complexity frontier (v2.2):** cx 0 skin-normal-3r-pin-knee 27.2 (reach 0.658, ib14 0.895,
  contact 0.026; 23.64 under the current checks), raglan-knee 27.82; geneva-tail-pinknee 23.57 at cx 12; desmo-slipper
  18.95 at 15.75; desmo-conecut 18.98 at 16.5; lead 18.28 at 18.5.
- **95 arithmetic** (gap_of, tools/concept_bench.py line 53: 100 (max(0, .90 - ib14) + max(0, .95 - follow) +
  max(0, .90 - reach)) + 100 contact): at ib14 >= 0.90 and the lead's contact 0.0106, reach 0.7731 = 279/360 (+17
  takes); at ib14 0.88 and 0 contact, 0.7825 = 282/360. In-band above 0.90 buys nothing; in-band below it costs 1:1.
- **Where the lead loses poses (bench, 98 lost):** fold 88 (stretched 73 at th 107-176, 64 of them internal rotation
  >= 90 across the body; folded 15 at th 7.7-22, scapular-plane overhead), J3 stop 6 (182/184/208/209/211/238, bound
  by hub 2 / K-housing metal 1-22 mm into the skin), contact 4. Overhead (desmo-conecut) 8/28: lost to fold 14,
  contact 3, J3 stop 3. Stretched wall = dK 52.6 of the 57-deg cap.
- **The 4 shared contacts** (identical on conecut, desmo-conecut and the round-12 cells; depths on desmo-conecut):
  237 (plane 15, elev 165: crank -9.42, tip plate -5.87), 205 (hub 2 -4.28, cap ring -3.64), 316 (link 2 -1.23), 264
  (hub K -1.17; conecut -5.80). Paired: two of them were worth +0.53; all four without a lost take ~1 point (conecut
  ~17.2). Measured on trimlug (round 11): lateral relief 1 mm toward K's axis gains 0.9-1.0 mm at 237 / 264; the crank
  tip's outer wall needs ~0.5 mm narrower, hub 2's housing wall a ~0.3 mm flat; a radial lift makes both deeper (T5
  16.07); trimming 264 by the flank needs the stroke to stop at dK ~35 (the stroke wall).
- **Measured ceilings:** back-of-shoulder knuckle 269-271 takes (proximal-j3 ghost 16.52 at 271; 16.91 / 269 at the
  knee rule ang_min 25.22; round-12 long-dyad ghost max 270); plain O20 3R kinematic reach 250/360 at the back seat;
  cap pole J1 bvec(43.2, 59.9) 50.2/60.3, J3 wdir(92.0, -9.0) 281/360 kinematic (267 with metal frozen, T-0 56.40);
  U-law a1 = clip(max(40, th - 62), 40, 62), a2 70: 295/360 ws at wdir(90, 10), 285 at wdir(92, -9) (judge-reproduced);
  fixed 60/70 311-318. Cap-pole revolute J2: hub 2 <= 0.12 in band over 668 configs (ib14 <= 0.68), J2 ray exits the
  skin 107-116 mm at mode-A poses. U-law hub-2 trade: level 79 -> 271 ws clear, 52/394 in band (~21); level 63-67 ->
  0.69-0.70 in band, 206-235 ws (>= 25); the planner's stop-box scan keeps <= 100/360 with a 12 mm band >= 0.8.
  Antcrest seats (J1 bvec(55, 62), J3 wdir(98-104, +5..+18)), Bench(60,160): J2-exit p95 76-77 (cap control 96), > 75 mm
  on 8-9/160 ws (cap 20) and 0-3/60 clips; fold loss 20-24 of 220 vs H1's 36; H1's knee collides 182-196/220 there; the
  plain crest cell at bvec(55, 62) / wdir(98, 5) 50/58 reads 62.80 fast with hub 2 0.00 in band at 99 mm. Exact
  Bench(110,360) J2-exit for the antcrest seats is running (j2exit.py 110 360, the J2 judge's section 7).
- **Dead, do not rescreen (main):** back-seat J3 / hub-K / link-2 seat moves (proximal-j3), link-2 bar offsets, the wrap
  region wd 74-78, knee re-fits on Bench(60,160) without an |axial| >= 150 gate, stage-2 slot length as a reach lever,
  K law / gain / onset / cap / dyad cells (26), positive four-bar K under strict B1 (51.75, 2520 configs), drive cranks
  beside link 1b, radial lifts of overhead metal, the dip below stop A (gamed), spring-held spare 4R, direct cam pairs
  between O20 stacks, scapular relays on a plain 3R (acromion-relay 41.62), rigid arm rings (>= 72.2), 2R pointer +
  arm-axial J3, arm-fixed races, 4R Keemink windows (rounds 2 / 10 / J1).
- **Process lessons to obey (round 13):** every rule bound is a hard search-box edge (ang_min >= 25.22, th >= 5 incl.
  K play, O20, own-angle stops), never a starting point; knee re-fits on the envelope bench; the pre-registered search
  bench is the one the runner uses; held-out pose indices never enter a search / selection bench or a tolerance / box
  edge (select on the envelope-selection draw, claim held out); every claim reports the plain gap, S6 equal-sample
  in-band for any added or lengthened in-band metal, min th margin, continuity flood, per-pose dumps
  (tools/alignment_paired.py dump, bench + held), T5 depth, the motion preview.
- **Machinery still open:** verify template bar 68.93 / 75.94 -> 18.28; row verdict rewritten from the verification
  block; near-touch columns from the dumps; slop state in the models; search-box edges enforced by the runner.
- **Compute:** farm CLOSED (budget line); local only, niced, <= 2 processes per agent, OMP_NUM_THREADS=1, judges
  --jobs 1. Load ~6.5 on 4 cores at 21:35 (gen-8 CAD score_design + checks, j2exit 110 360).

### Lenses

1. **LENS knuckle-o20-overhead (the one knuckle lens; complexity + contact depth as cells of one row; suggested id
   desmo-o20-knuckle-3r).** Base: desmo-conecut's chain, knee, J3 dowel and inverted stage 2, verified placement.
   - *Cell A (complexity):* stage 1's cap-ring sector kept inside hub 2's O20 footprint or under its stack, cx <= 16.5.
     Worth +0.67 measured (decomposition reads 18.37 without the sector). Gates IN the model: stage-1 forward PA bind
     >= 1 deg of K above the held stroke at a_s +-0.1 mm, psi +-0.5 deg and mu 0.17; RC_MIN enforced (or retired with
     the insert's Hertz stress on the part); the K 0.33-9.0 back-drive band gated or force-measured (R17-style); the
     relief pocket as metal against the hub-2 stack (pair probe incl. r < 11.5); plate-vs-horn running gap >= 0.25 mm;
     K play carried into th per pose, held min >= 5.
   - *Cell B (overhead contacts, on cell A's chain):* per-pose attribution first (part, coordinate) for 237 / 205 / 316
     / 264, then only levers that move the metal sideways (crank / tip-plate routing at 237, cap ring and hub-2 housing
     at 205, K-side relief at 264, link-2 planform at 316); radial lifts are measured-dead; a stop that turns a contact
     into a fold or a J3-stop loss is a relabel and does not count.
   - Target: <= 17.5 frozen exact at cx <= 16.5 with >= 262 takes (a new lead, 2 points simpler); floor: cell A alone
     <= 18.28 at cx 16.5. Report paired vs conecut (bench + held), S6, T5. Kill: no stage-1 placement keeps the sector
     inside O20 with dK_lim >= 46.3 at mu 0.15 (report the binding gate); cell B clears < 2 contacts without a lost take.
2. **LENS cap-seat-ulaw (reach >= 0.77 at ib14 >= 0.88; the jump judge's routed cell, id cap-plateau-knuckle-3r).** The
   only main-side cell with a kinematic count over 279 (295/360). It is at a NEW seat (cap pole / antcrest, acromion
   top), so it does not reopen the back-seat reach the directive closed, and no drive work happens here (it borrows
   lens 1's drive if it passes). Gate 0 (ghost, 30-45 min, metal hubs O20 at their stacks, 3 mm bars at real height,
   ideal K law): fit the U-law chain at wdir(90, 10), wdir(92, -9) and the antcrest J1 bvec(55, 62) / J3 wdir(98-104,
   +5..+18), search on the envelope bench, judge frozen exact Bench(110,360) with the continuity flood. Pre-registered
   pass: hub 2 within 12 mm of its fitted level on >= 0.8 of taken poses, with <= 10 ws lost to a J1 OWN-angle stop
   (dowel in an arc slot), AND >= 279 takes at ib14 >= 0.88 with <= 4 contacts. Report the per-pose J2-ray skin exit
   (K3 march), taken / 360, overhead / 28, min th margin. Kill (expected ~90 %): the tail does not separate - write the
   number to FINDINGS as the knuckle's cap-pole bound and stop.
3. **LENS crest-pinknee-cx0 (low complexity at reach; catalogue row crest-knee-3r, seeded by the antcrest basin).** A
   PLAIN O20 3R (three pins on bearing pairs, no drive, no spring) with the two-pin MR63ZZ cuff knee (cx 0 under v2.2)
   at the antcrest seats, where the fold loss is 20-24 of 220 vs H1's 36. The knee is re-fit on the envelope bench with
   an |axial| >= 150 contact gate (H1's knee collides there), ang_min >= 25.22 and the knee window as a physical stop.
   Bar: frozen exact <= 21.0 (beats the cx-0 frontier 27.2 / 23.64 by >= 2.6); stretch <= 18.28 (a cx-0 lead).
   Kill: hub 2 <= 0.5 in band on taken poses (the cap-pole failure) or frozen exact > 23.64. Shares lens 2's J2-exit
   measurement (same seats, j2exit_110 when it lands); per-pose table for the antcrest binders and every new loss.

### Carried (ideated, never screened)

- crest-knee-3r (round-4 pick): lens 3's row, re-measured at O20 / margin 5 on the antcrest basin.
- deltoid-crest-j3-3r (round-4 pick): a closing screen on the jump judge's forwarded O20 numbers (seeds 75.75 / 91.12
  fast; best crest cell 62.80, hub 2 0.00 at 99 mm); 20-min box, expected dead; doubles as lens 3's no-knee control.
- slotted-eccentric-pin-knee-3r (round-4 pick): only as lens 3's cell B if lens 3's measured limiter after gate 0 is the
  fold, with its knee hub at O20 (not O11) and its complexity recorded.

### Elsewhere, not to be duplicated

- Jump track round 102 (J2) screening now: remote-pole-fourbar-j2-3r, cuff-slaved-elbow-fourbar-3r (virtual J2 at the
  cap pole). Lens 2 / 3 here are revolute-J2 cells at the cap / antcrest seats that its judge routed to main; the J2
  track's next planner should not re-pick them.
- Lead: gen-8 full CAD user_conecut_knee (judging), j2exit 110 360 (J2 judge section 7).

### Needs the lead's say

- proximal-j3-geodesic-knuckle-3r with a re-placed drive at the knee rule reads ~17.2 by its verifier's estimate (16.91
  ghost, drive ~+0.3): a possible ~1-point lead change that the directive ("not reach") and the round-13 closer's
  do-not-rescreen block. Not a 95 path (269 takes); a score question for the lead.

### Needs the user's say (unchanged)

- B1 (m_sub at K rest vs the coupled reading) still decides G4 for the whole knuckle family.

## Round 102 results (Round J2, track jump; 2026-10-17 ~20:00 - 2026-10-18 ~00:40 UTC, closer)

I re-read the ledger with `tools/alignment_ledger.py get <id>` at 00:37 UTC, just before naming the winner:
- deltoid-crest-j3-3r exits 0, verdict WATCH (skeptic, 00:32 UTC);
- cruciate-knuckle-3r, remote-pole-fourbar-j2-3r and cuff-slaved-elbow-fourbar-3r exit 2 (no entry: dead rows, never
  audited).

No design is gamed. Complexity is tools/simplicity.py v2.2. All four rows are dead, and every verifier upheld its
number (0 of 4 refuted). The farm was closed all round, so everything ran locally (<= 2 niced processes). "Fast" means
Bench(60,160) fast with kit checks; "frozen" means frozen exact Bench(110,360), the verification protocol. The lens-0
instrument (the hub-2-free ceiling, windows 90 / 100 / 110) produced no row. The judge's Bench(110,360) J2-exit for the
cap control (docs/concepts/round102_ideation.md section 7) is its only measured output: 281/360 closing, J2 exit p95
107 mm, 0.181 of closing ws poses > 75 mm.

| design (lens) | verified number | frozen | reach / overhead | act / P / cx | ledger | outcome |
|---|---|---|---|---|---|---|
| deltoid-crest-j3-3r (2: plain O20 3R, J3 on the deltoid crest; the round-4 pick re-measured at O20 / margin 5) | **v_gap 47.86 frozen** (score 82.60) on the claimed 36.63-fast config; held 50.05. The screen's later best is 26.78 fast; the verifier re-wore it at **40.17 frozen** (score 85.39) | 47.86 / 40.17 | 0.575 (207/360), overhead 4/28 / 0.606 (218/360), overhead 6/28 | 3 / 0 / **0** | WATCH | dead on the spec's kill bar (32.10) and on the track's 17.5 gate; convergence passed (n 7118: 0.265 / 0.0 / 0.0) |
| cruciate-knuckle-3r (1: crossed four-bar J2 at the cap pole, O20 pins) | 86.95 fast (score 68.38), honest | not run (fast is 4.5x the bar) | 0.7125 fast / not measured | 3 / 3 / 16 | exit 2 | dead at gate 0; 23.8 worse than the plain cap-pole 3R through the same kit (63.18) |
| remote-pole-fourbar-j2-3r (1: open spherical four-bar J2, pole off the linkage) | 90.11 fast (score 67.23), honest | not run (fast is 5x the bar) | 0.7688 fast / kinematic window 16/28; taken 4/12 fast | 3 / 3 / 16 | exit 2 | dead at gate 0; 27 worse than the control |
| cuff-slaved-elbow-fourbar-3r (1: 4R elbow path with a slave loop closed through the arm cuff) | 108.22 fast (kit-honest; the claim's 107.61 fails the kit audit) | 117.08 (claimant's; not re-run by the verifier), overhead 5/28 | 0.7625 fast | 3 / 3 / 16 | exit 2 | dead at gate 0; follow 0.70 (the loop root vanishes mid-motion) |
| conecut-knee-knuckle-3r (the lead, for reference) | 18.28 frozen (93.35), held 22.38 | - | 0.7278 (262/360) / 8 of 28 | 3 / 0 / 18.5 | WATCH | stays the verified lead |

**Winner (by the rule): deltoid-crest-j3-3r.** Its v_gap is 47.86 frozen (score 82.60), complexity 0, 3 active
joints, 0 passive joints, 0 passive translations, ledger WATCH. It is the round's only design with a number on the
verification protocol, and that number was confirmed by an independent verifier. The verifier also re-wore the
screen's later best (26.78 fast) at 40.17 frozen (score 85.39). **It does not beat the previous verified lead, 18.28
(conecut-knee-knuckle-3r): it trails by 29.58 on the claim and by 21.89 on the later best.** It is dead on the track's
gate-0 bar (17.5) and on its spec's kill bar (32.10), and the row says so (status dead). So, as in round J1, it is not
a build candidate: no generation CAD for J2, and the generation CAD of record stays the lead's. No design reached the
judges (judge_all), so no EVOLUTION row. Passed over as gamed: none.

**Alignment.** The ledger's WATCH reasons for deltoid-crest-j3-3r (auditor 00:25 UTC, skeptic 00:32 UTC; the skeptic
upheld 4 of 6 and refuted 2 by measurement):
- **reporting:** the dashboard's sweep best of 26.78 (score 90.26) sits 21.08 below the verified 47.86.
- **T1 (plain-gap search):** the zc-frontier family's evaluate() (docs/concepts/models/zc-frontier-3r.py lines 128 and
  148) returns the PLAIN gap as the objective, so 2526 configs (later 7118) were searched on the plain gap, not on the
  near-touch gap CLAUDE.md asks for.
  - Bench reading: 47.87 plain, 64.85 with metal < 1 mm counted as contact, 95.55 at < 2 mm, 122.83 at < 3 mm.
  - The near-touch shells (16.98 / 47.70 points) compare with the lead's 1.64 / 16.56.
- **G1 (overhead is metal-on-skin):** the 4 overhead workspace poses the claim takes (4/28, elev >= 140) have their
  lowest metal at 0.13, 0.84, 1.20 and 1.34 mm on the bench, and at 0.07-0.66 mm on the 4/26 held poses.
  - At the 1 mm reading, overhead falls to 2/28 on the bench and 0/26 held.
  - Raised-arm clip frames: 6 of 10 taken, all within 1.4 mm.
  - 0 overhead poses have 2 mm of clearance.
- **R2:** the s10 config (26.78 fast) wears to 40.17 frozen, 13.39 worse.
  - Contact depth reaches 23.4 mm at (0, 165, +15) and 11.6 mm at (0, 165, -45).
  - Held, the claimed config goes 10.5 mm deep at (30, 165, -15) and 9.2 mm at (0, 150, -30).
- **Refuted by the skeptic:**
  - P2, the held drop: content-disjoint +1.54, search-unseen +3.23, under the watch line.
  - The verifier's 6 static islands (connected reach 0.589): an artefact of a one-way kNN-8 flood. With edges in both
    directions there are 0 islands.
- **Missed, per the skeptic (process, all rows):**
  - the held set shares 32 clip frames by pose vector with the claim bench, including every overhead clip frame;
  - the directed flood can report reachable poses as islands on any row it runs on.

The three four-bar rows have no ledger entry. Their verifiers' findings are carried here at watch level:
- **cruciate-knuckle-3r:**
  - *in-band sample-weighting (auditor note):* low-floor crossed windows read 75.05 in the kit only because their
    metal floats at 9.7-11.5 mm sample spacing (rule: 4 mm). Weighted by real area they read 90.21, and the row's
    "best measured" 79.77 (k1) reads 91.28. Only kit-audit-clean numbers are quoted.
  - *follow constant:* follow is 0.8833 on every top config. The 7 lost Raise-overhead frames sit at th 24-30, below
    every window floor (~33). This is a real kinematic loss, not a bug.
  - *transmission guard [30, 150] not lowered:* lowering it would shrink a margin, which is the user's call.
- **remote-pole-fourbar-j2-3r:**
  - *missed levers, now measured:* q 0.99-0.93 gives 101.7-154.3; extra th stops of 5-20 deg give 94.5-147.1. Both
    lose.
  - *hub level:* the row lists A0 at 90 mm, but a per-pose recompute reads 100 mm at pose 93. Contact is 0, so the
    number does not change.
  - *kit `over` lift (open):* fit_profiles lifts once, before the climb limit, so the lift is not a fixed point.
    Iterated, the J1-cluster cell moves 274.37 -> 133.04 and the best is unchanged. Fixing the kit is a measurement
    change for every model that uses `over`, so it goes to the kit owner.
- **cuff-slaved-elbow-fourbar-3r:**
  - *reporting:* the claim says "honest", but the kit reports honest=False on 107.61 (the coupler is sampled at
    4.14 mm). The kit-honest best is 108.22 (verifier) / 108.36 (screen k559).
  - *search box:* the J1 / J3 seats were fixed. A seat-free ES reached 103.91, all of it reach (+4 ws), and fails the
    kit audit.
  - *gate:* re-evaluations of one best were counted; the gate still passes on 239 distinct later configs.
  - *process:* a pattern-matched `pkill -f` on the screener's own run.
- **Process, all rows:**
  - three of four verifiers again quoted the stale template bar (68.93, refute at 78.93; the lead is 18.28);
  - three of four claims never ran frozen exact, because their fast numbers were 4.5-6x the bar.

**What the round measured (lessons).**
1. **The virtual J2 is closed at the cap pole, in all three cells.** Through the same kit and bench, the plain
   cap-pole O20 3R scores 63.18 fast (56.40 frozen). Against it:
   - open four-bar: 90.11 (+27);
   - crossed four-bar: 86.95 (+24);
   - slaved elbow: 107.61-108.22 (+45).

   The kinematics are never the limit. The open cell's window covers 286/360 against the plain 281, and the crossed
   cell reaches W 101 at legal pins. The metal is the limit.
2. **Every added O20 pin is a rigid disc whose level comes from its own worst 2-3 % of poses.** So more pins near the
   J2 zone mean more tails:
   - open four-bar: A1 136-141 mm on the Raise-overhead frames against a median of 61; A0 100 against 51; B0 99-109
     against 47;
   - slaved elbow: disc edges A0 / A1 / B0 at 97-137 mm;
   - crossed four-bar: hubs 79-130 mm, 0-0.003 in band.
3. **The cap pole's binder is a zone, not a ray.** At (0..15, 150, 0) and (0, 105, 0), every part within ~25-50 deg of
   J2 is pushed to 79-130 mm.
   - A crossed cell puts metal on its own pole, the J2 ray.
   - An open cell's coupler pins roam into the zone.
   - A cell clustered within 25-30 deg of J1 keeps every member <= 76 mm on centre rays (W 91.8), but dies on layering
     (K6 rejects 99.5 % of poses; 274.37, or 133.04 with an iterated lift).
   - Bound in the plain cap 3R's link-1 frame: metal 22 deg from J1 is in band at almost any dihedral (median 0.93);
     at 40 deg the best is 0.87; on hub 2's ring (50.2 deg) the best is 0.083.
4. **A slave loop closed through the arm cannot follow internal rotation.** The loop root exists only while the
   arm-fixed pin stays in reach. Internally rotated climbs and cross-body sweeps carry it out of reach mid-motion:
   - Reach a high shelf loses 5 of 9 transitions;
   - Wash opposite shoulder loses 7 of 9;
   - follow is 0.70 on the dense path against 0.918 on the proxy.

   A pose-by-pose bench cannot see this. Any coupling loop grounded on the arm inherits it.
5. **For a plain O20 3R, the J3 seat height is a fold lever, not a proximity lever.** Hub 3 sits well on the crest
   (0.90-0.95 in band at 62 mm), but J3 on the crest (wd ~104) widens the J1-J3 angle the dyad must span:
   - p5-p95 18-137 deg, against a window of [10.5, 81.4];
   - 88/360 ws lost stretched (overhead 14/28, across the body 48/68);
   - the best gap rises steadily with wd: 37.9 / 45.2 / 60.4 / 77.1 at wd 100-120.

   The round-4 "crest basin" was an artefact of O15 hubs and the 10-deg margin: with equal arcs, hub 2 sat 0.82-0.997
   in band at O15 and sits 0.02-0.07 at O20.
6. **At the crest seats, Bench(60,160) over-reads by 11-14 points; at the zc seats the gap is +2.2.** Pairs:
   36.63 -> 47.86, 29.85 -> 43.99, 28.63 -> 41.04, 26.78 -> 40.17. The fit bench under-samples the stretched poses the
   window costs. Searches at any new seat should run on the envelope bench, or pre-register a fast-to-frozen check.
7. **Proxies overstate four-bar cells by 130-240 points.** Lens 1's proxy (centre rays only, no layering, no K6, no
   O20 disc edges):
   - proxy 42.34 -> kit 103.72; proxy 63.38 -> kit 79.77;
   - centre-ray hub levels are 15-60 mm optimistic for roaming pins.

   Loop and four-bar mechanisms need the kit in the search loop from the first config.
8. **The four-pose binder test is necessary, not sufficient.** A minimax search clears it at 67 mm in ~2 min (the
   judge's 90000 random layouts missed it), then the binder moves to the median and p90 poses (B1 94 / 126 mm).

**The 3-joint picture after rounds J1 and J2 (for the lead's ceiling statement).**
- No jump-track class has beaten the 17.5 gate: 0 of 9 designs in J1 and J2.
- At the legal seats:
  - the back seat's plain 3R is kinematically capped at 250/360;
  - the back-seat knuckle family is capped at 269-271 takes (ghosts with an ideal drive);
  - the cap pole reaches 281/360 kinematically, but every J2 realisation fails its zone:
    - revolute J2: hub 2 <= 0.12 in band over 668 configs;
    - virtual J2: >= 86.95 fast in all three cells;
    - plain J3 on the crest: 40.17 frozen.
- 95 needs 279/360 at the lead's in-band.

**Next focus (round J3, track jump).** The score has not reached 95. The best verified gap is 18.28 (conecut, WATCH),
and 95 needs 13.75: +17 takes, to 279/360, at ib14 >= 0.90 and the lead's contact.

Close these in the catalogue, with the numbers above:
- virtual-J2 cells at the cap pole (open, crossed, slaved, clustered);
- arm-grounded coupling loops;
- plain crest-J3 3Rs;
- proxy-only screens of loop mechanisms.

Two 4-joint ghost gates, like-for-like against the lead. The 3-joint classes at legal seats are measured capped
(above). The user prefers 3, so any claim says so.
- **Lens A, a ghost J0 relay under the lead's verified chain** (conecut's frozen shape; a zero-size J0 at the legal
  seats, back of the shoulder / acromion top; continuity flood; frozen exact Bench(110,360)).
  - *Measured reason:* round J1's ghost J0 under the pin-knee host bought 5.0-5.3 fast points (23.64 -> 18.30 front /
    18.62 seat-legal) on a back-seat host whose losses are also mostly fold. The lead loses 88 poses to fold (stretched
    73, 64 of them internal rotation >= 90 across the body). +17 takes is the 95 line.
  - *Gate:* ghost <= 15 or >= 279 takes with <= 4 contacts. Otherwise the relay class is closed for good, with the
    number.
  - *If it passes:* the hardware question is J0's metal against hub 2's orbit. Per J1 lesson 5, that needs a1 <= ~20
    deg or a J0 that sits clear of the orbit. Measure it before modelling.
- **Lens B, the redundant-4R null-space ghost at the cap pole.** Four O20 hubs at real height. Per pose, the
  null-space is chosen for clearance, under the continuity flood (no joint jump > 10 deg per 2-deg step, no branch
  change). The 4th hub is parked on the acromion top (bony, 2-5 mm skin spread), not the deltoid.
  - *Measured reason:* the cap pole is the only legal seat with kinematic reach >= 0.78 (281/360). Its sole failure is
    hub 2's zone (0.181 of closing poses exit > 75 mm), which a revolute 3R cannot move per pose. A null-space can.
  - *Precedent:* the redundant 4R's kinematic headroom is ~1.0. Its cost was entirely parking (hub 4 0.51 in band when
    on the deltoid), and that was never measured with hub 4 on the acromion top.
  - *Gate:* as lens A.
  - *If it passes:* determination is the next question (spring-centred + stops; a free spare sags within 0.1 s).
- **Machinery before the next claim:**
  - set the verify template's bar to 18.28 (stale in 3 of 4 verifications);
  - zc-frontier evaluate() objective -> the near-touch gap (T1);
  - make the continuity flood's kNN edges bidirectional (the skeptic's islands refutation);
  - de-duplicate the held set against the claim bench by pose vector (32 shared clip frames);
  - in-band weighted by real area for members sampled sparser than 4 mm;
  - the kit `over` lift iterated to a fixed point (a measurement change; announce it);
  - every claim message's numbers come from the row file, kit-honest only.

### Needs the user's say (unchanged, now with J2's numbers)

- The 4-joint question: every 3-joint class at the legal seats is measured at >= 18.28 (above). Lenses A / B give the
  4-joint class's ghost number like-for-like before the lead asks.
- The transmission guard [30, 150] and the J1 seat rule stay as they are. No lens relaxed them, and cruciate's
  low-floor windows would need the first.

## Round 103 plan (Round J3, track jump; 2026-10-18 ~00:55 UTC, lead verified gap 18.28)

Planner's read at 00:40-00:55 UTC: ROUNDS.md (J1 / J2 results, round 14 plan), rows/*.json, events.jsonl tail,
catalogue, acromion-relay-4r.md, arm-parked-knee-4r row, tools/simplicity.py v2.2. Ledger re-read
(`tools/alignment_ledger.py latest`): gamed = dipped-law-groove-knuckle-3r (fold margin 0.184), seed-offset-3r-slides;
every other audited row WATCH. This round answers the J2 closer: two 4-joint ghost gates, like-for-like against the
lead. **The user prefers 3 joints; every claim from this round says it is a 4-DOF design and compares with the 3-joint
lead and with the 4-DOF rows (minarc-stop-knuckle-4r 18.40 polished / 19.54 verified, arm-parked-knee-4r 26.71).**

### State

- **Lead (best verified, not gamed): conecut-knee-knuckle-3r 18.28** (score 93.35) frozen exact Bench(110,360), held
  22.38; reach 0.7278 (262/360), ib14 0.9012, follow 1.0, contact 0.0106 (4 poses), overhead 8/28, 3 active, 0 passive
  translations, cx 18.5. Config: stk 6.0, lE 97.14, lc 24.35, phiE 0.75, phib -91.80, J3 window [-111.90, 122.74].
  WATCH (carry into every summary that names it; no lens may buy points the same way): reporting (sweep 12.5 shown as
  95.45); T1 (16.56 points of the bench claim live in the 1-2 mm shell; pose 203 taken at 0.263 mm); T3 (held th
  margin 5.006, a +-0.3 deg K-phase error crosses 5; the J3 dowel's held number holds in a 1.33-deg window);
  NEW-strap-dilution (18.67 at the displaced lead's strap sampling); P2 (held poses read by the knee prefilter, measured
  effect nil); M5 (J3 stop returns 155 N per N.m through MR117 bearing 1); NEW-self-reference (T5 reference swap).
- **Others at the lead's reach:** slipper-nose 18.49 (cx 18.25), trimlug-k165 18.51, roller-longdyad 18.67,
  desmo-slipper 18.95 (cx 15.75), desmo-conecut 18.98 (cx 16.5). Complexity frontier: cx 0 pin-knee 23.64 (current
  checks; verified 27.2), crest-knee-3r 32.84 frozen (main r14, cx 0); geneva-tail-pinknee 23.57 at cx 12.
- **95 arithmetic** (tools/concept_bench.py gap_of): reach 0.7731 = 279/360 at ib14 >= 0.90 and the lead's contact
  (+17 takes); 282/360 at ib14 0.88 and 0 contact. In-band above 0.90 buys nothing.
- **Where the lead loses poses (98 of 360):** fold 88 = stretched 73 (th 107-176; 64 of them internal rotation >= 90
  across the body; the stretched wall is the K drive's stroke, dK 52.6 of the 57 cap) + folded 15 (th 7.7-22,
  scapular-plane overhead); J3 stop 6; contact 4 (237 / 205 / 316 / 264). Overhead 8/28: fold 14, contact 3, J3 stop 3.
- **3-joint ceilings at the legal seats (measured):** back-seat plain O20 3R 250/360 kinematic; back-seat knuckle
  ghosts (ideal drive) 269-271 takes (proximal-j3 16.52 / 271 / 4 contacts but < 274 bar; desmo-vrocker 17.23 / 269 /
  6; long-dyad 17.86 / 269 / 8); cap pole 281/360 kinematic (267 metal frozen; T-0 56.40) but every J2 realisation
  fails its zone (revolute hub 2 <= 0.12 in band over 668 configs; virtual J2 86.95-108.22 fast; crest J3 40.17
  frozen); cap-pole knuckle (main r14 cap-plateau-knuckle-3r, 00:27): control 26.24 fast / 33.19 frozen, cells C 43.77
  and B 47.76 frozen, pre-registered KILL. Cap-pole J2 ray: exit p95 107 mm, 0.181 of the 281 closing poses > 75 mm.
- **4-joint precedents (what this round builds on, not repeats):**
  - Ghost J0 under the pin-knee host H1 (J1 verifier): 23.64 -> 18.30 fast (front seat) / 18.62 (seat-legal), 40
    placements a0 15-60 x azu 0-315 at T 60. With real metal every J0 placement jams on hub 2's orbit about J1
    (radius a1 + ~25 deg, covers every allowed seat): a relay needs a0 <= ~20 or J0 inside J1's footprint.
  - acromion-relay-4r (J0 under the plain cap 3R, least-|q0| clamp policy): +4.57 frozen (+17 ws, 0 overhead), in-band
    +0.001, hub 2 <= 0.12; max |q0| 38.5 deg. The relay never engages at the binder poses (J2 strictly inside its
    stops there, so q0 = 0): a clamp policy cannot move hub 2 by construction. A CLEARANCE-chosen null-space was never
    run.
  - arm-parked-knee-4r (spare hub on the deltoid, spring-centred): frozen reach 0.772 (the 95 line) at ib14 0.799;
    hub 4 0.51 and link 3 0.32 in band; cx 32.25. park4 (spring-centred, back seat) 22.36 self-measured. K as the 4th
    joint (minarc, skinnormal-shortk-4r 18.58): 1:1 fold for contact.
  - Complexity: any 4th DOF costs +25 (tools/simplicity.py v2.2 active_extra, "a spare freedom in MVP1"), so a 4-DOF
    95 is cx >= ~28; the golden (95 at cx ~0) stays a 3-joint question that the measured caps above answer "not at
    these seats".
- **Dead on this track (J1-J2, 0 of 9 under the 17.5 gate):** rigid arm rings (>= 72.2), 2R pointer + arm-axial J3 /
  spars (sleeve ghost 101.02), arm-fixed races (44.53), base relays on plain O20 hosts with a1 >= 40 under a clamp
  policy, virtual-J2 cells at the cap pole (open 90.11, crossed 86.95, slaved elbow 107.61-108.22 fast), arm-grounded
  coupling loops (follow 0.70), plain crest-J3 3Rs (40.17 frozen), proxy-only loop screens (130-240 points optimistic).
  Main-track closures stand (knuckle drive / law / flank / lobe / seat variants are not this track's).
- **Machinery open before the next claim (J2 closer):** verify template bar -> 18.28 (stale in 3 of 4 verifications);
  zc-frontier evaluate() -> near-touch objective (T1); continuity flood kNN edges bidirectional (tools/spare_flood.py
  and the kit's connected(): the skeptic's islands refutation, 6 -> 0); held set de-duplicated against the claim bench
  by pose vector (32 shared clip frames incl. every overhead clip frame); in-band weighted by real area for members
  sampled sparser than 4 mm; the kit `over` lift iterated to a fixed point (a MEASUREMENT change: announce it and
  re-wear the lead under it); claim numbers from the row file, kit-honest only.
- **Compute:** farm CLOSED (CLAUDE.md (7)); local only, niced, <= 2 processes per agent, OMP_NUM_THREADS=1.

### Lenses

1. **LENS relay-under-lead (reach; 4 DOF; suggested id lead-relay-j0-4r).** A spare J0 on bony scapula skin under
   conecut's FROZEN verified chain (the config above, no refit of the 3R, its knee, K law and J3 window unchanged).
   - *Measured reason:* J1's ghost J0 bought 5.0-5.3 fast points on H1, whose losses are also mostly fold; the lead's
     88 fold losses are the 95 gap (+17 takes needed), and J0 tilts J1's axis so the same arm pose needs a smaller th.
   - *Gate 0 (<= 45 min, ghost J0 = zero-size, then its O20 stack):* legal seats only (back of the shoulder /
     acromion top, J1 seat rule); a0 in {15, 20, 30, 45, 60} x J0 azimuth 0-315 step 45 x travel T 30 / 45 / 60.
     Two policies, both reported: (i) per-pose free q0 within T (the bound); (ii) the realisable spring-centred clamp
     (q0 = 0 while the chain closes at th margin >= 5 incl. K play; else the least |q0| that closes, J0-J1-J3
     sub-chain margin >= 5, J0 stops as own-angle dowels). Continuity flood with bidirectional edges (no J0 jump > 10
     deg per 2-deg slerp edge, no K-branch change); frozen exact Bench(110,360); report static and connected
     taken / 360, overhead / 28, contacts, min th margin, which of the 73 stretched / 15 folded / 6 J3-stop losses are
     relayed, and the gain as a function of a0.
   - *Pass (pre-registered):* policy (ii) <= 15, or >= 279 taken with <= 4 contacts, at a0 <= 20 (J0 stackable inside
     J1's footprint), or at a larger a0 only with hub 2's measured orbit clearing J0's O20 stack + 5 mm on every taken
     pose. *Kill:* policy (i) > 17.5 at every a0 -> relays under the knuckle closed with the number.
   - *If it passes:* J0's metal (O20 stack + spring) against hub 2's orbit, measured before any CAD; feel (spring
     torque at the relay poses as cuff force; the twin cell of acromion-relay was felt on 189-192 / 201 poses).
     Complexity ~18.5 + 25 + 2 + 3 (spring) + parts ~= 49; state it beside the score.
2. **LENS clearance-nullspace-4r (reach AND the low-complexity cell of the 4-DOF class; suggested id
   cap-nullspace-4r).** A plain-pin redundant spherical 4R at the cap pole (four O20 v5 hubs on MR117 pairs, 3 mm bent
   bars at real height; no drive, no lobe, no knuckle), Keemink 2018 (TNSRE 26(4)) with the null-space resolved for
   CLEARANCE, the one policy no row has run; the spare hub parked on the acromion top (bony, 2-5 mm skin spread), never
   on the deltoid (arm-parked: 0.51).
   - *Measured reason:* the cap pole is the only legal seat at >= 0.78 kinematic reach (281/360); its only failure is
     hub 2's zone (0.181 of closing poses exit > 75 mm), which a 3R cannot move per pose and a clamp relay never
     moves (above). A null-space slides J2 along its a2-circle about the arm-fixed J3.
   - *Step 0 instrument (<= 15 min, no hardware; the bound for ANY null-space at these arcs):* for each of the cap
     control's 281 closing ws poses (J1 bvec(43.2, 59.9), a1/a2 50.2/60.3, J3 wdir(92.0, -9.0)), sweep J2 along the arc
     of its a2-circle that the spare dyad reaches with >= 5 deg margin in both sub-chains (base J0 on the acromion top,
     the spare hub on its a0-circle, a0 15-40, kept inside the acromion-top / back seat region), K3-march the J2 ray's and the spare hub's skin exits at 2-deg steps, and report the share of poses with
     a point where both exit <= 75 mm (cap control: 0.819) and the continuity of the min-exit choice. *Kill at step 0:*
     share < 0.95 -> the null-space class is closed at the cap pole with the number (write it to FINDINGS).
   - *Gate 0 if step 0 passes:* ghost wear with all four O20 stacks and links as metal, null-space per pose = min over
     the arc of the worst member requirement, under the bidirectional continuity flood; fit on the envelope bench (the
     crest seats over-read Bench(60,160) by 11-14), frozen exact Bench(110,360); then the realisable MVP1
     determination (spring-centred spare + own-angle stops, least-energy) - report both, and their difference as the
     price of an unpowered null-space. Same pass / kill as lens 1.
   - *Complexity if built:* 25 + 1 body + 1 joint + ~1.5 parts (+3 with a centring spring) ~= 28-31 - no drive or
     lobe, the simplest 4-DOF realisation on file (arm-parked 32.25, minarc 32.5, lens 1 ~49).
   - *Red team:* sag (a free spare drops within 0.1 s; the clearance policy is what MVP2's cables enforce, the user's
     context only, not a metric); the spare hub on the acromion under shrug / overhead; the two-sub-chain fold.

No third lens: the 3-joint low-complexity cells at new seats (crest-knee-3r cx 0, slotted-eccentric-pin-knee-3r) are
main round 14's and running; every other 3-joint class at the legal seats is measured capped (State).

### Carried (ideated, never screened)

- None this round. The round-4 picks are done or running in main (deltoid-crest-j3-3r dead 40.17 frozen; crest-knee-3r
  32.84 frozen; slotted-eccentric-pin-knee-3r modelling since 00:38). The other 20 ideated entries fall under measured
  closures: hubless / rolling / thin-ring joints (O20 only; rings >= 72.2), spherical parallel / five-bar / tripod
  loops (seed-spm 193; J2 lesson 2: every added O20 pin is a disc levelled by its own worst 2-3 % of poses; lesson 7:
  loop proxies 130-240 points optimistic), offset-axis skin hubs (3 passive translations), strap / tape / lame J2s (no
  real component at size).

### Elsewhere, not to be duplicated

- Main round 14: slotted-eccentric-pin-knee-3r (modelling), cap-plateau-knuckle-3r (gate-0 KILL at 00:27; cell C
  search still writing), lowarm-halfring-knuckle-3r (pick 1), crest-knee-3r (screened 32.84 frozen; verification next).

### Needs the user's say (unchanged)

- The 4-joint question: lenses 1-2 give the 4-DOF class its ghost numbers like-for-like before the lead asks. The
  transmission guard [30, 150], the J1 seat rule and the 5-deg fold margin stay as they are.

## Round 14 results (2026-10-17 ~21:45 - 2026-10-18 ~03:05 UTC, track main, closer)

All numbers are frozen exact on Bench(110,360) (fit on Bench(60,160) fast, shape frozen, worn with no refit) and were
re-measured by an independent verifier. Ledger exits were re-read with `tools/alignment_ledger.py get <id>` at 03:05 UTC,
just before naming the winner:
- crest-knee-3r exit 0: WATCH (skeptic 02:45:19Z).
- slotted-eccentric-pin-knee-3r exit 0: WATCH (skeptic 02:50:50Z).
- deltoid-crest-j3-3r exit 0: WATCH. That entry (00:32Z) is for its 47.86 claim; the 34.98 audit re-wear has not been
  audited.
- **lowarm-halfring-knuckle-3r exit 3: GAMED** (skeptic 03:00:45Z, P1 upheld).
- cap-plateau-knuckle-3r exit 2: no entry (dead, not audited).
- The lead, conecut-knee-knuckle-3r, exit 0: WATCH.

Complexity is tools/simplicity.py v2.2. Every row has 3 active joints and 0 passive translations. The farm was closed (the
budget line was reached), so every screen, verification and audit ran locally (<= 2 niced processes). No bench, judge or
kit file changed this round, so no number moved because the measurement changed.

| design (lens) | verified gap (score) | held out | reach (takes) / overhead | cx | ledger | outcome |
|---|---|---|---|---|---|---|
| **crest-knee-3r** (3, crest-pinknee-cx0: plain O20 3R + two-pin MR63ZZ cuff knee at the crest seats, J3 own-angle window) | **32.84 (88.06)**; claim reproduced to the digit | **29.81** (28.13 with every frame shared with either bench removed) | 0.6333 (228/360) / 5 of 28 (held 6/26) | **0** | **WATCH** (4 upheld, 2 refuted) | **winner by the rule**. Not a lead (+14.56 behind 18.28; +5.64 behind H1's 27.20 on the same bench). Over the lens's pre-registered kill line of 23.64. The screen stays "verified", not "dead", because its convergence gate fails (last-third gain 0.62 > 0.5) |
| lowarm-halfring-knuckle-3r (1, knuckle-o20-overhead: half ring + low arm + link-2 root lift, cell B) | 17.96 (93.47) reproduced | 22.70 (lead 22.38) | 0.7306 (263) / 9 of 28 (held 19/71) | 16.5 | **GAMED** (P1) | **passed over as gamed** |
| cap-plateau-knuckle-3r (2, cap-seat-ulaw: cell C, two-sided dwell K law at the cap pole, paired kit) | 32.08 (88.33): ghost drive, no drive metal and no cuff knee in the model | 35.16 | 0.6861 (247) / 9 of 28 (held 23/71) | 17.5 | no entry | DEAD at gate 0 (247 takes vs the pre-registered 279); passed over as a ghost |
| deltoid-crest-j3-3r (carried; lens 3's no-knee control) | 34.98 (87.28) on the audit's re-wear (s12 basin, end_extra 8); the claim config read 40.17 | not read at 34.98 | 0.606 (218) / 6 of 28 | 0 | WATCH (on the 47.86 claim) | DEAD on the spec's kill bar (32.10); convergence gate passed |
| slotted-eccentric-pin-knee-3r (carried; lens 3 cell B) | 201.20 (26.84) | - (held reach 0.192) | 0.181 (65) / 0 of 28 | 5.0 | WATCH (7 upheld, 4 refuted) | screened, not dead (its convergence gate is open); the second refutation of the slotted-eccentric family |
| conecut-knee-knuckle-3r (the lead, reference) | 18.28 (93.35) | 22.38 | 0.7278 (262) / 8 of 28 | 18.5 | WATCH | stays the verified lead |

**Winner: crest-knee-3r, v_gap 32.84 (score 88.06), held out 29.81, complexity 0, 0 passive translations, ledger WATCH
(exit 0; final skeptic verdict 2026-10-18T02:45:19Z). It does NOT beat the previous verified lead of 18.28
(conecut-knee-knuckle-3r stays the lead, 14.56 points ahead). No lead change.**

Two designs were passed over:
- **lowarm-halfring-knuckle-3r (17.96, the round's best verified number) is GAMED (P1 upheld).**
  - The number holds: the verifier reproduced 17.96, and three independent wears agree.
  - Its rank above the lead is an in-sample pick that does not hold out. The link-2 root lift (h 1.5, r_full 14,
    L 9.836) is the minimum of 794 frozen-exact surrogate configs scanned on Bench(110,360) exact, the claim bench
    itself. The spread of that scan: min 17.96, p10 18.07, median 18.42; 251 of 794 beat 18.28.
  - The whole bench edge is one pose: 316 (plane 60, elev 150, axial -105), cleared by 0.048 mm.
  - Held out paired against the lead it is 0.32 WORSE: 22.70 vs 22.38, CI90 [-0.34, +0.68], P(better) 0.26. Pooled
    over bench and held out it is 0.13 worse.
  - The hard-pad build fails the claim's own dwell-hold gate: 0.638 deg of K play against 0.25.
- **cap-plateau-knuckle-3r (32.08) is a lower number than the winner, but it is not eligible.**
  - Its two-lobe K drive does not exist. 19 of its 247 takes sit on the folded lobe, and without that lobe cell C takes
    260/360 kinematic, not 275. The verifier puts a buildable one-sided version 4-5 points worse, at about 36-37.
  - It is a paired-kit number with no drive metal and no cuff knee, and its row is dead at its own gate 0.
  - "Every joint maps to a real component" (CLAUDE.md, manufacturable joints) rules it out. Round 13 passed over
    proximal-j3's ghost the same way.
  - Held out it is also worse than the winner (35.16 vs 29.81).

**Lens outcomes against the pre-registered bars:**
- **Lens 1, knuckle-o20-overhead (lowarm-halfring-knuckle-3r).**
  - Target <= 17.5 at cx <= 16.5: MISSED (17.96, and gamed).
  - Floor, cell A <= 18.28 at cx 16.5: met on the number only. Cell A (half ring + low arm, zr 2.0) reproduces 18.28 three
    times, with the same 262 takes and 4 contacts as the lead, held 22.64 (proposer, same code path), at cx 16.5 vs 18.5.
    But its hard-pad dwell hold fails the 0.25-deg gate (0.638 nominal, 0.292 at 5-10 micron tolerances). It stands only
    with a preloaded pad, whose preload (estimated 5-36 N) and J2 drag (~0.07 N m) are unmeasured. Cell A was not
    verified separately.
  - Cell B's kill fired: it clears < 2 contacts. Only 316 cleared, by a 0.048-mm graze. 205 (hub 2 -4.28 mm), 237 (crank
    -9.47) and 264 (hub K -1.17) are unchanged.
  - Machinery items closed: the stage-1 built-groove PA holds at mu 0.17 over 9 tolerance corners (first fail at K
    52.89, gate 47.27); slot slop 0.04 deg; link 2 clears the crank arm by 12.32 mm.
  - Still open: RC_MIN (rc_min 1.0, ridge 0.243 mm); crank-free worst-tolerance slop 0.27 vs 0.25; slot end dK_lim 46.0
    vs the plan's 46.3 (bench max taken 45.62).
- **Lens 2, cap-seat-ulaw (cap-plateau-knuckle-3r): DEAD at gate 0, the cap-pole knuckle is closed.**
  - In the same paired kit, the lead's own seats and law take 277/360 kinematically; cells C, B and A take 275, 270 and
    294.
  - Real-model takes: C 247 against the bar of 279. The lead-seat control: 259 takes, 30.59 frozen, 34.03 held.
  - Cell A puts hub 2 at 0.04 in band. Cell C's box holds configs at 299 kinematic, but a metal search started there
    walked back to 275 and ended 4 points worse.
- **Lens 3, crest-pinknee-cx0 (crest-knee-3r): over the kill line** (bar <= 21.0; kill at > 23.64; frozen 32.84).
  - On Bench(60,160) the crest seat cuts fold losses from 48 to 16-24 of 220. But J3-window stops rise from 5 to 17,
    because member 3 sweeps into the skin over the crest. Total losses stay at 48-55 of 220 for every wa, against H1's 51.
  - The next lever is a joggled knee link, bounded at about 25-27 frozen: not a 95 path.
  - The no-knee control (deltoid-crest-j3-3r) died at 34.98, and the slotted eccentric at 201.20, 142.7 behind its own
    locked control.

**Generation CAD (the lead's call).** Under the standing rule, the round's winner, crest-knee-3r, is owed an L2 CAD. Its
build is H1's pin-knee CAD (pipeline/conformal/param_cad/user_style_pinknee.py) re-seated to J1 bvec(106.32, 62.87) and J3
wdir(93.04, -1.37), with the fitted E strap and J3 window. It is a cx-0 design 14.56 behind the lead, and the gen-9
desmo-conecut CAD is still being built, so whether to build this one before a better row lands is the lead's call.

**Alignment.** Every watch reason of the round's designs is carried here as upheld by the skeptic, with its numbers.
- **crest-knee-3r: WATCH, 4 upheld, 2 refuted.**
  - Refuted: *continuity* (959 of 959 connected, 0 islands; a stricter one-seed flood also connects all 959 and drops
    nothing) and *P2* (with every frame shared with either bench removed, held out reads 28.13, better than 29.81).
  - *reporting*: the row's verdict text still reads as the screen's ("SCREENED, below the lens bar").
  - *R2*: docs/dashboard/data/morphs.json shows gap and sweep_gap 26.34 (score 90.42), the in-sample fast best of 531
    configs. That is 6.50 below the verified 32.84; the out-of-search held reads 30.88. There is no rank effect: the
    board ranks by v_gap.
  - *G1* (report-only): overhead reach is metal at the skin.
    - Bench: 5 of 28 taken, lowest metal 0.59 / 0.96 / 1.23 / 1.72 / 2.10 mm. Held out: 6 of 26 taken, at 0.02-1.45 mm.
    - All 10 Raise-overhead clip frames sit at 1.08-1.85 mm.
    - Taken poses under 2 mm: 34 bench / 34 held; under 1 mm: 6 / 10; under 3 mm: 77 / 83. The 1-2 mm shell holds 25.14
      points of the claim.
  - *NEW-ws-inband*: unscored in-band on taken workspace poses is 0.793 bench and 0.775 held, against 0.853 on the scored
    clip frames. 20.5 % of that metal is above 14 mm (max 27.7 mm). That is the lowest of 18 audited probes (H1 0.867, the
    lead 0.868). The knee link is 0.628 in band, median 12.9 mm.
  - Also carried (verifier): bench contact 5 poses, depth sum 6.40 mm, deepest -2.77 mm (281 and 338, elev 75-90); held
    out 6 poses, 4.80 mm, deepest -1.63. Held min th margin 5.33 deg; min J3-window margin 1.00 deg. The fold still owns
    22 of the 27 workspace poses with |axial| >= 150.
- **lowarm-halfring-knuckle-3r: GAMED** (P1, above), with 8 watch reasons upheld and NEW-string-params refuted.
  - *continuity* / *S5*: the rule's flood loses nothing (17.96 / 22.70). The kNN flood reads 19.64 bench (-1.68) and
    30.93 held (-8.23), and the bench-graph flood 49.98: forced poses connect only through the envelope sample.
  - *T1*: all 251 scan configs that beat the lead clear 316 by only 0.014-0.197 mm. The best config with at least 0.1 mm
    of clearance reads 18.24.
  - *R3*: the 17.96 is the best of 794 configs, shown without its spread (p10 18.07, median 18.42).
  - *M5*: K play 0.638 deg vs the 0.25 gate. The fold margin survives it (min 5.088, 0 poses dropped). Unmeasured: the
    metal shift at near-touch poses 316 and 139 (taken at 0.072 mm), and the drag of the preloaded pad.
  - *M3*: the verifier's promised V5 check was never implemented. The lifted link 2 is on file at 12.32 mm from the crank
    arm. The tip plate, hub-2 crown and root-in-stack clearances are unmeasured.
  - *S3*: the crank stop pad on link 1b is unsampled metal.
  - *G4*, now measured on this row: m_sub at K rest is under 1 deg on 50 of 205 rest poses, identical to desmo-conecut.
    B1 is the user's call.
- **slotted-eccentric-pin-knee-3r: WATCH, 7 upheld, 4 refuted.**
  - Refuted: fold_margin (min th margin 15.80 bench / 17.30 held), S2, G1 and R1 (201.20 reproduced in three wears).
  - *fast_frozen*: 153.49 fast -> 201.20 verified (+47.71). +34.98 of that is the search's laxer 0.5 mm part-part rule.
  - *continuity* / *S5*: no flood is on file. The slot track's end at th 74.0 blocks the rest region: 82 of 110 clip frames
    and 72 of 128 workspace poses at elev <= 30 fall below it. A bench-graph upper bound already loses >= 10.56.
  - *sampling*: hub 2 is 0.00 in band, the crank 0.36 and L2b 0.27; they ride 16-20 mm off the skin.
  - *reporting* / *NEW-dishonest-sweep-best*: the dashboard's sweep best of 97.45 (score 64.56) is AUD-g9-2, an audit
    probe the model flagged honest=false (ib14 0.21). tools/dash_build.py never reads the honest flag.
  - *S3*: the cuff pin knee in the row's name is not in the model; member 3 is the kit neck, the pessimistic side.
  - Verifier's notes: at the parent's seats the O20 knee IS the killer (O10 70.07 vs O20 209.85 fast). The knee hub is
    never stacked over link 1, an over-strict check (fixed in a probe: 209.85 -> 160.72; the best config is unchanged at
    153.86).
- **deltoid-crest-j3-3r: WATCH** (ledger entry on the 47.86 claim; the 34.98 re-wear was not audited).
  - *reporting* / *R2*: the dashboard sweep best of 26.78 (score 90.26) sits 13.39 below the frozen 40.17 at the same
    config.
  - *T1*: the plain-gap objective parks metal just past the 0 mm contact cutoff.
  - *G1*: the 4 overhead poses taken on the claim bench have metal at 0.13-1.34 mm (2 of 28 at the 1 mm reading; held
    out 0 of 26).
  - Audit: fast rank fully inverted frozen. The box cut end_extra at 6.0 against the rule bound of 8.0 (+0.64 frozen
    when opened). Part-part: hub2-neck 10 poses overhead, hub1-hub3 and hub1-link2 9 each at elev 30-45.
- **cap-plateau-knuckle-3r: no ledger entry** (dead). Verifier notes, carried:
  - The row mis-attributes its limiter. Exempting link 2 x neck makes it WORSE (35.65): the 14 freed poses already have
    metal 0.34-10.77 mm in the skin. The real limiter is skin proximity.
  - 19 takes ride the folded lobe of a drive that does not exist.
  - The convergence gate is degenerate: chained streams, top 5 are neighbours, and the one independent start ended
    worse.
- **The lead, conecut-knee-knuckle-3r: WATCH, unchanged** (carry into every summary): reporting (sweep 12.5 shown as
  95.45); T1 (16.56 points in the 1-2 mm shell; pose 203 at 0.263 mm); T3 (held th margin 5.006, K play ~0.23 deg takes it
  near 4.92); NEW-strap-dilution (18.67 at equal strap sampling); M5 (the J3 stop returns 155 N per N.m through MR117
  bearing 1); NEW-self-reference; G4 (B1).

**Lessons (measured).**
1. **The main track's 3-joint seat question is closed at every legal seat measured.**
   - Back of shoulder: the knuckle ghost ceiling is 269-271 takes (rounds 12-13).
   - Cap pole: 275 kinematic and 247 on metal, with no surplus over the lead's own seats (277 kinematic in the same kit).
   - Deltoid crest: pin knee 228 takes frozen, no knee 218.
   - At 271 takes, 0 contact and ib14 >= 0.90 the gap floor is 14.72 (score 94.65), still above 13.75; 95 needs 275 takes
     at zero contact or 279 at the lead's contact.
   - Reach did not move for the fifth round: the best non-gamed verified take count is still 262.
2. **Kinematic surplus is paid back in metal.**
   - Cap C's box holds 299 kinematic, but a metal search walks back to 275.
   - The crest seat's fold gain (48 -> 16-24 of 220) comes back as J3-window stops (5 -> 17), where member 3 sweeps over
     the crest. Totals stay at 48-55 of 220 against H1's 51.
   - Count takes on metal, never kinematic takes against a metal ceiling.
3. **A flat two-pin knee cannot serve pin sites over skin of different heights.**
   - At the fold-free end, the E boss and the arm pad share one level, and the skin under them does not. In band: boss
     0.43 / pad 0.85 at wa -0.99, or boss 0.88 / pad 0.04 at wa -0.72.
   - The fix is a joggled knee link, bounded at about 25-27 frozen.
4. **At the crest, the knee buys about 2 frozen points, not the ~25 the no-knee control said it must.**
   - crest-knee 32.84 vs deltoid-crest 34.98, at neighbouring seats: J1 bvec (106.3, 62.9) vs (108.6, 64.5), both on the
     acromion top.
5. **At fold-limited seats, fast rank inverts frozen rank, and fitted stops lose half their value.**
   - deltoid-crest: 26.78 fast -> 40.17 frozen, while 29.59 fast -> 34.98. crest-knee: 26.34 -> 32.84.
   - A J3 window fitted on 160 poses stops twice as many on 360 (15-17 of 220 vs 29-32 of 470).
   - Wear the top 3-4 distinct fast basins frozen on the envelope-selection draw (not on Bench(110,360)) before claiming.
6. **Selection on the claim bench is gaming even when every number reproduces (lowarm, P1).**
   - The frozen-exact per-sample surrogate is the right instrument: replace one part's distance segment and re-run
     Bench.report, about 0.1 s per config, matching the full model to 0.00.
   - But scanned on Bench(110,360) it picked a 0.048-mm graze that held out did not keep (22.70 vs the lead's 22.38). It
     must scan the envelope-selection draw.
7. **A dwell stop that replaces a one-part groove wall must be read through the drive ratio.**
   - 17.6 deg of K per mm at the stage-1 pin, and a pad lever of at most 12.3 mm, give 0.638 deg of K play (0.292 at
     5-10 micron tolerances).
   - The 0.01-mm groove wall was doing real work. The "free +0.67" of cell A needs a preloaded pad.
8. **Radial lifts are dead for link 2 too.** At pose 316 the skin runs parallel under ~18 mm of link 2. A root lift
   grazes it (+0.048 mm), and a robust 0.2 mm clear is a whole-bar lift that costs in-band 1:1 (18.41).
9. **The fast Bench(60,160) holds none of the family's four contact poses** (205 / 237 / 264 / 316), so a fast search
   is blind to contact levers.
10. **The slotted eccentric on a J2 crank is closed (twice).**
    - The roller track lies in hub 2's annulus [b - dG, b + dG], the same annulus the knee hub sweeps. So at O20 the
      knee, crank and track cross link 1: 88-100 % of closing poses collide.
    - Paired deficit +142.7 frozen against its own locked control.
    - A cuff-side closure cannot fix a fold lever placed between J2 and J3.
    - The kit neck costs about 10 points against the two-pin knee (36.83 vs 27.20 at H1's directions).
11. **Process.**
    - The dashboard shows sweep bests the model flagged dishonest (97.45).
    - The verify template's bar is still 68.93 / 75.94; every verifier applied the spec's bars by hand.
    - A row kept the screen's verdict text after verification (crest-knee).
    - A model box edge sat inside a rule bound (end_extra 6 vs 8, +0.64 frozen): box edges equal the rule bounds in both
      directions.
    - A J3 window was fitted on the search bench.
    - A convergence gate was passed by chained streams with one start; it needs >= 2 independent starts.
    - slotted-eccentric's gate needs ~165 more no-gain evals.

**Next focus (round 15).** The score has not reached 95. The best verified, non-gamed gap is 18.28 (conecut-knee, the
lead); 95 needs 13.75. This round closed the last two 3-joint seat families the main track had open: the cap-pole knuckle
(no kinematic surplus over the lead, 247 metal takes) and the crest pin knee (32.84 at cx 0). With the back seat's
269-271 ghost ceiling, no measured 3-joint cell at the legal J1 seats has a metal path to 275 takes (zero contact) or 279
(the lead's contact). The next round should:
- **Lens A (bound first, 1 slot): write the 3-joint take bound as one table from the files on disk.** One row per seat
  family (back, cap, crest, antcrest), with its kinematic window takes, its best ghost / metal takes, its best verified
  takes and the gap floor at zero contact. The jump track's round-103 4-joint gates report against that table. If no
  family reaches 275 metal takes, the lead takes it to the user as a blocker (a big update): **95 at 3 DOF is measured out
  of reach at the back + acromion-top seats.** The options are a 4th joint (the cap allows it; the user prefers 3), J1
  seats beyond ruling 4, or the in-band / contact ceiling of about 17.2 at 3 DOF.
- **Lens B (complexity at the lead's number, the user's second objective; measured lever: cell A ties 18.28 at cx 16.5,
  2 points simpler, same 262 takes).** Build the dwell preload as metal (its element counted in cx), measure its J2 drag
  (R17-style), and measure the near-touch shift of the 0.638-deg play at poses 139, 316 and 203. Select on the
  envelope-selection draw, claim held out, paired against the lead.
  - Alternative cell: the one-part groove with the low arm (A0 read 18.37; with the low arm, unmeasured).
  - Kill: held out paired > 0.5 worse than the lead, or cx > 16.5 once the preload is counted.
- **Contacts, inside lens B and only as sideways moves:** 264 (hub K -1.17) and 316 (link 2 -1.23 on the lead) are within
  the ~1 mm lateral levers measured on trimlug. 237 (crank -9.47) and 205 (hub 2 -4.28) are not. Worth <= ~0.6.
- **Machinery before any claim:**
  - The runner refuses a selection scan on Bench(110,360) or held out (P1).
  - tools/dash_build.py reads the honest flag and the penalised objective.
  - The verify template's bar becomes 18.28.
  - The row verdict is rewritten from the verification block.
  - The convergence gate requires >= 2 independent starts.
  - Box edges equal the rule bounds both ways.
- **Do not rescreen:**
  - cap-pole knuckle seats (cells A / B / C);
  - crest pin-knee seat moves (only the joggled-knee cell is open, bounded at 25-27);
  - the crest no-knee 3R;
  - slotted eccentrics on a J2 crank (any knee size);
  - link-2 root or whole-bar lifts;
  - hard-pad dwell stops on the desmo crank;
  - two-lobe K drives without a real drive component.

### Needs the user's say

- **The 3-DOF ceiling (pending lens A's table):** by every measurement so far, 95 needs a 4th joint or wider J1 seats.
  The lead should ask once the table is on file and the jump track's 4-joint ghosts give their like-for-like numbers.
- B1 (unchanged): m_sub at K rest vs the coupled reading still decides G4 for the whole knuckle family (now measured on
  lowarm too: 50 of 205 rest poses under 1 deg).

## Round 15 plan (2026-10-18 ~03:15 UTC, track main, lead verified gap 18.28)

Planner's read at 03:05-03:15 UTC: ROUNDS.md (round 14 results, round 103 plan), FINDINGS.md (round 14; "The fold is
two walls"; "Long-stroke K drive, measured"), rows/*.json, catalogue.json, events.jsonl tail (to 03:07:56Z),
tools/simplicity.py v2.2, tools/env_bench.py, the lead's per-pose and stop-window dumps
(docs/alignment/remeasure/conecut-knee-knuckle-3r_{bench_perpose,stopwindow}.json). Ledger re-read
(`tools/alignment_ledger.py latest`, exits by `get`): **gamed** = lowarm-halfring-knuckle-3r (P1, 03:00:45Z),
dipped-law-groove-knuckle-3r (fold margin 0.184), seed-offset-3r-slides; the lead conecut-knee-knuckle-3r exit 0 WATCH;
desmo-conecut and desmo-slipper exit 0 WATCH. No bench, judge or kit file changed since round 14's close.

### State

- **Lead (best verified, not gamed): conecut-knee-knuckle-3r 18.28** (score 93.35), frozen exact Bench(110,360), held
  22.38. Reach 0.7278 (262/360), ib14 0.9012, follow 1.0, contact 0.0106 (4 poses), overhead 8/28. 3 active joints,
  0 passive translations, cx 18.5. Config: stk 6.0, lE 97.14, lc 24.35, phiE 0.75, phib -91.80, J3 window
  [-111.90, 122.74].
  - WATCH reasons (carry into every summary that names it; no lens may buy points the same way):
    - reporting: the sweep's 12.5 is shown as 95.45;
    - T1: 16.56 points sit in the 1-2 mm shell, and pose 203 is taken at 0.263 mm;
    - T3: held th margin 5.006; K play of ~0.23 deg takes it near 4.92;
    - NEW-strap-dilution: 18.67 at equal strap sampling;
    - M5: the J3 stop returns 155 N per N.m through MR117 bearing 1;
    - NEW-self-reference; G4 (B1).
- **At the lead's number (all WATCH, 3 active, 0 passive translations):**

  | design | verified gap | cx |
  |---|---|---|
  | inband-rssr | 18.33 polished | - |
  | slipper-nose | 18.49 | 18.25 |
  | trimlug-k165 | 18.51 | - |
  | roller-longdyad | 18.67 | - |
  | desmo-slipper | 18.95 | 15.75 |
  | desmo-conecut | 18.98 | 16.5 |

  - lowarm-halfring 17.96 (cx 16.5) is GAMED: its link-2 lift was picked from 794 configs on the claim bench; held out
    22.70 vs 22.38; the bench edge is a 0.048-mm graze at pose 316.
  - Its cell A (half ring + low arm, zr 2.0) ties 18.28 three times (262 takes, 4 contacts, proposer held 22.64) at
    cx 16.5, but only with a hard pad of 0.638 deg K play (0.292 at 5-10 micron) against the 0.25 gate.
  - Complexity frontier: H1 pin knee 27.20 at cx 0; crest-knee-3r 32.84 at cx 0 (WATCH: G1 overhead metal at 0.02-2.10
    mm; ws in-band 0.793); geneva-tail-pinknee 23.57 at cx 12.
- **95 arithmetic** (gap = 100 (0.90 - ib14)+ + 100 (0.95 - follow)+ + 100 (0.90 - reach)+ + 100 contact):
  - 95 = 13.75 needs 275/360 takes at zero contact, or 279 at the lead's contact.
  - Each lead contact pose that becomes a take is worth ~0.54 (one take 0.28 + contact 0.265).
  - Zero contact at the lead's 262 takes = 17.22, the "in-band / contact ceiling".
- **Where the lead loses its 98 poses:**
  - fold 88: 73 on the stretched wall (th 107-176; 64 of them internal rotation >= 90 across the body; the wall is the
    K drive's stroke and law, dK 52.6 of the 57 cap) and 15 on the folded wall (scapular-plane overhead; a hub-2
    clearance trade, median need 71 mm);
  - J3 stop 6;
  - contact 4: 237 crank -9.42 mm, 205 hub 2 -4.28, 316 link 2 -1.23, 264 hub K -1.17.
  - The J3 window is already at its edge: the stop-window sweep moves 1 contact into a stop, never a take.
- **Measured take ceilings at the legal J1 seats (3 DOF):**
  - Back of shoulder:
    - plain O20 3R: 250 kinematic;
    - knuckle, law-only kinematics: 267 at kK 1.96, 272 at 2.3;
    - knuckle ghosts (ideal drive): 269-271, about 40 cells over rounds 12-13 (proximal-j3 269 at the knee rule);
    - long-dyad, drive metal deleted, kK 3.0: 18.25 frozen (fold 88 -> 77);
    - parking_k's ideal-law estimate: 0.775-0.778 at a 75-deg stroke. The real lobe law cannot follow it at
      PA <= 42.
  - Cap pole:
    - plain 3R: 281 kinematic, 267 frozen;
    - knuckle: cell C 275 kinematic, 247 metal (299 kinematic box -> a metal search walked back to 275);
    - the lead's seats in the same kit: 277 kinematic, 259 metal.
  - Deltoid crest: pin knee 228 frozen verified, no knee 218. A joggled knee is bounded at about 25-27 frozen.
  - Antcrest: hub-2 need 50-400 mm; pin knee 375 with H1's knee (dead).
  - Floor at 271 takes and zero contact: 14.72.
- **4-DOF reference (jump track, round 103, every row dead):**
  - lead-relay-j0-4r: a ghost J0 takes 275 (16.07); real hub 0 + link 0 give 22.18-24.92 (ib14 0.82-0.84), riding
    25-30 mm over the skin at all 108 legal seats.
  - backbridge 32.13; wobble 32.92.
  - cap-nullspace-4r is still modelling: sprung 70.64 vs control 66.26 frozen.
  - Older rows: minarc-stop-knuckle-4r 18.40 polished / 19.54 verified (cx 32.5); arm-parked-knee-4r 26.71.
  - Any 4th DOF costs +25 cx.
- **Dead: do not rescreen.**
  - Round 14's list: cap-pole knuckle cells A/B/C; crest seat moves (except the joggled knee); the crest no-knee 3R;
    slotted eccentrics on a J2 crank; link-2 root or whole-bar lifts (radial lifts cost in-band 1:1, 18.41); hard-pad
    dwell stops; two-lobe ghost K drives.
  - Plus: back-seat J3 / hub-K / link-2 seat moves (proximal-j3), long-stroke K drives (bell crank and ball links do
    not park: 23.31 / 27.67), relays under the lead (r103 lens 1).
- **Complexity arithmetic (tools/simplicity.py v2.2):** spring or flexure +3, catalogue part +0.25, made part +0.5,
  sliding pair +1. **Any spring preload on cell A reads 16.5 + 3 = 19.5, above the lead's 18.5, so it is dead by
  arithmetic.** The preload must be spring-free.
- **Machinery still open (round 14, lesson 11):**
  - no runner guard against selection on Bench(110,360) or held out (P1);
  - tools/dash_build.py does not read the honest flag (slotted-eccentric's dishonest 97.45 is shown);
  - the verify bar is still 68.93 / 75.94 (tools/workflows/exo-screen.js line 24);
  - row verdicts are not rewritten from the verification block (crest-knee);
  - the convergence gate passes on one start;
  - box edges have sat inside rule bounds (end_extra 6 vs 8, +0.64).
- **Compute:** the farm is CLOSED. Local only, niced, <= 2 processes per agent, OMP_NUM_THREADS=1, judges --jobs 1.

### Lenses

**A. take-bound-3dof (reach: the decisive table and the user's blocker; 1 slot, analysis + ghost fills, <= 90 min).**
- Write `docs/research/take_bound_3dof.md`, with its script and JSON beside it, from the files on disk.
  - Rows: one per J1 seat family (back, cap, crest, antcrest) x realisation (plain 3R, knuckle, pin knee).
  - Columns:
    - kinematic window takes at the 5-deg th margin;
    - law-limited kinematic takes, where a K law applies;
    - best ghost takes (drive metal deleted);
    - best metal takes, frozen exact Bench(110,360);
    - best verified non-gamed takes;
    - the gap floor at zero contact, 100 (0.90 - takes/360);
    - the gap at that family's measured ib14 / contact.
  - Every cell is cited to a file. A cell nobody measured is run as a ghost on the paired kit (the crest-seat knuckle
    with an ideal K law is the known hole), or marked unmeasured with the reason.
- Add a 4-DOF reference row from round 103: ghost 275 vs real 22.18, and why (hub 0 + link 0 0-2 % in band).
- Optional, report-only (<= 20 min): a "price of ruling 4" row. Give the kinematic + ghost take bound of the best
  front / clavicle J1 seat in the knuckle family, so the user's choice has a number. Never a row, a design or a claim.
- Reconcile parking_k's 0.775-0.778 with the measured 267-272 law cap and 269-271 ghosts, in one paragraph.
- Write the result to FINDINGS. If no 3-DOF family reaches 275 metal takes, end the doc with the blocker text for the
  lead, ready to send as a big update: "95 at 3 DOF is measured out of reach at the back-of-shoulder and acromion-top
  seats". The options, each with its number:
  - a 4th joint, with the jump track's best like-for-like;
  - J1 seats beyond ruling 4 (the optional row);
  - accept the ~17.2 in-band / contact ceiling at 3 DOF.
- The jump track's 4-joint gates report against this table.

**B. cx-at-lead-spring-free-dwell (complexity at the lead's number; suggested id lowarm-adjpad-knuckle-3r, a NEW row,
because lowarm-halfring-knuckle-3r is GAMED).** Lowarm cell A's 18.28 at cx 16.5 stands only with a dwell hold <= 0.25
deg. Two cells, in this order:
- **A0L: the one-part groove (desmo-conecut with the cap-ring sector inside hub 2's O20, read 18.37) with the low arm.**
  It has no pad, so it has no play question.
- **A-adj: half ring + low arm with an assembly-adjusted RIGID pad** (an eccentric pin or locked set screw shims it to
  zero clearance), built as metal.
  - Its adjuster and lock are sampled metal (the pad is S3-unsampled today). Each part is counted in cx (+0.25-0.5
    each).
  - Measure its J2 drag R17-style at mu 0.17 over the tolerance corners.
  - Report the near-touch shift of the residual K play at poses 139, 316 and 203, and min th with that play.
- Pre-register before any run:
  - **kill:** held out paired worse than the lead by > 0.5; cx > 17.0; a spring preload (19.5 by arithmetic); or
    residual play > 0.25 deg at any tolerance corner.
  - **pass:** frozen exact <= 18.28 at cx <= 17.0, held out paired within 0.5 of the lead.
- Selection: fit on env, select on envsel (tools/env_bench.py), wear frozen exact Bench(110,360) once, claim held out
  paired against the lead (CI90, P(better)).
- Restore round 13's open items in the same model:
  - bind at least 1 deg of K above the held stroke at a_s +-0.1 mm and mu 0.17;
  - enforce RC_MIN (rc_min 1.0, ridge 0.243 mm);
  - bring the crank-free worst-tolerance slop under 0.25 (0.27 today);
  - make the slot end dK_lim >= 46.3 (46.0 today) or prove the bench max 45.62 safe;
  - model the relief pocket as metal;
  - carry K play into th.
- The claim reports plain and near-touch gap, S6 equal-sample in-band for any added metal, the min th margin, and the
  convergence gate over >= 2 independent starts.
- If B passes, its config is a Pareto point at the lead's number (2 points simpler). It is not a lead change by itself:
  the old CI tie rule is withdrawn and the question is with the user.

**C. sideways-contacts (takes + contact on the lead's frozen chain and on B's cell; suggested id
conecut-sidestep-knuckle-3r).** Only 264 (hub K -1.17 mm, overhead) and 316 (link 2 -1.23) are in reach. Each one
cleared into a take is worth ~0.54, both ~1.1, to about 17.2 (score ~93.75): a lead change on the plain gap.
- 237 (crank -9.42) and 205 (hub 2 -4.28) are out.
- Lateral only, in the skin tangent plane: bar offset, lug or crown trim inside O20, hub phase about its own axis.
  Radial lifts are dead (lesson 8).
- Stops that turn a contact into a fold or a J3-stop loss do not count.
- **Gate 0 (<= 30 min, the frozen-exact per-sample surrogate, ~0.1 s per config):**
  1. Attribute each contact: the binding part sample, its contact normal, and the lateral direction that frees it.
  2. Measure mm of skin clearance per mm of lateral move at 264 and 316.
  3. Measure what the same move costs on envsel poses within 15 deg of them.
  - The round-13 lesson says 264 binds radially (a +-1.5 mm bar offset moved 129 by <= 0.4 mm). If the lateral gain
    is under 1.4 mm for 1.5 mm of move, or the move loses a take on envsel, kill at gate 0 with the number.
  - The gate's Bench(110,360) reading is a kill test only, never a pick.
- **Lever size:** set on envsel with a pre-registered >= 0.2 mm clearance at the cleared pose. The lead's T1 / lowarm's
  T1 lesson: 0.014-0.197-mm grazes are not clears.
- **Claim:**
  - wear frozen exact once;
  - claim held out paired against the lead;
  - report the 1-2 mm shell points and pose 203's distance before and after.
- **Kill:** held out paired not better than the lead (P(better) < 0.5), or any new contact.
- Apply the same lever to B's cell if B passes.

**Machinery before any claim (the lead, or the first free slot in this round):**
- the runner guard refusing a selection scan on Bench(110,360) or held out;
- tools/dash_build.py reads the honest flag and the penalised objective;
- the verify bar becomes 18.28 in tools/workflows/exo-screen.js;
- the row verdict is rewritten from the verification block;
- the convergence gate needs >= 2 independent starts;
- box edges equal the rule bounds both ways.

A claim that lands before these must apply each by hand and say so.

### Carried (ideated, never screened)

None. The 22 'ideated' catalogue entries all fall under measured closures:
- tripods / telescopes / crossed rails: passive translations, or no compact component;
- lamellae, rings and rolling cones: O20 only; rings >= 72.2;
- spherical parallel / five-bar loops: seed-spm 193; loop proxies 130-240 points optimistic;
- strap / tape J2s: no real component at size;
- offset-axis skin hubs: 3 passive translations.

cap-nullspace-4r is modelling on the jump track. The round-4 picks are done (crest-knee-3r, deltoid-crest-j3-3r,
slotted-eccentric-pin-knee-3r).

### Elsewhere, not to be duplicated

- cap-nullspace-4r (jump round 103, lens 2; modelling since 02:27Z).
- The gen-9 desmo-conecut L2 CAD build (pipeline/conformal/param_cad/user_style_desmo.py, uncommitted, the lead's
  slot). Lens B models a sibling cell in the paired kit and does not touch that CAD.

### Needs the user's say

- The 3-DOF ceiling: lens A's table, then the blocker message.
- B1 (G4, m_sub at K rest): unchanged.
- The lead's withdrawn CI tie rule: still with the user.

## Round 103 results (Round J3, track jump; 2026-10-18 ~00:55 - ~03:50 UTC, closer)

I re-read the ledger with `tools/alignment_ledger.py get <id>` at ~03:50 UTC, just before naming the winner:
- lead-relay-j0-4r, lead-relay-backbridge-4r, lead-relay-wobble-4r and cap-nullspace-4r all exit 2 (no entry: dead
  rows, never audited; this round's alignment audit list is empty);
- the lead, conecut-knee-knuckle-3r, exits 0, verdict WATCH (skeptic, 2026-10-17 20:15 UTC).

No design is gamed. Complexity is tools/simplicity.py v2.2. All four rows are dead, and every verifier upheld its
number (0 of 4 refuted; each re-ran the claim and reproduced it to the digit). The farm was closed all round, so
everything ran locally (<= 2 niced processes). "Fast" is Bench(60,160) fast with kit checks; "frozen" is frozen exact
Bench(110,360), the verification protocol. Every design this round has **4 counted joints**; the user prefers 3, and
every number below is compared like-for-like with the 3-joint lead (18.28) and with the 4-DOF rows on file
(minarc-stop-knuckle-4r 19.54 verified / 18.40 polished, arm-parked-knee-4r 26.71).

| design (lens) | verified number (frozen) | fast / ghost | reach / overhead | act / P / cx | ledger | outcome |
|---|---|---|---|---|---|---|
| lead-relay-j0-4r (1: spring-centred J0 relay beside J1 under the lead's frozen chain, real O20 hub 0 + link 0) | **22.18** (score 91.93) at a0 10 / azu 45, window [-60, +42] picked on the fit bench | ghost (zero-size J0) 16.22; ghost's own seat a0 20: real 24.92 / ghost 16.07; lowest hub a0 7.5: 22.95 / 18.22 | 0.7583 (273/360), ib14 0.8404, 8 contacts / 8 of 28 | 4 / 0 / 50.75 | exit 2 | dead at gate 0 (> 17.5); hub 0 floats 17-55 mm over the skin at every legal seat |
| lead-relay-backbridge-4r (1, the "larger a0" clause: J0 outside hub 2's orbit, link 0 bridging the knuckle) | **32.13** (88.32) at a0 60 / azu 330 | ghost 18.22; other seats 34.01 / 35.42 / 38.64 | 0.725 (261/360), ib14 0.7722, 7 contacts / 8 of 28 | 4 / 0 / 50.75 | exit 2 | dead at gate 0; link 0 0.000 in band (median 25.8 mm over the skin) |
| lead-relay-wobble-4r (1, the "inside J1's footprint" clause: J0 stacked under hub 1 on a wedge) | **32.92** (88.03) at a0 6 / azu 180 | 28.10 fast; ghost = lead 18.28 (0 claim poses relayed) | 0.6472 (233/360), follow 0.90, ib14 0.8796, 2 contacts / 7 of 28 | 4 / 0 / 50.75 | exit 2 | dead; 42 claim poses lost to stack clashes (riser 35, hub 0 on hub K 7) |
| cap-nullspace-4r (2: cap-pole redundant spherical 4R, null-space set by torsion springs on J0 / J2 / J3 + own-angle stops) | **57.70** (79.02) | 46.32 fast (model check 46.97); its searched plain cap 3R control 60.61 frozen / 54.15 fast | 0.7444, ib14 0.5476, contact 0.069 / 11 of 28 | 4 / 0 / 34.5 | exit 2 | dead; hub 2 fitted ~117-121 mm from GH, 0.00 in band |
| conecut-knee-knuckle-3r (the lead, for reference) | 18.28 (93.35), held 22.38 | 12.50 fast | 0.7278 (262/360) / 8 of 28 | 3 / 0 / 18.5 | WATCH | stays the verified lead |

**Winner (by the rule): lead-relay-j0-4r.** v_gap 22.18 frozen exact (score 91.93), 4 active joints, 0 passive
translations, complexity 50.75, no ledger entry (not gamed). It is the best number an independent verifier confirmed
this round. **It does not beat the previous verified lead, 18.28 (conecut-knee-knuckle-3r, 3 joints): it trails by
3.90**, and it is dead on the track's gate (17.5), so it is not a build candidate: no generation CAD for J3, and the
generation CAD of record stays the lead's (gen-9 desmo-conecut is building in the lead's slot). No design reached the
judges (judge_all), so no EVOLUTION row. Passed over as gamed: none. It also does not beat the best 4-DOF row on file
(minarc-stop-knuckle-4r 19.54 verified).

**Alignment.** None of the four rows has a ledger entry (exit 2): the auditor did not run on this round's dead rows,
so the verifiers' findings are carried here at watch level, with the numbers. The lead's own WATCH reasons
(reporting 12.5 shown as 95.45; T1, 16.56 points in the 1-2 mm shell, pose 203 at 0.263 mm; T3, held th margin 5.006;
NEW-strap-dilution 18.67; P2 nil; M5, 155 N per N.m through MR117 bearing 1; NEW-self-reference) stand unchanged; this
round's relay cells wore the lead frozen and inherit its T1 class (near-touch minimum 0.054-0.072 mm on every relay
claim).
- **lead-relay-j0-4r:**
  - *reporting:* the proposer's 13.63 dropped the relayed skin contacts; it is not a real number. With relayed hits
    counted as contacts the best ghost is 16.07-16.22.
  - *near-touch:* at a0 20, four relayed takes sit within 1 mm of the skin (pose 259 at 0.05 mm).
  - *r0 from the fit bench:* at a0 20 and a0 7.5, two poses the lead takes jam (hub 0 or link 0 within 1 mm of hub K);
    counted as losses.
  - *not run:* the continuity flood (connected reach <= static reach, so it cannot rescue the number) and the per-pose
    alignment dump (dead row, not a contender).
  - *refuted over-strictness (verifier):* r0 freed (44-90 mm, jams counted as losses, hub 0 alone, link 0 deleted)
    over 3324 placements: best 18.77 fit (a0 35 / azu 300) against the lead's 12.50 fit; dropping the 5-deg J0-J1-J3
    sub-chain margin makes the best real gap worse (14.03 -> 14.66 at a0 10, 17.37 -> 17.87 at a0 20 fit).
- **lead-relay-backbridge-4r:**
  - *sampling density:* link 0 is sampled at 1 per 3.4 mm2 against the 1 per 4 mm2 rule; at the right density the
    claim is ~30.6, still dead.
  - *doc wording:* seat 60/330 is called clash-free, but the current build_metal gives r0_chain 77.0 against r0 76.0
    (1 fit pose; no claim-bench effect).
  - *search box:* the screen covered azu 285-0 only; the verifier's full-circle scan at a0 60 (legal azu 270-90) found
    link 0 0-13 % in band on every route, no region missed.
  - *gate:* passes only formally (4 decisive wears, no search).
- **lead-relay-wobble-4r:**
  - *generous to the design (not counted against it):* the riser is ~1 mm shorter than hub K's near rim requires; hub
    0's skin-level ground bracket is not modelled; hub 1's cover mask is computed at q0 = 0 and reused on 1-3 relayed
    poses.
  - *gaming option refused:* a skirt hung from the wedge to pull hub 1's exposed crescent into the band was not
    counted.
  - *reporting:* the row's `gap` is 28.10 fast; the verified number is v_gap 32.92 frozen.
- **cap-nullspace-4r:**
  - *T1 (plain-gap search, again):* the search objective was the plain gap, not the near-touch gap CLAUDE.md asks for.
    Contact doubles when frozen (0.035 fast -> 0.069 frozen exact); near-touch gap 64.51 frozen against 57.70 plain.
  - *reporting:* headline fast 46.32 vs the model's own check 46.97 (cosmetic 0.65).
  - *numbers not on file (judge, round103_ideation.md 1.5):* the proposer's 44.97 ghost, 59.90 split-elbow ghost and
    60.79 control were in no saved output (the control log crashed on its import). The verifier re-ran the ghost at
    the claim geometry: 71.01 fast with K2 off (hub 2 0.037 in band), 158.89 with K2 on (follow 0.13).
  - *search box:* neither the 4R nor the control searched a1 < 45 or a2 < 54. The audit's oracle grid there puts hub
    2 0.56-0.64 in band but reach falls to 0.29-0.40; best 83.31.
  - *feel / continuity:* the springs wind ~+-170 deg (a 120-deg range collapses the top 25 cells to 102-191 fast);
    J0 sweeps ~320 deg (q0 -165..151 frozen); the motion preview shows a 46-deg J0 basin snap at frame 91, which the
    bench's flood (snaps <= 10 deg per edge) does not see. Any revival must check the preview path.
- **Process, all rows:** all four verifiers again quoted the stale template bar (68.93, refute at 78.93; the lead is
  18.28) and judged against the round's own bar by hand. The template has now been stale in 7 of 8 verifications over
  J2-J3. The alignment auditor wrote no ledger entry for any of the four rows.

**What the round measured (lessons).**
1. **A grounded relay hub cannot sit in the band beside a J1 whose first link carries a hub within ~35 mm of J1's
   axis.** J1 sweeps hub K (15-33 mm off its axis), hub 2 (31-46 mm), L1b and the crank through an annulus around its
   own axis. A grounded O20 hub 7-40 deg off J1 must ride above it: r0 65.5-120.5 mm, 17-55 mm over the skin, 0-2 %
   in band, over 108 legal seats. Hub 0 + link 0 add 50-101 skin-facing samples per pose: ib14 0.9012 -> 0.8404 at the
   best seat (+6.1 gap), 0.8171 at the ghost's seat (+8.4). The verifier's bound with r0 free and link 0 deleted:
   hub 0 alone costs >= 6.27 fit points at every a0 <= 40, against a largest relay gain of 4.48 fit points.
2. **Any part that must reach a hub from outside the ring its neighbours sweep rides at their crown height plus
   clearance, about 22-30 mm over the skin.** Measured chain-set at every station of 5 link-0 routes (backbridge); link
   0 was 0-1.7 % in band at 4 seats, 0-13 % over the full legal circle. Its in-band cost is set by its sample count,
   not by the hub it carries: about +0.2 score points per mm of 12 mm bar at the lead's 1062-sample pool (+11.5 at 48
   mm). Remote relay hubs, base bridges and links routed over the knuckle can be priced before they are built.
3. **Stacking a relay under J1 jams.** The output link must ride the upper hub's boss (~20 mm rise, not 12.25) and
   come back down as a riser in the ~4 mm gap between hub 1's rim and hub K's rim; the riser hits hub 0 on 35 claim
   poses (5 of them frames of the scapular-plane overhead clip). Rule: no relay hub stacks under J1 when the next hub
   sits within one hub diameter. With every clash forgiven and the riser deleted, the stack's dilution alone floors the
   cell at 14.92 fast (lead 12.50). Price stacks with a cover mask (part-table arithmetic +7.4 vs measured +2.0-2.7).
4. **A spring-centred relay under a skin-fitted chain turns lost poses into contacts about as often as into takes**
   (15 takes / 8 contacts at a0 20, 11 / 4 at a0 10). The relay ghost's gain on the lead is at most 1.9-2.2 frozen
   points (16.07-18.22 vs 18.28); 0 overhead poses are relayed at any seat (overhead stays 8/28). A relay must be
   judged by its contacts, not only its takes.
5. **A zero-size ghost overstates a 4-DOF base relay by 6-9 points at these seats.** Screen future 4-DOF base-relay
   proposals with hub 0 worn as real metal from the first configuration.
6. **The cap-pole null-space is capped by hub 2's zone whatever the spare does.** The 1-D null-space goes to the
   cap-pole members (hub 0 / link 0 / hub 1 0.98-1.0 in band) and never to hub 2 (fitted ~117-121 mm, 0.00 in band).
   The spring-set 4R is worth ~3 frozen points over the plain cap 3R it replaces (57.70 vs 60.61). Verifier bounds,
   frozen exact: hub 2 deleted 53.10; hub 2 ideal 50.25; hub 2 + links 1-2 ideal 19.84; every member ideal 18.26;
   in-band perfect (reach + contact only) 22.46. Even a perfect J2 side does not reach 17.5 at the cap pole.
7. **Redundant models must fix both assembly-mode signs** (two fold stops pin a spherical four-bar's branch): letting
   either J2 branch win misstated the cell by ~7 fast points (70.36 vs 63.75). A quadratic spring law in the wrapped
   angle is physical only below 180 deg of deflection; spring-determined designs must state and check the range.
8. **Fast gains stop surviving the frozen wear after ~400 tries on a spring cell** (fast 49.62 -> 45.47 while frozen
   went 59.44 -> 57.70): watch the frozen plateau, not only the fast gate, when deciding to stop.
9. **A free hub on the back of the shoulder at azu 330-345 is mostly in band (0.73-0.88, median ~11 mm)**; its height
   is set by overhead deltoid / supraspinatus bunching (closest 2.8 mm at elevation 150-165), not by behind-back
   poses. The chain's free sector around J1 (azimuth ~150-180) is free because the skin is high there at elevation
   120-165: free-sector placement arguments must be checked against high-elevation skin.

**The 4-joint picture after J3 (for round 15 lens A's take-bound table and the user's blocker).** Both 4-joint levers
the planner left open are closed at the legal seats with O20 hardware, with metal numbers:
- relays under the 3-joint lead (beside, backbridge, stacked): 22.18 / 32.13 / 32.92 frozen; ghosts 16.07-18.22; the
  relay's own gain <= ~2 points;
- the cap-pole null-space: 57.70 frozen; every-member-ideal bound 18.26.

The best 4-DOF verified number on file stays minarc-stop-knuckle-4r 19.54 (K as the 4th joint). No 4-DOF design beats
the 3-joint lead's 18.28, so "add a 4th joint" is not by itself a route to 95 at these seats. The 4-DOF reference row
for lens A: real 22.18 (273/360 taken, 8 contacts, ib14 0.8404) against the zero-size ghost's 16.07-16.22, the
difference being hub 0 + link 0 (0-2 % in band).

**Next focus (round J4, track jump).** The score has not reached 95. The best verified gap is 18.28 (conecut, WATCH);
95 needs 13.75, i.e. +17 takes to 279/360 at ib14 >= 0.90 and the lead's contact. Close in the catalogue, with the
numbers above: base relays under any host whose first link carries a hub within ~35 mm of J1 (beside / stacked /
bridged), and spring-set null-spaces at the cap pole. Do not open a co-fitted relay host either: the verifier's
optimistic ceiling for the whole relay cell is 14.29 fit against the lead's 12.50 fit.
- **Price first (new instrument from this round, <= 10 min per idea, before any ghost):** count the metal the class
  adds and price it with lessons 1-3 (a part crossing a swept ring rides 22-30 mm over the skin, +0.2 points per mm of
  12 mm bar; a grounded hub in J1's annulus floats 17-55 mm; a stack under J1 jams when the next hub is within one hub
  diameter). An idea whose priced metal costs more than +17 takes can return is dead before its ghost.
- **Lens a, the length-changing chain (the brief's one untested class under the current rules):** one real
  miniature guide (catalogue part, rail = travel + block, worn as metal from the first config; a radial slide stands
  up by its travel + block length) inside link 2 or as the counted cuff slide, so the stretched poses close without
  the dyad stretching. *Measured reason:* 73 of the lead's 98 losses are stretched (th 107-176, the K drive's stroke
  wall), and every rotation lever that tried to relieve them this round (relay, null-space) failed on added hub
  metal, not kinematics; a guide inside a link adds no hub and no crossing. Gate 0 as before (ghost with the guide's
  real envelope, fit Bench(60,160), frozen exact Bench(110,360), <= 15 or >= 279 takes with <= 4 contacts; kill > 17.5).
  Check the early curved-slide deaths (trombone-arc, seed-arc-rails, j2-arc-sector-3r) for the reason before
  repeating them.
- **Lens b, an outside-field mechanism done as that field does it, priced first:** the planner's choice (orthotic
  polycentric hinges, prosthetic socket suspension, remote-centre / spherical mechanisms), only if its priced metal
  passes the instrument above.
- **Machinery before the next claim:** fix the verify template's bar to the current lead (stale in 7 of 8
  verifications over J2-J3); make every search objective the near-touch gap (cap-nullspace searched the plain gap and
  doubled its contact frozen); have the auditor write a ledger entry for each round winner, dead or not; keep
  quoted numbers to saved outputs only (three of cap-nullspace's proposer numbers were never on file).

### Needs the user's say (unchanged, now with J3's numbers)

- The 4-joint question, answered like-for-like: no 4-DOF design on file beats the 3-joint lead (best 19.54; this
  round 22.18-57.70). Round 15 lens A's table carries the 3-joint side; the blocker message goes to the user from there.
- The transmission guard [30, 150], the J1 seat rule and the 5-deg fold margin stay as they are; no lens relaxed them.

## Round 104 plan (Round J4, track jump; 2026-10-18 ~04:00 UTC, lead verified gap 18.28)

Planner's read at 03:45-04:00 UTC: ROUNDS.md (round 103 results, round 15 plan), FINDINGS.md (J3; "The fold is two
walls"; "Long-stroke K drive, measured"), rows/*.json, catalogue.json, events.jsonl tail (to 03:51Z),
docs/research/manufacturability_audit.md, docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json,
tools/workflows/exo-screen.js. Ledger (`tools/alignment_ledger.py latest`): **gamed** = lowarm-halfring-knuckle-3r (P1),
dipped-law-groove-knuckle-3r (fold margin 0.184), seed-offset-3r-slides (3 passive translations); every other audited
row WATCH. No bench, judge or kit file changed since round 103 closed.

### State

- **Lead (best verified, not gamed): conecut-knee-knuckle-3r 18.28** (score 93.35) frozen exact Bench(110,360), held
  22.38; reach 0.7278 (262/360), ib14 0.9012, follow 1.0, contact 0.0106 (4 poses), overhead 8/28; 3 active, 0 passive
  translations, cx 18.5. **The bar for every claim this round is 18.28** (the verify template still defaults to 68.93 /
  75.94 / lead 30.35, tools/workflows/exo-screen.js line 24: every verifier states 18.28 by hand and says so). WATCH
  reasons carried (no lens may buy points the same way): reporting (sweep 12.5 shown as 95.45); T1 (16.56 points in the
  1-2 mm shell, pose 203 taken at 0.263 mm); T3 (held th margin 5.006; ~0.23 deg K play takes it near 4.92);
  NEW-strap-dilution (18.67 at equal strap sampling); M5 (J3 stop 155 N per N.m through MR117 bearing 1);
  NEW-self-reference; G4 (B1).
- **95 arithmetic:** 13.75 = 279/360 takes at the lead's ib14 and contact (+17), or 275 at zero contact. One take
  +0.28; a contact turned into a take +0.54. Zero contact at 262 takes = 17.22.
- **Where the lead loses its 98 poses:** fold 88 = stretched 73 (th 107-176, 64 of them internal rotation >= 90 across
  the body) + folded 15 (scapular-plane overhead, hub-2 clearance, median need 71 mm vs 62); J3 stop 6; contact 4 (237
  crank -9.42, 205 hub 2 -4.28, 316 link 2 -1.23, 264 hub K -1.17).
- **How far the stretched wall must move (counted from the roller-longdyad per-pose file above; same family, max th
  taken 106.3):** raising th_hi by +5 / +10 / +15 / +20 deg returns 7 / 19 / 25 / 30 of the 73 stretched poses
  kinematically (held 22 / 47 / 72 / 87 of 211). +17 takes needs th_hi ~ +10 deg AND those poses clean of metal.
- **The second wall behind the stretched one (measured three ways, the decisive limiter now):**
  - free K (K as a sensed 4th joint, no law): minarc-stop-knuckle-4r 19.54 verified / 18.40 polished;
    skinnormal-shortk-knuckle-4r 18.58 frozen, fold-for-contact 1:1 (74 fold / 8 contact -> k33 55 / 19 -> k56 50 /
    24; best frozen reach 0.769 at contact 0.048);
  - ideal K law, drive metal deleted, kK 3.0: 18.25 frozen (fold 88 -> 77; the lobe at PA <= 42 caps kK ~2.0, law-only
    267 takes at 1.96, 272 at 2.3);
  - desmo-vrocker ghost 17.23 (269 takes, 6 contacts): the same 5 poses go into the skin in every cell at onset 12-14
    whatever the gain: 117 / 127 / 129 / 139 (plane -90..-60, elev 45-60, axial 105-135: link 2 to -7.7 mm, hub 2's rim
    to -3.5) and 316 (60/150/-105). 129 binds radially across link 2's full width over the lateral-deltoid crest (a
    +-1.5 mm bar offset moves it <= 0.4 mm).
  - **So every K-side lever (any drive, any law, a free K) is bounded at ~18.2-18.6 frozen at these seats: once K opens,
    link 2 and hub 2 meet the skin.** Kinematics are not the cap (twist-long-a2 law-only reach 0.814-0.825;
    split-knuckle-twosided passes its law gate); every death is metal parking.
- **4-DOF on file (all dead or behind):** relays under the lead 22.18 / 32.13 / 32.92 (ghost 16.07-18.22, relay gain
  <= ~2), cap null-space 57.70, minarc 19.54, arm-parked-knee 26.71, skinnormal-shortk 18.58 (killed). Any 4th DOF +25
  cx. No 4-DOF row beats 18.28.
- **The length-changing chain priced at plan time (lens a of the J3 closer), before any ghost:**
  - th, a1e and a2 are angles between joint-AXIS DIRECTIONS; the arm's orientation is the product of the revolute
    rotations only. A straight guide (inside link 2, or as the counted cuff slide) changes no axis direction, so it
    moves neither wall: **0 kinematic takes** on the 73 stretched poses. On file: offset-skin-normal-3r's limiter "J2
    fold ... orientation-level, untouched by offsets or slides" (47 of 220). The cuff knee's pins are parallel to J3,
    so they do not change th either. A guide that breaks axis concurrency also needs the knee + guide to close a 3D
    offset (3R + P + 2 pins = 6 for 6), which buys nothing on the fold.
  - The guide variants that DO change an angle are all dead or bounded: a GH-concentric arc = a virtual revolute with one
    radius over its travel (trombone-arc 88.29, seed-arc-rails 73.0, j2-arc-sector 71.53 / 66.3 vs its own hub control
    57.75, short-a2-arc-slide 41.19 frozen self / v 55.3: hub 3 0.31-0.33 in band on the slot); a guide as the
    follower of a slider-crank K drive or a spherical lazy-tongs link 1 = a K law, bounded by the free-K numbers above;
    a radial guide lifting hub 2 at the folded wall stands block + travel (RSR3M 12 + ~9 = ~21 mm, 1.5x the band;
    manufacturability_audit finding 1).
- **Dead, do not rescreen:** everything on round 15's list (cap-pole knuckle cells, crest seats, crest no-knee, slotted
  eccentrics, link-2 root / whole-bar radial lifts, hard-pad dwell, two-lobe ghost drives, back-seat J3 / hub-K / link-2
  seat moves, long-stroke K drives 23.31 / 27.67, relays under the lead, cap null-space); the dog drive (dogring
  refuted 97.83 on a -0.18 mm dog / link-1b overlap); four-bar and coupler K drives (51.75 / 23.87); the arm-side K2
  (split-knuckle-twosided 34.18: K2's hub 70-116 mm); straight-guide length changes (above).
- **Process:** farm CLOSED (local, niced, <= 2 processes, OMP_NUM_THREADS=1, judges --jobs 1; load 9-11). Near-touch
  objective in every search (cap-nullspace's plain-gap search doubled its contact frozen). The auditor writes a ledger
  entry for the round winner, dead or not. Quote only numbers in saved outputs.

### Lenses

**A. guide-price-close (lens a, closed or kept on a measured survivor; 1 slot, <= 30 min, analysis + one kit check).**
- Run the price-first gate on the length-changing class and write the closure to FINDINGS: (1) on the paired kit, wear
  the lead frozen with a real catalogue guide (RSR3M class: block 12 x 8 x 4, rail 3 x 2.6, rail = travel + block) in
  link 2 at travel 0 / 10 / 20 mm and show th per bench pose unchanged and the takes unchanged (0 gain), with the
  guide's metal priced (+0.2 points per mm of bar out of band); (2) the arc / slider-crank / lazy-tongs / radial-guide
  variants close by the numbers in the state.
- A variant survives only if it changes an axis direction AND its priced metal leaves >= 17 takes, with the free-K
  bound (~18.2-18.6) beaten on paper. Gate 0 if one survives: ghost with the real envelope, Bench(60,160) fit, frozen
  exact Bench(110,360), kill > 17.5. No 4th guide, never a second cuff slide.

**B. second-wall-route (reach >= 0.77 at ib14 >= 0.88; suggested id freek-route-knuckle-4r as the bound, never a
claim; 1 slot, <= 90 min).** The measured binder is link 2 + hub 2 at the K-open stretched states (117 / 127 / 129 /
139 / 316), not the K law. Attack it with a route change, not a lift:
- On the free-K kit (minarc / skinnormal-shortk, K sensed: the upper bound for any K law), change where link 2 runs:
  enter hub 3 from the other (posterior) side, phase hub 3 about its own axis, or bend link 2 in planform around the
  crest (line / tangent-arc bars, ramps <= 60 deg, bend radius >= 15 mm). All metal real, O20 only, J1 seats legal.
- Price first: an added bar out of band costs ~+0.2 points per mm; a route that crosses a swept ring rides 22-30 mm.
- **Gate (pre-registered):** with K free, >= 279 takes at <= 4 contacts (or >= 275 at 0) on frozen exact
  Bench(110,360) after a Bench(60,160) fit with the near-touch objective, and the 5 binder poses cleared by >= 0.2 mm
  (not grazes). Kill otherwise, with the per-pose distances.
- If the bound passes, the same route goes on the lead's coupled K (3 joints) and is claimed on the protocol. If it
  fails, the number is the jump track's answer to round 15's take-bound table: no K lever reaches 95 at these seats
  with O20.
- Not main round 15 lens C: C moves only 264 / 316 on the frozen lead by small lateral offsets; this changes link 2's
  route under a free K.

**C. low-cx-same-reach (complexity; 1 slot, <= 60 min).** Desmo-slipper is 18.95 at cx 15.75 (12 made, 13 catalogue,
2 sliding pairs, 3 loops, 0 springs); the lead is 18.5. Price the coaxial dog drive's return (no lobe, follower or
sliding pair; refuted only on a -0.18 mm dog / link-1b root-ramp overlap) on the lead's chain:
- First the cx with tools/simplicity.py and the clash relief as metal (link 1b's root ramp relieved, or the dog
  re-phased). Dead before modelling if cx >= 15.75 or the relief costs more than it can return.
- **Pre-registered:** kill if frozen exact > 18.95 + 0.5 or held out paired worse than the lead by > 0.5; pass at
  frozen exact <= 18.95 with cx < 15.75 (a Pareto point, not a lead change).
- Select on envsel (tools/env_bench.py), wear frozen exact once, report plain and near-touch gap, min th margin, and
  the dog's engagement at PA <= 42 on every K-open pose.
- Not main round 15 lens B (lowarm A0L / A-adj on the conecut groove).

**Feed to main round 15 lens A (take-bound table) and the user's blocker:** the 4-DOF row is 22.18 real vs 16.07-16.22
ghost (relays) and the free-K bound 18.40-18.58 (minarc / skinnormal-shortk); this round adds lens A's 0-take result
for straight guides and lens B's free-K route bound.

### Carried (ideated, never screened)

None. The 21 ideated catalogue entries fall under measured closures (round 15's list). lazy-tongs-j2 and
pauldron-lame-telescope are angle-changing length changes on link 1 / J2: K-law class, bounded by the free-K numbers;
tape-spool-humeral, telescopes and tripods are translations (0 fold takes) or passive-translation counts > 2.

### Elsewhere, not to be duplicated

- Main round 15: take_bound_3dof (lens A), lowarm-adjpad-knuckle-3r (lens B), conecut-sidestep-knuckle-3r (lens C).
- The gen-9 desmo-conecut-knuckle-3r L2 CAD (user_style_desmo.py; judging in the lead's slot).

### Needs the user's say

- The 3-DOF ceiling and the 4-joint answer (round 15 lens A's table, then the blocker message).
- The transmission guard, the J1 seat rule and the 5-deg fold margin stay; no lens relaxes them.

## Round 104 results (Round J4, track jump; 2026-10-18 ~04:00 - ~08:50 UTC, closer)

I re-read the ledger with `tools/alignment_ledger.py get <id>` at 08:47 UTC, just before naming the winner:
- freek-oracle-route-knuckle-4r exits 0, verdict **WATCH** (skeptic 08:43:54Z; it was GAMED P1 at 07:37 when its
  verifier ran, the auditor lowered it to WATCH at 08:29 and the skeptic kept WATCH);
- armarc-relay-knuckle-4r, kfree-armarc-relay-4r and desmo-window-knuckle-3r exit 2 (no entry: dead rows, never
  audited);
- the lead, conecut-knee-knuckle-3r, exits 0, verdict WATCH (skeptic 2026-10-17 20:15 UTC).

No design is gamed now. 0 of 4 verifications refuted. The farm was closed: everything ran locally (<= 2 niced
processes). "Fast" is Bench(60,160) fast with kit checks; "frozen" is frozen exact Bench(110,360), the verification
protocol. Complexity is tools/simplicity.py v2.2. The bar was 18.28 (the lead); every verifier stated it by hand.

The four rows do not map one-to-one on the plan's lenses: lens A (guide-price-close) closed the straight-guide class at
step 0 and its one survivor was the cuff arm-arc relay (armarc), with kfree-armarc as its K-free sibling; lens B
(second-wall-route) ran as the free-K oracle and its cell B (freek-oracle); desmo-window is a buildable desmo stack (lens
C's complexity column; it is not the dog drive the plan priced, and the dog drive was not screened).

| design (lens) | verified number (frozen) | fast | reach / contacts | act / P / cx | ledger | outcome |
|---|---|---|---|---|---|---|
| freek-oracle-route-knuckle-4r (B: free-K oracle at the k33 seats; cell B = sensed K + a dowel on J3's own angle, K opening to hold it) | **16.20** (score 94.11) one reading, held 21.89; family reading 20.68 / 24.56; claim's mixed reading 17.35 / 22.67 | 9.56 (best of 8, 1-D sweep) | 0.7778 / 15 contacts (0.0375), follow 0.9545, ib14 0.8977 | 4 / 0 / 33.25 | WATCH | **round winner**; not a lead (4 joints; paired coin flip) |
| armarc-relay-knuckle-4r (A survivor: one-sided spring arm-arc relay at the cuff on the frozen lead) | **18.01** (93.45); continuity on contacts 17.76 | 8.79 | 0.7639 (275/360) / 11 contacts (0.0278), ib14 0.8838 (chain only 0.8466) | 4 / 0 / 52.0 | exit 2 | dead at the pre-registered kill (> 17.5) |
| desmo-window-knuckle-3r (C column: desmo drive, J2-first stop order, insert at link 1b plate top + 0.15) | **19.01** (93.09) at kit sampling density (18.80 area-exact; screened 20.43 over-dense); held 23.00-23.20 | 14.68 | 0.7278 (262/360) / 4 contacts, ib14 0.8927 | 3 / 0 / 16.25 | exit 2 | dead on the held kill line (+0.62..0.82 over the lead) |
| kfree-armarc-relay-4r (A sibling: K welded, plain O20 3R + cuff relay) | **26.42** (90.39); near-touch 27.53 | 18.45 | 0.6722 (242/360) / 9 contacts (0.0249) | 4 / 0 / 29.0 | exit 2 | dead at the kill; perfect-metal bound >= 19.72 |
| conecut-knee-knuckle-3r (the lead, for reference) | 18.28 (93.35), held 22.38 (22.43 at kit density) | 12.50 | 0.7278 (262/360) / 4 contacts | 3 / 0 / 18.5 | WATCH | stays the verified lead |

**Winner (by the rule): freek-oracle-route-knuckle-4r.** v_gap 16.20 frozen exact (score 94.11), held 21.89, 4 counted
joints (K is a sensed joint), 0 passive translations, complexity 33.25, ledger WATCH. It is the best number an
independent verifier confirmed this round and the first 4-DOF verified number under the 3-joint lead's 18.28, and the
best 4-DOF row on file (minarc-stop-knuckle-4r 19.54, skinnormal-shortk 18.58). **It does not replace the verified
lead.** (1) Under the user's 2026-10-17 ruling the 3-joint leaders are the real leaders, and this row has 4 joints at
complexity 33.25 against 18.5. (2) The paired difference against the lead is a coin flip on both benches: -2.08 bench
(CI90 [-4.99, 2.98], P 0.745), -0.49 held (CI90 [-2.70, 2.13], P 0.622). (3) The 2.08 bench lead is reach bought with
contact: 15 contact poses against 4 (13 only it has, 2 only the lead has). (4) It reads 16.20 only on the verifier's
model reading of the fold margin; on the family reading applied consistently it is 20.68 / 24.56, behind the lead.
(5) It failed lens B's pre-registered gate (>= 279 takes at <= 4 contacts, binders cleared by >= 0.2 mm): the oracle
reaches 280 connected takes with ~21 contacts and 5 binders touch at every legal K. Passed over as gamed: none. Its
row still reads `screened` (the verifier held it there under GAMED P1 at 07:41); the ledger no longer blocks calling it
verified, and the status flip is the lead's call. The generation CAD rule names it as J4's winner; before any CAD its
open items are the J3 dowel force, the K-spring hold (R17), the cuff twist with the stop engaged and a converged
search (q3max is a 1-D, 8-point fast sweep), and the groove goes at J3's own angle q3' 96.87 deg, not 86. No design
reached judge_all this round, so no EVOLUTION row; the generation CAD of record stays the lead's (gen-9 desmo-conecut).

**Alignment.** freek-oracle-route-knuckle-4r carries these WATCH reasons (auditor 08:29, skeptic 08:43; all numbers from
the saved per-pose dumps):
- *contact_depth / T5:* bench 15 contact poses, 78.55 mm summed, deepest 20.88 mm at ws 15/165/-60 (overhead); the
  lead has 4 and 20.24 mm (x3.88). Held 47 poses, 232.2 mm against 14 and 60.97 mm (x3.81). Contacts only this design
  has vs only the lead has: 13 vs 2 bench, 37 vs 4 held.
- *P1 (lowered from gamed):* the J3 stop was placed from claim-bench binders (binder_q3.json, poses 316 / 343 / 369 /
  423); the bench lead over the 3-joint lead is -2.08 (P 0.745) and held -0.49 (P 0.622), so about 24 % survives held
  out.
- *P4:* after the GAMED audit the verifier swapped the shared flood reading for a design-specific kin_nodes_model; the
  row moved 17.35 / 22.67 -> 16.20 / 21.89 and the held-out rank flipped. Stated openly and supported by the audit's
  measurement, but there is no change-log entry and judge_change cannot see it.
- *NEW-mixed-reading:* the row carries v_gap 16.20 (one reading) beside frozen_gap 17.35 and held_out_gap 22.67 (family
  reading).
- *NEW-stop-refusal:* the dowel refuses poses 343 and 423, which were kit contacts (-2.67 / -1.66 mm); read as contacts
  the claim is 16.68, so 0.48 of the 2.08 lead is these two poses.
- *M5:* in state 2 (32 bench / 61 held taken poses) J1 and J2 are free; per unit of K spring torque the cuff carries
  1.89-3.11x as a moment and the dowel 1.13-2.00x (0.08-0.25 N.m on the cuff at pick1's 0.04-0.08 N.m preload). The
  skeptic adds that state 1 also puts 1.9-2.6x on the cuff, so the load acts on 102 bench / 234 held poses (the whole
  knuckle-4r family). R17, the preload sweep and the dowel force are not run.
- *G1 (reported only):* gap 21.01 at 1 mm and 46.22 at 2 mm against the lead's 19.92 / 34.84; held at 2 mm 48.10 vs
  37.11; taken poses with metal under 2 mm 46 vs 33 bench, 91 vs 71 held; overhead p10 metal 1.08 mm bench, 0.18 mm held.
- *G6:* best v_gap of any 4-DOF row, 2.08 under the 3-joint lead, at 4 joints vs 3, complexity 33.25 vs 18.5, overhead
  15 vs 18 of 71 held.
- *NEW-stop-angle-label:* "q3max 86" is the model's q3 (cuff vs link 2); J3's own angle is q3' = 96.87 (phi 10.87 at
  every engaged pose). A groove cut at own angle 86 reads 11.22 fast instead of 9.56.
- *reporting / R4:* the dashboard still shows gap / sweep_gap 9.56 (score 96.52), the best of 8 fast fit-bench runs,
  6.64 below the verified 16.20 and above the 95 line.
- *sampling:* no per-part in-band record, so unsampled bodies cannot be ruled out.
- *dominance:* ahead on the plain gap, behind by about 11 at 2 mm (A1 gate retired; reported only).
- *Skeptic, missed by the audit:* the 5 lost bench clip frames (8 held) are one continuous run of overhead contact that
  follow does not price (v_follow 0.9545, half a frame above the 0.95 cutoff; the lead loses none); the consistent held
  overhead-contact count is 20 against the lead's 7; in state 2 J2 comes within 1 deg of its own stop at three poses.
- *Skeptic, refuted with measurements:* held_out (each reading against itself drops +5.68 / +5.31, under the 6.0 watch
  line), fold_margin and T3 (min th 5.91 bench / 6.50 held on every moving chain; where the family term binds J2 is free
  and >= 28 deg from its stop).

The three dead rows have no ledger entry; their verifiers' findings are carried here at watch level:
- **armarc-relay-knuckle-4r:** v_gap 18.01 reproduced exactly from the saved per-pose results, not re-run (2 other
  agents' processes on the box); continuity applied to contacts makes pose 206 (phi 0 -> 17 between neighbours) a
  blocked island: 17.76; an end dowel at PHI 10 reads 17.36-17.75 but PHI was picked on the claim bench (P1 class), not
  admissible; *dilution:* the relay shell is 24 % of the in-band samples, all in band, lifting 0.8466 to 0.8838 (chain
  only 21.73; same class as the lead's NEW-strap-dilution); near-touch 21.72 vs the lead's 19.92; the 11 contacts are
  the chain's own member 3 / hub 3 / neck (same with the ideal relay); *process:* the author used `pkill -f` once,
  against the rule (it matched only the author's own held-out run).
- **kfree-armarc-relay-4r:** v_* re-tallied from the author's frozen dump (the exact wear took 2337 s), not re-run;
  the model keeps hub K + links 1a / 1b as metal while the morphology is one bent bar (cannot matter: perfect-metal
  bound >= 19.72); the headline in-band counts the relay shell 100 % in band (chain only 30.6); the sweep was thin at
  PHI 25-40 / psi2 -13..-16 (verifier probes 23.93-30.54 fast) and sense -1 is not a missed region (21.39-29.06 fast,
  ideal); *red team:* the optimum sits on a jam cliff, 25 of 68 neighbours 0.3-2 deg away jam (7-76 jams, 34.6-132.1
  fast); continuity flood and gravity check not run (neither can lower the gap).
- **desmo-window-knuckle-3r:** *sampling density (a measurement change, not a design change):* the ring2 insert sector
  is sampled at 1 pt / 1 mm2, 4x the kit's 1 pt / 4 mm2, so the screened 20.43 / 24.61 over-weighted it; at kit
  density 18.80-19.01 / 23.00-23.20 (re-weighted from parts_ib14; the fast run backs it, near-touch 20.52 -> 19.02
  measured). The exact re-wear at kit density was stopped (~55 min projected at load 18). The honesty audit flagged only
  sparse sampling; the lead's cross-row density audit (tools/sample_density.py, 07:41Z) then found 9 of 13 rows over
  2x and re-weighted them: the lead 18.28 / 22.38 -> 18.28 / 22.43; desmo-conecut 18.98 -> 18.68; desmo-slipper 18.95
  -> 18.81; no row moves under the lead. v_inband10 is the screened value.
- **The lead's WATCH reasons** (reporting 12.5 shown as 95.45; T1, 16.56 points in the 1-2 mm shell; T3, held th margin
  5.006; NEW-strap-dilution 18.67; M5; NEW-self-reference; G4) stand; armarc wore the lead frozen and inherits them.
- **Process, all rows:** all four verifiers again stated the bar by hand: tools/workflows/exo-screen.js line 24 still
  reads BASE 68.93 / BIG 75.94 / LEAD default 30.35 (stale now in 11 of 12 verifications over J2-J4; the planner can pass
  `lead: 18.28` in the args). The near-touch objective was used in kfree-armarc's and desmo-window's searches. The
  auditor wrote ledger entries for the round winner (audit + skeptic) but none for the three dead rows.

**What the round measured (lessons).**
1. **A straight guide adds 0 fold takes, wherever it sits** (inside link 2, as the counted cuff slide, as a radial
   guide for hub 2): th is identical to 0.000 deg on 470 poses with the guide, and the rail costs ~+0.6 / 1.1 / 1.6 gap
   at travel 0 / 10 / 20 mm. A rail normal to J3 forms a planar 4-DOF group with J3 and the two knee pins, leaving one
   coordinate undetermined. The length-changing class is closed; only angle-changing variants touch the fold, and they
   are relays (lesson 2-4) or K laws (lesson 5).
2. **Relaying past the stretched wall from the arm side meets the same second wall as opening K from the scapula
   side.** armarc parks the chain at its wall posture with the arm turned further: 20 relayed bench poses, 13 taken at a
   median 1.81 mm (lead 3.5), 7 contacts, the same with the ideal relay. A one-sided spring relay cannot choose its wall,
   so it also relays folded-side poses into the skin (262 at -9.79 to -11.44 mm, 206 at -6.07). Kit-metal clearances
   run ~4 mm optimistic against the lead's real metal (relayed median 7.6-8.3 kit vs 3.25 real).
3. **The relay range is invisible on the fast bench and capped by the track's metal.** Ideal relay on the lead, frozen
   exact: 16.39 / 13.78 / 12.37 at PHI 20 / 30 / 45 (Bench(60,160) reads 4.89 at both 20 and 25). The real circular
   shell at PHI 30 reads 19.86 (worse than PHI 20's 18.01): a one-radius arc fits the arm only near the pad and touches at
   arm-down poses. On the K-free 3R the torso caps an arm-fixed arc at ~45 deg (9 of 14 fast contacts at PHI 45 are the
   un-relayed track in the chest, to -10.1 mm). The knee stack's 4.59-5.4 mm climb onto a carriage costs the chain
   0.055-0.07 of in-band.
4. **A K-free cuff relay is kinematically worth 8 points over the knuckle lead, with no hardware:** an ideal 75-deg
   relay on a plain O20 3R at the lead's seats reads 10.22 frozen exact (304/360, overhead 14/28). It is the only bound
   on file under 13.75. Every real arm-fixed track long enough to reach it has hit the torso or the arm-down skin. The
   J2 window shift psi2 (J2's rest axis turned about J1, a2 57.2 -> 62-64.5) is worth 8-16 fast points on the welded
   plain 3R alone (39.80 -> 23.65-31.83).
5. **Every K-side lever at the k33 seats is bounded at 17.25 connected plain / 21.46 near-touch** (per-pose oracle K on
   the legal self-motion, every model check run per sample; frozen exact Bench(110,360)). The second wall is
   seat-level parking of link 2 / hub 2 at the external-rotation binders 117 / 119 / 129 (plane -90..-75, elev 45-60,
   axial 120-135): they touch at every legal K (best -1.14 / -10.74 / -5.87 mm). An anterior link-2 corridor (+12 deg)
   lifts them only 0.7-2.3 mm and costs in-band (18.71 connected). ER binders want less K, IR binders (343 / 423) want
   K at stop B, so a J3 own-angle stop serves only the IR side. A stop can beat a static oracle by refusing poses, and
   that bench gain did not hold out (cell B +1.26 connected bench, +0.70 held over its own kit).
6. **Oracle hazard:** if "lost" outranks "contact", a per-pose oracle parks contact poses at refused configurations and
   reads ~1.7 points optimistic (15.27 vs 16.96 here). Only legal configurations may compete, and member 3 / the knee
   move with K (J3's line misses GH by ~15 mm).
7. **Sampling density moves in-band either way.** Over-dense out-of-band metal weighs extra (desmo ring2 at 4x: +1.45
   screened vs +0.31-0.44 real for the 3.04 mm lift); a buildable desmo must keep stage 1 inside the O20 footprint
   (pitch_hi + 1.56 <= 10) or under link 1b's plate top, and at the verified law no legal pin has pitch below ~9.7, so
   the desmo lever left is the drive geometry (crank axis dR, ratio g, PA budget). The J2-first stop order itself costs
   0 reach.
8. **Machinery:** batching contact-only parts into one exact distance call per pose made armarc's exact hardware-path
   wear ~5x faster (548 s, reproduces 18.01 exactly); Bench.dist accepts batched point sets, so per-pose exact scans of
   many K samples are affordable.

**The 4-joint picture after J4 (for main round 15 lens A's take-bound table and the user's blocker).**
- free-K oracle at the k33 seats (any K law, spring, J3 split or sensed K): 17.25 connected plain / 21.46 near-touch,
  280 connected takes with ~21 contacts; cell B (sensed K + J3 own-angle dowel) 16.20 bench / 21.89 held, 4 joints,
  cx 33.25, paired coin flip against the lead;
- arm-side relay on the lead: real 18.01 (275 takes, 11 contacts), ideal 16.39 / 13.78 / 12.37 at PHI 20 / 30 / 45,
  real PHI 30 19.86;
- K-free cuff relay on a plain O20 3R: real 26.42 (242 takes), ideal 75-deg bound 10.22 (304 takes);
- straight guides: 0 fold takes;
- earlier: relays under the lead 22.18-32.92, cap null-space 57.70, minarc 19.54, skinnormal-shortk 18.58.
For the first time a 4-DOF verified number (16.20) sits under the 3-joint lead's 18.28 on the bench, but not
significantly (P 0.745 bench, 0.622 held), and it buys its reach with 15 contacts against 4. No 4-DOF row reaches 95;
the only bound under 13.75 is the hardware-free K-free relay.

**Next focus (round J5, track jump).** The score has not reached 95 (best verified 16.20 at 4 joints, 18.28 at 3; 95 is
13.75). Measured reason: every K lever and every arm-fixed relay is capped at 16.2-18.3 by metal parking at the second
wall (lessons 2, 3, 5), while the only sub-13.75 bound (10.22) is a K-free relay whose arm-fixed track hits the torso.
- **Lens a, the carriage-borne relay rail (kfree-armarc's unmeasured lever):** a short curved rail on the pad side that
  runs on rollers fixed to the arm at lateral stations only, so no metal covers the medial arc until the relay turns.
  Price first with armarc's rule: relayed poses must clear the skin by >= 2 mm on the lead's REAL metal, the carriage
  needs no knee-stack lift, and the relay must be two-sided or stopped (a one-sided spring relays folded poses in).
  Decide relay range on frozen exact, never on Bench(60,160). Gate 0: frozen exact <= 15, kill > 17.5. It is a 4th
  joint: a pass goes to the user as the 4-joint answer, not a lead change on its own.
- **Lens b, psi2 on the 3-joint lead (cheap, <= 30 min):** the J2 window shift bought 8-16 fast points on the welded
  plain 3R; re-fit the lead's chain with psi2 free on the near-touch objective (envsel), wear frozen exact once, report
  paired vs the lead. Check first whether the lead's a2 / seat fit already spans it.
- **Lens c, the second wall at the ER binders (117 / 119 / 129) with the free-K oracle as the instrument:** only moves
  not on the round-15 dead list (back-seat J3 / hub-K / link-2 seat moves, link-2 root / whole-bar radial lifts);
  pre-register the oracle gate (>= 279 takes at <= 4 contacts, binders cleared by >= 0.2 mm) before any claim, and never
  place a stop from claim-bench binders (freek's P1).
- **Machinery before the next claim:** pass `lead: 18.28` to the verify template (or fix the default in exo-screen.js
  line 24); have the auditor write an entry for every verified row, dead or not; correct the dashboard's 9.56 for
  freek-oracle (verified 16.20); record the verifier's fold-reading change in the change log; re-wear the desmo pair at
  kit density on the exact path when the box allows.

### Needs the user's say (with J4's numbers)

- The 4-joint question: freek-oracle-route-knuckle-4r is the first 4-joint row under the 3-joint lead on the bench
  (16.20 vs 18.28; held 21.89 vs 22.38), a coin flip that trades 13 extra contacts for reach; the only path to 95 on
  file is a hardware-free bound (K-free relay 10.22) that needs a 4th joint. Round 15 lens A's table carries the 3-joint
  side; the blocker message goes to the user from there.
- The transmission guard, the J1 seat rule and the 5-deg fold margin stay; no lens relaxed them.

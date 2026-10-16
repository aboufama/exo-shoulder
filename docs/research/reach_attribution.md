# Reach attribution: where the leaders lose the workspace, and what each lever is worth (2026-10-16)

User, 2026-10-16: "the reach numbers at 60s just isn't good, it seems like they're plateauing near the top, lets try
to max these out as much as we can". This note measures where every lost pose goes, what each topology could reach
at most, and what each lever buys at the in-band bar. It changes no design and no rule.

**User rulings that landed while this ran (2026-10-16 ~05:50 UTC, CLAUDE.md):** (1) the fold margin is now **5 deg** for
the unpowered MVP1 (was 10) - section 3 has every leader at 10 and at 5, and the red team of the feel at the edge;
(2) **O20 hubs only** - spine-parked-j2-3r's verified 34.29 uses O15 J2 / J3 hubs and does not stand (its attribution
below is kept as the plain-3R reference); (3) complexity re-weighted (passive translation 2, sliding pair 1, passive
rotation 1) - the complexity column uses the new weights; (4) J1 seats on the back of the shoulder or the acromion top
only - all four leaders seat J1 on the acromion top (bvec az 93-106, el 65-67); the kinematically best seats of
section 2 (J1 posteromedial, low) are back-of-shoulder seats, the far-end-posterior history says what the skin does
there.

Instruments (all in `docs/research/reach/`, data next to them):

| script | what it measures | output |
|---|---|---|
| `attribute.py` | wears a leader's VERIFIED configuration with its verifier's frozen protocol (fit Bench(60,160) fast, worn on Bench(110,360) exact, verifier extra checks applied) and gives every pose its first cause, in the model's own check order | `runs/<leader>_m<margin>[_refit].json`, `<leader>_poses.csv` |
| `analyse.py` | the attribution tables and the fold-margin sensitivity from the runs | `summary.json` |
| `ceilings.py` | orientation-level reach ceilings on the 360 workspace poses: the fold law at the leaders' seats, over all seats, with a per-pose-free J1 rocker and with a two-state arc relay | `ceilings.json` |
| `frontier_mine.py` | reach vs in-band frontier from every sweep / CMA history (Bench(60,160) fast) + the 4-DOF lens histories | `frontier_mined.json` |
| `relay_parking.py` | where hub 2 must sit when a relay state rescues a folded pose | `relay_parking_<leader>.json` |
| (inline) | seat re-tuning near the leaders' seats, arcs fixed, on the 360 poses | `seat_local.json` |

The fold law used throughout (docs/FINDINGS.md "The J2 fold is not a hard limit"): any 3R chain that reproduces the
arm's rotation closes a pose only if th = angle(J1, J3) lies in [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m],
m = 10 deg on the bench. Orientation depends on the axis directions only, so cuff slides, knees and offsets do not move
it. Below the window the dyad is folded (J1, J2, J3 coplanar with the links overlapping), above it stretched.

## 1. Attribution: every lost workspace pose, by first cause (Bench(110,360) exact, verified frozen shapes)

The order is the models' own: fold window -> second closure window (pin knee / raglan knee: the knee's two-circle
reach and angle; knuckle: knuckle and cuff circles) -> continuity along the 10 fps fit clips (a branch flip = the jam
of a passive follower) -> closure residual -> part-part clearance -> skin requirement (a pose the fit gave up) ->
contact (metal < 0 mm, incl. the verifiers' top / crown / wall faces) -> the verifiers' extra checks. The fold split is
exact from the kinematics (`fold_split_kinematic.json`, it equals every verifier's fold count); the rest is from the
model runs (`runs/<leader>_m10.json`, per-pose CSV `<leader>_poses.csv`). The runs reproduce the verified numbers
exactly: pin knee 30.35 (reach 0.6056, in-band 0.9043, contact 0.0091), knuckle 31.89 (0.6167, 0.8705, 0.0061),
spine-parked 34.29 (0.5944, 0.8781, 0.0154); local and farm runs are identical pose by pose. Raglan does NOT reproduce
(note below).

| leader (v_gap, v_reach) | workspace lost (of 360) | fold, folded side | fold, stretched side | knee / cuff window | jam (flip) | part collision | skin req. | contact | verifier extra |
|---|---|---|---|---|---|---|---|---|---|
| pin knee k4598 (30.35, 0.606) | 142 | 57 | 76 | 4 | 0 | 2 | 0 | 3 | 0 |
| raglan knee (31.52 verified, 0.600; today's model 32.37, 0.603 - note below) | 143 | 60 | 76 | 0 | 0 | 3 | 0 | 4 | 0 |
| knuckle cufflink (31.89, 0.617) | 138 | 55 | 77 | 2 (cuff) | 0 | 2 | 0 | 2 | 0 |
| spine-parked k7008 (34.29, 0.594) | 146 | 59 | 81 | - | 0 | 1 (K6, 1 mm radial) | - (kit: quantile q 0.972 instead) | 5 (incl. top faces) | - |

**The fold takes 93.7 % (pin knee), 95.1 % (raglan), 95.7 % (knuckle) and 95.9 % (spine-parked) of the lost workspace.** Everything else together is
6-9 poses (1.7-2.5 points of reach). Clip frames: the pin knee follows 110 / 110; the others lose 3-5 clip frames, all
to the fold (raglan 3 folded, knuckle 4 folded, spine 5 stretched).

By region (measured per pose; raglan = today's model):

| region | n | pin knee taken / lost: folded, stretched, other | raglan (today's model) | knuckle | spine-parked |
|---|---|---|---|---|---|
| overhead (elev >= 140) | 28 | **7** / 7, 10, knee window 4 | **7** / 9, 10, parts 1 + contact 1 | **7** / 9, 10, cuff 1 + contact 1 | **5** / 8, 10, contact 4 + parts 1 |
| across the body (plane >= 100, elev >= 40) | 68 | **20** / 1, 47, 0 | **20** / 0, 48, 0 | **20** / 0, 48, 0 | **16** / 1, 51, 0 |
| behind the back (plane < -30, elev > 20, or a "back" clip) | 25 | **17** / 1, 5, contact 2 | **16** / 2, 5, contact 2 | **17** / 1, 6, contact 1 | **17** / 2, 5, contact 1 |
| the rest (none of the three; 6 poses are both overhead and across) | 245 | 174 / 48, 20, parts 2 + contact 1 | | | |

* **Across the body is a pure stretched-side loss** (47-51 of 68, th up to 173-179 deg against a window top of 101-104):
  horizontal adduction swings the humerus-fixed J3 away from the scapula-fixed J1 beyond the two arcs' reach. Only a
  longer a1 + a2 (or a second, longer state) rescues it; the margin cannot (it moves the top 3-8 deg).
* **Overhead fails on both sides** (7-9 folded at th 24-37, 10 stretched at th 110-142) - the overhead poses alone
  span th 18-146. No shift of the window helps; only a wider one (min(a1, a2) larger) or two states.
* **The pin knee's 4 knee-window poses are all elevation 165** (#211, #237, #264, #345): hub 3's in-plane drift reaches
  65.8-70.1 mm against the knee's lE + lc - 1 = 66.0 mm (knee angle 157-180 deg). Measured, a longer knee does not
  rescue them: at lc 28 the refit re-centres the knee and the same 4 fail; at lc 31 two are admitted and both put metal
  0.8 / 1.3 mm into the skin (`runs/pin-knee_m10_lc28.json`, `_lc31.json`).
* **Behind the back** loses 5-6 to the stretched side and the pin knee 2 to contact (#129, #139: plane -75 / -60,
  elevation 60, axial 105-120: metal 0.5-1.7 mm inside; #129 is also the spine-parked contact).
* **The plain 3R loses half of its in-window overhead to the skin**: spine-parked has 10 overhead poses in its window
  and takes 5 - #289, #318, #345, #371 (plane 45-90, elevation 150-165) are contact (0.6-4.4 mm inside, link 2's top
  face among them) and #211 jams parts. The pin knee takes 7 of its 11 in-window overhead poses and loses the other 4
  to its knee reach, not to the skin.

* **Red team: raglan-knee-3r's verified 31.52 no longer reproduces (32.37 today, in-band 0.886 instead of 0.902).**
  Its routed links are injected by replacing `S.Geometry` in its private module copy (raglan-knee-3r.py line 119), but
  since the 04:07 UTC per-hub-radius change the pin-knee model builds its links with its own `_Geo(S.Geometry)` class,
  bound at import time before the raglan swap - so the raglan model now silently runs great-circle links. The verified
  number (04:05) predates the change. The fold attribution is unaffected (kinematic); the raglan model / verifier needs
  `_Geo` to inherit the routed `add_links` (or the raglan module to patch `PK._Geo`) before it is re-run or polished.

Conditioning over the poses the leaders take today: sigma_min of [u1 u2 u3] min 0.288 / p5 0.347 / median 0.461 (pin
knee) and 0.281 / 0.323 / 0.434 (spine-parked); the J2 transmission angle never drops below 35.7 / 37.2 deg.

## 2. Reach ceilings per topology (360 workspace poses of Bench(110,360), m = 10 deg unless stated)

**The fast-to-frozen reach loss is kinematic, not proximity.** At the SAME seats and arcs, the share of workspace poses
inside the fold window is 0.69-0.71 on Bench(60,160)'s 160 poses and 0.61-0.63 on Bench(110,360)'s 360 (overhead
2 / 12 vs 9-11 / 28). The CMA tuned the window edges to the 160-pose sample; the frozen loss (pin knee fast 0.694 ->
frozen 0.606) is that, not a skin effect.

| leader (seats as verified) | arcs a1 / a2 | window th | th of the workspace 5-95 % | in window: ws / overhead | verified reach |
|---|---|---|---|---|---|
| pin knee k4598 | 40.1 / 72.3 | 42.2-102.4 | 26.3-140.5 | 0.631 / 0.39 | 0.606 |
| raglan knee | 39.6 / 74.9 | 45.3-104.4 | 27.5-143.1 | 0.622 / 0.32 | 0.600 |
| knuckle cufflink | 40.1 / 72.6 | 42.4-102.7 | 25.9-141.8 | 0.633 / 0.32 | 0.617 |
| spine-parked k7008 | 37.6 / 73.6 | 46.0-101.2 | 26.6-142.7 | 0.611 / 0.36 | 0.594 |

(The task brief's [43.1, 104.4] window for spine-parked is the CMA-B shape's, a1 40.7; the verified k7008 has a1 37.6.)
The overhead poses alone span th 18-146 deg: they fall off BOTH ends of the window, so no single shift of the window
rescues overhead; only a wider window (or a second one) does.

Ceilings by topology class. "Kinematic" = fold law only, no skin; "in-band" = the best reach any measured
configuration of that class reaches with in-band14 >= 0.88 and follow >= 0.95 (Bench(60,160) fast, from the sweep
histories; frozen Bench(110,360) exact where verified):

| class | kinematic ceiling (no proximity) | best reach at in-band14 >= 0.88 (fast) | frozen exact (verified unless noted) |
|---|---|---|---|
| plain 3R, best seats anywhere | 0.928 at arcs 40/40, 0.969 at 45/45, 0.989 at 50/50, 1.000 at a1 + a2 >= 130. The seats are J1 posteromedial and low (bvec(-36..-42, 12-36)) with J3 pointing back up the arm (wdir(105-155, -126..-156)), or J1 straight down with J3 along the arm: axes through the trunk and axilla | fold-frontier seats: never above in-band 0.51 (fold-sph3r, raglan-routed: hubs 0 % in band) | - |
| plain 3R at the leaders' arcs (40 / 73), best seats | 0.74-0.78 (J1 bvec(-114, 16), J3 wdir(60, 138)) | - | - |
| plain 3R at the leaders' seats, arcs free | same sum rebalanced to 55 / 57: 0.76-0.78; shorter arc 65-67 for 90 %; 88-91 / 88-91: 0.98 | spine-parked 0.644 (a1 37.6; every in-band >= 0.88 config has a1 35-45; a1 40-45 best 0.589) | spine-parked 0.594 (in-band 0.878) |
| plain 3R, seats re-tuned locally on the 360 poses (arcs fixed) | +-5 deg: +0.014-0.025; +-10 deg: +0.020-0.042; +-15 deg: +0.036-0.064 | (the Bench(110,360) polish in flight measures it) | - |
| 3R + passive planar closure (pin knee, raglan knee, knuckle) | = plain 3R at the same seats (0.62-0.63 at the leaders') | pin knee 0.700 (0.694 at 0.90, 0.719 at 0.80: flat - fold-capped), raglan 0.700, knuckle 0.681 | pin knee 0.606 (0.904), raglan 0.600 (0.902), knuckle 0.617 (0.871) |
| 3R + 2 cuff slides (osn) | = plain 3R | none: in-band never above 0.81 in 9825 tries | 0.611 (in-band 0.784) |
| 3R + per-pose-free J1 rocker, travel beta (pivot scanned) | beta 5: 0.65-0.68, 10: 0.68-0.73, 15: 0.73-0.76, 20: 0.77-0.81, 30: 0.84-0.88 (overhead 0.68-0.82 at 30) | stop-relay-rocker-3r 0.700 at in-band 0.881 (contact 0.055; 12.3 k tries, round 4 in flight; its deltoid-pivot relay: kinematic 0.95, in-band 0.20) | - |
| 3R + two-state arc relay (a detented mid-joint in link 1: a1 -> a1') | a1' 77-84: 0.93-0.95, overhead 0.89-1.00; relay on a2 (a2' 129-132): 0.82-0.84 | unmeasured (no model); hub-2 parking below | - |
| 3R + coupled schedule (dwell four-bar knee, arc knee) | <= the per-pose-free rocker of the same travel | dwell four-bar: none (0.700 at 0.84, 5.7 k tries); closure-set arc knee: none (refuted) | arc knee 0.589 (in-band 0.486) |
| redundant 4R, spring-centred sensed 4th (4-DOF lens park4, 450 tries) | ~1.0 (a 4R folds only with all four axes coplanar) | 0.644 (one config, contact 0.053); 0.781 at in-band 0.864, 0.788 at 0.842 | 0.750 at in-band 0.864, contact 0.038, gap 22.36 (self-measured by the lens, NOT verified) |
| redundant 4R, ring 4th (lens) | ~1.0 | none (in-band <= 0.79) | 0.683 (in-band 0.786, self-measured) |

Reading: every 3-joint class sits on the same fold-capped ceiling (0.61-0.63 at the seats proximity allows); the
kinematic headroom (0.93-1.00) exists only at seats or arcs that put hub 2 (or a pivot) over the raised arm.

## 3. Fold-margin sensitivity (10 / 7 / 5 / 2 deg); 5 is the MVP1 rule since ~05:50 UTC

The bench takes a pose only if th is at least m = 10 deg inside the closure limits. That margin is a conditioning
rule: at the window edge the J2 dihedral (the spherical dyad's transmission angle) and the smallest singular value of
the orientation Jacobian U = [u1 u2 u3] (the arm's angular velocity is U q-dot, so 1 / sigma_min is the worst joint
rate per unit arm rate) are set by (a1, a2, th) alone:

| margin | sigma_min at the window edges | joint rate per arm rate (1 / sigma_min) | transmission angle at the edges (from folded / from stretched) | kinematic reach at the seats: pin knee / raglan / knuckle / spine (overhead pin knee) |
|---|---|---|---|---|
| mid-window (best) | 0.46-0.49 | 2.0-2.2 | 90 | - |
| 10 (bench) | 0.276-0.296 | 3.4-3.6 | 34-36 / 43-44 | 0.631 / 0.622 / 0.633 / 0.611 (0.39) |
| 7 | 0.229-0.249 | 4.0-4.4 | 28-30 / 36-37 | 0.664 / 0.661 / 0.667 / 0.647 (0.39) |
| 5 | 0.193-0.212 | 4.7-5.2 | 23-25 / 30-31 | 0.681 / 0.672 / 0.689 / 0.658 (0.43) |
| 2 | 0.120-0.134 | 7.5-8.3 | 14-15 / 19 | 0.722 / 0.714 / 0.736 / 0.681 (0.46) |
| 0 (closure limit) | 0 | infinite | 0 / 0 | 0.73 / 0.73 / 0.75 / 0.70 |

So the WHOLE fold margin is worth at most +0.09-0.11 of kinematic reach at the leaders' seats; going from 10 to 7
is +0.03-0.04, to 5 +0.05-0.06. The transmission angle a linkage designer keeps above ~30-40 deg drops to 28-36 at
m = 7 and 23-31 at m = 5: in MVP1 (unpowered, the arm drives the chain through the cuff) the wearer back-drives J2
through a 4-5x lever near the edge, and in MVP2 the J2 motor needs that rate.

Measured on Bench(110,360) exact (`runs/<leader>_m<m>.json`: the margin-10 shape frozen, only the window widened;
`_refit`: shape refitted on Bench(60,160) at the new margin, then worn frozen):

| leader | m 10 (verified) reach / gap | m 7 frozen | m 5 frozen | m 2 frozen | m 7 refit | m 5 refit | overhead poses gained (any run) |
|---|---|---|---|---|---|---|---|
| pin knee | 0.606 / 30.35 | 0.617 / 30.11 (+0.011) | 0.625 / 29.26 (+0.019) | 0.631 / 29.26 (+0.025) | 0.628 / 29.83 (in-band 0.880) | 0.636 / 29.54 (in-band 0.877) | 0 |
| raglan knee (current model, see the note below) | 0.603 / 32.37 | 0.628 / 30.21 (+0.025; follow 0.973 -> 0.991) | 0.631 / 29.93 (+0.028) | 0.647 / 29.38 (+0.044) | 0.628 / 30.32 | 0.631 / 30.04 | 0 |
| knuckle cufflink | 0.617 / 31.89 | 0.642 / 30.29 (+0.025; follow 0.964 -> 0.991) | 0.647 / 30.03 (+0.031) | 0.664 / 28.89 (+0.047) | 0.647 / 30.52 (in-band 0.856) | 0.664 / 29.10 (in-band 0.856) | 1 (refits) |
| spine-parked | 0.594 / 34.29 | 0.614 / 33.78 (+0.020; contact 0.015 -> 0.030) | 0.617 / 33.49 (+0.022) | 0.628 / 32.91 (+0.033) | 0.617 / 33.65 | 0.594 / 34.77 (refit loses 8 ws + 4 clip frames to parts) | 1 (m 7 refit) |

Conditioning at the poses each margin actually gains (all four leaders): sigma_min min / median 0.236-0.268 / 0.263-0.283
at m 7, 0.206-0.246 / 0.254-0.275 at m 5, 0.134-0.152 / 0.247-0.261 at m 2; transmission angle min 28.7-38.8 deg at
m 7, 24.8-36.3 at m 5, 19.5-21.3 at m 2. The pin knee's own m 7 / m 5 frozen runs, pose by pose:

| margin (pin knee k4598, shape frozen at its margin-10 fit) | reach | gap | contact | ws taken (net gain) | poses newly inside the window: taken / contact / parts / knee | sigma_min at the poses gained (min / median) | transmission at the gained poses (min / median) |
|---|---|---|---|---|---|---|---|
| 10 (verified) | 0.6056 | 30.35 | 0.0091 | 218 | - | taken poses: 0.288 / 0.461 | taken poses: 35.7 / - |
| 7 | 0.6167 | 30.11 | 0.0178 | 222 (+4) | 12: 4 / 3 / 4 / 1 | 0.268 / 0.283 | 38.8 / 41.1 |
| 5 | 0.6250 | 29.26 | 0.0176 | 225 (+7) | 18: 7 / 3 / 6 / 2 | 0.220 / 0.268 | 31.2 / 38.8 |

**Measured, the margin buys a third to a half of its kinematic promise**: +0.011-0.025 of reach at m 7 and
+0.019-0.031 at m 5 against +0.033-0.039 / +0.047-0.056 kinematic, gap -0.2 to -2.2 at m 7, and **no overhead pose in
any frozen run** (one in two refits). Two mechanisms eat the rest. **The folded side is closed by the links, not by
the kinematics**: every newly admitted folded-side pose of the pin knee (th 38-42) fails on a part collision (link 1
and link 2 stack on each other as the dyad folds) or on the knee window. The stretched-side poses (th 102-107:
behind the back, across the body, mid-range) are the ones gained, some lost to the skin with the frozen shape (contact
doubles for spine-parked). Refitting at the new margin trades in-band for reach (pin knee m 7 refit: reach 0.628 but
in-band 0.880; knuckle 0.856). The raglan / knuckle gap gains are mostly follow (their folded clip frames come back).
**Re-measured at the user's new 5 deg (a MEASUREMENT change, not a design change)**: pin knee 30.35 -> **29.26**
(frozen shape) / 29.54 (refit), knuckle 31.89 -> **30.03** / 29.10, raglan (today's model) 32.37 -> 29.93 / 30.04,
spine-parked (O15, does not stand under O20-only) 34.29 -> 33.49 / 34.77. **Red team of the feel at the edge (MVP1,
unpowered):** at 5 deg the poses the margin adds sit at sigma_min 0.21-0.25 (the arm must turn J2 4-5x faster than
itself, and the cuff force that back-drives J2 is amplified by the same factor through a 25-36 deg transmission
angle); the edge of the 5 deg window itself is sigma_min 0.19-0.21 / transmission 23-31 deg. Put a soft J2 end stop
(elastomer) at the 5 deg line so the wearer meets a cushion, not a toggle; m 2 (sigma_min 0.12-0.13, 8x, 14-19 deg)
is not a mechanism. Even at 5 deg the margin is not what the plateau is made of (+0.02-0.03 measured).

## 4. Levers, ranked by measured reach gain at in-band14 >= 0.88

Reference: the pin knee, fast frontier 0.700 at in-band 0.88 (Bench(60,160)), frozen exact 0.606 at in-band 0.904.
"Measured" means a model run with every proximity check; kinematic headroom is the fold law alone. Complexity is
tools/simplicity.py with the user's 2026-10-16 weights (lower = simpler; the pin knee is 19.5, the plain 3R 0).

| rank | lever | measured reach gain at in-band >= 0.88 | kinematic headroom | in-band cost (measured) | complexity | buildability |
|---|---|---|---|---|---|---|
| 1 | **Per-pose-free J1 rocker / stop relay** (stop-relay-rocker-3r, round 4, 12.3 k tries) | **+0.056 over its plain-3R base** (0.644 -> 0.700 at in-band 0.881, fast; contact 0.055; = the pin knee's 0.700, not above it; frozen not yet measured) | beta 10: +0.07-0.09, 20: +0.16-0.18, 30: +0.23-0.24 | contact 0.055; its own screen: the gained poses put hub 2 / the pivot hub over high skin | 12.5 | rocker + stops + spring; the mode switch is force-closed (sag torque vs preload) |
| 2 | **Fold margin 10 -> 5** (the MVP1 rule since ~05:50 UTC) | +0.019-0.031 (pin knee 0.606 -> 0.625, gap 29.26; knuckle +0.031, raglan +0.028, spine +0.022) | +0.047-0.056 | in-band 0 to -0.006 frozen (refit: -0.02 to -0.03); contact up to 0.018-0.030; the extra folded-side poses jam parts | +0 | sigma_min 0.21-0.25 at the gains (5x joint rate), transmission 25-36 deg: poor |
| 3 | **Fold margin 10 -> 7** (superseded by the 5 deg ruling; kept for the curve) | +0.011-0.025 (pin knee 0.606 -> 0.617, gap 30.35 -> 30.11; raglan / knuckle +0.025, gap -2.2 / -1.6; spine +0.020) | +0.033-0.039 | in-band 0 to -0.006 frozen; contact 0.009 -> 0.018 (pin knee), 0.015 -> 0.030 (spine); the folded-side gains jam link 1 on link 2 | +0 (J2 hard stops 7 deg from the fold) | same parts; sigma_min 0.24-0.27 at the gains, transmission 29-39 deg |
| 4 | **Seats re-tuned on the full 360-pose workspace** (the Bench(110,360) polish in flight; arcs fixed) | pending (the polish measures it) | +0.014-0.025 within 5 deg of the seats, +0.020-0.042 within 10, +0.036-0.064 within 15 | small for 3-5 deg moves (the CMA's own basin) | +0 | unchanged parts |
| 5 | **Non-fold fixes** (contact, parts, cuff) | <= 0.008 each (2-5 poses per leader) | - | - | +0 | local part edits |
| 6 | **Coupled schedule** (dwell four-bar knee 5.7 k tries; closure-set arc knee) | none at 0.88 (dwell: 0.700 at in-band 0.84 vs the plain base's 0.688, +0.012; best gap 26.86 fast at in-band 0.843; arc knee refuted, 0.589 at 0.486) | <= the rocker of the same travel; the dwell moves only the window's low end | the four-bar / cam lifts hub 2 or sweeps the cuff link over the arm | 16 (dwell four-bar), 30 (arc knee) | six-bar / cam: pins only |
| 7 | **Longer knee link** (pin knee: lc 24.9 -> 28 / 31 mm, refit + frozen exact) | **0** (lc 28: the refit re-centres the knee, the same 4 elevation-165 poses fail its window; lc 31: 2 of them admitted, both touch the skin 0.8 / 1.3 mm, gap 30.94) | +4 overhead poses (+0.011) | contact 0.009 -> 0.015 at lc 31 | +0 | same part |
| 8 | **Two-state arc relay** (a detented mid-joint in link 1, a1 40 -> 77-84) | not modelled (hub-2 parking gate measured: next column) | **+0.30-0.33 (0.93-0.95; overhead 0.89-1.00)** - the largest kinematic headroom of any <= 4-joint option | hub 2 cannot serve both states at one level (pin knee seats, `relay_parking_pin-knee.json`): state A needs it at 51-55 mm (p10-p90; fitted F 60.9), the 114 poses only state B closes need median 70.5, p90 205 mm; at F <= 60 only 30 % of them clear, at <= 75 59 % (then state A sits 20 mm off the skin). Parking bound: ~+0.09-0.14, not +0.32 | 9.5 (a detented passive rotation, its state sensed; 12.5 if the detent counts as a spring) | detent hinges exist (ball-detent / index plunger); the trigger that flips the state is unsolved |
| 9 | **Redundant 4R, spring-centred 4th** (4-DOF lens park4; 4 joints = at the DOF cap) | **-0.056 at in-band 0.88** (0.644 vs 0.700, one config, contact 0.053); +0.075 at in-band 0.86 (0.781 vs 0.706) | ~1.0 | link 3 0.51 in band, hub 4 0.86; contact 0.038 | 12.5 (passive sensed spring-centred 4th) or 28.5 (4th active) | one more O15 hub + a centring spring; 4th deflects p95 56 deg, max 86 (the spring must carry the chain) |
| 10 | **Longer or balanced arcs on the plain 3R** (the fold window is 2 min(a1, a2) - 20) | **-0.055** (spine-parked history: every in-band >= 0.88 config has a1 35-45; a1 40-45 best 0.589 vs 0.644 at 37.6) | +0.13-0.15 at the same a1 + a2 rebalanced to 55 / 57; 65-67 shorter arc for 90 % | hub 2 leaves the skin (a1 >= 55: hub 2 level 186-400 mm, spine-parked doc) | +0 | unchanged parts |
| 11 | **2 cuff slides** (osn) | excluded: in-band never above 0.81 (9825 tries) | = plain 3R | stage parts 62-70 %, bridge 0 % | 17.75 | crossed rails |

Reading the ranking:

* **The relay's parking gate, measured (pin knee seats, a1 40.1 <-> 84, exact skin, both branches).** In state A the
  J2 ray needs hub 2 at 51-55 mm (p10-p90, branch -1; the fitted hub sits at 60.9). In state B the 114 workspace poses
  only B closes (17 of them overhead) need it at a median 70.5 mm, p90 205 mm (overhead median 67; the other branch is
  worse: median 80, overhead 113). A GH-ray hub has one level on its link, so F must lie within 12 mm above every
  requirement it serves to stay in band: at F ~ 60-65 state A stays in band and 30-45 % of the B poses clear (+0.09 to
  +0.14 of reach before links, hub 1 and the knee are checked); covering more of B lifts hub 2 out of band in A. The
  relay is a real lever, but a ~+0.1 one, not +0.3, unless hub 2 moves between states too. The same gate at the other
  leaders' seats (farm, `relay_parking_<leader>.json`): state A 51-57 mm, state B median 70-73 / p90 153-226 mm, 27-35 %
  of B clear at 60 mm and 55-60 % at 75 mm - the same answer at every seat the leaders use (a second, sliding hub
  level = a passive translation along the J2 axis, 1 slide, complexity +2-3 under the new weights).
* **Benches:** the rocker / dwell rows are Bench(60,160) fast (their histories); the margin / knee rows are frozen
  Bench(110,360) exact. On the 160-pose bench every class tops out at 0.70-0.72 at in-band >= 0.80.
* **By measured gain at the bar, the best levers are the small ones** (margin, seats, non-fold fixes: +0.01-0.03 each
  measured or bounded, +0.04-0.07 together at most; the longer knee measured 0). By kinematic headroom the order is reversed: the relay (+0.30-0.33),
  the 4R (~+0.37) and the rocker (+0.16-0.24 at 20-30 deg) hold all of it, and none of them has a configuration at
  in-band >= 0.88 yet. Their in-band cost is the whole question, and it is a parking question: where hub 2 (or the
  pivot) sits in the poses the second state rescues.
* **Complexity** (new weights): the small levers cost 0 points; every second-window lever costs 9.5-12.5 (one passive
  rotation, sensed, sprung or detented) - a 4th joint is within the user's cap ("at most 4 DOF ... 4 joints") but
  against "push for 3 before settling for 4", and the golden target is complexity ~0. The pin knee itself is 19.5 (its
  knee pins); the plain spherical 3R is 0.
* **Buildability:** all ranked levers map to catalogue parts (MR117 hubs, detent hinges, a torsion spring); the relay's
  state switch has no passive trigger yet (the stop-relay concept uses J2's hard stops to push the rocker; its own
  force-closure check is open), and the 4R's centring spring must carry the chain through 56 deg (p95) of deflection.

## 5. What this says, and what runs next

* **The plateau is the fold, and the fold is set by the arcs proximity allows.** 94-96 % of every leader's lost
  workspace is the J2 fold; the rest (6-9 poses) is worth 1.7-2.5 points of reach. At the seats where the hubs can sit
  in band (J1 over the acromion top, arcs ~40 / 73) the fold window is 55-60 deg wide against a 114-deg (5-95 %)
  workspace spread of th, so the kinematic ceiling AT THOSE SEATS is 0.61-0.63 - the verified reaches are 0.594-0.617.
  Across the body is lost on the stretched side only; overhead on both sides.
* **No measured 3-joint configuration beats ~0.70 fast / ~0.61 frozen at in-band >= 0.88**, across 50 k plain-3R,
  22 k pin-knee, 2.8 k raglan, 2.2 k knuckle, 9.8 k osn, 12.3 k stop-relay and 5.7 k dwell tries (the stop relay lifts
  the plain 3R to the pin knee's 0.700, not above). The pin knee's frontier is flat in in-band (0.719 at
  0.80, 0.700 at 0.88, 0.694 at 0.90): giving up in-band does not buy reach; only a wider window does.
* **The zero-complexity levers add up to about +0.04-0.07** (the 5 deg margin the user just ruled, +0.019-0.031
  measured; seats re-tuned on the 360 poses, +0.02-0.04 kinematic; the longer knee measured 0): reach ~0.65-0.68
  frozen, gap ~23-26. Worth taking, not 0.90.
* **0.90 needs a second window** - a two-state arc relay (+0.30-0.33 kinematic) or a fourth joint (~1.0) - AND hub 2
  in band in the second state. The lens's spring-centred 4R is the only measured route above 0.75 (0.75 frozen at
  in-band 0.864, unverified), and it pays in-band on link 3 / hub 4. The two-state relay's own gate is measured: hub 2
  parks in band for only 30-45 % of the poses its second state rescues (+0.09-0.14 at best, section 4).
* **Next (queued / to queue):**
  1. this note's farm batch landed (24 / 24 jobs, exo-cpu1 cpu3c-8-16, ~$0.55); the knee-length probes
     (`runs/pin-knee_m10_lc28.json`, `_lc31.json`) landed too (both 0); `python3 docs/research/reach/analyse.py`
     rebuilds `summary.json`; fix raglan-knee-3r's link routing (section 1)
     before its polish;
  2. the Bench(110,360) polish (in flight) should optimise on the 360 poses, not 160 - the 0.08 fast-to-frozen reach
     loss is the 160-pose window fit, not skin;
  3. a verifier run of the 4-DOF lens's park4 (frozen exact, independent harness) and a CMA of it constrained to
     in-band >= 0.88 - it is the only class whose reach moves;
  4. a two-state relay model only where its parking gate passes: the pin-knee seats give ~+0.1 (hub 2 parks for 30-45 %
     of the rescued poses); scan seats / a1' for the pair whose two hub-2 requirements overlap within 12 mm, or let
     hub 2 change level with the state (J2 on a rod in a linear-rotary bushing: 1 slide, cheap under the new weights);
  5. every new fold lever gets the ray-parking gate before any CMA: where hub 2 / the pivot sits in the poses the
     lever rescues.
* **Red team / what is optimistic here:** the kinematic ceilings ignore skin by construction; the in-band frontier is
  Bench(60,160) fast (frozen loses 0.06-0.09 of reach, section 2); the 4-DOF lens numbers are self-measured; the
  per-pose-free rocker assumes the best travel direction in every pose, which a real stop relay chooses only at the
  stops; the margin runs keep the margin-10 shape (frozen) or refit it on 160 poses only.

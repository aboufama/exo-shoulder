# Reach attribution: where the leaders lose the workspace, and what each lever is worth (2026-10-16)

User, 2026-10-16: "the reach numbers at 60s just isn't good, it seems like they're plateauing near the top, lets try
to max these out as much as we can". This note measures where every lost pose goes, what each topology could reach
at most, and what each lever buys at the in-band bar. It changes no design and no rule.

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
exactly: pin knee 30.35 (reach 0.6056, in-band 0.9043, contact 0.0091), spine-parked 34.29 (0.5944, 0.8781, 0.0154).
The raglan and knuckle rows use the kinematic fold split (exact) and their verifiers' own non-fold counts.

| leader (v_gap, v_reach) | workspace lost (of 360) | fold, folded side | fold, stretched side | knee / cuff window | jam (flip) | part collision | skin req. | contact | verifier extra |
|---|---|---|---|---|---|---|---|---|---|
| pin knee k4598 (30.35, 0.606) | 142 | 57 | 76 | 4 | 0 | 2 | 0 | 3 | 0 |
| raglan knee (31.52, 0.600) | 144 | 60 | 76 | 0 | 0 | 3 (E strap - link 2) | 0 | 5 | 0 |
| knuckle cufflink (31.89, 0.617) | 138 | 55 | 77 | 2 (cuff) | 0 | 2 (link 2 - E arm) | 0 | 2 | 0 |
| spine-parked k7008 (34.29, 0.594) | 146 | 59 | 81 | - | 0 | 1 (K6, 1 mm radial) | - (kit: quantile q 0.972 instead) | 5 (incl. top faces) | - |

**The fold takes 93.7 % (pin knee), 94.4 %, 95.7 % and 95.9 % of the lost workspace.** Everything else together is
6-9 poses (1.7-2.5 points of reach). Clip frames: the pin knee follows 110 / 110; the others lose 3-5 clip frames, all
to the fold (raglan 3 folded, knuckle 4 folded, spine 5 stretched).

By region (pin knee measured per pose; the fold split of the others is kinematic and exact):

| region | n | pin knee taken / lost: folded, stretched, other | raglan in window (folded / stretched) | knuckle | spine taken / lost: folded, stretched, other |
|---|---|---|---|---|---|
| overhead (elev >= 140) | 28 | **7** / 7, 10, knee window 4 | 9 (9 / 10) | 9 (9 / 10) | **5** / 8, 10, contact 4 + parts 1 |
| across the body (plane >= 100, elev >= 40) | 68 | **20** / 1, 47, 0 | 20 (0 / 48) | 20 (0 / 48) | **16** / 1, 51, 0 |
| behind the back (plane < -30, elev > 20, or a "back" clip) | 25 | **17** / 1, 5, contact 2 | 18 (2 / 5) | 18 (1 / 6) | **17** / 2, 5, contact 1 |
| the rest (none of the three; 6 poses are both overhead and across) | 245 | 174 / 48, 20, parts 2 + contact 1 | | | |

* **Across the body is a pure stretched-side loss** (47-51 of 68, th up to 153 deg against a window top of 101-104):
  horizontal adduction swings the humerus-fixed J3 away from the scapula-fixed J1 beyond the two arcs' reach. Only a
  longer a1 + a2 (or a second, longer state) rescues it; the margin cannot (it moves the top 3-8 deg).
* **Overhead fails on both sides** (7-9 folded at th 24-37, 10 stretched at th 110-142) - the overhead poses alone
  span th 18-146. No shift of the window helps; only a wider one (min(a1, a2) larger) or two states.
* **The pin knee's 4 knee-window poses are all elevation 165** (#211, #237, #264, #345): hub 3's in-plane drift reaches
  65.8-70.1 mm against the knee's lE + lc - 1 = 66.0 mm (knee angle 157-180 deg). A longer knee link admits them
  kinematically (lever probe below); they are 4 of the 7 overhead poses the pin knee could add without touching the fold.
* **Behind the back** loses 5-6 to the stretched side and the pin knee 2 to contact (#129, #139: plane -75 / -60,
  elevation 60, axial 105-120: metal 0.5-1.7 mm inside; #129 is also the spine-parked contact).
* **The plain 3R loses half of its in-window overhead to the skin**: spine-parked has 10 overhead poses in its window
  and takes 5 - #289, #318, #345, #371 (plane 45-90, elevation 150-165) are contact (0.6-4.4 mm inside, link 2's top
  face among them) and #211 jams parts. The pin knee takes 7 of its 11 in-window overhead poses and loses the other 4
  to its knee reach, not to the skin.

ATTRIB_EXTRA

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
| 3R + per-pose-free J1 rocker, travel beta (pivot scanned) | beta 5: 0.65-0.68, 10: 0.68-0.73, 15: 0.73-0.76, 20: 0.77-0.81, 30: 0.84-0.88 (overhead 0.68-0.82 at 30) | stop-relay-rocker-3r: none yet (best 0.681 at in-band 0.852, round 4 in flight; its own deltoid-pivot relay: kinematic 0.95, in-band 0.20) | - |
| 3R + two-state arc relay (a detented mid-joint in link 1: a1 -> a1') | a1' 77-84: 0.93-0.95, overhead 0.89-1.00; relay on a2 (a2' 129-132): 0.82-0.84 | unmeasured (no model); hub-2 parking below | - |
| 3R + coupled schedule (dwell four-bar knee, arc knee) | <= the per-pose-free rocker of the same travel | dwell four-bar: none (best 0.669 at 0.852); closure-set arc knee: none (refuted) | arc knee 0.589 (in-band 0.486) |
| redundant 4R, spring-centred sensed 4th (4-DOF lens park4, 450 tries) | ~1.0 (a 4R folds only with all four axes coplanar) | 0.644 (one config, contact 0.053); 0.781 at in-band 0.864, 0.788 at 0.842 | 0.750 at in-band 0.864, contact 0.038, gap 22.36 (self-measured by the lens, NOT verified) |
| redundant 4R, ring 4th (lens) | ~1.0 | none (in-band <= 0.79) | 0.683 (in-band 0.786, self-measured) |

Reading: every 3-joint class sits on the same fold-capped ceiling (0.61-0.63 at the seats proximity allows); the
kinematic headroom (0.93-1.00) exists only at seats or arcs that put hub 2 (or a pivot) over the raised arm.

## 3. Fold-margin sensitivity (10 / 7 / 5 / 2 deg): report only, not adopted

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
through a 4-5x lever near the edge, and in MVP2 the J2 motor needs that rate. Measured on the frozen shapes:

MARGIN_MEASURED

## 4. Levers, ranked by measured reach gain at in-band14 >= 0.88

Reference: the pin knee, fast frontier 0.700 at in-band 0.88 (Bench(60,160)), frozen exact 0.606 at in-band 0.904.
"Measured" means a model run with every proximity check; kinematic headroom is the fold law alone. Complexity is
tools/simplicity.py (lower = simpler; the pin knee is 21.5, the plain 3R 0).

| rank | lever | measured reach gain at in-band >= 0.88 | kinematic headroom | in-band cost (measured) | complexity | buildability |
|---|---|---|---|---|---|---|
LEVER_ROWS

LEVER_NOTES

NEXT_SECTION

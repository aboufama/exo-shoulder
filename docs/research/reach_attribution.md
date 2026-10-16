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

ATTRIBUTION_TABLES

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
| plain 3R, best seats anywhere | 0.928 at arcs 40/40, 0.969 at 45/45, 0.989 at 50/50, 1.000 at a1 + a2 >= 130 (J1 posteromedial low, J3 up the arm: inside the body) | fold-frontier seats: never above in-band 0.51 (fold-sph3r, raglan-routed: hubs 0 % in band) | - |
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

MARGIN_SECTION

LEVERS_SECTION

NEXT_SECTION

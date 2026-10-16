# acromial-rocker-3r - fold lever: J1 on a passive acromial rocker set by an S-U tie rod

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the rocker as a *scheduled fourth
   axis* and ask first what the best possible schedule is worth, before any rod: with q0 free per pose (an ideal
   cam), how many fold poses can a J1 cone of half-angle beta recover? Then ask whether a four-bar-like S-U rod can
   realise that schedule (its q0 = phi(C) + acos x(C) is a function of where the arm stud C is, i.e. of the J3
   direction, with a polar-distance term that can flip J1 from "away from J3" overhead to "toward J3" across the body).
   Only then spend skin evaluations. Also: put the arm stud on the arm (arm-fixed) rather than on member 3, so q0 does
   not inherit the knee drift; and carry the rod's real bodies (ball link, U-joint) and its sweep through the chain.
2. **Rawest material.** The posed skin itself (bench signed-distance grid / exact libigl path), the motion clips at
   their full 10 fps rate (continuity incl. q0), the per-pose humerus frames HG (the rod closure is evaluated on them,
   not on summaries), and the pin-knee leader's own fold list (47 of 220 poses on Bench(60,160): 23 with J3 too close
   to J1 - flexion planes 0-45 deg at elevation 90-150; 24 too far - across the body, planes 75-120, and behind,
   planes -90..-60).
3. **Methods and tools.** Kinematic upper bound (free q0 within +-75 deg), a rod-realisable proxy search (closed-form
   q0, transmission, cap, 10 fps jumps) to seed the skin search; the full model on the pin-knee leader's verified
   S.VModel checks (closure, continuity, jam rule, near-touch audit, overhead split); farm sweeps (tools/cloud_run.py)
   then CMA-ES (tools/concept_cma.py) on Bench(60,160) fast; frozen shape worn on Bench(110,360) exact.
4. **What else shows the number is right.** The plain-3R control in the same file (rocker=0) reproduces the pin-knee
   leader's 26.34 exactly; the bench (outside judge); the frozen-shape exact bench (lesson c); the red-team pose list
   (rest / overhead / across / behind groups, the closest metal and the near-touch gap); the adversarial verifier.

## What was built (docs/concepts/models/acromial-rocker-3r.py)

On the pin-knee leader (skin-normal-3r-pin-knee k10; its Model = the seed's verified S.VModel rules + knee checks):
J1's hub rides a passive rocker (member 7) turning about a GH line c (pivot boss O14, MR63ZZ pair, 9 mm crown, on
the scapula); every chain member is rotated by R0(q0); q0 in closed form from the rod length (one branch, the rest
pose's); taken only with transmission >= 25 deg, |q0| <= 75 deg, ball-link tilt <= 30 deg and U bend <= 40 deg (fixed
best mountings over the fit clips), and q0 is in the 10 fps continuity vector. Parts at real size: rocker straps
8 x 3 (pivot -> hub 1 at f1 + UP, pivot -> stud A), ball link at A and U-joint at C as O8 x 12 bodies, an O12 x 3
U base plate on the cuff at C, the O4 rod sampled every 2 mm on its skin side. Stud centres derive from the rest skin
along their rays + h and are then raised (refit loop) to >= 9 mm over their fitted plates. Collisions: rod vs hubs 1-3,
links, E, knee, pad, boss, rocker strap; rocker / boss / ball vs hubs 2-3, link 2, E, knee, pad, arm base, U (1 mm) and
link 1 (adjacent at J1, 0.15 mm); arm base / U vs hubs, links, E (1 mm) and knee (adjacent at pin b).
**Spec fixes:** the arm stud sits on the arm (member 5), not on member 3, so q0 does not inherit the knee drift; the
first build's bracket strap from the arm pad to C was replaced by a base plate on the cuff (a strap ray toward the
medial arm traced into the torso and parked the stud at 215 mm).

**Control (same file, rocker=0): 26.34** on Bench(60,160) fast - reach 0.7063, follow 0.9667, in-band 0.8419 / 0.4001,
contact 0.0116, fold 47 of 220 - identical to the pin-knee row.

## Kill test, measured

| step | what | result |
|---|---|---|
| fold census (leader seats) | th = angle(J1, J3), window [43.7, 104.4] deg (a1 40.3, a2 74.1, 10 deg margin) | 23 poses too close (flexion planes 0-45, elev 90-150), 24 too far (across the body planes 75-120; behind -90..-60); needed th 10.4-160.2 |
| ideal schedule (free q0, +-75) | J1 cone beta 10 / 20 / 30 / 40 deg | fold-free 187 / 201 / 211 / 216 of 220 (control 173) |
| rod-realisable, free placement | closed-form q0, transmission 25, cap 75, 10 fps jumps; hill-climb | ws fold-free 132-133 of 160 (control 115), 0 jumps - but rA 50-80 / rC 50-83 at any radius |
| rod-realisable, skin placement | pivot skin <= 66 mm, stud centres h 9-16 mm over the rest skin, C <= 30 deg from hub 3's seat ray; 39 871 tries + hill-climb | best ws fold-free 126 random, 131 hill-climbed (+16 = reach <= 0.79 kinematically) |
| full model, real parts | 6 hill-climbed proxy picks (local) | **0 poses taken in every one** (gap 275-375) |

Why the kinematic gain does not survive the parts (measured on those 6): the rocker strap to stud A and the ball link
sweep +-75 deg cones over the acromion/deltoid and must clear the highest skin under the whole sweep: fitted at
60-87 mm over 45-55 mm skin; the refit then lifts the ball centre to rA 70-98 mm, which changes the rod geometry the
proxy optimised; 69-129 of 220 poses fail the rod limits (dead point / cap / ball tilt / U bend); the pivot boss
overlaps hub 1 whenever beta < ~22 deg (boss O14 + hub O20 at r ~50 mm need >= 18 mm, 114 poses); the U base on the
arm overlaps hub 3 whenever C is < ~20 deg from hub 3's seat (72-124 poses); the ball body hits hub 2 (69 poses).

## Constrained sweep (40 configs, beta >= 22, C >= 20 deg from hub 3, gam 20-60) and the measured limiter

Best **k22: gap 125.84** (score 54.2): reach 0.200, follow 0.600, in-band 0.785 / 0.431, contact 0.093; params beta 23,
psi 220, gam 29.3, psiA 13.9, dl 22.9, psiC 199.9, q0r 13.7, hA 10.6, hC 12.2 (fitted rA 70.6, rC 75.8, L 66.2).
Control in the same file: 26.34. Pose losses summed over the 40: rod 6631, parts 1467, fold 308, skin 228 - the
fold is gone (the rocker does widen the window) but the rod takes its place.

Rod-limit split on the four best (closed-form q0 over the 220 bench poses):

| k | gap | dead point | cap 75 | ball > 30 | U > 40 | q0 range (deg) | U bend p50 / max | relaxed (cap 90, trans 15, ball 45, U 50) |
|---|---|---|---|---|---|---|---|---|
| 22 | 125.84 | 61 | 34 | 0 | 49 | -173..160 | 42.5 / 111 | rod-ok 98 vs 76 |
| 39 | 165.20 | 171 | 4 | 0 | 23 | -178..145 | 37.7 / 145 | 61 vs 22 |
| 34 | 167.39 | 97 | 52 | 0 | 5 | -180..173 | 32.3 / 144 | 75 vs 66 |
| 48 | 199.67 | 104 | 67 | 0 | 18 | -176..174 | 53.3 / 91 | 41 vs 31 |

**Why (new knowledge).** An arm-fixed stud near hub 3 is carried around the shoulder by the workspace (flexion ->
abduction -> extension / behind the back): seen from any pivot axis through GH near the J1 seat, it circles almost the
full azimuth, so a fixed-length rod from a rocker drives q0 through ~330 deg and crosses its dead centre; the rod's
direction in the arm frame swings by 90-145 deg, beyond any miniature U-joint. Even relaxing every rod-end limit only
recovers 10-40 poses. A rocker schedule that compresses the J1-J3 angle needs q0 to depend on the POLAR distance of
J3 from J1 (near -> away, far -> toward), but the rod's q0 is dominated by C's AZIMUTH. The ideal free schedule is
worth +28 (beta 20) to +43 (beta 40) fold-free poses; the realisable one with real parts is worth less than nothing.

## Gate, verdict, next

- Gate (48 rocker configs, in order): gain over the 2nd half 0.00, over the last third 0.00, top-5 spread 28.01
  score points -> **not converged**; status stays `screened`. The 168-config farm sweep was lost to a client timeout
  (its 24 jobs ran orphaned in a 92-113-job queue) and the 61-config resubmission had not started inside the time box.
- **Verdict: the kill test fails** (needs reach > 0.75 at <= 2 in-band points; best rocker reach 0.20). Passive
  translations 0; 6 passive rotations (pin, ball 3, U 2), all closure-set.
- Frozen Bench(110,360) exact not run (the fast best is 100 points behind the control; nothing to claim).
- Red team (from the measured pairs): the rod sweeps through the arm base (rod-brk 524 pose-hits), link 2 (156), the
  knee (107); the ball body hits hub 2 (86); the rocker strap is adjacent-jammed with link 1 at J1 (44).
- **Next, if anyone continues:** replace the azimuth-driven rod by a schedule on the polar angle - e.g. a rod whose
  arm stud lies ON the J3 axis line (C on d3 at radius rC: its azimuth about c still moves, but its distance to c's
  axis measures th directly), or drive the rocker from link 2 / J2 (q2 is a monotone function of th: a two-pin
  coupler J2 -> rocker would schedule exactly the polar term). Both keep rotations only. The second is a planar
  four-bar on the chain itself, no arm stud, and is the variant that removes the measured limiter.

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

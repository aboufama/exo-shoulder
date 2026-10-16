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

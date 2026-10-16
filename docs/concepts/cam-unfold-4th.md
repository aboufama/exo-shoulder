# cam-unfold-4th - Cam-unfolding link: a cam-slaved knee K = c(q2) in link 2

The verified pin-knee chain with link 2 split by a fourth, passive O20 hub K. K is not sensed and not sprung. A groove face
cam on link 1 around hub 2 drives it through a follower and a pushrod, so its angle is a fixed function of J2's own angle,
K = c(q2). This is the arm-side, sensor-free sibling of minarc-stop-knuckle-4r (spring knuckle in link 1, sensed: 4 active).

Model: `docs/concepts/models/cam-unfold-4th.py` (subclasses the minarc variant-B / pin-knee VModel machinery). Sweep:
`docs/concepts/sweeps/cam-unfold-4th.json`. Row: `docs/concepts/rows/cam-unfold-4th.json`. Preview:
`docs/concepts/viz/concepts/cam-unfold-4th.js`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the coupled chain as what it is: with K = c(q2), the angle th = angle(J1, J3) is a function of q2 ALONE, so
     the coupled 3R is singular exactly where dth/dq2 = 0. Design c(q2) by that 1-D map, not by a spline in the dark:
     the window is the monotone stretch of th(q2), and an arm pose has exactly one q2 (no branch, no flip by
     construction).
   - Make the cam two-sided if it pays. A spring K (minarc) can only open; a positive-drive groove can also CLOSE the
     knee at the folded end (a2e toward a1, so th_min = |a1 - a2e| falls). The spring family cannot do this at all.
   - Keep the user's 5-deg margin honest in the coupled chain: the effective dyad (a1, a2e(q2)) keeps >= 5 deg of
     J1-J3 margin (the kit-rule `m3e` reading) AND dth/dq2 never drops below the plain dyad's own gain at its 5-deg
     margin (the coupled chain transmits no worse than the 3R at its fold stop).
   - Price the parts the spec waved through: the cam flange is O30 on link 1 (the groove 10.6-13.7 mm stays outside
     hub 2's O20 housing: the housing rule); the pushrod is real metal on top of link 2a; the cam slope is capped by
     the pressure angle (<= 27 deg with a 4 mm crank and a 12 mm pitch radius: slope <= 1.5).
   - Replace the spec's +-18 deg crossed flexure with an O20 bearing-pair pin (the user's O20-only ruling; minarc's K
     needed ~28 deg).
   - Run the 3R control at the same seats (cs = cf = 0) so the cam's gain is measured, not assumed.
2. **Rawest material.** The posed skin itself (the bench's signed-distance grids: the fast cache on Bench(60,160), the
   exact libigl path on Bench(110,360)), the fit motion clips at 10 fps and the workspace grid; the minarc / pin-knee
   verified seats only as starting points. No digested summary feeds a number.
3. **Methods and tools.** The pin-knee VModel machinery (closure < 0.5 deg, 10 fps continuity incl. K, jam rule,
   part-part 1 mm / 0.15 mm, walls / crowns / tops skin-checked, near-touch audit, overhead split); an exact 1-D table
   of the coupled chain (0.1 deg) inverted per pose, then Paden-Kahan for q1 and q3; a coarse random sweep on the
   cloud CPU farm, then CMA-ES (tools/concept_cma.py) on the near-touch gap until the convergence gate passes; the
   frozen protocol (fit Bench(60,160) fast, wear Bench(110,360) exact).
4. **What, other than me, shows the number is right.** The bench report; the cam-off control at the same seats; the
   frozen Bench(110,360) exact wear; a red-team pose list (rest, overhead, across-body, behind-back, the nearest metal);
   the independent verifier of the next stage (the minarc remeasure harness takes this model with its handle swapped).

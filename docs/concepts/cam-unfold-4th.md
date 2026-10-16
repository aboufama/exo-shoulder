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

## The mechanism (as modelled; the spec improved where it was wrong)

- **Topology.** Scapula handler -> J1 (O20, active, GH ray) -> link 1 -> J2 (O20, active, GH ray, dowel stops at the
  cam window's ends) -> link 2a -> **K** (O20 bearing-pair pin, passive, through GH) -> link 2b -> J3 (O20, active,
  tilted b3 toward the skin normal) -> member 3 -> flat two-pin knee -> arm pad on the cuff / BOTTOM.
- **The cam.** A groove face cam on link 1 around hub 2. Two builds are modelled:
  - the FLANGE cam (`cam_r` 15): an O30 x 3.5 flange at the skin face, groove 10.6-13.7 mm (outside hub 2's O20
    housing = the housing rule), O3 iglidur-sleeved follower pin on a lever of link 2a;
  - the CROWN cam (`cam_r` 10, `cam_h` 3): a 3 mm grooved ring on hub 2's crown, so hub 2 stays O20 but stands
    15.25 mm.
  - The follower drives an O2 Ti pushrod along link 2a (modelled as real metal on top of the strap) to a 4 mm crank on
    link 2b. Cam slope |dK/dq2| <= 1.5 (pressure angle <= 27 deg at a 12 mm pitch radius).
- **Spec corrections.** The +-18 deg crossed flexure became an O20 bearing pin (O20-only ruling; minarc's K needs
  ~28 deg). The spec's 5-knot spline became a one- or two-sided smoothstep lobe placed in the kit's J1-J3 metric
  (onset `mons` / `monf` deg of th before the plain dyad's fold), because the coupled chain is singular exactly where
  dth/dq2 = 0 and the lobe has to act at the folds, nowhere else. The spec's 10-deg evaluator margin became the user's
  5 deg, applied to the EFFECTIVE dyad (a1, a2e(q2)) plus a transmission floor (dth/dq2 >= the plain dyad's gain at its
  own 5-deg margin, 0.29-0.32 here).
- **DOF.** 3 active (J1, J2, J3, encoders). K is a function of q2 through a positive-drive groove, so it is
  determined without a sensor and cannot sag (R17). The two knee pins are passive and sensed as in the pin knee.
  0 passive translations; passive rotations: K + 2 knee pins. No gear, pulley or cable (a cam + pushrod, MVP1-legal).
- **Complexity 33.75** (tools/simplicity.py; the pin knee is 19.5): +1 passive rotation, +2 bodies (link 2b, pushrod),
  +3 joints, 1 closed loop, 1 sliding pair (the follower), +5 made / +3 bought parts.

## Measured (Bench(60,160) fast, VModel rules, O20, fold margin 5; objective = near-touch gap)

| configuration | near-touch gap | plain gap | reach | follow | in-band 14 | contact | note |
|---|---|---|---|---|---|---|---|
| minarc BDp seats, K 35/50 sK +1, cs 25 / ws 25 | 88.29 | 88.29 | 0.506 | 0.733 | 0.722 | 0.094 | first check |
| same seats, K 30/45, cs 40 / ws 45 | 50.42 | 45.68 | 0.694 | 0.917 | 0.755 | 0.073 | th window 25.7-103.5 vs plain 25.7-91.8 |
| **control**: same, cam off (rigid K) | 87.59 | 84.79 | 0.450 | 0.800 | 0.722 | 0.070 | the cam is worth 37 points HERE |
| coarse farm sweep, 256 random (seats +- perturbation, lobes, both K sides) | 40.91 | 39.71 | 0.706 | 0.917 | 0.764 | 0.035 | hub K 0 % in band |
| K-atlas sweep, 192 (K in the in-band patch next to J1 / J2) | 59.47 | 56.95 | 0.625 | 0.850 | 0.750 | 0.044 | hub K collides with hub 1 / link 1 |
| **CMA best (S2, 6 streams, 5206 tries)** | **27.07** | **25.85** | **0.700** | 0.950 | 0.842 | 0.000 | score 90.16 near-touch fast |
| **control**: S2 seats, cam off (rigid K) | 31.57 | 30.05 | 0.688 | 0.983 | 0.824 | 0.012 | cam worth 4.5 points at the optimum |
| **control**: S2 seats, no K at all (the plain pin knee) | 27.68 | 27.68 | 0.669 | 0.917 | 0.921 | 0.012 | the pin knee alone ties it |

CMA best S2: J1 bvec(93.52, 60.83), J2 bvec(35.33, 41.52), J3 wd 62.11 / wa -9.97, b3 0.239, knee lE 63.6, lc 25.7,
phiE -8.9, phib -51.5, ang_min 30.46, stk 5.68; K bk1 29.15 / bk2 45.94, sK +1; stretched lobe mons 20.9, ws 74.8,
cs 25.0 (slope 0.5); folded lobe cf 1.8 (off). a1 39.5, a2 68.1; th window 33.6-105.5 (the plain dyad: 33.6-102.6);
**a2e only 68.1 -> 72.0**. Per part in band: hub 1 1.00, hub 2 0.94, **hub K 0.42**, hub 3 0.73, L1 0.87, **L2a 0.52**,
L2b 0.64, E 0.98, knee 0.98. Lost: 36 fold, 15 knee window. Overhead (elevation >= 140): reach 0 of 12, follow 2 of 5.

## The limiter, measured: the arm-side K cannot live in the band where it would unfold anything

1. **The K hub sweeps a 2-D patch of skin.** On link 2a, K moves with q1 AND q2 (minarc's K on link 1 moves with q1
   only). A K-placement atlas (`models/cam-unfold-4th_katlas.py`: an O20 GH-ray disc fixed in link 2a at arcs 22-60
   deg from J2 and 12 azimuths, its skin need traced over the 175 kinematically valid poses, F = p95 need) gives:
   - in band (>= 0.75) ONLY within 22-40 deg of J2 and either (a) toward J1 (azimuth ~0, J1 sits at azimuth -3 and
     35 deg), where the K disc's 5-95 % height spread is 8-11 mm, or (b) along link 2's own line (azimuth 240-330),
     where K is nearly straight (interior angle 133-169 deg) and its rotation barely changes a2e (sin psi 0.2-0.5);
   - everywhere else 0.02-0.43 in band: the 5-95 % spread of the skin height under K is 19-35 mm, against a 12 mm
     band. The same disc on link 1 (minarc's side) is >= 0.92 in band over a wide arc (0-60 deg azimuth up to 40 deg).
2. **Where it is in band, it collides.** K in patch (a) circles J2 at 22-30 deg over the ~136 deg q2 window and
   passes over hub 1 (35 deg from J2): the targeted sweep (192 configurations) loses 40-114 poses to hub1-hubK and
   L1-L2a / L2b-hub1 clashes; its best is 59.47. With the O30 flange cam, patch (a) at 22 deg also overlaps hub 2.
   The crown cam (hub 2 O20, 15.25 tall) puts hub K at 0.75 in band at bk1 23, but hub 1 still collides in 93 poses.
3. **So the search turns the cam down.** The best stream (S2) converges to a flat, late lobe (a2e +4 deg, slope 0.5).
   The streams that keep a real lobe buy reach and lose more in-band than they gain:
   - S4, a TWO-SIDED cam (the lever a spring knuckle cannot have): a2e 60.7-76.8, th window 29.1-108.4, 89 fit poses
     on a lobe, reach 0.706, in-band 0.825 (hub K 0.50): 30.24;
   - S3 (cs 72): a2e 52-71, reach 0.731, in-band 0.744: 36.37; S6 (cs 49): reach 0.706, in-band 0.780: 33.72.
   Unfolding swings J3 / link 2b over higher skin. At the optimum the cam is worth 4.5 near-touch points over a rigid
   K, and the plain pin knee with no K at all scores the same (27.68 vs 25.85 plain) at in-band 0.92 instead of 0.84.

This predicts beyond this morphology: **a 4th joint whose hub rides on link 2 (between J2 and J3) cannot be in band
unless it sits within ~25 deg of J2, and there it either clashes with hub 1 or has no leverage on a2.** A fold lever has
to live on the scapula side (link 1: minarc, geneva-tail-knuckle) or act at J2 itself.

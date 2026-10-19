# Offset-centre 2R pointer with a sliding twist sleeve (offset-pointer-slip-sleeve)

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the rod line as a free design
   choice, not "the line O -> C": a straight O->C rod converges on O (deep inside the shoulder), so every mm of rod
   proximal of the sleeve sinks ~0.25 mm toward the arm axis - the rod's own travel buries it. They would check that
   first (a one-line geometric bound), then tilt/offset the prismatic axis so it lies along the arm surface (a
   Stanford-arm style offset P, still 6 coordinates for the cuff's 6 DOF), and shape the bar as a skin-fitted rigid
   body in ITS frame (it never follows axial rotation, so its underside must clear the arm at every axial angle).
2. **Rawest material.** The posed skin of every bench pose (the signed-distance grid of `B.skin(i)` per pose, not a
   summary), the fit-clip frames in time order (`B.clip_order()`, held-out clips untouched), the band humerus and
   scapula rotations from `pipeline/conformal/band_poses_wsf.b64`, and the skin-motion map
   `pipeline/conformal/analysis/skin_motion_map_14.json` to place the hubs where the skin moves least.
3. **Methods and tools.** Closed-form inverse kinematics of the pointer (J1, J2 from dh, slide from |C - O|, J3 and the
   two U angles from the cuff orientation); per-sample skin-fitted undersides by the kit's K3 march along rays from
   the joint centre O (not from GH, since link 1 and the bar rotate about O); K2 dense continuity along the slerped
   motion; K6-style pairwise clearance; vectorised over poses on the Bench(60,160) grid cache; coarse-then-refined
   sweep of |o|, its direction, a1, cuff station / azimuth, rod height and rod tilt.
4. **What shows the number is right, other than me.** `tools/concept_bench.py` (the same skin, poses and metric as
   the 68.93 champion), the adversarial verifier re-running the best config on the exact path, and a red-team pose
   list (rest, overhead 150-170 deg, across-the-body, behind-the-back, extreme axial rotation) with the worst pinch
   point and the pose that jams.

## The morphology

Scapula -> **J1** (O20 hub, axis a1 through a centre O fixed in the scapula, |o| mm from GH) -> **link 1** (12 x 3 strap,
90 deg great-circle arc about O from a1 to j2) -> **J2** (O20 hub, axis j2 = branch * unit(a1 x dh) through O) -> **bar**
(12 x 3 strap: a cap arc about O from j2 down to th_k from the rod line, then a run along the rod line at azimuth
psi_b, fitted from the line outward) -> **boss** (rod clamp O12 x 10) -> **O6 rod** on the line O -> C -> **sleeve**
(O12 x 25 linear-rotary bushing centred at the cuff point C: **J3** spin, ACTIVE; slide lam = |C - O|, PASSIVE) ->
**Hooke U** (ring around the sleeve on the inner axis u1, outer pins u2 on two 3 x 10 cheeks on the cuff; 2 PASSIVE)
-> the user's upper-arm cuff. 3 ACTIVE + 3 PASSIVE; closed-form IK (residual 0), every passive coordinate set by
closure (the cuff's 6 DOF = 6 chain coordinates).

Model: `docs/concepts/models/offset-pointer-slip-sleeve.py`, rebuilt on the shared kit (K2 dense continuity on joint
values AND joint axes, K3 march, quantile underside, kit sampling). The interrupted session's per-pose model was
replaced. Every part at real size: flat O20 hub discs with the 12.25 mm crown (walls checked for contact), link 1 and
the bar at 12 x 3 with the 60 deg climb limit and the hub stack (link 1 upper at J1, lower at J2; the bar over the J2
hub and **over link 1 by construction** (+1 mm clearance + 1 mm sampling slack) wherever link 1 passes under it in any
taken pose - without it link 1 and the bar collide in 52 % of the closing poses), the rod, boss, sleeve and U ring
sampled on the half facing the arm and contact-checked on the whole circumference, cheeks with skin-fitted feet.

### Spec corrections (measured)

- C0: the catalogue took the bind pose (BP.V0). Here C0 sits hC mm over the q90 (over the bench poses) of the arm's
  own outer skin, marched OUT from the band humerus axis (a march inward stops on the trunk in the poses where the arm
  presses on it: 83-106 mm instead of 49 mm).
- The U is a ring + two cheeks at real size (the spec's O16 disc cannot carry a 2-axis gimbal); ring radius from the
  measured U tilt (5-6 deg at the best configurations, so the 9 mm minimum governs).
- Rod line: the spec's straight O -> C rod is the measured limiter of the offset (below). A tilted / offset prismatic
  axis is the fix in principle; it was bounded, not built (see "What limits it").

## Results (Bench(60,160), fast grid cache, K3 march, K2 dense, K6 on)

114 configurations in `docs/concepts/sweeps/offset-pointer-slip-sleeve.json` (coarse 72: |o| 0/10/20 x four J1 axes x bar
azimuth x quantile; refine 26 around the best; q = 1 refine 13; third stage 3, stopped when each configuration took
~110 s on the loaded machine). Baseline 68.93.

| config | gap | reach | follow | in-band 14 | in-band 10 | contact | note |
|---|---|---|---|---|---|---|---|
| k 113: o 0, a1 bvec(85, 78), dpsi 45, q 1.0 | **71.15** | 0.950 | 0.950 | 0.239 | 0.170 | 0.050 | bench best - DEGENERATE: hub 2 327 mm, link 1 199 mm, bar cap 274 mm off the skin (no clearance in some pose -> fitted at the 400 mm cap); only the cuff end is in band |
| k 109: o 0, a1 bvec(100, 60), width 10, q 1.0 | 74.57 | 0.950 | 0.950 | 0.204 | 0.135 | 0.050 | shoulder side >= 32 mm off the skin (grid clamp) |
| k 86: o 0, a1 bvec(100, 60), dpsi 45, th_k 55, q 0.95 | 88.62 | 0.763 | 0.883 | 0.423 | 0.243 | 0.205 | best that keeps hub 1 (93 %) and link 1 (67 %) in band |
| k 96: same, o 5 | 152.45 | 0.500 | 0.733 | 0.429 | 0.261 | 0.436 | the offset, the morphology's point, costs +64 |
| k 97: same, o 10 | 224.15 | 0.256 | 0.500 | 0.430 | 0.299 | 0.677 | boss in contact in 139 / 220 poses |

Per part at k 86 (in-band 14, median mm, samples): hub 1 0.93 / 10.7; link 1 0.67 / 11.0; **hub 2 0.02 / >= 32**;
**bar cap 0.16 / 24**; **bar arm run 0.04 / >= 32 (525 samples, a quarter of all metal)**; boss 0.90 / 4.6; sleeve
0.84 / 10.5; rod 0.68 / 12.2; U ring 0.90 / 8.3; cheeks 0.86 / 2.5.

## What limits it (measured)

1. **The offset itself.** With O off GH the slide works (lam 207-219 mm at o 10), but the rod lies on the line O -> C,
   which converges on O at ~15 deg to the arm surface: the rod clamp sits (range + 25) mm proximal of the sleeve and
   sinks ~0.27 mm per mm into the deltoid. Contact by the boss: 11 poses at o 0, 139 at o 10; gap 88.6 -> 152 (o 5)
   -> 224 (o 10) -> 250 (o 20). Bound for the fix (a tilted / offset prismatic axis): removing every boss-only contact
   at o 10 leaves link 1 / bar / hub 2 contacts in ~40 poses and in-band 0.43, i.e. ~85-90 - no better than o 0,
   because the bar, rotating about O while the arm rotates about GH, drops from 4 % to 0.2 % in band (it slides
   against the skin by |o| x angle, the spec's own risk). So the tilt was bounded, not built.
2. **The pointer's bar does not follow axial rotation.** Its roll is set by a1 x dh, the arm's by the arm: the rigid
   run down the lateral arm must clear the arm at every axial angle and floats >= 32 mm (0-4 % in band) in every
   configuration. This is the 3R family's proximity limit moved from link 2 to the bar.
3. **J2 hub**: 0-4 % in band at every J1 axis (it sweeps over the posterior-lateral cap that the elevated arm fills).
4. q trades contact for in-band; at q = 1 the shoulder side floats (best numbers above are degenerate).

## Red team (best bench config, k 113)

- Rest 3/3, overhead (elev >= 150) 13/13, behind-the-back (axial <= -80) 44/45, across-the-body (plane >= 110)
  27/38 taken. The 11 lost poses are all across-the-body: the cuff end (boss, sleeve, rod, U ring, cheeks) is inside
  the body - the arm pressed on the chest.
- Pinch: the rod clamp (boss) 0.25 mm off the skin at plane 122, elev 31, axial -80, flex 122.
- No jam: closed-form chain, 0 flips along the clips (K2 dense on values and axes), no part collision (bar over
  link 1 by construction). J1 spans -115..101 deg, J2 -163..-59, J3 a full turn (a sleeve can spin), U angles 0 at
  o = 0 (the slide and U are idle: the cuff-sleeve-3r limit, as the spec said).

## Verdict

**Dead as an offset-pointer morphology.** The offset (its reason to exist) is monotonically harmful; at o = 0 it is
the cuff-sleeve-3r limit, whose best non-degenerate number (88.6) is worse than the champion 3R (68.93) because the
bar cannot follow the arm's axial rotation. Not worth a GPU sweep. What it teaches beyond this morphology: (a) any
prismatic element on a line through a centre near GH is buried by its own travel (depth ~ sin(angle to the arm
surface) x travel; ~0.27 mm/mm at a 200 mm cuff); (b) a long rigid run down the upper arm whose roll is not slaved to the humerus cannot be in band (it must clear
every axial rotation): put the twist joint high, so the part that runs along the arm is humerus-fixed, rather than
at the cuff; (c) a q = 1 fit can "win" the gap by floating whole subassemblies - the bench should cap or penalise parts more than
~30 mm off the skin (a verifier check).

## Audit

An independent audit on Bench(60,160) with the fast grid cache, using the same model file and no code changes.

- **No modelling bug and no convention error found.** The closed-form closure, K2 continuity, part clearance, contact
  on hub walls and full cylinders, and ~1 pt / 4 mm2 sampling all match the baseline's conventions. Strap width 12 vs
  the baseline's 8 moves the gap by less than 1 (88.62 -> 86.28).
- **The 88.62 "best non-degenerate" number was a coarse-grid miss.** Around k86, the bar azimuth was only tried at
  -45, 0 and 45 with q 0.9 and 0.95, and the q 0.98 / 1.0 refine was run around dpsi +45. Results from k86 with
  dpsi 0:
  - q 0.97: gap 79.11 (reach .78, follow .92, ib14 .44, contact .18).
  - q 0.98: gap **76.42** (reach .8125, follow .95, ib14 .3733, contact .15). Hub 1 has a median of 16.7 mm and
    link 1 13.9 mm, so the shoulder side is still near the skin.
  - With J1 axis bvec(85,78): 75.09, but link 1 then floats.
- **The degenerate / non-degenerate line does not hold.** Even in k86, the J2 hub sits 104 mm out along its axis and
  is 0-4 % in band in every configuration. The gap falls continuously with q: 88.6 -> 79.1 -> 76.4 -> 71.15.
- **Other one-at-a-time probes from k86** (none helps):
  - dpsi -135, -90, 90, 135, 180 -> 234, 207, 88, 80, 258.
  - hC 9 and 11 -> 375 and 313: the cuff end is buried.
  - s 150 / 250 -> 375 / 92.
  - q 0.9 -> 118.
- **Verdict: the death is refuted on the number, not on the idea.** The best honest gap, 76.42, is within 10 of 68.93
  but still behind it. The measured limiters are:
  - the J2 hub, whose axis a1 x dh floats more than 100 mm;
  - the bar run down the arm, at 1-10 % in band, because its roll is not tied to the humerus.

  At o = 0 this is still the cuff-sleeve-3r limit, and the centre offset that gives the morphology its name stays
  harmful. A GPU sweep is worth it only for the o = 0 / dpsi 0 / q 0.97-0.98 region, and only together with a fix for
  the J2 hub.

## Polish (2026-10-15, convergence check of the "dead" verdict)

**Why.** The screening sweep stopped while still climbing (best found on its last try, +6.5 points in its second half),
so the death verdict could have been a sampling false negative. Model, honesty checks and geometry rules unchanged;
only parameters searched, on the same bench (Bench(60,160) fast grid cache), evaluated with the model's own
`setup()` + `evaluate()` on the CPU farm (16 slots, ~$0.1 in all).

**Method.** Local search from the screening's top configurations (k 113 / 101 / 111 / 98, all o = 0): one-at-a-time
coordinate steps on a1_az, a1_el, dpsi, th_k, s, caz, hC, q, width, sing, t_link (round 1), then coordinate steps
around each new incumbent with shrinking steps (rounds 2-4, 6) and Gaussian sampling around the incumbent (rounds 5,
7, 8; sd shrinking from a1 6 deg / s 4 mm / hC 0.4 mm / q 0.006 to 2 deg / 1.5 mm / 0.1 mm / 0.002). No range was
widened (width 10 is the lower end the screening already used; not taken below, a strap rule). o kept at 0 (the
screening measured the offset monotonically harmful). **252 new evaluations** (entries k 114-365, stage "polish").

**Best-so-far curve** (score = 100 (1 - gap / 275)): before 74.13 (gap 71.15) -> after 22 evals 75.03 -> 64: 77.72 ->
127: 78.32 -> 190: 78.47 -> 252: **78.58 (gap 58.90, k 306)**. Per round best gap: 68.67, 67.19, 61.27, 60.72, 59.93,
59.62, 59.32, 58.90. The jump came from leaving q = 1 (q 0.98: the fit sacrifices 2 % of poses per sample instead of
floating the shoulder side at the 400 mm cap) with the 10 mm strap and a more posterior J1 axis (a1_az 75-78).

**Best (k 306):** o 0, a1 bvec(77.5, 78), s 189, caz -2, hC 12.9, dpsi 60, th_k 45, width 10, q 0.98 (rest as PARAMS):
gap 58.90, reach 0.90, follow 0.95, in-band 14 0.397, in-band 10 0.287, contact 0.086 (19 poses lost to contact; 0 to
singularity, U, slide, flip or part collision), closure 1.0. Per part (in-band 14, median mm): hub 1 1.00 / 5.9;
**hub 2 0.04 / >= 32**; **link 1 0.34 / >= 32**; **bar cap 0.05 / >= 32**; **bar arm run 0.13 / >= 32** (390 samples);
boss 0.97 / 5.1; sleeve 0.85 / 10.5; rod 0.69 / 12.2; U ring 0.90 / 8.2; cheeks 0.87 / 2.4.

**Convergence gate:** best gain over the second half 0.26 (< 1: pass); top-5 within 0.12 (< 3: pass); best found at
eval 193 of 252, inside the last third (from 169): **fail -> not converged by the gate**. It is a flat ridge: the
last 125 evaluations gained 0.26 points in steps of 0.05-0.15 (a1_az, s, hC trading against each other).

**Screened, with a caveat.** 78.58 clears the 74.9 bar on this bench (and 76.3 on honest kit geometry), so the
status goes back to "screened". But the score is carried by the cuff end (boss, sleeve, rod, ring, cheeks 0.69-0.97 in
band, hub 1 1.00); hub 2, the bar cap and the bar's arm run are 4-13 % in band with medians at the grid clamp
(>= 32 mm off the skin), i.e. the rigid pointer still floats - limiter (2) and (3) above are unchanged. The 1 cm rule
is not met by the shoulder half of this mechanism; a verifier should cap or penalise parts > ~30 mm off the skin
before this number is compared with the champion's.

**What limits it:** the bar's roll is set by a1 x dh, not by the arm, so its run down the arm clears every axial angle
and floats; the J2 hub sweeps the posterior-lateral cap filled by the elevated arm. Contact (19 poses) is the rest of
the gap: 100 x 0.086 = 8.6 of the 58.9.

**Red team of k 306 (partial).** The model's own checks stayed on in every polish evaluation: closure 1.0, 0 flips
(K2 dense on values and axes), 0 part collisions, 0 singular / U / slide failures; 19 of 220 poses lost to skin contact.
The full `red` pose list (rest / overhead / across-the-body / behind-the-back, pinch point) and the CB_EXACT re-run
were sent to the farm but did not return within the time box - still owed before this number is promoted.

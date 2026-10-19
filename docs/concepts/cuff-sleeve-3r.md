# cuff-sleeve-3r - spherical 3R, the twist joint a GH-aimed rod turning in a sleeve on the cuff

Model: `docs/concepts/models/cuff-sleeve-3r.py` (shared kit + model-placed spar, crank, rod, sleeve and foot). Sweep:
`docs/concepts/sweeps/cuff-sleeve-3r.json`. Row: `docs/concepts/rows/cuff-sleeve-3r.json`. Preview:
`docs/concepts/viz/concepts/cuff-sleeve-3r.js`. Round J1 (round 101), lens 1 cell S, GATE 0 screen.
**Verdict: DEAD at gate 0** (numbers below): link 2 must run down the arm in the POINTING frame while the arm turns
+-90 deg under it about e3, an axis 24-50 mm off the arm's centre. That puts every pointing-frame part between the
deltoid and the sleeve 12-90 mm off the skin. The bound below shows this for ANY such link, not only for this shape.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Before drawing link 2, measure the
   twist the arm makes about e3 relative to the pointing frame over the real poses (the rod-in-sleeve joint has no
   travel limit, so the joint never caps it; the metal around it does). Then bound what ANY rigid link fixed in the
   pointing frame can do along the arm: per station s and spar azimuth, march from the e3 line to the arm's own skin
   in every pose. Set e3's tilt from the arm-fixed saddle under the sleeve (the sleeve must clear the skin over its
   whole 30 mm, not only at s3), and treat the crank at the rod's proximal end as metal that sweeps the arm with the
   twist. Do not take the spec's "4.7 mm sphere" claim for the cap on trust: it holds only near GH, and the spar runs
   from s 45 to s 210.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (every part is
   marched and scored on it pose by pose); the scapula and humerus rotations of the 60 fit-clip frames and 160 / 360
   workspace poses (pipeline/conformal/band_poses_wsf.b64 through K.frames); the body_pose humerus axis E for the
   arm-fixed parts. The digest's numbers are re-measured, not reused (e.g. the spec's lateral skin radius 47 mm at
   s 230 is 50-51 mm at the 0.9 quantile over the poses, and 63-109 mm in the 5-10 % of poses where the torso, chin or
   folded forearm reaches the lateral distal arm).
3. **Methods and tools.** tools/concept_kit.py: K1 closure (a1 + a2 = 180, the planner's window), K2 dense
   continuity, K3 march, K4 O20 hubs, K5 straps, K6 collisions + `over`, audit. The spar, crank, rod, sleeve and foot
   are placed by the model: they are fitted radially from the e3 line or the humeral axis, not on GH rays (the
   pointer-cslide lesson: GH rays along the arm run 100+ mm inside it). Around them: a parameter-free per-station bound
   (scratchpad bound.py, numbers below), a coarse grid, compact CMA-ES on Bench(60, 160) fast, and a frozen wear on
   Bench(110, 360) exact.
4. **What, other than me, shows the number is right.** The bench scores every sample I hand it against its own skin,
   contact included. Beyond that: the kit audit (O20 hubs, sampling density, pose locality), the parameter-free spar
   bound (it does not depend on my link-2 shape), the adversarial verifier and the alignment auditor, and the red-team
   pose list: rest, overhead (elev >= 140), across the body (plane 135-150), behind the back, the pose that drives the
   crank into the arm, and the poses where the trunk reaches the arm-fixed saddle.

## The morphology as built (spec fixes in **bold**)

Scapula -> **J1** O20 hub, axis p1 = bvec(az, el) (back of the shoulder / acromion top only) -> link 1 (12 x 3 strap
on the great circle p1 -> p2) -> **J2** O20 hub, p2 = K.closure(p1, e3, a1, a2, sigma) -> link 2 = **cap strap**
(12 x 3, GH-ray fitted over the deltoid cap from p2 toward e3, over link 1 + 1 mm) + **spar** (12 x 3, fixed in the
pointing frame at azimuth psi_b about e3, stations s_a .. s_c every 2 mm, underside fitted radially from the e3 line
at quantile q, climb <= 60 deg) + **crank** (12 x 4 plate at s_c from the rod out to the spar) + **O5 rod** on e3 ->
**J3**: the rod turns in an O11 x 30 housing with two MR85ZZ (5 x 8 x 2.5), and the inner rings let the rod float
+-5 mm along e3 (**1 passive translation**, set by closure: on a fixed GH the rod's distance from GH never changes)
-> **foot** (the sleeve's saddle; the user's BOTTOM is cut and merged into it), arm-fixed.

- **e3's tilt gamma is set by the foot, not by the rest-pose radius**: the foot's skin face is fitted radially from
  the humeral axis (3 mm window: only the arm's own skin) at quantile qf over all bench poses, and gamma is the
  smallest tilt at which the sleeve's skin-side generator clears the foot's face by >= 1.5 mm over the sleeve's
  whole length. qf 0.9 -> gamma 15.1 deg at s3 230 (the spec has 13.6, from one rest radius); 13.3 deg at s3 260.
  qf 1.0 -> 28 deg, because the torso, chin or folded forearm comes within 3 mm of the lateral distal arm in 15 of
  the 220 poses (across the body plane 135-150 with elbow flexion, behind the back plane -15 / 30 at axial 60-105).
  Those poses are lost to the arm-fixed sleeve in any variant (11 contact poses each for rod, sleeve and foot at
  every configuration).
- **a1 + a2 = 180** (the planner's window [|a1 - a2| + 5, 175] for th = angle(p1, e3)) instead of the spec's 64 / 90.
  The measured th span is 49-177 deg at bvec(-20, 0) and 57-174 deg at bvec(30, 70) with gamma 15; closure is 0.97-1.0.
- The fold margin is read in th (K.closure), 5 deg; min th margin over the taken poses is reported.

## Measured

### The twist the spar must ride over (kinematic, Bench(60, 160), gamma 15.1)

J3 (the arm's angle about e3 from the pointing frame), spread about its circular mean over the closing poses:

| J1 seat | 5-95 % | 25-75 % | ws 5-95 % |
|---|---|---|---|
| bvec(-20, 0) back of the shoulder | -105 .. +79 (184 deg) | -46 .. +48 | -91 .. +80 |
| bvec(0, 30) | -133 .. +135 (269 deg) | -52 .. +61 | -120 .. +146 |
| bvec(30, 70) acromion top | -115 .. +113 (228 deg) | -54 .. +48 | -130 .. +117 |

The rod-in-sleeve joint does carry this twist (no travel limit). The metal of link 2 is what cannot.

### Parameter-free bound: any rigid link fixed in the pointing frame along the arm

For each station s along e3 and each azimuth psi_b (15 deg steps), I marched from the e3 point outward to the arm's
own skin (3 mm window) in every closing pose. A rigid spar sits at R = the q-quantile of that requirement (torso-blocked
rays count as contact). The table gives its in-band share (skin 2-14 mm) at the BEST azimuth per station; one real
spar has one azimuth, so the true numbers are lower:

| station s (mm) | bvec(-20, 0): q 1.0 in-band / contact | q 0.95 | q 0.9 | bvec(30, 70): q 1.0 | q 0.95 |
|---|---|---|---|---|---|
| 40 | 0.22 / 0 | 0.51 / 0.05 | 0.74 / 0.09 | 0.08 / 0.20 | 0.29 / 0.05 |
| 70 | 0.13 / 0 | 0.49 / 0.04 | 0.68 / 0.10 | 0.09 / 0.35 | 0.16 / 0.05 |
| 100 | 0.12 / 0 | 0.37 / 0.05 | 0.47 / 0.09 | 0.06 / 0.01 | 0.24 / 0.05 |
| 130 | 0.04 / 0 | 0.16 / 0.05 | 0.21 / 0.09 | 0.04 / 0.12 | 0.22 / 0.05 |
| 160 | 0.04 / 0 | 0.12 / 0.05 | 0.12 / 0.10 | 0.15 / 0 | 0.17 / 0.05 |

Between s 100 and the rod, no rigid pointing-frame part is in band more than 12-37 % of the time, even when it gives
up 5 % of the poses at EACH station. Those contacts land on different poses at different stations, so the spar's
union of contact poses is 29-45 of 220. The arithmetic: at s 100, e3 sits d = s tan(gamma) = 27 mm off the arm's
centre, and the arm (R ~ 50) swings its centre +-90 deg about e3. A point that clears it everywhere is >= 2d - (a few)
= 20-30 mm off the skin at the other end of the swing. Placing the rod further down the arm only trades d for a
longer spar (s3 260: gamma 13.3, the same table to +-0.02).

### Sweep (Bench(60, 160) fast grid cache, K3 march, K2 dense, K6 + `over`; local niced at load 15-20, farm closed)

| k | config | gap | reach | follow | in-band 14 | contact | overhead | binding members (in-band; contact poses) |
|---|---|---|---|---|---|---|---|---|
| 0 | spec-like: bvec(-20, 0), 90 / 90, psi_b 0, qf 0.9 | 139.25 | 0.631 | 0.85 | 0.182 | 0.306 | 0/12 | spar 0.00 (35), crank 0.11 (52), hub 2 0.00 (13), link 1 0.02 (24) |
| 2 | bvec(-20, 0), 90 / 90, **psi_b -41** (spar opposite the arm's mean twist), qf 0.9 | **110.96** | 0.763 | 0.85 | 0.238 | 0.210 | 0/12 | spar 0.15 (29), crank 0.23 (21), hub 2 0.00 (13), cap 0.01 (21), sleeve 0.83, foot 0.98 |
| 3 | same, a1 120 / a2 60 | 129.74 | 0.713 | 0.75 | 0.240 | 0.250 | 1/12 | hub 2 0.03, cap 0.17 |
| 4 | same, q 1.0 | 120.56 | 0.825 | 0.767 | 0.140 | 0.187 | 4/12 | spar 0.00 (2), crank 0.05 (21) |
| 5-6 | bvec(0, 30) / bvec(30, 70) | 163-195 | | | | 0.33-0.51 | | hub 2 at the 90-deg 'equator' points into the trunk / neck in 10-16 % of poses |

(The full list, in order, with every member's numbers, is in the sweep file. The CMA-ES rows are tagged `cma1`.)

Frozen wear of k2 on Bench(110, 360) exact (no refit): NOT completed - the exact path (no local fast cache for
Bench(110, 360)) did not finish inside the 75-min box at load 15-20, so it was stopped; the fast number is 93 gap points
over the death line, and frozen wears have only ever lost points.

## Why it dies (the limiter, measured)

1. **The spar** (link 2's run from the deltoid cap to the rod) is in band 0-15 %, with 29-45 contact poses. The bound
   above shows that no rigid pointing-frame part does better than 12-37 % between s 100 and the rod. This is the
   'sweep principle' risk in the catalogue, and the measured number is worse than its estimate (it estimated a
   3-5 mm gap at +-45 deg; the real twist is +-90 deg for 90 % of poses, and the gap at s 130 reaches 25-40 mm).
2. **The crank**: at the rod's proximal end e3 runs only 5-8 mm off the lateral skin. The arm blocks ~116 deg of
   directions around e3 there, and with 184 deg of twist that leaves no direction the crank can always take: 21-52
   contact poses.
3. **Hub 2** (a2 = 90 about e3) sits on the arm's 'equator', and the twist swings it round to the axilla / chest side:
   0-3 % in band, 7-16 contact poses. a2 60 / a1 120 raises the cap's in-band (0.17), but closure and follow drop.
4. **The arm-fixed sleeve is the only good part** (sleeve 0.83, foot 0.98 in band). It is also lost in the 11 poses
   where the trunk or forearm reaches the lateral distal arm.

Lesson for the class (lens 1): a near-coaxial J3 removes th's axial dependence, as the planner measured. But it moves
the problem into link 2: whatever joins the 2R (pointing frame) to an axial joint on the arm has to ride the twist
somewhere. The ring (cell R) rides it ON the bearing, a part concentric with the arm, so nothing sweeps. The sleeve
(cell S) rides it along a 150 mm spar, which sweeps the arm. Cell S is dead; cell R is the only form of lens 1 left.

## Red team (own best, k2)

- **The pose that jams**: none jams (closure 0.99, 0 flips). Poses are lost by CONTACT: the crank into the lateral
  distal arm when the twist is at its far end (internal rotation across the body), and the spar into the arm at
  s 100-160 on the opposite end.
- **The point that pinches**: the crank's inner corner at the rod (s ~211). e3 runs 5-8 mm off the skin there, and
  the crank's plate face passes over the skin as the arm turns.
- **The optimistic number**: the fast grid's skin is used for the fit and the score alike (same as every row). Spar
  in-band at q 0.95 counts 5 % contact PER STATION as acceptable; the union is 29 poses (13 %). The foot's qf 0.9
  hides 11 contact poses that are counted, not removed. Overhead 0/12 at the best configuration: the design takes no
  overhead pose.

## Audit (2026-10-17, independent auditor) - death STANDS

Refutation line: corrected gap <= 78.93 (champion 68.93 + 10) on Bench(60, 160). Every number below came from the
model's own `evaluate`, Bench(60, 160) fast, local niced, one process per run.

- **Reproduced**: k2 gives 110.96 (reach 0.7625, follow 0.85, in-band14 0.2379, in-band10 0.1512, contact 0.21,
  overhead 0/12, honest True), identical to the claim. On a quiet core one evaluation takes 3 s; under load 15 it took
  about 60 s.
- **Ghost bound (independent of the spar's shape)**: with the spar and crank removed from the metal and from K6 at k2,
  the gap is still **101.02** (reach 0.781, follow 0.867, in-band14 0.284, contact 0.192). Hub 2 (0.00 in band,
  13 contact poses), link 1 (0.02, 24) and the cap (0.01, 21) keep it 22 points above the line however good a spar
  might be. A ghost CMA-ES over the corrected box (9 evaluations) found 104.84 at best, nothing below the k2 ghost.
- **Search-box bug (found, does not change the verdict)**: the model's `CMA_BOX` has el 20-85, but the best seat k2 is
  bvec(-20, 0), so all four original CMA rows were clipped to el 20 (129-171). I re-ran the audit CMA-ES from k2 with
  el 0-85, s3 120-270 and az -40..90: 10 evaluations (sweep k14-23, tag `audit-cma`), best 129.98, none below 110.96.
  A proximal sleeve (s3 161, gamma 21) scored 207.19.
- **Explanation fix**: hub 2's loss is not the twist. p2 = K.closure(p1, e3) depends only on the J1 seat and e3's
  direction, and J3 never enters it. With a 90 / 90 dyad, p2 is the pole of the (p1, e3) great circle. That is the
  2R pointer's hub-2 placement (the planner's "WHERE hub 2 sits"), and this design inherits it whatever its J3 is.
- **Convergence gate**: still not met (24 evaluations; I stopped the audit CMA at the 25-min box). The death does not
  rest on it, because the ghost bound covers every spar and crank shape at k2. Conventions match the champion (p95
  profile quantile, the same `report`).

One line: removing the spar and crank entirely still leaves 101.02 (the 2R pointer's hub 2, link 1 and cap are
0-2 % in band), and the search with the corrected box, which can now reach el 0, found nothing below 110.96. Cell S
stays dead.

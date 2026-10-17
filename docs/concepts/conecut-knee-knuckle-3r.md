# conecut-knee-knuckle-3r: the lead's knee re-centred so it never binds, and a hard stop on J3

Lens: round 12, lens 2 (overhead cone). This row is also the knee column that the long-dyad picks carry. Family:
slaved-knuckle 3R with a pin knee. 3 ACTIVE DOF (J1, J2, J3 encoded). K is slaved and never read. The knee pins are
passive rotations outside the DOF count. 0 passive translations. No gears, pulleys or cables.

- Model: `docs/concepts/models/conecut-knee-knuckle-3r.py`. It loads the verified lead slipper-nose-knuckle-3r
  (SN_CELL=lead) unchanged and adds the knee and stop parameters.
- Sweep: `docs/concepts/sweeps/conecut-knee-knuckle-3r.json`
- Row: `docs/concepts/rows/conecut-knee-knuckle-3r.json`
- Preview: `docs/concepts/viz/concepts/conecut-knee-knuckle-3r.js`

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - **Find out whether the stop takes any pose, or only relabels it.** A stop never makes a pose reachable. It turns
     a "knee slide" into a "J3 stop", and both mean the wearer is blocked. So the first check is which part of the
     lead binds at the 8 stopped poses. The proposer's per-pose diagnosis (scratch `cone/log_diag_kw25.txt`) says hub 2
     and the K-housing member 7 are 0.03-7.9 mm into the skin at 182 / 184 / 203 / 205 without the stop. That is chain
     metal, which the knee cannot move. If that holds, no knee geometry takes those poses, and this morphology can only
     buy in-band and contact points.
   - **Treat the knee as a force path, not only as a window.** The knee link is a two-force member in hub 3's plane. A
     moment M about J3 crosses it as a force F = M / d_perp, where d_perp = lE sin(knee angle) is the distance from the
     J3 centre to the knee link's line. The lead's near-straight knee (124-152 deg) has d_perp down to ~32 mm. A knee
     near 90 deg has d_perp ~ lE. Measure d_perp per pose.
   - **Size the stop for the moment the wearer actually puts on it.** The cuff on soft tissue limits what reaches the
     stop: a strapped upper-arm cuff slips at about 2-5 N m about the humeral axis. Size the dowel for a deliberate
     10 N m push.
   - **Put the stop inside the hub rather than adding metal outside it.** The spec's tab on link 2's root is new metal
     at the hub rim, next to the skin. A 2 mm dowel pressed axially into hub 3's lower plate at r 7.5, running in an arc
     groove under link 2's ring, sits inside the O20 x 12.25 envelope. The bearing OD is 11 mm, so r 5.5 < 7.5 - 1.05,
     and the rim is at r 10. It acts on J3's own angle and adds no skin-facing samples.
   - **Try the other knee assembly mode.** The window map has a second branch with phib near +90, where the knee link
     points the other way across the drift cloud. That branch reaches a margin of 45 deg with lc 39. The sweep samples
     both branches.
   - **Watch the E strap as an in-band diluter.** A longer E strap lying flat on the posterior humerus adds in-band
     samples and raises the in-band share without moving any part that was out of band. Report this per part, so a
     verifier can tell real clearance gains from dilution.
2. **Rawest material.**
   - The drift cloud: member 3's drift relative to the arm in hub 3's plane, for every bench, held-out and fit-clip
     frame (scratch `cone/drift.json`, from the lead's IK on the posed skin). The knee window map is computed exactly on
     it, with no bench in the loop.
   - The per-pose skin distance fields of Bench(60,160) and Bench(110,360) exact, and the per-pose contact depths.
   - The motion clips at 10 fps: q3' against the stop over every fit-clip frame.
   - The lead's per-pose dumps (`docs/alignment/remeasure/slipper-nose-knuckle-3r_{bench,held}_perpose.json`) for the
     paired comparison.
3. **Specific methods and tools.**
   - The closed-form two-circle closure of the planar RRR (hub 3's plane), the model's own `knee()`, for the window
     map over (lE, lc, phiE, phib).
   - A coarse Latin-hypercube sweep on Bench(60,160) fast, then CMA-ES from the top configurations, with the 1 mm
     near-touch gap as the objective and the knee margin as a penalty. Everything runs locally on 2 niced processes,
     because the farm is past its budget line (CLAUDE.md (7)).
   - The claim protocol: fit on Bench(60,160) fast, freeze, then wear on Bench(110,360) exact and on the held-out bench.
   - Statics of the two-force knee link and the stop dowel: shear and bearing stress.
   - `tools/alignment_paired.py` for the per-pose dump and the paired comparison with the lead.
4. **What, other than me, shows the number is right.**
   - The bench: the lead control through this file reproduces the lead's 13.00 fast.
   - The adversarial verifier, which re-runs the frozen exact bench and the held-out bench.
   - The paired per-pose comparison with the lead.
   - A red-team pose list: the stopped poses, pose 316 (contact on the positive side), the overhead contacts at 237
     and 264, and the held-out contacts with their depths.

## The mechanism

Everything from the scapula handler to hub 3 is the verified lead slipper-nose-knuckle-3r, loaded unchanged: the J1
and J2 seats on GH rays, the slaved knuckle K with its stop A / stop B, the hub-2 rim lobe, the bell crank with the
sliding 440C nose on the link-1a flank, the clock spring, b3 0.329, and the O20 v5 hubs. Two things change.

1. **The knee, re-centred.** Member 3 is hub 3's lower plate plus the E strap (8 x 3 Ti-6Al-4V). It runs lE from hub 3
   to pin a. The knee link (lc, O12 ends, 10 wide) runs to pin b on the arm pad. Both pins are MR63ZZ pairs (stk 6.0,
   the lead's build rule). The pins are parallel to J3. The knee is a planar RRR closure in hub 3's plane, solved in
   closed form, as in the lead. Its window [ang_min, 180 - ang_min] = [25.22, 154.78] is a physical knee stop. The new
   proportions keep the knee angle near 90 deg over the whole drift cloud, about 15 mm in radius. The lead's knee runs
   from 86 to 152 deg and exits its window on 9 bench poses.
2. **A hard stop on J3's own angle.** q3' = q3 + phi, where phi is member 3's rotation about the J3 axis from the
   knee closure, so q3' is the link 2 -> member 3 angle. The stop is an ISO 8734 2 m6 440C dowel pressed axially into
   hub 3's lower plate (member 3) at r 7.5 mm. It runs in a 2.1 x 1.0 mm arc groove cut under link 2's ring (member 2),
   inside the O20 x 12.25 stack: the MR117 bearing OD 11 puts the bearing at r 5.5 < 7.5 - 1.05, and the rim is at
   r 10. There is a lower end at J3MIN and, in the two-sided column, an upper end at J3MAX. It adds no body, no DOF and
   no skin-facing metal. The spec's alternative, a 3 x 2.5 x 2 tab on link 2's root, would add metal at the hub rim, so
   it was not modelled.

DOF: 3 ACTIVE (J1, J2, J3, encoded). K, the bell crank and the two knee pins are passive rotations: K is slaved, and
the pins are cuff alignment outside the count. 0 passive translations. No gears, pulleys or cables. The stop bounds J3
and adds nothing to the count. Complexity is the lead's like-for-like 18.25: the dowel is one catalogue part, with no
body, joint or loop added.

## The stop and the knee as a force path (statics, the judge's addition)

The knee link is a two-force member in hub 3's plane, because both of its pins are parallel to J3. A moment M about
J3 between the arm and member 3 crosses the knee as a force F = M / d_perp along the knee link, where
d_perp = lE sin(knee angle) is the distance from the J3 centre to the knee link's line. At the stop, the same M ends
on the dowel: F_dowel = M / r = M / 7.5 mm = 133 N per N m.

| exact Bench(110,360), taken poses | lead (lE 67.8, lc 21.1, stk 4.85) | this row, best (lE 97.1, lc 24.4, stk 6.0) |
|---|---|---|
| knee angle | 86.2-152.2 deg | 59.3-105.9 deg (held 59.3-107.1) |
| d_perp min / median | 31.6 / - mm | 83.5 / 87.7 mm |
| knee link force per N m about J3 (worst taken pose) | 31.6 N | 12.0 N |
| window margin (deg) | 61.0 / 2.6 | 34.1 / 48.8 |
| window margin in d (mm) | - / 0.33 | 11.4 / 13.2 |

What the wearer feels at the stop. It is a rigid end of J3 travel: the arm's internal/external rotation moment about
J3's axis, which lies within 19 deg and 14 mm of the humeral axis, comes to rest on the dowel. In the unpowered MVP1
the moments in normal motion are the exo's own inertia and bearing drag, about 0.1-0.3 N m. They load the knee link
with 1-4 N and the dowel with 15-40 N. A deliberate push into the stop is limited by the cuff, because a strapped cuff
on soft tissue twists and slips at roughly 2-5 N m about the humerus (an estimate, not measured here): 270-670 N on
the dowel. Sizing at 10 N m gives 1.33 kN.

- ISO 8734 2 m6 440C, hardened, in single shear: tau_y ~ 0.58 x 1.9 GPa = 1.1 GPa on 3.14 mm2, so 3.4 kN, a factor of
  2.6 at 10 N m.
- Groove flank in Ti-6Al-4V, 1.0 mm engagement, projected 2.0 x 1.0 mm: 0.67 GPa at 10 N m against a bearing yield of
  about 1.3 GPa, a factor of 2. Conformal contact (O2 dowel in a 2.1 mm groove).
- Knee pins (MR63ZZ pairs): 110-125 N at 10 N m. That is at or above the static rating of a pair (C0r is about 0.06-0.07
  kN per bearing, a typical catalogue value that is not in tools/hardware_catalogue.json). At the cuff-slip limit of
  2-5 N m the load is 22-62 N, inside the rating.
- The lead's knee, at its own window end, carries M / (67.8 sin 154.8) = 35 N per N m. The re-centred knee carries a
  third of that per N m at every pose.

The stop does not take a pose. At the 8 bench poses where it engages, the lead's knee ran out of its window: the lead
calls them "slide" and this row calls them "j3stop". Both are blocked. Without a stop, the re-centred knee takes those
poses into contact. The proposer's per-pose diagnosis, without the stop, found hub 2 and the K-housing member 7 0.03 to
7.9 mm into the skin at 182 / 184 / 203 / 205. That is chain metal the knee cannot move, so the stop is the honest
end, not a lever for reach.

## Red team: the stop placed to admit one pose (found by the CMA, rejected)

The two-sided CMA found plain 11.88 fast (reach 0.7812, one more ws pose than every other row of this sweep, 0
contacts). It got there by moving J3MIN to -112.8 .. -113.4. The deepest taken pose then sits 0.17-0.46 deg inside the
stop. The pose it admits is one of the stopped cone poses. On the exact bench without a stop (proposer's
`cone/fz_kw25.json`) the cone poses read 182 hub 2 -1.67 mm, 203 hub 2 -0.03 mm, 205 -4.48 mm, 184 parts (E vs link 2
-0.9), and 208 / 209 / 211 / 238 hub 2 and K housing 12-22 mm into the skin. On the fast bench, the 203-type pose clears
by a hair. A stop that sits 0.2 deg from a taken pose to admit a pose whose metal is 0.03 mm from the skin on the exact
bench is tuned to the sample. The search objective therefore charges every degree of stop margin under 4 deg
(`stop_pen` in the sweep rows). Those configurations score 16.6-22.8 on the objective and are not the row's best. They
are in the sweep file (cma2s-g3-2, g6-2, g6-3, g7-3) for the verifier.

## Measured (claim protocol: fit Bench(60,160) fast, freeze, wear Bench(110,360) exact and the held-out bench)

Everything below ran locally on <= 2 niced processes, because the farm is past its budget line. The lead control
through this file reproduces the lead exactly on the fast bench: plain 13.00, 2 mm 16.47.

| column | knee (lE / lc / phiE / phib), stop, stk | fast plain / 1 mm | exact Bench(110,360) | held out | contacts bench / held (T5 depth sum) | ws taken bench / held |
|---|---|---|---|---|---|---|
| lead slipper-nose (verified) | 67.8 / 21.1 / -2.8 / -58.8, none, 4.85 | 13.00 / 14.16 | **18.49** | 23.45 | 2 / 10 (14.75 / 46.12 mm) | 261 / 650 |
| spec, one-sided (proposer, same code) | 82 / 27 / 3.8 / -96.6, q3' >= -105, 4.85 | 13.13 / 14.29 | 18.36 | 22.79 | 3 / 14 (- / 64.6 mm) | 261 / - |
| **row best: CMA two-sided** | 97.14 / 24.35 / 0.75 / -91.80, [-111.90, 122.74], **6.0 (MR63ZZ)** | **12.50** / 13.66 | **18.28** (score 93.35) | **22.38** | 4 / 14 (20.24 / 60.97 mm) | 262 / 659 |
| CMA one-sided | 100.96 / 31.17 / -2.25 / -86.04, q3' >= -110.26, 6.0 | 13.44 / 13.44 | 18.84 | see row note | 4 / - | 261 / - |

Row best, exact bench: reach 0.7278 (262/360), follow 1.0, ib14 0.9012, ib10 0.5739, contact 0.0106 (4 poses). The
gap splits into reach 17.22 + in-band 0 + contact 1.06. The 1 mm near-touch gap is 19.92 (lead 20.12) and the 2 mm one
34.84 (lead 33.02). Min metal over taken poses 0.07 mm, as the lead. Overhead (elev >= 140) 8/28, as the lead: 14 fold,
3 J3 stop, 3 contact. Held out: reach 0.6922 (659/952), ib14 0.900, 14 contacts, overhead 18/71. Why (bench): fold 88,
J3 stop 6, contact 4. In the lead: fold 88, knee slide 9, contact 2.

Knee and stop over the taken poses, exact. The knee runs 59.3-105.9 deg on the bench and 59.3-107.1 held out, so its
window margins are 34 / 48 deg = 11.4 / 12.8 mm in d (lead 0.33 mm). d_perp is at least 83.5 mm (12.0 N per N m about
J3). q3' spans -109.2 to 116.1 on the bench and -111.16 to 119.44 held out. Every fit-clip frame (356 at 10 fps)
closes with the knee in its window, at q3' -62.4 to 101.4: 0 frames cut by either stop.

**Paired against the lead** (`tools/alignment_paired.py compare`, per-pose dumps in `docs/alignment/remeasure/`):

| wear | diff (this - lead) | split: reach / in-band / contact | ws taken only here / only lead | contacts only here / only lead / both | 90 % CI | P(better) |
|---|---|---|---|---|---|---|
| bench | -0.20 | -0.28 / -0.45 / +0.53 | 1 / 0 | 2 / 0 / 2 | [-1.05, +0.80] | 0.60 |
| held | -1.08 | -0.95 / -0.57 / +0.44 | 11 / 2 | 4 / 0 / 10 | [-1.86, +0.06] | 0.935 |
| pooled | -0.82 | -0.76 / -0.53 / +0.47 | 12 / 2 | 6 / 0 / 12 | [-1.46, +0.09] | 0.918 |

This is a **tie on the bench** under the 1-point rule. Held out it gains a point, with an interval that touches 0.

## Red team on the row best (per pose, exact)

1. **The one pose it adds pinches.** On the bench the only pose taken here and not by the lead is 203 (plane 0, elev 90,
   axial 45). Its metal is 0.72 mm from the skin (hub 2 / K housing). It is the pose that sat at -0.03 mm in the
   proposer's no-stop run. Count it as a near-touch, not as reach.
2. **Contacts get worse (T5).** Bench: 4 contacts, 20.24 mm summed, worst 8.93 (lead: 2, 14.75 mm, worst 9.01). Two
   are new: 205 (0, 105, 15) with hub 2 at -4.28 mm, which the lead's knee blocked as a slide and which this stop
   admits, and 316 (60, 150, -105) with link 2 / hub 2 at -1.23 mm. 237 and 264 are the lead's crank / horn contacts,
   unchanged. Held out: 14 contacts, 60.97 mm summed, worst 9.86 (lead: 10, 46.12 mm, worst 9.05). The 4 new ones
   are 447 (-0.21), 683 (-9.86), and **835 (90, 15, -150) and 978 (120, 15, -165)**. The last two are low elevation at
   extreme axial rotation. The lead takes both cleanly, and they are far from hub 2 and the drive. The held contact
   split by part counts **2 arm-pad and 1 knee-link contacts**. So the knee group itself probably touches there; this
   still needs per-pose confirmation, since the lead's held dump has no part split to compare. The longer E strap
   seats the knee plane about 2 mm lower (pad median 6.2 mm vs the lead's 8.1 on the bench), and extreme rotation
   finds it.
3. **The upper stop does nothing on the exact bench.** J3MAX 122.74 caught the fast bench's positive-side contact,
   but on Bench(110,360) pose 316 sits below it and stays a contact. Held out, the taken q3' reaches 119.44, 3.3 deg
   from the stop. The two-sided column is effectively one-sided at -111.9. Held out, the lower stop sits 0.74 deg past
   a taken pose (-111.16), so the stop is close to the sample there too. A 3 mm GH-centre error moves phi by about
   2 deg (proposer), so the stopped / taken split near -111 is not robust.
4. **The in-band gain is dilution.** Per part (exact bench), the E strap grows from 104 to 164 samples per pose at
   97.9 % in band, and the knee link reaches 99.9 % (lead 94.1 %). Without the knee group (E, boss, pad, knee), the
   chain's own in-band is **0.8590 vs the lead's 0.8689**: hub 2 0.912 vs 0.953, crank 0.801 vs 0.818. Hub 2 sits
   0.5 mm higher (median 11.6 vs 11.1 mm). The likely cause, inferred and not isolated: the fit bench's taken set
   changes when the stop admits the 203-type pose, and the frozen fit lifts hub 2 / the crank to clear it. The total
   0.9012 clears the 0.90 target only because the longer E strap adds well-placed samples.
5. **Continuity.** The flood fill on the exact bench gives full 18.28 (0 dropped) and knn 19.97 (lead 18.49 / 20.16).
   No branch change and no knee jump: the knee stays 34 deg or more inside its window everywhere.
6. **Fold margin and K-at-rest watches (G4, M5).** These are the lead's, unchanged. The chain, the K law and the drive
   are the lead's. The fold-side losses are identical (88 fold on the bench).
7. **A longer knee buys fast-bench points and loses them held out.** The one-sided CMA pick (lE 101, lc 31.2) is
   clean on the fast bench: 1 mm gap = plain 13.44, no metal under 1 mm. Worn exact it scores **18.84** (4 contacts:
   203 at -0.03, 237, 264, 316) and held out **23.90** (20 contacts). The held contacts include 9 by the arm pad and the
   knee link, at 764 / 835 / 907 / 978 / 1047: elev 15, axial -135 to -165. The fast bench does not sample
   low-elevation extreme rotation, so it cannot bound the knee's size. The bound is held out, on the arm hanging down
   and rotated, which is the same lesson as "select on the envelope bench".
8. **The knee needs the MR63ZZ stack.** The row best worn at the lead's stk 4.8534 (like-for-like) fails knee vs E
   clearance on 329 poses (fast fit 160.0, exact 164.88). At that stack the long knee link crosses the E strap's end
   inside the 0.15 mm adjacent gap. The row is stated at stk 6.0, the MR63ZZ pair from the lead's build rule. The
   lead's own 18.49 is at 4.8534, so the comparison is "this row as it would be built" against "the lead as verified".

## Sweep and convergence

There are 352 configurations on Bench(60,160) fast, in `docs/concepts/sweeps/conecut-knee-knuckle-3r.json`:

- 200 coarse Latin-hypercube configurations over lE 70-98, lc 20-38, phiE -10..12, phib in both assembly modes
  (-112..-74 and 74..112), J3MIN -112..-100, J3MAX off or 114-124, and stk 4.85 / 6.0. Each configuration was
  pre-filtered on the exact kinematic knee margin (>= 10 deg) over the drift cloud: bench, held out and every fit-clip
  frame.
- Two CMA-ES runs at stk 6.0, 1 worker each: two-sided 80 configurations, one-sided 72.

Objective: the 1 mm near-touch gap + 2 x max(0, 18 - knee margin) + the stop-margin penalty (< 4 deg) + 100 if dishonest.

- The phib > 0 assembly mode collides everywhere (best 17.48; most configurations fail on parts).
- 62 of the 200 coarse configurations fail on part-part clearance (knee or pad vs link 2 / E); 14 of the 21 in the
  phib > 0 mode are among them.
- Plain gap: the floor is 12.50, which is the reach term alone (reach 0.775 is fixed by the chain). Below it are only
  the tuned-stop configurations at 11.88 (red team above).

**Convergence gate (binding), passed.**

| measure | gain over the 2nd half | gain over the last third | top-5 spread |
|---|---|---|---|
| search objective | 0.08 pt | 0.04 pt | 0.02 pt |
| plain gap | 0.23 pt | 0.01 pt | 0.23 pt |

The fast landscape is a plateau. Once ib14 >= 0.90, the knee earns nothing on the fast bench, and the only lever
left is relabelling one contact pose with a stop.

## Verdict

**Screened: a measured tie with the lead, not a new leader.**

- Frozen exact Bench(110,360): 18.28 (score 93.35) vs 18.49. Paired diff -0.20, CI90 [-1.05, +0.80].
- Held out: 22.38 vs 23.45. Diff -1.08, CI90 [-1.86, +0.06], P(better) 0.935. The gain comes from 11 held-out poses
  where the lead's knee ran out of its window.
- Flood: full 18.28, knn 19.97.
- Complexity 18.5, against the lead's 18.25 plus one catalogue dowel.

No bench pose is newly taken except 203, and that one is a 0.72 mm near-touch. The stopped poses bind on hub 2 and the
K-housing metal of the chain. The in-band gain is the longer E strap's dilution: the chain's own in-band falls
0.8689 -> 0.8590. Contacts get worse: bench 4 vs 2 (20.24 vs 14.75 mm), held 14 vs 10 (60.97 vs 46.12 mm), with new
pad / knee contacts at low elevation and extreme rotation held out. So the T5 watch reason on the lead gets worse here.

What it does deliver, measured: a knee that never binds and a better force path. The window margin is 11.4 / 12.8 mm
in d against the lead's 0.33 mm, the knee link carries 12 N per N m of J3 moment against 31-35, there are 0 held
knee slides against 32, and the J3 end is a clean dowel stop at 133 N per N m.

**What next (for the knee column the long-dyad picks wear).**

1. Cap the knee's size by the held-out low-elevation extreme-rotation poses, not by the fast bench. lE ~82 / lc ~27
   (the spec) had 14 held contacts against 20 for lE 101 / lc 31. Add 764 / 835 / 907 / 978 / 1047 to the envelope
   search bench.
2. Do not place J3MIN to admit the 203 / 205 pair. On the exact bench they straddle any stop: 203 is taken at 0.72 mm
   and 205 is a contact at -4.28 mm, both chain metal. A stop at -105 (spec) blocks both.
3. The verifier: re-run the paired CI, the flood, the clip q3' table, and the per-pose T5 against the lead. Dumps are in
   `docs/alignment/remeasure/conecut-knee-knuckle-3r_{bench,held}_perpose.json`.

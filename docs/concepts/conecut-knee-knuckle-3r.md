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

| | lead (lE 67.8, lc 21.1) | this row, best (lE ~97, lc ~24-27) |
|---|---|---|
| knee angle over taken poses (fast) | 86-152 deg | ~65-107 deg |
| d_perp min / median (fast, taken) | 31.9 / 67.6 mm | 86-89 / 91-93 mm |
| knee link force per N m about J3 (worst taken pose) | 31.3 N | 11-12 N |
| window margin (deg, fast taken) | 61.0 / 2.8 | 40 / 48 |
| window margin in d (mm) | 20.2 / 0.36 | ~15 / ~13 |

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

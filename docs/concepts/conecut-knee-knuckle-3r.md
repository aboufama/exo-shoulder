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

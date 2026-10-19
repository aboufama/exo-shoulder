# trimlug-k165-knuckle-3r: the slipper-nose lead with its horn lug trimmed / raised at the two elev-165 contacts

Lens: round 11, lens 3 lever c (overhead cone), run as a polish of the lead's T5 watch reason. Family: slaved-knuckle 3R
(pin knee). 3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, no gears / pulleys /
cables / rods. Model: `docs/concepts/models/trimlug-k165-knuckle-3r.py` (on the lead
`docs/concepts/models/slipper-nose-knuckle-3r.py`, SN_CELL=lead). Sweeps: `docs/concepts/sweeps/trimlug-k165-knuckle-3r.json`.
Row: `docs/concepts/rows/trimlug-k165-knuckle-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Do not move the working surface if dead metal is what touches. The flank is a ruled cone through GH, and the nose
     only uses a 2.5 mm radial slice of it. Most of what dips into the skin at pose 264 is the lug's 6 mm back band and
     its outer end, not the flank face. The first fix is to remove metal the contact never uses. That means a
     trim at the farthest contact radius plus a wall, and a chamfer on the back band's underside that rises with the
     distance behind the flank. Neither touches the nose, the arm or the cam table, so neither can cost drive stroke
     or crank in-band. Only if that is not enough does the flank layer itself go up, and then the nose has to be
     lengthened and the arm raised with it.
   - Count what the lift really moves. Raising the lug's shell by dz raises its top too, so the arm tip that sweeps
     over it must rise by dz. The nose dowel must be dz longer to keep a full 2.5 mm contact line. That arm rise is the
     in-band risk the judge named, so it is modelled as metal, not assumed away.
   - Report contact as depth (T5), not only as a pose count. A 1 mm improvement that leaves the pose in contact is still
     real for the wearer: the drive presses less into the deltoid. Report the held-out depth too.
2. **Rawest material.** The posed skin itself: the bench's exact per-pose skin distance field, sampled at every lug,
   arm, nose and hub-cap point at poses 237 and 264 and over every taken pose. The motion clips, both bench and held
   out, with the held-out set only as a column. The lead's per-pose lost list
   (`docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json`). The cam table: contact radius, pressure
   angles and lift-off per 0.25 deg of K. Not the round-11 summary numbers. Those are only the hypothesis to check.
3. **Specific methods and tools.**
   - The lead's spherical conjugate-cam synthesis, re-run when the lug layer changes. The flank is the same ruled
     surface, but the arm-over-lug clearance (CRK-HORN) and the lug's swept cut are re-checked.
   - Per-sample skin depth with r from K's axis and the distance behind the flank.
   - The lead's claim protocol: fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact and on the held-out
     bench.
   - The farm sweep over the trim / chamfer / lift / crank / cap parameters, and CMA-ES only if the coarse sweep is
     not flat. Drive law, beta, g, r_c and every seat stay fixed at the lead's verified values, as the spec says.
4. **What, other than me, shows the number is right.**
   - The bench (`tools/concept_bench.py`), exact path.
   - The lead's Frozen class, which reproduces 18.49 before any change.
   - The held-out bench.
   - The 1 / 2 mm near-touch audit.
   - A red-team pose list: every taken pose whose minimum metal falls by more than 0.5 mm, and the lowest metal over the
     cone set.

## What was built

The model is `docs/concepts/models/trimlug-k165-knuckle-3r.py`. It loads the lead (`slipper-nose-knuckle-3r.py`,
SN_CELL=lead) unchanged and points every model name in the lead's module chain at `TLModel`. After the lead's own drive
synthesis (`_rod_metal`), `TLModel` applies cuts on the existing custom parts. Every cut defaults to OFF, which gives
the lead exactly.

- **Lug trim.** `trim_wall` keeps the horn lug's band only where r_K <= the farthest flank contact over the drive's
  whole range (19.77 mm at dK_lim 49.8) + the wall. The flank face over the full stroke is kept, so the cam table,
  dK_lim (49.8, horn PA 36.1 + friction 5.0 = 41.1 <= 43) and the stroke do not change.
- **Back-band thickness.** `back_t` sets how far the band reaches behind the flank (the lead's is 6 mm).
- **The spec's radial lift.** `rlift` / `lift_r0` lift the lug only, which is OPTIMISTIC. The longer nose and the
  raised arm tip that a real lift needs are left out.
- **The spec's crank-arm underside cut.** `crank_cut`.
- **A 45-degree chamfer on the arm tip's outer-lower edge.** `crank_edge`. Its side wall and chamfer face are added
  as contact-only samples.
- **A hub-2 top-ring edge break.** `cap_break`.
- **A dense contact-only copy of the lug.** `dense`=1, the default. It is a 0.5 mm grid along and behind the flank:
  underside, mid layer and top, with the same cuts. It is skin-checked like every contact-only sample and not scored
  for in-band.

The dense copy is a measurement change. The lead's lug is 23 samples, so a trim edge would otherwise be unsampled. It is
reported as its own column: lead + dense, no cut. The claim protocol is the lead's own, with its Frozen class and the
same attribute list plus `_trim_info`: fit on Bench(60,160) fast, freeze the shape, wear it on Bench(110,360) exact and
on the held-out bench.

## What was measured first: the spec's premise is wrong in direction

Per-sample skin depth at the two elev-165 contacts, Bench(110,360) exact, the lead's frozen shape
(`scratchpad probe1/probe2/probe3`, the numbers below):

**Pose 264 (30, 165, -60): four parts in the skin.**

| part | depth (mm) | where |
|---|---|---|
| lug top (contact samples) | -5.74 | r_K 24.2 |
| lug underside | -5.34 | r_K 23.0, 6 mm behind the flank |
| crank arm | -0.26 | the arm tip's outer-lower edge (r_K 18.16, the last arc sample) |
| hub 2 | -0.09 | the side-wall ring 8.17 mm up its 12.25 mm crown |
| hub 2 | -0.03 | the top ring (only this one is the cap edge) |

**Pose 237 (15, 165, -60):**

| part | depth (mm) |
|---|---|
| crank (contact set) | -9.00 |
| crank underside | -8.5 |
| lug top | -8.49 |
| lug underside | -7.07 |
| hub K's own O20 disc | -2.65 (no drive change saves this pose) |

**The skin comes in from the side and from above, not from below.** Directional sensitivity at 264, from the same probe:

- A radial lift of the lug along unit(X) makes it DEEPER. +1 mm costs 0.12-0.20 mm on the underside samples, and +2.5
  mm costs 0.16-0.37. The top samples get deeper too. At 237, +1 mm costs 0.4-0.7.
- Pulling the same samples 1 mm toward K's axis (r_K -1) gains 0.9-1.0 mm.
- On the crank, a radial +0.3 mm (the spec's underside cut) gains 0.02 mm. r_K -0.5 gains +0.47 and clears the
  underside sample (0.21). Moving 0.5 mm along +uK costs 0.17.
- Hub 2's -0.09 is its side wall 4 mm below the cap. A 0.5 mm cap edge break moves only the top ring.

Two-pose check (exact, frozen lead shape + the cut; `k165` mode):

| config | 237 depth | 264 depth | T5 (mm) | 264: parts still in the skin |
|---|---|---|---|---|
| lead (dense = lead sparse) | 9.00 | 5.74 | 14.74 | lug top -5.74, lug -5.34, crank -0.26, hub 2 -0.09 |
| rlift 2.5 (spec lift, optimistic) | 10.21 | 5.86 | **16.07 (worse)** | lug top -5.86, lug -5.71 |
| crank_cut 0.3 (spec) | 9.00 | 5.74 | 14.74 | crank -0.24 |
| cap_break 0.5 (spec) | 9.00 | 5.74 | 14.74 | hub 2 wall -0.09 unchanged |
| crank_edge 0.5 / 1.0 (lateral chamfer) | 9.00 | 5.74 | 14.74 | underside clears; the side wall above it -0.23 / -0.19 |
| **trim_wall 1.5 (r_trim 21.27)** | 9.00 | **4.18** | **13.18** | lug top -4.18, lug -3.29 (r_K 20.5, 2.3 mm behind the flank's end) |
| trim_wall 1.0 (r_trim 20.77) | 9.00 | 3.67 | 12.67 | lug -3.29 |
| trim 1.5 + back_t 4 | 9.00 | 4.18 | 13.18 | (237's lug 8.35 -> 6.96; 237 stays the crank's 9.00) |
| the spec's combination (trim 1.5, rlift 2.5, cut 0.3, cap 0.5) | 9.88 | 4.21 | 14.09 | lug -3.63 |

**The limiter, measured.** The metal that keeps 264 in contact is the lug's band directly behind the END of the flank's
stroke. At r_K 19.6-20.5, 2.3 mm behind contacts at r_K 19.1-19.8, it sits 2.2-3.3 mm inside the skin. Clearing it needs
the lug to end at r_K ~18.0. The flank reaches r_K 18.0 at dK ~35 deg (cam table: 0 -> 14.9, 30 -> 17.4, 35 -> 18.0,
45 -> 19.1, 49.8 -> 19.8 mm), against the drive's 49.8 and the bench's taken 45.6. That stroke is the lead's fold wall:
73 of its 88 fold losses are stretched poses on K's drive stroke. Pose 264 is therefore not clearable inside this
morphology, where the drive law, beta, g, r_c and the seats are fixed. Even if it were, the crank's side wall (-0.19 after a
1 mm chamfer) and hub 2's housing wall (-0.09) would keep it in contact unless the arm tip is narrowed ~0.5 mm and hub 2
gets a ~0.3 mm flat. The lead note's stop rule ("stop if ... pose 264 is not cleared") applies. What remains is the T5
depth.

## Results: the claim columns (the lead's protocol, the farm)

All rows are frozen: fit on Bench(60,160) fast, worn exact without a refit, through the lead's own Frozen class.

| config | Bench(110,360) exact | score | reach | ib14 | contact poses | T5 bench (mm) | held out | T5 held (mm, 10 poses) | near1 | min metal |
|---|---|---|---|---|---|---|---|---|---|---|
| lead (sparse lug = the lead's row) | 18.49 | 93.28 | 0.725 | 0.8955 | 2 | 14.74 | 23.45 | 46.13 | 20.12 | 0.07 |
| lead + dense lug check (measurement) | 18.49 | 93.28 | 0.725 | 0.8955 | 2 | 14.74 | 23.45 | 46.35 | 20.12 | 0.07 |
| **trim_wall 1.5 (pick)** | **18.51** | **93.27** | 0.725 | 0.8953 | 2 | **13.18** | **23.47** | **40.59** | 20.14 | 0.07 |
| trim_wall 1.0 | 18.51 | 93.27 | 0.725 | 0.8953 | 2 | 12.67 | 23.47 | 38.71 | 20.14 | 0.07 |
| trim_wall 1.5 + back_t 4 | 18.56 | 93.25 | 0.725 | 0.8948 | 2 | 13.18 | 23.52 | 40.22 | 20.19 | 0.07 |

- **Unchanged against the lead.** Reach 261/360, overhead 8/28 (held 18/71), follow 1.0. The why-list is the same:
  fold 88, knee slide 9, contact 2. Parts 0. The drive is unchanged: dK_lim 49.8, horn PA 36.1 + friction 5.0 = 41.1,
  CRK-HORN clearance 15.71.
- **Gap.** 18.49 -> 18.51. The +0.02 is in-band accounting: 3 of the 23 scored lug samples are removed, and they were
  in band (horn ib14 0.956 -> 0.955).
- **Contact depth (T5).** Bench 14.74 -> 13.18 mm (pose 264: 5.74 -> 4.18). Held out 46.35 -> 40.59 mm. The five held-out
  contacts where the lug is the deepest part each get 1.2-1.7 mm shallower:
  - (15, 150, -60): 7.29 -> 6.13
  - (30, 150, -45): 5.33 -> 4.07
  - (45, 165, -45): 5.80 -> 4.18
  - (60, 165, -30): 6.87 -> 5.15
  - (30, 165, -45): still 9.06, the crank
- **The lead note's first test (cone set: 110 clips + 47 cone poses, exact).** In-band 0.8955 (lead), 0.8954 (rlift 2.5,
  optimistic), 0.8953 (trim 1.5). The in-band gate (drop <= 0.005) passes. The pose gate (264 cleared) fails, so the
  note's stop rule applies, and no wider search was run.
- **Fast grid (Bench(60,160), the fit bench; it has no contact pose, so it reads only the in-band cost).**
  - Trims: 13.00-13.06.
  - back_t 3-4: 13.0-13.06 (in-band 0.8941-0.8944).
  - rlift 2.5: 13.02.
  - crank_cut 0.3 / 0.6: 13.21 / 13.40. The arm's arc rises out of band, crank ib14 0.819 -> 0.804, which is exactly the cost
    the judge predicted for the lift.
  - cap_break: 13.00.
- **Convergence gate on the grid (score points).** 0.00 / 0.00 / top-5 spread 0.004: passes. CMA-ES was not run, because
  the fit bench is flat in these cuts and on the frozen bench T5 is monotone in the trim, bounded by the wall rule.

## Red team of the pick

- **The pose that jams.** None new: parts 0 on both benches. The trim only removes lug metal, so the low-arm-to-lug
  clearance can only grow.
- **The point that pinches.** The lead's own 0.07 mm at (-60, 60, 105) is unchanged. near1 is 20.14 against the lead's
  20.12.
- **The optimistic numbers.**
  - (1) The lift test leaves out the 2.5 mm longer nose and the raised arm tip. It loses anyway (T5 16.07, cone in-band
    -0.0001 before the arm's cost, and the arm alone costs ~0.2 fast per 0.3 mm, per crank_cut).
  - (2) The trimmed lug's edge is sampled by the dense contact-only copy (0.5 mm). Its top sets 264's 4.18.
  - (3) The lead's own held-out T5 was 0.22 mm optimistic with the sparse lug (46.13 vs 46.35 dense).
  - (4) The wall. 1.5 mm behind the farthest contact (r_K 19.77) at the end of the drive's stroke only. Elsewhere the 6 mm
    band is intact. Under MVP1 (clock spring, 5-15 N at the nose) this is trivial. Under MVP2's ~175 N line load the wall
    is in compression over the 3 mm lug layer (~40 MPa), fine in the DLC-coated Ti flank. The 1.0 mm wall (T5 12.67) is
    listed, not picked.
- **What would clear 264.** It is not in this morphology. All three would be needed:
  - the lug band ending at r_K ~18 (dK ~35, the stroke wall);
  - a ~0.5 mm narrower arm tip;
  - a ~0.3 mm flat on hub 2's housing.

  The first one costs the K stroke that the round-11 levers are trying to buy.

## Verdict

**Screened.** This is a T5 depth polish of the lead, not a lead change: 18.51 against 18.49 frozen exact, 23.47 against 23.45
held out, -1.56 mm bench and -5.76 mm held-out contact depth.

The spec's central claim is refuted by the skin itself. A radial lift of the flank / nose layer, the crank underside cut
and the cap edge break do not clear 264. The lift deepens both elev-165 contacts, because at elev 165 the upper arm's skin
comes over the drive from the side and from above.

The lesson that carries beyond this morphology: **near-skin metal at overhead poses must be cut laterally (in r_K / in
plan), not lifted.** Read the skin normal at the contact before choosing the direction of a relief.

## Verification (independent skeptic, 2026-10-17 12:25 UTC)

**Verified, not refuted. Not a lead change.**

Harness: `docs/concepts/verify/trimlug-k165-knuckle-3r.py`. It loads the claim's model unchanged and reuses the lead's
verifier (`verify/slipper-nose-knuckle-3r.py`), retargeted at TLModel. The protocol is the lead's: fit on Bench(60,160)
fast, freeze the shape, wear it exact. The jobs ran on the farm (4 jobs, $0.14), and the bench column was repeated locally
with identical numbers. Raw outputs are in `verify/trimlug-k165-knuckle-3r_v_{bench_frozen,held_frozen,bench_edge,bench_lead}.json`.

| column | gap | score | reach | follow | ib14 | ib10 | contact poses | T5 (mm) | near1 | min metal |
|---|---|---|---|---|---|---|---|---|---|---|
| lead control, same harness (trim off) | 18.49 | 93.28 | 0.725 | 1.0 | 0.8955 | 0.5163 | 2 | 14.74 | 20.12 | 0.07 |
| **pick: trim 1.5, frozen exact Bench(110,360)** | **18.51** | **93.27** | 0.725 | 1.0 | 0.8953 | 0.515 | 2 | **13.18** | 20.14 | 0.07 |
| pick + flank-edge strip (trimmed) | 18.47 | 93.28 | 0.725 | 1.0 | 0.8957 | 0.5163 | 2 | 13.18 | 20.10 | 0.07 |
| pick, held out | 23.47 | 91.47 | 0.6828 | 1.0 | 0.8941 | 0.5136 | 10 | 40.59 | 26.56 | 0.33 |

**Base checks (the lead's verifier).** 0 failing taken poses: 0 of 371 on the bench, 0 of 852 held out.

- Closure, nose vs lug and K sense all pass.
- Pressure angle plus friction: horn 40.77, crank 34.47. Both are at or under 43 (and 45).
- th margin: 5.181 on the bench, 5.006 held out.
- Conjugate undercut: 0 points.

Overhead (elev >= 140): 8 of 28 poses taken, the same as the lead.

The why-list is unchanged (fold 88, knee slide 9, contact 2), so the kinematics are untouched. The lead's continuity
flood therefore still applies: 18.49 full, 20.16 knn.

**Trim checks added for this claim:**

- **T1, contact line on retained metal.** I took the dowel's contact line along the GH ruling (rings at -1.25 / 0 /
  +1.25 mm) and read it at the trim's own radius. The edge margin is 2.53 mm over the taken stroke and 1.99 mm over the
  full 49.75-deg stroke.
  - The trim is decided on the lug underside and carried up the GH ray. The real margin is therefore larger than the
    stated "1.5 mm wall".
- **T2, back thickness behind every used contact.** At least 4.30 mm (4.15 held out), against 6 mm untrimmed. This is
  more than the doc's red team assumed, so the strength argument is conservative.
- **T3, connectivity.** The trimmed lug is connected exactly as the lead's lug is: one piece at 3 mm.
- **T4, consistency.** No member-1 sample is left outside the trim.
- **T5, dense lug part-to-part.** The claim adds the dense lug copy as contact-only, so it is never checked against
  other parts. I wore it against every member at every taken pose:
  - crank: 0.153 mm, the arm's 0.15 running gap over the lug;
  - nose: 0.424 mm, its own sliding pair;
  - every other member: at least 20.96 mm.

  These are the same minima as the lead, so there are no new collisions.

**Champion on the same bench:** 75.94, from the risley-turret verifier (Bench(110,360) exact, kit checks plus 1 mm
clearance). Through the offset-skin-normal verifier it is 66.97. v_gap 18.51 is far below both, and no hard rule is broken:

- 3 active DOF, with K slaved;
- 0 passive translations;
- no gears, pulleys or cables;
- the trim only cuts link 1a's existing lug.

**What the verification does not support:**

- **A gap gain.** The gap is +0.02 worse than the lead's 18.49, because 3 in-band lug samples are removed. Both
  elev-165 contacts remain:
  - 237: crank 9.00, the trimmed lug still 8.35, hub K 2.65;
  - 264: lug 4.18, crank 0.26, hub 2 0.09.

  The row's limiter says 237 is "hub K's disc plus the crank". The lug is also 8.35 mm deep there; it does not set the
  pose's depth, so the conclusion holds.
- **The bookkeeping.**
  - The row verdict says 5 held-out contacts are lug-deepest. The table above lists 4, and the verifier's per-pose
    reading agrees with 4.
  - The sweep file holds 31 entries, all with one timestamp, against n_configs 45.

The deliverable that does survive is contact depth: T5 -1.56 mm on the bench and -5.76 mm held out, at +0.02 gap.

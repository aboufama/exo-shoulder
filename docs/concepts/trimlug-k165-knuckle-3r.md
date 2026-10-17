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

# slipper-nose-knuckle-3r: the drive's roller deleted, a hardened O3 nose slides on the flank

Lens: round 10, lens 3 (low complexity at the lead's reach). Family: slaved-knuckle 3R. 3 ACTIVE DOF (J1, J2, J3
encoded), K slaved and never read, 0 passive translations, no gears / pulleys / cables / rods.
Model: `docs/concepts/models/slipper-nose-knuckle-3r.py` (SN_CELL=lead | kneeless). Sweeps:
`docs/concepts/sweeps/slipper-nose-knuckle-3r.json`. Row: `docs/concepts/rows/slipper-nose-knuckle-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Put the friction where it is binding, not everywhere. The nose slides on both strokes. On the outward stroke the
     crank drives the horn; on the return the clock spring drives the crank through the horn. The friction cone adds
     atan(mu) to whichever body is being driven. The crank-side angle is 8-11 deg, so only the horn side on the outward
     stroke binds. The honest rule is therefore max(PA_horn) + atan(mu) <= 43 (45 gate, 2 deg slop). The spec's
     PA_kin = 43 - atan(mu) applied to both sides is the same rule, because the crank side never comes near it.
   - Ask whether a plain-bearing sleeve beats a bare nose. An iglidur sleeve O4 on the O3 dowel makes the flank contact
     roll and moves the slide to the journal. The effective coefficient is then mu_journal x r_pin / r_sleeve = 0.15 x
     1.5 / 2.0 = 0.11, worse than greased DLC sliding (0.05-0.087). At this size a bare hardened nose is the better slider,
     and the sweep's nose_r 1.5-2.0 covers the sleeve's geometry.
   - Check the load the nose really sees. MVP1 is unpowered (R17), so the nose carries the clock-spring force only
     (5-15 N at the contact radius 13-17 mm), and the friction drag at J2 is ~mu x N x r ~ 0.01 N.m, against R17's
     1 N.m. Under MVP2's 10 N.m (R9), part of that moment crosses K. There the O3 x 2.5 line contact on a DLC-coated Ti
     flank (p_max <= ~1.1 GPa, the substrate's limit) carries ~175 N. The MR63ZZ it replaces is rated C0r ~0.07 kN, so
     deleting the bearing raises the static capacity of the drive tip by ~2x. A hardened flank insert would carry ~640 N.
   - Re-fit the drive (g, beta, r_c, lift, nose_r) at the central friction case, mu 0.087, instead of only wearing the
     lead's mu~0 drive at a smaller pressure-angle cap. The stroke the friction takes away may come back from the
     law/flank geometry.
2. **Rawest material.** The posed skin itself: the bench's per-pose skin distance fields and the per-pose lost-pose
   list (fold / slide / contact, with plane, elevation, axial). The motion clips (the bench's clip frames) and the
   held-out clips (only in the held-out column). The skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`
   and the proximity atlas data for where hub 3 sits (`docs/research/proximity_atlas.md`). For the wedge, its own
   face-to-skin distances per taken pose and hub 3's crown height. Not the digested summaries in the round-10 text.
3. **Specific methods and tools.**
   - Spherical conjugate-cam synthesis per 0.25 deg of K: the parent's code, with the nose radius as the offset.
   - The friction cone in the pressure-angle budget.
   - Hertz line contact and Archard wear for the nose / flank pair (hand calc below).
   - The farm sweep (`tools/cloud_run.py sweep`), then CMA-ES (`tools/concept_cma.py`) as one farm job.
   - The claim protocol: fit on Bench(60,160) fast, wear the frozen shape on Bench(110,360) exact, then held-out and
     flood.
4. **What, other than me, shows the number is right.**
   - The bench (`tools/concept_bench.py`).
   - The frozen-exact Bench(110,360) claim, worn without a refit, through the same Frozen class that reproduces the
     lead at 18.67 (`kw/frz.py` harness = `SC.frozen`).
   - The held-out clips.
   - The flood (continuity) report.
   - The 2 mm / 1 mm near-touch audit (`PK.audit`).
   - The per-pose red-team list (lowest metal, contact poses by part).
   - The alignment auditor's ruling on the wedge, which gets both columns: flat and wedged, with hub 3's crown height.

## What was built

The model is `docs/concepts/models/slipper-nose-knuckle-3r.py`. It loads the parent unchanged: the lead
`roller-longdyad-knuckle-3r` (SN_CELL=lead) or the control `kneeless-roller-knuckle-3r` (SN_CELL=kneeless). It changes
four things:

- **Nose radius.** `RF.ROLL_R = nose_r` sets it. The flank is synthesised as the offset of the nose-centre path. Cusp,
  contact-on-lug, the lug's clearance cut and the tip's clearance to hub K all follow from it. The tip metal is the
  nose's end disc and rings at the roller's old layer, member 9.
- **No retaining head.** The roller's O4.5 x 0.8 retaining head is gone, because a pressed dowel has no head on the
  skin side.
- **Friction in the pressure-angle budget.** `RF.PA_MAX = 43 - atan(mu)`. A design whose taken stroke breaks the cap is
  dishonest.
- **Optional planar hub-3 wedge.** Its offset is bisected on the fit bench to keep >= 2.0 mm, and the frozen protocol
  copies it.

Each frozen claim is the same protocol that reproduces the lead at 18.67: fit on Bench(60,160) fast, freeze the shape
(drive, metal, wedge), wear it on Bench(110,360) exact. The worn model reports:

- the cam table;
- the 1 / 2 mm near-touch audit;
- the workspace in-band;
- the contact split by part;
- hub 3's crown and underside heights above the skin.

The mechanism record (tools/simplicity.py v2) gives **22.25**, against the lead's 24.25. The changes:

- -1 moving body (the roller), -1 passive rotation, -1 joint;
- rolling pairs 2 -> 1;
- +1 sliding pair (the nose on the flank);
- catalogue parts: -1 MR63ZZ, +1 ISO 8734 dowel.

The spec's 22.0 left the dowel uncounted. Passive translations: 0.

## Measured: fast Bench(60,160), the lead's seats and drive (160-config farm sweep, stage coarse1)

| mu (PA_kin) | nose_r | dK_lim | horn PA taken | plain gap | 2 mm gap | reach |
|---|---|---|---|---|---|---|
| 0 (43) | 3.0 (= the roller, no head) | 46.2 | 43.0 | 13.23 | 16.60 | 0.775 |
| 0 (43) | 1.5 | 52.8 | 39.9 | 13.26 | 16.62 | 0.775 |
| 0.026 (41.5) | 1.5 | 49.5 | 39.9 | 13.28 | 16.64 | 0.775 |
| 0.05 (40.1) | 1.5 | 46.5 | 39.9 | 13.29 | 16.64 | 0.775 |
| 0.05 (40.1) | 2.0 | 44.2 | 40.0 | 14.52 | 16.75 | 0.7625 |
| 0.05 (40.1) | 3.0 | 39.8 | 40.0 | 16.37 | 18.63 | 0.744 |
| 0.087 (38.0) | 1.0 | 44.5 | 37.9 | 14.58 | 16.79 | 0.7625 |
| 0.087 (38.0) | 1.5 | 42.2 | 37.9 | 15.18 | 17.40 | 0.756 |
| 0.087 (38.0) | 2.0 | 40.0 | 37.9 | 15.79 | 18.02 | 0.750 |
| 0.12 (36.2) | 1.5 | 38.8 | 36.1 | 16.43 | 18.67 | 0.744 |

**A smaller nose buys stroke at a given cap**, about +2.3 deg of dK per -0.5 mm of nose radius. The contact point
Q = C + r n moves toward the nose centre, and the horn-side pressure angle at a given dK drops. This is the lever that
pays for friction. At mu 0.05 the O3 nose already carries more stroke (46.5) than the roller (46.2). At mu 0.087 an O2
nose gets back 2.3 of the 4.3 deg that friction takes.

**The wedge on the lead cell: measured dead, 36 configurations.** Tilt 15 / 25 / 35 x azimuth 0-330 step 30 all give
drop 0.0 mm. Hub 3 on the pin-knee lead already passes 0.38 mm over the skin at one fit pose (plane 120, elev 30, axial
-135: across the body, internal rotation). A planar face kept >= 2 mm off the skin over every fit pose therefore cannot
go lower anywhere. On the kneeless control, hub 3 rides with the arm (rigid bracket) and the wedge drops 3.4 mm on
average.

## Measured: frozen exact Bench(110,360), the parents' drives worn unchanged (farm job sn_claims1)

The lead's roller row is the reference: **18.67**. Reach 0.725, ib14 0.8937, contact 0.0054. Lost: fold 88 / slide 9 /
contact 2. Held out 23.73.

| cell | mu (PA_kin) | nose | wedge | fit fast | FROZEN | reach | ib14 | contact | lost (fold / slide / parts / contact) | dK_lim | horn PA + friction |
|---|---|---|---|---|---|---|---|---|---|---|---|
| lead | 0 (43) | O3 | - | 13.26 | 18.75 | 0.725 | 0.8929 | 0.0054 | 88 / 9 / 0 / 2 | 52.8 | 39.9 |
| lead | 0.05 (40.1) | O3 | - | 13.29 | **18.77** | 0.725 | 0.8927 | 0.0054 | 88 / 9 / 0 / 2 | 46.5 | 42.8 |
| lead | 0.05, held out | O3 | - | - | 23.73 | 0.683 | 0.8915 | 0.0116 | 260 / 32 / 0 / 10 | 46.5 | 42.8 |
| lead | 0.087 (38.0) | O3 | - | 15.18 | **19.90** | 0.714 | 0.8925 | 0.0054 | 92 / 9 / 0 / 2 | 42.2 | 42.9 |
| kneeless | 0.05 | O3 | flat | 16.80 | 21.18 | 0.725 | 0.8894 | 0.0262 | 86 / 0 / 3 / 10 | 46.8 | 42.5 |
| kneeless | 0.05 | O3 | 25 deg / 120 | 15.66 | **20.12** | 0.725 | 0.9142 | 0.0262 | 86 / 0 / 3 / 10 | 46.8 | 42.5 |
| kneeless | 0.087 | O3 | flat | 18.08 | 21.76 | 0.719 | 0.8894 | 0.0264 | 88 / 0 / 3 / 10 | 42.5 | 43.0 |
| kneeless | 0.087 | O3 | 25 deg / 120 | 16.94 | 20.70 | 0.719 | 0.9142 | 0.0264 | 88 / 0 / 3 / 10 | 42.5 | 43.0 |

- **The control reproduces.** The proposer measured 21.13 flat and 20.12 wedged. Here: 21.18 and 20.12, with hub 3 at
  0.505 -> 0.799 in band (median 13.9 -> 10.8 mm). The wedge's whole gain is the in-band term, and hub 3's crown does
  not move: median 21.9 mm above the skin (min 13.0, max 37.3), flat and wedged alike. The wedge drops 3.4 mm on
  average (7.6 max) for +4.7 g. The alignment auditor rules on this column.
- **The lead's drive on its own:**
  - At mu 0.05 the nose is a Pareto move: +0.10 points (one in-band hundredth) for -2.0 complexity. Held out it is
    identical to the roller (23.73).
  - At mu 0.087, the honest central friction, the lead's drive loses 4 workspace poses to the shorter stroke
    (dK_lim 42.2): +1.23 points.
  - Below mu 0.05 the extra stroke is worth nothing (mu 0: dK_lim 52.8, still 18.75): K's dyad window (a1max) binds
    first.

## The deeper move: re-fit the flank at the honest friction (CMA-ES on the farm, 3 runs, 3603 evaluations)

The objective is the round-9 one, the 2 mm near-touch gap on Bench(60,160) fast. Each run started from the lead's
drive with an O2 nose (nose_r 1.0, 16 per generation, sigma 0.5):

| run | what moves | mu | evals | start (2 mm) | best (2 mm) | best plain | dK_lim | gate (2nd half / last third / top-5, score points) |
|---|---|---|---|---|---|---|---|---|
| A | drive + nose (9) | 0.087 | 993 | 16.79 | **16.47** | 13.00 | 49.8 | 0.00 / 0.00 / 0.00 (passes) |
| B | drive + nose + 11 seats (20) | 0.087 | 1617 | 16.79 | 15.57 | 14.52 | 44.0 | 0.36 / 0.31 / 0.12 (passes) |
| C | drive + nose (9) | 0.05 | 993 | 16.66 | 16.47 | 13.09 | 52.8 | 0.00 / 0.00 / 0.00 (passes) |

A's best: g 2.3934, beta -176.684, r_c 15.3739, lift 0.7882, hl 1.9442, zr 4.0293, s_arm 4.0, r_lobe 8.2661, nose_r
1.1839 (an O2.37 nose: an O2.4 ground 440C pin, or an O2.5 m6 dowel at r 1.25), with the lead's seats.

**The flank re-fit takes back everything friction cost.** At mu 0.087 the horn's kinematic pressure angle peaks at
36.1 deg over the taken stroke, under the 38.0 cap: 41.1 with the friction angle, against 43. Its own range is 49.8
deg, against the lead roller's 46.2. The same flank keeps the following fast numbers, all honest:

| mu | dK_lim | fast plain |
|---|---|---|
| 0 | 60.0 | 12.98 |
| 0.05 | 54.0 | 12.97 |
| 0.12 | 46.2 | 13.00 |
| 0.15 | 43.2 | 14.90 (3 poses lost) |

So the friction risk is retired up to mu 0.12, i.e. greased steel on DLC with margin, and dry 440C on DLC at its
better end. The price is a crank-side pressure angle of 29.5 deg (34.5 with friction; the lead's was 8.2), still far
inside 43.

### Frozen exact Bench(110,360), A's shape worn unchanged at mu 0.087 (the central case)

**18.49 (score 93.28)**, against the lead roller's 18.67 through the same Frozen class. The best fit on the fast bench
was 13.00.

- **Gap terms.** Reach 0.725 (261/360), follow 1.0, ib14 0.8955, ib10 0.5163, contact 0.0054 (2 poses).
- **Lost poses:** fold 88, slide 9, contact 2. These are the lead's exact losses. The contact split is horn / hub K /
  crank, the lead's own pair.
- **Overhead (elevation >= 140):** 8/28 taken, in-band 0.894, lost fold 14, slide 4, contact 2. Same as the lead.
- **Near-touch.** The lowest metal is 0.07 mm, at plane -60, elevation 60, axial 105: the lead's own pose and metal.
  - Counting metal < 1 mm as contact: 20.12 (lead 20.30), 3 poses.
  - Counting metal < 2 mm as contact: 33.02 (lead 33.10), 30 poses.
- **Workspace in-band (unscored):** 0.856 / 0.509 overall, 0.800 at elevation 90-140, 0.940 overhead. The lead,
  same harness: 0.854 / 0.798 / 0.937.
- **Parts in band.** The re-cut arm runs lower: crank 0.797 -> 0.818. Hub 3 0.739 and L2 0.736 are unchanged.
- **Cam check.** Horn PA 36.1 + 5.0 friction; crank PA 29.5 + 5.0. The flank's smallest radius is 1.3 mm, a concave
  pocket around the 1.18 nose. Hub K clearance 1.31; nose-to-hub-K clearance 3.92; contact radius 14.9-19.8 mm.

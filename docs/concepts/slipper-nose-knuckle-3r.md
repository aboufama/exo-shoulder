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

## Red team (my own best configuration)

- **The pose that jams.** The driven side is the horn on the outward stroke and the crank on the return. The horn
  peaks at 36.1 + 5.0 = 41.1 deg at the last taken K step. Stop B sits at dK 49.8, past every taken pose (the dyad
  window binds first). Jamming needs PA + friction angle -> 90. At the 43 rule, the flank keeps all its taken poses
  up to mu 0.12. At mu 0.15 (dry Ti-Ti would be ~0.3-0.4 and galls: never run without the DLC + grease) it loses 3
  fast poses.
- **The point that pinches.** The lowest metal over the taken frozen poses is 0.07 mm at plane -60, elev 60, axial
  105. That is the lead's own pose and part (the nose metal stays >= 7 mm off the skin over every taken pose). 3 poses
  are under 1 mm (gap 20.12), 30 under 2 mm (gap 33.02); the lead's numbers are 20.30 / 33.10. The 2 contact poses
  are the lead's (horn lug and hub K / crank).
- **The optimistic number.**
  1. mu 0.05 is the optimistic friction. The claim uses mu 0.087, and the shape is honest to 0.12.
  2. The flank's smallest radius is 1.3 mm, a concave pocket 0.12 mm larger than the nose radius. It is wire-EDM
     friendly, but nose wear (~14 um over 1e6 cycles) eats a tenth of that clearance. The pocket is where the contact
     is conformal, so the stress there is lowest.
  3. The +0.18 over the lead is all in-band (crank 0.797 -> 0.818). It is below the 1-point rule.
  4. The spec's 22.0 complexity leaves the dowel out; 22.25 counts it.
  5. Workspace in-band at elevation 90-140 is 0.800. The lead is at 0.798 in the same harness, but both sit under
     the 0.874 / 0.841 bar quoted for the lead.
- **The wedge, both columns.** On the kneeless control the planar wedge is worth -1.06 points frozen at mu 0.05 and
  -1.06 at 0.087. The gain is in-band only: hub 3 in band 0.505 -> 0.799 while its crown stays at a median 21.9 mm
  above the skin. That is a share-metric gain of the floating-centre kind, so it is left to the auditor. On the lead
  the wedge cannot exist (0 mm of drop at 2 mm clearance).

## More claim columns (farm job sn_claims2, local held-out of A)

| configuration | frozen exact Bench(110,360) | held out | note |
|---|---|---|---|
| lead roller (reference) | 18.67 | 23.73 | flood full 18.67, knn 20.34 |
| lead drive, O3 nose, mu 0.026 (PA_kin 41.5) | 18.77 | - | dK_lim 49.5 |
| lead drive, O3 nose, mu 0.05 (PA_kin 40) | 18.77 | 23.73 | flood full 18.77 / knn 20.44 (the lead's +0.10 everywhere) |
| lead drive, O2 nose, mu 0.05 | 18.79 | - | dK_lim 48.8 |
| lead drive, O3 nose, mu 0.087 (PA_kin 38) | 19.90 | 25.23 | 4 poses (16 held out) lost to the shorter stroke |
| lead drive, O2 nose, mu 0.087 | 19.09 | 24.83 | the smaller nose alone gets back 0.81 of the 1.23 |
| **A: re-fit flank, O2.37 nose, mu 0.087** | **18.49** | **23.45** | equal reach; +0.0018 in-band; held out 0.28 better than the lead |

The held-out column for A is held-out clips only (never used in a fit): 23.45 (reach 0.683, ib14 0.8943, contact
0.0116; lost fold 260, slide 32, contact 10; overhead 18/71; min metal 0.33 mm). The lead roller scores 23.73 on the
same column.

## Last claim columns (farm job sn_claims3: the same numbers as the local run)

| configuration | frozen exact | held out | flood (full / knn / bench) |
|---|---|---|---|
| A at mu 0.087 (the claim) | **18.49** | 23.45 | 18.49 / 20.16 / 50.11 (lead 18.67 / 20.34 / -) |
| A worn at mu 0.05 | 18.46 | - | - |
| C (drive re-fit at mu 0.05) | 18.55 | - | - |
| B (drive + 11 seats re-fit, mu 0.087) | 19.81 | 24.78 | - |
| A' (CMA A's best PLAIN fast eval, nose_r 1.106, mu 0.087) | 18.18 | not run | - |

- **B confirms round-3 lesson (c).** The seat re-fit wins on the fast bench (2 mm 15.57 vs 16.47) and loses frozen
  (19.81, 6 fold poses more) and held out. The seats stay the lead's.
- **A' is not claimed.** It was worn alongside A before either result was seen, and it scores 18.18. Choosing it now
  would use the frozen bench to select. The claim stays A, the CMA objective's own best. A' is recorded in the row for
  the verifier.

## Verdict

**Screened: a Pareto move of the lead.**

- **The claim.** Delete the drive roller, slide a hardened O2.4 nose on a flank re-fit at the honest friction (mu
  0.087), and the lead's frozen 18.67 becomes **18.49** (held out 23.73 -> 23.45, flood knn 20.34 -> 20.16).
- **What it costs and saves.** Complexity 24.25 -> 22.25, one bought bearing fewer, 0 passive translations, 3 active.
- **What it does not do: move the wall.** Reach is the lead's 261/360 and overhead 8/28. Every lost pose is the lead's
  (fold 88 at K's dyad window, knee slide 9, horn contact 2).
- **The nose with the lead's drive left unchanged** is honest only at mu <= 0.05 (18.77). At mu 0.087 it costs 1.23
  points until the flank is re-fit.
- **The wedge.** It is a kneeless-only, in-band-only lever (-1.06) with an unmoved crown, and it does not exist on the
  lead.
- **Next.** Wear test of the 440C / DLC pair at 5-15 N to pin mu. Then CAD of the re-cut flank: its 1.3 mm concave
  pocket and the O2.4 pin seat in the 3 mm Ti arm tip.

## Verification (independent skeptic, 2026-10-17 ~06:30 UTC)

Harness: `docs/concepts/verify/slipper-nose-knuckle-3r.py`. It loads the claim's model unchanged (SN_CELL=lead) and
reuses the lead's verifier (`docs/concepts/verify/roller-longdyad-knuckle-3r.py`, on the round's roller-flank verifier),
retargeted at the claim's model class, clamp, params, best config and nose radius. The parent harness hard-codes the
roller's 3 mm in its nose-vs-lug check, so the retarget sets it to nose_r. It adds four checks for the sliding nose:

- **N1, pressure angle with friction.** At every taken pose, kinematic PA + atan(mu) <= 43 (the claim's rule) and
  <= 45 (the judge's gate).
- **N2, conjugate validity.** Every flank contact point over the used stroke must stay >= nose_r - 0.02 mm from the
  nose centre at every other K step (0.05 deg grid). Otherwise the flank has an undercut and the scored flank does not
  exist there. The parent's lug sampling deletes every sample within ROLL_R + 0.3 of the path, which would hide one.
- **N3, relative pole.** The nose centre's sliding speed per unit of K, and the flank's smallest radius.
- **N4, stock nose and friction.** The shape worn again with stock ISO 8734 radii (O2.5, O2) and at mu 0.12. The flank
  is re-cut for each nose by the claim's own synthesis; the drive parameters are unchanged.
- `--edge`: an envelope correction with no head (a pressed dowel has none). It re-adds the lug's flank-edge strip at
  nose_r + 0.1 from the path.

Protocol: fit on Bench(60,160) fast, freeze the shape, then wear it on Bench(110,360) exact (CB_EXACT=1, farm batch,
6 jobs, $0.06) and on the held-out set. Outputs are in `docs/concepts/verify/slipper-nose-knuckle-3r_v_*.json`.

| frozen exact | plain | 1 mm | 2 mm | reach | follow | ib14 | ib10 | contact | min metal |
|---|---|---|---|---|---|---|---|---|---|
| Bench(110,360), the claim (A, nose_r 1.1839, mu 0.087) | **18.49** | 20.12 | 33.02 | 0.725 | 1.0 | 0.8955 | 0.5163 | 0.0054 | 0.07 mm |
| Bench(110,360), envelope-corrected (lug flank-edge strip, no head) | 18.44 | 20.07 | 33.02 | 0.725 | 1.0 | 0.8960 | 0.5175 | 0.0054 | 0.07 mm |
| Bench(110,360), stock O2.5 dowel (nose_r 1.25) | 18.49 | 20.12 | 33.02 | 0.725 | 1.0 | 0.8955 | 0.5162 | 0.0054 | 0.07 mm |
| Bench(110,360), stock O2 dowel (nose_r 1.0) | 18.49 | 20.12 | 33.02 | 0.725 | 1.0 | 0.8955 | 0.5160 | 0.0054 | 0.07 mm |
| Bench(110,360), mu 0.12 (PA_kin cap 36.16) | 18.49 | 20.12 | 33.02 | 0.725 | 1.0 | 0.8955 | 0.5163 | 0.0054 | 0.07 mm |
| held out | 23.45 | 26.54 | 36.95 | 0.683 | 1.0 | 0.8943 | 0.5148 | 0.0116 | 0.33 mm |
| champion spherical 3R, same bench (risley-turret verifier) | 75.94 | | | | | | | | |

**Checks on every taken pose: 0 of 371 fail on the bench, 0 of 852 held out, in every column.**

- **Cam closure in the world:** 0.0 mm.
- **Nose vs lug:** the nose centre stays 2.70-3.28 mm from the lug's mid-shell metal, against the nose's 1.18 mm radius.
- **K sense:** always the drive's (0 wrong-sense poses).
- **Pressure angles:**
  - Kinematic: crank 29.5, horn 35.8 (36.1 held out), under the claim's friction cap of 38.03.
  - With friction (mu 0.087): horn 40.8 (41.1 held out), crank 34.5. That passes both 43 and 45.
  - At mu 0.12: horn 42.6 with friction, still <= 43.
  - The real lobe pressure angle is 23.5.
- **Stroke:** dK taken 45.6 deg (46.3 held out), inside dK_lim 49.75.
  - dK_lim is 49.5 with the O2.5 nose, 50.5 with O2, and 46.25 at mu 0.12.
  - The drive is not idle.
- **Fold margin in th:** minimum 5.181 on the bench and 5.006 held out; no pose is under 5.
- **Continuity flood:** the full grid drops 0 poses (18.49); knn 20.16 (6 dropped); bench-only 50.11. These match the
  claim.
- **N2, conjugate validity:** 0 undercut points over 913 steps (0.0 mm). The flank exists everywhere the nose uses it.
- **N3, relative pole:**
  - The nose sits 0.66 mm/rad from the relative pole at rest (8.5 at the end of the stroke).
  - The flank there is a conformal pocket: radius 1.285 at K 0.5 deg, against nose 1.184 (0.10 mm clearance). With the
    O2.5 dowel the pocket is 1.351.
  - This is wire-EDM-able. Conformal contact keeps the stress lowest exactly there. Normals and pressure angles are well
    conditioned, because both stay under the cap.

**Lost poses:** 99 of 360 (fold 88, slide 9, contact 2), the lead's own. Overhead: 8 of 28 (fold 14, slide 4,
contact 2).

**Parts in band:** hub3 0.739, L2 0.736, crank 0.818, nose 0.938; the rest >= 0.93. Mechanism: 3 active, 0 passive
translations, no gears / pulleys / cables.

**Where the +0.18 over the lead comes from (attribution, not a refutation).** The score does not move with the nose:

- O2, O2.37 and O2.5 all give 18.49, and so does mu 0.087 -> 0.12. The drive stroke never binds, because K's dyad
  window caps first: taken 45.6 against dK_lim 46.25-50.5.
- The gain is the re-fit arm geometry (beta, r_c, lift): the crank's in-band rises 0.797 -> 0.818.
- The lead's own MR63ZZ roller (O6 plus the O4.5 head, PA 43, mu 0) worn on A's re-fit arm scores 12.88 plain on the
  fast bench, against the nose's 13.00. Its dK_lim is 52.2, the crank 0.819 in band.
- Frozen exact Bench(110,360), the same protocol through the lead model's own code (farm, not re-run through this
  harness): **18.36**. Reach 0.725, ib14 0.8968, contact 0.0054. Lost: fold 88, slide 9, contact 2. 1 mm 19.99, 2 mm
  34.66 (the O4.5 head).

So against a roller given the same arm re-fit, the nose costs 0.13 plain (18.49 vs 18.36) and 0.13 at 1 mm, and gains
1.64 at 2 mm (no head under the tip). It saves one bearing and 2.0 complexity. The claim's "+0.18 over the lead"
compares with the lead's un-refit arm, so it is not the nose's gain. The claim itself files the move as a
simplification rather than a points lead, which is the correct reading. File it as a simplification at -0.13 plain:
below the 1-point rule either way.

**Verdict: VERIFIED, not refuted.**

- **The numbers:** 18.49 frozen exact Bench(110,360), score 93.28, against the champion's 75.94 on the same bench.
- **Hard rules:** none broken.
- **Recommendation:** build it with the stock ISO 8734 O2.5 m6 dowel (nose_r 1.25, measured 18.49) instead of the
  O2.37 ground pin.

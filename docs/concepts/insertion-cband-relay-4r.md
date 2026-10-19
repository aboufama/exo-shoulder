# insertion-cband-relay-4r: short-strap C-band relay at the deltoid insertion (round 401 K1, judge pick 2)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the band as a bearing race, not as a cuff. The race must be a surface of revolution about the relay axis (a
     cone or a curved profile is fine, since any surface of revolution still rotates), while the underside follows the
     arm in 2D. So the band's radial thickness varies with azimuth, and the carriage only ever sees the race. That
     splits two jobs: the skin fit (underside, per azimuth and per axial station) and the guide (race top, one profile
     R(w)). The spec's single-station band merges them.
   - Price the axis tilt as a metal variable. The 8.75-deg tilt is chosen to put the band centre 15 mm posterior. The
     near-long axis gives +7 static ws poses (319 vs 312, measured here with the judge's kinematics), so the tilt has
     to buy its 7 poses back in band and race clearance.
   - Read the wheels as skin-facing metal. The V-wheel blocks stand outboard of the 22 mm band at the band edges. At
     the insertion the proximal edge sits on the rising deltoid, and the wheel blocks are the lowest metal there.
2. **The rawest material.**
   - The posed skin itself, through B.dist / K.requirement: the exact signed distance of every metal sample in every
     pose. The band's underside is fitted by marching rays from the relay axis at every (azimuth, axial) sample over
     the fit poses, not taken from band.py's one-station digest.
   - The relayed humerus frames: AR.solve_phi least-phi on the whole archive, envsel included.
   - The lead's own fitted metal: the conecut CC model's rigid / link samples, frozen.
   - Not used: the Bench(60,160) proxies of the ideation (no link metal, no in-band term).
3. **The specific methods and tools.**
   - kfree-armarc-relay-4r.py lead_eval, modified only in its bench, with these settings: K welded (|dK| <= 0.1 deg
     gate), drive metal stripped, and knee-side samples dropped (round-401 lens A's readings).
   - The frozen protocol: fit on Bench(60,160) fast, wear on envsel exact (selection), then Bench(110,360) exact (claim).
   - K.requirement for the 2D-contoured band underside.
   - AR.flood_relay for the continuity flood on the 1432-pose envelope grid.
   - The th fold margin in the one metric (angle(J1, J3) against the welded window).
4. **What, other than me, shows the number is right.**
   - The bench (tools/concept_bench.py, exact path).
   - The judge's pre-registered gates: ideal > 14.0 kills; hardware > 17.0 kills.
   - The round's adversarial verifier and the alignment auditor.
   - The red-team pose list below: the deltoid-insertion bulge under the band's proximal edge at abduction 60-120, the
     band's anterior end against the chest at plane 120-150, hub 3 in the deltoid bunching, and the wheel blocks' side
     clearance to the strap.

## Step 1: the ideal bound on the lead-quality chain (the judge's pre-registered gate: kill if > 14.0)

**Model.** docs/concepts/models/insertion-cband-relay-4r.py, mode `ideal`, built on kfree-armarc-relay-4r.py
lead_eval. Only the bench changes, and these readings are added:
- **Chain.** conecut-knee-knuckle-3r's own fitted metal on the frozen protocol: fit on Bench(60,160) fast, worn exact.
- **K welded.** The |dK| <= 0.1 deg gate holds K at stop A; the drive metal is stripped.
- **J3 re-aim.** wdir(95, -8.2) with b3 0, asserted in the fitted model.
- **a2.** Set by psi2: J2's rest axis is turned about J1 and a1 stays 37.552.
- **No J4 metal.**
- **Knee-less reading.** The E strap, O12 boss, pad and knee link are dropped, as in round-401 lens A.

**Relay.** Least phi in [0, PHI] about raxis(8.75, -90), sgn +1.
- That axis and sign reproduce the judge's kinematic count: 312 / 360 static ws, 22 / 28 overhead at a2 67 (scratch
  icb/axsign.py). The opposite sign gives 285 / 18.
- The near-long axis (tilt 0) gives 319 / 22: the posterior tilt costs 7 kinematic poses.
- The lead's gates (J3 own-angle stops, R_tol, the 0.5 deg closure) leave 291 / 360 closing at PHI 45.

**th fold margin.** Measured in the one metric over every taken pose. The minimum is 5.00 deg in every cell; no taken
pose sits below 5.

| k | cell | bench | gap | reach | follow | ib14 | contact (n, depth sum / max mm) | overhead | near-1 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | psi2 -45 (a2 67.34), PHI 45, lead J3 stops | envsel exact | **19.70** | 0.767 | 0.936 | 0.921 | 0.050 (20, 102.9 / 13.2) | 5/26 | 24.46 |
| 1 | psi2 -36.5 (a2 62.0), PHI 45 | envsel | 24.42 | 0.706 | 0.945 | 0.922 | 0.045 (17, 50.3 / 7.0) | 3/26 | 34.67 |
| 2 | psi2 -45, PHI 50, J3 stops off | envsel | 23.14 | 0.767 | 0.936 | 0.919 | 0.085 (35, 168.3 / 13.6) | 2/26 | 26.78 |
| 3 | psi2 -45, PHI 45, J2 dowel q2 <= 100 | envsel | 19.70 | (q2 <= 100 never binds: identical to k 0) | | | | | |
| 4 | CONTROL: lead J3 (66.87 / -10.66, b3 0), psi2 0 (a2 66.48), PHI 45 | envsel | 36.15 | 0.683 | 0.982 | 0.833 | 0.078 (30, 160.0) | 2/26 | 38.84 |
| 5 | J3 wdir(90, -8.2), psi2 -37.5 (a2 67.16), PHI 45 | envsel | 20.13 | 0.767 | 0.936 | 0.896 | 0.050 (20, 90.7) | 2/26 | 22.78 |

For reference, Bench(60,160) fast for cell 0 reads 9.62 (reach 0.844, follow 0.95). That bench is the metal's own fit
set, so the reading is in-sample, and this is exactly the trap the judge named: the proxies at reach 0.838 were all on
that bench. On envsel, a fresh draw, the same chain loses 10 points.

**Where cell 0 loses (envsel, 360 ws).**
- 59 fold: no welded solution within PHI 45.
- 15 contact, all burials. 11 are hub 2 under the acromion at abduction 90-126 in planes -21..+29, down to 13.2 mm
  deep, for example ws (27, 126, 2) at -13.19 mm and (29, 123, -14) at -10.77 mm. The overhead fit clip (plane 30,
  elevation 138-150, axial -60) buries hub 2 4.0-9.4 mm on 7 frames.
- 10 J3 stop.
- 2 parts.

Half of the 20 contacts are un-relayed, phi 0. The psi2 -45 re-placement that buys a2 67 for the re-aimed J3 moves hub
2 45 deg round J1, onto skin that the lead's fit never saw.

**Lever reading.**
- **PHI 50 with the stops off.** It adds 22 kinematic poses (313) and loses them all again to contacts (35: hub 2 12,
  hub K 7, link 2 9), so it scores worse.
- **a2 62.** Worse: the stretched window closes earlier.
- **J2 dowel q2 <= 100.** It never binds, so it does not steer the burials.
- **J3 at wdir(90, -8.2).** Level on reach. It trades contacts for in-band.
- **Without the re-aim.** The relay on this axis is far worse (36.15 against 19.70), so the re-aim is what makes the
  cell work at all.

**Gate.** The best ideal on the selection bench is 19.70. Reach and follow alone already cost 13.3 + 1.4 = 14.7 points,
and J4 metal can only add contact and jams, never reach. **The pre-registered kill (> 14.0) fires.**

Convergence over the 6 ideal cells:
- The best gained 0 score points over the second half and 0 over the last third.
- The top 5 lie within 1.72 score points (19.70-24.42 gap).

The gate passes formally, but 6 cells are a thin sweep: the farm is closed and only 2 local processes are allowed.

## Step 1 on the claim bench: frozen exact Bench(110,360), ideal, cell 0

**Reading: 16.86 (score 93.87).**
- reach 0.792 (285 / 360 ws taken), follow 0.936, ib14 0.921, ib10 0.507.
- contact 0.047: 19 poses, depth sum 101.9 mm, max 14.4 mm, against the lead's 4 / 20.24 mm (T5: x5.0).
- Near-touch: 20.00 at 1 mm, 35.42 at 2 mm.
- Overhead 7 / 28.
- min th margin 5.001.
- Kinematics: 300 / 360 close, 67 relayed, phi max 44.9.
- Losses (360 ws): fold 54, contact 12, J3 stop 6, parts 3.
- Contacts by part: hub 2 6, hub K 2, link 2 2, contact-list members 9.
- Deepest burials: ws (30, 135, 0) at -14.43 mm, (45, 150, -45) at -7.98, (0, 105, 15) at -6.44, and the overhead fit clip
  (30, 138-150, -60) at -4.0 to -9.4.

**The kill fires on the claim bench too** (16.86 > 14.0). If hub K's O20 stack is also deleted, the reading is still
16.86: link 1's bar over the stack is unsampled, so that reading is optimistic, and in-band 0.916 changes nothing.

## Step 2 (diagnostic, not converged): the J4 hardware at the insertion, sampled across the full width

The J4 metal comes from the raw posed skin, fitted on Bench(60,160) and frozen. model `j4=1`; geometry in `j4_geometry`.

**Band.** Saddle 26 mm wide (band 22), psi -28..+42 about the relay axis, the station 98.65 mm down the axis.
- Underside 2D-contoured: one ray from the axis per 2 mm in azimuth and in axial w, each at the q 1 skin requirement
  with 2 mm clearance (a 2 mm liner) over the fit poses.
- Rays that meet the torso or forearm first are excluded from the fit: requirement > median + 15 mm, which happens on
  across-body / |axial| 135-165 poses, where the requirement reaches 110-170 mm. Those poses then read as band contacts.
- Race top: a surface of revolution about the axis, R(w) = max over azimuth of the underside + 3.0 mm. Measured R(w) is
  76 / 72 / 76 mm at w -11 / 0 / +11, and the band's radial thickness runs 3.0-15.0 mm.

**Carriage.** 20 deg x 34 mm at R + 0.5, plate 2.5. Four wheel blocks of 8 x 8 mm at psi0 +-7 outboard of the band
edges, standing 3 mm below the race top (outer walls sampled).

**Strap.** 12 x 3, 94.7 mm, from hub 3's fitted centre (67.6 mm from GH) to the carriage top. Underside at the q 1 GH-ray
requirement in the member-3 frame, with 10 mm ramps into the end heights.

**Part check.** Strap, carriage and wheels against hub 1, hub 2, hub K, link 1 and link 2: >= 1 mm, or the pose is
lost as a jam.

| bench | gap | reach | follow | ib14 | contact (n) | overhead | carriage ib14 (p5 / p50 / p95 mm) | band ib14 | strap contact poses |
|---|---|---|---|---|---|---|---|---|---|
| envsel exact | 79.79 | 0.644 | 0.755 | 0.760 | 0.207 (82) | 0/26 | 0.317 (10.5 / 16.0 / 22.0) | 0.914 | 61 (41 ws) |
| Bench(110,360) exact frozen | **74.53** | 0.681 | 0.755 | 0.760 | 0.190 (77) | 0/28 | 0.340 (10.1 / 15.7 / 21.9) | 0.918 | 54 (34 ws) |

On Bench(110,360) the contacts break down as follows:
- **Strap.** 54 poses, shallow (max 2.6 mm): deltoid bunching that the q 1 fit with the 15 mm outlier cut does not
  cover.
- **Band.** 10 ws poses, up to 12 mm: the torso-side poses.
- **Wheels / carriage.** 1 pose each.
- **Jams.** 2 ws.

This is one unswept hardware configuration, so it is not the design's floor; the kill is already decided at step 1. A second read with the strap fitted without the 15 mm outlier cut (out_strap 80) is identical (74.53). The strap's 54 shallow contacts are therefore fit-set generalisation: a q 1 fit on Bench(60,160) does not cover Bench(110,360)'s deltoid bunching.
What it measures:

- **The carriage cannot sit in band at the insertion.** The race must clear the worst skin at every azimuth it covers,
  and the arm's skin at s 0.30 swings 6-10 mm (p5 to p95, per sample) and up to 12 mm (to max) against the humerus
  frame. So a rigid carriage floats 10-22 mm above the skin: in-band 0.34, against the proposer's single-station 0.958.
- **The band underside is fine where only the arm is under it** (in-band 0.92). It meets the torso at deep across-body
  and axial rotation.

## Red team (the pose that jams, the point that pinches, the optimistic number)

- **The optimistic numbers.**
  - Bench(60,160) fast is the fit set and reads 9.62. Against it, frozen Bench(110,360) reads 16.86 and envsel 19.70.
  - The proposer's Bench(60,160) proxy (reach 0.838) carried no link metal.
  - The single-station carriage in-band of 0.958 reads 0.34 with the race honestly made a surface of revolution.
- **The points that pinch.**
  - Hub 2 under the acromion at abduction 105-150, planes 0-45: 14.4 mm deep at (30, 135, 0). This is the price of the
    psi2 -45 J2 re-placement that the J3 re-aim needs for a2 67.
  - The strap over the deltoid bunching: 54 poses, <= 2.6 mm.
  - The band against the chest / torso at across-body with extreme axial rotation: 10 poses, <= 12 mm.
- **The poses that jam.** 2 ws poses put J4 metal within 1 mm of chain metal. Parts (chain-internal): 3.
- **Shoulder slip.** The standing price, not re-measured: misfit p95 4.83 / max 5.14 mm at a 3 mm GH offset, about
  6.4 / 6.9 mm at R10 4 mm, 13-31 N at 2-4.5 N/mm against R17's 5 N. This build assumes a 2 mm liner under the band.
- **Not run (the row is killed at step 1).** The continuity flood: connected <= static, so it can only raise the gap.
  The held-out bench: untouched, no claim. The per-pose zero-return margin: the 2 N strip on R ~0.075 m gives about
  0.15 N m against the judge's 0.04-0.08 N m gravity plus 0.016 N m for the rollers, not computed per pose.

## Limiter (measured)

**Reach**, on the lead-quality chain with no J4 metal. Of 360 ws on Bench(110,360) exact frozen, 75 are lost: fold 54,
hub-2 burials 12, J3 stop 6, parts 3. The levers on file do not move it:
- PHI 50 trades 22 kinematic poses for 15 more contacts.
- The q2 dowel does not bind.
- a2 62 is worse.
- J3 at wdir(90, -8.2) is level.

Then **the hardware**: strap contacts, a carriage out of band (0.34) and band-torso contacts.

## New knowledge

1. **The skin at the insertion moves against the bone.** Rays from a GH-through axis at s 0.30 meet the arm's skin at a
   radius of p50 ~60-64 mm from the axis (2 mm clearance included). Per sample the radius spreads 6-10 mm (p5 to p95)
   and reaches +5 to +12 mm over p95 at the max, across Bench(60,160) poses, in the humerus frame. Any arm-fixed race,
   being a surface of revolution about its axis, inherits the per-azimuth maximum, and its rigid carriage floats 10-22
   mm. Single-station medians over-read the carriage in-band by ~0.6.
2. **The torso blocks the posterior-lateral arm.** At across-body poses with extreme axial rotation (plane 105-120,
   elevation 45, axial -135..-165, and plane -75..-90 with axial 135-165) the band's psi -30..-10 and +30..+60 sectors
   face the torso (ray requirement 110-170 mm). An arm-fixed band there must give up those poses.
3. **The re-aim is real but its J2 re-placement buries hub 2.** With J3 at wdir(95, -8.2) the relay at this axis reads
   19.70 envsel, against 36.15 with the lead's J3. But the psi2 -45 re-placement that makes a2 67 buries hub 2 under the
   acromion at abduction 105-150 (6-11 contacts, up to 14.4 mm deep). Hub 2's metal is already fitted to the re-placed
   seat on Bench(60,160), so it buries on poses outside its fit set: the seat itself sits under the acromion's swing.
   The next levers are a J1 / a1 change that reaches a2 67 without turning J2 45 deg round J1, or fitting the metal on
   the envelope sample (env) instead of Bench(60,160).
4. **Lead-quality ideal bounds must be read off the fit bench.** The in-sample Bench(60,160) reads 7-10 points better
   than envsel or frozen Bench(110,360).

## Audit (dead-row auditor, 2026-10-19 ~03:45 UTC)

**Ruling: the death stands, but for a different reason than the row gave.** The step-1 reading was over-strict. With the
welded K modelled as the one bar link 1 is, the ideal bound reads **12.74 on the claim bench** (frozen exact
Bench(110,360)), which passes the 14.0 kill. It still reads **16.59 on envsel**, the bench the spec names first, so the
pre-registered kill still fires there. The step-2 hardware reading (74.53, one configuration that was never swept) is
untouched by the correction and is still 57 points past the 17.0 hardware kill. A green claim-bench reading on one
bench is not a refutation. Nothing here is a claim, and held-out was not used.

### What was wrong: the welded K kept the walls and crowns of an O20 stack that does not exist

The row's mechanism record says "K welded (link 1 one bar)": there is no hub K. The ideal reading kept that stack anyway:
- The `kneeless` reading kept hub K's rigid underside, plus every contact-only entry of member 1 that hub K owns
  (14 entries: wall rings up the stack and the crown disc).
- The `kneeless_noK` reading claimed to delete the stack. It dropped only the scored underside samples; the
  contact-only re-read still filtered by member (`m not in (5, 6)`), so hub K's walls and crowns stayed in.
  That is why noK equalled the full reading (16.86) **by construction**, not by measurement.
- The row's "contact-list members 9" were all hub K (attributed by `contact_owner`: each contact entry goes to the
  same-member part with the least median nearest-neighbour distance, then the deepest entry is picked per pose). The
  B110 contact parts read `contact-only:hubK 9, hub2 6, hubK 2, L2 2`.
- Seven of those nine are the overhead fit clip (30, 138-150, -60) at -4.0 to -9.4 mm. Those are the clip's 7
  unfollowed frames: follow 0.9364 is 103/110.

**A smaller leak with no effect here.** The members-5/6 filter also keeps the knee-side contact entries on member 3: the
E-strap top (164 points) and the two O12 boss rings. Dropping them (`kc 1`) changes nothing (16.86): none of them is in
contact on Bench(110,360).

**The corrected reading** (`kc 2`, in the model file: `ideal '{"psi2": -45, "kc": 2}' b110`) does three things:
- deletes hub K's walls and crowns;
- keeps its 20 mm skin-facing underside disc as scored metal (wider than the 12 mm bar it stands for);
- adds a 3 mm top face and rim as contact-only metal, so the joint between link 1a and link 1b is still sampled.

| reading (cell 0: psi2 -45, a2 67.34, PHI 45, raxis(8.75, -90), J3 wdir(95, -8.2)) | bench | gap | reach | follow | ib14 | contact (n, depth sum mm) | overhead | near-1 / near-2 |
|---|---|---|---|---|---|---|---|---|
| row (kneeless, hub K walls / crowns kept) | Bench(110,360) exact frozen | 16.86 | 0.7917 | 0.9364 | 0.9209 | 0.0467 (19, 101.9) | 7/28 | 20.00 / 35.42 |
| audit kc 1 (knee-side member-3 entries dropped as well) | same | 16.86 | 0.7917 | 0.9364 | 0.9209 | 0.0467 (19, 101.9) | 7/28 | 20.00 / 35.42 |
| **audit kc 2 (K welded as one bar)** | same | **12.74** | 0.7972 | 1.000 | 0.9206 | 0.0246 (10, 30.9) | 8/28 | 17.80 / 34.90 |
| row | envsel exact | 19.70 | 0.7667 | 0.9364 | 0.9209 | 0.0501 (20, 102.9) | 5/26 | 24.46 / 39.98 |
| **audit kc 2** | envsel exact | **16.59** | 0.7667 | 1.000 | 0.9206 | 0.0326 (13, 39.6) | 5/26 | 23.30 / 39.98 |

- min th margin: 5.001 (0 taken poses below 5).
- What is left on Bench(110,360) after the correction is real:
  - hub 2 under the acromion (6 poses, to -14.43 mm at (30, 135, 0)), the price of the psi2 -45 J2 re-placement;
  - link 2 (2 poses);
  - hub K's underside (2 poses);
  - 54 fold and 6 J3-stop poses.
- On envsel, 11 of the 13 contacts are hub 2: the burial is the limiter there.

### Levers tried (none reverses the ruling)

1. **Fit the chain metal on the relayed poses** (`fitrel 1`). The default fits on the un-relayed Bench(60,160) poses
   only; this fits on the fit bench as the relayed design takes it. Result: 16.86 B110 and 19.70 envsel, identical gaps
   (ib14 0.9166). Only 5 of the 19 B110 contacts are relayed, so the fit set is not the cause.
2. **The mirror J2 seat** (the other psi2 root for a2 67.34: psi2 +122.55, J2 at az ~132, el ~36.5, the dyad's other
   branch), with kc 2 on envsel: **174.99**. The conecut metal there collides with itself (181 ws parts, hub 2 floating
   at a median 32.5 mm), so that region is dead for this chain's metal, not missed.

### The gate, recomputed from the sweep

Ideal envsel cells in order: 19.70, 24.42, 23.14, 19.70, 36.15, 20.13.
- Gain: 0 score points over the second half and 0 over the last third.
- Top 5: within 1.72 score points.

The gate passes formally, but k 3 duplicates k 0 (the q2 dowel never binds), so it is 5 distinct cells and no search.
The hardware has ONE configuration, so the step-2 death is not gate-converged. The binding hardware costs are measured
geometry, not tuning:
- the carriage floats 10-22 mm (in band 0.34), because a race of revolution clears the per-azimuth maximum of skin that
  swings 6-12 mm against the bone;
- strap contacts on 54 poses;
- band against the torso on 10 poses.

The sibling distal-cband-sq95-relay-4r (s 0.72, swept) died at the same hardware kill: best 35.48, ideal 13.56.

### Consequences beyond this row (for the judge and the alignment auditor)

- **Every knee-less row whose ideal is read through this file's `readings`, or a copy of it, should be re-read.**
  - The "noK" reading never deleted hub K.
  - The "kneeless" reading keeps a hub K stack that a welded-K design does not have: up to 9 contact poses, the
    follow term of an overhead clip, and ~4 gap points here.
  - The judge's 14.0 bars, read through this reading, were all over-strict by that much.
- **The correction can also cut the other way:** it deletes metal. A row that claims a gain from `kc 2` must show its
  link 1 really is one bar at a buildable height, in its CAD and its viz.

### Measured reason, in one line

Corrected for the phantom hub K stack, the ideal bound passes on the claim bench (12.74 < 14.0) but not on envsel
(16.59 > 14.0: 11 hub-2 burials of the psi2 -45 J2 re-placement under the acromion). The J4 hardware still reads 74.53
(carriage in band 0.34, 54 strap contacts), so the row stays dead. The next lever, if anyone takes it:
- an axis-centre sweep that makes the race concentric with the arm's cross-section at s 0.30;
- with a J1 / a1 change that reaches a2 67 without turning J2 45 deg round J1.

Audit files:
- docs/concepts/models/insertion-cband-relay-4r.py (`contact_owner`, `kc 1 / 2`, `fitrel`; the defaults are unchanged)
- scratch icb_audit/hubk_levels.py (the height of each hub-K contact entry above its underside, at every hub-K
  contact pose)

# minarc pick1 red team: contact attribution, the spring at 56.6 deg, the forced swing and the feel (2026-10-16)

Independent red team of the confirmed final polish pick1 (envp-F7-g35-6) against BDp, on the open items of
`docs/research/minarc_final_polish.md` section 5. Both configs are priced like the judge (`tools/env_polish.priced()`:
J2 stops built +0.5 read at CB_FOLD_MARGIN 5.5, K stop B at the 5-deg rule cut) and worn through the judge's harness
`docs/concepts/verify/minarc-bdp-remeasure.py`, imported unchanged.

* Harness: `docs/concepts/verify/minarc-pick1-redteam.py` (modes `attr`, `verify`, `mech`; the `LIFT` and `STOPB_DK`
  switches price the CAD fixes).
* Outputs: `docs/research/minarc_pick1_redteam/` (`attr_*` per-pose files, `mech.json`, farm job files and logs).
* Every baseline reproduces the verified numbers to the digit: pick1 env fit -> held out 21.31, fit Bench(60,160) ->
  held out 22.69, fit Bench(60,160) -> Bench(110,360) 18.40; BDp 23.68 / 24.18.

## 1. Contact attribution (held out, 1154 poses)

Per contact pose: the signed skin distance of every part (hub 1 / K / 2 / 3 underside, wall, crown, K's cap; links 1a,
1b, 2 underside and top; E strap, boss, pad, knee link), the body region under the deepest point, the K state, and
the geodesic distance (thorax-humerus) to the nearest frame of any daily clip (fit clips plus the held-out Wave and
Walking).

**Totals.** pick1 28 contact poses (env fit) / 35 (fit 60); BDp 9 / 13. Every one is a workspace-envelope pose; no clip
frame touches. The nearest daily-clip frame is 11.2 deg away (env fit), median 29 deg. With the fit-60 shape one
contact sits 8.4 deg from a "Comb hair" frame: link 2 at -0.02 mm (plane 75, elevation 150, axial -75), where BDp
keeps 1.89 mm.

**Five clusters (env fit; fit 60 in brackets):**

| cluster | pick1 poses | deepest | part (deepest) | body region | K state | BDp on the same poses | fix |
|---|---|---|---|---|---|---|---|
| A. overhead, elevation 150-165, plane 15-60 | 6 (6) | **-14.6 mm** | hub K wall / cap | upper arm (deltoid) | A, K closed | 3 contact (-5.5 to -7.3), 3 not closed (fold) | structural |
| B. overhead across the body, elevation 135-165, plane 60-135, axial -60..-105 | 9 (14) | -3.6 mm (-5.0) | link 2 underside, hub 2 wall, link 1b | back (scapula), acromion | stretched (1 in A), dK 0-49 | 7 not closed, 1 contact, 1 taken (fit 60: 6 taken) | a lift, priced below: does not pay |
| C. low across the body, elevation 15-30, plane 105-150, axial -150..-180 | 7 (7) | **-10.0 mm** | knee link wall, pad wall | side of the chest / axilla, back | stretched, dK 41-54 | 6 not closed (fold), 1 taken | structural |
| D. behind the back, plane -90..-15, elevation 60-75, axial 105-120 | 5 (7) | -6.5 mm | link 2 underside | shoulder cap | stretched, dK 9-51 | 3 not closed, 2 contact | shared with BDp |
| E. plane 15, elevation 105, axial 15 | 1 (1) | -0.5 mm | hub 2 wall | upper arm | A | parts clash | - |

**Where the extra contact comes from.** Of pick1's 28 contact poses, 19 are poses BDp cannot close at all (13 at its
fold, 6 at the knee slide). 6 are contacts for BDp too, 1 is a BDp part clash, 2 BDp takes clean. 20 of the 28 sit
in the stretched state (K open, dK 9-54 deg). The extra contact is the extra reach: the poses K's longer opening newly
closes are the poses where metal enters the body.

* **Cluster A (hub K into the deltoid).** At elevation 150-165 the raised upper arm comes up against the SIDE wall of
  hub K's 18.25 mm stack (O20 + 6 mm cap). Lifting hub K 7 mm along its axis moves the deepest pose from -14.58 to
  -14.23 mm only: the wall is lateral to the deltoid, not above it. The two deepest (-14.6 / -13.0) are new closures
  (BDp: fold). Structural for hub K's seat on link 1 (bk1 33.8 vs 30.2) and the O20 rule.
* **Cluster C (cuff into the chest wall).** Arm across the body at elevation 15-30 with extreme internal rotation: the
  arm-mounted knee link and pad lie between the upper arm and the torso. These are arm-fixed parts, so no hub level
  moves them. Only removing the poses (stop B earlier, priced below) or re-seating the cuff (a new polish) does.
* **Clusters B and D (link 2 / hub 2 into the scapula and the shoulder cap).** Shallow (-0.1 to -3.6 mm on B), the
  fit-issue kind. A 4 mm lift of link 2 + hub 2 clears B (only -0.17 mm left) and halves the count (28 -> 15), but
  see the price.

**Near-touch.** pick1 has fewer taken poses under 1 mm than BDp (8 vs 20; hub 2's overhead pinch 4 vs 14). Contact +
near-touch together: pick1 36, BDp 29 held-out poses.

### Pricing the fixes (LIFT = mm added to the fitted level before the shape is frozen; pick1, priced stops)

Priced with `attr` (fit -> frozen -> worn exact, the judge's checks). It skips the continuity flood fill, which drops
0 poses for pick1 on every protocol (verifier, section 5 of the polish note); the unfixed rows reproduce the verified
numbers to the digit.

| fix | env fit -> held out (gap / in-band14 / contact poses) | fit 60 -> Bench(110,360) | fit 60 -> held out |
|---|---|---|---|
| none (pick1) | **21.31** / 0.889 / 28 | **18.40** / 0.894 / 11 | **22.69** / 0.892 / 35 |
| hub K +7 | 29.51 / 0.809 / 29 | 26.83 / 0.815 / 12 | - |
| link 2 + hub 2 +4 | 32.77 / 0.747 / 15 | - | - |
| hub K +7, link 2 + hub 2 +4 | 40.97 / 0.667 / 16 | 34.47 / 0.701 / 5 | 38.30 / 0.701 / 19 |
| hub K +3, link 2 + hub 2 +2 (the best lift) | 27.47 / 0.813 / 21 | 22.52 / 0.837 / 8 | 26.16 / 0.836 / 25 |
| BDp (reference) | 23.68 / 0.891 / 9 | 19.54 / 0.893 / 4 | 24.18 / 0.890 / 13 |

**K stop B moved earlier** (`STOPB_DK`: a1max set so stop B engages at that opening; the fit is redone, so the
levels can drop). It removes the stretched-state poses past the cut, which is where cluster C lives:

| stop B at dK | env fit -> held out (gap / in-band14 / in-band 2-10 / contact poses) | fit 60 -> Bench(110,360) (gap / contact poses) |
|---|---|---|
| 56.65 (pick1 as priced) | **21.31** / 0.889 / 0.497 / 28 | **18.40** / 11 |
| 50 | 22.45 / 0.887 / 0.509 / 24 | 18.98 / 11 |
| 45 | 22.76 / 0.887 / 0.521 / 22 | 19.60 / 8 |
| 40 | 23.34 / 0.888 / 0.525 / 18 (no knee / pad contact left) | 18.60 / 5 |
| BDp (34.47) | 23.68 / 0.891 / 0.574 / 9 | 19.54 / 4 |

Every earlier stop B costs more reach than the contact it removes. Stop B at 40 deg is a middle point (contact 18 vs
28, R1-aim 0.525 vs 0.497, cluster C gone) but its held-out gain over BDp is only +0.34, below the final-polish
rule's 1 point, so it is not a config the rule would accept. Capping K at BDp's 34.5 deg would lose about 3.2 points
held out (43 taken poses lost for 12 contacts removed, counted on the frozen pick1 shape): K's longer travel IS the
gain.

**Verdict on contact.** No CAD lift pays: the fitted levels are already the in-band / contact optimum, and every lift
loses 4-20 points on both protocols. The deep contacts (A, C) are structural: the reach pick1 adds is where its metal
enters the body. All of it is already counted in the verified numbers (a contact pose counts as not taken and adds its
contact share), and the contact-aware continuity drops 0 poses: no taken pose is reached through a contact pose.

## 2. The spring at K = 56.6 deg

**Demand, re-measured on pick1's fitted shape** (`mech`: the buildability lens's member masses + 4 g for the cap and
strip, gravity in the worst direction at 2 g, plus 2 mN.m per sealed bearing pair along K's self-motion):

| config | state A (K must stay on stop A) | forced | clip frames | K on the clips (dK max, rate) |
|---|---|---|---|---|
| BDp | 0.040 N.m | 0.022 N.m | 0.031 N.m | Reach a high shelf 0.85 deg / 6.9 deg/s; Wash opposite shoulder 3.34 deg / 28 deg/s |
| pick1 | **0.048 N.m** | 0.022 N.m (0.022 at dK > 34.5) | 0.033 N.m | **Reach a high shelf 15.8 deg / 52 deg/s** (26 frames forced); Wash opposite shoulder 6.2 deg / 32 deg/s |

The 0.08 N.m preload is 1.67x pick1's worst demand (BDp 1.99x): the spring returns K to stop A on every clip, fit and
held out. Wave, walking and the other four clips never open K.

**Strip stress** (0.3 x 5 mm 1.4310, E 193 GPa, EI 0.00217 N.m^2, sigma = 6 M / (b t^2), M = preload + k dK):

| rate (N.m/rad) | strip (mm) | preload turns | at BDp stop B 34.5 deg | at pick1 stop B 56.65 deg (priced) | at the as-designed 60.42 |
|---|---|---|---|---|---|
| 0.015 (the spec) | 145 | 0.85 | 1187 MPa | **1264 MPa** | 1278 MPa |
| **0.010** | 217 | 1.27 | 1147 MPa | **1198 MPa** | 1207 MPa |
| 0.0075 | 290 | 1.70 | 1127 MPa | 1166 MPa | 1172 MPa |

Limits (static bending, 0.7-0.8 Rm): +C1700 1190-1360 MPa, +C1900 1330-1520 MPa.

* The specified 0.015 N.m/rad strip reaches 1264 MPa at pick1's stop B: inside +C1900 (5 % under 0.7 Rm) but over
  +C1700's 0.7 Rm. It is buildable only in +C1900.
* **The spring for pick1: 0.010 N.m/rad, 217 mm of 0.3 x 5 mm 1.4310 +C1900, 0.08 N.m preload (1.27 turns of preload
  wind).** 1198 MPa at stop B, 10 % under +C1900's 0.7 Rm. The return demand does not depend on the rate (the preload
  carries it), so the lower rate costs nothing.
* **It fits the 6 mm cap.** The strip is still 5 mm wide (0.7 mm left for a steel cover, as for BDp); 217 mm x 0.3 mm
  fills 36 % of the O16 / O5 annulus (181 mm^2), the top of the buildability lens's 24-36 % range. 0.0075 N.m/rad
  (290 mm, 48 % fill) is too full to wind freely.
* Stop B must be built at the priced cut, dK 56.65 deg (the as-designed 60.42 engages below the 5-deg rule).

## 3. Forced J1 swing and feel (real timing)

Clips at their stored 10 fps (the arm's peak angular speed over every clip: 136.5 deg/s, Wave). The forced J1 swing
is measured on 2-deg slerp edges between neighbouring closed poses of the 1432-pose workspace grid: joint gain = deg of
joint per deg of arm, scaled to that peak arm speed.

| | BDp | pick1 |
|---|---|---|
| J1 peak rate on the clips | 125.6 deg/s (Wash opposite shoulder) | 125.7 deg/s (same) |
| K peak rate on the clips | 28 deg/s | 52 deg/s (Reach a high shelf) |
| J1 gain, forced edges, max / p95 | 2.55 / 2.36 | **2.29 / 1.99** |
| J1 gain, state-A edges, max | 3.41 | 3.30 |
| forced J1 at the clips' peak arm speed | 348 deg/s = 35 deg per 10-fps frame | **313 deg/s = 31 deg per frame** |
| K gain, forced edges, max | 2.16 | 2.01 |
| cuff force, state A (3 mN.m Coulomb per joint, worst sign), max / median | 0.32 / 0.15 N | 0.24 / 0.13 N |
| cuff force, forced (spring torque reflected), max / median | 2.35 / 2.24 N | 1.99 / 1.81 N |
| J2-stop impact (Carnot loss at 136.5 deg/s, worst direction) | 0.31 mJ | 0.24 mJ |

* The forced sub-chain swings J1 no faster than BDp: the larger opening does not steepen the self-motion (gain max
  2.29 vs 2.55). The steepest J1 gain of both designs is in state A (3.3-3.4), not in the forced states.
* The feel in the forced states is the spring preload reflected to the cuff, about 2 N; pick1's cuff pad sits further
  from GH (95 vs 84 mm), so the force is lower. The stop impact is negligible (fractions of a mJ).
* What the wearer notices that BDp's wearer does not: K moves on "Reach a high shelf" (15.8 deg at up to 52 deg/s,
  26 frames). K's sensor must track 52 deg/s, which any magnetic encoder does.

## 4. Verdict

**pick1 is buildable as the gen-4 CAD config (gen-4b), with two spec changes and no geometric fix.** The CAD does not
have to stay on BDp.

1. **Spring:** 0.3 x 5 mm 1.4310 **+C1900**, **0.010 N.m/rad** (217 mm strip), 0.08 N.m preload (1.27 turns of preload
   wind). 1198 MPa at stop B, 10 % under +C1900's 0.7 Rm. Return margin 1.67x pick1's worst demand (0.048 N.m). It fits
   the same 6 mm cap (36 % annulus fill). The present spec (0.015 N.m/rad) is acceptable only in +C1900, at 5 % margin
   (1264 MPa).
2. **K stop B at dK 56.65 deg** (the priced 5-deg rule cut), not the as-designed 60.42.
3. **No lift.** Every priced CAD lift is 4-20 points worse on both protocols; every earlier stop B is worse than pick1
   as priced. The fitted levels stay.

**What the CAD inherits and must disclose (red team, open for the user):**
* **Skin contact on extreme envelope poses: 28 vs 9 held-out poses (env fit), 35 vs 13 (fit 60).** None on a daily
  clip; the nearest is 11.2 deg from a "Raise overhead" frame (a pose BDp touches too), and the contacts only pick1
  has are at least 12.9 deg from any clip frame. They are structural: 19 of the 28 are poses BDp cannot reach at all.
  * Hub K's side wall meets the raised deltoid at elevation 150-165 (to -14.6 mm; BDp -7.3). Lifting the hub does not
    move it (-14.23 at +7 mm).
  * The knee link and pad meet the chest wall with the arm across the body at elevation 15-30 and extreme internal
    rotation (to -10.0 mm; K open 41-54 deg).
  * The gap already counts every one of them as not reached plus their contact share. The contact-aware continuity
    shows that no taken pose is reached through one.
  * Physically, the wearer meets the device there as a soft end stop through tissue, deeper than with BDp.
* **R1-aim lower:** in-band 2-10 mm held out 0.497 vs 0.574 (env fit), 0.563 vs 0.593 (fit 60).
* **K moves on one more clip:** "Reach a high shelf" opens K to 15.8 deg at up to 52 deg/s (BDp 0.85 deg). The spring
  holds it and the sensor tracks it.
* **The forced swing and the feel are not worse.** Forced J1 gain 2.29 vs 2.55, so 31 vs 35 deg per 10-fps frame at
  the clips' peak arm speed. Cuff force 0.24 / 1.99 N (state A / forced) vs 0.32 / 2.35 N. Stop impact 0.24 vs
  0.31 mJ.

**Verified numbers carried to the CAD (unchanged by this red team):** Bench(110,360) 18.40 (score 93.31), held out
21.31 / 22.69 vs BDp 19.54 / 23.68 / 24.18.

## Cost

Farm exo-cpu1 (cpu3c rate): attribution 3 jobs $0.096, lift fixes 10 jobs $0.105, stop-B cuts 6 jobs $0.070; total $0.27 (cpu5c $0.32), within the $0.60 budget. Local:
the `mech` run and the BDp fit-60 attribution (at most 3 processes, nice 10).

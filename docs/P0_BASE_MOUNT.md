# P0: base-mount physics (R10)

Question: the pipeline holds the exo's base fixed to the **scapula**; physically it bolts to a back plate on the
**thorax**. How far apart are those, what does it do to the reference design, and how is it resolved within the DOF cap
(target 3 DOF, user 2026-10-14)?

Instrument: the body rig's own girdle model (`pipeline/avg/body_pose.py`: `segs()` lifts the GH centre by
0.2 mm/deg x S above 30 deg elevation, `scap()` turns the scapula about the GH centre), exact signed distance to the
posed skin (`judge/sdist.py`), every frame of the 8 clips (1337 frames, the person's wanted poses).
Code: `pipeline/girdle/p0_base_mount.py` (analysis), `pipeline/girdle/girdle.py` (chain maths), results
`pipeline/girdle/p0_results.json`. Judge that keeps it measured: `judge/base_mount.py` (R10, every scorecard).
**Not yet cross-checked with OpenSim Seth 2016** (download needs the user's OK) - every number below inherits the rig's
girdle law, which is a hand-made model (purely superior, zero below 30 deg).

## 1. The human: GH centre and scapula vs the thorax

| clip | max elevation | GH rise vs thorax | scapula rotation |
|---|---|---|---|
| Raise overhead | 150 deg | 25.3 mm | 57.8 deg |
| Comb hair | 143 | 23.9 | 54.9 |
| Reach a high shelf | 132 | 21.5 | 50.1 |
| Wave (held out) | 95 | 13.7 | 34.1 |
| Drink from a cup | 69 | 8.2 | 22.8 |
| Wash opposite shoulder | 60 | 6.2 | 18.9 |
| Reach back pocket | 40 | 2.1 | 10.5 |
| Walking arm swing (held out) | 24 | 0.0 | 3.8 |

The GH centre passes 4 mm at 49 deg elevation and 10 mm at 77 deg.

## 2. The base part on a thorax plate

Between the pipeline's model (base turns with the scapula) and a thorax-fixed base, the reference base part's vertices
move up to **57.6 mm** (p95 55.2). Bolted to the thorax, the base part **enters the body in 197 of 446 checked frames,
up to 44.0 mm deep** (worst: Raise overhead, pose plane 30 / elev 150 / axial -60): the rising shoulder runs into a base
that no longer rises with it. Every design so far was shaped against skin that moved with its base.

## 3. The reference chain (4R, every axis through the GH centre) on a thorax base

- GH misalignment = the GH rise itself: worst **25.3 mm**, p95 23.8 mm; > 4 mm in 48 % of frames, > 10 mm in 33 %.
- The 4R closure still exists in every frame with the base thorax-fixed (kinematics only): the spare joint can absorb
  the scapula's 58 deg of rotation. The rotation is not the problem; the translation is.
- **Bound (new):** a chain whose axes all meet at one point fixed to the thorax misaligns the GH centre by at least half
  the range of GH positions - **12.7 mm** on the rig with the best possible centre. That exceeds the whole 8 mm width of
  the 2-10 mm band, so no link shaping can keep the metal in the band over the full range of motion: the
  fixed-centre-on-a-back-plate family is ruled out by the data, not by taste. (A misalignment e shifts the metal
  against the skin by up to e; staying in a band of width 8 mm needs e <= 4 mm - the proposed R10 threshold.)

## 4. Resolutions within the cap

| architecture (base on a thorax back plate) | DOF | worst GH misalignment mm | p95 | held-out worst | notes |
|---|---|---|---|---|---|
| spherical chain (all axes through GH), centre at GH rest = the reference as built | 4 | **25.34** | 23.78 | = | fails R10 by 6x |
| spherical chain, best fixed centre | any | **12.67** | 12.67 | = | the bound of section 3: > the 8 mm band |
| spherical chain + passive vertical base slide | N+1 | **0.0** | 0.0 | = | 0 only because the rig's lift is purely vertical; a passive joint counts as a DOF |
| **3R, offset axes** (axes need not meet at GH) | **3** | **5.82** | 5.63 | 5.82 | axis offsets [5.2, 7.6, 5.4] mm; singular margin 20.0 deg fit / **12.5 deg held-out** |
| **2R shoulder (offset axes) + humeral-rotation ring** (user's idea) | **3** | **6.79** | 6.46 | 6.79 | axis offsets [10.3, 5.8, 0.0] mm; singular margin 28.1 / 55.4 deg; ring travel 163.8 deg at this fit |
| scapula-fixed base (the pipeline's model) | - | **0.0** | 0.0 | = | not buildable: no back plate rides the scapula |

Residual by elevation is flat (3R: {'0-30': 4.5, '30-60': 4.68, '60-90': 5.63, '90-120': 5.82, '120-181': 4.68}; ring: {'0-30': 5.19, '30-60': 6.69, '60-90': 6.79, '90-120': 5.84, '120-181': 6.58}): a chain's translation is a smooth
function of its joint angles and cannot reproduce the rig's kink (0 mm up to 30 deg, then 0.2 mm/deg), so the minimax
spreads the error. Joint travel (3R): {'J1': {'min': 2.3, 'max': 163.0, 'span': 160.7}, 'J2': {'min': -20.6, 'max': 90.2, 'span': 110.8}, 'J3': {'min': -173.4, 'max': 17.0, 'span': 190.5}}.

**The ring, measured.** (a) *Travel*: the misalignment-optimal ring fit needs 163.8 deg of ring travel, but the
2R geometry can be chosen for travel instead: **66.7 deg** on the fitting clips, 86.5 deg with the held-out Wave
(`ring_travel.py`); the floor is **58.8 deg** - the humeral twist the clips use at nearly the same arm direction
(Wave, pose [16, 83, -56]). Misalignment and ring travel pull the 2R geometry different ways: a P3 trade-off.
(b) *Roundness* (`ring_roundness.py`): a circular rail centred on the humerus axis sees the arm's skin radius vary by
**13.5-24.9 mm over 120 deg** at every station 80-280 mm below GH (elbow 0-140 deg) - more than the whole band - and
only the deltoid cap (~60 mm) is round (4.7 mm over 120 deg, 9.9 over 160). So the rail must be **arm-fixed with a skin-
shaped underside** (carriage on link 2), and an arm-fixed rigid arc must fit the trunk-free window (-20..+62 deg about
the humerus, FINDINGS): ~67 deg travel + ~25 deg carriage ~ 92 deg vs an 82 deg window - tight, not impossible.

## 5. Where the arm never points

Over all 1337 frames the humerus never comes within **45.4 deg** (either sense) of the axis
(-0.525, -0.253, 0.812) in the thorax frame (x anterior, y up, z right): posterior-inferior-lateral <-> anterior-
superior-medial. That is the place for the singular configuration of a 2R pointing shoulder (J1 along it, a1 = a2 = 90):
the user's "2 at the shoulder + humeral rotation lower down" is kinematically sound for these 8 tasks, with a 45 deg
margin before the arm reaches the singular direction.

## 6. How fragile the 3-DOF fits are to the girdle law (synthetic laws, NOT data)

| fitted design | rhythm law (synthetic) | worst mm | p95 |
|---|---|---|---|
| 2R+ring | slope x0.75 | 7.6 | 7.11 |
| 2R+ring | slope x1.25 | 12.48 | 11.32 |
| 2R+ring | onset 20 deg | 8.48 | 7.68 |
| 2R+ring | onset 40 deg | 7.63 | 7.03 |
| 2R+ring | +8 mm anterior in flexion | 10.66 | 9.03 |
| 3R offset | slope x0.75 | 5.77 | 5.55 |
| 3R offset | slope x1.25 | 10.83 | 8.79 |
| 3R offset | onset 20 deg | 7.12 | 7.07 |
| 3R offset | onset 40 deg | 6.56 | 5.86 |
| 3R offset | +8 mm anterior in flexion | 11.03 | 9.36 |

A design fitted to one girdle law loses 1-6 mm when the law changes by plausible amounts. This is why the R10 judge must
move from the rig law to measured trajectories (OpenSim Seth 2016; the user's OpenCap shoulder markers) before any
3-DOF design is committed to CAD at L2, and why P3 fits against several laws at once (minimax).

## Decision

1. **A thorax back plate with a chain whose axes all meet at the GH centre is ruled out** (section 3: >= 12.7 mm
   misalignment with any fixed centre, wider than the band). Every design so far, the reference included, is in that
   family; its overhead numbers were measured against a base that moved with the scapula.
2. **Primary family: 3 DOF with offset axes on a thorax plate** - the user's target. On the rig law it brings the worst
   misalignment from 25.3 mm to **5.8 mm (3R)** / **6.8 mm (2R + humeral-rotation ring)**, with no extra joint and no
   actuator. That passes a 2-14 mm band (the user's allowance, e <= 6 mm) for 3R, not yet the proposed R10 (4 mm, the
   2-10 band). Closing the last ~2 mm, in order of preference: (a) P3 searches directions for misalignment AND skin
   hug together, minimax over girdle laws; (b) a compliant arm interface (liner + strap) specified to take +-2-3 mm,
   which turns R10 into "residual <= liner travel"; (c) only if the user allows a *passive* joint: a girdle slide (+1
   passive DOF, 0 mm on the rig).
3. **The 2R + ring is kinematically sound** (45 deg from the singular direction over all 8 clips, 55 deg margin on
   held-out clips), but its rail must be arm-fixed and shaped, the travel minimised (~67-87 deg), and it lives near the
   deltoid cap or in the lateral-posterior window - P3 objectives, not afterthoughts. The 3R has the smaller misalignment
   but its singular margin collapses on held-out motion (12.5 deg): the red team is searching the full ROM for its jam.
4. **R10 is now a judged number** on every scorecard (`judge/base_mount.py`, threshold 4 mm proposed); the reference
   design fails it at 25.3 mm, and its base part enters the body by 44 mm on a thorax plate.
5. Before L2 CAD of any 3-DOF design: the girdle law from OpenSim Seth 2016 and the user's OpenCap (data/raw/README.md
   items 1-2).

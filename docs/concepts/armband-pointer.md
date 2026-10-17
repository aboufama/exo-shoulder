# armband-pointer: closed thin-section armband at the distal arm + 2R donut pointer

Round J1 jump track, lens 1 cell R (humerus-axial J3). 3 active DOF, 0 passive, 0 passive translations.
Topology: scapula handler -> J1 (O20 hub, acromion top / back of shoulder) -> link 1 -> J2 (O20 hub, a2 = +-unit(a1 x t))
-> link 2 = a spar fixed in the pointing frame, down the lateral arm -> J3 = a closed thin-section ring bearing coaxial
with the humerus at station s (stator on the spar, rotor bolted into the user's upper-arm cuff).

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask.** Ask the anatomy before the mechanism: a
   closed ring is the one part in this design that must pass BETWEEN the arm and the trunk in every arm-down pose, so
   the first job is a parameter-free bound - for ANY ring (any station s along the arm, any axis through GH within
   12 deg of the humerus, any bore, the thinnest real section) on how many bench poses it can exist at all. That
   bound is independent of hubs, spar and seats, so it decides the morphology before a sweep is spent. Second: centre
   the ring on the arm section, not on the anatomical humerus line (the J3 axis only has to pass through GH; a few
   degrees of tilt move the ring centre ~10 mm at s 220 and keep th almost twist-free - planner: span 95.5 deg at 12
   deg off). Third: the rotor is ARM-fixed, so the bore only has to clear the arm's own section in the arm frame (no
   twist sweep), while the spar is in the pointing frame and sees the full twist - measure them separately.
2. **Rawest material.** The posed render skin of every bench pose (B.skin / signed distance on the fast grid cache and
   the exact libigl path), marched radially from the J3 axis at every 10 deg, every 20 mm from s 140 to 320, out to
   160 mm: the arm's own section (first radius clear of skin) and the first obstacle beyond it (trunk, axilla, forearm,
   head). Not the proximity atlas summaries. Cross-check against the J1 proposer's pre-screen (round101_ideation.md
   section 2 row 4: KA045XP0 in contact on 169-204 / 220 poses at s 205-240).
3. **Methods and tools.** tools/concept_kit.py (frames, wdir, dist_many, closure, members, evaluate with K3 march, K2
   dense continuity, K6), tools/concept_bench.py Bench(60,160) fast for the screen and Bench(110,360) exact frozen for
   the gate; an exhaustive grid over (station, tilt, bore, section) for the bound instead of CMA (the bound is cheap
   and has no local minima); then the faithful kit model at the bound's best ring for the real number.
4. **What else shows the number is right.** The bench itself (gap from B.report), the bound (a lower bound on any
   configuration's gap: reach and follow can only fall when hubs, spar and continuity are added), the independent
   J1 ring scan already in the repo (agreement check), the verifier harness and the alignment auditor; a red-team pose
   list (rest, walking-like arm-down clip frames, across-body, behind-back, overhead, elbow flexed 120+).

## Spec fixes (made before measuring)

- **J1 seat**: the spec's p* = [0.36, 0.72, 0.60] / bvec(120, 46) is the anterior acromion, outside the user's seat rule
  (back of the shoulder + acromion top only). The model seeds J1 at bvec(30, 70) (acromion top, the planner's
  narrowest-th seat: th 78.1-173.6 over the workspace) and bvec(0, 60) / bvec(60, 60).
- **Hubs**: O20 at every joint ("Keep O20 only"), not the spec's donuts.
- **Fold margin**: K.FOLD_MARGIN (5 deg) in th = angle(a1, J3 axis), the metric every verified row uses (the spec's 32-deg
  pole limit is pointer-cslide's, not this design's).
- **Ring bore**: the spec's KA045XP0 (bore radius 57.15) cannot hold this arm - the arm's 2-mm-clear radius about the
  humeral axis is 58-74 mm posteriorly (triceps) at s 220-280 in most poses (p50 of the per-pose maximum: 72 at s 220,
  64 at s 260). The sweep uses KA055XP0 (bore radius 69.85) and the bound takes ANY bore.

## Parameter-free bound: where can a closed ring exist at all? (raw posed skin, Bench(60, 160) fast)

Method (scratchpad probe, reproducible with the model's frames): for every bench pose, every station s along the J3
axis, every 10 deg about it, march the signed distance to the posed skin from the axis out to 120-140 mm. r0 = the
largest radius at which the arm is cleared (dist >= 0 or >= 2), over the angles; r1 = the smallest radius beyond the
arm at which skin starts again (trunk, axilla, folded forearm, head). A closed ring of radial section sec (KA..XP0
6.35 + two 1.5 mm housings = 9.35; the thinnest real 4.76 section + housings = 8) fits a pose iff r0 <= r_face and
r_face + sec <= r1. "Per-pose bore" lets each pose choose its own ring (an upper bound no rigid design reaches);
"fixed bore" is one ring. Reach and follow can only FALL when hubs, spar, continuity and collisions are added, so
gap >= 100 (max(0, .95 - follow_ub) + max(0, .90 - reach_ub)) for every configuration of the morphology.

Results (Bench(60, 160) fast grid cache; `python3 docs/concepts/models/armband-pointer.py bound '{...}'` reproduces them;
stations 160-300 mm, axis tilts 0 and 8 deg toward lateral / anterior / medial / posterior, any bore 30-112 mm):

| J3 axis, station | per-pose bore (sec 8, clr 0): follow ceiling / reach ceiling | gap lower bound | arm meets body (no gap at all) |
|---|---|---|---|
| humerus axis, s 160 | 0.217 / 0.388 | 124.5 | |
| humerus axis, s 200 | 0.500 / 0.456 | 89.4 | |
| humerus axis, s 220 | 0.533 / 0.531 | 78.6 | |
| humerus axis, s 240 | 0.583 / 0.644 | 62.3 | 0.268 |
| humerus axis, s 260 | 0.467 / 0.675 | 70.8 | 0.250 |
| humerus axis, s 280 | 0.517 / 0.688 | 64.6 | 0.241 |
| humerus axis, s 300 | 0.583 / 0.000 (the flexed forearm sits inside every ring) | 126.7 | |
| 8 deg lateral, s 280 | 0.617 / 0.725 | 50.8 | 0.186 |
| 8 deg medial, s 280 | 0.767 / 0.744 | 34.0 | 0.150 |
| 8 deg medial, s 300 (most generous cell) | 0.800 / 0.844 | **20.6** | |

**One rigid ring (fixed bore) - the bound that a real design obeys: gap >= 58.7** at the best cell (8 deg lateral,
s 280, ring face at 82 mm, follow <= 0.550, reach <= 0.713; 9.35 mm section: 60.0); the next cells are 64.6-69.4. With
both lattice errors given to the ring (arm exit 2 mm earlier, section 6 mm): **>= 55.8**. The per-pose-bore cells above
need a different ring in every pose, so 20.6 is not reachable by any mechanism; even it sits above the 17.5 bar.
Hubs, the spar, continuity and collisions can only lower reach and follow further.

Agreement: the J1 proposer's independent raw-skin scan (round101_ideation.md, KA045XP0 at s 205-240 in contact on
169-204 / 220 poses incl. all 85 arm-down poses) - the same wall, measured with other code.

Red team of the ring alone (named poses, humerus axis; "bore >= x" = the arm's 2-mm-clear radius, "free < y" = the
first other skin):

| pose (plane, elev, axial) | s 220 | s 260 | s 280 |
|---|---|---|---|
| rest (0, 4, 0), clip | **blocked**: medial arm on the flank 130-220 deg | **no ring**: bore >= 56, flank at 42 | **no ring**: bore >= 54, flank at 50 |
| rest + IR 75 | **blocked** 180-280 deg | **blocked** 190-270 | **blocked** 200-270 |
| across low (120, 45, -30) | **blocked** 80-210 deg | **blocked** 100-210 | **blocked** 100-210 |
| across body (135, 90, -45) | **no ring**: bore >= 74, chest at 62 | ring 68-94 | ring 64-116 |
| abduction 45 / 90, extension | ring >= 62-64 | ring >= 58-60 | ring >= 58 |
| overhead abduction 150 | ring >= 62 | ring >= 60 | ring >= 58 |
| overhead flexion 165 + IR 90 | ring 66-98 (head) | ring 60-108 | ring 58-124 |
| behind the back (-75, 30, 165) | ring 64-96 (back) | ring 60-134 | ring >= 60 |

The ring is lost exactly where the arm is near the body - rest, walking-like clip frames, internal rotation at the side,
reaching across low - i.e. the poses the wearer spends most time in (follow ceiling 0.55-0.62), not overhead.

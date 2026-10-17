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

Results (Bench(60, 160) fast grid cache; `python3 docs/concepts/models/armband-pointer.py bound2 '{...}'` reproduces
them: 35 cells = stations 240-300 x J3 axes through GH at the humerus axis and tilted 4 / 8 / 12 / 16 deg laterally,
8 deg anterior / posterior / medial / posterolateral, 16 deg medial at s 240; ring face radius 2-112 mm; the test is the
general one - the ring's annulus skin-free on all 36 rays AND the humerus line passing through the ring):

| J3 axis, station | per-pose ring (sec 8): follow / reach ceiling, gap bound | ONE ring (fixed bore): face, follow / reach, gap bound |
|---|---|---|
| humerus axis, s 240 | 0.583 / 0.631, 63.5 | 70, 0.517 / 0.606, 72.7 |
| humerus axis, s 260 | 0.450 / 0.675, 72.5 | 66, 0.450 / 0.650, 75.0 |
| humerus axis, s 280 | 0.467 / 0.688, 69.6 | 62, 0.450 / 0.688, 71.2 |
| humerus axis, s 300 | 0.533 / 0.000 (the flexed forearm fills every ring), 131.7 | 138.3 |
| 4 deg lateral, s 280 | 0.550 / 0.706, 59.4 | 70, 0.483 / 0.694, 67.3 |
| 8 deg lateral, s 280 | 0.567 / 0.713, 57.1 | 82, 0.550 / 0.700, 60.0 |
| 12 deg lateral, s 280 | 0.583 / 0.694, 57.3 | 100, 0.567 / 0.694, 59.0 |
| 16 deg lateral, s 260-300 | <= 0.5 / <= 0.14 (the ring must exceed 112 mm) | >= 121 |
| **8 deg posterolateral, s 280** | 0.567 / 0.713, 57.1 | **72, 0.567 / 0.706, 57.7** |
| 8 deg posterolateral, s 240 (most generous cell) | 0.650 / 0.681, **51.9** | 80, 0.600 / 0.613, 63.7 |
| 8 deg anterior, s 240-300 | 0.38-0.55 / 0.52-0.64, 66-95 | 73-100 |
| 8 deg medial, s 240-300 | 0.33-0.43 / 0.49-0.55, 92-148 | 92-148 |
| 8 deg posterior, s 240-260 | 0.48-0.52 / 0.64-0.66, 70 | 74-76 |

**One rigid ring - the bound a real design obeys: gap >= 57.7** (8 deg posterolateral, s 280, face 72: follow <= 0.567,
reach <= 0.706); with the lattice error given to the ring (6 mm section) >= 57.1. Even a new ring in every pose cannot
beat 51.9. Hubs, the spar, continuity and collisions can only lower reach and follow further. (A first version of the
probe marched from the ring centre and assumed the centre inside the arm; for tilted axes whose centre leaves the arm it
"fitted" small rings beside the arm - e.g. per-pose 0.98 at 12 deg lateral - an artefact the general test removes. Its
humerus-axis numbers agree with the table within 1-4 points.)

**The same bound on Bench(110, 360) EXACT** (libigl path, 470 poses; axis tilts 0 and 8 deg lateral, s 240-280, section
8, arm clearance 0; first-version centre-march test, exact for the humerus axis): fixed bore >= **56.5** at the best cell (8 deg lateral, s 280, ring face 82: follow <= 0.555,
reach <= 0.731), 64.9-74.1 elsewhere; per-pose bore 46.3-68.3; the arm meets the body (no gap at all along some ray from
the axis) on 19.6-26 % of the poses. Bench(60, 160) fast and Bench(110, 360) exact agree within 2.2 points.

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

## The faithful model (kit, Bench(60, 160) fast, K3 march, K2 dense, K6, ring outer faces contact-checked)

docs/concepts/models/armband-pointer.py: O20 hubs 1-2, link 1 and link 2's shoulder strap (12 x 3, K3 fitted, 60-deg
climb, laid out 2 x 2 mm at 140 mm from GH since hub 2 rides 90-160 mm out), the spar (16 x 4, in the pointing frame,
underside per sample = the radial requirement about J3 at its P-angle over the closing poses, so it clears the arm at
every twist), the ring (skin face at bore - 1.5 all the way round, 10 mm wide, K6 member; the outer cylinder and both
side annuli contact-checked). Sweep file docs/concepts/sweeps/armband-pointer.json (every configuration, in order).

| batch | configs | best gap | what it measured |
|---|---|---|---|
| A: ring KA055XP0 (bore radius 69.85) at s 260 on the humerus axis; J1 bvec(30, 70) / (0, 60) / (60, 60); sigma +-1; A1/A2 90/90, 110/70; q 0.9 | k0-k4 | 220.19 (k1) | sigma +1 parks hub 2 on a GH ray into the neck / trunk (K3 requirement infinite on > 10 % of poses): 310-330 |
| B: the bound's best ring (8 deg lateral, s 280, KA065XP0, face 81), sigma -1; q 0.9 / 1.0; spar angle c -40 / 0 / +40 | k5-k8 | 244.48 | ring face in band 0.20 (vs 0.11), but its outer face sits in the trunk / forearm on 77 poses |
| C: links laid out at 140 mm (the audit's sparse-sampling flag), batch A's ring, sigma -1: q 0.95, A1/A2 110/70 and 70/110, seats, el 80, c +40 | k9-k16 | **212.62 honest (k15)**; 200.43 (k11) flagged | k11 (A1 110 / A2 70) parks hub 2 so far out that link 2a is sampled 5.1 mm apart: not an honest number |

Best honest configuration k15 (score 22.68): J1 bvec(30, 70), sigma -1, A1 = A2 = 90, ring KA055XP0 at s 260 on the
humerus axis, spar at c +40, q 0.9: **gap 212.62, reach 0.581, follow 0.367, in-band 14 0.146, in-band 10 ~0.10,
contact 0.47**, 87 poses with the ring's outer face inside the trunk / forearm; per member in band: hub 1 1.00, hub 2
0.00, link 1 0.39, link 2 strap 0.01, spar 0.00, ring 0.11. Min th margin 6.37 deg (the fold is not the limiter).
Convergence gate (17 configs): best gained 7.19 score points over the second half, 5.80 over the last third, top-5
spread 7.19 - NOT converged, and it does not need to be: the verdict rests on the bound, which already takes the best
of every ring parameter and still sits 40 points above the bar; the sweep only shows how much more the real metal
loses (hub 2, spar, ring float) on top of it.

## Red team of the best configuration (k15)

- **The pose that jams**: none kinematically - the closed ring has no travel limit and the pointer's th stays 78-174 deg
  (min margin 6.37); the chain closes on 100 % of the bench. Every loss is metal against skin.
- **The point that pinches**: the ring's medial arc between the arm and the flank at rest, in walking-like clip frames,
  in internal rotation at the side and reaching across low (table above: no ring of any bore exists there), and the
  folded forearm at s >= 280 when the elbow is flexed (s 300: no ring fits any workspace pose, all of which have the
  elbow at 90). 87 of the taken poses carry the ring's outer face inside the body.
- **The optimistic number**: k11's 200.43 (link 2's strap sampled 5.1 mm apart because hub 2 is parked > 250 mm out) -
  reported as flagged, not as the best. And the bound's per-pose-bore cells (they need a new ring every pose).
- **Donning**: the hand must pass through a 139.7 mm bore (fine) but the rotor is bolted into the cuff around the arm -
  a closed rotor housing needs a split cuff; the bearing cannot be split.

## Verdict (GATE 0, round J1 jump track)

**Dead with its number, by a parameter-free bound.** No rigid closed ring about any axis through GH (humerus axis or
tilted up to 16 deg, any station s 240-300, any bore up to 112 mm, the thinnest real section) exists on more than
0.567 of the clip frames and 0.706 of the workspace, because the medial upper arm meets the flank (rest, walking-like frames,
IR at the side, across-low) and the folded forearm fills the ring plane near the elbow. That alone is gap >= 57.7
(Bench(60, 160) fast; Bench(110, 360) exact: humerus axis >= 67.0, 8 deg lateral >= 56.5) against the gate's 15 / 17.5, before any hub, spar or float. The
faithful kit model scores 212.62 honest (score 22.68; reach 0.581, follow 0.367, in-band 0.146): hub 2 of the 90/90
pointer is never in band, the twist-free spar floats over a 2:1 elliptical arm (0.00 in band), the ring face floats 20+
mm off the medial skin (0.11 in band). Passive translations: 0. Complexity 0.5 (tools/simplicity.py v2.2) - the
simplest mechanism screened, and the one the anatomy rules out. Lead 18.49.

## New knowledge (predicts beyond this morphology)

1. **Nothing rigid may close around the upper arm.** On this body a closed metal loop about the arm (ring bearing,
   ring gear, closed cuff shell) is impossible on >= 43 % of clip frames and >= 29 % of workspace poses at every
   station 160-300 mm and every axis within 16 deg of the humerus: the medial arm meets the flank (19-27 % of poses
   have no gap at all), and near the elbow the flexed forearm fills the ring plane. A cuff's medial arc must be soft
   (strap / liner); every arm-fixed metal part lives on the ~105-deg torso-free lateral arc (acromion-pointer-arm-ctrack
   measured it). This rules out ARMin / NESM-style closed humeral rings for this wearer.
2. **The humerus axis is eccentric in the arm**: the 2-mm-clear radius about it is 58-74 mm posteriorly (triceps) vs
   34-46 mm medially / anteriorly at s 220-280, so any coaxial ring's face is >= 20 mm off the medial skin (ring in band
   0.08-0.11 at a ring that holds the arm; the in-band-best ring face, 54-58 mm, fits only 2-5 % of poses).
3. **Conservation, measured on the coaxial side** (planner lesson, round 101): putting J3 on the arm axis makes th
   twist-free (th 78.1-173.6, margin >= 6.37 everywhere) but moves the full twist under link 2: the pointing-frame spar
   must clear the arm at every axial angle and sits 0.00-0.06 in band.
4. **A 90/90 pointer's hub 2 is off the skin by construction**: J2 is 90 deg from both J1 and the arm, i.e. on the great
   circle 90 deg from the J1 pole; from the acromion top that circle runs through the neck and the trunk, so hub 2's
   GH ray never clears skin in > 10 % of poses (sigma +1) or rides 90-190 mm out (sigma -1): 0.00 in band in all 17
   configurations.
5. **Tool fix for anyone bounding arm-encircling parts**: test the annulus on every ray AND that the ring encloses the
   humerus line (models/armband-pointer.py `ring_bound2`); a march-from-the-centre test (`ring_bound`) mis-scores tilted
   axes whose centre leaves the arm (it "fits" small rings beside the arm: per-pose 0.98 at 12 deg - an artefact).

## What happens next

The humerus-axial lever is closed on both sides (axis on the arm: this bound; axis off the arm: the lead's fold losses).
The loop moves on to the round planner's other lever - move hub 2 itself (ROUNDS.md, J1 lesson) - with this bound
available as a one-call pre-screen for any arm-encircling idea (`python3 docs/concepts/models/armband-pointer.py bound2
'{"stations":[...],"tilts":[[d,a]]}'`).

## Audit (independent auditor, 2026-10-17, Bench(60, 160) fast)

**Verdict: the death stands (not refuted).** Measured reason, one line: no rigid closed ring about any GH axis fits
between the medial arm and the flank (or the folded forearm) on >= 43 % of clip frames / 29 % of the workspace, and a
ring cannot vanish, so even with ideal stops and every other part ideal the gap is >= 72.2 (no stops >= 90.9) - versus
the 17.5 gate, the lead's 18.49 and the refutation line 78.93 (champion 68.93 + 10), before link 2's twist-free float.

- **Reproduced**: k15 re-run through the model file gives gap 212.62, reach 0.5813, follow 0.3667, in-band 14 0.1458,
  in-band 10 0.0983, contact 0.47, 87 outer-face contact poses, th 78.1-173.6, min margin 6.37: identical to the claim.
- **Convergence gate**: NOT met (17 configs; best gain over the 2nd half 7.19 score points, over the last third 0.00 by
  the k-order split - the claim's 5.80 used another split - top-5 spread 7.19). The farm is closed, so no CMA was run.
  The death is accepted on the bounds below, which cover every ring parameter (station, tilt, bore, section), not on
  the sweep.
- **The claim's bound is design-favourable**: ring_bound2 drops a pose where no ring fits without charging contact. A
  closed ring is always round the arm, so on such a pose it is in the body unless a stop keeps the arm out:
  - no stops (closed ring, fold window only): gap >= **90.9** at the claim's best cell (8 deg posterolateral, s 280,
    face 72; contact >= 0.332); 94.1-131.8 elsewhere;
  - generous stops (J1 / J2 stops excluding ANY spherical cap of arm directions - 600 axes x half-angle 5-120 deg - plus
    a twist window on the axial angle; the remaining ring-less poses are contact): gap >= **72.2** at the best cell (the
    best stop is a 35-deg cap about the adducted arm-down direction; contact still 0.145), 74.7-84.5 at 8 deg lateral /
    humerus axis / s 240 / 12 deg lateral. All with every other part ideal (in-band 0.90, no hub / spar / link loss).
- **Coverage gap closed**: the claim bounded tilted axes only at s 240-300. Proximal tilted cells are worse (perfect
  stops): s 220 at 8 deg posterolateral 72.9, s 200 83.1, s 220 at 8 deg lateral 66.2.
- **Over-strict check? One, and it does not matter**: the ring's skin face is modelled as a circle (in band 0.11; 0.20-0.23
  at the best cells). The rotor housing is arm-fixed, so its bore could be contoured to the arm section (ring in band up
  to ~0.9). That leaves the 72.2 ring-only floor and the twist-free link 2 (spar + strap in the pointing frame over a
  58-74 mm posterior / 34-46 mm medial arm section: 0.00-0.37 in band in all 17 configs) and hub 2 (0.00-0.03). Reaching
  78.93 would need in-band >= ~0.83 with no hub / link contact on top of the 72.2 floor.
- **Reporting note**: the median skin distance 31.8 mm shown for hub 2 / link 2a / spar is the fast cache clamp (+31.75),
  not a measured distance (those parts are farther out).
- Harness: `docs/concepts/verify/armband-pointer-audit-stops.py` (stop-aware and no-stop bounds),
  `docs/concepts/verify/armband-pointer-audit-cells.py` (cells + circular ring-face in-band), numbers in
  `docs/concepts/verify/armband-pointer_audit.json`.

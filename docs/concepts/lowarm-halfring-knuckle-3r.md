# lowarm-halfring-knuckle-3r - half-ring desmo knuckle (round 14, knuckle-o20-overhead lens)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Check the stop that replaces the deleted
   wall *as a tolerance chain*, not as a picture: the outer wall was a one-part groove (0.01 mm clearance); the pad makes
   the dwell hold a two-body stack (link 2 through J2's bearings vs link 1b's pad), so J2 runout, ring-insert
   concentricity and the pad's lap all enter the K play through the stage-1 lever (pin-to-wall motion per rad of crank)
   and the stage-2 ratio (K per rad of crank). Read the pad's real lever from the model (where the crank arm actually
   crosses link 1b), not an assumed 25-38 mm. Also: the link-2 root lift does not depend on the half ring at all; it is a
   change to link 2 that the lead's own chain (conecut) shares the contact with, so measure it as a lever that transfers.
2. **Rawest material.** The posed skin itself through the exact signed distance (CB_EXACT=1, libigl) on every pose of
   Bench(110,360) and the held-out clips, per sample: the frozen wear's per-pose distance arrays (978 samples per pose,
   link 2's 124 of them) are edited directly, never a digested in-band summary; the proposer's per-pose attribution logs
   (skin-distance gradient at pose 316 in link 2's frame) were re-read, not trusted.
3. **Methods and tools.** The model's own frozen protocol (DS._frozen_model: fit Bench(60,160) fast -> shape frozen ->
   worn on Bench(110,360) exact), a surrogate scan that replaces only link 2's segment of each pose's distance array and
   re-runs Bench.report (exact for in-band / reach / contact; the per-pose parts checks are re-run in the full model for the
   picks), a Latin-hypercube + local search of the morphology box on Bench(60,160), the S-bend as two tangent arcs at the
   R15-inner bar's centreline radius (16.5 mm) as a hard box edge, and the stage-1 / stage-2 kinematics (RF.dphi_of) for
   the dwell-hold tolerance stack.
4. **What else shows the number is right.** Bench.report itself (the outside judge), the cell-A0/A reproduction of the
   proposer's 18.37 / 18.28 on the same harness, the adversarial verifier (docs/concepts/verify/desmo-conecut-knuckle-3r.py
   pattern: plate-vs-horn solids, th margin with K play, blended IK, flood, per-pose dump), the alignment auditor, and the
   red-team pose list below (205 / 237 / 264 / 316 and the min-th poses).

## Morphology

desmo-conecut-knuckle-3r's verified chain unchanged (seats, K law, dyad 26 / 38.03, conecut knee, J3 dowel, inverted
stage 2) with three changes run as cells on one harness (docs/concepts/models/lowarm-halfring-knuckle-3r.py):

- **A0 half ring**: stage 1's groove keeps its inner wall over dwell + rise; the outer wall is cut back to the rise + the
  10-deg blend + 2 deg of q2 (135 of the 462 groove stations built, an 18.9-deg lip). The crank is held at phi = 0 in the
  dwell by the inner wall (phi > 0) and an own-angle stop pad on link 1b's top face under the crank arm (phi < 0).
- **A low arm**: the crank's free span 2.0 mm above link 1b's level (was 4.03); the arm builder joins levels with 60-deg
  ramps (5-axis machined crank, stated).
- **B link-2 root lift**: link 2's bar leaves the hub-2 stack h mm higher for r <= r_full from J2's axis and returns on an
  S-bend of two tangent arcs over L >= sqrt(4 R h - h^2), R = 16.5 mm (R15 inner on the 3 mm bar; 9.84 mm at h 1.5).

3 active DOF (J1, J2, J3); K slaved (never read); crank pivot and two knee pins are passive rotations; two higher pairs;
0 passive translations; no springs, gears, pulleys or cables.

## Results

(filled in below as measured)

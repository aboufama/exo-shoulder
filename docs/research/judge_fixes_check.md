# Independent check of the 2026-10-16 judge fixes (R1 groups, R17 general chain, R7 cut BOTTOM)

Checked 2026-10-16 16:19-16:55 UTC by a separate agent, against commit d434fd3 and the code it picked up in 9a08d62 /
9d89d57 / 53c2c5a. Every number below was re-measured here, not copied from the claim. **Verdict: not refuted.** All
three fixes do what the claim says. Every claimed number re-measures exactly, or to within 10 % on the hand check.
Two findings are new: the R17 attribution mislabels the K-stop mismatch as "inertia", and the knuckle's preload sits
right at the arm's push. Everything here is a MEASUREMENT change; no design changed.

Scratch scripts used: `bottom_check.py` (c) and `qs_check.py` (b hand check). They lived in the session scratchpad and
are reproduced in essence below; nothing in the repo was modified except this file and one events line.

## (a) R1 / R1-aim / R4 group rule (pipeline/full-exo/metal_groups.py, score_design.py, r1_decompose.py)

- **Diff read.** The only change to how parts are picked is the group filter: the old `base | l<digits> | H | cuff` became
  `metal_groups.classify`. The H branch (arm-fixed parts, kept only within 110 mm of GH, posed on the humerus) is
  byte-identical. Two new stops: a scored group missing from a frame, and a glb group the rule cannot place. BANDS=10,14
  computes the frame metrics once and bins them twice. The per-clip and overall arithmetic is unchanged. r1_decompose.py
  uses the same rule and now applies the per-group offsets T, as score_design.py does.
- **All 31 designs with exo.glb + clips.json, old rule vs new rule.** No design raises. **No group is dropped.** Only three
  designs gain a group:
  - `user_minarc_bdp` and `l1_minarc-bdp` gain `l1a` and `l1b` (link 1a / 1b and hub K, which were silently dropped before).
  - `param2_r20_n3_s1414_4` gains `S`. S is this project's own part, not the user's handler: D6-01 scapula base + J1 cap /
    spacer / 2 bearings.
- **The user's own parts are treated as before.**
  - `F` (the user's MIDDLE / FOREARM CUFF + screws) was skipped implicitly before. It is now skipped explicitly, with a reason.
  - `H` (BOTTOM, arm pad, the user's upper-arm cuff, ...) keeps the 110 mm rule.
  - On both minarc designs H contributes 0 samples, old and new: no arm-fixed metal lies within 110 mm of GH. So R1 cannot
    move from the re-cut BOTTOM, as the claim says.
- **Note (pre-existing, not a regression):** arm-fixed metal beyond 110 mm of GH is never scored by R1.

## (b) R17 / R11 dynamics judge (judge/dynamics.py GenDesign)

**Old 3-joint results reproduce.**
- `judge/test_dynamics.py --fast` PASS (51 s): single hinge exact; chain vs transmission.py p95 0.0015; wedge unlocked
  p95 0.032, locked frames >= 50x.
- `--general` PASS: the general chain matches the spherical path on band_r14_3r_s1351_1. The largest difference is 0.06
  relative, on a 0.17 N force that is rounded to 0.01 N.
- I ran the pre-fix dynamics.py (9a08d62~1) and the current one on band_r14_3r_s1351_1 (`--quick`, Raise overhead + Wash).
  The two JSONs are identical except one field: `forearm_parts_mass_g` 446.3 -> 406.4 g. That field is reporting only;
  F_mass enters no simulation. It moved because of the seam-mesh mass fix on the user's forearm parts.

**Re-run of R17 / R11 on both minarc designs (full default case set, local, jobs 2).**

| | user_minarc_bdp | l1_minarc-bdp |
|---|---|---|
| dynamics.json vs committed | identical (only the order of the unordered lock-clip lists differs) | identical (same caveat) |
| moves freely (nominal rolling bearings) | yes | yes |
| M_GH peak | 0.153 N.m | 0.152 N.m |
| force peak | 0.70 N | 0.69 N |
| twist peak | 1.96 deg | 1.96 deg |
| cuff pressure incl. arm parts (R11) | 0.273 kPa | 0.397 kPa |

The claim and scorecard show the CAD's R11 as 0.272 kPa; this run reads 0.273. That is a 0.001 rounding difference.

**Hinge fit, checked my own way.** For every adjacent pair I took the relative rotation between the reference frame and
the frame of largest travel. Its axis agrees with GenDesign's fitted axis to within 0.0007 deg.

**Hand check of the physics (quasi-static, user_minarc_bdp, every clip frame).**
- *Model:* gravity only, frictionless hinges, member masses from GenDesign. The cuff is the judge's 6-axis tissue spring
  at 200 mm. Equilibrium is J^T W = -tau_g with W = Kt J dq. K is held on stop A. On frames where the plan puts J2 on its
  q2 stop, J2 is held there too. The K opening that the stop refuses becomes a tissue deflection.
- *K-closed frames (1312):* |M_GH| at most 0.033 N.m, |F| at most 0.153 N. The judge's frictionless per-clip peaks are
  0.034-0.038 N.m, which include dynamics. Gravity accounts for them.
- *K-open-in-plan frames (25, all on Wash; the plan opens K by up to 2.19 deg while J2 sits on its stop):*

  | Wash frame | hand check M_GH / F / twist | judge |
  |---|---|---|
  | 78 | 0.149 N.m / 0.65 N / 2.02 deg | 0.151 / 0.65 / 2.0 |
  | 122 | 0.137 / 0.60 / 1.86 | 0.153 / 0.70 / 1.96 |

  The judge's worst frame (122) moves the arm at 3.1 deg/s, so quasi-static is the right comparison. **The 0.15 N.m peak
  is physical:** the clock spring's 0.08 N.m preload holds K closed, and the cuff tissue (0.03 N.m/deg in torsion) twists
  about 2 deg instead.
- *Without the J2 stop held:* the other hinges absorb the refused K opening and the peak falls to 0.022 N.m. The J2 limit
  in GenDesign is therefore what makes the result, and it is applied correctly.

**Finding 1 - the attribution labels the mismatch as inertia.** The "inertia only" row (`passive|nofric|nograv`) keeps
the K spring. For Wash it reads 0.138 of 0.153 N.m, at an arm speed of 3.1 deg/s. That load is the K stop / preload
mismatch, not inertia. The fix is to relabel that attribution row (or drop the spring in that run) before anyone uses it
to argue about link mass.

**Finding 2 - K is marginal, not comfortably closed.**
- The torque the tissue puts on K at its stop reaches 0.078-0.084 N.m on Wash frames 78-79 and 122, against the
  0.08 N.m preload.
- So the claim "K never leaves stop A" holds only to the judge's stop softness. Quasi-statically K would open by about
  0.1 deg there.
- On the clips this changes nothing (twist about 2 deg, against the 5 deg limit).
- Forward-looking: for pick1 (gen-4b, K opens up to 56.65 deg on the bench), the same rule puts a floor of about
  preload / tissue torsion = 2.7 deg of cuff twist under every K opening. The rate adds about 0.015 N.m over 56 deg, or
  about 0.5 deg more. That is still under 5 deg, but with half the margin. Re-run R17 on gen-4b at both spring rates.

## (c) The cut BOTTOM (pipeline/concept_l1/build_pinknee_l1.py slice_capped, repair_cut_bottom.py)

I checked the BOTTOM node in exo.glb on l1_minarc-bdp and l1_skin-normal-3r-pin-knee-h1 against the builders' source
BOTTOM.

The source BOTTOM as loaded is 7 open pieces. Merged, and with its zero-area slivers dropped, it is one closed volume of
24.2461 cm3. That confirms the stated root cause.

| | l1_minarc-bdp | l1_skin-normal-3r-pin-knee-h1 |
|---|---|---|
| watertight / winding consistent / is_volume | yes / yes / yes | yes / yes / yes |
| pieces | 1 | 1 |
| edges not shared by exactly 2 faces | 0 | 0 |
| volume | 21.017 cm3 | 22.505 cm3 |
| cut-plane flatness | 4.1e-6 mm | 3.7e-6 mm |
| cap area: unsigned / signed along -n / exact source section | 85.3705 / 85.3704 / 85.3704 mm2 | 84.6921 / 84.692 / 84.692 mm2 |
| Monte Carlo (200k pts, libigl winding numbers) vs source clipped at the plane | 0 disagreements | 0 disagreements |

The cap's unsigned and signed areas match, so the cap does not overlap itself. The cap area equals the exact source
section, so no area is missing. The Monte Carlo test finds no point that is inside one solid and outside the other.

**Before vs after, glb by glb.** I compared all four touched glbs (the two cut L1s, plus l1_skin-normal-3r-pin-knee and
l1_offset-skin-normal-3r; I did not compare the k4598-m5 variant's glb) node by node:
- Only the BOTTOM node changed.
- The two uncut BOTTOMs keep their volume exactly (24.2461 cm3).
- The cut BOTTOMs moved from 20.991 to 21.017 cm3 and from 22.484 to 22.505 cm3. That is the old self-overlapping fan cap.

**Correction.** repair_cut_bottom.py says it keeps "the same node names and order". The names are the same set, but
trimesh reloads them in a different order. No judge depends on the order (sampling is seeded per mesh), so this is
harmless. The docstring is still wrong.

**R7 re-run.**
- `judge/part_validity.py` on a copy of l1_minarc-bdp: 22 parts judged, all one closed solid, all_ok True (PASS). The
  BOTTOM is the 21.02 cm3 single piece.
- On a copy of user_minarc_bdp (41 STEP parts, coverage complete): all valid single solids, all_ok True (PASS).

## (d) R1 / R4 / R7 / R17 re-measured on both minarc designs

| design | R1 (2-14) | R1-aim (2-10) | R4 Raise overhead (14) | R7 | R17 | source |
|---|---|---|---|---|---|---|
| user_minarc_bdp, claimed | 80.0 % | 51.0 % | 72.0 % | PASS | PASS 0.153 N.m / 0.70 N / 2.0 deg | d434fd3 |
| user_minarc_bdp, re-measured | 80.0355 % | 50.9553 % | 71.9848 % | PASS (41/41) | PASS 0.153 / 0.70 / 1.96 | this check, local |
| l1_minarc-bdp, claimed | 80.5 % | 52.5 % | 72.7 % | PASS | PASS 0.152 / 0.69 / 1.96 | d434fd3 |
| l1_minarc-bdp, re-measured | 80.5116 % | 52.4948 % | 72.7380 % | PASS (22/22) | PASS 0.152 / 0.69 / 1.96 | this check; R1 / R4 on the CPU farm (one job, $0.01-0.05; a first submission lost its client after upload, so at most one more job of the same size) |

user_minarc_bdp's R1 / R1-aim / R4 (local run) reproduce the committed score files to all printed digits.
l1_minarc-bdp's farm run rewrote score.json and score_14mm.json byte-identical to the committed files.
On both designs the scored groups are base, l1a, l1b, l2, l3, l4; F is excluded, and H gives no samples within 110 mm.

## What was not checked

- R2, R6 and R16 on the re-cut L1s, which the claim also did not re-run.
- The other designs that will move on their next re-judge (param2's S, the pin-knee R17s, the slide fallbacks).
- R8: the parts_full.json material rule is still open; the claim says so.
- The k4598-m5 variant's glb diff.

## Next

1. Relabel the attribution row (Finding 1).
2. Re-run R17 on gen-4b / pick1 at spring rates 0.010 and 0.015 to price the K-preload twist floor (Finding 2).
3. Fix the repair tool's docstring.

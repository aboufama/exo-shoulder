# Independent check of the dense R6 judge (judge/part_contact.py, commits 8a7e220 / 864c696)

Verifier, 2026-10-16. Verdict: **not refuted.** The new judge catches the edge crossings it was built to catch. It
agrees with an independent measurement to within 0.1 mm and raised no false alarm at the running gaps of the passing
build. One gap stays open and must be fixed before the next user-style CAD is graded: **open parts are never used as
containers** (see section 3).

## Method (independent of judge/sdist.py and of the judge's sampling)

Script: `indep_r6.py`, kept in the verifier's scratchpad and not committed. Its method:

- **Samples.** Each part's welded mesh gets RANDOM area-weighted surface samples at 0.25-0.3 mm spacing, plus every
  vertex, plus points on EVERY triangle edge (not only the sharp ones) at 0.15 mm. That is 2.6-3.2 M points per design.
  The judge samples faces at h = 1.0 mm.
- **Pose.** The samples are posed in world with `scene_export.frame_xforms`, the shared input data.
- **Inside, two ways.**
  - libigl's exact generalized winding number, |w| > 0.5. It does not care about orientation and tolerates small
    cracks in the mesh.
  - Separately, ray parity: a vectorised Moller-Trumbore test with 3 random rays and a majority vote. It ignores face
    orientation entirely.
- **Depth.** `igl.point_mesh_squared_distance` to B in world.
- **Pairs.** Every ordered pair from different groups is tested, open parts included (as A and as B).

A sanity case reproduces the regression test: two crossed slabs read exactly 1.00 mm. The same value comes out when
B's normals are inverted, by both inside tests.

## 1. Results

Values are in mm. "Independent" gives the winding-number value / the ray-parity value. "Judge" is part_contact.run,
step 1, on the same frames.

| build, frame | pair | independent | judge |
|---|---|---|---|
| 06b5a59, Raise overhead 20 / 24 / 27, Wave 72 / 74 | link 2 strap IN J3 plate | 1.15-1.16 / 1.15-1.16 | 1.07 |
| same frames | J3 plate IN link 2 strap | 0.99-1.01 / 0.99-1.01 | 0.91-0.94 |
| 06b5a59, Wave 72 / 74 | link 1 IN link 2 | 0.67 / 0.67 | 0.66 |
| 06b5a59, Wave 72 / 74 | link 2 IN link 1 | 0.45 / 0.45 | 0.44 |
| HEAD, Raise overhead 20 / 24 / 28, Wave 68 / 72 / 76 | all 49 parts, every pair | none > 0.15 | 0.00 (no pair) |
| param_r20_n3_s1414_4, Raise overhead 0 | link 2 (D5-03) IN arm end (D5-04) | 3.45 / 3.45 (3.49 at 0.2 mm) | 3.50 |
| same | link 1 IN base | 1.50 / 1.50 | 1.44 |
| same | link 1 IN link 2 | 1.47 / 1.47 | 1.48 (Wave 150) |
| same | arm end IN link 2 | 1.48 / 1.48 | 1.46 (Walking 108) |
| same | **base IN link 1 (open part)** | **3.49 / 3.49** | **not measured** |
| same | **link 2 IN link 1 (open part)** | **3.49 / 3.49** | **not measured** |
| band_r16_3r_s1373_1, Raise overhead 60 | l1 proxy IN l2 proxy | 1.48 / 1.48 | 1.48 |
| same | l2 proxy IN l1 proxy | 1.33 / **1.08** | 1.07 (max over all frames) |

Where the param_r20 overlap sits: the 3.49 mm region of link 2 inside the arm end is a 5 x 8 x 4 mm block, 77 mm from
the arm end's origin. It is a real overlap between two groups that rotate relative to each other at J3 (162 deg apart
at this frame), not a seated coaxial fit.

## 2. What this shows

- **The bug is fixed.** Both the 1.1 mm plate crossing and the 0.66 mm strap crossing on the first build of
  l1_offset-skin-normal-3r are caught, at the right frames and with the right pairs. The old vertex-only test read 0.00
  on them. The judge reads on average 0.01-0.10 mm low, because a 1.0 mm face grid does not land exactly on the deepest
  point. It never reads higher than the independent value except within sampling noise (3.50 vs 3.45-3.49). A real
  crossing of more than about 0.25 mm therefore cannot drop under the 0.15 mm tolerance.
- **No false positives.** On the HEAD build, at 6 frames of the two motions that failed before, both inside tests find
  no point of any part deeper than 0.15 mm in any other part. That covers every pair that shares a joint (seated
  washers, plates on hubs). The judge's 0.00 is true.
- **Re-orienting the band proxies is right.** On the inconsistently wound band proxies, the orientation-free ray parity
  reads 1.08 mm. The judge's re-oriented answer is 1.07 mm. The winding number on the raw mesh reads 1.33, which is
  the artefact the fix describes.
- **Runtime is fine for judge_all fast.**
  - Measured in this run: 0.22-0.23 CPU s per frame on l1_offset-skin-normal-3r, after a one-off setup of about 30 s
    on a cold cache.
  - From the recorded runs: user_osn_k4216_v3 at step 3 (451 frames) took 137 s wall with 4 jobs (0.96 CPU s per
    frame). The heaviest user-style CAD, cad_r18, takes about 2 CPU s per frame, so about 15 CPU-min fast and 45 CPU-min
    full.
  - Step 3 at 30 fps samples every crossing that lasts 0.1 s or more. The full run (step 1) sees every frame.

## 3. Open gap: open parts are never containers (fix before grading the gen-2 CAD)

`pair_ok()` drops every B that is not watertight after `weld()`. Three main links are open because of tiny
tessellation cracks: 14-194 boundary edges, 2-19 mm in total, and one body each.

| design | open part (never a container) |
|---|---|
| param_r20_n3_s1414_4 | D5-02 link 1 |
| param2_r20_n3_s1414_4 | D6-03 link 2 |
| user_osn_k4216 / _v2 / _v3 (gen-2 winner CAD) | D7-03 link 2, and the two RSR3R3 rails |

The measured consequence is on param_r20, Raise overhead 0. The base and link 2 sit 3.49 mm inside link 1, and both
inside tests agree. The judge sees each pair only from the other direction, at 1.44 and 1.48 mm. Here the pairs are
still flagged and the design's max (3.50) is still right. But a part fully embedded in an open link would be missed
entirely, for example a pin or screw whose bore was not cut: the link's surface never enters it.

Fix, for the judge's owner: use a container test that does not need a watertight mesh. Two options:

- close the cracks: weld at 1e-2 mm, then fill the holes;
- for parts that stay open, fall back to libigl's generalized winding number, |w| > 0.5. Here it matched ray parity to
  0.01 mm on the open D5-02.

Add an open-container case to judge/test_part_contact.py. Until then, read R6 on the user-style CADs as a lower bound
for pairs that involve those links.

user_osn_k4216_v3 itself was checked at Wave 102, the judge's worst frame for its link pairs. Every part was tested
against the open D7-03 link 2 with both inside tests, and nothing sits deeper than 0.15 mm inside it. So the blind spot
hides nothing at that frame. Other frames were not checked.

## Not checked

The full 1337-frame sweep. This check covers the 15 frames named above, and the judge's own step-1 sweep was not
re-run end to end. The cad_r13 / l1_3r_offset / l1_r14 drops come from the earlier sdist fix, and were not
re-measured here.

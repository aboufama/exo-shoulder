# Independent check: open parts as R6 containers (judge/part_contact.py close_open, dfd0503 + a0abee9, re-judges b45c80f)

Verifier, 2026-10-16. Verdict: **not refuted.** On every open container in today's designs, the judge's capped
closure gives the same inside/outside answer as an independent generalized winding number of the raw open mesh, and as
my own ray parity. The depths it reports are reproduced, and nothing missed turned up. The new regression case fails on
the old judge and passes on the new one. The passing l1_offset build still reads 0.00 with the same output format. The
D6 user note checks out point by point.

There is **one latent gap**, which affects no current part (section 5). An OPEN part with more than one body, one of
which is wound inward, still hides whatever sits inside that inward body when open_mode is "cap" (the default).

## Method (shares no code with judge/sdist.py or judge/part_contact.py)

The scripts live in the verifier's scratchpad and are not committed:
`/tmp/claude-0/-home-user-exo-shoulder/029f38fb-570e-5d7a-bebc-fc64e6215529/scratchpad/vopen/` (indep.py,
run_open.py, field.py, d6.py, old_case4.py, redteam_multibody.py, scan_open.py).

- **Input data (shared).** Parts come from `judge/common.load_parts`: the RAW exo.glb, NOT welded and NOT capped. Poses
  come from `scene_export.frame_xforms`.
- **A side.** Random area-weighted surface samples: 6-10 per mm² on the parts, 25 per mm² on the cuffs. Every vertex
  is added as well.
- **Inside, two ways.**
  - libigl's exact `igl.winding_number` on B's raw open mesh, |w| > 0.5.
  - My own ray parity: 3 random directions with a majority vote. The triangles are projected onto the plane normal to
    the ray and grid-binned. Each hit uses an exact 2D barycentric test, and its depth along the ray is interpolated.
- **Depth.** libigl's exact distance to B's RAW mesh (igl.AABB). It is not measured to the capped mesh.
- **Tolerance.** Depth is reported for points deeper than 0.02 mm. "> tol" means deeper than 0.15 mm.

## 1. What is inside each open container, at the worst frames

Depths are in mm, shown as GWN / ray parity, compared with the judge's part_contact.json at step 1.

| container (design) | frames re-measured | inside it (independent) | judge |
|---|---|---|---|
| D5-02 link 1 (param_r20_n3_s1414_4) | Raise overhead 0, Wave 150 | D5-01 base **3.494 / 3.494**; D5-03 link 2 **3.477 / 3.477** (w = 1.00 at the deepest point); J2 bearing 1 0.098 (< tol); every other part 0 | 3.50 / 3.50 at all 1337 frames |
| D6-03 link 2 (param2_r20_n3_s1414_4) | Drink from a cup 37 and 69, Comb hair 100, Wash opposite shoulder 100, Raise overhead 60 | **nothing at any depth > 0.02** (D6-02, D6-04, the J2/J3 nuts, spacers and bearings) | nothing |
| D7-03 link 2 (user_osn_k4216_v3, read from git e1a3c87^) | Wave 71, Raise overhead 60, Drink from a cup 69, Comb hair 100 | **nothing at any depth > 0.02** (D7-01 base, D7-02 link 1, D7-04 member 3, the J3 ring nut) | nothing new |
| RSR3R3 rails (user_osn_k4216) | not re-run per frame: the rails have no boundary edges, so close_open adds nothing; their closure field equals GWN (section 2) | - | nothing new |
| cad_r13 BOTTOM + neck + dovetail rail (cad_r13_n3_s1331_0) | Wash opposite shoulder 192, Drink from a cup 33 | flank liner (iglidur J) **0.555 / 0.555** at Wash 192 (w = 1.00, 184 points > tol), 0.50 at Drink 33; the reverse direction (BOTTOM in the liner) 0.248 / 0.248 | 0.55 at Wash 192; 0.25 the other way |

The depths agree to within 0.03 mm, which is the random-sample spacing. GWN and ray parity agree on every one of these
points.

## 2. The judge's closure as a field, against the raw open mesh

Subject under test: `part_contact.weld` followed by `close_open(m, "cap")`. I evaluate the integer winding number of
the capped chain with **igl.winding_number**, not with sdist, and call a point inside if round(w) >= 1, as the judge
does. That is compared with |GWN of the raw open mesh| > 0.5 and with my ray parity on the raw mesh.

The points are 25,000 uniform in the box plus 25,000 near the surface (offset 0.15-3 mm along the face normal, on both
sides). Only points deeper than 0.15 mm count.

| open part | bodies | closure | points | inside (judge / GWN / ray) | judge != GWN | GWN != ray |
|---|---|---|---|---|---|---|
| D5-02 link 1 | 1 | 6 cap triangles, 4 loops | 48,560 | 11,383 / 11,383 / 11,383 | **0** | 0 |
| D6-03 link 2 | 1 | 186 caps, 4 loops | 48,889 | 11,448 / 11,448 / 11,449 | **0** | 3 (rays through the export holes) |
| cad_r13 BOTTOM part | 1 | 9 caps, 1 loop | 48,905 | 10,238 / 10,238 / 10,238 | **0** | 0 |
| across rail RSR3R3 | 1 | no boundary (non-manifold edges only) | 44,509 | 13,017 x 3 | **0** | 0 |
| along rail RSR3R3 | 1 | no boundary | 43,111 | 13,928 x 3 | **0** | 0 |
| D7-03 link 2 (v3) | 1 | 15 caps, 2 loops | 48,826 | 11,123 x 3 | **0** | 0 |

On every part the capped chain's winding number is an integer to 1e-4, between 0 and 1. No point reads -1, so no part
is inverted. The author's claim (0 disagreements on about 35,000 points per part) is reproduced with independent code.

## 3. The regression case fails on the old code and passes now

I ran `test_part_contact.open_containers()` against the judge at 3774132, the last version before the change. Its
`prepare` is wrapped to ignore open_mode.

- **Old judge:** 10 checks fail. The pin reads **0.000 mm** in all 4 variants (T-junction / hole x cap / gwn), because
  the slab is never used as a container.
- **New judge:** 0 checks fail. The pin reads **3.000 mm** in all 4 variants, and the pad above the hole stays silent.

There is one weakness in the test, and the test is not wrong. The "2 x 2 mm hole" variant actually removes two
separate triangles: 6 boundary edges in 2 loops, each capped by the very triangle that was removed. So ear clipping
of a loop with many edges is exercised only by the T-junction variant (24 edges, 20 caps). A non-convex polygonal hole
of 8 or more edges would test the shortest-diagonal ear clipping properly.

## 4. No false alarm, and the output format is unchanged

- `python3 judge/test_part_contact.py` (the full suite) passes:
  - the 06b5a59 first build still FAILs at 1.07 / 0.66 mm, and the vertex-only test reads 0.00;
  - the fast path equals sdist's max_depth to 1e-6;
  - the final build reads **0.0 / 0.0 mm** over 14 + 117 frames.
- The judge's CLI on a copy of the HEAD `l1_offset-skin-normal-3r` build (exo.glb + clips.json), at step 3, over 451
  frames and 1324 ordered pairs, read **0 interpenetrating (worst 0.0 mm)**. Its CLI line, in the usual place, reads
  "0 open parts closed as containers (0 not usable)".
- JSON: every key of the committed (older) file is present, and the only new keys are `open_parts` and
  `reoriented_parts`. `open_parts_not_tested_as_container` is still there, now empty.
- `judge/scorecard.py` reads the file through the same path.

## 5. Red team: an open part with an inward body (the latent gap)

`weld()` re-orients body by body only when a part is watertight. `close_open()` only fixes consistency
(`fix_winding`), followed by one global volume-sign flip.

I built a synthetic part: the test's open slab plus a separate closed 6 mm block wound inward. An R0.5 pin sits fully
inside the block, 2.65 mm deep.
- `open_mode="cap"` reads **0.0** (the block's interior has winding -1, and the judge counts W >= 1).
- `open_mode="gwn"` reads **2.65**.

Inward bodies do occur in this pipeline: the band_* D4 member proxies, as weld's own docstring says.

**Today nothing is affected.** I scanned all 35 design dirs. There are 8 open parts, and every one is a single body
with positive volume after capping. The extra component of D6-03 is a zero-volume pinhole cap.

**Fix (one line of intent):** in close_open, after capping, split into bodies and invert each body whose volume is
negative, as weld() does. Alternatively, count inside as W != 0.

A second note, also with no current impact: the retired band_* designs (band_r13_n3_s1331_0, band_r10a_0,
band_4c_best, none with a judge dir) carry open "sliding-cuff guide rail (proxy)" parts. Their cap_max_dev_mm is
5.8-8.0, so those are real open ends, not cracks, and the cap decides what counts as their inside. That is visible in
part_contact.json, as designed. I did not validate it here.

## 6. The D6 user note, checked against the parts

| claim | independent measurement |
|---|---|
| Nothing inside D6-03 link 2 | 0 at depth > 0.02 at the 5 frames in section 1. The closure field agrees with GWN everywhere (section 2). |
| The UPPER ARM CUFF is 4.65 mm inside the FOREARM CUFF at Drink from a cup 69 | **4.65 / 4.65** (GWN / ray) at Drink from a cup 69. The reverse direction reads **1.00 / 1.00**. |
| 346 frames: Drink 36-145, Comb hair 40-163, Wash opposite shoulder 41-152 | Every boundary was checked. Drink 35 = 0, 36 = 1.02, 145 = 1.62, 146 = 0; Comb hair 39 = 0, 40 = 1.61, 163 = 1.59, 164 = 0; Wash 40 = 0, 41 = 1.60, 152 = 0.46, 153 = 0. The three ranges add up to 110 + 124 + 112 = 346. |
| Only the -vB arc is involved; the flat land and the +vB arc are clear | All 20,381 inside points over 16 frames lie on the -vB side arc. None are on the land or on +vB. |
| The overlap runs from the elbow end to s 139.1, from 19.1 deg of wrap to the 110 deg tip | s 83.9-138.8, wrap 19.5-110.0 deg (16 frames; the author had 1337) |
| Deeper than 3 mm: s 83.9-117.4, wrap 24.5-56.5 | s 83.9-116.6, wrap 24.8-53.8 |
| The deepest point is at s 89.0, 32 deg | s 87.9, 31.4 deg, 4.65 mm (random samples) |
| The sketch frame | The cuff mesh spans s 83.85-164.65. The side-arc vertices lie at R 50.0-52.0 about (v 4 +- 35, z -54.8): the inner R50 and the 2 mm wall. |
| Trim the -vB arc to <= 19 deg: the R50 arc goes from 96 to 16.7 mm, with its tip at v -47.4 / z -7.6 | 50 x 110 deg = 96.0 mm; 50 x 19.1 deg = 16.7 mm; the tip is at (-31 - 50 sin 19.1, -54.8 + 50 cos 19.1) = (-47.4, -7.6) |
| Shortening the cuff needs 55.25 mm | 139.1 - 83.85 = 55.25 |
| The gen-2 CAD already trims to 12 deg | `CUFF_WRAP_NEG = 12.0` in pipeline/conformal/param_cad/user_style_osn.py:47 |

The note's advice holds. Nothing sits inside D6-03 link 2. The judge lists no pair involving D6-01 to D6-04 above
0.15 mm. Those parts are closed meshes, so the change under test does not alter that answer, and I did not
re-measure them as containers. The only failing overlap is the project's U cuff against the user's FOREARM CUFF.

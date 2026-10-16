# Findings so far (2026-10-09 .. 2026-10-14)

What has been learned, with numbers, so nobody re-derives it. Earlier history and commits:
github.com/aboufama/exo-arm (archive, private).

## Score history (honest score = `pipeline/full-exo/score_design.py`: follow x share of covered skin 2-10 mm)

| design | honest | notes |
|---|---|---|
| conformal 4R, first CAD (`designs/final`) | 8.1 % | 15-20 mm median gap, overhead follow 39 % |
| band designs, simplified geometry (`designs/band_4c_best`) | 80.5 % | **5 DOF** (4R + cuff), 4.0 mm links, no real stacks / neck / rail - not buildable as modelled |
| GPU search on real geometry, r13 (`gpu_client/band_search_r13.json`) | 37-45 % search, 35-37 % local detail | 5.5 mm links (FEA), v4 joint stack, hugging neck, back/top base |
| r13 4R built as fair CAD, first build | 38.0 % | follows 64.5 %, in-band 58.9 %, zero collisions |
| same, after the quality pass (swept-band links, turned JN hub, conformal saddle cuff) | 29.6 % | follows 64.5 %, in-band 45.9 %; the turned JN hub had lost its contoured skin side |
| same, turned skin side restored (dimple) + neck fixes (2026-10-15) | 32.0 % | follows 64.5 %, in-band 49.6 %, overhead 20.7 %. Same rebuild with the old flat hub: 30.2 % -> the skin side is worth +1.8 pts, the neck changes +0.6 |
| r13 3R + sliding cuff (`cad_r13_n3_s1331_0`), first build with every part valid | 21.2 % | follows 61.0 %, in-band 34.8 %, overhead 20.5 %, 436 g (R8 fail: Ti rail + keel); see "Arm end" |

**Measurement changes are not design regressions.** Stricter skin, natural motions and the in-band metric each moved
numbers on 2026-10-13. Always report a score change with its cause.

The search evaluator (`pipeline/conformal/gpu/band_impl.py`) is optimistic against real CAD: 4 mm slabs, sparse
samples, no stacks/neck early on. The honest scorer on built CAD is the reference.

## The base mount -> R10 (measured 2026-10-14, docs/P0_BASE_MOUNT.md)

The pipeline held the base fixed in the **scapula** frame; physically it bolts to a back plate on the **thorax**. On the
rig's girdle law (GH lift 0.2 mm/deg above 30 deg, scapula rotating about GH), all 1337 frames:
- GH rises up to **25.3 mm** vs the thorax (4 mm at 49 deg elevation, 10 mm at 77 deg); the scapula turns up to 58 deg.
- The reference base on a thorax plate: **enters the body in 197 of 446 frames, up to 44 mm** (Raise overhead) - every
  design so far was shaped against skin that moved with its base.
- **Bound**: any chain whose axes meet at one thorax-fixed point misaligns the GH centre by >= half the GH range =
  **12.7 mm** > the 8 mm band. The fixed-centre family on a back plate cannot meet the 1 cm rule overhead.
- **Offset axes absorb it without a joint**: for fixed axis directions, the GH point a serial chain carries is linear in
  the axis points (`pipeline/girdle/girdle.py`), so the best points are an exact minimax LP. 3-DOF on a thorax plate:
  3R **5.8 mm**, 2R shoulder + humeral-rotation ring **6.8 mm** (vs 25.3). Not yet <= 4 mm (R10 proposed). Sensitive to
  the girdle law: +25 % slope -> 10.8 / 12.5 mm. The residual is flat in elevation: no chain reproduces the rig's
  0-then-linear kink.
- 3R's singular margin: 20 deg on fitting clips, **12.5 deg on held-out** clips. The 2R pointing shoulder: the arm never
  comes within **45 deg** of one axis over the 8 clips -> its singularity has a home (55 deg margin held-out).
- **Humeral-rotation ring**: travel can be 67 deg (87 with held-out Wave; floor 59 deg = twist the clips use at the same
  arm direction). A circular rail on link 2 sees **13.5-25 mm of skin-radius spread** over 120 deg at every station
  80-280 mm down the arm (only the deltoid cap, ~60 mm, is round: 4.7 mm) -> the rail must be arm-fixed and shaped.
- Judge: `judge/base_mount.py` (R10 on every scorecard). Still the rig's law: OpenSim Seth 2016 / OpenCap must replace it.

## R10 on the scapula handler: what passive elements can and cannot do (2026-10-15, `judge/base_stage.py`)

The measurement is unchanged: `judge/base_slip.py`'s central law (handler = acromion cluster, Karduna / van Andel /
Lempereur angles, 4.2 mm slip) still gives **15.2 mm** worst frame (Raise overhead, 150 deg) for a base rigid on the
handler. `judge/base_stage.py` (new, design side) keeps those sources and changes only the mechanism that turns them into
a chain-centre error; all numbers are worst frame over the 6 fitting clips (held-out Wave + Walking in brackets),
central law, every frame of cad_r18_n3_s1392_1_f300's clips. No design here adds an active DOF: every passive element
is set by closure (the arm or a bone contact), the user's handler is untouched, only how J1 sits on it changes.

| mechanism between handler and J1 | worst frame (mm) | across the humerus (R1-relevant) |
|---|---|---|
| rigid on the handler (today, R10's number); passive cuff slides alone change nothing here - they remove the force, not the offset | **15.2** (7.5) | 11.8 |
| 3-axis stage set by the arm brace (elbow-referenced; Hamming 2012 cuff errors 0-4 deg x 325 mm) | 23.6 (16.2) | - |
| 1 slider set by the brace along the humerus, cuff slides across it | 10.0 (6.2) | - |
| 1 torque-free slider, set perfectly (earlier P0 idealisation) | 7.0 (5.4) | 6.4 |
| **3-axis stage set by a bony follower on the lateral acromion** (32 mm above GH) | **7.3** (5.7) | 5.9 |
| **2-axis stage set by the follower, the handler holding the centre along n** (n 17 deg from its lever) | **6.55** (5.05) | - |
| 2-axis stage across the handler's lever, set perfectly (no such reference exists) | 2.4 (1.6) | 2.3 |
| per-user calibrated law (f 0.32 on angles and slip), rigid | 4.9 (2.4) | 4.0 |
| **follower stage + per-user calibrated law (f 0.32 on angles and slip)** | **2.3** (1.8) | 1.9 |
| follower stage + calibrated angles only (slip not repeatable) | 4.6 (3.1) | 3.8 |
| follower stage, low law (review best case, no slip) | 3.95 (3.75) | - |
| **2-axis follower stage + calibrated law (f 0.32 / 0.55)** | **2.15** (1.6) / 3.65 (2.8) | - |
| 2-axis follower stage, low law | 3.39 (3.23) | - |

What this shows (new knowledge, with the reason):
- **A skin-held body knows the GH centre along its lever, not across it.** Its error is (rotation error) x (lever) plus
  its slip; the rotation part is perpendicular to the lever. The handler's lever is GH - acromion (45 mm), so a perfect
  2-axis stage across it leaves 2.4 mm (the stage-2 normal found by search, (0.55, -0.75, 0.37), is 8 deg from the
  lever). The arm brace's lever is the humerus (325 mm): it knows GH along the arm (elbow, bony) and is 6 mm off across
  it per degree of cuff error. The two good directions span a plane; the third (lever x humerus, anterior overhead)
  has no good skin reference, so **none of the handler + arm combinations tried reaches 4 mm** (best 10 mm: a slider
  set by the brace), and the "slider set perfectly" of P0 (7.0 mm) has no physical reference that sets it.
- **A bony follower moves the lever, not the slip.** A spring-loaded pad on the lateral acromion, directly above GH,
  setting a 3-axis torque-free stage under J1, makes the lever vertical, so the dominant overhead error (handler
  IR/ER, 25 deg about the superior axis, 12.6 of the 15.2 mm) no longer moves the chain centre: 15.2 -> 7.3 mm. Better
  with one axis fewer: let the handler hold the centre along n = (0.68, -0.57, 0.46) (17 deg from its own lever, where
  it is good) and the follower set the two directions across it: 6.55 mm, 2.15 calibrated, 3.39 under the low law.
- **Proof that no uncalibrated skin reference passes R10 under the central law:** every skin contact over the scapula
  slips 4.2 mm at 150 deg (McQuade & Smidt), already > 4 mm with zero lever (averaging several contacts helps only if
  they slip independently; a skin sheet does not). "Impossible" here is conditional on the
  literature law; it fails only if the user's skin slips less (measure it) or the slip is repeatable (calibrate it).
- **The path to <= 4 mm:** follower stage + the user's systematic slip removed by a calibrated motion law (double /
  multiple calibration of an acromion cluster cut max errors 44.8 -> 14.2 deg in cadavers, f ~ 0.32 = the share that is
  not repeatable; Brochard 2011 matched palpation on 5 of 6 axes): **2.3 mm (1.8 held out)**, or 4.6 mm if the slip
  itself is not repeatable. The law need not cost a part: offset (non-concurrent) axes can carry it, as P0's exact
  minimax LP did for the thorax base (`girdle.fit_minimax`; not fitted here: it needs the signed, measured c(pose), so
  the user's own data come first - handler + bony landmarks at 3-4 elevations, base_slip_model.md section 6.1).
- **Design rule (the number the user's measurement must hit):** the follower path passes R10 when the non-repeatable
  share f of the user's slip is <= 0.55 (f 0.5 -> 3.6 mm, 0.55 -> 4.0, 0.7 -> 5.1); a rigid base needs f <= ~0.26
  (0.32 -> 4.9 mm): the follower doubles the tolerable non-repeatability. Placement: 25-40 mm above GH and +-10 mm off
  the vertical gives 2.0-3.1 mm calibrated, 6.3-9.7 mm uncalibrated (in the scaled Seth scapula the AC joint is 38 mm
  above and 25 mm medial of GH, so the spot is the acromion lateral of the AC joint).
- **Judge:** `judge/base_mount.py` now scores a girdle design with `base.stage = {kind: follower, gh_minus_p_mm,
  f_ang, f_slip}` (7.28 / 2.33 mm, and 6.55 with `normal`, reproduced on a copy of cad_r18_n3_s1392_1_f300); f < 1 only with measured data.
- **It helps R1 as much:** R1 is judged with the chain centred on GH; on the body the links are offset by the misalignment
  across the arm - 11.8 mm today (the whole 10 mm band), 5.9 with the follower, 1.9 with follower + calibration.
- **Red team / costs:** a pad on a bony prominence worn for hours (keep it torque-free and gravity-balanced so it
  carries < 0.5 N, soft liner); it must fit beside the user's handler footprint (unknown: ask); stage travel >= 15 mm
  (23 mm under the high law) adds height under J1 (R1 near the base); the stage passes every moment, so MVP2's assist
  still lands on the handler (Stienen 2009). Model limits: brace errors are Hamming's averages, elbow slip 3 mm assumed,
  the follower's slip = the handler's slip law, the calibration factor is a cadaver ratio.

## R2 on the user's own body (`BODY_FIT=user`, 2026-10-15)

Measurement unchanged (`judge/body_contact.py`); only the body option: the rig bounded by the user's own arm parts
(`pipeline/avg/user_fit.py`). Coverage is partial: the box ran at load 40-70 on 4 cores and the CPU farm (exo-cpu1)
was not deployed, so instead of the full step-6 sweep (228 frames, ~4 h at the CPU share available here):
(a) every part (80 / 62) at the 9 frames where any part of either design was deepest on the rig (each part's rig-worst
and attributable-worst frame: `<design>/judge/body_contact_user_worst9.json`); (b) every step-6 frame of Comb hair
(31 more) for the only three parts of ours that enter the rig by > 0.5 mm at all (upper-arm cuff, its M4 screws,
BOTTOM + neck + JN hub). The user fit only pulls skin inward, so a part outside the rig stays outside the fitted body
(except in the rig's arm-in-chest overlap, where (a) found nothing new).

| design | ours, attributable (limit 0.5 mm) | where | on the rig (step 6) |
|---|---|---|---|
| cad_r20_n3_s1414_4 | **0.93 mm** (17 of 31 Comb hair frames; 0.65 at the 9 rig-worst frames) | BOTTOM + neck + JN hub, Comb hair f174 [60, 90, -53, 79] | 4.71 mm (same part, Comb hair f162) |
| cad_r18_n3_s1392_1_f300 | **0.93 mm** (same frames; 0.72 at the 9 rig-worst frames, Wave f126 held out) | same part, same frame | not reported (old judge format) |

- **R2 on the user's body: 0.93 mm vs 0.5 mm, one part, both designs (the arm end is the same).** The user fit takes
  r20's 4.71 mm to 0.93: most of the rig's R2 was the rig's oversize elbow.
- **The 0.93 mm is most likely the fit, not the design (red team on our own measurement).** The deepest points
  (8 vertices, 0.33-0.93 mm, "region edge (plain depth)") sit at the lateral elbow, 57 mm from the elbow centre and
  level with it - BOTTOM's distal end under the user's elbow stack, 300 mm from the neck we added. `user_fit.py` leaves
  BOTTOM out of the skin bound because this project modifies it, but its elbow end is the user's own geometry, worn on
  the user's arm, so the real skin clears it. Next (a measurement change, to be reported as such): bound the skin by
  BOTTOM's unmodified elbow end too, then re-run; if 0.93 survives, lift BOTTOM's skin face there by 0.5 mm.
- Our upper-arm cuff (19.9 mm) and its M4 screws (17.6 mm) lie in the rig's arm-in-chest overlap (Wash opposite
  shoulder): attributable 0 on both bodies.
- **Measurement caveat found:** the user's forearm cuff scores 24.1 mm attributable ("other region, own skin visible",
  Wash opposite shoulder f42) - the user fit pulls the forearm skin inside the cuff, so in the rig's forearm-through-
  chest overlap the cuff is no longer hidden by its own skin. Same 24.1 mm on the rig; an artefact of the missing
  soft-tissue contact, on the user's part, not a design finding.
- Next: the full sweep (all parts, step 6 and the judge default step 2) on the farm once exo-cpu1 is up:
  `BODY_FIT=user python3 judge/body_contact.py <id> --step 6 --out <design>/judge/body_contact_user.json`.

## Published girdle motion and the red team (2026-10-14)

- **The rig's girdle law is 2-3x too small and 1-D** (docs/research/gh_translation_literature.md): bone-pin clavicle /
  scapula angles through a rigid clavicle chain put GH +35 mm superior at 90 deg scaption (rig 12.7), plus 5-24 mm
  posterior and 10-28 mm medial, plane-dependent; vector error of the rig 16-51 mm. +-7-12 mm (1 SD) is not a function
  of arm orientation. The rig's scapular rotation rates match bone pins, but it pivots the scapula about GH instead of
  the AC joint. Acromion skin plates track the scapula to 5-7 deg below 100-120 deg elevation, up to 25 deg above.
- Under that law (`girdle.lift_literature`): reference chain on a thorax plate 64.9 mm; offset-axis 3-DOF refits
  10.7-19 mm on fitting clips, 22-26 mm held out (`p0_literature.json`).
- **Red team** (pipeline/redteam/REPORT.md): orientation-only chains are >= 12.5 mm off for a -10..+15 mm shrug; the
  reference 4R cannot close in 19 % of the plausible workspace (47-49 % of cross-body poses); P0's 3R gimbal-locks at an
  arm-forward pose near walking (a1 ~ a2); the least-travel ring has a 21 deg closure hole at the T-pose; the elevation
  assist never lands on the rigid saddle - the knit band carries all of it (25 N.m on the saddle = 18 kPa mean).
- **Kinematic optima are not designs**: P0's 3R built as L1 keep-out CAD (`designs/l1_3r_offset`) scores R1 0.1 %,
  R2 25 mm, R6 51 mm - its thorax-fixed J1 hub sits where the raised arm goes.
- **Rig vs the user's parts**: the user's forearm cuff (24 mm) and BOTTOM sit inside the rig's arm in every frame - the
  rig's forearm / elbow is likely too big (P2 scans).

## The human model is wrong in measurable places -> P2

- **Biceps bulge**: the swept upper-arm envelope (max over all frames) sits up to 25-30 mm above the relaxed skin at the
  anterior midline (theta ~ -90 deg about the humerus, s 160-190 mm from GH) at full flexion (132 deg). Triceps ~10 mm.
- **No contact model**: in "wash opposite shoulder" the upper arm passes into the chest; in "walking" (axial -90, arm
  at the side) the posterior-medial arm passes into the torso. Anything hugging the arm inherits these overlaps.
- The upper arm is not round about the humerus: skin radius 36-70 mm depending on direction.

## Cuffs

- **The old upper cuff** (user's forearm cuff scaled x1.24) entered the body in 7 of 8 clips, up to 46 mm, including
  the lateral side. (An earlier check missed it: a name-matching bug skipped it.)
- **A rigid C-cuff wing cannot exist** beyond theta = -20 .. +62 deg about the humerus (0 = lateral, + posterior)
  without touching the trunk or chest in some ADL frame (`fair_cad/out_cuff/trunkmap.npz` method,
  `fair_cad/cuff_trunkmap.py`). Current cuff = a lateral **saddle** under BOTTOM (`fair_cad/cuff_fair.py`): fair
  shrink-wrap inner surface over the swept envelope + 2 mm compressed liner, flat land in BOTTOM's plane, 5 lines + 5
  tangent arcs outline, 6x M4x6 ISO 10642 from inside (same thread engagement as the user's M4x8), 40.6 g AlSi10Mg.
  Zero body contact in every frame. The knit band wraps the rest of the arm.
- The user's **forearm cuff** (not ours, not modified) enters the forearm/biceps 19-27 mm at deep flexion and the torso
  in walking. Flag to the user; do not change their part.

## Links and joints

- **Short link** (r13 4R): J1-J2 hub centres 24.7 mm apart (1.7 mm between the O23 seats), axes 24 deg apart, 5 mm
  height step. No surface treatment fixes it - the search needs a minimum arc (~35 deg at R ~60 mm) so every link has a
  real arm. Same failure the user called "heinous" earlier (two hubs side by side).
  **Guarded since band code `band-2026-10-15t`**: job keys `min_arc` (35 deg; bounds the samplers, rejects in evaluate)
  and `min_arm_mm` (10 mm clear between a link's two hub seats at the fitted hub heights, after the shape fit);
  `make_cad_design.py` refuses either (override `--allow-short-link`, only with the user's OK). The deg rule alone is not
  enough: 35 deg leaves 16.1 / 13.1 / 10.1 / 7.1 / 4.1 mm between O23 seats (r 11.5) with hubs 65 / 60 / 55 / 50 / 45 mm
  from GH, and 5.1 mm at 65 mm with r 17 seats. Conversely r13's link 3 (29.6 deg) has 16.9 mm at its fitted 74 / 80 mm
  hub heights: the deg rule rejects it, the mm rule would not. The evaluator's geometry puts r13's link 1 at 2.1 mm.
- **Construction that reads as designed** (members.py `FIELD_MODE=swept`, default): each arm a swept constant-section
  band (straight generators across its 14 mm width, one fair height profile along it, clamped in value and slope to the
  hub planes), thickness easing hub stack -> 5.5 mm over 12 mm, G2 blend into exact hub planes over 4 mm. The earlier
  2-D "fair field" and the original local-lift fields produced folds and lumps.
- **Stacked joints**: the lower link's top must stay under its seat plane + 35 deg near the hub (it thickens toward the
  skin instead), otherwise the upper link leaps over it in a cliff. Joints whose hub plane sits below the skin floor get
  raised (ramp check) - J1 needed 3.7 mm once; cap lower hub plates at 6.5 mm or they become blocks.
- **Edge round 0.5 mm on links**: with 1.2 mm the flat seat ended at r 10.3 and the O22 cap skirt (r 9.3-11) and its
  M1.6 screws (r 10.15) overhung the round - a fit error and an invalid sliver face.
- **v4 joint** (`fair_cad/joint_v4.py`, docs/HARDWARE.md): O23 hub, 10.47 mm above the skin face; magnet + sensor PCB
  placeholders under a O22 G2 dome cap.
- **Strap links ride high because of their bend radius, not their section** (2026-10-15, r20 s1414 #4, strap vs fair
  links on the same chart grids, skin side minus the band evaluator's fitted ribbon underside, off the hubs): l1 median
  3.55 mm (fair 1.34), l2 9.58 mm (fair 0.13) -> R1 2-14 mm 35.0 % (strap) vs 46.2 % (fair). The cross-slope the
  constant section cannot follow is only 2-3 mm edge to edge; the excess is along the spine: l2's hubs sit 21.3 / 11.5
  mm over the need (both upper), and an S-bend at the old R >= 25 mm + 60 deg ramp needs ~45 mm to drop 21 mm, so the
  B-spline (<= 5 control points, bending weight 1500) stayed 8.4 mm over its own floor (median). The fair link drops
  with ~5 mm bends (smootherstep over Lt 8-25 mm). At R >= 10 mm (3.3 t of the 3.0 Ti strap: hot-formed or 5-axis
  machined), bending weight 150 and 3-6 control points the offline refit on the same floors gives 0.36 (l1) / 0.49
  (l2) mm. Rule: a link's bend radius must be small next to the height its hubs sit over the skin (here R <~ drop / 2).
- **A clamping cap must not bottom on its housing** (v5 joint, docs/HARDWARE.md "Preload by construction"): the cap
  flange sat on the outer ring and the spigot top in one plane, so with bearing rings at the low end of their width
  tolerance (0/-120 um, P0) the cap bottoms on the spigot and the outer rings float up to 0.24 mm - the loose bearing
  again. The spigot now tops out 0.03 under the ring (`joint_v5.CLAMP_GAP`); spacerO (select-ground) and spacerI
  (matched, delta shorter) set the preload, the cap and ring nut clamp the two stacks.

## Arm end (BOTTOM + neck + J4 hub, one 7075 part)

- **Turned hub + swept neck** (`armend_fair.build_hub_neck_v2`): revolve with exact seat; neck = constant 14 x 6.5
  section along the skin-hugging path, starting 6 mm inside the hub.
- **Turned skin side** (`hub_need` / `fit_underside`): per ring radius the axial height the dense envelope allows (max
  over the ring and all followed frames, skin + 2 mm + 0.5), then the closest sketch above it - centre flat + cone
  (+ the old face F as an outer annulus = "dimple"), short G2 corner blends, revolved. r13 n4: centre 3.1 mm under F to
  r 2.5, 25 deg cone back to F by r ~10. Radial skin gap under the hub: min 3.15 -> 2.71 mm, worst-frame median 7.14 ->
  4.78, all-frames median 13.33 -> 11.46; exact body clearance of the hub region (451 frames) 2.68 -> 2.60 mm.
- **Neck end**: morphing the 14 mm neck into BOTTOM's 30 mm bar section over the last few mm folded the loft (the
  lateral face self-intersects; OCC `isValid` still says True, every later boolean silently fails). Now the neck keeps
  14 x 5.5 and runs 6 mm into BOTTOM past the cut -> plain transversal fuse (`NECK_END=bar` = old). Inside the hub it
  starts 5.9 thick (0.3 inside both hub faces) so nothing is coincident or tangent; a flat face 0-0.4 mm under F is
  snapped to F (a neck underside grazing the rim blend broke the recess cut). Check lofts with
  `armend_fair.self_x` (BOPAlgo_ArgumentAnalyzer), not `isValid`.
- **3R + sliding cuff** (`cad_r13_n3_s1331_0`): every part one valid solid now (R7). What was broken:
  (1) `sheet.sheet_solid` sewed the 5 faces at 5 um and took the FIRST shell: on steep members the edge rounds drift
  from the exact trimmed outline, sewing leaves several shells -> an open 3-4 face "solid" with a meaningless volume
  (reproduced on the official maps: link 1, 4 faces, invalid). Now: retry 0.02-0.1 mm, keep the one closed shell.
  (2) the evaluator's ribbon floor for link 2 started 29 mm above J2's plane at J2's rim (JN plane 119 mm vs J2 61 mm
  from GH, ramp-limited from JN only) -> an 85 deg wall, J2 raised 12 mm by the ramp loop, link 2's skin side 8 mm inside
  the envelope. Now the floor is capped at RAMP_DEG out of every hub plane (`Member.ramp_cap`): J2 raise 2.6 mm, link 2
  -1.4 mm, link 1's J2 hub 0.8 mm over its need (was 9.2). (3) rail + neck were ONE loft whose dovetail-with-keel
  sections morphed into the neck: self-intersecting -> the BOTTOM merge returned 0 cm3 and assemble crashed. Now
  (`build_dovetail_rail_neck`): exact revolve head, straight-quad keel loft to the skin envelope, separate neck (smoothing
  spline path, approach run down the bar's axis). (4) saddle: channel tool had a sign error (a 13 mm rectangular slot,
  no dovetail) and the 18 mm plate was narrower than the v4 washer recess (r 9.15-9.3) -> recess broke out of its
  sides; now the dovetail + liner offset, plate 2 x 12.3. (5) the top-mounted base: cap-screw drills ended exactly on the
  seat face (invalid solid) and the 3 M2 back-plate holes sat 0.075 mm from a cap-screw hole / 0.55 mm from the disc
  edge; now drills cross the face, M2 at r 12 between the cap screws on a O28 disc.
- Still wrong on the 3R build: the neck runs back beside the rail toward the bar and grazes the saddle's lip in the
  last ~2.5 deg of travel (0.44 mm at the clips' max 45.0 deg, 0.55 at the 45.6 deg limit; true ray-parity check); the
  rail part enters the body by 1.0 mm (ray-parity verified, 'Wave' 60); the JN plate sits ~35 mm above the skin
  (zj4 112) so the skin-following keel is 4.5-40 mm deep and the rail part is 63 cm3 of Ti (R8 436 g).
- **Travel of an arc slide / open ring** (for a 2R + humeral-rotation ring): an ARM-fixed ring at this rail's height (64 mm
  down the humerus) is body-free (> 2 mm, all 451 clip frames, exact distance) only over 130 deg at r 92 mm about the
  humerus axis and 124 deg at r 80; at r 70 (about skin + 1 cm) it hits the body even at its centre. Travel + the
  saddle's length (+-8 deg) + the neck must fit inside that window, so 120-160 deg of travel cannot be an arm-fixed rail
  here; the long arc has to ride on the shoulder side (it then does not turn with the humerus) with a short arm-fixed
  cuff, and its constant radius stands off a non-round arm (36-70 mm skin radius). Other limits seen in this build:
  one-end neck = a long cantilever arc; the 26 mm saddle and the stop slot set the end stops; the neck must leave
  beyond the saddle's reach (here the body window ends 0.3 deg past the saddle's travel).

## Structure (in-house FEA, `pipeline/conformal/thin_study/REPORT.md`)

25 N.m worst direction: link bodies need ~5.5 mm (SF 1.5); seat zones carry 0.3-0.6x body stress; a cuff rail needs
>= 10 mm in Ti; the 7075 neck at 14 x 6.5 has SF ~2. Superseded for 10 N.m by the CalculiX section below.

## R9 strength, measured with CalculiX (`judge/fea.py`, 2026-10-15 afternoon)

Loads: D1 = 10 N.m about GH in the exact worst direction. D1F = the same moment plus the 50 N cuff force that produces
it at 200 mm, worst pair. MVP1 = R17's envelope (D1F / 10) plus 3 g of the part's own weight. Solver: C3D10, t/2 mesh,
then a t/3 check under the governing wrench (validated on a cantilever and a thick ring within 2 %). Every design now
gets R9 from `tools/judge_all.sh`. Red-team cases: the overhead pose, a fall on the elbow at 2x D1F (judged against
fracture), the smallest section, and the joint bearings, pin and threads (hand calcs on the FE wrench). Results are in
`<design>/judge/fea.json`.

| design | part (mass) | SF D1 | SF D1F | t/2 -> t/3 | d_GH at D1F |
|---|---|---|---|---|---|
| r20 s1414 #4 strap (v5) | base 19.4 g | 6.07 | **4.71** | -11 % | 0.18 mm |
| | link 1 22.4 g (3.0 x 14 strap) | 0.72 | **0.50** | -17 % | 56.7 mm |
| | link 2 22.0 g | 0.73 | **0.50** | -13 % | 58.2 mm |
| | BOTTOM (7075) | not measured: OOM-killed at t/2 and t/2.5 on the shared machine (run at t/1.5 open) | | | |
| r20 #4 f300 (fair links, same BOTTOM) | base 163 g | 5.91 | 4.56 | -18 % | 0.18 mm |
| | link 1 29.4 g | 0.40 | **0.28** | -3 % | 32.3 mm |
| | link 2 49.1 g | 2.09 | 1.47 | -0.3 % | 3.9 mm |
| r18 s1392 f300 (v4, rendered) | base / link 1 / link 2 / BOTTOM | 0.29 / 0.60 / 0.36 / 0.83 | 0.23 / 0.42 / 0.25 / 0.56 | -3 to +5 % | 158.6 mm chain |

- **R9 fails on every champion, by ~3x on the links.** It passes for MVP1: SF 4.7 at the R17 envelope, and 30.9 at the
  measured MVP1 peak (0.162 N.m, 0.24 N). The links are the problem; the r20 base passes at SF 4.7. The r18 base
  fails at SF 0.23 on a 0.82 mm sliver (its smallest section).
- **The failure point is the strap-to-J2-hub junction, not the 3 mm arm.** Both r20 links peak 16-20 mm off the J2 axis
  and 92 mm out along it. That is where the strap climbs ~35 mm, from J1's level (r ~ 62) up to J2's raised plate
  (r 97-104). `judge/fea_sizing.py` scales the real tet10 mesh and solves it again (link 1,
  `cad_r20_n3_s1414_4/judge/fea_sizing_D4-02.json`):
  - Thickening the arm to 1.5x and 1.8x (hub pads unchanged) moves the peak only as t^-0.26 (SF 0.58), but halves
    d_GH (t^-1.5).
  - Widening the whole part, hubs included, scales the peak as w^-1.05: SF 1.06 at 2x and 1.58 at 3x.
  - **So SF 1.5 needs the J2 junction ~2.8x stronger.** Measured upper bound: 2.84x width, 63.5 g per link instead of
    22.4 g, so +41 g per link and +82 g for both. The lightest real fix is local, at the J2 ramp: a gusset plus a
    fillet (L2 CAD), or a lower J2 so the ramp is smaller. It is not yet measured. Keeping the links at 3 mm is
    possible, but only if the junction changes.
  - A radial thickness map is wrong on such ramps: it lengthens them instead of thickening them. The tool now offsets
    along the thickness from the skin side.
- **The joint bearings fail MVP2 by ~9x.** The D1F tilt at a joint is 10 N.m + 50 N x z = 13.1 / 15.0 / 14.1 N.m at
  J1 / J2 / J3 (z = 61 / 101 / 82 mm). On the MR117-2RS pair (pressure centres ~6 mm apart) that is 2.2-2.5 kN per
  bearing against C0 0.28 kN: s0 = 0.11. Needed: C0 x s_eff >= 15 N.m per joint; the pair has 1.7. Under the MVP1
  envelope s0 = 1.11-1.27, which passes, just. The O7 Ti pin root (SF 1.95-2.24), the M7x0.5 ring nut (6.3-7.2) and
  the M18x0.5 cap (> 28) all pass. The r18 v4 joints pass at SF 2.66, because the iglidur thrust washers carry the
  tilt as an O18 annulus (25-30 MPa against 80). MVP2 therefore needs a moment-capable joint: thrust washers or needle
  thrust bearings either side of the boss, as in v4, or a larger-diameter pair.
- **Stiffness binds harder than strength.** At D1F the r20 strap chain's d_GH is 115 mm (base plus two links) against
  the 2 mm floor. Even at the measured MVP1 peak it is 1.87 mm, against the 2.66 mm minimum skin gap. Thickening the
  arm 1.8x gives 23.6 mm per link. No skin-hugging section reaches 2 mm at 10 N.m: a 20 x 8 x 1.2 closed box is ~15x
  stiffer than the 14 x 3 strap (analytic), and ~50x is needed. Either the MVP2 deflection rule is judged at the MVP1
  loads (user decision), or MVP2 needs a different load path.
- Red team, other cases:
  - **Overhead**: covered by the worst-direction envelope. In a serial spherical chain every member carries the same
    end wrench about GH; a pose only turns it in the part frame.
  - **The 10 N.m load is ~70 % of this user's full arm gravity** (13.8 N.m, de Leva 1996, 85 kg). Full support would
    scale every stress by 1.38.
  - **Fall on the elbow (2x D1F)**: SF 0.27 against fracture on the r20 links, 2.5 on the base.
  - **Smallest section**: the 0.5-1.5 mm walls (edge features) are at SF >= 3.5, so they do not govern.
  - **Scapula handler interface**: it must carry 13.3 N.m + 50 N at the base tab.
- Mesh convergence: from t/2 to t/3 the judged peaks fall by 0.3-18 %. The judged value keeps the coarse (higher)
  number, so the reported SFs are conservative by up to 18 %.
- Infrastructure:
  - BOTTOM (~140k nodes at t/2) is OOM-killed while a dozen agents share 16 GB. It is now meshed coarser
    (`FEA_K0_BOTTOM`, default t/2.5), with t/3 only within 30 mm of the peak.
  - ccx's ITERATIVE CHOLESKY was tried and did not converge (870 iterations on the validation beam).
  - One failing part no longer loses the others (`parts_failed`, `complete = False`).

## Unpowered tracking (MVP1) needs exactly 3 DOF (judge/dynamics.py, MuJoCo, 2026-10-15)

- The arm drives the chain through the cuff (soft-tissue stiffness, Schiebl et al. 2025), joint friction load-
  dependent, links with their real mass and inertia. Validated (judge/test_dynamics.py): single-hinge analytic cases
  exact; vs transmission.py (quasi-static) median 0.09 %, max 0.75 %; vs rt_wedge.py's self-locking onset within
  0.2 s in 8 of 10 cases. MuJoCo's default friction is a damper at low speed (0.0019 vs 0.2 N.m at 0.01 rad/s): the
  judge turns on the exact setting - any other MuJoCo friction work here needs it too.
- Rolling bearings (mu 0.005), real speed / 2x: **band_r14_3r_s1351_1 moves freely** - 0.05 / 0.10 N.m about the
  shoulder, 0.2 / 0.4 N at the cuff, 1.2 / 1.8 deg cuff twist, links never touch (20x under the proposed 1 N.m).
  **Both 4R designs fail unpowered for kinematic reasons:** the spare joint has nothing holding it - it falls under the
  links' weight within 0.1 s and drifts 10-37 deg with gravity off, so R1/R2/R6 score a configuration these chains
  never take; the reference folds l2 into l3 (needs 2.3 N.m, 121 N link contact). -> for an unpowered tracker 3 DOF is
  not only the user's preference but required (or a detent / spring / motor per spare joint).
- Plain bearings (3R): mu 0.15 -> 0.64 N.m but ~8 deg cuff twist; 0.25 -> near-lock in Wash opposite shoulder; 0.37
  (worn sleeve carrying the tilt) -> 2-4 clips lock and stay locked. Cuff twist (0.03 N.m/deg torsion) is the weak
  point under friction. Cuff pressure is far below the all-day budget (worst 1.8 kPa vs 7.5 kPa for the exo).

## Range first: the search finds stand-off designs (r17 / r18, 2026-10-15)

- Scoring range first (score x min(1, workspace share / 0.9)^4, functional workspace) trades closeness for range:
  the detail evals (15 deg functional grid, 1432 poses) run from 74 % of the workspace at 18 % in band (14 mm) to 45 %
  of the workspace at 62 % in band. No design reaches the 90 % range target.
- The two widest-range designs (r18 s1394 #1, s1392 #0: 73-74 % of the workspace, Raise overhead followed 100 %)
  get there by holding the last joint in the air: J3 at 248 / 275 mm from GH with its hub plane 169 mm above its
  skin need. The fair CAD builder then twists link 2 (a valid but self-intersecting shell, 0.52 cm3, -1.64 cm3 after
  features; reported as 1118 g). These are not close-fitting designs; `fair_build.py` now flags a hub > 25 mm over
  its need (STANDOFF_MM) and a non-positive solid volume. A compact design (J3 within ~100 mm of GH) costs about 2-3
  points of workspace (r18 s1394 #0: 72 %, 29 % in band).
- The workspace losses of the compact designs are mostly skin (the shape under the links sits above the skin in
  12-31 % of poses) and squeeze (9-19 %), not kinematics (5-15 %): range has to come from the shape and the link
  routing, not from more joints.
- **Joint size is worth ~20 points of workspace.** The five best compact hub_r 8.5 (O17) designs re-evaluated at
  hub_r 11.5 (O23, the v4 / v5 joint the CAD builds): 69-75 % -> 47-53 % of the workspace (r19 s1403 #3: 74.9 % at
  24 % in band -> 53.1 % at 52 % in band), almost all of it lost to skin under the larger hubs. The CAD builder
  always uses the O23 joint (members.HUB_R, joint_v4.py), so an 8.5 eval does not describe its CAD. A O17 joint needs
  a smaller bearing stack (e.g. HK0810 needles, O12, or a 6700 at O15 with a 1 mm wall) - a joint-design task, the
  next lever for range.

## Measurement fixes found by the proximity agent (2026-10-15 midday)

- **Skin-map holes over the top of the shoulder (evaluator).** The band evaluator's 0.5 deg skin maps leave 9 / 21 / 38 /
  58 / 87 % of the pixels at latitude 40 / 60 / 70 / 80 / 88 deg empty (r1 = 0: no clearance constraint, never in band),
  though exact ray casts hit skin 40-70 mm out in every checked hole. Fill (`fill_holes` job key,
  pipeline/conformal/analysis/band_impl_fill_holes.patch) agrees with the ray casts to ~1 mm. Effect on the final's
  evaluator in-band: 58.6 -> 67.5 % (clips, CPU) - a measurement change; the R1 judge (score_design.py, exact skin) was
  never affected.
- **Held-out leak in the CAD stage.** `fair_cad/envelope.py` shaped the links over every followed clip frame, Wave and
  Walking arm swing included (16 % of the final's too-far skin was held up by Wave frames). Fixed: held-out motions
  (data/raw/split.json) no longer shape the CAD (`ENV_ALL_CLIPS=1` restores the old envelope). Designs built before
  this fix were (slightly) fitted to the held-out clips.

## What blocks the range (range agent, 2026-10-15 midday; analysis/why_held.py, ws_collisions.py, judge/workspace.py)

- **Every held clip frame of the final 3R is a shape problem, not kinematics.** `analysis/why_held.py` re-runs the
  evaluator on CPU with per-constraint hooks (band_impl exec'd with stash lines; the DETAIL result's own shape imposed:
  agrees with the GPU on 100 % of the 451 clip frames). The chain closes in every clip frame with >= 25 deg to its J2
  fold limit (J1-J3 39.5..101 deg, allowed 14..149). Measured on the maps before fill_holes:
  - Raise overhead, 142-150 deg (19 of 61 frames): link 1's J2 hub (2.7-6.7 mm) and its ribbon near J1 (0.4-1.9 mm)
    under the trunk skin; the J2 hub lands on the back over the medial scapula (rest position [-83, 9, -40]), the
    ribbon on top of the acromion. At 149.9-150 deg the base's mounting tab (mount_dir [0, 0.6, -0.8], medial toward
    the neck) is also 34.6 mm in the trapezius; turned 30 deg posterior it clears every clip frame (`tab_dirs.py`).
    Following overhead on this chain costs stand-off: the shape refitted with a wide band (`follow_first.py`, CPU
    clips) follows Raise overhead 100 % with the J2 hub face 27 mm higher, in-band (14 mm) 58.6 -> 31.4 %. The r20
    chains (O20 hubs) follow it 100 % without that.
  - Reach back pocket (28 of 49): link 2's ribbon 3-20 mm under the arm skin and, in most frames, also above a
    re-entry sheet (squeeze): it is routed between the arm and the trunk, no underside height fits (routing problem).
  - Wave (held-out, 30 of 58): link 1's J2 hub up to 57 mm and link 2's J2 hub up to 49 mm inside the arm.
- **The CAD follows 3.4 points less than the evaluator because of the hold-resume rule**: a held clip resumes only
  when the wanted pose comes back within RESUME = 4 deg of the held pose in every coordinate, and Reach back pocket's
  return path never does (eval-feasible 42.9 % of its frames, CAD 22.4 %; Wave 48.3 -> 39.7 %). A resume rule based
  on reachability would be a measurement change of R3 - not made.
- **R16 was half a CAD bug.** In every hub-arm-end fair CAD so far (the rendered final included) the JN joint hardware
  (washers A / B, magnet, ring nut) was returned in the canonical humerus frame under group H (the rest frame): 12.2 deg
  (HR) off the J3 axis, ~10-20 mm beside the joint. And the neck root climbed to 93.1 mm inside link 2's plate radius
  (seat plane S 92.32, link 2's underside 92.47). Fixed in `armend_fair.py` (hardware converted like the BOTTOM merge;
  the neck runs level under S until its section is 12 mm from the axis; exit +7 deg, NECK_GAP 60 - the +27 deg exit
  folded every loft with the level run): **R16 46.7 -> 78.3 %** (part interference 50.8 -> 14.2 %, agreement with
  the evaluator 72 -> 90 %), same links (`cad_r18_n3_s1392_1_c1`). The 3 evaluator-feasible poses still failing:
  the JN hub's turned skin side 0.5-1.1 mm in the arm at elevation 90-165 (fitted to the clip frames only;
  `armend_fair.WorkspaceSkin` adds the workspace poses, not yet built).
- **Link N-1 turns through every direction about JN over the functional workspace** (30 deg bins 116 / 172 / 347 / 340
  / 160 / 80 / 18 / 18 / 12 / 18 / 34 / 74 of 1432 poses), so no neck exit clears it: the arm-fixed neck climbs from
  the JN hub (85.8 mm from GH) to the bar (underside 96.4) through link 2's plate level. On the r20 picks every
  evaluator part collision over the workspace (14.2 % of the poses on s1414 #0) is 'link 2 - neck'
  (`ws_collisions.py`). The fix is the stacking order at JN: link N-1 under the arm hub (key `jn_low: link`,
  band-2026-10-15m) AND a neck that bridges link N-1 instead of dipping to the skin (v2 patch,
  analysis/jn_flip_band_impl_v2.diff): 14.2 -> 0.0 % of the poses collide; v1 alone changed in-band only
  (+0.8..1.6 points, GPU) and no workspace share. CAD side: `armend_fair.build_hub_neck_upper` (needs fair_build
  role / joint_lv for link N-1).

## Infrastructure

- RunPod Flash endpoints: band evaluator `exo-band10` (5ogdx1ex9wyh02), Blender Cycles render `exo-blender-cycles`
  (dj3qfmtwrwy2pr). Warm workers serve old code after a deploy -> new endpoint name per code change, check
  CODE_VERSION. Queued jobs may need `workersMin` PATCHed > 0 to start; reset to 0 after. Account quota 10 workers.
- The dense per-frame skin maps (`.cache/maps_s1.pt`, 857 MB) are not in git: `tools/build_maps.py`.
- **The contact judges over-reported - fixed 2026-10-15 (judge/sdist.py, judge/test_sdist.py).** The old sign came from
  the face normal of the nearest of 10 triangle centroids; on long glb facets and the coarse body mesh (median edge
  8 mm, max 87 mm) the true closest triangle was often not among them (e.g. "link 2 IN J2 cap" 4.78 mm where ray parity
  in 3 directions and the winding number find 0 points inside), and the posed body self-intersects (winding up to 3)
  where no normal-based sign exists. Now: exact closest point (covering samples + one ball query) and the integer
  winding number (scanline grid + segment crossings). Test vs brute force: wrong inside 0 % on cube, sphere, a real
  part and the posed body (old: 0 / 0 / 2.6 / 2.8 %), |d| error 0. **Measurement change** on the reference
  (cad_r13_n4_s1343_1): R6 37.64 -> 0.80 mm (15 pairs > 0.15 mm), R2 24.43 -> 24.62 mm (the user's forearm cuff vs the
  rig's forearm: a size mismatch, not exo metal).

## Proximity atlas: the shoulder cap moves with a graded fraction of the arm's swing (2026-10-15)

`tools/proximity_atlas.py`, docs/research/proximity_atlas.md. From the raw posed skin alone (no mechanism), the share
of fit-clip poses a rigid point can sit 2-14 mm from the skin while clear in every pose. It **predicts the champion 3R
(in-band 0.24 predicted vs 0.23 measured with every part clear)** and names the cause: its link 2 has ceiling 0.04 (the
skin under it moves 40 mm). Over the lateral / superior cap, scapula-fixed metal can stay in band over 27 % of
directions; metal that rotates by the region's own fraction of the arm's swing (no twist) over 54 % (mean ceiling 0.30
-> 0.70). The fractions are bimodal: ~0-0.2 over the top, ~0.7-0.9 over the deltoid. Design rule: pieces over the cap
must turn by graded fractions of the swing (pauldron lames, spherical lazy tongs, rolling / CV couplings), and the
humeral twist belongs below the cap.

## The baseline bar is soft: the same 3R scores 65.05 with honest flat hubs (2026-10-15, kit verification)

The shared modelling kit (tools/concept_kit.py, docs/concepts/KIT.md, verified: 22 tests, K1 closure on 120k cases)
reproduces the baseline row exactly (gap 68.93). Built on the kit's own conventions - flat O20 hubs fitted by a
true-offset march, 12 x 3 mm straps with the 60 deg climb limit, the K7 neck, every part clear in every pose (q 1.0),
dense branch continuity, part-part collisions - the SAME champion kinematics score **gap 65.05**
(docs/concepts/models/_template.py). With the kit's stricter K3 radius but the baseline's cap hubs it scores 70.27
(a measurement change). So a morphology must beat **~65**, not 68.93, before it beats the 3R family; screened rows
below 68.93 are compared against both numbers. Models built on kit flat hubs before the K4 fix (commit 03bb5bf)
must be re-measured.

## The champion's axes were not optimal: the 3R scores 51.97 at axes a rail concept's CMA found (2026-10-15, rail-elbow stage 1)

A farm CMA-ES of rail-elbow (`tools/concept_cma.py`, 1410 tries, converged by the gate) moved it from 63.72 to 57.19.
The rail stages stayed 0 % in band through all of it; the whole gain was the arm end (hub 3 0.36 -> 0.75, neck
0.51 -> 0.68). The in-model control settles where that gain lives:
* The plain spherical 3R with honest flat O20 hubs (`docs/concepts/models/_template.py`, q 1.0, dense K2, K6), at the
  same axes, scores **51.97** (score 81.1). At the champion's axes it scores 65.05, on the same bench and checks.
  - Axes: b az 0.65 el 76.82, a1 80.71, a2 62.93, W (93.82, -4.20), sigma -1.
  - reach 0.888, follow 1.0, in-band 14 0.393, contact 0.
* At every rail-elbow axis set the hub beats the rail by 4-5 points.
* On the large bench (Bench(110,360), exact, 1 mm radial, geometry frozen from (60,160)), the 3R at these axes scores
  **60.03**. The champion scores 75.94 and the rail-elbow 64.52 at the same axes.
* At the rail's other basin (k2221), the 3R scores 51.33 on Bench(60,160).
* Two lessons:
  - A concept's bench gain must be checked against the champion topology at the concept's own axes before it is
    credited to the morphology.
  - The 3R family itself has at least 13 points (gap) left in the axis choice.
* MVP1 rule hit by the concept: a 2-stage telescopic rail needs a synchronising 2:1 drive (cable loop, rack, or a
  creeping roller cage). The first two are forbidden in MVP1; a floating stage is an undriven coordinate (R17).
  - The legal rigid rail at the same axes needs 209 mm.
  - Its own CMA shrinks the rail into a 21 mm ring around the J2 axis, which is a hub.
  - docs/concepts/rail-elbow.md, "Convergence and red team".

## Built and judged: the 3R at the CMA's axes beats the built champion on R1; the rail loses 11 points (2026-10-16, rail-elbow stage 2)

* `pipeline/concept_l1/build_kit_l1.py` (new) turns any concept-kit model configuration into a judge-ready L1 design
  dir, from the model's own fitted samples. The kinematics are reproduced exactly: the model's metal vs the posed
  exo.glb is within 0.15 mm, and `judge/dynamics.py` ik_check reads 0.000 deg.
* Outside judges (`judge_all.sh fast` on the farm) against the built champion `param_r20_n3_s1414_4`:
  - `l1_3r-k2221` (plain 3R at rail-elbow k2221's axes): R1 **56.1 %** vs 54.1 %, R1-aim **27.6 %** vs 23.0 %,
    overhead 48.2 vs 48.7 %. It is the first concept-bench design to beat the built champion on proximity.
  - `l1_rail-elbow` (k2221): R1 44.9 %, overhead 33.4 %. The rail parts ride 127-148 mm from GH.
* Red team from the CAD: the telescopic stages were fitted at different radii (stage 1 at 143 mm, stage 2 at 127 mm).
  That is an 11 mm gap with nothing in the model carrying stage 2.
* Limiter on both built designs: the kit's J3 hub zone. The 6 mm neck starts at plate level F inside the J3
  footprint and overlaps the upper boss by 2.85 mm. The upper strap passes over the neck inside the zone the kit
  exempts from K6 and `over`. Ramps compare a radial distance with a flat plate's axial level (0.46 mm into the
  plate). This flaw sets R6 at 2.85 mm and fails about 107 of 120 judged workspace poses on parts (R16 39-46 %).
  The fix goes into tools/concept_kit.py, so it reaches every model.
* docs/concepts/rail-elbow.md, "Stage 2".

## The J2 fold is not a hard limit: 50 / 50 deg arcs can keep 96 % of the workspace fold-free (2026-10-16, fold frontier)

Every 3R chain that reproduces the arm's rotation folds when the angle between the scapula-fixed J1 axis and the
humerus-fixed J3 axis leaves the band [|a1 - a2| + 10, min(a1 + a2, 360 - a1 - a2) - 10] deg. Orientation depends on
the axis directions only, so this bounds reach for every 3R morphology, offset axes and cuff slides included.
`tools/fold_frontier.py` scans J1 = bvec(az, el) x J3 = wdir(wd, wa) on a 6 / 4 / 5 / 6 deg grid against the 160
workspace poses and 60 clip frames of Bench(60,160). It writes `docs/research/fold/frontier.json`. Results (best layout per
a1 + a2, all clip frames in band):

| a1 + a2 | arcs | workspace in band | J1 | J3 |
|---|---|---|---|---|
| 75 | 35 / 40 | 0.762 | bvec(120, 16) | wdir(70, -6) |
| 90 | 45 / 45 | 0.938 | bvec(132, 16) | wdir(70, 24) |
| 100 | 50 / 50 | 0.963 | bvec(132, 16) | wdir(75, 24) |
| 110 | 50 / 60 | 0.969 | bvec(120, 28) | wdir(70, 6) |
| 150 | 65 / 85 | 0.994 | bvec(-48, 20) | wdir(125, 60) |
| 165 | 80 / 85 | 1.000 | bvec(-180, 16) | wdir(30, -48) |

The measured leaders sit far inside this frontier:
- offset-skin-normal-3r k4216: band 44-104 deg, reach 0.706.
- skin-normal-hubs: reach 0.656.
- The champion: arcs 77 / 67, reach 0.775.

Their fold losses come from the axis layout the proximity terms pulled them to, not from a limit of the 3R. Short arcs
(45-50 deg) make links short, which suits the band. The fold-free layouts point J1 anterolateral and nearly horizontal
(bvec az 108-138, el 16-28: the front of the acromion), and J3 roughly radial on the arm (wd 55-85).

Open question, now under test: can hubs on those rays stay within 14 mm?
- The anterior deltoid moves under a scapula-fixed hub 1.
- docs/research/proximity_atlas.md says where rigid metal can live.

Seeds for every 3R search come from frontier.json (the template's az / el / a1 / a2 / wd / wa map 1:1).

## On a GH-ray-hub 3R, the fold frontier trades fold for skin: J1 cannot be both fold-free and in band (2026-10-16, osn fold seeds)

offset-skin-normal-3r was re-seeded from the fold frontier. Its J1 and J2 are hubs on GH rays (the 2-slide closure
theorem). Seeds came from `tools/osn_fold_seeds.py`, then six CMA streams ran on the farm; 5346 new tries, all on
Bench(60,160) fast with every model check on.

* **Seeds lose to skin.** The fold-free layouts cut fold losses from 47 to 5-15 poses. Skin losses rose from 2 to
  34-73. The best of 144 frontier seeds scored 83.95; the best of 32 joint-frontier seeds 72.82.
* **CMA returns to k4216.** All six CMA streams went back to the k4216 basin: J1 bvec(95-106, 63-66). The two frontier
  starts climbed from J1 elevation 32 back to 63-66. The best stays 32.61 (42.59 frozen on Bench(110,360) exact). The
  whole-history gate passes (9869 tries).
* **Mechanism: hub-1 band map** (`tools/fold_rayblock.py` -> docs/research/fold/rayblock.json). A 20 mm hub disc on
  each J1 ray, with the height each of 220 poses needs. On k4216's J1 bvec(96, 64), one hub height keeps 98 % of poses
  in band (90 % overhead). On the frontier's J1 bvec(132, 16), only 69 % (2 % overhead): the hub must rise p90 44 mm,
  max 124 mm, because the anterior deltoid and the elevated arm rise under the front of the acromion.
* **Joint frontier: the problem moves to hub 2.** Fold-free and hub-1 band together peak at J1 bvec(120, 60), arcs
  60-65: fold-free 0.96, hub-1 band 0.93. Hub 2 rides on link 1 and then swings over the abducted, externally rotated
  arm (31.8 mm, 2-5 % in band).
* **The fold limit and the band limit pull J1 in opposite directions.** The band limit puts J1 up over the acromion
  (el 60-66); the fold frontier wants el 16-36. The bench's own metric prefers 47 fold poses with both hubs in band to
  8 fold poses with the hubs 25-32 mm up.

What this predicts: a 3R that puts J1 / J2 metal on their own axes (any spherical or GH-ray hub chain, the champion
included) cannot use the fold frontier on this body. The lever left is a morphology that rotates about the J2 GH ray
without metal on it: an arc guide or remote-centre carriage whose track follows the skin on the J2 circle.
Offsetting J1 / J2 off GH needs a third (radial) slide, which would make 3 passive translations: not allowed.

## The fold frontier does not seed a concurrent 3R: its axes run inside the arm and the trunk (2026-10-16, fold-sph3r)

The plain spherical 3R (three O20 bearing hubs, axes through GH, 0 passive translations, no cuff slide) was re-seeded
from every frontier.json layout with a1 + a2 85-140 (792 configurations, both branches, farm) and tuned by 6 farm
CMA-ES streams (4790 tries, gate converged). Bench(60,160), fast grid, kit checks plus a new hub crown / wall check;
docs/concepts/fold-sph3r.md.

* **The frontier's layouts score 74.4-170 (median 118).** The 3R at known axes scores 51.33.
  - Reach mostly survives: 0.925 for the best seed against the frontier's 0.95.
  - Proximity does not: hub 1 and hub 2 are 0 % in band, and 80 % of the configurations put the links beyond 150 mm.
* **Why (tools/fold_parking.py -> docs/research/fold/hub_parking.json).** To keep the J1-J3 angle in band, J1 must
  point near the middle of the humerus's workspace cone, which is where the arm passes.
  - Overhead, the frontier's anterolateral J1 lies within 9-16 deg of the humerus axis, inside the arm.
  - The J1 ray never clears the skin in some closing pose for 39 % of the layouts with J1 el 16-33.
  - The J2 ray never clears (it runs into the trunk) in 26-39 % of the layouts at any J1 elevation.
  - The fold frontier must be intersected with hub parking before it seeds a concurrent morphology.
* **CMA walks every frontier start back to J1 over the acromion** (el 37-79): 59.3 and 59.6 from the frontier
  starts. The best results came from the known basin:
  - **49.03** at q 1.0 (score 82.2, near-touch clean, min metal 1.37 mm);
  - 44.72 at q 0.98 (score 83.7). That shape puts metal 0.00-0.9 mm from the skin in 8 poses; counting < 1 mm as
    contact gives 53.66.

  This is the best plain spherical 3R so far. The 2-slide osn leader is 32.61 fast / 42.59 verified.
* **Limiter of the concurrent 3R (every axis set):**
  - Hub 2 is 0 % in band (F 145-154 mm, posterolateral horizontal).
  - Link 2 is 5-10 % in band (median 116 mm).
  - Overhead reach is 0.42-0.50.
  - With zero slides every axis must pass through GH (the osn closure theorem with no slide), so nothing is left to
    tune. The cheapest way out is the osn one: an offset, skin-normal J3 with 2 cuff slides.
* **Measurement finding.** The kit fits and scores only each hub's skin face. In 47 % of the frontier configurations
  a hub crown or wall (F .. F + 12.25) was inside the skin in some taken pose, although every face was clear. On the
  big bench every axis set has 2-3 such poses. Models that use `K.hub_member` should add the crown check
  (`crown_points` in docs/concepts/models/fold-sph3r.py). At the known 3R axes with q 1.0 it changes nothing on
  Bench(60,160); the crowns clear by 1.4-3.5 mm.
* Frozen on Bench(110,360) exact (lesson c), against 51.33 / 51.97 fast:
  - 3R at k2221's axes: **57.99**;
  - 3R at k1530's axes: 60.03, which reproduces the earlier verifier's number;
  - best frontier seed: 78.11;
  - CMA bests: queued on the farm.

## Raglan routing and far-end hubs: a tailor's two levers, measured (2026-10-16, raglan-routed-3r / raglan-knee-3r / far-end-posterior-3r)

* **Raglan map** (new instrument, `map` mode of docs/concepts/models/raglan-routed-3r.py and raglan-knee-3r.py): for
  every direction of a link's OWN moving frame (t along the link, d off its great circle), the sphere-traced need over
  every pose the chain takes and the share of poses one height keeps in 2-14 mm. The skin-motion map in the link frame.
* **On the plain 3R it is a real lever**: the straight link 1 crosses the posterior acromion edge; one 38 deg planform
  turn (two straight legs + a tangent arc, constant 8 x 3 section) keeps it over skin that rides with it. Link 1
  0.36 -> 0.60 in band; 51.33 -> 42.72 fast (CMA gate converged, 4396 tries) and **50.06 frozen on Bench(110,360)
  exact** against 57.99 for straight links at k2221's axes: the best plain spherical 3R with no passive DOF at all.
* **On the leader it is not**: at the pin knee / osn k4216 seats the map's argmax IS the great circle for both links
  (link 1 ceiling 0.99-1.00 over d -20..+10, link 2 peaks at d 0); the leader's 9869-try CMA had already found seats
  whose straight links are raglan lines. Link-2 turns all lose (parts collisions at the knee / pad, deltoid end).
* **In-band dilution (red team)**: in-band 14 is a share of metal SAMPLES, so extra metal that sits in band lowers the
  gap without moving any part closer. A 114 deg hairpin in link 1 (36 -> 84 samples, +~9 g) takes the pin knee from
  26.34 to 24.79 fast (score 90.99), but weighted at the straight sample count it is 25.89: +0.45 real, +1.1 dilution;
  worn frozen on Bench(110,360) exact 32.33 (33.41 at fixed sizes) vs the pin knee's 33.84.
  CMA over seats + routes then finds **23.00 fast / 31.52 frozen exact** (32.11 at fixed sizes; in-band 0.902 meets
  its target): J3 3.3 deg more proximal brings hub 3 / the knee into band (same seats, straight links: 24.49 fast). The
  remaining 30 points are reach, i.e. the J2 fold.
  On the plain 3R the same check gives 43.97 instead of 42.72 (mostly real). Every in-band claim should be re-scored at
  fixed part sizes (raglan-knee-3r reports `gap_fixed_n`); a CMA on the bench gap will chase the artefact (annular-ring
  skirt, docs/concepts/annular-ring-3r.md, is the same thing).
* **Far-end hubs** (a revolute axis is a line; the bearing may sit at either end): kinematically free, but on this body
  the far end of every GH line we can use lies in the torso, axilla, neck or chest wall - all 8 end choices worse on the
  plain 3R (far-end-posterior-3r, 256 configs).
* **Posterior J1 line** (bvec(-24, 4), fold-free on 100 % of poses with hub 1 in one band): dead in both families - the
  plain 3R (best honest 118.55) and the pin-knee family (64 layouts, best 122.45: fold 6-20 poses instead of 47, but
  46-69 skin poses of 220; which part hits was not split per part here, the plain-3R raglan map puts the link rays over the neck and chest). The fold-free posterior layout moves the poses from
  the fold column to the skin column.
* **Farm detail that wasted a round**: `tools/cloud_run.py batch` jobs must carry `"link": [".cache/concept_bench"]`
  (`sweep` adds it): without it the bench runs the exact path, a pin-knee CMA generation takes 660-1060 s instead of
  ~20 s, and the gaps are not comparable with fast-grid ones (49.89 exact vs 46.74 fast at the same configuration).

## The R6 judge was optimistic: it tested only vertices, on every 12th frame (2026-10-16, judge/part_contact.py)

* **What failed.** R6 tested only the vertices of part A inside part B. In fast mode it used every other vertex on every
  12th frame; the full run used step 4. When two thin plates cross at their edges, no vertex of one lies inside the
  other.
  - On the first build of l1_offset-skin-normal-3r (git 06b5a59) the judge scored 0.0 mm.
  - The verifier's dense check found link 2 1.12 mm inside the J3 plate (VERIFY.md).
  - Re-measured at step 1 with the new judge: link 2 sits 1.07 mm inside the J3 plate at every frame (a fixed overlap
    at the joint). Link 1 and link 2 cross by 0.66 mm for 9 frames (Wave 71-79 and 95-103) and by 0.59 mm over Raise
    overhead 35-145.
  - The old vertex-only test reads 0.00 mm at those frames. The final build is 0.00 mm at all 1337 frames.
* **Fix: dense surface samples, both ways, with the same exact depth.** For each part, cached in its own frame:
  - every vertex;
  - points along every sharp or open edge, at most 0.5 mm apart;
  - every face, bisected until no edge is longer than 1.0 mm.

  Inside = sdist's integer winding number. Depth = libigl's exact AABB closest point. Every speed-up is exact, and
  judge/test_part_contact.py checks the fast path point by point against sdist's Mesh.max_depth.
  - Cost: 13.5 s of CPU per frame for the first dense version, now 0.06-0.2 s on L1 designs and 0.6-2 s on user-style
    CADs with many hardware parts.
  - tools/judge_all.sh now runs R6 on every frame, and on every 3rd frame in fast mode (it was 4 / 12). At 30 fps, a
    crossing that lasts 3 frames (0.1 s) is always sampled.
* **A second fault: inverted meshes.** The band_* D4 member proxies have inverted or inconsistently wound bodies (all
  bodies at negative volume). The grid winding number takes its sign from the face normals, so it put a vertex
  3.44 mm "inside" a member where the generalized winding number is 0.07.
  - weld() now re-orients each closed body outward. The geometry does not change, and part_contact.json lists the
    re-oriented parts.
  - No other judged design has such a part.
* **Re-judged at step 1** (the full judge; 12 designs on the farm, ~$0.45; the 3 band designs locally):

| design | R6 old (step) | R6 new | why it moved |
|---|---|---|---|
| l1_offset-skin-normal-3r | 0.00 (12) | **0.00 PASS** | true at all 1337 frames |
| param_r20_n3_s1414_4 (user-style 3R, D5 drawings) | 1.03 (12) | **3.50** | link 2 strap 3.5 mm inside the arm end's J3 pad at every frame; vertex-only reads 0.00 (pure edge crossing) |
| param2_r20_n3_s1414_4 | 4.38 (4) | 4.65 | upper-arm cuff in forearm cuff (Drink 69) |
| l1_seed-offset-3r-slides | 0.81 (12) | 1.50 | link 2 strap in J3 plate (as osn's first build) |
| band_r16_3r_s1373_1 | 0.72 (12) | 1.48 | l1 / l2 members, 183 frames; re-oriented proxies |
| band_r14_4r_s1354_0 | 2.00 (4) | 2.69 | l2 / l3 members, 101 frames; re-oriented proxies |
| band_r14_3r_s1351_1 | 1.09 (4) | 1.09 | unchanged |
| cad_r13_n4_s1343_1 | 0.80 (4) | 0.85 | J4 ring nut in J4 cap |
| cad_r18_n3_s1392_1 / _f300 | 0.29 (12) | 0.30 | link 2 vs BOTTOM, J3 washer vs link 2 |
| l1_3r-k2221, l1_rail-elbow | 2.85 (12) | 2.86 | link 2 strap / neck |
| cad_r13_n3_s1331_0 | 90.07 (12) | 0.25 | stale file from before the 2026-10-15 sdist fix (old sign rule) |
| l1_3r_offset | 50.84 (12) | 2.73 | stale, before the sdist fix: 50.8 mm cannot fit in a 5.5 mm slab |
| l1_r14_3r_s1351_1 | 11.09 (12) | 2.67 | stale, before the sdist fix: brute force finds 2.16 at Wave 36, where the old file said 11.09 |

* **No status flips.** Every design that failed R6 still fails, and the leader still passes, so no pass count moves.
  Only the R6 rows of the scorecards were patched; the other rows were left as judged.
* **For the design loop:**
  - The user-style 3R (param_r20, the D5 drawings) needs its link 2 strap / arm-end J3 pad overlap fixed: 3.5 mm at
    every pose.
  - Seed-offset and the osn first build show that a link strap ending on the next hub's plate is the recurring
    pattern. The L1 builders should end straps on the plate's top face, not through it.

## R6 now uses open parts as containers too; the D6 cuff overlap, located (2026-10-16, judge/part_contact.py)

* **The blind spot.** `pair_ok()` never used a part as the container B unless its mesh was watertight after `weld()`.
  So a pin fully embedded in a link with a meshing crack could not be seen. Six judged design dirs had such parts:
  - mesh cracks and T-junctions in D5-02 link 1, D6-03 link 2, D7-03 link 2 and the cad_r13 BOTTOM part;
  - the RSR3R3 rails, which trimesh calls open only because 6 edges are shared by 4 faces.
* **The fix keeps the exact path.** `close_open()` closes the mesh's oriented surface:
  - The boundary is every directed edge whose reverse is missing.
  - Each boundary loop gets a cap, built by ear clipping on the shortest diagonal. The cap's edges cancel the boundary,
    so the integer winding number and the exact libigl depth apply unchanged.
  - A mesh that still does not close falls back to libigl's generalized winding number, |w| > 0.5.
  - `part_contact.json` now has an `open_parts` key listing how each part was closed and the cap's size.

  The caps:

  | part | cap | cap area | max cap distance from the open mesh | what the hole is |
  |---|---|---|---|---|
  | D5-02 | 6 triangles | 0.15 mm² | 0.02 mm | T-junction cracks |
  | D6-03 | 186 triangles | 3.76 mm² | 0.46 mm | two 2.4 x 1.3 mm holes, top face, where the bent bar meets the J2 and J3 hubs |
  | D7-03 | 15 triangles | 0.009 mm² | 0.0004 mm | cracks |
  | cad_r13 BOTTOM | 9 triangles | 1.56 mm² | 0.11 mm | one hole |
  | rails | none | - | - | already closed |

  The D6-03 holes come from the mesh export. The STEP solid is valid, and so is the user's Onshape model.
* **Checked against an independent method.** We compared the capped winding number with the generalized winding number
  of the uncapped (open) mesh:
  - On ~35 000 random points deeper than 0.15 mm per part (D5-02, D6-03, D7-03, rails): 0 disagreements.
  - At cad_r13's two worst frames: 0 disagreements, and w = 1.00 at the deepest point, 60 mm from the cap.
  - The quick suite has a new case 4 (1.6 s): a pin fully inside a slab with T-junction cracks or a hole. Both the
    cap and the GWN fallback catch it at exactly 3.000 mm. A pad 0.5 mm above the hole stays clean.
  - The full suite passes.
* **Re-judged at step 1 on the farm** (8 jobs, ~$0.18):

  | design | R6 before | R6 now | what the blind spot hid |
  |---|---|---|---|
  | param_r20_n3_s1414_4 (D5) | 3.50 | 3.50 | base and link 2 3.50 mm inside link 1 at every frame (seen before only the other way round, at 1.44 / 1.48) |
  | param2_r20_n3_s1414_4 (D6) | 4.65 | 4.65 | nothing: no part inside D6-03 link 2 at any depth > 0 (every 3rd frame) nor > 0.15 mm (all 1337 frames) |
  | cad_r13_n3_s1331_0 | 0.25 | **0.55** | the flank liner 0.55 mm inside the BOTTOM + dovetail rail part, 347 frames (Wash opposite shoulder 192) |
  | user_osn_k4216 (gen-2 final) | 0.85 (step 3) | 0.85 | nothing new |
  | dropped gen-2 builds v2 / v3 / v4 | 4.65 / 4.65 / - | 4.65 / 4.65 / 1.10 | nothing new inside D7-03 link 2 or the rails |

  No status flips. Only cad_r13's R6 value changed in the scorecards.
* **The D6 overlap: the upper-arm cuff against the user's forearm cuff** (param2_r20, 1337 frames). The UPPER ARM
  CUFF here is the project's U cuff (`user_style.upper_cuff`):
  - It spans s 83.85 (elbow end) to s 164.65 along BOTTOM, measured from the elbow axis.
  - Its side arcs are R50 and wrap 110 deg.
  - The overlap is 4.65 mm deep. The forearm cuff's edge also passes right through the upper cuff's 2 mm wall
    (1.00 mm = half the wall).
  - It happens only in deep elbow flexion: Drink from a cup frames 36-145, Comb hair 40-163, Wash opposite shoulder
    41-152 (346 frames).
  - The worst frame is Drink from a cup 69, with the elbow rotated 116 deg from the clip's first frame.
  - Location: only on the -vB (anterior) side arc, never on the flat land. It runs from the elbow end to s 139.1, the
    distal 55 mm of the 80.8 mm cuff, and from 19.1 deg of wrap to the tip at 110 deg.
  - Deeper than 3 mm: s 83.9-117.4, wrap 24.5-56.5 deg. The deepest point is 5 mm from the elbow end (s 89.0), at
    32 deg of wrap.
* **The cut that removes it:**
  - Trim the -vB arc to <= 19 deg of wrap. The inner arc goes from 96 mm to 16.7 mm, and its tip moves to
    v -47.4 / z -7.6. The gen-2 CAD already does this at 12 deg (`CUFF_WRAP_NEG`), which leaves 7 deg of margin.
  - Or, to keep more grip, notch only the part of that arc beyond 19 deg from the elbow end to s ~142. That keeps
    full wrap on the proximal 22 mm.
  - Shortening the cuff from the elbow end instead would cost 55 mm, leaving a cuff 25.5 mm long without its screw
    rows.

## The full CAD loses R1 to its scapula tab; R17 fails on a mesh artefact (2026-10-16, user_osn_k4216)

The generation-2 winner (offset-skin-normal-3r k4216) was built in the user's style on the L1's exact kinematics (frame
deviation 1e-4 mm, the model's hub / neck / bridge metal within 0.17 mm). It scores 5 of 19 against its L1's 7: R1
49.0 vs 78.7 %, R6 0.85 vs 0.0, R16 55.8 vs 57.5 %. Details: docs/concepts/offset-skin-normal-3r.md, "Full CAD in the
user's style".

* **A scapula-fixed tab from a J1 over the acromion sits 15-42 mm off the skin.** It must clear the arm and deltoid of
  every pose in the scapula frame. On every heading outside link 1's sweep, a 22-26 mm M4 terminal clears that
  envelope only 18-58 mm above J1's face. The tab then takes a third of all covered skin, at a median gap of 42 mm,
  and only 3 % of that skin is in band.
  * R1 by nearest part, every 15th followed frame: 0.47 with the tab, about 0.68 without it, 0.76 for the L1.
  * The L1 never modelled the scapula interface, so any L1 with this J1 site is optimistic by up to ~30 R1 points.
  * Where the user's handler takes the base decides it, not the chain.
  * The tab fitted to the clip envelope also misses the workspace: 3 overhead poses at 1.6-3.6 mm in the skin, and
    0.85 mm into link 1 at Wave 72. It needs the workspace envelope and link 1's swept volume, not only link 1's heading.
* **R17 "does not move freely" is our mesh, not the mechanism.** OCC tessellates two glued seams of link 2 with 0.02 mm
  gaps, giving an open shell. judge/dynamics.py replaces an open shell with its convex hull, so link 2 weighs 150-158 g
  instead of 20 g, and the cuff twist reaches 5.85-6.6 deg (limit 5).
  * A 0.05 mm weld closes the mesh in mm.
  * The judges then reload it as float32 in metres, merge at 1e-7 m and drop degenerate faces, which reopens 69 edges.
    Builders must close meshes in the judges' own units.
  * param2_r20_n3_s1414_4's R17 FAIL is probably the same artefact (untested).
* **The user-style U cuff's anterior arc meets the user's forearm cuff at deep elbow flexion.** At flexion 131 deg
  (Drink from a cup), the forearm cuff touches the arc from 19 deg of wrap to its end (110 deg).
  * Judged result: R6 4.65 mm, and 23.6 mm into the forearm skin (R2, ours).
  * param2's R6 4.38 is the same contact.
  * Stopping that arc at 12 deg clears it.
  * The +vB arc still enters the trunk with the arm at the side (7.55 mm).
* **Catalogue guides need their screw lengths and channel sides modelled, not just their envelopes.** Two mistakes
  cost 43 % of the R16 workspace poses:
  * the across block's channel was drawn in its top face;
  * the M1.6x4 block screws reached into the rail's path.

  With the channel turned down and M1.6x2.5 screws, R16 went from 16.7 to 55.8 %.
* **k4216 does not follow the Raise overhead clip past elevation 66 deg, though it reaches the clip's peak.**
  - The clip holds frames 37-143. In the scapular plane the chain closes only at axial rotation -60 deg or less above about 70 deg (workspace grid: -45 fails from 75 deg up).
  - The clip climbs at -43 to -57 deg.
  - The peak (30, 150, -60) itself closes and is feasible.
  - The overhead stills show that workspace pose, not a clip frame (renders/2026-10-16_userstyle_osn_k4216/README.md).
* **Stills jobs on exo-blender-cycles failed on stale frames, not on bodyless scenes.**
  - The worker renders into /tmp/job_<a> and counts every PNG there.
  - A warm worker still had the previous a = 0 job's frames, so the count check failed. This explains "parts close-ups fail" and "5 sets at once fail".
  - film_client.py stills now gives each job a fresh frame offset (client side only).
  - Mannequin look: base 0.004 renders a flat silhouette; 0.028 at roughness 0.9 with no coat reads matte black with the muscles visible.

## Reach is the fold, and the fold is set by the arcs proximity allows (2026-10-16, docs/research/reach_attribution.md)

User, 2026-10-16: the reach numbers sit near 0.60 and plateau; max them out. Every lost workspace pose of the four
verified leaders was given its first cause on Bench(110,360) exact with the verifiers' frozen shapes
(`docs/research/reach/attribute.py`; the runs reproduce the verified 30.35 and 34.29 exactly), and every topology class
got a kinematic and an in-band ceiling (`ceilings.py`, `frontier_mine.py`).

* **The J2 fold takes 94-96 % of the lost workspace** (pin knee 133 of 142: 57 folded side, 76 stretched; raglan 136 of
  143; knuckle 132 of 138; spine-parked 140 of 146). Everything else is 6-9 poses: the pin knee's knee reach (4, all
  at elevation 165: hub 3 drifts 65.8-70.1 mm against lE + lc - 1 = 66.0; a longer knee measured 0 - lc 31 admits 2
  and both touch the skin), contact 2-5, parts 1-3, no jams.
* **Across the body is lost on the stretched side only** (47-51 of 68; th up to 173-179 against window tops of 101-104).
  **Overhead is lost on both sides** (7-9 folded at th 24-37, 10 stretched at 110-142): the overhead poses alone span
  th 18-146, so no shift of the window rescues them, only a wider one or a second one.
* **The plain 3R loses half its in-window overhead to the skin** (spine-parked: 5 of 10, link 2's top face among
  them); the pin knee loses none of its in-window overhead to the skin, 4 to its knee reach.
* **The fast-to-frozen reach loss is kinematic, not proximity.** At the same seats the share of workspace poses in the
  window is 0.69-0.71 on Bench(60,160)'s 160 poses and 0.61-0.63 on Bench(110,360)'s 360 (overhead 12 vs 28 poses):
  the CMA fitted the window edges to the 160-pose sample. Searches should score the window on the 360 poses.
* **Ceilings (360 poses, m = 10).** Plain 3R anywhere: 0.93 at 40 / 40 arcs, 0.97 at 45 / 45, 1.00 at a1 + a2 >= 130,
  all with axes through the trunk or axilla. At the leaders' arcs, best seats 0.74-0.78; at the leaders' seats 0.61-0.63
  (verified 0.594-0.617). Seats re-tuned within 5 / 10 / 15 deg: +0.02 / +0.04 / +0.06. Per-pose-free J1 rocker of
  travel 10 / 20 / 30 deg: +0.08 / +0.17 / +0.24. Two-state relay of the J1-J2 arc (40 <-> 77-84): 0.93-0.95.
* **At in-band14 >= 0.88 every measured class tops out at ~0.70 fast / ~0.61 frozen** (50 k plain-3R, 22 k pin-knee,
  9.8 k osn, 12.3 k stop-relay, 5.7 k dwell tries; osn never reaches in-band 0.81; the stop relay lifts the plain 3R
  to the pin knee's 0.700 at contact 0.055, not above). The pin knee's frontier is flat (0.719 at in-band 0.80, 0.700 at
  0.88, 0.694 at 0.90): giving up in-band does not buy reach. Longer arcs measured negative (every in-band >= 0.88
  plain 3R has a1 35-45). The 4-DOF lens's spring-centred 4R reaches 0.78 at in-band 0.86 (+0.075) but 0.644 at 0.88.
* **Red team: raglan-knee-3r's verified 31.52 no longer reproduces (32.37, in-band 0.886).** Since the 04:07 UTC
  per-hub-radius change the pin-knee model builds links with its own `_Geo(S.Geometry)`, bound before raglan-knee-3r.py
  swaps `S.Geometry` for its routed class, so the raglan model silently runs great-circle links. Fix before any raglan
  polish or re-verification. Pin knee, knuckle and spine-parked reproduce exactly (local and farm, pose by pose).
* **Fold margin (the user ruled 5 deg for MVP1 at ~05:50 while this ran).** At the window edge sigma_min of U = [u1 u2 u3] is 0.28 (m 10), 0.23 (7), 0.19 (5),
  0.12 (2) - joint rate per arm rate 3.6x / 4.3x / 5.2x / 8.3x - and the J2 transmission angle 34-44 / 28-36 / 23-31 /
  14-19 deg. The whole margin is worth at most +0.09-0.11 of kinematic reach at the leaders' seats (m 7: +0.03-0.04).
  Measured on the four frozen shapes, m 7 buys +0.011-0.025 of reach (gap -0.2 to -2.2) and m 5 +0.019-0.031, and no
  frozen run gains a single overhead pose: the folded-side poses the wider window admits jam link 1 on link 2 (the
  dyad stacks as it folds), the stretched-side ones partly hit the skin. At 5 deg (a measurement change): pin knee
  30.35 -> 29.26 frozen / 29.54 refit, knuckle 31.89 -> 30.03 / 29.10. Red team of the feel: the added poses need
  J2 4-5x faster than the arm through a 25-36 deg transmission angle - give J2 a soft (elastomer) stop at the 5 deg
  line. Not what the plateau is made of.
* **What follows.** The zero-complexity levers (the 5 deg margin, 360-pose seats) add ~+0.04-0.07.
  0.90 needs a second window (relay or 4th joint) with hub 2 in band in that state; the next gate for every fold lever
  is where hub 2 / the pivot parks in the poses it rescues (`relay_parking.py`). Measured for a two-state J1-J2 arc
  relay at the pin knee's seats (40 <-> 84 deg, kinematic 0.947): state A needs hub 2 at 51-55 mm, the 114 poses only
  state B closes need a median 70.5 / p90 205 mm, so one hub level keeps A in band and clears only 30-45 % of B:
  ~+0.09-0.14 of reach at best, not +0.32.

## Rebase to the user's rulings: every verified leader at fold margin 5 / O20 (2026-10-16, docs/research/rebase/)

User, 2026-10-16 ~05:50 UTC: fold margin 5 deg for the unpowered MVP1 (was 10), "Keep O20 only". **This is a measurement
change, not a design change.** The rules now live in ONE place: `tools/concept_kit.py` `FOLD_MARGIN` (5; `CB_FOLD_MARGIN`
overrides for comparisons) and `O20_ONLY` / `hub_rad()` (`CB_ALLOW_SLIM=1` only to re-measure an old slim claim). Routed:
the seed `SING` (offset-skin-normal-3r, pin knee, raglan knee, knuckle cufflink, closure-set arc knee, acromial rocker,
skin-normal-hubs), spine-parked, dwell four-bar knee, stop-relay rocker (stops and switch margin), fold-sph3r,
raglan-routed, crown-ring, meridian-goniometer, the model template, `tools/fold_frontier.py`, `fold_ends.py`,
`osn_fold_seeds.py`; slim-hub defaults -> O20 (spine-parked, dwell, stop-relay); the pin-knee model refuses a slim hub.
Not routed (dead / refuted / killed, or a different margin): annular-ring, back-anchored-ring, floating-centre,
j2-arc-sector (10, dead); clavicular-front-route, fivebar-roll, convergent-spm, spm-coaxial-turret (8, SPM / five-bar
legs); cam-unfold-4th, cam-coupled-4r, magrace-arc-chain, seed-arc-rails (10, dead); deltoid-oval-track and
scapula-halo-track (transversality, not a fold); pointer-cslide (15), posterior-max-margin-cardan / offset-arc-selfalign
(5 already); the champion reference `tools/concept_baseline.py` + `baseline-3r-kit` (10: a reference config, kept for
parity); `docs/research/reach/attribute.py` (fits at 10 by design, takes `--margin`). New models written this hour
(arm-parked-knee-4r, zc-frontier-3r, slotted-eccentric-j2-3r) carry a literal 5.0 = the rule; they should read
`K.FOLD_MARGIN` so `CB_FOLD_MARGIN` comparisons cover them.

**Red-team fix on the way: raglan-knee-3r routes its links again.** Its model swapped `S.Geometry` for the routed
class, but since 04:07 UTC the pin knee builds links with its own `_Geo`, bound before the swap, so the raglan model ran
great-circle links (32.37 instead of the verified 31.52, docs/research/reach_attribution.md). The model now patches
`PK._Geo.add_links` too (parity at r1d = r2d = 0 keeps the pin knee's own links): **31.52 reproduces to the digit.**

Each leader through ITS OWN verifier harness (farm, Bench(110,360) exact, the shape frozen from a Bench(60,160) fast fit
made at the same margin, the verifier's checks; `docs/research/rebase/<run>.json`, rows merged by
`docs/research/rebase/merge_rows.py`: v_* = margin 5 / O20, v_*_m10 = before). Every margin-10 re-run reproduces the
verified number exactly (pin knee k4598 30.35, raglan 31.52, knuckle 31.89, osn 42.59, spine-parked O15 34.29) - the
routing changed nothing at 10.

| leader (config) | complexity | v_gap as verified (m 10) | m 10, O20, re-run | **m 5, O20** | delta | reach 10 -> 5 | in-band14 10 -> 5 | follow 10 -> 5 | contact 10 -> 5 |
|---|---|---|---|---|---|---|---|---|---|
| **skin-normal-3r-pin-knee H1** (polish winner H-g107-1, O20 x3) | 19.5 | 28.21 (fit-60; 26.45 polish protocol) | 28.21 | **27.20** (polish protocol 24.48) | -1.01 | 0.644 -> 0.658 | 0.899 -> 0.895 | 0.964 -> 0.964 | 0.026 -> 0.026 |
| skin-normal-3r-pin-knee k4598 (round-3 winner) | 19.5 | 30.35 | 30.35 | **29.54** | -0.81 | 0.606 -> 0.636 | 0.904 -> 0.877 | 1.0 -> 1.0 | 0.009 -> 0.009 |
| raglan-knee-3r k1284 | 19.5 | 31.52 | 31.52 (routing fixed) | **27.82** | -3.70 | 0.600 -> 0.644 | 0.902 -> 0.895 | 0.973 -> 1.0 | 0.015 -> 0.017 |
| skin-normal-3r-knuckle-cufflink k1187 | 29.25 | 31.89 | 31.89 | **29.10** | -2.79 | 0.617 -> 0.664 | 0.871 -> 0.856 | 0.964 -> 1.0 | 0.006 -> 0.011 |
| offset-skin-normal-3r k4216 | 17.75 | 42.59 | 42.59 | **41.02** | -1.57 | 0.611 -> 0.631 | 0.784 -> 0.783 | 0.964 -> 0.973 | 0.021 -> 0.023 |
| spine-parked-j2-3r k7008 | 0 | 34.29 (O15 J2 / J3: does not stand) | **41.77** (O20) | **41.00** | -0.77 (O15 -> O20: +7.48) | 0.592 -> 0.600 | 0.809 -> 0.805 | 0.955 -> 0.973 | 0.019 -> 0.015 |
| arm-parked-knee-4r k-A seats at O20 (its own model `frozen`, NO verifier yet; the 22.36 ideation claim used O15 J2-J4) | not counted yet (4 active R + 1 spring) | 22.36 (O15, self-measured: does not stand) | 33.91 | 44.24 | +10.33 | 0.744 -> 0.672 | 0.760 -> 0.726 | 1.0 -> 1.0 | 0.043 -> 0.041 |

* **The 5 deg margin is worth 0.8-3.7 gap points; most of it is follow, then reach.** The knee designs' folded clip
  frames come back (raglan, knuckle: follow 0.96-0.97 -> 1.0) and reach rises 0.02-0.05, while the shape fitted at 5
  covers more poses and in-band drops 0.01-0.03 (pin knee 0.904 -> 0.877). The newly admitted folded-side poses jam
  link 1 on link 2 (pin knee parts losses 2 -> 8). No leader gains more than one overhead workspace pose (raglan 7 -> 8 of
  28; pin knee 7 -> 7).
* **O20-only costs the zero-complexity 3R 7.5 points** (spine-parked k7008: 34.29 at O15 -> 41.77 at O20, margin 10):
  in-band14 0.878 -> 0.809, hub 3 0.84 -> 0.74, link 2 0.79 -> 0.65 and hub 2 1.00 -> 0.95 of their samples in band
  (same seats, same fit rules; only the J2 / J3 hub radius 7.5 -> 10). At margin 5 it is 41.00. The only complexity-0 verified design is now 27
  gap points from the golden 13.75; the knee designs (complexity 19.5) lead.
* **Leader after the rebase: skin-normal-3r-pin-knee H1, 27.20 (score 90.11) at margin 5 / O20**, reproduced to the digit
  by this track's farm run of the round-3 verifier (the polish verifier measured 27.20 too; 24.48 with the shape fitted on
  Bench(110,360) itself); raglan-knee-3r 27.82 (89.88) is 0.6 behind and has not been polished; knuckle 29.10, the
  round-3 k4598 29.54. All three knee designs are complexity 19.5-29.25 (two or three sensed passive pins).
* **The polish optimum moves with the margin: a margin-5 re-polish gains 2-2.7 more (CANDIDATE, not yet independently
  verified).** 4 CMA streams from H1 / HW / R2 at margin 5 (`tools/knee_polish.py`, O20 fixed, 3876 evals, farm,
  `docs/research/rebase/polish_m5/cma_streams.json`; H1's own objective at margin 5 is 25.68): best P5 = HWm5-g23-5
  near-touch 22.08 fast. Exact: **21.79** on the polish protocol (score 92.08; reach 0.714, follow 1.0, in-band14 0.887,
  contact 0.019, near-touch 22.34; H1 24.48), disjoint held-out 24.87 (near-touch 28.70), round-3 fit-60 verifier 24.88
  (follow 0.946; H1 27.20). Q5 = H1m5-g71-14: fit-60 25.24 (follow 1.0, contact 0.009). Both clear the >= 1 point bar
  on every protocol measured; an independent verifier must confirm before either replaces H1 in the CAD
  (row field `rebase_polish_m5`). Reach 0.69-0.71 is still short of the ~0.77 that 95 needs.
* **The 4R's margin is a design element, not a rule.** arm-parked-knee-4r's spare is set by J2 stops AT the fold-margin
  line, so margin 5 moves its stops and the spring parks the knee elsewhere: hub 2 in band 0.75 -> 0.58, gap 33.91 ->
  44.24. At O20 it keeps the highest frozen reach of any class (0.744 at margin 10, overhead 10 of 28) but link 3 is
  0.37 in band. Its stop margin should be a free parameter >= the 5 deg rule, searched; it needs its own verifier.
* **Still far from 95.** At margin 5 the best verified reach is 0.64-0.66 against the ~0.77 that 95 needs at
  in-band 0.88: the margin moved every leader by a third of the way it moved the kinematic window (+0.02-0.05 of the
  +0.05-0.06 promised, docs/research/reach_attribution.md section 3), as predicted. The fold is still the plateau.
* **Red team of the feel at 5 deg** (reach_attribution.md section 3): at the new window edge sigma_min of [u1 u2 u3]
  is 0.19-0.21 (J2 turns ~5x faster than the arm) and the J2 transmission angle 23-31 deg: give J2 a soft elastomer
  stop at the 5 deg line in MVP1. Searches that ran before ~06:05 UTC ran at 10; any farm job shipped after that runs
  at 5 unless it sets `CB_FOLD_MARGIN=10`.

## The zero-complexity 3R tops out at 31 frozen exact: hub 2 caps the fold window (2026-10-16, zc-frontier-3r)

The user's golden target is score >= 95 (gap <= 13.75 on Bench(110,360) exact, frozen shape) at complexity ~0. The
complexity-0 class (three active O20 pins through GH, three links, nothing else) was mapped globally under the
05:50 UTC rulings (O20 only, fold margin 5, J1 on the back / acromion top), with every free choice open: J1 anywhere
on the allowed seats, J3 on the whole arm sphere, both ends of every axis line (arcs 12-168), branch, and the J2 / J3
stack order (`docs/concepts/zc-frontier-3r.md`, `tools/zc_frontier.py`, data `docs/concepts/zc/`).

* **Kinematics is not the cap.** 22 % of 16384 Sobol configs close >= 0.7625 of the 360 workspace poses at margin 5
  from allowed seats; the J1 seat hardly matters, the arcs do (shorter arc < 40 deg: 50 of 9652 configs; viable
  median 63 deg).
* **Proximity is.** Of the 3560 kinematically viable configs, 3639 of the 4268 evaluated have a hub axis with no skin
  within 170 mm (hub 2 or hub 3 floats), and the 235 with all three hubs on the body reach in-band <= 0.669 (hub 2
  median 0.06). Over 15394 full evaluations on the verification bench (sweep + 22 CMA streams) the frontier is:
  reach <= 0.633 at in-band >= 0.88, in-band <= 0.592 at reach >= 0.7625. CMA started from four wide-window basins
  ends at 64.9-74.1, one forced to a1 = 52 walks back to a1 36.7, and eight restarts of J1 over the back / medial top
  either return to the acromion top (32.1-38.5) or stay wide-window (55.8-72.2).
* **Mechanism, measured as a slice (fixed a1, same seats, Bench(60,160)):** a1 38 / 46 / 54 / 62 -> gap 27.2 / 43.8 /
  55.6 / 67.4, hub 2 level 60 / 64 / 86 / 107 mm, hub 2 in band 1.00 / 0.90 / 0.06 / 0.01, reach +0.05 at best.
  A complexity-0 hub is one disc at one level on an axis the closure moves; the arcs that open the fold window
  carry it over skin spanning more than the 12 mm band.
* **Converged optimum: 28.85 fast / 31.04 frozen exact (score 88.7; round-3 protocol 33.51)** at J1 bvec(109.4,
  65.9), J3 wdir(85.7, -16.2), a1 36.7 / a2 69.1, branch -1, inverted J3 stack (link 2 on hub 3's lower plate: worth
  ~8 points over the normal stack at these seats on the fast big bench; +4.1 at k7008's seats). Six convergence
  streams (1446 evaluations) found nothing 0.05 better. Out of sample (all 1432 workspace poses, exact): 35.04. The fold takes 121 of 136 lost workspace poses (44 folded, 77 stretched; across the body
  19 / 68, overhead 6 / 28).
* **What follows.** At complexity 0 the measured ceiling is ~31 exact: 13.75 needs reach +0.13 at the same in-band,
  i.e. a second fold window (relay, 4th joint) whose hub 2 stays in band in the poses it rescues. A radial slide at
  hub 2 would have to absorb 26-47 mm of level spread and stands up by its travel (CLAUDE.md): ruled out. That is
  the near-zero track's input.

## The polished pin knee wins the bench but not the built proximity judges (2026-10-16, l1_skin-normal-3r-pin-knee-h1)

Measured: the L1 build of the verified polish H1 (fit on Bench(110,360) fast, fold margin 5) against k4598 through the
SAME builder at the same margin (control `l1_skin-normal-3r-pin-knee-k4598-m5`): R1 80.1 vs 81.1 %, R1-aim 42.3 vs 43.2 %,
R4 overhead 74.2 vs 79.6 % (both FAIL at 80; Raise overhead median skin gap 12.1 vs 11.1 mm), R16 67.9 vs 66.5 %, lowest
metal over the followed frames 1.66 vs 0.60 mm, R6 0.0 both. The verified bench gain (2.3-4.9 gap points at margin 5)
came from reach (fold losses 115 -> 97) and from removing near-touch poses by moving metal outward (knee level +5.9 mm,
hub 3 face +2.3 mm); the judges' R1 / R4 measure covered SKIN within 2-14 / 2-10 mm and pay for the outward metal. Lesson:
the polish objective must carry the judge's coverage term (or cap tr / the faces), or the generation's built winner
regresses on R1 / R4 while the bench improves. Also measured: k4598's own L1 moved R1 84.2 -> 81.1 and R4 83.9 -> 79.6 from
the margin-10 -> 5 refit alone (hub 3 +2 mm, more Wave / overhead frames followed) - a measurement change, not a design one.
Builder fix found on the way: a mount routed to the nearest end of the user's BOTTOM can sit inside the knee's sweep (H1:
every frame jammed, 1.18 mm); the builder now sweeps member 3 + the knee bar through the arm frame, cuts BOTTOM clear of it
and routes the mount clear by >= 1 mm (pipeline/concept_l1/build_pinknee_l1.py). Details: docs/concepts/skin-normal-3r-pin-knee.md
"L1 keep-out CAD of the polished H1".

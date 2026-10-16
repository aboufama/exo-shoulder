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

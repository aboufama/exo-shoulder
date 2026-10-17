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

## No 1- or 2-passive closure widens the fold; the middle planar knee parks hub 2's pins but its plates float (2026-10-16, docs/research/nzc/closures.md)

Near-zero-closure track of the golden push. Measured / derived:
* **A single slider (or single pin) cannot close any offset 3R exactly**: a J3 line off GH leaves a 2-D drift (a circle in
  hub 3's plane), a J2 line off GH an unavoidable radial component d sin a2 |sin q2|. Every 1-passive closure is
  degenerate (the passive locks at 0).
* **The only 2-passive closures are planar** (all joints on GH lines or parallel to one w; RR / RP / PP next to the
  active joint || w): distal (the pin knee / osn cuff), proximal (base-side, no value), and **middle - the new
  virtual-J2 knee**: J2 as a planar pin triple, link 2 turning about a virtual GH line. In all of them the passives only
  re-parametrise the rotation about w: **the fold law is unchanged; widening the window needs >= 3 passives (a passive
  rotation not parallel to an active axis, e.g. the Jarrasse-Morel 2 pins + 1 slide along the arm) or a 4th active joint.**
* Sensing: on a rigid-GH body the 3 active encoders fix the arm iff the knee pins and the virtual axis are not collinear
  in the knee plane (|sin| > 0; untuned: min 0.017, reading sigma_min 0.019 -> RIG_MIN 0.17 added); under GH translation
  the pin angles must be read (or slides used). A pin pair never stays out of the orientation reading.
* **Virtual-J2 knee gate (Bench(60,160), zc seats):** at a1 / a2 52 / 70 (fold-law reach 0.819) hub 2 ON the w-ray is in
  band 0.03 (level 123 mm), but a link-1 pin 28 mm off the w-line parks 0.958 at 53 mm and a link-2 pin 0.969 at 63 mm,
  17.6-38.7 mm apart. **First honest model screen: 103.68** (reach 0.54, in-band 0.40): the pins park, the crank / knee
  PLATES, swept around the virtual axis at one level each, float (knee 94 mm, 0 % in band; pin b and link 2 stacked on
  it 0 / 10 %) - the virtual-pole four-bar's "J2 neighbourhood is the worst skin" again. Complexity 19.0 sensed (= the
  pin-knee class). Not a ceiling yet (22 configs); next: Bench(110,360) gate (farm), a plate-footprint gate, farm CMA.

## A 3-passive closure widens the fold only through a moving chain centre; hub 2 still caps it (2026-10-16, docs/concepts/fold-widening-3passive.md)

Measured / derived (Bench(110,360) frames, margin 5, H1 seats; `docs/research/fold3p/`):
* **Passives parallel to active axes never move the fold** (slides rotate nothing): "pin knee + a slide along the arm"
  cannot widen it. **A passive rotation between GH-centred bodies locks at a constant**: a tilted knee pin, a passive
  cuff roll or a Jarrasse-Morel cuff (2 pins + slide) on a GH-concentric chain all sit at one value in every pose.
* **The closure that works: a coupled J1 rocker** - J1 on a rocker pinned about a posterior (anteroposterior) axis
  passing R mm from GH, closed by the pin knee. The knee's out-of-plane equation fixes the rocker:
  rho = atan2(B, A) + s acos((A - k) / |A, B|) (A, B = the arm-fixed J3 direction on the pivot's frame, k = h / R):
  determined, smooth, no islands. Kinematic reach 0.731 -> **0.842 connected** (travel 30; 0.864 at 45), overhead
  0.46 -> 0.68-0.71, all clip frames close; the per-pose-free bound is 0.92-0.95. The arm-side mirror (cuff roll driven
  by an offset chain centre) loses (0.72).
* **Hub 2 caps it again**: the rescued poses put the J2 ray over 78-93 mm skin (q0.97; bulk 55 mm). Parked in band >= 0.8
  the rocker keeps **0.775** of the workspace (plain H1 0.719 at 0.96): +0.05, 0.005 short of the 0.78 gate. J1 rides
  down to el 28 (outside the acromion-top seat region), and rho moves 6.5 deg per mm of real GH translation at R 12
  (sensed: complexity 19.5 -> 29.0); a larger R moves the chain centre 11-21 mm and lifts hubs 1 / 2 out of band.
  Not catalogued. Next: a joint search with the hub-2 gate and J1 el >= 50 in the objective (seats free).

## The zero-complexity class, searched near-exhaustively on GPUs: one narrow-window basin, ceiling 31.04 exact frozen; the reach / in-band frontier is 2x short of 95 (2026-10-16, tools/gpu_bench.py screen / cma / polish / pareto)

The whole complexity-0 class under the 05:50 UTC rulings (three active O20 pins through GH, margin 5, J1 on the back /
acromion top only, J3 anywhere on the arm sphere, both ends of every axis line, branch, all four J2 / J3 stack orders,
underside quantile, strap end hold) on the verification pose set Bench(110,360), with the exact-parity GPU port of
zc-frontier-3r (incl. the verifier's near-touch metric: the pods' CPU-kit checks max |GPU - CPU| 0.0 on gap, 0.01 on
near-touch), on three RunPod pods (2x RTX 5090, 1x RTX PRO 4000; data, method and per-config numbers in
docs/research/golden/README.md and docs/research/golden/gpu_frontier.json).

* **Sobol, 560,478 configs (two independent scrambled sequences), with exact lower bounds.** Stage A (closure + dense
  K2, i.e. the fold law and the jam check alone): 78,724 (14 %) could still score 95 (bound <= 13.75). Stage B (the
  three hubs alone: their K3 levels and their skin contact): only 6,528 of those keep all three hubs on the body (F <=
  140 mm; hub 3 floats in 64 %, hub 2 in 64 %, hub 1 in 33 %: median F 99 / 213 / 400 mm), and 470 still have bound <=
  13.75. Every Sobol config with bound < 45 (first sequence) / < 35 (second) ran on the full bench at both J3 stack
  orders (7,644 evaluations): **the best Sobol point is 63.63**. The 470 that fold and hubs would allow at 95 reach
  0.75-0.83 but sit at in-band 0.21-0.41: hub 2 in band 0.0-0.09 (F 87-131 mm), link 2 0.0-0.3, link 1 0.1-0.5.
* **The good region is a needle for sampling and a wide basin for local search.** 130 CMA-ES runs (108,768 evaluations) started from the best
  distinct points of both sequences (plus the 4 earlier leaders and 2 seeds) land in two families only: the **narrow-window spine-parked family** (J1
  bvec(81-111, 62-68) = acromion top / back of the shoulder, a1 34-41, a2 64-81, J3 wdir(64-90, -10..-22), branch -1,
  mostly inv3 = 1) at 28.85-38 fast, reached from starts as poor as 83-86; and a **wide-window medial acromion-top
  family** (J1 az 23-125 / el 64-81, a1 70-85, a2 50-60, J3 wd 93-97) at reach 0.78-0.87 but in-band 0.39-0.56, 50-58.
  No third basin. The deep polish (every branch x stack order at each basin's best, then IPOP-style CMA, lambda 24 / 48,
  on the near-touch AND the plain gap) leaves the plain-gap optimum at 28.85 (three restarts, no gain: a strict local optimum) and brings the other basins to 29.12-29.26 plain or 33.48 near-touch.
* **The class's reach / in-band frontier** (CMA on the best in-band at reach >= R, Bench(110,360) fast, 56 runs):
  R 0.63 -> in-band 0.89 (the 28.85 optimum), 0.66 -> 0.83, 0.69 -> 0.83 (contact 0.05), 0.70 -> 0.76, 0.73 -> 0.69,
  0.75 -> 0.64, 0.80 -> 0.52, 0.85 -> 0.42. A 95 needs (0.90 - in-band) + (0.90 - reach) <= 0.1375 - contact at follow
  >= 0.95; the frontier's smallest sum is 0.28 (at reach 0.63), so **the class cannot score better than ~28 fast on this
  bench** - the 28.85 found by the CPU CMA earlier is the class optimum, and no GPU run found a lower plain gap.
* **Verified (outside judge = the CPU kit, `tools/zc_frontier.py frozen`, the zc model's checks + the spine-parked
  verifier's top_check at O20 / margin 5, run on the pods' CPUs; 10 best distinct configs by GPU gap).** The CPU fast
  numbers equal the GPU's on all 10 (gap identical, near-touch +-0.01). Exact frozen wear on Bench(110,360): best
  **31.04** (the 28.85 config; near-touch 38.03; verifier protocol fit 60/160 -> 33.51), then **32.08** for the
  plain-gap polish 29.12 (best on the verifier protocol: **32.95**), **32.37** for the near-touch optimum (CMA basin
  23: GPU 32.44 / near 33.60 -> exact 32.37 / near 34.69, fit-60 33.70 / 36.60 - the near-touch search loses nothing to
  the exact path, the plain-gap optimum loses 2.2), then 34.52, 34.84, 35.98, 36.36, 37.73, 38.07, 38.61, 38.69 (11
  verified). **Nothing reaches 13.75; the measured ceiling of the class is 31.04 exact frozen (score 88.7) on the
  fit-110 protocol and 32.95 (score 88.0) on the verifier's fit-60 protocol.**
* **What caps it, by pose and member (the 31.04 config, exact):** 136 of the 360 workspace poses are lost, 121 to the
  fold (44 folded, 77 stretched: 49 of the 68 across-body poses, 18 of the 28 overhead ones), 7 to parts, 8 to contact
  (link 2 3, hub 3 2, hub 2 2, neck 1); in band: hub 3 0.82, neck 0.81, link 2 0.88 (hub 1 0.98, hub 2 1.00, link 1
  0.95). Opening the window to take the stretched across-body poses (a2 up, J3 toward the arm's inside) drops link 2
  (0.88 -> 0.72 -> 0.52 -> 0.36 at reach 0.63 / 0.66 / 0.70 / 0.75), hub 3 (0.82 -> 0.70) and the neck (-> 0.33 at 0.75);
  the wide-window family takes the poses but floats hub 2 (in band 0.0, F 102-113 mm) and link 2 (0.05-0.08).
  At complexity 0 a hub is one disc at one level on an axis the closure moves: the fold window that 95 needs puts the
  J2 neighbourhood (hub 2 + link 2) or the J3 side (hub 3 + link 2 + neck) over skin that spans more than the 12 mm band.
* **Method lessons.** (1) A 10^5-10^6 Sobol map of an 8-D needle basin finds nothing (best 63.6 vs 28.85): sampling
  maps the bounds, local search finds the basins - start CMA from many distinct points, not from the best samples only.
  (2) Exact lower bounds without straps prune 99 % of a Sobol map in seconds (57 k configs: stage A + B in 61 s on a
  5090), which makes the full bench affordable on what is left. (3) RTX 5090 ~40 evaluations/s on CMA batches vs RTX PRO
  4000 Blackwell ~12.6: 3.2x the speed at 2.1x the price - the 5090 is the better buy per dollar too. (4) The near-touch
  objective holds up under the exact path (32.44 fast -> 32.37 exact), the plain one does not (28.85 -> 31.04).
* **What follows.** The golden 13.75 is out of reach at complexity 0 under the rulings (measured, not argued): the
  frontier must move by ~2x, which needs a member that follows the skin where the window opens (hub 2 / link 2 or the J3
  side) - i.e. the near-zero track (one sensed passive or a 4th joint), not more search of this class.

## The pin-knee family runs exactly on a GPU pod; its in-sample polish runs out in 20 min (2026-10-16, tools/gpu_bench_knee.py)

* **Port = the kit, accelerated**: knee_polish's whole evaluation (model + verifier extra_checks + near-touch audit)
  runs the kit's own code; only the per-pose loops (sphere-traced skin requirement, every part pair incl. the 0.15 mm
  adjacent ones, the verifier's closure / knee / boss checks) and Bench.dist are batched on the device. Parity vs the CPU
  kit on the pod: **max |diff| 0.0 on every metric** (gap, near-touch < 1 / < 2 mm, model gap, reach, follow, in-band
  14 / 10, contact) for 53 configs (H1, k4598, P5 + 50 inside the rulings) x 2 protocols (same-bench Bench(110,360);
  fit Bench(60,160) -> wear Bench(110,360)), and again for v2 + raglan-knee-3r's routed best (54).
* **Where the kit's time went**: 1.7 s of ~4 s per config was libigl rebuilding the rest-skin AABB + winding-number BVH
  for the three seats on every call; built once they give the same numbers bit for bit (0.009 s). Port v2: 0.26 s per
  config alone on the GPU, 0.86 s median with 8 workers (kit 8.2 s same-bench, 10.9 s frozen); the polish ran **9.8
  evals/s on one $0.72/h pod** (~10x per dollar against the farm, outside the worker quota). The tail is the kit's exact
  libigl path for samples traced out of the +-260 mm grid box (junk configs, 1-4 min in both implementations).
* **The in-sample polish converges in 20 min**: knee_polish's CMA on the GPU (near-touch, Bench(110,360), margin 5, O20,
  12 004 evaluations, every stream stopped by sigma collapse) takes H1 25.68 -> 22.29 (sigma 0.5) and **20.81** (sigma
  1.5, a new corner: lE 72, lc 37.5, ang_min 24.2; plain 20.26, reach 0.706, follow 1.0, in-band 0.900, min metal
  0.46 mm), P5 22.08 -> 21.89, raglan's fixed route 36.82 -> 24.18. P5's in-sample gain was refuted on the disjoint
  held-out bench, so these are candidates for the independent verifier (exact wear, fit-60, held-out, continuity),
  not results; the next polish wants a held-out-aware objective (the port takes any Bench with a fast grid).

## The knuckle's 15.42 needs J2 stops inside the fold margin; at the 5-deg margin it is 18.45, held out 22.27 (2026-10-16, minarc-stop-knuckle-4r variant B, judge)

Claim: variant B (pin knee + a spring-held passive knuckle K splitting link 1 + J2 hard stops, CMA stream BD), frozen
exact Bench(110,360) 15.42 (score 94.4). Two independent verifiers ran. A third, skeptic lens from another workflow
agrees with them. Verdict: **REFUTED**.

Raw data:
* the lenses: `docs/concepts/verify/minarc-stop-knuckle-4r-{remeasure,mechanism}.md`;
* the judge's cross-check: `docs/concepts/verify/minarc-judge/`;
* the merged ruling: `docs/concepts/rows/minarc-stop-knuckle-4r.json` (`verification`).

What was measured:
* **The number reproduces to the digit, but only in the model's own fold reading.** Both lenses got 15.42 locally and on
  the farm. The verifiers' own closure, stop and boss checks remove 0 poses. On the full 1432-pose grid the continuity
  rule drops nothing (1143 of 1143 nodes; contact-aware 1097 of 1097). In the same reading the held-out bench gives
  18.22, against H1's 31.39.
* **What failed: the fold margin.** The model clamps the J2 *interior angle* to [5, 175] and puts its J2 stops at
  phi 12.28 / 162.70.
  * With K on stop A the chain is a plain 3R (a1 38.07, a2 58.75). There, those stops sit **1.88 / 1.37 deg** from the
    J1-J3 fold in the kit's metric (`tools/concept_kit.py`). That metric is the one H1 and every verified row are held to.
  * Taken poses come down to 1.97 deg on the bench (25 under 5) and 1.51 deg held out (44 under 5). 8 clip frames
    (wash opposite shoulder) come down to 4.02 deg.
  * At the stretched stop, J2 turns 6.35 deg per deg of J1-J3 motion; H1's worst is 3.15.
  * This is the singularity margin being shrunk to buy reach, which the user's 5-deg lower bound forbids.
* **Priced.** With the J2 stops moved to the 5-deg margin (phi 20.793 / 146.614), same seats, shape refit fast, worn
  frozen exact, the gap is **18.45** (score 93.3; reach 0.747, follow 1.0, in-band14 0.889, contact 0.021; near-touch
  24.26).
  * Three harnesses agree: the mechanism lens, the skeptic lens, and the judge's run of the re-measure lens' strict
    harness. In that strict run every joint, the actives included, is held to 10 deg per 2-deg step, and 0 of 269
    taken workspace poses are dropped.
  * The minimum state-A margin is 5.12 deg and the forced sub-chain margin is at least 16.9 deg.
  * **Held out: 22.27, against H1's 31.39 under the same harness** (near-touch 26.71; 0 of 682 dropped).
  * If the claimed stops are kept and the 5-deg band is simply refused, the knuckle-open states become islands
    (reachable from rest only through the band): 21.33 static, **35.56 connected**; held out 21.67 / 38.20.
* **What failed in the mechanism** (mechanism lens). Both faults are fixable, and the fixes cost no bench points.
  * The J2 "hard stop" acts on a *virtual* angle (arc J2->J1 vs J2->J3), which no dowel at J2 can stop. In the claim's
    forced states J2 sits up to 14.5 deg off its own stop. A real q2 stop gains 1.13 points, giving 17.32 with the
    repaired stops. This is single-lens, so it is not credited.
  * The specified 0.2 x 3 mm clock spring carries 0.028-0.040 N.m, but the claim needs 0.08-0.113 N.m (the demand is
    0.057 N.m at 2 g). A 0.3 x 5 mm 1.4310 strip in a cap 6 mm taller than the O20 stack does the job, at 0.00 cost.
* **Other measurements.**
  * K never moves on any clip (0 deg/s): its whole gain is static workspace reach.
  * The minimum metal is 0.05 mm on the overhead raise. The CMA searched the plain gap, not the near-touch gap.
  * The chain has 4 revolutes, which is at the user's cap, not the preferred 3. K is sensed. Complexity is 33.
* **Protocol lesson.** `connected()` run on the 360-pose bench subsample under-connects any design (here 24.79 for the
  claim and 32.07 for the repair). Use the full-grid flood fill, which both lenses' harnesses implement. A model must
  state its fold margin in the kit's J1-J3 metric. A stop on any other angle has to be mapped into that metric before
  a number is claimed.

What it means:
* The priced knuckle (18.45 in-sample, 22.27 held out) beats the verified H1 (27.20 same protocol, 24.48 polish, 31.39
  held out under this harness) by 6-9 points with 0 passive translations. It is the strongest lead in the project.
* It is still a *different configuration* from the one claimed, and is not confirmed. Next:
  1. a re-claim with the q2-stop model fix;
  2. a near-touch CMA with the stops held at least 5 deg from the J1-J3 fold, starting from BD at the margin and from
     the agent's BB stream;
  3. its own two-lens verification;
  4. a MuJoCo feel and stop-impact red team at the J2 stops.

## The knuckle under every rule as it stands: 19.06 frozen exact, held out 23.24 vs H1 31.39 (2026-10-16, minarc-stop-knuckle-4r kit-rule re-optimisation)

Question: what does the knuckle family score when J2's stop is one a dowel can make, every state keeps the kit's 5-deg
J1-J3 fold margin, the clock spring is one that carries the load, the search runs on the near-touch gap, and reach is
scored on the continuously reachable set? Model `docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py` (opt-in
`kitrule`, `phys`, `capK`, `m3e`; the claim's model unchanged); claim harness `...-kitrule-wear.py` = the independent
re-measure verifier imported unchanged with its model handle swapped; raw data `docs/concepts/verify/minarc-kitrule/`;
write-up `docs/concepts/minarc-stop-knuckle-4r.md` "Kit-rule re-optimisation".

What was measured (fit Bench(60,160) fast -> wear Bench(110,360) EXACT, margin 5 in every state, O20 + hub K cap 6 mm,
full-grid continuity):
* **The physical stop law works and costs little.** J2's own angle q2 locked on a dowel, K opening to the smallest
  rotation that closes (closed form): at the claim's seats with both stops at the 5-deg margin (BDp) it measures
  **19.06 (score 93.07)**, near-touch 26.15, against the judge's virtual-stop 18.45; **held out 23.24** (near-touch 28.31)
  against the virtual 22.27 and H1's 31.39 under the same harness. Every taken pose keeps >= 5.01 deg in its own state;
  1041 of 1041 grid nodes connect, 0 islands: with the stops placed in the kit metric no forbidden band separates the
  states (the claim's stops kept under the kit rule gave 35.56).
* **The near-touch CMA from there (stream LB1, 417 evals, gate 0.24 / 0.23 / 0.23 passed)** finds 11.22 fast, frozen
  19.63 with near-touch 22.88 (stretched stop moved to 7.27 deg, K's whole range used) - but held out it is 24.59 /
  near-touch 28.22: the in-sample gain does not generalise, and it pinches 0.02 mm on overhead clips Bench(60,160) never
  shows. BDp stays the claim.
* **The effective-dyad check is not the limiter**: without it forced poses reach 2.97 deg of margin and BDp gets worse
  (20.91), because the refit shape changes.
* **Variant A** (the plain chain + K, complexity 13.5) under the same rules (stream LA1, 337 evals, gate passed): 41.14
  frozen exact, in-band 0.71 - not a contender. Its rest pose sits with K open, which the strict rest-seed rule cannot
  seed; from any elevation-0 seed all 1263 nodes connect.

What it means: under the rules as they stand the knuckle (complexity 33, 4 revolutes, K sensed = 4 active DOF by the
skeptic's ruling) is the best measured family - 8.1 points ahead of H1 in-sample, 8.2 held out - and 5.3 points short of
95. Next: the independent verifier on BDp (LB1 as the near-touch alternative); a cross-fit (held-out-aware) near-touch
objective; the farm streams PB1-6 / PA1-3 (queued, never started); the user's ruling on the sensed 4th joint.

## Feel of the near-fold J2 stop, measured (2026-10-16; docs/research/fold-stop-feel.md)

Method: quasi-static Jacobian analysis (`docs/research/fold_stop_feel.py`); T = 3 N.mm per O20 pair and per knee pin;
fit clips at their stored 10 fps.

**Rate ratio and J2 contact speed.** At B's claimed stop (phi 162.70) the fold margin is 1.37 deg and the J2 rate
ratio is **6.36**. With the stops at the kit's 5-deg margin (phi 20.79 / 146.61) it is 3.45; H1 is 3.15. At the clips'
peak arm speed of 127 deg/s, J2 reaches the stop at 805 / 437 / 399 deg/s.

**Cuff force from bearing friction.** 0.39 N at B's stop, against 0.20 N for both the kit rule and H1. Over the clips
the peak is 0.28 N for both B variants and 0.19 N for H1, against the 5 N limit. The figures scale linearly with T.

**Stop impact.** 5.5 / 2.1 / 1.0 mJ at 127 deg/s, and 1.2 / 0.47 / 0.21 mJ at the clips' 60 deg/s peak J1-J3 rate.
For H1 this is the chain only: with no K, its stop also blocks the arm itself.

**Spring K preload.** B needs 45 N.mm (friction 23 + weight 25) and the kit rule needs 33. Over the 63-deg stroke a
music-wire spring at D 15.5 mm takes 4-7 mm of axial body and does not fit inside the v5 O20 stack. At B's duty the
4-6 mm candidates exceed their fatigue rating.

**No jam at the stop.** The J1-K-J3 sub-chain has a condition number of 3.9 there, so K opens at 2.1 rad/rad. The
wearer feels a spring step of about 0.8-1.7 N at the cuff.

**Red team.** The model's stretched state holds phi constant while the J2 joint angle drifts 0 to 14.3 deg off its
contact value as K opens (15.1 deg for the kit rule). A hard stop on J2 cannot produce that law, so B's stretched poses
must be re-measured with a q2 stop.

## Full CAD of the polished pin knee: the J1 ring has no room for side ears; bent bars cost R1 (2026-10-16, user_pinknee_h1)

The polished H1 was built as a full user-style CAD (`pipeline/conformal/param_cad/user_style_pinknee.py`). The verified
Bench(110,360) shape was carried over as a frozen pickle from the farm (`pipeline/concept_l1/pinknee_shape.py`), and the
kinematics match the model within 1e-4 mm.

- **Base at the J1 ring (user ruling): side ears do not fit.** Link 1, built and posed over every clip frame and every
  feasible workspace frame (1.9 M samples), sweeps the whole zone where short ears would sit (radius 10-19 mm):
  - At the seat level, 9 of 180 headings clear link 1 by >= 1 mm, and none of them clears the skin envelope (best:
    5.2 mm inside it).
  - Raised 1.3 mm, 14 headings clear both, but all lie within 304-310 deg, so there is no pair 90-180 deg apart.

  The base is therefore the J1 upper member alone, and the handler's bracket threads onto the M18x0.5 spigot in place of
  the dome cap. Coming down axially over the crown is the one direction link 1 never occupies. This holds for any 3R
  whose link 1 sweeps most headings about J1: the handler interface belongs on the J1 axis, above the crown.
- **Bent bars ride above the evaluator's straps and cost R1.**
  - Link 1 has to climb 59.6 deg to J2, whose face sits 9.6 mm higher. No chain with every bend >= 15 mm inner radius
    stays above the L1 strap, so link 1 is 5-axis machined from solid (R 3.5).
  - Link 2 is a bent 3 mm Ti bar with bends >= 15.5 mm. It sits on average 2.6 mm, and at most 9.4-10.9 mm, above the L1
    strap at J3.
  - Against its own L1, R1 drops 80.1 -> 71.6 % and R1-aim 42.3 -> 33.1 %. The upper-arm cuff was trimmed to 10 deg on
    both side arcs (the trunk comes within 1 mm across the body, at plane 122-145 and elevation 31-48), which also removes
    arm-side metal near GH.
  - Next levers: a machined link 2 that hugs the strap (switch `PK_LINK2_MACHINED=1`), and a cuff-trim rule over the
    followed frames only.
- **Exporter bugs that the judges caught.**
  - Pin a's iglidur sleeve was placed in member 3's frame (A0) instead of the knee link's (A0m), 10.2 mm off. That alone
    gave R6 1.43 mm and 42.5 % of R16's fails.
  - The knee link's name contains "clip", so it was classed as hardware: no STEP, wrong density, and left out of the
    kinematic check.
  - All three are fixed in the builder and in the design.
- **Open link 2 mesh.** OCC leaves a T-junction crack in link 2's tessellation (71 open edges in one 8 x 6 mm patch).
  Neither welding up to 0.3 mm, other tolerances, ShapeFix nor sewing closes it, so R17's mass model uses link 2's convex
  hull (139 g for 19.8 g). R17 still passes. The real fix is to find the offending face pair in the glued bar.

## 10^5 pin-knee configs on GPU pods confirm the in-sample corner; its gain over H1 shrinks from 4.2 to 0.9-1.3 points held out (2026-10-16, tools/gpu_knee_search.py, run gks1)

* **What ran.** 101,240 configurations returned a report. The objective was the near-touch gap on Bench(110,360),
  same-bench, through the GPU port (parity 0.0 with the CPU kit), with every clip frame kept followed. Free: the 13
  continuous parameters plus the fold margin (>= 5); fixed: O20, J1 on the back / acromion top. The configs came from
  three stages:
  * 67,214 scored Sobol points around the seven leaders' basins and over the whole bounds;
  * CMA in 30 basins, 80 generations each, stopped by the deadline;
  * the top 10 distinct plus H1 run by the CPU kit, exact frozen, on the pods' CPUs. This is self-measured.
* **Sobol finds no better basin.** No Sobol point beats G3, the 20.81 polish best: the best Sobol point is 23.31. The
  wide points' best is 59.2.
* **Every CMA basin ends in the same corner.** That corner is a long E strap: lE 65-80, ang_min 22-37, J2 seat az2
  30-40. 12 of the 30 basins end below 22.
* **The fold margin goes to the floor.** The free margin ends at 5.0-5.4 deg in every top-10 config: the 5-deg ruling
  binds, and more margin only costs reach.
* **Exact frozen numbers, same batch, against H1:**

  | protocol | best | H1 | gain |
  |---|---|---|---|
  | fit Bench(110,360) | F2 20.26 / near-touch 20.81 | 24.48 / 25.59 | 4.2 / 4.8 |
  | fit Bench(60,160) | F2 23.34 / 24.46 | 27.20 / 31.75 | 3.9 / 7.3 |
  | held-out disjoint poses | F7 27.22 / 29.04 | 28.55 / 31.06 | 1.33 / 2.02 |

  F2's own held-out number is 27.65 / 29.25, a gain of 0.90 / 1.81.
* **Other checks.** Reach on Bench(110,360) is 0.703-0.711 against H1's 0.669, and overhead workspace reach is 0.29-0.32
  against 0.25. Every clip frame is followed. The continuity flood fill leaves 0-3 islands.
* **Lesson: the same-bench objective overfits.** The corner G3 found overfits the 470 search poses: 7.4 points worse
  held out, where H1 is 4.1 worse. This is the third polish to show it, after P5 and polish 2.
* **Candidates.** F7 (held-out score 90.10 vs 89.62) and F5 (held-out gain 1.04) are candidates for the independent
  verifier. The next pin-knee polish must use a held-out-aware (2-fold cross-fit) objective.
* **Instrument lesson: one grid copy per GPU worker caps the workers.** Each worker held its own 1.06 GB int8 copy of
  the Bench(110,360) grid, so one worker per vCPU (31 on a 32 GB card) failed on CUDA out-of-memory. The errors were
  fast, which made the log show 77 "evals/s". After the cap, a card ran 10 workers and 13-14 evals/s. Sharing one
  device grid per GPU through CUDA IPC (GridDev already takes a shared tensor) is the next speed-up. Pod cost about
  $2.6.

## The pin-knee GPU polish's held-out gain is the knee's singularity margin, not a better shape (2026-10-16, independent verifier)

* **Reproduced to the digit.** The CPU kit on the farm, with unchanged harnesses, gives every number the GPU polish
  claimed. On the polish protocol F2 is 20.26 / near-touch 20.81 against H1's 24.48 / 25.59. Held out, F2 is 27.65,
  F7 27.22 and F5 27.51, against H1's 28.55.
* **Where the gain comes from.** The search lowered the knee window ang_min from 30.5 to 22-23 deg, close to the
  polish bound of 20. The taken knee then runs to 157 deg, 22.7 deg from the straight singular posture, against H1's
  31.6 deg.
* **The test.** Put H1's window (ang_min 30.46) back on F2 and F7:
  * the polish-protocol gain falls from 3.7-4.2 to 0.57;
  * the held-out gain falls to -0.08 (F7) and -0.73 (F2).
* **The fold floor.** At the old 10-deg fold margin, both configs lose to H1 by 1.7-2.5 points.
* **Lesson.** A bound a search tool sets for itself (ang_min >= 20) is not a ruling. A margin that guards a singular
  posture must be fixed in the objective, or the search spends it to buy reach (CLAUDE.md: the user must have their say
  first). The next polish (cross-fit) should hold ang_min >= 30 unless the user rules otherwise.
* Raw data: `docs/research/verify_gpuknee/`. The row fields are `v_gpuknee_*`.

## The knuckle BDp is verified, the new leader: 19.54 with buildable stops (19.06 at the rule), held out 24.18 vs H1 31.39 (2026-10-16, minarc-stop-knuckle-4r BDp, judge)

**Claim.** Config BDp:
- variant B: the pin knee plus a spring knuckle K in link 1;
- both J2 stops at the 5-deg J1-J3 kit margin, as a physical dowel in a q2 slot;
- hub K's cap 6 mm taller for a 0.3 x 5 mm clock strip.

Claimed 19.06 frozen exact on Bench(110,360). Two independent lenses checked it, and the judge combined them.
**Verdict: CONFIRMED, the new VERIFIED LEADER.**

Raw data:
* the lenses: `docs/concepts/verify/minarc-bdp-{remeasure,buildability}.md`;
* the judge: `docs/concepts/verify/minarc-bdp-judge.{py,md}`, with its farm runs in `minarc-bdp-judge/`;
* the merged ruling: `rows/minarc-stop-knuckle-4r.json` `v_kitrule_*`, status verified.

What was measured:
* **The claim reproduces to the digit in two harnesses.**
  * The re-measure lens used its own harness (frozen hand-over by `__dict__` diff, frame-based checks, its own flood
    fills).
  * The buildability lens used the claim's `run()` path plus an independent K / q2 closure.
  * Both get 19.06 (score 93.07) and held out 23.24, against H1's 31.39 in the same harness. H1 is 27.20 on the bench.
  * The judge recomputed every gap from its components with the bench's `gap_of`.
* **Every rule holds.**
  * The minimum own-state J1-J3 margin is 5.007, with 0 poses under 5.
  * Continuity: 1041 of 1041 grid nodes connect kinematically and 1014 of 1014 contact-aware, with 0 islands and 0 taken
    poses dropped.
  * The forced state is the spring's unique minimum-energy equilibrium. Lens 2 scanned th 0-180 and found 0 multiple
    equilibria and 0 mismatches.
  * The margin-10 reading is 22.40, against H1's 28.21.
* **The stops as built cost +0.48.** This is measured by the judge: six farm jobs of the re-measure harness, about
  $0.10.
  * As modelled, K's stop B (dK 62.83) engages at an effective-dyad margin of 2.74 deg, below the rule. Moving it to
    dK 34.47 (a1max 54.748) is free: the run gives 19.06, identical.
  * The J2 stops sit exactly at 5.00, so a slot cut long breaks the rule. A buildable slot is drawn 5.0 +0.5 / -0 deg of
    margin, which is about 1.5 deg of q2, or 0.2 mm at the dowel.
  * The worst built pairing is J2 at 5.5 with stop B at 34.47. It measures **19.54 (score 92.89)**: reach 0.7222, follow
    1.0, in-band14 0.8931, contact 0.0107, near-touch 26.44. **Held out it is 24.18** (near-touch 28.86).
  * The J2 stops alone at 5.5 give 19.29 (held out 23.36); at 6.0, 19.53. The cost is in-band, about 0.47 points per
    degree; reach does not move.
  * A tighter band (0.05 mm at the dowel) would recover most of the +0.48. That is a CAD and compliance choice.
* **The spring is buildable** at a rate of 0.015 N.m/rad or less, in +C1900 temper. The demand is at most 0.044 N.m
  against the 0.08 N.m preload.
* **What stands, disclosed.**
  * Hub 2's wall is 0.05 mm from the skin at the overhead raise peak. This is the same as BD, and the held-out set
    repeats the pose.
  * 99 of 371 taken bench poses sit under 10 deg of margin.
  * The folded stop never engages.
  * K is sensed, so the chain is 4 active DOF, at the cap. Complexity is 33 against H1's 19.5.
  * K adds no overhead reach: every taken pose at elevation 140 or more has K closed.

What it means:
* The knuckle beats the pin knee by 7.7 points on the bench and 7.2 held out, with buildable stops and 0 passive
  translations. It is the first design verified above score 92.5.
* It is 5.8 points short of the golden 13.75, at a complexity far from 0.
* **Protocol lesson: a stop placed exactly at a rule is not a buildable stop.** From now on every claim prices its stops
  at the rule plus a unilateral tolerance, together with every other stop the tolerance moves (here K's stop B).

Next:
1. The 2-fold cross-fit near-touch polish of BDp, with the stops as design variables. It must clear the hub-2 pinch.
2. The gen-4 L1 CAD and stills.
3. The user's ruling on the sensed 4th joint.
4. The cam-stop-knuckle lens: K driven from q2, 3 active DOF.

## A 2-fold cross-fit polish does not travel either: the held-out drop is a workspace-sample shift, not shape over-fit (2026-10-16, tools/crossfit_polish.py, docs/research/crossfit_polish.md)

* **What ran.** The new final-polish objective fits the shape on one stratified half of the search poses
  (Bench(110,360) U Bench(60,160), 634 poses) and scores the near-touch gap frozen on the other half, and vice versa.
  The continuity flood fill is on. The held-out set is asserted untouched.
* **The search.** Short CMA on the pin knee from H1, F2 and F7: 587 evaluations on the farm. The best of each start
  went through the polish verifier harness (unchanged) held out. Self-measured; farm about $0.18.
* **Measured.** The cross-fit picks lose to H1 held out:

  | pick | held out | gain over H1 (28.55) |
  |---|---|---|
  | XP1 | 29.50 | -0.95 |
  | XP2 | 29.59 | -1.04 |
  | XP3 | 61.67 | -33.1 |

  The in-sample picks gained P5 +0.16 (exact-fit protocol; -0.27 fast-fit), C1 +0.33 and F7 +1.33. Both XP1 and XP2
  drop 8.0 points from the polish bench to held out. Over these 7 configs, the cross-fit objective's rank correlation
  with the held-out near-touch gap is -0.07; the in-sample objective's is 0.50.
* **Why: the shape does not over-fit within the sample.** In-fold vs out-of-fold near-touch correlate at 0.984 over the
  587 rows, mean difference 0.04 points.
* **Why: the benches' workspace sample is aliased.** Its `linspace` pick over the grid order skews axial rotation:
  * |axial| >= 150 deg is 6.0 % of the pool vs 11.0 % of the held-out set;
  * axial -90..-45 is 33.1 % vs 27.9 %.

  Kinematic closure is 4.9 (H1) to 6.9 (P5, F2) points lower on held-out workspace poses for every config. Polishes
  buy 1.2-2.0 points more closure on the pool than held out, and the fitted shape then touches skin on the newly
  closed held-out poses: contact 0.019-0.031 vs H1 0.011. A split of the pool carries the same aliasing, so it cannot
  see this; CMA then selects on fold noise.
* **New failure: the claim fit can collapse.** XP3 is fine on both 317-pose fold fits, but its shape fitted on all of
  Bench(110,360) collapses (56.02; in-band 0.61). The tool now applies a claim-fit guard by default: XP3 25.25 -> 53.09,
  every other config unchanged.
* **Next instrument (not built).** A fresh jittered sample of the whole workspace envelope (grid pose +- 7.5 deg, no
  grid pose reused) matches the full grid's closure within 0.005 for every config. Use it as the search bench (own fast
  cache); the held-out set stays untouched. The minarc BDp cross-fit recipe is ready
  (`python3 tools/crossfit_polish.py farm minarc ...`) but NOT launched; run it only with the held-out acceptance.

### Cross-fit polish - independent check (2026-10-16, `docs/research/crossfit_polish_check.md`)

* **Not refuted: the conclusion and the held-out numbers.** Re-measured on the farm with the verifier harness
  unchanged (held, 1154 poses, worn exact; about $0.05). Every number matches to the digit:
  * H1: 28.55 / near-touch 31.06.
  * XP1: 29.50 / 32.22. The same at margin 5.0.
  * XP2: 29.59 / 30.95.
  * The cross-fit objective re-scores: H1 28.13, XP1 22.895.
  * Each pick ends WORSE held out than its own start: XP1 by 1.85 against F2 (27.65), XP2 by 2.37 against F7 (27.22).
    XP2 was found in generation 2, so it is a near-random step chosen on fold noise.
* **The held-out set stays out.** The picks are the objective's argmins. The folds are deterministic, 317 / 317, and
  every stratum is within +-1. Two small caveats:
  * The continuity flood fill sees the held-out workspace poses' KINEMATICS (the rule's own full grid).
  * The F2 / F7 starts were chosen after their held-out numbers were known.
* **Correction: in-fold against out-of-fold.** "0.984 / +0.04 over all 587 rows" is in fact the subset of rows with
  both gaps < 100. Over all 587 rows it is 0.996 / -1.51 (degenerate rows). On the working range (< 40, 554 rows) it is
  **0.854, mean +0.17 points**. The conclusion stands: shape over-fit is about 0.2 points.
* **Correction to the diagnosis: the axial skew is only the common part of the held-out drop.** The claim had no
  control, because every config it measured was polished on the pool. This check adds 16 configs never optimised
  (random draws around H1) and measures kinematic closure (`docs/research/crossfit_check/closure_control.json`):
  * The pool-minus-held closure gap is 0.036. Re-weighting the held-out set to the pool's axial mix leaves 0.006, so
    the skew explains it.
  * The 7 polished configs have a gap of 0.062. Re-weighting leaves 0.027, which is **selection on the pool's own
    poses**: any search over a fixed sample earns it, and no split of that sample sees it.
* **Consequence.** A fresh jittered search bench removes the skew, but if it is searched as a fixed sample it will be
  over-fit again. **Choose the pick on a second fresh draw the search never scored**, then accept held out. The
  CLAUDE.md "2-fold cross-fit" line guards a 0.2-point effect; rewording it is a rule change for the user to see.

## The envelope-bench polish of minarc BDp: pick1 gains +2.37 held out (+1.49 on BDp's own protocol), self-measured (2026-10-16, tools/env_bench.py, tools/env_polish.py, docs/research/minarc_final_polish.md)

* **The bench.** `env` is a fresh stratified draw of the continuous workspace envelope: 420 poses plus the 110 clip
  frames of Bench(110,360).
  * Its strata are the drawn pose's elevation x plane x signed axial band, with the grid's quotas. A uniform
    continuous draw under-samples the lattice's boundary rows (6.7 % vs 9.4 % with |axial| >= 150).
  * No pose lies within 2 deg of a held-out pose, by coordinates or by humerus orientation.
  * It matches the full grid on every band: |axial| >= 150 9.3 % vs 9.4 %; Bench(110,360) 7.5 %; held out 11.0 %,
    since the held-out set is the grid minus the aliased benches and so skews the other way.
  * A second, disjoint draw `envsel` (360 poses) is the pick-selection bench.
  * Fast caches on the farm: $0.10, validated (p99 1.1 mm).
* **As a predictor of held out, env is not reliably better.** The bench -> held drop:
  * BDp: +1.36 on env vs +4.64 on Bench(110,360);
  * H1: +5.17 on env vs +4.19.

  A 420-pose reach share has a ~2-point binomial error, the size of the skew itself. Fitting the shape on env
  instead of Bench(60,160) lowers both held-out numbers (BDp 24.18 -> 23.68, H1 31.39 -> 30.04). That is a
  measurement change, not a design change.
* **The polish.** CMA on env, in-sample, 3 starts (BDp, F2 seats, F7 seats), 787 evaluations, $0.20.
  * Objective: near-touch, continuity (grid flood fill plus a slerp edge from each fresh pose), O20, claim-fit guard.
  * Stops are variables >= 5.0, priced like the judge: the slot is built +0.5 and read at rule 5.5, and K's stop B
    is drawn at the 5-deg rule cut (BDp: dK 34.47, reproduced).
  * Every start stopped on patience (10 generations without a gain > 0.02) in a different basin (18.0 / 20.8 / 21.8).
* **The claim.** The top 3 distinct picks (ranked on envsel) + BDp, in one farm batch through the judge's harness
  (unchanged, benches swapped). BDp reproduces its verified 19.54 to the digit. Results (gap):

  | pick | held out, env fit | held out, fit 60 (BDp's protocol) | Bench(110,360), fit 60 |
  |---|---|---|---|
  | BDp | 23.68 | 24.18 | 19.54 |
  | **pick1** (from F7) | **21.31** | **22.69** | **18.40** |
  | pick2 | 23.68 | - | 21.42 |
  | pick3 | 24.51 | - | 21.77 |

  pick1's near-touch: 23.02 held out (env fit), 26.73 (fit 60), 23.36 on Bench(110,360). Its held-out gain over BDp
  is **+2.37 / +1.49** gap points; the bench score is 93.31 vs 92.89.
* **pick1 under the rules.**
  * Margin >= 5.586 vs the 5.5 priced rule; 0 knock-outs.
  * Continuity 1106 / 1106, 0 islands.
  * J1 seat on the acromion top (anterior 0.076).
* **What the gain is.** Reach (+4.5 points held out), partly paid in skin contact: 3.0 % vs 1.1 %.
* **Red team for the verifier.**
  * Contact triples.
  * K opens to 56.6 deg vs 34.1, so the spring winds further and the forced J1 swing needs re-measuring.
  * In-band 2-10 drops from 0.57 to 0.50.
* **New knowledge: the independent selection draw is what makes a polish travel.** The search objective is
  optimistic by 3.4-4.1 points for every polished config. The envsel number predicts the held-out near-touch within
  0.6-2.5 points (mean 1.75), in the right rank order for all 4 claimed configs.
* **Status.** Self-measured. Under the CLAUDE.md final-polish rule, pick1 replaces BDp's CAD config only after an
  independent verifier confirms the >= 1 held-out gain and clears the red team. Farm total about $0.58.

## minarc final polish verified: pick1 replaces BDp's CAD config (2026-10-16, independent verifier)

* **What was checked.** An independent skeptic re-ran pick1 (envp-F7-g35-6) and BDp through the judge's harness,
  imported unchanged, with the judge's built-stop pricing. Its own bench wiring:
  `docs/concepts/verify/minarc-final-polish-verify.py`.
* **The claim reproduces to the digit.**
  * Held out, env fit: pick1 21.31 vs BDp 23.68 (**+2.37**; near-touch +3.85).
  * Held out, fit Bench(60,160): 22.69 vs 24.18 (**+1.49**; near-touch +2.13).
  * Bench(110,360): 18.40 vs 19.54 (score 93.31 vs 92.89).
* **New checks, none of which bites.**
  * Contact-aware continuity drops 0 poses for either config.
  * Own-state margin >= 5.586 on every counted pose.
  * Knee inside its window everywhere (min margin 1.11 deg).
  * The spring cannot sit lower on any forced pose.
* **Bench integrity.**
  * env never reuses a held-out pose.
  * env poses stay >= 2.23 deg per coordinate and >= 2.04 deg in thorax orientation from every held-out pose.
  * Measured in glenohumeral orientation, 2 env poses sit 1.66 / 1.97 deg from a held-out pose. The fit-60 gain does
    not depend on env.
  * The draw and the picks were frozen before any held-out reading.
* **What the gain costs.** The gain is reach (+4.5 points held out). The bill:
  * Skin contact on 28 vs 9 held-out poses, all extreme workspace poses and none on an ADL clip. The deepest are
    overhead at elevation 165, -14.6 mm vs -7.3.
  * K travel 56.6 vs 34.1 deg: the spring and the forced J1 swing need re-measuring.
  * R1-aim -0.03 to -0.08.
* **Status.** CONFIRMED under the final-polish rule. pick1 is the CAD config (row `polished_*`); the verified BDp
  record stays. Verifier farm cost: $0.25.

## pick1 red team: the extra contact is the extra reach, no CAD lift pays, and the spring needs 0.010 N.m/rad in +C1900 (2026-10-16, docs/research/minarc_pick1_redteam.md)

* **Contact, attributed per part on the 1154 held-out poses** (`docs/concepts/verify/minarc-pick1-redteam.py attr`;
  every baseline reproduces the verified numbers to the digit).
  * pick1 touches on 28 poses (env fit) / 35 (fit 60) vs BDp 9 / 13. All are workspace-envelope poses; the nearest
    daily-clip frame is 11.2 deg away (one fit-60 contact, -0.02 mm, sits 8.4 deg from a "Comb hair" frame).
  * 19 of the 28 are poses BDp cannot close at all; 20 sit in the stretched state (K open 9-54 deg). The extra
    contact is the extra reach.
  * Deepest: hub K's SIDE wall into the raised deltoid at elevation 165 (-14.6 mm; BDp -7.3), and the arm-mounted knee
    link / pad into the chest wall with the arm across the body at elevation 15-30 and extreme internal rotation
    (-10.0 mm, K open 41-54 deg). Both structural: lifting hub K 7 mm moves its deepest from -14.58 to -14.23 mm, and
    no hub level moves an arm-fixed part.
  * Shallow ones: link 2 / hub 2 into the scapula on overhead across-body poses (-0.1 to -3.6 mm), and link 2 into
    the shoulder cap behind the back (shared with BDp).
* **Fixes priced on both protocols: none pays.**
  * Best lift (hub K +3, link 2 + hub 2 +2 mm): held out 27.47 (env fit) / 26.16 (fit 60), Bench(110,360) 22.52, vs
    pick1's 21.31 / 22.69 / 18.40. Lifts cost 4-20 points of in-band for a few contacts.
  * Earlier K stop B (40 / 45 / 50 deg): held out 23.34 / 22.76 / 22.45, bench 18.60 / 19.60 / 18.98. Stop B at 40
    removes every knee / pad contact (18 contact poses) but keeps only +0.34 held out over BDp, below the 1-point rule.
  * Capping K at BDp's 34.5 deg would lose about 3.2 held-out points: K's travel is the gain.
* **Spring at K 56.65 deg.** Return demand on pick1's shape: 0.048 N.m (2 g, worst direction, + 2 mN.m per sealed
  pair; BDp 0.040), so the 0.08 N.m preload keeps 1.67x.
  * The specified 0.015 N.m/rad strip reaches 1264 MPa at stop B: inside +C1900's 0.7 Rm (1330) by 5 %, over +C1700's.
  * **Use 0.010 N.m/rad: 217 mm of 0.3 x 5 mm 1.4310 +C1900, 0.08 N.m preload, 1198 MPa.** It fits the same 6 mm cap
    (36 % annulus fill).
  * K opens on "Reach a high shelf" (15.8 deg at up to 52 deg/s; BDp 0.85) and on "Wash opposite shoulder" (6.2 deg).
* **Forced J1 swing and feel at real timing: not worse than BDp.**
  * Forced J1 gain max 2.29 vs 2.55 deg/deg: 31 vs 35 deg per 10-fps frame at the clips' peak arm speed (136.5
    deg/s). The steepest J1 gain of both designs is in state A (3.3-3.4).
  * Cuff force: 0.24 / 1.99 N in state A / forced (BDp 0.32 / 2.35; the forced value is the preload reflected).
  * J2-stop impact: 0.24 vs 0.31 mJ.
* **Verdict: pick1 is buildable as the gen-4 CAD config** with the spring respec and K stop B built at 56.65 deg. The
  fitted levels stay. Disclosed: deeper contact on extreme envelope poses, already priced in the gap, and R1-aim
  0.497 vs 0.574 held out. Farm $0.27.

## Round 6: a sensor-free knuckle is verified at 3 active (23.57, score 91.4), at twice H1's complexity (2026-10-16, discovery round 6, closer)

Raw data:
- rows: `docs/concepts/rows/{geneva-tail-knuckle-pinknee-3r,cam-unfold-4th,j3-neck-over-3r,geneva-tail-knuckle-3r}.json`;
- verifier harnesses and outputs: `docs/concepts/verify/<id>.py`, `docs/concepts/verify/<id>*`;
- the round table: `docs/concepts/ROUNDS.md` "Round 6 results".

All numbers are frozen exact on Bench(110,360), at the 5-deg margin with O20 hubs only, fitted on Bench(60,160).

**What was measured**

* **geneva-tail-knuckle-pinknee-3r, rod embodiment: VERIFIED 23.57 (score 91.43), the round winner.** It is the pin knee
  plus a knuckle K in link 1. A spiral lobe in hub 2's O20 stack drives a rocker on link 1b, an O3 pushrod with M3 rod
  ends, and a horn on K's cap. K is slaved and never read.
  * 3 active DOF, 0 passive translations, complexity 42.5.
  * Reach 0.731, follow 1.0, in-band14 0.844, contact 0.011, overhead 8 of 28. Held out 28.12.
  * On the same protocol H1 is 27.20 (held out 31.39), so the 3-active class moves by 3.6 points. The sensed knuckle
    (pick1 18.40 / BDp 19.54, 4 active) stays 4-5 points ahead.
  * The verifier moved the horn and rod-end head out of K's spring cap (+0.20). The full-grid continuity drops 0
    poses.
* **cam-unfold-4th: VERIFIED 26.70 (score 90.29), 3 active, complexity 33.75.** K sits on link 2 as a two-sided crown cam
  with K = c(q2). Inverting the exact table gives one configuration per pose, so the verifier read back the cam law
  with 0.00 deg of error. The design ties H1.
* **j3-neck-over-3r: VERIFIED 28.46, but 4 active (K sensed).** Metal touches the skin (0.00 mm) and overhead reach is
  0.18. Not a contender.
* **geneva-tail-knuckle-3r: DEAD at 53.32 frozen** (39.34 fast, reproduced). It has the sensor-free law but no pin knee,
  and its J3 side is out of band (link 2 0.33, neck 0.23).

**What failed and why**

* **The Geneva tail.** Rigid with link 2, it sweeps a cone about u2 across J2's whole range. One workspace pose needs
  the tip 92 mm from GH, against hub K at 55-60 mm, so the tail is 0.0-0.25 in band.
  * Cost: 10-42 points on pick 1, 9.3 on pick 2.
  * **Rule: price a follower by its swept volume.** Put coupling elements inside existing hub stacks (the hub-2 lobe
    cost ~4.7), or on members that do not sweep a joint's range.
* **A hub on link 2.** It moves with q1 x q2 and sweeps a 2-D skin patch with 19-35 mm of height spread under it.
  * It is in band only 21-40 deg from J2. Toward J1 it clashes with hub 1; along link 2's line it has no leverage on
    a2.
  * The same disc on link 1 is >= 0.92 in band. **Fold levers belong on link 1 or at J2.**
* **The J3 side without the pin knee.** Hub obliquity law: a flat O20 hub is in band only if its axis meets the skin
  within ~25-30 deg of the normal (hub 3: 0.64 / 0.69 / 0.82 at 39 / 30 / 16 deg).
  * The seats that satisfy it (wd 58-71) cost overhead: 0.36-0.39 -> 0.18-0.25.
  * Seat choice cannot buy both, so the pin knee stays on every competitive knuckle.
* **The crest basin is an O15 artefact.** At the same seats hub 2 is 0.9975 in band at O15 and 0.03 at O20.
* **Idle-drive search optima.** A slaved-spare CMA that did not require the drive to engage found 16.10: a plain 3R
  with an unscored link 1b. Such objectives must penalise an idle drive, and a link with 0 samples is flagged.

**New knowledge**

* **A positive-drive cam gives a two-sided fold law** (a spring knuckle cannot). On cam-unfold-4th the folded-end lobe
  took 18 fit poses and most of the +8.8 points over the same-seat controls (rigid K 30.81, no K 30.85).
* The winner has no folded lobe, and 84 of its 112 lost poses are fold. Its folded-side lobe on the same hub-2 rim is
  round 7's lead lever. Target: reach >= 0.80 at in-band >= 0.85 and contact <= 0.01, i.e. gap <= 16 (score 94.2).
* **Pressure angles at O20 size:**
  * a lobe inside O20 caps kK at ~3-3.5;
  * a crown cam at slope 1.5 runs ~41 deg (23 deg with a 2:1 lever);
  * a one-tooth Geneva entry (psi_c 4-8) reaches dK 56 within 45 deg.
* **The fast-to-frozen loss persists at 4.7-7 points.** Overhead is 8 of 28 on every round-6 design.

## Judge fixes: split members now count in R1, the dynamics judge runs any hinge chain, the cut BOTTOM is one solid (2026-10-16, MEASUREMENT changes, no design changed)

Found by the gen-4 CAD and its verifier (`pipeline/full-exo/designs/user_minarc_bdp/VERIFY.md`). Every number below moved
because the MEASUREMENT changed; no part, shape or configuration changed.

**R1 / R1-aim / R4 (`score_design.py`).** The judge kept only groups named `base`, `l<digits>`, `H`, `cuff`, so minarc's
split members `l1a` / `l1b` (links 1a, 1b, hub K and its 6 mm taller cap, the K and J2 lower plates) never counted. New
rule (`pipeline/full-exo/metal_groups.py`): every group the chain poses in clips.json is scored, H within 110 mm of GH as
before, and any other exo.glb group must be listed in `EXCLUDED` with a reason (today only `F`, the forearm parts) or the
judge stops; a scored group missing from a frame also stops it. `BANDS=10,14` scores both bands in one pass (identical
numbers, half the time; `tools/judge_all.sh` uses it). Regression: user_pinknee_h1b (no split groups) reproduces
bit-identically (77.564 % at step 30, old and new code). Re-judged at step 3 on the farm:

| design | R1 (2-14 mm) | R1-aim (2-10 mm) | R4 (Raise overhead, 14 mm) |
|---|---|---|---|
| l1_minarc-bdp | 72.4 -> **80.5 %** | 38.6 -> **52.5 %** | 71.4 -> **72.7 %** |
| user_minarc_bdp | 71.7 -> **80.0 %** | 37.5 -> **51.0 %** | 70.0 -> **72.0 %** |

These reproduce the verifier's own re-measure (80.04 / 50.96 / 71.98 and the L1's 80.51 / 72.74). Still FAIL (90 % / 80 %
needed). The gen-4 "R1 below gen 3" story was this blind spot: the minarc CAD is 3.3 points above h1b's 76.7 %. Also
affected when re-judged: `param2_r20_n3_s1414_4` (its base group is named `S`; now counted). `r1_decompose.py` uses the
same rule and now applies the per-group offsets T.

**R17 / R11 (`judge/dynamics.py`).** The judge modelled only the spherical az/el/a chain (`KeyError 'l1'` on minarc) and
judged the pin-knee designs as their orientation-equivalent spherical 3R (its own `chain_vs_clip_G` mismatch was 10.7 /
33.0 deg on h1's links). New general chain (`GenDesign`): the clips' own members in serial order + the arm (canonical
humerus at GH), every adjacent pair joined by the hinge FITTED to its relative motion over all frames - minarc J1, K, J2,
J3, pin a, pin b and h1b J1, J2, J3, pin a, pin b all fit as pure hinges to 1e-4 deg / 3e-4 mm; the knuckle K gets its
clock spring (0.08 N.m preload at stop A; rate 0.015 nominal, 0.010 also run) and stops A / B (0 / 34.47 deg), J2 its q2
stops (125.8 deg window), as joint limits. Cross-check (`judge/test_dynamics.py --general`): on the spherical 3R
band_r14_3r_s1351_1 the general chain reproduces the original path (constant friction: M_GH peak 0.207 / 0.207 and
0.221 / 0.221 N.m, rms within 0.003; rolling: within the summaries' rounding). The 3-joint path is unchanged:
`test_dynamics.py --fast` PASS (analytic hinge, transmission p95 0.0015, wedge OK). Two more measurement fixes found on
the way: (1) part masses from a STEP tessellation with hairline seams (link 2: 0.87 mm of open edge) took the convex hull
of each open piece - link 2 weighed 121 g instead of 21 g; whole-part integrals now (1a 12.7, 1b 23.8 incl. hub K's
hardware, 2 28.8 g with its hub stacks); (2) numbered machined parts (D8-...) take their stated alloy, never a feature word
("O3 magnet pocket", "dowel holes", "sleeve bores" made link 1a NdFeB and the knee link iglidur).

| design (nominal: rolling mu 0.005, speed 1) | M_GH peak | cuff force peak | cuff twist peak | K drift vs plan | R17 | R11 (kPa, with arm parts) |
|---|---|---|---|---|---|---|
| l1_minarc-bdp | NOT RUN -> 0.152 N.m | 0.69 N | 1.96 deg | 2.13 deg | NOT RUN -> **PASS** | NOT RUN -> 0.399 **PASS** |
| user_minarc_bdp | NOT RUN -> 0.153 N.m | 0.70 N | 2.00 deg | 2.17 deg | NOT RUN -> **PASS** | NOT RUN -> 0.272 **PASS** |
| l1_skin-normal-3r-pin-knee-h1 | 0.040 -> 0.049 N.m | 0.11 -> 0.22 N | 0.94 -> 1.50 deg | - | PASS -> PASS | 0.349 -> 0.351 PASS |
| user_pinknee_h1b | 0.035 -> 0.046 N.m | 0.10 -> 0.22 N | 0.81 -> 1.39 deg | - | PASS -> PASS | 0.213 -> 0.216 PASS |

What the knuckle does: K never leaves stop A in any clip (on its stop 100 % of the time). On the 8 frames of Wash where the
plan opens K by up to 2.2 deg with J2 on its stop, the 0.08 N.m preload is more than the cuff's soft tissue resists (0.03
N.m/deg torsion: 2.7 deg of twist), so the cuff twists ~2 deg instead of K opening - inside R17's 5 deg; K's "stalls" are
these 66 ms lags of <= 1.6 deg (none >= 10 deg). The spring rate (0.010 vs 0.015 N.m/rad) changes nothing on the clips.
The pin-knee numbers rose (knee link, member 3 and the J3 offset now carry mass and leverage) but stay 20x under the 1 N.m
bar. Not modelled in the general chain: member-member contact (R6 judges it, 0.0 mm) and the knee stop (149.5 deg, not
in the CAD either). Designs with passive slides (osn, rail elbow) are refused by the hinge fit and fall back to the
spherical approximation, labelled in their dynamics.json "chain".

**R7 (cut BOTTOM).** The inherited BOTTOM tessellation (from l1_seed-offset-3r-slides) carries 6 zero-area slivers that
make 6 non-manifold edges (7 open pieces); the L1 slicer worked on the unmerged mesh and capped each cut loop with a
centroid fan, which overlaps itself on the channel's non-convex section. `build_pinknee_l1.slice_capped` cleans the mesh,
clips each triangle at the plane with one vertex per cut edge, and caps every section loop by ear clipping (holes bridged).
`pipeline/concept_l1/repair_cut_bottom.py` re-cut the two cut L1s in place (same source mesh, same plane recovered from the
old cut to 4e-6 mm): l1_minarc-bdp and l1_skin-normal-3r-pin-knee-h1 BOTTOM 7 open pieces -> one closed solid (21.02 /
22.50 cm3), R7 FAIL -> **PASS**; the three uncut L1s carrying the same mesh (l1_skin-normal-3r-pin-knee, its k4598-m5,
l1_offset-skin-normal-3r) were cleaned (geometry unchanged) and pass R7 under the current rule. R1 is unaffected (no H
metal within 110 mm of GH on these designs); R2 / R6 / R16 were not re-run: the new cap only removes the old fan's phantom
faces inside the channel notch.

Scorecards: l1_minarc-bdp 4 -> 7 of 19 (R7, R11, R17), user_minarc_bdp 5 -> 7 (R11, R17), l1 h1 7 -> 8 (R7), h1b 8 -> 8.
Open: R8 of user_minarc_bdp still reads parts_full.json's keyword-material masses (239.1 g; the verifier's 202.6 g) - the
builder's material rule needs the same fix as the dynamics judge's.

## Round 7: the fold relief is walled by geometry, not by K's law; the rod is the cheapest drive at O20 spacing (2026-10-16, discovery round 7, closer)

Raw data:
- rows: `docs/concepts/rows/{frontload-lobe-stopb-knuckle-3r,rim-lobe-arm-knuckle-3r,split-knuckle-twosided-3r,k-rim-lobe-stub-knuckle-3r}.json`;
- verifier harnesses and outputs: `docs/concepts/verify/<id>.py`, `docs/concepts/verify/<id>*`;
- the judge's red team: `docs/concepts/round7_ideation.md`;
- the round table: `docs/concepts/ROUNDS.md` "Round 7 results".

All numbers are frozen exact on Bench(110,360), at the 5-deg margin with O20 hubs only, fitted on Bench(60,160).

**What was measured**

* **frontload-lobe-stopb-knuckle-3r: VERIFIED 22.82 (score 91.70), the round winner.** 3 active, 0 passive
  translations, complexity 49 (tool). Reach 0.728, in-band14 0.855, contact 0.011, overhead 8/28. Held out 26.75.
  * It beats the round-6 lead (23.57) by 0.75, but the best configuration IS the round-6 rod drive on re-fitted seats.
    The control (the winner's linear law re-fitted under the same rules) scores 22.92 frozen.
  * Lever by lever, on the same seats: front-load 0.01, stop B 0.00, a 2:1 rocker -1.2 fast.
  * The gain is below the 1-point CAD-replacement rule. The verifier moved the claim's rod and rod-end head out of K's
    spring cap (+0.10).
  * Red team (from the verifier's audit): it is 0.75 better at the 1 mm near-touch rule (24.46 vs 25.21), but 5.2
    worse when metal under 2 mm counts as contact (44.08 / 34 poses vs 38.84 / 28). Held out the same holds: 29.39 vs
    30.31, and 46.73 vs 42.01. Min metal is 0.30 mm (0.14 held out). Part of the re-fit's in-band is proximity.
* **rim-lobe-arm-knuckle-3r (direct pair, no rocker, rod or rod ends): DEAD at 20.57 fast / 26.21 frozen.** Against
  the rod's 16.53 / 23.37 on the same protocol. Complexity 35.25 vs 46.75. Audited: 20.57 reproduced exactly, the
  convergence gate passes per run, and no bug was found.
* **split-knuckle-twosided-3r (a second knuckle K2 on link 2 for the folded end): DEAD at 26.62 / 34.18.** Fold losses
  are 84 = the winner's 84. Complexity 68.5.
* **k-rim-lobe-stub-knuckle-3r (lobe on link 1a, roller on a link-2 stub): VERIFIED 44.79**, not a contender. Follow
  0.873 frozen: roller-vs-lobe collisions in state A take 32 poses.
* **two-rise-lobe-pinknee-3r (a folded second rise on the winner's hub-2 lobe): dead at ideation**, measured by its
  proposer. 0 folded poses under the winner's msub rule, hub 2 needs 63-70 mm, and the 750-design re-seat scan's best is
  33.46 fast.

**What failed and why**

* **A direct cam pair between two O20 stacks (~38 deg apart).**
  * The pressure angle forces the follower arm 20-35 deg off the line of centres (aimed along it, the angle is 90
    deg: an idle drive), so the follower sits >= 19 mm from the cam axis.
  * On this body the skin under hub 2 rises 6-14 mm beyond ~27 mm from u2. A plate swept about J2 is either 18 mm
    over the skin (8 % in band) or lifted off the ring.
  * Capped at 31 mm, K travels 25.9 deg instead of 36, and reach is 0.731.
  * A groove embodiment's dwell flange (93 deg of q2) sweeps the body: best 95.51.
  * **The rod (a strap) carries a slaved-K law more cheaply than any swept plate.**
* **Any follower rigid with link 2** pays for link 2's whole q2 sweep, at any radius (Geneva tail ~38 mm, stub 24-28
  mm: ~20 points or more each). At K, link 1b is the upper member, so a lobe toward J2 stacks three layers.
* **Folded-side relief by an extra hub.** The prize is 8 of 160 fit poses (<= 5.0 gap points), and 23 of the 84
  frozen fold losses. K2's cheapest metal costs 5.8.
  * K2 engages only bent at psi0 <= 135 deg, where an O20 hub on link 2 is <= 0.12 in band.
  * Where it engages, link 2 lies back over link 1's drive and collides (ROD-hubK2 -5.2 mm).

**New knowledge**

* **The fold window is walled by geometry, not by K's law.** Frozen fold losses stay at 84-86 on every rod-drive
  variant of rounds 6-7, and are 105-106 on drives with less K travel. The binding walls on the stretched side are:
  * the K dyad's straight line, a1max + a2 - 5: 13 fit poses at th 124-157;
  * m3e plus lift-off: 6 poses. How fast K can open is capped by the lift-off gate (K's self-motion slope at fixed
    th), not only by the pressure angle.

  Raising stop B does nothing: taken poses never use K past 44.7 deg. The next levers are the seats (J1 on the back of
  the shoulder, out of the overhead cone), a2, and the knee window.
* **Two metal rules, both missed by claims this round:**
  * K's spring cap is a cylinder (HUB_R, CROWN + capK);
  * a rod over K must clear crown top + 2 mm within HUB_R + 2 of K's axis. The round-6 winner's own rod was 2.6 mm
    into the crown (cost 0.10).

  Swept-plate models also need a plate-height cap (the greedy fit floated a part 90 mm).
* **Near-touch at 1 mm vs 2 mm.** A re-fit that wins at the 1 mm rule can lose at 2 mm. Report both before a polished
  configuration replaces a CAD configuration.
* **Search hygiene.** Penalise every idle slaved spare (split-knuckle's 22.34 sweep minimum is K2-idle). Gate
  convergence per run, never on a concatenated sweep.

## Gen-4b CAD: pick1 built at L1 and in the user's style with the gen-4 build fixes; it fails R17 on K's opening, not on the CAD (2026-10-16, l1_minarc-pick1, user_minarc_pick1)

**Config and shape.** The CAD carries the verified polished config pick1 (envp-F7-g35-6) as the verifier wore it. Its stops are
priced by `tools/env_polish.priced()`:
* J2 stops +0.5 (smhi / smlo 7.377 / 7.3286), read at fold margin 5.5.
* K stop B: a1max 68.0047 -> 66.4696, i.e. dK 56.65, the 5-deg rule cut.
* Params file: `docs/research/minarc_final_polish/picks/pick1_priced.json` (= `verify/v_pick1_fit60_bench_params.json`).

The fit on Bench(60,160) fast at margin 5.5 reproduces the verifier's fit to the digit: plain 11.57, near-touch 15.94.
* Frozen hub levels J1 / K / J2 / J3: 49.11 / 57.90 / 60.71 / 79.97 mm; knee level 87.16 (BDp 49.4 / 56.2 / 62.1 / 81.6, 88.3).
* q2 window -15.85..97.42 deg (113.3 deg of slot); K window 0..56.65 deg.
* Clips: all 8 follow 100 %. K opens on Reach a high shelf (to 15.82 deg) and on Wash opposite shoulder (to 6.19 deg),
  the red team's 15.8 / 6.2. Workspace closes 0.764.

**Built vs model.**
* L1: rigid samples <= 0.0001 mm and straps 0.000 mm outside the lifted hub zones, at 9 poses incl. the overhead peak
  and forced K-open (dK -52.5). Dowels sit in their slots.
* Full CAD: hub / boss / pad features <= 0.144 mm, frames 8.7e-5 mm, dowels in their slots.
* Full-CAD strap samples outside the hub zones:

| link | max | median | BDp CAD max |
|---|---|---|---|
| 1a | 0.19 mm | 0.05 mm | 2.33 mm |
| 1b | 0.94 mm | 0.29 mm | 0.61 mm |
| 2 | 1.16 mm | 0.32 mm | 2.19 mm |

  Link 1a passes the 0.5 mm check everywhere; links 1b and 2 do not.
  * Links 1a / 1b are one side-view profile: their 4 strips do not glue into one valid solid on this shape. That one
    profile sits <= 0.39 mm over the L1 strap.
  * Link 2 is 4 glued strips.

**The gen-4 build findings, applied:**
1. **K stop pair moved off link 1a's root.**
   * Slot placement now counts the full CAD's pad root: the bar's seat along sd_b, 8 mm wide.
   * It maximises the clearance of BOTH opposed slots: homes 66 / 246 deg, 17.2 deg clear of the root.
   * Why gen 4 got this wrong: its L1 saw no strap points in the slot band, so it put the pair at 0 / 180, and the
     second slot ran through the root.
   * The L1 now carries the pair too (two slots, two dowels).
2. **J2 stop strength is stated as a push limit**, because no geometric fix fits:
   * O20 only leaves no larger radius.
   * An opposed pair would need two 136-deg slots at r 7.75. That leaves 44-deg webs, narrower than link 1b's 62-deg root.

   The numbers:
   * Single O3 dowel at r 7.75 mm, MR117 C0 280 N each: the stop is rated **4.34 N.m at s0 1.0**.
   * A 6 N.m shove gives s0 0.73 (brinelling).
   * The O3 dowel itself holds 6 N.m at SF 3.67 in bending.
   * The daily push at the stop is about 0.2 N.m (forced-state cuff force <= 2 N at the 95 mm pad, red team): about 22x
     under the limit.
3. **E strap capped at the boss top (tr + tp) under the knee's reach** in the L1 (the full CAD's member-3 rule).
   * On pick1 no station needed the cap.
   * Knee link vs E strap is 0.50 mm over the knee's whole range in both the L1 and the CAD: that is the washer gap.
   * BDp's L1 had a 0.115 mm static overlap there.
4. **Physical knee stop at 149.5 deg** (knee-window check), built as:
   * a 2.4 x 2 mm tooth behind pin a, hanging 1.5 mm into the E strap's level, outside the O12 boss (r >= 7.9);
   * a knee-level web joining it to the knee link.

   It is built in member 3's frame at the stop and carried to the knee link by the rotation about pin a. That rotation
   is checked against the model's member transforms: 0.0 deg on 28 poses.

   Measured clearance (`pipeline/concept_l1/knee_stop_check.py`; L1 and full CAD identical):

| knee angle | clearance |
|---|---|
| 143.6 deg (the bench's highest taken knee) | 0.68 mm |
| 147 deg | 0.29 mm |
| 149.4 deg | 0.012 mm |
| 149.5 deg (the stop) | 0.000 mm |
| 150 deg | -0.08 mm |
| 153 deg | -0.57 mm |

   The tooth's face lands flat on the strap's side, over a 3.6 mm2 contact.
   * Clips stay <= 131.6 deg.
   * Cost on Bench(110,360): none (taken knee max 143.56, the verifier's knee audit).
   * Cost held out: 4 of the verifier's taken poses lie past 149.5 (to 152.75). Those 4 poses are what the stop costs;
     they were not re-scored here.
   * The fit bench has 2 closing poses past the stop.
   * The L1 clips / workspace apply the stop: ang_min 30.5 on the frozen shape.
5. **Spring, as specified by the red team:**
   * 0.3 x 5 mm 1.4310 +C1900, 0.010 N.m/rad, 0.08 N.m preload.
   * 215.2 mm + 1.7 mm hook: 13 half-turns at 0.42 mm per half-turn, R2.75..R7.79.
   * Outer surface R7.94 in the O16 chamber, 36 % annulus fill.

**Judges.** Same judges as the 16:16 re-judge of BDp. FEA (R9) was skipped for every design, as before. Farm cost
$0.03 build, $0.06 L1 judges, $0.08 CAD judges.

| | l1_minarc-pick1 | user_minarc_pick1 | l1_minarc-bdp | user_minarc_bdp | H1 L1 | user_pinknee_h1b |
|---|---|---|---|---|---|---|
| R1 (2-14) | 80.8 % | 80.5 % | 80.5 % | 80.0 % | 80.1 % | 76.7 % |
| R1-aim (2-10) | 48.7 % | 47.2 % | 52.5 % | 51.0 % | 42.3 % | 35.8 % |
| R4 overhead | 71.8 % | 71.0 % | 72.7 % | 72.0 % | 74.2 % | 71.2 % |
| R16 workspace | 74.0 % | 74.0 % | 72.9 % | 73.5 % | 67.9 % | 61.7 % |
| R3 / R6 / R7 | PASS | PASS | PASS | PASS | PASS | PASS |
| R11 (kPa) | 0.404 | 0.281 | 0.399 | 0.272 | 0.351 | 0.216 |
| R8 (g) | 106 | 240 | 106 | 239 | 77 | 178 |
| R5-aim (3 DOF) | FAIL (4) | FAIL | FAIL | FAIL | PASS | PASS |
| **R17** | **FAIL** | **FAIL** | PASS | PASS | PASS | PASS |
| pass | 6 / 19 | 6 / 19 | 7 | 7 | 8 | 8 |

The CAD keeps its L1's numbers: R1 -0.3, R1-aim -1.5, R4 -0.8. Against BDp:
* R1 and R16 gain a little.
* R1-aim loses 3.8 points (L1 and CAD alike). The red team predicted that loss: held-out in-band 2-10 mm 0.497 vs 0.574.

**R17 fails on K's opening, not on the CAD.** In the nominal case (rolling bearings, mu 0.005), M_GH is 0.142 N.m, cuff
force 0.62 N and cuff twist 4.64 deg; all three pass. The failure is the 4R spare-drift rule:
* On Reach a high shelf, K stays on stop A for 66 % of the clip.
* It lags its planned 15.8-deg opening by up to 9.28 deg, over the 5-deg rule (7 lags, each under the 10-deg stall rule).
* The 0.08 N.m preload holds K closed while the cuff tissue (0.03 N.m/deg) twists instead.
* BDp plans only 0.85 deg of K on that clip, so its drift is 0.03 deg.

A preload sweep (same judge, nominal case, Reach a high shelf + Wash opposite shoulder; `docs/research/gen4b_k_preload_sweep.json`) finds no safe preload:

| preload | K drift | result |
|---|---|---|
| 0.08 N.m | 9.28 deg | FAIL |
| 0.06 N.m | 6.38 deg | FAIL |
| 0.05 N.m | 4.96 deg | PASS (twist 2.6 deg, M_GH 0.08 N.m) |

* At 0.05 N.m, state A needs 0.048 N.m to hold K on stop A (red team), so the return margin is only 1.04x.
* The spring rate changes nothing: 0.010 and 0.015 N.m/rad give the same drift.

This is pick1's config (the red team's "K moves on one more clip"), not a CAD defect. K is sensed, so the lag is
measured by the encoder, not hidden. The lead / the user has three choices:
* accept R17's drift rule failing on one clip;
* run preload 0.05 at a 1.04x return margin (red-team the hold first);
* build BDp, which passes R17 at 7 / 19.

**Open:**
* An independent verifier of these two CADs.
* The knee stop's held-out cost, re-scored (or the stop moved to 153.5 deg, which is free on both benches but
  gives up 4 deg of singularity margin).
* R8's keyword masses (as BDp).

## pick1's K hold: the lag is cosmetic for proximity, and a detent cannot beat a plain spring (2026-10-16, l1_minarc-pick1, user_minarc_pick1; docs/research/pick1_k_hold.md)

- **What the lag costs.** The dynamics judge's simulated K trajectory (0.08 preload, 9.3 deg behind the plan) was posed
  by FK through the judge's hinges, with the cuff's simulated twist applied to the arm parts.
  - On Reach a high shelf it keeps the metal slightly *farther* from the skin: min clearance 1.61 -> 1.78 mm.
  - In-band 2-14 is unchanged (87.9 / 88.0 %); in-band 2-10 drops 66.6 -> 65.2 %. No frame touches (exact winding number).
  - Wash opposite shoulder is unchanged.
  - The R17 failure was a tracking and cuff-twist failure (4.6 deg), not a proximity one.
- **The hold at stop A sets the peak drift; what K does after breakaway does not.** Measured in the judge:
  - A flank detent (0.03 spring + 0.035 detent, gone by 2 deg) drifts 7.15 deg.
  - A two-rate helper leaf (the same torque) drifts 7.08.
  - A plain 0.06 spring drifts 6.38.
  - So drift is about 0.0074 N.m of reflected cuff torque per degree of lag at breakaway. Drift <= 4 deg needs <= 0.042
    N.m at stop A, and no angle-only passive law gives a high hold with a low breakaway.
- **The 0.048 N.m demand is a worst-direction envelope.** With gravity in its real direction (the red team's method,
  unchanged), state A needs 0.023 N.m at 1 g and 0.0355 at 2 g (worst pose: elevation 165). In the judge at 2 g,
  K never leaves stop A on any of the 8 clips at 0.040 N.m.
- **Design change: K preload 0.08 -> 0.04 N.m (same spring, 0.64 preload turns).**
  - R17 PASSES on the L1: drift 3.68 deg, twist 1.98, M_GH 0.061 N.m. The L1 goes 6 -> 7 / 19; R11 0.404 -> 0.344 kPa.
  - The strip stress at stop B halves: about 670 MPa.
  - Measurement change, stated: `judge/dynamics.py` now reads the preload a design declares (build_fixes.spring.preload,
    else 0.08). No earlier number moves.
- **R8 builder fix.** Material now comes from an explicit per-part table in user_style_minarc.py; a part with no row
  stops the build. The CAD's custom mass is 142.1 g, not 178.2: links 1a / 1b / 2 were billed as NdFeB / steel.

## Round 8: a strap-level K drive is verified at 18.91 (score 93.12); the in-band half of 95 is done, the fold did not move (2026-10-16, discovery round 8, closer)

Raw data:
- rows: `docs/concepts/rows/{sidecar-longdyad-knuckle-3r,sidecar-parallelogram-knuckle-3r,sidecar-roller-flank-knuckle-3r,twist-long-a2-knuckle-3r}.json`;
- verifier harnesses and outputs: `docs/concepts/verify/<id>.py`, `docs/concepts/verify/<id>_v_*`;
- the alignment auditor's re-wear: `docs/alignment/remeasure/`, `docs/ALIGNMENT.md`;
- the judge's picks and red team: `docs/concepts/round8_ideation.md`;
- the round table: `docs/concepts/ROUNDS.md` "Round 8 results".

All numbers are frozen exact on Bench(110,360), at the 5-deg margin with O20 hubs only, fitted on Bench(60,160), and
were re-measured by an independent verifier (the sidecars a third time by the alignment auditor; all to the digit).

**What was measured**

* **sidecar-longdyad-knuckle-3r: VERIFIED 18.91 (score 93.12), the round winner and the new verified lead** (previous
  22.82, gain 3.91 frozen, 4.08 held out: 22.67 vs 26.75). 3 active (K slaved by the lobe and a strap-level RSSR
  sidecar: bell crank on link 1b, M2 ball-link rod, horn on link 1a), 0 passive translations, complexity 49. Reach
  0.725, follow 1.0, in-band14 0.897, contact 0.011, overhead 8/28; near-touch 20.00 at 1 mm, **34.03 at 2 mm** (the
  best of any verified row at 2 mm; frontload 44.08, geneva 38.84). Full-grid flood fill drops 0 (knn 21.72). The
  verifier's added checks (world-frame RSSR closure 0.000 mm, ball-link tilt <= 21.8 of 30 deg, real lobe pressure angle
  39.1 of 45) remove no pose.
* **sidecar-parallelogram-knuckle-3r: VERIFIED 19.13 (93.04)**, the same drive on the lead's dyad. Held out it is the
  best of the round (22.03), but at 2 mm it is 50.14 (44 taken poses with metal at 1-2 mm): the alignment audit rates
  its lead gamed on the 1-2 mm shell. In-band14 0.905 sits at the 0.90 edge; a ball centre at 4-4.5 mm keeps the gap but
  drops the rod's in-band to 0.53-0.61.
* **sidecar-roller-flank-knuckle-3r: VERIFIED 20.08 (92.70)**, rodless, complexity 45.25 (the lowest strap-level
  drive). Held out 22.35; the real-envelope correction (the lug strip the model's sampling deleted + the roller pin head)
  gives 19.96.
* **twist-long-a2-knuckle-3r: DEAD, death audited.** Converged over 4869 CMA configs; best frozen 24.46 (C0, the lead's
  axis + a wide dyad), worse than the lead on every margin (min metal 0.03 mm, follow 0.955).

**What it means**

1. **The drive's height was half of the distance to 95, and it is now paid.** The planner's sample arithmetic priced
   the crown-high rod (0 % in band) at 4.54 frozen; the strap-level drive delivered 3.69-3.91 (rod) and 2.74 (roller),
   and the gain holds out (4.1-4.7). Rod 0.89, rod ends 0.96, crank 0.91 in band. The worst parts are now the chain's
   own: hub 3 0.60, L2 0.75.
2. **The whole remaining gap is reach, and nothing in the drive moves it.** 18.91 = in-band 0.34 + reach 17.50 + contact
   1.07. Fold losses 86-88 of 360 on the three drive rows (84-86 in rounds 6-7); overhead 8/28 on every row. Score 95
   needs reach 0.775 at in-band 0.90: 18-19 more workspace poses.
3. **K-dyad length is worth under 1 point and flips sign held out.** The RSSR's transmission falls 36 -> 22 deg as bk2
   goes 37.6 -> 47; phasing the crank to fix it jams the rod on hub 2 past dK ~42 (seen only on the frozen and held-out
   benches). Stop B never binds. The stretched poses past th ~132 sit behind the a2 wall (they need a1e 76-100).
4. **A J3 re-seat has real kinematic headroom but no parking.** Law-only through the model's own IK: reach 0.814-0.825
   and overhead 17-21/28 (lead 0.742 / 10). With metal: hub 2 0.68, L2 0.49-0.62, or contact 0.06-0.07 when J2 stays
   parked; frozen +10 fold poses become +7 contact, +5 knee slide and -0.045 follow. A kinematic kill gate over-predicts
   by the parking term (+0.07 -> +0.005 reach).
5. **Spherical-cam rule for any two-rotor contact about GH:** both pressure angles stay <= 45 iff the speed ratio lies
   in [1/(cos t + sin t), cos t + sin t], t the angle between the contact velocities (widest [0.71, 1.41] at t = 45,
   closing to 1 at t = 0 and 90). Lugs must be shells about GH, never flat plates. The workable roller geometry sits at
   the pitch point and needs a 130-deg arm wrapped around hub K; it carries 52 deg of K (the RSSR 37-43).
6. **The 1 mm near-touch objective moves the metal to 1-2 mm.** Two of the three drive rows are worse than frontload at
   2 mm. Per pose, 169-178 of ~370 taken poses keep some metal under 3 mm. The 2 mm objective (or a plain AND 2 mm
   dominance gate) belongs in the next searches and the winner's polish.
7. **Fast to frozen widened to 8.4-9.0 points** (round 7: 7.25): the fit bench takes overhead 2/12 and reach 0.79-0.80,
   frozen 8/28 and 0.72-0.73. The fit bench under-samples the overhead end that now decides the score.

**What failed and why**

- twist-long-a2 (the window-geometry lens): parking, not kinematics (point 4). The J1 back-of-the-shoulder seat, the
  lens's first lever, was never run for the knuckle - it is the next round's first kill gate.
- The planned bk2 42-48 / a1max 66-75: transmission and hub-2 jam (point 3); the wide 35 / 45 / 75 cell at contact 0.12.
- All-metal GE4E ball links: +6.8 fast (the horn moves to 19.5 mm and drops into the skin). The RC acetal M2 ball link is
  load-bearing and must enter tools/hardware_catalogue.json before CAD.
- Progressive cam laws at the pitch point: cusp (every CMA stream drove the curvature to 0).

**Next:** the winner's final polish (representative envelope bench, 2 mm objective, ball centre 4-4.5 mm, follower and
lobe window as metal, r_h >= 15.5), its verifier, then the generation-winner CAD and stills. Round 9 attacks reach by
making the measured kinematic headroom parkable: the J1 back seat for the knuckle (kill gate with parking), a lower hub 3
/ L2 under the wide window (hub-3 crest seat, b3 0 with the knee window), and the roller-flank drive on a longer dyad.

## sidecar-longdyad-knuckle-3r final polish: no pick replaces the verified config; on this design the env-fitted shape travels worse (2026-10-16, docs/research/sidecar-longdyad-knuckle-3r_final_polish.md)

Raw data: `docs/research/sidecar_env_polish/` (CMA rows, picks, re-scores, claims; job files), tool
`tools/sidecar_env_polish.py`. Self-measured; every claimed number comes from the verifier's own harness
(`docs/concepts/verify/sidecar-longdyad-knuckle-3r.py`, imported unchanged), which reproduces the verified 18.91 / 20.00 /
34.03 / kNN 21.72 to the digit through the wrapper.

**What was measured**

* **The search:** 8 CMA runs from the verified config on the envelope bench `env`, 1216 configurations. The objective
  is the near-touch gap in-sample on env, priced, with continuity, plus the claim-fit guard and a 2-mm shell guard.
  The convergence gate passes on the combined runs: gain 0.07 over the second half, 0.07 over the last third, top 5
  within 0.39. In-sample best 19.64 vs the verified config's 21.64. Wide runs (sigma 0.5-0.6) never beat the verified
  config: the basin is narrow.
* **Selection on noise.** The 40 best rows average 20.53 in-sample but 24.32 on the independent envsel draw, worse than
  the verified config's 23.64. The picks were ranked on envsel with a 2-mm guard. All 3 beat the verified config on
  envsel at 1 mm and at 2 mm.
* **The claim (priced: smlo +0.5, margin 5.5, a1max <= bk1 + bk2 - 5.5).** With the shape fitted on env, the picks
  gain +2.32 / +2.39 / +2.45 held out. With the shape fitted on Bench(60,160), the verified protocol's fit, every pick
  LOSES held out: -0.31 / -0.71 / -0.55. The env fit itself costs the verified config 2.59 points held out (23.29 ->
  25.88), all in-band (0.896 -> 0.871). In the minarc polish the env fit helped (24.18 -> 23.68). Whether a fitted
  shape travels depends on the design.
* **The dominance gate fails on the verified protocol.** pick1 gains +0.76 plain on Bench(110,360) but loses 3.32 at
  1 mm and 4.60 at 2 mm (12 poses under 1 mm, min metal 0.07 mm): the gain is metal moved into the shell. pick2 and
  pick3 lose plain. Robust held-out gain (the best pick, the worse of the two fits): **-0.31**. Below 1, so no
  verifier run is needed.
* **Built-stop pricing of the verified config** (measurement change, no design change): 18.91 -> 19.36 on the bench
  (score 93.12 -> 92.96) and 22.67 -> 23.29 held out.
* **Min th margin over the taken poses**, not on file before: 5.232 deg at the verified reading (0 poses under 5) and
  5.513 priced.
* **Continuity:** the full-grid flood drops 0 poses in every run. kNN on the verified protocol: verified 23.01 priced,
  picks 21.95-24.40.

**Lessons**

* A final-polish objective must fit the shape the CAD builds. Next polish objective: fit the shape on the claim's fit
  bench, wear it FROZEN on env, and select on envsel. That is the claim's own protocol on a representative sample.
* Parameter polish does not move reach on this design. Fold is 266-268 of 952 held-out workspace poses for every
  config. The reach lever is the a2 / J3 re-seat (twist-long-a2), not the polish.
* For the CAD: every pick raised the horn radius r_h (15.2-16.0 vs 14.87), toward the >= 15.5 the red team asked for at
  the socket vs hub K. A single-parameter r_h 15.5 check through this harness should come before the CAD fixes the
  horn.

**Next:** the gen-6 CAD proceeds on the verified config (`best_params`). Cost: about $0.47 on the farm.

## Gen-5 CAD fix: the lobe's skin hit is fixed by a 0.5 mm radial offset; ratio fixes overload the roller and a mirrored follower hits its own crank (2026-10-17, user_geneva_rod -> user_geneva_rod_v2; docs/research/geneva-rod-gen5_fix.md)

**Measured**
* **Real parts move the lobe on their own.** The igus igubal KGLM-03 is 6 mm high, against the 4 mm the CAD modelled.
  Its eyes plus the 3.8 mm horn hub that the M1.6 thread needs raise the rod end 3.6 mm. The re-solved lobe then enters
  the skin by only -0.09 mm (gen-5: -0.26).
* **Stop B is not a lever for the skin.** Ending the law earlier costs nothing on the bench down to dK 50 deg. It costs
  +0.28 gap at 44 and +1.20 at 40, and even dK 35 leaves the ring 0.04 mm short of the 0.3 mm requirement. Bench:
  the verifier's harness, a1max only.
* **A higher drive ratio passes the skin by loading the roller.** A longer crank or a shorter horn shrinks the lobe
  (+0.86 to +1.26 mm). It also raises the MR63ZZ roller load to 85-155 N, against a static rating of about 0.07-0.10 kN.
  The earlier v2 draft (crank 14, horn r 1.8) was one of these.
* **A mirrored follower clears the skin by 2.26 mm and hits its own bell crank.** Its lobe nose sweeps through the
  O10 tube (-1.16 mm) over the J2 window. The skin screen alone passed it. The builder's posed drive check caught it.
* **The fix: the dwell from r 10.1 to 9.6.** The profile comes in 0.5 mm with the same law, forces and parts. The
  ring clears the skin by **+0.41 mm on all 1337 clip frames**, and Raise overhead's min gap goes 0.24 -> 0.72 mm.
  The follower eye shrinks to O4.5 to stay 0.35 mm off the J2 cap.
* **v2 judged (fast, two local queues):** R1 80.30 -> 80.17, R1-aim 49.80 -> 49.77, R4 73.83 -> 74.06, R6 0.0, link 1a
  valid. R16 is unchanged on the same poses (68.33 % both). R17 / R11 were not run: no mujoco in this container.
* **R1 vs the L1:** link 2's group (hubs 2 / 3, the machined bar, the J2 dowel) carries 0.53 of the 0.62 non-drive
  points. Link 1b's group carries -0.04.

**Lessons**
* A lobe fix must be screened by the posed drive check AND the follower / rod load, not by the skin alone. Two of the three
  skin-passing families failed on a part or a catalogue rating.
* Catalogue retaining rings have size-dependent lands: DIN 6799 RS 4 needs n >= 1.2 mm (RS 2.3: 1.0). The project's
  "1.0 mm land" rule holds only up to RS 3.2.
* The full CAD's R1 deficit against its L1 is now located in one group: link 2's hub-zone geometry. It belongs to the
  shared bar builder (user_style_minarc), not to the drive.

**Next:**
- a full judge run of v2, with R17 / R11 on the farm;
- the Comb hair -0.83 attribution (drive parts);
- a bar-only / hubs-only swap of link 2;
- then the re-shoot, if the user says yes.

## roller-longdyad-knuckle-3r final polish: the farm search did not run; the audit's four watches measured on the verified config (2026-10-17, docs/research/roller-longdyad-knuckle-3r_final_polish.md)

**Not run.** The envelope polish of the generation-6 winner was blocked:
* the farm batch (8 CMA runs + 2 env re-scores, est. $0.4) was refused at launch by the session's permission policy;
* the env fast caches live only on the farm volume, and rebuilding them here would take about 2 h at load 11-21.

**No polished config and no held-out gain is claimed. The verified config stays the CAD config.** The tool
(`tools/roller_env_polish.py`) and the farm batch are ready.

**The objective applies the sidecar polish's lesson.** It scores BOTH shapes: the env-fitted shape in-sample and the
Bench(60,160)-fitted shape (the CAD's) worn frozen on env. It also prices each of the alignment audit's watches:
* knee window ang_min >= 26.88;
* drive read at PA_MAX 42;
* a contact-depth guard;
* workspace in-band at elevation 90-140 logged.

**Measured** (claim harness, local, exact; the wrapper reproduces the verified 18.67 / 20.30 / 33.10 and the auditor's
per-pose dump on 470 / 470 poses):
* **Knee window.** Closing it to 26.88 costs nothing (auditor: 18.67 / 23.72).
* **Audit-compliant reading** (built stops +0.5, margin 5.5, PA 42, knee 26.88): **19.25** on the verified protocol
  (score 93.00) and **24.91** held out (+0.58 / +1.18, measurement changes). Held reach falls 0.6817 -> 0.6691 (fold
  261 -> 272). The taken K opening falls to 43.7-43.9 deg. The fold rule binds before the drive.
* **Transmission.** One flank change, beta -173.46 -> -178.0, moves the drive end 44 -> 48 deg and the taken horn
  pressure angle to 39.9-40.2 deg (5 under the 45 gate), at 19.32 / 24.86: within noise of 19.25 / 24.91. The PA watch
  is free to fix. The flank is a knife edge: 22 of 27 nearby cuts fail the cam synthesis at rest.
* **Contact depth** held out: 49.88 mm verified -> 39.0 mm priced, deepest 8.45. Still deeper than the lead's 35.66.
  3 of the 9 presses are a below-shoulder cluster behind the body (elevation 60, plane -75 / -90, axial 105-120: 5.5,
  3.5, 1.6 mm), separate from the overhead presses at 150-165.
* **Raised-arm workspace in-band** (elevation 90-140): 0.798 -> 0.802 bench (lead 0.841).
* **GH-offset within-liner share**, 3 mm misfit, knee-equivalent: 0.666 bench / 0.614 held (5 mm: 0.360 / 0.337),
  the same as the twin.

**Hard goal** (held out <= 20 at depth <= 35.66): 4.9 points and 3.4 mm short at the audit-compliant reading. The two
env polishes so far moved held out by +1.49 and -0.31 on the CAD's fit, so a polish alone will not close it. The fold
(272 of 952) is the limiter.

**Next:**
1. Run `docs/research/roller_env_polish/farm/jobs_cma.json` when the farm is permitted (about $0.5 with the claim
   batch).
2. Carry beta -178 (the PA fix) into the CAD's flank.
3. Attribute the below-shoulder press cluster to a part.

## The fold is two walls: the stretched one is the K drive's stroke, not hub 2; the family's ceiling is not kinematic (2026-10-17, docs/research/fold_ceiling.md)

Raw per-pose data for the verified roller-longdyad-knuckle-3r config: frozen Bench(110,360) exact, and the 952
held-out workspace poses. The model's own IK was re-run per pose, and an exact-skin K3 march was run per rigid part.
Scripts are in `docs/research/fold_ceiling/`. No rule, bench or verified row was changed.

**Where the 88 bench fold losses are**

* **73 stretched-side poses** (th 107-176):
  * 64 are internal rotation >= 90 deg across the body (axial <= -90, plane >= 60);
  * internal rotation swings the humerus-fixed J3 away from J1;
  * held out: 211 of 261.
* **15 folded-side poses** (th 7.7-22): scapular-plane abduction overhead (plane -20..45, elevation 90-165,
  axial -60..0); held out 50.
* Of the roller's 88, sidecar-longdyad loses 80, kneeless-roller 86 and the old pin knee 86.
* **The clip frames never leave th 41-96.** In-band never sees either side. A wider window costs in-band only
  through the part levels that the new workspace poses force.

**The stretched wall is the K drive**

* It is not stop B and not the dyad.
* The taken poses end at th 106.3: a1e 54.3 at dK 45.6 of the drive's 46.25.
* Stop B (a1max 58.8, th 111) is never reached.
* Closed form, with a one-sided K and a1 <= a2:
  * window = [a2 - a1 + 5, a1e(dK_max) + a2 - 5];
  * cos a1e = cos bk1 cos bk2 + sin bk1 sin bk2 cos(psiA + dK);
  * the width is a1 + a1e_max - 10, and a2 only slides the window.

**Hub 2 does not cap the stretched side at these seats**

* Exact skin, best J2 ray: 47 of the 73 stretched-lost poses put hub 2 within its fitted 62.0 mm level (clip band
  52-62). Held out: 142 of 211.
* **The folded side IS a hub-2 clearance trade:** 4 of 15 clear (held out 21 of 46); the median need is 71 mm.
* The margin accounts for 22 of the 88: they would close at margin 0, which the user's rule forbids.

**Kinematics is not the family's ceiling**

* Over all 247,860 seat pairs the user's ruling allows, a window >= 80 deg wide holds 0.99 of the 360 poses (held
  out 0.97-0.99 on the same seats).
* At the leader's seats, the best placement holds 0.797 at its width and 0.872 at 105.
* The 360-pose optimum puts a2 at ~62, not 57.2 (+10 poses kinematically).

**Realisability, exact (`parking_k.py`; every hub and link sample at ONE level, clearing every closed pose)**

* A K dyad of 28 / 50 (a1max 73) at the leader's seats admits **+14 poses**, R_est 0.739 -> 0.778. The parts' clip
  in-band stays at 0.768 -> 0.760.
* Link 1b (K -> J2) is the binding part.
* **But K must turn 78-89 deg.** The leader's drive turns 46; the round-9 flank caps at 55-57.5 at pressure angle
  <= 43.
* With 57.5 deg: th_hi ~115, reach ~0.76-0.77, score ~94.5-95 at best, before the drive's own metal.
* **Score 95 in the family is therefore not provably impossible, and it is not reached.** The gate is a 60-90 deg K
  drive whose metal parks. Above ~0.80 reach the folded wall (hub 2) must move too.

**An instrument that failed**

* A per-part parking relaxation over the whole family looked like a family bound. It was calibrated exactly on the
  leader (fast 0.775). It drops the workspace poses that do not clear.
* Its optima (0.84-0.89 fast) were refuted by a paired kit model: worse than the control under every fitting policy,
  with hub 2 and link 2 floating.
* Dropping uncleared poses is not available to a rigid chain: they are contact.
* Use the clear-every-closed-pose test (`parking_k.py`) as the gate.

__SHIFT_F__

# Verification: l1_offset-skin-normal-3r (L1 keep-out CAD of offset-skin-normal-3r k4216)

The skeptic re-measured the L1 CAD + judge claim (commit 4ae5925) on 2026-10-16. It used its own scripts,
single-threaded on the local box, on the committed exo.glb / clips.json (scratch copies where a judge writes files).
Scripts: `v_kin.py`, `v_size.py`, `v_contact.py` in the verifier scratchpad (not committed; their method is below).

**Verdict: not refuted.** Every scorecard number I re-measured reproduces to the digit, every PASS is a real PASS, and
the frames reproduce the bench model to 1e-4 mm. Two bookkeeping faults (below) do not change any value or status.

## 1. Member frames vs the bench model

I refitted k4216 on Bench(60,160) fast: gap 32.61, reach 0.7063, follow 0.9667, ib14 0.7792, ib10 0.3892, contact
0.0116, S 6.3 / 7.5 / 0.5, mid m (-5.642, 1.575, 0). That is the claim to the digit. The builder's `chain()` gives
the model's own bench kinematics within 1e-7 (Q, RS) and 8e-7 mm (slides).

At 7 clip frames, I posed the model and the exo.glb. The glb was posed through `scene_export.posed_scene` on the
COMMITTED clips.json, which is the judges' path. The arm-fixed parts were posed by the body rig, not by the model.

| clip, frame | why | plane / elev / axial | G / T dev | hubs 1-3, neck: model -> glb | straps | every built part's vertices | closure |
|---|---|---|---|---|---|---|---|
| Raise overhead 36 | highest followed | 30 / 65.9 / -42.9 | 5e-7 / 4e-5 mm | 0.0000 mm | L1 1.99, L2 1.07 | <= 7e-5 mm | 0.0001 deg |
| Reach back pocket 72 | behind the back | -80 / 39.0 / 101.1 | 5e-7 / 5e-5 | 0.0000 | same | <= 8e-5 | 0.0001 |
| Wave 63 | held out, highest followed | 15 / 95.0 / -80 | 5e-7 / 5e-5 | 0.0000 | same | <= 9e-5 | 0.0001 |
| Walking arm swing 54 | held out | 90 / 24.0 / -90 | 5e-7 / 4e-5 | 0.0000 | same | <= 7e-5 | 0.0001 |
| Comb hair 105 | high elevation | 78 / 143.1 / -67 | 5e-7 / 5e-5 | 0.0001 | same | <= 9e-5 | 0.0002 |
| Wash opposite shoulder 81 | across the body | 145 / 46.1 / -69 | 5e-7 / 4e-5 | 0.0000 | same | <= 6e-5 | 0.0002 |
| Raise overhead 120 | a held frame | shows frame 36's pose | same | 0.0000 | same | <= 7e-5 | 0.0001 |

**Confirmed.** No part is parked: all 17 parts sit in their kinematic group. The arm-fixed parts are posed by the
body rig (H group) and land on the model's RS Q (x + m) within 1e-4 mm. The strap offsets (<= 1.99 / 1.07 mm, the
same at every pose) are the stated hub-zone lift, not a frame error.

**The radial closure is exact, not a tolerance.** Over all 1216 followed frames the radial slide reads
|s_n - m_n| <= 7e-8 mm (J1 and J2 on GH rays: a J3 rotation about the 7 mm offset line is a GH rotation plus a
translation in hub 3's plane). Nothing hides inside the RSR3M stack, where a ball guide could not take radial play.

The along slide runs -3.98..+5.82 mm about mid (stroke +-6.3). The across slide runs -7.01..+4.59 (stroke +-7.5).

## 2. Parts at their real size

Each part was measured from the exo.glb in its own frame: the hub axis for the hubs, the stage frame (along, across,
normal from the fitted cuff level t_r = 77.84) for the rest.

| part | measured | real component | status |
|---|---|---|---|
| J1-J3 hubs | r 10.00. Lower plate F..F+3, boss + cap F+3.15..F+12.25 | O20 x 12.25 v5 hub, MR117 pairs (docs/HARDWARE.md) | real |
| along block (H, inverted) | 12 x 8, t_r+1.5..4.5 (body 3, the 1 mm H1 under it) | RSR3M / MGN03C: L 12, W 8, H 4 | real |
| along rail (l4) | 26.6 x 3, t_r+2.9..5.5 | rail 3 x 2.6, 12 + 2 x 6.3 + 2 | real |
| adapter (carriage A, l4) | plus 26.6 x 29, 5 wide, t_r+5.5..6.5 | 1 mm plate | as claimed |
| across rail (l4) | 3 x 29, t_r+6.5..9.1 | rail 3 x 2.6, 12 + 2 x 7.5 + 2 | real |
| carriage B (l3) | 8 x 12, t_r+7.5..10.5 | the second RSR3M block | real |
| base plate (H) | 14 x 10 x 1.5 | cuff base | as claimed |
| cuff mount slab (H) | along 6..37, across -5..19.6, 1.5 thick | 1.5 mm Ti slab to the BOTTOM bar | as claimed |
| bridge (l3) | along -17.3..4, 8 wide, t_r+10.5..16.5 | stepped filler | as claimed |
| neck (l3) | 8 wide x 3, along -35.1..-16.3 | the model's ramp | as claimed |

The stack built is 1.5 + 4 + 1 + 4 = 10.5 mm, as stated. The block is a full 12 mm long on the rail at both stroke
ends (along: 1 mm of rail to spare; across: 1 mm). Nothing is missing from the joint list: 3 hubs, 2 guides (2
blocks, 2 rails), the adapter, the base, and the mount.

**Caveat (stated in the claim):** the outer surface of the stage stays at t_r + 16.5, because the bridge fills the
3 mm the real stack saves. So the 10.5 mm stack buys no R1 yet.

R8: 17 parts, 79.42 g. **Confirmed.**

## 3. Held-out clips

- Bench(60,160) uses the fit clips only (`tools/concept_bench.py`; `data/raw/split.json` fit = the six clips). The
  CMA (sweep log k 4216, stage cma2-F) and the refit both use Bench(60,160).
- The slide strokes come from fit-clip and bench frames only (`Model.__init__`, CB.FIT).
- Wave (172 frames) and Walking arm swing (109) are in clips.json and in both score files: judged, never fitted.
  **Confirmed.**

## 4. Judges re-run

| row | claimed | re-measured | how | status |
|---|---|---|---|---|
| R1 (2-14) | 78.7 % | **78.7 %** in band while following, overall 71.5 %, follow 90.9 %. Every clip matches score_14mm.json to 0.1 pt, held-out Wave included (65.4 %) | full-exo/score_design.py, BAND_HI=14, step 3, scratch copy | confirmed |
| R1-aim (2-10) | 42.0 % | partial rerun (BAND_HI=10, step 3): Raise overhead 17.8 %, Drink 29.4 %, both = score.json to 0.1 pt; stopped at the time box | score_design.py | consistent |
| R3 | 90.9 % | **90.91 %** at step 3 (the judge's rate), 90.95 % at 30 fps (1216 of 1337 frames) | clips.json held flags | confirmed |
| R4 | 36.0 % | **36.0 %** = 42.6 % follow x 84.6 % in band (Raise overhead) | score_design.py rerun | confirmed |
| R2 (ours) | 0.0 mm | **0.0 mm**: none of our parts enters the skin in any of 228 frames (step 6, the judge's rate). Closest: hub 2 plate 1.49 mm clear (Wave 114), mount slab 1.73 (Reach back pocket 96), link 2 2.27, base plate 2.81 - the red team's numbers | own check: our 17 parts as dense SURFACE samples (~0.7 mm spacing + vertices), winding-number signed distance to the posed rig skin | ours 0.0 confirmed |
| R2 overall | 24.87 mm FAIL | not re-run. It is the user's FOREARM CUFF / upper cuff (judge's body_contact.json, owner "user") | | FAIL stands |
| R6 | 0.0 mm PASS | **0.00 mm at EVERY frame (1337, step 1)**. Covers all 1099 ordered pairs of parts in different motion groups (ours vs ours and ours vs the user's parts), with dense surface samples both ways. No pair is inside another by more than 0.01 mm | own check, igl winding-number signed distance to the closed B mesh | **PASS confirmed** |
| R6 sensitivity | | the same check on the FIRST build (git 06b5a59), step 12: link 2 strap 1.12 mm into the J3 plate (Raise overhead 24), link 1 / link 2 0.67 mm (Wave 72). The R6 judge reported 0.0 for that build | own check | the check sees what the judge missed |
| R7 | PASS | `judge/part_validity.py` rerun on the final glb: 14 of 14 valid, 1 solid each. The 3 H proxies are watertight, 1 piece (parts_full.json) | judge | PASS confirmed |
| R5 / R5-aim | 3 / 3 | 3 revolute joints set the orientation. The 2 slides are fixed by closure, with radial 7e-8 mm. The 2 passive translations are outside the count, and 2 is the stated hard maximum | design.json + section 1 | confirmed |
| R8 | 79.4 g | 79.42 g | parts_full.json | confirmed |
| R16 | 57.5 % | not re-run. The workspace closes 63.8 % (build.json), consistent | | consistent |

The comparison rows were checked against the champion's and l1_3r-k2221's own scorecard.json, and match exactly.
Champion: R1 32.87, R1-aim 17.31, R3 98.23, R4 30.51, R6 4.38, R16 80.17, 6 passes. l1_3r-k2221: R1 56.12, R1-aim
27.63, R3 97.34, R4 48.24, R6 2.85, R16 39.17, 5 passes.

## Findings that do not change the scorecard

1. **Stale judge file.** `judge/part_validity.json` is from the first build (commit 06b5a59). Its link strap
   volumes and boxes (1.759 / 0.499 cm3) are not the final build's (1.770 / 0.504). The rerun on the final glb
   passes, so R7 stands. The file should be regenerated with the build.
2. **The R6 judge is blind to edge crossings**, as the red team said. Its vertex-only test, every other vertex at
   step 12, scored 0.0 on a build that interpenetrated by up to 1.12 mm, more than the 0.59 mm the red team reported.
   On this build the 0.0 is true, by an independent dense check at step 1. The judge itself still needs surface
   samples.
3. **R17 / R11 are judged on the orientation-equivalent spherical chain.** design.json says so. The MuJoCo model
   omits the 7 mm J3 line offset and the 2 slides (RSR3M ball guides, closure-driven, with no free DOF, as section 1
   shows). The PASS is plausible but approximate.
4. The R1-aim gap is structural. Hub 2's plate comes to 1.49 mm (Wave). The bridge top sits at t_r + 16.5. Next
   step 1 of the claim (lower member 3 by 3 mm) is the right lever.

## What this means for the loop

The build is honest: it is the new leader among built designs on R1 / R1-aim and on the pass count (7 of 19). It
loses R3 / R4 to the J2 fold, as stated. The claim's next steps stand, with one addition:

- Regenerate `judge/part_validity.json` in `tools/judge_all.sh` / the farm judge whenever exo.glb changes.

Merge this verifier's dense R6 (surface samples, step 1) into `judge/part_contact.py`.

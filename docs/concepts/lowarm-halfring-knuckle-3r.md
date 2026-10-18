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

## Results (2026-10-18, local, niced; frozen protocol = fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360) exact)

| cell | frozen exact Bench(110,360) | reach (takes) | ib14 | ib10 | contact (poses) | held out | note |
|---|---|---|---|---|---|---|---|
| lead conecut-knee-knuckle-3r | 18.28 (93.35) | 0.7278 (262) | 0.9012 | - | 0.0106 (4) | 22.38 | cx 18.5 |
| A0 half ring (zr 4.03) | 18.37 (proposer, not re-run) | 0.7278 | 0.8991 | 0.5696 | 0.0106 (4) | - | |
| **A** half ring + low arm (zr 2.0) | **18.28 (93.35)**, reproduced 3x | 0.7278 (262) | 0.9006 | 0.5715 | 0.0106 (4) | 22.64 (proposer, same code path) | cx 16.5, ties the lead |
| B root lift h 1.5, r_full 14, L 9.84 (r_end 23.8) | 17.96 (93.47), full model | 0.7306 (263) | 0.8978 | 0.5682 | 0.0080 (3) | **22.70** (reach 0.6912, ib14 0.8967, 13 contacts) | 316 clears by **0.048 mm** |
| B robust (316 >= 0.2 mm) | best 18.41 (h 1.75, r_full 24, L 12.6, r_end 36.6) | 0.7306 | 0.8933 | - | 0.0080 | - | worse than A |

Cell B in the full model (link-2 samples, contact top copy, strap and the per-pose l2_check all lifted; l2 clear min 12.32 mm,
no parts losses): overhead (elev >= 140) 9/28 taken (A 8/28; 316 is plane 60 / elev 150 / axial -105), min metal 0.048 mm,
near-touch gap (1 mm) 20.14, (2 mm) 34.84, workspace in-band elev 90-140 0.828 (the lead's NEW-ws-inband watch 0.8315),
dK taken max 45.62 < kslot 46.0. Held out: the lift clears one held contact (14 -> 13) and costs 0.0028 of in-band: 22.70 vs
cell A's 22.64 - **the bench gain does not transfer**.

### Cell B is a graze, not a clear (the pre-registered rule stops the claim at A)

At pose 316 after the root lift, link 2's bar sits 0.05-0.37 mm over the skin along ~18 mm of its length (r_u2 15.5-33.3 mm
from J2's axis; samples j96-j105, skin normal 0.81-0.93 radial from GH, i.e. the skin runs parallel just under the bar):

| sample | r_u2 (mm) | lift (mm) | skin distance (mm) |
|---|---|---|---|
| j99 | 21.39 | 0.18 | 0.048 |
| j105 | 33.27 | 0.00 | 0.071 |
| j104 | 31.35 | 0.00 | 0.112 |
| j96 | 15.51 | 1.43 | 0.130 |
| j100 | 23.39 | 0.01 | 0.147 |

So no ROOT lift can give 316 the pre-registered 0.2 mm (727 configs, h 0.5-3.0, r_full 12-24, L = R15 minimum + 0-8 mm: the
best clearance is +0.07 mm, capped by j104/j105 outside any root S-bend). Lifting the bar out to r_end ~36.6 mm reaches
+0.30 mm at an in-band cost of 0.0073 -> 18.41 (67 configs, r_full up to 36, r_end <= 46). A second local lift around the
binder (h 0.3 / 0.6 over r 17-25) leaves 316 at +0.071 (18.00 / 18.06). The judge's "B ~35 % chance" resolves to no.

### The dwell hold over the two-body stack fails the 0.25-deg gate (the spec's numbers were optimistic 2x)

Read from the model's own stage-1 / stage-2 kinematics (r['cam']['desmo']['lowarm']): the pin moves 7.80 mm per rad of crank
normal to the inner wall, and K = phi / 0.418 in the dwell (stage 2 holds K at 2.39 x the crank angle), so **17.6 deg of K
per mm at the pin** (the proposer used 8.35). The crank arm passes over link 1b's own metal only within **12.3 mm** of the
crank axis (link 1b's strap spans lever 1.0-13.1 mm; beyond, the arm arcs around hub K at 16.6 mm from uK, outside hub K's
O20 and over no link-1b metal), so the pad lever is <= 12.3 mm, not the assumed 25-38 mm.

| tolerance set | J2 runout | ring concentricity | pad lap | slot | **K play** | gate 0.25 |
|---|---|---|---|---|---|---|
| nominal (0.010 / 0.005 / +-0.03 mm) | 0.176 | 0.088 | 0.335 | 0.040 | **0.638 deg** | fail |
| tight (0.005 / 0.003 / +-0.01 mm) | 0.088 | 0.053 | 0.112 | 0.040 | **0.292 deg** | fail |
| zero | 0 | 0 | 0 | 0.040 | 0.040 | pass |

A hard pad therefore leaves K free by 0.3-0.6 deg at every dwell pose (overhead included) - an unsensed passive coordinate
that rattles, against the R17 rule. The only passing build is a PRELOADED pad (the crank arm sprung against the pad so the
pin always bears on the inner wall): interference >= runout + concentricity at the pin (~0.015-0.03 mm, x 12.3 / 7.8 at
the pad) plus the lap; at the judge's ~340 N/mm arm stiffness that is ~5-36 N at the pad, ~7-50 N at the pin, a J2 drag in
the dwell of roughly mu 0.15 x 50 N x 9.6 mm ~ 0.07 N m (estimate, not measured), and a Hertz stress on the 1.5 mm crowned
pin of ~1.5 x (50/25)^(1/3) ~ 1.9 GPa (scaled from the spec's 1.3-1.5 GPa at 25 N) - at 440C's limit. With the preload
the half ring is a different mechanism claim (a drag reading the verifier must make), not a free 0.67.

The one-part groove of desmo-conecut-knuckle-3r holds the dwell at 0.01 mm clearance (0.18 deg at this sensitivity, 0.04
slot) - the outer wall the half ring deletes was doing real work.

### Gates that pass

- Stage-1 built-groove pressure angles at mu 0.17 over the 9 corners (a_s 9.1-9.3, psi 149-150): pin side first fails at
  K >= 52.89 (worst a_s 9.3 / psi 150), cap side >= 59.99, gate 47.27 (the proposer's 52.89 reproduced).
- Slot slop 0.04 deg, pocket PA 25.2 / 32.0 vs 34.47; dK_lim 46.0 at the slot end; l2_check clear 12.3 mm; no parts losses.
- Watch items carried unchanged from desmo-conecut: rc_min 1.0 (RC_MIN 1.5 never cut), ridge 0.243 mm.

### Sweeps and the convergence gate

- Bench(60,160) fast, Latin hypercube over the whole box (owd_margin 0-4, a_s 9.1-9.4, psi 149-150.5, glev -1..-0.5, blend
  10-20, zr 1.5-4, l2_lift 0-2, r_full 14-18, L ext 0-6), 114 configs: **flat** - reach 0.7688, contact 0 and the near-touch
  objective 19.45 for every config (the fast bench has none of the four contact poses), plain 13.12-13.59 moved only by
  in-band; best = cell A's pre-registered point (13.12); dwell K play 0.629-0.644 over the box (a_s / psi do not fix it).
- Frozen exact surrogate (link 2's segment of every scored pose's distance array replaced, Bench.report re-run; reproduces
  the full model to 0.00 at k0 and at the cell-B pick): 727 configs (moving set r < 31) + 67 (r < 48).
- Gate (score points): fast - gain over the 2nd half 0.000, over the last third 0.000, top-5 spread 0.007; frozen scan -
  0.000 / 0.000 / 0.007; extended scan 0.000 / 0.000 / 0.022. Converged.

### Red team

- **The pose that jams**: every dwell pose (K = 0, the folded side) - with a hard pad K is free by 0.3-0.6 deg; with a
  preloaded pad the drag rides the whole dwell. Not on the bench (the bench reads K as determined).
- **Named poses (cell B, frozen exact Bench(110,360), redteam mode)**: rest (plane 0, elev 15) taken, dK 4.6, lowest E strap
  3.85 mm; overhead axial -135 taken, dK 5.8, lowest hub K 2.94 mm; overhead axial 0 lost to the J3 stop; overhead plane 90,
  across the body with extreme internal rotation, behind the back (plane -60, elev 45, axial -120), abduction 90 over the
  deltoid crest and extreme external rotation all lost to the fold (unchanged from the lead); across the body (plane 120,
  elev 90) taken, lowest hub 1 4.36 mm. Lowest taken poses: 316 at 0.05 mm (link 2), 139 at 0.07 mm (as in cell A), 203 at
  0.72, 379 at 0.75.
- **The point that pinches**: pose 316 (plane 60, elev 150, axial -105, dK 43.9): link 2's bar over ~18 mm at 0.05-0.37 mm;
  the cell-B take rests on 0.048 mm. Remaining contacts (T5 depth, bench): 205 hub 2 -4.28, 237 crank -9.47, 264 hub K -1.17
  = 14.92 mm over 3 poses (cell A 16.15 over 4).
- **The optimistic number**: cell B's 17.96 (score 93.47) - one pose at 0.048 mm, held out 22.70 vs A's 22.64 (no
  transfer), and it stands only if the dwell hold is solved.

### New knowledge

1. The link-2 root lift is independent of the half ring and the lead's chain shares pose 316: the same lift on the lead's own chain
   should read the same ~-0.3 graze (predicted, not measured here); at 316 the skin lies parallel under ~18 mm of link 2, so a robust
   clear is a whole-bar radial lift (in-band 1:1; "radial lifts are dead" holds for link 2 as well).
2. Stops that replace a one-part groove wall must be read as a tolerance chain through the drive ratio: here 17.6 deg of K
   per mm at the pin (2.39 x the crank angle), and the only link-1b metal under the crank arm is within 12.3 mm of its
   axis. Any future own-angle crank stop on this drive has the same <= 12.3 mm lever.
3. The fast Bench(60,160) cannot see any of this cell's levers (no contact poses): screen contact levers on the frozen
   exact wear with a per-sample surrogate (2 min precompute, ~0.1 s per config) instead.

### Verdict

No new lead. Cell A ties the lead (18.28, same 262 takes and 4 contacts) at complexity 16.5 but its dwell hold fails the
0.25-deg gate as a hard pad (0.638 deg nominal, 0.292 tight); it stands only with a preloaded pad whose drag is unmeasured.
Cell B's 17.96 is a 0.048-mm graze that the pre-registered 0.2-mm rule rejects (robust: 18.41) and that does not transfer
held out (22.70 vs 22.64). Files: docs/concepts/models/lowarm-halfring-knuckle-3r.py (cells CELL_A0 / CELL_A / CELL_B),
docs/concepts/sweeps/lowarm-halfring-knuckle-3r.json (908 entries in order; 'stage' and 'bench' name the bench of each),
docs/concepts/viz/concepts/lowarm-halfring-knuckle-3r.js (cell B at its measured config, the model's own export).

## Verification (independent skeptic, 2026-10-18 ~02:35 UTC)

Harness: docs/concepts/verify/lowarm-halfring-knuckle-3r.py (the claim's model loaded UNCHANGED and worn through its own
frozen protocol; checks copied from the desmo-conecut-knuckle-3r verifier - V1 fit gates, V2 plate-vs-horn solids, V3
own-state th margin with dth/dK, continuity flood, per-pose dump - plus V4: th margin with the claim's OWN dwell K play,
poses below 5 deg removed and Bench.report re-run). Config = the row's best_params (cell B: l2_lift 1.5, r_full 14,
L 9.836) on the model's cell-B dict. CB_EXACT=1, local, niced (load 12 on 4 cores; the farm is closed).

| check | result |
|---|---|
| frozen exact Bench(110,360) | **17.96** (score 93.47) reproduced: reach 0.7306 (263/360), follow 1.0, ib14 0.8978, ib10 0.5682, contact 0.0080 (3: 205 hub 2 -4.28, 237 crank -9.47, 264 hub K -1.17); why: fold 88, contact 3, parts 0, closure 0, flip 0 |
| overhead (elev >= 140) | 9/28 taken |
| near-touch (reported only) | min metal 0.048 mm (pose 316, link 2); gap at 1 mm 20.14, at 2 mm 34.84 |
| per-pose dump | docs/alignment/remeasure/lowarm-halfring-knuckle-3r_bench_perpose.json, recomputes 17.97 (+0.01, rounding) |
| V1 own gates (fit model) | desmo_fail empty; dK_lim 46.0 (slot end), dK taken max 45.62; stage-1 built pin max moving 48.89, first fail K 58.0 / cap 62.8; slot slop 0.04; crank free 0.18 deg (worst-tol 0.27, the parent's watch); rc_min 1.0 / ridge 0.243 (carried watch) |
| claim's own dwell-hold gate | **FAILS: 0.638 deg vs 0.25** (runout 0.176, conc 0.088, pad lap 0.335 at lever 12.29 mm, slot 0.04) - re-read in the worn fit model, as the claim reports |
| V2 plate vs horn solids | 373/373 overlapping poses at >= 0.15 mm (min 0.150, pose 204): pass |
| V3 th margin (own state) | min 5.181 (pose 313, forced, dK 45.62); dwell min 5.389 (pose 229); 0 poses < 5 |
| V4 th margin with K play | dwell |dth/dK| <= 0.36, forced <= 0.438. Nominal pad play 0.638 (dwell) + 0.23 (forced): min 5.088, **0 poses dropped, gap unchanged 17.96**; tight 0.292 and parent-groove 0.22: same |
| continuity flood | connected_full 17.96 (0 dropped; envelope 1065 / forced 526 all connected); kNN 19.64 (6 forced dropped; desmo-conecut's verified wear reads 20.73 vs 19.04 the same way); bench-only 49.98 (the known sparse-bench artefact) |
| paired vs the lead (alignment_paired compare, bench) | -0.32 (A 17.97 vs conecut 18.29): ONE discordant pose (316: contact on the lead, taken here at 0.048 mm); split reach -0.28, contact -0.27, in-band +0.22; bootstrap CI90 [-1.55, +0.42], P(better) 0.64 |

Findings:

1. **The number reproduces and survives the added checks**: 17.96 frozen exact, no part, closure, flip or th-margin
   loss, and the dwell pad's 0.638-deg K play costs no pose through the fold margin (V4: dth/dK is 0.2-0.44 deg/deg, the
   lowest dwell margin is 5.39).
2. **But the 0.32 over cell A / the lead is one pose selected on the claim bench**: the lift (h, r_full, L) was chosen by
   a 727-config scan of the frozen-exact Bench(110,360) surrogate - the bench the claim is measured on - and the gain is
   pose 316 grazing at 0.048 mm (paired CI90 [-1.55, +0.42]). The rule is "claim on held out": held out reads 22.70
   (claim; see held row below) vs cell A 22.64 and the lead's 22.38 - no transfer.
3. **The design as claimed fails its own dwell-hold gate** (0.638 deg with the hard pad, 0.292 at 5-10 micron
   tolerances, gate 0.25): unmeasured here is what the extra dwell play does to near-touch poses through the chain's
   self-motion - pose 139 (plane -60 / elev 60 / axial 105) is taken at 0.072 mm and 203 / 379 at 0.72-0.75 mm; with
   K free by 0.64 deg the intermediate bodies move up to ~0.7 mm tangentially at r ~65 mm (not modelled; a red-team item).
   The preloaded-pad build that would pass the gate adds a preload element and a J2 drag the model does not read.
4. **Unmodelled metal**: the stop pad itself (a lateral block on link 1b's top face standing into the arm's layer) is not
   sampled for part-part clearance (small: it lies inside the arm's own swept band beside link 1b).

Champion on the same bench and checks: 75.94 (risley-turret verifier checks; 66.97 via the offset-skin-normal verifier).
Verdict: **VERIFIED at v_gap 17.96** (score 93.47) as a bench number - not refuted (better than the champion, no hard
rule broken: 3 active DOF, K slaved and never undetermined beyond its play, 0 passive translations, no gears / pulleys /
cables). It is NOT a lead change: the gain over the lead is a single 0.048-mm graze selected on the claim bench, held out
does not transfer, and the hard-pad build fails the claim's own 0.25-deg dwell gate.

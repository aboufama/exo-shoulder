# Take-bound table: can 3 joints reach 95 at the legal J1 seats? (round 15 lens A)

Status: sections 1-4 filled; 5-7 PENDING (filled section by section, each section committed). Started 2026-10-18 ~12:20
UTC on branch claude/exciting-albattani-94w8cp. Plan: docs/concepts/ROUNDS.md "Round 15 plan, re-dispatch
(2026-10-18 ~09:25 UTC)", lens A "take-bound-3dof".

The decision this table feeds (the user's): accept a 4th joint, or accept a verified score below 95 with 3 joints.

Machine-readable: `docs/research/take_bound_3dof.json`, built by `docs/research/take_bound_3dof.py` from the cited files
(the script re-reads every cited JSON value and checks it to +-0.005; markdown-line citations are quoted, not machine
checked). No bench, judge or kit file changed; nothing here was searched, selected or tuned on held-out poses. All gaps
are frozen exact Bench(110,360) unless marked FAST (Bench(60,160)).

## 1. Arithmetic (how takes turn into the gap)

gap = 100 [(0.90 - ib14)+ + (0.95 - follow)+ + (0.90 - reach)+ + contact] (tools/concept_bench.py gap_of); reach =
takes / 360; score 95 = gap 13.75.

- One take is worth 0.278 gap points; a contact pose turned into a take ~0.54.
- **95 needs 275 takes at zero contact** (with ib14 >= 0.90, follow >= 0.95), or **279 at the lead's contact** (0.0106).
- **Zero-contact floor** of a take count: 100 (0.90 - takes/360). 262 takes (the lead) -> 17.22; 271 -> 14.72;
  272 -> 14.44; 275 -> 13.61; 277 -> 13.06; 281 -> 11.94.
- **Takes 95 needs at a family's own proximity** = ceil(360 [0.90 - (13.75 - 100 [(0.90 - ib14)+ + (0.95 - follow)+ +
  contact]) / 100]). That column is the honest one: a family that pays in-band or contact needs more takes than 275.
- **The kinematic window is not the binding limit at the legal seats.** Over all 247,860 legal seat pairs (J1 on the
  back of the shoulder or the acromion top, J3 anywhere on the arm) the best window of width >= 80 holds 0.99 of the 360
  (docs/research/fold_ceiling.md section 2, `fold_ceiling/kin_ceiling.json` "curves"). So every "no" below is a metal /
  proximity result measured at specific seats and dyads, not a kinematic impossibility proof.

## 2. The 3-DOF table (one row per legal J1 seat family x realisation)

Takes are workspace takes of 360. Seat naming follows ROUNDS.md: the "back", "k33", "crest" and "H1" rows all sit
J1 on the back / top of the acromion near bvec(97-102, 62-65) (H1: anterior 0.085 / up 0.898 / lateral 0.432; the k33
seats about 6 deg of azimuth forward of the lead's) and differ in J2 / J3 seats and realisation; the "cap pole" J1 is
bvec(43.2, 59.9). Every J1 here is inside ruling 4 (back of the shoulder + acromion top). "Gap at family proximity" = the zero-contact floor of the row's best take count
plus that row's measured in-band / follow / contact penalty (from its best metal cell). Cells in *italics* are bounds or
estimates, not measurements of a buildable design.

| J1 seat family x realisation | kinematic window takes (th >= 5) | law-limited / K-oracle takes | best ghost: frozen gap / takes | best metal: frozen gap / takes | best VERIFIED non-gamed (ledger) | zero-contact floor (best takes) | takes 95 needs at the family's proximity | 95 reachable? |
|---|---|---|---|---|---|---|---|---|
| **Back** of the shoulder, plain O20 3R (no K) | 250 [a] | n/a (no K) | unmeasured (not needed: the kinematic floor is 20.56) | 39.80 FAST only (welded plain 3R, J4) [b]; no frozen exact | none | 20.56 (250) | > 275 even at zero contact | **No - kinematic** (250 < 275) |
| **Back**, knuckle (K law, 3 active) - the lead's family | 272 at the drive's 46-deg stroke [c] | law-only 267 (kK 1.96) - 272 (kK 2.3) [d]; *free-K oracle, any law, 76-deg stroke: 277 / 13 contacts / 17.69* [e]; at the lead's stroke 255 / 20.52 [e] | 16.91 / 269 (ideal drive, proximal-j3, knee rule) [f]; ~40 ghost cells 269-271 | **18.28 / 262** (ib14 0.9012, contact 0.0106) [g] | **conecut-knee-knuckle-3r 18.28, held 22.38 (WATCH)** [g] | 14.72 (271 ghost); 14.44 (272 kin); *13.06 (277 oracle)* | 279 (metal); 281 (ghost); 292 (oracle) | **No** - see reason [R1] |
| **Back / acromion boundary (k33 seats)**, knuckle, any K law | not separately recorded | *free-K oracle 280 / ~21 contacts / 17.25 connected* [h] | = the oracle | none 3-joint (the realised cell is 4-joint) | none 3-joint | *12.22 (280)* | 293 | **No** - the oracle bound is 17.25 [R2] |
| **Cap pole** (acromion top), plain O20 3R | 281 [i] | n/a | hub-2-free bound instead: hub 2 <= 0.12 in band over 668 configs [i] | 56.40 / 267 (ib14 0.502) [j]; searched control 60.61 [k] | none (controls only) | 11.94 (281 kin) | 421 (> 360) | **No - in-band** [R3] |
| **Cap pole**, knuckle (cap-plateau A/B/C) | 275 (cell C; box best 299) [l] | ghost drive (no separate law cell) | 32.08 / 247 (ib14 0.823, contact 0.030) [m] | 33.94 / 245 (buildable one-sided law) [n] | cap-plateau-knuckle-3r 32.08, held 35.16 (no ledger entry; dead at gate 0) [m] | 13.61 (275 kin) | 313 | **No** [R4] |
| **Cap pole**, virtual J2 (spherical four-bar / slaved elbow) | not recorded | n/a | FAST only | 86.95-108.22 FAST vs the plain cap 3R's 63.18 [o] | none (dead at gate 0) | - | - | **No** (24-45 fast points worse than the plain cap 3R) |
| **Crest** (J1 acromion top, J3 deltoid crest), plain O20 3R | 291 with hub 2 in band (336 with hub 2 anywhere; p95 272) [p] | n/a | unmeasured (kinematic scan is the bound) | 34.98 / 218 (ib14 0.897, follow 0.936, contact 0.039) [q] | deltoid-crest-j3-3r 34.98, held 39.27 (WATCH; dead) [q] | 9.17 (291 kin) | 295 | **No - metal**: 218 of 291 kinematic survive [R5] |
| **Crest**, pin knee (cx 0) | as the crest 3R (the knee does not change th) | n/a | unmeasured; joggle bounded at ~25-27 before it was built [r] | **31.50 / 226** joggled (ib14 0.872, contact 0.015); flat 32.84 / 228 [s] | **crest-knee-3r 31.50, held 28.45 (WATCH, NEW-tolcliff)** [s] | 27.22 (226) | 290 | **No** [R5] |
| **Crest**, knuckle with an ideal K law | **unmeasured** - the known hole; no model joins the crest J3 seat to a knuckle (a new model, over the 15-min fill budget) | unmeasured | unmeasured; nearest evidence: proximal-j3 moved J3 up the lateral deltoid at the back seat - 269-271 for every seat [f] | unmeasured | none | - | - | **Unmeasured** (nearest evidence says no) |
| **H1 seats** (J1 acromion top), pin knee (cx 0) | see section 2 note | n/a | GPU knee polish 20.26 REFUTED held out [t] | **27.20 / 237** (ib14 0.895, follow 0.964, contact 0.026) [t] | **skin-normal-3r-pin-knee (H1) 27.20, held 28.55 (WATCH)** [t] | 24.17 (237) | 286 | **No** (237 metal takes) |
| **Antcrest** (J1 acromion top, J3 anterior crest), pin knee | not recorded | n/a | hub-2 need 50-400 mm [u] | 61.12 / 212 [v] | none (dead) | 31.11 (212) | 352 | **No** (hub 2 cannot sit in band) |

**Reasons (measured):**

- **[R1] Back knuckle (the lead's family).** Ghosts with an ideal drive stop at 269-271 takes over ~40 cells (rounds
  12-13; floor 14.72-15.28 > 13.75 even at zero contact). The cap is the stretched-wall fold: 73 bench poses (th
  107-176, 64 of them internal rotation >= 90 across the body), set by the K drive's stroke (dK 52.6 of the 57-deg cap;
  fold_ceiling.md line 425). A free per-pose K (the ceiling of ANY law) with a 76-deg stroke reaches 277 takes, but
  (a) that stroke is not buildable at bk1 26 (K rule forces bk2 >= 55.55; link 1b lands on hub 1's crown, 165.18) and
  long-stroke drives were measured dead (bell crank / ball links 23.31 / 27.67), and (b) of the 24 poses it newly
  closes, 9 are 4.6-13.2 mm in the skin with the best K already picked: 13 contacts, ib14 0.886, gap 17.69. The lead
  also carries 4 contacts, 3 of them dwell poses at K = 0 that no law reaches.
- **[R2] k33 seats.** The per-pose oracle K (each sample a full frozen-model run) reaches 280 connected takes with ~21
  contacts; the external-rotation binders 117 / 119 / 129 touch at every legal K. Moving J1 forward along the acromion
  top (+15 / +25) reads 21.73 / 22.91 (seatoracle-erwall). This oracle bounds every 3-joint K law at these seats (and
  the sensed-K 4th joint).
- **[R3] Cap pole, plain 3R.** Kinematically open (281 -> 11.94 floor), closed by metal: hub 2 must sit on the J2 axis,
  which exits the deltoid / acromion skin 107-116 mm from GH on mode-A poses, so hub 2 is <= 0.12 in band over 668
  configs; the in-band term alone (ib14 0.50 -> 39.8 points) is ~3x the whole 95 budget.
- **[R4] Cap knuckle.** The kinematic surplus is paid back in proximity: a metal search started at the 299-kinematic
  box config walked back to 275 and ended 4 points worse; metal keeps ~40 % of the ghost's kinematic surplus; at its
  measured in-band / contact 95 would need 313 takes. The buildable one-sided law (33.94) trails its same-kit control at
  the lead's seats (30.59 / 259 takes).
- **[R5] Crest.** Kinematically the widest legal family (291 with hub 2 in band), but inside the crest basin
  fold-free poses and clearance trade ~1:1 (closure <= 0.81 with hub 2 in band); the fold gain returns as J3-window
  stops (5 -> 17) where member 3 sweeps over the crest; overhead skin at elevation 150 in the scapular plane is 6.9 mm
  from the chain. Metal keeps 218-228 of the 291.

**Section 2 note - H1-seat kinematic window:** see section 5 (fill attempt) - if not filled there it stays unmeasured;
H1's 237 metal takes against the 286 its proximity needs make the column non-decisive for this row.

Citations:
[a] docs/concepts/ROUNDS.md line 2595 (planner measurement, Bench(110,360) ws, closure at the 5-deg margin, no metal;
bvec(97.3, 64.6), a1/a2 41.7/72.1; no script saved), repeated at lines 2780, 3109, 3748.
[b] docs/FINDINGS.md Round J4 item 4 (welded plain 3R at the lead's seats 39.80 fast; 23.65-31.83 with the psi2 shift).
[c] docs/research/fold_ceiling.md line 175 and section 4b (`fold_ceiling/kin_ceiling.py`; 272 = 261 taken + 9 knee + 2
contact, measured on the roller leader's seats, same seat family).
[d] docs/concepts/ROUNDS.md line 1583 (law-only kinematics; kK >= 2.7 kills the lobe at its base radius at PA <= 42).
[e] docs/concepts/verify/seatoracle-erwall-knuckle-3r/cell_L0b.json `/oracle` (17.69, reach 0.7694, ib14 0.8862,
contact 0.0325); control at the lead's stroke 58.77: docs/concepts/seatoracle-erwall-knuckle-3r.md (20.52, 255 takes,
5 contacts). Kit metal, oracle K: a bound, not a design.
[f] docs/concepts/rows/proximal-j3-geodesic-knuckle-3r.json `/audit/at_knee_rule` (16.91, reach 0.7472, 4 contacts);
round 13 lesson 1, docs/concepts/ROUNDS.md line 2775-2780.
[g] docs/concepts/verify/conecut-knee-knuckle-3r_v_bench_frozen.json `/frozen` and `_v_held_frozen.json` `/frozen`
(22.38); ledger `python3 tools/alignment_ledger.py get conecut-knee-knuckle-3r` -> watch.
[h] docs/concepts/freek-oracle-route-knuckle-4r.md line 85 (ORACLE connected 17.25, 280, reach 0.7778, ib14 0.8990,
follow 0.9455, contact 0.0448; near-touch 21.46).
[i] docs/concepts/ROUNDS.md lines 2596-2603 (planner measurement: J1 bvec(43.2, 59.9), a1/a2 50.2/60.3, J3 wdir(92,
-9); hub-2 level 107-116 mm; 668 configs <= 0.12 in band).
[j] docs/concepts/acromion-relay-4r.md line 238 (T-0 control = plain O20 3R, frozen exact 56.40, reach 0.742, ib14
0.502, contact 0.008).
[k] docs/concepts/rows/cap-nullspace-4r.json (its searched plain cap 3R control 60.61 frozen).
[l] docs/FINDINGS.md lines 3122-3125 and 3128-3129; box best 299: docs/concepts/verify/cap-plateau-knuckle-3r_kinscan_C.json [0].ws.
[m] docs/concepts/verify/cap-plateau-knuckle-3r_frozen97_C2best.json `/frozen`; held docs/concepts/rows/cap-plateau-knuckle-3r.json
`/held_self/frozen` (35.16); ledger exit 2 (no entry).
[n] docs/concepts/verify/cap-plateau-knuckle-3r_frozen97_A3onesided.json `/frozen` (33.94, reach 0.6806).
[o] docs/FINDINGS.md "Round J2" heading; docs/concepts/rows/remote-pole-fourbar-j2-3r.json (90.11 fast).
[p] docs/concepts/verify/deltoid-crest-j3-3r_audit3_kinscan.json (`kin360_max_hub2_inband` 0.8083, `kin360_max_all`
0.9333, `kin360_p95_hub2_inband` 0.7556; 6676 honest configs).
[q] docs/concepts/verify/deltoid-crest-j3-3r_audit_frozen_s12_ee8.json `/wear` (34.98); held 39.27 and the ~1:1 trade:
docs/FINDINGS.md "Round 14 re-dispatch" item 7; ledger -> watch.
[r] docs/FINDINGS.md "Round 14" item 3 (joggled knee bounded at about 25-27 frozen; built, it read 31.50).
[s] docs/concepts/verify/crest-knee-3r-joggle_v_bench_frozen.json `/model` (31.50, reach 0.6278) and
`_v_held_frozen.json` `/model` (28.45); flat: crest-knee-3r_v_bench_frozen.json `/model` (32.84); ledger -> watch.
[t] docs/concepts/rows/skin-normal-3r-pin-knee.json (`v_gap` 27.20, `v_reach` 0.6583, `v_inband14` 0.8953,
`v_follow` 0.9636, `v_contact` 0.0256; held `v_polish2_h1_held_gap` 28.55; GPU knee `v_gpuknee_*` refuted); ledger -> watch.
[u] docs/concepts/ROUNDS.md line 3768. [v] docs/concepts/rows/crest-knee-3r.json `/antcrest_2026_10_18/frozen_exact_bench`.

Gamed rows are excluded from the "verified" column: lowarm-halfring-knuckle-3r (18.83, GAMED M3; buildable level
18.65 / 19.05), dipped-law-groove-knuckle-3r, seed-offset-3r-slides. The model-number-only desmo rows (desmo-slipper
18.95, desmo-conecut 18.98; WATCH, stage 1 inside link 1b's plate) take the lead's 262 takes and do not change the
back-knuckle row's take count.

## 3. 4-joint reference rows (not 3-DOF; for comparison only)

| 4-joint design | takes | frozen gap (held) | contacts / depth | joints / cx | status |
|---|---|---|---|---|---|
| lead-relay-j0-4r, ghost J0 (zero size) | 275 | 16.22 (16.07-18.22 over seats) | - | 4 / - | ghost: no hardware |
| lead-relay-j0-4r, real O20 hub 0 + link 0 | 273 | **22.18** | 8 | 4 / 50.75 | VERIFIED, dead (hub 0 + link 0 0-2 % in band at 108 seats) |
| free-K oracle at the k33 seats (freek cell A) | 280 | 17.25 connected (21.46 near-touch) | ~21 | instrument | bounds every K law and a sensed K |
| K-free ideal 75-deg cuff relay on a plain O20 3R | 304 | **10.22** | 15 ws contacts | 4 / no hardware | bound only: real arm tracks capped ~45 deg by the torso; real kfree-armarc-relay-4r 26.42 |
| freek-oracle-route-knuckle-4r (sensed K + J3 dowel) | 280 | **16.20** (21.89) | 15 / 78.55 mm | 4 / 33.25 | VERIFIED, WATCH |
| same, final polish pick1 | 275 | **15.40** (20.50 CAD shape; 20.24 env fit) | bench 0.0179 contact; 39.47 mm | 4 / 33.25 | polish CONFIRMED by its verifier; does not replace the verified fields |
| proxtrack-relay-knuckle-4r | - | screened 14.02 plain / 14.40 gate (held 18.01) | - | 4 / 52.5 | **UNVERIFIED** - an independent verification is running in parallel (pending; not waited for) |
| armarc-relay-knuckle-4r | 275 | 18.01 | 11 | 4 / 52.0 | VERIFIED, dead (> 17.5) |
| minarc-stop-knuckle-4r BDp (older) | 260 | 19.54 (24.18) | - | 4 / 32.5 | VERIFIED |

Against the 3-joint lead **conecut-knee-knuckle-3r 18.28 / held 22.38, 262 takes, 4 contacts / 20.24 mm, cx 18.5**.

Citations: docs/concepts/rows/{lead-relay-j0-4r,freek-oracle-route-knuckle-4r,proxtrack-relay-knuckle-4r,
armarc-relay-knuckle-4r,minarc-stop-knuckle-4r,kfree-armarc-relay-4r}.json; docs/FINDINGS.md "Round J3" / "Round J4" /
"freek-oracle-route-knuckle-4r final polish" (+ its independent verification); docs/research/fold_ceiling/kfree_armarc_ideal_frozen_exact.json
(`/wear` 10.22, `why_ws` 304 taken, 15 contact); docs/concepts/freek-oracle-route-knuckle-4r.md line 85. The polished
pick1's take count is 0.764 x 360 = 275 (FINDINGS "freek ... final polish": reach 0.778 -> 0.764).

## 4. Reconciling parking_k 0.775-0.778 with the 267-272 law cap and the 269-271 ghosts

The three numbers measure different things and agree once the K stroke is matched. parking_k's 0.775-0.778
(docs/research/fold_ceiling.md section 4, table at lines 324-334) is an ESTIMATED verified reach (279-280 takes) for an
IDEAL law with a ~75-deg K stroke on a 28-32 / 48-50 K dyad, every part parked at its clip max + 4 mm, with the leader's
in-band 0.894 and contact 0.005 held fixed, and before the knee, the part-part collisions and the drive's own metal.
The 267-272 law cap (docs/concepts/ROUNDS.md line 1583) is the kinematic count of the REAL lobe law, which cannot exceed
kK 2.3 at PA <= 42 (kK >= 2.7 kills the lobe at its base radius), i.e. a ~46-57 deg stroke; and the 269-271 ghosts are
frozen-exact takes of real chains with the drive metal deleted at those strokes. At a matched stroke parking_k agrees
with both: 26 / 38 at 46.25 -> 272 in window, est. reach 0.725 (the verified 0.7278); 26 / 38 at 57.5 -> 275 in
window, est. 0.731 (263 takes). The 0.775-0.778 needs the 75-deg stroke that no measured drive delivers: the lobe law
caps first, and the long-stroke drives were measured dead (bell crank / ball links do not park, 23.31 / 27.67;
longstroke_drive.md). The one direct test of parking_k's premise at a ~75-deg stroke is round 105's free-K oracle at
the lead's seats with stop B 76 (seatoracle-erwall cell L0b, kit metal, the best K per pose): 277 takes as estimated
(within 2-3 of 279-280), but ib14 0.886 instead of the assumed 0.894 and 13 contacts instead of ~2, because 9 of the 24
newly closed poses are external-rotation poses 4.6-13.2 mm in the skin at every legal K - so 17.69, not ~13.7.
parking_k's estimate was right about the takes and wrong about the proximity: a uniform +4 mm part lift does not clear
the ER binders, which bind radially (link 2 over the deltoid crest, hub K overhead) and are not reachable by K.

## 5. Jam-bias column for the pin-knee cells (H1 pin-a running gap)

PENDING

## 6. Conclusion for the user

PENDING

## 7. Sources

PENDING

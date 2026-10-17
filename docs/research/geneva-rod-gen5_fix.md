# Gen-5 fix: the slaved-K coupling in the dynamics judge, the lobe skin hit, the drive's real parts (2026-10-16)

Design: geneva-tail-knuckle-pinknee-3r, rod embodiment (verified v_gap 23.57, held out 28.12; 3 active J1 / J2 / J3 + K
slaved to q2 by a lobe on hub 2 -> MR63ZZ roller -> bell crank -> pushrod with igubal eyes -> horn on link 1a's arbor).
Builds: `pipeline/full-exo/designs/l1_geneva-rod` (L1), `user_geneva_rod` (full CAD), `user_geneva_rod_v2` (this fix).
Open items came from the independent check `pipeline/full-exo/designs/user_geneva_rod/VERIFY.md` (NOT REFUTED, 5 corrections).

## 1. Judge: a general slaved-coordinate coupling in judge/dynamics.py (MEASUREMENT change)

**What was wrong.** The general chain modelled K as a free, spring-held knuckle. A slaved K has no free spring path: the
drive sets it. So on the L1 K drifted 15.9 deg off its path (R17 FAIL, 4 lags > 10 deg), and the full CAD's drive groups
(`dk` bell crank, `dr` rod) had no place in the serial chain: the judge fell back to the spherical path, which stopped on
`KeyError 'l1'`.

**The term.** A design declares each slaved hinge in its `build.json` under `"slaved"` (the interface is in the judge's
docstring, "SLAVED COORDINATES"):

| key | meaning |
|---|---|
| `slaved`, `driver` | the two hinges, each named by the member groups it joins (`["l1a","l1b"]`, `["l1b","l2"]`) |
| `x_key`, `y_key` | where every clip frame stores the driver / slaved angle in the law's own convention (`q.1`, `knuckle.dK`) |
| `law_x_deg`, `law_y_deg` | the law as a table (deg), piecewise linear, ends held (a dwell is a flat end) |
| `rest_y_deg` | where the slaved hinge sits when the drive does not push (stop A) |
| `closure` | `force` (a cam held on by a spring: the drive only pushes, so lift-off is allowed and reported) or `form` (a linkage such as an RSSR, or a form-closed cam: bilateral) |
| `drive_groups` | posed drive bodies and the member whose mass they ride with (null: the member they turn least against) |

The judge maps the law onto its own fitted hinge angles. It does this by affine fits of the frames' `x_key` / `y_key` values;
|slope| must be 1 within 1e-3 and the residual < 0.05 deg, or the judge stops. It then checks the clips' own frames against
the law, and couples the two hinges with a MuJoCo joint equality. The equality is re-linearised on the law's tangent every
step, which is exact for a piecewise-linear law. Its reaction acts on the driver, so the arm feels the drive's load. With
`force` closure the equality is on only while the drive pushes:
- off in the dwell;
- off on a pull (lift-off);
- back on when the follower meets the law again.

Drive bodies are lumped rigidly on their mount: dk 4.44 g turns 5.1 deg on link 1b, dr 3.19 g turns 0.7 deg. Their own
motion is reported, not simulated. The drive's bearing friction is not modelled: the roller and the crank run on ball
bearings, and the rod-end balls carry < 0.03 N.m at these loads.

**R17 rule for a slaved joint.** A slaved hinge is DRIVEN, so it leaves the spare list. R17 then needs its error against the
law, at the simulated driver, to stay <= 5 deg (the spare-drift threshold); this covers lift-off. Its deviation from the
plan is the chain's own q2 deviation times the law's ratio (kK 3.18). That deviation is reported (`slaved.plan_err_deg`) next
to `config_dev_deg`. R17 thresholds that number for no driven joint: J1 deviates 6.6 deg and J2 5.4 deg on these designs
and on every knuckle design without failing. **A stricter reading would fail the L1:** if K's plan deviation were held to
5 deg, the L1 would fail at 5.69 deg on Reach a high shelf. That is why I state the choice here rather than bury it.

**No drift on designs without a slaved coordinate** (`docs/research/geneva_rod_drive/r17_nodrift.json`). The pre-change judge
(a16c80b) and the new judge ran on the same machine (`--quick`: nominal + k-rate 0.010). Comparing the whole dynamics.json,
minus version / seconds / rule text, every design came out **identical**:

| design | R17 | M_GH peak (N.m) | cuff (N) | twist (deg) | spare drift (deg) |
|---|---|---|---|---|---|
| l1_minarc-pick1 | PASS = PASS | 0.061 | 0.30 | 1.98 | 3.68 |
| user_minarc_pick1 | PASS = PASS | 0.062 | 0.31 | 2.00 | 3.72 |
| l1_minarc-bdp | PASS = PASS | 0.152 | 0.69 | 1.96 | 2.13 |
| l1_skin-normal-3r-pin-knee-h1 | PASS = PASS | 0.049 | 0.22 | 1.50 | - |

**R17 with the coupling** (full judge, farm, $0.05; nominal = rolling bearings mu 0.005, speed 1):

| build | before | after | M_GH peak / rms (N.m) | cuff (N) | twist (deg) | K vs law (deg) | K vs plan (deg) | lift-off (share of driven samples) | drive torque on K (N.m) |
|---|---|---|---|---|---|---|---|---|---|
| l1_geneva-rod | FAIL (K drift 15.9, 4 lags) | **PASS** | 0.123 / 0.081 | 0.55 | 3.72 | 0.146 | 5.69 | 0 | 0.021 |
| user_geneva_rod | NOT RUN (KeyError 'l1') | **PASS** | 0.122 / 0.081 | 0.53 | 3.68 | 0.156 | 5.63 | 0.0006 | 0.023 |

The law in build.json reads the clips' K to 0.0009 deg (L1) and 0.005 deg (CAD, the 15-row RSSR table). The cuff pressure
peak is 0.08 kPa against the 7.5 kPa budget.

The plain-bearing and constant-friction comparison cases fail, as they do for every knuckle design (pick1 too). Under
0.05 N.m of constant joint friction, Raise overhead opens K 24 deg away from stop A in the dwell. This is a real
force-closure effect: in the dwell only the 0.08 N.m clock spring holds K, and those cases print it as K's error against
the law. It does not apply with rolling bearings, but it is the first thing to watch if a plain bearing goes into K.

## 2. Lobe skin hit: candidate fixes measured in the judge

Tool: `docs/research/geneva_rod_drive/lobe_skin.py`. The ring is built by the CAD builder's own `lobe_ring()` on a
drive re-solved by the red team's `drive.py`, posed by the judged l2 frames, and measured signed against the judges' skin.
Frames: every frame of Raise overhead, every 4th of Reach a high shelf / Comb hair, every 8th of the rest. The rebuilt
baseline reproduces the as-built ring (-0.264 vs -0.258 mm).

**Where it enters:** at the profile END (r 12.87, az 60.7 deg, the contact at stop B), over the whole band height, at
Raise overhead frames 78-83. 1.2 % of the ring's samples are within 0.3 mm. The flank behind the peak is +0.23 mm and the
dwell +2.2 mm. So trimming the dwell or the flank (i) cannot fix it: the offending metal is the law's contact surface.

**Round 3 (this run): every candidate on the REAL-SIZE drive.** Rounds 1-2 (`lobe_skin_candidates_*.json`) solved the
drive with the gen-5 rod-end height. The real igubal (6 mm eyes) and the 3.8 mm horn hub (section 3) raise the rod end at
the horn by 3.6 mm, and that alone moves the lobe. So I re-ran every candidate with that height (`lobe_skin.py real`, the
posed skin cached per frame, 375 frames as above, 27 min, one process; `lobe_skin_real.json`). Pass = >= 0.3 mm on every
frame. Forces are the red team's spring case (0.08 N.m + 0.015 N.m/rad on K) and spring + the MVP1 opening bound
(0.033 N.m), through the solved arms. Every candidate has the same part list, so tools/simplicity.py stays at 12.0.

| candidate (least change first) | min skin distance (mm), where | frames < 2 mm | lobe profile r (mm) | cost | verdict |
|---|---|---|---|---|---|
| gen-5 as built (old rod-end height) | -0.258, Raise overhead 78 | 71 | 10.74 -> 12.87 | - | FAIL |
| real parts only (no lobe fix) | -0.091, Raise overhead 78, profile end (r 12.68, az 60.6) | 69 | 10.68 -> 12.68 | - | FAIL |
| (i) stop B at dK 50 (a1max 57.12) | -0.039 | 69 | -> 12.59 | bench 23.57 -> **23.57** | FAIL |
| (i) stop B at dK 47 | +0.016 | 69 | -> 12.51 | (between) | FAIL |
| (i) stop B at dK 44 (a1max 54.97) | +0.060 | 69 | -> 12.42 | bench **23.85** (+0.28), reach 0.7306 -> 0.7278 | FAIL |
| (i) stop B at dK 40 (a1max 53.46) | +0.155 | 67 | -> 12.30 | bench **24.77** (+1.20), reach 0.7139 | FAIL |
| (i) stop B at dK 35 | +0.258 | 65 | -> 12.14 | > +1.2 | FAIL |
| (v) thinner band 2.1 / 1.6 mm (top kept) | -0.094 / -0.096 | 69 | unchanged | - | FAIL: the end enters over the whole height |
| (iv) radial offset: dwell r 9.6 | **+0.409** | 65 | 10.19 -> 12.21 | forces unchanged; the follower-arm eye comes **0.1 mm** off the J2 cap skirt (r 10 from F2+8.8; was 0.6) and the roller top sits 0.1 mm under it | passes the skin, not buildable at normal tolerance |
| (iv) radial offset: dwell r 9.1 | +0.902 | 59 | 9.69 -> 11.73 | the eye 0.4 mm INTO the J2 cap | infeasible |
| **(iv) phase: mirrored follower (side -1)** | **+2.255** (the dwell, r 10.1) | **0** | 10.52 -> 12.76 at az -21.9 -> -5.8 (was 47.9 -> 60.6) | rod 42 / 59 N, roller 46 / 63 N (both LOWER); pressure angle 26.5-38.2 deg (limit 45); horn misalignment 12.8-15.0 deg (igubal swivel 32 deg) | **chosen** |
| (iii) crank 12, horn r 2.0 | +0.931 | 57 | 10.36 -> 11.57 | roller **85 / 114 N** | passes the skin, overloads the roller |
| (iii) crank 13, horn r 2.0 | +1.046 | 57 | 10.32 -> 11.44 | roller **94 / 127 N** | same |
| (iii) crank 14, horn r 2.493 | +0.864 | 59 | 10.39 -> 11.64 | roller **84 / 113 N** | same |
| (iii) crank 14, horn r 1.8 (the earlier v2 draft) | +1.260 | 53 | 10.26 -> 11.20 | rod 82 / 110 N, roller **115 / 155 N**; K error 2.4-3.5 deg per 0.05 mm of lobe (baseline 1.2-1.5) | same |
| baseline for the forces (a_c 9, r_h 2.493) | | | | rod 53 / 71 N, roller 48 / 65 N | |

What the table says:
- **Stop B cannot buy 0.3 mm.** Moving it costs nothing down to dK 50. It costs 0.28 points at 44 and 1.20 at 40, and
  even 35 deg leaves the ring 0.04 mm short. Bench runs: `stopb_bench.py` = the verifier's harness with only a1max
  changed (frozen exact Bench(110,360), flood fill), `stopb_bench_<a1max>.json`. The as-verified run reproduces 23.57.
- **A thinner band does nothing**, as section 2's probe predicted.
- **The ratio fixes (iii) pass the skin by buying a smaller lift with a higher mechanical advantage.** That multiplies the
  roller load: 85-155 N against the MR63ZZ's static rating of about 0.07-0.10 kN. They are out until a bigger roller fits,
  and none does: the follower arm must stay >= 8.3 mm (round 2). The earlier v2 draft in the tree (crank 14, horn r 1.8)
  was one of these, and this run replaces it.
- **The radial offset passes the skin but not the shop.** At r 9.6 the follower-arm eye runs 0.1 mm from the J2 cap skirt.
- **The mirrored follower moves the profile 70 deg round link 2, away from the deltoid.** It does not shrink the profile
  away from the skin. At the overhead peak the ring's nearest metal is then the O20.2 dwell (+2.26 mm), and no sampled
  frame has the ring under 2 mm. It changes no part count and no law: same lobe law, same K, same frames for every chain
  group. Only the bell crank's follower arm points the other way round the rocker post. Its forces are lower and its
  pressure angle higher (still 7 deg under the 45 deg limit). The horn's misalignment rises to 15.0 deg. That is within
  the KGLM-03's 32 deg swivel if the swivel is the full angle, with 1 deg spare if it is +-16. A horn pin tilted to the
  mid-stroke rod line, as the crank pin already is, would take that back. That is a later refinement, stated here.

LOBE_ALL

## 3. Real parts

Catalogue data, and what the fix builder (`pipeline/conformal/param_cad/user_style_geneva_fix.py`) now builds. "Gen-5" is
`user_geneva_rod` as committed; "v2" is this fix.

| part | catalogue data | gen-5 as built | v2 (real size) |
|---|---|---|---|
| 2x rod-end spherical bearing | igus igubal **KGLM-03**: bore 3, OD 10, **6 mm** high, 200-550 N static, 32 deg swivel, iglidur W300 ball in an igumid G housing (igus product page; distributor listings) | O10 housing in an O13 x **4** eye, ball 3.9 mm | O10 x **6** housing pressed in an O13 x 6 eye, ball truncated at +-3.0. The rod line rises **3.6 mm** at the horn (1.0 for the wider eye, 2.6 for the taller horn hub below). The RSSR, the crank-pin tilt (24.6 deg) and the lobe are re-solved for that height |
| clip on the O3 crank pin and horn pin | **DIN 6799 RS 2.3**: shaft 3-4, groove O2.3 x **0.64**, s 0.6, d3 max 6.3, land **n >= 1.0** | no groove; the clip overlaps the pin; land 0.5 / 0.6 | groove O2.3 x 0.64 cut 0.15 past the eye face, clip in it, land 1.0 |
| bell crank retention on the O5 post | **DIN 6799 RS 4**: shaft 5-7, groove O4 x **0.74**, s 0.7, d3 max **9.3**, land **n >= 1.2** | none: nothing reacts the wave-washer preload | 0.3 mm shim on the top MR85ZZ inner ring + RS 4 in an O4 x 0.74 groove. **Land 1.2, O9.3 clip (this run; the earlier fix draft used 1.0 and O9.0, under DIN's n min)** |
| follower roller | **MR63ZZ** 3 x 6 x 2.5. Static rating about 0.07-0.10 kN (distributor figure 16 lbf, the red team's 0.09-0.10 kN; the maker's datasheet is still to confirm) | no retention below the roller | inner race pressed on an O3 m6 pin + retaining compound, pin pressed in the follower arm (stated; no geometry change) |
| bell crank bearings | **MR85ZZ** 5 x 8 x 2.5 (2x, wave-washer preloaded) | no reaction for the preload | reacted by the shim + RS 4 clip |
| horn clamp screws | **ISO 7046-1 M1.6** countersunk: P 0.35, head O3.0 max x 1.0, 90 deg; tapped blind O1.25 | M1.6 in a 1.2 mm hub: 1.2 mm of thread (0.75 d) | hub 3.8 mm. **M1.6 x 4 (this run; the draft's x 5 ended 0.05 mm above the hole floor and left no tap lead):** 2.6 mm of thread (1.6 d), 1.05 mm (3 P) for the tap lead |
| K and J2 stops | ISO 8734 O3 x 6 dowels, m6 | as built | unchanged |
| hubs | v5 O20 stack, MR117-2RS 7 x 11 x 3 pair, M7 x 0.5 ring nut | as built | unchanged |

## 4. Where the full CAD's -0.8 R1 points go (against the L1)

`docs/research/geneva_rod_drive/r1_attr.py` scores scratch copies of user_geneva_rod with parts removed from exo.glb, using
the judges' own score_design.py (BANDS 10,14, step 3). This ran on the farm ($0.21); the tree was never written.

| variant | R1 (2-14) | R1-aim (2-10) | Raise overhead | Comb hair | Wave | Drink |
|---|---|---|---|---|---|---|
| L1 (l1_geneva-rod) | 81.10 | 51.10 | 72.97 | 88.38 | 66.85 | 88.09 |
| full CAD as built | 80.30 | 49.80 | 73.83 | 87.11 | 63.61 | 86.97 |
| minus dk + dr (bell crank set, rod set) | 80.41 | 49.86 | 71.46 | 88.30 | 65.57 | 86.97 |
| minus the D9-01 lobe ring | 80.37 | 49.82 | 74.03 | 87.11 | 63.95 | 86.97 |
| minus all drive metal | 80.48 | 49.89 | 71.68 | 88.30 | 65.94 | 86.97 |

- **The drive explains 0.19 of the 0.81 points net**: dk / dr -0.11, the lobe -0.07. The drive ADDS coverage at the overhead
  peak (Raise overhead 71.7 -> 73.8) and takes it in Comb hair / Wave, where the bell crank comes within 2 mm of the skin.
- **The remaining 0.62 points are in the non-drive parts**: the machined bars, hubs and caps against the L1's slabs. They
  show in every clip: Drink -1.1, Wave -0.9, Walking -0.7, Wash -0.5, and Raise overhead -1.3 without the drive.
- That pattern fits the checker's hub-zone bar lift (up to 1.85 mm over the model strap on link 2). The next attribution
  step is a per-group swap (each CAD group replaced by its L1 group).

V2_SECTION

# Gen-5 fix: the slaved-K coupling in the dynamics judge, the lobe skin hit, the drive's real parts (2026-10-16)

Design: geneva-tail-knuckle-pinknee-3r, rod embodiment (verified v_gap 23.57, held out 28.12; 3 active J1 / J2 / J3 + K
slaved to q2 by a lobe on hub 2 -> MR63ZZ roller -> bell crank -> pushrod with igubal eyes -> horn on link 1a's arbor).
Builds: `pipeline/full-exo/designs/l1_geneva-rod` (L1), `user_geneva_rod` (full CAD), `user_geneva_rod_v2` (this fix).
Open items came from the independent check `pipeline/full-exo/designs/user_geneva_rod/VERIFY.md` (NOT REFUTED, 5 corrections).

**Status 2026-10-17 (this run closes sections 2-5).**
- Lobe: radial offset (dwell r 9.6) + an O4.5 follower eye, +0.41 mm on every frame.
- Real parts: KGLM-03 at 6 mm, DIN 6799 grooves with catalogue lands, the post clip, M1.6 x 4.
- Link 1a: repaired.
- R1: link 2's group holds 0.53 of the 0.62 points.
- v2: built and judged (fast).

**Open:**
- a FULL judge run of v2 (R6 at step 1, R2 at step 2, R16 at step 4), and R17 / R11 on the farm (no mujoco here);
- the Comb hair -0.83 attribution;
- a bar-only / hubs-only split of link 2's 0.53;
- the horn pin tilt (misalignment 11.8-13.9 deg on the KGLM-03);
- the MR63ZZ static rating from the maker's datasheet;
- the re-shoot (needs the user's yes).

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
| **(iv) radial offset: dwell r 9.6** | **+0.409** | 65 | 10.19 -> 12.21 | forces unchanged (rod 53 / 71 N, roller 49 / 66 N), pressure angle 14.1-35.9 deg; with the O5 follower eye its edge comes **0.1 mm** off the J2 cap skirt (r 10 from F2+8.8; was 0.6), so the eye shrinks to O4.5 (0.75 mm wall round the pressed O3 pin): **0.35 mm** | **chosen (built)** |
| (iv) radial offset: dwell r 9.1 | +0.902 | 59 | 9.69 -> 11.73 | the eye 0.4 mm INTO the J2 cap | infeasible |
| (iv) phase: mirrored follower (side -1) | **+2.255** (the dwell, r 10.1) | **0** | 10.52 -> 12.76 at az -21.9 -> -5.8 (was 47.9 -> 60.6) | rod 42 / 59 N, roller 46 / 63 N (both lower); pressure angle 26.5-38.2 deg; horn misalignment 12.8-15.0 deg. **Built, then rejected: the lobe nose now sweeps through the bell crank's O10 tube, -1.16 mm** (the builder's posed drive check over 400 workspace poses) | FAIL (part clash) |
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
- **The mirrored follower moves the profile about 70 deg round link 2, away from the deltoid.** The ring's nearest metal at
  the overhead peak is then the O20.2 dwell (+2.26 mm), and no sampled frame has the ring under 2 mm. I built it first
  (`--side -1`). The fix builder's own posed check then found the cost: the profile now runs past the rocker post's
  azimuth, and over the J2 window the lobe nose sweeps through the bell crank's O10 tube (-1.16 mm, and the tube spans the
  band height). Moving the post is a new drive layout, so the mirrored follower is out for this fix.
- **The radial offset is the fix.** The dwell moves from r 10.1 to 9.6, so the roller rides 0.5 mm closer to J2's axis and
  the whole profile comes in by 0.5 mm. The law, K, the frames, the forces and the part list do not change. The one
  clearance it eats is the follower eye against the J2 cap skirt (0.6 -> 0.1 mm). An O4.5 eye (0.75 mm wall round the
  pressed O3 pin) gives back 0.35 mm. The arm's net section is then 2.25 mm2, at about 120 MPa in-plane bending at 66 N,
  against 880 MPa yield for Ti-6Al-4V. The roller's top face stays 0.1 mm under the cap skirt, as it already was in gen-5
  (0.143 mm in that build's posed check). It now overlaps the skirt radially by 0.4 mm. An open MR63 (3 x 6 x 2) would
  give 0.6 mm there if the build wants more.

**Every frame, the chosen fix.** `LOBE_SHORT="dwell r 9.6" lobe_skin.py real all` (every frame of every clip: 1337):
min **+0.409 mm** (Raise overhead frame 78, the profile end, r 12.21), 65 frames under 2 mm, the return flank +0.90 mm,
the dwell +2.17 mm (`lobe_skin_real_all.json`, 6 min). The built ring is this ring: the build ran the same `lobe_ring()`
with the same drive (profile r 10.186 -> 12.207, az 48.27 -> 61.34 deg in both). The judges' Raise-overhead minimum gap
says the same from the outside: 0.24 -> 0.72 mm (section 5).

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

**Per-group swap (this run).** `docs/research/geneva_rod_drive/r1_swap.py` starts from the full CAD without its drive
metal. It puts back ONE member group as the L1 built it, leaving out the L1's own drive keep-outs, and scores with the
judges' score_design.py (BANDS 10,14, step 3, locally, 26 min a variant). Both builds pose every chain group by the same
frames, so the swapped group sits where the L1 put it.

| variant | R1 (2-14) | R1-aim (2-10) | Raise overhead | Comb hair | Wave | Drink | Wash | Walking |
|---|---|---|---|---|---|---|---|---|
| full CAD minus all drive metal (section 4 above) | 80.48 | 49.89 | 71.68 | 88.30 | 65.94 | 86.97 | - | - |
| ... with **link 2's group (l2) from the L1** | **81.01** | **50.55** | 72.68 | 88.53 | 66.94 | 88.02 | 60.35 | 96.45 |
| ... with **link 1b's group (l1b) from the L1** | 80.44 | 50.18 | 71.54 | 88.31 | 65.81 | 86.96 | 59.80 | 96.37 |
| L1 (l1_geneva-rod, with its drive keep-outs) | 81.10 | 51.10 | 72.97 | 88.38 | 66.85 | 88.09 | 60.38 | 97.08 |

- **Link 2's group carries 0.53 of the 0.62 non-drive points** (85 %), and 0.66 of R1-aim. With l2 swapped, the CAD sits
  0.09 under the L1. Drink, Wave and Raise overhead come back to within 0.3 of the L1.
- The l2 group is hubs 2 and 3 (v5 O20 stacks, torispherical caps), the 4-strip machined link 2 bar, and the J2 stop
  dowel. The checker measured the bar riding up to 1.85 mm over the model strap in the hub zones, where the 60 deg ramp
  rule lifts it. That is the leading cause, but this swap does not separate the bar from the hub stacks. The next
  attribution step is a bar-only and a hubs-only swap (`r1_swap.py` takes the group, and a name filter is a one-line
  addition).
- **The fix is not local to this builder.** The bar comes from user_style_minarc.py's strip builder, imported unchanged by
  every gen-4 / gen-5 CAD. Its hub-zone ramp follows the user's 2026-10-16 ruling (ramps up to 60 deg near a hub, bend
  radius >= 15 mm). Lowering it is a change to the shared bar builder that every user-style CAD would inherit, so it
  needs its own judged run on all of them, not a patch inside the geneva fix.
- Link 1b's group is worth -0.04 R1 (+0.29 R1-aim): nothing. The l1a and base swaps were stopped unfinished to free the
  CPU for the judges. With l2 at 0.53 and l1b at -0.04, they and l3 / l4 share the remaining 0.13.

## 5. V2: rebuild and re-judge (DESIGN change, measured separately from the measurement changes)

**Build.** `user_style_geneva_fix.py --r-base 9.6 --arm-half 2.25` on `user_geneva_rod` -> `user_geneva_rod_v2`. It rebuilds
the drive parts: the lobe ring, the bell crank set, the pushrod set and the horn set. It repairs link 1a's solid
(BRepAlgoAPI_Defeaturing removes the 0.24 mm2 sliver face 78, the face that failed BRepCheck after tessellation; volume
change 0.0 mm3). It copies every other part, STEP and chain frame unchanged, and re-poses the drive groups dk / dr by the
exact RSSR closure. Result: 108 parts, 244.1 g, no invalid or multi-solid part, roller-to-lobe deviation 0.000 mm and
closure 0.000 mm on the law table. The slaved-K declaration is regenerated from the build's own drive_kin rows (same law).

The builder's posed drive check over 400 workspace poses (worst signed clearance between moving drive parts):

| pair | gen-5 | v2 |
|---|---|---|
| roller on the lobe | -0.001 (contact) | -0.000 (contact) |
| bell crank vs the lobe ring | +0.51 | +0.76 |
| follower eye vs the J2 cap | +0.60 | +0.35 (eye O4.5) |
| roller vs the J2 cap | +0.14 | +0.10 |
| pushrod vs the K clock-spring cap | +1.18 | **+3.75** (rod line 3.6 mm higher) |
| pushrod vs the horn plate | +0.17 | +0.43 |
| horn pin vs the igubal housing | - | +0.27 |
| igubal balls in their housings | - | 0.000 (seated) |

**How it was judged.** The run was `tools/judge_all.sh user_geneva_rod_v2 fast`, split into two queues of the same
commands, each judge with `--jobs 1` (at most 2 local processes). The farm was not permitted in this session, and the
full run does not fit the remaining box on this 4-core machine. That gives these MEASUREMENT differences from the
before-scorecard (a full run, partly on the farm). None of them is a design effect:
- R1 / R1-aim / R3 / R4 run at step 3 in both modes: identical measurement.
- R6 at step 3 (every 3rd frame) instead of 1. The checker re-ran gen-5 at step 3 and also got 0.0.
- R2 at step 6 instead of 2.
- R16 at step 12 (120 poses) instead of 4 (358). **On the same 120 poses gen-5 also scores 68.33 %**, so R16 does not
  move; the 72.6 -> 68.3 difference is sampling only.
- R17 / R11 NOT RUN: this container's Python has no mujoco. The before values came from the farm.

| | gen-5 `user_geneva_rod` (full) | v2 `user_geneva_rod_v2` (fast) | what changed it |
|---|---|---|---|
| R1 (2-14 mm) | 80.30 % | **80.17 %** (-0.12) | design (Raise overhead +0.23, Comb hair -0.83, the rest within 0.11) |
| R1-aim (2-10 mm) | 49.80 % | 49.77 % | design |
| R4 Raise overhead | 73.83 % (min gap 0.24 mm, the lobe 0.26 mm INSIDE) | **74.06 %** (min gap **0.72 mm**) | design: the lobe fix |
| R2 | 24.87 mm (user's forearm cuff; ours 17.71) | 24.87 mm (ours 17.67) | step 2 -> 6; the drive parts 0.0 in both |
| R3 | 100 % | 100 % | - |
| R5 / R5-aim | 3 / 3 | 3 / 3 | - |
| R6 | 0.0 mm | 0.0 mm | step 1 -> 3 (gen-5 at step 3: 0.0) |
| R7 | FAIL (link 1a: 2 faces fail BRepCheck after tessellation) | **PASS** (link 1a repaired; 59 custom parts each one valid solid, STEP coverage complete) | design. The first v2 judge run failed R7 on coverage only: the new shim washer had no STEP. The builder now exports it, and the rebuild's exo.glb, clips.json, workspace.json and parts_full.json are byte-identical (sha256), so only R7 was re-run |
| R8 | 242.6 g | 244.1 g | design (+1.5 g: the 6 mm igubals, the 3.8 mm horn hub, the clips, the shim) |
| R10 | NOT RUN | NOT RUN | base_slip.py handles spherical chains only |
| R11 | 0.254 kPa PASS | NOT RUN | environment (no mujoco here) |
| R16 | 72.6 % (358 poses) | 68.3 % (120 poses) = gen-5 on the same 120 | sampling (measurement) |
| R17 | PASS | NOT RUN | environment (no mujoco here) |

**6 of 19 pass (gen-5: 7).** R7 is newly PASS. R11 and R17 were not run in this container. No requirement regressed on a
measurement.

**What the numbers say.**
- The lobe fix does what it was for. The ring clears the judges' skin by 0.41 mm on every frame, and Raise overhead's
  nearest metal goes from 0.26 mm inside to 0.72 mm out (R4 +0.23).
- R1 falls 0.12 net. Comb hair loses 0.83. The lobe is an unlikely cause: it only moved 0.5 mm inward, away from the skin.
  The candidates are the drive parts that moved more. The rod line
  rose 3.6 mm and the eyes widened to 6 mm, so the pushrod and igubal heads sit 1-3.6 mm higher over K's cap. The
  crank-pin tilt went from 29.0 to 23.5 deg. The section-4 attribution found the drive TAKING Comb hair coverage
  before (88.30 without it, 87.11 with it). Attributing the 0.83 to one drive part is the next r1_swap / r1_attr step.
- The 0.62 non-drive points against the L1 sit in link 2's group (section 4). They are the next lever, not this fix's.

**Stills that would change** (not rendered; a re-shoot needs the user's yes for the GPU):
- The drive close-ups and macros, which change part sizes: kopen_drive_closeup, kopen_drive_lobe_macro,
  parts_drive_closeup, parts_drive_lobe_macro, parts_drive_lobe_side, parts_drive_lobe_side2 and parts_drive_oblique.
  They show 6 mm igubals, the taller horn hub with M1.6 x 4 screws, grooved pins with clips, the post clip and shim,
  the slimmer follower eye, and a lobe 0.5 mm smaller.
- The overhead heroes, where the lobe sits under the J2 cap: hero_overhead_chain, hero_overhead_chain_back,
  hero_overhead_back and hero_overhead_back_mid.
- The K-open views, where the pushrod line is 3.6 mm higher: kopen_chain and kopen_back.
- parts_shoulder_top, which shows the horn plate 2.6 mm higher on the K cap.
- Unchanged: rest_*, parts_knee_* and parts_four_hubs_posterior. Their parts are copied byte for byte, and the drive is
  not in their frame. hero_shelf_* changes only where the drive shows.

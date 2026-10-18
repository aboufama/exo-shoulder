# lowarm-kstop-knuckle-3r: half-ring desmo knuckle at the buildable stage-1 level, dwell held by a K-own set-screw stop

Round 15, lens B, pick 1 (cells P / C / T merged in). Model: `docs/concepts/models/lowarm-kstop-knuckle-3r.py`.
Preview: `docs/concepts/viz/concepts/lowarm-kstop-knuckle-3r.js`. Row: `docs/concepts/rows/lowarm-kstop-knuckle-3r.json`.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Check the sidedness first. Every number in this cell rests on the inner wall blocking +K. Measure it from the
     geometry, not from the docstring: rho(K) of the stage-1 pin about u2 at the dwell exit.
   - Put stop A where it is cheapest to make. It sits inside the O20 stack, so its azimuth is free. Choose the groove's
     K = 0 end so that the set screw's access bore leaves the hub wall away from the bar roots and the stage-2 boss.
   - Size the short-arm pocket from the swept crank metal over the whole stroke. The spec gives a notch box
     (r 6.3-10, floor F+1.0) taken from one frame. The pocket should come from the measured swept volume in link 1b's frame.
   - Check the pocket against the h2facet sector in the SAME frame (the judge flagged the frames as unconfirmed).
2. **The rawest material.**
   - The posed skin and the motion clips, through Bench(110,360) exact (the frozen protocol).
   - The per-pose dumps of the parent cell at F+3.9 (`docs/alignment/remeasure/lowarm-halfring-knuckle-3r_s1level3p9_A_bench_perpose.json`)
     and of the lead (`conecut-knee-knuckle-3r_bench_perpose.json`).
   - The model's own drive geometry (`_scg`, `_desmo`: PV, dR, F0, phi(K)), the crank's sample clouds and link 1b's
     transforms on every fit pose. These are used rather than the round-15 summary tables.
3. **Methods and tools.**
   - The harness `tools/alignment_lowarm_s1level.py` (the glev hook after the clamp) and the row's verifier
     `docs/concepts/verify/lowarm-halfring-knuckle-3r.py` (frozen wear, th margin, kplay correction).
   - The kplay red team's `PlayDesign`, exec'd verbatim into the same process: K = law + delta on dwell poses, J1 / J2 / J3 re-solved.
   - `tools/alignment_paired.py` for the per-pose dump and for the worst-of-two-wears combination, with +0.1 / +0.2 mm probes.
4. **What, other than me, shows the number is right.**
   - Bench(110,360) exact, worn frozen. The verifier's own checks run inside the same call (V1 fit gates, V3 th margin, V4 kplay).
   - The pose list the red team named (203, 139, 205, 237, 264, 316), read per pose at each wear, plus the delta-0 control
     against the parent's 18.65.
   - Then the independent verifier and the alignment auditor (M3 ruling, O20 ruling, flexure ruling for cell P).

## Spec correction

The catalogue's model_spec builds `P = dict(V.BEST) | LM.CELL_A | dict(a_s=9.8, psi=150, glev=2.039, kslot=46.9)`. That is
wrong. `V.BEST` is cell B (row best_params on top of `CELL_B`), and it carries `l2_lift 1.5`. `CELL_A` has no `l2_lift`
key, so the merge would silently wear cell B's lifted link 2. The model uses `CELL_A | KSTOP` with `l2_lift 0`, which is
the verified F+3.9 cell A (18.65).

## Step 0 (geometry, fast fit; `geom` mode)

| check | measured | gate |
|---|---|---|
| 3b: rho(K) of the pin about u2, K 0..2 deg at the dwell exit | 9.9035 -> 9.7830 mm (z drift +0.018), **drho/dK = -0.0606 mm/deg**, linear (1 / 0.0606 = 16.5 deg/mm, the model's 16.485) | +K pushes the pin into the INNER wall, which the half ring keeps over the dwell. Sidedness CONFIRMED. |
| stage-1 level | groove / pin band F+3.15..4.65; arm sheet at the pin end F+2.90; pivot r 16.02 about u2 | zero stage-1 metal in link 1b's plate band F+0..3.0 |
| stage-1 gates | pa pin 29.7 / cap 35.7 (gate 34.47 on the linear read; built read gates the cap side outside the blend), rc_min 1.02 (>= 1.0, RC_MIN cut passes), ridge 0.264, drift 0.291 | pass |
| slot / stroke | kslot 46.9 -> model dK_lim 46.75 (slot-end, 0.25-deg K grid); the J2 dowel at 46.35 cuts every pose needing more (applied in the wear) | stop B 46.6 |
| stop A in hub K | groove r 6.45-8.55, F_K+3.15..4.75, lug r 6.85-8.15 (0.40 radial clearance each side); groove-to-MR117-seat wall 0.95, thread-to-seat 1.20, groove-to-O20 wall 1.45; arc 57.4 deg | inside O20: no samples added, no skin-facing metal added |
| access bore | the screw axis exits the O20 wall 41.4 deg from the groove end. Around hub K (frame bx = unit(uK x [0.3,0.5,0.8])) the bar roots occupy az -89..-55 (link 1a) and -159..-129 (link 1b), and the stage-2 nose boss sits at az 39. Groove end at az 31.4 puts the exit at **az -10**: 45 deg from link 1a's root, 49 deg from the boss | >= 10 deg |
| M3, crank vs link 1b's J2 lower plate (every fit pose, K 0..46.25, in link 1b's frame, frame bx = unit(u2 x [0.3,0.5,0.8])) | 1210 crank samples fall inside r <= 10.15 and level < 3.15: az **9.9..43.1**, r 8.15..10.14, level **2.53..3.15** (3.15 = the pin's lower end; the arm sheet descends from 2.90 at the dwell to 2.53 in the rise, because the crank axis is 14.7 deg off u2) | the pocket must cover them |

**What the M3 numbers change in the spec.** The short arm's metal inside hub 2's footprint sits at az 9.9-43.1 in the
h2facet frame, not az 66-95. That puts it **65 deg clear of the facet sector (108-178)**, so the judge's notch-vs-facet
gate passes in the model's own frame.

The arm's sampled sheet is its top face. It sits 0.25 under the ring insert's underside (F+3.15) at the dwell, and the
pin protrudes from it. The sheet dips 0.37 mm over the stroke because the crank axis is 14.7 deg off u2. So the pocket's
floor and the arm's tip thickness t trade against each other:

- with the spec's floor at F+1.0 (+0.15 running gap), **t <= 2.53 - 1.15 = 1.38 mm**;
- with the spec's 1.75-1.85 mm arm, the floor goes to F+0.63..0.53, i.e. the pocket is 2.4-2.5 deep in the 3.0 plate.

A 3-wide x 1.38 Ti tip carrying the stage-1 pin is fine in bending: ~60 MPa at 20 N over a 3 mm cantilever. The build
spec is t 1.38 at the tip, with floor F+1.0 over az 6-47 and r 8.0-10.

The pocket removes link-1b plate metal on the plate's upper (non-skin) face. It adds no skin-facing metal and no samples.

## Sided hold budget (step 4; deg of K)

| corner | e+ (wall side) | e- (stop A) | 203 = 0.263 - 0.40 e+ | gates (203 >= 0.15, e- <= 0.29) |
|---|---|---|---|---|
| P5 worst statics | 0.264 | 0.210 | 0.157 | pass / pass |
| P5 RSS | 0.181 | 0.210 | 0.191 | pass / pass |
| P5 matched | 0.155 | 0.210 | 0.201 | pass / pass |
| P0 worst | 0.363 | 0.408 | 0.118 | **fail / fail** |
| P0 RSS | 0.280 | 0.408 | 0.151 | pass / fail |

So the claim stands on the stated ISO P5 J2 bearing spec. P0 fails on both sides.

## Step 0 wears (frozen exact Bench(110,360))

Protocol: the claim's own frozen protocol. The shape is fitted once on Bench(60,160) fast (stage 1 at F+3.9 through T's
glev hook) and worn unchanged on Bench(110,360) exact. On every DWELL pose K = law + delta, and J1 / J2 / J3 re-solve
(the kplay `PlayDesign`, verbatim). The J2 dowel cut at K-eq 46.35 removed 0 poses: the largest taken K is 45.615.
Outputs and dumps are in `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/kstop/`
(`wear_*.json`, `dump_*.json`, `summary_p0264_m0210.json`).

| wear | gap | reach | ib14 | ib10 | contact | 203 main / extra walls | 264 | 205 | 237 | 139 | near1 | overhead |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent cell A at F+3.9, delta 0 (s1level, kslot 46.0) | 18.65 | 0.7278 | 0.8963 | 0.5703 | 0.0106 | 0.716 / 0.263 | -1.169 | -4.28 | -9.47 | 0.072 | 20.29 | 8/28 |
| **+0.264** (wall side, P5 worst) | **18.60** | 0.7278 | 0.8968 | 0.5707 | 0.0106 | 0.610 / **0.158** | -0.999 | -4.44 | -9.39 | 0.072 | 20.78 | 8/28 |
| **-0.210** (stop A, P5) | **18.68** | 0.7278 | 0.8960 | 0.5703 | 0.0106 | 0.801 / 0.347 | -1.304 | -4.15 | -9.64 | 0.072 | 20.32 | 8/28 |
| **per-pose worst of the two** | **18.69** | 0.7278 | 0.8960 | - | 0.0106 | 0.158 | -1.304 | -4.44 | -9.64 | 0.072 | - | 8/28 |
| worst, +0.1 mm probe | 19.23 | 0.7250 | 0.8960 | - | 0.0133 | taken | | | | **flips** | | |
| worst, +0.2 mm probe | **19.77** | 0.7222 | 0.8960 | - | 0.0160 | **flips** | | | | **flips** | | |

The judge's rates reproduce. 203's c10 closes 0.105 mm over +0.264 deg (0.40 mm/deg predicted: 0.263 -> 0.157, read
0.158). 264 opens on the + side (-1.17 -> -1.00) and deepens on the - side (-1.30, 0.64 mm/deg predicted: -1.30). The
probe reading 19.77 matches the judge's ~19.73.

The 98 lost workspace poses keep the parent's / lead's attribution: fold 88 (the model's why), J3 stop 6, contact 4
(205, 237, 264, 316). 316 is the radial link-2 binder (-1.235), the same as on the lead.

### Gates

| gate | reading | verdict |
|---|---|---|
| frozen exact <= 19.05 (kill) | 18.69 per-pose worst | **pass** |
| 203 >= 0.15 at every stated corner (P5) | 0.158 worn (0.157 / 0.191 / 0.201 worst / RSS / matched) | **pass, by 0.008** |
| 203 at the +0.1 / +0.2 probes | 0.158 < 0.2 | **fails at +0.2**: the claim needs conecut-h2facet's facet (c 0.5: +0.31 -> ~0.47) |
| 139 at the probes | 0.072 < 0.1 | **fails at +0.1**: the claim needs conecut-l2jog (dl 1.0 planform: 0.487) |
| e- range <= 0.29 at P5 | 0.210 | pass (P0 0.408 fails: P5 is a stated build spec) |
| cx <= 17.0 | 16.75 (16.5 if simplicity.py leaves the set screw out as a fastener) | pass |
| M3 | no stage-1 metal in F+0..3.0; the short arm's swept metal inside r 10.15 sits at level 2.53..3.15 over az 9.9..43.1. It is clear of the plate with a pocket to F+1.0 and a 1.38 arm tip | pass as a build spec (pocket + tip thickness) |
| RC_MIN as a cut | rc_min 1.02 (a_s 9.8), 1.03 (9.9) | pass |
| bind first-fail >= 47.35 (a_s +-0.1, mu 0.12 / 0.15 / 0.17) | pin first fail 51.25 (9.8, mu 0.17), 48.11 (9.9, mu 0.17); cap side >= 58.3 | pass at every legal corner |
| a_s 9.7 corner | the pin's rho about u2 crosses the skirt pitch limit R_HI 9.94 (rho 9.904 at a_s 9.8, 0.036 under it): dK_lim 0 (s1-pitch) | **red-team flag**: the placement sits 0.036 mm inside the pitch window. It is a design-placement gate (the groove is ground to the chain), but the box edge is a cliff, not a slope |
| th >= 5 incl. play | dwell rows: min 5.389 at 229 with abs(dth/dK) 0.198 gives 5.34 at +0.264. Forced rows: 5.181 at 313 with the groove play 0.23 x 0.405 gives 5.09. PlayDesign's own J1-J3 check lost 0 dwell poses (m3e >= 17.0 in its last batch) | pass |

Note on the verifier's V3 under play: with delta != 0 every dwell pose has abs(dK) = delta > 1e-6, so V3 files it as
"forced" and reads the K sub-dyad m_sub (about 0 on rest poses; this is the lead's G4 WATCH item), not th. Its "min 0.0 /
lt5 106" is that artifact. It is not a fold, and the taken set is the same 372 poses as delta 0.


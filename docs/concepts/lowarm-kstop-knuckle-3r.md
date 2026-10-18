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

(filled from the wear runs below)

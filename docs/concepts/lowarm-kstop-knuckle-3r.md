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

P0 report corners: +0.363 reads 18.58 (203 = 0.571 / **0.118**, under 0.15) and -0.408 reads 18.71 (264 -1.43). The
per-pose worst is 18.72, with probes 19.26 / 19.81.

The + side of the dwell play IMPROVES the gap: 18.65 -> 18.60 -> 18.58, as in-band rises and 264 opens 0.64 mm/deg.
Only pose 203 limits how far the dwell can be phased toward +K. That is the lever pick 4 (lowarm-kphase-notch) prices.

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

## Held out (frozen, same shape, never searched or selected on)

| wear | gap | reach | ib14 | contact | overhead | near1 | min metal |
|---|---|---|---|---|---|---|---|
| +0.264 | 22.81 | 0.6922 | 0.8957 | 0.016 (14) | 18/71 | 25.66 | 0.33 |
| -0.210 | 22.88 | 0.6922 | 0.8950 | 0.016 (14) | 18/71 | 25.73 | 0.33 |
| **per-pose worst** | **22.876** | 0.6922 | 0.8950 | 0.016 | 18/71 | | |
| worst at the +0.1 / +0.2 probes | 22.876 / 22.876 (no held pose under 0.2 mm) | | | | | | |

The J2 dowel cut nothing on held: the largest taken K is 46.268, under 46.35.

**Paired against the lead** (conecut-knee-knuckle-3r's per-pose dumps, `tools/alignment_paired.py` compare_sets, 4000
boots). Saved in the scratchpad as `paired_vs_lead.json`.

| set | kstop | lead | diff | split | discordant poses | CI90 | P(kstop better) |
|---|---|---|---|---|---|---|---|
| bench, worst of +- | 18.686 | 18.286 | **+0.40** | in-band 0.40 | 0 takes, 0 contacts (4 shared) | [0.00, 0.58] | 0.00 |
| held, worst of +- | 22.876 | 22.379 | **+0.498** | in-band 0.50 | 0 takes, 0 contacts (14 shared) | [0.00, 0.55] | 0.00 |
| bench, +0.2 mm probe | 19.773 | 18.830 | +0.94 | 139 and 203 flip for kstop; 139 for the lead | | | |

kstop takes exactly the lead's poses and touches exactly the lead's poses, on bench and on held. The whole difference is
in-band: link 2's 440C ring insert at F+3.15..4.65 and the low crank arm sit higher over the skin than the lead's
stage. Held lands **0.002 inside the 0.5 kill line**, the borderline the lead note predicted.

Kit density was not re-measured on this row. `tools/sample_density.py` needs `mod.frozen`, which was added after the
wears. The parent cell's measured shifts on the same flagged parts (horn 2.52x, ring2 3.96x, L1a masked) are -0.06
(flagged at kit) / +0.08 (over-dense at kit) on bench and held. The lead's own kit-density held is 22.43, so the paired
held difference at kit density is ~0.38-0.52: the same borderline.

## Red team (own best config)

- **The pinch.** Pose 203 (plane 0, elev 90, axial 45), at hub 2's c10 ring, is 0.158 mm at the P5 worst wall-side
  corner, which passes the 0.15 floor by 0.008. It flips at the +0.2 probe. At P0 worst (e+ 0.363) it reads 0.118 worn (the rate predicted 0.118), so P0
  fails the gate and P5 has to be a stated build spec. Unmodelled and family-wide: the wall side is held through the crank's
  41 mm long arm. The judge's beam estimate is 27-77 N/mm, i.e. 0.14-0.55 deg of K per 0.05 N.m of K-advancing torque,
  which is 0.06-0.22 mm at 203. At that load 203 reads 0.10..-0.06 mm, a contact at the soft end. **This is the number
  most likely to be optimistic.** The arm's stiffness must be measured or modelled before a claim.
- **The pose that jams.** No taken pose needs K past 45.615 on bench or 46.268 on held. The J2 dowel at 46.35 engages
  before stop B (46.6), so stage 1 / stage 2 never carry J2 overtravel. Bind first-fail is >= 48.11 at every legal
  corner (a_s 9.8 / 9.9 x mu 0.12-0.17; cap side >= 58.3), leaving 1.8 deg over the dowel. Pressure angles: pin
  29.7-32.3 and cap 35.1-35.7 against the PA gate 33.35-36.16. The cap side is gated outside the blend on the built read,
  as in the parent.
- **A cliff in the box.** The stage-1 pin sits at rho 9.904 about u2, 0.036 mm inside the skirt's pitch limit R_HI 9.94.
  At a_s 9.7 the pitch gate trips at K = 0 (dK_lim 0, fit reach 0.34). The groove is ground to the chain, so this is a
  placement cliff, not a tolerance one. A fit must treat a_s < 9.8 as a wall.
- **Strength.** The short-arm pocket in link 1b's J2 lower plate (az 9.9-43.1, floor F+1.0) overlaps link 1b's bar
  root. The root runs az -0.7..21.6 at r 15 about u2, read from the preview's coarse link-1b export. A 2.0-deep pocket
  over ~12 deg of it removes roughly 30-35 % of the root section, against the judge's ~23 %. That is an FEA item for
  the CAD. The alternative is a 1.0-mm-thinner arm tip and a shallower pocket. Stop A's groove-to-MR117-seat wall is
  0.95 mm under 133 N per N.m of K torque, and the set screw relies on thread-lock (Loctite 243). Both are build risks,
  not bench risks.
- **Optimistic modelling choices, stated.**
  - The fit model sees kslot 46.9 (dK_lim 46.75), so its shape was fitted with poses up to 46.75. The dowel then cuts
    at 46.35 in the wears, and no taken pose exceeded it.
  - The +-delta wear moves dwell poses only. Forced poses keep the law value; their groove play (0.23) is the
    parent's / lead's T3 item.
  - Pose 139 (0.072, link 2) does not move with dwell K. It sits on a forced pose (K 30.97), so it was not worn with
    the groove play here.

## Cells merged in

- **C, adjpad (control): not run.** It is dominated by construction. The + side is the same wall-side chain, so 203 is
  identical. Its - side range is 0.273 against 0.210. It adds the 3 x 2 pad block as link-1b metal. It loads the MR63ZZ
  crank pivot at 355 N per N.m against stop A's 133 N per N.m into hub K's MR117 pair. Its cx is 17.0 (17.25 with the
  dowel charged, which is dead). The measured - side slope here (264 at 0.64 mm/deg; 18.68 at -0.210, 18.71 at -0.408)
  prices its -0.273 at ~18.69-18.70 before the pad metal.
- **P, kpreload: not run.** The ledger holds no auditor ruling on whether the cycled crank-loop preload is a flexure.
  If it is ruled one, its cx is 19.75 and it is dead.
- **T, bareti: not run.** Step 0 passed, but T needs the auditor to accept a Hertz-based RC_MIN, because its 35 N
  corner exceeds Ti first yield.
- **Combined cell (the claim): not measured.** It is kstop + conecut-h2facet (c 0.5) + conecut-l2jog (dl 1.0
  planform). Those rows have not landed. From the judge's measured rates it would read 203 ~0.47 (P5 worst) and 139
  ~0.49, so the +0.2 probe reading would equal the plain ~18.69. The facet sector (az 108-178) does not meet this row's
  pocket (az 9.9-43.1) in the same frame.

## Verdict (step 0)

**SCREENED, step 0 passes.**

| gate | reading |
|---|---|
| plain gap, per-pose worst at the P5 corners | 18.69 (<= 19.05) |
| pose 203 at P5 worst | 0.158 (>= 0.15) |
| held paired against the lead | +0.498 (inside 0.5, by 0.002) |
| cx | 16.75 |
| RC_MIN | 1.02 |
| bind first-fail | >= 48.1 |
| M3 | closed: stage 1 at F+3.9, plus the pocket and a 1.38 mm arm tip as build specs |

The sidedness that every number rests on is measured from the geometry: the inner wall blocks +K.

It is not a lead change. Against the lead it is +0.40 bench and +0.50 held, all of it in-band: the same takes and the same
contacts. Alone it fails the +0.2 mm probe (19.77, with 139 and 203 flipping), so the claim has to be the combined cell.
It is the buildable Pareto point at cx 16.75 (1.75 under the lead's 18.5) and closes the family's GAMED M3 finding.
Its risks are the 0.008 margin at 203, the unmodelled long-arm compliance (0.06-0.22 mm at 203 per 0.05 N.m), the
pocket's cut into link 1b's bar root, and the held line.

## Next (the loop)

1. The combined cell, once conecut-h2facet / conecut-l2jog report. Apply the facet (sampled as a solid) and the
   planform jog to this frozen shape, then re-wear +0.264 / -0.210 exact and read the probes.
2. The step-9 fit. Run the near-touch objective on env and select on envsel, with box a_s 9.8-10.0 (9.7 is a pitch
   cliff), psi 147-150, wall_rise 0.5-0.8, kslot 46.9-47.5, owd_margin 0-4, blend 10-20, zr 1.5-4. Use >= 2 LHS starts
   plus a sigma-0.8 restart. Wear frozen exact once, then held paired. The target is the in-band 0.40, which is the
   whole gap to the lead.
3. Pick 4 (kphase). The + phase lever is measured here: +0.363 deg of dwell K gains 0.07 and opens 264 0.64 mm/deg.
   Pose 203 is the only binder.
4. Model or measure the crank long arm's stiffness, since it decides 203 on the wall side.
5. The independent verifier and the alignment auditor: M3 closure, the stop-A O20 wall, the flexure ruling for P, and
   Hertz for T.

## Verification (independent skeptic, 2026-10-18 ~15:25 UTC)

Harness: `docs/concepts/verify/lowarm-kstop-knuckle-3r.py`. The claim's model is loaded UNCHANGED and worn through its own
frozen protocol: fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact and on the held-out set. Dwell K is
law + delta (the kplay PlayDesign), and the J2 dowel cut sits at 46.35. The verifier adds four checks:

- **V-ARM, a metal correction.** The parent samples the crank's short arm as one sheet, 1.0 mm under the pin centre
  (desmo-conecut-knuckle-3r.py line 267). The claim reads that sheet as the arm's TOP face and gives the arm a thickness
  (t <= 1.38 build spec; the gen-9 CAD has 1.5). So the arm's skin-facing underside was never sampled. V-ARM adds it at
  sheet - 1.38: the same 8 x 3 stations, crank frame, skin-checked contact list.
- **The continuity flood**, `connected()` of minarc-stop-knuckle-4r-mechanism.py, run on the post-dowel bench. The claim
  did not run it.
- **V3b, the fold margin th with a dwell flag that does not key on dK != 0.** Under play, a dwell pose carries
  dK = sp * delta exactly, so it is read with the effective J1-J3 dyad. The K sub-dyad m_sub (the lead's G4 item) is
  reported separately.
- **Per-pose worst dumps** in the alignment_paired format (the lead's rule), plus the paired comparison against the lead.

CB_EXACT=1, local, niced, <= 2 processes (the farm is closed).

| check | result |
|---|---|
| frozen exact Bench(110,360), +0.264 (wall side, P5 worst) | **18.60** reproduced bit-identically (reach 0.7278 = 262/360, ib14 0.8968, ib10 0.5707, follow 1.0, contact 0.0106 = 4); why: fold 88, contact 4, parts 0, closure 0, flip 0, skin 0; overhead 8/28 |
| frozen exact Bench(110,360), -0.210 (stop A, P5) | **18.68** reproduced (ib14 0.8960; 264 at -1.304, 203 at 0.801 / 0.347) |
| per-pose worst of the two (the claim) | **18.69** (score 93.20) reproduced. Dump: `docs/alignment/remeasure/lowarm-kstop-knuckle-3r_bench_perpose.json` (recomputes 18.69) |
| +0.1 / +0.2 mm probes (worst) | 19.23 (139 flips) / **19.77** (139 and 203 flip), reproduced. The lead reads 18.83 at +0.2 |
| V-ARM, short-arm underside at t 1.38 (24 samples, F-0.82..F+1.71 about hub 2's face) | **0 of 470 poses change** in either wear (min metal, extra-wall metal, taken, in-band all identical). Measured directly on the fit bench, the underside's lowest skin distance is 7.92 mm (sheet 9.26 mm) and it is never below the pose's other contact metal. The arm rides high over the dome beside hub 2. Correction applied, effect 0.00 |
| J2 dowel at K-eq 46.35 | cuts 0 (largest taken K 45.615) |
| continuity flood (+0.264 wear) | connected_full **18.60 (0 dropped)**; envelope 1065 ok / 526 forced, all connected; kNN 20.29 (6 forced dropped, the family's known kNN reading: parent 19.64); bench-only 50.45 (the known sparse-bench artefact, 18 of the 113 drops have no taken neighbour) |
| V1 own gates | desmo_fail empty; dK_lim 46.75 (slot end); stage-1 built pin first fail 52.33 / cap 59.74 (>= 47.35); rc_min 1.02; ridge 0.264; PA pin 29.7 / cap 35.7 (gate 34.47; the cap side is gated outside the blend on the built read, as in the parent) |
| near-touch (reported only) | min metal 0.07 (139, link 2); 0.16 (203); gap at 1 mm 20.78 / 20.32, at 2 mm 34.84 |
| complexity | the row's mechanism record lacked docs/SIMPLICITY.md's count fields, so tools/simplicity.py read **0**. The verifier merged the parent's record + 1 bought part (the M1.6 set screw): simplicity.py now reads **16.75**, which matches the claim |
| paired vs the lead (alignment_paired compare, 4000 boots) | bench **+0.3998** (18.686 vs 18.286), held **+0.4977** (22.876 vs 22.379), pooled +0.46. All of it is in-band (the lead's held ib14 is 0.89999, so every in-band point counts), with 0 discordant takes and 0 discordant contacts (4 / 14 shared). CI90 [0.00, 0.58] / [0.00, 0.55], **P(better) 0.00** on both. File: `docs/alignment/remeasure/lowarm-kstop-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json` |

### Findings

1. **The number stands.** The frozen exact bench reproduces 18.69 bit-identically. The only metal the claim left out (the
   short arm's underside) sits >= 7.9 mm from the skin and changes 0 poses. The flood drops 0 poses and the dowel cuts 0.
   Exactly 3 ACTIVE DOF: J1, J2 and J3 on O20 v5 hubs. K is a passive rotation, slaved by the two-stage desmo drive in
   the rise. In the dwell it is held between two pieces of metal that exist: the half ring's inner wall blocks +K
   (drho/dK = -0.0606 mm/deg, so +K presses that wall) and stop A, K's own lug in link 1b's groove, blocks -K. That
   leaves no undetermined passive coordinate. The crank pivot and the two knee pins are closure-determined rotations
   (MR63ZZ pairs). There are 0 passive translations and no gear, pulley, cable or spring. Every stop acts on its own
   joint's angle: stop A / B on K, the dowel on J2 (re-phased to the J2 angle at K-eq 46.35), the J3 dowel on J3.
2. **Ranked at the probe (the round-15 rule), this cell alone is 19.77, not 18.69.** 203 = 0.158 < 0.2 and
   139 = 0.072 < 0.1 both flip. That is 0.94 behind the lead's probe reading (18.83). The rule "203 >= 0.15 at every
   corner and at the +0.1 / +0.2 probes" FAILS at the +0.2 probe here, and at the P0 corner (203 0.118, e- 0.408 > 0.29).
   The claim says this itself and relies on the P5 J2 pair as a stated build spec, plus the combined cell with h2facet /
   l2jog. Both of those have landed since. h2facet's verified buildable config is the chamfer alone (its upper flat was
   mis-framed). l2jog reads 139 at 0.602. **The combined cell is unmeasured. It is not this verification.**
3. **Held is at the kill line, not inside it with room to spare.** The paired held difference is +0.4977 against a 0.5
   line, P(better) 0. The +0.5 includes no tolerance: kit density was not re-measured on this row (the parent's shifts
   are -0.06 / +0.08), and the claim's own red team puts the unmodelled long-arm compliance at 0.06-0.22 mm at 203 per
   0.05 N.m. Either can push held over the line, or 203 into contact (+0.54).
4. **Instrument notes (no number moves).**
   - The wear JSON's `play_info` (n_dwell 31, n_dwell_lost_fold 0, m3e_min) is the LAST IK BATCH only, because
     PlayDesign overwrites PLAY["info"] on every `_ik_phys` call. The real dwell count is 205 of the 372 taken (V3 at
     delta 0 files 167 as forced). What shows no dwell pose was lost under play is the unchanged taken count (372 at
     +0.264, at -0.210 and at 0).
   - Besides V3, the verifier's V4 kplay also misfiles under play. It reads 60.76 with 108 poses dropped, because the
     dwell poses carry dK = delta, so they are filed as forced and m_sub ~ 0 minus 0.23 is read as a fold. Nobody
     should quote that 60.76. V3b gives the true dwell th margin (below).
   - The row's mechanism record could not be scored (tools/simplicity.py read 0). It is fixed by merging.
5. **Build notes for the CAD (inside O20, no bench effect).**
   - The M1.6 stop-A set screw, centred on the 1.6-tall groove (F_K+3.15..4.75), has zero thread wall to link 1b's boss
     underside (U0 = F_K+3.15). Raise the bore to centre >= F_K+4.45 (0.5 wall), pocket the groove's K = 0 end to
     F_K+5.25 and run the lug to F_K+4.9. The flat point (O0.8) then bears at F_K+4.05..4.85. The thread stays 1.2 off
     the MR117 seat (r 6.7..8.3 vs 5.5).
   - The short arm needs the claim's t <= 1.38 tip, or the gen-9 CAD's 1.5 with the pocket floor at F+0.88. Either way
     the underside stays >= 7.9 mm off the skin (V-ARM).

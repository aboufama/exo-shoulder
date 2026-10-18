# Round 15 (main, re-launch) ideation: judge and red team (2026-10-18 ~13:30 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). Every candidate here is already past that line.
The real target is gap 0, and 95 (gap 13.75) at low complexity. The plan is docs/concepts/ROUNDS.md "Round 15 plan,
re-dispatch" (09:25) as amended by "Round 15 plan, re-launch" (12:25, 919906f). This loop runs lenses B
(lowarm-adjpad-buildable) and C (conecut-sidestep-metal) only. Lens A (take-bound-3dof) is a separate lead agent; its
table and the 12:50 blocker message are on file.

**Lead to beat:** conecut-knee-knuckle-3r, verified 18.28 (score 93.35), frozen exact Bench(110,360). Held 22.38 (22.43
at kit density). cx 18.5, 3 joints, 0 passive translations, WATCH. At the +0.2 mm probe the lead reads **18.83**: one
pose flips, 139 (link 2 at 0.072 mm).

**Candidates:** six came in.

- Lens B: lowarm-kstop-knuckle-3r, lowarm-kpreload-knuckle-3r, lowarm-adjpad-knuckle-3r.
- Lens C: lowarm-kphase-notch-knuckle-3r, conecut-l2jog-knuckle-3r, conecut-h2facet-knuckle-3r.
- The planner's fourth B idea, lowarm-kstop-bareti-knuckle-3r, came in as a cell of kstop, not as a row.

Every joint maps to a real part (MR117 / MR63ZZ pairs, ISO 8734 dowels, an ISO 4026 set screw, 440C pins). Every row has
3 active joints and 0 passive translations. None has an undetermined passive coordinate: K is slaved and held on both
sides in the dwell, the crank is set by its loop, and the knee pins sit outside the count.

**Outcome: FOUR picks.**

1. lowarm-kstop-knuckle-3r. kpreload is merged in as its conditional cell P, adjpad as its control cell C, and bareti as
   cell T.
2. conecut-h2facet-knuckle-3r, with its 203 numbers corrected down by the judge.
3. conecut-l2jog-knuckle-3r, with its direction corrected to the bar's planform by the judge.
4. lowarm-kphase-notch-knuckle-3r. It runs only after pick 1's step 0 passes.

No candidate is killed outright. Two merge into pick 1 as cells, because they share its metal.

**The judge's three findings:**

- **The sided-hold correction holds (pick 1, proposer).** The half-ring model's own docstring confirms it: "held at
  phi = 0 by the inner wall (phi > 0) and an own-angle STOP PAD ... (phi < 0)". The kplay code confirms it too (K = law
  + sp * delta, the rise is +). So the verifier's symmetric +-0.912 wear put the pad's play on the side the wall blocks.
  Pose 203 closes only with the wall-side tolerance chain (e+).
- **h2facet's 203 numbers are optimistic by 0.08-0.25 mm (sampling).** The proposer moved the existing ring and disc
  samples inward. The chamfer's top edge, on the unchanged O20 wall at z = c, was left unsampled. Sampled densely as a
  solid, the edge is the new binder:

  | chamfer | claimed 203 | judge 203 | judge 205 |
  |---|---|---|---|
  | c 0.5 | 0.654 | **0.571** | -4.13 |
  | c 1.0 | 1.045 | **0.878** | -4.00 |
  | c 1.5 | 1.436 | **1.185** | -3.87 |

  The gain is 0.62 mm per mm, which is the binder's axial gradient, not 0.78. It still clears the pre-registered 0.35.
- **l2jog's direction is not a planform move.** The tangent-to-GH gradient it uses splits in the bar's frame into:
  - 0.64 along the bar's axis: samples slide along a bar that does not move, an artifact worth 22 % of the first-order
    gain;
  - 0.21 out of the plate: a through-thickness bend, i.e. a local lift, 29 %;
  - 0.74 across the width, the real planform part, 48 %.

  The planform-only jog reads 139 = 0.383 / 0.487 / 0.594 / 0.716 at dl 0.75 / 1.0 / 1.25 / 1.5, against the claimed
  0.513 at dl 0.75. The lever survives at dl ~0.85-1.0.

## 1. Red-team checks made by the judge

Scripts and outputs are in
`/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge15/`: `jogplane.py` and
`chamfer_edge.py`. They ran exact on Bench(110,360) (CB_EXACT=1), nice 10, OMP_NUM_THREADS=1, one process. They read
the lead's per-part sample dump `lc/lead4.npz`, written by the lens-C proposer from the lead's frozen fit. Reproduction
checks: c10 at 203 = 0.263 and at 205 = -4.28, and the claimed jog at dl 0.75 = 0.513, all matching the proposer.

Raw data read:

- docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json (the lead);
- lowarm-halfring-knuckle-3r_s1level3p9_A_bench_perpose.json (cell A at F+3.9);
- lowarm-halfring-knuckle-3r_kplay_perpose_A.json (+-0.912);
- the proposers' logs in `scratchpad/lc/` (jog139, phase_lowA / phase_lead, beta_lowA / beta_lead, cfg1 / cfg2, lead4 /
  lowA4).

### 1.1 Guard and contact poses, per-pose dumps (min_mm main / cmin extra walls)

| pose | lead | cell A F+3.9 | A +0.912 | A -0.912 | binder |
|---|---|---|---|---|---|
| 139 (-60, 60, 105) | 0.072 / 1.70 | 0.072 / 1.70 | 0.072 | 0.072 | link 2, sample 13 |
| 203 (0, 90, 45) | 0.716 / **0.263** | 0.716 / 0.263 | **-0.102** | 1.083 / 0.626 | hub 2: c10 ring 0.263, r:hub2 disc 0.716 |
| 205 (0, 105, 15) | -4.28 | -4.28 | -4.82 | -3.73 | hub 2, c10 |
| 237 (15, 165, -60) | -8.93 | -9.47 | -9.50 | -10.22 | crank / horn |
| 264 (30, 165, -60) | -5.80 | **-1.17** | -0.58 | -1.75 | lead: horn lug; A: hub-K / horn c32 -1.17, crank -1.02, horn -0.69, plates -0.37 / -0.31, hub 2 c12 -0.13 / c13 -0.02, ring2 -0.12 / -0.08 |
| 316 (60, 150, -105) | -1.235 / 0.672 | same | same | same | link 2, a radial binder (g_rad 0.95) |

What this reads:

- **203 rates.** c10 closes at 0.40 mm per deg of +K, linearly (the crown-edge reads at +0.292 / +0.638 are 0.146 /
  0.008). The r:hub2 disc closes at 0.90 mm per deg. The two meet at +0.91 deg, so c10 governs for every e+ < 0.9 and
  kstop's table (203 = 0.263 - 0.40 e+) stands.
- **139 does not move with dwell K.** It reads 0.072 at +-0.912 and 0.
- **264 deepens on the - side at 0.64 mm per deg.** It goes -1.17 -> -1.75 at -0.912. This matters for pick 4: kstop's
  e- of 0.21 costs 264 about 0.13 mm.
- **- side cost.** -0.912 reads 18.35 against 18.28 (+0.07), and -0.638 reads 18.32. So kstop's -0.21 costs about
  +0.015, as claimed.

### 1.2 Pick 1's sidedness

The model's own text: "In the dwell the crank is held at phi = 0 by the inner wall (phi > 0) and an own-angle STOP PAD on
link 1b under the crank arm (phi < 0)" (lowarm-halfring-knuckle-3r.py lines 8-9). The kplay script wears
`dK = sp * radians(delta)` (lines 32-35), and the model turns link 1a by sp * K with the rise kp >= 0
(desmo-conecut-knuckle-3r.py line 398). So +delta is the rise, and the wall blocks it. The round-14 red team (+-0.638)
and the verifier (+-0.912) wore the pad's play symmetrically. Their 203 contact at +0.912 is on the wall's side, where
no pad play exists.

The proposer's sided budget (e+ = statics + 0.5 (Kea + conc) 16.485 + slot) gives 203:

| corner | 203 (mm) |
|---|---|
| P5, worst statics | 0.157 |
| P5, RSS | 0.191 |
| P5, ground to the chain | 0.201 |
| P0, worst | 0.118 |
| P0, RSS | 0.151 |

The judge re-derived these from the rates above and they reproduce.

At the **+0.2 mm probe**, kstop alone flips 203 (0.157 < 0.2) and 139 (0.072). Its probe reading is then about 18.65 +
0.54 + 0.54 = **19.73**, against the lead's 18.83. Picks 2 and 3 remove both flips:

- With the honest chamfer at c 0.5 (+0.31), 203 reads ~0.47 at P5 worst and ~0.43 at P0 worst.
- With the planform jog at dl 1.0, 139 reads 0.487.

So picks 1 + 2 + 3 together read their plain number at the probe.

### 1.3 Pick 2's chamfer, sampled as a solid

`chamfer_edge.py` samples the chamfered hub-2 solid densely over the +-35 deg sector at 203's binder azimuth. That means
the 45-deg face (11 rows), the unchanged wall above it up to z 4 (15 rows) and the bottom disc (21 rows), each 71
azimuths. The min sits at the chamfer's top edge (r 10, z = c) every time:

| c (mm) | 203 claimed | 203 judge | 205 claimed | 205 judge |
|---|---|---|---|---|
| 0 | 0.263 | 0.264 | -4.28 | -4.29 |
| 0.5 | 0.654 | **0.571** | -3.82 | **-4.13** |
| 1.0 | 1.045 | **0.878** | -3.61 | **-4.00** |
| 1.5 | 1.436 | **1.185** | -3.61 | **-3.87** |

The hub's wall between c10 (z 0) and c11 (z ~4) carries no ring samples. The proposer's patch moved c10 inward to
r 10 - c but left the new edge unsampled. The model must sample the facet as a solid: the face plus the edge ring at kit
density, the same rule in sd_cyl. The same caveat applies to the 264 upper flat's sector edges.

**Sector check.** In a frame bx = unit(u2 x [0.3, 0.5, 0.8]):

- 203's binder sits at az 142.8 (sector 108-178 at hw 35);
- 205's at 165-177;
- 264's hub-2 binders (c12 / c13) at 120.3;
- 316's at 221.6.

kstop's short-arm plate notch is specified at az 66-95 in "the desmo bx frame". If the frames agree, the two are 13 deg
apart, but the agreement is unconfirmed. In the notch sector the plate is only 1.0 mm thick (floor F+1.0), so a chamfer
of 1.0 there would open the pocket to the skin. This is a step-0 gate on B's chain.

### 1.4 Pick 3's jog direction

`jogplane.py` takes the binder's gradient at 139 (g = [0.089, 0.671, 0.736], g_rad 0.774, tangential 0.633, reproduced).
It runs a PCA of the 26 link-2 samples within 8 mm (singular values 19.8 / 10.7 / 2.0: axis / width / plate normal).
The claimed lat splits into:

- **along the bar axis -0.639.** A bar segment shifted along its own length is the same bar; the samples only slide.
  Gain share 0.139 / 0.633 = 22 %.
- **across the width -0.739.** The real planform part, 0.307 / 0.633 = 48 %.
- **plate normal -0.211.** A through-thickness bend, i.e. a local lift, against the row's "no lift" claim. Gain share
  0.186 / 0.633 = 29 %.

Measured exact at 139 with Lf 20 and T 10 (the row's own geometry):

| dl (mm) | claimed direction | planform only (bar width) |
|---|---|---|
| 0.75 | 0.513 | **0.383** |
| 1.0 | 0.671 | **0.487** |
| 1.25 | 0.820 | **0.594** |
| 1.5 | 0.952 | **0.716** |

316 / 203 / 205 / 264 / 237 do not change (-1.235 / 4.148 / 4.369 / 9.814 / 11.594 on link 2). The pre-registered plain
>= 0.4 at 139 needs a planform dl of about 0.85 mm. The direction is fixed to the bar's width direction (+-10 deg in the
plane only) and the dl box goes to 1.6.

### 1.5 Pick 4's lever

The proposer's logs reproduce the claimed table:

- **Rigid phase proxy** (phase_lowA, link-1a parts): 264 reads -1.15 / -0.51 / +0.60 / +1.58 at dAz 0 / 10 / 20 / 27
  (rclip 19).
- **Model re-synthesis** (beta_lowA): at beta -155 / -150 the PLATE-hubK gate gives dK_lim 0 (fit reach 0.34). The notch
  is what makes the phase legal.
- **No-notch cells** (cfg1 / cfg2, beta -168 .. -160): dK_lim 41.75-45.5 with 264 still in contact.
- **The lead chain** (beta_lead: -155 dK_lim 32.5, fit 17.5; -150 29.0, fit 21.38): dead, as the proposer says.

The judge adds five gates:

- **(a) The notch against stop A.** The notch sits at r 7.8-8.0, inside stop A's groove (r 6.45-8.55, F_K+3.0..4.75) and
  the M1.6 thread (r 7.5). If the slot plate's axial band +-0.5 meets the groove band at an overlapping azimuth, the
  notch breaks into the groove, and the stop is not buildable.
- **(b) 264 must clear at the - corner.** It needs >= 0.2 + 0.13 mm at nominal on every 264 binder: the probe plus kstop's
  e- of 0.21 at 0.64 mm per deg. The hub-2 / ring2 flats must be modelled as solids (section 1.3).
- **(c) Stroke.** dK_lim must stay >= 45.6, or the J2 dowel is re-phased under it and each lost pose is counted (+0.28).
  Prefer beta -160 (pa_eff_horn 40.9) over -155 (42.6 against the 43 cap, which the mu 0.17 column can cut).
- **(d) Wall.** It must stay >= 2.0 over the MR117 OD 11 after both cuts (the notch and the stop-A groove).
- **(e) The auditor's reading of "Keep O20 only".** A 2.0-2.2 mm sector cut is the deepest hub trim yet. The precedent
  is trimlug-k165, whose lug trims inside O20 sat at 0 cx (WATCH). The cut must read as a feature of the O20 housing,
  not a slim hub.

## 2. Verdicts

| candidate | verdict | reason |
|---|---|---|
| lowarm-kstop-knuckle-3r | **PICK 1** (cells P, C, T merged in) | The only buildable low-cx point at the lead's reach (cx 16.75 against 18.5). Stage 1 at F+3.9 with the short-arm notch closes M3. The sided hold is confirmed (1.2). It gates pick 4. Risk: held (cell A 22.64 + the F+3.9 layer ~ +0.3 gives ~22.9-23.0 against 22.38, at the 0.5 kill line). |
| conecut-h2facet-knuckle-3r | **PICK 2** (numbers corrected) | A 0-cx enabler on both chains. Honest 203 is +0.31 at c 0.5 and +0.62 at c 1.0. That takes kstop's 203 from 0.157 / 0.118 (P5 / P0 worst) to ~0.47 / ~0.43, so it survives the +0.2 probe and P0 on the + side. It also clears 264's hub-2 residuals for pick 4. It earns no take on the lead's plain gap, so it is never a lead claim alone: it is applied as a cell on B's chain, with the lead's T5 reported. |
| conecut-l2jog-knuckle-3r | **PICK 3** (direction corrected) | A 0-cx probe hardener. With a planform dl ~0.85-1.0 it takes 139 to >= 0.4, so the lead's probe reading goes 18.83 -> ~18.28. Cell A has the same link-2 binder (0.072, unchanged under K play), so it also clears kstop's 139 flip. No plain take. |
| lowarm-kphase-notch-knuckle-3r | **PICK 4** (conditional) | The only plain-gap lead-change lever this round: 264 contact -> take, -0.54, so B's 18.65 -> ~18.11 sampled (~17.8 at kit density). It runs only after pick 1's step 0 passes and pick 2's flat lands. Lowest confidence (gates a-e). |
| lowarm-kpreload-knuckle-3r | **MERGED into pick 1 as cell P** (conditional) | Its metal is identical to kstop's; only an assembly and grind spec differs. The judge's read for the auditor: the crank arm's 3-42 um preload engages and releases on EVERY dwell entry and exit (the rise leaves stop A). It is a cycled elastic element, which is what simplicity.py's spring / flexure weight prices (fatigue, hysteresis). That is unlike the v5 DB bearing preload, which is static, so +3 is likely: 19.75 > 18.5, dead. The 203 robustness it buys comes at 0 cx from pick 2 (203 ~0.43 at P0 worst). It is run only on an auditor ruling that it is not a flexure. Its own wear-out (3 um margin) falls back to cell kstop. |
| lowarm-adjpad-knuckle-3r | **MERGED into pick 1 as cell C** (control, step 0 only, <= 15 min) | Same metal minus stop A plus the eccentric pad. Its corrected prediction (203 set by the wall-side chain, the same as kstop) is right by 1.2. It is dominated on every axis: - side range 0.273 against 0.210 (P5) and 0.471 against 0.408 (P0); stop load 355 against 133 N per N.m; cx 17.0 against 16.75 (17.25 with the J2 dowel charged, dead). Buildability flag: 355 N per N.m through the MR63ZZ crank-pivot pair (C0 ~0.08 kN each) reaches C0 at ~0.23 N.m of K torque on one bearing, ~0.45 N.m shared. |
| (lowarm-kstop-bareti-knuckle-3r) | cell T of pick 1 | Only after kstop's step 0 passes. It needs the auditor's acceptance of a Hertz-based RC_MIN; its 35 N corner exceeds Ti first yield. |

## 3. Ranking

The plan's rule is (expected gap reduction vs the champion 75.94) x confidence x buildability. All four sit ~57.3-57.8
points under the champion, have 0 passive translations and 3 active joints. Read literally, the product ranks the two
lead-chain moves first, only because they inherit the lead's 18.28. The order below is by marginal value over the lead,
with claims ranked at the +0.2 mm probe as the round requires:

| rank | id | plain expected | probe expected | marginal vs the lead | confidence | cx | why this rank |
|---|---|---|---|---|---|---|---|
| 1 | lowarm-kstop-knuckle-3r | 18.65 sampled (~18.3-18.4 at kit density) | 19.73 alone / 18.65 with picks 2 + 3 | +0.37 plain at -1.75 cx (Pareto point) | 0.45 | 16.75 | It gates pick 4, it is the only buildable low-cx point, and it closes the GAMED M3 family finding. |
| 2 | conecut-h2facet-knuckle-3r | 18.28 (lead) | 18.83 alone on the lead (139 still flips) | 0 plain on the lead; +0.31 mm at 203 on both chains | 0.85 | +0 | Highest confidence; it removes pick 1's main step-0 risk and pick 4's hub-2 residual. |
| 3 | conecut-l2jog-knuckle-3r | 18.28 +-0.02 | ~18.28 | -0.55 at the probe | 0.7 | +0 | It hardens the lead's T1 / probe reading and pick 1's. |
| 4 | lowarm-kphase-notch-knuckle-3r | ~18.11 sampled (~17.8 kit) | ~18.11 with picks 2 + 3 | -0.17 vs the lead at kit density | 0.2 (joint) | 16.75 | The one lead-change path; conditional on pick 1 and gates a-e. |

The literal product, reported for the record:

| id | product |
|---|---|
| h2facet | 57.66 x 0.85 = 49.0 |
| l2jog | 57.66 x 0.7 = 40.4 |
| kstop | 57.29 x 0.45 = 25.8 |
| kphase | 57.83 x 0.2 = 11.6 |

## 4. Run order and gates (for the screen)

- **Pick 1 and pick 2/3 run in parallel** (2 slots, each <= 2 niced processes).
- **kstop step 0, <= 30 min** (the model_spec in the catalogue):
  - Print rho(K) at the dwell exit, to confirm that the inner wall blocks +K.
  - Wear at +0.264 / -0.210 (gate) and +0.363 / -0.408 (report), per-pose worst.
  - Read 203, 139, 205, 237, 264 and 316.
  - M3 with the short arm; RC_MIN as a cut; kit density.
  - **Kill:** frozen exact > 19.05; 203 < 0.15 at a stated corner; cx > 17.0; any M3 overlap.
  - Cell C (adjpad) is one extra wear (<= 15 min). Cell P waits for the auditor. Cell T comes after step 0.
- **Pick 2:**
  - Sample the facet as a solid (section 1.3); size on envsel to >= 0.35 at 203.
  - Hand the 203-vs-c table and the 264 flat table to pick 1 and pick 4.
  - Check the sector against kstop's plate notch (1.0 mm floor) in the model's own frame.
- **Pick 3:**
  - Planform-only direction, dl 0.75-1.6; pre-registered >= 0.4 at 139 plain.
  - Check envsel and held for a pose binding on the jog's other side.
- **Pick 4:** only after pick 1's step 0 passes. Gates a-e of section 1.5 come first; then the fit.
- **The combined claim** is kstop + the 203 facet + the 139 jog, then + kphase if it passes. It is ONE row,
  pre-registered:
  - frozen exact <= 18.65 (<= 18.28 for a lead change) at the +0.2 probe, cx <= 17.0;
  - held paired within 0.5 of the lead (P(better) reported);
  - 203 >= 0.15 at every stated corner.
- **Never search, select or tune on held out.** The near-touch objective runs on env, selection on envsel, and the claim
  on frozen exact Bench(110,360) once.

## 5. What happens next

If pick 1's step 0 passes and pick 4's gates hold, the combined row is the round's lead-change candidate. It goes to an
independent verifier, then the alignment auditor (the flexure and O20 rulings are on its list), then the
generation-winner L2 CAD. If pick 1 dies on held out, the lowarm family closes at the buildable level. The 3-DOF ceiling
(lens A, 12:50 blocker) then stands as the round's finding, and the loop moves to whatever the user picks from the
blocker's options. Picks 2 and 3 still harden the lead.

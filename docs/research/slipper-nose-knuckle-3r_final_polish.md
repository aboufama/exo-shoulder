# slipper-nose-knuckle-3r final polish on the envelope bench (2026-10-17): no pick replaces the verified config; the pre-registered pick's held-out gain is +0.38 priced and -0.59 unpriced

Self-measured. The verified lead (round-10 winner: frozen exact Bench(110,360) 18.49, score 93.28; held out 23.45) was
polished on the representative envelope bench `env` on the CPU farm and claimed through the verifier's own harness
(`docs/concepts/verify/slipper-nose-knuckle-3r.py`, imported unchanged). The tool is `tools/slipper_env_polish.py`
(new; adapted from `tools/roller_env_polish.py`, the same family's polish).

**Verdict: the verified config stays the CAD config. No verifier run is due.**

* **The single pick was pre-registered before any claim number existed** (commit e95a8aa,
  `slipper_env_polish/picks/prereg.json`). The rule: the highest-ranked envsel pick whose flank passes the
  synthesis-robustness check. That is pick1 (`snp-w3-g11-5`), the only one of the three picks that passes 6 / 6.
* **pick1 against the verified config, same protocol, same reading:**

  | protocol | priced (margin 5.5, smlo +0.5, stop B at bk1 + bk2 - 5.5) | unpriced (margin 5, nominal stops = the lead's reading) |
  |---|---|---|
  | held out, CAD shape (fit Bench(60,160) -> held out exact) | 24.63 -> 24.25, **+0.38** (paired CI [-0.59, +1.48], P better 0.70) | 23.45 -> 24.04, **-0.59** (P better 0.22) |
  | verified protocol (fit Bench(60,160) -> Bench(110,360) exact) | 19.05 -> 19.44, **-0.39** | 18.49 -> 19.44, **-0.95** |
  | held out, env fit (fit env fast -> held out exact) | 89.11 -> 24.44 (+64.7, an artifact: see below) | 89.00 -> 24.23 (artifact) |

* **The held-out gain over the verified config is +0.38 priced and -0.59 unpriced.** Both are under the 1-point rule,
  and they have opposite signs. The priced gain exists only because pick1's stops sit further from the fold (its own
  min th margin is 5.7, the verified config's 5.18 / 5.006), so the 5.5 reading costs pick1 0.21 held out and the
  verified config 1.18. Read at the user's 5-deg rule, the verified config wins on both benches.
* **The envelope bench showed under 1 point of headroom for the CAD shape**, and the claim confirms it:
  * The best of 250 honest CMA rows wears the Bench(60,160)-fit shape on env at 23.42 (1 mm), against the verified
    config's 24.65: 1.2 points, selected in-sample on that same draw.
  * The three picks read 24.38-25.58 there.
  * So I stopped after one CMA batch (3 runs, 379 tries) and did not buy a second one.
* **New red-team finding: the verified flank sits 0.02 in g, and 0.2 mm in r_c, from a drive that cannot leave rest.**
  * On the verified config, a step of g -0.02, r_c -0.2 mm or beta -1 deg drives the crank pressure angle over its
    38.03-deg cap (43 - atan(0.087)). The synthesis then ends the drive range at dK = 0, and the fit bench reads 86
    instead of 14.25.
  * Fitting the shape on env instead of Bench(60,160) does the same: crank PA 38.0 at rest, drive range 0, K never
    moves. That shape reads 88.3 on env and 89.1 held out (follow 0.64, 453 poses fail the pressure check).
  * pick1's flank is robust (crank PA 11.7 deg; all 6 tolerance neighbours keep their stroke). pick1 is NOT better
    held out, though. If the CAD wants a tolerance margin on the crank side, pick1's flank values are a reference, as
    the roller polish's pick3 was. A flank-only change needs its own check.
* **Hard goal** (held out <= 22.0): not met. The best held-out reading of any claimed config is 24.03 priced (pick2,
  report only) and 23.45 unpriced (the verified config itself).

Cost: CMA + re-score batch $0.1225 (cpu3c) / $0.1429 (cpu5c); claim batch $0.1788 / $0.2086. **Total $0.30 / $0.35
against the $0.30 budget**, plus cold starts. The cpu5c worst case runs $0.05 over; the claim batch billed more than
planned (pick2's env-fit held-out claim took 936 s). Balance after: $24.69, above the $24.40 line. Local work used at
most 2 processes: 6 fit60 claims, the reproduction, the robustness checks. Wall time about 55 min.

## 1. The search bench: `env`, reused (step 1)

The fast caches `env-72d21f5aa2e5-env` and `env-fc171830d1d7-envsel` live on the farm volume and were linked per job
(`tools/env_bench.py use`). A local rebuild was started as insurance and stopped once the farm claim batch made it
unnecessary. The draw is frozen in `docs/research/minarc_final_polish/env_poses.npz`:
* the 110 clip frames of Bench(110,360) (never Wave / Walking);
* 420 fresh workspace poses (`env`, the search bench);
* an independent 360-pose draw (`envsel`, the pick-selection bench).

Each draw is stratified on the grid's elevation x plane x signed-axial shares, and no pose lies within 2 deg of a
held-out pose. The table was re-printed today (`python3 tools/env_bench.py table`, saved to
`slipper_env_polish/env_table.json`):

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| **Bench(60,160) ws (the fit bench)** | 160 | **2.5 %** | 28.1 % | 7.5 % | 16.9 % | 6.3 % | 36.3 % | 23.8 % | 26.9 % | -26.1 |
| **env** ws | 420 | **9.3 %** | 23.1 % | 7.1 % | 17.1 % | 6.0 % | 35.7 % | 24.0 % | 27.4 % | -34.0 |
| **envsel** ws | 360 | **9.7 %** | 22.8 % | 7.2 % | 16.9 % | 6.9 % | 36.1 % | 23.6 % | 26.7 % | -33.4 |

Closest fresh pose to any held-out pose: env 2.23 deg (coordinates) / 2.04 deg (humerus orientation), envsel 2.07 /
2.03 deg; median 7.5 / 7.3 deg.

## 2. The tool: `tools/slipper_env_polish.py`

It keeps the family's objective, guards and continuity, retargeted at `SNModel` through the slipper verifier:
* a = the priced config fit on env FAST, scored in-sample;
* b = the same config fit on Bench(60,160) FAST, worn FROZEN on env;
* obj = (a + b) / 2 at the 1 mm near-touch gap, with the continuity knock-out (the full-grid flood plus every fresh env
  pose joined to the connected grid by a 2-deg slerp edge to one of its 6 nearest connected nodes).

The guards: the claim-fit guard max(0, g60 - a - 3); a depth guard 0.1 x (summed env depth over the verified config's
own); +100 for a dishonest report (drive idle, PA over the cap, knee moved) or for a taken pose whose own-state th margin
is under the reading's margin. Logged, not optimised: both shapes worn frozen on envsel.

What is new for this row:
* **Fixed, not polished:** mu 0.087 (a material property: the claim's honest friction) and nose_r 1.1839 (the verified
  nose; the verifier's N4 re-wears catalogue dowels).
* **The transmission cap is the model's own rule in both readings:** kinematic PA <= 43 - atan(mu) = 38.03 deg. Only
  the stops are priced.
* **The knee window** ang_min is free, bounded below by the verified 25.2189.
* 24 free parameters: the K dyad (bk1, bk2, a1max), the law kK, the flank (g, beta, r_c, lift), the arm (hl, zr, s_arm,
  r_lobe), the stops (smhi, smlo >= 5.0), the seats (az1, el1, az2, el2, wd, wa, b3, lc, phib) and ang_min.
* **The inband-rssr audit's three rulings are built in:**
  * `claimjobs` claims each config at both readings (`_p` priced, `_u` unpriced);
  * `prereg` fixes the single pick by a committed rule before any claim;
  * the claim reports the verified protocol and held out side by side.

**Reproduction.** `claim fit60 bench BEST` with ENVP_NOPRICE=1 CB_FOLD_MARGIN=5 gives 18.49 / near1 20.12 / near2
33.02 / depth 14.75 mm (max 9.005), the verified row to the digit (`local/claim_BEST_fit60_bench_u.json`, 170 s locally).

## 3. Re-score on env (step 2): the verified config's env fit has an idle drive

Farm job `snp-rescore` (`farm/rescore_BEST_{priced,unpriced}.json`), continuity on:

| reading | fit env fast, in-sample | fit env -> env exact | fit Bench(60,160) -> env exact | env depth, Bench(60,160) fit | min th | Bench(110,360) | held out |
|---|---|---|---|---|---|---|---|
| unpriced (margin 5) | 88.83 (1 mm 90.24), reach 0.338 | 88.76 | **21.19** (1 mm 24.07, 2 mm 41.64), reach 0.707, ib14 0.896 | 6 poses, 21.2 mm | 5.41 | 18.49 | 23.45 |
| priced (margin 5.5) | 88.37 (89.78), reach 0.338 | 88.30 | **21.19** (1 mm 24.56, 2 mm 42.17), reach 0.705 | 5 poses, 15.3 mm | 5.78 | 19.05 | 24.63 |

* **The env fit breaks the drive.** On the env-fitted shape the cam synthesis puts the crank pressure angle at the cap
  (38.0 against 38.03) at rest: dK_lim 0, why `pressure_crank`. K never moves (0 forced poses taken), reach 0.338.
  On the Bench(60,160)-fitted shape the same parameters synthesise with crank PA 29.5 and a 49.8-deg stroke.
* **So the env-fit protocol is not a fair reading of this config.** Its env-fit numbers (88-89) are a cliff of the cam
  synthesis, not the mechanism's envelope. The fair env reading is the CAD shape worn on env: **21.19**. That sits
  between the verified bench (18.49) and held out (23.45), as designed.
* Every env pose the flood reaches is connected (fresh poses 296 / 296, 155 with K forced).
* The pricing costs 0.0 plain on env but 0.49 at 1 mm, 0.56 on the verified protocol and **1.18 held out** (23.45 ->
  24.63). It is a MEASUREMENT change: the verified min th margin is 5.181 (bench) / 5.006 (held out), so a 5.5 reading
  drops poses to the fold (88 -> 90 bench, 260 -> 271 held out).

## 4. CMA on env (step 3) and the convergence gate

One farm batch (`farm/jobs_cma.json`): 3 runs from the verified config, popsize 8, 2 processes, 1500 s each, 4 jobs on
one 8-vCPU worker (the 4th was the re-score). An evaluation cost about 14-30 s (a generation of 8 took 69-119 s on 2 processes).

| run | sigma (start -> end) | tries | honest rows | x0 obj | best obj (row) | best Bench(60,160)-shape env 1 mm | best envsel 1 mm, Bench(60,160) shape | gate |
|---|---|---|---|---|---|---|---|---|
| s1 | 0.3 -> 0.23 | 129 | 88 | 57.22 | 24.11 (g7-2) | 24.05 | 28.31 | passes (0.00 / 0.00 / 0.60) |
| s2 | 0.3 -> 0.20 | 121 | 77 | 57.22 | 24.92 (g3-7) | 23.60 | 28.40 | passes (0.00 / 0.00 / 0.46) |
| w3 | 0.5 -> 0.38 | 129 | 85 | 57.22 | 24.45 (g15-6) | **23.42** | **26.99** | no (0.58 / 0.58: still moving) |
| **combined, by generation** | | 379 | 250 | | 24.11 | | | **passes** (0.00 / 0.00 / 0.54) |

* **The x0 objective (57.2) is the env-fit cliff, not a reading of the mechanism**: a = 89.8 (idle drive), b = 24.65.
  The first generation already reaches 25.3-25.9 by stepping off the cliff. So the objective's "33-point gain" is not
  headroom.
* **The headroom that matters is the CAD shape's** (term b, Bench(60,160) fit worn on env, 1 mm): verified 24.65,
  best of 250 honest rows 23.42 (w3-g14-2). That is 1.2 points, and it is the in-sample minimum of 250 noisy readings
  on the same draw. On the independent envsel draw the verified shape reads 28.89 and the best row 26.99. The picks
  read 24.38-25.58 on env and 26.99-27.84 on envsel.
* **The depth guard's reference was distorted by the same cliff.** It is the verified config's mean env depth over the
  two fits (8.03 mm), and half of that is the idle-drive shape. So every closing row paid 0.6-1.4 points of depth
  penalty. The pick rule's depth filter (envsel depth <= the verified config's 23.82 mm) is the same mean; the verified
  config's own CAD shape reads 30.0 mm on envsel, so the filter was stricter than like-for-like, not looser.
* **Caveat.** 121-129 tries per run in 24 dimensions read stagnation, not a proven optimum. w3 alone was still
  improving (0.58 over its last third). The CAD-shape headroom (under about 1.2 in-sample) did not justify a second
  batch inside the budget.

## 5. Picks and the pre-registration (committed before the claim, commit e95a8aa)

The pick rule (`picks`, unchanged from the family):
* candidates = the best 15 rows of each run by the objective (45);
* a candidate may not be deeper on envsel than the verified config (12 pass);
* ranked by the envsel 1 mm mean over the two fits;
* each pick differs from every kept pick by >= 0.5 CMA scale units.

The pre-registration (`prereg`, rule in `picks/prereg.json`): **the single CAD pick = the highest-ranked pick whose
flank passes the synthesis-robustness check** (`robust`: beta +-1 deg, r_c +-0.25 mm, g +-0.05, one at a time, priced,
on Bench(60,160); every neighbour must synthesise and keep a stroke >= the taken dK - 1). If none passes, pick1. The
other picks are report-only.

| pick | row | obj | env / env60 1 mm | envsel 1 mm mean (env fit / Bench(60,160) fit) | envsel depth (mm) | Bench(60,160) in-sample 1 mm | flank robustness |
|---|---|---|---|---|---|---|---|
| **pick1 (pre-registered)** | snp-w3-g11-5 | 25.17 | 22.89 / 25.58 | **26.83** (25.81 / 27.84) | 10.9 | 16.88 | **PASS 6 / 6** (stroke >= 41.5 at every neighbour) |
| pick2 (report only) | snp-w3-g15-2 | 25.36 | 23.67 / 25.08 | 27.25 (27.51 / 26.99) | 13.4 | 16.25 | FAIL 3 / 6: flank cusp at beta -1, r_c +0.25, g +0.05 |
| pick3 (report only) | snp-w3-g15-5 | 24.74 | 22.94 / 24.38 | 27.65 (27.84 / 27.46) | 9.4 | 16.44 | FAIL 3 / 6: crank PA cliff at g -0.05; stroke short at r_c +0.25, g +0.05 |
| verified | - | 57.22 | 89.78 / 24.65 | 61.54 (94.19 / 28.89) | 23.8 | **14.25** | FAIL 3 / 6 (section 7) |

**A warning sign before the claim:** every pick scores 2.0-2.6 points worse than the verified config on its own fit
bench (Bench(60,160) in-sample 1 mm 16.25-16.88 against 14.25). The claim confirms it on the verified protocol.

What moved (pick1 / pick2 / pick3 against the verified):

| key | verified | pick1 | pick2 | pick3 |
|---|---|---|---|---|
| bk1 / bk2 / a1max | 26.0 / 38.03 / 58.77 | 26.90 / 38.29 / **55.93** | 26.54 / 38.98 / 56.29 | 26.56 / 38.62 / 55.89 |
| kK | 2.153 | 2.389 | 2.337 | 2.351 |
| g / beta / r_c / lift | 2.393 / -176.68 / 15.37 / 0.79 | 2.396 / **-171.16** / 15.46 / 1.58 | 2.504 / -175.61 / 15.45 / 1.82 | 2.407 / -175.46 / 15.52 / 1.75 |
| hl / zr / s_arm / r_lobe | 1.94 / 4.03 / 4.00 / 8.27 | 1.17 / 3.84 / 4.00 / 8.32 | 1.65 / 4.13 / 4.12 / 7.91 | 1.42 / 4.03 / 4.07 / 8.11 |
| smhi / smlo | 16.84 / 5.00 | 15.84 / **6.07** | 15.54 / 6.09 | 17.27 / 6.39 |
| az1 / el1 / az2 / el2 | 95.39 / 67.90 / 45.82 / 41.09 | 96.63 / 67.90 / 47.02 / 41.43 | 95.51 / 68.03 / 45.21 / 42.24 | 95.25 / 67.88 / 43.96 / 42.45 |
| wd / wa / b3 / lc / phib / ang_min | 66.87 / -10.66 / 0.329 / 21.15 / -58.81 / 25.22 | 65.85 / -11.79 / 0.317 / 20.93 / -55.25 / 25.96 | 66.32 / -12.24 / 0.343 / 21.84 / -59.25 / 25.94 | 65.94 / -12.91 / 0.340 / 22.66 / -53.71 / 26.03 |

* **The common move gives away stop window for stop margin.** All three picks raise smlo from its 5.0 floor to 6.1-6.4
  and lower a1max from 58.8 to 55.9-56.3, which puts every taken pose further from the fold (min th 5.5-6.0 against
  5.18). They steepen the law (kK 2.34-2.39) and leave the dyad short (bk2 38.3-39.0).
* pick1 moves beta 5.5 deg toward -171, off the crank-PA cliff: its crank PA is 11.7 deg against 29.5.

## 6. The claim (step 4): one farm batch of 10 + 6 local claims

The farm batch (`farm/jobs_claim.json`, $0.18-0.21) ran every env-fit claim, plus the verified protocol priced for all
4 configs. The fit60 held-out claims and the unpriced verified-protocol claim of pick1 ran locally on the Bench(60,160)
fast cache (`local/`, 2 processes, about 15 min), through the same wrapper. Every claim is exact on the worn bench, has
the full-grid flood on, and writes the per-pose dump (`*_perpose.json`, the alignment_paired format).
`python3 docs/research/slipper_env_polish/summarize.py` prints the table; `paired.py` the paired bootstraps
(`paired.json`).

| config | protocol | reading | gap (flood-connected) | 1 mm / 2 mm | reach | ib14 | contact poses | depth sum / max (mm) | fold / slide | min th | dK taken / lim | PA kin crank / horn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| verified | fit60 -> Bench(110,360) | u | **18.49** (= row) | 20.12 / 33.02 | 0.7250 | 0.8955 | 2 | 14.75 / 9.01 | 88 / 9 | 5.181 | 45.6 / 49.8 | 29.5 / 35.8 |
| verified | fit60 -> Bench(110,360) | p | 19.05 | 20.69 / 34.17 | 0.7194 | 0.8955 | 2 | 14.75 / 9.01 | 90 / 9 | 5.714 | 43.7 / 49.8 | 29.5 / 34.6 |
| verified | fit60 -> held out | u | 23.45 (row; remeasure dump) | 26.54 / 36.95 | 0.6828 | 0.8943 | 10 | 46.12 / 9.05 | 260 / 32 | 5.006 | - | - |
| verified | fit60 -> held out | p | 24.63 | 27.51 / 37.34 | 0.6712 | 0.8943 | 10 | 46.12 / 9.06 | 271 / 32 | 5.529 | 44.3 / 49.8 | 29.5 / 35.0 |
| verified | env -> held out | p / u | 89.11 / 89.00 | 89.75 / 102.64 | 0.339 | 0.8870 | 5 | 12.90 / 9.86 | 666 / 30 | 6.38 / 5.41 | **0 / 0 (idle)** | 38.0 / 32.3 |
| **pick1** | fit60 -> Bench(110,360) | p | 19.44 | 21.09 / 45.24 | 0.7083 | 0.9088 | 1 | 5.42 / 5.42 | 90 / 14 | 5.705 | 43.6 / 44.5 | 11.7 / 37.5 |
| **pick1** | fit60 -> Bench(110,360) | u | 19.44 | 21.09 / 45.24 | 0.7083 | 0.9088 | 1 | 5.42 / 5.42 | 90 / 14 | 5.705 | 43.6 / 44.5 | 11.7 / 37.5 |
| **pick1** | fit60 -> held out | p | **24.25** | 27.16 / 48.31 | 0.6681 | 0.9070 | 9 | 40.48 / 8.74 | 269 / 38 | 5.716 | 43.5 / 44.5 | 11.7 / 37.5 |
| **pick1** | fit60 -> held out | u | **24.04** | 26.94 / 48.07 | 0.6702 | 0.9070 | 9 | 40.48 / 8.74 | 267 / 38 | 5.716 | 43.5 / 44.5 | 11.7 / 37.5 |
| **pick1** | env -> held out | p | 24.44 | 25.33 / 37.32 | 0.6691 | 0.8971 | 9 | 41.84 / 8.72 | 269 / 37 | 5.619 | 43.9 / 44.5 | 12.1 / 37.6 |
| **pick1** | env -> held out | u | 24.23 | 25.12 / 37.08 | 0.6712 | 0.8971 | 9 | 41.84 / 8.72 | 267 / 37 | 5.619 | 43.9 / 44.5 | 12.1 / 37.6 |
| pick2 (report only) | fit60 -> Bench(110,360) | p | 19.71 | 20.82 / 41.60 | 0.7056 | 0.9037 | 1 | 7.09 / 7.09 | 93 / 12 | 5.835 | 43.4 / 44.8 | 7.9 / 37.2 |
| pick2 | fit60 -> held out | p | 24.03 | 26.93 / 46.91 | 0.6691 | 0.9019 | 8 | 41.05 / 8.46 | 271 / 36 | 5.524 | 44.6 / 44.8 | 8.1 / 37.8 |
| pick2 | env -> held out | p | 26.34 | 26.79 / 35.05 | 0.6702 | 0.8770 | 9 | 43.59 / 8.30 | 271 / 34 | 5.524 | 44.6 / 46.0 | 7.1 / 37.2 |
| pick3 (report only) | fit60 -> Bench(110,360) | p | 21.20 | 22.31 / 33.47 | 0.7000 | 0.8935 | 2 | 11.16 / 7.28 | 90 / 16 | 6.023 | 47.2 / 48.5 | 22.1 / 37.3 |
| pick3 | fit60 -> held out | p | 24.76 | 25.87 / 39.66 | 0.6691 | 0.8916 | 7 | 41.81 / 8.59 | 266 / 42 | 5.968 | 47.4 / 48.5 | 22.1 / 37.4 |
| pick3 | env -> held out | p | 24.17 | 25.29 / 34.76 | 0.6702 | 0.8964 | 7 | 44.04 / 8.62 | 265 / 42 | 5.642 | 48.5 / 48.8 | 23.8 / 37.9 |

On every claim: the full-grid flood dropped no taken pose (connected = static); every taken pose's own-state th margin
is >= the reading's margin (5.0 / 5.5); 0 taken poses fail the verifier's pressure, closure or sense checks, except the
verified config's env-fit shape (453 pressure failures, idle drive). Low-arm extreme rotation (elev < 60,
abs(axial) >= 120): 0 contacts on every claim. The nose checks (N2 / N3) on pick1, held out: 0 undercut points;
relative-pole speed 1.57 mm/rad (verified 0.66, nearer its pole); smallest flank radius 1.92 mm against the 1.18 mm nose
(verified 1.29).

**Gain over the verified config, same protocol, same reading** (positive = better; paired bootstrap within kind, 90 % CI):

| config | held out, CAD shape (fit60), p | held out, CAD shape, u | verified protocol, p | verified protocol, u | held out, env fit, p | 2 mm, held / bench (p) | summed depth held (p) |
|---|---|---|---|---|---|---|---|
| **pick1 (pre-registered)** | **+0.38** (CI [-0.59, +1.48], P 0.70) | **-0.59** (CI [-1.64, +0.58], P 0.22) | -0.39 (P 0.36) | **-0.95** (CI [-2.44, +0.74], P 0.19) | +64.7 (artifact) | -10.97 / -11.07 | -5.6 mm |
| pick2 (report only) | +0.60 (CI [-0.32, +1.26], P 0.82) | not run | -0.66 (P 0.18) | not run | +62.8 (artifact) | -9.57 / -7.43 | -5.1 mm |
| pick3 (report only) | -0.13 (P 0.46) | not run | **-2.16** (CI [-3.62, -0.58], P 0.007) | not run | +64.9 (artifact) | -2.32 / +0.70 | -4.3 mm |

**Reading.**
* **No pick beats the verified config like-for-like on both readings.** pick1 gains 0.38 held out only at the priced
  reading, and loses 0.39-0.95 on the verified protocol at both readings. At the lead's own reading (margin 5) it is
  0.59 worse held out and 0.95 worse on the bench.
* **Where pick1's held-out change comes from** (CAD shape, priced; paired discordance): it takes 3 workspace poses the
  verified config does not, and loses 6. In-band rises (0.8943 -> 0.9070). Contact falls by one pose (overhead 6 -> 4
  contact poses, 34.3 -> 28.4 mm). Reach falls (0.6712 -> 0.6681), and the overhead class loses 2 taken poses
  (18 -> 16 of 71). That is the trade the stop move predicts: a tighter window costs reach and buys margin.
* **The 1 mm objective pushed metal into the 1-2 mm shell.** pick1's 2 mm near-touch is 11 points worse on both
  benches (33.0 -> 45.2 on the bench, 37.3 -> 48.3 held out). The 2 mm reading is report-only (user 2026-10-17), but
  it is the same pattern the sidecar and roller polishes measured.
* **The env-fit column is not a gain.** The verified config fitted on env has an idle drive (section 3). Every pick
  "gains" 63-65 points there for that reason alone. Compared shape-for-shape (each config on a fit that synthesises),
  pick1's env-fit held out 24.44 / 24.23 stands against the verified CAD shape's 24.63 / 23.45: +0.19 priced, -0.78
  unpriced.
* **The fold is untouched.** No pick moves the fold-limited classes held out: across-body 41-43 of 175 taken,
  abs(axial) >= 150 24-26 of 105, overhead 15-18 of 71. The fold is K's stroke, as on every member of the family:
  the picks' taken dK is 43.5-47.4 against the verified 44.3-45.6.

## 7. Red team

| attack | result |
|---|---|
| **Flank knife edge on the verified config** (`local/robust_BEST.json`, `local/flank_margin_BEST.json`, Bench(60,160), priced) | **It is a cliff on the crank side.** beta -1 deg, r_c -0.25 mm and g -0.05 each end the stroke at dK 0 (`pressure_crank`). The finer scan: beta -0.75 still synthesises (crank PA 36.0); r_c -0.15 mm synthesises (36.2), and r_c -0.20 mm fails (38.2 > 38.03, near1 14.25 -> 86.1); g -0.01 synthesises (34.2), and g -0.02 fails (38.5). The crank PA climbs about 2.3 deg per -0.05 mm of r_c and 4.5 deg per -0.01 of g. On the + side the verified config is robust (beta +1, r_c +0.25, g +0.05 all keep a 46.8-48.8 stroke). **The fit sample alone moves the crank PA from 29.5 to 38.0** (the env fit, section 3). The CAD's flank is cut from the Bench(60,160) fit, which works. But the margin to an immovable drive is 0.2 mm of crank radius. Before the CAD freezes the flank, a flank-only check toward pick1's beta (about -171) should measure what crank-side margin costs. |
| **The pre-registered pick's flank** | pick1 passes 6 / 6 (crank PA 11.7; its stroke stays >= 41.5 at every neighbour). Its horn side runs closer to its cap: horn PA 37.5 + 4.97 friction = 42.5 effective against 43 (the verified config: 35.0-35.8 + 4.97 = 40.0-40.8). pick2 fails 3 / 6 on flank cusps. pick3 fails 3 / 6 (crank cliff at g -0.05, short stroke at r_c +0.25 and g +0.05). |
| **Selection after the numbers** (the inband-rssr audit's ruling (ii)) | The pick was fixed by a committed rule (commit e95a8aa) before any claim ran. pick2 (+0.60 held out, priced, CAD shape) is the best held-out reading of the three, but it is report-only: it fails flank robustness, and it is still -0.66 on the verified protocol. |
| **Reading mismatch** (ruling (i)) | Every comparison above is same protocol, same reading. The pricing cost is config-dependent (verified: 0.56 bench / 1.18 held; pick1: 0.00 / 0.21), because the picks moved their stops off the fold. A priced-only claim would have shown pick1 at +0.38; the unpriced reading shows -0.59. |
| **Optimistic number** | The env-fit "+64.7" is a cam-synthesis cliff of the reference, not a gain. The CMA objective's "+33" is the same cliff. The in-sample CAD-shape headroom (1.2) is a best-of-250 on one draw; the picks realised -0.95 to +0.38 at the claim. |
| **Contact depth** | Every pick presses less in sum held out (40.5-41.8 mm against 46.1) and no deeper at the maximum (8.5-8.7 against 9.1). Their overhead presses are fewer (4 poses against 6). On the bench pick1 presses 1 pose at 5.4 mm against 2 at 14.7 mm summed. |
| **Pose that jams** | None in range on a working fit. The verified config's env-fit shape jams at rest, as described: it is the one jam this polish found, and it is a property of the synthesis margin, not of a pose. |

## 8. What happens next

1. **The verified config stays the CAD config.** The gain is under 1 on the robust reading (+0.38 priced, -0.59
   unpriced). No verifier run is due.
2. **The crank-side flank margin is the actionable finding for the CAD.** The lead's flank goes immovable at
   r_c -0.2 mm or g -0.02 (crank PA over 38.03). Before the flank is cut:
   * run a flank-only check: the verified seats and dyad with beta stepped toward pick1's -171 in 1-deg steps, on the
     verified protocol and held out;
   * claim the first beta that passes the 6-neighbour check if it costs < 0.2 held out.

   That is a buildability fix at (near) equal score, not a polish.
3. **This family's polish is exhausted.** Four env polishes have now run on it (sidecar, roller, inband-rssr, slipper).
   None moved the fold, which is K's stroke. The best confirmed gain was inband-rssr's +1.18 / +1.52 priced, which the
   audit ruled a tie with this lead. The next points need the morphology: a longer
   usable K stroke without the long dyad's overhead press, e.g. the trimmed horn lug of trimlug-k165.

## 9. Commands

```bash
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/slipper_env_polish/farm/jobs_cma.json      # 3 CMA runs + the env re-score
cd docs/research/slipper_env_polish/farm && python3 ../../../../tools/slipper_env_polish.py gate cma_snp-s1.json cma_snp-s2.json cma_snp-w3.json
python3 ../../../../tools/slipper_env_polish.py picks cma_snp-s1.json cma_snp-s2.json cma_snp-w3.json --out ../picks && cd -
CB_FOLD_MARGIN=5.5 python3 tools/slipper_env_polish.py robust BEST docs/research/slipper_env_polish/picks/pick{1,2,3}.json
python3 tools/slipper_env_polish.py prereg docs/research/slipper_env_polish/picks                                           # committed BEFORE the claim
python3 tools/slipper_env_polish.py claimjobs docs/research/slipper_env_polish/picks OUT.json --protos env:held,fit60:bench --readings p,u [--who BEST,pick1]
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/slipper_env_polish/farm/jobs_claim.json
# one claim by hand (exact): reproduce the verified 18.49 (3 min locally)
CB_EXACT=1 CB_FOLD_MARGIN=5 ENVP_NOPRICE=1 python3 tools/slipper_env_polish.py claim fit60 bench BEST out.json
python3 docs/research/slipper_env_polish/summarize.py; python3 docs/research/slipper_env_polish/paired.py docs/research/slipper_env_polish/paired.json
```

## 10. Cost

On exo-cpu1 (8-vCPU workers, 4 jobs per worker); `runpod_guard audit` before each batch (balance $25.16 at 12:48 UTC,
$24.94 at 13:17, $24.69 at 13:35 with other agents spending too); workersMin stayed 0.

| batch | jobs | billed worker-s | $ (cpu3c / cpu5c) |
|---|---|---|---|
| CMA (3 runs) + env re-score | 4 | 1531 | 0.1225 / 0.1429 |
| claim | 10 | 2235 | 0.1788 / 0.2086 |
| **total** | 14 | 3766 | **0.301 / 0.352** |

Against the $0.30 budget: on budget at cpu3c, $0.05 over at cpu5c (the billing line cannot say which type ran), plus
cold starts (about $0.01 per new worker). Local: at most 2 niced processes (the reproduction, 6 fit60 claims, the
robustness and flank-margin scans, a 23-min local env-cache build that was stopped unused).

## Files

* `tools/slipper_env_polish.py`: the objective, CMA (crossfit_polish's driver), gate, picks, `prereg`, rescore, claim
  (both readings, per-pose dump), claimjobs, robust, classes.
* `docs/research/slipper_env_polish/env_table.json`: the distribution table.
* `docs/research/slipper_env_polish/farm/`: `jobs_cma.json`, `jobs_claim.json`, `cma_snp-*.json` (+ state and log),
  `rescore_BEST_*`, `claim_*` (+ `_perpose.json`, 10 claims).
* `docs/research/slipper_env_polish/local/`: `claim_*` (+ `_perpose.json`, 7 claims including the reproduction),
  `robust_BEST.json`, `flank_margin_BEST.json`.
* `docs/research/slipper_env_polish/picks/`: `pick{1,2,3}.json`, `robust_picks.json`, `prereg.json`.
* `docs/research/slipper_env_polish/summarize.py`, `paired.py`, `summary.json`, `paired.json`.

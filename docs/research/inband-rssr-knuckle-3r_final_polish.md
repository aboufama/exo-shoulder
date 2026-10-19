# inband-rssr-knuckle-3r final polish on the envelope bench (2026-10-17): pick3 gains +1.18 / +1.52 held out and +1.10 on the verified protocol; a verifier is due

Self-measured, not verified. The winner is inband-rssr-knuckle-3r: its leak-free pick cma3 p was screened at 18.87 frozen
exact on Bench(110,360) and 23.21 held out, a tie with the leader slipper-nose-knuckle-3r (18.49 / 23.45). It was
polished on the representative envelope bench `env` on the CPU farm and claimed on the held-out set and on the verified
protocol. The tool is `tools/inband_env_polish.py` (new; adapted from `tools/roller_env_polish.py`). The row has no
verifier harness yet, so the claim runs the row's own frozen protocol from the long-stroke model's `_frozen_model` with
the fit bench swappable. Read unpriced at margin 5, it reproduces the row's 18.87 / 23.21 to the digit (section 6).

**Verdict.** pick3 (`ibp-s2-g6-4`) improves on the row's pick under every protocol at the same built-stop pricing
(smlo +0.5, the reading at margin 5.5, K's stop B at bk1 + bk2 - 5.5):
* held out: **+1.52** with the shape fit on Bench(60,160) (24.38 -> 22.86), +1.18 with it fit on env (24.75 -> 23.57);
* the verified protocol: **+1.10** (19.43 -> 18.33);
* 1 mm and 2 mm near-touch: better or equal on all three;
* summed contact depth: less on all three (bench 9.9 -> 0.2 mm, held 23.2 -> 21.2 mm).

**Robust held-out gain (the worse of the two held-out fits): +1.18.** That is >= 1, so the template's independent
verifier is due. The CAD keeps the row's pick until it confirms the gain. pick1 has the larger robust gain (+1.26), but
it is 1.37 worse at 1 mm on the verified protocol and fails 2 of 18 tolerance neighbours.

**What the long-dyad question measured.** On env the K dyad does not want to be long either:
* 4 long-dyad seeds walked back from bk2 47-48 to 42.7-46.7, and none converged inside the budget;
* with bk2 held at 48, the best objective was 27.8-28.5, against 22.1 for the short dyad;
* all 3 picks stay at 26 / 38;
* a report-only long-dyad row (29.0 / 44.6 / 68.1, kK 2.82, the best on envsel among rows with bk2 >= 43 that pass the
  depth guard) regains 20 held-out poses from the fold (fold 251 vs 271). It still reads 23.72 / 23.03 held out and
  20.44 on the verified protocol, and presses 40.9 mm summed held out (overhead 29.3 mm).
* So the long dyad buys reach on the stretched poses and pays it back in overhead contact depth and in-band.

**Hard goal not met.** pick3 reads 18.33 frozen exact (meets <= 18.5) but 22.86 held out (misses <= 22.0).

**Against the leader's 23.45 held out:** pick3, priced, reads 22.86. Paired per pose it is -0.59 held out (90 % CI
[-1.59, +0.32], P better 0.82) and -0.46 pooled (CI [-1.46, +0.44], P 0.79). That is an edge, not a clear lead. The
comparison is conservative, because the leader's dumps are read unpriced at margin 5.

Cost: $1.05 (cpu3c) to $1.23 (cpu5c) of the $1.2 budget (section 10). Wall time about 75 min.

## 1. The search bench: `env`, reused (step 1)

The fast caches `env-72d21f5aa2e5-env` and `env-fc171830d1d7-envsel` were linked from the farm volume
(`tools/env_bench.py use`). They were built and validated for the minarc polish (max fast-vs-exact error 1.86 mm, sign
agreement beyond 1 mm 1.0). The draw is frozen in `docs/research/minarc_final_polish/env_poses.npz`:
* the 110 clip frames of Bench(110,360) (never Wave / Walking);
* 420 fresh workspace poses (`env`, the search bench);
* an independent 360-pose draw (`envsel`, the pick-selection bench).

Each draw is stratified on the grid's elevation x plane x signed-axial shares, and no pose lies within 2 deg of a
held-out pose. The table was re-printed today with `python3 tools/env_bench.py table`
(`docs/research/inband_env_polish/env_table.json`):

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| **Bench(60,160) ws (the fit bench of every earlier search)** | 160 | **2.5 %** | 28.1 % | 7.5 % | 16.9 % | 6.3 % | 36.3 % | 23.8 % | 26.9 % | -26.1 |
| **env** ws | 420 | **9.3 %** | 23.1 % | 7.1 % | 17.1 % | 6.0 % | 35.7 % | 24.1 % | 27.4 % | -34.0 |
| **envsel** ws | 360 | **9.7 %** | 22.8 % | 7.2 % | 16.9 % | 6.9 % | 36.1 % | 23.6 % | 26.7 % | -33.4 |

Closest fresh pose to any held-out pose: env 2.23 deg (coordinates) / 2.04 deg (humerus orientation), envsel 2.07 /
2.03 deg; median 7.5 / 7.3 deg.

## 2. The tool: `tools/inband_env_polish.py`

It keeps the roller polish's objective and rules and adds three changes for this row:
* the in-band RSSR model (`docs/concepts/models/inband-rssr-knuckle-3r.py`) loaded unchanged;
* the drive's packaging kept fixed: clay 1 (the crank on its ear), bl_c 2 (the radial crank stud), bl_h 0;
* the knee window bounded below by the pick's own ang_min (25.2189).

The objective (lower is better):
* a = the priced config fit on env FAST, scored in-sample;
* b = the same config fit on Bench(60,160) FAST, worn FROZEN on env;
* obj = (a + b) / 2 at the 1 mm near-touch gap, with the continuity knock-out.

The guards:
* the claim-fit guard: max(0, g60 - a - 3);
* a depth guard: 0.1 x (summed env depth over the pick's own 6.89 mm);
* +100 for a dishonest report (RSSR open, drive idle, knee moved);
* +100 for any taken pose whose own-state th margin is under the reading's 5.5.

Logged: both shapes worn frozen on envsel, which is the pick-selection number.

The rules carried over:
* stops are variables >= 5.0, priced at +0.5 (smlo + 0.5, the reading at CB_FOLD_MARGIN 5.5, a1max' = min(a1max,
  bk1 + bk2 - 5.5));
* O20 hubs, and the RSSR range scan (transmission >= 48, i.e. PA <= 42 at both ball ends, and the radial socket's cone
  <= 30);
* continuity: the full-grid flood (2-deg slerp edges, passive joints <= 10 deg, actives <= 25), plus every fresh env pose
  joined to the connected grid by an edge to one of its 6 nearest connected nodes.

25 free parameters:
* the K dyad: bk1, bk2, a1max;
* the law: kK, free over 0.8-3.5;
* the drive: La, s_arm, r_h, beta, gam, hl, zc, eta, r_lobe;
* the stops: smhi, smlo;
* the seats: az1, el1, az2, el2, wd, wa, b3, lc, phib, ang_min.

Also in the tool:
* `robust`: the row's knife edge, one parameter at a time on Bench(60,160): +-1 deg on beta / gam / eta, +-0.25 mm on
  La / r_h / s_arm / hl / zc / r_lobe. A neighbour fails when it does not close, when its drive range falls under the
  taken dK - 1, or when it loses > 5 near-touch points.
* `claim` writes the per-pose dump (the alignment_paired format) and records:
  * contact depth by pose class;
  * the min th margin;
  * the socket tilt, transmission and dK taken / range;
  * the spring against R17.

## 3. Re-score on env (step 2)

Farm jobs `ibp-rescore-*`, continuity on (`farm/rescore_PICK_{nominal,priced}.json`):

| reading | fit env fast, in-sample | fit env -> env exact | fit Bench(60,160) -> env exact | env depth (mm), two fits | min th | Bench(110,360) | held out |
|---|---|---|---|---|---|---|---|
| as screened (nominal stops, margin 5) | 20.57 (1 mm 22.49) | **20.50** (1 mm 22.42), reach 0.714, ib14 0.893 | 20.79 (1 mm 23.67), reach 0.707, ib14 0.897 | 10.2 / 8.9 | 5.475 | 18.87 | 23.21 |
| priced (smlo +0.5, margin 5.5, a1max 58.5) | 20.58 (22.50) | 20.51 (22.43), reach 0.712 | 20.79 (24.16), reach 0.705 | 7.9 / 6.1 | 5.778 | 19.43 | 24.38 |

* env sits between the verified bench and held out, as designed: 20.5 against 18.87 / 23.21.
* Every fresh env pose the flood reaches is connected (300 / 300, 174 with K forced). Static = connected.
* The pricing is a MEASUREMENT change:
  * on env it costs 0.01 (env fit) to 0.49 (1 mm, Bench(60,160) fit);
  * on the verified protocol it costs 0.56 (18.87 -> 19.43);
  * held out it costs 1.17 (23.21 -> 24.38), with the fold at 260 -> 271 held-out poses.
* The pick sits close to the 5-deg rule (min th margin 5.045 held out), so a 5.5 reading drops poses that a polish run
  at 5.5 can win back.

## 4. CMA on env (step 3) and the convergence gate

One farm batch (`farm/jobs_cma.json`) ran 10 runs: popsize 8, 2 processes, patience 12, 2100 s each, 4 jobs per
8-vCPU worker. An evaluation cost 16-51 s, depending on the worker's load.

| run | start | sigma (start -> end) | evals | stop | x0 obj | best obj (row) | K dyad of the best | gate |
|---|---|---|---|---|---|---|---|---|
| s1 | the pick | 0.3 -> 0.20 | 113 | patience | 23.15 | 23.02 (g2-3) | 26.0 / 38.4 | passes |
| s2 | the pick | 0.3 -> 0.21 | 73 | budget | 23.15 | 22.58 (g5-6) | 26.0 / 38.0 | passes |
| w3 | the pick | 0.5 -> 0.37 | 105 | patience | 23.15 | **22.08** (g1-0) | 26.0 / 38.0 | passes |
| r1 | robust build (r_h +0.25, eta +1) | 0.3 -> 0.20 | 145 | budget | 23.04 | 22.35 (g17-0) | 26.1 / 39.1 | passes |
| L1 | ib-cma2-j-g10-1 (28.3 / 47.2, kK 2.73) | 0.3 -> 0.27 | 241 | budget | 38.63 | 25.01 | 28.1 / 43.5, kK 2.36 | no (2.27 / 1.07) |
| L2 | ib-cma2-j-g12-7 (28.5 / 48.0, kK 2.70) | 0.3 -> 0.30 | 257 | budget | 38.39 | 23.89 | 27.8 / 42.7, kK 2.72 | no (2.78 / 0.33) |
| L3 | the pick's drive on 30 / 48, kK 1.8 | 0.3 -> 0.26 | 89 | budget | 42.85 | 25.27 | 29.4 / 45.2, kK 1.78 | no (6.95) |
| L4 | the pick's drive on 28 / 48, kK 1.8 | 0.4 -> 0.30 | 89 | budget | 85.94 | 29.41 | 27.9 / 46.7 | passes |
| H1 | L1's seed, **bk2 held at 48** | 0.3 -> 0.24 | 145 | budget | 43.79 | 28.46 | 28.0 / 48, kK 2.95 | no (3.9 / 3.1) |
| H2 | L3's seed, **bk2 held at 48** | 0.3 -> 0.24 | 145 | budget | 42.85 | 27.79 | 29.0 / 48, kK 1.70 | no (2.9 / 2.3) |

* **Gate** (`gate`, `farm/gate.txt`): combined over all 1402 tries in generation order, the best gained 0.00 over the
  2nd half and 0.00 over the last third, and the top 5 sit within 0.42. **It passes.** Each short-dyad run passes too.
* **The long-dyad runs are still descending.** Their gates fail, so their best values are upper bounds, not optima.
* **Caveat.** As on the roller polish, 73-257 evaluations in 25 dimensions read stagnation, not a proven optimum.
* **Long-dyad seeds that close** (`local/seed_scan.json`, Bench(60,160) fast, priced):
  * on the pick's drive, only kK 1.8 on bk2 48 closes (near1 33.3-33.7);
  * kK 2.4-3.0 cuts the lobe law at 11 deg;
  * bk2 50, or bk1 32, leaves no drive range (transmission at rest);
  * the long-stroke row's leaky seeds (28.3-28.5 / 47.2-48.0, kK 2.7) close at near1 21.8-25.4, against the pick's 14.0.

**The objective by K dyad over every evaluated row** (1236 closing rows):

| bk2 | rows | best obj | its env / env60 1 mm | best envsel mean (1 mm, two fits) |
|---|---|---|---|---|
| 38-39 | 232 | **22.08** | 21.01 / 22.38 | 25.91 |
| 39-41 | 136 | 22.35 | 22.11 / 22.39 | 26.58 |
| 41-43 | 29 | 23.89 | 22.09 / 23.46 | 27.23 |
| 43-45 | 160 | 23.97 | 22.05 / 23.40 | 25.71 (depth 44 mm, fails the guard) |
| 45-47 | 243 | 24.22 | 22.81 / 23.66 | 25.77 (depth 43 mm, fails the guard) |
| 47-49 | 434 | 26.80 | 23.86 / 24.64 | 26.50 |

* The objective rises monotonically with bk2: about 2 points at 45 and 4.7 at 48.
* Most of the cost is in the Bench(60,160)-fit wear (env60), and in summed depth.
* On envsel the bands sit within 0.2 of each other at their noise-selected minima. Those minima belong to rows 2-3x
  deeper than the pick, which the depth guard excludes.
* **The envelope bench therefore does not overturn the fit bench's verdict.** It narrows it: the long dyad does not lose
  reach on env. It loses in-band, contact depth and fit transfer.

## 5. Picks (committed before the claim, commit 28b9bb4)

The rule (`picks`):
* candidates = the best 15 rows of each run by the objective, with no penalty;
* a candidate may not be deeper than the pick on envsel (19.58 mm);
* ranked on the envsel 1 mm mean over the two fits;
* each pick differs from every kept pick by >= 0.5 CMA scale units in some parameter.

| pick | row | obj | env / env60 1 mm | envsel 1 mm mean (the pick: 28.81) | envsel depth (mm) | Bench(60,160) in-sample 1 mm | crank socket tilt (deg) |
|---|---|---|---|---|---|---|---|
| pick1 | ibp-w3-g2-6 | 22.85 | 22.43 / 23.00 | **25.91** | 3.6 | 13.77 | 21.0 |
| pick2 | ibp-w3-g1-0 | 22.08 | 21.01 / 22.38 | 26.23 | 5.6 | 14.17 | 18.2 |
| pick3 | ibp-s2-g6-4 | 22.91 | 21.59 / 23.87 | 26.30 | 14.8 | 14.30 | 20.0 |

What moved, with the priced reading applied in the claim:

| key | the row's pick | pick1 | pick2 | pick3 |
|---|---|---|---|---|
| bk1 / bk2 / a1max | 26.0 / 38.0 / 59.0 | 26.0 / 38.0 / 58.14 | 26.01 / 38.0 / 57.15 | 26.04 / 38.0 / 59.24 |
| kK | 1.790 | 1.980 | 1.876 | 1.862 |
| La / s_arm / r_h | 19.50 / 4.05 / 14.62 | 19.46 / 4.00 / 14.74 | 19.79 / 4.02 / 14.68 | 20.00 / 4.10 / 14.76 |
| beta / gam / eta | -140.4 / 7.7 / -12.4 | -133.4 / **16.3** / -12.4 | -132.3 / 7.6 / -9.8 | -140.4 / **11.9** / -11.1 |
| hl / zc / r_lobe | 3.15 / 0.80 / 7.00 | 3.15 / 1.17 / 7.04 | 3.15 / 0.74 / 7.00 | 3.15 / 0.89 / 7.16 |
| smhi / smlo | 19.10 / 5.00 | 19.70 / 5.00 | 19.04 / 5.00 | 19.46 / 5.03 |
| az1 / el1 / az2 / el2 | 95.39 / 67.90 / 45.82 / 41.09 | 94.70 / 67.49 / 45.34 / 41.78 | 95.39 / 67.25 / 45.72 / 41.17 | 95.33 / 67.66 / 46.37 / 41.57 |
| wd / wa / b3 / lc / phib / ang_min | 66.87 / -10.66 / 0.329 / 21.15 / -58.81 / 25.22 | 66.02 / -10.89 / 0.342 / 22.47 / -57.14 / 25.57 | 64.73 / -10.61 / 0.311 / 21.91 / -58.34 / 25.22 | 66.07 / -10.78 / 0.325 / 21.55 / -57.92 / 25.22 |

* All three picks stay at 26 / 38, steepen the law a little (kK 1.86-1.98), and keep the folded dowel at its 5.0
  floor.
* The common move is the crank phase. pick1 and pick3 raise gam, which lowers the radial crank stud's socket tilt from
  25.5-26.0 to 18-21 deg (section 7).
* No long-dyad row qualified. The long rows with the best envsel numbers press 2-3x deeper than the pick.

## 6. The claim (step 4): one farm batch, 15 jobs (+ 3 report-only)

The batch is `farm/jobs_claim.json`; each job writes `claim_*.json` and a `_perpose.json` dump. It ran:
* the row's pick (PICK), priced, and the 3 picks, each through three protocols;
* PICK unpriced at margin 5 on the verified protocol and held out, as the reproduction;
* the row's robust build (r_h +0.25, eta +1), held out.

All runs are exact on the worn bench, with continuity on. The full-grid flood dropped no taken pose in any claim
(connected = static on every row). `python3 docs/research/inband_env_polish/summarize.py` prints the table.

| config | protocol | gap | 1 mm / 2 mm | reach | ib14 | contact poses | depth sum / max (mm) | fold / slide | min th | dK taken / range | crank / horn socket tilt | min transmission |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PICK as screened (margin 5, nominal) | fit60 -> Bench(110,360) | **18.87** (= row) | 19.96 / 34.12 | 0.7222 | 0.8971 | 3 | 9.86 / 9.72 | 88 / 9 | 5.231 | 45.8 / 65.8 | 25.5 / 15.1 | 52.0 |
| PICK as screened | fit60 -> held out | **23.21** (= row) | 26.53 / 36.97 | 0.6828 | 0.8956 | 9 | 23.20 / 8.71 | 260 / 33 | 5.045 | 46.4 / 65.8 | 25.5 / 15.1 | 52.0 |
| **PICK, priced (the baseline)** | fit60 -> Bench(110,360) | **19.43** | 20.53 / 34.72 | 0.7167 | 0.8971 | 3 | 9.86 / 9.72 | 90 / 9 | 5.799 | 44.0 / 63.5 | 25.5 / 14.5 | 52.0 |
| PICK, priced | fit60 -> held out | **24.38** | 27.50 / 37.35 | 0.6712 | 0.8956 | 9 | 23.20 / 8.71 | 271 / 33 | 5.601 | 44.6 / 63.5 | 25.5 / 14.5 | 52.0 |
| PICK, priced | env -> held out | 24.75 | 25.87 / 35.64 | 0.6723 | 0.8908 | 9 | 24.65 / 8.84 | 271 / 32 | 5.601 | 44.6 / 63.5 | 26.0 / 16.8 | 51.7 |
| robust build, priced | fit60 -> held out | 24.33 | 27.45 / 37.35 | 0.6712 | 0.8961 | 9 | 23.37 / 8.74 | 271 / 33 | 5.601 | 44.6 / 63.5 | 25.9 / 14.5 | 51.6 |
| pick1 | fit60 -> Bench(110,360) | 19.15 | 21.90 / 28.19 | 0.7139 | 0.9002 | 2 | 3.70 / 3.40 | 90 / 11 | 6.565 | 46.8 / 63.0 | 20.4 / 18.9 | 59.7 |
| pick1 | fit60 -> held out | 23.12 | 25.77 / 35.42 | 0.6807 | 0.8986 | 9 | 21.68 / 6.11 | 260 / 35 | 5.505 | 50.3 / 63.0 | 20.4 / 18.9 | 59.7 |
| pick1 | env -> held out | **22.43** | 25.97 / 35.09 | 0.6838 | 0.9032 | 7 | 22.02 / 6.65 | 260 / 34 | 5.505 | 50.3 / 63.0 | 21.0 / 18.9 | 59.7 |
| pick2 | fit60 -> Bench(110,360) | 19.49 | 22.23 / 33.34 | 0.7167 | 0.8965 | 3 | 5.19 / 4.07 | 89 / 10 | 6.132 | 44.1 / 58.5 | 17.9 / 18.6 | 60.1 |
| pick2 | fit60 -> held out | 23.39 | 27.14 / 38.16 | 0.6817 | 0.8949 | 9 | 24.78 / 6.79 | 259 / 35 | 5.594 | 45.9 / 58.5 | 17.9 / 18.6 | 60.1 |
| pick2 | env -> held out | 23.47 | 24.57 / 34.43 | 0.6796 | 0.8985 | 11 | 27.26 / 7.85 | 259 / 35 | 5.594 | 45.9 / 58.5 | 18.2 / 19.8 | 59.6 |
| **pick3** | fit60 -> Bench(110,360) | **18.33** | 20.52 / 33.38 | 0.7194 | 0.9071 | 1 | **0.22 / 0.22** | 90 / 10 | 5.589 | 47.5 / 65.5 | 19.6 / 16.6 | 54.1 |
| **pick3** | fit60 -> held out | **22.86** | 26.19 / 36.65 | 0.6807 | 0.9056 | 8 | 21.16 / 6.09 | 263 / 33 | 5.524 | 47.7 / 65.5 | 19.6 / 16.6 | 54.1 |
| **pick3** | env -> held out | 23.57 | 25.13 / 34.16 | 0.6807 | 0.8929 | 8 | 21.60 / 6.65 | 263 / 33 | 5.524 | 47.7 / 65.5 | 20.0 / 18.0 | 53.8 |
| long-dyad report row (29.0 / 44.6 / 68.1, kK 2.82; REPORT ONLY) | fit60 -> Bench(110,360) | 20.44 | 22.08 / 34.73 | 0.7139 | 0.8898 | 3 | 10.77 / 5.58 | 87 / 13 | 6.314 | 32.7 / 66.0 | 12.8 / 13.5 | 59.7 |
| long-dyad report row | fit60 -> held out | 23.72 | 25.72 / 41.97 | 0.6849 | 0.8883 | 9 | **40.86** / 9.01 | **251** / 40 | 5.515 | 37.7 / 66.0 | 12.8 / 13.5 | 59.7 |
| long-dyad report row | env -> held out | 23.03 | 25.02 / 33.40 | 0.6870 | 0.8942 | 10 | 42.73 / 8.30 | 251 / 37 | 5.515 | 37.7 / 64.8 | 13.4 / 16.0 | 59.3 |

**Held-out gain over the row's pick (positive = better).** Every number compares the same protocol at the same priced
reading (smlo +0.5, margin 5.5, stop B at bk1 + bk2 - 5.5):

| pick | env -> held | CAD shape, fit60 -> held | verified protocol (fit60 -> Bench(110,360)) | 1 mm (env-held / fit60-held / bench) | 2 mm (same) | summed depth (held fit60 / bench) | robust gain (worse held-out fit) |
|---|---|---|---|---|---|---|---|
| pick1 | **+2.32** | +1.26 | +0.28 | -0.10 / +1.73 / **-1.37** | +0.55 / +1.93 / +6.53 | -1.5 / -6.2 mm | **+1.26** |
| pick2 | +1.28 | +0.99 | -0.06 | +1.30 / +0.36 / -1.70 | +1.21 / -0.81 / +1.38 | +1.6 / -4.7 mm | +0.99 |
| **pick3** | +1.18 | **+1.52** | **+1.10** | +0.74 / +1.31 / +0.01 | +1.48 / +0.70 / +1.34 | -2.0 / -9.6 mm | **+1.18** |
| long-dyad row (report only) | +1.72 | +0.66 | -1.01 | +0.85 / +1.78 / -1.55 | +2.24 / -4.62 / -0.01 | +17.7 / +0.9 mm | +0.66 |

**Reading.**
* **pick3 is the only pick that gains under all three protocols**, at both near-touch thresholds and with less contact
  depth. Its fit-protocol spread is small: 22.86 on the Bench(60,160) fit vs 23.57 on the env fit. So this is not the
  fit-protocol artifact that made the sidecar and roller polishes' env-fit gains vanish.
* **Where pick3's gain comes from (held out, fit60):**
  * reach: 9 more held-out poses taken (fold 271 -> 263, one contact fewer);
  * in-band: 0.8956 -> 0.9056;
  * contact: 1 pose fewer.
  * On the verified protocol it takes the same 90-fold reading with in-band 0.9071 against 0.8971, and 1 contact at
    0.22 mm against 3 summing 9.86 mm.
  * Bench pose 237 (elev 165, plane 15, axial -60), where the pick pressed hub K + horn + rod 9.7 mm, is now lost to the
    fold or slide instead of pressed. A lost pose costs reach only; a contact pose costs reach and contact. The metal
    did not move off the skin there; the chain stopped reaching it.
* **pick1 gains most on the env fit** (+2.32), but on the verified protocol it is 1.37 worse at 1 mm, and it is a knife
  edge (section 7).
* **The long-dyad report row** reaches further: fold 251 against 263-271, plus 4 across-body and 2 axial >= 150 poses
  over pick3. It pays for that with 40.9 mm of summed held-out depth, 29.3 mm of it overhead, and 1 point of
  verified-protocol gap.
* **The pricing as a measurement change.** On the as-screened pick it costs 0.56 frozen and 1.17 held out. Against the
  row's on-file unpriced numbers (18.87 / 23.21), priced pick3 is 0.54 / 0.35 better; pick3 unpriced was not run
  (budget).

**Against the leader** (slipper-nose-knuckle-3r 18.49 / 23.45; the paired bootstrap of the inband_drive row,
`docs/research/inband_drive/paired.py`, on pick3's dumps; `farm/paired_*_vs_slipper-nose.json`):

| config (priced) | bench diff | held diff (90 % CI, P better) | pooled diff (90 % CI, P better) |
|---|---|---|---|
| PICK | +0.95 | +0.93 ([+0.26, +1.68], 0.01) | +0.94 ([+0.37, +1.61], 0.003) |
| pick1 | +0.67 | -0.34 ([-1.23, +0.75], 0.63) | -0.06 ([-0.80, +0.95], 0.46) |
| **pick3** | **-0.16** | **-0.59** ([-1.59, +0.32], 0.82) | **-0.46** ([-1.46, +0.44], 0.79) |

Negative = better than the leader. The leader is read unpriced at margin 5, so priced rows are handicapped by about the
PICK's 0.56 / 1.17 pricing cost. pick3 is ahead even so, but the CI crosses 0: an edge, not a clear lead.

**On every claimed run (rules):**
* **th margin** (own state, member frames): min over taken poses 5.505-6.565 on every priced run, 0 poses under 5.5.
  The as-screened reading is 5.231 / 5.045.
* **Continuity:** 0 taken poses dropped by the flood on every run.
* **Drive:** taken dK <= 50.3, inside each range (58.5-65.5, ended by the law). Transmission >= 51.6 (PA <= 38.4).
* **Low-arm extreme-rotation class** (elev < 60, abs(axial) >= 120; 110 held-out workspace poses): **0 contacts on every
  claim.** Taken: PICK 57-62, pick3 61, pick1 64, long-dyad row 66.
* **Overhead contact depth held out** (elev >= 140, fit60): PICK 5 poses / 10.8 mm, pick3 4 / 8.4 mm, pick1 4 / 8.3 mm,
  long-dyad row 4 / 29.3 mm.
* **Spring vs R17** (the lead's clock spring 0.08 N.m + 0.015 N.m/rad through kK, at the held-out dK taken):

| config | J2 static | cuff force at 150 / 120 mm | R17 share (1 N.m / 5 N) |
|---|---|---|---|
| PICK | 0.164 N.m | 1.09 / 1.37 N | 16 % / 27 % |
| pick3 | 0.172 N.m | 1.15 / 1.44 N | 17 % / 29 % |
| pick1 | 0.184 N.m | 1.23 / 1.54 N | 18 % / 31 % |
| long-dyad row | 0.254 N.m | 1.69 / 2.11 N | 25 % / 42 % |

  All are static only; the dynamic twist needs judge/dynamics.py on a CAD.

## 7. Red team

| attack | result |
|---|---|
| **Radial crank stud socket tilt** (the row: 25.5 deg against a 30 deg cone) | **It is a cliff, not a margin.** The tilt peaks at rest (dK = 0). Re-read with a smaller cone (`local/cone_check.json`, Bench(60,160)): 27 deg changes nothing, but at 25 deg the drive cannot leave rest (dK range 0, near1 14.0 -> 98.6, fold 33 -> 130). With the knife-edge neighbours it reaches 27.2 deg (robust build, gam -1). So the row's pick needs an M2 ball link with >= 28 deg swivel; a long-neck +-30 deg link leaves 2-3 deg. **The crank phase is the lever** (`local/gam_tilt_scan.json`, robust build): gam +2 / +3 / +4 gives tilt 23.4 / 22.2 / 21.0 deg at near1 13.86 / 13.81 / 13.76 (better than 14.01), near2 unchanged to +3. The picks found the same move: **pick3 runs at 19.6-20.0 deg, pick2 at 17.9-18.2, pick1 at 20.4-21.0, all within a 25 deg short-neck link.** The axial-stud alternative stays on file (row secondary cma1 f: 18.21 / 23.42, leaky law seed); this polish did not need it. |
| **Knife edge** (+-1 deg beta / gam / eta, +-0.25 mm La / r_h / s_arm / hl / zc / r_lobe, one at a time; `local/robust_pick.json`, `picks/robust_picks.json`) | The row's pick fails 2 of 18: r_h -0.25 (every pose lost, near1 275: the horn ball 0.25 mm from a 1 mm part pair) and eta -1 (+7.3). The robust build passes 18 / 18. **pick3 fails 1 of 18** (r_h -0.25: near1 14.3 -> 39.8). **pick3 + r_h 0.25 (`picks/pick3_rh025.json`) passes 18 / 18** (Bench(60,160) fast); it was not worn held out, so the verifier should wear it. pick1 fails 2 (r_h -0.25: 44.3; s_arm +0.25: the lobe law ends at 11 deg, near1 98.6). pick2 fails 1 (r_h -0.25: every pose lost). The long-dyad row fails 1 (r_h -0.25: every pose lost). **The horn ball's 1 mm part-pair edge is the family's knife edge: every buildable config needs r_h +0.25 over its nominal.** |
| **Contact depth, low-arm extreme rotation** | 0 contacts on every claim (section 6). pick3's deepest held-out press is 6.09 mm, against the pick's 8.71. |
| **Pose that jams** | None in range. Taken transmission >= 51.6 deg (PA <= 38.4) on every claim; every range ends on the law, not on transmission. |
| **Optimistic number** | pick1's +2.32 (env fit) is the biggest held-out gain, but its CAD-shape number is +1.26 and its verified protocol is -1.37 at 1 mm. pick3's numbers agree within 0.7 across fits. The robust gain stated here is the worse fit (+1.18). |
| **Selection on noise** | The env objective's best row (w3-g1-0, 22.08) is pick2, the weakest pick held out (+0.99 / +1.28). The envsel ranking put pick1 and pick3, which were not the objective's best, ahead. As on the roller, the objective's top rows do not transfer best. |

## 8. What happens next

1. **The independent verifier (template step 'Verify')**, since the robust held-out gain is >= 1. It should:
   * re-run PICK and pick3 through the claim harness, priced:
     * fit env -> held out;
     * fit Bench(60,160) -> Bench(110,360);
     * fit Bench(60,160) -> held out;
   * wear pick3's robust build (`picks/pick3_rh025.json`) held out;
   * confirm the env bench's held-out exclusion (`python3 tools/env_bench.py table`).
   * Confirm only on its own numbers.
   * The row has no verifier harness of its own yet, so its pick needs verifying too: `claim fit60 bench PICK` with
     ENVP_NOPRICE=1 CB_FOLD_MARGIN=5 reproduces 18.87, the row's claim.
2. **If confirmed:**
   * pick3 (with r_h +0.25) is the CAD config of this row;
   * the polished reading is 18.33 / 22.86 against the leader's 18.49 / 23.45;
   * a paired test at the same pricing (the leader re-read priced) decides whether it leads.
3. **The long dyad is a morphology question, not a polish one.** On the representative bench it regains about 20
   held-out fold poses and loses them back to overhead contact depth (hub K / horn at elevation >= 140) and in-band. A
   long-dyad variant would need its overhead press fixed first, for example the horn-lug trim the trimlug-k165 row is
   modelling.

## 9. Commands

```bash
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/inband_env_polish/farm/jobs_cma.json      # 10 CMA runs + 2 env re-scores
python3 tools/inband_env_polish.py gate docs/research/inband_env_polish/farm/cma_ibp-*.json   (state files excluded)
cd docs/research/inband_env_polish/farm && python3 ../../../../tools/inband_env_polish.py picks cma_ibp-s1.json cma_ibp-s2.json cma_ibp-w3.json cma_ibp-r1.json cma_ibp-L1.json cma_ibp-L2.json cma_ibp-L3.json cma_ibp-L4.json cma_ibp-H1.json cma_ibp-H2.json --out ../picks
python3 tools/inband_env_polish.py claimjobs docs/research/inband_env_polish/picks docs/research/inband_env_polish/farm/jobs_claim.json
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/inband_env_polish/farm/jobs_claim.json      # the 15 claims
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/inband_env_polish/farm/jobs_longdyad.json   # report only
python3 docs/research/inband_env_polish/summarize.py
CB_FOLD_MARGIN=5.5 python3 tools/inband_env_polish.py robust PICK ROBUST docs/research/inband_env_polish/picks/pick3.json docs/research/inband_env_polish/picks/pick3_rh025.json
# one claim by hand (exact; farm recommended): reproduce the row's 18.87
eval "$(python3 tools/env_bench.py use env)"; CB_EXACT=1 CB_FOLD_MARGIN=5 ENVP_NOPRICE=1 python3 tools/inband_env_polish.py claim fit60 bench PICK out.json
```

## 10. Cost

All on exo-cpu1 (8-vCPU workers, 4 jobs per worker); `runpod_guard audit` before each batch; workersMin stayed 0.

| batch | jobs | billed worker-s | $ (cpu3c / cpu5c) |
|---|---|---|---|
| CMA (10 runs) + 2 env re-scores | 12 | 8381 | 0.671 / 0.782 |
| claim | 15 | 4442 | 0.355 / 0.415 |
| long-dyad report row | 3 | 361 | 0.029 / 0.034 |
| **total** | 30 | 13184 | **1.055 / 1.231** |

Plus cold starts (about $0.01 per new worker). The cpu5c worst case runs $0.03 over the $1.2 budget. The billing line
cannot say which worker type ran. Local work used 1 process: the seed scan, the knife edge, the cone and gam scans
(about 6 min).

## Files

* `tools/inband_env_polish.py`: the objective, CMA (crossfit_polish's driver), gate, picks, rescore, claim (with the
  per-pose dump), claimjobs, robust, classes.
* `docs/research/inband_env_polish/env_table.json`: the distribution table.
* `docs/research/inband_env_polish/farm/`:
  * `jobs_*.json`;
  * `cma_ibp-*.json` (+ state and log);
  * `rescore_PICK_*`;
  * `claim_*` with `_perpose.json` (18 claims);
  * `paired_*_vs_slipper-nose.json`;
  * `summary.json`, `gate.txt`.
* `docs/research/inband_env_polish/picks/`:
  * `pick{1,2,3}.json`, `pick3_rh025.json`;
  * `longdyad_report.json` (report only);
  * `robust_picks.json`, `robust_pick3_rh025.json`.
* `docs/research/inband_env_polish/local/`:
  * `seed_scan.json`, `seed_cands.json`;
  * `robust_pick.json`, `cone_check.json`, `gam_tilt_scan.json`;
  * smoke runs.
* `docs/research/inband_env_polish/summarize.py`: the claim tables.

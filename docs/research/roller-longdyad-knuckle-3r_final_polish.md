# roller-longdyad-knuckle-3r final polish on the envelope bench (2026-10-17, second run): no pick replaces the verified config

Self-measured. The generation-6 winner (verified 18.67 frozen exact on Bench(110,360), score 93.21; held out 23.73;
audit-compliant reading 19.25 / 24.91) was polished on the representative envelope bench `env` on the CPU farm
(user decision (7), 2026-10-17 ~05:20 UTC) and claimed on the held-out set and on the verified protocol through the
verifier's own harness (`docs/concepts/verify/roller-longdyad-knuckle-3r.py`, imported unchanged).

**Verdict: no pick replaces the verified config. Robust held-out gain +0.73 (pick2), under the 1-point rule, so no
verifier run is needed and the verified config stays the CAD config.**

* **Same-protocol env-fit gain: +2.10** (pick1 and pick3: 26.72 -> 24.62, fit env fast -> held out exact). This is the
  fit-protocol artifact the sidecar polish found. Fitting the shape on env makes the verified config itself 1.81 points
  worse held out (24.91 -> 26.72). Compared shape for shape with the CAD's shape (fit Bench(60,160), 24.91), pick1 and
  pick3 gain only +0.29.
* **On the CAD's shape** (fit Bench(60,160) fast -> held out exact) the picks move held out by -0.16 / **+0.73** /
  +0.13.
* **On the verified protocol** (fit Bench(60,160) fast -> Bench(110,360) exact) every pick loses: -2.63 / -0.18 / -2.39.
* **Contact depth held out.** Every pick is deeper than the verified config's 39.0 mm summed depth (41.7 to 59.3 mm),
  and far from the hard goal's 35.66 mm. pick2's +0.73 is in-band (0.8924 -> 0.8986), not reach: it takes 1 more
  held-out pose net.
* **The fold is untouched.** The verified config loses 272 of 952 held-out workspace poses to the fold.
  * No pick regains more than 17 poses. At most 6 of them come from the fold-limited classes (pick3: 4 across-body,
    2 at axial >= 150).
  * Those classes stay lost: across-body 114-118 / 159, axial >= 150 deg 79-81 / 105, overhead 48-50 / 71.
  * Every pick loses 1-3 overhead poses net.
* **Hard goal** (held out <= 22.0 at summed held-out depth <= 35.66 mm): not met. The best held-out reading is 24.18
  (pick2, CAD shape), at 41.7 mm.

Cost $0.91-1.06 of the $1.5 budget on exo-cpu1 (5 batches, see Cost). Wall time about 70 min.

## 1. The search bench: `env`, reused (step 1)

The fast caches `env-72d21f5aa2e5-env` and `env-fc171830d1d7-envsel` were linked from the farm volume
(`tools/env_bench.py use`). They were validated for the minarc polish (max fast-vs-exact error 1.86 mm, sign agreement
beyond 1 mm 1.0). The draw is frozen (`docs/research/minarc_final_polish/env_poses.npz`):
* the 110 clip frames of Bench(110,360) (never Wave / Walking);
* 420 fresh workspace poses (env, the search bench);
* an independent 360-pose draw (envsel, the pick-selection bench).

Each draw is stratified on the grid's elevation x plane x signed-axial shares, with no pose within 2 deg of a held-out
pose. The table was re-printed today with `python3 tools/env_bench.py table`:

| set | n | abs(axial) >= 150 | axial -90..-45 | overhead | across-body | behind | el < 45 | el 90-140 | plane >= 100 | mean axial |
|---|---|---|---|---|---|---|---|---|---|---|
| full grid | 1432 | 9.4 % | 22.0 % | 7.5 % | 16.8 % | 6.7 % | 35.8 % | 23.8 % | 26.9 % | -32.8 |
| held out (ws) | 952 | 11.0 % | 20.7 % | 7.5 % | 16.7 % | 6.7 % | 35.5 % | 24.1 % | 26.8 % | -33.0 |
| Bench(110,360) ws | 360 | 7.5 % | 23.9 % | 7.8 % | 17.2 % | 6.9 % | 35.6 % | 23.6 % | 26.9 % | -34.8 |
| Bench(60,160) ws | 160 | 2.5 % | 28.1 % | 7.5 % | 16.9 % | 6.3 % | 36.3 % | 23.8 % | 26.9 % | -26.1 |
| **env** ws | 420 | **9.3 %** | 23.1 % | 7.1 % | 17.1 % | 6.0 % | 35.7 % | 24.0 % | 27.4 % | -34.0 |
| **envsel** ws | 360 | **9.7 %** | 22.8 % | 7.2 % | 16.9 % | 6.9 % | 36.1 % | 23.6 % | 26.7 % | -33.4 |

Closest fresh pose to any held-out pose: env 2.23 deg (coordinates) / 2.04 deg (humerus orientation), envsel 2.07 /
2.03 deg; median 7.5 deg.

## 2. The tool: `tools/roller_env_polish.py`

Built in the first run (commit 1ff02ba). It goes through the verifier's harness and scores BOTH shapes the claim uses:
* a = fit on env FAST, scored in-sample on env;
* b = fit on Bench(60,160) FAST, worn FROZEN on env;
* obj = (a + b) / 2 at the 1 mm near-touch gap with the continuity knock-out.

It prices the alignment audit's four watches:
* knee window ang_min >= 26.8823;
* the drive read at PA_MAX 42;
* a contact-depth guard: 0.1 x (summed env depth - the verified config's own);
* workspace in-band at elevation 90-140, logged.

The other rules: stops are variables >= 5.0 with smlo read at +0.5, the whole reading at margin 5.5, K's stop B at
min(a1max, bk1 + bk2 - 5.5), O20 hubs, a claim-fit guard, +100 for a th margin under the reading's margin or a
dishonest drive, and the verifier's full-grid flood plus fresh-pose edges for continuity. 24 free parameters.

**Added in this run:**
* **`robust`: a flank synthesis-robustness margin.** It re-fits the priced config on Bench(60,160) with each flank
  parameter moved by one tolerance step, one at a time: beta +-1 deg, r_c +-0.25 mm, g +-0.05.
  * Every neighbour must synthesise (honest, drive not idle, pressure angles <= 42).
  * Every neighbour must keep a drive range >= the nominal's taken dK - 1 deg.
  * With `ENVP_ROBUST=1` the objective adds 5 points per failing neighbour. The penalty is graded so CMA can walk off
    the knife edge.
* **`classes`:** which workspace pose classes a config regains or loses against another (per-pose dumps).

## 3. Re-score on env (step 2)

Farm job `rlp-rescore-*`, continuity on: fit env FAST -> wear env EXACT, and fit Bench(60,160) FAST -> wear env EXACT.

| reading | fit env fast, in-sample | fit env -> env exact | fit Bench(60,160) -> env exact | env depth sum (mm), two fits | min th | verified (Bench(110,360)) | held out |
|---|---|---|---|---|---|---|---|
| verified as verified (nominal stops, PA 43, margin 5) | 22.84 (1 mm 23.79) | 22.76 (1 mm 23.71), reach 0.7095, ib14 0.875 | 21.37 (1 mm 24.25), reach 0.7071, ib14 0.8937 | 24.9 / 23.7 | 5.41 | 18.67 | 23.73 |
| audit-compliant (knee 26.88, smlo +0.5, margin 5.5, PA 42) | 23.08 (24.04) | 23.00 (23.96), reach 0.7048, ib14 0.875 | 21.87 (24.77), reach 0.700, ib14 0.8935 | 17.1 / 16.6 | 5.78 | 19.25 | 24.91 |

env sits between the verified bench and held out, as designed: 23.0 against 19.25 / 24.91.

The fit protocol matters on env too:
* On the plain gap the Bench(60,160) fit wears 1.1-1.4 points better on env than the env fit itself.
* At 1 mm it is 0.5-0.8 worse.
* The env fit takes in-band 0.875 against 0.894, and reach 0.705 against 0.700.

## 4. CMA on env (step 3) and the convergence gate

**Batch 1: 8 runs from the verified config** (knee window 26.88): 4 at sigma 0.3, 2 at 0.4, 2 at 0.5; popsize 8,
2 processes, patience 12, 1800 s each.
* An evaluation costs 43-60 s on a shared worker (4 jobs x 2 processes on 8 vCPU). The roller's cam synthesis makes it
  4-5x slower than the sidecar's.
* So the runs made 57-105 evaluations each, 592 in all. s1, s3 and v1 stopped on patience; the others hit the budget.
* x0 (the audit-compliant verified config): obj 24.45 (env 1 mm 24.04, env60 1 mm 24.86, env depth 16.26 mm).
  On envsel: 1 mm mean 29.875, depth 33.93 mm.
* Best: obj 23.238 (rlp-s2-g3-1), a gain of 1.21 on the objective.

**Batch 2: 3 flank-robust runs** (`ENVP_ROBUST=1`, from the task's "beta -178 only with a synthesis-robustness margin"):
* rlr-v1 from the verified config (sigma 0.3), 105 evaluations. 21 robust rows; best robust obj 24.04 at beta -174.8.
* rlr-b1 and rlr-b2 from beta -178 (sigma 0.3 / 0.4), 41 and 49 evaluations.
  * Before the resume, b1 had found no robust row and b2's one robust row had walked back to beta -173.9 (obj 26.0).
  * After a 1200 s resume (batch 5) they reached 73 and 81 evaluations. Every robust row (2 and 13) sits at beta
    -171.9 to -175.5; none is near -178. The best robust objective is 25.38 (b1, beta -175.5) and 26.02 (b2), worse
    than x0's 24.45.

**Gate** (`python3 tools/roller_env_polish.py gate`: best gained < 1 over the 2nd half of the tries, < 0.5 over the
last third, top-5 within 3):

| runs | tries | best | gain 2nd half | gain last third | top-5 spread | passes |
|---|---|---|---|---|---|---|
| batch 1 combined (by generation) | 592 | 23.238 | 0.0 | 0.0 | 0.95 | yes |
| all 11 runs (b1 / b2 resumed) | 851 | 23.238 | 0.0 | 0.0 | 0.84 | yes |
| each batch-1 run and rlr-v1 | 57-105 | 23.24-24.45 | <= 0.24 | <= 0.20 | 0.14-1.48 | yes |
| rlr-b1 / rlr-b2 after the resume | 73 / 81 | 25.38 / 26.02 | 3.8 / 4.0 | 0.0 / 0.0 | 4.7 / 1.1 | no (they left beta -178; section 7) |

**Caveat.** The gate passes, but with 57-105 evaluations in 24 dimensions it reads stagnation, not a converged
optimum. Final step sizes were 0.22-0.41 against 0.3-0.5 at the start. The objective's best (23.24) sits 1.2 under x0,
and its envsel transfer is poor (section 5).

## 5. Picks (committed before the claim, commit 6a33673)

The rule (`picks`):
* candidates = the best 15 rows of each run by the objective, with no penalty;
* a candidate may not be deeper than the verified config on envsel (33.93 mm);
* ranked on the envsel 1 mm mean over the two fits;
* each pick differs from every kept pick by >= 0.5 CMA scale units in some parameter.

| pick | row | obj | env 1 mm (env fit / env60) | envsel 1 mm mean (verified 29.875) | envsel depth (mm) | flank robustness (6 neighbours) |
|---|---|---|---|---|---|---|
| pick1 | rlp-s3-g5-3 | 25.21 | 23.46 / 24.85 | **27.92** | 22.5 | FAIL 3/6: drive range 44.5-46.5 vs 49.1 needed at beta +1, r_c +0.25, g +0.05 (synthesis holds) |
| pick2 | rlp-s2-g3-7 | 24.47 | 23.72 / 24.94 | 28.00 | 25.3 | FAIL 4/6: synthesis fails at r_c -0.25 (crank vs hub K) and g +0.05 (flank cusp) |
| pick3 | rlr-v1-g5-2 | 24.89 | 23.33 / 23.64 | 28.08 | 26.0 | **PASS** 6/6 (dK_lim 50.0 nominal, >= 46.0 at every neighbour) |

All three are small moves from the verified config: <= 1.2 CMA scale units in any parameter.
* pick1: s_arm 4.05 -> 4.41, smhi 16.8 -> 18.1, wd 66.9 -> 65.1.
* pick2: bk1 26.0 -> 26.9, r_lobe 8.24 -> 8.50, wa -10.7 -> -11.7.
* pick3: beta -173.5 -> -175.6, bk1 -> 26.8, smhi -> 18.2, zr 4.02 -> 3.77.
* smlo stays at its 5.0 floor in all three.

The objective's best rows (obj 23.24-24.0) all ranked worse on envsel than these picks. The envsel selection matters.

## 6. The claim (step 4): one farm batch, 15 jobs

The batch (`farm/jobs_claim.json`, `claim_*.json` + `_perpose.json`): verified as verified (knee 25.22) and with the
knee at 26.88 (`BESTam`, the baseline), plus the 3 picks. Each runs three protocols, all priced (margin 5.5, smlo
+0.5, PA 42), continuity flood on. The farm reproduces the local claims to the digit: BESTam 19.25 / 24.91.

| config | protocol | gap | 1 mm / 2 mm | reach | follow | ib14 | contact poses | depth sum / max (mm) | fold / slide | min th | horn PA | dK taken / lim | ws ib el 90-140 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **verified (BESTam)** | fit60 -> Bench(110,360) | **19.25** | 20.89 / 34.26 | 0.7194 | 1.0 | 0.8935 | 2 | 15.9 / 10.5 | 90 / 9 | 5.71 | 41.8 | 43.7 / 44.0 | 0.802 |
| verified (BESTam) | fit60 -> held out | **24.91** | 27.80 / 37.65 | 0.6691 | 1.0 | 0.8924 | 9 | 39.0 / 8.4 | 272 / 34 | 5.66 | 41.9 | 43.9 / 44.0 | 0.818 |
| verified (BESTam) | env -> held out | 26.72 | 27.38 / 36.70 | 0.6712 | 1.0 | 0.8734 | 10 | 50.3 / 9.9 | 271 / 32 | 5.53 | 41.6 | 44.3 / 45.0 | 0.806 |
| verified as verified (knee 25.22) | fit60 -> bench / held / env -> held | 19.25 / 24.92 / 26.50 | - | - | - | - | 2 / 10 / 10 | 15.9 / 48.4 / 50.3 | - | 5.71 / 5.66 / 5.53 | - | - | - |
| pick1 | fit60 -> Bench(110,360) | 21.88 | 23.66 / 57.21 | 0.7000 | 1.0 | 0.8894 | 3 | 10.8 / 9.7 | 90 / 15 | 7.05 | 40.3 | 44.0 / 47.5 | 0.837 |
| pick1 | fit60 -> held out | 25.07 | 27.41 / 57.14 | 0.6733 | 1.0 | 0.8877 | 10 | 54.2 / 11.2 | 260 / 41 | 6.08 | 41.9 | 47.3 / 47.5 | 0.824 |
| pick1 | env -> held out | 24.62 | 26.04 / 49.49 | 0.6754 | 1.0 | 0.8901 | 10 | 55.0 / 11.2 | 260 / 39 | 6.08 | 41.8 | 47.3 / 47.5 | 0.825 |
| pick2 | fit60 -> Bench(110,360) | 19.43 | 20.53 / 43.35 | 0.7111 | 1.0 | 0.9001 | 2 | 5.4 / 5.3 | 91 / 11 | 6.22 | 41.6 | 42.2 / 43.0 | 0.813 |
| pick2 | fit60 -> held out | **24.18** | 26.41 / 45.71 | 0.6702 | 1.0 | 0.8986 | 9 | 41.7 / 8.8 | 270 / 35 | 6.08 | 41.8 | 42.7 / 43.0 | 0.826 |
| pick2 | env -> held out | 25.94 | 26.61 / 33.68 | 0.6765 | 1.0 | 0.8746 | 9 | 41.7 / 8.4 | 264 / 35 | 5.65 | 41.9 | 44.2 / 44.25 | 0.809 |
| pick3 | fit60 -> Bench(110,360) | 21.64 | 22.85 / 54.70 | 0.7083 | **0.9636** | 0.8970 | 8 | 14.3 / 10.7 | 90 / 11 | 6.23 | 40.1 | 45.1 / 49.0 | 0.829 |
| pick3 | fit60 -> held out | 24.78 | 26.58 / 58.17 | 0.6796 | 0.9653 | 0.8947 | 19 | 59.3 / 12.2 | 256 / 37 | 5.56 | 41.2 | 47.4 / 49.0 | 0.821 |
| pick3 | env -> held out | 24.62 | 26.24 / 36.68 | 0.6828 | 1.0 | 0.8826 | 10 | 58.2 / 12.3 | 256 / 36 | 5.56 | 40.7 | 47.4 / 50.0 | 0.817 |

Continuity: the full-grid flood dropped no taken pose in any claim (connected = static on every row). Every taken
pose's own-state th margin is >= 5.53 (>= the 5.5 reading). Taken horn pressure angle <= 41.9, under the 42 read cap.

**Held-out gain over the verified config (BESTam):**

| pick | same protocol, env -> held | CAD shape, fit60 -> held | pick's own-fit vs the CAD's 24.91 | verified protocol | held-out depth vs 39.0 mm | robust gain (worse held-out fit) |
|---|---|---|---|---|---|---|
| pick1 | +2.10 | -0.16 | +0.29 (env fit) | -2.63 | +15.2 mm | -0.16 |
| pick2 | +0.78 | **+0.73** | +0.73 (fit60) | -0.18 | +2.7 mm | **+0.73** |
| pick3 | +2.10 | +0.13 | +0.29 (env fit) | -2.39 | +19.2 mm | +0.13 |

**Reading.**
* **The +2.10 is the fit-protocol artifact, not a better mechanism.** Under the env fit, the verified config itself
  falls 24.91 -> 26.72. pick1 and pick3 recover that drop and add 0.29.
* **pick2 is the only pick that gains under both fits** (+0.78 / +0.73).
  * Its gain is in-band: ib14 0.8924 -> 0.8986. Reach 0.6691 -> 0.6702 is one pose.
  * The verified protocol has it 0.18 worse (19.43). Held-out depth is 2.7 mm deeper (41.7), and 2 mm near-touch is
    8 points worse (45.7 vs 37.7): metal moves into the 0-2 mm shell, the same pattern as the sidecar's pick1.
  * Its flank is a knife edge: 4 of 6 tolerance neighbours fail synthesis.
* **pick1 and pick3 move metal deeper.**
  * They open K further: dK taken 47.3-47.4 vs 43.9, drive end 47.5 / 49-50 vs 44.0.
  * They press 15-19 mm deeper in sum held out (deepest 11.2-12.3 mm vs 8.4).
  * pick3 also loses clip follow: 0.9636, clip frames the verified config tracks.
* **The depth guard's proxy failed.** Every pick was shallower than the verified config on envsel (22-26 vs 33.9 mm)
  and is deeper held out (41.7-59.3 vs 39.0 mm). A summed-depth guard on a 360-pose draw is too noisy for the 5-10
  presses that make the held-out sum. The next polish should price depth on the press clusters themselves: overhead
  at elevation 150-165, and behind the body at elevation 60, plane -90..-65, axial 105-120.

## 7. Red team: the flank sits on a synthesis knife edge, the verified config included

`robust` and a finer one-parameter-at-a-time scan (`local/robust_verified_probe.json`,
`local/flank_margin_verified_probe.json`, Bench(60,160) fit, PA 42) measure how far each flank parameter can move
before the cam synthesis fails or the drive range falls under the taken opening:

| config | beta - / + (deg) | r_c - / + (mm) | g - / + | fails first |
|---|---|---|---|---|
| verified (BESTam, beta -173.46) | >= 3 / 1.5 | **0.10** / 0.25 | >= 0.10 / **0.02** | r_c -0.15: crank vs hub K clearance under 1.0 mm (it is 1.14 nominal); g +0.03: drive range 42.0 < 43.4 |
| probe beta -178 | 1.5 / >= 3 | 0.10 / **0.0** | 0.03 / **0.0** | r_c +0.05: flank cusp; g +0.01: flank cusp |
| pick3 (beta -175.64) | passes +-1 / +-0.25 / +-0.05 | | | dK_lim >= 46.0 at all 6 neighbours |

* **The verified config is 0.10 mm (r_c) and 0.02 (g) from its synthesis rules.**
  * The r_c edge is a clearance rule, the crank's 1.0 mm to hub K, so the verified 1.14 mm is close to it but not in
    contact.
  * The g edge is the PA-42 drive range.
  * Neither is a contact, but a built flank should be cut at a config with margin.
* **beta -178 is worse.** It sits 0.0 from a flank cusp on two parameters.
* **pick3 shows the robust region exists.** A robust config sits 2 deg of beta away (-175.6, r_c 15.52, g 2.415).
  It is not a better config held out (section 6).
* **The beta -178 robust runs (151 evaluations after the resume).** Under the robustness price both rlr-b runs walk
  away from -178:
  * all 15 robust rows sit at beta -171.9 to -175.5;
  * the best robust objective there is 25.38, against the verified x0's 24.45 and rlr-v1's 24.04.
  * So beta -178 cannot be cut with a +-1 deg / +-0.25 mm / +-0.05 margin anywhere near this config. The PA fix it
    offered (taken PA 39.9-40.2) is not buildable at that margin.
  * The b runs' gate fails on the 2nd half (3.8 / 4.0: the walk off the edge). Their last third gained 0. They are a
    measured direction, not an optimum.

## 8. What the polish regains, and the fold

The verified config loses 306 of 952 held-out workspace poses: 272 to the fold, 34 to the slide, and continuity drops
none. By class (`classes`, BESTam fit60 -> held):

| class | poses | lost | share lost | contact |
|---|---|---|---|---|
| across-body (plane >= 100, el >= 40) | 159 | 118 | 74 % | 0 |
| overhead (el >= 140) | 71 | 48 | 68 % | 5 |
| el 105-140 | 89 | 48 | 54 % | 1 |
| behind (plane < -30, el > 20) | 64 | 26 | 41 % | 3 |
| el 70-105 | 114 | 35 | 31 % | 0 |
| el 35-70 | 137 | 13 | 9 % | 0 |
| el 0-35 | 318 | 18 | 6 % | 0 |
| abs(axial) >= 150 (cross-cut) | 105 | 81 | 77 % | 0 |

What the picks change (`farm/classes_*.json`):
* **pick2, CAD shape:** +3 / -2 poses (net +1). It gains 1 behind, 1 at el 35-70 and 1 at el 70-105, and loses 2
  overhead.
* **pick1, env fit:** +11 / -5. It gains 3 across-body and 2 behind, and loses 2 overhead.
* **pick3, env fit:** +17 / -4. It gains 5 at el 0-35, 4 across-body and 2 at abs(axial) >= 150, and loses 1 overhead
  net.

No pick touches the fold in the classes that hold it:
* across-body: 114-118 of 159 still lost;
* abs(axial) >= 150: 79-81 of 105;
* overhead: 48-50 of 71.

The overhead class gets slightly worse in every pick. **Within this morphology's free parameters the fold is
geometric. A polish cannot buy it.** The 4.9-point distance to the hard goal is a morphology question: the
across-body / high-axial fold, as on the lead.

## 9. Verdict

* **Held-out gain over the verified config: +0.73** (pick2, the worse of its two held-out fits; also its CAD-shape
  number). This is under the 1-point rule, so no verifier run is needed. pick2 also loses 0.18 on the verified
  protocol, presses 2.7 mm deeper held out and has a knife-edge flank. **The verified config stays the CAD config.**
* The same-protocol env-fit number (+2.10, pick1 / pick3) is the fit-protocol artifact. The verified config under the
  env fit is 1.81 worse than under its own fit.
* For the CAD's flank:
  * do not cut beta -178;
  * the verified flank is 0.10 mm (r_c) / 0.02 (g) from its synthesis rules;
  * if the CAD wants a tolerance margin, pick3's flank values (beta -175.64, r_c 15.52, g 2.415) are robust at
    +-1 deg / +-0.25 mm / +-0.05. Pick3's full config is NOT better: it is a flank reference, not a polish pick. A
    flank-only change (seats and dyad unchanged) needs its own check.
* Hard goal: not met. Best held out 24.18 at 41.7 mm vs the goal's 22.0 at 35.66.

## 10. Commands

```bash
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/roller_env_polish/farm/jobs_rescore.json
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/roller_env_polish/farm/jobs_cma_only.json
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/roller_env_polish/farm/jobs_cma_robust.json
python3 tools/roller_env_polish.py gate $(ls docs/research/roller_env_polish/farm/cma_rl*.json | grep -v state)
python3 tools/roller_env_polish.py picks $(ls docs/research/roller_env_polish/farm/cma_rl*.json | grep -v state) --out docs/research/roller_env_polish/picks
CB_FOLD_MARGIN=5.5 python3 tools/roller_env_polish.py robust docs/research/roller_env_polish/picks/pick{1,2,3}.json --out docs/research/roller_env_polish/picks/robust_picks.json
python3 tools/roller_env_polish.py claimjobs docs/research/roller_env_polish/picks docs/research/roller_env_polish/farm/jobs_claim.json
RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 tools/cloud_run.py batch docs/research/roller_env_polish/farm/jobs_claim.json
python3 tools/roller_env_polish.py classes <dump A> <dump B> [out.json]
```

## Cost

All on exo-cpu1 (cpu3c / cpu5c, 8 vCPU, 4 jobs per worker); runpod_guard audit before each batch.

| batch | jobs | billed worker-s | $ (cpu3c / cpu5c) |
|---|---|---|---|
| env re-score | 2 | 643 | 0.052 / 0.060 |
| CMA, 8 runs | 8 | 4448 | 0.356 / 0.415 |
| flank-robust CMA, 3 runs | 3 | 3220 | 0.258 / 0.301 |
| claim | 15 | 1960 | 0.157 / 0.183 |
| robust resume (b1, b2) | 2 | 1063 | 0.085 / 0.099 |
| **total** | 30 | 11334 | **0.91 / 1.06** |

Plus cold starts (about $0.01 per new worker). Local: 2 processes for the robustness checks (about 2 min).

## Files

* `tools/roller_env_polish.py`: added `robust` (flank synthesis-robustness margin, `ENVP_ROBUST`) and `classes`.
* `docs/research/roller_env_polish/farm/`:
  * `jobs_*.json` (the batches);
  * `cma_rl*.json` (+ `.state.json`, logs);
  * `rescore_*.json`;
  * `claim_*.json` + `_perpose.json` (15 claims, per-pose dumps for the depth check);
  * `classes_*.json`.
* `docs/research/roller_env_polish/picks/`: `pick{1,2,3}.json`, `robust_picks.json`.
* `docs/research/roller_env_polish/local/`:
  * the first run's local claims;
  * `robust_verified_probe.json`, `flank_margin_verified_probe.json` (the flank margins).

# minarc-stop-knuckle-4r BDp: independent re-measure (2026-10-16)

**Verdict: NOT REFUTED. All four of the task's conditions hold under this verifier's own harness.**

**Claim under test** (rows/minarc-stop-knuckle-4r.json `kitrule_*`): variant B (pin knee + spring knuckle K in link 1),
config BDp. Both J2 stops sit at the 5-deg J1-J3 kit margin. The stop is a physical dowel in a slot on q2 (slot -24.98 ..
100.84 deg). Hub K's cap is 6 mm taller. Params: `minarc-kitrule/params_floorBD5_phys_cap6.json`.

**Harness** (`minarc-bdp-remeasure.py`, written for this check): it imports the claim's model unchanged and does not
import the claim's harness or the earlier re-measure verifier.
- **Frozen hand-over.** The harness hands over every attribute the fit creates, found by diffing `__dict__` before and
  after the fit (21 attributes). It does not use a hand-written list. It then asserts that f, fK, tr, the knee centre m,
  the q2 stops and the hub K crown (18.25) are identical to the fit.
- **Per-pose checks from the member frames.** These cover the joint axes, th, the effective dyad, the J1-K-J3 sub-chain,
  K's own dyad, q2 vs the slot, and dK one-sided within stop B.
- **Spring-equilibrium scan.** For each forced pose: is there a smaller |dK| with J2 anywhere inside the slot?
- **Hub K cap, sampled independently.** Lattice of 1 mm x 3 deg plus the top disc, checked against the exact skin and
  against every non-adjacent member.
- **Near-touch re-score.** Includes the cap samples.
- **Flood fill.** The harness's own fill, plus a contact-aware variant.
- **Runs.** Fit Bench(60,160) FAST, then wear EXACT, O20 x 4. Raw JSON is in `minarc-bdp/` (the farm runs are in
  `minarc-bdp/farm/`). The farm cost was about $0.06 in total.

## Results

| check | claim | this verifier | pass |
|---|---|---|---|
| (1) frozen exact Bench(110,360), margin 5, continuity applied | 19.06 (93.07), near-touch 26.15, 15 poses < 1 mm, min 0.05 | **19.06 (93.07)**: reach 0.725, follow 1.0, in-band14 0.8951, in-band10 0.5969, contact 0.0107; near-touch **26.15**, 15 poses < 1 mm, min 0.05 mm (clip 30/150/-60) | yes (difference 0.00) |
| (2) min J1-J3 margin, each taken pose in its own state | 5.01 | bench **5.015** (state A plain dyad 5.124; stretched effective dyad 5.015, sub-chain 16.91, K dyad 21.36); held out 5.007; all 1014 grid poses taken 5.007; 0 poses < 5; 0 folded poses taken | yes |
| (3a) kinematic continuity, full 1432 grid, strict seeds (elevation 0, K on stop A) | 1041/1041, 0 islands | **1041/1041**, 0 islands, 915/915 edges pass (no rule / jump / branch refusals), one knee branch; 0 of 261 taken bench ws poses dropped | yes |
| (3b) contact-aware (taken nodes only; not run by the claim) | - | **1014/1014** taken grid poses connected, 0 islands, 888/888 edges | yes |
| (4) held out, 1154 disjoint poses | 23.24 (near-touch 28.31) vs H1 31.39 | **23.24** (91.55), near-touch 28.31, 0 of 656 dropped; **H1 31.39** (near-touch 34.66) in the same harness and benches | yes (beats H1 by 8.15) |
| (5) margin-10 reading (not run by the claim) | - | **22.40** (91.85): reach 0.714, follow 1.0, in-band14 0.870, contact 0.008; near-touch 26.21; min margin 10.017; 1014/1014 connected; slot narrows to -10.39 .. 90.59, K opens to 48.5 deg | H1 28.21 at margin 10 (re-measure verifier, same protocol) |

H1 in this harness on Bench(110,360), margin 5, is 27.20 (near-touch 31.75), which matches its fit60 verified number.

## Extra measurements (red team)

- **The forced state is the spring's state.** For all 59 forced bench poses (138 held out, 95 at margin 10), no q2
  inside the slot gives a smaller K opening than the model's J2-on-stop solution. The modelled state is the mechanism's
  minimum-spring-energy state.
- **Hub K cap.**
  - Skin: minimum 0.41 mm on one taken bench pose. The near-touch count already includes it, and it stays at 15. Held
    out the minimum is 1.01 mm.
  - Parts: minimum 1.34 mm, to link 1b metal away from K's axis. That is above the 1 mm rule.
- **Closure.** The largest joint-axis error is 0.016 deg, and J3 read from link 2 and from member 3 agrees to 0.016 deg.
  0 poses were knocked out.

## Issues (none of them overturns the claim)

1. **The margin sits exactly at the rule.** The minimum is 5.007-5.015 deg because the stops were placed at exactly
   5.00. The physical slot has no machining tolerance in the model, so a slot cut ~0.02 deg long breaks the 5-deg rule.
   - 99 of 371 taken bench poses sit under 10 deg (247 held out). They are the near-edge feel the user asked to
     red-team (docs/research/fold-stop-feel.md).
   - A build should place the stops at 5 deg plus the slot tolerance. The margin-10 reading of 22.40 bounds the cost:
     about 3.3 points for 5 extra degrees.
2. **The folded stop is never engaged** (0 folded poses anywhere). The folded side of the dowel slot and of K is
   untested by the bench.
3. **On forced poses the plain dyad (a1, a2) is 11.4-11.6 deg past its own fold.** This is legitimate because K opened
   and the effective dyad holds 5.0. It does mean the margin holds only because K opens: a sticky or slow K spring
   would drive J2 into the stop with the chain near-singular.
4. **The contact-aware fill checks only the nodes against the skin.** The intermediate 2-deg slerp steps are checked
   kinematically, not for skin contact (the same limit as the earlier re-measure verifier).
5. **Fit-to-wear loss is 6.8 points** (fast 12.25 to exact 19.06).
6. **K is sensed, so the skeptic's ruling of 4 active DOF stands.** Complexity is 33 against H1's 2.75. This is not a
   bench issue, but the golden target is a score of at least 95 at complexity near 0.

## Next

BDp is confirmed as the bench leader under the current rules. In-sample it is 19.06 against H1's 27.20 under the same
protocol, and held out 23.24 against 31.39. It is still 5.3 gap points short of the golden 13.75. The cross-fit final
polish (2-fold, held-out-only objective) is the next lever, with the stops treated as design variables at 5 deg plus
the slot tolerance.

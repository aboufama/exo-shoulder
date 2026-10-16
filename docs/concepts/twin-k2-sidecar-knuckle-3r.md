# twin-k2-sidecar-knuckle-3r - a second slaved knuckle K2 on link 2, opened past the lead's drive wall

## Deeper-version answers (written first, 2026-10-16 21:30 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the space before the mechanism:
   the twin knuckle puts a 5th O20 stack within ~22 mm of hub 2 on the bend side, beside a crank that already lives there
   (the lead's drive 1). So the first measurement is not the law but the *sweep* - which bodies pass over hub 2's
   neighbourhood as q2 turns (crank 1 on link 1b, crank 2 + hub K2 on link 2a) - and whether hub K2 can park in band
   on the posterior-lateral cap at all. Then: run the spec's law-only gate and the metal with drive 2 OFF as a control,
   so the cost of the K2 stack alone is separated from the cost of its drive; and use a *track* law (least K2 opening
   that keeps m3e at smt2) so the extension is monotone - the lead's 267 taken poses cannot change.
2. **Rawest material.** The bench's posed skin (CB requirement along every hub ray, exact path on Bench(110,360)), the
   clip frames themselves, and the lead's own per-pose IK (th, a1e, dK, m3e per pose) - not the proposer's crude
   parking map. The drive wall is re-derived from the lead's law table (m3e hits 5 at t 23.7, th 109.5, dK 38.5), not
   copied from the judge's note.
3. **Methods / tools.** The lead's model (sidecar-longdyad-knuckle-3r.py, verified code) as the parent class; the
   split-knuckle-twosided-3r machinery (5-hub fit, L2a / L2b straps, hubK2 cap, 5-hub collision pairs) re-based on it;
   a vectorised (t, dK2) grid for the twin law; tools/cloud_run.py for the sweep; the lead's frozen protocol
   (fit Bench(60,160) fast, worn on Bench(110,360) exact) for the claim.
4. **What, other than me, shows the number is right.** The bench (concept_bench), the lead's own verified number
   reproduced through this file with K2 off (control), the per-part in-band / pair counts the bench reports, and a red
   team pose list (the poses K2 opens on, the crank-crank and hub K2 - hub 1 pairs).

(The measured record follows below; it is appended as the screen runs.)

## What was built (docs/concepts/models/twin-k2-sidecar-knuckle-3r.py)

The verified lead's model (sidecar-longdyad-knuckle-3r.py at its A1 best_params, inlined) as the parent class, plus:

- **K2** on link 2 at `bk3` from J2 / `bk4` from J3 on side `sK2` (O20 MR117-2RS stack, 12.25 + a 6 mm clock-spring cap,
  member 10 = link 2a hub 2 -> K2; member 2 = link 2b K2 -> hub 3 with the J3 housing). Code names follow
  split-knuckle-twosided-3r (L2a = hub 2 -> K2), i.e. swapped against the catalogue's 2b / 2a wording.
- **The twin law** (`TDesign.law2`, a (t, dK2) grid): K follows the lead's lin law and DWELLS at `dK1cap` (43.0 = the
  lead's RSSR range end, rod vs hub 2, measured by its own model); K2 = the least opening that keeps m3e >= `smt2`
  (+ an optional linear ramp `kK2` from the wall), monotone, capped by lobe 2's pressure angle (45 deg), crest
  <= HUB_R + 1.5, K2 dyad margin 5, `dK2max` 40 (rod RSSR range), rate dq2/dth <= 3.45, no lift-off. With smt2 = 5 K2
  starts exactly at the lead's wall (measured from the lead's own law table: m3e = 5 at t 23.7, th 109.5, dK 38.5 -
  the judge's correction, not law end - 2). Stretched poses are solved by inverting th2(t), then q1 / q3 closed form.
- **Metal**: the 5-hub fit / greedy / link rows / 5-hub collision pairs of split-knuckle-twosided-3r re-based on the
  lead (drive 1 = the lead's per-pose RSSR, its own range, `_truncate`), plus drive-2 metal: crank-2 boss O10 x 6 on
  link 2a off the hub2-K2 line at HUB_R + 6 from both axes (there is no room between the hubs), its long arm lying
  sideways, O3 rod 2 to a horn lug of link 2b at K2 (r_h2 >= 15.5), M2 ball-link rings. `drv2 = 0` switches drive-2
  metal off (the spec's gate control). STATED SIMPLIFICATION: drive 2 is sampled rigid at its rest pose (exact on every
  clip frame and on the lead's taken poses, where K2 sits on stop A; on won poses the rod's swing is not swept - this
  can only flatter the design).
- Kinematics check: with the K2 law off (`k2 = 0`) the model takes exactly the lead's poses (fold 26 / slide 6 on the
  fit bench, as the lead); the unchanged parts keep the lead's in-band within the greedy's different pose set (hub 1
  1.0, hub K 1.0, hub 2 0.967, crank 0.94, rod 0.92 vs the lead's 0.995 / 0.981 / 0.989 / 0.908 / 0.892).

## Gate (1): law-only, Bench(110,360), lead IK (`gate` mode and scratch lawgrid.py)

| bk3 | bk4 | dA2 = a2e max - 61.89 | kin ws (lead 0.742) | won ws | overhead /28 (lead 10) | law end |
|---|---|---|---|---|---|---|
| 20 | 59 | 7.4 | 0.775 | +12 | 11 | rate |
| 20 | 62 | 10.0 | 0.783 | +15 | 11 | rate |
| 22 | 59 | 11.1 | 0.783 | +15 | 11 | rate |
| 22 | 62 | 13.5 | 0.794 | +19 | 11 | m3e (dK2 40) |
| 24 | 56 | 11.5 | 0.783 | +15 | 10 | rate |

K2 on the other side (`sK2 = -1`) wins 0 poses at every seat (opening it never lengthens a2e faster than th grows).
K2 mid-link or near hub 3 (bk3 34-45) opens only 0.2-0.4 deg before m3e binds: its gain is near zero there, as the
proposer said. The law ends on "rate" (dq2/dth > 3.45): past the wall th rises only through K2 (dth/dq2 -> 0 at the
straight dyad), so q2 must turn more than 3.45 deg per deg of th. **The spec's gate (1) fails narrowly in reach
(0.783 vs 0.785 at dA2 <= 12) and clearly in overhead (11 vs 12 of 28): the prize is not overhead poses** - of the 15-19
won poses only 1 is at elevation >= 140; the overhead poses are lost to other causes (fold on the folded side, slide,
contact), not to the stretched wall.

## Gate (2): the metal (fit bench Bench(60,160) fast, then frozen exact)

Coarse farm sweep, 192 configurations (bk3 18-28 x bk4 50-62 x kK2 {0, 1.5} x drv2 {0, 1} x dK1cap {40, 43}),
docs/concepts/sweeps/twin-k2-sidecar-knuckle-3r.json, against the lead's **10.30** through the same parent code:

- drive-2 metal OFF (upper bound): best **27.79** fast, but K2 never opens on a taken pose (k2_idle, dishonest); best
  with K2 working **29.94** (bk3 24 / bk4 50; 3 won workspace poses); hub K2 in band **0.09-0.23**, link 2a 0.14-0.41.
- drive-2 metal ON (the real embodiment): best **78.04** (k2_idle) / **112.26** with K2 working; crank 1 vs crank 2 on
  47-78 poses, crank 2 / rod 2 / horn 2 0.0-0.03 in band (stacked above crank 1's boss they stand 21-26 mm off the skin).
- Frozen exact Bench(110,360) of the best honest chain-only config (bk3 24 / bk4 50, drive 2 OFF): **38.49**
  (reach 0.675, follow 0.90, ib14 0.805, contact 0.014; near-touch 41.32 at 1 mm, 56.21 at 2 mm; min metal 0.12 mm;
  overhead 6/28) vs the lead's verified 18.91 (reach 0.725, overhead 8/28). K2 won 10 fold poses (fold 76 vs 86) and
  lost 37 more to parts (crank 1 vs link 2a on 35, crank 1 vs hub K2 on 4); hub K2 0.12 in band (median 18.3 mm),
  link 2a 0.19, link 2b 0.54 (the lead's single link 2: 0.75).

### Why hub K2 cannot park (rawest data: the per-pose need along K2's ray)

At bk3 20 / 24 the level hub K2 must stand at is set by overhead workspace poses (elevation 120-135) and an overhead
clip frame (132): need 62.3-65.9 mm, while its median need is 51-52 mm - a 12-15 mm spread, so only 10-19 % of clip
samples are within 12 mm. Hub 2, 20-24 deg away, has a 6 mm spread (F 60.3, median 54.4, 0.96 in band). K2 on the bend
side of link 2 sits over the part of the cap that the raised deltoid lifts overhead; the proposer's crude map
(0.76-0.93 at bk3 18-20) counted taken + won poses only and missed those overhead frames.

### The jam, the pinch and the optimistic number (red team)

- **Jam**: drive 1's crank (on link 1b beside hub 2, lying sideways) against link 2a: the K2 dog-leg (rest interior angle
  psi0 92-121 deg) routes link 2a sideways off the J2-J3 arc, straight through the zone the crank occupies, on 35 of 360
  frozen poses; with drive-2 metal on, crank 1 vs crank 2 on 47-78 of the fit bench's poses - two cranks beside one hub
  sweep through each other as q2 turns (risk 3 of the spec, measured).
- **Pinch**: 0.12 mm min metal on taken poses (frozen exact, chain-only).
- **Optimistic number**: every chain-only figure above omits drive 2's metal; the honest embodiment is 50-80 points
  worse on the fit bench. The roller-flank embodiment (merged twin-flank-k2-knuckle-3r) keeps the same K2 hub, links 2a /
  2b and a crank-plus-arm beside hub 2, so the chain-only figure bounds it too: it cannot rescue the morphology.

## CMA-ES on the farm

Bench(60,160) fast, the lead's objective (1 mm near-touch gap; dishonest = +100: K2 idle, hub2-K2 clash), 16 free parameters: bk3, bk4, kK2,
smt2, smlo, dK1cap, the lead's drive-1 beta / La / r_h, J2 az2 / el2, J3 wd / wa / b3, drive 2 r_h2 / La2. 8080
configurations in all (192 coarse + 7888 CMA, ~$0.5 of farm time).

| run | metal | evals | best fast | reach | ib14 | follow | contact | convergence gate (gain 2nd half / last third / top-5 spread, score pts) |
|---|---|---|---|---|---|---|---|---|
| A | drive 2 ON (the morphology) | 1049 | **60.86** | 0.644 | 0.753 | 0.783 | 0.013 | 0.00 / 0.00 / 0.87 - converged |
| B | drive 2 ON | 1601 | 20.32 -> **375** | - | - | - | - | LOOPHOLE (below) |
| C | drive 2 OFF (upper bound) | 1153 | 18.69 | 0.794 | 0.886 | 0.917 | 0.022 | 1.44 / 0.17 / 0.03 |
| D | drive 2 OFF (upper bound) | 1057 | **18.09** | 0.788 | 0.876 | 0.917 | 0.011 | 0.60 / 0.60 / 0.04 |
| E, F | drive 2 ON | 705, 553 | 20.32 (= B's corner) | - | - | - | - | invalid: shipped before the fix, restarted in the loophole |
| G (from D) | drive 2 OFF (upper bound) | 617 | **16.97** | 0.794 | 0.875 | 0.917 | 0.006 | D+G: 0.62 / 0.41 / 0.12 - converged |
| H (from C) | drive 2 OFF (upper bound) | 1153 | 17.37 | 0.794 | 0.877 | 0.917 | 0.011 | C+H: 0.48 / 0.33 / 0.03 - converged |

**Red team, CMA loophole (found and closed 21:53):** run B walked K2 to bk3 19.5, where the two O20 hubs are 21.3 mm
apart and link 2a has no strap sample outside both hub radii; `_rod2_metal` returned early on an empty link and drive 2's
metal vanished. Fixed (drive 2 is built from hub 2's strap level when link 2a is empty) and the judge's clearance gate
added (hub 2 - hub K2 >= 22.0 mm at the fitted levels, else dishonest). B's 20.32 re-measures **375** (crank 2 vs hub K2
on 136 poses, crank 1 vs crank 2 on 30, crank 2 vs hub K on 18). Runs A, C, D never entered that corner (bk3 23-28,
hub2-K2 26.8-30.2 mm) and re-measure identically through the fixed file (60.86, 18.09).

### Frozen exact Bench(110,360) (fit on Bench(60,160) fast, shape frozen; the lead's verified protocol)

| config | frozen gap | reach | follow | ib14 | contact | near-touch 1 / 2 mm | min metal | overhead /28 | fold / slide / parts / contact |
|---|---|---|---|---|---|---|---|---|---|
| lead (verified, for reference) | 18.91 | 0.725 | 1.0 | 0.897 | 0.011 | 20.00 / 34.03 | 0.28 | 8 | 86 / 7 / 2 / 4 |
| A, drive 2 ON (best honest) | **67.32** | 0.572 | 0.782 | 0.753 | 0.030 | 70.97 / 82.35 | 0.05 | 4 | 93 / 5 / 71 / 9 |
| G, drive 2 OFF (converged upper bound) | **25.64** | 0.722 | 0.918 | 0.875 | 0.022 | 27.28 / 48.40 | 0.27 | 6 | 87 / 12 / 2 / 8 |
| D, drive 2 OFF (upper bound) | 27.84 | 0.711 | 0.918 | 0.875 | 0.033 | 29.49 / 56.41 | 0.22 | 4 | 87 / 12 / 2 / 12 |
| coarse bk3 24 / bk4 50, drive 2 OFF | 38.49 | 0.675 | 0.900 | 0.805 | 0.014 | 41.32 / 56.21 | 0.12 | 6 | 76 / 8 / 39 / 5 |

At D / G, K2 opens on 25 / 18 frozen poses (dK2 up to 17.8 / 20.0, a2e up to 71.9 / 71.2) but the fold count is the lead's
(87 vs 86): the search set smt2 9-10.3, so K2 starts before the wall and spends its stroke on poses the lead already took, while its
hub (0.57 in band, median 13.4 mm) and the stretched contact (12 poses) take the points. At A the K2 law is reduced to
a token (won 0 on the frozen bench) and drive 2's metal stands 22-29 mm off the skin (crank 2 / rod 2 0.0 in band) with
crank 1 vs crank 2 on 70 poses.

## Verdict: DEAD (both embodiments)

The kinematic prize is real but small and not overhead (+15-19 workspace poses, overhead +1 at dA2 10-13.5 on the lead's
own IK), and the metal that buys it costs more than it wins, at every seat the sweeps reached:

1. **Hub K2 cannot park** (the spec's likely killer, confirmed from the per-pose need along its ray): 0.09-0.57 in band
   against the 0.85 gate; its level is set by overhead frames (elevation 120-135) where the raised deltoid lifts the
   skin under the bend side of link 2 by 12-15 mm over its median.
2. **Two drives beside one hub sweep through each other**: crank 1 (link 1b) vs crank 2 (link 2a) on 30-78 poses,
   crank 1 vs the dog-legged link 2a / hub K2 on 4-35; stacking crank 2 above crank 1 puts drive 2 22-29 mm off the
   skin (0.0 in band). The roller-flank embodiment keeps hub K2, links 2a / 2b and a crank-plus-arm beside hub 2, so the
   drive-2-OFF bound (25.64 frozen vs 18.91, converged) bounds it as well.
3. **The kinematic gate itself fails**: kin 0.783 vs 0.785 at dA2 <= 12 and overhead 11 vs 12 of 28; the twin law ends on
   "rate" (past the wall dth/dq2 -> 0, so th rises only through K2).

Complexity 75 (tools/simplicity.py on the record in the row) vs the lead's 49: it would have had to buy >= 2 frozen points;
it loses 6.7 (converged upper bound G: 25.64 frozen) to 48.4 (honest A: 67.32 frozen).

## New knowledge (predicts beyond this morphology)

- **A second slaved knuckle near an existing O20 hub inherits that hub's neighbourhood conflicts**: two O20 stacks need
  >= 22 mm centre to centre (>= 21 deg at F 60), and at that distance a hub on the BEND side of link 2 sits over skin
  that overhead elevation lifts by 12-15 mm, so its in-band collapses (0.1-0.6) - the skin under the bend side is not the
  skin under hub 2.
- **Two strap-level drives cannot share one hub's skirt**: any crank fixed to link 1b and any crank fixed to link 2a
  within ~25 mm of hub 2's axis sweep through each other over the q2 range (~140 deg); the only escape (stacking)
  costs the whole drive's in-band. A second q2-driven spare must be driven from somewhere else (or not at all).
- **The stretched wall is a slope, not a wall**: past the drive wall dth/dq2 -> 0, so a q2-slaved spare can only add
  th at the K2 gain; with a 3.45 rate cap the law ends after ~10-15 deg of th whatever dA2 the dyad allows.
- **CMA exploits an empty-sample corner**: a model that skips a part's metal when its host link has no samples gives
  the search a free exit; every drive-metal routine must build from a fallback level, never return early.

## Audit (2026-10-16 ~22:40 UTC, independent re-measure): death STANDS

- **Reproduced through the committed model file**: honest run A 60.86 on Bench(60,160) fast (why: fold 33, parts 31 - all
  CRK-CRK2), frozen exact Bench(110,360) **67.32** (reach 0.572, follow 0.782, ib14 0.753, ib10 0.465, contact 0.030;
  near-touch 70.97, min metal 0.05 mm; fold 93 / parts 71 / contact 9; K2 wins 0 frozen poses). The upper bound G reproduces at 16.97 fast.
- **Convergence gate** (recomputed from the sweep): honest run A best 60.86 (the sweep's best "gap" entries of run A, 23.47,
  are dishonest - K2 idle or hub2-K2 < 22 mm, objective +100 - correctly excluded); bound runs D+G and C+H converged;
  B/E/F loophole entries are logged as dishonest. Gate holds.
- **Modelling bugs / over-strict checks looked for**: the K2-idle rule (K2 must open on >= 1 taken pose) and the
  hub2-K2 >= 22 mm gate are the morphology's definition and O20 geometry, not over-strictness; the 1 mm near-touch
  objective is the round rule. Crank 2 is placed on one side only (+ax); that side choice was not swept, but it cannot
  matter: the bound with drive-2 metal deleted already loses.
- **New decomposition (measured)**: at bound G's seats, turning the K2 law OFF (hub K2 metal kept) gives 18.21 fast vs
  16.97 with it ON - **the K2 law is worth 1.24 fast points and 0 frozen fold poses** (87 vs 86). The lead scores 10.30
  through the same parent, so hub K2 + the dog-legged link 2a/2b cost ~8 fast points (hub K2 0.47-0.53 in band, link 2a
  0.57-0.60), and drive 2's metal another ~44 (crank 2 / rod 2 0.0 in band at 22-29 mm, CRK-CRK2 on 31 poses).
- The task's legacy criterion (within 10 of the champion 68.93 on Bench(60,160)) is met trivially (60.86), but it is not
  the kill line in round 9: the lead's verified 18.91 is, and no embodiment of this morphology can reach it.

**One line**: the second slaved knuckle's law buys at most 1.24 fast points (0 frozen fold poses) while its O20 hub over
the overhead-raised deltoid costs ~8 and a second drive in hub 2's skirt ~44; dead, converged.

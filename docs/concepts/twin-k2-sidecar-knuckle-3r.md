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

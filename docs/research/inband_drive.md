# An in-band RSSR K drive: making the long-stroke drive's metal cost little (2026-10-17)

User, 2026-10-17: "i want higher scores! get to work and do it well!" / "do not stop until i say, keep pushing".
The long-stroke row (docs/research/longstroke_drive.md) measured the prize: with the hub-2 lobe at its PA-42 law (kK 3.0)
the long-dyad chain with the drive's metal DELETED (LS_GHOST=1, attribution only) is **18.25 frozen / 21.11 held**, against
the verified leader slipper-nose-knuckle-3r's 18.49 / 23.45; the same law through the real rod drive is 25.83, and the
real rod re-searched at the steep law 23.31 / 27.67. This task: make the drive's metal cost little.

Files: model `docs/concepts/models/inband-rssr-knuckle-3r.py` (the long-stroke model loaded unchanged, its RSSR metal
re-placed by switches eta / clay / zc / bl_c / bl_h, defaults = the parent), row `docs/concepts/rows/inband-rssr-knuckle-3r.json`,
scripts and data `docs/research/inband_drive/` (attribute.py, screen.py, make_jobs.py, farm/), preview
`docs/concepts/viz/concepts/inband-rssr-knuckle-3r.js`.

## Depth answers (written before the work)

1. **What a top packaging / mechanism designer would do that the brief does not ask.**
   - Price the drive in the bench's own currency before moving metal: the gap is 100 x (0.90 - in-band) + 100 x (0.90 -
     reach) + 100 x contact, and in-band is POOLED over every sample point of the taken clip frames. So a part's cost is
     (its out-of-band points) / (all points) - the bell crank's 73 samples at 0.62 in band are worth ~3 points by
     themselves, the rod's 17 almost nothing - and a contact pose costs twice (it leaves reach AND enters contact).
   - Ask why the crank is high before moving it: it is high because it is STACKED (its pin is in link 1b, so its boss sits
     on link 1b's top + 0.15 running gap), not because it is far from the body. The fix a packaging designer reaches for
     first is a joggled bracket: give the pin a tab one layer DOWN, so the crank runs in link 1b's own layer beside the
     strap - the same thing every hub stack in this project does.
   - Keep stage 1 (the lobe law) untouched: the follower geometry (pivot 16 mm from hub 2's axis, s_arm on the rim lobe)
     carries the law and its pressure angle; repackage only stage 2's metal, so the kinematic claims stay the parent's.
   - Treat the ball-link offset as the second stack: an M2 ball's centre sits 3 mm off the arm face, the rod rides on
     it, so the rod is a layer above the crank; a stud pointing to the skin (ball under the arm) drops the rod 6 mm.
   - Check what the brief did not ask: does the new bracket (the ear) itself cost band or contact, and does the lower
     metal trade in-band for near-touch / contact (the 2 mm objective) - i.e. measure contact depth, not only counts.
2. **The rawest material.** The per-pose signed skin distance of every sample point of every drive part on the frozen
   exact Bench(110,360) and the 952 held-out poses (attribute.py), split by part (crank boss / arm by radius, rod,
   ball-link sockets, horn lug, ear) and by pose class (elevation bands), plus which part makes each contact pose and how
   deep. From that table the bench's score is recomputed with any part deleted - the exact per-part LS_GHOST with the fit
   unchanged.
3. **Methods / tools.** The model's own switches (the parent's LS_DRIVE / LS_GHOST; this row's IB_GHOST per part and the
   repackaging switches whose defaults reproduce the parent to the digit), concept_kit's exact skin (CB_EXACT=1), fast
   screens on Bench(60,160), CMA-ES on the farm (tools/concept_cma.py, 2 mm and 1 mm near-touch objectives, law held steep
   by LS_KK_MIN 2.7 and the drive range by LS_STROKE_MIN 55) to the convergence gate (cma_summary.py), the frozen claim
   protocol, the parent's RSSR range scan (transmission >= 48 = PA <= 42 at both ball ends) unchanged.
4. **What else shows it right.** The control (defaults reproduce the long-stroke row: fast 42.91 / plain 19.40), the
   frozen exact bench and the held-out bench, the per-pose dump (tools/alignment_paired.py), the alignment auditor
   against slipper-nose, and an independent verifier re-running section 7's commands.


## 0. Lead correction taken on board mid-task (2026-10-17 ~09:35, after the long-stroke audit)

The ghost's 21.11 held out was partly a leak (kK 3.0 / s_arm 4.0 / r_lobe 8.5 were picked from a law table that counted
Bench(110,360) AND the 952 held-out poses), and on the frozen protocol's own 2 mm fit objective kK 3.0 ranks last of four
linear laws. So the honest target became: beat slipper-nose 18.49 / 23.45 with real metal and a LEAK-FREE pick. What this
changed here: (a) three law-free CMA runs were added (cma3: no kK floor, no stroke floor, seeds = the long-stroke row's own
fit-bench CMA bests g65d / s65n2d / r75a); (b) the pick rule was committed before any cma3 result or frozen number
(`picks.json`, 09:40): the lowest 2 mm objective on the FIT bench among cma3; (c) cma1 / cma2 (kK >= 2.7, stroke >= 55,
seeded at the hand-picked k30 / k27b law) are reported as a secondary, never the claim; (d) contact depth is reported per
pose class; (e) the spring is read against R17; (f) the mechanism record is counted so tools/simplicity.py's topology flag
is clean (joints 9 = the long-stroke row's 10 minus the nose / flank pair it replaced; loops 3 = 9 - 6).

## 1. Attribution: where the long-stroke drive's ~7.6 points went (rawest material, measured before any change)

`attribute.py` wears a config with the frozen protocol, keeps every sample point's signed skin distance per pose per part
(rigid metal by name, link straps, contact-only samples split by part), and recomputes the bench's own gap with any set of
parts deleted. Check: it reproduces the model (k30 parent 25.82 vs 25.83 reported; all drive parts deleted 18.25 = the
LS_GHOST run; fast bench 19.40 = 19.40).

**The long-stroke row's real rod drive at the k30 law, frozen exact Bench(110,360)** (`farm/claimA/k30_attr_bench.json`;
gap 25.83 = in-band 4.11 + reach 18.06 + contact 3.66):

| part deleted (attribution only) | gap | change | in-band term | contact poses | what the part costs |
|---|---|---|---|---|---|
| none (the real drive) | 25.82 | - | 4.11 | 14 | |
| bell crank (73 pts / pose, in band 0.62, median 13.6 mm, p90 15.1) | 22.10 | **-3.72** | 2.01 | 11 | 2.10 in-band (38 % of its points > 14 mm; the boss region r < 5 mm only 0.43 in band, median 14.2) + 3 low-arm contact poses it makes ALONE (0.01-0.6 mm deep, elev 0-15, axial -45..-135) |
| ball-link sockets (32 pts, 0.59, median 11.8, p90 18.1) | 23.20 | **-2.62** | 3.11 | 11 | 1.00 in-band + 3 overhead contacts alone (0.6-2.2 mm, elev 135-165) |
| rod (17 pts, 0.58, median 12.8) | 25.29 | -0.53 | 3.58 | 14 | in-band only |
| horn lug (20 pts, 0.95, median 5.9) | 26.03 | +0.21 | 4.32 | 14 | nothing: it RAISES the pooled in-band; its 3 contacts are shared with hub K (pose 237, elev 165, 14.7 mm deep) |
| crank + sockets | 19.31 | -6.51 | 0.83 | 8 | |
| all drive metal (= LS_GHOST) | 18.25 | **-7.57** | 0.31 | 7 | |

By pose class, the crank's out-of-band metal is the LOW ARM: elev < 60 holds 68 of the 110 clip frames and the crank is
in band only 0.50 there (median 14.0), 0.92 at elev 90-120. Held out (952, `farm/attr3/attr_k30_parent_held.json`, part
level): the same real drive at the k30 law is **28.86** (the row had only the ghost's 21.11 on file); crank 0.62 in band,
sockets 0.58, 13 socket contacts (47 mm summed), 6 horn contacts.

So the drive's metal cost is two things: the crank is a layer too HIGH (it is stacked on link 1b: underside = link 1b's
top + 0.15), and the ball-link sockets sit high AND poke the skin overhead. The rod and the horn are not the problem.

## 2. Repackaging candidates, least complexity first (fast Bench(60,160), the parent's k30 config unsearched, then searched)

Model switches (every default = the parent): eta (pivot azimuth about hub 2, radius kept 16 mm so the lobe law is
unchanged), clay 1 (crank on a joggled EAR of link 1b, in link 1b's own layer), zc (crank layer over link 1b's underside),
bl_c / bl_h (M2 ball above 0 / below 1 / on a RADIAL stud screwed into the end face 2, ball centre in the arm's mid-plane,
socket cone gated at 30 deg). Files `out/screen{1..4}_*.jsonl` (`show.py` prints them).

| # | candidate | complexity | fast 2 mm / plain | crank in band | rod / sockets in band | contact poses | reading |
|---|---|---|---|---|---|---|---|
| 0 | parent: crank stacked on link 1b, balls on top | 28.5 | 42.91 / 19.40 | 0.62 (13.6 mm) | 0.59 / 0.58 | 3 + 2 | the control (= the long-stroke row) |
| 1 | pivot moved OFF link 1b's strap (eta +-40..90), crank stacked | +0 | 48.05-275 / 23.49-275 | 0.01-0.85 | | | worse: off the strap the pivot sits on link 1b's hub-2 EYE, which is 3.5 mm higher (lev 63.2 vs 59.7); \|eta\| >= 60 loses transmission or hits hub 2 (the report's own suggestion fails as stated) |
| 2 | **crank on a joggled ear in link 1b's layer (clay 1, eta 0)** | +0 (a tab of link 1b) | 49.43 / **16.90** | **0.93 (11.3 mm)** | 0.68 / 0.72 | 4 + 2 | THE in-band lever: in-band 0.858 -> 0.894; the ear itself 1.00 in band (8.2 mm) |
| 3 | ear + pivot off the strap (eta +-40..60) | +0 | 54-111 / 24-69 | 0.04-0.93 | | 2-30 | worse (same eye-level reason) |
| 4 | ball under the crank tip (bl_c 1) | +0 | 82.04 / 50.41 (108.65 / 60.02 on the ear) | | 0.92 / 0.94 | 29-39 | sockets 6.5 mm under the arm reach the skin |
| 5 | ball under the horn (bl_h 1) | +0 | 216 / 173 | | | 93 | at hub K the skin is 6 mm away |
| 6 | **radial ball stud at the crank tip (bl_c 2), on the ear** | +0 (same M2 ball link) | 68.70 / 22.07 | 0.92 | **0.90 / 0.89** | 9 + 2 | rod and sockets into the band (in-band 0.9035) but unsearched it pokes the skin; the search fixes that (below) |
| 7 | radial stud at the horn (bl_h 2) | +0 | 161-275 | | 0.98 / 0.89 | 16-36 | the horn end's socket cone (> 30 deg at rest) or skin: dead |
| 8 | shorter crank, same law by phasing (La 18-22, r_h 13-13.5) | +0 | 275-375 | | | | the horn ball at r_h 13-13.5 clashes with hub K on every pose (1 mm part pair) |
| 9 | horn lowered (hl 0 / 1.5) | +0 | 151.34 / 78.13, 133.49 / 17.44 | | | 5-42 | horn at hub K's base touches the skin |
| 10 | horn merged into link 1a | - | not built | | | | measured unnecessary: the horn is already in band (0.95, 5.9 mm) and deleting it RAISES the gap (+0.21) |

## 3. The search (farm CMA-ES, tools/concept_cma.py, Bench(60,160) fast, crank on the ear)

`python3 docs/research/longstroke_drive/cma_summary.py docs/research/inband_drive/farm/cma_cma*_*.json`; every batch's
combined convergence gate passes (cma1 4566 evaluations 0.00 / 0.00 / 0.32; cma2 1540 0.00 / 0.00 / 0.09; cma3 5470
0.17 / 0.03 / 0.00; the claim run cma3 p 1449: 0.04 / 0.00 / 0.00). Best fit-bench 2 mm objective per run:

| batch | run | stud | objective | best 2 mm | plain | dyad bk1 / bk2 / a1max | kK | reading |
|---|---|---|---|---|---|---|---|---|
| cma3 (leak-free, law free) | k (g65d seed) | axial | 2 mm | 17.47 | 15.04 | 26.7 / 38.5 / 60.2 | 1.91 | |
| | l (g65d) | radial | 2 mm | 19.50 | 17.00 | 26 / 38 / 59 | 1.59 | |
| | m (s65n2d) | axial | 2 mm | 17.21 | 14.56 | 26.8 / 41.1 / 62.9 | 1.94 | |
| | n (r75a) | radial | 2 mm | 16.58 | 13.75 | 26 / 38 / 59 | 1.50 | |
| | o (g65d) | axial | 1 mm | 18.38 (1 mm 13.82) | 14.64 | 26.8 / 42.0 / 63.9 | 1.67 | |
| | **p (s65n2d) = THE PICK** | **radial** | 2 mm | **16.47** | **12.79** | **26 / 38 / 59** | **1.79** | ties slipper-nose's 16.47 (plain 13.00) on the same objective |
| cma1 / cma2 (law floor 2.7, stroke >= 55; leaky seed) | f | axial | 2 mm | **16.35** | 11.71 | 26 / 38 / 59 | 2.70 | the secondary |
| | g / j | radial | 2 mm | 16.62 / 16.70 | 12.07 / 13.23 | 26 / 38.2 / 59.2 | 3.17 / 2.70 | |
| | a / d (k30 / k27b long-dyad seeds) | axial | 2 mm | 18.60 / 18.45 | 13.86 / 14.76 | 26 / 38 / 59, 26 / 39.9 / 59.3 | 2.70 / 3.12 | seeded on the long dyad, both walk back to 26 / 38-40; the steep law costs ~2 points on the fit objective |

Every run, leak-free or not, walks the K dyad back to the parents' 26 / 38 clamp. With the drive's metal now nearly free,
the fit bench still does not want the long dyad: the long-dyad lever is not a metal problem.

## 4. Claim columns (frozen protocol; pick committed 10:10 before any number; farm claimA-D)

| config | K used | frozen exact Bench(110,360) | reach (overhead) | in-band | contact (poses, summed / max mm) | near 1 / 2 mm | min th margin | held out (952) |
|---|---|---|---|---|---|---|---|---|
| slipper-nose verified (reference) | 46 | **18.49** | 0.725 (8/28) | 0.8955 | 0.0054 (2, 14.75 / 9.01) | 20.12 / 33.02 | 5.006 | **23.45** (10 contacts, 46.1 / 9.05 mm) |
| long-stroke real rod at k30 (parent, control) | 51.8 | 25.83 | 0.719 | 0.859 | 0.037 (14, 35.9 / 14.7) | - | 5.389 | **28.86** (new) |
| **PICK cma3 p (in-band RSSR, 26 / 38 / 59, kK 1.79)** | 45.8 | **18.87** (score 93.14) | 0.722 (8/28) | **0.8971** | 0.008 (3, **9.86 / 9.72**) | 19.96 / 34.12 | 5.231 | **23.21** (9 contacts, **23.20 / 8.71** mm; th margin 5.045) |
| robust build (r_h +0.25, eta +1) | 45.8 | **18.83** | 0.722 | 0.8975 | 0.008 (3, 9.83 / 9.69) | 19.92 / 34.12 | 5.231 | **23.16** |
| secondary cma1 f (law floor 2.7, axial studs) | 49.3 | 18.21 | 0.728 (8/28) | 0.8954 | 0.0053 (2, 10.17 / 10.08) | 20.94 / 35.49 | 5.133 | 23.42 (11 contacts, 27.6 / 8.71) |

- Per-pose dumps (lead's rule, `tools/alignment_paired.py dump --out`): `farm/claimA/inband-rssr-knuckle-3r_{bench,held}_perpose.json`,
  recomputed 18.87 / 23.21 = the claim.
- Continuity flood: static 18.87 = connected full 18.87 (0 dropped), knn 21.39, bench graph 51.74 (slipper-nose 18.49 / 20.16 / 50.11).
- **Attribution of the pick** (`farm/claimA/p_attr_bench.json`): all drive metal deleted 18.58, i.e. **the drive's metal now
  costs 0.29 points** (was 7.57): crank 0.29 (in band 0.71, median 13.2: the radial arm's mid-span r 5-15 mm still
  climbs over link 1b's strap, in band 0.23-0.26 there), sockets 0.22, rod 0.03, the ear -0.52 (it helps: 1.00 in band
  at 9.5 mm), horn -0.08. The 3 contact poses are not the drive's: they stay with the drive deleted (the overhead pose 237
  presses hub K / horn / rod together, 9.7 mm).
- **Paired per pose vs slipper-nose** (`paired.py`, 4000 paired bootstraps within kind): bench +0.39 (90 % CI [-0.28,
  +1.54], P better 0.22; 1 workspace pose fewer, 1 contact more at 0.04 mm), held **-0.24** ([-0.68, +0.17], P 0.77; 1
  / 1 discordant taken poses, 1 contact fewer), pooled -0.06 ([-0.44, +0.39], P 0.55). **Parity, not a lead.** The
  low-arm extreme-rotation class (elev < 60, |axial| >= 120) has 0 contacts on either wear; overhead contact depth held out
  10.8 mm summed vs slipper-nose's 34.3.
- Spring vs R17: 1.79 x (0.08 + 0.015 x 0.811 rad) = **0.165 N.m at J2**, 1.10 / 1.37 N at a 150 / 120 mm cuff lever: 17 %
  of R17's 1 N.m and 22-28 % of its 5 N, static only (the dynamic twist needs judge/dynamics.py on a CAD).
- Complexity `tools/simplicity.py --score` **28.5** (no flags) vs slipper-nose 22.25 and the long-stroke row's 30.5.

## 5. Red team (the pick)

| attack | result |
|---|---|
| **Pose that jams** | none in range: the RSSR scan stops at transmission 48 (PA 42 at both ball ends), the range ends on the law (65.8 deg) before that; over the taken K (<= 46.4) transmission >= 52.0 (PA <= 38.0). The radial crank stud's socket tilt peaks at **25.5 deg** (robust 25.9) against the 30 deg cone assumed for an M2 ball link: a short-neck link (~25 deg) would bind at the top of the taken range - specify a long-neck stud, or fall back to the axial stud (secondary f: 18.21 / 23.42). |
| **Lift-off ~2.5 N** | stage 2 (rod, two ball links) is bilateral; stage 1 (lobe follower) is held by K's clock spring as on the lead (static factor 2.4 against the exo's own weight about K); a cuff force cannot drive the chain's self-motion. Spring felt at the cuff 1.10-1.37 N. |
| **Knife edge** (+-1 deg beta / gam / eta, +-0.25 mm La / r_h / s_arm / hl / zc / r_lobe, 16 corners; `out/tol_p.jsonl`) | the pick parks the horn ball 0.25 mm from a 1 mm part pair: r_h -0.25 and its 9 corners lose every pose; eta -1 costs +7.1 (the pivot leaves link 1b's low strap for the higher hub-2 eye). **The robust build (r_h +0.25, eta +1) passes all 34 neighbours** (2 mm 16.47-17.64, plain 12.50-13.05; `out/tol_rob.jsonl`) and measures 18.83 / 23.16. |
| **Held out survives** | +4.34 bench -> held (reference +4.96); the held-out edge over slipper-nose is -0.24 with a CI crossing 0. |
| **The optimistic number** | the ghost's 18.25 / 21.11: with leak-free selection the same family measures 18.87 / 23.21 with metal and 18.58 frozen without the drive's metal. |
| **Point that pinches** | bench pose 237 (elev 165, plane 15, axial -60): hub K + horn + rod press 9.7 mm (slipper-nose loses the same pose at 9.0 mm and pose 264 at 5.7 mm, where this row touches 0.09 mm); held 9 contact poses, deepest 8.7 mm, half slipper-nose's summed depth. |

`python3 tools/alignment_audit.py audit inband-rssr-knuckle-3r --ref slipper-nose-knuckle-3r`: **WATCH, 0 gamed** (only
"held_out: no verified bench gap on the row" - it is not verified yet); near-touch ok (plain 18.87, 1 mm 19.96, 2 mm
34.12), dominance ok (plain -0.38, 2 mm -1.10 vs the reference), continuity ok, fold margin 5.045 ok, sampling ok
(sample- vs part-weighted in-band -1.54), complexity 28.5 recomputed = row, rules ok. Its contact-depth check reads the
row's top-level fit number (16.47) and so finds no dump that reproduces it; the dumps reproduce the frozen 18.87 / 23.21.

## 6. Verdict

- **The drive's metal no longer costs: 7.57 -> 0.29 points** on the frozen bench, at zero added complexity. Two moves did
  it: the bell crank on a joggled ear of link 1b, so it runs in link 1b's own layer instead of stacked on it (crank in band
  0.62 -> 0.93 at the same config), and the crank-tip M2 ball on a radial stud in the arm's end face, so the rod rides in
  the arm's mid-plane (rod / sockets 0.58 -> 0.87 / 0.85). The report's own suggestion (move the pivot off the strap)
  fails as stated: off the strap the pivot lands on link 1b's hub-2 eye, 3.5 mm higher.
- **The hard goal is not met:** frozen 18.87 / held 23.21 (robust 18.83 / 23.16) against <= 18.0 / <= 22.0. **No part's
  metal makes it impossible any more** (all drive metal deleted: 18.58). The wall is the CHAIN under leak-free selection:
  the fit bench picks the short dyad 26 / 38 / 59 at kK 1.79 (fold 88 = slipper-nose's 88, K used 45.8), and the steep-law
  long dyad that made the ghost 18.25 / 21.11 ranks worse on the fit objective (18.45-18.60 vs 16.47).
- **Against the leader: parity** (pooled paired -0.06, CI [-0.44, +0.39]) at +6.25 complexity; held-out contact depth
  halved (23.2 vs 46.1 mm summed). Not a new leader.
- **New knowledge.** (1) A stacked bell crank costs ~3.7 points by itself and its height comes from the stack, not the
  geometry; a joggled ear recovers it free. (2) On link 1b the strap near hub 2 is 3.5 mm LOWER than the hub-2 eye, so a
  pivot is best on the strap, not beside the eye. (3) A radial ball stud keeps an RSSR rod in the crank's plane; its
  socket cone (25.5 deg used of ~30) replaces the rod's lean as the binding angle. (4) With the metal free, the fit bench
  still returns to the 26 / 38 dyad: the long-dyad lever is a selection question (which bench sees the stretched poses),
  not a packaging one.
- **Next (cheapest first):** (a) the jittered workspace-envelope search bench CLAUDE.md asks for (never the held-out
  poses): the only leak-free instrument that can decide whether the steep law / long dyad is real; this row's in-band
  drive is ready to be searched on it (all switches in the model); (b) for any RSSR-family CAD, build the crank on the
  ear and the radial crank stud (the gen-6 CAD measured the same 3.97 mm boss rise this row removes); (c) a 25 deg ball
  link check (catalogue cone) before CAD; (d) the spherical-coupler drive (round 11) can reuse attribute.py unchanged.

## 7. What a verifier must re-run

```bash
P="$(python3 -c "import json;print(json.dumps(json.load(open('docs/research/inband_drive/picks.json'))['primary_cma3_p']['params']))")"
CB_EXACT=1 python3 docs/concepts/models/inband-rssr-knuckle-3r.py frozen "$P" out_bench.json   # 18.87
CB_EXACT=1 python3 docs/concepts/models/inband-rssr-knuckle-3r.py held "$P" out_held.json      # 23.21
python3 docs/concepts/models/inband-rssr-knuckle-3r.py flood "$P" out_flood.json               # 18.87 / knn 21.39 / bench 51.74
CB_EXACT=1 python3 tools/alignment_paired.py dump inband-rssr-knuckle-3r bench|held             # per-pose dumps (row best_params = the pick)
# the control: defaults reproduce the long-stroke row (fast 42.91 / plain 19.40; frozen 25.83)
python3 docs/concepts/models/inband-rssr-knuckle-3r.py check '{"La": 25.7026, "s_arm": 4.0, "r_h": 15.491, "beta": -147.3923, "gam": 22.4633, "hl": 2.929, "zr": 2.091, "r_lobe": 8.5, "bk1": 30.0377, "bk2": 42.9378, "a1max": 67.9755, "smhi": 15.2738, "kK": 3.0}'
# attribution (exact): per part ghosting recomputed from one wear (must reproduce the model's gap)
CB_EXACT=1 python3 docs/research/inband_drive/attribute.py "$P" bench out_attr.json docs/concepts/models/inband-rssr-knuckle-3r.py   # 18.87; all drive metal deleted 18.58
python3 docs/research/inband_drive/paired.py docs/research/inband_drive/farm/claimA slipper-nose-knuckle-3r                           # paired vs the leader
python3 tools/simplicity.py --score "$(python3 -c "import json;print(json.dumps(json.load(open('docs/concepts/rows/inband-rssr-knuckle-3r.json'))['mechanism']))")"   # 28.5
```

Cost: exo-cpu1 only, never GPU (attr1 timed out on unbatched exact distances - fixed; cma1 / cma2 / cma3, attr2 / attr3,
claimA-D). runpod_guard balance $29.19 (09:06) -> $27.99 (10:10) for every agent on the account; this task's batch lines
sum to ~$1.4 at the worst-case per-worker billing.

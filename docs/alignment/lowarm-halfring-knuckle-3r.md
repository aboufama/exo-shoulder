# Alignment audit: lowarm-halfring-knuckle-3r

First audit of this row (discovery round 14, slice r14-B: screened 01:42, verified 02:26 UTC 2026-10-18). Run
02:28-02:50 UTC on the box (at most 2 niced processes, load 12-19 from other agents; the farm was not used: the CPU-farm
approval window closed 2026-10-17 ~17:20 UTC).

- **Checks:** `docs/alignment/lowarm-halfring-knuckle-3r.json` (tool VERSION 2026-10-17.6, `--ref conecut-knee-knuckle-3r`).
  The tool crashed on this row (its `best_params` is a JSON string, see NEW-string-params), so the checks and the re-wear
  ran through the new adapter `tools/alignment_strparams_adapter.py` (decodes the string in memory and lays it over the
  model's `CELL_B`, exactly as the row's verifier does; the tool, the model and the row are unchanged).
- **Findings:** `docs/alignment/lowarm-halfring-knuckle-3r.findings.json` (9: 1 gamed, 8 watch).
- **Re-wears and probes written by this audit** (the model ran unchanged):
  - `remeasure/lowarm-halfring-knuckle-3r_bench.json`: frozen exact Bench(110,360) re-wear with near-touch at 1 / 2 / 3 mm,
    the metal histogram of taken clip frames, the band read 3-14 mm and coordinate spans. Reproduces 17.96 exactly (reach
    0.7306, ib14 0.8978, contact 0.008, 373 taken); near-touch 1 / 2 / 3 mm 20.14 / 34.84 / 86.40 (lead 19.92 / 34.84 /
    86.16); band read 3-14 mm 18.16 (lead 18.34); closest metal 0.048 mm; clip metal above 14 mm 10.22 % (lead 9.88 %);
    link 2's own in-band 0.709 (lead 0.731); knee angle 59.27-105.94 deg, dK span 45.61 deg. 623 s.
  - `remeasure/lowarm-halfring-knuckle-3r_probe_bench.json`: `tools/alignment_wear_probe_model.py` through the adapter
    (unscored workspace in-band, overhead and raised-arm in-band, reach by elevation, own-state fold margin). Reproduces 17.96; 546 s.
  - The held-out re-wear was started and stopped after 2.5 min (box at load 19; it needs ~15 CPU-min). The verifier's
    held per-pose dump (`remeasure/lowarm-halfring-knuckle-3r_held_perpose.json`, recomputes 22.70) is used for every
    held-out number below.

- **Ledger entry (appended 2026-10-18T02:43:22Z, by auditor, run `audit:lowarm-halfring-knuckle-3r`, git f804972):
  verdict GAMED**, tool verdict watch, claim v_gap 17.96. Reason items: continuity (tool, watch), judgement:P1 (gamed),
  judgement:T1, R3, M5, M3, S3, S5, G4, NEW-string-params (watch).

## Verdict: GAMED (as a lead claim), claim v_gap 17.96 (score 93.47), held out 22.70

The verified 17.96 is honest arithmetic: the verifier reproduced it, the per-pose dump recomputes it, every tool check is ok
except the family's carried continuity watch. What is gamed is the RANK it buys. 17.96 is the lowest
verified bench gap on the dashboard, 0.32 ahead of the lead conecut-knee-knuckle-3r (18.28), and under the user's
plain-gap rule that reads as a new lead. But:

1. **It was picked on the bench it is claimed on.** The link-2 root lift (h 1.5 / r_full 14 / L 9.836) is the minimum of
   794 frozen-exact surrogate configs scanned on Bench(110,360) exact itself (`docs/concepts/sweeps/lowarm-halfring-knuckle-3r.json`:
   min 17.96, p10 18.07, median 18.42, max 19.30; 251 of 794 under 18.28).
2. **It does not hold out.** On the held-out set (never searched) the same frozen design reads 22.70 against the lead's
   22.38 under the same frozen-exact harness: paired +0.32 WORSE (in-band +0.33, reach +0.11, contact -0.11; CI90
   [-0.34, +0.68], P(better) 0.26; pooled +0.13 worse, P 0.42;
   `remeasure/lowarm-halfring-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json`). The lift is worse held out than the
   design's own no-lift cell A too (22.70 vs 22.64).
3. **The bench edge is one 0.048-mm graze.** The only discordant bench pose is 316 (plane 60 / elev 150 / axial -105):
   the lead presses 1.235 mm in, this design's link 2 runs 0.05-0.37 mm over ~18 mm of skin. Every scan config that beats
   the lead clears 316 by 0.014-0.197 mm; the proposer's own pre-registered 0.2-mm clear reads 18.41, behind the lead.

So the number ranks the design above a design that is better on the poses no search saw. The proposer and the verifier
both wrote "NOT a lead change"; the dashboard does not carry that (no `leader_ruling`, first in the verified ranking),
and the ledger now does. **Action for the lead:** record a `leader_ruling` on the row ("not a lead: in-sample graze at
pose 316, held out behind"), or claim cell A (18.28, a tie with the lead at complexity 16.5 against 18.5) or the
held-out number. Either resolves the gamed finding; nothing about the design itself has to change.

What is genuinely good here: cell A (half ring + low arm, no lift) ties the lead at 18.28 on the bench with complexity
16.5 against the lead's 18.5, spring-free (desmo drive, no clock spring), and its held out reads 22.64 (proposer, same
code path) against 22.38. That is the honest reading of this round's knuckle lens: simpler at a tie, IF the dwell hold
can be built (M5 below).

## What the wearer gets (measured)

| quantity | this design (cell B) | lead conecut-knee | file |
|---|---|---|---|
| overhead reach (elev >= 140) taken | bench 9/28, held 19/71 | 8/28, 18/71 | *_perpose.json |
| raised-arm reach (elev >= 90) taken | bench 48/113, held 124/300 | 47/113, 123/300 | *_perpose.json |
| the overhead pose gained | bench 316 at **0.048 mm**; held 820 at 0.94 mm | 316 pressed 1.235 mm in; 820 0.18 mm in | *_perpose.json |
| taken poses with metal < 1 / 2 / 3 mm | bench 4 / 34 / 106; held 12 / 71 / 216 | 3 / 33 / 105; 13 / 71 / 217 | *_perpose.json (min of min_mm, cmin) |
| near-touch gap 1 mm / 2 mm (bench) | 20.14 / 34.84 | 19.92 / 34.84 | verifier; remeasure/conecut-knee-knuckle-3r_bench.json |
| in-band 2-14 mm (scored clips) | bench 0.8978 (under the 0.90 floor), held 0.8967 | 0.9012, 0.9000 | paired file |
| in-band 2-10 mm (the aim) | bench 0.5682 | 0.5739 | rows |
| workspace in-band (unscored ws poses) | 0.8634 | 0.8676 | probe files |
| workspace in-band elev 90-140 | 0.8283 | 0.8315 |
| workspace in-band overhead (elev >= 140), metal samples < 2 mm | 0.9279, **1.18 %** | 0.9359, 0.22 % | probe files |
| workspace in-band below elev 90 | 0.8671 | 0.8716 | probe files | probe files |
| contact poses, summed / deepest | bench 3, 14.92 mm, deepest **9.47 mm** at 237 (plane 15 / elev 165 / axial -60, the crank); held 13, 43.67 mm, deepest **10.39 mm** at 683 (45 / 165 / -30) | bench 4, 20.24 mm, deepest 8.93 at 237; held 14, 60.97 mm, deepest 9.86 at 683 | audit json contact_depth; *_perpose.json |
| fold margin th (own state) | min 5.181 bench / 5.11 held; with the claim's own K play 5.088 / 5.017, 0 poses dropped | 5.181 | verifier v3 / v4 |
| springs | none (desmo K drive, spring-free) | K clock spring | row mechanism |
| stops | J2 / J3 dowel stops; crank stop PAD on link 1b (unsampled) | J3 dowel | row |
| dwell hold (K play in the dwell) | **0.638 deg vs the 0.25 gate (fails; 0.292 at tight tolerances)** | - | verifier lowarm_fit |
| cuff twist | not measured (no CAD, no R17 run for this row) | not measured | - |
| near-singular postures | chain carried: m_sub at K rest < 1 deg on 50 of 205 rest bench poses (parent desmo-conecut) | same family | remeasure/desmo-conecut-knuckle-3r_msub_rest_bench.json |
| continuity | connected_full 17.96 / 22.70 (0 lost); kNN 19.64 / 30.93; bench graph 49.98 | - | verifier connected |
| complexity | 16.5 (recomputed 16.5) | 18.5 | audit json |

Note on contact depth: the summed depth is lower than the lead's (x0.74 bench, x0.72 held; T5 ok), but the two deepest
presses got deeper (bench 237: 9.47 vs 8.93 mm; held 683: 10.39 vs 9.86, 610: 9.82 vs 9.13). These sit on the crank,
which the low arm (zr 4.03 -> 2.0) brought 2 mm closer to the skin. Metal 9-10 mm into the arm overhead is a block, not a
graze; it was a block on the lead too.

## Findings (`lowarm-halfring-knuckle-3r.findings.json`)

1. **P1, gamed: in-sample tuning, behind held out.** Evidence above (Verdict 1-2). Why not better: the scan chose the lift on
   the poses it is scored on; on the 1154 held-out poses the lift costs in-band (link 2's root rides 1.5 mm higher on
   every pose) and the lead is ahead. Action: a `leader_ruling` on the row, or claim cell A / the held number.
2. **T1, watch: metal parked just past the 0-mm cutoff.** The whole bench edge is pose 316 at 0.048 mm; at a 0.1-mm cut the
   best scan config is 18.24 (+0.04 over the lead), at 0.2 mm 18.41 (behind). Report only (user decision (3)).
3. **R3, watch: best-of-794 without the spread.** The headline is the scan minimum; the row and dashboard do not carry p10
   18.07 / median 18.42.
4. **M5, watch: the dwell hold fails the claim's own gate.** 0.638 deg of K play in the dwell vs 0.25 (runout 0.176 +
   concentricity 0.088 + pad lap 0.335 + slot 0.04). The th margin survives it (V4), but its effect on metal position at
   the near-touch poses (316 at 0.048 mm, 139 at 0.072 mm) is unmeasured, and the proposed fix (a preloaded pad) adds a
   drag the wearer pushes through, also unmeasured.
5. **M3, watch: the promised clash check V5 was never run.** The verifier's docstring lists the lifted link 2 vs the crank /
   tip plate / hub-2 crown; no code implements it and no output has it. Link 2's root went up 1.5 mm while the crank's
   free span came down 2.03 mm.
6. **S3, watch: the crank stop pad is unsampled metal.** Probably harmless (it sits under the arm, covered by link 1b), but
   its height and its clearance to the arm in the forced region are not measured.
7. **S5, watch (carried): continuity needs the envelope stepping stones** (kNN held 30.93 vs 22.70).
8. **G4, watch (carried): near-singular sub-dyad at K rest** in this chain (parent's m_sub < 1 deg on 50 of 205 rest poses).
9. **NEW-string-params, watch: a row format the instrument cannot read.** `best_params` is a JSON string on this row only;
   the auditor's rules check and re-wear crashed, and a tolerant reader would silently wear the model's defaults (CELL_B
   has l2_rfull 16.0, the claim 14.0).

## Checks the tool ran, and where my reading differs

Tool verdict (after the re-wear was on file): **watch**, one reason, continuity (held kNN flood loses 8.23). The first run,
before the re-wear, also read near_touch / dominance / sampling as watch for want of data; with the re-wear on file they
read ok: near-touch 1 / 2 / 3 mm 20.14 / 34.84 / 86.40 with 16.88 points in the 1-2 mm shell (< 25); dominance vs
conecut-knee plain +0.32, 2 mm +0.00; sampling sample-weighted 0.898 vs part-weighted 0.905 (thin parts ring2 4, plate
8, L1a 8 samples); idle ok (dK 45.61 deg, knee 46.67 deg). held_out ok (+4.74, under the +6 line), fast_frozen ok,
contact_depth ok (x0.74 bench, x0.72 held), fold_margin ok (5.11), complexity ok (16.5), reporting ok, judge_change ok,
rules ok.

Where my reading differs: `held_out` compares the design's held number with its OWN bench number (+4.74, ordinary for
this family). It cannot see that the design and the lead swap order between bench and held out, which is the P1 finding.
`dominance` reads 2 mm only; at 1 mm and 3 mm this design is behind the lead, at 2 mm level. `reporting` compares the row,
the verifier and the dashboard NUMBERS (they agree); it does not read whether a row the verifier called "not a lead" is
displayed above the lead.

## Numbers I could not get, and why

- Held-out re-wear with the deep audit (near-touch gaps, metal histogram, coordinate spans held out): stopped after 2.5
  min to keep the time box on a box at load 19 (~15 CPU-min needed); the verifier's held per-pose dump stands in (the
  near 1 / 2 / 3 mm pose counts above), and the held probe was not run for the same reason.
- The V5 clash (lifted link 2 vs crank / tip plate / hub-2 crown): needs a per-pose body-to-body distance on the worn
  model; not built in this time box.
- Metal displacement under the dwell / forced K play at poses 316 and 139: needs a K-perturbed re-wear of those poses.
- Cuff twist, R17 drag of a preloaded pad: no CAD or dynamics run exists for this row.

## Proposals (not applied; none feeds the verdict)

- **A lead claim must name its search bench.** When a config is chosen on the claim bench itself (a frozen-exact scan of
  Bench(110,360)), the leader comparison uses the held-out number. Measured effect: of the sweep files of the seven
  verified rows nearest the top (this row, conecut-knee, slipper-nose, trimlug-k165, desmo-conecut, minarc-stop,
  roller-longdyad), only this row (794 configs) and trimlug-k165 (5 frozen-exact + 5 held configs) tag configs as
  scanned on Bench(110,360); the others carry no bench tag (conecut-knee 352, slipper-nose 3763, desmo-conecut 146,
  minarc 14437, roller-longdyad 7236 configs, all untagged), so their status is unknown, which is itself the gap the
  proposal closes. On this row the leader comparison moves from 17.96 vs 18.28 (ahead) to 22.70 vs 22.38 (behind).
- **A leader_ruling field is mandatory for a verified row whose verdict text says "not a lead".** The dashboard reads the
  field, not the free text. Measured effect: of the verified rows with v_gap <= 18.6 (this row 17.96, conecut-knee 18.28,
  slipper-nose 18.49, trimlug-k165 18.51), three say "not a lead" / "no new lead" in their text and none carries a
  `leader_ruling` in morphs.json; only this row sits AHEAD of the lead, so only its displayed rank changes. (The one row
  that does carry a ruling, inband-rssr-knuckle-3r "tie", shows 18.33 on the dashboard while its row reads status
  'screened' with no v_gap.)
- **New catalogue entry R5, "a row format the instrument cannot read":** the audit tool should coerce or reject a string
  `best_params` (one row today). It is a change of the instrument, so it is a proposal for the tool's owner, not done here.
- **Pre-registered clearances are part of the claim.** When the proposer pre-registers a clearance (here 0.2 mm at pose
  316) and the claim misses it, the claim row carries both numbers (17.96 graze / 18.41 robust) and the leaderboard uses
  the pre-registered one. Effect: this row 17.96 -> 18.41.

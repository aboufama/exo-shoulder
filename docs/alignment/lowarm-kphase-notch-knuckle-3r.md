# Alignment audit: lowarm-kphase-notch-knuckle-3r

Audited 2026-10-18 (~16:33-17:05 UTC) for discovery round 15, slice r15-B. Reference: the 3-active lead
conecut-knee-knuckle-3r. The parent, lowarm-kstop-knuckle-3r, is compared throughout because this design is that chain
plus one change. Instrument: `tools/alignment_audit.py` (VERSION 2026-10-18.1). New audit files (all read-only on the
models):
- `tools/alignment_remeasure_kphase.py`: re-wear through the verifier's harness with its corrections off.
- `tools/alignment_neartouch_dumps.py`: near-touch and reach readings from per-pose dumps.
- `tools/alignment_mu_probe_kphase.py`: friction red-team probe.

Checks: `docs/alignment/lowarm-kphase-notch-knuckle-3r.json`. Findings: `docs/alignment/lowarm-kphase-notch-knuckle-3r.findings.json`.

## Verdict: WATCH. Claim v_gap 18.47 (score 93.28); held out 22.87

The ledger tool printed WATCH: 5 tool checks and 12 judgement findings, all watch, none gamed (see "Ledger" below).

The number is real but thin. It is 0.18 behind the lead on the bench and 0.50 behind held, so nothing here touches the
leaderboard. What it claims over its parent is a 0.22 bench edge (18.47 vs 18.69, all in-band, from a shorter crank
arm). That edge rests on a 0.4 deg pressure-angle margin, a 0.135 deg dowel margin and a notched, clocked O20, and it
does not survive the readings the claim did not run:
- Held out: 22.87 against 22.88, a tie (P(better) 0.44).
- At the family's red-team friction mu 0.17: 18.75 against 18.69, behind by 0.06 (pose 313 lost to the shorter stroke).
- At 2 mm near-touch: equal on the bench (34.84) and 0.02 behind held.
- With the dowel 0.14 deg low: 18.75 (pose 313 cut).

No finding reaches 'gamed'. The friction and dowel readings are tightenings of the protocol (proposals A and B), not
the claim's harness. The same-harness reversals (held 2 mm, +0.02) are inside the paired noise and come from one to
three poses.

**The re-wear reproduces the claim.** This audit re-wore the claim with the model and the verifier's harness unchanged,
corrections off, and got:
- +0.264 deg wear: 18.39.
- -0.210 deg wear: 18.46.
- Per-pose worst: **18.47**, bit-identical to the verifier (262 takes, 4 contacts).

File: `docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_bench.json`.

Held out was not re-worn by this audit. Each held side takes about 1280 CPU-s, and the 4-core box ran at load 12, so it
did not fit the 35-minute box. The farm is off (exo-cpu1 workersMax 0 since the $8 line was spent). The held numbers
below are the verifier's own. They come from its per-pose dump (gap 22.87, reproduced from the dump) and from its sided
records, copied verbatim into `docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_verifier_wears.json`.

**The design.** It is lowarm-kstop's chain with the stage-2 pair phased (beta -177 -> -157). That phase needs a
2.45 mm x 52-deg notch in hub K's O20 boss, from F_K+6.0 to the crown, and the J2 dowel moved from 46.35 to 45.75.
Its aim was pose 264, from contact to take. That lever did not land: 264 is still a contact at -0.249 mm (ring2,
e+ play). The bench gain comes instead from a shorter crank arm.

| reading | this design | parent lowarm-kstop | lead conecut-knee |
|---|---|---|---|
| plain bench | 18.47 | 18.69 | 18.29 |
| 1 mm near-touch bench | 20.64 | 20.86 | 19.92 |
| 2 mm near-touch bench | 34.84 | 34.84 | 34.84 |
| 3 mm near-touch bench | 85.33 | 85.66 | 86.16 |
| held | 22.87 | 22.88 | 22.38 |
| 1 mm near-touch held | 25.73 | 25.73 | 25.23 |
| 2 mm near-touch held | 37.36 | 37.34 | 37.11 |
| red team: bench at mu 0.17 (family friction), not the claim | 18.75 (near1 20.93, near2 35.14) | 18.69 (fit and stroke unchanged; inferred, not re-worn) | |
| complexity (true / shown on the board) | 16.75 / **0** | 16.75 / 16.75 | 18.5 / 18.5 |

Sources: `remeasure/lowarm-kphase-notch-knuckle-3r_neartouch_dumps.json` and the `_vs_*_paired.json` files.

## What the wearer gets (measured)

Bench is frozen exact Bench(110,360), the per-pose worst of the P5 sided dwell wears.

**Reach.**

| | bench | held |
|---|---|---|
| overhead (elev >= 150) taken | 8 / 28 | 18 / 71 |
| raised arm (elev >= 90) taken | 47 / 113 | 123 / 300 |

These are the lead's and the parent's bench counts. Held is the same overhead count, but 3 fewer poses overall than
the parent: 274 and 1054 are lost to fold or stroke, and 1068 to the dowel.

Lost bench ws poses: fold 88, contact 4.

**Near-touch** (report-only, user decision 3).

| taken poses with metal under | bench | held |
|---|---|---|
| 1 mm | 4 | 13 |
| 2 mm | 33 | 72 |
| 3 mm | 104 | 217 |

- The bench sets are identical to the parent's.
- Closest taken metal: 0.072 mm at bench 139 (ws -60/60/105, link 2, a forced pose at K 31 deg), then 0.158 mm at 203
  (hub 2's ring at e+), 0.616 mm at 379 and 0.948 mm at 230. Held: 0.325 mm at held 1106 (ws 150/15/-180).
- Overhead (elev >= 140) taken poses: the 10th percentile of their min metal is 1.63 mm bench and 1.48 mm held.
- Clip frames: 0 % of metal is under 2 mm, 0.21 % at 2-3 mm and 10.10 % beyond 14 mm. In-band 2-14 is 0.8982; read as
  3-14 it is 0.8968, which gives a gap of 18.60.

**Contact depth.**

| | contacts | summed depth | deepest |
|---|---|---|---|
| bench | 4 | 15.66 mm (parent 16.62, lead 20.24) | 9.74 mm at pose 237 (plane 15, elev 165, axial -60, overhead) |
| held | 13 | 40.16 mm (parent 44.95) | 10.62 mm at plane 45, elev 165, axial -30 |

Four held contacts are deeper than 3 mm. The deep ones are overhead, as on the lead and the parent.

**Workspace in-band (unscored ws poses).** NOT obtained. `tools/alignment_wear_probe.py` does not support this family,
and the per-pose dumps carry in-band for clip frames only.

**Per part** (bench, this re-wear).

| part | in band | median metal | samples per frame |
|---|---|---|---|
| ring2 (link 2's raised stage-1 ring insert) | 0.179 | 15.6 mm | 6 |
| L2 | 0.732 | | |
| hub3 | 0.742 | | |
| crank | 0.817 | | 125 (parent 133) |
| plate | 0.846 | 11.3 mm (parent 0.715 / 12.3 mm) | |

Sample-weighted in-band is 0.899 and part-weighted 0.870 (parent 0.861, lead 0.925).

**Mechanism.**

- Springs: none. K's dwell is held between metal: the groove wall on +K and stop A on -K.
- Stops: K-own A and B, the J2 dowel (now 45.75), the J3 dowel and the knee window.
- Stage-2 pressure angle at the horn: 42.6 deg effective against the 43 cap at mu 0.15 (parent 33.1).
- Stroke limit: 46.0, set by pocket-pa (parent 46.75, set by the slot end).
- Cuff twist: knee pins on MR63ZZ pairs, with no spring-held lag. R17 was not run.
- Singular postures:
  - th fold margin: bench min 5.30 dwell / 5.18 forced (this re-wear); held 5.317 / 5.248 (verifier). 0 poses under 5.
  - m_sub (the K sub-dyad) is under 1 deg on 50 bench and 98-100 held dwell poses.
- DOF: 3 active (J1, J2, J3 on O20 v5; hub K is notched, see M2). 0 passive translations. Complexity 16.75; the board
  shows 0.

## Findings

1. **NEW-friction-corner (watch).** The 0.22 bench edge over the parent is bought by spending the stage-2 transmission margin, and only the model's nominal friction prices it. Phasing beta -177 -> -157 raises the horn's effective pressure angle from 33.1 to 42.6 deg against the 43 cap (PAC = 43 - atan(mu), read at the model's mu 0.15). The parent keeps 9.9 deg of margin, this design 0.4. The pa-limited stroke on the built geometry (lim_pa_by_mu) shows the same thing: the parent reads 64.5 deg up to mu 0.15 and 61.0 at 0.20; this design reads 46.5 at 0.15 and 40.75 at 0.20. The family's own red-team friction is mu 0.17 (lowarm-kstop gates(): stage-1 bind checked 'at mu 0.17'). At mu 0.17 the stroke ends at dK_lim 44.25 ('wall2B-pa'; 45.0 at mu 0.16) against the parent's unchanged 46.75 slot-end. This audit re-wore the frozen claim on the exact bench at mu 0.17, model and harness unchanged. Per-pose worst: 18.75 (+0.264 side 18.68, -0.210 side 18.75), against 18.47 at mu 0.15. Bench pose 313 (ws 60/120/-105, raised arm, K 45.615) is lost. Near-touch reads 20.93 at 1 mm and 35.14 at 2 mm. The parent's fit and stroke are identical at mu 0.15 and 0.17 (fast fit 18.8 both, dK_lim 46.75 both), so it stays 18.69 there; that is inferred from the identical fit, not re-worn. At the family's red-team friction this design therefore reads 0.06 behind its parent on the plain gap and 0.30 behind at 2 mm. Not gamed: ranking at mu 0.17 is a tightening of the protocol (proposal A), not the claim's harness, and the reversal is one pose.
   - Evidence: docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_mu017_bench.json (this audit, exact frozen Bench(110,360) at mu 0.17, both sides + per-pose worst); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_mu_probe.json (fast fit at mu 0.12-0.20 for both designs: dK_lim, why_lim, pa, lim_pa_by_mu); docs/concepts/models/desmo-conecut-knuckle-3r.py lines 169, 357-363 (PAC and lim_pa); docs/concepts/models/lowarm-kstop-knuckle-3r.py gates() (mu 0.17 rule)
   - Why the exo is not better than it reads: the parent reaches the same bench stroke end at any friction up to mu 0.20 with 10 deg to spare; this one needs mu <= 0.15 to reach pose 313, and higher drive load near the stroke end
   - Action: report dK_lim and the bench number at mu 0.17 beside the claim (proposal A); before any CAD, measure the as-built horn/pocket friction or re-synthesise the slot for a >= 2 deg pa margin

2. **P1 (watch).** The bench edge over the parent does not travel held out; the bench cannot see its cost. Bench: 18.47 against lowarm-kstop's 18.69 (-0.22, all in-band; the same 262 takes, the same 4 contacts, and identical near-touch poses). Held: 22.87 against 22.88 (-0.01; paired CI90 [-0.34, 0.44], P(better) 0.437). The in-band gain travels (-0.21 held). It is cancelled by +0.32 of held reach: 3 held ws poses that the parent takes are lost here. 274 (-60/45/120) and 1054 (135/30/-135) are lost to 'fold' (the model's why: 262 fold vs the parent's 260). 1068 (135/60/-90, dK 45.881) is cut by the re-phased J2 dowel. The dowel also cuts 835 (dK 46.0), a contact on the parent, worth -0.11. The cause is the shorter stroke the phase needs: dK_lim 46.75 slot-end -> 46.0 pocket-pa, J2 dowel 46.35 -> 45.75. The bench has no pose there: its max taken K is 45.615 and the dowel cuts 0 bench poses. So the bench sees the gain and none of the cost.
   - Evidence: docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_vs_lowarm-kstop-knuckle-3r_paired.json (bench / held / pooled); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_neartouch_dumps.json held diffs (taken_B_only 274, 1054, 1068; contact_B_only 835); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_verifier_wears.json (v_held_*: dowel n_cut 2 [835 46.0, 1068 45.881], why fold 262; v_bench_*: dowel n_cut 0, dK_taken_max 45.615); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_mu_probe.json (dK_lim kphase 46.0 pocket-pa vs kstop 46.75 slot-end at mu 0.15)
   - Why the exo is not better than it reads: the gain travels (in-band -0.21 held) but the stroke the phase needs costs the same amount of held reach; held it is the parent
   - Action: rank it against its parent on held (tie) and pooled (-0.06, CI90 [-0.29, 0.31]), not on the bench

3. **NEW-hairline-gates (watch).** The configuration sits at the edge of every gate it was chosen against (beta -157 is where three limits meet): (1) notch wall over the MR117 OD 2.05 mm against the 2.0 floor; (2) pa_eff_horn 42.6 against the 43 cap at mu 0.15 (0.4 deg); (3) plate-to-hub-K clearance 1.05 against the 1.0 part gap; (4) pose 203 at 0.158 mm at e+ against the round's 0.15 floor (flips at the +0.2 probe, 19.56); (5) bench pose 313 (ws 60/120/-105) taken at dK 45.615, 0.135 deg under the re-phased J2 dowel 45.75 (the parent had 0.735 deg there). A dowel 0.14 deg low cuts it: +0.28 reach, so the bench reads 18.75, behind the parent's 18.69. The lead's red team put ISO 2768-f dowel placement at 0.87 deg worst case. (6) Held paired vs the lead +0.49 against the round's 0.5 kill line; (7) notch clocking +-8 deg (plate az 54.9-89.7 inside the 46-98 notch) on a cap that is torqued and Loctited at an uncontrolled azimuth. None of these margins is priced in v_gap.
   - Evidence: docs/concepts/rows/lowarm-kphase-notch-knuckle-3r.json gate0 (b_wall_over_MR117 2.05, pa_eff_horn 42.6, c_dK_lim 46.0), verification.issues; docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_verifier_wears.json v_bench_0.264 named 313 dK 45.615 taken, dowel K 45.75; docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_mu_probe.json (clear_plate_hubK 1.05); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json held +0.5 (CI90 [-0.02, 0.79]); conecut-knee ledger T3 (ISO 2768-f 0.87 deg)
   - Why the exo is not better than it reads: a real build at the soft end of any one tolerance (dowel placement, friction, bearing class, notch clocking) gives back the 0.22
   - Action: price the dowel tolerance (proposal B) and report borderline gates as borderline

4. **M2 (watch).** Hub K is no longer the user's O20 v5 stack. The notch is a 52-deg x 2.45 mm sector from F_K+6.0 to the crown, and it does three things: (a) it thins the boss wall over the MR117 to 2.05 mm; (b) it removes the cap's 1 mm skirt (r 9-10, z 8.75-10.25) over that sector; (c) it removes the M18x0.5 spigot thread (86 % of about 3 threads left). docs/HARDWARE.md has the cap threaded on with Loctite 222 and torqued so that it clamps outer ring 2. A notch through it therefore needs a clocked cap (indexing pin, or machining after assembly). The bench gain depends on the notch: without it, beta -157's slot plate penetrates hub K by 1.40 mm and the fit collapses (reach 0.21). The user's ruling 'Keep O20 only' bans slim hubs. Whether a locally notched and clocked O20 counts as O20 is the user's call, not the model's. Not gamed: the cut's metal is modelled exactly (CSG max(sd_cyl, -sd_notch)), the hub stays O20 elsewhere, and the bearing wall stays above the round's 2.0 floor.
   - Evidence: docs/concepts/lowarm-kphase-notch-knuckle-3r.md Verification 'Issues' (cap skirt + thread); docs/HARDWARE.md lines 44-62, 100 (U0 3.15, H1 8.75, U1 10.25, M18x0.5 spigot, cap Loctite 222 to torque); rows gate0 plate footprint (true plate-hubK -1.403 at beta -157 without the notch); docs/concepts/lowarm-kphase-notch-knuckle-3r.md 'Without the per-pose notch the fit collapses: reach 0.21, follow 0.12'
   - Why the exo is not better than it reads: the hub K the bench scores is not the O20 v5 the user approved; its cap must be indexed against a torque-to-clamp thread
   - Action: ask the user whether a notched, clocked O20 meets 'Keep O20 only'; until then treat the 0.22 as conditional on that ruling

5. **G5 (watch).** The board shows complexity 0 for a 16.75 design. The row's mechanism block holds only a descriptive joints list, a cuts list and 'complexity': 16.75. It has none of docs/SIMPLICITY.md's count fields, so tools/simplicity.py scores it as the anchor, 0.0, and docs/dashboard/data/morphs.json carries complexity 0 with 'none: the anchor (three pins on bearing pairs, three links)'. The parent's verifier fixed exactly this schema on lowarm-kstop (its schema_note), and this row did not inherit the fix. The board's score-vs-simplicity chart plots the design at (93.28, 0), the golden-solution corner. On (v_gap, complexity) it dominates 29 of the 36 other verified rows with the shown 0, and 15 with its true 16.75. The audit tool's own complexity check misses it: it compares with row['complexity'] (None) and never reads mechanism.complexity, so it prints 'ok'. The clocked cap the notch needs would add one bought part (+0.25 -> 17.0).
   - Evidence: python3 tools/simplicity.py --json (lowarm-kphase-notch 0, lowarm-kstop 16.75); docs/dashboard/data/morphs.json row (complexity 0, complexity_items 'none: the anchor'); docs/concepts/rows/lowarm-kstop-knuckle-3r.json mechanism.schema_note; docs/alignment/lowarm-kphase-notch-knuckle-3r.json complexity check 'recomputed 0.0 vs row None'; dominance count this audit from morphs.json (verified rows with v_gap and complexity)
   - Why the exo is not better than it reads: complexity is the user's second objective; this design adds nothing on that axis (16.75, the parent's) but the board shows it as the anchor
   - Action: write lowarm-kstop's full mechanism record (+0.25 for the clocked cap's pin if adopted) into the row; proposal C for the tool

6. **R1 (watch).** Screen strings sit on a verified row, and the verifier's measurements are not on file. The row's verdict field still opens 'Gate 0 half-passed ... Not converged, not a verdict', and its limiter is the screen's. morphs.json shows gap / sweep_gap 13.33 (score 95.15, above the board's 95 line) beside v_gap 18.47, with alignment empty. The verifier wrote its four sided wear records to the session scratchpad and committed only the per-pose dumps. Those records hold the held frozen 22.80 / 22.87, the dowel cuts, the V3b fold margins and the bench flood. As a result the audit tool's held_out, fold_margin and continuity checks read 'nothing on file', although all three were measured. This audit copied the records verbatim into the repo (with sha256).
   - Evidence: docs/concepts/rows/lowarm-kphase-notch-knuckle-3r.json verdict / limiter; docs/dashboard/data/morphs.json (gap 13.33, sweep_gap 13.33, alignment ''); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_verifier_wears.json (copied from scratchpad kphv/v_{bench,held}_{0.264,-0.210}.json); docs/alignment/lowarm-kphase-notch-knuckle-3r.json checks held_out / fold_margin / continuity
   - Why the exo is not better than it reads: a reader of the board sees a 95.15 fast score and a screen verdict on a verified row, and the audit tool sees no held-out wear
   - Action: lead: put the verified result first in the verdict field; verifiers commit their wear records (proposal D)

7. **S5 (watch).** Only the bench's wall side is flooded. This audit re-ran the verifier's flood on its own +0.264 bench re-wear (gap 18.39 reproduced). Full flood: 18.39, 0 dropped (128 of 128 forced takes connected through 526 envelope poses). The knn flood reads 20.08 (6 dropped, +1.69) and the bench graph 50.24. No flood exists on the -0.210 wear, on the per-pose worst (18.47) or on held. The parent's held knn flood lost 8.14 points. The poses this design gives up held (274, 1054, 1068) are stroke-end poses, the region a flood stresses.
   - Evidence: docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_bench.json connected_side (this audit, delta 0.264); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_verifier_wears.json v_bench_0.264 connected (identical); lowarm-kstop audit S5 (held knn 22.64 -> 30.78)
   - Why the exo is not better than it reads: the stroke-end poses this design gives up are exactly where a continuous motion would hit the shortened stroke
   - Action: run the held flood (the verifier harness's --flood on the held wear)

8. **S2 (watch).** Carried from the parent. Sample-weighted in-band is 0.899, part-weighted 0.870 (parent 0.861, lead 0.925). Link 2's raised stage-1 ring insert (ring2) is 0.179 in band at a median 15.6 mm off the skin, on 6 samples per frame (0.6 % of the weight). The plate has 10 samples and L1a 8. The bench gain itself is real metal, not sampling: per frame the crank has 125 samples (parent 133: the re-phased long arm is 49.7 mm against 55.4 and its arc 107 deg against 127) and the plate's median is 11.3 mm (parent 12.3). That leaves 2.66 fewer out-of-band samples per frame (98.56 of 974 against 101.22 of 980), and metal > 14 mm falls from 10.32 % to 10.10 %. Kit density was not measured: tools/sample_density.py needs a frozen() entry the model lacks, and the parent's kit-density shift was +0.08, a third of the 0.22 edge.
   - Evidence: docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_bench.json parts_ib14 + deep.clip_metal_hist (this audit) vs docs/alignment/remeasure/lowarm-kstop-knuckle-3r_bench.json; docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_mu_probe.json (arm_len 49.7 vs 55.4, arc 107.1 vs 127.3)
   - Why the exo is not better than it reads: the wearer still has the raised ring bump over hub 2 that the in-band number barely sees
   - Action: measure kit density once the model has a frozen() entry

9. **G4 (watch).** Carried from the lead and the parent. The K sub-dyad m_sub is under 1 deg on 50 bench dwell poses (this audit, both sides) and on 98-100 held dwell poses (verifier V3b): a near-singular sub-dyad at rest. The th fold margin itself is fine: bench min 5.30 dwell / 5.18 forced (this audit), held 5.317 / 5.248 (verifier), 0 under 5. Held forced is 5.248 rather than the parent's 5.006 only because held 1054, the parent's 5.006 pose, is lost here.
   - Evidence: docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_bench.json th_margin (this audit); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_verifier_wears.json v_held_* v3b_th_margin
   - Why the exo is not better than it reads: a near-singular K sub-dyad at rest is felt as a soft or jerky K start
   - Action: with the user (the lead's G4 item)

10. **M5 (watch).** Carried from the parent, and the phase makes it worse. The dwell hold is rigid in the model and compliant in the build: stop A plus the crank's long arm, now 49.7 mm, never stiffness-modelled. R17 has not been run and no dynamics run exists. The phase raises the stage-2 pressure angle at the horn from 33.1 to 42.6 deg effective. The drive force grows by about 1/cos: cos(33.1)/cos(42.6) = 1.14, so 14 % more contact load for the same K torque near the stroke end. A higher pressure angle near the lock limit is what the wearer feels as stiction at the end of the K stroke.
   - Evidence: docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_mu_probe.json (pa kphase [10.3, 34.1, 42.6] vs kstop [14.6, 24.6, 33.1] at mu 0.15); lowarm-kstop audit M5; rows verification.issues
   - Why the exo is not better than it reads: the hold's compliance and the higher stage-2 contact load are unmodelled; both act at the stroke end
   - Action: model the long-arm stiffness and run R17 before any CAD

11. **M3 (watch).** The skin samples were framed on the wrong body, and the error was caught. The claim kept hub K's skin-checked O20 samples on link 1a and dropped the 15 inside the notch in link 1a's frame. The notch is on link 1b, so at K up to 45.6 deg the model's hole sat up to 45 deg from the real one. The verifier's V-OWN correction moved 161 samples to link 1b and measured an effect of 0.00, and this audit's re-wear without the correction reproduces 18.47. Still open from the parent: the pocket in link 1b's plate (about 30-35 % of the bar root section), the 1.38 mm arm tip against the CAD's 1.5, and the stop-A set-screw bore with zero thread wall. The notch floor is 1.25 mm over stop A's groove (OK).
   - Evidence: docs/concepts/lowarm-kphase-notch-knuckle-3r.md Verification check 2 (V-OWN: 161 moved, 15 dropped, effect none); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_bench.json sides (no correction: 18.39 / 18.46 -> 18.47); notch_info wall_to_stopA_groove_mm 1.25; lowarm-kstop audit M3
   - Why the exo is not better than it reads: none measured here (effect 0.00); the parent's open build specs remain
   - Action: carry the parent's actions (FEA of the pocketed root, bore fix)

12. **T1 (watch).** Carried, and unchanged by this design. The closest taken metal is 0.072 mm at bench pose 139 (ws -60/60/105, link 2, forced) and 0.158 mm at 203 (hub 2's ring at e+). Poses under 1 / 2 / 3 mm: 4 / 33 / 104 bench and 13 / 72 / 217 held, the parent's exactly on the bench. Near-touch gaps are 20.64 / 34.84 / 85.33 bench (parent 20.86 / 34.84 / 85.66, lead 19.92 / 34.84 / 86.16) and 25.73 / 37.36 / 82.71 held (parent 25.73 / 37.34 / 83.14). The 1-2 mm shell holds 16.37 points of the bench gap (report-only since the user's 2026-10-17 ruling). No metal moved into the 1-3 mm shell (clip histogram 0 % under 2 mm, 0.21 % at 2-3 mm), so G1 is not triggered. Against the parent the plain bench edge (-0.22) shrinks to 0.00 at 2 mm (bench) and turns to +0.02 behind at 2 mm held.
   - Evidence: docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_bench.json deep (this audit); docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_neartouch_dumps.json (bench + held, three designs)
   - Why the exo is not better than it reads: metal at 0.07-0.16 mm on a taken pose is metal on a real arm; nothing here makes it better or worse
   - Action: none new (family item)

## Proposals (measurement changes; none is an input to this verdict)

- **A. A friction corner in the stroke gates.**
  - The proposal: every desmo-family claim reports dK_lim and its take count at the family's red-team friction mu 0.17,
    beside the model's mu 0.15, and the round ranks at the worse of the two. Today only stage 1's bind is checked at
    0.17 (lowarm-kstop gates()), while the stage-2 pocket pa cap is read at the model's mu.
  - Effect on the verified rows of this family: lowarm-kstop 18.69 is unchanged (dK_lim 46.75 slot-end at both).
    lowarm-kphase-notch: 18.47 -> 18.75 (exact, this audit; pose 313 lost at dK_lim 44.25), so it ranks behind its parent. The other desmo rows (desmo-conecut, lowarm-halfring) have lim_pa_by_mu 64.5 to
    mu 0.15 and 61.0 at 0.20, so they would be unchanged unless their stage 1 binds.
- **B. A stop-tolerance corner.** Each claim states the largest taken K and its distance to every K / J2 dowel. A row
  whose bench take sits within the dowel's ISO 2768-f placement tolerance (0.87 deg worst case, the lead's red team) is
  ranked with that pose cut. Effect: lowarm-kphase-notch 18.47 -> 18.75 (313 at 0.135 deg). lowarm-kstop is unchanged
  on the bench (0.735 deg), but its held max K is 0.082 deg under its dowel.
- **C. The audit tool's complexity check should read mechanism.complexity** and flag a mechanism record that lacks
  docs/SIMPLICITY.md's count fields. Today it compares the recompute with row['complexity'] only and prints 'ok' here
  (recompute 0 vs None). Effect: lowarm-kphase-notch, conecut-h2facet and conecut-l2jog become G5 watch on the tool
  alone. No score changes.
- **D. Verifier records on file.** A verifier commits its sided wear JSONs, not only the per-pose dumps, so that the
  held-out, fold-margin and flood checks can read them. Effect here: held_out, fold_margin and continuity go from
  'nothing on file' to measured (held +4.40 drop, th 5.18 min, full flood 0 dropped).

## Ledger

`python3 tools/alignment_ledger.py append lowarm-kphase-notch-knuckle-3r --findings docs/alignment/lowarm-kphase-notch-knuckle-3r.findings.json --by auditor --run audit:lowarm-kphase-notch-knuckle-3r`
printed **verdict watch** (tool verdict watch, claim 18.47 v_gap).

The reason_items:
- tool checks (all watch):
  - held_out: no held-out measurement on file. The verifier measured held 22.87, a +4.40 drop, but its wear records
    were not on file; see R1.
  - continuity: no flood on file. This audit's full flood is 18.39 with 0 dropped; see S5.
  - fold_margin: no min-th on file. The measured minimum is 5.18; see G4.
  - sampling: part-weighted 0.870 against sample-weighted 0.899; ring2 is 0.18 in band.
  - reporting: the board's sweep best 13.33 (score 95.15) sits 5.14 below the verified number.
- judgement findings (all watch): NEW-friction-corner, P1, NEW-hairline-gates, M2, G5, R1, S5, S2, G4, M5, M3, T1.

Not measured, and why:
- Held re-wear and held flood: time box and box load; the farm is off.
- Workspace in-band: the wear probe does not support this family.
- Kit density: the model has no frozen() entry.
- The parent's exact wear at mu 0.17: inferred from its identical fit and stroke.
- R17, cuff twist and arm compliance: no dynamics model for this chain.

## New catalogue entry (proposed)

**NEW-friction-corner: a transmission margin spent at the nominal parameter.**
- Looks like: a design change gains a little in-band or reach and moves a pressure angle (or any friction-gated
  limit) to within a fraction of a degree of its cap, at the model's nominal mu.
- Why not better: real friction varies, with wear, lubricant and contamination. A drive at its pressure-angle cap
  binds or stalls at the stroke end, and the wearer feels that as a jam. The parent kept about 10 deg of margin.
- Detect: read every friction-gated limit (dK_lim, lim_pa_by_mu) at the family's red-team mu, and re-wear the claim
  there when the margin is under 2 deg.
- Here: lowarm-kphase-notch-knuckle-3r, pa_eff 42.6 / 43. At mu 0.17 it reads 18.75 against 18.47.

## Skeptic (2026-10-18, ~17:08-17:30 UTC)

**Final verdict: WATCH.** This is the ledger tool's skeptic entry (2026-10-18T17:23:56Z). Rulings are in
`docs/alignment/lowarm-kphase-notch-knuckle-3r.rulings.json`. I refuted 2 of the 17 reasons with evidence (held_out,
fold_margin) and upheld 15.

**What I re-measured.** I re-wore both held sides with the model unchanged, through the auditor's adapter:
`tools/alignment_remeasure_kphase.py side held <delta> <out> --flood`. That runs the verifier's harness with its
corrections off, the parent's `wear()` and the verifier's `flood()`. Settings: CB_EXACT=1, OMP_NUM_THREADS=1, nice 15,
2 processes, about 830 s each. The summary is `docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_skeptic_flood.json`.
The merged per-pose worst is `docs/alignment/remeasure/lowarm-kphase-notch-knuckle-3r_held.json`.

| held wear | static | connected_full | connected_knn | bench-graph flood | min th (dwell / forced) | m_sub < 1 deg (dwell) |
|---|---|---|---|---|---|---|
| -0.210 (worst side) | 22.87 | 22.87 (0 of 329 forced dropped) | **30.89 (75 dropped, +8.02)** | 24.05 (11 dropped) | 5.317 / 5.248 | 100 of 457 |
| +0.264 | 22.80 | 22.80 (0 dropped) | 30.82 (75 dropped, +8.02) | 23.98 (11 dropped) | 5.517 / 5.248 | 98 |
| per-pose worst | **22.87** (reach 0.6891, in-band 0.8971, contact 0.0149, 656 ws taken, 13 contacts) | | | | | |

- Each side matches the verifier's sided per-pose dump with 0 differences (1154 / 1154 poses).
- The J2 dowel cuts held 835 (K 46.0) and 1068 (45.881); the largest taken K is 45.367.
- Merged near-touch: 25.73 / 37.36 / 82.71 at 1 / 2 / 3 mm, closest metal 0.325 mm, overhead 18 of 71. These are the
  auditor's dump readings.

**Files on record I checked:**
- The four verifier records the auditor copied have the same sha256 as the session-scratchpad originals
  (`kphv/v_{bench,held}_{0.264,-0.210}.json`).
- The dumps recompute 18.47 (bench) and 22.87 (held).
- The sided taken sets are identical: bench 372 / 372 and held 858 / 858, symmetric difference 0, same contacts.
- An in-memory run of the audit tool (`audit(..., write=False)`, before my held file existed) still printed held_out,
  continuity and fold_margin as 'nothing on file'. `_verifier_outputs()` returns [] for this id, and the tool does not
  read `rows:verification.held / continuity / th_margin`, because those are text.

**Rulings.**
1. **held_out: REFUTED.** I measured held at 22.87 (per-pose worst; sides 22.80 / 22.87), 0 per-pose diffs from the
   verifier. Before this audit the number was on file at `rows:verification.held`, `remeasure/_held_perpose.json` and
   `remeasure/_verifier_wears.json` v_held_*.frozen. The drop is +4.40, under the documented held_watch 6.0, so the
   tool's rule reads ok. The tie with the parent is ruled under P1.
2. **continuity: upheld (watch).** The bench flood is on file (full 18.39, knn +1.69). Held, measured now: full = static
   (0 dropped), but knn **+8.02** (75 of 329 forced takes not knn-connected). The tool's rule watches when the knn loss
   is over 3, the same as on the parent (+8.24).
3. **fold_margin: REFUTED.** The min th is on file: `rows:verification.th_margin`, verifier records v3b_th_margin 5.248 /
   5.317, and bench `remeasure/_bench.json:th_margin` 5.181 / 5.301. My held re-measure gives 5.248 forced and 5.317
   dwell, with 0 under 5. The minimum over everything, 5.181, is at or above fold_min 5.0.
4. **sampling: upheld.** I re-derived it from parts_ib14 with the tool's arithmetic: +2.85 points (under 3), but ring2 is
   0.179 in band at 15.6 mm on 6 samples. That trips the documented out-of-band-part watch.
5. **reporting: upheld.** morphs.json has sweep_gap 13.33 against v_gap 18.47 (5.14 > 5), and the row verdict is still
   the screen's.
6. **NEW-friction-corner: upheld.** At mu 0.17, the per-pose worst is 18.75 (313 lost, dK_taken_max 43.661). The loss also
   holds on the fixed built geometry: lim_pa_by_mu (the same in every probe row) reads 46.5 at 0.15 and 40.75 at 0.20,
   so about 44.2 at 0.17, which is under 313's K of 45.615. Two corrections, neither of which changes the level:
   - mu is a synthesis input. The 'mu 0.17 wear' re-synthesises the plate and pocket (plate_len 9.67 -> 9.33). At
     mu 0.12 the re-synthesised plate hits hub K (dK_lim 0, fit 95.51).
   - The why-line "the parent reaches the stroke end up to mu 0.20" is wrong. At mu 0.20 the parent also collapses
     (dK_lim 0, s1b-pa-pin, fit 95.51).
7. **P1: upheld.** Recomputed from the dumps: bench -0.22, held -0.01. Only the parent takes held 274, 1054 and 1068, and
   835 is a contact only on the parent.
8. **NEW-hairline-gates: upheld.** Every margin checks out at its source: gate0 2.05 / 42.6, clear_plate_hubK 1.05,
   203 0.158, 313 at 0.135 deg, held vs the lead +0.49, clocking +8.9 / -8.3. See also the dowel-to-bind margin under
   missed.
9. **M2: upheld.** The claim doc (lines 168-176) and HARDWARE.md (lines 49 and 62) confirm the cut skirt and thread and
   the need for a clocked cap. Whether that counts as O20 is the user's call.
10. **G5: upheld.** simplicity.py gives 0 (the parent 16.75), and morphs.json shows complexity 0 as 'the anchor'.
    Dominance, recomputed over 36 rows: 29 at the shown 0, 15 at the true 16.75.
11. **R1: upheld.** The row verdict and limiter are the screen's, and morphs.json has alignment ''. The tool still reads
    nothing on file.
12. **S5: upheld.** The held flood now exists and confirms the concern: knn +8.02 on both sides. The bench -0.210 side's
    taken set is identical to the flooded +0.264 side's.
13. **S2: upheld.** crank 125 vs 133 samples per frame, plate 0.846 vs 0.715. Kit density not measured.
14. **G4: upheld.** m_sub < 1 deg on 50 bench and 98 / 100 held dwell poses (my held re-wear agrees). The cost to the
    wearer has not been measured.
15. **M5: upheld.** No R17 run and no compliance model. cos 33.1 / cos 42.6 = 1.138.
16. **M3: upheld.** The re-framing costs 0.00, but the parent's carried build items have nothing on file closing them.
17. **T1: upheld.** under1 at 139 0.072 and 203 0.158. Near-touch 4 / 33 / 104 bench and 13 / 72 / 217 held. The edge
    over the parent is 0.00 at 2 mm on the bench and +0.02 behind at 2 mm held.

**Missed (for the next audit; not in this verdict).**
- **M1. The family's dowel-to-bind margin is not applied to the new stage-2 bind.**
  - The parent's own gate keeps the J2 dowel at least 1.0 deg under any bind first-fail at mu 0.17. Source:
    `lowarm-kstop-knuckle-3r.py` gates(), rule "bind first-fail >= 47.35 (dowel 46.35 + 1.0)".
  - The phase turns K's stroke end from a metal slot end (the parent, 46.75) into a pressure-angle bind: pocket-pa 46.0
    at mu 0.15 (rows gate0.c_dK_lim). That is 0.25 deg over the re-phased dowel at 45.75.
  - At mu 0.17 the bind, 44.25 'wall2B-pa', comes 1.5 deg BEFORE the dowel. So the K stroke ends on a jam, not on a
    stop.
  - Under the parent's 1.0 deg rule, the dowel would sit at or under 45.0 even at mu 0.15. That cuts bench 313 (K 45.615)
    and gives about 18.75, the auditor's dowel-low reading, behind the parent's 18.69.
  - Neither the claim doc nor the verifier harness runs this gate. Searching both for 47.35, first-fail and mu 0.17
    gives no hits.
- **M2. Round-15 ranking at the probe.**
  - ROUNDS.md lines 4602-4604 say that a claim at a rule-floor clearance is ranked at its +0.2 mm probe. Here 203 is at
    0.158 against the 0.15 floor.
  - The claim states its probe reading (claim doc lines 153 and 180, `rows:verification.bench`): 19.56. The parent's is
    19.77 (`lowarm-kstop-knuckle-3r.md` line 95) and the lead's is 18.83.
  - The audit compares plain numbers only. At the probe the edge over the parent holds (-0.21), and the design is 0.73
    behind the lead.
  - The leaderboard stays the plain verified gap (CLAUDE.md), so this is a reporting note.
- **M3. Proposal A should read friction on the frozen geometry.**
  - The model takes mu as a synthesis input: it re-sizes the plate and pocket, and at mu 0.12 the design collapses on
    PLATE-hubK. That is impossible for a fixed part at lower friction.
  - A friction corner should therefore read lim_pa_by_mu, or re-check the pa cap, on the claim's built geometry. It
    should not re-fit at the red-team mu.
  - Here both readings agree (about 44.2 against 44.25).
- **M4. Tool blind spots with the same root as G5.**
  - c_idle prints 'no moving drive / joint declared', because `_declared_joints` reads the missing mechanism count fields.
    K's travel is therefore never checked. It does move (dK_taken_max 45.615), so there is no cost here.
  - c_rules reads O20 only from hub_r keys (line 786), so a notched hub passes as 'O20 as recorded'.

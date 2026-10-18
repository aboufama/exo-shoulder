# Alignment audit: desmo-conecut-knuckle-3r

Hourly audit, 2026-10-18 22:39-23:16 UTC. Due because the row was committed at 07:42:27 (ea9371b, the lead's density
audit) after the last ledger entry (05:59:03, WATCH). That commit put a new, lower number on the row's verdict text: the
S6 density re-weight, 18.68 bench / 22.89 held (18.49 with ring2 at 4x), next to v_gap 18.98. The confirmation re-wear was
still pending. This is the first audit of that number. Run on the box (at most 2 niced processes, OMP_NUM_THREADS=1; the
farm was not used, $0).

- **Ledger entry:** 2026-10-18T23:12:46Z, by auditor, run `audit:desmo-conecut-knuckle-3r`. Verdict **watch**, claim v_gap 18.98. Reasons: 2 tool reasons (continuity, density) and 13 judgement findings, all watch. None is gamed.
- **Checks:** `docs/alignment/desmo-conecut-knuckle-3r.json` (tool VERSION 2026-10-18.1). Tool verdict watch:
  continuity and density.
- **Findings:** `docs/alignment/desmo-conecut-knuckle-3r.findings.json` (13, all watch).
- **Files this audit wrote.** The model and the verifier ran unchanged. The wear was thinned in place by the same
  `_thin` that `tools/sample_density.py` uses.
  - `remeasure/desmo-conecut-knuckle-3r_bench.json`: the standard re-wear, 19.04 frozen exact on the claim's linear-law
    IK. It matches the 2026-10-17 re-wear number for number: near-touch 1 mm 20.68 / 2 mm 35.13 / 3 mm 87.13, closest
    metal 0.072 mm.
  - `remeasure/desmo-conecut-knuckle-3r_held.json`: the standard held re-wear, 23.24 frozen held out (linear-law IK; the verified blended IK reads 23.19); near-touch 1 mm 26.09 / 2 mm 37.56, closest metal 0.325 mm.
  - `tools/alignment_density_rewear_conecut.py` (new): the exact confirmation of the density re-weight through the
    verifier's own `--blend` harness. It is needed because the row's recorded command crashes (finding S6).
  - `remeasure/desmo-conecut-knuckle-3r_density_rewear_bench.json`: exact thinned bench 18.65 (in-band 0.8963; horn [27, 10], ring2 [19, 7]; fit_fast 13.27 = the verifier's).
  - `remeasure/desmo-conecut-knuckle-3r_density_rewear_held.json`: exact thinned held out 22.86 (in-band 0.8952; horn [27, 10], ring2 [19, 7]; reach 0.6922, contact 0.016; fit_fast 13.27).
  - `remeasure/desmo-conecut-knuckle-3r_s1level3p9_density_rewear_bench.json`: the plate-clearing level F+3.9 (glev 2.039, a_s 9.8 / psi 150, ring2 in link 2's true frame) thinned: exact bench 19.03 (in-band 0.8925; horn [27, 10], ring2 [29, 8]; desmo_fail []; as sampled 20.50).

## Verdict: WATCH, claim v_gap 18.98 (score 93.10), held out 23.19

Nothing in the number is gamed and no hard rule is broken. The ranking number is still v_gap 18.98, and the dashboard
shows 18.98.

The new number on the row is honest as a measurement. The density re-weight 18.68 is confirmed by an exact thinned
re-wear: **18.65 bench**, **22.86 held** (re-weight 22.89). It is a fair change in the design's favour. The family's ring2 sampler puts 1
sample per mm2 on a strip of out-of-band metal, against the kit's 1 per 4 mm2, so the as-sampled 18.98 over-counted that
strip.

But the 18.68 is the number of a stage 1 that cannot be built (M3), and it applies a one-sided correction (S6). The
same thinning at the only plate-clearing level with a feasible pin reads **19.03**. So the exo that could be built reads
19.03 at the kit's density. That is 0.05 from the verified 18.98, and 0.35-0.38 worse than the 18.68 now on the row. The
two corrections (density, -0.33; a buildable level, +0.38 at the kit's density) cancel to within 0.05.

| reading (exact frozen Bench(110,360) unless stated) | bench | held |
|---|---|---|
| verified v_gap (as sampled, unbuildable level glev -1.0) | 18.98 | 23.19 |
| row's S6 re-weight (horn 2.52x, ring2 2.44x to the kit) | 18.68 | 22.89 |
| **exact thinned re-wear (this audit; horn 27 -> 10, ring2 19 -> 7)** | **18.65** | **22.86** |
| re-weight, ring2 at the sampler's own pitch (4.0x) | 18.57 | 22.78 |
| re-weight, ring2 at its hull reading (1.45x, under the flag: horn only) | 19.07 | 23.28 |
| re-weight, over-dense parts AND the sparse straps L2 / L1b to the kit | 19.02 | 23.23 |
| re-weight, every part at the kit (the tool's all_parts) | 18.87 | 23.08 |
| plate-clearing level F+3.9 (glev 2.039, a_s 9.8), as sampled | 20.50 | not run |
| **plate-clearing level F+3.9, exact thinned (this audit; ring2 29 -> 8)** | **19.03** | not run (time box) |
| lead conecut-knee: as sampled / over-dense at kit / all parts at kit | 18.28 / 18.28 / 18.42 | 22.38 / 22.43 / 22.63 |

## What the wearer gets (measured)

All numbers are on the frozen claim. The claim, the model and the kit are unchanged since the 2026-10-17 re-wears, and
this audit's bench re-wear reproduces them exactly. Sources: `remeasure/desmo-conecut-knuckle-3r_bench.json`,
`_probe_bench.json`, the verifier's `+blend` per-pose dumps, `verify/desmo-conecut-knuckle-3r_v_*_blend.json` and this
audit's `_density_rewear_*` files.

| what | bench | held out |
|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 (0.286) | 18 / 71 (0.254) |
| raised-arm reach (elev >= 90), taken / total | 47 / 113 (0.416) | 123 / 300 (0.410) |
| why overhead poses are lost (ws, elev >= 140) | fold 14, contact 3, J3 stop 3 | - |
| taken poses with metal < 2 mm (< 1 mm) | 33 (3) of 372 | 71 (13) of 861 |
| taken overhead poses with metal < 2 mm | 4 of 8 | 10 of 18 |
| closest taken metal | 0.072 mm (pose 139: plane -60 / elev 60 / axial 105) | 0.325 mm |
| contact poses, summed depth, deepest | 4, 16.15 mm, 9.47 mm (pose 237: plane 15 / elev 165 / axial -60; crank -9.42, tip plate -5.87) | 14, 43.84 mm, 10.38 mm (pose 683: 45 / 165 / -30) |
| scored in-band 2-14 (clip frames): as sampled / at the kit's density | 0.893 / 0.8963 | 0.892 / 0.8952 |
| unscored workspace in-band: all taken / elev 90-140 / overhead | 0.863 / 0.831 (16.8 % of metal > 14 mm, max 30.7 mm) / 0.933 | - |
| fold margin th, min over taken | 5.181 deg (0 under 5) | 5.006 deg (pose 1054, at dK 46.27, the slot end) |
| th where stop B engages (K 46.5) | not on file (about 4.83-4.91, extrapolated) | not on file |

- **Springs:** none. K is slaved by a two-stage desmodromic drive. Stage 1 is a crowned O1.5 440C pin in a two-walled
  groove in hub 2's cap ring. Stage 2 is an O1.5 nose on link 1a in a 3.72 mm slot in the crank's tip plate.
- **Stops:**
  - the J2 fold: 88 bench / 260 held poses lost;
  - the J3 dowel: 3 overhead poses;
  - stop B at the slot's far end (K 46.5; the held stroke uses 46.27). The J2 low-end dowel engages after the drive's
    own end (NEW-stop-through-drive);
  - the knee window 25.22-154.78. The taken knee angles are 59.27-107.07, 34 deg clear.
- **Knee hardware:** the claim carries stk 6.0 mm, the kit's MR63ZZ-pair stack. So the lead's build rule (MR63ZZ
  bearing pairs) is met in the model. This was checked because two sibling rows were caught at stk 4.85.
- **Cuff twist and drag (gen-9 full CAD, R17):** nominal (bearing mu 0.005) twist 3.97 deg, 0.51 N, 0 lags. At f 0.05:
  11.74 deg with 23 lags over 10 deg. At f 0.2: 25.0 deg / 20.3 N. The R17 run drives K by the model's law, so the drive's
  own force flow is unmeasured (G3).
- **Near-singular postures:** th is 5.0-5.2 deg at the slot end (T3). The sub-dyad m_sub is under 1 deg on 50 of 205
  rest poses (G4).
- **Same arm as conecut:** the same 262 taken workspace poses and the same 4 bench contacts. The drive changes metal, not
  where the arm can go. The stage-1 ring sector the drive adds is 0.55 in band (median 13.8 mm) at the claim's level and
  0.143 (median 16.9 mm) at the level where it can be built. At the kit's density it is 7-8 samples, about 0.8 % of the
  scored metal, so the score barely sees it. A wearer feels a 1 mm sliver of metal 17 mm off the arm at the hub (S2, report
  only).

## Findings (all watch; `desmo-conecut-knuckle-3r.findings.json`)

1. **S6, over-dense sampling: the row's new number (NEW this audit).**
   - *Evidence:* the re-weight 18.68 / 22.89 is confirmed exactly at **18.65** bench / **22.86** held
     (`remeasure/desmo-conecut-knuckle-3r_density_rewear_{bench,held}.json`). The shape is the claim's: fit_fast 13.27
     equals the verifier's, and every unthinned part's in-band is identical.
   - *The confirmation command on the row cannot run.* `tools/sample_density.py rewear` crashes before any wear: its
     `fitted()` calls `_thin(M1, *thin)` with three arguments, but `_thin` takes two. So "exact re-wear pending" could not
     complete as written. The desmo-slipper audit hit the same crash and wrote its own adapter. This one,
     `tools/alignment_density_rewear_conecut.py`, is for this row's verifier.
   - *Spread:* the reading depends on which density figure ring2 gets: 19.07 (hull 1.45x, below the flag), 18.68 (cell
     2.44x, used) or 18.57 (the sampler's own 0.5 x 2 mm pitch, 4x).
   - *One-sided:* the correction applies only to parts above 2x. This row's sparse straps (L2 0.84x, in-band 0.732; L1b
     0.72x) are left as they are. Correcting them too gives 19.02, and every part at the kit gives 18.87.
   - *Why it is not gaming:* the over-sampled strip is out-of-band metal, so the as-sampled number was pessimistic for
     this row. The area-honest number is a little better.
   - *Why the exo is not better than 18.98 says:* see M3. The buildable design reads 19.03 at the kit's density.
   - *Action:* proposals 1 and 2.
2. **M3, unchecked clash (carried; re-measured at the kit's density).**
   - The verified stage-1 layer is inside link 1b's J2 lower plate at every glev in the search box (CAD R6 1.50 mm on 451
     of 451 frames).
   - Thinned to the kit's density:
     - claim's level: 18.65;
     - the only plate-clearing level with a feasible pin (F+3.9): **19.03**. As sampled, that level read 20.50.
   - So at the kit's density the buildable lift costs +0.38, not +1.52, and the 18.68 now on the row is 0.35-0.38
     optimistic as the number of an exo that can be built.
   - F+3.9 clears the plate by only 0.15 mm, and it is not shown clear of link 1b's strap.
   - Not gamed: v_gap ranks, and the row is not the lead at any reading. The 18.68 ranks the row only in
     `sample_density.md`, where it passes roller-longdyad (18.76 at kit). That row has its own open M2 (18.93 at the
     MR63ZZ stack), so it is not shown better for the wearer.
   - *Action:* the row's density sentence should carry the buildable 19.03 next to the 18.68 (the lead's call; the
     auditor edits no row).
3. **NEW-inherited-stack (proposed M6; now measured on three rows).**
   - lowarm-halfring is ledger GAMED on the same layer (its skeptic re-ran the geometry: F+0.11..1.61).
   - desmo-slipper reads 20.38 / 25.33 at the plate-clearing level, as sampled.
   - At the kit's density the lift is +0.38 here and +0.11 on lowarm-halfring: mostly a density artefact on the number.
     The clash is still real metal in a real plate.
4. **NEW-sample-frame (proposed entry renumbered S7, since S6 is now the density check).**
   - ring2 is sampled 7.28 deg off link 2's frame: +0.09 as sampled, +0.03 at the kit's density.
   - The insert's 28 deg outside O20 that the model does not sample is still unworn, estimated at +0.05 to +0.1 at the
     kit's density.
5. **T3 (carried; the rule's second clause still unmet).**
   - th on the taken poses: 5.181 bench and 5.006 held, 0 poses under 5.
   - th where the K-clamped stop B engages (K 46.5) is not on file, although the stop-buildability rule requires it.
     Extrapolated from the verifier's slope it is about 4.83-4.91.
   - With the drive's 0.23-0.28 deg K play, 2-3 held poses fall under 5.
6. **NEW-stop-through-drive (carried).** The groove's rise ends before the J2 dowel engages (0.17 deg of q2, about 0.37
   deg of K), so the stop load passes through the 1.5 mm pin. No force number exists.
7. **G3 (carried).** R17 passes nominal, but at f 0.05 the cuff twists 11.74 deg with 23 lags. The run drives K by the
   law, so the drive's force flow is unmeasured.
8. **NEW-pa-reread (carried).** "mu 0.15 on BOTH stages" rests on stage 1 read on the built groove, which exempts the
   back-drive band K 0.33-9.0 (35-81 deg, ungated). On the family's linear reading the limit is mu ~0.139. The row
   verdict still carries the sentence.
9. **NEW-friction-cliff (carried).** a_s +0.07 mm binds stage 1 at K 44.75, below the held stroke of 46.27.
10. **NEW-silent-check (carried).** RC_MIN 1.5 is declared and never cut on (rc_min 1.01). The worst-tolerance slop of
    0.281 deg is over the 0.25 gate.
11. **NEW-ws-inband (carried).** The raised-arm workspace in-band is 0.831, with 16.8 % of the metal above 14 mm (max
    30.7 mm). It is unscored.
12. **G4 (carried; measured on this row).** m_sub is under 1 deg on 50 of 205 rest poses.
13. **P2 (carried; negligible).** The slot length is argued from a held-out stroke.

**Retired this audit: R1.** The row verdict now opens with "VERIFIED 18.98 AS THE MODEL'S NUMBER, NOT AS A BUILDABLE
DRIVE", and the tool's reporting check reads ok. What remains of the label is NEW-pa-reread's friction sentence. The
dashboard's sweep_gap of 86.19 is a display error that understates the design (the sweep's best is 13.18), so it is not
gaming.

**Checked and clean:**
- the knee stack (stk 6.0 = the MR63ZZ pair; M2 clean);
- the dashboard number (18.98 = v_gap; R4 clean);
- no bench, judge, kit or model commit with the row since the last audit (P4 clean; the 07:29 / 07:42 commits touched
  only the verdict text);
- the density re-wear changes no take or contact (4 contacts, 372 taken, near-touch 1 mm 20.29 / 2 mm 34.84: S5, T1 and
  T5 unchanged).

## Checks the tool ran, and where my reading differs

- **held_out ok:** 23.24 (linear IK) / 23.19 (verified) vs 18.98, +4.2.
- **fast_frozen ok:** 19.04 to 18.98.
- **near_touch ok (report only):** plain 19.04, 1 mm 20.68, 2 mm 35.13, 3 mm 87.13, band read 3-14 mm 19.23.
- **contact_depth ok:** held 14 poses, 43.84 mm summed, deepest 10.38 mm. The tool still misses the bench depths
  (`+blend` dumps; proposal 1 of the 2026-10-17 audit, not applied). By hand: 4 poses, 16.15 mm, deepest 9.47.
- **continuity watch:** held knn 32.18 vs 23.19. This is the conecut chain's held sample property (lowarm-halfring
  -8.23), not the drive's. Upheld twice.
- **fold_margin ok:** 5.006. It does not read the stop-engagement th (T3).
- **idle ok, sampling ok, complexity ok (16.5), reporting ok, judge_change ok, rules ok.**
- **density watch:** the S6 finding above confirms it exactly.

## Numbers I could not get, and why

- **th at stop B / the J2 dowel** (T3): the model computes th only for the poses it takes, at their law K. Driving forced
  poses to K 46.5 needs a probe that sets K past the law, which this time box did not allow.
- **The plate-clearing level held out at the kit's density:** not run (two slots; the box was at load 11-14 on 4 cores).
  The bench lift at the kit's density is +0.38, and the frame / level re-wears so far moved bench and held alike, so I
  would expect about +0.4 held. That is an estimate.
- **Clearance of link 1b's strap at F+3.9, and a stage-1 level above link 1b with a feasible pin:** no geometry on file
  (the CAD's level scan finds 0 feasible pins above F+4.6).
- **The 28 deg of insert sector the model does not sample**, re-worn: not run.
- **Feel of the back-drive band and the drive's force flow:** no judge measures it (G3).

## Proposals (not applied; none feeds the verdict)

1. **Fix the S6 confirmation path** (instrument): in `tools/sample_density.py` `fitted()`, call `_thin(M1, thin[0],
   thin[1])` and thin at the Frozen wear model's `_truncate`, not at the second Bench. The desmo-slipper audit found that
   the held path otherwise patches the polish file's Bench(20, 20). Measured effect on this row: bench 18.65 (vs the
   re-weight's 18.68), held 22.86. Until then, quote S6 numbers as re-weights.
2. **Read density two-sided, at the sampler's pitch** (a measurement change; the lead's or the user's call):
   - use the sampler's own pitch where the model states it (ring2 0.5 x 2 mm = 4x; the boss disc 1 mm = 4x) instead of the
     cell / hull estimate;
   - re-weight sparse parts too, not only parts above 2x.

   Measured effect on this row:
   - bench: 18.98 -> 18.57 at the sampler's pitch (over-dense only), 19.02 with L2 / L1b corrected, 18.87 with every part
     at the kit;
   - the lead: 18.28 -> 18.42 with every part at the kit;
   - the gap between them: 0.70 as sampled, 0.40 at the cell reading, 0.29 at the sampler's pitch, 0.45 with every part
     at the kit.

   At every one of these readings this row stays behind the lead and slipper-nose.
3. **Quote a correction with the row's other measured corrections** (proposed catalogue entry R5, "a favourable
   re-reading quoted alone"). When a measurement change moves a row in its favour, the row should state it next to the
   row's other measured corrections at the same density: here the buildable level, 19.03 at the kit's density. Effect:
   reporting only.
4. **th at the stops** (carried from the CAD skeptic): `fold_margin` should read th where a K- or q2-clamped stop engages,
   not only on taken poses.

---

*Earlier skeptic sections below this rule (2026-10-17 21:30 and 2026-10-18 05:59 UTC), kept as written.*

## Skeptic (2026-10-17, 21:20-21:30 UTC)

Ledger entry 2026-10-17T21:28:48Z, by skeptic, run `skeptic:desmo-conecut-knuckle-3r`.

**Final verdict: WATCH.** The ledger tool takes the worst level among the reasons not refuted with evidence: 12 of 14
reasons are upheld, 2 are refuted (S2 and T1, both on the documented threshold). Rulings:
`docs/alignment/desmo-conecut-knuckle-3r.rulings.json`.

**How I checked.**
- Every number was re-read from the verifier files (`verify/desmo-conecut-knuckle-3r_v_{bench,held}_frozen{,_blend}.json`),
  the row's `verification` block, the audit's remeasure files and the `+blend` per-pose dumps, with my own short
  scripts. I did not import the audit tool.
- One new measurement: `tools/alignment_msub_rest_probe_model.py desmo-conecut-knuckle-3r bench` (CB_EXACT=1, nice 10,
  OMP_NUM_THREADS=1, 1 process, 339 s, model unchanged). It reproduces the frozen claim (19.04, reach 0.7278, ib14
  0.8924). Output: `remeasure/desmo-conecut-knuckle-3r_msub_rest_bench.json`. The farm was not used.

### Rulings

1. **continuity: upheld.** The held blend file reads static 23.19, full flood 23.19 (0 dropped), knn 32.18 (84
   dropped, all forced; 271 of 355 forced poses connected), bench-grid 24.47. The linear-IK held file shows the same
   pattern (knn 31.48, 77 dropped). The tool's line 503 rule (knn loss > 3 -> watch) is applied to the right number.
   - Partly not apples to apples: the tool takes the newest verifier file by mtime (`_verifier_outputs`, line 185), here
     the held blend file. On this row's own bench file the same check reads knn 20.67 vs 18.98 (-1.69): ok, and the
     same -1.67 to -1.69 every sibling reads on its bench file (conecut, desmo-slipper, slipper-nose).
   - Still upheld: no sibling has a held knn flood, so the held -8.99 cannot be shown to be a sample property, and the
     full flood checks no skin at its intermediate envelope nodes (minarc mechanism verifier lines 329-331). Whether the
     84 held poses can be reached without passing a contact pose is unmeasured.
2. **reporting: upheld.** The row verdict (20:48:45) still starts "SCREENED, not a new lead" under status verified,
   v_gap 18.98. morphs.json (21:12:45) carries the same text, with an empty alignment field.
3. **NEW-pa-reread: upheld.** The model's own arrays reproduce: the cap angle is above the 34.47 gate for K 0-8.995,
   above 60 for K 0-3.14, and self-locking only for K 0-0.326; at K 4.577 it is 52.71. The linear read at mu 0.15 gives
   86.52 (dK_lim 0, s1-pa-cap), and at mu 0.135 it gives 13.31. tan(43 - 35.05) = 0.1397. In the code (lines 226-243),
   s1-pa-cap cuts only when `s1_read == "linear"`; the claim uses `built`. This is a label, and its feel is unmeasured.
4. **NEW-friction-cliff: upheld.** The verifier's own `friction_probe`: a_s 9.60 binds at 44.75 (14.56), a_s 9.65 at
   43.0 (15.17), psi 150.2 at 46.0 (13.94), mu 0.17 at 45.5 (14.56). All are below the held stroke of 46.27.
5. **NEW-silent-check: upheld.** RC_MIN is imported (line 58) and used only in `lim_by_gate` (line 376). The cut dict
   has no radius entry. rc_min is 1.01 and the ridge 0.247 mm; worst-tolerance slop is 0.281 deg, over 0.25.
6. **M3: upheld.** The plate-to-horn radial gap is 0.150 mm on all 372 bench and 861 held poses: the rule's own value
   everywhere. plate_hubK is 1.23 mm. No CAD of this design exists (pipeline/ and judge/ have no desmo-conecut entry),
   so the hub-2 relief pocket is unmodelled.
7. **T3: upheld.** Held th 5.006 at i 1054 (dK 46.27, dth/dK 0.403). 5.006 - 0.403 x 0.227 = 4.91, and with 0.281
   deg it is 4.89. 46.27 + 0.227 = 46.497 is still inside stop B at 46.5, so the play is physically available there. No
   model carries a slop state.
8. **S2: refuted.** The measurement is confirmed: part-weighted 0.8844 vs sample-weighted 0.8923, which is +0.79
   points. The documented threshold is TH part_weight_watch 3.0 (ALIGNMENT.md section 5), and the tool's own sampling
   check reads ok. There is no rank effect: about 19.77 when part-weighted, behind all three siblings either way.
9. **T1: refuted.** The numbers are confirmed from the `+blend` dumps. Bench: 33 taken poses under 2 mm, 3 under 1 mm,
   closest 0.072 mm, 4 of 8 overhead poses under 2 mm. Held: 71 / 13 / 0.325 mm, 10 of 18 overhead under 2 mm. The 1-2
   mm shell is 16.09. Near-touch is report-only by the user's 2026-10-17 ruling (CLAUDE.md decisions 3 and 6), and
   `c_near_touch` keeps the level at ok (lines 277-281; SUPERSEDED in the self-test). A watch here applies the retired
   shell gate. The numbers stay in this report.
10. **NEW-ws-inband: upheld.** Workspace in-band at elevation 90-140 is 0.8308 (16.83 % of metal above 14 mm, max
    30.74 mm), against 0.8924 on the scored clip frames. The workspace number is unscored and off the 1 cm goal.
11. **G4: upheld, now measured on this row.** m_sub at rest: n 205, min 0.0, p10 0.267, under 1 deg on 50, under 2 deg
    on 65, under 5 deg on 107. This is identical to conecut. Moved poses: m_sub min 10.805, m_eff min 5.181. m_plain at
    rest min 5.389.
12. **G3: upheld.** There is no CAD, R17, cuff twist or drag reading anywhere.
13. **R1: upheld.** The row verdict still says "mu 0.15 on BOTH stages", but the verification text says "mu 0.15 is
    nominal only". The board's sweep_gap of 86.19 is not the sweep's best: the sweep file's minimum is 13.18 (k0, cell
    A, 146 rows). That is a display error, and an unflattering one.
14. **P2: upheld.** Concept doc line 15 cites the held stroke of 46.27. The "46.5 = lead dK_lim" match is slipper-nose
    `claims.lead_mu050.dK_lim` (a mu 0.05 friction limit; that row's frozen dK_lim is 49.8), so it does not show the
    value was chosen without held data. The bench claim does not depend on it, and the held drop is 4.21 < 6.

### Missed (gaming the auditor did not list)

None found. I checked these:
- **Claim selection:** two configs were worn exact (r_c 16.0 at 19.27, k57 at 19.04). k57 was pre-registered at 19:58
  (commit b368ebf), before the claim's exact wear, and was chosen on fast 13.31 vs 13.54.
- **The verified number is 0.06 better than the claim's own:** this comes from the verifier's blended-law IK, which
  follows the groove as built. The linear-law IK leaves the pin up to 0.162 mm off the groove on 93 of 184 fit poses.
  The blend is the more faithful reading.
- **Thin new-metal sampling:** the plate has 8 samples and L1a has 8. The S2 arithmetic shows the effect is under 1
  point.

Instrument notes for the next audit (not gaming):
- The continuity source depends on file mtime order.
- The held overhead near-touch (10 of 18 poses under 2 mm) was not in the audit's table.

## Skeptic, CAD-triggered audit (2026-10-18, 05:45-05:59 UTC)

Ledger entry 2026-10-18T05:59:03Z, by skeptic, run `skeptic:desmo-conecut-knuckle-3r`. It answers the auditor's
CAD-triggered entry of 2026-10-18T05:52:06Z (WATCH on claim 18.98, 15 reasons).

**Final verdict: WATCH.** The ledger tool takes the worst level among the reasons not refuted with evidence. All 15
reasons are upheld; none is refuted. Rulings: `docs/alignment/desmo-conecut-knuckle-3r.rulings.json` (this file
replaces the 2026-10-17 rulings, whose S2 and T1 refutations are no longer among the reasons).

**How I checked.** I re-read every number from the raw files with my own short scripts, without importing the audit
tool. The sources were the verifier's `_v_{bench,held}_frozen_blend.json`, the auditor's `remeasure/*ringframe*` and
`*s1level3p9*` files, and the gen-9 CAD's `build.json`, `stage1_level_scan.json`, `judge/part_contact.json`,
`judge/body_contact.json`, `judge/dynamics.json` and `VERIFY.md`. I also read the row, `morphs.json` and the model
source. Nothing new was run: the box was at load 17 on 4 cores, and an exact wear takes about 11 minutes there. $0 spent.

### Rulings

1. **continuity: upheld.** The held blend file reads full 23.19 (0 dropped) and knn 32.18 (84 dropped). The rule is
   applied as coded.
   - New since the last skeptic: a same-chain row now has a held knn flood on file. lowarm-halfring reads 22.70 to
     30.93 (-8.23, 77 dropped), and this row's linear-IK held file reads -8.24. So the held knn loss belongs to the
     conecut chain on the held sample, not to the drive.
   - Still upheld: no other chain has a held knn flood, and the full flood checks no skin at its envelope nodes.
2. **reporting: upheld.** The row verdict, unchanged since 2026-10-17 20:48, is still the screen text. The dashboard
   was rebuilt at 05:42 and carries the same text.
3. **M3: upheld, every number re-derived.**
   - Where the layer sits: build.json gives groove_mid 0.861 at glev -1.0, so the pivot is 1.289 mm below hub 2's face.
     The insert sits at F+0.111..1.611 and the short arm at F-1.825..-0.325, against the plate at F..F+3.
   - The box: the clamp [-1.0, 1.5] keeps the layer bottom at F+0.11..2.61, inside the plate for every value.
   - R6: max_depth 1.50 mm, 8 violating pairs, all stage-1 parts in l1b.
   - The re-wear: `_s1level3p9_bench.json` reads frozen 20.5, with glev_used 2.039, layer [3.15, 4.65], desmo_fail []
     and a dump that recomputes to 20.51. It ran on the same harness as the 18.98.
   - Feasible pins in the level scan: 2 at F+3.9 and 0 from F+4.6 up.
   - Note for the next audit: part of the +1.52 is the bigger ring that the a_s 9.8 pin needs (n_ring 19 to 29; the
     model's r_out grows with the pin radius, lines 250-255). That ring is real metal of the candidate, not an artefact.
4. **NEW-inherited-stack: upheld.** Confirmed: lowarm-halfring runs glev -1.0 on desmo-conecut's own
   `_desmo_build_B`, and desmo-slipper runs glev -0.5 with the same formula (line 148) and the same box (line 87).
   Neither row has an R6 reading of stage 1.
5. **NEW-sample-frame: upheld on its unmeasured half.** The frame re-wears are confirmed: 19.07 bench and 23.28 held,
   with the pin inside the model band 1.0 and inside the fixed band 0.864. The 28 deg of insert sector outside O20
   (123.88 vs 95.9 deg) is not sampled and has not been re-worn by anyone, so the +0.2 stays an estimate.
6. **T3: upheld.** The numbers are confirmed: held 5.006 (pose 1054, dK 46.27, slope 0.403), 0 poses under 5, and
   bench 5.181. The red team's slope 0.08 gives 4.986 on one pose.
   - Why I did not refute it as "the rule as written": the rule has a second clause, "a model that clamps another angle
     must show its stops engage at >= 5 deg of th". Stop B and the J2 dowel clamp K and q2 at K_law 46.5, not th.
   - No file reports th at that stop. The verifier's own slope carried from pose 1054 to K 46.5 gives about 4.91 even
     without play. That is an estimate, not a measurement.
7. **NEW-stop-through-drive: upheld, now from the CAD's own numbers.** The groove's rise ends at q2 -14.282. The J2
   dowel's window is -14.315 and it engages at -14.455. So the drive meets its end 0.17 deg of q2 (about 0.37 deg of K)
   before the dowel touches. No force number exists.
8. **G3: upheld.** The nominal case passes. At f 0.05 the cuff twists 11.74 deg (23 lags over 10 deg) on s1 and 11.78
   deg (29 lags) on s2. K is driven by the law (law error 0.099), so the drive's own force flow is unmeasured.
9. **R1: upheld.** The dashboard row is status verified, v_gap 18.98, sweep_gap 86.19, with the "BOTH stages" text. It
   says nothing of R6 1.50 or R16 24.2 %.
10. **NEW-pa-reread, NEW-friction-cliff, NEW-silent-check, NEW-ws-inband, G4, P2: upheld, unchanged.** The row file is
    unchanged since the 2026-10-17 skeptic, and the fields re-read the same. The F+3.9 candidate shows the same stage-1
    pattern: cap 35.7 vs gate 34.47, linear pa_cap limit 0.0, rc_min 1.02 with radius limit 0.75.

### Missed (for the next audit; not counted in this verdict)

- **No stop-engagement th on file.** The CLAUDE.md rule asks a K- or q2-clamped design to show th >= 5 where its stops
  engage. Here stop B and the J2 dowel engage at K_law 46.5, but th is reported only on taken poses (held 5.006 at
  46.27). The verifier's slope, extrapolated, gives about 4.91 at the stop for pose 1054's direction. For bench pose 313
  the same extrapolation gives 5.181 - 0.405 x 0.88 = 4.83, if that direction can reach the stop. Both are estimates.
  The tool's fold_margin check reads only the taken-pose minimum, so it cannot see this.
- **The verified claim's search optimum sits on the infeasible edge.** glev -1.0 is the box's lower edge, where the
  sector is lowest and the scored in-band is highest (0.893, against 0.8786 at glev 1.5 and 0.8778 at F+3.9). The whole
  box lies inside link 1b's plate (M3). The optimiser bought in-band from an unchecked clash.
  - That is the M3 pattern on the plain gap, worth +1.52 bench to the candidate level. It is not a rank change: the row
    is not the lead, and 20.50 is behind the rows the auditor lists.
  - The gen-9 CAD and EVOLUTION entry were built "AS MODELLED" (build.json stage1_mode "model"). Their judged
    R-numbers belong to the unbuildable level.
- **Checked and clean:** the stage-1 parts have 0 body contact in the CAD (judge/body_contact.json parts: pin, short
  arm, crank, insert and link 2 all max_depth 0.0). The s1level re-wear really ran at glev 2.039 (glev_used), and the
  WIP s1raised file's 20.42 ran clamped at 1.5, as the auditor said.

**Final verdict (ledger tool): WATCH.**

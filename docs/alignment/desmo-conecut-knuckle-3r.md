# Alignment audit: desmo-conecut-knuckle-3r

First audit of this row (discovery round 13, slice r13-A: screened 20:09, verified 20:48 UTC 2026-10-17). Run
20:49-21:18 UTC on the box (at most 2 niced processes; the farm was not used).

- **Ledger entry:** 2026-10-17T21:17:26Z, by auditor, run `audit:desmo-conecut-knuckle-3r`. Verdict **watch**, tool
  verdict watch, claim v_gap 18.98. Reasons: 2 tool reasons (continuity, reporting) and 12 judgement findings, all watch.
- **Checks:** `docs/alignment/desmo-conecut-knuckle-3r.json` (tool VERSION 2026-10-17.6, `--ref slipper-nose-knuckle-3r`).
- **Findings:** `docs/alignment/desmo-conecut-knuckle-3r.findings.json` (11, all watch).
- **Re-wears and probes written by this audit** (the model ran unchanged; only its `audit()` was wrapped, or its
  locals read with a return-trace):
  - `remeasure/desmo-conecut-knuckle-3r_bench.json`: frozen exact Bench(110,360) 19.04 (the claim's linear-law IK),
    with near-touch, metal histogram, coordinate spans and part in-band.
  - `remeasure/desmo-conecut-knuckle-3r_held.json`: frozen held out 23.24 (linear-law IK; the verifier's blended IK reads 23.19), near-touch 1 mm 26.09 / 2 mm 37.56 / 3 mm 84.36, band read 3-14 mm 23.42, closest metal 0.325 mm, knee angles 59.27-107.07.
  - `remeasure/desmo-conecut-knuckle-3r_probe_bench.json`: `tools/alignment_wear_probe_model.py` (unscored workspace
    in-band, standoff, clearance floor, reach by elevation, own-state fold margin).
  - `remeasure/desmo-conecut-knuckle-3r_s1read_check.json`: the stage-1 reading probe (fast Bench(60,160), five cells).
  - `remeasure/desmo-conecut-knuckle-3r_blendband_fast.json`: the new probe `tools/alignment_blend_band_probe.py
    --no-wear` (the built-groove back-drive pressure angle through the blend, read from the model's own arrays with a
    return-trace). Its frozen-wear part (the taken poses' K histogram) was stopped at 21:16 after 11 CPU-minutes on a
    box at load 6-8, to keep the time box.

## Verdict: WATCH, claim v_gap 18.98 (score 93.10), held out 23.19

Nothing in the number is gamed and no hard rule is broken. The verified 18.98 is the verifier's blended-law IK wear; the
claim's linear-law 19.04 reproduces exactly here (re-wear 19.04, per-pose dumps recompute to 18.99 / 19.05). The design
is behind every sibling on the plain gap (slipper-nose 18.49, conecut 18.28, desmo-slipper 18.95), so its number does
not buy it a rank. What it sells is a story: "spring-free, roller-free, the first desmo-family drive holding mu 0.15 on
both stages, at complexity 16.5". Two parts of that story are weaker than the row's verdict text says:

1. **The mu 0.15 claim rests on a gate the screener re-read for this design** (NEW-pa-reread). Read the way desmo-slipper
   was read, the same placement holds mu ~0.139, the same as desmo-slipper's jam at 0.14. The real gain is stage 2.
2. **At mu 0.15 the drive sits 0.07 mm from a cliff** (NEW-friction-cliff, the verifier's own probe).

Neither changes the score: at mu 0.087 or 0.135 on the linear reading the fast gap is the claim's 13.31.

## Ruling asked of the auditor: the built-groove stage-1 reading

The concept doc (Next, item 2) asks the auditor to rule on reading stage 1 on the built blended groove. My ruling, from
the model's own arrays (`tools/alignment_blend_band_probe.py`, `remeasure/desmo-conecut-knuckle-3r_blendband_fast.json`):

- **Where the reading applies.** The blend runs over K 0 to 10.72 deg (half-blend 10.77 deg of the linear law's K), a
  quarter of the 46.5 deg stroke. Through it the built cap-side (back-drive: the pin pushing link 2's cap ring)
  pressure angle falls from 89.9 deg at K 0 to 31.8 at K 9.8 (rows: K 0.25 82.7, 1.0 74.6, 2.2 65.7, 3.3 59.3,
  4.6 52.7, 6.1 45.9, 7.8 38.9, 8.8 35.3).
- **What is a lock and what is not.** At mu 0.15 the back-drive self-locks above 81.47 deg (90 - atan mu): only for
  K < 0.33 deg. That is the dwell lock, and exempting it is right: every blended dwell-rise groove has it, and a lock
  that holds K at rest against the cuff's load is the slaved coordinate's job. From K 0.33 to 9.0 the back-drive is
  NOT locked; it runs at 34.5-81 deg, above the family's 43 - atan(mu) margin gate, and the built reading leaves it
  ungated. The rest pose (dK 4.6, ~52.7 deg) and the taken overhead pose at axial -135 (dK 5.8, ~47 deg) live there.
- **Ruling.** The built reading is the right place to read the groove: it is the groove that is cut, and the linear
  law's kink is not (the linear read's 35.05 deg at K 0 is a kink artefact). Exempting the true lock (K < 0.33 here) is
  right. But no blended groove can pass the family's 43 - atan(mu) back-drive gate next to its dwell, because the cap
  angle goes to 90 as the law's slope goes to 0; so the exemption the screener chose (the whole blend, K 0-10.72) is a
  convention, not a measurement, and under it the back-drive from K 0.33 to 9.0 runs at 35-81 deg ungated. Neither
  reading measures whether the wearer feels that. The honest friction label is therefore: **stage 2 (the inverted
  slot) holds mu 0.15 with margin, a real gain over desmo-slipper's flank (43-44.5 deg of K at mu 0.135-0.15); stage 1
  is desmo-slipper's, with the first 9 deg of back-drive ungated under either reading, and its forward side 0.07 mm
  from a bind at mu 0.15.** "The first desmo-family drive holding mu 0.15 on both stages" compares a built-read claim
  with desmo-slipper's linear-read jam (mu 0.14); the same stage 1 on the same reading would read the same.
- **Score.** Unaffected: fast 13.31 at mu 0.087 and at mu 0.135 on the linear reading, equal to the claim
  (`remeasure/desmo-conecut-knuckle-3r_s1read_check.json`). A watch on a label, never a refutation of 18.98.
- **Equal-placement control.** Not available: cell A (the desmo stage 2 unchanged) at the claim's seat r_c 16.176
  fails its flank cusp at K 0 at any mu (fast 86.44 at mu 0.15 and 0.087, same file), so the inversion cannot be
  compared with the flank at this placement.

## What the wearer gets (measured)

All on the frozen claim (exact Bench(110,360) unless stated). Sources: `remeasure/desmo-conecut-knuckle-3r_bench.json`,
`_probe_bench.json`, the verifier's `+blend` per-pose dumps, `verify/desmo-conecut-knuckle-3r_v_*_blend.json`.

| what | bench | held out |
|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 (0.286) | 18 / 71 (0.254) |
| raised-arm reach (elev >= 90), taken / total | 47 / 113 (0.416) | 123 / 300 (0.410) |
| reach by elevation band 90-120 / 120-140 / 140-160 / 160+ | 27/51, 12/34, 5/13, 3/15 | - |
| why overhead poses are lost (ws, elev >= 140) | fold 14, contact 3, J3 stop 3 | - |
| taken poses with metal < 2 mm (< 1 mm) | 33 (3) of 372 | 71 (13) of 861 |
| closest taken metal | 0.072 mm (pose 139, plane -60 / elev 60 / axial 105) | 0.325 mm |
| taken overhead poses with metal < 2 mm | 4 of 8 | - |
| contact poses, summed depth, deepest | 4, 16.15 mm, 9.47 mm (pose 237, 15 / 165 / -60: crank -9.42, tip plate -5.87) | 14, 43.84 mm, 10.38 mm (pose 683, 45 / 165 / -30) |
| scored in-band 2-14 (clip frames) | 0.893 (verified), 0.892 (linear IK) | 0.892 |
| unscored workspace in-band: all taken / elev 90-140 / overhead | 0.863 / 0.831 (16.8 % of metal > 14 mm, max 30.7 mm) / 0.933 | - |
| fold margin th, min over taken | 5.181 deg (0 under 5) | 5.006 deg (pose 1054, at dK 46.27, the slot end) |

- **Springs:** none. K is slaved by a two-stage desmodromic drive (stage 1: a crowned O1.5 440C pin in a two-walled
  groove in hub 2's cap ring; stage 2: an O1.5 nose on link 1a in a 3.72 mm slot in the crank's tip plate).
- **Stops:** the J2 fold (88 bench / 260 held poses lost), the J3 dowel (j3stop, 3 overhead poses), the slot's far end
  (stop B at K 46.5; the held stroke uses 46.27), and the knee window 25.22-154.78 (the taken knee angles 59.27-105.94,
  34 deg clear).
- **Cuff twist, drag, R17:** not measured (no CAD, no dynamics run).
- **Near-singular postures:** the th margin sits at 5.0-5.2 deg at the slot end (T3); the sub-dyad m_sub is carried from
  conecut (under 1 deg on 50 of 205 rest poses there; G4).
- **Same arm, same takes as conecut.** The 262 taken workspace poses, the 4 bench contacts and the near-touch counts are
  conecut's. The drive swap changes metal (+0.67 by sample weight from desmo's cap-ring sector, +0.09 from the
  inversion: the row's S6 decomposition), not where the arm can go.

## Findings (all watch; `desmo-conecut-knuckle-3r.findings.json`)

1. **NEW-pa-reread (proposed catalogue entry T6, "a gate re-read for the design that carries the claim").**
   - *Looks like:* a claim passes a gate its family failed, because the claimant re-defined where the gate applies.
   - *Here:* stage 1's cap (back-drive) side is gated only outside the blend. Inside the blend (K 0-10.72) the back-drive is above the gate from K 0 to 9.0
     and self-locking only to K 0.33. On the
     family's linear reading the claim placement fails at K 0 at mu 0.15 (cap 35.05 vs 34.47) and holds mu ~0.139.
   - *Why not better:* the wearer gets the same stage 1 as desmo-slipper; the "first desmo drive at mu 0.15" is half a
     reading. Stage 2's inversion (PA stroke 64.5 to mu 0.15) is a real gain.
   - *Action:* state the friction claim under both readings in the row verdict; adopt one reading for the family
     (proposal 2).
2. **NEW-friction-cliff (carried).** a_s +0.07 mm binds stage 1 at K 44.75 (fast 14.56), below the held stroke 46.27.
   *Action:* report "mu 0.15 nominal; mu 0.087 robust"; put a_s / psi tolerances on the drawing, or move the placement
   to where a_s +-0.1 holds.
3. **NEW-silent-check (carried).** RC_MIN 1.5 declared, never cut; the claim's rc_min is 1.01 (ridge 0.25 mm, 440C
   insert). Worst-tolerance crank-free slop 0.281 deg > the 0.25 gate. *Action:* proposal 3.
4. **M3.** The stage-1 arm and pin inside hub 2's O20 footprint are unchecked (relief pocket assumed); the new tip plate
   rides 0.150 mm over link 1a's boss on every pose, and 1.23 mm from hub K's O20. *Action:* L1 CAD of the J2 seat stack
   and the plate / boss layer with their stack tolerances.
5. **T3 (carried).** th 5.006 held at the slot end; K play 0.227 deg (0.281 at worst tolerance) takes it to ~4.9.
6. **S2.** Tip plate 8 samples (0.719 in band, median 12.3 mm), ring sector 19 (0.542, 13.8 mm); sample-weighted in-band
   flatters this row by 0.79 points where it under-reads the siblings by 0.73-2.87. No rank changes.
7. **T1 (report only).** 33 / 71 taken poses with metal under 2 mm, closest 0.072 mm; 4 of 8 taken overhead poses
   under 2 mm. Same as conecut.
8. **NEW-ws-inband (carried).** Raised-arm workspace (elev 90-140) in-band 0.831 with 16.8 % of the metal above 14 mm
   (max 30.7 mm), unscored.
9. **G4 (carried).** Same chain as conecut, whose sub-dyad is under 1 deg on 50 of 205 rest poses.
10. **G3 (missing measurement).** No CAD, no R17, no cuff twist, no drag; the back-drive band's force flow is unmeasured.
11. **R1.** The row verdict still says "passes every drive gate at mu 0.15 on BOTH stages"; the dashboard (rebuilt 20:57)
    now shows "verified" 18.98 but carries the same screen text and a failing sweep best (86.19). *Action:* the lead
    updates the verdict text (with the verifier's "nominal only" and both friction readings).
12. **P2 (negligible).** The slot length was argued from a held-out stroke (46.27); its value equals the displaced lead's
    own dK_lim 46.5. At least +0.3 held points at stake, none on the bench.

## Checks the tool ran, and where my reading differs

- **held_out ok:** held 23.19 vs bench 18.98 (+4.21), inside the family's +4 to +4.6.
- **fast_frozen ok:** self 19.04 to verified 18.98.
- **near_touch ok (report only):** plain 19.04, 1 mm 20.68, 2 mm 35.13, 3 mm 87.13, band read 3-14 mm 19.23.
- **contact_depth "not measured", but the depths ARE on file.** The verifier wrote the per-pose dumps of the verified
  config as `remeasure/desmo-conecut-knuckle-3r+blend_{bench,held}_perpose.json`. The tool globs `<id>_*perpose*`, so
  it misses the `+blend` files, and the plain-named dumps carry the linear-IK 19.04 / 23.24, 0.06 / 0.05 off the
  claim (its +-0.05 rule). Read by hand (my sum of -min_mm over contact poses): bench 4 contacts, 16.15 mm, deepest
  9.47 mm (pose 237, plane 15 / elev 165 / axial -60: crank -9.42, tip plate -5.87); held 14 contacts, 43.84 mm,
  deepest 10.38 mm (pose 683, 45 / 165 / -30), 5 deeper than 3 mm. Reference slipper-nose: bench 2 / 14.75 mm, held
  10 / 46.12 mm (x1.09 and x0.95: no T5). conecut: bench 4 / 20.24 mm, held 14 / 60.97 mm. The contacts are conecut's
  poses; the summed depth is lower than conecut's because pose 264 is shallower (1.17 vs 5.80 mm).
- **dominance ok:** vs slipper-nose plain -0.55, 2 mm -2.11 (behind on both).
- **continuity watch (tool), not S5 in my reading.** The tool read the held file (knn flood 32.18 vs static 23.19,
  -8.99) where for the siblings it read the bench file. The rule's flood (full envelope) drops 0 on both wears. On the
  bench the knn flood reads 20.67 vs static 18.98 (-1.69), the same loss as conecut (19.97 vs 18.28, -1.69). No
  sibling has a held knn flood on file, so the -8.99 has no comparison. I add no S5 finding; the tool's watch stands.
- **fold_margin ok:** 5.006 held (see T3 for the K play).
- **idle ok:** dK span 45.61 deg, knee K.ang 59.27-105.94 deg (window 25.22-154.78: 34 deg to the knee stop).
- **sampling ok (tool), S2 in my reading:** part-weighted 0.884 vs sample-weighted 0.892 (see S2).
- **complexity ok:** 16.5 recomputed (2 passive rotations 2, 2 loops 8, 3 joints beyond 3, 2 sliding pairs 2, 2 made
  parts beyond 7 x 0.5, 2 bought beyond 6 x 0.25; the knee 0). Nothing hidden: the 440C ring insert and the J3 dowel
  are counted; the tip plate is integral to the crank and the boss to link 1a's hub-K member.
- **reporting watch:** the row's verdict text still reads as the screen (R1). The dashboard status / v_gap caught up at 20:57.
- **judge_change ok, rules ok.**

## Numbers I could not get, and why

- **Feel (R17, cuff twist, drag):** no CAD and no dynamics run exist for this design; the drive has no spring, so there
  is no preload to sweep, but the drag of two sliding pairs at 0.01 mm clearance and the force flow through the
  back-drive band are unmeasured (G3).
- **The full held dK histogram** (for the size of P2 and the held share of poses in the blend band): the blend-band probe
  wears the bench only (time box).
- **The hub-2 relief pocket clearance** (M3): no geometry of the J2 seat stack exists in the model.
- **K play carried into th per pose** (T3): the models carry no slop state; the ~0.09 deg is the verifier's dth/dK
  estimate.
- **The m_sub reading at rest for this row** (G4): carried from conecut's measurement on the identical chain.

## Proposals (not applied; none feeds the verdict)

1. **T5 reads the verifier's `+blend` dumps** (instrument fix, `tools/alignment_audit.py` `_depth_sources`): glob
   `<id>[_+]*perpose*.json` and key the pair by the stripped name. Measured effect on this row: contact_depth goes from
   "not measured" to ok (bench 16.15 mm vs 14.75, held 43.84 vs 46.12). On every other verified row: no change (no
   other row has a `+` dump whose gap is its v_gap; desmo-slipper's `+blend` / `+claim` dumps are 18.59 / other
   placements, not its 18.95). Until then a verifier should also write the verified config under `<id>_vblend_...`.
2. **One friction reading for the desmo family** (a measurement change; the user's or the lead's call). Read stage 1 on
   the built groove for every desmo row (desmo-slipper included); exempt only the self-locking band (cap angle above
   90 - atan(mu)), and report, not gate, the back-drive angle between that band and the blend's end, as a profile
   (K, angle), next to the forward-side bind K and its a_s / psi tolerance. A 43 - atan(mu) back-drive gate next to a
   dwell is unsatisfiable for any blended groove, so it should not be the rule; the feel question goes to proposal 4. Measured
   effect on the verified rows: none on any score (the frozen claims run at their own mu, and this row's score is the
   same 13.31 fast at mu 0.087 / 0.135); it changes only the friction label: this row "holds mu 0.15 (built) / 0.139
   (linear)", desmo-slipper "jams at 0.14 (linear)". No other verified row has a desmo stage 1.
3. **Enforce or delete RC_MIN** (desmo-slipper and this model): a declared gate that never cuts is a silent check. If the
   440C insert is the answer, the model should say `RC_MIN = pin radius + ridge_min` and cut on it.
4. **Back-drive force-flow judge** (new instrument): in a closed chain with a self-locking back-drive band, the dynamics
   judge (R17) should report where the wearer's force must come through and how large it gets. No judge does this.

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

# Alignment audit: desmo-conecut-knuckle-3r

First audit of this row (discovery round 13, slice r13-A: screened 20:09, verified 20:48 UTC 2026-10-17). Run
20:49-21:15 UTC on the box (at most 2 niced processes; the farm was not used).

- **Ledger entry:** LEDGER_PLACEHOLDER
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
  - `remeasure/desmo-conecut-knuckle-3r_blendband_bench.json`: the new probe `tools/alignment_blend_band_probe.py`
    (built-groove back-drive pressure angle through the blend; taken poses' K histogram on the frozen wear).

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
the model's own arrays (`tools/alignment_blend_band_probe.py`, `remeasure/desmo-conecut-knuckle-3r_blendband_bench.json`):

BLEND_RULING_PLACEHOLDER

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
   - *Here:* stage 1's cap (back-drive) side is gated only outside the blend. BLEND_FINDING_PLACEHOLDER On the
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
2. **One friction reading for the desmo family** (a measurement change; the user's or the lead's call). Gate stage 1's
   cap (back-drive) side on the built groove wherever the pin moves, at the same 43 - atan(mu), and report the dwell
   lock separately; or keep the built reading and report every desmo row's friction limit under BOTH readings. Measured
   effect on the verified rows: none on any score (the frozen claims run at their own mu, and this row's score is the
   same 13.31 fast at mu 0.087 / 0.135); it changes only the friction label: this row "holds mu 0.15 (built) / 0.139
   (linear)", desmo-slipper "jams at 0.14 (linear)". No other verified row has a desmo stage 1.
3. **Enforce or delete RC_MIN** (desmo-slipper and this model): a declared gate that never cuts is a silent check. If the
   440C insert is the answer, the model should say `RC_MIN = pin radius + ridge_min` and cut on it.
4. **Back-drive force-flow judge** (new instrument): in a closed chain with a self-locking back-drive band, the dynamics
   judge (R17) should report where the wearer's force must come through and how large it gets. No judge does this.

# Alignment audit: minarc-stop-knuckle-4r (2026-10-17)

Auditor run `audit:minarc-stop-knuckle-4r`, new session after the old one hit its usage limit. This audit applies the
user's 2026-10-17 rulings: a sensed joint is a joint (so this design has 4 joints), the 2 mm near-touch dominance gate
(A1) is retired (the plain verified gap decides, contact stays metal < 1 mm), and every check stays kinematic.

## Verdict and claim

- **Ledger verdict: WATCH** (printed by `tools/alignment_ledger.py`; see the ledger entry of this run).
- **Claim:** the ledger's claim is `polished_gap` **18.40** (score 93.31), the confirmed final polish pick1. The row's
  `v_gap` 19.54 is the earlier verified config BDp. Both were re-worn here.
- **In one line:** the number is real (re-worn to the digit), but it is not evidence of a better exo than the 3-joint
  rows. The 4th joint buys about 9 mid-range workspace poses and no overhead pose. The polish that produced 18.40
  takes fewer overhead poses than BDp and presses metal twice as deep into the arm on the poses next to its new reach.
  No finding reaches 'gamed': no design that is better for the wearer on every axis is ranked below it.

## What the wearer gets (measured)

RE-WEAR-TABLE

Sources: this audit's re-wear `docs/alignment/remeasure/minarc-stop-knuckle-4r_{pick1,BDp}_probe_{bench,held}.json`
(`tools/alignment_wear_probe_minarc.py`, new; it runs `docs/concepts/verify/minarc-final-polish-verify.py` unchanged
and only wraps the harness's `near_touch` to capture the worn bench), and the verifier files in
`docs/research/minarc_final_polish/verify/`.

- **Springs:** one clock spring at K. The bench treats K as geometry. As built (0.04 N.m preload) it passes R17 upright
  only: Reach a high shelf drifts 3.72 deg upright, but 4.12-7.70 deg with gravity across the thorax (fails the 5-deg
  rule in 3 of 4 directions). At 0.08 N.m it lags 9.28 deg upright (`docs/research/pick1_k_hold_check.md`).
- **Stops:** J2 dowel slot at the 5-deg J1-J3 margin (+0.5 built); K stop B at dK 56.65 deg; knee window ang_min
  26.14 in the model, 30.5 in the CAD.
- **Cuff twist:** 2.00 deg upright on R17; up to 3.83 deg with the thorax tilted.
- **Near-singular postures:** own-state J1-J3 margin min 5.623 (bench) / 5.586 (held out) at the 5.5 priced rule;
  107 of 380 taken bench poses under 10 deg. In forced poses the plain dyad is 22.8 deg past its own fold: the margin
  exists only because K opens. J1 swings up to 31 deg per 10-fps frame at the clips' peak arm speed. The taken knee
  reaches 152.75 deg held out, 27.3 deg from straight.

## Findings

Each finding is in `docs/alignment/minarc-stop-knuckle-4r.findings.json` with its evidence. All are 'watch'.

FINDINGS-LIST

## Checks of the tool (`docs/alignment/minarc-stop-knuckle-4r.json`)

TOOL-CHECKS

## Rule changes of 2026-10-17 applied here

- **A1 retired.** No reason in this entry cites the 2 mm dominance gate. The 2 mm numbers are reported, not used as a
  gate. The tool's `dominance` check still compares at 2 mm (it is the tool's code, unchanged); it reads 'watch' or
  'ok' here and decides nothing.
- **K is a joint.** This entry counts K as the 4th active joint: complexity 52 (`tools/simplicity.py`), not 33.
  The earlier ledger entry for this design (seed, 2026-10-16 20:26) carried no reason that treats K as passive; the
  ALIGNMENT.md text that does (G5, G6, section 3 item 6, proposal A5) is listed below for whoever next edits that file.
- **ALIGNMENT.md text now out of date** (not edited by this audit; other auditors are working in that file):
  - G5: "Its mechanism record still counts K as a sensed passive: 6 points instead of 25" - the record now counts K as
    active (active 4, sensed passive 2); only the row's `complexity` field (33.0) is stale.
  - G5 / G6 / item 6: "The user's question ... is open" - answered on 2026-10-17: a sensed joint is a joint.
  - A5 ("Count a sensed joint in the shoulder chain as active until the user rules"): adopted by the user's ruling.
  - A1: already marked "ADOPTED IN PART"; the dominance-gate part is now retired.

## Proposals (measurement or reporting changes for the lead or the user; none applied, none used in the verdict)

- **B1. Report overhead taken poses with every claim, and flag a polish that loses them.** Each claim states the
  workspace poses at elevation >= 140 it takes (closed, no contact, connected), bench and held out, next to the gap.
  A tightening for the user to decide: a polish may replace a verified config only if it does not lose overhead
  taken poses held out.
  - Measured effect: minarc pick1 would not replace BDp (held out 12 vs 16 of 71 with the fit-60 shape, 16 vs 17
    with the env-fit shape; bench 7 vs 8 of 28). No other verified row has a polish swap (the sidecar-longdyad polish
    was already rejected). Overhead taken on the bench, for reference: sidecar-longdyad 8 of 28
    (`remeasure/sidecar-longdyad-knuckle-3r_probe.json`); other rows are not measured.
- **B2. Report the deepest contact and the contact poses deeper than 3 mm with every claim.** The contact term
  counts a 14.6 mm press like a 0.1 mm graze. Reporting only; any depth weighting is the user's call.
  - Measured (bench): pick1 11 contact poses, deepest -13.17 mm; BDp 4, -6.41 mm; sidecar-longdyad 4, -4.61 mm.
    Held out (fit-60 shape): pick1 35, -14.61 mm; BDp 13, -7.27 mm.
- **B3. Compare held-out numbers only within one fit protocol in status lines.** README's "held out 21.31" (env fit)
  sits next to sidecar-longdyad's 22.67 (fit 60). Effect: minarc's line reads 22.69 (fit 60), a tie with 22.67.
- **B4. Recompute a row's `complexity` in the same commit that changes its mechanism record.** Effect today: minarc
  33.0 -> 52.0 (the tool's complexity check flags the mismatch).
- **B5. Hold the knee window at the CAD's stop (ang_min 30.5) in claims, or re-score the claim with it.** Effect:
  pick1 loses about 4 held-out poses (about 0.4 gap points held out), 0 on the bench; BDp 1 held-out pose.

## Not measured, and why

- `tools/alignment_audit.py remeasure` cannot wear this design: it loads the variant-A model
  (`docs/concepts/models/minarc-stop-knuckle-4r.py`) with variant-B params, while the verified numbers come from the
  kit-rule model through the judge's harness with built-stop pricing. The new adapter
  `tools/alignment_wear_probe_minarc.py` wears both verified configs exactly as their verifier did. Its pick1 bench
  output is also written in the remeasure format (`remeasure/minarc-stop-knuckle-4r_bench.json`) so that `audit`
  reads it.
- Per-part sample counts (S2): the harness does not export its metal groups per sample. Only the screen's per-part
  fractions are on file (hub 3 0.664, link 2 0.779 in band for BD), so the tool's `sampling` check stays 'watch'.
- The knn continuity flood (proposal A4) was not run. Both of the verifier's floods (kinematic and contact-aware) drop
  0 poses for pick1 and BDp.
- The spring, the feel and the forced swing were not re-run here. Their numbers come from the independent checks
  `docs/research/minarc_pick1_redteam.md` and `docs/research/pick1_k_hold_check.md`.
- A K-locked control of pick1 (how many poses K alone buys) was not run. The row's early numbers at the pin knee's
  seats are 26.82 with K locked against 24.00 with K.
HELD-STATUS

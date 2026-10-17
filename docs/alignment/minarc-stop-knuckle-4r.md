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

1. **G6, a 4th sensed joint against 3 active joints.**
   - Evidence: plain, pick1 is 18.40 against roller-longdyad 18.67 (+0.27, under one workspace pose = 0.278) and
     sidecar-longdyad 18.91 (+0.51). On the same held-out protocol (fit Bench(60,160), wear the 1154 held-out poses
     exact) it is 22.69 against sidecar-parallelogram 22.03, sidecar-longdyad 22.67 and roller-longdyad 23.73. At
     1 mm it is 23.36 against 20.00 / 20.22 / 20.30 on the bench, and 26.73 against 25.75 / 24.44 / 26.83 held out.
   - Why it is not a better exo: the 4th joint buys 9 workspace poses on the bench (reach 0.750 vs 0.725), none
     overhead (7 of 28 vs sidecar-longdyad's 8 of 28). It costs a joint, complexity 52 vs 49, and contact
     (11 vs 4 bench poses with metal inside the skin, deepest -13.17 vs -4.61 mm).
   - Action: none on the score. README's "Best verified overall" line should say the lead it holds is plain-only and
     within one to two poses; the user's ruling already names the 3-joint rows as the leaders.
2. **NEW-overhead-traded, the polish gained reach away from overhead.**
   - Evidence: pick1 replaced BDp (19.54 -> 18.40 bench, 24.18 -> 22.69 held out) but takes fewer overhead workspace
     poses (elevation >= 140): bench 7 vs 8 of 28; held out 12 vs 16 of 71 (fit-60 shape), 16 vs 17 (env-fit shape).
     Its gain is about 35 held-out workspace poses at mid and low elevation (reach 0.7195 vs 0.6828). The polish
     note's "overhead grid nodes rise from 32 to 44" counts kinematic closures, not poses the wearer takes.
   - Why it is not a better exo: the goal puts overhead first; the gap weighs every workspace pose equally.
   - Action: proposal B1. Not gamed, because BDp loses about 35 held-out workspace poses.
3. **NEW-depth-blind-contact, the new reach comes with deeper metal in the arm next to it.**
   - Evidence: contact poses bench 11 vs BDp 4 (deepest -13.17 vs -6.41 mm, both overhead at elevation 165); held
     out 35 vs 13 (fit-60), 28 vs 9 (env fit); deepest -14.61 vs -7.27 mm. The deepest is the side wall of hub K's
     18.25 mm stack in the raised deltoid; next is the knee link and pad 10 mm into the chest wall with the arm across
     the body. R1-aim (in-band 2-10) held out 0.563 vs 0.593. In-band never samples hub K's cap.
   - Why it is not a better exo: "never touching" is the first line of the goal; the score charges a 14.6 mm press and
     a 0.1 mm graze the same, and both only as poses not taken.
   - Action: proposal B2. Not gamed: no clip frame touches, and BDp cannot close 19 of pick1's 28 env-fit contact poses.
4. **G5, complexity hidden by a stale field.** The row's `complexity` is still 33.0 (and its mechanism note and HANDOFF
   lines 79-80 say 33) after the record was changed to 4 active; `tools/simplicity.py` gives 52.0, which the
   dashboard shows. The knee's 2 sensed pins are the same open question as in the sidecar-longdyad audit: counted as
   joints, this design reads 6 coordinates, over the cap of 4. Action: proposal B4; the knee-pin question is the
   user's.
5. **R2, stale leader text and a mixed row.** The row's and the dashboard's verdict strings still open with "VERIFIED
   LEADER" (BDp 19.54). The dashboard pairs pick1's v_gap 18.40 with BDp's verdict, held-out and complexity text. The
   sweep record is still the refuted 6.19. The tool's reason "the dashboard flatters the design" (18.4 vs 19.54) is
   partly a false positive: 18.40 is independently confirmed, only stored in `polished_gap`, not `v_gap`.
6. **NEW-mixed-protocol, held-out numbers from two protocols side by side.** README shows pick1 "held out 21.31"
   (env fit) next to sidecar-longdyad "held out 22.67" (fit 60). On one protocol they tie (22.69 vs 22.67). The env
   fit flatters minarc by 1.38 and makes sidecar-longdyad's verified config 2.59 worse
   (`docs/research/sidecar-longdyad-knuckle-3r_final_polish.md`). Minor P2 note: 2 env poses sit 1.66 / 1.97 deg
   from held-out poses; the fit-60 protocol does not use env, so pick1's +1.49 over BDp stands. Action: proposal B3.
7. **T4, the knee window below the polish lesson.** The polish's ang_min floor was BDp's 24.95; pick1 sits at 26.14,
   below the >= 30 FINDINGS set for polishes after the GPU-knee case. Held out the knee reaches 152.75 deg (27.3 deg
   from straight; window margin 1.11 deg), with 4 taken held-out poses past H1's 149.5. The CAD's 30.5 stop removes
   them, and the verified held-out number was not re-scored for it (about 0.4 points). Action: proposal B5.
8. **G4, near-singular postures.** 107 of 380 taken bench poses sit under 10 deg of J1-J3 margin; in the 86 forced
   poses the plain dyad is 22.8 deg past its fold, so the margin depends on K opening freely; J1 swings up to 31 deg
   per 10-fps frame at the clips' peak arm speed. Action: the MuJoCo feel check before the spring is frozen.
9. **M5 / G3, a spring with a narrow window.** The score treats K as geometry. As built, 0.04 N.m passes R17 only
   upright (drift 3.72 deg); with gravity across the thorax it drifts 4.12-7.70 deg (fails in 3 of 4 directions) and
   the cuff twists up to 3.83 deg. 0.08 N.m lags 9.28 deg upright. pick1's K moves 15.8 deg at 52 deg/s on "Reach a
   high shelf" where BDp's moves 0.85 deg. Action: a posture sweep in R17 (proposal in pick1_k_hold_check.md).
T1-ITEM

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

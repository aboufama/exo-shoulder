# Alignment audit: longstroke-slipper-knuckle-3r

Auditor run 2026-10-17 09:05-09:40 UTC (hourly 09:03). Ledger: `docs/alignment/ledger.jsonl`, `by auditor`, run
`audit:longstroke-slipper-knuckle-3r`. Checks: `docs/alignment/longstroke-slipper-knuckle-3r.json` (tool VERSION
2026-10-17.2, `--ref slipper-nose-knuckle-3r`). Findings: `docs/alignment/longstroke-slipper-knuckle-3r.findings.json`.
All local compute ran at 2 processes or fewer, nice 10, OMP_NUM_THREADS=1. Farm spend for this audit: $0.

## Verdict: WATCH (no gamed reason)

The claim is honestly worse than the leader. The ghost it produced is an honest attribution, but a leaky and narrow
one.

The ledger entry (2026-10-17T09:23:43Z) records claim 19.37, the row's `gap` field: the fast 2 mm objective, because
v_gap is empty. It holds 8 watch reasons: 3 from the tool (held_out, idle, sampling) and 5 judgement findings
(NEW-ghost-ceiling, P2, S1, G2, M4).

The tool's `idle` watch is the known instrument false positive. The regex `knee_moved` matches the inherited
honest-filter line of this pin-knee model, whose knee moves by design (K.qa span 65.21 deg; slipper-nose 65.71). A
skeptic refuted the same reading on slipper-nose (`slipper-nose-knuckle-3r.rulings.json`). I left it standing because I
do not edit the tool; it does not change the verdict.

- **The claim:** s65n2d (phased RSSR rod drive, K dyad 26.0 / 47.2). It scores 21.27 frozen exact Bench(110,360)
  (score 92.27) and 26.19 held out, at complexity 30.5. The reference, slipper-nose, scores 18.49 / 23.45 at 22.25.
  The row is screened and has no verifier yet.
- **Re-worn here, model unchanged** (`CB_EXACT=1 LS_DRIVE=rssr`, `docs/alignment/remeasure/longstroke-slipper-knuckle-3r_*.json`):
  - bench: 21.27 (reach 0.7222, in-band 0.8731, contact 0.008), reproduced to the digit;
  - 1 / 2 / 3 mm near-touch: 25.20 / 41.58 / 154.83;
  - held out: 26.19 (reach 0.6817, in-band 0.8714, contact 0.015), reproduced; 1 / 2 mm near-touch 30.17 / 45.28.
- **The claim is not an exo improvement, and the row says so.** It is 2.78 behind the reference on the bench and 2.74
  held out, at +8.25 complexity. Nothing in it ranks above a better design. The tool's watches (no verifier;
  crank 0.50 in band; the idle false positive above) stand.
- **The real subject of this audit is the attribution, the "ghost".** With the drive's metal deleted (`LS_GHOST=1`)
  and the lobe law at kK 3.0, it scores 18.25 / 21.11, against slipper-nose's 18.49 / 23.45. Another task is now
  chasing that number. My answer: the ghost is an honest attribution of THIS rod drive's kinematics. It is not a clean
  held-out number. Its held-out gain is real but comes mostly from low-arm poses, not from the long stroke. It is a
  ceiling only for a drive with the same stage-2 gain. Details below.

## What the wearer gets (measured)

| | claim s65n2d (real rod drive) | ghost kK 3.0 (no drive metal) | slipper-nose (reference) |
|---|---|---|---|
| overhead reach, elev >= 140, taken / total: bench | 7 / 28 (row) | 8 / 28 | 8 / 28 |
| overhead, held out | 16 / 71 (row) | 21 / 71 | 18 / 71 |
| raised arm, elev >= 90: bench / held | not dumped | 50 / 113, 121 / 300 | 46 / 113, 114 / 300 |
| taken poses with metal < 2 mm: bench / held | 36 / 79 (remeasure near2_poses) | 16 / 49 | 25 / 62 |
| contact poses, summed / deepest: bench | 3, 18.5 / 12.8 mm (horn lug, hub K, rod) | 7, 18.9 / 7.1 mm (elev 165 and a low pose, plane -75, elev 60, axial 120) | 2, 14.8 / 9.0 mm |
| contact, held | 13, 54.3 / 12.4 mm | 14, 38.1 / 9.2 mm (plane -90, elev 60, axial 120) | 10, 46.1 / 9.1 mm |
| workspace in-band (unscored) | all 0.850, elev 90-140 0.813, overhead 0.938 (row, self-measured) | not measured | - |
| clip in-band 2-14 mm (scored) | 0.873 (crank 0.50, median 14.0 mm; ball links 0.68) | 0.897 | 0.8955 |
| K used by taken poses / drive range | 41.63 deg (re-worn) / 65 | 51.75 bench, 53.97 held / 73 | 45.6 / 49.8 |
| fold margin, min th over taken poses | 5.036 | 5.389 / 5.28 | 5.006 |
| spring felt at the cuff (kK x tau_K) | 0.18 N.m: 1.2-1.5 N | 0.28 N.m: 1.9-2.35 N (not dynamically checked) | - |
| jam / dead centre | none in range (transmission >= 48) | kinematics same as the real rod (min transmission 54.8) | - |

Sources: `remeasure/longstroke-ghost-k30_{bench,held}_perpose.json`, `remeasure/slipper-nose-knuckle-3r_*_perpose.json`,
`remeasure/longstroke-ghost-k30_vs_slipper-nose-knuckle-3r_classes.json`, row `frozen` / `held_out` / `claims`.

What the score does not show for the ghost: it presses the skin in a new posture class. On the bench, 4 of its 5
contact-only poses are low-arm, internally rotated (plane -90 to -60, elev 45-60, axial +105 to +135). The deepest is
7.1 mm (plane -75, elev 60, axial 120), and slipper-nose takes 2 of those 4 cleanly. Held out, 6 of its 7 contact-only
poses are in the same class (plane -90 to -15, elev 45-75, axial +90 to +105), and slipper-nose takes 5 of them cleanly.
The deepest ghost held-out press is 9.2 mm at plane -90, elev 60, axial 120. Slipper-nose's contacts are mostly overhead
(6 of 10 held out).

## The ghost, question by question

**1. Does LS_GHOST delete only the drive's metal, or constraints too?** It deletes metal plus the drive's per-pose
part-pair checks. It keeps every kinematic constraint.

- Deleted (`_ghost`, model lines 127-135): the crank, rod, ball links and horn lug as in-band samples; their
  skin-contact samples (members 8 and 9, and the horn's member-1 entry); and the strap entries ROD / CRK / HORN. With
  those gone, `collide()` skips about 18 drive pairs (CRK-hubs, CRK-links, HORN-L1b / hub2 / L2, knee / pad / E vs
  CRK / HORN) plus the parent's ROD pairs.
- Kept:
  - the drive's range scan (transmission >= 48 at both ball ends; ROD-hub2, ROD-L1b and CRK-hub2 at 1 mm), which runs
    in `_rod_metal` BEFORE the deletion: dK_lim 73.0, why 'law';
  - the lobe law gates: pressure angle <= 42, skirt (crest 10.87 of 11.5 mm), lift-off, stop B;
  - the kit fold rule and the th fold margin (5.389 / 5.28).
- Do the deleted pair checks matter? At this config they do not bind on the bench: the same parameters with metal
  (farm `claimG/real_k30_bench.json`) lose 0 poses to parts. Held out with metal was never worn.

**2. Is kK 3.0 realisable by a drive with metal?** Kinematically, yes, by this rod drive, and with more margin than the
model shows. The model's lobe gate linearises the stage-2 gain (r_h / La = 0.603). The real RSSR map has
dphi/ddK = 0.558 at the base circle, rising to 0.653 mid-stroke. A new read-only probe
(`tools/alignment_lobe_exact.py` -> `remeasure/longstroke-ghost-k30_lobe_exact.json`) measures the exact lobe pressure
angle along the law:

- maximum 39.01 deg, at dK ~16; the gate reads 40.39 at the base circle;
- with s_arm +0.25 mm (one tolerance step): exact 40.60, while the model's gate would read 42.12 and kill the law.

So "kK 3.0 = the lobe's PA-42 limit" is the gate's limit, not the physics'. The exact limit for this drive is near kK
3.3. On the claim config the two agree (39.80 exact vs 39.85 gate). With metal, the same kK 3.0 config measures 25.83,
and the steep-law re-search (cma5) 23.31 / 27.67. No drive with metal has reached the ghost's number yet.

**3. Is the held-out gain (2.34) robust per pose, and where does it come from?** Paired, exact, every pose
(`remeasure/longstroke-ghost-k30_vs_slipper-nose-knuckle-3r_paired.json`):

- Bench: -0.24, 90 % CI [-2.12, +1.85], P(ghost better) 0.55, so a coin toss. +8 / -3 workspace poses; contact 2 -> 7.
- Held out: -2.35, CI [-3.70, -0.86], P 0.997, so statistically robust. +30 / -5 workspace poses.
- By pose class, held out: of the 30 extra poses, 17 are at elevation < 60 and 6 at 60-90, and 16 have |axial| >= 120.
  Only 4 are at 90-140 and 3 overhead. The gain is mostly low-arm, extreme-axial postures, which the bench samples
  thinly. It is not the stretched th 110-113 poses the long stroke and steep law were for.
- Split by attribution (a new held dump of ghost g65d, kK 1.98, the same chain:
  `remeasure/longstroke-ghost-g65d_held_perpose.json`, 22.69 reproduced; classes in
  `remeasure/longstroke-ghost-{g65d_vs_slipper-nose-knuckle-3r,k30_vs_longstroke-ghost-g65d}_classes.json`):
  - the long-dyad chain at the CMA's own law already takes +14 / -0 poses vs slipper-nose: 9 below elevation 90 and all
    3 overhead ones;
  - the steep law kK 3.0 adds +17 / -6 more. All 11 of the 17 below elevation 60 have |axial| >= 120; 3 are at 90-140
    and 0 overhead;
  - the steep law also adds 7 contact poses. 6 are shallow (0.2-2.0 mm) in the low-arm, internally rotated class, and
    g65d took 5 of them cleanly. It deepens the (-90, 60, 120) press from 6.1 to 9.2 mm.

  So kK 3.0's held-out -1.58 buys extreme-rotation postures with the arm low, and none of the 71 overhead poses.

**4. "Taken poses use 41.6 deg of K".** Confirmed. The re-worn claim bench records K spanning 41.63 deg over taken
poses (`remeasure/longstroke-slipper-knuckle-3r_bench.json` deep.coord_spans.dK = -0.7265 rad). Held out (re-worn, 26.19 reproduced) it spans 41.52 deg. Slipper-nose,
with a 49.8-deg drive, uses 45.6 / 46.3 deg. The long-stroke claim therefore uses LESS K than the short-stroke leader.

**5. The nose control (must reproduce slipper-nose 18.49).** The row records 18.49, fold 88, slide 9, contact 2,
identical to the verified number. I did not re-run it. It needs no re-run for this verdict, because it only proves the
wrapper reproduces slipper-nose through the NOSE branch. It exercises neither the rssr branch nor `LS_GHOST`. The ghost
is compared with slipper-nose across two model code paths (the sidecar's rssr chain vs slipper-nose's RF chain), and no
control ties the rssr path to a verified number. The nearest is sidecar-longdyad's verified 18.91 at transmission 30.

## Findings

**NEW-ghost-ceiling (watch): a metal-deleted attribution cited as a beat of the leader and handed on as the ceiling.**

- Evidence: question 1 and 2 above.
- Why the exo is not better: no such drive exists. The ghost's 18.25 needs a drive whose metal adds no out-of-band
  sample, no contact and no part clash. The only real drive at this law costs 7.6 points (25.83). As a ceiling it holds
  only for drives with this rod's phi(dK) gain. It is loose by up to 0.31 points of in-band (a drive whose own metal is
  mostly in band could raise the sample-weighted in-band). Its continuity flood was never measured.
- Action: whoever chases it must cite it as "ghost, no drive metal, this gain map". They should gate a real drive
  against the ghost pose by pose (`tools/alignment_paired_params.py` + `compare`, pose classes by
  `tools/alignment_pose_classes.py`), not against the headline.

**P2 (watch): held-out leakage in the law pick.**

- Evidence: kK 3.0 / s_arm 4.0 / r_lobe 8.5 were set by hand after the ghost fit. They were chosen from a law-only table
  counted on Bench(110,360) and the 952 held-out poses (`stroke_curve.py` calls `held_bench()`; research note section 8).
- The fit bench does not see the change (fit 12.23 -> 12.12). The claim bench does (19.50 -> 18.25), and so does held
  out (22.69 -> 21.11).
- Why it matters: 21.11 is not a clean held-out number. The leak is small: one boundary choice among about 6 laws, also
  the claim-bench best.
- Action: re-fit the steep law with the law set on the fit bench only (or by the gate rule alone), then wear it held
  out once.

**S1 (watch): the held-out gain comes from a pose class, not from the lever.**

- Evidence: question 3.
- Why it matters: the long-stroke story says the gain comes from stretched overhead poses. The measured gain comes from
  low-arm, extreme-axial postures. Measured by attribution: the chain change alone buys the 3 overhead poses. The steep law buys 11 low-arm,
  extreme-rotation poses, 0 overhead, and 7 new (mostly shallow) contacts.
- Action: attribute by pose class before naming the lever.

**G2 (watch): stiffer spring feel at the steep law, unmeasured (M5).**

- Evidence: 0.28 N.m reflected at J2, so 1.9-2.35 N at a 150-120 mm cuff, against 1.2-1.5 N on the claim. That is
  within 0.15 N of the 2.5 N line, and over it below a 113 mm lever.
- K turns 3x as fast as q2, so the follower's dynamic hold matters more. No R17 run exists.
- Action: run the dynamics judge at kK 3.0 before any drive is built to it.

**M4 (watch, claim): a partly idle stroke.**

- Evidence: range 65, use 41.63 (re-worn). 36 % of the stroke is idle on every taken pose, at +8.25 complexity. It uses
  less K than the leader.
- Why it matters: the row reports this itself, and the claim ranks behind the reference, so it is a watch, not gamed.

Patterns checked and not present:

- **Near-touch, T1 / T2 / G1 (report-only by the user's 2026-10-17 ruling):** 20.31 points of the claim live in the
  1-2 mm shell, against slipper-nose's 14.53 and the ghost's 15.02.
- **T3:** the th margin is read on th, 5.036 minimum.
- **T4 / G4:** the steep law sits at the gate's edge, but the exact PA has 3 deg of margin.
- **T5:** the claim's contact depth is 1.26x / 1.18x the reference, and the ghost's 1.28x / 0.83x. Both are under 2x.
- **S2:** the tool's watch (crank).
- **S3:** none on the claim. The ghost has no drive bodies by construction (finding above).
- **S5:** the claim's full flood equals static. The ghost's flood is not measured.
- **M1 / M2:** O20 hubs, catalogue ball links and MR63ZZ.
- **M3:** the claim parks the horn ball 0.25 mm from its ROD-hubK pair, but the robust build r_h +0.25 measures
  identical (21.27 / 26.20).
- **P1:** the frozen protocol is used for the claim.
- **P3 / R3:** the pick was committed before frozen numbers (`picks.json`). The other claims are listed alongside.
- **P4:** no bench / judge file is in the row's commits.
- **R1 / R2:** the dashboard shows the fast 14.54 in the gap column, the same convention as every row, with v_gap
  empty. The ghost appears only as attribution in the verdict text.
- **G3:** no cuff-twist number on file.
- **G5 / G6:** complexity 30.5 is recomputed and matches. The sidecar counted the same drive at 25.5, which would
  flatter it, and this row uses the higher count.

## Questions for the user

1. The ghost (18.25 / 21.11) is now a target. Should a target that deletes metal be allowed only with its own frozen
   protocol (law chosen on the fit bench), a per-pose paired comparison and a "no drive metal" label wherever it is
   shown? This is proposal A below.
2. The held-out gain lives mostly at low elevation with extreme axial rotation (behind-the-back and reach-across
   postures). Do you weight those postures equally with overhead? Your goal says "overhead most of all", and on
   overhead the ghost gains 3 of 71 held out and 0 of 28 on the bench.
3. The steep law raises the spring felt at the cuff to about 2 N (2.35 N at 120 mm). Is 2.5 N at the cuff still your
   comfort line, and at which cuff lever?

## Proposals (measurement or reporting changes, NOT applied; none changes any score)

- **A. Attribution numbers carry a protocol.** Any number from a run with real parts deleted (LS_GHOST or similar)
  that is cited as a target or against a leader must state:
  - how its free parameters were chosen (fit bench only);
  - its paired per-pose comparison;
  - the kinematic map it inherits.
  Measured effect: no verified row is an attribution, so every verified row is unchanged. On this row, the
  "held 2.34 better" sentence would read "held -2.35, 90 % CI [-3.70, -0.86]; bench -0.24, CI [-2.12, +1.85]; law
  picked with held-out counts in view".
- **B. Gate the hub-2 lobe on the exact RSSR map, not the small-angle gain** (a measurement change for the rssr
  family). Measured here, the gate is conservative at the ghost config (40.39 gate vs 39.01 exact) and equal on the
  claim (39.85 vs 39.80). Effect on the verified rssr rows (sidecar-longdyad, sidecar-parallelogram, kneeless-sidecar):
  not measured in this time box. `tools/alignment_lobe_exact.py <params>` measures each in about 1 min. A drive whose
  ratio at the base circle is ABOVE r_h / La would be optimistic under the current gate.
- **C. Catalogue entry (proposed), P5. "Ghost targets".**
  - Looks like: a counterfactual with real metal deleted is reported next to the leader and becomes the next task's
    target.
  - Why not better: it measures a drive that does not exist. Its free parameters may have been tuned where the
    protocol forbids, and it inherits one drive's kinematics.
  - Detect: every row `claims.*ATTRIBUTION*` entry cited outside its row needs (1) fit-bench-only parameter choice,
    (2) a paired per-pose comparison, and (3) a with-metal twin at the same parameters on the same wears.
  - Here: this audit.

## Numbers I could not get, and why

- Workspace in-band, unscored, for the ghost: no wear-probe run in the time box. The row's self-measured value for the
  claim is in the table.
- The real rod drive at kK 3.0, held out (and its held-out part pairs): never run, and not needed for the verdict.
- The ghost's continuity flood: not run, about 10 min of CPU.
- R17 dynamics (spring hold, cuff twist) at kK 3.0: no harness for this model.
- The nose control: not re-run (see question 5).
- The exact lobe PA on the verified rssr rows: proposal B.

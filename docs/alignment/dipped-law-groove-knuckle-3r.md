# dipped-law-groove-knuckle-3r: alignment audit

Auditor pass, 2026-10-17 (discovery round 10, slice r10-A). Tool `tools/alignment_audit.py` VERSION 2026-10-17.2.
Reference row for the comparisons: the verified 3-active lead `roller-longdyad-knuckle-3r` (18.67).

## Verdict and claim

**Verdict: GAMED** (computed by `tools/alignment_ledger.py`, worst of the 12 checks and the judgement findings).

- **The claim:** `v_gap` 18.64 (score 93.22), frozen exact Bench(110,360), fit-60 shape frozen.
  - The dashboard (`docs/dashboard/data/morphs.json`) ranks it first among the 3-active rows, 0.03 ahead of the lead.
  - The row's own verdict calls it "level with the lead, not a lead change", which is the honest reading.
- **The re-wear reproduces it.** This audit re-wore the claim with the model unchanged:
  - bench 18.64 (`docs/alignment/remeasure/dipped-law-groove-knuckle-3r_bench.json`);
  - held out 24.07 (`..._held.json`).
  - The number is real. The question is what it buys.
- **Why gamed:** the claim exists only under a fold-margin reading that the design applied to itself. That reading is
  an open question for the user.
  - The family's reading fails 84 of 371 taken bench poses and 202 of 850 held-out poses. Their margin is 0.204 deg
    (bench) and 0.184 deg (held out), against the 5 deg rule.
  - The same cell without the dip needs no new reading (min 5.181 deg). It scores 19.33, which is behind the lead's
    18.67.

## What the wearer gets (measured)

All numbers are on Bench(110,360) exact, frozen, worn on the claim's own parameters. The bench probe is
`docs/alignment/remeasure/dipped-law-groove-knuckle-3r_bench_probe.json`. The lead's probe is
`docs/alignment/live_audit_2026-10-16/probe_roller-longdyad-knuckle-3r.json`, worn through the same harness.

| what the wearer feels | this design | the lead (roller-longdyad) |
|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 | 8 / 28 |
| raised arm (elev 90-140), taken / total | 38 / 85 | 38 / 85 |
| taken poses with metal < 2 mm, bench (workspace + clip) | 34 (29 + 5) | 30 (25 + 5) |
| taken poses with metal < 3 mm, bench / held out | 147 / 334 | 133 / 274 |
| overhead taken poses with metal < 2 mm | 5 of 8 | 4 of 8 |
| contact poses, bench / held out | 4 / 17 | 2 / 10 |
| summed contact depth, bench | 21.87 mm | 16.46 mm |
| deepest contact, bench | 10.9 mm at workspace (15, 165, -60) | 10.55 mm at the same pose |
| new bench contacts | 4.52 mm at (0, 105, 15), 0.89 mm at (-15, 90, 45) | - |
| unscored workspace in-band 2-14 mm (all / elev 90-140) | 0.861 / 0.800 | 0.854 / 0.798 |
| scored clip in-band 2-14 mm | 0.8993 | 0.8937 |
| lowest metal, bench | 0.07 mm at (-60, 60, 105) | 0.07 mm, same pose |

Other numbers:
- **Springs:** one clock spring force-closes both rolling pairs (lobe follower and roller-flank). It now also has to
  close K below the old stop A, into a lobe dip 0.068 mm deep. No spring-torque or closure-force output exists for it.
- **Stops:** stop A moves to the dip floor. K is taken from -2.37 to 43.66 deg (`extras.dK_taken_max_deg` in the probe;
  `frozen.drive` in the row).
- **Knee:** the angle taken is 54.2-96.7 deg, inside its 20-160 window. The knee is not near its stops.
- **Cuff twist:** not measured. There is no R17 / dynamics run for this row.
- **Near-singular postures:**
  - The family's fold reading, min(m_sub, m_eff) wherever K is off its rest, is 0.204 deg on the bench. 84 taken poses
    are under 5 deg, all of them in the dip.
  - The verifier's coupled reading is 5.389 deg on the bench and 5.406 held out.
  - The horn pressure angle sits at its 43.0 deg cap (dK_lim 43.8, `why_lim` pressure_horn).
  - The bent arm clears hub K by 1.04 mm at the dip floor.

PAIRED_PLACEHOLDER

## Findings

FINDINGS_PLACEHOLDER

## Proposals (not applied: measurement or rule changes for the user or the lead)

PROPOSALS_PLACEHOLDER

## Not measured, and why

NOTMEASURED_PLACEHOLDER

# Round 9 ideation: judge and red team (2026-10-16 ~21:15 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)). The real target is gap 0, and 95
(gap 13.75) at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered, exactly 3 active DOF.

Lead to beat: sidecar-longdyad-knuckle-3r, verified at 18.91 (score 93.12, Bench(110,360) exact frozen, margin 5,
O20), 2 mm near-touch 34.03, complexity 49. A lead change must win plain AND at 2 mm (A1 dominance gate).

## Red-team checks made by the judge

Scripts are in the scratchpad (`judge9/`): the proposers' `gate.py` re-run on the lead with no change, and `kn.py`.

1. **The lead's binding stretched wall is the drive stroke, not stop B.** I re-ran the lead's own IK on
   Bench(110,360), law-only. The largest th it takes is **109.2**. That equals a1e 52.7 (the RSSR's taken dK 38.1 on
   bk1 28.9 / bk2 39.24, from the spherical cosine rule) + a2 61.89 - 5 = 109.5. Stop B (a1max 63.2, wall 120.1) never
   binds. Of the 93 lost workspace poses, 22 lie below the folded wall (th < 30.5), 7 lie inside the window, and 64 lie
   above 109.4.

   Lost poses above the drive wall, by wall height:

   | wall th | 113.5 | 117.6 | 119.4 | 120.2 | 121.4 | 123.6 (lobe skirt) | 124.4 | 129.4 |
   |---|---|---|---|---|---|---|---|---|
   | workspace poses won | +6 | +13 | +15 | +16 | +18 | +19 | +21 | +27 |
   | of which overhead | +1 | +1 | +2 | +2 | +2 | +2 | +3 | +3 |

   One pose = 0.278 points. This table sizes every reach lever in the round:
   - any lever that raises the drive's stroke wins poses;
   - a lever that raises a1max, or moves seats while the stroke stays capped, does not.

   The round-8 judge saw the same thing on the frontload lead ("the lead never uses its stretched range").
2. **Wall height per drive.** Drive-wall th = a1e(dK) + 61.89 - 5, with a1 held at 36.37:

   | dyad | dK | a1e | wall |
   |---|---|---|---|
   | bk2 39.24 | 38.1 (RSSR, taken) | 52.7 | 109.5 |
   | bk2 39.24 | 43 (RSSR wall) | 54.4 | 111.3 |
   | bk2 39.24 | 52 / 60 (re-cut flank) | 57.5 / 59.9 | 114.4 / 116.8 |
   | bk2 44 | 56 / 58.8 / 64 (roller-longdyad's measured re-cuts) | 60.6 / 61.6 / 63.3 | 117.5 / 118.5 / 120.2 |

3. **The knee-free claim reproduces exactly** (lead model, Bench(60,160) fast). The knee angle is 122.08 deg on all
   220 poses at b3 0 (88.7-180 at the lead's b3).

   | case | gap | reach | follow | in-band | contact |
   |---|---|---|---|---|---|
   | b3 0, as is | 21.67 | 0.7688 | 0.95 | 0.8885 | 0.0625 |
   | b3 0, wd 75 / wa -7 | 18.86 | 0.7812 | 1.0 | 0.873 | 0.0314 |

4. **Twin knuckle arithmetic.** The proposer's dK2 numbers re-derive: 34.7 and 40.2 against the claimed 34.8 and
   40.4.
   - **Clearance.** Two O20 hubs at F 57 need 20.5 mm centre to centre, so bk3 >= 20.6 deg. Where lobe 2's crest
     (HUB_R + 1.5) is at the same height as K2's stack, they need 22 mm, so bk3 >= 22.3 deg. The proposer's own
     in-band map is already falling there: 0.93 at 18 deg and <= 0.47 at 25 deg.
   - **Hand-over.** The default th_on2 (the K law's th_max - 2 = 117.3) would leave 12 of the 18 prize poses
     (th 109.4-117.3) unreachable. K2's law must start at the q2 where K's drive saturates.
5. **Roller arm stress.** As a 3 x 6 Ti beam under 2.5 N at 55 mm, the arm deflects 0.09 mm (~0.3 deg of K) at
   15 MPa. That is fine.

No candidate needs a passive translation. None has an undetermined passive coordinate: K and K2 are slaved by q2 and
never read, and the knee pins are sensed or deleted. Every joint maps to a catalogue part (MR117-2RS, MR63ZZ,
IGLIDUR-PIN, M2 ball links) or a machinable part. The 5-axis flank and arm tips are stated on the part. No candidate
duplicates a catalogue entry.

## Verdicts

| id | verdict | reason |
|---|---|---|
| backseat-sidecar-knuckle-3r | rejected: measured dead (lever (a) closed) | The proposer's own refit cells are all worse than the control 10.30: 20.29 / 61.21 / 73.21 at az 75 / 55 / 35. Fold losses rise 26 -> 33 -> 49 -> 47. H1 shows the same pattern (23.64 -> 39.79+). The judge's check agrees: the seat only slides a window whose top is the drive stroke (109.5). |
| eave-seat-sidecar-knuckle-3r | rejected: measured dead | The only J1 direction that buys window (kinematic 0.794-0.808 vs 0.761). But the scapula-fixed O20 hub 1 meets the bunching middle deltoid: workspace contact 0.05-0.12 at in-band >= 0.84, and rings are worse (0.156-0.231). Refit 27.92 / 34.80 vs 10.30. The one rescue left (hub-1 radius/seat search) is predicted at control + 3 or worse; not worth a slot. |
| crownlat-sidecar-knuckle-3r | rejected: measured dead | Kinematic +12 poses at (105, 72). The 30-eval refit escapes contact (0.15 -> 0) only by closing the window again (bk1 24.1, J2 raised): 25.29 vs 10.30. The judge's wall table explains why: W's top is the drive stroke, not a1. Its lesson feeds pick 1. |
| widewin-sidecar-knuckle-3r | rejected: killed by its own pre-gate (lever (b) closed) | Step 1 is already measured. Seed A gives kinematic 0.733 / 0.750 against the lead's 0.742 (stop rule < 0.76), fast 25.19. Seed B loses 166/220 poses to knee-E. The twist's headroom was K range (dK 82), which no strap-level drive carries (sidecar 43, flank 52). The attribution table is the closure; no run needed. |
| twin-k2-sidecar-knuckle-3r | **PICK 2** (merged with twin-flank-k2-knuckle-3r) | The only monotone (pure-add) reach lever: every taken pose stays the verified lead's. Corrected prize, measured from the true wall: +15 / +18 / +21 / +27 poses at dA2 10 / 12 / 15 / 20. Main risks: the clearance squeeze (bk3 >= 21-22.3) against K2's in-band, and complexity ~70-74. |
| twin-flank-k2-knuckle-3r | merged into pick 2 (emb2 'flank') | Same kinematics, same model file, same law-only gate step. It is the embodiment to switch to when the rod's dK2 43 caps dA2 at ~12. Rodless is ~4 cx lower. |
| roller-longdyad-knuckle-3r | **PICK 1** (re-aimed by the judge) | The proposer sized the gain by stop B (+3-7 deg) and gated on fit poses past the lobe skirt that no drive on this lobe can reach. The measured re-cut flanks (dK 56 / 58.8 / 64 at bk2 44) lift the binding wall from 109.5 to 117.5-120.2: +13-16 poses (3.6-4.4 points), skirt cap +19, at cx 44. That is ~80 % of the twin's prize at ~60 % of its complexity. The gate is replaced by a law-only kin360 >= 0.775 step, plus a bk2 39.24 control cell (the monotone version). |
| kneeless-sidecar-knuckle-3r | **PICK 3** | Every fast number reproduced exactly. It deletes ~22 complexity points and the 7 frozen slide losses, and pays hub 3 obliquity and 3.1 points of contact. Expected frozen ~21-24 (score ~91.3-92.4) at cx 27: a Pareto point between H1 (27.20, cx 19.5) and minarc (18.40, cx 33), not a lead change. The judge adds a GH-offset red team, because the bench cannot see what the knee absorbed. |
| kneeless-roller-knuckle-3r | **PICK 4** | The same lever on the rodless drive, at cx 23.5 with no sensed passive. It is not merged with pick 3: it has a different verified parent and the drive decides the claim (2 mm near-touch 46.82 vs 34.03; crude re-seat 19.47 vs 18.86). Both gates are 20 min and run in parallel. If pick 1 passes, wear its re-cut flank here next (cx ~22 with the drive-wall reach lever). |

## Ranking

Ranked by expected gap reduction vs the lead x confidence x buildability. All candidates have 0 passive translations,
so near-ties are broken by complexity (the user's standing "95+ with low simplicity").

1. **roller-longdyad-knuckle-3r** (cx 44.0).
   - Kinematic -3.6 to -4.4. Expected frozen 15.5-18 if half the won poses park.
   - Confidence low-medium: the design is not monotone, the no-refit wear lost follow / contact, and the pressure angles
     sit 0.1-1.9 deg under 45.
2. **twin-k2-sidecar-knuckle-3r** (rod, then flank; cx ~74 / ~70).
   - Kinematic -5.0 / -5.8. Expected frozen 15.5-17.5.
   - Confidence low-medium. It is monotone, but the K2 clearance and in-band gate are the likely killer, and it costs
     complexity.
   - It stacks with pick 1: K2 on top of a longer K stroke.
3. **kneeless-sidecar-knuckle-3r** (cx 27.0).
   - Gap +2 to +5 against the lead, but -22 complexity: the round's Pareto lever.
   - Confidence medium.
4. **kneeless-roller-knuckle-3r** (cx 23.5).
   - Gap +3 to +5, -25.5 complexity.
   - Confidence medium-low: the roller's 2 mm metal.

## What runs next (parallel, nothing waits)

- **Picks 1 and 2 start law-only.** Both start with their law-only gates on the lead's IK (drive metal off), from
  the judge's wall table:
  - pick 1: kin360 >= 0.775;
  - pick 2: >= 0.785 for the rod, >= 0.795 for the flank.

  If both pass, the 95 route is pick 1's longer stroke with K2 on top: wall ~120 + dA2.
- **Picks 3 and 4 start their 20-min CMA gates at once.** They share the knee-to-bracket code; write it once and wrap
  both parents.
- **Every gate reports:** the workspace in-band (>= 0.874 / 0.841), plain and 2 mm, and the per-part split.
- **Every survivor then gets:** the envelope-bench CMA (2 mm), frozen exact, held out, flood, simplicity,
  alignment_audit and the verifier.
- **Closed this round with measured reasons** (no rescreen):
  - J1 re-seats (back, eave, crown-lateral): lever (a);
  - the J3 twist seats on the strap-level drive: lever (b).

  The remaining open reach lever is the drive stroke (lever c), now picks 1 and 2.

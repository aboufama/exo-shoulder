# Alignment audit: ikring-thinstack-knuckle-4r (round 301, slice r301-A)

Auditor run 2026-10-19 ~04:35 UTC (`audit:ikring-thinstack-knuckle-4r`), tool `tools/alignment_audit.py` 2026-10-19.1,
reference `conecut-knee-knuckle-3r` (the verified 3-joint lead, v_gap 18.28).

## Verdict

**WATCH** (ledger entry 2026-10-19T04:35:27Z). The claim is v_gap **9.75** (score 96.45), the chain-only gate on
Bench(110,360) exact with a frozen shape. The plain reading is 8.76. No check and no finding reaches 'gamed'. Two things
cap what the number is evidence of:

- J4 is an IK-commanded ring that nothing holds in the unpowered MVP1.
- psi is chosen per pose on the scored skin.

The row says both itself: "a labelled 4-joint option, never the lead".

The verifier's re-run reproduces the claim exactly: the per-pose dump is identical at all 470 poses
(`docs/concepts/verify/ikring-thinstack-knuckle-4r/verifier/`). This audit found no arithmetic, sampling or
reporting trick in the number. The concerns are about what the number means for the wearer.

## What the wearer gets (measured)

Sources:
- Dumps on file, read by `tools/alignment_ikring_readout.py`, output in `docs/alignment/remeasure/ikring-thinstack-knuckle-4r_audit_readout.json`.
- This audit's wear of the held clip frames: `tools/alignment_wear_probe_ikring.py`, output in `docs/alignment/remeasure/ikring-thinstack-knuckle-4r_heldclip_k0.json`.

| | this row, bench | lead, bench | this row, held | lead, held |
|---|---|---|---|---|
| overhead reach (elev >= 140), taken / total | 13 / 28 | 8 / 28 | 32 / 71 (about 27 with a bench-learned psi map) | 18 / 71 |
| raised-arm reach (elev >= 90) | 73 / 113 | 47 / 113 | 191 / 300 | 123 / 300 |
| taken ws poses, metal < 1 mm | 15 / 296 | 3 / 262 | 57 / 774 | 13 / 659 |
| taken ws poses, metal < 2 mm | 63 / 296 | 23 / 262 | 151 / 774 | 57 / 659 |
| everyday-motion clip frames, metal < 1 / < 2 mm | 7 / 9 of 110 | 0 / 0 | 11 / 15 of 202 (min 0.419 mm) | 0 / 0 |
| contact poses, summed depth, deepest | 4, 19.48 mm, 8.93 mm | 4, 20.24 mm, 8.93 mm | 11, 55.91 mm, 9.86 mm | 14, 60.97 mm, 9.86 mm |

Where the contacts are:
- **Bench, deepest:** pose 237 (plane 15, elev 165, axial -60), 8.93 mm. This is the lead's own chain contact in the overhead abduction cone, which the ring cannot reach.
- **Held, deepest:** (45, 165, -30), 9.86 mm. Also the lead's own contact.
- **The only hardware contact:** pose 139 (-60, 60, 105), 0.48 mm, at the bracket and flange.

Other readings:
- **Workspace in-band of the taken ws poses:** not measured. The per-pose dumps carry sample counts only for clip frames, and the bench scores in-band on clip frames only.
- **Held clip in-band, full set (this audit):** chain-only 0.8888, pooled 0.9025, follow 1.0, 0 contacts. With the held ws sample this gives a full held chain-only gate of about **10.93** (plain 9.81), against 9.75 on the bench.
- **Springs:** none. The coil is deleted.
- **Stops:** the J3 dowel stop, the knee window, and the ring's slot-end stops at 0 and 40 deg. 14 of the 36 new bench takes sit on the 40-deg end stop.
- **Fold margin:** min th margin 5.083 deg over 406 taken poses (0 under 5); 5.000 held. No near-singular posture is bought.
- **Cuff twist:** J4's holding torque into the cuff is not modelled. In MVP1 nothing holds J4, so the ring is free. In the powered product the motor holds it.

## Findings

Every finding is watch. They are in `docs/alignment/ikring-thinstack-knuckle-4r.findings.json`.

### M5: a coordinate nothing holds, scored at its planned value

- **Evidence:**
  - The coil is deleted and J4's psi is set per pose by the IK.
  - The verifier's own R17 note says that in the unpowered MVP1 J4 is free.
  - On the same hardware without a drive, the unpowered least-phi control reads 14.46 (18 contacts, T5 77.49 mm) and the parked ring reads 20.37.
  - phi40-thinstack-relay-4r is the coil-held twin, determinate in MVP1, and reads 14.06.
- **Why the exo is not better than the number says:** an MVP1 build of this hardware does not deliver 9.75. Only a powered J4 with a controller can.
- **Why watch:** the row says so itself, and the dashboard leader excludes 4-joint rows (`docs/dashboard/core.js` line 13).
- **Action:** carry the unpowered reading (14.46 control, 20.37 parked) next to 9.75 wherever the row is compared (see proposals).

### P1: the redundant coordinate is tuned per pose on the scored bench

- **Evidence:**
  - psi is the best of 17 k values per pose, by min metal on the bench's own exact skin.
  - This audit built a crude controller learned off the held poses: each held pose takes the bench psi of its nearest bench ws pose (median 15 deg away).
  - That controller keeps **59 of the oracle's 119** held new takes (69 if any tied neighbour counts). 5 of the 60 lost takes are overhead.
  - Held ws taken falls from 774 to 697-714 of 952, and the held gate rises from about 10.93 to **at least 17.3-19.1**. Contacts at the lost poses were not measured, so this is a lower bound. phi40 held reads 16.69.
  - On the bench, 12 of the 36 new takes have a taking-k run under 10 deg, and 2 are taken at one k only: pose 127 at k 2.5 (0.099 mm) and pose 354 at k 40.
- **Why the exo is not better than the number says:** 9.75 is the oracle's upper bound. A table-driven controller lands somewhere between the oracle and the crude map, and part of the held edge over phi40 depends on which.
- **Action:** see proposal 1.

### P2: held-out leakage of the controller

- **Evidence:** the held reading builds a fresh k-table on the held poses and re-chooses psi on the held skin.
- **What that tests:** "some psi clears this pose", not a policy that generalises.
- **With the bench-learned map:** held overhead is about 27 of 71. That still passes the pre-registered >= 25.
- **Why watch:** the shape is frozen. The leak is in the redundant coordinate only.

### T1: the whole plain lead over the 3R lead sits in the 0-1 mm shell

- **Evidence, against the lead:**

  | reading | this row | lead | difference |
  |---|---|---|---|
  | plain | 8.76 | 18.28 | +9.52 |
  | 1 mm | 19.65 | 19.92 | +0.27 |
  | 2 mm | 47.00 | 34.84 | -12.16 |

- **Pose 127:** the IK's max-clearance choice puts the bracket 0.099 mm off the skin. At k = 0 that pose is a -0.15 mm contact.
- **Why watch:** the 1 and 2 mm readings are report-only by the user's 2026-10-17 ruling. phi40 had the same pattern (+4.76 plain, -12.32 at 2 mm) and was also watch.

### G1: the ring hardware hugs the arm in everyday motion

- **Evidence:**

  | clip frames | metal < 1 mm | metal < 2 mm |
  |---|---|---|
  | this row, bench (110) | 7 | 9 |
  | this row, held (202) | 11 | 15 |
  | lead, bench and held | 0 | 0 |
  | phi40, bench | 0 | 7 |
  | phi40, held | 0 | 13 |

- **Cause:** at the pre-registered 8.5 / 243 axis the shell sits 3.35 mm lower than phi40's (R_t 76.75 vs 80.1), and the bracket ramps 28.9 deg. The near-touch is at the posterior shell end and at the bracket / flange.
- **Why the exo is not better than the number says:** metal at 0.4-2 mm on the model is metal on a real, bulging arm. Here that happens during ordinary motion, not only at the extremes.
- **Action:** the row's own next step: a bracket that leaves outward, and a recessed flange.

### S5: continuity is shown kinematically, not on the skin

- **The flood's rules:** psi may move 10 deg per 2-deg arm step, and the ring may self-move freely inside a feasible-k run.
- **What was checked:** the verifier's metal-aware re-run kept only metal-good states at the 100 moved bench poses, and all 36 new takes stayed connected.
- **What was not:**
  - Edges between poses and non-bench nodes stay kinematic.
  - At 9 of the 36 new takes, a kinematically feasible k at the same pose is metal-bad, so a sweep inside a run can pass a contact state.
  - psi* jumps more than 20 deg between grid-adjacent taken poses on 3 of 176 pairs (max 32.5).
  - The skin along the J4 sweep is unmeasured.

### M3: clash margins are hairline by construction

- **The check ran:** X1 + X2 found 0 extra jams.
- **The margins:**
  - E strap to shell: 1.199 mm, which equals the bump parameter 1.2. 308 taken frames are under 2 mm, 244 under 1.5 mm.
  - Knee crown to bracket: 0.869 mm at pose 399 (k 40).
- **What is missing:** the shell is 1.0 mm Ti on a 4 mm liner whose compression is not modelled. No tolerance or shell-flex stack is on file.

### S1: the held reading on file is a sparse sample

- **The sample:** 3 of 202 held clip frames, so the held in-band (0.9713) and "gap on that sample 10.09" do not measure in-band.
- **This audit's full wear:** all 202 frames read chain-only ib14 0.8888. Combined with the ws sample, the full held gate is about 10.93, +1.18 over the bench.
- **Why watch:** the row labels it a sample, and the drop is small.

### NEW-oracle-bar: an oracle number used as the kill bar for designs that must be MVP1-determinate

- **Evidence:** `docs/concepts/ROUNDS.md` (line ~6056) sets the K2 knee-less 4R bar against this row's 9.75.
- **The mismatch:**
  - The user's K1 track (CLAUDE.md decision 10) is a rigid-cuff 4R with a sprung or slaved redundant joint, which an unpowered MVP1 can hold.
  - On that footing, this row's bar is its unpowered control, 14.46, or phi40's sprung 14.06.
- **Risk:** a sprung knee-less 4R at 10-14 would be ruled "not worth the switch", although for the MVP1 wearer it beats an undetermined ring.
- **Why watch:** no K2 row has been killed by this bar yet.

**Proposed catalogue entry.**
- **NEW-oracle-bar (P5).** A claim that needs a commanded coordinate, chosen on the scored skin, is used as a target or kill bar for designs that must be determinate unpowered.
- **Detect:** for each kill line in ROUNDS / planner specs that names a row, check whether that row's claim has an IK-commanded counted joint, and compare against its unpowered reading.

### Checked and not present

- **T3:** the fold margin is read on th: 5.083.
- **T4:** the k = 40 bound is the shell's pre-registered hardware extent. Riding it is not singular.
- **T5:** contact depth is no deeper than the lead's, on the bench or held.
- **S2:** the claim uses the chain-only in-band (0.8901), not the pooled 0.9034 that the flat shell's 752 points would dilute.
- **S3:** shell, carriage, bracket and flange are all sampled.
- **P3:** the IK rule changed once, from closest-contact (11.87) to take-only (9.75). Both are reported, and the new rule is better for the wearer: no ring-made contacts down to -15.4 mm.
- **P4:** no bench or judge file changed in the row's commits.
- **R1 / R2:** the verified number equals the screened one.
- **G5 / G6:** complexity 48.0 recomputes, with J4 counted active at 25 points.

## Numbers this audit could not get

- **The tool's `remeasure`:** unsupported. The model has no `frozen()` / pin-knee `audit()`, and a full IK run is about 21 min. The verifier's full re-run is the independent re-wear on file.
- **The tool's near_touch, dominance, continuity and held_out checks:** they read 'missing' because this row stores its numbers under `claim.near1` / `near2`, `claim.continuity.flood` and `held_out.gap_sample`. The values are read by hand above.
- **contact_depth:** the dumps reproduce the plain 8.76, not the chain-only claim 9.75. The tool requires ±0.05, so it skips them. By hand, T5 is 19.48 vs 20.24 mm on the bench and 55.91 vs 60.97 held: ok.
- **Workspace in-band of the taken ws poses:** not in the dumps.
- **Contacts at the 60 held poses the bench-learned controller loses:** the k-table holds only takes.
- **Skin along the J4 sweep:** unmeasured. It needs per-step wears.

## Proposals (proposals only: none is an input to this verdict)

1. **Commanded redundant joints claim with a controller, not an oracle.** This is a measurement change. Any counted joint whose value an IK chooses is claimed with a map psi(arm pose) learned off the scored poses, for example on envelope nodes outside the bench and held sets, then worn on the claim and held benches. The oracle stays as a reported ceiling.
   - Measured effect on this row: held new takes 119 -> 59, held gate about 10.93 -> at least 17.3. The bench effect is not measured.
   - Affected verified rows: only this row and ikring-distalshell-knuckle-4r (10.54), which is not measured. No 3-joint row has a commanded redundant joint.
2. **Every 4-joint row carries its unpowered MVP1 reading beside the claim:** free, parked, or sprung. Here that is 14.46 for the control and 20.37 parked. No score moves.
3. **K2 / K-track kill bars are set against MVP1-determinate rows:** here 14.46 / 14.06. The oracle 9.75 is quoted only as the powered ceiling.
4. **The audit tool's readers** (an instrument change, for the tool's owner): read `claim.near1` / `near2` / `plain`, `claim.continuity.flood` and `held_out.gate_sample` (flagged as a sample). Accept a per-pose dump whose plain gap reproduces the row's `claim.plain` when the claim is a chain-only gate. This row's four 'missing' checks would then read the numbers above.

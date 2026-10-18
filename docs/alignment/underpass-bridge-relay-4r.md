# Alignment audit: underpass-bridge-relay-4r (2026-10-18 ~21:00 UTC)

## Verdict

The ledger verdict is **gamed** (tool alone: watch). The worst finding is M3, an unchecked clash.

The claim is 13.74 on frozen exact Bench(110,360). That is score 95.00, 0.01 under the 13.75 pass line, read as the
chain-only gate. The design has 4 counted joints, so it is never a lead.

The number is not evidence of a better exo. To score 13.74, the E strap has to run through the bridge shell. Placed so
that the strap actually passes under it, the same bridge reads 19.74 by the model's own rule and 20.60 with the
verifier's full clash check. That is behind the parent offset-shortcar-relay-4r (verified 14.76) and behind the 3-joint
lead (18.28).

The independent verifier reached the same conclusion on its own, before this audit: "REFUTED as claimed, v_gap 20.60"
(docs/concepts/underpass-bridge-relay-4r.md, "Verification", in the working tree at 20:47 UTC; its held-out fix run was
still going). This audit checked that finding independently with its own script (below).

## What the wearer gets (measured)

These are the claimed config's numbers, from the per-pose dumps `docs/concepts/verify/underpass-bridge-relay-4r/verifier_claim_perpose.json`
and `verifier_held_perpose.json`. They recompute 13.73 and 16.63, which reproduces the claim to 0.01.

- **Overhead reach (elevation >= 140):** 8 of 28 taken on the bench, 19 of 71 held out.
- **Raised-arm reach (elevation >= 90):** 63 of 113 on the bench, 168 of 300 held out.
- **Overall reach:** 0.7944 (286 of 360 workspace poses) on the bench, 0.7773 held out.
- **Close metal:** taken poses with metal under 2 mm (walls and crowns included):
  - bench: 58 of 396 (48 on scored metal alone). Under 1 mm: 8. Under 3 mm: 142.
  - held: 138 of 942. Under 1 mm: 30.
- **Contact:**
  - Bench: 13 poses, 43.79 mm summed. The deepest is 9.79 mm at workspace pose (30, 135, 0), then 8.93 mm at
    (15, 165, -60). Twelve are inherited chain contacts. The new one is hardware: the posterior bridge foot, 0.56 mm into
    the arm at pose 466 (150, 105, -105).
  - Held: 43 poses, 173.02 mm summed, deepest 12.24 mm at (15, 135, -15).
- **Workspace in-band (unscored): not measured.** The dumps have no per-pose sample counts for workspace poses, and
  `tools/alignment_wear_probe.py` supports only longdyad, parallelogram and frontload.
- **In-band on clip frames:** 0.9012 chain-only and 0.9021 pooled on the bench; 0.9000 and 0.9009 held out.
- **Springs:** the relay coordinate is held by a constant-force coil on the carriage lug against the zero and PHI
  dowels. No R17 dynamics run is on file.
- **Stops and fold margin:** the minimum `th` is 5.000 deg over 396 taken poses, none below 5 (verifier_claim.json
  pick.th_margin).
- **Continuity:** the verifier's flood drops 0 relayed takes; static equals connected at 13.74.
- **Cuff twist:** not measured.
- **Near-singular postures:** none below the 5 deg margin.
- **What is physically there at the claimed height:** a 3 mm Ti strap whose top face sits up to 1.7 mm inside a
  2.5 mm Ti shell. As claimed, the mechanism cannot be assembled.

## Checks (tools/alignment_audit.py, docs/alignment/underpass-bridge-relay-4r.json)

The tool's verdict is watch. Most of its watch reasons are reading gaps, not measured problems:

- **held_out:** watch, because the row has no verified gap yet.
- **near_touch:** watch, because the tool finds no near-touch file. The row does carry near1 17.91 and near2 38.22.
- **continuity:** watch, because the tool finds no flood file. The verifier's flood is in verifier_claim.json
  pick.continuity.
- **idle:** watch, because the K, crank and knee spans are not on file.
- **sampling:** watch, because no per-part record is on file.
- **contact_depth:** read "not measured", because the tool looks only for alignment_paired / wear-probe dumps. The
  verifier's per-pose dumps are on file and reproduce the claim.
- **Every other check is ok.** Complexity recomputes to 53.0, the same as the row. The judge_change check found no
  bench or judge file moved in the row's commits.

The audit also ran with `--ref offset-shortcar-relay-4r`. It gives dominance: watch, "cannot compare at 2 mm", for the
same reading gap. The committed audit file is the default run.

**Re-wear: not run.** `tools/alignment_audit.py remeasure` needs a model with `frozen()` calling a pin-knee-style
`audit()`, and this model is an OS.wear / hwsweep model, so it is unsupported. The farm budget is also spent (CLAUDE.md
status 15:49 UTC: exo-cpu1 workersMax 0), and the local box was at load 11 on 4 cores with three verifier processes
running.

Instead, this audit used the verifier's per-pose dumps, which reproduce the claim, and ran one light independent check
of its own (below).

## Independent check by this audit

Script: `docs/alignment/remeasure/underpass-bridge-relay-4r_striptop.py`. Output:
`docs/alignment/remeasure/underpass-bridge-relay-4r_striptop.json`.

It imports the model unchanged, prepares on fit Bench(60,160) fast, and uses the strict shell footprint
(|s - s0| <= SH_W/2, azimuth in [lo, hi]) over all 184 fit kin_ok frames at phi 0. Results:

- The E strap's skin-facing underside (rigid E) reaches 79.99 mm.
- Its top face (contact set 23 on member 3, E + T_LINK along the skin normal) reaches **82.87 mm**, at the same
  frame, 68.
- The frozen shell underside is R_under 81.307.

So the strap top is above the underside on **62 of 184** fit frames. This confirms the verifier's need_all reading
(shell need 83.00 on fit frames, 83.02 on the claim bench) from different code.

## Answers to the three flags

1. **Is the 13.74 config picked on the claim bench? No.**
   - The pick (`pick.json`, 19:31 UTC) was written before the claim read (19:34:55 UTC). The claim was read once.
   - The envsel 14.59 and the claim 13.74 differ because they are different benches; the claim bench's own ideal-relay
     bound is 13.21.
   - A tie-break addendum was written after cells 1-5 had read. Those cells tie at 14.59, and the post-claim diagnostic
     reads 13.74 at foot heights 1.0, 1.5 and 2.0 (`diag_claimbench_postH.log`). So no number was bought by the pick.
2. **Posterior foot at pose 466 (-0.56 mm).** The score charges it as a contact (+0.24), so it is not hidden.
   - It is the claim's only hardware contact, but it is not the binding problem: the bridge height is.
   - At the corrected bridge height the foot clears 466 by only 0.59 mm (0.46 mm at the 1.0 mm minimum). That is metal
     parked just outside the cutoff (T1).
3. **In-band switching between chain 0.9012 and pooled 0.9021.** This is not a cherry-pick. Every file's gate takes the
   worse of the two readings:
   - claim: both readings pass, so the gate equals the plain gap, 13.74;
   - parent: chain-only 0.8898 fails, giving 14.76;
   - corrected bridge: pooled 0.8347 fails, giving 19.74.

   The pooled reading is exactly what the honest bridge loses. Raising the shell above the strap top takes its
   skin-facing metal out of band.

## Findings (docs/alignment/underpass-bridge-relay-4r.findings.json)

### M3 (gamed): unchecked clash, the strap passes through the bridge

The shell underside was frozen at 81.307: E's underside maximum (80.11) plus 1.2 mm. The strap is 3.0 mm thick
(T_LINK), and its top face reaches 83.02, up to 1.7 mm inside the shell [81.31, 83.81].

The verifier's X1 check reads the strap top at 0.0 mm from the shell and the T-nut flange:

- claim bench: 409 of 409 evaluated poses jam, so all 396 taken poses are lost, and the rescored gap is 375.0
  (verifier_claim.json pick.xcheck_drop0);
- held: 940 of 942 taken poses lost.

The bridge placed by the design's own rule over every chain set:

| Placement | R_under | Model rule | With X1 |
|---|---|---|---|
| Design's rule (up_clr 1.2) | 84.222 | 19.74 | 20.60 |
| Legal minimum (1.0 mm) | 84.022 | 19.06 | 19.92 |

Source: verifier_fix.log. Pooled in-band drops from 0.9021 to 0.8347.

**Why the exo is not better:** the claim ranks the design 1.02 ahead of its parent and over the 95 line. Built so that
it moves, it is 4.3 to 5.8 points behind the parent and behind the 3-joint lead. The under-pass does not remove the
parent's in-band cost; it moves that cost from the strap's bump to the shell.

**Action:** do not call this design a pass, verified or a 4-joint 95. Replace the row's number with the verifier's
corrected reading when the verifier lands. Any re-claim must place the bridge over every chain set, contact-only sets
included.

### NEW-skin-only-thickness (watch): a part's thickness lives only in a skin-check set

This is the new pattern behind M3.

- The kit samples a strap at its skin-facing face (M.rigid and M.link_pts).
- It keeps the strap's top face, the hub crowns and the knee-link top as "contact-only" sets, which are checked against
  the skin and nothing else.
- The model's `need_scan` (model lines 165-207) and the parent's jam rule read only the rigid and link sets.

To them, a 3 mm strap is a 0 mm sheet. In the parent, the rigid bump lifted the contact sets along with the strap, and
the parent's verifier X1 found 0 new jams. Removing the bump exposed the gap.

**Action:** see Proposal 1.

### T2 (watch): two knife edges

- The gap is 0.01 under the pass line. One more contact pose costs +0.24.
- In-band sits 0.0012 to 0.0021 above 0.90 on the bench and exactly 0.9000 chain-only held out.
- The 3-14 mm band reading was not measured.

### G1 (watch): metal hugging

- 58 of 396 bench poses (138 of 942 held) have metal under 2 mm.
- Near-touch: near1 17.91, near2 38.22.
- Against the parent, the design is 1.02 ahead on the gate and 0.52 behind at 2 mm (parent near2 37.70).
- At the corrected height the foot sits 0.59 mm off the skin at pose 466.

### T5 (watch): depth-blind contact

- Bench: 13 contacts, 43.79 mm summed, deepest 9.79 mm.
- Held: 43 contacts, 173.02 mm summed, deepest 12.24 mm.
- The 3-joint lead has 4 contacts / 20.24 mm on the bench and 14 / 60.97 mm held (x2.2 and x2.8).

All of these depths are inherited chain contacts plus the foot. The score charges them, but on a plain raise to 135 deg
the wearer gets J2's hub pressed 10-12 mm into the arm.

### S3 (watch): bodies the bridge needs that nothing samples

- The cantilever root moment (242.7 N.mm at the claimed height, 249.6 N.mm at the corrected height) needs a rigid
  arm-band anchor that the row itself calls unmodelled.
- The constant-force strip has no guide surface. The spec's "recess on the shell top" does not fit a drum outside the
  shell band. The verifier modelled the strip as a straight chord, as a diagnostic only.

### M5 (watch): a spring-held coordinate scored at its planned state

- No R17 dynamics run is on file.
- At the claimed height, the 4 N tip deflection (0.31 mm) drops E's underside below 1 mm at poses 118 and 163, which
  adds 2 jams. This is moot at the corrected height.

### R2 (watch): a refuted pass is still displayed

The row and the dashboard (`docs/dashboard/data/morphs.json`) still show 13.74 as "4-JOINT PASS BY 0.01 (claim,
unverified)", while the verifier reads refuted, 20.60. It is labelled unverified, so it is not R1 today. It becomes a
refuted record if the row is not updated when the verifier commits.

### Patterns checked and not found

- **T3:** the margin is read on `th`, minimum 5.000 deg.
- **T4:** R_under comes from a rule and up_clr is the larger option, so no search bound walks.
- **S1:** frozen claim bench plus the held set.
- **S2:** no thin part with bad metal was found.
- **S4:** the skin is unchanged.
- **S5:** the flood drops 0 takes.
- **M1, M2:** O20 hubs, 0 passive translations, catalogue T-nut, dowels and coil. The anchor is under S3.
- **M4:** the relay arc spans -1.65 to 45.65 deg, so the relay moves.
- **P1:** held 16.64 vs claim 13.74, +2.90.
- **P2:** no held-out import.
- **P3:** the claim and held benches were each read once.
- **P4:** no bench or judge file in the row's commits.
- **R1:** the row is labelled unverified.
- **R3:** a pre-registered discrete grid; the top-5 spread is 0.00.
- **R4:** the dashboard number equals the row.
- **G2:** no stiff preload is declared.
- **G3:** cuff twist not measured.
- **G4:** see T3.
- **G5:** complexity recomputes to 53.0.
- **G6:** the row says 4 joints, never a lead, and the dashboard says so too.

## Proposals (measurement changes; not applied, not inputs to the verdict)

### Proposal 1: proposed catalogue entry M6, "a part's thickness lives only in a skin-check set"

- **Looks like:** a bridge, under-pass or stacked part placed with "x mm of clearance" over a strap or link, where the
  clearance is read from the strap's skin-facing samples.
- **Why not better:** the strap's top face (T_LINK 3 mm higher) is inside the other part, so the mechanism cannot be
  assembled.
- **Detect:** any metal-to-metal placement or jam rule must read every rigid, link AND contact-only set. The verifier's
  X1 / need_all here, and the offset-shortcar verifier line 57, already do this.
- **Proposed rule:** a relay or bridge claim is not "screened" until X1 covers the contact sets.
- **Measured effect on the verified rows:**
  - offset-shortcar-relay-4r: 0 new jams (its verifier's X1 already includes the contact sets), so its 14.76 is
    unchanged.
  - The 3-joint rows have no bridge, so the rule does not apply to them.
  - Other relay rows (e.g. phi40-thinstack-relay-4r, being verified now) are not measured here.

### Proposal 2: `contact_depth` should also read docs/concepts/verify/<id>/*_perpose.json

This applies when a dump's recomputed gap reproduces the claim. These dumps are the T5 files the lead's rule asks
verifiers to write, and today the tool reports "not measured" for this row. It changes no score.

### Proposal 3: extend `alignment_wear_probe.py` with an OS.wear adapter for the offset relay family

This would read the unscored workspace in-band of the relay family. It changes no score.

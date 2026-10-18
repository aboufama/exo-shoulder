# Alignment audit: phi40-thinstack-relay-4r (round 107, lens A fallback)

Auditor run, 2026-10-18 ~20:46-21:15 UTC. The tool is tools/alignment_audit.py version 2026-10-18.1, run with reference
conecut-knee-knuckle-3r (the verified 3-active lead). Ledger: `python3 tools/alignment_ledger.py get phi40-thinstack-relay-4r`.

## Verdict: WATCH (claim gap 14.06, screened)

- The claim is gap 14.06: frozen exact Bench(110,360), chain-only buildable gate, read once at the envsel pick PHI 40 /
  delta 3.5. That is score 94.89, 0.31 short of the 95 line. The plain reading is 13.52 and held out is 16.69 (plain
  16.02).
- This audit re-wore the claim with the model unchanged (tools/alignment_wear_offset_relay.py, which already supports
  this family). It reproduces gate 14.06, plain 13.52, near1 18.18, 17 contacts, 0 jams and 290 workspace takes to
  0.00. The independent verifier, running at the same time, also reproduces 14.06 / 13.52 (verifier_claim.log line 2).
  That makes three reproductions.
- No hard rule is broken: O20 hubs, fold margin min 5.000 deg in th (0 of 400 taken bench poses below 5, 952 held),
  0 passive translations, 4 DOF. Complexity recomputes to 51.25.
- No finding shows the number ranking this design above a design that is better for the wearer under a gate the user
  keeps, so nothing is gamed. The nearest thing is the PHI 35 -> 40 band: ahead plain, behind at 1 mm and 2 mm on the
  same hardware (finding G1). Near-touch is report-only under the user's 2026-10-17 ruling.
- The row is screened, not verified: its verifier was running during this audit. It must not be called verified until
  the verifier's file lands.

## Tool checks (docs/alignment/phi40-thinstack-relay-4r.json)

Three of the 14 checks read watch. The other 11 read ok.

- **held_out:** there is no verified bench gap on the row. It is screened, and its verifier was running.
- **dominance:** the row beats conecut-knee-knuckle-3r by 4.76 plain but loses by 12.32 at 2 mm. The A1 gate is
  retired, so this reads watch.
- **continuity:** the tool reads "no flood on file". This is a gap in the instrument: the flood is on file with 0
  dropped. See the section on tool gaps below.

Ledger entry, 2026-10-18T21:05:25Z: the verdict is watch, made of the 3 tool items plus 6 judgement findings.

## What the wearer gets (measured)

Sources: this audit's re-wear, docs/alignment/remeasure/phi40-thinstack-relay-4r_bench.json and _bench_perpose.json;
the row's held dump docs/concepts/verify/phi40-thinstack-relay-4r/held_pick_perpose.json (reproduces held plain 16.02);
and this audit's held re-wear, docs/alignment/remeasure/phi40-thinstack-relay-4r_held.json and _held_perpose.json
(reproduces held gate 16.69, plain 16.02, 48 contacts, 0 jams, 750 / 952 taken to 0.00).

**Reach**

| | bench | held |
|---|---|---|
| Overhead taken (elev >= 140) | 9 / 28 | 22 / 71 |
| Raised arm taken (elev >= 90) | 67 / 113 | 176 / 300 |
| Workspace taken | 290 / 360 | 750 / 952 |
| Verified parent offset-shortcar-relay-4r (overhead, raised, workspace) | 8 / 28, 63 / 113, 286 / 360 | 19 / 71, 168 / 300, 740 / 952 |
| 3-active lead conecut-knee-knuckle-3r | 8 / 28, 47 / 113, 262 / 360 | 18 / 71, 123 / 300, 659 / 952 |

- Bench by elevation: elev >= 120 takes 28 / 62 and elev >= 160 takes 3 / 15.
- Against the parent, the design takes 4 more bench poses and loses none. On held it takes 11 more and loses one
  (211, behind-back ER, which becomes a contact on the anterior shell end at +48.9 deg, -0.49 mm).
- Every overhead pose it adds over the parent and the lead sits within 1.1 mm of the skin: 370 at 1.08 mm on the
  bench; 896 at 0.10 mm, 963 at 0.52 mm and 1036 at 0.62 mm held (969 at 0.24 mm against the lead).
- The overhead takes of all three designs hug the skin. The bench overhead metal runs 1.08-2.88 mm here (median
  2.0) and 1.71-2.88 mm for the lead. The 10th-percentile overhead metal is 1.80 mm (deep_audit).

**Near-touch**

- Taken poses with metal < 1 / 2 / 3 mm on the bench: 9 / 50 / 136 (43 workspace and 3 overhead below 2 mm). The
  parent has 8 / 47 / 133. The minimum metal on a taken pose is 0.072 mm, the same as the lead's.
- Gap with metal < t mm counted as contact, on the auditor's deep basis: 13.52 plain, 18.18 at 1 mm, 47.16 at 2 mm,
  100.73 at 3 mm. The parent reads 13.74 / 17.91 / 46.08 / 100.04 and the lead 18.28 / 19.92 / 34.84. So 33.64 points
  live in the 1-2 mm shell.
- Held, on the same deep basis (this audit's held re-wear): 16.02 plain, 22.99 at 1 mm, 47.92 at 2 mm, 97.52 at
  3 mm. The parent reads 16.63 / 22.83 / 47.71 (its skeptic's same basis) and the lead 22.38 / 25.23 / 37.11.
- Held taken poses with metal < 1 / 2 / 3 mm: 32 / 123 / 305 (4 / 9 / 20 overhead). The held overhead 10th-percentile
  metal is 0.62 mm (bench 1.80).
- Band read 3-14 mm: 16.02 held, unchanged.

**Contact**

| | contact poses | summed depth | deeper than 3 mm | deepest |
|---|---|---|---|---|
| bench | 17 | 74.92 mm | 7 | 15.37 mm at ws (30, 150, -30), elev 150, relay phi 39.7 (chain 14.42 mm in) |
| held | 48 | 198.11 mm | 23 | 13.89 mm at (45, 150, -15), phi 35.2 |
| parent bench / held | 13 / 43 | 46.18 / 173.02 mm | 5 / 21 | 9.79 / 12.24 mm |
| lead bench / held | 4 / 14 | 20.24 / 60.97 mm | 3 / 9 | 8.93 / 9.86 mm |

- The second deepest bench contact is 13.78 mm at (150, 60, -120), phi 39.3. The chain is 12.67 mm in, and the L-lug
  bracket is 5.63 mm into the skin as well.
- 13 of the 17 bench contacts are relayed poses. 466 (-0.33 mm) is a hardware-only contact on the posterior shell end.

**In-band**

- Chain-only in-band is 0.8946 (pooled 0.9169), and 13.52 is unchanged with the band read as 3-14 mm. The clip-frame
  metal histogram has 0.07 % of samples at 1-2 mm and 0.35 % at 2-3 mm, so nothing sits on the band edge.
- Per part, the hardware levers' in-band gain is the E strap: 0.915 -> 0.940 in band, median 10.29 -> 9.60 mm. The
  lowest parts are L2 0.731, hub3 0.742 and crank 0.801. Part-weighted chain in-band is 0.922 against sample-weighted
  0.8946. All 15 groups are sampled. L1a is thin at 8 samples per frame.

**Springs, stops, cuff, singular postures**

- The relay is a constant-force coil, 12 x 10 on the carriage's lug. R17 is inherited from proxtrack: 0.063 N.m,
  coil >= 0.79 N. The row's own arithmetic gives a 0.22-0.62 N margin over gravity plus tape friction. Friction,
  return, hysteresis and cuff twist are not on file (finding M5).
- The J2 stops hold th at min 5.000 deg. The 5 lowest taken poses are all at 5.000-5.003 deg (claim_phi40.json
  pick.th_margin), so the stops are in use. How many taken poses sit within 5-6 deg is not on file.
- The cuff knee moves 46.7 deg (K.ang 59.3-105.9) and K moves 46.3 deg. The relay moves up to 39.88 deg (41 relayed
  bench poses: 28 taken, 13 contacts).
- Continuity: the PHI 40 flood is on file (claim_phi40.json pick.continuity and held.json). 0 relayed poses are
  dropped and static equals connected. 174 of 177 relayed env poses are connected, and 26 phi-jump edges are refused.

## Findings

1. **T5, contact depth (watch).**
   - Bench: summed 74.92 mm against the lead's 20.24 (x3.70, +54.68) and the parent's 46.18 (x1.62).
   - Held: 198.11 mm against 60.97 (x3.25) and 173.02.
   - All 13 bench contacts beyond the lead's 4 are poses the lead loses to its fold or stop.
   - The PHI 35 -> 40 band alone turns 4 relay-stop poses into presses (31.36 mm on the bench), including the two
     deepest, 15.37 and 13.78 mm.
   - The score charges these poses more than a stop, so it does not reward them. Still, the wearer gets a 15 mm
     press on an overhead scapular-plane raise where PHI 35 gives a stop.
   - Action: cap the relay where the chain dives (the row's own next step, a skin-aware stop near 37 deg), or price
     the band's contacts before calling PHI 40 a reach gain.
2. **G1, metal hugging in the PHI band (watch).**
   - Same hardware, same harness (bench, per-pose dumps): PHI 40 against PHI 35 reads plain -0.21, 1 mm +0.27,
     2 mm +1.08. These are on one formula that reproduces each plain gap and holds follow fixed. Neither cell relays a
     clip frame, so the deltas hold on the deep basis too.
   - Of the 8 poses the band evaluates on the bench, 4 are contacts and 3 of the 4 takes are under 2 mm
     (0.21 / 1.08 / 1.74). Only 417, at 3.79 mm, is an in-band take.
   - Held: 15 band poses, 4 contacts, and 4 of the 11 takes under 1 mm.
   - Against the verified parent the row is ahead plain (bench 0.21, held 0.61). At 1 mm it is behind (0.27 / 0.16),
     and at 2 mm behind again (deep basis: 47.16 vs 46.08 bench, 47.92 vs 47.71 held).
   - Against the lead it is 4.76 ahead plain and 12.32 behind at 2 mm (the tool's dominance check).
   - Why this is not a better exo: on a real, bulging arm the band's overhead gain is metal on skin.
   - It is report-only under the user's ruling.
3. **S3, the coil strip (watch).**
   - The constant-force strip of the lug coil is not in the claim model.
   - The verifier's X3 check finds two realisations. The free chord keeps 14.06, but at its lowest it reaches radius
     76.61 mm against the liner surface at 79.1 mm, 2.49 mm into the 4 mm liner. A guide arc under the strip clashes
     with the chain on 326 of 417 poses (172.4).
   - Action: state the strip's path through the liner on the part, or route it over the shell and re-wear.
4. **M5, return spring (watch).**
   - The margin over gravity plus friction is 0.22-0.62 N on a 2.0 N coil. The coil is now on a new lug and the
     travel is now 40 deg.
   - No return or hysteresis test exists.
   - Action: the same test the parent's skeptic asked for, on this hardware.
5. **G6, 4th joint (watch).**
   - The 4.22-point lead over the 3-active lead comes from a counted 4th joint (complexity 51.25 against 18.5).
   - Overhead it buys only skin-hugging poses: bench +1 at 1.08 mm, held +4 at 0.10-0.62 mm.
   - The real gain is the raised arm: 67 against 47 of 113 on the bench.
   - The count is honest. Never display the row as the overall leader.
6. **P1, forward (watch).**
   - The claim bench has been read at five configurations of this hardware: 14.06 (claim), 13.67 (delta 5.0),
     13.55 (lean 0), 14.02 (delta 6, 5 jams) and 14.28 (PHI 35). Two of them read under the 95 line.
   - The row labels them diagnostics, which is right. But it plans the next relay row on exactly those two levers.
   - Action: that row's claim must be read on held or a fresh bench, never on Bench(110,360).

Checked and not present:
- T1: reported under G1 (9 bench takes under 1 mm, against the parent's 8). The 1 mm reading moves the gap by 4.66,
  against the parent's 4.17.
- T2: the band read as 3-14 mm leaves 13.52 unchanged.
- T3: the margin is read on th, 5.000 deg.
- T4: the pick's +1.5 deg partner reads +0.12 on envsel. The claim bench's cliff (delta 6.0, 5 jams) is 2.5 deg away.
  The posterior shell end is a one-pose cliff (259 envsel, 466 claim), and it costs the claim rather than flattering
  it. The verifier's delta 3.0 red team on the claim bench reads 14.01 with 0 jams (466 at -0.94 mm), so the low side
  is not a cliff either (verifier_claim.log, post0).
- S1: held 16.69, which is +2.63 over the bench and below the 6.0 watch line.
- S2: part-weighted 0.922 against sample-weighted 0.8946 (chain), so it is not flattered.
- S5: 0 dropped.
- M1 / M2: hubs are O20. The shell is a 1.0 mm Ti sheet on the liner and the carriage 1.4 mm high. Both are real
  thicknesses, but no stiffness check is on file (see "could not get").
- M3: the verifier's X1 / X2 checks add 0 jams and 0 contacts (14.06).
- M4: K, the knee and the relay all move.
- P2: held read once at the pick.
- P3 / R3: the claim was read once at a pick written before the claim log was opened. The envsel spread (9 readings,
  top-5 spread 0.41) is on file.
- P4: no bench or judge file in the row's 3 commits.
- R1 / R2 / R4: the row, verifier files and dashboard agree on screened 14.06.
- G5: complexity recomputes to 51.25.

## Tool readings that are gaps of the instrument, not of the design (for the tool owner)

- **continuity (watch).** The tool reads "no flood on file", but the flood is in the verify dir
  (claim_phi40.json and held.json, pick.continuity: dropped_relayed 0, static = connected). This is the same gap the
  parent's skeptic refuted. Proposal (repeated): also read `<verify>/<id>/*.json:*.continuity`.
- **T5 against the lead is still blind.** contact_depth prints "no bench depth of conecut-knee-knuckle-3r on file"
  although docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json exists. This is the _depth_sources
  failure the parent's audit reported. Measured by hand here: x3.70 bench, x3.25 held, both past the 2x / 5 mm line.
- **Before this audit's re-wear**, near_touch, idle, sampling and contact_depth read "not on file". The numbers were
  in the row (frozen_exact.near1 / near2) and in the verify dir's per-pose dumps, which the tool does not read.

## Proposals (measurement changes, not applied, not used in the verdict)

- **A1. A band-end column for travel levers.** When a row extends a relay or stop travel, it reports the takes and
  contacts the extension adds, with each take's metal and each contact's depth.
  - Measured on this row: PHI 35 -> 40 adds 8 evaluated bench poses. 4 are contacts (31.36 mm). 3 of the 4 takes are
    under 2 mm.
  - Other verified rows: only offset-shortcar-relay-4r has a relay travel lever. Its PHI 35 was never compared with a
    shorter travel.
- **A2. Depth-weighted contact as a reported column (not the score).** Report sum(depth) / (n_evaluated x 1 mm)
  next to the contact share.
  - Measured: this row bench 74.92 mm / 417 poses = 0.180 mm per pose; parent 46.18 / 409 = 0.113; lead
    20.24 / 376 = 0.054.
  - It would rank the three rows in the reverse of their gap order.
- **A3. The strip / tendon rule.** Every spring strip, cable or tendon in a model is sampled as metal along its path
  (chord or guide) in the claim model, not only in the verifier.
  - Measured: this row 14.06 (chord) or 172.4 (guide).

## Numbers this audit could not get

- **R17 return, friction, hysteresis and cuff twist.** No judge exists for this hardware.
- **Shell and carriage stiffness** (1.0 mm slotted Ti shell, 1.4 mm carriage). No FEA was run, and the thin shell's
  share of the -0.48 hardware gain is not isolated (the row reads all the levers together).
- **PHI 35 held on the same hardware**, which would show the band's held effect under one harness. This would need a
  held prepare at PHI 35 (~15 min, and no slot was free).
- **The th distribution between 5 and 6 deg.** Only the min and the 5 lowest are on file.
- **Per-part density** (tools/sample_density.py): not run, time box.

Files from this audit:
- docs/alignment/phi40-thinstack-relay-4r.json
- docs/alignment/phi40-thinstack-relay-4r.findings.json
- docs/alignment/remeasure/phi40-thinstack-relay-4r_bench.json
- docs/alignment/remeasure/phi40-thinstack-relay-4r_bench_perpose.json
- docs/alignment/remeasure/phi40-thinstack-relay-4r_held.json
- docs/alignment/remeasure/phi40-thinstack-relay-4r_held_perpose.json

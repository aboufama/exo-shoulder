# Round 11 ideation: judge and red team (2026-10-17 ~09:58 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)). The real target is gap 0, and 95
(gap 13.75) at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered, exactly 3 active DOF.

Lead to beat: slipper-nose-knuckle-3r, verified 18.49 (score 93.28; Bench(110,360) exact frozen, margin 5, O20), held out
23.45, ledger WATCH (M5, G4, T5, ws-inband). Its gap is reach 17.50 + in-band 0.45 + contact 0.54.

Nine candidates came in from three lenses: coupler-longstroke (3), lobe-free four-bar (3) and overhead-cone (3).
After merges and measured deaths, four are picked. All nine have 3 active joints and 0 passive translations, and every
joint is a catalogue or plausible part. No candidate was rejected on hardware, translations or an undetermined coordinate.

## Red-team checks made by the judge

Scripts and outputs: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge11/`
(`ib_dog.py`, `ib_dog_f2.py`, `fb_b1.py`, `lead_parts.py` and their `.log` files). Each one runs on the proposer's own
harness, imported unchanged.

### 1. The dog-ring drive, priced in the bench's own currency (pooled in-band)

The bench's in-band14 is pooled. It is the share of ALL metal sample points (about 1 point per 4 mm2; an O20 hub disc is
80 points) lying 2-14 mm from the skin, over the taken clip frames. So a part costs (its out-of-band points) / (all
points). The proposer reported per-part shares (ring 0.05-0.14, drag link 0.26-0.42) and estimated the total change at
-0.003 to -0.008. Measured in the proposer's own `coupler_lens/metal.py` (exec'd unchanged), on the 36 law-closed,
chain-clear clip frames of Bench(60,160) fast:

- chain = the model's rigid + link samples minus its RSSR parts;
- the ring is resampled at bench density (r 10.2-12.5 mm: 39 points);
- the strap and pin duplicates of metal.py's h = 0 sampling are removed.

| cell | chain alone | chain + dog drive as specified | delta | ring moved to hub 2's skin-face level |
|---|---|---|---|---|
| 34/46 (seed rank 0) | 0.8949 | 0.8298 | **-0.065** | 0.8565 (-0.038) |
| 32/48 (seed rank 0) | 0.8876 | 0.8271 | **-0.061** | - |

Per part, 34/46 (points per clip frame @ in-band share):

| part | points | in-band | out-of-band points |
|---|---|---|---|
| ring | 39 | 0.141 | ~34 |
| drag link | 40 | 0.257 | ~30 |
| arm | 44 | 0.761 | ~11 |
| pins | 32 | 0.881 | ~4 |
| horn | 12 | 0.877 | ~1.5 |

**The lead's own drive, for comparison.** slipper-nose on Bench(60,160) fast, row params, `parts_ib14`, 912 points per
frame:

- crank: 129 points @ 0.819;
- nose / roller: 19 @ 0.927;
- horn lug: 23 @ 0.946.

The lead's chain alone would be 0.906, so its drive costs 0.011.

**Reading.**
- As specified, the dog drive costs **+5.0 to +5.5 gap points more than the lead's drive**, not +0.3 to +0.8.
- Putting the ring on hub 2's skin-face layer (a C-ring or sector) halves that to about +2.8.
- The drag link, stacked above the arm, is then the largest single term: about 30 out-of-band points, about 3 points.
- With the drag link brought to about 0.75 in band, the drive would cost about +0.7 vs the lead.

So the claim stands or falls on layering. Pooled pricing is now part of gate B.

### 2. What the extra law-only poses turned into last time (longstroke ghost, longstroke_drive.md section 8)

The only frozen measurement on file of a long-dyad chain past the lead's stroke is the ghost (drive metal deleted, kK
3.0). It went from law-only 273 to frozen exact reach 0.739 (266) plus **7 contact poses**. The lead went from 263 to
261 + 2. So +10 law-only poses became +5 taken and +5 contacts:

- bench net -0.24;
- held out -2.34 (the only held-out gain on file).

The proposer assumes that 68-100 % of its +21 law-only poses park and that none of them turns into a contact. At the
ghost's measured split the +21 net about 0 on the bench and -2 to -4 held out. The K-open contact term in the search
(fit poses with dK > 20 and metal < 1 mm counted twice) is what decides it; the 0-contact fast check counted drive parts
only, on chain-clear poses (127-129 of 189-193 law-closed).

### 3. The four-bar's B1 count, by how far K is from rest

Proposer's `fb2.py` / `lawtab.py`, seeds unchanged, Bench(110,360), law-only. The lens 2 "strict" reading
min(m_sub, m_eff) >= 5 is, for a K that never rests exactly on a stop, simply **today's family reading**: the lead family
reads m_plain only where K sits exactly on stop A, and min(m_sub, m_eff) everywhere else.

| seed | law-only | B1 fails | abs K 0-1 deg | 1-3 | 3-6 | 6-10 | 10-20 | >= 20 |
|---|---|---|---|---|---|---|---|---|
| toggle43, hub-cap pins | 289 | **122** | 34 / 34 | 10 / 10 | 16 / 16 | 15 / 15 | 40 / 43 | 7 / 171 |
| strap_t43, strap lugs | 291 | **118** | 26 / 26 | 18 / 18 | 13 / 13 | 17 / 17 | 35 / 35 | 9 / 182 |

Each cell is fails / taken poses in that band.

- Every taken pose with abs K < 10 deg fails. m_sub < 1 on 63 poses; m3e < 5 on 0. The failing poses sit at th 30-71
  (p50 51.5-53.4).
- **Today's family reading:** law-only 167 / 173, against the lead's 263.
- **Reading abs K < 1 deg as rest:** 201 / 199.
- **The coupled reading (m_sub waived for a slaved K):** 289 / 291.

So the exposure is not the lead's G4 rest set. It is the coupled reading on a K that is moving 1-20 deg, which is the
pattern the audit ruled gamed for dipped-law-groove (T3).

The physical case is stronger here:
- the four-bar is positive both ways (no spring, no lift-off);
- m3e >= 5 holds on every pose;
- dth/dtau >= 1/3.45 is enforced, so th(q2) is monotone and the inverse is unique.

That makes it a clean question for the user's B1 ruling ("for a positively slaved K, does m_sub apply?"). It is not a
claim.

Also measured:
- **Knee:** 1 / 2 taken poses run past 153.12 deg (the build rule ang_min 26.88) on the lead's knee, so the knee needs a
  re-fit.
- **Load:**
  - compact cell, r_h 3.1-4.4 mm: the coupler force is M_K / (r_h sin mu_h), about 260-370 N per N.m, or 52-74 N per eye
    at the MVP1 0.2 N.m. An MR63ZZ's C0r is roughly 70-90 N (from memory; confirm), a static factor of about 1-1.7. The
    compact cell needs plain iglidur eyes (about 8 MPa on O3 x 3);
  - strap cell, r_h 12.3: about 19 N.
- **Hub-cap eyes:** they sit at crown level, about 12 mm above the hub faces. The coupler cannot be both stacked on link
  1b (at + 3.15) and pinned on the caps without a joggle, and the eyes must be sampled as metal.

### 4. G4 on the long dyads (proposer's msub logs, read from file)

With K on stop A, m_sub < 5 on rest poses:

| design | rest poses | m_sub < 5 |
|---|---|---|
| dogring 34/46, smhi 22 | 156 | 133 |
| dogring 38/42, smhi 22 | 156 | 97 |
| lead | 206 | 108 |

On the moved poses: m_sub min 6.78 / 9.8 and m3e min 5.3 / 5.31, so both pass today's reading.

Under a strict B1 ruling every one of these rest sets dies, the lead's included. The 38/42 "B1-robust" cell lowers the
count but survives a strict ruling no better than the lead does. It is a dyad cell of the same drive, so it is merged.

### 5. Other claims checked

- **dogring gate A re-base (290 -> 282):** accepted. The proposer's unconstrained stage-1 search (about 13,600 laws per
  dyad) tops out at 286-288. The window's 298-300 includes 14-15 knee and 1-5 m3e poses no law can take.
- **dogring hub K clearance:** +0.4 / -0.03 mm in the proposer's sweep. The gate needs >= 1 mm.
- **coupler-longdyad:** its kinematic ceiling equals dogring's (285 / 732 vs 284 / 727), and stage 1 adds a sliding nose
  at 60-80 N (about 930 MPa Hertz, DLC required). Its own fast metal check: crank boss 0.09 in band, coupler 0.69, and
  25 drive skin contacts (12 of 44 K-open, to 18 mm deep). All 24 PA-legal geometries sit 27-30 deg off link 1b. Every
  term the judge can price favours dogring.
- **trimlug-k165:** the clocking table and the r 17.3 / 19.8 band are consistent with the ledger's T5 depths (9.01 +
  5.74 mm). The risk is in-band: the 2.5 mm lift raises the nose end of a 129-point crank whose median is 11.2 mm. About
  10-14 points leaving the band costs 1.1-1.5, which outweighs the +0.55 ceiling. Wear it on the 150 s 'cone' set first.

## Verdicts, all nine

| # | candidate | verdict | reason |
|---|---|---|---|
| 1 | dogring-draglink-knuckle-3r | **PICK 1** | The only reach lever with a real mechanism under today's fold reading. It deletes stage 1 (PA 0, no lobe, no sliding pair, so the lead's M5 goes away). Its in-band claim is refuted (section 1), so it is re-aimed at layering. |
| 2 | coupler-longdyad-knuckle-3r | **PICK 4** | Valid, but dominated by dogring (same ceiling, measured drive contacts, sliding nose at 60-80 N). Kept as the lobe-input control with a hard kill. |
| 3 | dogring-equidyad-knuckle-3r | **merged into 1** | The same drive on the 38/42 dyad. Its B1 hedge does not survive a strict ruling (section 4). Carried as pick 1's third cell. |
| 4 | fourbar-longdyad-knuckle-3r | **PICK 2 (listed for B1)** | cx 14.0 (like-for-like 10.0 vs 18.25), spring-free and positive. Not claimable today: law-only 167 under the family reading (section 3). |
| 5 | sidecar-fourbar-knuckle-3r | **merged into 4** | Same law, IK and B1 exposure; the lugs move to strap level. It becomes pick 2's preferred cell for loads (r_h 12.3). |
| 6 | openhalf-fourbar-knuckle-3r | not picked: measured dead | Proposer's own exact parking: parts in band 0.47 (hub 2 at 81 mm vs 62). It closes the strict branch of lens 2 and is recorded here, not catalogued. |
| 7 | arcspan-knee-knuckle-3r | not picked: measured dead for reach | 0 of 9 frozen: E-L2 collides on all 8 cone knee poses, and hub 2 is 1.4-14.2 mm inside the skin on 7 of 8. Its finding (the knee stays in its window under a 3 mm GH error on 272 / 272 poses, vs 240 / 263) goes to the next knee change. |
| 8 | conehub-knuckle-3r | not picked: measured dead | 0 cone poses at any cone angle; hub-2 clip in-band -0.011 to -0.126. The b2 tilt breaks the closure (0.9-25 mm radial drift). |
| 9 | trimlug-k165-knuckle-3r | **PICK 3** | The only lens-3 lever with a positive ceiling (+1 pose, 17.94 best). Its real value is the lead's T5 depth (14.75 -> about 9.0 mm). |

Lens 3 as a whole reads (a) 0, (b) 0, (c) <= 1, under its own +3 kill line, so the overhead-cone lens stops. Trimlug
runs as a lead polish, not as the lens.

## Ranking (expected gap reduction vs the lead x confidence x buildability)

All rows have 3 active joints and 0 passive translations, so buildability ties on translations. It is decided by the
parts: catalogue part numbers, sliding pairs, loads.

| rank | id | judge's expected frozen gap | confidence | cx (record / like-for-like) | lead note |
|---|---|---|---|---|---|
| 1 | dogring-draglink-knuckle-3r | 18-22 as specified (drive in-band +5.0-5.5 measured); **16-19** with the ring on hub 2's skin layer, a low drag link and the K-open contact term working; 95 needs both | low-medium | 25.75 / ~21.75 | price pooled in-band first |
| 2 | fourbar-longdyad-knuckle-3r | 17-19.5 under the coupled reading (R_est 0.747-0.750 is +9-10 poses; the estimator counts no contacts, and its 28/50 cell, 0.761 at 57.5 deg, sits above the ghost's measured 0.739 + 7 contacts at 52-54 deg); not claimable under today's reading | low (gated on B1) | **14.0 / 10.0** | report the B1 count by abs K; strap cell first |
| 3 | trimlug-k165-knuckle-3r | 17.94 best; likely 18.3-19.0 | medium | 22.25 / 18.25 | in-band cost of the lift on the cone set |
| 4 | coupler-longdyad-knuckle-3r | > 20 likely (25 drive contacts on fast) | low | 27.75 / ~23.75 | kill at gate B < 0.755 or > 2 K-open drive contacts |

The 95 arithmetic is unchanged: gap 13.75 = +18 workspace poses at the lead's in-band and contact. Nothing on the table
reaches it on measured numbers. Pick 1 is the only route with the kinematic room (+21 law-only), and only if its metal
lands at the lead's in-band and the new stretched poses do not come back as contacts.

## Notes for the modellers

- **Pick 1:**
  - run `ib_dog.py` (judge11) on every layering before any farm spend. Gate B adds: pooled delta in-band of the drive vs
    the chain alone >= -0.02;
  - first lever: the ring as a C-ring or sector on hub 2's skin-face layer (measured -0.038);
  - second lever: an arm azimuth t1 that takes the arm tip beside link 1b, so the drag link drops a layer;
  - report the per-pose K-open contacts against the ghost's 7.
- **Pick 2:** state the B1 count in every report as fails / taken by abs K band (section 3), never as one number. Build
  the strap cell first. Give the compact cell plain eyes. Sample the hub-cap eyes at crown level. Re-fit the knee to the
  153.12 rule.
- **Pick 3:** wear on the 'cone' set (110 clip + 27 workspace, ~150 s) and stop if in-band drops more than 0.005.
- **Pick 4:** one CMA batch only. Stop on more than 2 K-open drive contacts or gate B < 0.755, and report the binding
  part.

**Open idea, not catalogued (for a later round):** a two-faced dog whose ring rests at the drag link's own dead point,
with K on stop A there. Turning the ring either way past an onset opens K, which would give the four-bar's folded-side
stroke with K exactly at rest in between. That would be B1-safe under today's reading. The ring is held only to second
order at the dead point (it needs a detent), so it is not yet a legal "determined" joint.

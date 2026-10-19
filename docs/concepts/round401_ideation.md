# Round 401 (K1, track kneeless) ideation: judge and red team (2026-10-19 00:52 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The lead is already past it, so the real targets
are gap 0 and 95 (gap 13.75) without the knee. The plan is docs/concepts/ROUNDS.md "Round 401 plan" (b7bb9b0), with
the restart note (acb1ad3). No bench, judge or kit file changed: no number below moved because the measurement changed.

**Lead to beat (3 joints):** conecut-knee-knuckle-3r, verified 18.28 (93.35), held 22.38, cx 18.5. The track's pass
is <= 15.4 (a clear 2-point-plus margin at 4 joints without the knee); its kill is > 16.28. **Best 4-joint, with the
knee:** phi40-thinstack-relay-4r 14.06 / held 16.69, cx 51.25. **Champion** (the ranking's reference): spherical 3R
75.94 on Bench(110,360) exact.

**Candidates:** nine, three per lens.

- Lens A (knee-less relay on the knuckle chain): kneeless-steer-midbracket, kneeless-steer-capshell,
  kneeless-steer-ebracket.
- Lens B (knee-less pin relay, no knuckle): kfree-o20pin-highexit, kfree-o20pin-steered, kfree-slimpin-lowexit.
- Lens C (ring on the humeral long axis): distal-cband-sq95, insertion-cband, distal-vroller-cband.

Every joint maps to a real part: O20 v5 / MR117-2RS hubs, ISO 8734 dowels, a T-nut carriage on a Ti shell, MR63ZZ
V-wheels on a hardened band, an iglidur shoe, clock and constant-force springs. All nine have 0 passive translations.
No passive coordinate is undetermined once two conditions hold: the relay's spring beats friction and gravity at every
pose, and K is slaved. The first condition decides the J4 hardware of lens C (section 1.4).

**Outcome: four picks, four merges, one rejection.**

1. **kneeless-steer-midbracket-relay-4r** (lens A). capshell is merged in as its s0 -55 cell and ebracket as its s0 -80
   control. The step-0 bound is re-read on an honest bracket proxy (section 1.1).
2. **insertion-cband-relay-4r** (lens C, s 0.30, 93 mm strap). distal-vroller's rolling J4 is merged in as its J4.
   Its band is re-specified across its full width (section 1.3).
3. **kfree-o20pin-highexit-relay-4r** (lens B, the lowest-complexity 4-joint relay). kfree-o20pin-steered is merged in
   as its stop cell. Step 0 runs on the lead-quality chain (section 1.2).
4. **distal-cband-sq95-relay-4r** (lens C, s 0.70), with the rolling J4. The strap kill is re-registered as the
   measured quantity it stood for (section 1.5).

Rejected: **kfree-slimpin-lowexit-relay-4r**. R4 is a counted joint, and the user's 2026-10-16 ruling is "Keep O20
only". The question goes to the user, with its measured price (section 1.6).

**The judge's main finding.** Lens A's headline bound of 15.25 was read with a "bracket" proxy, and that proxy keeps
every knee-side sample at rest: E 164, boss 32, pad 32, knee link 90. Of those 318 samples, 154 belong to parts that no
knee-less design has (scratch k1a/k1.py, KNEE_PARTS = E, boss, pad, knee). Re-derived from the proposer's own per-part
in-band numbers, the best cell reads **14.6-16.8, centre ~15.7**, against the 15.4 pass line. A second finding: lens C's
band numbers come from a single station, and the 26 mm wide band at the deltoid insertion meets a taper that the
single-station model never sees.

## 1. Red-team checks made by the judge

All of the judge's reads are on the fit bench, envsel or Bench(110,360) kinematics only. No metal was read on
Bench(110,360) and no held-out pose was touched.

- Scripts: /tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge401/
  (band_axial.py, band_axial2.py, kin_static.py, append.py).
- Proposer logs re-read: /tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/k1a/
  (relay_P*_env*.log, ctl3.log, seatgrid.log) and /tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/k1b/
  (wr1.out, wr2a.out, wr2b.out, wpost.out).

### 1.1 Lens A: the numbers reproduce, but the bracket proxy pads the in-band

Reproduced from the logs:

- The validation run: b3 0.329, PHI 40 gives 13.92 envsel, phi40's ideal to the digit.
- The 3-joint knee-less control: 23.11 (bracket) and 26.72 (deleted). On today's lead the knee is worth 4.8 to 8.4
  points, not round 9's ~2.2.
- The cells: 84 / -15 at PHI 58 reads 16.85 / 17.68; with the stops 15.25 / 16.07; at PHI 50 with the stops 16.45 /
  17.26.

The "full" reading in k1.py is B.report() over every sample in M, so it includes the boss, the pad and the knee link,
all at their rest positions. The table recomputes in-band with E's samples only, using the proposer's per-part figures
(E: in-band 0.947 over 164 samples; chain without knee-side parts: 0.8762 over 607 samples). Each cell gives two
readings: E's 4 rest-position contacts kept, or dropped with the deleted reading's reach.

| cell | proposer 'bracket' | E full length | 70 % of E | 50 % of E | 'deleted' |
|---|---|---|---|---|---|
| 84 / -15, PHI 58, stops | 15.25 | 14.56-16.12 | 14.94-16.50 | 15.23-16.79 | 16.07 |
| 84 / -15, PHI 50, stops | 16.45 | 15.75-17.32 | 16.13-17.70 | 16.42-17.99 | 17.26 |
| 78 / -15, PHI 58 | 15.83 | 17.60 | 18.05 | 18.38 | 19.36 |
| validation (knee chain), PHI 40 | 13.92 | 15.12-15.64 | 15.73-16.25 | 16.18-16.70 | 17.50 |

Reading the table:

- Where the bracket's metal sits decides the cell. The swing between "E's contacts kept" and "dropped" is ~1.5 points,
  and so is the in-band swing between 50 % and 100 % of E.
- The midbracket's 35-45 mm bracket is about 50-70 % of E. Its honest centre is ~15.7. A pass (<= 15.4) is about
  35 % likely, and staying under the kill line (<= 16.28) about 65 %.
- The cap-shell cell (s0 -55) has no E path, so its honest reading is the "deleted" 16.07. The full-E-bracket control
  (s0 -80, PHI <= 50) reads 15.75-17.99: expected dead at step 0.
- So the three lens-A ideas are one sweep (station s0, bracket length, seat, stops) on one driver, and the judge
  merges them.

Pre-registered for the merged row: step 0 is read on the bracket-honest proxy. That means E's samples truncated at the
carriage lug, no boss / pad / knee samples, and E's contacts kept where the truncated bracket covers them. Kill if every
cell reads > 15.4.

A cross-lens lever: lens B measured the relay axis line as first-order for relayed chain burials on its kit (12/237 is
the worst of 7 lines), even where the kinematics are flat. Lens A fixed its axis at 12 / 235 on kinematics alone, so the
judge adds a tilt {8, 12, 16} x taz {225, 235, 245} metal scan at the best cell. The tilt stays small because the shell
must still wrap the deltoid.

Determinacy: phi40's R17 friction is unmeasured (WATCH M5). The 2 N CF strip has to beat 0.79 N of gravity plus
mu 0.15-0.25 times the shell's normal load. The row reports this zero-return margin per relayed pose; a stalled
carriage is an undetermined phi, and that pose counts as lost.

### 1.2 Lens B: the conflict is resolved, but the hardware price is in-band, on a poor instrument

Accepted: the pin-burial conflict the planner flagged. burial.py puts hub 3 buried on 0 of 39 relayed ws poses at
35/45. The capshell's "6-18 mm deeper at p5" is the p5 of the depth change at high-tilt lines, not absolute contact.
The binding relayed contacts are the chain's (hub 2, link 1, link 2).

Not accepted as stated:

- **The instrument.** Every kit cell sits on a control of 60.55 (follow 0.8167, 23 "parts" losses in every cell,
  wr2a / wr2b). Kit numbers are deltas only.
- **Where the hardware price lands.** The kit's own hardware price at 55/45 is in-band: chain in-band falls 0.8258 ->
  0.7508. The member-3 bar (198 samples) reads 0.63 and the O20 boss 0.19-0.27, because R4 has to clear the line's
  maximum skin exit (79 mm) while the exit ranges 48-79 mm over poses. On a lead-quality chain at ~0.88 in-band, a
  ~150-sample bar at 0.63 costs ~6-8 in-band points.
- **The prior.** The 10.22 prior was read with the knee's b3 0.329. Lens A measured b3 0 at the CC lead's own J3 seat
  (66.9 / -10.7) at +9.8, with 38 contacts (L2 19, hub 2 14). This row's J3 is the champion seat wdir(77.25, -8.2),
  which is close to lens A's fit-bench cell (78, -8) where L2 has 2 contacts, so that burial need not transfer. The
  claim path must still assert the seat in M1.p.
- **The 'over' route.** On two kit lines it drove link 2 to in-band 0.04-0.05 (wpost.out, tilt 45 / 55 at taz
  -225 / -240). The row reports link 2's in-band.
- **Complexity.** It is 31.75 by tools/simplicity.py v2.2 --score, with the relay as the 4th counted joint (the
  kfree-armarc row reads 29.0 the same way). The proposer's 7.5 records a counted joint as a sprung passive rotation,
  which the user's 2026-10-17 rule ("a joint is a joint") rules out. It is still the lowest-complexity 4-joint relay in
  the round.

The judge's expectation: ideal ~11-15, hardware ~16-21 (the proposer said 13-16). Kill > 17.0.

kfree-o20pin-steered is the same hardware and the same file. Its Q2MAX, J3 window, BARMIN and PHI 50-66 are stop
variables, and under the 2026-10-16 rule stops are design variables chosen on envsel. It is merged in as a cell, and its
depth-first operating point is reported beside the PHI 75 one. The steering is legitimate only if the least-phi solve
honours the dowels; a clamp applied after solving would be a virtual stop.

### 1.3 Lens C, insertion station: the kinematics reproduce, the band is a centre-line reading

Kinematics (judge401/kin_static.py, the proposer's least_phi window, Bench(110,360) ws, 5-deg margin):

| relay | static ws | overhead |
|---|---|---|
| insertion axis raxis(8.75, -90), PHI 45 | 312 / 360 | 22 / 28 |
| distal axis raxis(2.74, -116.6), PHI 45 | 318 / 360 | 22 / 28 |
| distal axis, PHI 60 | 335 / 360 | 25 / 28 |
| no relay (PHI 0), J3 at 95 / -8.2 | 243 / 360 | 15 / 28 |

All of the proposers' counts reproduce. The insertion axis costs 6 poses against the near-long axis at the same PHI.

band.py reads the skin at ONE station (fr = 0.30). The band is 26 mm wide, about +-13 mm, which is 0.8 of a 16.25 mm
station step. judge401/band_axial2.py re-read the race and carriage at both edges, with the skin interpolated linearly
toward the neighbouring station:

| station, edge | race underside (fit at the centre) | carriage, cylinder | carriage, cone re-fit |
|---|---|---|---|
| s 0.30, centre | - | 7.1 / 11.0 / 13.9, ib 0.958 (reproduces) | same |
| s 0.30, proximal edge | skin rises up to 4.1 mm above it (p95 2.0; 36 / 198 poses past the 2 mm clearance) | 4.9 / 8.5 / 12.8, ib 0.976 | 8.0 / 11.6 / 15.9, ib 0.845 |
| s 0.30, distal edge | - | 11.1 / 13.9 / 16.2, ib 0.523 | (4 interpolation artefacts) |
| s 0.70, centre | - | 7.8 / 8.9 / 9.9, ib 1.0 (reproduces) | same |
| s 0.70, proximal edge | - | 6.1 / 7.3 / 8.2, ib 0.995 | 11.1 / 12.3 / 13.3, ib 0.995 |
| s 0.70, distal edge | - | 10.0 / 11.2 / 12.1, ib 1.0 | 7.6 / 8.8 / 9.7, ib 1.0 |

Gaps are carriage-to-skin p5 / p50 / p95 in mm.

The arm tapers at the deltoid insertion. A race underside contoured at one station touches the skin at its proximal
edge, and a cylindrical carriage floats out of band at its distal edge.

- Fixes: the underside is machined in 2D (per azimuth AND across the width), and the race and carriage become a
  surface of revolution about the axis. A cone still rotates about the axis, so it still guides.
- Even with those fixes, the proximal edge's pose-to-pose spread leaves the carriage at ~0.85 in-band there.
- The distal station holds ~1.0 across its width. That is the measured reason both stations keep a row.

The Bench(60,160) proxies (reach 0.838 / follow 1.00 insertion, 0.819 / 0.95 distal) carry no link metal and no in-band
term. The kfree ideal at reach 0.844 paid 4.66 contact points, so the lead-quality step 1 decides. The kit build may not
stand in for the bound (control 60.55).

### 1.4 Lens C: J4 hardware and determinacy (merging distal-vroller)

The friction arithmetic reproduces (worst case):

- iglidur shoe: mu 0.15-0.25 x ~5 N gib preload x R 0.058 m = 0.045-0.075 N m.
- Gravity about J4: ~70 g at ~60 mm, plus link 2's reaction, = 0.04-0.08 N m.
- Spring: a 2 N strip on R 0.058 gives 0.116 N m.
- Margin, plain shoe: down to -0.04 N m. The shoe can stall, which leaves an undetermined phi, and MVP1 must not have
  one.
- Margin, four shielded MR63ZZ (~0.004-0.016 N m): +0.02 to +0.03.

So the rolling V-wheel carriage becomes the J4 of both lens-C rows. The plain shoe is allowed only with a >= 3 N strip,
after a felt-torque check against R17. distal-vroller-cband-relay-4r is therefore not a separate morphology: it is the
J4 of the other two. Its complexity is the same 34.25 (sliding pair traded for rolling pairs; judge re-read with
simplicity.py --score).

### 1.5 Ruling on lens C's pre-registered strap kill

The plan's kill reads: "the strap from hub 3 to it is > 120 mm (its in-band < 0.85 kills the share)". At s 0.70 the
strap is ~220 mm, so the kill fires as worded. Its stated reason, in-band < 0.85, was measured false: the strap's
in-band is 0.99 on the q 1 fit. The planner left the ruling to the judge.

**Ruling:** the kill stands, converted into the measured quantity it was a proxy for, and pre-registered here before
any distal screening. Kill the distal row at step 0 if any of these holds:

- the strap's own in-band on the frozen PHI-0 fit is < 0.85;
- strap and band torso / other-skin losses on Bench(60,160) exceed 11 poses (8 ws + 3 clip measured);
- the strap deflects > 1 mm at the carriage under a 3 N relay load.

The insertion station (93 mm strap) does not trigger the original kill, and it ranks above the distal station on the
proposers' own proxies. The distal station keeps its own row because it has the round's highest kinematic ceiling
(335 / 360) and a band that stays in band across its width (section 1.3). The alignment auditor should see this ruling.

### 1.6 Rejection: kfree-slimpin-lowexit-relay-4r

R4 is a counted joint. The user's 2026-10-16 ~05:50 ruling is "hubs: Keep O20 only - the v5 O20 stack at every
joint", so an MR85ZZ boss is a slim hub and does not stand. Under O20 the 35/45 site is measured dead: kit 55.79, with
4 ws contacts and the boss's in-band 0.000.

The proposer recorded the price as the user's call, not the model's: the slim pin is 6.7 kit points better, and it
carries the best in-band arm metal (bar 0.758, boss 0.752). The question for the user: may a sprung relay pin use a
slim bearing (MR85ZZ pair in a Ø12 boss) instead of the O20 stack? If yes, this row is re-ideated next to pick 3.

## 2. Verdicts

| id | lens | verdict | reason |
|---|---|---|---|
| kneeless-steer-midbracket-relay-4r | A | **PICK 1** (merged row) | best-grounded knee-less 4-joint cell; honest bound ~15.7 (14.6-16.8) vs 15.4 pass |
| kneeless-steer-capshell-relay-4r | A | merged into pick 1 (s0 -55 neck cell) | same file, same patches; its 'deleted' 16.07 is the honest reading of its cell; seat-squareness sweep kept |
| kneeless-steer-ebracket-relay-4r | A | merged into pick 1 (s0 -80 control) | honest bracket proxy at PHI 50 is 15.75-17.99: the control that prices the knee on the verified shell |
| insertion-cband-relay-4r | C | **PICK 2** | strap 93 mm (kill not fired), 312/360 reproduced, proxy reach 0.838 / follow 1.00; band re-specified across its width |
| kfree-o20pin-highexit-relay-4r | B | **PICK 3** (merged row) | the lowest-complexity relay (no shell / knuckle / drive), conflict resolved; hardware price is in-band (bar 0.63) on a poor kit |
| kfree-o20pin-steered-relay-4r | B | merged into pick 3 (stop cell) | stops are design variables of the same hardware and file |
| distal-cband-sq95-relay-4r | C | **PICK 4** | highest kinematic ceiling (335/360, 25/28 overhead, reproduced), band in band across its width; strap kill re-registered |
| distal-vroller-cband-relay-4r | C | merged (J4 hardware of picks 2 and 4) | the rolling J4 is the determinacy fix for both C stations, not a separate morphology |
| kfree-slimpin-lowexit-relay-4r | B | **REJECTED** | violates "Keep O20 only" at R4 (a counted joint); under O20 the site is dead (kit 55.79); the user's call |

## 3. Ranking

Score = (expected gap reduction vs the champion 75.94) x (confidence) x (buildability). All four survivors have 0 passive
translations, so buildability ranks the guide hardware.

| rank | id | judge expected claim | reduction vs 75.94 | confidence | buildability | product |
|---|---|---|---|---|---|---|
| 1 | kneeless-steer-midbracket-relay-4r | ~15.8 (14.7-16.9) | 60.1 | 0.75 (validated driver, measured cells) | 0.9 (phi40's verified shell / carriage class; K slipper drive) | 40.6 |
| 2 | insertion-cband-relay-4r | ~15 (13-17) | 60.9 | 0.45 (proxies only; taper found) | 0.85 (machined cone band + MR63ZZ V-wheels) | 23.3 |
| 3 | kfree-o20pin-highexit-relay-4r | ~18 (16-21) | 57.9 | 0.40 (kit deltas; in-band price) | 1.0 (O20 bearing pairs only) | 23.2 |
| 4 | distal-cband-sq95-relay-4r | ~15.5 (13-18) | 60.4 | 0.35 (proxies; strap gate first) | 0.8 (220 mm strap, band, wheels) | 16.9 |

Expected order of news: pick 1 decides the track's question (a knee-less 4-joint at <= 15.4) within ~90 min. Picks 2
and 4 carry the round's ceiling: only lens C's kinematics reach 0.93, and only a lead-quality step 1 can tell whether
the link metal keeps it. Pick 3 is the simplicity bet: a Pareto pass (<= 15.4) at the lowest complexity of any relay
would beat pick 1 on the second objective.

## 4. Gates carried into screening (pre-registered here)

- **Pick 1:** step 0 on the bracket-honest proxy; kill if every (s0, PHI, seat, stops) cell is > 15.4. Then pass
  <= 15.4; kill > 16.28 or held >= 20.38. The +1.5 deg shell-end and stop-partner cliffs are gates. The zero-return
  margin is reported per relayed pose.
- **Pick 2:** ideal bound on the lead-quality chain (kfree lfrozen with the J3 re-aim asserted); kill > 14.0.
  Hardware: race and carriage sampled across the full width, with a 2D-contoured underside. Kill > 17.0.
- **Pick 3:** step 0 on the lead-quality chain, J3 seat asserted; kill if the ideal is > 14.0 or > 3 relayed taken
  poses come within 2 mm. Hardware kill > 17.0. Report link 2's in-band and the az 50-55 cliff partners.
- **Pick 4:** the strap gate (section 1.5) first, then step 1 with kill > 14.0, then hardware with kill > 17.0.

Common to all four:

- Select on envsel / envh only.
- The near-touch objective.
- Every face of every part sampled.
- Flood on the envelope grid with the relay state, static and connected.
- th margin >= 5 per pose.
- Reports: T5 depth vs the lead's 20.24 mm, the 2 mm reading, overhead /28 and /71, the shoulder-slip price (~6.4 /
  6.9 mm at R10 4 mm, 13-31 N vs the 5 N cap, liner compliance stated).
- viz js + test.mjs + thumbs.mjs before a row is called screened.
- Local CPU only: nice -n 10, OMP_NUM_THREADS=1, <= 2 processes per agent.

## 5. What happens next

The loop continues: screen + verify of these four, then the alignment audit (the strap ruling and the bracket-honest
proxy are both audit items), then close.

New knowledge for the next planner:

1. Knee-side samples pad any knee-less reading that keeps them. Every knee-less row must drop the boss, pad and knee
   samples and keep only the metal it builds.
2. A rigid band 26 mm wide at the deltoid insertion meets a ~3 mm / 13 mm taper. Single-station ring models
   over-read in-band there.
3. The relay axis line moves relayed chain burials even where the kinematics are flat. It is a metal variable,
   not a free choice.
4. Next-round idea, not ideated here: lens B's pin relay at 55/45 on the KNUCKLE chain, i.e. phi40's chain with the
   shell replaced by an O20 pin. It combines the knee-chain metal quality with the simplest guide.

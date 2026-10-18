# Round 106 (J6, track jump) ideation: judge and red team (2026-10-18 ~13:25 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75) at
low complexity. The plan is docs/concepts/ROUNDS.md "Round 106 plan" (95fd699).

**Lead to beat:** conecut-knee-knuckle-3r, verified 18.28 (score 93.35), frozen exact Bench(110,360), held 22.38,
cx 18.5, 3 joints. **Best 4-joint verified:** freek-oracle-route-knuckle-4r, frozen 16.20 / polished 15.40, held 21.89 /
20.50, cx 33.25 (WATCH; not a lead under the user's ruling).

**Candidates:** six came in, all built on proxtrack-relay-knuckle-4r's relay.

- Lens A (two-sided relay): twoside-proxtrack-relay-4r, offset-shortcar-relay-4r, twoside-longstroke-relay-4r.
- Lens B (cheapest base under the relay): proxtrack-desmo-relay-4r, leanrelay-knuckle-4r, leanrelay-desmo-relay-4r.

Every joint maps to a real part and all six have 0 passive translations.

**Outcome: ONE pick** (section 4), re-specified by the judge. Two candidates are dead by the round's own
pre-registered clause, three are dominated after the base moved, and one is merged.

## 0. The base moved under the round

The planner wrote the round at 12:30 on proxtrack's screened gate 14.40. At 12:53 the buildability verifier refuted it
as modelled (18c4b46; row `v_gap` 17.46, `v_verdict` "REFUTED as modelled"). The rigid local bump lifts the pin-a boss
1.76-5.69 mm, but the knee link riding on that boss only 0-3.72 mm, so the boss sits 5.05-5.08 mm inside the knee eye
at all 184 fit poses. The minimal buildable stack (knee eye lifted over the boss, 60-deg ramp) reads:

- frozen exact gate **17.46** (plain 14.40, near1 18.06), chain-only ib14 0.8962 -> 0.8656;
- held gate **21.46**.

This is a buildability correction of the metal, not a bench or metric change. The plan itself says: "If the verifier
moves proxtrack's number, re-base the gates on the verified reading". Every candidate's expected gap was computed from
14.40 (or 14.02 plain) and its "hardware price" from +1.19. **Re-based, the price at the claim hardware is +4.25
(17.46 - 13.21 ideal).** The planner's lens-A step-0 line (two-sided ideal + price <= 13.75) then needs an ideal
<= 9.50; the best candidate ideal is 11.63.

## 1. Red-team checks made by the judge

Judge scripts and outputs (local, nice 10-15, OMP_NUM_THREADS=1, at most 2 processes, proxtrack's model and the
verifier's harness imported read-only, flood caches redirected to the scratch dir):
`/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge106/`
(shortcar_stack.py / .json, coil_lug.py / .json, coil_lug_twoside.py / .json, ds_boss.py / .json, ds_stack.py / .json).

### 1.1 The buildable stack at a short carriage (frozen exact Bench(110,360), one prepare, PHI 35 one-sided)

| carriage | pre-arc | bump as claimed (gate) | buildable stack (gate) | boss lift max | stack cost |
|---|---|---|---|---|---|
| 24 mm (proxtrack claim, verifier) | 10.41 | 14.40 | 17.46 | 5.69 | +3.06 |
| 14 mm (judge) | 6.45 floor | **14.20** | **16.92** | 4.89 | +2.72 |
| 16 mm (judge) | 7.17 floor | - | **16.92** | 4.89 | - |

- The short carriage is worth -0.20 as claimed (the proposers' -0.23 reproduces) and -0.54 buildable.
- At <= 16 mm the boss lift is set by the shell window (R_t + 1), not the carriage footprint: carw 12 / 14 / 16 and
  h_c 1.2 / 1.7 all give 4.89 (`ds_boss.json`). So h_c and carriage length buy nothing more on the stack.
- **Every candidate's expected gap moves up by ~2.7-3.1.** The two-sided ideal 12.25 + buildable short-carriage price
  3.71 = ~15.96 (longstroke 11.63 + 3.71 = ~15.34), before the 18 mm shell (below) and the coils. None reaches 13.75.

### 1.2 Where the stack cost comes from: the track station

The boss lift is the cost driver (the verifier's 35 knee points must rise by it). It falls fast as the track moves
proximal, because the boss (s -124.8..-93.4) leaves the shell window (`ds_boss.json`, fit bench, short carriage):

| ds (mm proximal of the pad) | 19.5 (claim) | 22 | 24 | 26 | 28 | 31 |
|---|---|---|---|---|---|---|
| boss lift max (mm) | 4.89 | 4.98 | 4.62 | 4.06 | 2.84 | 1.13 |
| R_t (shell top) | 79.93 | 80.20 | 80.31 | 80.42 | 80.55 | 80.60 |
| E strap lift max | 6.22 | 6.21 | 6.16 | 6.11 | 6.19 | 5.93 |

proxtrack's sweep chose ds 19.54 under a model that charged nothing for the stack, so the station was selected by a
metal error. DS_STACK_PLACEHOLDER

### 1.3 Where the constant-force coil can live (fit bench, 184 poses, claim bump applied)

A real CF strip for ~0.8 N over a 49-55 mm stroke coils to ~7-8 OD x 8 wide (the verifier's sizing). Chain metal
within 1 mm of the coil = jam / extra bump (`coil_lug.json`, `coil_lug_twoside.json`):

| coil placement | poses hit / 184 | extra lift needed |
|---|---|---|
| arm-fixed beyond the zero end (proxtrack's, at th0 - 14; and at th0 - 10 / th0 - 5.5) | 0 | 0 |
| carriage proximal lug at az th0 - 12 .. th0 + 2 (on the shell or beyond its edge) | 0 | 0 |
| lug at th0 + 4 (beyond an 18 mm shell edge) | 24 | E strap +9.31 mm |
| lug at th0 + 4.5 (offset-shortcar's spec: centred on the offset carriage) | 30 (beyond edge) / 6 (on shell) | E strap +7.85 / +9.62 mm |
| lug at th0 + 6 | 110-119 | E strap +9.5 / +12.56 mm |

- **offset-shortcar's coil, as specified, sits under the E strap.** The proposer moved it onto the carriage lug
  because "the shortened posterior end leaves no room". The arm-fixed place beyond the moved zero end (th0 - 5.5) is
  clean of chain metal. Its skin margin at pose 466 is about 0 mm if the coil's bottom sits at R_t, so it must sit
  >= 1 mm above the shell top or on the lug at the carriage's POSTERIOR corner (az <= th0 + 2).
- **twoside's two coils** were both placed at "the proximal side lug (s0 + 8..14)" at rest: the same footprint. One of
  them must move. Only posterior azimuths (<= th0 + 2) are clean.

### 1.4 leanrelay's spring does not exist at that size

An extension spring of OD <= 1.2 mm with >= 0.83 N preload over a 49 mm stroke (302 stainless, G 69 GPa; Shigley's
initial-tension limit; working stress 0.45 UTS; Wahl factor):

| wire d (mm) | index C | max initial tension (N) | coils to survive 49 mm | close-wound body |
|---|---|---|---|---|
| 0.20 | 5.0 | 0.52 (< 0.83: no preload) | - | - |
| 0.22 | 4.5 | 0.74 (< 0.83) | - | - |
| 0.25 | 3.8 | 1.21 | 529 | **132 mm** |
| 0.30 | 3.0 | 2.39 | 717 | **215 mm** |

The lean shell arc is 44.3 deg x 79.9 mm = 62 mm. A spring that carries the preload is at least 2x the whole arc before
any stroke, and its rate (~0.05 N/mm) is 2.5x the proposed 0.02. **No such part exists at that size.** The buildable
spring is the CF coil arm-fixed beyond the zero end (1.3), which removes the "nothing taller than 1.4 mm" claim. It does
not move the gate (the verifier: >= 16.7 mm from every chain point), but it adds a drum or arbor (+0.25-0.5 cx), so the
row lands at ~51 cx against the lens's 50.5 line.

### 1.5 twoside: the round's pre-registered kill clause triggers on the proposer's own step 0

The lens-A kill was pre-registered at 12:30: "kill = gate > 14.40 (no gain over its parent) **or any new folded-side
contact**". The proposer's own step-0 data (`step0_metal.json`, `step0_envsel.json`, re-read here):

- claim bench: 129 (-75, 60, 120) relays to -1.4 deg and puts L2 2.83 mm into the skin; 207 (0, 135, -45) at -7.1 deg
  puts the K crank 8.88 mm in; 263 at -9.4 is a third. No useful cap avoids 129 (the - side takes sit at -6.8..-9.1).
- envsel (the selection bench) shows the same: 260 at -4.3 (-3.13 mm) and 447 at -1.9 (-8.77 mm).
- The planner's hypothesis is refuted too: 262 / 206 / 182 keep hub 2 in the deltoid at either sign (-9.62 / -5.52 /
  -0.13), so the two-sided relay does not remove the folded-side contacts it was meant to remove.
- The "clean" shell window is clean by hundredths: the -17.0 end clears (75, 60, -135) by 0.01 mm, +46.0 clears the
  elevation-0 alias by 0.22 mm, and proxtrack's own posterior end (-10.41) clears 129 by 0.37 mm
  (`step0_shell_fine.json`). Widening the shell to 18 mm raises R_t by 0.30 mm (80.23 vs 79.93), ~+0.27 gap at
  proxtrack's 0.9 per mm.
- Three of the six envsel - side takes are under 1.5 mm (255 1.02, 258 1.43, 261 1.24), and two of the five claim-bench
  ones are under 2 mm (117 1.53, 183 0.08).

Waiving a pre-registered kill after seeing the data is the auditor's and the lead's call, not the judge's. Re-based
(1.1) the best two-sided config reads ~15.3-16.0 buildable before the shell and coil costs, which would not beat
freek's polished 15.40 at +26.5 cx.

### 1.6 The desmo base under the relay: dominated

The proposers' own per-pose arithmetic (exact; clip poses are never relayed) puts proxtrack-desmo past both of its
pre-registered kill lines before the stack: bench gate 15.03 / 15.25 (> 15.0) and held 19.10 / 19.33 (> 18.51 + 0.5).
Add the buildable stack (+2.7-3.1) and it reads ~17.8-18.3, the 3-joint lead's number at +31.75 cx. leanrelay-desmo is
the same base plus 1.4 above (~17.7-18.2 at ~48.75 cx). The desmo-window drive is on the round's do-not-rescreen list.
Its cx-floor point needs no run: the per-pose transplant on file gives it.

## 2. Verdicts

| candidate | verdict | reason |
|---|---|---|
| twoside-proxtrack-relay-4r | **REJECTED (dead at step 0)** | pre-registered kill: new folded-side contacts 129 / 207 (and 260 / 447 on envsel) that no useful cap avoids; hypothesis refuted (262 / 206 are hub 2); re-based ~15.96 + 18 mm shell + coils > freek 15.40 at +26.5 cx |
| twoside-longstroke-relay-4r | **MERGED into twoside, rejected with it** | same model file, hardware and cx 59.75; PHI 38.5 is a sweep value; adds a 4th new contact (233, hub 2); anterior end 0-0.5 deg from the alias |
| offset-shortcar-relay-4r | **PICK (re-specified)** | the only candidate that keeps every pre-registered clause; judge fixes: buildable stack in every reading, the coil off the E strap (1.3), the track station re-selected under the stack (1.2) |
| leanrelay-knuckle-4r | **REJECTED (spring not a real part; dominated)** | 1.4: the OD 1.2 extension spring cannot exist at that preload / stroke; with the real CF coil it is proxtrack's metal at ~51 cx, i.e. ~17.4 buildable, dominated by freek (15.40 / 16.20 at 33.25 cx) on both axes; carry its part merges later |
| proxtrack-desmo-relay-4r | **REJECTED (dominated)** | past both pre-registered kill lines by its own arithmetic; ~17.8-18.3 buildable = the 3-joint lead at +31.75 cx; desmo-window on the dead list |
| leanrelay-desmo-relay-4r | **MERGED with proxtrack-desmo, rejected** | both parents' risks; ~17.7-18.2 at ~48.75; its two-sided route depends on lens A, which is dead |

## 3. Ranking

Score = expected gap reduction vs the lead (18.28) x confidence x buildability (all 0 passive translations), against
the 4-joint bar (freek 15.40 polished / 16.20 frozen):

| rank | candidate | expected buildable gate | gain vs lead | confidence | note |
|---|---|---|---|---|---|
| 1 | offset-shortcar-relay-4r (+ station) | RANK1_PLACEHOLDER | | medium | one-sided, no new contact, cx 52.5 |
| - | twoside (merged) | ~15.3-16.3 | 2.0-3.0 | killed by pre-registration | cx 59.75 |
| - | leanrelay-knuckle-4r | ~17.4 | 0.9 | spring fails | ~51 cx, dominated |
| - | desmo pair | ~17.7-18.3 | ~0-0.5 | high (dominated) | 48.75-50.25 cx |

## 4. Picks (lead notes)

PICKS_PLACEHOLDER

## 5. What happens next

NEXT_PLACEHOLDER

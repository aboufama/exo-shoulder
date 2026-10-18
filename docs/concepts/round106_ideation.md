# Round 106 (J6, track jump) ideation: judge and red team (2026-10-18 ~13:30 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75) at
low complexity. The plan is docs/concepts/ROUNDS.md "Round 106 plan" (95fd699).

**Lead to beat:** conecut-knee-knuckle-3r, verified 18.28 (score 93.35), frozen exact Bench(110,360), held 22.38,
cx 18.5, 3 joints.

**Best 4-joint verified:** freek-oracle-route-knuckle-4r, frozen 16.20 / polished 15.40, held 21.89 / 20.50, cx 33.25.
It is on WATCH and is not a lead under the user's ruling.

**Candidates:** six came in, all built on proxtrack-relay-knuckle-4r's relay.

- Lens A (two-sided relay): twoside-proxtrack-relay-4r, offset-shortcar-relay-4r, twoside-longstroke-relay-4r.
- Lens B (cheapest base under the relay): proxtrack-desmo-relay-4r, leanrelay-knuckle-4r, leanrelay-desmo-relay-4r.

Every joint maps to a real part (the cuff knee pins are outside the count). All six have 0 passive translations and 4
active joints.

**Outcome: ONE pick**, offset-shortcar-relay-4r, re-specified by the judge (section 4).

- leanrelay-knuckle-4r's part merges are merged into it.
- The two two-sided rows are dead by the round's own pre-registered clause.
- The two desmo-base rows are dominated.

**The judge's main finding.** The relay's buildable price is set by the track STATION, not by the contacts the round
targeted:

- At ds 31-34 mm proximal of the pad the pin-a boss leaves the shell window.
- The verifier's +3.06 stack cost then falls to ~0.
- The buildable gate falls from 16.92 to 14.26.

These are diagnostic claim-bench readings (section 1.2).

## 0. The base moved under the round

The planner wrote the round at 12:30 on proxtrack's screened gate 14.40. At 12:53 the buildability verifier refuted it
as modelled (18c4b46; row `v_gap` 17.46, `v_verdict` "REFUTED as modelled").

What is wrong with the claimed metal:

- The rigid local bump lifts the pin-a boss 1.76-5.69 mm.
- The knee link riding on that boss rises only 0-3.72 mm.
- So the boss sits 5.05-5.08 mm inside the knee eye at all 184 fit poses.

The minimal buildable stack (knee eye lifted over the boss, 60-deg ramp) reads:

- frozen exact gate **17.46** (plain 14.40, near1 18.06), chain-only ib14 0.8962 -> 0.8656;
- held gate **21.46**.

This corrects the metal; it is not a bench or metric change.

The plan says: "If the verifier moves proxtrack's number, re-base the gates on the verified reading". Every candidate
computed its expected gap from 14.40 (or 14.02 plain), and its hardware price from +1.19.

- **Re-based, the price of the claim hardware is +4.25** (17.46 - 13.21 ideal).
- The lens-A step-0 line (two-sided ideal + price <= 13.75) then needs an ideal <= 9.50. The best candidate ideal is
  11.63.

## 1. Red-team checks made by the judge

The judge's scripts and outputs live in
`/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge106/`:
shortcar_stack, ds_stack, ds_stack2, ds_boss, coil_lug and coil_lug_twoside, each as a `.py` / `.json` pair.

How they were run:

- Locally, nice 10-15, OMP_NUM_THREADS=1, at most 2 processes.
- proxtrack's model and the verifier's harness (`stackfix_amounts`) were imported read-only.
- The flood caches were redirected to the scratch dir.
- Each frozen exact Bench(110,360) table below comes from one prepare (the lead fit on Bench(60,160) fast at phi 0,
  ideal relay 13.21 reproduced), re-recorded per hardware config.
- All configs are one-sided at PHI 35, with the pre-arc at its floor and no rest offset.

### 1.1 The buildable stack at a short carriage

| carriage | pre-arc | bump as claimed (gate) | buildable stack (gate) | boss lift max | stack cost |
|---|---|---|---|---|---|
| 24 mm (proxtrack claim, verifier) | 10.41 | 14.40 | 17.46 | 5.69 | +3.06 |
| 14 mm (judge) | 6.45 floor | **14.20** | **16.92** | 4.89 | +2.72 |
| 16 mm (judge) | 7.17 floor | - | **16.92** | 4.89 | - |

- The short carriage is worth -0.20 as claimed (the proposers' -0.23 reproduces) and -0.54 with the buildable stack.
- At <= 16 mm the boss lift is set by the shell window (R_t + 1), not by the carriage footprint. carw 12 / 14 / 16 and
  h_c 1.2 / 1.7 all give 4.89 (`ds_boss.json`), so h_c and carriage length buy nothing more on the stack.
- At the claim station, every candidate's expected gap moves up by ~2.7-3.1.
  - The two-sided ideal 12.25 plus the short-carriage buildable price 3.71 gives ~15.96.
  - The longstroke ideal 11.63 gives ~15.34.
  - Both are before the 18 mm shell and the coils are priced.

### 1.2 Where the stack cost comes from: the track station

The boss lift drives the cost: the verifier's 30-36 knee points must rise by it. It falls as the track moves proximal,
because the boss (s -124.8..-93.4) leaves the shell window (`ds_boss.json`, fit bench, 14 mm carriage):

| ds (mm proximal of the pad) | 19.5 (claim) | 22 | 24 | 26 | 28 | 31 | 34 |
|---|---|---|---|---|---|---|---|
| boss lift max (mm) | 4.89 | 4.98 | 4.62 | 4.06 | 2.84 | 1.13 | 0.00 |
| R_t (shell top) | 79.93 | 80.20 | 80.31 | 80.42 | 80.55 | 80.60 | - |

**Frozen exact Bench(110,360), 14 mm carriage, buildable stack** (`shortcar_stack.json`, `ds_stack.json`,
`ds_stack2.json`). These are DIAGNOSTIC readings of hardware variants on the claim bench (P1 class): they set no
config.

| ds | 19.5 | 25 | 28 | 31 | 34 |
|---|---|---|---|---|---|
| buildable gate (chain-only) | 16.92 | 16.60 | 15.09 | **14.26** | **14.30** |
| chain-only ib14 | 0.8710 | 0.8714 | 0.8865 | 0.8948 | 0.8944 |
| bump as claimed (gate) | 14.20 | - | 14.14 | DS31BASE | - |
| plain (pooled) | 14.24 | 13.87 | 13.74 | 13.74 | 13.74 |
| near1 | 17.90 | 18.04 | 17.91 | 17.91 | 17.91 |
| ws taken / contacts / jams | 285 / 13 / 5 | 286 / 13 / 0 | 286 / 13 / 0 | 286 / 13 / 0 | 286 / 13 / 0 |
| 466 (shell posterior end) | -3.33 | -3.38 | -3.22 | -3.26 | -3.17 |

What the station readings show:

- **The stack cost is a station artefact.** proxtrack's sweep chose ds 19.54 under a model that charged nothing for the
  pin-a stack, so the station was selected on a metal error.
- At ds 31-34 the buildable gate (14.26-14.30) is back at the claim's own unbuildable 14.40.
- The 5 boss near-jams at the shell top vanish (pose 396 becomes a take).
- The contact set is proxtrack's 13, with no new pose. The relay pattern stays 33 relayed, 24 taken, 9 contacts.
- The plateau from 31 to 34 says the rest of the price (~1.05 over the 13.21 ideal) is the E-strap bump and pose 466.
- Pose 466 is the one hardware contact the offset was written for: the shell's posterior end at -6.45 deg sits ~3.2 mm
  in the skin there at every station.
- Arithmetic: ds 31 (14.26) plus 466 made a take (~-0.52: one take +0.28, one contact -0.25) gives **~13.74, the 95
  line**. That holds only if the 4.5-deg offset clears 466 at that station and its moved footprint costs nothing.
  Both are unmeasured.

### 1.3 Where the constant-force coil can live (fit bench, 184 poses, claim bump applied)

A real CF strip for ~0.8 N over a 49-55 mm stroke coils to ~7-8 OD x 8 wide (the verifier's sizing). Chain metal within
1 mm of the coil counts as a jam or needs extra bump (`coil_lug.json`, `coil_lug_twoside.json`):

| coil placement | poses hit / 184 | extra lift needed |
|---|---|---|
| arm-fixed beyond the zero end (proxtrack's, at th0 - 14; and at th0 - 10 / th0 - 5.5) | 0 | 0 |
| carriage proximal lug at az th0 - 12 .. th0 + 2 (on the shell or beyond its edge) | 0 | 0 |
| lug at th0 + 4 (beyond an 18 mm shell edge) | 24 | E strap +9.31 mm |
| lug at th0 + 4.5 (offset-shortcar's spec: centred on the offset carriage) | 30 (beyond edge) / 6 (on shell) | E strap +7.85 / +9.62 mm |
| lug at th0 + 6 | 110-119 | E strap +9.5 / +12.56 mm |

- **offset-shortcar's coil, as specified, sits under the E strap.** The proposer moved it onto the carriage lug
  because "the shortened posterior end leaves no room".
- The arm-fixed place beyond the moved zero end (th0 - 5.5) is clean of chain metal.
- Its skin margin at pose 466 is about 0 mm if the coil's underside sits at R_t. So the coil must sit >= 1 mm above the
  shell top, or ride a lug on the carriage's POSTERIOR corner (az <= th0 + 2).
- **twoside's two coils** were both placed on "the proximal side lug (s0 + 8..14)" at rest, which is the same footprint.
  One of them must move, and only posterior azimuths (<= th0 + 2) are clean.

### 1.4 leanrelay's spring does not exist at that size

The question: can an extension spring of OD <= 1.2 mm give >= 0.83 N preload over a 49 mm stroke? Assumptions: 302
stainless, G 69 GPa, Shigley's initial-tension limit, working stress 0.45 UTS, Wahl factor.

| wire d (mm) | index C | max initial tension (N) | coils to survive 49 mm | close-wound body |
|---|---|---|---|---|
| 0.20 | 5.0 | 0.52 (< 0.83: no preload) | - | - |
| 0.22 | 4.5 | 0.74 (< 0.83) | - | - |
| 0.25 | 3.8 | 1.21 | 529 | **132 mm** |
| 0.30 | 3.0 | 2.39 | 717 | **215 mm** |

- The lean shell arc is 44.3 deg x 79.9 mm = 62 mm.
- A spring that carries the preload is at least 2x the whole arc before any stroke.
- Its rate (~0.05 N/mm) is 2.5x the proposed 0.02.
- **No such part exists at that size.**

The buildable spring is the CF coil arm-fixed beyond the zero end (1.3), which removes the "nothing taller than 1.4 mm"
claim. It costs no gate: the verifier measured >= 16.7 mm to every chain point, and the judge found 0 / 184 hits at
th0 - 10. It does add a drum or arbor (+0.25-0.5 cx).

lean's real content is the part merges (BOTTOM-integral carriage / bracket / T-flange, slot-end PHI stop, one dowel).
These carry into the pick as a reported hardware flag (merged).

### 1.5 twoside: the round's pre-registered kill clause triggers on the proposer's own step 0

The lens-A kill was pre-registered at 12:30: "kill = gate > 14.40 (no gain over its parent) **or any new folded-side
contact**". The judge re-read the proposer's own step-0 data (`step0_metal.json`, `step0_envsel.json`) and proxtrack's
dump.

**New contacts on the claim bench.**

- 129 (-75, 60, 120) is lost in proxtrack. It relays to -1.4 deg and puts L2 2.83 mm into the skin.
- 207 (0, 135, -45) is also lost in proxtrack. At -7.1 deg it puts the K crank 8.88 mm in.
- 263, at -9.4 deg, is a third.
- No useful cap avoids 129: the - side takes sit at -6.8..-9.1 deg.

**The same on envsel** (the selection bench): 260 at -4.3 deg (-3.13 mm) and 447 at -1.9 deg (-8.77 mm).

**The planner's hypothesis is refuted.** 262 / 206 / 182 keep hub 2 in the deltoid at either sign (-9.62 / -5.52 /
-0.13 mm). The two-sided relay does not remove the folded-side contacts it was meant to remove.

**The "clean" shell window is clean by hundredths of a mm** (`step0_shell_fine.json`):

- the -17.0 end clears (75, 60, -135) by 0.01 mm;
- the +46.0 end clears the elevation-0 alias by 0.22 mm;
- proxtrack's own posterior end (-10.41) clears 129 by 0.37 mm.

**Other costs.**

- Widening the shell to 18 mm raises R_t by 0.30 mm (80.23 vs 79.93), ~+0.27 gap at proxtrack's 0.9 per mm.
- Three of the six envsel - side takes are under 1.5 mm (255 1.02, 258 1.43, 261 1.24).
- Two of the five claim-bench - side takes are under 2 mm (117 1.53, 183 0.08).
- The new contacts are chain metal (L2, K crank), so the station lever (1.2) does not remove them.

Waiving a pre-registered kill after seeing the data is the auditor's and the lead's call, not the judge's. The lead
should know the stake: at the station found in 1.2, the arithmetic for the two-sided rows reads ~12.95-13.6, below the
pick (section 3). That number buys its gap with contacts up to 8.88 mm deep, and the clause was written to stop exactly
that. If the lead and the auditor waive the clause, twoside-longstroke at the pick's envsel station is the next row to
run, and the proposer's model spec stands.

### 1.6 The desmo base under the relay: dominated by its own pre-registered held line

The proposers' own per-pose arithmetic is exact, since clip poses are never relayed. It puts proxtrack-desmo past both
of its pre-registered kill lines:

- bench gate 15.03 / 15.25 (> 15.0);
- held 19.10 / 19.33, which is worse than proxtrack by +0.59 / +0.82 (the kill is > 0.5).

The desmo's in-band price is a constant added to every relay config, so the held kill holds at any station. At ds 31
the pair would read ~14.9-15.2 at 48.75-50.25 cx.

- That is 0.6-0.9 worse than the pick for 2.25-3.75 cx less.
- The desmo-window drive is on the round's do-not-rescreen list.
- The cx-floor point needs no run: the per-pose transplant on file gives it.

## 2. Verdicts

| candidate | verdict | reason |
|---|---|---|
| twoside-proxtrack-relay-4r | **REJECTED (dead at step 0)** | pre-registered kill: new folded-side contacts 129 / 207 (and 260 / 447 on envsel) that no useful cap avoids, chain metal so no station removes them; its hypothesis is refuted (262 / 206 are hub 2); re-based ~15.96 at the claim station; cx 59.75 |
| twoside-longstroke-relay-4r | **MERGED into twoside and rejected with it** | same model file, hardware and cx 59.75 (PHI 38.5 is a sweep value); adds a 4th new contact (233, hub 2); its anterior end sits 0-0.5 deg from the alias (0.22 mm) |
| offset-shortcar-relay-4r | **PICK (re-specified)** | the only candidate that keeps every pre-registered clause. Judge changes: the buildable stack in every reading (1.1), the track station as a design variable (1.2), the coil off the E strap (1.3), lean's part merges as a flag (1.4) |
| leanrelay-knuckle-4r | **MERGED into the pick (hardware flag); rejected as a row** | its OD 1.2 extension spring cannot exist at that preload and stroke (1.4). With the real CF coil it is the pick's metal with fewer parts (~51 vs 52.5 cx); its h_c 1.4 is worth -0.08 fast and 0 on the stack (1.1) |
| proxtrack-desmo-relay-4r | **REJECTED (dominated)** | past both of its pre-registered kill lines by its own arithmetic, and the held kill (> +0.5 vs the relay) holds at any station; the desmo-window drive is on the dead list |
| leanrelay-desmo-relay-4r | **MERGED with proxtrack-desmo and rejected** | carries both parents' risks; its two-sided route depends on lens A, which is dead; ~14.9-15.2 at ~48.75 cx even at the best station |

## 3. Ranking

Score = expected gap reduction vs the lead (18.28) x confidence x buildability. All candidates have 0 passive
translations. The 4-joint bar is freek's 15.40 polished / 16.20 frozen.

| rank | candidate | expected buildable gate | gain vs lead | confidence | cx |
|---|---|---|---|---|---|
| 1 | offset-shortcar-relay-4r (station + offset + coil + lean flag) | **13.7-14.6** (95 needs <= 13.75) | 3.7-4.6 | medium: the station is measured, but the offset at the new station is not, and 466 / ds were read on the claim bench (P1) | 52.5 (~51 with the lean flag) |
| - | twoside (merged) | ~12.95-13.6 at ds 31 by arithmetic (ideal 11.63 / 12.25 + station price 1.05 + 18 mm shell 0.27; coils and the longer arc's bump unpriced), but killed | - | pre-registered kill (207 puts the K crank 8.88 mm into the skin) | 59.75 |
| - | desmo pair | ~14.9-15.2 at ds 31 | - | killed by its own held line | 48.75-50.25 |

## 4. Picks (lead notes)

1. **offset-shortcar-relay-4r**: proxtrack's one-sided relay re-priced under the buildable pin-a stack. It merges
   leanrelay-knuckle-4r's part merges. The first thing to test is the shell's posterior end at pose-466-type
   posterior internal-rotation skin ON ENVSEL, at the envsel-chosen station. If envsel shows no binder there, the 4.5
   deg offset cannot be pre-registered, and the row is the station result alone (~14.3).
   - **Every reading uses the buildable stack** (the verifier's `stackfix_amounts`, imported read-only).
   - **Controls** on the same prepare:
     - carw 24 / pre 10.41 / ds 19.538 -> 17.46;
     - carw 14 / pre floor / ds 19.538 -> 16.92.
   - **Select on envsel exact only:** ds (19.5-36), delta (0-7), carw (12-16), PHI (32-35), the coil placement and the
     lean flag. The judge's claim-bench station readings are diagnostic and set nothing.
   - **Coil:** arm-fixed beyond the moved zero end with its underside >= 1 mm above the shell top, or on the
     carriage's posterior lug (az <= th0 + 2). Never centred on the offset carriage (E strap +7.85 / +9.62 mm).
   - **Claim:** ONE frozen exact Bench(110,360) wear at the envsel pick, plus held, with T5 dumps.
   - **Pre-registered lines:**
     - **95 pass:** chain-only buildable gate <= 13.75 with no new contact vs proxtrack's 13, and held paired better
       than proxtrack's buildable held 21.46.
     - **4-joint pass:** <= 15.40 with held <= 20.50 (beats freek).
     - **Kill:** > 16.92 (the station, offset and coil buy nothing over the short-carriage control), any new
       folded-side contact, or held paired worse than 21.46.
   - **Report:** plain, near1, 2-mm, Proposal A / B, the flood, the min th margin, R17, contacts by cause, cx with and
     without the lean flag, and the motion preview.

## 5. What happens next

- The pick takes lens A's slot: model ~45 min, envsel selection ~40 min, one claim + held wear ~25 min at load 13-20.
- Lens B's slot is free. Two uses are worth it:
  - the posteromedial J1 seat (the lead's open take-bound cell);
  - an independent re-wear of the judge's station reading, to confirm ds 31 at 14.26 is not a judge artefact. This is
    the verifier's "lower boss" design answer, measured.
- **FINDING for FINDINGS.md** (the lead writes it):
  - The 4-joint relay's buildable price is a station effect. At ds 19.5 the pin-a boss sits inside the shell window
    and costs +2.7-3.1 (verifier + judge). At ds >= 31 it leaves the window: the cost is ~0 and the gate is 14.26-14.30
    (diagnostic).
  - Searches that do not model a part's stack select the station on a metal error.
- The user's blocker (12:50) said "no 4-joint design reaches 95 either", citing proxtrack at 94.90 unverified. The
  relay's buildable diagnostic now reads 94.81 (14.26) at ds 31, with ~13.74 (95.0) possible if pose 466 clears. The
  lead decides whether that goes to the user after the pick's claim and its verifier, not before.
- Not re-proposed (closed here): two-sided relays (new folded-side chain contacts), the OD <= 1.2 extension spring, coils
  at az >= th0 + 4 under the E strap, and the desmo base under any relay (its held line).

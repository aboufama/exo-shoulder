# phi40-thinstack-relay-4r: a longer one-sided over-pass relay (PHI 40) on the thin stack

Round 107 (J7 track jump), lens A fallback, run in parallel with underpass-bridge-relay-4r. lugcoil-lbracket-relay-4r is
merged here as its PHI 35 cell. 4 counted joints (J1, J2, J3 + the relay). It is a user option, never a lead.

## Deeper-version answers (written before the model)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Price the relay as a whole machine, not as a gap number.
   - The parent's verifier showed a 0.5 deg cliff (E over the carriage) and a 1.002 mm clearance floor.
   - So the designer would choose delta inside a window that is legal on both sides, and read the window BEFORE the
     claim: delta - 1 (the 259 contact comes back) and delta + 1.5 (the E-over-carriage jams).
   - The designer would also check the anterior shell end against the posed torso one bin at a time. A long shell can
     only gain if its last few degrees take poses without touching the skin.
   - The designer would ask whether the extra 5 deg buys reach that a person actually uses. Overhead is the user's
     priority, and the parent's relay bought 0 overhead.
2. **The rawest material.**
   - The posed skin itself: the bench's signed distance on every envsel / claim / held frame.
   - The motion clips and the 1432-pose workspace envelope grid, used by the continuity flood.
   - The clip-p90 skin radius about the relay axis a_r at the station (the proposer's longshell.py profile: 73.60 at
     +2 deg, 72.3 at +28, 69.3 at +44, 66.7 at +56).
   - The per-point shell distances, binned by azimuth (written by this model's 2-deg end bins).
   - Digested summaries are used only as pointers.
3. **Methods and tools.**
   - The parent's verified model, imported read-only (offset-shortcar-relay-4r -> proxtrack buildability ->
     armarc), with three source patches: the thin shell, the L-lug and the 2-deg end bins.
   - tools/env_bench.py envsel for selection, the exact signed-distance path, and Bench(110,360) exact frozen for the
     claim.
   - The held bench for held-out.
   - The armarc continuity flood (2-deg slerp edges, relay jump <= 10 deg) on the 1432-pose envelope grid at PHI 40.
   - tools/alignment_paired.py per-pose dumps (T5).
   - The armarc gravity check (R17).
4. **What, other than me, shows the number is right.**
   - The bench, read once at a pick that was pre-registered on envsel.
   - The held set.
   - An independent verifier rerunning the claim from this file.
   - The alignment auditor.
   - A red-team pose list: the anterior-end bins (envsel 119, behind-back ER), delta + 1.5 (the E-over-carriage cliff),
     delta - 1 (259), and the relayed poses at phi 35-40 that the PHI 35 flood never saw.

## Model (docs/concepts/models/phi40-thinstack-relay-4r.py)

The model imports offset-shortcar-relay-4r read-only. The chain is the verified lead's, with the buildable knee-over-boss
stack in every reading. The changes are:

- **PHI 40.** This needs its own prepare and its own continuity flood (flood_PHI40_t12_a235_s1.json in this row's
  verify dir).
- **Thin stack.**
  - The shell is 1.0 mm thick. The underside stays at R_liner; R_t = R_liner + 1.0, and the carriage, the bump target
    and the coil drop with it.
  - Lean flag: h_c 1.4, the slot end is the PHI stop, one zero dowel.
  - **Spec correction:** the proposer's patch read the pre-arc floors at R_liner + 1.5. Here they are re-read at the thin
    shell's R_t (each end 0.04 deg longer, conservative).
- **Lug coil 12 x 10:** a constant-force strip on the carriage's posterior-proximal lug. It is on the carriage-frame jam
  list and is sampled as metal.
- **Band 8, bump 1.2.**
- **L-lug bracket:** 2 x 10 Ti at the pad azimuth for every s (no planform turn), leaving the carriage at its
  posterior-distal corner.

## Results

### Selection protocol (envsel exact only; registered before each reading)

- Cells read at 19:33 UTC: PHI 40 x delta {3.5, 5.0, 4.0, 5.5}, plus the proposer's control (delta 4.5 with the old
  bracket). PHI 42 x delta {3.5, 5.0}.
- Registered at 19:40 UTC, BEFORE reading it (the PHI 40 / 42 trend is monotone so far): PHI 44 x delta {3.5, 5.0}.
- PHI 38 is a spec cell that was not read in the time box (see below).
- Pick rule (the spec's): the lowest gate with 0 jams whose delta + 1.5 partner reads 0 jams and lies within +0.5 of
  the pick. The claim bench is read ONCE at the pick. A claim-bench delta + 1.5 reading follows it as a red-team
  diagnostic that cannot change the pick.
- 19:44 UTC: the PHI 44 cell was stopped UNREAD (no output was written). PHI 42's delta 5.0 partner (shell end +53.08)
  put envsel 119 in contact at shell azimuth +51.9 (-0.67 mm). PHI 44 at delta 3.5 has its end at +53.6, past that point,
  and its partner at +55.1, so it cannot pass the +0.5 cliff clause. Registered instead at 19:44, BEFORE reading:
  PHI 41 x delta {3.5, 5.0} (end +50.6, partner end +52.1).
- 19:46 UTC: PHI 40 delta 4.0 read 14.50, which loses to delta 3.5 (14.46). Its partner (delta 5.5) and the
  proposer-reproduction control were stopped unread, because neither can change the pick. The claim-bench prepare at
  PHI 40 (and its flood) was started speculatively. It waits for a pick file and wears no hardware until one is written. Its
  prepare prints the hardware-free ideal-relay number; that log was not opened before the pick was written, so the
  PHI 40 / 41 choice could not see the claim bench.
- 19:50 UTC: the PICK was written before the claim log was opened.
  - PHI 41 at delta 3.5 reads 14.17, the same as PHI 42 at delta 3.5. One more pose relays at phi between 40 and 41,
    and the shell end at +50.6 is still clean at 0.90 mm on 119. Its partner (delta 5.0) reads 14.81 (+0.64): 119
    becomes a shell contact (-0.67 mm at +51.9) and drops out of reach.
  - So PHI 41 and PHI 42 both fail the +0.5 cliff clause, and on the same pose.
  - PHI 40 at delta 3.5 reads 14.46 with its partner at 14.58 (+0.12, 0 jams): legal.
  - **Pick = PHI 40, delta 3.5** (pick.json).

### Envsel (the selection bench, exact; chain-only gate)

| PHI | delta | gate | plain | ib14 chain / pooled | reach | contacts | jams | anterior end (119) |
|---|---|---|---|---|---|---|---|---|
| 40 | **3.5 (pick)** | **14.46** | 13.92 | 0.8946 / 0.9169 | 0.7972 | 15 | 0 | +49.6: 2.40 mm in the +48 bin |
| 40 | 5.0 (partner) | 14.58 | 13.92 | 0.8934 / 0.9153 | 0.7972 | 15 | 0 | +51.1: 0.82 mm |
| 40 | 4.0 | 14.50 | 13.92 | 0.8942 / 0.9163 | 0.7972 | 15 | 0 | +50.1: 1.87 mm |
| 41 | 3.5 | 14.17 | 13.63 | 0.8946 / 0.9165 | 0.8000 | 15 | 0 | +50.6: 0.90 mm |
| 41 | 5.0 (partner) | 14.81 (+0.64: fails) | 14.15 | 0.8934 | 0.7972 | 16 | 0 | +52.1: 119 at **-0.67 mm** (+51.9) |
| 42 | 3.5 | 14.17 | 13.63 | 0.8946 / 0.9165 | 0.8000 | 15 | 0 | +51.6: 0.90 mm |
| 42 | 5.0 (partner) | 14.81 (+0.64: fails) | 14.15 | 0.8934 | 0.7972 | 16 | 0 | +53.1: 119 at -0.67 mm |

For comparison, the proposer's readings on the same bench:

| reading | gate |
|---|---|
| PHI 35 lugcoil (the merged cell, delta 4.5) | 15.21 |
| PHI 40 composite, delta 4.5, planform-turn bracket | 14.54 |
| the same at delta 6.0 | 101.88 (188 E-over-carriage jams) |

Two things the table shows:

- The anterior end clears envsel 119 (behind-back ER) up to about +51.3 deg (about 0.75 mm per deg past +50). That
  is why PHI 41 and PHI 42 fail the cliff clause: their partners push the shell end onto the torso.
- The PHI 40 relay solve takes 6 envsel poses at phi > 35. Four are taken (222, 413, 423, and 467 at 0.97 mm) and two are
  chain contacts (360 -6.81, 421 -1.34).

### Claim: frozen exact Bench(110,360), read once at the pick (PHI 40, delta 3.5)

| | this row | offset-shortcar-relay-4r (verified 4-joint) | lead conecut-knee-knuckle-3r |
|---|---|---|---|
| chain-only gate | **14.06 (score 94.89)** | 14.76 (94.63) | 18.28 (93.35) |
| plain / near1 / near2 (no crown sets) | 13.52 / 18.18 / 38.82 | 13.74 / 17.91 / 37.70 | - / - / 34.84 |
| reach (ws taken) | **0.8056 (290/360)** | 0.7944 (286) | 0.7278 (262) |
| ib14 chain / pooled | 0.8946 / 0.9169 | 0.8898 / 0.9132 | 0.9012 |
| follow | 1.0 | 1.0 | 1.0 |
| contacts / jams | 17 / 0 | 13 / 0 | 4 |
| overhead (elev >= 140) | 9/28 | 8/28 | 8/28 |
| contact depth sum (min over each contact pose) | **74.93 mm**, deepest 15.37 | 46.18, deepest 9.79 | 20.24 |
| continuity (PHI 40 flood) | 0 relayed dropped | 0 | - |
| min th margin over taken | 5.000 (0 of 400 below 5) | 5.000 | 5.006 held |
| held-out gate | **16.69** (plain 16.02, reach 0.7878 = 750/952, 48 contacts, 0 jams, overhead 22/71) | 17.77 | 22.38 |

- **Gap breakdown:** reach 9.44 + contact 4.08 + in-band 0.54 = 14.06.
- **The 95 line (13.75) is missed by 0.31.**
- **Lens-A gate:** pass needs <= 13.75, so this is not a pass. Kill is > 14.76 or held > 18.27, so it is not killed
  either. The row stands as an option between the two lines.
- **Continuity flood at PHI 40** (flood_PHI40_t12_a235_s1.json, 1432-pose envelope grid): 177 relayed nodes, of which
  174 are connected. 3109 edges, 26 phi-jump failures. No taken relayed pose was dropped on the claim or on held.
- **Fold margin:** min th 5.000 on the claim and on held (952 taken, 0 below 5).
- **T5 per-pose dumps:** claim_phi40_pick_perpose.json and held_pick_perpose.json in docs/concepts/verify/phi40-thinstack-relay-4r/.

### Where the gain over the parent comes from (claim bench)

- **Thin stack, band 8, bump 1.2, lean.** Chain-only ib14 rises from 0.8898 to 0.8946: -0.48.
- **PHI 35 -> 40.** Eight claim poses relay at phi > 35.
  - Four are taken: 260 at **0.21 mm** (phi 38.3), 370 at 1.08 mm (overhead), 394, and 417.
  - Four are chain contacts: 233 -1.27, **263 (30, 150, -30) -15.37 mm** at phi 39.7, 421 -0.95, and
    **459 (150, 60, -120) -13.78 mm** at phi 39.3 (the L-lug bracket is at -5.63 there too).
  - At PHI 35 those 8 poses are lost. So PHI 40 buys -1.11 in reach and pays about +0.96 in contact: net about -0.15
    on the claim bench.
  - On held the band is better: 15 poses at phi > 35, of which 11 are taken and 4 are contacts.
- **466 (150, 105, -105) moved off the coil and onto the shell.** The parent's arm-fixed coil read -2.95; here the
  posterior shell end at -4.0 deg reads -0.33. The lean zero end (dowel + 1.5 mm slot end) and delta 3.5 together put
  the posterior end 2.1 deg further back than the parent's -1.9.

### Red team (each item is a measured reading)

1. **Deep contacts at the far end of the relay.**
   - 263 (overhead, elev 150) is -15.37 mm and 459 is -13.78 mm, both at phi ~39.5. Claim depth is x1.62 the
     parent's and x3.70 the lead's.
   - Held depth sum is 197.8 mm, deepest 13.89 (680, phi 35.2).
   - The bench's contact term is blind to depth, so the last 5 deg of travel is the most optimistic part of the number.
2. **The pinch point.** 260 is taken at 0.21 mm at phi 38.3. The min metal over taken poses is 0.072 mm (the
   inherited lead pose).
3. **Delta tolerance on the claim bench** (post-claim diagnostics; they cannot change the pick):
   - Delta 5.0 reads **13.67**, 0 jams: 466 clears the shell end at 0.41 mm, +1 take.
   - Delta 6.0 reads 14.02 with **5 E-over-carriage jams** at 0.88 mm (343, 370, 372, 423, 448).
   - The claim bench's delta window is therefore about [4.5, 5.5]. Envsel's is [3.5, 5.0]: 259 sets the floor and
     E-over-carriage the ceiling at 6.0.
   - The two benches agree only at delta 5.0. Envsel's cliff rule picked 3.5 and cost about 0.4 on the claim bench.
   - The posterior shell end is a pose-sample cliff (259 on envsel, 466 on the claim bench, 977 / 225 on held), not a
     tuning knob.
4. **Anterior end on held.** 211 (-90, 15, 165), behind-back ER, is a HARDWARE-only contact on the arm-fixed shell
   at +48.9 deg: -0.49 mm, chain clean at 4.66. This is the judge's predicted risk. The +50.9 end is not free on held
   even at PHI 40.
5. **T-nut flange and bracket in the skin on held.** On the extension / behind-back poses (-90 / -75, 60, 105-120) the
   1 mm flange under the shell is at -0.39 to -1.24 mm. Those poses are chain contacts anyway (224 -3.49, 225 -5.51,
   252 -1.60). 977 and 1134 have the L-lug bracket at -0.45 and -3.47 mm.
6. **Not priced here** (inherited from the parent; they need the verifier):
   - R17 friction / hysteresis: the CF coil 2.0 N vs gravity 0.78 N + mu 0.15-0.25 x 4 N = 1.38-1.78 N. The armarc
     gravity check is at phi 0 and depends only on the axis, so 0.063 N.m / coil >= 0.79 N is inherited.
   - The 3 bistable relay poses.
   - The 2 mm reading with the crown sets.
   - The deep_audit basis.
7. **The lean zero end costs one pose on the claim bench** (post-claim diagnostic).
   - lean 0 with h_c 1.4 kept (zero end (CAR_W/2 + dowel)/R_t, no 1.5 mm slot-end wall) reads **13.55**: 466 clears at
     0.15 mm.
   - The lean flag's 1.5 mm wall beyond the zero dowel is therefore worth 0.51 here, on one pose, at a 0.15 mm
     near-touch.
   - This is a bench-specific single-pose lever and a claim-bench reading, so it is NOT a claim. Move the dowel into
     the slot side wall to keep the parent's zero-end length; the next row should pre-register that on envsel and
     read held.

### Post-pick envsel completion and the PHI attribution (20:05 UTC, diagnostics only)

The PHI 35 cell (the merged lugcoil-lbracket hardware with the L-lug at delta 3.5 / 5.0) is read on envsel. The claim
bench at PHI 35 / delta 3.5 is also read, to price the PHI 35 -> 40 band on the claim bench. Neither can change the pick.

## Verdict

**SCREENED, between the lens-A lines.**

- **Claim:** 14.06, score 94.89, on frozen exact Bench(110,360), read once at the pre-registered envsel pick.
- **Held:** 16.69.
- **Against the parent** (offset-shortcar-relay-4r, the verified 4-joint, 14.76 / held 17.77): better by 0.70 on the
  bench and 1.08 on held. Reach 0.8056 is above every row with a gap under 20 on file (the parent has 0.7944).
- **The 95 line (13.75) is missed by 0.31.**
- **The cost is contact depth.** The last 5 deg of travel takes four poses and puts four into the skin, two of them at
  14-15 mm.
- **Status:** 4 active joints and complexity 51.25, so it is a user option, never a lead. It needs an independent
  verifier and an alignment audit (contact depth, the anterior end on held 211, crown-set near2) before it can be
  called verified.

## What happens next

1. **Verifier.** Reproduce the claim and held from this file (docs/concepts/models/phi40-thinstack-relay-4r.py
   pickrun with pick.json). Then run the X1 / X2 extended checks (the parent's verifier), the crown-set 2 mm reading,
   and the T5 depth comparison against the lead.
2. **The next relay row should register on envsel, before reading:**
   - The zero dowel in the slot side wall (keeps the parent's zero-end length; 0.51 on the claim bench here, one pose).
   - A delta inside BOTH benches' windows. Envsel is [3.5, 5.0]; the claim bench is about [4.5, 5.5]. 5.0 is the only
     value legal on both, and its claim-bench reading is now seen, so the next claim must be read on held first.
   - A soft-stop or skin-aware cap that keeps phi from passing about 37 deg where the chain dives (263, 459).
     The bench rewards the reach and ignores the depth.
3. **Fallback relation to the under-pass.** If the under-pass row (no bump: in-band chain 0.9012) passes its supports
   and height window, its in-band beats this row's 0.8946 by about 0.6 gap points. This row's levers (PHI 40, thin
   stack, L-lug) carry over to it.

| reading | gate | plain | ib14 chain | reach | contacts | jams |
|---|---|---|---|---|---|---|
| envsel PHI 35, delta 3.5 (the lugcoil-lbracket cell with the L-lug) | 15.13 | 14.59 | 0.8946 | 0.7861 | 13 | 0 |
| envsel PHI 35, delta 5.0 | 15.25 | 14.59 | 0.8934 | 0.7861 | 13 | 0 |
| claim bench PHI 35, delta 3.5 (diagnostic) | **14.28** | 13.74 | 0.8946 | 0.7944 (286) | 13 (466 on the shell end) | 0 |
| claim bench PHI 40, delta 3.5 (THE CLAIM) | **14.06** | 13.52 | 0.8946 | 0.8056 (290) | 17 | 0 |

- **Attribution on the claim bench:** the hardware levers alone (thin stack, band 8, bump 1.2, lean, lug coil,
  L-lug) take 14.76 to 14.28 (-0.48, all of it chain-only in-band 0.8898 -> 0.8946). PHI 35 -> 40 takes 14.28 to
  14.06 (-0.22): +4 takes and +4 contacts, two of them 14-15 mm deep.
- **On envsel PHI 40 is worth -0.67** (15.13 -> 14.46): 4 takes and 2 contacts there. The selection bench was more
  optimistic about the travel than the claim bench.
- **The PHI 35 cell would not have been the pick under the rule** (15.13 > 14.46). So the completed grid does not
  change the selection.
- **The chain-only in-band 0.8946 does not move with PHI or delta** (0.8934-0.8946). The bump window grows with PHI,
  but the E strap's band at the station is already covered at PHI 35.

## Convergence gate

This is a discrete, pre-registered hardware grid, not a CMA run: each wear takes 2-6 min and the farm is closed.

- **The 9 envsel readings:** 7 selection cells + 2 post-pick PHI 35 cells.
- **Gain over the 2nd half:** 0.00 score points. **Over the last third:** 0.00.
- **Top-5 spread:** 0.41 gap = 0.15 score points.
- **Caveat:** the two 14.17 cells fail the cliff clause, so the legal best is 14.46.

The grid did not include the axis, the station (ds 31), the carriage width or the band. Those levers belong to the
parent's grid and were inherited.

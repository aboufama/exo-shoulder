# offset-shortcar-relay-4r - proxtrack's one-sided relay, re-priced under the buildable pin-a stack

Round 106 (J6, track jump), lens A twoside-relay (the one-sided control), judge re-spec. Model:
`docs/concepts/models/offset-shortcar-relay-4r.py` (proxtrack-relay-knuckle-4r imported read-only THROUGH its buildability
verifier, so the verifier's stack rule `stackfix_amounts` is in every reading). Sweep: `docs/concepts/sweeps/offset-shortcar-relay-4r.json`.
Raw outputs: `docs/concepts/verify/offset-shortcar-relay-4r/`.

## Deeper-version answers (written before the first number)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the shell's two ends and the coil
   as the real design variables, not ds alone: the pose that binds (466-type posterior internal rotation) is a property of
   where arm-fixed metal sits over the posterior arm, so read the shell's skin margin per azimuth on the selection bench
   and place the zero end at the measured clean azimuth instead of at a pre-registered 4.5 deg. (b) Attribute every
   contact by part (chain / shell / carriage / bracket / flange / coil) at every config, so a hardware change can be
   seen to remove or add a specific contact rather than move a pooled number. (c) Sample the hardware the parent left out
   (T-nut retaining flange, constant-force coil) from the first reading, and put the coil on the JAM list (chain metal
   within 1 mm of it loses the pose), not only the contact list. (d) Check that a shorter carriage still carries the
   moment: the drawer rule L 14 > 2 mu d (7.5 mm) and the bracket's planform turn change the moment arm about the shell.
2. **Rawest material.** The posed skin itself through the bench's signed-distance field (every shell / coil / flange point
   is read against the posed scan at every pose, not against a summary radius); the fit-bench clip frames for the
   shell's p90 skin profile about the relay axis (the R_liner of the track); the envsel workspace draw (tools/env_bench.py,
   seed 2) as the only selection bench; the parent's per-pose dumps for the binders (466, 262, 206, 264).
3. **Methods and tools.** tools/concept_bench.py exact (libigl signed distance), the parent's relay solve / continuity
   flood (armarc), the verifier's buildable stack rule, the parent's rerecord with two hooks (part attribution, coil jam),
   envsel for every choice, one frozen exact Bench(110,360) claim wear + one held wear, T5 per-pose dumps
   (tools/alignment_paired.py format), AA.gravity_check for R17, tools/simplicity.py for cx.
4. **What other than me shows the number is right.** Three controls on one claim-bench prepare that must reproduce the
   verifier's 17.46 and the judge's 16.92 / 14.26 to 0.1 (a build check); the selection made on envsel only (the claim
   bench read once); the held-out bench paired against proxtrack's buildable held 21.46, freek 20.50 and the lead 22.38;
   the per-pose dumps on file for the auditor's T5 depth check; the red-team pose list below (posterior IR 466-type,
   folded-side relays 262 / 206, the elevation-0 alias at the anterior end, the near-jams at the 1 mm floor).

## The model (what was built, and where the spec was corrected)

- Parent imported read-only THROUGH `docs/concepts/verify/proxtrack-relay-knuckle-4r-buildability.py` (one module
  instance), with `bump_amounts = stackfix_amounts` (the knee link raised over the bumped pin-a boss, 60-deg ramp beyond
  the eye) in EVERY reading. PT.VDIR = this row's verify dir (own flood cache).
- `geometry()`: the parent's (pad azimuth th0, station s0 = s_pad + ds, p90 skin profile about a_r) with the carriage
  centre at th0 + delta, the shell at [th0 + delta - a0, th0 + delta + PHI + aP] (pre-arc floors (CAR_W/2 + 2)/R_t;
  lean flag: slot end (CAR_W/2 + 1.5) at PHI, dowel + wall at zero), R_liner re-derived over the moved arc. Because
  G['th0'] is the carriage centre, the parent's `_wcar` (carriage-footprint bump) and the carriage-sector clearance
  follow the offset unchanged; the bump window [lo - PHI, hi] follows lo / hi.
- `relay_points()`: shell as the parent; carriage at th0 + delta; bracket (2 x 10 Ti) from the carriage's distal edge
  at the carriage top to the pad's proximal edge with the planform turn interpolated along s; the T-nut retaining flange
  (the verifier's sampling, 1 mm Ti, 8 wide, skin-facing, in band); the constant-force coil (8 OD x 8 wide cylinder,
  axis along s) arm-fixed beyond the moved zero end (az lo - (D/2 + 1)/R_t, underside R_t + 1) or on a posterior lug.
- `rerecord()`: the parent's source with two hooks: (1) per-pose part attribution (chain / shell + azimuth of its
  deepest point / coil / carriage / bracket / flange); (2) the coil on the JAM list (knee, E, boss, hub 3, L2, pad
  within 1 mm of the coil = pose lost; metal in the skin stays a contact, as the parent).
- Spec correction: the parent's `prepare(nc=-2)` envsel path could not run (armarc reads the pose archive at import;
  envsel poses are appended later by tools/env_bench.py install()). Fixed here by installing envsel before the import
  (wrapped as an NpzFile-like dict); the claim / held benches are untouched by it (indices are appended).

## Controls (one claim-bench prepare, frozen exact Bench(110,360); coil none, flange 0 as in the references)

| control | this model | reference | |
|---|---|---|---|
| carw 24 / pre 10.41 / ds 19.538 / delta 0 (proxtrack buildable) | 17.46 | 17.46 (verifier) | exact |
| carw 14 / pre 0 / ds 19.538 / delta 0 | 16.92 | 16.92 (judge) | exact |
| carw 14 / pre 0 / ds 31 / delta 0 | 14.26 | 14.26 (judge) | exact |

All three reproduce to 0.00: the build is the verifier's and the judge's model. Part attribution on the controls: the
only hardware contact is 466 (150, 105, -105), on the shell's posterior end (az -10.4 at pre 10.41, -6.5 at the floor),
-8.22 / -3.33 / -3.26 mm.

## Selection on envsel exact (tools/env_bench.py envsel, seed 2, never the claim bench)

PHI 35 prepare (envsel ideal relay, no hardware: 14.59, reach 0.7861), carw 14, pre at its floor, coil arm-fixed,
flange sampled, buildable stack. Chain-only buildable gate:

| ds | delta | gate | ib14 chain | reach | contacts (hardware) | jams | note |
|---|---|---|---|---|---|---|---|
| 19.538 | 0 | 18.87 | 0.8710 | 0.7750 | 14 (197 shell -6.5 deg -1.94 mm; 264 chain+shell) | 5 (boss) | boss lift 4.89 |
| 28 | 0 | 15.94 | 0.8865 | 0.7861 | 13 (264 chain+shell) | 0 | 259 taken at 0.96 mm |
| 31 | 0 | 15.64 | 0.8948 | 0.7833 | 14 (259 shell -2.1 deg -0.02 mm; 264) | 0 | boss lift 1.13 |
| **31** | **4.5** | **15.61** | 0.8898 | 0.7861 | 13 (264 chain+shell only) | 0 | **pick**: 259 taken (shell 0.92 mm) |
| 34 | 0 | 15.68 | 0.8944 | 0.7833 | 14 (259 shell -0.08; 264) | 0 | boss lift 0 |
| 34 | 4.5 | 47.80 | 0.9212 | 0.6417 | 14 | 77 (E strap vs carriage / bracket) | cliff |
| 31 | 6 | 119.05 | 0.9443 | 0.4333 | 13 | 211 (E strap vs carriage / bracket, 0.09 mm) | cliff |

Envsel HAS its own posterior binder (259 at ds 31, 197 at ds 19.5: shell posterior end in the skin), so delta is
pre-registered by envsel, not by 466. The offset buys exactly that binder (+1 take) and pays it back in chain-only
in-band (0.8948 -> 0.8898: the bump window and the carriage footprint move with the carriage), net -0.03 on envsel.
Beyond delta ~4.5 the pad bracket's planform turn runs over the E strap: 211 jams at delta 6, 77 at ds 34 / delta 4.5.
The pick sits ~1.5 deg from that cliff. Not read (time box, load 13-15 on 4 cores): delta 3, carw 12 / 16, coil on the
lug, lean flag, bump 1.15, ds 36. PHI stays 35: the anterior end (45.9 rel th0) shows no hardware contact on envsel.

## Claim: ONE frozen exact Bench(110,360) wear at the envsel pick

Pick: PHI 35, tilt 12, taz 235, sgn +1, ds 31, delta 4.5, carw 14, pre 0 (floor 6.40 deg), h_c 1.7, bump 1.002, band
9.272, ramp 6.0 (floor 6.27), rt_extra 1.5, coil arm-fixed beyond the zero end (az -5.46 rel th0, underside R_t + 1),
T-nut flange sampled, lean 0. Shell R_t 80.6, arc [-1.9, +45.9] deg rel the pad azimuth (67.2 mm), bracket 25.0 deg
climb with a 6.46 mm planform turn (legal under the 60-deg ruling; bent 2 x 10 Ti), boss lift 1.23 mm (knee link
raised over it), 0 jams.

| reading | value |
|---|---|
| **chain-only buildable gate (the claim)** | **14.76** (score 94.63) |
| plain (pooled in-band 0.9132) | 13.74 |
| near1 (metal < 1 mm = contact) | 17.91 |
| 2 mm reading (near2) | 37.70 |
| ib14 chain-only / pooled / ib10 | 0.8898 / 0.9132 / 0.5608 |
| reach (ws taken) / follow / overhead | 0.7944 (286 / 360) / 1.0 / 8 of 28 |
| contacts | 13 (0.0318): the SAME 13 poses as proxtrack (no new contact of any kind) |
| jams | 0 |
| continuity (PHI 35 flood, own dir) | 0 relayed poses dropped (static = connected) |
| relayed bench poses | 33: 24 taken, 9 contacts, 0 jams, phi max 32.94 |
| min metal on taken poses | 0.072 mm |

Contacts by cause: the lead's own at phi 0: 205 -4.28, 237 -8.93, 264 -5.80, 316 -1.23; relayed chain: 182 -0.71,
206 -6.07, 262 -9.79 (folded-side one-sided relays, hub 2), 343 -1.73, 372 -0.07, 423 -0.70, 448 -1.92, 457 -2.00;
hardware: **466 (150, 105, -105) at phi 28: -2.95 mm, and it is the COIL, not the shell** - the offset did clear the
shell there (shell 0.68 mm, from -3.26 at delta 0), but the arm-fixed coil now sits where the old posterior end was.

vs the controls on the same bench: ds 31 / delta 0 = 14.26 (judge, reproduced). The offset costs chain-only in-band
0.8948 -> 0.8898 (+0.50: the bump window [lo - PHI, hi] and the carriage-footprint bump move 4.5 deg with the carriage)
and buys no take on this bench (466 trades a shell contact for a coil contact): 14.26 -> 14.76.

## Diagnostics on the claim bench (P1 class: read AFTER the claim, set nothing)

One more claim-bench prepare, the pick's hardware with the coil moved:

| coil | gate | plain | takes | contacts | jams |
|---|---|---|---|---|---|
| arm-fixed beyond the zero end (the claim) | 14.76 | 13.74 | 286 | 13 (466 = coil -2.95) | 0 |
| on the carriage's posterior-proximal lug (anterior edge az th0 + 2, underside at the carriage top) | 14.23 | 13.21 | 287 | 12 (466 taken, shell 0.68 mm) | 0 |
| none (ideal-coil bound) | 14.23 | 13.21 | 287 | 12 | 0 |

So the lug coil costs nothing over the ideal-coil bound on this bench, and the best this hardware can read here is
14.23: 0.48 over the 95 line (13.75), because the offset's in-band cost (+0.50) eats the 466 take (-0.52). Envsel (the legitimate
selection bench, read after the claim) TIES the two coils: 15.61 / 15.61 (envsel has no coil binder), so envsel cannot
choose the lug; the claim stays the arm coil read once, and 14.23 stays a diagnostic until someone pre-registers a
physical tie-break (e.g. no arm-fixed part over the posterior arc) and re-reads it.

## Held-out bench (the lead family's held set, 1154 poses; one prepare: proxtrack's buildable control, then the pick)

| | gate (chain-only) | plain | near1 | reach / takes | contacts | jams | overhead |
|---|---|---|---|---|---|---|---|
| proxtrack buildable control (carw 24, ds 19.538) | 21.46 (reproduces the verifier's 21.46) | 18.37 | 23.75 | 0.7689 / 732 | 47 | 17 | 18 / 71 |
| **pick (ds 31, delta 4.5, carw 14, arm coil)** | **17.77** | 16.64 | 22.62 | 0.7773 / 740 | 43 | 0 | 19 / 71 |

Bench -> held inflation +3.01 (proxtrack +4.0, the lead +4.10). No new held contact; 4 gone: 211 (-90, 15, 165)
(the anterior-end alias, -0.73), 842 / 914 / 1140 (posterior IR, shell -5.15 / -2.11 / -9.61 at az -9 / -10.4: the
offset moved the shell off them, and the coil does not reach them). 8 more workspace takes, 17 jams -> 0 (the station:
boss lift 5.69 -> 1.23). Paired (tools/alignment_paired.compare_sets on the per-pose dumps, plain pooled gap, 4000
paired bootstraps within kind): vs proxtrack buildable -1.73 (CI90 -2.91 .. -0.81, P(better) 1.00); vs the lead
conecut-knee-knuckle-3r 22.38: -5.74 (CI90 -7.90 .. -4.14, P 1.00); vs freek-oracle-route-knuckle-4r's dump on file
(21.89, the verified config): -5.26 (CI90 -8.49 .. -2.96, P 1.00); freek's polished held 20.50 is 2.73 above this gate.

## Red team (my own best config)

- **The pose that binds**: 466 (150, 105, -105) at phi 28, coil -2.95 mm; on the claim bench the shell is at 0.68 mm
  there (a near-touch: near1 counts it). On held the parent's posterior binders are 842 / 914 / 1140 (shell -2.1 to
  -9.6 mm at az -9 to -10.4); the offset moves the shell off them and the arm-fixed coil does NOT reach them on held (no held contact has coil metal under 1 mm): 466 is the coil's only
  binder on file.
- **The cliff**: the bracket's planform turn runs over the E strap: 0 jams at delta 4.5, 211 at delta 6 (E strap
  0.09 mm from the carriage frame), 77 at ds 34 / delta 4.5. The pick is ~1.5 deg from it; the CAD must route the
  bracket at the pad's azimuth (an L-shaped carriage lug) rather than turn over the strap, and re-read.
- **The optimistic numbers**: plain 13.74 pools the shell / flange / bracket metal into in-band (chain-only 0.8898 is
  the honest share); the min metal on taken poses is 0.072 mm; near1 17.91 and near2 37.70; the ramp sits on its
  60-deg floor (6.27) and rt_extra on the box edge 1.5 (proxtrack: rt 2.5 reads +0.86); 3 bistable relay poses and the
  stops parked at the 5-deg th margin are inherited from proxtrack (same prepare, same relay solve: min th 5.0 as the
  verifier measured).
- **Selection hygiene**: delta, ds, carw and the coil were chosen on envsel; the claim bench was read once at the
  pick; the coil diagnostics above were read after the claim and choose nothing.
- **R17**: the relay axis, PHI, sense and chain are proxtrack's, so the gravity check is proxtrack's: preload >= 0.063
  N.m, i.e. a constant-force coil F >= 0.79 N at R_t 80.6 (part number still to confirm). Not re-run (two niced
  processes on a load-14 box).

## Verdict against the judge's pre-registered clauses

- 95 PASS (chain-only buildable gate <= 13.75, no contact outside proxtrack's 13, held paired better than 21.46):
  **FAILS** on the bench number: 14.76 (0.99 over the line). The other two clauses hold.
- **4-JOINT PASS (<= 15.40 and held <= 20.50): PASSES**: 14.76 / held 17.77 - better than freek-oracle-route-knuckle-4r
  (polished 15.40 / held 20.50) on both, at complexity 52.5 (freek 33.25; lean flag 51.25).
- KILL (gate > 16.92, a new folded-side contact, held paired worse than 21.46): none triggered.

Score 94.63 frozen exact (lead conecut-knee-knuckle-3r 93.35 at 18.28; held 17.77 = the best held number on file,
lead 22.38). It is a 4-joint design: under the user's rulings it is not the headline lead; it is the best-held 4-joint
row and the nearest buildable reading to 95.

## What limits it (measured)

1. **The rigid bump's in-band**: chain-only ib14 0.8898 (pooled 0.9132). The offset moves the bump window
   [lo - PHI, hi] and the carriage-footprint bump 4.5 deg with the carriage: 0.8948 -> 0.8898 = +0.50 on both envsel and
   the claim bench. In-band is 0.11 points from its target here; the gap is reach (10.56) + contact (3.18) + in-band (1.02).
2. **12 chain contacts unchanged** (the lead's 4 at phi 0 + 8 relayed: the folded-side one-sided relays 262 / 206 on
   hub 2, 343 / 372 on L2, 182 / 423 / 448, boss + knee at 457) and the fold: 56 poses beyond the relay, overhead 8 / 28.
3. **The posterior binder follows the arm-fixed hardware**: 466 left the shell (0.68 mm) and landed on the coil
   (-2.95 mm). The coil on the carriage lug reads 14.23 (diagnostic) = the ideal-coil bound.
4. **The bracket cliff** at delta > 4.5 (E strap under the planform turn).

## New knowledge

- The buildable-stack station effect holds on the selection bench independently of the claim bench: envsel 18.87
  (ds 19.5) -> 15.94 (28) -> 15.64 (31) -> 15.68 (34), and on held it is larger than on the bench (21.46 -> 17.77 with
  the offset; 17 jams -> 0).
- An arm-fixed part near a one-sided relay's zero end is the posterior-IR binder whatever it is (shell end or coil):
  moving the shell end just hands the contact to the next arm-fixed part. The coil belongs on the carriage.
- Offsetting a carriage under a rigid bump is not free: the bump window follows the carriage, ~0.11 point per deg here.
- The judge's claim-bench prediction (466 a take -> ~13.74) missed because it priced the offset's take and not its
  in-band cost; the lug-coil diagnostic (14.23) is the measured ceiling of this hardware family at this station.

## What happens next

1. The verifier re-measures the claim (14.76 / held 17.77) from the per-pose dumps on file (T5: claim_pick_perpose.json,
   held_pick_perpose.json).
2. Lug coil: envsel ties it with the arm coil (15.61 / 15.61); with a pre-registered physical tie-break (no arm-fixed
   part over the posterior arc) one claim + one held wear at the lug (diagnostic 14.23 bench).
3. Win the in-band back: a bump window that follows only the carriage footprint's real travel instead of
   [lo - PHI, hi], or a delta-free fix for 466 (the lug coil alone at delta 0 keeps the shell end at -6.4, where 466's
   shell is -3.26: so the offset stays, and the in-band must be bought elsewhere - band 8 (its floor) on envsel).
4. Route the bracket at the pad azimuth (L-shaped carriage lug) so delta is no longer bounded by the E strap cliff.

## Status

SCREENED 2026-10-18 (status 'screened' in the catalogue): frozen exact Bench(110,360) chain-only buildable gate 14.76
(score 94.63), plain 13.74, held 17.77 / plain 16.64; 4 active joints, 0 passive translations, complexity 52.5
(51.25 lean). Selection grid on envsel: 8 readings (7 hardware configs + the lug), convergence gate on the grid: gain
over the 2nd half 0.00, over the last third 0.00, top-5 spread 1.19 score points (a pre-registered discrete grid,
not a CMA: ds / delta / coil are the only free hardware levers here; carw 12 / 16, lean, bump 1.15, ds 36 not read).
Files: model `docs/concepts/models/offset-shortcar-relay-4r.py`, outputs and T5 dumps
`docs/concepts/verify/offset-shortcar-relay-4r/` (controls_claimbench*, envsel_s1..s3, claim*, held*, diag_coil*,
paired_held.json), sweep `docs/concepts/sweeps/offset-shortcar-relay-4r.json`, preview
`docs/concepts/viz/concepts/offset-shortcar-relay-4r.js`.

## Verification (independent skeptic, 2026-10-18)

Verifier: `docs/concepts/verify/offset-shortcar-relay-4r-verify.py`. It imports the claim model unchanged, re-records the
same prepared wear, and adds the checks the model leaves out. Outputs are in `docs/concepts/verify/offset-shortcar-relay-4r/verifier_*`.

**Verdict: VERIFIED at v_gap 14.76** (frozen exact Bench(110,360), chain-only buildable gate; score 94.63). Held out:
**17.77**. Both reproduce the claim to 0.00, and the extended checks find no new jam. The champion on the same bench is
75.94 (the risley-turret verifier's champion with the kit checks and 1 mm clearance). This verifier's checks are a
superset of that family's, and the extra relay checks do not apply to a design without a relay. Not refuted: there are
4 active joints (inside the cap), 0 passive translations, and the relay coordinate is held by the CF coil on its zero
dowel plus an own-angle PHI dowel. The 95 line is missed by 1.01 (13.75 needed).

| reading (frozen exact) | gate (chain-only) | plain | near1 | ib14 chain / pooled | reach (ws taken) | contacts | jams |
|---|---|---|---|---|---|---|---|
| claim as modelled, re-run (`verifier_delta_probe` [0]) | 14.76 | 13.74 | 17.91 | 0.8898 / 0.9132 | 0.7944 (286) | 13 | 0 |
| **with the extended checks X1 + X2 (`verifier_claim`)** | **14.76** | 13.74 | 17.91 | 0.8898 / 0.9132 | 0.7944 (286) | 13 | 0 (+0) |
| held out, with X1 + X2 (`verifier_held`) | **17.77** | 16.64 | 22.62 | 0.8887 / 0.9123 | 0.7773 (740) | 43 | 0 (+0) |
| diag: coil on a shell tab (`verifier_tab`) | 14.76 | 13.74 | 17.91 | 0.8898 / 0.9151 | 0.7944 | 13 (466 now the tab, -5.56) | 0 |
| **red team: carriage rest delta 5.0 (+0.5 deg)** | **27.53** | 27.53 | 31.36 | 0.9130 / 0.9335 | 0.7278 (262), follow 0.8818 | 13 | **37** |
| red team: bump 1.2 (0.2 mm build tolerance on the E strap; `verifier_bump12`) | 14.88 | 13.74 | 17.91 | 0.8886 / 0.9122 | 0.7944 (286) | 13 | 0 |

Checks run:

1. **Active DOF and determinacy.** The design has J1, J2 and J3 plus the relay, which is a counted 4th joint (4 is the
   cap). The two knee pins sit outside the count, as the user ruled. There are no passive translations. The relay
   carriage is a curved sliding pair: a rotation about a_r. It sits on its zero dowel under the coil, and the PHI end
   is an own-angle dowel in the shell slot. The fold margin, read the H1 way on the claim bench, has a minimum `th`
   margin of 5.000 deg over 396 taken poses (0 below 5); held: 5.000 over 942. Continuity: the PHI 35 flood
   (153 of 154 relayed envelope nodes connected) drops 0 bench poses and 0 held poses.
2. **Every part at its real size and sampled.** The shell (both faces), carriage, T-nut flange, bracket and coil
   cylinder are all sampled at about 1 point per 4 mm2 and checked against the posed skin at every pose. This
   verifier adds two checks the model omits:
   - **X1:** every chain part, including the contact-only top and crown sets, is checked against every relay body,
     bumped exactly as the model bumps it. The model checked the shell against 6 parts, the carriage against 4, the
     bracket against the E strap and boss only, and the coil against 6.
   - **X2:** the bracket's top face is sampled as well (the bracket is a 2 mm plate).

   Result: **0 new jams** on the bench and 0 held. The closest non-adjacent pairs on taken poses are:
   - E strap over the carriage, 1.002 mm;
   - E strap over the shell, 1.115 mm;
   - E strap vs the bracket, 1.45 mm (nearest sample - 1);
   - every other part vs the coil, >= 13.8 mm.

   The knee link, which is adjacent to the pad/bracket body through pin b, comes to 0.216 mm of the bracket (sampled,
   - 1 mm) only on contact poses 343 (bench) and 1153 (held). On taken poses it stays >= 1.4 mm.
3. **Honest pose-taking.** The same 13 contacts as proxtrack: the lead's 4 at phi 0, 8 relayed chain contacts, and
   466 on the coil at -2.95 mm. All are counted. There are no jams laundered into lost poses, and the T5 per-pose dumps
   reproduce the plain gap (bench 13.74 -> 13.73 recomputed, held 16.64 -> 16.63; `verifier_claim_perpose.json`,
   `verifier_held_perpose.json`).
4. **No bench artefact.** CB_EXACT=1 throughout, with one prepare per bench, and the claim bench was read only at the
   pick. Selection was on envsel only: the pick beat delta 0 there by 0.03, and on the claim bench delta 4.5 is 0.50
   worse than the delta-0 control (14.26). The pick was not tuned to the claim bench.

Red-team findings (none breaks a rule; the first two make the number optimistic as a build):

- **The cliff is 0.5 deg away, not ~1.5.** At delta 5.0 the bench reads **27.53**: 37 poses jam, including 13 clip
  frames, so follow falls to 0.88. All 37 are the E strap over the carriage at 0.93 mm, not the bracket. The doc's
  "the pick sits ~1.5 deg from that cliff" is wrong. Delta 4.5 is the last safe reading on a 0.5 deg step (0.7 mm of
  carriage travel at R_t 80.6).
- **The E-over-carriage clearance is at the rule floor on most poses.** The bump is 1.002, so the E strap sits
  1.002 mm over the carriage. Of the taken poses, 112 on the bench (61 ws) and 270 held are under 1.1 mm; 182 bench
  and 400 held are under 1.2 mm. This is legal under the 1 mm rule, but it leaves no build tolerance. The bump-1.2
  reading prices a 0.2 mm tolerance: gate 14.88 (+0.12) with 0 jams, so the margin is cheap to buy (a build should
  use about 1.2).
- **The coil floats in the model.** It is an 8 x 8 cylinder 1 mm over the shell-top level beyond the zero end, with no
  mount. Mounted on a shell tab (the shell continued at R_t to the coil's far edge, -8.3 deg) it costs 0.00: 466 goes
  from -2.95 on the coil to -5.56 on the tab, with no new contact and no jam. A cheek mount from the shell's end face
  to the coil axle is the lighter build, and the tab bounds it.
- Inherited and unpriced here (from the buildability verifier of proxtrack, same PHI, axis and chain):
  - 3 bistable relay poses on the claim bench, worth <= ~0.6-0.8 points;
  - the R17 preload covers gravity only (no carriage friction or coil hysteresis);
  - 4 DOF where the user prefers 3, so this is not a leader under the 3-DOF ruling, and the complexity is 52.5.

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

## Status

(claim and held filled in below)

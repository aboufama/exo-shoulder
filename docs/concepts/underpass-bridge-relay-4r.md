# underpass-bridge-relay-4r - the E strap passes UNDER a raised arm-fixed bridge shell

Round 107 (J7, track jump). 4 counted joints (J1, J2, J3 + the relay): a user option, never a lead.
Model: `docs/concepts/models/underpass-bridge-relay-4r.py` (imports `offset-shortcar-relay-4r.py` read-only).
Verify dir: `docs/concepts/verify/underpass-bridge-relay-4r/`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the bridge as a structure, not a
   strip of sampled points: it carries the pad load (~4 N) through the carriage, so either both ends are supported or
   one end carries a moment. Check the real section against that load (deflection must stay inside the under-pass
   clearance, here <= 0.5 x up_clr), and keep the underside fixed when the section is stiffened: a thicker shell only
   raises the TOP (and what rides on it: carriage, bracket, lug coil), so the in-band price is the bracket and coil, not
   the shell underside. The judge's "+1 mm shell reads 15.99" moved the UNDERSIDE (rt_extra +1), not the thickness, so it
   does not price a thicker cantilever. Second: freeze the bridge height at selection and wear it unchanged on the claim
   and held benches; an under-pass whose height is re-placed per bench would hide the E-envelope risk.
2. **Rawest material.** The posed skin itself (signed distance per pose, B.dist) on the envsel / claim / held benches; the
   fitted chain's sampled metal in the arm frame (HG0) and the carriage frame at every fit and envsel frame (the need
   scan, per 1-deg azimuth bin rel the pad); the judge's raw block readings (scratch r107j/blocks.log, blocks2.log,
   eaz.log) and the proposer's under-pass wear (r107a/underpass2.log), reproduced here rather than quoted.
3. **Methods and tools.** The verified parent's buildability path (offset-shortcar -> proxtrack buildability verifier ->
   proxtrack -> armarc relay solve, flood continuity), its sector jam rule extended to every support / extension sector,
   envsel exact for selection only (tools/env_bench.py), frozen exact Bench(110,360) for the claim, the held bench once,
   curved-cantilever beam theory (Castigliano: radial tip deflection P R^3 / (E I) (a/2 - sin 2a / 4)) for the
   bridge section, tools/simplicity.py for the complexity record.
4. **What, other than me, shows the number is right.** The bench itself (the parent's verified wear path, unchanged gate
   arithmetic), the controls (the proposer's 14.59 no-support reading must reproduce on this code before any support
   is priced), the independent verifier that will re-run the claim, and a red-team pose list (the posterior binder
   class 259 / 264 / 265, the anterior torso pose 119, E's highest pose in the footprint, every jam / near-touch pose).

## Pre-registered selection (written before any reading)

Selection on envsel exact only. Cells: PHI {35, 40} x {ant ii (cantilever, tshc 2.5) d4.5 u1.2 H2; ant i (extension +
block beyond E) d4.5 u1.2 H2; ii d4.5 u1.0 H2; ii d3 u1.2 H2; ii d3 u1.0 H2; ii d4.5 u1.2 H1.5}; carw 14, ds 31, lug coil
D12 L10, flange on. Pick = the lowest chain-only gate with 0 jams, pooled ib14 >= 0.90 and bridge deflection <= 0.5 x
up_clr; ties (within 0.05) broken by fewer taken poses with metal < 1 mm, then the thinner posterior block. The claim
is read ONCE (CB_EXACT=1, Bench(110,360), frozen, rl_fix / hiE frozen from envsel), then the held bench once.
Pass = gate <= 13.75 with 0 jams; kill = gate > 14.76 or held > 18.27.

Addendum written after cells 1-5 had read and BEFORE cell 6 (H 1.5) read: cells 1, 3, 4, 5 (all ant ii) tie at 14.59 with
15 near-touch poses and the same block height, so the pre-registered rule cannot separate them. Last tie-break, chosen
for robustness and not for a number: the larger E clearance (up_clr 1.2: the claim's E envelope is the main risk), then
the parent's verified delta 4.5. If cell 6 ties, the rule's own "thinner posterior block" picks it.

## What was built (the model)

`underpass-bridge-relay-4r.py` imports the verified parent `offset-shortcar-relay-4r.py` (and through it the
proxtrack buildability verifier, proxtrack and the armarc relay solve) read-only and changes only the hardware:

* **No bump.** `PT.bump_amounts` returns `{}`: E strap, pin-a boss and knee link at the lead's verified heights (the lead's
  own pin-a stack, so the parent's stackfix is not needed).
* **Bridge height, frozen at selection.** Need scan over the 184 fit kin_ok frames (phi 0) + 296 envsel fresh frames
  (480 frames): the highest chain point inside the shell footprint is the E strap at r 80.11 (envsel 279, +18.5 deg rel
  pad); inside the T-nut flange footprint (carriage frame) E at 77.70 (fit 139). R_under = max(skin rule 79.10, 80.11 +
  up_clr, 77.70 + 3) = **81.307** at up_clr 1.2. The claim and held benches wear this number (`rl_fix`); they never
  re-place the bridge. E's arm-frame azimuth at the station spans **+6.44 .. +49.00 deg rel pad** (judge: 6.4 .. 49.0,
  reproduced).
* **Shell.** Ti, 12 wide (8 net), cantilever section **2.5 mm** (underside fixed at R_under, top R_t 83.807: carriage,
  T-nut flange, bracket and lug coil ride the real top / underside; the parent's hard-coded "underside = R_t - 1.5" is
  moved to R_under in the samples AND in the jam sector).
* **Supports as sampled metal** (arm-fixed contact list + jam sectors added to the parent's sector rule):
  posterior foot Ti 12 x 4 x H at [lo - 4 mm, lo] under the zero end (E never reaches it); ant='i' = the shell
  extended over E's envelope + an anterior foot at [hiE + 1, hiE + 5] mm; ant='ii' = no anterior support.
* **Cantilever check** (curved beam, Castigliano, radial tip load P = 4 N, R = 82.6, a = 47.3 deg):
  delta = P R^3 / (E I) (a/2 - sin 2a / 4) = **0.31 mm** at t 2.5 (I = 10.4 mm^4) <= 0.5 x up_clr = 0.6; a plain 1.5 mm
  strip would deflect 1.44 mm (more than the clearance). Root moment P R sin a = **243 N.mm**.
* **Coil**: CF coil D 12 x L 10 on the carriage's posterior-proximal lug (carriage-frame jam list).

## Selection (envsel exact, 480-frame placement, 406 evaluated poses)

| cell | PHI | ant | delta | up_clr | H | gate | chain | pooled ib14 | jams | hw contacts | metal<1 taken | defl |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 35 | ii | 4.5 | 1.2 | 2.0 | **14.59** | 14.59 | 0.9024 | 0 | 0 | 15 | 0.31 |
| 2 | 35 | i | 4.5 | 1.2 | 2.0 | 16.31 | 15.12 | 0.8881 | 0 | 1 (119 -1.80, ext at +52.5) | 15 | 0.14 |
| 3 | 35 | ii | 4.5 | 1.0 | 2.0 | 14.59 | 14.59 | 0.9047 | 0 | 0 | 15 | 0.31 |
| 4 | 35 | ii | 3.0 | 1.2 | 2.0 | 14.59 | 14.59 | 0.9037 | 0 | 0 | 15 | 0.31 |
| 5 | 35 | ii | 3.0 | 1.0 | 2.0 | 14.59 | 14.59 | 0.9059 | 0 | 0 | 15 | 0.31 |
| 6 | 35 | ii | 4.5 | 1.2 | 1.5 | 14.59 | 14.59 | 0.9021 | 0 | 0 | 15 | 0.31 |
| 1 | 40 | ii | 4.5 | 1.2 | 2.0 | 14.61 | 13.92 | **0.8931** | 0 | 0 (shell 0.35 at 119) | 17 | 0.41 |

* Every ant-ii cell at PHI 35 reads **14.59 = the envsel ideal-relay bound** (no hardware): the bridge, its posterior
  foot, the thicker cantilever top, the lug coil and the flange cost nothing on the selection bench. Hardware can only
  add metal, so no cell can read below the bound; the grid could only be separated by the tie-breaks -> cell 6 (H 1.5).
* ant 'i' is dead as the judge predicted: the extension over E's envelope meets the torso at envsel 119 (-64, 3, 151:
  arm down, behind-back ER), -1.80 mm, and its in-band metal pulls pooled ib14 to 0.888.
* PHI 40 (ideal 13.92 on envsel) fails the pooled in-band rule: the longer arc (to +50.65) brings the shell end to
  0.35 mm of the torso at 119 and relay ib to 0.874 -> pooled 0.8931. The remaining PHI 40 cells were stopped for the time
  box (measured sensitivity -0.016 pooled ib per mm of shell height: up_clr 1.0 buys ~0.003, short of the 0.007 needed).
* A first run with the parent's proxtrack base overriding this row's hardware (ds 19.5, pre 10.4: a bug, fixed in 2
  minutes) read 20.42 (log kept: verify/.../bug_base_override_phi35.log) - with the shell end at +49.9 deg the same
  torso pose 119 is a -4.16 mm contact.

CONVERGENCE GATE (discrete pre-registered grid, not CMA): gain over the 2nd half 0.00, over the last third 0.00, top-5
spread 0.00 score points (five cells tie at the bound) - converged on envsel; the bound itself is the limit.

## Claim: frozen exact Bench(110,360), read once (CB_EXACT=1; rl_fix 81.307, hiE 49.0 frozen from envsel)

**Chain-only gate 13.74 = plain 13.74, score 95.00 (pass line 13.75: PASS by 0.01).** reach 0.7944 (286/360), follow 1.0,
ib14 chain 0.9012 / pooled 0.9021 (relay metal 0.9047), ib10 0.5447, contact 0.0318 (13 contacts), **0 jams**, overhead
8/28, continuity flood: 0 relayed takes dropped (static = connected = 13.74), near1 17.91, near2 38.22 (crown sets not
re-read: owed), min metal over taken poses 0.072 mm, relayed 33 (24 taken, 9 contact, 0 jam, phi max 32.9).
Ideal-relay bound on the claim bench: 13.21 - so the whole hardware price is **one pose: 466** (150, 105, -105; phi 28.0):
the posterior foot is **0.56 mm in the skin** (shell_az -4.5 rel pad = inside the foot's [-4.47, -1.65]); 466 was a take
in the ideal reading (reach -1 take +0.28, contact +0.25).
Contacts: the 12 chain contacts the parent inherits (lead's 205 / 237 / 264 / 316 at phi 0; relayed 182, 206, 262, 343,
372, 423, 448, 457 - identical depths to the parent) + 466 at the foot (the parent's 466 was the arm-fixed coil, -2.95).
Contact depth sum 43.79 mm (parent 46.18 at its claim; the lead 20.24).
T5 dump: `verify/underpass-bridge-relay-4r/claim_perpose.json`.

Post-claim diagnostic (same claim-bench prepare protocol, NOT a claim, not used to pick): posterior foot H 1.0 / 2.0
read 13.74 / 13.74 (466 at the foot -0.33 / -0.79 mm; H 1.5 -0.56). The foot's depth at 466 falls only 0.46 mm per mm of
H, so a foot at the zero end is a contact at 466 for any real height (extrapolated clear only at H ~0).

## Red team (my own pick)

1. **The pass is 0.01 wide.** 13.74 vs 13.75: any one extra contact or lost take on the claim bench crosses the line.
   The whole hardware price is 466 (posterior foot in the skin); remove it and the claim is the ideal bound 13.21
   (score 95.20, margin 0.54).
2. **The pinch point: the posterior foot at 466** (150, 105, -105: arm across the front at 105 elevation, full IR, phi
   28 - the relay at 80 % travel). The judge's envsel table (259 / 264 / 265) did not contain this pose. Candidate lever
   for the next round: a foot UNDER the shell's zero end ([lo, lo + 4 mm] = [-1.65, +1.17] deg rel pad) is E-free (E's
   arm-frame azimuth starts at +6.44, ~7.6 mm of margin) BUT the T-nut flange's posterior edge rests at lo + 2 mm
   (carriage half-width + the 2 mm zero dowel), so a full-width inboard foot collides with the flange at rest; only side
   feet outside the flange's s band (|s - s0| 5..6 mm, 1 mm wide each) or a foot proximal / distal of the shell band
   would fit - each needs its own skin read at 466 (not done: time box).
3. **The root moment.** A cantilever needs 243 N.mm at its root; a 12 x 4 mm Ti foot on a soft liner pad cannot carry it
   (61 N couple over 4 mm). The root must be a rigid arm-band anchor (a band plate posterior of the foot) - unmodelled
   metal, and the band's compliance tilts the shell (tip drop not priced). Without that anchor the design is the
   simply-supported option (i), which the torso at 119 kills.
4. **Deflection vs the clearance.** 0.31 mm at 4 N leaves E 0.89 mm under the loaded shell at its highest pose (envsel
   279) - below the 1 mm jam rule when the pad is loaded there; the jam rule was read on the unloaded shell.
5. **Near-touch on the bracket.** The bracket (in-band, carriage frame) sits 0.45 mm over the skin at 139 (-60, 60, 105;
   envsel 259 0.36 mm) - inherited from the parent; 8 taken poses have metal < 1 mm (parent row: 56 < 2 mm; here 48).
6. **Inherited and unpriced:** 3 bistable relay poses, carriage friction / coil hysteresis (R17 covers gravity only), the
   parent's tolerance cliff (delta 5.0 -> 37 jams; delta + 1.5 not re-read here), 4 active joints (+25 complexity).
7. **Optimistic numbers I know of:** the 2 mm reading with the crown sets (lead basis) was not re-read (parent: 45.56 vs
   its 37.70 without); the claim / held E envelope was read only through the jam rule (0 jams), not tabulated.

## Held-out bench (read once, same frozen pick)

**Gate 16.64 = plain 16.64 = the held ideal-relay bound** (reach 0.7773, follow 1.0, ib14 chain 0.9000 / pooled 0.9009,
43 contacts, 0 jams, overhead 19/71, near1 22.62, near2 41.91, 29 taken poses < 1 mm). The parent reads 17.77 gate / 16.64
plain on the same held bench: the under-pass removes the parent's in-band term there too (-1.13), and the held hardware
contacts are all on poses the chain already loses (225 / 1134 at the shell zero end, 977 at the foot: chain+hw), so the
foot costs nothing held. Held is the best held number on file for any relay (parent 17.77, freek 20.50, the lead 22.38).
T5 dump: `verify/underpass-bridge-relay-4r/held_perpose.json`. Contact depth sum held 172.99 mm (pose minima).

## Verdict

4-JOINT PASS ON THE BENCH, by 0.01: frozen exact Bench(110,360) chain-only gate **13.74 (score 95.00)**, held **16.64**,
0 jams, 0 passive translations, complexity 53.0 (the parent's 52.5 record - the bump goes, the posterior foot comes).
Not a lead (4 joints), and the pass is hostage to one pose: the posterior foot at 466. The physically open item is the
cantilever root (243 N.mm into the arm band) - if the root cannot be made rigid, the design falls back to option (i),
which the torso at 119 kills (envsel 16.31).

## Next (the loop)

1. Verifier: re-run the claim from `verify/underpass-bridge-relay-4r/pick.json` (frozen rl_fix 81.307, hiE 49.0) and the
   held bench; T5 dumps are on file; read the 2 mm crown-set reading and the E envelope table on both benches.
2. Move the foot off 466 (side feet outside the T-nut flange's s band, or a foot beside the shell band in s; the plain
   inboard foot collides with the flange at rest): re-select on envsel, then one claim - the 466 contact is the whole
   hardware price (13.74 -> 13.21 if it clears).
3. Rigid root: model the arm-band anchor plate as metal and price the band compliance (tip drop vs the 1.2 mm clearance).
4. Cliff probes owed: delta + 1.5 (the parent's bracket cliff), shell +0.5 mm.

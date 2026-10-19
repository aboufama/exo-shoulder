# conecut-h2facet-knuckle-3r - hub 2 skin-side facet on the lead's frozen chain

Round 15 (main re-launch), lens C (conecut-sidestep-metal: tangent-plane metal moves on a frozen chain). Status: in work.

## Deeper-version answers (written first, before the model)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Make each cut ONE machining
   operation that a shop can quote: the bottom-edge cut is a 45-deg chamfer run by a chamfer mill along a sector of
   the edge (sector ends = the cutter's run-out, sampled as metal), the upper cut is a true PLANAR flat (one end-mill
   pass), not the spec's "r' = min(r, 10 - f)" cylindrical pocket with stepped sector faces - a flat of depth f has a
   natural half-width acos((10 - f)/10) (19.9 deg at f 0.6), no steps and less metal removed for the same clearance
   at its centre. (b) Sample the cut as a SOLID (face, top edge on the unchanged wall, wall above, bottom disc to
   r 10 - c, flat face and its two edges) at <= 0.5 mm spacing - the judge showed the min sits on the chamfer's top
   edge, which a sample move never sees. (c) Keep the uncut cylinder for part-vs-part collisions (a cut removes metal,
   so it can only add clearance: conservative) and say so. (d) Keep every frozen-chain coordinate bit-identical to the
   lead so any change in the bench is attributable to the cut alone (control = c 0, f 0 must reproduce the lead).
   (e) Price the wall over the MR117 OD 11 bearing (r 5.5): wall >= 3.0 means c, f <= 1.5.
2. **Rawest material.** The posed skin of the exact bench (CB.Bench(110,360) with CB_EXACT=1: the signed distance to
   the posed body mesh per pose), the lead's verified per-pose dump
   (docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json) and the judge's per-part binder dump at the
   six guard poses 139 / 203 / 205 / 237 / 264 / 316 (sample index, depth, skin gradient), not the round summaries.
3. **Methods and tools.** The lead's model loaded unchanged (docs/concepts/models/conecut-knee-knuckle-3r.py, its
   frozen claim protocol), a subclass that edits only hub 2's samples after the metal synthesis, exact signed-distance
   reads at the guard poses per config (fast: only six poses), a coarse grid + CMA (tools/concept_cma.py) on
   Bench(60,160) fast for the convergence gate, the frozen exact Bench(110,360) once, the held-out bench paired
   against the lead (tools/alignment_paired.py), kit density check (tools/sample_density.py).
4. **What, other than me, shows the number is right.** The exact bench itself, the round's verifier, the alignment
   auditor's T1 / T5 / probe checks, and a red-team pose list: 203 (the guard: >= 0.15 mm at +0.1 / +0.2 probes),
   205 (stays a contact: depth only), 237 / 264 (horn / crank: the cut cannot reach them on this chain), 316 (link 2:
   not hub 2), 139 (link 2 under K self-motion: unchanged by a hub-2 cut).

## What was built

`docs/concepts/models/conecut-h2facet-knuckle-3r.py` loads the verified lead (conecut-knee-knuckle-3r, its best_params)
unchanged and edits only hub 2's samples after the metal synthesis (FTModel._rod_metal -> apply_facet):

- **Bottom-edge chamfer** c x 45 deg over |az - (142.8 + daz)| <= hw (judge's frame e = unit(u2 x [0.3, 0.5, 0.8]); 142.8
  = ring c10 sample 17, pose 203's binder). Cone face r = 10 - c + z, z in [0, c]; run-out end faces sampled.
- **Upper flat**: a PLANAR flat of depth fd, normal at az 124 + dazf (264's hub-2 binders c12 / c13 samples 15-16), from
  the crown down to z0 with a 45-deg run-out below z0 (no ledge). Spec correction: the spec's "r' = min(r, 10 - f)" is a
  cylindrical pocket with stepped sector faces; a flat is one end-mill pass, removes less metal for the same centre
  clearance and has no steps (half-width acos((10 - fd)/10) = 19.9 deg at fd 0.6).
- **Sampled as a solid** (judge's rule): hub 2's contact-only rings lose every sample inside the cut, the in-band bottom
  disc keeps its 80 samples (5-9 clipped radially onto the cone: S6 equal count), and a dense contact-only solid is added
  in the cut sectors +- 6 deg (wall 0.5 mm x 1 deg, disc and crown bands, cone face, the chamfer's TOP EDGE on the
  unchanged wall, end faces, flat face; 2400-2700 points, ~4 pts / mm2). `dense 0` (sample move only) is reported to
  show why: at c 1.0 it reads 203 = 1.068 mm, the solid reads 0.877.
- **Collisions** keep the UNCUT hub-2 cylinder (a cut only removes metal: conservative).
- Build limits: wall over the MR117 OD 11 bore >= 3.0 needs c, fd <= 1.5; chosen c 1.4 (wall 3.1: 0.1 mm machining
  margin over the rule floor). The chamfer stays under z 1.4 (link 1b's lower plate band F+0..3.0; the member interface
  and any stop groove at F+3..3.15 untouched); the flat's run-out ends at z0 - fd = 3.9 (above the plate band).
  Notch clearance to lowarm-kstop's short-arm plate notch (az 66-95, judge's frame): 142.8 - 40 - 95 = 7.8 deg.
  Mass removed ~0.13 g (Ti-6Al-4V). Complexity +0 (a cut on an existing made part): 18.5 on the lead.

## Results (all exact unless marked)

**Claim protocol (the lead's: fit Bench(60,160) fast, shape frozen, worn exact Bench(110,360)), best config c 1.4, hw 40,
daz 0, fd 0.6, dazf 0, z0 4.5, dense 1:**

| | lead (verified dump) | h2facet |
|---|---|---|
| gap (plain) | 18.28 | **18.28** (score 93.35): reach 0.7278 (262/360), ib14 0.9012, ib10 0.5739, follow 1.0, 4 contacts |
| near1 (metal < 1 mm = contact) | 19.92 | **19.38** (203 leaves the 1-mm shell) |
| near2 | 34.84 | 34.84 (203 sits at 1.12: still in the 1-2 mm shell; shell count 30 -> 31) |
| +0.1 / +0.2 / +0.35 mm probe | 18.83 / 18.83 / 19.37 | 18.83 / 18.83 / **18.83** (only 139, link 2 at 0.072, is left under 1 mm) |
| pose 203 (guard) | 0.263 (c10 ring) | **1.122** (chamfer top edge), rigid disc 0.716 -> 1.380 |
| T5 contact depth 205 / 237 / 264 / 316 | -4.28 / -8.93 / -5.80 / -1.235 (sum 20.25) | -3.90 / -8.93 / -5.80 / -1.23 (sum 19.86) |
| overhead (elev >= 140) taken | 8 / 28 | 8 / 28 |

21 poses changed their lowest metal, all up (hub-2 chamfer) except 234: 1.556 -> 1.506 (the dense wall sampling, a
measurement change of -0.05 mm, still >= 1.5). No take, no contact and no in-band sample changed (clip nib identical).

**Search benches (the convergence gate).** 122 configurations (47 coarse + 3 CMA starts x 25, one at sigma 0.8): every one
reads Bench(60,160) fast plain 12.5 / near1 13.66 and envh (60 clips + 210 fresh env poses) 17.57 / near1 22.24, min
metal 0.44 mm. Gate: gain 0 over the second half, 0 over the last third, top-5 spread 0 - passed, because no pose of
either search bench binds on hub 2's skin-side edge. The cut is invisible to the search benches by construction; its
value is read on the exact guard poses (below), where it is linear and needs no search.

**203 vs c (lead chain, hw 35-40, daz 0, solid):** c 0 / 0.3 / 0.5 / 0.75 / 1.0 / 1.25 / 1.4 / 1.5 -> 0.263 / 0.447 /
0.570 / 0.723 / 0.877 / 1.030 / 1.122 / 1.184 mm (0.614 mm per mm, = the judge's 0.571 / 0.878 at 0.5 / 1.0). The
pre-registered >= 0.35 holds from c 0.15. Sector: hw 25 with daz -10 drops to 0.543 (binder outside the sector); hw >= 35
is flat for |daz| <= 10.

**264 vs fd (hub-2 wall only; c 1.4 hw 40):** fd 0.3 / 0.45 / 0.6 at dazf 0, z0 4.5 -> +0.087 / +0.228 / +0.370 (from
-0.128 ring / -0.166 dense). z0 6.0 -> +0.325-0.335; z0 7.5 fails (-0.056: the skin also binds at z ~7); dazf +-5 ->
+0.13 / +0.24; dazf +-10 fails at fd 0.3-0.45. On the lead's chain 264 stays a contact through the horn lug (-5.80).

**Cell on lowarm-kstop's chain** (its own harness `wear(delta, 'bench')` loaded unchanged: cell A at F+3.9, pad deleted,
K stop A; dwell K = law + delta; worn on the exact guard poses; docs/concepts/sweeps/conecut-h2facet-knuckle-3r_lowarm-kstop-cell.json):

| c (hw 35-40) | 203 at delta 0 | 203 at e+ 0.264 (P5 worst) | 203 at e+ 0.363 (P0 worst) |
|---|---|---|---|
| 0 | 0.263 | 0.157 | 0.117 |
| 0.5 | 0.570 | 0.463 | 0.423 |
| 0.75 | 0.723 | 0.616 | 0.576 |
| 1.0 | 0.877 | 0.769 | 0.729 |
| 1.25 | 1.030 | 0.923 | 0.882 |
| 1.4 | 1.122 | 1.014 | 0.974 |

So c >= 0.5 clears kstop's 203 gate at every corner and at the +0.2 probe (0.423 - 0.2 = 0.223 >= 0.15). 264's hub-2 wall
on that chain with the flat (fd 0.6, z0 4.5): +0.370 / +0.290 / +0.258 at delta 0 / 0.264 / 0.363 (from -0.13..-0.28), but
264's OTHER binder (hub K, -1.169 / -0.999 / -0.935) is untouched: the flat is necessary, not sufficient, for 264 -
lowarm-kphase-notch must remove the hub-K part. 205 stays a contact on both chains (needs 4.85 mm of radial cut: into the
MR117 bore).

## Red team (own)

- **Optimistic number?** The sample-move reading (dense 0) is +0.19 mm optimistic at c 1.0 (1.068 vs 0.877): the solid is
  the claim. The dense wall is a measurement change: the dense control (c 0) reads 205 -4.291 (vs -4.28), 264's hub-2
  wall -0.166 (vs -0.128) and pose 234 -0.05 mm; no take or contact moves.
- **Point that pinches:** after the cut 203's binder is the chamfer's top edge (r 10, z 1.4, az 143.8) at 1.122 mm; the
  next part at 203 is 3.75 mm away. With the lead's T3 K play (0.23 deg, ~0.4 mm/deg at this edge) 203 keeps ~1.03 mm.
- **Pose that jams:** none added - collisions use the uncut cylinder (conservative), no joint, stop or range changes.
- **Build:** wall 3.1 mm over the MR117 bore at c 1.4 (rule floor 3.0); 5-axis chamfer mill on link 1b's lower plate
  edge; the flat is one end-mill pass on the housing (z 3.9 -> 12.25). No new part, body or joint.
- **What it does not do:** no take on the lead's plain BENCH gap (it is never claimed as a lead on its own).

## Held out (never searched, selected or tuned on; c / hw / fd chosen on the bench guard poses)

Frozen held-out wear (952 ws + 202 clip): **22.16** vs the lead's 22.38 (-0.22): reach 0.6933 (660 / 952), ib14 0.900,
ib10 0.5726, follow 1.0, 13 contacts (lead 14). The one discordant pose is held ws 447 (plane 0, elev 90, axial 30 - the
neighbour of bench 203 at axial 45): a hub-2 bottom-edge contact on the lead (-0.207 mm), taken with the chamfer at
0.697 mm. All 45 held poses whose metal changed moved UP; none moved down. Paired bootstrap vs the lead
(tools/alignment_paired.py, 4000 resamples within kind): held diff -0.22, CI90 [-0.66, 0.00], P(better) 0.644; bench diff
0.00; pooled bench + held 21.08 vs 21.24 (-0.16, CI90 [-0.47, 0.00], P 0.645). The held gain is the mechanism working as
designed (the binder region around elev 90 / axial 30-45 is a hub-2 edge contact), not noise: one pose, one sign.
Kit density (tools/sample_density.py measure): same flags as the lead (roller 4.5x, L1a 0.33x - parts this cut does not
touch); hub 2 1.044x (lead 1.003x), so the lead's kit-density correction (+0.05 held) applies to both.

## Verdict and what next

SCREENED as a zero-complexity enabler. On the lead it ties the plain bench gap (18.28), improves held (22.16 vs 22.38),
near1 (19.38 vs 19.92), the +0.35 probe (18.83 vs 19.37) and T5 depth (19.86 vs 20.25). It is a candidate replacement for
the lead's hub 2 in the gen CAD (one chamfer + one flat on an existing Ti housing) once a verifier re-measures it; the
CI tie rule (bench tie, held P 0.64) is the user's open question. Next, in order: (1) conecut-l2jog + this facet as the
probe-hardened lead cell (only 139 is left under 1 mm; with 139 lifted >= 0.35 the +0.35 probe reads 18.28); (2)
lowarm-kstop takes the facet at c >= 0.5 (its 203 gate then passes at P5 / P0 and the +0.2 probe) - import
`apply_facet(M, P)` from this model, it works on any chain with `cyl['hub2']`; (3) lowarm-kphase-notch takes the flat
(fd 0.6, z0 <= 6, dazf 0 +- 5) and must still remove 264's hub-K binder (-0.94..-1.17).


## Verification (independent verifier, 2026-10-18 ~15:15 UTC)

**Verdict: VERIFIED at 18.28 on Bench(110,360) exact, frozen. That is a tie with the lead. The flat is modelled on the
wrong body. The buildable verified config is the chamfer alone.** The champion on the same bench and checks is 75.94
(the risley-turret verifier's reference, the same one the lead's verifier uses).

Harness: `docs/concepts/verify/conecut-h2facet-knuckle-3r.py`. It runs the lead's verifier
(`docs/concepts/verify/conecut-knee-knuckle-3r.py`) unchanged on the claim's model module (CCModel = FTModel). Checks:
cam closure in the world, pressure angles with friction, K sense, own-state th margin, the J3 own-angle stop (C1 / C2),
equal-strap in-band (C4), and the per-pose dump.

| | bench (110 clips + 360 ws) | held (202 + 952) |
|---|---|---|
| claim (c 1.4, hw 40, fd 0.6, z0 4.5) | **18.28**: reach 0.7278 (262), ib14 0.9012, ib10 0.5739, follow 1.0, 4 contacts, near1 19.38, overhead 8/28 | **22.16**: reach 0.6933 (660), ib14 0.900, 13 contacts, overhead 18/71 |
| chamfer only (fd 0) | 18.28, identical per pose (0 readings changed) | 22.16, identical per pose (447 taken at 0.697) |
| checks | closure 0.0 mm, 0 failing poses, th margin min 5.181, wrong sense 0, equal-strap gap 18.67 | th margin min 5.006, 0 failing, equal-strap 22.68 |

The per-pose dumps reproduce the claim's dumps bit for bit (max |diff| 0 over 470 + 1154 poses). The chamfer-only dumps
are on file at `docs/alignment/remeasure/conecut-h2facet-knuckle-3r+chamferonly_{bench,held}_perpose.json`.

What I checked and found:

1. **DOF: unchanged.** 3 active joints (J1, J2, J3). K is slaved by the drive and never read. The knee pins are passive
   rotations outside the count. 0 passive translations, no gears, pulleys or cables. A cut adds no joint.
2. **The chamfer is on the right body and sampled honestly.** Member 7 is link 1b, which sits at level 0 at J2 (the lower
   member). So the bottom-edge chamfer (z 0..1.4) lies in link 1b's lower plate (F+0..3.0) and is framed correctly. Under
   the plate there is the integral O7 pin, not a bearing bore. The MR117 pair sits in link 2's boss above U0 3.15, so the
   3.1 mm "wall over the bore" figure is conservative. Link 1b's bar leaves hub 2 at az ~355-25, outside the 102.8-182.8
   sector, so the chamfer does not cut a link root. The cut removed 17 of hub 2's 160 ring samples (c10-c13) and no
   sample of any other part. It added 3011 dense solid samples. The in-band disc kept its 80 samples, 6 of them clipped.
   The crank, roller and horn never come within the cut's azimuth windows. Link 2's bar comes no closer than 1.83 mm to
   the chamfer zone (pose 211), passing above it.
3. **The flat is mis-framed.** The upper flat (z 3.9..12.25) is cut into the O20 v5 boss and the threaded cap. In the
   real stack both turn with the UPPER member at J2, which is link 2 (docs/HARDWARE.md, R6 groups). The model fixes the
   flat in link 1b's frame. J2's relative angle spans -14..+91 deg over the fit poses, so a real flat sweeps about 105 deg
   of azimuth in link 1b's frame. The claimed tolerance is +-5 deg. The cap also threads on and tightens at an
   uncontrolled azimuth, so the flat must be indexed or machined after assembly.
   - Consequence: on the lead's chain the flat is worth nothing. With fd 0, bench and held are identical pose for pose.
   - The 264 hub-2-wall table on lowarm-kstop's chain (+0.26..+0.37) must be re-read with the flat in link 2's frame
     (az_L2 = 124 - q2(264)) before lowarm-kstop or lowarm-kphase-notch imports it. It holds at most at 264's own q2.
4. **No bench artefact.** Every number is exact (CB_EXACT=1). Part-vs-part collisions keep the uncut cylinder, which
   is conservative. The search benches carry no hub-2 binder, as the claim says. No take, contact or in-band sample
   moved on the bench, and on held only pose 447 moved.
5. **Not a new leader.** The bench tie is exact: the same 262 takes and the same 4 contacts (205 at -3.90, 237 at -8.93,
   264 at -5.80, 316 at -1.23). The held gain of -0.22 rests on ONE pose (447): CI90 [-0.66, 0], P(better) 0.644.
   - On the plain verified gap the lead stands. Swapping this in on the held number is the user's CI tie rule.
   - As a CAD change on the lead's hub 2 at 0 cx, the chamfer alone is a strict improvement: 203 rises 0.263 -> 1.122 mm,
     near1 19.92 -> 19.38, the +0.35 probe 19.37 -> 18.83, and T5 20.25 -> 19.86.

Next: put the chamfer (c 1.4, hw 40, fd 0) on the lead's gen CAD hub 2, which costs 0 cx. Re-read the flat for the
lowarm cells in link 2's frame. Hand the chamfer-only dumps to the auditor's T5 check.

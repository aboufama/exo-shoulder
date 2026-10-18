# conecut-l2jog-knuckle-3r - link-2 mid-bar planform jog at pose 139 on the lead's frozen chain

Round 15 (main re-launch), lens C (conecut-sidestep-metal: tangent-plane metal moves on a frozen chain). Status: screened (bench probe hardener; held -0.07 through in-band).

## Deeper-version answers (written first, before the model)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Move the bar's SECTION rigidly:
   a planform jog is a profile cut, so every row across the 6 mm bar must get the same displacement at the same
   station along the bar. The spec's weight w(distance from sample 13) would give a row 6 mm across a smaller weight
   than the binder's row (a shear, not a jog), so the station here is the per-row arc length from the binder's normal
   plane. (b) Use the S of two tangent arcs (a cosine run-out), not linear run-outs with kinks, and report its radius.
   (c) Try the variant that cannot hurt the far side: a one-sided WAIST (the edge the bar leaves moves dl, the far edge
   stays), because the spec's main risk is the far side of a jog meeting the skin elsewhere. Price its narrowing
   against the 6 mm bar. (d) Measure, as a separate, labelled variant, a local through-thickness JOGGLE (dz), because
   the judge found 29 % of the proposer's gain came from that component: a press-brake joggle in 3 mm Ti is a real,
   quotable operation if its radius meets the 5 t = 15 mm rule. Its in-band cost is read, not assumed. (e) Keep every
   other coordinate of the frozen chain bit-identical so the control (dl 0) reproduces the lead exactly and any change
   is the jog's alone.
2. **Rawest material.** The posed skin of the exact bench (CB.Bench(110,360) with CB_EXACT=1: signed distance to the
   posed body mesh per pose), the lead's own fitted link-2 samples (4 rows x 31, member 2) and their per-pose world
   transforms, the lead's verified per-pose dump (docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json),
   the judge's binder dump (scratchpad lc/lead4.npz: link-2 sample 13 at 0.072 mm at pose 139), the env / envsel fresh
   envelope draws (tools/env_bench.py) and the held-out bench for the paired test only.
3. **Methods and tools.** The lead's model loaded unchanged (conecut-knee-knuckle-3r.py and its frozen claim
   protocol); a subclass that moves only link 2's samples after the fit (underside, mid strap, top contact set); a
   PCA frame of the bar at the binder; a scan harness that wears the frozen lead ONCE per bench and re-reads only link
   2 on the poses where it is within 4 mm of the skin (exact on Bench(110,360) / envsel / env, fast on Bench(60,160) /
   envh); coarse grid + local refinement for the convergence gate; the frozen exact Bench(110,360) once (collisions
   re-checked there); held paired vs the lead (tools/alignment_paired.py); tools/sample_density.py.
4. **What, other than me, shows the number is right.** The exact bench, the round's verifier, the alignment auditor
   (T1 shell points, the +0.1 / +0.2 mm probes, T5 depth) and a red-team pose list: 139 (the target), 316 (link-2 root,
   must stay untouched: the jog's weight there must be 0), 203 / 205 / 237 / 264 (other parts: unchanged by
   construction), and every pose where the jogged stretch's FAR side or the run-outs come within 1 mm of the skin on
   any bench (envsel, held).

## What was built

`docs/concepts/models/conecut-l2jog-knuckle-3r.py` loads the verified lead (conecut-knee-knuckle-3r at its best_params)
unchanged and moves only link 2's samples right after the lead's fit (JogModel.fit -> apply_jog), so the frozen claim
protocol copies the jogged shape:

- **Bar frame at the binder** (link_pts['L2'] sample 13, row 0 = the bar's edge row, 69.6 mm from GH, s = 0): PCA of
  the samples within 8 mm (sv 19.81 / 10.73 / 2.00) gives axis a, plate normal n (outward) and width w = n x a
  (+w from row 0 toward row 3). The bar is 5.9 mm wide (4 rows at ~1.95 mm), 3 mm thick, from hub 2's rim (station
  -28) to hub 3's rim (+40.8). Row tangents . lat stay within -0.05 .. -0.01 and the across-bar vector . lat >= 0.95
  over the whole jog span: the bar is straight in planform and arched in elevation (T . n goes +0.35 -> -0.5), so a
  constant width-direction jog IS a planform move (the along-bar slide artifact the judge flagged is <= 5 % here,
  0.08 mm at dl 1.6). The coarse 4-mm PCA I tried first suggested a planform turn past station +5; the row tangents
  show it was the PCA's noise (4 x 4 samples), not the bar.
- **Station** = per-row arc length from the row's crossing of the binder's normal plane: the section moves rigidly.
- **Profile**: flat over Lf, cosine run-outs over T (the S of two tangent arcs; planform S radius 2 T^2 / (pi^2 dl),
  5.0 mm at the pick - a laser / waterjet profile cut before bending, no bend).
- **Moved sets**: underside (scored, 124), mid strap (collisions), top contact set (contact-only, member 2, index 22).
- **Variants** (mine, not the spec's): ff < 1 = a one-sided WAIST (the far edge moves ff dl, the bar narrows by
  (1 - ff) dl); dz > 0 = a local press-brake JOGGLE through the thickness, capped at bend radius 2 T^2 / (pi^2 dz)
  >= 15 mm (5 t).
- **Span rule** (spec: "the root stretch that binds radially at 316 is not touched"): link 2's root stretch at r_J2
  13.5 - 19.4 mm sits at stations -22.2 .. -16.3, so the moved span is clamped to stations >= -15 (and <= 38.8, 2 mm
  inside hub 3's rim). Without it the search drove the span to -29 (onto hub 2's rim: the bar would leave its hub) and
  the joggle made 316 shallower (-1.235 -> -0.92) - a radial root lift, which round 13 measured dead.

## Scan harness (and one measurement error I made and fixed)

`scan` wears the lead's frozen chain ONCE per bench (cached), then re-reads link 2 for every configuration with one
distance call per pose for all configurations. First version re-read only poses where link 2 is within 4 mm of the skin:
exact for contact, probes and near-touch, but NOT for in-band (2-14 mm per sample over clip frames moves wherever a jogged
sample sits near 14 mm). The frozen claim of the first pick exposed it: ib14 0.9012 -> 0.9000 on the bench and 0.9007 ->
0.8995 on Bench(60,160) where the scan had read "unchanged". The fast benches (Bench(60,160), envh) are now re-read on
every scored pose (L2JOG_NEAR default 1e9 there): the scan then reproduces the frozen fit exactly (12.55 / 0.8995 at the
pick). The exact benches keep the 4-mm re-read (contact / probes / near-touch) and their in-band comes from the frozen
protocol only. The sweep file's Bench(60,160) numbers are the corrected all-pose reads.

## Results

Search bench = envh (Bench(60,160)'s 60 fit clips + 210 fresh envelope poses, fast cache, no held-out pose), objective
near1 + plain - 0.5 min(link-2 min over taken, 1) (the near-touch objective with a margin tie-break). Selection bench =
envsel (exact, 110 clips + 360 fresh poses), lexicographic (plain, +0.2 probe, near1), then the search objective.
Pre-registered lever size: pose 139 >= 0.4 mm plain (so >= 0.2 after the +0.2 probe).

540 configurations: 10 direction checks + 290 coarse (structured + Latin) + 3 ES runs of 5 x 16 (2 starts at sigma 0.3
of the box, 1 restart at sigma 0.8). Convergence gate on the search objective (envh, all-pose re-read): gain 0.008 score
points over the second half, 0.008 over the last third, top-5 spread 0.013 - passed (the objective is nearly flat: one
envh pose is all the lever can move).

**Direction (exact, 139):** +w (toward the bar's far rows) is the lever; -w makes 139 and envh 150 worse. Planform
dl 0.5 / 1.0 / 1.5 at Lf 20, T 10: 139 = 0.280 / 0.487 / 0.716 mm (the judge's planform-only 0.487 / 0.716 reproduced to
the digit).
The opposite sign (-w) drives the bar INTO the bump: 139 = -0.199 / -0.484 / -0.811 (a new contact). A joggle alone
(dz 0.5, no planform) reads 139 = 0.501 (0.86 mm per mm: the binder's radial gradient 0.77 plus the arch).

**Selection.** 255 of 540 configurations meet the pre-registered 139 >= 0.4. Envsel ties for 182 of them at (plain 24.14
= the lead, +0.2 probe 24.70 = the lead, near1 28.02 vs the lead's 28.58: envsel 259 leaves the 1-mm shell, 0.605 ->
1.0-1.16). The search objective (with exact in-band) then picks the WAIST (k512): dl 1.6, Lf 20, T 9.69, cs +4.69,
rot +3.39, ff 0 (far edge kept), dz 0. The best spec-faithful pure jog (ff 1, dz 0) is k355: dl 1.6, Lf 20, T 6.28,
cs +1.28, rot -2.36 (k234, dl 1.37, is 0.006 better on the search objective - a tie). The best joggle is k333 (dz 0.54).

**Claim protocol (the lead's: fit Bench(60,160) fast, shape frozen, worn exact Bench(110,360) once; collisions
re-checked):**

| | lead | jog k355 (spec) | waist k512 (pick) |
|---|---|---|---|
| fit Bench(60,160) plain / near1 / ib14 | 12.50 / 13.66 / 0.9007 | 12.55 / 13.71 / 0.8995 | **12.50 / 13.66 / 0.9003** |
| frozen exact Bench(110,360) gap | 18.28 | 18.28 | **18.28** (score 93.35) |
| reach / follow / contacts / overhead | 0.7278 / 1.0 / 4 / 8 of 28 | same | same (205 / 237 / 264 / 316 unchanged: -4.28 / -8.93 / -5.80 / -1.23) |
| ib14 / ib10 | 0.9012 / 0.5739 | 0.9000 / 0.5737 | 0.9005 / 0.5737 |
| pose 139 (link 2) | 0.072 | 0.726 | **0.602** |
| +0.1 / +0.2 / +0.35 mm probe | 18.83 / 18.83 / 19.37 | 18.28 / 18.28 / 18.83 | **18.28 / 18.28 / 18.83** |
| near1 / near2 | 19.92 / 34.84 | 19.92 / 34.84 | 19.92 / 34.84 (203 at 0.263 and 379 at 0.616 stay under 1 mm) |
| lowest metal over taken | 0.072 (139) | 0.26 (203 wall) | 0.26 (203 wall); then 139 0.60, 379 0.62 |
| J3 stop margin (taken) | 2.7 deg | 2.7 | 2.7 |

So the lever does exactly what it was meant to: it removes the lead's only +0.1 / +0.2 mm probe flip (18.83 -> 18.28)
with no take and no new contact. What is left under 0.35 mm is pose 203 (hub 2's skin-side ring, 0.263): the h2facet
chamfer's job (conecut-h2facet: 203 -> 1.122). Predicted, not measured as one cell: together the +0.35 probe reads
18.28 and 379 (0.616, not link 2) is the lowest metal; the two edits touch disjoint samples (hub 2's skin-side ring vs
link 2's mid-bar), so their bench effects should add.

## Held out (never searched, selected or tuned on; both cells worn once, frozen, after the pick)

| held (952 ws + 202 clip, exact) | lead | jog k355 (spec) | waist k512 (pick) |
|---|---|---|---|
| gap | 22.38 | 22.49 (+0.11) | **22.45 (+0.07)** |
| ib14 / ib10 | 0.9000 / 0.5726 | 0.8989 / 0.5723 | 0.8993 / 0.5723 |
| reach / follow / contacts | 0.6922 / 1.0 / 14 | same 14 | same 14 |
| near1 | 25.23 | 25.56 | 25.30 |
| link-2 contacts 224 / 225 / 252 (139's neighbours: plane -90 / -75, elev 60, axial 105-120) | -3.49 / -5.51 / -1.60 | -2.43 / -4.55 / -1.06 | -2.43 / -4.57 / **-0.71** |
| held 898 (jog's far side) | 1.67 | **0.95** (into the 1-mm shell) | 1.67 (unchanged) |

Both cells lose on held, and the whole loss is IN-BAND: the lead's held ib14 sits exactly on the 0.900 target, so the
0.0007 (waist) / 0.0011 (jog) of samples the lever pushes past 14 mm over the 202 held clip frames cost 0.07 / 0.11 gap
points one for one. No take, no new contact, no pose changes status on held (deterministic difference; the per-pose
paired test has no discordant pose, so its CI is the in-band term alone). The jog's far side also pulls held 898 under
1 mm (near1 +0.33); the waist does not (its far edge stays put) - the deeper-version idea (c) measured.

**In-band price per lever (Bench(60,160) clips, all-pose re-read):** planform jog dl 0.5 / 1.0 / 1.5 -> ib14 0.9004 /
0.9001 / 0.8996 (139 0.28 / 0.49 / 0.72); waist dl 1.0 / 1.6 -> 0.9006 / 0.9003 (139 0.46 / 0.60); joggle dz 0.3 / 0.5
-> 0.8991 / 0.8982 (139 0.33 / 0.47): the joggle is a radial lift and pays in-band ~1:1, as round 13 measured for root
lifts. The waist is the cheapest lever per mm of clearance; it is still not free.

## Red team (own)

- **Optimistic number?** My first scan read in-band only on poses within 4 mm of link 2 and called it "unchanged": wrong
  by 0.0012 on the bench (fixed, see the harness section; every number above is the frozen protocol's or the
  all-pose re-read). The search objective on envh sees ONE movable pose (envh 150, a link-2 contact -0.53 -> taken
  +0.38 at dl 1.6), so the ES drives dl to the box edge; the claim bench's 139 lever and the held in-band cost are the
  real story, not the envh take.
- **Point that pinches:** after the waist, 139's binder is still link 2 (0.602 mm, row 0 at the waist's flat); the
  lowest metal over the taken bench poses is hub 2's skin-side ring at 203 (0.263). K play: the judge measured 139's
  link-2 binder unchanged (0.072) under +-0.912 deg of K play on lowarm cell A; not re-measured here on the waist.
- **Pose that binds on the far side:** envsel 458 (0.18 on the lead) went to -0.014 (a new contact, envsel +0.56) with a
  20 mm jog centred on the binder and no span rule; with the span rule it is untouched. Held 898 is the jog's far-side
  binder (0.95); the waist leaves it at 1.67. Bench 345 / envsel 461 come to ~1.2-1.3 mm under the jog (still > 1).
- **Pose that jams:** none added - the frozen runs re-checked part pairs with the jogged strap: why = fold 88, contact
  4, parts 0 on the bench; fold 260, contact 14, parts 0 held (= the lead).
- **Build:** the waist narrows the 5.9 mm bar to 4.3 mm over 20 mm (+ 9.7 mm cosine run-outs), cut into the flat profile
  before bending (laser / waterjet; planform S radius >= 5 mm, no bend). Out-of-plane section modulus 8.85 -> 6.45 mm3
  (-27 %): 155 MPa per N m in Ti-6Al-4V (yield ~880 MPa) - fine for the unpowered MVP1, but it is the weakest station
  of link 2 now and must be re-checked when link 2 carries the J3 stop's 155 N per N m (lead WATCH M5). Kit density
  (tools/sample_density.py measure): L2 0.919x, the same flags as the lead (roller 4.5x, L1a 0.33x).
- **What it does not do:** no take on any claim bench; it is not a lead change and it LOSES 0.07 on held.

## Verdict and what next

SCREENED, as a measured negative for the hardening role: the link-2 planform lever removes the lead's only +0.1 /
+0.2 mm probe flip (bench 18.83 -> 18.28, plain 18.28 tie, 139 0.072 -> 0.602 with the waist / 0.726 with the spec's
jog), but every link-2 planform or radial move at 139 pushes clip samples past 14 mm, and the lead's held in-band sits on
0.900 exactly, so held reads 22.45 (waist) / 22.49 (jog) vs 22.38. The lever is a trade, not a free hardener: about
-0.0004 ib14 per mm of edge move for +0.3 mm at 139.

New knowledge: (1) 139 is the edge of a held LINK-2 contact cluster (224 / 225 / 252: plane -90..-75, elev 60, axial
105-120, -1.6 .. -5.5 mm); the waist gains 0.9 - 1.06 mm there (252 -1.60 -> -0.71, 0.71 mm short of a take; 224 / 225 need 2.4 / 4.6 mm
more). (2) The lead's held ib14 = 0.9000: any metal move that adds clearance anywhere on links costs
held points unless it is paid back in-band elsewhere - the auditor's 'in-band margin' is ZERO on held. (3) The waist
(one-sided narrowing) beats the jog on every bench at equal clearance at the target, because the far edge does not
move into new skin (held 898, envsel 458).

Next, in order: (a) do NOT stack this lever on the lead cell unless an in-band source is found (e.g. pair it with a
lowered stretch elsewhere on link 2 that pulls samples back under 14 mm on the clips); (b) the h2facet chamfer (held
-0.22) is the hub-2 half of the hardened cell and has no in-band cost; (c) lowarm-kstop's chain carries the same link-2
binder at 139 (0.072): hand it the waist only if its held ib14 has margin (> 0.9007).

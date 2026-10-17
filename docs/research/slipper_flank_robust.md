# slipper-nose-knuckle-3r flank robustness (2026-10-17): the crank-side cliff is a synthesis artefact, not a build risk; no beta step is due; the phase of K is the dimension to hold

Self-measured, local only (at most 2 niced processes, $0 farm). Subject: the verified lead slipper-nose-knuckle-3r
(frozen exact Bench(110,360) 18.49, held out 23.45, min th 5.181 / 5.006) and the two measurements that disagreed:
* the final polish (`slipper-nose-knuckle-3r_final_polish.md`, issue 3): a re-synthesised flank goes immovable at
  r_c -0.2 mm, g -0.02 or beta -1 deg (crank PA over 38.03, stroke 0);
* the mechanism red team (`slipper_mechanism_redteam.md`): the built flank is fine, but the held-out fold margin 5.006
  is razor thin, so it asks for a +0.75 deg K lead.

Data and scripts: `docs/research/slipper_flank_robust/`.

## Verdict

**A. The cliff is not physical. It is a property of the cam SYNTHESIS (a design-space knife edge), not of the built
part.** With the verified flank held fixed and the crank built with each error, nothing jams and no stroke is lost at
any error tested, including the ones that zero the re-synthesised drive:

| as-built error | re-synthesis (polish) | as built on the verified flank (this note) |
|---|---|---|
| r_c -0.2 mm | crank PA 38.2 > 38.03, stroke 0 | crank PA 34.8 (margin 3.2), stroke 49.65, K error -0.09..+0.32 deg |
| g -0.02 | crank PA 38.5, stroke 0 | PA unchanged (29.5 / 36.5), stroke 50.17, K +0.38 deg at dK 45 |
| beta -1 deg | crank PA 38.8, stroke 0 | crank PA 23.6, stroke 48.77, K -0.99 deg (a lag) |

The physical crank PA climbs gradually as r_c shrinks (about 1.6 deg per -0.1 mm, no cliff): it keeps the 2-deg margin
to -0.25 mm and reaches its 38.03 cap between -0.4 and -0.5 mm. **So nothing in A blocks the CAD.** The polish's 6-neighbour
`robust` check measures whether a NEIGHBOURING DESIGN synthesises. It does not measure whether the built part tolerates
errors, and it should not be read as a buildability test (an auditor topic: the "knife edge" is in the design space).

**What the build does need: the phase of K.** Every as-built error appears as a K offset. A lag moves the held-out fold
margin by about 0.08 deg per deg of K. Without a built-in lead, a K lag of only ~0.07 deg puts a held-out pose under 5. So
these dimensions need a tolerance (per tolerance unit: K error / held-out min th):

| dimension | K per unit | +-0.02 mm | +-0.05 mm | cap / stroke |
|---|---|---|---|---|
| nose angular position about K's axis (beta, 0.268 mm per deg at r_c 15.37) | 1.0 deg per deg = 3.7 deg per mm | +-0.075 deg | +-0.19 deg | PA and stroke unaffected |
| crank pivot position across the arm (e2) | 3.6 deg per mm | +-0.07 deg | +-0.18 deg (held 4.989, 1 pose under 5) | unaffected |
| crank pivot position along the arm (e1) | 0.9 deg per mm | +-0.02 deg | +-0.05 deg | crank PA 14.5-31.1 |
| lobe lift scale (g; 0.84 % = 0.055 mm on the 6.5 mm follower arm) | 0.38 deg at dK 45 per 0.02 of g | about +-0.14 deg | about +-0.35 deg | PA unchanged |
| nose radius from K's axis (r_c) | <= 0.32 deg at -0.2 mm (early stroke) | +-0.04 deg | +-0.09 deg | **2-deg crank margin to -0.25 mm, cap at -0.4..-0.5 mm** |

* The stacked worst LAG at +-0.05 mm (r_c -0.05, beta -0.25 deg, pivot e2 -0.05, g +0.02) is **-0.83 deg of K**:
  - fold re-solve: held min th 4.936 (2 poses under 5), bench 5.110;
  - claimed on held out through the verifier's harness with that law: **gap 23.67 (+0.22, 2 poses lost to the fold
    rule)**, contact unchanged.
* The same stack at +-0.02 mm is -0.35 deg (held 4.979, 1 pose under 5).
* The red team's systematic lag (arm compliance, follower clearance, wear: -0.42 to -0.53 deg) comes on top.
* **Tolerances for the CAD:**
  - nose hole and crank pivot: true position +-0.02 mm, in the same setup as the follower pin. The red team already
    asks for +-5 um on the crank bores, which is inside this.
  - lobe profile and lobe phase: +-0.02 mm.
  - r_c (the nose's radius from K's axis): +-0.1 mm is plenty (with the bores held as above it is set to +-0.02 anyway).
  - none of these is a stroke or jam risk. They are a fold-margin (th) risk, and the K lead (C) pays for them.

**B. The beta step: no grid beta passes the pre-registered rule. The CAD keeps the verified flank.**
* Rule committed before any claim (commit 0761f77, `slipper_flank_robust/prereg.json`): the closest beta to -176.684
  whose flank passes 6 / 6 neighbours AND keeps >= 2 deg to both caps at mu 0.087.
* Stepping beta toward -171 moves the margin from the crank side to the horn side:
  - crank PA 29.5 -> 23.7 / 19.9 / 17.2 / 15.2 / 13.8;
  - horn PA 35.8 -> 36.3 / 36.8 / 37.2 / 37.7 / 37.1 (effective at mu 0.087 + 4.97).
* The lead's horn margin is 2.29. Every step reads 1.73 or less.
* -174.684 to -172.684 pass 6 / 6 neighbours but miss the horn's 2 deg. -175.684 and -171.684 fail a neighbour as well.
* All tie on the gap. Verified protocol, unpriced:
  - 18.48 / 18.46 / 18.44 / 18.43 / 18.70 against the lead's 18.48 (dump reading of 18.49);
  - paired CI90 of the gain [-0.0, +0.07] for -175.684 to -172.684.
* -174.684 (the closest flank that passes 6 / 6), report only:
  - held out unpriced 23.43 (lead 23.45);
  - priced and bench-priced claims: see the B table below.
* No flank gives margin on both sides; the A result shows the crank side does not need it.
* `recommended.json` therefore records the verified flank unchanged, plus the K lead and the tolerances.

**C. The +0.75 deg K lead costs nothing and buys a thin margin. It cannot reach 5.5.** Claimed through the verifier's
harness, with the lead law on the worn bench:
* bench 18.46 (paired gain +0.02, CI [-0.0, +0.03]), min th 5.244;
* held out 23.43 (lead 23.45), min th **5.068**, with 11 held-out poses under 5.5;
* contact poses unchanged (2 bench, 10 held), held depth 46.28 mm (lead 46.12), max 9.06;
* horn PA taken 36.2 held (+0.15): 41.2 effective at mu 0.087, 43.0 at mu 0.12 (on the 43 rule).

The margin rises 0.084 deg per deg of K, so **5.006 -> 5.5 would need about +6 deg of lead**. That is not available: the
horn cap and the a1max window bind first. The 5.5 reading is the stops' job: the polish's priced reading moves smlo
+0.5, held out 24.63. With the +0.75 lead, the stacked +-0.05 mm lag of A is held to 5.0. The claimed held-out min th is
in the B/C table below.

## What the gen-7 CAD should change

1. **Keep the verified flank** (beta -176.684, r_c 15.3739, g 2.3934; or the red team's r 1.25 re-cut of it). Do not
   step beta: it trades the crank margin, which the built part does not need, for the horn margin, which it does.
2. **Build in the +0.75 deg K lead**: lobe-ring dowel phase +0.35 deg of q2, stop B at q2 -15.47 (the red team's spec).
   Measured cost: 0.00 / -0.02 gap.
3. **Tolerances on the K phase, not on the crank PA:**
   - nose hole and crank pivot: true position +-0.02 mm, one setup;
   - lobe profile: +-0.02 mm;
   - r_c: +-0.1 mm.
   - Add a drawing note: "K phase at the onset +0.75 +-0.3 deg, measured at assembly (shim the lobe-ring dowel)".
     The stacked +-0.05 mm lag (-0.83 deg) is the case the lead is for.
4. Nothing in A is a BLOCKER.

## A. Method (`asbuilt.py`, `asbuilt.json`, `asbuilt_extra.json`)

* **The nominal flank.**
  - Rebuilt from the verified config's extracted geometry (`slipper_mechanism/geo_bench.npz`, the claim's model worn
    unchanged) with the model's own spherical-cam construction, on a 0.005-deg K grid.
  - Only the BUILT flank exists, dK 0 -> 51.75. The conjugate continuation before rest is not built and is not used.
  - It reproduces the model: K = g phi exactly, crank PA 29.50 at rest, fold re-solve 5.180 bench / 5.008 held (red
    team 5.180 / 5.008). With +0.75 offset it reads 5.246, and the claim reads 5.244.
* **The as-built crank.** The nose centre is moved radially (r_c) or about K's axis (beta), the pivot and the whole crank
  are moved +-0.05 mm (e1 along the arm, e2 across it), or the lobe is cut for g' = g +- 0.02.
* **The solve.** For each crank angle phi from -0.9 deg to 22 deg (the -0.9 is the float on the follower's 0.1 mm dwell
  gap), K = the smallest K >= 0 at which the nose clears the fixed flank: the spring closes K onto the nose, with a signed
  clearance on the mid shell.
  - Contact normal: from the nose centre to the closest flank point.
  - PA: the crank and horn velocity at the real contact.
  - The K error over the law is K(|dK_law| / g') - |dK_law|.
  - The per-pose th re-solve is drive.py's `fold_rows` with that error in place of a constant offset.
* **What the solve found in every case:**
  - K at rest stays 0 (on stop A) in every case up to beta +2. At beta +3 the nose holds K 0.87 off stop A.
  - The contact always stays on the built flank, and both members always push (n . v > 0).
  - A lag case has a small dead band at the onset (beta -1: 0.45 deg of crank).
* **Gap with the as-built law (`klaw_claim.py`).** `tools/slipper_env_polish.py claim` (the verifier's
  `H.frozen_wear`, flood on, per-pose dump) is run with the slaved law replaced on the WORN bench only. The fit bench
  keeps the nominal law, because the CAD shape is cut from it. Forced poses are re-solved exactly on the shifted law; the
  model's own fold rule drops a pose under the margin.

Full table (taken stroke K <= 47.05; PA margins to 38.03 crank, to 43 - atan(mu) horn at mu 0.087 / 0.12; fold = min th
(poses under 5)):

| case | K error min / max (deg) | K rest | stroke at stop B | crank PA (margin) | horn PA (margin 0.087 / 0.12) | bench th | held th |
|---|---|---|---|---|---|---|---|
| nominal | 0 / 0 | 0 | 49.75 | 29.5 (+8.5) | 36.5 (+1.5 / -0.4) | 5.180 (0) | 5.008 (0) |
| r_c -0.2 mm | -0.09 / +0.32 | 0 | 49.65 | 34.8 (+3.2) | 35.8 (+2.2 / +0.4) | 5.173 (0) | 4.997 (1) |
| r_c -0.1 mm | -0.05 / +0.17 | 0 | 49.70 | 32.7 (+5.3) | 36.1 (+1.9 / +0.0) | 5.177 (0) | 5.000 (0) |
| r_c -0.05 mm | -0.03 / +0.09 | 0 | 49.72 | 31.5 (+6.6) | 36.4 (+1.7 / -0.2) | 5.178 (0) | 5.002 (0) |
| r_c +0.05 mm | -0.05 / +0.03 | 0 | 49.78 | 13.0 (+25.0) | 36.6 (+1.4 / -0.5) | 5.181 (0) | 5.009 (0) |
| r_c +0.1 mm | -0.08 / +0.05 | 0 | 49.81 | 7.6 (+30.4) | 36.9 (+1.2 / -0.7) | 5.187 (0) | 5.010 (0) |
| r_c +0.2 mm | -0.09 / +0.11 | 0 | 49.87 | 7.2 (+30.8) | 37.2 (+0.8 / -1.0) | 5.190 (0) | 5.017 (0) |
| r_c -0.3 / -0.4 / -0.5 / -1.0 mm | up to +0.45 / +0.57 / +0.67 / +1.12 | 0 | 49.4-49.6 | 36.3 / 37.9 / **39.0** / 43.6 | 35.4 / 35.0 / 34.6 / 32.6 | 5.15-5.17 | 4.98-4.99 (1) |
| beta -0.25 deg | -0.25 / 0 | 0 | 49.51 | 26.9 (+11.1) | 36.5 (+1.5 / -0.4) | 5.160 (0) | 4.984 (1) |
| beta -0.5 deg | -0.50 / 0 | 0 | 49.26 | 25.6 | 36.5 | 5.141 (0) | 4.965 (2) |
| beta -1 deg | -0.99 / 0 | 0 | 48.77 | 23.6 (+14.4) | 36.6 (+1.5 / -0.4) | 5.101 (0) | 4.926 (3) |
| beta +0.25 / +1 deg | +0.25 / +1.0 | 0 | 49.99 / 50.72 | 29.7 / 30.1 | 36.5 | 5.200 / 5.264 | 5.027 / 5.086 |
| pivot e1 -0.05 / +0.05 mm | +0.08 / -0.05 | 0 | 49.80 / 49.70 | 31.1 / 14.5 | 36.4 / 36.6 | 5.183 / 5.177 | 5.011 / 5.004 |
| pivot e2 -0.05 / +0.05 mm | -0.18 / +0.18 | 0 | 49.57 / 49.93 | 29.0 / 28.2 | 36.5 | 5.166 / 5.194 | 4.989 (1) / 5.022 |
| g -0.02 / +0.02 (lobe) | +0.38 / -0.38 at dK 45 | 0 | 50.17 / 49.34 | 29.5 | 36.5 | 5.214 / 5.150 | 5.036 / 4.975 (2) |
| stack lag +-0.05 mm (r_c -0.05, beta -0.25, e2 -0.05, g +0.02) | -0.83 / 0 | 0 | 48.89 | 31.4 | 36.3 | 5.110 (0) | 4.936 (2) |
| stack lag +-0.02 mm (r_c -0.02, beta -0.075, e2 -0.02, g +0.01) | -0.35 / 0 | 0 | 49.39 | 30.3 | 36.4 | 5.150 (0) | 4.979 (1) |
| stack lead +-0.05 mm | +0.38 / +0.84 | 0 | 50.62 | 13.1 | 36.7 (+1.3 / -0.6) | 5.250 | 5.076 |

* The horn margin at mu 0.12 is under 0 for the nominal itself, read over K <= 47.05: 36.5 + 6.84 = 43.3. That is the
  red team's "43 rule reached at mu 0.122-0.127". No as-built error moves the horn by more than +0.7.
* **Why the synthesis is a knife edge and the part is not.**
  - At rest the nose sits near the crank / link-1a relative pole: relative sliding 0.66 mm/rad.
  - The synthesised contact normal is perpendicular to that tiny relative velocity, so a small change of a DESIGN
    parameter swings it, and with it the synthesised crank PA (2.3 deg per -0.05 mm of r_c, 4.5 deg per -0.01 of g).
    The re-synthesised flank then starts above the cap at dK 0.
  - The built flank has a fixed normal at every point. An as-built nose error only slides the contact along the
    conformal rest pocket: r_c -0.2 mm moves the contact a few degrees of K along it, PA 34.8.
  - The horn's normal velocity (m_horn 13.7-15.7 mm) fixes K to first order: dK = -(n . delta) / m_horn, the red team's
    0.04 deg per 10 um.

## B. The beta step (pre-registered, `prereg.json`; `robust.json`, `claim_b*_*.json`, `paired.json`)

| beta | robust 6 / 6 (min stroke) | verified u: gap (paired gain, CI90) | crank / horn PA taken | horn eff. mu 0.087 (margin) / mu 0.12 | R2 | held u | bench p / held p |
|---|---|---|---|---|---|---|---|
| -176.684 (lead) | 3 / 6 fail (cliff) | 18.49 (row) | 29.5 / 35.8 | 40.7 (+2.29) / 42.6 | - | 23.45 | 19.05 / 24.63 (polish) |
| -175.684 | 5 / 6 (g -0.05: crank cliff) | 18.48 (+0.01, [-0.0, +0.02]) | 23.7 / 36.3 | 41.3 (+1.73) / 43.1 | fail | - | - |
| **-174.684** (closest 6 / 6) | **6 / 6 (45.0)** | 18.46 (+0.02, [-0.0, +0.03]) | 19.9 / 36.8 | 41.8 (+1.23) / 43.6 | **fail (horn)** | **23.43** | B_P174 |
| -173.684 | 6 / 6 (44.0) | 18.44 (+0.05, [-0.0, +0.07]) | 17.2 / 37.2 | 42.2 (+0.83) / 44.0 | fail | - | - |
| -172.684 | 6 / 6 (43.2) | 18.43 (+0.05, [-0.0, +0.07]) | 15.2 / 37.7 | 42.7 (+0.33) / 44.5 | fail | - | - |
| -171.684 | 5 / 6 (g +0.05 short) | 18.70 (-0.22, [-0.79, +0.08]) | 13.8 / 37.1 | 42.1 (+0.93) / 43.9 | fail | - | - |

* The pre-registered pick does not exist: no beta passes R1 and R2. By the rule, no flank change is recommended.
* All the steps tie on the gap. Beta is nearly free for the gap; it is a transmission trade.
* The verified protocol's taken crank PA falls 5.8 deg per deg of beta near the lead, and the horn rises ~0.5 per deg.
* Only -174.684 got held-out and priced claims, report only (time box). The other held-out and priced columns were not
  run.

## C. The K lead (`claim_klead075_*`, `claim_stacklag*_held_u.*`)

| claim (unpriced, margin 5) | gap | paired gain vs lead (CI90) | min th | poses th < 5.5 | contact poses / depth sum (max) | horn PA taken |
|---|---|---|---|---|---|---|
| lead, bench (row) | 18.49 | - | 5.181 | 2 | 2 / 14.75 (9.01) | 35.8 |
| **+0.75 lead, bench** | **18.46** | +0.02 ([-0.0, +0.03]) | **5.244** | 2 | 2 / 14.75 (9.01) | 35.9 |
| lead, held out (row) | 23.45 | - | 5.006 | - | 10 / 46.12 (9.05) | 36.05 |
| **+0.75 lead, held out** | **23.43** | C_HELD_CI | **5.068** | 11 | 10 / 46.28 (9.06) | 36.2 |
| stack lag -0.83 deg (+-0.05 mm), no lead, held out | 23.67 | STACK0_CI | 5.009 (2 poses dropped by the fold rule) | - | 10 / 45.98 | 35.8 |
| stack lag -0.83 deg + the +0.75 lead, held out | STACK75 | STACK75_CI | STACK75_TH | - | STACK75_C | - |

## Red team

* **Is the solver right?** It reproduces the model's own construction at zero error (K = g phi to 1e-15, crank PA 29.50,
  fold 5.180 / 5.008). The fold re-solve matches the claim to 0.002 (5.246 vs 5.244 bench, 5.068 vs 5.068 held).
* **The negative-K conjugate continuation.** It crosses the nose at rest; that is why only the built flank (dK >= 0) is
  modelled. If the CAD extends the rest pocket before dK 0 as a continuing tangent arc, that run-in must stay clear of
  the nose's float path (phi down to -0.9 deg): a CAD check.
* **Spherical approximation.** Contact is read on the mid shell (radial ruled flank). A radial nose-position error does
  not matter for a radial-ruled flank. The +-1.5 mm band's taper (0.14-2.74 deg) is the red team's 4-axis-EDM item and
  is unchanged.
* **Not modelled here:**
  - lobe form and follower-pin errors, other than as a g scale and a phase. They are pure K phase, like beta, and the
    red team's +-0.125 deg per 5 um covers them;
  - hub tilt;
  - wear. The red team's systematic lag (-0.42 to -0.53 deg) adds to every lag above.
* **Optimistic number?** A says "no jam". The physical crank cap is still reached at r_c -0.4..-0.5 mm, so the +-0.1 mm
  r_c tolerance is a 3-4x factor, not unlimited.
* **The pre-registered R2 was strict on the horn.** The lead itself only just passes it (2.29). A rule at 1.5 deg would
  pick -175.684, which fails 6 / 6. A rule at 1.0 would pick -174.684 (1.23): tie on the gap, horn 43.6 effective at
  mu 0.12. Either way the pick changes nothing that A shows the part needs.

## Files

* `prereg.json`: the rule, committed before any claim (0761f77).
* `asbuilt.py`, `asbuilt.json`, `asbuilt_extra.json`, `asbuilt_extra.log`: A.
* `klaw_claim.py`: the claim with an as-built K law on the worn bench (A, C).
* `robust.json` / `robust.log`: R1 for the lead and the 5 betas.
* `claim_*.json` (+ `_perpose.json`, `.log`): every claim.
* `paired.py` / `paired.json`: paired bootstraps against the lead's own dumps.
* `recommended.json`: the CAD flank recommendation.

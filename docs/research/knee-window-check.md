# Knee-window singularity check: minarc BDp vs the pin knee H1 (2026-10-16 ~12:35 UTC)

**Answer: no. BDp's verified lead over H1 does not depend on its narrower knee window.**

BDp refitted at H1's knee window (ang_min 30.46 instead of 24.95, everything else the same) measures:
- **19.06** on the bench, identical to BDp's own 19.06;
- **23.24** held out, also identical.

H1 measures 27.20 / 31.39 in the same harness. The lead stays at 8.14 / 8.15 points.

On the bench, BDp's knee never opens past 149.48 deg on any taken pose. That is 30.52 deg from the straight singular
posture, inside H1's window. The extra window is used by exactly one held-out workspace pose (154.0 deg).

This is the opposite of the pin-knee GPU polish (F7), whose whole held-out gain was the knee window
(docs/concepts/skin-normal-3r-pin-knee.md, "Verification (massive GPU polish)").

## Harness

The verified BDp claim harness is `docs/concepts/models/minarc-stop-knuckle-4r-kitrule-wear.py`. It imports the
re-measure verifier `docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py` unchanged. This check drove it through
`docs/research/knee_window_check.py` (new), with the settings below:
- fit on Bench(60,160) fast, frozen;
- worn on Bench(110,360) EXACT, and on the disjoint held-out bench (1154 poses);
- `CB_FOLD_MARGIN=5`, O20 hubs;
- the continuity flood fill run per config (`conn_*.json`) and applied to the wear.

The script adds one thing to the harness's extra checks: a per-pose record of the knee's interior angle at pin a (180 =
straight, 0 = folded), J3's lever on the knee force `dist(C, ab) = lE sin(ang)`, and GH's lever. The taken set is still
the harness's own.

Farm: exo-cpu1, 6 jobs, 195 s wall, about $0.03. Raw outputs are in `docs/research/knee_window/`. Both baselines reproduce
to the digit: BDp 19.06 / 23.24 (the lenses' rule reading) and H1 27.20 / 31.39.

These runs put the J2 stops at the rule's nominal 5.0 deg. The verified 19.54 / 24.18 prices the stops at 5.5 deg with
K's stop B at dK 34.47, a separate +0.48 / +0.94. Taken poses at margin 5.5 are a subset of those at 5.0, so the knee
angles below bound that case too. This is inferred, not run.

## (1) How close the knee comes to its singular postures (taken poses, after continuity)

| run | ang_min (window edge) | taken | knee angle range | min distance to straight | min distance to folded | poses past H1's edge (149.54) | max amplification 1/sin(ang) | J3 lever min (mm) |
|---|---|---|---|---|---|---|---|---|
| BDp bench | 24.95 (155.05) | 371 | 68.82 - 149.48 | **30.52** | 68.82 | 0 | 1.97 | 32.8 |
| BDp held out | 24.95 (155.05) | 858 | 68.82 - 154.01 | **25.99** | 68.82 | **1** (workspace) | 2.28 | 28.3 |
| H1 bench | 30.46 (149.54) | 343 | 103.02 - 147.30 | **32.70** | 103.02 | 0 | 1.85 | 32.2 |
| H1 held out | 30.46 (149.54) | 785 | 103.02 - 147.32 | **32.68** | 103.02 | 0 | 1.85 | 32.2 |
| F7 (GPU polish, reference) held out | 21.93 (158.07) | - | 93.4 - 156.1 | 23.9 | 93.4 | yes (its whole gain) | 2.47 | - |

What this shows:
- **On the bench**, BDp's knee comes 2.2 deg closer to straight than H1's (30.5 against 32.7). It stays inside H1's
  window, and no taken pose sits within 3 deg of BDp's own edge.
- **Held out**, one workspace pose takes the knee to 154.0 deg (26.0 deg from straight). Every other held-out pose is
  at 143.4 deg or less.
- **Folded side.** BDp's knee works through a wider range than H1's (it reaches 68.8 deg), but it stays 69 deg from the
  folded posture.
- **J3's lever** never drops below 28 mm (H1: 32 mm). The GH-to-C lever ratio is 0.21 - 1.38 (H1: 0.67 - 1.23), so J3
  never loses its drive.
- **The fit clips at 10 fps** keep BDp's knee at 68.8 - 132.6 deg, 47.4 deg from straight. H1's clips reach 148.2 deg,
  31.8 deg from straight. On everyday motion, BDp's knee runs further from straight than H1's.

## (2) BDp refitted with ang_min = 30.46 (H1's window), everything else the same

| config | fit (Bench(60,160) fast) | **bench** (exact, connected) | reach / in-band14 / contact | near-touch | **held out** | held reach / contact | held near-touch | continuity |
|---|---|---|---|---|---|---|---|---|
| BDp (ang_min 24.95) | 12.25 | **19.06** (score 93.07) | 0.725 / 0.8951 / 0.0107 | 26.15 | **23.24** | 0.6891 / 0.0138 | 28.31 | 1041/1041 grid nodes, 0 dropped |
| BDp30 (ang_min 30.46) | 12.25 | **19.06** (score 93.07) | 0.725 / 0.8951 / 0.0107 | 26.15 | **23.24** | 0.6880 / 0.0127 | 28.09 | 1036/1036, 0 dropped |
| H1 (same harness) | 23.64 | 27.20 | 0.6583 / 0.8953 / 0.0256 | 31.75 | 31.39 | 0.6197 / 0.0273 | 34.66 | 971/971, 0 dropped |
| **BDp30 lead over H1** | | **8.14** | | 5.60 | **8.15** | | 6.57 | |

What this shows:
- **Fit and bench are identical to the digit.** No fit-bench or wear-bench pose needs the knee past 149.54 deg, so the
  narrower window changes nothing in the fit or on the bench.
- **Held out, the narrower window drops the one pose at 154.0 deg.** Reach goes 0.6891 to 0.6880 and contact goes
  0.0138 to 0.0127, so the gap stays 23.24 and near-touch even improves (28.31 to 28.09).
- **On the full 1432-pose grid**, continuity loses 5 of 1041 kinematic nodes (static reach 0.727 to 0.7235). None of the
  5 is a Bench(110,360) workspace pose: 265 of 265 stay connected.

## (3) Feel near the knee's straight posture (quasi-static Jacobian, the method of `fold_stop_feel.py`)

Setup:
- The six fit clips at 10 fps run through each frozen design, with joint rates from finite differences.
- Coulomb friction is 3 N.mm per O20 joint and per knee pin.
- The spherical part of the cuff moment is `A^-T (T sgn qdot)`; the rows use the K axis when K is forced.
- The knee pins add their dissipated power.
- Cuff force = moment / |GH to pin b|.

The planar knee dyad (C, pin a, pin b) turns drift into pin rates amplified by 1/sin(ang). Its J3 lever is lE sin(ang).

| | BDp | H1 |
|---|---|---|
| cuff force from all friction on the clips, max / p99 / median (N) | 0.29 / 0.27 / 0.11 | 0.19 / 0.19 / 0.09 |
| of which the knee pins, max / median (N) | 0.09 / 0.011 | 0.04 / 0.005 |
| knee drift per rad of arm, max (mm) | 38.3 | 17.5 |
| knee-pin rate per arm rate, max | 3.6 | 1.6 |
| worst bound with the knee AT its straight-side edge, at the clips' fastest drift (N) | **0.18** | 0.08 |
| amplification 1/sin at the window edge | 2.37 (155.05 deg) | 1.97 (149.54 deg) |
| J3 lever at the edge / min over taken poses (mm) | 27.3 / 28.3 (held) | 30.2 / 32.2 |
| knee force per N.m of J3 torque (MVP2), at the edge (N) | 36.7 | 33.1 |
| min transmission angle over taken poses (deg) | 26.0 held out, 30.5 bench | 32.7 |
| knee branch flips, clips / continuity grid | 0 / 0 (one branch sign) | 0 / 0 |
| jam (friction circles: 2 x 0.5 mm iglidur pins + 0.02 mm J3 ball pair) needs the knee within (deg of straight) | 0.90 | 0.98 |

Findings:
- **Friction.** The knee adds at most 0.09 N at the cuff on real motion. Even at its straight-side edge it would add
  at most 0.18 N. That is 1.2x H1's amplification at H1's edge, on a 2.2x larger drift.
  - BDp's knee works harder: it carries the knuckle-relieved drift, and its pin rates are about 2.3x H1's.
  - It does that work far from straight, so the friction it adds is a tenth of a newton.
- **No jam.** A two-force knee link jams J3 only if its force line passes within the friction circles, which needs the
  knee within 0.9 deg of straight. BDp's window keeps it at least 25 deg off, and the taken poses keep it at least 26.
- **No toggle on any taken pose or clip.** The knee never changes branch, and continuity holds with one branch sign.
  - **The red-team point**: a toggle needs the knee to pass through straight, which only happens outside the taken
    set, when the arm drives the drift past the dyad's reach.
  - The model counts those poses as lost ("slide": 10 bench, 24 held out). It does not stop the real knee from going
    there.
  - So the build needs a **physical knee stop** at the window edge: a shoulder on the knee link against the E boss, at
    180 - ang_min. It keeps the knee on its branch. Without it, a strong push could snap the knee through straight onto
    the other assembly branch.
  - The stop can sit at H1's 149.5 deg for free on the bench and at 0.0 cost held out (table 2). That gives 5.5 deg more
    margin to straight than BDp's 155.05 edge: amplification at the stop 1.97 instead of 2.37, J3 lever 32.8 mm instead
    of 27.3 mm.
- **MVP2 note.** At the edge, a powered J3 needs 36.7 N of knee force per N.m (H1: 33.1). The transmission angle of 26
  deg on the one held-out pose is below the usual 30 - 40 deg linkage guideline. Drawing the stop at 149.5 deg gives
  30.5 deg.

## Verdict

1. BDp's verified lead (19.54 bench / 24.18 held out against H1's 27.20 / 31.39) **does not depend on the knee window**.
   At H1's ang_min, BDp measures the same 19.06 / 23.24 at the rule's nominal stops. The F7 effect is absent.
2. BDp's knee sits 30.5 deg from straight on the bench and 26.0 deg held out (one pose), against H1's 32.7. Its
   everyday clips stay 47 deg off straight, against H1's 32.
3. Feel: friction at the cuff is 0.29 N at most (H1 0.19), the knee's share is 0.09 N, and there is no jam or toggle
   in the taken set.
4. **Build condition for the gen-4 CAD:**
   - draw ang_min = 30.46, as a physical knee stop at 149.5 deg (a shoulder on the knee link against the E boss);
   - do not leave the window as a model-only limit.

   It costs nothing measured, buys 5.5 deg of singularity margin, and removes the toggle path.
5. The cross-fit polish of BDp should hold ang_min >= 30 unless the user rules otherwise. That repeats the GPU-polish
   verifier's recommendation, which now holds for BDp at no cost.

Files:
- `docs/research/knee_window_check.py`
- `docs/research/knee_window/` (`conn_*.json`, `wear_{BDp,BDp30,H1}_{bench,held}.json` + logs, `stats.jsonl`,
  `feel_{BDp,H1}_{bench,held}.json`)

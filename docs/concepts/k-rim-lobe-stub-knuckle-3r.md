# k-rim-lobe-stub-knuckle-3r: inverse direct pair (lobe sector on link 1a around K, MR52 roller on a stub of link 2)

Round 7, pick 2 (docs/concepts/round7_ideation.md note E). Model: docs/concepts/models/k-rim-lobe-stub-knuckle-3r.py.
Sweeps: docs/concepts/sweeps/k-rim-lobe-stub-knuckle-3r.json. Row: docs/concepts/rows/k-rim-lobe-stub-knuckle-3r.json.

## Deeper-version answers (written before the model)

1. **What a top mechanism designer would do that the spec does not ask.** Treat the roller-lobe pair as a spherical cam
   (every axis through GH, roller axis radial, flank a radial ruled surface) and synthesise it exactly in 3-D, not on the
   planar approximation the 43.9-deg pressure angle came from. Check the pair's whole q2 sweep, not only the law: the
   stub is rigid with link 2, so in state A it swings ~110 deg about u2 (the Geneva tail's killer was exactly that sweep
   cone). Ask where the three stacked layers at K go (link 1b, lobe, stub): a lobe stacked over link 1b puts the stub 3
   layers up; a lobe at link 1a's own level BESIDE link 1b keeps it low but needs the roller on a post. Put both
   embodiments in the search instead of choosing by hand.
2. **Rawest material.** The posed skin itself through the bench's signed-distance field (every metal sample of the
   lobe, roller, post and stub is skin-checked per pose), the 60 / 110 fit clips and the 160 / 360 workspace poses
   (tools/concept_bench.py), the winner's verified seats (rows/geneva-tail-knuckle-pinknee-3r.json), not the planar
   synthesis numbers of the proposal.
3. **Methods and tools.** Exact spherical contact law with per-t gates (pressure angle on K's velocity, pitch-curve
   geodesic curvature vs roller radius, lift-off on the self-motion curve, stub boss vs hub K), the kit-rule chain with
   the physical q2 stops (minarc-stop-knuckle-4r-kitrule.py via geneva-tail-knuckle-pinknee-3r.py), part-pair 3-D
   clearances at every bench pose, farm LHS then CMA-ES on the near-touch gap, frozen exact Bench(110,360).
4. **What, other than me, shows the number is right.** The bench (Bench(60,160) fast for the search, Bench(110,360)
   exact frozen for the claim), the independent verifier harness the lead runs on the winner family, and the red-team
   pose list below (hub K clearance over the whole q2 range, roller vs lobe in state A, LOBE vs link 1b).

## Mechanism

Scapula handler -> J1 (active, O20) -> link 1a [+ lobe sector on K's housing] -> K (passive O20, clock spring + stop A;
slaved, never read) -> link 1b -> J2 (active, O20; folded dowel + stop-B dowel) -> link 2 [+ stub, O2 pin, MR52ZZ roller]
-> J3 (active, O20) -> member 3 -> pin knee (2 passive pins) -> pad -> BOTTOM. 3 active, 3 passive rotations, 0 passive
translations, one closed loop through the unilateral roller-lobe contact (spring-closed). No gears, pulleys or cables.

Law: past the stretched q2 onset, dK = sp kK t (t = q2 travel). Gates per t: th rising (rate <= 3.45), pressure angle
<= 45 deg (exact: angle between the lobe-side pitch normal and the lobe point's velocity), convex pitch radius >= rr + 1,
no lift-off, K <= stop B, stub-end boss >= 1 mm off hub K's O20 rim (nominal; collide checks every pose in 3-D).

## Measurements (Bench(60,160) fast unless stated)

Law-only reproduction (winner model, tail 0, kK 1.0, smhi 20, a1max 50): **13.76** (reach 0.775, ib 0.887, contact 0) -
the judge's number to the digit.

Law synthesis (exact 3-D, winner seats): the law is valid on two stub branches, a0 ~ 144-156 deg and ~ 204-216 deg (K sits
at 162 deg in link 2's frame at the onset); e.g. L_stub 22, a0 156, kK 1.0: pa max 38.8 deg, K reaches stop B (31.3 deg),
stub boss >= 4.9 mm off hub K's rim. The proposer's a0 168 has no valid prefix (pa > 45 at t = 0): the stub points almost
straight at K there, so K's velocity at the roller is near-perpendicular to the push.

First metal fits (hand configs):

| config | gap | reach | ib14 | contact | lost to | note |
|---|---|---|---|---|---|---|
| lobe over link 1b, L 22, a0 156 | 147.3 | 0.31 | 0.80 | 0.071 | parts 114 (LOBE-LT) | stub ramp dipped into the lobe -> stub kept flat |
| same, flat stub, tip-lift drop | 111.9 | 0.51 | 0.78 | 0.019 | parts 78 | lobe 0 % in band (18.9 mm), stub 17 mm |
| over, L 24, a0 216, kK 0.8 | 76.97 | 0.52 | 0.86 | 0.130 | parts 34, skin 19 | |
| lobe BESIDE link 1b (link 1a level), L 26, a0 216, kK 0.8 | 97.87 | 0.50 | 0.91 | 0.239 | skin 38, parts 21 | lobe 100 % in band (8.7 mm) |

Two structural findings already:

- **Stacked over link 1b** the lobe is >= link 1b + 4 mm and the stub >= lobe + 4 mm: three layers at K, the lobe sits
  12-19 mm off the skin and the stub 16-18 mm (0-37 % in band). The roller tip's skin need over the state-A sweep
  (q2 76-91 deg, the stub swinging about u2) lifted the whole lobe 6.5 mm until those poses were dropped.
- **Beside link 1b** the lobe is in band (100 %), but the roller on its post sweeps the skin at link 1a's level with
  link 2 (state A), and the poses whose roller would need lifting are lost (skin 38) - the Geneva tail's sweep cone again,
  on a shorter radius.

## Search (farm, Bench(60,160) fast, near-touch objective)

- LHS 256 over L_stub 18-28, a0 140-224, kK 0.7-1.3, smhi 14-28, a1max 48-60, bk1 29-34, bk2 37-41, tip_tol 0-6,
  lobe_w 3-5 and the lobe level (over / beside link 1b): best 38.34. 144 of 256 have a valid law. Best over link 1b
  38.34, best beside 57.2.
- Two local-search generations of 128 around the top 6 (sigma 8 % and 4 % of each range): 37.17, then **36.82**.
- **Best:** L_stub 24.49 (28.1 mm physical at the roller radius), a0 146.2, kK 0.825, smhi 22.1, a1max 48.0, bk1 33.19,
  bk2 39.93, tip_tol 3.1, lobe_w 3.5, lobe over link 1b.
  - Numbers: **36.82 near-touch, 30.79 plain**; reach 0.694, follow 0.933, ib14 0.827, ib10 0.567, contact 0.012, min
    metal 0.56 mm. Overhead: 2 of 12 workspace poses taken (fold 8, slide 2).
  - Law: pa max 35.3 deg, K opens 24.6 deg to stop B, th_max 101.5. The stub boss passes 6.6 mm off hub K's rim.
- Convergence gate (score points): 2nd-half gain 0.553 (< 1, met); last-third gain 0.549 (< 0.5, NOT met, by 0.05);
  top-5 spread 0.138 (< 3, met). Status therefore stays **screened**, not dead.
- **Kill gate (fast near-touch <= 15.5): failed by 21 gap points.**

## Red team

- **The optimistic number was the spec's:** the law-only 13.76 has no drive metal. With honest metal the pair costs
  about 23 points, five times the rod drive's 4.74.
- **Where the points go (best config):**
  - In band: lobe 0 % (45 samples, median 19.6 mm), stub 11 % (32, 21.6 mm), roller 17 % (9, 19.7 mm). Hub 3 0.68,
    L2 0.78.
  - Lost poses: fold 38, slide 4, skin 2, and parts 9. All 9 parts losses are ROL-LOBE: in state A the stub swings back
    across the lobe sector on clip frames, so follow falls to 0.933.
- **Pose that jams:** the clip frames where q2 sweeps back past the onset while K is still on stop A. The roller's
  state-A path crosses the lobe's web or band. The lobe would need a relief notch there, which shortens the law.
- **Point that pinches:** min metal 0.56 mm is on a taken pose, which is why near-touch (36.82) and plain (30.79)
  differ by 6 points.
- **Hub K (the lead's concern):** at the proposed a0 168 the law has no valid prefix (pa > 45 deg at t = 0). On the
  valid branch (a0 about 146) the boss clears hub K's rim by 6.6 mm in the measured run and by at least 4 mm nominally
  over q2's whole range. The 0.3 mm clash does not arise, but the law moves (kK 0.83, dK 24.6 against 31.3).

## Verdict and what it predicts

The inverse direct pair cannot beat the rod drive under these rules.

- The lobe must ride on link 1a at K.
- Link 1b leaves K exactly where the lobe has to point (toward J2). The lobe therefore sits one layer above link 1b, and
  the stub one layer above the lobe: three stacked layers, about 8 mm above link 1b's in-band level.
- Moving the lobe beside link 1b drops it into band. The roller then rides at link 1a's level, and its stub, rigid with
  link 2, sweeps the skin through state A.

New knowledge: **a slaving drive whose follower is rigid with link 2 pays for link 2's whole q2 sweep, at any radius, as
long as it must reach K's level.** This held at about 38 mm (the Geneva tail) and at 24-28 mm (this stub).

A direct pair that keeps the stub's sweep off the skin and out of a third layer has two candidate shapes:

- (a) the follower on a radius that never leaves link 1b's footprint (rim-lobe-arm, pick 1);
- (b) a lobe cut into link 1b's own strap, as a groove at link 1b's level.

The rod's out-of-band metal remains the cheapest measured drive (4.74 points).

## Verification (skeptic, 2026-10-16)

Harness: `docs/concepts/verify/k-rim-lobe-stub-knuckle-3r.py`. It loads the claim model unchanged. Result:
`docs/concepts/verify/k-rim-lobe-stub-knuckle-3r_corr_bench_frozen.json`.

What was checked:

- **Active DOF.** J1, J2 and J3 are active. K is slaved: the clock spring holds it on stop A in state A, and the law
  sets it while the roller is on the lobe. The two knee pins are closed by the cuff. That gives 3 active joints, 0
  passive translations and no undetermined coordinate.
- **Parts at real size.** The lobe is sampled every 1.5 x 1.5 mm, plus a 4 mm web to hub K. The MR52ZZ roller is O5;
  its boss is O6. The stub strap is 8 x 3. All of these are skin-checked.
- **Added check: lobe vs hub 1.** Never binding.
- **Added check: roller vs lobe inside the law.** The claim exempts this pair on law poses, so it was re-checked two ways:
  - geometrically over the whole law prefix (undercut -0.001 mm);
  - per pose, the roller centre against every lobe sample, at a tolerance of rr - 0.3 mm.

  Neither check removed a pose. A first per-pose check that sampled the roller rim against the lobe's back rows was an
  artefact: those rows sit exactly one sample half-thickness behind the flank. It was replaced.
- **Closure.** The largest residual is 0.015 deg.
- **Continuity flood fill.** All 131 taken law poses are connected on the full grid, and connected reach equals
  static reach.
- **Bench re-check.** The fit was reproduced exactly on Bench(60,160): 30.79 plain, 36.82 near-touch.

Frozen wear (no refit), exact path, Bench(110,360), with the corrected checks:

| | gap | reach | follow | ib14 | ib10 | contact | near-touch gap |
|---|---|---|---|---|---|---|---|
| claim, fit Bench(60,160) fast | 30.79 | 0.694 | 0.933 | 0.827 | 0.567 | 0.012 | 36.82 |
| **verified, Bench(110,360) exact frozen** | **44.79** | 0.622 | 0.873 | 0.826 | 0.566 | 0.018 | 53.51 |
| round-6 winner (rod), same protocol | 23.57 | 0.731 | 1.000 | 0.844 | 0.531 | 0.011 | - |
| champion spherical 3R, same code and checks | 66.97 | | | | | | |

**Where the poses go.** Lost: fold 105, parts 32 (all roller vs lobe in state A), slide 7, contact 6. Overhead
(elevation >= 140): 5 of 28 taken.

**Fast to frozen.** The design loses 14.0 points going from fast to frozen; the winner loses 6.8. Follow causes most of
it (0.933 -> 0.873): on clip frames in state A, the stub swings back across the lobe.

**Caveat.** The state-A roller-vs-lobe rule also charges a roller that is about to land on the flank onset. That makes
the rule slightly conservative, but it cannot close a 21-point deficit.

**Verdict: VERIFIED, not refuted** (v_gap 44.79, score 83.7, against the champion's 66.97). It is not a contender: it
sits 21.2 points behind the rod drive, and the claim's own conclusion (stub follower on link 2 = about 20+ points of
drive metal) stands.

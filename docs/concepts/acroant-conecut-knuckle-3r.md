# acroant-conecut-knuckle-3r - the lead with J1 slid forward on the acromion top

Round 105 pick 3 (lens B seat lever on the lead's coupled K). The verified lead conecut-knee-knuckle-3r (18.28 frozen exact
Bench(110,360), held 22.38) with only J1's seat moved forward (az1 +2.5..+12 deg at el1 67.90). J2's seat is re-solved so that
the dyad a1 37.552 / a2 57.218 stay the same. The K drive and the knee are re-fitted.

## Deeper-version answers (written first)

1. **What a top mechanism designer would do that the spec does not ask for.** Read the seat move as a change of where the
   fold sits in the arm's workspace, not as a metal-height tweak. The J1 ray moves 1.9-3.8 deg on the sphere. The fold
   window th is unchanged, but the arm direction at which th reaches the stretched wall moves. So every lost pose
   (fold 88, J3 stop 6, contact 4 on the lead) has to be attributed again pose by pose, and the move must turn more of
   them into takes than it costs. In-band surplus is worth 0 on the gap. Second, check what moving J1 does to the
   drive: the crank's pressure angle (PA) headroom (34.5 -> 14.3 deg at +10) is the only new resource. It can be spent
   on a longer K stroke (dK_lim), which is the stretched wall's own limiter (dK 52.6 of 57). A designer would spend it
   there: re-fit r_c / g / kK with the PA gate as a hard rule. Third, treat the 1-2 mm shell as a cost, not a free gain,
   and rank at the +0.1 / +0.2 mm tolerance probe. The lead's T1 watch is already 16.56 points there.
2. **Rawest material.** The posed skin itself: the bench's signed distance on the exact skin (CB_EXACT=1) on every pose
   of Bench(110,360) and of the held-out set, and the per-pose contact depth. Also the rest-pose skin under the J1 seat
   ray (OSN.seat samples the outermost skin along the ray), and the fit clips at 10 fps (q3' and the knee window,
   clip_check). Summaries in docs/ are not used as inputs; the per-pose bench dump is.
3. **Methods and tools.** The lead's own model code imported unchanged (docs/concepts/models/conecut-knee-knuckle-3r.py:
   the slipper-nose spherical cam synthesis per 0.25 deg of K, PA gate with friction, lift-off / cusp, O20 stacks, part
   pairs, the kit fold rule, the J3 own-angle stop). J2 is re-solved by least squares on the seat rays: the dyad
   constraint, same branch. The search is CMA-ES (near-touch 1 mm objective) on the Bench(60,160) fast cache. The env
   bench has no local fast cache and the farm is closed, so env search was not run (see Protocol). The pick is worn
   frozen on Bench(110,360) exact (CB_EXACT=1) and on the held-out bench, paired against the lead per pose
   (tools/alignment_paired.py).
4. **What shows the number is right, other than me.** The bench (an outside judge). The lead's verifier harness
   docs/concepts/verify/conecut-knee-knuckle-3r.py, which takes this row by its params (the seat move is three numbers).
   The paired per-pose comparison against the lead's dump. A red-team pose list: the proposer's new overhead contacts
   115 (15/135/-45) and 152 (60/165/-90), the lead's contacts 237 / 205 / 316 / 264, pose 203 (0.263 mm), and the ER
   binders 117 / 119 / 129.

## Verdict: DEAD (the pre-registered stop and kill)

- **The re-fit walks J1 back.** CMA-ES on envh used the 1 mm near-touch objective and 15 free parameters: d_az1, nine
  drive, four knee, the J3 stop and a1max. Both starts return d_az1 < 2.5, the pre-registered STOP:
  - from +2: 17.08 at d_az1 1.16;
  - from +5: 17.20 at d_az1 1.45.
- **The seat-only move at +5 is a tie that loses at the ranking reading.**
  - Frozen exact on Bench(110,360): 18.28, the same as the lead's 18.28 (paired 0.00, CI90 [-1.02, +0.56]).
  - Held out: 22.37 vs 22.38 (paired -0.01, CI90 [-1.10, +0.63]).
  - At the +0.2 mm probe it reads 19.37 against the lead's 18.83. Pose 203 drops to 0.138 mm, under the 0.15 mm kill line.
- **Every other point reads above 18.28.**
  - +2: 18.83, with 203 in contact.
  - The CMA best, frozen from its own envh fit: 19.66.

## Model

- `docs/concepts/models/acroant-conecut-knuckle-3r.py` imports the verified lead (`conecut-knee-knuckle-3r.py`) unchanged
  and adds one parameter, d_az1 (J1 azimuth; el1 stays 67.8974).
- J2's seat ray is re-solved on the lead's branch, so a1 37.552 / a2 57.218 hold exactly. The J3 seat is fixed at d3, and
  d2 = circ_int(d1, a1, d3, a2, branch).
- Checks:
  - d_az1 0 reproduces the lead's az2 / el2 (45.8211 / 41.0855).
  - +10 gives 51.7141 / 42.775, the spec's numbers.
- The th fold window and the K dyad are therefore the lead's. Only where the window sits in the arm's workspace changes,
  along with where the metal rides.
- Hooks:
  - `check` (Bench(60,160) fast, plus the +0.1 / +0.2 mm tolerance probe and the 1-2 mm shell count);
  - `frozen` / `held` (the lead's claim protocol; `ACRO_FIT=envh` freezes the shape from an envh fit instead);
  - `seats`, `viz`.
- `tools/alignment_paired.py dump` works through `PK`.
- Hardware and DOF are the lead's record: 3 active, 0 passive translations, 4 passive R, complexity 18.5. The seat move
  adds no part. At +5, J1 is 1.9 deg further along the acromion top, inside ruling 4.

## Step 0: what the proposer measured was not the verified lead

| d_az1 | Bench(60,160) fast plain / near1 / near2 | min metal | crank PA | dK_lim |
|---|---|---|---|---|
| 0 (the lead) | 12.50 / 13.66 / 18.80 | 0.20 | 32.4 | 50.0 |
| +1 | 12.78 / 12.78 / 17.64 | 1.06 | 26.6 | 49.5 |
| +2 | 13.12 / 13.12 / 18.28 | 1.13 | 25.7 | 49.2 |
| +3 / +4 | 13.12 / 13.12 / 20.62-21.80 | 1.2-1.3 | 25.1 / 24.4 | 49.2 |
| +5 | 12.50 / 12.50 / 19.97 | 1.33 | 23.6 | 49.2 |
| +6 | 13.04 / 13.04 / 18.86 | 1.37 | 22.7 | 49.0 |
| +7 .. +12 | 88-96 (drive fails) | - | 44-53 | 0 |

- The proposer's numbers (control 13.13; +10 14.73 / 15.90 / 24.49, crank PA 14.3, new contacts 115 / 152) reproduce
  exactly only with the module's default knee: lE 82 / lc 27 / phiE 3.8 / phib -96.6 / J3MIN -105
  (`conecut-knee-knuckle-3r.py check` with the +10 seats gives 14.73 / 15.90 / 24.49).
- On the verified lead row (lE 97.14, J3 stop -111.9 / 122.7):
  - the slipper drive fails beyond +6 (dK_lim 0);
  - 115 / 152 are taken at 2.9 / 4.7 mm and are not contacts.
- Lesson: step-0 probes must load the row's best_params, not the module defaults.

## Bench(60,160) cannot rank this lever; envh can

- **Bench(60,160) fast.** Every honest config reads 12.50. That is reach 0.775: the same 31 fold poses at every d_az1,
  with ib14 >= 0.90 and no contact. A 40-config CMA there (sigma 0.5 and 0.22) sat on that floor.
- **envh.** The search moved to envh: the 60 Bench(60,160) clip frames plus 210 fresh env workspace poses, on a fast
  cache, with no held-out pose. The model rebuilds tools/freek_env_polish.py's bench.

Seat-only scan on envh, at the lead's drive and knee (plain / near1):

| d_az1 | envh plain / near1 | reach | ib14 (fitted) | contacts |
|---|---|---|---|---|
| 0 | 18.54 / 19.47 | 0.7381 | 0.8903 | 3 |
| +1 | 17.30 / 18.24 | 0.7429 | 0.8978 | 3 |
| +2 | 17.24 / 18.18 | 0.7429 | 0.8984 | 3 |
| +3 | 17.76 / 18.69 | 0.7381 | 0.8981 | 3 |
| +4 | 19.11 / 19.11 | 0.7381 | 0.8846 | 3 |
| +5 | 19.19 / 19.19 | 0.7381 | 0.8838 | 3 |
| +6 | 19.67 / 19.67 | 0.7333 | 0.8928 | 5 |

- The in-band gain at +5 on Bench(60,160) (0.9007 -> 0.9068) is an artefact of the fit sample.
  - On envh the fitted in-band falls (0.890 -> 0.884), because more workspace poses lift the metal.
  - Worn frozen on Bench(110,360), the surplus reappears (0.9077), but it is worth 0 on the gap and it comes from metal
    in the 1-2 mm shell: near2 35.39 vs 34.84, and pose 203 at 0.138 mm. This is the judge's T1 reading, confirmed.

## Claims worn frozen (Bench(110,360) exact, CB_EXACT=1; lead dumps re-read through the same probe code)

| config | frozen exact | takes | contacts | near1 | +0.1 / +0.2 mm probe | 203 (mm) | held |
|---|---|---|---|---|---|---|---|
| lead (conecut-knee) | 18.28 | 262 | 4 | 19.92 | 18.83 / 18.83 | 0.263 | 22.38 (near1 25.23) |
| +5, lead drive / knee | **18.28** | 262 | 4 (205 -2.96, 237 -10.47, 264 -6.54, 316 -1.60) | 19.92 | 18.83 / **19.37** | **0.138** | **22.37** (near1 25.44) |
| +2, lead drive / knee | 18.83 | 261 | 5 (203 -0.14 new) | 20.46 | 19.37 / 19.37 | contact | - |
| CMA best k109 (d_az1 1.16), envh fit | 19.66 | 259 | 6 (139 -0.52, 203 -0.19 new) | 20.20 | 19.66 / 19.66 | contact | - |
| same k109, Bench(60,160) fit (lead protocol) | 86.67 | 132 | 4 | - | - | - | - |

- **+5 in detail.**
  - fold 89 / J3 stop 5 / contact 4 (the lead: 88 / 6 / 4). Moving J1 forward trades one J3-stopped pose for one fold pose.
  - J3 stop margin 0.84 deg (the lead's 2.7); held 0.74.
  - Overhead 8/28, the same as the lead.
  - Contact attribution is the lead's: hub 2 (205), crank / roller (237), hub K / horn (264), link 2 (316). 205 is
    shallower (-2.96 vs -4.28); 237 / 264 / 316 are deeper.
  - Held out: lead contacts 447 and 835 clear, and 679 (-5.62) is new. Overhead 534 / 607 / 683 / 755 are deeper by
    0.6-1.4 mm.
  - Paired vs the lead (tools/alignment_paired.py, 4000 boots): bench 0.00 [-1.02, +0.56] P 0.56; held -0.01
    [-1.10, +0.63] P 0.65; pooled -0.00 [-0.88, +0.46] P 0.65. The 1-2 mm shell holds 31 poses vs 30 on the bench.
- **The CMA best sits on a drive cliff.**
  - Its envh fit has crank PA 8.3 and dK_lim 44.5.
  - The same parameters fitted on Bench(60,160) synthesise no flank (dK_lim 0, 86.67), because the slipper cam is
    synthesised from the fit bench's poses.
  - Frozen from its own envh fit, it lifts metal (near2 28.87, shell 17 poses) but loses 3 takes and gains 2 contacts
    (139, 203).

## Convergence gate (score points = gap / 2.75)

| stream | configs | gain over 2nd half | gain over last third | top-5 spread | best (envh near1) | d_az1 of the best |
|---|---|---|---|---|---|---|
| A (from +2, sigma 0.25) | 170 | 0.00 | 0.00 | 0.00 | 17.08 | 1.16 (top-6 1.0-2.0) |
| B (from +5, sigma 0.25) | 110 | 0.37 | 0.00 | 0.04 | 17.20 | 1.45 (walked 4.6 -> 4.2 -> 2.5 -> 1.8 -> 1.45) |

Both streams pass the gate. The sweep holds 319 configs in order: coarse 12, Bench(60,160) CMA 40, envh scan 7, envh
CMA 280. A sigma-0.8 restart was not run: sigma 0.5 already broke the drive on 7 of 10 samples.

## Red team (my own best)

- **The point that pinches.** Pose 203 (plane 0 / elev 90 / axial 45, hub 2 wall) drops to 0.138 mm at +5 and goes into
  the skin at +2 and on the CMA best. The forward seat brings hub 2 toward the skin there, which is the same mechanism
  as the in-band gain.
- **The optimistic number.** The proposer's 14.73 / 24.49 was measured on the module-default knee. Bench(60,160)'s
  in-band rise at +5 is a fit-sample artefact (it falls on envh).
- **The jam.** The slipper drive is a cliff:
  - beyond +6 at the verified drive;
  - at sigma 0.5 (7 of 10 CMA samples dK_lim 0);
  - on a change of fit bench (k109).
  Any re-fit claim in this family must freeze the shape from its own fit bench (`ACRO_FIT`).
- **The stop.** At +5 the J3 dowel margin falls to 0.84 deg on the bench and 0.74 held. That is under the lead's 2.7 and
  inside the lead's T3 K-play watch (~0.23 deg).

## New knowledge

1. A J1 seat move at fixed a1 / a2 cannot move the lead's fold wall. It shifts the th window across the workspace and
   trades J3-stopped poses for fold poses one for one (88 + 6 -> 89 + 5). The four contacts belong to the drive and
   dwell metal and do not move. The lead's J1 (az1 95.39) is confirmed as the local optimum from two starts on a
   representative sample (envh).
2. Bench(60,160) is blind to seat moves in this family: reach is pinned at 0.775 by 31 fold poses. Search seat levers
   on envh.
3. In-band surplus from a seat move is a fit-sample effect: a sparser workspace sample lets the metal sit lower. Worn
   frozen, it reappears as metal in the 1-2 mm shell (T1) and as a thinner pose-203 clearance, not as takes.
4. The slipper-nose flank is synthesised from the fit bench's poses. A config tuned near the PA cliff on one bench can
   have no drive on another. Freeze from the search bench's own fit, or require a PA margin on both benches.

## Next

- The seat lever is closed for the coupled-K lead.
- The lead's remaining levers sit outside this row: drive geometry for the stretched wall (crank axis dR, ratio g, PA),
  and metal placement for 205 / 237 / 264 / 316.
- The seat-oracle row (round 105 pick 4) can take its L1 cell from the measured fact that J1 +2..+5 is not a gain at
  the lead's dyad.

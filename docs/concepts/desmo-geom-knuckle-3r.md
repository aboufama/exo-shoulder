# desmo-geom-knuckle-3r - slim-pivot regressive desmo: stage 1 wholly inside hub 2's O20 (cells B / A / T)

Round 105, lens C (the built complexity frontier). desmo-window-knuckle-3r's buildable level (stage-1 groove in a 440C insert
under link 2 at mid F2+3.9, one-piece crank through a window in link 1b) with new drive geometry: the crank axis moved ~1 mm
toward hub 2 (delta 13.75-14.2 deg off u2 instead of the parent's 14.66), the crank pivot on 2 x MR52ZZ in an O8 boss, a
regressive crank law phi = (K / g)(1 + c K), and a re-placed stage-1 pin, so that nothing of stage 1 sits outside the O20 rim.
3 active DOF, K slaved and never read, 0 passive translations, no spring, no gears / pulleys / cables.

**Verdict: DEAD by the pre-registered kill rule** ("kill the cell if no start holds the robust rc gate with the ring inside
O20"). It is stronger than the rule asks: with the ring inside the rim, no stage-1 pin passes even the NOMINAL built-groove
pressure-angle gate, over 108 crank geometries x ~7 800 pins in cells B and A. Cell T (0.6 mm wall) dies on the same numbers.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Gate the pin against the BUILT groove, not the linear law. The proposer's replica (scratchpad s1scan.py) takes the pressure
     angle on the linear law from K = 0+ and skips the onset. The milled groove has a C1 blend at the dwell-to-rise corner, and
     that blend is where both the pressure angle and the centreline radius are worst. I gate exactly what the claim model gates
     (desmo-conecut `_desmo_build_B`, built blended groove, pin side wherever the pin moves, cap side outside the blend).
   * Make the rc tolerance gate stricter than asked: a 3 x 3 grid (a_s +-0.05 mm x delta +-0.05 deg, corners, edges and
     nominal), with pitch, drift and the built PA re-checked at every point, not only rc.
   * Notice the symmetry: stage 1 is invariant under the crank axis's azimuth tau about u2 (link 2 turns about u2, the pin's
     azimuth frame turns with dR). Measured: tau 0 and 3.8 give identical rows. So tau is a stage-2 / packaging variable only, and
     the stage-1 question has 4 free variables (delta, g, c, pin) plus blend.
   * Price the things the new geometry moves that the spec did not list: the O8 boss's own clearance to hub 2's O20 stack (the
     parent's CRK-hub2 check skips everything within r2 + 6.5 of hub 2's axis, i.e. the boss), and the window's wall over the
     MR117 seat (it shrinks as the pin's pitch_lo falls).
2. **Rawest material.** The posed skin through the bench's signed-distance cache (Bench(60,160) fast); the model's own per-pose
   K / q2 / crank angles and its stage-1 synthesis; the verified parent's parts table and the desmo-window death audit's
   kit-density ring sampler (docs/concepts/verify/desmo-window-knuckle-3r_ringfix_audit.py). The skin-motion map and the
   proximity atlas are not the limiter here: the death is a drive-geometry feasibility fact, upstream of any skin number.
3. **Methods and tools.** The verifier's DCModel with the blended IK (via desmo-window's model, subclassed unchanged); the
   parent's `_rod_metal` re-compiled with exactly three asserted line swaps (crank axis, boss radius x2); `s1_metrics`, a
   vectorised replica of the claim model's stage-1 formulas, validated against the model (rc 0.895 vs 0.89, pitch_hi 9.851 vs
   9.851, drift 0.296 vs 0.297 at desmo-window's pin); an exhaustive grid (not an optimiser) for the feasibility question.
   Compute local only (farm closed), <= 2 niced processes.
4. **What, other than me, shows the number is right.** The control: with the parent's rule (dR_delta None, O10 boss, c 0) the
   model reproduces desmo-window k4 exactly (fast plain 14.68 / near-touch 20.52), and with ring_kit=1 it reproduces the
   death audit's ringfix (19.02 / ib14 0.8924). The replica validation above. The proposer's own replica, run at start 1, gives
   rc 0.722 (< 1.0 at nominal) - by their own numbers the start fails. Red-team pose list: rest, overhead, across the body,
   behind the back are the parent's (identical kinematics; the drive changes nothing in which poses close).

## Spec corrections (measured, stated for the verifier)

* **The proposer's start 1 does not pass in the claim model.** delta 13.766 / tau 3.8 / g 2.44 / c -0.057 / a_s 8.93 / psi 159.8:
  the built groove's pin-side PA in the onset blend (blend 8) is 48.5 deg against the 34.47 gate, so the drive is cut at K 0 (gap
  107.15, stop-order). Its rc is 0.68 (built) / 0.722 (the proposer's own replica, linear law). The proposer's 17.8 / 18.2 deg
  PA comes from the linear law, which skips the onset corner.
* **The parent clamp chain zeroes the crank law.** slipper-nose's clamp, re-applied inside the model build, sets cprog 0 (the
  spec warned of this). Fixed here by carrying the law under c_law (asserted: the built model reads c -0.057). The first 12
  sweep rows ran before the fix and are marked invalid in the sweep file.

## The decisive test: stage 1 inside the O20 rim (cells B, A, T)

Saved: docs/concepts/verify/desmo-geom-knuckle-3r_s1grid_inrim.json. Grid: delta 13.5 / 13.75 / 13.9 (13.5 is below the O8
boss's buildable bound; pitch only rises with delta, since the crank axis moves away from u2), g 2.2-2.6 (6 values), c -0.09
/ -0.057 / -0.03 / 0, a_s 7-11 x psi 60-250. Ring inside the rim = pitch_hi + 0.76 + 0.8 <= 10.0, i.e. pitch_hi <= 8.44.

| cell | geometries | pins with ring inside the rim AND the built PA gate | closest PA-feasible pin: pitch_hi (r_out) | its nominal rc | min built PA of pins inside the rim |
|---|---|---|---|---|---|
| B (mu 0.15, gate 34.47, kdrive 47.5) | 57 | **0** | 8.926 (10.49) | 0.83 | 43.9 |
| A (mu 0.087, gate 38.03, kdrive 53) | 51 | **0** | 8.836 (10.40) | 0.68 | 43.9 |
| T (0.6 wall: pitch_hi <= 8.64, rc >= 1.3) | (B / A grids) | **0** | 8.836 > 8.64 | 0.68 < 1.3 | - |

* The robust gate is not even reached. No pin with its ring inside the rim passes the NOMINAL built pressure-angle gate. The
  best such pin is 9.4 deg over cell B's gate and 5.9 deg over cell A's.
* The closest PA-feasible pins stick 0.40-0.50 mm past the rim, and their nominal rc is 0.67-0.83 (< 1.0).
* Why: the groove level is fixed by the stack (mid F2+3.9). The O8 boss holds the crank axis >= ~15 mm from u2 at that level
  (boss vs hub 2's O20 >= 1.0 mm at delta 13.75: measured 2.01 mm to the sampled stack at the boss ring, the spec's rule 13.747).
  A pin <= 8.44 from u2 must then point almost straight at u2 from the crank axis, so the crank turns it TANGENTIALLY about u2,
  the direction the cap ring moves. The relative motion that drives K vanishes, and the pressure angle climbs past 43 deg.
  The regressive law (c -0.09) lowers the best pitch by only ~0.05 mm.

## Variant W (what is left of the lens): the new drive geometry at desmo-window's level, ring past the rim

The judge named the other lever: the crank's ~133 samples (80 % in band) move with dR and g. So the robust-rc gate stays and the
rim gate is dropped (rim_gate 0), with the ring at the kit's density (ring_kit 1, the death audit's sampler). Window-level pin
scans: docs/concepts/verify/desmo-geom-knuckle-3r_s1grid_window.json. Robust pins exist at every geometry scanned (12-121 each,
delta 13.75).

Fast Bench(60,160), frozen-shape fit (sweep docs/concepts/sweeps/desmo-geom-knuckle-3r.json):

| config | near-touch | plain | ib14 | reach | robust rc | r_out | crank ib14 (n) | ring ib14 (n) | gates |
|---|---|---|---|---|---|---|---|---|---|
| desmo-window k4, kit-density ring (control, O10 boss) | 19.02 | 13.26 | 0.8924 | 0.775 | **0.891 FAIL** | 11.41 | - | 10 samples | rc-robust fails |
| same, O8 boss (control) | 18.80 | 12.64 | 0.8986 | 0.775 | **0.891 FAIL** | 11.41 | 0.845 (124) | 0.157 (10) | rc-robust fails |
| W k13: delta 13.75, g 2.39, c -0.057, blend 12, a_s 8.95 / psi 150.5 | **19.08** | **13.32** | 0.8918 | 0.775 | 1.043 | 10.90 | 0.802 (132) | 0.158 (10) | all pass |
| W k12: same at g 2.33 | 275 | - | - | 0.331 | 1.306 | 10.90 | - | - | stop-order (stage 2 wall2B-pa at K 0) |
| W at a_s 9.2 / psi 151 (pitch_lo 7.08) | 18.80 | 12.79 | 0.8971 | 0.775 | 1.013 | - | - | - | O11-wall 0.63 < 0.8 |

* desmo-window's own pin FAILS the robust rc gate (0.891 nominal). The judge's tolerance rule would therefore also refuse the
  parent's built stage 1. This is new, and the lead should carry it to desmo-window / desmo-conecut (verified pin a_s 9.529:
  not re-measured here).
* With the robust gate held, variant W reads 19.08 near-touch / 13.32 plain (fast). That is level with desmo-window's
  kit-density 19.02 / 13.26 (+0.06), the level that died on the held line.
* The O8 boss alone is worth 0.22 fast near-touch points at kit density (18.80 vs 19.02; 0.61 with the 4x-dense ring). But the O11 wall takes it back: a pin with
  pitch_lo >= ~7.4 is needed to leave >= 0.8 mm over the MR117 seat, and that pin rides further out.
* The crank does not move: 0.802 in band at 132 samples, the judge's "133 at 0.803". The lever the judge hoped for is not there
  inside these bounds.
* The rows after k13 landed before the time box ended (all in the sweep file). The best are tau +-3 or delta 14.0 at g 2.39 /
  c -0.057 / blend 12:

  | k | config | near-touch | plain | ib14 |
  |---|---|---|---|---|
  | **22** | delta 14.3, c -0.03, a_s 9.6 / psi 151 | **18.80** | **12.69** | 0.8981 |
  | 17 | tau +3, a_s 8.95 / psi 150.5 | 18.80 | 12.87 | 0.8963 |
  | 20 | tau -3 | 18.80 | 12.97 | 0.8953 |
  | 18 | delta 14.0, a_s 9.25 / psi 151 | 18.80 | 12.97 | 0.8953 |
  | 21 | delta 13.9, tau 2, g 2.44 | 18.80 | 12.92 | 0.8958 |

  * k22 is 0.57 plain / 0.22 near-touch under desmo-window's kit-density level, with every gate passing, the robust rc gate
    included (rc 1.031). It was NOT worn on Bench(110,360) exact or held out (time box, ~18 min per wear at a full core).
  * By desmo-window's fast-to-worn mapping (fast near-touch 19.02 -> bench 18.80-19.01 / held 23.00-23.20), k22 would land at
    about bench 18.6-18.8 and held 22.8-23.0. That is at or just under the lead's held line (22.38 + 0.5), and not under 18.28.
    This is an open item for the lead, not a claim.
  * c 0 at the same pin (k14) reads 20.18 near-touch / 13.26 plain. So the regressive law is worth ~1.4 near-touch points at
    this pin: c changes where the pin's crank arm sits, not only the law.
  * The no-robust-pin rows are delta 14.66 (the parent's axis at blend 10) and g 2.5. The stop-order rows are stage-2
    failures: g 2.33 (wall2B-pa at K 0) and g 2.44 at blend 10 (pocket-pa).

## Red team (own best, W k13)

* **The pin that pinches.** The window's wall over the O11 MR117 seat is the binding gate, not the groove. At pitch_lo 7.08 the
  wall is 0.63 mm (fails 0.8). Every pin that would buy in-band by riding closer to hub 2's axis breaks it.
* **Stop order.** The drive still ends at 47.5 (slot-end): stage 2's tip plate against hub K is unchanged by the crank move at
  g 2.39. At g 2.33 stage 2 dies at K 0 (wall2B-pa): the slot wall's pressure angle cannot be re-seated by the crank axis alone.
  r_c / beta were in the queue when the time box ended.
* **Boss vs hub 2.** 2.01 mm at delta 13.75 (O8). The spec's 1.0 mm figure is the boss axis distance minus the radii; the
  sampled stack gives more because the boss sits above the hub's crown band.
* **The optimistic number.** A fast near-touch 19.08 at kit density, against the lead's 18.28 frozen exact. desmo-window's fast
  19.02 wore to 18.80-19.01 bench / 23.00-23.20 held at the same density. Nothing here suggests a different wear.

## Convergence gate

Not the basis of the death. The death rests on an exhaustive feasibility grid over the spec's full ranges plus margin (every
crank geometry x every pin on a 0.1 mm x 1 deg grid), not on a sampled optimiser that might not have converged. The variant-W
fast sweep did NOT converge in the time box (2 valid rows, then the queue). Gate numbers: n/a / n/a / n/a. It is reported only
as a measured level, not as a verdict on the lens.

## What this teaches (beyond this morphology)

* **A groove drive at a J2 hub has a geometric floor on its pitch, set by the crank axis's distance from the hub axis at the
  groove level.**
  * The pin must move RADIALLY with respect to u2 to drive K. A pin closer to u2 than roughly the axis offset minus a_s
    moves tangentially, and its pressure angle runs away.
  * With an O8 pivot >= 1 mm off an O20 hub, the floor is pitch_hi ~8.84 (built PA, mu 0.087) or ~8.93 (mu 0.15). That is
    0.4-0.5 mm too big for any 0.8 mm-walled insert to stay inside the O20 rim.
  * Only three things move the floor: a crank axis that does not pass through GH (a different, non-spherical stage 1), a
    lower groove level (blocked by link 1b's plate), or a smaller hub.
* **Replicas must gate the built groove.**
  * The linear law's pressure angle skips the onset corner, where the blend makes both PA and rc worst.
  * The proposer's 17.8-deg PA and pitch 7.12-8.24 were real numbers on the linear law and wrong for the part that gets
    milled (48.5 deg).
* **The robust rc gate refuses the verified desmo family's own pins** (desmo-window 0.891 nominal). Ask the lead to rule
  whether that gate now applies retroactively.

## Audit (death auditor, 2026-10-18 ~11:25-11:50 UTC)

**Ruling: the death STANDS.** The stage-1 death reproduces and gets stronger over the ranges the scan skipped. The surviving
variant W, worn for the first time, reads **18.43 frozen exact on Bench(110,360)**. That is 0.15 over the lead, all of it
in-band, with identical takes and contacts. Its ceiling by arithmetic is a tie with the lead. Saved:
docs/concepts/verify/desmo-geom-knuckle-3r_audit_s1grid.json, docs/concepts/verify/desmo-geom-knuckle-3r_audit_k22_{bench,held}_frozen.json,
docs/alignment/remeasure/desmo-geom-knuckle-3r_{bench,held}_perpose.json (T5 dumps), and
docs/alignment/remeasure/desmo-geom-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json.

1. **Reproduction.** Re-run through the claim model's own `s1grid` / `s1_metrics`, unchanged, the blend-8 rows match the claim
   file exactly: cell B delta 13.75 has pitch_hi floor 8.937; cell A has 8.836 at delta 13.5 and 8.919 at delta 13.75.
2. **Ranges the scan skipped.**
   * The in-rim scan ran **blend 8 only**, though the spec allows 8-12.
   * It ran **delta >= 13.5 only**. The spec's 13.75 rule turns out to be conservative: the model's own boss-hub2 gate
     measures 0.60 / 1.00 / 1.17 / 1.21 mm at delta 12.5 / 12.85 / 13.0 / 13.75, so **12.85 is the real buildable floor**.
   * I re-scanned 131 geometries: blend 8 and 10, delta 12.5-13.75, g 2.0 / 2.2 / 2.44 / 2.6 / 3.0, c -0.09 / 0, cells B and
     A, pins a_s 7-11 x psi 60-250. One extra probe ran at blend 12 (delta 13.75, g 2.44): floor 8.994, in-rim built PA >= 44.7.
   * Result: **0 in-rim PA-feasible O1.5 pins.** The floor is 8.73 (cell A, delta 12.5, already past the boss gate) and
     8.79-8.92 at legal deltas, against 8.44. The built PA of in-rim pins is >= 41.1 (cell B) / 43.5 (cell A).
3. **Limiter correction.** The pitch floor is NOT set mainly by the crank axis's distance from u2. Moving delta from 13.75 to
   12.5 brings the axis ~1.4 mm closer and lowers the floor only 0.10-0.19 mm.
   * In every best pin, pitch_lo sits on R_LO 7.06-7.14: the insert bore of 6.3 over the O11 MR117 seat, plus half the groove.
   * The binding pair is the annulus between the bore wall and the rim wall. With an O1.5 pin it holds **1.38 mm of pitch**.
     A PA-feasible pin needs **>= 1.63-1.87 mm of radial stroke** to drive 47.5-53 deg of K through 18-24 deg of crank.
   * Identity behind it: the groove normal n is perpendicular to (v_pin - v_cap), so |v_pin| cos PA_pin = |v_cap| cos PA_cap.
     Holding both PA gates forces the pin speed to >= 0.82 x the cap speed at the pin, and the groove's radial excursion
     follows from that.
   * So the "only three things move the floor" list in the claim is incomplete. The groove width (pin diameter) and the 0.8
     walls are levers too.
4. **The one lever left: an O1.0 pin.** It is not a refutation, and it needs rulings.
   * An O1.0 pin (groove 1.02, same 0.8 walls) gives pitch [6.81, 8.69]. In-rim PA-feasible pins then exist at 46 of 72
     geometries.
   * With rc >= 1.0 as written: nominal rc reaches 1.14 (blend 12), but **0 pins pass the robust 3 x 3 gate**.
   * With rc scaled to the pin (>= 0.75: the same 0.24 mm inner-edge radius as O1.5 at rc 1.0): **3 robust pins**, all in
     cell A (mu 0.087), all at delta 12.85 where the boss gate sits at exactly 1.00 mm. Their built PA is 37.2-37.5 against
     38.03, robust rc 0.86-0.89. Cell B (mu 0.15) has 0.
   * It needs three changes the lead or user must rule on: an O1.0 pin (Hertz and bending unchecked), a scaled rc gate, and
     mu 0.087. Even then the ceiling is the judge's tie at 18.28.
5. **Convergence gate (variant W, the 12 valid rows k12-k23).**
   * Near-touch objective: gains 0.0 / 0.0 score points, top-5 spread 0.0. Six configurations sit at exactly 18.80, because
     the drive parameters do not move the near-touch poses.
   * Plain: 0.065 / 0.065 / 0.10 points.
   * Formally converged by the gate's numbers, contrary to the row's "not converged". It is a small sweep, but the near-touch
     plateau is flat.
6. **Variant W k22 worn (frozen exact, CB_EXACT=1, the claim's own `wear`, 526 s).**
   * fit_fast reproduces the claim: 12.69, reach 0.775, ib14 0.8981.
   * **Bench(110,360) frozen exact: gap 18.43.** reach 0.7278 (262/360), follow 1.0, ib14 0.8985, ib10 0.5713, contact
     0.0106 (the lead's four poses 205 / 237 / 264 / 316), overhead 8/28, near-touch 20.07, min metal 0.07 mm.
   * Gates: th margin min 5.181 (0 under 5), stop order J2 dowel first (margin 0.45), O11 wall 0.861, plate-horn 0.15,
     robust rc 1.031. The ring sits 1.05 mm past the rim (r_out 11.05), sampled at kit density (10 samples).
   * The per-pose dump recomputes 18.44 (+-0.05 OK).
   * **Paired vs the lead (conecut-knee-knuckle-3r):** diff +0.15, all in-band. Discordant takes 0 / 0, contacts 4 both,
     bootstrap ci90 [0.00, 0.34], P(better) 0.00.
   * Read: k22 beats desmo-window's kit-density wear (18.80-19.01), desmo-slipper (18.95) and desmo-conecut (18.98) by
     0.37-0.58. The claim's mapping (18.6-18.8) was 0.2-0.4 pessimistic. But reach and contact are the lead's exactly and
     in-band saturates at 0.90, so **18.28 is a hard ceiling (a tie)**, and k22 is 0.0015 of in-band (~1.4 samples) short.
   * Held out: see the line below.
7. **The refutation criterion in the audit template** ("within 10 of 68.93 on Bench(60,160)") is a round-3 rule. Any desmo
   row meets it trivially (fast 12.69). The bar that applies in round 105 is the lead's 18.28 frozen exact, and variant W
   cannot beat it.

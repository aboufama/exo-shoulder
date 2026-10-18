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


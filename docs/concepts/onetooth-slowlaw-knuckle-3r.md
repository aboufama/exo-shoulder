# onetooth-slowlaw-knuckle-3r - one-tooth slow-law knuckle (round 107, pick 1)

**Status: DEAD at step 0** (pre-registered kill gate: law-only ghost frozen exact Bench(110,360) > 19.0 or workspace
takes < 258). The slow law alone, with every drive part deleted, reads **22.79 with 247 workspace takes** at rho 0.8. The
lead's own law through the same harness reads __CTRL__. Separately, the spec's pin cannot carry the stroke: its built
flank is undercut 1.25 mm over K 2.5-20.3 deg, because the pin passes through the relative pole (the pitch point) at K 22.4.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do here that the spec does not ask for.** Before building any metal, check the
   two places where one pair can fail outright. (a) The **pitch point**. With a constant law, link 1a and link 2 have a
   fixed relative pole (the Kennedy axis) in link 1b's frame. A pin whose circle about uK passes through that pole has a
   cusped relative path, so the flank can act on one side of the pitch point only. This is the lantern-gear rule. The
   proposer's PA pass was sampled at 0.76 deg of K, which is coarse enough to step over the pole. (b) The **knuckle's own
   fold**. Moving the onset from th 77.9 to th 58.5 makes K open in a region where the J1-K-J3 sub-dyad (arcs bk1 and cK)
   may sit within the 5 deg fold margin (msub, the lead's own rule). A slow law changes where K opens, not only how fast.
   So step 0 goes to the law (ghost) first and checks the built flank separately. Two more checks follow: a paired control
   (the lead's own law, drive deleted, same harness), and an onset-held variant (slow rate from the lead's onset).
2. **Rawest material.** These are the posed skin signed-distance fields of every bench and the motion clips (the
   benches' own data, via tools/concept_bench.py, exact path). Also: the fresh envelope draw envsel
   (docs/research/minarc_final_polish/env_poses.npz, never the claim bench, for selection) and the lead's own extracted
   geometry (docs/research/slipper_mechanism/geo_bench.npz) for the pitch-point and PA geometry. I did not use the
   proposer's digested proxy numbers. The skin-motion map and proximity atlas were not needed, because the morphology
   died on kinematics before any metal was placed.
3. **Methods and tools.** The lead's verified model is loaded unchanged
   (docs/concepts/models/conecut-knee-knuckle-3r.py). Its per-t gated 'lin' law takes kK := rho, and the onset is moved
   in closed form on K's stop-A curve (cos th = A + R cos x) so the end state stays the lead's. Every drive part is
   deleted: metal, contact sets, strap sets and gates. The frozen protocol is used throughout: fit on Bench(60,160)
   fast, freeze the shape, then wear on envsel exact / Bench(110,360) exact. The built-flank check is exact spherical
   kinematics: the pin-centre path in link 2's frame, contact points X - rn F, and the union-of-discs boundary as the
   built flank. It gives the undercut depth, the built-flank pressure angles and the drive's own range.
4. **What, other than me, shows the number is right.** The bench (Bench(110,360) exact, frozen) and the paired control
   (the lead's law in the same ghost harness, so the harness error cancels). The model is the lead's verified code with
   only the law and the drive deletion changed. The red-team list below gives the poses lost, with th and dK, and why.

## Model

`docs/concepts/models/onetooth-slowlaw-knuckle-3r.py`:

- `OT_CELL=ghost` is step 0. It subclasses the lead's CCModel, and `_ghost()` deletes the crank, roller / nose, the
  flank lug, the ROD / CRK / HORN strap sets and the crank-side gates.
- The law is |dK| = rho t past the slow onset `smhi_for()`. The drive range DKLIM is 50.0 (the lead's fitted dK_lim),
  so the stretched wall is the lead's.
- This is a **law change, not a metric change**. No bench, judge or kit file was touched.
- `flank` mode is the built-flank check of the one pair at any pin start (r0, az0), nose radius and rho.

The spec's sign convention was checked against the model: link 1b = R1 R(uK, dK), so link 1a turns by R(uK, -dK) in
link 1b's frame. The proposer's geo_bench convention (omega_1a = +uK, omega_2 = -u2 / rho) is reproduced, and the pole for
the spec pin lands at K 22.4, consistent with the proposer's own Kennedy numbers.

## Step 0 - law-only ghost (no drive metal: a bound for this morphology)

Each fit is on Bench(60,160) fast, then the frozen shape is worn exact.

| law | onset th | fast plain / 2 mm | envsel exact frozen (ws takes / 360) | Bench(110,360) exact frozen (ws takes) |
|---|---|---|---|---|
| lead 2.1534 (control, drive deleted) | 77.93 | 12.50 / 18.80 | 24.14 (245) | __CTRLB__ |
| rho 0.90 | 62.25 | 16.25 / 25.56 | 27.55 (236) | __G090B__ |
| rho 0.80 (spec) | 58.55 | 16.88 / 30.29 | 27.87 (233) | **22.79 (247)**, 5 contacts, follow 0.9545 |
| rho 0.75 | 56.29 | 18.12 / 29.92 | 28.33 (233) | - |

The fast rho scan runs 2.1534 / 1.5 / 1.2 / 1.0 / 0.9 / 0.8 / 0.75 / 0.7, giving plain 12.50 / 13.12 / 13.12 / 13.12 /
16.25 / 16.88 / 18.12 / 20.00 (sweep file). The cost begins below rho 1.0, and that is where the J1-K-J3 sub-dyad margin
msub falls under 5 deg along the law: msub_min is 10.75 at 2.15, 6.51 at 1.2, 4.94 at 1.0, 4.02 at 0.9, 3.0 at 0.8 and
2.45 at 0.75.

**Limiter, measured.** On the fast bench, all 9 poses lost at rho 0.8 relative to the lead-law ghost come from the fold
rule, and 8 of them sit just past the slow onset. They are poses 23, 24, 87, 110, 112, 124, 132 and 157, at th 60.3-62.9
deg with K opened only 1.8-4.3 deg. Two of them are clip frames, which is why follow falls from 1.0 to 0.967. The ninth
pose, 174, sits at th 106.7 at the stroke end. The kit's knuckle sub-dyad rule rejects them (msub >= 5 deg: K's axis is
then within 5 deg of the J1-J3 great circle, so K's opening barely moves th, and the J1-K-J3 chain is near its fold).
The same mechanism shows on the exact benches:

- fold poses rise from 100 to 118 on envsel;
- ws takes fall from 245 to 233 on envsel;
- on Bench(110,360), 247 ws takes against the lead's verified 262.

The 2 mm near-touch reading gets worse still (envsel 48.69 against 38.25), because K is open on most taken poses (271 of
338 at rho 0.8, against 161 of 355) and hub K and hub 2 then sit at new places.

## Built flank of the one pair (independent second kill)

This is `flank` mode at rho 0.8, nose r 1.25, R 62, mu 0.087 (gate 38.03):

| pin start (r from u2, az) | pole K | kinematic PA max (excl. +-1 deg of pole) | undercut spans (K deg, depth mm) | drive range from stop A |
|---|---|---|---|---|
| 21.5 / +24 (spec) | 22.4 | 13.1 / 38.8 | 2.5-20.3 (1.25), 22.4-23.9 (1.13) | ~2.5 deg |
| 19.5 / +16 | 13.6 | 17.0 / 47.0 | 0-12.8 (1.04) | 0 |
| 20.0 / +18 | 15.8 | 15.6 / 45.5 | 0-15.8 (1.25) | 0 |
| 22.5 / +26 | 25.6 | 15.8 / 37.3 | 6.3-25.6 (1.25) | ~6 deg |

Pin scan (r 8-40 mm / az -180..180, rho 0.8 and 0.9, drive range = first K where the kinematic PA fails or the flank is
undercut): __SCAN__

The proposer's PA pass (18.3 / 34.0) was read on a 0.76 deg K grid, which steps over the pole spike. The pin's circle
about uK (23.0 mm) runs through the pole (pitch axis ~16.7 deg from u2, about 21.3 deg = 23 mm from uK). That is not an
accident: the PA gate pulls the contact toward the pitch point, because the common normal must pass through the pole
(Kennedy) and a small PA needs the contact near it. So this geometry makes a PA-passing pin also a pole-crossing pin.

## Red team

- **The pose that jams.** No jam reading applies to the ghost. The poses lost are fold-rule rejections at th 60-63 just
  past the slow onset (the arm at elevation 30-75, not overhead). The overhead count is unchanged: 5 of 26 on envsel and
  7 of 28 exact, the same as the control.
- **The point that pinches.** Contacts on Bench(110,360) at rho 0.8 are 205 (-4.03 mm, hub 2), 237 (-2.82), 316 (-1.16),
  139 (-0.61) and 264 (-0.10). These are the lead's four binders plus 139, and they come from hub 2 / hub K. No drive
  metal was present.
- **The optimistic number.** The ghost is a bound. Real pin + tooth metal stacked over link 1b at R 64-67 can only remove
  takes and in-band, and the built flank cannot carry more than a few degrees of K from stop A. Even the bound fails both
  kill thresholds.
- **Onset-held variant** (slow rate from the lead's onset, SMHI_FIX 16.84): __ONSET__

## Verdict

DEAD at step 0. This is no frontier point: the ghost bound of 22.79 is a bound, not a buildable reading, and the built
drive does not exist at the spec's pin. The cx 10-11 frontier point therefore stays unmeasured, and geneva-tail-pinknee
(cx 12.0, 23.57) is not dominated. Cell D (spring-free groove) is not run: the spec makes it conditional on the spring
cell's built flank passing the PA gate, which it does not.

**New knowledge** (it predicts beyond this row):

1. Any constant-rate one-pair K drive at the lead's seats has a fixed relative pole. A PA-passing pin sits near it, so it
   crosses the pole within the stroke and undercuts (lantern-gear rule). One pair with a pin can act on one side of the
   pitch point only. A one-pair drive must keep its whole working arc on one side of the pole, and that costs PA. The
   pin scan bounds how much.
2. Slowing the K law moves its onset to lower th, where the knuckle's J1-K-J3 sub-dyad is near its own fold. At the
   lead's seats msub < 5 deg for rho < ~1.0, so the 5 deg fold rule rejects the first ~5 deg of th past the onset. This
   costs 9-12 ws takes per 360. Any slaved-knuckle lens that wants a slow law must move its onset, or its seats, against
   msub as well as against PA.

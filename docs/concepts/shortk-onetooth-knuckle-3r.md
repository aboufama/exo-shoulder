# shortk-onetooth-knuckle-3r - re-seated short-K one-tooth knuckle (round 107, cell B)

**Status: DEAD at step 0.** The pre-registered kill is met: no pressure-angle-passing pin start leaves the tooth with <= 4
skin-contact poses at a level <= R 64. At the spec's law (rho 1.05-1.1) the cell is empty. Over 302,595 pin starts, no
single pin-flank pair (the spec's drive) carries the 44.1 deg K stroke. The best built range from stop A is 29.7 deg with a crowned pin and
35.9 with a rolling one. The law-only ghost with that range reads **31.80** frozen exact Bench(110,360). A full-stroke
single pair exists only at fast laws (rho >= 2.0 rolling, >= 2.5 sliding), where the pin sits on or inside hub K's O20 rim.
Its tooth (20-30 mm from hub 2's axis) then dips 9-19 mm into the skin on 19-57 overhead poses at every level up to R 67.
The re-seat alone, with no drive metal (ghost), reads **18.83** (261 ws takes) against the lead's 18.28 / 262.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do here that the spec does not ask for.** The parent row
   (onetooth-slowlaw-knuckle-3r) died on two counts: the slow law's ghost, and the lantern-gear rule (a PA-passing pin
   sits next to the fixed relative pole, so over a long stroke it crosses the pole and the flank undercuts). Re-seating K
   moves the pole; it does not remove it. So the first check is the built flank on the NEW dyad, on a fine K grid
   (0.05 deg - the proposer's PA reading used 61 samples over 44 deg, 0.74 deg apart, the same grid that stepped over the
   parent's pole spike), over every pin start on the sphere around hub 2 (r 4-45 mm, all azimuths), at mu 0.087 and at
   mu 0 (a rolling pin), and at rho up to 2. The second check is the law-only ghost with the drive range the built pair
   can actually carry (DKLIM = its built range), not only the ideal full stroke - that is the buildable bound. Third: the
   lead's parent clamps bk1 to [26, 32] and bk2 to [38, 48] (an old search box): a naive re-seat silently runs 32 / 38,
   not 34 / 30, so the dyad is restored after the clamp and asserted. Fourth: anchor the law on the lead's END STATE
   (a1e 54.27 at th 106.3, read from the lead's own kinematics), not on the lead's K value (45.62 on the old dyad is
   a1e 57.33 on the new one).
2. **Rawest material.** The posed-skin signed-distance fields of every bench and the motion clips, through
   tools/concept_bench.py on the exact path (Bench(110,360) exact for the frozen wear; envsel,
   docs/research/minarc_final_polish/env_poses.npz, for selection only). The lead's verified model code itself
   (docs/concepts/models/conecut-knee-knuckle-3r.py), loaded unchanged, for the chain and its exact kinematics. Not the
   proposer's proxy numbers (scratch shortk*.py: re-solved poses at a hand-placed patch, no fold rule, no re-fit).
3. **Specific methods and tools.** Exact spherical kinematics of the one pair (all axes through GH): the pin centre path
   in link 2's frame, the kinematic normal through the relative pole (Kennedy), contact points X - rn F, the built flank
   as the union-of-discs boundary (undercut where a contact point falls inside the pin disc of another K), both pressure
   angles vs 43 - atan(mu); a vectorised scan of 2,000+ pin starts per rho. Then the parent's ghost harness (every drive
   part deleted) on the frozen protocol: fit Bench(60,160) fast, freeze the shape, wear exact.
4. **What, other than me, shows the number is right.** The bench (Bench(110,360) exact, frozen) and a paired control
   that cancels harness error (the parent's control: the lead's own law in the same ghost harness reproduces the
   verified 18.28 / 262 takes exactly). The built-flank check is independent of the bench (pure kinematics, any reader
   can re-run `flank` mode). The red-team list gives the poses lost with th and dK and why.

## Model

`docs/concepts/models/shortk-onetooth-knuckle-3r.py` loads `onetooth-slowlaw-knuckle-3r.py`, which is the verified lead
conecut-knee-knuckle-3r unchanged, plus its ghost cell and its exact built-flank check. It changes three things.

- **The dyad, 34 / 30.** It is restored *after* the lead's chain clamp, because roller-longdyad clamps bk1 to [26, 32]
  and bk2 to [38, 48], an old search box. A naive re-seat runs 32 / 38 without saying so: my first a1e(K) check returned
  the same uK for 34 / 30 and 32 / 32. The K dyad's own fold rule is asserted here instead (`kdyad_ok`).
- **The anchor.** The law is anchored on the lead's end state, a1e 54.27 at th 106.30, both read from the lead's own
  kinematics. It is not anchored on the lead's K value: K 45.62 on the old dyad is a1e 57.33 on the new one. The onset is
  solved on the new dyad's exact th(q2, K). At rho 1.1 this gives th_on 62.26, q2_on 36.76 and K_end 44.15 at q2 -3.37,
  which reproduces the spec's 62.2 / 36.9 / 44.2 / -3.3.
- **The wall.** DKLIM is the K at the lead's wall, a1e 55.52 (the lead's K 50), which is 48.43 deg on the new dyad. That
  leaves the K dyad 8.48 deg from its stretch (minimum over taken poses 9.74). The spec's 5.23 deg margin applies only if
  the wall is a1max 58.77 (`WALL=a1max`). `DKCAP` caps the range at the built pair's range.

This is a law / seat change, not a metric change: no bench, judge or kit file was touched. Frozen protocol throughout:
fit on Bench(60,160) fast, freeze the shape, wear exact on envsel (for selection) and on Bench(110,360).

## Step 0a: law-only ghost (no drive metal, so a bound)

| cell | fast plain / 2 mm | envsel exact frozen (ws takes) | Bench(110,360) exact frozen (ws takes) |
|---|---|---|---|
| lead dyad + lead law (parent's paired control) | 12.50 / 18.80 | 24.14 (245) | **18.28 (262)** = the verified lead |
| 34 / 30, rho 1.1 (spec), full stroke 48.4 | 13.12 / 29.60 | 23.87 (246) | **18.83 (261)**, 5 contacts (139 -0.49 new; 205, 237, 264, 316 the lead's), near-2 40.34, overhead 8/28 |
| 34 / 30, rho 2.1534 | 13.12 / 35.19 | - | 18.83 (261), near-2 45.24 |
| 34 / 30, rho 2.5 | 12.50 / 34.53 | - | 18.83 (261), near-2 45.24 |
| 34 / 30, rho 2.0 | - | 23.87 (246) | - |
| 32 / 32, rho 2.0 | - | 23.87 (246) | - |
| 34 / 30, rho 1.1, **range = the best built sliding pair (29.7)** | 27.29 / 47.34 | - | **31.80 (221)**, follow 0.927 |

- The ideal ghost passes the 19.0 ghost gate.
- The re-seat costs +0.55 on the claim bench and -0.27 on envsel, at every law alike.
- The 2 mm near-touch reading is worse than the lead's (40.3-45.2 against 34.8), because hub K now rides on the new seat.

## Step 0b: built flank of the one pair (exact; K step 0.05 deg)

Read with `flank` mode on any pin (per pin), or with docs/research/shortk_onetooth/fscan.py (vectorised scan). Pin radial,
nose r 1.25, R 62. The drive range is the first K from stop A where either pressure angle exceeds 43 - atan(mu), or where
the built flank is undercut.

- **The spec's start** (r 19 / az +18 from u2, rho 1.1): the pole falls at K 22.2 and the flank is undercut 1.25 mm over
  K 0-21.4, so the drive range is 0. The proposer's pressure-angle pass came from 61 K samples over 44 deg (0.74 deg
  apart), the same grid that stepped over the parent's pole spike.
- **The spec's box** (r 16.5-20 / az 12-24, 0.25 mm x 1 deg): best range 24.85 deg.
- **Wide scan** (r 4-45 mm x all azimuths, 1 mm x 3 deg; best built range in deg against the 44.14 needed):

| dyad | mu | rho 1.1 | 1.5 | 2.0 | 2.1534 | 2.5 |
|---|---|---|---|---|---|---|
| 34 / 30 | 0.087 (crowned pin) | 29.7 | 35.9 | 39.6 | 40.6 | 46.7 (pin 9.2 mm from uK: inside hub K) |
| 34 / 30 | 0.005 (rolling) | 35.9 | 43.1 | 47.0 (1 pin outside hub K: r 28 / az 24, 12.9 mm from uK) | 48.5 | 48.5 |
| 32 / 32 | 0.087 | 29.1 | 36.6 | 40.3 | 42.8 | 47.9 (inside hub K) |
| 32 / 32 | 0.005 | 35.7 | 41.5 | 48.3 (3 pins outside hub K) | 48.3 | 48.3 |
| 33 / 31, 35 / 29, 36 / 28 | 0.087 | 27.7-28.5 | 34.5-37.2 | 39.2-43.7 | 39.4-42.2 | 44.6-47.7 (all inside hub K) |

Other laws: rho 0.85 / 0.95 / 1.05 give 24.4 / 25.8 / 26.6 at mu 0.087, and 34.9 frictionless at rho 1.05.

**Why (the pitch point).** With a constant law, link 1a and link 2 have a fixed relative pole in link 1b's frame (Kennedy,
spherical). It lies on the uK-u2 arc, about bk2 / (1 + rho) from uK: 14.3 deg at rho 1.1 and 8.6 deg at rho 2.5. The
common normal passes through the pole, so both pressure angles are small only in a lens around it. A pin circles uK, and
it stays inside that lens for at most ~30 deg of K (sliding) or ~36 deg (rolling) at rho 1.1.

A longer arc of action needs a pole closer to uK, which means a faster law. A full 44 deg stroke needs rho >= 2.0
(rolling) or >= 2.5 (sliding). At those laws the pole, and the pin next to it, sit on or inside hub K's O20 rim: 8.7-9.7
mm from uK sliding, 12.9-13.6 mm rolling, against the 12.6 mm a pin outside the rim needs. "Move K, not the law" cannot
open the "just outside the O20 rim" cell. Re-seating K moves the pole along the uK-u2 arc in proportion to bk2. It does not
lengthen the lens.

## Step 0c: the tooth sweep at the only buildable full-stroke pins (rho 2.0, rolling)

Script: docs/research/shortk_onetooth/metal.py. Envsel exact, on the frozen ghost's taken poses.

- **Pin side.** A radial pin O2.5, an O6 boss and an 8 x 3 horn on link 1a at hub K's level.
- **Tooth side.** The tooth lug is the exact flank locus plus 1.5 mm and 3 mm behind it, with a root bar from hub 2's
  rim, 3 mm thick at level Lt.
- **Frame check** (framecheck.py): on every K-open pose the pin centre sits on the tooth locus at the matching K, within
  0.011 deg.

| dyad, pin (r / az from u2) | tooth contact poses at R 61 / 63 / 65 / 67 | tooth min (mm) | tooth in-band 14 at R 67 | pin / horn contacts |
|---|---|---|---|---|
| 34 / 30, 28 / +24 | 57 / 46 / 37 / 33 | -17.4 .. -18.6 | 0.31 | 8 / 0 |
| 34 / 30, 27 / +21 | 47 / 38 / 34 / 32 | -15.8 .. -16.8 | 0.31 | 0 / 0 |
| 32 / 32, 22 / -9 | 29 / 27 / 24 / 19 | -9.8 .. -10.1 | 0.15 | 0 / 0 |
| 32 / 32, 22 / -6 | 29 / 26 / 23 / 19 | -9.3 .. -9.6 | 0.15 | 0 / 0 |

Every contact is overhead scaption at the stretched end: envsel ws 382 (plane 30.8 / elev 137.5 / axial -45.1), 453
(29.7 / 149.6 / -56.5), 378 and 375, and the clip frames 5-13 (plane 30, elev 107-150, axial -51..-60). There the tooth's
end of flank folds onto the shoulder top. The penetration *deepens* as the tooth rises (-17.4 -> -18.6 mm), because the
ray from GH through that tooth runs through the trapezius / neck, so no level fixes it. Raising the tooth also costs in
band: 0.87 -> 0.31.

## Red team

- **The pose that jams.** No jam reading applies to a ghost. The poses the drive loses are the stretched end: with the
  built 29.7 deg range, K > 29.7 drops 40 ws takes, and follow falls from 1.0 to 0.927.
- **The point that pinches.** The tooth's end of flank at overhead scaption (envsel 453: -18.6 mm on 34 / 30, -10.1 on
  32 / 32). On the ghost itself, hub 2 at 205 (-4.21) and 139 (-0.49; new against the lead, from the hub K re-seat).
- **The optimistic numbers.** The 18.83 ghost, which has no drive metal. And the proposer's proxy: 0 tooth contacts at
  hand-placed patches, with no fold rule, no re-fit and no pole.
- **The measurement I distrusted and checked.** The chain clamp: a1e(K) for 34 / 30 and 32 / 32 first returned the same
  uK, which exposed the old bk clamp. The anchor reproduces the spec's onset numbers. The pin / tooth frames are checked
  on every K-open pose.

## Verdict

DEAD at step 0. This is not a frontier point: the buildable bound at the spec law is 31.80, and the 18.83 ghost has no
buildable drive. The convergence gate does not apply: this is not a search plateau. The three full-stroke ghosts read
18.83 identically (gain over the 2nd half 0.00, over the last third 0.00, top-3 spread 0.00 points), and the death is the
pre-registered step-0 scan plus a kinematic bound over 302,595 pin starts.

**New knowledge** (it predicts beyond this row):

1. **Pin-flank K drive, arc-of-action law** (a pin or roller on one flank, which is what the spec builds). With a constant
   ratio rho, the PA lens sits around the fixed pole at ~bk2 / (1 + rho) from uK. At mu 0.087 the arc of action is
   ~27-30 deg of K at rho 1.1, ~35-37 at 1.5, ~40-44 at 2.0 and ~45-48 at 2.5, nearly independent of the dyad split
   (32 / 32 to 36 / 28). A pin-flank drive that must carry the lead's 44 deg stroke needs rho >= 2.5 (sliding) or >= 2.0
   (rolling), and its pin then sits within ~13 mm of uK, on hub K's own O20 rim. **Scope:** this holds for a pin (point /
   cylinder nose) only. The parent row's dead-row audit (f9ceb81, onetooth-slowlaw-knuckle-3r_audit_toothpair.py) shows
   that a tooth-tooth (spherical involute) pair, whose contact passes *through* the pitch point, carries 46.7-47.3 deg at
   rho 1.0-1.5 at the lead's own dyad, with a ghost of 18.83 / 261 there. That path needs no re-seat: this row's re-seat
   ghost is the same 18.83 / 261.
2. **Tooth-sweep law** (measured for link-2 contact at 20-30 mm from u2). A link-2 tooth there sweeps the
   overhead-scaption shoulder top at the stretched end, 10-19 mm deep, at every level up to R 67. The lead's two-stage
   drive avoids exactly this by keeping its link-2 element as a rim lobe inside hub 2's skirt (r <= 11.5). Any one-pair or
   cam drive, the involute pair above included (its pole is ~15-17 mm from u2 at rho 1.0-1.5), must measure its link-2
   tooth sweep before it claims anything. docs/research/shortk_onetooth/metal.py does that on any flank locus, with frames
   checked. The alternative is to keep the link-2 element within ~12 mm of u2.
3. **Simplest surviving pin-flank cell, if anyone wants it.** A rolling pin on hub K's cap. Rho 2.0-2.15 (the lead's own
   law), pin 12.9-13.6 mm from uK, contact 20-30 mm from u2. It dies on point 2 unless the link-2 flank is moved inside
   hub 2's rim, which is the lead's lobe again.
4. **Kit trap.** The lead's model stack clamps bk1 / bk2 to [26, 32] / [38, 48] (roller-longdyad's old search box). Any
   re-seat row built on it must restore the dyad after `_clamp`, or it silently measures 32 / 38.

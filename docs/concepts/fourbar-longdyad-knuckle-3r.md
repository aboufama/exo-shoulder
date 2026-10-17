# fourbar-longdyad-knuckle-3r - toggle four-bar knuckle (strap cell), LISTED FOR THE USER'S B1 RULING

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the four-bar as a *stacking* problem
   before a *law* problem: a spherical four-bar on ground link 1b puts a third layer (the coupler) on top of link 1b and
   two eye columns beside two O20 housings. The designer would (a) check that each eye boss (O9 for an MR63ZZ eye, not
   just the O3 pin) clears the hub housings below the crown, (b) give the coupler the 1 mm non-adjacent clearance to
   link 1b (it is not jointed to link 1b; the spec's +3.15 is a running gap), and (c) price the stack height as in-band
   loss before trusting any law-only count. Second: read B1 as a *sub-chain singularity* question - m_sub < 5 means the
   J1-K-J3 sub-chain is near its own fold, so even a positively slaved K sees th become insensitive to K there; the
   coupled reading is physically defensible only if the four-bar's own transmission at the horn holds through those
   poses (mu_h is gated at 48-132 here for exactly that reason).
2. **Rawest material.** The bench's posed skin itself (tools/concept_bench.py exact path and its grid cache), the motion
   clips through the bench's clip frames, the fit / held-out split; not the parking estimates or the proposer's law-only
   counts (those were synthesised against Bench(110,360) workspace poses - the verification sample - so they are not an
   independent check; held-out is).
3. **Methods and tools.** Closed-form spherical four-bar (crank cone about u2, horn azimuth from A cos b + B sin b = C),
   the generic slaved-K inverse (th -> tau -> q2, K, q1, q3), the lead's verified chain model (longstroke-slipper ->
   roller-longdyad -> sidecar -> frontload -> geneva-pinknee -> minarc kit-rule classes) with its skin, in-band,
   near-touch and part-pair checks, per-pose bodies for the coupler (member 8, its rotation about GH from the pin pair),
   the farm sweep (tools/cloud_run.py) and the frozen claim protocol.
4. **What shows the number is right, other than me.** The bench (Bench(60,160) fast, then the frozen shape on
   Bench(110,360) exact and held out), the verifier harness pattern (frozen + audit near-touch + th_margin), the B1 count
   by |K| band, and a red-team pose list (overhead cone, across-the-body, behind-the-back, the toggle frames).

(Results, limiter and red team below are filled in as measured.)

## What was built (docs/concepts/models/fourbar-longdyad-knuckle-3r.py)

The lead's chain on the 28/50 (or 30-32/48) K dyad at the verified seats, loaded unchanged from
longstroke-slipper-knuckle-3r.py and its parents (skin, in band, near-touch audit, part pairs, knee, O20 stacks). The K
drive (hub-2 lobe, bell crank, nose / roller, flank, clock spring) is deleted. In its place:

* **law**: the closed-form spherical four-bar on ground link 1b (crank cone about u2, horn azimuth from
  A cos b + B sin b = cos c - cos rh (pc . uK), branch br), tabulated per 0.25 deg of q2 travel; the usable window is
  the longest run with real closure, horn transmission 48-132 deg (PA <= 42 where the coupler drives K), K inside its
  stops (-1.5 deg .. stop B at a1max <= bk1 + bk2 - 5.5), kit dyad margin m3e >= 5 and th(q2) monotone with rate <= 3.45.
  The seed reproduces the proposer's numbers exactly (window th 6.22-122.67, K -1.12..79.15, mu_h 59.5-129.0);
* **IK**: th -> tau on the window -> q2, K, q1, q3 in closed form; every pose is forced (K is never parked on a stop);
* **B1 switch** `b1read`: `family` (default, today's reading, the row's numbers: min(m_sub, m_eff) >= 5 on every forced
  pose) or `coupled` (m3e >= 5 only; LISTED FOR B1, never claimed);
* **metal, per pose, real size**: crank lug (3 mm Ti, 6 wide, formed to the sphere, integral with link 2 at link 2's
  layer at hub 2, O9 eye boss = MR63ZZ + 1.5 wall; turns with q2), horn lug (same, link 1a at hub K, + hl), coupler (3 x 4
  mm Ti arc, member 8, its own per-pose rotation about GH mapping the reference pin pair onto the pose's pin pair; a
  linear joggle between two pin-end floors = max(lug top + 0.15, link 1b's top + 1.0) + zcp; O9 eye columns from lug to
  coupler top sampled as the coupler's metal). Part pairs: coupler vs all four hub housings, L1a / L1b / L2 (1 mm; 0.15
  only within the eye of its own pin), both lugs, knee / pad / E; lugs vs the hubs and straps they are not part of.
  `clay=1` (coupler in link 1b's own layer, beside it) was added and measured: it collides with link 1b (121 of 160
  poses on the family best) - the coupler of a useful four-bar runs along link 1b, so it must be stacked over it.

### Spec corrections (measured, not assumed)

1. **The strap seed is not buildable as specified.** Its horn pin sits 11.3 mm off hub K's axis, so the O9 eye boss of an
   MR63ZZ eye reaches 0.7 mm INTO hub K's O20 housing below its crown (CPL-hubK -0.7 mm): every pose is lost (gap 375
   under both readings, 114-187 of 160+60 poses binding on CPL-hubK). A horn eye beside an O20 housing needs >= 15.5 mm
   lateral; rh was swept 15.5-24 deg and the four-bar re-synthesised (the proposer's law-only numbers do not transfer).
2. **The coupler is not jointed to link 1b**, so it gets the 1 mm non-adjacent clearance over link 1b, not the spec's
   0.15 running gap (+0.85 mm of stack).
3. **The judge's knee re-fit for the strap cell (lE 74.3, lc 15.7, phiE 18.4, phib -77.8) hits pad-E on 109 poses** of
   the fit bench; the lead's knee (ang_min raised to 26.88) and swept knees are used instead.
4. The proposer's four-bar seeds were synthesised by counting law-only poses ON Bench(110,360) - the verification
   sample (lesson c). Here every search runs on Bench(60,160); Bench(110,360) frozen and the held-out bench are the checks.

## Search (all on Bench(60,160) fast, farm; sweeps/fourbar-longdyad-knuckle-3r.json, 2520 configurations in order)

* coarse: 300 random four-bars (rc 10-24, gc +-180, rh 15.5-24, c 20-65, br +-1, k0 -1..32, hl, zcp, bk1 28-32 / bk2 48-50,
  a1max = bk1 + bk2 - 5.5, lead knee or swept knee) pre-filtered on the law window alone (th window covering <= 22 .. >= 100),
  under both readings; then 120 coupled four-bars with the TOGGLE constraint (|K| <= 1.5 deg on th 41-44.5) and 100 local
  perturbations of the top configurations;
* CMA-ES (tools/concept_cma.py, popsize 8, 600 s, one 8-vCPU farm job each) from the top 2 of each reading, 11 dims
  (rc, gc, rh, c, k0, hl, zcp, lE, lc, phiE, phib).

| run | evals | best gap | gain 2nd half (score pts) | gain last third | top-5 spread | gate |
|---|---|---|---|---|---|---|
| CMA family-0 (from 55.94) | 457 | 53.26 | 0.073 | 0.036 | 0.022 | passed |
| CMA family-1 (from 58.05) | 369 | 53.35 | 0.196 | 0.156 | 0.025 | passed |
| CMA coupled-0 (from 45.24) | 793 | 34.56 | 0.000 | 0.000 | 0.182 | passed |
| CMA coupled-1 (from 60.07) | 377 | 45.69 | 0.818 | 0.113 | 0.076 | passed |

The two family runs land within 0.09 gap of each other from different starts; the coupled runs end in two basins (34.56,
45.69) - the coupled landscape is multi-modal (the toggle basin vs an open-K basin).

## Results (Bench(60,160) fast; near-touch 2 mm objective, round-9 rule)

| reading | gap | score | reach | follow | ib14 | ib10 | contact | K range used | notes |
|---|---|---|---|---|---|---|---|---|---|
| family (today's B1 reading; THE ROW) | 53.26 | 80.63 | 0.650 | 1.000 | 0.690 | - | 0.024 | 27.6-53.8 deg | hub 2 in band 0.10 |
| coupled (LISTED FOR B1, not claimable) | 34.56 | 87.43 | 0.806 | 1.000 | 0.712 | - | 0.041 | 2.0-65.9 deg | toggle: K <= 0.8 deg on the elev-150 clip |

Lead (slipper-nose-knuckle-3r) on the same fit bench is ~16-17 fast and 18.49 verified - neither reading of this
morphology is near it.

### B1 count (law-only = law window + knee + slide, Bench(110,360) workspace, fails = min(m_sub, m_eff) < 5)

| config | law-only coupled | law-only family | 0-1 | 1-3 | 3-6 | 6-10 | 10-20 | >= 20 | m_sub < 1 | overhead coupled / family |
|---|---|---|---|---|---|---|---|---|---|---|
| proposer's strap seed (kinematics only; its metal fails) | 313 | 180 | 27/27 | 19/19 | 15/15 | 20/20 | 38/38 | 14/194 | 75 | 22/28 / 8/28 |
| coupled coarse best k444 | 280 | 158 | 23/23 | 21/21 | 15/15 | 18/18 | 45/51 | 0/152 | 53 | 12/28 / 5/28 |
| coupled CMA best (34.56) | 286 | 170 | 0/0 | 27/27 | 21/21 | 19/19 | 41/41 | 8/178 | 62 | 15/28 / 7/28 |
| family CMA best (53.26) | 250 | 234 | - | - | - | - | - | 16/250 | 7 | 12/28 / 9/28 |

Every taken pose under |K| 20 deg fails today's reading in every configuration measured (the judge saw "every pose under
|K| 10"; on these four-bars it is every pose under 20 except 6 of 51 at 10-20 on k444). So the family-optimal four-bar keeps
K open 27-54 deg on EVERY pose, i.e. it never uses the toggle.

## Measured limiters

1. **Family reading (the row): B1 -> hub 2 off the skin.** With K held >= 27 deg everywhere, hub 2 never returns to the
   lead's rest seat: on the raise-overhead clip frames (elev 150, th 43) it needs 80.6 mm from GH (the proposer predicted
   71-79 at a1e 40), so its fitted level is 80.6 vs ~62 and hub 2 is in band on 0.10 of the clip frames (median 24 mm off
   the skin). The chain alone (four-bar metal deleted, attribution only) scores 46.5: B1 costs the chain ~22 points before
   any drive metal.
2. **Coupled reading: the four-bar's own metal.** Ghost attribution on the coupled k444 (law kept, lugs + coupler + eyes
   deleted): 45.24 -> 24.06 (plain 31.31 -> 18.54; ib14 0.773 -> 0.868; reach 0.769 -> 0.800). The crank lug of link 2
   sweeps a ~17-20 mm circle round hub 2 with q2 (in band 0.03, median 18.9 mm off the skin: it must clear the highest skin
   it ever passes over) and the coupler stacked over link 1b (link 1b top + 1 mm) is in band 0.20 (median 18.7 mm). The
   drive costs ~21 gap points - the planner's "the drive is ~14-16 of a knuckle's points", plus the third layer.
3. **The 2 mm near-touch** adds 14 points on the coupled best (plain 31.31 vs near2 45.24 on k444; min metal 0.82 mm).

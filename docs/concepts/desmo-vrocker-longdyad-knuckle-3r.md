# desmo-vrocker-longdyad-knuckle-3r (round 12, pick 4)

Desmo V-rocker long dyad. The pinned-horn slot (nose on link 1a, swept slot in the crank tip) drives a lengthened 32/48
K dyad on a steep linear law (kK 2.5). Stage 1 is a desmodromic conjugate cam: two open rim lobes stacked on hub 2's cap
ring ride two crowned pins on a V short arm of the crank. There is no spring, roller, rod or ball link. 3 active DOF
(J1, J2, J3), K slaved and never read, 0 passive translations.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Kill the row cheaply before drawing the
   drive. Every reach gain on this row comes from the long dyad opening K further on the stretched poses. The round-12
   judge and the spiral-lobe row measured where that opening goes on the same chain (34/48): hub 2 and link 2 swing
   into the bunched posterior deltoid. So the first job is the chain's own ceiling on 32/48 with no drive metal at all,
   the judge's gate 3, run on the claim bench (frozen, exact). The conjugate lobes, the V arm and the slotted plate can
   only add metal. A designer would also treat the stroke cap (kcap) as a free cut: the conjugate pair's stroke is a
   stop-B position, and a lower cap turns K-open contact poses into plain fold losses. They would read the per-pose
   table, not a sum: which poses each extra degree of K buys, and which part enters the skin there.
2. **The rawest material.** The posed skin, through concept_bench's exact signed distance per pose (CB_EXACT=1,
   Bench(110,360)), and each part's metal (M.rigid, M.contact, M.link_pts) placed in that pose's frame. Also the
   workspace pose list (plane / elev / axial) and the clip frames. The per-pose dump (g0_<tag>.json: K, th, taken /
   contact / slide / fold, part and depth) is the data the cap and onset are chosen from. The digested counts (fold 64,
   contact 14) are not.
3. **The methods and tools.** The real chain model: spiral-lobe-longdyad-knuckle-3r.py, loaded unchanged (it loads
   inband-rssr-knuckle-3r.py unchanged), switched to 32/48, stop B 74.5 and kK 2.5. The RSSR does not exist in this
   morphology, so its metal is deleted and its range limiter is replaced by the V-rocker's stroke,
   dK_lim = min(kcap, 78.5). The frozen protocol: fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360)
   exact. A per-pose attribution harness: signed distance per part per pose. The farm is at its budget line ($24.19
   against $24.40 at 16:22 UTC), so everything runs locally, with at most 2 niced processes.
4. **What, other than me, shows the number is right.** The bench's exact path on the frozen shape. The judge's own
   control cells: spiral-lobe's 34/48 ghost (18.84 seed, 17.86 best) and pick3's ghost (18.32), run through the same
   harness. The judge's law-only count at 32/48 (278-282 workspace poses taken by the law alone; envsel 276-278). Then
   the adversarial verifier and the alignment auditor, and the red-team pose list: contact poses by part and depth,
   the K-open takes, and the overhead cone (elev >= 140).

## Model

`docs/concepts/models/desmo-vrocker-longdyad-knuckle-3r.py` loads `spiral-lobe-longdyad-knuckle-3r.py` unchanged (which
loads `inband-rssr-knuckle-3r.py` unchanged) and switches it to the V-rocker cell:

- the K dyad 32/48, stop B a1max = bk1 + bk2 - 5.5 = 74.5, a linear law kK past the onset margin smhi;
- the parent's RSSR is not part of this morphology. Its metal is deleted (IB_GHOST=all) and its range limiter
  (transmission, rod clearances) is REPLACED by the V-rocker's stroke: dK_lim = min(kcap, s2cap). kcap is the
  conjugate-lobe pair's stroke (the cap); s2cap is the re-seated pinned-horn slot's stroke on 32/48 (78.5, judge
  section 4, reproduced below);
- the V-rocker's own metal is NOT sampled: the V arm, the two pins, the slotted crank plate and the nose boss on link 1a.
  The two lobe tracks (profile r <= 9.1) sit inside the O20 hub's envelope. **Every bench number in this row is a
  GHOST**: the chain's ceiling before the drive's metal. That is the round-12 judge's gate 3 for this row, never a claim.

Seats, knee, J2 / J3 placement and every part of the chain are pick3's (the spiral-lobe row's), as the judge specified
("the chain is the same"). The chain's checks are the parents' own: closure, knee window, parts pairs, frozen protocol
and the per-pose signed distance. The stage-1 / stage-2 gates (gate 1) are a separate closed-form harness on the 32/48
geometry, read from the slipper-nose model built at 32/48 with the lead's seats (as the judge's `inv_long.py` does).

## Gate 1: the conjugate lobe pair on 32/48 (closed form; fails at the spec's own floor)

Harness: scratchpad `vr/pack.py`. Pin paths come from the proposer's `stage1.follower()` construction: the crank turns
sig*K/g about its axis dR, link 2 turns t = K/kK about u2, and the path is read in link 2's frame at each track's
level. The stage-2 sign sig comes from the judge's re-seated nose at each g (32/48: g 2.4 at beta -177.5 / r_c 21.0,
stroke 78.25; g 2.6 at r_c 18.5, 78.0; g 2.9 at r_c 16.0, 76.75). The gates per pin are:

- pitch in [floor + r_pin, 11.46 - r_pin];
- both pressure angles <= 38.03 (mu 0.087);
- a monotone pitch (A rising, B falling, by >= 0.2);
- axial drift <= 0.6.

The gates per pair are: pins 3.5-5.0 apart on the V arm, and packing. Pin B's swept circles (+0.3) must stay clear of
lobe A's contact envelope. The pin that passes the other track's level must also clear that track's base ring by 0.3.

Control: the proposer's pins on the lead's geometry reproduce exactly (8.0 / 182: pitch 8.59-9.94, PA 34.6; 8.125 / 153:
10.07 -> 8.54, PA 35.1, drift 0.2), and the same pins on the 32/48 geometry read 8.58-9.94 / 34.6 and 10.06 -> 8.54 /
35.1. In the stage-1 frame (u2, dR, hub-2 level) the long dyad changes almost nothing.

| convention (g 2.4, kK 2.5) | pairs to K 56 | to 60 | to 64 |
|---|---|---|---|
| proposer's (pin r 1.18, both pins on one level, no base-ring check): control | 72 (PA 34.75) | 15 (36.4) | 2 (38.0) |
| real O2.5 pin (r 1.25), one level | 16 | 2 | 0 |
| r 1.18, track B one track lower (-1.5) | 16 | 0 | 0 |
| **as specified: r 1.25, track B lower (-1.5)** | **0** (A 4, B 0) | 0 | 0 |
| r 1.25, track B ON TOP (+1.5): designer fix | 16 (PA 34.75) | 2 (36.4) | 0 |
| + the passing pin clears the other track's base ring (floor 7.3) by 0.3: either stacking, g 2.4 / 2.6 / 2.9 | **0** | 0 | 0 |
| same, base ring relieved to r 7.0 (housing wall 1.5 over the MR117 OD), B on top | 40 (PA 34.75) | 6 (36.4) | 0 |

- **Packing in azimuth is never the binder.** Lobe A's contact arc and pin B's swept arc never share an azimuth in
  link 2's frame, for any pair found (the margin is unbounded). So the "track A vs pin B" collision the judge flagged
  as unchecked does not occur where the pins contact.
- **The binder is the base ring.** Each pin's pitch spans the whole window, from the floor at one end of the stroke to
  the skirt at the other, because that is what keeps the pressure angle under 38. So the pin that passes the other
  track's level always comes within ~0.03-0.1 mm of that track's base circle. With the spec's floor (profile >= 7.3)
  and a 0.3 mm pass clearance, **no conjugate pair exists** at any stroke 56-64, g 2.4-2.9 or stacking. The pair
  exists only if the base ring drops to r 7.0 under the passing pin, with track B on top (40 pairs to 56, 6 to 60,
  none to 64). That is a 0.3 mm knife edge on the hub-2 cap ring's wall.
- A higher g does not "lighten" stage 1 here: at g 2.6 and 2.9 there is no single feasible pin even before pairing.
  The crank turns less, so the pitch change the lobe needs comes from link 2's turn alone, at a higher pressure angle.

Gate 1 therefore **fails as specified** and passes only at the cap-56 / 60 cells with two changes: track B stacked on top,
and the base ring locally relieved to r 7.0. The judge's 64-deg cell does not exist under any convention with r 1.25 pins.

## Gate 3: the chain's ghost ceiling on 32/48 (frozen exact, per pose; fails)

Protocol: fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact (CB_EXACT=1). The RSSR is deleted and the
V-rocker metal is not added, so this is the chain's ceiling. Pass (the lead's pre-registered bar, the same as pick 1's
gate 0): <= 17.5 with <= 4 contact poses. Per-pose dumps: scratchpad `vr/g0_<tag>.json`.

| cell (32/48, stop B 74.5) | frozen gap | ws taken | contact poses (depth sum, mm) | fold | slide | ib14 | overhead taken |
|---|---|---|---|---|---|---|---|
| lin kK 2.5, onset smhi 19.46, cap 56 | 19.71 | 262 | 5 | 80 | 15 | 0.888 (follow 0.982) | 8/28 |
| kK 2.5, smhi 19.46, cap 64 | 17.98 | 270 | 7 | 70 | 15 | 0.888 (follow 0.982) | 8/28 |
| kK 2.5, smhi 16.84, cap 56 | 17.91 | 267 | 8 | 71 | 14 | 0.901 | 8/28 |
| kK 2.5, smhi 16.84, cap 64 | 17.31 | 270 | 9 | 67 | 14 | 0.901 | 8/28 |
| kK 2.5, smhi 14, cap 56 (= cap 64: the cap is idle, K max taken 52.5) | 17.48 | 268 | 6 | 72 | 14 | 0.896 | 8/28 |
| kK 2.5, smhi 13, cap 56 | 17.40 | 267 | 6 | 73 | 14 | 0.906 | 7/28 |
| kK 2.5, smhi 12, cap 56 | 18.52 | 263 | 6 | 80 | 11 | 0.905 | 7/28 |
| kK 2.5, smhi 10, cap 56 | 18.87 | 259 | **3** | 88 | 10 | 0.914 | 7/28 |
| **kK 2.4, smhi 14, cap 56 (best gap)** | **17.23** | **269** | **6 (18.66)** | 72 | 13 | 0.896 | 8/28 |
| kK 2.6, smhi 14, cap 56 | 17.48 | 268 | 6 | 72 | 14 | 0.896 | 8/28 |
| kK 2.3, smhi 14, cap 56 | 17.52 | 268 | 6 | 73 | 13 | 0.896 | 8/28 |
| kK 2.4, smhi 11, cap 56 | 18.85 | 261 | **3** | 85 | 11 | 0.895 | 7/28 |
| 30/49 (stop B 73.5), kK 2.5, smhi 14, cap 56 | 17.91 | 267 | 8 | 72 | 13 | 0.901 | 8/28 |

References through the same harness family: the lead slipper-nose 18.49 (261 taken, 2 contacts); spiral-lobe's 34/48
ghost, best 17.86 (269, 8 contacts); pick3's ghost 18.32 (260, 2).

**Gate 3 fails.** Every cell that takes >= 267 poses (17.23-17.48) carries 6-9 contact poses. The only cells with <= 4
(onset 10 / 11: 3 contacts) take 259 / 261 poses and read 18.87 / 18.85, worse than the lead (18.49 at 261 taken,
2 contacts). As on 34/48, contacts and takes trade
almost one for one at the bottom of the frontier.

### The six contact poses are the same in every cell at onset 12-14

| pose | plane / elev / axial | th | K (onset 14, kK 2.4) | deepest part (mm) | what moves it |
|---|---|---|---|---|---|
| 117 | -90 / 45 / 135 | 113.1 | 48.2 | link 2 -1.7 | K: onset 19.5 -> 14 takes it from -2.9 to -1.7; gone only as a fold (onset 19.5 cap 56) |
| 127 | -75 / 45 / 120 | 103.5 | 34.7 | link 2 -0.43 | -1.2 at onset 16.8; -0.8 at onset 12 (deeper at lower K) |
| 129 | -75 / 60 / 120 | 108.0 | 41.0 | link 2 -7.7, hub 2 -3.5 | in every cell (-4.3 even at onset 10) |
| 139 | -60 / 60 / 105 | 97.4 | 26.0 | link 2 -3.0 | in every cell from onset 12 up |
| 264 | 30 / 165 / -60 | 41.9 | 0 | hub K top -5.05 | the lead's own pose (K closed): not the long dyad's |
| 316 | 60 / 150 / -105 | 104.8 | 36.4 | link 2 -0.72 | -2.5 at onset 12: deeper at LOWER K |

- **No K cut (stop B / conjugate-lobe cap) makes the trade.** On the onset-14 table, a cap at 48 sheds one contact
  (117) and loses 5 takes; a cap at 40 sheds 2 and loses 12. The contacts sit at K 26-49, inside the 122 K-open takes
  (K up to 52).
- **Two of the six get deeper as K falls** (127 and 316 at onset 12). There, link 2 meets the skin with hub 2 nearer
  rest. So these are not over-openings: the stretched poses' link 2 sits low over the posterior deltoid
  (plane -90..-60, elev 45-60, high external rotation) and over the overhead internal-rotation fan (316).
- The cap is idle from onset 14 down (K max taken 52.5 < 56). The judge's 60 / 64-deg lobe cells buy nothing there.
  At onset 16.8 the 64 cap buys 3 takes and 1 more contact (17.91 -> 17.31).

### Loss attribution, best ghost cell (kK 2.4, smhi 14, cap 56; 269 / 360 taken)

- **Fold 72:** 54 stretched (th >= 117.3, against the lead's wall at 106.6) and 18 folded.
- **Knee slide 13** (lead 9): 8 at K 0 (folded side and the elev-165 fan; the lead's contact pose 237 becomes a slide)
  and 5 stretched at K 26-51 (180, 183, 343, 372, 396).
- **Contact 6.**
- **Overhead (elev >= 140):** 8 / 28 taken; losses 13 fold, 5 slide, 2 contact.
- Min metal over taken poses: 1.25 mm, so the near-touch gap equals the plain gap.

The long dyad moves the stretched wall by ~11 deg (+19 stretched poses closed vs the lead), and the chain spends 4 of
them on contacts. Before any drive metal, the net is +8 takes (269 vs 261) and +4 contacts (6 vs 2).

## Red team (my own best cell)

- **The optimistic number is the ghost itself.** 17.23 has no V arm, no pins, no slotted crank plate (~25-30 mm long
  arm from hub 2's rim to the nose) and no nose boss on link 1a at r_c 21 from a medial hub K. The judge's flank probe
  put a link-1a lug at r_c 17.5 on a medial hub K into the skin on 79 fit poses. With the RSSR's metal added unrefit,
  pick3's drive added 18 fit contacts on 34/48. The drive can only add metal, so 17.23 is a ceiling.
- **The point that pinches:** pose 129 (plane -75, elev 60, axial 120). Link 2 is 7.7 mm into the posterior deltoid
  and hub 2's rim 3.5 mm, at K 41, in every cell. Pose 264 (hub K top -5.05, K closed) is shared with the lead.
- **The pose that jams (gate 1):** the end of each lobe's stroke. There the passing pin's pitch sits within
  0.03-0.1 mm of the other track's base circle. A 0.15 mm running gap does not fit, and a 0.3 mm clearance kills every pair.
- **The fold margin and follow:** the onset-19.46 cells lose follow to 0.982 (a clip frame not followed). Every cell
  at onset <= 16.84 follows 1.0.

## Verdict

**DEAD at gate 3** (the lead's pre-registered kill rule, carried from pick 1: "a fail there kills this row too"). The
best ghost cell reads 17.23 frozen exact with 6 contact poses (18.66 mm summed) against the bar of <= 17.5 with <= 4,
before any drive metal. The cells under 4 contacts read 18.85-18.87. Gate 1 also fails as specified: no conjugate pair
exists once the passing pin clears the other track's base ring, and the pair exists only with the base ring relieved
to r 7.0 and track B on top, at caps 56-60.

The convergence gate does not apply. This is a ghost-ceiling kill over 14 cells (gain 2.3-2.6, onset 10-19.46,
caps 56-64, 32/48 and 30/49) on the claim bench, not a converged search. No CMA was run, because the ceiling's contact
count is above the bar on every cell at the lead's reach or better.

Complexity (tools/simplicity.py v2.2, desmo-slipper's record convention): **16.0** as specified (bodies 5, joints 8,
loops 3, sliding 2, springs 0, catalogue 14); **22.0** strict (the conjugate pair as 2 pairs + 1 loop). The judge read
19.0 / 17.0 / 25.0 on the lead's convention.

## New knowledge

1. **The long dyad's chain binder does not depend on the dyad length, the gain or the drive.** On 32/48 as on 34/48,
   the same link-2 / hub-2 contact cluster (plane -90..-60, elev 45-60, axial 105-135) and pose 316 appear in every
   cell whose takes beat the lead. Some contacts deepen as K falls. Any K-drive row on a long dyad with pick3's seats
   inherits this ceiling: ~17.2 frozen with 6 contacts, or ~18.9 with 3. That holds for this row, spiral-lobe,
   desmo-spiral-rssr and any future conjugate / groove drive on the same chain. What would move it is a J2 seat or a
   link-2 route over the posterior deltoid, a seat question (closed for fit-bench re-fits).
2. **32/48 at kK 2.4 beats 34/48 at kK 2.8** on the ghost (17.23 / 6 contacts vs 17.86 / 8), with the same takes (269).
   A gentler gain on a shorter-stretch dyad is the better long-dyad cell, though not good enough.
3. **Conjugate open lobes on one cap ring are bound by the base ring, not by packing in azimuth.** A pitch window wide
   enough for PA <= 38 puts each pin at the floor at one end of its stroke, so the other track cannot keep its base
   there. Stacked conjugate tracks need a relieved base ring (r 7.0 under the passing pin, a 1.5 mm wall over the
   MR117) or an offset pitch window, which costs the pressure-angle margin. Put track B on top: pin B's falling
   pitch then never crosses track A.

## Files

- Model: `docs/concepts/models/desmo-vrocker-longdyad-knuckle-3r.py` (ghost only; RSSR deleted, the V-rocker stroke as
  the K range).
- Sweep: `docs/concepts/sweeps/desmo-vrocker-longdyad-knuckle-3r.json`, one entry per gate-3 cell in run order.
- Row: `docs/concepts/rows/desmo-vrocker-longdyad-knuckle-3r.json`.
- Motion preview: `docs/concepts/viz/concepts/desmo-vrocker-longdyad-knuckle-3r.js` (best ghost cell's chain, the
  law cut at the 56-deg cap, the V-rocker drawn schematically: crank on link 1b, V arm with two pins on hub 2's two
  tracks, long arm to the nose on link 1a).
- Scratch harnesses (not committed): `vr/gdump.py` (per-pose frozen dump), `vr/pack.py` (gate 1), `vr/mkviz.py`.

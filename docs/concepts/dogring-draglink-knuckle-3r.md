# dogring-draglink-knuckle-3r - dog sector + spherical drag link driving the slaved knuckle K

## Deeper version (answered before the work)

1. **What a top mechanism designer would do that the spec does not ask for.** Lay the drive out in the *layers that
   already exist* before pricing it: at hub 2 link 1b is the LOWER member (f2 .. f2+3) and link 2 the UPPER (f2+3.15 ..
   f2+6.15, measured on the model's own link samples); at hub K link 1a is lower (fK) and link 1b upper (fK+3.15), and
   both links ramp DOWN to the skin within r 11.5-14 of each hub. So (a) the spec's ring "at link 1b's top + 0.15" is
   link 2's root layer, which link 2 sweeps over its whole q2 range - physically impossible; the honest stacked control
   sits above link 2 (f2 + 6.3); (b) a ring in the skin-face layer (f2) must be a C-SECTOR that clears link 1b's root
   over the swing, and then the DOG can be link 2's own root flank (it ramps down through that layer at r 11-13) - no
   dowel, PA 0, no sliding; (c) the arm, the drag link and the horn must swing ~35 deg (arm) and ~75 deg (horn)
   RELATIVE TO LINK 1B, which owns the corridor between hub 2 and hub K - so the binding check is not the PA table but
   the swept clearance of each drive body against link 1b over the drive's own range. Synthesis must be done on the
   fitted design's own u2 / uK (the judge's seeds came from another fit and fail PA at K = 0 here).
2. **Rawest material.** The posed skin itself through the bench's grid distance (every drive point is a rigid-part
   sample priced pooled by the bench, not a side harness), the motion clips of Bench(60,160) / Bench(110,360) and the 952
   held-out poses, the model's own link / hub samples (levels and azimuths read off them, not from docs).
3. **Methods and tools.** Spherical 4R closure by continuation (all axes through GH) with PA at both pins; vectorised
   synthesis per K-dyad cell on the fitted u2 / uK (~23k candidates per cell); the parents' per-t law gates (th monotone,
   rate <= 3.45, lift-off, stop B); swept-volume clearance of sector / arm / drag link / horn vs link 1b, hub 2, hub K in
   link 1b's frame over K = 0 .. table end -> dK_lim (stop B dowel there, every pose past it lost on every bench); per-pose
   collide() with the family's 1 mm rule; the CPU farm for every batch; frozen exact Bench(110,360) for the claim.
4. **What shows the number is right, other than me.** tools/concept_bench.py (the outside judge; pooled in-band over all
   metal points), the frozen-exact protocol of the family (fit fast, freeze, wear on Bench(110,360) exact), the held-out
   bench, and the round-11 verifier / red team (pose list: rest, overhead elev >= 140, across the body, behind the back).

## Verdict (screened, 2026-10-17 10:45 UTC)

**Claimed configuration** (k 1107 of the sweep; frozen exact is the pick, never fast):
`{"bk1": 34, "bk2": 46, "a1max": 74.5, "smhi": 20.13, "dr_a1": 26.32, "dr_t1": 3.69, "dr_a3": 17.71, "dr_t3": -43.94, "root_off": -59.3,
"ring_layer": 0, "arm_up": 1, "dr_hl": 7.715, "dl_a": 1, "dl_h": -1, "dl_lift": 0}` on the lead's frozen seats.

| bench | gap | score | reach | follow | in-band 14 | in-band 10 | contact | overhead (elev >= 140) |
|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast (fit) | 17.19 | 93.75 | 0.7875 | 0.95 | 0.8723 | 0.523 | 0.0317 | 2/12 |
| **Bench(110,360) exact, frozen** | **22.64** | **91.77** | 0.7333 (264/360) | 1.0 | 0.8638 | 0.520 | 0.0235 (9 poses) | 8/28 |
| held out (952), frozen | 25.36 | 90.78 | 0.7038 | 1.0 | 0.8617 | 0.518 | 0.0191 (17 poses) | 19/71 |
| lead slipper-nose (same protocol) | 18.49 / held 23.45 | 93.28 | 0.725 | 1.0 | 0.8955 | | 0.0054 | 8/28 |

Gap split (frozen): reach 16.67 + in-band 3.62 + contact 2.35. Near-touch: min metal 0.06 mm over taken poses, gap with metal
< 1 mm as contact (near1) 31.89, near2 53.61. Contact depth (T5): 9 poses, 26.1 mm summed, deepest 10.9 mm; the dog sector /
arm ("crank") is in 5 of the 9 (held: 9 of 17), hub 2 3, horn on hub K 2, hub 1 2. Own-state fold margin (the lead verifier's
th_margin, copied): min 5.39 deg on 374 taken bench poses (held 5.19 on 872), **none under 5** - the strict reading passes.
Same-protocol references on file: the lead 18.49 / 23.45; the first build of this row (ring stacked above link 2) 26.07 / -.

**It does not beat the lead.** The drive works kinematically (positive, coaxial, PA <= 42, no lobe, no sliding pair, no
follower; 3 active, 0 passive translations) and buys +3 bench poses (264 vs 261) and the strict fold margin, but its metal
costs pooled in-band and adds contacts:

* **Pooled in-band, measured by the bench itself (fast, drive vs its ghost = same law, drive metal deleted):** ring stacked
  above link 2's root + horn above link 1b: ib14 0.8318 vs 0.8983, **-0.0665** (the judge's -0.061/-0.065 as specified,
  confirmed); dog sector in hub 2's skin-face layer + arm up-joggle: 0.8472 vs 0.8950, **-0.0478** (judge's -0.038 for the
  ring alone; the horn is the rest). Gate B (>= -0.02) FAILS by 2.4x. Per part (claim, frozen): sector + arm 0.895 in band
  (median 11.2 mm), drag link 0.683 (13.3 mm), **horn 0.227 (16.8 mm)** - the horn is now the largest term.
* **Why the horn sits high (new, predicts beyond this row):** on the fitted u2 / uK, a spherical 4R from J2's axis to K's
  axis with PA <= 42 deg to K >= 60 exists only with the horn pin at t3 in [-110, +35] deg from link 1b's direction about
  uK (0 of ~3000 survivors in 4 cells outside it, 60-95k candidates). K's 75-deg swing then carries the horn across link
  1b's root band (+-34 deg at r 15), and link 1b's root ramps down through link 1a's layer at r 11.5-13. So the horn must
  ride ABOVE link 1b's root on hub K's housing (hl >= 7.15 = fK + 6.15 + 1 mm) and its eye at r_h >= 17 - every K drive
  that lands on link 1a near hub K pays this, unless link 1b's root ramp is pushed out past r_h + 4.
* **The dog sector layer:** the spec's "ring at link 1b's top + 0.15" is link 2's root layer at hub 2 (link 1b lower at f2,
  link 2 upper at f2 + 3.15, measured on the model's own link samples); the honest stacked control sits above link 2 (f2 +
  6.3) and costs 0.43-0.51 in band on the sector. In the skin-face layer the sector is 0.87-0.91 in band, and **link 2's
  own root flank is the dog** (it ramps down through that layer at r 11.8-13; ahead of the lug face link 2 never comes,
  so the arm root may joggle up over link 1b's root there - the measured trick that took fast 19.66 -> 17.19). The price:
  the sector in the skin-face layer is in 5 of the 9 frozen contacts. A sub-ring under hub 2 (f2 - 3.15) was measured:
  contact 0.09-0.12, dead.
* **Reach wall (law-only Bench(110,360), gate A, target 282):** 273 / 360 (held 687 / 952) at the claim, 279 / 360 with a
  high-gain 4R (g >= 2, arm arc >= 30, dK_lim 87). Lost (claim): law end th > 120-126 (PA end of the 4R table) 44-47,
  effective-dyad margin m3e < 5 15-18, folded 15, knee 10. The fast bench (60,160) is blind to the stretch: every config
  reaches 0.7875 there whatever its stroke, so the fast search drifts to short, low-gain arms (g 1.3-1.9) that save metal;
  dK taken stays <= 44-46 on the frozen bench even at dK_lim 65. The proposer's 284 / 727 needs g 2.1-2.45 AND the arm
  along link 1b at the stacked level - i.e. it is the in-band-expensive layout.
* Overhead cone: 8 / 28 frozen (lead 8 / 28): the drive does nothing for the folded side (15 folded + knee losses), as
  predicted.


**Law vs metal split (frozen exact, same fit, LS_GHOST=1 deletes the drive's metal only):** ghost 18.03 (reach 0.7389 = 266,
in-band 0.8991, contact 0.0183, 7 poses) vs the drive 22.64 -> the drive's metal costs **+4.61 gap** (in-band -0.035 = 3.5 pts,
+2 contacts, -2 reach poses). The dog LAW at the claim's stroke is worth 18.03, i.e. 0.46 better than the lead's verified
18.49 - the coaxial dog does not unlock a new reach regime at in-band-cheap geometry.
**Long stroke reproduces the longstroke-ghost lesson:** the high-gain config (g >= 2, dK_lim 86.8, law-only 279 / 360) froze
at 29.84: dK taken 55.8 (vs 44), but 26 contacts (70.4 mm summed) - the stretched poses come back as contacts, not reach
(0.725).

## Red team (own)

* **Optimistic number:** fast 17.19 -> frozen exact 22.64 (+5.45, the family's usual fit-to-frozen inflation); the fast
  search's best (16.57, gen 9) froze no better: gen-8 best 16.87 fast -> 24.34 frozen (17 contacts). Selection was by frozen.
* **Pinch point:** the dog sector at hub 2's skin face: 5 of 9 frozen contacts, deepest pose 10.9 mm (shared with hub 2 /
  hub 1 at elev 165, the lead's T5 poses). Near-touch: 20 bench poses < 1 mm (min 0.06 mm).
* **Jam:** the dog engages with a step in K rate (0 -> g ~1.4 x q2-dot) at the onset; one-sided contact force-closed by K's
  spiral spring - the parents' lift-off gate holds on the law (no lift-off before the table end). The sector is parked by the
  drag link while K rests on stop A (a 4R with K fixed has no free coordinate - R17 ok). Swept clearances (link 1b frame,
  K 0 -> dK_lim): sector-link 1b >= 0.15 (adjacent on hub 2), drag link-hub K >= 6.6, arm-hub K >= 9.5, drag link-link 1b
  >= 1.56, horn-link 1b >= 1.6 mm (hub K clearance gate >= 1 mm: passes).
* **Measurement vs design:** no bench / metric change in this session; every number above is the bench's own pooled
  pricing (drive points are rigid-part samples at 2 mm spacing).

## Convergence gate (on the plain bench gap, sweep order, 1448 configs over 10 farm batches)

Not passed: gain over the second half 1.21 score points (gate < 1), over the last third 1.12 (gate < 0.5), top-5 spread
0.11 (gate < 3). The row is **screened, not dead**; the fast objective is still creeping (17.19 -> 16.57) on in-band, but
the frozen pick did not follow it (see red team).

## What would move it (open levers)

1. Push link 1b's root ramp out past r 17-19 at hub K (flat to the horn eye) so the horn can stay in link 1a's layer: the
   horn term (32 pts at 0.22) is ~-0.02 pooled by itself.
2. Select on the law-only Bench(110,360) count + frozen in-band (not fast): the high-gain arms (279 law-only) need the
   drag link to clear link 1b (dl_L1b is the binding check in 66 of 84 high-gain configs).
3. A shorter sector (ring arc ~40 deg) by moving the dog ahead of link 2's root.

## Verification (independent skeptic, 2026-10-17 11:39 UTC) - REFUTED

Harness: `docs/concepts/verify/dogring-draglink-knuckle-3r.py` (the claim's model loaded unchanged, worn by its own
frozen protocol; outputs `docs/concepts/verify/dogring-draglink-knuckle-3r_v_{bench,held}_frozen.json`). Local CPU, one
process, `CB_EXACT=1`.

| bench | gap | score | reach | follow | ib14 | ib10 | contact | overhead |
|---|---|---|---|---|---|---|---|---|
| claim reproduced, Bench(110,360) exact frozen | 22.64 | 91.77 | 0.7333 | 1.0 | 0.8638 | 0.5198 | 0.0235 | 8/28 |
| **corrected, Bench(110,360) exact frozen** | **97.83** | **64.43** | 0.3472 | 0.60 | 0.8695 | 0.4992 | 0.045 | 4/28 |
| claim reproduced, held out | 25.36 | 90.78 | 0.7038 | 1.0 | 0.8617 | 0.5182 | 0.0191 | |
| corrected, held out | 101.1 | 63.24 | 0.3277 | 0.584 | 0.8651 | 0.4932 | 0.038 | 13/71 |
| champion spherical 3R, same bench (risley-turret verifier) | | 75.94 | | | | | | |

**The fault: the Ti arm sweeps through link 1b's root.** The arm (member 9) turns with the ring about J2's axis by phi (up
to -31.5 deg at K 44). Nothing checks it against link 1b per pose. The parent's `collide()` has CRK vs hub 1 / hub K /
hub 3 / L1a / L2 / knee / pad / E, but no CRK vs L1b. The design-stage rule ("stacked over link 1b at base + T_LINK + 1")
reads `base` at phi 0, at the link-1b point nearest the arm's centreline. Link 1b's root ramps down from f2 to f2 - 5.8
between r 11.5 and 14.5 mm of J2's axis. The arm at r 15.2 mm (underside radial level 61.5 mm) passes 1.35 mm
tangentially from link 1b's ramp (underside 59.1). The two 3-mm plates overlap.

- Plate rule (stacked OR side by side, edge-row insets 1.0 / 0.5; lenient on ramps and diagonals): clearance **-0.18 mm**.
  It is < 0.15 on **every** K-open pose with K >= 3.2 deg: 183 of 374 taken bench poses and 442 of 872 held out. It
  passes only for K <= 2.8.
- At rest the arm clears link 1b by only 0.5 mm. The model holds the horn-link 1b pair (also adjacent, through K) to its
  1 mm `collide()` rule. Held to that rule here, all 374 taken poses fail.
- Dropping the 183 poses gives **v_gap 97.83**, worse than the champion's 75.94 on the same bench, so the claim is
  **refuted**.

**What passed (checked here, not taken from the claim):**

- 3 active DOF, 0 passive translations, no undetermined coordinate (with K on stop A the 4R parks the ring).
- Dog closure: link 2's leading edge sits on the lug face within 0.000 mm on all 200 K-open poses. At rest it never
  enters the sector (max -0.06 mm).
- Drag-link closure 0.0001 mm. Arm root vs link 2 never within 8 mm. Sector vs link 1b >= 2.54 mm.
- Own-state fold margin min 5.389 (held 5.189), none under 5.

**Second finding (no score effect):** the claim's own sector-vs-link-2 check (RING-L2 in `DRModel.collide`) reads
`_dogg` / `_L2ring`. `LS._frozen_model`'s `Frozen.fit` does not copy those, so on every frozen bench the check silently
returned early. Re-instated here, it loses 0 poses.

**Not refuted on the morphology.** The coaxial dog itself closes exactly. The repair is to lift the arm >= 1 mm above
link 1b's root ramp over the whole swing (the highest link-1b top under its sweep, not the one under its rest
centreline), or to route it beside link 1b. Either costs in-band, unmeasured here; the drag link and horn levels follow
the arm tip. The convergence gate was not met in the claim either.

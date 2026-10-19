# split-knuckle-twosided-3r: the winner plus a slaved K2 on link 2 that folds a2 at the folded end

Round 7 screen, 2026-10-16. Model: `docs/concepts/models/split-knuckle-twosided-3r.py` (the winner
`geneva-tail-knuckle-pinknee-3r` in its rod embodiment, loaded as its own module copy, plus K2). Status: see the row
`docs/concepts/rows/split-knuckle-twosided-3r.json`.

## The deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** They would check the drive physics before
   the kinematics. The catalogue's "crown follower on hub 2 driving K2 through a short lever" cannot work at the gains
   the folded side needs. A lever from K2 back to hub 2 is 26-49 mm long, and its tip moves sideways when K2 turns, so the
   cam would be a radial lobe touching it from the side: tan(pa) = L kK2 / r_lobe, which gives kK2 <= ~0.3 at a 45-deg
   pressure angle. The law-only scan needs kK2 1.0-1.5. So K2 takes the winner's own embodiment, mirrored: a lobe fixed
   to link 1b (hub 2's STATOR side), a rocker on link 2a beside hub 2, and an O3 pushrod with M3 rod ends to a horn on
   K2. They would also price the metal first: a slaved hub on link 2 is O20 x 12.25 + a 6 mm spring cap, and the round-7
   dead list already says "any hub on link 2 is in band only within 21-40 deg of J2". So the first measurement is a
   control with K2's metal present and its law OFF.
2. **The rawest material.** The posed skins of every bench pose, through the bench's signed-distance grids
   (`.cache/concept_bench`) and the exact libigl path for the verify bench. The HG / RS pose arrays (`CB._poses_all`) for
   the folded poses, read directly: the 8 folded fit poses (th 15.6-29.4 deg, all workspace, no clip frame) and the 23
   folded verify poses. Per-pose needed heights of hub 2, K2 and hub 3 come from sphere tracing on that skin, not from a
   summary.
3. **Methods and tools.** An exact closed-form law per pose (no spare coordinate). On the sphere, th_f(t) =
   angle(u1, R(u2, q2lo + s_f t) R(uK2, s2 kK2 (t - t0)) u3) is inverted on its valid prefix. The prefix gates are:
   monotone; rate <= 3.45; the kit's 5-deg margin on the effective dyad (a1, a2e); K2's own dyad margin; lift-off along
   the self-motion; stop B2; and the pressure angle. The rest is the verified VModel checks (closure, continuity, jam
   rule, part-part >= 1 mm, crowns and walls skin-checked, near-touch objective), the farm sweep, CMA from the top
   configurations, and the frozen exact wear on Bench(110,360).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py). The round's verifier with
   the frozen exact protocol. A control run of the same code with `k2` 0 (K2 metal present, law off), which isolates
   what the law buys from what the metal costs. A red-team pose list (`redteam` mode: the poses not taken, the closest
   metal, near-touch, and the rest / overhead / across / behind groups).

## Model (what was built)

The chain: scapula handler -> J1 -> link 1a -> K (slaved, stretched end; the winner's rim lobe, rocker, rod and horn,
unchanged) -> link 1b -> J2 -> link 2a -> K2 (O20 + 6 mm clock-spring cap, slaved, folded end) -> link 2b -> J3 ->
member 3 -> pin knee -> pad. It has 3 active DOF and 0 passive translations. K and K2 are functions of q2 and are never
read.

The members are 0 scapula, 1 link 1a, 7 link 1b, **8 link 2a** (K2's housing, K2's rocker and rod), **2 link 2b** (J3's
housing), 3 member 3, 5 pad and 6 knee. The link levels follow cam-unfold-4th's split: L2a is the upper member at J2 and
the lower plate at K2; L2b is the upper member at K2 and at J3. Part-part pairs cover every pair of the 5 hubs. Each
strap is checked against the hubs it does not end in. Strap-strap pairs are non-adjacent at >= 1 mm; the adjacent pairs
at K, J2 and K2 are checked outside a 4-mm hub zone. Both drives are checked against the hubs, the straps, the knee,
the pad, E and each other.

Simplification, stated: K2's rod and horn are sampled on link 2a. The horn end turns with K2 only on folded workspace
poses, and no clip frame engages K2 on either bench, so every in-band sample is exact.

## Kill gate (lead: 15 min, law-only)

The gate ran at the spec's seat: bK2a 37, bK2b 62, sK2 +1 (K2 rests 79 deg bent), kK2 1.0, linear law from q2lo
(`gate` mode).

| bench | folded poses (th < th_lo) | law covers | closes with the pin knee too | lead's bar |
|---|---|---|---|---|
| fit Bench(60,160) | 8 (th 15.6-29.4, all workspace) | **8** | 5 (3 lost to the knee slide) | >= 6 |
| verify Bench(110,360) | 23 | **17** | 10 (7 slide, 6 law end) | >= 15 |

Hub levels at the 5 folded fit poses that close, against the 95th percentile of the other kept poses:

- hub 2: 51.8-63.4 mm, against 59.7. One pose is +3.7 mm.
- K2: 53.7-61.2 mm, against 61.6.
- hub 3: 49.6-62.8 mm, against 79.2.

**Law-only, the gate passes.** The lead's point holds: hub 2 does swing on its a1 circle, and it is measured above, not
assumed. The same seat's METAL fails at once:

- K2's hub needs fK2 77 mm over the kept poses and is 0.5 % in band.
- The dog-leg link 2 drops to L2a 0.38 and L2b 0.22.
- The control at that seat, with K2's law OFF, measures **52.92** against the winner's 16.53 through the same code.

## Search (farm, Bench(60,160) fast, near-touch objective)

| stage | configs | best (K2 engaged on >= 1 taken pose) |
|---|---|---|
| coarse 1 (LHS, t0K2 0-8) | 244 incl. 20 controls (K2 metal, law off) | 29.09; controls best 23.25 |
| coarse 2 (sampled by K2's rest bend psi0 55-165, t0K2 ~0, smlo 5.3-10) | 256 | 30.88 (reach 0.788, ib14 0.714, 3 folded poses taken) |
| CMA-ES, 6 streams x ~450-750 (2 seats x high / low horn, sK2 -1, 2 streams also moving a1max, smhi, kK and the J2 / J3 / knee seats) | 3534 | **26.62** (s3) |

In all, 4034 configurations. An idle K2 (no taken pose on the K2 law) is flagged dishonest (+100 in the CMA), because
it is the winner plus dead metal. **Convergence gate:** every stream passes. The best stream (s3) gained 0.04 gap points
over its second half and 0.04 over its last third, with a top-5 spread of 0.03. The loosest stream (s6) gained 1.24 gap
points (0.45 score points) over its second half and 0.13 over its last third, with a top-5 spread of 0.67. All six
streams settle at 26.6-30.2 against the winner's 16.53.

**Best (s3):** bK2a 20.43, bK2b 46.24, sK2 +1 (rest bend psi0 133), kK2 1.61, high horn r_horn2 4.25, B2 54.3,
smlo 7.95; the winner's seats, drive and K are unchanged.

- Fast Bench(60,160), near-touch: **26.62** (plain 26.62); reach 0.794, follow 1.0, in-band 0.745 / 0.438,
  contact 0.005, minimum metal 1.05 mm; overhead 1 of 12 workspace poses taken.
- **Frozen exact Bench(110,360): 34.18** (score 87.6); near-touch 36.89, minimum metal 0.11 mm; reach 0.728,
  in-band 0.746, contact 0.016; overhead 7 of 28.
- Lost poses: fold **84**, slide 8, contact 6. The fold count of 84 is EXACTLY the winner's, so K2 gains nothing on the
  verify bench.
- Coarse best A, worn frozen: 38.46 (fold 79, slide 10, contact 9).
- K2 at the s3 optimum bends only 4.7 deg. Its "3 folded poses taken" have th 32-33. The winner's plain window
  (th_lo 31.28) takes them already; raising smlo only handed them over to K2. **The search's optimum is to make K2 do
  nothing.**

## Why it fails (measured limiters)

1. **Engagement against the metal (the bend of K2 at rest, 500 coarse configs).** The law can extend the fold limit only
   if a2e falls faster than th from the first degree past q2lo. Otherwise the kit margin m3e = th - |a1 - a2e| hits
   5 deg at once: the winner's smlo is 5.28, which leaves 0.28 deg of slack. a2e falls at kK2 sin bK2a sin bK2b sin
   psi / sin a2e, so K2 must rest well bent.

   | K2 rest bend psi0 (deg) | law engages | median K2 hub ib14 | median fK2 (mm) |
   |---|---|---|---|
   | 150-165 | 0 % | 0.55 | 68 |
   | 135-150 | 3 % | 0.27 | 69 |
   | 120-135 | 23 % | 0.12 | 72 |
   | 90-120 | 14-22 % | 0.01-0.08 | 74-84 |

   A bent K2 sits off the J2-J3 great circle, over skin that rises under some pose. Its O20 hub then stands 70-116 mm
   from GH, and the link-2 dog-leg leaves the band. Its own metal costs **6.7 points** at the cheapest seat (control
   23.25, law off, against 16.53) and 10-36 at the engaging seats.
2. **Where K2 does extend the fold limit, link 2 lands on link 1's drive.** The best config with a 10-deg extension (s1:
   th_min 20.8 against th_lo 31.3, K2 bending 36 deg, a2e 61.6 -> 51.4) measures 27.44 at the winner's reach of
   0.794. Its truly folded poses:

   | pose | th | dK2 | result |
   |---|---|---|---|
   | #126 | 21.4 | 34.7 | PARTS: ROD-hubK2 -5.2 mm, hub K-hub K2 -0.7, L1b-hub K2 -0.4 |
   | #127 | 27.0 | 19.1 | PARTS: ROD-hubK2 -2.0 |
   | #116 | 29.4 | 12.0 | pin-knee slide |
   | #102, #114 | 20.6, 20.8 | - | past the law's end |

   At the folded end, link 2 lies back over link 1. K2, at 21 deg from J2, therefore lands on the K drive's pushrod and
   on hub K. **The two drives need the same space at exactly the poses K2 exists for.**
3. **The arithmetic was against it from the start.** The folded side holds 8 fit and 23 verify poses: about 5 fit-reach
   points and 6.4 verify-reach points at best. K2 costs >= 6.7 in-band points just by being there, before its drive.
   Complexity is 68.5 (tools/simplicity.py, full record) against the winner's 42.5 by hand. Rotations only, and 0
   passive translations.

## Red team

- **The optimistic number.** The CMA best's 3 "folded" poses are a relabelling of poses the winner already takes. The
  honest gain is 0, confirmed by the frozen fold count of 84 = 84.
- **The pinch.** On the verify bench, the frozen minimum metal is 0.11 mm (near-touch 36.89). On the fit bench, hub 1
  is 1.24 mm above the skin on Raise overhead, and hub K2 is 1.36 mm on #210 (plane 135, elev 135).
- **The jam.** ROD-hubK2 at -5.2 mm on #126 (plane 30, elev 105) whenever K2 does real work.
- **Simplification still in the model.** K2's rod and horn are sampled on link 2a, and their few-mm motion with K2 is
  ignored. That motion happens only on folded workspace poses, and no clip frame engages K2, so in-band is unaffected;
  the collision verdict in limiter 2 would only get worse.

## Verdict

**DEAD (converged, 4034 configurations).**

- Best 26.62 fast near-touch; 34.18 frozen exact on Bench(110,360), against the winner's 16.53 / 23.37-23.57 through
  the same code.
- A slaved knuckle on link 2 cannot fold a2 at the folded end. It must rest bent >= 45 deg off straight to out-run th
  at the 5-deg kit margin, and there its O20 hub and the link-2 dog-leg leave the band.
- Where it does extend the fold limit (by up to 10.5 deg), link 2 lies over link 1 and K2 collides with the K drive's
  pushrod and with hub K.
- The folded side's whole prize (+0.064 verify reach) is smaller than K2's metal cost alone.

**New knowledge** (applies beyond this morphology):

- (a) Any folded-end relief that shortens a2 by a knuckle near J2 must bend it faster than th falls. The engaging
  window is a rest bend psi0 of 90-135 deg, and there a hub on link 2 is <= 0.12 in band.
- (b) At the folded end, link 2 occupies link 1's space, so a folded-side mechanism near J2 conflicts with any
  stretched-side drive on link 1b.
- (c) For the folded side, the lead's other open lever, a drive with NO out-of-band metal on the existing chain, is
  the better bet than more hubs.

## Audit (round 7, independent auditor)

**The death stands.** The same code, run again:

- **Winner.** The verified winner through the same model module (its own row's best_params) scores 16.53 fast near-touch: reach 0.794, ib14 0.846, fold losses 27.
- **Claimed best.** The row's best_params reproduce exactly at 26.62: reach 0.794, ib14 0.745. K2 engages on 3 folded workspace poses, but fold losses stay at 27, the same as the winner. K2 moves 3 poses from the plain window onto its own law and adds no new ones. The whole loss is in-band: hub K2 is 0.41 in band and L2a is 0.17.
- **Sweep bookkeeping.** The sweep's best entry is 22.34, not 26.62 (k 2186, cma-s3; reproduced). It is a K2-idle config: the law takes 0 folded poses, with hub K2 0.52 in band. The model flags these `k2_idle` and CMA adds 100, so they are not claims. Treated as the price of K2's metal alone at its cheapest seat, they cost 5.81 points (22.34 - 16.53).
- **Bound on the prize.** The folded fit poses (th < th_lo) number 8 of the 160 workspace poses. Even if K2 took all 8 with no new collisions, reach would rise by at most 0.05, which is at most 5.0 gap points. That is less than the 5.8 that K2's cheapest metal costs, so the two-sided split cannot beat the winner on Bench(60,160) at any seat. The engaged seats are worse: hub K2 sits at psi0 <= 135 deg, 70-116 mm from GH.
- **Convergence gate.**
  - Stream cma-s3 holds the engaged best. It gained 0.00 over the 2nd half and 0.00 over the last third, and its top 5 lie within 0.03 (engaged) or 4.3 (all). It is converged.
  - cma-s1 is not converged: it gained 4.58 over the 2nd half and 4.14 over the last third. Its gains all came in K2-idle configs (best 22.69, idle). The bound above covers those, so more CMA cannot refute the death.
- **Model checks.** The model loads the winner's own module and only adds K2's members and law, and the K2-off path reproduces the winner's 16.53 bit for bit. The folded law's gates (monotone, rate <= 3.45, the kit's m3e >= 5, dyad margin, lift-off, stop, pressure angle) are the same ones the winner's stretched law uses, so none of them is stricter here. I found no convention bug.
- **Reference threshold.** The auditor template's "within 10 of 68.93" reference is obsolete: the design's 26.62 already beats the old champion. The relevant reference is the round winner, 16.53 fast / 23.57 verified, and against that the death stands.
- **Frozen exact, measured again.** The row's best_params worn frozen on Bench(110,360) exact (CB_EXACT=1, 136 s) score 34.18: reach 0.728, ib14 0.746, contact 0.016, near-touch 36.89, min metal 0.11 mm. Overhead takes 7 of 28. Fold losses are 84, the same as the winner. The K2 drive's own metal is out of band: rocker2 0.08, rod2 0.00, rod ends2 0.00, L2a 0.18. This matches the claim exactly.

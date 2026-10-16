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


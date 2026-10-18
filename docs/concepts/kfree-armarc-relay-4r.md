# kfree-armarc-relay-4r - plain O20 3R at the lead's seats + one-sided arm-arc relay (counted 4th R), no knuckle, no drive

Round 104 (J4, track jump), lens A "guide-price-close", the survivor's simplicity column. Model:
`docs/concepts/models/kfree-armarc-relay-4r.py`. Sweep: `docs/concepts/sweeps/kfree-armarc-relay-4r.json`. Row:
`docs/concepts/rows/kfree-armarc-relay-4r.json`. Preview: `docs/concepts/viz/concepts/kfree-armarc-relay-4r.js`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Price the relay against its own
   control before anything else: the same frozen lead metal with K welded and no relay (PHI 0). Every point the relay buys
   is measured against that number, not against the lead. Then split the relay's cost into its two physical parts, each
   measured: (a) the ideal relay (rotation only, no track / shell / carriage metal, no lift) as a lower bound on the gap
   for this morphology at any hardware, and (b) the hardware (the track radius about the axis, the arm-side stack's
   lift onto the carriage, the arc length). If (a) is not under the kill line, no hardware choice can save it. A designer
   would also check where the arc lies (deltoid crest, axilla side, torso) before sweeping the axis, because the track
   radius is set by the highest skin over the arc.
2. **Rawest material.** The posed skin itself (the bench's signed-distance field per pose through `CB.Bench.dist`),
   the motion clips (Bench(60,160) fit clips, Bench(110,360) exact), the lead's fitted metal in its own model
   (conecut-knee-knuckle-3r: O20 stacks, pin knee, J3 dowel stop), the proposer's lost-pose list
   (docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json) and the per-pose dumps written here.
   The relay track radius comes from ray marches through the posed arm skin per fit-clip frame (p90 over frames), not from
   a digested ring radius.
3. **Methods and tools.** tools/concept_bench.py (the outside judge), the lead's own model loaded unchanged with K welded
   (law onset moved to the plain wall, smhi 5, plus a gate |dK| <= 0.1 deg), the relay wrapper of armarc-relay-knuckle-4r
   (least-phi relay solve on every lost pose of either wall, track + shell + carriage sampled metal, the arm-side lift onto
   the carriage, jams), the kit model (tools/concept_kit.py) only to reproduce the proposer's nok_metal counts, and the
   frozen-shape protocol (fit Bench(60,160) fast, worn Bench(110,360) exact).
4. **What, other than me, shows the number is right.** The bench (Bench(110,360) exact, frozen), the adversarial verifier
   with the 18.28 bar, the alignment auditor's ledger, and the red-team pose list below (the relayed poses that end in
   contact or jams, the largest relayed phi, the folded-side relays the spring cannot refuse).

## The morphology

At rest three O20 hubs sit at the verified lead's seats (J1 back of the shoulder / acromion top bvec(95.39, 67.90), J2
over the posterior deltoid, J3 on the lateral arm; a1 37.55, a2 57.22). Link 1 is one bent bar (hub K, bell crank, nose,
horn deleted). The cuff knee is the lead's. BOTTOM's pad rides a carriage on a circular track about an arm-fixed axis
through GH (tilt / azimuth swept), held on a zero dowel by a constant-force spring, end dowel at PHI. When the arm leaves
the plain dyad's window (th > a1 + a2 - 5 = 89.77 stretched, th < |a1 - a2| + 5 folded) the arm turns the carriage to the
least phi in [0, PHI] at which every gate of the welded chain passes. A spring relay cannot choose its wall: a pose whose
least-phi state ends in metal on metal is a jam, counted lost.

DOF: 4 counted joints (J1, J2, J3, relay), 0 passive translations, knee pins a / b passive (outside the count).

## Modelling notes (what changed from the spec, and why)

* **The kit model reproduces the proposer exactly but cannot score this design.** `repro` (kit CONTROL metal, profiles
  fitted without the relay, worn exact on Bench(110,360)) gives +30: 54 relayed / 10 collide / 1 contact / 44 clean;
  +45: 68 / 15 / 1 / 53; +60: 83 / 15 / 1 / 68 - identical to nok_metal_out.json. But the kit's q 1.0 metal parks hub 2
  at 171 mm from GH even with no relay (kit CONTROL fast gap 74.45, K welded 102.98, against the lead's own model 12.50),
  so its in-band is meaningless. The score is taken from the lead's own model instead (spec: "Base: conecut-knee-knuckle-3r
  with K welded at stop A").
* **K welded properly.** The lead's linear K law opens from th = a1 + a2 - smhi (smhi 16.84, i.e. 12 deg before the
  plain wall). Gating on |dK| = 0 with the lead's law loses every pose in [77.9, 89.8] that a welded dyad closes (first run:
  reach 0.344). The law onset is moved to the plain wall (smhi 5), so K sits on stop A wherever the welded dyad closes, and
  the gate |dK| <= 0.1 deg is the welded window.
* **Drive metal deleted** (crank, nose, horn removed from the rigid and contact lists); hub K and link 1a / 1b at stop A
  stay as metal (the spec's first pass, as the kit did). Shape frozen from the phi = 0 fit.

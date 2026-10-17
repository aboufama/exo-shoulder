# armband-pointer: closed thin-section armband at the distal arm + 2R donut pointer

Round J1 jump track, lens 1 cell R (humerus-axial J3). 3 active DOF, 0 passive, 0 passive translations.
Topology: scapula handler -> J1 (O20 hub, acromion top / back of shoulder) -> link 1 -> J2 (O20 hub, a2 = +-unit(a1 x t))
-> link 2 = a spar fixed in the pointing frame, down the lateral arm -> J3 = a closed thin-section ring bearing coaxial
with the humerus at station s (stator on the spar, rotor bolted into the user's upper-arm cuff).

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask.** Ask the anatomy before the mechanism: a
   closed ring is the one part in this design that must pass BETWEEN the arm and the trunk in every arm-down pose, so
   the first job is a parameter-free bound - for ANY ring (any station s along the arm, any axis through GH within
   12 deg of the humerus, any bore, the thinnest real section) on how many bench poses it can exist at all. That
   bound is independent of hubs, spar and seats, so it decides the morphology before a sweep is spent. Second: centre
   the ring on the arm section, not on the anatomical humerus line (the J3 axis only has to pass through GH; a few
   degrees of tilt move the ring centre ~10 mm at s 220 and keep th almost twist-free - planner: span 95.5 deg at 12
   deg off). Third: the rotor is ARM-fixed, so the bore only has to clear the arm's own section in the arm frame (no
   twist sweep), while the spar is in the pointing frame and sees the full twist - measure them separately.
2. **Rawest material.** The posed render skin of every bench pose (B.skin / signed distance on the fast grid cache and
   the exact libigl path), marched radially from the J3 axis at every 10 deg, every 20 mm from s 140 to 320, out to
   160 mm: the arm's own section (first radius clear of skin) and the first obstacle beyond it (trunk, axilla, forearm,
   head). Not the proximity atlas summaries. Cross-check against the J1 proposer's pre-screen (round101_ideation.md
   section 2 row 4: KA045XP0 in contact on 169-204 / 220 poses at s 205-240).
3. **Methods and tools.** tools/concept_kit.py (frames, wdir, dist_many, closure, members, evaluate with K3 march, K2
   dense continuity, K6), tools/concept_bench.py Bench(60,160) fast for the screen and Bench(110,360) exact frozen for
   the gate; an exhaustive grid over (station, tilt, bore, section) for the bound instead of CMA (the bound is cheap
   and has no local minima); then the faithful kit model at the bound's best ring for the real number.
4. **What else shows the number is right.** The bench itself (gap from B.report), the bound (a lower bound on any
   configuration's gap: reach and follow can only fall when hubs, spar and continuity are added), the independent
   J1 ring scan already in the repo (agreement check), the verifier harness and the alignment auditor; a red-team pose
   list (rest, walking-like arm-down clip frames, across-body, behind-back, overhead, elbow flexed 120+).

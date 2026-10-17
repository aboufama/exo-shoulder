# pinknee-scapular-relay-4r - the verified pin-knee 3R on a spring-centred scapular relay J0

Model: `docs/concepts/models/pinknee-scapular-relay-4r.py` (wraps `skin-normal-3r-pin-knee.py` H1 unchanged; J0 =
`tools/spare_flood.Cfg` clamp policy; continuity = `tools/spare_flood.flood` on the 1432-node envelope grid, transit
nodes restricted to those where the host closes WITH its knee window). Sweep: `docs/concepts/sweeps/pinknee-scapular-relay-4r.json`.
Row: `docs/concepts/rows/pinknee-scapular-relay-4r.json`.

## Deeper-version answers (written first)

1. **What a top mechanism designer would do that the spec does not ask for.** Check the relay's own body against the
   host chain before anything else: J0 is a fourth O20 hub (20 mm disc, 12.25 mm stack) that must sit on the scapula
   where hub 2, link 1 and link 2 never pass. The host's J2 seat is bvec(30, 47) at rest and hub 2 sweeps a circle of
   radius a1 = 41 deg about J1; a J0 placed a0 = 25-35 deg from J1 lies INSIDE or ON that sweep for most phi. So the
   first instrument is a placement scan (a0, phi) of the hub-0 / hub-2 / link-1 angular clearance over the poses the
   chain takes, then the bench. Second: give link 0 an honest level at hub 1 (it must clear link 1, the adjacent body
   at J1, with the 0.15 mm running gap - the host's link 1 leaves hub 1 at the hub's underside, so link 0 rides over
   it), and check the knee window on every relayed pose (the proposer's flood never did).
2. **Rawest material.** The posed skin (concept_bench signed-distance fields of every bench pose, exact path on
   Bench(110,360)), the 10 fps fit clips (relay state path-tracked frame by frame), the 1432-node workspace envelope
   grid (concept_bench 'Workspace (envelope)', the continuity instrument), the host's own lost-pose list.
3. **Methods / tools.** The host model and its verified checks (S.VModel: closure, jam rule, part clearances, knee
   window, slide tolerance), tools/spare_flood.py (clamp policy, sub-chain margin, full-grid flood), the frozen-shape
   protocol (fit Bench(60,160) fast, wear frozen on Bench(110,360) exact), local sweeps (farm closed).
4. **What shows the number is right, other than me.** The bench (an outside judge), the independent verifier with the
   paired per-pose dump (tools/alignment_paired.py), the auditor's ledger, and the red-team pose list below (relayed
   poses: hub 0/1/2 levels, knee angle, th margin, sub-chain margin).

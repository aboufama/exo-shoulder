# insertion-cband-relay-4r: short-strap C-band relay at the deltoid insertion (round 401 K1, judge pick 2)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the band as a bearing race, not as a cuff. The race must be a surface of revolution about the relay axis (a
     cone or a curved profile is fine, since any surface of revolution still rotates), while the underside follows the
     arm in 2D. So the band's radial thickness varies with azimuth, and the carriage only ever sees the race. That
     splits two jobs: the skin fit (underside, per azimuth and per axial station) and the guide (race top, one profile
     R(w)). The spec's single-station band merges them.
   - Price the axis tilt as a metal variable. The 8.75-deg tilt is chosen to put the band centre 15 mm posterior. The
     near-long axis gives +7 static ws poses (319 vs 312, measured here with the judge's kinematics), so the tilt has
     to buy its 7 poses back in band and race clearance.
   - Read the wheels as skin-facing metal. The V-wheel blocks stand outboard of the 22 mm band at the band edges. At
     the insertion the proximal edge sits on the rising deltoid, and the wheel blocks are the lowest metal there.
2. **The rawest material.**
   - The posed skin itself, through B.dist / K.requirement: the exact signed distance of every metal sample in every
     pose. The band's underside is fitted by marching rays from the relay axis at every (azimuth, axial) sample over
     the fit poses, not taken from band.py's one-station digest.
   - The relayed humerus frames: AR.solve_phi least-phi on the whole archive, envsel included.
   - The lead's own fitted metal: the conecut CC model's rigid / link samples, frozen.
   - Not used: the Bench(60,160) proxies of the ideation (no link metal, no in-band term).
3. **The specific methods and tools.**
   - kfree-armarc-relay-4r.py lead_eval, modified only in its bench, with these settings: K welded (|dK| <= 0.1 deg
     gate), drive metal stripped, and knee-side samples dropped (round-401 lens A's readings).
   - The frozen protocol: fit on Bench(60,160) fast, wear on envsel exact (selection), then Bench(110,360) exact (claim).
   - K.requirement for the 2D-contoured band underside.
   - AR.flood_relay for the continuity flood on the 1432-pose envelope grid.
   - The th fold margin in the one metric (angle(J1, J3) against the welded window).
4. **What, other than me, shows the number is right.**
   - The bench (tools/concept_bench.py, exact path).
   - The judge's pre-registered gates: ideal > 14.0 kills; hardware > 17.0 kills.
   - The round's adversarial verifier and the alignment auditor.
   - The red-team pose list below: the deltoid-insertion bulge under the band's proximal edge at abduction 60-120, the
     band's anterior end against the chest at plane 120-150, hub 3 in the deltoid bunching, and the wheel blocks' side
     clearance to the strap.

(Results, limiter and red team follow below once measured.)

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

## Result: DEAD at gate 0 (Bench(60,160) fast, 31 configurations)

| config | gap | reach | in-band 14 | contact | why lost (parts pairs) |
|---|---|---|---|---|---|
| host H1 alone (same model, same bench) | 23.64 | 0.700 | 0.898 | 0.034 | fold 36, slide 5, skin 6, parts 4 |
| proposer BACK cell a0 35 / phi 90, T 0 (hub 0 present, relay locked) | 175.29 | 0.319 | 0.656 | 0.094 | hub0-hub2 56, L2-hub0 33, L0-L1 18 |
| proposer CAP cell a0 25 / phi 60, T 40 | 114.41 | 0.463 | 0.845 | 0.068 | L1-hub0 70 |
| a0 65 (outside hub 2's orbit), phi 60-150 | 108-204 | 0.30-0.48 | 0.51-0.82 | 0.08-0.18 | L0-hub2 21-61, L0-L1 31-53 |
| best seat-rule placement azu 280 / a0 25 | 33.33 | 0.719 | 0.782 | - | hub 0 high, 0-2 relayed |
| best overall azu 250 / a0 40 (J0 axis breaks the seat rule) | 31.06 | 0.675 | 0.906 | - | - |

(azu = J0's azimuth about J1, `e = unit(u1 x y)`, `f = u1 x e`; phi = tools/spare_flood.tilt_pivot's angle.) Kill line 17.5: no placement gets
within 13 gap points of it. Every measured placement scores worse than the host without the relay (23.64), so the relay
costs more than it adds everywhere.

**Why (measured, the limiter).** Hub 2 orbits J1 at a1 = 41 deg. Over the 898 closing poses (the 1432-node envelope
grid plus the fit clips, host at q0 = 0) its azimuth about J1 fills every back and acromion-top direction. In 10-deg
bins, 0-110 and 280-360 are all populated; the free sector, 120-270, lies in front of the acromion. A J0 hub needs
a0 >= ~21 deg to clear hub 1. Inside the orbit that requires a0 <= a1 - 21 = 20 deg, which is impossible. Outside the
orbit (a0 >= 62), link 0 has to cross the orbit, and hub 2 and link 1 jam on it on 20-60 % of poses. Placements in
the orbit's free sector fail the J0/J1 seat rule, which says back or acromion top only, not the front. Near the cap
pole they are allowed, but the seat rule then cuts the J1 travel to T_eff 15-16 deg, and only 0-2 relayed poses are
taken. Even the forbidden front placements (controls) score 56-64, because the hub 0 they need sits at 75-78 mm on
the anterior shoulder.

**Lead's question.** Do hubs 1 and 2 stay at the host's levels on relay poses? The question is moot. The relay takes
0-7 workspace poses at any placement where it is not jammed. The host levels stay at f 49.9-51.9, 60.6-61.6 and
75.7-77.2 mm. Hub 0 sits at 50 mm at the cap pole, 75-78 mm at the front, and 74-98 mm at the back for a0 >= 62.
On the relayed poses that were taken, the knee window held (126.7-144.4 inside [30.5, 149.5]). The minimum th margin
over taken poses is 5.02.

**New knowledge (predicts beyond this morphology).** A scapular spare that carries J1 of a dyad must keep its own hub
and link outside the orbit of the dyad's middle hub about J1 (radius a1). With a1 >= ~40 deg and J1 on the acromion
top, that orbit covers every allowed back/acromion seat for the spare. A relay on a pin-knee-class host would need a
short a1 (<= ~20 deg + hub clearance) or the spare stacked coaxially under J1. The kinematic flood numbers that
motivated the idea (connected reach 0.83-0.90) leave out the spare's own metal, which is what kills it.

**Convergence gate** (score points): gain over the 2nd half 2.70, over the last third 0.49, top-5 spread 1.05. That is
not converged on the first criterion. The kill rests on gate 0 and on the placement impossibility above.

**Red team of the best config** (azu 250 / a0 40): the J0 axis is at az -126 / el 72.5, which breaks the az window of
the seat rule. The seat rule cuts T_eff to 10 deg, and the relay takes 1 pose (q0 -4.5): the config is the host plus
hub 0's metal (hub0-hub2 4 jams, hub 0 at 54.9 mm), and its 31.06 is the host's 23.64 minus that metal. It is
optimistic for a build, because hub 0's handler mount is not modelled. The
frozen exact wear was launched for azu 265 / a0 25 (32.83 fast) and is reported in the row if it finished.

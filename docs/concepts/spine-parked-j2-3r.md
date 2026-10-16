# spine-parked-j2-3r - zero-passive spherical 3R at the leader's seats, slim O15 J2 / J3 hubs

Lens "round3: zero-passive spherical chain", family "spherical 3R". Model: `docs/concepts/models/spine-parked-j2-3r.py`.
Sweep log: `docs/concepts/sweeps/spine-parked-j2-3r.json`. Row: `docs/concepts/rows/spine-parked-j2-3r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Settle the model split before tuning anything: the same chain cannot be worth both 33.40 and 45.01.
     The split is a measurement problem, not a design problem.
   - Treat the J2 fold as the enemy. A pure spherical 3R closes only while angle(J1, J3) stays inside
     [|a1 - a2| + margin, a1 + a2 - margin], and a short link 1 narrows that window. So sweep a1 / a2 jointly with the
     seats, and report what the fold costs: the reach lost to "no closure" alone.
   - Use the hub size as a design variable that maps to real parts: O20 (v5), O17 (2.75 mm wall), O15 (2.0 mm wall),
     all the same MR117-2RS pair. Give credit only where a part exists.
   - Hold the strap end at its hub's level as far as the collision check exempts it. A shorter ramp would be an
     unchecked zone, not a gain.
2. **The rawest material.**
   - The posed skin itself: `concept_bench` distance grids, with CB_EXACT for the exact mesh.
   - The fit clips at their full 10 fps (`CB._poses_all`) for continuity.
   - The proximity atlas data (`docs/research/proximity_atlas.md`: rigid metal must clear the highest skin it ever
     passes over).
   - `pipeline/conformal/analysis/skin_motion_map_14.json` for where skin moves under a rigid part.
   - Digested summaries are used only as pointers.
3. **Methods and tools.**
   - The kit (`tools/concept_kit.py`: K1 closure, K3 march, K4 flat hubs, K5 straps, K6 collisions, dense K2).
   - The crown / wall skin check, near-touch rule and overhead split (fold-sph3r's, here per hub radius).
   - The farm sweep (`tools/cloud_run.py sweep`), then CMA-ES (`tools/concept_cma.py`) as farm batch jobs until the
     convergence gate passes.
   - The frozen-shape run on Bench(110,360) exact (lesson c).
   - Diagnostics on each check separately (per-pair K6, fold vs K2 vs contact) to explain every lost pose.
4. **What other than me shows the number is right.**
   - The bench (`concept_bench`, an outside judge).
   - The kit audit (honest flag).
   - The verifier's frozen Bench(110,360) exact run.
   - The judge's VModel reference at the same seats (41.73 exact).
   - A red-team pose list: rest, overhead >= 140, across the body, behind the back, the q-dropped poses with the arm
     on hub 2, and the closest metal over taken poses.

(Results below.)

## What it is

* Three active pins whose axes meet at GH. Each pin runs on a preloaded MR117-2RS pair (7 x 11 x 3).
* J1 sits in the v5 O20 hub on the acromion top (bvec ~ (95, 66) in the scapula frame).
* J2 is parked behind and above it, over the posterior acromion / scapular spine. A short link 1 (a1 ~ 40 deg) and
  branch sigma -1 keep J2's circle on the posterior-superior cap.
* J3 sits on the lateral deltoid at the leader's d3 direction. The leader's b3 = 0.23 skin-normal "tilt" is a
  spherical freedom: it is the same chain with another a2 / wd / wa.
* J2 and J3 may be slim hubs (O17 / O15, the same bearing pair; see the hand calc below).
* Links are 12 x 3 Ti straps on great circles. Link 2 passes over link 1 and the neck (K6 by construction).
* Member 3 is hub 3's arm-end plate plus the K7 14 x 6 neck, rigid to BOTTOM's bar. The neck starts at hub 3 at
  hub 3's level, so member 3 is physically connected (no air gap).
* **Passive translations 0. Passive rotations 0. Cuff slides 0. Liner compliance claimed 0 mm.** On the bench the
  arm rotates about a fixed GH, so the spherical chain closes exactly (residual 0.0 deg). R10 (GH translation) is off
  this bench. Its options (cuff liner, one RSR3M along the humerus, the base follower slide) are judged separately.
* No gears, pulleys or cables. 3 active DOF, no undetermined coordinate (R17).

### Slim hub, hand calc (O15 = MR117-2RS pair in a 2.0 mm Ti-6Al-4V wall)

* **Bore.** 11 H7 for the bearing OD 11. Wall 2.0 mm gives OD 15.0. The stack is unchanged (12.25 mm F -> crown), so
  the bearing spacing and the moment stiffness are the O20 hub's.
* **Retention without a thread on the OD.** An external M14x0.5 cap thread would leave 1.19 mm under the thread root
  ((13.39 - 11) / 2), and its ring nut grows the crown to O16+, which breaks the O15 envelope. Instead:
  - the lower outer ring sits on a bore shoulder in the lower member;
  - the upper outer ring is held by an internal DIN 472 retaining ring in a groove of ~O11.6, which leaves
    (15 - 11.6) / 2 = 1.7 mm of wall at the groove;
  - the cap is a press-fit O15 disc carrying the O6 x 2.5 magnet;
  - the sensor sits on a 1.6 mm PCB of O13. An AS5600 SOIC-8 is 4.9 x 6.0 mm, so it fits.
* **Strength.**
  - Tube section at the groove (OD 15, ID 11.6): Z = pi (15^4 - 11.6^4) / (32 x 15) = 210 mm^3. A 10 N m bending
    moment (MVP2, generous) gives 48 MPa, against a Ti-6Al-4V yield of ~830 MPa: SF ~17.
  - MVP1 is unpowered. The loads are the chain's own weight and inertia (< 0.5 N m), so SF > 300.
* **Mass.** About 6 g less per hub than O20 (solid estimate: pi (10^2 - 7.5^2) x 12.25 mm x 4.43 g/cm^3).
* **Verdict.** Buildable for MVP1 and plausibly MVP2. The component is the same catalogue bearing pair, and the
  housing is a simple machined part.
  - The model accepts a slim hub only as a DECLARED component (`SLIM` in the model). Its sampled disc must cover
    >= 75 % of its own disc and reach >= rad - 0.5. Crowns, walls and K6 use the declared radius.
  - To do (shared files, not edited by this track): add a `MR117-pair-O15-slim` entry to
    tools/hardware_catalogue.json and a declared-radius path to the kit audit.

## The split: kit vs VModel at the same axes, settled

Before this track the judge had one zero-passive chain at the k4216 seats with two numbers:
* 33.40 fast / 41.73 exact in osn's VModel spherical reference (`slides 0`);
* "45.01" in a kit run.

This model rebuilds the chain on the kit at exactly those axes. The conversion goes through osn's own Design
(`scratchpad conv.py`): u1 = bvec(95.86, 65.21), a1 = 40.34, a2 = 74.07, u3 = wdir(84.80, -11.37), branch -1. Each
difference was then switched on and off separately (Bench(60,160) fast, kit checks, O20 hubs unless stated, q 0.98):

| step | gap | reach | follow | in-band 14 | what changed |
|---|---|---|---|---|---|
| kit, 12 mm strap ramps at the hubs | **54.35** | 0.588 | 0.850 | 0.802 | |
| strap ends held at hub level 2 mm longer (`end_extra 2`) | **38.73** | 0.688 | 0.917 | 0.788 | 20 link1-link2 K6 rejections vanish (kit artifact, below) |
| same + fold margin 7.5 instead of 10 | 35.35 | 0.700 | 1.000 | 0.775 | the 3 Raise-overhead frames after the margin violation come back |
| same at 10 deg but 8 mm straps (the VModel width) | 36.18 | 0.694 | 0.917 | 0.801 | straps 12 -> 8 mm: +1.3 in-band points |
| VModel spherical reference (judge) | 33.40 | 0.706 | 0.967 | 0.771 | |

What differs, and which side is right:

1. **K6 artifact in the kit (worth 15.6 points, conservative).**
   - Mechanism: `K._over` decides whether link 2 passes over link 1 at link 2's PRE-raise radius, but `K.collisions`
     judges the shared-joint exemption (HUB_R + 2 = 12 mm of arc around J2) at the FINAL radius. A link-2 sample
     12.8 mm from J2 at r 63.2 lies inside the 12 mm zone at its lower pre-raise radius. So `_over` skips it, and K6
     then rejects the pose (link 1 / link 2 radial overlap at 12.2-12.8 mm from J2).
   - It costs the chain 20 of 170 poses.
   - The physical fix is real and cheap: hold each strap end at its hub's stack level for 14 mm instead of 12
     (`end_extra`). The upper link then stays on the hub's upper plate until it has cleared the lower link.
   - The kit bug is reported as a separate task, with a test to add.
2. **The fold margin along the motion (worth 3.4 points; the kit is right).**
   - Raw 10 fps Raise-overhead clip at k4216: the chain closes in every frame, minimum margin 7.9 deg, 12 frames inside
     the 10 deg jam margin.
   - The kit's dense K2 asks for the margin at every interpolated step between bench frames. It therefore drops the 3
     bench frames that follow the violation.
   - The VModel asks for the margin only at the bench frames. Its 10 fps check only looks for > 25 deg jumps and resets
     after a non-closing frame.
   - The rule is the same 10 deg jam margin, so applying it along the whole path (kit) is the consistent reading. The
     VModel's 0.967 follow is optimistic by 3 frames.
   - The real clip clears 7.9 deg, so a 7.5 deg margin would pass. That is a rule change, not a design change, and it
     is not taken.
3. **Strap width and fitting conventions (~2 points).**
   - The VModel uses 8 x 3 mm straps. This model uses the project's 12 x 3 Ti links (docs/HARDWARE.md, catalogue
     components); 8 mm straps add 1.3 in-band points.
   - The VModel drops contact poses greedily. The kit uses quantile q.
4. **The "45.01" number.** It did not reproduce. It was a kit run with 12 mm ramps at slightly different axes, so it
   carries part of the K6 artifact.

**Settled**: at the same axes and the same honest rules, the zero-passive chain scores 38.73 fast (kit, 12 mm straps,
O20). It would score 33.4-35.4 with the VModel's lax margin rule and 8 mm straps. The judge's 41.73 exact (VModel)
should be read as ~3-5 points optimistic on follow, and the kit numbers here are the honest ones.

# Stop-relay rocker 3R (stop-relay-rocker-3r)

J1 rides a spring-centred passive acromial rocker (pivot axis c through GH, rocker arc beta). J2 has hard stops a
margin short of its fold. Mode A: the rocker sits on its centre and the chain is the spine-parked leader. Mode B / C: J2
sits on a stop and the rocker turns by the least angle that keeps the arm reachable.

## Deeper-version prompt (answered before modelling, 2026-10-16 ~05:00 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the relay as a force-closed system, not a kinematic one. Check four things:
     - The mode-A sag torque (chain gravity about c, plus J1 friction) is below the spring preload in every pose.
     - The stop is reached before the rocker sub-chain's own fold (the margin on the c-u1-p3 triangle).
     - The rocker root is continuous through the switch, with no jump at th = lo / hi.
     - The felt torque overhead stays within the comfort limit.
   - Put the two stop margins (lo / hi) as separate parameters: across-body (hi) recovers almost nothing, so its
     margin may stay large while the overhead (lo) margin is tuned.
   - Let link 1 ride over the rocker by construction (1 mm), so K6 cannot silently pass a rocker / link-1 crossing.
   - Wear the frozen shape on the big bench. The gains are workspace poses, which the Bench(60,160) fit sees only 160 of.
2. **Rawest material.**
   - The posed skin itself: the bench's signed-distance grid, and the exact libigl path for the claim.
   - The bench's raw workspace frames (scapula and humerus rotations per pose) for the mode map.
   - The fit clips for continuity. The held-out clips are never loaded.
   - Not the ideation proxy (axis-ray in-band 0.922). It ignores hub stacks, strap width, K6, `over` and the neck, so
     it is re-measured here with the kit's members.
3. **Methods and tools.**
   - tools/concept_kit.py: K1 closure for both the J2 closure and the rocker sub-closure, K2 dense continuity on every
     axis (R0, J1, J2, J3) and on q0..q3, K3 march, K4 hubs, K5 straps with `over`, K6 at 1 mm radial (verifier
     setting), K7 neck.
   - The spine-parked model's crown / wall / near-touch / overhead extras, generalised to the pivot hub.
   - The farm (tools/cloud_run.py sweep): a coarse sweep, then tools/concept_cma.py from the top. The convergence gate
     comes from the sweep history.
   - The verifier harness pattern (docs/concepts/verify/spine-parked-j2-3r.py): the frozen Bench(110,360) exact run
     with the top-face check.
4. **What, other than me, shows the number is right.**
   - The bench (the outside judge).
   - The spine-parked verifier's checks re-run on this model: top faces, all-face near-touch, 1 mm radial K6, and the
     closure residual.
   - A red-team pose list: synthetic overhead-flexion / abduction sequences that cross the switch (continuity through
     the relay), the rocker / link-1 crossing poses, the acromion-top pivot crown, and the q0 extremes.
   - The frozen exact number next to the fast one (lesson c).

## The model (docs/concepts/models/stop-relay-rocker-3r.py, on tools/concept_kit.py)

### Chain and relay

Chain: scapula handler -> R0, a passive pivot on an O15 slim hub (MR117-2RS pair, AS5600 sensed, spring-centred) ->
a 12 x 3 Ti rocker strap with arc beta -> J1 (O20) -> link 1 -> J2 (O15, two hard stops) -> link 2 -> J3 (O15) ->
member 3, the K7 neck rigid on BOTTOM.

Relay, from the force closure:
- th = angle(u1 at the rocker centre, u3).
- **Mode A** (|a1 - a2| + m_lo <= th <= a1 + a2 - m_hi): q0 = 0.
- **Modes B / C**: J2 sits on its stop. q0 is the root with the least |q0| of the rocker sub-chain (c, u1, u3; arcs
  beta and the stop angle). That root needs a sub-chain fold margin >= m_sw = 10 and |q0| <= qmax.

Every taken pose closes to residual 0 (J2 closure and rocker arc < 1e-4 deg). Dense K2 follows q0..q3 and the four
axes.

The checks are those of the spine-parked model, generalised to the pivot hub:
- the declared slim-hub audit, including R0;
- crown / wall skin checks on all 4 hubs;
- near-touch;
- the overhead split.

### Where the spec was wrong or incomplete (corrected here)

- **"Hub 1 rises by one STACK (3.15 mm)."** It does not. The rocker replaces the base as hub 1's lower member, so the
  stack at J1 is unchanged. The new metal is the rocker strap itself (R0 upper member -> J1 lower member) plus the
  pivot hub. Both are modelled at full size.
- **Stop margins.** The spec's sweep range m_stop 8-14 allowed a J2 stop 8 deg from the fold, looser than the
  leader's 10. Two CMA streams used that, and their best (26.27 fast, m_hi 8.0) is therefore NOT a valid claim. The
  model now clamps m_lo, m_hi >= 10.
- **Spacer at a folded joint.** In mode C every taken pose sits at J2's stop, the most folded state. Link 1 and link 2
  then overlap in plan for about 22 mm past J2: 12 mm straps that diverge at q2 ~ 34 deg. Just past K6's 12 mm
  joint-exempt zone they were 0.15 mm apart, which is a K6 hit. The kit's `over` misses these samples: its exemption
  uses the un-raised radius. The fix is a spacer under link 2's J2 end (`lift2`, 0-4 mm). It only raises metal, and
  the hub's crown rises by the same amount (checked).
- **Relay per side** (`relay_lo` / `relay_hi`). The across-body side (B) recovers almost nothing and costs metal
  height.
- **Continuity through the relay** (`connect`, the main red-team finding below). Static closure at a workspace pose
  does not mean the rocker can get there.

## Red team (measured, 2026-10-16)

### 1. The relay's entry is singular, and the static gains are islands (the main finding)

The rocker sub-chain is the triangle (c, u1, u3) with arcs beta and the stop angle. At the switch, u1 = u1r and
angle(u1r, u3) = lo exactly, so q0 = 0 is a root.

That root is regular only if u3 is NOT in the plane of c and u1r. Its sub-chain fold margin is
min(angle(c, u3) - |beta - lo|, beta + lo - angle(c, u3)).

The CMA optimises static closure at the bench poses, and it picks pivot directions where u3 reaches the switch almost
in that plane. There the rocker can swing furthest, so a static pose deep in mode C closes. The entry is then at the
rocker's own fold. q0 grows like sqrt(lo - th) with an infinite rate, and the m_sw >= 10 rule rejects the frames next
to the switch.

Frame trace at the C-stream best, elevation 30 -> 90 at plane 0, axial -15, Bench(110,360) workspace grid, 2-deg
slerp:

| frames | th (deg) | relay margin | state |
|---|---|---|---|
| 0-7 | 52.2 -> 42.1 | n/a | mode A, q0 = 0 |
| 8-13 | 40.7 -> 33.5 | 1.4 -> 8.7 | nothing takes the pose (a jam) |
| 14 | | | q0 = 29.7 deg at once |
| 14-30 | | | mode C, q0 29.7 -> 65.0 |

So the pose at elevation 90 closes statically, but the arm cannot get there from elevation 30 without the rocker
passing its own singularity (m_sw < 10) or jumping 30 deg.

Instrument (`connected()` in the model, `connect=1`, the default since this finding):
- A flood fill over the workspace grid, seeded at the taken mode-A poses.
- An edge joins two grid neighbours (one step in plane, elevation or axial) when every 2-deg frame between them closes
  and q0 never steps more than 10 deg.
- Relay poses that are not reached are dropped.
- Mode-A poses are never dropped. In mode A, 232 / 232 are connected anyway.

| configuration | bench | relay poses (static) | reachable continuously | static gap | gap with islands dropped |
|---|---|---|---|---|---|
| seed (beta 30, phi 330, spacer 1) | Bench(110,360) kinematics | 49 | 23 (elevation chains only) | | |
| C-stream best (overhead relay only) | Bench(110,360) kinematics | 38 | 13 (elevation chains only) | | |
| C-stream best | Bench(60,160) fast | 11 | **0** (flood fill) | 27.32 | **31.92** |
| B-stream best, stops clamped to 10 | Bench(60,160) fast | 15 | **0** | | 34.45 |

Synthetic elevation sequences across the workspace grid (211 on Bench(110,360)), seed configuration:
- 37 cross the switch.
- **14 jam**: both ends are taken but frames between them are not. With the relay off there are 0 jams.
- 1 sequence has a rocker **snap**: q0 jumps 137 deg in one 2-deg step. The least-|q0| root swaps sides, so the rocker
  state depends on the path (hysteresis). The bench's per-pose rule is optimistic there.
- The fit clips never cross the switch: clip_BC = 0 in every run. So the bench's K2 never sees any of this, as the
  lead note warned.

### 2. R17 sag in mode A

Gravity on the moving bodies (rocker 6 g, hub 1 12 g, link 1 7 g, hub 2 9 g, link 2 13 g, at about 62 mm) along the
mode-A self-motion, by finite difference over the Bench(60,160) poses:
- median 0.003 N.m, p95 0.009 N.m, max 0.010 N.m;
- against T0 = 0.2 N.m, a factor of about 19. Mode A cannot sag.

With J1-J3 frictionless, cuff loads put no moment on the rocker in MVP1.

### 3. MVP2 blocker (the spec did not ask)

A J1 motor reacts on the rocker. The share of the J1 torque about c is cos(beta), 0.87 at beta 29. So 1 N.m of J1
assistance puts 0.87 N.m on a 0.2 N.m centring spring, and the rocker turns under its own actuator in mode A. MVP2
needs a rocker lock (a brake, effectively a 4th actuator) or a 4th motor on R0. This sits on top of the spec's own
point that overhead (modes B/C) J2 assistance is lost with J2 on its stop.

### 4. Felt torque and the switch

- The rocker breaks away only once the arm pushes J2 onto its stop with more than T0 = 0.2 N.m about c. The wearer
  feels a detent at every entry: 0.2 N.m, rising to about 0.35 N.m at |q0| 60 (qmax at the C-stream best is 69 deg,
  so about 0.37 N.m).
- With bearing friction about 0.002 N.m, against T0, chatter is not expected. The singular entry (section 1) is the
  real switch problem.

### 5. Kinematic ceiling WITH continuity, over pivot directions (the proof behind the verdict)

Setup:
- C-stream seats, stops 10.7 / 10.3 deg.
- beta 20 / 30 / 40 x phi 0-330 in 30-deg steps x relay_hi 0 / 1: 72 pivot directions.
- Bench(110,360) workspace kinematics: closure only, no skin, which is an upper bound.
- "connected" is the flood fill above.

| | best static | best connected | mode A alone |
|---|---|---|---|
| workspace reach | 0.906 (beta 40, phi 120) | **0.667** (same) | 0.644 |
| overhead (elevation >= 140) reach | 0.929 | **0.393** (every one of the 72) | 0.393 |

Under continuity the relay adds at most 0.023 of big-bench reach (8 of 360 poses) and nothing overhead, for every
pivot direction tried.

Entries into the relay are not always singular. Where elevation chains cross th = lo, the entry sub-chain margin is
>= 10 in 34-69 % of entries, depending on phi. But the overhead relay poses sit on the opposite root branch from the
one entered.

Example: plane 0, axial -15.
- q0 is -49.5 at elevation 90 and +44.2 at elevation 120. The least-|q0| root swaps sides.
- The rocker would have to cross its infeasible arc, which means J2 going past its stop.
- So the elevation-150 pose (q0 +20) is a static island.

The ideation proxy's overhead gain (0.357 -> 0.571) is static closure. A motion cannot use it.

## The same rocker under the pin-knee leader (k4598): kinematic proxy only

Setup:
- The pin knee's J1 / J2 lie on GH rays. J3's DIRECTION (tilted b3 0.325) sets the fold exactly as in the spherical
  chain: arcs 40.12 / 72.31, u1 = (0.113, 0.910, 0.399) in the scapula frame.
- The relay is a function of the axis directions only, so the same `relay()` runs on the pin knee's u1 and its
  arm-frame u3 (RS @ HG @ u3).
- Bench(110,360) workspace, static closure.

| rocker | workspace reach | overhead | clips |
|---|---|---|---|
| none (the verified leader's fold) | 0.631 | 0.393 | 1.000 |
| beta 30, phi 330 (acromion-top pivot) | 0.772 | 0.607 | 1.000 |
| beta 40, phi 300 | 0.858 | 0.857 | 1.000 |
| beta 40, phi 210 (pivot on the anterolateral deltoid) | 0.922 | 0.964 | 1.000 |

Same pattern as the spherical seats: 0.639 -> 0.775 at beta 30 / phi 330, and up to 0.95 at beta 45 / phi 210.

It was NOT built as a full pin-knee VModel. Three reasons, all measured on the spherical version, and none depends on
how the cuff closes:
- Continuity removes the gain (section 5).
- Pivots that give the large static gains sit on the deltoid, where the pivot hub and hub 2 leave the band. At
  beta 45 / phi 210: in-band 0.20, hub 0 fitted at 141 mm, hub 2 at 176 mm, 0.0-0.05 per member.
- J1's MVP2 reaction trips the spring (section 3).

## Results (Bench(60,160), fast grid cache, kit checks; sweep file docs/concepts/sweeps/stop-relay-rocker-3r.json)

Farm spend for this morphology: exo-cpu1 CPU workers (cpu3c / cpu5c, 8 vCPU). About $0.03 for the coarse sweep and
$0.17-0.20 for CMA A-D. The later batches (CMA E-K, frozen runs) were queued behind other agents' jobs at write time.

| run | configs | best gap (fast) | score | note |
|---|---|---|---|---|
| seed, ideation spec (beta 30, phi 330, CMA-B seats) | 1 | 46.83 | 82.97 | K6: link 1 x link 2 at the folded J2 (27 poses), pivot hub x link 1 / hub 2 |
| + end_extra 1.02 + J2 spacer 1 mm | 1 | 35.24 | 87.19 | link 1 x link 2 cleared; the pivot hub still hits link 1 in 9 mode-A poses (5 clip frames) |
| deltoid pivots (beta 40-45, phi 180-210) | 2 | 96.9-134.5 | | static reach 0.72, in-band 0.20: pivot hub F 141 mm, hub 2 F 176 mm |
| farm coarse (random, 2 seat sets) | 256 | 37.14 | 86.49 | |
| CMA A (k7008 seats) | 1385 | 30.77 | | m_hi 9.5 < 10: not compliant (compliant best 41.29) |
| CMA B (CMA-B seats) | 1665 | 26.27 | | m_hi 8.0: J2 stop 8 deg from the fold. NOT compliant; clamped to 10 -> 34.45 |
| **CMA C** (overhead relay only, relay_hi 0) | 1241 | **27.32** | **90.07** | compliant (m_lo 10.73 / m_hi 10.25), static relay |
| CMA D (anterior pivot, phi ~185) | 1697 | 39.73 | | m_hi 8: not compliant; pivot hub in band only 0.26 |
| **C best, continuity enforced** (connect = 1) | 1 | **31.92** | **88.39** | all 7 relay poses are islands; relay taken 0 |
| C best shape, relay off | 1 | 32.63 | | the relay's usable worth: 0.71 points |

The C best (static, the configuration the gate refers to) is:

| parameter | value |
|---|---|
| J1 (az, el) | 98.84, 64.44 |
| arcs a1, a2 | 41.76, 72.34 |
| J3 wdir (wd, wa) | 83.01, -15.19 |
| sigma | -1 |
| q | 0.963 |
| rocker beta, phi | 28.83, 324.51 (pivot on the acromion top) |
| stop margins m_lo, m_hi | 10.73, 10.25 |
| qmax | 69.1 |
| relay | lo side only |
| link 1 over rocker | yes |
| spacers lift1, lift2 | 0.70, 0.32 |
| end_extra | 0.50 |
| hubs | O15 R0, O20 J1, O15 J2, O15 J3 |

Its static report:

| metric | value |
|---|---|
| reach / follow | 0.694 / 1.0 |
| in-band 14 / 10 | 0.888 / 0.514 |
| contact | 0.055 |
| per member in band | rocker 1.0, pivot 1.0, hub 1 0.996, hub 2 0.999, hub 3 0.883, link 1 0.983, link 2 0.752, neck 0.859 |
| mass | 101 g Ti |

With continuity:

| metric | value |
|---|---|
| gap | 31.92 |
| reach / follow | 0.650 / 1.0 |
| in-band 14 / 10 | 0.888 / 0.514 |
| contact | 0.0575 |
| near-touch gap (metal < 1 mm = contact) | 43.80 |
| min metal-skin | 0.06 mm |
| overhead (elevation >= 140) workspace reach | 0 / 12 |
| overhead clip follow | 5 / 5 |

**Convergence gate** (static objective, compliant entries, the whole history of 6255 tries in time order, parallel
streams interleaved by generation):
- gain over the 2nd half: 0.06 score points;
- gain over the last third: 0.01;
- top-5 spread: 0.01;
- -> converged.

The continuity objective (CMA H-K, connect = 1, pivot directions 230-360 deg) was queued on the farm at write time.
Its outputs land in .cache/srr/cma_[E-K].json.

**Frozen Bench(110,360) exact** of the seed-spacer shape and of the B / C bests was queued at write time:
.cache/srr/frozen_{k6,B,C}.json. These are static-relay numbers from the model as shipped before the continuity filter.
Read them as an upper bound.

## Verdict

The stop-relay rocker's gains are static closure islands.
- The CMA's best static shape (27.32 fast, score 90.07) crosses 27.5 only because the bench scores each workspace pose
  on its own.
- With the requirement that the arm can MOVE into a pose (flood fill from the mode-A region, 2-deg frames, no rocker
  snap), every relay pose of that shape is unreachable. The number falls to 31.92, 0.71 points better than the same
  shape with the rocker locked (32.63).
- Across 72 pivot directions, the kinematic ceiling with continuity is +0.023 big-bench reach and +0 overhead.

The leader it is built on (spine-parked-j2-3r, 0 passive joints, complexity 0) is 28.49 fast / 34.29 verified. This
design adds complexity 13.5 (sensed passive pivot + spring) for no usable gain. J1's MVP2 reaction (0.87 tau1 on the
spring) also rules it out for the powered version.

Limiter, measured:
- At the switch the rocker sub-chain (c, u1, u3; arcs beta, lo) sits at or near its own fold for the entries the CMA
  favours (frame trace: margin 1.4-8.7 deg over 6 frames, then a 30-deg q0 jump).
- Where entries are regular (34-69 % of elevation-chain entries, depending on phi), the overhead poses lie on the
  other root branch (q0 -49.5 -> +44.2 between elevation 90 and 120).
- A spring-centred rocker cannot reach them without J2 passing its stop.

**What would be needed instead.** A transmission that sets q0 as a smooth function of the J1-J3 angle, entered with a
non-zero slope (a coupler that drives the rocker from link 1 / J2, as the round-4 state's "measured hope" says), not a
force-closed unilateral stop. The fold lever has to be kinematic and continuous, not a relay.

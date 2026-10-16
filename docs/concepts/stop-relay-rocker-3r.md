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

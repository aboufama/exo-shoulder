# Fold-widening 3-passive closures: which exist, where the passive rotation must sit, what they open (2026-10-16)

Track: golden push, after docs/research/nzc/closures.md ("No 1- or 2-passive closure widens the fold"). Question: which
buildable closures with >= 3 passives widen the J2 fold window AND keep hub 2 on quiet skin? Instruments (new, all in
`docs/research/fold3p/`): `fold3p.py` (closures, bounds, search, continuity; output `fold3p.json`), `fold3p_park.py`
(hub parking gate, exact skin; output `fold3p_park.json`). Bench(110,360) frames (110 clip + 360 workspace poses, raw),
fold margin 5 (K.FOLD_MARGIN), seats of the polished pin knee H1 (J1 / J2 on GH rays, a1 41.02, a2 68.26, branch -1,
window th in [32.2, 104.3]). Kinematic level unless stated; the parking gate is exact skin.

## 1. Derivation: where a passive rotation can and cannot move the fold

Fold law: the chain takes a pose iff th = angle(J1, J3) lies in the window. Passive joints change th only if they change
the DIRECTION of J1 in the scapula or of J3 in the arm. Three results (all bench-checked numerically by fold3p.py):

1. **Any passive set whose rotations are all parallel to active axes leaves the fold law intact, whatever its
   translations.** Slides rotate nothing; pins || J3 add to q3. So "pin knee + a short slide along the arm" does NOT
   widen the window: a widening closure needs a passive rotation whose axis is not parallel to J1-J3.
2. **A passive rotation between two GH-centred bodies is locked to a constant (no widening).** If the active chain is
   spherical about GH (J1, J2 lines through GH, J3 line anywhere) and the extra pin sits on the arm side (a carriage on
   the arm turning by c about v, carrying the knee's pin b), the knee closes the in-plane drift and the out-of-plane
   equation reads (Rv(c) u3) . o_v = const (o_v = a point of the v line, arm frame): it holds for ONE c at every pose.
   The same holds for the Jarrasse-Morel cuff (2 pins normal to the arm + a slide along it) on a GH-concentric chain:
   P3 = U(p1, p2)(c0 + t s) is pose-free, so the U and the slide sit at constants. **Tilting a knee pin out of the
   J3-parallel plane, a passive roll at the cuff, a Jarrasse-Morel cuff: all lock on a GH-centred chain.** The passive
   coordinate varies with the pose only if the loop contains a body whose rotation centre moves relative to GH.
3. **The working closure: a coupled J1 rocker (PROX).** J1's hub sits on a rocker plate that turns by rho about a
   passive pin c through a point o, |o| = R mm off GH (o perp c). The active chain is then centred at
   G'(rho) = (I - Rc(rho)) o, the pin knee (2 pins || J3) closes the in-plane drift, and the out-of-plane equation is
   `w . (I - Rc(rho)) o = h` (w = the arm-fixed J3 direction seen from the scapula, h = the knee-plane height offset,
   a build constant). With A = w.o^, B = w.(c x o^), k = h / R:
   **rho = atan2(B, A) + s acos((A - k) / |A, B|)** - one determined value per pose and branch s; no undetermined
   coordinate (R17). For k -> 0 the branch is rho ~ 2 psi (psi = azimuth of w about c), a smooth ramp; k != 0 keeps
   the two branches apart (no bifurcation). The fold law becomes th = angle(Rc(rho) u1, w): the closure tilts J1
   toward the window as the arm leaves it. Isostatic count: 3 active + 3 passive (rocker, knee pin a, knee pin b) + GH 3
   - 6 = 3 = the arm.
   The mirror closure (DIST: active chain centred at a scapula-fixed point e off GH, arm-side carriage pin v, rho fixed
   by `Rv(c) u3 . g_arm = -k`) also varies with the pose, but its schedule is driven by the arm-frame direction of a
   scapula-fixed offset - it measured WORSE than the plain chain (below).

## 2. Measured: kinematic reach (360 workspace poses, margin 5, connected = continuity flood fill)

Continuity (CLAUDE.md rule): kNN graph over the 360 workspace poses (6 nearest by max(scapula, humerus) rotation,
<= 32 deg; 1256 edges, 13 403 slerp sub-frames at <= 2 deg), seeds = the taken poses at elevation <= 15 (85), an edge
holds only if every sub-frame closes in the window and rho never steps > 10 deg (no branch change: the branch is fixed).
The bench's 360 workspace poses are a sparse sample of the 4488-point grid, so the stop-relay `connected()` grid-step
graph would isolate most poses; the kNN graph is the deviation, stated.

| closure (H1 seats) | passive travel cap | workspace reach static / CONNECTED | overhead (elev >= 140, 28) | clip frames closing | passive range p5-p95 |
|---|---|---|---|---|---|
| plain H1 (no passive rotation) | - | 0.731 / - | 0.464 | 1.000 | - |
| per-pose-free rotation of J1 (scapula side), best axis (bound, undetermined) | 20 / 30 / 40 deg | 0.861 / 0.917 / 0.950 | | | |
| per-pose-free rotation of J3 (arm side), best axis (bound, undetermined) | 20 / 30 / 40 deg | 0.867 / 0.917 / 0.950 | | | |
| **PROX coupled J1 rocker A** (c = bvec(6.6, 11.3): posterior, pivot hub on the back of the shoulder; o^ at chi 28.7; k -0.083, s +1) | 30 | 0.842 / **0.842** | 0.679 | 1.000 | rho -24.6 .. -5.1 (rest -6.9) |
| **PROX coupled J1 rocker B** (c = bvec(5.4, 1.6), chi 27.2, k -0.084, s +1) | 45 | 0.864 / **0.864** | 0.714 | 1.000 | rho -29.8 .. -5.1 (rest -7.2) |
| PROX, pivot line on the other side of GH (chi 209.7, k +0.081, s -1) | 45 | 0.864 / 0.864 | 0.714 | 1.000 | -32.1 .. -5.0 |
| DIST coupled cuff roll, best of 5000 + refine | 30 / 45 | 0.578 / 0.719 | 0.14 / 0.25 | 0.74 / 0.92 | |

* **The scapula side wins; the axis is anteroposterior.** Every PROX optimum (12 of 12 refined starts per cap) puts c
  within ~12 deg of the posterior horizontal (or its antipode, the same line): the rocker tilts J1 in the coronal plane,
  i.e. it re-seats J1 medial / lateral over the acromion as the arm elevates. The determined closure realises 0.84-0.86 of
  the 0.92-0.95 per-pose-free bound - most of it - and overhead goes 0.46 -> 0.68-0.71.
* **Every taken pose is connected** (static = connected): the closure is a smooth function of the arm direction, no
  islands, and all 110 clip frames close (follow kinematic 1.0).
* **The arm-side coupled roll (DIST) loses**: its schedule follows a scapula-fixed offset seen from the arm, which is
  not the direction the fold needs; best 0.72 < the plain 0.73. Dropped.
* J1 seat rule: rho turns J1 about the posterior axis by -5 .. -30 deg; the J1 directions stay in the acromion-top /
  back region (fold3p_park.json `J1_az` / `J1_el`, section 3).

## 3. Hub parking gate (exact skin, Bench(110,360); fold3p_park.py)

Per taken pose, the skin requirement along each hub's ray (K3 march, 2 mm clearance, exact distance), rays from the
moving chain centre G' (hub 1: Rc(rho) u1; hub 2: the two-circle J2 of (Rc(rho) u1, w), H1's branch; pivot hub: the c
line through o, posterior end). R = distance of the pivot line from GH (rho does not depend on R; the chain-centre
shift 2 R sin(rho / 2) does). First pass: one level = quantile 0.97 over the taken poses (j2knee_gate rule), in band =
level - requirement <= 12 mm (`fold3p_park.json`). Second pass, THE GATE: the hub-2 level L that keeps the most workspace
poses with hub 2 in band >= 0.8 among the kept, poses needing more than L dropped as contact (`fold3p_park_gate.json`,
per-pose requirements in `fold3p_park_req.npy`).

| design | R mm | chain-centre shift p95 / max mm | hub 1 level, in band (q0.97) | hub 2 level, in band (q0.97); req p10 / p50 / p90 | pivot hub level, in band | **GATE: hub-2 level L, in band, workspace reach kept** |
|---|---|---|---|---|---|---|
| plain H1 (reference, same metric) | - | 0 | 48, 1.00 | 59, 1.00; 52 / 53 / 56 | - | 64, 0.962, **0.719** |
| PROX A (travel 30) | 12 | 5.1 / 7.5 | 56, 1.00 | 78.3, **0.06**; 52 / 55 / 62 | 71, 0.98 | **65, 0.833, 0.775** |
| PROX A | 25 | 10.7 / 15.6 | 59.6, 0.46 | 84.8, 0.05; 53 / 56 / 66 | 64, 1.00 | - |
| PROX B (travel 45) | 12 | 6.2 / 10.0 | 59, 0.46 | 85.2, 0.05; 52 / 55 / 63 | 78.4, 0.44 | **65, 0.827, 0.769** |
| PROX B | 25 | 12.9 / 20.8 | 64, 0.19 | 93.4, 0.04; 53 / 57 / 68 | 70, 1.00 | - |
| PROX C (other side) | 12 / 25 | 6.6 / 10.5, 13.8 / 21.9 | 51 / 50, 1.00 / 0.97 | 68.4 / 66.8, 0.10; 49 / 52 / 57 | 89 / 97, 0.18 / 0.12 | - |

**Hub 2 is still the cap, exactly as for the relay.** Over the bulk of the poses hub 2's requirement is the plain
chain's (p50 55 vs 53 mm); the poses the rocker RESCUES put the J2 ray over high skin (the q0.97 tail 78-93 mm), so one
hub-2 level cannot serve both. Holding hub 2 in band >= 0.8, the coupled rocker keeps **0.775** of the workspace (A) /
0.769 (B) against the plain H1's 0.719 at 0.96 in band: **+0.05 of reach, 0.005 short of the 0.78 gate**, and it pays
13 points of hub-2 in band. A larger R (less GH sensitivity, section 4) makes it worse: the chain centre moves 11-21 mm
and hub 1 leaves the band (0.19-0.46).
**J1 seat rule:** the rocker carries J1 from el 59 down to el 28 (A; 15 for B) at az 93-100 - over the lateral deltoid,
outside the acromion-top region (el >= 50) for the rescued poses. The handler still holds the pivot on the back of the
shoulder, but J1 itself leaves the allowed region while the arm is raised.

## 4. Sensing, determinacy, complexity, components

* **Determinacy (R17):** on a rigid-GH body the closure fixes rho (formula above) and the knee pins; no free coordinate.
* **Sensitivity to real GH translation (red team):** a GH shift delta along w moves rho by delta / (R sqrt(|A,B|^2 -
  (A - k)^2)) rad: measured over the taken poses **6.5 deg/mm (p50), 16 deg/mm (p95) at R 12; 3.1 / 7.8 at R 25;
  2.0 / 4.9 at R 40**. The real GH moves 2-5 mm over the range (docs/research/gh_translation_literature.md), so rho is
  NOT predictable from q1-q3 in a real shoulder: **rho must be sensed** (an encoder on the rocker pin), and the fold
  margin near the window edge is eaten by GH translation unless R >= ~25-40 mm. That is the trade: larger R = less
  sensitivity but a larger chain-centre shift 2 R sin(rho / 2) (R 25: up to ~13 mm at rho -30, hubs leave the band).
* **Complexity (tools/simplicity.py, the user's weights):** pin knee 19.5 -> **29.0** with all three passive
  coordinates sensed (3 passive rotations, 3 sensed, 6 bodies, 6 joints, 13 made / 14 bought; 24.0 if the knee pins
  could stay unread). Not near 0: this closure is a reach lever on the pin-knee class, not a zero-complexity route.
* **Components:** rocker pin = MR85ZZ pair (5 x 8 x 2.5 mm, 2 bearings, ~6.5 mm stack with a 1 mm Ti washer) on a
  ground Ti pin, or an iglidur GSM-0505 sleeve + 2 GTM washers (5 mm stack) as the pin knee uses; rocker plate 3 mm
  Ti-6Al-4V, ~35 x 14 mm, from the pivot hub (back of the shoulder) to J1's O20 hub; rocker encoder: AS5600-class
  magnet on the pin (it is a sensed passive, 5 points). Knee pins as H1 (iglidur pins, lE 59.6, lc 28.2). J1-J3 O20.
  Passive translations: 0.

## 5. Verdict and next

**No candidate passes the gate.** Best: PROX A (coupled J1 rocker on a posterior pivot, R 12 mm, travel 30):
kinematic reach 0.842 connected (plain 0.731), overhead 0.68 (0.46), follow 1.0 - but with hub 2 parked in band >= 0.8
only **0.775** of the workspace stays (gate 0.78), J1 dips to el 28 (rule: el >= 50 over the acromion top), the rocker
angle moves 6.5 deg per mm of real GH translation at R 12 (so it must be sensed: complexity 19.5 -> 29.0), and a larger R
that would tame that sensitivity lifts hubs 1 / 2 out of band. Every other closure the brief named locks (section 1) or
loses (DIST 0.72). Not catalogued (the brief's gate: reach >= 0.78 at hub-2 in band >= 0.8, continuous).

What the data says to do next, in order: (1) one joint search of the PROX closure with the hub-2 gate IN the objective
(rocker axis, o^, k, branch AND the seats u1 / u3 / arcs, constraint J1 el >= 50) - the shortfall is 0.005 of reach, so a
seat re-tune may cross it, but the hub-2 tail (78-93 mm on the rescued poses) is the same physics that capped the relay
(+0.09-0.14) and the zc frontier; (2) if it crosses, a kit model with the rocker plate as a member (its own level) and the
knee's extra drift; (3) the honest alternative remains the 4th active joint / sensed 4R class (hub 4 parks the far end).
A closure that widens the fold without moving hub 2 over the raised arm would need J2's ray to stay on the quiet cap in
the rescued poses, i.e. a coupling that also moves hub 2 - one more passive (a slide along J2: a ptrans, +2-3 points).

## 6. Red team

* Kinematic + one-level parking only: no links / straps, no knee window with the extra drift of G', no part collisions,
  no contact. The pin knee lost ~0.03 of reach from kinematic to frozen; expect the same or more here.
* The search ran at H1's seats only (rocker axis / o^ / k / branch free); the seats were tuned for the rockerless chain.
* The continuity graph is kNN on a sparse sample, not the full grid; clip frames are checked by closure only.
* The hub level is one quantile over the taken poses with the ray from the moving chain centre; the O20 disc rim and the
  rocker plate's own level are not sampled (j2knee_gate showed the plate, not the pin, can be the cap).

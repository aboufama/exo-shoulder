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

PARK_TABLE

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

VERDICT

## 6. Red team

* Kinematic + one-level parking only: no links / straps, no knee window with the extra drift of G', no part collisions,
  no contact. The pin knee lost ~0.03 of reach from kinematic to frozen; expect the same or more here.
* The search ran at H1's seats only (rocker axis / o^ / k / branch free); the seats were tuned for the rockerless chain.
* The continuity graph is kNN on a sparse sample, not the full grid; clip frames are checked by closure only.
* The hub level is one quantile over the taken poses with the ray from the moving chain centre; the O20 disc rim and the
  rocker plate's own level are not sampled (j2knee_gate showed the plate, not the pin, can be the cap).

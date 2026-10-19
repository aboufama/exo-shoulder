# virtual-pole-4bar-j2: J2 as a spherical four-bar with a virtual pole

Model: `docs/concepts/models/virtual-pole-4bar-j2.py` (at=2; the same file runs the J1 variant,
`docs/concepts/virtual-pole-4bar-j1.md`). Sweeps: `docs/concepts/sweeps/virtual-pole-4bar-j2.json`. Row:
`docs/concepts/rows/virtual-pole-4bar-j2.json`.

## Depth answers (before any number)

**What would a top practitioner of spherical / deployable linkages do here?** They would not put a bearing where the
skin moves. A revolute about a GH ray needs metal on that ray. A spherical four-bar's coupler turns about an
instantaneous pole, the crossing of its two crank great circles (Chiang, *Kinematics of Spherical Mechanisms*). That pole
is virtual and walks along the fixed centrode. So you choose the pole where the kinematics wants the joint axis and put
the four pins on rays where the skin is quiet. Then you check three things:
* mobility, by Grubler and also by a Jacobian rank (overconstrained loops fool Grubler);
* the transmission angle (dead points, toggles);
* thickness accommodation where links cross. This is the problem thick-panel origami solves. A degree-4 origami vertex
  IS a spherical 4R with its vertex at GH.

The planar remote-centre answer (Taylor's double parallelogram) does not carry over to the sphere: it works through
translations, and the sphere has none. A coupler can rotate about a fixed non-joint axis only if both crank lines always
pass through it, so only if a ground pin sits on it. The four-bar's moving pole is the honest spherical RCM.

**Rawest material.** The posed skin per bench pose (the bench distance grids of the scan-fitted body), mapped into the
frame of every MOVING body. A pin fixed in link 1 sees the skin that link 1 sees, not the skin the scapula sees. New
instrument: a body-frame free-space map (scratch `pinmap2.py`, results below). For every ray fixed in link 1 / link 2 of
the plain 3R at given axes, laid out around the J2 pole (arc d, angle psi), it gives the requirement in every closing
pose and the share inside one 12 mm window (one hub height in band).

**Instrument.**
* Closed-form spherical four-bar input-output: the kit's verified two-circle closure applied to the loop, Rodrigues
  rotations, a 1-D root of the coupler curve against the target circle.
* Spherical Grubler plus a numeric 3 x 3 Jacobian of the arm's rotation.
* The kit (K3 march, K2 dense continuity on every joint axis, K6 collisions, audit).

**Outside judge.**
* tools/concept_bench through `K.evaluate` (honest: march, dense K2, K6, audit), on Bench(60,160) fast for the search.
* The FROZEN best shape on Bench(110,360) exact through `tools/concept_bigbench.py` (verifier protocol, 1 mm radial
  part clearance).

## Mechanism

```
scapula -J1 (O20)- link 1 ==A0== crank A ==A1== coupler (link 2) -J3 (O20)- arm -> K7 neck -> BOTTOM
                          ==B0== crank B ==B1==
```

Every axis passes through GH. The home pose: J1 = bvec(az, el); J2_home at arc a1 from J1; J3 at arc a2 from J2_home,
at dihedral beta from the arc to J1. The crank great circles leave the pole at angles psiA / psiB, and the pins sit at
signed arcs dA0, dA1 / dB0, dB1 along them. At home the coupler turns, to first order, about J2_home, like the 3R's J2.
Away from home the pole moves.

* **Mobility.** Spherical Grubler with 6 bodies and 6 revolutes: 3(6-1) - 2*6 = 3. The loop alone: 3(4-1) - 2*4 = 1.
  The numeric Jacobian of the arm's rotation with respect to (phi1, theta, q3) is checked at the taken poses (red
  team below).
* **Joints.** 0 passive translations, no slide. Six bearing pairs, each at its real envelope (K4): all O20 x 12.25 mm
  by default; see Pins below for the slim option.
* **Undetermined coordinates: none.** The cranks and coupler are set by closure. In MVP1 the arm drives everything
  through the cuff. In MVP2, crank A's pin is the J2 actuator.
* **Ranges in ok.**
  - Both transmission angles (crank vs coupler at A1 and B1) within [25, 155] deg.
  - Coupler-curve crossing angle >= 12 deg. The 3R's 10 deg fold margin equals 11-34 deg here.
  - Pins of one body, and each pin against its body's J1 / J3 hub, >= 22 deg apart (two O20 bearings side by side).
  - Closure residual < 0.5 deg (measured 1e-4 deg).
* **Pins.** J1, A0 (the J2 drive in MVP2, the encoder in MVP1) and J3 are O20 v5 hubs (MR117-2RS pair, 12.25 mm
  stack). With `slim=1`, the three PASSIVE pins (B0, A1, B1) are MR63ZZ pairs (3 x 6 x 2.5, tools/hardware_catalogue.json: two plates, ~6 mm stack), crown 6 mm, footprint kept at the O20 disc (conservative). This is the thick-panel-origami move: thin passive hinges so crossing layers lift less. Default slim=0 (all O20).
* **Members (K4 / K5 / K7).** Every rigid body's straps form ONE polyline member (link 1: J1 -> nearer ground pin ->
  other ground pin; coupler: far pin -> near pin -> J3), so a body never collides with itself. Layers: the cranks lie
  lowest. The coupler passes over the cranks, the neck and link 1's pins (`over`, >= 1 mm), and link 1 passes over the
  cranks and the coupler's pins. K6 checks every other pair.

## New instrument: free-space maps in the frames of the MOVING bodies (rawest material first)

The proximity atlas gives the skin seen from the thorax and the scapula. A pin fixed in link 1 or link 2 sees
something else: the skin as that body moves. Scratch script `pinmap2.py` measures it. For the plain 3R at given axes,
each ray fixed in a body is laid out around a pole (arc d from the pole, angle psi as `layout()` measures it). The
script marches the skin requirement in every closing pose (Bench(60,160)) and reports the share of poses inside the
best 12 mm window: one hub height in band. `*` marks a ray that some pose sends INTO the body (requirement > 220 mm),
so a rigid part there must lift to 400 mm. Selected rows (d = 30 / 45 deg):

| base 3R axes | body (pole) | best sector | band there | worst sector |
|---|---|---|---|---|
| k2221 (J1 bvec(0.65, 76.8), 80.7 / 62.9) | link 1 (around J2) | psi 285-345 | 0.74-0.79 | psi 75-210: 0.17-0.35 * |
| k2221 | link 2 (around J2) | psi' 0-30 from the J3 arc | 0.78-0.88 | psi' 120-285: 0.17-0.54 * |
| k2221 | J2 ray itself (d 10) | - | 0.61-0.70 | - |
| jfront (J1 bvec(120, 60), 60 / 65) | scapula (around J1) | psi 300-90 | **1.00** | psi 165-225: 0.69-0.78 |
| jfront | link 1 (around J1) | psi 60-270 from the J2 arc | **0.93-1.00** | psi 300-15: 0.67-0.78 |
| jfront | link 1 (around J2) | psi 315-15 | 0.74-0.86 | psi 120-255: 0.13-0.47 * |
| jfront | link 2 (around J2) | psi' 255-285 | 0.70-0.81 | psi' 60-195: 0.14-0.37 * |
| front132 (J1 bvec(132, 16), 50 / 50) | scapula (around J1) | psi 330-60, d 45-60 | 0.93-1.00 | psi 120-240 * |
| posterior lead (J1 bvec(-24, 4), 65 / 65) | link 1 / link 2 (around J2) | none | <= 0.74, almost all * | - |

What it says:
* Around J1, metal fixed in the scapula or in link 1 can sit in band at one height in 93-100 % of poses.
* Around J2, every body has a blocked half-plane where the raised arm or the torso crosses the ray. The free half
  reaches 0.74-0.88, while the J2 ray itself reaches 0.45-0.70.
* So the J2 neighbourhood is the worst place for metal in EVERY frame, not only on the J2 ray. A linkage that keeps J2's
  motion must keep its pins within ~30-60 deg of J2, so it inherits the blocked half-plane. This is the measured reason
  the four-bar's own pins fail (below).

## Coarse sweeps (farm, Bench(60,160) fast, every kit check on)

| stage | configs | honest | best honest gap | best any gap | closure p50 |
|---|---|---|---|---|---|
| v1 random layouts (before the member fix: same-body straps were separate K6 pairs, no layers) | 210 | 2 | 275.0 | 146.20 | 0.00 |
| v2 structured from the free-space map (before the member fix) | 142 | 14 | 203.29 | 203.29 | 0.32 |
| v3 = v2 + 60 of v1, final members and layers, q in {0.93, 0.97, 1.0} | 202 | 33 | **145.94** | 104.57 | 0.23 |
| rp: remote-pole family (cranks 55-115 deg from the pole, nearly parallel) | 210 | 5 | 177.76 | 176.59 | 0.00 |

What the sweeps taught, in order:
1. **Thickness accommodation is the first wall.** In a random layout the coupler pins sweep over link 1 and the
   cranks sweep under the coupler. With straps as separate members and no layers, 60-98 % of the closing poses had a
   part-part collision. The polyline members plus explicit layers (`over`, as thick-panel origami stacks its panels)
   bring that to 1-30 %. The price is that the upper layer lifts by the lower layer's 12.25 mm hub crown + 1 mm, out of
   the band wherever the layers cross.
2. **The four-bar margin is the transmission angle, not the circle-intersection margin.** The first margin (the
   two-circle closure's distance from its arccos ends) rejected four-bars whose transmission angle was 116 deg.
   Replaced by the transmission angle at both coupler pins in [25, 155] deg.
3. **Remote-pole layouts (a spherical "parallelogram") put the pins close to the skin.** Nearly parallel cranks meet
   about 90 deg away: the instantaneous pole sits ~90 deg from all four pins, the spherical RCM. Hubs fitted at 54-75 mm
   (the J1 hub sits at 55): pins on quiet skin, as the field promised. But those pins are then 10-20 deg from the J1 or
   J3 hub and collide with them. With a 22 deg separation rule they collide with hub J3 and the neck instead whenever
   the J2 angle closes (68 and 39 of 128 closing poses in the probe). Best honest 177.76.
4. **Crossed cranks through the pole region reach furthest.** These are the v3 rows with dA1 < 0 (crank A runs from a
   link-1 pin across the pole region to a coupler pin on the J3 side). Best any 104.57: reach 0.69, follow 0.88. But
   the cranks pass over the pole region, which is the worst skin in every frame (the map above). They park at 400 mm
   (in-band 0.19, not honest).

### The free wedge: where a converging J2 four-bar can put its pins (scratch `wedge.py`)

A crank joins a link-1 pin to a coupler (link-2) pin on ONE ray through the pole, so both pins need a ray that is free
in link 1 AND in link 2 (at the 3R's median home dihedral beta). For each arc d, the widest run of such rays (band >= 0.7,
never into the body), and the bearing separation that run allows (two O20 pins need ~22 deg):

| base | d 20 | d 30 | d 40 | d 50 | d 60 |
|---|---|---|---|---|---|
| k2221 | 60 deg / 20 | 45 / 22 | 60 / 37 | 30 / 23 | 0 / 0 |
| jfront | 0 / 0 | 45 / 22 | 45 / 28 | 60 / 45 | 90 / 76 |
| front132 | 0 / 0 | 0 / 0 | 0 / 0 | 15 / 11 | 0 / 0 |

At a 0.6 band threshold the wedges widen to 75-105 deg. So a converging four-bar FITS geometrically on k2221
(d 30-50) and jfront (d 40-60), but only with every pin at 0.7-0.8 band, which is no better than the 3R's own hub 2
(0.61-0.70). On the fold-free front132 layout no free wedge exists.

## Field options considered and rejected before modelling (with the reason)

* **Planar double-parallelogram RCM** (Taylor; the da Vinci arm). Pins parallel to the J2 axis, the links in the
  plane normal to it, which is roughly tangent to the skin. It gives an EXACT remote centre on the J2 line, so the
  kinematics are the 3R's and no slide is needed. It was not built, for two reasons:
  - Its translating coupler is not a GH-ray body, so the kit's skin-fitted members (radial rays from GH) cannot
    represent it honestly. It needs a new member kind.
  - A flat linkage tangent to a 60 mm-radius sphere leaves the skin by x^2 / 2R: 7.5 mm at x = 30 mm. Its links and
    pins must also orbit the virtual centre, so the metal does not leave the J2 neighbourhood, which the map above
    shows is the worst skin.
  Range is fine: a double parallelogram stays clear of its singularities over +-75 deg about the mid position, and the
  3R's J2 uses ~85-90 deg (p5-p95 of beta).
* **Spherical double parallelogram.** It does not exist: the planar version works through translations. A spherical
  four-bar coupler turns about a FIXED non-joint axis only if both crank great circles always pass through it, which
  happens only if a ground pin sits on it.
* **Bennett loop as link 2.** Its axes are skew, so its coupler motion is not a rotation about GH. The 2-slide cuff
  closes exactly only when J1 and J2 pass through GH (offset-skin-normal-3r's closure theorem). A Bennett link 2 would
  need the radial third slide, i.e. 3 passive translations, which the rules forbid.
* **Spherical lazy tongs / angulated scissors along a great circle.** The tongs' end pivot moves along the circle,
  which is a rotation about its pole, but no lame keeps its orientation. A rigid link 2 would need a further
  constraint (another loop), and the metal would sit 90 deg from J2 at constant radius, which is the remote-pole family
  that was swept (rp rows).

## Control: the plain 3R at the same axes (same bench, same checks; `_template.py`, q 1.0)

| base axes | plain 3R gap | reach | follow | in-band 14 | hub 2 in band | link 2 in band |
|---|---|---|---|---|---|---|
| k2221 | **51.97** | 0.888 | 1.0 | 0.393 | **0.00** | 0.056 |
| jfront | 119.28 (not honest: parked parts) | 0.70 | 0.967 | 0.082 | 0.00 | 0.00 |
| front132 | 87.52 (not honest) | 0.888 | 0.95 | 0.103 | 0.026 | 0.00 |

At k2221 the 3R's hub 2 is 0 % in band and link 2 is 6 %. The best coarse four-bar there (145.94) puts its A side in
band: hub A0 0.59, hub A1 0.57, crank A 0.69. So the virtual pole does improve the skin near J2 on the side where the map
said the skin is free. It loses on everything else: reach 0.43 / follow 0.55 against 0.89 / 1.0, and the B side and
the coupler land in the blocked half-plane (0 %).

### How far the virtual pole walks, and how far the coupler turns (best coarse honest layout, k2221 base)

| crank angle theta | coupler turned from home | pole walked from its home ray | transmission margin |
|---|---|---|---|
| -49.0 (window end) | 25.3 deg | 25.7 deg | 25.1 |
| -13.5 | 6.7 | 7.9 | 45.8 |
| 22.2 | 10.8 | 12.7 | 69.4 |
| 58.0 | 28.9 | 29.2 | 58.1 |
| 93.5 (window end) | 55.1 | 35.1 | 25.0 |

* Inside the transmission window the coupler turns about 80 deg in all. The 3R's J2 at these axes uses about 88 deg
  (p5-p95 of the dihedral beta, -129 to -41), and the overhead poses sit at the ends. That is the measured reason
  71 of 220 poses do not close (12 of the 17 overhead poses).
* The pole walks up to 35 deg from home, about 40 mm at the hub radius. The "virtual J2" is not where the 3R's J2 is
  for most of the motion, so link 1 moves differently from the 3R whose free-space map placed the pins. The A side
  stays in the free half (0.57-0.69 in band); the B side drifts into the blocked half (0 %).

### Can a virtual-pole J2 widen the fold window instead? (leader seats k4216, measured)

At the seats of the zero-passive 3R at k4216 (J1 bvec(95.9, 65.2), arcs 40.3 / 74.1; spine-parked-j2-3r), the
free-space map is almost clean. Link-1 rays around J2 are 0.9-1.0 in band over psi 240-90, and link-2 rays 0.92-0.99
over psi' 285-120. The skin is not that layout's problem; its 47 fold poses are. So the other question for a moving
pole: does the four-bar's coupler curve sweep a WIDER range of the J1-J3 axis angle alpha than the 3R's circle?

4000 random four-bars were placed in those free sectors (d 12-45, cranks 22-40, beta -125 to -35); 295 assemble inside
the transmission window. On the monotone branch through home, alpha spans p50 34.8 deg and at most **81.9 deg** (29.1
-> 111.0). The 3R at the same arcs spans 80.7 raw (33.7 -> 114.4) and 60.7 with its 10 deg margins. Some four-bars
SHIFT the window (2.4 -> 75.7, or 70.9 -> 143.2), but none widens it. The window still closes at a tangency, where the
crossing angle goes to 0, so the 12 deg crossing rule trims it like the 3R's margin.

Measured conclusion: a virtual pole moves the fold window; it does not widen it at equal link size. The fold is a
property of how far the carried axis can swing relative to J1, whatever produces the swing.

## Frozen shape on Bench(110,360) exact, and red team: coarse best honest (v3, k2221 axes)

Files: docs/concepts/sweeps/_big_vp4j2-coarse.json (`tools/concept_bigbench.py --mode frozen`, CB_EXACT=1, 1 mm radial
part clearance) and _rt_vp4j2-coarse.json / _rtfast_vp4j2-coarse.json (`docs/concepts/verify/virtual-pole-4bar.py`).

| bench | gap | reach | follow | in-band 14 | in-band 10 | contact |
|---|---|---|---|---|---|---|
| Bench(60,160) fast (search) | 145.94 | 0.425 | 0.550 | 0.363 | 0.203 | 0.047 |
| Bench(60,160) exact (fit) | 147.34 | 0.419 | 0.550 | 0.364 | 0.203 | 0.057 |
| **Bench(110,360) exact, frozen** | **151.43** | 0.361 | 0.564 | 0.365 | 0.203 | 0.054 |

* **Jam poses (frozen, 470 poses).** 192 do not close: the coupler leaves the transmission window or the crossing
  rule fails. The "Raise overhead" clip jams from elevation 21 deg up. 75 have a part-part collision and 11 skin
  contact.
* **Overhead (elevation >= 140).** 7 of 38 taken (27 lost to closure); 0.49 in band on the poses taken.
* **Pinch.** The closest metal is the K7 neck at 0.28 mm (ws plane 60, elev 165), then the neck at 0.51 mm and the
  coupler at 0.75 mm (plane 90, elev 150). Counting < 1 mm as contact: gap 153.74, 3 poses.
* **Mobility.** The 3 x 3 matrix of instantaneous axes (J1, four-bar pole, J3) has rank 3 at all 203 taken poses:
  sigma_min / sigma_max >= 0.229, p5 0.288. No undetermined coordinate, no singular pose taken.

Per-hub metal-to-skin distance over the taken poses (coarse best, Bench(60,160) fast; p5 / median / p95, mm):

| hub | level (mm from GH) | p5 | median | p95 |
|---|---|---|---|---|
| J1 | 55.0 | 2.7 | 2.9 | 3.0 |
| A0 (link 1, free half) | 69.0 | 7.4 | 12.8 | 20.2 |
| A1 (coupler, free half) | 63.6 | 2.8 | 11.9 | 18.6 |
| B0 (link 1) | 83.1 | 10.6 | **27.9** | 31.5 |
| B1 (coupler) | 92.1 | 24.9 | **31.7** | 31.7 |
| J3 | 68.0 | 2.6 | 10.3 | 19.2 |

The B pins sit 28-32 mm off the skin. That is the same ~31.8 mm the osn fold-seed hub 2 reached, and for the same
reason: the raised, externally rotated arm comes up under the J2 neighbourhood. The four-bar splits hub 2 into an A
side that fits and a B side that inherits the problem.

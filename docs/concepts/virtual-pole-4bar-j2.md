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
* **Joints.** 0 passive translations, no slide. Six O20 bearing pairs, each at its real 20 mm x 12.25 mm envelope (K4).
* **Undetermined coordinates: none.** The cranks and coupler are set by closure. In MVP1 the arm drives everything
  through the cuff. In MVP2, crank A's pin is the J2 actuator.
* **Ranges in ok.**
  - Both transmission angles (crank vs coupler at A1 and B1) within [25, 155] deg.
  - Coupler-curve crossing angle >= 12 deg. The 3R's 10 deg fold margin equals 11-34 deg here.
  - Pins of one body >= 20 deg apart.
  - Closure residual < 0.5 deg (measured 1e-4 deg).
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

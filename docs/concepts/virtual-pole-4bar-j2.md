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

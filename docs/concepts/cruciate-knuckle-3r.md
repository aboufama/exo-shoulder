# cruciate-knuckle-3r: a crossed (cruciate) spherical four-bar as J2 at the cap pole

Status: screening (round 102, track jump, lens virtual-j2's crossed cell). Model:
`docs/concepts/models/cruciate-knuckle-3r.py`. Sweep: `docs/concepts/sweeps/cruciate-knuckle-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** The catalogue spec replaces all three
   revolutes with hubless rolling knuckles. That is the wrong target twice over. "Keep O20 only" rules out the hubless
   pins, and J1 and J3 are not the limiter. The measured limiter at the cap-pole seats is J2. Its ray leaves the skin
   107-116 mm from GH on the binder poses, so any metal on that ray is out of band. So the designer would build a knee,
   not three knuckles: one crossed four-bar at J2, with J1 and J3 kept as plain O20 hubs. The knuckle's rolling centrode
   is the design variable, as in a polycentric orthotic knee (O'Connor, Zavatsky). The designer would also see the cell's
   own weakness straight away. The instantaneous axis IS the crossing of the two ligaments, so the crossed cell does
   put metal on the J2 ray: two 3 mm cranks instead of a 12.25 mm stack. The question to measure is whether two
   thin bars can ride over the high skin there while all four O20 pins sit on low skin. The cell's kinematics are not
   the question. Lens 1's synthesis at the cap seats (rp4/kin.py, 4000 random layouts) gives the crossed layouts the
   widest th windows on file: W up to 162 deg, kinematic reach 0.986. The open layouts top out at W 127 / 0.928.
2. **Rawest material.** I used the posed skin directly: the signed distance on the Bench(60,160) fast grid, with every
   metal sample's K3 march per pose. I also used the motion clips and workspace poses of Bench(60,160) /
   Bench(110,360), and the J2-ray skin exit per pose (judge102/j2exit.py: the cap control's J2 ray exits > 75 mm on
   18 % of closing poses, max 215 mm). Lens 1's proxy instrument (rp4/opt.py, calibrated: plain cap 3R 36.6 proxy vs
   56.40 frozen exact) is the search's inner loop. I did not search on digested summaries.
3. **Methods and tools.**
   - Closed-form spherical four-bar closure (two-circle intersection; virtual-pole-4bar-j2's FourBar).
   - The longest monotone run of th(theta) with both transmission angles in [30, 150] deg, and the 5-deg th margin at
     the run's ends. This is the fold rule read in ONE metric, th. The stop is a dowel on crank A's own angle.
   - A spherical-arc crossing test, so the cell stays cruciate over the whole run.
   - The shared kit for every metal part: O20 hubs at all six pins, 12 x 3 cranks / links with 60-deg climb ramps, the
     K7 neck, the K3 march, K2 dense continuity and K6 collisions.
   - (1+1)-ES restarts on the proxy, then honest kit evaluations of the top configurations.
4. **What shows the number is right, other than me.**
   - The kit bench, Bench(60,160) fast, with the honesty audit.
   - The plain cap-pole 3R control through the same code.
   - A frozen exact wear on Bench(110,360) when time allows.
   - The adversarial verifier, with this red-team pose list: the cap pole's binder poses (-75, 60, +60),
     (0..30, 150, 0) and (0, 105, 0); the poses where a coupler pin's axis runs down the arm or into the torso (the K3
     march finds no skin exit within 220 mm); and the crank crossing over a pin hub.

## What was built (and where the spec was wrong)

The spec's three hubless knuckles were not built. "Keep O20 only" excludes them, and the measured limiter is J2, not
J1 / J3. What was built is lens virtual-j2's **crossed cell**, the form the round-102 plan allows:

- a plain O20 J1 at the cap pole, bvec(43.15, 59.93);
- a plain O20 J3 on the arm, wdir(92.03, -9.03);
- J2 replaced by a spherical four-bar whose two cranks cross:
  - link 1 carries the ground pins A0 (ACTIVE, the J2 drive) and B0;
  - crank A runs A0 -> A1 and crank B runs B0 -> B1, crossing crank A 1 mm above it;
  - the coupler carries A1, B1 and the J3 hub.

All six pins are O20 v5 stacks (12.25 mm). The links and cranks are 12 x 3 mm straps on skin-fitted undersides with
60 deg climb ramps, and the K7 neck runs to BOTTOM.

Mechanism and rules:

- **DOF.** 3 active (J1, A0, J3) + 3 passive pins (B0, A1, B1) set in closed form by the crank angle. 0 passive
  translations, 1 closed loop, no spring, nothing undetermined.
- **Cruciate.** The arcs A0 -> A1 and B0 -> B1 cross at 9 crank angles across the whole working run (`arcs_cross`), so
  the cell is a true X, not an open four-bar.
- **Fold rule in th.** The window is the longest monotone th run with both transmission angles in [30, 150] deg, minus
  K.FOLD_MARGIN = 5 deg at each end. The end stop is a dowel on crank A's own angle.
- **Pins.** Same-body pins are >= 22 deg apart, as in lens 1's rule.

Two layouts are in the model: pole-centred (virtual-pole-4bar-j2's) and **anchored** (lens 1's: link-1 pins placed
around J1, coupler pins around J3). The search ran on the anchored one.

## Instruments and search

1. **Proxy search** (lens 1's `rp4/opt.py`, unchanged, plus a crossing penalty and a hard 22-deg pin rule).
   - (1+1)-ES restarts: 2 x 11.25 k tries.
   - Then CMA-ES restarts from the top: 4 rounds, ~3.9 k tries.
   - Proxy best: 42.34. On the same proxy the plain cap 3R reads 36.6.
2. **Honest kit evaluation** of the proxy's top configurations (Bench(60,160) fast, K3 march, K2 dense, K6).
   - The proxy does not carry over. Proxy 42.34 -> kit 103.72; proxy 63.38 -> kit 79.77.
   - The proxy samples only centre rays and has no collisions; the crossed cell loses 7-29 % of its closing poses to
     K6.
3. **CMA-ES with the honest kit in the loop**, from the two best kit configurations: no improvement in ~620 tries.
4. **Control: the plain cap-pole O20 3R through the same kit and bench** (`_template` build, 50.2 / 60.3, sigma -1,
   q 1.0): **63.18**, honest. Reach 0.794, ib14 0.375, contact 0; hub 2 0.048 in band, link 1 0.194, link 2 0.041.

Sweep: `docs/concepts/sweeps/cruciate-knuckle-3r.json`. It holds every honest-kit evaluation in time order, including
the layouts that do not assemble a crossed window (gap 275).

## Results (Bench(60,160) fast, kit checks)

| configuration | gap (score) | reach | follow | ib14 / ib10 | contact | W (th window) | notes |
|---|---|---|---|---|---|---|---|
| plain cap-pole O20 3R (control, same code) | 63.18 (77.0) | 0.794 | 1.0 | 0.375 / 0.192 | 0 | 50.2/60.3 dyad | hub 2 0.048 in band |
| **cruciate J2, best honest** (sweep k25) | **86.95 (68.4)** | 0.7125 | 0.883 | 0.285 / 0.134 | 0 | 76.6 [33.5, 110.1] | min th margin 5.80, min transmission 33.7, pin sep 22.0, collide 7.2 %, mass 232 g |
| cruciate J2, best measured (sweep k1) | 79.77 (71.0) | 0.85 | 1.0 | 0.219 | 0 | 101.1 [32.8, 133.9] | audit flag: crank B floats > 140 mm, so its 2 mm layout spreads to 4.6 mm (sparse). Not honest-clean; in-band 0 either way |

Kinematically the crossed cell does what the knee does. Its th window reaches W 101 at legal pins, against the plain
dyad's ~90. Lens 1's synthesis found W 162 / reach 0.986 with long cranks. The honest best's window reaches 0.733 of
the Bench(110,360) workspace and 0.891 of its clips (no metal). The metal is what fails.

Per member in band, honest best:

| member | in band | level | binder poses |
|---|---|---|---|
| J1 hub | 1.00 | | |
| A0 hub | 0.00 | 79 mm | ws (0, 150, 0) |
| B0 hub | 0.00 | 129 mm | (0, 150, 0), (-15, 105, 45) |
| A1 hub | 0.003 | 109 mm | ws (0, 60, -60) |
| B1 hub | 0.81 | | |
| J3 hub | 0.66 | | |
| crank A | 0.11 | 107 mm | |
| crank B | 0.15 | 130 mm | |
| link 1 | 0.005 | 121 mm | |
| coupler | 0.10 | 101 mm | |
| neck | 0.74 | | |

The binder poses are the cap pole's mode-A poses from the round-102 plan: (0, 150, 0), (15, 150, 0), (0, 105, 0) and
(-15, 105, 45). At the median pose every member's requirement is only 56-67 mm, so the levels come from a few poses.

## Verdict: DEAD at gate 0

The best honest gap is 86.95, and 79.77 is the best measured. Both are far above lens 1's 17.5 kill bar, and the cell
is 16.6-23.8 points worse than the plain cap-pole 3R through the same code (63.18).

**Convergence gate (kit sweep, 662+ tries):**

- best gained 0.00 score points over the second half and 0.00 over the last third;
- the top 5 distinct configurations (79.77, 83.36, 84.65, 86.45, 86.95) lie within 2.61 score points.

The gate passes.

The proxy search alone was not converged (its last CMA round still gained ~6 proxy points). But proxy gains did not
carry over to the kit: proxy 42.34 read 103.72 in the kit. Given the time box, the kit-in-the-loop CMA is the gate of
record.

**Measured limiter.** The crossed cell does not escape the cap pole's binder. At the overhead abduction poses
(0..15, 150, 0) and at (0, 105, 0) the skin is high in a band around the J2 ray, not only on the ray:

- the link-1 pins (A0, B0) sit 22-47 deg from J1;
- crank B and link 1 pass the same deltoid / acromion bulge;
- all of them are pushed to 79-130 mm there, while the median pose asks only 56-65.

The cell also adds what the plain chain does not have:

- four more O20 crowns where hub 2 used to be one;
- a second crank layer at the crossing;
- K6 losses where a crank crosses a pin hub (7-29 % of closing poses).

**Ideal pose-drop bound** (honest best, proxy in-band). Dropping the 20 worst binder poses (11 % of the closing set)
lifts the sample-weighted in-band share from 0.62 to 0.78, and it plateaus at 0.80 after 40. On this design the proxy
reads ~0.33 above the kit's in-band (0.62 vs 0.285). So even joint stops that exclude every binder pose, paid for in
reach, leave the cell above the 17.5 bar.

## New knowledge

1. **A crossed four-bar puts metal on its own pole.** The instantaneous axis is the ligament crossing, so the cruciate
   cell is the WRONG virtual-J2 cell wherever the J2 ray is the binder. Only the open (remote-pole) cell keeps the ray
   clear.
2. **The cap pole's binder is a zone, not a ray.** At (0..15, 150, 0) every member of either body within ~25-50 deg of
   J2 is pushed to 79-130 mm. So any virtual-J2 cell whose pins or cranks pass there fails the same way.
3. **Link-1 metal can sit in band near J1 in the plain 3R's link-1 frame** (scratchpad `cruc/ring.py`; Bench(60,160)
   fast, plain cap 3R closure, a point at cone angle d from J1 and dihedral psi from the arc J1 -> J2):

   | d from J1 | best psi | in-band share there | median over psi |
   |---|---|---|---|
   | 22 deg | | | 0.93 |
   | 30 deg | 0 (toward J2) | 1.0 | |
   | 40 deg | 60 | 0.87 | |
   | 50.2 deg (hub 2's ring) | | 0.083 at best | |

   A four-bar's link 1 does not turn like the plain 3R's: its pole walks, so its pins pass the binder zone. Hence any
   virtual-J2 synthesis should constrain the fixed centrode to stay within ~30 deg of J1 on the J2 side, which is a
   different cell from both the open and the crossed ones tried here.
4. **Lens 1's proxy is optimistic by ~0.3 in in-band for four-bar cells**, because it samples only centre rays and
   has no layering or collisions. Use the kit in the loop for four-bar cells.

## Red team (own best)

- **Jam.** The minimum transmission over taken poses is 33.7 deg, 3.7 deg above the toggle guard. The run's end
  stops are on crank A's own angle, and the th margin is 5.80 at worst.
- **Pinch.** At the ligament crossing, crank B passes 1 mm over crank A, built by `over`. K6 still rejects 7.2 % of the
  closing poses where a crank meets a pin hub. Near-touch was not run (dead design).
- **Optimistic number.** 79.77 carries the sparse-sampling audit flag (crank B floats > 140 mm). The row reports the
  honest-clean 86.95. Both are fast-cache numbers on Bench(60,160). No frozen exact Bench(110,360) wear was run: the
  fast number is 4.5x the kill bar, and the 360-pose workspace would only add binder poses (the plain cap 3R loses
  63 -> 56 frozen).
- **Follow.** The honest best follows 0.883: the knuckle's run ends cut some clip frames, unlike the control's 1.0.

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

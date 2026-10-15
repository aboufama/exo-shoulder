# Dynamics judge: does the chain actually move when the arm drives it?

Research note, 2026-10-15. Judge: `judge/dynamics.py` (MuJoCo 3.16, local CPU, <= 4 processes), test:
`judge/test_dynamics.py`, results: `pipeline/full-exo/designs/<id>/judge/dynamics.json`. Nothing was downloaded or
installed; papers were read on the web for the interface stiffness and the ISO/TS 15066 values (references at the end).

The question (user, 2026-10-15): "if there's some slight friction perhaps it will be hard for a linkage to pass over
another because it's pressing from a bad action angle ... It needs to actually work". Every judge before this one is
geometric; `pipeline/conformal/analysis/transmission.py` did the quasi-static check with ideal massless joints. This
judge adds what a real chain has: link mass and inertia, gravity, joint friction (constant and load-dependent), a soft
cuff on a soft arm, contact between the stacked links, real and double clip speed.

**Scope (user via the lead, 2026-10-15): MVP1 is unpowered** - a kinematic proof of concept, no motors, gears, pulleys
or cables. The main case is therefore a fully passive chain on **high-quality rolling bearings**; plain (iglidur)
bearings are the comparison. The motor-armature and servo cases built earlier remain as `--cases` options and are not in
the results below.

## 1. Answer

**MVP1 (passive, rolling bearings mu_eff 0.005, tau0 0.001 N.m), all 8 clips, worst clip per design:**

| design | interaction moment about GH, peak (1x / 2x speed) | cuff force peak (1x / 2x) | mean cuff pressure | cuff twist | joint speed peak (x arm) | spare J1 off its planned path | links touch (beyond the plan's own overlap) | moves freely? |
|---|---|---|---|---|---|---|---|---|
| band_r14_3r_s1351_1 (3R) | **0.05 / 0.10 N.m** | 0.2 / 0.4 N | 0.035 kPa | 1.2 / 1.8 deg | 242 deg/s (1.6x); 504 at 2x | - | **none** (no adjacent pair ever within 2 mm) | **yes** |
| band_r14_4r_s1354_0 (4R) | 0.13 / 0.24 N.m | 0.6 / 1.1 N | 0.08 kPa | 2.0 / 2.9 deg | 318 deg/s (2.9x) | **63-100 deg in every clip** | l2-l3, 1-5 N (10 N at 2x), most of every clip | **no**: the spare falls |
| cad_r13_n4_s1343_1 (reference 4R) | **2.3 / 2.4 N.m** (Raise overhead) | 10.5 / 10.8 N | 1.5 kPa | 11.5 deg | 238 deg/s (3.4x) | 9-45 deg | l1-l2, l2-l3, up to **121 N** (Raise overhead, Wave) | **no**: it jams on its own links |

1. **The 3R works as a passive chain on good rolling bearings.** The wearer drives it through every clip with at most
   0.05 N.m about the shoulder at real speed (0.10 N.m at 2x), 0.2-0.4 N at the cuff, 0.035-0.065 kPa of mean cuff
   pressure (0.5 % of the 7.5 kPa sustained budget left after the strap), no stall that misses 10 deg of joint travel,
   never a link touching another.
   That is 20x under the proposed "not felt" limit (1 N.m). Friction is not even visible at this level: the same motion
   with zero friction gives 0.05 / 0.09 N.m. What the wearer carries is the links' own weight (0.03-0.05 N.m; 89 g of
   Ti proxies) and, at 2x speed, their inertia (up to 0.11 N.m in the worst jerk, Reach back pocket's held-to-resume
   step). Sealed bearings (tau0 0.005 N.m) give 0.07 N.m; the cuff stiffness (1-5 N/mm) does not change the moment and
   moves the twist between 0.8 and 4 deg.
2. **A passive 4R does not stay on the path every geometric judge assumes.** Its spare degree of freedom (J1) has no
   stiffness: with free bearings the chain folds under its own weight within 0.1 s of standing still (54 deg in the band
   4R, 19 deg in the reference) until two links rest on each other; with gravity switched off it still drifts 10-37 deg
   once the arm moves (self-motion). R1 / R2 / R6 for the 4R designs judge a configuration the unpowered chain never
   takes. With plain bearings friction holds it better but still not on the plan (per clip 11-78 deg in the band 4R,
   19-45 deg in the reference).
3. **The reference design jams kinematically.** After the spare has dropped, l2 runs into l3 in Raise overhead and Wave:
   up to 121 N of link-on-link contact, and the arm needs 2.3 N.m about GH (10.5 N at the cuff) to push through. The
   friction-free and gravity-free run needs the same 2.3 N.m, so this is geometry (the chain folding into itself), not
   friction. It is the jam the user asked about, but caused by the free spare, not by an action angle.
4. **With plain bearings the action angle matters, as the user suspected** (load-dependent friction, red team G6):

   | mu_eff (tau0 0.05) | 3R peak about GH (tilt about GH / about the bearing) | 3R clips that lock | band 4R | reference 4R |
   |---|---|---|---|---|
   | 0.06 (washers carry the tilt, mu 0.06) | 0.31 / 0.30 N.m | 0 | 0.41 / 0.43 N.m | 3.0 / 2.7 N.m |
   | 0.15 | 0.63 / 0.64 N.m | 0 | 0.49 / 0.57 N.m | 6.7 / 9.5 N.m |
   | 0.25 | **3.1 / 4.2 N.m**, 14 / 19 N (Wash) | 0 | 0.86 / 1.87 N.m | **47 / 51 N.m, 5-6 of 8 clips lock** |
   | 0.37 (worn: the sleeve carries the tilt) | **29 / 101 N.m**, 136 / 550 N | **2 / 4** (Wash, Reach back pocket; + Raise overhead, Wave) | 49 / 98 N.m, 1-2 lock | 74 N.m, all 8 lock |

   "Lock" = the arm would need > 10 N.m about GH or > 150 N at the cuff (ISO/TS 15066). The reference's numbers include
   its 2.3 N.m kinematic jam (item 3) and its larger friction amplification (up to 5.3, cond(U) up to 5.0). The 3R stays
   under 1 N.m at mu_eff 0.15 (its cuff twists 8 deg),
   near-locks in Wash at 0.25 (rt_wedge.py: self-locking from mu_eff 0.215 on the planned path; the soft cuff lets the
   chain twist off the locking configuration, so the dynamics needs 3-4 N.m instead of infinity) and locks at 0.37. Once
   wedged it stays wedged when the arm stops: the cuff's own restoring moment loads the bearings (Reach back pocket at
   0.37: 83 % of its frames over 10 N.m). The tilt taken about the bearing centre (the cuff force times the hub's
   distance from GH adds to the tilt, the red team's R x F term) makes it worse at high mu_eff (101 vs 29 N.m).
5. **Constant friction (the brief's sweep), passive, 3R:** 0.05 N.m per joint -> 0.23 N.m about GH, 1.0 N; 0.2 -> 0.85 N.m,
   3.9 N; 0.5 -> 2.0 N.m, 9.1 N (worst: Wash opposite shoulder, friction amplification 4.3-4.8 at cond(U) 3.1). The same at
   2x speed (friction-dominated): of the 0.85 N.m, 0.05 is gravity + inertia, 0.80 friction x amplification.
6. **Cuff twist is the soft spot of any friction.** The cuff's torsional stiffness about the humerus is only 0.03 N.m/deg
   (Schiebl 2025), and every design's resistance has a component about the humerus axis (JN's axis W is 56-84 deg off
   it). With plain bearings the cuff turns 5 / 17 / 37 deg on the arm (0.05 / 0.2 / 0.5 N.m friction), at a sustained
   axial moment of only 0.17-1.1 N.m; the chain then lags the arm by that much (the "stalls" in dynamics.json are this
   lag). A stiffer torsional path (x10, as the user's forearm cuff gives with the elbow bent) cuts it to 1.9 deg. With
   rolling bearings it is 1-3 deg (3R / band 4R).
7. **Joint speeds and accelerations** stay modest at real speed: up to 242-318 deg/s (1.6-3.4x the arm's angular speed,
   highest in Wave, the fastest clip), 6,000-38,000 deg/s^2; 2x speed doubles the speeds and quadruples the
   accelerations (3R: 504 deg/s, 5.6x in Wave). Nothing comes near a chain singularity (cond(U) <= 3.5 for the 3R, <= 5.0
   for the reference). The clips' held-to-resume steps (the geometric pipeline holds the arm where the exo cannot follow,
   then resumes within 4 deg in 0.1 s) are real accelerations in these clips and inflate the 2x inertia terms.
8. **All-day cuff pressure is not the constraint.** Mean pressure on the cuff's 68 cm2 from the chain: 0.035 kPa (3R),
   0.08 kPa (band 4R), 1.5 kPa (reference; 1.8 kPa with its 154 g of arm-side parts hanging on the cuff), against the
   7.5 kPa the 14 kPa budget leaves after the strap preload. It is exceeded only where plain bearings wedge (3R at
   mu_eff 0.37: 20-81 kPa mean).
9. **No motors (MVP1).** The motor-armature case (0.03 kg m^2 reflected per joint) built before the scope change gave
   2.5-5.5 N.m and 11-25 N for the 3R; it is kept only as `--cases motor`.

**Verdict for the lead.** For an unpowered MVP1 the 3R is the design that can actually be driven by the arm: on
rolling bearings it is transparent (<= 0.10 N.m, <= 0.4 N, <= 1.8 deg twist, no contact); on plain bearings the moment
stays under the 1 N.m felt limit up to mu_eff ~0.15 but the soft cuff twists 6-8 deg, and it wedges in Wash beyond ~0.22,
i.e. it needs bearings whose tilt is carried by rolling elements (or, second best, the thrust washers), never by a worn
sleeve. Both 4R designs need something to hold the spare DOF (a
detent, a spring, or a motor) before their geometric scores mean anything; the reference additionally jams on its links.

## 2. Model

| element | how | source / assumption |
|---|---|---|
| frame | body-rig thorax frame, x anterior, y up, z right, origin = right GH centre; gravity -y (standing) | `pipeline/avg/body_pose.py` |
| scapula + base | base body on a ball joint at GH, driven along the rig's scapula law `scap(elev)` by feed-forward + PD on a 1000 kg m^2 armature: the chain sees the base's real angular velocity and acceleration, the base does not feel the chain. The base part is rigid on it (the user's scapula handler is separate). The law's 20 deg kink (`max(0, elev - 20)`) is rounded over 1.5 deg (softplus); otherwise the base would get an angular-velocity step | `body_pose.scap` |
| links | serial hinges J1..J(N-1) with axes through GH, built from `design.json` exactly as `band_impl.chain()` (b = bvec(az, el), arcs a, closure branch); body frames = the exo.glb group frames | <= 0.024 deg from every frame's G in clips.json (all three designs) |
| link mass | trimesh mass properties of the L1 meshes per motion group (welded, every component closed): Ti-6Al-4V 4.43 g/cm3; iglidur 1.46; magnets 7.5; PCB 1.85; steel screws 7.9; AlSi10Mg 2.67; 7075 2.81; user parts otherwise 2.8 | band proxies carry no bearing hardware (see limits) |
| arm | the humerus follows the clip's followed pose `p` (the same frames every other judge uses) kinematically; the 30 fps poses are piecewise linear between 10 fps samples, so the path is a PCHIP through the clip's knots (C1, no overshoot, finite accelerations). Held frames hold the arm | `clips.json` |
| cuff | the arm-side member at JN (hinge about W) is joined to the humerus bone by a 6-axis spring-damper at the cuff centre on the humerus axis, 200 mm from GH (the user's upper-arm cuff spans 165-246 mm): 3.5 N/mm across the arm, 2.1 N/mm along it, 0.20 N.m/deg bending, **0.03 N.m/deg torsion about the humerus**; damping 20 N.s/m, 0.1 / 0.02 N.m.s/rad (assumed) | Schiebl et al. 2025 medians (2.1-4.5 N/mm, 0.18-0.22 and 0.03 N.m/deg; 9 cm brace at 65 mbar); Langlois et al. 1.1-2.2 N/mm (soft cuff, 0-100 mmHg) |
| what is "interaction" | the tissue wrench. The cuff member is 20 g and gravity-compensated: the user's arm parts (BOTTOM, cuffs, elbow) are carried by the arm, so every N and N.m reported is what the **shoulder chain** adds; their own weight is listed separately | |
| joint friction, main | rolling bearings, load-dependent: tau_f = tau0 + mu_eff \|M_perp\|, mu_eff 0.002 / 0.005, tau0 0.001 N.m | see below |
| joint friction, comparison | plain bearings, the same law with mu_eff 0.06 / 0.15 / 0.25 / 0.37, tau0 0.05 N.m (red team G6, `pipeline/redteam/rt_wedge.py`); and the brief's constant 0.05 / 0.2 / 0.5 N.m per joint | |
| friction solver | MuJoCo `frictionloss` with `noslip_iterations` 20 and stiff `solreffriction` / `solimpfriction` (exact Coulomb, see 3.1) | |
| load-dependent update | after every step, `mj_rnePostConstraint`; each hinge's reaction wrench from `cfrc_int` (parent on child, referenced at the tree's `subtree_com`, checked against a static hand calculation); its moment about the bearing centre (the hub stack's mid-height on the axis: J1 52.5, J2 69.9, J3 97.7 mm for the 3R), the part perpendicular to the axis is M_perp; `dof_frictionloss` = tau0 + mu_eff M_perp for the next step. Plain bearings also run with the moment about GH (rt_wedge.py's model, no R x F term) | |
| contact | hub discs as cylinders (hub radius 11.5 mm, the axial extent of the mesh within it), ribbons as capsule chains along the member's great circle with the mesh's real radial height and thickness per 5 mm station and rows across the width; mu 0.2, margin 0 (force only on penetration), a 2 mm inactive band for near misses. Members that are not adjacent collide automatically. Adjacent members (they share a joint, so their relative pose is that joint's angle alone) collide through an explicit pair list: every primitive pair that comes within 2 mm somewhere in a full 360 deg sweep of the shared joint, minus the designed bearing (hub on hub, hub on the other member's hub-side ribbon root: the hinge itself), minus the pairs that already interpenetrate on that clip's planned path. Those are reported as **planned overlap** (the L1 geometry or the primitives overlap by design there; R6 judges the real geometry), so "contact" below means touching **beyond** what the plan already has | the reference design's short link 1 made the plain approach fail: its fat near-hub capsules overlapped its neighbours by 3.6 mm in the planned start pose, where R6 (exact) finds <= 0.8 mm |
| integration | 0.2 ms, implicitfast, Newton; recorded at 1 kHz; 0.5 s settle at the first pose (excluded from the metrics) | |
| speeds | each clip at its real speed (30 fps) and at 2x | |

**Rolling-bearing numbers.** A joint on a pair of small shielded bearings (bore d ~ 10 mm, spacing L ~ 5 mm) carries
its tilt couple M_perp as a force couple M_perp / L. With the SKF simplified friction moment M_f = 0.5 mu P d per bearing
(mu ~ 0.0015 deep-groove ball, ~ 0.0025 needle roller), the pair gives M_f = mu d M_perp / L, i.e. mu_eff = 0.003-0.005;
the lead's 0.002-0.005. tau0 = 0.001 N.m is the grease drag of two shielded bearings at these speeds; sealed bearings
(contact seals, ~ 2-5 N.mm each) are a sensitivity case. The radial force through the bearing adds mu F d / 2
~ 4e-5 N.m at 5 N, negligible.

**Plain-bearing numbers.** The v4 joint (docs/HARDWARE.md): iglidur GSM-1012-04 sleeve on a 10 mm Ti pin, two
GTM-1018-005 thrust washers (10 x 18 x 0.5, mean friction radius 7.2 mm), ring-nut preload. tau = mu (F_axial r_washer +
F_radial r_pin) gives 0.02-0.07 N.m for a 20-40 N preload at mu 0.15-0.25 (the "0.05" case). Under load, the tilt couple
dominates: tau ~ mu_eff M_perp with mu_eff ~ mu (0.06-0.18) while the washers carry it and ~ 2 mu r_pin / L_sleeve = 0.37
once wear lets the 4 mm sleeve carry it (rt_wedge.py). The constant 0.2 and 0.5 N.m stand for ~ 1-3 N.m of tilt load.

## 3. Measurement validity

### 3.1 Two MuJoCo defaults that would have given wrong answers

- **frictionloss is soft by default.** Driven at 0.01 rad/s through a stiff spring, a hinge with frictionloss 0.2 N.m
  resists with 0.0019 N.m under the default solver settings (0.19 N.m at 1 rad/s): the default friction constraint
  behaves like a viscous damper at low speed, i.e. exactly where a joint sticks. With `noslip_iterations` and stiff
  friction impedance it is exact Coulomb at every speed, including no creep below breakaway
  (`judge/test_dynamics.py` 1a, 1c). Any MuJoCo friction study on this project must use `option_xml()`.
- **contact margins add, and margin is an activation distance.** Two geoms with margin 2 mm each push apart at 4 mm.
  The judge uses margin 0 and a gap band for near-miss reporting.

### 3.2 Validation

All in `judge/test_dynamics.py` (PASS, ~40 s with `--fast`) and in each design's `dynamics.json` (`validation`,
`validation_load_friction`).

| check | case | result |
|---|---|---|
| Coulomb friction, analytic | single hinge driven at 0.01 and 1 rad/s through a spring, 0.2 N.m | 0.20000 N.m at both speeds (default MuJoCo settings: 0.0019 / 0.19) |
| inertia, analytic | constant 5 rad/s^2, I_axis 4.5e-4 kg m^2 | spring torque 0.20225 = I alpha + friction 0.20225 |
| breakaway | 0.15 N.m against 0.2 N.m | moved 3e-17 rad |
| load-dependent friction, analytic | COM 40 mm along the axis: gravity tilt couple 0.196 N.m, tau0 0.02, mu 0.25 | mean spring torque over a turn 0.06905 = tau0 + mu x tilt 0.06905 |
| **chain vs transmission.py** (the brief's check) | 3R band_r14_3r_s1351_1, x0.25 speed, no gravity, cuff x20 stiffer, 0.05 N.m on every joint; \|M_GH\| / friction against transmission.py's friction amplification on its own 10 fps frames | **156 frames: median error 0.09 %, p95 0.49 %, max 0.75 %**; 0 frames with a different joint-rate sign pattern. Excluded: held frames, frames within 0.15 s of a joint-rate reversal or with a joint below 5 % of the fastest one (friction is set-valued there) |
| 4R, J1 imposed on the plan (servo as a numerical device) | band 4R / reference, same conditions; reference = the exact quasi-static moment of the three passive joints, U_p^-T sgn(qdot) | 48 frames: median 0.04 %, p95 0.14 %, max 0.54 % / 29 frames: median 0.02 %, p95 0.34 %, max 0.49 %. transmission.py's N = 4 number (least squares over all four joints, no exact equilibrium) differs from this by -49 % to +195 % (median 0.3 %): it is not a physical value for a 4R |
| **load-dependent friction vs rt_wedge.py** | 3R, x0.25, no gravity, cuff x20, tau0 0.05 N.m, tilt about GH (rt_wedge's model), mu_eff 0.005 / 0.15 / 0.25 / 0.37 | frames well clear of a lock (tan alpha* >= 1.2 mu): 452 frames, error vs the exact quasi-static solution of u_i.M = s_i (tau0 + mu \|M_perp,i\|): median 0.12 %, p95 1.1 %. Frames rt_wedge.py calls locked (tan alpha* <= mu): 137, the dynamics needs a median **89x** the frame's constant-friction moment to drag the chain (a few already-dragged frames lower). Lock onset: 8 of 10 clip / mu cases within 0.2 s (Wash at 0.25: rt_wedge's first locked frame 48, the dynamics passes 10x at 42 as the moment diverges approaching it; Walking arm swing at 0.25 approaches but never reaches lock and passes 10x anyway; Reach a high shelf at 0.37: 30 vs 39) |
| kinematics | this judge's chain (from design.json) vs every frame's G in clips.json | <= 0.016 deg (band designs), 0.024 deg (reference) |
| contact reference point | `cfrc_int` vs a static hinge by hand | equal to 4 digits once referenced at `subtree_com[root]` |

## 4. Proposed thresholds

| criterion | threshold | why |
|---|---|---|
| moves freely (not felt) | interaction moment about GH <= 1.0 N.m peak and <= 0.5 N.m RMS; cuff force <= 5 N; cuff twist about the humerus <= 5 deg; no stall that misses >= 10 deg of planned joint travel; 4R spare within 5 deg of the planned path | the arm's own gravity moment at 90 deg elevation is ~ 10 N.m (arm 4.9 % of body mass, de Leva 1996; 70 kg, elbow straight); force and weight discrimination has a Weber fraction of ~ 7-10 % (Jones 1986), so <= 1 N.m is about one JND of the arm's own load at shoulder height (more noticeable lower down, where gravity is smaller - a proposal to be checked on the wearer). 5 N at the 200 mm cuff is the same 1 N.m. 5 deg twist: the red team's R19(c) axial-lag limit; beyond it the parts are no longer where R1 / R2 / R6 put them. 5 deg spare drift: the geometric judges assume the planned path |
| drives at all (no lock) | never > 10 N.m about GH, never > 150 N at the cuff | 10 N.m doubles the shoulder's work at horizontal; 150 N = ISO/TS 15066 quasi-static limit for the upper arm (onset of pain under clamping; collision standard, not a comfort value) |
| all-day wear | mean pressure on the cuff's 68 cm2 skin side <= 14 kPa including the strap preload (~ 6.5 kPa to get Schiebl's stiffness), i.e. <= 7.5 kPa (51 N) from the exo | the lead / user's sustained budget; Langlois et al. find 50-80 mmHg (6.7-10.7 kPa) the best stiffness / comfort trade-off; Van Vlerken et al. control straps within a 15 kPa comfort threshold. ISO/TS 15066's 190 / 220 N/cm2 (deltoid / humerus, pain onset, 1 cm2 probe) are not wear values |

## 5. Limits

- **One cuff.** The interface is the upper-arm cuff alone. The user's forearm cuff, behind the elbow hinge, also resists
  humeral rotation when the elbow is bent (x10 torsional stiffness cuts the twist from 17 to 1.9 deg at 0.2 N.m) and
  shares the bending load; upper-cuff forces are therefore upper bounds, the moment about GH is unchanged.
- **Linear tissue.** Schiebl's medians, linearised; the real curves stiffen (exponential), so small loads see a softer
  cuff (more twist) than modelled. Damping is assumed. The interface is the same for every design.
- **No skin.** The chain can pass through the body; a 4R that has folded under gravity would in reality rest on the
  skin (R2 is not re-run on the dynamic path; that is the red team's R19 "loaded fit").
- **L1 masses.** The band designs' proxies have no bearing hardware; two 10 mm deep-groove bearings per joint add
  ~ 8-12 g and ~ 5e-5 kg m^2 per joint about GH (the 3R's links are 1.5e-4 / 4.5e-4 kg m^2), not enough to change the
  verdict. Whether such bearings fit the 23 x 10.5 mm hub (docs/HARDWARE.md) is a CAD question this judge does not ask.
- **Primitive contact.** Cylinders and capsules from the L1 meshes; they overlap their neighbours near the joints by up
  to 4 mm where the exact geometry (R6) has <= 0.8 mm (reference). Those pairs are reported as planned overlap and taken
  out of the dynamic contact; a drifting 4R could reach them at other angles. Impact forces depend on the soft contact
  (solref 4 ms).
- **Girdle and base.** The base follows the rig's scapula law (2-3x less girdle motion than the literature,
  docs/research/gh_translation_literature.md) rigidly; base slip on the skin is R10's question.
- **Clips.** Eight synthetic clips at 1x and 2x, the followed motion `p` (held frames hold the arm); real motion is
  faster and more varied (G9). The 4R results start from the planned configuration of frame 0.
- **Friction law.** Single Coulomb coefficient (no stiction peak, no Stribeck); the plain-bearing tau0 (0.05 N.m) and
  the rolling tau0 (0.001 N.m) are estimates, the latter checked at 0.005 (0.07 N.m).

## 6. How to run

```bash
python3 judge/dynamics.py <design id>                    # full sweep + both validations, ~5-8 min on 4 cores
python3 judge/dynamics.py <design id> --quick            # nominal rolling-bearing case only (~30 s)
python3 judge/dynamics.py <design id> --friction 0.2 --speed 1 --mu_roll '' --mu_eff ''   # one constant-friction case
python3 judge/test_dynamics.py [--fast]                  # analytic hinge + both validations
```

## References

- Schiebl J, Elsner N, Birchinger P, Aschenbrenner J, Maufroy C, Tröster M, Schneider U, Bauernhansl T. Quantification
  of the mechanical properties in the human-exoskeleton upper arm interface during overhead work postures in healthy
  young adults. Sensors 2025;25(15):4605. doi:10.3390/s25154605 (PMC12349243): translational 2.1 N/mm (along the arm) to
  4.5 N/mm (across), rotational 0.18-0.22 N.m/deg across and 0.03 N.m/deg about the long axis, medians of 21 subjects,
  9 cm braces at 65 mbar; damping reported negligible at their test speeds; exponential (stiffening) curves.
- Langlois K et al. (VUB). Investigating the effects of strapping pressure on human-robot interface dynamics using a
  soft robotic cuff (researchportal.be/en/node/6261269): connection stiffness 1139 N/m at 0 mmHg to 2232 N/m at 100 mmHg,
  optimum 50-80 mmHg for stiffness vs comfort. (Journal not re-checked here.)
- Van Vlerken et al. Active physical interface with soft pneumatic actuator straps (VUB): strap pressure kept within a
  15 kPa comfort threshold (as summarised in the search result; not re-read in full).
- ISO/TS 15066:2016, Annex A, Table A.2: upper arm and elbow, quasi-static force 150 N; pressure deltoid 190 N/cm2,
  humerus 220 N/cm2. The pressures were checked against the "Mainz" column in Behrens R, Elkmann N, "From head to toe -
  biomechanical thresholds to protect robot operators against injuries", Fraunhofer IFF, IROS 2019 workshop (NIST-hosted
  slides); the 150 N force value is from the standard's table and was not re-read here. The same slides give newer
  blunt-clamping pain onsets of 70 N (deltoid) and 110 N (humerus) (preliminary).
- Jones LA. Perception of force and weight: theory and research. Psychol Bull 1986;100(1):29-42 (force / weight JND
  ~ 7-10 %).
- de Leva P. Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters. J Biomech 1996;29(9):1223-1230 (upper
  arm 2.71 %, forearm 1.62 %, hand 0.61 % of body mass).
- SKF rolling bearings catalogue, frictional moment, simplified model M = 0.5 mu P d (mu 0.0015 deep-groove ball,
  0.0025 needle roller).
- In this repo: `pipeline/conformal/analysis/transmission.py` (quasi-static friction amplification),
  `pipeline/redteam/rt_wedge.py` and `docs/research/sim_to_real_gaps.md` G4 / G6 (load-dependent friction, cuff torsion).

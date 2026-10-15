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

RESULTS_PLACEHOLDER

## 2. Model

| element | how | source / assumption |
|---|---|---|
| frame | body-rig thorax frame, x anterior, y up, z right, origin = right GH centre; gravity -y (standing) | `pipeline/avg/body_pose.py` |
| scapula + base | base body on a ball joint at GH, driven along the rig's scapula law `scap(elev)` by feed-forward + PD on a 1000 kg m^2 armature: the chain sees the base's real angular velocity and acceleration, the base does not feel the chain. The base part is rigid on it (the user's scapula handler is separate). The law's 20 deg kink (`max(0, elev - 20)`) is rounded over 1.5 deg (softplus); otherwise the base would get an angular-velocity step | `body_pose.scap` |
| links | serial hinges J1..J(N-1) with axes through GH, built from `design.json` exactly as `band_impl.chain()` (b = bvec(az, el), arcs a, closure branch); body frames = the exo.glb group frames | max 0.016 deg from every frame's G in clips.json (all three designs) |
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

VALIDATION_PLACEHOLDER

## 4. Proposed thresholds

| criterion | threshold | why |
|---|---|---|
| moves freely (not felt) | interaction moment about GH <= 1.0 N.m peak and <= 0.5 N.m RMS; cuff force <= 5 N; cuff twist about the humerus <= 5 deg; no stall that misses >= 10 deg of planned joint travel; 4R spare within 5 deg of the planned path | the arm's own gravity moment at 90 deg elevation is ~ 10 N.m (arm 4.9 % of body mass, de Leva 1996; 70 kg, elbow straight); force and weight discrimination has a Weber fraction of ~ 7-10 % (Jones 1986), so <= 1 N.m is about one JND of the arm's own load at shoulder height (more noticeable lower down, where gravity is smaller - a proposal to be checked on the wearer). 5 N at the 200 mm cuff is the same 1 N.m. 5 deg twist: the red team's R19(c) axial-lag limit; beyond it the parts are no longer where R1 / R2 / R6 put them. 5 deg spare drift: the geometric judges assume the planned path |
| drives at all (no lock) | never > 10 N.m about GH, never > 150 N at the cuff | 10 N.m doubles the shoulder's work at horizontal; 150 N = ISO/TS 15066 quasi-static limit for the upper arm (onset of pain under clamping; collision standard, not a comfort value) |
| all-day wear | mean pressure on the cuff's 68 cm2 skin side <= 14 kPa including the strap preload (~ 6.5 kPa to get Schiebl's stiffness), i.e. <= 7.5 kPa (51 N) from the exo | the lead / user's sustained budget; Langlois et al. find 50-80 mmHg (6.7-10.7 kPa) the best stiffness / comfort trade-off; Van Vlerken et al. control straps within a 15 kPa comfort threshold. ISO/TS 15066's 190 / 220 N/cm2 (deltoid / humerus, pain onset, 1 cm2 probe) are not wear values |

## 5. Limits

LIMITS_PLACEHOLDER

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

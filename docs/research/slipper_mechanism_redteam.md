# Slipper-nose drive red team + build spec: slipper-nose-knuckle-3r (gen-7 winner)

2026-10-17. Subject: the one new mechanism in generation 7. The gen-6 roller-flank drive (docs/research/roller_mechanism_redteam.md)
loses its MR63ZZ flank roller: the crank's bent long arm ends in a pressed ISO 8734 O2.5 m6 440C dowel (the nose) that SLIDES
on a conjugate flank wire-EDM'd into link 1a's Ti-6Al-4V lug, a-C:H DLC coated and greased (claim: nose_r 1.1839, mu 0.087,
PA_kin <= 43 - atan(mu)). Everything else in the train is the gen-6 drive: lobe on hub 2 -> lobe follower -> crank on link 1b
-> nose -> flank on link 1a, one clock spring in K's cap closing the whole train.

This note prices the nose with real parts and real numbers: Hertz line contact and wear over 1e6 cycles at the worst spring
load, pressure angle + friction at mu 0.087 / 0.12 / 0.15 on BOTH strokes (the alignment watch M5: does the spring still
return the crank through a sliding contact?), the conjugate pocket vs the nose, the dowel's press fit and pull-out, and what
a buildable flank tolerance does to K and to the one fold-margin metric `th`.

Scripts and outputs: `docs/research/slipper_mechanism/`.

- `extract.py` wears the VERIFIED config (rows/slipper-nose-knuckle-3r.json best_params, mu 0.087, nose_r 1.1839, knee
  stop ang_min 25.2189 as the claim ran it) through the claim's own model, loaded unchanged via the verifier harness
  (SN_CELL=lead), frozen protocol (fit Bench(60,160) fast, worn on Bench(110,360) exact / held out). It dumps the drive
  geometry, cam table, per-pose state and every part's signed skin distance (`geo_*.npz / .json`).
- `drive.py` (from the gen-6 roller script, changed for a sliding nose): cam re-synthesis on a 0.05 deg grid, the flank as
  a ruled surface + tangent-arc sketch + signed curvature, friction on both strokes, Hertz incl. the edge loading of a
  straight extrude (slicing method), Archard wear maps, the dowel fit, the real lobe follower, crank-pair statics, arm
  stiffness, per-pose fold margin under a K offset (exact re-solve on the slaved law). Run:
  `A_S=6.5 PSI=216 RR=3.0 python3 drive.py geo_bench.npz bench [geo_held.npz]` (env `NR=1.25` re-cuts for the stock O2.5).

**Reproduced (bench):** frozen exact Bench(110,360) **18.49** (reach 0.725, ib14 0.8955, contact 0.0054; near-touch 1 mm
20.12, 2 mm 33.02, min metal 0.07 mm), th margin min **5.181** (forced pose plane 60 / elev 120 / axial -105), N2 undercut 0 of
913 steps, the re-synthesised cam = the model's horn pressure angle to 0.000 deg. **Held out: 23.45** (reach 0.6828, ib14
0.8943, contact 0.0116; 1 / 2 mm 26.54 / 36.95; min metal 0.33 mm), th margin min **5.006** (forced pose plane 135 /
elev 30 / axial -135), taken dK max 46.27, horn PA + friction 41.07, N2 undercut 0 of 926 steps. Both reproduce the
verifier's JSON to the digit.

## Verdict

**Buildable at this size for MVP1. Nothing in the nose is unbuildable.** The nose is lightly loaded (5-9 N), the flank is
concave everywhere (a conformal pocket at rest), and the friction risk M5 raised is retired quasi-statically: at mu 0.15
the spring still returns 92 % of its work to the crank, ~90x the crank's drag. Three things must change from what the
gen-6 CAD did or the model assumed, each cheap:

1. **The flank must be cut as its exact ruled surface (4-axis UV wire EDM), NOT as a straight 2-axis extrude.** A straight
   extrude (the gen-6 roller CAD's method) leaves the nose's line ends 22 um off the flank. A line contact whose elastic
   approach is 0.18 um then carries the whole load on one end: p0 1144 MPa on 0.26 mm of line, past the a-C:H-on-Ti
   eggshell limit (~1.0 GPa) and near Ti-6Al-4V's line-contact yield onset (1383 MPa). Aligned, the same load gives
   **236-282 MPa**. Combined tilt between nose axis and flank rulings must stay <= ~5 um over the 2.2 mm line (0.13 deg):
   p0 <= 800 MPa.
2. **A K lead of +0.75 deg must be built in** (lobe-ring dowel phase +0.35 deg of q2 early), because the held-out fold
   margin is 5.006: a K lag of only 0.07 deg puts a held-out pose under 5, and the drive's systematic lag is 0.42-0.53 deg
   with +-0.24 deg random. The +-0.02 mm flank tolerance alone is +-0.08 deg of K.
3. **Coat the nose too** (same a-C:H batch) and grease at assembly. Uncoated 440C against DLC is the wearing member: 26 um at
   one spot of the nose after 1e6 dry cycles (2.6 um greased), because the contact dwells at a turning point on the nose.
   The flank's 2-3 um DLC survives 1e6 cycles in every case but "grease lost + abrasive".

Plus two carried from gen 6, with new numbers: the crank pair needs **2 x 683ZZ straddling the follower** (O10 x 10 boss,
static factor 3.07 at MVP1 with friction; the side-by-side O10 x 6 layout drops to 1.31-2.02), and the modelled lobe follower
(s_arm 4.0 on r 8.27) lies inside hub 2's O20, so the real follower is **an MR63ZZ on a 6.5 mm short arm at psi 216**, lobe
r 10.79 -> 12.77, PA <= 16.2 deg.

| # | Finding (measured) | Fix (cheapest first) |
|---|---|---|
| 1 | **Contact stress is low when aligned.** MVP1 load (0.113 N.m + 0.015 N.m/rad at K) on the outward stroke: Fn **7.4-8.5 N** at mu 0.087 (8.97 at mu 0.15); spring alone 5.3-6.3 N. 440C (E 200) on DLC-on-Ti (substrate E 114), line 2.2 mm (the 2.5 mm band minus the dowel's end form): **p0 275 MPa** worst (mu 0.087), 282 at mu 0.15; half-width 9-32 um, so the max shear (0.786 b = 7-25 um deep) sits in the Ti, under the 2-3 um coating: tau_max 83 MPa against Ti's 415. Fatigue: sigma_vm ~0.557 p0 x 1.2 (sliding) = 184 MPa, far under Ti-6Al-4V's ~500 MPa endurance: infinite-life class. | Nothing at the contact itself; see 2 for the alignment it needs. |
| 2 | **A straight extrude edge-loads the nose.** Rulings converge on GH, wire taper 0.14-2.74 deg over the stroke; a straight extrude along z_c leaves the nose line ends -22.3 / +19.9 um off. Slicing the 2.2 mm line (0.01 mm slices, 2D approach per slice): mismatch 2 / 5 / 10 / 20 um gives p0 626 / 796 / 955 / 1144 MPa on 0.89 / 0.55 / 0.38 / 0.26 mm of contact. | **Cut the exact ruled flank: 4-axis (XY-UV) wire EDM** with the top and bottom contours in `flank_bench.csv` (+-1.5 mm about the mid plane along z_c), skim pass. Specify a **parallelism of the flank rulings to the nose axis <= 5 um over the line** (hole perpendicularity in the arm 0.05 deg, taper accuracy, hub tilt). The CAD keeps the straight constant-section extrude as its geometry (no-loft rule) and puts the true ruled surface on the drawing. Fallback if 4-axis wire is not available: a duplex substrate (plasma-nitrided Ti + CrN interlayer + a-C:H) lifts the allowable to ~1.5 GPa. |
| 3 | **The flank is concave toward the nose over 100 % of the stroke; never convex** (the auditor's open sign question). Radius: **1.27 mm pocket at dK 0.1** (the verifier read 1.285 at 0.5 on its grid), 1.47 at 2.5, 2.9 at 10, 5.3 at 20, 8.9 at 35, 11.2 at 45. Pocket clearance to the nose 0.083 mm. No undercut (N2: 0 of 913 steps). The hand calculation's "3.5 mm convex" was wrong in the safe direction: equivalent radius 1.32 mm (end of stroke) to 18 mm (pocket). | None. Any wire (O0.1-0.25) makes R >= 1.27 concave. Tolerances eat the pocket clearance from one side only: a flank cut 0.02 fat and an m6 nose at +4 um on the radius leave **0.059 mm**, still > 0, so the nose never wedges in the pocket; the dry-wear flat (26 um) does not reach it either. |
| 4 | **Friction on both strokes (M5).** Kinematic horn PA 35.74 (bench taken) / 36.05 (held taken), crank 29.5 at rest, 5.9 at the end. With friction (horn, the binding side): **40.71 / 42.58 / 44.27 deg** at mu 0.087 / 0.12 / 0.15 (held taken: 41.02 / 42.89 / 44.58). Margin to the 43 design rule: 2.29 / 0.42 / -1.27; to the 45 gate: 4.29 / 2.42 / 0.73. The 43 rule is reached at **mu 0.127** (held 0.122). **True lock-up (PA + friction angle = 90) needs mu 1.39**: there is no jam at any real friction. Efficiency: outward 0.91-0.99, **return 0.92-0.99** (mu 0.15 worst). | Nothing to change at mu <= 0.12. At mu 0.15 the 43 rule is broken by 1.3 deg (the 45 gate is not): that is the "grease lost" case, so the grease is a maintenance item (finding 6). |
| 5 | **The spring returns the crank with a wide margin.** On the return stroke the spring delivers 189-209 N.mm to the crank (spring alone) and 111-134 N.mm against the MVP1 opening load, against a pessimistic crank drag of 1.2 N.mm (2 x 683ZZ greased + follower): **factor 92-158** at every mu. The friction lowers the q2 acceleration the spring can follow from 43.7 (roller) to **42.9-43.2 rad/s2** (MVP1, gen-5 inertia 5e-4 kg m2). J2 torque the wearer feels: outward 0.174-0.209 N.m (spring) / 0.245-0.284 (MVP1); return 0.171-0.188 / 0.241-0.256; **friction hysteresis <= 0.020 N.m** at mu 0.087, 0.036 at 0.15 (spring); 0.028 / 0.048 with MVP1. | None for MVP1. R17 (dynamics, return stroke, mu 0.087 / 0.12 / 0.15) still runs on the CAD, as M5 asks: this note is quasi-static. |
| 6 | **Wear over 1e6 full-stroke cycles (2 passes each, MVP1 load).** Sliding 4.23 mm per stroke; the contact travels 4.96 mm on the flank and 35.4 deg (0.73 mm) round the nose, with a turning point where it dwells. Archard per surface point: | **DLC-coat the nose too** (a-C:H on the 440C dowel, same batch as the flank): the steel member stops being the soft one. Grease at assembly (a PAO grease without EP additives, e.g. Kluber Isoflex Topas NB 52) and at service. |
|   | greased (K_DLC 1e-9, K_440C 1e-8 mm3/N.m): flank 0.01 um, **nose 2.6 um**, K lag 0.011 deg; dry typical (1e-7 / 1e-7): flank 1.0 um, **nose 26 um**, K lag 0.116 deg; grease lost + abrasive (1e-6 / 1e-6): flank 10 um (**DLC worn through**), nose 265 um, K lag 1.16 deg. The flank coating (2-3 um) survives the first two. | |
| 7 | **The dowel.** ISO 8734 2.5 m6 x 6 pressed 3 mm (the arm's thickness) into an O6 tip boss: flush on the arm's outer face, its end reaches 59.96 mm from GH, 0.10 mm past the modelled end disc and 0.15 mm above the lug's skin-side face (59.81). **H7/m6 is a transition fit** (-8 / +8 um): 0 N pull-out at its loose end. P7 / N7 give 6-24 um but up to 716 MPa hoop in the 1.75 mm Ti wall (yield 830). Nose root bending 12 MPa, deflection 0.07 um, axial load <= 0.45 N (a 3 deg tilt of an 8.5 N force). | **Ream the tip hole 2.495-2.500 (2-13 um interference): hoop <= 388 MPa (factor 2.1), pull-out 119-772 N**, plus Loctite 648 (about 350 N on its own) so the loose end of the band still holds; press with anti-seize, chamfered hole, slow. Pull-out need <= 0.45 N axial: factor > 250. |
| 8 | **Play stack (systematic lag, all one-sided under the spring):** arm compliance -0.223 deg (0.053 mm along the normal, MVP1; 6 x 3 Ti, 58.8 mm polyline); follower MR63ZZ radial clearance up to -0.19 (10 um x 0.187-0.252 deg / 10 um); wear -0.011 (greased) to -0.116 (dry). Sum **-0.42 to -0.53 deg**. Random: flank profile +-20 um = **+-0.084 deg** (0.037-0.042 deg per 10 um, m_horn 13.65-15.69 mm); nose hole position +-10 um = +-0.042; lobe form, follower-pin and PV positions at +-5 um = +-0.125 each; RSS **+-0.24 deg** (+-0.44 at +-10 um on the lobe side). Nose m6 diameter (+1..+4 um on the radius) = +0.004..+0.017 (a lead). | **Pre-set a +0.75 deg K lead**: advance the lobe ring's dowel phase by **+0.35 deg of q2** (0.75 / kK 2.1534). Hold the crank's three bores (PV, follower pin, nose) and the lobe profile to **+-5 um** (one wire-EDM / jig-grind setup each). Preload the crank pair. |
| 9 | **Fold margin (the one th metric, per taken pose, exact re-solve on the slaved law).** Bench: lag -0.7 / -0.5 / -0.3 / -0.1 deg -> 5.122 / 5.138 / 5.158 / 5.174; lead +0.25 / +0.5 / +0.75 / +1.0 -> 5.203 / 5.222 / 5.246 / 5.265 (slope 0.084 deg of margin per deg of K; 0 poses under 5 on the bench at any offset). **Held out** (852 taken, 400 forced): lag -0.05 / -0.1 / -0.3 / -0.5 / -0.7 -> 5.001 / **4.998 (1 pose under 5)** / 4.982 / 4.966 / 4.950 (2 poses); lead +0.25 / +0.5 / +0.75 / +1.0 -> 5.026 / 5.049 / 5.068 / 5.087 (slope ~0.08). The re-solve reads 5.008 at zero offset (verifier 5.006). **A K lag of 0.07-0.1 deg puts a held-out pose under 5.** | The +0.75 deg lead of finding 8 puts the worst lag build (systematic -0.53, random -0.24) at about -0.02 deg: held out >= 5.003 (0 poses under 5), bench >= 5.18; the nominal build sits at +0.2-0.5 deg (held out 5.025-5.049, bench 5.20-5.22). Without the lead the worst build (-0.77 deg) reads ~4.95 held out, 2 poses under 5. Cost at the worst LEAD build (new, spring-only arm lag -0.16, follower clearance 5 um, random +0.24: +0.74 deg): horn PA +0.39 deg -> 41.1 bench / 41.4 held at mu 0.087, 43.3 held at mu 0.12 (over the 43 rule by 0.3, under the 45 gate); taken dK 46.9 < dK_lim 49.75. |

**MVP2.** As for the roller and the sidecar: a powered K load through this train multiplies by g = 2.39 at the crank; the
follower and the crank pair would see kN. Not an MVP1 issue, and not modelled (CLAUDE.md: kinematic proof only).

## 1. Geometry for the CAD (`spec_points_bench.json`; frame = link 1b at q = 0 with K on stop A = link 1a at K 0; mm from GH)

**Axes and levels**
- Crank axis dR: 14.78 deg from u2, 23.26 deg from uK; uK is 38.03 deg from u2. All axes pass through GH.
- Crank pivot PV on dR at 62.82 mm (boss underside). Member levels f = 50.45 / 62.04 / 78.21, fK = 55.12.

**Law and crank motion**
- dK = 2.1534 (q2_onset - q2), q2_onset 7.279 deg; the drive range ends at dK_lim 49.75 (horn PA cap) at q2 -15.82; the
  crank turns phi = |dK| / 2.3934 (20.79 deg at dK_lim), sense sig as in `spec_points`. Taken max dK 45.62 bench / 46.17
  held (K's dyad window a1max binds first, not the drive). `slaved_law_bench.json` is the build.json `slaved` table
  (closure "force", drive group crank on l1b).

**Nose (the dowel)**
- Nose centre at rest `nose_centre_rest` (61.31 mm from GH), axis radial through GH (`nose_axis_rest`).
- Radial levels from GH along the nose axis: lug shell **59.81-62.81** (3 mm), running gap 0.15, arm **62.96-65.96**
  (3 mm), nose end disc (model) 60.06. An O2.5 x 6 dowel flush with the arm's outer face ends at 59.96.
- Nose radius for the flank: the claim's 1.1839 (`NR` default). **Build with the stock O2.5 (r 1.25)** and the flank re-cut
  for it (`NR=1.25`; the verifier measured 18.49 for that column, identical to the claim): pocket radius 1.333 mm,
  clearance 0.083, p0 267 MPa aligned, horn PA + friction 42.74 at mu 0.12 (vs 42.58). The arcs below are for r 1.1839;
  rerun `NR=1.25 ... drive.py` for the O2.5 export (same command, same frame).

**Flank (link 1a lug, Ti-6Al-4V, a-C:H DLC)**
- Ruled surface: rulings parallel to the nose axis (radial lines through GH) offset by the nose radius; wire taper
  0.14-2.74 deg along the stroke. Built from dK 0 to **51.75** (dK_lim + 2 deg run-out; horn PA 38.9 kinematic there,
  43.9 with friction, < 45). Length 6.03 mm. Contact radius from uK 14.88-20.03 mm.
- Sketch frame `flank_sketch_frame` (origin GH, ez = z_c the mean ruling = the straight-extrude direction), mid plane at
  61.287 along z_c.
- Mid-plane section, 4 tangent arcs within 3 um (`results_bench.json flank_arcs`, (ex, ey) in mm):
  **R 1.625** (dK 0-8.55, the rest pocket), **R 4.372** (8.55-24.35), **R 8.553** (24.35-42.8), **R 11.762** (42.8-51.75).
- `flank_bench.csv` per 0.25 deg of K: mid / top / bottom sections (+-1.5 mm along z_c = the two UV wire contours), nose
  centre, contact point and normal (link 1a frame), both pressure angles.

**Lobe follower (real, not the model's)**
- MR63ZZ on an O3 pin at a_s **6.5 mm, psi 216 deg**, centre `follower_centre_onset`, axis dR (s 70.48 along dR).
- Lobe ring profile (normal offset, `lobe_polar_bench.csv`): r **10.79 -> 12.77** over 23.10 deg of q2 past the onset; PA
  10.8-16.2 deg; pitch curvature >= 13.25; drift along u2 0.43 mm; dwell O20.7 (10.35 + 0.1 running gap).
- Options (`results_bench.json follower_options`): 7.0 / 219 gives r 12.76, PA 18.7; 8.0 / 222 gives r 13.05 (too high: the
  gen-5 ring entered the skin at r 12.87).

## 2. Parts list (real parts, real size)

| part | spec | qty | play / rating |
|---|---|---|---|
| **nose** | **ISO 8734 - 2.5 m6 x 6, type C** (martensitic stainless 1.4125 = X105CrMo17, the 440C grade; order with a hardness cert >= 52 HRC), a-C:H DLC coated with the flank batch. Rounded end at the nose tip (ISO 8734 / DIN 6325 pins have one radiused, one chamfered end: confirm on the supplier sheet). Pressed 3 mm into the arm tip, flush on the outer face. | 1 | d 2.502-2.508; reamed hole 2.495-2.500 (+ Loctite 648); Fn <= 9 N, p0 <= 282 MPa aligned |
| flank | cut in link 1a's lug (Ti-6Al-4V, the 5-axis spherical-shell lug): exact ruled surface, **4-axis UV wire EDM**, skim cut, profile +-0.02 (target +-0.01), ruling parallelism to the nose axis <= 5 um over 2.2 mm; **a-C:H DLC 2-3 um on a Cr / Si adhesion interlayer** (coating at < 250 deg C), greased | (in link 1a) | +-20 um = +-0.084 deg of K |
| crank pair | **2 x 683ZZ (3 x 7 x 3), straddling the follower, boss O10 x 10**, light axial preload (wave washer for O7, 5-10 N) | 2 | worst 39.1 N (MVP1, mu 0.087) / C0r ~120 N (to confirm): factor **3.07**; side-by-side O10 x 6: 91.3 N, factor 1.31 (with a_s 6.5) |
| pivot pin | O3 h5 17-4PH H900, pressed into link 1b, DIN 6799 RS 2.3 clip | 1 | |
| crank | Ti-6Al-4V, **5-axis machined from solid** (the arm's arc and its joggle are R < 15 mm): boss O10 x 10, bent arm 6 x 3 on `arm_polyline` (58.8 mm), O6 tip boss with the reamed O2.5 nose hole, follower lug carrying the O3 follower pin at a_s 6.5. All three bores in one setup, +-5 um | 1 | arm root 34 MPa, arm 0.053 mm along the normal at 8.5 N = K lag 0.223 deg |
| lobe follower | **MR63ZZ** (3 x 6 x 2.5) on an O3 h5 pin pressed into the crank's short arm | 1 | 43.7-49.9 N (MVP1) vs C0r ~73 N: factor 1.46; MC3 clearance -0.19 deg of K |
| lobe ring | 17-4PH H900, wire-EDM, 3 mm band at f2 + 6.2..9.2, profile r 10.79 -> 12.77, dwell elsewhere; on hub 2's turned ring, keyed by an O1 dowel **at the onset phase + 0.35 deg** (the K lead) | 1 | Hertz 582 MPa (MVP1) |
| K closing spring | the gen-6 spiral spring, unchanged: 1.4310 strip 0.3 x 5 x 144.7 mm (0.015 N.m/rad), pre-wound 306 deg for **0.080 N.m on stop A**, 0.092 at stop B; peak 1229 MPa (the lower-stress 0.35 x 5 x 230 mm, 901 MPa, is the better build). Custom from catalogue strip. | 1 | the only preload in the train |
| knee | the two-pin cuff knee, unsensed, **MR63ZZ ball-bearing pairs** per pin (CLAUDE.md 5), physical knee stop at **[25.22, 154.78] deg** (the claim's ang_min 25.2189; taken max 151.92 bench / 153.16 held) | 2 pins | as the lead |
| grease | PAO-based, no EP additives (Kluber Isoflex Topas NB 52 class) on the nose / flank | - | |

## 3. What keeps contact

- **One spring, in series, closes the nose and the follower.** K's spring presses the flank on the nose with 5.3-6.3 N
  (8.5 N with the MVP1 opening load added); the crank torque that results (190-232 N.mm, 273-315 with MVP1) always has the
  same sign and presses the follower on the lobe with 35-50 N. A pair lifts off only if K's own load beats its spring:
  static factor 0.080 / 0.033 = **2.4-2.8** (the gen-5 MVP1 bound), as for the roller.
- **Friction does not change that, and does not jam.** The return-stroke efficiency is 0.92-0.99 at mu up to 0.15; true
  lock-up needs mu 1.39. The spring has 90-160 x the crank's drag left on the return stroke.
- **At rest the crank floats.** Before the onset K sits on stop A, so the spring's torque goes into the stop, not the nose; the
  crank is held only between the flank pocket (0.083 mm clearance) and the follower's 0.1 mm dwell gap: about +-0.9 deg of
  crank, K unaffected. The crank pair's preload drag keeps it from rattling; the onset pickup is a 0.1 mm tap, as gen 6.
- **Dynamic.** The q2 acceleration the spring can follow without the follower leaving the lobe: 43.2 rad/s2 at mu 0.087,
  42.9 at 0.15 (MVP1; gen-5 inertia). A throw exceeds it; everyday motion does not. R17 on the CAD replaces both the load
  and the inertia estimate.

## 4. Play stack, the cuff and the 5-deg fold margin

| source | K error | sign |
|---|---|---|
| arm compliance (MVP1, 8.5 N) | -0.223 deg (spring only: about -0.16) | lag, systematic |
| follower MR63ZZ clearance (MC3, <= 10 um) | up to -0.19 to -0.25 deg | lag, systematic |
| nose + flank wear, 1e6 cycles | -0.011 (greased) / -0.116 (dry) deg | lag, grows with life |
| crank pair | 0 when preloaded (0.45 deg per 10 um if not) | |
| flank profile +-20 um (wire EDM) | **+-0.084 deg** | random |
| nose hole position +-10 um | +-0.042 deg | random |
| lobe form / follower pin / PV position, +-5 um each | +-0.125 deg each | random |
| nose diameter m6 (+1..+4 um radius) | +0.004..+0.017 deg | lead |

Systematic lag **-0.42 to -0.53 deg**; random RSS **+-0.24 deg** (+-0.44 if the lobe-side features are only +-10 um).

**The cuff does not feel this as strain.** K is slaved and never read; the three hub encoders and the law give the pose, so a
K error is a tracked-humerus error about uK (about 0.2 deg after the lead, 0.8 deg without it) that the cuff knee absorbs.

**Fold margin.** The flank's own +-0.02 mm moves the margin by +-0.007 deg: bench 5.181 -> 5.174 at worst, held out 5.006 ->
4.999. Everything else in the stack is bigger, so the K lead is what keeps th >= 5 (finding 9).

| K offset (deg) | -0.7 | -0.5 | -0.3 | -0.1 | -0.05 | 0 | +0.25 | +0.5 | +0.75 | +1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| bench min th margin (371 taken) | 5.122 | 5.138 | 5.158 | 5.174 | 5.177 | 5.180 | 5.203 | 5.222 | 5.246 | 5.265 |
| held-out min (852 taken) | 4.950 (2) | 4.966 (2) | 4.982 (1) | 4.998 (1) | 5.001 | 5.008 | 5.026 | 5.049 | 5.068 | 5.087 |

(poses under 5 in brackets; per taken pose, exact re-solve of q2 on the slaved law at the pose's own th; rest poses keep
K on stop A and do not move.)

## 5. Skin (signed distance on the bench's exact skin, taken poses)

| part | min distance | where (plane, elev, axial) |
|---|---|---|
| nose (sampled as the old "roller" member) | **6.76 mm** | 15, 135, -60 |
| crank arm | 1.99 mm | 60, 15, -120 |
| horn lug | 2.48 mm | 15, 135, -60 |
| crank boss | 2.49 mm | -60, 60, 105 |
| hub K | 2.44 mm | 15, 75, 75 |

All drive parts pass the 0.3 mm rule by >= 1.7 mm on taken poses. The 2 bench contact poses are the lead family's own, lost
and scored as contact: (15, 165, -60) crank -8.50, horn -7.07, **nose -4.16**, hub K -2.65 mm; (30, 165, -60) crank -0.26,
horn -5.34 mm. The nose is in the first one (the roller was -5.29 there). Unsampled by the model: the real lobe ring (r up to
12.77) and the follower plate, and the 10 mm straddle boss (+4 mm along dR over the 6 mm one) - the CAD sweep decides them.

**Held out (852 taken):** nose >= **6.11 mm**, crank 1.84, horn 2.60, boss 2.74, hub K 0.89 (one pose under 1 mm: plane 45 /
elev 90 / axial 45). Of the 10 held-out contact poses the nose is in 2: (15, 150, -60) nose -0.48 with horn -7.07 / crank
-1.32, and (30, 165, -45) nose -3.86 with crank -7.98 / horn -6.62 / hub K -1.34. The other drive presses are horn and
crank at elevation 150-165 (the T5 watch's depth); 3 contact poses have no rigid drive sample under 0 (link metal).

## 6. Build spec for the CAD agent (pipeline/concept_l1/build_slipper_l1.py, user_style_slipper.py)

1. **Config.** The verified best_params (rows/slipper-nose-knuckle-3r.json, mu 0.087, ang_min 25.2189). Nose: stock O2.5
   (r 1.25) with the flank re-cut for it (`NR=1.25 A_S=6.5 PSI=216 RR=3.0 python3 docs/research/slipper_mechanism/drive.py
   geo_bench.npz bench_r125`), or the claim's r 1.1839 exports as they are; state which.
2. **Nose.** ISO 8734 2.5 m6 x 6 type C, DLC, pressed 3 mm into an O6 tip boss of the crank arm, flush with the arm's outer
   face, axis radial through GH at `nose_centre_rest`. No head, no retaining part. Drawing note: "reamed O2.495-2.500
   (2-13 um interference with m6), Loctite 648, press with anti-seize".
3. **Flank.** The CAD body: the mid-plane tangent-arc section (`flank_arcs`) extruded straight along z_c through the 3 mm
   lug (allowed: one constant section). The drawing: "exact ruled surface, 4-axis UV wire EDM, contours = `flank_bench.csv`
   top / bot at +-1.5 mm, profile +-0.02, ruling parallelism to the nose axis <= 0.005 over 2.2 mm, a-C:H DLC 2-3 um on an
   adhesion interlayer, grease". Built dK 0 -> 51.75.
4. **Crank.** 5-axis machined from solid; boss O10 x 10 with **2 x 683ZZ straddling the follower**, wave-washer preload; arm
   6 x 3 on `arm_polyline`; follower pin at a_s 6.5 / psi 216 carrying an MR63ZZ. All bores one setup, +-5 um.
5. **Lobe ring.** Profile `lobe_polar_bench.csv` (normal offset, r 10.79 -> 12.77) as tangent arcs, joined to the dwell with
   a concave R2.5 at the onset, extruded along dR over the 3 mm band; **phased +0.35 deg of q2 early** (K lead +0.75).
6. **Stops.** q2 dowel stop B at the drive end, q2 = -15.82 + 0.35 = **-15.47 deg** (dK_lim 49.75 with the lead); K stop A as
   modelled; knee stop at [25.22, 154.78]; each a dowel in an arc slot on the joint's own two bodies.
7. **build.json `slaved`.** `slaved_law_bench.json` (closure "force", drive group crank on l1b), shifted by the +0.35 deg
   phase; map the CAD's own frame keys.
8. **Judges.**
   - **R17 on the return stroke at mu 0.087 / 0.12 / 0.15** (alignment M5's action): report slaved.law_err_deg, lift-off at
     the follower, and the J2 hysteresis; this note predicts <= 0.05 N.m hysteresis and no lift-off below ~43 rad/s2 of q2.
   - **R16 / skin sweep** on every frame: the real lobe ring and follower plate, the O10 x 10 boss and the nose end at
     >= 0.3 mm; rerun with the +0.75 deg lead law (the lead moves link 1a by ~0.8 mm at 60 mm radius on driven poses).
   - **Carry-overs from gen 6** (this note does not close them; the CAD does): (a) the 10 body-contact poses of
     user_roller_longdyad's R16 (link 1a overhead 6.4-10.4 mm, link 2 5.9 mm) are links, not the nose; attribute them in
     the build; (b) knee MR63ZZ pairs + stop; (c) sliver_free in the shared builder; (d) the fit notes of this section and
     section 2 (nose H-band above, 683ZZ / MR63ZZ seats: housing J6, pins h5 with Loctite 641, crank pair preloaded).
   - Report, not hide: horn PA + friction 41.0 held (42.9 at mu 0.12), hub K clearance at rest 1.31 (arm) / 3.92 (nose),
     the elev-165 contact depth (nose -4.16).
9. **Render.** Skipped this run (no_render: GPU stills need the user's separate yes). When approved: the nose and flank from
   the lug side at ~45 deg; DLC flank dark grey is a coating, not a black part - render it as polished metal (no black parts).

## Red team (what could still be optimistic)

- **mu is still assumed.** 0.087 is the claim's central value; the design holds the 43 rule to mu 0.122-0.127 and never
  jams. A pin-on-flat wear test of 440C(DLC) on DLC-on-Ti at 5-9 N, greased, 1e6 strokes of 4.2 mm, is still the cheapest
  way to pin both mu and K.
- **Wear coefficients are literature ranges**, not measured on this pair: greased 1e-9 / 1e-8, dry 1e-7, pessimistic 1e-6
  mm3/N.m. The nose wear concentrates at a turning point of the contact on the nose; its depth is set by the Hertz width
  used to spread it (2b = 18-64 um).
- **Hub tilt is not in the alignment budget.** The 5 um parallelism needs the hub K and crank-pair tilt under load; the O20
  hub stacks' tilt stiffness is not on file. If they tilt more than ~0.1 deg under 8.5 N at 15 mm, edge loading returns
  (finding 2's fallback: the duplex substrate).
- **The MVP1 load (0.033 N.m) and inertia (5e-4 kg m2) are the gen-5 estimates.** R17 on the CAD replaces both.
- **Bearing ratings are from memory** (MR63ZZ C0r ~73 N, 683ZZ ~120 N): confirm on the supplier sheet.
- **The ISO 8734 type C hardness** (the standard allows a lower band than through-hardened 440C) must be ordered with a
  certificate; a softer nose wears faster than the "dry" row.
- **The +0.75 deg K lead is sized on the bench slope and the held-out minimum**; it costs 0.3 deg over the 43 rule at
  mu 0.12 held out at the worst lead build. The CAD's R16 with the shifted law must confirm the skin numbers.
- **The thinnest number is the lobe follower**: MR63ZZ at 43.7-49.9 N (MVP1) against C0r ~73 N, factor 1.46 (about 2.1
  on the spring alone). A 683ZZ (O7) follower does not fit: on every short arm tried (7.0 / 216-219, 7.5 / 219) its lobe
  dips to r 9.6-9.95, inside hub 2's housing (>= 10.1 needed). The 8.0 mm / psi 222 arm lowers the load to 35-43 N
  (factor 1.7) for a lobe at r 13.05 (skin risk). MVP1 is unpowered and the 0.033 N.m load is an estimate: R17 decides.

# Roller-flank drive red team + build spec: roller-longdyad-knuckle-3r (gen-6 winner)

2026-10-17. Subject: the drive that slaves K to q2 in the round-9 winner (docs/concepts/roller-longdyad-knuckle-3r.md,
VERIFIED 18.67 frozen exact, held out 23.73). The chain is: a lobe on hub 2, then a bell crank on link 1b (an MR63ZZ
pair), then a bent 6 x 3 Ti arm, then an MR63ZZ roller on an integral stub, then the conjugate flank milled into a lug of
link 1a at hub K. One clock spring in K's cap closes both rolling pairs. There is no rod and there are no ball links.
This note prices that drive with real parts and real numbers, by the same method as
docs/research/sidecar_mechanism_redteam.md.

Scripts and outputs are in `docs/research/roller_mechanism/`:

- `extract.py` wears the verified config through the claim's own model, loaded unchanged through the verifier harness.
  It uses `ang_min` 26.8823, the auditor's knee fix, and the frozen protocol: fit on Bench(60,160) fast, then worn on
  Bench(110,360) exact or held out. It dumps the drive geometry, the cam table, the per-pose state and every part's
  signed skin distance on every reached pose to `geo_*.npz` / `geo_*.json`.
- `drive.py` does the rest:
  - re-synthesises the cam pair on a 0.05 deg grid;
  - computes the flank as a ruled surface, its machining and straight-extrude errors, and a 3-arc sketch;
  - solves the real lobe follower;
  - computes the loads, using exact two-support statics on the crank pair;
  - computes the arm's stiffness with the unit-load method on its real 57 mm polyline;
  - converts play into K error and fold margin;
  - sizes the spring and checks lift-off;
  - measures skin distance per part.

  It writes `results_bench.json`, `flank_bench.csv`, `lobe_polar_bench.csv`, `spec_points_bench.json` and
  `slaved_law_bench.json`. The chosen follower is set by env: `A_S=7.0 PSI=219 RR=3.0 python3 drive.py geo_bench.npz bench [geo_held.npz]`.

**Reproduced:**
- Frozen exact Bench(110,360) at `ang_min` 26.88: **18.67**. Held out: **23.72**, equal to the auditor's re-wear.
- The re-synthesised cam matches the model's horn pressure angle to 0.000 deg.
- Taken K maximum: 45.62 on the bench and 46.17 held out. The drive range ends at dK_lim **46.25**, at
  q2 = -14.199 deg. The onset is at q2 = +7.279.

## Verdict

**The drive is buildable at this size for MVP1. Nothing in it is unbuildable.**

Three things must change from the model, each one cheap:

- **the lobe follower**: the modelled one does not exist;
- **the crank bearings**: 683ZZ for margin;
- **a pre-set K bias**: there is no turnbuckle to trim with.

The ~2.5 N roller load that round 9 assumed is really 5.3-8.3 N. Everything still holds at that load.

| # | Finding (measured) | Fix (cheapest first) |
|---|---|---|
| 1 | **The modelled lobe follower does not exist.** s_arm 4.05 on a lobe of r_lobe 8.24 lies inside hub 2's O20 housing, as in the sidecar's finding 3. The L1 builder in progress draws this lobe "inside the O20 skirt". The exact spatial cam, solved for the verified law (dK = 2.1534 t, phi = dK / 2.4696), gives 23 feasible followers. Each one: (a) has a dwell between O20.2 and O21.6; (b) has a profile that never dips under r 10.1; (c) sweeps its nose clear of the O6 neck; (d) drifts <= 0.6; (e) has no undercut. | Build an **MR63ZZ roller (O6 x 2.5) on an O3 pin, on a 7.0 mm short arm at psi 219 deg**. The **profile runs r 10.84 -> 12.80 mm** (normal offset, `lobe_polar_bench.csv`). The **real pressure angle is 10.2-16.8 deg** (the verifier's 23.2 was the model's own lobe), the pitch radius of curvature is at least 12.5, and the drift along u2 is 0.43 mm. I chose the 7.0 arm over 8.5 to keep the nose low (12.80 against 13.19), because gen-5's lobe entered the skin at r 12.87. The lobe ring's skin clearance must be measured: see build step 7. |
| 2 | **The crank torque is g times K's torque.** It is T_K x g = **0.20-0.23 N.m** from the spring alone and **0.28-0.31 N.m** with the MVP1 load. The virtual-work check is exact. So the lobe follower carries **29-34 N** (spring) and **41-46 N** (MVP1). The crank pair also carries a tilt moment: the roller acts 14.0 mm below the boss on dR and the follower 7.6 mm above it. Exact two-support statics give a worst bearing load of **43.5 N (spring) and 61.5 N (MVP1)** for 2 x MR63ZZ in the O10 x 6 boss. Against C0r of about 73 N that is a static factor of **1.68 / 1.19**: buildable, but thin. | **2 x 683ZZ (3 x 7 x 3, C0r about 120 N) in the same O10 x 6 boss** (1.5 mm wall, no spacer): factor **2.46 / 1.74**, with no envelope change. With more height allowed, the best option is 2 x MR63ZZ **straddling** the follower plate in an O10 x 9.5 boss: worst load 25.7 / 34.9 N, factor 2.84 / 2.09. The boss top then rises 3.5 mm, still under hub 2's crown (f2 + 12.25), and must be judged. The follower MR63ZZ itself (29-46 N) sits at factor 2.2 / 1.6, and Hertz on the lobe is 480-560 MPa, so a 17-4PH H900 lobe is fine. |
| 3 | **The roller load is 5.26-6.11 N (spring) and 7.43-8.30 N (with MVP1), not ~2.5 N.** The normal's moment arm about uK is **15.0-15.2 mm over the whole stroke**. It does not shrink at the pressure-angle cap, because the contact radius grows from 15.7 to 20.6 mm as the angle rises. Arm stiffness (6 x 3 Ti-6Al-4V, 57.4 mm bent polyline, unit-load method): **0.049-0.057 mm along the contact normal**. That is **K lagging 0.22 deg**, varying only 0.03 deg over the stroke. Root stress is 27.5 MPa. The O3 stub deflects 0.1 um, at 6 MPa. Hertz roller-on-flank is at most 183 MPa even against a flat flank, and the real flank is concave. | Nothing to fix. The lag is a constant: put it into the K bias (finding 6). |
| 4 | **The 43 deg cap is soft, and the drive is not at a wall there.** pa_horn reaches 43.0 at dK 46.3, 44 at 48.6 and 45 at **51.05**, rising 0.43 deg per deg of K. Past the limit the arm-hub K, roller-hub K and arm-hub 2 clearances all stay **> 5.0 mm** (to dK 52). The audit's 1.14 / 2.02 mm hub K minima are **at dK 0 (rest)**, not at the cap. The force cost of 43 deg is nil, since the moment arm about uK stays 15.05 mm. The real hazard at the end is the **flank's end**: the model builds the flank only to dK_lim, so with 0.5 deg of K slop the roller would run off its edge. | **Build the flank to dK 48.25** (+2 deg run-out, PA <= 43.9, clearances > 5 mm). The binding stop is the **q2 dowel stop B at q2 = -14.20 deg (dK 46.25)**. If K's own stop B (dyad) sits at a smaller dK than 48.25, the flank needs nothing more. |
| 5 | **The flank is easy to machine.** It is a ruled developable surface: its rulings are parallel to radial lines through GH, offset 3 mm by the roller radius. It is **6.55 mm long** (dK 0-48.25), at a contact radius of 15.7-20.9 mm from uK, and it is **concave everywhere toward the roller**. Its mid-plane section is **3 tangent arcs within 3 um**: **R 6.134** (dK 0-18.6), **R 10.403** (18.6-38.5) and **R 13.619** (38.5-48.25) (`results_bench.json` `flank_arcs`). The exact surface needs only 0.1-2.6 deg of wire taper. A **straight extrude** of the mid section along the mean ruling z_c leaves the roller's edges **+-10 um** off, which is +-0.04 deg of K. | **Cut it as a straight 2-axis wire-EDM pass along z_c** (or flank-mill it along z_c). The concave R >= 6.1 takes any cutter of O12 or less. No taper and no 5-axis are needed for the flank itself. The lug body around it (a spherical shell) is the 5-axis part, as already stated. The CAD draws exactly that: a constant 3-arc section extruded along z_c, which the no-loft rule allows. |
| 6 | **There is no trim, and the play is biased one way.** The rod sidecar trims with a turnbuckle; this drive has nothing to turn. Under the spring, every compliance and clearance shifts K toward **less open**: arm -0.22 deg, roller MR63ZZ radial clearance (MC3, 5-10 um) -0.04, follower MR63ZZ clearance -0.17 to -0.19 deg. The systematic sum is about **-0.45 deg**. Random parts (lobe form +-10 um: +-0.19; flank +-10 um: +-0.04; the preloaded pair: about 0) give RSS +-0.2 deg. The crank pair **must be preloaded**: unpreloaded, its radial play costs 0.41 deg of K per 10 um at a 3.5 mm span (0.20 at the 7 mm straddle). Fold margin (the one `th` metric; slope +0.084 deg of margin per deg of K): -0.25 deg gives 5.160 (bench min 5.181), +0.5 gives 5.223 and +1.0 gives 5.265. Held out, the minimum is 5.031, so **a K lag of more than about 0.37 deg puts a held-out pose under 5**. | **Pre-set a +0.5 deg K lead**: advance the lobe ring's dowel phase by **+0.23 deg of q2** (0.5 / kK). The systematic -0.45 deg then cancels and the margin keeps >= 5.03 held out. It costs nothing: the cam's onset dwell absorbs it, and pa_horn at dK + 0.5 is 43.2. A 0.1 mm wave washer preloads the crank pair. |

**MVP2.** If a powered K load (several N.m about uK) went through this train, it would multiply by g = 2.47 at the crank:
the follower would see kN and the 683ZZ would fail. This is the same verdict as for the sidecar and gen-5. It is not an
MVP1 issue.

## 1. Geometry for the CAD (`spec_points_bench.json`; model frame = link 1b at q = 0, K on stop A = link 1a at K 0; mm from GH)

**Axes and levels**
- The crank axis dR is 14.78 deg from u2 and 23.26 deg from uK. uK is 38.03 deg from u2.
- Crank pivot: PV is on dR at 62.82 mm, the boss underside. The boss is O10 x 6, so it spans 62.82-68.82 along dR.
- Member levels: f = 50.45 / 62.04 / 78.21 and fK = 55.12.

**Crank motion and law**
- The crank turns phi = |dK| / 2.4696, with sense sig +1 about dR. That is **18.73 deg at dK 46.25**.
- Law: dK = 2.1534 (q2_onset - q2), with q2_onset 7.279 deg. K's sense is sp = -1.
- `slaved_law_bench.json` gives the table for build.json `slaved` (force closure; drive groups crank / roller on l1b).

**Roller and arm**
- Roller centre at rest: `roller_centre_rest`, 61.70 mm from GH. Its axis is radial (`roller_axis_rest`).
- Roller r_c 15.22 from uK at beta -173.46 deg, at the lug's mid layer: fK + hl 2.154 + lift 1.027 + 1.5.
- Bent arm: `arm_polyline` (27 points, 57.4 mm developed). It runs straight from the boss to the tangent point, then
  along a 121.3 deg arc concentric with uK at r_c. Its tip is over the lug at level 63.4.

**Lobe follower**
- Follower centre at the onset: `follower_centre_onset`, 70.44 along dR (7.6 above PV). Its axis is parallel to dR.
- Its short arm is 7.0 mm at psi 219 deg. The polar frame is `lobe_polar_x` / `lobe_polar_y` (link 2 at the onset).
- The lobe band is f2 + 6.2 .. f2 + 9.2, as in the sidecar.

**Flank**
- Sketch frame `flank_sketch_frame`: origin GH, ez = z_c (the extrude direction), ex = uK projected.
- Mid plane at 61.678 along z_c. The arcs in `results_bench.json` `flank_arcs` are given as (p0, pm, p1, centre, r) in
  (ex, ey).
- `flank_bench.csv` gives, per 0.25 deg of K: the mid / top / bottom sections (+-1.5 mm), the roller centre, the
  contact point and the normal, all in link 1a's frame, plus both pressure angles.

## 2. Parts list (real parts, real size)

| part | spec | qty | play / rating |
|---|---|---|---|
| flank roller | **MR63ZZ** (3 x 6 x 2.5; NMB DDL-630ZZ class), on the crank's integral O3 g6 stub. It is retained from the skin side by an **ISO 2341-B 3 x 8** headed pin pressed through the arm tip (head O5 x 1.0; the verifier priced O5 x 0.8). The alternative is the modelled O4.5 x 0.8 Ti cap pressed onto an O1.5 spigot. A 0.2 mm integral step clears the shield. | 1 | radial clearance MC3 5-10 um (one-sided: -0.04 deg of K); load 5.3-8.3 N against C0r about 73 N, factor >= 8.8; the roller's skin distance is >= 5.76 mm on every taken pose, so the head size is free |
| crank pair | **2 x 683ZZ** (3 x 7 x 3, C0r about 120 N, to confirm) in the O10 x 6 boss, or 2 x MR63ZZ straddling the follower (O10 x 9.5) | 2 | **preloaded** by a 0.1 mm wave washer (unpreloaded: 0.41 deg of K per 10 um); worst 48.8 / 68.9 N, factor 2.46 / 1.74 |
| pivot pin | O3 h6 17-4PH H900, pressed into link 1b, retained by a DIN 6799 RS 2.3 clip (as the L1) | 1 | |
| crank | Ti-6Al-4V, **5-axis machined from solid**: boss O10 x 6, bent arm 6 x 3 (the arm's arc and the joggle to the tip level are machined, not bent: R < 15 mm), integral O3 stub at the tip, follower lug at 7.6 above PV carrying the O3 follower pin | 1 | arm root 27.5 MPa; arm 0.057 mm at 8.3 N |
| lobe follower | **MR63ZZ** on an O3 h6 pin pressed into the crank's short arm at a_s 7.0 | 1 | 29-46 N against C0r 73 N (factor 2.2 / 1.6); MC3 clearance -0.17 to -0.19 deg of K |
| lobe ring | 17-4PH H900, 3 mm band at f2 + 6.2..9.2, profile r 10.84 -> 12.80 over 21.48 deg of q2 past the onset, dwell O20.4 elsewhere. Wire-EDM, bore O18 on link 2's turned ring, keyed by an O1 dowel **at the onset phase + 0.23 deg** (K bias), clamped by the cap skirt. | 1 | Hertz 480-560 MPa |
| flank | cut into link 1a's horn lug (Ti-6Al-4V, the 5-axis spherical-shell lug): 3-arc section R 6.134 / 10.403 / 13.619, straight wire-EDM along z_c, 6.55 mm long to dK 48.25, 3 mm deep | (in link 1a) | +-10 um edge deviation = +-0.04 deg |
| K closing spring | the kit-rule spiral spring in K's cap: 1.4310 (EN 10151 +C1900) strip 0.3 x 5, **144.7 mm** for 0.015 N.m/rad, pre-wound **306 deg** for **0.080 N.m at stop A**, 0.092 N.m at the end of the stroke. Peak bending stress **1229 MPa**. The stroke amplitude is only 85 MPa, so Goodman sits at about 0.77. Made to order (spiral springs are not catalogue parts). Lower stress: 0.35 x 5 x 230 mm gives 901 MPa. | 1 | the only preload in the train |
| knee | unchanged two-pin knee (iglidur GSM sleeve + 2 GTM washers per pin on integral Ti pins), **no encoders** (user, 2026-10-17); knee stop at ang_min 26.88 | | |

## 3. What keeps contact

**One spring in series closes both pairs.**
- K's spring presses the flank on the roller with 5.3-6.1 N. That gives a crank torque of 198-227 N.mm, which always
  has the same sign.
- The crank torque presses the follower on the lobe with 29-34 N.
- A pair lifts off only if the train's torque changes sign. The crank's own inertia is negligible: about 2e-6 kg m2 at
  0.87 q2-acceleration gives about 1e-4 N.m against 0.2 N.m.
- So both pairs close **if and only if** K's spring wins against K's own load.

**Static.** The spring gives a factor of **2.42-2.79** over the MVP1 opening load of 0.033 N.m (the gen-5 bound).

**Dynamic.** The estimate takes the gen-5 inertia, about 5e-4 kg m2 about uK. K's acceleration limit is 94 rad/s2. With
kK 2.15 that is a **q2 acceleration limit of 43.7 rad/s2**, which a throw exceeds and everyday motion does not. R17 must
run the clips with `slaved_law_bench.json` (closure "force") and report slaved.law_err_deg and lift-off.

**The dwell.**
- Before the onset, K sits on stop A and the roller rests on the flank's rest end. The lobe follower sits 0.1 mm off
  the O20.4 dwell, which covers J2's window above the onset.
- The onset is a velocity step, at kK x phi' = 0.87 rad/rad on the crank. The 0.1 mm gap gives a small pickup tap.
  A 1 deg cubic lead-in is allowed and must be re-verified.

## 4. Play stack, the cuff and the 5-deg fold margin

**K error per 10 um:**

| source | K error per 10 um |
|---|---|
| flank or roller normal | 0.038 deg (m_horn 15.05-15.20 mm) |
| lobe or follower normal | 0.171-0.191 deg (g x m_crank 37.2-37.6 / m_f 6.7-6.9) |
| crank-pair tilt, unpreloaded | 0.41 deg at a 3.5 mm span, 0.20 at a 7 mm span |

**What moves K, one-sided under the spring (toward less open):**
- arm -0.22 deg;
- roller clearance -0.04 deg;
- follower clearance up to -0.19 deg.

The systematic total is **about -0.45 deg**. The random part, RSS **+-0.2 deg**, is lobe and flank form plus hole
position. That last term is the largest unknown, at about 0.19 deg of K per 10 um of follower-to-lobe distance.

**The cuff does not feel the K error as strain.** K is slaved and never read. The 3 hub encoders plus the law give the
pose, and a K error only re-solves q1-q3 and the two knee pins. The tracked humerus orientation is off by the K error
about uK: about 0.2 deg after the bias, and about 0.65 deg without it.

**Fold margin (verifier `th_margin`: 5.181 bench, 5.031 held out; slope 0.084 per deg of K):**

| K offset | taken min margin (bench) |
|---|---|
| -0.25 deg | 5.160 |
| +0.25 deg | 5.202 |
| +0.5 deg | 5.223 |
| +1.0 deg | 5.265 |

Below -0.25 deg the law's `th` is not monotone, so it is not interpolated. By extrapolation, -0.65 deg (no bias, worst
case) reads about 5.13 on the bench and **4.98 held out**. **With the +0.5 deg lead** the worst case is about -0.15 deg,
which reads 5.17 on the bench and **5.02 held out**.

## 5. Skin (the drive parts, signed distance on the bench's exact skin)

**Taken poses (Bench(110,360) exact).** The drive's minimum per part:

| part | min distance |
|---|---|
| crank arm | **2.60 mm** |
| horn lug | **2.16 mm** |
| crank boss | **2.49 mm** |
| roller | **5.76 mm** |

All drive parts pass the 0.3 mm rule with 1.8 mm to spare. The hard goal's 0.3 mm is therefore at risk only from parts
the model does not sample: **the real lobe ring** (r up to 12.80, gen-5 lesson) and the follower plate.

**The audit's deep contact is the drive.** The 2 contact poses are workspace (plane 15 / 30, elevation 165, axial -60):

| pose (plane, elevation, axial) | depth by part (mm) |
|---|---|
| 15, 165, -60 | horn lug -9.08, crank arm -8.51, roller -5.29, hub K -2.65 |
| 30, 165, -60 | horn lug -5.60, roller -0.46 |

That is the summed depth of 16.46 mm the audit flagged. Both poses are lost, and they are scored as contact. The CAD
must report them as presses, not hide them.

## 6. Build spec for the CAD agent (pipeline/concept_l1/build_roller_l1.py, user_style_roller.py)

1. **Config.** best_params with ang_min 26.8823 (bench 18.67 / held out 23.72, reproduced here).
2. **Lobe = the real follower, not the model's s_arm 4.05 / r_lobe 8.24.**
   - Ring profile: `lobe_polar_bench.csv`, normal-offset r 10.84 -> 12.80 over 21.48 deg past the onset.
   - Draw it as tangent arcs through the profile points, then join it to the O20.4 dwell with a concave R2.5 at the
     onset. Extrude it along the follower axis (dR at mid-stroke) over the 3 mm band.
   - Phase it **+0.23 deg of q2** early (K bias +0.5).
   - The follower is an MR63ZZ on a 7.0 mm short arm at psi 219 deg, centre `follower_centre_onset`, axis dR.
3. **Crank.**
   - Boss O10 x 6 on PV, carrying 2 x 683ZZ preloaded (or the straddle layout, stated).
   - Bent arm 6 x 3 along `arm_polyline`.
   - Integral O3 stub at the tip carrying the MR63ZZ roller, retained by the ISO 2341-B head (O5 x 1) on the skin side.
   - Mark it "5-axis machined from solid".
4. **Flank.**
   - The 3-arc section in `flank_sketch_frame`, extruded straight along z_c through the 3 mm lug.
   - It covers dK 0 -> **48.25** (run-out).
   - The lug root runs to hub K's rim as modelled.
5. **Stops.**
   - **q2 dowel stop B at q2 = -14.20 deg** (dK 46.25), shifted by the bias: -13.97 with the +0.23 phase.
   - K stop A as modelled.
   - Knee stop at 180 - 26.88.
   - Each stop is a dowel in an arc slot.
6. **build.json `slaved`.** Use `slaved_law_bench.json` (closure "force"). Map the CAD's own frame keys. Run R17.
7. **Judge.**
   - **Skin**, with the gen-5 tool (`docs/research/geneva_rod_drive/lobe_skin.py` method), on every frame of Raise
     overhead: the real lobe ring and the follower plate at >= 0.3 mm. If the lobe end enters, take gen-5's fix (iv):
     a radial offset of the dwell. A 6.5 mm arm at psi 219 gives a nose of 12.63 and PA 14.7 at higher load
     (`follower_options`).
   - **R6**: the follower lug and plate against hub 2's cap skirt, and the 683ZZ boss O10 against hub 2.
   - **The audit's watch items**, reported and not hidden:
     - PA at the last taken step: 42.95 held out;
     - hub K clearance at rest: 1.14 / 2.02;
     - contact depth, summed: 16.46 mm;
     - workspace in-band at elevation 90-140: 0.798.
8. **Render.** The flank, roller and follower are best seen from the lug side at about 45 deg. The lobe and the crank
   are bead blasted, the bearings polished, and nothing is black.

## Red team (what could still be optimistic)

- **The held-out per-part skin split is not in this note.** The held-out wear reproduces 23.72, but its per-part
  distance pass (952 poses, exact skin) did not finish inside the time box. Rerun it with
  `extract.py geo_held.npz '{"ang_min": 26.8823}' held`, then `drive.py geo_bench.npz bench geo_held.npz`, which fills
  `skin_held`.
- **The lobe ring's skin clearance is not measured.** The model samples no lobe. Gen-5's ring at r 12.87 entered the
  skin by 0.26 mm. This one tops out at 12.80. The CAD's frame sweep decides it.
- **Bearing ratings are from memory:** MR63ZZ C0r about 73 N, 683ZZ about 120 N. Confirm them on the supplier sheet.
  At C0r 73 the as-modelled pair's factor of 1.19 at MVP1 is the thinnest number in this note.
- **The MVP1 load (0.033 N.m) and the inertia (5e-4 kg m2) are the gen-5 estimates**, not this chain's. R17 with the
  slaved coupling replaces both.
- **Hole-position tolerance is the largest play term.** The follower-to-lobe distance costs 0.19 deg of K per 10 um,
  so specify +-10 um on the PV and follower-pin bores (jig-bored or wire-EDM'd).
- **Below -0.25 deg the K-offset rows are extrapolated** because the law's `th` is not monotone there. The +0.5 deg
  bias keeps the build on the measured side.

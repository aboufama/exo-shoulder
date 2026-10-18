# Desmo K-drive red team + build spec: desmo-conecut-knuckle-3r (gen-9 winner)

2026-10-18. Subject: the one new mechanism in generation 9, the **spring-free desmodromic K drive**.
- **Stage 1:** a crowned O1.5 440C pin on the crank's short arm (a_s 9.529, psi 149.71) runs in a 1.52 groove under hub 2's
  cap ring. The groove is blended over 10 deg of q2 at the onset.
- **Stage 2, inverted:** an O1.5 440C dowel is pressed in a boss on link 1a at C0 (r_c 16.176, beta -177.169). It runs in a
  1.52 x 3.72 slot cut in the crank's tip plate.
- There is no clock spring.

Everything else is the gen-8 chain (conecut knee, J3 dowel stop, the lead's seats and law).

Scripts and outputs are in `docs/research/desmo_mechanism/`:
- `extract.py` fits the verified claim config (the model's BEST = k57) with the claim's own model, loaded unchanged, on
  Bench(60,160). It reproduces the claim's drive report exactly: dK_lim 46.5 at the slot end, slot slop 0.04, crank-free
  play 0.174, stage-1 forward PA first failing at K 47.504 at mu 0.15. Runtime 8 s.
- `drive.py` computes loads, efficiency both ways, Hertz, pin and dowel bending, press fit, wear, play stack, tolerance to
  K error, and the slot rulings. It writes `results.json` plus the CAD exports `groove_link2.csv` and `slot_crank.csv`.
- `fold_offset.py` maps K offset to the one fold-margin metric th by exact re-solve on the slaved law, on the verified
  taken poses. It reproduces the verifier: 5.180 bench (pose 313), 5.008 held (pose 1054). Output: `fold_offset.json`.

All runs were local, nice 15, 1 process, OMP_NUM_THREADS=1. Every number below comes from those three JSON files.

## Verdict

**Buildable for MVP1 at this size, with four changes.** One element sits at its material limit: stage 1's convex
groove ridge. Nothing is unbuildable, provided **the drive only ever carries in-motion loads**. Any stop or overload load
that flows through stage 1 bends the O1.5 pin or brinells the ridge. So every stop must act on its own joint angle,
outside the drive.

### Unbuildable as modelled, each with the cheapest fix

1. **Stage 1 cannot be cut in Ti-6Al-4V.**
   - The groove centreline radius is 1.01-1.37 mm over the blend (K 0.5-8, which includes the rest pose at dK 4.6) and
     1.09 at K 46. That leaves a **convex inner-wall ridge of r 0.247-0.33 mm**.
   - The pin's tilt across the groove (4.76 deg) forces a crown of R <= 4.5 mm (chosen R 4.0), so the contact is a
     point, not a line.
   - Hertz p0 at the ridge, nominal in-motion load: **2.0 GPa on Ti**. Point-contact yield onset is about 1.34 GPa
     (1.61 sigma_y), so Ti yields.
   - On the **440C insert** the same load gives 2.4 GPa, against an elastic limit of about 3.0 GPa. At the in-motion
     upper bound it is 3.8 GPa, at shakedown.
   - **Fix:** the 440C ring insert is mandatory (the model already counts it, cx 16.5). Cut the groove as a **through
     slot by 2-axis wire EDM in a hardened 440C ring**, rather than milling it blind. The walls are parallel to u2 and
     the pin is crowned, so 2-axis is correct here. Skim pass, width 1.520 +-0.003.
   - Cheapest geometric relief: blend 24 lifts the ridge to 0.34 mm at an equal fast number (concept doc, k128, 13.31).
     That cuts p0 by about 15 %. It needs a verified wear before the CAD can use it.
2. **The slot cannot be a straight 2-axis wire cut.**
   - The nose's axis is radial through GH, so the slot walls are ruled surfaces of radial lines. Over the 3.72 mm slot
     the rulings turn 0-2.24 deg against the mean.
   - A straight extrude leaves the walls **48.8 um off at the plate faces**. That is 5x the 10 um running clearance, so
     it would jam or edge-load.
   - **Fix:** 4-axis (XY-UV) wire EDM of the exact ruled walls (`slot_crank.csv`, centreline in the crank frame), with
     a skim pass. The CAD keeps a constant-section extrude (no lofts) and puts the ruled surface on the drawing.
3. **Bare Ti sliding on 440C galls.** At k ~1e-5 (galling class), 1e6 strokes wear 0.5 mm off a bare Ti groove and
   78 um off a bare Ti slot wall at the in-motion upper load. With a 440C ring insert, greased (k 1e-8), the groove wall
   loses 0.5 um and the pin 1.9 um.
   - **Fix:** use the 440C groove insert. Either make the crank's tip plate in **17-4PH H900**, or keep it Ti and give
     the slot an **a-C:H DLC** coat (2-3 um, the gen-7 flank spec). Coat the O1.5 dowel in the same batch. Grease with
     Kluber Isoflex Topas NB 52 (PAO, no EP).
4. **The K play takes one held-out pose under th 5, and the slot end becomes the J2 stop.**
   - With no preload, K floats in its play band: **0.227 deg** one-sided at the model's c 0.01, **0.217 / 0.276**
     nominal / worst with the wire-EDM fits.
   - A lag of 0.227 reads **th 4.986** held out (1 pose under 5: pose 1054, dK 46.27). The bench still reads 5.16.
   - The re-solve slope is **0.08 deg of th per deg of K**, not the verifier's partial dth/dK of 0.403 (the chain
     re-closes). The auditor's T3 estimate (4.91) is therefore pessimistic. The direction is right: 1 pose under 5.
   - **Fix: build a +0.25 deg K lead.** Phase the cap ring's key on hub 2 by **+0.116 deg of q2** (0.25 / kK 2.1534).
     The band then sits at [+0.02, +0.48] nominal and [-0.03, +0.53] worst. Held th >= 5.004 (0 poses under 5); bench
     >= 5.18.
   - The lead pushes the most-open K to 46.27 + 0.53 = 46.80. So **cut the slot to kslot 46.9** (stage 1's forward PA
     rule first fails at 47.5 at mu 0.15, so this is free). **Put J2's own dowel stop B at K_law 46.30**, i.e.
     q2 = 7.279 - 46.30 / 2.1534 = **-14.22 deg** in the gen-8 convention. The gen-8 CAD's -15.47 belonged to dK_lim 49.75.
   - J2's stop then always lands before the slot end. No taken pose is lost: the taken max is 46.27 held and 45.62
     bench.
   - The lead and the longer slot are a re-wear item for the verifier: same takes expected, metal moves by 0.26-0.35 mm
     at R 60-80.

### What is not a problem

- **Friction.** No pose binds at mu 0.087-0.17.
  - Stage 1 forward efficiency at the held stroke end is 0.954 / 0.937 / 0.921 / 0.910. Overall (both stages) it is
    **0.907 / 0.873 / 0.842 / 0.822**.
  - The only true self-lock is stage 1's back-drive at K 0-0.12 / 0.21 / 0.33 / 0.41 deg: the dwell lock, the same
    0.326 the auditor measured.
  - The family's 43-deg design rule (PA + atan mu) on the pin side first fails at **mu 0.17, at K 45.98**, below the
    held stroke of 46.27.
  - Read the verifier's "binds at K 44.75 at a_s +0.07" as that **rule**, on a groove re-synthesised for the new a_s.
    It is **not a jam**: efficiency there is still about 0.9.
  - A real hole-position error does not re-synthesise the groove. It shifts the K law (next bullet).
- **A hole-position error is a K-law error, not a bind** (exact intersection of the pin circle with the nominal groove):
  - a_s +-0.01 mm moves K by +-0.007 at the onset, rising to +-0.095 deg at the stroke end;
  - psi +0.06 deg (0.01 mm tangential at the pin) is a **constant -0.144 deg** phase;
  - groove profile +-0.01 gives 0.145-0.173 deg; slot profile +-0.01 gives 0.036-0.039 deg.

  Hold the crank's three holes (pivot, pin, plate datum) to +-5 um in one setup. The constant phase errors are taken
  out by setting the lead at assembly (build step 6).
- **The dowel and the pin in motion.** Dowel bending is 10-36 MPa and stage-1 pin bending 31-115 MPa, against
  440C's ~1.9 GPa. Stage-2 Hertz is 0.28-0.53 GPa on Ti / 0.32-0.61 on 440C: line 2.2 mm, the slot's tightest wall is
  the convex 0.68 mm at the closed end.
- **The cap-ring sector vs hub 2's O20.** The ring reaches r_out 10.96, so it is **0.96 mm outside O20 over 99.9 deg**.
  That is the verified metal (the +0.67 in-band). The round-14 lens (`lowarm-halfring-knuckle-3r`, half-ring stage 1)
  had only started modelling at 01:00 UTC, with no result in events.jsonl yet. Build the verified sector.

## 1. Loads (moment about uK through the drive; worst pose = largest force over the stroke)

Levers, frictionless and either sign:

| quantity | value |
|---|---|
| stage 2 (normal lever) | 14.69-15.97 mm/rad, so **62.6-68.1 N per N.m** of T_K |
| stage 1 | the crank multiplies by 2.393; the pin's normal lever is 7.93-9.46 mm per rad of crank, so **253-302 N per N.m** of T_K (worst at K 46.4) |
| J2 torque | T_K x kK 2.1534 |
| stop B (slot end along the path) | 61.8 N per N.m |

The judge's 0.034 N.m (nominal) comes from the gen-8 CAD with a spring and force closure (`user_conecut_knee`
dynamics.json, `drive_torque_peak`). Spring-free, the K reaction is unmeasured. The 0.126 row bounds it: the spring
design's preload, plus its rate x 0.81 rad, plus 0.034.

| T_K (N.m) | case | stage-1 pin F (N) | stage-2 dowel F (N) | ridge p0 Ti / 440C (GPa) | pin bending (MPa) | dowel bending (MPa) |
|---|---|---|---|---|---|---|
| 0.034 | nominal in motion | 10.3 | 2.3 | 2.00 / 2.43 | 31 | 10 |
| 0.126 | in-motion upper bound | 38.0 | 8.6 | 3.09 / **3.76** | 115 | 36 |
| 1.0 | felt line (1 N.m at GH, all of it about uK) | 302 | 68 | 6.2 / 7.5 (brinell) | 911 | 288 |
| 2.28 | cuff slip, mu 0.5 at 14 kPa | 688 | 155 | - | **2077 (pin yields)** | 656 |
| 8.4 | lock line | 2535 | 572 | - | 7651 | 2416 |

The drive survives in-motion loads only. **Every stop torque must bypass stage 1:**
- J2 stop B is a dowel on J2's own angle (above);
- K stop A: keep the gen-8 O3 dowel-in-arc-slot on K's own angle, set to engage at **K = -0.25 deg**, just beyond the
  slot's closed end plus the play. It takes every -K overload at rest directly, link 1a to link 1b.
- **+K at rest has no bypass.** It is held only by the dwell lock (nose, slot end, crank, pin, dwell groove at pitch
  9.4, conformal walls 8.64 / 10.16). Its load path is the pin's 300 N per N.m.

**This is the one residual risk:** a +K torque above ~0.15 N.m at rest marks the ridge. The rest pose dK 4.6 sits on the
ridge (r 0.27 mm). R17 must report the K reaction at rest. If it exceeds ~0.1 N.m, take blend 24 and a smaller-pin
re-placement to the next round. An O1.0 pin lifts the ridge to ~0.5 mm, for about 18 % lower p0 and pin bending x3.4,
still under 400 MPa at the upper bound.

## 2. Free play, chatter, drift (no preload)

One-sided play stack (deg of K). Slopes come from the model: 0.187 per 10 um of groove clearance (the verifier's dense
scan) and 0.040 per 10 um of slot clearance.

| build | groove c1 (mm) | slot c2 (mm) | play |
|---|---|---|---|
| model nominal | 0.010 | 0.010 | 0.227 |
| wire-EDM 440C insert, best / nominal / worst | 0.0075-0.0125 | 0.0045-0.0105 | 0.158 / 0.217 / 0.276 |
| milled Ti groove, worst | 0.020 | 0.0105 | 0.416 |
| plus an un-preloaded crank pair (10 um) | | | 0.449 |

- The crank pair must be axially preloaded: 2 x 683ZZ straddling the pin arm with a 5-10 N wave washer, as in gen 7.
  K and J2 are DB-preloaded (0 play).
- **Chatter.** K crosses its band whenever T_K changes sign. The metal shift is up to 0.28-0.35 mm at R 60-80
  (0.25 deg). Impact energy is about T_K x band = 0.034 N.m x 0.0048 rad = 0.16 mJ: an audible tick at most, no damage.
- **Drift.** K sits wherever friction leaves it inside the band. With the +0.25 lead the whole band stays on the safe
  side of th.
- **The dynamics judge cannot see this.** Its "form" closure is bilateral with zero backlash. Run R17 with
  `"closure": "form"` and spring preload 0, and add the band by hand (0.16-0.28 deg). A backlash-aware slaved closure
  is a judge request, not something this design can fix.
- **Cheapest real preload, if R17 or the wearer reports chatter:** a torsion spring on the crank pivot (O3 pin, crank
  bias of ~0.08 N.m, wire about 0.5 mm, one coil set over the 683ZZ spacer). It preloads both stages through the train
  and removes the band up to T_K ~0.033 N.m. It costs the "spring-free" label and simplicity points. **Not recommended
  for MVP1**: the lead already holds th.

## 3. Build spec (for `user_style_desmo.py` / `build_desmo_l1.py`)

Geometry is in the frame of link 1b at q2 onset, K = 0, mm from GH (`results.json axes`):
- crank axis dR is 14.66 deg from u2 and 23.37 deg from uK; uK is 38.03 deg from u2;
- PV is at 63.288 along dR;
- pin centre F0 (-33.048, 43.888, 32.964): 9.529 from dR, pitch radius 9.40 from u2, level 63.377 along u2 (groove
  mid-plane hmid);
- dowel seat C0 (-13.653, 59.209, -9.585): R 61.514 from GH, r 16.176 from uK, level 59.349 along uK;
- g 2.3934 (crank turns |dK| / g); kK 2.1534.

Steps:
1. **Stage-1 groove** (`groove_link2.csv`: centreline in link 2's ring plane gx / gy with drift gz <= 0.286, every
   0.2 deg of the law, PA and N per N.m).
   - A 440C ring insert, through-hardened 58-60 HRC, 1.5 thick, pressed and keyed into hub 2's cap ring.
   - Groove as a through slot, 2-axis wire EDM, 1.520 +-0.003, walls parallel to u2.
   - Ring OD per the verified sector (r_out 10.96, 99.9 deg arc).
   - Key the insert with an O1 dowel at the onset phase **+0.116 deg of q2** (the +0.25 deg K lead). Ream that key
     hole at assembly (step 6).
2. **Stage-1 pin:** O1.5 440C, ground +-0.002, **crowned R 4.0** over its 1.5 mm engagement (drop 0.070 at the ends >
   the 0.062 tilt mismatch). Pressed 3 mm into the crank's short arm along u2, H7 reamed 1.500 -0.005/0. Greased.
3. **Stage-2 dowel:** ISO 8734 1.5 m6 x 6, 440C, DLC-coated. Pressed into link 1a's O5 x 3 boss, reamed 1.500
   -0.005/0 (2-13 um interference): contact 78-507 MPa, boss hoop 93-607 MPa (factor >= 1.37 on Ti), pull-out 220-1434 N.
   Ground to 5.6: 3.0 boss + 0.15 gap + 2.45 in the plate, end 0.05 under the plate top.
4. **Slot:** in a tip plate 7.04 x 3.32 x 2.5 at the crank's arm-tip layer (underside R0 + 1.65 = 63.16).
   - **4-axis UV wire EDM** of the ruled walls, width 1.520 +-0.003, **kslot 46.9** (not 46.5). The closed end is the
     dowel disc (stop A).
   - Plate in 17-4PH H900, or Ti + a-C:H DLC. Hold the plate to hub K's O20 at >= 1.0: the model has 1.23, which leaves
     0.23 mm of pivot-position error.
5. **Stops, all on their own angles, all outside the drive:**
   - J2 stop B at q2 -14.22 (K_law 46.30);
   - K stop A dowel at K -0.25;
   - J3 dowel unchanged (gen 8).
   - Delete the gen-8 clock spring, its cap and the stop-A preload.
6. **Assembly, setting the lead.** Assemble without the insert key. Drive J2 through 3 points (K_law 5, 25, 45). Read K
   with the hub encoders or a dial on the boss. Rotate the insert until K leads the law by +0.25 +-0.05 deg, then ream
   and pin the key. This also removes the constant psi / groove phase errors (-0.144 deg per 10 um).
7. **Crank pair:** 2 x 683ZZ (3 x 7 x 3) straddling the pin arm, O10 boss, 5-10 N wave washer (gen-7 spec, factor 3.07).

**For the CAD agent to answer:**
- R17 with form closure, preload 0: the K reaction at rest and in motion, the law error, and the hand-added band;
- R6 on the plate against hub K;
- the insert and the hub-2 relief pocket (the auditor's M3);
- the verifier's re-wear at +0.25 lead and kslot 46.9.

## 4. Short parts list

| part | spec | qty |
|---|---|---|
| groove insert | 440C ring, 58-60 HRC, 1.5 t, wire-EDM through groove 1.520 +-0.003, O1 key dowel (ISO 8734 1 m6 x 4) | 1 + 1 |
| stage-1 pin | O1.5 440C, ground, crowned R 4.0, length 4.5 (1.5 engaged + 3 pressed) | 1 |
| stage-2 dowel | ISO 8734 1.5 m6 x 6, 440C, DLC, ground to 5.6 | 1 |
| crank pair | 683ZZ 3 x 7 x 3 + wave washer O7 (5-10 N) | 2 + 1 |
| stops | O3 dowels in arc slots (K stop A, J2 stop B), gen-8 parts re-phased | 2 |
| grease | Kluber Isoflex Topas NB 52 | - |

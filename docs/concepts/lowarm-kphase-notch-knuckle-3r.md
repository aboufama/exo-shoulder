# lowarm-kphase-notch-knuckle-3r

Round 15 lens C pick 4 (conditional): lowarm-kstop-knuckle-3r's chain (stage 1 at F+3.9, K-own set-screw stop A, pad
deleted) with the stage-2 pair phased toward hub 2 (beta -177.2 -> about -160), a sector notch in hub K's O20 housing where
the phased slot plate crosses it, and the hub-2 / ring2 flats. Aim: pose 264 from contact to take (-0.54 gap).

Status: gate 0 in progress (written incrementally; the numbers below are measured, nothing is predicted unless marked).

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Ask which body owns the notch: hub K's
   O20 is shared by link 1a (lower plate, stop-A lug) and link 1b (boss, stop-A groove). The slot plate is crank metal
   (crank pivots on link 1b), so its path relative to link 1b repeats every stroke, but relative to link 1a it turns with
   K. A notch on link 1b's boss is a fixed pocket swept once; a notch on link 1a's housing must cover the plate's path over
   the whole stroke in link 1a's frame. Measure the plate's level and azimuth band in BOTH frames and cut the notch in the
   body where the swept band is smallest. Second: re-phasing beta shortens the long arm (arc 127 -> 105-115 deg), which
   moves the dwell geometry and the pressure angles at every pose, not only 264 - so re-check the stroke limiter (dK_lim),
   the pocket pressure angle and the J2 dowel at the same time, before the 264 number.
2. **Rawest material.** The posed skin itself at the red-team poses (the bench's signed-distance field at 264 / 237 / 203
   / 205 / 316 / 139, exact path), the per-pose dumps of the lead and of kstop (docs/alignment/remeasure/*_perpose.json,
   kstop's sided wears), and the judge's own gate-0 logs (phase / beta / cfg scans of the lowarm cell). Not the
   catalogue's digest: every number in the spec is re-measured here.
3. **Methods and tools.** The chain's own model through kstop's harness (tools/alignment_lowarm_s1level.py ->
   docs/concepts/verify/lowarm-halfring-knuckle-3r.py -> desmo-conecut's _desmo_build_B), unchanged, with ONE override:
   hub K's solid is a cylinder minus a sector notch, as a CSG difference max(sd_cyl, -sd_notch), used in the PLATE-hubK
   stroke gate and in every per-pose collide check (ROD / CRK vs hub K), with hub-K skin samples inside the notch moved to
   the notch face. Bench(60,160) fast for the fit, Bench(110,360) exact for the frozen wear; the reduced 6-pose exact wear
   for gate 0.
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, exact), the round's
   verifier protocol (frozen shape, sided dwell wears, +0.1 / +0.2 probes, kit density), the alignment auditor (the notch
   under 'Keep O20 only'), and a red-team pose list: 264 (the target), 203 (the guard, >= 0.15 at every corner and probe),
   139 (0.072 on the lead), 237 / 205 / 316 (must not get deeper), plus the poses at the stroke end (dK >= 44) that a
   shorter stroke would lose.

## Gate 0, measured (2026-10-18 ~14:35-15:00 UTC)

Model: `docs/concepts/models/lowarm-kphase-notch-knuckle-3r.py`. lowarm-kstop-knuckle-3r's harness runs unchanged; the
one override is hub K's solid (O20 cylinder minus a sector notch, CSG `max(sd_cyl, -sd_notch)`). It applies in the
PLATE-hubK stroke gate and in every per-pose collide check. Hub-K contact samples inside the notch are dropped, and a
dense notch solid (face, side walls, floor; 0.5 mm / 1 deg) is added on link 1b. Scratch logs: the scratchpad `kph/`.

**Spec correction: the notch belongs to link 1b, not to link 1a's housing.** The model puts hub K's cylinder on link 1a
(member 1). The plate crosses hub K at F_K+7.1..9.9, but in kstop's stack link 1a owns only the lower plate (F..F+3).
Above F+3.15 the O20 metal is link 1b's boss, which also carries stop A's groove. The crank pivots on link 1b, so in
link 1b's frame the plate moves only by the crank angle. The notch is therefore a fixed pocket in link 1b's boss.

**Plate footprint** (gate bypassed, true clearance recorded; points within 1 mm of the O20):

| beta | true plate-hubK min | az about uK (link 1b) | z over F_K | K range | dK_lim (bypassed) |
|---|---|---|---|---|---|
| -160 | -1.108 | 50.9-84.8 | 7.08-9.89 | 0-20.0 | 46.75 slot-end |
| -157 | -1.403 | 54.9-89.7 | 7.08-9.94 | 0-20.75 | 46.0 pocket-pa |
| -155 | -1.212 | 57.5-89.7 | 7.08-9.91 | 0-18.75 | 44.0 pocket-pa |
| -152 | -0.899 | 61.5-89.5 | 7.08-9.86 | 0-15.75 | 41.0 pocket-pa |

**With the notch** (crown-open sector, floor F_K+6.0):
- beta -160, n 2.2: dK_lim 46.75, plate-hubK 1.07.
- beta -157, n 2.45: dK_lim 46.0, plate-hubK 1.05, pa_eff_horn 42.6.
- Bench(60,160) fast fit: 12.74 at beta -160 and 13.33 at beta -157, against kstop's cell at 13.50.
- Without the per-pose notch the fit collapses: reach 0.21, follow 0.12. This matches the judge's warning.

**Pose 264, exact, frozen, per part (mm):**

| config | K play | nose boss c32 | horn | crank | hub 2 c12 | hub 2 c13 | ring2 c33 | r:ring2 |
|---|---|---|---|---|---|---|---|---|
| kstop beta -177 | 0 | -1.17 | -0.69 | -1.02 | (hidden) | | | |
| -160, n 2.2 | 0 | +0.256 | +0.529 | +0.606 | -0.128 | -0.015 | -0.159 | -0.114 |
| -160, n 2.2 | -0.210 | **+0.103** | +0.387 | +0.493 | -0.058 | +0.058 | -0.087 | -0.042 |
| -157, n 2.45 | 0 | > 0.57 | > 0.57 | > 0.57 | -0.128 | -0.015 | -0.159 | -0.114 |
| -157, n 2.45 | -0.210 | +0.484 | | | -0.058 | +0.058 | -0.087 | -0.042 |
| -157, n 2.45 | +0.264 | > 0.48 | | | **-0.214** | -0.106 | **-0.249** | -0.204 |

Guards are unchanged by the phase:
- 203: 0.263 nominal, 0.347 at e-, 0.158 at e+ (kstop's values).
- 139: 0.072.
- 237 (hub K -2.65, crank -9.4), 205 and 316 remain contacts.

**Gate verdicts:**
- (a) PASS. The notch floor is at F_K+6.0, 1.25 mm over the groove top. Groove, thread and access bore are untouched.
- (b) PASS, but tight. Wall over the MR117 is 2.05 at n 2.45. A deeper phase needs n > 2.5, so beta -157 is the edge.
- (c) PASS. dK_lim is 46.0 at beta -157, and the J2 dowel moves 46.35 -> 45.75.
- (d) PASS for the drive parts at beta -157. Beta -160 fails at the e- corner (0.103).
- (d) NOT MET for 264 as a whole: hub 2 and ring2 remain binders.
- (e) Unchanged from kstop. The +0.1 / +0.2 probes still flip 203 and 139; that needs kstop's combined cell.

**What this teaches (new knowledge):** at 264 the drive layer (nose boss, horn, crank, plate) can be cleared by phase
alone. This needs a 2.2-2.45 mm notch, and the notch is legal because it sits in link 1b's boss above stop A, not in
the bearing seat. With the drive cleared, the pose is decided by hub 2's upper wall and the stage-1 ring lip on the
wall side of the dwell play (e+). The sided play costs 0.09-0.13 mm per binder there. The flats are therefore no longer
optional: hub 2 needs >= 0.41 mm at az ~124, and ring2 needs >= 0.45 mm.

## Next (to finish the screen)
1. Port conecut-h2facet's planar hub-2 flat onto this chain (its kstop cell table read +0.26..+0.37 at 264).
2. Add a ring2 lip relief f2 0.45-0.5 mm, sampled as a solid, with RC_MIN as a cut.
3. Re-run the guard at the three play corners and the +0.1 / +0.2 probes.
4. If 264 >= 0.2 at every corner, run the full frozen exact Bench(110,360) sided wears with dowel 45.75, then
   CMA over (beta -158..-156, n, a0 / a1, f, f2) to the convergence gate.

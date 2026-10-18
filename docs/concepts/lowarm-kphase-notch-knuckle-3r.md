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

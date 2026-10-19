# distal-cband-sq95-relay-4r: distal C-band relay at s 0.70 on the knee-less O20 3R (round 401 K1, lens C)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Read the strap as the part that decides the row, not the ring. A ~220 mm bar from hub 3 to s 0.70 runs past the
     deltoid bunching at the top and into the across-body torso zone at the bottom; the ring at s 0.70 is the easy part
     (the arm is round there). So the strap gate goes first and its losses are attributed per station along the strap.
   - Separate the band's two jobs: the underside follows the skin per (azimuth, width) while the race top is ONE surface
     of revolution about the relay axis. The carriage rides the race, so the carriage height over skin is set by the
     WORST skin per azimuth over all poses, not by the median. Price that with the race quantile as a design variable
     (q 1 = no in-sample band contact but a floating carriage; q < 1 = carriage in band, some poses lost as contacts).
   - Fit the band per POSE, not per ray: a pose with other skin (torso, forearm) over the band is lost as a whole; letting
     its clean rays still set the race max floats the carriage for everyone.
   - The strap's first 10 mm is hub 3's lower plate: model the strap from the plate rim, with its underside never below
     its own fitted requirement (a joggle onto the plate where the deltoid stands proud).
2. **The rawest material.** The posed skin itself through B.dist / K.requirement (exact signed distance of every metal
   sample, rays marched from the relay axis per (psi, w) at the station and from GH along the strap); the relayed
   humerus frames from the least-phi solve on the whole archive; the lead's own fitted chain metal (conecut CC model
   samples, frozen). Not the req60 / band.py digests (one 6-mm slice about the GH-elbow line, no strap, no link metal).
3. **The specific methods and tools.** insertion-cband-relay-4r.py's ideal + J4 hardware machinery (imported, not
   copied; it sits on kfree-armarc-relay-4r.py lead_eval: K welded through the |dK| <= 0.1 deg gate, drive stripped,
   knee-side samples dropped), with this row's station, axis, race arc and sampling radius; the frozen protocol (fit on
   Bench(60,160) fast, wear exact on Bench(110,360)); the th fold margin in the one metric; analytic beam theory for the
   strap deflection (12 x 3 Ti-6Al-4V, E 114 GPa, cantilever from hub 3).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, exact path on
   Bench(110,360)), the judge's pre-registered gates (strap gate; ideal > 14.0; hardware > 17.0), the round's adversarial
   verifier and the alignment auditor, and the red-team pose list below (deep across-body IR over the posterolateral
   distal arm, abduction / IR at the strap's hub end, the race's worst azimuth).

## Verdict

**DEAD at the judge's pre-registered gates.** The ideal bound passes, but the strap gate and the hardware kill both fire.

- **Ideal bound passes.** No J4 metal, frozen exact Bench(110,360): **12.40** (score 95.49), against the 14.0 kill.
- **Hardware kill fires.** Every J4 part sampled, frozen exact Bench(110,360): **41.15** (score 85.04) at the spec cell and
  **35.48** (score 87.10) at the sweep's best cell, against the 17.0 kill.
- **Strap gate fires on two of its three items.** See step 0.

**The measured limiter is the torso over the distal arm.**
- At s 0.70, about 9-10 % of all poses put torso (or other) skin across the whole race arc (psi -58..+28), 6-14 mm deep. The
  deep across-body IR poses (plane 105-150, elev 0-60, axial -45..-165) do this. So does the hanging-ER corner at the
  race's anterior end.
- That costs 44 poses on Bench(110,360): strap 24, band 20.
- No race parameter moves them: psi0, s, q, hb, out_mm and the axis centre were all swept.
- The lead takes these poses only because BOTTOM is unscored.

## Step 0: the strap gate (judge's re-registered kill, frozen PHI-0 fit, Bench(60,160))

**Strap model.** 12 x 3 Ti-6Al-4V, 220 mm.
- It runs from hub 3's lower-plate rim to the carriage top, along the great circle about GH.
- Its underside sits at the q 1 requirement along GH rays, with no outlier cut, and is never below that requirement
  away from the 10 mm end ramps.
- Every sample is worn exact.

| gate item (kill if) | measured (q_band 0.95 build) | verdict |
|---|---|---|
| strap own in-band on the hardware-taken clip frames (< 0.85) | **0.828** (ib10 0.58; p5 / 50 / 95 = 4.1 / 9.2 / 33.0 mm on Bench(110,360)) | **fires** |
| strap + band torso / other-skin losses on Bench(60,160) (> 11; "8 ws + 3 clip measured") | strap **9 ws + 3 clip = 12**, band 9 + 2 = 11, so **23** on the literal strap + band reading | **fires** (strap-only reading: 12 > 11) |
| deflection at the carriage under 3 N (> 1 mm) | 0.217 mm (strong axis: the relay load is tangential, in the strap's width direction). The weak axis reads 3.47 mm, but the wheels' radial capture reacts that load, not the strap. Twist 0.05 deg | passes |

**Bench(110,360) exact.** Strap losses 19 ws + 5 clip; band 16 ws + 4 clip.
- Same rate as the fit bench (9.4 % vs 10.4 %), so the losses generalise. They are not fit-set artefacts.

## Step 1: the ideal bound (no J4 metal; knee-less readings of the lead-quality chain)

**Chain.** conecut-knee-knuckle-3r's own fitted metal, frozen.
- K welded through the |dK| <= 0.1 deg gate; drive stripped; knee-side samples dropped.
- J3 re-aim wdir(95, -8.2) with b3 0, asserted in the fitted model.
- psi2 -45, giving a1 / a2 = 37.55 / 67.34.

**Relay.** Least phi in [0, 60] about raxis(2.74, -116.6) = unit(10, 234, 5), sgn +1 (lateral turns toward anterior).

| bench | gap | reach | follow | ib14 | ib10 | contact (n, depth sum / max mm) | overhead | near-1 / near-2 |
|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast (IN-SAMPLE: the metal's fit set, not a claim) | 4.65 | 0.888 | 0.950 | 0.922 | 0.500 | 0.034 (7, 41.9 / 9.0) | 5/12 | 7.97 / 13.53 |
| **Bench(110,360) exact, frozen** | **12.40** | **0.839** (302/360) | 0.936 | 0.921 | 0.507 | 0.049 (21, 121.2 / 13.6) | **11/28** | 15.99 / 32.20 |

**Where the ideal loses on Bench(110,360) ws.**
- **Fold 33.** No welded solution within PHI 60.
- **Contact 14.** Hub 2 is buried under the acromion at relayed stretched poses: 10 poses, plane -15..60, elev 90-150, to
  13.6 mm. The welded hub K accounts for 2 more.
- **Parts 6.**
- **J3 stop 5.**
- **Overhead clips.** 7 overhead clip frames (plane 30, elev 138-150, axial -57..-60) are contacts at 4-9.4 mm. That is
  why follow is 0.936.

**Ideal-reading checks.**
- **th margin.** Minimum 5.001 deg on every taken pose. The window is [29.79, 104.89], with 0 taken poses below 5.
- **Phi.** Maximum 59.6 deg. 89 ws poses are relayed; 76 of them are taken.
- **Versus the insertion station.** The insertion station's ideal read 16.86 (PHI 45, tilt 8.75). This axis at PHI 60
  buys 4.5 points: reach 0.792 -> 0.839, overhead 7 -> 11/28.
- **T5 contact depth.** 121.2 mm over 21 poses, against the lead's 20.24 / 4. The relayed hub-2 burials are deep, so the
  ideal itself would carry the auditor's depth WATCH.

## Step 2: the J4 hardware (every part sampled at its real envelope)

**Parts.**
- **Band.** 22 x 3 17-4PH on a 26-wide saddle at s 0.70 (227.8 mm along the axis). Its underside is 2D-contoured per
  (psi, w) at q_band of the fit poses. A fit pose with other skin more than 12 mm over the median on ANY band ray leaves
  the fit whole, and is then lost in the wear.
- **Race.** A surface of revolution R(w) = max_psi underside + 3: 60 / 63 / 66 mm.
- **Carriage.** 2.5 mm plate at R + 0.5, 20 deg x 34 mm.
- **Wheels.** 4 blocks of 8 x 8 x 3 at the band edges, 14 deg apart.
- **Strap.** As in step 0.
- **Sampling.** 2 mm, with r_ref 60 for the race.

| build | bench | gap | reach | follow | ib14 | contact (n) | overhead | carriage ib14 / p5-50-95 mm |
|---|---|---|---|---|---|---|---|---|
| q_band 0.95, psi0 -45 | Bench(60,160) fast (in-sample) | 35.39 | 0.775 | 0.867 | 0.934 | 0.146 (30) | 5/12 | 0.999 / 6.9-8.8-11.5 |
| q_band 0.95, psi0 -40 | Bench(60,160) fast | 34.29 | 0.781 | 0.867 | 0.938 | 0.141 | 5/12 | 1.0 |
| **sweep best**: q_band 0.96, psi0 -40, s 0.72, PHI 55, raxis(1.888, -90), hb 2.5 | Bench(60,160) fast (in-sample) | 29.56 | 0.781 | 0.900 | 0.929 | 0.127 | 5/12 | 1.0 |
| q_band 1 (race 71-74 mm: the carriage floats) | Bench(60,160) fast | 51.55 | 0.775 | 0.900 | 0.695 | 0.136 | 5/12 | 0.007 / 15.9-18.1-20.3 |
| **q_band 0.95, psi0 -45** | **Bench(110,360) exact, frozen** | **41.15** | 0.739 (266/360) | 0.855 | 0.932 | 0.155 (66, 754 mm / 42.7) | 11/28 | 1.0 / 6.9-8.7-11.5 |
| **sweep best (the row's reading)** | **Bench(110,360) exact, frozen** | **35.48** | 0.753 (271/360) | 0.873 | 0.932 | 0.130 (55, 635 mm / 42.0) | 11/28 | 0.999 / 6.8-8.6-11.1 |

**Hardware loss attribution on Bench(110,360).**
- **Over the ideal.** The hardware costs 28.75 points: contact +10.6, reach +10.0 (36 ws: strap 19, band 16,
  carriage 1), follow +8.1 (clip frames lost to the same contacts).
- **In-band improves.** 0.921 -> 0.932, because the carriage and band sit in band at 7-12 mm.
- **Contact depth.** Torso contacts reach 13-43 mm.

**The race quantile trade.**
- q 1 clears every fit pose, but the race must clear the worst skin per azimuth (71-74 mm), so the carriage floats
  16-20 mm (ib14 0.007).
- q 0.95 puts the carriage in band (1.00), but its underside meets the 5 % bulges.
- Neither touches the torso losses, which run across the WHOLE arc.

**The sweep-best cell.**
- **Ideal (no J4 metal).** PHI 55 about raxis(1.888, -90) reads 13.56 frozen exact: reach 0.828, follow 0.936, 21
  contacts / 113.5 mm, overhead 11/28.
- **Hardware.** 35.48: J4 costs 21.9 points (contact +8.1, reach +7.5, follow +6.4).
- **Strap gate on Bench(110,360).** Strap in-band 0.830; losses strap 16 ws + 4 clip, band 11 + 3.

## Sweep and convergence gate (Bench(60,160) fast, hardware readings; local, farm closed)

**Sweep.** 39 entries in order: 11 SUPERSEDED by the modelling fixes below (10 fast, plus the first Bench(110,360)
hardware read; that read's ideal stands), 26 valid fast hardware cells, and 2 valid Bench(110,360) reads.

**Ranges swept.**
- q_band 0.95-0.99
- psi0 -50 / -45 / -40 / -35 / -30
- station s 0.70 / 0.72 / 0.75 / 0.78 / 0.80 / 0.82
- PHI 55 / 60
- axis centre 0-5 mm medial x 7.5-12.5 mm posterior (tilt 1.9-3.2)
- carriage 20 / 24 deg
- band t (hb) 2.5 / 3
- band outlier cut 12 / 15 mm
- psi2 -45 / -40 / -36.5 (first sweep only)

**Gate.** On the 26 valid cells: gain over the second half 0.156, over the last third 0.0, top-5 spread 0.156 score
points. **It PASSES.**

**What the sweep shows.**
- **Best in-sample cell.** 29.56, which is 12.6 points over the 17.0 kill on the metal's own fit set.
- **s >= 0.78 is worse.** Elbow-flexion band losses grow: clip 5 -> 17 at s 0.82, 63.24.
- **psi0.** -35 / -30 move the race's anterior end into more hanging-ER contact. -50 lengthens the strap's posterior
  route: strap losses 17-21.

## Modelling fixes made here (and measured reasons; the insertion row's machinery is imported, not edited)

1. **Band fitted per POSE, not per ray (pose_cut).** With the per-ray +15 mm cut, a pose with torso over part of the band
   still set the race max with its clean rays, and the race floated to 74-76 mm.
2. **Strap starts at hub 3's plate rim (strap_rim 10 mm).** The insertion row's ramp to the plate centre's underside put
   27 of 38 fit-bench strap contacts on the strap's first row (0.1-1.6 mm), inside the hub's footprint, where hub 3's own
   samples clear.
3. **Strap march end t1 300 (t1_strap).** K.requirement's default t1 of 220 mm left the strap's distal ~20 mm (GH
   distance 220-240 mm) unfitted: inf fell back to the straight radius interpolation. Neighbouring sweep cells jumped from
   12 to 49 strap losses, and q_band 0.9 put the strap through the arm on every pose. All entries before the fix are
   marked SUPERSEDED in the sweep. **This is a kit pitfall for any part more than 220 mm from GH.**
4. **Strap floor only away from the end ramps.** Flooring the end rows lifted the strap end up to 276 mm, off the
   carriage top at 239 mm. The strap must reach the carriage.

## Red team (own best config)

- **The pose that jams.** No J4 jams (0 poses with strap, carriage or wheels within 1 mm of non-adjacent chain metal).
- **The point that pinches.** The race's anterior end (psi +24..+28) meets the arm at 7.1 mm at hanging ER (elev 0, axial
  +60..+105: plane -15, 30, 135, 150). The strap's carriage end meets the torso at 13-43 mm at across-body IR.
- **The optimistic number.**
  - The fast numbers (4.65 ideal, 34-35 hardware) are in-sample: the metal is fitted on those poses.
  - The frozen exact Bench(110,360) reading is the claim bench. The held-out set was never used.
  - The continuity flood was not run: the row is dead before it matters, and the flood can only drop relayed poses.
  - The ideal's 12.40 carries 121 mm of contact depth.
- **Shoulder slip.** This is the standing price of every rigid-cuff spherical chain: misfit p95 4.83 / max 5.14 mm at
  3 mm GH offset, about 6.4 / 6.9 mm at the R10 4 mm slip. It is reported, not scored; this build assumes a 3 mm
  closed-cell liner under the saddle.
- **Follow.** 0.936 ideal, against the 0.95 the lead note flagged. The hardware reads 0.855.

## New knowledge

1. **The distal one-sided relay is the best knee-less ideal on file.** The knee-less re-aimed O20 3R with an ideal
   one-sided relay PHI 60 about the near-long distal axis raxis(2.74, -116.6) reads 12.40 frozen exact on Bench(110,360)
   (reach 0.839, overhead 11/28). The relay ceiling with the knee's b3 is 10.22 at PHI 75, so knee-less at PHI 60 sits
   2.2 points behind it. **The kinematics are not the problem; the guide's metal is.**
2. **An arm-fixed J4 guide at s 0.70 is lost to the torso on ~10 % of poses, whatever its race.** The lost poses are deep
   across-body IR (plane 105-150, elev 0-60, axial -45..-165) and the hanging-ER corner of the anterior end. The skin
   covers the whole posterolateral-to-anterolateral arc, 6-14 mm deep on the band and up to 43 mm at the strap's carriage
   end. That costs about 29 points over the ideal (contact ~11, reach ~10, follow ~8).
   - Both C-band stations are now dead for opposite reasons. At the insertion (s 0.30) the skin swings 6-12 mm against
     the humerus frame; at s 0.70 the torso overlies the arm.
   - **A J4 guide that is not on the arm surface at all is the open lever** (see the open levers in ROUNDS).
3. **A rigid strap cannot follow the arm.** A rigid 220 mm strap along the arm reads in-band 0.83, because it must clear
   the highest skin it ever passes over: p95 33 mm at its carriage end.

## Audit (2026-10-19, death auditor)

**Verdict: the death STANDS.** The hardware kill (> 17.0) fires under every correction tried. Measured reason in one
line: the J4 losses are real torso / forearm penetrations at the deep across-body IR and hanging-ER poses; forgiving the
rig's own self-intersection under the metal and repairing the strap's float leave the in-sample hardware at 27.3-29.6,
10+ points over the kill on the metal's own fit set.

- **Convergence gate.** Re-read from the sweep file: 26 valid cells, gain 0.156 over the second half, 0.0 over the last
  third, top-5 spread 0.156. It passes, though the sweep is a coarse grid rather than CMA. The kill does not rest on it.
- **Reproduction.** The sweep-best hardware cell reads 29.56 on Bench(60,160) fast, exactly as entry k 28 (reach 0.7812,
  follow 0.900, ib14 0.9291, ib10 0.7646, contact 0.1268, 26 contacts). Its ideal reads 5.29. The Bench(110,360) exact
  claim of 35.48 was not re-run, because the box load is 12 on 4 cores.
- **Is the "torso over the arm" the rig's self-intersection?** REQUIREMENTS R2 notes that the rig has no soft tissue:
  its arm passes into its chest. The bench's winding-number sign counts that overlap as inside.
  - The test: for every penetrating J4 sample, take the arm-skin vertex under it (skin vertices rigid in the humerus
    frame), offset it 1 mm outward and check whether it lies inside another body part.
  - Of the 19 ideal-taken poses the J4 metal loses on the fit bench, 13 are mostly self-intersection under the metal and
    3 wholly.
  - Forgiving every self-intersecting sample (the R2 attributable-depth idea; a MEASUREMENT change, not a design change)
    moves the hardware from 29.56 to 27.34 (contacts 26 -> 24, reach 0.781 -> 0.794).
  - 17 of the 19 poses keep real penetration. The strap stands above the arm with torso skin in the gap between, and the
    race's anterior end sits at -6.7 mm in the hanging-ER poses at elbow flexion 90.
- **The strap's float is a fit artefact, but it does not matter to the gap.**
  - The row ran the strap with an effectively absent outlier cut (out_strap 80). Cutting it at 12 or 25 mm lifts the
    strap's own in-band from 0.83 to 0.94 / 0.93 (p95 30 -> 14.5 / 15.1 mm). Strap-gate item 1 then PASSES.
  - Strap-gate item 2 still sits at or over 11 (strap 11 + 2 / 10 + 2).
  - The hardware gap does not move (30.67 / 29.56).
  - The kill does not depend on the strap's in-band. The poses are lost to contact either way.
- **Out-of-date refutation line.** The template's line ("within 10 of 68.93 on Bench(60,160)") is out of date: this row
  is far better than the old champion. The death is judged at the round-401 pre-registered gate, and nothing found
  brings the hardware anywhere near 17.
- **What happens next.** The open lever stands as the row wrote it: a J4 guide that is NOT on the distal arm surface. A
  bench issue is flagged for the lead. The concept bench counts the rig's self-intersection as contact, while R2 forgives
  it. Here that costs ~2.2 points, which is small but systematic against any distal arm metal.

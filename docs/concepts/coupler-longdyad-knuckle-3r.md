# coupler-longdyad-knuckle-3r - hub-2 lobe + crank on dR + spherical-4R coupler driving the slaved knuckle K

## Deeper version (answered before the work)

1. **What a top mechanism designer would do that the spec does not ask for.** Before pricing PA tables, ask *where the
   crank tip and the coupler physically go relative to the skin*. The spec's stage 2 swings a 30 mm arm 27-37 deg about
   an axis on link 1b and sends a 35-45 mm coupler across to hub K; every PA-legal geometry points the arm SIDEWAYS
   (t1 = +-55..110 deg off the dR -> K line), i.e. off link 1b's skin-fitted corridor onto the deltoid / the anterior
   shoulder. The chain's own links are levelled to clear the highest skin they pass over (the proximity atlas rule);
   a drive that lives beside them must obey the same rule, so the honest test is (a) the drive at link 1b's level
   (what the proposer priced: contacts) and (b) the drive SKIN-FITTED like the chain (raise each section until it
   clears every fit pose by 1 mm: contacts gone, in-band priced). If (b) costs > 14 mm of lift somewhere the drive
   cannot be both clear and in band, and that is the verdict. Second: re-synthesise stage 2 on THIS fit's u2 / uK / dR
   (the seed pins came from another fit), with the horn eye clear of hub K's O20 + 1 mm (r_h >= 15, a3 >= 14.7 - the
   spec's 13.5 floor puts the coupler eye 0.07-0.9 mm from hub K's housing). Third: the lobe skirt (12.8) caps the
   crank angle at 32.6 deg (s_nose 4) - the stage-1 wall the round-11 plan predicts; s_nose 3.5 lifts it to 37 deg.
2. **Rawest material.** The posed skin itself through the bench's grid distance (every drive sample is a rigid-part
   sample priced pooled by the bench, and the skin-fit raise is sphere-traced against the same distance field on the
   fit bench's poses), the motion clips of Bench(60,160) / Bench(110,360) and the 952 held-out poses, the model's own
   link 1b / hub samples (levels, layers), the proposer's own scratch harness (coupler_lens/metal.py) as a cross-check.
3. **Methods and tools.** Spherical 4R closure by continuation (all axes through GH) with PA at both pins (the dogring
   row's solver, reused); per-fit re-synthesis (12k + 8k random pin sets, 4R table PA <= 42 and crank monotone to
   K >= 77); the parents' per-t law gates plus stage 1 on the real follower (lobe radius, lobe PA <= 42 - atan(mu));
   swept clearances in link 1b's frame (drive range dK_lim, stop B there); per-pose collide with the family's 1 mm
   rule; the CPU farm for the coarse sweep (256) and ONE CMA batch (4 starts); frozen exact Bench(110,360) + held out.
4. **What shows the number is right, other than me.** tools/concept_bench.py (pooled in-band over all metal points,
   contact on metal < 0), the family's frozen-exact protocol (fit fast, freeze, wear on Bench(110,360) exact), the
   held-out bench, the K-open drive-contact count (the lead note's kill rule) read on the same bench distances, and the
   round-11 verifier / red team (rest, overhead elev >= 140, across the body, behind the back).

(Verdict, numbers and red team below - written after the measurements.)

## Verdict (dead, 2026-10-17 12:24 UTC) - killed by the lead note's hard kill

**No configuration passes the kill rule.** 1540 configurations (256 coarse + ONE CMA batch, 4 starts x 321, CPU farm,
objective = 1 mm near-touch gap + 2 x K-open drive contacts): none has the drive's pooled in-band >= 0.755 (gate B, read
on the bench's own distances over taken clip frames) together with <= 2 K-open drive contacts.

Frozen pick `{"cr_a1": 34.0, "cr_t1": 24.94, "cr_a3": 13.74, "cr_t3": -165.93, "kK": 3.016, "smhi": 12.34, "s_nose": 4.04,
"r_base": 11.2, "cr_zr": 8.0, "dl_lift": 0, "dr_hl": 6.58, "cr_tilt": 17.30, "dl_a": 1, "dl_h": 1, "bk1": 32, "bk2": 48, "a1max": 74.5}`:

| bench | gap | score | reach | follow | ib14 | ib10 | contact | overhead | drive in-band (crank / coupler / horn) | K-open drive contacts |
|---|---|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast (fit) | 18.58 | 93.24 | 0.781 | 1.0 | 0.854 | - | 0.021 | - | 0.72 / 0.63 / 0.79 | 1 |
| **Bench(110,360) exact, frozen** | **23.87** | **91.32** | 0.739 (266/360) | 1.0 | 0.856 | 0.498 | 0.033 (13 poses, 47.7 mm summed, max 16.9) | 4/28 | 0.73 / 0.63 / 0.82 = 0.70 | 1 (+1 < 1 mm) |
| held out, CMA-C best (frozen 25.78) | 29.73 | 89.19 | 0.703 | 0.955 | 0.853 | 0.493 | 0.053 (48) | 12/71 | 0.70 | 11 |
| lead slipper-nose (same protocol) | 18.49 / held 23.45 | 93.28 | 0.725 | 1.0 | 0.896 | | 0.005 | 8/28 | | |

Other frozen exact readings: C1 25.78, C2 26.59, D1 (skin-fitted drive) 27.39 (held 32.36), far side B1 30.76 / A1 31.18
(0 K-open contacts, drive in-band 0.29-0.31, coupler 0.0), coarse best 33.39 (held 37.65). Near-touch: min metal 0.14 mm,
near1 29.42. Strict fold reading passes everywhere (own-state th margin 5.0-6.9, none < 5).

## The measured limiter

* **The drive lives over the deltoid.** Re-synthesised on this fit's own u2 / uK / dR (132 + 81 PA-legal geometries to
  K >= 77), every stage 2 that reaches the stroke points the crank arm 55-110 deg sideways of the dR -> K line (two
  families: t1 +45..80, the spec's, and t1 -85..-110 on the far side). Skin-fitting the drive like the chain (sphere-
  traced raise to clear every fit pose by 1 mm) needs **+33 mm** at the arm tip for the spec's seed - i.e. the skin under
  the swept tip rises 33 mm above link 1b's level somewhere in the workspace.
* **At link 1b's level the spec side touches** (fit bench, config k 169: 58 drive contacts, crank in 49, 34 of them with
  K CLOSED - the parked crank under internal rotation -75..-105 deg - depth up to 14.7 mm; spec-side coarse configs: min
  10, median 26 K-open drive contacts). **Raised or on the far side it leaves the band** (<= 2 K-open contacts: drive in-
  band never above 0.56 in the coarse sweep; far-side frozen: coupler 0.0 in band).
* **The CMA's escape gives up the stroke.** It swings the arm back toward link 1b (t1 +25), lifts it to the clamp (cr_zr 8)
  and the horn +6.6; PA-legal 4R tables there end at dK 60-65 (vs 77-88 sideways), dK taken 52 on the frozen bench, so
  reach is 266/360 (lead 261) - the long K dyad's window is not used - while the coupler still sits 0.63 in band and
  13 frozen contacts appear (coupler 6, crank 4, horn 2; elev-165 and across-body poses).
* **Stage-1 wall:** the 12.8 mm skirt caps the crank at 32.6 deg (s_nose 4.0); with g ~2.0 on this fit (not the proposer's
  2.39, which came from another fit) the lobe alone stops the law at dK ~65 (law end 'skirt' on most configs).
* **Spec corrections (stated):** horn arc a3 >= 14.7 (the spec's 13.5 floor puts the coupler eye 0.07-0.9 mm from hub K's
  O20 housing); the seed pins do not close PA-legally on this fit (re-synthesised); the sidecar parent's 11.75 crest rule
  is replaced by the spec's 12.8 skirt gated in the law (the uploaded build of the coarse sweep still carried the old flag:
  plain metrics valid, 'honest' false on law-skirt configs).

## Red team (own)

* **Optimistic number:** fast 18.58 -> frozen exact 23.87 (+5.3, the family's usual inflation); held out of the CMA best
  29.73 with 11 K-open drive contacts (bench 2): the K-open contacts the kill rule counts are under-sampled by Bench(110,360).
* **Pinch point:** the coupler at elev 165 and across-body poses (frozen contacts: coupler in 6 of 13, crank 4, horn 2;
  deepest 16.9 mm). Min metal 0.14 mm on taken poses.
* **Jam:** none found kinematically (4R continuation without branch change over the table; PA <= 42 at both pins;
  lobe PA <= 37.03 = 42 - atan(0.087)); the sliding nose still carries the lead's M5 / R17 caveat at 60-80 N.
* **Measurement vs design:** no bench / metric change; gate B is read on the bench's pooled drive in-band, not the parking
  harness (stated).

## Convergence gate (score points)

Full sweep in run order: gain over the 2nd half 2.15, over the last third 1.45, top-5 spread 0.39 - **not passed**; CMA
runs A / B passed (0.27 / 0.06 / 0.06; 0.24 / 0.15 / 0.15), C (spec side) 2.93 / 0.00 / 0.77 and D (skin-fit) 0.99 /
0.53 / 0.26 not passed. The row is closed by the lead note's hard kill (one CMA batch; gate B < 0.755 or > 2 K-open drive
contacts), which every configuration fails, not by convergence.

## What predicts beyond this row

Any K drive whose input crank sits on link 1b beside hub 2 and whose spherical 4R reaches >= 75 deg of K with PA <= 42
puts its arm 55-110 deg sideways of link 1b; there the skin rises up to ~33 mm above link 1b's skin-fitted level, so the
drive is either in contact or off band. Bringing the arm back over link 1b's corridor (t1 ~25) keeps it in band only by
shortening the PA-legal stroke to 60-65 deg - the stroke the lead already has. The long K dyad's window needs a drive
that stays INSIDE link 1b's corridor (coaxial on u2 / uK, or stacked along link 1b), not beside it.

# weldk-overstrap-pinknee-3r - welded-K crossover pin-knee 3R (cx 0)

Round 301 (O1, overhead track), lens drive-free-cone taken to its limit. Model:
`docs/concepts/models/weldk-overstrap-pinknee-3r.py` (loads the H1 model `skin-normal-3r-pin-knee.py` unchanged and
changes only the J3 stack order and the E-strap / link-2 rule). Sweep: `docs/concepts/sweeps/weldk-overstrap-pinknee-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Price the crossover where it is born:
   link 2 rotates about J3 relative to member 3, so the E strap that leaves hub 3 above link 2 must clear link 2's
   swept annulus *in plan view*, not only the H1-style "nearest point minus 3 mm" kd test (that test reads up to
   +0.3 mm optimistic on a 2 mm grid for two stacked parallel plates). The model makes the E underside a function of
   the measured link-2 top over every kept fit pose (plan-view overlap, +0.15 mm), so the in-band cost of the 3.15 mm
   lift is computed, not assumed. (b) Run the same seats with H1's stack order (`over=0`) as the control, so the
   crossover's own worth is measured separately from the J3 re-aim. (c) Put the E direction (phiE) in the sweep: if
   link 2's relative sweep leaves a free sector, an E strap pointing into it never crosses link 2 and pays nothing.
2. **Rawest material.** The posed skin itself (concept_bench exact signed distance on the posed body mesh, CB_EXACT=1
   for the claim), the motion clips at 10 fps for continuity of q1..q3, pin a and pin b, and the workspace poses of
   Bench(110,360) (28 overhead ws poses, elev >= 140) - not the ghost's digest. The ghost (dfc2/park_wk.py) is
   used only as the prior, and the judge's H1 control (ghost +13 ws / +5 overhead vs verified H1) as its error bar.
3. **Methods and tools.** H1's exact closed-form IK + two-circle knee closure, seed VModel honesty rules (closure,
   continuity incl. the knee branch, jam rule, 1 mm non-adjacent / 0.15 mm adjacent clearances), sphere-traced skin
   heights on 1 pt / 4 mm2 samples, <= 60 deg ramps, O20 v5 hubs, MR63ZZ knee pairs (stk 6.0); tools/concept_sweep.py
   on Bench(60,160) fast for the search; the frozen-shape protocol (fit 60/160 fast, wear on 110/360 exact) for the
   claim; the 1 / 2 mm near-touch readings and the overhead split from H1's audit().
4. **What shows the number is right, other than me.** The bench (the outside judge), the `over=0` control at the same
   seats, the round-3 frozen exact protocol that every verified row uses (H1 27.20 through the same code path), and a
   red-team pose list (the lead's 28 overhead poses by index, the three 1-2 mm shell poses 205 / 235 / 262, the drive
   contact poses 237 / 264, rest / across / behind groups) for the adversarial verifier.

## Results (2026-10-19, round 301 screen; local CPU only, farm closed)

**Verdict: fails every gate the judge set for it.** Best fast fit **39.09** on Bench(60,160) (CMA, 191 configurations,
not converged; params in the row), worn FROZEN on Bench(110,360) exact: **45.96** (score 83.3; reach 0.6306, follow
0.9273, ib14 0.7415, ib10 0.4473, contact 0.009) against the kill line 27.20 (H1) and the pass line 26.0; follow < 0.95
(the judge's second kill condition); step-0 E-strap in-band **0.38-0.66 < 0.80** in every configuration that takes
poses at the spec's J3 station (0.48 at the best). Overhead (elev >= 140, ws) **7/28** (the lead 8/28, H1 5/28), every
one in the 1-2.6 mm shell or below (0.07, 1.04, 1.13, 1.18, 1.69, 1.74, 2.59 mm); elev 90-140 band 37/85 (lead 39/85).
Near-touch: min 0.07 mm (ws 345, plane 75 / elev 165 / axial -75), gap with metal < 1 mm as contact 53.04, < 2 mm 90.67
(49 poses in the 2 mm shell). Min th margin over taken poses 5.262 deg. Not taken: fold 104, part jams 34 (E-over-L2
stacked 18 - every cone pose 209 / 235 / 236 / 262 / 263 / 292 -, L1-L2 11, knee-E 5), contact 3. Its CMA neighbour
(fast 39.93) reads 49.07 frozen exact (overhead 6/28, contact 0.0457: the cone poses are contacts there, see below).
Complexity 0.0 (tools/simplicity.py v2.2 --score on the row's mechanism record; the knee is the free cuff_knee block).
0 passive translations. Claim files: the row's `exact_frozen` (best) and `exact_frozen_neighbour`.

### Code check (the model is H1 where it should be)

`over=0` (H1's stack order) at H1's own verified parameters (H-g107-1, stk 5.6815) reproduces H1's fast fit **23.64**
exactly (the rebase's fit_gap 23.64). The crossover alone at H1's seats (`over=1`, same parameters) reads **23.43**
(link 2 in band 0.82 -> 0.84, E unchanged 0.918: at H1's seats the E strap points into link 2's free sector, so the
crossover is free there and passes the step-0 test). The losses below are the spec's seats, not the code.

### What limits it (measured)

1. **Hub 3 at the re-aimed J3 station dives into the bunched deltoid at the cone** (measured on the 39.93 neighbour,
   where the cone poses reach the skin check; at the best they jam first on the E-over-link-2 stack). The J3 re-aim works
   kinematically: the cone poses the lead loses to fold / J3 stop (209, 210, 236, 237, 263, 264, 292) all CLOSE here
   (0 cone folds). But worn frozen they are contacts: hub 3 sits **-17.7 (209), -16.5 (236), -7.9 (237), -9.1 (263),
   -15.4 (292), -25.6 (210)** mm inside the skin (exact distance, frozen shape; `conepart` probe, scratch), hub 1 at
   -0.15..+0.86 mm (acromion top, in the shell), link 2 -0.8..-4.8 mm at 236 / 237 / 292. 235 and 262 (two of the
   ghost's 1-2 mm shell takes) are contacts too: hub 3 -6.4 / -8.0 mm. The ghost's "cone takes at 2.0-7.9 mm" do not
   survive real hub-3 metal at a fitted level (f3 62.2 mm, set by the 60/160 fit sample): to clear the cone hub 3 would
   have to park ~80 mm along its axis, which takes the whole J3 side out of band everywhere else.
2. **Hub 2 parking at the lead's J1 with a1 40.5.** Three pure-abduction poses (elev 105, axial 0, planes 0-30) park
   hub 2 15-27 mm above its median need (81.8 vs median 54.6 mm); H1's greedy drop cannot pay that off (no move of <= 8
   poses improves its proxy). The `dg` pre-drop (dropped poses count as contact) is the design's explicit choice: at the
   best dg ~17 hub 2 parks at 62.5 mm, in band 0.86 (H1 1.0).
3. **The knee lands on falling skin.** At the spec's J3 station every knee placement the search found puts the knee
   stack 15-20 mm off the skin (boss 0.17, pad 0.31, knee link 0.41 in band on Bench(110,360); H1's knee 0.93-1.0):
   in hub 3's plane the deltoid falls away from the station within the knee's reach (lE 30-70 mm), across poses.
   The E strap itself is 0.40 in band (median 14.7 mm). Control at the best configuration with H1's stack order
   (`over=0`): 90.77 (62 E-link-2 jams), E 0.53 - so the crossover costs the E ~0.15 of in-band but is what makes the
   chain buildable at these seats; the E's low band is the station's, not the stack's.
4. Reach: fold 100 of 470 poses (no K: the window ends at a1 + a2 - 5), plus 16 contacts and 20 part jams
   (L1-L2 12, knee-E 6, E-L2 stacked 2).

### What I built (and changed against the spec)

- The spec said "E flat over link 2's reach, then a <= 60 deg ramp". The model instead computes the E underside per
  station from the measured link-2 top in member 3's frame over every kept fit pose (plan-view overlap |y| <= 5 mm,
  |dx| <= 2 mm, +0.15 mm), so the lift is priced, not assumed; collide() replaces H1's kd E-L2 test (optimistic by up
  to ~0.3 mm for stacked plates on a 2 mm grid) by the same plan-view stacked-pair test.
- The crossover exposed a stack conflict H1 never had: E leaves hub 3 3.15 mm higher, so near pin a it rises into the
  knee link that rides over it (H1 relies on E sloping DOWN from the boss). Two honest fixes, both in the model:
  kinv 0 (H1's knee stack; E kept <= zb + tp + RUN - T - ADJ under the knee link footprint, else the boss / knee rise)
  and **kinv 1, the inverted knee stack** (knee link lowest, boss and pad over it, so E stays the upper layer from hub 3
  to pin a - a two-layer design: link 2 and the knee link below, E above). The CMA preferred kinv 1 (40.46 vs 42.83).
- `dg`: explicit pre-drop of poses that park a hub / the knee stack > dg mm above that part's median need.

### Search and convergence (binding gate: NOT met)

~150 configurations on Bench(60,160) fast (2 local processes, nice 10): 4 probes, a 64-config LHS over the spec box
(random knees mostly fail the knee window), a knee-aware LHS (phib from a mid knee angle), then three CMA-ES runs
(kinv 0, kinv 1, kinv 1 restart). Best fast 39.09 (kinv 1). Gate numbers are in the row (`gate`): the search was still
gaining (gate: +1.44 score points over the 2nd half, +0.67 over the last third, top-5 spread 0.33), so by the binding
rule this is **screened, not dead** - but the frozen exact read (45.96) is ~19 points past the
kill line and the measured limiter (hub 3 inside the bunched deltoid at the cone) is geometric, so the recommendation
is to stop here rather than spend the farm on it.

### Red team (my own best)

- The pose that jams: 236 (plane 15, elev 150, axial -30) - the E-over-link-2 stacked pair goes to -1 (jam) while hub 3
  is 16.5 mm in the skin; link 2 / link 1 crossings (L1-L2 12 poses) are the most common jam.
- The point that pinches: ws 118 (plane -90, elev 60, axial 75, behind the back) 0.25 mm; 313 (60 / 120 / -105) 0.42;
  288 (45 / 135 / -60) 0.59; clips 8 / 9 (30 / 150 / -60) 0.97 mm.
- The optimistic number: the fast fit (39.09) - worn frozen exact it is 45.96; and every overhead take sits at
  0.07-2.59 mm (the 2 mm reading is 90.67).
- Held out: not run (the bench claim already fails the kill line; held cannot rescue it and must not be used to tune).

### New knowledge

- A J3 re-aim that opens the abduction cone kinematically is not an overhead lever on its own: the station that opens
  it (wd ~95-99, wa ~7-8, b3 ~0.6-0.67) puts hub 3 on the deltoid where it bunches in elevation 150-165, 8-18 mm deeper
  than the fitted hub-3 level - a hub-3-level wall at the cone, on top of the J1/J2-seat-level wall lens C measured.
  The K-free ghost's cone clearances (2.0-7.9 mm) are not reproduced once hub 3 carries one fitted level.
- The E-strap crossover (inverted J3 stack) is free where the E points into link 2's free sector (H1's seats: 23.64 ->
  23.43 fast); it needs the inverted knee stack (knee link under the boss) to stay buildable when the E arrives high.

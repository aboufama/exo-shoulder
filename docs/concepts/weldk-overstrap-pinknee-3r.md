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

## Results

(written at the end of the screen, below)

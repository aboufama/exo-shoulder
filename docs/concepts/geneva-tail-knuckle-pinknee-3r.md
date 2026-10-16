# geneva-tail-knuckle-pinknee-3r: a one-tooth Geneva tail that slaves the knuckle to q2

Status: screened (round 6). Model: `docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py`. Sweep:
`docs/concepts/sweeps/geneva-tail-knuckle-pinknee-3r.json`. Row: `docs/concepts/rows/geneva-tail-knuckle-pinknee-3r.json`.
Motion preview: `docs/concepts/viz/concepts/geneva-tail-knuckle-pinknee-3r.js`.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Write the drive as the exact spatial contact, not a planar ratio. Every axis passes through GH, so the roller centre
     and the flank both live on the unit sphere. The law is then exact in 3-D: a flank half-plane through K's axis, and the
     roller on a small circle about u2. The pressure angle and the contact radius fall out of the same geometry.
   - Check the passive coordinate's equilibrium, not just the law: could the spring park K off the roller at a smaller
     opening along the pose's self-motion curve? If it can, q2 no longer gives K.
   - Price the swept volume of the rigid tail before tuning anything. A part rigid with link 2 turns about u2 through
     J2's whole range. Its height is set by the highest skin under its whole sweep cone, and by link 1b, which it crosses.
     That surface of revolution is the honest stacking rule.
   - Treat the tail length as a seat variable. L_t is about bk2, so the tail is short only if K sits near J2.
2. **The rawest material.** The posed skins of the bench itself: the signed distance of every tail sample on every pose,
   from the bench's `needed()` trace on the skin and not from a digested atlas. Also the fit clips' frame order for
   continuity, and the workspace poses for reach.
3. **Methods and tools.**
   - A closed-form law on a 0.1-deg q2 grid.
   - Th_law inversion: the J1-J3 angle along the law is independent of the pose, so a stretched pose is solved by
     interpolation.
   - Per-t gates: monotone, rate, pressure angle, tooth extent, stop B and lift-off.
   - The kit-rule B model's checks: closure, continuity, fold margins of 5 deg, every part pair, and the near-touch
     objective.
   - The farm for LHS and CMA. The frozen exact Bench(110,360) for the claim.
4. **What, other than me, shows the number is right.**
   - The bench, with skin distance on every sample.
   - The judge's law-only reproduction: 14.34 fast at LB1 here, against the judge's 13.79-14.34.
   - The red-team pose list: rest, overhead, across the body and behind the back, with the tail-tip skin heights.
   - The verifier harness of minarc B, which this model subclasses unchanged except for the stretched state and the
     tail.

## The mechanism

- minarc B under the kit rule, using the physical q2 stop, the K cap (+6 mm) and the pin knee.
- The stretched J2 stop is replaced by a drive. Link 2's strap continues past hub 2 as a rigid tail of arc L_t, with an
  MR63ZZ roller at its tip.
- One flank fixed to link 1a takes the roller. Past the onset q2hi, which sits at smhi from the fold, the roller turns K
  open by dK(q2). K is never read.
- The folded side has no tooth.
- Count: 0 passive translations. Passive rotations: K (slaved) and the 2 knee pins.

### Exact law

The parameters are:

- **t:** the q2 travel past the onset.
- **p(t) = R(u2, q2hi + s t) p0:** the roller centre, in link 1b's frame.
- **az, p_perp:** the azimuth and perpendicular distance of the roller about uK.

The flank azimuth that keeps the roller tangent is `az_pl = az + s_m asin(rho / |p_perp|)`, and the law is
`dK = -(az_pl(t) - az_pl(0))`.

The tail tip p0 is placed by two variables:

- **d_mm:** the closest approach of the roller to K's axis.
- **psi_c:** the q2 travel at which that closest approach happens.

The side is chosen so that the pushed flank opens K. The flank must be inside the roller's path ("inside", L_t = bk2 - d)
or outside it.

### Gates per t

The valid prefix ends at the q2 dowel, stop B. A t is valid only if all of these hold:

- th rises;
- dq2/dth <= 3.45;
- the pressure angle is <= 45 deg;
- the contact radius is <= 10 mm on the cap (crown) or <= lug_max (beside);
- |dK| <= K's stop B;
- the spring cannot park K off the roller along the self-motion curve.

At LB1 with psi_c 0 (closest approach at the onset), the pressure angle hits 45 at dK 17 deg. With psi_c 6 (a Geneva
entry), dK reaches 56 deg inside 45 deg of pressure angle.

### Tail metal

- **LT** is an 8 x 3 strap on member 2, skin-fitted like every link and counted in band.
- It ramps at 60 deg from hub 2's upper level to a tip floor:
  - crown embodiment: the roller bottom sits at K's cap top + 1 mm, and the strap at + 3 mm above that;
  - beside embodiment (d >= 14 mm): the roller runs beside hub K against a lug on link 1a (lug sampled), and the strap
    sits at link 1a's top + 1 mm.
- The tail is stacked over link 1b by the surface-of-revolution rule. At each angular distance from u2, it clears every
  link-1b point at that distance by 1 mm.
- The roller boss (O8 x 3) hangs below the tip. It is skin-checked and in band.
- Part pairs: LT and the roller against hub 1, K (the cap counts, exempt only while the law says the parts touch), hub 3,
  L1a, L1b, the knee, the pad and E, at >= 1 mm.

## Measurements (Bench(60,160) fast, near-touch objective)

| config | gap | reach | in-band14 | contact | note |
|---|---|---|---|---|---|
| LB1, law only, psi_c 0 | 23.01 | 0.688 | 0.908 | 0.018 | closest approach at the onset: pressure gate at dK 17 |
| LB1, law only, psi_c 6 | **14.34** | 0.794 | 0.900 | 0.037 | reproduces the judge's law-only 13.79-14.34 |
| LB1 + tail, crown (d 7) | 56.48 | 0.700 | 0.848 | 0.162 | tail in band 0.25 (median 20.6 mm), roller 0.04; 30 poses dropped |
| LB1 + tail, beside (d 15) | 39.24 | 0.706 | 0.861 | 0.093 | tail in band 0.15 (23.6 mm), roller 0.10 |

**The decisive unknown (the tail metal) is measured.** At the judge's seats it costs 25-42 points, against the kill
threshold of 4.

The reason is geometric. A tail of L_t ~ 41 deg (~46 mm) rigid with link 2 sweeps a cone of half-angle L_t about u2
through J2's whole range. Its tip passes over skin that needs it 92 mm from GH (the trapezius side), while hub K's base
sits at 55 mm. The tail also has to stack over link 1b, which it crosses.

The sweep below searches the seats where the tail can be short (bk2 small, i.e. K close to J2).

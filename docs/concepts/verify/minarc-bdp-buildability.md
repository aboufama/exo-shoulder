# minarc-stop-knuckle-4r BDp: independent verifier, lens buildability and red team

**Claim under test.** `docs/concepts/rows/minarc-stop-knuckle-4r.json` (`kitrule_*` fields) and
`docs/concepts/minarc-stop-knuckle-4r.md` ("Kit-rule re-optimisation"). The config is BDp: variant B, a physical q2
dowel stop at J2, both J2 stops at the 5-deg J1-J3 margin, and hub K's cap 6 mm taller. The claim is 19.06 frozen
exact on Bench(110,360), which is score 93.07, and 23.24 held out.

**Sources.**
- Harness: `docs/concepts/verify/minarc-bdp-buildability.py`. It imports the model and the claim harness unchanged and
  re-derives the K / q2 closure independently.
- Raw outputs: `.cache/minarc_bdp_build/` (git-ignored).
- Compute: 4 local runs (at most 3 at once), no farm.

## Reproduction (exact, by the claim's own `run()` path)

- **Bench:** worn Bench(110,360) gives 19.06 (reach 0.725, follow 1.0, in-band14 0.8951, contact 0.0107). The fit60
  fast run gives 12.25.
- **Held out:** 23.24 (reach 0.6891).
- Both match the claim to the digit.

## 1. The q2 stop and the K-opening law

- **Real stop, right bodies.** J2's housing rides on link 1b (member 7), and the model's q2 is link 2 relative to
  link 1b about u2. The dowel-in-slot therefore sits between the two bodies J2 connects.
  - Slot: q2 from -24.98 to 100.84 deg, so 125.8 deg of travel. With an O2 dowel at r about 7.75 mm, that is about
    17 mm of arc plus the dowel.
  - It fits the 4.5 mm land between the MR117 outer diameter (r 5.5) and the O20 rim (r 10), inside the 12.25 mm stack.
  - The slot is not sampled separately. It lies inside the hub cylinder, which is sampled as metal (disc, walls,
    crown). The folded stop (q2 100.84) never engages on a taken pose; the taken maximum is 97.96.
- **The law is the physical equilibrium, and it is unique.**
  - Method: an independent scan, parametrised by dK, of every spring equilibrium. An equilibrium is a local minimum of
    |dK| on the self-motion curve at a fixed arm pose, with J2 inside its slot and K between stop A and stop B.
  - Scan resolution: th from 0 to 180 deg in 0.1-deg steps, dK in 0.02-deg steps.
  - Every th has 0 or 1 equilibrium. There are 0 multiple-equilibrium cases, so the state depends only on th (w = Q u3).
    There is no hysteresis and no path dependence.
  - At every pose the model takes, its dK equals the global minimum to within 0.1 deg (0 mismatches).
  - The forced equilibria all sit with J2 on the stretched stop (q2 -24.96 to -24.98).
- **Stop B sits below the claim's own margin (spec issue, costs 0).**
  - The rule cut (effective-dyad margin m3e = 5.0) falls at th 108.5 deg, dK 34.47.
  - The metal physically locks only at th 122.2 deg, where dK reaches stop B at 62.65 of 62.83 and m3e is 2.74 deg.
    The sub-chain margin there is 13.25 deg.
  - So between th 108.5 and 122.2 the device still follows the arm (94 envelope poses), with J2 on its stop and m3e
    falling from 5 to 2.74 deg.
  - The bench drops those poses, so no number is optimistic. But stop B, as specified (a1max 66.16), engages below 5
    deg in the claim's own m3e reading.
  - **Fix:** a1max such that dK at stop B is 34.5 deg (a 35-deg K slot). Bench cost: 0, because every taken pose has dK
    at most 34.29 held out and 33.95 on the bench. It also lowers the spring stress below.

## 2. The spring: 0.3 x 5 mm 1.4310 strip

**Stress.** Bending stress is sigma = 6M / (b t^2), with EI = 0.00217 N.m^2.

| rate (N.m/rad) | strip L (mm) | preload 0.08 N.m | at the bench max dK 33.95 | at stop B, 62.83 as modelled |
|---|---|---|---|---|
| 0.010 | 217 | 1067 MPa | 1146 MPa | 1213 MPa |
| 0.015 | 145 | 1067 MPa | 1185 MPa | 1286 MPa |
| 0.030 (the doc's rate) | 72 | 1067 MPa | 1304 MPa | **1505 MPa** |

- **Against the 1.4310 limits.** For spring-hard strip (EN 10151 +C1700 / +C1900, Rm about 1700-2100 MPa), static
  bending is allowed up to about 0.7-0.8 Rm, roughly 1190-1520 MPa.
  - Buildable at a rate of 0.015 N.m/rad or less (strip 145 mm or longer, 0.85 turns of preload wind) in +C1900.
  - At the doc's 0.03 N.m/rad the strip is over the limit at stop B, which the wearer can reach (section 5).
- **Fit.** 145-217 mm of strip fills 24-36 % of an O16 cap annulus around an O5 arbor, which fits.
- **Cap height is tight.** A 5 mm strip in a 6 mm cap leaves about 0.7 mm for the cover. Spec it as a steel cover.
- **Demand, re-measured on the fitted BDp shape** (`demand` mode). Masses: the lens's member model plus 4 g for the cap
  and strip. The demand is the opening torque along K's self-motion.

| where | poses | gravity 1 g, worst direction | 2 g + seals at 2 mN.m per pair |
|---|---|---|---|
| state A | 1293 | 0.0155 N.m | **0.044 N.m** (0.050 at 3 mN.m per pair) |
| forced | 238 | 0.0077 N.m | 0.023 N.m |
| clip frames | 451 | 0.0112 N.m | 0.031 N.m |

- **Margin.** The 0.08 N.m preload is 1.6-1.8x the worst demand. Only a pessimistic 10 mN.m per sealed pair combined
  with 2 g exceeds it.
- **K on the clips.** K now moves on one clip: Wash opposite shoulder, 8 frames, dK up to 2.19 deg, at most 16.6
  deg/s. On those frames J2 sits on its stop and K is set kinematically by th. The demand there is 0.021 N.m.
- **Verdict on the spring.** It returns K to stop A on every clip, fit and held out. Wave and walking never open K.

## 3. Hub K's 6 mm cap in the worn copies

- **Present in both runs.** In the worn copies on the bench and on the held-out set, `apply_cap` runs on the fit model
  (KModel) and again on the worn copy (Frozen).
- **Modelled as metal.** Crown 18.25 mm, crown samples up to 18.25 mm, and 4 cap contact rings in the worn copy.
- **Never the limiting part.**
  - On every taken overhead pose (elevation 140 or more) the cap is at least 4.08 mm from the skin (held out).
  - Where the cap is inside the skin (bench 264, held-out 534 / 682 / 755), hub K's own wall is deeper still, and the
    pose is already contact.
  - Cost: 0.
- **Not scored by in-band.** The bench's in-band counts skin-facing metal only, never crowns; that is the same
  convention for every design. Hub K stands 18.25 mm above its base, 6 mm prouder than every other hub, and that is not
  scored anywhere.

## 4. DOF: what the user would accept

- **Four revolutes.** The shoulder chain has J1, K, J2 and J3, which is the cap of 4, not the preferred 3.
  - K is passive and spring-held, but it must be sensed. In the forced states J2 reads its stop value, and the arm pose
    is a one-parameter family without K's angle.
  - So MVP1 needs a 4th encoder, and the chain is 4 DOF in the user's count (the round-5 skeptic's ruling stands).
  - The two-pin knee is cuff self-alignment, outside the count. There are 0 passive translations.
- **What it adds.**
  - Two hard stops at J2, one used.
  - Two stops at K: stop A, plus stop B, which should move to 35 deg (section 1).
  - A clock spring in an 18.25 mm tall hub K.
- **How much K is used.** K opens only beyond th 91.8 deg. That is 8 clip frames (one clip, 2.19 deg), and up to 34.3
  deg on workspace poses. The reach K adds is static workspace reach below elevation 140.
  - **Overhead (elevation 140 or more) gains nothing from K.** Every taken overhead pose is in state A, with K closed. The forced overhead poses (bench 316, held-out 820 / 893) are lost to link-2 contact.
- **MVP2.** K is unpowered spring return, so a powered MVP2 cannot drive the arm through the forced region with K.

## 5. Red team

- **The jam: q2 on its stop with K at stop B.**
  - Where: th 122.2 deg. Both dowels are loaded and the arm meets a hard wall.
  - 184 of 1432 envelope poses lie beyond it, and 0 clip frames do (fit or held out; the clip th maximum is 92.8).
  - It is not a trap. The equilibrium is unique, so reversing th retraces the same path.
  - Dowel load if the wearer pushes on the wall: 6 N.m about GH gives about 770 N on an O2 dowel at r 7.75 mm (246 MPa
    shear). At 20 N.m it is about 820 MPa, at the limit. The dowels need the L1 CAD strength check, as the mechanism
    lens noted.
- **The pinch.**
  - What: hub 2's wall at 0.05 mm, at the raise-overhead peak (plane 30, elevation 150, axial -60), in state A (K
    closed).
  - It is the same part, same frames and same 0.05 mm as the refuted claim BD (re-measured here on BD's own shape). The
    kit-rule changes did not touch it, and it is a fit issue of hub 2's level.
  - It holds held out: the same peak appears as clip frames 13-19 and workspace pose 606 (hub 2 at 0.05 mm). Hub 1's
    wall also comes to 0.08-0.20 mm at elevation 165 (poses 609, 681, 754).
  - The held-out overhead set therefore does not test the pinch independently: it is the same pose.
  - The claim reports it (near-touch 26.15, 15 poses under 1 mm; held out 28.31), and BDp still beats H1 on near-touch
    (31.75; held out 34.66).
- **The optimistic number.** None found.
  - The claim harness is the re-measure verifier imported unchanged.
  - Its only relaxation is the virtual-phi check, which clamps to [5, 175] under the physical stop. That is replaced by
    q2 inside the slot (a check of the model's own frames, so tautological, but my independent closure agrees).
  - It adds the conservative m3e knock-out, which removes 0 poses.
  - The continuity file the claim used (a scratchpad copy) is identical to the committed
    `minarc-kitrule/conn_floorBD5_phys_cap6.json`: same 1041 keys, same params.

## Verdict: NOT REFUTED from this lens. 19.06 stands; it is buildable with two spec corrections, both at 0 bench cost

1. **K stop B at dK 34.5 deg instead of 62.83.** As specified, stop B engages at m3e 2.74 deg, below the claim's own
   5-deg reading. Moving it costs 0 points.
2. **Clock-spring rate of 0.015 N.m/rad or less** (strip 145 mm or longer, +C1900 temper). At the doc's 0.03 N.m/rad
   the strip reaches 1505 MPa at stop B.

**Unpriced but disclosed.**
- The 0.05 mm hub-2 pinch on the overhead raise (near-touch 26.15).
- 4 DOF with a sensed K.
- Hub K stands 6 mm prouder than the other hubs.

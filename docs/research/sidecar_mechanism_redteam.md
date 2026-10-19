# Sidecar drive red team + build spec: sidecar-longdyad-knuckle-3r (gen-6 winner)

2026-10-16. Subject: the drive that slaves K to q2 in the round-8 winner (docs/concepts/sidecar-longdyad-knuckle-3r.md,
VERIFIED 18.91 frozen exact, held out 22.67). The drive is a lobe on hub 2's rotor, then a bell crank with a roller on
link 1b, then an M2 ball-link pushrod beside link 1b, then a horn on link 1a at hub K. This note prices that drive with
real parts and real numbers.

Scripts and outputs are in `docs/research/sidecar_mechanism/`:

- `extract.py` wears the verified config with the claim's own model, the verifier's harness checks and the frozen
  protocol (fit Bench(60,160) fast, worn on Bench(110,360) exact or held out). It dumps the drive geometry and the
  per-pose state to `geo_*.npz` / `geo_*.json`.
- `drive.py` covers the stroke table, the KBRM-02 eye clearances, the real follower and lobe, loads, play and fold
  margin. It writes `results_rh155.json`, `lobe_polar_rh155.csv` and `spec_points_rh155.json`.
- The npz files are derived. Rebuild them with `OMP_NUM_THREADS=1 nice python3 extract.py geo_rh155.npz '{"r_h": 15.5}'`.

## Verdict

The drive is buildable for MVP1 at this size, with two changes to the verified envelope and one honest loss.

| # | Finding (measured) | Fix (cheapest first) |
|---|---|---|
| 1 | **r_h 15.5 holds.** Run through the claim harness (verifier extra checks included), it gives frozen exact **18.92**, score 93.12, near-touch 20.01 / 34.03, min metal 0.28. That is the same as 18.91 and well inside 0.3. Other changes: the drive's own range drops from dK 43.0 to **40.5** (ROD-hub2); the taken maximum stays 37.8; transmission rises from 38.8 to 40.2 deg; horn tilt is now 22.2-22.6 deg; real lobe pressure angle is 40.3 deg; m3e min 5.232 is unchanged; held out reads **22.69** against the verified 22.67. | **Build at r_h 15.5** (changed from 14.87; stated on the part). |
| 2 | **The real M2 ball link is bigger than the modelled socket.** The catalogued part is igus igubal **KBRM-02** (RH) / **KBLM-02** (LH): bore 2 E10, head **O9 x 4**, ball 4.1 wide, h1 12.5, overall 17, tilt **30 deg**, static 100 N long-term tensile, 0.4 g. The model sampled an O7 socket. With the real O9 head, still at r_h 15.5: (a) the horn eye runs **0.97 -> 0.62 mm** to hub K's O20 cylinder over the stroke, below the 1 mm rule; (b) at 22.6 deg of tilt the horn eye's lower rim dips **0.58 mm under the horn lug top** when the ball centre is 3 mm over the lug; (c) the crank-tip eye runs **0.87 mm to hub 2 at dK 36** and 0.07 at dK 40. With a 1 mm rule the drive range then ends at **dK ~35.4** instead of 40.5. | (a) The hub K "cylinder" is conservative, because the eye's upper rim sits above U1 (fK+10.25) where the cap is already the G2 dome. L1 R6 must measure eye vs cap on the real dome. If it reads < 1 mm, tilt the horn stud 18 deg toward the mean rod direction (the eye then stays near square, so 1.0 mm at r_h 15.5) or use r_h 15.9 (one claim-harness run). (b) Add a **0.6 mm spacer**: the ball centre goes to 3.6 mm over the lug. The verifier priced 4.0 mm at +0.39 fast, so 3.6 is about +0.2 fast. (c) Move **stop B (the q2 dowel) to dK 35.4** (q2 = -25.65 deg). That loses the **3 taken workspace poses of 360** with dK 35.4-37.8 (0 clips): an honest cost of about 0.3-0.8 gap points, to be measured. The alternative is a custom Ti dog-bone with an O7 x 3 eye at the crank tip only, carrying a pressed iglidur ball cup, which restores the modelled envelope. The crank-tip tilt is only 1.3-9.9 deg, so a small cup is enough there. |
| 3 | **The modelled follower does not exist; the real one does.** The model's s_arm 4.39 on a lobe at r 7.7-10.2 lies inside hub 2's O20 housing, as the verifier flagged. The exact spatial cam, solved here for the verified law (kK 1.6232 through the real RSSR), needs a different follower. The roller rides a lobe ring on link 2's housing, **profile r 10.29 -> 13.43 mm** (dwell O20.4, r 10.19). The roller is an **IKO CFS2.5** stud cam follower (O5 x 3, stud 2.5) on a **6.0 mm** short arm at psi 201 deg. The real pressure angle is **9.1-19.1 deg**, the minimum pitch radius of curvature 8.67 mm (no undercut), and the roller drifts 0.59 mm along u2 over the stroke. | Build this follower. The lobe is re-solved, so the law, the RSSR, the long arm, the rod and the horn are unchanged. Of every grid option (rr 2.5 / 3.0, a_s 5.5-9, psi 0-357), this one alone passed all five gates: dwell between O20.2 and O21.6, the nose sweeping clear of the crank neck over the whole J2 range, the roller clear of the neck, drift <= 0.6, and no undercut. An MR63ZZ roller (O6) has no feasible slot at this pivot. |
| 4 | **The crank axis dR is 15.19 deg off u2.** The lobe and the crank are a spherical cam: both axes pass through GH. A roller whose axis is parallel to dR, running on a lobe extruded along u2, would be misaligned by 15 deg (edge contact). | Extrude the lobe flank along the **roller axis at mid-stroke** (dR seen in the lobe frame at t = 12.5 deg). The residual misalignment is then +-3.3 deg over the stroke: 0.17 mm across the 3 mm roller. Machine the flank by **4-axis wire-EDM with UV taper**, so that each ruling follows R(u2, t) dR (exact). The CAD shows the straight extrude along the mid direction, which is allowed (a constant section along a line). |
| 5 | **Loads are small.** With the kit-rule K clock spring at 0.08 N.m preload + 0.015 N.m/rad, plus the MVP1 0.033 N.m: rod 5-13 N (compression), follower 15-28 N, J2 step **0.13-0.20 N.m** (checked by virtual work to 0.5 %), Hertz roller-on-lobe **417-487 MPa**, every pin and arm under 81 MPa. | Every part is far inside its rating: KBRM-02 at 100 N long-term (factor 7.7), CFS2.5 (supplier to confirm), 17-4PH H900 lobe. A preload of 0.05 N.m cuts the J2 step to 0.135-0.153 N.m. |

**Nothing here is unbuildable at this size for MVP1.** The binding item is finding 2: the real M2 eye costs the poses
with K open past 35.4 deg, unless the crank-tip eye is a custom O7.

MVP2, a powered K load through this drive, is the same story as gen-5. If the arm's gravity moment about uK (several
N.m) went through a 9.5-15 mm horn, the rod would see several hundred N, beyond the KBRM-02. MVP2 needs K driven or
a different morphology. That is not an MVP1 issue.

## 1. Geometry (link 1b frame at q = 0, K on stop A, mm from GH; `spec_points_rh155.json`)

**Axes**
- Crank axis dR: 15.19 deg from u2.
- uK: 39.24 deg from u2.
- The pivot sits 16.01 mm off hub 2's axis at the boss underside (61.09 along dR), and 18.41 mm off it at the lobe
  mid-band (F2 + 7.45).

**Crank and RSSR**
- Crank: long arm La 16.55 mm. Its tip ball centre is `crank_tip_ball_centre`, at link 1b's layer + 6 (zr 0, ZB 3).
- RSSR: rod centres **26.773 mm**; the closure error over the stroke is 0.000 mm.
- Ratio dphi/ddK is 0.78-0.92. The crank turns 35.05 deg at dK 40.5.

**Horn and moment arms**
- Horn: r_h **15.5**, beta -86.45 deg from link 1b's direction. The horn ball centre `horn_ball_centre` sits at
  fK + 3.15 (hl) + 3 + 3.
- The rod's moment arm about uK is 9.5-15.0 mm, and about dR 12.2-16.2 mm.

**Ball-link tilt**
- Crank: 1.3-9.9 deg. Horn: 14.1-22.6 deg. Both are inside the KBRM-02's 30 deg.

**Stroke**
- Onset q2 = -3.840 deg. The model's stop B is at q2 -28.791 (dK 40.5); the build stop B is -25.65 (dK 35.4, finding 2).

**Lobe (`lobe_polar_rh155.csv`)**
- Columns: t past onset, dK, crank phi, pitch az / r, profile az / r, pressure angle, and the rod and follower forces.
- Polar frame: x = `lobe_polar_x` (the pitch direction at the onset, in link 2's frame), y = u2 x x.
- Profile: r 11.04 at t 0 (the roller sitting on the dwell + 0.1 lift-in) up to 13.43 at the drive end (profile
  az 8.6 -> 21.0 deg). The dwell is the O20.4 base elsewhere (r 10.19; the roller pitch r 12.79 leaves it 0.1 clear).

**Lobe band**
- u2 levels F2 + 6.2 .. F2 + 9.2, a 3 mm band for the 3 mm roller plus the 0.59 drift. It is clamped under the cap
  skirt, as in gen-5's lobe ring.

**Crank stack**

| element | level |
|---|---|
| boss O10 on link 1b | 61.09 .. 66.09 along dR (2x MR63ZZ, 3 x 6 x 2.5, on the O3 pivot pin pressed in link 1b) |
| long arm | leaves the boss bottom and joggles 60 deg down to the strap layer, as modelled |
| neck | O6 from the boss top up to the short-arm plate |
| short-arm plate (1.5 thick) | above the roller, at the lobe band top + 0.15 |
| roller | IKO CFS2.5 stud through the plate, nut on top; roller centre `roller_centre_onset` (s 68.72 along dR) |

The roller sits 6.0 mm from the dR axis. The roller-to-neck clearance is 0.5 mm, and the nose (r <= 13.43)
sweeps about 2.0 mm clear of the neck (its inner edge sits at r 15.4) over the whole J2 range.

## 2. Parts list (real parts, real size)

| part | spec | qty | play / rating |
|---|---|---|---|
| rod ends | igus igubal **KBRM-02** + **KBLM-02** (M2 RH / LH), head O9 x 4, h1 12.5, 30 deg tilt, igumid G / iglidur W300 | 1 + 1 | bore 2 E10 (+14..+54 um) on an O2 h6 pin, so 14-60 um diametral. 100 N long-term static tensile (rod max 13 N). |
| rod | Ti-6Al-4V stud M2 RH / M2 LH (turnbuckle), 1.8 mm exposed between the ends at 26.773 centres, 5 mm thread engagement each side (>= the 4 mm minimum) | 1 | 0.8 mm per turn; 0.4 mm (half turn) = 1.5-2.4 deg of K before the trim |
| pivot pin | O3 h6 17-4PH H900, pressed in link 1b, crank-pin root 81 MPa | 1 | |
| crank bearings | **MR63ZZ** (3 x 6 x 2.5; NMB 673ZZ class Cr 0.206 kN, C0r 0.073 kN), back-to-back, preloaded by a 0.1 mm wave washer (no axial play) | 2 | follower + rod load 28 N radial, 30 % of C0 |
| crank | Ti-6Al-4V, 5-axis machined from solid (boss O10 x 5, neck O6, long arm 3 x 6, joggle 60 deg, short-arm plate 1.5) | 1 | arm root 9 MPa |
| roller | **IKO CFS2.5** stud cam follower, O5 x 3, stud 2.5 (crowned outer ring if offered; otherwise a +-3.3 deg edge allowance) | 1 | stud bending 32 MPa |
| lobe ring | 17-4PH H900, 3 mm band, wire-EDM with UV taper, bore O18 on link 2's turned ring, keyed by an O1 dowel at the onset q2 -3.840 deg, clamped by the cap skirt | 1 | Hertz 487 MPa against an allowable >= 1.5 GPa |
| horn stud | O2 h6 17-4PH pin with a 0.6 mm shoulder spacer, pressed in the horn lug (link 1a's own layer at hub K), M2 nut over the eye | 1 | 60 MPa |
| K closing spring | the kit-rule clock spring in K's cap: 0.3 x 5 mm 1.4310 strip, about 145 mm, 0.015 N.m/rad, **0.08 N.m preload** at stop A (0.05 is enough, factor 1.5 over the 0.033 N.m MVP1 load) | 1 | the only preload in the train |

## 3. What keeps contact

**The spring.**
- K's clock spring closes K. This puts the whole train in compression: horn -> rod -> crank -> roller -> lobe.
- At the onset the spring gives 0.08 N.m, a factor 2.4 over the MVP1 opening load (0.033 N.m). With 0.05 N.m the
  factor is 1.5.
- No second spring is needed.

**The dwell.**
- Before the onset, the roller waits 0.1 mm off the O20.4 dwell and K sits on stop A.
- The dwell must cover J2's full window, q2 +90.06 down to -3.84 (94 deg of rim).

**Dynamic lift-off.**
- The estimate is the gen-5 one: a self-motion inertia of about 5e-4 kg m2 lifts off at q2 accelerations above about
  30 rad/s2 with 0.08 N.m.
- R17 must run the clips with the drive coupling. Its judge fix is in progress (wf_6b8df655-403).

## 4. Play stack, the cuff and the 5-deg fold margin

**Play sets one constant offset.**
- Under the spring preload, every clearance sits on one side: the KBRM bore on the pin, the ball in its housing, and
  the cam follower's internal clearance.
- Together they are one constant offset, trimmed at assembly with the turnbuckle (0.8 mm per turn).

**K error per 10 um of each source (measured on the stroke):**

| source | K error per 10 um |
|---|---|
| rod length | 0.038-0.060 deg |
| roller or lobe form | 0.105-0.130 deg |
| crank-tip eye | 0.038-0.060 deg |

**Variation after the trim:**
- lobe form +-10 um: 0.13 deg;
- CFS2.5 runout 5-10 um: 0.13 deg;
- igubal polymer compliance, 2 x about 5 um at 13 N: about 0.06 deg;
- MR63ZZ pair (preloaded): about 0.

The total is **RSS about 0.2 deg, worst case about 0.35 deg**, against gen-5's 0.55 / 1.1. That is the gain from the
2.5-6x larger lever arms.

**If the load ever reversed** past the spring: igubal clearance 2 x 0.02-0.10 mm plus the E10 bore, about
0.05-0.25 mm, gives **0.2-1.6 deg of K**. The preload factor of 1.5-2.4 prevents it.

**The cuff does not feel K error.** K is slaved and the 3 active joints close the chain on the arm, so a K error only
re-solves q1-q3. There is no strain at the cuff. The encoder-read pose is off by about the K error (0.2-0.35 deg).

**Fold margin (the one `th` metric, m3e; nominal taken min 5.232, reproduced exactly):**

| K offset | taken min margin |
|---|---|
| +0.5 deg | 5.291 |
| +1.0 deg | 5.351 |

The slope is 0.06 deg of margin per deg of K. By extrapolation, -1 deg gives about 5.17 and -2 deg about 5.11. Those
two rows are not measured, because the law's th is not monotone there, so the interpolation is skipped. Every row
stays >= 5. The trim direction is still **open, not closed**: set the onset with K +0.5 deg open.

## 5. Build spec for the CAD agent

1. **Build the verified config with r_h 15.5.**
   - Measured 18.92 frozen against 18.91, and held out 22.69 against 22.67 (min taken th margin 5.021 held out).
   - State the change on the horn part.
2. **Crank stack and follower**: as section 1, from `spec_points_rh155.json`. Lobe ring profile from
   `lobe_polar_rh155.csv`.
   - Draw it as tangent 3-point arcs through the profile points (no splines, no lofts).
   - Join the profile to the O20.4 dwell with a concave R2.5 arc at the onset (the roller seat), as gen-5's R3.
   - Extrude it along the roller axis at mid-stroke over the 3 mm band.
3. **Rod.**
   - KBRM-02 at the crank tip, KBLM-02 at the horn, on an M2 RH/LH Ti stud at 26.773 centres.
   - Model the real O9 x 4 heads, h1 12.5 and the O4.6 shanks.
4. **Horn.**
   - A lug of link 1a at K, on link 1a's own layer.
   - O2 h6 stud with a **0.6 mm** spacer, so the ball centre sits 3.6 mm over the lug top.
   - Lug end rounded at r_h + 4.5.
5. **Stops.**
   - Put the q2 dowel stop B at **q2 = -25.65 deg (dK 35.4)**, unless the crank-tip eye is the custom O7 (then
     -28.79).
   - K stop B at dK 40.5 as a backstop.
   - Each stop is a dowel in an arc slot between the two bodies of its joint.
6. **Judge at 1 mm (R6 / R16):**
   - KBRM-02 horn eye vs hub K's real cap dome (if it reads < 1 mm: tilt the horn stud 18 deg or take r_h 15.9);
   - crank-tip eye vs hub 2;
   - lobe nose vs crank neck (2.0);
   - roller vs neck (0.5);
   - short-arm plate vs the cap skirt (the plate is 15 deg tilted to the lobe ring top: check the inner edge).
7. **Show the lobe.**
   - It sits at F2 + 6.2..9.2, beside the cap skirt.
   - The roller and the short-arm plate sit on the crank side, so a close-up from the crank side at about 45 deg
     shows the lobe, roller and plate together.
   - The lobe ring is bead blasted, the roller polished, the igubal heads iglidur orange; no black parts.

## Red team (what could still be optimistic)

- **The 3-pose loss of finding 2c is counted, not measured.** It is 3 workspace poses of 360 past dK 35.4. The claim
  harness with the drive range capped at 35.4 is one run that settles it.
- **Hub K treated as a full O20 cylinder to F + 12.25** overstates the eye pinch. The dome is narrower above U1. The
  L1 decides.
- **One feasible follower slot** means the geometry is tight. A CAD placement off by about 0.3 mm (roller vs neck 0.5)
  may need the neck at O5.
- **The CFS2.5 crown and C0 are not confirmed here**: a supplier check.
- **Not computed here (CAD checks):** the short-arm plate against the cap skirt (tilted 15 deg), and the lobe ring's
  in-band and skin clearance. Gen-5's lobe went 0.23 mm into the skin at the overhead peak.

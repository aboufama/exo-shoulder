# Independent check of the gen-7 CAD fix pass (user_slipper_nose rebuilt, user_trimlug_k165)

2026-10-17, 17:34-18:45 UTC. Skeptic of `docs/research/user_slipper_nose_fix.md` (commits e55b2b7, 106e615, 3cf299c). Local
only: niced, at most 2 of my own processes, OMP_NUM_THREADS=1; no farm, no GPU. Judges and the fix pass's files not edited.
Scratch: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/vfix/`.

**Verdict: NOT REFUTED on the numbers. R1 reproduces exactly: 81.1814 / 81.2959, and R1-aim 47.5356 / 47.5722.**

**Not ready for a render: 3 defects and 3 open items below.**

- The defects are two drawing contradictions and one crank stack that does not hold the running gaps it claims.

None of them is a judge failure. Each one sits on an item the fix pass reports as closed.

## 1. Re-run of the failing judge (R1, both CADs)

`BANDS=10,14 score_design.py <copy> 3` (the judge_all line, the vs-L1 rule's step) on copies of the committed exo.glb +
clips.json. The copies keep the judge from overwriting the design's own score files. sha1: user_slipper_nose c4a05605,
user_trimlug_k165 ed3b1b58, L1 9e17f5f8.

| design | R1 2-14 committed | R1 2-14 re-run | R1-aim 2-10 committed / re-run | per clip | wall time |
|---|---|---|---|---|---|
| user_slipper_nose (fixed) | 81.1814 | **81.1814** | 47.5356 / 47.5356 | all 8 identical (max diff 0.0) | 3813 s |
| user_trimlug_k165 | 81.2959 | **81.2959** | 47.5722 / 47.5722 | all 8 identical | 3812 s |

The trimlug glb differs from the fixed slipper's in exactly one of its 102 nodes:

- link 1a, 2826.58 to 2804.83 mm3 in the mesh (22.39 in B-rep);
- every other node has the same volume, transform and face count.

So it is slipper-nose plus one cut, as claimed.

The L1 (82.03) and v1 (81.09, glb from 5a74d30^) were read from their committed score files, not re-run. score_design.py
has not changed since the L1 was judged.

Per clip, min gap (read from the committed score files, step 3):

| clip | L1 | v1 | fixed | trimlug |
|---|---|---|---|---|
| Raise overhead | 74.48 / 1.97 | 73.08 / 1.95 | 73.15 / 1.95 | 73.38 / 1.95 |
| Comb hair | 90.94 / 2.46 | 90.32 / 2.86 | 90.42 / **2.68** | 90.66 / 2.68 |
| Reach a high shelf | 90.43 / 2.40 | 90.08 / 2.81 | 90.12 / **2.61** | 90.06 / 2.61 |
| Drink from a cup | 87.09 / 3.51 | 85.13 / 3.84 | 85.29 / 3.84 | 85.35 / 3.76 |
| Wash opposite shoulder | 60.14 / 3.59 | 59.28 / 3.89 | 59.37 / 3.89 | 59.35 / 3.77 |

- Every clip moves up with link 2 at margin 0.
- Two minimum gaps fall by 0.2 mm (2.86 to 2.68, 2.81 to 2.61), as expected when the bar comes down onto the model strap.
  They stay above 2 mm (the L1's 2.40-2.46).
- R6 on the rebuilt slipper is 0 interpenetrating by > 0.15 mm, worst 0.0 (the fix pass's own single-worker chain, read
  from its log). No skin contact is introduced.
- trimlug's min gaps 3.84 to 3.76 and 3.89 to 3.77 cannot come from removing metal. They are the R1 sampler's metal
  resampling: one point per 1.5 mm2, seed 3 per part. Cutting the lug changes link 1a's sample positions.
  - So the R1 deltas of +0.09 (margin 0) and +0.12 (lug trim) sit at the scale where resampling could move them.
  - A metal-seed paired test (v1 against the fix at seed 4) was prepared (`vfix/score_design_seed.py`) but not run: the
    box was at load 15-19 and one R1 run took 64 min.
  - Neither delta is used to claim anything beyond "no worse". The fix pass claims only that, and that stands.

## 2. Is each fix a real component at a real size?

- **Link 2 margin 0.** It is a profile offset on a 2.5-D machined bar. It is real, and the reflex rounds' 0.08 mm dip under the
  model strap is disclosed. The model strap is the bench's verified metal, so the bar now sits on the verified envelope.
- **+-0.02 mm profile on the crank's running faces, the knee-stop tooth and the E strap side.** These are achievable by
  5-axis finishing or wire EDM. They are tight and expensive, but they are real.
- **K phase +0.75 +0.15 / -0.10 deg by shimming the O1 key dowel.** At the O20 bore, 0.1 deg is about 17 um at r 10. This is
  an assembly adjustment against a phase measurement, which is plausible with a fixture.
- **Knee pins "ISO 8734 3 m6 x 10 faced to 9.2" with an e-clip groove.** ISO 8734 pins are hardened (440C here), so the
  groove must be ground or EDM'd, not turned. The pin is a modified stock pin and the drawing should say so.
  - Also, the pins are pressed H7/m6 over only 2.18 mm (L/D 0.73). That is unchanged from v1, but it is short for a pin
    that carries the cuff. It is worth a pull-out check before the wear test.
- **The trimlug cut.** It is one cylinder about uK. That is real and trivially machined.
- **No lofts.**
  - The builder does import `param_build.py`, through user_style_minarc, user_style_pinknee and user_style, for the v5
    hub stack. Its two `makeLoft` calls sit in `strap_solid()` and `main()`, and the slipper chain calls neither.
  - `joint_parts()` builds a spline cap, which the minarc builder replaces with the torispherical line/arc cap. The part
    names confirm the replacement ("J1 cap O20, torispherical dome").
  - No `ThruSections` call exists in the chain.
  - The flank is a constant section extruded straight in CAD. The drawing calls for a ruled EDM surface, which is a
    machining instruction, not a loft.

## 3. Failure-cost reproductions

- **Knee stop.** At the 6.8 mm contact radius:
  - 2768-f, +-0.05 + +-0.05, gives 0.1 / 6.8 rad = +-0.84 deg, which leaves 0.78 deg.
  - +-0.02 on each face gives 0.04 / 6.8 = +-0.34 deg, which leaves 1.28 deg. Reproduced.
  - The stack counts the two faces only. Adding +-0.02 true position on each knee pin hole (not on the drawing) gives
    +-0.67 deg, which still leaves >= 0.95 deg. The stop holds.
- **The r 1.25 nose held out.** The result file `docs/concepts/verify/slipper-nose-knuckle-3r_v_held_r125.json` carries
  `params.nose_r 1.25` and `sets ["--set=nose_r=1.25"]`. Its sidecar also reads nose_r 1.25. Its numbers are:
  - frozen gap 23.45, taken 852, poses failing 0, closure 0, min th 5.006;
  - drive limit 49.5 (horn), horn PA 36.3.

  So the run really was at r 1.25, not the space-bug control. The harness now reads both spellings (lines 148-150).
  **Stands.**
- **K phase, worst-case linear stack at the drawn low end.** The lead's ruling of 17:20 (audit 17:15) is reproduced from the
  robustness study's own numbers:

  ```
  +0.65 (drawn low end) - 0.35 (+-0.02 mm stack lag) - 0.42 (systematic lag, low end) = -0.12 deg K
  held-out th = 5.006 + 0.08 x (-0.12) = 4.996  -> 1 held-out pose under th 5
  ```

  The band holds only on an RSS stack. See D2.

## 4. Gap claims

The fix pass makes no new bench gap claim. The r 1.25 held-out claim is checked in section 3, and the bench r 1.25 value
(18.49) is the row's existing dump. Nothing here needs Bench(110,360) re-run.

## 5. Builder fixes: applied or not

| item | in the builder | in the delivered design |
|---|---|---|
| link 2 margin 0 (link 1b kept 0.1) | yes (`LINK_MARGIN`) | yes: build.json `links.link 2.margin_mm 0.0`, `link 1b 0.1` |
| trimlug cut | yes (`lug_trim_radius`, one cylinder) | yes: r_trim 21.304, removed 22.39 mm3, lug and web 1 solid each |
| knee pins "x 10 faced to 9.2", part names (spacer, bearing 1/2 MR63ZZ, shim, e-clip) | yes | yes, in parts_full.json |
| stock STEPs to step/stock/ (R7 judges custom parts only) | yes | yes: 7 hardware STEPs (pin clip, 2 knee pins, 2 shims, 2 e-clips) plus the 6 M4x6 upper-cuff screws, which are ours (the [ours] cuff) |
| lobe-ring name "+0.35 deg of q2" | yes | yes |
| wear-test pass mu <= 0.105 | yes | yes: fits + `drive_build.wear_test_pass_mu_max` 0.105 |
| knee stop tooth +-0.02, crank faces +-0.02, K phase +0.15/-0.10 | yes | yes, **but see D1 and D2** |
| `all_within_0p5` renamed + model-metal-outside table (VERIFY item 4) | yes (`run_checks`) | **no**: both build.json read `checks: "not run in this pass (--no-checks)"` and carry no `kinematics_exact` block |
| R7 | - | all_ok True for both (part_validity.json) |

## 6. Red team: where the fixes stop working

### D1. The drawing carries two tolerances for the same running faces (defect)

Both design.json `fits` still contain the L1's entry. It is inherited through `RL1.FITS` from
`pipeline/concept_l1/build_slipper_l1.py` line 67:

> "crank-to-link 1a / link 1b running faces: ISO 2768-f (+-0.05) on these 5-axis Ti faces"

It sits next to the new "+-0.02 ... never leave these faces to the general tolerance" entry.

- A machinist reading the first entry builds the 0.10 mm stack that can close the 0.086 gap.
- Fix: override that entry in `user_style_slipper.py` (as FITS[0..4] already are) and regenerate design.json. No rebuild
  of the metal is needed.

### D2. The K-phase band does not state RSS (the lead's 17:20 ruling not applied)

The drawn "+0.75 +0.15 / -0.10 deg" was committed at 17:22, after the 17:17 HANDOFF ruling. The ruling says "the drawing
must state RSS, or the low end becomes -0.02 deg". Section 3 reproduces the 4.996 worst case. One of the two must go on the
drawing.

### D3. Nothing in the crank stack holds the crank's axial position, so the running gaps are not set by the faces (defect, from v1)

The fix pass closed the running-gap item with +-0.02 face profiles (stack 0.04 against the 0.086 gap). Here is the
builder's own crank stack (`drive_layout()` line 307 and the crank build, lines 545-560):

- **Boss underside.** zb = link 1b's top under the O10 footprint + 0.15. The lower 683ZZ seat is cut open through that
  underside, so the lower bearing's faces are flush with it at zb.
- **Pivot pin.** The pin is a plain O3 cylinder, h5 under slip-on 683ZZ inner rings, with no shoulder and no step. The
  parts list has no inner-ring spacer under the lower bearing (the knee and the follower both have one).
- **Wave washer.** The 5-10 N wave washer is not modelled. It gets 0.15 mm between the upper inner ring (ztop) and the
  e-clip (ztop + 0.15). A DIN 137 B M3 wave washer is about 0.3 mm stock with about 0.8 mm free height (catalogue values, to confirm on the part).

The washer's load path runs from the upper inner ring, through the balls and the outer ring, to the crank's seat floors.
From there it goes through the lower outer ring and balls to the lower inner ring, which has nothing under it but the
0.15 mm air gap to link 1b.

So the preload slides the whole crank 0.15 mm down the pin until the lower inner ring lands on link 1b:

- The rotating boss annulus (r 3.5-5) and the outer ring land on link 1b's top, give or take the bearing's axial play.
- The 0.086 (1b) gap goes to about 0. The 0.108 (1a) and 0.123 (2) gaps each shift by about 0.15 along dR. The
  reachable geometry does not tell which of those two close.
- The +-0.02 face profiles do not control any of this.

**Fix (drawing and two stock parts, no judge change):**

- a ground inner-ring spacer, O3.1 x O4.5 x 0.15-0.20, between link 1b and the lower 683ZZ inner ring;
- real axial room for the wave washer under the clip (or a shim with a measured end float);
- then re-run the posed drive pairs.

The stack then becomes spacer +-0.01 plus the bearing's axial play, not the faces. This is not a judge item: the CAD
is judged as drawn, so R1 / R6 do not move.

### O2. The trimlug "1.5 mm wall" holds at the mid-plane only

The lug band is +-1.5 mm along ez (15.9 deg off uK). Along the contact line, the farthest flank contact from K's axis is:

| | mid-plane | lug top (+1.5 ez) |
|---|---|---|
| over [0, dK_lim 49.75] | 19.80 | 20.22 |
| over the built stroke to 51.75 | 20.07 | 20.48 |

So the wall past the last contact is 1.08 mm, or 0.82 over the built stroke. The model uses the same mid-plane rule
(21.27), so CAD = model. The flank face is cut beyond r_K 21.3, where no contact over [0, 51.75] lands, so "flank face
untouched" means "the used flank is untouched". The drawing should state the edge wall as >= 0.8 mm.

### O3. The rebuilt designs carry no post-export checks

`--no-checks` means the delivered build.json has none of the following:

- the kinematics table;
- the drive-to-skin distance (v1: 1.90 mm, 1.85 mm at the working end);
- the per-part model-metal-outside table that VERIFY item 4 asked for.

The link 2 change moved metal toward the skin by up to 0.1 mm. The R1 min gaps above (>= 1.95 mm) bound it, but the
builder's own drive-skin and working-end numbers are stale v1 values. Run `--checks-only` on both before the render.

### O4. The 60-deg ramp is not obviously a blocker

CLAUDE.md CAD ruling (2) sets "ramps up to 60 deg ... on a 3 mm bent bar; a tighter transition only where the part is
5-axis machined from solid, stated on the part". Link 2 is machined from solid (3+2-axis, 2.5-D side profile). A 68 deg drop
in a milled side profile is an ordinary 2.5-D feature.

The +0.16 R1 (proxy +0.24 with margin 0) the fix pass left for a ruling may already be allowed if stated on the part. That
is the lead's reading to make, not the user's.

## 7. The fix pass's single-worker chain (read at 18:40, not re-run here)

The chain is `scratchpad fix/judge_rest.sh`. Its results are in each design's judge/ folder:

| | user_slipper_nose | user_trimlug_k165 |
|---|---|---|
| R6 (part contact) | 0.0 mm, PASS | 0.0 mm, PASS |
| R16 | 64.2 % (fails only on chain_does_not_close 35.8 %; body 0, parts 0) | 64.2 % (same) |
| R17 | PASS | PASS |
| R10 | not run (base_slip.py handles a spherical chain only) | not run (same) |
| scorecard | 8 / 19 | 8 / 19 |

These equal the v1 build's and the L1's values. The trimlug claim "keeps R1 / R16" holds on these files.

The M5 forward bound on the slipper at mu 0.087 reads a twist of 4.45 deg. The runs at mu 0.105 and 0.12 were still going
at 18:40, so the wear line's "forward twist < 4.78 at mu 0.105" is not yet on file for the rebuilt CAD.

## Next

1. Apply D1 and D2 (fits only) and regenerate design.json.
2. Apply D3: add the crank inner-ring spacer and real wave-washer room, then re-run `posed_drive_check`.
3. Run `--checks-only` on both designs (O3).
4. Let the chain finish, then read R16 / R17 / M5.
5. Then the stills, after the user's yes.

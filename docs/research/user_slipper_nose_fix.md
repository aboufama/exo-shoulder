# Gen-7 full CAD fix pass: user_slipper_nose (and the round-11 winner's CAD user_trimlug_k165)

2026-10-17, 15:50-17:30 UTC. Local only: niced, at most 2 processes, OMP_NUM_THREADS=1; farm closed (CLAUDE.md (7)), no GPU,
no render. Subject: the independent check of the gen-7 full CAD (`pipeline/full-exo/designs/user_slipper_nose/VERIFY.md`,
NOT REFUTED, 8 / 19) listed six items to fix before any render, plus the round-11 winner trimlug-k165-knuckle-3r whose
generation CAD is the same builder with one lug cut. Builder: `pipeline/conformal/param_cad/user_style_slipper.py`
(new options below; defaults reproduce the v1 build). Judges unchanged (`judge/*` not edited).

## 1. What each item costs or risks (measured first)

### R1 -0.94 against the L1: it is link 2

`tools/r1_attrib.py <dir> 9` (score_design's own covered-skin rule, per part, every 9th clip frame) on the v1 CAD and the L1
reproduces the attribution in `judge/vs_l1.json` to the sample (frame mean 0.8152 vs 0.8242). Per group, CAD minus L1:

| group | in band 2-14 | over 14 | reading |
|---|---|---|---|
| **l2 (link 2 + J2 cap + lobe ring)** | **-16 490** | **+25 274** | the whole deficit: link 2 rides higher than the model strap |
| l1a (link 1a + flank lug + web) | +4 906 | +3 904 | net neutral |
| l4 (knee link: MR63ZZ bosses 3.3 mm proud, away from the skin) | +6 795 | +5 103 | net neutral (the lead's bearing build rule) |
| l3 (member 3: J3 disc + E strap + E boss) | -105 | +5 204 | ~ -0.1 pt: the E strap's upper hull + top cap cover more skin over 14 |
| l1b, base, dk | +4 186 / +1 / -213 | +921 / +1 076 / -946 | noise |

Geometry of link 2 (rest frames, mesh vs mesh, `scratchpad fix/cmp_l2.py`): 18 % of the L1 strap's surface lies more than
0.3 mm outside the built bar (max 1.26 mm, almost all BELOW the bar = the bar is higher); 12 % of the bar's surface lies
outside every L1 l2 keep-out (median 0.6, max 2.05 mm), all along the link (r 66-83 mm from GH). The builder's own profile
report says why: the underside sits on average 0.15-0.19 mm over the L1 strap (0.10 of it = `USM.MARGIN`) and up to
0.83-1.24 mm where the user-ruled 60-deg ramp lifts the low end of the model's 68-deg drop after J2's footprint.

Candidate link-2 fixes, each spliced into a copy of the v1 exo.glb (only link 2 rebuilt by the builder's own functions,
`scratchpad fix/patch_parts.py`) and measured with the same attribution (frame mean share, step 9):

| link 2 variant | R1 proxy | l2 in band / over 14 | verdict |
|---|---|---|---|
| v1 (margin 0.1, 4 strips, ramp <= 60 deg) | 0.8152 | 411 497 / 211 842 | - |
| **margin 0** (the verifier's suggestion) | **0.8160 (+0.08)** | 417 264 / 209 194 | **adopted** (reflex rounds may dip <= 0.08 mm under the strap, as the R_REFLEX note says) |
| margin 0, 8 strips | 0.8026 (-1.26) | 394 792 / 256 975 | rejected (measured worse) |
| margin 0, ramp <= 70 deg (67.8 used) | 0.8176 (+0.24) | 427 975 / 206 847 | NOT adopted: the 60-deg ramp is the lead's chosen CAD standard (CLAUDE.md CAD ruling 2); a machined-from-solid link 2 could take 68 deg - **the lead's / user's call** |
| L1 | 0.8242 | 427 987 / 186 568 | target |

So the margin buys 0.08 pt, the 60-deg ramp costs 0.16, and the remaining ~0.66 pt is over-14 coverage the L1 does not
have: link 2's pads / rings (+20 k over 14 even when its in-band equals the L1's) and the real hardware (knee bosses, E
strap cap). Those are the CAD's honest metal, not a fitting error; R1 >= the L1's 82.0 is **not reachable** by trims
inside the rules (see section 3 for the judged number).

### The r 1.25 nose: held out stands

`SN_CELL=lead CB_EXACT=1 python3 docs/concepts/verify/slipper-nose-knuckle-3r.py wear held <out> --set=nose_r=1.25`
(`docs/concepts/verify/slipper-nose-knuckle-3r_v_held_r125.json`, 321 s) against a same-session control at the claim's
r 1.1839 (291 s):

| nose | gap | reach | in-band 14 / 10 | contact | taken | horn PA taken | dK_lim |
|---|---|---|---|---|---|---|---|
| r 1.1839 (claim, control) | 23.45 | 0.6828 | 0.8943 / 0.5148 | 0.0116 | 852 | 36.1 | 49.75 |
| **r 1.25 (built stock O2.5)** | **23.45** | 0.6828 | 0.8943 / 0.5148 | 0.0116 | 852 | 36.3 | 49.5 |

Identical held out (and bench 18.49 = 18.49): **keep the stock r 1.25 nose.** Its drive limit drops 0.25 deg (49.5,
horn-PA bound) and stays 3.2 deg past the taken 46.25. (First launch passed `--set nose_r=1.25` with a space; the harness
reads only `--set=k=v`, so that run was the control - noted so nobody repeats it.)

### The gap stack and the stops

- Running gaps (v1 posed-drive check): crank to link 1b 0.086, link 2 0.123, link 1a 0.108 mm at dK 0. With ISO 2768-f
  (+-0.05) on both faces the worst stack is 0.10 mm, so 0.086 can close. Chosen: **profile +-0.02 on the crank's running
  faces and the facing pads** (stack 0.04, leaves >= 0.046) - a drawing change, no metal moved (opening to >= 0.15 would
  move the crank boss and re-open the drive layout).
- Knee stop 154.78 vs the workspace's largest knee angle 153.16 (1.62 deg). The tooth meets the E strap's side at a 6.8 mm
  radius (build.json knee stop face s 6.8-9.2): +-0.05 + +-0.05 (2768-f) is +-0.84 deg -> 0.78 deg left; **+-0.02 each on
  the tooth face and the E strap's side face** gives +-0.34 deg -> >= 1.28 deg. On the drawing.
- K phase: the "+0.75 +-0.3 deg" assembly tolerance was wider than the red team's stack covers (+0.45 nets 1 held-out pose
  under th 5; the high end pushes the horn PA past 43 at mu 0.12, docs/HANDOFF.md section 9): **+0.75 +0.15 / -0.10 deg**.
  The lobe-ring part name still said "+0.23 deg (K bias)" from the gen-6 text; it now reads the same +0.35 deg of q2.
- Wear-test pass line **mu <= 0.105** (the horn's 43-deg rule caps mu at 0.108-0.113; mu 0.15 forward bound 5.00081 deg raw
  = FAIL on the unrounded gate): on the drawing (fits) and in design.json `drive_build.wear_test_pass_mu_max`.

## 2. Builder changes (user_style_slipper.py)

- `--link-margin` (links 1b / 2 underside clearance; v1 0.1), `--l1b-margin` (link 1b alone; kept 0.1: link 1b sets the
  crank's layout, so its margin is left unchanged),
  `--lug-trim WALL` (trimlug: ONE cylinder about uK at r_K = the farthest r 1.25 flank contact over [0, dK_lim] + wall =
  19.80 + 1.5 = 21.30 mm; the model's 21.27 at r 1.1839), `--id`, `--no-checks` / `--checks-only` (the post-export checks
  are ~60 of the 77 build minutes on this box; judges need only the export).
- build.json: `kinematics_exact.all_within_0p5` renamed `joint_features_and_frames_within_0p5` (it never tested the bars),
  plus `model_metal_outside_built_max_mm` per sample set (winding number, the verifier's measure) and
  `model_metal_within_0p5_except_crank`.
- Drawing (design.json `fits` + part names): knee pins "ISO 8734 3 m6 x 10 faced to 9.2"; knee spacer / bearings / shims /
  e-clips named "knee pin a spacer", "knee pin a bearing 1 MR63ZZ", ...; stock hardware STEPs (pins with clip grooves,
  shims, e-clips) exported to `step/stock/` (outside `step/`, so R7 still judges the custom parts only); the K-phase,
  knee-stop, running-face and wear-line notes above; flank beta -176.684 kept (no beta step).

## 3. Rebuild and judges

(filled below)

# Check: gen-5 fix `user_geneva_rod_v2` (lobe radial offset + real drive parts), 2026-10-17

Independent skeptic of the result in `docs/research/geneva-rod-gen5_fix.md` sections 2-5 (commit dfa93be). Time box
45 min, local only (niced, at most 2 processes of mine; the machine ran at load 10-14 from other agents), $0 farm.
Scratch tools: `docs/research/geneva_rod_drive/check_skin_all.py` (copied in with this check).

**Verdict: NOT REFUTED** on the claim that matters - the D9-01 lobe ring no longer enters the judges' skin. Measured
from the outside on the as-built `exo.glb`, every frame of every clip, the ring clears the skin by RESULT_LOBE. The
gen-5 failure reproduces. The judges' R1 / R4 re-run on v2 reproduces the scorecard. Six corrections and four red-team
findings below; none of them reverses the fix.

## 1. The failing requirement, re-run by me

**(a) Signed skin distance of the as-built parts, every frame of every clip.** `check_skin_all.py` loads the design's
own `exo.glb` (NOT the builder's `lobe_ring()` re-made, which is what the claim's `lobe_skin.py` measured), poses every
part by the design's own `clips.json` through `scene_export.frame_xforms` (the judges' convention), and measures the
signed distance (libigl point-mesh distance, inside by the fast winding number > 0.5) of 2 000-80 000 surface samples +
all vertices per part to the judges' posed skin (`pipeline/avg/body_pose.py`). No radius filter: the claim's tool drops
every ring point at r <= 10.05 from J2's axis (`keep = r > 10.05`), which in v2 is the whole 9.6 dwell; this check keeps
it.

RESULT_TABLE

**(b) The judges' score_design.py on v2** (BANDS 10,14, step 3, a scratch copy of the design dir so the tree was not
written):

SCORE_TABLE

## 2. The failure cost reproduces (one case)

Gen-5 `user_geneva_rod`, groups l2 / dk / dr, every frame of Raise overhead (181), same check: the D9-01 ring reaches
**-0.230 mm** (inside) at Raise overhead frame 78 (the claim: -0.258 as built, -0.264 rebuilt; my samples are
different, the depth agrees to 0.03 mm). The J2 cap's nearest is +2.25, link 2's bar +2.52.

**Correction 1 - the entry is not "frames 78-83".** The ring is inside the skin on **43 of the 181** Raise overhead
frames and under 0.3 mm on 51. Frames 78-83 are the deepest, not the only ones. The fix is measured on every frame, so
this does not change the verdict, but the failure was larger than stated.

**Correction 2 - R2 could not see it.** The claim's scorecard says "R2: drive parts 0.0 in both". R2
(`judge/body_contact.py`) counts depth only past its 0.5 mm tolerance, so a 0.26 mm entry reads 0.0 there. R2's 0.0 for
gen-5's drive is not evidence the drive was clear; only the signed check above is. (A property of the judge's declared
tolerance, not a judge bug.)

## 3. Real components at real sizes; sourced or measured?

| item | claim | check | status |
|---|---|---|---|
| igus igubal KGLM-03 | bore 3, OD 10, 6 mm, 200-550 N, 32 deg | distributor listings (West3D, TME) agree on all five numbers; igus' own KGLM-03 sheet was not reachable here (the KGLM low-cost line is the successor) | sourced (distributor); the housing is modelled at the full 6 mm, which is the conservative envelope if igus' housing width is under the ball width |
| horn-side misalignment 11.8-13.9 deg | listed open | if igus' 32 deg is the total swivel (+-16), 2.1 deg margin; if it is the half angle, 18 deg | open (as the claim says) |
| DIN 6799 RS 2.3 / RS 4 | groove 2.3 x 0.64 / 4 x 0.74, land 1.0 / 1.2, d3 6.3 / 9.3 | match DIN 6799; built as such in the builder constants (`CLIP23`, `CLIP4`) and in the part names | sourced, applied |
| ISO 7046-1 M1.6 x 4 | head O3.0 x 1.0, 2.6 mm thread in a 3.65 mm blind hole | 4 - 1.4 plate = 2.6 mm; the hub hole is cut 0.15 above its floor in the 3.8 mm hub | applied |
| MR63ZZ roller static rating | "about 0.07-0.10 kN, maker datasheet still to confirm" | **NMB L-630ZZ (3 x 6 x 2.5, the same size), maker spec sheet: C0r 73 N, Cr 206 N** | now sourced: closes the claim's open item |
| roller load 49 / 66 N (spring / spring + MVP1) | measured through the solved drive | not re-derived here | measured by the claim |

With C0r = 73 N the roller's static safety is **s0 = 1.49 (spring) / 1.11 (spring + MVP1 bound)**. That confirms the
rejection of every ratio candidate (iii) (84-155 N > 73 N) and shows the chosen fix sits just above s0 = 1, the usual
floor for quiet running (red team, section 6).

## 4. Gap claims

The fix makes no bench claim: the lobe radial offset changes CAD geometry only (the law, K, every chain frame - I
compared v2's and gen-5's `clips.json`: l1a / l1b / l2 / l3 / l4 / base identical to 0, only dk / dr re-posed by 0.004 in
rotation and 0.07 mm), so the verified 23.57 stands untouched. The stop-B candidate gaps (23.57 at dK 50, 23.85 at dK 44)
are rejection evidence only. BENCH_LINE

## 5. Builder fixes applied; no lofts

- The v2 `exo.glb` carries every claimed part: KGLM-03 O10 x 6 housings in O13 x 6 eyes, horn hub O9.4 x 3.8 with 2x
  M1.6 x 4 ISO 7046, grooved O3 crank / horn pins with RS 2.3 clips, the RS 4 post clip + 0.3 shim, roller "inner race
  pressed on the pin". R7 output: 59 custom parts, `all_ok` true; the shim has its STEP (`112_drive_post_shim_washer...`).
- The lobe ring as built: r 9.0 (bore) -> 9.6 (dwell) -> profile max **12.207** (claim 12.207), 2.6 mm band (my circle fit
  on the exo.glb mesh). Gen-5: max 12.869, dwell 10.1.
- No loft is reachable: the only `makeLoft` calls in `pipeline/conformal/param_cad` are in `param_build.strap_solid()` and
  `param_build.main()`, neither called by `user_style_geneva_fix.py` -> `user_style_geneva.py` -> `user_style_minarc.py`
  / `user_style.py` / `build_geneva_l1.py` (grep of every call site).
- **Correction 3 - stale text in the builder:** the module docstring of `user_style_geneva_fix.py` (lines 10-15) and the
  `horn_parts` docstring (line 103) still say "M1.6 x 5 ... 3.6 mm of thread (2.25 d)" and "RS 4 ... 1.0 mm land"; the
  constants that build the parts say x 4 and 1.2. The parts are right, the text is not.
- **Correction 4 - stale part name:** the v2 lobe's name still says "R3 concave into the O20.2 dwell"; the built dwell
  is O19.2 (r 9.6).
- **Correction 5 - the as-built ring was not in the claim's every-frame file.** `lobe_skin_real_all.json` holds only the
  re-made candidate ring (`LOBE_ASBUILT` entry absent), and its "dwell +2.17 mm" reads ring points at 10.05 < r <= 10.2
  (the dwell at r 9.6 is filtered out). Section 1 here measures the as-built ring with nothing filtered, so the claim now
  stands on an outside number.

## 6. Red team: where the fix stops working

RED_TEAM

## 7. Corrections to the record

CORRECTIONS

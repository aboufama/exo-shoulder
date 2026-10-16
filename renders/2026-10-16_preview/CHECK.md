# Number + brief check: preview film v4 (`exo_preview.mp4`, 31 s)

Checker: independent of the maker. Every on-screen number was re-derived from git at the snapshot **`d7f4bd2`**
(2026-10-16T14:43:57Z) with a separate script that does not import or reuse the producer's `snap4.py`; frames were pulled from the encoded
file at every number-bearing moment (24 stills, 1280 px) and read by eye. Checked file: v4 as committed in `dd44ad1`
(md5 `91375e90...`); after the fix below the file is md5 `15ad0c7e...`.

**Verdict: PASS. Every on-screen number matches the repo, and verified and self-measured are labelled correctly.** One visual-honesty defect
was fixed: the Y score column was cut with no break mark. Two README wording fixes were made. Nothing else changed.

## ffprobe (re-encoded file)

| | brief | measured |
|---|---|---|
| duration | 30-40 s | 31.000 s video, 31.000 s audio, 930 frames decoded |
| video | - | H.264 1920x1080 yuv420p, 30 fps |
| audio | - | AAC 48 kHz stereo, ~162 kb/s |
| size | <= 20 MB | 15.37 MB (15,369,759 B) |
| greyscale | dashboard theme | max channel spread 13 / 255 over 93 frames (every 10th), p99.9 = 11: grey |

## Numbers (screen vs repo at `d7f4bd2`)

Score formula, as in `tools/concept_bench.py` `gap_of` at the snapshot:
`gap = round(100 x [max(0, .90 - inband14) + max(0, .95 - follow) + max(0, .90 - reach)] + 100 x contact, 2)`.
The score is `100 x (1 - gap / 275)`, as in `docs/dashboard/simple/index.html` `scoreOf` and `tools/knee_polish.py` `score`.
95 is gap 13.75. The README's Y row restates this formula exactly. The film shows no equation, by design: the formula is told as bites.

| shot | on screen | re-derived | source | ok |
|---|---|---|---|---|
| H1 | 108 shoulder-exo designs | 108 ids (108 unique) in `morphs.json`; all 108 have a `mech` preview in `motion.json` | dashboard data | yes |
| H2 / H2b | within 1 cm / never touching | the goal in CLAUDE.md. The bench band is 2-14 mm, disclosed in the README | CLAUDE.md | yes (goal, not a measurement) |
| S | 89 % / 100 % / 75 % / 11 poses; targets 90 / 95 / 90 / 0 | inband14 0.8941, follow 1.0, reach 0.75 (ws_taken 270), contact 0.0281, `contact_raw.n` 11 (all workspace poses, 0 clip) | `docs/research/minarc_final_polish/verify/v_pick1_fit60_bench.json` | yes |
| S | check on "follows" only | only follow meets its target (0.8941 < 0.90, 0.75 < 0.90, contact > 0) | same | yes |
| Y | bites 0.21 / 5.45 / 1.02, follow 0 -> 93.31; "95 target" | gap_of = 0.59 + 0 + 15.0 + 2.81 = 18.40; /2.75 = 0.215 / 5.455 / 1.022; score 93.31 | same file `final.gap` 18.4, `score` 93.31 | yes |
| M1 | 30 dead (slashed ring) | seed-spm-3rrr gap 193.44 -> 29.66, status dead | `rows/seed-spm-3rrr.json` | yes |
| M2 | 68 dead | fivebar-roll 89.13 -> 67.59, dead | `rows/fivebar-roll.json` | yes |
| M3 | 50 refuted, ring at the claim | floating-centre-3r claim 58.17 (78.85) -> v_gap 136.31 (50.43), refuted | rows | yes |
| M4 | 70 self-measured (hollow) | crown-ring-3r 82.37 -> 70.05, screened, no v_gap | rows | yes |
| M5 | 84 self-measured | raglan-routed-3r 42.72 -> 84.47, screened, no v_gap | rows | yes |
| M6 | 89 verified, ring at the claim | skin-normal-3r-knuckle-cufflink 24.47 (91.10) -> v_gap 29.1 (89.42), verified | rows | yes |
| M7 | 58 refuted | slotted-eccentric-j2-3r 74.0 (73.09) -> 115.21 (58.11), refuted | rows | yes |
| M8 | 91 verified | geneva-tail-knuckle-pinknee-3r 16.53 (93.99) -> 23.57 (91.43), verified | rows | yes |
| M order | "ideation order" | t_ideated 15 Oct 14:54, 15:12, 15:12, 17:21; 16 Oct 01:20, 01:35, 05:47, 12:11: ascending | morphs.json | yes |
| Z1 | 93.31 leader; 13 verified; 13 framed tiles | statuses {ideated 44, dead 19, verified 13, refuted 11, screened 10, duplicate 7, modelling 4}; 13 frames counted on the frame at 15.9 s | morphs.json | yes |
| Z2 | 270,718 configurations scored | 57 sweep files ('_' excluded), 270,737 rows, **270,718 with gap and t** | `docs/concepts/sweeps/*.json` | yes |
| Z2b | 805,852; + 535,134 on GPU | 247,646 (`gpu_searches.json` evals) + 186,248 (golden README search table: 2,252 + 5,396 + 108,768 + 27,016 + 42,816) + 101,240 (`gks1_digest.json` n_ok) = 535,134; + 270,718 = 805,852. The 560,478 bounded-only configurations are not counted | dashboard data, docs/research/golden | yes |
| V1 | 97.75 struck, "refuted" | the sweep minimum is gap 6.19 = 97.75, minarc-stop-knuckle-4r, 08:12:02Z. 3,374 readings >= 95, all minarc, 08:12:01-02Z. The claim from that search (15.42) was refuted at 09:45:42Z and 09:49:42Z | sweeps, `events.jsonl` | yes (a fast-screen reading, struck; the README says so) |
| V2 | 26 of 30 came in lower; hollow = claimed, filled = verified | 30 rows have a v_gap that differs from the claim (`v_gap_claim_reading` for minarc); in 26 the verified score is lower; 4 are higher (coupler-path-j1, geneva-tail-knuckle-3r, j2-arc-sector-3r, sliding-rivet-pauldron) | `rows/*.json` | yes |
| V2 independence | filled = an independent number | 24 of the 30 are verified or refuted rows. For the other 6 (5 dead, 1 screened), git shows that a later audit or verify commit rewrote each v_gap (a98f90b, dfb0246, a72210d, 564b45c, 02c8315, b7ad64f), so each is an independent re-measure. The 10 rows whose v_gap equals the claim are left out, as the README says | git log -G | yes |
| C1 | 75.83 84.51 88.96 90.38 92.89 93.31 | 66.47 (15 Oct 20:32:53, seed-offset-3r-slides), 42.59 (00:32:53), 30.35 (03:58:22), 26.45 (06:30:25, verifier CONFIRMED), 19.54 (row v_t 11:57:11), 18.40 (polished_t 13:58, CONFIRMED) -> scores as on screen | `events.jsonl`, `rows/minarc-stop-knuckle-4r.json` | yes |
| C1 | 17 hours; 1.69 to go; bracket 95 to 93.31 | 20:32:53 -> 13:58:00 = 17.4 h; 95 - 93.31 = 1.69. The step x positions fit a linear time axis to within ~10 px at 1280 | same | yes |
| B1 | 93.31 -> 95; still running; automated search · 43 hours; snapshot 16 Oct 2026; claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r | 821 commits, first commit to `d7f4bd2` = 42.97 h; dashboard address appears once in `docs/DASHBOARD.md` | git log, DASHBOARD.md | yes |

Verified vs self-measured on screen: a filled dot always means the verifier's number. Hollow rings are self-measured (M4, M5, the V2
claims). A slashed ring means dead. The hero number printed is always the verifier's when one exists (M3, M6, M7, M8). The leader's 93.31
is the verifier-confirmed polished number. 97.75 is the only self-measured reading above 95, and it is shown muted and struck through.

## Fixed by the checker (frames re-rendered, film re-encoded)

1. **The Y score column was a cut axis with no mark.** It is drawn at 42 px per score point from the 100 tick, so its foot sits at about
   77.6. Yet a baseline rule at the foot made it read as 0-100, which made the three bites look ~4.5x their share of the score. I added an
   axis-break mark across the column at y = 900 in `film4.py` `Y()`, re-rendered frames 210-284 only (75 frames; the other 855 frame PNGs are
   untouched) and re-ran `assemble4.py`. The re-measured spec is unchanged: 31.00 s, 15.37 MB, 20 shots, median 1.5 s, 0 still runs,
   60 words, smallest text 36 px, spread 13, scene cuts 0 / 5 / 10 at 0.3 / 0.1 / 0.05.
2. **README, disclosures:** added a line saying the Y column is cut and carries a break mark.
3. **README, Z2b source:** "186,248 (docs/research/golden/README.md)" now names the sum, because that README has no 186,248 figure: it is
   the sum of the search table, 2,252 + 5,396 + 108,768 + 27,016 + 42,816.

The README was regenerated with `gen_readme4.py`. Its diff against `dd44ad1` is exactly items 2 and 3.

## Brief

| brief item | status |
|---|---|
| 30-40 s, less draggy | 31.0 s; 20 shots, median 1.5 s, longest 4.0 s (climax); no run of >= 8 near-still frames (maker's measure, re-run) |
| greyscale, dashboard theme | yes (spread <= 13; canvas #1a1a19, text #f0efec, muted #898781) |
| no detailed CAD, basic previews only, every design has one | yes: only kinematic stick previews on a primitive silhouette; 108 / 108 have a preview |
| huge amount of simple tests | the 108 wall, 270,718 points drawn, 805,852 counted (the GPU part named, not drawn) |
| graphs | density cloud, V1 zoom, claims-vs-verified dumbbells, time-true staircase climb |
| how the score is determined, as a story | S (four measurements against targets) -> Y (bites -> 93.31 under the 95 target) -> C1 (1.69 to go) |
| fewer subtitles | 60 non-numeric words (166 tokens with numbers and ticks) |

## Open (not errors; for the critics and the lead)

- S labels the contact cell "never touches" with the value "11 poses" and target 0. That is correct, but the label states the goal, not the
  result, and a cold viewer may take it as "the design never touches". "touches" would read straighter.
- The halo shows 10 mm. The bench scores the 2-14 mm band (pass at 14), as disclosed.
- ffmpeg's 0.3 scene detector still finds 0 of the 19 cuts. That is a property of the dark theme, disclosed by the maker; not a number
  issue.
- The critics may have watched the `dd44ad1` encode. The picture differs only in the Y shot (2.5 s), by the break mark.

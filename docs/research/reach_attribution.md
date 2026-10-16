# Reach attribution: where the leaders lose the workspace, and what each lever is worth (2026-10-16)

User, 2026-10-16: "the reach numbers at 60s just isn't good, it seems like they're plateauing near the top, lets try
to max these out as much as we can". This note measures where every lost pose goes, what each topology could reach
at most, and what each lever buys at the in-band bar. It changes no design and no rule.

Instruments (all in `docs/research/reach/`, data next to them):

| script | what it measures | output |
|---|---|---|
| `attribute.py` | wears a leader's VERIFIED configuration with its verifier's frozen protocol (fit Bench(60,160) fast, worn on Bench(110,360) exact, verifier extra checks applied) and gives every pose its first cause, in the model's own check order | `runs/<leader>_m<margin>[_refit].json`, `<leader>_poses.csv` |
| `analyse.py` | the attribution tables and the fold-margin sensitivity from the runs | `summary.json` |
| `ceilings.py` | orientation-level reach ceilings on the 360 workspace poses: the fold law at the leaders' seats, over all seats, with a per-pose-free J1 rocker and with a two-state arc relay | `ceilings.json` |
| `frontier_mine.py` | reach vs in-band frontier from every sweep / CMA history (Bench(60,160) fast) + the 4-DOF lens histories | `frontier_mined.json` |
| `relay_parking.py` | where hub 2 must sit when a relay state rescues a folded pose | `relay_parking_<leader>.json` |
| (inline) | seat re-tuning near the leaders' seats, arcs fixed, on the 360 poses | `seat_local.json` |

The fold law used throughout (docs/FINDINGS.md "The J2 fold is not a hard limit"): any 3R chain that reproduces the
arm's rotation closes a pose only if th = angle(J1, J3) lies in [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m],
m = 10 deg on the bench. Orientation depends on the axis directions only, so cuff slides, knees and offsets do not move
it. Below the window the dyad is folded (J1, J2, J3 coplanar with the links overlapping), above it stretched.

ATTRIBUTION_TABLES

CEILINGS_SECTION

MARGIN_SECTION

LEVERS_SECTION

NEXT_SECTION

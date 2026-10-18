# seatoracle-erwall-knuckle-3r - seat oracle at the second wall (instrument, never a claim)

Round 105 lens B (leadseat-longstop-oracle merged in). Model: `docs/concepts/models/seatoracle-erwall-knuckle-3r.py` (a thin
wrapper on the verified free-K oracle harness `freek-oracle-route-knuckle-4r.py`); outputs `docs/concepts/verify/seatoracle-erwall-knuckle-3r/`.

## Deeper-version answers (written before the runs)

1. **What a top mechanism designer would do that the spec does not ask for.** Separate the two levers the cells mix:
   (a) stroke (stop B 58.77 -> 76.04 at the lead's seats) and (b) seat (J1 forward along the acromion top). An oracle cell at
   the lead's seats is only meaningful next to its own control at the lead's stroke in the SAME harness (the kit's metal, not
   the lead's drive), so the stroke lever is read as a paired difference L0 - C0, not against the k33 number from a different
   seat. I ran C0 (the lead seats at the lead's own stroke) as the 4th cell instead of L1, because acroant-conecut (L1's
   reason) died by its pre-registered stop (the re-fit walks J1 back to d_az1 < 2.5), so its bound has no customer. A designer
   would also check that each cell is a legal mechanism before spending exact time: the plan's L0 / C0 K dyads violate the
   model's own K rule at stop B (a1max <= bk1 + bk2 - 5.5) - measured, fixed (below).
2. **Rawest material.** The posed exact skin of Bench(110,360) (CB_EXACT=1, the signed distance of each posed mesh), the
   workspace-envelope grid (`RM.ws_grid()`: the flood fill's nodes, 2-deg slerp edges), the clip frames (continuity incl. dK
   jumps); the per-pose oracle sample records (every K sample is a full composed run of the frozen model, not a proxy ray).
   The GH-ray seat proxy (scratchpad seatprice.py) is the digested summary this instrument checks.
3. **Methods and tools.** The verified oracle harness unchanged (`freek-oracle-route-knuckle-4r.run_oracle`: NSR 7 composed
   runs per cell, pick = taken-and-clear > lost > contact, only kinematically legal K compete); the verifier's fit-fast /
   wear-frozen-exact protocol (`RM.freeze`); the kinematic flood (`RM.kin_nodes` + `RM.flood`) re-run on each cell's own frozen
   kit design and fed to the oracle's connected filter (never the k33 conn file); near-touch re-score (`RM.near_touch`).
4. **What, other than me, shows the number is right.** The bench (exact skin, every check of the model), the k33 control on
   file (17.25 connected / 21.46 near-touch / 280 takes, `docs/concepts/verify/freek-oracle-route-knuckle-4r/wear3_r0.json`)
   reproduced by the same harness, the proxy's pre-registered predictions (L0 277-279 takes / ~14 contacts / 16.0-16.6;
   S1 ~16.8-18.0; S2 ~17-20; binders 117 / 119 / 129 / 148 at +0.9 / -12.1 / -5.0 / -0.1 control), and a red-team pose list
   (ER binders 117 / 119 / 129 / 148, overhead clip 7-11 + 234 / 237 / 264 / 290, IR 343 / 423 / 316 / 369, never-clear 405 / 459).

## What the instrument is

The verified free-K oracle harness (`freek-oracle-route-knuckle-4r.py`, the k33 skinnormal-shortk chain with the minarc kitrule
harness: O20 v5 hubs at J1 / K / J2 / J3, 3 mm bent Ti-6Al-4V bars, two-pin cuff knee on MR63ZZ pairs, ISO 8734 dowels in arc
grooves) run UNCHANGED on seat cells. Per stretched pose the oracle tries the kit's K plus 7 evenly spaced |dK| on
[5.5-deg fold floor, stop B]; each sample is a full composed run of the frozen model on Bench(110,360) exact (every check:
closure, knee window, slide residual, part pairs, skin, clip continuity incl. the dK jump rule); per pose it keeps taken-and-clear
over lost over contact, only kinematically legal K competing. One final composed run with the picked K table gives the static
bound; the connected bound keeps a taken workspace pose only if its grid node is in the cell's OWN kinematic flood set (re-run
per cell on the cell's frozen kit design: 2-deg slerp edges, 10-deg jump incl. dK, no branch change) and K can be swept from the
kit's value to the pick without a kinematic refusal. 3 active (J1, J2, J3) + K as the oracle coordinate + 2 knee pins outside
the count; 0 passive translations. No unpowered mechanism picks K per pose: every cell is a BOUND, never a claim.

| cell | seats | K dyad / stop B |
|---|---|---|
| L0 | the 3-joint lead's: J1 bvec(95.3929, 67.8974), J2 rest bvec(45.8211, 41.0855), J3 wdir(66.8662, -10.6559), b3 0.329; a1 37.552 / a2 57.218 | bk1 26 / bk2 55.56, a1max 76.044 (the k33 stroke) |
| C0 | as L0 (control: the lead's own stroke) | bk1 26 / bk2 38.28, a1max 58.7678 |
| S1 | k33 seats with J1 az1 101.6411 -> 116.6411 (+15 along the acromion-top band, 5.6 deg on the sphere), J2 re-solved at a1 37.912 / a2 58.500 (az2 53.5141, el2 46.478) | k33: bk1 32 / bk2 52, a1max 76.044 |
| S2 | k33 seats with az1 126.6411 (+25, 9.4 deg), az2 61.0385, el2 47.5979 | k33 |

Every other parameter (knee lE / lc / phiE / phib / ang_min, kit K law smhi / smlo / capK, metal rules, the k33 J3 seat in S1 / S2)
is the verified k33 set (`docs/concepts/verify/skinnormal-shortk-knuckle-4r/c_k33_fit60_bench_params.json`). In L0 / C0 the
knee is the kit's, not the lead's (the lead's crank / horn / lobe drive metal is absent: 237 / 264 are drive-metal contacts on the
lead), so L0 bounds the K LAW at the lead's seats, not the lead's drive parts.

**Spec corrections (measured).** (1) The plan's L0 bk2 55.04 (and its fallback bk1 30 / bk2 51.04, same sum) and the lead's
C0 bk2 38.0336 violate the model's K-dyad rule a1max <= bk1 + bk2 - 5.5 (76.044 > 75.54; 58.77 > 58.53): KRDesign.k_ok is
False, every pose is refused and the fit finds no closed pose (the first L0 launch died with `min() iterable argument is
empty`). The plan's k_ok check covered only the a1 side. bk2 is raised by the least amount that keeps the planned stroke:
55.56 (low-end margin |26 - 55.56| + 5.5 = 35.06 <= 37.55, 2.49 deg) and 38.28. (2) Cell 4 is C0, not L1: L1 was conditional
on acroant-conecut (J1 +10 at the lead's seats), which died by its pre-registered stop (the re-fit walks J1 back to
d_az1 1.16 / 1.45 < 2.5); C0 instead isolates the stroke lever L0 - C0 in the same harness.

## Results (frozen exact Bench(110,360), fit Bench(60,160) fast, CB_FOLD_MARGIN 5.5, oracle NSR 7)

Files: `docs/concepts/verify/seatoracle-erwall-knuckle-3r/cell_<cell>.json` (+ `_perpose.json`, the cell's own flood
`c_<cell>_fit60_bench_conn.json`), `summary.json`; sweep `docs/concepts/sweeps/seatoracle-erwall-knuckle-3r.json`.

| cell | kit | oracle static | **oracle connected** | near-touch (conn) | ws takes (conn) | contacts | ib14 | follow | overhead ws taken / contact | flood nodes / islands |
|---|---|---|---|---|---|---|---|---|---|---|
| k33 control (on file, wear3_r0) | 18.61 | 16.96 | **17.25** | 21.46 | 280 | ~21 | 0.899 | 0.9455 | - | 1138 / 0 |
| L0 lead seats, bk1 26 / bk2 55.56, stop B 76.04 | 174.65 | 165.18 | 221.45 | 225.18 | 2 | 13 | 0.851 | 0.127 | 2 / 2 | 1076 / 333 |
| **L0b** lead seats, K dyad 32 / 52, stop B 76.04 | 18.26 | 17.69 | **17.69** | 22.11 | 277 | 13 | 0.8862 | 1.0 | 9 / 5 | 1154 / 0 |
| C0 lead seats, lead dyad 26 / 38.28, stroke 58.77 | 19.71 | 18.83 | **20.52** | 22.16 | 255 | 5 | 0.9128 | 1.0 | 8 / - | 1003 / 0 (6 oracle moves not sweepable) |
| S1 k33 seats, J1 az +15 | 22.90 | 21.73 | **21.73** | 26.47 | 272 | 27 | 0.8986 | 0.9455 | 5 / 9 | 1142 / 0 |
| S2 k33 seats, J1 az +25 | 24.54 | 22.91 | **22.91** | 28.72 | 273 | 26 | 0.8816 | 0.9455 | 4 / 10 | 1149 / 0 |

Min fold margin over taken poses in each pose's own state: 5.5 in L0b / C0 / S1 / S2 (L0: 4.01, 13 poses below - its flat
K triangle; the cell is dead anyway). Score of the best bound: 100 (1 - 17.69 / 275) = 93.57 (lead 93.35).

**Pre-registered gate (>= 279 connected takes at <= 4 contacts): FAIL in every cell. KILL rule (every cell > 17.25): met -> KILL,
as the plan expected by arithmetic.**

### Groups (final state, mm; negative = metal in the skin)

| pose group | k33 (plan) | L0b | C0 | S1 | S2 |
|---|---|---|---|---|---|
| ER 117 / 119 / 129 / 148 | -1.14 / -10.74 / -5.87 / +0.46 | -2.23 / -13.22 / -7.80 / **+1.28** | fold / fold / -4.83 / fold | -0.06 / -7.39 / -4.82 / -0.16 | **+0.79** / -6.74 / -4.02 / **+0.66** |
| overhead clip 7-11 | in the skin (9 parking contacts) | **+0.53..+0.88** | **+1.82..+1.91** | -3.63..-4.44 | -3.54..-4.37 |
| 234 / 237 / 264 / 290 | - | +0.30 / -14.70 / -7.37 / +0.91 | +1.53 / -3.04 / -0.09 / +1.91 | -2.50 / -16.74 / -12.18 / -4.83 | -2.06 / -18.37 / -12.07 / -5.51 |
| IR 343 / 423 / 316 / 369 | -0.19 / -1.33 / +2.40 / +1.56 | -0.51 / -1.30 / +2.43 / +1.76 | fold / fold / -1.20 / -0.64 | -2.14 / -1.94 / +1.30 / +0.66 | -2.29 / -2.25 / +0.51 / +0.92 |
| never clear 405 / 459 | -10.85 / -6.91 | -10.29 / fold | fold / fold | -10.94 / -6.65 | fold / -6.29 |

### What the cells say

1. **The plan's L0 is not a legal long stroke for the lead's K dyad.** Stop B 76.04 needs bk1 + bk2 >= 81.55 (K rule at 5.5);
   at bk1 26 that is bk2 >= 55.55, and the K triangle (bk1 26, a1 37.55, bk2 55.56) is so flat that hub 1 sits ~13 mm from link
   1b's centreline in planform against the 16 mm (hub radius 10 + half bar 6) it needs: link 1b crosses hub 1's crown at 0.89 mm
   in every state-A pose (stroke 76.04) and at -0.09 mm with the same dyad at stroke 58.77 (fast) - 192 ws poses refused as
   `parts`, 165.18 static. Bridging link 1b over the O20 crown costs a full stack (~12 mm) of height. **A long stroke at the lead's
   seats needs a longer bk1 (32 here), i.e. hub K moves** - it is not "the lead with a longer drive".
2. **Stroke (L0b vs C0, same seats, oracle K in both).** The stroke newly closes 24 ws poses (the proxy said 27): 13 clear, 2 near,
   **9 in the skin** (119 -13.2, 405 -10.3, 448 -5.1, 399 -4.6, 117 -2.2, 372 -1.8, 423 -1.3, 431 -0.8, 343 -0.5 mm) with the best
   legal K already chosen per pose; no pose closing in C0 is lost in L0b; 260 common takes stay taken. In-band falls 0.913 -> 0.886
   (fast attribution at equal stroke: K dyad 26 / 38 -> 32 / 52 costs 0.003 (0.912 -> 0.909); the stroke 58.77 -> 76.04 at dyad
   32 / 52 costs 0.023 (0.909 -> 0.886) and adds contacts 0.011 -> 0.025). Bound 17.69 > 13.75; even at zero contact the 277 takes
   would need ib14 >= 0.90 that the stroke itself takes away (13.06 + 1.38 = 14.44). **No-go on 'a longer stroke on the lead'.**
3. **J1 forward (S1 / S2 vs the k33 control).** The ER wall moves as the proxy said in sign (S1 shifts 117 +1.08, 119 +3.35,
   129 +1.05 mm; S2 clears 117 / 148 at 0.79 / 0.66 mm), but in-band falls (0.899 -> 0.8986 -> 0.8816), new contacts appear
   (207 -11.6, 399, 448, 469, 150, 372, 345, 466, 318, 291) and the overhead clip frames stay in the skin: 21.73 / 22.91 against
   17.25. **No-go on 'J1 forward'.**
4. **New: the overhead clip contacts are a SEAT property.** Frames 7-11 / 234 / 290 (elevation 135-150) are taken at the lead's
   seats (C0 1.5-1.9 mm, L0b 0.3-0.9 mm) and in the skin by 3.5-4.4 mm at the k33 seats and forward of them. J1 az 95.39 (the lead)
   vs 101.64 (k33) is the difference: J1 back helps overhead, J1 forward helps the ER binders - one J1 seat cannot serve both, and
   the K law (oracle) cannot fix either. The plan's "9 overhead state-A parking contacts untouched by any seat or K" holds for the
   k33 / forward seats only.
5. **Proxy calibration.** The GH-ray proxy's pose classes hold (newly closing 24 vs 27; 13 / 2 / 9 vs 15 / 2 / 10); its gap
   (16.0-16.6 for L0) was 1.1-1.7 optimistic because the in-band cost of the stroke is larger than its 0.95-quantile levels show;
   its S1 shifts are right for 117 / 119, optimistic for 129 / 148 (+1.05 / -0.62 measured vs +2.0 / +0.2).

### Red team (own)

- The pose that jams: L0's link 1b over hub 1 (above). In L0b two poses still refuse as `parts` (incl. bench index 203, plane 0 /
  elev 90 / axial 45): the K triangle 32 / 37.55 / 52 is close to the same limit.
- The point that pinches: L0b min metal-skin 0.052 mm over taken poses, 12 poses under 1 mm (near-touch 22.11 vs plain 17.69); the
  overhead clip frames at the lead's seats sit at 0.53-0.88 mm in L0b (1.8-1.9 in C0), i.e. the stroke's refit lowered the metal.
- The optimistic number: every cell is an oracle (per-pose K pick by skin distance); a realisable K law can only be worse. The kit
  metal is not the lead's drive (237 / 264 are kit parking contacts here, drive-metal contacts on the lead). Connected = static in
  L0b / S1 / S2 (flood complete); C0 drops 6 (flood complete, 1003 nodes / 0 islands, but 6 oracle K picks cannot be swept from the kit's K without a kinematic refusal).
- Per-part in-band (link 2 / hub 2 / hub K) was not computed: the harness has no per-part band tool; ib14 is the whole-chain value.

### Next

For round 15 lens A's take-bound table, knuckle row (oracle K, kit metal, frozen exact connected): k33 seats 17.25 (280 / ~21);
lead seats at the lead's stroke 20.52 (255 / 5); lead seats + stop B 76.04 (K dyad 32 / 52) 17.69 (277 / 13); J1 +15 21.73
(272 / 27); J1 +25 22.91 (273 / 26). No K law and no J1 move along the acromion top reaches 13.75 at 3 active DOF on this chain;
what is left is a seat that serves both the ER binders and the overhead clip (they pull J1 in opposite directions), or a
mechanism change that removes the stretched-pose contacts the stroke creates (119 / 405 / 448 / 399 are deep: 4.6-13.2 mm).

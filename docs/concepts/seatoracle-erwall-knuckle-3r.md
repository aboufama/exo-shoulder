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

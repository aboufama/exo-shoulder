# spiral-lobe-longdyad-knuckle-3r (round 12, pick 1)

Spiral-lobe long-dyad knuckle 3R: inband-rssr pick3's in-band RSSR K drive on an efficient 34/48 K dyad, an early K
onset and a log-spiral hub-2 lobe. Merged: desmo-spiral-rssr (spring-free cell C) and conecut-longdyad (the re-centred
knee + J3 stop column). 3 active DOF (J1, J2, J3), K slaved and never read, 0 passive translations.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the K law as a per-pose decision,
   not a gain. The judge measured that the long dyad's extra closures split into takes and hub-2 / link-2 skin hits.
   A designer would not search kK blindly. They would tabulate each newly closed pose (K, th, the part in the skin,
   elevation, axial) and read the law off it. The law has three cuts: the gain (how fast K opens), the onset (smhi:
   where it starts) and stop B (a1max: where it ends). If the contact poses sit at large K, stop B turns them into
   plain fold losses. Each such pose saves about 0.25 points (a contact costs reach plus the contact term; a fold
   costs reach only), and the takes at smaller K stay. They would also check the reverse: whether the knee column
   re-opens the extra knee slides (10 -> 13) without new metal.
2. **The rawest material.** The posed skin itself (concept_bench's exact signed distance per pose: CB_EXACT=1,
   Bench(110,360)). The per-pose metal of every part (M.rigid, M.contact, M.link_pts) in that pose's frame. The
   workspace pose list (plane / elev / axial) and the clip frames. Not the digested "fold 64, contact 14" counts:
   the per-pose table (g0_*.json in the scratch dir) is the data the law is chosen from.
3. **Methods and tools.** The real chain model (docs/concepts/models/inband-rssr-knuckle-3r.py, loaded unchanged, with
   IB_GHOST=all for gate 0 and the drive metal back for gate A). The frozen protocol: fit Bench(60,160) fast, shape
   frozen, worn on Bench(110,360) exact. The conecut knee + J3-stop subclass. A per-pose attribution harness
   (part-by-part signed distance). Then a small grid on (kK, smhi, a1max), then CMA on the envelope bench, but only
   if gate 0 passes. The farm is at its budget line ($24.42 at 15:21 UTC against the $24.40 line), so everything
   runs locally, at most 2 niced processes.
4. **What, other than me, shows the number is right.** The bench's exact path (CB_EXACT=1) on the frozen shape. The
   judge's own reproduction (pick3 ghost 18.32, seed ghost 18.84) re-run first as the control. Later the adversarial
   verifier and the alignment auditor (paired against slipper-nose, `tools/alignment_audit.py audit --ref
   slipper-nose-knuckle-3r`). And the red-team pose list: the contact poses by part and depth, the knee-slide poses,
   the overhead cone (elev >= 140), all in the per-pose dump.

## Model

`docs/concepts/models/spiral-lobe-longdyad-knuckle-3r.py` loads `inband-rssr-knuckle-3r.py` unchanged and adds:

- the dyad clamp: bk1 26-40, bk2 38-56, a1max <= bk1 + bk2 - 5.5;
- two new hub-2 lobe laws on the parents' rocker convention (i_rock = La / s_arm, PA <= 42 at every lobe radius):
  - `law_in: "spiral"` is the catalogue's constant-pressure-angle log spiral;
  - `law_in: "tsp"` is the least-opening track law (hold the dyad margin m3e >= smt) under the spiral's
    radius-dependent gain cap, with an optional look-ahead target `thx` and a linear floor `kf`;
- the conecut knee column: the knee as params, plus the J3 stop q3' >= SL_J3MIN as a physical stop on the joint's own angle.

Every parent gate is kept (th monotone, rate, lobe PA, lift-off, stop B, skirt, the RSSR transmission >= 48 range
truncation). With `IB_GHOST=all`, every drive part's metal is deleted for attribution; the kinematics, law and
truncation stay.

## Gate 0 (the lead's kill gate): frozen exact ghost wear, per pose

Protocol: fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact, drive metal ghosted. This is the chain's
ceiling before any drive metal is added. Pass: <= 17.5 with <= 4 contact poses. Scripts and per-pose dumps are in
`/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/spiral/` (gdump.py, g0_<tag>.json).

| cell | frozen gap | ws taken | contact poses | fold | slide / j3stop | ib14 |
|---|---|---|---|---|---|---|
| judge seed 34/48 lin kK 2.8 smhi 19.46 (control; judge 18.84) | **18.84** | 269 | 14 | 64 | 13 | 0.901 |
| seed + conecut knee column (lE 82, lc 27, phiE 3.8, phib -96.6, J3 >= -105) | 19.09 | 269 | 15 | 66 | 0 / 10 | 0.906 |
| log-spiral law (pa 41.9), onset 19.46 | 18.88 | 268 | 13 | 65 | 14 | 0.900 |
| track law (base-radius cap), smt 5.2 | 34.89 | 210 | 3 | 146 | 9 | 0.937 (follow 0.927) |
| track law (base-radius cap), smt 8 | 19.71 | 255 | 2 | 92 | 11 | 0.913 |
| track law, spiral cap, smt 8 | 19.43 | 256 | 2 | 91 | 11 | 0.913 |
| track law, spiral cap, smt 11 | 18.38 | 267 | 6 | 74 | 13 | 0.890 |
| look-ahead track, smt 6, thx 124 | 21.38 | 249 | 2 | 99 | 10 | 0.913 |
| look-ahead track, smt 8, thx 124 | 19.66 | 259 | 4 | 87 | 10 | 0.895 |
| **lin kK 2.8, onset smhi 14 (best)** | **17.86** | 269 | 8 | 70 | 13 | 0.895 |
| lin kK 2.8, onset smhi 12 | 17.94 | 266 | 7 | 73 | 14 | 0.903 |
| lin kK 2.8, onset smhi 10 | 19.51 | 260 | 4 | 85 | 11 | 0.893 |

References: pick3 drive-ghosted 18.32 (260 taken, 2 contacts); the lead slipper-nose 18.49 (261, 2).

**Gate 0 fails.** The best cell (onset smhi 14) reads 17.86 with 8 contact poses, against the bar of <= 17.5 with
<= 4. On the frontier, every cell that brings the contacts down to <= 4 (lin smhi 10, both track laws,
look-ahead smt 8) takes <= 260 workspace poses. That is pick3's own ghost count, so those cells read 19.4-19.7.
Contacts and takes trade almost 1:1 at the bottom of the frontier, and stop B cannot split them (next section). As
the lead rule says, the drive can only add metal, so no drive placement can bring this chain under the bar.

### Per-pose trade, seed vs onset 14 (every pose that changes or touches)

| pose | plane / elev / axial | th | seed K | seed | onset-14 K | onset-14 | binding part (deepest, mm) |
|---|---|---|---|---|---|---|---|
| 117 | -90 / 45 / 135 | 113.1 | 55.1 | contact -5.2 | 47.6 | contact -2.3 | L2 -5.2 |
| 119 | -90 / 60 / 135 | 119.0 | 63.3 | contact -15.3 | 56.1 | fold | L2 -15.3 |
| 127 | -75 / 45 / 120 | 103.5 | 42.3 | contact -3.7 | 34.3 | contact -0.7 | L2 -3.7 |
| 129 | -75 / 60 / 120 | 108.0 | 48.3 | contact -12.1 | 40.5 | contact -8.3 | L2 -12.1 |
| 137 | -60 / 45 / 105 | 94.1 | 29.5 | contact -0.5 | 20.9 | taken | L2 -0.5 |
| 139 | -60 / 60 / 105 | 97.4 | 34.0 | contact -6.4 | 25.6 | contact -3.3 | L2 -6.4 |
| 164 | -15 / 0 / -45 | 96.4 | 32.7 | contact -1.0 | 24.3 | taken | hub-2 rim -1.0 |
| 237 | 15 / 165 / -60 | 31.9 | 0.0 | contact -14.8 | 0.0 | slide | hub K top -14.8 |
| 264 | 30 / 165 / -60 | 41.9 | 0.0 | contact -4.8 | 0.0 | contact -4.8 | hub K top -4.8 |
| 316 | 60 / 150 / -105 | 104.8 | 44.0 | contact -0.1 | 36.0 | contact -0.7 | L2 -0.1 |
| 318 | 60 / 165 / -75 | 77.6 | 3.9 | taken | 0.0 | contact -0.1 | hub K top -0.1 |
| 319 | 75 / 0 / -135 | 96.4 | 32.7 | contact -1.0 | 24.3 | taken | hub-2 rim -1.0 |
| 333 | 75 / 75 / -120 | 120.5 | 65.4 | taken | 58.4 | fold | |
| 343 | 75 / 150 / -105 | 114.1 | 56.5 | contact -1.8 | 49.1 | slide | hub-2 rim -1.8 |
| 372 | 90 / 165 / -90 | 111.1 | 52.4 | contact -4.1 | 44.7 | slide | L2 -4.1 |
| 396 | 105 / 135 / -90 | 115.0 | 57.7 | taken | 50.3 | contact -0.4 | hub-2 rim -0.4 |
| 423 | 120 / 135 / -90 | 120.0 | 64.8 | contact -1.9 | 57.7 | fold | L1b -1.9 |

### What the table says (new knowledge)

1. **Stop B cannot make the trade.** The seed's 12 chain contacts sit at K 29.5-64.8, spread across the same K range
   as its 147 K-open takes (median 21.7, max 65.4). Every K cut on the seed's own table loses more takes than it sheds
   contacts: cut 60 -> 266 taken / 12 contacts (est. 19.2); cut 50 -> 254 / 9 (21.9); cut 40 -> 243 / 6 (24.2).
   The contacts are pose-specific, not K-specific: a cluster at plane -90..-60, elev 45-60, axial +105..+135
   (poses 117-139), and the overhead internal-rotation fan at plane 60-120, elev 135-165, axial -105..-90.
2. **Over-opening is the chain binder, and the least-opening law sheds it.** K is a function of th on any law. At the
   same th, a smaller K keeps hub 2 nearer its rest place. The base-cap track law (least K that holds margin 8)
   removes all 12 chain contacts (2 left, both the lead's known hub-K-top poses at elev 165), and poses 127 / 137 /
   139 / 164 / 319 become takes at K 11-26 instead of 29-42.
3. **But late K costs the stretched takes.** Track-type laws lose 14-15 poses at th 110-115 to the fold rule, below
   the drive range (dK_lim 65.8). On the base-cap law the law's own m3e falls to 0.0002 (the gain cap 2.83 cannot
   catch up once K starts late). The spiral cap and a look-ahead (the least K that still meets the margin at every
   th <= 124) did not recover them (21.38 / 19.66). Why those 14-15 poses still fold under the look-ahead is open (not
   traced inside the time box; m3e at poses 146 / 161 / 313 / 333 read 1.4-5.0 on the base-cap law).
4. **The onset is the only lever with a gain, and it is small.** Moving the onset from margin 19.46 to 14 keeps all
   269 takes and drops the contacts from 14 to 8, for 17.86. But in-band falls 0.901 -> 0.895 (0.5 points), and later
   onsets give back takes faster than contacts (smhi 12: 266 / 7; smhi 10: 260 / 4).
5. **The conecut knee column does not stack here.** It turns the 13 knee slides into 10 J3-stop losses and 2 more
   folds, with 1 more contact: 19.09 vs 18.84. Its gain on the lead (18.49 -> 18.36) came from the lead's knee poses,
   and the long dyad's extra knee fails are different poses.
6. **The deepest binders are link 2 (to -15.3 mm) and hub 2's rim (to -10.3 mm)**, both at plane -90..-75 /
   elev 45-60 / axial 120-135, where the stretched long dyad swings hub 2 into the bunched posterior deltoid. That is
   the same wall the round-11 planner measured for the folded cone ("hub 2's disc"), now on the stretched side.

## Verdict

**DEAD at gate 0** (the lead's pre-registered kill rule). The best ghost cell reads 17.86 frozen exact with 8 contact
poses (bar: <= 17.5 with <= 4) before any drive metal, and the drive can only add metal (judge: pick3's drive unrefit
adds 18 fit contacts). Expected with metal: >= 18.5, i.e. no gain over the lead (18.49) at complexity 24.5 vs 18.25.
The convergence gate does not apply to this verdict. This is a ghost-ceiling kill over 12 law cells on the claim bench,
not a converged sweep, and no CMA was run because the ceiling is already above the bar.

Gate-0 numbers for the record: best 17.86 (lin kK 2.8, smhi 14, 34/48, a1max 76.5, pick3's placement and knee);
reach 0.7472 (269/360), follow 1.0, ib14 0.8949, ib10 0.5472, contact 0.0207 (8 poses); overhead 7/28.

What would revive it (not this row): a chain whose hub 2 can open K without swinging into the plane -90..-60 /
elev 45-60 / high external-rotation cluster. Hub 2's level and a2 are fixed by the clip frames, so that means a
different J2 seat or a K axis whose opening moves hub 2 along the skin instead of into it. That is a seat/K-axis
question for the planner, not a law question.
Cell C (the spring-free groove) was not built: it shares this chain, so the same ghost ceiling kills it.

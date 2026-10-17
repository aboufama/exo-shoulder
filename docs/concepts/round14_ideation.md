# Round 14 ideation: judge and red team (2026-10-17 ~23:25 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75)
at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered, exactly 3 active DOF.

**Lead to beat: conecut-knee-knuckle-3r, verified 18.28** (score 93.35; Bench(110,360) exact frozen), held out 22.38,
cx 18.5, ledger WATCH. The plain verified gap decides (LEAD NOTE 18:21 UTC). The champion spherical 3R reads 75.94 on
the same bench; every candidate is 48-58 points under it, so that ratio does not separate them, and this judge ranks
against the lead.

Nine candidates came in from the planner's three lenses (ROUNDS.md "Round 14 plan"): three cells of the knuckle lens,
three cells of the cap-seat lens and three cells of the crest pin-knee lens. All nine have 3 active joints and 0 passive
translations, and every joint maps to a catalogue or machinable part (MR117-2RS / MR63ZZ pairs, ISO 8734 dowels, a
wire-EDM slot, a pressed 440C insert, a lapped pad). No candidate is rejected on hardware or translations. One is
conditional on determinacy: cap-dwell's two-lobe K drive does not exist, so it runs only as a ghost cell.

After merges, **two picks**:

1. **lowarm-halfring-knuckle-3r** (knuckle lens; stopdwell = cell A0, l2rootlift = cell B).
2. **cap-plateau-knuckle-3r** (cap-seat lens; shorta1 = cell B, dwell = cell C).

The crest lens's two seat cells duplicate crest-knee-3r, which is queued elsewhere; they are forwarded to it (section 5).
Its control cell, pinknee-j3stop-3r, was measured by this judge and is not picked (section 4).

The box was at load ~14 on 4 cores. Every check below ran locally, niced, one process, OMP_NUM_THREADS=1. Held out was
not touched.

## 1. Verdicts

| candidate | lens / cell | verdict | reason |
|---|---|---|---|
| stopdwell-halfring-knuckle-3r | knuckle, cell A0 | MERGED into pick 1 (control) | Measured 18.37: the floor of the lens, 0.09 above the lead. It is the base file the other two cells patch. |
| lowarm-halfring-knuckle-3r | knuckle, cell A | **PICK 1** (row id) | Measured 18.28 = the lead's gap with the same 262 takes and 4 contacts, at cx 16.5 vs 18.5. A tie, not a lead; it is the platform for cell B. |
| l2rootlift-halfring-knuckle-3r | knuckle, cell B | MERGED into pick 1 (cell B) | The row's only route to a new lead (~17.98 estimated). Same harness, stacked on cell A, so it cannot run as a separate row. Thin: section 2. |
| cap-plateau-knuckle-3r | cap seat, cell A | **PICK 2** (row id; the jump judge's routed id) | Expected kill, but it is the only main-side seat whose kinematic count clears 279 (295/360). The lens needs its formal real-model number to close. |
| cap-shorta1-plateau-knuckle-3r | cap seat, cell B | MERGED into pick 2 (cell B) | Passes the hub-2 half of gate 0 and fails the takes half (271 kinematic < 279). |
| cap-dwell-ulaw-knuckle-3r | cap seat, cell C | MERGED into pick 2 (cell C, ghost only) | Best cap proxy (22.54 vs the lead's 16.76 on the same instrument) but 275 < 279 kinematic, and its two-lobe K drive does not exist. Without a drive, K is set only by an ideal law, so it cannot be called a design. |
| crest-j3stop-pinknee-3r | crest pin knee | DUPLICATE of crest-knee-3r, forwarded | Same family and seats. crest-knee-3r has J1 bvec(94, 62), J2 home bvec(17, 46), crest J3, b3 tilt and link 2 flying over the knee. C1 is J1 bvec(100, 62), J2 bvec(19.6, 47.8), J3 wdir(92, -5), b3 0.28, fly. Section 5. |
| crest-overstack-pinknee-3r | crest pin knee | DUPLICATE of crest-knee-3r (its hub-3 interface), forwarded | A layer-order variant of the same row. Unmeasured; it shares that row's hub-2 dome ceiling. |
| pinknee-j3stop-3r | crest pin knee, control | NOT PICKED; measured here | The judge reproduced its gain on Bench(110,360). The gain relabels four 0.02-0.07 mm touches at the top of one overhead clip, and it holds only when the stop edge sits in a 0.5-deg band (section 4). That number is the J3-stop control crest-knee-3r needs; a modeller would add only held out. |

## 2. Red team, knuckle lens (pick 1)

Proposer logs read: `scratchpad/s1/fz_m1.txt` (A0), `fz_m3.txt` (A), `held_m3.txt` (A held), `attrib4-6.txt` (cell B),
`o_noring.txt` (gates and parts). Arithmetic: `scratchpad/judge14/` (inline run).

- **Gap arithmetic reproduces.** gap_of at the logged components gives A0 18.38 (logged 18.37, reach rounding),
  A 18.29 (18.28) and B 17.98.
  - Cell A is the lead's own decomposition: 262/360 takes, 4/376 contacts, ib14 just over the 0.90 knee. **It is a tie
    at cx 16.5, not a lead.**
  - Cell A's whole gain over A0 is 0.0015 of ib14 (0.09 points). The blended-IK correction (-0.06 on desmo-conecut), the
    arm's ramps and the pad's own samples are each the same size.
- **Cell B's clear is outside its own lift.**
  - attrib6 reads 316 at +0.07 mm at h 1.5 AND h 2.0. The binding sample is therefore link 2 outside the lifted span:
    more height does not help, only a longer lift does.
  - The proposer pre-registered >= 0.2 mm. Reaching it means moving r_full / r_end outward, and with A only 0.0006
    above the knee, in-band costs 1:1:
    - in-band loss 0.003 -> 17.98;
    - 0.004 -> 18.08;
    - 0.005 -> 18.18.
  - Judge estimate: 17.95-18.2, about 35 % to stand.
- **Cell B's S-bend is not R15 as modelled.**
  - The spec's taper is linear over r 16 -> 24 (8 mm) for a 1.5 mm rise. As tangent arcs that is an R9.5 inner bend
    (centreline 11.0), against the CAD ruling's R >= 15 inner (centreline 16.5).
  - At R15, 1.5 mm takes 17.3-deg arcs over 9.8 mm, so r_end >= r_full + 9.8. Written into the spec.
- **Cell A's step has no transition.** The arm-level rule the lead's family uses is a step:
  lvl = ref + zr beside link 1b, ref + T_LINK + RUNG over it (dipped-law-groove line 289).
  - A 2.03 mm drop on an R15 S-bend needs 11.4 mm per end, so the crank must be 5-axis machined from solid, as the
    proposer allows. Even then a 60-deg ramp needs >= 1.2 mm per end.
  - The spec now requires the arm sampled at its as-built level.
- **The dwell hold is now a two-body stack.**
  - In desmo-conecut both groove walls are on link 2, so J2's runout moves both walls together and only the groove's
    0.02 mm clearance is play. Here the pin sits between a link-2 wall and a link-1b pad, so J2's radial runout and the
    ring insert's concentricity add to the play.
  - At the proposer's own sensitivity (dwell slop 0.167 deg of K for 0.02 mm, 8.35 deg/mm at the pin):
    - 0.005-0.015 mm of runout or concentricity is 0.04-0.13 deg of K;
    - the pad lap +-0.03 mm at 25-38 mm is 0.11-0.17 deg (phi 0.045-0.069 x g 2.39);
    - with the slot's 0.04, the worst corner is 0.28-0.33 deg against the 0.25 gate (RSS ~0.15-0.22).
  - The other way to set it, a preloaded pad, varies with runout: 0-0.02 mm through a ~340 N/mm crank arm is 0-7 N at
    the pad, ~0-28 N at the pin, i.e. drag or a jam at the dwell entry.
  - The dwell K play also lands on the FOLDED-side poses (K = 0 there): the lead's 15 folded losses sit at th 7.7-22.
  - The gate is rewritten to cover the whole stack.
- **The pad is unsampled metal.** None of the proposer's numbers include it.
  - Placed under the arm beside link 1b (cell A's level), it is skin-side metal at link 1b's level.
  - Placed on link 1b's TOP face where the arm crosses link 1b at phi 0, it adds none. The spec asks for that, or for
    the pad to be sampled.
- **Held out mixes rules.** A's 22.64 is at kslot 46.0, which enforces th >= 5 with K play. The lead's 22.38 does not
  enforce it (its own watch item: held th 5.006 -> ~4.92 with K play). The claim must pair the two at the same rule.
- **What stands.**
  - The O20-ring impossibility (31/294 robust placements, all r_out >= 11.10) is reproduced in the proposer's
    standalone synthesis.
  - The robust stage-1 placement (pin-side first fail 52.89 at the worst corner, mu 0.17, gate 47.27) fixes
    desmo-conecut's NEW-friction-cliff.
  - The per-pose attribution (205 / 237 / 264 cannot be cleared; 316's skin is below its root) is a real lesson.
  - "Radial lifts are dead" holds only where the skin comes from above.

## 3. Red team, cap-seat lens (pick 2)

All three proposers already measured their own kill conditions; the judge checked the arithmetic and the routing.

- **The follow tax.** U-law clips close 99/110 (follow 0.90, +5.0 gap; the round-102 judge reproduced 295/360 ws and
  99/110 clips).
  - The planner's gate cell (279 takes, ib14 0.88, 4 contacts) is gap 20.55 at that follow.
  - To beat 18.28 at follow 0.90 a cell needs >= 288 takes (computed: 287.2).
- **Hub 2.**
  - Cell A: hub 2 is 0.07-0.23 in band against the 0.8 gate. No J1 own-angle window keeps hub 2 >= 0.8 with <= 10 ws
    lost; the best keeps 38/160. This is the planner's own kill condition.
  - Cells B and C pass hub 2 (0.83-0.90 and 0.91-1.0) but sit at 271 and 275 kinematic, under 279 before any metal.
- **Cell C's lever is not new at the back seat.** The proposer's wide scan puts the two-sided law's peak (315/360
  kinematic) at the lead's own J1, with J3 wdir(65.4, -17) and a ~75-deg K stroke.
  - Folded-side lobes at the back-of-shoulder seats are on the dead list: rounds 6-7 measured that frozen fold losses
    never moved off 84-86, and the round-6 two-lobe run took 1 folded pose.
  - No drive in the class carries 75 deg (46-57.5).
  - So pick 2 does not reopen that. Its value is the cap pole's real-model bound, which is still unwritten.
- **Feel near the fold lobe.** In cell C, J1 runs ~1/sin(th) as J3 passes under J1 at th 5-10. The spec asks for the
  max J1 rate per unit arm rate.
- **Why it is picked over pinknee-j3stop-3r.** The literal ranking formula (gap reduction x confidence) would put
  pinknee-j3stop-3r second (26.1 vs >= 23-40). But the judge has already measured that number and found it a
  margin-sensitive relabel (section 4). The cap row is the round's only cell above the 279-take bar, and the plan's gate
  0 there (frozen exact plus flood) has not run. A modeller slot adds new knowledge here and almost none there.

## 4. Red team, crest pin-knee lens: pinknee-j3stop-3r measured by the judge

Script: `scratchpad/judge14/j3win.py` (logs `j3win_m1.0.log`, `j3win_m2.0.log`, `j3win_m3.0.log`).

Method:

1. The proposer's harness (r14l3/pkfly.py, FlyModel over the unchanged skin-normal-3r-pin-knee.py) fits the J3 window on
   Bench(60,160) fast with H1's verified params. It reproduces 22.59: window gap 154.8 deg, lo 110.9, 4 stopped.
2. The model's own IK gives q3' = q3 + phi on Bench(110,360) with the frozen knee centre m.
3. These are joined with H1's verified per-pose exact dump (docs/alignment/remeasure/skin-normal-3r-pin-knee_bench_perpose.json;
   it recomputes 27.20). Levels are not refit, so this is the frozen protocol.

| stop margin | H1 taken poses cut | H1 contacts stopped (of 9) | frozen gap | delta |
|---|---|---|---|---|
| 1 deg | 2: clip #7 (plane 30 / elev 148 / axial -60, q3' 112.7), ws #318 (60 / 165 / -75, q3' 112.8) | 4 | 26.16 | -1.04 |
| 2 deg | 0 | 4 | 26.08 | -1.12 |
| 3 deg | 0 | 0 | 27.20 | 0.00 |

- **All four stopped contacts are the top frames of one motion:** Raise overhead #8-11, plane 30, elev 149-150, axial
  -60, q3' 113.2-113.5. Their contact depth is only -0.07 / -0.02 mm.
- **The stop edge must sit between 112.7 (taken frame #7) and 113.2 (contact frame #11).** That is a 0.5-deg band,
  fitted to one clip's frame spacing.
- **The gain is the contact term only.** Follow (0.9636) and reach do not move at 2 deg. A 0.1 mm trim of the touching
  metal would score the same and keep the frames.
- Verdict: a real dowel and a legal stop, but the -1.1 is a relabel of near-zero touches at the overhead top. The
  round-13 cell-B rule would not count it. Not picked.
- This table is the control crest-knee-3r's J3-stop claims must be paired against.

## 5. Forwarded to crest-knee-3r (queued elsewhere; do not re-pick)

The crest lens's proposer measured, and crest-knee-3r's modeller should start from:

- **The literal antcrest seats are dead.** Hub-2 need 50-400 mm; the pin-knee model reads 375 with H1's knee and 86.12
  with E in the free sector (hub 2 at 192.8 mm).
- **The re-seated cells.**
  - C1: J1 bvec(100, 62), J2 bvec(19.64, 47.82), J3 wdir(92, -5), b3 0.28, a_deg [45.0, 59.6].
  - C2: J3 wdir(98, 5).
  - C3: J1 az 110, J3 wdir(92, -15).
- **The hub-2 tail separates on J3's own angle, not J1's.**
  - Stoppable on J3: C1 12 of 16, C2 17 of 21, C3 5 of 6.
  - With the stop, contact 0.114 -> 0.0355 at C1; hub 2 0.948 in band.
  - The stopped poses include the Raise-overhead frames at elev 150 (follow 0.917).
- **The crest hub-3 interface.**
  - Link 2's free sector about J3 shrinks to 43-62 deg (H1 117.5), so link 2 must fly over E.
  - The knee level sits at or below hub 3's face, so knee-E jams on 131-188/220 unless the knee angle stays at 58-85
    deg, or the stack is reversed (crest-overstack: knee link on the bottom layer, E boss and pad on top; unmeasured,
    gate: knee-E <= 5/220, knee parts >= 0.9 in band).
- **The untuned real model.** C1 37.37 fast (reach 0.675, follow 0.917, ib14 0.820), C2 42.37, C3 36.31.
  - Proxy gain over H1 ~2.2 points (15.57 vs 17.78).
  - Bar <= 21 frozen: ~5-10 %.
- **J3-window rules for any claim.**
  - Explicit J3MIN / J3MAX, fitted on the search bench and FROZEN into Bench(110,360) and held out.
  - Report the cut poses.
  - Pair against section 4's control, because a 0.5-deg-band relabel is worth ~1 point on H1 alone.

## 6. Ranking

Score = expected reduction vs the lead x confidence x buildability. The champion ratio is uniform: 48-58 points for
everyone.

1. **lowarm-halfring-knuckle-3r.**
   - Cell A 18.25-18.40, a tie at cx 16.5 (2 points simpler than the lead).
   - Cell B 17.95-18.2 (~35 %), the round's only lead chance.
   - 0 passive translations; every part real (one lapped pad).
   - Confidence medium-high for A, low-medium for B.
2. **cap-plateau-knuckle-3r.**
   - Expected kill (~90-95 %). Best cell C ~23-26 frozen.
   - Value: the formal close of the cap-pole lens (FINDINGS), and the only cell over 279 kinematic takes.
3. pinknee-j3stop-3r: 26.08-26.16 frozen at margin 1-2 deg, 27.20 at 3 deg (judge-measured). A relabel; not picked.
4. crest-j3stop-pinknee-3r / crest-overstack-pinknee-3r: 24-26.5 if they survive gate 0. Forwarded to crest-knee-3r.

## 7. What happens next

- Pick 1 runs on one harness, A0 -> A -> B, with the rewritten dwell-hold gate (two-body stack), the pad on link 1b's top
  face, as-built arm and S-bend levels, held paired at the same K-play rule, and the full claim set (blended IK, flood,
  dumps, S6, T5, viz).
  - New lead only if B lands at >= 0.2 mm on 316 with in-band loss <= 0.0035.
  - Otherwise it records the cx-16.5 tie, and the knuckle lens's contact cell closes at 205 / 237 / 264 = uncleareable
    by the measured attribution.
- Pick 2: a 45-min gate 0 (C, then B, then A's exact J2-exit). On the kill, the cap-pole bound goes to FINDINGS.
- Neither pick is a 95 path. The 95 arithmetic still needs +17 takes at the lead, and the back-seat knuckle ceiling is
  269-271.
- The next planner should look outside the knuckle-at-the-back-seat family for reach, and treat any stop-based contact
  gain with section 4's control.

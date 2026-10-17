# Round 101 (J1, track jump) ideation: judge and red team (2026-10-17 ~17:45 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75)
at low complexity. Gate 0 bar for this round (docs/concepts/ROUNDS.md "Round J1 plan"): reach >= 0.80 or gap <= 15 with
<= 4 contact poses; a cell worse than 17.5 frozen exact dies with its number.

Lead to beat: slipper-nose-knuckle-3r, verified 18.49 (score 93.28; Bench(110,360) exact frozen, margin 5, O20), held out
23.45, complexity 22.25 (18.25 like-for-like), ledger WATCH. 4-active references (a sensed or spring-held joint in the
chain is a joint): minarc pick1 18.40 (complexity 32.5), skinnormal-shortk-4r 18.58.

Six candidates came in from the planner's two lenses: the humerus-axial J3 (lens 1: 3 candidates, all 3 active) and the
scapular spare (lens 2: 3 candidates, all 4 active). All six have 0 passive translations. After the duplicate check, the
hardware check and the red team, **two are picked**, both from lens 2. Lens 1 has no survivor: its three candidates are
variants of entries already queued elsewhere, and the proposer's own pre-screen on raw posed skin already measures each
one dead. Those numbers go to the queued entries' screens (section 3).

Scripts and logs for the judge's checks: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge101/`
(`graph.py`, `pksurv.py` / `pksurv.out`, `epi.py`). Every check runs on the repo's own bench and kit (Bench(60,160) fast
cache 0089c747c10f, Bench(110,360) poses), niced, single-threaded, local only (farm closed).

## 1. Red-team checks made by the judge

### 1.1 The "sparse-graph artifact" behind the stop-relay's death is real, and the flood instrument already exists

The lens-2 proposer says stop-relay-rocker-3r's `connected()` (docs/concepts/models/stop-relay-rocker-3r.py lines 196-229)
floods only the 360 Bench(110,360) workspace poses, a graph too sparse to carry a continuous motion. `graph.py` rebuilds
that graph from the bench itself, before any take mask:

- **157 components, the largest 10 poses, 52 isolated, mean degree 1.13**, the proposer's numbers exactly. The 360
  bench poses are a 1-in-4 subsample of the 15-deg envelope grid (17 planes x 12 elevations x 25 axial).
- A relay pose that is not a grid neighbour of another taken bench pose can never be reached, whatever the mechanism
  does. The stop-relay's "static gains are islands" verdict was therefore partly the instrument.
- **Correction to the proposal:** the full workspace grid has **1432** envelope poses (`CID == 'Workspace (envelope)'`),
  not 4488. The proposer's own `flood.py` selects exactly those 1432, so its numbers stand; only the count in the text is
  wrong.
- **Do not write a new flood.** A full-grid flood is already in the repo:
  `docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py` `flood(Mw, B, grid="full")` (1432 envelope nodes used as
  transit nodes only, scoring on the bench poses). The proposer's path-tracked multi-state version (scratchpad
  `flood.py`, ~120 lines) adds q0 tracking for the spare. Both picks use one shared, validated flood: it must reproduce
  ~0.67 on the 360-node graph and ~0.91 on the full grid for the stop-relay section-5 setup.
- Held-out poses (952 of the 1432) become transit nodes of the graph. That is connectivity, not fitting: nothing is
  scored or tuned on them. It must still be stated in the claim.

### 1.2 Pin-knee host + relay: only 53-68 % of the kinematic gain survives the hubs' own levels

The proposal reports each hub's skin requirement on the relay poses separately (hub 1 median 46-48 mm, hub 2 median
57-58 mm, p90 95-148 mm) and then assumes "about 70 %" of the kinematic gain survives. Survival is a joint condition:
both hubs must sit under the levels the plain chain is already fitted to. `pksurv.py` reuses the proposer's
instrument (`pkprox.py`: K3 requirement on hub-centre rays, Bench(60,160) fast, the pin-knee H1 axes, clamp policy) and
counts the relay (newly taken) poses on which **both** hubs clear the plain chain's levels:

| cell | relay poses | hub 1 clear | hub 2 clear | both clear (p98 levels: hub 1 48, hub 2 60 mm) |
|---|---|---|---|---|
| back c = bvec(43, 47), a0 35, T 60 | 26 | 17 | 18 | **15 (0.58)** |
| back, T 40 | 22 | 17 | 15 | **15 (0.68)** |
| cap c = bvec(41, 65), a0 25, T 60 | 15 | 10 | 8 | **8 (0.53)** |

- The plain chain's hub-2 **max** level reads 400 mm: on one plain pose the K3 march escapes its 220 mm limit. The p98
  (60 mm) is the real level. Any "<= plain max" statistic for hub 2 is meaningless.
- **T 40 keeps the same 15 survivors as T 60.** Every relay pose that the extra travel from 40 to 60 deg adds fails
  proximity. Gate 0 should start at T 30-45, not 60.
- The failing poses are the round's two known binders, not new ones:
  - scapular-plane overhead (plane 0-30, elev 135-150, axial -45..0): hub 2 needs 86-189 mm, under the acromion and
    toward the neck. These are the lead's "folded 15".
  - the overhead internal-rotation fan (plane 105-120, elev 165, axial -90): hub 2 needs 71-73 mm.
  - hub 1 needs 51-58 mm against its 48-49 mm level on 4-6 poses, and up to 81 mm on one pose (plane 15, elev 135,
    q0 -58).
- **Re-estimate.** Bench(110,360) kinematic gain from the back cell: +0.166 (0.731 -> 0.897). At 0.58 survival that is
  +0.096 reach, so 0.658 -> ~0.75 and v_gap 27.2 -> ~17.6. Then subtract the in-band cost of raising hub 1 by 3-10 mm
  and the knee-window losses the kinematic flood never checks. Expected **18-22 frozen**: a tie with the 4-active
  references, not a clear lead. Chance of <= 17.5: about 1 in 4. It is still the only candidate this round with a
  measured path to the bar.

### 1.3 Epicondyle hub: an O20 hub on the GH -> lateral-epicondyle axis has no room outside the skin

EPI_RESULT

### 1.4 Complexity (tools/simplicity.py v2.2, `--score` on the mechanism records)

- pinknee-scapular-relay-4r: **31.5** (clamp, 1 spring: +25 active DOF, +1 body, +1 joint, +3 spring, +1.5 parts; the
  unsensed two-pin cuff knee scores 0). **34.5** with the twin springs.
- acromion-relay-4r: **31.5** (34.5 twin), matching the proposer.
- Against: minarc pick1 32.5 and the lead 18.25. Even a tie on the bench costs ~13 complexity points over the lead,
  and the user prefers 3 joints. A 4-active pick must therefore beat the lead by a clear margin to matter: <= 17.5
  frozen and better held out.

## 2. Verdicts

| # | id | lens | active / passive / transl. | verdict | reason (measured) |
|---|---|---|---|---|---|
| 1 | **pinknee-scapular-relay-4r** | 2 | 4 / 2 (cuff knee) / 0 | **PICK 1** (absorbs acromion-twinspring-4r's twin policy as a determination cell) | Only candidate with a measured path to <= 17.5. Verified host (v_gap 27.2, ib 0.895, gap = reach). Kinematic connected 0.828-0.897 (overhead 17-24/28) on the full grid. Judge: 53-68 % of the gain survives both hubs' levels, giving 18-22 expected. Every joint is a catalogue part. Spring + own-angle stops determine J0. |
| 2 | **acromion-relay-4r** | 2 | 4 / 0 / 0 | **PICK 2** (absorbs acromion-twinspring-4r) | Plain-host control for pick 1, built on the same shared full-grid flood, plus the stop-relay re-measure under the corrected instrument (an instrument change, reported separately). Measured 45.82 fast against the plain chain's 62.86 at the same seat. Hub 2 0.06 in band is the plain spherical 3R's own binder, which the relay does not move. Expected to die at gate 0 (38-45 fast); time-boxed to 30 min. |
| 3 | acromion-twinspring-4r | 2 | 4 / 0 / 0 | **MERGED** into picks 1 and 2 | Same metal as acromion-relay-4r; only the q0 policy differs (energy minimum of a J0 spring + a J2 spring). The proposal already says it drops into the pin-knee wrapper as the "twin" cell. Plain-host kit: 46.54 fast. Pin-knee host: connected 0.847 / 0.919 against the clamp's 0.828 / 0.897, with no stop impacts. Cost: J1 moves on 197-203 / 220 poses, two springs felt continuously (~1.9 N at the cuff), complexity 34.5. |
| 4 | axial-ring-gimbal-3r | 1 | 3 / 0 / 0 | **REJECTED**: duplicate of the queued armband-pointer, and measured dead | armband-pointer is the same morphology (closed thin-section armband at the distal arm + 2R pointer + lateral spar). Proposer's raw-skin pre-screen: KA045XP0 ring in contact on 169-204 / 220 poses at s 205-240, including all 85 arm-down poses. The distal arm is a ~68 x 115 mm ellipse about any GH axis. The twist-free spar's in-band ceiling is <= 0.56. The catalogue ring KA040AR0 does not fit the arm at all (220 / 220 poses exceed its bore). |
| 5 | epicondyle-hub-j3-3r | 1 | 3 / 0 / 0 | **REJECTED**: no real component fits at that place (1.3), and it is a variant of the queued cuff-sleeve-3r | An O20 disc normal to an axis 5.6 deg off the humerus cannot sit on the epicondyle: its plate would be perpendicular to the skin, not on it. Even without that, the spar has the same twist exposure (ceiling 0.53-0.56). |
| 6 | cap-race-twist-3r | 1 | 3 / 0 / 0 | **REJECTED**: variant of the queued acromion-pointer-arm-ctrack (and the inverse of the dead pointer-cslide), measured dead | The proposer's own pre-screen gives a 64 mm radial band (64-92 at s 70) over the needed +-90-deg arc, against a 12 mm band (skin spread 55-70 mm front / back, 98 mm medial). Its expected gap is > 60. An arm-fixed rail at s 35-55 also rises under the acromion in abduction >= 90, the recurring subacromial binder. |

Hardware and determinacy (CLAUDE.md "Manufacturable joints only"):

- All six map every joint to a real part: MR117-2RS pairs, MR63ZZ knee pairs, Reali-Slim KA045XP0, a Franke-type
  wire-race segment, music-wire torsion springs, O3 dowel-in-slot stops. The one exception is the epicondyle hub (1.3).
- None has a passive translation.
- No coordinate is undetermined:
  - the relays' J0 sits on a preloaded spring with own-angle stops, and the clamp's J2 on its own-angle stops;
  - the twin cell is set by a spring-energy minimum (k0 ~0.3 N.m/rad against the chain's <= 0.010 N.m sag and ~2 mN.m
    of seal friction: < 1 deg of dead band);
  - the cuff knee is set by the host's closure, as verified.

## 3. Ranking and what happens to the rest

Score = (expected gap reduction vs the champion 75.94) x (confidence) x (buildability: fewer passive translations first;
all six have 0):

1. **pinknee-scapular-relay-4r**: 75.94 - ~20 = ~56 x 0.5 (verified host; kinematic gain measured on the full grid;
   joint survival measured by the judge) = **~28**. The only candidate whose expected number (18-22) reaches the lead's
   neighbourhood.
2. **acromion-relay-4r** (+ twin): 75.94 - ~45 = ~31 x 0.8 (measured kit number) = **~25**. Its value to the outcome is
   the control (how much of pick 1's gain the relay alone buys), the shared flood instrument, and the corrected
   stop-relay number. It cannot reach the lead: its distal binder is the champion 3R's own.
3. cap-race-twist-3r: < 16 x 0.8. 4. epicondyle-hub-j3-3r: ~0-16, buildability 0. 5. axial-ring-gimbal-3r: ~0.

Forwarded to the queued entries (no new catalogue rows for the rejects; the screens of those ids should start from these
numbers instead of re-measuring them):

- **armband-pointer** <- axial-ring-gimbal-3r's ring scan (`axring/ringaxis2.py`, `ringfix.py`: KA045XP0 contact
  169-204 / 220, anteromedial arc inside biceps / flank in 78-99 % of arm-down poses) and spar ceiling (`spar.py`,
  `sparoff.py`: <= 0.56 at q 0.9-0.95). Unless the armband screen finds a ring position that clears the arm-down poses,
  it dies on these numbers.
- **cuff-sleeve-3r** <- the spar ceiling (same twist exposure) and the epicondyle hub check (1.3). The sleeve's 1 passive
  translation is what lets its axis run along the arm; the hub version cannot.
- **acromion-pointer-arm-ctrack** <- the cap skin-spread scan (12-23 mm over lateral +-50 deg at s 25-70; 55-70 mm at az
  60-120 / 240-300; 98 mm medial). A track at the cap must stay within lateral +-55 deg or follow the skin.

Planner lesson for the next round:

- Lens 1 (humerus-axial J3) is closed by conservation, measured on both sides. In a spherical 3R the humeral twist shows
  up either in th (J3 off the arm axis: the lead's fold losses) or under link 2 / a ring (J3 on the arm axis:
  proximity on the 2:1 elliptical arm).
- Lens 2's binder is hub 2, wherever J1 walks: hub 2 rides its a2-circle about the humerus-fixed J3. A relay only moves
  hub 2 along that circle.
- The next jump should move hub 2 itself, the subject of the lead's binder (posterior deltoid at K 29-65; the
  scapular-plane overhead fan). It should not move the base.

## 4. Picks (appended to docs/concepts/catalogue.json, status "ideated")

1. **pinknee-scapular-relay-4r**, lead note: test first whether hub 2 / hub 1 stay at the host's own levels on the relay
   poses (judge: 15 of 22-26 do). Start at T 30-45, check the knee window on every relay pose, and kill it at gate 0 if
   the frozen exact number is > 17.5.
2. **acromion-relay-4r** (+ twin cell), lead note: build and validate the shared full-grid flood first (stop-relay control
   0.67 / 0.91). Then a 30-min plain-host gate 0. Its distal binder (hub 2 0.06 in band) is expected to kill it at
   38-45 fast. Report the stop-relay re-measure as an instrument change.

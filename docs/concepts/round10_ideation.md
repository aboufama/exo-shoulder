# Round 10 ideation: judge and red team (2026-10-17 ~03:50 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)). The real target is gap 0, and 95
(gap 13.75) at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered; 3 active DOF is the aim, and a sensed 4th joint counts as a 4th DOF (user, 2026-10-17).

Lead to beat: roller-longdyad-knuckle-3r, verified at 18.67 (score 93.21, Bench(110,360) exact frozen, margin 5, O20),
held out 23.73. Ledger status: WATCH.

## Measurement change during judging (not a design change)

Commit 3ceacea (tools/simplicity.py v2, user ruling 2026-10-17) landed while this round was being judged. The unsensed
two-pin cuff knee now scores 0.

| design | complexity v1 | complexity v2 |
|---|---|---|
| the lead (roller-longdyad, pin knee) | 43.75 | **24.25** |
| kneeless-roller (no knee) | 23.75 | 23.75 |
| minarc pick1 (4 active, sensed K) | 52.0 | **32.5** |

Consequence for this round: deleting the knee now saves 0.5 complexity points and costs ~2.4 gap points. The kneeless
class is dominated by the lead (21.07 at 23.75 vs 18.67 at 24.25). So every lens-3 drive simplification (nose, groove,
dip) is re-aimed onto the lead, and the proposer's kneeless chain stays as the measured control cell. The planner's open
lever (4) ("deleting the knee halves cx") no longer holds.

## Red-team checks made by the judge

Scripts and outputs: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge10/`
(`fast4r.py`, `dipband2.py`, `thband*.py`, `p_*.json`, `dipband2_*.json`).

### 1. The 4R seeds, re-run in pick1's verified harness

Harness: `docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py`, imported unchanged, on Bench(60,160) fast. Pricing:
`tools/env_polish.py priced()`, which builds the J2 stops at +0.5 deg and cuts stop B where the 5-deg rule refuses the
stretched branch.

| config | plain | near1 | reach | follow | ib14 | contact | priced plain / near1 |
|---|---|---|---|---|---|---|---|
| pick1 (verified 18.40 frozen) | 11.57 | 15.94 | 0.806 | 1.0 | 0.894 | 0.0156 | (already priced) |
| skinnormal, unrounded search point | **11.38** | **11.38** | 0.806 | 1.0 | 0.890 | 0.0105 | 12.49 / 12.49 (stop B cut at dK 75.84 of 77.52) |
| skinnormal, the spec's rounded numbers (b3 0.37) | 11.87 | 11.87 | 0.800 | 1.0 | 0.892 | 0.0105 | 12.46 / 12.46 |
| stopb80 | 12.70 | 12.70 | 0.8125 | **0.95** | 0.897 | 0.0361 | 12.83 / 12.83 (stop B 80.3 not cut) |
| earlystop | 11.28 | 16.99 | 0.8125 | 1.0 | 0.895 | 0.0206 | 11.58 / 16.14 (cut at dK 68.36 of 71.21) |

- skinnormal's claim reproduces to the digit with the one-sided law. Its two-way spring (dKm) is idle, as the proposer
  said. The spec's rounded seed costs 0.49, so the catalogue carries the unrounded seed.
- stopb80 keeps metal off the skin (near1 = plain), but it loses 3 of 60 fit clip frames to skin (follow 0.95, on the
  threshold). The proposer puts hub K's side wall on the Raise-overhead peak frames (30, 150, -60).
- earlystop is dominated on near1.
- Pricing barely bites: stop B is cut by 0-1.7 deg of dK.
- The class limiter is the fast-to-frozen loss. pick1 went 11.57 -> 18.40 (+6.83 plain, +2.46 over near1), all of it
  contact on extreme envelope poses.
  - If near1 predicts frozen: 14.9 (skinnormal) / 15.3 (stopb80).
  - If plain does: 19.3 / 19.7.
- pick1's own stop-B scan says travel past dK ~45 bought ~0 on the bench (18.60 / 19.60 / 18.98 at 40 / 45 / 50 vs
  18.40 at 56.65). Its held-out red team found the arm-fixed knee link and pad pressed into the chest across the body
  when K is open 41-54 deg; stop B at 40 removes all 18 of those contacts. Seeds that open K to 76-80 must show this does
  not grow.

### 2. Springs

At 0.04 N.m preload, 0.010 N.m/rad (217 mm of 0.3 x 5 mm 1.4310 +C1900; E b t^3 / 12 L = 0.0100 checks):

- stress at dK 80.3: 6M / (b t^2) = 720 MPa;
- stress at dK 75.8: 710 MPa;
- 0.7 Rm = 1330 MPa, so both are inside.

pick1's K hold passes R17 upright only: 4.1-7.7 deg drift with the thorax tilted, in 3 of 4 directions over the 5-deg
rule. skinnormal leaves stop A on ~20 % of clip frames (its own kin record), so the hold check must be re-run.

### 3. The dipped K law: hub 2 on every pose of the band, not 3

**Share of poses in the dip band** (th from each design's own J1 / J3 seats):

| th band | kneeless clips | kneeless ws | lead clips | lead ws |
|---|---|---|---|---|
| [43, 68] | 28 / 110 | 66 / 360 | 23 / 110 | 56 / 360 |
| [45, 62] | 8 / 110 | 42 / 360 | 5 / 110 | 43 / 360 |

The clip th floor (43.0) is the Raise-overhead peak, not rest.

**The proposer's branch rule picks the wrong branch on the Raise-overhead peak frames.** twosided.py picks the branch by
the lower scapula-frame elevation. On those frames it reads hub-2 contacts of -7 to -18 mm on clips that the verified
designs follow cleanly. With the design's branch fixed (sigma -1), the baseline reproduces the proposer's depths to
0.01 mm and shows 0 clip contacts:

| pose | 182 | 203 | 230 | 208 | 211 |
|---|---|---|---|---|---|
| hub-2 depth, mm | -4.48 | -2.87 | -0.69 | -22.74 | -22.77 |

**Kneeless, 138 poses with th 36-72 (39 clip frames).** Closing a1e by 4 / 8 deg moves hub 2:

- closer (> 0.5 mm) on 0 poses;
- farther on 127 / 138 poses.

Hub-2 contacts fall 5 -> 3 -> 2:

| pose | a1e as built | a1e -4 | a1e -8 |
|---|---|---|---|
| 182 | -4.48 | -0.67 | +2.97 |
| 203 | -2.87 | +0.40 | +3.57 |
| 230 | -0.69 | +2.26 | +4.03 |
| 264 (near-touch) | 0.94 | 4.00 | 7.45 |

- The deep elev 135-165 pair (208 / 211) stays at -16 to -19 mm.
- 0 clip contacts at any dip.
- Median hub-2 clearance on clip frames goes 8.9 -> 10.5 mm, and none passes 14.

**Lead (crude: J3 direction without the b3 offset), 103 poses.** It reads 182 / 203 at -1.87 / -0.50 mm, against
kneewin's measured -1.67 / -0.03.

- 0 poses move closer.
- 182 / 203 clear at +1.79 / +2.79 mm already at a1e -4 (about -9 deg of K).

These are the two hub-2 contacts that killed kneewin-roller-knuckle-3r. Its frozen run
(`scratchpad/kw/frz_kneeB2.json`) lists the new poses:

- 182: hub 2 at -1.67 mm;
- 203: at -0.03 mm;
- 205: -4.48 mm, th 32, the folded side;
- 316: knee-E;
- five E-L2 jams.

So the dip is the round's only 3-joint lever on the limiter that killed all three lens-1 steps. Lead cell arithmetic:
19.33 - 2 x 0.548 = 18.24 if nothing else moves. That is below the lead, but by less than the 1-point rule.

**Unchecked:**

- links 1a / 1b, hub K, the crank (backward ~4 deg on the lead, ~8 on kneeless), the roller and the horn lug;
- clip-frame in-band (in-band is scored on clips, and 24-39 clip frames sit in the band);
- the spring-closed embodiment loads the drive through the whole dwell: ~19-26 N at the lobe follower, up to ~20 mN.m of
  J2 drag if it slides.

### 4. The hub-2 groove does not fit as proposed

| geometry | groove span | problem |
|---|---|---|
| groove-desmo: O2 dowel, 2.02 groove, pitch 7.6-8.9 | r 6.59-9.91 | 0.09 mm outer wall in the r-10 cap |
| dipped: dip pitch 7.07 | inner edge 6.06 | 0.44 mm into an O13 boss |

Re-sized fit window, with an ISO 8734 1.5 m6 dowel in a 1.52 groove, an O12 boss (+0.3 mm clearance) and a 0.8 mm outer
wall:

- pitch radius in [7.06, 8.44], i.e. at most 1.38 mm of radial travel;
- s_arm <= 3.85 for kneeless's 20.5-deg crank stroke (the proposal's 3.6 / base 7.1 / crest 8.4 fits);
- s_arm <= 4.2 for the lead's 18.7-deg stroke (the lead's lobe must be re-cut from r_lobe 8.24 to a ~7.06 base);
- s_arm <= 2.7 with the dip's extra 8.3 deg of crank.

This is gate 0 of pick 4 and the precondition of pick 2's cx-19.75 embodiment.

### 5. The wedge and the nose

**The wedge.** The arithmetic holds: 20.12 = reach 17.5 + contact 2.62 + in-band 0. The wedge's whole gain is the
0.95-point in-band term.

- The face moves 80 samples by up to 7.6 mm; the bearing seat and crown stay put.
- For it: the user's dimpled hub skin side (+1.8 honest points, FINDINGS score history).
- Against it: floating-centre-3r's skin-contoured plate, a share-metric gain.
- Ruling: allowed with disclosure. Every claim shows flat and wedged columns plus the crown height; the alignment
  auditor rules.

**The nose.** mu 0.05 is the optimistic end for a greased hardened pin on a DLC flank (boundary-lubricated pairs run
~0.05-0.12). So the proposer's mu 0.087 red team is the central case: PA_kin 38, dK_lim 42.2, fast +1.33.

**On the lead.** The lead's stroke is horn-PA-limited (dK_lim 46.5, horn PA 42.8; `scratchpad/kw/frz_leadF.json`
reproduces 18.67). That is the case where the nose keeps the stroke at PA_kin 40.

### 6. The three lens-1 steps are measured dead, and the measurements stand

`scratchpad/kw/frz_leadF.json` reproduces the lead at 18.67 in the proposers' frozen harness.

| candidate | frozen | lead in the same harness |
|---|---|---|
| kneewin | 19.33 | 18.67 |
| kneewin pad-moved | 19.56 | 18.67 |
| dogleg | 21.06 | 18.67 |
| stroke40 | 19.23 / 19.51 | 18.67 |

- The poses behind the knee wall and the drive wall come back as contacts or E-L2 jams.
- The dogleg's exposed pair (208 / 211) is hub 2 at -22 mm, deep elev 135-165. No lever in this round reaches it.

No candidate needs a passive translation. None has an undetermined passive coordinate:

- K is slaved and never read, or sensed (the 4R);
- the knee pins are closed by the cuff.

Every joint maps to a catalogue part (MR117-2RS, MR63ZZ, MR52ZZ, IGLIDUR-PIN, ISO 8734 dowels) or a machinable part. The
exception is the O2 hub-2 groove, which is re-sized above. No candidate duplicates a catalogue entry. Checked against
cam-unfold-4th (a two-sided cam on link 2), split-knuckle-twosided-3r (K2 on link 2), two-rise-lobe (a folded-side rise
that opens K, not a mid-band closing) and rim-lobe-arm's groove flange (a swept plate, not a groove inside the cap).

## Verdicts

| id | verdict | reason |
|---|---|---|
| skinnormal-shortk-knuckle-4r | **PICK 1** (merged: stopb80, earlystop) | The judge reproduced 11.38 = near1 in pick1's verified harness (priced 12.49), with follow 1.0 and contact 0.0105. It is the first config at pick1's reach with no metal under 1 mm at fast. It attacks the class limiter (the fast-to-frozen loss). 4 active, cx 32.5 (v2): the 4-joint route, never a 3-joint lead. |
| stopb80-knuckle-4r | merged into pick 1 (seed 2) | Same harness, topology, components and gate. Reproduced 12.70 = near1, but follow 0.95: the Raise-overhead peak is lost to hub K. Stop B 80.3 is not cut by pricing. K travel past ~45 bought ~0 on pick1. |
| earlystop-symk-knuckle-4r | merged into pick 1 (seed 3) | Same morphology. Dominated on near1 (16.99; priced 16.14). The spec's az2 = el2 = 42.70 looks like a copy slip: recompute with seats_for. Its useful knowledge: the Keemink wide arcs (law-only 0.944, 28/28 overhead) cannot park hub 2 with a th-only law. |
| dipped-law-groove-knuckle-3r | **PICK 2** (re-aimed; merged: kneewin's centred knee as the lead cell) | The only 3-joint lever on hub 2's abduction wall. The judge's 241-pose check: closing K moves hub 2 away on every band pose, with 0 new hub-2 contacts. Re-aimed to a spring-closed dip first (no new part), on the lead + centred knee (~18.2-18.8, cx 24.25) and the kneeless control. The groove + nose embodiment (cx 19.75) waits for pick 4's fit gate. |
| slipper-nose-knuckle-3r | **PICK 3** (re-aimed onto the lead) | Measured kneeless + wedge control 20.12 frozen, 21.13 flat. Under simplicity v2 its value is on the lead: cx 24.25 -> 22.0 at ~0 points if mu <= 0.05. Friction is the central risk (mu 0.087: +1.3 or more). The wedge is disclosed for the auditor. |
| groove-desmo-knuckle-3r | **PICK 4** (re-sized, re-aimed onto the lead) | Spring deleted, K positively held (no stop-A drift), cx 22.0 on the lead. The proposed O2 groove does not fit (0.09 mm wall); the O1.5 re-size fits with ~0.1 mm to spare (gate 0). It is the hardware the dip's cheapest embodiment needs. |
| kneewin-roller-knuckle-3r | rejected as a standalone: measured dead (19.33 vs 18.67); its centred knee lives on as pick 2's lead cell | All 9 knee poses come back as 5 E-L2 jams + 4 contacts. Two of those (182, 203: hub 2 -1.67 / -0.03 mm, th 55-58) are exactly the dip's targets. |
| kneewin-dogleg-roller-knuckle-3r | rejected: measured dead (21.06) | Clearing E-L2 exposes hub 2 / drive in the bunched deltoid (11 contacts). Its pair 208 / 211 sits at -22 mm, beyond the dip (-16 to -19 at a1e -8). |
| stroke40-roller-knuckle-3r | rejected: measured dead (19.23 / 19.51) | The drive wall and the m3e margin already coincide at th 106.7. The +2-3 stretched poses arrive as horn / hub-2 / link-2 contacts. |

## Ranking

The score is expected gap reduction vs the lead x confidence x buildability. All four have 0 passive translations.

| rank | id | expected frozen (Bench(110,360)) | confidence | cx (v2) | first test |
|---|---|---|---|---|---|
| 1 | skinnormal-shortk-knuckle-4r | 15-18.5 (score 93.3-94.5) | medium-low | 32.5, 4 active | frozen exact + held out of the 3 priced seeds in one farm batch; kill at >= 18.40 for all |
| 2 | dipped-law-groove-knuckle-3r | lead cell 18.2-18.8; kneeless 19.4-20.5 | low-medium | 24.25 -> 19.75 | the dip on the lead + centred knee, frozen, with the per-part split; D = 0 controls 19.33 / 21.07 |
| 3 | slipper-nose-knuckle-3r | lead cell ~18.7 (mu 0.05) / ~19.5-20 (mu 0.087); control 20.12 | high on the control, medium on the lead | 22.0 | the lead + nose at PA_kin 40 and 38, frozen |
| 4 | groove-desmo-knuckle-3r | lead cell ~18.7-19.0; control ~20.1-21.1 | medium after gate 0 | 22.0 | gate 0, the groove-fit annulus and link 2 vs the crank on both parents |

**Why the 4R ranks first and is still not the lead.**

- It is the only class whose reproduced fast numbers sit under 13 with metal off the skin.
- Its downside is bounded by a cheap kill rule.
- It carries a 4th active joint (+8.25 cx over the lead under v2), which it must earn in measured points.
- The user ruled 3 joints first: a 4R at 95 is the 4-joint route's number, not the lead.

**Picks 2-4 are one programme on the lead's drive.**

- The dip is the reach / contact lever.
- The nose and the groove are the complexity levers.
- Stacked on the lead they reach cx 19.75 with the dip.
- Run them in parallel, then combine whatever passes.

## Lessons for the planner

1. Under simplicity v2 the knee is free. Low-complexity levers now go on the lead, not on knee deletion.
2. Every lens-1 step this round died on hub 2's crown in scapular-plane abduction 90-105 with external rotation (poses
   182 / 203 / 230 on both parents). The dip is the first lever that moves hub 2 away there without touching the
   stretched stroke. If pick 2's frozen per-part split shows only hub 2 moving, the next lever is the dip on the lead
   plus the knee window, then the E-L2 dogleg on top.
3. Branch choice in standalone checks: an elevation-based rule picks the wrong closure branch on the Raise-overhead peak
   frames. Use the model's own ik branch.
4. The 4R class's open question is the fast-to-frozen loss, not kinematics. Pick 1's three frozen runs answer it in one
   batch.

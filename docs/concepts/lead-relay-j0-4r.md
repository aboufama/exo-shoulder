# lead-relay-j0-4r: a spring-centred J0 relay under the lead, with a real O20 hub 0 (4 counted joints)

Round 103 (J3, track jump), lens 1 "relay under the lead", pick 1. Model: `docs/concepts/models/lead-relay-j0-4r.py`;
sweep: `docs/concepts/sweeps/lead-relay-j0-4r.json`; row: `docs/concepts/rows/lead-relay-j0-4r.json`; motion preview:
`docs/concepts/viz/concepts/lead-relay-j0-4r.js`. **4 counted joints. The user prefers 3.** Every comparison below is
with the 3-joint lead conecut-knee-knuckle-3r (verified 18.28, Bench(110,360) exact, frozen).

## 0. The deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Price the metal first and the kinematics second. The ghost (a zero-size J0) answers "how many poses can a relay
     buy". The real question is "what does it cost to carry the relay". Hub 0 is grounded and axisymmetric about c, so
     its distance to the skin never changes with the arm. It is either always in band or never. At the ghost's seat it
     is never in band, and that sets the price before any pose is relayed.
   - Route link 0 as a machinist would. The spec draws link 0 as a bar descending the 20-deg arc. That bar crosses the
     annulus that hub K sweeps around J1 (hub K turns with J1, 15-33 mm off J1's axis, crown about 67 mm from GH). The
     first build clashed with hub K on 47 of 160 fit poses. The buildable link 0 is a turned standoff post that stands
     inside hub 1's own footprint, then a flat bar under hub 0's rotor plate. The model builds that. Hub 0 then has to
     ride higher still: r0 78.5 mm, not 76.5.
   - Scan the seat as well as the window. A cheap fit-bench scan (about 15 s per seat) over a0 x azu with real metal
     shows whether any seat brings hub 0 into band. None can: at every legal seat the chain's sweep sets r0 at 74-104 mm.
   - Not pursued, recorded for the planner: a J0 built as a thin-section ring or arc guide around hub 1 (a ring slide
     centred on c), so that J0's metal sits at hub 1's level instead of above the sweep. It breaks the user's "O20 only"
     hub ruling, and the smallest catalogue ring slides (about 90 mm OD) do not fit inside a 1 cm band.
2. **Rawest material.**
   - The posed skin itself, through the bench's signed distance: `B.dist` on every pose for hub 0's disc, rim, walls
     and crown, and for link 0.
   - The lead's frozen metal samples (981 per pose) and its per-pose dump
     (`docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json`).
   - The humerus rotations HG of every bench pose, which the relay rotates.
   - Skin height along c (the judge's `skinray.py` probe): median 45-48 mm, max 51-57 mm.
3. **Methods and tools.**
   - The lead's own model, unchanged (`conecut-knee-knuckle-3r.py`, SN_CELL=lead), frozen on Bench(60,160) fast.
   - The relay as a rotation of the arm seen by the chain: Q' = Rc(q0)^T Q, then every member turned by Rc(q0).
   - Policy (ii) by grid search over q0 in 1-deg steps: the lead's IK, knee window, closure, J3 stop, |dK| <= dK_lim and
     the J0-J1-J3 sub-chain margin >= 5 deg.
   - The kit's bench report, recomposed per stop window from per-pose records.
   - Hub 0's r0 derived on the fit bench (skin >= 2 mm on every pose, chain >= 1 mm on every pose the lead takes).
   - Stop window picked on the fit bench. Claim on exact Bench(110,360).
4. **What, other than me, shows the number is right.**
   - The bench (exact path) and the same composition run as a ghost: the ghost reproduces the judge's 15.78-15.90 class
     on the claim bench.
   - The lead's 18.28 reproduced by the q0 = 0 column with hub 0 stripped.
   - The alignment auditor's checks: in-sample window, contacts kept as contacts, near-touch shell.
   - The red-team pose list in section 4.

## 1. The mechanism as built (honest metal)

`scapula handler -> post -> J0 (O20 v5 hub 0, counted, spring-centred, own-angle dowel stops) -> link 0 (flat 12 x 3 Ti
bar under hub 0's rotor plate + turned standoff post on J1's housing crown) -> J1 -> L1a -> K -> L1b -> J2 -> L2 -> J3 ->
member 3 / E strap -> knee pins a / b (MR63ZZ pairs) -> arm pad / BOTTOM`. From J1 to the cuff it is the lead's frozen
record, untouched: stk 6.0, lE 97.14, lc 24.35, phiE 0.75, phib -91.80, J3 window [-111.90, 122.74].

- **Hub 0.** Axis c through GH, a0 20 deg from J1's axis at azimuth 45 (c = (-0.186, 0.780, 0.598) in the scapula
  frame). Underside at **r0 = 78.5 mm**, crown 90.75 mm.
  - r0 is derived, not free: it is the lowest underside at which hub 0 clears the skin by 2 mm on every fit-bench pose
    AND hub 0 + link 0 clear every chain sample by 1 mm on every fit-bench pose the lead takes.
  - That puts hub 0 about 30 mm over the skin along c (judge: median skin 45-48 mm on c). It is **0 % in band**.
- **Link 0.**
  - A 14.3 mm turned standoff post (r 6) stands on J1's housing crown, inside hub 1's footprint, which is the only
    place hub K's sweep never reaches.
  - From the post top a flat 12 x 3 Ti bar (26.7 mm to hub 0's axis, then a pad under the whole rotor plate) runs under
    hub 0.
  - Skin-facing samples: 76 for the bar and 25 for the exposed rest of hub 0's underside. That is 101 extra samples per
    pose, all 26-32 mm over the skin.
  - The descending bar the spec drew clashed with hub K on 47 of the 160 fit poses (measured in this model's first
    build).
- **J0 stops and spring.**
  - ISO 8734 2 m6 440C dowel in an arc groove of hub 0's lower plate (own angle), window [lo, hi].
  - Double-leg torsion spring, 1.4310 wire 0.95, D 22, 6 coils: rate E d^4 / (64 D n) ~ 0.019 N m/rad. With a
    0.08 N m preload the torque is about 0.10 N m at the window end (-59 deg). That is about 0.7 N at the cuff on a
    ~150 mm lever, and about 13 N at the lead's J3 dowel / slipper nose (155 N per N m), well inside the M5 WATCH
    range.

## 2. Results

See the row file for the full per-pose dump. Section 3 holds the claim numbers.

### Fit bench, Bench(60,160) fast (window picked here, never on the claim bench)

| state | gap | reach | ib14 | contacts |
|---|---|---|---|---|
| lead alone (frozen fit) | 12.50 | 0.775 | 0.9007 | 0 |
| hub 0 + link 0 worn, q0 = 0 | 20.83 | 0.775 | 0.8167 | 0 |
| **real, best window [-59, +18]** | **17.37** | 0.825 | 0.8167 | 3 |
| ghost (zero-size J0), same window | 9.54 | 0.825 | 0.9007 | 3 |

The relay buys 3.5 points, and carrying it costs 8.3. On the fit bench the window enumeration is exhaustive (99
(lo, hi) pairs, every breakpoint of the per-pose q0 set), so the sweep over the window is converged by construction.

# Shared modelling kit (tools/concept_kit.py)

Why: in the last screening round ~48 agents each re-implemented the same helpers (frames, two-circle closure, skin
march, hubs, straps, collisions, sweep files) in 500-700 lines per model. The kit holds the COMMON KIT K0-K7 of the
catalogue specs once, vectorised over all bench poses and tested against brute force, so a morphology model is
**members + a closure + params** in ~70-150 lines and costs ~1-3 s per configuration on Bench(60, 160).

Start from `docs/concepts/models/_template.py` (the champion spherical 3R written with the kit conventions, every
line commented for a new author). `docs/concepts/models/baseline-3r-kit.py` is the same design with the baseline's own
conventions and reproduces `docs/concepts/rows/baseline-3r.json` exactly.

## Model contract

```python
import concept_kit as K
def build(B, F, p) -> K.Chain:         # geometry from F ONLY (K2 calls it again on interpolated frames)
    p1 = F.S(K.bvec(az, el)); p3 = F.HG(K.wdir(d, a))                         # K0
    p2, ok, margin = K.closure(p1, p3, a1, a2, sigma, margin_deg=K.FOLD_MARGIN)   # K1 (ranges: ok &= ...)
    q = np.stack([K.axis_angle(p1, F.S([1, 0, 0]), p2), ...], -1)            # joint values for K2 (deg)
    members = [K.hub_member("hub1", p1, "J1"), ...,                           # K4
               K.strap_member("link1", p1, p2, ("J1", "J2"), ramp_to=(("hub1", K.STACK), ("hub2", 0.0))),   # K5
               K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]                     # K7
    return K.Chain(members=members, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3), info={...})
rep = K.evaluate(B, build, params)     # K3 fit, K2, K6, bench scoring
best, rows = K.sweep(B, build, configs, "docs/concepts/sweeps/<id>.json")
K.write_row("<id>", name, rep, family=..., active_dof=3, passive_dof=0, n_configs=len(rows), verdict=..., note=...)
K.log_event(f"screened <name>: gap {rep['gap']} (baseline 68.93)")
```

## API

| | |
|---|---|
| `bench(n_clip, n_ws)` | `concept_bench.Bench` (fast grid cache when built) |
| `frames(B)` -> `Frames` | per pose (P = all bench poses): `RS`, `RHG` (= RS @ HG, the band humerus frame), `RH` (body_pose humerus), masks `clip`, `ws`; `F.S(u)`, `F.HG(u)`, `F.H(u)` map local directions (u may be (3,) or (n, 3)) |
| `bvec(az, el)`, `wdir(d, a)` | K0 directions, identical to band_impl / concept_baseline (tested) |
| `axis_angle(k, ref, v)` | signed angle about k from ref to v (joint values) |
| `closure(b, w, a1, a2, sigma, margin_deg)` | K1 -> `p (P,3)`, `ok`, `margin`; `closure_residual(...)` for the honesty check |
| `FOLD_MARGIN` | the J1-J3 fold margin (deg) of every J2 dyad, in ONE place: 5 since the user's 2026-10-16 ruling (was 10); `CB_FOLD_MARGIN=10` re-measures at the old rule. Models pass it as their `margin` default (never a free search parameter); the seed-offset-3r-slides `SING` (osn, pin knee, raglan knee, knuckle, arc knee) reads it |
| `hub_rad(x, declared)`, `O20_ONLY` | "Keep O20 only" (user 2026-10-16): every hub radius a search or verifier sets is O20 (rad 10, 12.25 stack); `CB_ALLOW_SLIM=1` re-measures an old slim-hub claim only |
| `continuity(B, q, ok)` / `continuity_dense(B, F, build, p, ok)` | K2 (see below) |
| `dist_many(B, I, P)` | signed distance of points each in its own pose, one vectorised gather on the grid cache (= `B.dist`, tested) |
| `requirement(B, I, D, mode)` | K3 per ray: `'march'` (default) or `'outer'` (the baseline's) |
| `strap_dirs`, `cap_dirs`, `disc_xy`, `rect_xy`, `plane_frame` | sampling |
| `Member`, `Chain` | the data model (docstrings); kinds `free` (skin-fitted underside per sample), `cap` (one radius), `flat` (K4 plate at h_F) |
| `hub_member`, `strap_member`, `neck_member` | K4 / K5 / K7 members |
| `fit_profiles`, `member_points`, `collisions` | K3 fit with quantile q over the fit poses (a member with `over` lifted to a fixed point of `over` + climb, 2026-10-18), K6 |
| `evaluate(B, build, params, q=None, mode='march', cont=True, collide=True)` | report: `reach follow inband14 inband10 contact gap`, `inband_member`, `mass_g` (Ti 4.43 g/cm3), `mass_g_strap55` (straps at 5.5 mm), `closure` (share of poses the chain closes in), `flips`, `collide`, + `Chain.info`; `B._kit_last` keeps chain, profiles and points for plots |
| `sweep(B, build, configs, out_json)` | writes the sweep file after EVERY configuration: list of `{k, t, params, inband14, inband10, reach, follow, contact, gap, closure, mass_g}` |
| `write_row(id, name, rep, ...)` | `docs/concepts/rows/<id>.json` with the screen2.js fields (v_* null until verified); refuses a report that is not `honest` unless `force=True` (the row then carries `honest: false`, `checks`, `audit`) |
| `audit(...)` (run by `evaluate`) | report fields `honest`, `checks` (mode, cont, collide, q), `audit` (problems), `sample_mm` (median sample spacing per member), `hubless`; raises if a joint has no member centred on it and is not in `Chain.hubless` |
| `log_event(text, kind)` | appends `{"time", "kind", "event"}` to docs/concepts/events.jsonl |

## Conventions (and where they differ from the spec text, measured)

- **Frames.** RS = `B.frames(i)['S'][0]` (tested). The band's humerus frame (where `wdir` and every band W live) is
  `RS @ HG` from the pose file; `B.frames(i)['H'][0]` (body_pose) differs from it by a CONSTANT rotation of ~12 deg
  (`RH = RHG @ C`). The spec line "a humerus-frame direction maps to RH @ u" combined with "wdir matches band_impl" is
  therefore off by 12 deg: use `F.HG(wdir(...))` for band axes and `F.H(u)` only for body_pose-frame data (BOTTOM's
  bar Wb, Db). The champion's numbers are only reproduced with `F.HG`.
- **Sampling** = the baseline's: straps every 2 mm along and across laid out at r_ref = 70 mm (so a strap fitted at
  107 mm is 1.5x wider and coarser - the baseline does this too; collisions scale sample extents with radius),
  baseline cap hubs every 2.5 mm, kit flat hubs every 2 mm in true mm. In-band is a share of samples, so keep every
  skin-facing surface at this ~1 pt / 4 mm2 density.
- **K3 requirement.** `'march'` = the spec: first t on the 1 mm lattice 15..220 with dist >= 2 and >= 0 over
  [t, t+15]; skips only lattice points the 1-Lipschitz distance rules out, so it equals a brute 1 mm march (600/600
  rays on 4 real poses, test). `'outer'` = `concept_baseline.skin_radius` + 2 (inward sphere trace to the outermost
  skin, + 2 mm radially; identical to it, test). On the champion's 137 k rays the march sits a median +0.59 mm higher
  (lattice round-up, and 2 mm normal clearance needs > 2 mm radially on oblique skin); 11.8 % of rays > 1 mm higher,
  0.6 % > 1 mm lower. Effect on the champion: gap 68.93 -> 70.27 (in-band 14 0.438 -> 0.425). The march is the
  honest one; quote `mode` with every number.
- **Fit poses** = poses where the chain closes (after K2), clip and workspace. Underside = quantile q over them
  (`params['q']`, default 1.0). q < 1 makes the worst poses contact poses, which count as NOT taken.
- **K4 hubs.** `hub_member`: flat 10 mm disc normal to the axis at h_F = max over its samples of quantile_q(the K3
  march of that sample ALONG the axis from its true in-plane offset - a plane's points move along its normal);
  member thickness 12.25 (F to crown) for collisions and mass. Lower member skin face at F,
  upper member underside at F + 3.15 (`K.STACK`): say which with `ramp_to=((hub, dz), (hub, dz))`. The nominal
  directions `D` (laid out at `h0` = 70 mm) are no longer used for the fit (see Verification, bug 1).
- **K5 straps.** 12 x 3 mm default, climb limit 60 deg applied AFTER the hub ramps (raises only), mass also reported at
  5.5 mm.
- **K2 continuity.** The spec rule (25 deg between consecutive bench frames, `cont='frames'`) is wrong on this bench:
  60 clip frames over 6 clips are ~10 per clip, so real fast motion exceeds 25 deg between frames - it flags 25 of 60
  frames of the champion, which never flips (follow 1.00 -> 0.58). The kit default `cont=True` interpolates the motion
  between consecutive taken frames (scapula and humerus slerped, <= 2 deg steps), rebuilds the chain there, and drops
  the frame if the chain fails to close anywhere on the way or any joint jumps > 25 deg between 2-deg steps (a branch
  flip or a pass through a singularity): champion 0 flips, a constructed branch switch is caught (test). The same
  25 deg-per-step test runs on every joint AXIS in `Chain.joints`, so a flip is caught even if `q` omits a joint
  (champion: max 3.1 deg joint value and 2.5 deg axis motion per step along all 6 clips).
- **K6 collisions.** Every member pair: samples nearer than hw_a + hw_b + 1 mm (arc at radius) with radial intervals
  [r, r + t] closer than 0.5 mm (the spec's "+0.5 mm"; so K6 itself enforces 1 mm lateral but only 0.5 mm radial
  part-part clearance, `over` builds 1 mm) -> the pose is not taken; joint partners exempt within HUB_R + 2 mm
  of the shared joint. To avoid collisions by construction, give the upper part `over=[(name, 1.0)]`: its underside is
  raised to the other's top + 1 mm wherever they meet in any fit pose (the template's link 2 over link 1 and the neck:
  without it 34 % of the template's closing poses collide; link 2 then pays for it: 5 % in band). Since 2026-10-18 the
  lift and the K5 climb repeat until nothing rises, so the FINAL profile satisfies `over` (one pass did not: see
  "Measurement change 2026-10-18"). It clears K6 as `_over` tests the pair (lifted member first); K6 tests pairs in
  `Chain.members` order and `_near` is not symmetric, so a lower-first pair can still be rejected (same section).
- **K7.** `neck_member(F, p_from)`: 14 x 6 strap from the arm-end plate (direction p_from) to the start of BOTTOM's bar
  (RH @ (67.5 Wb + 40 Db)), K3 underside, K5 climb.

## HONESTY RULES (every model; the verifier checks them)

1. Every part at real size: hubs 20 mm with the 12.25 mm stack, straps at their real width and thickness, rails,
   carriages, ring bearings with their section. Nothing that is metal is left out of `members`.
2. Every skin-facing surface sampled at ~1 pt / 4 mm2 (the kit's helpers); never sample only near the skin.
3. Closure residual < 0.5 mm / 0.5 deg (`closure_residual`, put it in `Chain.info`); iterative closures must report it.
4. Joint and slide ranges enforced in `ok`.
5. >= 1 mm part-part clearance: K6 on (`collide=True`), or `over` by construction.
6. Branch continuity along every clip: `cont=True` (dense). Give every joint and slide value in `Chain.q`
   (slides in mm need `q_period=None`, or a separate scale).
7. Held-out clips (Wave, Walking) are never used; the bench excludes them - do not load them.
8. No undetermined passive coordinate: every coordinate is set by the 3 actuators + the closure (it would sag
   unpowered, R17). A passive slide must be solved by the closure, and its value goes into `q`.
9. Quote numbers with `mode` and the bench size; the screening bench is Bench(60, 160) on the fast grid cache, and
   winners are re-checked on the exact path / the full bench by the verifier.

## Measured (2026-10-15, Bench(60, 160), fast grid cache, 4 shared cores at load ~15)

| model | conventions | gap | reach | follow | in-band 14 | in-band 10 | contact | CPU s / eval | wall s |
|---|---|---|---|---|---|---|---|---|---|
| rows/baseline-3r.json | concept_baseline.py | 68.93 | 0.775 | 1.000 | 0.4381 | 0.2789 | 0.1024 | | |
| baseline-3r-kit | baseline (`outer`, no K2/K6) | **68.93** | 0.775 | 1.000 | 0.4381 | 0.2789 | 0.1024 | 0.6 | 1.2-1.8 |
| baseline-3r-kit | kit checks (`march`, K2 dense, K6) | 70.27 | 0.775 | 1.000 | 0.4247 | 0.2665 | 0.1024 | 0.7 | 1.3-2.5 |
| _template | kit conventions (flat O20 hubs, 12x3 straps, K7 neck, `over`), q 0.95 | 69.29 | 0.7625 | 1.000 | 0.4568 | 0.2975 | 0.1122 | 1.2-1.3 | 1.8-2.0 |
| _template | same, q 1.0 | 65.05 | 0.9062 | 1.000 | 0.2495 | 0.1575 | 0.0 | 1.2 | 1.6 |

The kit reproduces the baseline row exactly (every metric to 4 decimals). The template is the same design at real
part sizes: in-band 14 rises (wider straps and the neck sit closer), reach drops (12 mm straps, neck); Ti mass 127 g
(164 g with 5.5 mm straps) before the K4 fix, 125 g after. Hub 2 is never in band (it floats at 105 mm) - the
champion's known weakness. (Before the verification the template read 70.19 at q 0.95 and 79.53 at q 1.0: bug 1.)

Baseline quirks found while reproducing it (kept in baseline-3r-kit.py for fidelity, fixed in the template): the
link ends are raised by 2 x (link level - hub level) over their hub (the stack offset is added twice); cap hubs and
straps laid out at r_ref 70 grow with radius (hub 2 at 107 mm is a 31 mm disc) and shrink below it (hub 1 at ~52 mm
covers 56 % of an O20 disc, reaches 7.5 mm: the audit flags it); no continuity or collision check.

## Tests

`OMP_NUM_THREADS=1 python3 -m pytest -q tools/test_concept_kit.py` (25 tests, ~20-45 s): directions vs band_impl, frames
vs Bench, closure vs a brute-force circle scan on random vectors (both branches) and near-degenerate cases (b ~ w,
tangent circles), K3 march vs a brute 1 mm march on real poses, `outer` vs concept_baseline, `dist_many` vs
`B.dist` (incl. points outside the grid box), collisions on constructed hit / miss / exempt cases, `over`, K2 on a
constructed flip (frames rule and dense rule), and the baseline row reproduction. Since 2026-10-18: the `over` lift is
a fixed point and clears K6 where one pass collided (constructed), no `over` pair K6-collides on the template and the
remote-pole four-bar cluster layout, and a strict xfail that records `_near`'s pair-order residual (it starts failing,
on purpose, the day that residual is fixed).

Status 2026-10-18 (Bench(60,160) fast cache built locally, Python 3.12 venv): 23 passed, 1 xfailed, 1 failed. The
failure is `test_template_runs_on_kit_conventions` (collide 0.0095 != 0): hub 1 vs hub 3 (2 poses) and hub 1 vs the neck
(1 pose), no `over` pair. It fails identically with the kit before the 2026-10-18 change (base 9eb026a3), so it is not
this change's (why it started failing was not investigated here).

## Verification (adversarial verifier, 2026-10-15)

Checked independently on Bench(60, 160), fast grid cache, my own reference code for each item (scripts in the
verifier's scratchpad, the lasting ones are now tests 19-22).

| item | what I did | result |
|---|---|---|
| K1 closure | re-derived by rotation (w = c b + s e1, cos phi = (cos a2 - c cos a1) / (sin a1 sin theta), sigma = sign sin phi); 120 000 cases, both branches: random, b ~ w (theta < 1e-3 deg), theta within 0.3 deg of abs(a1-a2), a1+a2 and 360-a1-a2, antipodal | 0 ok mismatches, 0 branch mismatches, max p error 5e-11, residual < 1e-6 deg; margin equals the spec formula (to 2e-4 deg at the arccos ends) |
| K3 march | own brute 1 mm march on the champion's 667 rays in 7 real taken poses (4 clip, 3 ws) + 6000 random rays | 4668/4669 identical, 1 ray 1 mm off (trilinear grid is not exactly 1-Lipschitz); random rays all identical |
| K4 h_F | own march of every disc sample along the axis from its true offset (a plane's points move along its normal) | **bug 1** (below) - fixed, now identical |
| K6 | 20 constructed cases: lateral 2.0/2.9 mm hit, 3.1/4.0 miss; radial gap 0.3/0.45 hit, 0.55/1.0 miss; partners crossing 49 mm from their shared joint hit, at the joint exempt; non-partners at the joint hit; one-pose collision flags that pose only; not-ok poses never flagged; flat hub over a strap: gap 0 hit, 2 mm miss | all as the spec says; radial clearance enforced is 0.5 mm (spec), not the 1 mm of honesty rule 5 - docstring corrected |
| K2 | champion along the 6 real clips: frame-to-frame jumps up to 79 deg (so the literal rule is wrong, confirmed), dense steps max 3.1 deg (q) / 2.5 deg (axes), 0 flips; a model that switches branch but reports q = 0 | **bug 2** (below) - fixed |
| baseline | `tools/concept_baseline.py` and `baseline-3r-kit.py` re-run independently, same bench | identical on every metric: gap 68.93, reach 0.775, follow 1.0, in-band14 0.4381, in-band10 0.2789, contact 0.1024 (p95); kit honest 70.27 |
| speed | 3 runs each, load ~10 | baseline conventions 0.46 CPU s (0.6 wall); honest 0.7 CPU s (1.0-1.4 wall); template 1.2 CPU s (1.8-2.0 wall) incl. the new audit |

Bugs found and fixed (each with a test):

1. **K4 hub level wrong (numbers changed).** h_F was the requirement along rays laid out at a nominal 70 mm height,
   projected on the axis; a disc at another height has its samples on other rays. Hub 1 (true 54 mm) was fitted at
   52.6 mm and sat 1.36 mm from the skin in every pose (below the 2 mm rule); hub 2 at q 1.0 got 400 mm (a tilted
   ray never cleared in 220 mm -> inf) instead of 161, which dragged both links to 400 mm. Now every disc sample is
   marched along the axis from its true offset (`requirement(..., O=offsets)`). Template: q 0.95 70.19 -> 69.29,
   q 1.0 79.53 -> 65.05. Cap hubs (the baseline) are unaffected.
2. **K2 trusted the model's own q.** Dense continuity looked only at `Chain.q`; a chain that omits or zeroes a joint
   value passed a real branch switch (constructed: 0 flips caught), and a Chain with `q=None` skipped K2 silently.
   Now every joint axis is followed too (25 deg per 2-deg step), and `cont` with neither q nor joints raises.
3. **Strap layout not pose-local.** `strap_dirs(ang=None)` used the mean u-v angle over ALL poses (incl. poses the
   chain does not close in) for every pose, so a strap whose arc varies did not end on its axis, and the layout
   changed with the pose set (dense K2 rebuilds on other frames). Now each pose uses its own angle, the sample count
   the median. No number changed for closure-built links (constant arc).

Honesty holes closed (`audit`, run by every `evaluate`; `honest` = march + K2 + K6 + clean audit):
skipped hub -> ValueError unless the joint is declared in `Chain.hubless` (listed in the report); hub smaller than O20
(< 75 % of the disc within 10.5 mm or reaching < 9.5 mm) -> flagged (it flags the baseline's own hub 1, a quirk);
sparse sampling (median spacing > 4 mm at real radius) -> flagged, spacing reported per member; build not pose-local
(uses B or all-pose statistics, so dense K2 and the fit see different geometry) -> flagged; held-out clips in the bench
-> ValueError; checks off (`outer`, `cont=False`, `collide=False`) -> `honest` false; `write_row` refuses a non-honest
report unless `force=True`, and stores `honest`, `checks`, `audit`; sweep entries carry `honest` and `kmode`.
Verified: the sweep file is rewritten after every configuration with all of them (not best only), and its gap equals
`concept_bench.gap_of` (it is `B.report()`'s); contact poses never count as taken (B.report).

Holes that remain (the verifier must look): a member that samples only part of its surface at the right density
(the kit cannot know the true outline), understated thickness `t`, a sweep re-run with `resume=False` that drops
earlier configurations, `n_configs` written by hand, a model that reads poses outside `B` (only held-out clips in
B are caught), monkey-patching the kit.

## Measurement change 2026-10-18: the `over` lift is a fixed point

**A MEASUREMENT change, not a design change**: no model, configuration or row was edited; numbers move only where the
kit measured them wrongly before. Re-measure the old way with the kit at 9eb026a3 (`git show 9eb026a3:tools/concept_kit.py`).

**The bug.** `fit_profiles` ran ramps -> `_over` -> K5 climb ONCE per member. `_near` judges each sample at the member's
CURRENT radius, and the shared-joint exemption is an arc there (angle x radius / layout scale <= HUB_R + 2), which
grows as a sample below r_ref = 70 mm rises. So a sample that `_over` left alone (exempt at its pre-climb radius) could
be lifted by the climb, from the samples `_over` had raised further out, into the partner's layer, no longer exempt,
and K6 rejected the pose. Found on remote-pole-fourbar-j2-3r's cluster layout: crank A vs link 1 ~17 mm from their
shared A0 axis, link 1 at 87.5 mm over crank A's 87.0 (top 90.0), where `_over` on the final profile asks for 91.0.

**The fix** (`fit_profiles`, nothing else in the kit changed: `_over`, `_near`, `collisions` are untouched; `_climb` is
the old climb code moved into a helper): ramps -> `_over` -> climb, then `_over` -> climb again until no sample rises by
more than 1e-9 mm (both steps only raise, so it ends; > 20 passes raises a RuntimeError, never seen). A profile that
one pass already left at the fixed point comes back bit-identical, so a model where one pass was enough does not move.
Measured: every member that moved needed 2 passes (3 `_over` calls with the final check); a member that does not move
costs one extra `_over` call (the check).

**What moved.** Bench(60,160) fast cache, kit checks on (march, dense K2, K6, audit):

| model / configuration | gap old kit -> fixed point | collide | note |
|---|---|---|---|
| remote-pole-fourbar-j2-3r cluster layout (sweep k90) | 274.37 -> **133.04** | 0.9948 -> 0.2723 | link 1 over crank A: 190 of 191 poses hit -> 0 |
| remote-pole-fourbar-j2-3r best honest (k298) | 90.11 -> **87.62** | 0.088 -> 0.067 | link 1 over crank B cleared; dead verdict stands (control 63.18) |
| remote-pole-fourbar-j2-3r k46 | 90.59 -> 90.59 | 0.0785 | |
| remote-pole-fourbar-j2-3r PARAMS (lens-1 seed s1) | 245.81 -> 203.94 | 0.945 -> 0.695 | |
| spine-parked-j2-3r PARAMS (end_extra 0) | 56.80 -> **37.82** | 0.149 -> 0.011 | link 2 over link 1: 27 poses -> 1 |
| zc-frontier-3r PARAMS (end_extra 0) | 45.92 -> **34.50** | 0.124 -> 0.056 | link 2 over link 1: 22 poses -> 1 |
| slotted-eccentric-j2-3r PARAMS | 275 -> 275 | 1.0 -> 1.0 | crank over link 1 cleared, still no pose taken; Ti mass 124.0 -> 125.5 g |
| _template (q 0.95) | 67.87 -> 67.87 | 0.0095 | unchanged |

Breadth: of the 62 model files with `over`, 34 run through `K.evaluate(build, PARAMS)` (the other 28 need their own
entry points or arguments); at their PARAMS 30 are unchanged to the last digit and the 4 above moved.

**The verified leaderboard (30 rows) does not move.** Only 5 verifiers build kit members with `over` (arm-parked-knee-4r,
dwell-fourbar-knee-3r, j3-neck-over-3r, spine-parked-j2-3r, zc-frontier-3r). The other 24 with a committed harness never
call `fit_profiles`: each harness was run in full under the new kit with `fit_profiles` instrumented (its verified
command, flags and config), 0 calls in every one, and each reproduced its row's `v_gap` to the digit (cam-unfold-4th
26.70, conecut 18.28, crest 32.84, desmo-conecut 18.98, desmo-slipper 18.95, dipped-law 18.64, frontload 22.82, geneva
23.57, groove-desmo 22.64, k-rim 44.79, kneeless-roller 21.07, kneeless-sidecar 21.11, lowarm 17.96, minarc 19.54,
offset-skin-normal 41.02, raglan 27.82, roller-longdyad 18.67, sidecar-longdyad 18.91, sidecar-parallelogram 19.13,
sidecar-roller-flank 20.08, skin-normal cufflink 29.10, pin knee 27.20, slipper-nose 18.49, trimlug 18.51).
seed-offset-3r-slides has no committed harness and no `over` anywhere in its model. For the 5, every
`fit_profiles` call of the harness's Bench(60,160) fit gives bit-identical profiles with the fixed point (max difference
0.0 mm), and each harness re-run in full (Bench(110,360) exact, frozen from the Bench(60,160) fast fit, the verifier's
checks, Python 3.12 venv, local 4 cores) gives:

| row (harness, config) | v_gap recorded | old kit (9eb026a3) | fixed point |
|---|---|---|---|
| spine-parked-j2-3r (verify/spine-parked-j2-3r.py frozen, k7008 O20, rebase/sp20_m5.json params) | 41.00 | 41.00 | 41.00 |
| dwell-fourbar-knee-3r (verify/dwell-fourbar-knee-3r.py, verifier_checks params) | 37.66 | 37.66 | 37.66 |
| zc-frontier-3r (verify/zc-frontier-3r-gpu-skeptic.py frozen --fits fit60) | 33.51 | 33.51 | 33.51 |
| j3-neck-over-3r (verify/j3-neck-over-3r.py claim) | 28.46 | 28.46 | 28.46 |
| arm-parked-knee-4r (verify/arm-parked-knee-4r.py frozen_r12_botharc) | 26.71 | 26.71 | 26.71 |

Every field of each run record is identical between the two kits, except wall-clock times and the ORDER of one list
(j3-neck-over's `independent_audit.clip_big_steps`: the same 13 entries, clips iterated in another order).

**Why the leaders did not move, and what it means for their searches.** spine-parked and zc carry `end_extra` (the
strap-end hold past the shared-joint zone, 1.02 / 1.78 mm), which their searches found. spine-parked's note called it
a "K6 strap-end artifact" cleared by end_extra 0.24. That matches this bug: at the verified seats with end_extra 0 the
old kit rejects link 2 over link 1 in 18 poses (zc: 20), the fixed point in none, and the workaround no longer pays. At the verified seats, Bench(60,160) fast fit:

| seat | old kit, searched end_extra | old kit, end_extra 0 | fixed point, searched | fixed point, end_extra 0 |
|---|---|---|---|---|
| spine-parked-j2-3r k7008 | 36.20 | 42.32 (collide 0.103) | 36.20 | **32.61** (collide 0) |
| zc-frontier-3r v00 | 30.04 | 40.11 (collide 0.127) | 30.04 | **29.26** |

Worn on the verifier protocol (the rows' own harnesses, Bench(110,360) exact, frozen from the fast fit), fixed-point kit:
spine-parked-j2-3r k7008 with end_extra 0: **38.85** (verified 41.00; near-touch 49.98 vs 54.44; reach 0.617 vs 0.600,
in-band14 0.810 vs 0.805); zc-frontier-3r v00 with end_extra 0: **32.75** (verified 33.51; near-touch 39.78 vs 40.57).
These are DESIGN candidates (a changed parameter), measured by the agent that proposes them: not verified, rows
unchanged. What it means: searches run on the old kit steered `end_extra` (and possibly other strap-end / layer
parameters) to dodge this bug; a re-search of spine-parked / zc (and any family whose optimum carries such a hold) on
the fixed kit is the next step, and its winner needs an independent verifier.

**Not fixed here: `_near` is not symmetric (pair order).** `_near(A, B)` measures the arc at A's radius and adds B's
largest sample extent; `_over` tests (lifted member, partner) while K6 (`collisions`) tests pairs in `Chain.members`
order. When the partner comes first in the chain, K6's near set can be larger than the one the lift cleared, so a pose
can still be rejected. At the fixed point every `over` pair is clear tested lifted-member-first (test), but in K6's order the
cluster layout keeps crank A / crank B over hub J1 (36 / 6 poses) and the coupler over crank B (16): all 52 of its
remaining K6 rejections. Side experiment (NOT the kit; scratch `_over` testing each pair in K6's order): cluster layout
133.04 -> 82.76 (collide 0), k46 90.59 -> 88.31. The same lower-first residual is in the PARAMS of arm-parked-knee-4r
(link 2 over link 1, 14 poses), cap-nullspace-4r, seed-2r-cring, geneva-tail-knuckle-3r and stop-relay-rocker-3r, with
the old kit and the new alike (measured: every one of these hits is in a lower-first pair and none remains when the
pair is tested lifted-member-first). Fixing it is a second measurement change (the user's call); `test_over_pairs_clear_in_k6_order_with_lower_member_first` is a strict xfail that will flag the day it is fixed.

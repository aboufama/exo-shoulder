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
    p2, ok, margin = K.closure(p1, p3, a1, a2, sigma, margin_deg=5)          # K1 (ranges: ok &= ...)
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
| `continuity(B, q, ok)` / `continuity_dense(B, F, build, p, ok)` | K2 (see below) |
| `dist_many(B, I, P)` | signed distance of points each in its own pose, one vectorised gather on the grid cache (= `B.dist`, tested) |
| `requirement(B, I, D, mode)` | K3 per ray: `'march'` (default) or `'outer'` (the baseline's) |
| `strap_dirs`, `cap_dirs`, `disc_xy`, `rect_xy`, `plane_frame` | sampling |
| `Member`, `Chain` | the data model (docstrings); kinds `free` (skin-fitted underside per sample), `cap` (one radius), `flat` (K4 plate at h_F) |
| `hub_member`, `strap_member`, `neck_member` | K4 / K5 / K7 members |
| `fit_profiles`, `member_points`, `collisions` | K3 fit with quantile q over the fit poses, K6 |
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
- **K5 straps.** 12 x 3 mm default, climb limit 60 deg applied AFTER the hub ramps and BEFORE `over`, then `over` and
  the climb repeat until no sample rises (raises only; bug 4), mass also reported at 5.5 mm.
- **K2 continuity.** The spec rule (25 deg between consecutive bench frames, `cont='frames'`) is wrong on this bench:
  60 clip frames over 6 clips are ~10 per clip, so real fast motion exceeds 25 deg between frames - it flags 25 of 60
  frames of the champion, which never flips (follow 1.00 -> 0.58). The kit default `cont=True` interpolates the motion
  between consecutive taken frames (scapula and humerus slerped, <= 2 deg steps), rebuilds the chain there, and drops
  the frame if the chain fails to close anywhere on the way or any joint jumps > 25 deg between 2-deg steps (a branch
  flip or a pass through a singularity): champion 0 flips, a constructed branch switch is caught (test). The same
  25 deg-per-step test runs on every joint AXIS in `Chain.joints`, so a flip is caught even if `q` omits a joint
  (champion: max 3.1 deg joint value and 2.5 deg axis motion per step along all 6 clips).
- **K6 collisions.** Every member pair: samples nearer than hw_a + hw_b + 1 mm (arc at the SMALLER of the two
  samples' radii, each half extent at its own radius: symmetric, so the order of `Chain.members` does not matter) with
  radial intervals [r, r + t] closer than 0.5 mm (the spec's "+0.5 mm"; so K6 itself enforces 1 mm lateral but only
  0.5 mm radial part-part clearance, `over` builds 1 mm) -> the pose is not taken; joint partners exempt within
  HUB_R + 2 mm of the shared joint (each sample at its own radius, so a sample that rises can leave the zone). The
  smaller radius is the wider cone (conservative); the lateral distance at the pair's common radius would use the
  larger, a 3-5 % narrower cone where straps meet (it changes 0-2 % of poses on the models measured, bug 4). To avoid
  collisions by construction, give the upper part `over=[(name, 1.0)]`: its underside is raised to the other's top
  + 1 mm wherever they meet in any fit pose, on the final climbed underside (the template's link 2 over link 1 and the
  neck: without it 34 % of the template's closing poses collide; link 2 then pays for it: 5 % in band).
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
| _template | kit conventions (flat O20 hubs, 12x3 straps, K7 neck, `over`), q 0.95 | 69.27 | 0.7625 | 1.000 | 0.4570 | 0.2976 | 0.1122 | 1.2-1.3 | 1.8-2.0 |
| _template | same, q 1.0 | 65.04 | 0.9062 | 1.000 | 0.2496 | 0.1575 | 0.0 | 1.2 | 1.6 |

The template rows moved with the `over` / K6 fix (bug 4): 69.29 -> 69.27 and 65.05 -> 65.04 (in-band +0.0001-0.0002);
before it they read 69.29 / 0.4568 / 0.2975 and 65.05 / 0.2495, still reproduced by the old kit on this bench.

The kit reproduces the baseline row exactly (every metric to 4 decimals). The template is the same design at real
part sizes: in-band 14 rises (wider straps and the neck sit closer), reach drops (12 mm straps, neck); Ti mass 127 g
(164 g with 5.5 mm straps) before the K4 fix, 125 g after. Hub 2 is never in band (it floats at 105 mm) - the
champion's known weakness. (Before the verification the template read 70.19 at q 0.95 and 79.53 at q 1.0: bug 1.)

Baseline quirks found while reproducing it (kept in baseline-3r-kit.py for fidelity, fixed in the template): the
link ends are raised by 2 x (link level - hub level) over their hub (the stack offset is added twice); cap hubs and
straps laid out at r_ref 70 grow with radius (hub 2 at 107 mm is a 31 mm disc) and shrink below it (hub 1 at ~52 mm
covers 56 % of an O20 disc, reaches 7.5 mm: the audit flags it); no continuity or collision check.

## Tests

`OMP_NUM_THREADS=1 python3 -m pytest -q tools/test_concept_kit.py` (23 tests, ~20-45 s): directions vs band_impl, frames
vs Bench, closure vs a brute-force circle scan on random vectors (both branches) and near-degenerate cases (b ~ w,
tangent circles), K3 march vs a brute 1 mm march on real poses, `outer` vs concept_baseline, `dist_many` vs
`B.dist` (incl. points outside the grid box), collisions on constructed hit / miss / exempt cases, `over`, `over` on
the climbed underside of a strap ramped off a hub over a member that shares the joint, in every member order, and
`_near` symmetry (bug 4), K2 on a constructed flip (frames rule and dense rule), and the baseline row reproduction.

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
4. **`over` and K6 disagreed (2026-10-15; numbers of models using `over` moved, table below).** Found on
   scapular-race-j2-carriage: link 2 (`over` the race) collided with the race in 80 % of closing poses at its PARAMS
   (85 % in the run that found it). Two causes. (a) `fit_profiles` ran `over` on the underside BEFORE the K5 climb
   limit raised it, and a shared joint's exempt zone (HUB_R + 2 mm) is measured at each sample's own radius: a row
   just outside link 2's hub ramp sat at its raw ~55 mm, 11 mm (arc) from J2 -> exempt, so `over` skipped it; the
   climb then lifted it to ~73 mm, ~14 mm from J2 -> not exempt in K6, which found it 0.15 mm over the race.
   (b) `_near` measured the arc at member A's radius (with B's largest half extent): `_over` passes the upper member
   as A, `collisions` whichever comes first in `Chain.members`, so the two used different cones. Now the climb runs
   before `over`, then `over` + climb repeat until no sample rises (after the first pass only the samples that moved
   are re-tested: their verdict depends on their own radius only; 2-4 passes, bit-identical to re-testing all), and
   `_near` is symmetric (per pair hw_a + hw_b + 1 mm at the smaller radius; a per-row bound prefilters, the exact
   test runs on the candidates). Test: `test_over_sees_the_climbed_underside` (fails on the old kit at the K6
   assertion, and with only (a) fixed at the symmetry assertion). Outside check: an independent brute-force K6 (per
   pose, exact arccos, no prefilter or chunks) agrees with the kit pose for pose on 8 models after the fix, and no
   `over` pair is left in contact in any of them (with the larger radius instead of the smaller, 0-2 % fewer poses
   collide). The scapular-race workarounds (link 2 ramped over 16 mm instead of
   12, and listed first) are removed: at its PARAMS the model now reads 159.65 without them, 159.64 with them.
   posterior-max-margin-cardan carries its own workaround for (a) (a `fit_profiles` override with the climb first,
   and r_ref = 0.8 x its layout radius so the exemption never shrinks); left as is, its numbers do not move. Cost:
   the template 1.4 -> 1.6 s per evaluation, floating-centre-3r 6.0 -> 7.0 s (single process, idle machine).

   **Numbers of models using `over` moved.** Every kit model with `over` at its PARAMS, Bench(60, 160), fast grid
   cache, through the model's own entry point (`bench_eval` > `evaluate` > `K.evaluate`), old kit -> new kit (rows,
   sweeps and write-ups measured before this fix are on the old kit: re-measure before comparing with new numbers):

   | model (PARAMS) | gap | reach | follow | in-band 14 | contact | K6 collide |
   |---|---|---|---|---|---|---|
   | floating-centre-3r | 219.11 -> **84.82** | 0.2938 -> 0.7438 | 0.1333 -> 0.9167 | 0.2724 -> 0.3581 | 0.1406 -> 0.1168 | 0.6878 -> 0.0390 |
   | scapular-race-j2-carriage, without the workarounds (the model now) | 225.30 -> **159.65** | 0.0625 -> 0.3500 | 0.1333 -> 0.5500 | 0.3538 -> 0.3067 | 0.0526 -> 0.0532 | 0.7979 -> 0.0 |
   | scapular-race-j2-carriage, with the workarounds (as it was) | 155.40 -> **159.64** | 0.35 | 0.55 | 0.3071 -> 0.3068 | 0.0111 -> 0.0532 | 0.0426 -> 0.0 |
   | seed-2r-cring | 129.98 -> **126.00** | 0.4437 -> 0.4500 | 0.7333 -> 0.7667 | 0.3886 -> 0.3927 | 0.1154 -> 0.1194 | 0.0299 -> 0.0 |
   | annular-ring-3r | 104.91 -> **101.12** | 0.7625 -> 0.7688 | 0.9167 -> 0.9500 | 0.1278 -> 0.1245 | 0.1061 -> 0.1045 | 0.0341 -> 0.0195 |
   | crown-ring-3r | 88.17 -> **86.91** | 0.8875 -> 0.9125 | 0.9167 | 0.0641 -> 0.0642 | 0.0 | 0.0248 -> 0.0050 |
   | risley-turret | 94.73 -> **94.67** | 0.65 | 0.90 | 0.2527 -> 0.2533 | 0.0 | 0.0 |
   | _template, q 0.95 / q 1.0 | 69.29 -> **69.27** / 65.05 -> **65.04** | 0.7625 / 0.9062 | 1.0 | 0.4568 -> 0.4570 / 0.2495 -> 0.2496 | 0.1122 / 0.0 | 0.0 |

   Unchanged on every metric: back-anchored-ring-3r 90.95, clavicular-front-route 141.38, fivebar-roll 297.38,
   pointer-cslide 270.0, posterior-max-margin-cardan 91.16, rail-elbow 71.15, seed-pauldron-shells 79.46,
   trombone-arc 91.08, baseline-3r-kit (no `over`: 68.93 baseline conventions, 70.27 kit checks); the template
   without `over` still collides in 34.15 % of its closing poses. Most gaps fell: poses K6 used to reject wrongly are
   taken. The scapular race's rose because the 4 % of poses K6 rejected there are contact poses at q 0.95: still not
   taken, now counted as contact (the gap weighs contact, not collisions). annular-ring-3r and seed-2r-cring wrap
   `K.collisions` (they drop their by-construction pairs) and get the fix through it. A model's K6 can also move
   without `over` (the symmetric cone, B's half extent per pair): the two cases measured (baseline-3r-kit, the
   template without `over`) did not.

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

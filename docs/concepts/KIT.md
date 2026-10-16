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
| `fit_profiles`, `member_points`, `collisions` | K3 fit with quantile q over the fit poses (`over` + climb to a fixed point), K6 |
| `hub_zones(chain)`, `catalogue_hubs()` | K6 exempt radius per joint (hub radius + 2, capped at 12 mm); the catalogue hubs a slim hub may be declared as (`Chain.info['hub_rad']`) |
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
  A hub smaller than O20 (`hub_member(rad=7.5)`) is honest only as a DECLARED catalogue component: put its radius in
  `Chain.info['hub_rad']` (`{joint: mm}`); when `tools/hardware_catalogue.json` holds a hub of that OD
  (`K.catalogue_hubs()`: today `MR117-pair-O15-slim`, O15, 12.25 mm stack) the audit checks the sampled disc against
  that disc (>= 75 % covered, reaching >= rad - 0.5, thickness >= the stack) and lists it in the report's
  `declared_hubs`; any other radius gets the O20 check. A slim hub also shrinks the K6 zone of its joint (below).
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
  part-part clearance, `over` builds 1 mm) -> the pose is not taken; joint partners exempt within `hub_zones(chain)`
  of the shared joint = its hub radius + 2 mm (width / 2 of the joint's `hub_member`, capped at HUB_R: 12 mm at an
  O20 hub, 9.5 mm at an O15 one, 12 mm at a joint without a hub member). A model that runs `collisions` on sub-chains
  without the hub member (pair by pair) passes `zone=K.hub_zones(full chain)`. To avoid collisions by construction,
  give the upper part `over=[(name, 1.0)]`: its underside is raised to the other's top + 1 mm wherever K6 would see
  them meet in any fit pose - the same `_near` test, zones and pair order as `collisions`, at the final radius (`over`
  and the K5 climb are iterated to a fixed point) - (the template's link 2 over link 1 and the neck: without it 34 % of
  the template's closing poses collide; link 2 then pays for it: 5 % in band). With an O20 hub, `strap_member`'s
  default `end_mm = HUB_R + 2` holds a strap end at its hub level over exactly the K6 zone; at a slim hub
  `end_mm = rad + 2` is equally honest (a longer ramp is checked, and lifted by `over`, beyond rad + 2).
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

`OMP_NUM_THREADS=1 python3 -m pytest -q tools/test_concept_kit.py` (26 tests, ~20 s on 4 idle cores; ~35-45 s
loaded): directions vs band_impl, frames vs Bench, closure vs a brute-force circle scan on random vectors (both
branches) and near-degenerate cases (b ~ w, tangent circles), K3 march vs a brute 1 mm march on real poses, `outer` vs
concept_baseline, `dist_many` vs `B.dist` (incl. points outside the grid box), collisions on constructed hit / miss /
exempt cases, `over`, K2 on a constructed flip (frames rule and dense rule), the baseline row reproduction, and the
constructed cases of Verification 2: `over` at the final radius (bug 4), the K6 zone per hub radius (bug 5, incl. the
`zone=` override for sub-chains), `over` in K6's pair order (bug 6), the declared slim hub audit.

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
(< 75 % of the disc within 10.5 mm or reaching < 9.5 mm) -> flagged (it flags the baseline's own hub 1, a quirk),
unless it is a declared catalogue slim hub that covers its own disc (Verification 2);
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

## Verification 2: `over` vs K6 near a shared joint, slim hubs (2026-10-16)

Found on `docs/concepts/models/spine-parked-j2-3r.py` (spherical 3R at the k4216 seats: az 95.8565, el 65.2093,
a1 40.3436, a2 74.0692, wd 84.7998, wa -11.3702, sigma -1, q 0.98), Bench(60, 160), fast grid cache, march, dense K2,
K6. Three bugs made `over` (K6 clearance by construction) and `collisions` (K6) disagree, so a member built to pass
over another was still rejected, and the O20 exemption around a slim hub hid an unchecked band. Each has a constructed
test; each test fails when its own fix is reverted and passes otherwise (mutation check).

4. **`over` judged the shared-joint exemption at the pre-raise radius.** `_near` exempts samples within the zone (mm
   of arc = angle x radius) of a shared joint axis. `_over` called it with the underside BEFORE the K5 climb
   (`xa_all = broadcast(r)`), `collisions` with the final one. A link-2 sample 12.8 mm from J2 at its final 63.2 mm is
   ~10 mm from J2 at its pre-raise ~50 mm: `_over` skipped it as exempt, the climb lifted it partly, K6 found link 1 /
   link 2 overlapping (20 of 170 closing poses). Now `fit_profiles` iterates `_over` and the climb to a fixed point
   (both only raise; 2-4 passes; a warning after 20), so `_over` last tested every sample at its final radius.
   `test_over_decides_the_k6_zone_at_the_final_radius` (that 12.8 / 10.1 mm sample, constructed).
5. **The K6 zone ignored the hub's size.** `_near` exempted HUB_R + 2 = 12 mm at every joint and `strap_member`'s
   `end_mm` defaults to the same. A model with a slim hub (`hub_member(rad=7.5)`) and ramps shortened to rad + 2 left
   link 1 / link 2 unchecked between 9.5 and 12 mm from the joint: optimistic. Now `hub_zones(chain)` gives each joint
   min(hub radius, HUB_R) + 2, the hub radius being width / 2 of the joint's `hub_member` (`Member.hub`); a joint
   without one (hubless, rings, hand-built cap hubs) keeps 12 mm. A hub larger than O20 keeps 12 mm too: a zone grown
   with the hub would open the same unchecked band the other way round, since the ramps hold the partners at their
   stack levels only 12 mm by default. `collisions(..., zone=)` serves models that test sub-chains without the hub
   member. `test_k6_zone_follows_the_hub_radius`.
6. **`over` asked in the other pair order.** `_near` is not symmetric (arc at the first member's radius, the second
   member's LARGEST sample half extent). `collisions` tests pairs in `Chain.members` order, `_over` tested (upper,
   lower). With O15 hubs, 5 poses stayed rejected after fixes 4 and 5: link 1 (listed first, 55.6 mm) and link 2
   (59.0 mm; its far end at 84 mm makes its largest half extent 1.2 mm) are 3.1 mm apart at link 1's radius (near:
   < 3.2) but 3.3 mm at link 2's (not near: > 3.0), 0.4 mm radial gap. `_over` now runs `_near` on the points K6 sees
   (`member_points`) in K6's order. `test_over_tests_the_pair_in_the_k6_order`.

Each fix on and off (gap, K6-rejected poses of 170 closing; spine-parked at the seats above):

| case | old kit | 5 only | 4 only | 4 + 6 | 4 + 5 + 6 (now) |
|---|---|---|---|---|---|
| O20 hubs, 12 mm ramps | 54.35 (20) | 54.35 (20) | 37.53 (0) | 37.53 (0) | **37.53** (0) |
| O20 hubs, 14 mm ramps (`end_extra 2`) | 38.73 (0) | 38.73 (0) | 38.73 (0) | 38.73 (0) | **38.73** (0) |
| O15 hubs at J2 / J3, 12 mm ramps | 44.49 (15) | 38.25 (5) | 36.95 (5) | 32.01 (0) | **33.38** (0) |
| O15 hubs, ramps rad + 2 (link 1 12 mm, link 2 9.5 mm) | 35.11 (7) | 38.18 (5) | 36.35 (5) | 31.40 (0) | **33.31** (0) |

The O20 zone around an O15 hub was worth ~2 points of optimism (31.40 vs 33.31); with all three fixes the ramp length
no longer matters (33.38 vs 33.31). Independent check: a float64 brute-force K6 (own loops, exact arccos, own reading
of the zones) agrees with the kit pose for pose on these four cases, the sweep's best entry and the template at q 0.95 /
1.0 (0 hits each), and on virtual-pole-4bar-j2 k472 / -j1 k700 (41 / 22 hits).

**Declared slim hubs.** `tools/hardware_catalogue.json` rotary_bearings `MR117-pair-O15-slim`: 2 x MR117-2RS in a
2.0 mm Ti wall, OD 15, 12.25 mm stack, internal DIN 472 retention (hand calc: docs/concepts/spine-parked-j2-3r.md).
`audit` reads `Chain.info['hub_rad']`. A declared radius < 10 with a catalogue hub of that OD (`catalogue_hubs()`) is
checked against that disc (>= 75 % covered within rad + 0.5, reaching >= rad - 0.5, thickness >= its stack) and listed
in the report's `declared_hubs`. An undeclared slim hub, or a radius with no catalogue entry (O17), still gets "smaller
than O20"; a declared O15 built smaller gets "smaller than its declared MR117-pair-O15-slim". `test_audit_declared_slim_hub`.

**Committed sweep numbers that move (a measurement change, not a design change).** Every kit model with a sweep file:
its best 3 entries by gap and its first entry (spine-parked-j2-3r: all 245), re-evaluated through
`tools/concept_sweep.py`'s hooks on Bench(60, 160) fast, kit before (85c53e7) and after, ONE FRESH PROCESS PER MODEL
(several models monkeypatch the kit at import - `K.collisions`, `K.fit_profiles`, `K._levels`, `K.HUB_R` - so a shared
process leaks the patches into the next model).

| model | entry k | committed | before (HEAD) | after |
|---|---|---|---|---|
| spine-parked-j2-3r | 32 (best) / 196 / 110 / 0 | 31.90 / 33.86 / 32.53 / 54.35 | same | 32.35 / 32.88 / 32.98 / 37.53 |
| floating-centre-3r | 28 / 31 / 32 | 58.17 / 59.73 / 62.93 | 61.76 / 87.27 / 58.48 (stale) | 51.69 / 51.98 / 58.04 |
| seed-2r-cring | 8 (best) / 19 / 23 | 129.98 / 134.81 / 139.60 | same | 126.23 / 138.58 / 127.59 |
| fivebar-roll | 13 (best) / 6 / 7 / 0 | 89.13 / 90.30 / 94.80 / 95.89 | same | 88.46 / 89.61 / 94.41 / 95.86 |
| back-anchored-ring-3r | 12 (best) / 14 / 13 | 82.26 / 83.80 / 85.78 | same | 82.72 / 84.26 / 86.22 |
| clavicular-front-route | 414 (best) / 303 / 0 | 65.53 / 67.19 / 218.34 | 65.53 / 67.19 / 230.75 | 65.52 / 66.10 / 226.10 |
| j2-arc-sector-3r | 1 / 0 (best 78.47 unchanged) | 82.81 / 93.88 | same | 81.79 / 92.96 |
| pointer-cslide | 375 (best) / 469 / 366 | 69.84 / 70.23 / 71.48 | same | 69.78 / 70.22 / 71.47 |
| virtual-pole-4bar-j2 | 472 (best 104.57 unchanged) | 122.09 | same | 124.16 |
| virtual-pole-4bar-j1 | 700 (best 152.69 unchanged) | 182.68 | same | 178.48 |
| meridian-goniometer | 63 (best 86.81 unchanged) | 89.79 | same | 89.64 |
| seed-pauldron-shells | 0 (best 70.26 unchanged) | 90.07 | same | 88.37 |
| scapular-race-j2-carriage | 0 (best unchanged) | 158.84 | 155.40 (stale) | 159.69 |
| risley-turret | 42 | 63.17 | 68.17 (stale) | 67.98 |
| rail-elbow | 0 (best 56.25 unchanged) | 100.46 | 101.32 (stale) | 98.25 |

spine-parked-j2-3r, all 245 entries (all reproduce at HEAD): 238 move (180 down, 58 up, median -0.36, -26.85 to
+1.25); entries with K6 rejections 122 -> 5 (the 5 left are hub 1 / neck and link 1 / neck, pairs no `over` covers);
best still k32, 31.90 -> 32.35; best O20 entry k227 37.37 unchanged; the 12 mm-ramp O15 entries (k2, k5) 44.49 ->
33.38. fivebar-roll k13 also turns honest (its coupler 2 spacing 4.03 mm -> under the 4 mm audit limit).
Gap unchanged, only the Ti mass moves (-0.1 to -3 %): annular-ring-3r, crown-ring-3r, fold-sph3r, twin-rail-one-hub,
the best entries of j2-arc-sector-3r and meridian-goniometer, `_template` (69.29 / 65.05; Ti 125.1 -> 124.9 g,
176.7 -> 175.4 g). Unchanged: baseline-3r-kit (68.93 / 70.27),
raglan-routed-3r, trombone-arc, posterior-max-margin-cardan (its own over + climb loop), fraction-pauldron (its own
profiles; its committed 92.32 reads 189.73 at HEAD before and after). "Stale" = the committed number did not reproduce
at HEAD on the unchanged kit either (model or kit changed after the sweep: also annular-ring-3r k51 / k52,
posterior-max-margin-cardan, the k0 rows of trombone-arc, seed-2r-cring, pointer-cslide); re-sweep those separately.

Gap is not monotone in this fix: a pose K6 no longer rejects is taken, and costs 100 x contact if metal is in the skin
there (seed-2r-cring k19, back-anchored-ring-3r, scapular race k0); `over` now raises only where K6 looks, so some
members sit lower (mass down) and nearer the skin; a member raised to clear its `over` targets can meet a member not in
its list (virtual-pole-4bar-j2 k472: link 1 / coupler 36 -> 39 poses).

Holes that remain: a hub larger than O20 keeps the 12 mm zone (pessimistic: its partners are checked over the outer
part of its disc); a `flat` member with `over` (a plate's per-sample raise is not represented: `member_points` uses one
level); a model that calls `collisions` on sub-chains without the hub member must pass `zone=` (no committed model has
a slim hub on that path today).

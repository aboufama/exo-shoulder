# Concept gallery: kinematic previews (docs/concepts/viz)

One page that shows every morphology of docs/dashboard/data/morphs.json (minus duplicates) as a schematic, animated 3D
preview on a primitive mannequin running a motion loop. Schematic, not CAD: the point is honest topology (how many
active and passive DOF, which axes pass through GH, what is fixed to the scapula and what to the arm).

    node docs/concepts/viz/test.mjs [id ...]            # harness: closure, continuity, NaN, sanity per concept (exit 1 = broken)
    python3 docs/concepts/viz/build.py [--only a,b]      # meta.js + index.html script block + dist/index.html (the Artifact)
    PW_MODULE=<scratch>/node_modules/playwright-core node docs/concepts/viz/shots.mjs --out <dir> [id ...]
                                                          # stage shots at 2 poses per concept + contact sheet + console errors
    node docs/concepts/viz/thumbs.mjs [--stats] [--sheet f.svg] [--out f.json] [--n 56] [id ...]
                                                          # tiny monochrome motion previews -> docs/dashboard/data/motion.json
                                                          # (the dashboard leaderboard; tools/dash_build.py re-runs it when stale;
                                                          # parts named "construction line" / "not metal" / "trace" are not drawn)
    open docs/concepts/viz/index.html via any static server (dev page, loads the files one by one)

Files: `kin.js` (maths, motion loop, IK, registry), `concepts/<id>.js` (one per morphology, file name = id),
`viewer.js` (three.js r128 page), `index.html` (page template + dev page), `meta.js` (generated), `dist/index.html`
(generated, self-contained), `test.mjs`, `shots.mjs`. Reference concepts: `baseline-3r.js` (closed form, spherical 3R),
`rail-elbow.js` (closed form, rail + carriage), `seed-offset-3r-slides.js` (numeric IK, offset axes + 3 passive slides).

## Concept API

Write `docs/concepts/viz/concepts/<id>.js` (id = the morphs.json / catalogue.json id). Plain JS, no modules, no THREE:

```js
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { /* the concept's best parameters (sweeps/<id>.json lowest gap, or the doc / catalogue spec) */ };
  K.register({
    id: '<id>', name: 'Short display name',
    dof: { active: 3, passive: 1 },                 // must match the concept's own DOF count
    params: P,
    q0: [ ... ] or (ctx) => [ ... ],                // unknowns at the loop's first frame (rest pose)
    qNames: [...], qUnits: ['deg', ..., 'mm'],      // revolute q in DEGREES, prismatic in mm
    resUnits: ['deg', 'deg', 'deg', 'mm', ...],     // unit of each residual entry ('mm' default)
    residual: (q, ctx) => [ ... ],                  // closure error of the loop scapula -> chain -> arm; ~0 when closed
    solve: (ctx, qPrev) => q,                       // OPTIONAL closed form; without it the numeric IK solves residual
    check: (q, ctx) => null | 'reason',             // OPTIONAL working-range test (fold margin, rail end, slide range)
    parts: (q, ctx) => [ descriptor, ... ]          // SAME length and kinds every frame (meshes are reused by index)
  });
})();
```

Solving, per frame of the loop: `solve` when given (the residual is still evaluated and reported), else damped least
squares (Levenberg-Marquardt, central-difference Jacobian, step <= 8 deg|mm per iteration) warm-started from the
previous frame's q (frame 0 from q0; if that fails it retries from q0). The loop CLOSES when every |mm| residual entry
<= 0.5 and every |deg| entry <= 0.5; `check` returning a reason marks the frame "outside its working range". A frame the
concept cannot reach is drawn as solved (not hidden) and the indicator turns red.

Frame (same as the bench, pipeline/avg/body_pose.py): rig mm, x anterior, y up, z right (lateral; right shoulder), GH
centre at the origin. Every descriptor is in this WORLD frame. Matrices are row-major 3x3 arrays, vectors [x, y, z].

`ctx` (one per frame, built by `KIN.makeCtx(pose, t)`):

| field | meaning |
|---|---|
| `ctx.H` | humerus rotation Ry(plane) Rx(-elev) Ry(axial) = the BAND humerus frame (band_impl w_dir, concept_kit F.HG). A humerus-fixed direction u is `M.mulv(ctx.H, u)`. At rest the arm hangs along -y. |
| `ctx.S` | scapula rotation scap(elev) = Rz(0.12 elev) R(n, -0.36 max(0, elev - 20)), n = (cos30, 0, -sin30): a scapula-fixed base turns with it (about GH). The relative arm rotation is `M.mul(M.T(ctx.S), ctx.H)` (band HG). |
| `ctx.Hb` | body_pose humerus frame (= H rest_humerus^T; concept_kit F.H, for BOTTOM's bar data) |
| `ctx.armAxis` | unit GH -> elbow direction (= H [0, -1, 0]) |
| `ctx.elbow`, `ctx.wrist`, `ctx.elbowAxis` | elbow centre, wrist (ulnar head), elbow flexion axis (mm, world) |
| `ctx.lift` | the trunk (torso, head) moves by -lift (shrug); GH, scapula and arm do not |
| `ctx.pose`, `ctx.t` | {plane, elev, axial, flex, pron} (deg), loop time 0..1 |
| `ctx.attach.armDir(u)`, `.armPt(p)` | humerus-fixed direction / point -> world |
| `ctx.attach.scapDir(u)`, `.scapPt(p)` | scapula-fixed direction / point -> world |
| `ctx.attach.onArm(s, radial, dirArm)` | point on the humerus axis s mm from GH, + radial mm toward the arm-frame direction dirArm (default lateral [0,0,1]) |
| `ctx.attach.cuff(s)` | {o: point on the arm axis at s mm, R: H} |
| `ctx.attach.foreArmPt(p)` | forearm-fixed point (body_mesh rest-arm coordinates) -> world |

Descriptors (plain data; all points / directions in world mm; directions need not be unit). Every descriptor has
`kind`, `role` and an optional `name`:

| kind | fields | drawn as |
|---|---|---|
| `hub` | `c` (centre of the skin-side face), `axis` (outward), `r` (10), `h` (stack, 12.25), `p0` (a point on the axis line; default GH) | cylinder c -> c + h axis, plus a faint axis line from p0 (toggle "Joint axes") |
| `link` | `a`, `b`, `r` (2.5) | straight rod |
| `arc` | `pts` [[x,y,z], ...] OR `u`, `v` (unit dirs from GH, or from `c`), `r0`, `r1` (radius at each end), `c` (default GH); `r` (2.5) | tube along the polyline / the great circle u -> v with the radius going r0 -> r1 |
| `rail` | `c` (circle centre), `axis` (circle normal), `ref` (azimuth 0), `rho` (circle radius), `a0`, `a1` (deg, about axis from ref toward axis x ref), `r` (2.6) | tube on that circular arc |
| `carriage` | `c`, `x` (travel direction), `z` (outward normal), `size` [l, w, t] | box |
| `slider` | `a`, `b` (guide ends), `at` (block centre), `z` (block normal), `size` [l, w, t] (12, 10, 5), `r` (guide 1.6) | rod + block |
| `telescope` | `a`, `b`, `split` (outer tube length from a, mm), `r0` (5), `r1` (3.2) | outer tube a -> a + split, inner rod from a + split/2 to b |
| `strap` | `c`, `axis`, `r`, `w` (width, 20), optional `ref`, `a0`, `a1` (deg, fixed for the concept) for a partial band | thin open band around axis |
| `ring` | `c`, `axis`, `r` (ring radius), `t` (section radius, fixed), optional `ref` | torus |
| `plate` | `c`, `z` (normal), `x` (in-plane direction), `size` [sx, sy], `t` (3) | flat box |
| `point` | `p`, `r` (4) | sphere (a marker; `name: 'GH centre'` draws the GH marker) |

Roles and colours: `active` (active joints: accent blue), `passive` (passive joints, slides, sleeves: iglidur orange),
`link` (rigid links: bead-blasted metal), `fixed-scapula` (the base on the user's scapula handler: steel blue-grey),
`fixed-arm` (cuff, neck, anything rigid with the humerus: warm light metal).

Helpers on `KIN` (degrees unless the name says rad):

* `V`: add, sub, scale, dot, cross, norm, unit, lerp, madd(a, b, s) = a + s b, angle(a, b), perp(a), reject(v, k)
* `M`: I3, mul, mulv, T, col, fromCols, rot(axis, deg), rotRad, logRot(R) (rad vector), rotErrDeg(A, B) (rotation
  vector in deg taking B to A: the standard orientation residual)
* `bvec(az, el)` (band base axis), `wdir(d, a)` (band humerus axis), `circInt(c1, r1, c2, r2, sign)` -> {p, ok, h2}
  (two-circle closure), `foldMargin(x, y, a1, a2)`, `axisAngle(k, ref, v)`, `onCone(k, ref, pol, az)`,
  `greatArc(u, v, r0, r1, n)` (points), `wrap180`
* `sph3r(b, w, a1, a2, branch)` -> {u1, u2, u3, fk(q, ctx) -> {p1, p2, p3 (world axes), R}, solve(ctx) -> q,
  residual(q, ctx) -> 3 deg, margin(ctx)}: the band's spherical 3R (base axis b in the scapula frame, last axis w in
  the humerus frame, J2 from the two-circle closure on `branch`); q measured from the home configuration H = S.
* `humerus(pose)`, `scap(elev)`, `lift(pose)`, `armFrames(pose)`, `makeCtx(pose, t)`, `motion(n)` (the loop: rest ->
  forward raise -> overhead -> lateral abduction -> across the body -> (lowering) -> hand behind the back -> rest,
  smootherstep between keys, ~240 frames), `KEYS`, `run(concept, frames)`, `solveFrame`, `dls`, `BODY` (landmarks)

Rules of thumb: hubs on the real joint axes at the concept's face distances (a revolute joint with no metal on its
axis, like a rail, gets no hub); one descriptor per physical member; passive slides / sleeves / self-aligning joints as
`passive` sliders, straps or rings; the base plate as `fixed-scapula`; the arm cuff as a `fixed-arm` strap (~47 mm
radius at 150-170 mm down the arm); a `point` at GH helps the eye read "axes through GH". Run `node test.mjs <id>`
until it prints OK with no NaN, then `python3 build.py`.

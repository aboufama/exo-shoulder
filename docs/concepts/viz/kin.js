/* kin.js - kinematics core of the concept gallery (docs/concepts/viz). Plain browser JS, no modules: attaches
 * window.KIN (and module.exports in node, for test.mjs). No THREE here.
 *
 * Frame (same as the bench, pipeline/avg/body_pose.py): rig mm, x anterior, y up, z right (lateral, right shoulder),
 * GH centre at the origin. Matrices are row-major 3x3 arrays [[r0],[r1],[r2]]; vectors [x, y, z]; angles in the
 * public helpers are DEGREES unless the name says rad.
 *
 *   H = KIN.humerus(pose)   = Ry(plane) Rx(-elev) Ry(axial)  (band humerus frame: band_impl w_dir / CHAMP W live here)
 *   S = KIN.scap(elev)      = Rz(0.12 elev) R(n, -0.36 max(0, elev - 20)), n = (cos30, 0, -sin30)
 *   the trunk (torso, head, left arm) moves by -lift, lift = (0, 0.2 max(0, elev - 30) scale, 0); the scapula and the
 *   arm turn about GH.
 */
(function (root) {
  'use strict';
  const D2R = Math.PI / 180, R2D = 180 / Math.PI;

  // ---------------------------------------------------------------- vectors
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const scale = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = a => Math.sqrt(dot(a, a));
  const unit = a => { const n = norm(a) || 1e-12; return [a[0] / n, a[1] / n, a[2] / n]; };
  const lerp = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
  const madd = (a, b, s) => [a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s];       // a + s b
  const angle = (a, b) => Math.acos(Math.max(-1, Math.min(1, dot(unit(a), unit(b))))) * R2D;   // deg
  const perp = a => unit(Math.abs(a[1]) < 0.9 ? cross(a, [0, 1, 0]) : cross(a, [1, 0, 0]));  // any unit normal to a
  // component of v normal to unit k
  const reject = (v, k) => sub(v, scale(k, dot(v, k)));
  const V = { add, sub, scale, dot, cross, norm, unit, lerp, madd, angle, perp, reject };

  // ---------------------------------------------------------------- matrices
  const I3 = () => [[1, 0, 0], [0, 1, 0], [0, 0, 1]];
  const mul = (A, B) => A.map(r => [0, 1, 2].map(j => r[0] * B[0][j] + r[1] * B[1][j] + r[2] * B[2][j]));
  const mulv = (A, v) => [dot(A[0], v), dot(A[1], v), dot(A[2], v)];
  const T = A => [[A[0][0], A[1][0], A[2][0]], [A[0][1], A[1][1], A[2][1]], [A[0][2], A[1][2], A[2][2]]];
  const col = (A, j) => [A[0][j], A[1][j], A[2][j]];
  const fromCols = (a, b, c) => [[a[0], b[0], c[0]], [a[1], b[1], c[1]], [a[2], b[2], c[2]]];
  function rotRad(axis, a) {                                   // Rodrigues, axis need not be unit
    const u = unit(axis), c = Math.cos(a), s = Math.sin(a), t = 1 - c, [x, y, z] = u;
    return [[c + x * x * t, x * y * t - z * s, x * z * t + y * s],
            [y * x * t + z * s, c + y * y * t, y * z * t - x * s],
            [z * x * t - y * s, z * y * t + x * s, c + z * z * t]];
  }
  const rot = (axis, deg) => rotRad(axis, deg * D2R);
  function logRot(R) {                                         // rotation vector (rad) of R
    const c = Math.max(-1, Math.min(1, (R[0][0] + R[1][1] + R[2][2] - 1) / 2)), a = Math.acos(c);
    const w = [R[2][1] - R[1][2], R[0][2] - R[2][0], R[1][0] - R[0][1]];
    if (a < 1e-7) return scale(w, 0.5);
    if (Math.PI - a < 1e-4) {                                  // near pi: axis from the diagonal
      const d = [R[0][0], R[1][1], R[2][2]], i = d.indexOf(Math.max(...d));
      const ax = [0, 0, 0]; ax[i] = Math.sqrt(Math.max(0, (d[i] + 1) / 2));
      for (let j = 0; j < 3; j++) if (j !== i) ax[j] = (R[i][j] + R[j][i]) / (4 * ax[i] || 1e-12);
      return scale(unit(ax), a);
    }
    return scale(w, a / (2 * Math.sin(a)));
  }
  const rotErrDeg = (A, B) => scale(logRot(mul(T(B), A)), R2D);   // rotation vector (deg) taking B to A, in B's frame
  const M = { I3, mul, mulv, T, col, fromCols, rot, rotRad, logRot, rotErrDeg };

  // ---------------------------------------------------------------- body (pipeline/avg/body_mesh.json landmarks)
  const BODY = {
    scale: 1.0556638846119553,
    rest_humerus: [[0.9912306950561375, 0.022730583508942376, -0.1301730761404597],
                   [-0.0008302154507958161, 0.9861460730488582, 0.1658771634451883],
                   [0.13214015256852168, -0.16431446431662505, 0.9775171286967346]],
    elbow: [-7.3874396404062725, -320.4974737408789, 53.40220090290314],
    elbow_axis: [-0.1314623781881947, 0.09514925749125984, 0.9867442738217264],
    radial_head: [-4.533470881044573, -334.3544848575334, 75.55866455391481],
    ulnar_head: [40.36879342130444, -563.6595124707354, 84.15608069640786],
    rest_flex: 12.529805317425245,
    // trunk outline from the rest render skin (trunk vertices, y slices): midline z, chest / back x, head
    mid_z: -175, gh_left_z: -350
  };

  const humerus = p => mul(mul(rot([0, 1, 0], p.plane), rot([1, 0, 0], -p.elev)), rot([0, 1, 0], p.axial));
  function scap(elev) {
    const n = [Math.cos(30 * D2R), 0, -Math.sin(30 * D2R)];
    return mul(rot([0, 0, 1], 0.12 * elev), rot(n, -0.36 * Math.max(0, elev - 20)));
  }
  const lift = p => [0, 0.2 * Math.max(0, p.elev - 30) * BODY.scale, 0];

  /** arm segment points of a pose: body_pose humerus Hb = H rest^T, elbow E, forearm rotation F about E, wrist W */
  function armFrames(p) {
    const H = humerus(p), Hb = mul(H, T(BODY.rest_humerus));
    const E = mulv(Hb, BODY.elbow), ax = mulv(Hb, BODY.elbow_axis);
    const Rf = rot(ax, (p.flex == null ? 15 : p.flex) - BODY.rest_flex), F = mul(Rf, Hb);
    const toF = x => add(mulv(Rf, sub(mulv(Hb, x), E)), E);
    const W = toF(BODY.ulnar_head), Wr = toF(BODY.radial_head);
    return { H, Hb, F, Rf, toF, elbow: E, elbowAxis: ax, wrist: W, radialHead: Wr };
  }

  // ---------------------------------------------------------------- shared design helpers (band_impl / concept_kit)
  /** band_impl.bvec: base axis in the scapula frame (deg) */
  const bvec = (az, el) => [-Math.cos(el * D2R) * Math.cos(az * D2R), Math.sin(el * D2R), Math.cos(el * D2R) * Math.sin(az * D2R)];
  /** band_impl.w_dir / concept_kit.wdir: humerus-frame direction, d from the down-the-arm axis, a 0 lateral +90 anterior */
  const wdir = (d, a) => [Math.sin(d * D2R) * Math.sin(a * D2R), -Math.cos(d * D2R), Math.sin(d * D2R) * Math.cos(a * D2R)];
  /** two-circle closure (band_impl.circ_int): unit p with angle(p, c1) = r1, angle(p, c2) = r2 (deg) on branch sign;
   *  ok false when the circles miss (p is then the closest point, h clamped to 0) */
  function circInt(c1, r1, c2, r2, sign) {
    c1 = unit(c1); c2 = unit(c2);
    const dd = Math.max(-1, Math.min(1, dot(c1, c2))), n = unit(cross(c1, c2)), den = 1 - dd * dd + 1e-12;
    const a = (Math.cos(r1 * D2R) - dd * Math.cos(r2 * D2R)) / den, b = (Math.cos(r2 * D2R) - dd * Math.cos(r1 * D2R)) / den;
    const p = add(scale(c1, a), scale(c2, b)), h2 = 1 - dot(p, p);
    return { p: unit(madd(p, n, sign * Math.sqrt(Math.max(0, h2)))), ok: h2 > 0, h2 };
  }
  /** fold / stretch margin (deg) of a spherical 2-link triangle with arcs a1, a2 between axes x, y (band tri_ok) */
  function foldMargin(x, y, a1, a2) {
    const th = angle(x, y); return Math.min(th - Math.abs(a1 - a2), Math.min(a1 + a2, 360 - a1 - a2) - th);
  }
  /** signed angle (deg) about unit axis k from ref to v (both projected normal to k) = concept_kit.axis_angle */
  function axisAngle(k, ref, v) {
    const r = reject(ref, k), w = reject(v, k);
    return Math.atan2(dot(cross(r, w), k), dot(r, w)) * R2D;
  }
  /** point at polar angle pol and azimuth az (deg) on the cone about unit k, azimuth 0 = ref (normal to k) */
  function onCone(k, ref, pol, az) {
    const e = unit(reject(ref, k)), f = cross(k, e), p = pol * D2R, a = az * D2R;
    return unit(add(scale(k, Math.cos(p)), scale(add(scale(e, Math.cos(a)), scale(f, Math.sin(a))), Math.sin(p))));
  }
  /** points along the great circle u -> v (unit dirs), radius r0 -> r1 (mm), n samples */
  function greatArc(u, v, r0, r1, n) {
    u = unit(u); v = unit(v); const th = angle(u, v) * D2R, nn = n || Math.max(4, Math.ceil(th * 18));
    const e = th < 1e-6 ? perp(u) : unit(reject(v, u)), out = [];
    for (let i = 0; i <= nn; i++) {
      const s = i / nn, d = add(scale(u, Math.cos(s * th)), scale(e, Math.sin(s * th)));
      out.push(scale(d, r0 + (r1 - r0) * s));
    }
    return out;
  }
  const wrap180 = a => ((a + 180) % 360 + 360) % 360 - 180;

  /** spherical 3R helper (band_impl.Band.chain, N = 3, no cuff): base axis b fixed in the scapula frame, last axis w
   *  fixed in the humerus frame, link arcs a1, a2 (deg), J2 from the two-circle closure on `branch`. Joint values q
   *  (deg) are measured from the home configuration (the arm at H = S, where p1 = b, p3 = w, p2 = circInt(b, a1, w, a2)).
   *  Returns { u1, u2, u3, fk(q, ctx) -> {p1, p2, p3 (world unit axes), R (chain end rotation, world)},
   *            solve(ctx) -> q (closed form), residual(q, ctx) -> 3 deg (chain end vs humerus), margin(ctx) -> deg } */
  function sph3r(b, w, a1, a2, branch) {
    const u1 = unit(b), u3 = unit(w), u2 = circInt(u1, a1, u3, a2, branch).p;
    const v3 = perp(u3);
    function fk(q, ctx) {
      const R1 = rot(u1, q[0]), R12 = mul(R1, rot(u2, q[1])), E = mul(R12, rot(u3, q[2]));
      return { p1: mulv(ctx.S, u1), p2: mulv(ctx.S, mulv(R1, u2)), p3: mulv(ctx.S, mulv(R12, u3)), R: mul(ctx.S, E), R1, R12, E };
    }
    function solve(ctx) {
      const Q = mul(T(ctx.S), ctx.H), p3 = mulv(Q, u3), c = circInt(u1, a1, p3, a2, branch), p2 = c.p;
      const q1 = axisAngle(u1, u2, p2), R1 = rot(u1, q1);
      const q2 = axisAngle(u2, u3, mulv(T(R1), p3)), R12 = mul(R1, rot(u2, q2));
      const R3 = mul(T(R12), Q), q3 = axisAngle(u3, v3, mulv(R3, v3));
      return [q1, q2, q3];
    }
    const residual = (q, ctx) => rotErrDeg(fk(q, ctx).R, ctx.H);
    const margin = ctx => foldMargin(mulv(ctx.S, u1), mulv(ctx.H, u3), a1, a2);
    return { u1, u2, u3, fk, solve, residual, margin, a1, a2, branch };
  }

  // ---------------------------------------------------------------- motion loop
  // key poses (deg): plane (0 = abduction, 90 = flexion, 30 = scapular plane), elev, axial (+ internal), flex (elbow)
  const KEYS = [
    { key: 'rest', label: 'Rest', pose: { plane: 20, elev: 6, axial: -15, flex: 18 } },
    { key: 'reach', label: 'Forward raise', pose: { plane: 88, elev: 92, axial: -12, flex: 15 } },
    { key: 'overhead', label: 'Overhead', pose: { plane: 40, elev: 152, axial: -48, flex: 25 } },
    { key: 'abduct', label: 'Lateral abduction', pose: { plane: 0, elev: 90, axial: -5, flex: 15 } },
    { key: 'across', label: 'Across the body', pose: { plane: 128, elev: 88, axial: -18, flex: 70 } },
    { key: 'lower', label: '(transition)', pose: { plane: 30, elev: 22, axial: 20, flex: 60 }, via: true },
    { key: 'behind', label: 'Hand behind the back', pose: { plane: -65, elev: 42, axial: 105, flex: 95 } },
    { key: 'rest2', label: 'Rest', pose: { plane: 20, elev: 6, axial: -15, flex: 18 }, via: true }
  ];
  const smooth = s => s * s * s * (s * (6 * s - 15) + 10);      // smootherstep: zero speed and acceleration at the keys
  /** the loop: ~n frames, each {i, t (0..1), pose, key (label at a key frame, else null), seg} */
  function motion(n) {
    n = n || 240; const segs = KEYS.length - 1, hold = 6;
    // frames per segment proportional to its angular size (min 14)
    const size = []; for (let k = 0; k < segs; k++) {
      const a = KEYS[k].pose, b = KEYS[k + 1].pose;
      size.push(Math.max(30, Math.abs(b.elev - a.elev) + 0.6 * Math.abs(b.plane - a.plane) * Math.sin(Math.max(a.elev, b.elev) * D2R) + 0.4 * Math.abs(b.axial - a.axial)));
    }
    const tot = size.reduce((x, y) => x + y, 0), budget = n - hold * segs, frames = [];
    for (let k = 0; k < segs; k++) {
      const a = KEYS[k].pose, b = KEYS[k + 1].pose, m = Math.max(14, Math.round(budget * size[k] / tot));
      for (let h = 0; h < hold; h++) frames.push({ pose: Object.assign({}, a), key: KEYS[k].via ? null : KEYS[k].key, seg: k });
      for (let j = 1; j <= m; j++) {
        const s = smooth(j / (m + 1)), p = {};
        for (const f of ['plane', 'elev', 'axial', 'flex']) p[f] = a[f] + (b[f] - a[f]) * s;
        frames.push({ pose: p, key: null, seg: k });
      }
    }
    frames.forEach((f, i) => { f.i = i; f.t = i / frames.length; f.pose.pron = 0; });
    return frames;
  }

  // ---------------------------------------------------------------- context of a frame
  /** ctx handed to a concept: H, S (rotations), pose, t, lift, arm points and attach helpers */
  function makeCtx(pose, t) {
    const A = armFrames(pose), S = scap(pose.elev);
    const ctx = {
      pose, t: t || 0, H: A.H, S, Hb: A.Hb, F: A.F, lift: lift(pose),
      elbow: A.elbow, wrist: A.wrist, elbowAxis: A.elbowAxis,
      armAxis: mulv(A.H, [0, -1, 0]),                          // GH -> elbow direction (band humerus axis)
      attach: {
        /** humerus-fixed direction / point: H u, H p (mm) */
        armDir: u => mulv(A.H, u), armPt: p => mulv(A.H, p),
        /** scapula-fixed direction / point: S u, S p (the base rides the scapula) */
        scapDir: u => mulv(S, u), scapPt: p => mulv(S, p),
        /** forearm-fixed point (rest-arm coordinates, as body_pose): F (x) about the elbow */
        foreArmPt: p => A.toF(p),
        /** point on the humerus axis at distance s (mm) from GH, plus an optional radial offset: dir in arm frame */
        onArm: (s, radial, dirArm) => {
          const ax = mulv(A.H, [0, -1, 0]); let p = scale(ax, s);
          if (radial) p = madd(p, unit(reject(mulv(A.H, dirArm || [0, 0, 1]), ax)), radial);
          return p;
        },
        /** cuff frame on the upper arm at distance s from GH: origin on the axis, columns (lateral, axis, anterior) */
        cuff: s => ({ o: scale(mulv(A.H, [0, -1, 0]), s || 150), R: A.H })
      }
    };
    return ctx;
  }

  // ---------------------------------------------------------------- linear algebra for the solver
  function solveLin(A, b) {                                  // Gaussian elimination with partial pivoting, A n x n
    const n = b.length, M2 = A.map((r, i) => r.concat([b[i]]));
    for (let c = 0; c < n; c++) {
      let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M2[r][c]) > Math.abs(M2[p][c])) p = r;
      [M2[c], M2[p]] = [M2[p], M2[c]]; const d = M2[c][c] || 1e-12;
      for (let r = c + 1; r < n; r++) { const f = M2[r][c] / d; if (f) for (let k = c; k <= n; k++) M2[r][k] -= f * M2[c][k]; }
    }
    const x = new Array(n).fill(0);
    for (let r = n - 1; r >= 0; r--) { let s = M2[r][n]; for (let k = r + 1; k < n; k++) s -= M2[r][k] * x[k]; x[r] = s / (M2[r][r] || 1e-12); }
    return x;
  }
  const sq = r => r.reduce((s, x) => s + x * x, 0);

  /** damped least squares (Levenberg-Marquardt) on concept.residual from q0. Returns {q, r, err, iters} */
  function dls(concept, ctx, q0, opt) {
    opt = opt || {}; const it = opt.iters || 60, tol = opt.tol || 1e-6, h = 1e-6;
    let q = q0.slice(), r = concept.residual(q, ctx), e = sq(r), lam = opt.lambda || 1e-3, k = 0;
    const n = q.length, m = r.length;
    if (!n || !m) return { q, r, err: Math.sqrt(e), iters: 0 };
    for (; k < it && e > tol; k++) {
      const J = []; for (let i = 0; i < m; i++) J.push(new Array(n).fill(0));
      for (let j = 0; j < n; j++) {                            // central differences
        const qa = q.slice(), qb = q.slice(); qa[j] += h; qb[j] -= h;
        const ra = concept.residual(qa, ctx), rb = concept.residual(qb, ctx);
        for (let i = 0; i < m; i++) J[i][j] = (ra[i] - rb[i]) / (2 * h);
      }
      // (J^T J + lam diag) dq = -J^T r  (n x n)
      const JtJ = [], Jtr = new Array(n).fill(0);
      for (let a = 0; a < n; a++) { JtJ.push(new Array(n).fill(0)); for (let b = 0; b < n; b++) { let s = 0; for (let i = 0; i < m; i++) s += J[i][a] * J[i][b]; JtJ[a][b] = s; } for (let i = 0; i < m; i++) Jtr[a] += J[i][a] * r[i]; }
      let improved = false;
      for (let tries = 0; tries < 8; tries++) {
        const A = JtJ.map((row, a) => row.map((x, b) => a === b ? x + lam * (x + 1e-9) + lam * 1e-6 : x));
        const dq = solveLin(A, Jtr.map(x => -x));
        const step = opt.maxStep || 8, big = Math.max(...dq.map(Math.abs));
        const sc = big > step ? step / big : 1;                // limit the step (deg / mm per iteration: keeps branches)
        const qn = q.map((x, j) => x + dq[j] * sc), rn = concept.residual(qn, ctx), en = sq(rn);
        if (isFinite(en) && en < e) { q = qn; r = rn; e = en; lam = Math.max(lam / 3, 1e-9); improved = true; break; }
        lam *= 6;
      }
      if (!improved) break;
    }
    return { q, r, err: Math.sqrt(e), iters: k };
  }

  // ---------------------------------------------------------------- registry and per-frame solving
  const concepts = {}, order = [];
  /**
   * KIN.register({ id, name, dof: {active, passive}, params, q0, qNames?, qUnits?, resUnits?, residual(q, ctx),
   *                parts(q, ctx), solve?(ctx, qPrev), check?(q, ctx) })
   *  q0: array, or function(ctx) -> array (ctx of the first frame of the loop: the rest pose)
   *  residual(q, ctx) -> array; entries in mm or deg as resUnits says ('mm' default for every entry)
   *  parts(q, ctx) -> descriptor array, SAME length and kinds every frame (meshes are reused by index)
   *  solve(ctx, qPrev) -> q: optional closed form (the residual is still evaluated and reported)
   *  check(q, ctx) -> null | short reason: optional working-range test (rail end, slide range, fold margin)
   */
  function register(c) {
    if (!c || !c.id) throw new Error('KIN.register: concept needs an id');
    for (const f of ['residual', 'parts']) if (typeof c[f] !== 'function') throw new Error(`KIN.register(${c.id}): ${f}() missing`);
    if (!c.dof || c.dof.active == null || c.dof.passive == null) throw new Error(`KIN.register(${c.id}): dof {active, passive} missing`);
    if (!concepts[c.id]) order.push(c.id);
    concepts[c.id] = c; return c;
  }

  const CLOSE_MM = 0.5, CLOSE_DEG = 0.5;
  /** split a residual vector into max |mm| and max |deg| */
  function resSplit(c, r) {
    let mm = 0, deg = 0; const u = c.resUnits || [];
    r.forEach((x, i) => { const a = Math.abs(x); if ((u[i] || 'mm') === 'deg') deg = Math.max(deg, a); else mm = Math.max(mm, a); });
    return { mm, deg };
  }
  /** solve one frame from qPrev: closed form when given, else DLS warm-started (fallback: restart from q0) */
  function solveFrame(c, ctx, qPrev, q0) {
    let q, how;
    if (c.solve) { q = c.solve(ctx, qPrev); how = 'closed form'; }
    else {
      let s = dls(c, ctx, qPrev, { iters: 60 });
      if (s.err > 1e-3 && q0) {
        const s2 = dls(c, ctx, q0, { iters: 120 });
        if (s2.err < s.err * 0.5) s = s2;
      }
      q = s.q; how = 'numeric IK';
    }
    const r = c.residual(q, ctx), sp = resSplit(c, r), bad = q.some(x => !isFinite(x)) || r.some(x => !isFinite(x));
    const reason = c.check ? c.check(q, ctx) : null;
    const closes = !bad && sp.mm <= CLOSE_MM && sp.deg <= CLOSE_DEG;
    return { q, r, resMm: sp.mm, resDeg: sp.deg, closes, inRange: !reason, reason, how, nan: bad };
  }
  /** run a concept over frames (default: the motion loop). Returns per-frame solutions. */
  function run(c, frames) {
    frames = frames || motion(); const out = [];
    const ctx0 = makeCtx(frames[0].pose, 0);
    const q0 = typeof c.q0 === 'function' ? c.q0(ctx0) : (c.q0 || []).slice();
    let qPrev = q0;
    for (const f of frames) {
      const ctx = makeCtx(f.pose, f.t), s = solveFrame(c, ctx, qPrev, q0);
      s.ctx = ctx; out.push(s); if (!s.nan) qPrev = s.q;
    }
    return { q0, frames: out };
  }

  const KIN = { D2R, R2D, V, M, BODY, humerus, scap, lift, armFrames, bvec, wdir, circInt, foldMargin, axisAngle, onCone,
                greatArc, wrap180, sph3r, KEYS, motion, makeCtx, dls, register, concepts, order, solveFrame, run, resSplit,
                CLOSE_MM, CLOSE_DEG, ROLES: ['active', 'passive', 'fixed-scapula', 'fixed-arm', 'link'],
                KINDS: ['hub', 'link', 'arc', 'rail', 'carriage', 'slider', 'telescope', 'strap', 'ring', 'plate', 'point'] };
  root.KIN = KIN;
  if (typeof module !== 'undefined' && module.exports) module.exports = KIN;
})(typeof window !== 'undefined' ? window : globalThis);

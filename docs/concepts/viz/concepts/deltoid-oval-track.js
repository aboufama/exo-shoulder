/* deltoid-oval-track - J3 is a CLOSED oval cam track fixed to the arm on the deltoid cap (Ti 8 x 5, ~60 x 125 mm, at one
 * radius R_O from GH), carrying the J2 hub on a 20 x 16 bogie carriage; J1 is an O20 hub on the lateral acromion top
 * (b = bvec(106, 64)); link 1 (arc a1 = 70 deg) runs from J1 down over the acromion edge to J2. No link 2, no J3 hub,
 * no separate neck: the oval is the arm end and merges into BOTTOM (docs/concepts/models/deltoid-oval-track.py PARAMS;
 * oval u(t) = wdir(95 + 30 cos t, -10 + 60 sin t), band humerus frame). Closure: the circle at a1 about b, seen in the
 * arm frame, must cross the oval - a 1-D root t along it (branch sigma = sign of the oval tangent . b); q1 = azimuth of
 * the crossing about b, q2 = twist about p2 between link 1 and the carriage. Closed form (root along the oval, nearest
 * to the previous frame); where the circle misses the oval the closest approach is shown and the residual says so.
 * Model status: dead on the bench (reach 0: contact / part-part), the kinematics here are the idea itself. 3 active. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { b_az: 106, b_el: 64, a1: 70, d0: 95, a0: -10, A: 30, Bw: 60, sigma: 1, sing: 10,
              R_O: 62, F1: 55, hub_r: 10, stack: 12.25, car: [20, 16, 9], cuff_at: 165 };
  const b = V.unit(K.bvec(P.b_az, P.b_el)), N = 360;
  const u = t => K.wdir(P.d0 + P.A * Math.cos(t * D2R), P.a0 + P.Bw * Math.sin(t * D2R));     // t in deg
  const tan = t => V.unit(V.reject(V.sub(u(t + 0.05), u(t - 0.05)), u(t)));
  const G = t => { const x = u(t), y = tan(t); return M.fromCols(x, y, V.cross(x, y)); };      // carriage frame (arm)
  const wrap360 = t => ((t % 360) + 360) % 360;
  /** roots t of angle(bh, u(t)) = a1 on branch sigma (bh = b in the arm frame); refined by bisection */
  function roots(bh) {
    const f = t => V.angle(bh, u(t)) - P.a1, out = [];
    for (let i = 0; i < N; i++) {
      let t0 = i * 360 / N, t1 = (i + 1) * 360 / N, f0 = f(t0), f1 = f(t1);
      if ((f0 <= 0) === (f1 <= 0)) continue;
      for (let k = 0; k < 30; k++) { const tm = (t0 + t1) / 2, fm = f(tm); if ((fm <= 0) === (f0 <= 0)) { t0 = tm; f0 = fm; } else t1 = tm; }
      const t = (t0 + t1) / 2, cphi = V.dot(tan(t), bh) / Math.sin(P.a1 * D2R);
      if (Math.sign(cphi) === P.sigma) out.push({ t, cphi });
    }
    return out;
  }
  // home configuration (arm at H = S): the root with the most transversal crossing
  const home = roots(b).sort((x, y) => Math.abs(y.cphi) - Math.abs(x.cphi))[0] || { t: 90 };
  const p20 = u(home.t), T0 = tan(home.t), G0 = G(home.t);
  function joint(ctx, t) {                                         // q1, q2 for a carriage at t (closed form)
    const Q = M.mul(M.T(ctx.S), ctx.H), q1 = K.axisAngle(b, p20, M.mulv(Q, u(t))), R1 = M.rot(b, q1);
    return [t, q1, K.axisAngle(p20, T0, M.mulv(M.T(R1), M.mulv(Q, tan(t))))];
  }

  K.register({
    id: 'deltoid-oval-track',
    name: 'Deltoid oval track (J3 a closed cam track on the arm)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => joint(ctx, home.t),
    qNames: ['J3 carriage on the oval (t)', 'J1', 'J2'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: (ctx, qPrev) => {
      const Q = M.mul(M.T(ctx.S), ctx.H), bh = M.mulv(M.T(Q), b), rs = roots(bh), tp = qPrev ? qPrev[0] : home.t;
      let t;
      if (rs.length) t = rs.reduce((a, r) => (Math.abs(K.wrap180(r.t - tp)) < Math.abs(K.wrap180(a.t - tp)) ? r : a)).t;
      else {                                                       // no closure: closest approach near the last carriage spot
        let best = 1e9; for (let d = -60; d <= 60; d += 0.5) { const e = Math.abs(V.angle(bh, u(tp + d)) - P.a1); if (e < best) { best = e; t = tp + d; } }
      }
      ctx.ovalJump = Math.abs(K.wrap180(t - tp));                 // read by check(): a vanished root means a flip
      return joint(ctx, wrap360(t));
    },
    residual: (q, ctx) => {
      const R = M.mul(M.mul(M.mul(ctx.S, M.rot(b, q[1])), M.rot(p20, q[2])), M.mul(G0, M.T(G(q[0]))));
      return M.rotErrDeg(R, ctx.H);
    },
    check: (q, ctx) => {
      const Q = M.mul(M.T(ctx.S), ctx.H), bh = M.mulv(M.T(Q), b);
      const cphi = V.dot(tan(q[0]), bh) / Math.sin(P.a1 * D2R);
      if (Math.abs(V.angle(bh, u(q[0])) - P.a1) > 0.5) return 'the J1 circle misses the oval: no closure';
      if (Math.abs(cphi) < Math.sin(P.sing * D2R)) return 'link 1 tangent to the oval (singular)';
      if (ctx.ovalJump > 25) return 'the tracked crossing vanished: the carriage would have to jump along the oval';
      return null;
    },
    parts: (q, ctx) => {
      const H = ctx.H, p2 = M.mulv(H, u(q[0])), T = M.mulv(H, tan(q[0])), B = M.mulv(ctx.S, b), harm = ctx.armAxis;
      const oval = []; for (let i = 0; i <= 72; i++) oval.push(V.scale(M.mulv(H, u(i * 5)), P.R_O - 2.5));
      const cuffC = V.scale(harm, P.cuff_at), low = M.mulv(H, u(180)), lowPt = V.scale(low, P.R_O - 2.5);    // t 180: delta 65 (deltoid belly)
      const cuffTop = V.madd(cuffC, V.unit(V.reject(lowPt, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (lateral acromion)', c: V.scale(B, P.F1 - 3), z: B, x: ctx.attach.scapDir([1, 0, 0]), size: [36, 28], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(B, P.F1), axis: B, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'link 1 (70 deg)', u: B, v: p2, r0: P.F1 + 7, r1: P.R_O + 4 + 5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (on the carriage)', c: V.scale(p2, P.R_O + 4), axis: p2, r: P.hub_r, h: P.stack },
        { kind: 'carriage', role: 'active', name: 'J3: bogie carriage on the oval', c: V.scale(p2, P.R_O - 0.5), x: T, z: p2, size: P.car },
        { kind: 'arc', role: 'fixed-arm', name: 'closed oval track (arm-fixed)', pts: oval, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'oval into BOTTOM / cuff', a: lowPt, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

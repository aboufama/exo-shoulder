/* rotator-cuff-pair - a PARALLEL mechanism laid out like the rotator cuff (catalogue entry rotator-cuff-pair; no bench
 * model yet). Leg 1 (supraspinatus line): radial pivot on a scapula pad A1 = bvec(20, 75) [passive] -> telescoping
 * great-circle arc, length theta1 [ACTIVE] -> O20 v5 hub at the "exo greater tubercle" B1 = wdir(112, -15) on the arm,
 * the arm's lowest-motion spot [ACTIVE: the twist tau between leg 1's arc and the arm pad]. Leg 2 (infraspinatus line):
 * radial pivot on a pad A2 = bvec(-10, 25) over the infraspinous fossa [passive] -> telescoping arc theta2 [ACTIVE] ->
 * radial pivot on a posterior arm pad B2 = wdir(95, -55) [passive]. Mobility 6 + 3 - 2 x 3 = 3: 3 active (theta1,
 * theta2, tau) + 3 passive pivots, every one set by its leg's end points (closure). q = [theta1, theta2, tau, pivot A1,
 * pivot A2, pivot B2] (deg), closed form; the residual rebuilds each leg end from its pivot + length. Rejected: theta
 * outside [20, 160] (or a telescope past its 3-stage span), leg 2 within 19 mm of the B1 hub, and an UNSENSABLE pose
 * (the 3 x 3 sensing Jacobian of (theta1, theta2, tau) under small arm rotations, rows normalised, |det| < 0.1).
 * Telescopes: the spec's telescope3 (3 stages, theta_max / theta_min <= 2.6), each leg's window placed on this loop to
 * hold the most frames (the span ratio is the concept's main risk). Pad radius 58 mm (schematic). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { A1: [20, 75], A2: [-10, 25], B1: [112, -15], B2: [95, -55], rho0: 58, lift: 3.15, hub_r: 10, stack: 12.25,
              th_min: 20, th_max: 160, span: 2.6, hub_clear: 19, det_min: 0.1, bar: [0, -70, 67.5], cuff_at: 165 };
  const A1 = K.bvec(...P.A1), A2 = K.bvec(...P.A2), B1 = K.wdir(...P.B1), B2 = K.wdir(...P.B2), D2R = K.D2R, R2D = K.R2D;
  const t0 = V.unit(V.reject([0, -1, 0], B1)), t2 = V.unit(V.reject([0, -1, 0], B2));      // arm-fixed tangents at B1, B2
  const sref1 = V.unit(V.reject([1, 0, 0], A1)), sref2 = V.unit(V.reject([1, 0, 0], A2));  // scapula-fixed tangents at A1, A2
  const tanTo = (from, to) => V.unit(V.reject(to, from));                                  // great-circle tangent at `from`
  const along = (p, q, a) => V.add(V.scale(p, Math.cos(a * D2R)), V.scale(tanTo(p, q), Math.sin(a * D2R)));
  const signed = (k, ref, v) => K.axisAngle(k, ref, v);

  function ends(ctx, H) {
    H = H || ctx.H; const S = ctx.S;
    return { P1: M.mulv(S, A1), P2: M.mulv(S, A2), Q1: M.mulv(H, B1), Q2: M.mulv(H, B2), T1: M.mulv(H, t0), T2: M.mulv(H, t2),
             R1: M.mulv(S, sref1), R2: M.mulv(S, sref2) };
  }
  const coords = e => [V.angle(e.P1, e.Q1), V.angle(e.P2, e.Q2), signed(e.Q1, e.T1, tanTo(e.Q1, e.P1))];
  function solve(ctx) {
    const e = ends(ctx);
    return coords(e).concat([signed(e.P1, e.R1, tanTo(e.P1, e.Q1)), signed(e.P2, e.R2, tanTo(e.P2, e.Q2)),
                             signed(e.Q2, e.T2, tanTo(e.Q2, e.P2))]);
  }
  /** sensing Jacobian |det| (rows normalised): (theta1, theta2, tau) under +-0.3 deg arm rotations about x, y, z */
  function sense(ctx) {
    const J = [[], [], []];
    for (const ax of [[1, 0, 0], [0, 1, 0], [0, 0, 1]]) {
      const a = coords(ends(ctx, M.mul(M.rot(ax, 0.3), ctx.H))), b = coords(ends(ctx, M.mul(M.rot(ax, -0.3), ctx.H)));
      for (let i = 0; i < 3; i++) J[i].push((i === 2 ? K.wrap180(a[i] - b[i]) : a[i] - b[i]) / 0.6);
    }
    const Jn = J.map(r => { const n = Math.hypot(...r) || 1e-12; return r.map(x => x / n); });
    return Math.abs(V.dot(Jn[0], V.cross(Jn[1], Jn[2])));
  }
  // telescope stage length per leg, sized on this loop: the [Ls, 2.6 Ls] window that holds the most frames
  let LS = null;
  function stages() {
    if (LS) return LS;
    const th = K.motion(120).map(f => coords(ends(K.makeCtx(f.pose))));
    return (LS = [0, 1].map(k => {
      const t = th.map(x => x[k]).filter(x => x >= P.th_min && x <= P.th_max);
      let best = [-1, 0];
      for (const c of t.concat(t.map(x => x / P.span))) {
        const n = t.filter(x => x >= c - 1e-9 && x <= P.span * c + 1e-9).length;
        if (n > best[0]) best = [n, c];
      }
      return best[1];
    }));
  }
  function legParts(P0, Q0, th, Ls, R, name) {          // 3 nested arcs: sleeve on the pivot, two moving stages
    const e = Math.max(0, (th - Ls) / 2), seg = (a, b, r, dr, role, nm) =>
      ({ kind: 'arc', role, name: `${name} ${nm}`, pts: K.greatArc(along(P0, Q0, a), along(P0, Q0, b), R + dr, R + dr), r });
    return [seg(0, Ls, 3.4, 0, 'link', 'sleeve'), seg(e, e + Ls, 2.7, 0.6, 'active', 'stage 2'), seg(2 * e, 2 * e + Ls, 2.0, 1.2, 'active', 'stage 3')];
  }
  // smallest distance (mm, at radius R) from point dir x to the great-circle arc p -> q
  function arcDist(p, q, x, R) {
    let best = 1e9; const th = V.angle(p, q);
    for (let i = 0; i <= 30; i++) best = Math.min(best, V.angle(along(p, q, th * i / 30), x));
    return best * D2R * R;
  }

  K.register({
    id: 'rotator-cuff-pair',
    name: 'Rotator-cuff pair (two telescoping arcs + tubercle hub)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['leg 1 length', 'leg 2 length', 'B1 hub twist', 'pivot A1', 'pivot A2', 'pivot B2'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => {
      const e = ends(ctx), rot = (k, ref, a) => M.mulv(M.rot(k, a), ref);
      const Q1 = V.add(V.scale(e.P1, Math.cos(q[0] * D2R)), V.scale(rot(e.P1, e.R1, q[3]), Math.sin(q[0] * D2R)));
      const Q2 = V.add(V.scale(e.P2, Math.cos(q[1] * D2R)), V.scale(rot(e.P2, e.R2, q[4]), Math.sin(q[1] * D2R)));
      return V.scale(V.sub(Q1, e.Q1), R2D).concat(V.scale(V.sub(Q2, e.Q2), R2D),
        [K.wrap180(q[2] - signed(e.Q1, e.T1, tanTo(e.Q1, e.P1))), K.wrap180(q[5] - signed(e.Q2, e.T2, tanTo(e.Q2, e.P2)))]);
    },
    check: (q, ctx) => {
      const L = stages();
      for (let k = 0; k < 2; k++) {
        if (q[k] < P.th_min || q[k] > P.th_max) return `leg ${k + 1} arc outside [${P.th_min}, ${P.th_max}] deg`;
        if (q[k] < L[k] - 1e-6) return `leg ${k + 1} telescope fully collapsed`;
        if (q[k] > P.span * L[k] + 1e-6) return `leg ${k + 1} telescope fully extended`;
      }
      const e = ends(ctx);
      if (arcDist(e.P2, e.Q2, e.Q1, P.rho0) < P.hub_clear) return 'leg 2 crosses the B1 hub';
      const d = sense(ctx);
      if (d < P.det_min) return `unsensable: sensing Jacobian |det| ${d.toFixed(2)}`;
      return null;
    },
    parts: (q, ctx) => {
      const e = ends(ctx), L = stages(), R = P.rho0 + P.lift, h = P.stack;
      const bar = M.mulv(ctx.H, P.bar), cuffC = V.scale(ctx.armAxis, P.cuff_at);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'pad A1 (supraspinous fossa)', c: V.scale(e.P1, P.rho0 - 3), z: e.P1, x: e.R1, size: [24, 24], t: 3 },
        { kind: 'hub', role: 'passive', name: 'pivot A1', c: V.scale(e.P1, P.rho0), axis: e.P1, r: 6, h: 5 },
        ...legParts(e.P1, e.Q1, q[0], L[0], R, 'leg 1'),
        { kind: 'plate', role: 'fixed-scapula', name: 'pad A2 (infraspinous fossa)', c: V.scale(e.P2, P.rho0 - 3), z: e.P2, x: e.R2, size: [24, 24], t: 3 },
        { kind: 'hub', role: 'passive', name: 'pivot A2', c: V.scale(e.P2, P.rho0), axis: e.P2, r: 6, h: 5 },
        ...legParts(e.P2, e.Q2, q[1], L[1], R + 1.5, 'leg 2'),
        { kind: 'hub', role: 'active', name: 'B1 hub (exo greater tubercle)', c: V.scale(e.Q1, P.rho0), axis: e.Q1, r: P.hub_r, h },
        { kind: 'hub', role: 'passive', name: 'pivot B2', c: V.scale(e.Q2, P.rho0), axis: e.Q2, r: 6, h: 5 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm bridge B1 - B2', u: e.Q1, v: e.Q2, r0: P.rho0 - 2, r1: P.rho0 - 2, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm piece to BOTTOM', pts: K.greatArc(e.Q1, bar, P.rho0 - 2, V.norm(bar)), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

/* coupler-path-j1 - J1 replaced by a spherical FOUR-BAR on the base: J2 rides a synthesised coupler path instead of
 * a circle about one base axis (catalogue coupler-path-j1; ideated, no model or sweep yet). Base hubs A0 (crank,
 * ACTIVE) and B0 (rocker, PASSIVE) ~30 deg apart on the acromion / spine; crank arc alpha, rocker arc beta, coupler
 * arc c; the coupler = link 1 (passive pins A1, B1) carries J2's axis p2 at a coupler point (arc kd from A1, angle
 * kphi from A1 -> B1). J2 and J3 are the final's distal 2R (a2 81.45, W0 = wdir(71.38, 4.78)). Every axis through GH.
 * 3 ACTIVE (crank, J2, J3) + 3 PASSIVE (B0, A1, B1, set by the four-bar closure). Closed form = the spec's IK: scan
 * the crank angle t, roots of angle(p2(t), p3) - a2, bisection, root nearest the previous frame; reject a four-bar
 * transmission angle outside [25, 155] or a coupler path within 10 deg of tangency to J3's circle (fold).
 * Four-bar dimensions are hand-picked inside the spec's ranges so the whole loop closes (crank swings ~90 deg, rocker
 * ~37 deg); the spec's CMA-ES synthesis on the skin-radius spread under J2 has not run: not a bench result. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 32.55, el: 80.56, bAng: 30, bPhi: 200, alpha: 35, beta: 45, c: 30, s4: 1, kd: 50, kphi: 160,
              a2: 81.45, w: [71.38, 4.78], trace: [-95, 10], tmin: 25, fold: 10, faces: [54, 60, 66, 70, 72], hub_r: 10, pin_r: 8, stack: 12.25,
              neck_deg: 25, cuff_at: 165 };
  const A0 = K.bvec(P.az, P.el), ref = V.unit(V.cross(A0, [0, 1, 0])), B0 = K.onCone(A0, ref, P.bAng, P.bPhi), W0 = K.wdir(P.w[0], P.w[1]);
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  /** four-bar + coupler point for crank angle t (deg), scapula frame */
  function bar(t) {
    const A1 = K.onCone(A0, ref, P.alpha, t), c = K.circInt(B0, P.beta, A1, P.c, P.s4), B1 = c.p;
    return { A1, B1, p2: K.onCone(A1, B1, P.kd, P.kphi), ok: c.ok, tr: V.angle(V.reject(B0, B1), V.reject(A1, B1)) };
  }
  const L2f = (p2, p3) => M.fromCols(p3, V.unit(V.reject(p2, p3)), V.cross(p3, V.unit(V.reject(p2, p3))));
  function roots(p3) {
    const out = []; let a = bar(-180), ga = V.angle(a.p2, p3) - P.a2;
    for (let t = -179; t <= 180; t++) {
      const b = bar(t), gb = V.angle(b.p2, p3) - P.a2;
      if (a.ok && b.ok && Math.sign(ga) !== Math.sign(gb)) {
        let lo = t - 1, hi = t, glo = ga;
        for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2, gm = V.angle(bar(m).p2, p3) - P.a2; if (Math.sign(gm) === Math.sign(glo)) { lo = m; glo = gm; } else hi = m; }
        out.push((lo + hi) / 2);
      }
      a = b; ga = gb;
    }
    return out;
  }
  // home = the rest pose, on the root with the best transmission
  const Qh = Qof(K.makeCtx(K.KEYS[0].pose)), p3h = M.mulv(Qh, W0);
  const th = roots(p3h).sort((x, y) => Math.abs(bar(x).tr - 90) - Math.abs(bar(y).tr - 90))[0] || 0, bh = bar(th), L2h = L2f(bh.p2, p3h);
  /** q = [crank t, J2, J3, rocker B0, pin A1, pin B1] (deg; passive values are reported, set by the closure) */
  function full(t, p3, Q) {
    const b = bar(t), q2 = K.axisAngle(b.p2, b.A1, p3), Mr = M.mul(M.mul(M.mul(Q, M.T(Qh)), L2h), M.T(L2f(b.p2, p3))), v = V.perp(p3);
    return [t, q2, K.axisAngle(p3, v, M.mulv(Mr, v)), K.axisAngle(B0, A0, b.B1), K.axisAngle(b.A1, A0, b.B1), K.axisAngle(b.B1, B0, b.A1)];
  }
  function fk(q) {
    const b = bar(q[0]), p3 = K.onCone(b.p2, b.A1, P.a2, q[1]);
    return Object.assign(b, { p3, E: M.mul(M.mul(M.mul(M.rot(p3, q[2]), L2f(b.p2, p3)), M.T(L2h)), Qh) });
  }
  function solve(ctx, qPrev) {
    const Q = Qof(ctx), p3 = M.mulv(Q, W0), tp = qPrev ? qPrev[0] : th, rs = roots(p3);
    if (!rs.length) return qPrev ? qPrev.slice() : [th, 0, 0, 0, 0, 0];
    const t = rs.reduce((a, b) => Math.abs(K.wrap180(b - tp)) < Math.abs(K.wrap180(a - tp)) ? b : a);
    return full(t, p3, Q);
  }

  K.register({
    id: 'coupler-path-j1',
    name: 'Four-bar base (J2 on a coupler path)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx, null),
    qNames: ['crank A0', 'J2', 'J3', 'rocker B0 (passive)', 'pin A1 (passive)', 'pin B1 (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => M.rotErrDeg(M.mul(ctx.S, fk(q).E), ctx.H),
    check: (q, ctx) => {
      const b = fk(q);
      if (!b.ok) return 'the four-bar cannot assemble';
      if (b.tr < P.tmin || b.tr > 180 - P.tmin) return `four-bar transmission angle ${b.tr.toFixed(0)} deg (toggle)`;
      const d = V.sub(bar(q[0] + 0.5).p2, bar(q[0] - 0.5).p2), p3 = b.p3;
      const cross = 90 - V.angle(d, V.reject(p3, b.p2));       // path direction vs J3's circle about p3
      if (Math.abs(cross) < P.fold) return 'coupler path tangent to J3\'s circle (fold)';
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q), S = ctx.S, W = d => M.mulv(S, d), F = P.faces, h = P.stack;
      const a0 = W(A0), b0 = W(B0), a1 = W(f.A1), b1 = W(f.B1), p2 = W(f.p2), p3 = W(f.p3), harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[4] + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const path = []; for (let i = 0; i <= 40; i++) { const b = bar(P.trace[0] + (P.trace[1] - P.trace[0]) * i / 40); path.push(V.scale(W(b.p2), F[2] - 4)); }
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(V.unit(V.add(a0, b0)), F[0] - 3), z: V.unit(V.add(a0, b0)), x: V.unit(V.sub(b0, a0)), size: [56, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'A0 crank (J1)', c: V.scale(a0, F[0]), axis: a0, r: P.hub_r, h },
        { kind: 'hub', role: 'passive', name: 'B0 rocker pivot', c: V.scale(b0, F[0]), axis: b0, r: P.pin_r, h: 9 },
        { kind: 'arc', role: 'link', name: 'crank', u: a0, v: a1, r0: F[0] + h, r1: F[1], r: 2.2 },
        { kind: 'arc', role: 'link', name: 'rocker', u: b0, v: b1, r0: F[0] + 9, r1: F[1], r: 2.2 },
        { kind: 'hub', role: 'passive', name: 'A1 coupler pin', c: V.scale(a1, F[1]), axis: a1, r: P.pin_r, h: 9 },
        { kind: 'hub', role: 'passive', name: 'B1 coupler pin', c: V.scale(b1, F[1]), axis: b1, r: P.pin_r, h: 9 },
        { kind: 'arc', role: 'link', name: 'coupler = link 1 (A1-B1)', u: a1, v: b1, r0: F[1] + 9, r1: F[1] + 9, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'coupler = link 1 (to J2)', u: V.unit(V.add(a1, b1)), v: p2, r0: F[1] + 9, r1: F[2] + 2, r: 2.5 },
        { kind: 'arc', role: 'fixed-scapula', name: 'coupler path of J2 over the loop (trace, not metal)', pts: path, r: 0.6 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(p2, F[2]), axis: p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', u: p2, v: p3, r0: F[2] + 9, r1: F[4] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(p3, F[4]), axis: p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: p3, v: nk, r0: F[4] + 1, r1: F[4] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

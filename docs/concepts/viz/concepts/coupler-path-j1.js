/* coupler-path-j1 - J1 of the pin-knee leader replaced by a spherical FOUR-BAR on the scapula base: J2's axis rides a
 * coupler curve (a fold lever with no spring, no sensor). Base hubs A0 (crank, ACTIVE, O20) and B0 (rocker pin); crank
 * arc alpha, rocker arc beta, coupler arc c; the coupler = link 1 (pins A1, B1) carries J2's axis p2 at a coupler
 * point (arc kd from A1, angle kphi from the A1 -> B1 direction). kd = 0 puts J2 ON the crank (a circle about A0 = a
 * re-seated plain 3R: the control). Every axis passes through GH. 3 ACTIVE (crank, J2, J3) + rocker / pins set by the
 * loop. The model (docs/concepts/models/coupler-path-j1.py) closes the arm end with the leader's pin knee; this preview
 * draws the arm end as a neck to the cuff. IK = the model's: roots of angle(p2(t), p3) = a2 over the crank angle t,
 * bisection, root nearest the previous frame; red = the four-bar's transmission angle outside [25, 155] or the
 * osculating-circle fold rule (margin < 10 deg, the bench's m). Parameters: the sweep's best (see the P block). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = {"A0": [0.11259, 0.90999, 0.39905], "B0": [-0.3047, 0.82473, 0.47642], "W0": [-0.18127, -0.0897, 0.97933], "alpha": 40.12, "beta": 40.0, "c": 40.0, "s4": 1, "kd": 0.0, "kphi": 0.0, "a2": 72.31, "branch": 1, "ideal": 1, "tmin": 25, "fold": 10, "faces": [49.9, 60.9, 72.0], "hub_r": 10, "pin_r": 6, "stack": 12.25, "neck_deg": 25, "cuff_at": 165};
  const A0 = V.unit(P.A0), B0 = V.unit(P.B0), W0 = V.unit(P.W0), ref = V.unit(V.cross(A0, [0, 1, 0]));
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  /** four-bar + coupler point for crank angle t (deg), scapula frame */
  function bar(t) {
    const A1 = K.onCone(A0, ref, P.alpha, t);
    if (P.ideal) return { A1, B1: A1, p2: A1, ok: true, tr: 90 };
    const c = K.circInt(B0, P.beta, A1, P.c, P.s4), B1 = c.p;
    const p2 = P.kd > 0 ? K.onCone(A1, B1, P.kd, P.kphi) : A1;
    return { A1, B1, p2, ok: c.ok, tr: V.angle(V.reject(B0, B1), V.reject(A1, B1)) };
  }
  /** osculating-circle fold margin (deg) of the coupler curve at crank t against J3's axis p3 */
  function margin(t, p3) {
    const a = bar(t - 0.5).p2, b = bar(t).p2, c = bar(t + 0.5).p2;
    let n = V.unit(V.cross(V.sub(c, a), V.add(V.sub(c, b), V.sub(a, b))));
    if (V.dot(n, b) < 0) n = V.scale(n, -1);
    const rho = V.angle(n, b), th = V.angle(n, p3);
    return Math.min(th - Math.abs(rho - P.a2), Math.min(rho + P.a2, 360 - rho - P.a2) - th);
  }
  function roots(p3) {
    const out = []; let a = bar(-180), ga = V.angle(a.p2, p3) - P.a2;
    for (let t = -179; t <= 180; t++) {
      const b = bar(t), gb = V.angle(b.p2, p3) - P.a2;
      if (a.ok && b.ok && Math.sign(ga) !== Math.sign(gb)) {
        let lo = t - 1, hi = t, glo = ga;
        for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2, gm = V.angle(bar(m).p2, p3) - P.a2; if (Math.sign(gm) === Math.sign(glo)) { lo = m; glo = gm; } else hi = m; }
        const r = (lo + hi) / 2, d = V.sub(bar(r + 0.25).p2, bar(r - 0.25).p2);
        if (Math.sign(V.dot(d, p3)) === P.branch) out.push(r);
      }
      a = b; ga = gb;
    }
    return out;
  }
  const L2f = (p2, p3) => M.fromCols(p3, V.unit(V.reject(p2, p3)), V.cross(p3, V.unit(V.reject(p2, p3))));
  const Qh = Qof(K.makeCtx(K.KEYS[0].pose)), p3h = M.mulv(Qh, W0);
  const th0 = roots(p3h).sort((x, y) => margin(y, p3h) - margin(x, p3h))[0] || 0, bh = bar(th0), L2h = L2f(bh.p2, p3h);
  const jref = b => (P.kd === 0 || P.ideal) ? A0 : b.A1;            // azimuth reference of J2 (never parallel to p2)
  function full(t, p3, Q) {
    const b = bar(t), q2 = K.axisAngle(b.p2, jref(b), p3), Mr = M.mul(M.mul(M.mul(Q, M.T(Qh)), L2h), M.T(L2f(b.p2, p3))), v = V.perp(p3);
    return [t, q2, K.axisAngle(p3, v, M.mulv(Mr, v))];
  }
  function fk(q) {
    const b = bar(q[0]), p3 = K.onCone(b.p2, jref(b), P.a2, q[1]);
    return Object.assign(b, { p3, E: M.mul(M.mul(M.mul(M.rot(p3, q[2]), L2f(b.p2, p3)), M.T(L2h)), Qh) });
  }
  function solve(ctx, qPrev) {
    const Q = Qof(ctx), p3 = M.mulv(Q, W0), tp = qPrev ? qPrev[0] : th0, rs = roots(p3);
    if (!rs.length) return qPrev ? qPrev.slice() : [th0, 0, 0];
    const t = rs.reduce((a, b) => Math.abs(K.wrap180(b - tp)) < Math.abs(K.wrap180(a - tp)) ? b : a);
    return full(t, p3, Q);
  }
  K.register({
    id: 'coupler-path-j1',
    name: 'Four-bar base (J2 on a coupler path)',
    dof: { active: 3, passive: P.ideal ? 0 : 3 },
    params: P,
    q0: ctx => solve(ctx, null),
    qNames: ['crank A0', 'J2', 'J3'],
    qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => M.rotErrDeg(M.mul(ctx.S, fk(q).E), ctx.H),
    check: (q, ctx) => {
      const b = bar(q[0]), p3 = M.mulv(Qof(ctx), W0);
      if (!b.ok) return 'the four-bar cannot assemble';
      if (!P.ideal && (b.tr < P.tmin || b.tr > 180 - P.tmin)) return `four-bar transmission angle ${b.tr.toFixed(0)} deg (toggle)`;
      if (margin(q[0], p3) < P.fold) return 'J2 fold (osculating-circle margin < 10 deg)';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = d => M.mulv(S, d), F = P.faces, h = P.stack, b = bar(q[0]), Q = Qof(ctx);
      const a0 = W(A0), b0 = W(B0), a1 = W(b.A1), b1 = W(b.B1), p2 = W(b.p2), p3 = W(M.mulv(Q, W0)), harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[2] + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const path = []; for (let i = 0; i <= 72; i++) path.push(V.scale(W(bar(-180 + 5 * i).p2), F[1] - 4));
      return [
        { kind: 'hub', role: 'active', name: 'A0 crank (J1)', c: V.scale(a0, F[0]), axis: a0, r: P.hub_r, h },
        { kind: 'hub', role: 'passive', name: 'B0 rocker pivot', c: V.scale(b0, F[0]), axis: b0, r: P.pin_r, h: 6 },
        { kind: 'arc', role: 'link', name: 'crank', u: a0, v: a1, r0: F[0] + h, r1: F[0] + h, r: 2.2 },
        { kind: 'arc', role: 'link', name: 'rocker', u: b0, v: b1, r0: F[0] + 6, r1: F[0] + h, r: 2.2 },
        { kind: 'hub', role: 'passive', name: 'A1 coupler pin', c: V.scale(a1, F[0] + h), axis: a1, r: P.pin_r, h: 6 },
        { kind: 'hub', role: 'passive', name: 'B1 coupler pin', c: V.scale(b1, F[0] + h), axis: b1, r: P.pin_r, h: 6 },
        { kind: 'arc', role: 'link', name: 'coupler = link 1 (A1-B1)', u: a1, v: b1, r0: F[0] + h + 6, r1: F[0] + h + 6, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'coupler = link 1 (to J2)', u: a1, v: p2, r0: F[0] + h + 6, r1: F[1], r: 2.5 },
        { kind: 'arc', role: 'fixed-scapula', name: 'coupler path of J2 (trace, not metal)', pts: path, r: 0.6 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(p2, F[1]), axis: p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', u: p2, v: p3, r0: F[1] + h, r1: F[2] + h, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(p3, F[2]), axis: p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: p3, v: nk, r0: F[2] + 1, r1: F[2] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

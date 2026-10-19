/* offset-axis-skin-hubs - off-sphere skin hubs + passive cuff stage: axis DIRECTIONS spherical (the champion's,
 * r20 s1414 #4), axis POSITIONS free (catalogue offset-axis-skin-hubs; ideated, no model or sweep yet). Each hub lies
 * flat on its own skin patch (J1 a thin KAA15XL0 donut on the crown, J2 / J3 O20 hubs), its axis line 10-13 mm off
 * GH; member 3 runs down the lateral arm to a stage under the saddle at s 170 mm: one along-arm miniature guide (RSR7,
 * +-40 mm) + two short transverse guides (RSR3, +-8 mm). Offsets: the best of 3000 random line placements (|o| 10-20
 * mm) for the most loop frames inside those travels (106 / 114 in-band frames) - a stand-in for the spec's minimax
 * fit with hubs at ENV + 2, which needs the skin. Orientation = the spherical IK of the directions (closed form); the
 * slides = member 3's drift since rest (assembled centred). 3 ACTIVE + 3 PASSIVE (mobility 3 + 3 + 3 - 6 = 3). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
              w: [86.32769021001913, 21.829657347343378], branch: -1,
              c: [[3.16, 0.44, 10.85], [-7.54, -2.52, -6.95], [-7.45, -10.58, 2.25]], S_a: 40, S_t: 8, at_s: 170, r_arm: 52,
              faces: [50, 90, 70], hub_r: 10, donut_r: 16, stack: 12.25, sing: 10 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch), u = [C.u1, C.u2, C.u3], c = P.c;
  const h0 = [0, -1, 0], sn = V.unit(V.reject(u[2], h0)), st = V.cross(sn, h0);                    // stage: along h0, across st, radial sn
  const stageC = V.add(V.scale(h0, P.at_s), V.scale(sn, P.r_arm));                                  // on the lateral arm (rest coords)
  function fk(q) {
    const R1 = M.rot(u[0], q[0]), R2 = M.rot(u[1], q[1]), R3 = M.rot(u[2], q[2]), R12 = M.mul(R1, R2);
    const t1 = V.sub(c[0], M.mulv(R1, c[0])), t2 = V.add(t1, M.mulv(R1, V.sub(c[1], M.mulv(R2, c[1]))));
    return { X1: [R1, t1], X2: [R12, t2], X3: [M.mul(R12, R3), V.add(t2, M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))))] };
  }
  const ap = (X, p) => V.add(M.mulv(X[0], p), X[1]), Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  const drift = (q, Q) => M.mulv(M.T(Q), fk(q).X3[1]);
  const rc = K.makeCtx(K.KEYS[0].pose), d0 = drift(C.solve(rc), Qof(rc));
  const sv = q => V.add(d0, V.add(V.add(V.scale(h0, q[3]), V.scale(st, q[4])), V.scale(sn, q[5])));
  function solve(ctx) { const q = C.solve(ctx), d = V.sub(drift(q, Qof(ctx)), d0); return q.concat([V.dot(d, h0), V.dot(d, st), V.dot(d, sn)]); }

  K.register({
    id: 'offset-axis-skin-hubs',
    name: 'Off-sphere skin hubs + cuff stage',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'guide along the arm', 'guide across', 'guide radial'], qUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => { const X = fk(q).X3, Q = Qof(ctx); return M.rotErrDeg(X[0], Q).concat(V.sub(X[1], M.mulv(Q, sv(q)))); },
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      if (Math.abs(q[3]) > P.S_a) return `along-arm guide past +-${P.S_a} mm (${q[3].toFixed(1)})`;
      if (Math.abs(q[4]) > P.S_t || Math.abs(q[5]) > P.S_t) return `transverse guide past +-${P.S_t} mm`;
      return null;
    },
    parts: (q, ctx) => {
      const W = p => M.mulv(ctx.S, p), F = P.faces, h = P.stack, { X1, X2, X3 } = fk(q), Q = Qof(ctx), arm = p => W(M.mulv(Q, p));
      const hubs = [[0, [M.I3(), [0, 0, 0]]], [1, X1], [2, X2]].map(([k, X]) => {
        const ax = M.mulv(X[0], u[k]), p0 = ap(X, c[k]), d = k === 0;
        return { kind: 'hub', role: 'active', name: d ? 'J1 (KAA15XL0 donut flat on the crown)' : `J${k + 1} (flat on its skin patch)`, c: W(V.madd(p0, ax, F[k])),
                 axis: W(ax), r: d ? P.donut_r : P.hub_r, h: d ? 6 : h };
      });
      const top = (hb, dz) => V.madd(hb.c, hb.axis, dz), arcPts = (a, b) => K.greatArc(a, b, V.norm(a), V.norm(b));
      const s = [q[3], q[4], q[5]], aC = V.madd(stageC, h0, s[0]), tC = V.madd(aC, st, s[1]);
      const carr = W(ap(X3, V.madd(stageC, sn, 12)));                                    // member 3's end on the stage
      return [
        { kind: 'plate', role: 'fixed-scapula', c: W(V.madd(c[0], u[0], F[0] - 3)), z: W(u[0]), x: W([1, 0, 0]), size: [46, 32], t: 3 },
        hubs[0],
        { kind: 'arc', role: 'link', name: 'link 1', pts: arcPts(top(hubs[0], 6), V.madd(hubs[1].c, hubs[1].axis, 2)), r: 2.5 },
        hubs[1],
        { kind: 'arc', role: 'link', name: 'link 2', pts: arcPts(top(hubs[1], 9), top(hubs[2], h + 1)), r: 2.5 },
        hubs[2],
        { kind: 'link', role: 'link', name: 'member 3 down the lateral arm', a: top(hubs[2], h + 1), b: carr, r: 3 },
        { kind: 'plate', role: 'fixed-arm', name: 'saddle (BOTTOM) under the stage', c: arm(V.madd(stageC, sn, -2)), z: arm(sn), x: arm(h0), size: [20 + 2 * P.S_a, 24], t: 3 },
        { kind: 'slider', role: 'passive', name: 'RSR7 guide along the arm (+-40)', a: arm(V.madd(stageC, h0, -P.S_a)), b: arm(V.madd(stageC, h0, P.S_a)),
          at: arm(V.madd(aC, sn, 3)), z: arm(sn), size: [17, 14, 8] },
        { kind: 'slider', role: 'passive', name: 'RSR3 guide across (+-8)', a: arm(V.madd(V.madd(aC, sn, 8), st, -P.S_t)), b: arm(V.madd(V.madd(aC, sn, 8), st, P.S_t)),
          at: arm(V.madd(tC, sn, 9)), z: arm(sn), size: [12, 8, 4] },
        { kind: 'slider', role: 'passive', name: 'RSR3 guide radial (+-8)', a: arm(V.madd(tC, sn, 10 - P.S_t)), b: arm(V.madd(tC, sn, 12 + P.S_t)),
          at: carr, z: arm(h0), size: [8, 8, 4] },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: arm(V.scale(h0, P.at_s)), axis: arm(h0), r: 47, w: 30 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

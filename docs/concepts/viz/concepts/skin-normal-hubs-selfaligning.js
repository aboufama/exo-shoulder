/* skin-normal-hubs-selfaligning - non-concurrent 3R whose hubs stand square on their skin seats (axis = a blend of the
 * GH ray and the local skin normal, so the axis LINES miss GH by a few mm) + a passive XYZ translation stage that
 * takes the resulting drift (docs/concepts/skin-normal-hubs-selfaligning.md, models/skin-normal-hubs-selfaligning.py).
 * Best entry of the sweep that keeps the concept's own idea (blend > 0, slides on; the overall best is the spherical
 * control): gap 64.73, seats J1 bvec(82.95, 80.36) blend 0.32, J2 bvec(30.8, 48.42) blend 0.60, J3 wdir(71.38, 0.44)
 * blend 0.33; tilts 24 / 15 / 30 deg, lines 5.8 / 7.3 / 11.4 mm off GH; stage travel +-18.6 along the humerus,
 * +-16.4 across, +-6.0 normal; faces 46.6 / 75.5 / 72.8 mm. Axis lines (home frame H = S) dumped from the model's
 * Design (skin-normal seats need the scanned skin). 3 ACTIVE + 3 PASSIVE slides (mobility 3 + 3 + 3 - 6 = 3). Closed
 * form: the spherical IK of the three directions (only directions set orientation), then the slides = the drift of
 * member 3 in the stage frame (the model's s = Q^T t3). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { u: [[0.09594925326948651, 0.9687794379100976, 0.22860477133608453], [-0.3927455271775273, 0.7981813030538611, 0.4567904972033529],
                  [0.06351892896297213, -0.16387308032176973, 0.9844343346344904]],
              c: [[-5.071757710964899, 1.127187991939742, -2.64808639161191], [-6.596782180118382, -3.1589846615201154, -0.1519606950505903],
                  [-2.575183849291488, -10.95412124087594, -1.6573097995856259]],
              A: [32.85961836621343, 72.90643087935244], branch: -1, S_a: 18.6, S_t: 16.4, R_r: 6.0, faces: [46.6, 75.5, 72.8],
              tilt: [24.1, 14.9, 29.7], hub_r: 10, stack: 12.25, neck: 5, car_l: 20, sing: 10 };
  const u = P.u.map(V.unit), c = P.c, C = K.sph3r(u[0], u[2], P.A[0], P.A[1], P.branch);
  const h0 = [0, -1, 0], sn = u[2], sa = V.unit(V.reject(h0, sn)), st = V.cross(sn, sa);
  const stageC = V.madd(c[2], sa, P.hub_r + P.neck + P.car_l / 2 + P.S_a);
  /** member transforms [R, t] (p -> R p + t, scapula frame) of rotations q about the axis LINES (u_k through c_k) */
  function fk(q) {
    const R1 = M.rot(u[0], q[0]), R12 = M.mul(R1, M.rot(C.u2, q[1])), R123 = M.mul(R12, M.rot(u[2], q[2]));
    const t1 = V.sub(c[0], M.mulv(R1, c[0])), t2 = V.add(t1, M.mulv(R1, V.sub(c[1], M.mulv(M.rot(C.u2, q[1]), c[1]))));
    const t3 = V.add(t2, M.mulv(R12, V.sub(c[2], M.mulv(M.rot(u[2], q[2]), c[2]))));
    return { X1: [R1, t1], X2: [R12, t2], X3: [R123, t3] };
  }
  const ap = (X, p) => V.add(M.mulv(X[0], p), X[1]);
  const sv = q => V.add(V.add(V.scale(sa, q[3]), V.scale(st, q[4])), V.scale(sn, q[5]));
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const q = C.solve(ctx), d = M.mulv(M.T(Qof(ctx)), fk(q).X3[1]);            // member-3 drift in the arm rest frame
    return q.concat([V.dot(d, sa), V.dot(d, st), V.dot(d, sn)]);
  }

  K.register({
    id: 'skin-normal-hubs-selfaligning',
    name: 'Skin-normal hubs + passive XYZ stage',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'slide along the humerus', 'slide across', 'slide normal'], qUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => { const X = fk(q).X3, Q = Qof(ctx); return M.rotErrDeg(X[0], Q).concat(V.sub(X[1], M.mulv(Q, sv(q)))); },
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const lim = [P.S_a, P.S_t, P.R_r], nm = ['along', 'across', 'normal'];
      for (let i = 0; i < 3; i++) if (Math.abs(q[3 + i]) > lim[i]) return `slide ${nm[i]} past its range (${q[3 + i].toFixed(1)} mm)`;
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), F = P.faces, h = P.stack;
      const { X1, X2, X3 } = fk(q), Q = Qof(ctx), arm = p => W(M.mulv(Q, p));
      const hubs = [[0, [M.I3(), [0, 0, 0]], u[0]], [1, X1, C.u2], [2, X2, u[2]]].map(([k, X, uk]) => {
        const ax = M.mulv(X[0], uk), p0 = ap(X, c[k]);
        return { kind: 'hub', role: 'active', name: `J${k + 1} (square on its seat, ${P.tilt[k]} deg off the GH ray)`, c: W(V.madd(p0, ax, F[k])), axis: W(ax), r: P.hub_r, h };
      });
      const lineOf = (hb, k) => ({ kind: 'link', role: 'link', name: `J${k + 1} axis line, aimed ${V.norm(c[k]).toFixed(0)} mm off GH (construction line, not metal)`,
        a: V.madd(hb.c, hb.axis, -F[k] + 22), b: hb.c, r: 0.5 });
      const top = (hb, dz) => V.madd(hb.c, hb.axis, dz), arcPts = (a, b) => K.greatArc(a, b, V.norm(a), V.norm(b));
      const s = [q[3], q[4], q[5]], z0 = F[2] - 4, aC = V.madd(stageC, sa, s[0]), tC = V.madd(aC, st, s[1]);
      const m3Top = ap(X3, V.madd(stageC, sn, z0 + 6));
      return [
        { kind: 'plate', role: 'fixed-scapula', c: W(V.madd(c[0], u[0], F[0] - 3)), z: W(u[0]), x: W([1, 0, 0]), size: [46, 32], t: 3 },
        hubs[0], lineOf(hubs[0], 0),
        { kind: 'arc', role: 'link', name: 'link 1', pts: arcPts(top(hubs[0], 7), V.madd(hubs[1].c, hubs[1].axis, 2)), r: 2.5 },
        hubs[1], lineOf(hubs[1], 1),
        { kind: 'arc', role: 'link', name: 'link 2', pts: arcPts(top(hubs[1], 9), top(hubs[2], h + 1)), r: 2.5 },
        hubs[2], lineOf(hubs[2], 2),
        { kind: 'link', role: 'link', name: 'member 3 neck + bridge', a: W(ap(X3, V.madd(V.madd(c[2], u[2], F[2] + h - 2), sa, P.hub_r))), b: W(m3Top), r: 3 },
        { kind: 'plate', role: 'fixed-arm', name: 'stage rail on BOTTOM\'s top', c: arm(V.madd(stageC, sn, z0 - 8)), z: arm(sn), x: arm(sa), size: [20 + 2 * P.S_a, 22], t: 3 },
        { kind: 'slider', role: 'passive', name: 'slide along the humerus', a: arm(V.madd(V.madd(stageC, sn, z0 - 5), sa, -P.S_a)),
          b: arm(V.madd(V.madd(stageC, sn, z0 - 5), sa, P.S_a)), at: arm(V.madd(aC, sn, z0 - 3)), z: arm(sn), size: [16, 14, 4] },
        { kind: 'slider', role: 'passive', name: 'slide across', a: arm(V.madd(V.madd(aC, sn, z0 + 0.5), st, -P.S_t)),
          b: arm(V.madd(V.madd(aC, sn, z0 + 0.5), st, P.S_t)), at: arm(V.madd(tC, sn, z0 + 2)), z: arm(sn), size: [14, 14, 4] },
        { kind: 'slider', role: 'passive', name: 'slide normal', a: arm(V.madd(tC, sn, z0 + 2 - P.R_r)),
          b: arm(V.madd(tC, sn, z0 + 6 + P.R_r)), at: W(m3Top), z: arm(sa), size: [10, 10, 5] },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: arm(V.scale(h0, V.dot(stageC, h0) + 8)), axis: arm(h0), r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

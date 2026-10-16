/* fold-sph3r - plain spherical 3R on fold-frontier axes: three active pins on O20 hubs (MR117-2RS pair, 12.25 mm
 * stack) whose axes meet at GH, 0 passive DOF, no cuff slide (bench model docs/concepts/models/fold-sph3r.py =
 * _template.py build(): great-circle 12 x 3 Ti straps, link 2 over link 1 and the neck, K7 neck rigid to BOTTOM's bar).
 * Best config (rows/fold-sph3r.json best_params, CMA gate converged, 44.72 Bench(60,160) fast at q 0.98): J1
 * bvec(28.34, 65.40) fixed in the scapula, J3 wdir(94.33, -9.37) fixed in the humerus, arcs a1 83.51 / a2 62.90 deg,
 * branch sigma -1, fold margin 10 deg. The fold-frontier seeds did not survive CMA: every start walked back to J1 over
 * the acromion. Hubs at the model's fitted levels F 53 / 154 / 67 mm (hub 2 posterolateral and horizontal at 154 mm:
 * the measured limiter, 0 % in band); straps and the neck drawn at their fitted underside levels along the member.
 * Closed form (KIN.sph3r); fold frames (overhead) show red. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 28.338, el: 65.3972, a: [83.5065, 62.9048], w: [94.3254, -9.3721], branch: -1, margin_deg: 10,
              width: 12, faces: [53, 154, 67.1], hub_r: 10, stack: 12.25, cuff_at: 165,
              // fitted underside level (mm from GH) at 11 stations along each member (model prof at best_params, Bench(60,160) fast)
              lv1: [56.1, 56.1, 55.0, 60.0, 67.4, 88.2, 105.5, 122.8, 140.1, 154.0, 154.0],
              lv2: [157.2, 157.2, 154.5, 144.1, 130.3, 116.4, 102.6, 88.7, 80.0, 70.2, 70.2],
              lvn: [67.1, 67.1, 69.0, 71.5, 74.0, 78.0, 82.0, 84.5, 87.6, 91.5, 95.6] };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];             // BOTTOM's bar (body_pose humerus frame)
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  /** polyline through the unit nodes (great-circle legs), radius following the station levels lv over the arc length */
  function profPath(nodes, lv, dz) {
    const legs = [], out = [];
    for (let i = 0; i < nodes.length - 1; i++) legs.push(V.angle(nodes[i], nodes[i + 1]));
    const tot = legs.reduce((x, y) => x + y, 0) || 1; let acc = 0;
    nodes.slice(0, -1).forEach((a, i) => {
      const n = Math.max(4, Math.ceil(legs[i] / 3)), g = K.greatArc(a, nodes[i + 1], 1, 1, n);
      for (let j = i ? 1 : 0; j <= n; j++) {
        const f = (acc + legs[i] * j / n) / tot, s = f * (lv.length - 1), k = Math.min(lv.length - 2, Math.floor(s));
        out.push(V.scale(V.unit(g[j]), lv[k] + (lv[k + 1] - lv[k]) * (s - k) + dz));
      }
      acc += legs[i];
    });
    return out;
  }

  K.register({
    id: 'fold-sph3r',
    name: 'Spherical 3R on fold-frontier axes (CMA best)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach (the fold)';
      if (m < P.margin_deg) return `J2 within ${m.toFixed(0)} deg of its fold (model margin ${P.margin_deg})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack, R = P.hub_r;
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = profPath([f.p3, V.unit(bar0)], P.lvn, 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, MR117-2RS pair)', c: V.scale(f.p1, F[0]), axis: f.p1, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti)', pts: profPath([f.p1, f.p2], P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, floats at 154 mm)', c: V.scale(f.p2, F[1]), axis: f.p2, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1 and the neck)', pts: profPath([f.p2, f.p3], P.lv2, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20)', c: V.scale(f.p3, F[2]), axis: f.p3, r: R, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, member 3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

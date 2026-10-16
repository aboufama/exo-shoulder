/* raglan-routed-3r - plain spherical 3R (3 active pins on O20 hubs, 0 passive DOF, no cuff slide) whose links are
 * RAGLAN-ROUTED: a link need not run on the great circle between its hubs; it takes one planform turn at a waypoint
 * W = cos(d) slerp(h_a, h_b, t) + sin(d) n_ab (n_ab = unit(h_a x h_b)), FIXED IN THE LINK (one rigid 8 x 3 Ti strap,
 * constant section, two great-circle legs, a tangent-arc corner; no loft, no twist). Bench model
 * docs/concepts/models/raglan-routed-3r.py; best config (rows/raglan-routed-3r.json best_params, CMA converged, 42.72
 * fast, 50.06 frozen Bench(110,360) exact): J1 bvec(8.64, 81.58) fixed in the scapula (on top of the shoulder), J3
 * wdir(94.17, -0.85) fixed in the humerus (lateral arm), arcs a1 79.72 / a2 61.59 deg, branch sigma -1, every hub at the
 * near end of its GH line (e1 = e2 = e3 = +1). Link 1 turns 38.1 deg off its great circle at t 0.79 (bows out over the
 * posterior deltoid before turning in to hub 2), link 2 1.7 deg at t 0.55. All three axes pass through GH. Hubs at the
 * model's fitted levels F 53 / 128 / 68 mm (hub 2 floats at 128 mm: the measured limiter, 0 % in band); straps and the
 * K7 neck drawn at their fitted underside levels along the strap. Closed form (KIN.sph3r); fold frames show red. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { az: 8.6354, el: 81.5826, a: [79.7193, 61.5935], w: [94.1683, -0.8536], branch: -1, margin_deg: 10,
              route1: [0.789, 38.088], route2: [0.5504, -1.7406], width: 8, faces: [53, 128, 68], hub_r: 10, stack: 12.25, cuff_at: 165,
              // fitted underside level (mm from GH) at 11 stations along each member (model prof at best_params, Bench(60,160) fast)
              lv1: [56.1, 52.7, 53.0, 56.0, 60.0, 62.0, 66.0, 79.5, 103.8, 124.5, 128.0],
              lv2: [131.2, 131.2, 132.0, 118.1, 107.8, 93.9, 88.0, 84.0, 79.0, 71.2, 71.2],
              lvn: [68.0, 68.0, 69.5, 72.0, 75.5, 79.5, 82.5, 85.0, 88.5, 92.5, 97.5] };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];             // BOTTOM's bar (body_pose humerus frame)
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  const slerp = (a, b, t) => { const th = V.angle(a, b) * D2R, s = Math.sin(th) || 1e-9;
    return V.unit(V.add(V.scale(a, Math.sin((1 - t) * th) / s), V.scale(b, Math.sin(t * th) / s))); };
  /** the link's waypoint (model routed_strap): fixed in the link because both hubs are */
  function waypoint(a, b, route) {
    const g = slerp(V.unit(a), V.unit(b), route[0]), n = V.unit(V.cross(a, b)), d = route[1] * D2R;
    return V.unit(V.add(V.scale(g, Math.cos(d)), V.scale(n, Math.sin(d))));
  }
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
    id: 'raglan-routed-3r',
    name: 'Raglan-routed spherical 3R (link 1 bowed over the posterior deltoid)',
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
      const W1 = waypoint(f.p1, f.p2, P.route1), W2 = waypoint(f.p2, f.p3, P.route2);
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = profPath([f.p3, V.unit(bar0)], P.lvn, 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, MR117-2RS pair)', c: V.scale(f.p1, F[0]), axis: f.p1, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 Ti, raglan turn 38 deg)', pts: profPath([f.p1, W1, f.p2], P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, floats at 128 mm)', c: V.scale(f.p2, F[1]), axis: f.p2, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 Ti, over link 1 and the neck)', pts: profPath([f.p2, W2, f.p3], P.lv2, 1.5), r: 2.5 },
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

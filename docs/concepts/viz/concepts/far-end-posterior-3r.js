/* far-end-posterior-3r - KILLED after the coarse sweep (rows/far-end-posterior-3r.json: best honest 118.55 vs the
 * plain 3R control 51.33). Plain spherical 3R (3 active pins on O20 hubs, 0 passive DOF) on the fold-free POSTERIOR J1
 * line: J1 = bvec(-24, 4), a horizontal line pointing straight back from GH (slightly medial), J3 on the posterior arm
 * wdir(60, -78); the hub of each axis may sit at either end of its GH line and the links may take a raglan turn (the
 * raglan-routed-3r builder, docs/concepts/models/far-end-posterior-3r.py). Best honest config (best_params): arcs
 * a1 65 / a2 85 deg, branch sigma +1, every hub at the NEAR end (e = +1: the far ends lie in the torso / axilla /
 * neck), no route turn (d 0: great circles), q 0.9. Fold-free (margin >= 10.6 deg on every bench pose), but the hubs
 * and links stand far off the skin: fitted levels F 108 / 77 / 137 mm, links up to 140 mm, and link rays run through
 * the neck / chest in 10-20 % of closing poses (contact 0.28) - the measured reason it was killed. Hubs, straps and
 * the neck drawn at the model's fitted levels. Closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: -24.0, el: 4.0, a: [65.0, 85.0], w: [60.0, -78.0], branch: 1, margin_deg: 10, e: [1, 1, 1],
              width: 12, faces: [108, 77.2, 136.5], hub_r: 10, stack: 12.25, cuff_at: 165,
              // fitted underside level (mm from GH) at 11 stations along each member (model prof at best_params, Bench(60,160) fast)
              lv1: [111.2, 111.2, 104.2, 97.2, 98.2, 100.1, 97.1, 90.1, 80.1, 77.2, 77.2],
              lv2: [80.3, 80.3, 83.0, 69.1, 73.0, 81.1, 98.5, 115.8, 133.1, 140.0, 139.6],
              lvn: [136.5, 136.5, 129.6, 115.7, 113.0, 112.0, 109.0, 106.5, 103.0, 99.0, 93.5] };
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
    id: 'far-end-posterior-3r',
    name: 'Far-end posterior 3R (fold-free posterior J1 line; killed)',
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
        { kind: 'hub', role: 'active', name: 'J1 (O20, behind the shoulder at 108 mm)', c: V.scale(f.p1, F[0]), axis: f.p1, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti)', pts: profPath([f.p1, f.p2], P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20)', c: V.scale(f.p2, F[1]), axis: f.p2, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1 and the neck)', pts: profPath([f.p2, f.p3], P.lv2, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, posterior arm at 137 mm)', c: V.scale(f.p3, F[2]), axis: f.p3, r: R, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, member 3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

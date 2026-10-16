/* zc-frontier-3r - the ZERO-COMPLEXITY class (complexity 0: three active O20 pins whose axes meet at GH, three links,
 * nothing else) searched globally under the user's 2026-10-16 rulings: J1 on the back of the shoulder / acromion top,
 * O20 hubs at every joint, fold margin 5 deg (bench model docs/concepts/models/zc-frontier-3r.py, search
 * tools/zc_frontier.py, doc docs/concepts/zc-frontier-3r.md). Drawn at the search's best configuration (P below):
 * J1 axis bvec(az, el) fixed in the scapula, J3 axis wdir(wd, wa) fixed in the humerus, link arcs a1 / a2, J2 from the
 * two-circle closure on branch sigma (concept_kit.closure convention). Hubs O20 (r 10, 12.25 mm stack) at the model's
 * fitted levels F (Bench(60,160) fast fit of P); links 12 x 3 Ti straps on the great circles at their fitted
 * underside levels; member 3 = hub 3's plate + the K7 14 x 6 neck to BOTTOM's bar, then the bar to the cuff. inv3 = 1:
 * link 2 on hub 3's lower plate and member 3 on the cap plate bridging over it (the j3-neck-over stack); inv2 = 1:
 * link 2 on hub 2's lower plate, link 1 on top. 0 passive translations, 0 passive rotations. Closed form (KIN.sph3r);
 * the fold (J1-J3 angle outside the closure window) shows red - the class's measured limiter. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 95.8565, el: 65.2093, a: [37.6, 73.6], w: [84.8, -11.37], branch: -1, inv2: 0, inv3: 1,
              faces: [51, 60, 71], stack: 12.25, margin_deg: 5, cuff_at: 165,
              lv1: [54.2, 54.2, 54.2, 54.2, 50.4, 51.2, 52.3, 60.0, 60.0, 60.0, 60.0],
              lv2: [63.2, 63.2, 60.2, 59.9, 62.6, 64.0, 65.6, 67.6, 71.0, 71.0, 71.0],
              lvn: [74.2, 74.2, 75.5, 78.0, 79.6, 81.0, 83.2, 86.4, 88.6, 91.3, 94.6] };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  const lo = Math.abs(P.a[0] - P.a[1]), hi = Math.min(P.a[0] + P.a[1], 360 - P.a[0] - P.a[1]);
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];             // BOTTOM's bar (body_pose humerus frame)
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  /** polyline on the great circle u -> v whose radius follows the station levels lv (+ dz: strap thickness / 2) */
  function profArc(u, v, lv, dz) {
    const n = 24, out = [], g = K.greatArc(u, v, 1, 1, n);
    for (let i = 0; i <= n; i++) {
      const s = i / n * (lv.length - 1), j = Math.min(lv.length - 2, Math.floor(s)), r = lv[j] + (lv[j + 1] - lv[j]) * (s - j);
      out.push(V.scale(V.unit(g[i]), r + dz));
    }
    return out;
  }

  K.register({
    id: 'zc-frontier-3r',
    name: 'Zero-complexity 3R frontier (three O20 pins through GH, global seats)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return `J2 cannot close: the J1-J3 angle is outside [${lo.toFixed(0)}, ${hi.toFixed(0)}] deg (the fold)`;
      if (m < P.margin_deg) return `J2 within ${m.toFixed(0)} deg of its fold (margin ${P.margin_deg})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack;
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = profArc(f.p3, bar0, P.lvn, 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, MR117-2RS pair)', c: V.scale(f.p1, F[0]), axis: f.p1, r: 10, h },
        { kind: 'arc', role: 'link', name: P.inv2 ? 'link 1 (12 x 3 Ti, on hub 2\'s cap plate)' : 'link 1 (12 x 3 Ti)', pts: profArc(f.p1, f.p2, P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20)', c: V.scale(f.p2, F[1]), axis: f.p2, r: 10, h },
        { kind: 'arc', role: 'link', name: P.inv3 ? 'link 2 (12 x 3 Ti, on hub 3\'s lower plate)' : 'link 2 (12 x 3 Ti, over link 1 and the neck)', pts: profArc(f.p2, f.p3, P.lv2, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20)', c: V.scale(f.p3, F[2]), axis: f.p3, r: 10, h },
        { kind: 'arc', role: 'fixed-arm', name: P.inv3 ? 'neck (K7 14 x 6, member 3 on the cap plate, over link 2)' : 'neck (K7 14 x 6, member 3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

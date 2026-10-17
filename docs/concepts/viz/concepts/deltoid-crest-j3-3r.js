/* deltoid-crest-j3-3r - the deltoid-crest J3 spherical 3R re-measured at O20 / fold margin 5 (closing screen, round 14;
 * bench model docs/concepts/models/deltoid-crest-j3-3r.py = zc-frontier-3r's build restricted to the crest box, doc
 * docs/concepts/deltoid-crest-j3-3r.md). Drawn at the screen's best configuration (P below, Bench(60,160) fast fit):
 * J1 axis bvec(az, el) fixed in the scapula (acromion top), J3 axis wdir(wd, wa) fixed in the humerus ON THE DELTOID
 * CREST (wd >= 95), link arcs a1 / a2, J2 from the two-circle closure on branch sigma. Hubs O20 (r 10, 12.25 mm stack)
 * at the fitted levels F; links 12 x 3 Ti straps on the great circles at their fitted underside levels; member 3 =
 * hub 3's plate + the K7 14 x 6 neck to BOTTOM's bar. inv3 = 1: link 2 on hub 3's lower plate and member 3 on the cap
 * plate bridging over it; inv2 = 1: link 2 on hub 2's lower plate, link 1 on top. 0 passive translations, 0 passive
 * rotations, complexity 0. The fold (J1-J3 angle outside the window) shows red - with hub 2's level spread, the limiter. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 103.4879, el: 65.8246, a: [38.1218, 51.4912], w: [103.0802, -7.0294], branch: -1, inv2: 1, inv3: 1,
              faces: [50.0, 59.6, 62.0], stack: 12.25, margin_deg: 5, cuff_at: 165,
              // fitted underside level (mm from GH) at 11 stations along each strap (Bench(60,160) fast fit of the screen's best, gap 37.90)
              lv1: [53.1, 53.1, 56.4, 53.1, 58.4, 56.2, 63.6, 63.6, 62.7, 62.7, 62.7],
              lv2: [59.6, 59.6, 59.6, 56.1, 55.0, 56.6, 58.0, 58.5, 62.0, 62.0, 62.0],
              lvn: [65.2, 65.2, 66.0, 67.0, 66.0, 70.0, 75.0, 74.1, 81.0, 90.5, 88.0] };
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
    id: 'deltoid-crest-j3-3r',
    name: 'Deltoid-crest J3 3R (O20, margin 5; three pins through GH, J3 on the deltoid crest)',
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

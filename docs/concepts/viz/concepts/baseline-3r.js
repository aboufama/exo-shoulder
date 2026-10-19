/* baseline-3r - the champion spherical 3R (r20 s1414 #4; tools/concept_baseline.py CHAMP, band_impl.Band.chain N = 3).
 * Base axis b(az, el) fixed in the scapula, last axis W(w) fixed in the humerus, J2 from the two-circle closure on
 * branch -1. Hubs on the real joint axes at the judged face distances (band_cad inputs r20_n3_s1414_4: faces 52.8 /
 * 93.2 mm, J3 plate on the arm 71.8, link 2 over it at 78.5), links on the great circles between the axes, the arm-end
 * neck 25 deg toward the humerus axis, then the user's cuff. Closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
              w: [86.32769021001913, 21.829657347343378], branch: -1, faces: [52.82, 93.18, 71.85, 78.50],
              hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165, sing_deg: 10 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);

  K.register({
    id: 'baseline-3r',
    name: 'Spherical 3R (champion)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.sing_deg) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack;
      const harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[2] + 1);
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: f.p1, v: f.p2, r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', u: f.p2, v: f.p3, r0: F[1] + 9, r1: F[3] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(f.p3, F[2]), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: f.p3, v: nk, r0: F[2] + 1, r1: F[2] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

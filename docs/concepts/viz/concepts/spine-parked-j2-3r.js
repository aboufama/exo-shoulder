/* spine-parked-j2-3r - zero-passive spherical 3R at the leader's seats with J2 parked over the posterior acromion /
 * scapular spine (bench model docs/concepts/models/spine-parked-j2-3r.py; VERIFIED 34.29 on Bench(110,360) exact,
 * docs/concepts/spine-parked-j2-3r.md). Best config k7008 (rows/spine-parked-j2-3r.json): J1 axis bvec(104.41, 67.05)
 * fixed in the scapula, J3 axis wdir(82.06, -14.09) fixed in the humerus, link arcs a1 37.61 / a2 73.63 deg, J2 from
 * the two-circle closure on branch sigma -1 (same convention as concept_kit.closure), fold margin 10 deg. All three
 * axes pass through GH. Hubs: J1 O20 (r 10), J2 and J3 slim O15 (r 7.5, the same MR117-2RS pair in a 2 mm Ti wall),
 * 12.25 mm stacks at the verifier's fitted levels F 50 / 58 / 72 mm. Links 12 x 3 Ti straps on the great circles; link 2
 * rides over link 1 and the neck. Member 3 = hub 3's arm-end plate + the K7 14 x 6 neck to the start of BOTTOM's bar
 * (body_pose humerus frame, BAR0_H = 67.5 WB + 40 DB), BOTTOM's bar down to the cuff. 0 passive translations, 0 passive
 * rotations. Closed form (KIN.sph3r); the fold (J1-J3 angle outside [43, 104] deg) shows red - that is the design's
 * measured limiter (overhead / across-the-body reach). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 104.41, el: 67.05, a: [37.61, 73.63], w: [82.06, -14.09], branch: -1, faces: [50, 58, 72],
              hub_r: [10, 7.5, 7.5], stack: 12.25, margin_deg: 10, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];             // BOTTOM's bar (body_pose humerus frame)
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));

  K.register({
    id: 'spine-parked-j2-3r',
    name: 'Spherical 3R, J2 parked over the scapular spine (slim O15 J2/J3)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the J1-J3 angle is outside [43, 104] deg (the fold)';
      if (m < P.margin_deg) return `J2 within ${m.toFixed(0)} deg of its fold (model margin ${P.margin_deg})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack, R = P.hub_r;
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(bar0, harm)), 47);
      const neckR = V.norm(bar0), barEnd = V.madd(bar0, barDn, Math.max(20, V.dot(V.sub(cuffTop, bar0), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, MR117-2RS pair)', c: V.scale(f.p1, F[0]), axis: f.p1, r: R[0], h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti)', u: f.p1, v: f.p2, r0: F[0] + 3.15, r1: F[1], r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (slim O15, over the scapular spine)', c: V.scale(f.p2, F[1]), axis: f.p2, r: R[1], h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1 and the neck)', u: f.p2, v: f.p3, r0: F[1] + 3.15, r1: F[2] + 3.15, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (slim O15)', c: V.scale(f.p3, F[2]), axis: f.p3, r: R[2], h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, member 3)', u: f.p3, v: bar0, r0: F[2], r1: neckR, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: bar0, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

/* open-ring-joints - the spherical 3R with every joint built as an OPEN-CENTRE thin-section ring around its pole
 * (catalogue open-ring-joints, ideated; marked a duplicate of annular-ring-3r, whose bore variant measured worse than the
 * O20 hub). Same kinematics as the champion 3R (KIN.sph3r, closed form, every axis through GH, 0 passive): J1 ring
 * circles the acromion summit, J2 ring sits over the posterior-lateral cap, J3 ring (arm-fixed axis) circles the most
 * bulging point of the deltoid cap. Each ring per the catalogue: a four-point-contact thin-section bearing (wire-race or
 * KAA type) of mean radius r_m 14-24 mm (drawn 18), 5 x 5 mm section; the INNER race is the lower member and the OUTER
 * race the upper member, both in one ~9 mm layer (no pin, no dome cap); links are short straps between ring rims. Ring
 * levels are the champion's judged faces (52.8 / 93.2 / 71.8 mm), schematic: no bench model or sweep exists. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
              w: [86.32769021001913, 21.829657347343378], branch: -1, margin: 10,
              rm: 18, sec: 5, stack: 9, levels: [52.8, 93.2, 71.8], lug: 2, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  const rIn = P.rm - P.sec / 2, rOut = P.rm + P.sec / 2, rim = rOut + P.sec / 2 + P.lug;
  // one open ring about axis k at level z: inner race (lower member) and outer race (upper member) side by side
  const ring = (k, z, ref, roles, name) => [
    { kind: 'ring', role: roles[0], name: `${name} inner race (lower member)`, c: V.scale(k, z + P.stack / 2), axis: k, ref, r: rIn, t: 2.4 },
    { kind: 'ring', role: roles[1], name: `${name} outer race (upper member)`, c: V.scale(k, z + P.stack / 2), axis: k, ref, r: rOut, t: 2.4 }];
  const root = (k, z, toward, dz, R) => V.madd(V.scale(k, z + dz), V.unit(V.reject(toward, k)), R);
  const arc = (role, name, a, b) => ({ kind: 'arc', role, name, u: a, v: b, r0: V.norm(a), r1: V.norm(b), r: 2.5 });

  K.register({
    id: 'open-ring-joints',
    name: 'Open-centre ring joints (3R, rings around the poles)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 ring', 'J2 ring', 'J3 ring'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), Z = P.levels, harm = ctx.armAxis, s1 = ctx.attach.scapDir([1, 0, 0]);
      const r1 = root(f.p1, Z[0], f.p2, P.stack - 1, rim), r2a = root(f.p2, Z[1], f.p1, 1, rIn - 4), r2b = root(f.p2, Z[1], f.p3, P.stack - 1, rim);
      const r3 = root(f.p3, Z[2], f.p2, P.stack - 1, rim), r3arm = root(f.p3, Z[2], harm, 1, rIn - 4);
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(r3arm, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (inner race 1 mount on the handler)', c: V.madd(V.scale(f.p1, Z[0] - 2), V.unit(V.reject(s1, f.p1)), -rim - 6), z: f.p1, x: s1, size: [28, 24], t: 3 },
        ...ring(f.p1, Z[0], s1, ['fixed-scapula', 'active'], 'J1 ring'),
        arc('link', 'link 1 (strap, ring 1 rim -> ring 2)', r1, r2a),
        ...ring(f.p2, Z[1], f.p1, ['link', 'active'], 'J2 ring'),
        arc('link', 'link 2 (strap, ring 2 rim -> ring 3 rim)', r2b, r3),
        ...ring(f.p3, Z[2], f.p2, ['fixed-arm', 'active'], 'J3 ring'),
        { kind: 'link', role: 'fixed-arm', name: 'arm-end stub to the cuff / BOTTOM', a: r3arm, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

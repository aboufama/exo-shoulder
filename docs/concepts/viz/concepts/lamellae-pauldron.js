/* lamellae-pauldron - spherical 3R where every joint is a large open thin-section ring and every link is a dished Ti
 * lame (1.5-2 mm) that nests over its neighbour like the lames of a pauldron: around each ring the two members that
 * turn about it overlap as SURFACES OF REVOLUTION about that ring's axis (lower dish + 2.5 mm, so they can never
 * collide), and between rings the lames are 20 mm ribbons on the great circle (catalogue entry; not modelled yet).
 * Kinematics of back-anchored-ring-3r with J1 on the dome pole p* = S-local (lat 66, lon -68), J3 humerus-fixed through
 * the lateral arm strip (arm point s 100, th 20 posterior, rho 60: 31 deg off the humerus axis), a12 70, a23 100,
 * branch +1 (J2 over the front-top of the shoulder at rest; fold margin >= 41 deg over the loop). Ring pitch radii
 * 30 / 26 / 24 mm, overlap zones 15 mm wide, levels 62 / 78 / 120 mm (dome skin 39-68; J3 where its axis meets the arm
 * skin). Closed form (KIN.sph3r), 3 active, 0 passive: the lames' sliding overlap adds no DOF. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { lat1: 66, lon1: -68, s3: 100, th3: 20, rho3: 60, a12: 70, a23: 100, br: 1, margin: 10,
              pitch: [30, 26, 24], level: [62, 78, 120], overlap: 15, gap: 2.5, lame_w: 20, cuff_at: 165 };
  const sdir = (lat, lon) => [Math.cos(lat * D2R) * Math.sin(lon * D2R), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.cos(lon * D2R)];
  // J3 axis: rig arm point (s, th, rho) -> band humerus frame (ctx.H = Hb rest)
  const a = V.unit(K.BODY.elbow), RH = K.BODY.rest_humerus, z = V.unit(V.reject(M.col(RH, 2), a)), y = V.cross(a, z);
  const j3 = M.mulv(M.T(RH), V.unit(V.madd(V.scale(a, P.s3), V.add(V.scale(z, Math.cos(P.th3 * D2R)), V.scale(y, Math.sin(P.th3 * D2R))), P.rho3)));
  const C = K.sph3r(sdir(P.lat1, P.lon1), j3, P.a12, P.a23, P.br);

  const races = (k, zl, p, ref, roles, name) => [0, 1].map(i => ({ kind: 'ring', role: roles[i], name: `${name} ${i ? 'upper' : 'lower'} race`,
    c: V.scale(k, zl + 2 + 4 * i), axis: k, ref, r: p, t: 2.2 }));
  // revolved overlap dish about axis k: two thin rings on the sphere of radius R at cap angles inside the zone
  const dish = (k, R, p, ref, role, name) => [1, 2].map(j => {
    const th = (p + 6 + P.overlap * j / 3) / R;
    return { kind: 'ring', role, name: `${name} (revolved dish)`, c: V.scale(k, R * Math.cos(th)), axis: k, ref, r: R * Math.sin(th), t: 1.1 };
  });
  // lame body: 20 mm ribbon between two rim points, drawn as its centre line and both edges
  function lame(A, B, role, name) {
    const n = V.unit(V.cross(A, B)), h = P.lame_w / 2;
    return [-h, 0, h].map(o => {
      const a2 = V.madd(A, n, o), b2 = V.madd(B, n, o);
      return { kind: 'arc', role, name: `${name}${o ? ' edge' : ''}`, u: a2, v: b2, r0: V.norm(a2), r1: V.norm(b2), r: o ? 1.2 : 1.8 };
    });
  }
  const rimPt = (k, zl, toward, r) => V.madd(V.scale(k, zl), V.unit(V.reject(toward, k)), r);

  K.register({
    id: 'lamellae-pauldron',
    name: 'Revolved-lamellae pauldron',
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
      const f = C.fk(q, ctx), L = P.level, R = P.pitch, harm = ctx.armAxis, s1 = ctx.attach.scapDir([1, 0, 0]);
      const zo = j => R[j] + 6 + P.overlap;                                   // outer edge of overlap zone j (mm)
      const e1 = rimPt(f.p1, L[0] + P.gap + 1, f.p2, zo(0)), e2a = rimPt(f.p2, L[1] - 1, f.p1, zo(1));
      const e2b = rimPt(f.p2, L[1] + P.gap - 1, f.p3, zo(1)), e3 = rimPt(f.p3, L[2] + P.gap, f.p2, zo(2));
      const st3 = rimPt(f.p3, L[2], harm, zo(2)), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(st3, harm)), 47);
      return [
        ...races(f.p1, L[0], R[0], s1, ['fixed-scapula', 'active'], 'J1 ring'),
        ...dish(f.p1, L[0], R[0], s1, 'fixed-scapula', 'base lame under J1'),
        ...dish(f.p1, L[0] + P.gap + 2, R[0], s1, 'link', 'lame 1 over the base'),
        ...lame(e1, e2a, 'link', 'lame 1'),
        ...races(f.p2, L[1], R[1], f.p1, ['link', 'active'], 'J2 ring'),
        ...dish(f.p2, L[1], R[1], f.p1, 'link', 'lame 1 under J2'),
        ...dish(f.p2, L[1] + P.gap + 2, R[1], f.p1, 'link', 'lame 2 over lame 1'),
        ...lame(e2b, e3, 'link', 'lame 2'),
        ...races(f.p3, L[2], R[2], f.p2, ['fixed-arm', 'active'], 'J3 ring'),
        ...dish(f.p3, L[2], R[2], f.p2, 'fixed-arm', 'arm lame under J3'),
        ...dish(f.p3, L[2] + P.gap + 2, R[2], f.p2, 'link', 'lame 2 over the arm lame'),
        { kind: 'link', role: 'fixed-arm', name: 'arm lame to the cuff', a: st3, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

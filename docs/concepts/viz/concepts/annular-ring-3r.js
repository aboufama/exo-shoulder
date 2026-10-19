/* annular-ring-3r - the champion's spherical 3R with every revolute realised as an open-bore thin-section ring
 * (Reali-Slim KAA type, housed 9 mm radial x 8 mm stack) coaxial with its joint axis through GH: the skin dome under
 * each axis pierce point is meant to rise into the bore instead of lifting a solid hub (docs/concepts/annular-ring-3r.md,
 * models/annular-ring-3r.py). Shown: the spec's "rings at all three joints" at the smallest bore (sweeps k13, bore
 * r 12.7, fitted levels 58 / 111.8 / 68 mm from GH). Lower race housing = proximal member, upper race (+4) = distal;
 * at J3 the lower race is the arm side. Straps 12 x 3 leave the race rims through a 2 mm lug. Measured verdict: the
 * bore loses to the O20 hub at every joint (gap 91.6 vs 65.1 for its hub twin); refuted. Closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
              w: [86.32769021001913, 21.829657347343378], branch: -1, margin: 10,
              bore: 12.7, ring_w: 9, stack: 8, levels: [58, 111.8, 68], lug: 2, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  const pitch = P.bore + P.ring_w / 2, rim = P.bore + P.ring_w + P.lug;      // race centre radius, strap root radius

  // one ring = two stacked races about axis k at level z: lower [z, z+4] (proximal), upper [z+4, z+8] (distal)
  const races = (k, z, ref, roles, name) => [0, 1].map(i => ({ kind: 'ring', role: roles[i], name: `${name} ${i ? 'upper' : 'lower'} race`,
    c: V.scale(k, z + 2 + 4 * i), axis: k, ref, r: pitch, t: 2.1 }));
  // strap root on a ring: the rim point toward direction toward, at race level dz above the ring's lower face
  const root = (k, z, toward, dz) => V.madd(V.scale(k, z + dz), V.unit(V.reject(toward, k)), rim);
  const arc = (role, name, a, b) => ({ kind: 'arc', role, name, u: a, v: b, r0: V.norm(a), r1: V.norm(b), r: 2.5 });

  K.register({
    id: 'annular-ring-3r',
    name: 'Annular-ring 3R (open-bore ring at every joint)',
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
      const f = C.fk(q, ctx), Z = P.levels, harm = ctx.armAxis;
      const s1 = ctx.attach.scapDir([1, 0, 0]);
      const r1 = root(f.p1, Z[0], f.p2, 6), r2a = root(f.p2, Z[1], f.p1, 2), r2b = root(f.p2, Z[1], f.p3, 6);
      const r3 = root(f.p3, Z[2], f.p2, 6), r3arm = root(f.p3, Z[2], harm, 2);
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(r3arm, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (ring 1 stator mount)', c: V.madd(V.scale(f.p1, Z[0] - 2), V.unit(V.reject(s1, f.p1)), -pitch - 8), z: f.p1, x: s1, size: [30, 26], t: 3 },
        ...races(f.p1, Z[0], s1, ['fixed-scapula', 'active'], 'J1'),
        arc('link', 'link 1 (ring 1 rim to ring 2 rim)', r1, r2a),
        ...races(f.p2, Z[1], f.p1, ['link', 'active'], 'J2'),
        arc('link', 'link 2 (ring 2 rim to ring 3 rim)', r2b, r3),
        ...races(f.p3, Z[2], f.p2, ['fixed-arm', 'active'], 'J3'),
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM stub to the cuff', a: r3arm, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

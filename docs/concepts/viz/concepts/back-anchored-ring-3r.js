/* back-anchored-ring-3r - spherical 3R that leaves the top of the shoulder bare: J1 is a thin-section ring (4.76 section,
 * pitch r 24.6, housed 9 x 8, rotor at +4.8) seated on the back over the infraspinous fossa, axis u1 = S-local (lat -10,
 * lon -120) through GH, 110 mm out; J2 an O20 hub placed by the two-cone closure (a12 = a23 = 90, branch +1) at the
 * posterolateral acromion corner; J3 a second ring on the arm, humerus-fixed axis 50 deg off the humerus axis, 30 deg
 * posterior of lateral, 75 mm out (the model's arm site; the spec's d3 26.6 stands the ring on edge). Straps 14 x 5.5
 * leave the rings from a 4.5 mm lug at the rotor level; a bracket joins the J3 stator to the cuff / BOTTOM.
 * docs/concepts/back-anchored-ring-3r.md, models/back-anchored-ring-3r.py (PARAMS + the k18 arm site, rings kept).
 * Measured: dead - link 1 floats 32 mm (median) and goes into the body overhead; best honest gap 116.3 (O20 hubs).
 * Closed form (KIN.sph3r), 3 active, 0 passive. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { lat1: -10, lon1: -120, R1: 110, p1: 24.6, a12: 90, a23: 90, d3: 50, th3: 30, R3: 75, p3: 24.6, br: 1,
              margin: 10, F2: 72, hub_r: 10, stack: 12.25, ring_w: 9, lug: 4.5, up: 4.8, cuff_at: 165 };
  const sdir = (lat, lon) => [Math.cos(lat * D2R) * Math.sin(lon * D2R), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.cos(lon * D2R)];
  // J3 axis in the rig arm frame (a = humerus axis, z lateral, y posterior; models/back-anchored-ring-3r.py arm_dir),
  // carried into the band humerus frame of ctx.H (H = Hb rest)
  const a = V.unit(K.BODY.elbow), RH = K.BODY.rest_humerus, z = V.unit(V.reject(M.col(RH, 2), a)), y = V.cross(a, z);
  const j3mesh = V.add(V.scale(a, Math.cos(P.d3 * D2R)), V.scale(V.add(V.scale(z, Math.cos(P.th3 * D2R)), V.scale(y, Math.sin(P.th3 * D2R))), Math.sin(P.d3 * D2R)));
  const C = K.sph3r(sdir(P.lat1, P.lon1), M.mulv(M.T(RH), j3mesh), P.a12, P.a23, P.br);
  const rimR = p => p + P.ring_w / 2 + P.lug;
  const rimPt = (k, zl, toward, r) => V.madd(V.scale(k, zl), V.unit(V.reject(toward, k)), r);
  const races = (k, zl, p, ref, roles, name) => [0, 1].map(i => ({ kind: 'ring', role: roles[i], name: `${name} ${i ? 'rotor' : 'stator'} race`,
    c: V.scale(k, zl + 2 + P.up * i), axis: k, ref, r: p, t: 2.3 }));

  K.register({
    id: 'back-anchored-ring-3r',
    name: 'Back-anchored ring-ended 3R',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 back ring', 'J2 hub', 'J3 arm ring'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), harm = ctx.armAxis, s1 = ctx.attach.scapDir([0, 1, 0]);
      const r1 = rimPt(f.p1, P.R1 + P.up + 2, f.p2, rimR(P.p1)), r3 = rimPt(f.p3, P.R3 + P.up + 2, f.p2, rimR(P.p3));
      const h2lo = V.scale(f.p2, P.F2 + 1.5), h2hi = V.scale(f.p2, P.F2 + P.stack + 1);
      const st3 = rimPt(f.p3, P.R3 + 2, harm, rimR(P.p3));
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(st3, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'scapula handler plate (infraspinous fossa)', c: V.madd(V.scale(f.p1, P.R1 - 3), V.unit(V.reject(s1, f.p1)), 0),
          z: f.p1, x: s1, size: [70, 56], t: 3 },
        ...races(f.p1, P.R1, P.p1, s1, ['fixed-scapula', 'active'], 'J1 ring'),
        { kind: 'arc', role: 'link', name: 'link 1 (back ring to J2)', u: r1, v: h2lo, r0: V.norm(r1), r1: V.norm(h2lo), r: 3 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.p2, P.F2), axis: f.p2, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'link 2 (J2 to the arm ring)', u: h2hi, v: r3, r0: V.norm(h2hi), r1: V.norm(r3), r: 3 },
        ...races(f.p3, P.R3, P.p3, f.p2, ['fixed-arm', 'active'], 'J3 ring'),
        { kind: 'link', role: 'fixed-arm', name: 'bracket: J3 stator to BOTTOM / cuff', a: st3, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

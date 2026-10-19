/* crown-ring-3r - spherical 3R whose J1 is one large open thin-section ring (Reali-Slim KA025XP0, pitch r 34.9, land
 * pitch +-8, 9 mm stack) lying flat on the shoulder crown, axis a1 through GH at c* = bvec(22.8, 65.6) (the direction
 * the humerus never comes within 82 deg of), so the bony crown sits inside the bore like an eyelet. Stator on the
 * scapula handler, rotor = link 1, which leaves from the rotor's pitch circle; J2 and J3 are KAA15-type donut hubs
 * (O38 x O47.6) on the champion's closure angles and arm axis (docs/concepts/crown-ring-3r.md, models/crown-ring-3r.py
 * PARAMS). Ring level 60 mm = the spec's seat (2-9 mm over the 48-55 mm crown skin); the bench fit measured 91-107 mm
 * (the trapezius rises into the land medially, sweeps k16 / k28), and the O20-hub control beat every ring (64.3 vs
 * 83.4). Hub faces 93 / 72 mm (the champion's). Closed form (KIN.sph3r), 3 active, 0 passive. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V;
  const P = { az1: 22.8, el1: 65.6, p1: 34.9, land: 8, stack: 9, a12: 76.9, a23: 66.75, wd: 86.33, wa: 21.83, sigma: -1,
              margin: 10, F1: 60, donut: 21.4, faces: [93, 72], cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az1, P.el1), K.wdir(P.wd, P.wa), P.a12, P.a23, P.sigma);
  const ring = (role, name, k, z, r, t, ref) => ({ kind: 'ring', role, name, c: V.scale(k, z), axis: k, ref, r, t });
  const rimPt = (k, z, toward, r) => V.madd(V.scale(k, z), V.unit(V.reject(toward, k)), r);

  K.register({
    id: 'crown-ring-3r',
    name: 'Crown ring 3R (J1 an open ring on the crown)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 crown ring', 'J2 donut', 'J3 donut'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, harm = ctx.armAxis, s1 = ctx.attach.scapDir([1, 0, 0]);
      const top = P.F1 + P.stack, root1 = rimPt(f.p1, top, f.p2, P.p1);          // link 1 bolted on the rotor, pitch circle
      const j2lo = rimPt(f.p2, F[0], f.p1, P.donut + 4), j2hi = rimPt(f.p2, F[0] + 5, f.p3, P.donut + 4);
      const j3hi = rimPt(f.p3, F[1] + 5, f.p2, P.donut + 4), j3arm = rimPt(f.p3, F[1], harm, P.donut + 4);
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(j3arm, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'handler boss (ring stator mount)', c: rimPt(f.p1, P.F1 - 2, V.scale(f.p2, -1), P.p1 + 10), z: f.p1, x: s1, size: [26, 22], t: 3 },
        ring('fixed-scapula', 'J1 ring stator (on the handler)', f.p1, P.F1 + 2.25, P.p1, 4, s1),
        ring('active', 'J1 ring rotor (link 1)', f.p1, P.F1 + 6.75, P.p1, 4, s1),
        { kind: 'arc', role: 'link', name: 'link 1 (rotor flange to J2)', u: root1, v: j2lo, r0: V.norm(root1), r1: V.norm(j2lo), r: 2.5 },
        ring('link', 'J2 donut lower race (link 1)', f.p2, F[0] + 1.2, P.donut, 2.4, f.p1),
        ring('active', 'J2 donut upper race (link 2)', f.p2, F[0] + 3.6, P.donut, 2.4, f.p1),
        { kind: 'arc', role: 'link', name: 'link 2 (over the deltoid)', u: j2hi, v: j3hi, r0: V.norm(j2hi), r1: V.norm(j3hi), r: 2.5 },
        ring('active', 'J3 donut upper race (link 2)', f.p3, F[1] + 3.6, P.donut, 2.4, f.p2),
        ring('fixed-arm', 'J3 donut lower race (arm saddle)', f.p3, F[1] + 1.2, P.donut, 2.4, f.p2),
        { kind: 'link', role: 'fixed-arm', name: 'neck to BOTTOM / cuff', a: j3arm, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

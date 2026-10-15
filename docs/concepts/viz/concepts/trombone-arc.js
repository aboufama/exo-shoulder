/* trombone-arc - one curved Ti band on the arm-side member slides through a swivelling guide on top of the scapula
 * (docs/concepts/trombone-arc.md, models/trombone-arc.py; DEAD, best honest k143, gap 88.29). A spherical 3R in
 * disguise: J1 = O20 hub on b = bvec(45, 30) (scapula), the guide rides an L1 strap 22 deg across the band (goff);
 * J2 = rotation about p2 (two-cone closure, A1 = A2 = 90, branch -1) realised by the band, a circle about p2 at polar
 * A1 + goff, sliding through the guide (no metal at p2); J3 = O20 hub on W = wdir(86.33, 21.83) (humerus), reached
 * from the band's arm-side end by a connector strap. Telescoping 2-stage arc (tele 1): sleeve A slides through the
 * guide and band B slides in A; A turns half of J2 (2:1 cable, a determined coordinate, not a DOF), so the tail past
 * the guide is halved. Band ends phi 18.7 .. 148.7 deg (L2 frame: e2 toward W); sleeve and band at R_a 110.6 mm (they
 * clear the highest trunk skin they sweep: the measured limiter), the guide a ~50 mm pedestal from its 60 mm skin face.
 * J2 value = guide azimuth on the band. 3 active, 0 passive; closed form (KIN.sph3r). Hub faces 55 / 72 schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, D2R = K.D2R;
  const P = { az: 45, el: 30, A1: 90, A2: 90, wd: 86.33, wa: 21.83, sigma: -1, margin: 5, phi_lo: 18.69, phi_hi: 148.67,
              Rn: 106, Ra: 110.6, goff: 22, guide_L: 30, guide_W: 22, guide_face: 60, width: 10, faces: [55, 72],
              hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.wd, P.wa), P.A1, P.A2, P.sigma);
  const hl = P.guide_L / 2 / (P.Rn * Math.sin(P.A1 * D2R)) * K.R2D, g0 = P.phi_lo + hl + 1, g1 = P.phi_hi - hl - 1;
  const Ab = (P.A1 + P.goff) * D2R, hiB = (g0 + g1) / 2 + hl - 1;
  function frame(q, ctx) {
    const f = C.fk(q, ctx), e2 = V.unit(V.reject(f.p3, f.p2)), e3 = V.cross(f.p2, e2);
    const phi = Math.atan2(V.dot(f.p1, e3), V.dot(f.p1, e2)) * K.R2D;                 // J2 value: guide azimuth on the band
    const u = V.unit(V.reject(f.p1, f.p2)), g = V.add(V.scale(f.p2, Math.cos(Ab)), V.scale(u, Math.sin(Ab)));   // guide dir (L1)
    return Object.assign(f, { e2, e3, phi, g });
  }
  const onBand = (f, az, R) => V.scale(V.add(V.scale(f.p2, Math.cos(Ab)), V.scale(V.add(V.scale(f.e2, Math.cos(az * D2R)), V.scale(f.e3, Math.sin(az * D2R))), Math.sin(Ab))), R);

  K.register({
    id: 'trombone-arc',
    name: 'Trombone arc (band through a swivel guide)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 swivel hub', 'J2 (band through the guide)', 'J3 hub'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const phi = frame(q, ctx).phi;
      if (phi < g0 || phi > g1) return `guide off the band end (azimuth ${phi.toFixed(0)}, band holds ${g0.toFixed(0)}..${g1.toFixed(0)})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = frame(q, ctx), F = P.faces, h = P.stack, Ra = P.Ra;
      const phM = (Math.min(g1, Math.max(g0, f.phi)) + g1) / 2;                       // sleeve A: half of J2 (2:1)
      const t = V.unit(V.cross(f.p2, f.g)), m = V.unit(V.reject(f.p2, f.g));
      const rail = (name, R, a0, a1, r) => ({ kind: 'rail', role: 'link', name, c: V.scale(f.p2, R * Math.cos(Ab)), axis: f.p2, ref: f.e2,
        rho: R * Math.sin(Ab), a0, a1, r });
      const cLo = onBand(f, P.phi_lo, Ra + 2.5), harm = ctx.armAxis, ng = P.neck_deg * D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[1] + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 swivel hub', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'guide arm (L1)', u: f.p1, v: f.g, r0: F[0] + h + 1, r1: P.guide_face, r: 2.5 },
        { kind: 'link', role: 'link', name: 'guide pedestal (L1)', a: V.scale(f.g, P.guide_face), b: V.scale(f.g, Ra - 6), r: 4 },
        { kind: 'carriage', role: 'active', name: 'J2 guide (needle rollers)', c: V.scale(f.g, Ra + 1), x: t, z: f.g, size: [P.guide_L, P.guide_W, 9] },
        rail('sleeve A (half of J2, 2:1)', Ra + 1, phM - (g1 - g0) / 2 - hl - 1, phM + hl + 1, 4),
        rail('band B (L2)', Ra + 2.5, P.phi_lo, hiB, 2.4),
        { kind: 'arc', role: 'link', name: 'connector (band end to J3)', pts: K.greatArc(cLo, V.scale(f.p3, F[1] + h + 1), Ra + 2.5, F[1] + h + 1), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(f.p3, F[1]), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: f.p3, v: nk, r0: F[1] + 1, r1: F[1] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

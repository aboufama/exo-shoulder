/* clavicular-front-route - spherical 3R entered from the FRONT: J1 on the acromio-clavicular front-top edge, reached by
 * a scapula-fixed bridge strap from the handler over the acromion top; short links over the anterior shoulder; J3 on
 * the anterolateral upper-arm strip, neck down the strip to BOTTOM (docs/concepts/clavicular-front-route.md,
 * models/clavicular-front-route.py). Best honest sweep entry (sweeps/clavicular-front-route.json k368, gap 68.26):
 * J1 sdir(66.3, -105.5), a12 83.4, a23 73.8, J3 armpt(10.2, -34.1, 76) (body_pose humerus frame), branch -1, fold
 * margin 7.3. 3 ACTIVE, 0 PASSIVE; closed form (KIN.sph3r). Hub faces are schematic (the kit fits them per design). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { j1lat: 66.3, j1lon: -105.5, a12: 83.4, a23: 73.8, s3: 10.2, th3: -34.1, r3: 76.0, sigma: -1, margin: 7.3,
              br: [[45, 90], [65, 20]], faces: [52, 74, 62], hub_r: 10, stack: 12.25, r_env: 50, cuff_at: 165 };
  const E_ = V.unit([-0.023, -0.986, 0.164]), L_ = [0.004, 0.164, 0.986], B_ = [-1.0, 0.023, 0.0];
  const sdir = (lat, lon) => [-Math.cos(lat * D) * Math.sin(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.cos(lon * D)];
  const armpt = (s, th, r) => V.add(V.scale(E_, s), V.scale(V.add(V.scale(L_, Math.cos(th * D)), V.scale(B_, Math.sin(th * D))), r));
  // body_pose humerus frame Hb = H rest^T: an arm direction d there is rest^T d in the band humerus frame
  const toBand = d => M.mulv(M.T(K.BODY.rest_humerus), d);
  const C = K.sph3r(sdir(P.j1lat, P.j1lon), toBand(V.unit(armpt(P.s3, P.th3, P.r3))), P.a12, P.a23, P.sigma);
  const armP = (ctx, s, th, r) => M.mulv(ctx.Hb, armpt(s, th, r));

  K.register({
    id: 'clavicular-front-route',
    name: 'Front route (J1 on the AC front)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack, S = d => ctx.attach.scapDir(d);
      const b0 = S(sdir(...P.br[0])), bw = S(sdir(...P.br[1]));
      const nA = armP(ctx, 65, -30, P.r_env + 4), nB = armP(ctx, 65, 0, P.r_env + 4), harm = ctx.armAxis;
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(nB, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'handler mount', c: V.scale(b0, 58), z: b0, x: S([0, 0, 1]), size: [30, 24], t: 3 },
        { kind: 'arc', role: 'fixed-scapula', name: 'bridge over the acromion (a)', u: b0, v: bw, r0: 60, r1: 58, r: 3, w: 14 },
        { kind: 'arc', role: 'fixed-scapula', name: 'bridge to the front seat (b)', u: bw, v: f.p1, r0: 58, r1: F[0] - 3, r: 3, w: 14 },
        { kind: 'hub', role: 'active', name: 'J1 (AC front-top)', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: f.p1, v: f.p2, r0: F[0] + h + 1, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', u: f.p2, v: f.p3, r0: F[1] + 9, r1: F[2] + h, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (anterolateral arm)', c: V.scale(f.p3, F[2]), axis: f.p3, r: P.hub_r, h },
        { kind: 'link', role: 'fixed-arm', name: 'neck down the anterolateral strip', a: V.scale(f.p3, F[2] + 2), b: nA, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to BOTTOM\'s top', a: nA, b: nB, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to cuff', a: nB, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

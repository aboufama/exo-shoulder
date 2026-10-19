/* posterior-max-margin-cardan - a spherical 3R wrapped BEHIND the shoulder, axes placed for the largest singularity
 * margin over the workspace (docs/concepts/posterior-max-margin-cardan.md, models/posterior-max-margin-cardan.py;
 * verdict refuted). J1 low on the back of the scapula (b = bvec(-28, -19): posterior-inferior-medial), link 1 up the
 * infraspinatus to J2 over the posterior acromion / scapular spine, link 2 down the posterior deltoid to J3 on the
 * posterior upper arm (W = wdir(42, -64)), then the arm-end neck to BOTTOM's lateral bar. The catalogue's Cardan has
 * a1 = a2 = 90 (p2 = b x w); the best honest configuration (sweep k9: gap 72.02, min margin 9.2 deg) shortens both
 * arcs to 75 deg, shown here, sigma +1. Hubs sit far out on their axes (skin faces 154 / 91 / 164 mm from GH) on WEDGE
 * seats (22-24 mm) because the radial rays meet the back / posterior arm skin ~49 deg off its normal: the wedge plates
 * are drawn normal to the local skin (posterior for J1, radial from the humerus for J3). Closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { b_az: -28, b_el: -19, w_d: 42, w_a: -64, a1: 75, a2: 75, sigma: 1, margin: 5,
              F: [154, 91, 164], wedge: [23, 24, 22], hub_r: 10, stack: 12.25,
              bottom: { Wb: [0, -0.0713, 0.9975], Db: [0, -0.9975, -0.0713], out: 67.5, from: 40, len: 70 }, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.b_az, P.b_el), K.wdir(P.w_d, P.w_a), P.a1, P.a2, P.sigma);
  const ss = u => u * u * (3 - 2 * u);
  const arc = (u, v, r0, r1) => { const g = K.greatArc(u, v, 1, 1, 22), m = g.length - 1; return g.map((p, i) => V.scale(p, r0 + (r1 - r0) * ss(i / m))); };
  /** wedge seat under a hub: a plate normal to the skin, its centre half the wedge height under the hub face */
  const wedge = (p, F, wh, nrm, role, name) => ({ kind: 'plate', role, name, c: V.scale(p, F - wh / 2), z: V.unit(V.add(V.scale(p, 0.4), V.scale(nrm, 0.6))),
    x: V.unit(V.cross(p, nrm)), size: [26, 26], t: wh });

  K.register({
    id: 'posterior-max-margin-cardan',
    name: 'Posterior max-margin Cardan',
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
      const f = C.fk(q, ctx), F = P.F, h = P.stack, harm = ctx.armAxis, B = P.bottom;
      const back = ctx.attach.scapDir([-1, 0, 0]), armOut = V.unit(V.reject(f.p3, harm));
      const barA = ctx.attach.armPt(V.add(V.scale(B.Wb, B.out), V.scale(B.Db, B.from)));
      const barB = ctx.attach.armPt(V.add(V.scale(B.Wb, B.out), V.scale(B.Db, B.from + B.len)));
      const cuffC = V.scale(harm, P.cuff_at);
      return [
        wedge(f.p1, F[0], P.wedge[0], back, 'fixed-scapula', 'J1 wedge seat (back of the scapula)'),
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (up the infraspinatus)', pts: arc(f.p1, f.p2, F[0] + 7, F[1] + 2), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (posterior acromion)', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (down the posterior deltoid)', pts: arc(f.p2, f.p3, F[1] + 9, F[2] + h + 2), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (posterior arm)', c: V.scale(f.p3, F[2]), axis: f.p3, r: P.hub_r, h },
        wedge(f.p3, F[2], P.wedge[2], armOut, 'fixed-arm', 'J3 wedge seat (arm end)'),
        { kind: 'link', role: 'fixed-arm', name: 'neck to BOTTOM', a: V.madd(V.scale(f.p3, F[2] - 2), armOut, 6), b: barA, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar', a: barA, b: barB, r: 3.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

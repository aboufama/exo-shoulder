/* septum-barrel-arm-link - spherical 3R whose last joint is a BARREL lying along the arm (catalogue
 * septum-barrel-arm-link; ideated, no bench model or sweep yet). J1: O20 hub, ACTIVE, on the acromion top a1 = sdir(55, 15)
 * (scapula frame); J2: O20 hub, ACTIVE, floating; J3: barrel hinge, ACTIVE (two MR117 back to back, O14 x 24 mm), its
 * axis through GH aimed down the posterolateral intermuscular-septum strip: barrel centre at armpt(s 150, th 35,
 * R_env + 9 + k) = 21 deg off the humeral axis, so the barrel lies ALONG the arm, nearly tangent to the skin, on its own
 * saddle cuff beside BOTTOM. No neck: the humerus is the rigid link between the barrel cuff and the user's cuff / BOTTOM.
 * Arcs alpha12 / alpha23 = 100 / 50 (the spec's acromion variant), J2 on branch -1: behind the shoulder at rest (all
 * loop frames close, 197 / 239 with the 8 deg margin; branch +1 puts J2 in front). R_env (arm skin radius at s 150 over the poses) taken as 47 mm (schematic: no skin fit yet); hub faces 48 / 66
 * mm. Closed form (KIN.sph3r); out of range when the J2 triangle is within 8 deg of its fold (spec tri_ok) or when L2
 * (rigid great arc J2 -> barrel) swings through the upper arm (the catalogue's main risk 1: q3 carries the axial twist). 3 ACTIVE,
 * 0 PASSIVE (the user-approved cuff slides sit outside the count and are not drawn). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { j1: [55, 15], a12: 100, a23: 50, branch: -1, s_b: 150, th_b: 35, R_env: 47, k: 2, barrel: [7, 24],
              faces: [48, 66], hub_r: 10, stack: 12.25, saddle: [50, 40], margin: 8, cuff_at: 200 };
  const sdir = (lat, lon) => [-Math.cos(lat * D) * Math.sin(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.cos(lon * D)];
  // arm frame of the spec (body_pose H-local = bind coordinates): e down the humerus, l lateral, b posterior
  const e = V.unit(K.BODY.elbow), l = V.unit(V.reject([0, 0, 1], e)), b = V.cross(e, l);
  const armpt = (s, th, r) => V.add(V.scale(e, s), V.scale(V.add(V.scale(l, Math.cos(th * D)), V.scale(b, Math.sin(th * D))), r));
  const cB = armpt(P.s_b, P.th_b, P.R_env + 9 + P.k), wL = V.unit(cB);                    // barrel centre, J3 axis (bind)
  const w = M.mulv(M.T(K.BODY.rest_humerus), wL);                                       // J3 axis in the band humerus frame
  const C = K.sph3r(sdir(P.j1[0], P.j1[1]), w, P.a12, P.a23, P.branch);
  const fitB = (() => {                                                                 // BOTTOM bar (pipeline/full-exo/arm_fit.json)
    const Cb = [-14.71, -315.20, 108.36], ub = [0.0134, 0.9955, -0.0942]; return [Cb, V.madd(Cb, ub, 265)];
  })();

  function L2pts(f, ctx) {                                                              // L2: great arc p2 -> barrel's proximal end
    const prox = V.madd(M.mulv(ctx.Hb, cB), f.p3, -P.barrel[1] / 2);
    return { prox, pts: K.greatArc(f.p2, V.unit(prox), P.faces[1] + 9, V.norm(prox) + P.barrel[0], 16) };
  }
  const inArm = (x, ctx) => { const s = V.dot(x, ctx.armAxis); return s > 30 && s < 300 && V.norm(V.reject(x, ctx.armAxis)) < P.R_env - 6; };

  K.register({
    id: 'septum-barrel-arm-link',
    name: 'Septum barrel (J3 along the arm)',
    dof: { active: 3, passive: 0 },
    params: Object.assign({ j3_off_axis_deg: V.angle(wL, e) }, P),
    q0: ctx => C.solve(ctx),
    qNames: ['J1 (acromion)', 'J2 (floating)', 'J3 (barrel)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the barrel axis is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      if (L2pts(C.fk(q, ctx), ctx).pts.some(x => inArm(x, ctx))) return 'L2 swings across the arm (the barrel carries the axial twist)';
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack, A = p => M.mulv(ctx.Hb, p);
      const cW = A(cB), wW = f.p3, bL = P.barrel[1], L2 = L2pts(f, ctx), prox = L2.prox;
      const radial = V.unit(V.reject(cW, ctx.armAxis)), sad = A(armpt(P.s_b, P.th_b, P.R_env + 2));
      const cuffC = V.scale(ctx.armAxis, P.cuff_at), bt = A(fitB[1]), bb = A(fitB[0]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [44, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (acromion top)', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'L1', u: f.p1, v: f.p2, r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (floating)', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'L2 (to the barrel sleeve)', pts: L2.pts, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 barrel (axis through GH, along the arm)', c: prox, axis: wW, p0: [0, 0, 0], r: P.barrel[0], h: bL },
        { kind: 'plate', role: 'fixed-arm', name: 'barrel saddle cuff (septum strip)', c: sad, z: radial, x: ctx.armAxis, size: P.saddle, t: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM (user part)', a: bt, b: bb, r: 4 },
        { kind: 'strap', role: 'fixed-arm', name: 'user cuff', c: cuffC, axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

/* arm-parked-knee-4r - spherical 4R (all axes through GH) whose spare is set by a torsion spring on the arm-end joint J4
 * and the J2 fold-margin stops (bench model docs/concepts/models/arm-parked-knee-4r.py, doc docs/concepts/arm-parked-knee-4r.md).
 * J1 axis bvec(az, el) fixed in the scapula, J4 axis wdir(wd, wa) fixed in the humerus (band frame); the knee J3 lies on
 * the a3 cone about J4 at the azimuth the spring wants (pz4, arm-fixed: the knee hub parks on arm skin) unless the
 * J1-J3 angle would leave the J2 window [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m]: then the J2 stop takes the
 * load and link 3 swings about J4 against the spring to the nearest feasible azimuth (closed form, the model's policy).
 * J2 from the two-circle closure on branch s1 (concept_kit.closure convention). O20 hubs at every joint (r 10, 12.25 mm
 * stack; hub 4 carries the spring coil, OD ~23) at the model's fitted levels; links 12 x 3 Ti. Member 4 = hub 4's
 * arm-end plate + the K7 14 x 6 neck to BOTTOM's bar, then the bar to the cuff. 4 active joints (unpowered bearing pairs
 * in MVP1), 0 passive translations, 1 spring, 2 stops. Joint values are measured from the rest pose. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 108.0282, el: 71.0171, wd: 76.2005, wa: -7.9064, a: [32.8519, 72.9724, 25.4941], pz4: 104.0211, s1: -1,
              margin: 11.7402, inner: 0.5, faces: [49.0, 59.0, 66.2, 77.0], hub_r: [10, 10, 10, 10], spring_r: 12, stack: 12.25, cuff_at: 165 };
  // best configuration W3n (near-touch objective, farm CMA; Bench(60,160) fast 19.32 / near 21.60; Bench(110,360) exact frozen 25.05);
  // faces = the model's fitted hub levels (mm from GH) at this configuration
  const D2R = K.D2R, R2D = K.R2D;
  const u1 = K.bvec(P.az, P.el), W0 = K.wdir(P.wd, P.wa), [a1, a2, a3] = P.a;
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];             // BOTTOM's bar (body_pose humerus frame)
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  // spring rest direction of the knee, humerus-fixed (band HG frame) = the model's pp
  const ref = Math.abs(W0[1]) < 0.9 ? [0, -1, 0] : [0, 0, -1], e1 = V.unit(V.cross(W0, ref)), e2 = V.cross(W0, e1);
  const PP = V.add(V.scale(W0, Math.cos(a3 * D2R)), V.scale(V.add(V.scale(e1, Math.cos(P.pz4 * D2R)), V.scale(e2, Math.sin(P.pz4 * D2R))), Math.sin(a3 * D2R)));
  const mi = P.margin + P.inner, lo1 = Math.abs(a1 - a2) + mi, hi1 = Math.min(a1 + a2, 360 - a1 - a2) - mi;
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  /** the spare (scapula frame): knee p3, J2 axis p2, spring deflection (deg), whether the J2 stop carries it */
  function state(Q) {
    const p4 = M.mulv(Q, W0), pp = M.mulv(Q, PP), th = V.angle(u1, p4) * D2R;
    const dp = K.axisAngle(p4, u1, pp) * D2R, sa = Math.sin(a3 * D2R), ca = Math.cos(a3 * D2R), den = sa * Math.sin(th) + 1e-12;
    const cmin = (Math.cos(hi1 * D2R) - ca * Math.cos(th)) / den, cmax = (Math.cos(lo1 * D2R) - ca * Math.cos(th)) / den;
    const dlo = Math.acos(Math.max(-1, Math.min(1, cmax))), dhi = Math.acos(Math.max(-1, Math.min(1, cmin)));
    const feas = cmax >= -1 && cmin <= 1 && dlo <= dhi;
    const ad = Math.max(dlo, Math.min(dhi, Math.abs(dp))), d = (dp >= 0 ? 1 : -1) * ad, defl = Math.abs(ad - Math.abs(dp)) * R2D;
    const w = V.unit(V.reject(u1, p4)), base = V.add(V.scale(p4, ca), V.scale(w, sa)), p3 = M.mulv(M.rot(p4, d * R2D), base);
    const c = K.circInt(u1, a1, p3, a2, P.s1);
    return { p: [u1, c.p, p3, p4], ok: feas && c.ok, defl, stop: defl > 1e-3 };
  }
  // home = the rest key configuration
  const restPose = K.KEYS.find(x => x.key === 'rest').pose, Qh = Qof(K.makeCtx(restPose)), U = state(Qh).p;
  function angles(Pa, Q) {
    const q = []; let R = M.I3();
    for (let k = 0; k < 3; k++) { q.push(K.axisAngle(U[k], U[k + 1], M.mulv(M.T(R), Pa[k + 1]))); R = M.mul(R, M.rot(U[k], q[k])); }
    const v = V.perp(U[3]), RL = M.mul(M.mul(M.T(R), Q), M.T(Qh));
    q.push(K.axisAngle(U[3], v, M.mulv(RL, v))); return q;
  }
  function fk(q) {                                                         // scapula frame
    const Rs = [M.rot(U[0], q[0])]; for (let k = 1; k < 4; k++) Rs.push(M.mul(Rs[k - 1], M.rot(U[k], q[k])));
    return { p: [U[0], M.mulv(Rs[0], U[1]), M.mulv(Rs[1], U[2]), M.mulv(Rs[2], U[3])], E: M.mul(Rs[3], Qh) };
  }
  const solve = ctx => { const Q = Qof(ctx); return angles(state(Q).p, Q); };

  K.register({
    id: 'arm-parked-knee-4r',
    name: 'Arm-parked knee 4R (J4 spring + J2 stops)',
    dof: { active: 4, passive: 0 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2 (fold stops)', 'J3 (knee)', 'J4 (spring)'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => M.rotErrDeg(M.mul(ctx.S, fk(q).E), ctx.H),
    check: (q, ctx) => {
      const s = state(Qof(ctx));
      if (!s.ok) return `the J2 window [${lo1.toFixed(0)}, ${hi1.toFixed(0)}] deg cannot be met with link 3 on the a3 cone (fold)`;
      if (s.defl > 1e-3) return null;                                     // on the J2 stop: the spring carries the spare (a working state)
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q), S = ctx.S, W = d => M.mulv(S, d), F = P.faces, h = P.stack, R = P.hub_r;
      const p = f.p.map(W), harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = K.greatArc(p[3], bar0, F[3] + 1, V.norm(bar0), 16), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(p[0], F[0] - 3), z: p[0], x: W([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, MR117-2RS pair)', c: V.scale(p[0], F[0]), axis: p[0], r: R[0], h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti)', u: p[0], v: p[1], r0: F[0] + 4.5, r1: F[1] + 1.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, fold-margin stops: dowel in a slot)', c: V.scale(p[1], F[1]), axis: p[1], r: R[1], h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1)', u: p[1], v: p[2], r0: F[1] + 4.5, r1: F[2] + 1.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 knee (O20, parked on arm skin)', c: V.scale(p[2], F[2]), axis: p[2], r: R[2], h },
        { kind: 'arc', role: 'link', name: 'link 3 (12 x 3 Ti, over link 1 and the neck)', u: p[2], v: p[3], r0: F[2] + 4.5, r1: F[3] + 4.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J4 (O20 + torsion spring coil, OD ~23)', c: V.scale(p[3], F[3]), axis: p[3], r: P.spring_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, arm-end plate of J4)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

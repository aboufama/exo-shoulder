/* minarc-stop-knuckle-4r - a plain spherical 3R whose link 1 is split by a 4th, PASSIVE, sensed O20 hub K held on its
 * stop A by a preloaded clock spring; J2 has hard stops on its interior angle phi (bench model
 * docs/concepts/models/minarc-stop-knuckle-4r.py, doc docs/concepts/minarc-stop-knuckle-4r.md).
 * Min-arc law (the determined 4th coordinate): with J1 fixed in the scapula and J3 fixed in the humerus, the arc
 * a1e = angle(J1, J2) is a1 (K on stop A, rigid 3R) while the 3R (a1, a2) closes with phi in [phi_lo, phi_hi]; past it
 * J2 rests on its stop and the arm opens K to the smallest a1e >= a1 that closes with phi = phi_stop (<= a1max = stop B).
 * K from the two-circle closure J1 (arc b1) / J2 (arc b2) on branch sK. All four axes pass through GH.
 * 0 passive translations, 1 passive rotation (K: spring + stops, so it never sags). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = { az: 90.76, el: 65.50, w: [74.85, -10.5], a1: 44.0, a2: 74.0, b1: 35.0, b2: 55.0, a1max: 78.0,
              phi_lo: 15.0, phi_hi: 170.0, sigma: -1, sK: -1, faces: [51.8, 68.5, 123.0, 78.0], stack: 12.25, cuff_at: 165,
              lv: { l1a: 59.3, l1b: 95.8, l2: 102.2, neck: 85.2 } };
  const u1 = K.bvec(P.az, P.el), u3 = K.wdir(P.w[0], P.w[1]);
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  /** the min-arc law: -> {a1e, state (0 A, 1 stretched, -1 folded), ok} for J1-J3 angle th (deg) */
  function law(th) {
    const ca = Math.cos(P.a1 * D2R), sa = Math.sin(P.a1 * D2R), c2 = Math.cos(P.a2 * D2R), s2 = Math.sin(P.a2 * D2R);
    const cphi = (Math.cos(th * D2R) - ca * c2) / (sa * s2);
    let state = 0, ps = 0;
    if (cphi < Math.cos(P.phi_hi * D2R)) { state = 1; ps = P.phi_hi; } else if (cphi > Math.cos(P.phi_lo * D2R)) { state = -1; ps = P.phi_lo; }
    if (!state) return { a1e: P.a1, state, ok: true };
    const A = c2, B = s2 * Math.cos(ps * D2R), R = Math.hypot(A, B), d = Math.atan2(B, A) / D2R, c = Math.cos(th * D2R) / R;
    if (Math.abs(c) > 1) return { a1e: P.a1, state, ok: false };
    const g = Math.acos(c) / D2R; let best = Infinity;
    for (const x0 of [d - g, d + g]) { const x = K.wrap180(x0); if (x >= P.a1 - 1e-6 && x < best) best = x; }
    return isFinite(best) ? { a1e: best, state, ok: best <= P.a1max } : { a1e: P.a1, state, ok: false };
  }
  function axes(ctx) {
    const p1 = M.mulv(ctx.S, u1), p3 = M.mulv(ctx.H, u3), th = V.angle(p1, p3), L = law(th);
    const c2 = K.circInt(p1, L.a1e, p3, P.a2, P.sigma), p2 = c2.p, cK = K.circInt(p1, P.b1, p2, P.b2, P.sK), pK = cK.p;
    return { p1, p2, p3, pK, L, ok: L.ok && c2.ok && cK.ok };
  }
  const ref1 = ctx => ctx.attach.scapDir([1, 0, 0]);
  function qOf(a, ctx) {
    return [K.axisAngle(a.p1, ref1(ctx), a.pK), K.axisAngle(a.pK, a.p1, a.p2), K.axisAngle(a.p2, a.pK, a.p3),
            K.axisAngle(a.p3, ctx.attach.armDir([0, -1, 0]), a.p2)];
  }
  K.register({
    id: 'minarc-stop-knuckle-4r',
    name: 'Min-arc stop knuckle 4R (spring-held passive K in link 1, J2 hard stops)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => qOf(axes(ctx), ctx),
    qNames: ['J1', 'K (passive, spring)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve: ctx => qOf(axes(ctx), ctx),
    residual: (q, ctx) => {
      // rebuild the chain forward from the joint values and compare with the closure's axes
      const a = axes(ctx), p1 = M.mulv(ctx.S, u1);
      const pK = K.onCone(p1, ref1(ctx), P.b1, q[0]);
      const p2 = K.onCone(pK, p1, P.b2, q[1]);
      const p3 = K.onCone(p2, pK, P.a2, q[2]);
      return [V.angle(pK, a.pK), V.angle(p2, a.p2), V.angle(p3, a.p3), Math.abs(V.angle(a.p1, a.p2) - a.L.a1e)];
    },
    check: (q, ctx) => {
      const a = axes(ctx);
      if (!a.ok) return a.L.state ? `K would pass stop B (a1e > ${P.a1max} deg): the J1-J3 angle is out of reach` : 'chain cannot close';
      return null;
    },
    parts: (q, ctx) => {
      const a = axes(ctx), F = P.faces, h = P.stack, harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const arc = (u, v, r) => K.greatArc(u, v, r, r, 24);
      const neck = arc(a.p3, bar0, P.lv.neck + 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(a.p1, F[0] - 3), z: a.p1, x: ref1(ctx), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, MR117-2RS pair)', c: V.scale(a.p1, F[0]), axis: a.p1, r: 10, h },
        { kind: 'arc', role: 'link', name: 'link 1a (12 x 3 Ti, arc b1)', pts: arc(a.p1, a.pK, P.lv.l1a + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'K (O20, passive, sensed, clock spring on stop A)', c: V.scale(a.pK, F[1]), axis: a.pK, r: 10, h },
        { kind: 'arc', role: 'link', name: 'link 1b (12 x 3 Ti, arc b2)', pts: arc(a.pK, a.p2, P.lv.l1b + 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, interior-angle hard stops)', c: V.scale(a.p2, F[2]), axis: a.p2, r: 10, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1 and the neck)', pts: arc(a.p2, a.p3, P.lv.l2 + 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20)', c: V.scale(a.p3, F[3]), axis: a.p3, r: 10, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, member 3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

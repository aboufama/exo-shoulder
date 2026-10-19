/* crossed-muscle-rails - a spherical 3R with no strap links: two curved rails cross and one small double carriage rides
 * the crossing. Rail 1 (the 'acromial arch', 10 x 5 mm) is part of the exo-scapula: a small circle of half-angle a12
 * about a1 through GH, over the acromion / supraspinatus / spine. Rail 2 (the 'collar') is part of the arm piece: a
 * small circle of half-angle a23 about the arm-fixed a3, around the top of the humeral head, running on to BOTTOM.
 * J1 = carriage 1's position on the arch (about a1), J2 = the O20 bearing between the two carriages about the
 * crossing direction a2, J3 = carriage 2's position on the collar (about a3); a2 is the two-cone closure, so both
 * carriages are captive and nothing sags (catalogue entry; not modelled yet). Seed 1 of the spec's kinematic screen
 * (az1 64.9, el1 56.1, a12 57.4, d3 147.1, az3 -119, a23 87.9, sigma -1); arch low at 56 mm, collar one carriage
 * stack (14 mm) above. Rail extents = the crossing's travel over this loop + half a carriage + 2 deg, capped at
 * Lmax 200 deg; out of range when a carriage leaves its rail or the rails cross at < 25 deg (the rails go tangent
 * across the body and behind the back, ~16 % of the loop). Red team: the arch needs ~198 deg of travel, and overhead
 * that long arch passes 19 mm from the humerus axis (inside the deltoid). Closed form (KIN.sph3r), 3 active, 0 passive. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, R2D = K.R2D, D2R = K.D2R;
  const P = { az1: 64.9, el1: 56.1, a12: 57.4, d3: 147.1, az3: -119.0, a23: 87.9, sigma: -1, rho1: 56, delta: 14,
              car: [26, 14, 6], gamma_min: 25, Lmax: 200, hub_r: 10, bar: [0, -70, 67.5], cuff_at: 165 };
  const a1 = V.unit(K.bvec(P.az1, P.el1)), a3 = V.unit(K.wdir(P.d3, P.az3)), rho2 = P.rho1 + P.delta;
  const C = K.sph3r(a1, a3, P.a12, P.a23, P.sigma);
  const ref1 = K.V.perp(a1), ref3 = K.V.perp(a3);
  // crossing coordinates: phi (deg) about a1 in the scapula frame, psi about a3 in the arm frame; gamma = crossing angle
  function cross(ctx, q) {
    const f = C.fk(q, ctx), A1 = M.mulv(ctx.S, a1), A3 = M.mulv(ctx.H, a3);
    const phi = K.axisAngle(a1, ref1, M.mulv(M.T(ctx.S), f.p2)), psi = K.axisAngle(a3, ref3, M.mulv(M.T(ctx.H), f.p2));
    const t1 = V.unit(V.cross(A1, f.p2)), t3 = V.unit(V.cross(A3, f.p2));
    return { f, A1, A3, phi, psi, t1, t3, gamma: Math.acos(Math.min(1, Math.abs(V.dot(t1, t3)))) * R2D };
  }
  // rail extents from the loop (continuous unwrap, widened by half a carriage + 2 deg, capped at Lmax about the median)
  const half = rho => P.car[0] / 2 / rho * R2D + 2;
  const ext = (() => {
    const out = { phi: [], psi: [] };
    for (const fr of K.motion(240)) {
      const ctx = K.makeCtx(fr.pose, fr.t); if (C.margin(ctx) < 0) continue;
      const c = cross(ctx, C.solve(ctx)); if (c.gamma < P.gamma_min) continue;
      for (const k of ['phi', 'psi']) { const a = out[k], v = c[k]; a.push(a.length ? a[a.length - 1] + K.wrap180(v - a[a.length - 1]) : v); }
    }
    const span = (a, h) => {
      const s = [...a].sort((x, y) => x - y), med = s[s.length >> 1];
      let lo = s[0] - h, hi = s[s.length - 1] + h;
      if (hi - lo > P.Lmax) { lo = Math.max(lo, med - P.Lmax / 2); hi = Math.min(hi, lo + P.Lmax); }
      return [lo, hi];
    };
    return { phi: span(out.phi, half(P.rho1 * Math.sin(P.a12 * D2R))), psi: span(out.psi, half(rho2 * Math.sin(P.a23 * D2R))) };
  })();
  const inside = (v, [lo, hi], h) => { const m = (lo + hi) / 2, d = K.wrap180(v - m); return Math.abs(d) <= (hi - lo) / 2 - h; };

  K.register({
    id: 'crossed-muscle-rails',
    name: 'Crossed muscle-line rails',
    dof: { active: 3, passive: 0 },
    params: Object.assign({ rail1_extent_deg: ext.phi, rail2_extent_deg: ext.psi }, P),
    q0: ctx => C.solve(ctx),
    qNames: ['J1 carriage on the arch', 'J2 carriage bearing', 'J3 carriage on the collar'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      if (C.margin(ctx) < 0) return 'the rails do not cross: the arm is out of the chain\'s reach';
      const c = cross(ctx, q);
      if (c.gamma < P.gamma_min) return `rails cross at ${c.gamma.toFixed(0)} deg (tangent = 3R singularity)`;
      if (!inside(c.phi, ext.phi, half(P.rho1 * Math.sin(P.a12 * D2R)) - 2)) return 'carriage 1 past the end of the arch';
      if (!inside(c.psi, ext.psi, half(rho2 * Math.sin(P.a23 * D2R)) - 2)) return 'carriage 2 past the end of the collar';
      return null;
    },
    parts: (q, ctx) => {
      const c = cross(ctx, q), p2 = c.f.p2, harm = ctx.armAxis;
      const rail = (role, name, A, ref, half, rho, e) => ({ kind: 'rail', role, name, c: V.scale(A, rho * Math.cos(half * D2R)), axis: A, ref,
        rho: rho * Math.sin(half * D2R), a0: e[0], a1: e[1], r: 3 });
      // collar end nearest BOTTOM's cut end -> arm-end strip to BOTTOM
      const bar = M.mulv(ctx.H, P.bar), e3 = V.unit(V.reject(M.mulv(ctx.H, ref3), c.A3)), f3 = V.cross(c.A3, e3);
      const endPt = a => V.add(V.scale(c.A3, rho2 * Math.cos(P.a23 * D2R)), V.scale(V.add(V.scale(e3, Math.cos(a * D2R)), V.scale(f3, Math.sin(a * D2R))), rho2 * Math.sin(P.a23 * D2R)));
      const ends = ext.psi.map(endPt), end = V.norm(V.sub(ends[0], bar)) < V.norm(V.sub(ends[1], bar)) ? ends[0] : ends[1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(bar, harm)), 47);
      return [
        rail('fixed-scapula', 'rail 1: acromial arch (exo-scapula)', c.A1, M.mulv(ctx.S, ref1), P.a12, P.rho1, ext.phi),
        { kind: 'carriage', role: 'active', name: 'J1: carriage 1 on the arch', c: V.scale(p2, P.rho1 + 3), x: c.t1, z: p2, size: P.car },
        { kind: 'hub', role: 'active', name: 'J2: bearing between the carriages', c: V.scale(p2, P.rho1 + 6), axis: p2, r: P.hub_r, h: P.delta - 6 },
        { kind: 'carriage', role: 'active', name: 'J3: carriage 2 on the collar', c: V.scale(p2, rho2 - 3), x: c.t3, z: p2, size: P.car },
        rail('fixed-arm', 'rail 2: humeral-head collar (arm piece)', c.A3, M.mulv(ctx.H, ref3), P.a23, rho2, ext.psi),
        { kind: 'arc', role: 'fixed-arm', name: 'arm end: collar to BOTTOM', u: end, v: bar, r0: rho2, r1: V.norm(bar), r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM to the cuff', a: bar, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

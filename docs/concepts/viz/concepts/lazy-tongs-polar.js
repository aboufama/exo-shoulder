/* lazy-tongs-polar - spherical lazy-tongs polar positioner (catalogue lazy-tongs-polar, models/lazy-tongs-polar.py
 * PARAMS; no sweep yet). Base hub at the scapula pole p1 = bvec(-25.2, 16.8) (medial spine / supraspinatus) carries TWO
 * coaxial ACTIVE joints (root a-bar theta_a, root b-bar theta_b): J1 = their mean = the scissor's azimuth about p1,
 * J2 = their difference = its opening. A thin two-layer scissor of n = 3 rhombi (half-bar 28 deg) runs along the great
 * circle p1 -> e and lengthens / narrows with the hub distance Theta; 3n = 9 PASSIVE pivots, every axis radial through
 * GH. Arm hub at e = H wdir(70.1, -69.4) (posterior deltoid): J3 ACTIVE between the end a-half-bar and the arm member.
 * Closed form (model IK): m = tangent at p1 toward e, half-width w = acos(cos l / cos(Theta / 2n)), J2 = 2 atan(tan w /
 * sin(Theta / 2n)); the residual is the forward kinematics of (J1, J2, J3) against the arm frame, so a pose past the
 * stretch limit (Theta > 0.96 2nl) or below Theta 20 deg reports its error. Node radii are schematic (65 -> 62 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R, R2D = K.R2D;
  const P = { p1_az: -25.2, p1_el: 16.8, e0_d: 70.1, e0_az: -69.4, n: 3, l: 28, stretch: 0.96, th_min: 20,
              R_base: 66, R_arm: 62, bulge: 5, layer: 3.0, bar_w: 7, hub_r: 10, stack: 12.25 };
  const n = P.n, l = P.l * D2R, p1 = V.unit(K.bvec(P.p1_az, P.p1_el)), e0 = V.unit(K.wdir(P.e0_d, P.e0_az));
  const t1 = V.unit(V.reject([0, 1, 0], p1)), t2 = V.cross(p1, t1), t0 = V.unit(V.reject([0, -1, 0], e0));
  const thMax = P.stretch * 2 * n * P.l;
  /** scissor geometry from the world pole P1, unit tangent m at P1 and Theta (deg) */
  function tongs(P1, m, Th) {
    const T = Th * D2R, a = T / (2 * n), w = Math.acos(Math.min(1, Math.cos(l) / Math.cos(a))), bp = V.cross(P1, m);
    const c = s => V.add(V.scale(P1, Math.cos(s)), V.scale(m, Math.sin(s)));
    const X = (s, ww) => V.add(V.scale(c(s), Math.cos(ww)), V.scale(bp, Math.sin(ww)));
    const C = [], Sp = [], Sm = [];
    for (let j = 0; j <= n; j++) C.push(c(j * T / n));
    for (let k = 1; k <= n; k++) { Sp.push(X((k - 0.5) * T / n, w)); Sm.push(X((k - 0.5) * T / n, -w)); }
    return { C, Sp, Sm, w, a, e: C[n], open: 2 * Math.atan(Math.tan(w) / Math.sin(a)) * R2D };
  }
  const endTan = g => V.unit(V.reject(V.sub(g.Sp[n - 1], g.e), g.e));          // end a-half-bar tangent at e
  function solveRaw(ctx) {
    const P1 = M.mulv(ctx.S, p1), e = M.mulv(ctx.H, e0), Th = V.angle(P1, e), Tc = Math.max(P.th_min, Math.min(thMax, Th));
    const m = V.unit(V.reject(e, P1)), g = tongs(P1, m, Tc);
    const J1 = K.axisAngle(P1, M.mulv(ctx.S, t1), m), J3 = K.axisAngle(g.e, endTan(g), M.mulv(ctx.H, t0));
    return [J1, g.open, J3];
  }
  function fk(q, ctx) {                                                           // (J1, J2, J3) -> scissor + arm frame
    const P1 = M.mulv(ctx.S, p1), m = V.add(V.scale(M.mulv(ctx.S, t1), Math.cos(q[0] * D2R)), V.scale(M.mulv(ctx.S, t2), Math.sin(q[0] * D2R)));
    const Tq = Math.tan(Math.max(1e-4, Math.min(179, q[1])) * D2R / 2) * Math.cos(l), cl = Math.cos(l);
    const a = Math.acos(Math.min(1, Math.sqrt((Tq * Tq + cl * cl) / (1 + Tq * Tq)))), g = tongs(P1, m, 2 * n * a * R2D);
    const t = M.mulv(K.M.rot(g.e, q[2]), endTan(g));
    return Object.assign(g, { P1, m, Th: 2 * n * a * R2D, F: M.fromCols(g.e, t, V.cross(g.e, t)) });
  }
  const rad = (j, side) => P.R_base + (P.R_arm - P.R_base) * j / n + P.bulge * Math.sin(Math.PI * j / n) + (side ? 1.5 : 0);
  const arc = (a, b, ra, rb) => K.greatArc(a, b, ra, rb, 10);

  K.register({
    id: 'lazy-tongs-polar',
    name: 'Lazy-tongs polar positioner',
    dof: { active: 3, passive: 9 },
    params: P,
    q0: ctx => solveRaw(ctx),
    qNames: ['J1 azimuth (theta_a + theta_b) / 2', 'J2 opening theta_b - theta_a', 'J3 arm hub'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: (ctx, qp) => { const q = solveRaw(ctx); return qp ? q.map((x, i) => i === 1 ? x : qp[i] + K.wrap180(x - qp[i])) : q; },
    residual: (q, ctx) => {
      const g = fk(q, ctx), e = M.mulv(ctx.H, e0), t = V.unit(V.reject(M.mulv(ctx.H, t0), e));
      return M.rotErrDeg(g.F, M.fromCols(e, t, V.cross(e, t)));
    },
    check: (q, ctx) => {
      const Th = V.angle(M.mulv(ctx.S, p1), M.mulv(ctx.H, e0));
      if (Th > thMax) return `scissor fully stretched (hubs ${Th.toFixed(0)} deg apart)`;
      if (Th < P.th_min) return 'hubs too close (scissor fully closed)';
      if (Th * D2R * (P.R_base + P.R_arm) / 2 < 2 * P.hub_r + 4) return 'hub rims within 4 mm';
      return null;
    },
    parts: (q, ctx) => {
      const g = fk(q, ctx), L1 = 0, L2 = P.layer, out = [], S = ctx.S, h = P.stack;
      const pt = (d, r) => V.scale(d, r);
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: pt(g.P1, P.R_base - 9), z: g.P1, x: M.mulv(S, t1), size: [40, 30], t: 3 });
      out.push({ kind: 'hub', role: 'active', name: 'base hub theta_a (root a-bar)', c: pt(g.P1, P.R_base - 6), axis: g.P1, r: P.hub_r, h: 6 });
      out.push({ kind: 'hub', role: 'active', name: 'base hub theta_b (root b-bar)', c: pt(g.P1, P.R_base), axis: g.P1, r: P.hub_r - 1, h: 6 });
      // a-family on layer 1, b-family on layer 2 (catalogue node order); full bars cross at C_k
      const fam = (side, dz) => {
        const Sa = side > 0 ? g.Sp : g.Sm, Sb = side > 0 ? g.Sm : g.Sp, bars = [];
        bars.push(arc(g.C[0], Sb[0], rad(0, 0) + dz, rad(0.5, 1) + dz));
        for (let k = 1; k <= n - 1; k++) bars.push(arc(Sa[k - 1], g.C[k], rad(k - 0.5, 1) + dz, rad(k, 0) + dz).concat(arc(g.C[k], Sb[k], rad(k, 0) + dz, rad(k + 0.5, 1) + dz).slice(1)));
        bars.push(arc(Sa[n - 1], g.C[n], rad(n - 0.5, 1) + dz, rad(n, 0) + dz));
        return bars;
      };
      fam(+1, L1).forEach((pts, i) => out.push({ kind: 'arc', role: 'link', name: `a-bar ${i}`, pts, r: 2 }));
      fam(-1, L2).forEach((pts, i) => out.push({ kind: 'arc', role: 'link', name: `b-bar ${i}`, pts, r: 2 }));
      for (let j = 1; j < n; j++) out.push({ kind: 'hub', role: 'passive', name: `centre pivot C${j}`, c: pt(g.C[j], rad(j, 0) - 2), axis: g.C[j], p0: pt(g.C[j], rad(j, 0)), r: 4, h: 6.3 });
      for (let k = 1; k <= n; k++) for (const [Sx, s] of [[g.Sp, '+'], [g.Sm, '-']])
        out.push({ kind: 'hub', role: 'passive', name: `side pivot S${k}${s}`, c: pt(Sx[k - 1], rad(k - 0.5, 1) - 2), axis: Sx[k - 1], p0: pt(Sx[k - 1], rad(k - 0.5, 1)), r: 4, h: 6.3 });
      out.push({ kind: 'hub', role: 'active', name: 'J3 arm hub', c: pt(g.e, P.R_arm - 12), axis: g.e, r: P.hub_r, h: 9 });
      out.push({ kind: 'hub', role: 'passive', name: 'end pivot C_n (a / b half-bars)', c: pt(g.e, P.R_arm - 2), axis: g.e, p0: pt(g.e, P.R_arm), r: 4, h: 6.3 });
      const e = M.mulv(ctx.H, e0), cuffC = V.scale(ctx.armAxis, 165), dn = V.unit(V.reject(e, ctx.armAxis));
      out.push({ kind: 'link', role: 'fixed-arm', name: 'arm member to the cuff', a: V.scale(e, P.R_arm - 8), b: V.madd(cuffC, dn, 49), r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff (passive self-aligning slides)', c: cuffC, axis: ctx.armAxis, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();

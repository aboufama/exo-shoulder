/* rolling-elbow-fivebar - hubless spherical five-bar + roll (catalogue rolling-elbow-fivebar,
 * models/rolling-elbow-fivebar.py PARAMS and Leg kinematics; no sweep yet). Two legs from the scapula to ONE arm hub on
 * the arm-fixed axis W = wdir(71.38, 4.78): base hub A_k ACTIVE (u1 = bvec(-60, 40), u2 = bvec(-40, 40)) -> crank (a 60)
 * ending in an edge disc (angular radius rho 10 about c1) that ROLLS without slip on the coupler's edge disc (rho about
 * c2), held by crossed flexure straps (Jacob's ladder) - no elbow hub, both link ends on one layer -> coupler (c 120) ->
 * C PASSIVE at W; coupler 1 -> D ACTIVE roll about W -> arm plate -> neck to BOTTOM. Coupler vs crank
 * M(psi) = R(c1, psi) R(c2, k psi), k = sin rho1 / sin rho2 = 1, psi = 0 the straight leg; per leg psi solves
 * angle(u, M W0) = angle(u, W) on the monotone branch (side s1 = +1, s2 = -1) holding the most loop frames, then theta
 * = azimuth about u (model Leg.segment / solve / joints). 3 ACTIVE (A1, A2, D) + 3 PASSIVE (two rolling elbows, C).
 * The contact point travels along both rims as the A-frame folds. Radii are schematic (hubs 58, discs 72, W hub 62). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { b1: [-60, 40], b2: [-40, 40], a: [60, 60], c: [120, 120], rho: 10, ratio: 1, wd: 71.38, wa: 4.78, s: [1, -1],
              sing: 8, par: 12, sep: 17, psi_max: 120, faces: [58, 58], R_e: 72, F_W: 62, hub_r: 10, stack: 12.25 };
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];
  const rho1 = P.rho, rho2 = P.rho * P.ratio, kk = Math.sin(rho1 * D2R) / Math.sin(rho2 * D2R);
  const Wh = K.wdir(P.wd, P.wa), rh = V.unit(V.reject([0, 0, 1], Wh));
  const legs = [0, 1].map(i => {
    const u = V.unit(K.bvec(...(i ? P.b2 : P.b1))), e = V.unit(V.reject([1, 0, 0], u));
    const gc = s => V.add(V.scale(u, Math.cos(s * D2R)), V.scale(e, Math.sin(s * D2R))), a = P.a[i], c = P.c[i];
    const L = { u, c1: gc(a - rho1), g0: gc(a), c2: gc(a + rho2), W0: gc(a + c), near: gc(a - 2 * rho1), far: gc(a + 2 * rho2), sigma: P.s[i] };
    L.t0 = V.unit(V.reject(L.c2, L.W0));
    L.M = psi => M.mul(M.rot(L.c1, psi), M.rot(L.c2, kk * psi));
    L.f = psi => V.angle(u, M.mulv(L.M(psi), L.W0));
    return L;
  });
  const wS = ctx => M.mulv(M.mul(M.T(ctx.S), ctx.H), Wh);                       // arm axis W in the scapula frame
  // per leg: the monotone run of f(psi) on side sigma holding the most loop targets (model Leg.segment)
  const loopW = K.motion(90).map(f => wS(K.makeCtx(f.pose, f.t)));
  legs.forEach(L => {
    const pg = [], fg = []; for (let p = 0; p <= P.psi_max + 1e-9; p += 0.5) { pg.push(L.sigma * p); fg.push(L.f(L.sigma * p)); }
    const T = loopW.map(w => V.angle(w, L.u)); let best = null, j0 = 0;
    const sg = j => Math.sign(fg[j + 1] - fg[j]) || 1;
    for (let j = 1; j <= fg.length - 1; j++) {
      if (j < fg.length - 1 && sg(j) === sg(j0)) continue;
      const loI = fg[j] >= fg[j0] ? j0 : j, hiI = loI === j0 ? j : j0, stat = x => x !== fg.length - 1;
      const lo = fg[loI] + (stat(loI) ? P.sing : 0), hi = fg[hiI] - (stat(hiI) ? P.sing : 0);
      const sc = T.filter(t => t >= lo && t <= hi).length;
      if (hi > lo && (!best || sc > best.sc)) best = { sc, ps: pg.slice(j0, j + 1), fs: fg.slice(j0, j + 1), lo, hi };
      j0 = j;
    }
    if (best.fs[best.fs.length - 1] < best.fs[0]) { best.ps.reverse(); best.fs.reverse(); }
    L.seg = best;
  });
  function legSolve(L, w) {                                                      // psi by bisection on the branch (clamped)
    const { ps, fs } = L.seg, T = Math.max(fs[0], Math.min(fs[fs.length - 1], V.angle(w, L.u)));
    let j = 0; while (j < fs.length - 2 && fs[j + 1] < T) j++;
    let a = ps[j], b = ps[j + 1];
    for (let i = 0; i < 40; i++) { const m = 0.5 * (a + b); if (L.f(m) < T) a = m; else b = m; }
    const psi = 0.5 * (a + b), th = K.axisAngle(L.u, M.mulv(L.M(psi), L.W0), w);
    return [th, psi];
  }
  function state(q, ctx) {                                                       // q = [th1, th2, D, psi1, psi2, C]
    return legs.map((L, i) => { const Rk = M.rot(L.u, q[i]), Rc = M.mul(Rk, L.M(q[3 + i])); return { Rk, Rc, L, psi: q[3 + i] }; });
  }

  K.register({
    id: 'rolling-elbow-fivebar',
    name: 'Rolling-elbow five-bar + roll',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => K.concepts['rolling-elbow-fivebar'].solve(ctx),
    qNames: ['A1', 'A2', 'D roll about W', 'rolling elbow 1 psi', 'rolling elbow 2 psi', 'C (coupler 2 vs 1)'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: (ctx, qp) => {
      const w = wS(ctx), s = legs.map(L => legSolve(L, w)), st = state([s[0][0], s[1][0], 0, s[0][1], s[1][1], 0], ctx);
      const t1 = M.mulv(st[0].Rc, legs[0].t0), Qrh = M.mulv(M.mul(M.T(ctx.S), ctx.H), rh);
      const q = [s[0][0], s[1][0], K.axisAngle(w, t1, Qrh), s[0][1], s[1][1], K.axisAngle(w, t1, M.mulv(st[1].Rc, legs[1].t0))];
      return qp ? q.map((x, i) => (i === 3 || i === 4) ? x : qp[i] + K.wrap180(x - qp[i])) : q;
    },
    residual: (q, ctx) => {
      const w = wS(ctx), st = state(q, ctx), Qrh = M.mulv(M.mul(M.T(ctx.S), ctx.H), rh);
      return [V.angle(M.mulv(st[0].Rc, legs[0].W0), w), V.angle(M.mulv(st[1].Rc, legs[1].W0), w),
              K.wrap180(q[2] - K.axisAngle(w, M.mulv(st[0].Rc, legs[0].t0), Qrh))];
    },
    check: (q, ctx) => {
      const w = wS(ctx), st = state(q, ctx);
      for (const [i, L] of legs.entries()) { const T = V.angle(w, L.u); if (T < L.seg.lo || T > L.seg.hi) return `leg ${i + 1} out of its branch window (straight / folded / strap wrap)`; }
      const g = st.map(s => M.mulv(s.Rk, M.mulv(M.rot(s.L.c1, s.psi), s.L.g0)));
      const n1 = V.unit(V.cross(g[0], w)), n2 = V.unit(V.cross(g[1], w));
      if (V.norm(V.cross(n1, n2)) < Math.sin(P.par * D2R)) return 'loop (parallel) singularity: couplers aligned';
      if (V.angle(g[0], g[1]) < P.sep) return 'rolling contacts too close';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, st = state(q, ctx), Wd = d => M.mulv(S, d), F = P.faces, Re = P.R_e, out = [];
      const Ww = M.mulv(ctx.H, Wh), sr = Re * Math.sin(rho1 * D2R), cr = Re * Math.cos(rho1 * D2R);
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base (one part on the scapula handler)', u: Wd(legs[0].u), v: Wd(legs[1].u), r0: F[0] - 3, r1: F[1] - 3, r: 4 });
      st.forEach((s, i) => {
        const L = s.L, R = s.Rk, Rc = s.Rc, ax = Wd(L.u);
        const g = Wd(M.mulv(R, M.mulv(M.rot(L.c1, s.psi), L.g0)));
        out.push({ kind: 'hub', role: 'active', name: `A${i + 1}`, c: V.scale(ax, F[i]), axis: ax, r: P.hub_r, h: P.stack });
        out.push({ kind: 'arc', role: 'link', name: `crank ${i + 1}`, u: ax, v: Wd(M.mulv(R, L.near)), r0: F[i] + 4.6, r1: Re, r: 2.5 });
        out.push({ kind: 'ring', role: 'passive', name: `crank ${i + 1} edge disc (rolling)`, c: V.scale(Wd(M.mulv(R, L.c1)), cr), axis: Wd(M.mulv(R, L.c1)), r: sr, t: 4 });
        out.push({ kind: 'ring', role: 'passive', name: `coupler ${i + 1} edge disc (rolling)`, c: V.scale(Wd(M.mulv(Rc, L.c2)), cr), axis: Wd(M.mulv(Rc, L.c2)), r: sr, t: 4 });
        out.push({ kind: 'point', role: 'passive', name: `rolling contact ${i + 1}`, p: V.scale(g, Re), r: 3.2 });
        out.push({ kind: 'arc', role: 'link', name: `coupler ${i + 1}`, u: Wd(M.mulv(Rc, L.far)), v: Ww, r0: Re, r1: P.F_W + 4 + 4 * i + P.hub_r * 0.2, r: 2.5 });
      });
      out.push({ kind: 'hub', role: 'active', name: 'D (roll about W)', c: V.scale(Ww, P.F_W), axis: Ww, r: 12, h: 4 });
      out.push({ kind: 'hub', role: 'passive', name: 'C (coupler 2 vs coupler 1)', c: V.scale(Ww, P.F_W + 4), axis: Ww, r: 11, h: 8 });
      const bar0 = M.mulv(ctx.Hb, V.add(V.scale(WB, 67.5 + 6.5), V.scale(DB, 40)));
      out.push({ kind: 'link', role: 'fixed-arm', name: 'neck to BOTTOM', a: V.scale(Ww, P.F_W + 2), b: bar0, r: 3.5 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar (user part)', a: M.mulv(ctx.Hb, V.add(V.scale(WB, 70.5), V.scale(DB, 40))),
                 b: M.mulv(ctx.Hb, V.add(V.scale(WB, 70.5), V.scale(DB, 170))), r: 4 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 170), axis: ctx.armAxis, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();

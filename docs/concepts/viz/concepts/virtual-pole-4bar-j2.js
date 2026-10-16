/* virtual-pole-4bar-j2 - DEAD: a spherical 3R whose J2 is replaced by a SPHERICAL FOUR-BAR on link 1 (every pin axis
 * through GH): link 1 carries the ground pins A0 (ACTIVE, the J2 drive) and B0, cranks A and B run to the coupler pins
 * A1 / B1, and the COUPLER carries the J3 hub; the coupler turns about the instantaneous pole (the crossing of the two
 * crank great circles) = a VIRTUAL J2 axis that walks along the centrode (docs/concepts/virtual-pole-4bar-j2.md,
 * models/virtual-pole-4bar-j2.py, at = 2). Drawn at its best honest configuration (sweeps k442, coarse-v3, gap 145.94
 * fast / 151.43 frozen Bench(110,360) exact): the k2221 3R axes J1 bvec(0.65, 76.82), a1 80.71, a2 62.93, J3 wdir(93.82,
 * -4.2), home dihedral beta -110; pins on great circles from the home pole (J2): A at psi 285 (A0 35 deg, A1 60 deg out),
 * B at psi 335 (B0 20, B1 45), sigma auto (the home slope), q 0.97. Hub levels = the doc's per-hub table for this config
 * (J1 55.0, A0 69.0, A1 63.6, B0 83.1, B1 92.1, J3 68.0 mm). Closure as the model: the coupler's rotation Rc(theta) in
 * closed form (crank A angle theta, B1 by the two-circle closure on the assembly sign), the carried J3 axis c(theta)
 * must keep angle(j1, c) = angle(j1, w) (a 1-D root on the model's 0.25 deg grid inside the transmission window
 * [25, 155] deg at both coupler pins, crossing angle >= 12), then J1 turns phi about j1 to carry c onto w. The preview
 * takes the root nearest the previous frame (the model: nearest theta 0, pose-local) so the linkage moves continuously;
 * where no root exists the four-bar stays at its last angle and the frame shows red. 3 ACTIVE (J1, A0 = J2 drive, J3)
 * + 3 PASSIVE pins (B0, A1, B1, set by the crank angle), 0 passive translations. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { at: 2, az: 0.65, el: 76.82, a1: 80.71, a2: 62.93, wd: 93.82, wa: -4.2, zeta: 0, beta: -110, sigma: 0,
              psiA: 285, dA0: 35, dA1: 60, psiB: 335, dB0: 20, dB1: 45, q: 0.97, M4: 25, XMIN: 12,
              lv: { J1: 55.0, A0: 69.0, A1: 63.6, B0: 83.1, B1: 92.1, J3: 68.0 }, hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const ID = 'virtual-pole-4bar-j2', NAME = 'Virtual-pole four-bar as J2 (3R)';

  // ---- shared spherical four-bar kinematics (models/virtual-pole-4bar-j2.py: gc, FourBar, layout, curve, solve)
  const ang = (u, v) => V.angle(u, v);
  const gc = (c, ref, psi, d) => {
    c = V.unit(c); const t0 = V.unit(V.reject(ref, c));
    const t = V.add(V.scale(t0, Math.cos(psi * D2R)), V.scale(V.cross(c, t0), Math.sin(psi * D2R)));
    return V.add(V.scale(c, Math.cos(d * D2R)), V.scale(V.unit(t), Math.sin(d * D2R)));
  };
  const frame2 = (x, y) => { x = V.unit(x); y = V.unit(V.reject(y, x)); return M.fromCols(x, y, V.cross(x, y)); };
  const j = V.unit(K.bvec(P.az, P.el)), Y = Math.abs(j[1]) < 0.95 ? [0, 1, 0] : [1, 0, 0];
  const t0 = M.mulv(M.rot(j, P.zeta), V.unit(V.reject(Y, j)));
  const j2h = V.add(V.scale(j, Math.cos(P.a1 * D2R)), V.scale(t0, Math.sin(P.a1 * D2R)));
  const pole = P.at === 2 ? j2h : j, ref = P.at === 2 ? j : j2h, carried = P.at === 2 ? gc(j2h, j, P.beta, P.a2) : j2h;
  const a0 = gc(pole, ref, P.psiA, P.dA0), b0 = gc(pole, ref, P.psiB, P.dB0), a1h = gc(pole, ref, P.psiA, P.dA1), b1h = gc(pole, ref, P.psiB, P.dB1);
  const aB = ang(b0, b1h), gC = ang(a1h, b1h), sA = Math.sign(V.dot(b1h, V.cross(b0, a1h))) || 1, E0 = frame2(a1h, b1h);
  function fbAt(th) {                                  // theta deg -> a1, b1, Rc, transmission margin (deg, -90: no assembly)
    const a1 = M.mulv(M.rot(a0, th), a1h), cl = K.circInt(b0, aB, a1, gC, sA), b1 = cl.p;
    const tang = (at, to) => V.unit(V.reject(to, at));
    const muB = ang(tang(b1, b0), tang(b1, a1)), muA = ang(tang(a1, a0), tang(a1, b1));
    const mg = cl.ok ? Math.min(muA, 180 - muA, muB, 180 - muB) : -90;
    return { a1, b1, Rc: M.mul(frame2(a1, b1), M.T(E0)), mg };
  }
  // the coupler curve on the model's 0.25 deg grid, restricted to the transmission window around theta 0
  const grid = []; for (let th = -180; th < 180; th += 0.25) { const f = fbAt(th); grid.push({ th, c: M.mulv(f.Rc, carried), ok: f.mg >= P.M4 }); }
  let i0 = grid.findIndex(g => g.th === 0), lo = i0, hi = i0;
  if (grid[i0].ok) { while (lo > 0 && grid[lo - 1].ok) lo--; while (hi < grid.length - 1 && grid[hi + 1].ok) hi++; }
  const CV = grid.slice(lo, hi + 1); i0 -= lo;
  const near = ang(a1h, carried) <= ang(b1h, carried) ? 'A1' : 'B1';         // coupler pin nearest the carried hub
  const gName = ang(j, a0) <= ang(j, b0) ? 'A0' : 'B0';                     // at = 2: link-1 pin nearest J1
  let SIG = P.sigma;
  /** target (z, rho) of a frame, in the scapula frame: at 2 angle(j, c) = angle(j, ws); at 1 angle(c, ws) = a2 */
  const wS = ctx => M.mulv(M.T(ctx.S), M.mulv(ctx.H, K.wdir(P.wd, P.wa)));
  const target = ctx => { const ws = wS(ctx); return P.at === 2 ? { z: j, rho: ang(j, ws), ws } : { z: ws, rho: P.a2, ws }; };
  if (SIG === 0) {                                     // at = 2 home branch: slope sign of c(theta) . j at theta 0
    const a = CV[Math.max(i0 - 1, 0)].c, b = CV[Math.min(i0 + 1, CV.length - 1)].c; SIG = Math.sign(V.dot(V.sub(b, a), j)) || 1;
  }
  /** roots of c(theta) . z = cos rho on branch SIG: theta, crossing angle; the one nearest thPrev */
  function root(ctx, thPrev) {
    const { z, rho } = target(ctx), cr = Math.cos(rho * D2R); let best = null;
    for (let i = 0; i < CV.length - 1; i++) {
      const g0 = V.dot(CV[i].c, z) - cr, g1 = V.dot(CV[i + 1].c, z) - cr;
      if (Math.sign(g0) === Math.sign(g1) || Math.sign(g1 - g0) !== SIG) continue;
      const f = Math.max(0, Math.min(1, g0 / (g0 - g1))), th = CV[i].th + f * 0.25;
      const dc = V.sub(CV[i + 1].c, CV[i].c), zr = V.unit(V.reject(z, CV[i].c));
      const x = Math.asin(Math.min(1, Math.abs(V.dot(dc, zr)) / (V.norm(dc) || 1e-12))) * K.R2D;
      const cost = Math.abs(th - thPrev);
      if (!best || cost < best.cost) best = { th, x, cost };
    }
    return best;
  }
  const thLo = CV[0].th, thHi = CV[CV.length - 1].th;
  /** chain geometry from q */
  function geo(q, ctx) {
    const th = P.at === 2 ? q[1] : q[0], f = fbAt(th), c = M.mulv(f.Rc, carried), S = ctx.S, w = M.mulv(ctx.H, K.wdir(P.wd, P.wa));
    if (P.at === 2) {
      const R1 = M.rot(j, q[0]), SR = M.mul(S, R1), g = u => M.mulv(SR, u);
      return { f, th, c, J1: M.mulv(S, j), A0: g(a0), B0: g(b0), A1: g(f.a1), B1: g(f.b1), J3: g(c), w, pole: g(j2h) };
    }
    const g = u => M.mulv(S, u);
    return { f, th, c, A0: g(a0), B0: g(b0), A1: g(f.a1), B1: g(f.b1), J2: g(c), J3: w, w, pole: g(j) };
  }

  K.register({
    id: ID, name: NAME,
    dof: { active: 3, passive: 3 },
    params: Object.assign({ theta_window: [thLo, thHi], sigma_used: SIG }, P),
    q0: ctx => (function () { const r = root(ctx, 0), th = r ? r.th : 0; return solveQ(ctx, th); })(),
    qNames: P.at === 2 ? ['J1', 'crank A (A0, the J2 drive)', 'J3'] : ['crank A (A0, the J1 drive)', 'J2', 'J3'],
    qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg'],
    solve: (ctx, qPrev) => {
      const thPrev = qPrev ? (P.at === 2 ? qPrev[1] : qPrev[0]) : 0, r = root(ctx, thPrev);
      return solveQ(ctx, r ? r.th : Math.max(thLo, Math.min(thHi, thPrev)));
    },
    residual: (q, ctx) => {
      const G = geo(q, ctx);
      return P.at === 2 ? [ang(G.J3, G.w)] : [Math.abs(ang(G.J2, G.w) - P.a2)];
    },
    check: (q, ctx) => {
      const r = root(ctx, P.at === 2 ? q[1] : q[0]);
      if (!r) return 'the coupler curve misses the arm (four-bar outside its transmission window)';
      if (r.x < P.XMIN) return `coupler curve crosses the target at ${r.x.toFixed(0)} deg (fold)`;
      const G = geo(q, ctx); if (G.f.mg < P.M4) return `transmission angle ${G.f.mg.toFixed(0)} deg (dead point)`;
      return null;
    },
    parts: (q, ctx) => partsOf(geo(q, ctx), ctx)
  });

  function solveQ(ctx, th) {
    const f = fbAt(th), c = M.mulv(f.Rc, carried), { ws } = target(ctx);
    if (P.at === 2) {
      const phi = K.axisAngle(j, c, ws), R1 = M.rot(j, phi), J3 = M.mulv(ctx.S, M.mulv(R1, c)), A1 = M.mulv(ctx.S, M.mulv(R1, f.a1));
      return [phi, th, K.axisAngle(J3, A1, ctx.armAxis)];
    }
    const J2 = M.mulv(ctx.S, c), A1 = M.mulv(ctx.S, f.a1), J3 = M.mulv(ctx.H, K.wdir(P.wd, P.wa));
    return [th, K.axisAngle(J2, A1, J3), K.axisAngle(J3, J2, ctx.armAxis)];
  }

  function partsOf(G, ctx) {
    const L = P.lv, h = P.stack, top = n => L[n] + h + 1, harm = ctx.armAxis, ng = P.neck_deg * D2R;
    const nk = V.unit(V.add(V.scale(G.w, Math.cos(ng)), V.scale(V.unit(V.reject(harm, G.w)), Math.sin(ng))));   // neck on the ARM's J3 axis w
    const neckEnd = V.scale(nk, L.J3 + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
    const pin = { A0: G.A0, B0: G.B0, A1: G.A1, B1: G.B1 }, X = pin[near], Yn = near === 'A1' ? 'B1' : 'A1', Yp = pin[Yn];
    const hub = (n, role, label) => ({ kind: 'hub', role, name: label, c: V.scale(n === 'J2' ? G.J2 : n === 'J1' ? G.J1 : n === 'J3' ? G.J3 : pin[n], L[n]),
      axis: n === 'J2' ? G.J2 : n === 'J1' ? G.J1 : n === 'J3' ? G.J3 : pin[n], r: P.hub_r, h });
    const arc = (role, name, u, v, r0, r1) => ({ kind: 'arc', role, name, u, v, r0, r1, r: 2.5 });
    const out = [];
    if (P.at === 2) {
      const oName = gName === 'A0' ? 'B0' : 'A0';
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(G.J1, L.J1 - 3), z: G.J1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 });
      out.push(hub('J1', 'active', 'J1 (O20 hub)'));
      out.push(arc('link', 'link 1 (J1 to the ground pins)', G.J1, pin[gName], top('J1'), top(gName)));
      out.push(arc('link', 'link 1 (between the ground pins)', pin[gName], pin[oName], top(gName), top(oName)));
    } else {
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(V.unit(V.add(G.A0, G.B0)), Math.min(L.A0, L.B0) - 3), z: V.unit(V.add(G.A0, G.B0)), x: ctx.attach.scapDir([1, 0, 0]), size: [40, 28], t: 3 });
      out.push(arc('fixed-scapula', 'base ground strap A0 - B0', G.A0, G.B0, L.A0 - 1, L.B0 - 1));
    }
    out.push(hub('A0', 'active', P.at === 2 ? 'A0 (the J2 drive)' : 'A0 (the J1 drive)'));
    out.push(hub('B0', 'passive', 'B0'));
    out.push(arc('link', 'crank A', G.A0, G.A1, L.A0 + 1, L.A1 - 1));
    out.push(arc('link', 'crank B', G.B0, G.B1, L.B0 + 1, L.B1 - 1));
    out.push(hub('A1', 'passive', 'A1 (coupler pin)'));
    out.push(hub('B1', 'passive', 'B1 (coupler pin)'));
    if (P.at === 2) {
      out.push(arc('link', 'coupler (between its pins)', Yp, X, top(Yn), top(near)));
      out.push(arc('link', 'coupler (to J3)', X, G.J3, top(near), top('J3')));
      out.push({ kind: 'link', role: 'link', name: 'virtual J2 pole at home (construction line)', a: V.scale(G.pole, 30), b: V.scale(G.pole, 90), r: 0.5 });
    } else {
      out.push(arc('link', 'link 1 = coupler (between its pins)', Yp, X, top(Yn), top(near)));
      out.push(arc('link', 'link 1 = coupler (to J2)', X, G.J2, top(near), top('J2')));
      out.push(hub('J2', 'active', 'J2 (O20 hub)'));
      out.push(arc('link', 'link 2 (true arc a2: a gap to J3 when the loop cannot close)', G.J2, gc(G.J2, G.J3, 0, P.a2), top('J2'), top('J3')));
      out.push({ kind: 'link', role: 'link', name: 'virtual J1 pole at home (construction line)', a: V.scale(G.pole, 30), b: V.scale(G.pole, 90), r: 0.5 });
    }
    out.push(hub('J3', 'active', 'J3 (O20 hub, on the chain side; the neck sits on the arm\'s axis w)'));
    out.push({ kind: 'arc', role: 'fixed-arm', name: 'neck', u: G.w, v: nk, r0: L.J3 + 1, r1: L.J3 + 1, r: 3 });
    out.push({ kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 });
    out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
    out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
    return out;
  }
})();

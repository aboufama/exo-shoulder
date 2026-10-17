/* cruciate-knuckle-3r - a plain O20 spherical 3R at the cap-pole seats whose J2 is a CROSSED (cruciate) spherical
 * four-bar, the knee's ligaments: link 1 carries the ground pins A0 (ACTIVE, the J2 drive) and B0; crank A runs A0 -> A1
 * and crank B runs B0 -> B1 and the two CROSS in an X (crank B 1 mm over crank A); the coupler carries A1, B1 and the J3
 * hub. The instantaneous J2 axis is the crossing of the two cranks, and it rolls along both as the knuckle turns
 * (docs/concepts/cruciate-knuckle-3r.md, models/cruciate-knuckle-3r.py, anchored layout). Kinematics as the model: the
 * coupler curve c(theta) of the carried J3 axis on a 0.25 deg crank grid; th(theta) = angle(J1, c); the knuckle lives
 * on the LONGEST monotone th run with both transmission angles in [30, 150] deg; its window is that run minus 5 deg of th
 * at each end (a dowel on crank A's own angle). Per frame th = angle(J1, arm's J3 axis) -> theta by interpolation on the
 * run (monotone, so unique: no branch choice), then J1 turns phi to carry c onto w, then J3 turns q3. Outside the window
 * the knuckle stays at the run's end and the frame shows red. 3 ACTIVE (J1, A0, J3) + 3 PASSIVE pins (B0, A1, B1),
 * 0 passive translations. All six pins are O20 v5 stacks (Keep O20 only). Drawn at the screen's best honest config. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { az: 43.15, el: 59.93, wd: 92.03, wa: -9.03,
              th0: 21.46, dA0: 46.64, pA0: 21.88, dB0: 26.79, pB0: 49.2, dA1: 34.95, pA1: 8.6, dB1: 61.7, pB1: 16.06, MU: 30, MARGIN: 5,
              lv: { J1: 55, A0: 150, B0: 65, A1: 101, B1: 164, J3: 70 }, hub_r: 10, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const ID = 'cruciate-knuckle-3r', NAME = 'Cruciate knuckle J2: crossed four-bar at the cap pole (3R)';

  const ang = (u, v) => V.angle(u, v);
  const gc = (c, ref, psi, d) => {
    c = V.unit(c); const t0 = V.unit(V.reject(ref, c));
    const t = V.add(V.scale(t0, Math.cos(psi * D2R)), V.scale(V.cross(c, t0), Math.sin(psi * D2R)));
    return V.add(V.scale(c, Math.cos(d * D2R)), V.scale(V.unit(t), Math.sin(d * D2R)));
  };
  const frame2 = (x, y) => { x = V.unit(x); y = V.unit(V.reject(y, x)); return M.fromCols(x, y, V.cross(x, y)); };
  const j = V.unit(K.bvec(P.az, P.el)), T0 = V.unit(V.reject([0, 1, 0], j));
  const carried = V.add(V.scale(j, Math.cos(P.th0 * D2R)), V.scale(T0, Math.sin(P.th0 * D2R)));   // J3 home (link-1 frame)
  const a0 = gc(j, carried, P.pA0, P.dA0), b0 = gc(j, carried, P.pB0, P.dB0);
  const a1h = gc(carried, j, P.pA1, P.dA1), b1h = gc(carried, j, P.pB1, P.dB1);
  const aB = ang(b0, b1h), gC = ang(a1h, b1h), sA = Math.sign(V.dot(b1h, V.cross(b0, a1h))) || 1, E0 = frame2(a1h, b1h);
  function fbAt(th) {
    const a1 = M.mulv(M.rot(a0, th), a1h), cl = K.circInt(b0, aB, a1, gC, sA), b1 = cl.p;
    const tang = (at, to) => V.unit(V.reject(to, at));
    const muB = ang(tang(b1, b0), tang(b1, a1)), muA = ang(tang(a1, a0), tang(a1, b1));
    const mg = cl.ok ? Math.min(muA, 180 - muA, muB, 180 - muB) : -90;
    return { a1, b1, Rc: M.mul(frame2(a1, b1), M.T(E0)), mg };
  }
  // longest monotone th run inside the transmission window (the model's curve())
  const grid = []; for (let th = -180; th < 180; th += 0.25) { const f = fbAt(th), c = M.mulv(f.Rc, carried); grid.push({ th, g: ang(j, c), ok: f.mg >= P.MU }); }
  let best = { span: 0, s: 0, e: 0 };
  for (let i = 0; i < grid.length;) {
    if (!grid[i].ok) { i++; continue; }
    let k = i; while (k + 1 < grid.length && grid[k + 1].ok) k++;
    let s = i;
    while (s < k) {
      let e = s; const sg = Math.sign(grid[s + 1].g - grid[s].g);
      while (e < k && Math.sign(grid[e + 1].g - grid[e].g) === sg) e++;
      const span = Math.abs(grid[e].g - grid[s].g); if (span > best.span) best = { span, s, e };
      s = e;
    }
    i = k + 1;
  }
  let RUN = grid.slice(best.s, best.e + 1); if (RUN.length > 1 && RUN[RUN.length - 1].g < RUN[0].g) RUN = RUN.slice().reverse();
  const gLo = RUN[0].g + P.MARGIN, gHi = RUN[RUN.length - 1].g - P.MARGIN;
  function thetaOf(rho) {                               // interpolate theta on the monotone run (th ascending)
    const r = Math.max(RUN[0].g, Math.min(RUN[RUN.length - 1].g, rho));
    for (let i = 0; i < RUN.length - 1; i++) if (RUN[i + 1].g >= r) { const f = (r - RUN[i].g) / ((RUN[i + 1].g - RUN[i].g) || 1e-12); return RUN[i].th + f * (RUN[i + 1].th - RUN[i].th); }
    return RUN[RUN.length - 1].th;
  }
  const wS = ctx => M.mulv(M.T(ctx.S), M.mulv(ctx.H, K.wdir(P.wd, P.wa)));
  const near = ang(a1h, carried) <= ang(b1h, carried) ? 'A1' : 'B1';
  const gName = ang(j, a0) <= ang(j, b0) ? 'A0' : 'B0';
  function geo(q, ctx) {
    const f = fbAt(q[1]), c = M.mulv(f.Rc, carried), S = ctx.S, w = M.mulv(ctx.H, K.wdir(P.wd, P.wa));
    const SR = M.mul(S, M.rot(j, q[0])), g = u => M.mulv(SR, u);
    return { f, c, J1: M.mulv(S, j), A0: g(a0), B0: g(b0), A1: g(f.a1), B1: g(f.b1), J3: g(c), w };
  }
  function solveQ(ctx, th) {
    const f = fbAt(th), c = M.mulv(f.Rc, carried), ws = wS(ctx);
    const phi = K.axisAngle(j, c, ws), R1 = M.rot(j, phi), J3 = M.mulv(ctx.S, M.mulv(R1, c)), A1 = M.mulv(ctx.S, M.mulv(R1, f.a1));
    return [phi, th, K.axisAngle(J3, A1, ctx.armAxis)];
  }

  K.register({
    id: ID, name: NAME,
    dof: { active: 3, passive: 3 },
    params: Object.assign({ th_window: [gLo, gHi] }, P),
    q0: ctx => solveQ(ctx, thetaOf(ang(j, wS(ctx)))),
    qNames: ['J1', 'crank A (A0, the J2 drive)', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg'],
    solve: (ctx) => solveQ(ctx, thetaOf(ang(j, wS(ctx)))),
    residual: (q, ctx) => { const G = geo(q, ctx); return [ang(G.J3, G.w)]; },
    check: (q, ctx) => {
      const rho = ang(j, wS(ctx));
      if (rho < gLo || rho > gHi) return `J1-J3 angle ${rho.toFixed(0)} deg outside the knuckle window [${gLo.toFixed(0)}, ${gHi.toFixed(0)}] (5 deg th margin)`;
      const G = geo(q, ctx); if (G.f.mg < P.MU) return `transmission angle ${G.f.mg.toFixed(0)} deg (toggle)`;
      return null;
    },
    parts: (q, ctx) => partsOf(geo(q, ctx), ctx)
  });

  function partsOf(G, ctx) {
    const L = P.lv, h = P.stack, top = n => L[n] + h + 1, harm = ctx.armAxis, ng = P.neck_deg * D2R;
    const nk = V.unit(V.add(V.scale(G.w, Math.cos(ng)), V.scale(V.unit(V.reject(harm, G.w)), Math.sin(ng))));
    const neckEnd = V.scale(nk, L.J3 + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
    const pin = { A0: G.A0, B0: G.B0, A1: G.A1, B1: G.B1 }, X = pin[near], Yn = near === 'A1' ? 'B1' : 'A1', Yp = pin[Yn];
    const oName = gName === 'A0' ? 'B0' : 'A0';
    const ax = n => n === 'J1' ? G.J1 : n === 'J3' ? G.J3 : pin[n];
    const hub = (n, role, label) => ({ kind: 'hub', role, name: label, c: V.scale(ax(n), L[n]), axis: ax(n), r: P.hub_r, h });
    const arc = (role, name, u, v, r0, r1) => ({ kind: 'arc', role, name, u, v, r0, r1, r: 2.5 });
    return [
      { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(G.J1, L.J1 - 3), z: G.J1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
      hub('J1', 'active', 'J1 (O20 hub)'),
      arc('link', 'link 1 (J1 to the ground pins)', G.J1, pin[gName], top('J1'), top(gName)),
      arc('link', 'link 1 (between the ground pins)', pin[gName], pin[oName], top(gName), top(oName)),
      hub('A0', 'active', 'A0 (the J2 drive)'), hub('B0', 'passive', 'B0'),
      arc('link', 'crank A (lower ligament)', G.A0, G.A1, L.A0 + 1, L.A1 + 1),
      arc('link', 'crank B (upper ligament, crosses crank A)', G.B0, G.B1, L.B0 + 5, L.B1 + 5),
      hub('A1', 'passive', 'A1 (coupler pin)'), hub('B1', 'passive', 'B1 (coupler pin)'),
      arc('link', 'coupler (between its pins)', Yp, X, top(Yn), top(near)),
      arc('link', 'coupler (to J3)', X, G.J3, top(near), top('J3')),
      hub('J3', 'active', 'J3 (O20 hub)'),
      { kind: 'arc', role: 'fixed-arm', name: 'neck', u: G.w, v: nk, r0: L.J3 + 1, r1: L.J3 + 1, r: 3 },
      { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
      { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
      { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
    ];
  }
})();

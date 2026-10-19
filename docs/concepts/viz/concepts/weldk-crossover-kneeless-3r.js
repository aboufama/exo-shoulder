/* weldk-crossover-kneeless-3r - the kneeless welded crossover 3R (round 301, O1 overhead track; complexity 0).
 * Three O20 hubs on GH rays: J1 at the lead's acromion-top seat (az 95.39 el 67.90), J2 on a GH ray (rest seat solved
 * from the arcs a1 / a2), J3 on the GH ray wdir(wd, wa) (b3 0: its line passes through GH). The J3 stack is INVERTED:
 * link 2 on hub 3's LOWER plate, member 3 = ONE rigid Ti bracket (hub 3's upper member + the E leg, stacked over link 2
 * by the plan-view rule +0.15 mm, + the pad leg + the arm pad bolted to BOTTOM). No knee, no K, no drive, no J3 stop:
 * with all three axes through GH the cuff drift is identically 0, so member 3 moves with the arm (the model asserts it).
 * Exported from docs/concepts/models/weldk-crossover-kneeless-3r.py at its best screened configuration (sweep k82: Bench(60,160) fast 31.83, near-touch 34.18; frozen exact Bench(110,360) 37.42; pad at the end of the skin-following E leg, lc 6.3).
 * Red = the J2 fold (J1-J3 axis-angle window, 5 deg margin). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.3929, "el1": 67.8974, "az2": 26.4889, "el2": 47.0709, "wd": 108.587, "wa": 6.1136, "a1": 39.5895, "a2": 52.6183, "lE": 70.6049, "lc": 15.0, "phiE": -18.6946, "phib": -125.4093, "dg": 20.4018};
  const G = {"u":[[0.03536,0.92651,0.3746],[-0.57702,0.65836,0.48334],[0.10095,0.31874,0.94245]],"c":[[0.0,0.0,0.0],[-0.0,0.0,-0.0],[0.0,0.0,-0.0]],"sa":[0.03395,-0.94784,0.31693],"st":[0.99431,0.0,-0.1065],"sn":[0.10095,0.31874,0.94245],"A":[39.59,52.618],"branch":-1.0,"f":[50.4,63.68,62.67],"tr":53.36,"tp":3.0,"UP":3.15,"SING":5.0,"eE":[-0.28655,-0.89783,0.33435],"eK":[-0.83007,0.54919,-0.09683],"A0":[-20.232,-63.391,23.606],"Bm":[-32.683,-55.154,22.154],"L1":[[-8.19,46.14,21.21],[-9.4,43.16,20.46],[-11.14,42.97,21.0],[-12.91,42.78,21.55],[-17.67,45.18,24.18],[-20.71,47.25,26.07],[-23.95,49.14,27.95],[-27.38,50.83,29.83]],"L2":[[-36.86,47.61,47.88],[-27.57,39.63,45.78],[-22.02,34.42,43.44],[-17.84,32.53,46.76],[-14.86,30.9,48.43],[-10.59,28.91,51.7],[-7.59,27.25,53.4],[-3.12,25.68,58.15]]};
  const u = G.u, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  /** closed-form spherical 3R IK (all three lines through GH): Q = band HG -> q1, q2, fold margin */
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), c12 = V.dot(u1, u2), b1 = V.dot(w, u1), b2 = V.dot(u2, u3), det = 1 - c12 * c12;
    const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, u2);
    const g2 = (1 - al * al - be * be - 2 * al * be * c12) / V.dot(cr, cr), th = V.angle(w, u1);
    const margin = Math.min(th - Math.abs(a1 - a2), Math.min(a1 + a2, 360 - a1 - a2) - th);
    let pick = null;
    for (const sg of [1, -1]) {
      const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
      const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, z), p2 = M.mulv(M.rot(u1, q1), u2);
      const br = Math.sign(V.dot(p2, V.cross(u1, w)));
      if (pick === null || br === G.branch) pick = [q1, q2];
    }
    return { q1: pick[0], q2: pick[1], ok: margin >= G.SING && g2 > 0, margin };
  }
  function chain(q1, q2, q3) {
    const R1 = M.rot(u[0], q1), R2 = M.rot(u[1], q2), R12 = M.mul(R1, R2), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    return { R1, R12, R123 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.rot(u[0], k.q1), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref)));
    return [k.q1, k.q2, q3];
  }
  const check = (q, ctx) => {
    const k = ik(Qof(ctx));
    if (!k.ok) return k.margin < 0 ? 'J2 fold: the J1-J3 axis angle is outside the 3R window' : `J2 within ${k.margin.toFixed(0)} deg of its fold (>= ${G.SING})`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'weldk-crossover-kneeless-3r', name: 'Kneeless welded crossover 3R: rigid bracket over link 2, no knee, no K, no drive (cx 0)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: solveC,
    residual: (q, ctx) => { const X = chain(q[0], q[1], q[2]); return M.rotErrDeg(X.R123, Qof(ctx)); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), X = chain(q[0], q[1], q[2]);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const hp = (R, k) => on(R, V.scale(u[k], G.f[k]));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (O20, axis on a GH ray)', c: hp(I, 0), axis: Wd(u[0]), r: rad, h: hub };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (O20, axis on a GH ray)', c: hp(X.R1, 1), axis: Wd(M.mulv(X.R1, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (O20, axis on a GH ray, inverted stack)', c: hp(X.R12, 2), axis: Wd(M.mulv(X.R12, u[2])), r: rad, h: hub };
      const Rb = X.R123, br = p => on(Rb, p);                         // the rigid bracket moves with member 3 (= the arm)
      const lv = G.tr + G.tp / 2;
      const rim = br(V.add(V.scale(sn, G.f[2] + G.UP + 1.5), V.scale(G.eE, rad)));
      const pa = br(V.madd(G.A0, sn, lv)), pd = br(V.madd(G.Bm, sn, lv)), padN = Wd(M.mulv(Rb, sn));
      const arm = p => M.mulv(ctx.H, p);
      const lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 Ti strap, fitted)', pts: G.L1.map(p => on(X.R1, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 Ti strap on hub 3 LOWER plate, fitted)', pts: G.L2.map(p => on(X.R12, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'fixed-arm', name: 'bracket E leg (hub 3 UPPER member, stacked over link 2)', a: rim, b: pa, r: 2.5 },
        { kind: 'link', role: 'fixed-arm', name: 'bracket pad leg (same rigid Ti part)', a: pa, b: pd, r: 2.5 },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (2x M3 to BOTTOM)', c: pd, z: padN, x: Wd(M.mulv(Rb, sa)), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(pd, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();

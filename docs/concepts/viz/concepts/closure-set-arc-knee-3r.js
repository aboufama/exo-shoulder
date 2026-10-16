/* closure-set-arc-knee-3r - the leader 3R with hub 3 carried on a PASSIVE trunnion knee: link 2 ends in a fork, two
 * coaxial trunnion pins (axis dK = u2 x u3, 92.6 mm up J3's line) carry the yoke = hub 3's housing; J3 drives the E arm;
 * pin a -> cuff link -> pin b on the arm pad close the in-plane drift. 3 active, 3 passive rotations (knee, pin a, pin b),
 * 0 passive translations. The knee angle psi is set by the RADIAL closure (member 3's height along J3 above the arm,
 * rad(psi) = c0); with J1 / J2 on GH rays it would be inert, so J2's line is offset o2 = 30 mm (the cam) and b2 0.11.
 * REFUTED: 68.59 on Bench(60,160) fast (75.28 frozen on Bench(110,360)) vs 31.32 for the same chain with the knee locked;
 * the knee removes the J2 fold kinematically but lifts hub 2 (face 105.7 mm along its axis) out of band. Exactly the
 * model docs/concepts/models/closure-set-arc-knee-3r.py at rows best_params (k322): axis directions, line points, knee
 * axis, c0, dyad layout, levels and fitted link centrelines exported from its fit on Bench(60,160) (the export re-ran
 * the model: 68.59, as the row). Per frame (model rules): psi = the root of rad(psi) - c0 on a 1 deg grid over +-60 deg
 * on the rest root's flank, the one nearest the previous frame's (tracking, as the fit clips; frame 0 from psi_rest),
 * refined by secant; the spherical IK with axis 3 = RK(psi) u3; the dyad's two circles. The residual is the full-loop
 * forward kinematics from the 6 joint values. Red = no root / fold / authority < 8 mm/rad / knee at +-60 / dyad elbow. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 94.5191, "el1": 68.9031, "b1": 0.0, "az2": 19.4523, "el2": 53.3244, "b2": 0.1125, "wd": 77.5616, "wa": -20.9113, "b3": 0.173, "o2": 30.0, "chi2": -72.2636, "psi_rest": 19.3538, "pmax": 60.0, "toff": 6.5819, "lE": 40.0, "lc": 37.1893, "phiE": 2.3161, "beta0": 113.9108, "earm_over": 1, "earm_under": 0, "dh": 26.59};
  const G = {"u":[[0.028361,0.932973,0.358827],[-0.545686,0.775997,0.316315],[-0.342477,-0.139338,0.929136]],"c":[[0.0,0.0,0.0],[-26.2909,-17.1095,-3.3816],[-1.2827,-4.7901,-1.1911]],"sa":[0.04819,-0.990245,-0.130739],"st":[0.93829,-0.0,0.345851],"sn":[-0.342477,-0.139338,0.929136],"A":[34.7134,68.1203],"branch":-1.0,"dK":[0.82447,0.429633,0.368327],"cK":[-32.9882,-17.6896,84.8256],"hK":92.57711047586747,"c0":-16.66790405288995,"flank":-1.0,"a0":[39.9673,1.6165],"b0":[53.6544,36.1955],"gam0":68.40530000000001,"s_rest":[-29.1399,-12.6226],"sig":-1.0,"lE":40.0,"lc":37.1893,"phiE":2.3161,"pmax":60.0,"auth_min":8.0,"bmin":20.0,"psi_rest":19.3538,"lv":{"f1":50.195,"f2":105.701,"f3":87.306,"zE":100.458,"zc":97.258,"zp":94.058,"zf":89.577},"SING":10.0,"L1":[[-5.84,48.27,19.0],[-8.01,45.19,17.94],[-10.6,45.21,18.1],[-13.32,45.45,18.35],[-14.69,45.45,18.43],[-17.58,45.71,18.7],[-20.52,45.74,18.89],[-24.62,47.75,19.91],[-30.6,52.22,21.99],[-37.15,56.23,23.92],[-44.25,59.75,25.71],[-51.8,62.69,27.29],[-55.72,63.91,27.99],[-63.95,65.99,29.28],[-72.5,67.37,30.33],[-81.41,68.13,31.14]],"L2":[[-89.19,62.16,43.29],[-80.75,52.91,44.84],[-72.11,44.19,45.15],[-62.85,35.8,43.9],[-57.51,31.07,43.01],[-53.19,26.31,43.84],[-52.35,23.41,47.31],[-50.31,19.98,49.69],[-50.18,17.26,54.03],[-47.68,13.68,55.89],[-46.79,10.52,59.69],[-43.91,6.9,61.02],[-43.04,4.64,63.36],[-40.57,1.06,65.27],[-40.55,-2.7,71.53],[-39.08,-6.8,75.97]]};
  const u = G.u, c = G.c, sn = G.sn, sa = G.sa, st = G.st, lv = G.lv, rad = 10, hub = 12.25, TL = 3.0;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8])), a1 = G.A[0];
  const ipt = (x, y) => V.add(V.add(c[2], V.scale(sa, x)), V.scale(st, y));        // hub 3's plane coords -> home point
  /** Design.core: spherical IK with axis 3 = RK(psi) u3 (deg), the member transforms and the drift s (arm-home frame) */
  function core(Q, psi) {
    const [u1, u2, u3] = u, RK = M.rot(G.dK, psi), U3 = M.mulv(RK, u3), w = M.mulv(Q, u3), c12 = V.dot(u1, u2), c23 = V.dot(U3, u2);
    const b1 = V.dot(w, u1), det = 1 - c12 * c12, al = (b1 - c12 * c23) / det, be = (c23 - c12 * b1) / det, cr = V.cross(u1, u2);
    const g2 = (1 - al * al - be * be - 2 * al * be * c12) / V.dot(cr, cr), th = V.angle(w, u1), a2 = Math.acos(Math.max(-1, Math.min(1, c23))) / D2R;
    const margin = Math.min(th - Math.abs(a1 - a2), Math.min(a1 + a2, 360 - a1 - a2) - th);
    let pick = null;
    for (const sg of [1, -1]) {
      const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
      const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, U3, z), br = Math.sign(V.dot(M.mulv(M.rot(u1, q1), u2), V.cross(u1, w)));
      if (pick === null || br === G.branch) pick = [q1, q2];
    }
    const [q1, q2] = pick, R1 = M.rot(u1, q1), R2 = M.rot(u2, q2), R12 = M.mul(R1, R2), Ry = M.mul(R12, RK);
    const q3 = K.axisAngle(u3, vref, M.mulv(M.T(Ry), M.mulv(Q, vref))), R3 = M.rot(u3, q3);
    const t1 = V.sub(c[0], M.mulv(R1, c[0])), t2 = V.add(M.mulv(R1, V.sub(V.sub(c[1], M.mulv(R2, c[1])), c[0])), c[0]);
    const ty = V.add(M.mulv(R12, V.sub(G.cK, M.mulv(RK, G.cK))), t2), Rf = M.mul(Ry, R3), tf = V.add(M.mulv(Ry, V.sub(c[2], M.mulv(R3, c[2]))), ty);
    const s = M.mulv(M.T(Q), tf);
    return { q1, q2, q3, ok: margin >= G.SING && g2 > 0, margin, g2, s, rad: V.dot(s, u3) };
  }
  const radOf = (Q, psi) => { const k = core(Q, psi); return k.g2 > 0 ? k.rad - G.c0 : NaN; };
  /** knee root: 1 deg grid over +-pmax, flank rule, nearest to ref; secant-refined; authority |d rad / d psi| (mm/rad) */
  function root(Q, ref) {
    let best = null;
    let f0 = radOf(Q, -G.pmax);
    for (let p = -G.pmax; p < G.pmax - 1e-9; p += 1) {
      const f1 = radOf(Q, p + 1);
      if (isFinite(f0) && isFinite(f1) && f0 * f1 <= 0 && f0 !== f1 && Math.sign(f1 - f0) === G.flank) {
        let a = p, b = p + 1, fa = f0, fb = f1;
        for (let it = 0; it < 4; it++) { const x = b - fb * (b - a) / (fb - fa), fx = radOf(Q, x); if (!isFinite(fx)) break; a = b; fa = fb; b = x; fb = fx; }
        const pr = b, au = Math.abs(f1 - f0) / D2R;
        if (!best || Math.abs(pr - ref) < Math.abs(best.psi - ref)) best = { psi: pr, auth: au };
      }
      f0 = f1;
    }
    return best;
  }
  /** Design.dyad: in-plane drift -> E arm angle phi, cuff link angle gam, elbow beta (deg), pin a (plane coords) */
  function dyad(s) {
    const sx = V.dot(s, sa), sy = V.dot(s, st), vx = G.b0[0] + G.s_rest[0] - sx, vy = G.b0[1] + G.s_rest[1] - sy, d = Math.hypot(vx, vy);
    const cb = (G.lE ** 2 + G.lc ** 2 - d * d) / (2 * G.lE * G.lc), beta = Math.acos(Math.max(-1, Math.min(1, cb))) / D2R;
    const ca = (G.lE ** 2 + d * d - G.lc ** 2) / (2 * G.lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca))) / D2R;
    const phi = Math.atan2(vy, vx) / D2R + G.sig * al, pa = [G.lE * Math.cos(phi * D2R), G.lE * Math.sin(phi * D2R)];
    const gam = Math.atan2(vy - pa[1], vx - pa[0]) / D2R;
    return { phi, gam, beta, ok: Math.abs(cb) <= 1 && beta >= G.bmin && beta <= 180 - G.bmin };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solveAll(ctx, qPrev) {
    const Q = Qof(ctx), ref = qPrev && isFinite(qPrev[2]) ? qPrev[2] : G.psi_rest, r = root(Q, ref);
    const psi = r ? r.psi : (qPrev ? qPrev[2] : G.psi_rest), k = core(Q, psi), dy = dyad(k.s), W = K.wrap180;
    const q = [k.q1, k.q2, psi, W(k.q3 + dy.phi - G.phiE), W((dy.gam - G.gam0) - (dy.phi - G.phiE)), W(dy.gam - G.gam0)];
    return { q, r, k, dy };
  }
  // the loop's forward kinematics from [J1, J2, knee psi, J3, pin a, pin b] (home coordinates of each member as the model's T)
  const A0 = ipt(G.a0[0], G.a0[1]), B0 = ipt(G.b0[0], G.b0[1]), Barm = V.madd(ipt(G.b0[0] + G.s_rest[0], G.b0[1] + G.s_rest[1]), sn, G.c0);
  function fk(q) {
    const R1 = M.rot(u[0], q[0]), R2 = M.rot(u[1], q[1]), R12 = M.mul(R1, R2), RK = M.rot(G.dK, q[2]), Ry = M.mul(R12, RK);
    const t1 = V.sub(c[0], M.mulv(R1, c[0])), t2 = V.add(M.mulv(R1, V.sub(V.sub(c[1], M.mulv(R2, c[1])), c[0])), c[0]);
    const ty = V.add(M.mulv(R12, V.sub(G.cK, M.mulv(RK, G.cK))), t2);
    const R3 = M.rot(u[2], q[3]), R4 = M.mul(Ry, R3), t4 = V.add(M.mulv(Ry, V.sub(c[2], M.mulv(R3, c[2]))), ty);   // E arm (J3 output)
    const pa = V.add(M.mulv(R4, A0), t4), R6 = M.mul(R4, M.rot(u[2], q[4])), t6 = V.sub(pa, M.mulv(R6, A0));
    const pb = V.add(M.mulv(R6, B0), t6), R5 = M.mul(R6, M.rot(u[2], -q[5])), t5 = V.sub(pb, M.mulv(R5, Barm));
    return { R1, t1, R12, t2, Ry, ty, R4, t4, R6, t6, R5, t5, pa, pb };
  }
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  /** unreachable frames (no root, fold) are drawn at the least-squares nearest configuration from the previous frame */
  const solve = (ctx, qPrev) => { const q = solveAll(ctx, qPrev).q; return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'closure-set-arc-knee-3r', name: 'Closure-set arc knee 3R: hub 3 on a passive trunnion knee + pinned cuff dyad (refuted)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solveAll(ctx, null).q,
    qNames: ['J1', 'J2', 'knee (trunnion)', 'J3', 'pin a', 'pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check: (q, ctx) => {
      const Q = Qof(ctx), r = root(Q, q[2]);
      if (!r) return 'knee: no radial-closure root on its flank';
      const k = core(Q, r.psi);
      if (!k.ok) return k.margin < 0 ? 'J2 fold' : `J2 within ${k.margin.toFixed(0)} deg of its fold (>= ${G.SING})`;
      if (r.auth < G.auth_min) return `knee authority ${r.auth.toFixed(1)} mm/rad < ${G.auth_min}`;
      if (Math.abs(r.psi) > G.pmax - 0.5) return 'knee at its +-60 deg stop';
      if (!dyad(k.s).ok) return 'cuff dyad elbow out of its window';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q), I = M.I3();
      const on = (R, t, p) => W(V.add(M.mulv(R, p), t));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.madd(c[0], u[0], lv.f1)), axis: Wd(u[0]), r: rad, h: hub };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (line offset 30 mm: the cam)', c: on(F.R1, F.t1, V.madd(c[1], u[1], lv.f2)), axis: Wd(M.mulv(F.R1, u[1])), r: rad, h: hub,
                   p0: on(F.R1, F.t1, c[1]) };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (on the yoke, line misses GH)', c: on(F.Ry, F.ty, V.madd(c[2], u[2], lv.f3)), axis: Wd(M.mulv(F.Ry, u[2])), r: rad, h: hub,
                   p0: on(F.Ry, F.ty, c[2]) };
      const kd = Wd(M.mulv(F.R12, G.dK)), n3 = Wd(M.mulv(F.R4, sn)), off = rad + 1.75;
      const tr1 = on(F.R12, F.t2, V.madd(G.cK, G.dK, off)), tr2 = on(F.R12, F.t2, V.madd(G.cK, G.dK, -off));
      // fork: half ring round hub 3 at the cheek level (link 2's frame), from the link-2 end
      const bh0 = V.sub(V.madd(c[1], u[1], 60), c[2]), bh = V.unit(V.reject(bh0, u[2])), dK2 = V.unit(V.reject(G.dK, bh)), fork = [];
      for (let a = -90; a <= 90; a += 15) fork.push(on(F.R12, F.t2, V.madd(V.add(c[2], V.add(V.scale(bh, 15 * Math.cos(a * D2R)), V.scale(dK2, 15 * Math.sin(a * D2R)))), u[2], G.hK)));
      const arm = p => M.mulv(ctx.H, p), padN = M.mulv(ctx.H, sn);
      const pinA = (h) => V.madd(W(F.pa), n3, h), pinB = h => arm(V.madd(Barm, sn, h - G.c0));
      const padC = pinB(lv.zp + 1.5);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 strap, fitted)', pts: G.L1.map(p => on(F.R1, F.t1, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted, to the fork)', pts: G.L2.map(p => on(F.R12, F.t2, p)), r: 2.5 },
        { kind: 'arc', role: 'link', name: 'fork (link 2) round the yoke', pts: fork, r: 2 },
        { kind: 'hub', role: 'passive', name: 'knee trunnion 1 (axis u2 x u3)', c: tr1, axis: kd, r: 3, h: 3, p0: tr1 },
        { kind: 'hub', role: 'passive', name: 'knee trunnion 2', c: tr2, axis: V.scale(kd, -1), r: 3, h: 3, p0: tr2 },
        h3,
        { kind: 'link', role: 'link', name: 'E arm (J3 output)', a: on(F.R4, F.t4, V.madd(V.madd(c[2], V.unit(V.sub(A0, c[2])), rad), sn, lv.zE + 1.5)),
          b: pinA(lv.zE + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'pin a (parallel to J3)', c: pinA(lv.zc), axis: n3, r: 5, h: lv.zE - lv.zc + TL, p0: pinA(lv.zc) },
        { kind: 'link', role: 'link', name: 'cuff link', a: pinA(lv.zc + 1.5), b: pinB(lv.zc + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'pin b (parallel to J3, on the pad)', c: pinB(lv.zp), axis: padN, r: 5, h: lv.zc - lv.zp + TL, p0: pinB(lv.zp) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad boss (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [10, 10], t: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: arm([Barm[0], -150, 50]), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();

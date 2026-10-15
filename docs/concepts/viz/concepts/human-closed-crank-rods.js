/* human-closed-crank-rods - a human-closed 3-RUS truss (catalogue human-closed-crank-rods, models/human-closed-crank-rods.py
 * PARAMS; no sweep yet). Three ACTIVE crank hubs on the dome, axes c_k THROUGH GH (bvec(60,75) acromion top,
 * bvec(-10,40) spine root, bvec(150,40) clavicle end), crank arc beta 35 deg so each tip T rides a circle; a passive
 * U-joint at T (2) -> a thin rigid O5 rod -> a passive ball (3) on an arm stud (leg 1 on BOTTOM's bar 80 mm down, legs
 * 2 / 3 on a saddle posterolateral +45 deg at 110 mm and anterolateral -15 deg at 100 mm). NO exo joint at GH: the
 * wearer's own shoulder closes the loop. Per leg the closed form A cos th + B sin th = C on a fixed branch; the rod
 * length L_k is picked (as the model's stab_L) to keep the most loop frames closed with transmission >= 15 deg.
 * 3 ACTIVE (crank angles) + 15 PASSIVE (2 U + 3 ball per leg, all set by the arm). Hub faces are schematic (dome skin
 * 45-60 mm + clearance); the model fits them. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { hubs: [[60, 75], [-10, 40], [150, 40]], beta: [35, 35, 35], sigma: [1, 1, 1], faces: [50, 60, 58],
              s1: 80, h1: 8, studs: [[110, 45], [100, -15]], skin: 52, sad_t: 4, h_stud: 7, trans: 15, det: 0.10,
              hub_r: 10, stack: 12.25 };
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713], BAR_Z = 67.5;
  // arm frame in bind coords (models: A_AX humerus axis, Z_L lateral, Y_L posterior); arm points map by ctx.Hb
  const AX = V.unit(K.BODY.elbow), ZL = V.unit(V.reject(M.col(K.BODY.rest_humerus, 2), AX)), YL = V.cross(AX, ZL);
  const armPt = (s, th, r) => V.add(V.scale(AX, s), V.add(V.scale(ZL, r * Math.cos(th * D2R)), V.scale(YL, r * Math.sin(th * D2R))));
  const rStud = P.skin + P.sad_t + P.h_stud;
  const q = [V.add(V.scale(WB, BAR_Z + P.h1), V.scale(DB, P.s1)), armPt(P.studs[0][0], P.studs[0][1], rStud),
             armPt(P.studs[1][0], P.studs[1][1], rStud)];
  const legs = P.hubs.map(([az, el], k) => {
    const c = V.unit(K.bvec(az, el)), a = Math.abs(c[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0];
    const e1 = V.unit(V.reject(a, c)), e2 = V.cross(c, e1), rT = P.faces[k] + 3.15 + 3 + 6 + 1, b = P.beta[k] * D2R;
    return { c, e1, e2, rT, O: V.scale(c, rT * Math.cos(b)), rho: rT * Math.sin(b), q: q[k], sigma: P.sigma[k], L: 0 };
  });
  const tip = (g, S, th) => M.mulv(S, V.add(g.O, V.add(V.scale(g.e1, g.rho * Math.cos(th * D2R)), V.scale(g.e2, g.rho * Math.sin(th * D2R)))));
  function legSolve(g, ctx, L) {                       // closed form on the leg's branch; ok false when the circle misses
    const O = M.mulv(ctx.S, g.O), E1 = M.mulv(ctx.S, g.e1), E2 = M.mulv(ctx.S, g.e2), Q = M.mulv(ctx.Hb, g.q), OQ = V.sub(O, Q);
    const A = 2 * g.rho * V.dot(E1, OQ), B = 2 * g.rho * V.dot(E2, OQ), C = L * L - V.dot(OQ, OQ) - g.rho * g.rho, R = Math.hypot(A, B);
    const x = C / (R || 1e-9);
    return { th: (Math.atan2(B, A) + g.sigma * Math.acos(Math.max(-1, Math.min(1, x)))) * K.R2D, ok: Math.abs(x) <= 1 };
  }
  function trans(g, ctx, th) {                         // |cos angle(dT/dth, rod)|: 0 at the crank's dead centre
    const T = tip(g, ctx.S, th), dT = V.sub(tip(g, ctx.S, th + 0.5), tip(g, ctx.S, th - 0.5)), Q = M.mulv(ctx.Hb, g.q);
    return Math.abs(Math.cos(V.angle(dT, V.sub(Q, T)) * D2R));
  }
  // rod lengths: the value that keeps the most loop frames closed with transmission >= trans (model stab_L)
  const frames = K.motion(90).map(f => K.makeCtx(f.pose, f.t));
  legs.forEach(g => {
    const d = frames.map(ctx => V.norm(V.sub(M.mulv(ctx.Hb, g.q), tip(g, ctx.S, 0))));
    let best = -1;
    for (let L = Math.min(...d) - 40; L <= Math.max(...d) + 40; L += 1) {
      let n = 0;
      for (const ctx of frames) { const s = legSolve(g, ctx, L); if (s.ok && trans(g, ctx, s.th) >= Math.sin(P.trans * D2R)) n++; }
      if (n > best) { best = n; g.L = L; }
    }
  });
  const detOf = (ctx, th) => {
    const m = legs.map((g, k) => V.unit(V.cross(tip(g, ctx.S, th[k]), M.mulv(ctx.Hb, g.q))));
    return Math.abs(V.dot(m[0], V.cross(m[1], m[2])));
  };

  K.register({
    id: 'human-closed-crank-rods',
    name: 'Human-closed crank-rod truss (3-RUS)',
    dof: { active: 3, passive: 15 },
    params: Object.assign({ L: legs.map(g => +g.L.toFixed(1)) }, P),
    q0: ctx => legs.map(g => legSolve(g, ctx, g.L).th),
    qNames: ['crank 1 (top)', 'crank 2 (spine)', 'crank 3 (clavicle)'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['mm', 'mm', 'mm'],
    solve: ctx => legs.map(g => legSolve(g, ctx, g.L).th),
    residual: (q, ctx) => legs.map((g, k) => V.norm(V.sub(M.mulv(ctx.Hb, g.q), tip(g, ctx.S, q[k]))) - g.L),
    check: (q, ctx) => {
      for (let k = 0; k < 3; k++) if (trans(legs[k], ctx, q[k]) < Math.sin(P.trans * D2R)) return `crank ${k + 1} near its dead centre`;
      if (detOf(ctx, q) < P.det) return 'rods near a line singularity (moments about GH coplanar)';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, h = P.stack, out = [];
      const hubC = legs.map((g, k) => M.mulv(S, V.scale(g.c, P.faces[k])));
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base bracket (top - spine)', u: M.mulv(S, legs[0].c), v: M.mulv(S, legs[1].c), r0: P.faces[0] - 2, r1: P.faces[1] - 2, r: 3 });
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base bracket (top - clavicle)', u: M.mulv(S, legs[0].c), v: M.mulv(S, legs[2].c), r0: P.faces[0] - 2, r1: P.faces[2] - 2, r: 3 });
      legs.forEach((g, k) => {
        const T = tip(g, S, q[k]), Q = M.mulv(ctx.Hb, g.q), ax = M.mulv(S, g.c), rr = P.faces[k] + 4.6;
        out.push({ kind: 'hub', role: 'active', name: `crank hub ${k + 1}`, c: hubC[k], axis: ax, r: P.hub_r, h });
        out.push({ kind: 'arc', role: 'link', name: `crank ${k + 1}`, u: ax, v: V.unit(T), r0: rr, r1: rr, r: 3 });
        out.push({ kind: 'hub', role: 'passive', name: `U-joint ${k + 1}`, c: V.madd(T, V.unit(T), -4), axis: V.unit(T), r: 6, h: 8 });
        out.push({ kind: 'link', role: 'link', name: `rod ${k + 1}`, a: T, b: Q, r: 2.5 });
        out.push({ kind: 'point', role: 'passive', name: `ball ${k + 1}`, p: Q, r: 6 });
        const foot = k === 0 ? V.add(V.scale(WB, BAR_Z + 6), V.scale(DB, P.s1)) : armPt(P.studs[k - 1][0], P.studs[k - 1][1], P.skin + P.sad_t);
        out.push({ kind: 'link', role: 'fixed-arm', name: `stud ${k + 1}`, a: M.mulv(ctx.Hb, foot), b: Q, r: 3.5 });
      });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm saddle', c: M.mulv(ctx.Hb, V.scale(AX, 105)), axis: ctx.armAxis, r: P.skin + 2, w: 14 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar (user part)', a: M.mulv(ctx.Hb, V.add(V.scale(WB, BAR_Z + 3), V.scale(DB, 40))),
                 b: M.mulv(ctx.Hb, V.add(V.scale(WB, BAR_Z + 3), V.scale(DB, 170))), r: 4 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre (the wearer\'s joint closes the loop)', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();

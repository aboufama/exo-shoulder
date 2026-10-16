/* coaxial-rus-turret - KILLED: the human-closed 3-RUS truss with all three ACTIVE crank bearings STACKED on ONE O20 hub
 * shaft at one posterior-horizontal scapula seat (a coaxial-input spherical parallel mechanism whose platform is the
 * user's humerus and whose centre is the user's GH; docs/concepts/coaxial-rus-turret.md, models/coaxial-rus-turret.py
 * = models/human-closed-crank-rods.py + the foldfree-rus-truss / coaxial patches). Drawn at the row's best_params
 * (sweeps k2, the honest full-model config: gap 275.0, 0 poses taken): seat bvec(-24, 4) for all three cranks, crank
 * arcs beta 70 / 65 / 60 deg, branch sigma -1 on every leg, three own saddle studs (studs3) at (s, theta) = (10, 90),
 * (10, 150), (0, 105) (s mm down the arm, theta from lateral toward posterior, the model's rest-arm frame mapped by
 * ctx.Hb), fit percentile 90. Logged fitted sizes: crank tip radius r_T 94.3 / 230 / 234.5 mm (cranks 2 / 3 at the
 * 220 mm march ceiling: they found no clearance), hub face 106.9 + one 4.5 mm layer per crank (stack 21.25 mm).
 * Crank k: tip T = r_T (cos beta c + sin beta (cos th e1 + sin th e2)) in the scapula frame; per leg the closed form
 * A cos th + B sin th = C on the leg's branch. A passive U-joint at T (2) -> an O5 rod -> a passive ball (3) on the arm
 * stud. NO exo joint at GH: the wearer's shoulder closes the loop. Schematic here (not logged by the row): the saddle's
 * fitted radius (60 mm skin + 4 saddle + 7 stud = ball 71 mm off the arm line; the legs are sensitive to it: their studs
 * sit near the crank axis line) and therefore the rod lengths, re-picked by the model's own rule (stab_L: the length
 * keeping the most loop frames closed with transmission >= 15 deg; logged at the bench: 149 / 213 / 202); rods are
 * drawn straight (the model fits a bow). 3 ACTIVE (crank angles) + 15 PASSIVE rotations (2 U + 3 ball per leg, all set
 * by the arm), 0 passive translations. Red frames: a leg that cannot close, a crank at its dead centre, or the
 * parallel singularity (|det| of the three moment lines < 0.10) - the turret's measured killer. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { seat: [-24, 4], beta: [70, 65, 60], sigma: [-1, -1, -1], studs: [[10, 90], [10, 150], [0, 105]], p: 90,
              rT: [94.3, 230.0, 234.5], F0: 106.9, layer: 4.5, stack: 21.25, hub_r: 10, skin: 60, sad_t: 4, h_stud: 7,
              trans: 15, det: 0.10, L_logged: [149.0, 213.0, 202.0] };
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713], BAR_Z = 67.5;   // BOTTOM bar (user part) in rest-arm coords
  const c = V.unit(K.bvec(P.seat[0], P.seat[1])), aa = Math.abs(c[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0];
  const e1 = V.unit(V.reject(aa, c)), e2 = V.cross(c, e1);
  const nq = th => [-Math.sin(th * D2R), 0, Math.cos(th * D2R)];
  const legs = [0, 1, 2].map(k => {
    const b = P.beta[k] * D2R, rT = P.rT[k], [s, th] = P.studs[k];
    return { k, rT, O: V.scale(c, rT * Math.cos(b)), rho: rT * Math.sin(b), sigma: P.sigma[k], s, th,
             q: null, L: 0, skin: 0, F: P.F0 + k * P.layer };
  });
  const tip = (g, S, th) => M.mulv(S, V.add(g.O, V.add(V.scale(e1, g.rho * Math.cos(th * D2R)), V.scale(e2, g.rho * Math.sin(th * D2R)))));
  function legSolve(g, ctx, L) {
    const O = M.mulv(ctx.S, g.O), E1 = M.mulv(ctx.S, e1), E2 = M.mulv(ctx.S, e2), Q = M.mulv(ctx.Hb, g.q), OQ = V.sub(O, Q);
    const A = 2 * g.rho * V.dot(E1, OQ), B = 2 * g.rho * V.dot(E2, OQ), C = L * L - V.dot(OQ, OQ) - g.rho * g.rho, R = Math.hypot(A, B);
    const x = C / (R || 1e-9);
    return { th: (Math.atan2(B, A) + g.sigma * Math.acos(Math.max(-1, Math.min(1, x)))) * K.R2D, ok: Math.abs(x) <= 1 };
  }
  function trans(g, ctx, th) {                         // |cos angle(dT/dth, rod)|: 0 at the crank's dead centre
    const T = tip(g, ctx.S, th), dT = V.sub(tip(g, ctx.S, th + 0.5), tip(g, ctx.S, th - 0.5)), Q = M.mulv(ctx.Hb, g.q);
    return Math.abs(Math.cos(V.angle(dT, V.sub(Q, T)) * D2R));
  }
  // rod lengths: the model's stab_L on the preview loop (the length keeping the most frames closed with transmission
  // >= 15 deg on the leg's branch), with the schematic saddle radius
  const frames = K.motion(90).map(f => K.makeCtx(f.pose, f.t));
  legs.forEach(g => {
    g.skin = P.skin; g.q = V.add([0, -g.s, 0], V.scale(nq(g.th), g.skin + P.sad_t + P.h_stud));
    const d = frames.map(ctx => V.norm(V.sub(M.mulv(ctx.Hb, g.q), M.mulv(ctx.S, g.O))));
    let best = -1, run = [];
    for (let L = Math.max(5, Math.floor(Math.min(...d) - g.rho)); L <= Math.ceil(Math.max(...d) + g.rho); L += 1) {
      let n = 0;
      for (const ctx of frames) { const s = legSolve(g, ctx, L); if (s.ok && trans(g, ctx, s.th) >= Math.sin(P.trans * D2R)) n++; }
      if (n > best) { best = n; run = [L]; } else if (n === best) run.push(L);
    }
    g.L = run[Math.floor(run.length / 2)];
  });
  const detOf = (ctx, th) => {
    const m = legs.map((g, k) => V.unit(V.cross(tip(g, ctx.S, th[k]), M.mulv(ctx.Hb, g.q))));
    return Math.abs(V.dot(m[0], V.cross(m[1], m[2])));
  };

  K.register({
    id: 'coaxial-rus-turret',
    name: 'Coaxial RUS turret (3 stacked cranks, 1 seat)',
    dof: { active: 3, passive: 15 },
    params: Object.assign({ L_preview: legs.map(g => g.L) }, P),
    q0: ctx => legs.map(g => legSolve(g, ctx, g.L).th),
    qNames: ['crank 1 (bottom layer)', 'crank 2', 'crank 3 (top layer)'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['mm', 'mm', 'mm'],
    solve: (ctx, qp) => legs.map((g, k) => { const th = legSolve(g, ctx, g.L).th; return qp ? qp[k] + K.wrap180(th - qp[k]) : th; }),
    residual: (q, ctx) => legs.map((g, k) => V.norm(V.sub(M.mulv(ctx.Hb, g.q), tip(g, ctx.S, q[k]))) - g.L),
    check: (q, ctx) => {
      for (let k = 0; k < 3; k++) if (trans(legs[k], ctx, q[k]) < Math.sin(P.trans * D2R)) return `crank ${k + 1} near its dead centre`;
      if (detOf(ctx, q) < P.det) return 'parallel singularity: the three rods\' moment lines about GH near coplanar';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, ax = M.mulv(S, c), out = [];
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'seat (scapula handler)', c: V.scale(ax, P.F0 - 3), z: ax, x: M.mulv(S, e1), size: [40, 30], t: 3 });
      out.push({ kind: 'hub', role: 'active', name: 'coaxial hub: 3 stacked crank bearings', c: V.scale(ax, P.F0), axis: ax, r: P.hub_r, h: P.stack });
      legs.forEach((g, k) => {
        const T = tip(g, S, q[k]), Q = M.mulv(ctx.Hb, g.q), rr = g.F + 3.15;
        out.push({ kind: 'arc', role: 'link', name: `crank ${k + 1} (layer ${k + 1})`, u: ax, v: V.unit(T), r0: rr, r1: g.rT - 7, r: 3 });
        out.push({ kind: 'hub', role: 'passive', name: `U-joint ${k + 1}`, c: V.madd(T, V.unit(T), -4), axis: V.unit(T), p0: T, r: 6, h: 8 });
        const E = V.madd(T, V.unit(V.sub(Q, T)), g.L);     // the rod keeps its length: a leg that cannot close shows the gap
        out.push({ kind: 'link', role: 'link', name: `rod ${k + 1} (O5)`, a: T, b: E, r: 2.5 });
        out.push({ kind: 'point', role: 'passive', name: `ball ${k + 1}`, p: E, r: 6 });
        out.push({ kind: 'link', role: 'fixed-arm', name: `stud ${k + 1}`, a: M.mulv(ctx.Hb, V.add([0, -g.s, 0], V.scale(nq(g.th), g.skin + P.sad_t))), b: Q, r: 3.5 });
        const ext = (7 + 1) / 50 / D2R;
        out.push({ kind: 'strap', role: 'fixed-arm', name: `saddle ${k + 1}`, c: M.mulv(ctx.Hb, [0, -g.s, 0]), axis: M.mulv(ctx.Hb, [0, -1, 0]),
                   ref: M.mulv(ctx.Hb, [0, 0, 1]), a0: Math.min(0, g.th) - ext, a1: Math.max(0, g.th) + ext, r: g.skin + 2, w: 14 });
      });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar (user part)', a: M.mulv(ctx.Hb, V.add(V.scale(WB, BAR_Z + 3), V.scale(DB, 40))),
                 b: M.mulv(ctx.Hb, V.add(V.scale(WB, BAR_Z + 3), V.scale(DB, 170))), r: 4 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre (the wearer\'s joint closes the loop)', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();

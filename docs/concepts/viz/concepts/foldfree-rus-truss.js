/* foldfree-rus-truss - KILLED: the human-closed 3-RUS truss (three ACTIVE crank hubs on the scapula, three O5 rods to
 * ball studs on the arm, the wearer's own GH as the closing spherical joint) with every leg seeded from the fold-free
 * seat-stud pairs (docs/concepts/foldfree-rus-truss.md, models/foldfree-rus-truss.py = models/human-closed-crank-rods.py
 * + the studs3 patch). The fold lever works PER LEG (each leg closed by GH is a spherical RRR with its own fold band);
 * the truss dies on crank parking, the parallel singularity and part count. Drawn at the row's best_params (sweeps k0,
 * honest full model: gap 275.0, 0 poses taken): crank hubs bvec(-24, 4) / bvec(-42, 20) / bvec(-10, 40) (posterior
 * scapula), crank arcs beta 65 / 65 / 70 deg, branch sigma +1 on every leg, three own saddle studs (studs3) at (s, theta)
 * = (10, 105), (10, 150), (0, 150) (s mm down the arm, theta from lateral toward posterior, rest-arm frame mapped by
 * ctx.Hb), fit percentile 100. Logged fitted sizes: hub faces 110.1 / 148.4 / 73.9 mm, crank tip radius r_T 230 on all
 * three (the 220 mm march ceiling: the cranks found no clearance), base brackets on the two shortest hub-hub edges.
 * Crank k: tip T = r_T (cos beta c_k + sin beta (cos th e1 + sin th e2)) in the scapula frame; per leg the closed form
 * A cos th + B sin th = C on the leg's branch; a passive U-joint at T (2) -> O5 rod -> passive ball (3) on the stud.
 * NO exo joint at GH. Schematic here (not logged by the row): the saddle's fitted radius (60 mm skin + 4 saddle + 7
 * stud = ball 71 mm off the arm line) and therefore the rod lengths, re-picked by the model's own rule (stab_L on the
 * preview loop; logged at the bench: 212 / 212 / 236); rods drawn straight (the model fits a bow). 3 ACTIVE (crank
 * angles) + 15 PASSIVE rotations (2 U + 3 ball per leg), 0 passive translations. Red frames: a leg that cannot close,
 * a crank at its dead centre, or the parallel singularity (|det| of the three moment lines < 0.10). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { hubs: [[-24, 4], [-42, 20], [-10, 40]], beta: [65, 65, 70], sigma: [1, 1, 1], studs: [[10, 105], [10, 150], [0, 150]],
              p: 100, rT: [230.0, 230.0, 230.0], F: [110.1, 148.4, 73.9], stack: 12.25, hub_r: 10, skin: 60, sad_t: 4, h_stud: 7,
              trans: 15, det: 0.10, L_logged: [212.0, 212.0, 236.0] };
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713], BAR_Z = 67.5;   // BOTTOM bar (user part) in rest-arm coords
  const nq = th => [-Math.sin(th * D2R), 0, Math.cos(th * D2R)];
  const legs = [0, 1, 2].map(k => {
    const c = V.unit(K.bvec(P.hubs[k][0], P.hubs[k][1])), aa = Math.abs(c[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0];
    const e1 = V.unit(V.reject(aa, c)), e2 = V.cross(c, e1);
    const b = P.beta[k] * D2R, rT = P.rT[k], [s, th] = P.studs[k];
    return { k, c, e1, e2, rT, O: V.scale(c, rT * Math.cos(b)), rho: rT * Math.sin(b), sigma: P.sigma[k], s, th,
             q: null, L: 0, skin: 0, F: P.F[k] };
  });
  // base brackets (model): S-fixed 12 x 3 straps on the two shortest great-circle edges between the hubs
  const brackets = [[0, 1], [0, 2], [1, 2]].map(([a, b]) => [V.angle(legs[a].c, legs[b].c), a, b]).sort((x, y) => x[0] - y[0]).slice(0, 2);
  const tip = (g, S, th) => M.mulv(S, V.add(g.O, V.add(V.scale(g.e1, g.rho * Math.cos(th * D2R)), V.scale(g.e2, g.rho * Math.sin(th * D2R)))));
  function legSolve(g, ctx, L) {
    const O = M.mulv(ctx.S, g.O), E1 = M.mulv(ctx.S, g.e1), E2 = M.mulv(ctx.S, g.e2), Q = M.mulv(ctx.Hb, g.q), OQ = V.sub(O, Q);
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
    id: 'foldfree-rus-truss',
    name: 'Fold-free RUS truss (3 crank hubs, GH-closed)',
    dof: { active: 3, passive: 15 },
    params: Object.assign({ L_preview: legs.map(g => g.L) }, P),
    q0: ctx => legs.map(g => legSolve(g, ctx, g.L).th),
    qNames: ['crank 1 (bvec -24, 4)', 'crank 2 (bvec -42, 20)', 'crank 3 (bvec -10, 40)'], qUnits: ['deg', 'deg', 'deg'],
    resUnits: ['mm', 'mm', 'mm'],
    solve: (ctx, qp) => legs.map((g, k) => { const th = legSolve(g, ctx, g.L).th; return qp ? qp[k] + K.wrap180(th - qp[k]) : th; }),
    residual: (q, ctx) => legs.map((g, k) => V.norm(V.sub(M.mulv(ctx.Hb, g.q), tip(g, ctx.S, q[k]))) - g.L),
    check: (q, ctx) => {
      for (let k = 0; k < 3; k++) if (trans(legs[k], ctx, q[k]) < Math.sin(P.trans * D2R)) return `crank ${k + 1} near its dead centre`;
      if (detOf(ctx, q) < P.det) return 'parallel singularity: the three rods\' moment lines about GH near coplanar';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, out = [];
      brackets.forEach(([, a, b]) => out.push({ kind: 'arc', role: 'fixed-scapula', name: `base bracket (hub ${a + 1} - hub ${b + 1})`,
        u: M.mulv(S, legs[a].c), v: M.mulv(S, legs[b].c), r0: legs[a].F - 2, r1: legs[b].F - 2, r: 3 }));
      legs.forEach((g, k) => {
        const T = tip(g, S, q[k]), Q = M.mulv(ctx.Hb, g.q), rr = g.F + 3.15, ax = M.mulv(S, g.c);
        out.push({ kind: 'hub', role: 'active', name: `crank hub ${k + 1}`, c: V.scale(ax, g.F), axis: ax, r: P.hub_r, h: P.stack });
        out.push({ kind: 'arc', role: 'link', name: `crank ${k + 1}`, u: ax, v: V.unit(T), r0: rr, r1: g.rT - 7, r: 3 });
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

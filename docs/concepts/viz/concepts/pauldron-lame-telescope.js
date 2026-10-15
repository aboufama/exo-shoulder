/* pauldron-lame-telescope - lobster-tail lames as a remote-centre J2 (catalogue pauldron-lame-telescope; no model /
 * sweep yet, so the catalogue's seed axes). Spherical 3R with a12 = a23 = 90 deg and NO J2 hub: J1 ACTIVE O20 hub on
 * the exo-scapula top (a1 = bvec(15, 80)) -> lame 0 -> N - 2 = 2 PASSIVE intermediate lames, each held at an equal share
 * k / (N - 1) of the extension by the coupling -> lame N - 1 -> J3 ACTIVE O20 hub at the arm's low-motion spot just
 * under the acromion edge (a3 = wdir(112, -15)). J2 ACTIVE = the stack's total extension theta = angle(A1, A3), a
 * remote-centre rotation about a2 = A1 x A3 (the lames slide on each other along circular tracks about a2). Lame k covers
 * lambda in [k (theta - Lam) / (N - 1), + Lam] from A1 toward A3 (N 4, Lam 45 deg, 28 mm wide, 3 mm thick, radii rising
 * one lame thickness toward the arm, like the skin). Closed form (KIN.sph3r, 90 / 90). With the seed axes the loop's
 * theta runs 6-89 deg, below the stack's shortest length Lam + 2 asin(12 / rho) ~ 73 deg in most poses: the check
 * reports it (the lames would ride over the J1 hub) - a sweep has to move a1 / a3 or shorten the lames. A kinematic-only
 * scan over the loop (a1 az -90..150 / el 30..90, a3 d 60..130 / a -120..120, N 4-5) finds theta-feasible pairs only
 * with J3 off the lateral arm (e.g. a1 bvec(60, 70) + a3 wdir(80, 120), anterior-medial, Lam <= 55 deg). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { a1: [15, 80], a3: [112, -15], N: 4, Lam: 45, ov: 0.3, hw: 14, tl: 3, rho0: 46, tab: [-20, 45], branch: 1,
              hub_r: 10, stack: 12.25, bar_end: [0, -70, 67.5] };
  const C = K.sph3r(K.bvec(P.a1[0], P.a1[1]), K.wdir(P.a3[0], P.a3[1]), 90, 90, P.branch), N = P.N, Lam = P.Lam;
  const rhoL = P.rho0 + 3.15, rk = k => rhoL + k * P.tl;
  const thMax = Lam * (1 + (N - 1) * (1 - P.ov)), thMin = Lam + 2 * Math.asin(12 / rhoL) / D2R;
  const theta = ctx => V.angle(M.mulv(ctx.S, C.u1), M.mulv(ctx.H, C.u3));

  K.register({
    id: 'pauldron-lame-telescope',
    name: 'Pauldron lame telescope (remote-centre J2)',
    dof: { active: 3, passive: 2 },
    params: Object.assign({ theta_range: [+thMin.toFixed(1), +thMax.toFixed(1)] }, P),
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2 (lame stack extension, remote axis a2)', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const th = theta(ctx);
      if (th < 25) return 'J1 and J3 nearly coaxial (wrist singularity)';
      if (th < thMin) return 'lames telescoped onto the hubs (stack shorter than one lame)';
      if (th > thMax || th > 155) return 'lames over-extended (overlap below 30 %)';
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), A1 = f.p1, A3 = f.p3, th = V.angle(A1, A3), out = [];
      const a2 = V.unit(V.cross(A1, A3)), e = V.unit(V.cross(a2, A1));
      const dir = lam => V.add(V.scale(A1, Math.cos(lam * D2R)), V.scale(e, Math.sin(lam * D2R)));
      const tab = M.mulv(ctx.S, K.bvec(P.tab[0], P.tab[1])), tabEnd = V.unit(V.add(V.scale(A1, Math.cos(0.5)), V.scale(V.unit(V.reject(tab, A1)), Math.sin(0.5))));
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base pad tab to the scapula handler', u: A1, v: tabEnd, r0: P.rho0 - 2, r1: P.rho0 - 2, r: 4 });
      out.push({ kind: 'hub', role: 'active', name: 'J1', c: V.scale(A1, P.rho0), axis: A1, r: P.hub_r, h: P.stack });
      for (let k = 0; k < N; k++) {
        const lk = k * (th - Lam) / (N - 1), role = k === 0 || k === N - 1 ? 'link' : 'passive';
        out.push({ kind: 'strap', role, name: k === 0 ? 'lame 0 (on J1)' : k === N - 1 ? `lame ${k} (on J3)` : `lame ${k} (passive share ${k}/${N - 1})`,
                   c: [0, 0, 0], axis: a2, ref: dir(lk), a0: 0, a1: Lam, r: rk(k) + P.tl / 2, w: 2 * P.hw });
      }
      const r3 = rk(N - 1) - 3.15;
      out.push({ kind: 'hub', role: 'active', name: 'J3', c: V.scale(A3, r3), axis: A3, r: P.hub_r, h: P.stack });
      const cut = M.mulv(ctx.H, V.unit(P.bar_end));
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm piece to BOTTOM', u: A3, v: cut, r0: r3 - 2, r1: 96, r: 3.5 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar (user part)', a: M.mulv(ctx.H, V.scale(V.unit(P.bar_end), 96)), b: M.mulv(ctx.H, [0, -190, 74]), r: 4 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 170), axis: ctx.armAxis, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre (J2 remote centre: no metal at a2)', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();

/* seed-offset-3r-slides - non-spherical offset 3R + 3 passive self-aligning slides (docs/concepts/seed-offset-3r-slides.md,
 * models/seed-offset-3r-slides.py). Best honest configuration (k324, gap 57.95; k320 shares its parameters): the
 * champion's axis directions + deltas, each axis LINE moved off GH by a few mm (along / across its link), remote
 * slide stage down the arm past a 5 mm neck. Loop: scapula -> R1 -> R2 -> R3 -> member 3 -> slide stage (along the
 * humerus, across it, normal to the stage) -> arm. Mobility 3 + 3 + 3 - 6 = 3: 3 ACTIVE, 3 PASSIVE, every slide set
 * by closure. Solved by the NUMERIC IK (6 unknowns: q1..q3 deg, s_a, s_t, s_n mm; residual 3 deg + 3 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const SEED = { az: 2.4305071427308924, el: 80.67633718429899, a: [76.90180446920043, 66.74921235407174],
                 w: [86.32769021001913, 21.829657347343378], branch: -1 };
  const P = { o1a: 1.6, o1c: -5.6, o2a: 1.6, o2c: -4.0, o3a: -0.3, o3c: 4.8, S_a: 13.0, S_t: 9.2, R_r: 6.7,
              remote: 1, neck: 5.0, d_az: 1.7, d_el: -6.4, d_a1: 2.1, d_a2: -1.4, d_wd: 4.1, d_wa: 3.6,
              faces: [56, 90, 64], hub_r: 10, stack: 12.25, car_l: 20, sing: 10 };
  // design (models/seed-offset-3r-slides.py Design.__init__), home frame = scapula frame with the arm at H = S
  const u1 = V.unit(K.bvec(SEED.az + P.d_az, SEED.el + P.d_el));
  const u3 = V.unit(K.wdir(SEED.w[0] + P.d_wd, SEED.w[1] + P.d_wa));
  const A = [SEED.a[0] + P.d_a1, SEED.a[1] + P.d_a2];
  const u2 = K.circInt(u1, A[0], u3, A[1], SEED.branch).p, u = [u1, u2, u3];
  const nb = [u2, u3, u2], ea = u.map((x, k) => V.unit(V.reject(nb[k], x))), ec = u.map((x, k) => V.cross(x, ea[k]));
  const c = [0, 1, 2].map(k => V.add(V.scale(ea[k], P[`o${k + 1}a`]), V.scale(ec[k], P[`o${k + 1}c`])));
  const h0 = [0, -1, 0], sn = u3, sa = V.unit(V.reject(h0, sn)), st = V.cross(sn, sa);
  const stageC = V.madd(c[2], sa, P.hub_r + P.neck + P.car_l / 2 + P.S_a);   // stage centre (member-3 / arm rest coords)

  /** forward kinematics in the scapula frame: member transforms X1, X2, X3 as [R, t] (p -> R p + t) */
  function fk(q) {
    const R1 = M.rot(u1, q[0]), R2 = M.rot(u2, q[1]), R3 = M.rot(u3, q[2]), R12 = M.mul(R1, R2), R123 = M.mul(R12, R3);
    const t1 = V.sub(c[0], M.mulv(R1, c[0]));
    const t2 = V.add(M.mulv(R1, V.sub(V.sub(c[1], M.mulv(R2, c[1])), c[0])), c[0]);
    const t3 = V.add(M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))), t2);
    return { X1: [R1, t1], X2: [R12, t2], X3: [R123, t3] };
  }
  const ap = (X, p) => V.add(M.mulv(X[0], p), X[1]);
  const sv = q => V.add(V.add(V.scale(sa, q[3]), V.scale(st, q[4])), V.scale(sn, q[5]));   // slide displacement (arm rest frame)

  K.register({
    id: 'seed-offset-3r-slides',
    name: 'Offset 3R + passive slides',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: [0, 0, 0, 0, 0, 0],                       // home (H = S); the numeric IK walks from here to the loop's rest pose
    qNames: ['J1', 'J2', 'J3', 'slide along', 'slide across', 'slide normal'], qUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    residual: (q, ctx) => {
      const X = fk(q).X3, Q = M.mul(M.T(ctx.S), ctx.H);
      // member 3 must carry the arm's orientation, and sit on the arm displaced by exactly the slide travel
      return M.rotErrDeg(X[0], Q).concat(V.sub(X[1], M.mulv(Q, sv(q))));
    },
    check: (q, ctx) => {
      const m = K.foldMargin(M.mulv(ctx.S, u1), M.mulv(ctx.H, u3), A[0], A[1]);
      if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const lim = [P.S_a, P.S_t, P.R_r], nm = ['along', 'across', 'normal'];
      for (let i = 0; i < 3; i++) if (Math.abs(q[3 + i]) > lim[i]) return `slide ${nm[i]} past its range (${q[3 + i].toFixed(1)} mm)`;
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = d => M.mulv(S, d), F = P.faces, h = P.stack;
      const { X1, X2, X3 } = fk(q), Q = M.mul(M.T(S), ctx.H), arm = p => W(M.mulv(Q, p));     // arm-fixed (rest coords)
      const hubs = [[0, [M.I3(), [0, 0, 0]]], [1, X1], [2, X2]].map(([k, X]) => {
        const ax = M.mulv(X[0], u[k]), p0 = ap(X, c[k]);
        return { kind: 'hub', role: 'active', name: `J${k + 1}`, c: W(V.madd(p0, ax, F[k])), axis: Wd(ax), p0: W(p0), r: P.hub_r, h };
      });
      const top = (hb, dz) => V.madd(hb.c, hb.axis, dz);
      const arcPts = (a, b) => K.greatArc(a, b, V.norm(a), V.norm(b));
      const s = [q[3], q[4], q[5]], z0 = F[2] - 4;                  // stage base just under hub 3's face height
      const baseC = arm(V.madd(stageC, sn, z0 - 8));
      const aC = V.madd(stageC, sa, s[0]), tC = V.madd(aC, st, s[1]);
      const m3Top = ap(X3, V.madd(stageC, sn, z0 + 6));               // member 3's end of the radial slide
      return [
        { kind: 'plate', role: 'fixed-scapula', c: W(V.madd(c[0], u1, F[0] - 3)), z: Wd(u1), x: Wd([1, 0, 0]), size: [46, 32], t: 3 },
        hubs[0],
        { kind: 'arc', role: 'link', name: 'link 1', pts: arcPts(top(hubs[0], 7), V.madd(hubs[1].c, hubs[1].axis, 2)), r: 2.5 },
        hubs[1],
        { kind: 'arc', role: 'link', name: 'link 2', pts: arcPts(top(hubs[1], 9), top(hubs[2], h + 1)), r: 2.5 },
        hubs[2],
        { kind: 'link', role: 'link', name: 'member 3 neck', a: W(ap(X3, V.madd(V.madd(c[2], u3, F[2] + h - 2), sa, P.hub_r))),
          b: W(m3Top), r: 3 },
        { kind: 'plate', role: 'fixed-arm', name: 'stage base on the arm', c: baseC, z: arm(sn), x: arm(sa), size: [20 + 2 * P.S_a, 22], t: 3 },
        { kind: 'slider', role: 'passive', name: 'slide along the humerus', a: arm(V.madd(V.madd(stageC, sn, z0 - 5), sa, -P.S_a)),
          b: arm(V.madd(V.madd(stageC, sn, z0 - 5), sa, P.S_a)), at: arm(V.madd(aC, sn, z0 - 3)), z: arm(sn), size: [16, 14, 4] },
        { kind: 'slider', role: 'passive', name: 'slide across', a: arm(V.madd(V.madd(aC, sn, z0 + 0.5), st, -P.S_t)),
          b: arm(V.madd(V.madd(aC, sn, z0 + 0.5), st, P.S_t)), at: arm(V.madd(tC, sn, z0 + 2)), z: arm(sn), size: [14, 14, 4] },
        { kind: 'slider', role: 'passive', name: 'slide normal', a: arm(V.madd(tC, sn, z0 + 2 - P.R_r)),
          b: arm(V.madd(tC, sn, z0 + 6 + P.R_r)), at: W(m3Top), z: arm(sa), size: [10, 10, 5] },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: arm(V.scale(h0, V.dot(stageC, h0) + 8)), axis: arm(h0), r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

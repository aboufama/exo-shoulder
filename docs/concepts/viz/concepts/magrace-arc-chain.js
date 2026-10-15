/* magrace-arc-chain - the spherical 3R realised as three hubless ARC joints on magnet-preloaded open ball races
 * (catalogue magrace-arc-chain; models/magrace-arc-chain.py, no sweep yet: its PARAMS, seed = the champion 3R).
 * Joint k: a Ti race plate (12 x 2.5 mm, gothic groove) on the circle at angular radius g_k = 40 deg about the joint
 * axis m_k (through GH), on ONE of the joint's members (s = 0 proximal, 1 distal: J1's race is the scapula base, J2's on
 * link 1, J3's on the arm = the "humeral ring" side); the other member's 25 mm carriage rolls on it (O2 balls, magnets,
 * 7 mm stack). The carriage's place along its race IS the joint angle: 3 ACTIVE, 0 passive; closed form (KIN.sph3r,
 * branch -1). No hub at any axis pierce point. Races span the joint's travel over the loop (mid-range, largest gap)
 * + half a carriage + 1 mm; azimuth 0 = toward the neighbour axis; running radii R schematic (the model fits them).
 * Race centre azimuths c: the model's 0 puts J2's race across the arm (the arm axis comes within 31.5 deg of p2 and the
 * race passes 1.5 mm from it); c2 = 120 deg (inside the model's sweep) keeps it >= 52 mm off the arm axis on the loop. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a1: 76.90180446920043, a2: 66.74921235407174,
              wd: 86.32769021001913, wa: 21.829657347343378, branch: -1, g: [40, 40, 40], c: [0, 120, 0], s: [0, 0, 1],
              R: [64, 72, 66], car: [25, 14, 2.5], race_t: 2.5, balls: 2, sing: 10, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.wd, P.wa), P.a1, P.a2, P.branch), u = [C.u1, C.u2, C.u3];
  const e = [V.unit(V.reject(C.u2, C.u1)), V.unit(V.reject(C.u3, C.u2)), V.unit(V.reject(C.u2, C.u3))];
  const qs = K.motion(240).map(f => K.makeCtx(f.pose, f.t)).filter(c => C.margin(c) >= P.sing).map(c => C.solve(c));
  const J = [0, 1, 2].map(k => {                                  // travel: mid qc, half span qh (largest-gap rule)
    const s = qs.map(q => K.wrap180(q[k])).sort((a, b) => a - b); let g = -1, at = 0;
    s.forEach((x, i) => { const d = (i + 1 < s.length ? s[i + 1] : s[0] + 360) - x; if (d > g) { g = d; at = i; } });
    const qh = (360 - g) / 2, qc = K.wrap180(s[(at + 1) % s.length] + qh), sg = P.s[k] ? -1 : 1;
    const hc = (P.car[0] / 2 + 1) / (P.R[k] * Math.sin(P.g[k] * K.D2R)) * K.R2D;
    return { qc, qh, Lh: Math.min(180, qh + hc), sg, phi: P.c[k] - sg * qc, rm: P.s[k] ? k + 1 : k, cm: P.s[k] ? k : k + 1 };
  });
  const dirAt = (k, az) => K.onCone(u[k], e[k], P.g[k], az);       // member-home coords
  // link straps: each member joins its two elements at their closest points (fixed in the member)
  const near = (k, to) => { let best = null, bd = 1e9; for (let i = 0; i <= 24; i++) { const az = P.c[k] - J[k].Lh + i * J[k].Lh / 12, d = V.angle(dirAt(k, az), to); if (d < bd) { bd = d; best = az; } } return best; };
  const el = (k, mem) => mem === J[k].cm ? { az: J[k].phi, fixed: true } : null;
  const endDir = (k, mem, other) => (el(k, mem) ? dirAt(k, J[k].phi) : dirAt(k, near(k, other)));
  const L1a = endDir(0, 1, dirAt(1, P.c[1])), L1b = endDir(1, 1, L1a), L2a = endDir(1, 2, dirAt(2, P.c[2])), L2b = endDir(2, 2, L2a);

  K.register({
    id: 'magrace-arc-chain',
    name: 'Magnet ball-race arc chain',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1 (carriage 1)', 'J2 (carriage 2)', 'J3 (carriage 3)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < P.sing) return m < 0 ? 'J2 cannot close: the arm axis is out of reach' : `within ${m.toFixed(0)} deg of the chain's fold`;
      for (let k = 0; k < 3; k++) if (Math.abs(K.wrap180(q[k] - J[k].qc)) > J[k].qh + 0.5) return `carriage ${k + 1} at the end of its race`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), Rw = [ctx.S, M.mul(ctx.S, f.R1), M.mul(ctx.S, f.R12), M.mul(ctx.S, f.E)];
      const W = (mem, d) => M.mulv(Rw[mem], d), out = [], g = k => P.g[k] * K.D2R;
      const roles = ['fixed-scapula', 'link', 'fixed-arm'];
      for (let k = 0; k < 3; k++) {
        const j = J[k], R = P.R[k], ax = W(j.rm, u[k]), rr = R + P.race_t / 2;
        out.push({ kind: 'rail', role: roles[k], name: `J${k + 1} race (${['scapula base', 'link 1', 'arm: humeral ring side'][k]})`,
                   c: V.scale(ax, rr * Math.cos(g(k))), axis: ax, ref: W(j.rm, e[k]), rho: rr * Math.sin(g(k)), a0: P.c[k] - j.Lh, a1: P.c[k] + j.Lh, r: 3 });
        const cd = W(j.cm, dirAt(k, j.phi)), tg = V.cross(ax, cd), rc = R + P.race_t + P.balls + P.car[2] / 2;
        out.push({ kind: 'carriage', role: 'active', name: `J${k + 1} carriage (balls + magnets)`, c: V.scale(cd, rc), x: tg, z: cd, size: P.car });
      }
      const top = R => R + P.race_t + P.balls + P.car[2];
      out.push({ kind: 'arc', role: 'link', name: 'link 1 (strap)', u: W(1, L1a), v: W(1, L1b), r0: top(P.R[0]), r1: P.R[1] + P.race_t, r: 2.5 });
      out.push({ kind: 'arc', role: 'link', name: 'link 2 (strap)', u: W(2, L2a), v: W(2, L2b), r0: top(P.R[1]), r1: top(P.R[2]), r: 2.5 });
      const harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at);
      const x3 = W(3, dirAt(2, near(2, M.mulv(M.T(Rw[3]), harm)))), neckA = V.scale(x3, P.R[2] + P.race_t);
      out.push({ kind: 'link', role: 'fixed-arm', name: 'race 3 to cuff (neck)', a: neckA, b: V.madd(cuffC, V.unit(V.reject(neckA, harm)), 47), r: 3 });
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'handler pad', c: V.scale(W(0, dirAt(0, P.c[0])), P.R[0] - 2), z: W(0, dirAt(0, P.c[0])),
                 x: W(0, V.cross(u[0], dirAt(0, P.c[0]))), size: [30, 16], t: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();

/* offset-pointer-slip-sleeve - a 2R pointer about a centre O near GH + a linear-rotary SLEEVE on a rod at the cuff
 * (docs/concepts/offset-pointer-slip-sleeve.md, models/offset-pointer-slip-sleeve.py). Scapula -> J1 hub (axis a1
 * through O) -> link 1 (90 deg arc about O) -> J2 hub (axis j2 = unit(a1 x dh) through O) -> bar -> boss -> O6 rod on
 * the line O -> C -> sleeve at the cuff point C: J3 = spin about the rod (ACTIVE), slide along it (PASSIVE) -> Hooke U
 * (ring on the inner axis u1, cheeks on the cuff's outer axis u2: 2 PASSIVE) -> the user's cuff. 3 ACTIVE + 3 PASSIVE:
 * the cuff's 6 DOF = 6 chain coordinates, every passive set by closure (closed form; the residual re-checks it by FK:
 * cuff orientation 3 deg + sleeve on C 3 mm). Parameters: the best sweep entry (k306, gap 58.9: a1 = bvec(77.5, 78),
 * cuff station 189 mm, azimuth -2, rod 12.9 mm over the skin, bar 60 deg round the rod, cap arc to 45 deg) EXCEPT the
 * offset: the best entry has |o| = 0 (the cuff-sleeve-3r limit, where the slide is idle and the U angles constant);
 * this preview moves O 10 mm toward the acromion top along bvec(14.2, 68.4) (the swept direction) so the slide and the
 * U visibly do their job. Hub faces are schematic (58 / 80 mm from O); the bar's run is fitted outward over the loop
 * against a cylinder arm (the model fits it to the bench skin). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { o: 10, o_az: 14.2, o_el: 68.4, a1_az: 77.5, a1_el: 78.0, branch: -1, s: 189, caz: -2, hC: 12.9, r_out: 44,
              u_lim: 40, rod_cap: 70, sing: 12, dpsi: 60, th_k: 45, R1: 58, R2: 80, r_cap: 70, hub_r: 10, stack: 12.25, ring_r: 9 };
  const O = V.scale(K.bvec(P.o_az, P.o_el), P.o), a1 = V.unit(K.bvec(P.a1_az, P.a1_el));
  const nC = [Math.sin(P.caz * K.D2R), 0, Math.cos(P.caz * K.D2R)], C0 = V.add([0, -P.s, 0], V.scale(nC, P.r_out + P.hC));
  const dh0 = V.unit(V.sub(C0, O)), j20 = V.scale(V.unit(V.cross(a1, dh0)), P.branch);
  const u2c = V.unit(V.cross(dh0, [0, -1, 0])), u1c = V.cross(u2c, dh0);                 // U axes: outer (cuff), inner
  const E = M.fromCols(dh0, u1c, u2c);
  /** closed form in the scapula frame: q = [J1, J2, J3, slide lam (mm), U inner, U outer] */
  function solve(ctx) {
    const Q = M.mul(M.T(ctx.S), ctx.H), d = V.sub(M.mulv(Q, C0), O), lam = V.norm(d), dh = V.scale(d, 1 / lam);
    const j2 = V.scale(V.unit(V.cross(a1, dh)), P.branch), q1 = K.axisAngle(a1, j20, j2), R1 = M.rot(a1, q1);
    const q2 = K.axisAngle(j20, dh0, M.mulv(M.T(R1), dh)), R12 = M.mul(R1, M.rot(j20, q2));
    const G = M.mul(M.mul(M.T(E), M.mul(M.T(R12), Q)), E);                                  // = Rx(J3) Ry(U1) Rz(U2) in E
    const b = Math.asin(Math.max(-1, Math.min(1, G[0][2])));
    return [q1, q2, Math.atan2(-G[1][2], G[2][2]) * K.R2D, lam, b * K.R2D, Math.atan2(-G[0][1], G[0][0]) * K.R2D];
  }
  function fk(q) {                                                                          // members in the scapula frame
    const R1 = M.rot(a1, q[0]), R12 = M.mul(R1, M.rot(j20, q[1])), R123 = M.mul(R12, M.rot(dh0, q[2]));
    const Rr = M.mul(R123, M.rot(u1c, q[4])), Rc = M.mul(Rr, M.rot(u2c, q[5]));
    return { R1, R12, Rr, Rc, Cend: V.madd(O, M.mulv(R12, dh0), q[3]) };
  }
  // rod span (the loop's lam range + 15 mm each way) and the bar's azimuth about the rod (outward side + dpsi)
  let lo = 1e9, hi = -1e9; const outs = [];
  for (const fr of K.motion(240)) {
    const ctx = K.makeCtx(fr.pose), q = solve(ctx), f = fk(q), Q = M.mul(M.T(ctx.S), ctx.H);
    lo = Math.min(lo, q[3]); hi = Math.max(hi, q[3]);
    const dh = M.mulv(f.R12, dh0), j2 = M.mulv(f.R12, j20);
    outs.push(K.axisAngle(dh, j2, M.mulv(Q, nC)));
  }
  outs.sort((x, y) => x - y);
  const psiB = outs[outs.length >> 1] + P.dpsi, xTop = lo - 15, xBot = Math.min(hi + 15, xTop + P.rod_cap);
  // the bar's run along the rod line, link-2-fixed: offset rho(x) along uk, fitted OUTWARD (as the model) so it clears
  // a cylinder arm (radius 50 -> 44 mm down to the cuff, + 3 mm) over every frame of the loop
  const thk0 = P.th_k * K.D2R, xs = [], rho = [], NB = 9, x0 = P.r_cap * Math.cos(thk0), x1 = xTop - 5;
  for (let i = 0; i <= NB; i++) { xs.push(x0 + (x1 - x0) * i / NB); rho.push(P.r_cap * Math.sin(thk0) + (7 - P.r_cap * Math.sin(thk0)) * i / NB); }
  const barFrame = (q, S) => {
    const R12 = fk(q).R12, dh = M.mulv(S, M.mulv(R12, dh0)), j2 = M.mulv(S, M.mulv(R12, j20)), nb = V.cross(dh, j2);
    return { dh, uk: V.add(V.scale(j2, Math.cos(psiB * K.D2R)), V.scale(nb, Math.sin(psiB * K.D2R))) };
  };
  for (const fr of K.motion(240)) {
    const ctx = K.makeCtx(fr.pose), q = solve(ctx), bf = barFrame(q, ctx.S), Ow = M.mulv(ctx.S, O), ax = ctx.armAxis;
    xs.forEach((x, i) => {
      for (let r = rho[i]; r < 140; r += 1) {
        const p = V.madd(V.madd(Ow, bf.dh, x), bf.uk, r), sa = V.dot(p, ax), d = V.norm(V.sub(p, V.scale(ax, Math.max(0, sa))));
        if (sa < 0 || d >= 50 - 6 * Math.min(1, sa / P.s) + 3) { rho[i] = r; break; }
      }
    });
  }

  K.register({
    id: 'offset-pointer-slip-sleeve',
    name: 'Offset 2R pointer + sliding twist sleeve',
    dof: { active: 3, passive: 3 },
    params: Object.assign({ rod: [xTop, xBot] }, P),
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3 (sleeve spin)', 'sleeve slide (|C - O|)', 'U inner', 'U outer'], qUnits: ['deg', 'deg', 'deg', 'mm', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => {
      const f = fk(q), Q = M.mul(M.T(ctx.S), ctx.H);
      return M.rotErrDeg(f.Rc, Q).concat(V.sub(f.Cend, M.mulv(Q, C0)));
    },
    check: (q, ctx) => {
      const Q = M.mul(M.T(ctx.S), ctx.H), a = V.angle(a1, V.sub(M.mulv(Q, C0), O));
      if (a < P.sing || a > 180 - P.sing) return `pointer within ${Math.min(a, 180 - a).toFixed(0)} deg of J1's axis`;
      if (Math.hypot(q[4], q[5]) > P.u_lim) return 'cuff U past its tilt';
      if (q[3] < xTop + 12.5 || q[3] > xBot - 12.5) return 'sleeve past the rod end';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = d => M.mulv(S, d), f = fk(q), h = P.stack;
      const Ow = W(O), A1 = Wd(a1), J2 = Wd(M.mulv(f.R1, j20)), bf = barFrame(q, S), dh = bf.dh, uk = bf.uk;
      const vend = V.unit(V.add(V.scale(dh, xs[0]), V.scale(uk, rho[0]))), rCap = Math.hypot(xs[0], rho[0]);
      const about = (u, v, r0, r1) => K.greatArc(u, v, r0, r1).map(p => V.add(p, Ow));
      const Cw = W(f.Cend), boss = V.madd(V.madd(Ow, dh, xTop - 5), uk, 0), u2w = Wd(M.mulv(f.Rc, u2c));
      const pin = s => V.madd(Cw, u2w, s * (P.ring_r + 2)), foot = s => V.madd(pin(s), V.unit(V.reject(V.sub(Cw, V.scale(ctx.armAxis, V.dot(Cw, ctx.armAxis))), ctx.armAxis)), -12);
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.madd(Ow, A1, P.R1 - 3), z: A1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (axis through O)', c: V.madd(Ow, A1, P.R1), axis: A1, p0: Ow, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (90 deg about O)', pts: about(A1, J2, P.R1 + 7, P.R2 + 2), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (axis through O)', c: V.madd(Ow, J2, P.R2), axis: J2, p0: Ow, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'bar cap', pts: about(J2, vend, P.R2 + 9, rCap), r: 2.5 },
        { kind: 'arc', role: 'link', name: 'bar along the rod (fitted outward)', pts: xs.map((x, i) => V.madd(V.madd(Ow, dh, x), uk, rho[i])), r: 2.5 },
        { kind: 'hub', role: 'link', name: 'rod boss', c: boss, axis: dh, p0: boss, r: 6, h: 10 },
        { kind: 'slider', role: 'passive', name: 'O6 rod + sleeve slide', a: V.madd(Ow, dh, xTop), b: V.madd(Ow, dh, xBot), at: Cw, z: uk, size: [25, 12, 12] },
        { kind: 'ring', role: 'active', name: 'J3: sleeve spin about the rod', c: Cw, axis: dh, r: 7 },
        { kind: 'ring', role: 'passive', name: 'U ring (inner axis)', c: Cw, axis: Wd(M.mulv(f.Rr, dh0)), r: P.ring_r },
        { kind: 'link', role: 'fixed-arm', name: 'U cheek (outer pin)', a: pin(1), b: foot(1), r: 2 },
        { kind: 'link', role: 'fixed-arm', name: 'U cheek (outer pin)', a: pin(-1), b: foot(-1), r: 2 },
        { kind: 'strap', role: 'fixed-arm', name: 'upper-arm cuff', c: V.scale(ctx.armAxis, P.s), axis: ctx.armAxis, r: 45, w: 26 },
        { kind: 'point', role: 'link', name: 'pointer centre O', p: Ow, r: 2.5 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

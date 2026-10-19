/* skin-stretch-scissor - a spherical 3R whose J2 is a tapered spherical lazy-tongs from the scapula-top hub to the
 * deltoid hub (catalogue skin-stretch-scissor, models/skin-stretch-scissor.py; no sweep result yet: the model's
 * PARAMS are used). J1: O20 hub, ACTIVE, about b = bvec(32.55, 80.56) on the scapula top; L1 = J1's upper member, a
 * slotted cap plate holding the scissor root (+u node on a pin, -u node in a lateral slot); J2 = the lazy-tongs, N = 4
 * units of 6 x 2 mm bars (lambda 32 deg), its one DOF = its angular span ss, sensed at the root centre pivot, ACTIVE;
 * L2 = J3's upper plate holding the tip the same way; J3: O20 hub, ACTIVE, about W0 = wdir(71.38, 4.78) on the lateral
 * deltoid, its lower member humerus-fixed with the BOTTOM stub. Every pivot axis radial through GH; 14 PASSIVE pivots /
 * slots, all functions of ss (a lazy-tongs has mobility 1). The model's spec correction is kept: pinned + slotted ends
 * make a scissor LIFT, so L2 moves relative to L1 as F(ss) = R_XY(a) R_XZ(ss) R_XY(-a), a = u_ref - u(ss) (not a pure
 * rotation about b x W); closure solves angle(b, W) = g(ss) for ss, then J1 from the azimuth, J3 from the twist.
 * Node radius constant per node (taper 59.75 -> 67.75 mm: hub faces 44 / 52 + the 'over' cap, schematic before the
 * skin fit). Out of range: tongs stretched (ss / N > lambda - 3), folded (centre pivots < 9 mm apart or the end pair
 * wider than 40 mm), sigma outside 10..170 deg. Closed form. 3 ACTIVE + 14 PASSIVE. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R, R2D = K.R2D;
  const P = { b_az: 32.55, b_el: 80.56, w_d: 71.38, w_az: 4.78, N: 4, lam: 32, stretch: 3, pitch: 2.5, faces: [44, 52],
              over: 15.75, hub_r: 10, stack: 12.25, boss_r: 4, boss_h: 5.5, stub: 40, cuff_at: 165 };
  const N = P.N, lam = P.lam * D, b = V.unit(K.bvec(P.b_az, P.b_el)), W0 = V.unit(K.wdir(P.w_d, P.w_az));
  const ssMax = N * (lam - P.stretch * D);
  const uOf = ss => Math.acos(Math.sqrt(Math.max(0, Math.min(1, (1 + Math.cos(lam)) / (1 + Math.cos(ss / N))))));
  const rXZ = a => [[Math.cos(a), 0, -Math.sin(a)], [0, 1, 0], [Math.sin(a), 0, Math.cos(a)]];   // X -> Z (model _rot)
  const rXY = a => [[Math.cos(a), -Math.sin(a), 0], [Math.sin(a), Math.cos(a), 0], [0, 0, 1]];  // X -> Y
  const rX = a => [[1, 0, 0], [0, Math.cos(a), -Math.sin(a)], [0, Math.sin(a), Math.cos(a)]];
  const e0 = Math.abs(b[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0], Y = V.unit(V.cross(b, e0)), L1ref = M.fromCols(b, Y, V.cross(b, Y));
  const y3 = V.unit(V.reject([0, -1, 0], W0));
  // u_ref: middle of the end-pair half opening over the loop (the model uses the fit clips)
  const [uMin, uMax] = (() => {
    const us = K.motion(240).map(fr => { const c = K.makeCtx(fr.pose, fr.t), Wq = M.mulv(M.mul(M.T(c.S), c.H), W0);
      return uOf(Math.max(0.02, Math.min(ssMax, Math.acos(Math.max(-1, Math.min(1, V.dot(b, Wq))))))); });
    return [Math.min(...us), Math.max(...us)];
  })(), uRef = (uMin + uMax) / 2;
  const FL2 = ss => { const a = uRef - uOf(ss); return M.mul(M.mul(rXY(a), rXZ(ss)), rXY(-a)); };
  const g = ss => Math.acos(Math.max(-1, Math.min(1, FL2(ss)[0][0])));
  const tab = []; for (let i = 0; i <= 600; i++) { const ss = 0.2 * D + (ssMax - 0.2 * D) * i / 600; tab.push([ss, g(ss)]); }
  function ssOf(sig) {                                          // invert the monotone g (clamped at the table ends)
    if (sig <= tab[0][1]) return tab[0][0];
    for (let i = 1; i < tab.length; i++) if (tab[i][1] >= sig) {
      const [s0, g0] = tab[i - 1], [s1, g1] = tab[i]; return s0 + (s1 - s0) * (sig - g0) / (g1 - g0 || 1e-12);
    }
    return tab[tab.length - 1][0];
  }
  const Wsc = ctx => M.mulv(M.mul(M.T(ctx.S), ctx.H), W0);    // J3 axis in the scapula frame
  function chain(q, ctx) {                                      // L1, L2 (scapula frame) from q = [J1, ss, J3] (deg)
    const L1 = M.mul(L1ref, rX(q[0] * D)), F = FL2(q[1] * D), L2 = M.mul(L1, F);
    return { L1, L2, F };
  }
  function solve(ctx) {
    const Wq = Wsc(ctx), sig = Math.acos(Math.max(-1, Math.min(1, V.dot(b, Wq)))), ss = ssOf(sig), F = FL2(ss);
    const a = M.mulv(M.T(L1ref), Wq), wl = M.col(F, 0);
    const q1 = Math.atan2(a[2], a[1]) - Math.atan2(wl[2], wl[1]), L2 = M.mul(M.mul(L1ref, rX(q1)), F);
    const q3 = K.axisAngle(Wq, M.mulv(M.mul(M.T(ctx.S), ctx.H), y3), M.col(L2, 1));
    return [K.wrap180(q1 * R2D), ss * R2D, q3];
  }
  const rf = f => P.faces[0] + P.over + (P.faces[1] - P.faces[0]) * f;                       // node radius (taper)

  K.register({
    id: 'skin-stretch-scissor',
    name: 'Skin-stretch scissor (lazy-tongs J2)',
    dof: { active: 3, passive: 14 },
    params: Object.assign({ u_ref_deg: uRef * R2D, ss_max_deg: ssMax * R2D }, P),
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2 scissor span', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => {
      const c = chain(q, ctx), Wq = Wsc(ctx);
      const tw = K.axisAngle(Wq, M.mulv(M.mul(M.T(ctx.S), ctx.H), y3), M.col(c.L2, 1));
      return [V.angle(M.col(c.L2, 0), Wq), K.wrap180(q[2] - tw)];
    },
    check: (q, ctx) => {
      const sig = V.angle(b, Wsc(ctx)), ss = q[1] * D, u = uOf(ss);
      if (sig < 10 || sig > 170) return 'hubs too close / opposite (sigma outside 10-170 deg)';
      if (ss / N > lam - P.stretch * D + 1e-6 || V.angle(M.col(FL2(ss), 0), [1, 0, 0]) < sig - 0.5) return 'tongs fully stretched';
      if (ss / N * rf(0.5) < 2 * P.boss_r + 1) return 'tongs folded (centre pivots touch)';
      if (2 * u * rf(0) > 40) return 'tongs folded too wide (> 40 mm)';
      return null;
    },
    parts: (q, ctx) => {
      const c = chain(q, ctx), S = x => M.mulv(ctx.S, x), F = P.faces, h = P.stack, ss = q[1] * D, u = uOf(ss);
      const Fr = M.mul(c.L1, rXY(uRef - u)), node = (f, s) => [Math.cos(f * ss) * Math.cos(u), s * Math.sin(u), Math.sin(f * ss) * Math.cos(u)];
      const at = (loc, f, dz) => S(V.scale(M.mulv(Fr, loc), rf(f) + (dz || 0)));
      const pb = S(b), p3 = M.mulv(ctx.H, W0), out = [];                 // J3 + stub on the ARM axis: a gap shows when the tongs cannot reach
      const plate = (L, f, nm) => {
        const ax = S(M.col(L, 0)), x = S(M.col(L, 2)), r = (f ? F[1] : F[0]) + 11.75 + 1.5;
        return { kind: 'plate', role: 'link', name: nm, c: V.scale(ax, r), z: ax, x, size: [24, 2 * 22], t: 3 };
      };
      const slot = (f, nm) => {                                 // -u end node rides a lateral slot on its plate: in the plate's
        const L = f ? c.L2 : c.L1;                              // frame the pin sits at u_ref, the slot node at u_ref - 2u
        const lat = d => S(V.scale(M.mulv(L, [Math.cos(d), Math.sin(d), 0]), rf(f) - 1));
        return { kind: 'slider', role: 'passive', name: nm, a: lat(uRef - 2 * uMin + 1.5 * D), b: lat(uRef - 2 * uMax - 1.5 * D),
                 at: lat(uRef - 2 * u), z: S(M.col(L, 0)), size: [8, 7, 3], r: 1.4 };
      };
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.scale(pb, F[0] - 3), z: pb, x: ctx.attach.scapDir([1, 0, 0]), size: [44, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (scapula top)', c: V.scale(pb, F[0]), axis: pb, r: P.hub_r, h },
        plate(c.L1, 0, 'L1: J1 cap plate (root pin + slot)'), slot(0, 'root slot (-u end node)'));
      for (let k = 0; k < N; k++) {
        out.push({ kind: 'arc', role: 'link', name: `bar A${k + 1}`, pts: K.greatArc(at(node(k / N, 1), k / N), at(node((k + 1) / N, -1), (k + 1) / N), rf(k / N), rf((k + 1) / N), 6), r: 1.5 },
          { kind: 'arc', role: 'link', name: `bar B${k + 1}`, pts: K.greatArc(at(node(k / N, -1), k / N), at(node((k + 1) / N, 1), (k + 1) / N), rf(k / N) + P.pitch, rf((k + 1) / N) + P.pitch, 6), r: 1.5 });
      }
      for (let k = 0; k <= N; k++) for (const s of [1, -1]) {
        const p = at(node(k / N, s), k / N, P.pitch / 2), end = k === 0 || k === N;
        out.push({ kind: 'hub', role: 'passive', name: end ? `end ${k ? 'tip' : 'root'} ${s > 0 ? 'pin' : 'slot node'}` : `side pivot ${k}${s > 0 ? '+' : '-'}`,
                   c: V.madd(p, V.unit(p), -2.5), axis: V.unit(p), p0: p, r: P.boss_r, h: P.boss_h });
      }
      for (let k = 0; k < N; k++) {
        const f = (k + 0.5) / N, p = at([Math.cos(f * ss), 0, Math.sin(f * ss)], f, P.pitch / 2);
        out.push({ kind: 'hub', role: k === 0 ? 'active' : 'passive', name: k === 0 ? 'J2 sensor (root centre pivot)' : `centre pivot ${k + 1}`,
                   c: V.madd(p, V.unit(p), -2.5), axis: V.unit(p), p0: p, r: k === 0 ? 4.6 : P.boss_r, h: P.boss_h });
      }
      const harm = ctx.armAxis, stubEnd = V.madd(V.scale(p3, F[1] + 4), harm, P.stub), cuffC = V.scale(harm, P.cuff_at);
      out.push(plate(c.L2, 1, 'L2: J3 cap plate (tip pin + slot)'), slot(1, 'tip slot (-u end node)'),
        { kind: 'hub', role: 'active', name: 'J3 (lateral deltoid)', c: V.scale(p3, F[1]), axis: p3, r: P.hub_r, h },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM stub (14 x 6, 40 mm down the arm)', a: V.scale(p3, F[1] + 1), b: stubEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'stub to the cuff', a: stubEnd, b: V.madd(cuffC, V.unit(V.reject(stubEnd, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();

/* short-a2-arc-slide-3r - a spherical 3R with a SHORT link 2 whose J3 hub rides a spring-returned, GH-concentric arc
 * slide in link 2 (bench model docs/concepts/models/short-a2-arc-slide-3r.py, doc docs/concepts/short-a2-arc-slide-3r.md).
 * J1 axis bvec(az, el) fixed in the scapula, J3 axis wdir(wd, wa) fixed in the humerus, link 1 arc a1, link 2 home arc
 * a2h. J2 has HARD STOPS at the dihedrals where angle(J1, J3) = |a1 - a2h| + m and a1 + a2h - m (a2 = a2h). Mode A
 * (J2 inside its stops): the constant-force spring holds the carriage on its home stop, a2 = a2h, a plain 3R. Mode B / C
 * (the arm asks for more): J2 sits on its stop and the carriage slides out along the arc slot (a rotation about
 * n = J2 x J3 through GH) by the least amount that closes the chain: a2 = the smallest root >= a2h of
 * cos th = cos a1 cos a2 + sin a1 sin a2 cos mu_stop, up to a2max. 3 ACTIVE R + 1 PASSIVE R (the slide, sensed,
 * spring-returned; 4th q entry, mm of carriage travel at the slot radius); 0 passive translations.
 * Drawn: the O20 hubs at the model's fitted levels, link 1, the rail plate (root + the constant-radius slot zone), the
 * carriage (orange: iglidur bushings), hub 3 on the carriage, the K7 neck to BOTTOM's bar and the cuff. Frames the relay
 * cannot take (past the full travel, or the fold) show red. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  // best config (CMA stream 3, Bench(60,160) fast 29.38): carriage integrated in hub 3's lower member (carr_t 0), rail plate
  // the UPPER member at J2 (over link 1), fitted levels F 53 / 63 / 69.15 mm, slot at 66 mm, rail span 36.8-59.8 deg from J2
  const P = { az: 86.6683, el: 61.6608, wd: 102.6189, wa: -3.6242, a1: 42.143, a2h: 45.5057, a2max: 51.1109, sigma: -1, m_stop: 5,
              faces: { J1: 53, J2: 63, J3: 69.15 }, rail: 66, rail_span: [36.82, 59.79], stack: 12.25, cuff_at: 165,
              lv1: [56.1, 56.1, 56.1, 51.0, 52.0, 53.0, 55.0, 59.7, 63.2, 63.2, 63.2],
              lvr: [66.2, 66.2, 66.2, 67.2, 63.7, 60.0, 60.0, 62.5, 66.0, 66.0, 66.0],
              lvn: [72.3, 72.3, 70.0, 70.0, 72.0, 75.0, 78.0, 81.0, 86.0, 92.0, 98.0] };
  const u1 = K.bvec(P.az, P.el), u3 = K.wdir(P.wd, P.wa);
  const C0 = K.sph3r(u1, u3, P.a1, P.a2h, P.sigma), u2 = C0.u2, nH = V.unit(V.cross(u2, u3)), v3 = V.unit(V.reject([1, 0, 0], u3));
  const cosd = x => Math.cos(x * D2R), sind = x => Math.sin(x * D2R), acosd = x => Math.acos(Math.max(-1, Math.min(1, x))) / D2R;
  const dihedral = (a1, a2, th) => acosd((cosd(th) - cosd(a1) * cosd(a2)) / (sind(a1) * sind(a2)));
  const lo = Math.abs(P.a1 - P.a2h) + P.m_stop, hi = P.a1 + P.a2h - P.m_stop;
  const muLo = dihedral(P.a1, P.a2h, lo), muHi = dihedral(P.a1, P.a2h, hi);
  function stopRoot(th, mu) {                                 // smallest a2 in [a2h, a2max] (model stop_root)
    const A = cosd(P.a1), B = sind(P.a1) * cosd(mu), R = Math.hypot(A, B), phi = Math.atan2(B, A) / D2R, c = cosd(th) / R;
    if (Math.abs(c) > 1) return NaN;
    const d = acosd(c); let best = NaN;
    for (const x of [phi + d, phi - d, phi + d + 360, phi - d + 360, phi + d - 360, phi - d - 360])
      if (x >= P.a2h - 1e-7 && x <= P.a2max + 1e-7 && !(best <= x)) best = x;
    return best;
  }
  function relay(ctx) {
    const Q = M.mul(M.T(ctx.S), ctx.H), p3 = M.mulv(Q, u3), th = V.angle(u1, p3);
    if (th >= lo && th <= hi) return { a2: P.a2h, mode: 0, Q, p3, th };
    const a2 = stopRoot(th, th > hi ? muHi : muLo);
    return Number.isFinite(a2) ? { a2, mode: th > hi ? 1 : 2, Q, p3, th } : { a2: th > hi ? P.a2max : P.a2h, mode: -1, Q, p3, th };
  }
  function fk(q, ctx) {
    const R1 = M.rot(u1, q[0]), R12 = M.mul(M.mul(R1, M.rot(u2, q[1])), M.rot(nH, q[3])), E = M.mul(R12, M.rot(u3, q[2]));
    return { p1: M.mulv(ctx.S, u1), p2: M.mulv(ctx.S, M.mulv(R1, u2)), p3: M.mulv(ctx.S, M.mulv(R12, u3)), R: M.mul(ctx.S, E), R1, R12 };
  }
  function solve(ctx) {
    const r = relay(ctx), s = r.a2 - P.a2h, p2 = K.circInt(u1, P.a1, r.p3, r.a2, P.sigma).p;
    const q1 = K.axisAngle(u1, u2, p2), R1 = M.rot(u1, q1), ws = M.mulv(M.rot(nH, s), u3);
    const q2 = K.axisAngle(u2, ws, M.mulv(M.T(R1), r.p3)), R12 = M.mul(M.mul(R1, M.rot(u2, q2)), M.rot(nH, s));
    const R3 = M.mul(M.T(R12), r.Q), q3 = K.axisAngle(u3, v3, M.mulv(R3, v3));
    return [q1, q2, q3, s];
  }
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  function profArc(u, v, lv, dz) {
    const n = 24, out = [], g = K.greatArc(u, v, 1, 1, n);
    for (let i = 0; i <= n; i++) {
      const s = i / n * (lv.length - 1), j = Math.min(lv.length - 2, Math.floor(s)), r = lv[j] + (lv[j + 1] - lv[j]) * (s - j);
      out.push(V.scale(V.unit(g[i]), r + dz));
    }
    return out;
  }
  const arcPt = (p2, e, s, r) => V.scale(V.unit(V.add(V.scale(p2, cosd(s)), V.scale(e, sind(s)))), r);
  K.register({
    id: 'short-a2-arc-slide-3r',
    name: 'Short-link-2 3R, J3 on a spring-returned GH-concentric arc slide (a2 relay)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'slide'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => M.rotErrDeg(fk(q, ctx).R, ctx.H),
    check: (q, ctx) => {
      const r = relay(ctx);
      if (r.mode < 0) return r.th > hi ? `stretched past the slide's full travel (J1-J3 ${r.th.toFixed(0)} deg)` : `folded past J2's low stop (J1-J3 ${r.th.toFixed(0)} deg)`;
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), F = P.faces, h = P.stack, s = q[3];
      const n = V.unit(V.cross(f.p2, f.p3)), e = V.unit(V.cross(n, f.p2));
      const railRoot = [], railSlot = [];
      for (let i = 0; i <= 20; i++) { const a = P.rail_span[0] * i / 20, x = i / 2, j = Math.min(9, Math.floor(x));
        railRoot.push(arcPt(f.p2, e, a, P.lvr[j] + (P.lvr[j + 1] - P.lvr[j]) * (x - j) + 1.5)); }
      for (let i = 0; i <= 16; i++) { const a = P.rail_span[0] + (P.rail_span[1] - P.rail_span[0]) * i / 16; railSlot.push(arcPt(f.p2, e, a, P.rail + 1.5)); }
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = profArc(f.p3, bar0, P.lvn, 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      const t3 = V.unit(V.cross(n, f.p3));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F.J1 - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, MR117-2RS pair)', c: V.scale(f.p1, F.J1), axis: f.p1, r: 10, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti)', pts: profArc(f.p1, f.p2, P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, hard stops at the fold margin)', c: V.scale(f.p2, F.J2), axis: f.p2, r: 10, h },
        { kind: 'arc', role: 'link', name: 'link 2a rail plate, root', pts: railRoot, r: 3 },
        { kind: 'arc', role: 'passive', name: 'arc slot (GH-concentric, constant radius)', pts: railSlot, r: 3.2 },
        { kind: 'carriage', role: 'passive', name: `hub 3 sole on the slot (iglidur bushings, slide ${s.toFixed(1)} deg)`, c: V.scale(f.p3, P.rail + 3.1), x: t3, z: f.p3, size: [16, 12, 1] },
        { kind: 'hub', role: 'active', name: 'J3 (O20, on the carriage)', c: V.scale(f.p3, F.J3), axis: f.p3, r: 10, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, upper member of J3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

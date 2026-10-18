/* cap-nullspace-4r - cap-pole redundant 4R whose 1-D null-space is set by two preloaded torsion springs (J0 to the
 * base, J3 to the arm-end plate) inside own-angle stops (docs/concepts/models/cap-nullspace-4r.py; params = the
 * model's best spring cell on Bench(60,160) fast, see P.src; hub 2 sits at its fitted 121 mm: the measured limiter).
 * J0 (counted joint, O20, scapula-fixed axis c on the back of the shoulder, a0 from the cap pole toward bearing beta)
 * -> link 0 (12 x 3 Ti, arc a0) -> J1 (O20, rest at the cap pole b; dowel stop on the J0-J1-J2 fold) -> link 1 (a1)
 * -> J2 (O20; dowel stop on the J1-J2-J3 fold) -> link 2 (a2) -> J3 (O20, humerus-fixed) -> K7 neck -> BOTTOM / cuff.
 * State: c-J1-J2-J3 is a spherical four-bar per pose; q0 (J0's own angle) follows the LOCAL minimum of the spring
 * energy E = sum k_i wrap(q_i - r_i)^2, tracked from the previous frame (frame 0: the global minimum), inside the
 * feasible window (both folds >= m, the assembly mode sB / sig fixed, J1 on the legal seat). A stop push > 10 deg or
 * a descent that runs > 10 deg (a basin snap) is flagged red, not smoothed. 4 joints, 0 passive, 0 passive translations. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = {"src": "search best (k=best2: 552 configs ES, 47.28 fast / 59.05 frozen exact Bench(110,360)), springs on J0 + J2 + J3, sig -1", "b_az": 43.2, "b_el": 59.9, "a0": 25.0, "beta": 298.78, "a1": 57.39, "a2": 63.55, "wd": 83.9, "wa": -14.24, "sB": 1, "sig": -1, "m": 5.21, "k": [0.638, 0.0, 0.166, 0.208], "r": [-10.49, -3.15, 55.54, -141.51], "faces": {"J0": 57.0, "J1": 53.0, "J2": 121.2, "J3": 73.0}, "stack": 12.25, "cuff_at": 165, "lv0": [60.1, 60.1, 60.1, 53.0, 53.0, 53.0], "lv1": [56.1, 54.8, 69.2, 93.5, 117.7, 121.2], "lv2": [125.4, 125.2, 101.0, 73.6, 85.0, 76.2], "lvn": [73.0, 73.8, 77.0, 87.0, 89.8, 90.0]};

  const b = K.bvec(P.b_az, P.b_el), w3 = K.wdir(P.wd, P.wa);
  const t1 = V.unit(V.cross(b, [0, 1, 0])), t2 = V.cross(b, t1);
  const dB = V.add(V.scale(t1, Math.cos(P.beta * D2R)), V.scale(t2, Math.sin(P.beta * D2R)));
  const cS = V.unit(V.add(V.scale(b, Math.cos(P.a0 * D2R)), V.scale(dB, Math.sin(P.a0 * D2R))));
  const C = K.sph3r(b, w3, P.a1, P.a2, P.sig);                 // the dyad J1-J2-J3 on link 0 (home J1 = b)
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];  // BOTTOM's bar (body_pose humerus frame)
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  const seatOk = u => { const el = Math.asin(Math.max(-1, Math.min(1, u[1]))) / D2R, az = Math.atan2(u[2], -u[0]) / D2R;
                        return az >= -110 && az <= 135 && el >= -20 && u[0] <= 0.2; };
  const QN = 360, QG = Array.from({ length: QN }, (_, i) => i - 180);
  const U1 = QG.map(q => M.mulv(M.rot(cS, q), b)), SEAT = U1.map(seatOk);
  /** feasibility + spring energy of every q0 state at this frame (scapula frame) */
  function scan(ctx) {
    const Q = M.mul(M.T(ctx.S), ctx.H), u3 = M.mulv(Q, w3), ref3 = M.mulv(Q, [0, -1, 0]);
    return U1.map((u1, i) => {
      if (!SEAT[i] || K.foldMargin(u1, u3, P.a1, P.a2) < P.m) return Infinity;
      const p2 = K.circInt(u1, P.a1, u3, P.a2, P.sig).p;
      if (K.foldMargin(cS, p2, P.a0, P.a1) < P.m || Math.sign(V.dot(V.cross(cS, p2), u1)) !== P.sB) return Infinity;
      const q = [QG[i], K.axisAngle(u1, cS, p2), K.axisAngle(p2, u1, u3), K.axisAngle(u3, ref3, p2)];
      return q.reduce((e, x, j) => e + P.k[j] * Math.pow(K.wrap180(x - P.r[j]) * D2R, 2), 0);
    });
  }
  /** the spring's state: {q0, ok, why}. Frame 0 = global minimum; later frames = descent from the previous q0 */
  function state(ctx, prev) {
    const E = scan(ctx); let best = 0;
    for (let i = 1; i < QN; i++) if (E[i] < E[best]) best = i;
    if (!isFinite(E[best])) return { q0: prev == null ? 0 : prev, ok: false, why: 'no closing state (both folds / seat)' };
    if (prev == null) return { q0: QG[best], ok: true };
    let iq = ((Math.round(prev) + 180) % 360 + 360) % 360, why = null;
    if (!isFinite(E[iq])) {
      let k = -1;
      for (let d = 1; d <= 180 && k < 0; d++) for (const j of [iq - d, iq + d]) { const jj = (j + 360) % 360; if (k < 0 && isFinite(E[jj])) k = jj; }
      if (Math.abs(K.wrap180(QG[k] - prev)) > 10) why = 'a fold stop pushes J0 > 10 deg in one frame (a snap)';
      iq = k;
    }
    const i0 = iq;
    for (;;) { const a = (iq + 359) % 360, c = (iq + 1) % 360, j = E[a] < E[c] ? a : c; if (E[j] < E[iq]) iq = j; else break; }
    if (Math.abs(K.wrap180(QG[iq] - QG[i0])) > 10) why = why || 'the spring basin snaps J0 > 10 deg';
    return { q0: QG[iq], ok: !why, why };
  }
  const onLink0 = (ctx, q0) => ({ S: M.mul(ctx.S, M.rot(cS, q0)), H: ctx.H });
  const flag = new WeakMap();
  function solveAll(ctx, qPrev) {
    const s = state(ctx, qPrev ? qPrev[0] : null); if (!s.ok) flag.set(ctx, s.why);
    return [s.q0].concat(C.solve(onLink0(ctx, s.q0)));
  }
  function profArc(u, v, lv, dz) {
    const n = 24, out = [], g = K.greatArc(u, v, 1, 1, n);
    for (let i = 0; i <= n; i++) {
      const s = i / n * (lv.length - 1), j = Math.min(lv.length - 2, Math.floor(s)), r = lv[j] + (lv[j + 1] - lv[j]) * (s - j);
      out.push(V.scale(V.unit(g[i]), r + dz));
    }
    return out;
  }

  K.register({
    id: 'cap-nullspace-4r',
    name: 'Cap-pole redundant 4R (null-space set by J0 + J3 torsion springs and own-angle stops)',
    dof: { active: 4, passive: 0 },
    params: P,
    q0: ctx => solveAll(ctx, null),
    qNames: ['J0 (spring, back seat)', 'J1 (cap pole spare)', 'J2', 'J3 (spring to the arm plate)'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve: (ctx, qPrev) => solveAll(ctx, qPrev),
    residual: (q, ctx) => C.residual(q.slice(1), onLink0(ctx, q[0])).concat([0]),
    check: (q, ctx) => {
      if (flag.has(ctx)) return flag.get(ctx);
      const m = C.margin(onLink0(ctx, q[0]));
      if (m < P.m - 1e-3) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const sh = onLink0(ctx, q[0]), f = C.fk(q.slice(1), sh), F = P.faces, h = P.stack, R = 10;
      const c = M.mulv(ctx.S, cS);
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = profArc(f.p3, bar0, P.lvn, 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler, carries J0 hub ring)', c: V.scale(c, F.J0 - 3), z: c, x: ctx.attach.scapDir([1, 0, 0]), size: [30, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J0 (O20, back seat, torsion spring to the base)', c: V.scale(c, F.J0), axis: c, r: R, h },
        { kind: 'ring', role: 'link', name: 'J0 torsion spring (double-leg, preloaded)', c: V.scale(c, F.J0 + 6), axis: c, r: 12, t: 1.3 },
        { kind: 'arc', role: 'link', name: 'link 0 (12 x 3 Ti, J0 to the cap pole)', pts: profArc(c, f.p1, P.lv0, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, cap pole spare, J0-J1-J2 fold stop)', c: V.scale(f.p1, F.J1), axis: f.p1, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti, over link 0)', pts: profArc(f.p1, f.p2, P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, J1-J2-J3 fold stop)', c: V.scale(f.p2, F.J2), axis: f.p2, r: R, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1 and the neck)', pts: profArc(f.p2, f.p3, P.lv2, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, humerus-fixed)', c: V.scale(f.p3, F.J3), axis: f.p3, r: R, h },
        { kind: 'ring', role: 'fixed-arm', name: 'J3 torsion spring (double-leg, to the arm-end plate)', c: V.scale(f.p3, F.J3 + 6), axis: f.p3, r: 12, t: 1.3 },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, member 3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

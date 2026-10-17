/* acromion-relay-4r - a PLAIN O20 spherical 3R whose J1 walks the acromion-cap rim on a spring-centred J0 at the cap
 * pole (docs/concepts/models/acromion-relay-4r.py; params = k=clampC-g31-1 (CMA, 555 configs) -> gap 42.74 near-touch / 41.62 plain, Bench(60,160) fast).
 * J0 (counted joint, O20, axis c = bvec(az_c, el_c) through GH at the acromion / supraspinatus cap pole, centred by a
 * preloaded double-leg torsion spring against a base dowel, own-angle stops +-T) -> link 0 (12 x 3 Ti, arc a0) -> J1
 * (O20, rest bvec(az_c, el_c - a0) on the cap rim) -> link 1 (a1) -> J2 (O20, own-angle stops at th margin m_lo / m_hi
 * from each fold) -> link 2 (a2) -> J3 (O20, humerus-fixed) -> K7 neck -> BOTTOM / cuff.
 * Clamp determination (model q0_policy): J2 strictly inside its stops -> q0 = 0 (the spring preload holds J0: the chain
 * IS the plain 3R); J2 on its high / low stop -> J0 turns the least |q0| that keeps angle(J1, J3) = hi / lo; the
 * J0-J1-J3 sub-chain keeps >= m_sw of fold margin. 4 joints (J0..J3), 0 passive, 0 passive translations.
 * Hub levels = the model's fitted levels at that config. A frame the relay cannot take (no J0 root, sub-chain at its
 * own fold, |q0| > T) is drawn at the nearest physical state and shows red; a least-|q0| root switch > 25 deg (a snap
 * a real J0 cannot follow) is flagged red, not smoothed. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = {"az_c": 43.15, "el_c": 88.23, "beta": 28.3, "a1": 50.21, "a2": 60.26, "wd": 92.03, "wa": -9.03, "sigma": -1, "m_lo": 5.0, "m_hi": 5.01, "m_sw": 5.0, "qmax": 47.0, "lift2": 1.08, "end_extra": 0.0, "faces": {"R0": 51.0, "J1": 54.5, "J2": 124.0, "J3": 69.5}, "hub_r": {"R0": 10, "J1": 10, "J2": 10, "J3": 10}, "stack": 12.25, "cuff_at": 165, "lvr": [54.1, 54.1, 54.1, 54.1, 50.7, 49.0, 51.0, 54.5, 54.5, 54.5, 54.5], "lv1": [58.7, 58.7, 61.6, 72.0, 82.4, 92.8, 103.2, 113.6, 124.0, 124.0, 124.0], "lv2": [128.2, 128.2, 128.0, 113.6, 107.2, 93.4, 87.3, 84.4, 79.2, 72.6, 72.6], "lvn": [69.5, 69.9, 71.5, 73.1, 76.3, 79.7, 82.6, 84.8, 87.4, 89.9, 92.0]};

  const cS = K.bvec(P.az_c, P.el_c), u1r = K.bvec(P.az_c, P.el_c - P.beta), w3 = K.wdir(P.wd, P.wa);
  const lo = Math.abs(P.a1 - P.a2) + P.m_lo, hi = P.a1 + P.a2 - P.m_hi;
  const C = K.sph3r(u1r, w3, P.a1, P.a2, P.sigma);            // the plain 3R on link 0 (home J1 = u1r)
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713];  // BOTTOM's bar (body_pose humerus frame)
  const BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  /** the relay (model relay()): -> {q0 (deg), ok, mode 'A' | 'B' | 'C', th, why}. A frame the relay cannot take (no
   *  rocker root, rocker within m_sw of its own fold, |q0| > qmax) is drawn at the nearest physical state: the rocker
   *  root nearest the previous frame's q0 (else the model's least-|q0| root; the closest point when no root exists),
   *  clamped to its end stops; check() turns it red. Taken frames use the model's least-|q0| rule exactly. */
  function relay(ctx, prevQ0) {
    const Q = M.mul(M.T(ctx.S), ctx.H), p3 = M.mulv(Q, w3), th = V.angle(u1r, p3);
    if (th >= lo && th <= hi) return { q0: 0, ok: true, mode: 'A', th };
    const ths = th > hi ? hi : lo, mg = K.foldMargin(cS, p3, P.beta, ths);
    const roots = [1, -1].map(s => K.axisAngle(cS, u1r, K.circInt(cS, P.beta, p3, ths, s).p));
    const pick = Math.abs(roots[1]) < Math.abs(roots[0]) ? roots[1] : roots[0];
    const mode = th > hi ? 'B' : 'C';
    if (mg > 0 && mg >= P.m_sw && Math.abs(pick) <= P.qmax) return { q0: pick, ok: true, mode, th };
    const near = prevQ0 == null ? pick : roots.reduce((a, b) => Math.abs(K.wrap180(b - prevQ0)) < Math.abs(K.wrap180(a - prevQ0)) ? b : a);
    return { q0: Math.max(-P.qmax, Math.min(P.qmax, near)), ok: false, mode, th,
             why: mg <= 0 ? 'no rocker root' : (mg < P.m_sw ? 'J0-J1-J3 sub-chain within ' + P.m_sw + ' deg of its own fold' : 'J0 on its end stop') };
  }
  const JUMP = 25, flip = new WeakMap();                        // model K2 jump rule (deg) on q0; per-frame flag for check()
  function solveRelay(ctx, qPrev) {
    const r = relay(ctx, qPrev ? qPrev[0] : null);
    if (qPrev && r.ok && Math.abs(K.wrap180(r.q0 - qPrev[0])) > JUMP) flip.set(ctx, K.wrap180(r.q0 - qPrev[0]));
    return [r.q0].concat(C.solve(onRocker(ctx, r.q0)));
  }
  const onRocker = (ctx, q0) => ({ S: M.mul(ctx.S, M.rot(cS, q0)), H: ctx.H });
  /** J2 interior angle at hub 2 (deg) for a J1-J3 angle th (spherical law of cosines) */
  const interior = th => Math.acos(Math.max(-1, Math.min(1, (Math.cos(th * D2R) - Math.cos(P.a1 * D2R) * Math.cos(P.a2 * D2R)) /
                                                         (Math.sin(P.a1 * D2R) * Math.sin(P.a2 * D2R))))) / D2R;
  const A_lo = interior(lo), A_hi = interior(hi);
  function profArc(u, v, lv, dz) {
    const n = 24, out = [], g = K.greatArc(u, v, 1, 1, n);
    for (let i = 0; i <= n; i++) {
      const s = i / n * (lv.length - 1), j = Math.min(lv.length - 2, Math.floor(s)), r = lv[j] + (lv[j + 1] - lv[j]) * (s - j);
      out.push(V.scale(V.unit(g[i]), r + dz));
    }
    return out;
  }

  K.register({
    id: 'acromion-relay-4r',
    name: 'Acromion-pole relay 4R (plain O20 3R, J1 on a spring-centred J0 at the cap pole)',
    dof: { active: 4, passive: 0 },
    params: P,
    q0: ctx => { const r = relay(ctx); return [r.q0].concat(C.solve(onRocker(ctx, r.q0))); },
    qNames: ['J0 (spring-centred, own-angle stops)', 'J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve: (ctx, qPrev) => solveRelay(ctx, qPrev),
    residual: (q, ctx) => C.residual(q.slice(1), onRocker(ctx, q[0])).concat([K.wrap180(q[0] - relay(ctx, q[0]).q0)]),
    check: (q, ctx) => {
      const r = relay(ctx);
      if (!r.ok) return `J2 on its ${r.mode === 'B' ? 'high' : 'low'} stop and J0 cannot relay (${r.why})`;
      if (flip.has(ctx)) return `relay root switch: the least-|q0| rule jumps J0 ${flip.get(ctx).toFixed(0)} deg (a real J0 cannot follow on this path)`;
      const m = C.margin(onRocker(ctx, q[0]));
      if (m < Math.min(P.m_lo, P.m_hi) - 1e-3) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const sh = onRocker(ctx, q[0]), f = C.fk(q.slice(1), sh), F = P.faces, h = P.stack, R = P.hub_r;
      const c = M.mulv(ctx.S, cS);
      const harm = ctx.armAxis, bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const neck = profArc(f.p3, bar0, P.lvn, 3), neckEnd = neck[neck.length - 1];
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      // J2 stops: blocks fixed in link 1 at the interior angles of lo / hi, the dog fixed in link 2 (toward J3)
      const t1 = V.unit(V.reject(f.p1, f.p2)), t3 = V.unit(V.reject(f.p3, f.p2));
      const sg = Math.sign(K.axisAngle(f.p2, t1, t3)) || 1, zs = V.scale(f.p2, F.J2 + 8);
      const tab = (dir, r0, r1) => ({ a: V.madd(zs, dir, r0), b: V.madd(zs, dir, r1) });
      const sLo = M.mulv(M.rot(f.p2, sg * A_lo), t1), sHi = M.mulv(M.rot(f.p2, sg * A_hi), t1);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(c, F.R0 - 3), z: c, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J0 (O20, cap pole, own-angle stops)', c: V.scale(c, F.R0), axis: c, r: R.R0, h },
        { kind: 'ring', role: 'link', name: 'J0 centring spring (preloaded double-leg torsion spring)', c: V.scale(c, F.R0 + 6), axis: c, r: R.R0 + 3, t: 1.3 },
        { kind: 'arc', role: 'link', name: 'link 0 (12 x 3 Ti, cap pole to the rim)', pts: profArc(c, f.p1, P.lvr, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, on the cap rim)', c: V.scale(f.p1, F.J1), axis: f.p1, r: R.J1, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti, over link 0)', pts: profArc(f.p1, f.p2, P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, own-angle fold stops)', c: V.scale(f.p2, F.J2), axis: f.p2, r: R.J2, h: h + P.lift2 },
        Object.assign({ kind: 'link', role: 'link', name: 'J2 low stop (on link 1)', r: 1.8 }, tab(sLo, R.J2 + 0.5, R.J2 + 5)),
        Object.assign({ kind: 'link', role: 'link', name: 'J2 high stop (on link 1)', r: 1.8 }, tab(sHi, R.J2 + 0.5, R.J2 + 5)),
        Object.assign({ kind: 'link', role: 'link', name: 'J2 stop dog (on link 2)', r: 1.8 }, tab(t3, R.J2 + 0.5, R.J2 + 6)),
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1, link 0 and the neck)', pts: profArc(f.p2, f.p3, P.lv2, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, humerus-fixed)', c: V.scale(f.p3, F.J3), axis: f.p3, r: R.J3, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, member 3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

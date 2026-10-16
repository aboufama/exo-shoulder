/* stop-relay-rocker-3r - DRAWN FROM THE CURRENT MODEL FILE while the screening agent is still modelling it
 * (docs/concepts/models/stop-relay-rocker-3r.py as of 2026-10-16 05:03 UTC; rows/stop-relay-rocker-3r.json "in
 * progress": best so far 35.24 Bench(60,160) fast = the model PARAMS + end_extra 1.02, lift2 1.0; CMA still running, so
 * this preview shows that config and will be redrawn when the row settles).
 * The spine-parked spherical 3R (CMA-B seats: J1 home axis u1r = bvec(102.78, 65.35), J3 wdir(84.49, -12.76) in the
 * humerus, arcs a1 40.68 / a2 73.76 deg, sigma -1, slim O15 J2 / J3) with J1 on a SPRING-CENTRED PASSIVE ACROMIAL ROCKER:
 * R0 = a passive pivot (slim O15 hub, MR117-2RS pair, AS5600 sensed) whose axis c passes through GH (c = u1r tilted
 * beta 30 deg about a normal turned phi 330 deg about u1r), two opposed preloaded torsion springs centre it (|q0| <= 75).
 * J2 has HARD STOPS a margin short of its fold: angle(u1, u3) in [lo, hi] = [|a1 - a2| + 10, a1 + a2 - 10] deg.
 * The relay (model relay()): mode A, J2 inside its stops -> the rocker sits on its centre (q0 = 0, the preload holds
 * it) and the chain IS the spine-parked 3R; mode B / C, the arm asks for more than the stop allows -> J2 sits on its
 * high / low stop and the rocker turns by the least |q0| that keeps angle(u1, u3) = hi / lo (the spring's energy
 * minimum on the feasible arc); the rocker sub-chain keeps >= 10 deg of fold margin. Every axis passes through GH.
 * 3 ACTIVE (J1, J2, J3) + 1 PASSIVE rotation (R0, set by the relay: the 4th residual entry); 0 passive translations.
 * Drawn: the pivot hub with its centring springs (orange ring), the rocker strap c -> J1, the two J2 stop blocks fixed
 * on link 1 and the dog fixed on link 2 (they meet when J2 is on a stop), hub and strap levels = the model's fitted
 * levels at that config (F 50.3 / 52 / 60.1 / 71 mm, hub 2 with the 1 mm lift2 spacer).
 * Frames the relay cannot take are drawn at the nearest physical state (rocker root continuous with the previous frame,
 * clamped to its +-75 deg end stops) and show red. Measured on the loop: lateral abduction needs the rocker at
 * ~+-90 deg (both roots past the end stops: red), and on the way to "across the body" the model's least-|q0| rule picks
 * the OTHER root (-72 deg) while the rocker sits on its +75 end stop: a 147 deg switch the model takes pose by pose
 * (static bench poses) but a real rocker cannot follow on this path - that frame is flagged red, not smoothed. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { az: 102.78, el: 65.35, a1: 40.68, a2: 73.76, wd: 84.49, wa: -12.76, sigma: -1, beta: 30, phi: 330,
              m_lo: 10, m_hi: 10, m_sw: 10, qmax: 75, lift2: 1.0, end_extra: 1.02,
              faces: { R0: 50.3, J1: 52.0, J2: 60.1, J3: 71.0 }, hub_r: { R0: 7.5, J1: 10, J2: 7.5, J3: 7.5 }, stack: 12.25, cuff_at: 165,
              // fitted underside level (mm from GH) at 11 stations along each member (model prof at this config, Bench(60,160) fast)
              lvr: [53.5, 53.5, 53.5, 53.5, 53.5, 47.0, 52.0, 52.0, 52.0, 52.0, 52.0],
              lv1: [55.1, 55.1, 55.1, 55.1, 57.5, 57.5, 57.5, 60.1, 60.1, 60.1, 60.1],
              lv2: [64.2, 64.2, 60.6, 60.1, 62.0, 63.0, 65.0, 66.1, 73.1, 77.5, 74.2],
              lvn: [71.0, 71.0, 73.0, 76.0, 77.5, 80.5, 83.0, 84.6, 88.5, 90.5, 94.1] };
  const u1r = K.bvec(P.az, P.el), w3 = K.wdir(P.wd, P.wa);
  const cS = (function () {                                    // model pivot_dir(): c in the scapula frame
    const ref = V.unit(V.cross(u1r, [0, 1, 0])), ax = M.mulv(M.rot(u1r, P.phi), ref);
    return V.unit(M.mulv(M.rot(ax, P.beta), u1r));
  })();
  const lo = Math.abs(P.a1 - P.a2) + P.m_lo, hi = P.a1 + P.a2 - P.m_hi;
  const C = K.sph3r(u1r, w3, P.a1, P.a2, P.sigma);            // the 3R on the rocker (home J1 = u1r)
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
             why: mg <= 0 ? 'no rocker root' : (mg < P.m_sw ? 'rocker within ' + P.m_sw + ' deg of its own fold' : 'rocker on its end stop') };
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
    id: 'stop-relay-rocker-3r',
    name: 'Stop-relay rocker 3R (spring-centred acromial rocker under J1)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => { const r = relay(ctx); return [r.q0].concat(C.solve(onRocker(ctx, r.q0))); },
    qNames: ['R0 (rocker, passive)', 'J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve: (ctx, qPrev) => solveRelay(ctx, qPrev),
    residual: (q, ctx) => C.residual(q.slice(1), onRocker(ctx, q[0])).concat([K.wrap180(q[0] - relay(ctx, q[0]).q0)]),
    check: (q, ctx) => {
      const r = relay(ctx);
      if (!r.ok) return `J2 on its ${r.mode === 'B' ? 'high' : 'low'} stop and the rocker cannot relay (${r.why})`;
      if (flip.has(ctx)) return `relay root switch: the least-|q0| rule jumps the rocker ${flip.get(ctx).toFixed(0)} deg (taken statically by the model; a real rocker cannot follow on this path)`;
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
        { kind: 'hub', role: 'passive', name: 'R0 rocker pivot (slim O15, AS5600 sensed)', c: V.scale(c, F.R0), axis: c, r: R.R0, h },
        { kind: 'ring', role: 'passive', name: 'R0 centring springs (opposed preloaded torsion pair)', c: V.scale(c, F.R0 + 6), axis: c, r: R.R0 + 3, t: 1.3 },
        { kind: 'arc', role: 'link', name: 'rocker (12 x 3 Ti, arc 30 deg)', pts: profArc(c, f.p1, P.lvr, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, rides the rocker)', c: V.scale(f.p1, F.J1), axis: f.p1, r: R.J1, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti, over the rocker)', pts: profArc(f.p1, f.p2, P.lv1, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (slim O15, hard stops, 1 mm spacer)', c: V.scale(f.p2, F.J2), axis: f.p2, r: R.J2, h: h + P.lift2 },
        Object.assign({ kind: 'link', role: 'link', name: 'J2 low stop (on link 1)', r: 1.8 }, tab(sLo, R.J2 + 0.5, R.J2 + 5)),
        Object.assign({ kind: 'link', role: 'link', name: 'J2 high stop (on link 1)', r: 1.8 }, tab(sHi, R.J2 + 0.5, R.J2 + 5)),
        Object.assign({ kind: 'link', role: 'link', name: 'J2 stop dog (on link 2)', r: 1.8 }, tab(t3, R.J2 + 0.5, R.J2 + 6)),
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, over link 1, the rocker and the neck)', pts: profArc(f.p2, f.p3, P.lv2, 1.5), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (slim O15)', c: V.scale(f.p3, F.J3), axis: f.p3, r: R.J3, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (K7 14 x 6, member 3)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();

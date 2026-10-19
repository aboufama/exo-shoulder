/* pinknee-scapular-relay-4r - the verified pin-knee 3R (H1, skin-normal-3r-pin-knee) with its J1 seat carried by a
 * spring-centred O20 J0 (docs/concepts/models/pinknee-scapular-relay-4r.py; shown at azu 265 / a0 25 / T 40 = the
 * near-pole cap placement in hub 2's free sector: 32.83 Bench(60,160) fast, dead at gate 0).
 * J0 (counted joint, O20, axis c0 on a GH ray, scapula-fixed housing, preloaded torsion spring + own-angle stops +-T_eff)
 * -> link 0 (12 x 3 Ti, fitted) -> J1 -> link 1 -> J2 (own-angle stops at th margin 5) -> link 2 -> J3 (skin-normal tilt)
 * -> E strap -> knee pin a -> knee link -> pin b -> arm pad (two-pin knee, outside the DOF count).
 * Clamp determination (model / tools/spare_flood Cfg 'clamp'): J2 strictly inside its stops -> q0 = 0 (the host chain);
 * J2 on a stop -> J0 turns the least |q0| that brings angle(J1, J3) back inside [lo, hi]; the J0-J1-J3 sub-chain keeps
 * >= m_sw of fold margin. The whole host chain is the host's own chain for Q' = Rc^T Q, mapped back with Rc = R(c0, q0).
 * Geometry exported from the model's fit on Bench(60,160) (hub levels f, f0, knee level, fitted link centrelines).
 * Red = the J2 fold beyond the relay's travel, the sub-chain fold, the knee window, or the radial drift. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  // best configuration (bench model parameters) and the home-frame geometry the model builds from it (exported from the
  // model's Design / fit on Bench(60,160): axis directions u, line points c, hub face levels f along u, hub 3's plane
  // basis sa / st / sn = u3, mid drift m, knee level tr, pin a / pin b home points, fitted link centrelines)
  const P = {"az1": 101.1634, "el1": 63.8986, "az2": 30.153, "el2": 47.0108, "wd": 70.3931, "wa": -8.1248, "b3": 0.2842, "lE": 59.5534, "lc": 28.2401, "phiE": -5.8107, "phib": -54.914, "stk": 5.6815, "ang_min": 30.4611, "azu": 265, "a0": 25, "T": 40};
  const G = {"u": [[0.08518, 0.89802, 0.43164], [-0.57761, 0.6727, 0.46243], [-0.09125, -0.19853, 0.97584]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.793, -10.319, -2.267]], "sa": [0.01848, -0.9801, -0.19766], "st": [0.99566, 0.0, 0.0931], "sn": [-0.09125, -0.19853, 0.97584], "A": [41.018, 68.259], "branch": -1.0, "m": [-9.209, 1.988, 0.0], "f": [49.91, 61.28, 77.17], "tr": 84.74, "tp": 2.591, "RUN": 0.5, "SING": 5.0, "hr": [10.0, 10.0, 10.0], "A0": [-6.701, -68.387, -14.539], "A0m": [-4.891, -59.361, -12.534], "Bm": [-27.599, -75.27, -17.894], "eE": [-0.08241, -0.97506, -0.20607], "eK": [-0.80411, -0.56336, -0.1898], "L1": [[-6.01, 44.75, 23.73], [-8.55, 44.42, 24.12], [-11.28, 44.73, 24.88], [-15.18, 45.0, 25.86], [-20.11, 46.06, 27.46], [-25.17, 48.89, 29.96]], "L2": [[-34.75, 34.83, 38.16], [-32.92, 30.3, 41.06], [-32.46, 27.08, 45.6], [-31.79, 24.05, 49.17], [-31.0, 20.84, 52.76], [-29.78, 16.65, 56.86], [-28.02, 12.0, 60.21], [-26.38, 7.94, 62.84], [-24.32, 3.66, 64.62], [-21.45, -1.57, 65.8], [-18.41, -6.8, 66.49], [-16.52, -11.69, 69.94], [-15.42, -16.39, 75.95]], "L0": [[3.24, 53.0, 10.23], [3.41, 50.64, 12.42], [3.68, 51.85, 14.34]], "c0": [0.04014, 0.99911, 0.01314], "f0": 50.06, "T": 16.0, "lo": 32.241, "hi": 104.277, "m_sw": 5.0, "a0": 25.0};
  const u = G.u, c = G.c, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;     // knee assembly branch (build posture)
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  /** the model's closed-form IK (seed S.Design.ik): Q = band HG -> q1..q3 (deg), fold ok, member transforms, drift s */
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), c12 = V.dot(u1, u2), b1 = V.dot(w, u1), b2 = V.dot(u2, u3), det = 1 - c12 * c12;
    const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, u2);
    const g2 = (1 - al * al - be * be - 2 * al * be * c12) / V.dot(cr, cr), th = V.angle(w, u1);
    const margin = Math.min(th - Math.abs(a1 - a2), Math.min(a1 + a2, 360 - a1 - a2) - th);
    let pick = null;
    for (const sg of [1, -1]) {
      const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
      const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, z), p2 = M.mulv(M.rot(u1, q1), u2);
      const br = Math.sign(V.dot(p2, V.cross(u1, w)));
      if (pick === null || br === G.branch) pick = [q1, q2];
    }
    return { q1: pick[0], q2: pick[1], ok: margin >= G.SING && g2 > 0, margin };
  }
  /** member transforms from joint angles (deg): lines through c1, c2, c3 (J1 / J2 lines pass GH) */
  function chain(q1, q2, q3) {
    const R1 = M.rot(u[0], q1), R2 = M.rot(u[1], q2), R12 = M.mul(R1, R2), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t1 = V.sub(c[0], M.mulv(R1, c[0]));
    const t2 = V.add(M.mulv(R1, V.sub(V.sub(c[1], M.mulv(R2, c[1])), c[0])), c[0]);
    const t3 = V.add(M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))), t2);
    return { R1, t1, R12, t2, R123, t3 };
  }
  /** planar RRR knee in hub 3's plane (model Design.knee): drift s -> E angle th, pin a, knee link angle psi, knee angle */
  function knee(s) {
    const vx = B2[0] - s[0], vy = B2[1] - s[1], d = Math.hypot(vx, vy), gam = Math.atan2(vy, vx);
    const ca = (lE * lE + d * d - lc * lc) / (2 * lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca)));
    const th = gam + kbr * al, pa = [s[0] + lE * Math.cos(th), s[1] + lE * Math.sin(th)];
    const wx = B2[0] - pa[0], wy = B2[1] - pa[1], psi = Math.atan2(wy, wx);
    const cosk = ((s[0] - pa[0]) * wx + (s[1] - pa[1]) * wy) / (lE * lc), ang = Math.acos(Math.max(-1, Math.min(1, cosk))) / D2R;
    return { th, pa, psi, ang, d, phi: wrapR(th - pe), span: d >= Math.abs(lE - lc) + 1 && d <= lE + lc - 1 };
  }
  const QofT = ctx => M.mul(M.T(ctx.S), ctx.H);                     // band HG: the arm's rotation in the scapula frame
  const c0 = G.c0, u1r = u[0];
  /** clamp relay (spare_flood Cfg.static_q): least |q0| (0.5-deg grid, |q0| <= T) with lo <= angle(J1, J3) <= hi */
  function relay(ctx) {
    const w = M.mulv(QofT(ctx), u[2]); let best = null;
    for (let k = 0; k <= 2 * G.T; k++) {
      for (const sg of (k ? [1, -1] : [1])) {
        const q0 = sg * k * 0.5; if (Math.abs(q0) > G.T) continue;
        const th = V.angle(M.mulv(M.rot(c0, q0), u1r), w);
        if (th >= G.lo && th <= G.hi) { best = q0; break; }
      }
      if (best !== null) break;
    }
    if (best === null) return { q0: 0, ok: false };
    if (best !== 0) {
      const th = V.angle(M.mulv(M.rot(c0, best), u1r), w), ths = th > (G.lo + G.hi) / 2 ? G.hi : G.lo, g = V.angle(c0, w);
      const sm = Math.min(g - Math.abs(G.a0 - ths), G.a0 + ths - g, 360 - G.a0 - ths - g);
      if (sm < G.m_sw) return { q0: best, ok: false, sub: true };
    }
    return { q0: best, ok: true };
  }
  const Rc = ctx => M.rot(c0, relay(ctx).q0);
  const Qof = ctx => M.mul(M.T(Rc(ctx)), QofT(ctx));             // the host chain sees Q' = Rc^T Q
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.rot(u[0], k.q1), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.q2, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    // q: J1, J2, J3 (link 2 -> member 3 = q3 + phi), pin a (member 3 -> knee link), pin b (knee link -> arm), from home
    return [k.q1, k.q2, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  /** forward kinematics of the whole loop from q: every member, pin a, pin b and the arm it implies */
  function fk(q) {
    const X = chain(q[0], q[1], q[2]), Rm3 = X.R123;                // member 3 = hub 3's lower plate + E strap + E boss
    const pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[3])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[4])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const rl = relay(ctx);
    if (!rl.ok) return rl.sub ? 'J0-J1-J3 sub-chain within ' + G.m_sw + ' deg of its own fold' : 'J2 fold beyond the relay travel (|q0| <= ' + G.T + ')';
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.margin < 0 ? 'J2 fold' : `J2 within ${k.margin.toFixed(0)} deg of its fold (>= ${G.SING})`;
    q = q.slice(1);
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    if (Math.abs(V.dot(sv, sn)) > 0.5) return 'radial drift > 0.5 mm';
    return null;
  };
  /** a frame the loop cannot close (fold, knee out of span) is shown at the least-squares nearest configuration
   *  warm-started from the previous frame (continuous, drawn red), not at the clipped closed form */
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solve4 = ctx => [relay(ctx).q0].concat(solve(ctx));
  const solveC = (ctx, qPrev) => solve4(ctx);
  const C = {
    id: 'pinknee-scapular-relay-4r', name: 'Pin-knee 3R on a spring-centred scapular relay J0 (4 joints, 0 passive translations)',
    dof: { active: 4, passive: 2 },
    params: P,
    q0: ctx => solve4(ctx),
    qNames: ['J0 (spring-centred relay)', 'J1', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm', 'deg'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q.slice(1)); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5).concat([K.wrap180(q[0] - relay(ctx).q0)]); },   // arm pose implied by the loop vs the arm
    check,
    parts: (q, ctx) => {
      const R0 = M.rot(c0, q[0]), S = M.mul(ctx.S, R0), W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q.slice(1));
      const on = (R, t, p) => W(V.add(M.mulv(R, p), t)), I = M.I3(), Z = [0, 0, 0];
      const hp = (R, t, k) => on(R, t, V.madd(c[k], u[k], G.f[k]));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: hp(I, Z, 0), axis: Wd(u[0]), r: rad, h: hub };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray)', c: hp(F.R1, F.t1, 1), axis: Wd(M.mulv(F.R1, u[1])), r: rad, h: hub };
      const ax3 = Wd(M.mulv(F.R12, u[2]));
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: hp(F.R12, F.t2, 2), axis: ax3, r: rad, h: hub,
                   p0: on(F.R12, F.t2, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn));                              // pin axis direction (all pins parallel to J3)
      const lvl = (p, h) => V.madd(W(p), n3, h);
      const paW = F.pa, pbW = F.pb, kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = on(F.Rm3, F.t3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad)));
      const arm = p => M.mulv(ctx.H, p);                             // arm-fixed home point -> world (= S Q p)
      const padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn);
      const lat = arm([G.Bm[0], -150, 50]);
      const c0W = M.mulv(ctx.S, c0), h0c = V.scale(c0W, G.f0);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler (carries hub 0)', c: V.madd(h0c, c0W, -3), z: c0W, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J0 (O20 relay, spring-centred, own-angle stops)', c: h0c, axis: c0W, r: rad, h: hub },
        { kind: 'ring', role: 'link', name: 'J0 centring spring (preloaded double-leg torsion spring)', c: V.scale(c0W, G.f0 + 6), axis: c0W, r: rad + 3, t: 1.3 },
        { kind: 'arc', role: 'link', name: 'link 0 (12 x 3 Ti, fitted; carries hub 1)', pts: G.L0.map(p => W(p)), r: 2.5 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1 (8 x 3 strap, fitted)', pts: G.L1.map(p => on(F.R1, F.t1, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, F.t2, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(paW, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (iglidur pin, parallel to J3)', c: lvl(paW, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(paW, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(paW, kz), b: lvl(pbW, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (iglidur pin, parallel to J3)', c: lvl(pbW, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(pbW, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();

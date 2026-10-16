/* minarc-stop-knuckle-4r (variant B) under the KIT fold rule with the BUILDABLE J2 stop - the pin-knee chain (J1 / J2 on GH
 * rays, J3 tilted toward the skin normal, a flat two-pin knee closing member 3 on the cuff) with link 1 split by a 4th,
 * PASSIVE, sensed O20 hub K held on its stop A by a preloaded clock spring (0.3 x 5 mm strip, cap 6 mm taller), and a
 * dowel-in-slot stop on J2's OWN angle q2. While the J1-J3 angle th stays inside [thLo, thHi] (5+ deg of J1-J3 fold
 * margin, the kit's rule) K stays on stop A (a rigid 3R); past it J2 sits on its stop and the arm opens K to the smallest
 * rotation that closes the chain (closed form, <= stop B). Exactly docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py
 * (phys 1) at BDp, the kit-rule claim (the claim's BD seats, both J2 stops at the 5-deg J1-J3 margin, frozen exact 19.06) (axis directions, line points, hub levels, knee level, link centrelines exported from the
 * model's fit on Bench(60,160)). Red = K would pass stop B / the knee outside its window. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 95.4669, "el1": 67.7011, "az2": 47.212, "el2": 39.8943, "wd": 59.8224, "wa": -9.0298, "b3": 0.4579, "lE": 64.6617, "lc": 30.3886, "phiE": -1.5412, "phib": -69.7597, "stk": 5.2691, "ang_min": 24.9512, "bk1": 30.1634, "bk2": 47.0063, "sK": -1.0, "a1max": 66.1587, "smlo": 5.0, "smhi": 5.0, "capK": 6.0};
  const G = {"u": [[0.03615, 0.92522, 0.37771], [-0.45199, 0.5985, 0.66144], [-0.064, -0.24941, 0.96628]], "uK": [-0.28481, 0.9581, -0.03059], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-3.25576, -21.89016, -5.86581]], "sa": [0.01648, -0.9684, -0.24887], "st": [0.99781, 0.0, 0.06609], "sn": [-0.064, -0.24941, 0.96628], "A": [38.072, 58.749], "branch": -1.0, "m": [-19.82913, 3.62885, 0.0], "f": [49.42, 62.05, 81.59], "fK": 56.22, "capK": 6.0, "tr": 88.3, "tp": 2.385, "RUN": 0.5, "SING": 5.0, "hr": [10.0, 10.0, 10.0], "A0": [-3.92563, -84.48575, -22.067], "A0m": [-0.63156, -65.28327, -16.89238], "Bm": [-28.90804, -75.46422, -21.39308], "eE": [-0.01036, -0.96805, -0.25055], "eK": [-0.9305, -0.33503, -0.1481], "psiA": -57.4652, "dKB": 62.8267, "thLo": 25.6772, "thHi": 91.8206, "q2s": [100.8425, -24.9789], "L1a": [[-5.25, 49.25, 10.71], [-6.94, 52.6, 9.69], [-8.86, 56.31, 8.52]], "L1b": [[-20.89, 56.03, 8.72], [-19.71, 49.03, 11.18], [-20.78, 48.04, 14.59], [-21.73, 46.73, 17.96], [-22.67, 45.37, 21.35], [-23.61, 43.94, 24.79], [-25.88, 44.72, 29.84]], "L2": [[-29.02, 31.75, 50.02], [-26.71, 26.89, 48.7], [-26.45, 24.23, 50.94], [-26.16, 21.48, 53.18], [-25.93, 18.71, 55.63], [-25.68, 15.83, 58.16], [-25.3, 12.75, 60.51], [-24.73, 9.47, 62.54], [-23.99, 6.03, 64.25], [-23.23, 2.49, 65.99], [-22.22, -1.17, 67.16], [-21.07, -4.9, 67.98], [-19.84, -8.68, 68.62], [-18.43, -12.43, 68.67], [-16.87, -16.09, 68.2], [-15.33, -19.76, 67.77], [-14.32, -24.41, 70.09], [-13.74, -30.7, 75.49]]};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, sa = G.sa, st = G.st, a1 = G.A[0], a2 = G.A[1], hub = 12.25, rad = 10;
  const wrapR = a => { a = (a + Math.PI) % (2 * Math.PI); return (a < 0 ? a + 2 * Math.PI : a) - Math.PI; };
  const pe = P.phiE * D2R, pb = P.phib * D2R, lE = P.lE, lc = P.lc;
  const A02 = [G.m[0] + lE * Math.cos(pe), G.m[1] + lE * Math.sin(pe)], B2 = [A02[0] + lc * Math.cos(pb), A02[1] + lc * Math.sin(pb)];
  const kbr = Math.sign(wrapR(pe - Math.atan2(B2[1] - G.m[1], B2[0] - G.m[0]))) || 1;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R), sb = x => Math.sin(x * D2R);
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
  const dot = V.dot;
  function ik(Q) {
    const [u1, u2, u3] = u, w = M.mulv(Q, u3), th = V.angle(w, u1);
    if (th >= G.thLo && th <= G.thHi) {
      const c12 = dot(u1, u2), b1 = dot(w, u1), b2 = cb(a2), det = 1 - c12 * c12;
      const al = (b1 - c12 * b2) / det, be = (b2 - c12 * b1) / det, cr = V.cross(u1, u2);
      const g2 = (1 - al * al - be * be - 2 * al * be * c12) / dot(cr, cr);
      let pick = null;
      for (const sg of [1, -1]) {
        const z = V.madd(V.add(V.scale(u1, al), V.scale(u2, be)), cr, sg * Math.sqrt(Math.max(g2, 0)));
        const q1 = K.axisAngle(u1, z, w), q2 = K.axisAngle(u2, u3, z), p2 = M.mulv(M.rot(u1, q1), u2);
        const br = Math.sign(dot(p2, V.cross(u1, w)));
        if (pick === null || br === G.branch) pick = [q1, q2];
      }
      return { q1: pick[0], dK: 0, q2: pick[1], ok: g2 > 0, L: { state: 0 } };
    }
    const state = th > G.thHi ? 1 : -1, q2s = state === 1 ? G.q2s[1] : G.q2s[0], p = M.mulv(M.rot(u2, q2s), u3);
    const A0 = dot(u1, uK) * dot(uK, p), Bk = dot(u1, p) - A0, Ck = dot(u1, V.cross(uK, p));
    const x = (cb(th) - A0) / Math.hypot(Bk, Ck), f0 = Math.atan2(Ck, Bk) / D2R, sp = Math.sign(G.psiA);
    let dK = sp * G.dKB, ok = false;
    if (Math.abs(x) <= 1) {
      const g = Math.acos(x) / D2R; let best = Infinity;
      for (const r0 of [f0 - g, f0 + g]) { const r = K.wrap180(r0); if (r * sp >= -1e-9 && Math.abs(r) < best) best = Math.abs(r); }
      if (best <= G.dKB + 1e-9) { dK = sp * best; ok = true; }
    }
    const q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
    return { q1, dK, q2: q2s, ok, L: { state } };
  }
  function chain(q1, dK, q2, q3) {
    const R1 = M.rot(u[0], q1), R1b = M.mul(R1, M.rot(uK, dK)), R12 = M.mul(R1b, M.rot(u[1], q2)), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));
    return { R1, R1b, R12, R123, t3 };
  }
  function knee(s) {
    const vx = B2[0] - s[0], vy = B2[1] - s[1], d = Math.hypot(vx, vy), gam = Math.atan2(vy, vx);
    const ca = (lE * lE + d * d - lc * lc) / (2 * lE * Math.max(d, 1e-9)), al = Math.acos(Math.max(-1, Math.min(1, ca)));
    const th = gam + kbr * al, pa = [s[0] + lE * Math.cos(th), s[1] + lE * Math.sin(th)];
    const wx = B2[0] - pa[0], wy = B2[1] - pa[1], psi = Math.atan2(wy, wx);
    const cosk = ((s[0] - pa[0]) * wx + (s[1] - pa[1]) * wy) / (lE * lc), ang = Math.acos(Math.max(-1, Math.min(1, cosk))) / D2R;
    return { th, pa, psi, ang, d, phi: wrapR(th - pe), span: d >= Math.abs(lE - lc) + 1 && d <= lE + lc - 1 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref))), X = chain(k.q1, k.dK, k.q2, q3);
    const sv = M.mulv(M.T(Q), X.t3), s = [V.dot(sv, sa), V.dot(sv, st), V.dot(sv, sn)], kn = knee(s);
    const R = x => K.wrap180(x / D2R);
    return [k.q1, k.dK, k.q2, K.wrap180(q3 + kn.phi / D2R), R(wrapR(kn.psi - pb - kn.phi)), R(wrapR(kn.psi - pb))];
  }
  function fk(q) {
    const X = chain(q[0], q[1], q[2], q[3]), Rm3 = X.R123, pa = V.add(M.mulv(Rm3, G.A0), X.t3);
    const R6 = M.mul(Rm3, M.rot(sn, q[4])), t6 = V.sub(pa, M.mulv(R6, G.A0m));
    const pbW = V.add(M.mulv(R6, G.Bm), t6), R5 = M.mul(R6, M.rot(sn, -q[5])), t5 = V.sub(pbW, M.mulv(R5, G.Bm));
    return Object.assign(X, { Rm3, R6, t6, R5, t5, pa, pb: pbW });
  }
  const check = (q, ctx) => {
    const Q = Qof(ctx), k = ik(Q);
    if (!k.ok) return k.L.state ? `J2 on its q2 stop: K would pass stop B (a1max ${P.a1max} deg)` : 'chain cannot close';
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'minarc-stop-knuckle-4r', name: 'Min-arc stop knuckle on the pin knee: spring-held passive K in link 1, J2 dowel stop on q2 (kit fold rule)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, spring + stops)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, sensed; clock-spring cap, stop A)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray, dowel-in-slot stop on q2)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (skin-normal tilt, line misses GH)', c: on(F.R12, V.madd(c[2], u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub,
                   p0: on(F.R12, c[2]) };
      const n3 = Wd(M.mulv(F.Rm3, sn)), lvl = (p, h) => V.madd(W(p), n3, h), kz = G.tr + G.tp + G.RUN + G.tp / 2;
      const rim = W(V.add(M.mulv(F.Rm3, V.add(V.madd(c[2], sn, G.f[2] + 1.5), V.scale(G.eE, rad))), F.t3));
      const arm = p => M.mulv(ctx.H, p), padC = arm(V.madd(G.Bm, sn, G.tr + G.tp / 2)), padN = M.mulv(ctx.H, sn), lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1a (8 x 3 strap, J1 -> K)', pts: (G.L1a.length ? G.L1a : [V.scale(u[0], G.f[0]), V.scale(uK, G.fK)]).map(p => on(F.R1, p)), r: 2.5 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 1b (8 x 3 strap, K -> J2)', pts: G.L1b.map(p => on(F.R1b, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, p)), r: 2.5 },
        h3,
        { kind: 'link', role: 'link', name: 'E strap (member 3: hub 3 lower plate -> pin a)', a: rim, b: lvl(F.pa, G.tr + 1.5), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'knee pin a (iglidur pin, parallel to J3)', c: lvl(F.pa, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pa, G.tr) },
        { kind: 'link', role: 'link', name: 'knee link (flat Ti plate)', a: lvl(F.pa, kz), b: lvl(F.pb, kz), r: 3 },
        { kind: 'hub', role: 'passive', name: 'knee pin b (iglidur pin, parallel to J3)', c: lvl(F.pb, G.tr), axis: n3, r: 6, h: P.stk, p0: lvl(F.pb, G.tr) },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (on the cuff / BOTTOM)', c: padC, z: padN, x: arm(sa), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, padN, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();

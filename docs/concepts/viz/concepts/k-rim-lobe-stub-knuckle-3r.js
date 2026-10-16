/* k-rim-lobe-stub-knuckle-3r at its best measured configuration (Bench(60,160) fast near-touch 36.82, reach 0.6937, in band 0.8269).
 * The pin-knee chain with link 1 split by a passive O20 knuckle K that is SLAVED to q2 by ONE direct higher pair: a lobe
 * sector on link 1a around hub K and an MR52ZZ roller on a short stub of link 2 at hub 2 (on an O2 post when the lobe sits
 * beside link 1b). Past the stretched onset the roller opens K by dK = kK t (t = q2 travel) up to the q2 dowel stop B; the
 * clock spring keeps the lobe on the roller. J1, J2, J3 encoders give the pose (3 active, K never read). Folded side: J2
 * dowel stop. Geometry exported from docs/concepts/models/k-rim-lobe-stub-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 93.5546, "el1": 67.3642, "az2": 43.4586, "el2": 43.3068, "wd": 63.337, "wa": -9.6473, "b3": 0.3837, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "ang_min": 27.8544, "bk1": 33.191, "bk2": 39.926, "sK": -1, "a1max": 48.0, "smhi": 22.126, "smlo": 5.2777, "capK": 6.0, "emb_mode": "kstub", "kK": 0.825, "L_stub": 24.487, "a0": 146.225, "rr": 2.5, "lobe_w": 3.493, "lobe_lev": 0, "tip_tol": 3.087};
  const G = {"u": [[0.02386, 0.92297, 0.38413], [-0.47582, 0.64318, 0.59993], [-0.09951, -0.23654, 0.96651]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-1.97854, -17.4181, -4.46644]], "uK": [-0.38383, 0.92327, -0.01598], "sa": [0.02422, -0.97162, -0.23529], "st": [0.99474, 0.0, 0.10241], "sn": [-0.09951, -0.23654, 0.96651], "A": [35.636, 61.637], "branch": -1.0, "m": [-14.1944, 2.40896, 0.0], "f": [49.34, 60.24, 79.61], "fK": 58.04, "capK": 6.0, "tr": 88.11, "tp": 2.177, "RUN": 0.5, "A0": [-3.61735, -83.24731, -20.74558], "A0m": [-1.5649, -69.45571, -17.15904], "Bm": [-24.70614, -79.78874, -22.07033], "eE": [-0.02416, -0.97047, -0.23999], "psiA": -60.8802, "thLo": 31.2787, "thHi": 75.1472, "q2s": [93.3985, 12.6859], "lawTh": [75.147, 75.979, 76.819, 77.668, 78.524, 79.387, 80.257, 81.132, 82.013, 82.899, 83.79, 84.684, 85.582, 86.482, 87.385, 88.289, 89.195, 90.101, 91.007, 91.913, 92.817, 93.72, 94.621, 95.519, 96.413, 97.304, 98.19, 99.07, 99.945, 100.813], "lawDK": [-0.0, -0.825, -1.65, -2.475, -3.3, -4.125, -4.95, -5.775, -6.6, -7.425, -8.25, -9.075, -9.9, -10.725, -11.55, -12.375, -13.2, -14.025, -14.85, -15.675, -16.5, -17.325, -18.15, -18.975, -19.8, -20.625, -21.45, -22.275, -23.1, -23.925], "lawQ2": [12.686, 11.686, 10.686, 9.686, 8.686, 7.686, 6.686, 5.686, 4.686, 3.686, 2.686, 1.686, 0.686, -0.314, -1.314, -2.314, -3.314, -4.314, -5.314, -6.314, -7.314, -8.314, -9.314, -10.314, -11.314, -12.314, -13.314, -14.314, -15.314, -16.314], "emb": "kstub", "tip": [-20.17, 61.6, 23.39], "tipTop": [-20.61, 62.94, 23.9], "lobe": [[-22.33, 59.78, 18.38], [-19.92, 61.0, 17.1], [-20.11, 59.98, 20.2], [-21.15, 58.85, 22.34], [-18.3, 59.77, 22.43], [-19.72, 58.55, 24.36], [-21.36, 57.38, 25.72], [-18.56, 57.96, 26.58], [-20.39, 56.76, 27.8], [-22.3, 55.62, 28.62], [-19.66, 55.89, 30.0], [-21.69, 54.74, 30.71], [-24.58, 61.02, 9.08], [-21.01, 62.48, 8.01], [-22.35, 61.73, 9.98], [-23.67, 60.89, 11.93], [-20.1, 62.35, 10.87], [-21.42, 61.54, 12.83], [-22.71, 60.63, 14.77], [-19.15, 62.09, 13.7], [-20.45, 61.21, 15.64], [-21.72, 60.25, 17.57], [-18.15, 61.71, 16.5]], "L1a": [[-4.77, 49.23, 10.46], [-9.91, 54.52, 7.06], [-7.36, 48.28, 10.29], [-13.64, 57.32, 7.4], [-10.45, 49.99, 10.69], [-8.57, 47.71, 14.33], [-14.1, 52.85, 11.33]], "L1b": [[-29.62, 54.12, 9.4], [-27.82, 46.99, 13.96], [-28.97, 45.13, 19.5], [-31.74, 45.42, 26.54], [-25.55, 47.88, 12.59], [-26.73, 46.18, 18.1], [-28.04, 44.55, 23.87], [-24.83, 51.9, 11.97], [-24.41, 46.97, 16.64], [-25.34, 44.85, 22.02], [-24.06, 56.46, 11.29], [-22.17, 47.76, 15.24], [-23.04, 45.6, 20.48], [-26.27, 47.73, 28.4]], "L2": [[-32.3, 33.0, 44.66], [-30.47, 23.87, 50.5], [-29.78, 15.17, 58.5], [-27.71, 4.79, 64.61], [-24.2, -6.64, 68.0], [-19.43, -18.21, 68.08], [-28.84, 30.48, 43.82], [-28.54, 22.97, 51.91], [-27.58, 14.1, 59.66], [-25.21, 3.63, 65.34], [-21.33, -7.71, 67.74], [-16.75, -19.34, 68.47], [-27.37, 30.01, 45.8], [-26.65, 22.09, 53.39], [-25.48, 13.09, 61.05], [-22.62, 2.47, 65.73], [-18.42, -8.69, 67.08], [-14.66, -21.35, 71.8], [-25.93, 29.59, 47.93], [-24.99, 21.42, 55.42], [-23.45, 12.12, 62.7], [-20.39, 1.35, 67.17], [-16.0, -9.88, 68.11], [-12.33, -23.44, 75.1]], "LT": [[-24.42, 50.67, 34.84], [-21.89, 59.16, 31.27], [-25.84, 50.2, 33.36], [-23.64, 59.14, 30.01], [-27.46, 50.13, 32.15], [-25.38, 59.06, 28.71], [-29.31, 50.46, 31.2], [-27.09, 58.93, 27.39]]};
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
    const state = th > G.thHi ? 1 : -1;
    if (state === -1) { const q2s = G.q2s[0], p = M.mulv(M.rot(u2, q2s), u3); return { q1: K.axisAngle(u1, p, w), dK: 0, q2: q2s, ok: false, L: { state } }; }
    // stretched: invert the tabulated law th(t) -> (q2, dK)
    const T = G.lawTh, n = T.length; let j = 0;
    while (j < n - 2 && T[j + 1] < th) j++;
    const ok = th <= T[n - 1], a = Math.max(0, Math.min(1, (th - T[j]) / Math.max(T[j + 1] - T[j], 1e-9)));
    const q2s = G.lawQ2[j] + a * (G.lawQ2[j + 1] - G.lawQ2[j]), dK = G.lawDK[j] + a * (G.lawDK[j + 1] - G.lawDK[j]);
    const p = M.mulv(M.rot(u2, q2s), u3), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (q2 dowel at the end of the lobe law)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'k-rim-lobe-stub-knuckle-3r', name: 'Inverse direct pair: lobe sector on link 1a around K, roller on a link-2 stub slaves K to q2 (3 active, K not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the stub roller on the lobe)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; carries the lobe sector)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
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
        { kind: 'arc', role: 'link', name: 'stub of link 2 (8 x 3 Ti, hub 2 -> roller)', pts: (G.LT.length ? G.LT : [V.scale(u[1], G.f[1]), G.tipTop]).map(p => on(F.R12, p)), r: 2 },
        { kind: 'hub', role: 'passive', name: 'MR52ZZ roller on an O2 post (stub tip)', c: on(F.R12, G.tip), axis: Wd(M.mulv(F.R12, V.unit(G.tip))), r: 2.5, h: 3 },
        { kind: 'arc', role: 'link', name: 'lobe sector on link 1a around hub K (3 mm Ti, flank = the roller pitch curve)', pts: G.lobe.map(p => on(F.R1, p)), r: 1.5 },
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

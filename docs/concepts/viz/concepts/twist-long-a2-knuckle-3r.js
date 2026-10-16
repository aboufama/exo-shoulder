/* twist-long-a2-knuckle-3r at its best measured configuration: the verified lead's knuckle chain (pin knee, link 1 split by a
 * passive O20 knuckle K SLAVED to q2 by the hub-2 rim lobe -> rocker -> O3 pushrod -> horn on K's cap) with the J3 axis
 * re-seated (turned about the humerus), a2 re-chosen and the K dyad widened on the bk2 side. 3 active (J1, J2, J3), K never
 * read, 0 passive translations. LHS best (preliminary).
 * Geometry exported from docs/concepts/models/twist-long-a2-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 94.92, "el1": 70.006, "az2": 52.67879787723275, "el2": 41.988953068908565, "wd": 65.3420128756457, "wa": -0.869080169223557, "b3": 0.217, "lE": 73.649, "lc": 23.977, "phiE": -7.59, "phib": -70.065, "stk": 4.8534, "ang_min": 29.154, "bk1": 30.926, "bk2": 44.75, "sK": -1, "a1max": 70.676, "smhi": 12.593, "smlo": 5.1723, "capK": 6.0, "law_mode": "seg", "kA": 2.645, "t1": 10.976, "kB": 2.496, "smt": 12.0, "kK": 3.1796, "i_rock": 1.0, "r_horn": 2.4709, "r_lobe": 7.3499, "arm_lo": 1.0};
  const G = {"u": [[0.02932, 0.93973, 0.34066], [-0.36874, 0.63443, 0.67936], [0.0327, -0.30808, 0.9508]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-2.49109, -8.49172, -2.66582]], "uK": [-0.36205, 0.93191, -0.02142], "sa": [-0.01059, -0.95136, -0.3079], "st": [0.99941, -0.0, -0.03437], "sn": [0.0327, -0.30808, 0.9508], "A": [35.233, 63.997], "branch": -1.0, "m": [-8.10013, 2.37815, 0.0], "f": [48.35, 60.74, 80.97], "fK": 57.97, "capK": 6.0, "tr": 91.71, "tp": 2.177, "RUN": 0.5, "A0": [-12.9862, -77.94461, -24.80907], "A0m": [-10.52368, -70.23847, -22.39681], "Bm": [-33.13723, -78.01589, -24.13914], "eE": [-0.1425, -0.94303, -0.30066], "psiA": -54.9875, "thLo": 33.9363, "thHi": 86.637, "q2s": [103.9267, 3.2212], "lawTh": [86.637, 87.758, 88.915, 90.107, 91.331, 92.585, 93.866, 95.172, 96.501, 97.851, 99.219, 100.602, 101.999, 103.407, 104.807, 106.169, 107.535, 108.9, 110.264, 111.624, 112.977, 114.32, 115.652, 116.969, 118.267, 119.545, 120.799, 122.025, 123.22, 124.381, 125.502, 126.581, 127.614, 128.595, 129.521, 130.387, 131.188, 131.921, 132.581], "lawDK": [-0.0, -2.116, -4.232, -6.348, -8.464, -10.58, -12.696, -14.812, -16.928, -19.044, -21.16, -23.276, -25.392, -27.508, -29.591, -31.587, -33.584, -35.581, -37.578, -39.575, -41.571, -43.568, -45.565, -47.562, -49.559, -51.555, -53.552, -55.549, -57.546, -59.543, -61.539, -63.536, -65.533, -67.53, -69.527, -71.523, -73.52, -75.517, -77.514], "lawQ2": [3.221, 2.421, 1.621, 0.821, 0.021, -0.779, -1.579, -2.379, -3.179, -3.979, -4.779, -5.579, -6.379, -7.179, -7.979, -8.779, -9.579, -10.379, -11.179, -11.979, -12.779, -13.579, -14.379, -15.179, -15.979, -16.779, -17.579, -18.379, -19.179, -19.979, -20.779, -21.579, -22.379, -23.179, -23.979, -24.779, -25.579, -26.379, -27.179], "emb": "rod", "rocker": [-24.1, 48.471, 28.79], "rockerAx": [-0.39307, 0.79057, 0.46957], "rodA": [-31.765, 63.887, 37.946], "rodB": [-24.205, 69.127, -1.568], "armA": [-31.764, 63.887, 37.946], "armB": [-31.765, 63.887, 37.946], "L1a": [[-4.59, 48.65, 8.12], [-10.54, 58.23, 5.08], [-9.72, 54.35, 7.75], [-8.91, 50.45, 10.03], [-8.26, 47.32, 12.11], [-14.93, 56.63, 9.87]], "L1b": [[-26.83, 55.38, 9.58], [-23.82, 46.97, 13.71], [-24.12, 45.31, 19.0], [-24.26, 43.25, 24.22], [-26.88, 45.27, 32.55], [-22.38, 48.88, 12.42], [-22.05, 45.92, 17.3], [-22.31, 44.19, 22.56], [-23.69, 44.47, 29.35], [-21.87, 53.22, 11.61], [-20.07, 46.56, 15.66], [-20.37, 45.0, 20.88], [-20.71, 43.49, 26.34], [-21.09, 57.63, 10.59], [-18.05, 46.97, 14.0], [-18.36, 45.5, 19.14], [-18.77, 44.29, 24.58], [-21.18, 47.5, 33.55]], "L2": [[-24.63, 32.78, 50.07], [-21.69, 23.44, 54.68], [-19.97, 15.04, 62.67], [-17.02, 4.84, 68.02], [-13.19, -6.31, 70.74], [-8.85, -17.96, 71.57], [-20.88, 28.75, 49.33], [-19.38, 21.3, 57.23], [-17.24, 12.41, 64.65], [-14.04, 1.92, 69.7], [-9.98, -9.47, 71.92], [-6.06, -23.86, 80.95], [-18.6, 25.82, 53.59], [-16.88, 17.9, 61.98], [-14.01, 8.05, 68.01], [-10.42, -3.03, 72.72], [-5.88, -14.67, 73.06], [-18.24, 31.54, 49.23], [-16.5, 24.04, 56.8], [-14.39, 15.58, 65.0], [-11.07, 5.2, 70.04], [-7.14, -6.23, 74.34], [-2.41, -18.28, 75.04]]};
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
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (stop B / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel (no tooth)' : 'chain cannot close');
    const F = fk(q), sv = M.mulv(M.T(Q), F.t3), kn = knee([V.dot(sv, sa), V.dot(sv, st)]);
    if (!kn.span) return 'knee span: the drift is beyond lE + lc';
    if (kn.ang < P.ang_min || kn.ang > 180 - P.ang_min) return `knee angle ${kn.ang.toFixed(0)} deg outside [${P.ang_min}, ${180 - P.ang_min}]`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'twist-long-a2-knuckle-3r', name: 'J3 re-seat for reach on the knuckle drive: J3 axis turned about the humerus, a2 re-chosen, K dyad widened (3 active, K slaved, not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe-rocker-pushrod drive)', 'J2', 'J3', 'knee pin a', 'knee pin b'], qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R5, Qof(ctx)).concat(F.t5); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const on = (R, p) => W(M.mulv(R, p)), I = M.I3();
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap with the pushrod horn, stop A)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
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
        { kind: 'hub', role: 'passive', name: 'follower post (O10 on link 1b, 1:1; rides the lobe on hub 2 rotor rim; its rod end raised to clear hub K crown)', c: on(F.R1b, G.rocker), axis: Wd(M.mulv(F.R1b, G.rockerAx)), r: 5, h: 9 },
        { kind: 'link', role: 'link', name: 'O3 pushrod with M3 rod ends (post -> horn on K cap, over hub K crown)', a: on(F.R1b, G.rodA), b: on(F.R1b, G.rodB), r: 1.5 },
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

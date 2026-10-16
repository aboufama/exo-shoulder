/* kneeless-roller-knuckle-3r at its best measured configuration: the verified roller-flank knuckle (J1 acromion top, link 1a
 * with the conjugate flank lug, passive O20 knuckle K SLAVED to q2 by the hub-2 rim lobe -> bell crank (MR63ZZ pair on link
 * 1b) -> bent long arm -> MR63ZZ roller -> flank, link 1b, J2, link 2, J3) with J3's axis ON A GH RAY (b3 0): member 3 moves
 * with the arm, the drift is identically 0, so the two-pin knee carried nothing and is DELETED - hub 3's lower plate, the
 * E strap and the former knee link are ONE rigid Ti bracket bolted to the arm pad on BOTTOM. 3 active (J1, J2, J3 encoded),
 * K slaved and never read, 0 passive translations, 0 sensed passives.
 * Best measured (CMA A2, 2 mm objective, 5914 configs, converged): frozen exact Bench(110,360) plain 21.07 / 1 mm 23.23 / 2 mm 32.25 (score 92.34), held out 24.59; fast Bench(60,160) plain 16.70 / 2 mm 20.02. Not verified.
 * Geometry exported from docs/concepts/models/kneeless-roller-knuckle-3r.py (mode viz). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = Math.PI / 180;
  const P = {"az1": 94.353, "el1": 65.9804, "az2": 41.8875, "el2": 41.0083, "wd": 73.9288, "wa": -11.3645, "b3": 0.0, "lE": 82.2602, "lc": 29.9075, "phiE": -2.4165, "phib": -89.2952, "stk": 4.8534, "ang_min": 0.0, "bk1": 27.4142, "bk2": 35.6795, "sK": -1, "a1max": 56.0143, "smhi": 16.9881, "smlo": 5.0, "capK": 6.0, "law_mode": "seg", "kA": 2.568, "t1": 6.0, "kB": 2.568, "smt": 12.0, "kK": 2.568, "i_rock": 2.2297, "r_horn": 4.7677, "r_lobe": 8.4303, "arm_lo": 1.0};
  const G = {"u": [[0.0309, 0.91341, 0.40587], [-0.51639, 0.61264, 0.59834], [-0.18935, -0.27683, 0.94208]], "c": [[0.0, 0.0, 0.0], [-0.0, 0.0, -0.0], [-0.0, 0.0, 0.0]], "uK": [-0.33774, 0.93493, 0.10882], "sa": [0.05455, -0.96092, -0.2714], "st": [0.98039, 0.0, 0.19705], "sn": [-0.18935, -0.27683, 0.94208], "A": [38.142, 60.537], "branch": -1.0, "m": [0.0, 0.0, 0.0], "f": [51.15, 61.71, 79.3], "fK": 55.61, "capK": 6.0, "tr": 93.58, "tp": 2.177, "RUN": 0.5, "A0": [1.08291, -78.97505, -22.98933], "A0m": [1.08291, -78.97505, -22.98933], "Bm": [-28.21592, -79.32856, -28.982], "eE": [0.01316, -0.96006, -0.27947], "psiA": -75.9018, "thLo": 27.3952, "thHi": 81.6906, "q2s": [98.0058, 2.5189], "lawTh": [81.691, 82.923, 84.174, 85.441, 86.722, 88.016, 89.318, 90.629, 91.945, 93.264, 94.585, 95.904, 97.22, 98.53, 99.832, 101.124, 102.403, 103.667, 104.914, 106.14, 107.344, 108.522, 109.672, 110.79, 111.875], "lawDK": [-0.0, -2.054, -4.109, -6.163, -8.218, -10.272, -12.326, -14.381, -16.435, -18.49, -20.544, -22.598, -24.653, -26.707, -28.762, -30.816, -32.87, -34.925, -36.979, -39.034, -41.088, -43.142, -45.197, -47.251, -49.306], "lawQ2": [2.519, 1.719, 0.919, 0.119, -0.681, -1.481, -2.281, -3.081, -3.881, -4.681, -5.481, -6.281, -7.081, -7.881, -8.681, -9.481, -10.281, -11.081, -11.881, -12.681, -13.481, -14.281, -15.081, -15.881, -16.681], "emb": "rod", "rocker": [-28.943, 49.012, 25.776], "rockerAx": [-0.46321, 0.78439, 0.41252], "rodA": [-15.601, 59.158, -8.788], "rodB": [-15.601, 59.158, -8.788], "armA": [-28.943, 49.012, 25.776], "armB": [-35.042, 51.551, 11.894], "L1a": [[-5.77, 51.55, 12.59], [-9.23, 54.56, 13.6], [-9.41, 49.73, 16.98]], "L1b": [[-27.13, 51.32, 14.84], [-27.61, 45.9, 18.91], [-30.58, 44.59, 24.61], [-24.57, 47.93, 16.5], [-26.57, 45.38, 21.41], [-31.1, 46.45, 28.73], [-23.24, 46.82, 18.74], [-25.39, 44.62, 23.78], [-21.96, 52.85, 17.74], [-22.09, 46.06, 21.07], [-25.45, 46.11, 27.48]], "L2": [[-35.11, 31.72, 45.62], [-32.27, 22.38, 51.11], [-31.09, 13.78, 59.51], [-28.27, 3.49, 65.82], [-24.84, -8.11, 71.98], [-31.23, 27.04, 47.61], [-29.79, 18.83, 55.2], [-27.74, 9.51, 62.58], [-24.18, -1.19, 67.64], [-31.93, 33.31, 46.72], [-28.71, 23.58, 51.4], [-26.93, 14.98, 58.82], [-24.23, 5.11, 65.48], [-21.13, -6.25, 73.27], [-28.34, 28.73, 48.95], [-26.32, 20.2, 55.66], [-23.98, 11.0, 62.66], [-21.1, 0.57, 70.18]], "armPts": [[-29.638, 50.189, 26.394], [-29.352, 48.609, 23.424], [-30.432, 49.326, 21.629], [-31.057, 49.306, 19.512], [-31.662, 49.271, 17.422], [-32.375, 49.414, 15.42], [-33.122, 49.617, 13.452], [-35.87, 52.769, 12.176], [-36.451, 52.788, 10.212], [-36.801, 52.896, 8.197], [-36.918, 53.091, 6.162], [-36.797, 53.37, 4.137], [-36.443, 53.729, 2.152], [-35.859, 54.163, 0.238], [-35.054, 54.665, -1.577], [-34.041, 55.228, -3.266], [-32.835, 55.842, -4.802], [-31.454, 56.499, -6.164], [-29.919, 57.19, -7.33], [-28.253, 57.903, -8.284], [-26.48, 58.628, -9.009], [-24.628, 59.353, -9.497], [-22.725, 60.069, -9.739], [-20.799, 60.764, -9.732], [-18.879, 61.428, -9.475], [-16.993, 62.05, -8.973], [-16.555, 62.191, -8.82]], "lugPts": [[-18.315, 55.725, -4.284], [-20.786, 57.16, -10.996], [-19.612, 57.17, -12.933], [-18.254, 57.267, -14.406], [-16.761, 57.407, -15.612], [-15.177, 57.571, -16.597], [-14.698, 57.622, -16.849]], "roller": [-15.601, 59.158, -8.788], "rollerAx": [-0.25241, 0.95712, -0.14218], "sig": 1.0, "g": 2.2297, "cprog": 0.0, "dKlim": 46.8};
  const u = G.u, c = G.c, uK = G.uK, sn = G.sn, a2 = G.A[1], hub = 12.25, rad = 10;
  const vref = V.unit(V.cross(u[2], [0.3, 0.5, 0.8]));
  const cb = x => Math.cos(x * D2R);
  const dot = V.dot;
  /** physical J2 stop: th (deg) inside [thLo, thHi] -> K on stop A (state 0); else J2 locked on its q2 stop, K opens */
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
    const T = G.lawTh, n = T.length; let j = 0;
    while (j < n - 2 && T[j + 1] < th) j++;
    const ok = th <= T[n - 1], a = Math.max(0, Math.min(1, (th - T[j]) / Math.max(T[j + 1] - T[j], 1e-9)));
    const q2s = G.lawQ2[j] + a * (G.lawQ2[j + 1] - G.lawQ2[j]), dK = G.lawDK[j] + a * (G.lawDK[j + 1] - G.lawDK[j]);
    const p = M.mulv(M.rot(u2, q2s), u3), q1 = K.axisAngle(u1, M.mulv(M.rot(uK, dK), p), w);
    return { q1, dK, q2: q2s, ok, L: { state } };
  }
  function chain(q1, dK, q2, q3) {
    const R1 = M.rot(u[0], q1), R1b = M.mul(R1, M.rot(uK, dK)), R12 = M.mul(R1b, M.rot(u[1], q2)), R3 = M.rot(u[2], q3), R123 = M.mul(R12, R3);
    const t3 = M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2])));        // c3 = 0 (J3 on a GH ray): t3 = 0
    return { R1, R1b, R12, R123, t3 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const Q = Qof(ctx), k = ik(Q), R12 = M.mul(M.mul(M.rot(u[0], k.q1), M.rot(uK, k.dK)), M.rot(u[1], k.q2));
    const q3 = K.axisAngle(u[2], vref, M.mulv(M.T(R12), M.mulv(Q, vref)));
    return [k.q1, k.dK, k.q2, K.wrap180(q3)];
  }
  const fk = q => chain(q[0], q[1], q[2], q[3]);
  const check = (q, ctx) => {
    const k = ik(Qof(ctx));
    if (!k.ok) return k.L.state === 1 ? 'past the drive stop B (stop B / pressure angle / lift-off)' : (k.L.state === -1 ? 'folded side: J2 on its dowel' : 'chain cannot close');
    if (Math.abs(k.dK) > G.dKlim + 1e-6) return `past the flank's working range (|dK| ${Math.abs(k.dK).toFixed(1)} > ${G.dKlim} deg): stop B`;
    return null;
  };
  const closes = (q, ctx) => { const r = C.residual(q, ctx); return Math.max(...r.map(Math.abs)) <= 0.5; };
  const solveC = (ctx, qPrev) => { const q = solve(ctx); return (!qPrev || closes(q, ctx)) ? q : K.dls(C, ctx, qPrev, { iters: 40 }).q; };
  const C = {
    id: 'kneeless-roller-knuckle-3r', name: 'Knee-free roller-flank knuckle: J3 on a GH ray, the pin knee replaced by one rigid bracket (3 active, K slaved, not read)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the lobe - bell crank - roller - flank drive)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve: solveC,
    residual: (q, ctx) => { const F = fk(q); return M.rotErrDeg(F.R123, Qof(ctx)).concat(F.t3); },
    check,
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), Wd = v => M.mulv(S, v), F = fk(q);
      const Rc = M.mul(F.R1b, M.rot(G.rockerAx, G.sig * (Math.abs(q[1]) / G.g) * (1 + (G.cprog || 0) * Math.abs(q[1]) * D2R)));
      const on = (R, p) => W(M.mulv(R, p));
      const h1 = { kind: 'hub', role: 'active', name: 'J1 (axis on a GH ray)', c: W(V.scale(u[0], G.f[0])), axis: Wd(u[0]), r: rad, h: hub };
      const hK = { kind: 'hub', role: 'passive', name: 'K (O20, passive, slaved; clock-spring cap, stop A; the flank is a lateral lug of link 1a)', c: on(F.R1, V.scale(uK, G.fK)), axis: Wd(M.mulv(F.R1, uK)), r: rad, h: hub + (G.capK || 0) };
      const h2 = { kind: 'hub', role: 'active', name: 'J2 (axis on a GH ray; folded dowel stop, drive stop B)', c: on(F.R1b, V.scale(u[1], G.f[1])), axis: Wd(M.mulv(F.R1b, u[1])), r: rad, h: hub };
      const h3 = { kind: 'hub', role: 'active', name: 'J3 (axis ON a GH ray, b3 0: member 3 moves with the arm)', c: on(F.R12, V.scale(u[2], G.f[2])), axis: Wd(M.mulv(F.R12, u[2])), r: rad, h: hub };
      const Rm = F.R123, n3 = Wd(M.mulv(Rm, sn)), lv = (p, h) => V.madd(on(Rm, p), n3, h);
      const rim = on(Rm, V.add(V.scale(sn, G.f[2] + 1.5), V.scale(G.eE, rad)));
      const arm = p => M.mulv(ctx.H, p), padC = lv(G.Bm, G.tr + G.tp / 2), lat = arm([G.Bm[0], -150, 50]);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler', c: V.madd(h1.c, h1.axis, -3), z: h1.axis, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        h1,
        { kind: 'arc', role: 'link', name: 'link 1a (8 x 3 strap, J1 -> K)', pts: (G.L1a.length ? G.L1a : [V.scale(u[0], G.f[0]), V.scale(uK, G.fK)]).map(p => on(F.R1, p)), r: 2.5 },
        hK,
        { kind: 'arc', role: 'link', name: 'link 1b (8 x 3 strap, K -> J2)', pts: G.L1b.map(p => on(F.R1b, p)), r: 2.5 },
        h2,
        { kind: 'arc', role: 'link', name: 'link 2 (8 x 3 strap, fitted)', pts: G.L2.map(p => on(F.R12, p)), r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'bell crank boss (MR63ZZ pair, pin in link 1b beside hub 2; short arm rides the hub-2 rim lobe)', c: on(Rc, G.rocker), axis: Wd(M.mulv(Rc, G.rockerAx)), r: 5, h: 6 },
        { kind: 'arc', role: 'link', name: 'bell crank bent long arm (3 mm Ti: straight run, then an arc concentric with hub K)', pts: G.armPts.map(p => on(Rc, p)), r: 1.5 },
        { kind: 'hub', role: 'passive', name: 'MR63ZZ roller (O6 x 2.5, radial axis) on the arm tip', c: on(Rc, G.roller), axis: Wd(M.mulv(Rc, G.rollerAx)), r: 3, h: 2.5 },
        { kind: 'arc', role: 'link', name: 'flank lug of link 1a (conjugate flank, wire-EDM)', pts: G.lugPts.map(p => on(F.R1, p)), r: 1.5 },
        h3,
        { kind: 'link', role: 'fixed-arm', name: 'rigid bracket, E run (hub 3 lower plate -> corner), 3 mm Ti, moves with the arm', a: rim, b: lv(G.A0, G.tr + 1.5), r: 2.5 },
        { kind: 'link', role: 'fixed-arm', name: 'rigid bracket, arm run (corner -> pad; the former knee link, no pins)', a: lv(G.A0, G.tr + 1.5), b: lv(G.Bm, G.tr + 1.5), r: 3 },
        { kind: 'plate', role: 'fixed-arm', name: 'arm pad (bracket bolted to the cuff / BOTTOM)', c: padC, z: n3, x: Wd(M.mulv(Rm, G.sa)), size: [14, 14], t: G.tp },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM bar to the cuff (schematic)', a: V.madd(padC, n3, -2), b: lat, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  };
  K.register(C);
})();
